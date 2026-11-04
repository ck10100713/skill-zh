---
name: project-health
description: "一站式的專案設定與健康管理。建立新專案（settings.local.json、CLAUDE.md、.gitignore），稽核既有專案（權限、context 品質、MCP 涵蓋範圍、外洩的 secret、過時的文件），整理累積的雜物，擷取 session 學到的東西，並加入權限預設組。繁重的分析交給 sub-agent，讓主 context 保持乾淨。用 'project health'、'check project'、'setup project'、'kickoff'、'bootstrap'、'tidy permissions'、'clean settings'、'capture learnings'、'audit context'、'add python permissions' 或 'init project' 觸發。"
compatibility: claude-code-only
---

# Project Health

用一個 skill 搞定專案裡所有跟 Claude Code 設定有關的事。專案開始、中期或結束時都可以跑，它會自己判斷需要做什麼。

**目標**：零權限提示、context 檔案組織良好、沒有雜物。

## 什麼時候用

| 你說…… | 會發生什麼 |
|-----------|-------------|
| "project health" / "check project" | 完整稽核：權限 + context + 文件 |
| "setup project" / "kickoff" / "bootstrap" | 從零開始設定新專案 |
| "tidy permissions" / "clean settings" | 只修權限檔 |
| "capture learnings" / "update CLAUDE.md" | 儲存 session 中的發現 |
| "add python" / "add docker permissions" | 把一組預設加到既有設定 |
| "audit context" / "audit memory" | 只做 context 方面的稽核 |

## 架構：Sub-Agent

**繁重的分析在 sub-agent 裡跑**，讓主對話保持乾淨。主 agent 負責協調，sub-agent 負責掃描並回傳摘要。

### Agent 1：權限稽核員

用 `Task(subagent_type: "general-purpose")` 啟動。Prompt：

```
Read .claude/settings.local.json.

**Discover connected MCP servers**: Use ToolSearch (search "mcp") and extract unique
server prefixes from tool names (e.g. mcp__vault__secret_list → vault).

**Discover installed skills**: Use the Skill tool or ToolSearch to list available skills.
For each skill that has scripts/ in its directory, note what Bash patterns it needs
(python3, env var prefixes like GEMINI_API_KEY=*, etc.). Check the SKILL.md for any
MCP tools the skill references (e.g. mcp__vault__secret_get).

Report:
1. MCP servers connected but NOT in settings (missing)
2. MCP servers in settings but NOT connected (stale)
3. Skill permissions: Bash patterns and MCP tools that installed skills need but aren't approved
4. File access: check for Read/Edit/Write patterns for .claude/** and //tmp/**
   in project settings, and ~/Documents/**/~/.claude/** in global settings
5. Leaked secrets: entries containing API keys, tokens, bearer strings, hex >20 chars, base64 >20 chars
6. Legacy colon syntax: entries like Bash(git:*) instead of Bash(git *)
7. Junk entries: shell fragments (Bash(do), Bash(fi), Bash(then), Bash(else), Bash(done)),
   __NEW_LINE_* artefacts, loop body fragments (Bash(break), Bash(continue), Bash(echo *))
8. Duplicates: entries covered by a broader pattern (e.g. Bash(git add *) redundant if Bash(git *) exists)
9. Missing presets: based on files present, suggest presets from [permission-presets.md]

Prefer Read/Glob/Grep tools over Bash. If you need to scan multiple files or
run 3+ commands for one analysis, write a Python script to .jez/scripts/
and run it once (mkdir -p .jez/scripts first).

Return a structured summary, not raw data.
```

### Agent 2：Context 稽核員

用 `Task(subagent_type: "general-purpose")` 啟動。Prompt：

```
Audit the project context landscape at [repo-path]:

1. Find all CLAUDE.md files. For each:
   - Count lines (target: root 50-150, subdirs 15-50)
   - Score quality on 6 criteria (see quality-criteria.md)
   - Check for stale file/path references
   - Flag oversized files

2. Find .claude/rules/ topic files. Check sizes (target: 20-80 lines).

3. Detect project type from files present (see project-types.md).
   Check expected docs exist (ARCHITECTURE.md, DATABASE_SCHEMA.md, etc.)

4. Find public markdown (README.md, LICENSE, CONTRIBUTING.md).
   Check for overlap with CLAUDE.md content.

5. Check auto-memory at ~/.claude/projects/*/memory/MEMORY.md

6. If Cloudflare project: find all wrangler.jsonc/wrangler.toml files.
   Check each has "observability": { "enabled": true }. Flag any missing it.

Prefer Read/Glob/Grep tools over Bash. If you need to scan many files or
aggregate data across the repo, write a Python script to .jez/scripts/
and run it once rather than running many individual bash commands
(mkdir -p .jez/scripts first).

Return: project type, quality scores, missing docs, stale refs, overlaps,
size violations, observability gaps, and total markdown footprint.
```

