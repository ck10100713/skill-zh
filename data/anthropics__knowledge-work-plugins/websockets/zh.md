---
name: setup-zoom-websockets
description: Zoom WebSockets 的參考 skill。導向低延遲事件工作流程之後，在需要持久連線、更快的事件遞送，或安全限制讓 WebSockets 比 webhook 更合適時使用。
triggers:
  - "zoom websockets"
  - "websocket event subscription"
  - "persistent zoom events"
  - "low latency zoom events"
  - "zoom websocket connection"
---

# /setup-zoom-websockets

Zoom 持久事件串流的背景參考。優先用工作流程路由，當 WebSockets 很可能比 webhook 更合適時，再用這個檔案。

## WebSockets vs Webhooks

| 面向 | WebSockets | Webhooks |
|--------|------------|----------|
| **連線** | 持久、雙向 | 一次性的 HTTP POST |
| **延遲** | 較低（沒有 HTTP 額外負擔） | 較高（每個事件都要新連線） |
| **安全** | 直接連線，不暴露 endpoint | 需要 endpoint 驗證、IP 白名單 |
| **模式** | Pull（你連到 Zoom） | Push（Zoom 連到你） |
| **狀態** | 有狀態（維持連線） | 無狀態（每個事件各自獨立） |
| **設定** | 較複雜（access token、連線） | 較簡單（只要 endpoint URL） |

**這些情況選 WebSockets：**
- 即時、低延遲的更新很關鍵
- 安全是最優先（銀行、醫療、金融）
- 你不想暴露公開的 endpoint
- 你需要雙向通訊

**這些情況選 Webhooks：**
- 偏好較簡單的設定
- 事件通知的數量不多
- 已經有 HTTP 基礎設施

## 先決條件

- [Zoom Marketplace](https://marketplace.zoom.us/) 裡的 Server-to-Server OAuth app
- Account ID、Client ID 和 Client Secret
- 啟用了事件的 WebSocket 訂閱

> **需要 S2S OAuth 的協助？** 完整的驗證流程請看 **[zoom-oauth](../oauth/SKILL.md)** skill。

> **快速開始排查：** 深入除錯之前，先用 **[5-Minute Runbook](RUNBOOK.md)**。

## Quick Start

### 1. 建立 Server-to-Server OAuth App

1. 前往 [Zoom Marketplace](https://marketplace.zoom.us/develop/create)
2. 建立一個 **Server-to-Server OAuth** app
3. 複製 Account ID、Client ID、Client Secret

### 2. 啟用 WebSocket 訂閱

1. 在你的 app 裡，前往 **Feature** → **Event Subscriptions**
2. 新增一個 Event Subscription
3. 選擇 **WebSockets** 當作方法類型
4. 選擇要訂閱的事件（例如 `meeting.created`、`meeting.started`）
5. 儲存：會產生一個 endpoint URL

### 3. 透過 WebSocket 連線

```javascript
const WebSocket = require('ws');
const axios = require('axios');

// 步驟 1：取得 access token
async function getAccessToken() {
  const credentials = Buffer.from(`${CLIENT_ID}:${CLIENT_SECRET}`).toString('base64');
  
  const response = await axios.post(
    'https://zoom.us/oauth/token',
    new URLSearchParams({
      grant_type: 'account_credentials',
      account_id: ACCOUNT_ID
    }),
    {
      headers: {
        'Authorization': `Basic ${credentials}`,
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    }
  );
  
  return response.data.access_token;
}

// 步驟 2：連到 WebSocket
async function connectWebSocket() {
  const accessToken = await getAccessToken();
  
  // 從你的訂閱設定取得 WebSocket URL
  const wsUrl = `wss://ws.zoom.us/ws?subscriptionId=${SUBSCRIPTION_ID}&access_token=${accessToken}`;
  
  const ws = new WebSocket(wsUrl);
  
  ws.on('open', () => {
    console.log('WebSocket connection established');
  });
  
  ws.on('message', (data) => {
    const event = JSON.parse(data);
    console.log('Event received:', event.event);
    
    // 處理不同的事件類型
    switch (event.event) {
      case 'meeting.started':
        console.log(`Meeting started: ${event.payload.object.topic}`);
        break;
      case 'meeting.ended':
        console.log(`Meeting ended: ${event.payload.object.uuid}`);
        break;
      case 'meeting.participant_joined':
        console.log(`Participant joined: ${event.payload.object.participant.user_name}`);
        break;
    }
  });
  
  ws.on('close', (code, reason) => {
    console.log(`Connection closed: ${code} - ${reason}`);
    // 實作重新連線的邏輯
  });
  
  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
  });
  
  return ws;
}

