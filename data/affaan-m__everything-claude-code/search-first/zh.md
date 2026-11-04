---
name: search-first
description: "先研究再寫程式的工作流程：在寫自訂程式碼之前，先搜尋 npm/PyPI、MCP server、skill 和 GitHub 有沒有現成工具，再決定採用、擴充或自己建。遇到不簡單的需求時啟動 researcher agent。開始做功能、新增相依套件或整合、或正要寫一個可能已經有人做過的工具函式時使用。"
metadata:
  origin: ECC
---

# /search-first：先研究，再寫程式

把「實作之前先找現有解法」的流程系統化。

## 觸發時機

在這些情況使用這個 skill：
- 開始做一個可能已有現成解法的新功能
- 新增相依套件或整合
- 使用者說「加上 X 功能」，而你正要開始寫程式
- 建立新的工具函式、helper 或抽象層之前

## 工作流程

```
┌─────────────────────────────────────────────┐
│  0. TOOL AVAILABILITY PREFLIGHT             │
│     Check search channels before relying on │
│     them; report skipped channels honestly   │
├─────────────────────────────────────────────┤
│  1. NEED ANALYSIS                           │
│     Define what functionality is needed      │
│     Identify language/framework constraints  │
├─────────────────────────────────────────────┤
│  2. PARALLEL SEARCH (researcher agent)      │
│     ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│     │  npm /   │ │  MCP /   │ │  GitHub / │  │
│     │  PyPI    │ │  Skills  │ │  Web      │  │
│     └──────────┘ └──────────┘ └──────────┘  │
├─────────────────────────────────────────────┤
│  3. EVALUATE                                │
│     Score candidates (functionality, maint, │
│     community, docs, license, deps)         │
├─────────────────────────────────────────────┤
│  4. DECIDE                                  │
│     ┌─────────┐  ┌──────────┐  ┌─────────┐  │
│     │  Adopt  │  │  Extend  │  │  Build   │  │
│     │ as-is   │  │  /Wrap   │  │  Custom  │  │
│     └─────────┘  └──────────┘  └─────────┘  │
├─────────────────────────────────────────────┤
│  5. IMPLEMENT                               │
│     Install package / Configure MCP /       │
│     Write minimal custom code               │
└─────────────────────────────────────────────┘
```

## 決策矩陣

| 訊號 | 動作 |
|--------|--------|
| 完全吻合、維護良好、MIT/Apache | **Adopt**：直接安裝使用 |
| 部分吻合、基礎不錯 | **Extend**：安裝後再寫一層薄薄的 wrapper |
| 多個都不太夠 | **Compose**：組合 2 到 3 個小套件 |
| 找不到合適的 | **Build**：自己寫，但要以研究結果為依據 |

## 使用方式

### 步驟 0：工具可用性預檢

這是給 agent 的指引，不是可執行的設定 script。只檢查跟眼前任務和專案相關的管道。

| 管道 | 檢查方式 | 缺少時 |
|---------|-------|------------|
| Repository 搜尋 | `rg --files` 和針對性的 `rg` 查詢 | 說明只檢視了看得到的檔案 |
| 套件 registry | `npm --version`、`python -m pip --version` 或專案的套件管理工具 | 改用網頁/文件搜尋，並避免宣稱涵蓋了 registry |
| GitHub CLI | `gh auth status` | 只用公開網頁或本地 git 歷史 |
| MCP/文件工具 | 可用工具清單或本地 MCP 設定 | 退回官方文件/網頁搜尋 |
| Skills 目錄 | 適用時用 `ls ~/.claude/skills ~/.codex/skills` | 說明沒有可用的本地 skill 目錄 |

### 快速模式（內聯）

寫工具函式或加功能之前，在腦中跑一遍：

