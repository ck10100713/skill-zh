---
name: fal-ai-media
description: 透過 fal.ai MCP 統一產生媒體：圖片、影片與音訊。涵蓋文字生圖（Nano Banana）、文字/圖片生影片（Seedance、Kling、Veo 3）、文字轉語音（CSM-1B），以及影片生音訊（ThinkSound）。在使用者想用 AI 產生圖片、影片或音訊時使用。
metadata:
  origin: ECC
---

# fal.ai 媒體生成

> **容易過時的 skill。** fal.ai 的 model ID、價格、輸入和 MCP 工具名稱
> 變動很快。在承諾某個模型、參數、輸出格式或費用之前，
> 先搜尋或抓取最新的模型 metadata。

透過 MCP 使用 fal.ai 模型產生圖片、影片和音訊。

## 何時啟用

- 使用者想從文字 prompt 產生圖片
- 從文字或圖片建立影片
- 產生語音、音樂或音效
- 任何媒體生成任務
- 使用者說「generate image」、「create video」、「text to speech」、「make a thumbnail」或類似的話

## MCP 需求

必須設定好 fal.ai MCP server。加到 `~/.claude.json`：

```json
"fal-ai": {
  "command": "npx",
  "args": ["-y", "fal-ai-mcp-server"],
  "env": { "FAL_KEY": "YOUR_FAL_KEY_HERE" }
}
```

