---
name: google-chat-messages
description: "透過 incoming webhook 發送 Google Chat 訊息：純文字、rich card（cardsV2）、串接回覆。內含 TypeScript 型別、card builder 工具、widget 參考。只要使用者想從 script 發訊息到 Google Chat、做 chatbot 回覆、發通知卡片、做 Google Chat webhook 整合，或排查卡片 / 串接問題，就用這個 skill。"
compatibility: claude-code-only
---

# Google Chat Messages

透過 incoming webhook 發訊息到 Google Chat 空間。可以產生純文字訊息、rich card（cardsV2）和串接回覆。

## 你會產出什麼

- 套用 Google Chat 格式的文字訊息
- 有標頭、區段、widget 的 rich card 訊息（cardsV2）
- 串接的對話
- 可重複使用的 webhook 發送工具

## 工作流程

### 步驟 1：取得 Webhook URL

在 Google Chat 裡：
1. 打開一個 Space > 點空間名稱 > **Manage webhooks**
2. 建立 webhook（取名字，頭像 URL 可選）
3. 複製 webhook URL

把 URL 存成環境變數或放進 secrets manager，絕對不要寫死在程式碼裡。

### 步驟 2：選擇訊息類型

| 需求 | 類型 | 複雜度 |
|------|------|------------|
| 簡單通知 | 文字訊息 | 低 |
| 結構化資訊（狀態、摘要） | 卡片訊息（cardsV2） | 中 |
| 持續更新 | 串接回覆 | 中 |
| 動作按鈕（開啟 URL） | 帶 buttonList 的卡片 | 中 |

### 步驟 3：發送訊息

發送工具用 `assets/webhook-sender.ts`。結構化卡片的建構用 `assets/card-builder.ts`。

## 文字格式

Google Chat **不是**用標準 Markdown。

| 格式 | 語法 | 範例 |
|--------|--------|---------|
| 粗體 | `*text*` | `*important*` |
| 斜體 | `_text_` | `_emphasis_` |
| 刪除線 | `~text~` | `~removed~` |
| 等寬字 | `` `text` `` | `` `code` `` |
| 程式碼區塊 | ` ```text``` ` | 多行程式碼 |
| 連結 | `<url\|text>` | `<https://example.com\|Click here>` |
| 提及使用者 | `<users/USER_ID>` | `<users/123456>` |
| 提及所有人 | `<users/all>` | `<users/all>` |

**不支援**：`**雙星號**`、標題（`###`）、引用區塊、表格、行內圖片。

### 文字訊息範例

```typescript
await sendText(webhookUrl, '*Build Complete*\n\nBranch: `main`\nStatus: Passed\n<https://ci.example.com/123|View Build>');
```

## cardsV2 結構

卡片使用 cardsV2 格式（建議用它，不要用舊版卡片）。

```typescript
const message = {
  cardsV2: [{
    cardId: 'unique-id',
    card: {
      header: {
        title: 'Card Title',
        subtitle: 'Optional subtitle',
        imageUrl: 'https://example.com/icon.png',
        imageType: 'CIRCLE'  // or 'SQUARE'
      },
      sections: [{
        header: 'Section Title',  // optional
        widgets: [
          // widgets go here
        ]
      }]
    }
  }]
};
```

## Widget 參考

cardsV2 區段裡可用的所有 widget 類型。

### textParagraph

格式化的文字區塊。支援 Google Chat 格式（`*bold*`、`_italic_`、`<url|text>`）。

```typescript
{
  textParagraph: {
    text: '*Status*: All systems operational\n_Last checked_: 5 minutes ago'
  }
}
```

### decoratedText

帶標籤的值，可以加圖示。呈現 key-value 資料時最萬用的 widget。

**基本：**
```typescript
{
  decoratedText: {
    topLabel: 'Environment',
    text: 'Production',
    bottomLabel: 'Last deployed 2h ago'
  }
}
```

