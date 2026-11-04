---
name: azure-ai-projects-dotnet
description: |
  Azure AI Projects SDK（.NET 版）。Azure AI Foundry project 的高階 client，涵蓋 agent、connection、dataset、deployment、evaluation 和 index。用於 AI Foundry project 管理、版本化 agent 和編排。Triggers: "AI Projects", "AIProjectClient", "Foundry project", "versioned agents", "evaluations", "datasets", "connections", "deployments .NET"。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.AI.Projects
---

# Azure.AI.Projects（.NET）

Azure AI Foundry project 操作的高階 SDK，包含 agent、connection、dataset、deployment、evaluation 和 index。

## 安裝

```bash
dotnet add package Azure.AI.Projects
dotnet add package Azure.Identity

# 選用：版本化 agent 搭配 OpenAI 擴充時需要
dotnet add package Azure.AI.Projects.OpenAI --prerelease

# 選用：低階 agent 操作時需要
dotnet add package Azure.AI.Agents.Persistent --prerelease
```

**目前版本**：GA v1.1.0，預覽版 v1.2.0-beta.5

## 環境變數

```bash
PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>  # 必填：Azure AI project endpoint
MODEL_DEPLOYMENT_NAME=gpt-4o-mini  # 必填：model deployment 名稱
CONNECTION_NAME=<your-connection-name>  # 選填：project connection 名稱
AI_SEARCH_CONNECTION_NAME=<ai-search-connection>  # 選填：Azure AI Search connection 名稱
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境用 DefaultAzureCredential 時才需要
```

## 認證

```csharp
using Azure.Identity;
using Azure.AI.Projects;

var endpoint = Environment.GetEnvironmentVariable("PROJECT_ENDPOINT");
// 本機開發：用 DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
var credential = new DefaultAzureCredential(
    DefaultAzureCredential.DefaultEnvironmentVariableName
);
// 或在正式環境直接使用指定的 credential：
// See https://learn.microsoft.com/dotnet/api/overview/azure/identity-readme?view=azure-dotnet#credential-classes
// var credential = new ManagedIdentityCredential();
AIProjectClient projectClient = new AIProjectClient(
    new Uri(endpoint), 
    credential);
```

## Client 階層

```
AIProjectClient
├── Agents          → AIProjectAgentsOperations（版本化 agent）
├── Connections     → ConnectionsClient
├── Datasets        → DatasetsClient
├── Deployments     → DeploymentsClient
├── Evaluations     → EvaluationsClient
├── Evaluators      → EvaluatorsClient
├── Indexes         → IndexesClient
├── Telemetry       → AIProjectTelemetry
├── OpenAI          → ProjectOpenAIClient（預覽）
└── GetPersistentAgentsClient() → PersistentAgentsClient
```

## 核心流程

### 1. 取得 Persistent Agents Client

```csharp
// 從 project client 取得低階 agents client
PersistentAgentsClient agentsClient = projectClient.GetPersistentAgentsClient();

// 建立 agent
PersistentAgent agent = await agentsClient.Administration.CreateAgentAsync(
    model: "gpt-4o-mini",
    name: "Math Tutor",
    instructions: "You are a personal math tutor.");

// 建立 thread and run
PersistentAgentThread thread = await agentsClient.Threads.CreateThreadAsync();
await agentsClient.Messages.CreateMessageAsync(thread.Id, MessageRole.User, "Solve 3x + 11 = 14");
ThreadRun run = await agentsClient.Runs.CreateRunAsync(thread.Id, agent.Id);

// 輪詢直到完成
do
{
    await Task.Delay(500);
    run = await agentsClient.Runs.GetRunAsync(thread.Id, run.Id);
}
while (run.Status == RunStatus.Queued || run.Status == RunStatus.InProgress);

// 取得 messages
await foreach (var msg in agentsClient.Messages.GetMessagesAsync(thread.Id))
{
    foreach (var content in msg.ContentItems)
    {
        if (content is MessageTextContent textContent)
            Console.WriteLine(textContent.Text);
    }
}

// 清理
await agentsClient.Threads.DeleteThreadAsync(thread.Id);
await agentsClient.Administration.DeleteAgentAsync(agent.Id);
```

### 2. 帶工具的版本化 Agent（預覽）

