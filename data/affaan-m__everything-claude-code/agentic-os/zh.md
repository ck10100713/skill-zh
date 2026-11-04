---
name: agentic-os
description: 在 Claude Code 上建構持久的多 agent 作業系統。涵蓋 kernel 架構、專家 agent、slash command、以檔案為基礎的記憶、排程自動化，以及不靠外部資料庫的狀態管理。想在 Claude Code 上建一個有自己的記憶、指令和排程的持久多 agent 系統時使用。
metadata:
  origin: ECC
---

# Agentic OS

把 Claude Code 當成持久的 runtime / 作業系統，而不是聊天 session。這個 skill 把正式環境 agentic 設定所用的架構整理成規範：一份把任務分派給專家 agent 的 kernel 設定、持久的檔案式記憶、排程自動化，以及 JSON/markdown 資料層。

## 何時啟用

- 在 Claude Code 裡建構多 agent 工作流程
- 設定能撐過 session 重啟的持久 Claude Code 自動化
- 為重複性任務建立「個人 OS」或「agentic OS」
- 使用者說「agentic OS」「personal OS」「multi-agent」「agent coordinator」「persistent agent」
- 規劃長期進行、context 必須跨 session 保留下來的專案

## 架構概覽

Agentic OS 有四層。每一層都是專案根目錄下的一個資料夾。

```
project-root/
├── CLAUDE.md          # Kernel：身分、路由規則、agent 登錄表
├── agents/            # 專家 agent 的定義（markdown prompt）
├── .claude/commands/  # Slash command：面向使用者的 CLI
├── scripts/           # Daemon script：排程或事件驅動的任務
└── data/              # 狀態：JSON/markdown 檔案系統，不用外部 DB
```

### 各層的職責

| 層 | 用途 | 持久化方式 |
|---|---|---|
| Kernel（`CLAUDE.md`） | 身分、路由、模型政策、agent 登錄表 | 由 Git 追蹤 |
| Agents（`agents/`） | 有限定工具和記憶範圍的專家身分 | 由 Git 追蹤 |
| Commands（`.claude/commands/`） | 面向使用者的 slash command（`/daily-sync`、`/outreach`） | 由 Git 追蹤 |
| Scripts（`scripts/`） | 由 cron 或 webhook 觸發的 Python/JS daemon | 由 Git 追蹤 |
| State（`data/`） | 只增不減的 log、專案狀態、決策紀錄 | Git 忽略或追蹤 |

## Kernel

`CLAUDE.md` 就是 kernel。它扮演 COO / orchestrator 的角色。Claude 在 session 開始時讀它，並用它來分派工作。

### Kernel 結構

```markdown
# CLAUDE.md - Agentic OS Kernel

## Identity
你是 [project-name] 的 COO。你負責把任務分派給專家 agent。
你絕對不直接寫程式。你把工作委派給對的 agent，再綜合結果。

## Agent Registry

| Agent | Role | Trigger |
|---|---|---|
| @dev | 程式碼、架構、除錯 | 使用者說 "build"、"fix"、"refactor" |
| @writer | 文件、內容、電子郵件 | 使用者說 "write"、"draft"、"blog" |
| @researcher | 研究、分析、事實查核 | 使用者說 "research"、"analyze"、"compare" |
| @ops | DevOps、部署、基礎設施 | 使用者說 "deploy"、"CI"、"server" |

## Routing Rules
1. 解析使用者請求中的意圖關鍵字
2. 對照 Agent Registry 的 trigger 欄
3. 從 `agents/<name>.md` 載入對應的 agent 檔案
4. 帶著完整 context 交接執行
5. 綜合結果，呈現給使用者

## Model Policies
- 預設模型：用 repo 或 harness 的預設值。
- @dev 任務：複雜的架構優先用推理能力較強的模型。
- @researcher 任務：用設定好、具研究能力的模型，以及核准的搜尋工具。
- 成本上限：超過專案設定的花費門檻之前先警告。
```

### 關鍵原則

Kernel 應該**小而宣告式**。路由邏輯寫在純 markdown 表格裡，不寫在程式碼裡。這讓系統不用 debug 就能檢視和修改。

## 專家 Agent

每個 agent 都是 `agents/` 裡獨立的 markdown 檔案。Claude 分派任務時，會載入相關的 agent 檔案。

### Agent 定義格式

