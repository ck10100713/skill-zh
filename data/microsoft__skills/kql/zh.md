---
name: kql
description: "KQL 語言專業知識，用來寫出正確又有效率的 Kusto Query Language 查詢。涵蓋語法陷阱、join 模式、dynamic 型別、datetime 陷阱、regex 模式、serialization、記憶體管理、結果大小控管，以及進階函式（geo、vector、graph）。只要在寫、除錯或審查 KQL 查詢就用這個 skill，連簡單的也一樣，因為陷阱那幾節能預防最常見的錯誤，那些錯誤會浪費工具呼叫，還會引發昂貴的重試連鎖。Trigger on: KQL, Kusto, ADX, Azure Data Explorer, Fabric Real-Time Intelligence, EventHouse, Log Analytics, log analysis, data exploration, time series, anomaly detection, summarize, where clause, join, extend, project, let statement, parse operator, extract function, any mention of pipe-forward query syntax."
---

# KQL Mastery

> **自己試試看**：這個 skill 裡所有標 `✅` 的範例，都可以對公開的 help cluster 執行：
> `https://help.kusto.windows.net`，資料庫 `Samples`（包含 `StormEvents`、`SimpleGraph_Nodes`/`Edges`、`nyc_taxi` 等等）。

## 1. KQL Basics

Kusto Query Language（KQL）是用來探索資料的 pipe-forward 查詢語言。它是 Azure Data Explorer（ADX）、Microsoft Fabric Real-Time Intelligence（EventHouse）、Azure Monitor Log Analytics、Microsoft Sentinel 和其他 Microsoft 資料服務的原生查詢語言。

### Pipe-forward syntax

KQL 查詢是用 `|` 分隔的一串運算子。資料從左流向右：

```kql
StormEvents                          // 從一個資料表開始
| where State == "TEXAS"             // 過濾列
| summarize count() by EventType     // 聚合
| top 5 by count_ desc              // 限制結果
```

### Query vs management commands

KQL 有兩個執行平面：

| Plane | Starts with | Examples |
|-------|-------------|----------|
| **Query** | 資料表名稱、`let`、`print`、`datatable` | `StormEvents \| where State == "TEXAS"` |
| **Management** | `.show`、`.create`、`.set`、`.drop`、`.alter` | `.show tables`、`.show table T schema` |

Management 指令後面可以接查詢運算子（輸出是表格形式），但整個請求都在 management 平面執行。你不能從查詢開始，再 pipe 到 management 指令。

```kql
// ✅ WORKS — management command piped to query operators
.show tables | project TableName | where TableName has "Events"

// ❌ WRONG — query piped into management command
StormEvents | take 5 | .show tables
```

拿不準的時候：第一個 token 以 `.` 開頭，就是 management 指令。要看 schema 探索指令的完整清單，見 `references/discovery-queries.md`。

## 2. Dynamic Type Discipline

KQL 的 `dynamic` 型別很有彈性，但在某些情境下很嚴格。常見的錯誤是在 `summarize by`、`order by` 或 `join on` 裡直接用 dynamic 欄位而沒有轉型。

**規則**：只要在 `by`、`on` 或 `order by` 裡用到 dynamic 型別的欄位，就一定要用明確的轉型包起來。

```kql
// ❌ ERROR: "Summarize group key ... is of a 'dynamic' type"
StormEvents | summarize count() by StormSummary.Details.Location

// ✅ FIX
StormEvents | summarize count() by tostring(StormSummary.Details.Location)
```

```kql
// ❌ ERROR: "order operator: key can't be of dynamic type"
StormEvents | order by StormSummary.TotalDamages desc

// ✅ FIX
StormEvents | order by tolong(StormSummary.TotalDamages) desc
```

```kql
// ❌ ERROR in join: dynamic join key
StormEvents | join kind=inner (PopulationData) on $left.StormSummary == $right.State

// ✅ FIX — cast both sides
StormEvents
| extend State_str = tostring(StormSummary.Details.Location)
| join kind=inner (PopulationData) on $left.State_str == $right.State
```

**自我修正**：錯誤訊息出現 "is of a 'dynamic' type" 時，加上 `tostring()`、`tolong()` 或 `todouble()`。

## 3. Join Patterns & Pitfalls

