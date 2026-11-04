---
name: autonomous-agent-harness
description: 把 Claude Code 變成完全自主的 agent 系統，具備持久記憶、排程操作、computer use 和任務佇列。利用 Claude Code 原生的 cron、dispatch、MCP 工具和記憶，取代獨立的 agent 框架（Hermes、AutoGPT）。使用者想要持續的自主運作、排程任務，或自我導向的 agent 迴圈時使用。
metadata:
  origin: ECC
---

# Autonomous Agent Harness

把 Claude Code 的 session 工具，跟另外設定的排程、記憶和 computer-use 整合組合起來。這是一種設定模式，不是內建的、常駐運作的 runtime。

## 同意與安全邊界

自主運作必須由使用者明確要求，並界定範圍。除非使用者已核准該能力和目前設定的目標工作區，否則不要建立排程、派送遠端 agent、寫入持久記憶、使用電腦控制、對外發文、修改第三方資源，或對私人通訊採取行動。

在啟用週期性或事件驅動的動作之前，優先使用 dry-run 計畫和本機佇列檔案。憑證、私人工作區匯出檔、個人資料集和特定帳號的自動化，不要放進可重複使用的 ECC 成品裡。

## 何時啟用

- 使用者想要持續執行或依排程執行的 agent
- 設定定期觸發的自動化工作流程
- 建構能跨 session 記住 context 的個人 AI 助理
- 使用者說「每天跑這個」「定期檢查這個」「持續監控」
- 想複製 Hermes、AutoGPT 或類似自主 agent 框架的功能
- 需要把 computer use 跟排程執行結合

## 架構

```
┌──────────────────────────────────────────────────────────────┐
│                    Claude Code Runtime                        │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐ │
│  │  Crons   │  │ Dispatch │  │ Memory   │  │ Computer    │ │
│  │ Schedule │  │ Remote   │  │ Store    │  │ Use         │ │
│  │ Tasks    │  │ Agents   │  │          │  │             │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬──────┘ │
│       │              │             │                │        │
│       ▼              ▼             ▼                ▼        │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              ECC Skill + Agent Layer                  │    │
│  │                                                      │    │
│  │  skills/     agents/     commands/     hooks/        │    │
│  └──────────────────────────────────────────────────────┘    │
│       │              │             │                │        │
│       ▼              ▼             ▼                ▼        │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              MCP Server Layer                        │    │
│  │                                                      │    │
│  │  memory    github    exa    supabase    browser-use  │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

## 核心元件

### 1. 持久記憶

使用 Claude Code 內建的記憶系統，並用 MCP memory server 強化結構化資料。

**內建記憶**（`~/.claude/projects/*/memory/`）：
- 使用者偏好、回饋、專案 context
- 以帶有 frontmatter 的 markdown 檔案儲存
- session 開始時自動載入

**MCP memory server**（結構化的知識圖譜）：
- 實體、關係、觀察
- 可查詢的圖譜結構
- 跨 session 的持久化

**記憶模式：**

```
# 短期：目前 session 的 context
用 TodoWrite 追蹤 session 內的任務

# 中期：專案記憶檔案
寫到 ~/.claude/projects/*/memory/，供跨 session 回想

# 長期：MCP 知識圖譜
用 mcp__memory__create_entities 存永久的結構化資料
用 mcp__memory__create_relations 做關係對應
用 mcp__memory__add_observations 記錄已知實體的新事實
```

### 2. 排程操作（Cron）

用 Claude Code 原生的[排程任務](https://code.claude.com/docs/en/scheduled-tasks)，在互動式 session 裡執行週期性的 prompt。這些任務的範圍限於 session；需要獨立於已開啟 session 運作的工作，要用外部排程器。`/loop` 不需要排程用的 MCP server。

**設定 cron：**

```
# 在互動式的 Claude Code session 裡
/loop 30m Review open PRs in this repository and summarize CI failures.
```

要從 shell 一次性執行，先設定工作目錄再呼叫 CLI：

```bash
cd "/path/to/repo" && claude -p "Review open PRs and summarize"
```

沒有互動式 session 在跑的時候，用 OS 排程器或 CI 排程重複呼叫那個指令。另外設定 runner 的驗證和工具權限。

**實用的 cron 模式：**

| 模式 | 排程 | 使用情境 |
|---------|----------|----------|
| 每日 standup | `0 9 * * 1-5` | 檢視 PR、issue、部署狀態 |
| 每週回顧 | `0 10 * * 1` | 程式碼品質指標、測試覆蓋率 |
| 每小時監控 | `0 * * * *` | 正式環境健康狀況、錯誤率檢查 |
| 夜間 build | `0 2 * * *` | 跑完整的測試套件、安全掃描 |
| 會議前 | `*/30 * * * *` | 為即將到來的會議準備 context |

### 3. Dispatch / 遠端 Agent

讓已驗證身分的 CI job 或 webhook 接收端，在它自己擁有的工作區裡呼叫 Claude Code。支援的進入點是[程式化 CLI 模式](https://code.claude.com/docs/en/headless)，不是 Anthropic 的公開 dispatch endpoint。

**Dispatch 模式：**

```bash
# 在 CI 工作區內執行
cd "/path/to/repo" && claude -p "Build failed on main. Diagnose the failure."

# 從 webhook 觸發
# GitHub webhook -> authenticated CI runner -> claude -p -> reviewable result

