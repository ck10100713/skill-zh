---
name: video-editing
description: AI 輔助的影片剪輯工作流，用來剪輯、建立結構和擴充真實素材。涵蓋從原始拍攝，經過 FFmpeg、Remotion、ElevenLabs、fal.ai，一直到在 Descript 或 CapCut 做最後收尾的完整流程。當使用者想剪影片、剪素材、做 vlog，或製作影片內容時使用。
metadata:
  origin: ECC
---

# Video Editing

AI 輔助真實素材的剪輯。不是用 prompt 生成，而是快速剪輯現有的影片。

## 何時啟用

- 使用者想剪輯、剪裁或整理影片素材的結構
- 把長時間的錄影變成短影音內容
- 用原始拍攝的素材製作 vlog、教學或 demo 影片
- 為現有影片加上疊加層、字幕、音樂或旁白
- 為不同平台（YouTube、TikTok、Instagram）重新構圖影片
- 使用者說「edit video」、「cut this footage」、「make a vlog」或「video workflow」

## 核心主張

當你不再要求 AI 創造整支影片，而是開始用它來壓縮、整理結構和擴充真實素材時，AI 影片剪輯才有用。價值不在生成，價值在壓縮。

## 流程

對以量測為基礎、由參考片驅動的工作，先把 `taste-distillation` 接到
`taste-application`，再回到這裡處理剪輯器和最終輸出的 review。
獨立的 taste skill 可以使用既有素材；生成是選用的。

在對剪輯器或 DAW 做即時變更之前，先保存一個有版本的專案 checkpoint，並
驗證檔案確實存在。變更之後，再保存並驗證另一個 checkpoint。
API 讀回只能證明目前記憶體內的狀態，不能證明已經存檔。
在交接時，要把 render 出來的媒體、可編輯的專案和創意核可，
當成各自獨立的狀態。

對由 MIDI 驅動的音訊，要對照接收端 rack 的音符對應檢查音高，
並實際試聽結果；成功建立 clip 仍然可能產生無聲。
對重建出來的專案，要透過原生的載入和存檔來驗證，把事件依
時間軸順序排好，驗證取樣連結和靜音狀態，然後檢查並試聽
確切匯出的音訊，看有沒有非預期的無聲。光是 XML 解析，
並不能證明 DAW 接受了每個 clip，或產生了聽得到的輸出。
呼叫較新的指令之前，要先檢查橋接的能力交握。不要把
開啟上傳或訓練資料遙測當成創意任務的副作用；
在缺少同意或能力時，要使用支援的本機控制路徑。

```
Screen Studio / raw footage
  → Claude / Codex
  → FFmpeg
  → Remotion
  → ElevenLabs / fal.ai
  → Descript or CapCut
```

每一層都有特定的工作。不要跳層。不要試圖讓一個工具做所有事。

## 第 1 層：擷取（Screen Studio / 原始素材）

收集來源素材：
- **Screen Studio**：給 app demo、寫程式過程、瀏覽器工作流用的精緻螢幕錄影
- **原始攝影機素材**：vlog 素材、訪談、活動錄影
- **透過 VideoDB 做桌面擷取**：帶有即時 context 的 session 錄影（見 `videodb` skill）

輸出：準備好整理的原始檔案。

## 第 2 層：整理（Claude / Codex）

用 Claude Code 或 Codex 來：
- **轉錄並標記**：產生逐字稿，找出主題和議題
- **規劃結構**：決定什麼留下、什麼剪掉、什麼順序有效
- **找出冗餘的段落**：找出停頓、離題和重複的 take
- **產生剪輯決策清單**：要剪的時間戳、要保留的片段
- **搭出 FFmpeg 和 Remotion 程式碼的骨架**：產生指令和合成

```
Example prompt:
"Here's the transcript of a 4-hour recording. Identify the 8 strongest segments
for a 24-minute vlog. Give me FFmpeg cut commands for each segment."
```

這一層處理的是結構，不是最終的創意品味。

## 第 3 層：確定性的剪輯（FFmpeg）

FFmpeg 處理無聊但關鍵的工作：切割、修剪、串接和前處理。

### 依時間戳擷取片段

```bash
ffmpeg -i raw.mp4 -ss 00:12:30 -to 00:15:45 -c copy segment_01.mp4
```

