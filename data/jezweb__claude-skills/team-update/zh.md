---
name: team-update
description: "把專案進度更新貼到團隊聊天室、收集回饋、分類處理回應，並規劃下一步。會依可用的工具（聊天、git、issue、任務）調整做法。第一次執行會探索工具並存下 playbook，之後直接照 playbook 執行。觸發詞：'team update'、'post update'、'sync with team'、'standup'、'check team chat'、'feedback loop'、'project update'、'what did the team say'。"
compatibility: claude-code-only
allowed-tools: "*"
---

# Team Update

把專案進度更新貼到團隊聊天室，讀取並分類回饋，再規劃下一步。會配合手邊有的溝通和專案工具來調整。

## Playbook 模式

這個 skill 在專案根目錄用一個 **playbook** 檔案：`.claude/team-update-playbook.md`。

- **第一次執行**：探索可用工具、詢問使用者偏好、執行、存下 playbook
- **之後的執行**：讀 playbook，跳過探索，直接執行
- **使用者編輯 playbook**：改動立刻生效（頻道、風格、分類規則）

Playbook 是使用者可以自己編輯的純 markdown。裡面記錄工具設定、頻道偏好、訊息風格、分類規則，以及上次執行的 metadata。

---

## Phase 0：檢查 Playbook

檢查專案根目錄有沒有 `.claude/team-update-playbook.md`。

**如果存在**：讀它。所有工具設定、頻道資訊、訊息風格和分類規則都在裡面。帶著已知的設定直接跳到 Phase 1。

**如果不存在**：先執行 Phase 0b（探索）。

---

## Phase 0b：探索（只在第一次執行）

檢查有哪些 MCP 工具已連線、本機有哪些工具，偵測可用的能力。

讀 [references/discovery-patterns.md](references/discovery-patterns.md) 看偵測模式。

### 能力偵測

逐一檢查每個能力類別：

| 能力 | 怎麼偵測 | 缺少時的替代方案 |
|---|---|---|
| **Chat** | 名稱符合 `chat`、`slack`、`discord`、`teams` 的 MCP 工具 | 輸出排好版的文字，讓使用者手動貼 |
| **Git** | `git rev-parse --is-inside-work-tree` | 跳過 commit 摘要 |
| **Issues** | 名稱符合 `github`、`linear`、`jira` 的 MCP 工具 | 跳過，或輸出文字清單 |
| **Tasks** | 名稱符合 `tasks`、`todos`、`asana` 的 MCP 工具 | 跳過，或輸出文字清單 |
| **Knowledge** | Basalt Cortex（`~/Documents/basalt-cortex/`） | 搜尋相關的知識筆記 |

### 使用者偏好（詢問）

探索完之後，請使用者確認：

1. **頻道**：要把更新貼到哪個聊天空間/頻道？（列出探索到的選項）
2. **身分**：用自己的身分貼，還是用 bot 身分？（例如 Anthro Morphic）
3. **Repo 範圍**：要追蹤哪些 repo？（預設：目前這個 repo）
4. **訊息風格**：簡短的 standup、詳細的 changelog，還是對話式更新？
5. **團隊背景**：有需要特別留意的成員嗎？（姓名、角色）
6. **分類規則**：處理回饋有沒有自訂規則？（或用預設的）

### 儲存 Playbook

探索加上使用者偏好都有了之後，把 playbook 存到 `.claude/team-update-playbook.md`。

讀 [references/playbook-format.md](references/playbook-format.md) 看完整模板。所有區塊都用探索到的工具和使用者偏好填好。如果某個能力沒找到，就在 playbook 裡標成 "Not available"。

確認 `.claude/` 在 `.gitignore` 裡（playbook 含有空間 ID 和偏好設定，不該被 commit）。

---

## Phase 1：收集背景資訊

從所有可用的來源蒐集資訊。用 playbook 的 "Data Sources" 區塊來知道要呼叫哪些工具。

### 1a. 決定時間範圍

查看 playbook 的 "Last Run" 區塊，找出上次更新的時間戳記。如果之前沒跑過，問使用者要回溯多久（預設：24 小時）。

### 1b. 收集資料

從每個可用的來源蒐集：

| 來源 | 要收集什麼 | 工具 |
|---|---|---|
| **Git commits** | `git log --oneline --since=<last-update>` | Bash |
| **聊天訊息** | 自上次更新以來，設定的頻道裡的訊息 | playbook 裡的 Chat MCP 工具 |
| **未結的 issue/PR** | 最近更新或新建立的項目 | playbook 裡的 issue tracker |
| **進行中的任務** | 進行中或最近完成的任務 | playbook 裡的任務追蹤工具 |

### 1c. 整理成起草用的摘要

把 commit 依主題分組（不要列個別的 hash）。記下關閉的 issue、合併的 PR 或完成的任務。標出需要回覆的團隊訊息。

---

## Phase 2：起草並發布更新

### 2a. 撰寫訊息

讀 [references/message-composition.md](references/message-composition.md) 看訊息模式。

照 playbook 的 "Message Style" 區塊。一般原則：

