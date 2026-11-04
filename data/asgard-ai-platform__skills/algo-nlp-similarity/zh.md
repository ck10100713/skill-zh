---
name: "algo-nlp-similarity"
description: "用詞彙與語意方法計算文字相似度，用於配對與去重。當使用者需要找出相似文件、偵測近乎重複的內容，或衡量文字之間的語意接近程度時使用，即使他們說的是『how similar are these texts』『find duplicates』或『semantic matching』。"
metadata:
  category: "WP-45 NLP 演算法"
  tags: ["nlp", "text-similarity", "embeddings", "deduplication"]
---

# 文字相似度

## 概述

文字相似度衡量兩段文字在意義或表面形式上有多接近。詞彙方法（Jaccard、TF-IDF 上的 cosine）比較詞的重疊度。語意方法（sentence embeddings）即使用字不同也能抓到意思。要選哪個，取決於你需要的是完全比對還是意義比對。

## 何時使用

**觸發條件：**
- 在集合中找出相似或重複的文件
- 把查詢配對到 FAQ 答案或知識庫條目
- 偵測抄襲或內容重複使用

**不該使用的情況：**
- 主題層級的分群（用主題模型 / LDA）
- 從文字中抽出實體（用 NER）

## 演算法

```
IRON LAW: Lexical Similarity ≠ Semantic Similarity
"The car is fast" and "The automobile is speedy" have LOW lexical
similarity (different words) but HIGH semantic similarity (same meaning).
"Bank of the river" and "Bank account" have HIGH lexical similarity
but LOW semantic similarity. Choose the method that matches your
definition of "similar."
```

### 階段 1：輸入驗證
確定：需要的相似度類型（詞彙或語意）、文字前處理需求、規模（成對 vs 全部配對 vs 查詢對語料庫）。
**關卡：** 文字已前處理，已選好方法。

### 階段 2：核心演算法
**詞彙方法：**
- Jaccard：詞集合上的 |A∩B| / |A∪B|
- TF-IDF 向量上的 cosine：cos(θ) = (A·B) / (|A|×|B|)

**語意方法：**
- Sentence embeddings：用 sentence-transformers（all-MiniLM-L6-v2）編碼文字
- 在 embedding 向量上算 cosine 相似度
- 大規模時：用 FAISS 或 Annoy 做近似最近鄰搜尋

### 階段 3：驗證
抽樣檢查：高度相似的配對應該真的相似。低相似度的配對應該真的不同。檢查門檻的校準。
**關卡：** 相似度分數在抽樣配對上和人的判斷一致。

### 階段 4：輸出
回傳相似度分數或最近鄰。

## 輸出格式

```json
{
  "similarities": [{"text_a": "doc1", "text_b": "doc5", "score": 0.92, "method": "semantic_cosine"}],
  "metadata": {"method": "sentence-transformers", "model": "all-MiniLM-L6-v2", "pairs_computed": 500}
}
```

## 範例

### 輸入輸出範例
**輸入：** 文字 A："How to reset my password"，文字 B："I forgot my login credentials"
**預期：** 詞彙（Jaccard）≈ 0.07（幾乎沒有詞重疊）。語意 ≈ 0.82（意圖相同）。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 完全相同的文字 | 分數 = 1.0 | 完全比對 |
| 空文字 | 無定義或 0 | 要妥善處理 |
| 不同語言 | 詞彙=0，語意視模型而定 | 多語言模型可以跨語言比對 |

## 注意事項

- **門檻依使用情境而定**：0.8 的相似度在去重時可能代表「重複」，在推薦時只代表「有點相關」。要用有標註的範例來校準門檻。
- **文字長度的影響**：TF-IDF 上的 cosine 對文件長度很敏感。很短的文字向量稀疏，相似度不可靠。短文字要用 embeddings。
- **Embedding 模型的選擇**：不同模型各有強項。all-MiniLM-L6-v2 速度快，但準確度不如較大的模型。要依效能需求選模型。
- **運算的擴展性**：N 份文件的全部配對相似度是 O(N²)。大型語料庫要用近似方法（locality-sensitive hashing、FAISS）。
- **領域適應**：通用的 embedding 模型可能抓不到領域專屬的相似度（法律、醫療）。要用領域資料 fine-tune 才有最好的效果。

## 參考資料

- Embedding 模型的比較與基準測試，見 `references/model-benchmarks.md`
- 大規模的近似最近鄰搜尋，見 `references/ann-search.md`
