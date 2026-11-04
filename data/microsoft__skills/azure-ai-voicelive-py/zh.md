---
name: azure-ai-voicelive-py
description: 用 Azure AI Voice Live SDK（azure-ai-voicelive）建構即時語音 AI 應用程式。需要和 Azure AI 做即時雙向音訊通訊的 Python 應用程式都適用，包括語音助理、支援語音的聊天機器人、即時語音對語音翻譯、語音驅動的虛擬人物，或任何用 WebSocket 對 AI 模型串流音訊的場景。支援 Server VAD（語音活動偵測）、輪流對話、function calling、MCP tools、avatar 整合和轉錄。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-ai-voicelive
---

# Azure AI Voice Live SDK

用雙向 WebSocket 通訊建構即時語音 AI 應用程式。

## Installation

```bash
pip install azure-ai-voicelive aiohttp azure-identity
```

## Environment Variables

```bash
AZURE_COGNITIVE_SERVICES_ENDPOINT=https://<region>.api.cognitive.microsoft.com  # 所有驗證方式都需要
AZURE_TOKEN_CREDENTIALS=prod # 只有在 production 使用 DefaultAzureCredential 時才需要
AZURE_COGNITIVE_SERVICES_KEY=<api-key>  # 只有下面舊版 API key 驗證路徑才需要
```

## Authentication & Lifecycle

> **🔑 下面每個程式範例都適用兩條規則：**
>
> 1. **優先用 `DefaultAzureCredential`。** 它在本機（Azure CLI / VS Code / Developer CLI）和 Azure 上（managed identity、workload identity）都能跑，程式碼不用改。避免用 connection string、account/API key，因為它們會繞過 Entra 的稽核和金鑰輪替。
>    - 本機開發：`DefaultAzureCredential` 直接可用。
>    - Production：設定 `AZURE_TOKEN_CREDENTIALS=prod`（或 `AZURE_TOKEN_CREDENTIALS=<specific_credential>`），把 credential chain 限縮在 production 安全的 credential。
> 2. **每個 client 都要包在 context manager 裡**，這樣 HTTP transport、socket 和 token cache 會確實被釋放：
>    - 同步：`with <Client>(...) as client:`
>    - 非同步：`async with <Client>(...) as client:` **而且** `async with DefaultAzureCredential() as credential:`（來自 `azure.identity.aio`）
>
> 範例程式碼可能會省略這部分設定，但 production 程式碼一定要兩條規則都遵守。

```python
import os
from azure.ai.voicelive.aio import connect
from azure.identity.aio import DefaultAzureCredential, ManagedIdentityCredential

# 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
# 或在 production 直接用指定的 credential：
# 參考 https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()

async with DefaultAzureCredential(require_envvar=True) as credential:
    async with connect(
        endpoint=os.environ["AZURE_COGNITIVE_SERVICES_ENDPOINT"],
        credential=credential,
        model="gpt-4o-realtime-preview",
        credential_scopes=["https://cognitiveservices.azure.com/.default"]
    ) as conn:
        ...
```

### Legacy: API Key (existing keyed deployments)

新程式碼請用上面的 `DefaultAzureCredential`。只有在既有的 key 驗證部署還沒遷移到 Entra ID 時才用 `AzureKeyCredential`，例如還在進行 Entra 上線的受管制環境。

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive.aio import connect

