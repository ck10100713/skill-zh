---
name: sql-optimization-patterns
description: 精通 SQL 查詢優化、索引策略和 EXPLAIN 分析，大幅提升資料庫效能並消除慢查詢。在除錯慢查詢、設計資料庫 schema 或優化應用程式效能時使用。
---

# SQL Optimization Patterns

透過系統化的優化、適當的索引和查詢計畫分析，把緩慢的資料庫查詢變成閃電般快速的操作。

## When to Use This Skill

- 除錯執行很慢的查詢
- 設計高效能的資料庫 schema
- 優化應用程式的回應時間
- 降低資料庫負載和成本
- 為持續成長的資料集提升可擴展性
- 分析 EXPLAIN 查詢計畫
- 實作有效率的索引
- 解決 N+1 查詢問題

## Core Concepts

### 1. Query Execution Plans (EXPLAIN)

看懂 EXPLAIN 的輸出，是優化的基礎。

**PostgreSQL EXPLAIN：**

```sql
-- Basic explain
EXPLAIN SELECT * FROM users WHERE email = 'user@example.com';

-- With actual execution stats
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'user@example.com';

-- Verbose output with more details
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT u.*, o.order_total
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.created_at > NOW() - INTERVAL '30 days';
```

**要注意的關鍵指標：**

- **Seq Scan**：全表掃描（對大型資料表通常很慢）
- **Index Scan**：使用索引（好）
- **Index Only Scan**：只用索引、不碰資料表（最好）
- **Nested Loop**：join 方式（小資料集可以接受）
- **Hash Join**：join 方式（適合較大的資料集）
- **Merge Join**：join 方式（適合已排序的資料）
- **Cost**：估算的查詢成本（越低越好）
- **Rows**：估算回傳的列數
- **Actual Time**：實際的執行時間

### 2. Index Strategies

索引是最強大的優化工具。

**索引類型：**

- **B-Tree**：預設，適合等值和範圍查詢
- **Hash**：只適用於等值（=）比較
- **GIN**：全文檢索、陣列查詢、JSONB
- **GiST**：幾何資料、全文檢索
- **BRIN**：Block Range INdex，適合有關聯性的超大型資料表

```sql
-- Standard B-Tree index
CREATE INDEX idx_users_email ON users(email);

-- Composite index (order matters!)
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Partial index (index subset of rows)
CREATE INDEX idx_active_users ON users(email)
WHERE status = 'active';

-- Expression index
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

-- Covering index (include additional columns)
CREATE INDEX idx_users_email_covering ON users(email)
INCLUDE (name, created_at);

-- Full-text search index
CREATE INDEX idx_posts_search ON posts
USING GIN(to_tsvector('english', title || ' ' || body));

-- JSONB index
CREATE INDEX idx_metadata ON events USING GIN(metadata);
```

### 3. Query Optimization Patterns

**避免 SELECT \*：**

```sql
-- Bad: Fetches unnecessary columns
SELECT * FROM users WHERE id = 123;

-- Good: Fetch only what you need
SELECT id, email, name FROM users WHERE id = 123;
```

**有效率地使用 WHERE 子句：**

```sql
-- Bad: Function prevents index usage
SELECT * FROM users WHERE LOWER(email) = 'user@example.com';

-- Good: Create functional index or use exact match
CREATE INDEX idx_users_email_lower ON users(LOWER(email));
-- Then:
SELECT * FROM users WHERE LOWER(email) = 'user@example.com';

-- Or store normalized data
SELECT * FROM users WHERE email = 'user@example.com';
```

**優化 JOIN：**

```sql
-- Bad: Cartesian product then filter
SELECT u.name, o.total
FROM users u, orders o
WHERE u.id = o.user_id AND u.created_at > '2024-01-01';

-- Good: Filter before join
SELECT u.name, o.total
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.created_at > '2024-01-01';

-- Better: Filter both tables
SELECT u.name, o.total
FROM (SELECT * FROM users WHERE created_at > '2024-01-01') u
JOIN orders o ON u.id = o.user_id;
```

## Detailed patterns and worked examples

詳細的 pattern 文件放在 `references/details.md`。上面這層導覽不夠用的時候，再去讀那個檔案。

## Best Practices

1. **選擇性地建索引**：索引太多會拖慢寫入
2. **監控查詢效能**：用慢查詢 log
3. **保持統計資料最新**：定期執行 ANALYZE
4. **用適當的資料型別**：型別越小，效能越好
5. **審慎地做正規化**：在正規化和效能之間取得平衡
6. **快取常被存取的資料**：用應用程式層級的快取
7. **Connection Pooling**：重複使用資料庫連線
8. **定期維護**：VACUUM、ANALYZE、重建索引

```sql
-- Update statistics
ANALYZE users;
ANALYZE VERBOSE orders;

-- Vacuum (PostgreSQL)
VACUUM ANALYZE users;
VACUUM FULL users;  -- Reclaim space (locks table)

-- Reindex
REINDEX INDEX idx_users_email;
REINDEX TABLE users;
```

## Common Pitfalls

- **過度建索引**：每個索引都會拖慢 INSERT/UPDATE/DELETE
- **沒用到的索引**：浪費空間並拖慢寫入
- **缺少索引**：查詢很慢，全表掃描
- **隱含的型別轉換**：會讓索引失效
- **OR 條件**：無法有效使用索引
- **LIKE 以萬用字元開頭**：`LIKE '%abc'` 用不到索引
- **WHERE 裡用函式**：除非有 functional index，否則會讓索引失效

## Monitoring Queries

```sql
-- Find slow queries (PostgreSQL)
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Find missing indexes (PostgreSQL)
SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    seq_tup_read / seq_scan AS avg_seq_tup_read
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC
LIMIT 10;

-- Find unused indexes (PostgreSQL)
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```
