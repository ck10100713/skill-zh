---
name: prisma-patterns
description: TypeScript 後端的 Prisma ORM 模式：schema 設計、查詢最佳化、transaction、分頁，以及幾個關鍵陷阱，例如 updateMany 回傳的是筆數而不是紀錄、$transaction 會 timeout、migrate dev 會重設資料庫、批次寫入會跳過 @updatedAt，以及 serverless 連線耗盡。撰寫 Prisma schema 或查詢，或排查 transaction、migration 或 serverless 連線上限的問題時使用。
metadata:
  origin: ECC
---

# Prisma Patterns

TypeScript 後端使用 Prisma ORM 的正式環境模式，以及不明顯的陷阱。

> **套用這些模式之前，先確認你的版本。** Prisma 的 API 介面在各個主要版本之間一直在演進：
>
> ```bash
> npx prisma --version
> ```
>
> 各版本之間值得注意的 API 差異：
> - `relationJoins` 可以用 JOIN 載入關聯，而不是分開的查詢，但在大型的 1:N 關聯或很深的 `include` 上可能造成資料列暴增，兩種做法都要 benchmark
> - 新增了 `omit` 欄位修飾詞和 `prisma.$extends` Client Extensions API
> - **較新的安裝**：套件名稱可能是 `prisma`，而不是 `@prisma/client`；`PrismaClient` 可能需要 driver adapter（例如 `@prisma/adapter-pg`）；`datasource.url` 可能放在 `prisma.config.ts`，而不是 `schema.prisma`
> - CLI 指令（`migrate dev`、`migrate deploy`、`generate`）在各版本之間沒有變

## 何時啟用

- 設計或修改 Prisma 的 schema model 和關聯
- 撰寫查詢、transaction 或分頁邏輯
- 使用 `updateMany`、`deleteMany` 或任何批次操作
- 執行或規劃資料庫 migration
- 部署到 serverless 環境（Vercel、Lambda、Cloudflare Workers）
- 實作 soft delete 或多租戶的資料列過濾

## 核心概念

### ID 策略

| 策略 | 適用時機 | 避免時機 |
|---|---|---|
| `@default(cuid())` | 預設選擇，URL 安全、可排序、不會碰撞 | 外部系統需要連續 ID 的時候 |
| `@default(uuid())` | 需要跟非 Prisma 的系統互通 | 高寫入量的資料表（隨機 UUID 會讓 B-tree 索引碎片化） |
| `@default(autoincrement())` | 內部的 join table、稽核紀錄 | 對外公開的 ID（會暴露紀錄數量） |

### Schema 預設值

```prisma
model User {
  id        String    @id @default(cuid())
  email     String    @unique  // @unique 已經會建立索引，不需要再加 @@index
  name      String
  role      Role      @default(USER)
  posts     Post[]
  createdAt DateTime  @default(now())
  updatedAt DateTime  @updatedAt
  deletedAt DateTime?

  @@index([createdAt])
  @@index([deletedAt, createdAt]) // soft delete + 排序查詢用的複合索引
}
```

- 每個外鍵，以及每個用在 `WHERE` 或 `ORDER BY` 的欄位，都要加 `@@index`。
- 如果可預見會需要 soft delete，就事先宣告 `deletedAt DateTime?`，之後才加的話，要對正在線上的資料表做 migration。
- `updatedAt @updatedAt` 只有在 `update` 和 `upsert` 時，Prisma 才會自動設定（批次更新的陷阱見反模式）。

### `include` 和 `select`

| | `include` | `select` |
|---|---|---|
| 回傳 | 所有純量欄位 + 指定的關聯 | 只有指定的欄位 |
| 適用時機 | 你需要大部分欄位再加上一個關聯 | 熱點路徑、大型資料表、避免過度撈取 |
| 效能 | 在欄位很多的資料表上可能過度撈取 | payload 最小，大型資料集上比較快 |
| Prisma 5 備註 | 預設使用 JOIN（`relationJoins`） | 相同 |

```ts
// include：所有欄位 + 關聯
const user = await prisma.user.findUnique({
  where: { id },
  include: { posts: { select: { id: true, title: true } } },
});

// select：明確的 allowlist
const user = await prisma.user.findUnique({
  where: { id },
  select: { id: true, email: true, name: true },
});
```

