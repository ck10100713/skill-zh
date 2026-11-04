---
name: azure-resource-lookup
description: "列出、尋找並顯示跨 subscription 或 resource group 的 Azure 資源。處理像是 \"list the websites in my subscription\"、\"list my web apps\"、\"show my app services\"、\"list virtual machines\"、\"list my VMs\"、\"show storage accounts\"、\"find container apps\"、\"what resources do I have\" 這類 prompt。USE FOR: list websites, list web apps, list app services, show websites in subscription, resource inventory, find resources by tag, tag analysis, orphaned resource discovery (not for cost analysis), unattached disks, count resources by type, cross-subscription lookup, and Azure Resource Graph queries. DO NOT USE FOR: 部署／變更資源（改用 azure-deploy）、成本最佳化（改用選配 azure-cost plugin 裡的 cost-optimization）、非 Azure 的雲。"
license: MIT
metadata:
  author: Microsoft
  version: "1.2.3"
---

# Azure 資源查詢

列出、尋找並探索跨 subscription 與 resource group 的任何類型 Azure 資源。當專屬的 MCP 工具涵蓋不到該資源類型時，用 Azure Resource Graph (ARG) 做快速的跨範圍查詢。

## 何時使用這個 Skill

使用者想做以下事情時使用這個 skill：
- **列出任何類型的資源**（VM、web app、storage account、container app、資料庫等）
- **顯示**特定 subscription 或 resource group 內的資源
- 查詢**跨多個 subscription** 或多種資源類型的資源
- 找出**孤兒資源**（沒掛載的磁碟、沒用的 NIC、閒置的 IP）
- 找出**缺少必要 tag** 或設定的資源
- 取得橫跨多種類型的**資源清單**
- 找出處於**特定狀態**的資源（不健康、佈建失敗、已停止）
- 回答「**我有哪些資源？**」或「**顯示我的 Azure 資源**」
- **列出 web app、website 或 App Service**

> ⚠️ **警告：**App Service / Web Apps 沒有專屬的 MCP `list` 指令。像 "list websites"、"list web apps" 或 "list app services" 這類 prompt，**一定要**走這個 skill，用 Azure Resource Graph 處理。

> 💡 **提示：**單一資源類型的查詢，先確認有沒有專屬的 MCP 工具可以處理（見下方的路由表）。沒有的話，就用 Azure Resource Graph。

## 快速參考

| 屬性 | 值 |
|----------|-------|
| **查詢語言** | KQL（Kusto Query Language 的子集） |
| **CLI 指令** | `az graph query -q "<KQL>" -o table` |
| **Extension** | `az extension add --name resource-graph` |
| **MCP 工具** | `extension_cli_generate`，intent 為 `az graph query` |
| **最適合** | 跨 subscription 查詢、孤兒資源、tag 稽核 |

## MCP 工具

| 工具 | 用途 | 何時使用 |
|------|---------|-------------|
| `extension_cli_generate` | 產生 `az graph query` 指令 | 主要工具：依使用者意圖產生 ARG 查詢 |
| `mcp_azure_mcp_subscription_list` | 列出可用的 subscription | 查詢前先探索 subscription 範圍 |
| `mcp_azure_mcp_group_list` | 列出 resource group | 縮小查詢範圍 |

## 流程

### Step 1：確認有沒有專屬的 MCP 工具

單一資源類型的查詢，先確認有沒有專屬的 MCP 工具可以處理：

| 資源類型 | MCP 工具 | 涵蓋範圍 |
|---|---|---|
| Virtual Machines | `compute` | ✅ 完整：list、詳細資料、規格大小 |
| Storage Accounts | `storage` | ✅ 完整：帳號、blob、table |
| Cosmos DB | `cosmos` | ✅ 完整：帳號、資料庫、查詢 |
| Key Vault | `keyvault` | ⚠️ 部分：只有 secret/key，不能列出 vault |
| SQL Databases | `sql` | ⚠️ 部分：需要 resource group 名稱 |
| Container Registries | `acr` | ✅ 完整：列出 registry |
| Kubernetes (AKS) | `aks` | ✅ 完整：cluster、node pool |
| App Service / Web Apps | `appservice` | ❌ 沒有 list 指令，改用 ARG |
| Container Apps | — | ❌ 沒有 MCP 工具，改用 ARG |
| Event Hubs | `eventhubs` | ✅ 完整：namespace、hub |
| Service Bus | `servicebus` | ✅ 完整：queue、topic |

如果有專屬工具且涵蓋完整，就用它。否則進到 Step 2。

### Step 2：產生 ARG 查詢

用 `extension_cli_generate` 來建立 `az graph query` 指令：

```yaml
mcp_azure_mcp_extension_cli_generate
  intent: "query Azure Resource Graph to <user's request>"
  cli-type: "az"
```

常見的 KQL 寫法請看 [Azure Resource Graph Query Patterns](references/azure-resource-graph.md)。

### Step 3：執行並整理結果

執行產生的指令。用 `--query`（JMESPath）來調整輸出的形狀：

```bash
az graph query -q "<KQL>" --query "data[].{name:name, type:type, rg:resourceGroup}" -o table
```

用 `--first N` 限制結果數量。用 `--subscriptions` 限定範圍。

## 錯誤處理

| 錯誤 | 原因 | 修復 |
|-------|-------|-----|
| `resource-graph extension not found` | 沒安裝 extension | `az extension add --name resource-graph` |
| `AuthorizationFailed` | 沒有 subscription 的讀取權限 | 檢查 RBAC，需要 Reader 角色 |
| 查詢出現 `BadRequest` | KQL 語法無效 | 確認資料表／欄位名稱；用 `=~` 做不分大小寫的類型比對 |
| 結果是空的 | 沒有符合的資源，或範圍錯誤 | 檢查 `--subscriptions` 旗標；確認資源類型拼寫 |

## 限制

- ✅ **一律**用 `=~` 做不分大小寫的類型比對（類型都是小寫）
- ✅ **一律**用 `--subscriptions` 或 `--first` 限定範圍，尤其是大型 tenant
- ✅ **優先**用專屬的 MCP 工具處理單一資源類型的查詢
- ❌ **絕對不要**用 ARG 做即時監控（資料有些許延遲）
- ❌ **絕對不要**透過 ARG 嘗試做變更（它是唯讀的）