- 先講出貨了什麼或改了什麼，不要先講過程
- 把相關的 commit 歸成主題
- 只在相關時才提到特定的人
- 保持好掃讀（短段落、條列）
- **像隊友一樣寫，不要像 AI**：不要狂用 emoji，不要含糊其辭，不要過度解釋團隊早就知道的背景。看 [references/message-composition.md](references/message-composition.md) 的 Communication Style 區塊。

### 2b. 預覽與核准

把草稿給使用者看。包含：
- 寫好的訊息
- 會貼到哪個頻道
- 是新訊息還是在 thread 裡回覆

**必須經過核准**：沒有使用者明確同意，絕對不要貼到外部頻道。

### 2c. 發布

用 playbook 裡的聊天工具貼出已核准的訊息。如果沒有可用的聊天工具，就輸出排好版的訊息，讓使用者手動貼。

### 2d. 更新 Playbook

貼完之後，更新 playbook 的 "Last Run" 區塊：
- 目前的時間戳記
- Thread key（如果適用）
- 這次貼了什麼的簡短摘要

---

## Phase 3：讀取並分類回饋

### 3a. 讀取回應

讀取設定的頻道裡，更新貼出之後的訊息。找：
- 對這則更新的直接回覆
- 頻道裡提到這個專案的新訊息
- 表情反應或確認回應

### 3b. 分類回饋

讀 [references/feedback-triage.md](references/feedback-triage.md) 看分類模式。

用 playbook 的 "Triage Rules" 區塊。預設分類：

| 類型 | 動作 |
|---|---|
| Bug 回報 | 建立 issue（label: bug） |
| 功能請求 | 建立 issue（label: enhancement） |
| 問題 | 起草回覆，等使用者核准 |
| Blocker | 立刻標出來，建議解法 |
| 確認回應 | 記下，不需要動作 |
| 離題 | 忽略 |

### 3c. 呈現並執行

呈現回饋摘要和建議的動作：

```
## Feedback Summary

- Daniel: "Can we add dark mode?" -> Create issue (enhancement)
- Rabin: "Auth is broken on staging" -> Create issue (bug, priority)
- Karen: "Looks good!" -> No action

Proceed with these actions?
```

**必須經過核准**：沒有使用者明確同意，絕對不要建立 issue、貼回覆或採取任何外部動作。

---

## Phase 4：規劃下一步

### 4a. 排優先順序

從所有收集到的背景資訊（commit、issue、任務、回饋），找出：
1. **Blockers**：阻擋進度的事
2. **高優先**：Bug、緊急請求、截止日
3. **接下來**：已規劃的工作、功能請求
4. **Backlog**：有最好、低優先的項目

### 4b. 呈現（不要貼出去）

把排好優先順序的清單給使用者看。這只供使用者自己規劃，**不要**貼到任何頻道。

```
## Suggested Priorities

1. [BLOCKER] Fix auth on staging (from Rabin's feedback)
2. [HIGH] Complete API endpoint for user profiles (current sprint)
3. [NEXT] Dark mode support (from Daniel's request)
4. [BACKLOG] Refactor database queries
```

---

## 自主權規則

| 動作 | 層級 |
|---|---|
| 讀取/建立 playbook | 直接做 |
| 探索工具（第一次執行） | 直接做，跟使用者確認偏好 |
| 收集背景資訊（git、聊天、issue） | 直接做 |
| 起草更新訊息 | 直接做，並顯示預覽 |
| **貼到外部頻道** | **需要核准** |
| **建立 issue/任務** | **需要核准** |
| **貼回覆給團隊** | **需要核准** |
| 更新 playbook 的 "Last Run" | 直接做 |
| 呈現計畫/優先順序 | 直接做 |

---

## 優雅降級

不管有多少工具可用，這個 skill 都能運作：

| 可用工具 | 體驗 |
|---|---|
| 只有 Git | 摘要 commit，輸出文字讓使用者手動貼 |
| Git + Chat | 完整的貼出/讀取循環，手動建立 issue |
| Git + Chat + Issues | 完整循環，自動建立 issue |
| Git + Chat + Issues + Tasks + Knowledge | 完整循環，附持續追蹤 |

---

## 運作模式

這個 skill 會依不同的觸發詞做出不同反應：

| 觸發詞 | 行為 |
|---|---|
| "team update" / "post update" | 完整循環：收集、起草、發布、讀取回饋 |
| "check team chat" / "what did the team say" | 只做 Phase 3：讀取並分類回饋 |
| "standup" / "sync with team" | Phase 1 + 2：收集並發布，跳過回饋 |
| "project update" | Phase 1 + 2 + 4：收集、發布、規劃（跳過回饋分類） |
| "feedback loop" | Phase 3 + 4：讀取回饋並規劃 |

---

## 參考檔案

| 時機 | 讀這個 |
|------|------|
| 第一次執行：儲存 playbook | [references/playbook-format.md](references/playbook-format.md) |
| 第一次執行：偵測工具 | [references/discovery-patterns.md](references/discovery-patterns.md) |
| 撰寫更新訊息 | [references/message-composition.md](references/message-composition.md) |
| 分類團隊回饋 | [references/feedback-triage.md](references/feedback-triage.md) |