0. Repo 裡已經有了嗎？ → 先對相關模組/測試用 `rg` 搜
1. 這是常見問題嗎？ → 搜 npm/PyPI
2. 有對應的 MCP 嗎？ → 查 `~/.claude/settings.json` 並搜尋
3. 有對應的 skill 嗎？ → 查 `~/.claude/skills/`
4. 有 GitHub 上的實作/範本嗎？ → 在寫全新程式碼之前，先對有在維護的開源專案跑 GitHub 程式碼搜尋

### 完整模式（agent）

遇到不簡單的功能，就啟動 researcher agent：

```
Agent(subagent_type="general-purpose", prompt="
  Research existing tools for: [DESCRIPTION]
  Language/framework: [LANG]
  Constraints: [ANY]

  Search: npm/PyPI, MCP servers, Claude Code skills, GitHub
  Return: Structured comparison with recommendation
")
```

舊版 Claude Code 文件可能叫它 `Task(...)`，請使用目前 harness 提供的 agent/subagent 工具名稱。

## 依類別的搜尋捷徑

### 開發工具
- Linting → `eslint`、`ruff`、`textlint`、`markdownlint`
- 格式化 → `prettier`、`black`、`gofmt`
- 測試 → `jest`、`pytest`、`go test`
- Pre-commit → `husky`、`lint-staged`、`pre-commit`

### AI/LLM 整合
- Claude SDK → 用 Context7 查最新文件
- Prompt 管理 → 查 MCP server
- 文件處理 → `unstructured`、`pdfplumber`、`mammoth`

### 資料與 API
- HTTP client → `httpx`（Python）、`ky`/`undici`（Node）
- 驗證 → `zod`（TS）、`pydantic`（Python）
- 資料庫 → 先查有沒有 MCP server

### 內容與發布
- Markdown 處理 → `remark`、`unified`、`markdown-it`
- 圖片最佳化 → `sharp`、`imagemin`

## 整合點

### 搭配 planner agent
Planner 應該在階段 1（架構檢視）之前呼叫 researcher：
- Researcher 找出可用的工具
- Planner 把它們納入實作計畫
- 避免在計畫裡「重造輪子」

### 搭配 architect agent
Architect 應該找 researcher 諮詢：
- 技術堆疊決策
- 整合模式探索
- 現有的參考架構

### 搭配 iterative-retrieval skill
結合使用，做漸進式探索：
- 第 1 輪：廣泛搜尋（npm、PyPI、MCP）
- 第 2 輪：詳細評估最優的候選
- 第 3 輪：測試跟專案限制的相容性

## 範例

### 範例 1：「加上死連結檢查」
```
Need: Check markdown files for broken links
Search: npm "markdown dead link checker"
Found: textlint-rule-no-dead-link (score: 9/10)
Action: ADOPT — npm install textlint-rule-no-dead-link
Result: Zero custom code, battle-tested solution
```

### 範例 2：「加上 HTTP client wrapper」
```
Need: Resilient HTTP client with retries and timeout handling
Search: npm "http client retry", PyPI "httpx retry"
Found: got (Node) with retry plugin, httpx (Python) with built-in retry
Action: ADOPT — use got/httpx directly with retry config
Result: Zero custom code, production-proven libraries
```

### 範例 3：「加上設定檔 linter」
```
Need: Validate project config files against a schema
Search: npm "config linter schema", "json schema validator cli"
Found: ajv-cli (score: 8/10)
Action: ADOPT + EXTEND — install ajv-cli, write project-specific schema
Result: 1 package + 1 schema file, no custom validation logic
```

## 反模式

- **直接跳去寫程式**：沒檢查有沒有現成的就開始寫工具函式
- **忽略 MCP**：沒檢查是否已有 MCP server 提供這個能力
- **默默跳過**：某個搜尋管道其實不可用，卻回報「什麼都沒找到」
- **過度客製化**：把函式庫包得太厚，結果失去它原本的好處
- **相依套件膨脹**：為了一個小功能，裝一個龐大的套件
