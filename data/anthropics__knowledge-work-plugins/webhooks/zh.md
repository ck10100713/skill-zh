---
name: setup-zoom-webhooks
description: Zoom webhook 的參考 skill。導向事件驅動的工作流程之後，在實作訂閱、簽章驗證、遞送處理、重試或事件類型選擇時使用。
triggers:
  - "zoom webhook"
  - "webhook signature"
  - "x-zm-signature"
  - "event subscription"
  - "recording completed webhook"
---

# /setup-zoom-webhooks

透過 HTTP 遞送 Zoom 事件的背景參考。優先用工作流程 skill，再用這個檔案查驗證、訂閱和遞送的細節。

## 先決條件

- 啟用了 Event Subscriptions 的 Zoom app
- 接收 webhook 的 HTTPS endpoint
- 用於驗證的 webhook secret token

> **需要驗證方面的協助？** OAuth 設定請看 **[zoom-oauth](../oauth/SKILL.md)** skill。

## Quick Start

```javascript
// Express.js webhook handler
const crypto = require('crypto');

// 擷取原始 body 供簽章驗證用（避免重新序列化 JSON）。
app.use(require('express').json({
  verify: (req, _res, buf) => { req.rawBody = buf; }
}));

app.post('/webhook', (req, res) => {
  // 驗證 webhook 簽章
  const signature = req.headers['x-zm-signature'];
  const timestamp = req.headers['x-zm-request-timestamp'];
  const body = req.rawBody ? req.rawBody.toString('utf8') : JSON.stringify(req.body);
  const payload = `v0:${timestamp}:${body}`;
  const hash = crypto.createHmac('sha256', WEBHOOK_SECRET)
    .update(payload).digest('hex');
  
  if (signature !== `v0=${hash}`) {
    return res.status(401).send('Invalid signature');
  }

  // 處理事件
  const { event, payload } = req.body;
  console.log(`Received: ${event}`);
  
  res.status(200).send();
});
```

## 常見事件

| 事件 | 說明 |
|-------|-------------|
| `meeting.started` | 會議已開始 |
| `meeting.ended` | 會議已結束 |
| `meeting.participant_joined` | 參與者加入會議 |
| `recording.completed` | 雲端錄影已就緒 |
| `user.created` | 新增使用者 |

## 詳細參考

- **[references/events.md](references/events.md)** - 完整的事件類型參考
- **[references/verification.md](references/verification.md)** - Webhook URL 驗證
- **[references/subscriptions.md](references/subscriptions.md)** - 事件訂閱 API

## 疑難排解

- **[RUNBOOK.md](RUNBOOK.md)** - 深入除錯之前的 5 分鐘 preflight 檢查
- **[troubleshooting/common-issues.md](troubleshooting/common-issues.md)** - 簽章驗證、重試、URL 驗證

## 範例 Repo

### 官方（Zoom 出品）

| 類型 | Repository | Stars |
|------|------------|-------|
| Node.js | [webhook-sample](https://github.com/zoom/webhook-sample) | 34 |
| PostgreSQL | [webhook-to-postgres](https://github.com/zoom/webhook-to-postgres) | 5 |
| Go/Fiber | [Go-Webhooks](https://github.com/zoom/Go-Webhooks) | - |
| Header Auth | [zoom-webhook-verification-headers](https://github.com/zoom/zoom-webhook-verification-headers) | - |

### 社群

| 語言 | Repository | 說明 |
|----------|------------|-------------|
| Laravel | [binary-cats/laravel-webhooks](https://github.com/binary-cats/laravel-webhooks) | Laravel webhook handler |
| AWS Lambda | [splunk/zoom-webhook-to-hec](https://github.com/splunk/zoom-webhook-to-hec) | 送到 Splunk HEC 的 serverless |
| Node.js | [Will4950/zoom-webhook-listener](https://github.com/Will4950/zoom-webhook-listener) | Webhook 轉發器 |
| Express+Redis | [ojusave/eventSubscriptionPlayground](https://github.com/ojusave/eventSubscriptionPlayground) | Socket.io + Redis |

### 多語言範例（作者 tanchunsiong）

| 語言 | Repository |
|----------|------------|
| Node.js | [Zoom-Webhook-Signature-OAuth-and-REST-API-Development-Sample-In-NodeJS](https://github.com/tanchunsiong/Zoom-Webhook-Signature-OAuth-and-REST-API-Development-Sample-In-NodeJS) |
| C# | [Zoom-Webhook-Signature-OAuth-and-REST-API-Development-Sample-In-ASP.NET-Core-C-](https://github.com/tanchunsiong/Zoom-Webhook-Signature-OAuth-and-REST-API-Development-Sample-In-ASP.NET-Core-C-) |
| Java | [Zoom-Webhook-Signature-OAuth-and-REST-API-Development-Sample-In-Java-Spring-Boot](https://github.com/tanchunsiong/Zoom-Webhook-Signature-OAuth-and-REST-API-Development-Sample-In-Java-Spring-Boot) |
| Python | [Zoom-Webhook-Signature-OAuth-and-REST-API-Development-Sample-In-Python](https://github.com/tanchunsiong/Zoom-Webhook-Signature-OAuth-and-REST-API-Development-Sample-In-Python) |
| PHP | [Zoom-Webhook-Signature-OAuth-and-REST-API-Development-Sample-In-PHP](https://github.com/tanchunsiong/Zoom-Webhook-Signature-OAuth-and-REST-API-Development-Sample-In-PHP) |

**完整清單**：見 [general/references/community-repos.md](../general/references/community-repos.md)

## 資源

- **Webhook 文件**：https://developers.zoom.us/docs/api/webhooks/
- **事件參考**：https://developers.zoom.us/docs/api/rest/reference/zoom-api/events/
- **開發者論壇**：https://devforum.zoom.us/

## 環境變數

- 標準化的 `.env` key，以及每個值要去哪裡找，請看 [references/environment-variables.md](references/environment-variables.md)。
