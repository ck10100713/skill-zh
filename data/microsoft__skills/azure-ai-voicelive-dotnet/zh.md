---
name: azure-ai-voicelive-dotnet
description: |
  Azure AI Voice Live SDK for .NET。用雙向 WebSocket 通訊建構即時語音 AI 應用程式。適用於語音助理、對話式 AI、即時語音對語音，以及支援語音的聊天機器人。Triggers: "voice live", "real-time voice", "VoiceLiveClient", "VoiceLiveSession", "voice assistant .NET", "bidirectional audio", "speech-to-speech".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.AI.VoiceLive
---

# Azure.AI.VoiceLive (.NET)

用 Azure AI 建構雙向語音助理的即時語音 AI SDK。

## Installation

```bash
dotnet add package Azure.AI.VoiceLive
dotnet add package Azure.Identity
dotnet add package NAudio                    # 用於音訊擷取/播放
```

**目前版本**：穩定版 v1.0.0，預覽版 v1.1.0-beta.1

## Environment Variables

```bash
AZURE_VOICELIVE_ENDPOINT=https://<resource>.services.ai.azure.com/  # 必填：Voice Live endpoint
AZURE_VOICELIVE_MODEL=gpt-4o-realtime-preview  # 必填：model deployment 名稱
AZURE_VOICELIVE_VOICE=en-US-AvaNeural  # 選填：Voice Live 的語音名稱
AZURE_VOICELIVE_API_KEY=<your-api-key>  # 只有 AzureKeyCredential 驗證才需要
AZURE_TOKEN_CREDENTIALS=prod  # 只有在 production 使用 DefaultAzureCredential 時才需要
```

## Authentication

### Microsoft Entra Token Credential

```csharp
using Azure.Identity;
using Azure.AI.VoiceLive;

Uri endpoint = new Uri("https://your-resource.cognitiveservices.azure.com");
// 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
var credential = new DefaultAzureCredential(
    DefaultAzureCredential.DefaultEnvironmentVariableName
);
// 或在 production 直接用指定的 credential：
// 參考 https://learn.microsoft.com/dotnet/api/overview/azure/identity-readme?view=azure-dotnet#credential-classes
// var credential = new ManagedIdentityCredential();
VoiceLiveClient client = new VoiceLiveClient(endpoint, credential);
```

**需要的角色**：`Cognitive Services User`（在 Azure Portal 的 Access control 指派）

### API Key

```csharp
Uri endpoint = new Uri("https://your-resource.cognitiveservices.azure.com");
AzureKeyCredential credential = new AzureKeyCredential("your-api-key");
VoiceLiveClient client = new VoiceLiveClient(endpoint, credential);
```

## Client Hierarchy

```
VoiceLiveClient
└── VoiceLiveSession (WebSocket connection)
    ├── ConfigureSessionAsync()
    ├── GetUpdatesAsync() → SessionUpdate events
    ├── AddItemAsync() → UserMessageItem, FunctionCallOutputItem
    ├── SendAudioAsync()
    └── StartResponseAsync()
```

## Core Workflow

### 1. Start Session and Configure

```csharp
using Azure.Identity;
using Azure.AI.VoiceLive;

var endpoint = new Uri(Environment.GetEnvironmentVariable("AZURE_VOICELIVE_ENDPOINT"));
var client = new VoiceLiveClient(endpoint, new DefaultAzureCredential());

var model = "gpt-4o-mini-realtime-preview";

// 啟動 session
using VoiceLiveSession session = await client.StartSessionAsync(model);

// 設定 session
VoiceLiveSessionOptions sessionOptions = new()
{
    Model = model,
    Instructions = "You are a helpful AI assistant. Respond naturally.",
    Voice = new AzureStandardVoice("en-US-AvaNeural"),
    TurnDetection = new AzureSemanticVadTurnDetection()
    {
        Threshold = 0.5f,
        PrefixPadding = TimeSpan.FromMilliseconds(300),
        SilenceDuration = TimeSpan.FromMilliseconds(500)
    },
    InputAudioFormat = InputAudioFormat.Pcm16,
    OutputAudioFormat = OutputAudioFormat.Pcm16
};

// 設定 modality（語音助理要同時有文字和音訊）
sessionOptions.Modalities.Clear();
sessionOptions.Modalities.Add(InteractionModality.Text);
sessionOptions.Modalities.Add(InteractionModality.Audio);

await session.ConfigureSessionAsync(sessionOptions);
```

### 2. Process Events

```csharp
await foreach (SessionUpdate serverEvent in session.GetUpdatesAsync())
{
    switch (serverEvent)
    {
        case SessionUpdateResponseAudioDelta audioDelta:
            byte[] audioData = audioDelta.Delta.ToArray();
            // 用 NAudio 或其他音訊函式庫播放音訊
            break;
            
        case SessionUpdateResponseTextDelta textDelta:
            Console.Write(textDelta.Delta);
            break;
            
        case SessionUpdateResponseFunctionCallArgumentsDone functionCall:
            // 處理 function call（見 Function Calling 一節）
            break;
            
        case SessionUpdateError error:
            Console.WriteLine($"Error: {error.Error.Message}");
            break;
            
        case SessionUpdateResponseDone:
            Console.WriteLine("\n--- Response complete ---");
            break;
    }
}
```

