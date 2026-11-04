---
name: azure-kusto
description: "用 KQL 查詢和分析 Azure Data Explorer（Kusto/ADX）裡的資料，適用於 log 分析、遙測和時間序列分析。WHEN: KQL queries, Kusto database queries, Azure Data Explorer, ADX clusters, log analytics, time series data, IoT telemetry, anomaly detection."
license: MIT
metadata:
  author: Microsoft
  version: "1.2.2"
---

# Azure Data Explorer（Kusto）查詢與分析

執行 KQL 查詢並管理 Azure Data Explorer 資源，對 log、遙測和時間序列資料做快速、可擴展的大數據分析。

## 概觀

這個 skill 讓你查詢和管理 Azure Data Explorer（Kusto）。這是一個快速、高度可擴展的資料探索服務，專門為 log 和遙測資料最佳化。Azure Data Explorer 用 Kusto Query Language（KQL）對數十億筆紀錄做到次秒級的查詢效能。

主要能力：
- **執行查詢**：對海量資料集跑 KQL 查詢
- **探索 Schema**：找出 table、欄位和資料型別
- **資源管理**：列出叢集和資料庫
- **分析**：聚合、時間序列、異常偵測、機器學習

## 核心流程

1. **探索資源**：列出 subscription 裡可用的叢集和資料庫。如果不知道目標 table 在哪，而且有多個候選的叢集、資料庫或 Log Analytics workspace，就批次搜尋（見 Pattern 6），所有候選都查完之後才能回報「找不到」。
2. **探索 Schema**：取得 table 結構，了解資料模型
3. **查詢資料**：執行 KQL 查詢做分析、過濾、聚合
4. **分析結果**：處理查詢輸出，整理出洞見和報告

## 查詢模式

### Pattern 1：基本資料擷取
用簡單的過濾條件抓 table 裡最近的紀錄。

**KQL 範例**：
```kql
Events
| where Timestamp > ago(1h)
| take 100
```

**適用於**：快速檢視資料、擷取最近的事件

### Pattern 2：聚合分析
依維度彙總資料，用於洞見和報告。

**KQL 範例**：
```kql
Events
| summarize count() by EventType, bin(Timestamp, 1h)
| order by count_ desc
```

**適用於**：事件計數、分佈分析、top-N 查詢

### Pattern 3：時間序列分析
在時間視窗內分析資料，找出趨勢和模式。

**KQL 範例**：
```kql
Telemetry
| where Timestamp > ago(24h)
| summarize avg(ResponseTime), percentiles(ResponseTime, 50, 95, 99) by bin(Timestamp, 5m)
| render timechart
```

**適用於**：效能監控、趨勢分析、異常偵測

### Pattern 4：Join 與關聯
合併多個 table，做跨資料集分析。

**KQL 範例**：
```kql
Events
| where EventType == "Error"
| join kind=inner (
    Logs
    | where Severity == "Critical"
) on CorrelationId
| project Timestamp, EventType, LogMessage, Severity
```

**適用於**：根本原因分析、追蹤相關聯的事件

### Pattern 5：Schema 探索
查詢之前先看 table 結構。

**工具**：`kusto_table_schema_get`

**適用於**：了解資料模型、規劃查詢

### Pattern 6：跨候選來源批次搜尋
不知道 table 在哪，而且有好幾個候選的叢集、資料庫或 workspace 時，批次做唯讀的 metadata 探索，不要一個一個查。列出每個候選資料庫或 workspace 裡的 table，先比對 table 的完整名稱，再去查資料。

確認哪些來源有這個 table 之後，需要的話可以一起查這些來源：
```kql
union workspace('ws1').Requests, workspace('ws2').Requests
| take 1
```

**適用於**：在很多候選資源裡找 table，避免把空結果誤當成 table 不存在

## 主要資料欄位

執行查詢時，常見的欄位模式：
- **Timestamp**：事件時間（datetime），時間過濾用 `ago()`、`between()`、`bin()`
- **EventType/Category**：分類欄位，用來分組
- **CorrelationId/SessionId**：用來追蹤相關事件
- **Severity/Level**：依重要性過濾
- **Dimensions**：自訂屬性，用於分組和過濾

## 結果格式

查詢結果包含：
- **Columns**：欄位名稱和資料型別
- **Rows**：符合查詢的資料紀錄
- **Statistics**：筆數、執行時間、資源使用量
- **Visualization**：圖表呈現的提示（timechart、barchart 等）

## KQL 最佳實務

