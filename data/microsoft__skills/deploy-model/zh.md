---
name: deploy-model
description: "統一的 Azure OpenAI 模型部署 skill，依意圖智慧路由。處理快速 preset 部署、完整自訂部署（版本/SKU/容量/RAI policy），以及跨 region 和 project 的容量探索。USE FOR: deploy model, deploy gpt, create deployment, model deployment, deploy openai model, set up model, provision model, find capacity, check model availability, where can I deploy, best region for model, capacity analysis. DO NOT USE FOR: listing existing deployments (use foundry_models_deployments_list MCP tool), deleting deployments, agent creation (use agent/create), project creation (use project/create)."
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# Deploy Model

> **範圍：先讀這段。** 這個 skill 是透過 Azure CLI / MCP / portal，以 **out-of-band** 的方式建立模型部署。如果是 azd 管理的 Foundry project（用 `azd ai agent init` 建出來的），請改在 `azure.yaml services.ai-project.deployments[]` 宣告 deployment，`azd ai agent init` 會從範例 manifest 寫入該項目，`azd provision` 再透過 Bicep 建立 deployment。Golden Path 見 [foundry-agent/create/create-hosted.md](../../foundry-agent/create/create-hosted.md)。這個 skill 只用在：(a) 不是 azd project 管理的 Foundry project，(b) azd 生命週期以外的臨時部署。

所有 Azure OpenAI 模型部署流程的統一入口。分析使用者的意圖，路由到適合的部署模式。

## Quick Reference

| Mode | When to Use | Sub-Skill |
|------|-------------|-----------|
| **Preset** | 快速部署，不需要自訂 | [preset/SKILL.md](preset/SKILL.md) |
| **Customize** | 完整控制：版本、SKU、容量、RAI policy | [customize/SKILL.md](customize/SKILL.md) |
| **Capacity Discovery** | 找出哪裡可以部署指定容量 | [capacity/SKILL.md](capacity/SKILL.md) |

## Intent Detection

分析使用者的 prompt，路由到正確的模式：

```
User Prompt
    │
    ├─ Simple deployment (no modifiers)
    │  "deploy gpt-4o", "set up a model"
    │  └─> PRESET mode
    │
    ├─ Customization keywords present
    │  "custom settings", "choose version", "select SKU",
    │  "set capacity to X", "configure content filter",
    │  "PTU deployment", "with specific quota"
    │  └─> CUSTOMIZE mode
    │
    ├─ Capacity/availability query
    │  "find where I can deploy", "check capacity",
    │  "which region has X capacity", "best region for 10K TPM",
    │  "where is this model available"
    │  └─> CAPACITY DISCOVERY mode
    │
    └─ Ambiguous (has capacity target + deploy intent)
       "deploy gpt-4o with 10K capacity to best region"
       └─> CAPACITY DISCOVERY first → then PRESET or CUSTOMIZE
```

### Routing Rules

| Signal in Prompt | Route To | Reason |
|------------------|----------|--------|
| 只有模型名稱，沒有選項 | **Preset** | 使用者想快速部署 |
| "custom"、"configure"、"choose"、"select" | **Customize** | 使用者想要控制權 |
| "find"、"check"、"where"、"which region"、"available" | **Capacity** | 使用者想做探索 |
| 指定容量數字 + "best region" | **Capacity → Preset** | 先探索，再快速部署 |
| 指定容量數字 + "custom" 類關鍵字 | **Capacity → Customize** | 先探索，再帶選項部署 |
| "PTU"、"provisioned throughput" | **Customize** | PTU 需要選 SKU |
| "optimal region"、"best region"（沒有容量目標） | **Preset** | 最佳化 region 是 preset 的專長 |

### Multi-Mode Chaining

有些 prompt 需要依序用兩種模式：

**Pattern: Capacity → Deploy**
使用者指定了容量需求，而且要部署時：
1. 執行 **Capacity Discovery**，找出配額足夠的 region/project
2. 把結果呈現給使用者
3. 詢問：「要用**快速預設值**部署，還是**自訂設定**？」
4. 依回答路由到 **Preset** 或 **Customize**

> 💡 **Tip：** 不確定使用者要哪種模式時，預設用 **Preset**（快速部署）。想要自訂的使用者通常會明確說出「custom」、「configure」或「with specific settings」之類的關鍵字。

## Project Selection (All Modes)

任何部署之前，都要先決定要部署到哪個 project。這適用於**所有**模式（preset、customize，以及容量探索之後）。

### Resolution Order

1. **檢查 `PROJECT_RESOURCE_ID` 環境變數**：有設就當預設值
2. **檢查使用者的 prompt**：使用者有指定 project 或 region 就用那個
3. **都沒有**：查詢使用者的 project，並建議目前的那一個

### Confirmation Step (Required)

**部署之前一定要先確認目標。** 把要用的內容給使用者看，讓他有機會更改：

```
Deploying to:
  Project:  <project-name>
  Region:   <region>
  Resource: <resource-group>

Is this correct? Or choose a different project:
  1. ✅ Yes, deploy here (default)
  2. 📋 Show me other projects in this region
  3. 🌍 Choose a different region
```

如果使用者選 2，顯示該 region 前 5 個 project：

```
Projects in <region>:
  1. project-alpha (rg-alpha)
  2. project-beta (rg-beta)
  3. project-gamma (rg-gamma)
  ...
```

> ⚠️ **沒讓使用者看到要用哪個 project 之前，絕對不准部署。** 這樣才不會誤部署到錯的資源。

## Pre-Deployment Validation (All Modes)

在呈現任何部署選項（SKU、容量）之前，一定要先驗證這兩件事：

1. **模型支援該 SKU**：查詢模型目錄，確認所選的模型+版本支援目標 SKU：
   ```bash
   az cognitiveservices model list --location <region> --subscription <sub-id> -o json
   ```
   過濾出該模型，取 `.model.skus[].name` 得到支援的 SKU。

2. **Subscription 有可用配額**：檢查使用者的 subscription 對這組 SKU+模型還有沒有未分配的配額：
   ```bash
   az cognitiveservices usage list --location <region> --subscription <sub-id> -o json
   ```
   用 usage 名稱格式 `OpenAI.<SKU>.<model-name>` 比對（例如 `OpenAI.GlobalStandard.gpt-4o`）。計算 `available = limit - currentValue`。

> ⚠️ **警告：** 只呈現兩項檢查都通過的選項。不要顯示寫死的 SKU 清單，一定要動態查詢。可用配額是 0 的 SKU 要用 ❌ 標成純資訊項目，不能當作可選的選項。

> 💡 **配額管理：** 申請增加配額、監控用量和排除配額錯誤，都交給 [quota skill](../../quota/quota.md)，不要在這裡重複寫一份指引。

## Prerequisites

所有部署模式都需要：
- 已安裝並登入 Azure CLI（`az login`）
- 有部署權限的啟用中 Azure subscription
- Microsoft Foundry project 的 resource ID（或由 agent 透過 `PROJECT_RESOURCE_ID` 環境變數協助探索）

## Sub-Skills

- **[preset/SKILL.md](preset/SKILL.md)** — 用合理的預設值快速部署到最佳 region
- **[customize/SKILL.md](customize/SKILL.md)** — 互動式引導流程，可完整控制設定
- **[capacity/SKILL.md](capacity/SKILL.md)** — 探索跨 region 和 project 的可用容量
