---
name: azure-postgres-ts
description: |
  用 pg（node-postgres）套件，從 Node.js/TypeScript 連線到 Azure Database for PostgreSQL Flexible Server。用於 PostgreSQL 查詢、connection pooling、transaction，以及 Microsoft Entra ID（免密碼）驗證。Triggers: "PostgreSQL", "postgres", "pg client", "node-postgres", "Azure PostgreSQL connection", "PostgreSQL TypeScript", "pg Pool", "passwordless postgres".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: pg
---

# Azure PostgreSQL for TypeScript (node-postgres)

用 `pg`（node-postgres）套件連線到 Azure Database for PostgreSQL Flexible Server，支援密碼與 Microsoft Entra ID（免密碼）驗證。

## 安裝

```bash
npm install pg @azure/identity
npm install -D @types/pg
```

## 環境變數

```bash
# 必填
AZURE_POSTGRESQL_HOST=<server>.postgres.database.azure.com
AZURE_POSTGRESQL_DATABASE=<database>
AZURE_POSTGRESQL_PORT=5432

# 密碼驗證用
AZURE_POSTGRESQL_USER=<username>
AZURE_POSTGRESQL_PASSWORD=<password>

# Entra ID 驗證用
AZURE_POSTGRESQL_USER=<entra-user>@<server>   # 例如 user@contoso.com
AZURE_POSTGRESQL_CLIENTID=<managed-identity-client-id>  # 用於 user-assigned identity
AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境使用 DefaultAzureCredential 時才需要
```

## 驗證

### 選項 1：密碼驗證

```typescript
import { Client, Pool } from "pg";

const client = new Client({
  host: process.env.AZURE_POSTGRESQL_HOST,
  database: process.env.AZURE_POSTGRESQL_DATABASE,
  user: process.env.AZURE_POSTGRESQL_USER,
  password: process.env.AZURE_POSTGRESQL_PASSWORD,
  port: Number(process.env.AZURE_POSTGRESQL_PORT) || 5432,
  ssl: { rejectUnauthorized: true }  // Azure 必須設定
});

await client.connect();
```

### 選項 2：Microsoft Entra ID（免密碼）- 建議

```typescript
import { Client, Pool } from "pg";
import { DefaultAzureCredential, ManagedIdentityCredential } from "@azure/identity";

// 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
const credential = new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]});
// 或在正式環境直接使用特定的 credential：
// See https://learn.microsoft.com/javascript/api/overview/azure/identity-readme?view=azure-node-latest#credential-classes
// const credential = new ManagedIdentityCredential();

// 使用 user-assigned managed identity 時
// const credential = new DefaultAzureCredential({
//   managedIdentityClientId: process.env.AZURE_POSTGRESQL_CLIENTID
// });

// 取得 Azure PostgreSQL 的 access token
const tokenResponse = await credential.getToken(
  "https://ossrdbms-aad.database.windows.net/.default"
);

const client = new Client({
  host: process.env.AZURE_POSTGRESQL_HOST,
  database: process.env.AZURE_POSTGRESQL_DATABASE,
  user: process.env.AZURE_POSTGRESQL_USER,  // Entra ID 使用者
  password: tokenResponse.token,             // 把 token 當作密碼
  port: Number(process.env.AZURE_POSTGRESQL_PORT) || 5432,
  ssl: { rejectUnauthorized: true }
});

await client.connect();
```

## 核心流程

### 1. 單一 Client 連線

```typescript
import { Client } from "pg";

const client = new Client({
  host: process.env.AZURE_POSTGRESQL_HOST,
  database: process.env.AZURE_POSTGRESQL_DATABASE,
  user: process.env.AZURE_POSTGRESQL_USER,
  password: process.env.AZURE_POSTGRESQL_PASSWORD,
  port: 5432,
  ssl: { rejectUnauthorized: true }
});

try {
  await client.connect();
  
  const result = await client.query("SELECT NOW() as current_time");
  console.log(result.rows[0].current_time);
} finally {
  await client.end();  // 一定要關閉連線
}
```

### 2. Connection Pool（正式環境建議使用）

```typescript
import { Pool } from "pg";

const pool = new Pool({
  host: process.env.AZURE_POSTGRESQL_HOST,
  database: process.env.AZURE_POSTGRESQL_DATABASE,
  user: process.env.AZURE_POSTGRESQL_USER,
  password: process.env.AZURE_POSTGRESQL_PASSWORD,
  port: 5432,
  ssl: { rejectUnauthorized: true },
  
  // Pool 設定
  max: 20,                    // pool 中的最大連線數
  idleTimeoutMillis: 30000,   // 閒置 30 秒後關閉閒置連線
  connectionTimeoutMillis: 10000  // 建立新連線的 timeout
});

// 用 pool 查詢（自動取得並釋放連線）
const result = await pool.query("SELECT * FROM users WHERE id = $1", [userId]);

// 為多個查詢明確借出連線
const client = await pool.connect();
try {
  const res1 = await client.query("SELECT * FROM users");
  const res2 = await client.query("SELECT * FROM orders");
} finally {
  client.release();  // 把連線還給 pool
}

// shutdown 時清理
await pool.end();
```

