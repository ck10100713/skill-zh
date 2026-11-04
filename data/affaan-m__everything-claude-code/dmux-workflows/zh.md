---
name: dmux-workflows
description: 用 dmux（給 AI agent 用的 tmux pane 管理工具）做多 agent 編排。涵蓋在 Claude Code、Codex、OpenCode 與其他 harness 之間做平行 agent 工作流的模式。在同時跑多個 agent session 或協調多 agent 開發流程時使用。
metadata:
  origin: ECC
---

# dmux 工作流

用 dmux（一個給 agent harness 用的 tmux pane 管理工具）來編排平行的 AI agent session。

## 何時啟用

- 同時跑多個 agent session
- 在 Claude Code、Codex 與其他 harness 之間協調工作
- 適合用分而治之、平行處理的複雜任務
- 使用者說「平行跑」、「把這個工作拆開」、「用 dmux」或「multi-agent」

## 什麼是 dmux

dmux 是一個以 tmux 為基礎的編排工具，負責管理 AI agent 的 pane：
- 按 `n` 用一個 prompt 建立新 pane
- 按 `m` 把 pane 的輸出 merge 回主 session
- 支援：Claude Code、Codex、OpenCode、Cline、Gemini、Qwen

**安裝：** 先檢查過套件內容，再從它的 repo 安裝 dmux。見 [github.com/standardagents/dmux](https://github.com/standardagents/dmux)

## 快速開始

```bash
# Start dmux session
dmux

# Create agent panes (press 'n' in dmux, then type prompt)
# Pane 1: "Implement the auth middleware in src/auth/"
# Pane 2: "Write tests for the user service"
# Pane 3: "Update API documentation"

# Each pane runs its own agent session
# Press 'm' to merge results back
```

## 工作流模式

### 模式 1：研究 + 實作

把研究和實作拆成兩條平行的軌道：

```
Pane 1 (Research): "Research best practices for rate limiting in Node.js.
  Check current libraries, compare approaches, and write findings to
  /tmp/rate-limit-research.md"

Pane 2 (Implement): "Implement rate limiting middleware for our Express API.
  Start with a basic token bucket, we'll refine after research completes."

# After Pane 1 completes, merge findings into Pane 2's context
```

### 模式 2：多檔案功能

把工作分散到互相獨立的檔案上平行處理：

```
Pane 1: "Create the database schema and migrations for the billing feature"
Pane 2: "Build the billing API endpoints in src/api/billing/"
Pane 3: "Create the billing dashboard UI components"

# Merge all, then do integration in main pane
```

### 模式 3：測試 + 修正循環

一個 pane 跑測試，另一個 pane 修：

```
Pane 1 (Watcher): "Run the test suite in watch mode. When tests fail,
  summarize the failures."

Pane 2 (Fixer): "Fix failing tests based on the error output from pane 1"
```

### 模式 4：跨 Harness

不同任務用不同的 AI 工具：

```
Pane 1 (Claude Code): "Review the security of the auth module"
Pane 2 (Codex): "Refactor the utility functions for performance"
Pane 3 (Claude Code): "Write E2E tests for the checkout flow"
```

### 模式 5：Code Review Pipeline

用平行的角度做 review：

```
Pane 1: "Review src/api/ for security vulnerabilities"
Pane 2: "Review src/api/ for performance issues"
Pane 3: "Review src/api/ for test coverage gaps"

# Merge all reviews into a single report
```

## 最佳實務

1. **只拆獨立任務。** 彼此輸出有依賴的任務不要平行化。
2. **邊界清楚。** 每個 pane 處理不同的檔案或關注點。
3. **有策略地 merge。** merge 前先檢查 pane 的輸出，避免衝突。
4. **用 git worktree。** 容易檔案衝突的工作，每個 pane 用獨立的 worktree。
5. **注意資源。** 每個 pane 都會耗 API token，pane 總數控制在 5 到 6 個以內。

## Git Worktree 整合

任務會動到重疊檔案時：

```bash
# Create worktrees for isolation
git worktree add -b feat/auth ../feature-auth HEAD
git worktree add -b feat/billing ../feature-billing HEAD

# Run agents in separate worktrees
# Pane 1: cd ../feature-auth && claude
# Pane 2: cd ../feature-billing && claude

# Merge branches when done
git merge feat/auth
git merge feat/billing
```

## 互補工具

| 工具 | 功能 | 何時使用 |
|------|-------------|-------------|
| **dmux** | 給 agent 用的 tmux pane 管理 | 平行 agent session |
| **Superset** | 可同時跑 10 個以上 agent 的終端機 IDE | 大規模編排 |
| **Claude Code Task tool** | 在 process 內啟動 subagent | 在單一 session 內用程式做平行 |
| **Codex multi-agent** | 內建的 agent 角色 | Codex 專屬的平行工作 |

## ECC Helper

ECC 現在附了一個 helper，用獨立的 git worktree 做外部 tmux pane 編排：

```bash
# Use the configured plugin root or standalone install (~/.claude or
# $CLAUDE_CONFIG_DIR). For a reviewed and explicitly authorized ECC checkout:
# export CLAUDE_PLUGIN_ROOT="/absolute/path/to/reviewed/ECC"
ECC_ROOT="${CLAUDE_PLUGIN_ROOT:-${CLAUDE_CONFIG_DIR:-$HOME/.claude}}"
[ -f "$ECC_ROOT/scripts/orchestrate-worktrees.js" ] || { echo "ECC scripts not found in the selected root (set CLAUDE_PLUGIN_ROOT to an authorized ECC checkout)" >&2; exit 1; }
node "$ECC_ROOT/scripts/orchestrate-worktrees.js" plan.json --execute
```

`plan.json` 範例：

```json
{
  "sessionName": "skill-audit",
  "baseRef": "HEAD",
  "launcherCommand": "codex exec --cwd {worktree_path} --task-file {task_file}",
  "workers": [
    { "name": "docs-a", "task": "Fix skills 1-4 and write handoff notes." },
    { "name": "docs-b", "task": "Fix skills 5-8 and write handoff notes." }
  ]
}
```

這個 helper 會：
- 替每個 worker 建立一個有 branch 支撐的 git worktree
- 可選擇把主 checkout 裡指定的 `seedPaths` 覆蓋進每個 worker 的 worktree
- 在 `.orchestration/<session>/` 底下為每個 worker 寫出 `task.md`、`handoff.md` 和 `status.md`
- 啟動一個 tmux session，每個 worker 一個 pane
- 在各自的 pane 裡啟動每個 worker 的指令
- 主 pane 留給 orchestrator 使用

當 worker 需要用到還沒進 `HEAD` 的未提交或未追蹤本地檔案時（例如本地的編排 script、草稿計畫或文件），就用 `seedPaths`：

```json
{
  "sessionName": "workflow-e2e",
  "seedPaths": [
    "scripts/orchestrate-worktrees.js",
    "scripts/lib/tmux-worktree-orchestrator.js",
    ".claude/plan/workflow-e2e-test.json"
  ],
  "launcherCommand": "bash {repo_root}/scripts/orchestrate-codex-worker.sh {task_file} {handoff_file} {status_file}",
  "workers": [
    { "name": "seed-check", "task": "Verify seeded files are present before starting work." }
  ]
}
```

## 疑難排解

- **Pane 沒反應：** 直接切到那個 pane，或用 `tmux capture-pane -pt <session>:0.<pane-index>` 檢查。
- **Merge 衝突：** 用 git worktree 把每個 pane 的檔案變更隔離開。
- **Token 用量太高：** 減少平行 pane 的數量。每個 pane 都是完整的 agent session。
- **找不到 tmux：** macOS 用 `brew install tmux` 安裝，Linux 用 `apt install tmux`。
