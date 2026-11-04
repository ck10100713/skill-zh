---
name: azure-ai-voicelive-ts
description: |
  Azure AI Voice Live SDK for JavaScript/TypeScript。用雙向 WebSocket 通訊建構即時語音 AI 應用程式。適用於在 Node.js 或瀏覽器環境中開發語音助理、對話式 AI、即時語音對語音，以及支援語音的聊天機器人。Triggers: "voice live", "real-time voice", "VoiceLiveClient", "VoiceLiveSession", "voice assistant TypeScript", "bidirectional audio", "speech-to-speech JavaScript".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: '@azure/ai-voicelive'
---

# @azure/ai-voicelive (JavaScript/TypeScript)

在 Node.js 和瀏覽器環境中，用 Azure AI 建構雙向語音助理的即時語音 AI SDK。

## Installation

```bash
npm install @azure/ai-voicelive @azure/identity
# TypeScript 使用者
npm install @types/node
```

**目前版本**：1.0.0-beta.3

**支援的環境**：
- Node.js LTS 版本（20+）
- 現代瀏覽器（Chrome、Firefox、Safari、Edge）

## Environment Variables

```bash
AZURE_VOICELIVE_ENDPOINT=https://<resource>.cognitiveservices.azure.com
# 選填：不用 Entra ID 時的 API key
AZURE_VOICELIVE_API_KEY=<your-api-key>
# 選填：Logging
AZURE_LOG_LEVEL=info
AZURE_TOKEN_CREDENTIALS=prod # 只有在 production 使用 DefaultAzureCredential 時才需要
```

## Authentication

### Microsoft Entra Token Credential (Recommended)

```typescript
import { DefaultAzureCredential, ManagedIdentityCredential } from "@azure/identity";
import { VoiceLiveClient } from "@azure/ai-voicelive";

// 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
const credential = new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]});
// 或在 production 直接用指定的 credential：
// 參考 https://learn.microsoft.com/javascript/api/overview/azure/identity-readme?view=azure-node-latest#credential-classes
// const credential = new ManagedIdentityCredential();
const endpoint = "https://your-resource.cognitiveservices.azure.com";

const client = new VoiceLiveClient(endpoint, credential);
```

### API Key

```typescript
import { AzureKeyCredential } from "@azure/core-auth";
import { VoiceLiveClient } from "@azure/ai-voicelive";

const endpoint = "https://your-resource.cognitiveservices.azure.com";
const credential = new AzureKeyCredential("your-api-key");

const client = new VoiceLiveClient(endpoint, credential);
```

## Client Hierarchy

```
VoiceLiveClient
└── VoiceLiveSession (WebSocket connection)
    ├── updateSession()      → Configure session options
    ├── subscribe()          → Event handlers (Azure SDK pattern)
    ├── sendAudio()          → Stream audio input
    ├── addConversationItem() → Add messages/function outputs
    └── sendEvent()          → Send raw protocol events
```

## Quick Start

```typescript
import { DefaultAzureCredential } from "@azure/identity";
import { VoiceLiveClient } from "@azure/ai-voicelive";

const credential = new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]});
const endpoint = process.env.AZURE_VOICELIVE_ENDPOINT!;

// 建立 client 並啟動 session
const client = new VoiceLiveClient(endpoint, credential);
const session = await client.startSession("gpt-4o-mini-realtime-preview");

// 設定 session
await session.updateSession({
  modalities: ["text", "audio"],
  instructions: "You are a helpful AI assistant. Respond naturally.",
  voice: {
    type: "azure-standard",
    name: "en-US-AvaNeural",
  },
  turnDetection: {
    type: "server_vad",
    threshold: 0.5,
    prefixPaddingMs: 300,
    silenceDurationMs: 500,
  },
  inputAudioFormat: "pcm16",
  outputAudioFormat: "pcm16",
});

// 訂閱事件
const subscription = session.subscribe({
  onResponseAudioDelta: async (event, context) => {
    // 處理串流的音訊輸出
    const audioData = event.delta;
    playAudioChunk(audioData);
  },
  onResponseTextDelta: async (event, context) => {
    // 處理串流的文字
    process.stdout.write(event.delta);
  },
  onInputAudioTranscriptionCompleted: async (event, context) => {
    console.log("User said:", event.transcript);
  },
});

// 從麥克風送出音訊
function sendAudioChunk(audioBuffer: ArrayBuffer) {
  session.sendAudio(audioBuffer);
}
```

## Session Configuration

