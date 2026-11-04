---
name: azure-ai-agents-persistent-dotnet
description: |
  Azure AI Agents Persistent SDK（.NET 版）。用來建立和管理 AI agent 的低階 SDK，包含 thread、message、run 和工具。用於 agent 的 CRUD、對話 thread、串流回應、function calling、file search 和 code interpreter。Triggers: "PersistentAgentsClient", "persistent agents", "agent threads", "agent runs", "streaming agents", "function calling agents .NET"。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.AI.Agents.Persistent
---

# Azure.AI.Agents.Persistent（.NET）

用來建立和管理持久化 AI agent 的低階 SDK，包含 thread、message、run 和工具。

## 安裝

```bash
dotnet add package Azure.AI.Agents.Persistent --prerelease
dotnet add package Azure.Identity
```

**目前版本**：穩定版 v1.1.0，預覽版 v1.2.0-beta.8

## 環境變數

```bash
PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>  # 必填：Azure AI project endpoint
MODEL_DEPLOYMENT_NAME=gpt-4o-mini  # 必填：model deployment 名稱
AZURE_BING_CONNECTION_ID=<bing-connection-resource-id>  # 必填：Bing connection 資源 ID
AZURE_AI_SEARCH_CONNECTION_ID=<search-connection-resource-id>  # 必填：Azure AI Search connection 資源 ID
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境用 DefaultAzureCredential 時才需要
```

## 認證

```csharp
using Azure.AI.Agents.Persistent;
using Azure.Identity;

var projectEndpoint = Environment.GetEnvironmentVariable("PROJECT_ENDPOINT");
// 本機開發：用 DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
var credential = new DefaultAzureCredential(
    DefaultAzureCredential.DefaultEnvironmentVariableName
);
// 或在正式環境直接使用指定的 credential：
// See https://learn.microsoft.com/dotnet/api/overview/azure/identity-readme?view=azure-dotnet#credential-classes
// var credential = new ManagedIdentityCredential();
PersistentAgentsClient client = new(projectEndpoint, credential);
```

## Client 階層

```
PersistentAgentsClient
├── Administration  → Agent CRUD 操作
├── Threads         → Thread 管理
├── Messages        → Message 操作
├── Runs            → Run 執行與串流
├── Files           → 檔案上傳／下載
└── VectorStores    → Vector store 管理
```

## 核心流程

### 1. 建立 Agent

```csharp
var modelDeploymentName = Environment.GetEnvironmentVariable("MODEL_DEPLOYMENT_NAME");

PersistentAgent agent = await client.Administration.CreateAgentAsync(
    model: modelDeploymentName,
    name: "Math Tutor",
    instructions: "You are a personal math tutor. Write and run code to answer math questions.",
    tools: [new CodeInterpreterToolDefinition()]
);
```

### 2. 建立 Thread 和 Message

```csharp
// 建立 thread
PersistentAgentThread thread = await client.Threads.CreateThreadAsync();

// 建立 message
await client.Messages.CreateMessageAsync(
    thread.Id,
    MessageRole.User,
    "I need to solve the equation `3x + 11 = 14`. Can you help me?"
);
```

### 3. 執行 Agent（輪詢）

```csharp
// 建立 run
ThreadRun run = await client.Runs.CreateRunAsync(
    thread.Id,
    agent.Id,
    additionalInstructions: "Please address the user as Jane Doe."
);

// 輪詢直到完成
do
{
    await Task.Delay(TimeSpan.FromMilliseconds(500));
    run = await client.Runs.GetRunAsync(thread.Id, run.Id);
}
while (run.Status == RunStatus.Queued || run.Status == RunStatus.InProgress);

// 取得 messages
await foreach (PersistentThreadMessage message in client.Messages.GetMessagesAsync(
    threadId: thread.Id, 
    order: ListSortOrder.Ascending))
{
    Console.Write($"{message.Role}: ");
    foreach (MessageContent content in message.ContentItems)
    {
        if (content is MessageTextContent textContent)
            Console.WriteLine(textContent.Text);
    }
}
```

### 4. 串流回應

