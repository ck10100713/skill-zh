---
name: "ecom-conversational"
description: "設計跨訊息平台的對話式商務體驗，包含聊天機器人流程、商品卡片與轉換策略。當使用者需要透過 LINE、WhatsApp、Instagram DM 或其他訊息管道銷售、設計聊天機器人購物流程，或把訊息整合進銷售漏斗時使用。就算使用者只說「用 LINE 賣東西」、「做一個購物聊天機器人」、「客人都在私訊問要買」或「對話式銷售策略」也要用。"
metadata:
  category: "WP-01 電商"
  tags: ["e-commerce", "conversational-commerce", "chatbot", "messaging"]
---

# 對話式商務

## 框架

```
IRON LAW: Conversation First, Commerce Second

Conversational commerce works because it meets customers WHERE THEY
ALREADY ARE (messaging apps). Forcing a sales pitch into a chat channel
kills trust. The conversation must provide genuine value (answering questions,
solving problems) BEFORE introducing products or purchases.

The sequence: Help → Trust → Recommend → Convert
```

### 平台比較（以亞太地區為主）

| 平台 | 使用者數（台灣） | 商務功能 | 最適合 |
|----------|---------------|------------------|----------|
| **LINE** | 2,100 萬以上（滲透率 95%） | LINE 購物、Rich Menu、LIFF、支付 | 台灣、日本、泰國的主要管道 |
| **Instagram DM** | 約 1,000 萬 | 商品標籤、快速回覆、商品貼圖 | 視覺型商品、較年輕的族群 |
| **Facebook Messenger** | 約 1,800 萬 | 商店整合、自動回覆 | 觸及廣、較年長的族群 |
| **WhatsApp** | 台灣使用有限 | 型錄、購物車、支付（部分市場） | 東南亞、印度、巴西 |
| **WeChat** | 約 100 萬（台灣） | 小程式、微信支付 | 與中國有往來的企業 |

### 對話流程設計

**1. 進入點**：客戶怎麼開始對話
- 門市的 QR code、廣告的點擊後傳訊息、網站聊天視窗、社群連結

**2. 歡迎流程**：前 3 則訊息
- 親切問候、設定期待、提供導覽選項
- 用 Rich Menu（LINE）或快速回覆按鈕，一開始不要問開放式問題

**3. 商品探索**：幫他們找到需要的東西
- 引導式提問：「你在找什麼？」→ 類別 → 商品
- 附圖片、價格和「購買」按鈕的商品卡片
- 依對話脈絡做 AI 推薦

**4. 購買流程**：把阻力降到最低
- 盡量在聊天室內完成結帳（LINE Pay、App 內支付）
- 如果要導到網站，要 deep link 到特定商品（不是首頁）
- 附追蹤資訊的訂單確認訊息

**5. 購後**：留住客戶並追加銷售
- 用訊息通知出貨進度
- 後續關心：「商品用得怎麼樣？」（到貨後 7 天）
- 依購買紀錄做個人化推薦

### 機器人 vs 轉真人

| 情境 | 由機器人處理 | 轉給真人 |
|----------|----------------|------------------|
| FAQ（營業時間、運送、退貨） | ✓ | — |
| 商品推薦（簡單的） | ✓ | — |
| 複雜的商品問題 | — | ✓ |
| 客訴 / 問題 | — | ✓（立即） |
| 高單價購買 | 機器人協助 → 真人成交 | ✓ |

**關鍵指標**：機器人自助解決率（不需真人就解決的比例），成熟的機器人目標是 60-70%。

## 輸出格式

```markdown
# Conversational Commerce Plan: {Business}

## Channel Selection
- Primary: {platform} — rationale: {why}
- Entry points: {QR / ad / social / website}

## Conversation Flow
1. Welcome: {message template}
2. Discovery: {question flow}
3. Product Card: {template}
4. Checkout: {in-chat / redirect}
5. Post-purchase: {follow-up sequence}

## Bot vs Human Split
| Scenario | Handler | SLA |
|----------|---------|-----|
| {scenario} | Bot/Human | {response time} |

## KPIs
| Metric | Target |
|--------|--------|
| Response time | < {X} seconds (bot) / < {X} minutes (human) |
| Containment rate | > 60% |
| Conversation-to-purchase rate | > {X%} |
| Customer satisfaction (CSAT) | > 4.0/5 |
```

## 常見陷阱

- **LINE 官方帳號的方案等級很重要**：免費方案限制每月訊息數，超過就會被限流。客戶數超過 500 就要編預算升級付費方案。
- **不要過度自動化**：機器人聽不懂問題，一直循環「我不太明白，請從選單中選擇」，會比沒有機器人更快毀掉信任。一定要提供轉真人的路徑。
- **訊息是非同步的**：跟電話不同，客戶預期傳了訊息之後晚點再回來。流程要能承受中斷：保存購物車狀態、記住上下文。
- **訊息中的隱私**：聊天紀錄是個人的。沒有取得同意，不要在內部分享對話，也要對資料用途保持透明。
- **社群電商在東南亞/台灣快速爆發**：LINE 購物、Instagram 購物、TikTok Shop 讓社群和商務的界線變得模糊。把它們當成主要管道，不是附加選項。

## 參考資料

- LINE 官方帳號的設定，見 `references/line-oa-setup.md`
- 聊天機器人 NLU 設計模式，見 `references/chatbot-design.md`