```typescript
await session.updateSession({
  // Modalities
  modalities: ["audio", "text"],
  
  // System instructions
  instructions: "You are a customer service representative.",
  
  // 語音選擇
  voice: {
    type: "azure-standard",  // 或 "azure-custom", "openai"
    name: "en-US-AvaNeural",
  },
  
  // Turn detection（VAD）
  turnDetection: {
    type: "server_vad",      // 或 "azure_semantic_vad"
    threshold: 0.5,
    prefixPaddingMs: 300,
    silenceDurationMs: 500,
  },
  
  // 音訊格式
  inputAudioFormat: "pcm16",
  outputAudioFormat: "pcm16",
  
  // Tools（function calling）
  tools: [
    {
      type: "function",
      name: "get_weather",
      description: "Get current weather",
      parameters: {
        type: "object",
        properties: {
          location: { type: "string" }
        },
        required: ["location"]
      }
    }
  ],
  toolChoice: "auto",
});
```

## Event Handling (Azure SDK Pattern)

這個 SDK 用訂閱式的事件處理模式：

```typescript
const subscription = session.subscribe({
  // 連線生命週期
  onConnected: async (args, context) => {
    console.log("Connected:", args.connectionId);
  },
  onDisconnected: async (args, context) => {
    console.log("Disconnected:", args.code, args.reason);
  },
  onError: async (args, context) => {
    console.error("Error:", args.error.message);
  },
  
  // Session 事件
  onSessionCreated: async (event, context) => {
    console.log("Session created:", context.sessionId);
  },
  onSessionUpdated: async (event, context) => {
    console.log("Session updated");
  },
  
  // 音訊輸入事件（VAD）
  onInputAudioBufferSpeechStarted: async (event, context) => {
    console.log("Speech started at:", event.audioStartMs);
  },
  onInputAudioBufferSpeechStopped: async (event, context) => {
    console.log("Speech stopped at:", event.audioEndMs);
  },
  
  // 轉錄事件
  onConversationItemInputAudioTranscriptionCompleted: async (event, context) => {
    console.log("User said:", event.transcript);
  },
  onConversationItemInputAudioTranscriptionDelta: async (event, context) => {
    process.stdout.write(event.delta);
  },
  
  // 回應事件
  onResponseCreated: async (event, context) => {
    console.log("Response started");
  },
  onResponseDone: async (event, context) => {
    console.log("Response complete");
  },
  
  // 串流文字
  onResponseTextDelta: async (event, context) => {
    process.stdout.write(event.delta);
  },
  onResponseTextDone: async (event, context) => {
    console.log("\n--- Text complete ---");
  },
  
  // 串流音訊
  onResponseAudioDelta: async (event, context) => {
    const audioData = event.delta;
    playAudioChunk(audioData);
  },
  onResponseAudioDone: async (event, context) => {
    console.log("Audio complete");
  },
  
  // 音訊逐字稿（助理說的內容）
  onResponseAudioTranscriptDelta: async (event, context) => {
    process.stdout.write(event.delta);
  },
  
  // Function calling
  onResponseFunctionCallArgumentsDone: async (event, context) => {
    if (event.name === "get_weather") {
      const args = JSON.parse(event.arguments);
      const result = await getWeather(args.location);
      
      await session.addConversationItem({
        type: "function_call_output",
        callId: event.callId,
        output: JSON.stringify(result),
      });
      
      await session.sendEvent({ type: "response.create" });
    }
  },
  
  // 除錯用的全部攔截
  onServerEvent: async (event, context) => {
    console.log("Event:", event.type);
  },
});

// 用完要清理
await subscription.close();
```

## Function Calling

```typescript
// 在 session 設定裡定義 tools
await session.updateSession({
  modalities: ["audio", "text"],
  instructions: "Help users with weather information.",
  tools: [
    {
      type: "function",
      name: "get_weather",
      description: "Get current weather for a location",
      parameters: {
        type: "object",
        properties: {
          location: {
            type: "string",
            description: "City and state or country",
          },
        },
        required: ["location"],
      },
    },
  ],
  toolChoice: "auto",
});

// 處理 function call
const subscription = session.subscribe({
  onResponseFunctionCallArgumentsDone: async (event, context) => {
    if (event.name === "get_weather") {
      const args = JSON.parse(event.arguments);
      const weatherData = await fetchWeather(args.location);
      
      // 送出 function 的結果
      await session.addConversationItem({
        type: "function_call_output",
        callId: event.callId,
        output: JSON.stringify(weatherData),
      });
      
      // 觸發產生回應
      await session.sendEvent({ type: "response.create" });
    }
  },
});
```

## Voice Options

| Voice Type | Config | Example |
|------------|--------|---------|
| Azure Standard | `{ type: "azure-standard", name: "..." }` | `"en-US-AvaNeural"` |
| Azure Custom | `{ type: "azure-custom", name: "...", endpointId: "..." }` | 自訂語音 endpoint |
| Azure Personal | `{ type: "azure-personal", speakerProfileId: "..." }` | 個人語音複製 |
| OpenAI | `{ type: "openai", name: "..." }` | `"alloy"`, `"echo"`, `"shimmer"` |

