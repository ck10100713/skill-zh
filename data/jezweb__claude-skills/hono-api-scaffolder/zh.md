---
name: hono-api-scaffolder
description: "為 Cloudflare Workers 建立 Hono API route 骨架。產出 route 檔案、middleware、有型別的 bindings、Zod 驗證、錯誤處理，以及 API_ENDPOINTS.md 文件。在專案已用 cloudflare-worker-builder 或 vite-flare-starter 建好之後，需要新增 API route、建立 endpoint 或產生 API 文件時使用。"
compatibility: claude-code-only
---

# Hono API Scaffolder

為既有的 Cloudflare Workers 專案加上結構化的 API route。這個 skill 是在專案外殼已經存在之後才跑的（透過 cloudflare-worker-builder 或 vite-flare-starter 建立），負責產出 route 檔案、middleware 和 endpoint 文件。

## 工作流程

### 步驟 1：蒐集 Endpoint

判斷 API 需要什麼。可以問使用者，也可以從專案描述推斷。依資源分組 endpoint：

```
Users:    GET /api/users, GET /api/users/:id, POST /api/users, PUT /api/users/:id, DELETE /api/users/:id
Posts:    GET /api/posts, GET /api/posts/:id, POST /api/posts, PUT /api/posts/:id
Auth:     POST /api/auth/login, POST /api/auth/logout, GET /api/auth/me
```

### 步驟 2：建立 Route 檔案

每個資源群組一個檔案。使用 [assets/route-template.ts](assets/route-template.ts) 的範本：

```typescript
// src/routes/users.ts
import { Hono } from 'hono'
import { zValidator } from '@hono/zod-validator'
import { z } from 'zod'
import type { Env } from '../types'

const app = new Hono<{ Bindings: Env }>()

// GET /api/users
app.get('/', async (c) => {
  const db = c.env.DB
  const { results } = await db.prepare('SELECT * FROM users').all()
  return c.json({ users: results })
})

// GET /api/users/:id
app.get('/:id', async (c) => {
  const id = c.req.param('id')
  const user = await db.prepare('SELECT * FROM users WHERE id = ?').bind(id).first()
  if (!user) return c.json({ error: 'Not found' }, 404)
  return c.json({ user })
})

// POST /api/users
const createUserSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
})

app.post('/', zValidator('json', createUserSchema), async (c) => {
  const body = c.req.valid('json')
  // ... insert logic
  return c.json({ user }, 201)
})

export default app
```

### 步驟 3：加上 Middleware

依專案需求，從 [assets/middleware-template.ts](assets/middleware-template.ts) 加入：

**Auth middleware**：保護需要認證的 route：
```typescript
import { createMiddleware } from 'hono/factory'
import type { Env } from '../types'

export const requireAuth = createMiddleware<{ Bindings: Env }>(async (c, next) => {
  const token = c.req.header('Authorization')?.replace('Bearer ', '')
  if (!token) return c.json({ error: 'Unauthorized' }, 401)
  // Validate token...
  await next()
})
```

**CORS**：用 Hono 內建的：
```typescript
import { cors } from 'hono/cors'
app.use('/api/*', cors({ origin: ['https://example.com'] }))
```

### 步驟 4：串接 Route

在主進入點掛載所有 route 群組：

```typescript
// src/index.ts
import { Hono } from 'hono'
import type { Env } from './types'
import users from './routes/users'
import posts from './routes/posts'
import auth from './routes/auth'
import { errorHandler } from './middleware/error-handler'

const app = new Hono<{ Bindings: Env }>()

// Global error handler
app.onError(errorHandler)

// Mount routes
app.route('/api/users', users)
app.route('/api/posts', posts)
app.route('/api/auth', auth)

// Health check
app.get('/api/health', (c) => c.json({ status: 'ok' }))

export default app
```

### 步驟 5：建立型別

```typescript
// src/types.ts
export interface Env {
  DB: D1Database
  KV: KVNamespace      // if needed
  R2: R2Bucket         // if needed
  API_SECRET: string   // secrets
}
```

### 步驟 6：產生 API_ENDPOINTS.md

把所有 endpoint 寫成文件。格式見 [references/endpoint-docs-template.md](references/endpoint-docs-template.md)：

```markdown
## POST /api/users
Create a new user.
- **Auth**: Required (Bearer token)
- **Body**: `{ name: string, email: string }`
- **Response 201**: `{ user: User }`
- **Response 400**: `{ error: string, details: ZodError }`
```

## 關鍵模式

### Zod 驗證

request body 一律用 `@hono/zod-validator` 驗證：

```typescript
import { zValidator } from '@hono/zod-validator'
app.post('/', zValidator('json', schema), async (c) => {
  const body = c.req.valid('json')  // fully typed
})
```

安裝：`pnpm add @hono/zod-validator zod`

### 錯誤處理

使用 [assets/error-handler.ts](assets/error-handler.ts) 的標準錯誤處理器：

```typescript
export const errorHandler = (err: Error, c: Context) => {
  console.error(err)
  return c.json({ error: err.message }, 500)
}
```

**API route 一定要回 JSON 錯誤，不能回 redirect。** `fetch()` 會默默跟著 redirect 走，結果 client 就會拿 HTML 去當 JSON 解析。

### RPC 型別安全

要讓 Worker 和 client 之間做到端到端的型別安全：

```typescript
// Worker: export the app type
export type AppType = typeof app

// Client: use hc (Hono Client)
import { hc } from 'hono/client'
import type { AppType } from '../worker/src/index'

const client = hc<AppType>('https://api.example.com')
const res = await client.api.users.$get()  // fully typed
```

### Route 群組 vs 單一檔案

| 專案規模 | 結構 |
|-------------|-----------|
| < 10 個 endpoint | 單一 `index.ts` 放所有 route |
| 10-30 個 endpoint | 每個資源一個 route 檔（`routes/users.ts`） |
| 30 個以上 endpoint | Route 檔 + 共用 middleware + 有型別的 context |

## 參考檔案

| 什麼時候 | 讀什麼 |
|------|------|
| Hono 模式、middleware、RPC | [references/hono-patterns.md](references/hono-patterns.md) |
| API_ENDPOINTS.md 格式 | [references/endpoint-docs-template.md](references/endpoint-docs-template.md) |

## 資產

| 檔案 | 用途 |
|------|---------|
| [assets/route-template.ts](assets/route-template.ts) | 含 CRUD + Zod 的 route 起手檔 |
| [assets/middleware-template.ts](assets/middleware-template.ts) | Auth middleware 範本 |
| [assets/error-handler.ts](assets/error-handler.ts) | 標準 JSON 錯誤處理器 |
