---
name: claude-devfleet
description: 透過 Claude DevFleet 編排多 agent 的寫程式任務：規劃專案、在隔離的 worktree 裡平行派出 agent、監控進度，並讀取結構化的報告。適用於跨隔離 worktree 平行派出寫程式 agent、並追蹤它們的報告。
metadata:
  origin: community
---

# Claude DevFleet Multi-Agent Orchestration

## When to Use

需要派出多個 Claude Code agent 平行處理寫程式任務時，用這個 skill。每個 agent 都在隔離的 git worktree 裡執行，工具齊全。

## Setup

DevFleet 伺服器是獨立的專案，不包含在 ECC 裡。請先從它的 repository 安裝並
執行：<https://github.com/LEC-AI/claude-devfleet>

接著透過 MCP 連接正在執行的實例：
```bash
claude mcp add devfleet --transport http http://localhost:18801/mcp
```

第一次使用之前，先確認監聽 18801 port 的 process 是你安裝的 DevFleet
執行檔（參考 SECURITY.md 中關於 localhost MCP 伺服器的說明）。

## How It Works

```
User → "Build a REST API with auth and tests"
  ↓
plan_project(prompt) → project_id + mission DAG
  ↓
Show plan to user → get approval
  ↓
dispatch_mission(M1) → Agent 1 spawns in worktree
  ↓
M1 completes → auto-merge → auto-dispatch M2 (depends_on M1)
  ↓
M2 completes → auto-merge
  ↓
get_report(M2) → files_changed, what_done, errors, next_steps
  ↓
Report back to user
```

### Tools

| Tool | Purpose |
|------|---------|
| `plan_project(prompt)` | AI 把一段描述拆成一個專案，裡面有串接起來的 mission |
| `create_project(name, path?, description?)` | 手動建立專案，回傳 `project_id` |
| `create_mission(project_id, title, prompt, depends_on?, auto_dispatch?)` | 新增 mission。`depends_on` 是 mission ID 字串的清單（例如 `["abc-123"]`）。設 `auto_dispatch=true` 的話，依賴滿足時會自動開始。 |
| `dispatch_mission(mission_id, model?, max_turns?)` | 在某個 mission 上啟動 agent |
| `cancel_mission(mission_id)` | 停止執行中的 agent |
| `wait_for_mission(mission_id, timeout_seconds?)` | 阻塞直到 mission 完成（見下方說明） |
| `get_mission_status(mission_id)` | 不阻塞地查看 mission 進度 |
| `get_report(mission_id)` | 讀取結構化報告（改了哪些檔案、測了什麼、錯誤、下一步） |
| `get_dashboard()` | 系統總覽：執行中的 agent、統計、最近的活動 |
| `list_projects()` | 瀏覽所有專案 |
| `list_missions(project_id, status?)` | 列出專案中的 mission |

> **關於 `wait_for_mission` 的說明：** 它最多會阻塞對話 `timeout_seconds`（預設 600）。對於長時間執行的 mission，建議改成每 30–60 秒用 `get_mission_status` 輪詢，這樣使用者才看得到進度更新。

### Workflow: Plan → Dispatch → Monitor → Report

1. **Plan**：呼叫 `plan_project(prompt="...")`，回傳 `project_id` 和一份 mission 清單，裡面有 `depends_on` 的串接關係，而且都是 `auto_dispatch=true`。
2. **Show plan**：把 mission 的標題、類型和依賴鏈呈現給使用者。
3. **Dispatch**：對根 mission（`depends_on` 是空的）呼叫 `dispatch_mission(mission_id=<first_mission_id>)`。其餘 mission 會在依賴完成時自動派出（因為 `plan_project` 對它們設了 `auto_dispatch=true`）。
4. **Monitor**：呼叫 `get_mission_status(mission_id=...)` 或 `get_dashboard()` 查看進度。
5. **Report**：mission 完成後呼叫 `get_report(mission_id=...)`。把重點分享給使用者。

### Concurrency

DevFleet 預設最多同時跑 3 個 agent（可用 `DEVFLEET_MAX_AGENTS` 設定）。所有名額都滿了的時候，`auto_dispatch=true` 的 mission 會在 mission watcher 裡排隊，名額空出來就自動派出。用 `get_dashboard()` 查看目前的名額使用情況。

## Examples

### Full auto: plan and launch

1. `plan_project(prompt="...")`，顯示包含 mission 和依賴關係的計畫。
2. 派出第一個 mission（`depends_on` 是空的那個）。
3. 其餘 mission 在依賴解決時自動派出（它們有 `auto_dispatch=true`）。
4. 回報專案 ID 和 mission 數量，讓使用者知道啟動了什麼。
5. 定期用 `get_mission_status` 或 `get_dashboard()` 輪詢，直到所有 mission 都進入終止狀態（`completed`、`failed` 或 `cancelled`）。
6. 對每個終止的 mission 呼叫 `get_report(mission_id=...)`，摘要成功的部分，並點出失敗的項目，附上錯誤和下一步。

### Manual: step-by-step control

1. `create_project(name="My Project")`，回傳 `project_id`。
2. 為第一個（根）mission 呼叫 `create_mission(project_id=project_id, title="...", prompt="...", auto_dispatch=true)`，記下 `root_mission_id`。
   之後的每個任務呼叫 `create_mission(project_id=project_id, title="...", prompt="...", auto_dispatch=true, depends_on=["<root_mission_id>"])`。
3. 對第一個 mission 呼叫 `dispatch_mission(mission_id=...)` 來啟動這條鏈。
4. 完成後呼叫 `get_report(mission_id=...)`。

### Sequential with review

1. `create_project(name="...")`，取得 `project_id`。
2. `create_mission(project_id=project_id, title="Implement feature", prompt="...")`，取得 `impl_mission_id`。
3. `dispatch_mission(mission_id=impl_mission_id)`，然後用 `get_mission_status` 輪詢直到完成。
4. `get_report(mission_id=impl_mission_id)` 檢視結果。
5. `create_mission(project_id=project_id, title="Review", prompt="...", depends_on=[impl_mission_id], auto_dispatch=true)`，因為依賴已經滿足，會自動啟動。

## Guidelines

- 派出之前，一定要先跟使用者確認計畫，除非他們說了直接做。
- 回報狀態時，要附上 mission 的標題和 ID。
- 如果 mission 失敗，重試之前先讀它的報告。
- 大量派出之前，先用 `get_dashboard()` 確認 agent 還有名額。
- Mission 的依賴關係構成一個 DAG，不要建立循環依賴。
- 每個 agent 都在隔離的 git worktree 裡執行，完成時會自動 merge。如果發生 merge 衝突，變更會留在 agent 的 worktree branch 上，等人工解決。
- 手動建立 mission 時，如果想讓它們在依賴完成時自動觸發，一定要設 `auto_dispatch=true`。沒設這個 flag 的話，mission 會停在 `draft` 狀態。
