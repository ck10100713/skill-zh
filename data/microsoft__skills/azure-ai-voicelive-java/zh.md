---
name: azure-ai-voicelive-java
description: |
  Azure AI VoiceLive SDK for Java。用 WebSocket 和 AI 助理進行即時雙向語音對話。
  Triggers: "VoiceLiveClient java", "voice assistant java", "real-time voice java", "audio streaming java", "voice activity detection java".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: com.azure:azure-ai-voicelive
---

# Azure AI VoiceLive SDK for Java

用 WebSocket 技術和 AI 助理進行即時、雙向的語音對話。

## Installation

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-ai-voicelive</artifactId>
    <version>1.0.0-beta.2</version>
</dependency>
```

## Environment Variables

```bash
AZURE_VOICELIVE_ENDPOINT=https://<resource>.openai.azure.com/ # 所有驗證方式都需要
AZURE_VOICELIVE_API_KEY=<your-api-key> # 只有 AzureKeyCredential 驗證才需要
AZURE_TOKEN_CREDENTIALS=prod  # 只有在 production 使用 DefaultAzureCredential 時才需要
```

## Authentication

### API Key

```java
import com.azure.ai.voicelive.VoiceLiveAsyncClient;
import com.azure.ai.voicelive.VoiceLiveClientBuilder;
import com.azure.core.credential.AzureKeyCredential;

VoiceLiveAsyncClient client = new VoiceLiveClientBuilder()
    .endpoint(System.getenv("AZURE_VOICELIVE_ENDPOINT"))
    .credential(new AzureKeyCredential(System.getenv("AZURE_VOICELIVE_API_KEY")))
    .buildAsyncClient();
```

### DefaultAzureCredential (Recommended)

```java
import com.azure.core.credential.TokenCredential;
import com.azure.identity.AzureIdentityEnvVars;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.identity.ManagedIdentityCredentialBuilder;

TokenCredential credential = new DefaultAzureCredentialBuilder()
    .requireEnvVars(AzureIdentityEnvVars.AZURE_TOKEN_CREDENTIALS)
    .build();
// 或在 production 直接用指定的 credential：
// 參考 https://learn.microsoft.com/java/api/overview/azure/identity-readme?view=azure-java-stable#credential-classes
// TokenCredential credential = new ManagedIdentityCredentialBuilder().build();

VoiceLiveAsyncClient client = new VoiceLiveClientBuilder()
    .endpoint(System.getenv("AZURE_VOICELIVE_ENDPOINT"))
    .credential(credential)
    .buildAsyncClient();
```

## Key Concepts

| Concept | Description |
|---------|-------------|
| `VoiceLiveAsyncClient` | 語音 session 的主要入口 |
| `VoiceLiveSessionAsyncClient` | 用於串流的使用中 WebSocket 連線 |
| `VoiceLiveSessionOptions` | Session 行為的設定 |

### Audio Requirements

- **取樣率**：24kHz（24000 Hz）
- **位元深度**：16-bit PCM
- **聲道**：單聲道（1 個聲道）
- **格式**：Signed PCM，little-endian

## Core Workflow

### 1. Start Session

```java
import reactor.core.publisher.Mono;

client.startSession("gpt-4o-realtime-preview")
    .flatMap(session -> {
        System.out.println("Session started");
        
        // 訂閱事件
        session.receiveEvents()
            .subscribe(
                event -> System.out.println("Event: " + event.getType()),
                error -> System.err.println("Error: " + error.getMessage())
            );
        
        return Mono.just(session);
    })
    .block();
```

### 2. Configure Session Options

```java
import com.azure.ai.voicelive.models.*;
import java.util.Arrays;

ServerVadTurnDetection turnDetection = new ServerVadTurnDetection()
    .setThreshold(0.5)                    // 靈敏度（0.0-1.0）
    .setPrefixPaddingMs(300)              // 開口前保留的音訊
    .setSilenceDurationMs(500)            // 靜音多久就結束這一輪
    .setInterruptResponse(true)           // 允許打斷
    .setAutoTruncate(true)
    .setCreateResponse(true);

AudioInputTranscriptionOptions transcription = new AudioInputTranscriptionOptions(
    AudioInputTranscriptionOptionsModel.WHISPER_1);

