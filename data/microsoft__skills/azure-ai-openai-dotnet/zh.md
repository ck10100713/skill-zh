---
name: azure-ai-openai-dotnet
description: |
  Azure OpenAI SDK（.NET 版）。Azure OpenAI 和 OpenAI 服務的 client 函式庫。用於 chat completion、embedding、圖片生成、音訊轉錄和 assistant。Triggers: "Azure OpenAI", "AzureOpenAIClient", "ChatClient", "chat completions .NET", "GPT-4", "embeddings", "DALL-E", "Whisper", "OpenAI .NET"。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.AI.OpenAI
---

# Azure.AI.OpenAI（.NET）

Azure OpenAI Service 的 client 函式庫，可存取 OpenAI 模型，包括 GPT-4、GPT-4o、embedding、DALL-E 和 Whisper。

## 安裝

```bash
dotnet add package Azure.AI.OpenAI

# 為了相容 OpenAI（非 Azure）
dotnet add package OpenAI
```

**目前版本**：2.1.0（穩定版）

## 環境變數

```bash
AZURE_OPENAI_ENDPOINT=https://<resource-name>.openai.azure.com  # 必填：Azure OpenAI endpoint
AZURE_OPENAI_API_KEY=<api-key>  # 只有用 AzureKeyCredential 認證時才需要
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini  # 必填：model deployment 名稱
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境用 DefaultAzureCredential 時才需要
```

## Client 階層

```
AzureOpenAIClient（最上層）
├── GetChatClient(deploymentName)      → ChatClient
├── GetEmbeddingClient(deploymentName) → EmbeddingClient
├── GetImageClient(deploymentName)     → ImageClient
├── GetAudioClient(deploymentName)     → AudioClient
└── GetAssistantClient()               → AssistantClient
```

## 認證

### API Key 認證

```csharp
using Azure;
using Azure.AI.OpenAI;

AzureOpenAIClient client = new(
    new Uri(Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")!),
    new AzureKeyCredential(Environment.GetEnvironmentVariable("AZURE_OPENAI_API_KEY")!));
```

### Microsoft Entra Token Credential

```csharp
using Azure.Identity;
using Azure.AI.OpenAI;

// 本機開發：用 DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
var credential = new DefaultAzureCredential(
    DefaultAzureCredential.DefaultEnvironmentVariableName
);
// 或在正式環境直接使用指定的 credential：
// See https://learn.microsoft.com/dotnet/api/overview/azure/identity-readme?view=azure-dotnet#credential-classes
// var credential = new ManagedIdentityCredential();
AzureOpenAIClient client = new(
    new Uri(Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")!),
    credential);
```

### 直接用 OpenAI SDK 連 Azure

```csharp
using Azure.Identity;
using OpenAI;
using OpenAI.Chat;
using System.ClientModel.Primitives;

#pragma warning disable OPENAI001

BearerTokenPolicy tokenPolicy = new(
    new DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default");

ChatClient client = new(
    model: "gpt-4o-mini",
    authenticationPolicy: tokenPolicy,
    options: new OpenAIClientOptions()
    {
        Endpoint = new Uri("https://YOUR-RESOURCE.openai.azure.com/openai/v1")
    });
```

## Chat Completion

### 基本 Chat

```csharp
using Azure.AI.OpenAI;
using OpenAI.Chat;

AzureOpenAIClient azureClient = new(
    new Uri(endpoint),
    new DefaultAzureCredential());

ChatClient chatClient = azureClient.GetChatClient("gpt-4o-mini");

ChatCompletion completion = chatClient.CompleteChat(
[
    new SystemChatMessage("You are a helpful assistant."),
    new UserChatMessage("What is Azure OpenAI?")
]);

Console.WriteLine(completion.Content[0].Text);
```

### 非同步 Chat

```csharp
ChatCompletion completion = await chatClient.CompleteChatAsync(
[
    new SystemChatMessage("You are a helpful assistant."),
    new UserChatMessage("Explain cloud computing in simple terms.")
]);

Console.WriteLine($"Response: {completion.Content[0].Text}");
Console.WriteLine($"Tokens used: {completion.Usage.TotalTokenCount}");
```

### 串流 Chat

```csharp
await foreach (StreamingChatCompletionUpdate update 
    in chatClient.CompleteChatStreamingAsync(messages))
{
    if (update.ContentUpdate.Count > 0)
    {
        Console.Write(update.ContentUpdate[0].Text);
    }
}
```

### 帶選項的 Chat

```csharp
ChatCompletionOptions options = new()
{
    MaxOutputTokenCount = 1000,
    Temperature = 0.7f,
    TopP = 0.95f,
    FrequencyPenalty = 0,
    PresencePenalty = 0
};

ChatCompletion completion = await chatClient.CompleteChatAsync(messages, options);
```

