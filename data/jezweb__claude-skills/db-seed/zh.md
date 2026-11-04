---
name: db-seed
description: "產生帶有擬真範例資料的資料庫 seed 腳本。讀取 Drizzle schema 或 SQL migration，遵守外鍵的順序，產出具冪等性的 TypeScript 或 SQL seed 檔。處理 D1 的批次限制、唯一約束，以及符合領域的資料。填充 dev/demo/test 資料庫時使用。觸發詞：'seed database', 'seed data', 'sample data', 'populate database', 'db seed', 'test data', 'demo data', 'generate fixtures'。"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
compatibility: claude-code-only
---

# Database Seed Generator

產生 seed 腳本，用擬真、符合領域的範例資料填充資料庫。讀取你的 schema，產出可以直接執行的 seed 檔。

## 工作流程

### 1. 找出 Schema

掃描專案裡的 schema 定義：

| 來源 | 位置模式 |
|--------|-----------------|
| Drizzle schema | `src/db/schema.ts`、`src/schema/*.ts`、`db/schema.ts` |
| D1 migrations | `drizzle/*.sql`、`migrations/*.sql` |
| 原始 SQL | `schema.sql`、`db/*.sql` |
| Prisma | `prisma/schema.prisma` |

讀完所有 schema 檔案。在腦中建立這些的模型：
- 資料表和它們的欄位
- 資料型別和約束（NOT NULL、UNIQUE、DEFAULT）
- 外鍵關聯（哪些資料表參照哪些）
- 以 TEXT 儲存的 JSON 欄位（D1/SQLite 常見）

### 2. 決定 Seed 參數

詢問使用者：

| 參數 | 選項 | 預設 |
|-----------|---------|---------|
| 目的 | dev、demo、testing | dev |
| 資料量 | small（每張表 5-10 列）、medium（20-50）、large（100+） | small |
| 領域脈絡 | 「電商商店」、「SaaS app」、「部落格」等 | 從 schema 推斷 |
| 輸出格式 | TypeScript (Drizzle)、原始 SQL，或兩者都要 | 配合專案用的 ORM |

**目的會影響資料品質**：
- **dev**：資料多樣，包含一些邊界情況（空欄位、很長的字串、unicode）
- **demo**：精緻的資料，放在截圖和簡報裡好看
- **testing**：有系統地涵蓋邊界條件、重複、特殊字元的資料

### 3. 規劃 Insert 順序

從外鍵建立相依圖。先 insert 父資料表，再 insert 子資料表。

部落格 schema 的順序範例：
```
1. users        (no dependencies)
2. categories   (no dependencies)
3. posts        (depends on users, categories)
4. comments     (depends on users, posts)
5. tags         (no dependencies)
6. post_tags    (depends on posts, tags)
```

**循環相依**：如果資料表 A 參照 B、B 又參照 A，就用可為 NULL 的外鍵，分兩輪 insert（先用 NULL insert，再 UPDATE）。

### 4. 產生擬真的資料

**不要用通用的佔位符**，像是 "test123"、"foo@bar.com" 或 "Lorem ipsum"。產生符合領域的資料。

#### 資料產生模式（不需要外部函式庫）

**姓名**：用寫死的常見姓名清單。混合不同性別和文化背景。
```typescript
const firstNames = ['Sarah', 'James', 'Priya', 'Mohammed', 'Emma', 'Wei', 'Carlos', 'Aisha'];
const lastNames = ['Chen', 'Smith', 'Patel', 'Garcia', 'Kim', 'O\'Brien', 'Nguyen', 'Wilson'];
```

**Email**：從姓名衍生，例如 `sarah.chen@example.com`。用 `example.com` 網域（RFC 2606 保留）。

**日期**：在合理的範圍內產生。D1/SQLite 用 ISO 8601 格式。
```typescript
const randomDate = (daysBack: number) => {
  const d = new Date();
  d.setDate(d.getDate() - Math.floor(Math.random() * daysBack));
  return d.toISOString();
};
```

**ID**：UUID 用 `crypto.randomUUID()`，schema 用自動遞增的話就用循序整數。

**確定性 seed**：要產生可重現的資料，用有 seed 的 PRNG：
```typescript
function seededRandom(seed: number) {
  return () => {
    seed = (seed * 16807) % 2147483647;
    return (seed - 1) / 2147483646;
  };
}
const rand = seededRandom(42); // Same seed = same data every time
```

