---
name: tanstack-start
description: "從零開始在 Cloudflare Workers 上建一個全端 TanStack Start app：SSR、file-based routing、server function、D1+Drizzle、better-auth、Tailwind v4+shadcn/ui。只要使用者提到 TanStack Start、要用 SSR 做全端 Cloudflare app 的腳手架、想要 SSR 儀表板，或要一個 React 19 + Cloudflare Workers、有 file-based routing 和 server function 的 app，就用這個 skill，即使他沒有明講 TanStack Start。沒有 template repo，Claude 會針對每個專案重新產生每一個檔案。"
compatibility: claude-code-only
---

# TanStack Start on Cloudflare

從零建出一個完整的全端 app。每個檔案都由 Claude 產生，不 clone template，也不用 scaffold 指令。

技術堆疊：TanStack Start v1（SSR、file-based routing、透過 Nitro 的 server function）跑在 Cloudflare Workers 上；React 19 + Tailwind v4 + shadcn/ui；D1 + Drizzle；better-auth（Google OAuth + email/password）。

## 專案檔案樹

```
PROJECT_NAME/
├── src/
│   ├── routes/
│   │   ├── __root.tsx              # 根 layout（HTML 外殼、主題、CSS import）
│   │   ├── index.tsx               # 首頁 / 驗證導向
│   │   ├── login.tsx               # 登入頁
│   │   ├── register.tsx            # 註冊頁
│   │   ├── _authed.tsx             # 驗證守衛 layout route
│   │   ├── _authed/
│   │   │   ├── dashboard.tsx       # 有統計卡片的儀表板
│   │   │   ├── items.tsx           # Item 列表表格
│   │   │   ├── items.$id.tsx       # 編輯 item
│   │   │   └── items.new.tsx       # 建立 item
│   │   └── api/
│   │       └── auth/
│   │           └── $.ts            # better-auth API catch-all
│   ├── components/
│   │   ├── ui/                     # shadcn/ui 元件（自動安裝）
│   │   ├── app-sidebar.tsx         # 導覽側邊欄
│   │   ├── theme-toggle.tsx        # Light/dark/system 切換
│   │   ├── user-nav.tsx            # 使用者下拉選單
│   │   └── stat-card.tsx           # 儀表板統計卡片
│   ├── db/
│   │   ├── schema.ts               # Drizzle schema（所有資料表）
│   │   └── index.ts                # Drizzle client factory
│   ├── lib/
│   │   ├── auth.server.ts          # better-auth server 設定
│   │   ├── auth.client.ts          # better-auth React hook
│   │   └── utils.ts                # shadcn/ui 用的 cn() helper
│   ├── server/
│   │   └── functions.ts            # Server function（CRUD、驗證檢查）
│   ├── styles/
│   │   └── app.css                 # Tailwind v4 + shadcn/ui CSS 變數
│   ├── router.tsx                  # TanStack Router 設定
│   ├── client.tsx                  # Client 進入點（hydrateRoot）
│   ├── ssr.tsx                     # SSR 進入點
│   └── routeTree.gen.ts            # 自動產生的 route tree（不要編輯）
├── drizzle/                        # 產生出來的 migration
├── public/                         # 靜態資產（favicon 等）
├── vite.config.ts
├── wrangler.jsonc
├── drizzle.config.ts
├── tsconfig.json
├── package.json
├── .dev.vars                       # 本機環境變數（不要 commit）
└── .gitignore
```

## 相依套件

**Runtime：**
```json
{
  "react": "^19.0.0",
  "react-dom": "^19.0.0",
  "@tanstack/react-router": "^1.120.0",
  "@tanstack/react-start": "^1.120.0",
  "drizzle-orm": "^0.38.0",
  "better-auth": "^1.2.0",
  "zod": "^3.24.0",
  "class-variance-authority": "^0.7.0",
  "clsx": "^2.1.0",
  "tailwind-merge": "^3.0.0",
  "lucide-react": "^0.480.0"
}
```

