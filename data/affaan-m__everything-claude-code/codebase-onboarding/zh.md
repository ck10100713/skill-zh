---
name: codebase-onboarding
description: 分析不熟悉的 codebase，產出結構化的上手指南，包含架構地圖、關鍵進入點、慣例，以及一份起手的 CLAUDE.md。適用於加入新專案，或第一次在某個 repo 裡設定 Claude Code。
metadata:
  origin: ECC
---

# Codebase Onboarding

有系統地分析不熟悉的 codebase，產出結構化的上手指南。設計給加入新專案的開發者，或是第一次在既有 repo 裡設定 Claude Code 的人。

## When to Use

- 第一次用 Claude Code 開啟某個專案
- 加入新團隊或新的 repository
- 使用者問「help me understand this codebase」
- 使用者要求為專案產生 CLAUDE.md
- 使用者說「onboard me」或「walk me through this repo」

## How It Works

### Phase 1: Reconnaissance

不用讀完每個檔案，先蒐集這個專案的原始訊號。平行執行下面這些檢查：

```
1. Package manifest detection
   → package.json, go.mod, Cargo.toml, pyproject.toml, pom.xml, build.gradle,
     Gemfile, composer.json, mix.exs, pubspec.yaml

2. Framework fingerprinting
   → next.config.*, nuxt.config.*, angular.json, vite.config.*,
     django settings, flask app factory, fastapi main, rails config

3. Entry point identification
   → main.*, index.*, app.*, server.*, cmd/, src/main/

4. Directory structure snapshot
   → Top 2 levels of the directory tree, ignoring node_modules, vendor,
     .git, dist, build, __pycache__, .next

5. Config and tooling detection
   → .eslintrc*, .prettierrc*, tsconfig.json, Makefile, Dockerfile,
     docker-compose*, .github/workflows/, .env.example, CI configs

6. Test structure detection
   → tests/, test/, __tests__/, *_test.go, *.spec.ts, *.test.js,
     pytest.ini, jest.config.*, vitest.config.*
```

### Phase 2: Architecture Mapping

從偵察得到的資料，找出：

**Tech Stack**
- 程式語言和版本限制
- Framework 和主要的函式庫
- 資料庫和 ORM
- 建置工具和 bundler
- CI/CD 平台

**Architecture Pattern**
- Monolith、monorepo、microservices 或 serverless
- 前後端分離或 full-stack
- API 風格：REST、GraphQL、gRPC、tRPC

**Key Directories**
把最上層的目錄對應到它們的用途：

<!-- 這是 React 專案的範例，請換成偵測到的目錄 -->
```
src/components/  → React UI components
src/api/         → API route handlers
src/lib/         → Shared utilities
src/db/          → Database models and migrations
tests/           → Test suites
scripts/         → Build and deployment scripts
```

**Data Flow**
追蹤一個請求從進入到回應：
- 請求從哪裡進來？（router、handler、controller）
- 怎麼驗證？（middleware、schema、guard）
- 商業邏輯在哪裡？（service、model、use case）
- 怎麼連到資料庫？（ORM、raw query、repository）

### Phase 3: Convention Detection

找出 codebase 已經遵循的模式：

**Naming Conventions**
- 檔案命名：kebab-case、camelCase、PascalCase、snake_case
- 元件/類別的命名模式
- 測試檔案的命名：`*.test.ts`、`*.spec.ts`、`*_test.go`

**Code Patterns**
- 錯誤處理風格：try/catch、Result 型別、錯誤碼
- 依賴注入或直接 import
- 狀態管理的做法
- 非同步模式：callback、promise、async/await、channel

**Git Conventions**
- 從最近的 branch 看 branch 命名
- 從最近的 commit 看 commit 訊息風格
- PR 工作流程（squash、merge、rebase）
- 如果 repo 還沒有 commit，或只有淺層歷史（例如 `git clone --depth 1`），就跳過這一節，並註明「Git history unavailable or too shallow to detect conventions」

### Phase 4: Generate Onboarding Artifacts

產出兩份東西：

#### Output 1: Onboarding Guide