```csharp
using Azure.AI.Projects.OpenAI;

// 建立帶網頁搜尋工具的 agent
PromptAgentDefinition agentDefinition = new(model: "gpt-4o-mini")
{
    Instructions = "You are a helpful assistant that can search the web",
    Tools = {
        ResponseTool.CreateWebSearchTool(
            userLocation: WebSearchToolLocation.CreateApproximateLocation(
                country: "US",
                city: "Seattle",
                region: "Washington"
            )
        ),
    }
};

AgentVersion agentVersion = await projectClient.Agents.CreateAgentVersionAsync(
    agentName: "myAgent",
    options: new(agentDefinition));

// 取得 response client
ProjectResponsesClient responseClient = projectClient.OpenAI.GetProjectResponsesClientForAgent(agentVersion.Name);

// 建立 response
ResponseResult response = responseClient.CreateResponse("What's the weather in Seattle?");
Console.WriteLine(response.GetOutputText());

// 清理
projectClient.Agents.DeleteAgentVersion(agentName: agentVersion.Name, agentVersion: agentVersion.Version);
```

### 3. Connection

```csharp
// 列出所有 connection
foreach (AIProjectConnection connection in projectClient.Connections.GetConnections())
{
    Console.WriteLine($"{connection.Name}: {connection.ConnectionType}");
}

// 取得指定的 connection
AIProjectConnection conn = projectClient.Connections.GetConnection(
    connectionName, 
    includeCredentials: true);

// 取得預設 connection
AIProjectConnection defaultConn = projectClient.Connections.GetDefaultConnection(
    includeCredentials: false);
```

### 4. Deployment

```csharp
// 列出所有 deployment
foreach (AIProjectDeployment deployment in projectClient.Deployments.GetDeployments())
{
    Console.WriteLine($"{deployment.Name}: {deployment.ModelName}");
}

// 依發行者過濾
foreach (var deployment in projectClient.Deployments.GetDeployments(modelPublisher: "Microsoft"))
{
    Console.WriteLine(deployment.Name);
}

// 取得指定的 deployment
ModelDeployment details = (ModelDeployment)projectClient.Deployments.GetDeployment("gpt-4o-mini");
```

### 5. Dataset

```csharp
// 上傳單一檔案
FileDataset fileDataset = projectClient.Datasets.UploadFile(
    name: "my-dataset",
    version: "1.0",
    filePath: "data/training.txt",
    connectionName: connectionName);

// 上傳資料夾
FolderDataset folderDataset = projectClient.Datasets.UploadFolder(
    name: "my-dataset",
    version: "2.0",
    folderPath: "data/training",
    connectionName: connectionName,
    filePattern: new Regex(".*\\.txt"));

// 取得 dataset
AIProjectDataset dataset = projectClient.Datasets.GetDataset("my-dataset", "1.0");

// 刪除 dataset
projectClient.Datasets.Delete("my-dataset", "1.0");
```

### 6. Index

```csharp
// 建立 Azure AI Search index
AzureAISearchIndex searchIndex = new(aiSearchConnectionName, aiSearchIndexName)
{
    Description = "Sample Index"
};

searchIndex = (AzureAISearchIndex)projectClient.Indexes.CreateOrUpdate(
    name: "my-index",
    version: "1.0",
    index: searchIndex);

// 列出 index
foreach (AIProjectIndex index in projectClient.Indexes.GetIndexes())
{
    Console.WriteLine(index.Name);
}

// 刪除 index
projectClient.Indexes.Delete(name: "my-index", version: "1.0");
```

### 7. Evaluation

```csharp
// 建立 evaluation 設定
var evaluatorConfig = new EvaluatorConfiguration(id: EvaluatorIDs.Relevance);
evaluatorConfig.InitParams.Add("deployment_name", BinaryData.FromObjectAsJson("gpt-4o"));

// 建立 evaluation
Evaluation evaluation = new Evaluation(
    data: new InputDataset("<dataset_id>"),
    evaluators: new Dictionary<string, EvaluatorConfiguration> 
    { 
        { "relevance", evaluatorConfig } 
    }
)
{
    DisplayName = "Sample Evaluation"
};

// 執行 evaluation
Evaluation result = projectClient.Evaluations.Create(evaluation: evaluation);

// 取得 evaluation
Evaluation getResult = projectClient.Evaluations.Get(result.Name);

// 列出 evaluation
foreach (var eval in projectClient.Evaluations.GetAll())
{
    Console.WriteLine($"{eval.DisplayName}: {eval.Status}");
}
```

