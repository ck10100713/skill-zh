---
name: project-docs
description: "從 codebase 分析產生專案文件：ARCHITECTURE.md、API_ENDPOINTS.md、DATABASE_SCHEMA.md。讀原始碼、schema 檔、route 和設定，產出準確、有結構的文件。用於專案剛開始、新貢獻者 onboarding，或文件缺漏、過時的時候。觸發詞：'generate docs'、'document architecture'、'create api docs'、'document schema'、'project documentation'、'write architecture doc'。"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
compatibility: claude-code-only
---

# 專案文件產生器

分析 codebase 來產生結構化的專案文件。產出的文件反映的是**實際的程式碼**，不是理想中的架構。

## 什麼時候用

- 新專案需要最初的文件
- 文件缺漏或過時
- 帶人熟悉 codebase
- 重構之後的文件更新

## 工作流程

### 1. 偵測專案類型

掃描專案根目錄，判斷這是哪種專案：

| 指標 | 專案類型 |
|-----------|-------------|
| `wrangler.jsonc` / `wrangler.toml` | Cloudflare Worker |
| `vite.config.ts` + `src/App.tsx` | React SPA |
| `astro.config.mjs` | Astro 網站 |
| `next.config.js` | Next.js app |
| `package.json` 含 `hono` | Hono API |
| `src/index.ts` 含 `Hono` | API server |
| `drizzle.config.ts` | 有資料庫層 |
| `schema.ts` 或 `schema/` | 有資料庫 schema |
| `pyproject.toml` / `setup.py` | Python 專案 |
| `Cargo.toml` | Rust 專案 |

### 2. 問要產生什麼

```
Which docs should I generate?
1. ARCHITECTURE.md — system overview, stack, directory structure, key flows
2. API_ENDPOINTS.md — routes, methods, params, response shapes, auth
3. DATABASE_SCHEMA.md — tables, relationships, migrations, indexes
4. All of the above
```

只提供符合專案的文件。靜態網站不要提供 API_ENDPOINTS.md。沒有資料庫就不要提供 DATABASE_SCHEMA.md。

### 3. 掃描 Codebase

對每份要產生的文件，讀相關的原始檔：

**ARCHITECTURE.md**：掃描：
- `package.json` / `pyproject.toml`（技術堆疊、相依套件）
- 進入點（`src/index.ts`、`src/main.tsx`、`src/App.tsx`）
- 設定檔（`wrangler.jsonc`、`vite.config.ts`、`tsconfig.json`）
- 目錄結構（前 2 層）
- 關鍵模組及它們的 export

**API_ENDPOINTS.md**：掃描：
- Route 檔案（`src/routes/`、`src/api/`，或寫在 index 裡）
- Middleware 檔案（auth、CORS、logging）
- Request/response 型別或 Zod schema
- 錯誤處理模式

**DATABASE_SCHEMA.md**：掃描：
- Drizzle schema 檔案（`src/db/schema.ts`、`src/schema/`）
- Migration 檔案（`drizzle/`、`migrations/`）
- 有的話，原始 SQL 檔案
- 有的話，種子檔案

### 4. 產生文件

把每份文件寫到 `docs/`（目錄不存在就建立）。如果專案在那裡已經有文件，就提議更新，不要直接覆寫。

對於沒有 `docs/` 目錄的小專案，改寫到專案根目錄。

## 文件範本

### ARCHITECTURE.md

```markdown
# Architecture

## Overview
[One paragraph: what this project does and how it's structured]

## Stack
| Layer | Technology | Version |
|-------|-----------|---------|
| Runtime | [e.g. Cloudflare Workers] | — |
| Framework | [e.g. Hono] | [version] |
| Database | [e.g. D1 (SQLite)] | — |
| ORM | [e.g. Drizzle] | [version] |
| Frontend | [e.g. React 19] | [version] |
| Styling | [e.g. Tailwind v4] | [version] |

## Directory Structure
[Annotated tree — top 2 levels with purpose comments]

## Key Flows
### [Flow 1: e.g. "User Authentication"]
[Step-by-step: request → middleware → handler → database → response]

### [Flow 2: e.g. "Data Processing Pipeline"]
[Step-by-step through the system]

## Configuration
[Key config files and what they control]

## Deployment
[How to deploy, environment variables needed, build commands]
```

### API_ENDPOINTS.md

```markdown
# API Endpoints

## Base URL
[e.g. `https://api.example.com` or relative `/api`]

## Authentication
[Method: Bearer token, session cookie, API key, none]
[Where tokens come from, how to obtain]

## Endpoints

### [Group: e.g. Users]

#### `GET /api/users`
- **Auth**: Required
- **Params**: `?page=1&limit=20`
- **Response**: `{ users: User[], total: number }`

#### `POST /api/users`
- **Auth**: Required (admin)
- **Body**: `{ name: string, email: string }`
- **Response**: `{ user: User }` (201)
- **Errors**: 400 (validation), 409 (duplicate email)

[Repeat for each endpoint]

## Error Format
[Standard error response shape]

## Rate Limits
[If applicable]
```

### DATABASE_SCHEMA.md

```markdown
# Database Schema

## Engine
[e.g. Cloudflare D1 (SQLite), PostgreSQL, MySQL]

## Tables

### `users`
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT | PK | UUID |
| email | TEXT | UNIQUE, NOT NULL | User email |
| name | TEXT | NOT NULL | Display name |
| created_at | TEXT | NOT NULL, DEFAULT now | ISO timestamp |

### `posts`
[Same format]

## Relationships
[Foreign keys, join patterns, cascading rules]

## Indexes
[Non-primary indexes and why they exist]

## Migrations
- Generate: `npx drizzle-kit generate`
- Apply local: `npx wrangler d1 migrations apply DB --local`
- Apply remote: `npx wrangler d1 migrations apply DB --remote`

## Seed Data
[Reference to seed script if one exists]
```

## 品質規則

1. **記錄現有的，不是計畫中的**：讀實際的程式碼，不要編造 endpoint 或資料表
2. **包含版本**：從 package.json/lock 檔擷取，不要憑記憶
3. **顯示真實的 response 形狀**：從程式碼裡的 TypeScript 型別或 Zod schema 複製
4. **保持好掃讀**：表格優於段落，程式碼區塊優於散文
5. **不要重複 CLAUDE.md**：如果架構資訊已經在 CLAUDE.md 裡，要嘛搬到 ARCHITECTURE.md，要嘛引用它
6. **標出缺口**：如果發現沒有文件的 route，或用途不明的資料表，用 `<!-- TODO: document purpose -->` 標註

## 更新既有文件

如果文件已經存在：
1. 讀既有的文件
2. 對照目前的 codebase 找差異
3. 向使用者展示有什麼變動（新 endpoint、移除的資料表、更新的技術堆疊）
4. 套用更新，同時保留任何手寫的註記或章節

絕對不要默默覆寫使用者加在文件裡的自訂內容。