KQL 的 join 有些限制和 SQL 不一樣。

### Equality only
KQL 的 join 條件**只支援 `==`**。join 條件裡不能用 `<`、`>`、`!=` 或函式呼叫。

```kql
// ❌ ERROR: "Only equality is allowed in this context"
StormEvents | join (nyc_taxi) on geo_distance_2points(BeginLon, BeginLat, pickup_longitude, pickup_latitude) < 1000

// ✅ WORKAROUND — pre-bucket into spatial cells, then join on cell ID
StormEvents
| extend cell = geo_point_to_s2cell(BeginLon, BeginLat, 8)
| join kind=inner (nyc_taxi | extend cell = geo_point_to_s2cell(pickup_longitude, pickup_latitude, 8)) on cell
```

範圍型的 join 要先把值分箱：`| extend bin_val = bin(Value, 100)`，再用 `bin_val` 做 join。注意：靠近箱子邊界的值可能落在相鄰的箱子，要考慮檢查相鄰的箱子，或讓範圍重疊，才能確保精準。

### Left/right attribute matching
join 的 `on` 子句兩邊都必須**只參照欄位實體**，不能是運算式，也不能是聚合。

```kql
// ❌ ERROR: "for each left attribute, right attribute should be selected"
StormEvents | join kind=inner (PopulationData) on $left.State

// ✅ FIX — specify both sides explicitly
StormEvents | join kind=inner (PopulationData) on $left.State == $right.State
```

### Cardinality check before large joins
join 超過 10K 列的資料表之前，**一定**要先檢查 cardinality。唯一一次 `E_RUNAWAY_QUERY` 錯誤，就是 cross-join 爆炸造成的（25K × 195 = 可能有 4.8M 列）。

```kql
// Before joining, check how many rows each side contributes
StormEvents | summarize dcount(State)        // → 67 distinct states
PopulationData | summarize dcount(State)     // → 52 — safe to join
```

## 4. Regex in KQL

KQL 原生就能處理 regex，不需要用 Python。

### The `extract_all` gotcha
和 Python 的 `re.findall()` 不同，KQL 的 `extract_all` **要求 regex 裡有 capturing group**：

```kql
// ❌ ERROR: "extractall(): argument 2 must be a valid regex with [1..16] matching groups"
StormEvents | extend words = extract_all(@"[a-zA-Z]{3,}", EventNarrative)

// ✅ FIX — add parentheses around the pattern
StormEvents | extend words = extract_all(@"([a-zA-Z]{3,})", EventNarrative)
```

### Regex toolkit — don't fall back to Python
| Function | Use case | Example |
|----------|----------|---------|
| `extract(regex, group, source)` | 單一比對 | `extract(@"User '([^']+)'", 1, Msg)` |
| `extract_all(regex, source)` | 所有比對（需要 `()`） | `extract_all(@"(\w+)", Text)` |
| `parse` | 結構化擷取 | `parse Msg with * "User '" Sender "' sent" *` |
| `matches regex` | 布林過濾 | `where Url matches regex @"^https?://"` |
| `replace_regex` | 尋找並取代 | `replace_regex(Text, @"\s+", " ")` |

## 5. Serialization Requirements

Window 函式需要 serialize 過（有排序）的輸入。

```kql
// ❌ ERROR: "Function 'row_cumsum' cannot be invoked. The row set must be serialized."
StormEvents
| where State == "TEXAS"
| summarize DailyCount = count() by bin(StartTime, 1d)
| extend CumulativeCount = row_cumsum(DailyCount)

// ✅ FIX — add | serialize (or | order by, which implicitly serializes)
StormEvents
| where State == "TEXAS"
| summarize DailyCount = count() by bin(StartTime, 1d)
| order by StartTime asc
| extend CumulativeCount = row_cumsum(DailyCount)
```

需要 serialization 的函式：`row_number()`、`row_cumsum()`、`prev()`、`next()`、`row_window_session()`。

## 6. Memory-Safe Query Patterns

這是最常見的記憶體錯誤。成因是沒有先過濾，就掃描了太多資料。

### The progression of safety
```
Safest ──────────────────────────────────────────────── Most dangerous
| count    | take 10    | where + summarize    | summarize (no filter)    | full scan
```

