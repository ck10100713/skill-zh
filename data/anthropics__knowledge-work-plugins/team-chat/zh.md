---
name: build-zoom-team-chat-app
description: "Zoom Team Chat 的參考 skill。在導向某個聊天工作流程之後使用，適用於建立以使用者為範圍的訊息整合、chatbot 體驗、rich card、按鈕、slash command 或聊天 webhook。"
triggers:
  - "zoom team chat"
  - "zoom chatbot"
  - "zoom messaging"
  - "team chat api"
  - "chatbot api"
  - "zoom slash commands"
  - "zoom chat integration"
---

# /build-zoom-team-chat-app

Zoom Team Chat 整合的背景參考資料。在工作流程已經明確之後使用，尤其是需要區分 Team Chat API 和 Chatbot API 的時候。

## 先讀這個（很重要）

有兩種不同的整合類型，彼此不能互換：

1. **Team Chat API（使用者類型）**
   - 以真實的已驗證使用者身分發送訊息
   - 使用 **User OAuth**（`authorization_code`）
   - Endpoint 家族：`/v2/chat/users/...`

2. **Chatbot API（bot 類型）**
   - 以你的 bot 身分發送訊息
   - 使用 **Client Credentials**（`client_credentials`）
   - Endpoint 家族：`/v2/im/chat/messages`

如果一開始就選錯類型，驗證、scope 和 endpoint 全部會對不上，實作就會失敗。

**官方文件**：https://developers.zoom.us/docs/team-chat/  
**Chatbot 文件**：https://developers.zoom.us/docs/team-chat/chatbot/extend/  
**API 參考**：https://developers.zoom.us/docs/api/rest/reference/chatbot/

## 快速連結

**剛接觸 Team Chat？照這條路徑走：**

1. **[Get Started](get-started.md)** - 端到端的快速路徑（使用者類型 vs bot 類型）
2. **[Choose Your API](concepts/api-selection.md)** - Team Chat API vs Chatbot API
3. **[Environment Setup](concepts/environment-setup.md)** - 憑證、scope、app 設定
4. **[OAuth Setup](examples/oauth-setup.md)** - 完整的驗證流程
5. **[Send First Message](examples/send-message.md)** - 可以運作的發送訊息程式碼

**參考資料：**
- **[Chatbot Message Cards](references/message-cards.md)** - 完整的 card 元件參考
- **[Webhook Events](references/webhook-events.md)** - 所有 webhook 事件類型
- **[API Reference](references/api-reference.md)** - Endpoint、方法、參數
- **[Sample Applications](references/samples.md)** - 10 個以上的官方範例 app
- **整合索引** - 見本檔案下方的章節

**遇到問題？**
- 驗證錯誤 → [OAuth Troubleshooting](troubleshooting/oauth-issues.md)
- Webhook 沒收到事件 → [Webhook Setup Guide](troubleshooting/webhook-issues.md)
- 訊息發不出去 → [Common Issues](troubleshooting/common-issues.md)
- 先做快速檢查 → [5-Minute Runbook](RUNBOOK.md)

**OAuth endpoint 健全性檢查：**
- Authorize URL：`https://zoom.us/oauth/authorize`
- Token URL：`https://zoom.us/oauth/token`
- 如果 `/oauth/token` 回傳 404/HTML，就用 `https://zoom.us/oauth/token`。

**要建立互動式 bot？**
- [Button Actions](examples/button-actions.md) - 處理按鈕點擊
- [Form Submissions](examples/form-submissions.md) - 處理表單資料
- [Slash Commands](examples/slash-commands.md) - 建立自訂指令

## 快速決定：該用哪個 API？

| 使用情境 | 該用的 API |
|----------|------------|
| 從腳本/CI/CD 發送通知 | **Team Chat API** |
| 以使用者身分自動發送訊息 | **Team Chat API** |
| 建立互動式 chatbot | **Chatbot API** |
| 回應 slash command | **Chatbot API** |
| 建立有按鈕/表單的訊息 | **Chatbot API** |
| 處理使用者互動 | **Chatbot API** |

### Team Chat API（使用者層級）
- 訊息看起來是由**已驗證的使用者**發送的
- 需要 **User OAuth**（authorization_code 流程）
- Endpoint：`POST https://api.zoom.us/v2/chat/users/me/messages`
- Scope：`chat_message:write`、`chat_channel:read`