```markdown
# @dev - Software Engineer

## Identity
你是資深軟體工程師。你寫乾淨、有測試、達正式環境水準的程式碼。
你偏好簡單的解法。需求模糊的時候，你會提出釐清問題。

## Memory Scope
- 讀 `data/projects/<current-project>.md` 取得 context
- 讀 `data/decisions/` 取得架構決策
- 把執行 log 附加到 `data/logs/<date>-@dev.md`

## Tool Access
- 專案根目錄內的完整檔案系統存取
- Git 操作（status、diff、commit、branch）
- 測試執行器存取
- `.claude/mcp.json` 裡設定的 MCP server

## Constraints
- 新功能一定要寫測試
- 絕對不直接 commit 到 `main`；用 feature branch
- 優先修改既有檔案，不要新建檔案
- 盡可能讓函式維持在 50 行以內
```

### 多 Agent 協作模式

任務橫跨多個 agent 時，kernel 會依序或平行地執行它們：

```
User: "Build a landing page and write the launch blog post"

Kernel routing:
1. @dev - "Build a landing page with [requirements]"
2. @writer - "Write a launch blog post for [product] using the landing page copy"
3. Kernel 把兩份輸出綜合成一個統一的回應
```

要平行執行，可以用 Claude Code 的背景任務功能，或用 shell script 帶著特定的 agent context 去呼叫 Claude Code。

## Command 與每日工作流程

Slash command 是 `.claude/commands/` 裡的 markdown 檔案。它們定義可重複使用的工作流程。

### Command 結構

```markdown
# /daily-sync

執行早晨簡報：

1. 讀 `data/logs/last-sync.md` 取得 context
2. 檢查專案狀態：`git status`、待處理的 PR、CI 健康狀況
3. 檢視 `data/inbox/` 裡有沒有新任務或需要做的決定
4. 產生阻礙、優先順序和下一步動作的摘要
5. 把簡報附加到 `data/logs/daily/<date>.md`
```

### 標準 Command 組合

| Command | 用途 |
|---|---|
| `/daily-sync` | 早晨簡報：狀態、阻礙、優先順序 |
| `/outreach` | 執行開發信流程（電子郵件、LinkedIn 等） |
| `/research <topic>` | 附引用追蹤的深入研究 |
| `/apply-jobs` | 針對目標職位調整履歷和求職信 |
| `/analytics` | 從 Stripe、GitHub 或自訂來源取得指標 |
| `/interview-prep` | 產生字卡或模擬面試題 |
| `/decision <topic>` | 記錄一個決策，含優缺點和選定的路線 |

### 啟用 Command

把 command 檔案放在 `.claude/commands/<command-name>.md`。Claude Code 會自動發現它們。使用者用 `/<command-name>` 來呼叫。

## 持久記憶

記憶是以檔案為基礎的。沒有向量資料庫、沒有 Redis、沒有 PostgreSQL。`data/` 裡的 JSON 和 markdown 檔案就是資料庫。

### 記憶目錄結構

```
data/
├── daily-logs/         # 只增不減的每日活動 log
├── projects/           # 每個專案的 context 檔案
├── decisions/          # 架構和商業決策（ADR 格式）
├── inbox/              # 等著分流的新任務或想法
├── contacts/           # 人、公司、關係筆記
└── templates/          # 可重複使用的 prompt 和格式
```

### 每日 Log 格式

```markdown
# 2026-04-22 - Daily Log

## Sessions
- 09:00 - Session 1：重構 auth 模組（@dev）
- 11:30 - Session 2：起草投資人更新（@writer）

## Decisions
- 從 JWT 改成 session cookie（見 `data/decisions/2026-04-22-auth.md`）

## Blockers
- 等廠商給 API key（2026-04-24 追蹤）

## Next Actions
- [ ] Merge auth 重構的 PR
- [ ] 送出投資人更新給人 review
```

### 自動反思模式

每個 session 結束時，kernel 會附加一段反思：

```markdown
## Reflection - Session 3
- 有效的：平行執行 agent 省了 20 分鐘
- 無效的：@researcher 碰到付費牆的來源，需要更好的來源排序
- 要改的：在研究筆記加上 `source-tier` 欄位（A/B/C 可信度）
```

這會形成一個回饋迴圈，不用改程式碼就能讓系統隨時間變好。

## 排程自動化

Agentic OS 的任務用外部 cron 排程執行，不用 Claude Code 內建的 cron（session 結束它就掛了）。

### macOS：LaunchAgent

