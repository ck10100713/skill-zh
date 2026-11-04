---
name: sql-queries
description: 在所有主要資料倉儲方言（Snowflake、BigQuery、Databricks、PostgreSQL 等）寫出正確又有效率的 SQL。適用於撰寫查詢、優化慢速 SQL、在不同方言之間轉換，或用 CTE、window function 或聚合函式建構複雜的分析查詢。
user-invocable: false
---

# SQL 查詢 Skill

在所有主要資料倉儲方言中，寫出正確、有效率、好讀的 SQL。

## 各方言參考

### PostgreSQL（含 Aurora、RDS、Supabase、Neon）

**日期／時間：**
```sql
-- 目前日期／時間
CURRENT_DATE, CURRENT_TIMESTAMP, NOW()

-- 日期運算
date_column + INTERVAL '7 days'
date_column - INTERVAL '1 month'

-- 截斷到某個期間
DATE_TRUNC('month', created_at)

-- 取出部分
EXTRACT(YEAR FROM created_at)
EXTRACT(DOW FROM created_at)  -- 0=Sunday

-- 格式化
TO_CHAR(created_at, 'YYYY-MM-DD')
```

**字串函式：**
```sql
-- 串接
first_name || ' ' || last_name
CONCAT(first_name, ' ', last_name)

-- 模式比對
column ILIKE '%pattern%'  -- 不分大小寫
column ~ '^regex_pattern$'  -- regex

-- 字串處理
LEFT(str, n), RIGHT(str, n)
SPLIT_PART(str, delimiter, position)
REGEXP_REPLACE(str, pattern, replacement)
```

**陣列與 JSON：**
```sql
-- JSON 存取
data->>'key'  -- text
data->'nested'->'key'  -- json
data#>>'{path,to,key}'  -- 巢狀 text

-- 陣列操作
ARRAY_AGG(column)
ANY(array_column)
array_column @> ARRAY['value']
```

**效能提示：**
- 用 `EXPLAIN ANALYZE` 剖析查詢
- 在常被過濾／join 的欄位建立索引
- 相關子查詢用 `EXISTS` 而不是 `IN`
- 常見過濾條件用 partial index
- 並行存取時用 connection pooling

---

### Snowflake

**日期／時間：**
```sql
-- 目前日期／時間
CURRENT_DATE(), CURRENT_TIMESTAMP(), SYSDATE()

-- 日期運算
DATEADD(day, 7, date_column)
DATEDIFF(day, start_date, end_date)

-- 截斷到某個期間
DATE_TRUNC('month', created_at)

-- 取出部分
YEAR(created_at), MONTH(created_at), DAY(created_at)
DAYOFWEEK(created_at)

-- 格式化
TO_CHAR(created_at, 'YYYY-MM-DD')
```

**字串函式：**
```sql
-- 預設不分大小寫（視 collation 而定）
column ILIKE '%pattern%'
REGEXP_LIKE(column, 'pattern')

-- 解析 JSON
column:key::string  -- VARIANT 用點記法
PARSE_JSON('{"key": "value"}')
GET_PATH(variant_col, 'path.to.key')

-- 展開陣列／物件
SELECT f.value FROM table, LATERAL FLATTEN(input => array_col) f
```

**半結構化資料：**
```sql
-- VARIANT 型別存取
data:customer:name::STRING
data:items[0]:price::NUMBER

-- 展開巢狀結構
SELECT
    t.id,
    item.value:name::STRING as item_name,
    item.value:qty::NUMBER as quantity
FROM my_table t,
LATERAL FLATTEN(input => t.data:items) item
```

**效能提示：**
- 大型資料表用 clustering key（不是傳統索引）
- 過濾 clustering key 欄位，才能做 partition pruning
- 依查詢複雜度設定適當的 warehouse 大小
- 用 `RESULT_SCAN(LAST_QUERY_ID())` 避免重跑昂貴的查詢
- staging／暫存資料用 transient table

---

### BigQuery（Google Cloud）

**日期／時間：**
```sql
-- 目前日期／時間
CURRENT_DATE(), CURRENT_TIMESTAMP()

-- 日期運算
DATE_ADD(date_column, INTERVAL 7 DAY)
DATE_SUB(date_column, INTERVAL 1 MONTH)
DATE_DIFF(end_date, start_date, DAY)
TIMESTAMP_DIFF(end_ts, start_ts, HOUR)

-- 截斷到某個期間
DATE_TRUNC(created_at, MONTH)
TIMESTAMP_TRUNC(created_at, HOUR)

-- 取出部分
EXTRACT(YEAR FROM created_at)
EXTRACT(DAYOFWEEK FROM created_at)  -- 1=Sunday

-- 格式化
FORMAT_DATE('%Y-%m-%d', date_column)
FORMAT_TIMESTAMP('%Y-%m-%d %H:%M:%S', ts_column)
```