到 [fal.ai](https://fal.ai) 取得 API key。

## MCP 工具

fal.ai MCP 提供這些工具：
- `search`：用關鍵字找可用的模型
- `find`：取得模型細節與參數
- `generate`：用參數執行模型
- `result`：檢查非同步生成的狀態
- `status`：檢查 job 狀態
- `cancel`：取消執行中的 job
- `estimate_cost`：估算生成費用
- `models`：列出熱門模型
- `upload`：上傳檔案當作輸入

---

## 圖片生成

### Nano Banana 2（快速）
最適合：快速迭代、草稿、文字生圖、圖片編輯。

```
generate(
  app_id: "fal-ai/nano-banana-2",
  input_data: {
    "prompt": "a futuristic cityscape at sunset, cyberpunk style",
    "image_size": "landscape_16_9",
    "num_images": 1,
    "seed": 42
  }
)
```

### Nano Banana Pro（高擬真）
最適合：正式產出的圖片、寫實感、字體排印、細節豐富的 prompt。

```
generate(
  app_id: "fal-ai/nano-banana-pro",
  input_data: {
    "prompt": "professional product photo of wireless headphones on marble surface, studio lighting",
    "image_size": "square",
    "num_images": 1,
    "guidance_scale": 7.5
  }
)
```

### 常用圖片參數

| 參數 | 型別 | 選項 | 備註 |
|-------|------|---------|-------|
| `prompt` | string | required | 描述你想要的內容 |
| `image_size` | string | `square`, `portrait_4_3`, `landscape_16_9`, `portrait_16_9`, `landscape_4_3` | 長寬比 |
| `num_images` | number | 1-4 | 要產生幾張 |
| `seed` | number | any integer | 可重現性 |
| `guidance_scale` | number | 1-20 | 要多貼近 prompt（越高越字面） |

### 圖片編輯
用 Nano Banana 2 搭配輸入圖片，做 inpainting、outpainting 或風格轉換：

```
# First upload the source image
upload(file_path: "/path/to/image.png")

# Then generate with image input
generate(
  app_id: "fal-ai/nano-banana-2",
  input_data: {
    "prompt": "same scene but in watercolor style",
    "image_url": "<uploaded_url>",
    "image_size": "landscape_16_9"
  }
)
```

---

## 影片生成

### Seedance 1.0 Pro（ByteDance）
最適合：文字生影片、動態品質高的圖片生影片。

```
generate(
  app_id: "fal-ai/seedance-1-0-pro",
  input_data: {
    "prompt": "a drone flyover of a mountain lake at golden hour, cinematic",
    "duration": "5s",
    "aspect_ratio": "16:9",
    "seed": 42
  }
)
```

### Kling Video v3 Pro
最適合：附原生音訊生成的文字/圖片生影片。

```
generate(
  app_id: "fal-ai/kling-video/v3/pro",
  input_data: {
    "prompt": "ocean waves crashing on a rocky coast, dramatic clouds",
    "duration": "5s",
    "aspect_ratio": "16:9"
  }
)
```

### Veo 3（Google DeepMind）
最適合：帶生成音效、視覺品質高的影片。

```
generate(
  app_id: "fal-ai/veo-3",
  input_data: {
    "prompt": "a bustling Tokyo street market at night, neon signs, crowd noise",
    "aspect_ratio": "16:9"
  }
)
```

### 圖片生影片
從現有的圖片開始：

```
generate(
  app_id: "fal-ai/seedance-1-0-pro",
  input_data: {
    "prompt": "camera slowly zooms out, gentle wind moves the trees",
    "image_url": "<uploaded_image_url>",
    "duration": "5s"
  }
)
```

### 影片參數

| 參數 | 型別 | 選項 | 備註 |
|-------|------|---------|-------|
| `prompt` | string | required | 描述影片 |
| `duration` | string | `"5s"`, `"10s"` | 影片長度 |
| `aspect_ratio` | string | `"16:9"`, `"9:16"`, `"1:1"` | 畫面比例 |
| `seed` | number | any integer | 可重現性 |
| `image_url` | string | URL | 圖片生影片用的來源圖片 |

---

## 音訊生成

### CSM-1B（對話式語音）
自然、有對話感的文字轉語音。

```
generate(
  app_id: "fal-ai/csm-1b",
  input_data: {
    "text": "Hello, welcome to the demo. Let me show you how this works.",
    "speaker_id": 0
  }
)
```

### ThinkSound（影片生音訊）
從影片內容產生搭配的音訊。

```
generate(
  app_id: "fal-ai/thinksound",
  input_data: {
    "video_url": "<video_url>",
    "prompt": "ambient forest sounds with birds chirping"
  }
)
```

### ElevenLabs（透過 API，不用 MCP）
要專業的語音合成，直接使用 ElevenLabs：

```python
import os
import requests

resp = requests.post(
    "https://api.elevenlabs.io/v1/text-to-speech/<voice_id>",
    headers={
        "xi-api-key": os.environ["ELEVENLABS_API_KEY"],
        "Content-Type": "application/json"
    },
    json={
        "text": "Your text here",
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
)
with open("output.mp3", "wb") as f:
    f.write(resp.content)
```

### VideoDB 生成式音訊
如果有設定 VideoDB，就用它的生成式音訊：

```python
# Voice generation
audio = coll.generate_voice(text="Your narration here", voice="alloy")

# Music generation
music = coll.generate_music(prompt="upbeat electronic background music", duration=30)

# Sound effects
sfx = coll.generate_sound_effect(prompt="thunder crack followed by rain")
```

---

## 費用估算

生成之前，先檢查預估費用：

```
estimate_cost(
  estimate_type: "unit_price",
  endpoints: {
    "fal-ai/nano-banana-pro": {
      "unit_quantity": 1
    }
  }
)
```

## 模型探索

為特定任務找模型：

```
search(query: "text to video")
find(endpoint_ids: ["fal-ai/seedance-1-0-pro"])
models()
```

## 小技巧

- 迭代 prompt 時用 `seed` 取得可重現的結果
- prompt 迭代先用較低成本的模型（Nano Banana 2），定稿時再換成 Pro
- 影片的 prompt 要描述清楚但精簡，聚焦在動作與場景
- 圖片生影片比純文字生影片更能控制結果
- 執行昂貴的影片生成之前，先檢查 `estimate_cost`

## 相關 Skill

- `tasteforge-video`：離線的品味萃取與模態規劃。它的
  endpoint 候選與 request manifest 只供參考，不是已提交的
  job 或已儲存的 Fal 工作流。TasteForge 的交接不代表授權上傳
  或生成；請使用另外授權的 provider 工作流，並在執行前驗證
  它目前的 endpoint schema。
- `videodb`：影片處理、剪輯與串流
- `video-editing`：AI 驅動的影片剪輯工作流
- `content-engine`：社群平台的內容創作
