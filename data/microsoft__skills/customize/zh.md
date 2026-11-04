---
name: customize
description: "互動式引導部署 Azure OpenAI 模型，可完整自訂。一步一步選擇模型版本、SKU（GlobalStandard/Standard/ProvisionedManaged）、容量、RAI policy（內容過濾），以及進階選項（dynamic quota、priority processing、spillover）。USE FOR: custom deployment, customize model deployment, choose version, select SKU, set capacity, configure content filter, RAI policy, deployment options, detailed deployment, advanced deployment, PTU deployment, provisioned throughput. DO NOT USE FOR: quick deployment to optimal region (use preset)."
license: MIT
metadata:
  author: Microsoft
  version: "1.0.1"
---

# Customize Model Deployment

互動式引導流程，用來部署 Azure OpenAI 模型，版本、SKU、容量、內容過濾和進階選項都可以完整自訂。

## Quick Reference

| Property | Description |
|----------|-------------|
| **Flow** | 互動式、一步一步的引導部署 |
| **Customization** | Version, SKU, Capacity, RAI Policy, Advanced Options |
| **SKU Support** | GlobalStandard, Standard, ProvisionedManaged, DataZoneStandard |
| **Best For** | 需要精準控制部署設定 |
| **Authentication** | Azure CLI (`az login`) |
| **Tools** | Azure CLI, MCP tools（選用） |

## When to Use This Skill

當你需要**精準控制**部署設定時用這個 skill：

- ✅ **選擇特定的模型版本**（不只是最新版）
- ✅ **選擇部署 SKU**（GlobalStandard、Standard 還是 PTU）
- ✅ **在可用範圍內設定確切的容量**
- ✅ **設定內容過濾**（選擇 RAI policy）
- ✅ **啟用進階功能**（dynamic quota、priority processing、spillover）
- ✅ **PTU 部署**（Provisioned Throughput Units）

**替代方案：** 想快速部署到最佳 region、設定自動套用，就用 `preset`。

### Comparison: customize vs preset

| Feature | customize | preset |
|---------|---------------------|----------------------------|
| **Focus** | 完整的自訂控制 | 挑選最佳 region |
| **Version Selection** | 使用者從可用版本中選 | 自動用最新版 |
| **SKU Selection** | 使用者選（GlobalStandard/Standard/PTU） | 只有 GlobalStandard |
| **Capacity** | 使用者指定確切數值 | 自動計算（可用容量的 50%） |
| **RAI Policy** | 使用者從選項中選 | 只用預設 policy |
| **Region** | 先用目前的 region，沒容量再改查所有 region | 一開始就檢查所有 region 的容量 |
| **Use Case** | 部署需求很精確 | 快速部署到最佳 region |

## Prerequisites

- 有 Cognitive Services Contributor 或 Owner 角色的 Azure subscription
- Microsoft Foundry project 的 resource ID（格式：`/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{account}/projects/{project}`）
- 已安裝並登入 Azure CLI（`az login`）
- 選用：設定 `PROJECT_RESOURCE_ID` 環境變數

## Workflow Overview

### Complete Flow (14 Phases)

```
1. Verify Authentication
2. Get Project Resource ID
3. Verify Project Exists
4. Get Model Name (if not provided)
5. List Model Versions → User Selects
6. List SKUs for Version → User Selects
7. Get Capacity Range → User Configures
   7b. If no capacity: Cross-Region Fallback → Query all regions → User selects region/project
8. List RAI Policies → User Selects
9. Configure Advanced Options (if applicable)
10. Configure Version Upgrade Policy
11. Generate Deployment Name
12. Review Configuration
13. Execute Deployment & Monitor
```

### Fast Path (Defaults)

如果使用者全部接受預設值（最新版、GlobalStandard SKU、建議容量、預設 RAI policy、標準升級 policy），大約 5 次互動就能完成部署。

---

## Phase Summaries

> ⚠️ **一定要先讀：** 執行任何 phase 之前，先載入 [references/customize-workflow.md](references/customize-workflow.md)，裡面有完整的 script 和實作細節。下面的摘要只講每個 phase *做什麼*，參考檔才有 *怎麼做*（CLI 指令、配額模式、容量公式、跨 region fallback 邏輯）。