### Chatbot API（bot 層級）
- 訊息看起來是由你的 **bot** 發送的
- 需要 **Client Credentials** grant
- Endpoint：`POST https://api.zoom.us/v2/im/chat/messages`
- Scope：`imchat:bot`（自動加入）
- **Rich card**：按鈕、表單、下拉選單、圖片

## 前置條件

### 系統需求

- Zoom 帳號
- 帳號擁有者、管理員，或已啟用 **Zoom for developers** 角色
  - 啟用方式：**User Management** → **Roles** → **Role Settings** → **Advanced features** → 啟用 **Zoom for developers**

### 建立 Zoom App

1. 前往 [Zoom App Marketplace](https://marketplace.zoom.us/)
2. 點 **Develop** → **Build App**
3. 選擇 **General App**（OAuth）

> ⚠️ **不要用 Server-to-Server OAuth**：S2S app 沒有 Chatbot/Team Chat 功能。只有 General App（OAuth）支援 chatbot。

### 必要的憑證

從 Zoom Marketplace → 你的 App：

| 憑證 | 位置 | 使用於 |
|------------|----------|---------|
| Client ID | App Credentials → Development | 兩種 API |
| Client Secret | App Credentials → Development | 兩種 API |
| Account ID | App Credentials → Development | Chatbot API |
| Bot JID | Features → Chatbot → Bot Credentials | Chatbot API |
| Secret Token | Features → Team Chat Subscriptions | Chatbot API |

**參閱**：[Environment Setup Guide](concepts/environment-setup.md) 取得完整的設定步驟。

## 快速開始：Team Chat API

以使用者身分發送訊息：

```javascript
// 1. 透過 OAuth 取得 access token
const accessToken = await getOAuthToken(); // 見 examples/oauth-setup.md

// 2. 發送訊息到頻道
const response = await fetch('https://api.zoom.us/v2/chat/users/me/messages', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: 'Hello from CI/CD pipeline!',
    to_channel: 'CHANNEL_ID'
  })
});

const data = await response.json();
// { "id": "msg_abc123", "date_time": "2024-01-15T10:30:00Z" }
```

**完整範例**：[Send Message Guide](examples/send-message.md)

## 快速開始：Chatbot API

建立互動式 chatbot：

```javascript
// 1. 取得 chatbot token（client_credentials）
async function getChatbotToken() {
  const credentials = Buffer.from(
    `${CLIENT_ID}:${CLIENT_SECRET}`
  ).toString('base64');
  
  const response = await fetch('https://zoom.us/oauth/token', {
    method: 'POST',
    headers: {
      'Authorization': `Basic ${credentials}`,
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: 'grant_type=client_credentials'
  });
  
  return (await response.json()).access_token;
}

// 2. 發送帶有按鈕的 chatbot 訊息
const response = await fetch('https://api.zoom.us/v2/im/chat/messages', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    robot_jid: process.env.ZOOM_BOT_JID,
    to_jid: payload.toJid,           // 來自 webhook
    account_id: payload.accountId,   // 來自 webhook
    content: {
      head: {
        text: 'Build Notification',
        sub_head: { text: 'CI/CD Pipeline' }
      },
      body: [
        { type: 'message', text: 'Deployment successful!' },
        {
          type: 'fields',
          items: [
            { key: 'Branch', value: 'main' },
            { key: 'Commit', value: 'abc123' }
          ]
        },
        {
          type: 'actions',
          items: [
            { text: 'View Logs', value: 'view_logs', style: 'Primary' },
            { text: 'Dismiss', value: 'dismiss', style: 'Default' }
          ]
        }
      ]
    }
  })
});
```

**完整範例**：[Chatbot Setup Guide](examples/chatbot-setup.md)

## 主要功能

### Team Chat API

| 功能 | 說明 |
|---------|-------------|
| **Send Messages** | 把訊息發到頻道或私訊 |
| **List Channels** | 取得使用者的頻道及其 metadata |
| **Create Channels** | 以程式建立公開/私人頻道 |
| **Threaded Replies** | 在討論串中回覆特定訊息 |
| **Edit/Delete** | 修改或刪除訊息 |

### Chatbot API

| 功能 | 說明 |
|---------|-------------|
| **Rich Message Cards** | 標頭、圖片、欄位、按鈕、表單 |
| **Slash Commands** | 自訂的 `/commands` 觸發 webhook |
| **Button Actions** | 帶有 webhook callback 的互動式按鈕 |
| **Form Submissions** | 用表單收集使用者輸入 |
| **Dropdown Selects** | 頻道、成員、日期/時間選擇器 |
| **LLM Integration** | 輕鬆整合 Claude、GPT 等 |

## Webhook 事件（Chatbot API）

| 事件 | 觸發時機 | 使用情境 |
|-------|---------|----------|
| `bot_notification` | 使用者傳訊息給 bot 或使用 slash command | 處理指令、整合 LLM |
| `bot_installed` | Bot 被加到帳號 | 初始化 bot 狀態 |
| `interactive_message_actions` | 按鈕被點擊 | 處理按鈕動作 |
| `chat_message.submit` | 表單被提交 | 處理表單資料 |
| `app_deauthorized` | Bot 被移除 | 清理 |

**參閱**：[Webhook Events Reference](references/webhook-events.md)

## Message Card 元件

用這些元件建立豐富的互動式訊息：

| 元件 | 說明 |
|-----------|-------------|
| **header** | 標題與副標題 |
| **message** | 純文字 |
| **fields** | 鍵值對 |
| **actions** | 按鈕（Primary、Danger、Default 樣式） |
| **section** | 有顏色側邊條的分組 |
| **attachments** | 帶連結的圖片 |
| **divider** | 水平線 |
| **form_field** | 文字輸入 |
| **dropdown** | 選單 |
| **date_picker** | 日期選擇 |

**參閱**：[Message Cards Reference](references/message-cards.md) 取得完整的元件目錄

## 架構模式

### Chatbot 生命週期

```
User types /command → Webhook receives bot_notification
                            ↓
                     payload.cmd = "user's input"
                            ↓
                     Process command
                            ↓
                     Send response via sendChatbotMessage()
```

### LLM 整合模式

```javascript
case 'bot_notification': {
  const { toJid, cmd, accountId } = payload;
  
  // 1. 呼叫你的 LLM
  const llmResponse = await callClaude(cmd);
  
  // 2. 把回應送回去
  await sendChatbotMessage(toJid, accountId, {
    body: [{ type: 'message', text: llmResponse }]
  });
}
```

**參閱**：[LLM Integration Guide](examples/llm-integration.md)

## 範例應用程式

| 範例 | 說明 | 連結 |
|--------|-------------|------|
| **Chatbot Quickstart** | 官方教學（建議從這裡開始） | [GitHub](https://github.com/zoom/chatbot-nodejs-quickstart) |
| **Claude Chatbot** | 使用 Anthropic Claude 的 AI chatbot | [GitHub](https://github.com/zoom/zoom-chatbot-claude-sample) |
| **Unsplash Chatbot** | 帶資料庫的圖片搜尋 | [GitHub](https://github.com/zoom/unsplash-chatbot) |
| **ERP Chatbot** | 有排程警示的 Oracle ERP | [GitHub](https://github.com/zoom/zoom-erp-chatbot-sample) |
| **Task Manager** | 完整的 CRUD app | [GitHub](https://github.com/zoom/task-manager-sample) |

**參閱**：[Sample Applications Guide](references/samples.md) 取得全部 10 個範例的分析

## 常見操作

### 發送訊息到頻道

```javascript
// Team Chat API
await fetch('https://api.zoom.us/v2/chat/users/me/messages', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: JSON.stringify({
    message: 'Hello!',
    to_channel: 'CHANNEL_ID'
  })
});
```

### 處理按鈕點擊

```javascript
// Webhook handler
case 'interactive_message_actions': {
  const { actionItem, toJid, accountId } = payload;
  
  if (actionItem.value === 'approve') {
    await sendChatbotMessage(toJid, accountId, {
      body: [{ type: 'message', text: '✅ Approved!' }]
    });
  }
}
```

### 驗證 Webhook 簽章

```javascript
function verifyWebhook(req) {
  const message = `v0:${req.headers['x-zm-request-timestamp']}:${JSON.stringify(req.body)}`;
  const hash = crypto.createHmac('sha256', process.env.ZOOM_VERIFICATION_TOKEN)
    .update(message)
    .digest('hex');
  return req.headers['x-zm-signature'] === `v0=${hash}`;
}
```

## 部署

### 本機開發用 ngrok

```bash
# 安裝 ngrok
npm install -g ngrok

# 把本機伺服器公開出去
ngrok http 4000

# 在 Zoom Marketplace 中，把 HTTPS URL 當成 Bot Endpoint URL
# 例如：https://abc123.ngrok.io/webhook
```

### 正式環境部署

**參閱**：[Deployment Guide](concepts/deployment.md)，內容包含：
- Nginx 反向代理設定
- Base path 設定
- OAuth redirect URI 設定

## 限制

| 限制 | 數值 |
|-------|-------|
| 訊息長度 | 4,096 個字元 |
| 檔案大小 | 512 MB |
| 每個頻道的成員數 | 10,000 |
| 每位使用者的頻道數 | 500 |

## 安全最佳實務

1. **驗證 webhook 簽章**：一律用 `x-zm-signature` header 來驗證
2. **清理訊息**：限制在 4096 個字元以內，移除控制字元
3. **驗證 JID**：檢查格式：`user@domain` 或 `channel@domain`
4. **環境變數**：絕對不要把憑證寫死在程式碼裡
5. **使用 HTTPS**：正式環境的 webhook 必須使用

**參閱**：[Security Best Practices](concepts/security.md)

## 完整文件庫

### 核心概念（從這裡開始！）
- **[API Selection Guide](concepts/api-selection.md)** - 選擇 Team Chat API 或 Chatbot API
- **[Environment Setup](concepts/environment-setup.md)** - 完整的憑證指南
- **[Authentication Flows](concepts/authentication.md)** - OAuth vs Client Credentials
- **[Webhook Architecture](concepts/webhooks.md)** - Webhook 如何運作
- **[Message Card Structure](concepts/message-structure.md)** - Card 元件的階層

### 完整範例
- **[OAuth Setup](examples/oauth-setup.md)** - 完整的 OAuth 實作
- **[Send Message](examples/send-message.md)** - Team Chat API 發送訊息
- **[Chatbot Setup](examples/chatbot-setup.md)** - 含 webhook 的完整 chatbot
- **[Button Actions](examples/button-actions.md)** - 處理互動式按鈕
- **[Form Submissions](examples/form-submissions.md)** - 處理表單資料
- **[Slash Commands](examples/slash-commands.md)** - 建立自訂指令
- **[LLM Integration](examples/llm-integration.md)** - Claude/GPT 整合
- **[Scheduled Alerts](examples/scheduled-alerts.md)** - Cron + incoming webhook
- **[Channel Management](examples/channel-management.md)** - 建立/管理頻道

### 參考資料
- **[API Reference](references/api-reference.md)** - 所有 endpoint 與方法
- **[Webhook Events](references/webhook-events.md)** - 完整的事件參考
- **[Message Cards](references/message-cards.md)** - 所有 card 元件
- **[Sample Applications](references/samples.md)** - 10 個官方範例的分析
- **[Error Codes](references/error-codes.md)** - 錯誤處理指南

### 疑難排解
- **[OAuth Issues](troubleshooting/oauth-issues.md)** - 驗證失敗
- **[Webhook Issues](troubleshooting/webhook-issues.md)** - Webhook 除錯
- **[Common Issues](troubleshooting/common-issues.md)** - 快速診斷

## 資源

- **官方文件**：https://developers.zoom.us/docs/team-chat/
- **API 參考**：https://developers.zoom.us/docs/api/rest/reference/chatbot/
- **開發者論壇**：https://devforum.zoom.us/
- **App Marketplace**：https://marketplace.zoom.us/

---

**需要協助？** 從下方的整合索引章節開始，取得完整的導覽。

---

## 整合索引

_這個章節是從 `SKILL.md` 遷移過來的。_

Zoom Team Chat skill 的完整導覽指南。

## 快速開始路徑

- 從這裡開始：[Get Started](get-started.md)
- 先做快速疑難排解：[5-Minute Runbook](RUNBOOK.md)

### 路徑 1：Team Chat API（使用者層級的訊息）

用於以使用者帳號發送訊息。

1. [API Selection Guide](concepts/api-selection.md) - 確認 Team Chat API 是正確的選擇
2. [Environment Setup](concepts/environment-setup.md) - 取得憑證
3. [OAuth Setup Example](examples/oauth-setup.md) - 實作驗證
4. [Send Message Example](examples/send-message.md) - 發送你的第一則訊息

### 路徑 2：Chatbot API（互動式 bot）

用於建立有豐富訊息的互動式 chatbot。

1. [API Selection Guide](concepts/api-selection.md) - 確認 Chatbot API 是正確的選擇
2. [Environment Setup](concepts/environment-setup.md) - 取得憑證（包含 Bot JID）
3. [Webhook Architecture](concepts/webhooks.md) - 了解 webhook 事件
4. [Chatbot Setup Example](examples/chatbot-setup.md) - 建立你的第一個 bot
5. [Message Cards Reference](references/message-cards.md) - 建立豐富的訊息

## 核心概念

兩種 API 都必須了解的重點。

| 文件 | 說明 |
|----------|-------------|
| [API Selection Guide](concepts/api-selection.md) | 選擇 Team Chat API 或 Chatbot API |
| [Environment Setup](concepts/environment-setup.md) | 完整的憑證與 app 設定 |
| [Authentication Flows](concepts/authentication.md) | OAuth vs Client Credentials |
| [Webhook Architecture](concepts/webhooks.md) | Webhook 如何運作（Chatbot API） |
| [Message Card Structure](concepts/message-structure.md) | Card 元件的階層 |
| [Deployment Guide](concepts/deployment.md) | 正式環境的部署策略 |
| [Security Best Practices](concepts/security.md) | 保護你的整合 |

## 完整範例

常見情境的可運作程式碼。

### 驗證
| 範例 | 說明 |
|---------|-------------|
| [OAuth Setup](examples/oauth-setup.md) | User OAuth 流程實作 |
| [Token Management](examples/token-management.md) | Refresh token、過期處理 |

### 基本操作
| 範例 | 說明 |
|---------|-------------|
| [Send Message](examples/send-message.md) | Team Chat API 發送訊息 |
| [Chatbot Setup](examples/chatbot-setup.md) | 含 webhook 的完整 chatbot |
| [List Channels](examples/channel-management.md) | 取得使用者的頻道 |
| [Create Channel](examples/channel-management.md) | 建立公開/私人頻道 |

### 互動功能（Chatbot API）
| 範例 | 說明 |
|---------|-------------|
| [Button Actions](examples/button-actions.md) | 處理按鈕點擊 |
| [Form Submissions](examples/form-submissions.md) | 處理表單資料 |
| [Slash Commands](examples/slash-commands.md) | 建立自訂指令 |
| [Dropdown Selects](examples/dropdown-selects.md) | 頻道/成員選擇器 |

### 進階整合
| 範例 | 說明 |
|---------|-------------|
| [LLM Integration](examples/llm-integration.md) | 整合 Claude/GPT |
| [Scheduled Alerts](examples/scheduled-alerts.md) | Cron + incoming webhook |
| [Database Integration](examples/database-integration.md) | 儲存對話狀態 |
| [Multi-Step Workflows](examples/multi-step-workflows.md) | 複雜的使用者互動 |

## 參考資料

### API 文件
| 參考資料 | 說明 |
|-----------|-------------|
| [API Reference](references/api-reference.md) | 指引與常見的 endpoint |
| [Webhook Events](references/webhook-events.md) | 事件類型與處理檢查清單 |
| [Message Cards](references/message-cards.md) | 所有 card 元件 |
| [Error Codes](references/error-codes.md) | 錯誤處理指南 |

### 範例應用程式
| 參考資料 | 說明 |
|-----------|-------------|
| [Sample Applications](references/samples.md) | 範例 app 的索引與備註 |

### 實用指南
| 參考資料 | 說明 |
|-----------|-------------|
| [JID Formats](references/jid-formats.md) | 了解 JID 識別碼 |
| [Scopes Reference](references/scopes.md) | 常見的 scope |
| [Rate Limits](references/rate-limits.md) | 節流指引 |

## 疑難排解

| 指南 | 說明 |
|-------|-------------|
| [Common Issues](troubleshooting/common-issues.md) | 快速診斷與解法 |
| [OAuth Issues](troubleshooting/oauth-issues.md) | 驗證失敗 |
| [Webhook Issues](troubleshooting/webhook-issues.md) | Webhook 除錯 |
| [Message Issues](troubleshooting/message-issues.md) | 訊息發送問題 |
| [Deployment Issues](troubleshooting/deployment-issues.md) | 正式環境的問題 |

## 架構模式

### Chatbot 生命週期

```
User Action → Webhook → Process → Response
```

### LLM 整合模式

```
User Input → Chatbot receives → Call LLM → Send response
```

### 核准流程模式

```
Request → Send card with buttons → User clicks → Update status → Notify
```

## 常見使用情境

### 通知
- CI/CD 建置通知
- 伺服器監控警示
- 排程報表
- 系統健康檢查

### 工作流程
- 核准請求
- 任務指派
- 狀態更新
- 表單提交

### 整合
- LLM 驅動的助理
- 資料庫查詢
- 外部 API 整合
- 檔案/圖片分享

### 自動化
- 排程訊息
- 自動回覆
- 資料蒐集
- 報表產生

## 資源連結

### 官方文件
- **[Team Chat Docs](https://developers.zoom.us/docs/team-chat/)** - 官方概覽
- **[Chatbot Docs](https://developers.zoom.us/docs/team-chat/chatbot/extend/)** - Chatbot 指南
- **[API Reference](https://developers.zoom.us/docs/api/rest/reference/chatbot/)** - REST API 文件
- **[App Marketplace](https://marketplace.zoom.us/)** - 建立與管理 app

### 範例程式碼
- **[Chatbot Quickstart](https://github.com/zoom/chatbot-nodejs-quickstart)** - 官方教學
- **[Claude Chatbot](https://github.com/zoom/zoom-chatbot-claude-sample)** - AI 整合
- **[Unsplash Chatbot](https://github.com/zoom/unsplash-chatbot)** - 圖片搜尋 bot
- **[ERP Chatbot](https://github.com/zoom/zoom-erp-chatbot-sample)** - 企業整合
- **[Task Manager](https://github.com/zoom/task-manager-sample)** - 完整的 CRUD app

### 工具
- **[App Card Builder](https://appssdk.zoom.us/cardbuilder/)** - 視覺化的 card 設計工具
- **[ngrok](https://ngrok.com/)** - 本機 webhook 測試
- **[Postman](https://www.postman.com/)** - API 測試

### 社群
- **[Developer Forum](https://devforum.zoom.us/)** - 提問
- **[GitHub Discussions](https://github.com/zoom)** - 社群支援
- **[Developer Support](https://devsupport.zoom.us)** - 官方支援

## 文件狀態

### ✅ 已完成
- 主要的 skill.md 進入點
- API Selection Guide
- Environment Setup
- Webhook Architecture
- Chatbot Setup Example（完整的可運作程式碼）
- Message Cards Reference
- Common Issues 疑難排解

### 📝 待處理（高優先）
- OAuth Setup Example
- Send Message Example
- Button Actions Example
- LLM Integration Example
- Webhook Events Reference
- API Reference
- Sample Applications Analysis

### 📋 規劃中（較低優先）
- Form Submissions Example
- Channel Management Examples
- Database Integration Example
- Error Codes Reference
- Rate Limits Guide
- Deployment troubleshooting

## 開始使用檢查清單

### Team Chat API

- [ ] 閱讀 [API Selection Guide](concepts/api-selection.md)
- [ ] 完成 [Environment Setup](concepts/environment-setup.md)
- [ ] 取得 Client ID、Client Secret
- [ ] 加入必要的 scope
- [ ] 實作 OAuth 流程
- [ ] 發送第一則訊息

### Chatbot API

- [ ] 閱讀 [API Selection Guide](concepts/api-selection.md)
- [ ] 完成 [Environment Setup](concepts/environment-setup.md)
- [ ] 取得 Client ID、Client Secret、Bot JID、Secret Token、Account ID
- [ ] 在 Features 中啟用 Team Chat
- [ ] 設定 Bot Endpoint URL 和 Slash Command
- [ ] 設定 ngrok 做本機測試
- [ ] 實作 webhook handler
- [ ] 發送第一則 chatbot 訊息

## 版本歷史

- **v1.0**（2026-02-09）- 初版完整文件
  - 核心概念（API 選擇、環境設定、webhook）
  - 完整的 chatbot 設定範例
  - Message cards 參考
  - Common issues 疑難排解

## 支援

把這份 SKILL.md 當作導覽中心，用來選擇 Team Chat API、設定、查看範例和疑難排解。

## 環境變數

- 標準化的 `.env` key，以及每個值要去哪裡找，見 [references/environment-variables.md](references/environment-variables.md)。