```markdown
# Onboarding Guide: [Project Name]

## Overview
[2-3 sentences: what this project does and who it serves]

## Tech Stack
<!-- Example for a Next.js project — replace with detected stack -->
| Layer | Technology | Version |
|-------|-----------|---------|
| Language | TypeScript | 5.x |
| Framework | Next.js | 14.x |
| Database | PostgreSQL | 16 |
| ORM | Prisma | 5.x |
| Testing | Jest + Playwright | - |

## Architecture
[Diagram or description of how components connect]

## Key Entry Points
<!-- Example for a Next.js project — replace with detected paths -->
- **API routes**: `src/app/api/` — Next.js route handlers
- **UI pages**: `src/app/(dashboard)/` — authenticated pages
- **Database**: `prisma/schema.prisma` — data model source of truth
- **Config**: `next.config.ts` — build and runtime config

## Directory Map
[Top-level directory → purpose mapping]

## Request Lifecycle
[Trace one API request from entry to response]

## Conventions
- [File naming pattern]
- [Error handling approach]
- [Testing patterns]
- [Git workflow]

## Common Tasks
<!-- Example for a Node.js project — replace with detected commands -->
- **Run dev server**: `npm run dev`
- **Run tests**: `npm test`
- **Run linter**: `npm run lint`
- **Database migrations**: `npx prisma migrate dev`
- **Build for production**: `npm run build`

## Where to Look
<!-- Example for a Next.js project — replace with detected paths -->
| I want to... | Look at... |
|--------------|-----------|
| Add an API endpoint | `src/app/api/` |
| Add a UI page | `src/app/(dashboard)/` |
| Add a database table | `prisma/schema.prisma` |
| Add a test | `tests/` matching the source path |
| Change build config | `next.config.ts` |
```

#### Output 2: Starter CLAUDE.md

根據偵測到的慣例，產生或更新專案專屬的 CLAUDE.md。如果 `CLAUDE.md` 已經存在，先讀它再加強，保留既有的專案專屬指示，並清楚標出新增或更動了什麼。

```markdown
# Project Instructions

## Tech Stack
[Detected stack summary]

## Code Style
- [Detected naming conventions]
- [Detected patterns to follow]

## Testing
- Run tests: `[detected test command]`
- Test pattern: [detected test file convention]
- Coverage: [if configured, the coverage command]

## Build & Run
- Dev: `[detected dev command]`
- Build: `[detected build command]`
- Lint: `[detected lint command]`

## Project Structure
[Key directory → purpose map]

## Conventions
- [Commit style if detectable]
- [PR workflow if detectable]
- [Error handling patterns]
```

## Best Practices

1. **不要全部都讀**：偵察應該用 Glob 和 Grep，不要對每個檔案都用 Read。只有訊號不明確時，才選擇性地讀。
2. **要驗證，不要猜**：如果從設定檔偵測到某個 framework，但實際程式碼用的是別的東西，以程式碼為準。
3. **尊重既有的 CLAUDE.md**：如果已經有一份，就加強它，不要取代它。標出哪些是新的、哪些是原本就有的。
4. **保持精簡**：上手指南應該 2 分鐘內就能掃完。細節屬於程式碼，不屬於指南。
5. **標出未知的部分**：如果某個慣例無法有把握地偵測出來，就直說，不要猜。「Could not determine test runner」比給錯誤的答案好。

## Anti-Patterns to Avoid

- 產生超過 100 行的 CLAUDE.md，要保持聚焦
- 列出每一個依賴，只強調那些會左右你怎麼寫程式的
- 描述顯而易見的目錄名稱，`src/` 不需要解釋
- 照抄 README，上手指南要補上 README 缺少的結構性洞見

## Examples

### Example 1: First time in a new repo
**User**: "Onboard me to this codebase"
**Action**: 執行完整的 4 個階段流程 → 產出 Onboarding Guide + Starter CLAUDE.md
**Output**: Onboarding Guide 直接印在對話裡，再加上寫到專案根目錄的 `CLAUDE.md`

### Example 2: Generate CLAUDE.md for existing project
**User**: "Generate a CLAUDE.md for this project"
**Action**: 執行 Phase 1-3，跳過 Onboarding Guide，只產出 CLAUDE.md
**Output**: 含有偵測到的慣例、專案專屬的 `CLAUDE.md`

### Example 3: Enhance existing CLAUDE.md
**User**: "Update the CLAUDE.md with current project conventions"
**Action**: 讀取現有的 CLAUDE.md，執行 Phase 1-3，合併新的發現
**Output**: 更新後的 `CLAUDE.md`，新增的部分有清楚標記