### 3. Send User Message

```csharp
await session.AddItemAsync(new UserMessageItem("Hello, can you help me?"));
await session.StartResponseAsync();
```

### 4. Function Calling

```csharp
// 定義 function
var weatherFunction = new VoiceLiveFunctionDefinition("get_current_weather")
{
    Description = "Get the current weather for a given location",
    Parameters = BinaryData.FromString("""
        {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state or country"
                }
            },
            "required": ["location"]
        }
        """)
};

// 加進 session options
sessionOptions.Tools.Add(weatherFunction);

// 在事件迴圈裡處理 function call
if (serverEvent is SessionUpdateResponseFunctionCallArgumentsDone functionCall)
{
    if (functionCall.Name == "get_current_weather")
    {
        var parameters = JsonSerializer.Deserialize<Dictionary<string, string>>(functionCall.Arguments);
        string location = parameters?["location"] ?? "";
        
        // 呼叫外部服務
        string weatherInfo = $"The weather in {location} is sunny, 75°F.";
        
        // 送出回應
        await session.AddItemAsync(new FunctionCallOutputItem(functionCall.CallId, weatherInfo));
        await session.StartResponseAsync();
    }
}
```

## Voice Options

| Voice Type | Class | Example |
|------------|-------|---------|
| Azure Standard | `AzureStandardVoice` | `"en-US-AvaNeural"` |
| Azure HD | `AzureStandardVoice` | `"en-US-Ava:DragonHDLatestNeural"` |
| Azure Custom | `AzureCustomVoice` | 搭配 endpoint ID 的自訂語音 |

## Supported Models

| Model | Description |
|-------|-------------|
| `gpt-4o-realtime-preview` | 支援即時音訊的 GPT-4o |
| `gpt-4o-mini-realtime-preview` | 輕量、互動快速 |
| `phi4-mm-realtime` | 高性價比的多模態模型 |

## Key Types Reference

| Type | Purpose |
|------|---------|
| `VoiceLiveClient` | 建立 session 的主要 client |
| `VoiceLiveSession` | 使用中的 WebSocket session |
| `VoiceLiveSessionOptions` | Session 設定 |
| `AzureStandardVoice` | 標準 Azure 語音提供者 |
| `AzureSemanticVadTurnDetection` | 語音活動偵測 |
| `VoiceLiveFunctionDefinition` | Function tool 定義 |
| `UserMessageItem` | 使用者文字訊息 |
| `FunctionCallOutputItem` | Function call 回應 |
| `SessionUpdateResponseAudioDelta` | 音訊片段事件 |
| `SessionUpdateResponseTextDelta` | 文字片段事件 |

## Best Practices

1. **兩種 modality 一定要都設**：語音助理要同時包含 `Text` 和 `Audio`
2. **用 `AzureSemanticVadTurnDetection`**：對話流程比較自然
3. **設定適當的靜音時長**：一般用 500ms，避免太早被截斷
4. **用 `using` 陳述式**：確保 session 正確釋放
5. **處理所有事件類型**：要檢查錯誤、音訊、文字和 function call
6. **用 DefaultAzureCredential**：絕對不要把 API key 寫死在程式碼裡

## Error Handling

```csharp
if (serverEvent is SessionUpdateError error)
{
    if (error.Error.Message.Contains("Cancellation failed: no active response"))
    {
        // 無害的錯誤，可以忽略
    }
    else
    {
        Console.WriteLine($"Error: {error.Error.Message}");
    }
}
```

## Audio Configuration

- **輸入格式**：`InputAudioFormat.Pcm16`（16-bit PCM）
- **輸出格式**：`OutputAudioFormat.Pcm16`
- **取樣率**：建議 24kHz
- **聲道**：單聲道

## Related SDKs

| SDK | Purpose | Install |
|-----|---------|---------|
| `Azure.AI.VoiceLive` | 即時語音（本 SDK） | `dotnet add package Azure.AI.VoiceLive` |
| `Microsoft.CognitiveServices.Speech` | 語音轉文字、文字轉語音 | `dotnet add package Microsoft.CognitiveServices.Speech` |
| `NAudio` | 音訊擷取/播放 | `dotnet add package NAudio` |

## Reference Links

| Resource | URL |
|----------|-----|
| NuGet Package | https://www.nuget.org/packages/Azure.AI.VoiceLive |
| API Reference | https://learn.microsoft.com/dotnet/api/azure.ai.voicelive |
| GitHub Source | https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/ai/Azure.AI.VoiceLive |
| Quickstart | https://learn.microsoft.com/azure/ai-services/speech-service/voice-live-quickstart |
