---
name: durable-objects
description: 建置、除錯或審查用於持久狀態與協調的 Cloudflare Durable Objects 程式碼。
---

# Durable Objects

用 Durable Objects 在 Cloudflare 的 edge 上建置有狀態、需要協調的應用程式。

## Retrieval Sources

你對 Durable Objects API 和設定的知識可能已經過時。任何 Durable Objects 的任務，都要**優先用檢索，不要靠預訓練記憶**。

| 資源 | URL |
|----------|-----|
| Docs | https://developers.cloudflare.com/durable-objects/index.md |
| API Reference | https://developers.cloudflare.com/durable-objects/api/index.md |
| Best Practices | https://developers.cloudflare.com/durable-objects/best-practices/index.md |
| Examples | https://developers.cloudflare.com/durable-objects/examples/index.md |
| Roles and permissions | https://developers.cloudflare.com/workers/authorization/durable-objects/index.md |

實作功能時，去抓對應的文件頁面。

## When to Use

- 建立新的 Durable Object class，用於有狀態的協調
- 實作 RPC method、alarm 或 WebSocket handler
- 審查既有的 DO 程式碼是否符合最佳實務
- 為 DO binding 和 migration 設定 wrangler.jsonc/toml
- 用 Cloudflare 的 Vitest 整合撰寫測試
- 設計 sharding 策略和父子關係

## Reference Documentation

- `./references/rules.md` - 核心規則、儲存、並行、RPC、alarm
- [Testing reference](./references/testing.md) - 目前的 Vitest 文件、遷移選項和測試選擇
- [Workers reference](./references/workers.md) - Workers handler、型別、設定、tracing 和本機除錯

搜尋關鍵字：`blockConcurrencyWhile`、`idFromName`、`getByName`、`setAlarm`、`sql.exec`

## Core Principles

### Use Durable Objects For

| 需求 | 範例 |
|------|---------|
| 協調 | 聊天室、多人遊戲、協作文件 |
| 強一致性 | 庫存、預約系統、回合制遊戲 |
| 每個實體各自的儲存 | 多租戶 SaaS、每個使用者的資料 |
| 持久連線 | WebSocket、即時通知 |
| 每個實體各自的排程工作 | 訂閱續約、遊戲逾時 |

### Do NOT Use For

- 無狀態的 request 處理（用一般的 Workers）
- 需要最大程度全球分散的情況
- 大量彼此獨立的 fan-out request

## Quick Reference

### Wrangler Configuration

```jsonc
// wrangler.jsonc
{
  "durable_objects": {
    "bindings": [{ "name": "MY_DO", "class_name": "MyDurableObject" }]
  },
  "migrations": [{ "tag": "v1", "new_sqlite_classes": ["MyDurableObject"] }]
}
```

### Basic Durable Object Pattern

```typescript
import { DurableObject } from "cloudflare:workers";

export interface Env {
  MY_DO: DurableObjectNamespace<MyDurableObject>;
}

export class MyDurableObject extends DurableObject<Env> {
  constructor(ctx: DurableObjectState, env: Env) {
    super(ctx, env);
    ctx.blockConcurrencyWhile(async () => {
      this.ctx.storage.sql.exec(`
        CREATE TABLE IF NOT EXISTS items (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          data TEXT NOT NULL
        )
      `);
    });
  }

  async addItem(data: string): Promise<number> {
    const result = this.ctx.storage.sql.exec<{ id: number }>(
      "INSERT INTO items (data) VALUES (?) RETURNING id",
      data
    );
    return result.one().id;
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const stub = env.MY_DO.getByName("my-instance");
    const id = await stub.addItem("hello");
    return Response.json({ id });
  },
};
```

## Critical Rules

1. **圍繞協調單元（coordination atom）建模** - 每個聊天室／遊戲／使用者各一個 DO，不要只有一個全域 DO
2. **用 `getByName()` 做確定性的 routing** - 輸入相同 = 同一個 DO instance
3. **用 SQLite 儲存** - 在 migration 裡設定 `new_sqlite_classes`
4. **在 constructor 裡初始化** - `blockConcurrencyWhile()` 只用在 schema 設定
5. **用 RPC method** - 不要用 fetch() handler（compatibility date >= 2024-04-03）
6. **先持久化，再快取** - 更新記憶體中的狀態之前，一定要先寫進 storage
7. **每個 DO 只有一個 alarm** - `setAlarm()` 會取代既有的 alarm

## Authorization

Durable Objects 沒有獨立的角色或權限；存取權限跟著實作它們的 Worker 走。授予 observability 或 Data Studio 存取之前，先檢索目前的 [Durable Objects authorization 指引](https://developers.cloudflare.com/workers/authorization/durable-objects/index.md)，並把 Workers 角色的範圍限定在預定的 Worker 或 Workers 產品。

## Anti-Patterns (NEVER)

- 單一全域 DO 處理所有 request（瓶頸）
- 每個 request 都用 `blockConcurrencyWhile()`（拖垮吞吐量）
- 只把關鍵狀態存在記憶體裡（被驅逐或當機就消失）
- 在相關的 storage 寫入之間用 `await`（破壞原子性）
- 讓 `blockConcurrencyWhile()` 橫跨 `fetch()` 或外部 I/O

## Stub Creation

```typescript
// 確定性的，大部分情況優先用這個
const stub = env.MY_DO.getByName("room-123");

// 從既有的 ID 字串
const id = env.MY_DO.idFromString(storedIdString);
const stub = env.MY_DO.get(id);

// 新的唯一 ID，對應關係要存在外部
const id = env.MY_DO.newUniqueId();
const stub = env.MY_DO.get(id);
```

## Storage Operations

```typescript
// SQL（同步，建議使用）
this.ctx.storage.sql.exec("INSERT INTO t (c) VALUES (?)", value);
const rows = this.ctx.storage.sql.exec<Row>("SELECT * FROM t").toArray();

// KV（非同步）
await this.ctx.storage.put("key", value);
const val = await this.ctx.storage.get<Type>("key");
```

## Alarms

```typescript
// 排程（會取代既有的）
await this.ctx.storage.setAlarm(Date.now() + 60_000);

// Handler
async alarm(): Promise<void> {
  // 處理排程的工作
  // 也可以重新排程：await this.ctx.storage.setAlarm(...)
}

// 取消
await this.ctx.storage.deleteAlarm();
```

## Testing

設定測試套件或撰寫 Durable Object 測試之前，先讀 [testing reference](./references/testing.md)。它會帶你到目前的設定、API 和範例，並指出該涵蓋哪些行為。

## Skill feedback

如果使用者反映這個 skill 給了錯誤或過時的指引，或是缺了資訊，就去讀 [references/skill-feedback.md](references/skill-feedback.md)。