VoiceLiveSessionOptions options = new VoiceLiveSessionOptions()
    .setInstructions("You are a helpful AI voice assistant.")
    .setVoice(BinaryData.fromObject(new OpenAIVoice(OpenAIVoiceName.ALLOY)))
    .setModalities(Arrays.asList(InteractionModality.TEXT, InteractionModality.AUDIO))
    .setInputAudioFormat(InputAudioFormat.PCM16)
    .setOutputAudioFormat(OutputAudioFormat.PCM16)
    .setInputAudioSamplingRate(24000)
    .setInputAudioNoiseReduction(new AudioNoiseReduction(AudioNoiseReductionType.NEAR_FIELD))
    .setInputAudioEchoCancellation(new AudioEchoCancellation())
    .setInputAudioTranscription(transcription)
    .setTurnDetection(turnDetection);

// 送出設定
ClientEventSessionUpdate updateEvent = new ClientEventSessionUpdate(options);
session.sendEvent(updateEvent).subscribe();
```

### 3. Send Audio Input

```java
byte[] audioData = readAudioChunk(); // 你的 PCM16 音訊資料
session.sendInputAudio(BinaryData.fromBytes(audioData)).subscribe();
```

### 4. Handle Events

```java
session.receiveEvents().subscribe(event -> {
    ServerEventType eventType = event.getType();
    
    if (ServerEventType.SESSION_CREATED.equals(eventType)) {
        System.out.println("Session created");
    } else if (ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED.equals(eventType)) {
        System.out.println("User started speaking");
    } else if (ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED.equals(eventType)) {
        System.out.println("User stopped speaking");
    } else if (ServerEventType.RESPONSE_AUDIO_DELTA.equals(eventType)) {
        if (event instanceof SessionUpdateResponseAudioDelta) {
            SessionUpdateResponseAudioDelta audioEvent = (SessionUpdateResponseAudioDelta) event;
            playAudioChunk(audioEvent.getDelta());
        }
    } else if (ServerEventType.RESPONSE_DONE.equals(eventType)) {
        System.out.println("Response complete");
    } else if (ServerEventType.ERROR.equals(eventType)) {
        if (event instanceof SessionUpdateError) {
            SessionUpdateError errorEvent = (SessionUpdateError) event;
            System.err.println("Error: " + errorEvent.getError().getMessage());
        }
    }
});
```

## Voice Configuration

### OpenAI Voices

```java
// 可用：ALLOY, ASH, BALLAD, CORAL, ECHO, SAGE, SHIMMER, VERSE
VoiceLiveSessionOptions options = new VoiceLiveSessionOptions()
    .setVoice(BinaryData.fromObject(new OpenAIVoice(OpenAIVoiceName.ALLOY)));
```

### Azure Voices

```java
// Azure Standard Voice
options.setVoice(BinaryData.fromObject(new AzureStandardVoice("en-US-JennyNeural")));

// Azure Custom Voice
options.setVoice(BinaryData.fromObject(new AzureCustomVoice("myVoice", "endpointId")));

// Azure Personal Voice
options.setVoice(BinaryData.fromObject(
    new AzurePersonalVoice("speakerProfileId", PersonalVoiceModels.PHOENIX_LATEST_NEURAL)));
```

## Function Calling

```java
VoiceLiveFunctionDefinition weatherFunction = new VoiceLiveFunctionDefinition("get_weather")
    .setDescription("Get current weather for a location")
    .setParameters(BinaryData.fromObject(parametersSchema));

VoiceLiveSessionOptions options = new VoiceLiveSessionOptions()
    .setTools(Arrays.asList(weatherFunction))
    .setInstructions("You have access to weather information.");
```

## Best Practices

1. **用非同步 client**：VoiceLive 需要 reactive 模式
2. **設定 turn detection**，讓對話流程自然
3. **開啟降噪**，提升語音辨識效果
4. **用 `setInterruptResponse(true)`** 好好處理打斷
5. **輸入音訊的轉錄用 Whisper**
6. **對話結束時要正確關閉 session**

## Error Handling

```java
session.receiveEvents()
    .doOnError(error -> System.err.println("Connection error: " + error.getMessage()))
    .onErrorResume(error -> {
        // 嘗試重新連線或清理
        return Flux.empty();
    })
    .subscribe();
```

## Reference Links

| Resource | URL |
|----------|-----|
| GitHub Source | https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/ai/azure-ai-voicelive |
| Samples | https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/ai/azure-ai-voicelive/src/samples |
