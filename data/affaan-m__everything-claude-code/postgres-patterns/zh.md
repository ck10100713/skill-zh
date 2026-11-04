---
name: postgres-patterns
description: PostgreSQL 資料庫模式，涵蓋查詢最佳化、schema 設計、索引和安全，根據 Supabase 的最佳實踐。設計 PostgreSQL schema、索引或 RLS policy，或查詢太慢時使用。
metadata:
  origin: ECC
---

# PostgreSQL 模式

PostgreSQL 最佳實踐的速查表。要更詳細的指引，請用 `database-reviewer` agent。

## 何時啟用

- 撰寫 SQL 查詢或 migration
- 設計資料庫 schema
- 排查慢查詢
- 實作 Row Level Security
- 設定 connection pooling

## 速查

### 索引速查表

| 查詢模式 | 索引類型 | 範例 |
|--------------|------------|---------|
| `WHERE col = value` | B-tree（預設） | `CREATE INDEX idx ON t (col)` |
| `WHERE col > value` | B-tree | `CREATE INDEX idx ON t (col)` |
| `WHERE a = x AND b > y` | Composite | `CREATE INDEX idx ON t (a, b)` |
| `WHERE jsonb @> '{}'` | GIN | `CREATE INDEX idx ON t USING gin (col)` |
| `WHERE tsv @@ query` | GIN | `CREATE INDEX idx ON t USING gin (col)` |
| 時間序列範圍 | BRIN | `CREATE INDEX idx ON t USING brin (col)` |

### 資料型別速查

| 用途 | 正確型別 | 避免 |
|----------|-------------|-------|
| ID | `bigint` | `int`、隨機 UUID |
| 字串 | `text` | `varchar(255)` |
| 時間戳記 | `timestamptz` | `timestamp` |
| 金額 | `numeric(10,2)` | `float` |
| 旗標 | `boolean` | `varchar`、`int` |

### 常見模式

**Composite Index 的順序：**
```sql
-- 等值比較的欄位放前面，範圍比較的欄位放後面
CREATE INDEX idx ON orders (status, created_at);
-- 適用於：WHERE status = 'pending' AND created_at > '2024-01-01'
```

**Covering Index：**
```sql
CREATE INDEX idx ON users (email) INCLUDE (name, created_at);
-- SELECT email, name, created_at 時可以避免回表查詢
```

**Partial Index：**
```sql
CREATE INDEX idx ON users (email) WHERE deleted_at IS NULL;
-- 索引比較小，只包含有效的使用者
```

**RLS Policy（最佳化版）：**
```sql
CREATE POLICY policy ON orders
  USING ((SELECT auth.uid()) = user_id);  -- 要包在 SELECT 裡！
```

**UPSERT：**
```sql
INSERT INTO settings (user_id, key, value)
VALUES (123, 'theme', 'dark')
ON CONFLICT (user_id, key)
DO UPDATE SET value = EXCLUDED.value;
```

**Cursor 分頁：**
```sql
SELECT * FROM products WHERE id > $last_id ORDER BY id LIMIT 20;
-- O(1)，相較之下 OFFSET 是 O(n)
```

**佇列處理：**
```sql
UPDATE jobs SET status = 'processing'
WHERE id = (
  SELECT id FROM jobs WHERE status = 'pending'
  ORDER BY created_at LIMIT 1
  FOR UPDATE SKIP LOCKED
) RETURNING *;
```

### 反模式偵測

```sql
-- 找出沒有索引的外鍵
SELECT conrelid::regclass, a.attname
FROM pg_constraint c
JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
WHERE c.contype = 'f'
  AND NOT EXISTS (
    SELECT 1 FROM pg_index i
    WHERE i.indrelid = c.conrelid AND a.attnum = ANY(i.indkey)
  );

-- 找出慢查詢
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC;

-- 檢查 table bloat
SELECT relname, n_dead_tup, last_vacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

### 設定範本

```sql
-- 連線上限（依 RAM 調整）
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET work_mem = '8MB';

-- Timeout
ALTER SYSTEM SET idle_in_transaction_session_timeout = '30s';
ALTER SYSTEM SET statement_timeout = '30s';

-- 監控
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 安全預設值
REVOKE ALL ON SCHEMA public FROM public;

SELECT pg_reload_conf();
```

## 相關

- Agent：`database-reviewer` - 完整的資料庫 review 流程
- Skill：`clickhouse-io` - ClickHouse 分析模式
- Skill：`backend-patterns` - API 與後端模式

---

*根據 Supabase Agent Skills（致謝：Supabase 團隊）(MIT License)*
