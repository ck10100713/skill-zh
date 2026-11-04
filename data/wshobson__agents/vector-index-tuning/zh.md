---
name: vector-index-tuning
description: 針對延遲、召回率（recall）和記憶體最佳化向量索引的效能。調整 HNSW 參數、選擇量化（quantization）策略，或擴展向量搜尋基礎設施時使用。
---

# Vector Index Tuning

最佳化向量索引、達到 production 效能的指南。

## When to Use This Skill

- 調整 HNSW 參數
- 實作量化
- 最佳化記憶體使用量
- 降低搜尋延遲
- 在召回率和速度之間取得平衡
- 擴展到數十億個向量

## Core Concepts

### 1. Index Type Selection

```
Data Size           Recommended Index
────────────────────────────────────────
< 10K vectors  →    Flat (exact search)
10K - 1M       →    HNSW
1M - 100M      →    HNSW + Quantization
> 100M         →    IVF + PQ or DiskANN
```

### 2. HNSW Parameters

| Parameter          | Default | Effect                                               |
| ------------------ | ------- | ---------------------------------------------------- |
| **M**              | 16      | 每個節點的連線數，↑ = 召回率更好、記憶體用更多 |
| **efConstruction** | 100     | 建立品質，↑ = 索引更好、建立更慢        |
| **efSearch**       | 50      | 搜尋品質，↑ = 召回率更好、搜尋更慢     |

### 3. Quantization Types

```
Full Precision (FP32): 4 bytes × dimensions
Half Precision (FP16): 2 bytes × dimensions
INT8 Scalar:           1 byte × dimensions
Product Quantization:  ~32-64 bytes total
Binary:                dimensions/8 bytes
```

## Templates and detailed worked examples

完整的範本庫和詳細的實作範例放在 `references/details.md`。需要具體範本時，再去讀那個檔案。

## Best Practices

### Do's

- **Benchmark with real queries** - 合成資料不一定能代表 production
- **Monitor recall continuously** - 會隨資料漂移（data drift）而退化
- **Start with defaults** - 需要時才調整
- **Use quantization** - 能大幅節省記憶體
- **Consider tiered storage** - 區分熱資料與冷資料

### Don'ts

- **Don't over-optimize early** - 先 profile
- **Don't ignore build time** - 更新索引是有成本的
- **Don't forget reindexing** - 要規劃維護
- **Don't skip warming** - 冷索引很慢
