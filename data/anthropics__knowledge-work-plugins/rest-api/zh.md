---
name: build-zoom-rest-api-app
description: "Zoom REST API 的參考 skill。在選定以 API 為主的工作流程之後，需要挑 endpoint、資源管理模式、OAuth 需求、rate limit 注意事項，或 API 錯誤除錯時使用。"
triggers:
  - "api call"
  - "rest api"
  - "api create meeting"
  - "api get meeting"
  - "api list meetings"
  - "api update meeting"
  - "api delete meeting"
  - "meeting endpoint"
  - "/v2/meetings"
  - "create user"
  - "zoom api"
  - "api endpoint"
  - "recordings api"
  - "users api"
  - "webinars api"
  - "server-to-server oauth"
  - "account_credentials"
  - "account id"
  - "invalid access token"
  - "does not contain scopes"
  - "access token is expired"
  - "webhook verification"
  - "crc"
  - "download_url"
---

# /build-zoom-rest-api-app

確定性的伺服器端 Zoom 自動化和資源管理的背景參考。請先用 `plan-zoom-product`、`plan-zoom-integration` 或 `debug-zoom`，再導到這裡查 endpoint 層級的細節。

# Zoom REST API

專家指引：用 Zoom REST API 建構伺服器端整合。這個 API 提供 600 多個 endpoint，可以用程式管理會議、使用者、網路研討會、錄影、報表，以及所有 Zoom 平台資源。

**官方文件**：https://developers.zoom.us/api-hub/
**API Hub 參考**：https://developers.zoom.us/api-hub/meetings/
**OpenAPI 清單**：`https://developers.zoom.us/api-hub/<domain>/methods/endpoints.json`

## 快速連結

**剛接觸 Zoom REST API？照這個順序走：**

1. **[API Architecture](concepts/api-architecture.md)** - Base URL、區域 URL、`me` 關鍵字、ID vs UUID、時間格式
2. **[Authentication Flows](concepts/authentication-flows.md)** - OAuth 設定（S2S、User、PKCE、Device Code）
3. **[Meeting URLs vs Meeting SDK](concepts/meeting-urls-and-sdk-joining.md)** - 不要再把 `join_url` 跟 Meeting SDK 混在一起用
3. **[Meeting Lifecycle](examples/meeting-lifecycle.md)** - 建立 → 更新 → 開始 → 結束 → 刪除，搭配 webhook
4. **[Rate Limiting Strategy](concepts/rate-limiting-strategy.md)** - 方案層級、每位使用者的限制、重試模式

**參考：**
- **[Meetings](references/meetings.md)** - 會議 CRUD、類型、設定
- **[Users](references/users.md)** - 使用者佈建與管理
- **[Recordings](references/recordings.md)** - 雲端錄影的存取與下載
- **[AI Services](references/ai-services.md)** - Scribe endpoint 清單，以及目前 AI Services 的路徑介面
- **[GraphQL Queries](examples/graphql-queries.md)** - 替代的查詢 API（beta）
- **Integrated Index** - 見本檔案下方的區段

`references/` 底下大多數的領域檔案，都對齊官方 API Hub 的 `endpoints.json` 清單。把這些檔案當作查找 method／path 的本地事實來源。

**遇到問題？**
- 先做 preflight 檢查 → [5-Minute Runbook](RUNBOOK.md)
- 401 Unauthorized → [Authentication Flows](concepts/authentication-flows.md)（檢查 token 有沒有過期、scope）
- 429 Too Many Requests → [Rate Limiting Strategy](concepts/rate-limiting-strategy.md)
- 錯誤碼 → [Common Errors](troubleshooting/common-errors.md)
- 分頁搞不清楚 → [Common Issues](troubleshooting/common-issues.md)
- Webhook 沒送到 → [Webhook Server](examples/webhook-server.md)
- 從論壇整理出來的 FAQ → [Forum Top Questions](troubleshooting/forum-top-questions.md)
- Token／scope 失敗 → [Token + Scope Playbook](troubleshooting/token-scope-playbook.md)