### 多輪對話

```csharp
List<ChatMessage> messages = new()
{
    new SystemChatMessage("You are a helpful assistant."),
    new UserChatMessage("Hi, can you help me?"),
    new AssistantChatMessage("Of course! What do you need help with?"),
    new UserChatMessage("What's the capital of France?")
};

ChatCompletion completion = await chatClient.CompleteChatAsync(messages);
messages.Add(new AssistantChatMessage(completion.Content[0].Text));
```

## 結構化輸出（JSON Schema）

```csharp
using System.Text.Json;

ChatCompletionOptions options = new()
{
    ResponseFormat = ChatResponseFormat.CreateJsonSchemaFormat(
        jsonSchemaFormatName: "math_reasoning",
        jsonSchema: BinaryData.FromBytes("""
            {
                "type": "object",
                "properties": {
                    "steps": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "explanation": { "type": "string" },
                                "output": { "type": "string" }
                            },
                            "required": ["explanation", "output"],
                            "additionalProperties": false
                        }
                    },
                    "final_answer": { "type": "string" }
                },
                "required": ["steps", "final_answer"],
                "additionalProperties": false
            }
            """u8.ToArray()),
        jsonSchemaIsStrict: true)
};

ChatCompletion completion = await chatClient.CompleteChatAsync(
    [new UserChatMessage("How can I solve 8x + 7 = -23?")],
    options);

using JsonDocument json = JsonDocument.Parse(completion.Content[0].Text);
Console.WriteLine($"Answer: {json.RootElement.GetProperty("final_answer")}");
```

## 推理模型（o1、o4-mini）

```csharp
ChatCompletionOptions options = new()
{
    ReasoningEffortLevel = ChatReasoningEffortLevel.Low,
    MaxOutputTokenCount = 100000
};

ChatCompletion completion = await chatClient.CompleteChatAsync(
[
    new DeveloperChatMessage("You are a helpful assistant"),
    new UserChatMessage("Explain the theory of relativity")
], options);
```

## Azure AI Search 整合（RAG）

```csharp
using Azure.AI.OpenAI.Chat;

#pragma warning disable AOAI001

ChatCompletionOptions options = new();
options.AddDataSource(new AzureSearchChatDataSource()
{
    Endpoint = new Uri(searchEndpoint),
    IndexName = searchIndex,
    Authentication = DataSourceAuthentication.FromApiKey(searchKey)
});

ChatCompletion completion = await chatClient.CompleteChatAsync(
    [new UserChatMessage("What health plans are available?")],
    options);

ChatMessageContext context = completion.GetMessageContext();
if (context?.Intent is not null)
{
    Console.WriteLine($"Intent: {context.Intent}");
}
foreach (ChatCitation citation in context?.Citations ?? [])
{
    Console.WriteLine($"Citation: {citation.Content}");
}
```

## Embedding

```csharp
using OpenAI.Embeddings;

EmbeddingClient embeddingClient = azureClient.GetEmbeddingClient("text-embedding-ada-002");

OpenAIEmbedding embedding = await embeddingClient.GenerateEmbeddingAsync("Hello, world!");
ReadOnlyMemory<float> vector = embedding.ToFloats();

Console.WriteLine($"Embedding dimensions: {vector.Length}");
```

### 批次 Embedding

```csharp
List<string> inputs = new()
{
    "First document text",
    "Second document text",
    "Third document text"
};

OpenAIEmbeddingCollection embeddings = await embeddingClient.GenerateEmbeddingsAsync(inputs);

foreach (OpenAIEmbedding emb in embeddings)
{
    Console.WriteLine($"Index {emb.Index}: {emb.ToFloats().Length} dimensions");
}
```

## 圖片生成（DALL-E）

```csharp
using OpenAI.Images;

ImageClient imageClient = azureClient.GetImageClient("dall-e-3");

GeneratedImage image = await imageClient.GenerateImageAsync(
    "A futuristic city skyline at sunset",
    new ImageGenerationOptions
    {
        Size = GeneratedImageSize.W1024xH1024,
        Quality = GeneratedImageQuality.High,
        Style = GeneratedImageStyle.Vivid
    });

Console.WriteLine($"Image URL: {image.ImageUri}");
```

## 音訊（Whisper）

### 轉錄

```csharp
using OpenAI.Audio;

AudioClient audioClient = azureClient.GetAudioClient("whisper");

AudioTranscription transcription = await audioClient.TranscribeAudioAsync(
    "audio.mp3",
    new AudioTranscriptionOptions
    {
        ResponseFormat = AudioTranscriptionFormat.Verbose,
        Language = "en"
    });

Console.WriteLine(transcription.Text);
```