**Dev：**
```json
{
  "@cloudflare/vite-plugin": "^1.0.0",
  "@tailwindcss/vite": "^4.0.0",
  "@vitejs/plugin-react": "^4.4.0",
  "tailwindcss": "^4.0.0",
  "typescript": "^5.7.0",
  "drizzle-kit": "^0.30.0",
  "wrangler": "^4.0.0",
  "tw-animate-css": "^1.2.0"
}
```

**Scripts：**
```json
{
  "dev": "vite",
  "build": "vite build",
  "preview": "vite preview",
  "deploy": "wrangler deploy",
  "db:generate": "drizzle-kit generate",
  "db:migrate:local": "wrangler d1 migrations apply PROJECT_NAME-db --local",
  "db:migrate:remote": "wrangler d1 migrations apply PROJECT_NAME-db --remote"
}
```

## 工作流程

### 步驟 1：收集專案資訊

| 必填 | 選填 |
|----------|----------|
| 專案名稱（kebab-case） | Google OAuth 憑證 |
| 一句話描述 | 自訂網域 |
| Cloudflare 帳號 | 需要 R2 儲存嗎？ |
| 驗證方式：Google OAuth、email/password，或兩者都要 | 管理員 email |

### 步驟 2：初始化專案

建立專案目錄，並從零建立所有設定檔。

**`vite.config.ts`**：plugin 順序很重要，Cloudflare 一定要放第一個：

```typescript
import { defineConfig } from "vite";
import { cloudflare } from "@cloudflare/vite-plugin";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import tailwindcss from "@tailwindcss/vite";
import viteReact from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [
    cloudflare({ viteEnvironment: { name: "ssr" } }),
    tailwindcss(),
    tanstackStart(),
    viteReact(),
  ],
});
```

**`wrangler.jsonc`**：

```jsonc
{
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "PROJECT_NAME",
  "compatibility_date": "2025-04-01",
  "compatibility_flags": ["nodejs_compat"],
  "main": "@tanstack/react-start/server-entry",
  "account_id": "ACCOUNT_ID",
  "d1_databases": [
    {
      "binding": "DB",
      "database_name": "PROJECT_NAME-db",
      "database_id": "DATABASE_ID",
      "migrations_dir": "drizzle"
    }
  ]
}
```

重點：`main` 一定要是 `"@tanstack/react-start/server-entry"`（Nitro server 進入點）。用 `nodejs_compat`（不是 `node_compat`）。加上 `account_id` 可以避免互動式提問。

**`tsconfig.json`**：

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "paths": { "@/*": ["./src/*"] },
    "types": ["@cloudflare/workers-types/2023-07-01"]
  },
  "include": ["src/**/*", "vite.config.ts"]
}
```

**`.dev.vars`**：用 `openssl rand -hex 32` 產生 `BETTER_AUTH_SECRET`：

```
BETTER_AUTH_SECRET=<generated-hex-32>
BETTER_AUTH_URL=http://localhost:3000
TRUSTED_ORIGINS=http://localhost:3000
# GOOGLE_CLIENT_ID=
# GOOGLE_CLIENT_SECRET=
```

**`.gitignore`**：node_modules、.wrangler、dist、.output、.dev.vars、.vinxi、.DS_Store

接著安裝並建立 D1 資料庫：

```bash
cd PROJECT_NAME && pnpm install
npx wrangler d1 create PROJECT_NAME-db
# Copy the database_id into wrangler.jsonc d1_databases binding
```

### 步驟 3：資料庫 Schema

**`src/db/schema.ts`**：放所有資料表。better-auth 需要：`users`、`sessions`、`accounts`、`verifications`。再加上應用程式的資料表（例如 `items`）做 CRUD 示範。

D1 專屬規則：
- timestamp 用 `integer`（Unix epoch），不要用 Date 物件
- 主鍵用 `text`（nanoid/cuid2），不要用 autoincrement
- 每個查詢的 bound parameter 控制在 100 個以內（大量 insert 要分批）
- D1 的外鍵永遠是開啟的

**`src/db/index.ts`**：Drizzle client factory：

```typescript
import { drizzle } from "drizzle-orm/d1";
import { env } from "cloudflare:workers";
import * as schema from "./schema";