**在做事件驅動的整合？**
- [Webhook Server](examples/webhook-server.md) - 附 CRC 驗證的 Express.js 伺服器
- [Recording Pipeline](examples/recording-pipeline.md) - 透過 webhook 事件自動下載

## 快速開始

### 取得 Access Token（Server-to-Server OAuth）

```bash
curl -X POST "https://zoom.us/oauth/token" \
  -H "Authorization: Basic $(echo -n 'CLIENT_ID:CLIENT_SECRET' | base64)" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=account_credentials&account_id=ACCOUNT_ID"
```

回應：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "scope": "meeting:read meeting:write user:read"
}
```

### 建立會議

```bash
curl -X POST "https://api.zoom.us/v2/users/HOST_USER_ID/meetings" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Team Standup",
    "type": 2,
    "start_time": "2025-03-15T10:00:00Z",
    "duration": 30,
    "settings": {
      "join_before_host": false,
      "waiting_room": true
    }
  }'
```

用 S2S OAuth 時，路徑裡要用明確的主辦者 user ID 或 email，不要用 `me`。

### 用分頁列出使用者

```bash
curl "https://api.zoom.us/v2/users?page_size=300&status=active" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

## Base URL

```
https://api.zoom.us/v2
```

### 區域 Base URL

OAuth token 回應裡的 `api_url` 欄位指出使用者所在的區域。為了符合資料落地（data residency）的合規要求，請使用區域 URL：

| 區域 | URL |
|--------|-----|
| 全球（預設） | `https://api.zoom.us/v2` |
| 澳洲 | `https://api-au.zoom.us/v2` |
| 加拿大 | `https://api-ca.zoom.us/v2` |
| 歐盟 | `https://api-eu.zoom.us/v2` |
| 印度 | `https://api-in.zoom.us/v2` |
| 沙烏地阿拉伯 | `https://api-sa.zoom.us/v2` |
| 新加坡 | `https://api-sg.zoom.us/v2` |
| 英國 | `https://api-uk.zoom.us/v2` |
| 美國 | `https://api-us.zoom.us/v2` |

**注意：** 不管 `api_url` 的值是什麼，你永遠都可以使用全球 URL `https://api.zoom.us`。

## 主要功能

| 功能 | 說明 |
|---------|-------------|
| **會議管理** | 建立、讀取、更新、刪除會議，完整控制排程 |
| **使用者佈建** | 自動化的使用者生命週期（建立、更新、停用、刪除） |
| **網路研討會操作** | 網路研討會 CRUD、報名者管理、panelist 控制 |
| **雲端錄影** | 列出、下載、刪除錄影，可依檔案類型篩選 |
| **報表與分析** | 使用量報表、參與者資料、每日統計 |
| **Team Chat** | 頻道管理、訊息、chatbot 整合 |
| **Zoom Phone** | 通話管理、語音信箱、通話路由 |
| **Zoom Rooms** | 會議室管理、裝置控制、排程 |
| **Webhooks** | 100 多種事件類型的即時事件通知 |
| **WebSockets** | 不需要公開 endpoint 的持續事件串流 |
| **GraphQL（Beta）** | 在 `v3/graphql` 的單一 endpoint 彈性查詢 |
| **AI Companion** | 會議摘要、逐字稿、AI 產生的內容 |
| **AI Services / Scribe** | 透過 Build 平台、以 JWT 驗證的 endpoint，做檔案和封存的轉錄 |

## 先決條件