| Phase | Action | Key Details |
|-------|--------|-------------|
| **1. Verify Auth** | 檢查 `az account show`；需要的話提示 `az login` | 確認啟用的是正確的 subscription |
| **2. Get Project ID** | 讀 `PROJECT_RESOURCE_ID` 環境變數，或詢問使用者 | 必須是 ARM resource ID 格式 |
| **3. Verify Project** | 解析 resource ID，呼叫 `az cognitiveservices account show` | 取出 subscription、RG、account、project、region |
| **4. Get Model** | 用 `az cognitiveservices account list-models` 列出模型 | 使用者從可用模型中選，或輸入自訂名稱 |
| **5. Select Version** | 查詢所選模型的版本 | 推薦最新版；使用者從清單中選 |
| **6. Select SKU** | 查詢模型目錄 + subscription 配額，只顯示可部署的 SKU | ⚠️ 絕對不要寫死 SKU 清單，一定要查即時資料 |
| **7. Configure Capacity** | 查詢容量 API，驗證 min/max/step，使用者輸入數值 | 目前 region 沒容量就跨 region fallback |
| **8. Select RAI Policy** | 列出內容過濾選項 | 預設：`Microsoft.DefaultV2` |
| **9. Advanced Options** | Dynamic quota（GlobalStandard）、priority processing（PTU）、spillover | 能不能用取決於 SKU |
| **10. Upgrade Policy** | 選擇：OnceNewDefaultVersionAvailable / OnceCurrentVersionExpired / NoAutoUpgrade | 預設：有新的預設版本就自動升級 |
| **11. Deployment Name** | 自動產生唯一名稱，允許自訂覆寫 | 驗證格式：`^[\w.-]{2,64}$` |
| **12. Review** | 顯示完整設定摘要，繼續之前先確認 | 使用者核准或取消 |
| **13. Deploy & Monitor** | `az cognitiveservices account deployment create`，輪詢狀態 | 5 分鐘 timeout；顯示 endpoint + portal 連結 |


---

## Error Handling

### Common Issues and Resolutions

| Error | Cause | Resolution |
|-------|-------|------------|
| **Model not found** | 模型名稱無效 | 用 `az cognitiveservices account list-models` 列出可用模型 |
| **Version not available** | 這個 SKU 不支援該版本 | 換版本或換 SKU |
| **Insufficient quota** | 容量大於可用配額 | skill 會自動搜尋所有 region；只有在沒有任何 region 有配額時才會失敗 |
| **SKU not supported** | 這個 region 沒有該 SKU | 跨 region fallback 會自動搜尋其他 region |
| **Capacity out of range** | 容量數值無效 | **已預防**：skill 在輸入時就驗證 min/max/step（Phase 7） |
| **Deployment name exists** | 名稱衝突 | 自動遞增產生名稱 |
| **Authentication failed** | 沒登入 | 執行 `az login` |
| **Permission denied** | 權限不足 | 指派 Cognitive Services Contributor 角色 |
| **Capacity query fails** | API／權限／網路錯誤 | **部署會被擋下**：沒有有效的配額資料就不會繼續 |

### Troubleshooting Commands

```bash
# Check deployment status
az cognitiveservices account deployment show --name <account> --resource-group <rg> --deployment-name <name>

# List all deployments
az cognitiveservices account deployment list --name <account> --resource-group <rg> -o table

# Check quota usage
az cognitiveservices usage list --name <account> --resource-group <rg>

# Delete failed deployment
az cognitiveservices account deployment delete --name <account> --resource-group <rg> --deployment-name <name>
```

---

## Selection Guides & Advanced Topics

> SKU 比較表、PTU 容量估算公式和進階選項的細節，請載入 [references/customize-guides.md](references/customize-guides.md)。

**SKU 選擇：** GlobalStandard（正式環境/高可用）→ Standard（開發/測試）→ ProvisionedManaged（大流量/保證吞吐量）→ DataZoneStandard（資料落地）。

**容量：** 以 TPM 計的 SKU，範圍從 1K（開發）到 100K 以上（大型正式環境）。以 PTU 計的用這個公式：`(Input TPM × 0.001) + (Output TPM × 0.002) + (Requests/min × 0.1)`。

**進階選項：** Dynamic quota（只有 GlobalStandard）、priority processing（只有 PTU，要額外付費）、spillover（溢出到備援的 deployment）。

---

## Related Skills

- **preset** - 自動設定，快速部署到最佳 region
- **microsoft-foundry** - 所有 Microsoft Foundry 操作的上層 skill
- **[quota](../../../quota/quota.md)** — 查看配額、申請增加配額、排除配額錯誤，都交給這個 skill，不要重複寫一份指引
- **rbac** - 管理權限和存取控制

---

## Notes

- 設定 `PROJECT_RESOURCE_ID` 環境變數就能跳過詢問
- 不是每個 region 都有所有 SKU；容量依 subscription/region/模型而異
- 自訂的 RAI policy 可以在 Azure Portal 設定
- 自動版本升級會在維護時段進行
- 正式環境部署要搭配 Azure Monitor 和 Application Insights