### Rules for large tables (>1M rows)

1. **一律先用 `| count`** 了解資料表大小
2. **一律在 `| summarize` 之前先 `| where`**：先過濾時間範圍、partition key 或類別
3. **絕對不要在沒預先過濾的情況下，對高 cardinality 的欄位用 `dcount()`**
4. 執行前**先檢查 join 的 cardinality**（見第 3 節）
5. 被多次參照的子查詢要用 **`materialize()`**

```kql
// ❌ OUT OF MEMORY — large table, no filter, many group-by columns
StormEvents
| summarize dcount(EventType), count() by StartTime, State, Source
| where dcount_EventType > 1

// ✅ SAFE — filter first, then aggregate
StormEvents
| where StartTime between (datetime(2007-04-15) .. datetime(2007-04-16))
| summarize dcount(EventType) by State, Source
| where dcount_EventType > 1
```

### When you see `E_LOW_MEMORY_CONDITION`
查詢碰了太多資料。你的選擇：
- 加上 `| where` 過濾（時間範圍、partition key）
- 減少 `summarize` 裡 `by` 欄位的數量
- 拆成較小的時間區段，再把結果 union 起來
- 做探索時用 `| sample 10000`，不要全表掃描

### When you see `E_RUNAWAY_QUERY`
join 或聚合產生了太多輸出列。檢查 join 的 cardinality，其中一邊或兩邊太大了。

## 7. Result Size Discipline

太大的結果會拖慢分析。預防方式：

| Query type | Safeguard |
|-----------|-----------|
| 探索性 | 一律以 `\| take 10` 或 `\| take 20` 結尾 |
| 聚合 | 用 `\| top 20 by ...`，不要用沒有限制的 `summarize` |
| 很寬的列（vector、JSON） | 用 `\| project` 只留需要的欄位 |
| `make_list()` / `make_set()` | 避免用在高 cardinality 的分組（會產生超巨大的儲存格） |
| 大小不明 | 先跑 `\| count` |

**Vector 陷阱**：有 embedding 欄位（1536 維 float 陣列）的資料表，每列大約 30KB。就算只有 `| take 20` 也有 600KB。除非你特別需要，否則一律用 `| project` 把 vector 欄位去掉。

## 8. String Comparison Strictness

KQL 在比較計算出來的字串值時，有時需要明確轉型，就算兩邊本來就是字串也一樣。

```kql
// ❌ ERROR: "Cannot compare values of types string and string. Try adding explicit casts"
StormEvents | where geo_point_to_s2cell(BeginLon, BeginLat, 16) == other_cell

// ✅ FIX — wrap both sides in tostring()
StormEvents | where tostring(geo_point_to_s2cell(BeginLon, BeginLat, 16)) == tostring(other_cell)
```

這最常出現在 `geo_point_to_s2cell()` 和 `strcat()` 算出來的值做比較時。拿不準就用 `tostring()` 轉型。

## 9. Advanced Functions

KQL 原生就能處理這些，不需要用 Python：

### Vector similarity
```kql
// try it! — cosine similarity on Iris feature vectors
let target = pack_array(5.1, 3.5, 1.4, 0.2);
Iris
| extend Vec = pack_array(SepalLength, SepalWidth, PetalLength, PetalWidth)
| extend sim = series_cosine_similarity(Vec, target)
| top 5 by sim desc
```

### Geo operations
```kql
// Distance between two points (meters)
StormEvents | extend dist = geo_distance_2points(BeginLon, BeginLat, EndLon, EndLat)

// Spatial bucketing for joins
StormEvents | extend cell = geo_point_to_s2cell(BeginLon, BeginLat, 8)
```

### Graph queries
```kql
// Persistent graph model — try it on the help cluster!
graph("Simple")
| graph-match (src)-[e*1..3]->(dst)
  where src.name == "Alice"
  project src.name, dst.name, path_length = array_length(e)

// Transient graph — build inline with make-graph
SimpleGraph_Edges
| make-graph source --> target with SimpleGraph_Nodes on id
| graph-match (src)-[e*1..5]->(dst)
  where src.name == "Alice"
  project src.name, dst.name, path_length = array_length(e)
```