絕對不要在 API 回應裡直接回傳原始的 Prisma entity，要對應到回應用的 DTO，來控制公開的欄位：

```ts
// BAD: 會洩漏 passwordHash、deletedAt 和內部欄位
return await prisma.user.findUniqueOrThrow({ where: { id } });

// GOOD: 明確對應到 DTO
const user = await prisma.user.findUniqueOrThrow({ where: { id } });
return { id: user.id, name: user.name, email: user.email };
```

### Transaction 形式的選擇

| 情況 | 使用 |
|---|---|
| 彼此獨立的操作，沒有相依關係 | Array 形式 |
| 後面的步驟依賴前面的結果 | Interactive 形式 |
| 牽涉到外部呼叫（email、HTTP） | 完全放在 transaction 外面 |

```ts
// Array 形式：批次在一次 round trip 內完成
const [user, post] = await prisma.$transaction([
  prisma.user.update({ where: { id }, data: { name } }),
  prisma.post.create({ data: { title, authorId: id } }),
]);

// Interactive 形式：只能用 tx client，絕對不要用外層的 prisma client
const post = await prisma.$transaction(async (tx) => {
  const user = await tx.user.findUniqueOrThrow({ where: { id } });
  if (user.role !== 'ADMIN') throw new Error('Forbidden');
  return tx.post.create({ data: { title, authorId: user.id } });
});
```

### PrismaClient Singleton

每個 `PrismaClient` 實例都會開自己的連線池。只實例化一次。

```ts
// lib/prisma.ts

// 選項 A：以 adapter 初始化（較新的 Prisma 安裝需要這樣做）
import { PrismaClient } from '@prisma/client'; // 或你的環境產生出來的 client 路徑
import { PrismaPg } from '@prisma/adapter-pg';

function createPrismaClient() {
  const adapter = new PrismaPg({
    connectionString: process.env.DATABASE_URL!,
  });
  return new PrismaClient({
    adapter,
    log: process.env.NODE_ENV === 'development' ? ['query', 'error'] : ['error'],
  });
}

const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient };

export const prisma = globalForPrisma.prisma ?? createPrismaClient();

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;

// 選項 B：直接初始化（較舊的安裝，不需要 adapter）
// import { PrismaClient } from '@prisma/client';
// export const prisma = globalForPrisma.prisma ?? new PrismaClient({ ... });
```

如果你的 Prisma 安裝需要在 `PrismaClient` 建構子傳入 `adapter` 引數，就用選項 A。
如果 `new PrismaClient()` 不帶引數就能運作，就用選項 B。哪個正確，讓編譯器告訴你。

`globalThis` 這個寫法可以避免 hot reload（Next.js、nodemon、ts-node-dev）時產生重複的實例。

### N+1 問題

在迴圈裡載入關聯，每一列都會發出一次查詢。

```ts
// BAD: N+1，每個 user 多一次查詢
const users = await prisma.user.findMany();
for (const user of users) {
  const posts = await prisma.post.findMany({ where: { authorId: user.id } });
}

// GOOD: 單一查詢
const users = await prisma.user.findMany({ include: { posts: true } });
```

在 Prisma 5+ 的 `relationJoins` 下，`include` 的寫法會用單一 JOIN。在大型的 1:N 集合上，這可能讓結果集變大；如果每個 parent 可能回傳很多列關聯資料，兩種做法都要 benchmark。

## 程式碼範例

### Cursor 分頁（feed 和大型資料集的首選）

```ts
async function getPosts(cursor?: string, limit = 20) {
  const items = await prisma.post.findMany({
    where: { published: true },
    orderBy: [
      { createdAt: 'desc' },
      { id: 'desc' }, // 次要排序，避免時間戳記重複時分頁不穩定
    ],
    take: limit + 1,
    ...(cursor && { cursor: { id: cursor }, skip: 1 }),
  });

  const hasNextPage = items.length > limit;
  if (hasNextPage) items.pop();

  return { items, nextCursor: hasNextPage ? items[items.length - 1].id : null };
}
```

多撈 `limit + 1` 筆再 pop 掉，是不用額外 count 查詢就能偵測 `hasNextPage` 的標準做法。一定要把唯一欄位（例如 `id`）當成次要的 `orderBy`，避免多筆資料時間戳記相同時分頁不穩定。只有在使用者需要跳到任意頁面時（管理後台的表格）才用 offset 分頁。

