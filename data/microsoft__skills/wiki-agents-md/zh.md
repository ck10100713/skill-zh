---
name: wiki-agents-md
description: 為 repository 的資料夾產生 AGENTS.md 檔案，這是給 coding agent 的 context 檔案，包含 build 指令、測試說明、程式碼風格、專案結構和邊界。只在缺少 AGENTS.md 的地方產生。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# AGENTS.md 產生器

為 repository 的資料夾產生高品質的 `AGENTS.md` 檔案。每個檔案都為 coding agent 提供專案專屬的 context：build 指令、測試說明、程式碼風格、結構和操作邊界。

## 什麼是 AGENTS.md

`AGENTS.md` 是 `README.md` 的補充。README 給人看，AGENTS.md 給 coding agent 看。

- **位置可預期**：Agent 會先找目前目錄的 `AGENTS.md`，再往上層目錄找
- **可以巢狀**：子資料夾可以有自己的 `AGENTS.md`，優先於根目錄那份
- **和 README 分開**：讓 README 保持精簡；agent 專屬的細節（確切的指令、邊界、慣例）放在這裡
- **和 `.github/agents/*.agent.md` 不一樣**：那些是 agent 的角色定義（agent 是誰）。`AGENTS.md` 是專案 context（agent 該知道這份程式碼的什麼事）

## 關鍵防護：只在缺少時才產生

> **這是最重要的一條規則。**

**絕對不准覆蓋現有的 AGENTS.md。**

為任何資料夾產生之前：

```bash
# Check if AGENTS.md already exists
ls AGENTS.md 2>/dev/null
```

- 如果已存在 → **跳過**並回報：`"AGENTS.md already exists at <path> — skipping"`
- 如果不存在 → 繼續產生
- 這個檢查對**每個資料夾各自獨立**適用

## 偵測該放 AGENTS.md 的資料夾

找出哪些資料夾應該有 `AGENTS.md`：

### 一定要產生：

- **Repository 根目錄**（`/`）
- **Wiki 資料夾**（`wiki/`）：如果是由 deep-wiki 產生的（有帶 VitePress 的 `package.json`）

### 存在的話就產生：

- `tests/`、`src/`、`lib/`、`app/`、`api/`
- Monorepo 套件：`packages/*/`、`apps/*/`、`services/*/`
- 任何有自己 build manifest 的資料夾：
  - `package.json`
  - `pyproject.toml`
  - `Cargo.toml`
  - `*.csproj` / `*.fsproj`
  - `go.mod`
  - `pom.xml` / `build.gradle`
- `.github/`：只有裡面有 workflow 或 action 時

### 一律跳過：

- `node_modules/`、`.git/`、`dist/`、`build/`、`out/`、`target/`
- `vendor/`、`.venv/`、`venv/`、`__pycache__/`
- 任何是產生出來的輸出或第三方相依套件的目錄

## 六大核心領域

每份好的 AGENTS.md 都涵蓋這些領域，並依資料夾裡實際有的東西調整。專案沒有的東西，不要硬發明段落。

### a) Build 與執行指令：放最前面

Agent 會一直參考這些。要用確切的指令和 flag，不要只寫工具名稱。

```markdown
## Build & Run

npm install          # Install dependencies
npm run dev          # Start dev server (port 3000)
npm run build        # Production build
npm run lint         # Run ESLint
```

從這些來源找真正的指令：
- `package.json` → `scripts` 區塊
- `Makefile` → targets
- `pyproject.toml` → `[tool.poetry.scripts]` 或 `[project.scripts]`
- `Cargo.toml` → 標準的 cargo 指令
- CI 設定 → `.github/workflows/*.yml`、`Jenkinsfile`、`.gitlab-ci.yml`

### b) 測試說明

```markdown
## Testing

pytest tests/ -v                    # Run all tests
pytest tests/test_auth.py -v        # Run single file
pytest -k "test_login" -v           # Run single test by name
pytest --cov=src --cov-report=term  # With coverage
```

要包含：
- 測試框架和它的設定方式
- 怎麼跑全部測試、單一檔案、單一測試
- commit 之前預期的行為（例如「所有測試都必須通過」）

### c) 專案結構

```markdown
## Project Structure

src/
├── api/          # FastAPI route handlers
├── models/       # Pydantic data models
├── services/     # Business logic
└── utils/        # Shared utilities

tests/            # Mirrors src/ structure
```

要包含：
- 主要目錄和它們裡面的內容
- 進入點（例如 `src/main.py`、`src/index.ts`）
- 新功能該加在哪裡

### d) 程式碼風格與慣例

一個真實的程式碼範例，勝過三段描述。