### 依剪輯決策清單批次剪輯

```bash
#!/bin/bash
# cuts.txt: start,end,label
while IFS=, read -r start end label; do
  ffmpeg -i raw.mp4 -ss "$start" -to "$end" -c copy "segments/${label}.mp4"
done < cuts.txt
```

### 串接片段

```bash
# Create file list
for f in segments/*.mp4; do echo "file '$f'"; done > concat.txt
ffmpeg -f concat -safe 0 -i concat.txt -c copy assembled.mp4
```

### 建立 proxy 加快剪輯

```bash
ffmpeg -i raw.mp4 -vf "scale=960:-2" -c:v libx264 -preset ultrafast -crf 28 proxy.mp4
```

### 擷取音訊做轉錄

```bash
ffmpeg -i raw.mp4 -vn -acodec pcm_s16le -ar 16000 audio.wav
```

### 正規化音量

```bash
ffmpeg -i segment.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=11 -c:v copy normalized.mp4
```

## 第 4 層：可程式化的合成（Remotion）

Remotion 把剪輯問題變成可組合的程式碼。用它處理傳統剪輯器做起來很痛苦的事：

### 何時使用 Remotion

- 疊加層：文字、圖片、品牌、lower third
- 資料視覺化：圖表、統計、動態數字
- 動態圖形：轉場、解說動畫
- 可組合的場景：跨影片重用的範本
- 產品 demo：加註解的截圖、UI 重點標示

### 基本的 Remotion 合成

```tsx
import { AbsoluteFill, Sequence, Video, useCurrentFrame } from "remotion";

export const VlogComposition: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill>
      {/* Main footage */}
      <Sequence from={0} durationInFrames={300}>
        <Video src="/segments/intro.mp4" />
      </Sequence>

      {/* Title overlay */}
      <Sequence from={30} durationInFrames={90}>
        <AbsoluteFill style={{
          justifyContent: "center",
          alignItems: "center",
        }}>
          <h1 style={{
            fontSize: 72,
            color: "white",
            textShadow: "2px 2px 8px rgba(0,0,0,0.8)",
          }}>
            The AI Editing Stack
          </h1>
        </AbsoluteFill>
      </Sequence>

      {/* Next segment */}
      <Sequence from={300} durationInFrames={450}>
        <Video src="/segments/demo.mp4" />
      </Sequence>
    </AbsoluteFill>
  );
};
```

### Render 輸出

```bash
npx remotion render src/index.ts VlogComposition output.mp4
```

