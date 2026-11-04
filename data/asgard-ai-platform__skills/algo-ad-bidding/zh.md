---
name: "algo-ad-bidding"
description: "實作並挑選廣告出價策略，從手動 CPC 到自動化的 target-CPA、target-ROAS 都包含。當使用者需要選出價策略、設定自動出價或最佳化出價參數時使用，即使他們說的是『what bidding strategy should I use』『target CPA setup』或『smart bidding configuration』。"
metadata:
  category: "WP-37 廣告演算法"
  tags: ["advertising", "bidding-strategy", "automated-bidding", "optimization"]
---

# 廣告出價策略

## 概述

出價策略決定廣告主每次競價要付多少錢。範圍從手動 CPC（完全自己控制）到自動化策略（Target CPA、Target ROAS、Maximize Conversions），後者用機器學習依情境訊號即時最佳化出價。

## 何時使用

**觸發條件：**
- 在手動與自動出價策略之間做選擇
- 設定或排查 Target CPA / Target ROAS 廣告活動
- 分析出價策略的成效並做調整

**不該使用的情況：**
- 設計競價機制本身時（用 GSP/VCG）
- 建立 CTR 預測模型時（用 CTR prediction skill）

## 演算法

```
IRON LAW: Automated Bidding Requires SUFFICIENT Conversion Data
Below ~30 conversions/month, the algorithm lacks signal and performs
WORSE than manual bidding. Strategy selection depends on data volume:
- < 30 conv/month: Manual CPC or Maximize Clicks
- 30-50 conv/month: Maximize Conversions
- 50+ conv/month: Target CPA
- 50+ conv/month + revenue data: Target ROAS
```

### 階段 1：輸入驗證
評估：每月轉換量、轉換追蹤的準確度、廣告活動預算、業務目標（量 vs 效率 vs 營收）。
**關卡：** 轉換追蹤已驗證，且資料量足以支撐所選策略。

### 階段 2：核心演算法
**Manual CPC：** 逐個關鍵字設定出價。依裝置、時段、地點、受眾成效資料來調整。

**Target CPA：** 1. 設定目標單次獲客成本。2. 演算法用情境訊號預測每次競價的轉換機率。3. 轉換機率高就加價，低就降價。4. 目標是長期平均下來落在 target CPA。

**Target ROAS：** 跟 CPA 一樣，但改成最佳化廣告投資報酬率 = conversion_value / cost。

### 階段 3：驗證
監控：實際 CPA 對比目標、轉換量是否穩定、曝光比重變化、預算使用率。
**關卡：** 學習期（2-4 週）過後，實際 CPA 要落在目標的 20% 以內。

### 階段 4：輸出
回傳策略建議，附上預期的成效範圍。

## 輸出格式

```json
{
  "recommendation": {"strategy": "target_cpa", "target": 500, "currency": "TWD", "confidence": "high"},
  "expected_performance": {"cpa_range": [400, 600], "volume_change": "-10% to +15%"},
  "metadata": {"monthly_conversions": 85, "current_cpa": 550, "learning_period_days": 14}
}
```

## 範例

### 輸入輸出範例
**輸入：** 電商廣告活動，每月 120 次轉換，目前 CPA=NT$450，目標：維持 CPA、拉高量
**預期：** Target CPA 設在 NT$450。預期：演算法找到有效率的競價後，量會增加 10-20%。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 每月 10 次轉換 | Manual CPC | 資料不足，無法自動化 |
| Target CPA 設得太激進 | 量掉到接近零 | 演算法找不到有利潤的競價 |
| 轉換追蹤壞掉 | 所有策略都會失敗 | 垃圾資料進，垃圾最佳化出 |

## 注意事項

- **學習期的波動**：切換策略後的前 2 週成效不穩定。這段時間不要改目標。
- **轉換延遲**：如果轉換要隔好幾天才歸因（例如 B2B），演算法就是在過期的資料上做最佳化。用轉換建模，或把歸因視窗拉長。
- **預算是限制條件**：Target CPA 達不到目標就不會花錢。大預算搭配很激進的 CPA，不會讓花費變多，只是省錢。
- **微轉換**：如果拿代理轉換（加入購物車）而不是最終購買來訓練，演算法就會去最佳化那個代理指標。要確保追蹤的轉換和商業價值一致。
- **季節性衝擊**：自動出價是從近期資料學習的。黑色星期五、節日或競爭事件會把它帶偏。要用季節性調整。

## 參考資料

- 出價策略遷移的操作手冊，見 `references/migration-playbook.md`
- 學習期的最佳實務，見 `references/learning-period.md`