export function getDb() {
  return drizzle(env.DB, { schema });
}
```

**重要**：用 `import { env } from "cloudflare:workers"`，不要用 `process.env`。Drizzle client 要在每個 server function 裡面建立（每個 request 一個），不要在 module 層級建。

**`drizzle.config.ts`**：

```typescript
import { defineConfig } from "drizzle-kit";

export default defineConfig({
  schema: "./src/db/schema.ts",
  out: "./drizzle",
  dialect: "sqlite",
});
```

產生並套用初始 migration：

```bash
pnpm db:generate
pnpm db:migrate:local
```

### 步驟 4：設定驗證

**`src/lib/auth.server.ts`**：Server 端的 better-auth：

```typescript
import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { drizzle } from "drizzle-orm/d1";
import { env } from "cloudflare:workers";
import * as schema from "../db/schema";

export function getAuth() {
  const db = drizzle(env.DB, { schema });
  return betterAuth({
    database: drizzleAdapter(db, { provider: "sqlite" }),
    secret: env.BETTER_AUTH_SECRET,
    baseURL: env.BETTER_AUTH_URL,
    trustedOrigins: env.TRUSTED_ORIGINS?.split(",") ?? [],
    emailAndPassword: { enabled: true },
    socialProviders: {
      // Add Google OAuth if credentials provided
    },
  });
}
```

**重要**：`getAuth()` 必須在每個 request 內呼叫（在 handler/loader 裡面），不要在 module 層級呼叫。

**`src/lib/auth.client.ts`**：Client 端的驗證 hook：

```typescript
import { createAuthClient } from "better-auth/react";

export const { useSession, signIn, signOut, signUp } = createAuthClient();
```

**`src/routes/api/auth/$.ts`**：better-auth 的 API catch-all：

```typescript
import { createAPIFileRoute } from "@tanstack/react-start/api";
import { getAuth } from "../../../lib/auth.server";

export const APIRoute = createAPIFileRoute("/api/auth/$")({
  GET: ({ request }) => getAuth().handler(request),
  POST: ({ request }) => getAuth().handler(request),
});
```

**重要**：驗證一定要用 API route（`createAPIFileRoute`），不要用 server function（`createServerFn`）。better-auth 需要直接存取 request/response。

### 步驟 5：Server Function

**核心模式**：一定要在 handler 裡面建立 DB client：

```typescript
import { createServerFn } from "@tanstack/react-start";
import { getDb } from "../db";

export const getItems = createServerFn({ method: "GET" }).handler(async () => {
  const db = getDb();
  return db.select().from(items).all();
});
```

**用 Zod 做輸入驗證**：

```typescript
export const createItem = createServerFn({ method: "POST" })
  .inputValidator(
    z.object({
      name: z.string().min(1),
      description: z.string().optional(),
    })
  )
  .handler(async ({ data }) => {
    const db = getDb();
    const id = crypto.randomUUID();
    await db.insert(items).values({ id, ...data, createdAt: Date.now() });
    return { id };
  });
```

**受保護的 server function**：檢查驗證，沒驗證就 throw redirect：

```typescript
import { redirect } from "@tanstack/react-router";
import { getAuth } from "../lib/auth.server";

async function requireSession(request?: Request) {
  const auth = getAuth();
  const session = await auth.api.getSession({
    headers: request?.headers ?? new Headers(),
  });
  if (!session) {
    throw redirect({ to: "/login" });
  }
  return session;
}

export const getSessionFn = createServerFn({ method: "GET" }).handler(
  async ({ request }) => {
    const auth = getAuth();
    return auth.api.getSession({ headers: request.headers });
  }
);