```csharp
AsyncCollectionResult<StreamingUpdate> stream = client.Runs.CreateRunStreamingAsync(
    thread.Id, 
    agent.Id
);

await foreach (StreamingUpdate update in stream)
{
    if (update.UpdateKind == StreamingUpdateReason.RunCreated)
    {
        Console.WriteLine("--- Run started! ---");
    }
    else if (update is MessageContentUpdate contentUpdate)
    {
        Console.Write(contentUpdate.Text);
    }
    else if (update.UpdateKind == StreamingUpdateReason.RunCompleted)
    {
        Console.WriteLine("\n--- Run completed! ---");
    }
}
```

### 5. Function Calling

```csharp
// 定義 function tool
FunctionToolDefinition weatherTool = new(
    name: "getCurrentWeather",
    description: "Gets the current weather at a location.",
    parameters: BinaryData.FromObjectAsJson(new
    {
        Type = "object",
        Properties = new
        {
            Location = new { Type = "string", Description = "City and state, e.g. San Francisco, CA" },
            Unit = new { Type = "string", Enum = new[] { "c", "f" } }
        },
        Required = new[] { "location" }
    }, new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.CamelCase })
);

// 建立帶 function 的 agent
PersistentAgent agent = await client.Administration.CreateAgentAsync(
    model: modelDeploymentName,
    name: "Weather Bot",
    instructions: "You are a weather bot.",
    tools: [weatherTool]
);

// 在輪詢期間處理 function call
do
{
    await Task.Delay(500);
    run = await client.Runs.GetRunAsync(thread.Id, run.Id);

    if (run.Status == RunStatus.RequiresAction 
        && run.RequiredAction is SubmitToolOutputsAction submitAction)
    {
        List<ToolOutput> outputs = [];
        foreach (RequiredToolCall toolCall in submitAction.ToolCalls)
        {
            if (toolCall is RequiredFunctionToolCall funcCall)
            {
                // 執行函式並取得結果
                string result = ExecuteFunction(funcCall.Name, funcCall.Arguments);
                outputs.Add(new ToolOutput(toolCall, result));
            }
        }
        run = await client.Runs.SubmitToolOutputsToRunAsync(run, outputs, toolApprovals: null);
    }
}
while (run.Status == RunStatus.Queued || run.Status == RunStatus.InProgress);
```

### 6. 搭配 Vector Store 的 File Search

```csharp
// 上傳檔案
PersistentAgentFileInfo file = await client.Files.UploadFileAsync(
    filePath: "document.txt",
    purpose: PersistentAgentFilePurpose.Agents
);

// 建立 vector store
PersistentAgentsVectorStore vectorStore = await client.VectorStores.CreateVectorStoreAsync(
    fileIds: [file.Id],
    name: "my_vector_store"
);

// 建立 file search 資源
FileSearchToolResource fileSearchResource = new();
fileSearchResource.VectorStoreIds.Add(vectorStore.Id);

// 建立帶 file search 的 agent
PersistentAgent agent = await client.Administration.CreateAgentAsync(
    model: modelDeploymentName,
    name: "Document Assistant",
    instructions: "You help users find information in documents.",
    tools: [new FileSearchToolDefinition()],
    toolResources: new ToolResources { FileSearch = fileSearchResource }
);
```

### 7. Bing Grounding

```csharp
var bingConnectionId = Environment.GetEnvironmentVariable("AZURE_BING_CONNECTION_ID");

BingGroundingToolDefinition bingTool = new(
    new BingGroundingSearchToolParameters(
        [new BingGroundingSearchConfiguration(bingConnectionId)]
    )
);

PersistentAgent agent = await client.Administration.CreateAgentAsync(
    model: modelDeploymentName,
    name: "Search Agent",
    instructions: "Use Bing to answer questions about current events.",
    tools: [bingTool]
);
```

### 8. Azure AI Search

```csharp
AzureAISearchToolResource searchResource = new(
    connectionId: searchConnectionId,
    indexName: "my_index",
    topK: 5,
    filter: "category eq 'documentation'",
    queryType: AzureAISearchQueryType.Simple
);

PersistentAgent agent = await client.Administration.CreateAgentAsync(
    model: modelDeploymentName,
    name: "Search Agent",
    instructions: "Search the documentation index to answer questions.",
    tools: [new AzureAISearchToolDefinition()],
    toolResources: new ToolResources { AzureAISearch = searchResource }
);
```

