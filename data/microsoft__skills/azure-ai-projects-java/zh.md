---
name: azure-ai-projects-java
description: |
  Azure AI Projects SDK（Java 版）。Azure AI Foundry project 管理的高階 SDK，包含 connection、dataset、index 和 evaluation。
  Triggers: "AIProjectClient java", "azure ai projects java", "Foundry project java", "ConnectionsClient", "DatasetsClient", "IndexesClient"。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: com.azure:azure-ai-projects
---

# Azure AI Projects SDK（Java）

Azure AI Foundry project 管理的高階 SDK，可存取 connection、dataset、index 和 evaluation。

## 安裝

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-ai-projects</artifactId>
    <version>1.0.0-beta.1</version>
</dependency>
```

## 環境變數

```bash
PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project> # project 設定必填
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境用 DefaultAzureCredential 時才需要
```

## 認證

```java
import com.azure.ai.projects.AIProjectClientBuilder;
import com.azure.core.credential.TokenCredential;
import com.azure.identity.AzureIdentityEnvVars;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.identity.ManagedIdentityCredentialBuilder;

TokenCredential credential = new DefaultAzureCredentialBuilder()
    .requireEnvVars(AzureIdentityEnvVars.AZURE_TOKEN_CREDENTIALS)
    .build();
// 或在正式環境直接使用指定的 credential：
// See https://learn.microsoft.com/java/api/overview/azure/identity-readme?view=azure-java-stable#credential-classes
// TokenCredential credential = new ManagedIdentityCredentialBuilder().build();

AIProjectClientBuilder builder = new AIProjectClientBuilder()
    .endpoint(System.getenv("PROJECT_ENDPOINT"))
    .credential(credential);
```

## Client 階層

這個 SDK 為不同的操作提供多個子 client：

| Client | 用途 |
|--------|---------|
| `ConnectionsClient` | 列舉已連接的 Azure 資源 |
| `DatasetsClient` | 上傳文件並管理 dataset |
| `DeploymentsClient` | 列舉 AI 模型 deployment |
| `IndexesClient` | 建立並管理 search index |
| `EvaluationsClient` | 執行 AI 模型 evaluation |
| `EvaluatorsClient` | 管理 evaluator 設定 |
| `SchedulesClient` | 管理排程操作 |

```java
// 從 builder 建立子 client
ConnectionsClient connectionsClient = builder.buildConnectionsClient();
DatasetsClient datasetsClient = builder.buildDatasetsClient();
DeploymentsClient deploymentsClient = builder.buildDeploymentsClient();
IndexesClient indexesClient = builder.buildIndexesClient();
EvaluationsClient evaluationsClient = builder.buildEvaluationsClient();
```

## 核心操作

### 列出 Connection

```java
import com.azure.ai.projects.models.Connection;
import com.azure.core.http.rest.PagedIterable;

PagedIterable<Connection> connections = connectionsClient.listConnections();
for (Connection connection : connections) {
    System.out.println("Name: " + connection.getName());
    System.out.println("Type: " + connection.getType());
    System.out.println("Credential Type: " + connection.getCredentials().getType());
}
```

### 列出 Index

```java
indexesClient.listLatest().forEach(index -> {
    System.out.println("Index name: " + index.getName());
    System.out.println("Version: " + index.getVersion());
    System.out.println("Description: " + index.getDescription());
});
```

### 建立或更新 Index

```java
import com.azure.ai.projects.models.AzureAISearchIndex;
import com.azure.ai.projects.models.Index;

String indexName = "my-index";
String indexVersion = "1.0";
String searchConnectionName = System.getenv("AI_SEARCH_CONNECTION_NAME");
String searchIndexName = System.getenv("AI_SEARCH_INDEX_NAME");

Index index = indexesClient.createOrUpdate(
    indexName,
    indexVersion,
    new AzureAISearchIndex()
        .setConnectionName(searchConnectionName)
        .setIndexName(searchIndexName)
);

System.out.println("Created index: " + index.getName());
```

### 存取 OpenAI Evaluation

這個 SDK 對外提供 OpenAI 官方 SDK 來做 evaluation：

```java
import com.openai.services.EvalService;

EvalService evalService = evaluationsClient.getOpenAIClient();
// 直接使用 OpenAI 的 evaluation API
```

## 最佳實務

1. 正式環境認證**用 DefaultAzureCredential**
2. **重複使用 client builder**，有效率地建立多個子 client
3. 用 `PagedIterable` 列舉資源時要**處理分頁**
4. connection 名稱和設定都**用環境變數**
5. 存取憑證之前先**檢查 connection 類型**

## 錯誤處理

```java
import com.azure.core.exception.HttpResponseException;
import com.azure.core.exception.ResourceNotFoundException;

try {
    Index index = indexesClient.get(indexName, version);
} catch (ResourceNotFoundException e) {
    System.err.println("Index not found: " + indexName);
} catch (HttpResponseException e) {
    System.err.println("Error: " + e.getResponse().getStatusCode());
}
```

## 參考連結

| 資源 | URL |
|----------|-----|
| 產品文件 | https://learn.microsoft.com/azure/ai-studio/ |
| API 參考 | https://learn.microsoft.com/rest/api/aifoundry/aiprojects/ |
| GitHub 原始碼 | https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/ai/azure-ai-projects |
| 範例 | https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/ai/azure-ai-projects/src/samples |
