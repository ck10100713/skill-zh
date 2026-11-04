---
name: vite-flare-starter
description: "從 vite-flare-starter 模板建出全端 Cloudflare app 的腳手架：React 19 + Hono + D1+Drizzle + better-auth + Tailwind v4+shadcn/ui + TanStack Query + R2 + Workers AI。執行 setup.sh 來 clone、設定並部署。只要使用者想要一個功能齊全的 Cloudflare 全端 app、vite-flare-starter 腳手架，或一個驗證 + 資料庫 + Workers AI 都準備好的 React + Cloudflare app，就用這個 skill。"
compatibility: claude-code-only
---

# Vite Flare Starter

把功能齊全的 Cloudflare starter clone 下來，設定成獨立的專案。產出一個完整換上自己品牌、可以部署的全端 app。

## 技術堆疊

| 層 | 技術 | 版本 |
|-------|-----------|---------|
| 前端 | React、Vite、Tailwind CSS、shadcn/ui | 19、6.x、v4、latest |
| 後端 | Hono（跑在 Cloudflare Workers 上） | 4.x |
| 資料庫 | D1（邊緣的 SQLite）+ Drizzle ORM | 0.38+ |
| 驗證 | better-auth（Google OAuth + email/password） | latest |
| 儲存 | R2（相容 S3 的物件儲存） | — |
| AI | Workers AI binding | — |
| 資料抓取 | TanStack Query | v5 |

### Cloudflare Binding

| Binding | 類型 | 用途 |
|---------|------|---------|
| `DB` | D1 Database | 主要的應用程式資料庫 |
| `AVATARS` | R2 Bucket | 使用者頭像儲存 |
| `FILES` | R2 Bucket | 一般檔案上傳 |
| `AI` | Workers AI | AI 模型推論 |

### 專案結構

```
src/
├── client/                 # React frontend
│   ├── components/         # UI components
│   ├── hooks/              # Custom hooks + TanStack Query
│   ├── pages/              # Route pages
│   ├── lib/                # Utilities (auth client, etc.)
│   └── main.tsx            # App entry point
├── server/                 # Hono backend
│   ├── index.ts            # Worker entry point
│   ├── routes/             # API routes
│   ├── middleware/          # Auth, CORS, etc.
│   └── db/                 # Drizzle schema + queries
└── shared/                 # Shared types between client/server
```

### 重要指令

| 指令 | 用途 |
|---------|---------|
| `pnpm dev` | 啟動本機開發 server |
| `pnpm build` | 正式環境 build |
| `pnpm deploy` | 部署到 Cloudflare |
| `pnpm db:migrate:local` | 在本機套用 migration |
| `pnpm db:migrate:remote` | 把 migration 套用到正式環境 |
| `pnpm db:generate` | 依 schema 的變更產生 migration |

## 工作流程

### 步驟 1：收集專案資訊

詢問：

| 必填 | 選填 |
|----------|----------|
| 專案名稱（kebab-case） | 管理員 email |
| 描述（一句話） | Google OAuth 憑證 |
| Cloudflare 帳號 | 自訂網域 |

### 步驟 2：Clone 並設定

#### 2a. Clone 並清理

```bash
git clone https://github.com/jezweb/vite-flare-starter.git PROJECT_DIR --depth 1
cd PROJECT_DIR
rm -rf .git
git init
```

#### 2b. 要尋找取代的目標

把這些位置的 `vite-flare-starter` 換成專案名稱：

| 檔案 | 目標 | 取代成 |
|------|--------|-------------|
| `wrangler.jsonc` | `"vite-flare-starter"`（worker 名稱） | `"PROJECT_NAME"` |
| `wrangler.jsonc` | `vite-flare-starter-db` | `PROJECT_NAME-db` |
| `wrangler.jsonc` | `vite-flare-starter-avatars` | `PROJECT_NAME-avatars` |
| `wrangler.jsonc` | `vite-flare-starter-files` | `PROJECT_NAME-files` |
| `package.json` | `"name": "vite-flare-starter"` | `"name": "PROJECT_NAME"` |
| `package.json` | `vite-flare-starter-db` | `PROJECT_NAME-db` |
| `index.html` | `<title>` 的內容 | App 顯示名稱（Title Case） |

同樣在 `wrangler.jsonc` 裡：
- **移除**寫死的 `account_id` 那一行（讓 wrangler 提示或改用環境變數）
- **把** `database_id` 的值**換成** `REPLACE_WITH_YOUR_DATABASE_ID`

