---
name: videodb
description: 用 VideoDB Python SDK 擷取、索引、搜尋、剪輯和監控影片與音訊：從檔案、URL 或 RTSP 串流上傳，建立語音和場景索引，做帶時間戳的搜尋並產生可播放的片段，轉碼與重新構圖，做時間軸剪輯（字幕、疊加層、配音），並對直播串流或桌面擷取執行即時警報。處理影片搜尋、轉錄、剪輯片段、轉碼、串流或直播影片警報時使用。
metadata:
  origin: ECC
allowed-tools: Read Grep Glob Bash(python:*)
argument-hint: "[task description]"
---

# VideoDB Skill

**給影片、直播串流和桌面 session 用的感知 + 記憶 + 動作。**

## 何時使用

### 桌面感知
- 啟動/停止**桌面 session**，擷取**螢幕、麥克風和系統音訊**
- 串流**即時 context**，並儲存**情節式的 session 記憶**
- 對說出口的內容和螢幕上發生的事，執行**即時警報/觸發**
- 產出 **session 摘要**、可搜尋的時間軸，和**可播放的證據連結**

### 影片擷取 + 串流
- 擷取**檔案或 URL**，並回傳**可播放的網頁串流連結**
- 轉碼/正規化：**編碼、位元率、fps、解析度、長寬比**

### 索引 + 搜尋（時間戳 + 證據）
- 建立**視覺**、**語音**和**關鍵字**索引
- 搜尋並回傳帶有**時間戳**和**可播放證據**的確切時刻
- 從搜尋結果自動建立**片段**

### 時間軸剪輯 + 生成
- 字幕：**產生**、**翻譯**、**燒入**
- 疊加層：**文字/圖片/品牌**、動態字幕
- 音訊：**背景音樂**、**旁白**、**配音**
- 透過**時間軸操作**做程式化的合成和匯出

### 直播串流 (RTSP) + 監控
- 連接 **RTSP/直播串流**
- 執行**即時的視覺和語音理解**，並為監控工作流發出**事件/警報**

## 運作方式

### 常見的輸入
- 本機**檔案路徑**、公開 **URL** 或 **RTSP URL**
- 桌面擷取請求：**start / stop / summarize session**
- 想要的操作：取得用於理解的 context、轉碼規格、索引規格、搜尋查詢、片段範圍、時間軸剪輯、警報規則

### 常見的輸出
- **串流 URL**
- 帶有**時間戳**和**證據連結**的搜尋結果
- 產生的素材：字幕、音訊、圖片、片段
- 直播串流的**事件/警報 payload**
- 桌面 **session 摘要**和記憶項目

### 執行 Python 程式碼

在執行任何 VideoDB 程式碼之前，先切換到專案目錄並載入環境變數：

```python
from dotenv import load_dotenv
load_dotenv(".env")

import videodb
conn = videodb.connect()
```

這會從這些地方讀取 `VIDEO_DB_API_KEY`：
1. 環境變數（如果已經 export）
2. 目前目錄下專案的 `.env` 檔

如果缺少 key，`videodb.connect()` 會自動丟出 `AuthenticationError`。

簡短的行內指令能解決時，不要寫 script 檔。

寫行內 Python（`python -c "..."`）時，一定要使用格式正確的程式碼，用分號分隔陳述式，並保持可讀。超過約 3 個陳述式的內容，就改用 heredoc：

```bash
python << 'EOF'
from dotenv import load_dotenv
load_dotenv(".env")

import videodb
conn = videodb.connect()
coll = conn.get_collection()
print(f"Videos: {len(coll.get_videos())}")
EOF
```

### 設定

當使用者要求「setup videodb」或類似的事情時：

### 1. 安裝 SDK

```bash
pip install "videodb[capture]" python-dotenv
```

如果 `videodb[capture]` 在 Linux 上失敗，就不帶 capture extra 安裝：

```bash
pip install videodb python-dotenv
```

### 2. 設定 API key

使用者必須用**其中一種**方式設定 `VIDEO_DB_API_KEY`：

- **在終端機 export**（在啟動 Claude 之前）：`export VIDEO_DB_API_KEY=your-key`
- **專案的 `.env` 檔**：把 `VIDEO_DB_API_KEY=your-key` 存在專案的 `.env` 檔裡

