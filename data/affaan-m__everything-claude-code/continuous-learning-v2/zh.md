---
name: continuous-learning-v2
description: 以 instinct 為基礎的學習系統，透過 hook 觀察 session，建立帶信心分數的原子 instinct，並把它們演化成 skill/指令/agent。v2.1 加入以專案為範圍的 instinct，避免跨專案污染。適用於從 session 擷取教訓、管理 instinct，或把它們升級成 skill、指令或 agent 時。
metadata:
  version: 2.1.0
  origin: ECC
---

# Continuous Learning v2.1 - Instinct
-Based Architecture

一套進階的學習系統，透過原子化的「instinct」（帶信心分數的小型學習行為），把你的 Claude Code session 變成可重複使用的知識。

**v2.1** 加入了**以專案為範圍的 instinct**：React 的模式留在你的 React 專案，Python 的慣例留在你的 Python 專案，而通用的模式（例如「一律驗證輸入」）則全域共享。

## When to Activate

- 設定從 Claude Code session 自動學習
- 透過 hook 設定以 instinct 為基礎的行為擷取
- 調整學習行為的信心門檻
- 審查、匯出或匯入 instinct 資料庫
- 把 instinct 演化成完整的 skill、指令或 agent
- 管理以專案為範圍 vs 全域的 instinct
- 把 instinct 從專案範圍升級到全域範圍

## What's New in v2.1

| Feature | v2.0 | v2.1 |
|---------|------|------|
| Storage | Global (`~/.claude/homunculus/`) | Project-scoped (`${XDG_DATA_HOME:-~/.local/share}/ecc-homunculus/projects/<hash>/`) |
| Scope | 所有 instinct 到處都適用 | 專案範圍 + 全域 |
| Detection | 無 | git remote URL / repo 路徑 |
| Promotion | N/A | 在 2 個以上專案出現時，從專案升級到全域 |
| Commands | 4 (status/evolve/export/import) | 6 (+promote/projects) |
| Cross-project | 有污染風險 | 預設隔離 |

## What's New in v2 (vs v1)

| Feature | v1 | v2 |
|---------|----|----|
| Observation | Stop hook (session 結束) | PreToolUse/PostToolUse (100% 可靠) |
| Analysis | 主 context | 背景 agent (Haiku) |
| Granularity | 完整的 skill | 原子的「instinct」 |
| Confidence | 無 | 0.3-0.9 加權 |
| Evolution | 直接變成 skill | Instincts -> 聚合 -> skill/指令/agent |
| Sharing | 無 | 匯出/匯入 instinct |

## The Instinct Model

instinct 是一個小型的學習行為：

```yaml
---
id: prefer-functional-style
trigger: "when writing new functions"
confidence: 0.7
domain: "code-style"
source: "session-observation"
scope: project
project_id: "a1b2c3d4e5f6"
project_name: "my-react-app"
---

# Prefer Functional Style

## Action
Use functional patterns over classes when appropriate.

## Evidence
- Observed 5 instances of functional pattern preference
- User corrected class-based approach to functional on 2025-01-15
```

**屬性：**
- **原子性**：一個觸發條件，一個動作
- **以信心加權**：0.3 = 暫定，0.9 = 近乎確定
- **有領域標記**：code-style、testing、git、debugging、workflow 等等
- **有證據支撐**：追蹤是哪些觀察產生了它
- **知道範圍**：`project`（預設）或 `global`

## How It Works

```
Session Activity (in a git repo)
      |
      | Hooks capture prompts + tool use (100% reliable)
      | + detect project context (git remote / repo path)
      v
+---------------------------------------------+
|  projects/<project-hash>/observations.jsonl  |
|   (prompts, tool calls, outcomes, project)   |
+---------------------------------------------+
      |
      | Observer agent reads (background, Haiku)
      v
+---------------------------------------------+
|          PATTERN DETECTION                   |
|   * User corrections -> instinct             |
|   * Error resolutions -> instinct            |
|   * Repeated workflows -> instinct           |
|   * Scope decision: project or global?       |
+---------------------------------------------+
      |
      | Creates/updates
      v
+---------------------------------------------+
|  projects/<project-hash>/instincts/personal/ |
|   * prefer-functional.yaml (0.7) [project]   |
|   * use-react-hooks.yaml (0.9) [project]     |
+---------------------------------------------+
|  instincts/personal/  (GLOBAL)               |
|   * always-validate-input.yaml (0.85) [global]|
|   * grep-before-edit.yaml (0.6) [global]     |
+---------------------------------------------+
      |
      | /evolve clusters + /promote
      v
+---------------------------------------------+
|  projects/<hash>/evolved/ (project-scoped)   |
|  evolved/ (global)                           |
|   * commands/new-feature.md                  |
|   * skills/testing-workflow.md               |
|   * agents/refactor-specialist.md            |
+---------------------------------------------+
```

## Project Detection

