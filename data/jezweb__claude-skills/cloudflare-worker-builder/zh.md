---
name: cloudflare-worker-builder
description: "用 Hono 路由、Vite plugin 和 Static Assets 建立並部署 Cloudflare Workers。描述專案、建立骨架、設定 binding、部署。只要使用者想建立 Worker 專案、在 Cloudflare 上設定 Hono、設定 D1 / R2 / KV / Queues binding，或排查 Worker export 語法、API 路由衝突、HMR 問題或部署失敗，就使用。"
compatibility: claude-code-only
---

# Cloudflare Worker Builder

從一段簡短的描述建立一個能運作的 Cloudflare Worker 專案。產出可部署的專案，包含 Hono 路由、Vite dev server 和 Static Assets。

## 工作流程

### Step 1：了解專案

詢問專案的內容，選出合適的 binding 和結構：

- 這個 app 做什麼？（只有 API、SPA + API、landing page）
- 要什麼資料儲存？（D1 資料庫、R2 檔案、KV cache、不需要）
- 需要驗證嗎？（Clerk、better-auth、不需要）
- 用自訂網域還是 workers.dev 子網域？

像「有資料庫的待辦事項 app」這樣簡短的描述就足以開始。

### Step 2：建立專案骨架

```bash
npm create cloudflare@latest my-worker -- --type hello-world --ts --git --deploy false --framework none
cd my-worker
npm install hono
npm install -D @cloudflare/vite-plugin vite
```

從這個 skill 的 `assets/` 目錄複製並客製化這些資源檔：
- `wrangler.jsonc`：Worker 設定
- `vite.config.ts`：Vite + Cloudflare plugin
- `src/index.ts`：帶 Static Assets fallback 的 Hono app
- `package.json`：scripts 和相依套件
- `tsconfig.json`：TypeScript 設定
- `public/index.html`：SPA 進入點

### Step 3：設定 Binding

依專案需求把 binding 加到 `wrangler.jsonc`。Wrangler 4.45+ 會在第一次部署時自動建立資源，所以一定要明確指定名稱：

```jsonc
{
  "name": "my-worker",
  "main": "src/index.ts",
  "compatibility_date": "2025-11-11",
  "assets": {
    "directory": "./public/",
    "binding": "ASSETS",
    "not_found_handling": "single-page-application",
    "run_worker_first": ["/api/*"]
  },
  // Add as needed:
  "d1_databases": [{ "binding": "DB", "database_name": "my-app-db" }],
  "r2_buckets": [{ "binding": "STORAGE", "bucket_name": "my-app-files" }],
  "kv_namespaces": [{ "binding": "CACHE", "title": "my-app-cache" }]
}
```

### Step 4：部署

```bash
npm run dev           # Local dev at http://localhost:8787
wrangler deploy       # Production deploy
```

---

## 關鍵寫法

### Export 語法

```typescript
// CORRECT — use this pattern
export default app

// WRONG — causes "Cannot read properties of undefined"
export default { fetch: app.fetch }
```

來源：[honojs/hono #3955](https://github.com/honojs/hono/issues/3955)

### Static Assets + API 路由

沒有 `run_worker_first` 的話，SPA fallback 會攔截 API 路由，回傳 `index.html` 而不是 JSON：

```jsonc
"assets": {
  "not_found_handling": "single-page-application",
  "run_worker_first": ["/api/*"]  // CRITICAL
}
```

來源：[workers-sdk #8879](https://github.com/cloudflare/workers-sdk/issues/8879)

### Vite 設定

```typescript
import { defineConfig } from 'vite'
import { cloudflare } from '@cloudflare/vite-plugin'

export default defineConfig({ plugins: [cloudflare()] })
```

一定要在 wrangler.jsonc 設定 `main` 欄位，Vite plugin 需要它。

### Scheduled/Cron Handler

加上 cron trigger 時，改成明確的 export：

```typescript
export default {
  fetch: app.fetch,
  scheduled: async (event, env, ctx) => { /* ... */ }
}
```

---

## 參考檔案

要詳細的疑難排解就讀這些：

- `references/common-issues.md`：10 個有記載的問題，附來源和解法
- `references/architecture.md`：路由優先順序、快取、Workers RPC
- `references/deployment.md`：CI/CD、自動建立資源、漸進式 rollout
