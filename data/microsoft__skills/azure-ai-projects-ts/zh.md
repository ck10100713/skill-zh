---
name: azure-ai-projects-ts
description: 用 Azure AI Projects SDK（JavaScript 版，@azure/ai-projects）建立 AI 應用程式。在使用 Foundry project client、agent、connection、deployment、dataset、index、evaluation，或取得 OpenAI client 時使用。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: '@azure/ai-projects'
---

# Azure AI Projects SDK（TypeScript）

Azure AI Foundry project 的高階 SDK，包含 agent、connection、deployment 和 evaluation。

## 安裝

```bash
npm install @azure/ai-projects @azure/identity
```

要做 tracing：
```bash
npm install @azure/monitor-opentelemetry @opentelemetry/api
```

## 環境變數

```bash
AZURE_AI_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
MODEL_DEPLOYMENT_NAME=gpt-4o
AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境用 DefaultAzureCredential 時才需要
```

## 認證

```typescript
import { AIProjectClient } from "@azure/ai-projects";
import { DefaultAzureCredential, ManagedIdentityCredential } from "@azure/identity";

// 本機開發：用 DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
const credential = new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]});
// 或在正式環境直接使用指定的 credential：
// See https://learn.microsoft.com/javascript/api/overview/azure/identity-readme?view=azure-node-latest#credential-classes
// const credential = new ManagedIdentityCredential();

const client = new AIProjectClient(
  process.env.AZURE_AI_PROJECT_ENDPOINT!,
  credential
);
```

## 操作群組

| 群組 | 用途 |
|-------|---------|
| `client.agents` | 建立並管理 AI agent |
| `client.connections` | 列出已連接的 Azure 資源 |
| `client.deployments` | 列出模型 deployment |
| `client.datasets` | 上傳並管理 dataset |
| `client.indexes` | 建立並管理 search index |
| `client.evaluators` | 管理 evaluation 指標 |
| `client.memoryStores` | 管理 agent 記憶 |

## 取得 OpenAI Client

```typescript
const openAIClient = await client.getOpenAIClient();

// 用來產生 response
const response = await openAIClient.responses.create({
  model: "gpt-4o",
  input: "What is the capital of France?"
});

// 用來處理 conversation
const conversation = await openAIClient.conversations.create({
  items: [{ type: "message", role: "user", content: "Hello!" }]
});
```

## Agent

### 建立 Agent

```typescript
const agent = await client.agents.createVersion("my-agent", {
  kind: "prompt",
  model: "gpt-4o",
  instructions: "You are a helpful assistant."
});
```

### 帶工具的 Agent

```typescript
// Code Interpreter
const agent = await client.agents.createVersion("code-agent", {
  kind: "prompt",
  model: "gpt-4o",
  instructions: "You can execute code.",
  tools: [{ type: "code_interpreter", container: { type: "auto" } }]
});

// File Search
const agent = await client.agents.createVersion("search-agent", {
  kind: "prompt",
  model: "gpt-4o",
  tools: [{ type: "file_search", vector_store_ids: [vectorStoreId] }]
});

// Web Search
const agent = await client.agents.createVersion("web-agent", {
  kind: "prompt",
  model: "gpt-4o",
  tools: [{
    type: "web_search_preview",
    user_location: { type: "approximate", country: "US", city: "Seattle" }
  }]
});

// Azure AI Search
const agent = await client.agents.createVersion("aisearch-agent", {
  kind: "prompt",
  model: "gpt-4o",
  tools: [{
    type: "azure_ai_search",
    azure_ai_search: {
      indexes: [{
        project_connection_id: connectionId,
        index_name: "my-index",
        query_type: "simple"
      }]
    }
  }]
});

// Function Tool
const agent = await client.agents.createVersion("func-agent", {
  kind: "prompt",
  model: "gpt-4o",
  tools: [{
    type: "function",
    function: {
      name: "get_weather",
      description: "Get weather for a location",
      strict: true,
      parameters: {
        type: "object",
        properties: { location: { type: "string" } },
        required: ["location"]
      }
    }
  }]
});

// MCP Tool
const agent = await client.agents.createVersion("mcp-agent", {
  kind: "prompt",
  model: "gpt-4o",
  tools: [{
    type: "mcp",
    server_label: "my-mcp",
    server_url: "https://mcp-server.example.com",
    require_approval: "always"
  }]
});
```

### 執行 Agent

```typescript
const openAIClient = await client.getOpenAIClient();

// 建立 conversation
const conversation = await openAIClient.conversations.create({
  items: [{ type: "message", role: "user", content: "Hello!" }]
});

// 用 agent 產生 response
const response = await openAIClient.responses.create(
  { conversation: conversation.id },
  { body: { agent: { name: agent.name, type: "agent_reference" } } }
);

// 清理
await openAIClient.conversations.delete(conversation.id);
await client.agents.deleteVersion(agent.name, agent.version);
```

## Connection

```typescript
// 列出所有 connection
for await (const conn of client.connections.list()) {
  console.log(conn.name, conn.type);
}

// 用名稱取得 connection
const conn = await client.connections.get("my-connection");

// 取得含憑證的 connection
const connWithCreds = await client.connections.getWithCredentials("my-connection");

// 依類型取得預設 connection
const defaultAzureOpenAI = await client.connections.getDefault("AzureOpenAI", true);
```

## Deployment

```typescript
// 列出所有 deployment
for await (const deployment of client.deployments.list()) {
  if (deployment.type === "ModelDeployment") {
    console.log(deployment.name, deployment.modelName);
  }
}

// 依發行者過濾
for await (const d of client.deployments.list({ modelPublisher: "OpenAI" })) {
  console.log(d.name);
}

// 取得指定的 deployment
const deployment = await client.deployments.get("gpt-4o");
```

## Dataset

```typescript
// 上傳單一檔案
const dataset = await client.datasets.uploadFile(
  "my-dataset",
  "1.0",
  "./data/training.jsonl"
);

// 上傳資料夾
const dataset = await client.datasets.uploadFolder(
  "my-dataset",
  "2.0",
  "./data/documents/"
);

// 取得 dataset
const ds = await client.datasets.get("my-dataset", "1.0");

// 列出版本
for await (const version of client.datasets.listVersions("my-dataset")) {
  console.log(version);
}

// 刪除
await client.datasets.delete("my-dataset", "1.0");
```

## Index

```typescript
import { AzureAISearchIndex } from "@azure/ai-projects";

const indexConfig: AzureAISearchIndex = {
  name: "my-index",
  type: "AzureSearch",
  version: "1",
  indexName: "my-index",
  connectionName: "search-connection"
};

// 建立 index
const index = await client.indexes.createOrUpdate("my-index", "1", indexConfig);

// 列出 index
for await (const idx of client.indexes.list()) {
  console.log(idx.name);
}

// 刪除
await client.indexes.delete("my-index", "1");
```

## 主要型別

```typescript
import {
  AIProjectClient,
  AIProjectClientOptionalParams,
  Connection,
  ModelDeployment,
  DatasetVersionUnion,
  AzureAISearchIndex
} from "@azure/ai-projects";
```

## 最佳實務

1. **使用 getOpenAIClient()**：用於 response、conversation、檔案和 vector store
2. **替 agent 做版本管理**：用 `createVersion` 讓 agent 定義可以重現
3. **清理資源**：用完就刪掉 agent 和 conversation
4. **使用 connection**：從 project connection 取得憑證，不要寫死在程式碼裡
5. **過濾 deployment**：用 `modelPublisher` 過濾器找特定的模型
