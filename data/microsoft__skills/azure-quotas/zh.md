---
name: azure-quotas
description: "檢查與管理跨 provider 的 Azure quota 與用量。用於部署規劃、容量驗證、region 選擇。WHEN: \"check quotas\", \"service limits\", \"current usage\", \"request quota increase\", \"quota exceeded\", \"validate capacity\", \"regional availability\", \"provisioning limits\", \"vCPU limit\", \"how many vCPUs available in my subscription\"."
license: MIT
metadata:
  author: Microsoft
  version: "1.2.2"
---


# Azure Quotas - 服務上限與容量管理

> **權威指引**：quota 管理與容量驗證請完全照這些指示做。

## 概覽

**什麼是 Azure Quota？**

Azure quota（也叫服務上限）是你在一個 subscription 裡最多能部署的資源數量。Quota 的作用：
- 防止不小心過度佈建
- 確保 Azure 上的資源分配公平
- 代表各 region 的**可用容量**
- 可以調高（可調整的 quota），或是固定的（不可調整）

**關鍵概念：** **Quota = 資源可用性**

沒有 quota 就無法部署資源。規劃部署或選擇 region 時，一定要先檢查 quota。

## 何時使用這個 Skill

符合以下情況時呼叫這個 skill：

- **規劃新的部署**：部署前先驗證容量
- **選擇 Azure region**：比較各 region 的 quota 可用量
- **排查 quota exceeded 錯誤**：檢查目前用量與上限
- **申請提高 quota**：透過 CLI 或 Portal 提交提高申請
- **比較各 region 的容量**：找出還有 quota 的 region
- **驗證佈建上限**：確保部署不會超過 quota

## 快速參考