### Soft Delete

```ts
// 一律明確過濾，不要依賴 middleware（會藏住行為，難以 debug）
const activeUsers = await prisma.user.findMany({ where: { deletedAt: null } });

await prisma.user.update({ where: { id }, data: { deletedAt: new Date() } });
await prisma.user.update({ where: { id }, data: { deletedAt: null } }); // 還原
```

### 錯誤處理

```ts
import { Prisma } from '@prisma/client'; // 或你的環境產生出來的 client 路徑

try {
  await prisma.user.create({ data: { email } });
} catch (e) {
  if (e instanceof Prisma.PrismaClientKnownRequestError) {
    if (e.code === 'P2002') throw new ConflictError('Email already exists');
    if (e.code === 'P2025') throw new NotFoundError('Record not found');
    if (e.code === 'P2003') throw new BadRequestError('Referenced record does not exist');
  }
  throw e;
}
```

常見的錯誤碼：`P2002` 違反唯一性 · `P2025` 找不到 · `P2003` 違反外鍵。

在 service 邊界捕捉並轉成領域錯誤。絕對不要把原始的 Prisma 訊息暴露給 API 使用者。

### 連線池：Serverless

連線參數直接內嵌在 `DATABASE_URL` 裡，如果 URL 已經有 query 參數（例如 `?schema=public`），用字串串接會壞掉：

```bash
# .env：建議把參數內嵌在 URL 裡
DATABASE_URL="postgresql://user:pass@host/db?connection_limit=1&pool_timeout=20"

# 搭配外部的 pooler（PgBouncer、Supabase pooler）
DATABASE_URL="postgresql://user:pass@host/db?pgbouncer=true&connection_limit=1"
```

```ts
// Vercel、AWS Lambda 和類似的 serverless runtime：
// 每個實例把連線池上限設成 1；connection_limit 和 pool_timeout 由 DATABASE_URL 控制

// 以 adapter 設定（如果你的 Prisma 安裝需要 adapter）：
import { PrismaClient } from '@prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';

const prisma = new PrismaClient({
  adapter: new PrismaPg({ connectionString: process.env.DATABASE_URL }),
});

// 直接設定（如果你的 Prisma 安裝不需要 adapter）：
// const prisma = new PrismaClient();
```

## 反模式

### `updateMany` 回傳的是筆數，不是紀錄

```ts
// BAD: 結果是 { count: 2 }，users[0] 是 undefined
const users = await prisma.user.updateMany({ where: { role: 'GUEST' }, data: { role: 'USER' } });

// GOOD: 先抓 ID，再更新，最後只撈受影響的列
const targets = await prisma.user.findMany({
  where: { role: 'GUEST' },
  select: { id: true },
});
const ids = targets.map((u) => u.id);
await prisma.user.updateMany({ where: { id: { in: ids } }, data: { role: 'USER' } });
const updated = await prisma.user.findMany({ where: { id: { in: ids } } });
```

`deleteMany` 也一樣，回傳 `{ count: n }`，絕對不會回傳被刪掉的列。

### `$transaction` 的 interactive 形式 5 秒後會 timeout

```ts
// BAD: transaction 裡的外部呼叫超過預設的 5 秒 → 「Transaction already closed」
await prisma.$transaction(async (tx) => {
  const user = await tx.user.findUniqueOrThrow({ where: { id } });
  await sendWelcomeEmail(user.email); // 外部呼叫
  await tx.user.update({ where: { id }, data: { emailSent: true } });
});

// GOOD: 外部呼叫放在 transaction 外面
const user = await prisma.user.findUniqueOrThrow({ where: { id } });
await sendWelcomeEmail(user.email);
await prisma.user.update({ where: { id }, data: { emailSent: true } });

// 只有批次處理真的需要時，才調高 timeout
await prisma.$transaction(async (tx) => { ... }, { timeout: 30_000 });
```

### `migrate dev` 可能會重設資料庫

`migrate dev` 偵測到 schema drift 時，可能會提示要重設資料庫，把所有資料清掉。