# 從另一個 agent 觸發
claude -p "Analyze the output of the security scan and create issues for findings"
```

### 4. Computer Use

電腦控制需要另外設定的整合。Anthropic 的 [computer-use 工具和參考環境](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)，需要有應用程式在隔離的桌面環境裡執行工具呼叫。加上一個 MCP 套件名稱，並不會提供那個環境。

**能力：**
- 瀏覽器自動化（導覽、點擊、填表單、截圖）
- 桌面控制（開啟 app、打字、滑鼠控制）
- CLI 之外的檔案系統操作

**在 harness 裡的使用情境：**
- web UI 的自動化測試
- 填表單和資料輸入
- 以截圖為基礎的監控
- 跨多個 app 的工作流程

### 5. 任務佇列

管理能跨越 session 邊界的持久任務佇列。

**實作：**

```
# 透過記憶持久化任務
把任務佇列寫到 ~/.claude/projects/*/memory/task-queue.md

# 任務格式
---
name: task-queue
type: project
description: Persistent task queue for autonomous operation
---

## Active Tasks
- [ ] PR #123: Review and approve if CI green
- [ ] Monitor deploy: check /health every 30 min for 2 hours
- [ ] Research: Find 5 leads in AI tooling space

## Completed
- [x] Daily standup: reviewed 3 PRs, 2 issues
```

## 取代 Hermes

| Hermes 元件 | ECC 對應 | 做法 |
|------------------|---------------|-----|
| Gateway/Router | CLI + 外部排程器 | 由已驗證身分的 runner 啟動 agent session |
| Memory System | Claude 記憶 + MCP memory server | 內建持久化 + 知識圖譜 |
| Tool Registry | MCP server | 動態載入的工具提供者 |
| Orchestration | ECC skill + agent | 由 skill 定義引導 agent 行為 |
| Computer Use | 另外設定的整合 | 在隔離環境裡控制瀏覽器或桌面 |
| Context Manager | Session 管理 + 記憶 | ECC 2.0 的 session 生命週期 |
| Task Queue | 以記憶持久化的任務清單 | TodoWrite + 記憶檔案 |

## 設定指南

### 步驟 1：設定 MCP Server

Memory MCP 是選用的。[MCP 參考版 memory server](https://github.com/modelcontextprotocol/servers/tree/main/src/memory) 以 `@modelcontextprotocol/server-memory` 發布；`2026.8.31` 版已於 2026-09-07 在公開的 npm registry 上驗證過。它是參考實作，不是 ECC 內建的服務。

在審查過那個套件並核准使用之後，把這個項目合併進 `~/.claude.json` 裡使用者範圍的 MCP 設定，並保留既有的設定。把 `MEMORY_FILE_PATH` 換成你自己擁有的私有目錄裡的絕對路徑。CLI 註冊和 Windows 的 `cmd /c npx` 設定，請看 [Claude Code MCP 設定](https://code.claude.com/docs/en/mcp)。

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory@2026.8.31"],
      "env": {
        "MEMORY_FILE_PATH": "/absolute/path/to/private/memory.jsonl"
      }
    }
  }
}
```

不要註冊猜出來的或沒發布的 npm 套件：`npx -y` 會執行之後任何發布在那個名稱底下的東西。新增其他 server 之前，要先驗證確切的套件、發布者和版本。排程和 computer use 並不需要這裡先前列出的那三個未發布的套件名稱。

### 步驟 2：建立基本的 Cron

要在互動式 session 期間輪詢，輸入：

```text
/loop 30m Review open PRs in this repository and summarize CI failures.
```

需要在 session 關掉之後仍然運作的每日或每週工作，要設定外部排程器（例如 OS cron job 或 GitHub Actions），去執行核心元件步驟 2 的一次性指令。呼叫 `claude -p` 要求建立排程，並不會佈建一個常駐的排程器。啟用之前，要明確選好排程、工作區和允許的動作。

### 步驟 3：初始化記憶圖譜

```bash
# 建立你的身分和 context 的初始資料
claude -p "Create memory entities for: me (user profile), my projects, my key contacts. Add observations about current priorities."
```

### 步驟 4：啟用 Computer Use（選用）

依照上面連結的 computer-use 參考環境，或你審查過的特定瀏覽器整合的文件操作。只授予必要的權限，並在加進排程的工作流程之前，先在隔離環境裡驗證一個無害的動作。

## 範例工作流程

### 自主 PR Reviewer
```
Cron: every 30 min during work hours
1. Check for new PRs on watched repos
2. For each new PR:
   - Pull branch locally
   - Run tests
   - Review changes with code-reviewer agent
   - Post review comments via GitHub MCP
3. Update memory with review status
```

### 個人研究 Agent
```
Cron: daily at 6 AM
1. Check saved search queries in memory
2. Run Exa searches for each query
3. Summarize new findings
4. Compare against yesterday's results
5. Write digest to memory
6. Flag high-priority items for morning review
```

### 會議準備 Agent
```
Trigger: 30 min before each calendar event
1. Read calendar event details
2. Search memory for context on attendees
3. Pull recent email/Slack threads with attendees
4. Prepare talking points and agenda suggestions
5. Write prep doc to memory
```

## 限制

- 原生的排程 prompt 與它所在的互動式 session 共用資源。外部排程器的呼叫會開啟獨立的 session，除非明確要求 resume。
- Computer use 需要明確的權限授予。不要假設有存取權。
- CLI 自動化仍然會消耗模型用量，並受所設定的 provider 的限制。請選擇適當的排程間隔。
- 記憶檔案要保持精簡。把舊資料封存起來，不要讓檔案無限成長。
- 一定要確認排程任務有成功完成。在 cron 的 prompt 裡加上錯誤處理。
