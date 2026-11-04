---
name: azure-monitor-query-py
description: |
  Python 版 Azure Monitor Query SDK。用於查詢 Log Analytics workspace 與 Azure Monitor metric。
  Triggers: "azure-monitor-query", "LogsQueryClient", "MetricsQueryClient", "Log Analytics", "Kusto queries", "Azure metrics".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-monitor-query
---

# Azure Monitor Query SDK for Python

查詢 Azure Monitor 與 Log Analytics workspace 的 log 和 metric。

## 安裝

```bash
pip install azure-monitor-query
```

## 環境變數

```bash
# Log Analytics
AZURE_LOG_ANALYTICS_WORKSPACE_ID=<workspace-id>  # log 查詢必填

# Metrics
AZURE_METRICS_RESOURCE_URI=/subscriptions/<sub>/resourceGroups/<rg>/providers/<provider>/<type>/<name>  # metric 查詢必填
AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境使用 DefaultAzureCredential 時才需要
```

## 驗證與生命週期

> **🔑 下面每一段程式碼都適用兩條規則：**
>
> 1. **優先使用 `DefaultAzureCredential`。** 它在本機（Azure CLI / VS Code / Developer CLI）和 Azure 上（managed identity、workload identity）都能運作，不用改程式碼。避免使用 connection string、account/API key，它們會繞過 Entra 的稽核與輪替。
>    - 本機開發：直接用 `DefaultAzureCredential` 即可。
>    - 正式環境：設定 `AZURE_TOKEN_CREDENTIALS=prod`（或 `AZURE_TOKEN_CREDENTIALS=<specific_credential>`），把 credential chain 限制在適合正式環境的 credential。
> 2. **每個 client 都要包在 context manager 裡**，這樣 HTTP transport、socket 和 token cache 才會確定性地被釋放：
>    - 同步：`with <Client>(...) as client:`
>    - 非同步：`async with <Client>(...) as client:` **以及** `async with DefaultAzureCredential() as credential:`（來自 `azure.identity.aio`）
>
> 範例程式碼可能會省略這段設定，但正式環境的程式碼一定要同時遵守這兩條規則。

```python
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential

# 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在正式環境直接使用特定的 credential：
# See https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()
```

## Logs Query Client

### 基本查詢

```python
from azure.monitor.query import LogsQueryClient
from datetime import timedelta

query = """
AppRequests
| where TimeGenerated > ago(1h)
| summarize count() by bin(TimeGenerated, 5m), ResultCode
| order by TimeGenerated desc
"""

with LogsQueryClient(credential) as client:
    response = client.query_workspace(
        workspace_id=os.environ["AZURE_LOG_ANALYTICS_WORKSPACE_ID"],
        query=query,
        timespan=timedelta(hours=1)
    )

    for table in response.tables:
        for row in table.rows:
            print(row)
```

### 指定時間範圍查詢

```python
from datetime import datetime, timezone

response = client.query_workspace(
    workspace_id=workspace_id,
    query="AppRequests | take 10",
    timespan=(
        datetime(2024, 1, 1, tzinfo=timezone.utc),
        datetime(2024, 1, 2, tzinfo=timezone.utc)
    )
)
```

### 轉成 DataFrame

```python
import pandas as pd

response = client.query_workspace(workspace_id, query, timespan=timedelta(hours=1))

if response.tables:
    table = response.tables[0]
    df = pd.DataFrame(data=table.rows, columns=[col.name for col in table.columns])
    print(df.head())
```

### 批次查詢

```python
from azure.monitor.query import LogsBatchQuery

queries = [
    LogsBatchQuery(workspace_id=workspace_id, query="AppRequests | take 5", timespan=timedelta(hours=1)),
    LogsBatchQuery(workspace_id=workspace_id, query="AppExceptions | take 5", timespan=timedelta(hours=1))
]

responses = client.query_batch(queries)

for response in responses:
    if response.tables:
        print(f"Rows: {len(response.tables[0].rows)}")
```

### 處理部分結果