connectWebSocket();
```

## 事件格式

透過 WebSocket 收到的事件，格式跟 webhook 事件一樣：

```json
{
  "event": "meeting.started",
  "event_ts": 1706123456789,
  "payload": {
    "account_id": "abcD3ojkdbjfg",
    "object": {
      "id": 1234567890,
      "uuid": "abcdefgh-1234-5678-abcd-1234567890ab",
      "host_id": "xyz789",
      "topic": "Team Standup",
      "type": 2,
      "start_time": "2024-01-25T10:00:00Z",
      "timezone": "America/Los_Angeles"
    }
  }
}
```

## 常見事件

| 事件 | 說明 |
|-------|-------------|
| `meeting.created` | 會議已排程 |
| `meeting.updated` | 會議設定已變更 |
| `meeting.deleted` | 會議已刪除 |
| `meeting.started` | 會議開始 |
| `meeting.ended` | 會議結束 |
| `meeting.participant_joined` | 參與者加入會議 |
| `meeting.participant_left` | 參與者離開會議 |
| `recording.completed` | 雲端錄影已就緒 |
| `user.created` | 新增使用者 |
| `user.updated` | 使用者資料已變更 |

## 連線管理

### Keep-Alive

WebSocket 連線需要定期 heartbeat。Zoom 會關閉閒置的連線。

```javascript
// 每 30 秒送一次 ping
setInterval(() => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.ping();
  }
}, 30000);
```

### 重新連線

實作自動重新連線以提高可靠度：

```javascript
function connectWithReconnect() {
  const ws = connectWebSocket();
  
  ws.on('close', () => {
    console.log('Connection lost. Reconnecting in 5 seconds...');
    setTimeout(connectWithReconnect, 5000);
  });
  
  return ws;
}
```

### 單一連線限制

**重要：** 每個訂閱同一時間只能開一條 WebSocket 連線。開新的連線會把既有的那條關掉。

## 詳細參考

- **[references/connection.md](references/connection.md)** - 連線生命週期、驗證、錯誤處理
- **[references/events.md](references/events.md)** - 完整的事件類型參考

## 疑難排解

- **[troubleshooting/common-issues.md](troubleshooting/common-issues.md)** - 訂閱 URL 搞混、斷線、收不到事件的除錯

## 範例 Repo

### 官方 / 社群

| 類型 | Repository | 說明 |
|------|------------|-------------|
| Node.js | [just-zoomit/zoom-websockets](https://github.com/just-zoomit/zoom-websockets) | 搭配 S2S OAuth 的 WebSocket 範例 |

## WebSockets vs RTMS

不要把 WebSockets 跟 RTMS（Realtime Media Streams）搞混：

| 功能 | WebSockets | RTMS |
|---------|------------|------|
| **目的** | 事件通知 | 媒體串流 |
| **資料** | 會議事件、使用者事件 | 音訊、影像、逐字稿 |
| **使用情境** | 回應 Zoom 事件 | AI/ML、即時轉錄 |
| **Skill** | 這個 skill | **rtms** |

需要即時音訊/影像/逐字稿資料時，改用 **rtms** skill。

## 資源

- **WebSockets 文件**：https://developers.zoom.us/docs/api/websockets/
- **Webhooks 比較**：https://www.zoom.com/en/blog/a-guide-to-webhooks-and-websockets/
- **開發者論壇**：https://devforum.zoom.us/

## 環境變數

- 標準化的 `.env` key，以及每個值要去哪裡找，請看 [references/environment-variables.md](references/environment-variables.md)。