**帶起始圖示：**
```typescript
{
  decoratedText: {
    topLabel: 'Status',
    text: 'Healthy',
    startIcon: { knownIcon: 'STAR' }
  }
}
```

**帶自訂圖示 URL：**
```typescript
{
  decoratedText: {
    topLabel: 'GitHub',
    text: 'PR #142 merged',
    startIcon: {
      iconUrl: 'https://github.githubassets.com/favicons/favicon.svg',
      altText: 'GitHub'
    }
  }
}
```

**帶按鈕：**
```typescript
{
  decoratedText: {
    topLabel: 'Alert',
    text: 'CPU at 95%',
    button: {
      text: 'View',
      onClick: { openLink: { url: 'https://monitoring.example.com' } }
    }
  }
}
```

**可點擊（整個 widget）：**
```typescript
{
  decoratedText: {
    text: 'View full report',
    wrapText: true,
    onClick: { openLink: { url: 'https://reports.example.com' } }
  }
}
```

**帶自動換行：**
```typescript
{
  decoratedText: {
    topLabel: 'Description',
    text: 'This is a longer description that should wrap to multiple lines instead of being truncated',
    wrapText: true
  }
}
```

### buttonList

一個或多個動作按鈕。按鈕可以開啟 URL 或觸發動作。

**單一按鈕：**
```typescript
{
  buttonList: {
    buttons: [{
      text: 'Open Dashboard',
      onClick: { openLink: { url: 'https://dashboard.example.com' } }
    }]
  }
}
```

**多個按鈕：**
```typescript
{
  buttonList: {
    buttons: [
      {
        text: 'Approve',
        onClick: { openLink: { url: 'https://app.example.com/approve/123' } },
        color: { red: 0, green: 0.5, blue: 0, alpha: 1 }
      },
      {
        text: 'Reject',
        onClick: { openLink: { url: 'https://app.example.com/reject/123' } }
      }
    ]
  }
}
```

**帶圖示的按鈕：**
```typescript
{
  buttonList: {
    buttons: [{
      text: 'View on GitHub',
      icon: { knownIcon: 'BOOKMARK' },
      onClick: { openLink: { url: 'https://github.com/org/repo/pull/42' } }
    }]
  }
}
```

### image

獨立的圖片 widget。

```typescript
{
  image: {
    imageUrl: 'https://example.com/chart.png',
    altText: 'Monthly usage chart'
  }
}
```

### divider

widget 之間的水平分隔線。

```typescript
{ divider: {} }
```

### 可收合的區段

區段可以收合，只顯示前 N 個 widget：

```typescript
{
  header: 'Details',
  collapsible: true,
  uncollapsibleWidgetsCount: 2,  // Show first 2, collapse rest
  widgets: [
    { decoratedText: { topLabel: 'Status', text: 'Active' } },
    { decoratedText: { topLabel: 'Region', text: 'AU' } },
    // These start collapsed
    { decoratedText: { topLabel: 'Instance', text: 'prod-01' } },
    { decoratedText: { topLabel: 'Memory', text: '2.1 GB' } },
    { decoratedText: { topLabel: 'CPU', text: '45%' } }
  ]
}
```

## 內建圖示

decoratedText 和按鈕 widget 可以透過 `knownIcon` 使用的圖示。

```typescript
{ startIcon: { knownIcon: 'STAR' } }
// or
{ icon: { knownIcon: 'EMAIL' } }
```

