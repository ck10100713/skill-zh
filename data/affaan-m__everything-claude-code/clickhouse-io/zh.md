---
name: clickhouse-io
description: ClickHouse 資料庫模式、查詢最佳化、分析，以及高效能分析型工作負載的資料工程最佳實務。適用於撰寫 ClickHouse schema 或查詢，或是分析查詢太慢的時候。
metadata:
  origin: ECC
---

# ClickHouse Analytics Patterns

針對高效能分析與資料工程的 ClickHouse 專屬模式。

## When to Activate

- 設計 ClickHouse 資料表 schema（選擇 MergeTree 引擎）
- 撰寫分析查詢（聚合、window function、join）
- 最佳化查詢效能（partition pruning、projection、materialized view）
- 匯入大量資料（批次 insert、Kafka 整合）
- 為了分析，從 PostgreSQL/MySQL migration 到 ClickHouse
- 實作即時儀表板或時間序列分析

## Overview

ClickHouse 是用於線上分析處理（OLAP）的欄式資料庫管理系統（DBMS）。它針對大型資料集上的快速分析查詢做了最佳化。

**主要特色：**
- 欄式儲存
- 資料壓縮
- 平行查詢執行
- 分散式查詢
- 即時分析

## Table Design Patterns

### MergeTree Engine (Most Common)

```sql
CREATE TABLE markets_analytics (
    date Date,
    market_id String,
    market_name String,
    volume UInt64,
    trades UInt32,
    unique_traders UInt32,
    avg_trade_size Float64,
    created_at DateTime
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (date, market_id)
SETTINGS index_granularity = 8192;
```

### ReplacingMergeTree (Deduplication)

```sql
-- 用在可能有重複資料的情況（例如來自多個來源）
CREATE TABLE user_events (
    event_id String,
    user_id String,
    event_type String,
    timestamp DateTime,
    properties String
) ENGINE = ReplacingMergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (user_id, event_id, timestamp)
PRIMARY KEY (user_id, event_id);
```

### AggregatingMergeTree (Pre-aggregation)

```sql
-- 用來維護聚合後的指標
CREATE TABLE market_stats_hourly (
    hour DateTime,
    market_id String,
    total_volume AggregateFunction(sum, UInt64),
    total_trades AggregateFunction(count, UInt32),
    unique_users AggregateFunction(uniq, String)
) ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (hour, market_id);

-- 查詢聚合後的資料
SELECT
    hour,
    market_id,
    sumMerge(total_volume) AS volume,
    countMerge(total_trades) AS trades,
    uniqMerge(unique_users) AS users
FROM market_stats_hourly
WHERE hour >= toStartOfHour(now() - INTERVAL 24 HOUR)
GROUP BY hour, market_id
ORDER BY hour DESC;
```

## Query Optimization Patterns

### Efficient Filtering

```sql
-- PASS: GOOD: 先用有索引的欄位
SELECT *
FROM markets_analytics
WHERE date >= '2025-01-01'
  AND market_id = 'market-123'
  AND volume > 1000
ORDER BY date DESC
LIMIT 100;

-- FAIL: BAD: 先過濾沒有索引的欄位
SELECT *
FROM markets_analytics
WHERE volume > 1000
  AND market_name LIKE '%election%'
  AND date >= '2025-01-01';
```

### Aggregations

```sql
-- PASS: GOOD: 使用 ClickHouse 專屬的聚合函式
SELECT
    toStartOfDay(created_at) AS day,
    market_id,
    sum(volume) AS total_volume,
    count() AS total_trades,
    uniq(trader_id) AS unique_traders,
    avg(trade_size) AS avg_size
FROM trades
WHERE created_at >= today() - INTERVAL 7 DAY
GROUP BY day, market_id
ORDER BY day DESC, total_volume DESC;

-- PASS: 百分位數用 quantile（比 percentile 更有效率）
SELECT
    quantile(0.50)(trade_size) AS median,
    quantile(0.95)(trade_size) AS p95,
    quantile(0.99)(trade_size) AS p99
FROM trades
WHERE created_at >= now() - INTERVAL 1 HOUR;
```

