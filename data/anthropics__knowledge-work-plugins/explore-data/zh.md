---
name: explore-data
description: 對資料集做 profiling 與探索，了解它的形狀、品質和模式。遇到新的資料表或檔案、檢查 null 比例和欄位分布、找出重複或可疑值之類的資料品質問題，或決定要分析哪些維度和指標時使用。
argument-hint: "<table or file>"
---

# /explore-data - Profile and Explore a Dataset

> 如果看到不熟悉的佔位符，或需要確認目前連接了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

為資料表或上傳的檔案產生完整的資料 profile。在動手分析之前，先了解它的形狀、品質和模式。

## 用法

```
/explore-data <table_name or file>
```

## 流程

### 1. 存取資料

**如果有連接 data warehouse 的 MCP server：**

1. 解析資料表名稱（處理 schema 前綴，有歧義時建議可能的對象）
2. 查詢資料表的 metadata：欄位名稱、型別，有的話還有描述
3. 對即時資料執行 profiling 查詢

**如果提供的是檔案（CSV、Excel、Parquet、JSON）：**

1. 讀取檔案並載入成工作用的資料集
2. 從資料推斷欄位型別

**兩者都沒有：**

1. 請使用者提供資料表名稱（需要連接他們的 warehouse），或上傳檔案
2. 如果他們描述了資料表 schema，就提供該跑哪些 profiling 查詢的指引

### 2. 理解結構

分析任何資料之前，先理解它的結構：

**資料表層級的問題：**
- 有幾列、幾欄？
- Grain 是什麼（一列代表什麼）？
- Primary key 是什麼？它是唯一的嗎？
- 資料最後一次更新是什麼時候？
- 資料最早追溯到什麼時候？

**欄位分類**：把每個欄位歸類成下列其中之一：
- **Identifier**：唯一鍵、外部鍵、實體 ID
- **Dimension**：用來分組／篩選的類別屬性（status、type、region、category）
- **Metric**：用來衡量的量化值（revenue、count、duration、score）
- **Temporal**：日期和時間戳記（created_at、updated_at、event_date）
- **Text**：自由格式的文字欄位（description、notes、name）
- **Boolean**：真／假旗標
- **Structural**：JSON、陣列、巢狀結構

### 3. 產生資料 Profile

執行以下 profiling 檢查：

**資料表層級的指標：**
- 總列數
- 欄位數和型別分布
- 資料表的大約大小（metadata 有提供的話）
- 日期範圍覆蓋（日期欄位的最小／最大值）

**所有欄位：**
- Null 數量和 null 比例
- Distinct 數量和基數比（distinct / total）
- 最常見的值（前 5 到 10 名，附頻率）
- 最不常見的值（最後 5 名，用來發現異常）

**數值欄位（metric）：**
```
min, max, mean, median (p50)
standard deviation
percentiles: p1, p5, p25, p75, p95, p99
zero count
negative count (if unexpected)
```

**字串欄位（dimension、text）：**
```
min length, max length, avg length
empty string count
pattern analysis (do values follow a format?)
case consistency (all upper, all lower, mixed?)
leading/trailing whitespace count
```

**日期／時間戳記欄位：**
```
min date, max date
null dates
future dates (if unexpected)
distribution by month/week
gaps in time series
```

**Boolean 欄位：**
```
true count, false count, null count
true rate
```

**把 profile 呈現成一份乾淨的摘要表**，依欄位類型分組（dimension、metric、日期、ID）。

### 4. 找出資料品質問題

套用下面的品質評估框架。標記潛在的問題：

- **高 null 比例**：null 超過 5% 的欄位（警告）、超過 20%（警示）
- **低基數的意外**：應該是高基數、但實際不是的欄位（例如只有 50 個 distinct 值的「user_id」）
- **高基數的意外**：應該是類別型、卻有太多 distinct 值的欄位
- **可疑的值**：只應該出現正數的地方卻有負的金額、歷史資料裡出現未來日期、明顯是佔位的值（例如「N/A」「TBD」「test」「999999」）
- **重複偵測**：檢查是否有自然鍵，以及它有沒有重複
- **分布偏斜**：極度偏斜、會影響平均值的數值分布
- **編碼問題**：類別欄位大小寫混用、尾端空白、格式不一致

### 5. 發現關聯與模式

逐一 profiling 個別欄位之後：

- **外部鍵候選**：可能連到其他資料表的 ID 欄位
- **階層**：形成自然下鑽路徑的欄位（country > state > city）
- **相關性**：一起變動的數值欄位
- **衍生欄位**：看起來是由其他欄位計算出來的欄位
- **冗餘欄位**：資訊相同或幾乎相同的欄位

### 6. 建議有意思的維度和指標

根據欄位 profile，推薦：

- **最適合的維度欄位**，用來切分資料（基數合理的類別欄位，3 到 50 個值）
- **關鍵指標欄位**，用來衡量（分布有意義的數值欄位）
- **時間欄位**，適合做趨勢分析
- 資料中明顯可見的**自然分組**或階層
- 連到其他資料表的**潛在 join key**（ID 欄位、外部鍵）

### 7. 建議後續分析

建議使用者接下來可以跑的 3 到 5 個具體分析：

- 「Trend analysis on [metric] by [time_column] grouped by [dimension]」
- 「Distribution deep-dive on [skewed_column] to understand outliers」
- 「Data quality investigation on [problematic_column]」
- 「Correlation analysis between [metric_a] and [metric_b]」
- 「Cohort analysis using [date_column] and [status_column]」

## 輸出格式

