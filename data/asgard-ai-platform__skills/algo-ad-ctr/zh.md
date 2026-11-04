---
name: "algo-ad-ctr"
description: "建立 CTR 預測模型，從特徵估算廣告點擊率。當使用者需要預測點擊機率、建立廣告排序模型或評估廣告素材成效時使用，即使他們說的是『predict click rate』『ad relevance scoring』或『which ad will get more clicks』。"
metadata:
  category: "WP-37 廣告演算法"
  tags: ["advertising", "ctr-prediction", "machine-learning", "ranking"]
---

# CTR 預測模型

## 概述

CTR 預測是在給定情境（使用者、查詢、廣告、版位）下，估計使用者點擊廣告的機率。它是廣告排序的核心：AdRank = Bid × pCTR。通常用邏輯迴歸或梯度提升樹，用數十億筆曝光來訓練。

## 何時使用

**觸發條件：**
- 建立或改善廣告排序系統
- 為了最佳化出價而預測點擊機率
- 從特徵分析評估廣告素材的成效

**不該使用的情況：**
- 預測點擊之後的轉換時（用轉換率模型）
- 設定出價金額時（用出價策略 skill）

## 演算法

```
IRON LAW: A CTR Model Must Be CALIBRATED
Predicting relative ranking is insufficient. The predicted probability
must MATCH actual click frequency (e.g., predicted 5% → 5 clicks per
100 impressions). Without calibration, bid optimization breaks:
  Expected Value = Bid × pCTR × pConversion
  If pCTR is off by 2x, bids are wrong by 2x.
```

### 階段 1：輸入驗證
收集曝光記錄，包含：使用者特徵、廣告特徵、查詢特徵、版位、點擊標籤（0/1）。處理類別不平衡（CTR 通常 1-5%）。
**關卡：** 資料量足夠（100K+ 曝光）、點擊標籤已驗證、版位沒有造成資料洩漏。

### 階段 2：核心演算法
1. 特徵工程：使用者人口統計、廣告類別、查詢與廣告的匹配度、歷史 CTR、時間/裝置特徵
2. 訓練模型：邏輯迴歸（可解釋）或 GBDT（準確度較高）
3. 校準預測：在 holdout 集上用 Platt scaling 或 isotonic regression
4. 評估：log-loss（校準）+ AUC（排序品質）

### 階段 3：驗證
檢查校準：把預測值分成十分位的桶，逐桶比較預測 CTR 和實際 CTR。畫 reliability diagram。
**關卡：** 校準曲線貼近對角線，AUC > 0.70。

### 階段 4：輸出
回傳預測的 CTR，附上信賴區間和貢獻最大的特徵。

## 輸出格式

```json
{
  "prediction": {"ctr": 0.035, "confidence_interval": [0.028, 0.042]},
  "top_features": [{"feature": "query_ad_match", "importance": 0.32}],
  "metadata": {"model": "gbdt", "auc": 0.78, "log_loss": 0.21, "calibration_error": 0.008}
}
```

## 範例

### 輸入輸出範例
**輸入：** 訓練好的邏輯迴歸，有 3 個特徵，係數如下：
```
intercept: -3.0
position_1:  0.8
query_ad_match: 1.5
user_is_mobile: 0.3
```
當前請求的特徵：position_1=1, query_ad_match=1, user_is_mobile=1

**預期：** logit = -3.0 + 0.8 + 1.5 + 0.3 = -0.4
pCTR = sigmoid(-0.4) = 1/(1 + e^0.4) ≈ 0.401 → **40.1%**

驗證：特徵全為 0（基準）時，pCTR = sigmoid(-3.0) ≈ 0.047（4.7%）。校準的檢查方式，是把預測值分桶，再和每個桶的實際 CTR 比較。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 新廣告，沒有歷史 | 用廣告類別的平均值 | 特徵的冷啟動 |
| 版位 1 vs 版位 4 | CTR 不同，相關性相同 | 版位偏誤會墊高最上面版位的 CTR |
| 非常冷門的查詢 | 低信心 | 這個查詢的訓練資料不足 |

## 注意事項

- **版位偏誤**：不管相關性如何，版位 1 的廣告就是比較多人點。要用去除版位偏誤的資料訓練，或把版位當特徵，在推論時再做正規化。
- **資料新鮮度**：CTR 模式變動很快（季節性、趨勢）。每天重新訓練，或用 online learning。
- **特徵洩漏**：如果納入由點擊衍生的特徵（例如這組廣告與查詢配對的歷史 CTR），沒有用時間切分小心處理的話就會造成洩漏。
- **類別不平衡**：97% 沒點、3% 有點。要用合適的評估指標（log-loss、AUC），不要看 accuracy。訓練時可以考慮對負樣本降採樣。
- **多任務學習**：CTR 和轉換率有關但不一樣。聯合模型透過共用底層，可以讓兩者都變好。

## 參考資料

- 特徵工程的最佳實務，見 `references/feature-engineering.md`
- 去除版位偏誤的技巧，見 `references/position-debiasing.md`
