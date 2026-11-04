---
name: capacity
description: "跨 region 和 project 探索可用的 Azure OpenAI 模型容量。分析配額上限、比較可用性，並依容量需求推薦最適合的部署位置。USE FOR: find capacity, check quota, where can I deploy, capacity discovery, best region for capacity, multi-project capacity search, quota analysis, model availability, region comparison, check TPM availability. DO NOT USE FOR: actual deployment (hand off to preset or customize after discovery), quota increase requests (direct user to Azure Portal), listing existing deployments."
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# Capacity Discovery

在使用者能存取的所有 region 和 project 裡，找出可用的 Azure OpenAI 模型容量，再依容量需求推薦最佳部署位置。

## Quick Reference

| Property | Description |
|----------|-------------|
| **Purpose** | 找出哪裡有足夠容量可以部署模型 |
| **Scope** | 使用者有權存取的所有 region 和 project |
| **Output** | 依可用容量排序的 region/project 表格 |
| **Action** | 唯讀分析，不會部署。找完後交給 preset 或 customize |
| **Authentication** | Azure CLI (`az login`) |

## When to Use This Skill

- ✅ 使用者問「gpt-4o 可以部署在哪？」
- ✅ 使用者指定容量目標：「幫我找有 10K TPM 的 gpt-4o region」
- ✅ 使用者想比較可用性：「哪些 region 有 gpt-4o？」
- ✅ 使用者遇到配額錯誤，需要找替代位置
- ✅ 使用者問「部署模型 X 最適合哪個 region 和 project」

**探索完之後 → 交給 [preset](../preset/SKILL.md) 或 [customize](../customize/SKILL.md) 做實際部署。**

## Scripts

預先寫好的 script 已經處理了複雜的 REST API 呼叫和資料處理。直接用這些，不要自己手刻指令。

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/discover_and_rank.ps1` | 完整探索：容量 + project + 排名 | 容量探索的主要 script |
| `scripts/discover_and_rank.sh` | 同上（bash 版） | 容量探索的主要 script |
| `scripts/query_capacity.ps1` | 原始容量查詢（不比對 project） | 快速檢查容量或列出版本 |
| `scripts/query_capacity.sh` | 同上（bash 版） | 快速檢查容量或列出版本 |

## Workflow

### Phase 1: Validate Prerequisites

```bash
az account show --query "{Subscription:name, SubscriptionId:id}" --output table
```

### Phase 2: Identify Model and Version

從使用者的 prompt 取出模型名稱。如果不知道版本，就查詢可用版本：

```powershell
.\scripts\query_capacity.ps1 -ModelName <model-name>
```
```bash
./scripts/query_capacity.sh <model-name>
```

這會列出可用的版本。除非使用者另外指定，否則用最新版。

### Phase 3: Run Discovery

帶入模型名稱、版本和最低容量目標，執行完整的探索 script：

```powershell
.\scripts\discover_and_rank.ps1 -ModelName <model-name> -ModelVersion <version> -MinCapacity <target>
```
```bash
./scripts/discover_and_rank.sh <model-name> <version> <min-capacity>
```

> 💡 這個 script 會自動查詢「所有」region 的容量，和使用者現有的 project 交叉比對，然後輸出排好序的表格，排序依據是：達到目標 → project 數量 → 可用容量。

### Phase 3.5: Validate Subscription Quota

探索找出候選 region 之後，要確認使用者的 subscription 在每個 region 是不是真的有可用配額。Phase 3 的模型容量代表平台撐得住多少，但 subscription 配額限制的是這個使用者實際能部署多少。

```powershell
# 對探索結果中的每個候選 region：
$usageData = az cognitiveservices usage list --location <region> --subscription $SUBSCRIPTION_ID -o json 2>$null | ConvertFrom-Json

# 檢查模型支援的每個 SKU 的配額
# 配額名稱格式：OpenAI.<SKU>.<model-name>
$usageEntry = $usageData | Where-Object { $_.name.value -eq "OpenAI.<SKU>.<model-name>" }

if ($usageEntry) {
  $quotaAvailable = $usageEntry.limit - $usageEntry.currentValue
} else {
  $quotaAvailable = 0  # 沒有分配配額
}
```
```bash
# 對探索結果中的每個候選 region：
usage_json=$(az cognitiveservices usage list --location <region> --subscription "$SUBSCRIPTION_ID" -o json 2>/dev/null)

# 取出特定 SKU+model 的配額
quota_available=$(echo "$usage_json" | jq -r --arg name "OpenAI.<SKU>.<model-name>" \
  '.[] | select(.name.value == $name) | .limit - .currentValue')
```

**標註探索結果：**

在 Phase 3 的排名輸出加上「Quota Available」欄：

| Region | Available Capacity | Meets Target | Projects | Quota Available |
|--------|-------------------|--------------|----------|-----------------|
| eastus2 | 120K TPM | ✅ | 3 | ✅ 80K |
| westus3 | 90K TPM | ✅ | 1 | ❌ 0 (at limit) |
| swedencentral | 100K TPM | ✅ | 0 | ✅ 100K |

`quotaAvailable = 0` 的 region/SKU 要在結果裡標上 ❌。如果沒有任何 region 有可用配額，就交給 [quota skill](../../../quota/quota.md) 處理增加配額的申請和疑難排解。

### Phase 4: Present Results and Hand Off

script 輸出排名表格（現在已標上配額資訊）之後，把它呈現給使用者並詢問：

1. 🚀 **快速部署**：用預設值部署到排名最高的推薦 → 導向 [preset](../preset/SKILL.md)
2. ⚙️ **自訂部署**：自己選版本/SKU/容量/RAI → 導向 [customize](../customize/SKILL.md)
3. 📊 **查別的模型**或別的容量目標 → 重跑 Phase 2
4. ❌ 取消

### Phase 5: Confirm Project Before Deploying

交給 preset 或 customize 之前，**一定要先跟使用者確認目標 project**。規則看上層 router 的 [Project Selection](../SKILL.md#project-selection-all-modes)。

如果探索表格有列出所選 region 的範例 project，就把它當預設建議。否則查詢該 region 的 project，讓使用者自己挑。

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| "No capacity found" | 模型不可用，或全部都達到配額上限 | 交給 [quota skill](../../../quota/quota.md) 處理增加配額的申請和疑難排解 |
| Script auth error | `az login` 過期 | 重新執行 `az login` |
| Empty version list | 模型不在該 region 的目錄裡 | 換個 region 試試：`./scripts/query_capacity.sh <model> "" eastus` |
| "No projects found" | 沒有 AI Services 資源 | 引導去 `project/create` skill 或 Azure Portal |

## Related Skills

- **[preset](../preset/SKILL.md)** — 容量探索之後的快速部署
- **[customize](../customize/SKILL.md)** — 容量探索之後的自訂部署
- **[quota](../../../quota/quota.md)** — 查看配額、申請增加配額、排除配額錯誤，都交給這個 skill，不要重複寫一份指引
