---
name: postgresql-table-design
description: 在設計或審查 PostgreSQL 專用的 schema 時使用這個 skill。涵蓋最佳實務、資料型別、索引、約束、效能模式與進階功能
---

# PostgreSQL Table Design

## When to Use

- 設計新的 PostgreSQL schema，或在上線前審查 schema。
- 專門針對 PostgreSQL 選擇欄位型別、key、約束或索引。
- 決定大型資料表是否要分區、怎麼分區，或怎麼儲存半結構化資料。
- 規劃在線上資料庫做 schema 變更，而且不能停機。

這是 PostgreSQL schema 的規則與決策點。完整的資料型別目錄、workload
模式（大量更新、大量寫入、upsert、schema 演進）、擴充套件、JSONB 索引，
以及完整的 DDL 範例都在 `references/details.md`；下面哪個段落指向那裡，就去打開它。

## Core Rules

- 為參考資料表（users、orders 等）定義 **PRIMARY KEY**。時間序列/事件/log 資料不一定需要。需要時優先用 `BIGINT GENERATED ALWAYS AS IDENTITY`；只有需要全域唯一或不透明的 ID 時才用 `UUID`。
- **先正規化（到 3NF）** 來消除資料冗餘與更新異常；**只有**在讀取效益高、且已證實 join 效能有問題時才反正規化。
- 凡是語意上必須有值的欄位都加 **NOT NULL**；常見的值用 **DEFAULT**。
- **為你實際會查詢的存取路徑建立索引**：PK/unique（自動）、**FK 欄位（要手動！）**、常用的過濾/排序，以及 join 的 key。
- 事件時間優先用 **TIMESTAMPTZ**；金額用 **NUMERIC**；字串用 **TEXT**；整數用 **BIGINT**；浮點數用 **DOUBLE PRECISION**（要精確的小數運算則用 `NUMERIC`）。

## PostgreSQL Gotchas

- **識別字**：沒加引號的會轉成小寫。避免加引號或大小寫混合的名稱；用 `snake_case`。
- **Unique + NULL**：UNIQUE 允許多個 NULL。用 `UNIQUE NULLS NOT DISTINCT (...)`（PG15+）限制只能有一個 NULL。
- **FK 索引**：PostgreSQL **不會**自動替 FK 欄位建索引。要自己加。
- **沒有靜默的型別轉換**：長度/精度溢位會報錯（不會截斷）。對 `NUMERIC(2,0)` 插入 999 會失敗，跟會靜默截斷或四捨五入的資料庫不一樣。
- **Sequence/identity 會有空號**（正常；不要去「修」）。Rollback、當機和並行交易都會留下空號（1、2、5、6...）。
- **Heap 儲存**：預設沒有 clustered PK；`CLUSTER` 只是一次性的重新整理，之後插入的資料不會維持。
- **MVCC**：更新/刪除會留下 dead tuple；由 vacuum 處理，設計時要避免熱點寬資料列的頻繁變動。

## Data Types

- **ID**：`BIGINT GENERATED ALWAYS AS IDENTITY`；分散式或不透明的 ID 用 `UUID`，以 `uuidv7()`（PG18+）或 `gen_random_uuid()` 產生。
- **數字**：除非儲存空間很關鍵，否則用 `BIGINT`；`DOUBLE PRECISION` 優先於 `REAL`；金額和精確小數用 `NUMERIC(p,s)`。
- **字串**：用 `TEXT`，需要長度上限時加上 `CHECK (LENGTH(col) <= n)`；二進位用 `BYTEA`。不分大小寫的查詢：對 `LOWER(col)` 建 expression index，或當約束本身必須不分大小寫時用 `CITEXT`。
- **時間**：`TIMESTAMPTZ`、`DATE`、`INTERVAL`。`now()` 是交易開始的時間；`clock_timestamp()` 是實際的時鐘時間。
- **布林**：`BOOLEAN NOT NULL`，除非需要三態。
- **Enum**：`CREATE TYPE ... AS ENUM` 只用在小型、穩定的集合；會演進的業務值用 `TEXT` + `CHECK` 或查找表。
- **JSONB** 優先於 JSON，用 GIN 建索引，只用在可選的/半結構化的屬性。
- 陣列、range、網路、幾何、全文檢索、domain、composite 與 vector 型別，以及 TOAST 儲存和 collation 控制：見 `references/details.md`。

### Types to avoid

| Avoid | Use instead |
|---|---|
| `timestamp` (without time zone) | `timestamptz` |
| `char(n)`, `varchar(n)` | `text` (+ `CHECK` on length if needed) |
| `money` | `numeric` |
| `timetz` | `timestamptz` |
| `timestamptz(0)` or any precision | `timestamptz` |
| `serial` | `generated always as identity` |