```python
from azure.monitor.query import LogsQueryStatus

response = client.query_workspace(workspace_id, query, timespan=timedelta(hours=24))

if response.status == LogsQueryStatus.PARTIAL:
    print(f"Partial results: {response.partial_error}")
elif response.status == LogsQueryStatus.FAILURE:
    print(f"Query failed: {response.partial_error}")
```

## Metrics Query Client

### 查詢資源 Metric

```python
from azure.monitor.query import MetricsQueryClient
from datetime import timedelta

with MetricsQueryClient(credential) as metrics_client:
    response = metrics_client.query_resource(
        resource_uri=os.environ["AZURE_METRICS_RESOURCE_URI"],
        metric_names=["Percentage CPU", "Network In Total"],
        timespan=timedelta(hours=1),
        granularity=timedelta(minutes=5)
    )

    for metric in response.metrics:
        print(f"{metric.name}:")
        for time_series in metric.timeseries:
            for data in time_series.data:
                print(f"  {data.timestamp}: {data.average}")
```

### 聚合

```python
from azure.monitor.query import MetricAggregationType

response = metrics_client.query_resource(
    resource_uri=resource_uri,
    metric_names=["Requests"],
    timespan=timedelta(hours=1),
    aggregations=[
        MetricAggregationType.AVERAGE,
        MetricAggregationType.MAXIMUM,
        MetricAggregationType.MINIMUM,
        MetricAggregationType.COUNT
    ]
)
```

### 依維度過濾

```python
response = metrics_client.query_resource(
    resource_uri=resource_uri,
    metric_names=["Requests"],
    timespan=timedelta(hours=1),
    filter="ApiName eq 'GetBlob'"
)
```

### 列出 Metric 定義

```python
definitions = metrics_client.list_metric_definitions(resource_uri)
for definition in definitions:
    print(f"{definition.name}: {definition.unit}")
```

### 列出 Metric Namespace

```python
namespaces = metrics_client.list_metric_namespaces(resource_uri)
for ns in namespaces:
    print(ns.fully_qualified_namespace)
```

## 非同步 Client

```python
from azure.monitor.query.aio import LogsQueryClient, MetricsQueryClient
from azure.identity.aio import DefaultAzureCredential

async def query_logs():
    async with DefaultAzureCredential() as credential:
        async with LogsQueryClient(credential) as client:
            response = await client.query_workspace(
                workspace_id=workspace_id,
                query="AppRequests | take 10",
                timespan=timedelta(hours=1)
            )
            return response
```

## 常用 Kusto 查詢

```kusto
// 依狀態碼統計請求
AppRequests
| summarize count() by ResultCode
| order by count_ desc

// 例外隨時間的變化
AppExceptions
| summarize count() by bin(TimeGenerated, 1h)

// 慢請求
AppRequests
| where DurationMs > 1000
| project TimeGenerated, Name, DurationMs
| order by DurationMs desc

// 最常見的錯誤
AppExceptions
| summarize count() by ExceptionType
| top 10 by count_
```

## Client 類型

| Client | 用途 |
|--------|---------|
| `LogsQueryClient` | 查詢 Log Analytics workspace |
| `MetricsQueryClient` | 查詢 Azure Monitor metric |

## 最佳實務

1. **同步或非同步擇一，並保持一致。** 在同一條呼叫路徑裡，不要混用 `azure.xxx` 同步 client 和 `azure.xxx.aio` 非同步 client。每個 module 選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都包在 `with Client(...) as client:`（同步）或 `async with Client(...) as client:`（非同步）裡。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，這樣 token 和 transport 才會被清掉。
3. **使用 `DefaultAzureCredential`**，在本機開發和 Azure 之間都能通用（盡量避免 connection string / API key）。
4. **相對時間範圍用 timedelta**
4. **大型查詢要處理部分結果**
5. **要跑多個查詢時用批次查詢**
6. **替 metric 設定適當的 granularity**，減少資料點
7. **轉成 DataFrame**，資料分析比較方便
8. **用聚合**來彙總 metric 資料
9. **依維度過濾**，縮小 metric 結果範圍

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打功能、operation group 涵蓋範圍，以及正式環境檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 針對次要／進階情境的專屬非主打範例。 |
