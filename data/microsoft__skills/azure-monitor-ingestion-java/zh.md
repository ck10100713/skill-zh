---
name: azure-monitor-ingestion-java
description: |
  Java 版 Azure Monitor Ingestion SDK。透過 Data Collection Rules (DCR) 與 Data Collection Endpoints (DCE) 把自訂 log 送到 Azure Monitor。
  Triggers: "LogsIngestionClient java", "azure monitor ingestion java", "custom logs java", "DCR java", "data collection rule java".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: com.azure:azure-monitor-ingestion
---

# Azure Monitor Ingestion SDK for Java

用 Logs Ingestion API，透過 Data Collection Rules 把自訂 log 送到 Azure Monitor 的 client library。

## 安裝

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-monitor-ingestion</artifactId>
    <version>1.2.11</version>
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
        <artifactId>azure-monitor-ingestion</artifactId>
    </dependency>
</dependencies>
```

## 前置條件

- Data Collection Endpoint (DCE)
- Data Collection Rule (DCR)
- Log Analytics workspace
- 目標資料表（自訂或內建：CommonSecurityLog、SecurityEvents、Syslog、WindowsEvents）

## 環境變數

```bash
DATA_COLLECTION_ENDPOINT=https://<dce-name>.<region>.ingest.monitor.azure.com  # 所有驗證方式都必填
DATA_COLLECTION_RULE_ID=dcr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # log 上傳路由必填
STREAM_NAME=Custom-MyTable_CL  # 目標 DCR stream 必填
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境使用 DefaultAzureCredential 時才需要
```

## 建立 Client

### 同步 Client

```java
import com.azure.core.credential.TokenCredential;
import com.azure.identity.AzureIdentityEnvVars;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.identity.ManagedIdentityCredentialBuilder;
import com.azure.monitor.ingestion.LogsIngestionClient;
import com.azure.monitor.ingestion.LogsIngestionClientBuilder;

// 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
TokenCredential credential = new DefaultAzureCredentialBuilder()
    .requireEnvVars(AzureIdentityEnvVars.AZURE_TOKEN_CREDENTIALS)
    .build();
// 或在正式環境直接使用特定的 credential：
// See https://learn.microsoft.com/java/api/overview/azure/identity-readme?view=azure-java-stable#credential-classes
// TokenCredential credential = new ManagedIdentityCredentialBuilder().build();

LogsIngestionClient client = new LogsIngestionClientBuilder()
    .endpoint("<data-collection-endpoint>")
    .credential(credential)
    .buildClient();
```

### 非同步 Client

```java
import com.azure.monitor.ingestion.LogsIngestionAsyncClient;

LogsIngestionAsyncClient asyncClient = new LogsIngestionClientBuilder()
    .endpoint("<data-collection-endpoint>")
    .credential(credential)
    .buildAsyncClient();
```

## 關鍵概念

| 概念 | 說明 |
|---------|-------------|
| Data Collection Endpoint (DCE) | 你所在 region 的 ingestion endpoint URL |
| Data Collection Rule (DCR) | 定義資料轉換，以及要路由到哪些資料表 |
| Stream Name | DCR 中的目標 stream（例如 `Custom-MyTable_CL`） |
| Log Analytics Workspace | 匯入 log 的目的地 |

## 核心操作

### 上傳自訂 Log

```java
import java.util.List;
import java.util.ArrayList;

List<Object> logs = new ArrayList<>();
logs.add(new MyLogEntry("2024-01-15T10:30:00Z", "INFO", "Application started"));
logs.add(new MyLogEntry("2024-01-15T10:30:05Z", "DEBUG", "Processing request"));

client.upload("<data-collection-rule-id>", "<stream-name>", logs);
System.out.println("Logs uploaded successfully");
```

### 並行上傳

log 數量很大時，可以開啟並行上傳：

```java
import com.azure.monitor.ingestion.models.LogsUploadOptions;
import com.azure.core.util.Context;