### 平行執行

完整健康檢查時，**平行啟動兩個 agent**：

```
Task(subagent_type: "general-purpose", name: "permission-audit", prompt: "...")
Task(subagent_type: "general-purpose", name: "context-audit", prompt: "...")
```

兩者都回傳摘要。主 agent 把它們合併成一份報告，並提出修正建議。

## 模式 1：完整健康檢查

**預設模式。** 隨時都可以跑。

### 步驟

1. **平行**啟動權限稽核員和 Context 稽核員 agent
2. 把發現合併成一份報告：

   ```
   ## Project Health Report

   **Project type**: [detected type]
   **CLAUDE.md quality**: [score]/100 ([grade])

   ### Permissions
   - Missing MCP servers: [list]
   - Leaked secrets: [count] found
   - Legacy syntax: [count] entries
   - Missing presets: [list]

   ### Context
   - Oversized files: [list]
   - Stale references: [list]
   - Missing docs: [list]
   - Overlaps: [list]

   ### Recommended Fixes
   1. [fix 1]
   2. [fix 2]
   ...
   ```

3. 一次 yes/no 確認後，套用修正

## 模式 2：新專案設定

**什麼時候**：沒有 `.claude/settings.local.json`，或使用者說「setup」/「kickoff」。

### 步驟

1. 從現有檔案**偵測專案類型**：

   | 指標 | 類型 | 預設組 |
   |-----------|------|--------|
   | `wrangler.jsonc` 或 `wrangler.toml` | cloudflare-worker | JS/TS + Cloudflare |
   | `vercel.json` 或 `next.config.*` | vercel-app | JS/TS + Vercel |
   | `astro.config.*` | astro | JS/TS + Static Sites |
   | `package.json`（沒有部署目標） | javascript-typescript | JS/TS |
   | `pyproject.toml` 或 `setup.py` 或 `requirements.txt` | python | Python |
   | `Cargo.toml` | rust | Rust |
   | `go.mod` | go | Go |
   | `Gemfile` 或 `Rakefile` | ruby | Ruby |
   | `composer.json` 或 `wp-config.php` | php | PHP |
   | `pom.xml` 或 `build.gradle*` | java | Java/JVM |
   | `*.sln` 或 `*.csproj` | dotnet | .NET |
   | `mix.exs` | elixir | Elixir |
   | `Package.swift` | swift | Swift + macOS |
   | `pubspec.yaml` | flutter | Mobile |
   | `Dockerfile` 或 `docker-compose.yml` | docker | Docker |
   | `fly.toml` 或 `railway.json` 或 `netlify.toml` | hosted-app | Hosting Platforms |
   | `supabase/config.toml` | supabase | Hosting + Database |
   | `.claude/agents/` 或維運 script | ops-admin | — |
   | 空目錄 | 問使用者 | — |

   類型可以疊加（例如 cloudflare-worker + javascript-typescript）。

2. **產生 `.claude/settings.local.json`**：
   - 讀 [references/permission-presets.md](references/permission-presets.md)
   - 一定要包含 Universal Base（含 `.claude/**`、`//tmp/**` 的檔案存取）
   - 加上偵測到的語言 + 部署預設組
   - 檢查全域的 `~/.claude/settings.local.json` 有沒有以 home 為基準的檔案存取規則
     （`~/Documents/**`、`~/.claude/**`）。沒有的話，建議加在那邊
     （不要加在專案檔案裡，home 路徑只屬於全域設定）
   - **啟動權限稽核員 agent** 來找出 MCP server，並加上每個 server 的萬用字元規則
   - 一定要包含 `WebSearch`、`WebFetch`
   - 一定要包含明確的 `gh` 子指令（`Bash(gh *)` bug 的暫時解法）
   - 用 `//` 註解分組來寫

3. **產生 `CLAUDE.md`**：
   - 讀 [references/templates.md](references/templates.md)
   - 使用符合專案類型的範本

