---
name: scan
description: 掃描 codebase 來產生 project-doc.md 和 AGENTS.md。在為新的 agent 驅動 repo 做初始化、架構變動後刷新專案文件，或跑 delta scan 偵測偏移時使用。第一次使用跑完整掃描，之後的執行跑聰明的 delta 掃描。有 understand-anything + context-mode 就用，沒有就退回原生工具。只有在偵測到架構變動、且經過人工確認後，才會更新 AGENTS.md。
---

# Codebase Scanner

你是技術分析師。你的工作是掃描專案的 codebase，產出準確、專屬於這個專案的文件，供所有下游 agent 使用。

## Step 1: Check Optional Plugin Dependencies

檢查兩個選用的加強 plugin 有沒有裝：

```
understand-anything  →  /plugin list | grep understand-anything
context-mode         →  /plugin list | grep context-mode
```

這些 plugin 是**選用的**。它們能提升掃描品質，但不是必要的：

- **understand-anything**（Lum1104/Understand-Anything）：提供更深入的語意程式碼分析
- **context-mode**（mksglu/context-mode）：把大量輸出導進 sandbox，保護 context window

如果兩個都有，就照下面的說明在 Step 3–4 使用。如果缺了其中一個或兩個都缺，就走**原生 fallback** 的做法：直接用 `find`、`grep`、`cat` 和 `git` 指令，如果有 context-mode，大量輸出就導進 `ctx_execute` / `ctx_execute_file`，沒有的話就在行內做摘要。

> **注意：** 要手動安裝這些選用 plugin：
> ```
> /plugin marketplace add Lum1104/Understand-Anything && /plugin install understand-anything
> /plugin marketplace add mksglu/context-mode && /plugin install context-mode@context-mode
> ```

## Step 2: Determine Scan Mode

檢查 `.claude/pipeline/project-doc.md` 是否存在。

- **不存在** → FULL SCAN（第一次執行）
- **存在** → DELTA SCAN

## Step 3A: Full Scan

用 `understand-anything` 分析整個 codebase。如果有 **context-mode**（在 Step 1 確認過），所有輸出都要經過它的工具（`ctx_batch_execute` / `ctx_execute_file`），絕對不要把原始檔案內容倒進主要的 context window。如果沒有 context-mode，就在行內摘要每個檔案的發現，避免印出原始檔案內容。

用下面的結構產出 `.claude/pipeline/project-doc.md`（依據 architecture-blueprint-generator 的模式）：

```md
# Project Documentation
> Generated: [timestamp] | Mode: FULL

## Tech Stack
- Runtime: [e.g. Node.js 20, Python 3.11]
- Language: [e.g. TypeScript, Python]
- Framework: [e.g. Next.js 14 App Router, FastAPI]
- Database: [e.g. PostgreSQL via Prisma]
- Styling: [e.g. Tailwind CSS]
- State Management: [e.g. Zustand, Redux]

## Dependencies
[主要函式庫和版本，依以下分組：core / dev / testing]

## Architecture Pattern
[e.g. Feature-based, Layered MVC, Clean Architecture]
[描述專案是怎麼組織的，以及為什麼這樣組織]

## Folder Structure
[最上層的目錄對照表，註明每個資料夾的用途]

## Code Style Conventions
[命名模式、檔案命名、import 順序、export 模式]
[從實際程式碼推斷，不是猜的]

## Modularity Practices
[關注點怎麼分離、共用模組放在哪、service 的模式]

## Data Architecture
[實體關係、資料存取模式、ORM 的使用方式]

## Cross-Cutting Concerns
[auth/authz 的做法、錯誤處理模式、logging、驗證]

## Service Communication
[REST / GraphQL / event-driven，記錄實際存在的]

## Test Coverage
- Overall coverage: [X%]
- Testing framework: [e.g. Jest, Vitest, Pytest]
- Key untested areas: [list]
- Test patterns used: [unit / integration / e2e]

## Entry Points
[主要檔案、重要的設定檔、環境設定]

## Changed Files
[只會出現在 delta scan：重新掃描過的檔案清單]

## Last Scanned
[ISO timestamp]
```

寫完 `project-doc.md` 之後，繼續到 **Step 4** 產生 `AGENTS.md`。

## Step 3B: Delta Scan

1. 執行 `git diff HEAD~1 --name-only` 取得有變動的檔案
2. 如果沒有變動的檔案，回報「No changes detected — project-doc.md is current」並結束
3. 用 `understand-anything` 只重新分析有變動的檔案；如果有 context-mode，輸出就導進 `ctx_execute_file`，沒有的話就在行內摘要
4. 只修補 `.claude/pipeline/project-doc.md` 中受影響的段落
5. 更新 `Last Scanned` 和 `Changed Files` 欄位
6. 繼續到 **Step 4B**（偵測架構變動）

## Step 4A: Generate AGENTS.md (First Run Only)

把 `AGENTS.md` 寫到 repo 根目錄。這不是 `project-doc.md` 的複本，而是改寫成給 agent 的指示，針對這個專案量身訂做。每個 agent 都會先讀這個檔案。

寫 AGENTS.md 之前，先讀過並完整遵循[專案專屬的指示範本](references/agents-template.md)，包含它的安全規則和需經人工確認才能更新的要求。

如果專案是 MERN stack（MongoDB + Express + React + Node.js，從 package.json / requirements 偵測），就在 AGENTS.md 附加一個 `### MERN Stack Notes` 段落，涵蓋：優先用 Mongoose middleware 而不是原始 query、在 Express 用集中的 error handler 處理 async 錯誤、避免把 JWT token 存在 localStorage（改用 httpOnly cookie），以及絕對不要把 Mongoose 的 error 物件直接暴露在 API 回應裡。

## Step 4B: Architectural Change Detection (Delta Runs Only)

修補完 `project-doc.md` 後，把新版本跟之前的版本比較。檢查：
- 有沒有新增框架或重要函式庫
- 有沒有建立新的架構性目錄模式（例如新的 `/lib/hooks/`、`/services/`）
- 有沒有重大的依賴替換（例如 axios → fetch、moment → dayjs）
- 有沒有新的 auth 或 session 處理模式

如果偵測到任何一項，就顯示：

```
⚠️  Architectural change detected in delta scan:
    [List specific changes found]

AGENTS.md may need updating. Review and confirm:
  [y] Update AGENTS.md — patch affected sections only
  [n] Skip — this is not an architectural change
```

只有在使用者按 `[y]` 確認時：才修補 `AGENTS.md` 的相關段落。絕對不要重寫整個檔案。

## Step 5: Report

印出摘要：

```
✅ Scan complete ([FULL/DELTA])
   project-doc.md → updated
   AGENTS.md      → [generated / patched / unchanged]
   Changed files  → [N files re-scanned / N/A for full scan]
   Coverage       → [X%]
```

把 `state.json` 的 `checkpoints.scan` 欄位更新成 `"completed"`。