async with connect(
    endpoint=os.environ["AZURE_COGNITIVE_SERVICES_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["AZURE_COGNITIVE_SERVICES_KEY"]),
    model="gpt-4o-realtime-preview",
) as conn:
    ...
```

## Quick Start

```python
import asyncio
import os
from azure.ai.voicelive.aio import connect
from azure.identity.aio import DefaultAzureCredential

async def main():
    async with connect(
        endpoint=os.environ["AZURE_COGNITIVE_SERVICES_ENDPOINT"],
        credential=DefaultAzureCredential(),
        model="gpt-4o-realtime-preview",
        credential_scopes=["https://cognitiveservices.azure.com/.default"]
    ) as conn:
        # 用 instructions 更新 session
        await conn.session.update(session={
            "instructions": "You are a helpful assistant.",
            "modalities": ["text", "audio"],
            "voice": "alloy"
        })
        
        # 監聽事件
        async for event in conn:
            print(f"Event: {event.type}")
            if event.type == "response.audio_transcript.done":
                print(f"Transcript: {event.transcript}")
            elif event.type == "response.done":
                break

asyncio.run(main())
```

## Core Architecture

### Connection Resources

`VoiceLiveConnection` 提供這些資源：

| Resource | Purpose | Key Methods |
|----------|---------|-------------|
| `conn.session` | Session 設定 | `update(session=...)` |
| `conn.response` | 模型回應 | `create()`, `cancel()` |
| `conn.input_audio_buffer` | 音訊輸入 | `append()`, `commit()`, `clear()` |
| `conn.output_audio_buffer` | 音訊輸出 | `clear()` |
| `conn.conversation` | 對話狀態 | `item.create()`, `item.delete()`, `item.truncate()` |
| `conn.transcription_session` | 轉錄設定 | `update(session=...)` |

## Session Configuration

```python
from azure.ai.voicelive.models import RequestSession, FunctionTool

await conn.session.update(session=RequestSession(
    instructions="You are a helpful voice assistant.",
    modalities=["text", "audio"],
    voice="alloy",  # 或 "echo", "shimmer", "sage" 等
    input_audio_format="pcm16",
    output_audio_format="pcm16",
    turn_detection={
        "type": "server_vad",
        "threshold": 0.5,
        "prefix_padding_ms": 300,
        "silence_duration_ms": 500
    },
    tools=[
        FunctionTool(
            type="function",
            name="get_weather",
            description="Get current weather",
            parameters={
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        )
    ]
))
```

## Audio Streaming

### Send Audio (Base64 PCM16)

```python
import base64

# 讀取音訊片段（16-bit PCM、24kHz 單聲道）
audio_chunk = await read_audio_from_microphone()
b64_audio = base64.b64encode(audio_chunk).decode()

await conn.input_audio_buffer.append(audio=b64_audio)
```

### Receive Audio

```python
async for event in conn:
    if event.type == "response.audio.delta":
        audio_bytes = base64.b64decode(event.delta)
        await play_audio(audio_bytes)
    elif event.type == "response.audio.done":
        print("Audio complete")
```

## Event Handling

```python
async for event in conn:
    match event.type:
        # Session 事件
        case "session.created":
            print(f"Session: {event.session}")
        case "session.updated":
            print("Session updated")
        
        # 音訊輸入事件
        case "input_audio_buffer.speech_started":
            print(f"Speech started at {event.audio_start_ms}ms")
        case "input_audio_buffer.speech_stopped":
            print(f"Speech stopped at {event.audio_end_ms}ms")
        
        # 轉錄事件
        case "conversation.item.input_audio_transcription.completed":
            print(f"User said: {event.transcript}")
        case "conversation.item.input_audio_transcription.delta":
            print(f"Partial: {event.delta}")
        
        # 回應事件
        case "response.created":
            print(f"Response started: {event.response.id}")
        case "response.audio_transcript.delta":
            print(event.delta, end="", flush=True)
        case "response.audio.delta":
            audio = base64.b64decode(event.delta)
        case "response.done":
            print(f"Response complete: {event.response.status}")
        
        # Function call
        case "response.function_call_arguments.done":
            result = handle_function(event.name, event.arguments)
            await conn.conversation.item.create(item={
                "type": "function_call_output",
                "call_id": event.call_id,
                "output": json.dumps(result)
            })
            await conn.response.create()
        
        # 錯誤
        case "error":
            print(f"Error: {event.error.message}")
```

## Common Patterns

### Manual Turn Mode (No VAD)

```python
await conn.session.update(session={"turn_detection": None})

# 手動控制輪流
await conn.input_audio_buffer.append(audio=b64_audio)
await conn.input_audio_buffer.commit()  # 使用者這一輪結束
await conn.response.create()  # 觸發回應
```

### Interrupt Handling

```python
async for event in conn:
    if event.type == "input_audio_buffer.speech_started":
        # 使用者打斷了，取消目前的回應
        await conn.response.cancel()
        await conn.output_audio_buffer.clear()
```

### Conversation History

```python
# 加入 system 訊息
await conn.conversation.item.create(item={
    "type": "message",
    "role": "system",
    "content": [{"type": "input_text", "text": "Be concise."}]
})

# 加入使用者訊息
await conn.conversation.item.create(item={
    "type": "message",
    "role": "user", 
    "content": [{"type": "input_text", "text": "Hello!"}]
})

await conn.response.create()
```

## Voice Options

| Voice | Description |
|-------|-------------|
| `alloy` | 中性、平衡 |
| `echo` | 溫暖、口語 |
| `shimmer` | 清晰、專業 |
| `sage` | 沉穩、有權威感 |
| `coral` | 友善、活潑 |
| `ash` | 低沉、穩重 |
| `ballad` | 富表現力 |
| `verse` | 說故事風格 |

Azure 語音：使用 `AzureStandardVoice`、`AzureCustomVoice` 或 `AzurePersonalVoice` 模型。

## Audio Formats

| Format | Sample Rate | Use Case |
|--------|-------------|----------|
| `pcm16` | 24kHz | 預設，高品質 |
| `pcm16-8000hz` | 8kHz | 電話 |
| `pcm16-16000hz` | 16kHz | 語音助理 |
| `g711_ulaw` | 8kHz | 電話（美國） |
| `g711_alaw` | 8kHz | 電話（歐洲） |

## Turn Detection Options

```python
# Server VAD（預設）
{"type": "server_vad", "threshold": 0.5, "silence_duration_ms": 500}

# Azure Semantic VAD（更聰明的偵測）
{"type": "azure_semantic_vad"}
{"type": "azure_semantic_vad_en"}  # 針對英文優化
{"type": "azure_semantic_vad_multilingual"}
```

## Error Handling

```python
from azure.ai.voicelive.aio import ConnectionError, ConnectionClosed

try:
    async with connect(...) as conn:
        async for event in conn:
            if event.type == "error":
                print(f"API Error: {event.error.code} - {event.error.message}")
except ConnectionClosed as e:
    print(f"Connection closed: {e.code} - {e.reason}")
except ConnectionError as e:
    print(f"Connection error: {e}")
```

## Best Practices

1. **這個 SDK 只有非同步版本，全程用 `.aio` namespace。** 同一條呼叫路徑裡不要嘗試搭配其他 Azure SDK 的同步 client，整條請求路徑都保持非同步。
2. **client 和非同步 credential 一律用 context manager。** 每個連線都包在 `async with connect(...) as conn:` 裡。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，這樣 token 和 transport 才會被清掉。

## References

- **詳細 API 參考**：見 [references/api-reference.md](references/api-reference.md)
- **完整範例**：見 [references/examples.md](references/examples.md)
- **所有 Model 與型別**：見 [references/models.md](references/models.md)
