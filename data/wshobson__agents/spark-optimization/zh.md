---
name: spark-optimization
description: 用 partitioning、快取、shuffle 優化和記憶體調校來優化 Apache Spark 任務。在提升 Spark 效能、除錯執行很慢的任務，或擴展資料處理 pipeline 時使用。
---

# Apache Spark Optimization

優化 Apache Spark 任務的正式環境模式，包含 partitioning 策略、記憶體管理、shuffle 優化和效能調校。

## When to Use This Skill

- 優化執行很慢的 Spark 任務
- 調整記憶體和 executor 設定
- 實作有效率的 partitioning 策略
- 除錯 Spark 的效能問題
- 為大型資料集擴展 Spark pipeline
- 減少 shuffle 和資料傾斜（data skew）

## Core Concepts

### 1. Spark Execution Model

```
Driver Program
    ↓
Job (triggered by action)
    ↓
Stages (separated by shuffles)
    ↓
Tasks (one per partition)
```

### 2. Key Performance Factors

| Factor            | Impact                | Solution                      |
| ----------------- | --------------------- | ----------------------------- |
| **Shuffle**       | 網路 I/O、磁碟 I/O | 盡量減少 wide transformation |
| **Data Skew**     | task 耗時不均  | Salting、broadcast join      |
| **Serialization** | CPU 開銷          | 用 Kryo、columnar 格式    |
| **Memory**        | GC 壓力、spill   | 調整 executor 記憶體          |
| **Partitions**    | 平行度           | 把 partition 大小調整到合適 |

## Quick Start

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# Create optimized Spark session
spark = (SparkSession.builder
    .appName("OptimizedJob")
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
    .config("spark.sql.adaptive.skewJoin.enabled", "true")
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    .config("spark.sql.shuffle.partitions", "200")
    .getOrCreate())

# Read with optimized settings
df = (spark.read
    .format("parquet")
    .option("mergeSchema", "false")
    .load("s3://bucket/data/"))

# Efficient transformations
result = (df
    .filter(F.col("date") >= "2024-01-01")
    .select("id", "amount", "category")
    .groupBy("category")
    .agg(F.sum("amount").alias("total")))

result.write.mode("overwrite").parquet("s3://bucket/output/")
```

## Detailed patterns and worked examples

詳細的 pattern 文件放在 `references/details.md`。上面這層導覽不夠用的時候，再去讀那個檔案。

## Best Practices

### Do's

- **啟用 AQE** - Adaptive query execution 能處理很多問題
- **用 Parquet/Delta** - 有壓縮的 columnar 格式
- **Broadcast 小表** - 小表 join 時避免 shuffle
- **監控 Spark UI** - 檢查 skew、spill、GC
- **把 partition 大小調整到合適** - 每個 partition 128MB - 256MB

### Don'ts

- **不要 collect 大量資料** - 讓資料保持分散
- **不要不必要地用 UDF** - 用內建函式
- **不要過度快取** - 記憶體是有限的
- **不要忽略資料傾斜** - 它會主導整個任務的耗時
- **不要用 `.count()` 來判斷是否存在** - 用 `.take(1)` 或 `.isEmpty()`