### Time series
```kql
// try it! — create a time series and detect anomalies
StormEvents
| make-series count() default=0 on StartTime step 1d
| extend anomalies = series_decompose_anomalies(count_)
```

詳細的範例和模式請參考 `references/advanced-patterns.md`。

## 10. Self-Correction Lookup Table

遇到錯誤時，先在這裡查，再重試：

| Error message contains | Likely cause | Fix |
|---|---|---|
| `is of a 'dynamic' type` | `by`/`on`/`order by` 裡有 dynamic 欄位 | 用 `tostring()`/`tolong()` 包起來 |
| `Only equality is allowed` | join 條件裡有範圍判斷 | 用 S2/H3 cell 或 `bin()` 預先分箱 |
| `extractall(): matching groups` | regex 缺少 `()` | 加上 `()`：用 `@"(\w+)"`，不要用 `@"\w+"` |
| `row set must be serialized` | 在沒排序的資料上用 window 函式 | 在它之前加 `\| serialize` 或 `\| order by` |
| `Cannot compare values of types string and string` | 比較計算出來的字串 | 兩邊都加 `tostring()` |
| `Failed to resolve column named 'X'` | 欄位名稱或資料表錯了 | 執行 `.show table T schema` 檢查欄位名稱 |
| `E_LOW_MEMORY_CONDITION` | 查詢碰了太多資料 | 加 `\| where` 過濾、縮小時間範圍、拆成多步 |
| `E_RUNAWAY_QUERY` | join/聚合產生太多列 | join 之前先檢查 cardinality；加預先過濾 |
| `for each left attribute, right attribute` | join 的 `on` 子句不完整 | 用明確的寫法：`on $left.X == $right.Y` |
| `needs to be bracketed` | 把保留字當識別字用 | 用 `['keyword']` 語法 |
| `plugin doesn't exist` | 這個 cluster 沒有該 plugin | 改用等效的函式或 Python |
| `Expected string literal in datetime()` | datetime 字面值裡放了單純的整數 | 用 `datetime(2024-01-01)`，不要用 `datetime(2024)` |
| `Unexpected token` after `by` | summarize 的 by 子句裡有複雜運算式 | 先 `extend` 出該運算式，再對那個欄位 `summarize by` |
| `not recognized` / `unknown operator` | 這個引擎沒有該運算子 | 檢查運算子支援狀況；試試等效的（`order by` = `sort by`） |

## 11. Datetime Pitfalls

Datetime 字面值是常見的錯誤來源。字面值格式一錯，常常讓人改用完全不同的做法，而不是修掉那個小問題。

### Literal format
```kql
// ❌ WRONG — bare year is not a valid datetime
StormEvents | where StartTime > datetime(2007)

// ✅ RIGHT — always use full date format
StormEvents | where StartTime > datetime(2007-01-01)
```

### Filtering by year, month, or hour
```kql
// ❌ WRONG — comparing datetime column to integer
StormEvents | where StartTime == 2007

// ✅ RIGHT — use datetime_part() to extract components
StormEvents | where datetime_part("year", StartTime) == 2007

// ✅ ALSO RIGHT — use between with datetime range
StormEvents | where StartTime between (datetime(2007-01-01) .. datetime(2007-12-31T23:59:59))
```

### Time bucketing in summarize
```kql
// This works, but can be harder to read and reuse in complex queries
StormEvents | summarize count() by startofmonth(StartTime)

// Clearer — extend first, then summarize by the computed column
StormEvents
| extend Month = startofmonth(StartTime)
| summarize count() by Month
| order by Month asc
```

### Useful datetime functions
| Function | Purpose | Example |
|----------|---------|---------|
| `bin(ts, 1h)` | 向下取整到箱子邊界 | `bin(Timestamp, 1d)` |
| `startofmonth(ts)` | 該月的第一天 | `startofmonth(Timestamp)` |
| `datetime_part("hour", ts)` | 取出組成部分 | `datetime_part("year", Timestamp)` |
| `format_datetime(ts, fmt)` | 格式化成字串 | `format_datetime(Timestamp, "yyyy-MM")` |
| `ago(1d)` | 相對時間 | `where Timestamp > ago(1d)` |
| `between(a .. b)` | 範圍過濾（含兩端） | `where Timestamp between (datetime(2024-01-01) .. datetime(2024-01-31T23:59:59))` |
| `todatetime(str)` | 解析字串 → datetime | `todatetime("2024-01-15T10:30:00Z")` |
| `totimespan(str)` | 解析字串 → timespan | `totimespan("01:30:00")` |