4. **產生 `.gitignore`**：
   - 讀 [references/templates.md](references/templates.md)
   - 一定要包含 `.claude/settings.local.json`、`.claude/plans/`、`.jez/screenshots/`、`.jez/artifacts/`
   - **不要**把 `.jez/scripts/` 加進 gitignore，產生的 script 值得留著

5. **選用**（先問）：`git init` + `gh repo create`

6. **警告**：「專案的 settings.local.json 會蓋過全域設定（不是合併）。需要重啟 session。」

## 模式 3：整理權限

**什麼時候**：使用者說「tidy permissions」，或健康檢查發現權限問題。

啟動權限稽核員 agent，然後套用它建議的修正。

## 模式 4：擷取學到的東西

**什麼時候**：session 結束時、「capture learnings」、「save what we learned」。

這個模式在**主 context** 裡跑（不是 sub-agent），因為它需要存取對話歷史。

1. 回顧對話，找出值得保存的發現
2. 決定放哪裡：
   ```
   Applies to all projects?
   ├── YES → ~/.claude/rules/<topic>.md
   └── NO  → Specific to a subdirectory?
       ├── YES → <dir>/CLAUDE.md
       └── NO  → Reference or operational?
           ├── Reference → docs/ or ARCHITECTURE.md
           └── Operational → ./CLAUDE.md (root)
   ```
3. 把所有改動一次起草成 diff
4. 一次 yes/no 確認後套用

**保持精簡**：一個概念一行。

## 模式 5：加入預設組

**什麼時候**：「add python permissions」、「add docker」、「add MCP servers」。

1. 從 [references/permission-presets.md](references/permission-presets.md) 讀取預設組
2. 讀既有的 `.claude/settings.local.json`
3. 合併，不要重複
4. 提醒：**需要重啟 session**

## 模式 6：重組 Context

**什麼時候**：根目錄的 CLAUDE.md 超過 200 行、「restructure memory」。

1. 先啟動 Context 稽核員 agent
2. 依發現：
   - 把過大的 CLAUDE.md 拆成 `.claude/rules/<topic>.md`
   - 把特定目錄的內容抽到子目錄的 CLAUDE.md
   - 把參考資料搬到 `docs/`
   - 解決重疊
   - 為專案類型建立缺少的文件
3. 呈現計畫，核准後套用

### 大小目標

| 檔案 | 目標 | 上限 |
|------|--------|---------|
| 根目錄 CLAUDE.md | 50-150 行 | 200 |
| 子目錄 CLAUDE.md | 15-50 行 | 80 |
| Rules 主題檔 | 20-80 行 | 120 |

## 權限語法速查

| 規則 | 意義 |
|---------|---------|
| `Bash(git *)` | 建議用法：`*` 前面的空格代表字詞邊界 |
| `Bash(nvidia-smi)` | 完全比對，不帶參數 |
| `WebFetch` | 全面的網頁抓取 |
| `WebSearch` | 全面的網頁搜尋 |
| `mcp__servername__*` | 某個 MCP server 的所有工具 |

### 不會動的寫法

| 規則 | 原因 |
|---------|-----|
| `mcp__*` | 萬用字元不能跨過 `__` 邊界 |
| `mcp__*__*` | 一樣不行 |
| `Bash(git:*)` | 已棄用的冒號語法（還能用，但建議用空格） |

### 重要行為

- **不會熱重載**：改了 `settings.local.json` 需要重啟 session
- **「Don't ask again」** 會在執行時用冒號格式寫入（不需重啟），這是正常的
- **是蓋過，不是合併**：專案設定會完全取代全域設定
- **`gh` bug**：`Bash(gh *)` 有時會漏掉子指令，所以要明確列出 `Bash(gh issue *)` 等

## 自主程度

- **直接做**：偵測專案類型、啟動稽核 agent、找出 MCP server
- **簡短確認**：寫入/更新檔案（一次 yes/no）
- **先問**：git init、GitHub repo、刪除既有內容、大型重組

## 參考檔案

| 什麼時候 | 讀什麼 |
|------|------|
| 建立權限預設組 | [references/permission-presets.md](references/permission-presets.md) |
| 產生 CLAUDE.md、.gitignore | [references/templates.md](references/templates.md) |
| 為 CLAUDE.md 品質評分 | [references/quality-criteria.md](references/quality-criteria.md) |
| 偵測專案類型 + 預期文件 | [references/project-types.md](references/project-types.md) |
| 設定 commit 擷取 hook | [references/commit-hook.md](references/commit-hook.md) |