```bash
# 在共用的 dev、staging 或 production 上絕對不要用
npx prisma migrate dev --name add_column

# 除了本機單人開發以外，到處都安全
npx prisma migrate deploy

# 檢查 drift 但不套用
npx prisma migrate diff \
  --from-migrations ./prisma/migrations \
  --to-schema-datamodel ./prisma/schema.prisma \
  --shadow-database-url "$SHADOW_DATABASE_URL"
```

### 手動編輯 migration 檔案會讓之後的 deploy 壞掉

Prisma 會對每個 migration 檔案做 checksum。套用之後再編輯，會讓每個已經跑過原版的環境都出現 `P3006 checksum mismatch`。要改的話，請另外建立新的 migration。

### 破壞性的 schema 變更需要多步驟 migration

在一次 migration 裡替現有欄位加上 `NOT NULL`，或重新命名欄位，會鎖住資料表或掉資料。請用 expand-and-contract：

```bash
# Step 1: 在本機建立 migration，然後 deploy
npx prisma migrate dev --name add_new_column   # 只限本機
npx prisma migrate deploy                       # staging / production
```

```ts
// Step 2: 回填資料（在 script 或 migration job 裡執行，不要在 shell 裡跑）
await prisma.user.updateMany({ data: { newColumn: derivedValue } });
```

```bash
# Step 3: 在本機建立 NOT NULL 限制的 migration，然後 deploy
npx prisma migrate dev --name make_new_column_required  # 只限本機
npx prisma migrate deploy                               # staging / production
```

### `@updatedAt` 不會在 `updateMany` 時觸發

`@updatedAt` 只會在 `update` 和 `upsert` 時自動設定。批次寫入會讓它保持舊值。

```ts
// BAD: updatedAt 維持舊值
await prisma.post.updateMany({ where: { authorId }, data: { published: true } });

// GOOD
await prisma.post.updateMany({
  where: { authorId },
  data: { published: true, updatedAt: new Date() },
});
```

### Soft delete + `findUniqueOrThrow` 會洩漏已刪除的紀錄

`findUniqueOrThrow` 只有在資料庫裡真的沒有那一列時，才會丟出 `P2025`。被 soft delete 的列仍然存在，會不報錯地被回傳。

`findUniqueOrThrow` 的 `where` 需要放唯一限制的欄位，在 `id` 旁邊加上 `deletedAt: null` 會讓型別出錯，因為 `{ id, deletedAt }` 不是複合唯一限制。請改用 `findFirstOrThrow`。

```ts
// BAD: 會回傳被 soft delete 的 user
const user = await prisma.user.findUniqueOrThrow({ where: { id } });

// BAD: Prisma 型別錯誤，{ id, deletedAt } 不是唯一限制
const user = await prisma.user.findUniqueOrThrow({ where: { id, deletedAt: null } });

// GOOD: findFirstOrThrow 支援任意的 where 條件
const user = await prisma.user.findFirstOrThrow({ where: { id, deletedAt: null } });
```

### 沒有 `where` 的 `deleteMany` 會刪掉每一列

```ts
// BAD: 悄悄把整張表清空
await prisma.post.deleteMany();

// GOOD
await prisma.post.deleteMany({ where: { authorId: userId } });
```

## 最佳實踐

| 規則 | 原因 |
|---|---|
| CI/CD 用 `migrate deploy`，`migrate dev` 只在本機用 | `migrate dev` 遇到 drift 時可能重設資料庫 |
| 把 entity 對應到回應用的 DTO | 避免洩漏內部欄位 |
| 在 service 邊界捕捉 `PrismaClientKnownRequestError` | 轉成領域錯誤 |
| 優先用 `*OrThrow` 方法，不要手動檢查 null | 會自動丟出 P2025；過濾非唯一欄位時用 `findFirstOrThrow` |
| Serverless 用 `connection_limit=1` + 外部 pooler | 避免連線耗盡 |
| `deleteMany` 一定要給 `where` | 避免不小心清空整張表 |
| 在 `updateMany` 裡手動設定 `updatedAt: new Date()` | `@updatedAt` 會跳過批次寫入 |

## 相關 Skills

- `nestjs-patterns`：整合 Prisma 的 NestJS service 層
- `postgres-patterns`：PostgreSQL 層級的索引和連線調校
- `database-migrations`：正式環境的多步驟 migration 規劃
- `backend-patterns`：通用的 API 與 service 層設計
