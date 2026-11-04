---
name: "algo-nlp-lda"
description: "實作 LDA 主題模型，找出文件集合中的潛在主題。當使用者需要從文本語料抽出主題、依主題分類文件，或探索主題結構時使用，即使他們說的是『what are the main topics』『topic extraction』或『document clustering by theme』。"
metadata:
  category: "WP-45 NLP 演算法"
  tags: ["nlp", "lda", "topic-modeling", "text-mining"]
---

# LDA 主題模型

## 概述

Latent Dirichlet Allocation 把每份文件建模成多個主題的混合，每個主題則是詞彙上的分布。以非監督的方式從語料庫找出 K 個潛在主題。使用 Gibbs sampling 或變分推論。複雜度：O(N × K × iterations)，N = 詞 token 總數。

## 何時使用

**觸發條件：**
- 在大量文件中找出潛在主題
- 依自動找出的主題組織 / 分類文件
- 類別未知時的探索式文本分析

**不該使用的情況：**
- 類別已知時（用監督式分類）
- 短文本（推文、標題），每份文件字數太少，無法可靠地指派主題
- 需要語意理解時（用 embeddings）

## 演算法

```
IRON LAW: The Number of Topics K Must Be Chosen, Not Discovered
LDA does NOT tell you how many topics exist. K is a hyperparameter.
Too few topics: overly broad, mixed themes. Too many: fragmented,
redundant topics. Use coherence score (C_v) to compare K values,
but the final choice requires human judgment on topic interpretability.
```

### 階段 1：輸入驗證
前處理：斷詞、移除停用字、做詞形還原。建立文件-詞矩陣。過濾：移除出現在少於 5 份或超過 50% 文件的詞。
**關卡：** DTM 乾淨，詞彙量合理（1K-50K 個詞）。

### 階段 2：核心演算法
1. 選 K（從 √(N/2) 開始，試範圍 K=5,10,15,20,...）
2. 設定超參數：α = 50/K（文件-主題密度）、β = 0.01（主題-詞密度）
3. 執行 LDA（Gibbs sampling：1000 次以上迭代，或變分推論）
4. 抽出：主題-詞分布（每個主題前 10-20 個詞）和文件-主題分布

### 階段 3：驗證
評估：主題一致性（C_v 分數，越高越好）、人工檢視每個主題的前幾個詞、檢查有沒有「垃圾」主題（混雜不連貫的詞）。
**關卡：** 一致性分數可接受，主題人看得懂。

### 階段 4：輸出
回傳主題，附上前幾個詞和文件歸屬。

## 輸出格式

```json
{
  "topics": [{"id": 0, "label": "finance", "top_words": ["revenue", "profit", "quarter", "growth"], "coherence": 0.55}],
  "doc_topics": [{"doc_id": "d1", "dominant_topic": 0, "topic_distribution": [0.7, 0.1, 0.2]}],
  "metadata": {"K": 10, "coherence_avg": 0.48, "documents": 5000, "vocabulary": 8000}
}
```

## 範例

### 輸入輸出範例
**輸入：** 1000 篇新聞文章，K=5
**預期：** 主題像是：{政治、體育、科技、商業、娛樂}，每個主題的前幾個詞都連貫。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 非常短的文件 | 主題指派很差 | 字太少，無法可靠估計混合比例 |
| 同質的語料庫 | 1-2 個主題占主導 | 所有文件都很相似，主題多樣性有限 |
| K=1 | 單一主題 = 語料庫詞彙 | 退化的情況，沒有區分力 |

## 注意事項

- **一定要移除停用字**：如果留著停用字，LDA 會產生被常見詞（「the」「is」「and」）主導的「垃圾」主題。
- **主題命名要手動**：LDA 給的是詞的分布，不是主題名稱。你必須根據前幾個詞自己詮釋並命名。
- **可重現性**：Gibbs sampling 是隨機的。不同的隨機種子會得到不同的主題。要跑多次並檢查穩定性。
- **動態主題**：標準 LDA 假設主題是靜態的。對於會演變的語料庫（跨年的新聞），要用 Dynamic Topic Models。
- **超參數的敏感度**：α 低會讓文件的主題更少、更鮮明。β 低會讓主題的詞更少、更具體。要調整，或用自動方法。

## 參考資料

- 一致性指標與 K 的選擇，見 `references/topic-evaluation.md`
- 動態與相關主題模型，見 `references/advanced-lda.md`