**字串函式：**
```sql
-- 沒有 ILIKE，用 LOWER()
LOWER(column) LIKE '%pattern%'
REGEXP_CONTAINS(column, r'pattern')
REGEXP_EXTRACT(column, r'pattern')

-- 字串處理
SPLIT(str, delimiter)  -- 回傳 ARRAY
ARRAY_TO_STRING(array, delimiter)
```

**陣列與 struct：**
```sql
-- 陣列操作
ARRAY_AGG(column)
UNNEST(array_column)
ARRAY_LENGTH(array_column)
value IN UNNEST(array_column)

-- Struct 存取
struct_column.field_name
```

**效能提示：**
- 一定要過濾 partition 欄位（通常是日期），減少掃描的位元組數
- 在 partition 內，對常被過濾的欄位用 clustering
- 大規模基數估算用 `APPROX_COUNT_DISTINCT()`
- 避免 `SELECT *`：計費是依掃描的位元組數
- 參數化腳本用 `DECLARE` 和 `SET`
- 執行大型查詢之前，先用 dry run 預覽查詢成本

---

### Redshift（Amazon）

**日期／時間：**
```sql
-- 目前日期／時間
CURRENT_DATE, GETDATE(), SYSDATE

-- 日期運算
DATEADD(day, 7, date_column)
DATEDIFF(day, start_date, end_date)

-- 截斷到某個期間
DATE_TRUNC('month', created_at)

-- 取出部分
EXTRACT(YEAR FROM created_at)
DATE_PART('dow', created_at)
```

**字串函式：**
```sql
-- 不分大小寫
column ILIKE '%pattern%'
REGEXP_INSTR(column, 'pattern') > 0

-- 字串處理
SPLIT_PART(str, delimiter, position)
LISTAGG(column, ', ') WITHIN GROUP (ORDER BY column)
```

**效能提示：**
- 設計 distribution key 讓 join 在同一節點上完成（DISTKEY）
- 常被過濾的欄位用 sort key（SORTKEY）
- 用 `EXPLAIN` 檢查查詢計畫
- 避免跨節點的資料搬移（注意 DS_BCAST 和 DS_DIST）
- 定期執行 `ANALYZE` 和 `VACUUM`
- 用 late-binding view 讓 schema 更有彈性

---

### Databricks SQL

**日期／時間：**
```sql
-- 目前日期／時間
CURRENT_DATE(), CURRENT_TIMESTAMP()

-- 日期運算
DATE_ADD(date_column, 7)
DATEDIFF(end_date, start_date)
ADD_MONTHS(date_column, 1)

-- 截斷到某個期間
DATE_TRUNC('MONTH', created_at)
TRUNC(date_column, 'MM')

-- 取出部分
YEAR(created_at), MONTH(created_at)
DAYOFWEEK(created_at)
```

**Delta Lake 功能：**
```sql
-- 時間旅行
SELECT * FROM my_table TIMESTAMP AS OF '2024-01-15'
SELECT * FROM my_table VERSION AS OF 42

-- 查看歷史
DESCRIBE HISTORY my_table

-- Merge（upsert）
MERGE INTO target USING source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
```

**效能提示：**
- 用 Delta Lake 的 `OPTIMIZE` 和 `ZORDER` 提升查詢效能
- 運算密集的查詢善用 Photon 引擎
- 常存取的資料集用 `CACHE TABLE`
- 依基數低的日期欄位做 partition

---

## 常見 SQL 模式

### Window Function

```sql
-- 排名
ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC)
RANK() OVER (PARTITION BY category ORDER BY revenue DESC)
DENSE_RANK() OVER (ORDER BY score DESC)

-- 累計總和／移動平均
SUM(revenue) OVER (ORDER BY date_col ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as running_total
AVG(revenue) OVER (ORDER BY date_col ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as moving_avg_7d

-- Lag / Lead
LAG(value, 1) OVER (PARTITION BY entity ORDER BY date_col) as prev_value
LEAD(value, 1) OVER (PARTITION BY entity ORDER BY date_col) as next_value

-- 第一個／最後一個值
FIRST_VALUE(status) OVER (PARTITION BY user_id ORDER BY created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
LAST_VALUE(status) OVER (PARTITION BY user_id ORDER BY created_at ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)

-- 佔總數的百分比
revenue / SUM(revenue) OVER () as pct_of_total
revenue / SUM(revenue) OVER (PARTITION BY category) as pct_of_category
```