### 3. 參數化查詢（防止 SQL Injection）

```typescript
// 一律使用參數化查詢，絕對不要直接串接使用者輸入
const userId = 123;
const email = "user@example.com";

// 單一參數
const result = await pool.query(
  "SELECT * FROM users WHERE id = $1",
  [userId]
);

// 多個參數
const result = await pool.query(
  "INSERT INTO users (email, name, created_at) VALUES ($1, $2, NOW()) RETURNING *",
  [email, "John Doe"]
);

// 陣列參數
const ids = [1, 2, 3, 4, 5];
const result = await pool.query(
  "SELECT * FROM users WHERE id = ANY($1::int[])",
  [ids]
);
```

### 4. Transaction

```typescript
const client = await pool.connect();

try {
  await client.query("BEGIN");
  
  const userResult = await client.query(
    "INSERT INTO users (email) VALUES ($1) RETURNING id",
    ["user@example.com"]
  );
  const userId = userResult.rows[0].id;
  
  await client.query(
    "INSERT INTO orders (user_id, total) VALUES ($1, $2)",
    [userId, 99.99]
  );
  
  await client.query("COMMIT");
} catch (error) {
  await client.query("ROLLBACK");
  throw error;
} finally {
  client.release();
}
```

### 5. Transaction 輔助函式

```typescript
async function withTransaction<T>(
  pool: Pool,
  fn: (client: PoolClient) => Promise<T>
): Promise<T> {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const result = await fn(client);
    await client.query("COMMIT");
    return result;
  } catch (error) {
    await client.query("ROLLBACK");
    throw error;
  } finally {
    client.release();
  }
}

// 用法
const order = await withTransaction(pool, async (client) => {
  const user = await client.query(
    "INSERT INTO users (email) VALUES ($1) RETURNING *",
    ["user@example.com"]
  );
  const order = await client.query(
    "INSERT INTO orders (user_id, total) VALUES ($1, $2) RETURNING *",
    [user.rows[0].id, 99.99]
  );
  return order.rows[0];
});
```

### 6. 搭配 TypeScript 的型別化查詢

```typescript
import { Pool, QueryResult } from "pg";

interface User {
  id: number;
  email: string;
  name: string;
  created_at: Date;
}

// 替查詢結果指定型別
const result: QueryResult<User> = await pool.query<User>(
  "SELECT * FROM users WHERE id = $1",
  [userId]
);

const user: User | undefined = result.rows[0];

// 型別安全的 insert
async function createUser(
  pool: Pool,
  email: string,
  name: string
): Promise<User> {
  const result = await pool.query<User>(
    "INSERT INTO users (email, name) VALUES ($1, $2) RETURNING *",
    [email, name]
  );
  return result.rows[0];
}
```

## 搭配 Entra ID Token 更新的 Pool

長時間執行的應用程式，token 會過期，需要更新：

```typescript
import { Pool, PoolConfig } from "pg";
import { DefaultAzureCredential, AccessToken } from "@azure/identity";

class AzurePostgresPool {
  private pool: Pool | null = null;
  private credential: DefaultAzureCredential;
  private tokenExpiry: Date | null = null;
  private config: Omit<PoolConfig, "password">;

  constructor(config: Omit<PoolConfig, "password">) {
    this.credential = new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]});
    this.config = config;
  }

  private async getToken(): Promise<string> {
    const tokenResponse = await this.credential.getToken(
      "https://ossrdbms-aad.database.windows.net/.default"
    );
    this.tokenExpiry = new Date(tokenResponse.expiresOnTimestamp);
    return tokenResponse.token;
  }

  private isTokenExpired(): boolean {
    if (!this.tokenExpiry) return true;
    // 在過期前 5 分鐘更新
    return new Date() >= new Date(this.tokenExpiry.getTime() - 5 * 60 * 1000);
  }

  async getPool(): Promise<Pool> {
    if (this.pool && !this.isTokenExpired()) {
      return this.pool;
    }

    // token 過期時關閉現有的 pool
    if (this.pool) {
      await this.pool.end();
    }

    const token = await this.getToken();
    this.pool = new Pool({
      ...this.config,
      password: token
    });

    return this.pool;
  }

  async query<T>(text: string, params?: any[]): Promise<QueryResult<T>> {
    const pool = await this.getPool();
    return pool.query<T>(text, params);
  }

  async end(): Promise<void> {
    if (this.pool) {
      await this.pool.end();
      this.pool = null;
    }
  }
}

// 用法
const azurePool = new AzurePostgresPool({
  host: process.env.AZURE_POSTGRESQL_HOST!,
  database: process.env.AZURE_POSTGRESQL_DATABASE!,
  user: process.env.AZURE_POSTGRESQL_USER!,
  port: 5432,
  ssl: { rejectUnauthorized: true },
  max: 20
});

const result = await azurePool.query("SELECT NOW()");
```