export const getItems = createServerFn({ method: "GET" }).handler(
  async ({ request }) => {
    const session = await requireSession(request);
    const db = getDb();
    return db.select().from(items).where(eq(items.userId, session.user.id)).all();
  }
);
```

**Route loader 模式**：在 route 的 `loader` 裡用 server function：

```typescript
export const Route = createFileRoute("/_authed/items")({
  loader: () => getItems(),
  component: ItemsPage,
});

function ItemsPage() {
  const items = Route.useLoaderData();
  return <div>{items.map((item) => <div key={item.id}>{item.name}</div>)}</div>;
}
```

**驗證守衛**（`_authed.tsx`）：用 `beforeLoad`：

```typescript
export const Route = createFileRoute("/_authed")({
  beforeLoad: async () => {
    const session = await getSessionFn();
    if (!session) {
      throw redirect({ to: "/login" });
    }
    return { session };
  },
});
```

子 route 透過 `Route.useRouteContext()` 取得 session。

**Mutation + invalidation**：mutation 之後要 invalidate router，讓 loader 重新抓資料：

```typescript
function CreateItemForm() {
  const router = useRouter();
  const handleSubmit = async (data: NewItem) => {
    await createItem({ data });
    router.invalidate();
    router.navigate({ to: "/items" });
  };
  return <form onSubmit={...}>...</form>;
}
```

**型別安全**：server function 的輸入/輸出型別用 Drizzle 的 `InferSelectModel` / `InferInsertModel`。驗證失敗一律用 `throw redirect()`，不要回傳錯誤 response。

### 步驟 6：App 外殼 + 主題

**`src/routes/__root.tsx`**：完整的 HTML 文件，含 `@tanstack/react-router` 的 `<HeadContent />` + `<Scripts />`，`<html>` 上加 `suppressHydrationWarning`（SSR + 主題），inline 主題初始化 script 以避免閃爍，以及全域 CSS import。

**`src/styles/app.css`**：`@import "tailwindcss"`（v4 語法）+ 放在 `:root` 和 `.dark` 的 shadcn/ui CSS 變數。只用語意化 token。

**`src/router.tsx`**：

```typescript
import { createRouter as createTanStackRouter } from "@tanstack/react-router";
import { routeTree } from "./routeTree.gen";

export function createRouter() {
  return createTanStackRouter({ routeTree });
}

declare module "@tanstack/react-router" {
  interface Register {
    router: ReturnType<typeof createRouter>;
  }
}
```

**`src/client.tsx`** + **`src/ssr.tsx`**：標準的 TanStack Start 進入點樣板程式碼。

安裝 shadcn/ui：

```bash
pnpm dlx shadcn@latest init --defaults
pnpm dlx shadcn@latest add button card input label sidebar table dropdown-menu form separator sheet
```

**主題切換**：三種狀態（light → dark → system → light），存在 localStorage，`.dark` class 加在 `<html>` 上。系統偏好**只用 JS** 偵測，不要用 CSS `@media (prefers-color-scheme)` 查詢。

**元件**放在 `src/components/`：`app-sidebar.tsx`、`theme-toggle.tsx`、`user-nav.tsx`、`stat-card.tsx`。

### 步驟 7：CRUD Server Function

| 函式 | Method | 用途 |
|----------|--------|---------|
| `getItems` | GET | 列出目前使用者的所有 item |
| `getItem` | GET | 依 ID 取得單一 item |
| `createItem` | POST | 建立新 item |
| `updateItem` | POST | 更新既有 item |
| `deleteItem` | POST | 依 ID 刪除 item |

每個 server function：(1) 取得驗證 session，(2) 透過 `getDb()` 建立每個 request 專屬的 Drizzle client，(3) 執行 DB 操作，(4) 回傳有型別的資料。Route loader 呼叫 GET 函式。Mutation 呼叫 POST 函式，然後 `router.invalidate()`。

### 步驟 8：本機驗證

```bash
pnpm dev
```

- [ ] App 在 http://localhost:3000 載入成功
- [ ] 註冊新帳號（email/password）
- [ ] 登入和登出都正常
- [ ] 儀表板載入，統計卡片有顯示
- [ ] 建立、列出、編輯、刪除 item
- [ ] 主題切換會依序循環：light -> dark -> system
- [ ] 側邊欄在行動裝置上會收合
- [ ] Console 沒有錯誤

### 步驟 9：部署到正式環境

**部署前檢查清單**：執行 deploy 之前先確認：
- [ ] `wrangler.jsonc` 有正確的 `account_id`；`main` 是 `"@tanstack/react-start/server-entry"`；`compatibility_flags` 裡有 `nodejs_compat`
- [ ] D1 資料庫已建立，`database_id` 已填入
- [ ] `.dev.vars` 已加入 gitignore；原始碼裡沒有寫死的 secret

**設定正式環境的 secret：**

```bash
openssl rand -hex 32 | npx wrangler secret put BETTER_AUTH_SECRET
echo "https://PROJECT.SUBDOMAIN.workers.dev" | npx wrangler secret put BETTER_AUTH_URL
echo "http://localhost:3000,https://PROJECT.SUBDOMAIN.workers.dev" | npx wrangler secret put TRUSTED_ORIGINS

