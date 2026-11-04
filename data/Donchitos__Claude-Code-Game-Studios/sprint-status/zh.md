---
name: sprint-status
description: "快速精簡的 sprint 快照：burndown 和浮現中的風險，用來掌握現況。'How is the sprint going?'"
argument-hint: "[sprint-number or blank for current]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Bash(bash "*/.claude/skills/sprint-status/../../hooks/yaml-helper.sh" resolve_config *), Bash(bash "*/.claude/skills/sprint-status/../../scripts/story-status.sh"), Bash(bash .claude/scripts/story-status.sh*)
model: haiku
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys story_granularity,workflow`



# Sprint Status

這是快速掌握現況的檢查，不是 sprint 審查。它會讀目前的
sprint 計畫和 story 檔案、掃描狀態標記，並在 30 行以內產出一份
精簡的快照。要做詳細的 sprint 管理，用
`/sprint-plan update` 或 `/milestone-review`。

**這個 skill 是唯讀的。** 它絕對不會提議修改、絕對不會要求寫檔，
而且最多只給一個具體的建議。

**`story_granularity`**：它決定
burn-down 判讀的粒度：`coarse`（預設，透過 `rigor: minimal`）是**功能等級**的區塊，`balanced`（`rigor: standard`）是**任務等級**，
`fine` 是 **AC 等級**。

---

## 1. Find the Sprint

**參數：** `$ARGUMENTS`（空白 = 用目前的 sprint）

- 如果有給參數（例如 `/sprint-status 3`），在
  `production/sprints/` 裡搜尋符合 `sprint-003.md`、`sprint-03.md`、`sprint-3.md`
  或類似名稱的檔案（`/sprint-plan` 寫的是三位數）。要回報找到哪個檔案。
- 如果沒有給參數，找 `production/sprints/` 裡最近修改的檔案，
  把它當成目前的 sprint。
- 如果 `production/sprints/` 不存在或是空的：
  - **在 `workflow: minimal` 時，依設計就沒有 sprint**：brief 的
    build order 就是計畫，story 檔案承載它。改為回報
    它的進度，然後停下來：
    1. 下面的清單是在你讀這個 skill 之前，由 `.claude/scripts/story-status.sh`
       印出來的：每個未完成的 story 一行，已經依
       路線的順序排好（`IN_REVIEW`、`IN_PROGRESS`，然後是 `TODO`：`Ready`
       或 `Not Started` 的 story，依 build order），接著是 `BLOCKED`、`OTHER`、
       `NO_STATUS` 和 `COMPLETE` 的數量：

!`bash "${CLAUDE_SKILL_DIR}/../../scripts/story-status.sh"`

    2. 在 15 行以內印出：`Build order: [N] of [M] stories complete`
       取自 `COMPLETE` 那一行（只計算 `Complete` 和 `Done` 的 story：
       `In Review` 不算完成），然後是 **Next**：第一個 `IN_REVIEW`、
       `IN_PROGRESS` 或 `TODO` 那一行的 story。清單已經是
       最新的；不要再跑一次腳本，也不要重新排序 story 檔案：`In Review` 的 story 要先結掉，
       才繼續 `In Progress` 的：它的工作已經寫完了。`IN_REVIEW` 建議
       `/story-done [path]`，`IN_PROGRESS` 或 `TODO` 建議
       `/dev-story [path]`。任何 `BLOCKED` 的 story 要連同它的 blocker 一起點名；它
       絕對不會是 Next。
    3. 每個 story 都是 `Complete`（或 `Done`）→ "Build order done: [M] of [M]
       stories complete." 提供三條路往下走：玩玩這個 build；用 `/create-stories`
       從 brief 加入下一批 story；或者如果遊戲已經超出一頁 brief 的範圍，
       用 `/settings` 提高 `modes.rigor`。
    4. `STORIES none`：完全沒有 story 檔案 → "No stories yet. Run
       `/create-stories` to turn the brief's build order into stories."
    5. 沒有 `IN_REVIEW`、`IN_PROGRESS` 或 `TODO` 那一行，但 `COMPLETE` 那一行
       少於總數：每個未完成的 story 都是 `BLOCKED`、`OTHER`
       （例如 `Draft`）或 `NO_STATUS`。**沒有 Next**，而且 build
       order **沒有**完成：絕對不要說它完成了。印出 `Build order` 那一行，
       然後逐一點名每個 `BLOCKED` 的 story 和它的 blocker（從它的 story
       檔案讀，通常是 `BLOCKED:` 的備註），以及其他每個 story 和它寫的
       狀態。建議一個步驟：第一個 blocker 需要什麼，否則
       就是完成第一個 `Draft` 或沒有狀態的 story，並把它的 Status 設成
       `Ready`。
  - **在 `standard` 或 `full` 時**，回報："No sprint files found. Start a sprint
    with `/sprint-plan new`." 然後停下來。

完整讀 sprint 檔案。擷取：
- Sprint 編號和目標
- 開始日期和結束日期
- 所有 story 或任務條目，附上它們的優先順序（Must Have / Should Have /
  Nice to Have）、負責人和估算

---

## 2. Calculate Days Remaining

使用今天的日期和 sprint 檔案裡的 sprint 結束日期，計算：
- sprint 總天數（結束減開始）
- 已經過的天數
- 剩餘天數
- 已消耗時間的百分比

如果 sprint 檔案沒有明確的日期，註記 "Sprint dates not
found — burndown assessment skipped."

---

## 3. Scan Story Status

**首先：檢查 `production/sprint-status.yaml`。**

如果它存在，直接讀它：它是權威的事實來源。
擷取每個 story 的 `status`，以及有設定時的 `priority`、`owner` 和 `blocker`：它們填進狀態表的欄位。不需要掃描 markdown。
用它的 `sprint`、`goal`、`start`、`end` 欄位，不要重新解析 sprint 計畫。

**如果 `sprint-status.yaml` 不存在**（舊版 sprint 或第一次設定），
退而掃描 markdown：

1. 如果條目引用了 story 檔案路徑，檢查檔案是否存在。
   讀檔案並掃描狀態標記：DONE、COMPLETE、IN PROGRESS、
   BLOCKED、NOT STARTED（不分大小寫）。
2. 如果條目沒有檔案路徑（sprint 計畫裡的 inline 任務），掃描
   sprint 計畫本身，找那個條目旁邊的狀態標記。
3. 如果找不到狀態標記，分類為 NOT STARTED。
4. 如果引用了檔案但它不存在，分類為 MISSING 並記下來。

使用備援做法時，在輸出底部加一則註記：
"⚠ No `sprint-status.yaml` found — status inferred from markdown. Run `/sprint-plan update` to generate one."

可選的（只做快速檢查，不要做深度掃描）：在程式碼根目錄 grep
符合 story 系統 slug 的目錄或檔名，檢查有沒有實作的證據。
這只是提示，不是確定的狀態。

### Stale Story Detection

收集完所有 story 的狀態之後，檢查每個 IN PROGRESS 的 story 是否過時：

- 用**對整組 story 做一次 grep，不要每個 story 各讀一次**
  來解析日期：日期是單獨一行，為了找它而打開每個進行中的 story，
  就是這項檢查的全部成本：
  ```
  Grep pattern="\*{0,2}(Last Updated|Updated|last-updated|updated_at)\*{0,2}[[:space:]]*:" glob="production/epics/**/story-*.md" output_mode="content"
  ```
  那一個 pattern 接受所有欄位名稱的變體。沒有符合的 story 就是
  **沒有日期**，這不等於過時：把它回報成 "never stamped"，
  而且不要為它計算天數。

> **`\*{0,2}` 這些包覆是它能運作的根本原因。** `/create-stories` 輸出
> `> **Last Updated**: …`，所以要求單字後面緊接 `:` 的 pattern
> 一個 story 都比對不到。再加上緊接在上面的「沒有符合 = never stamped」規則，
> 那個失敗是靜默的：每個進行中的 story 都回報成 never
> stamped，過時 story 偵測永遠不會觸發。不要使用單純的 `Updated:`
> 錨點。
- 用今天的日期計算距離那個日期的天數。
- 如果日期超過 4 天前，把 story 標記為 **STALE**。（4 天的門檻考慮到週末：星期五最後碰過的 story，要到星期三才會顯示為過時。）
- 如果在 story 檔案裡找不到日期欄位，註記 "no timestamp — cannot check staleness."
- 如果 story 沒有引用的檔案（inline 任務），註記 "inline task — cannot check staleness."

STALE 的 story 會列在輸出表格裡，並收集到一個 "Attention Needed"
段落（見 Phase 5 的輸出格式）。

**過時 story 的升級**：如果任何 IN PROGRESS 的 story 被標為 STALE（4 天以上沒有進展），burndown 的結論
至少升級為 **At Risk**：即使完成百分比在正常的
On Track 範圍內。記錄這個升級的原因："At Risk — [S] stale story(ies): [title]
([D] days)[, …]"：[S] 是 STALE 的 story 數量，每個 story 都用它自己的 [D] 點名，
就是從它自己的 Last Updated 日期起算的天數（不是最久的天數，也不是平均值）。

---

## 4. Burndown Assessment

計算：
- 已完成的任務（DONE 或 COMPLETE）
- 進行中的任務（IN PROGRESS）
- 被阻擋的任務（BLOCKED）
- 尚未開始的任務（NOT STARTED 或 MISSING）
- 完成百分比：(complete / total) * 100

把完成百分比跟已消耗時間百分比做比較，來評估 burndown：

- **On Track**：完成 % 在已消耗時間 % 的 10 個百分點以內，或是領先
- **At Risk**：完成 % 落後已消耗時間 % 10-25 個百分點
- **Behind**：完成 % 落後已消耗時間 % 超過 25 個百分點

如果沒有日期，跳過 burndown 評估，回報 "On Track /
At Risk / Behind: unknown — sprint dates not found."

---

## 5. Output

輸出要精簡。story 狀態表是必備的：不要截斷它。總共目標在 50 行以內；如果沒發現什麼值得注意的，就省略 Emerging Risks 段落。使用這個格式：

```markdown
## Sprint [N] Status — [Today's Date]
**Sprint Goal**: [from sprint plan]
**Days Remaining**: [N] of [total] ([% time consumed])