## 錯誤處理

```typescript
import { DatabaseError } from "pg";

try {
  await pool.query("INSERT INTO users (email) VALUES ($1)", [email]);
} catch (error) {
  if (error instanceof DatabaseError) {
    switch (error.code) {
      case "23505":  // unique_violation（違反唯一約束）
        console.error("Duplicate entry:", error.detail);
        break;
      case "23503":  // foreign_key_violation（違反外鍵約束）
        console.error("Foreign key constraint failed:", error.detail);
        break;
      case "42P01":  // undefined_table（資料表不存在）
        console.error("Table does not exist:", error.message);
        break;
      case "28P01":  // invalid_password（密碼錯誤）
        console.error("Authentication failed");
        break;
      case "57P03":  // cannot_connect_now（server 啟動中）
        console.error("Server unavailable, retry later");
        break;
      default:
        console.error(`PostgreSQL error ${error.code}: ${error.message}`);
    }
  }
  throw error;
}
```

## Connection String 格式

```typescript
// 替代做法：使用 connection string
const pool = new Pool({
  connectionString: `postgres://${user}:${password}@${host}:${port}/${database}?sslmode=require`
});

// 要求 SSL（Azure）
const connectionString = 
  `postgres://user:password@server.postgres.database.azure.com:5432/mydb?sslmode=require`;
```

## Pool 事件

```typescript
const pool = new Pool({ /* config */ });

pool.on("connect", (client) => {
  console.log("New client connected to pool");
});

pool.on("acquire", (client) => {
  console.log("Client checked out from pool");
});

pool.on("release", (err, client) => {
  console.log("Client returned to pool");
});

pool.on("remove", (client) => {
  console.log("Client removed from pool");
});

pool.on("error", (err, client) => {
  console.error("Unexpected pool error:", err);
});
```

## Azure 專屬設定

| 設定 | 值 | 說明 |
|---------|-------|-------------|
| `ssl.rejectUnauthorized` | `true` | Azure 一律使用 SSL |
| 預設 port | `5432` | 標準 PostgreSQL port |
| PgBouncer port | `6432` | 啟用 PgBouncer 時使用 |
| Token scope | `https://ossrdbms-aad.database.windows.net/.default` | Entra ID token scope |
| Token 有效期 | 約 1 小時 | 過期前要更新 |

## Pool 大小建議

| 工作負載 | `max` | `idleTimeoutMillis` |
|----------|-------|---------------------|
| 輕量（dev/test） | 5-10 | 30000 |
| 中等（正式環境） | 20-30 | 30000 |
| 重度（高並行） | 50-100 | 10000 |

> **Note**：Azure PostgreSQL 的連線數上限依 SKU 而定。請確認你那個層級的最大連線數。

## 最佳實務

1. **正式環境的應用程式一律使用 connection pool**
2. **使用參數化查詢**：絕對不要直接串接使用者輸入
3. **一律關閉連線**：用 `try/finally` 或 connection pool
4. **啟用 SSL**：Azure 必須設定（`ssl: { rejectUnauthorized: true }`）
5. **處理 token 更新**：Entra ID token 約 1 小時後過期
6. **設定連線 timeout**：避免網路問題造成卡住
7. **使用 transaction**：用於多個語句的操作
8. **監控 pool 指標**：追蹤 `pool.totalCount`、`pool.idleCount`、`pool.waitingCount`
9. **優雅地 shutdown**：應用程式結束時呼叫 `pool.end()`
10. **使用 TypeScript generic**：替查詢結果加上型別，更安全

## 主要型別

```typescript
import {
  Client,
  Pool,
  PoolClient,
  PoolConfig,
  QueryResult,
  QueryResultRow,
  DatabaseError,
  QueryConfig
} from "pg";
```

## 參考連結

| 資源 | URL |
|----------|-----|
| node-postgres 文件 | https://node-postgres.com |
| npm 套件 | https://www.npmjs.com/package/pg |
| GitHub 儲存庫 | https://github.com/brianc/node-postgres |
| Azure PostgreSQL 文件 | https://learn.microsoft.com/azure/postgresql/flexible-server/ |
| 免密碼連線 | https://learn.microsoft.com/azure/postgresql/flexible-server/how-to-connect-with-managed-identity |
