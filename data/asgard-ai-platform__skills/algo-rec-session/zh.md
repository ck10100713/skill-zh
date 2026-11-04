---
name: "algo-rec-session"
description: "實作以 session 為基礎的推薦，從短期使用者行為序列做推薦，不依賴長期檔案。當使用者需要在匿名 session 中推薦、從瀏覽序列預測下一次點擊、或替未登入的使用者做推薦時使用，即使他們說的是「他們下一步會點什麼」、「匿名使用者推薦」或「瀏覽序列預測」也一樣。"
metadata:
  category: "WP-36 推薦系統"
  tags: ["recommendation", "session-based", "sequential", "real-time"]
---

# 以 Session 為基礎的推薦（Session-Based Recommendation）

## 概述

以 session 為基礎的推薦，是根據使用者當前 session 的點擊／瀏覽序列，預測他下一個會互動的項目，不依賴長期的使用者檔案。使用 Markov chain、關聯規則，或神經網路做法（GRU4Rec）。即時運作，推論複雜度 O(sequence_length)。

## 何時使用

**觸發條件：**
- 匿名使用者（沒登入、沒有長期檔案）
- 短時間的瀏覽 session，新近度最重要
- 在進行中的 session 裡，即時預測「下一個項目」

**何時不要用：**
- 有豐富的使用者歷史時（用 CF 或內容式，個人化效果更好）
- session 極短時（1-2 次點擊），訊號不足

## 演算法

```
鐵律：最前面的幾次點擊，重要性不成比例地高
以 session 為基礎的方法是在「沒有」長期檔案的情況下運作。
意圖必須從「很短」的序列推論出來。前 2-3 次點擊就決定了
這個 session 的意圖，早期訊號判讀錯誤，整個 session 都會偏掉。
```

### 階段 1：輸入驗證
把點擊流切成 session（依 session ID，或依逾時切分，通常是閒置 30 分鐘）。過濾掉低於最短長度（3 個以上事件）的 session。
**關卡：** session 已解析、已套用最短長度門檻。

### 階段 2：核心演算法
**Markov Chain 做法：**
1. 從所有 session 的項目到項目序列建出轉移矩陣
2. 對當前 session [A, B, C]，用 P(next | C) 或更高階的 P(next | B, C) 預測下一個項目

**關聯規則做法：**
1. 挖掘頻繁的項目序列（序列模式探勘）
2. 把當前 session 的結尾和已知模式比對
3. 推薦經常接在匹配模式後面的項目

### 階段 3：驗證
用 leave-one-out 評估：把每個 session 的最後一個項目藏起來，做預測，檢查命中率和 MRR（Mean Reciprocal Rank，平均倒數排名）。
**關卡：** Hit@20 明顯高於隨機基準線。

### 階段 4：輸出
回傳排好名的下一個項目預測，附上信心分數。

## 輸出格式

```json
{
  "predictions": [{"item_id": "789", "score": 0.65, "based_on": "last_3_clicks"}],
  "session": {"length": 5, "items_viewed": ["a", "b", "c", "d", "e"]},
  "metadata": {"method": "markov_order2", "hit_rate_at_20": 0.35}
}
```

## 範例

### 輸入輸出範例
**輸入：** Session：[shoes_page, running_shoes, nike_air_max]
**預期：** 推薦：nike_air_zoom (0.72)、adidas_ultraboost (0.58)、shoe_size_guide (0.41)

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| Session 長度 = 1 | 退回熱門度 | 單一次點擊不足以形成序列模式 |
| 重複瀏覽同一項目 | 加重新近度，不是次數 | 使用者可能是在比較，不是在擴大範圍 |
| Session 意圖轉移 | 適應最新的點擊 | 使用者在 session 中途改變了目標 |

## 常見陷阱

- **session 的定義很重要**：30 分鐘逾時是慣例，但很隨意。電商可能需要更短（15 分鐘）；研究型的瀏覽可能需要更長（60 分鐘）。
- **位置偏誤**：使用者比較常點排在上面的結果。session 資料反映的是 UI 位置，不只是偏好。要修正位置偏誤。
- **重複推薦**：使用者常會回頭看看過的項目。要區分「推薦新的東西」和「提醒之前看過的」。
- **新項目的冷啟動**：從沒出現在任何 session 的項目，轉移矩陣預測不到。要混入以特徵為基礎的候選項目。
- **計算效率**：即時推論的話，要預先算好轉移機率。大規模下每次請求都重算，太慢了。

## 參考資料

- GRU4Rec 神經網路 session 模型，見 `references/gru4rec.md`
- session 切分的啟發法，見 `references/session-splitting.md`