## 12. Operator Naming & Equality

KQL 和 SQL 語法有些微妙的差異。

### Naming conventions

| Entity | Convention | Example |
|--------|-----------|---------|
| 資料表 | UpperCamelCase | `StormEvents`、`NetworkLogs` |
| 欄位 | UpperCamelCase | `StartTime`、`EventType` |
| 變數（`let`） | snake_case | `let filtered_events = ...` |
| 內建函式 | snake_case | `format_bytes()`、`geo_distance_2points()` |
| 已儲存的函式 | UpperCamelCase | `.create function GetTopUsers` |

### Equality operators
```kql
// In where clauses, == is case-sensitive, =~ is case-insensitive
StormEvents | where State == "TEXAS" | count        // exact match
StormEvents | where State =~ "texas" | count        // case-insensitive

// In joins, use == only
StormEvents | join kind=inner (PopulationData) on State
```

### sort vs order
`sort by` 和 `order by` 在 KQL 裡運作完全相同，它們是別名。要用哪個隨你，但要保持一致。

### contains vs has
```kql
// contains: substring match (slower)
StormEvents | where EventNarrative contains "tree"   // finds "trees", "treetop" too

// has: term/word match (faster, uses index)
StormEvents | where EventNarrative has "tree"        // matches word boundaries only

// For exact prefix/suffix
StormEvents | where EventType startswith "Thunder"
StormEvents | where Source endswith "Spotter"
```

## 13. Error Recovery Strategy

第一個 KQL 查詢失敗時，很容易想整個放棄、改試完全不同的做法。正確的反應幾乎都是**修掉那個具體的錯誤**，不要換策略。

### The pattern to avoid
```
Query 1: extract(@"pattern", 1, col)  → Parse error
Query 2: todynamic(col)               → Different error  
Query 3: parse_json(col)              → Another error
Query 4: Python script                → Works but 10x tokens
```

### The correct pattern
```
Query 1: extract(@"pattern", 1, col)  → Parse error (bad escaping)
Query 2: extract(@"pattern", 1, col)  → Fix the specific escaping issue → Success
```

**錯誤復原的規則：**
1. 仔細讀錯誤訊息，它幾乎總是明確告訴你哪裡出了問題
2. 修掉**具體的**語法/跳脫問題，不要換做法
3. 用自我修正表（第 10 節）把錯誤對應到修法
4. 同一個查詢修了 2 次都失敗，才換做法
5. 對結構化文字，`parse` 運算子通常比 `extract()` 簡單：

```kql
// Instead of complex regex on TraceLogs:
// extract(@"file path: \"\"([^\"]+)\"\"", 1, Message)

// Use parse for structured extraction (try it on help cluster, SampleLogs db):
cluster("help").database("SampleLogs").TraceLogs
| where Message has "file path"
| parse Message with * "file path: \"\"" FilePath "\"\"" *
| project Timestamp, FilePath
| take 5
```

## 14. Query Writing Checklist

執行任何 KQL 查詢之前，先在心裡檢查：

1. **有預先過濾嗎？** 大型資料表在任何 `| summarize` 之前都有 `| where`
2. **結果有設上限嗎？** 探索性查詢以 `| take N` 或 `| top N` 結尾
3. **dynamic 欄位轉型了嗎？** `by`/`on`/`order by` 裡的 dynamic 欄位都有包起來
4. **regex 有 group 嗎？** `extract_all` 的 pattern 在要擷取的部分外面有 `()`
5. **join cardinality 安全嗎？** join 之前兩邊都用 `dcount()` 檢查過
6. **只留需要的欄位嗎？** 寬的資料表用 `| project` 去掉不需要的欄位
7. **datetime 字面值有效嗎？** 用 `datetime(2024-01-01)`，不要用 `datetime(2024)` 或單純的整數
8. **有複雜的 by 運算式嗎？** 先 `| extend`，再對算出來的欄位 `| summarize by`
9. **有錯誤復原計畫嗎？** 查詢失敗時，修掉具體的錯誤，不要換策略