```markdown
## Code Style

- snake_case for functions and variables
- PascalCase for classes
- Type hints on all function signatures
- Async/await for I/O operations

### Example

```python
async def get_user_by_id(user_id: str) -> User:
    """Fetch a user by their unique identifier."""
    async with get_db_session() as session:
        return await session.get(User, user_id)
```
```

讀現有程式碼來偵測慣例：
- 命名模式（camelCase、snake_case、PascalCase）
- Import 的組織方式（stdlib → 第三方 → 本地）
- Module 結構模式

### e) Git 工作流程

```markdown
## Git Workflow

- Branch naming: `feature/`, `fix/`, `chore/`
- Commit messages: conventional commits (`feat:`, `fix:`, `docs:`)
- Run `npm test && npm run lint` before committing
- PR titles follow conventional commit format
```

只有 repo 有慣例的證據時才放（例如 commitlint 設定、PR 範本、貢獻指南）。

### f) 邊界

用三層系統：

```markdown
## Boundaries

- ✅ **Always do:** Run tests before committing. Write tests for new features. Use type hints.
- ⚠️ **Ask first:** Adding new dependencies. Changing database schemas. Modifying CI/CD configs. Changing public API signatures.
- 🚫 **Never do:** Commit secrets or credentials. Modify `vendor/` or `node_modules/`. Push directly to `main`. Delete migration files.
```

依專案調整邊界：
- 後端專案：schema 變更、API 契約
- 前端專案：會破壞元件 API、design system 變更
- 基礎設施：正式環境設定、IAM 權限

## 產生流程

為特定資料夾產生 AGENTS.md 時：

### 步驟 1：檢查是否存在

```bash
ls <folder>/AGENTS.md 2>/dev/null
```

如果存在，**停下來**。回報並換下一個資料夾。

### 步驟 2：掃描資料夾

找出：
- 主要語言（Python、TypeScript、Rust、Go、Java、C#）
- Framework（FastAPI、Next.js、Actix、Spring Boot）
- Build 工具（npm、cargo、poetry、maven、gradle）
- 測試執行器（pytest、vitest、cargo test、JUnit）

### 步驟 3：讀設定檔

從這些地方擷取真實的指令和設定：
- `package.json` 的 scripts
- `Makefile` / `Justfile` 的 targets
- `pyproject.toml` 的 scripts 和工具設定
- `Cargo.toml` 的 metadata
- `.github/workflows/*.yml` 的 build/test 步驟
- `docker-compose.yml` 的服務定義
- Linter 設定（`.eslintrc`、`ruff.toml`、`rustfmt.toml`）

### 步驟 4：偵測慣例

讀 3 到 5 個原始碼檔案，找出：
- 命名模式
- Import 的組織方式
- 錯誤處理風格
- 註解風格
- Module 結構

### 步驟 5：撰寫 AGENTS.md

只用適用的段落。如果資料夾沒有測試，就省略測試段落。如果沒有 CI 設定，就省略 git 工作流程。

### 步驟 6：驗證

寫入檔案之前：
- 每個指令都參照到真實的 script、target 或工具
- 每個檔案路徑都參照到實際存在的檔案或目錄
- 沒有像 `<your-project>` 或 `TODO` 這樣的 placeholder 文字
- 沒有為不存在的東西發明段落

## 範本結構

```markdown
# [Folder Name] — Agent Instructions

## Overview
[1-2 sentences: what this folder/project does, its role in the larger system]

## Build & Run
[Exact commands — install, dev, build, clean]

## Testing
[Framework, run commands, single-test commands]

## Project Structure
[Key directories, entry points, where to add new things]

## Code Style
[Naming conventions + one real code example from this project]

## Boundaries
- ✅ **Always do:** [safe operations]
- ⚠️ **Ask first:** [risky operations]
- 🚫 **Never do:** [dangerous operations]

## Documentation
[Only include if wiki/, llms.txt, or docs/ exist in the repo]
- Wiki: `wiki/` — architecture, API, onboarding guides
- LLM Context: `llms.txt` — project summary for coding agents (full version: `wiki/llms-full.txt`)
- Onboarding: `wiki/onboarding/` — guides for contributors, staff engineers, executives, PMs
```

不適用的段落一律省略。一份 20 行、有真實指令的 AGENTS.md，勝過 200 行充滿通用廢話的。

## 根目錄 vs 巢狀 AGENTS.md

### 根目錄 AGENTS.md（`/AGENTS.md`）

涵蓋整個專案：
- 整體技術堆疊和架構
- 全域慣例和程式碼標準
- 開發環境設定
- 整個 repository 的邊界
- CI/CD 概觀

### 巢狀 AGENTS.md（例如 `tests/AGENTS.md`）

