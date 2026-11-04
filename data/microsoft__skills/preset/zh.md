---
name: preset
description: "分析所有可用 region 的容量，聰明地把 Azure OpenAI 模型 deploy 到最適合的 region。會先檢查目前的 region，必要時列出替代方案。USE FOR: quick deployment、optimal region、best region、automatic region selection、fast setup、multi-region capacity check、high availability deployment、deploy to best location。DO NOT USE FOR: 自訂 SKU 選擇（用 customize）、指定版本（用 customize）、自訂容量設定（用 customize）、PTU deployment（用 customize）。"
license: MIT
metadata:
  author: Microsoft
  version: "1.0.1"
---

# 把模型 Deploy 到最佳 Region

自動化聰明的 Azure OpenAI 模型 deploy：檢查各 region 的容量，再 deploy 到最好的選項。

## 這個 Skill 做什麼

1. 驗證 Azure 身分驗證和專案範圍
2. 檢查目前專案所在 region 的容量
3. 如果沒有容量：分析所有 region，列出可用的替代方案
4. 依選定的 region 篩選專案
5. 需要時支援建立新專案
6. 用 GlobalStandard SKU deploy 模型
7. 監控 deployment 進度

## 前置條件

- 已安裝並設定好 Azure CLI
- 有效的 Azure subscription，並有 Cognitive Services 的讀取/建立權限
- Microsoft Foundry 專案資源 ID（`PROJECT_RESOURCE_ID` 環境變數，或互動式提供）
  - 格式：`/subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{account}/projects/{project}`
  - 位置：Microsoft Foundry 入口網站 → Project → Overview → Resource ID

## 快速流程

### 快速路徑（目前 Region 有容量）
```
1. Check authentication → 2. Get project → 3. Check current region capacity
→ 4. Deploy immediately
```

### 替代 Region 路徑（沒有容量）
```
1. Check authentication → 2. Get project → 3. Check current region (no capacity)
→ 4. Query all regions → 5. Show alternatives → 6. Select region + project
→ 7. Deploy
```

---

## Deployment 階段

| 階段 | 動作 | 關鍵指令 |
|-------|--------|-------------|
| 1. 驗證身分 | 檢查 Azure CLI 登入和 subscription | `az account show`, `az login` |
| 2. 取得專案 | 解析 `PROJECT_RESOURCE_ID` 這個 ARM ID，確認存在 | `az cognitiveservices account show` |
| 3. 取得模型 | 列出可用模型，由使用者選擇模型 + 版本 | `az cognitiveservices account list-models` |
| 4. 檢查目前 Region | 用 GlobalStandard SKU 查詢容量 | `az rest --method GET .../modelCapacities` |
| 5. 多 Region 查詢 | 如果本地沒有容量，查詢所有 region | 同一個容量 API，不加 location 篩選 |
| 6. 選擇 Region + 專案 | 使用者挑 region；找到或建立專案 | `az cognitiveservices account list`, `az cognitiveservices account create` |
| 7. Deploy | 產生唯一名稱、計算容量（可用量的 50%，最少 50 TPM）、建立 deployment | `az cognitiveservices account deployment create` |

詳細的逐步說明請看 [workflow reference](references/workflow.md)。

---

## 錯誤處理

| 錯誤 | 症狀 | 處理方式 |
|-------|---------|------------|
| 驗證失敗 | `az account show` 回傳錯誤 | 執行 `az login`，然後 `az account set --subscription <id>` |
| 沒有配額 | 所有 region 的容量都是 0 | 增加配額的申請和疑難排解，交給 [quota skill](../../../quota/quota.md)；檢查現有的 deployment；試試別的模型 |
| 找不到模型 | 容量清單是空的 | 用 `az cognitiveservices account list-models` 確認模型名稱；注意大小寫 |
| 名稱衝突 | "deployment already exists" | 在 deployment 名稱後面加 suffix（`generate_deployment_name` script 會自動處理） |
| Region 不可用 | Region 不支援該模型 | 從可用清單中選別的 region |
| 權限不足 | "Forbidden" 或 "Unauthorized" | 確認有 Cognitive Services Contributor 角色：`az role assignment list --assignee <user>` |

---

## 進階用法

```bash
# Custom capacity
az cognitiveservices account deployment create ... --sku-capacity <value>

# Check deployment status
az cognitiveservices account deployment show --name <acct> --resource-group <rg> --deployment-name <name> --query "{Status:properties.provisioningState}"

# Delete deployment
az cognitiveservices account deployment delete --name <acct> --resource-group <rg> --deployment-name <name>
```

## 備註

- **SKU：** 只支援 GlobalStandard，**API 版本：** 2024-10-01（GA 穩定版）

---

## 相關 Skills

- **microsoft-foundry** - Microsoft Foundry 操作的上層 skill
- **[quota](../../../quota/quota.md)**：查看配額、申請增加配額和排除配額錯誤，都交給這個 skill
- **azure-quick-review** - 檢視 Azure 資源的合規性
- **cost-estimation** - 透過另外安裝的 `azure-cost` plugin 估算成本
- **azure-validate** - deploy 前驗證 Azure 基礎設施
