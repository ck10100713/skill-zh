---
name: d1-drizzle-schema
description: "為 Cloudflare D1 資料庫產生 Drizzle ORM schema，採用正確的 D1 專屬寫法。產出 schema 檔、migration 指令、型別匯出，以及 DATABASE_SCHEMA.md 文件。處理 D1 的特殊之處：外鍵一律強制啟用、沒有原生的 BOOLEAN/DATETIME 型別、綁定參數上限 100 個、JSON 存成 TEXT。建立新資料庫、新增資料表或建立 D1 資料層骨架時使用。"
compatibility: claude-code-only
---

# D1 Drizzle Schema

為 Cloudflare D1 產生正確的 Drizzle ORM schema。D1 以 SQLite 為基礎，但有一些重要的差異，如果照標準 SQLite 的寫法，會造成不易察覺的 bug。這個 skill 產出的 schema，能正確配合 D1 的限制。

## D1 的關鍵差異

| 功能 | 標準 SQLite | D1 |
|---------|-----------------|-----|
| 外鍵 | 預設關閉 | **一律開啟**（無法關閉） |
| Boolean 型別 | 沒有 | 沒有，用 `integer({ mode: 'boolean' })` |
| Datetime 型別 | 沒有 | 沒有，用 `integer({ mode: 'timestamp' })` |
| 綁定參數上限 | ~999 | **100**（影響批次 insert） |
| JSON 支援 | 要靠擴充 | **一律可用**（json_extract、->、->>） |
| 並行 | 多寫入者 | **單執行緒**（一次一個查詢） |

## 工作流程

### Step 1：描述資料模型

蒐集需求：有哪些資料表、什麼關聯、哪些需要索引。如果是根據現有的描述來做，就直接推導出 schema。

### Step 2：產生 Drizzle Schema

用符合 D1 的欄位寫法建立 schema 檔：

```typescript
import { sqliteTable, text, integer, real, index, uniqueIndex } from 'drizzle-orm/sqlite-core'

export const users = sqliteTable('users', {
  // UUID primary key (preferred for D1)
  id: text('id').primaryKey().$defaultFn(() => crypto.randomUUID()),

  // Text fields
  name: text('name').notNull(),
  email: text('email').notNull(),

  // Enum (stored as TEXT, validated at schema level)
  role: text('role', { enum: ['admin', 'editor', 'viewer'] }).notNull().default('viewer'),

  // Boolean (D1 has no BOOL — stored as INTEGER 0/1)
  emailVerified: integer('email_verified', { mode: 'boolean' }).notNull().default(false),

  // Timestamp (D1 has no DATETIME — stored as unix seconds)
  createdAt: integer('created_at', { mode: 'timestamp' }).notNull().$defaultFn(() => new Date()),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).notNull().$defaultFn(() => new Date()),

  // Typed JSON (stored as TEXT, Drizzle auto-serialises)
  preferences: text('preferences', { mode: 'json' }).$type<UserPreferences>(),

  // Foreign key (always enforced in D1)
  organisationId: text('organisation_id').references(() => organisations.id, { onDelete: 'cascade' }),
}, (table) => ({
  emailIdx: uniqueIndex('users_email_idx').on(table.email),
  orgIdx: index('users_org_idx').on(table.organisationId),
}))
```

完整的型別參考見 [references/column-patterns.md](references/column-patterns.md)。

### Step 3：加上 Relations

Drizzle 的 relations 是 query builder 的輔助工具（跟外鍵約束是分開的）：

```typescript
import { relations } from 'drizzle-orm'

export const usersRelations = relations(users, ({ one, many }) => ({
  organisation: one(organisations, {
    fields: [users.organisationId],
    references: [organisations.id],
  }),
  posts: many(posts),
}))
```

### Step 4：匯出型別

```typescript
export type User = typeof users.$inferSelect
export type NewUser = typeof users.$inferInsert
```

### Step 5：設定 Drizzle Config

把 [assets/drizzle-config-template.ts](assets/drizzle-config-template.ts) 複製成 `drizzle.config.ts`，並更新 schema 路徑。

### Step 6：加入 Migration 腳本

加到 `package.json`：
```json
{
  "db:generate": "drizzle-kit generate",
  "db:migrate:local": "wrangler d1 migrations apply DB --local",
  "db:migrate:remote": "wrangler d1 migrations apply DB --remote"
}
```

**測試之前，本機和遠端兩邊都一定要跑。**

### Step 7：產生 DATABASE_SCHEMA.md

把 schema 記錄下來，給之後的 session 使用：
- 資料表，含欄位、型別和約束
- 關聯和外鍵
- 索引及其用途
- Migration 流程

## 批次 Insert 的寫法

D1 把綁定參數限制在 100 個。計算批次大小：

```typescript
const BATCH_SIZE = Math.floor(100 / COLUMNS_PER_ROW)
for (let i = 0; i < rows.length; i += BATCH_SIZE) {
  await db.insert(table).values(rows.slice(i, i + BATCH_SIZE))
}
```

## D1 執行期用法

```typescript
import { drizzle } from 'drizzle-orm/d1'
import * as schema from './schema'

// In Worker fetch handler:
const db = drizzle(env.DB, { schema })

// Query patterns
const all = await db.select().from(schema.users).all()           // Array<User>
const one = await db.select().from(schema.users).where(eq(schema.users.id, id)).get()  // User | undefined
const count = await db.select({ count: sql`count(*)` }).from(schema.users).get()
```

## 參考檔案

| 什麼時候 | 讀這個 |
|------|------|
| D1 vs SQLite、JSON 查詢、限制 | [references/d1-specifics.md](references/d1-specifics.md) |
| Drizzle + D1 的欄位型別寫法 | [references/column-patterns.md](references/column-patterns.md) |

## 資源檔

| 檔案 | 用途 |
|------|---------|
| [assets/drizzle-config-template.ts](assets/drizzle-config-template.ts) | D1 用的 drizzle.config.ts 起始範本 |
| [assets/schema-template.ts](assets/schema-template.ts) | 含所有常見 D1 寫法的 schema 範例 |
