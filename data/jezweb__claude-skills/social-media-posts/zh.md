---
name: social-media-posts
description: "為 LinkedIn、Facebook、Instagram 和 Reddit 產生各平台專屬的社群貼文。處理各平台的字數上限、hashtag 策略、hook 位置和圖片規格。可以從零開始寫、從既有內容（部落格、電子報、公告）改寫，或做成多平台的 campaign。產出可以直接複製貼上的貼文。觸發詞：'social media post'、'linkedin post'、'facebook post'、'instagram caption'、'reddit post'、'social posts'、'post to social'、'repurpose for social'、'social media campaign'。"
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
---

# Social Media Post Generator

產生符合各平台慣例、字數上限和受眾期待的專屬社群貼文。產出可以直接複製貼上的內容。

## 模式

### 從零開始
使用者提供主題 + 重點。為選定的平台產生貼文。

### 從既有內容
使用者提供既有內容（部落格文章、電子報、公告、新聞稿）。改寫成適合各平台的貼文。

### Campaign
為單一的產品發布、公告或活動，產生一組跨所有平台、互相配合的貼文。包含發文順序和時間建議。

## 工作流程

### 1. 收集輸入

| 欄位 | 必填 | 範例 |
|-------|----------|---------|
| 主題或原始內容 | 是 | "We just launched a new feature" 或部落格文章的路徑 |
| 目標平台 | 是 | LinkedIn、Facebook、Instagram、Reddit |
| 語氣 | 否 | 專業、輕鬆、熱情、教學 |
| CTA | 否 | "Try it free"、"Read more"、"Comment your thoughts" |
| 要附的連結 | 否 | https://example.com/blog/new-feature |
| 有圖片嗎？ | 否 | 有/沒有，會影響貼文結構 |

如果使用者給的是既有內容的檔案路徑或網址，先讀過，擷取關鍵訊息。

### 2. 產生各平台貼文

---

#### LinkedIn

**受眾**：專業人士、B2B、業界同行
**語氣**：有權威但親切，思想領導型
**最佳長度**：1,200–1,500 字元（長一點的貼文表現比較好）

**結構**：
```
[Hook line — must grab attention before "see more" truncation]
[blank line]
[2-3 short paragraphs with line breaks between]
[blank line]
[CTA or question to drive comments]
[blank line]
[3-5 relevant hashtags]
```

**規則**：
- Hook 要在前 2 行就有效（在約 210 字元處的 "…see more" 之前）
- 多換行，一大坨文字會殺掉互動
- 結尾丟一個問題，帶動留言
- Hashtag：最多 3-5 個，混合廣泛的（#Marketing）和細分的（#CloudflareWorkers）
- 連結放留言區比放貼文內文表現好（演算法會扣分）
- 不要塞滿 emoji，最多 1-2 個，嚴肅話題就不要用

**圖片規格**：連結預覽用 1200×627px (1.91:1)，單獨貼圖用 1080×1080 (1:1)

**範例**：
```
We just shipped something we've been building for 6 months.

It started as a "wouldn't it be nice if…" conversation and turned
into our most requested feature. Here's what we learned:

→ Users don't want more features. They want fewer clicks.
→ The prototype we almost killed became the final product.
→ Shipping weekly forced us to cut scope ruthlessly.

The full story is in our latest blog post (link in comments).

What's the hardest product decision you've made this year?

#ProductDevelopment #StartupLife #BuildInPublic
```

---

#### Facebook

**受眾**：混合型，朋友、家人、社群、在地商家
**語氣**：對話式、溫暖、以社群為主
**最佳長度**：要拚互動就 80–150 字元，說故事可以到 500

**結構**：
```
[Opening hook — conversational, relatable]
[1-2 short paragraphs]
[Link (if applicable) — Facebook generates preview cards]
[Engagement prompt — question or poll]
```

**規則**：
- 連結貼文：Facebook 會自動產生預覽卡片，不要在文字裡重複標題
- 短貼文（130 字元以內）在動態消息裡會用比較大的字體顯示
- 問題和投票帶來的互動最高
- 提到合作夥伴/客戶時，標記相關粉絲專頁
- Hashtag：1-3 個或不用，Facebook 的 hashtag 效果比其他平台差
- Emoji 可以用，但別過頭（最多 2-3 個）

**圖片規格**：連結預覽用 1200×630px (1.91:1)，照片貼文用 1080×1080 (1:1)

**範例**：
```
6 months ago we started building something our users kept asking for.
Today it's live. 🚀

We wrote up the full story — the pivots, the almost-killed prototype,
and why "fewer clicks" won over "more features."

[link]

What feature have you shipped that surprised you?
```

---

#### Instagram

**受眾**：視覺優先、較年輕的族群、生活風格/品牌導向
**語氣**：真誠、視覺化說故事、突顯個性
**最佳長度**：關鍵訊息放在前 125 字元（截斷點），完整 caption 最多 2,200

**結構**：
```
[First line — must work as standalone (before "…more")]
[blank line]
[Story or detail — 2-4 short paragraphs]
[blank line]
[CTA — save, share, comment, link in bio]
.
.
.
[Hashtags — in first comment OR separated by dots]
```

**規則**：
- 前 125 字元要能傳達訊息（後面的都被藏在 "…more" 後面）
- Caption 裡的連結不能點，導向 "link in bio"
- Hashtag：20-30 個放在第一則留言（不要放 caption），增加被發現的機會
- 混合不同量級的 hashtag：5 個大的（100 萬篇以上）、10 個中的（10 萬到 100 萬）、10 個細分的（10 萬以下）
- Emoji 是語言的一部分，自然地用
- 輪播貼文：加上滑動 CTA（"Swipe for the full breakdown →"）
- 限時動態：引導互動（"Reply with 🔥 if you relate"）

