---
name: azure-monitor-query-java
description: |
  Java 版 Azure Monitor Query SDK。對 Log Analytics workspace 執行 Kusto 查詢，並查詢 Azure 資源的 metric。
  Triggers: "LogsQueryClient java", "MetricsQueryClient java", "kusto query java", "log analytics java", "azure monitor query java".
  Note: 這個套件已棄用。請遷移到 azure-monitor-query-logs 與 azure-monitor-query-metrics。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: com.azure:azure-monitor-query
---

# Azure Monitor Query SDK for Java

> **棄用通知**：這個套件已棄用，請改用：
> - `azure-monitor-query-logs`：用於 Log Analytics 查詢
> - `azure-monitor-query-metrics`：用於 metric 查詢
>
> 遷移指南：[Logs 遷移](https://github.com/Azure/azure-sdk-for-java/blob/main/sdk/monitor/azure-monitor-query-logs/migration-guide.md) | [Metrics 遷移](https://github.com/Azure/azure-sdk-for-java/blob/main/sdk/monitor/azure-monitor-query-metrics/migration-guide.md)

用來查詢 Azure Monitor Logs 與 Metrics 的 client library。

## 安裝

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-monitor-query</artifactId>
    <version>1.5.9</version>
</dependency>
```

或使用 Azure SDK BOM：

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.azure</groupId>
            <artifactId>azure-sdk-bom</artifactId>
            <version>{bom_version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <dependency>
        <groupId>com.azure</groupId>
        <artifactId>azure-monitor-query</artifactId>
    </dependency>
</dependencies>
```

## 前置條件

- Log Analytics workspace（用於 log 查詢）
- Azure 資源（用於 metric 查詢）
- 具備適當權限的 TokenCredential

## 環境變數

```bash
LOG_ANALYTICS_WORKSPACE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  # 查詢 Log Analytics workspace 時必填
AZURE_RESOURCE_ID=/subscriptions/{sub}/resourceGroups/{rg}/providers/{provider}/{resource}  # 針對資源查詢 metric 時必填
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境使用 DefaultAzureCredential 時才需要
```

## 建立 Client

### LogsQueryClient（同步）

```java
import com.azure.core.credential.TokenCredential;
import com.azure.identity.AzureIdentityEnvVars;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.identity.ManagedIdentityCredentialBuilder;
import com.azure.monitor.query.LogsQueryClient;
import com.azure.monitor.query.LogsQueryClientBuilder;

// 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
TokenCredential credential = new DefaultAzureCredentialBuilder()
    .requireEnvVars(AzureIdentityEnvVars.AZURE_TOKEN_CREDENTIALS)
    .build();
// 或在正式環境直接使用特定的 credential：
// See https://learn.microsoft.com/java/api/overview/azure/identity-readme?view=azure-java-stable#credential-classes
// TokenCredential credential = new ManagedIdentityCredentialBuilder().build();

LogsQueryClient logsClient = new LogsQueryClientBuilder()
    .credential(credential)
    .buildClient();
```

### LogsQueryAsyncClient

```java
import com.azure.monitor.query.LogsQueryAsyncClient;

LogsQueryAsyncClient logsAsyncClient = new LogsQueryClientBuilder()
    .credential(credential)
    .buildAsyncClient();
```

### MetricsQueryClient（同步）

```java
import com.azure.monitor.query.MetricsQueryClient;
import com.azure.monitor.query.MetricsQueryClientBuilder;

MetricsQueryClient metricsClient = new MetricsQueryClientBuilder()
    .credential(credential)
    .buildClient();
```

### MetricsQueryAsyncClient

```java
import com.azure.monitor.query.MetricsQueryAsyncClient;

MetricsQueryAsyncClient metricsAsyncClient = new MetricsQueryClientBuilder()
    .credential(credential)
    .buildAsyncClient();
```

### 主權雲設定

```java
// Azure 中國雲：Logs
LogsQueryClient logsClient = new LogsQueryClientBuilder()
    .credential(credential)
    .endpoint("https://api.loganalytics.azure.cn/v1")
    .buildClient();

// Azure 中國雲：Metrics
MetricsQueryClient metricsClient = new MetricsQueryClientBuilder()
    .credential(credential)
    .endpoint("https://management.chinacloudapi.cn")
    .buildClient();
```

## 關鍵概念

| 概念 | 說明 |
|---------|-------------|
| Logs | 透過 Kusto Query Language 取得的 Azure 資源 log 與效能資料 |
| Metrics | 以固定間隔收集的數值時間序列資料 |
| Workspace ID | Log Analytics workspace 的識別碼 |
| Resource ID | 用於 metric 查詢的 Azure 資源 URI |
| QueryTimeInterval | 查詢的時間範圍 |

## Logs 查詢操作

### 基本查詢

```java
import com.azure.monitor.query.models.LogsQueryResult;
import com.azure.monitor.query.models.LogsTableRow;
import com.azure.monitor.query.models.QueryTimeInterval;
import java.time.Duration;

LogsQueryResult result = logsClient.queryWorkspace(
    "{workspace-id}",
    "AzureActivity | summarize count() by ResourceGroup | top 10 by count_",
    new QueryTimeInterval(Duration.ofDays(7))
);

for (LogsTableRow row : result.getTable().getRows()) {
    System.out.println(row.getColumnValue("ResourceGroup") + ": " + row.getColumnValue("count_"));
}
```

### 用 Resource ID 查詢

```java
LogsQueryResult result = logsClient.queryResource(
    "{resource-id}",
    "AzureMetrics | where TimeGenerated > ago(1h)",
    new QueryTimeInterval(Duration.ofDays(1))
);

for (LogsTableRow row : result.getTable().getRows()) {
    System.out.println(row.getColumnValue("MetricName") + " " + row.getColumnValue("Average"));
}
```

### 把結果對應到自訂 Model

```java
// 定義 model class
public class ActivityLog {
    private String resourceGroup;
    private String operationName;
    
    public String getResourceGroup() { return resourceGroup; }
    public String getOperationName() { return operationName; }
}

// 搭配 model mapping 查詢
List<ActivityLog> logs = logsClient.queryWorkspace(
    "{workspace-id}",
    "AzureActivity | project ResourceGroup, OperationName | take 100",
    new QueryTimeInterval(Duration.ofDays(2)),
    ActivityLog.class
);

for (ActivityLog log : logs) {
    System.out.println(log.getOperationName() + " - " + log.getResourceGroup());
}
```

### 批次查詢

```java
import com.azure.monitor.query.models.LogsBatchQuery;
import com.azure.monitor.query.models.LogsBatchQueryResult;
import com.azure.monitor.query.models.LogsBatchQueryResultCollection;
import com.azure.core.util.Context;

LogsBatchQuery batchQuery = new LogsBatchQuery();
String q1 = batchQuery.addWorkspaceQuery("{workspace-id}", "AzureActivity | count", new QueryTimeInterval(Duration.ofDays(1)));
String q2 = batchQuery.addWorkspaceQuery("{workspace-id}", "Heartbeat | count", new QueryTimeInterval(Duration.ofDays(1)));
String q3 = batchQuery.addWorkspaceQuery("{workspace-id}", "Perf | count", new QueryTimeInterval(Duration.ofDays(1)));

LogsBatchQueryResultCollection results = logsClient
    .queryBatchWithResponse(batchQuery, Context.NONE)
    .getValue();

LogsBatchQueryResult result1 = results.getResult(q1);
LogsBatchQueryResult result2 = results.getResult(q2);
LogsBatchQueryResult result3 = results.getResult(q3);

// 檢查是否有失敗
if (result3.getQueryResultStatus() == LogsQueryResultStatus.FAILURE) {
    System.err.println("Query failed: " + result3.getError().getMessage());
}
```

### 帶選項的查詢

```java
import com.azure.monitor.query.models.LogsQueryOptions;
import com.azure.core.http.rest.Response;

LogsQueryOptions options = new LogsQueryOptions()
    .setServerTimeout(Duration.ofMinutes(10))
    .setIncludeStatistics(true)
    .setIncludeVisualization(true);

Response<LogsQueryResult> response = logsClient.queryWorkspaceWithResponse(
    "{workspace-id}",
    "AzureActivity | summarize count() by bin(TimeGenerated, 1h)",
    new QueryTimeInterval(Duration.ofDays(7)),
    options,
    Context.NONE
);

LogsQueryResult result = response.getValue();

// 存取統計資料
BinaryData statistics = result.getStatistics();
// 存取視覺化資料
BinaryData visualization = result.getVisualization();
```

### 查詢多個 Workspace

```java
import java.util.Arrays;

LogsQueryOptions options = new LogsQueryOptions()
    .setAdditionalWorkspaces(Arrays.asList("{workspace-id-2}", "{workspace-id-3}"));

Response<LogsQueryResult> response = logsClient.queryWorkspaceWithResponse(
    "{workspace-id-1}",
    "AzureActivity | summarize count() by TenantId",
    new QueryTimeInterval(Duration.ofDays(1)),
    options,
    Context.NONE
);
```

## Metrics 查詢操作

### 基本 Metrics 查詢

```java
import com.azure.monitor.query.models.MetricsQueryResult;
import com.azure.monitor.query.models.MetricResult;
import com.azure.monitor.query.models.TimeSeriesElement;
import com.azure.monitor.query.models.MetricValue;
import java.util.Arrays;

MetricsQueryResult result = metricsClient.queryResource(
    "{resource-uri}",
    Arrays.asList("SuccessfulCalls", "TotalCalls")
);

for (MetricResult metric : result.getMetrics()) {
    System.out.println("Metric: " + metric.getMetricName());
    for (TimeSeriesElement ts : metric.getTimeSeries()) {
        System.out.println("  Dimensions: " + ts.getMetadata());
        for (MetricValue value : ts.getValues()) {
            System.out.println("    " + value.getTimeStamp() + ": " + value.getTotal());
        }
    }
}
```

### 帶聚合的 Metrics

```java
import com.azure.monitor.query.models.MetricsQueryOptions;
import com.azure.monitor.query.models.AggregationType;

Response<MetricsQueryResult> response = metricsClient.queryResourceWithResponse(
    "{resource-id}",
    Arrays.asList("SuccessfulCalls", "TotalCalls"),
    new MetricsQueryOptions()
        .setGranularity(Duration.ofHours(1))
        .setAggregations(Arrays.asList(AggregationType.AVERAGE, AggregationType.COUNT)),
    Context.NONE
);

MetricsQueryResult result = response.getValue();
```

### 查詢多個資源（MetricsClient）

```java
import com.azure.monitor.query.MetricsClient;
import com.azure.monitor.query.MetricsClientBuilder;
import com.azure.monitor.query.models.MetricsQueryResourcesResult;

MetricsClient metricsClient = new MetricsClientBuilder()
    .credential(new DefaultAzureCredentialBuilder().build())
    .endpoint("{endpoint}")
    .buildClient();

MetricsQueryResourcesResult result = metricsClient.queryResources(
    Arrays.asList("{resourceId1}", "{resourceId2}"),
    Arrays.asList("{metric1}", "{metric2}"),
    "{metricNamespace}"
);

for (MetricsQueryResult queryResult : result.getMetricsQueryResults()) {
    for (MetricResult metric : queryResult.getMetrics()) {
        System.out.println(metric.getMetricName());
        metric.getTimeSeries().stream()
            .flatMap(ts -> ts.getValues().stream())
            .forEach(mv -> System.out.println(
                mv.getTimeStamp() + " Count=" + mv.getCount() + " Avg=" + mv.getAverage()));
    }
}
```

## 回應結構

### Logs 回應階層

```
LogsQueryResult
├── statistics (BinaryData)
├── visualization (BinaryData)
├── error
└── tables (List<LogsTable>)
    ├── name
    ├── columns (List<LogsTableColumn>)
    │   ├── name
    │   └── type
    └── rows (List<LogsTableRow>)
        ├── rowIndex
        └── rowCells (List<LogsTableCell>)
```

### Metrics 回應階層

```
MetricsQueryResult
├── granularity
├── timeInterval
├── namespace
├── resourceRegion
└── metrics (List<MetricResult>)
    ├── id, name, type, unit
    └── timeSeries (List<TimeSeriesElement>)
        ├── metadata (dimensions)
        └── values (List<MetricValue>)
            ├── timeStamp
            ├── count, average, total
            ├── maximum, minimum
```

## 錯誤處理

```java
import com.azure.core.exception.HttpResponseException;
import com.azure.monitor.query.models.LogsQueryResultStatus;

try {
    LogsQueryResult result = logsClient.queryWorkspace(workspaceId, query, timeInterval);
    
    // 檢查部分失敗
    if (result.getStatus() == LogsQueryResultStatus.PARTIAL_FAILURE) {
        System.err.println("Partial failure: " + result.getError().getMessage());
    }
} catch (HttpResponseException e) {
    System.err.println("Query failed: " + e.getMessage());
    System.err.println("Status: " + e.getResponse().getStatusCode());
}
```

## 最佳實務

1. **使用批次查詢**：把多個查詢合併成一個請求
2. **設定適當的 timeout**：長查詢可能需要延長 server timeout
3. **限制結果大小**：在 Kusto 查詢裡用 `top` 或 `take`
4. **使用 projection**：用 `project` 只選需要的欄位
5. **檢查查詢狀態**：優雅地處理 PARTIAL_FAILURE 結果
6. **快取結果**：Metric 不會常變動，適合時就快取
7. **遷移到新套件**：規劃遷移到 `azure-monitor-query-logs` 與 `azure-monitor-query-metrics`

## 參考連結

| 資源 | URL |
|----------|-----|
| Maven 套件 | https://central.sonatype.com/artifact/com.azure/azure-monitor-query |
| GitHub | https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/monitor/azure-monitor-query |
| API 參考 | https://learn.microsoft.com/java/api/com.azure.monitor.query |
| Kusto Query Language | https://learn.microsoft.com/azure/data-explorer/kusto/query/ |
| Log Analytics 限制 | https://learn.microsoft.com/azure/azure-monitor/service-limits#la-query-api |
| 疑難排解 | https://github.com/Azure/azure-sdk-for-java/blob/main/sdk/monitor/azure-monitor-query/TROUBLESHOOTING.md |
