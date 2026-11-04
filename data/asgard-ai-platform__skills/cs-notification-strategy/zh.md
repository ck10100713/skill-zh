---
name: "cs-notification-strategy"
description: "設計推播通知與訊息策略，包含管道選擇、發送時間最佳化、個人化與通知疲勞管理。當使用者需要提升通知互動率、降低退訂率、規劃多管道訊息，或對通知內容做 A/B 測試時使用。就算使用者只說「我們的推播開啟率很低」、「使用者一直在取消訂閱」、「通知該什麼時候發」或「警示該用哪個管道」也要用。"
metadata:
  category: "WP-06 Agent通訊+客服"
  tags: ["notification", "push", "engagement", "retention"]
---

# 通知策略

## 框架

```
IRON LAW: Every Notification Must Earn Its Send

Each notification interrupts the user. If it doesn't deliver clear value
to the RECIPIENT (not to your business), it erodes trust and drives
opt-outs. Before sending: "Would the user thank me for this notification?"
If no → don't send.
```

### 管道比較

| 管道 | 開啟率 | 速度 | 成本 | 最適合 | 限制 |
|---------|----------|-------|------|----------|-------------|
| **推播通知** | 5-15% | 即時 | 免費 | 有時效、需要採取行動的 | 容易被關閉，文字有限 |
| **Email** | 15-25% | 數分鐘 | 低 | 詳細內容、收據、電子報 | 垃圾郵件過濾、較慢 |
| **SMS** | 90%+ 開啟 | 即時 | $$$ | 重要警示、OTP、緊急事項 | 貴、打擾性高、有法規限制 |
| **App 內訊息** | 25-40% | 下次開啟時 | 免費 | 功能公告、小技巧 | 只觸及活躍使用者 |
| **LINE/Messenger** | 40-60% | 即時 | 免費到 $ | 對話式、台灣/亞洲 | 依賴平台 |

### 發送時間最佳化

| 受眾 | 最佳時間 | 最差時間 |
|----------|----------|-----------|
| B2C 一般 | 上午 10-12 點、晚上 7-9 點 | 凌晨 12-6 點、通勤時 |
| B2B | 週二到週四上午 9-11 點 | 週末、週五下午 |
| 電商 | 週四到週六（週末前購物） | 週一上午 |
| 突發/緊急 | 立刻 | 不適用 |

**時區規則**：用「收件人」的時區發送，不是你的。

### 個人化層級

| 層級 | 內容 | 範例 | 相較通用訊息的提升 |
|------|------|---------|----------------|
| **無** | 所有人收到同一則訊息 | 「來看看我們的特賣！」 | 基準 |
| **分群** | 依使用者群組 | 「身為高級會員，你可以搶先體驗」 | +20-30% |
| **行為** | 依過去的行為 | 「你購物車裡的商品快賣完了」 | +40-60% |
| **個人** | 1:1 個人化 | 「嗨 [名字]，你最愛的 [產品] 又有貨了」 | +60-80% |

### 疲勞管理

| 訊號 | 代表什麼 | 行動 |
|--------|-------------|--------|
| 開啟率下滑 | 內容越來越不相關 | 改善目標對象/內容 |
| 退訂率 > 0.5%/次 | 發太多或內容不對 | 降低頻率、分群更精細 |
| 推播後解除安裝暴增 | 通知正在把使用者趕走 | 立刻降低量 |
| 點擊率下滑但開啟率穩定 | 標題不錯，內容令人失望 | 改善內容/優惠品質 |

**頻率上限**：設定每位使用者在一段時間內的通知上限：
- 推播：最多每週 3-5 則
- Email：最多每週 2-3 封（行銷類），交易類不限
- SMS：最多每月 2-4 則

### 通知的 A/B 測試

| 元素 | 測什麼 | 範例 |
|---------|-------------|---------|
| **標題** | 長度、語氣、emoji、個人化 | 「你的訂單已出貨 📦」vs「訂單 #1234 正在送達途中」 |
| **時間** | 一天中的時段、星期幾 | 上午 10 點 vs 晚上 7 點 |
| **內容** | 簡短 vs 詳細、圖片 vs 純文字 | 20 字 vs 50 字 |
| **CTA** | 按鈕文字、動作類型 | 「查看」vs「立即追蹤」 |
| **管道** | 同一則訊息用推播、email 還是 App 內訊息 | 內容相同，管道不同 |

## 輸出格式

```markdown
# Notification Strategy: {Product/Campaign}

## Channel Mix
| Message Type | Primary Channel | Fallback | Frequency |
|-------------|----------------|----------|-----------|
| {type} | {channel} | {backup} | {max/period} |

## Segmentation
| Segment | Notification | Personalization Tier |
|---------|-------------|---------------------|
| {segment} | {content} | None/Segment/Behavioral/Individual |

## Timing
| Segment | Send Time | Day | Timezone |
|---------|----------|-----|---------|
| {segment} | {HH:MM} | {day(s)} | {user's TZ} |

## Fatigue Rules
- Max push: {N}/week
- Max email: {N}/week
- Opt-out threshold: {%} → action: {reduce/pause}

## A/B Test Plan
| Test | Variant A | Variant B | Metric | Sample |
|------|----------|----------|--------|--------|
| {test} | {A} | {B} | {open rate / CTR} | {N users} |
```

## 常見陷阱

- **權限是一種特權**：iOS 的推播需要使用者明確同意。要在「對的時機」問（使用者看到價值之後），不要在第一次開啟時就問。第一次開啟就要求權限，同意率是 40-60%；情境式詢問可到 70-80%。
- **交易類 vs 行銷類**：訂單確認、出貨更新和安全警示屬於交易類（使用者預期會收到，開啟率高）。行銷促銷是打擾性的（可有可無，開啟率較低）。在使用者的感受裡絕對不要把兩者混在一起。
- **台灣的 LINE 很特別**：LINE 在台灣的滲透率有 95%。LINE 官方帳號訊息的開啟率有 60% 以上，遠高於 email 或推播。台灣受眾要優先用 LINE。
- **Rich push 被低估**：推播通知可以帶圖片、動作按鈕和 deep link。帶「查看訂單」按鈕的 rich push，轉換率比純文字推播高 3 到 5 倍。

## 參考資料

- LINE 通知設定，見 `references/line-notification.md`
- Email 送達率最佳化，見 `references/email-deliverability.md`
