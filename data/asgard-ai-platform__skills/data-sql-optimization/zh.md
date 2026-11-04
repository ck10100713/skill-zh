---
name: "data-sql-optimization"
description: "用 EXPLAIN 分析、索引策略和常見反模式的修正，最佳化 SQL 查詢效能。當使用者需要加速慢查詢、設計索引、修正 N+1 問題，或最佳化資料庫效能時使用。就算使用者只說「這個查詢很慢」、「幫我最佳化資料庫」、「需要建哪些索引」或「我們的 dashboard 要 30 秒才載入完」也要用。"
metadata:
  category: "WP-04 數據分析"
  tags: ["data-analysis", "sql", "database", "performance"]
---

# SQL 查詢最佳化

## 框架

```
IRON LAW: Measure Before Optimizing

NEVER guess which query is slow or why. Use EXPLAIN (EXPLAIN ANALYZE in
PostgreSQL) to see the actual execution plan. The database's plan often
differs from what you expect — a query you think is efficient may do
a full table scan, and a complex-looking query may use an index perfectly.

Measure → identify bottleneck → fix → measure again.
```

### 讀懂 EXPLAIN 輸出

EXPLAIN ANALYZE（PostgreSQL）中的關鍵指標：
| 指標 | 代表什麼 | 警訊 |
|--------|-------------|----------|
| **Seq Scan** | 全表掃描 | 出現在大型資料表（>10 萬列） |
| **Index Scan** | 使用了索引 | 有篩選條件的查詢本來就該這樣 |
| **Nested Loop** | Join 方式（逐列處理） | 大型資料表又沒有索引 |
| **Hash Join** | Join 方式（雜湊表） | 對較大的資料表來說是正常的 |
| **Sort** | 對結果排序 | 大型結果集卻沒有索引支援 |
| **Actual Time** | 這個步驟花的毫秒數 | 互相比較就能找出瓶頸 |
| **Rows** | 實際處理的列數 vs 估計值 | 落差很大 = 統計資料過時 |

### 索引策略

| 何時建索引 | 索引類型 | 範例 |
|--------------|-----------|---------|
| WHERE 條件的欄位 | B-Tree（預設） | `CREATE INDEX idx_user_email ON users(email)` |
| JOIN 的欄位 | B-Tree | `CREATE INDEX idx_order_user ON orders(user_id)` |
| 複合篩選 | 複合索引 | `CREATE INDEX idx_order_status_date ON orders(status, created_at)` |
| 文字搜尋 | GIN / 全文檢索 | `CREATE INDEX idx_product_name_gin ON products USING gin(name gin_trgm_ops)` |
| 範圍查詢 | B-Tree | 搭配 `BETWEEN`、`>`、`<` 使用的欄位 |

**複合索引的欄位順序很重要**：選擇性最高（基數最大）的欄位放前面。如果你永遠先用 status 篩選，`INDEX(status, date)` 就不錯。如果你永遠先用日期範圍篩選，`INDEX(date, status)` 會更好。

### 常見反模式

| 反模式 | 問題 | 修正 |
|-------------|---------|-----|
| `SELECT *` | 讀取所有欄位，無法做 index-only scan | 只 select 需要的欄位 |
| WHERE 裡的子查詢 | 每一列都重新執行一次 | 改寫成 JOIN 或 CTE |
| WHERE 裡的 `OR` | 讓索引失效 | 改寫成 UNION 或拆成不同查詢 |
| 對有索引的欄位套用函式 | `WHERE YEAR(date) = 2024` 會繞過索引 | `WHERE date >= '2024-01-01' AND date < '2025-01-01'` |
| N+1 查詢 | 1 個查詢取清單 + N 個查詢取細節 | JOIN，或用 `IN` 做批次查詢 |
| 沒有分頁 | 只顯示 20 筆卻撈了全部的列 | `LIMIT` + `OFFSET` 或 keyset 分頁 |
| 隱式型別轉換 | `WHERE id = '123'`（字串 vs 整數） | 用正確的型別：`WHERE id = 123` |

### 最佳化流程

1. **找出慢查詢**：資料庫的慢查詢日誌（pg_stat_statements、MySQL slow log）
2. **對最慢的跑 EXPLAIN ANALYZE**
3. **找出瓶頸**：大型資料表上的 Seq Scan？缺索引？昂貴的排序？
4. **套用修正**：加索引、改寫查詢，或重構 schema
5. **驗證**：再跑一次 EXPLAIN ANALYZE，確認有改善
6. **監控**：確認這個修正沒有拖慢其他查詢

### 分區（大型資料表）

當資料表超過數百萬列：
| 策略 | 運作方式 | 最適合 |
|----------|-------------|----------|
| **Range 分區** | 依日期範圍切分（每月、每年） | 時間序列資料、日誌 |
| **Hash 分區** | 依某欄位的雜湊值分散 | 平均分布、高吞吐量 |
| **List 分區** | 依特定的值切分 | 多租戶、依狀態分 |

## 輸出格式

```markdown
# Query Optimization: {Context}

## Slow Query
```sql
{the original slow query}
```
- Execution time: {current ms}
- Rows scanned: {N}
- Problem: {what EXPLAIN revealed}

## Fix Applied
{What was changed — new index, query rewrite, etc.}

## Result
- Execution time: {original ms} → {optimized ms} ({X% improvement})
- Rows scanned: {original N} → {optimized N}
```

## 常見陷阱

- **索引有寫入成本**：每次 INSERT/UPDATE 都要更新所有索引。索引過多會拖慢寫入。只替你會查詢的欄位建索引，不是全部都建。
- **統計資料可能過時**：如果 EXPLAIN 的估計值跟實際值差很多，就跑 `ANALYZE`（PostgreSQL）或 `ANALYZE TABLE`（MySQL）更新統計資料。
- **查詢快取會掩蓋問題**：查詢看起來很快可能只是因為被快取了。要在清掉快取或冷啟動的狀態下測試。
- **ORM 產生的查詢**：ORM（Django、SQLAlchemy、ActiveRecord）產生的 SQL 不一定最佳。效能關鍵的路徑，一定要檢查實際的 SQL。
- **連線池**：有時瓶頸不在查詢，而是連線的額外負擔。高併發的應用要用連線池（PgBouncer、ProxySQL）。

## 參考資料

- PostgreSQL 專屬的最佳化，見 `references/pg-optimization.md`
- CTE 與暫存表的效能比較，見 `references/cte-vs-temp.md`
