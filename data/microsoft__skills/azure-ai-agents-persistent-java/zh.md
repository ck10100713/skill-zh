---
name: azure-ai-agents-persistent-java
description: |
  Azure AI Agents Persistent SDK（Java 版）。用來建立和管理 AI agent 的低階 SDK，包含 thread、message、run 和工具。
  Triggers: "PersistentAgentsClient", "persistent agents java", "agent threads java", "agent runs java", "streaming agents java"。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: com.azure:azure-ai-agents-persistent
---

# Azure AI Agents Persistent SDK（Java）

用來建立和管理持久化 AI agent 的低階 SDK，包含 thread、message、run 和工具。

## 安裝

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-ai-agents-persistent</artifactId>
    <version>1.0.0-beta.1</version>
</dependency>
```

## 環境變數

```bash
PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project> # project 設定必填
MODEL_DEPLOYMENT_NAME=gpt-4o-mini # 選擇 agent 的 model 時必填
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境用 DefaultAzureCredential 時才需要
```

## 認證

```java
import com.azure.ai.agents.persistent.PersistentAgentsClient;
import com.azure.ai.agents.persistent.PersistentAgentsClientBuilder;
import com.azure.core.credential.TokenCredential;
import com.azure.identity.AzureIdentityEnvVars;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.identity.ManagedIdentityCredentialBuilder;

String endpoint = System.getenv("PROJECT_ENDPOINT");
TokenCredential credential = new DefaultAzureCredentialBuilder()
    .requireEnvVars(AzureIdentityEnvVars.AZURE_TOKEN_CREDENTIALS)
    .build();
// 或在正式環境直接使用指定的 credential：
// See https://learn.microsoft.com/java/api/overview/azure/identity-readme?view=azure-java-stable#credential-classes
// TokenCredential credential = new ManagedIdentityCredentialBuilder().build();

PersistentAgentsClient client = new PersistentAgentsClientBuilder()
    .endpoint(endpoint)
    .credential(credential)
    .buildClient();
```

## 核心概念

Azure AI Agents Persistent SDK 提供低階 API，用來管理可以跨 session 重複使用的持久化 agent。

### Client 階層

| Client | 用途 |
|--------|---------|
| `PersistentAgentsClient` | 處理 agent 操作的同步 client |
| `PersistentAgentsAsyncClient` | 處理 agent 操作的非同步 client |

## 核心流程

### 1. 建立 Agent

```java
// 建立帶工具的 agent
PersistentAgent agent = client.createAgent(
    modelDeploymentName,
    "Math Tutor",
    "You are a personal math tutor."
);
```

### 2. 建立 Thread

```java
PersistentAgentThread thread = client.createThread();
```

### 3. 加入 Message

```java
client.createMessage(
    thread.getId(),
    MessageRole.USER,
    "I need help with equations."
);
```

### 4. 執行 Agent

```java
ThreadRun run = client.createRun(thread.getId(), agent.getId());

// 輪詢直到完成
while (run.getStatus() == RunStatus.QUEUED || run.getStatus() == RunStatus.IN_PROGRESS) {
    Thread.sleep(500);
    run = client.getRun(thread.getId(), run.getId());
}
```

### 5. 取得回應

```java
PagedIterable<PersistentThreadMessage> messages = client.listMessages(thread.getId());
for (PersistentThreadMessage message : messages) {
    System.out.println(message.getRole() + ": " + message.getContent());
}
```

### 6. 清理

```java
client.deleteThread(thread.getId());
client.deleteAgent(agent.getId());
```

## 最佳實務

1. 正式環境認證**用 DefaultAzureCredential**
2. **輪詢要有適當的間隔**：建議每次狀態檢查間隔 500ms
3. **清理資源**：用完就刪掉 thread 和 agent
4. **處理所有 run 狀態**：檢查 RequiresAction、Failed、Cancelled
5. 高併發情境下**用非同步 client** 可以有比較好的吞吐量

## 錯誤處理

```java
import com.azure.core.exception.HttpResponseException;

try {
    PersistentAgent agent = client.createAgent(modelName, name, instructions);
} catch (HttpResponseException e) {
    System.err.println("Error: " + e.getResponse().getStatusCode() + " - " + e.getMessage());
}
```

## 參考連結

| 資源 | URL |
|----------|-----|
| Maven 套件 | https://central.sonatype.com/artifact/com.azure/azure-ai-agents-persistent |
| GitHub 原始碼 | https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/ai/azure-ai-agents-persistent |