**價格/金額**：用貼近真實的範圍。`(rand() * 900 + 100).toFixed(2)` 對應 $1-$10 的範圍。

**描述/內容**：每種內容類型寫 3 到 5 個擬真的變化版本，輪流使用。不要產生聽起來像 AI 的文字，要寫得像真實的使用者資料。

### 5. 輸出格式

#### TypeScript (Drizzle ORM)

```typescript
// scripts/seed.ts
import { drizzle } from 'drizzle-orm/d1';
import * as schema from '../src/db/schema';

export async function seed(db: ReturnType<typeof drizzle>) {
  console.log('Seeding database...');

  // Clear existing data (reverse dependency order)
  await db.delete(schema.comments);
  await db.delete(schema.posts);
  await db.delete(schema.users);

  // Insert users
  const users = [
    { id: crypto.randomUUID(), name: 'Sarah Chen', email: 'sarah@example.com', ... },
    // ...
  ];

  // D1 batch limit: 10 rows per INSERT
  for (let i = 0; i < users.length; i += 10) {
    await db.insert(schema.users).values(users.slice(i, i + 10));
  }

  // Insert posts (references users)
  const posts = [
    { id: crypto.randomUUID(), userId: users[0].id, title: '...', ... },
    // ...
  ];

  for (let i = 0; i < posts.length; i += 10) {
    await db.insert(schema.posts).values(posts.slice(i, i + 10));
  }

  console.log(`Seeded: ${users.length} users, ${posts.length} posts`);
}
```

執行方式：`npx tsx scripts/seed.ts`

給 Cloudflare Workers 用的話，加一個 seed endpoint（上線前要移除）：
```typescript
app.post('/api/seed', async (c) => {
  const db = drizzle(c.env.DB);
  await seed(db);
  return c.json({ ok: true });
});
```

#### 原始 SQL (D1)

```sql
-- seed.sql
-- Run: npx wrangler d1 execute DB_NAME --local --file=./scripts/seed.sql

-- Clear existing (reverse order)
DELETE FROM comments;
DELETE FROM posts;
DELETE FROM users;

-- Users
INSERT INTO users (id, name, email, created_at) VALUES
  ('uuid-1', 'Sarah Chen', 'sarah@example.com', '2025-01-15T10:30:00Z'),
  ('uuid-2', 'James Wilson', 'james@example.com', '2025-02-01T14:22:00Z');

-- Posts (max 10 rows per INSERT for D1)
INSERT INTO posts (id, user_id, title, body, created_at) VALUES
  ('post-1', 'uuid-1', 'Getting Started', 'Welcome to...', '2025-03-01T09:00:00Z');
```

### 6. 冪等性

Seed 腳本必須能安全地重複執行：

```typescript
// Option A: Delete-then-insert (simple, loses data)
await db.delete(schema.users);
await db.insert(schema.users).values(seedUsers);

// Option B: Upsert (preserves non-seed data)
for (const user of seedUsers) {
  await db.insert(schema.users)
    .values(user)
    .onConflictDoUpdate({ target: schema.users.id, set: user });
}
```

dev/testing 預設用選項 A，demo 用選項 B（使用者可能已經加了自己的資料）。

## D1 專屬的陷阱

| 陷阱 | 解法 |
|--------|----------|
| 每個 INSERT 最多約 10 列 | 以 10 列為單位分批 insert |
| 沒有原生 BOOLEAN | 用 INTEGER (0/1) |
| 沒有原生 DATETIME | 用 TEXT 存 ISO 8601 字串 |
| JSON 以 TEXT 儲存 | insert 之前先 `JSON.stringify()` |
| 外鍵一律強制啟用 | 先 insert 父資料表 |
| 綁定參數上限 100 個 | 讓批次大小 × 欄位數 < 100 |

## 品質規則

1. **符合領域**：電商的 seed 要有聽起來真實的商品名稱和價格，不要 "Product 1"
2. **讓資料有變化**：不要讓每個使用者都叫 "John Smith"，也不要每個價格都是 "$9.99"
3. **包含邊界情況**（給測試用的 seed）：空字串、很長的文字、特殊字元、最大值
4. **參照真實存在的 ID**：外鍵必須指向實際已 insert 的父資料列
5. **印出 seed 了什麼**：一定要記錄筆數，讓使用者知道有成功
6. **記下執行指令**：把它寫成檔案最上面的註解