List<Object> logs = getLargeLogs(); // 大量資料

LogsUploadOptions options = new LogsUploadOptions()
    .setMaxConcurrency(3);

client.upload("<data-collection-rule-id>", "<stream-name>", logs, options, Context.NONE);
```

### 上傳時處理錯誤

優雅地處理部分上傳失敗：

```java
LogsUploadOptions options = new LogsUploadOptions()
    .setLogsUploadErrorConsumer(uploadError -> {
        System.err.println("Upload error: " + uploadError.getResponseException().getMessage());
        System.err.println("Failed logs count: " + uploadError.getFailedLogs().size());
        
        // 選項 1：記錄後繼續
        // 選項 2：丟出例外，中止剩下的上傳
        // throw uploadError.getResponseException();
    });

client.upload("<data-collection-rule-id>", "<stream-name>", logs, options, Context.NONE);
```

### 搭配 Reactor 非同步上傳

```java
import reactor.core.publisher.Mono;

List<Object> logs = getLogs();

asyncClient.upload("<data-collection-rule-id>", "<stream-name>", logs)
    .doOnSuccess(v -> System.out.println("Upload completed"))
    .doOnError(e -> System.err.println("Upload failed: " + e.getMessage()))
    .subscribe();
```

## Log 項目 Model 範例

```java
public class MyLogEntry {
    private String timeGenerated;
    private String level;
    private String message;
    
    public MyLogEntry(String timeGenerated, String level, String message) {
        this.timeGenerated = timeGenerated;
        this.level = level;
        this.message = message;
    }
    
    // JSON 序列化需要 getter
    public String getTimeGenerated() { return timeGenerated; }
    public String getLevel() { return level; }
    public String getMessage() { return message; }
}
```

## 錯誤處理

```java
import com.azure.core.exception.HttpResponseException;

try {
    client.upload(ruleId, streamName, logs);
} catch (HttpResponseException e) {
    System.err.println("HTTP Status: " + e.getResponse().getStatusCode());
    System.err.println("Error: " + e.getMessage());
    
    if (e.getResponse().getStatusCode() == 403) {
        System.err.println("Check DCR permissions and managed identity");
    } else if (e.getResponse().getStatusCode() == 404) {
        System.err.println("Verify DCE endpoint and DCR ID");
    }
}
```

## 最佳實務

1. **批次上傳 log**：分批上傳，不要一筆一筆送
2. **使用並行**：大量上傳時設定 `maxConcurrency`
3. **處理部分失敗**：用 error consumer 記錄失敗的項目
4. **符合 DCR schema**：log 項目的欄位要符合 DCR 轉換的預期
5. **包含 TimeGenerated**：多數資料表都需要時間戳記欄位
6. **重複使用 client**：建立一次，整個應用程式共用
7. **高吞吐量用 async**：反應式模式用 `LogsIngestionAsyncClient`

## 查詢已上傳的 Log

用 [azure-monitor-query](../query/SKILL.md) 查詢已匯入的 log：

```java
// LogsQueryClient 的用法請看 azure-monitor-query skill
String query = "MyTable_CL | where TimeGenerated > ago(1h) | limit 10";
```

## 參考連結

| 資源 | URL |
|----------|-----|
| Maven 套件 | https://central.sonatype.com/artifact/com.azure/azure-monitor-ingestion |
| GitHub | https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/monitor/azure-monitor-ingestion |
| 產品文件 | https://learn.microsoft.com/azure/azure-monitor/logs/logs-ingestion-api-overview |
| DCE 概觀 | https://learn.microsoft.com/azure/azure-monitor/essentials/data-collection-endpoint-overview |
| DCR 概觀 | https://learn.microsoft.com/azure/azure-monitor/essentials/data-collection-rule-overview |
| 疑難排解 | https://github.com/Azure/azure-sdk-for-java/blob/main/sdk/monitor/azure-monitor-ingestion/TROUBLESHOOTING.md |
