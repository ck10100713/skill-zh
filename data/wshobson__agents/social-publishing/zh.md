---
name: social-publishing
description: >
  透過 SocialClaw API，在 13 個平台（X、LinkedIn、Instagram、Facebook Pages、TikTok、Discord、Telegram、YouTube、Reddit、WordPress、Pinterest）上排程並發布社群貼文。在使用者想用程式化的方式發布、排程或管理社群媒體內容時使用。需要 SOCIALCLAW_API_KEY。
license: MIT
metadata:
  version: "1.0.0"
  source: https://github.com/ndesv21/socialclaw
  homepage: https://getsocialclaw.com
---

# Social Publishing

以 agent 為優先的社群媒體發布，透過 [SocialClaw](https://getsocialclaw.com) 進行。一把 workspace API key，13 個平台，不用逐一設定各平台的 OAuth。

## When to Use This Skill

使用者想做以下事情時，使用這個 skill：
- 在多個社群媒體平台發布或排程貼文
- 統籌跨平台的內容活動
- 上傳媒體並附加到社群貼文
- 取得貼文層級的互動分析
- 用程式化的方式管理內容行事曆

## Supported Platforms

| Platform | Notes |
|----------|-------|
| X (Twitter) | 個人貼文、串文 |
| LinkedIn | 個人貼文 + 公司頁面 |
| Instagram | 商業帳號 + 獨立帳號 |
| Facebook Pages | 附連結預覽的粉專貼文 |
| TikTok | 影片說明 |
| Discord | 指定頻道、embed |
| Telegram | 頻道/群組訊息 |
| YouTube | 影片說明和 metadata |
| Reddit | 帶 flair 的 subreddit 貼文 |
| WordPress | 帶 SEO metadata 的部落格文章 |
| Pinterest | 指定 board 的 Pin |

## Setup

```bash
# Install via npx
npx skills add ndesv21/socialclaw

# Or install as package
npm install socialclaw@0.1.12

# Set your workspace API key
export SOCIALCLAW_API_KEY=your_key_here
```

到 [getsocialclaw.com](https://getsocialclaw.com) 取得 workspace API key。

## Workflow

### Step 1: Define Campaign
指定平台、訊息內容、排程，以及任何要附加的媒體。

### Step 2: Draft Platform Variants
Claude 為每個頻道產生針對該平台優化的文案（字數限制、hashtag 慣例、語氣）。

### Step 3: Upload Media (Optional)
圖片或影片上傳一次就好，SocialClaw 會儲存起來，供跨平台重複使用。

### Step 4: Validate Schedule
送出之前，Claude 會檢查各平台專屬的時間規則和 rate limit。

### Step 5: Publish or Schedule
貼文透過 SocialClaw API 排入佇列。會收到 post ID 和排程時間，用來確認。

### Step 6: Analytics
發布 24–48 小時後，拉取互動指標（曝光、點擊、反應）。

## Usage Examples

### Single Platform Post
```
Post to our company LinkedIn page:
"Excited to announce our Q2 product roadmap — here's what's coming next.
[roadmap image]"
```

### Multi-Platform Campaign
```
Announce our beta launch on X, LinkedIn, Instagram, and Discord.
Message: "Our beta is live! 100 spots available — sign up at example.com #launch"
Schedule for tomorrow 9am PST
```

### Content Series
```
Create a 5-day drip campaign for our feature launch week.
Platforms: X and LinkedIn.
I'll provide copy for each day.
```

## Guidelines

1. **一把 key，所有平台** — SOCIALCLAW_API_KEY 可以驗證所有已連結的帳號
2. **平台原生的文案** — 依各平台調整語氣和格式，不要直接複製貼上
3. **驗證時間** — 送出前一定要確認排程，避免 rate limit 錯誤
4. **媒體重複使用** — 資產上傳一次，之後在多篇貼文中用 ID 引用

## Limitations

- 需要有已啟用的 SocialClaw 帳號，並已連結社群帳號
- 平台能不能用，取決於 workspace 的方案等級
- 有些平台需要影片內容才能達到最佳觸及（TikTok、YouTube、Instagram Reels）