```
## Data Profile: [table_name]

### Overview
- Rows: 2,340,891
- Columns: 23 (8 dimensions, 6 metrics, 4 dates, 5 IDs)
- Date range: 2021-03-15 to 2024-01-22

### Column Details
[summary table]

### Data Quality Issues
[flagged issues with severity]

### Recommended Explorations
[numbered list of suggested follow-up analyses]
```

---

## 品質評估框架

### 完整度評分

替每個欄位評級：
- **Complete**（非 null 超過 99%）：綠色
- **Mostly complete**（95-99%）：黃色，要調查那些 null
- **Incomplete**（80-95%）：橘色，要弄清楚原因，以及有沒有影響
- **Sparse**（少於 80%）：紅色，不做補值（imputation）可能無法使用

### 一致性檢查

要找的：
- **值的格式不一致**：同一個概念用不同寫法表示（「USA」「US」「United States」「us」）
- **型別不一致**：數字存成字串、日期有各種格式
- **參照完整性**：外部鍵對不到任何上層記錄
- **違反業務規則**：負的數量、結束日期早於開始日期、百分比大於 100
- **跨欄位一致性**：status = "completed" 但 completed_at 是 null

### 準確性指標

暗示準確性有問題的警訊：
- **佔位的值**：0、-1、999999、「N/A」「TBD」「test」「xxx」
- **預設值**：單一值的出現頻率高得可疑
- **過期的資料**：在活躍的系統裡，updated_at 沒有顯示任何近期變動
- **不可能的值**：年齡超過 150、遠在未來的日期、負的時長
- **整數偏差**：所有值都以 0 或 5 結尾（暗示是估計，不是量測）

### 時效性評估

- 資料表最後一次更新是什麼時候？
- 預期的更新頻率是多少？
- 事件發生時間和載入時間之間有沒有延遲？
- 時間序列裡有沒有缺口？

## 模式發現技巧

### 分布分析

對數值欄位，描述它的分布特徵：
- **Normal**：平均值和中位數很接近，呈鐘形
- **Skewed right**：高值有長長的尾巴（營收、session 時長很常見）
- **Skewed left**：低值有長長的尾巴（較少見）
- **Bimodal**：有兩個峰（暗示有兩個不同的族群）
- **Power law**：少數非常大的值、大量的小值（使用者活動很常見）
- **Uniform**：整個範圍內頻率大致相等（常常是合成或隨機的資料）

### 時間模式

對時間序列資料，要找：
- **Trend**：持續的上升或下降走勢
- **Seasonality**：重複出現的模式（每週、每月、每季、每年）
- **星期幾的效應**：平日 vs. 週末的差異
- **假日效應**：已知假日前後的下降或暴增
- **Change point**：水準或趨勢的突然轉變
- **Anomaly**：打破模式的個別資料點

### 分群發現

用這些方式找出自然的區隔：
- 找出有 3 到 20 個 distinct 值的類別欄位
- 比較各區隔值之間的指標分布
- 找出行為明顯不同的區隔
- 測試區隔是同質的，還是包含子區隔

### 相關性探索

在數值欄位之間：
- 計算所有指標配對的相關矩陣
- 標記強相關（|r| > 0.7）以便調查
- 注意：相關不代表因果，要明確標示這一點
- 檢查非線性關係（例如二次、對數）

## Schema 理解與文件

### Schema 文件範本

為團隊使用而記錄資料集時：

```markdown
## Table: [schema.table_name]

**Description**: [What this table represents]
**Grain**: [One row per...]
**Primary Key**: [column(s)]
**Row Count**: [approximate, with date]
**Update Frequency**: [real-time / hourly / daily / weekly]
**Owner**: [team or person responsible]

### Key Columns

| Column | Type | Description | Example Values | Notes |
|--------|------|-------------|----------------|-------|
| user_id | STRING | Unique user identifier | "usr_abc123" | FK to users.id |
| event_type | STRING | Type of event | "click", "view", "purchase" | 15 distinct values |
| revenue | DECIMAL | Transaction revenue in USD | 29.99, 149.00 | Null for non-purchase events |
| created_at | TIMESTAMP | When the event occurred | 2024-01-15 14:23:01 | Partitioned on this column |

### Relationships
- Joins to `users` on `user_id`
- Joins to `products` on `product_id`
- Parent of `event_details` (1:many on event_id)

### Known Issues
- [List any known data quality issues]
- [Note any gotchas for analysts]

### Common Query Patterns
- [Typical use cases for this table]
```

### Schema 探索查詢

連接到 data warehouse 時，用這些模式來探索 schema：

```sql
-- List all tables in a schema (PostgreSQL)
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Column details (PostgreSQL)
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'my_table'
ORDER BY ordinal_position;

-- Table sizes (PostgreSQL)
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- Row counts for all tables (general pattern)
-- Run per-table: SELECT COUNT(*) FROM table_name
```

### 血緣與相依關係

探索不熟悉的資料環境時：

1. 從「輸出」資料表開始（哪些報表或儀表板會用到它們）
2. 往上游追：哪些資料表餵進它們？
3. 辨識 raw／staging／mart 各層
4. 畫出從原始資料到分析用資料表的轉換鏈
5. 註明資料在哪裡被補充、過濾或聚合

## 小提醒

- 對非常大的資料表（1 億列以上），profiling 查詢預設會用抽樣，如果你需要精確的計數，請特別說明
- 第一次探索新資料集時，這個指令能讓你在寫具體查詢之前，先掌握全貌
- 品質標記是啟發式的：不是每個標記都是真正的問題，但每一個都值得快速看一眼
