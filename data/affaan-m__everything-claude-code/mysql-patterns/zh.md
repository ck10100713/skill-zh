---
name: mysql-patterns
description: 正式環境後端的 MySQL 與 MariaDB schema、查詢、索引、交易、複寫和連線池模式。設計 MySQL 或 MariaDB 的 schema 和索引，或查詢、交易、replica 出現延遲時使用。
metadata:
  origin: ECC
---

# MySQL Patterns

處理 MySQL 或 MariaDB 的 schema 設計、migration、
慢查詢調查、佇列式交易、連線池或
正式環境的資料庫設定時，用這個 skill。套用某個功能專屬的模式之前，先精確檢查版本，
因為 MySQL 和 MariaDB 在好幾個 SQL
細節上已經分歧了。

## Activation

- 設計 MySQL 或 MariaDB 的資料表、索引和限制條件
- 在大型正式資料表上執行 migration 之前先審查
- 除錯慢查詢、鎖等待、死結或連線耗盡
- 加入 keyset 分頁、upsert、全文檢索、JSON 欄位或佇列
- 設定應用程式連線池、唯讀 replica、TLS 或 slow log

## Version Check

先確認引擎和版本：

```sql
SELECT VERSION();
SHOW VARIABLES LIKE 'version_comment';
```

語法不同時，MySQL 和 MariaDB 的指引要分開：

- MySQL 文件把 row alias 當作 `ON DUPLICATE KEY UPDATE` 裡 `VALUES(col)` 的
  替代方案；`VALUES(col)` 在那裡已棄用。
- MariaDB 文件把 `VALUES(col)` 當作在 `ON DUPLICATE KEY UPDATE` 裡參照插入值的
  支援寫法；要跨引擎相容就用它。
- `SKIP LOCKED` 只適合類似佇列的工作。它會略過被鎖住的資料列，
  可能回傳不一致的視圖，所以不要用在一般的帳務
  或對完整性敏感的讀取上。

## Schema Defaults

```sql
CREATE TABLE orders (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    account_id BIGINT UNSIGNED NOT NULL,
    status VARCHAR(32) NOT NULL,
    total DECIMAL(15, 2) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at DATETIME NULL,
    PRIMARY KEY (id),
    KEY idx_orders_account_status_created (account_id, status, created_at),
    KEY idx_orders_active (account_id, deleted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

預設選擇：

| 使用情境 | 偏好 | 避免 |
| --- | --- | --- |
| 代理主鍵 | `BIGINT UNSIGNED AUTO_INCREMENT` | 資料表可能成長超過 20 億列時用 `INT` |
| UUID 查詢鍵 | `BINARY(16)` 搭配轉換 helper | 熱資料表用 `VARCHAR(36)` 當主鍵 |
| 金額和精確數量 | `DECIMAL(p, s)` | `FLOAT` 或 `DOUBLE` |
| 面向使用者的文字 | `utf8mb4` 的資料表和索引 | MySQL 的 `utf8` / `utf8mb3` 預設值 |
| 應用程式時間戳記 | `DATETIME`，UTC 由應用程式管理 | 假設 `DATETIME` 會存時區 metadata |
| 軟刪除 | `deleted_at DATETIME NULL` 加上有範圍的索引 | 過濾軟刪除資料列卻沒有索引 |
| 可擴充的狀態值 | 查找表或有限制的 `VARCHAR` | 值常常變動時用 `ENUM` |

## Indexing

複合索引的順序通常是等值條件在前，接著是範圍或
排序欄位：

```sql
CREATE INDEX idx_orders_account_status_created
    ON orders (account_id, status, created_at);

SELECT id, total
FROM orders
WHERE account_id = ?
  AND status = 'pending'
  AND created_at >= ?
ORDER BY created_at DESC
LIMIT 50;
```

新增或修改索引之前，先用 `EXPLAIN`：

```sql
EXPLAIN
SELECT id, total
FROM orders
WHERE account_id = 123 AND status = 'pending'
ORDER BY created_at DESC
LIMIT 50;
```

需要調查的訊號：

| 欄位 | 風險訊號 |
| --- | --- |
| `type` | 大型資料表上出現 `ALL` |
| `key` | 有高選擇性條件卻是 `NULL` |
| `rows` | 互動路徑上的預估列數非常高 |
| `Extra` | `Using temporary`、`Using filesort`，或範圍很廣的 `Using where` |

不要盲目加索引。每個索引都會增加寫入成本、migration 時間、
備份大小和 buffer pool 的壓力。

## Query Patterns

### Upsert

跨引擎相容的寫法：

```sql
INSERT INTO user_settings (user_id, setting_key, setting_value)
VALUES (?, ?, ?)
ON DUPLICATE KEY UPDATE
    setting_value = VALUES(setting_value),
    updated_at = CURRENT_TIMESTAMP;