### 用 CTE 提升可讀性

```sql
WITH
-- 步驟 1：定義基礎母體
base_users AS (
    SELECT user_id, created_at, plan_type
    FROM users
    WHERE created_at >= DATE '2024-01-01'
      AND status = 'active'
),

-- 步驟 2：計算使用者層級的指標
user_metrics AS (
    SELECT
        u.user_id,
        u.plan_type,
        COUNT(DISTINCT e.session_id) as session_count,
        SUM(e.revenue) as total_revenue
    FROM base_users u
    LEFT JOIN events e ON u.user_id = e.user_id
    GROUP BY u.user_id, u.plan_type
),

-- 步驟 3：聚合到摘要層級
summary AS (
    SELECT
        plan_type,
        COUNT(*) as user_count,
        AVG(session_count) as avg_sessions,
        SUM(total_revenue) as total_revenue
    FROM user_metrics
    GROUP BY plan_type
)

SELECT * FROM summary ORDER BY total_revenue DESC;
```

### 世代留存（Cohort Retention）

```sql
WITH cohorts AS (
    SELECT
        user_id,
        DATE_TRUNC('month', first_activity_date) as cohort_month
    FROM users
),
activity AS (
    SELECT
        user_id,
        DATE_TRUNC('month', activity_date) as activity_month
    FROM user_activity
)
SELECT
    c.cohort_month,
    COUNT(DISTINCT c.user_id) as cohort_size,
    COUNT(DISTINCT CASE
        WHEN a.activity_month = c.cohort_month THEN a.user_id
    END) as month_0,
    COUNT(DISTINCT CASE
        WHEN a.activity_month = c.cohort_month + INTERVAL '1 month' THEN a.user_id
    END) as month_1,
    COUNT(DISTINCT CASE
        WHEN a.activity_month = c.cohort_month + INTERVAL '3 months' THEN a.user_id
    END) as month_3
FROM cohorts c
LEFT JOIN activity a ON c.user_id = a.user_id
GROUP BY c.cohort_month
ORDER BY c.cohort_month;
```

### 漏斗分析

```sql
WITH funnel AS (
    SELECT
        user_id,
        MAX(CASE WHEN event = 'page_view' THEN 1 ELSE 0 END) as step_1_view,
        MAX(CASE WHEN event = 'signup_start' THEN 1 ELSE 0 END) as step_2_start,
        MAX(CASE WHEN event = 'signup_complete' THEN 1 ELSE 0 END) as step_3_complete,
        MAX(CASE WHEN event = 'first_purchase' THEN 1 ELSE 0 END) as step_4_purchase
    FROM events
    WHERE event_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY user_id
)
SELECT
    COUNT(*) as total_users,
    SUM(step_1_view) as viewed,
    SUM(step_2_start) as started_signup,
    SUM(step_3_complete) as completed_signup,
    SUM(step_4_purchase) as purchased,
    ROUND(100.0 * SUM(step_2_start) / NULLIF(SUM(step_1_view), 0), 1) as view_to_start_pct,
    ROUND(100.0 * SUM(step_3_complete) / NULLIF(SUM(step_2_start), 0), 1) as start_to_complete_pct,
    ROUND(100.0 * SUM(step_4_purchase) / NULLIF(SUM(step_3_complete), 0), 1) as complete_to_purchase_pct
FROM funnel;
```

### 去重

```sql
-- 每個 key 只保留最新的一筆紀錄
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY entity_id
            ORDER BY updated_at DESC
        ) as rn
    FROM source_table
)
SELECT * FROM ranked WHERE rn = 1;
```

## 錯誤處理與除錯

查詢失敗時：

1. **語法錯誤**：檢查方言專屬的語法（例如 BigQuery 沒有 `ILIKE`，`SAFE_DIVIDE` 只有 BigQuery 有）
2. **找不到欄位**：對照 schema 驗證欄位名稱，檢查拼字、大小寫敏感度（PostgreSQL 對加引號的識別字是區分大小寫的）
3. **型別不符**：比較不同型別時要明確轉型（`CAST(col AS DATE)`、`col::DATE`）
4. **除以零**：用 `NULLIF(denominator, 0)` 或方言專屬的安全除法
5. **欄位有歧義**：JOIN 時一律用 table alias 限定欄位名稱
6. **Group by 錯誤**：所有沒有聚合的欄位都必須放進 GROUP BY（BigQuery 例外，它允許用 alias 分組）