- Zoom 帳號（免費方案也能用 API，但 rate limit 較低）
- 在 [Zoom App Marketplace](https://marketplace.zoom.us/) 註冊的 app
- OAuth 憑證（Server-to-Server OAuth 或 User OAuth）
- 目標 endpoint 需要的適當 scope

> **認證需要協助？** 完整的 OAuth 流程實作，請看 **[zoom-oauth](../oauth/SKILL.md)** skill。

## 關鍵陷阱與最佳實務

### ⚠️ JWT App 類型已棄用

JWT app 類型已棄用。請遷移到 **Server-to-Server OAuth**。這不會影響 Video SDK 使用的 JWT token 簽章，只影響 Marketplace 上用於 REST API 存取的「JWT」app 類型。

```javascript
// OLD (JWT app type - DEPRECATED)
const token = jwt.sign({ iss: apiKey, exp: expiry }, apiSecret);

// NEW (Server-to-Server OAuth)
const token = await getServerToServerToken(accountId, clientId, clientSecret);
```

### ⚠️ `me` 關鍵字的規則

- **User-level OAuth app**：一定要用 `me`，不要用 `userId`（否則會出現 invalid token 錯誤）
- **Server-to-Server OAuth app**：絕對不能用 `me`，要提供實際的 `userId` 或 email
- **Account-level OAuth app**：`me` 或 `userId` 都可以用

### ⚠️ Meeting ID vs UUID：雙重編碼

以 `/` 開頭或包含 `//` 的 UUID，必須做**雙重 URL 編碼**：

```javascript
// UUID: /abc==
// Single encode: %2Fabc%3D%3D
// Double encode: %252Fabc%253D%253D  ← USE THIS

const uuid = '/abc==';
const encoded = encodeURIComponent(encodeURIComponent(uuid));
const url = `https://api.zoom.us/v2/meetings/${encoded}`;
```

### ⚠️ 時間格式

- `yyyy-MM-ddTHH:mm:ssZ`：**UTC 時間**（注意 `Z` 後綴）
- `yyyy-MM-ddTHH:mm:ss`：**本地時間**（沒有 `Z`，使用 `timezone` 欄位）
- 有些報表 API 只接受 UTC。請查每個 endpoint 的 API 參考。

### ⚠️ Rate Limit 是依帳號計算，不是依 App

同一個 Zoom 帳號上的所有 app **共用** rate limit。一個很吃資源的 app 會影響其他 app。要主動監控 `X-RateLimit-Remaining` header。

### ⚠️ 每位使用者的每日上限

會議／網路研討會的建立／更新操作，限制為**每位使用者每天 100 次**（UTC 00:00 重置）。做批次操作時，要把操作分散到不同的主辦者使用者。

### ⚠️ 下載 URL 需要驗證，而且會跟著重新導向

錄影的 `download_url` 值需要 Bearer token 驗證，而且可能會重新導向。一定要跟著重新導向：

```bash
curl -L -H "Authorization: Bearer ACCESS_TOKEN" "https://zoom.us/rec/download/..."
```

### 用 Webhook，不要輪詢

```javascript
// DON'T: Poll every minute (wastes API quota)
setInterval(() => getMeetings(), 60000);

// DO: Receive webhook events in real-time
app.post('/webhook', (req, res) => {
  if (req.body.event === 'meeting.started') {
    handleMeetingStarted(req.body.payload);
  }
  res.status(200).send();
});
```

> **Webhook 設定細節：** 完整的 webhook 實作，請看 **[zoom-webhooks](../webhooks/SKILL.md)** skill。

## 完整文件庫

這個 skill 包含依類別整理的完整指南：

### 核心概念
- **[API Architecture](concepts/api-architecture.md)** - REST 設計、base URL、區域路由、`me` 關鍵字、ID vs UUID、時間格式
- **[Authentication Flows](concepts/authentication-flows.md)** - 所有 OAuth 流程（S2S、User、PKCE、Device Code）
- **[Rate Limiting Strategy](concepts/rate-limiting-strategy.md)** - 依方案的限制、重試模式、請求排隊

### 完整範例
- **[Meeting Lifecycle](examples/meeting-lifecycle.md)** - 完整的建立 → 更新 → 開始 → 結束 → 刪除流程，搭配 webhook 事件
- **[User Management](examples/user-management.md)** - 使用者 CRUD、分頁列表、批次操作
- **[Recording Pipeline](examples/recording-pipeline.md)** - 透過 webhook + API 下載錄影
- **[Webhook Server](examples/webhook-server.md)** - 附 CRC 驗證和簽章驗證的 Express.js 伺服器
- **[GraphQL Queries](examples/graphql-queries.md)** - GraphQL 的查詢、mutation、cursor 分頁

### 疑難排解
- **[Common Errors](troubleshooting/common-errors.md)** - HTTP 狀態碼、Zoom 錯誤碼、錯誤回應格式
- **[Common Issues](troubleshooting/common-issues.md)** - Rate limit、token 更新、分頁陷阱、各種坑

### 參考（39 個檔案，涵蓋所有 Zoom API 領域）

#### 核心 API
- **[references/meetings.md](references/meetings.md)** - 會議 CRUD、類型、設定
- **[references/users.md](references/users.md)** - 使用者佈建、類型、scope
- **[references/webinars.md](references/webinars.md)** - 網路研討會管理、報名者
- **[references/recordings.md](references/recordings.md)** - 雲端錄影存取
- **[references/reports.md](references/reports.md)** - 使用量報表、分析
- **[references/accounts.md](references/accounts.md)** - 帳號管理

#### 通訊
- **[references/team-chat.md](references/team-chat.md)** - Team Chat 訊息
- **[references/chatbot.md](references/chatbot.md)** - 互動式 chatbot
- **[references/phone.md](references/phone.md)** - Zoom Phone
- **[references/mail.md](references/mail.md)** - Zoom Mail
- **[references/calendar.md](references/calendar.md)** - Zoom Calendar

#### 基礎設施
- **[references/rooms.md](references/rooms.md)** - Zoom Rooms
- **[references/scim2.md](references/scim2.md)** - SCIM 2.0 佈建 API
- **[references/rate-limits.md](references/rate-limits.md)** - Rate limit 細節
- **[references/qss.md](references/qss.md)** - Quality of Service Subscription

#### 進階
- **[references/graphql.md](references/graphql.md)** - GraphQL API（beta）
- **[references/ai-companion.md](references/ai-companion.md)** - AI 功能
- **[references/authentication.md](references/authentication.md)** - 認證參考
- **[references/openapi.md](references/openapi.md)** - OpenAPI 規格、Postman、程式碼產生

#### 其他 API 領域
- **[references/events.md](references/events.md)** - Events 與事件平台 API
- **[references/scheduler.md](references/scheduler.md)** - Zoom Scheduler API
- **[references/tasks.md](references/tasks.md)** - Tasks API
- **[references/whiteboard.md](references/whiteboard.md)** - Whiteboard API
- **[references/video-management.md](references/video-management.md)** - 影片管理 API
- **[references/video-sdk-api.md](references/video-sdk-api.md)** - Video SDK REST API
- **[references/marketplace-apps.md](references/marketplace-apps.md)** - Marketplace app 管理
- **[references/commerce.md](references/commerce.md)** - 商務與帳務 API
- **[references/contact-center.md](references/contact-center.md)** - Contact Center API
- **[references/quality-management.md](references/quality-management.md)** - 品質管理 API
- **[references/workforce-management.md](references/workforce-management.md)** - 人力管理 API
- **[references/healthcare.md](references/healthcare.md)** - 醫療 API
- **[references/auto-dialer.md](references/auto-dialer.md)** - 自動撥號 API
- **[references/number-management.md](references/number-management.md)** - 號碼管理 API
- **[references/revenue-accelerator.md](references/revenue-accelerator.md)** - Revenue Accelerator API
- **[references/virtual-agent.md](references/virtual-agent.md)** - Virtual Agent API
- **[references/cobrowse-sdk-api.md](references/cobrowse-sdk-api.md)** - Cobrowse SDK API
- **[references/crc.md](references/crc.md)** - Cloud Room Connector API
- **[references/clips.md](references/clips.md)** - Clips API
- **[references/zoom-docs.md](references/zoom-docs.md)** - Zoom 文件與來源參考

## 範例 Repository

### 官方（Zoom 提供）

| 類型 | Repository |
|------|------------|
| OAuth 範例 | [oauth-sample-app](https://github.com/zoom/oauth-sample-app) |
| S2S OAuth 入門 | [server-to-server-oauth-starter-api](https://github.com/zoom/server-to-server-oauth-starter-api) |
| User OAuth | [user-level-oauth-starter](https://github.com/zoom/user-level-oauth-starter) |
| S2S Token | [server-to-server-oauth-token](https://github.com/zoom/server-to-server-oauth-token) |
| Rivet Library | [rivet-javascript](https://github.com/zoom/rivet-javascript) |
| WebSocket 範例 | [websocket-js-sample](https://github.com/zoom/websocket-js-sample) |
| Webhook 範例 | [webhook-sample-node.js](https://github.com/zoom/webhook-sample-node.js) |
| Python S2S | [server-to-server-python-sample](https://github.com/zoom/server-to-server-python-sample) |

## 資源

- **API 參考**：https://developers.zoom.us/api-hub/
- **GraphQL Playground**：https://nws.zoom.us/graphql/playground
- **Postman Collection**：https://marketplace.zoom.us/docs/api-reference/postman
- **開發者論壇**：https://devforum.zoom.us/
- **Changelog**：https://developers.zoom.us/changelog/
- **狀態頁面**：https://status.zoom.us/

---

**需要協助？** 先看下面的 Integrated Index 區段，裡面有完整的導覽。

---

## Integrated Index

_這個區段是從 `SKILL.md` 搬過來的。_

## 快速上手路徑

**如果你剛接觸 Zoom REST API，照這個順序：**

1. **先跑 preflight 檢查** → [RUNBOOK.md](RUNBOOK.md)

2. **理解 API 設計** → [concepts/api-architecture.md](concepts/api-architecture.md)
   - Base URL、區域 endpoint、`me` 關鍵字規則
   - Meeting ID vs UUID、雙重編碼、時間格式

3. **設定認證** → [concepts/authentication-flows.md](concepts/authentication-flows.md)
   - Server-to-Server OAuth（後端自動化）
   - 附 PKCE 的 User OAuth（面向使用者的 app）
   - 交叉參考：[zoom-oauth](../oauth/SKILL.md)

4. **建立你的第一場會議** → [examples/meeting-lifecycle.md](examples/meeting-lifecycle.md)
   - 附 curl 和 Node.js 範例的完整 CRUD
   - Webhook 事件整合

5. **處理 rate limit** → [concepts/rate-limiting-strategy.md](concepts/rate-limiting-strategy.md)
   - 依方案的限制、重試模式、請求排隊

6. **設定 webhook** → [examples/webhook-server.md](examples/webhook-server.md)
   - CRC 驗證、簽章驗證、事件處理

7. **排查問題** → [troubleshooting/common-issues.md](troubleshooting/common-issues.md)
   - Token 更新、分頁陷阱、常見的坑

---

## 文件結構

```
rest-api/
├── SKILL.md                              # Main skill overview + quick start
├── SKILL.md                              # This file - navigation guide
│
├── concepts/                             # Core architectural concepts
│   ├── api-architecture.md              # REST design, URLs, IDs, time formats
│   ├── authentication-flows.md          # OAuth flows (S2S, User, PKCE, Device)
│   └── rate-limiting-strategy.md        # Limits by plan, retry, queuing
│
├── examples/                             # Complete working code
│   ├── meeting-lifecycle.md             # Create→Update→Start→End→Delete
│   ├── user-management.md              # CRUD users, pagination, bulk ops
│   ├── recording-pipeline.md           # Download recordings via webhooks
│   ├── webhook-server.md               # Express.js CRC + signature verification
│   └── graphql-queries.md              # GraphQL queries, mutations, pagination
│
├── troubleshooting/                      # Problem solving
│   ├── common-errors.md                # HTTP codes, Zoom error codes table
│   └── common-issues.md               # Rate limits, tokens, pagination pitfalls
│
└── references/                           # 39 domain-specific reference files
    ├── authentication.md                # Auth methods reference
    ├── meetings.md                      # Meeting endpoints
    ├── users.md                         # User management endpoints
    ├── webinars.md                      # Webinar endpoints
    ├── recordings.md                    # Cloud recording endpoints
    ├── reports.md                       # Reports & analytics
    ├── accounts.md                      # Account management
    ├── rate-limits.md                   # Rate limit details
    ├── graphql.md                       # GraphQL API (beta)
    ├── zoom-team-chat.md                     # Team Chat messaging
    ├── chatbot.md                       # Chatbot integration
    ├── phone.md                         # Zoom Phone
    ├── rooms.md                         # Zoom Rooms
    ├── calendar.md                      # Zoom Calendar
    ├── mail.md                          # Zoom Mail
    ├── ai-companion.md                  # AI features
    ├── openapi.md                       # OpenAPI specs
    ├── qss.md                           # Quality of Service
    ├── contact-center.md                # Contact Center
    ├── events.md                        # Zoom Events
    ├── whiteboard.md                    # Whiteboard
    ├── clips.md                         # Zoom Clips
    ├── scheduler.md                     # Scheduler
    ├── scim2.md                         # SCIM 2.0
    ├── marketplace-apps.md              # App management
    ├── zoom-video-sdk-api.md                 # Video SDK REST
    └── ... (39 total files)
```

---

## 依使用情境

### 我想建立並管理會議
1. [API Architecture](concepts/api-architecture.md) - Base URL、時間格式
2. [Meeting Lifecycle](examples/meeting-lifecycle.md) - 完整 CRUD + webhook 事件
3. [Meetings Reference](references/meetings.md) - 所有 endpoint、類型、設定

### 我想用程式管理使用者
1. [User Management](examples/user-management.md) - CRUD、分頁、批次操作
2. [Users Reference](references/users.md) - Endpoint、使用者類型、scope

### 我想自動下載錄影
1. [Recording Pipeline](examples/recording-pipeline.md) - 由 webhook 觸發的下載
2. [Recordings Reference](references/recordings.md) - 檔案類型、下載認證

### 我想接收即時事件
1. [Webhook Server](examples/webhook-server.md) - CRC 驗證、簽章檢查
2. 交叉參考：完整的 webhook 文件請看 [zoom-webhooks](../webhooks/SKILL.md)
3. 交叉參考：WebSocket 事件請看 [zoom-websockets](../websockets/SKILL.md)

### 我想用 GraphQL 取代 REST
1. [GraphQL Queries](examples/graphql-queries.md) - 查詢、mutation、分頁
2. [GraphQL Reference](references/graphql.md) - 可用的實體、scope、rate limit

### 我想設定認證
1. [Authentication Flows](concepts/authentication-flows.md) - 所有 OAuth 方式
2. 交叉參考：完整的 OAuth 實作請看 [zoom-oauth](../oauth/SKILL.md)

### 我碰到 rate limit
1. [Rate Limiting Strategy](concepts/rate-limiting-strategy.md) - 依方案的限制、策略
2. [Rate Limits Reference](references/rate-limits.md) - 詳細的表格
3. [Common Issues](troubleshooting/common-issues.md) - 實務上的解法

### 我遇到錯誤
1. [Common Errors](troubleshooting/common-errors.md) - 錯誤碼表
2. [Common Issues](troubleshooting/common-issues.md) - 診斷工作流程

### 我想做網路研討會
1. [Webinars Reference](references/webinars.md) - Endpoint、類型、報名者
2. [Meeting Lifecycle](examples/meeting-lifecycle.md) - 適用類似的模式

### 我想整合 Zoom Phone
1. [Phone Reference](references/phone.md) - Phone API endpoint
2. [Rate Limiting Strategy](concepts/rate-limiting-strategy.md) - Phone 有獨立的 rate limit

---

## 最關鍵的文件

### 1. API Architecture（基礎）
**[concepts/api-architecture.md](concepts/api-architecture.md)**

在呼叫任何 API 之前必備的知識：
- Base URL 和區域 endpoint
- `me` 關鍵字的規則（每種 app 類型不一樣！）
- Meeting ID vs UUID 的雙重編碼
- ISO 8601 時間格式（UTC vs 本地）
- 下載 URL 的認證

### 2. Rate Limiting Strategy（正式環境最常見的問題）
**[concepts/rate-limiting-strategy.md](concepts/rate-limiting-strategy.md)**

Rate limit 是依帳號計算、所有 app 共用：
- Free：Light 4/秒、Medium 2/秒、Heavy 1/秒
- Pro：Light 30/秒、Medium 20/秒、Heavy 10/秒
- Business+：Light 80/秒、Medium 60/秒、Heavy 40/秒
- 每位使用者：每天 100 次會議建立／更新

### 3. Meeting Lifecycle（最常見的任務）
**[examples/meeting-lifecycle.md](examples/meeting-lifecycle.md)**

搭配 webhook 整合的完整 CRUD，這是大多數開發者最先需要的模式。

---

## 關鍵心得

### 重要發現：

1. **JWT app 類型已棄用**：改用 Server-to-Server OAuth
   - Marketplace 上棄用的是 JWT *app 類型*，不是 JWT token 簽章
   - 見：[Authentication Flows](concepts/authentication-flows.md)

2. **`me` 關鍵字在不同 app 類型下行為不同**
   - User OAuth：一定要用 `me`
   - S2S OAuth：絕對不能用 `me`
   - 見：[API Architecture](concepts/api-architecture.md)

3. **Rate limit 有細微差別（不要假設只有單一全域規則）**
   - 限制可能依 endpoint 而異，也可能在帳號／app／使用者層級強制執行
   - 把配額當作可能跟你的整個帳號共用，並實作 backoff
   - 監控 rate limit 的回應 header（例如 `X-RateLimit-Remaining`）
   - 見：[Rate Limiting Strategy](concepts/rate-limiting-strategy.md)

4. **每位使用者每天 100 次會議建立**
   - 這是硬性的每位使用者上限，跟 rate limit 無關
   - 批次操作時分散到不同的主辦者使用者
   - 見：[Rate Limiting Strategy](concepts/rate-limiting-strategy.md)

5. **某些 UUID 必須做雙重編碼**
   - 以 `/` 開頭或包含 `//` 的 UUID 必須雙重編碼
   - 見：[API Architecture](concepts/api-architecture.md)

6. **分頁：用 `next_page_token`，不要用 `page_number`**
   - `page_number` 是舊的做法，正在被淘汰
   - `next_page_token` 是建議的做法
   - 見：[Common Issues](troubleshooting/common-issues.md)

7. **GraphQL 在 `/v3/graphql`，不在 `/v2/`**
   - 單一 endpoint，cursor 式分頁
   - Rate limit 依欄位計算（每個欄位相當於一次 REST 呼叫）
   - 見：[GraphQL Queries](examples/graphql-queries.md)

---

## 快速參考

### 「401 Unauthorized」
→ [Authentication Flows](concepts/authentication-flows.md) - Token 過期或 scope 錯誤

### 「429 Too Many Requests」
→ [Rate Limiting Strategy](concepts/rate-limiting-strategy.md) - 看 header 裡的重置時間

### 用 userId 時出現「Invalid token」
→ [API Architecture](concepts/api-architecture.md) - User OAuth app 必須用 `me`

### 「我要怎麼分頁取得結果？」
→ [Common Issues](troubleshooting/common-issues.md) - 用 `next_page_token`

### 「Webhook 沒送到」
→ [Webhook Server](examples/webhook-server.md) - 需要 CRC 驗證

### 「錄影下載失敗」
→ [Recording Pipeline](examples/recording-pipeline.md) - Bearer 認證 + 跟著重新導向

### 「我要怎麼建立會議？」
→ [Meeting Lifecycle](examples/meeting-lifecycle.md) - 完整可運作的範例

---

## 相關 Skill

| Skill | 什麼時候用 |
|-------|----------|
| **[zoom-oauth](../oauth/SKILL.md)** | 實作 OAuth 流程、token 管理 |
| **[zoom-webhooks](../webhooks/SKILL.md)** | 深入的 webhook 實作、事件目錄 |
| **[zoom-websockets](../websockets/SKILL.md)** | WebSocket 事件串流 |
| **[zoom-general](../general/SKILL.md)** | 跨產品的模式、社群 repo |

---

**根據 Zoom REST API v2（現行）和 GraphQL v3（beta）**

## 環境變數

- 標準化的 `.env` key，以及各個值要去哪裡找，請看 [references/environment-variables.md](references/environment-variables.md)。