### 9. 清理

```csharp
await client.Threads.DeleteThreadAsync(thread.Id);
await client.Administration.DeleteAgentAsync(agent.Id);
await client.VectorStores.DeleteVectorStoreAsync(vectorStore.Id);
await client.Files.DeleteFileAsync(file.Id);
```

## 可用工具

| 工具 | Class | 用途 |
|------|-------|---------|
| Code Interpreter | `CodeInterpreterToolDefinition` | 執行 Python 程式碼、產生視覺化圖表 |
| File Search | `FileSearchToolDefinition` | 透過 vector store 搜尋上傳的檔案 |
| Function Calling | `FunctionToolDefinition` | 呼叫自訂函式 |
| Bing Grounding | `BingGroundingToolDefinition` | 透過 Bing 搜尋網頁 |
| Azure AI Search | `AzureAISearchToolDefinition` | 搜尋 Azure AI Search 的 index |
| OpenAPI | `OpenApiToolDefinition` | 透過 OpenAPI 規格呼叫外部 API |
| Azure Functions | `AzureFunctionToolDefinition` | 呼叫 Azure Functions |
| MCP | `MCPToolDefinition` | Model Context Protocol 工具 |
| SharePoint | `SharepointToolDefinition` | 存取 SharePoint 內容 |
| Microsoft Fabric | `MicrosoftFabricToolDefinition` | 存取 Fabric 資料 |

## 串流更新類型

| 更新類型 | 說明 |
|-------------|-------------|
| `StreamingUpdateReason.RunCreated` | Run 開始 |
| `StreamingUpdateReason.RunInProgress` | Run 處理中 |
| `StreamingUpdateReason.RunCompleted` | Run 完成 |
| `StreamingUpdateReason.RunFailed` | Run 發生錯誤 |
| `MessageContentUpdate` | 文字內容片段 |
| `RunStepUpdate` | 步驟狀態變更 |

## 主要型別參考

| 型別 | 用途 |
|------|---------|
| `PersistentAgentsClient` | 主要進入點 |
| `PersistentAgent` | 含 model、instructions、工具的 agent |
| `PersistentAgentThread` | 對話 thread |
| `PersistentThreadMessage` | Thread 裡的 message |
| `ThreadRun` | 對 thread 執行 agent |
| `RunStatus` | Queued、InProgress、RequiresAction、Completed、Failed |
| `ToolResources` | 合併的工具資源 |
| `ToolOutput` | Function call 的回應 |

## 最佳實務

1. **一定要 dispose client**：用 `using` 陳述式或明確 dispose
2. **輪詢要有適當的間隔**：建議每次狀態檢查間隔 500ms
3. **清理資源**：用完就刪掉 thread 和 agent
4. **處理所有 run 狀態**：檢查 `RequiresAction`、`Failed`、`Cancelled`
5. **要即時體驗就用串流**：使用者體驗比輪詢好
6. **存 ID，不要存物件**：用 ID 參照 agent／thread
7. **用非同步方法**：所有操作都應該是非同步的

## 錯誤處理

```csharp
using Azure;

try
{
    var agent = await client.Administration.CreateAgentAsync(...);
}
catch (RequestFailedException ex) when (ex.Status == 404)
{
    Console.WriteLine("Resource not found");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Error: {ex.Status} - {ex.ErrorCode}: {ex.Message}");
}
```

## 相關 SDK

| SDK | 用途 | 安裝 |
|-----|---------|---------|
| `Azure.AI.Agents.Persistent` | 低階 agent（本 SDK） | `dotnet add package Azure.AI.Agents.Persistent` |
| `Azure.AI.Projects` | 高階的 project client | `dotnet add package Azure.AI.Projects` |

## 參考連結

| 資源 | URL |
|----------|-----|
| NuGet 套件 | https://www.nuget.org/packages/Azure.AI.Agents.Persistent |
| API 參考 | https://learn.microsoft.com/dotnet/api/azure.ai.agents.persistent |
| GitHub 原始碼 | https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/ai/Azure.AI.Agents.Persistent |
| 範例 | https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/ai/Azure.AI.Agents.Persistent/samples |