## Constraints

- **PK**：隱含 UNIQUE + NOT NULL；會建立 B-tree 索引。
- **FK**：指定 `ON DELETE/UPDATE`（`CASCADE`、`RESTRICT`、`SET NULL`、`SET DEFAULT`）。為參照的欄位建索引。對在 commit 時才檢查的循環相依，用 `DEFERRABLE INITIALLY DEFERRED`。
- **UNIQUE**：會建立 B-tree 索引；除非用 `NULLS NOT DISTINCT`（PG15+），否則允許多個 NULL。除非你要允許重複的 NULL，否則優先用 `NULLS NOT DISTINCT`。
- **CHECK**：只看單一資料列；NULL 會通過（三值邏輯）。要搭配 `NOT NULL`：`price NUMERIC NOT NULL CHECK (price > 0)`。
- **EXCLUDE**：用運算子防止重疊，例如 `EXCLUDE USING gist (room_id WITH =, booking_period WITH &&)` 可以防止重複訂房。需要支援 GiST 的型別。

## Indexing

- **B-tree**：等值/範圍查詢的預設（`=`、`<`、`>`、`BETWEEN`、`ORDER BY`）。
- **Composite**：最左前綴規則（`WHERE a = ? AND b > ?` 會用到 `(a,b)`；`WHERE b = ?` 則不會）。選擇性最高的欄位放最前面。
- **Covering**：`CREATE INDEX ON tbl (id) INCLUDE (name, email)`，用於 index-only scan。
- **Partial**：熱門的子集，`CREATE INDEX ON tbl (user_id) WHERE status = 'active'`。
- **Expression**：`CREATE INDEX ON tbl (LOWER(email))`；查詢必須使用相同的表達式。
- **GIN**：JSONB 的包含/存在、陣列、全文檢索。**GiST**：range、幾何、exclusion constraint。
- **BRIN**：大型、天然有序的資料（時間序列），儲存成本極低；當磁碟順序和索引欄位相關時有效。

## Partitioning

- 用於大型資料表（超過 1 億筆），且查詢一律以分區 key 過濾，或維護作業（清除、整批替換）是依 key 進行的情況。
- 時間序列用 **RANGE**（`PARTITION BY RANGE (created_at)`；**TimescaleDB** 會自動處理，並附帶保留與壓縮），離散值用 **LIST**，沒有自然 key 但要均勻分布時用 **HASH**。
- **Constraint exclusion**：planner 會透過分區的 `CHECK` 約束來剪枝；宣告式分區（PG10+）會替你建立這些約束。
- 優先使用宣告式分區或 hypertable。不要使用 table inheritance。
- **限制**：沒有全域的 UNIQUE 約束，要把分區 key 包含在 PK/UNIQUE 裡。從分區資料表出發的 FK 需要 PG11+，參照分區資料表的 FK 需要 PG12+；舊版本請用 trigger。

## Examples

```sql
CREATE TABLE users (
  user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX ON users (LOWER(email));
CREATE INDEX ON users (created_at);
```

```sql
CREATE TABLE orders (
  order_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(user_id),
  status TEXT NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING','PAID','CANCELED')),
  total NUMERIC(10,2) NOT NULL CHECK (total > 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON orders (user_id);
CREATE INDEX ON orders (created_at);
```

```sql
-- JSONB attributes with a generated, indexable scalar
CREATE TABLE profiles (
  user_id BIGINT PRIMARY KEY REFERENCES users(user_id),
  attrs JSONB NOT NULL DEFAULT '{}',
  theme TEXT GENERATED ALWAYS AS (attrs->>'theme') STORED
);
CREATE INDEX profiles_attrs_gin ON profiles USING GIN (attrs);
```

## Going deeper

`references/details.md` 收錄這個檔案只點到名稱的內容：

- 完整的資料型別目錄：TOAST 儲存、collation、陣列、range、網路、幾何、全文檢索、domain、composite、vector。
- 資料表類型（`TEMPORARY`、`UNLOGGED`）與 row-level security。
- 約束與索引的備註，以及 RANGE、LIST 和 HASH 的分區 DDL。
- Workload 模式：大量更新、大量寫入、upsert 設計、安全的 schema 演進。
- Generated column 與擴充套件（`pg_trgm`、`citext`、`timescaledb`、`postgis`、`pgvector` 等）。
- JSONB 索引策略，包括 `jsonb_path_ops` 和抽出來的 B-tree 欄位。