### Progress: [complete/total] tasks ([%])

| Story / Task         | Priority   | Status      | Owner   | Blocker        |
|----------------------|------------|-------------|---------|----------------|
| [title]              | Must Have  | DONE        | [owner] |                |
| [title]              | Must Have  | IN PROGRESS | [owner] |                |
| [title]              | Must Have  | BLOCKED     | [owner] | [brief reason] |
| [title]              | Should Have| NOT STARTED | [owner] |                |

### Attention Needed
| Story / Task         | Status      | Last Updated   | Days Stale | Note           |
|----------------------|-------------|----------------|------------|----------------|
| [title]              | IN PROGRESS | [date or N/A]  | [N days]   | [STALE / no timestamp — cannot check staleness / inline task — cannot check staleness] |

*(Omit this section entirely if no IN PROGRESS stories are stale or have timestamp concerns.)*

### Burndown: [On Track / At Risk / Behind]
[1-2 sentences. If behind: which Must Haves are at risk. If on track: confirm
and note any Should Haves the team could pull.]

### Must-Haves at Risk
[List any Must Have stories that are BLOCKED or NOT STARTED with less than
40% of sprint time remaining. If none, write "None."]

### Emerging Risks
[Any risks visible from the story scan: missing files, cascading blockers,
stories with no owner. If none, write "None identified."]