### Window Functions

```sql
-- 計算累計總和
SELECT
    date,
    market_id,
    volume,
    sum(volume) OVER (
        PARTITION BY market_id
        ORDER BY date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_volume
FROM markets_analytics
WHERE date >= today() - INTERVAL 30 DAY
ORDER BY market_id, date;
```

## Data Insertion Patterns

### Bulk Insert (Recommended)

```typescript
import { createClient } from '@clickhouse/client'

const clickhouse = createClient({
  url: process.env.CLICKHOUSE_URL ?? 'http://localhost:8123',
  username: process.env.CLICKHOUSE_USER,
  password: process.env.CLICKHOUSE_PASSWORD
})

// PASS: 批次 insert（有效率）
async function bulkInsertTrades(trades: Trade[]) {
  await clickhouse.insert({
    table: 'trades',
    values: trades.map(trade => ({
      id: trade.id,
      market_id: trade.market_id,
      user_id: trade.user_id,
      amount: trade.amount,
      timestamp: trade.timestamp.toISOString()
    })),
    format: 'JSONEachRow'
  })
}

// FAIL: 逐筆 insert（很慢）
async function insertTrade(trade: Trade) {
  // 不要在迴圈裡這樣做！
  await clickhouse.insert({
    table: 'trades',
    values: [{
      id: trade.id,
      market_id: trade.market_id,
      user_id: trade.user_id,
      amount: trade.amount,
      timestamp: trade.timestamp.toISOString()
    }],
    format: 'JSONEachRow'
  })
}
```

### Streaming Insert

```typescript
// 用於持續匯入資料
import { Readable } from 'node:stream'

async function streamInserts(dataSource: AsyncIterable<Record<string, unknown>>) {
  await clickhouse.insert({
    table: 'trades',
    values: Readable.from(dataSource, { objectMode: true }),
    format: 'JSONEachRow'
  })
}
```

## Materialized Views

### Real-time Aggregations

```sql
-- 建立每小時統計的 materialized view
CREATE MATERIALIZED VIEW market_stats_hourly_mv
TO market_stats_hourly
AS SELECT
    toStartOfHour(timestamp) AS hour,
    market_id,
    sumState(amount) AS total_volume,
    countState() AS total_trades,
    uniqState(user_id) AS unique_users
FROM trades
GROUP BY hour, market_id;

-- 查詢 materialized view
SELECT
    hour,
    market_id,
    sumMerge(total_volume) AS volume,
    countMerge(total_trades) AS trades,
    uniqMerge(unique_users) AS users
FROM market_stats_hourly
WHERE hour >= now() - INTERVAL 24 HOUR
GROUP BY hour, market_id;
```

## Performance Monitoring

### Query Performance

```sql
-- 檢查慢查詢
SELECT
    query_id,
    user,
    query,
    query_duration_ms,
    read_rows,
    read_bytes,
    memory_usage
FROM system.query_log
WHERE type = 'QueryFinish'
  AND query_duration_ms > 1000
  AND event_time >= now() - INTERVAL 1 HOUR
ORDER BY query_duration_ms DESC
LIMIT 10;
```

### Table Statistics

```sql
-- 檢查資料表大小
SELECT
    database,
    table,
    formatReadableSize(sum(bytes)) AS size,
    sum(rows) AS rows,
    max(modification_time) AS latest_modification
FROM system.parts
WHERE active
GROUP BY database, table
ORDER BY sum(bytes) DESC;
```

## Common Analytics Queries

### Time Series Analysis