## Supported Models

| Model | Description | Use Case |
|-------|-------------|----------|
| `gpt-4o-realtime-preview` | 支援即時音訊的 GPT-4o | 高品質對話式 AI |
| `gpt-4o-mini-realtime-preview` | 輕量版 GPT-4o | 快速、有效率的互動 |
| `phi4-mm-realtime` | Phi 多模態 | 高性價比的應用 |

## Turn Detection Options

```typescript
// Server VAD（預設）
turnDetection: {
  type: "server_vad",
  threshold: 0.5,
  prefixPaddingMs: 300,
  silenceDurationMs: 500,
}

// Azure Semantic VAD（更聰明的偵測）
turnDetection: {
  type: "azure_semantic_vad",
}

// Azure Semantic VAD（針對英文優化）
turnDetection: {
  type: "azure_semantic_vad_en",
}

// Azure Semantic VAD（多語言）
turnDetection: {
  type: "azure_semantic_vad_multilingual",
}
```

## Audio Formats

| Format | Sample Rate | Use Case |
|--------|-------------|----------|
| `pcm16` | 24kHz | 預設，高品質 |
| `pcm16-8000hz` | 8kHz | 電話 |
| `pcm16-16000hz` | 16kHz | 語音助理 |
| `g711_ulaw` | 8kHz | 電話（美國） |
| `g711_alaw` | 8kHz | 電話（歐洲） |

## Key Types Reference

| Type | Purpose |
|------|---------|
| `VoiceLiveClient` | 建立 session 的主要 client |
| `VoiceLiveSession` | 使用中的 WebSocket session |
| `VoiceLiveSessionHandlers` | 事件處理器介面 |
| `VoiceLiveSubscription` | 使用中的事件訂閱 |
| `ConnectionContext` | 連線事件的 context |
| `SessionContext` | Session 事件的 context |
| `ServerEventUnion` | 所有 server 事件的 union |

## Error Handling

```typescript
import {
  VoiceLiveError,
  VoiceLiveConnectionError,
  VoiceLiveAuthenticationError,
  VoiceLiveProtocolError,
} from "@azure/ai-voicelive";

const subscription = session.subscribe({
  onError: async (args, context) => {
    const { error } = args;
    
    if (error instanceof VoiceLiveConnectionError) {
      console.error("Connection error:", error.message);
    } else if (error instanceof VoiceLiveAuthenticationError) {
      console.error("Auth error:", error.message);
    } else if (error instanceof VoiceLiveProtocolError) {
      console.error("Protocol error:", error.message);
    }
  },
  
  onServerError: async (event, context) => {
    console.error("Server error:", event.error?.message);
  },
});
```

## Logging

```typescript
import { setLogLevel } from "@azure/logger";

// 開啟詳細 log
setLogLevel("info");

// 或用環境變數
// AZURE_LOG_LEVEL=info
```

## Browser Usage

```typescript
// 瀏覽器需要 bundler（Vite、webpack 等）
import { VoiceLiveClient } from "@azure/ai-voicelive";
import { InteractiveBrowserCredential } from "@azure/identity";

// 使用瀏覽器相容的 credential
const credential = new InteractiveBrowserCredential({
  clientId: "your-client-id",
  tenantId: "your-tenant-id",
});

const client = new VoiceLiveClient(endpoint, credential);

// 請求麥克風權限
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
const audioContext = new AudioContext({ sampleRate: 24000 });

// 處理音訊並送到 session
// ...（完整實作見 samples）
```

## Best Practices

1. **本機開發用 `DefaultAzureCredential`，production 用 `ManagedIdentityCredential` 或 `WorkloadIdentityCredential`**：絕對不要把 API key 寫死在程式碼裡
2. **兩種 modality 都要設**：語音助理要包含 `["text", "audio"]`
3. **用 Azure Semantic VAD**：turn detection 比基本的 server VAD 更好
4. **處理所有錯誤類型**：連線、驗證和協定錯誤
5. **清理訂閱**：用完要呼叫 `subscription.close()`
6. **用合適的音訊格式**：24kHz 的 PCM16 品質最好

## Reference Links

| Resource | URL |
|----------|-----|
| npm Package | https://www.npmjs.com/package/@azure/ai-voicelive |
| GitHub Source | https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/ai/ai-voicelive |
| Samples | https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/ai/ai-voicelive/samples |
| API Reference | https://learn.microsoft.com/javascript/api/@azure/ai-voicelive |
