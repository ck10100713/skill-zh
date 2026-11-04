---
name: zoom-rtms
description: Zoom RTMS 的參考 skill。在已經導向 live-media 工作流程之後，處理即時音訊、視訊、聊天、逐字稿、螢幕分享或客服中心語音串流時使用。
user-invocable: false
triggers:
  - "real-time media"
  - "rtms"
  - "live audio stream"
  - "live video stream"
  - "meeting transcription"
  - "raw audio"
  - "raw video"
  - "websocket media"
  - "live transcript"
  - "streaming audio"
  - "streaming video"
  - "meeting bot media"
  - "contact center voice media"
  - "participant video on"
  - "participant video off"
  - "single individual video stream"
---

# Zoom 即時媒體串流（RTMS）

即時 Zoom 媒體 pipeline 的背景參考。請先用 `build-zoom-bot`，再用這個 skill 查串流類型、能力，以及 RTMS 特有的實作限制。

# Zoom 即時媒體串流（RTMS）

專家指引：即時存取 Zoom 會議、網路研討會、Video SDK session 和 Zoom Contact Center Voice 的音訊、視訊、逐字稿、聊天和螢幕分享資料。RTMS 使用基於 WebSocket 的協定，採開放標準，而且不需要會議機器人（bot）就能擷取媒體層。

## 先讀這段（關鍵）

RTMS 基本上是一個**後端的媒體擷取服務**。

- 你的後端接收並處理即時媒體：**音訊、視訊、螢幕分享、聊天、逐字稿**。
- RTMS 本身不是前端 UI SDK。
- 處理是**事件觸發**的：後端要等到 RTMS 開始的 webhook 事件，才開始處理串流。

選用的架構（常見）：

- 加一個 **Zoom App SDK** 前端，提供 client 內的 UI／控制項。
- 透過 **WebSocket**（或 SSE、gRPC、queue worker 等）把後端 RTMS 的輸出串流給前端。

用 RTMS 處理媒體／資料層，用前端框架／Zoom Apps 處理呈現和使用者互動。

**官方文件**：https://developers.zoom.us/docs/rtms/
**SDK 參考（JS）**：https://zoom.github.io/rtms/js/
**SDK 參考（Python）**：https://zoom.github.io/rtms/py/
**範例 Repository**：https://github.com/zoom/rtms-samples

## 快速連結

**剛接觸 RTMS？照這個順序走：**

1. **[Connection Architecture](concepts/connection-architecture.md)** - 兩階段 WebSocket 設計
2. **[SDK Quickstart](examples/sdk-quickstart.md)** - 接收媒體最快的方式（建議）
3. **[Manual WebSocket](examples/manual-websocket.md)** - 不用 SDK、完整掌控協定
4. **[Media Types](references/media-types.md)** - 音訊、視訊、逐字稿、聊天、螢幕分享

**完整實作：**
- **[RTMS Bot](examples/rtms-bot.md)** - 端到端的 bot 實作指南

**參考：**
- **[Lifecycle Flow](concepts/lifecycle-flow.md)** - 從 webhook 到串流的完整流程
- **[Data Types](references/data-types.md)** - 所有 enum 和常數
- **[Webhooks](references/webhooks.md)** - 事件訂閱的細節
- **[Environment Variables](references/environment-variables.md)** - 憑證模式和執行期參數
- **[Quickstart Notes](references/quickstart.md)** - 次要的快速入門指南
- **Integrated Index** - 見本檔案下方的區段