到 [console.videodb.io](https://console.videodb.io) 取得免費的 API key（50 次免費上傳，不需要信用卡）。

**不要**自己讀取、寫入或處理 API key。一律讓使用者自己設定。

### 速查

### 上傳媒體

```python
# URL
video = coll.upload(url="https://example.com/video.mp4")

# YouTube
video = coll.upload(url="https://www.youtube.com/watch?v=VIDEO_ID")

# Local file
video = coll.upload(file_path="/path/to/video.mp4")
```

### 逐字稿 + 字幕

```python
# force=True skips the error if the video is already indexed
video.index_spoken_words(force=True)
text = video.get_transcript_text()
stream_url = video.add_subtitle()
```

### 在影片內搜尋

```python
from videodb.exceptions import InvalidRequestError

video.index_spoken_words(force=True)

# search() raises InvalidRequestError when no results are found.
# Always wrap in try/except and treat "No results found" as empty.
try:
    results = video.search("product demo")
    shots = results.get_shots()
    stream_url = results.compile()
except InvalidRequestError as e:
    if "No results found" in str(e):
        shots = []
    else:
        raise
```

### 場景搜尋

```python
import re
from videodb import SearchType, IndexType, SceneExtractionType
from videodb.exceptions import InvalidRequestError

# index_scenes() has no force parameter — it raises an error if a scene
# index already exists. Extract the existing index ID from the error.
try:
    scene_index_id = video.index_scenes(
        extraction_type=SceneExtractionType.shot_based,
        prompt="Describe the visual content in this scene.",
    )
except Exception as e:
    match = re.search(r"id\s+([a-f0-9]+)", str(e))
    if match:
        scene_index_id = match.group(1)
    else:
        raise

# Use score_threshold to filter low-relevance noise (recommended: 0.3+)
try:
    results = video.search(
        query="person writing on a whiteboard",
        search_type=SearchType.semantic,
        index_type=IndexType.scene,
        scene_index_id=scene_index_id,
        score_threshold=0.3,
    )
    shots = results.get_shots()
    stream_url = results.compile()
except InvalidRequestError as e:
    if "No results found" in str(e):
        shots = []
    else:
        raise
```

### 時間軸剪輯

**重要：** 建立時間軸之前，一定要先驗證時間戳：
- `start` 必須 >= 0（負值會被悄悄接受，但產生壞掉的輸出）
- `start` 必須 < `end`
- `end` 必須 <= `video.length`

```python
from videodb.timeline import Timeline
from videodb.asset import VideoAsset, TextAsset, TextStyle

timeline = Timeline(conn)
timeline.add_inline(VideoAsset(asset_id=video.id, start=10, end=30))
timeline.add_overlay(0, TextAsset(text="The End", duration=3, style=TextStyle(fontsize=36)))
stream_url = timeline.generate_stream()
```

### 轉碼影片（變更解析度 / 品質）

```python
from videodb import TranscodeMode, VideoConfig, AudioConfig

# Change resolution, quality, or aspect ratio server-side
job_id = conn.transcode(
    source="https://example.com/video.mp4",
    callback_url="https://example.com/webhook",
    mode=TranscodeMode.economy,
    video_config=VideoConfig(resolution=720, quality=23, aspect_ratio="16:9"),
    audio_config=AudioConfig(mute=False),
)
```

### 重新構圖長寬比（給社群平台）

**警告：** `reframe()` 是很慢的伺服器端操作。對長影片可能要花
好幾分鐘，也可能 timeout。最佳實務：
- 可能的話，一律用 `start`/`end` 限制在一小段
- 對完整長度的影片，用 `callback_url` 做非同步處理
- 先在 `Timeline` 上修剪影片，再對比較短的結果重新構圖

```python
from videodb import ReframeMode

# Always prefer reframing a short segment:
reframed = video.reframe(start=0, end=60, target="vertical", mode=ReframeMode.smart)

# Async reframe for full-length videos (returns None, result via webhook):
video.reframe(target="vertical", callback_url="https://example.com/webhook")

# Presets: "vertical" (9:16), "square" (1:1), "landscape" (16:9)
reframed = video.reframe(start=0, end=60, target="square")

# Custom dimensions
reframed = video.reframe(start=0, end=60, target={"width": 1280, "height": 720})
```

### 生成式媒體

```python
image = coll.generate_image(
    prompt="a sunset over mountains",
    aspect_ratio="16:9",
)
```

## 錯誤處理

```python
from videodb.exceptions import AuthenticationError, InvalidRequestError

try:
    conn = videodb.connect()
except AuthenticationError:
    print("Check your VIDEO_DB_API_KEY")

try:
    video = coll.upload(url="https://example.com/video.mp4")
except InvalidRequestError as e:
    print(f"Upload failed: {e}")
```

### 常見陷阱

| 情境 | 錯誤訊息 | 解法 |
|----------|--------------|----------|
| 對已經索引過的影片再做索引 | `Spoken word index for video already exists` | 用 `video.index_spoken_words(force=True)`，已索引就跳過 |
| 場景索引已經存在 | `Scene index with id XXXX already exists` | 用 `re.search(r"id\s+([a-f0-9]+)", str(e))` 從錯誤訊息取出現有的 `scene_index_id` |
| 搜尋找不到符合的結果 | `InvalidRequestError: No results found` | 攔截例外，當成空結果處理（`shots = []`） |
| Reframe timeout | 在長影片上無限期阻塞 | 用 `start`/`end` 限制片段，或傳 `callback_url` 做非同步 |
| Timeline 上的負時間戳 | 悄悄產生壞掉的串流 | 建立 `VideoAsset` 之前，一定要驗證 `start >= 0` |
| `generate_video()` / `create_collection()` 失敗 | `Operation not allowed` 或 `maximum limit` | 這些是方案限定的功能，要告訴使用者方案的限制 |

## 範例

### 標準 prompt
- "Start desktop capture and alert when a password field appears."
- "Record my session and produce an actionable summary when it ends."
- "Ingest this file and return a playable stream link."
- "Index this folder and find every scene with people, return timestamps."
- "Generate subtitles, burn them in, and add light background music."
- "Connect this RTSP URL and alert when a person enters the zone."

### 螢幕錄影（桌面擷取）

用 `ws_listener.py` 在錄影 session 期間擷取 WebSocket 事件。桌面擷取只支援 **macOS**。

#### 快速開始

1. **選擇 state 目錄**：`STATE_DIR="${VIDEODB_EVENTS_DIR:-$HOME/.local/state/videodb}"`
2. **啟動 listener**，要從專案目錄啟動，這樣它才會讀專案的 `.env`：`VIDEODB_EVENTS_DIR="$STATE_DIR" python "${CLAUDE_SKILL_DIR}/scripts/ws_listener.py" --clear "$STATE_DIR" &`
3. **取得 WebSocket ID**：`cat "$STATE_DIR/videodb_ws_id"`
4. **執行擷取程式碼**（完整流程見 reference/capture.md）
5. **事件寫入到**：`$STATE_DIR/videodb_events.jsonl`

參考檔案裡的 `scripts/ws_listener.py`，是相對於這個 skill 的目錄（`${CLAUDE_SKILL_DIR}`），不是相對於專案。
Claude Code 會填入 `${CLAUDE_SKILL_DIR}`。其他 host 會讓它是空的，所以要換成這個 skill 安裝的目錄（Codex 是 `$HOME/.codex/skills/videodb`；`~` 在引號裡不會展開）。

每次啟動全新的擷取執行時，都要用 `--clear`，這樣過期的逐字稿和視覺事件才不會洩漏到新的 session。

#### 查詢事件

```python
import json
import os
import time
from pathlib import Path

events_dir = Path(os.environ.get("VIDEODB_EVENTS_DIR", Path.home() / ".local" / "state" / "videodb"))
events_file = events_dir / "videodb_events.jsonl"
events = []

if events_file.exists():
    with events_file.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

transcripts = [e["data"]["text"] for e in events if e.get("channel") == "transcript"]
cutoff = time.time() - 300
recent_visual = [
    e for e in events
    if e.get("channel") == "visual_index" and e["unix_ts"] > cutoff
]
```

## 額外文件

參考文件放在跟這個 SKILL.md 相鄰的 `reference/` 目錄。需要時可以用 Glob 工具找到它。

- [reference/api-reference.md](reference/api-reference.md) - 完整的 VideoDB Python SDK API 參考
- [reference/search.md](reference/search.md) - 影片搜尋的深入指南（語音和以場景為基礎）
- [reference/editor.md](reference/editor.md) - 時間軸剪輯、素材和合成
- [reference/streaming.md](reference/streaming.md) - HLS 串流和即時播放
- [reference/generative.md](reference/generative.md) - AI 驅動的媒體生成（圖片、影片、音訊）
- [reference/rtstream.md](reference/rtstream.md) - 直播串流擷取工作流（RTSP/RTMP）
- [reference/rtstream-reference.md](reference/rtstream-reference.md) - RTStream SDK 方法和 AI 管線
- [reference/capture.md](reference/capture.md) - 桌面擷取工作流
- [reference/capture-reference.md](reference/capture-reference.md) - 擷取 SDK 和 WebSocket 事件
- [reference/use-cases.md](reference/use-cases.md) - 常見的影片處理模式和範例

**VideoDB 支援某項操作時，不要用 ffmpeg、moviepy 或本機編碼工具。** 下面這些全都由 VideoDB 在伺服器端處理：修剪、合併片段、疊加音訊或音樂、加字幕、文字/圖片疊加層、轉碼、解析度變更、長寬比轉換、依平台需求調整大小、轉錄，以及媒體生成。只有 reference/editor.md 的 Limitations 底下列出的操作（轉場、變速、裁切/縮放、調色、音量混合），才退回使用本機工具。

### 什麼情況用什麼

| 問題 | VideoDB 的解法 |
|---------|-----------------|
| 平台拒絕影片的長寬比或解析度 | `video.reframe()`，或搭配 `VideoConfig` 的 `conn.transcode()` |
| 需要為 Twitter/Instagram/TikTok 調整影片大小 | `video.reframe(target="vertical")` 或 `target="square"` |
| 需要變更解析度（例如 1080p → 720p） | 搭配 `VideoConfig(resolution=720)` 的 `conn.transcode()` |
| 需要在影片上疊加音訊/音樂 | 在 `Timeline` 上用 `AudioAsset` |
| 需要加字幕 | `video.add_subtitle()` 或 `CaptionAsset` |
| 需要合併/修剪片段 | 在 `Timeline` 上用 `VideoAsset` |
| 需要生成旁白、音樂或音效 | `coll.generate_voice()`、`generate_music()`、`generate_sound_effect()` |

## 來源

這個 skill 的參考資料以 vendored 的方式放在本機的 `skills/videodb/reference/` 底下。
請使用上面的本機副本，不要在 runtime 去追外部 repo 的連結。