| 圖示名稱 | 用途 |
|-----------|---------|
| `AIRPLANE` | 旅行、航班 |
| `BOOKMARK` | 儲存、參考、連結 |
| `BUS` | 交通、大眾運輸 |
| `CAR` | 開車、交通 |
| `CLOCK` | 時間、時長、行程 |
| `CONFIRMATION_NUMBER_ICON` | 票券、訂位 |
| `DESCRIPTION` | 文件、檔案 |
| `DOLLAR` | 金錢、價格、成本 |
| `EMAIL` | Email、訊息 |
| `INVITE` | 邀請 |
| `MAP_PIN` | 位置、地址 |
| `MEMBERSHIP` | 會員、使用者 |
| `MULTIPLE_PEOPLE` | 團隊、群組 |
| `OFFER` | 優惠、促銷 |
| `PERSON` | 單一使用者 |
| `PHONE` | 電話號碼、通話 |
| `SHOPPING_CART` | 電商、購買 |
| `STAR` | 評分、最愛、重要 |
| `STORE` | 商店、零售 |
| `TICKET` | 票券、活動 |
| `VIDEO_CAMERA` | 影片、會議 |

清單裡沒有的圖示，用 `iconUrl` 搭配任何可公開存取的圖片（正方形，最好是 24x24 或 48x48 像素）。

## 串接

用 `threadKey` 把訊息串在一起：

```typescript
// First message — creates thread
const response = await sendCard(webhookUrl, card, {
  threadKey: 'deploy-2026-02-16'
});

// Reply to thread — append &messageReplyOption=REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD
const threadUrl = `${webhookUrl}&messageReplyOption=REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD`;
await sendCard(threadUrl, replyCard, {
  threadKey: 'deploy-2026-02-16'
});
```

`threadKey` 是由 client 自訂的字串。相關訊息要用一致的 key（例如 `deploy-{date}`、`alert-{id}`）。

## 常見模式

### 通知卡片

```typescript
import { buildCard, sendCard } from './assets/card-builder';
import { sendWebhook } from './assets/webhook-sender';

const card = buildCard({
  cardId: 'deploy-notification',
  title: 'Deployment Complete',
  subtitle: 'production - v2.1.0',
  imageUrl: 'https://example.com/your-icon.png',
  sections: [{
    widgets: [
      { decoratedText: { topLabel: 'Environment', text: 'Production' } },
      { decoratedText: { topLabel: 'Version', text: 'v2.1.0' } },
      { decoratedText: { topLabel: 'Status', text: '*Healthy*', startIcon: { knownIcon: 'STAR' } } },
      { buttonList: { buttons: [{ text: 'View Deployment', onClick: { openLink: { url: 'https://dash.example.com' } } }] } }
    ]
  }]
});
```

### 摘要卡片（每週總結）

```typescript
const digest = buildCard({
  cardId: 'weekly-digest',
  title: 'Weekly Summary',
  subtitle: `${count} updates this week`,
  sections: [
    {
      header: 'Highlights',
      widgets: items.map(item => ({
        decoratedText: { text: item.title, bottomLabel: item.date }
      }))
    },
    {
      widgets: [{
        buttonList: {
          buttons: [{ text: 'View All', onClick: { openLink: { url: dashboardUrl } } }]
        }
      }]
    }
  ]
});
```

## 錯誤預防

| 錯誤 | 修法 |
|---------|-----|
| 文字裡用 `**bold**` | 改用 `*bold*`（單星號） |
| `[text](url)` 連結 | 改用 `<url\|text>` 格式 |
| 缺少 `cardsV2` 外層 | 把卡片包在 `{ cardsV2: [{ cardId, card }] }` 裡 |
| 串接回覆沒有串在一起 | 在 webhook URL 後面加 `&messageReplyOption=REPLY_MESSAGE_FALLBACK_TO_NEW_THREAD` |
| Webhook 回 400 | 檢查 JSON 結構，常見問題是最上層缺少 `text` 或 `cardsV2` |
| 卡片沒顯示 | 確認 `sections` 至少有一個 widget |

## 資產檔案

| 檔案 | 用途 |
|------|---------|
| `assets/types.ts` | cardsV2 的 TypeScript 型別定義 |
| `assets/card-builder.ts` | 建構卡片訊息的工具 |
| `assets/webhook-sender.ts` | 帶錯誤處理的 webhook POST |