| **屬性** | **細節** |
|--------------|-------------|
| **主要工具** | Azure CLI（`az quota`）：**一律先用這個** |
| **需要的 Extension** | `az extension add --name quota`（必須先安裝） |
| **主要指令** | `az quota list`、`az quota show`、`az quota usage list`、`az quota usage show` |
| **完整 CLI 參考** | [commands.md](./references/commands.md) |
| **Azure Portal** | [My quotas](https://portal.azure.com/#blade/Microsoft_Azure_Capacity/QuotaMenuBlade/myQuotas)：只當作備援 |
| **REST API** | Microsoft.Quota provider：**不可靠，不要先用** |
| **MCP Server** | `azure-quota` MCP server：**絕對不要用。它不可靠。一律改用 `az quota` CLI。** |
| **所需權限** | Reader（檢視）或 Quota Request Operator（管理） |

> **⚠️ 一律先用 CLI**
>
> REST API 和 Portal 可能顯示誤導人的「No Limit」值，這**不代表**容量無限，而是 quota API 不支援那種資源類型。一律從 `az quota` 指令開始；如果 CLI 回傳 `BadRequest`，再退回去看 [Azure service limits 文件](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits)。
>
> 完整 CLI 參考請看 [commands.md](./references/commands.md)。

## Quota 類型

| **類型** | **可調整性** | **核准** | **範例** |
|----------|-------------------|--------------|--------------|
| **可調整** | 可透過 Portal/CLI/API 提高 | 通常自動核准 | VM vCPU、Public IP、Storage account |
| **不可調整** | 固定上限 | 無法變更 | subscription 範圍的硬性上限 |

**重要：**申請提高 quota 是**免費**的。你只需要為實際使用的資源付費，不用為 quota 配額付費。

## 了解資源名稱對應

**⚠️ 關鍵：**ARM 資源類型和 quota 資源名稱之間**沒有 1:1 對應**。

### 對應範例

| ARM 資源類型 | Quota 資源名稱 |
|-------------------|---------------------|
| `Microsoft.App/managedEnvironments` | `ManagedEnvironmentCount` |
| `Microsoft.Compute/virtualMachines` | `standardDSv3Family`, `cores`, `virtualMachines` |
| `Microsoft.Network/publicIPAddresses` | `PublicIPAddresses`, `IPv4StandardSkuPublicIpAddresses` |

### 探索流程

**絕對不要從 ARM 類型去猜 quota 資源名稱。** 一律用這個流程：

1. **列出**該 resource provider 的所有 quota：
   ```bash
   az quota list --scope /subscriptions/<id>/providers/<ProviderNamespace>/locations/<region>
   ```

2. **用 `localizedValue`**（人類可讀的描述）比對，找到相關的 quota

3. **後續指令用 `name` 欄位**（不是 ARM 資源類型）：
   ```bash
   az quota show --resource-name ManagedEnvironmentCount --scope ...
   az quota usage show --resource-name ManagedEnvironmentCount --scope ...
   ```

> **📖 詳細的對應範例與流程：**見 [commands.md - Resource Name Mapping](./references/commands.md#resource-name-mapping)

## 腳本

預先寫好的腳本會處理 quota extension 安裝、用量查詢與容量計算。請用它們，不要自己手動組指令。一次呼叫就會回傳上限、用量與可用容量。

| 腳本 | 用途 | 用法 |
|--------|---------|-------|
| `scripts/check-quota.ps1` | 回傳所有 quota（或提供資源名稱時只回傳單一 quota）的上限、用量與可用容量 | quota 檢查的主要腳本 |
| `scripts/check-quota.sh` | 同上（bash） | quota 檢查的主要腳本 |

## 核心流程

### 流程 1：檢查特定資源的 Quota

**情境：**部署前驗證 quota 上限與目前用量

用 resource provider 和 region 執行腳本。它一次呼叫就會回傳**所有** quota 的表格，包含上限、目前用量與可用容量：

```powershell
.\scripts\check-quota.ps1 -ResourceProvider <provider> -Region <region>
```
```bash
./scripts/check-quota.sh <provider> <region>
```

要檢查單一資源，加上資源名稱：

```powershell
.\scripts\check-quota.ps1 -ResourceProvider <provider> -Region <region> -ResourceName <resource-name>
```
```bash
./scripts/check-quota.sh <provider> <region> <resource-name>
```

**範例：**

```powershell
.\scripts\check-quota.ps1 -ResourceProvider Microsoft.Compute -Region eastus
```

**範例輸出：**

| 資源 | Region | 上限 | 用量 | 可用 |
|----------|--------|-------|-------|-----------|
| cores | eastus | 100 | 50 | 50 |
| standardDSv3Family | eastus | 350 | 50 | 300 |
| virtualMachines | eastus | 25000 | 5 | 24995 |
| ... | ... | ... | ... | ... |

> **📖 另請參閱：**[az quota show](./references/commands.md#az-quota-show)、[az quota usage show](./references/commands.md#az-quota-usage-show)

### 流程 2：比較各 Region 的 Quota

**情境：**依可用容量找出最適合部署的 region

```bash
# 定義候選 region
REGIONS=("eastus" "eastus2" "westus2" "centralus")
VM_FAMILY="standardDSv3Family"
SUBSCRIPTION_ID="<subscription-id>"

# 檢查各 region 的 quota 可用量
for region in "${REGIONS[@]}"; do
  echo "=== Checking $region ==="
  
  # 取得上限
  LIMIT=$(az quota show \
    --resource-name $VM_FAMILY \
    --scope "/subscriptions/$SUBSCRIPTION_ID/providers/Microsoft.Compute/locations/$region" \
    --query "properties.limit.value" -o tsv)
  
  # 取得目前用量
  USAGE=$(az quota usage show \
    --resource-name $VM_FAMILY \
    --scope "/subscriptions/$SUBSCRIPTION_ID/providers/Microsoft.Compute/locations/$region" \
    --query "properties.usages.value" -o tsv)
  
  # 計算可用量
  AVAILABLE=$((LIMIT - USAGE))
  
  echo "Region: $region | Limit: $LIMIT | Usage: $USAGE | Available: $AVAILABLE"
done
```

> **📖 另請參閱：**[commands.md](./references/commands.md#az-quota-show)，有完整的多 region 迴圈腳本寫法

### 流程 3：申請提高 Quota

**情境：**目前的 quota 不夠部署

```bash
# 申請提高 VM quota
az quota update \
  --resource-name standardDSv3Family \
  --scope /subscriptions/<subscription-id>/providers/Microsoft.Compute/locations/eastus \
  --limit-object value=500 \
  --resource-type dedicated

# 檢查申請狀態
az quota request status list \
  --scope /subscriptions/<subscription-id>/providers/Microsoft.Compute/locations/eastus
```

**核准流程：**
- 多數可調整的 quota 會在幾分鐘內自動核准
- 有些申請需要人工審核（數小時到數天）
- 不可調整的 quota 需要開 Azure Support ticket

> **📖 另請參閱：**[az quota update](./references/commands.md#az-quota-update)、[az quota request status](./references/advanced-commands.md#az-quota-request-status-list)

### 流程 4：列出所有 Quota 以便規劃

**情境：**了解某個 region 內某個 resource provider 的所有 quota

```bash
# 列出美國東部所有 compute quota（表格格式）
az quota list \
  --scope /subscriptions/<subscription-id>/providers/Microsoft.Compute/locations/eastus \
  --output table

# 列出所有網路 quota
az quota list \
  --scope /subscriptions/<subscription-id>/providers/Microsoft.Network/locations/eastus \
  --output table

# 列出所有 Container Apps quota
az quota list \
  --scope /subscriptions/<subscription-id>/providers/Microsoft.App/locations/eastus \
  --output table
```

> **📖 另請參閱：**[az quota list](./references/commands.md#az-quota-list)

## 疑難排解

### 常見錯誤

| **錯誤** | **原因** | **解法** |
|-----------|-----------|--------------|
| REST API 顯示 "No Limit" | 誤導，並非無限 | 改用 CLI；見快速參考中的警告 |
| `ExtensionNotFound` | 沒安裝 quota extension | `az extension add --name quota` |
| `BadRequest` | quota API 不支援該 resource provider | 查看 [service limits 文件](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits) |
| `MissingRegistration` | 沒註冊 Microsoft.Quota provider | `az provider register --namespace Microsoft.Quota` |
| `QuotaExceeded` | 部署會超過 quota | 申請提高，或選擇其他 region |
| `InvalidScope` | scope 格式不正確 | 使用格式：`/subscriptions/<id>/providers/<namespace>/locations/<region>` |
| CLI 指令整個失敗 | 驗證、extension 或環境問題 | 確認 Azure CLI 已登入（`az account show`）、重新安裝 quota extension、檢查網路。不要使用 `azure-quota` MCP server，它不可靠。 |

### 不支援的 Resource Provider

**已知不支援的 provider：**
- ❌ Microsoft.DocumentDB (Cosmos DB)：用 Portal 或 [Cosmos DB 上限文件](https://learn.microsoft.com/en-us/azure/cosmos-db/concepts-limits)

**已確認可用的 provider：**
- ✅ Microsoft.Compute（VM、磁碟、core）
- ✅ Microsoft.Network（VNet、IP、load balancer）
- ✅ Microsoft.App（Container Apps）
- ✅ Microsoft.Storage（storage account）
- ✅ Microsoft.MachineLearningServices（ML compute）

> **📖 另請參閱：**[疑難排解指南](./references/commands.md#troubleshooting)

## 其他資源

| 資源 | 連結 |
|----------|------|
| **CLI 指令參考** | [commands.md](./references/commands.md)：完整語法、參數、範例 |
| **Azure Quotas 概觀** | [Microsoft Learn](https://learn.microsoft.com/en-us/azure/quotas/quotas-overview) |
| **服務上限文件** | [Azure subscription 上限](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits) |
| **Azure Portal - My Quotas** | [Portal 連結](https://portal.azure.com/#blade/Microsoft_Azure_Capacity/QuotaMenuBlade/myQuotas) |
| **申請提高 Quota** | [如何申請提高](https://learn.microsoft.com/en-us/azure/quotas/quickstart-increase-quota-portal) |

## 最佳實務

1. ✅ **部署前一律檢查 quota**：避免 quota exceeded 錯誤
2. ✅ **先執行 `az quota list`**：找出正確的 quota 資源名稱
3. ✅ **比較各 region**：找出有可用容量的 region
4. ✅ **預留成長空間**：在眼前需求之外，多申請 20% 緩衝
5. ✅ **用表格輸出看概覽**：用 `--output table` 快速瀏覽
6. ✅ **監控用量趨勢**：設定 80% 門檻的警示（透過 Portal）