把 `package.json` 的 version 重設成 `"0.1.0"`。

取代時用 Edit 工具（比 sed 更好，可避免 macOS/GNU 的差異）。

#### 2c. 產生驗證用的 secret

```bash
BETTER_AUTH_SECRET=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
```

#### 2d. 建立 .dev.vars

轉換 kebab-case 的專案名稱：`my-cool-app` 變成顯示名稱 `My Cool App`、ID `my_cool_app`。

```
# Local Development Environment Variables
# DO NOT COMMIT THIS FILE TO GIT

# Authentication (better-auth)
BETTER_AUTH_SECRET=<generated>
BETTER_AUTH_URL=http://localhost:5173

# Google OAuth (optional)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Email Auth Control (disabled by default)
# ENABLE_EMAIL_LOGIN=true
# ENABLE_EMAIL_SIGNUP=true

# Application Configuration
APP_NAME=<Display Name>
VITE_APP_NAME=<Display Name>
VITE_APP_ID=<app_id>
VITE_TOKEN_PREFIX=<app_id>_
VITE_GITHUB_URL=
VITE_FOOTER_TEXT=

NODE_ENV=development
```

#### 2e. 建立 Cloudflare 資源（選用）

```bash
npx wrangler d1 create PROJECT_NAME-db
# Extract database_id from output, update wrangler.jsonc

npx wrangler r2 bucket create PROJECT_NAME-avatars
npx wrangler r2 bucket create PROJECT_NAME-files
```

#### 2f. 安裝並 migrate

```bash
pnpm install
pnpm run db:migrate:local
```

#### 2g. 初始 commit

```bash
git add -A
git commit -m "Initial commit from vite-flare-starter"
```

### 步驟 3：手動設定

1. **Google OAuth**（如果要用）：到 Google Cloud Console 建立 OAuth 2.0 Client ID，加入 redirect URI `http://localhost:5173/api/auth/callback/google`，把 Client ID 和 Secret 複製到 `.dev.vars`
2. **Favicon**：替換 `public/favicon.svg`
3. **CLAUDE.md**：更新專案描述，移除對 vite-flare-starter 的參照
4. **index.html**：更新 `<title>` 和 meta description

### 步驟 4：本機驗證

```bash
pnpm dev
```

檢查：http://localhost:5173 能載入、顯示的是**你的** app 名稱、註冊/登入能運作（如果有設定 OAuth）。

### 步驟 5：部署到正式環境

```bash
# Set production secrets
openssl rand -base64 32 | npx wrangler secret put BETTER_AUTH_SECRET
echo "https://PROJECT_NAME.SUBDOMAIN.workers.dev" | npx wrangler secret put BETTER_AUTH_URL
echo "http://localhost:5173,https://PROJECT_NAME.SUBDOMAIN.workers.dev" | npx wrangler secret put TRUSTED_ORIGINS

# If using Google OAuth
echo "your-client-id" | npx wrangler secret put GOOGLE_CLIENT_ID
echo "your-client-secret" | npx wrangler secret put GOOGLE_CLIENT_SECRET

# Migrate remote database
pnpm run db:migrate:remote

# Build and deploy
pnpm run build && pnpm run deploy
```

**重要**：第一次部署之後，把 BETTER_AUTH_URL 更新成你實際的 Worker URL。把正式環境的網址加到 Google OAuth 的 redirect URI。

## 安全指紋

把這些全部改掉，讓攻擊者無法辨識你的網站用的是這個 starter：

| 位置 | 預設值 | 怎麼改 |
|----------|---------------|---------------|
| 頁面標題 | "Vite Flare Starter" | `index.html` |
| UI 裡的 app 名稱 | "Vite Flare Starter" | `VITE_APP_NAME` 環境變數 |
| localStorage key | `vite-flare-starter-theme` | `VITE_APP_ID` 環境變數 |
| API token | `vfs_` 前綴 | `VITE_TOKEN_PREFIX` 環境變數 |
| GitHub 連結 | starter repo | `VITE_GITHUB_URL`（設成空的就會隱藏） |
| Worker 名稱 | `vite-flare-starter` | `wrangler.jsonc` |
| 資料庫名稱 | `vite-flare-starter-db` | `wrangler.jsonc` |
| R2 bucket | `vite-flare-starter-*` | `wrangler.jsonc` |

## 環境變數

### 品牌（VITE_ 前綴 = 前端可用）