```sql
-- 每日活躍使用者
SELECT
    toDate(timestamp) AS date,
    uniq(user_id) AS daily_active_users
FROM events
WHERE timestamp >= today() - INTERVAL 30 DAY
GROUP BY date
ORDER BY date;

-- 留存分析
SELECT
    signup_date,
    countIf(days_since_signup = 0) AS day_0,
    countIf(days_since_signup = 1) AS day_1,
    countIf(days_since_signup = 7) AS day_7,
    countIf(days_since_signup = 30) AS day_30
FROM (
    SELECT
        user_id,
        min(toDate(timestamp)) AS signup_date,
        toDate(timestamp) AS activity_date,
        dateDiff('day', signup_date, activity_date) AS days_since_signup
    FROM events
    GROUP BY user_id, activity_date
)
GROUP BY signup_date
ORDER BY signup_date DESC;
```

### Funnel Analysis

```sql
-- 轉換漏斗
SELECT
    countIf(step = 'viewed_market') AS viewed,
    countIf(step = 'clicked_trade') AS clicked,
    countIf(step = 'completed_trade') AS completed,
    round(clicked / viewed * 100, 2) AS view_to_click_rate,
    round(completed / clicked * 100, 2) AS click_to_completion_rate
FROM (
    SELECT
        user_id,
        session_id,
        event_type AS step
    FROM events
    WHERE event_date = today()
)
GROUP BY session_id;
```

### Cohort Analysis

```sql
-- 依註冊月份分的使用者世代
SELECT
    toStartOfMonth(signup_date) AS cohort,
    toStartOfMonth(activity_date) AS month,
    dateDiff('month', cohort, month) AS months_since_signup,
    count(DISTINCT user_id) AS active_users
FROM (
    SELECT
        user_id,
        min(toDate(timestamp)) OVER (PARTITION BY user_id) AS signup_date,
        toDate(timestamp) AS activity_date
    FROM events
)
GROUP BY cohort, month, months_since_signup
ORDER BY cohort, months_since_signup;
```

## Data Pipeline Patterns

### ETL Pattern

```typescript
// Extract, Transform, Load
async function etlPipeline() {
  // 1. 從來源擷取
  const rawData = await extractFromPostgres()

  // 2. 轉換
  const transformed = rawData.map(row => ({
    date: new Date(row.created_at).toISOString().split('T')[0],
    market_id: row.market_slug,
    volume: parseFloat(row.total_volume),
    trades: parseInt(row.trade_count)
  }))

  // 3. 載入到 ClickHouse
  await bulkInsertToClickHouse(transformed)
}

// 定期執行
setInterval(etlPipeline, 60 * 60 * 1000)  // 每小時
```

### Change Data Capture (CDC)

```typescript
// 監聽 PostgreSQL 的變更並同步到 ClickHouse
import { Client } from 'pg'

const pgClient = new Client({ connectionString: process.env.DATABASE_URL })

pgClient.query('LISTEN market_updates')

pgClient.on('notification', async (msg) => {
  const update = JSON.parse(msg.payload)

  await clickhouse.insert({
    table: 'market_updates',
    values: [
      {
        market_id: update.id,
        event_type: update.operation,  // INSERT, UPDATE, DELETE
        timestamp: new Date(),
        data: JSON.stringify(update.new_data)
      }
    ],
    format: 'JSONEachRow'
  })
})
```

## Best Practices

### 1. Partitioning Strategy
- 依時間分區（通常是月或日）
- 避免分區太多（會影響效能）
- 分區鍵用 DATE 型別

### 2. Ordering Key
- 最常被過濾的欄位放最前面
- 考慮基數（高基數放前面）
- 排序會影響壓縮

### 3. Data Types
- 用最小的合適型別（UInt32 vs UInt64）
- 重複出現的字串用 LowCardinality
- 類別資料用 Enum

### 4. Avoid
- SELECT *（要指定欄位）
- FINAL（改成在查詢前先合併資料）
- 太多 JOIN（分析用途要去正規化）
- 小量又頻繁的 insert（改成批次）

### 5. Monitoring
- 追蹤查詢效能
- 監控磁碟用量
- 檢查 merge 操作
- 檢視慢查詢日誌

**記住**：ClickHouse 擅長分析型工作負載。依照你的查詢模式設計資料表、批次 insert，並善用 materialized view 做即時聚合。