**圖片規格**：動態用 1080×1080 (1:1)，直式用 1080×1350 (4:5)，限時動態/reels 用 1080×1920 (9:16)

**範例**：
```
We shipped our most requested feature today. Here's the story 👇

Six months ago, someone on our team said "wouldn't it be nice
if users could do this in one click instead of five?"

We almost killed the prototype twice. But our users kept asking
for it. So we shipped it.

The biggest lesson? Your users don't want more features.
They want fewer clicks.

Full story → link in bio

💬 What's one feature you wish was simpler in your favourite app?
```

**第一則留言**：
```
#ProductLaunch #StartupLife #BuildInPublic #TechStartup
#ProductDevelopment #UXDesign #SaaS #FeatureLaunch
[... 20-30 total hashtags]
```

---

#### Reddit

**受眾**：各社群有自己的調性，重視真誠，對行銷過敏
**語氣**：真誠、價值優先、對話式，絕對不要推銷感
**最佳長度**：標題 100-150 字元，內文依 subreddit 而定

**結構**：
```
Title: [Descriptive, value-focused — NOT clickbait]

Body:
[Context — why this matters to this community]
[The substance — what you learned, built, or discovered]
[Optional: link to more detail]
[Discussion prompt — genuine question]
```

**規則**：
- **標題就是一切**，Reddit 生死都看標題
- 不能有自我宣傳的感覺，先給價值，不要先講產品
- 每個 subreddit 的規範都不同，發文前先看規則
- 不要用 hashtag（Reddit 沒有這個慣例）
- 標題不要用 emoji（在大多數 subreddit 會顯得格格不入）
- 分享洞見，不要分享產品。"Here's what we learned" 勝過 "Check out our new feature"
- 跨版發文：依各 subreddit 調整語氣（r/startups、r/webdev、r/smallbusiness 各不相同）

**依主題挑 subreddit**：
| 主題 | Subreddits |
|-------|-----------|
| 產品發布 | r/SideProject、r/startups、r/indiehackers |
| 網頁開發 | r/webdev、r/javascript、r/reactjs |
| 設計 | r/web_design、r/UI_Design |
| 商業 | r/smallbusiness、r/Entrepreneur |
| 科技 | r/programming、r/technology |

**範例**：
```
Title: After 6 months of building, the biggest lesson was
"users want fewer clicks, not more features"

We built a feature our users kept requesting. Halfway through
we almost killed it because the prototype felt clunky.

What saved it: we stopped adding capabilities and started
removing steps. The final version does less than the prototype
but users complete the task in 1 click instead of 5.

Three things I'd tell past-me:
1. Prototype with your heaviest users, not your most vocal ones
2. "Ship weekly" forces you to cut scope — that's a feature
3. The thing users ask for and the thing they need are different

Anyone else had a similar experience where removing features
improved the product?
```

---

### 3. 圖片建議

針對每個平台，建議圖片需求：

| 平台 | 格式 | 尺寸 | 備註 |
|----------|--------|-----------|-------|
| LinkedIn | PNG/JPG | 1200×627 | 可以疊文字，關鍵訊息放中間 |
| Facebook | PNG/JPG | 1200×630 | 文字要少（舊的 20% 規則仍會影響觸及） |
| Instagram | PNG/JPG | 1080×1080 | 視覺優先，圖片本身要能脫離 caption 獨立成立 |
| Reddit | PNG/JPG | 不一定 | 選用，純文字貼文通常表現更好 |

如果有 `ai-image-generator` skill，建議用它來產生比例正確的配圖。

### 4. 輸出格式

把每則貼文放在標示清楚的區塊裡：

```
═══ LINKEDIN ═══
[post content]

═══ FACEBOOK ═══
[post content]

═══ INSTAGRAM (Caption) ═══
[caption content]

═══ INSTAGRAM (First Comment — Hashtags) ═══
[hashtags]

═══ REDDIT (r/subreddit) ═══
Title: [title]
Body: [body]
```

如果使用者想留著排程用，存到 `.jez/artifacts/social-posts-[topic].md`。

## Campaign 模式

產品發布或公告時，產生一組發文順序：

| 時間 | 平台 | 貼文類型 |
|--------|----------|-----------|
| Day -1 | LinkedIn | 預告 / 幕後花絮 |
| Day 0（早上） | 所有平台 | 公告貼文 |
| Day 0（下午） | Instagram Stories | 短影片/輪播 |
| Day +1 | Reddit | 以價值為主的討論 |
| Day +3 | LinkedIn | 成果/心得後續 |
| Day +7 | Facebook | 顧客反應 / 使用者見證 |

## 品質規則

1. **絕對不要把同一段文字複製貼到各平台**，每個平台的慣例都不同
2. **不要企業行話**，"leverage our synergies" 哪裡都不該出現
3. **把價值放在最前面**，每個平台都會截斷，第一行一定要能獨立成立
4. **配合平台文化**，LinkedIn 不是 Instagram，Instagram 也不是 Reddit
5. **給人一個互動的理由**：問題、投票，或真誠的討論引導
6. **檢查字數上限**：LinkedIn (3,000)、Facebook (63,206)、Instagram caption (2,200)、Reddit 標題 (300)
7. **絕對不要製造假互動**：LinkedIn 不要 "Drop a 🔥 if you agree"，Reddit 不要塞 hashtag