### 文字轉語音

```csharp
BinaryData speech = await audioClient.GenerateSpeechAsync(
    "Hello, welcome to Azure OpenAI!",
    GeneratedSpeechVoice.Alloy,
    new SpeechGenerationOptions
    {
        SpeedRatio = 1.0f,
        ResponseFormat = GeneratedSpeechFormat.Mp3
    });

await File.WriteAllBytesAsync("output.mp3", speech.ToArray());
```

## Function Calling（工具）

```csharp
ChatTool getCurrentWeatherTool = ChatTool.CreateFunctionTool(
    functionName: "get_current_weather",
    functionDescription: "Get the current weather in a given location",
    functionParameters: BinaryData.FromString("""
        {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"]
                }
            },
            "required": ["location"]
        }
        """));

ChatCompletionOptions options = new()
{
    Tools = { getCurrentWeatherTool }
};

ChatCompletion completion = await chatClient.CompleteChatAsync(
    [new UserChatMessage("What's the weather in Seattle?")],
    options);

if (completion.FinishReason == ChatFinishReason.ToolCalls)
{
    foreach (ChatToolCall toolCall in completion.ToolCalls)
    {
        Console.WriteLine($"Function: {toolCall.FunctionName}");
        Console.WriteLine($"Arguments: {toolCall.FunctionArguments}");
    }
}
```

## 主要型別參考

| 型別 | 用途 |
|------|---------|
| `AzureOpenAIClient` | Azure OpenAI 的最上層 client |
| `ChatClient` | Chat completion |
| `EmbeddingClient` | 文字 embedding |
| `ImageClient` | 圖片生成（DALL-E） |
| `AudioClient` | 音訊轉錄／TTS |
| `ChatCompletion` | Chat 回應 |
| `ChatCompletionOptions` | 請求設定 |
| `StreamingChatCompletionUpdate` | 串流回應片段 |
| `ChatMessage` | 訊息的基底型別 |
| `SystemChatMessage` | System prompt |
| `UserChatMessage` | 使用者輸入 |
| `AssistantChatMessage` | Assistant 回應 |
| `DeveloperChatMessage` | Developer 訊息（推理模型用） |
| `ChatTool` | Function／工具定義 |
| `ChatToolCall` | 工具呼叫請求 |

## 最佳實務

1. **正式環境用 Entra ID**：避免用 API key，改用 `DefaultAzureCredential`
2. **重複使用 client 實例**：建立一次，在各個請求間共用
3. **處理速率限制**：遇到 429 錯誤要實作 exponential backoff
4. **長回應用串流**：用 `CompleteChatStreamingAsync` 體驗比較好
5. **設定適當的 timeout**：長的 completion 可能需要更長的 timeout
6. **使用結構化輸出**：JSON schema 能確保回應格式一致
7. **監控 token 用量**：追蹤 `completion.Usage` 來管理成本
8. **驗證 tool call**：執行前一定要驗證函式的參數

## 錯誤處理

```csharp
using Azure;

try
{
    ChatCompletion completion = await chatClient.CompleteChatAsync(messages);
}
catch (RequestFailedException ex) when (ex.Status == 429)
{
    Console.WriteLine("Rate limited. Retry after delay.");
    await Task.Delay(TimeSpan.FromSeconds(10));
}
catch (RequestFailedException ex) when (ex.Status == 400)
{
    Console.WriteLine($"Bad request: {ex.Message}");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Azure OpenAI error: {ex.Status} - {ex.Message}");
}
```

## 相關 SDK

| SDK | 用途 | 安裝 |
|-----|---------|---------|
| `Azure.AI.OpenAI` | Azure OpenAI client（本 SDK） | `dotnet add package Azure.AI.OpenAI` |
| `OpenAI` | OpenAI 相容 | `dotnet add package OpenAI` |
| `Azure.Identity` | 認證 | `dotnet add package Azure.Identity` |
| `Azure.Search.Documents` | 給 RAG 用的 AI Search | `dotnet add package Azure.Search.Documents` |

## 參考連結

| 資源 | URL |
|----------|-----|
| NuGet 套件 | https://www.nuget.org/packages/Azure.AI.OpenAI |
| API 參考 | https://learn.microsoft.com/dotnet/api/azure.ai.openai |
| 遷移指南（1.0→2.0） | https://learn.microsoft.com/azure/ai-services/openai/how-to/dotnet-migration |
| 快速開始 | https://learn.microsoft.com/azure/ai-services/openai/quickstart |
| GitHub 原始碼 | https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/openai/Azure.AI.OpenAI |