系統會自動偵測你目前的專案：

1. **`CLAUDE_PROJECT_DIR` 環境變數**（最高優先）：即使該目錄不是 git repo，也會被當成明確的覆寫值採用（以它的絕對路徑做雜湊）
2. **`git remote get-url origin`**：雜湊後產生可攜的專案 ID（不同機器上的同一個 repo 會得到同一個 ID）
3. **`git rev-parse --show-toplevel`**：備用方案，用 repo 路徑（跟機器有關）
4. **全域備用**：如果沒偵測到專案，instinct 就進入全域範圍

每個專案會得到一個 12 個字元的雜湊 ID（例如 `a1b2c3d4e5f6`）。位於 `${XDG_DATA_HOME:-~/.local/share}/ecc-homunculus/projects.json` 的登錄檔，把 ID 對應到人看得懂的名稱。

### Data Directory

Continuous-learning-v2 把 observer 資料存在 `~/.claude` 之外，這樣 Claude Code 的敏感路徑防護才不會擋掉背景的 instinct 寫入：

1. `CLV2_HOMUNCULUS_DIR`（設定為絕對路徑時）
2. `$XDG_DATA_HOME/ecc-homunculus`
3. `$HOME/.local/share/ecc-homunculus`

資料原本放在 `~/.claude/homunculus` 的既有使用者，可以一次性 migration：

```bash
bash skills/continuous-learning-v2/scripts/migrate-homunculus.sh
```

## Quick Start

### 1. Enable Observation Hooks

**如果是以 plugin 安裝**（建議）：

不需要額外的 `settings.json` hook 區塊。Claude Code v2.1+ 會自動載入 plugin 的 `hooks/hooks.json`，而 `observe.sh` 已經登記在裡面了。

如果你之前把 `observe.sh` 複製進了 `~/.claude/settings.json`，請移除那個重複的 `PreToolUse` / `PostToolUse` 區塊。重複 plugin 的 hook 會造成重複執行，以及 `${CLAUDE_PLUGIN_ROOT}` 解析錯誤，因為那個變數只能在 plugin 管理的 `hooks/hooks.json` 項目裡使用。

**如果是手動安裝**到 `~/.claude/skills`，把這段加到你的 `~/.claude/settings.json`：

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/continuous-learning-v2/hooks/observe.sh"
      }]
    }],
    "PostToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/continuous-learning-v2/hooks/observe.sh"
      }]
    }]
  }
}
```

### 2. Initialize Directory Structure

系統在第一次使用時會自動建立目錄，不過你也可以手動建立：

```bash
# Global directories
mkdir -p "${XDG_DATA_HOME:-$HOME/.local/share}/ecc-homunculus"/{instincts/{personal,inherited},evolved/{agents,skills,commands},projects}

# Project directories are auto-created when the hook first runs in a git repo
```

### 3. Use the Instinct Commands

```bash
/instinct-status     # Show learned instincts (project + global)
/evolve              # Cluster related instincts into skills/commands
/instinct-export     # Export instincts to file
/instinct-import     # Import instincts from others
/promote             # Promote project instincts to global scope
/projects            # List all known projects and their instinct counts
```

## Commands

| Command | Description |
|---------|-------------|
| `/instinct-status` | 顯示所有 instinct（專案範圍 + 全域）和信心分數 |
| `/evolve` | 把相關的 instinct 聚合成 skill/指令，並建議升級 |
| `/instinct-export` | 匯出 instinct（可依範圍/領域過濾） |
| `/instinct-import <file>` | 匯入 instinct，並控制範圍 |
| `/promote [id]` | 把專案 instinct 升級到全域範圍 |
| `/projects` | 列出所有已知的專案和它們的 instinct 數量 |

## Configuration

編輯 `config.json` 來控制背景 observer：

```json
{
  "version": "2.1",
  "observer": {
    "enabled": false,
    "run_interval_minutes": 5,
    "min_observations_to_analyze": 20
  }
}
```

| Key | Default | Description |
|-----|---------|-------------|
| `observer.enabled` | `false` | 啟用背景 observer agent |
| `observer.run_interval_minutes` | `5` | observer 多久分析一次觀察資料 |
| `observer.min_observations_to_analyze` | `20` | 開始分析之前最少需要的觀察數量 |

其他行為（觀察擷取、instinct 門檻、專案範圍、升級條件）是透過 `instinct-cli.py` 和 `observe.sh` 裡程式碼的預設值來設定。

### Observer platform support

背景 observer 需要 WSL2、Linux 或 macOS。在原生 Windows
（Git Bash / MSYS2）上，它會啟動並回報成功，但是當啟動它的 hook 結束、它的 Job Object 關閉時，
process 就會被殺掉，所以從來不會有分析在跑，在那裡設 `observer.enabled: true` 實際上沒有作用
（見 issue #2489）。

`observe.sh` 會在下一次 hook 被呼叫時偵測到這個狀況，並在 observer 連續
幾次都活不下來之後，把一則說明性的警告寫進 `observer-start.log`。

| Env var | Default | Description |
|---------|---------|-------------|
| `ECC_OBSERVER_NOSURVIVE_WARN_AFTER` | `3` | 記錄警告之前，連續活不下來的次數 |

## File Structure

```
${XDG_DATA_HOME:-~/.local/share}/ecc-homunculus/
+-- identity.json           # Your profile, technical level
+-- projects.json           # Registry: project hash -> name/path/remote
+-- observations.jsonl      # Global observations (fallback)
+-- instincts/
|   +-- personal/           # Global auto-learned instincts
|   +-- inherited/          # Global imported instincts
+-- evolved/
|   +-- agents/             # Global generated agents
|   +-- skills/             # Global generated skills
|   +-- commands/           # Global generated commands
+-- projects/
    +-- a1b2c3d4e5f6/       # Project hash (from git remote URL)
    |   +-- project.json    # Per-project metadata mirror (id/name/root/remote)
    |   +-- observations.jsonl
    |   +-- observations.archive/
    |   +-- instincts/
    |   |   +-- personal/   # Project-specific auto-learned
    |   |   +-- inherited/  # Project-specific imported
    |   +-- evolved/
    |       +-- skills/
    |       +-- commands/
    |       +-- agents/
    +-- f6e5d4c3b2a1/       # Another project
        +-- ...