| 變數 | 用途 | 範例 |
|----------|---------|---------|
| `VITE_APP_NAME` | UI 裡的顯示名稱 | "My Cool App" |
| `VITE_APP_ID` | localStorage 前綴、Sentry | "mycoolapp" |
| `VITE_TOKEN_PREFIX` | API token 前綴 | "mca_" |
| `VITE_GITHUB_URL` | GitHub 連結（空的 = 隱藏） | "" |
| `VITE_FOOTER_TEXT` | 頁尾版權文字 | "2026 My Company" |
| `APP_NAME` | Server 端的 app 名稱 | "My Cool App" |

### 驗證

| 變數 | 用途 | 備註 |
|----------|---------|-------|
| `BETTER_AUTH_SECRET` | Session 加密 | `openssl rand -hex 32` |
| `BETTER_AUTH_URL` | 驗證的 base URL | 必須跟實際網址完全一致 |
| `TRUSTED_ORIGINS` | 允許的 origin | 以逗號分隔，包含 localhost + 正式環境 |
| `GOOGLE_CLIENT_ID` | Google OAuth | 從 Google Cloud Console 取得 |
| `GOOGLE_CLIENT_SECRET` | Google OAuth | 從 Google Cloud Console 取得 |
| `ENABLE_EMAIL_LOGIN` | 啟用 email/password | "true" 才會啟用 |
| `ENABLE_EMAIL_SIGNUP` | 啟用 email 註冊 | 需要 ENABLE_EMAIL_LOGIN |

### Email（選用）

| 變數 | 用途 | 備註 |
|----------|---------|-------|
| `EMAIL_FROM` | 寄件人地址 | 用於驗證/密碼重設 |
| `EMAIL_API_KEY` | Email 服務的 API key | 建議用 Resend |

## 常見客製化

### 新增資料表
1. 在 `src/server/db/schema.ts` 加上 schema
2. 產生 migration：`pnpm db:generate`
3. 在本機套用：`pnpm db:migrate:local`
4. 套用到正式環境：`pnpm db:migrate:remote`

### 新增 API Route
1. 在 `src/server/routes/` 建立 route 檔案
2. 在 `src/server/index.ts` 註冊
3. 在 `src/client/hooks/` 加上 TanStack Query hook

### 更換驗證提供者
編輯 `src/server/auth.ts`：把 provider 加到 `socialProviders`，把憑證加到 `.dev.vars` 和正式環境的 secret，並更新前端的登入按鈕。

### Feature Flag
透過環境變數控制功能：`VITE_FEATURE_STYLE_GUIDE=true`、`VITE_FEATURE_COMPONENTS=true`。自己的 flag 加在 `src/client/lib/features.ts`。

## 疑難排解

| 症狀 | 原因 | 解法 |
|---------|-------|-----|
| 驗證後無聲地導回首頁 | 缺少 TRUSTED_ORIGINS | 把所有合法的網址設進 TRUSTED_ORIGINS |
| 部署時出現 "Not authorized" | account_id 錯誤 | 從 wrangler.jsonc 移除 account_id，或設成你自己的 |
| 資料庫 500 錯誤 | 缺少 migration | 執行 `pnpm db:migrate:local` 和 `pnpm db:migrate:remote` |
| localStorage 顯示 "vite-flare-starter" | 缺少 VITE_APP_ID | 在 .dev.vars 設定 `VITE_APP_ID=yourapp` |
| 只有正式環境驗證失敗 | BETTER_AUTH_URL 不一致 | 必須跟實際的 Worker URL 完全一致（https，結尾不要有斜線） |
| Google 登入時出現 "redirect_uri_mismatch" | 缺少 OAuth redirect URI | 把正式環境網址加到 Google Cloud Console 的 OAuth redirect URI |
| 改了 secret 卻沒有效果 | 沒有重新部署 | `wrangler secret put` **不會**重新部署。之後要執行 `pnpm deploy` |

## 正式環境部署檢查清單

- [ ] 已設定 `BETTER_AUTH_SECRET`（要跟開發環境不同！）
- [ ] `BETTER_AUTH_URL` 與實際的 Worker URL 一致
- [ ] `TRUSTED_ORIGINS` 包含所有合法的網址
- [ ] Google OAuth 的 redirect URI 包含正式環境網址
- [ ] 遠端資料庫已 migrate（`pnpm db:migrate:remote`）
- [ ] 設定檔裡沒有任何 `vite-flare-starter` 的參照
- [ ] Favicon 已替換
- [ ] CLAUDE.md 已更新
- [ ] `.dev.vars` 沒有被 commit（檢查 `.gitignore`）
