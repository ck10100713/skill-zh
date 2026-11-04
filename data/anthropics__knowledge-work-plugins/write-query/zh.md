---
name: write-query
description: 針對你的 SQL 方言，依最佳實務寫出最佳化的 SQL。當要把自然語言的資料需求翻成 SQL、建立含 join 與聚合的多重 CTE 查詢、針對大型分區資料表最佳化查詢，或是想取得 Snowflake、BigQuery、Postgres 等的方言專屬語法時使用。
argument-hint: "<description of what data you need>"
---

# /write-query - 撰寫最佳化的 SQL

> 如果看到不熟悉的 placeholder，或需要確認目前連接了哪些工具，請見 [CONNECTORS.md](../../CONNECTORS.md)。

依照自然語言的描述寫出 SQL 查詢，針對你用的 SQL 方言做最佳化，並遵循最佳實務。

## 用法

```
/write-query <description of what data you need>
```

## 工作流程

### 1. 理解需求

解析使用者的描述，找出：

- **輸出欄位**：結果應該包含哪些欄位？
- **篩選條件**：哪些條件限制了資料（時間範圍、客群、狀態）？
- **聚合**：有 GROUP BY、count、sum、average 嗎？
- **Join**：需要結合多張資料表嗎？
- **排序**：結果要怎麼排序？
- **筆數限制**：有 top-N 或取樣的需求嗎？

### 2. 確定 SQL 方言

如果還不知道使用者的 SQL 方言，就問他用哪一種：

- **PostgreSQL**（包含 Aurora、RDS、Supabase、Neon）
- **Snowflake**
- **BigQuery**（Google Cloud）
- **Redshift**（Amazon）
- **Databricks SQL**
- **MySQL**（包含 Aurora MySQL、PlanetScale）
- **SQL Server**（Microsoft）
- **DuckDB**
- **SQLite**
- **其他**（問清楚細節）

在同一個 session 裡，把方言記住，之後的查詢都沿用。

### 3. 探索 Schema（如果已連接資料倉儲）

如果已連接資料倉儲的 MCP server：

1. 依據使用者的描述搜尋相關的資料表
2. 檢查欄位名稱、型別和關聯
3. 檢查會影響效能的分區或 clustering key
4. 找找有沒有預先建好的 view 或 materialized view 可以簡化查詢

### 4. 撰寫查詢

遵循以下最佳實務：

**結構：**
- 查詢有多個邏輯步驟時，用 CTE（WITH 子句）提升可讀性
- 每個邏輯轉換或資料來源用一個 CTE
- CTE 的名稱要能說明用途（例如 `daily_signups`、`active_users`、`revenue_by_product`）

**效能：**
- 正式環境的查詢絕對不要用 `SELECT *`，只指定需要的欄位
- 越早篩選越好（把 WHERE 子句盡量往基礎資料表推）
- 有分區篩選就用（尤其是日期分區）
- 結果集很大的子查詢，優先用 `EXISTS` 而不是 `IN`
- 用適當的 JOIN 類型（該用 INNER JOIN 時不要用 LEFT JOIN）
- 能用 JOIN 或 window function 解決時，避免相關子查詢
- 小心爆炸性的 join（多對多）

**可讀性：**
- 對不明顯的邏輯加註解說明「為什麼」
- 縮排和格式要一致
- 資料表別名要有意義、又簡短（不要只用 `a`、`b`、`c`）
- 每個主要子句各佔一行

**方言專屬的最佳化：**
- 套用方言專屬的語法和函式（細節見 `sql-queries` skill）
- 使用適合該方言的日期函式、字串函式和 window 語法
- 註明任何方言專屬的效能功能（例如 Snowflake clustering、BigQuery partitioning）

### 5. 呈現查詢

提供：

1. **完整的查詢**，放在有語法標示的 SQL code block 裡
2. **簡短說明**，講解每個 CTE 或每個區塊在做什麼
3. **效能備註**（如果相關）（預期成本、分區的使用、潛在瓶頸）
4. **修改建議**：針對常見的變化該怎麼調整（不同的時間範圍、不同的粒度、額外的篩選條件）

### 6. 主動提議執行

如果已連接資料倉儲，就提議幫忙執行查詢並分析結果。如果使用者想自己跑，查詢已經可以直接複製貼上。

## 範例

**簡單的聚合：**
```
/write-query Count of orders by status for the last 30 days
```

**複雜的分析：**
```
/write-query Cohort retention analysis -- group users by their signup month, then show what percentage are still active (had at least one event) at 1, 3, 6, and 12 months after signup
```

**效能關鍵：**
```
/write-query We have a 500M row events table partitioned by date. Find the top 100 users by event count in the last 7 days with their most recent event type.
```

## 小提醒

- 一開始就說明你的 SQL 方言，就能馬上拿到正確的語法
- 如果你知道資料表名稱就附上；不知道的話，Claude 會幫你找
- 說明你需要的查詢是要冪等的（重跑也安全），還是只跑一次
- 對於會重複執行的查詢，說明是否要把日期範圍做成參數