**遇到問題？**
- 連線失敗 -> [Common Issues](troubleshooting/common-issues.md)
- 重複連線 -> [Webhook Gotchas](troubleshooting/common-issues.md#webhook-response-timing)
- 沒有音訊／視訊 -> [Media Configuration](references/media-types.md)
- 先做 preflight 檢查 -> [5-Minute Runbook](RUNBOOK.md)

## 支援的產品

| 產品 | Webhook 事件 | Payload ID | App 類型 |
|---------|--------------|------------|----------|
| **Meetings** | `meeting.rtms_started` / `meeting.rtms_stopped` | `meeting_uuid` | General App |
| **Webinars** | `webinar.rtms_started` / `webinar.rtms_stopped` | `meeting_uuid`（一樣！） | General App |
| **Video SDK** | `session.rtms_started` / `session.rtms_stopped` | `session_id` | Video SDK App |
| **Zoom Contact Center Voice** | 各產品專屬的 RTMS/ZCC Voice 事件 | 各產品專屬的串流／session 識別碼 | Contact Center / 已核准的 RTMS 整合 |

連線之後，核心的 signaling／media socket 模型在各產品之間是共用的。Meetings、webinars 和 Video SDK session 用大家熟悉的 start/stop webhook。Zoom Contact Center Voice 加上它自己的 RTMS/ZCC Voice 事件系列，應該視為同一個傳輸模型，只是事件 payload 因產品而異。

## RTMS 概覽

RTMS 是一條資料 pipeline，讓你的 app 能存取 Zoom 會議、網路研討會和 Video SDK session 的即時媒體，**不需要參與者 bot**。不用讓自動化的 client 加入會議，而是用 RTMS 直接從 Zoom 的基礎設施蒐集媒體資料。

### RTMS 提供什麼

| 媒體類型 | 格式 | 使用情境 |
|------------|--------|-----------|
| **Audio** | PCM (L16)、G.711、G.722、Opus | 轉錄、語音分析、錄製 |
| **Video** | H.264、JPG、PNG | 錄製、AI 視覺、縮圖、活躍參與者選擇 |
| **Screen Share** | H.264、JPG、PNG | 內容擷取、投影片擷取 |
| **Transcript** | JSON 文字 | 會議記錄、搜尋、合規 |
| **Chat** | JSON 文字 | 封存、情緒分析 |

### 2026 年 3 月的協定變更

- **Zoom Contact Center Voice 支援**：RTMS 現在涵蓋 Contact Center Voice 的音訊和逐字稿情境。
- **逐字稿語言辨識（Language Identification）控制**：逐字稿媒體 handshake 現在支援 `src_language` 和 `enable_lid`。預設行為是啟用 LID。設定 `enable_lid: false` 可以強制使用固定語言。
- **單一個人視訊串流訂閱**：當 `data_opt` 設為 `VIDEO_SINGLE_INDIVIDUAL_STREAM` 時，RTMS 現在可以一次只串流一位參與者的鏡頭畫面。
- **client 發起的優雅關閉**：後端可以透過 signaling socket 送出 `STREAM_CLOSE_REQ`，然後等待 `STREAM_CLOSE_RESP`。
- **媒體 keep-alive 容忍度提高**：media socket 的 keep-alive 逾時現在是 **65 秒**，不是 35 秒。

### 兩種做法

| 做法 | 適合 | 複雜度 |
|----------|----------|------------|
| **SDK**（`@zoom/rtms`） | 大多數使用情境 | 低：幫你處理 WebSocket 的複雜度 |
| **Manual WebSocket** | 自訂協定、其他語言 | 高：要實作完整的協定 |

## 先決條件

- **Node.js 20.3.0+**（建議 24 LTS），給 JavaScript SDK 用
- **Python 3.10+**，給 Python SDK 用
- Zoom General App（給會議／網路研討會）或 Video SDK App（給 Video SDK），並啟用 RTMS 功能
- 接收 RTMS 事件的 webhook endpoint
- 接收 WebSocket 串流的伺服器

> **需要 RTMS 存取權限？** 到 [Zoom Developer Forum](https://devforum.zoom.us/) 發文，附上你的使用情境，申請 RTMS 存取權限。

## 快速開始（SDK，建議）

```javascript
import rtms from "@zoom/rtms";

// All RTMS start/stop events across products
const RTMS_EVENTS = ["meeting.rtms_started", "webinar.rtms_started", "session.rtms_started"];

// Handle webhook events
rtms.onWebhookEvent(({ event, payload }) => {
  if (!RTMS_EVENTS.includes(event)) return;

  const client = new rtms.Client();

  client.onAudioData((data, timestamp, metadata) => {
    console.log(`Audio from ${metadata.userName}: ${data.length} bytes`);
  });

  client.onTranscriptData((data, timestamp, metadata) => {
    const text = data.toString('utf8');
    console.log(`${metadata.userName}: ${text}`);
  });

  client.onJoinConfirm((reason) => {
    console.log(`Joined session: ${reason}`);
  });

  // SDK handles all WebSocket connections automatically
  // Accepts both meeting_uuid and session_id transparently
  client.join(payload);
});
```

## 快速開始（Manual WebSocket）

想完整掌控，或使用沒有 SDK 的語言，就要實作兩階段的 WebSocket 協定：

```javascript
const WebSocket = require('ws');
const crypto = require('crypto');

const RTMS_EVENTS = ['meeting.rtms_started', 'webinar.rtms_started', 'session.rtms_started'];

// 1. Generate signature
// For meetings/webinars: uses meeting_uuid. For Video SDK: uses session_id.
function generateSignature(clientId, idValue, streamId, clientSecret) {
  const message = `${clientId},${idValue},${streamId}`;
  return crypto.createHmac('sha256', clientSecret).update(message).digest('hex');
}

// 2. Handle webhook
app.post('/webhook', (req, res) => {
  res.status(200).send();  // CRITICAL: Respond immediately!
  
  const { event, payload } = req.body;
  if (RTMS_EVENTS.includes(event)) {
    connectToRTMS(payload);
  }
});

// 3. Connect to signaling WebSocket
function connectToRTMS(payload) {
  const { server_urls, rtms_stream_id } = payload;
  // meeting_uuid for meetings/webinars, session_id for Video SDK
  const idValue = payload.meeting_uuid || payload.session_id;
  const signature = generateSignature(CLIENT_ID, idValue, rtms_stream_id, CLIENT_SECRET);
  
  const signalingWs = new WebSocket(server_urls);
  
  signalingWs.on('open', () => {
    signalingWs.send(JSON.stringify({
      msg_type: 1,  // Handshake request
      protocol_version: 1,
      meeting_uuid: idValue,
      rtms_stream_id,
      signature,
      media_type: 9  // AUDIO(1) | TRANSCRIPT(8)
    }));
  });
  
  // ... handle responses, connect to media WebSocket
}
```

**參見**：完整實作請看 [Manual WebSocket Guide](examples/manual-websocket.md)。

## 媒體類型 Bitmask

用位元運算 OR 組合各類型：

| 類型 | 值 | 說明 |
|------|-------|-------------|
| Audio | 1 | PCM 音訊樣本 |
| Video | 2 | H.264/JPG 視訊影格 |
| Screen Share | 4 | **跟視訊是分開的！** |
| Transcript | 8 | 即時語音轉文字 |
| Chat | 16 | 會議中的聊天訊息 |
| All | 32 | 所有媒體類型 |

**範例**：Audio + Transcript = `1 | 8` = `9`

## 關鍵陷阱

| 問題 | 解法 |
|-------|----------|
| **只允許 1 條連線** | 新連線會把既有的踢掉。要追蹤活躍的 session！ |
| **立刻回 200** | 如果 webhook 延遲，Zoom 會重試，造成重複連線 |
| **Heartbeat 是強制的** | 收到 msg_type 12 要回 msg_type 13，否則連線會斷 |
| **重新連線是你的工作** | RTMS 不會自動重連。媒體 keep-alive 容忍度現在約 **65 秒**；signaling 則維持約 **60 秒** |
| **逐字稿語言飄移** | 想要固定語言的轉錄、而不是自動切換語言時，用 `src_language` 加 `enable_lid: false` |
| **只支援單一參與者視訊** | `VIDEO_SINGLE_INDIVIDUAL_STREAM` 一次只支援一位參與者。新的 `VIDEO_SUBSCRIPTION_REQ` 會覆蓋先前的選擇 |
| **優雅關閉現在是明確的** | 後端想要乾淨地結束串流時，用 `STREAM_CLOSE_REQ` / `STREAM_CLOSE_RESP` |

## 環境變數

### SDK 環境變數

```bash
# Required - Authentication
ZM_RTMS_CLIENT=your_client_id          # Zoom OAuth Client ID
ZM_RTMS_SECRET=your_client_secret      # Zoom OAuth Client Secret

# Optional - Webhook server
ZM_RTMS_PORT=8080                      # Default: 8080
ZM_RTMS_PATH=/webhook                  # Default: /

# Optional - Logging
ZM_RTMS_LOG_LEVEL=info                 # error, warn, info, debug, trace
ZM_RTMS_LOG_FORMAT=progressive         # progressive or json
ZM_RTMS_LOG_ENABLED=true
```

### 手動實作用的變數

```bash
ZOOM_CLIENT_ID=your_client_id
ZOOM_CLIENT_SECRET=your_client_secret
ZOOM_SECRET_TOKEN=your_webhook_token   # For webhook validation
```

## Zoom App 設定

### 給 Meetings 和 Webinars（General App）

1. 前往 [marketplace.zoom.us](https://marketplace.zoom.us) -> Develop -> Build App
2. 選擇 **General App** -> **User-Managed**
3. Features -> Access -> **Enable Event Subscription**
4. Add Events -> 搜尋「rtms」-> 選取：
   - `meeting.rtms_started`
   - `meeting.rtms_stopped`
   - `webinar.rtms_started`（如果用 webinar）
   - `webinar.rtms_stopped`（如果用 webinar）
5. Scopes -> Add Scopes -> 搜尋「rtms」-> 新增：
   - `meeting:read:meeting_audio`
   - `meeting:read:meeting_video`
   - `meeting:read:meeting_transcript`
   - `meeting:read:meeting_chat`
   - `webinar:read:webinar_audio`（如果用 webinar）
   - `webinar:read:webinar_video`（如果用 webinar）
   - `webinar:read:webinar_transcript`（如果用 webinar）
   - `webinar:read:webinar_chat`（如果用 webinar）

### 給 Video SDK（Video SDK App）

1. 前往 [marketplace.zoom.us](https://marketplace.zoom.us) -> Develop -> Build App
2. 選擇 **Video SDK App**
3. 使用你的 SDK Key 和 SDK Secret（不是 OAuth Client ID/Secret）
4. Add Events：
   - `session.rtms_started`
   - `session.rtms_stopped`

## 範例 Repository

### 官方範例

| Repository | 說明 |
|------------|-------------|
| [rtms-samples](https://github.com/zoom/rtms-samples) | RTMSManager、樣板、AI 範例 |
| [rtms-quickstart-js](https://github.com/zoom/rtms-quickstart-js) | JavaScript SDK 快速入門 |
| [rtms-quickstart-py](https://github.com/zoom/rtms-quickstart-py) | Python SDK 快速入門 |
| [rtms-sdk-cpp](https://github.com/zoom/rtms-sdk-cpp) | C++ SDK |
| [zoom-rtms](https://github.com/zoom/rtms) | SDK 主要 repository |

### AI 整合範例

| 範例 | 說明 |
|--------|-------------|
| [rtms-meeting-assistant-starter-kit](https://github.com/zoom/rtms-meeting-assistant-starter-kit) | 附摘要功能的 AI 會議助理 |
| [arlo-meeting-assistant](https://github.com/zoom/arlo-meeting-assistant) | 附資料庫的正式環境會議助理 |
| [videosdk-rtms-transcribe-audio](https://github.com/zoom/videosdk-rtms-transcribe-audio) | Whisper 轉錄 |

## 完整文件

### 概念
- **[Connection Architecture](concepts/connection-architecture.md)** - 兩階段 WebSocket 設計
- **[Lifecycle Flow](concepts/lifecycle-flow.md)** - 從 webhook 到串流的流程

### 範例
- **[SDK Quickstart](examples/sdk-quickstart.md)** - 使用 @zoom/rtms SDK
- **[Manual WebSocket](examples/manual-websocket.md)** - 原始協定實作
- **[RTMS Bot](examples/rtms-bot.md)** - 完整的 bot 實作指南
- **[AI Integration](examples/ai-integration.md)** - 轉錄與分析的模式

### 參考
- **[Media Types](references/media-types.md)** - 音訊、視訊、逐字稿、聊天、螢幕分享
- **[Data Types](references/data-types.md)** - 所有 enum 和常數
- **[Connection](references/connection.md)** - WebSocket 協定細節
- **[Webhooks](references/webhooks.md)** - 事件訂閱

### 疑難排解
- **[Common Issues](troubleshooting/common-issues.md)** - FAQ 和解法

## 資源

- **官方文件**：https://developers.zoom.us/docs/rtms/
- **資料類型**：https://developers.zoom.us/docs/rtms/data-types/
- **媒體參數**：https://developers.zoom.us/docs/rtms/media-parameter-definition/
- **開發者論壇**：https://devforum.zoom.us/

---

**需要協助？** 先看下面的 Integrated Index 區段，裡面有完整的導覽。

---

## Integrated Index

_這個區段是從 `SKILL.md` 搬過來的。_

RTMS 提供即時存取 Zoom 會議、網路研討會和 Video SDK session 的音訊、視訊、逐字稿、聊天和螢幕分享。

## 關鍵定位

把 RTMS 當成接收並處理媒體串流的**後端服務**。

- 後端的角色：擷取音訊／視訊／分享／聊天／逐字稿，執行 AI／分析，持久化／轉送資料。
- 選用的前端角色：Zoom App SDK 或網頁 dashboard，透過後端的傳輸管道（WebSocket/SSE/其他）取用處理過的串流資料。
- 啟動模型：後端等待 RTMS 開始的 webhook 事件，然後開始處理串流。

不要把 RTMS 當成純前端的 SDK 來設計。

## 快速上手路徑

**如果你剛接觸 RTMS，照這個順序：**

1. **先跑 preflight 檢查** -> [RUNBOOK.md](RUNBOOK.md)
2. **理解架構** -> [concepts/connection-architecture.md](concepts/connection-architecture.md)
   - 兩階段 WebSocket：Signaling + Media
   - 為什麼 RTMS 不用 bot

3. **選擇你的做法** -> SDK 或 Manual
   - SDK（建議）：[examples/sdk-quickstart.md](examples/sdk-quickstart.md)
   - Manual WebSocket：[examples/manual-websocket.md](examples/manual-websocket.md)

4. **理解生命週期** -> [concepts/lifecycle-flow.md](concepts/lifecycle-flow.md)
   - Webhook -> Signaling -> Media -> Streaming

5. **設定媒體類型** -> [references/media-types.md](references/media-types.md)
   - 音訊、視訊、逐字稿、聊天、螢幕分享

6. **排查問題** -> [troubleshooting/common-issues.md](troubleshooting/common-issues.md)
   - 連線問題、重複的 webhook、資料遺失

---

## 文件結構

```
rtms/
├── SKILL.md                           # Main skill overview
├── SKILL.md                           # This file - navigation guide
│
├── concepts/                          # Core architectural patterns
│   ├── connection-architecture.md     # Two-phase WebSocket design
│   └── lifecycle-flow.md              # Webhook to streaming flow
│
├── examples/                          # Complete working code
│   ├── sdk-quickstart.md              # Using @zoom/rtms SDK
│   ├── manual-websocket.md            # Raw protocol implementation
│   ├── rtms-bot.md                    # Complete RTMS bot implementation
│   └── ai-integration.md              # Transcription and analysis
│
├── references/                        # Reference documentation
│   ├── media-types.md                 # Audio, video, transcript, chat, share
│   ├── data-types.md                  # All enums and constants
│   ├── connection.md                  # WebSocket protocol details
│   └── webhooks.md                    # Event subscription
│
└── troubleshooting/                   # Problem solving guides
    └── common-issues.md               # FAQ and solutions
```

---

## 依使用情境

### 我想取得會議逐字稿
1. [SDK Quickstart](examples/sdk-quickstart.md) - 最快的做法
2. [Media Types](references/media-types.md#transcript) - 逐字稿設定
3. [AI Integration](examples/ai-integration.md) - Whisper、Deepgram、AssemblyAI

### 我想錄製會議
1. [Media Types](references/media-types.md) - 音訊 + 視訊設定
2. [SDK Quickstart](examples/sdk-quickstart.md) - 接收媒體
3. [AI Integration](examples/ai-integration.md#audio-recording) - 補齊空缺的錄製

### 我想做 AI 會議助理
1. [AI Integration](examples/ai-integration.md) - 完整的模式
2. [SDK Quickstart](examples/sdk-quickstart.md) - 媒體擷取
3. [Lifecycle Flow](concepts/lifecycle-flow.md) - 事件處理

### 我想做完整的 RTMS bot
1. [RTMS Bot](examples/rtms-bot.md) - **完整的實作指南**
2. [Lifecycle Flow](concepts/lifecycle-flow.md) - 從 webhook 到串流的流程
3. [Connection Architecture](concepts/connection-architecture.md) - 兩階段設計

### 我需要完整掌控協定
1. [Manual WebSocket](examples/manual-websocket.md) - **從這裡開始**
2. [Connection Architecture](concepts/connection-architecture.md) - 兩階段設計
3. [Data Types](references/data-types.md) - 所有訊息類型和 enum
4. [Connection](references/connection.md) - 協定細節

### 我遇到連線錯誤
1. [Common Issues](troubleshooting/common-issues.md) - 診斷檢查清單
2. [Connection Architecture](concepts/connection-architecture.md) - 驗證流程
3. [Webhooks](references/webhooks.md) - 驗證與時間點

### 我想理解架構
1. [Connection Architecture](concepts/connection-architecture.md) - 兩階段 WebSocket
2. [Lifecycle Flow](concepts/lifecycle-flow.md) - 完整流程圖
3. [Data Types](references/data-types.md) - 協定常數

---

## 依產品

### 我在做 Zoom Meetings
- 標準的 RTMS 設定。Webhook 事件：`meeting.rtms_started`。使用有 OAuth 的 General App。
- 從 [SDK Quickstart](examples/sdk-quickstart.md) 或 [Manual WebSocket](examples/manual-websocket.md) 開始。

### 我在做 Zoom Webinars
- 跟會議一樣，但 webhook 事件是 `webinar.rtms_started`。Payload 仍然用 `meeting_uuid`（不是 `webinar_uuid`）。
- 加上 webinar 的 scope 和事件訂閱。見 [Webhooks](references/webhooks.md)。
- 只有 **panelist** 的串流確認可用。與會者（attendee）的串流可能不是個別的。

### 我在做 Zoom Video SDK
- Webhook 事件：`session.rtms_started`。Payload 用 `session_id`（不是 `meeting_uuid`）。
- 需要有 SDK Key/Secret 的 **Video SDK App**（不是 OAuth Client ID/Secret）。
- 連線之後，協定跟會議**完全相同**。
- Payload 細節見 [Webhooks](references/webhooks.md)。

---

## 關鍵文件

### 1. Connection Architecture（關鍵）
**[concepts/connection-architecture.md](concepts/connection-architecture.md)**

RTMS 使用**兩條獨立的 WebSocket 連線**：
- **Signaling WebSocket**：認證、控制、heartbeat
- **Media WebSocket**：實際的音訊／視訊／逐字稿資料

### 2. SDK vs Manual（決策點）
**[examples/sdk-quickstart.md](examples/sdk-quickstart.md)** vs **[examples/manual-websocket.md](examples/manual-websocket.md)**

| SDK | Manual |
|-----|--------|
| 處理 WebSocket 的複雜度 | 完整掌控協定 |
| 自動重連 | 自己做重連 |
| 程式碼較少 | 程式碼較多 |
| 最適合大多數使用情境 | 最適合自訂需求 |

### 3. 關鍵陷阱（最常見的問題）
**[troubleshooting/common-issues.md](troubleshooting/common-issues.md)**

1. **立刻回 200**：webhook 回應延遲會造成重複
2. **每個串流只有 1 條連線**：新連線會把既有的踢掉
3. **需要 heartbeat**：必須回應 keep-alive，否則連線會斷
4. **追蹤活躍的 session**：避免重複的加入嘗試

---

## 關鍵心得

### 重要發現：

1. **兩階段 WebSocket 設計**
   - Signaling：控制層（handshake、heartbeat、start/stop）
   - Media：資料層（音訊、視訊、逐字稿、聊天、分享）
   - 見：[Connection Architecture](concepts/connection-architecture.md)

2. **Webhook 回應時間**
   - 一定要在做任何處理**之前**先回 200
   - 延遲回應 -> Zoom 重試 -> 重複連線
   - 見：[Common Issues](troubleshooting/common-issues.md#webhook-response-timing)

3. **Heartbeat 是強制的**
   - Signaling：收到 msg_type 12，回 msg_type 13
   - Media：同樣的模式
   - 沒回應 = 連線被關閉
   - 見：[Connection](references/connection.md#heartbeat)

4. **簽章產生**
   - 格式：`HMAC-SHA256(clientSecret, "clientId,meetingUuid,streamId")`
   - Video SDK 用 `session_id` 取代 `meetingUuid`
   - Webinar 仍然用 `meeting_uuid`（不是 `webinar_uuid`）
   - signaling 和 media 的 handshake 都需要
   - 見：[Manual WebSocket](examples/manual-websocket.md#signature-generation)

5. **媒體類型是 bitmask**
   - Audio=1、Video=2、Share=4、Transcript=8、Chat=16、All=32
   - 用 OR 組合：Audio+Transcript = 1|8 = 9
   - 見：[Media Types](references/media-types.md)

6. **螢幕分享跟視訊是分開的**
   - 不同的 msg_type（16 vs 15）
   - 不同的媒體旗標（4 vs 2）
   - 必須分別訂閱
   - 見：[Media Types](references/media-types.md#screen-share)

---

## 快速參考

### 「連線失敗」
-> [Common Issues](troubleshooting/common-issues.md)

### 「重複連線」
-> [Webhook timing](troubleshooting/common-issues.md#webhook-response-timing)

### 「沒有音訊／視訊資料」
-> [Media Types](references/media-types.md) - 檢查設定

### 「我要怎麼手動實作？」
-> [Manual WebSocket](examples/manual-websocket.md)

### 「有哪些訊息類型？」
-> [Data Types](references/data-types.md)

### 「我要怎麼整合 AI？」
-> [AI Integration](examples/ai-integration.md)

---

## 文件版本

根據 **Zoom RTMS SDK v1.x** 和截至 2026 年的官方文件。

---

**祝寫程式愉快！**

記得：想走最快的路徑就從 [SDK Quickstart](examples/sdk-quickstart.md) 開始，需要完整掌控的話就用 [Manual WebSocket](examples/manual-websocket.md)。
