---
name: "algo-seo-tfidf"
description: "實作 TF-IDF 評分，衡量詞彙相對於文件語料庫的重要性。當使用者需要依關鍵字相關性替文件排名、從文字擷取重要詞彙、或建立基本的搜尋相關性引擎時使用，即使他們說的是「找出相關文件」、「關鍵字擷取」或「詞彙重要性」也一樣。"
metadata:
  category: "WP-35 SEO 演算法"
  tags: ["seo", "tfidf", "information-retrieval", "text-analysis"]
---

# TF-IDF

## 概述

TF-IDF（詞頻–逆向文件頻率）把詞彙的重要性評為 TF(t,d) × IDF(t)。高分代表這個詞在某份文件裡很常出現，但在整個語料庫裡很少見。計算複雜度 O(N × V)，N 是文件數，V 是詞彙表大小。

## 何時使用

**觸發條件：**
- 要依關鍵字相關性替文件排名
- 要從文件擷取具區別性的詞彙
- 要建立不需要 ML 模型的輕量搜尋

**何時不要用：**
- 語意相似度很重要時（改用 embedding）
- 需要結合連結權威度排名時（搭配 PageRank）

## 演算法

```
鐵律：TF-IDF 衡量的是「相對」重要性
- TF 高但 IDF 低的詞是常見詞，「不是」重要詞
- TF-IDF = TF(t,d) × log(N / DF(t))
- 出現在「所有」文件的詞，IDF = 0 → 分數 = 0
```

### 階段 1：輸入驗證
把文件斷詞、轉小寫、移除停用詞。建立詞彙表。
**關卡：** 所有文件都已斷詞、詞彙表大小合理。

### 階段 2：核心演算法
1. 計算每份文件中每個詞的 TF(t,d)（原始次數、對數正規化或布林）
2. 計算 IDF(t) = log(N / DF(t))，其中 DF(t) = 包含詞 t 的文件數
3. 計算 TF-IDF(t,d) = TF(t,d) × IDF(t)
4. 視需要對文件向量做 L2 正規化，以便計算餘弦相似度

### 階段 3：驗證
檢查：出現在所有文件的詞，IDF ≈ 0。罕見的詞 IDF 高。
**關卡：** 分數分布合理；常見字分數低。

### 階段 4：輸出
回傳每份文件的詞彙評分，或每個查詢的文件排名。

## 輸出格式

```json
{
  "query_results": [{"document": "doc_id", "score": 0.73, "matching_terms": ["term1", "term2"]}],
  "metadata": {"corpus_size": 1000, "vocabulary_size": 5000, "tf_variant": "log_normalized"}
}
```

## 範例

### 輸入輸出範例
**輸入：** 語料庫：["the cat sat", "the dog sat", "the cat played"]，查詢："cat"
**預期：** TF("cat", doc1)=1/3、DF("cat")=2、IDF=log(3/2)=0.405。TF-IDF(doc1)=0.135、TF-IDF(doc3)=0.135、TF-IDF(doc2)=0

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 詞出現在所有文件 | 分數 = 0 | IDF = log(N/N) = 0 |
| 詞只出現在一份文件 | IDF 最高 | log(N/1) = log(N) |
| 空文件 | 所有分數 = 0 | 沒有詞可以評分 |

## 常見陷阱

- **停用詞很重要**：沒移除停用詞的話，「the」、「is」、「a」會主導 TF，但 IDF 是零。要好好做前處理。
- **TF 變體的選擇**：原始次數、log(1+count) 或布林 TF，會產生差異很大的排名。對數正規化能防止長文件佔上風。
- **IDF 平滑**：分母加 1，避免未知的查詢詞造成除以零：IDF = log(N / (DF+1)) + 1。
- **不是語意的**：「car」和「automobile」會被當成完全不同的詞。TF-IDF 沒有同義詞的概念。
- **依賴語料庫**：語料庫改變時，IDF 值也會變。新增文件會改變所有分數。

## 腳本

| 腳本 | 說明 | 用法 |
|--------|-------------|-------|
| `scripts/tfidf.py` | 計算 TF-IDF 向量、每份文件的前幾名詞彙，以及查詢評分 | `python scripts/tfidf.py --help` |

執行 `python scripts/tfidf.py --verify` 可以跑內建的健全性測試。

## 參考資料

- BM25（改良版的 TF-IDF），見 `references/bm25-comparison.md`
- 高效的倒排索引實作，見 `references/inverted-index.md`
