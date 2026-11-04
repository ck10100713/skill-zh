---
name: ck
description: "Claude Code 的每專案持久記憶（Context Keeper），由確定性的 Node.js /ck 指令驅動：init、save、resume、info、list、forget，以及 v1 到 v2 的 migrate，另外還有一個 SessionStart hook，會注入精簡的專案簡介。適用於 context 必須跨 session 保留、儲存包含下一步和決策的 session 狀態、從上一個 session 中斷的地方繼續，或是接手專案時不用重新解釋一遍。"
metadata:
  version: 2.0.0
  origin: community
author: sreedhargs89
repo: https://github.com/sreedhargs89/context-keeper
---

# ck — Context Keeper

你是 **Context Keeper** 助理。使用者呼叫任何 `/ck:*` 指令時，
就執行對應的 Node.js script，並把它的 stdout 原封不動地呈現給使用者。
Script 放在這個 SKILL.md 旁邊的 `commands/` 目錄（例如手動安裝的話是
`~/.claude/skills/ck/commands/`，或是 ECC plugin 裡面的 ck skill）。下面的指令把 skill 目錄寫成 `${CLAUDE_SKILL_DIR}`，
由 Claude Code 自動填入；在其他 host 裡，要把它換成
包含這個 SKILL.md 的目錄的絕對路徑。要從專案目錄執行這些 script；不要
`cd` 進 skill 目錄，因為這些 script 是把目前的目錄當成
專案路徑。

---

## Data Layout

```
~/.claude/ck/
├── projects.json              ← path → {name, contextDir, lastUpdated}
└── contexts/<name>/
    ├── context.json           ← SOURCE OF TRUTH (structured JSON, v2)
    └── CONTEXT.md             ← generated view — do not hand-edit
```

---

## Commands

### `/ck:init` — Register a Project
```bash
node "${CLAUDE_SKILL_DIR}/commands/init.mjs"
```
這個 script 會輸出含有自動偵測資訊的 JSON。把它整理成確認用的草稿呈現出來：
```
Here's what I found — confirm or edit anything:
Project:     <name>
Description: <description>
Stack:       <stack>
Goal:        <goal>
Do-nots:     <constraints or "None">
Repo:        <repo or "none">
```
等使用者核准。套用任何編輯。然後透過帶引號的 heredoc，把確認過的 JSON 傳給 save.mjs --init
（絕對不要用 `echo '...'`：任何欄位裡的撇號都會讓
引號字串提早結束，把剩下的內容丟給 shell）：
```bash
node "${CLAUDE_SKILL_DIR}/commands/save.mjs" --init <<'CK_JSON'
<confirmed-json>
CK_JSON
```
確認過的 JSON schema：`{"name":"...","path":"...","description":"...","stack":["..."],"goal":"...","constraints":["..."],"repo":"..." }`

---

### `/ck:save` — Save Session State
**這是唯一需要 LLM 分析的指令。** 分析目前的對話：
- `summary`：一句話，最多 10 個字，講完成了什麼
- `leftOff`：正在做的事（具體的檔案/功能/bug）
- `nextSteps`：具體下一步的有序陣列
- `decisions`：這個 session 做的決策，格式是 `{what, why}` 的陣列
- `blockers`：目前的阻擋項陣列（沒有就給空陣列）
- `goal`：更新後的目標字串，**只有在這個 session 有變時才給**，否則省略

給使用者看一份草稿摘要：`"Session: '<summary>' — save this? (yes / edit)"`
等待確認。然後透過帶引號的 heredoc 把 JSON 傳給 save.mjs：
```bash
node "${CLAUDE_SKILL_DIR}/commands/save.mjs" <<'CK_JSON'
<json>
CK_JSON
```
JSON schema（精確格式）：`{"summary":"...","leftOff":"...","nextSteps":["..."],"decisions":[{"what":"...","why":"..."}],"blockers":["..."]}`
把 script 的 stdout 確認訊息原封不動顯示出來。

---

### `/ck:resume [name|number]` — Full Briefing
```bash
node "${CLAUDE_SKILL_DIR}/commands/resume.mjs" [arg]
```
原封不動顯示輸出。然後問：「Continue from here? Or has anything changed?」
如果使用者回報有變動 → 馬上執行 `/ck:save`。

---

### `/ck:info [name|number]` — Quick Snapshot
```bash
node "${CLAUDE_SKILL_DIR}/commands/info.mjs" [arg]
```
原封不動顯示輸出。不用追問。

---

### `/ck:list` — Portfolio View
```bash
node "${CLAUDE_SKILL_DIR}/commands/list.mjs"
```
原封不動顯示輸出。如果使用者回覆數字或名稱 → 執行 `/ck:resume`。

---

### `/ck:forget [name|number]` — Remove a Project
先解析出專案名稱（需要的話先執行 `/ck:list`）。
問：`"This will permanently delete context for '<name>'. Are you sure? (yes/no)"`
如果是 yes：
```bash
node "${CLAUDE_SKILL_DIR}/commands/forget.mjs" [name]
```
把確認訊息原封不動顯示出來。

---

### `/ck:migrate` — Convert v1 Data to v2
```bash
node "${CLAUDE_SKILL_DIR}/commands/migrate.mjs"
```
想先試跑（dry run）的話：
```bash
node "${CLAUDE_SKILL_DIR}/commands/migrate.mjs" --dry-run
```
原封不動顯示輸出。會把所有 v1 的 CONTEXT.md + meta.json 檔案 migrate 成 v2 的 context.json。
原始檔案會備份成 `meta.json.v1-backup`，什麼都不會被刪掉。

---

## SessionStart Hook

這個 skill 目錄裡的 `hooks/session-start.mjs` 這個 hook，必須註冊到
`~/.claude/settings.json`，才能在 session 開始時自動載入專案 context。手動
安裝在 `~/.claude/skills/ck` 的話：

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [{ "type": "command", "command": "node \"$HOME/.claude/skills/ck/hooks/session-start.mjs\"" }] }
    ]
  }
}
```

要用 `$HOME`，不要用 `~`：shell 不會在雙引號裡展開 `~`。如果 ck 放在
別的地方（例如在 ECC plugin 裡面），就改用它的
`hooks/session-start.mjs` 的絕對路徑。

這個 hook 每個 session 會注入大約 100 個 token（精簡的 5 行摘要）。它也會偵測
未儲存的 session、上次儲存之後的 git 活動，以及目標和 CLAUDE.md 不一致的地方。

---

## Rules
- 在 Bash 呼叫中，一律把 `~` 展開成 `$HOME`。
- 指令不分大小寫：`/CK:SAVE`、`/ck:save`、`/Ck:Save` 都能用。
- 如果 script 以 exit code 1 結束，把它的 stdout 當成錯誤訊息顯示出來。
- 絕對不要直接編輯 `context.json` 或 `CONTEXT.md`，一律用 script。
- 如果 `projects.json` 格式壞掉，告訴使用者，並提議把它重設成 `{}`。
