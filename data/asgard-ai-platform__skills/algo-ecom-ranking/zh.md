---
name: "algo-ecom-ranking"
description: "設計多目標的電商商品排序，結合相關性、轉換和商業指標。當使用者需要建立超越文字相關性的商品排序系統、在相關性與商業目標之間取得平衡，或實作 learning-to-rank 時使用，即使他們說的是『product sorting』『search result ranking』或『how to rank products』。"
metadata:
  category: "WP-43 電商搜尋演算法"
  tags: ["ecommerce", "ranking", "learning-to-rank", "multi-objective"]
---

# 電商商品排序

## 概述

電商排序把文字相關性（BM25）和商業訊號（CTR、轉換率、營收、毛利）合成一個統一的排序分數。用 learning-to-rank（LTR）模型，以點擊和轉換資料訓練，去最佳化對商業有意義的結果。

## 何時使用

**觸發條件：**
- 建立超越純文字相關性的商品搜尋 / 瀏覽排序
- 把商業指標（毛利、庫存）納入排序
- 實作 learning-to-rank 流程

**不該使用的情況：**
- 只需要純文字搜尋相關性時（用 BM25）
- 沒有點擊 / 轉換資料時（先從規則式排序開始）

## 演算法

```
IRON LAW: Relevance Is Necessary But NOT Sufficient for E-Commerce Ranking
A result that is textually relevant but has zero sales history, no
reviews, and is out of stock serves no one. E-commerce ranking must
balance: relevance (does it match the query?), quality (is it a good
product?), and commercial value (does it generate revenue?).
```

### 階段 1：輸入驗證
為每組商品與查詢配對收集特徵：文字相關性分數（BM25）、歷史 CTR、轉換率、平均評分、評論數、價格競爭力、庫存水位、毛利。
**關卡：** 具備最低限度的特徵，且有 30 天以上的點擊資料。

### 階段 2：核心演算法
**規則式基準：** Score = w₁×relevance + w₂×popularity + w₃×rating + w₄×recency。手動調權重。

**LTR 做法：**
1. 從點擊記錄產生訓練資料（點擊 = 正樣本，略過 = 負樣本，並去除版位偏誤）
2. 特徵：文字比對、行為（CTR、加入購物車率）、商品品質（評分、評論）、新鮮度、價格
3. 訓練：LambdaMART 或最佳化 NDCG 的梯度提升排序模型
4. 混合：final_score = α × LTR_score + (1-α) × business_boost

### 階段 3：驗證
離線評估：NDCG@10、MRR。線上 A/B 測試：每次搜尋的營收、點擊率、轉換率。
**關卡：** NDCG 比基準提升，A/B 測試在主要指標上為正面。

### 階段 4：輸出
回傳排好序的商品清單，附上分數拆解。

## 輸出格式

```json
{
  "results": [{"product_id": "P123", "rank": 1, "final_score": 0.92, "components": {"relevance": 0.85, "popularity": 0.95, "quality": 0.90}}],
  "metadata": {"query": "wireless earbuds", "model": "lambdamart", "ndcg_at_10": 0.72}
}
```

## 範例

### 輸入輸出範例
**輸入：** 查詢「laptop」，500 筆符合的商品
**預期：** 最前面的結果要兼顧文字比對 + 高轉換 + 好評分，不能只看關鍵字相關性。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 新商品，沒有歷史 | 依靠文字相關性 + 分類平均 | 冷啟動，沒有行為訊號 |
| 缺貨商品 | 降權或移除 | 顯示買不到的商品會讓使用者不爽 |
| 贊助商品 | 把廣告排名和自然排序混合 | 要清楚區分贊助與自然結果 |

## 注意事項

- **訓練資料的版位偏誤**：排名高的商品不管品質好壞都會有比較多點擊。用逆傾向加權（inverse propensity weighting）或隨機實驗來去除訓練資料的偏誤。
- **熱門偏誤**：沒有多樣性控制的話，熱門商品會壟斷排名，新的或小眾商品完全沒有曝光。要加探索加分。
- **營收最佳化 ≠ 使用者滿意**：依毛利排序會把貴的商品往上推。使用者覺得結果被商業操弄，就會失去信任。
- **特徵新鮮度**：點擊訊號每天都在變。要常常重新訓練或更新特徵。過期的特徵會讓排序品質下降。
- **分類專屬模型**：單一排序模型不一定適用所有分類。3C 的排序和服飾的排序不一樣。

## 參考資料

- LambdaMART 的實作，見 `references/lambdamart.md`
- 去除版位偏誤的技巧，見 `references/position-debiasing.md`
