---
name: podcast-generation
description: 透過 WebSocket 使用 Azure OpenAI 的 GPT Realtime Mini 模型，產生 AI 驅動的 podcast 風格語音旁白。適用於建立文字轉語音功能、語音旁白生成、把內容做成 podcast，或串接 Azure OpenAI Realtime API 取得真實音訊輸出。涵蓋從 React 前端到 Python FastAPI 後端、搭配 WebSocket 串流的完整全端實作。
---

# 用 GPT Realtime Mini 產生 Podcast

用 Azure OpenAI 的 Realtime API，把文字內容變成真正的語音旁白。

## 快速開始

1. 設定 Realtime API 的環境變數
2. 透過 WebSocket 連到 Azure OpenAI Realtime endpoint
3. 送出文字 prompt，收集 PCM 音訊 chunk 和逐字稿
4. 把 PCM 轉成 WAV 格式
5. 把 base64 編碼的音訊回傳給前端播放

## 環境設定

```env
AZURE_OPENAI_AUDIO_API_KEY=your_realtime_api_key
AZURE_OPENAI_AUDIO_ENDPOINT=https://your-resource.cognitiveservices.azure.com
AZURE_OPENAI_AUDIO_DEPLOYMENT=gpt-realtime-mini
```

**注意**：Endpoint 絕對不要包含 `/openai/v1/`，只放 base URL。

## 核心流程

### 後端音訊生成

```python
from openai import AsyncOpenAI
import base64

# Convert HTTPS endpoint to WebSocket URL
ws_url = endpoint.replace("https://", "wss://") + "/openai/v1"

client = AsyncOpenAI(
    websocket_base_url=ws_url,
    api_key=api_key
)

audio_chunks = []
transcript_parts = []

async with client.realtime.connect(model="gpt-realtime-mini") as conn:
    # Configure for audio-only output
    await conn.session.update(session={
        "output_modalities": ["audio"],
        "instructions": "You are a narrator. Speak naturally."
    })
    
    # Send text to narrate
    await conn.conversation.item.create(item={
        "type": "message",
        "role": "user",
        "content": [{"type": "input_text", "text": prompt}]
    })
    
    await conn.response.create()
    
    # Collect streaming events
    async for event in conn:
        if event.type == "response.output_audio.delta":
            audio_chunks.append(base64.b64decode(event.delta))
        elif event.type == "response.output_audio_transcript.delta":
            transcript_parts.append(event.delta)
        elif event.type == "response.done":
            break

# Convert PCM to WAV (see scripts/pcm_to_wav.py)
pcm_audio = b''.join(audio_chunks)
wav_audio = pcm_to_wav(pcm_audio, sample_rate=24000)
```

### 前端音訊播放

```javascript
// Convert base64 WAV to playable blob
const base64ToBlob = (base64, mimeType) => {
  const bytes = atob(base64);
  const arr = new Uint8Array(bytes.length);
  for (let i = 0; i < bytes.length; i++) arr[i] = bytes.charCodeAt(i);
  return new Blob([arr], { type: mimeType });
};

const audioBlob = base64ToBlob(response.audio_data, 'audio/wav');
const audioUrl = URL.createObjectURL(audioBlob);
new Audio(audioUrl).play();
```

## 語音選項

| Voice | 特色 |
|-------|-----------|
| alloy | 中性 |
| echo | 溫暖 |
| fable | 富表現力 |
| onyx | 低沉 |
| nova | 親切 |
| shimmer | 清晰 |

## Realtime API 事件

- `response.output_audio.delta` - Base64 音訊 chunk
- `response.output_audio_transcript.delta` - 逐字稿文字
- `response.done` - 生成完成
- `error` - 用 `event.error.message` 處理

## 音訊格式

- **輸入**：文字 prompt
- **輸出**：PCM 音訊（24kHz、16-bit、單聲道）
- **儲存**：Base64 編碼的 WAV

## 參考資料

- **完整架構**：完整的技術堆疊設計請看 [references/architecture.md](references/architecture.md)
- **程式碼範例**：正式環境的寫法請看 [references/code-examples.md](references/code-examples.md)
- **PCM 轉換**：音訊格式轉換請用 [scripts/pcm_to_wav.py](scripts/pcm_to_wav.py)
