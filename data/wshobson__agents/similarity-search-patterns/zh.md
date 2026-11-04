---
name: similarity-search-patterns
description: 用向量資料庫實作高效率的相似度搜尋。在建構語意搜尋、實作最近鄰查詢或優化檢索效能時使用。
---

# Similarity Search Patterns

在正式環境系統裡實作高效率相似度搜尋的模式。

## When to Use This Skill

- 建構語意搜尋系統
- 實作 RAG 檢索
- 建立推薦引擎
- 優化搜尋延遲
- 擴展到數百萬個向量
- 結合語意搜尋和關鍵字搜尋

## Core Concepts

### 1. Distance Metrics

| Metric             | Formula            | Best For              |
| ------------------ | ------------------ | --------------------- | --- | -------------- |
| **Cosine**         | 1 - (A·B)/(‖A‖‖B‖) | 正規化後的 embedding |
| **Euclidean (L2)** | √Σ(a-b)²           | 原始 embedding        |
| **Dot Product**    | A·B                | 向量大小有意義的時候     |
| **Manhattan (L1)** | Σ                  | a-b                   |     | 稀疏向量 |

### 2. Index Types

```
┌─────────────────────────────────────────────────┐
│                 Index Types                      │
├─────────────┬───────────────┬───────────────────┤
│    Flat     │     HNSW      │    IVF+PQ         │
│ (Exact)     │ (Graph-based) │ (Quantized)       │
├─────────────┼───────────────┼───────────────────┤
│ O(n) search │ O(log n)      │ O(√n)             │
│ 100% recall │ ~95-99%       │ ~90-95%           │
│ Small data  │ Medium-Large  │ Very Large        │
└─────────────┴───────────────┴───────────────────┘
```

## Templates and detailed worked examples

完整的範本庫和詳細的實作範例放在 `references/details.md`。需要具體範本時，再去讀那個檔案。

## Best Practices

### Do's

- **用適當的索引** - 大多數情況用 HNSW
- **調整參數** - 用 ef_search、nprobe 在召回率和速度之間取捨
- **實作混合搜尋** - 結合關鍵字搜尋
- **監控召回率** - 衡量搜尋品質
- **可以的話先做預先過濾** - 縮小搜尋空間

### Don'ts

- **不要跳過評估** - 先量測再優化
- **不要過度建索引** - 從 flat 開始，再往上擴展
- **不要忽略延遲** - P99 對使用體驗很重要
- **不要忘了成本** - 向量儲存的成本會累積