```xml
<!-- ~/Library/LaunchAgents/com.agentic.daily-sync.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" ...>
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.agentic.daily-sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>/claude</string>
        <string>--cwd</string>
        <string>/path/to/project</string>
        <string>--command</string>
        <string>/daily-sync</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/agentic-daily-sync.log</string>
</dict>
</plist>
```

### Linux：systemd Timer

```ini
# ~/.config/systemd/user/agentic-daily-sync.service
[Unit]
Description=Agentic OS Daily Sync

[Service]
Type=oneshot
ExecStart=/usr/local/bin/claude --cwd /path/to/project --command /daily-sync
```

```ini
# ~/.config/systemd/user/agentic-daily-sync.timer
[Unit]
Description=Run daily sync every morning

[Timer]
OnCalendar=*-*-* 8:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

### 跨平台：pm2

```bash
# ecosystem.config.js
module.exports = {
  apps: [{
    name: 'agentic-daily-sync',
    script: 'claude',
    args: '--cwd /path/to/project --command /daily-sync',
    cron_restart: '0 8 * * *',
    autorestart: false
  }]
};
```

## 資料層

資料層就是你的檔案系統。結構化資料用 JSON，敘述性內容用 markdown。

### 結構化狀態用 JSON

```json
// data/projects/website-v2.json
{
  "name": "Website v2",
  "status": "in-progress",
  "milestone": "beta-launch",
  "agents_involved": ["@dev", "@writer"],
  "files": {
    "spec": "docs/website-v2-spec.md",
    "design": "designs/website-v2.fig"
  },
  "metrics": {
    "commits": 47,
    "last_session": "2026-04-22T11:30:00Z"
  }
}
```

### 敘述性內容用 Markdown

凡是給人看的東西都用 markdown：決策、log、研究筆記、聯絡人紀錄。

### Schema 演進

絕對不要重新命名既有欄位。新增欄位，並把舊的標成已棄用：

```json
{
  "name": "Website v2",
  "status": "in-progress",
  "milestone": "beta-launch",
  "_deprecated_priority": "high",
  "priority_v2": { "level": "high", "rationale": "Blocks investor demo" }
}
```

這樣不用 migration script，歷史資料也能保持可讀。

## 反面模式

### 單體式的單一 Agent

```markdown
# BAD - 一個 agent 包辦所有事
你是全端開發者、作家、研究員，也是 DevOps 工程師。
```

拆成專家 agent。路由交給 kernel 處理。

### 無狀態的 Session

```markdown
# BAD - session 之間沒有記憶
每次 Claude Code 開啟都從頭開始。
```

一定要在 session 開始時讀 `data/`，結束時寫回去。

### 寫死的憑證

```markdown
# BAD - API key 放在 agent 檔案或 CLAUDE.md 裡
你的 OpenAI API key 是 sk-xxxxxxxx
```

用環境變數，或由 script 載入的 `.env` 檔案。Agent 參照 `process.env.API_KEY`。

### 簡單狀態卻用外部資料庫

```markdown
# BAD - 單人使用者的 agentic OS 卻用 PostgreSQL
```

在有多個並行使用者或好幾 GB 的資料之前，都用 JSON/markdown 檔案。

### 過度設計的路由

```markdown
# BAD - 路由邏輯寫在程式碼裡，不是 markdown 表格
if (intent.includes('deploy')) { agent = opsAgent; }
```

路由要宣告式地寫在 `CLAUDE.md` 的 markdown 表格裡。這樣可檢視、可修改、可 debug。

## 最佳實務

- [ ] `CLAUDE.md` 在 200 行以內，能放進 context window
- [ ] 每個 agent 檔案在 100 行以內，專注單一領域
- [ ] 敏感的 log 在 `data/` 裡用 git 忽略，決策和規格用 git 追蹤
- [ ] Command 用祈使句命名：`/daily-sync`，不是 `/run-daily-sync`
- [ ] Log 只增不減；絕對不要修改過去的每日 log
- [ ] 每個 agent 都有 `Memory Scope` 段落，定義它讀哪些檔案
- [ ] 每個 session 結束時都寫反思
- [ ] 排程任務用外部 cron（LaunchAgent、systemd、pm2），不用 Claude Code 的 session cron
- [ ] 成本追蹤：把每個 session 的 API 花費記在 `data/logs/<date>-costs.json`
- [ ] 一個專案 = 一個 Agentic OS。不要讓不相關的專案共用同一份 `CLAUDE.md`。