### 8. 取得 Azure OpenAI Chat Client

```csharp
using Azure.AI.OpenAI;
using OpenAI.Chat;

ClientConnection connection = projectClient.GetConnection(typeof(AzureOpenAIClient).FullName!);

if (!connection.TryGetLocatorAsUri(out Uri uri) || uri is null)
    throw new InvalidOperationException("Invalid URI.");

uri = new Uri($"https://{uri.Host}");

AzureOpenAIClient azureOpenAIClient = new AzureOpenAIClient(uri, new DefaultAzureCredential());
ChatClient chatClient = azureOpenAIClient.GetChatClient("gpt-4o-mini");

ChatCompletion result = chatClient.CompleteChat("List all rainbow colors");
Console.WriteLine(result.Content[0].Text);
```

## 可用的 Agent 工具

| 工具 | Class | 用途 |
|------|-------|---------|
| Code Interpreter | `CodeInterpreterToolDefinition` | 執行 Python 程式碼 |
| File Search | `FileSearchToolDefinition` | 搜尋上傳的檔案 |
| Function Calling | `FunctionToolDefinition` | 呼叫自訂函式 |
| Bing Grounding | `BingGroundingToolDefinition` | 透過 Bing 搜尋網頁 |
| Azure AI Search | `AzureAISearchToolDefinition` | 搜尋 Azure AI 的 index |
| OpenAPI | `OpenApiToolDefinition` | 呼叫外部 API |
| Azure Functions | `AzureFunctionToolDefinition` | 呼叫 Azure Functions |
| MCP | `MCPToolDefinition` | Model Context Protocol 工具 |

## 主要型別參考

| 型別 | 用途 |
|------|---------|
| `AIProjectClient` | 主要進入點 |
| `PersistentAgentsClient` | 低階 agent 操作 |
| `PromptAgentDefinition` | 版本化 agent 的定義 |
| `AgentVersion` | 版本化 agent 的實例 |
| `AIProjectConnection` | 連到 Azure 資源的 connection |
| `AIProjectDeployment` | 模型 deployment 資訊 |
| `AIProjectDataset` | Dataset 的 metadata |
| `AIProjectIndex` | Search index 的 metadata |
| `Evaluation` | Evaluation 的設定與結果 |

## 最佳實務

1. 正式環境認證**用 `DefaultAzureCredential`**
2. 所有 I/O 操作都**用非同步方法**（`*Async`）
3. 等待 run 時**輪詢要有適當的間隔**（建議 500ms）
4. **清理資源**：用完就刪掉 thread、agent 和檔案
5. 正式環境情境**用版本化 agent**（透過 `Azure.AI.Projects.OpenAI`）
6. 工具設定**存 connection ID**，不要存名稱
7. 只有真的需要憑證時才**用 `includeCredentials: true`**
8. **處理分頁**：列舉操作用 `AsyncPageable<T>`

## 錯誤處理

```csharp
using Azure;

try
{
    var result = await projectClient.Evaluations.CreateAsync(evaluation);
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Error: {ex.Status} - {ex.ErrorCode}: {ex.Message}");
}
```

## 相關 SDK

| SDK | 用途 | 安裝 |
|-----|---------|---------|
| `Azure.AI.Projects` | 高階 project client（本 SDK） | `dotnet add package Azure.AI.Projects` |
| `Azure.AI.Agents.Persistent` | 低階 agent 操作 | `dotnet add package Azure.AI.Agents.Persistent` |
| `Azure.AI.Projects.OpenAI` | 搭配 OpenAI 的版本化 agent | `dotnet add package Azure.AI.Projects.OpenAI` |

## 參考連結

| 資源 | URL |
|----------|-----|
| NuGet 套件 | https://www.nuget.org/packages/Azure.AI.Projects |
| API 參考 | https://learn.microsoft.com/dotnet/api/azure.ai.projects |
| GitHub 原始碼 | https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/ai/Azure.AI.Projects |
| 範例 | https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/ai/Azure.AI.Projects/samples |