**🔵 查詢模式：**
- 聚合用 `summarize`，不要只用 `count()`
- 時間序列的時間分桶用 `bin()`
- 用 `project` 只選需要的欄位
- 用 `extend` 新增計算欄位

**🟡 常用函式：**
- `ago(timespan)`：相對時間（ago(1h)、ago(7d)）
- `between(start .. end)`：範圍過濾
- `startswith()`、`contains()`、`matches regex`：字串過濾
- `parse`、`extract`：從字串擷取值
- `percentiles()`、`avg()`、`sum()`、`max()`、`min()`：聚合

## 最佳實務

- 先用時間範圍過濾，並優先用有索引的欄位，這樣查詢效能最好
- 探索性的查詢用 `take` 或 `limit`，避免拿到太大的結果集
- 聚合用 `summarize`，不要在 client 端處理
- 常用的查詢存成資料庫裡的 function
- 重複的聚合用 materialized view
- 監控查詢效能和資源消耗
- 套用資料保留政策來控制儲存成本
- 即時分析用 streaming ingestion（延遲 < 1 秒）
- 整合 Azure Monitor 取得營運洞見

## 使用的 MCP 工具

| 工具 | 用途 |
|------|---------|
| `kusto_cluster_list` | 列出 subscription 裡所有 Azure Data Explorer 叢集 |
| `kusto_database_list` | 列出特定 Kusto 叢集裡所有資料庫 |
| `kusto_query` | 對 Kusto 資料庫執行 KQL 查詢 |
| `kusto_table_schema_get` | 取得特定 table 的 schema 資訊 |

**必要參數**：
- `subscription`：Azure subscription ID 或顯示名稱
- `cluster`：Kusto 叢集名稱（例如 "mycluster"）
- `database`：資料庫名稱
- `query`：KQL 查詢字串（查詢操作用）
- `table`：table 名稱（schema 操作用）

**選用參數**：
- `resource-group`：resource group 名稱（列表操作用）
- `tenant`：Azure AD tenant ID

## Fallback 策略：Azure CLI 指令

如果 Azure MCP 的 Kusto 工具失敗、逾時或不可用，就改用 Azure CLI 指令當 fallback。

### CLI 指令對照

| 操作 | Azure CLI 指令 |
|-----------|-------------------|
| 列出叢集 | `az kusto cluster list --resource-group <rg-name>` |
| 列出資料庫 | `az kusto database list --cluster-name <cluster> --resource-group <rg-name>` |
| 顯示叢集 | `az kusto cluster show --name <cluster> --resource-group <rg-name>` |
| 顯示資料庫 | `az kusto database show --cluster-name <cluster> --database-name <db> --resource-group <rg-name>` |

### 透過 Azure CLI 執行 KQL 查詢

查詢要用 Kusto REST API 或直接打叢集 URL：
```bash
az rest --method post \
  --url "https://<cluster>.<region>.kusto.windows.net/v1/rest/query" \
  --body "{ \"db\": \"<database>\", \"csl\": \"<kql-query>\" }"
```

### 何時改用 Fallback

遇到這些情況就切到 Azure CLI：
- MCP 工具回傳逾時錯誤（查詢超過 60 秒）
- MCP 工具回傳「service unavailable」或連線錯誤
- MCP 工具認證失敗
- 明明知道資料庫有資料，回應卻是空的

## 常見問題

- **Access Denied**：確認資料庫權限（查詢至少要 Viewer 角色）
- **Query Timeout**：用時間過濾最佳化查詢、縮小結果集，或調高 timeout
- **Syntax Error**：檢查 KQL 語法，常見問題是漏了 pipe、運算子用錯
- **Empty Results**：檢查時間範圍過濾（可能太嚴格），確認 table 名稱
- **Table Location Unknown**：先用 Pattern 6 批次搜尋所有候選來源，再下「資料不存在」的結論
- **Cluster Not Found**：檢查叢集名稱格式（不要加 ".kusto.windows.net" 後綴）
- **High CPU Usage**：查詢範圍太廣，加過濾條件、縮短時間範圍、減少聚合
- **Ingestion Lag**：串流資料依 ingestion 方式不同，可能有 1 到 30 秒的延遲

## 使用情境

- **Log 分析**：應用程式 log、系統 log、稽核 log
- **IoT 分析**：感測器資料、裝置遙測、即時監控
- **資安分析**：SIEM 資料、威脅偵測、資安事件關聯
- **APM**：應用程式效能指標、使用者行為、錯誤追蹤
- **商業智慧**：點擊流分析、使用者分析、營運 KPI