詳細的模式和 API 參考，請看 [Remotion 文件](https://www.remotion.dev/docs)。

## 第 5 層：生成的素材（ElevenLabs / fal.ai）

只生成你需要的。不要生成整支影片。

### 用 ElevenLabs 做旁白

```python
import os
import requests

resp = requests.post(
    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
    headers={
        "xi-api-key": os.environ["ELEVENLABS_API_KEY"],
        "Content-Type": "application/json"
    },
    json={
        "text": "Your narration text here",
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
)
with open("voiceover.mp3", "wb") as f:
    f.write(resp.content)
```

### 用 fal.ai 做音樂和音效

使用 `fal-ai-media` skill 來做：
- 背景音樂生成
- 音效（ThinkSound 模型，影片轉音訊）
- 轉場音效

### 用 fal.ai 生成視覺素材

用在插入鏡頭、縮圖，或不存在的 b-roll：
```
generate(app_id: "fal-ai/nano-banana-pro", input_data: {
  "prompt": "professional thumbnail for tech vlog, dark background, code on screen",
  "image_size": "landscape_16_9"
})
```

### VideoDB 的生成式音訊

如果有設定 VideoDB：
```python
voiceover = coll.generate_voice(text="Narration here", voice="alloy")
music = coll.generate_music(prompt="lo-fi background for coding vlog", duration=120)
sfx = coll.generate_sound_effect(prompt="subtle whoosh transition")
```

## 第 6 層：最後收尾（Descript / CapCut）

最後一層是人的工作。用傳統剪輯器處理：
- **節奏**：調整感覺太快或太慢的剪點
- **字幕**：自動產生，再手動清理
- **調色**：基本校正和氛圍
- **最終混音**：平衡人聲、音樂和音效的音量
- **匯出**：平台專屬的格式和品質設定

品味就住在這裡。AI 清掉重複的工作，最終的決定由你來做。

## 社群媒體重新構圖

不同平台需要不同的長寬比：

| 平台 | 長寬比 | 解析度 |
|----------|-------------|------------|
| YouTube | 16:9 | 1920x1080 |
| TikTok / Reels | 9:16 | 1080x1920 |
| Instagram Feed | 1:1 | 1080x1080 |
| X / Twitter | 16:9 或 1:1 | 1280x720 或 720x720 |

### 用 FFmpeg 重新構圖

```bash
# 16:9 to 9:16 (center crop)
ffmpeg -i input.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920" vertical.mp4

# 16:9 to 1:1 (center crop)
ffmpeg -i input.mp4 -vf "crop=ih:ih,scale=1080:1080" square.mp4
```

### 用 VideoDB 重新構圖

```python
from videodb import ReframeMode

# Smart reframe (AI-guided subject tracking)
reframed = video.reframe(start=0, end=60, target="vertical", mode=ReframeMode.smart)
```

## 場景偵測與自動剪輯

### FFmpeg 場景偵測

```bash
# Detect scene changes (threshold 0.3 = moderate sensitivity)
ffmpeg -i input.mp4 -vf "select='gt(scene,0.3)',showinfo" -vsync vfr -f null - 2>&1 | grep showinfo
```

### 用靜音偵測做自動剪輯

```bash
# Find silent segments (useful for cutting dead air)
ffmpeg -i input.mp4 -af silencedetect=noise=-30dB:d=2 -f null - 2>&1 | grep silence
```

### 精華擷取

用 Claude 分析逐字稿 + 場景時間戳：
```
"Given this transcript with timestamps and these scene change points,
identify the 5 most engaging 30-second clips for social media."
```

## 各工具最擅長的事

| 工具 | 強項 | 弱項 |
|------|----------|----------|
| Claude / Codex | 整理、規劃、產生程式碼 | 不是創意品味那一層 |
| FFmpeg | 確定性的剪輯、批次處理、格式轉換 | 沒有視覺化的剪輯介面 |
| Remotion | 可程式化的疊加層、可組合的場景、可重用的範本 | 對非開發者有學習曲線 |
| Screen Studio | 馬上就有精緻的螢幕錄影 | 只能擷取螢幕 |
| ElevenLabs | 語音、旁白、音樂、音效 | 不是工作流的核心 |
| Descript / CapCut | 最終的節奏、字幕、收尾 | 手動，無法自動化 |

## 關鍵原則

1. **剪輯，不要生成。** 這個工作流是用來剪真實素材，不是用 prompt 創造。
2. **先結構，後風格。** 在碰任何視覺的東西之前，先在第 2 層把故事弄對。
3. **FFmpeg 是骨幹。** 無聊但關鍵。長素材就是在這裡變得好處理。
4. **Remotion 帶來可重複性。** 如果你會做超過一次，就把它做成 Remotion 元件。
5. **選擇性地生成。** 只對不存在的素材使用 AI 生成，不要什麼都用。
6. **品味是最後一層。** AI 清掉重複的工作。最終的創意決定由你來做。

## 原生 Fusion 預設

[ITO Production v1](assets/fusion/ito-production-v1/README.md) 提供克制的高光 bloom、相反方向的 RGB 空間偏移，以及亮度/邊緣的光暈。這些確切的檔案，在經過兩個來源的視覺 review 之後，通過了先前的原生匯入、存檔/重新開啟，和短時間動態 render 檢查。這些只是需要依個別鏡頭 review 的起始值；光暈不會偵測或追蹤主體。

[ITO V28](assets/fusion/ito-v28/README.md) 包含保留下來、經原生驗證的 Fusion graph 片段，和一個冪等的 Lua 安裝程式。這些是技術相容性的範例，**不是建議的 production 預設值**：它們有記載的視覺限制，使用前需要調整和品味 review。先前匯入和 render 檢查的範圍，請看這個 bundle 的來源說明。

## 相關 Skills

- `fal-ai-media`：AI 圖像、影片和音訊生成
- `videodb`：伺服器端的影片處理、索引和串流
- `content-engine`：各平台原生的內容發布
