---
name: "algo-ecom-bm25"
description: "實作 BM25 排序函式，用於電商商品搜尋的相關性評分。當使用者需要建立以文字為基礎的商品搜尋引擎、改善搜尋結果相關性，或想把基本 TF-IDF 換成更穩健的排序函式時使用，即使他們說的是『product search ranking』『search relevance』或『BM25 implementation』。"
metadata:
  category: "WP-43 電商搜尋演算法"
  tags: ["ecommerce", "bm25", "search", "information-retrieval"]
---

# BM25 排序函式

## 概述

BM25（Best Matching 25）是改良版的 TF-IDF 排序函式，加入了詞頻飽和和文件長度正規化。Score = Σ IDF(t) × (TF(t,d) × (k₁+1)) / (TF(t,d) + k₁ × (1 - b + b × |d|/avgdl))。標準參數：k₁=1.2、b=0.75。大多數文字搜尋引擎（Elasticsearch、Solr）的骨幹。

## 何時使用

**觸發條件：**
- 建立以文字相關性排序的商品搜尋
- 把基本 TF-IDF 換成文件長度正規化更好的做法
- 在 Elasticsearch/Solr 裡調整搜尋相關性

**不該使用的情況：**
- 語意相似度比關鍵字比對更重要時（用 embeddings）
- 單一欄位的完全比對（用更簡單的方法就夠了）

## 演算法

```
IRON LAW: BM25 Has Two Critical Parameters — k₁ and b
k₁ controls term frequency saturation: higher k₁ = more weight to
repeated terms. k₁=0 ignores TF entirely (boolean).
b controls document length normalization: b=1 fully normalizes by
length, b=0 ignores length. Default k₁=1.2, b=0.75 works for most
cases but MUST be tuned for your specific corpus.
```

### 階段 1：輸入驗證 + 斷詞
把每份文件斷成小寫的單字 token。計數之前要**移除停用字**，隨附的 script 會丟掉一份標準的英文停用字清單（`the, a, an,
and, or, but, of, in, on, at, to, for, with, by, from, as, is, are, was, were,
be, been, being`）。接著建立反向索引：詞 → (文件, 詞頻) 的清單。計算：文件長度（移除停用字之後）、平均文件長度、每個詞的文件頻率。

> ⚠️ **移除停用字會影響 `|d|` 和 `avgdl`**：因為量長度之前就已經丟掉停用字，
> 手算 BM25 時如果沒移除，長度正規化會錯，分數會差 3–5%。
> 如果你是手動重現 BM25 來和 script 比對，要先套用同一份停用字清單，或乾脆直接跑 script。

**關卡：** 索引已建好、統計量已算出、語料庫不是空的。

### 階段 2：核心演算法
對於包含詞 t₁...tₙ 的查詢 Q，針對文件 d：
1. 對每個查詢詞 tᵢ：計算 IDF(tᵢ) = log((N - DF(tᵢ) + 0.5) / (DF(tᵢ) + 0.5) + 1)
2. 計算 TF 部分：(TF(tᵢ,d) × (k₁+1)) / (TF(tᵢ,d) + k₁ × (1 - b + b × |d|/avgdl))
3. Score(d, Q) = Σᵢ IDF(tᵢ) × TF_component(tᵢ, d)
4. 依分數由高到低排序文件

> ⚠️ **IDF 變體已鎖定**：BM25 在外面有好幾種 IDF 公式（Robertson-Sparck Jones、
> 經典 Okapi、Lucene 的平滑 `+1`、BM25+、BM25L）。
> 這個 skill 和隨附的 script 用的是上面那個 **Lucene 風格的平滑變體**
> （`log((N - df + 0.5) / (df + 0.5) + 1)`），遇到非常常見的詞也不會得到負的 IDF。
> 如果你拿分數去和別的引擎（Elasticsearch、Solr、Whoosh）比，即使輸入完全一樣，也可能差 3–5%。
> 除非你打算全面換掉這個變體，否則不要去「修正」script。

### 階段 3：驗證
抽樣檢查：查詢「red shoes」時，同時包含「red」和「shoes」的文件應該排在只含其中一個詞的文件前面。同時有這兩個詞的短商品標題，應該排在只零星提到的長描述前面。
**關卡：** 10 個以上的測試查詢通過相關性抽樣檢查。

### 階段 4：輸出
回傳排好序的結果，附上分數。

## 輸出格式

```json
{
  "results": [{"doc_id": "SKU-123", "score": 12.5, "title": "Red Running Shoes"}],
  "metadata": {"query": "red shoes", "hits": 85, "k1": 1.2, "b": 0.75, "avg_doc_length": 45}
}
```

## 範例

### 輸入輸出範例
**輸入：** 查詢「wireless earbuds」，語料庫有 1000 筆商品
**預期：** 標題有「wireless earbuds」的商品排最前面；「wireless headphones」排比較後面（沒有「earbuds」這個詞）。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 單字查詢 | 由 IDF 主導排序 | 只有一個詞的 IDF 能拉開差距 |
| 非常常見的詞（「the」） | IDF 趨近零，影響很小 | IDF 會壓低常見詞 |
| 文件重複 100 次 | TF 飽和，分數不會是 100 倍 | k₁ 限制了重複的好處 |

## 注意事項

- **多欄位評分**：電商商品有標題、描述、品牌、分類。欄位權重要不同：標題命中 > 描述命中。用欄位加權的 BM25。
- **同義詞與詞幹還原**：BM25 是關鍵字完全比對。「earphones」不會比對到「earbuds」。要在查詢流程裡加同義詞擴展和詞幹還原。
- **參數調校**：預設的 k₁=1.2、b=0.75 合理，但不是最佳。要用你自己商品目錄的相關性判斷來調。
- **數值屬性**：BM25 不處理數值篩選（價格區間、評分）。拿它做文字相關性，再結合數值篩選條件。
- **零結果查詢**：BM25 查不到東西時，退回模糊比對或語意搜尋，不要顯示空白結果。

## Scripts

| Script | 說明 | 用法 |
|--------|-------------|-------|
| `scripts/bm25.py` | 用 BM25 排序函式針對查詢替文件打分 | `python scripts/bm25.py --help` |

執行 `python scripts/bm25.py --verify` 來跑內建的健全性測試。

## 參考資料

- BM25F 多欄位延伸，見 `references/bm25f.md`
- 參數調校方法論，見 `references/parameter-tuning.md`