# Google OAuth (optional)
echo "your-client-id" | npx wrangler secret put GOOGLE_CLIENT_ID
echo "your-client-secret" | npx wrangler secret put GOOGLE_CLIENT_SECRET
```

如果用 Google OAuth，要在 Google Cloud Console 加上正式環境的 redirect URI：`https://PROJECT.SUBDOMAIN.workers.dev/api/auth/callback/google`。

**Migrate 並部署：**

```bash
pnpm db:migrate:remote
pnpm build && npx wrangler deploy
```

第一次部署之後，把 `BETTER_AUTH_URL` 更新成實際的 Worker URL，再重新部署一次。

**驗證：** app 在正式網址載入成功、驗證正常、CRUD 正常、主題有保留。

**自訂網域**（選用）：Cloudflare Dashboard → Workers → Triggers → Custom Domains。把 `BETTER_AUTH_URL` + `TRUSTED_ORIGINS` secret 和 Google OAuth redirect URI 都更新成新網域，然後重新部署。

## 常見問題

| 症狀 | 原因 | 解法 |
|---------|-------|-----|
| `env` 是 undefined | 在 module 層級存取 | 只在 request handler 裡使用 `import { env } from "cloudflare:workers"` |
| 找不到 D1 資料庫 | Binding 對不上 | 檢查 wrangler.jsonc 裡 `d1_databases` 的 binding 名稱跟程式碼一致 |
| 驗證 redirect 無限迴圈 | URL 不一致 | `BETTER_AUTH_URL` 必須跟實際網址完全一致（協定 + 網域，結尾不要有斜線） |
| 驗證無聲失敗 | 缺少 origin | 用 `TRUSTED_ORIGINS` secret 設定所有合法網址（以逗號分隔） |
| 樣式沒載入 | 缺少 plugin | 確認 vite.config.ts 裡有 `@tailwindcss/vite` plugin |
| SSR hydration 不一致 | 主題閃爍 | 在 `<html>` 元素加上 `suppressHydrationWarning` |
| 在 Cloudflare 上 build 失敗 | 設定錯誤 | 檢查 wrangler.jsonc 裡的 `nodejs_compat` flag 和 `main` 欄位 |
| Secret 沒有生效 | 沒有重新部署 | `wrangler secret put` **不會**重新部署，之後要跑 `npx wrangler deploy` |
| 驗證 endpoint 回傳 404 | Route 類型錯誤 | better-auth 要用 `createAPIFileRoute`（API route），不要用 `createServerFn` |
| "redirect_uri_mismatch" | 缺少 URI | 把正式環境網址加到 Google Cloud Console 的 OAuth redirect URI |
| 看不懂的 Vite 錯誤 | Plugin 順序 | 一定要是：`cloudflare()` -> `tailwindcss()` -> `tanstackStart()` -> `viteReact()` |
| "Table not found" 500 錯誤 | 缺少 migration | 部署之前先跑 `pnpm db:migrate:remote` |