涵蓋那個特定的子資料夾：
- 這個資料夾做什麼、為什麼存在
- 該資料夾專屬的指令（例如 `cd tests && pnpm test`）
- 該資料夾專屬的慣例
- **不應該**重複根目錄層級的內容

### Wiki AGENTS.md（`wiki/AGENTS.md`）

產生之前**一定要檢查** `wiki/AGENTS.md` 是否存在，和其他資料夾一樣是「缺少才產生」的防護。如果存在，就跳過。

用這個範本（依實際專案調整）：

```markdown
# Wiki — Agent Instructions

## Overview
Generated VitePress documentation site. Contains architecture docs, onboarding guides, and API references with source-linked citations and dark-mode Mermaid diagrams.

## Build & Run
- Install: `npm install`
- Dev server: `npm run dev`
- Build: `npm run build`
- Preview: `npm run preview`

## Wiki Structure
- `index.md` — Landing page with project overview and navigation
- `onboarding/` — Audience-tailored guides (contributor, staff engineer, executive, product manager)
- `{NN}-{section}/` — Numbered documentation sections
- `llms.txt` — LLM-friendly project summary (links + descriptions)
- `llms-full.txt` — LLM-friendly full content (inlined pages)
- `.vitepress/config.mts` — VitePress config with sidebar and Mermaid setup
- `.vitepress/theme/` — Dark theme (custom.css) and zoom handlers (index.ts)

## Content Conventions
- All Mermaid diagrams use dark-mode colors (fills `#2d333b`, borders `#6d5dfc`, text `#e6edf3`)
- Every page has VitePress frontmatter (`title`, `description`)
- Citations link to source repository with line numbers
- Tables include a "Source" column with linked citations
- Mermaid diagrams followed by `<!-- Sources: ... -->` comment blocks

## Boundaries
- ✅ **Always do:** Add new pages following existing section numbering, use dark-mode Mermaid colors
- ⚠️ **Ask first:** Change theme CSS, modify VitePress config, restructure sections
- 🚫 **Never do:** Delete generated pages without understanding dependencies, use light-mode colors, remove citation links

## Documentation
- Wiki: `./` — This folder is the wiki
- LLM Context: `llms.txt` — Quick summary; `llms-full.txt` — Full content
- Onboarding: `onboarding/` — Four audience-tailored guides
```

填入真實的章節名稱、技術和專案專屬的慣例。

Agent 會讀目錄樹裡最近的 AGENTS.md。巢狀檔案優先，所以它們應該放資料夾專屬的細節，不是全域的。

## CLAUDE.md 配套檔案

每當你在某個資料夾產生 `AGENTS.md`，也要在同一個資料夾產生 `CLAUDE.md`，**但只有 `CLAUDE.md` 不存在時才產生**。

`CLAUDE.md` 的內容永遠只有這樣：

```markdown
# CLAUDE.md

<!-- Generated for repository development workflows. Do not edit directly. -->

Before beginning work in this repository, read `AGENTS.md` and follow all scoped AGENTS guidance.
```

這樣能確保 Claude Code（以及其他會找 `CLAUDE.md` 的類似工具）被導向權威的 `AGENTS.md` 指示。

**同樣的防護適用：** 寫入之前先檢查 `CLAUDE.md` 是否存在。如果存在，就跳過。

## 品質原則

| 原則 | 好 | 壞 |
|-----------|------|-----|
| **具體** | "React 18 with TypeScript, Vite, Tailwind CSS" | "React project" |
| **可執行** | `pytest tests/ -v --tb=short` | "run the tests" |
| **有根據** | 放這個專案的真實程式碼片段 | 用抽象的詞描述風格 |
| **真實路徑** | `src/api/routes/` | `path/to/your/code/` |
| **誠實** | 沒有測試就省略測試段落 | 發明一個測試段落 |
| **精簡** | 大多數資料夾 30 到 80 行 | 300 多行的散文 |

## 要避免的反模式

- ❌ **"You are a helpful coding assistant"**：太模糊，描述的是感覺不是動作
- ❌ **通用的制式內容**：任何專案都適用的內容沒有價值
- ❌ **發明的指令/路徑**：每個指令和路徑都必須參照到真實存在的東西
- ❌ **重複 README.md**：AGENTS.md 是補充 README，不是複製它
- ❌ **放入 secret**：絕對不要把憑證、API key 或 token 放進 AGENTS.md
- ❌ **覆蓋現有檔案**：如果 AGENTS.md 已存在，不要碰它
- ❌ **硬塞空的段落**：沒有測試就不要寫測試段落
- ❌ **描述 agent 該「想」或「感覺」什麼**：描述它們該**做**什麼