```

MySQL row alias 的寫法：

```sql
INSERT INTO user_settings (user_id, setting_key, setting_value)
VALUES (?, ?, ?) AS new
ON DUPLICATE KEY UPDATE
    setting_value = new.setting_value,
    updated_at = CURRENT_TIMESTAMP;
```

確認目標是 MySQL 之後，才用 row alias 的寫法。MariaDB 或
MySQL/MariaDB 混合的環境就用 `VALUES(col)`。

### Keyset Pagination

```sql
SELECT id, name, created_at
FROM products
WHERE (created_at, id) < (?, ?)
ORDER BY created_at DESC, id DESC
LIMIT 50;
```

用符合 cursor 的索引來支撐它：

```sql
CREATE INDEX idx_products_created_id ON products (created_at, id);
```

大型資料表不要用很深的 `OFFSET` 分頁；它會讓伺服器掃描
並丟棄資料列，之後才回傳該頁。

### JSON Fields

JSON 欄位用來放擴充資料，不要用在需要大量關聯式過濾或限制條件的欄位。

```sql
CREATE TABLE events (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    payload JSON NOT NULL,
    event_type VARCHAR(64)
        GENERATED ALWAYS AS (JSON_UNQUOTE(JSON_EXTRACT(payload, '$.type'))) STORED,
    KEY idx_events_type (event_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

常被查詢的 JSON 路徑，要露出一個 generated column 並替那個
欄位建索引。外鍵、所有權、租戶和生命週期欄位要維持關聯式。

### Full-Text Search

```sql
ALTER TABLE articles ADD FULLTEXT KEY ft_articles_title_body (title, body);

SELECT id, title, MATCH(title, body) AGAINST (? IN NATURAL LANGUAGE MODE) AS score
FROM articles
WHERE MATCH(title, body) AGAINST (? IN NATURAL LANGUAGE MODE)
ORDER BY score DESC
LIMIT 20;
```

需要容錯拼字、複雜排序、跨表 facet，或超出內建全文檢索行為的
特定語言分析時，改用外部搜尋。

## Transactions

交易要短，而且依一致的順序鎖定資料列：

```sql
START TRANSACTION;

SELECT id, balance
FROM accounts
WHERE id IN (?, ?)
ORDER BY id
FOR UPDATE;

UPDATE accounts SET balance = balance - ? WHERE id = ?;
UPDATE accounts SET balance = balance + ? WHERE id = ?;

COMMIT;
```

死結和鎖等待的檢查清單：

- 在所有程式路徑上，依確定的順序鎖定資料列。
- 外部 API 呼叫在開啟交易之前做，不要放在交易裡面。
- 替 `UPDATE`、`DELETE` 和鎖定讀取用到的條件加索引。
- 發生死結時，rollback 並重試整個交易，重試次數要有上限。
- 死結發生後馬上抓 `SHOW ENGINE INNODB STATUS\G`；它會被
  之後的事件覆蓋。

佇列式的 worker 領取工作：

```sql
START TRANSACTION;

SELECT id
FROM jobs
WHERE status = 'pending'
ORDER BY created_at
LIMIT 1
FOR UPDATE SKIP LOCKED;

UPDATE jobs
SET status = 'processing', started_at = CURRENT_TIMESTAMP
WHERE id = ?;

COMMIT;
```

只對可以接受略過被鎖資料列的佇列式工作負載使用 `SKIP LOCKED`。
它不能取代正常的交易一致性。

## Connection Pools

SQLAlchemy 範例：

```python
from sqlalchemy import create_engine

engine = create_engine(
    "mysql+mysqlconnector://app:secret@db.internal/app",
    pool_size=10,
    max_overflow=5,
    pool_timeout=30,
    pool_recycle=240,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 5},
)
```

Node.js `mysql2` 範例：

```javascript
import mysql from 'mysql2/promise';

const pool = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,
  enableKeepAlive: true,
  keepAliveInitialDelay: 30000,
});

const [rows] = await pool.execute(
  'SELECT id, total FROM orders WHERE account_id = ? LIMIT 50',
  [accountId],
);
```

應用程式連線池的回收時間要低於伺服器的 `wait_timeout`。如果伺服器
用 `wait_timeout = 300`，`pool_recycle` 設在 240 秒左右是合理的；
`pool_pre_ping` 仍然有助於從網路和 failover 事件中恢復。

## Diagnostics

好用的第一輪指令：

```sql
SHOW FULL PROCESSLIST;
SHOW ENGINE INNODB STATUS\G;
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';
```

在受控的環境裡啟用 slow log：

```sql
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;
SET GLOBAL log_queries_not_using_indexes = 'ON';
```

只有在可以安全執行該查詢時才用 `EXPLAIN ANALYZE`。它會真的執行
該語句，在正式環境大小的資料上可能很貴。

## Replication

唯讀 replica 可能有延遲。寫入之後，不要立刻把「讀自己剛寫的資料」的路徑、結帳流程、
權限檢查或 idempotency-key 的讀取導向 replica。

```sql
-- MySQL 舊式術語，在既有環境裡仍然常見
SHOW SLAVE STATUS\G;

-- 有支援的話，用新式術語
SHOW REPLICA STATUS\G;
```

統一使用某個指令之前，先檢查引擎/版本。要監控 replica 的
SQL thread 健康度、IO thread 健康度和延遲，不要只看 TCP
連線是不是還活著。

## Security

```sql
CREATE USER 'app'@'%' IDENTIFIED BY 'use-a-secret-manager';
GRANT SELECT, INSERT, UPDATE, DELETE ON appdb.* TO 'app'@'%';

ALTER USER 'app'@'%' REQUIRE SSL;

SELECT user, host
FROM mysql.user
WHERE user = '';

DROP USER IF EXISTS ''@'localhost';
DROP USER IF EXISTS ''@'%';
```

安全審查要點：

- 不要把 `ALL PRIVILEGES` 或 `*.*` 授予應用程式使用者。
- 流量跨主機或跨網路時，要求應用程式使用者使用 TLS。
- 憑證存放在平台的 secret manager，不要放在範例、腳本或
  repo 檔案裡。
- 把 migration/管理員使用者和執行期的應用程式使用者分開。
- 調整效能之前，先稽核對外的網路暴露和 bind address。

## Configuration

專用資料庫主機的起點範例：

```ini
[mysqld]
innodb_buffer_pool_size = 4G
innodb_flush_log_at_trx_commit = 1
sync_binlog = 1

max_connections = 300
thread_cache_size = 50

wait_timeout = 300
interactive_timeout = 300
innodb_lock_wait_timeout = 10

slow_query_log = ON
long_query_time = 1
log_queries_not_using_indexes = ON

log_bin = mysql-bin
binlog_format = ROW
binlog_expire_logs_seconds = 604800
```

把設定值當成審查的引子，不是通用的預設組合。記憶體、連線數、紀錄保留和持久性設定，
要依工作負載、硬體、備份政策和復原目標來決定大小。

## Anti-Patterns

| Anti-Pattern | 風險 | 比較好的模式 |
| --- | --- | --- |
| 熱路徑裡用 `SELECT *` | 過度取得，client 也變脆弱 | 明確選取欄位 |
| 很深的 `OFFSET` 分頁 | 線性掃描和頁面變慢 | keyset 分頁 |
| 外鍵 join 沒有索引 | join 變慢，刪除時鎖很多 | 有意識地替 FK 欄位建索引 |
| 長交易 | 鎖等待和龐大的 undo 歷史 | commit 小單位的工作 |
| 直接對 `mysql.user` 做 DML | 授權表損壞的風險 | 用 `CREATE USER`、`ALTER USER`、`DROP USER` |
| 應用程式使用者擁有管理員權限 | 爆炸半徑很大 | 最小權限的執行期使用者 |
| 連線池回收時間高於 `wait_timeout` | 連線池裡有過期的連線 | 回收時間低於逾時，並搭配 pre-ping |
| 寫入之後讀 replica | 面向使用者的狀態過期 | 把寫後讀的流程固定導向 primary |

## Output Expectations

用這個 skill 做審查時，要回傳：

1. 引擎/版本的假設。
2. 風險最高的正確性、鎖、安全和 migration 問題。
3. 安全路徑上確切的 SQL 或程式碼變更。
4. 驗證計畫：`EXPLAIN`、migration 試跑、鎖/死結檢查，以及
   回滾條件。
5. 任何會影響建議的 MySQL/MariaDB 語法差異。

## Related

- Skill: `postgres-patterns`：PostgreSQL 專屬的 schema 和查詢模式
- Skill: `database-migrations`：migration 規劃和上線安全
- Skill: `backend-patterns`：API 和 service 層模式
- Skill: `security-review`：機密處理、驗證和最小權限
- Agent: `database-reviewer`：更廣的資料庫審查流程