### Recommendation
[One concrete action, or "Sprint is on track — no action needed."]
```

---

## 6. Fast Escalation Rules

輸出之前套用這些規則，如果觸發了，把旗標放在輸出的最上面
（狀態表之上）：

**Critical flag**：如果 Must Have 的 story 是 BLOCKED 或 NOT STARTED，而且
sprint 剩餘時間少於 40%：

```
SPRINT AT RISK: [N] Must Have stories are not complete with [X]% of sprint
time remaining. Recommend replanning with `/sprint-plan update`.
```

**Completion flag**：如果所有 Must Have 的 story 都是 DONE：

```
All Must Haves complete. Team can pull from Should Have backlog.
```

**Missing stories flag**：如果任何引用的 story 檔案不存在：

```
NOTE: [N] story files referenced in the sprint plan are missing.
Run `/story-readiness sprint` to validate story file coverage.
```

---

## Collaborative Protocol

這個 skill 是唯讀的。它回報的是從磁碟上的檔案觀察到的事實。

- 它不會更新 sprint 計畫
- 它不會改變 story 狀態
- 它不會提議砍範圍（那是 `/sprint-plan update`）
- 它每次執行最多給一個建議

要看某個特定 story 的更多細節，使用者可以直接讀 story 檔案，
或是跑 `/story-readiness [path]`。

要重新規劃 sprint，用 `/sprint-plan update`。
要做 sprint 結束時的回顧，用 `/retrospective`。