```

## Scope Decision Guide

| Pattern Type | Scope | Examples |
|-------------|-------|---------|
| 語言/framework 慣例 | **project** | "Use React hooks", "Follow Django REST patterns" |
| 檔案結構偏好 | **project** | "Tests in `__tests__`/", "Components in src/components/" |
| 程式碼風格 | **project** | "Use functional style", "Prefer dataclasses" |
| 錯誤處理策略 | **project** | "Use Result type for errors" |
| 安全實務 | **global** | "Validate user input", "Sanitize SQL" |
| 一般最佳實務 | **global** | "Write tests first", "Always handle errors" |
| 工具工作流偏好 | **global** | "Grep before Edit", "Read before Write" |
| Git 實務 | **global** | "Conventional commits", "Small focused commits" |

## Instinct Promotion (Project -> Global)

同一個 instinct 以高信心出現在多個專案時，就是升級到全域範圍的候選。

**自動升級條件：**
- 同一個 instinct ID 出現在 2 個以上的專案
- 平均信心 >= 0.8

**怎麼升級：**

```bash
# Promote a specific instinct
python3 instinct-cli.py promote prefer-explicit-errors

# Auto-promote all qualifying instincts
python3 instinct-cli.py promote

# Preview without changes
python3 instinct-cli.py promote --dry-run
```

`/evolve` 指令也會建議升級的候選。

## Confidence Scoring

信心會隨時間演變：

| Score | Meaning | Behavior |
|-------|---------|----------|
| 0.3 | 暫定 | 會建議，但不強制 |
| 0.5 | 中等 | 相關時套用 |
| 0.7 | 強 | 自動核准套用 |
| 0.9 | 近乎確定 | 核心行為 |

**信心會提高**，當：
- 這個模式被反覆觀察到
- 使用者沒有更正建議的行為
- 來自其他來源的類似 instinct 意見一致

**信心會降低**，當：
- 使用者明確更正這個行為
- 長時間沒有觀察到這個模式
- 出現相反的證據

## Why Hooks vs Skills for Observation?

> "v1 relied on skills to observe. Skills are probabilistic -- they fire ~50-80% of the time based on Claude's judgment."

Hook 會 **100% 觸發**，具確定性。這代表：
- 每一次工具呼叫都被觀察到
- 不會漏掉任何模式
- 學習是全面的

## Backward Compatibility

v2.1 完全相容 v2.0 和 v1：
- 既有的全域 instinct 可以用 `scripts/migrate-homunculus.sh` 從 `~/.claude/homunculus/instincts/` migration 過來
- v1 留下來的 `~/.claude/skills/learned/` skill 仍然能用
- Stop hook 仍然會執行（但現在也會餵進 v2）
- 逐步 migration：兩套平行執行

## Privacy

- 觀察資料留在你機器的**本地**
- 專案範圍的 instinct 依專案隔離
- 只有 **instinct**（模式）可以匯出，原始觀察資料不行
- 不會分享任何實際的程式碼或對話內容
- 你控制什麼可以被匯出和升級

## Related

- [ECC-Tools GitHub App](https://github.com/apps/ecc-tools)：從 repo 歷史產生 instinct
- Homunculus：啟發 v2 以 instinct 為基礎架構的社群專案（原子化觀察、信心分數、instinct 演化管線）
- [The Longform Guide](https://x.com/affaanmustafa/status/2014040193557471352)：持續學習章節

---

*以 instinct 為基礎的學習：一個專案一個專案地，教 Claude 你的模式。*
