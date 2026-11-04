---
name: retrospective
description: "根據已完成的工作、velocity、blocker 做 sprint 或 milestone 回顧，產出下一輪可執行的洞見。"
argument-hint: "[sprint-N|milestone-name]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, AskUserQuestion, Bash(bash "*/.claude/skills/retrospective/../../hooks/yaml-helper.sh" resolve_config *), Bash(git log *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation,workflow,qa.level`

# Retrospective



每一次 `AskUserQuestion` 呼叫都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律詢問 · guided 只問重大事項 · autonomous 記錄後直接進行；
屬於 `automation_always_ask` 的類別一律要詢問）。

## Insufficient input：產出任何報告之前，先檢查這個

**如果這個 skill 需要的輸入不存在，答案就是「跑不了」，
不是一份硬填出來的報告。** 先檢查，檢查沒過就停。

1. 列出這個 skill 要讀的輸入（資料檔、先前的報告、profiler 輸出、
   測試結果、registry、原始碼）。
2. 對每一項記錄 `FOUND` 或 `ABSENT`，不要寫「假設存在」。
3. 如果某一段需要的輸入是 ABSENT，那一段就是
   **`NOT ASSESSED — NO DATA`**。不要估算，不要從相鄰的產物推論，
   也不要把規定要填的欄位留給下一個讀範本的人去填。
4. 如果**所有**必要的輸入都是 ABSENT，就停下來，整份結論回報
   **`NOT ASSESSED — NO DATA`**，並點名缺了什麼、
   是哪個 skill 會產出它。

**`NOT ASSESSED` 這個結論算成功。** 當根本沒有資料時，
這就是對「資料說了什麼？」最正確、最有用的回答。這條規則要防的失敗模式很具體：
如果報告的結論列舉值裡沒有「跑不了」這個狀態，就會產生
**假的乾淨通過**：在一個沒有資產也沒有標準的專案上，資產稽核回傳 COMPLIANT；
或是在 profiler 資料是零、預算也從沒設定的情況下，效能報告寫「對 16.67ms 預算有 >99% 餘裕」。

**沒有證據，不等於沒有問題。** 掃描時因為沒有檔案可掃而找不到任何符合的東西，
等於什麼都沒驗證。要講清楚是這兩種情況的哪一種，
因為讀的人光看綠燈結果分辨不出來。

---

## Phase 1: Parse Arguments

判斷這是 sprint 回顧（`sprint-N`）還是 milestone 回顧（`milestone-name`）。

---

## Phase 1b: Check for Existing Retrospective

載入任何資料之前，先 glob 看有沒有已存在的回顧檔：

- sprint 回顧：`production/retrospectives/retro-[sprint-slug]-*.md`
  （也要檢查備用位置 `production/sprints/sprint-[N]-retrospective.md`）
- milestone 回顧：`production/retrospectives/retro-[milestone-name]-*.md`

如果找到符合的檔案，用 `AskUserQuestion`：
- Prompt："An existing retrospective was found: [filename]. How do you want to proceed?"
- Options：
  - `[A] Update existing — load it and add/revise sections with new data`
  - `[B] Start fresh — generate a new retrospective (archive the old one)`

選 [A]：讀取既有檔案，沿用它的內容，用新資料修訂各段。
選 [B]：從空白狀態繼續進 Phase 2。寫新檔之前，先把既有檔案改名，加上 `-archived-[date]` 後綴。改名也算寫入：它發生在 Phase 5，而且要等那裡的詢問（詢問內容會點名這件事）被核准之後才做。

---

## Phase 2: Load Sprint or Milestone Data

從適當的位置讀取 sprint 或 milestone 計畫：

- Sprint 計畫：`production/sprints/`
- Milestone 定義：`production/milestones/`

**也要檢查 `production/sprint-status.yaml`**：如果存在，就跟 sprint 計畫一起讀。它是 story 實際完成狀態（status: done、完成日期、blocker）的權威來源。Phase 3 的完成度指標以它為主要來源。只有 yaml 不存在時才退而掃描 markdown。要記下 yaml 和 sprint 計畫之間的差異（例如 yaml 裡有但計畫裡沒有的 story，或反過來）。

**如果檔案不存在或是空的**，輸出：

> "No sprint data found for [sprint/milestone]. Run `/sprint-plan new` to create a
> sprint (`/sprint-status` only reads one), or provide the sprint details manually."

在 `workflow: minimal`（上面已解析）時沒有 sprint：改為提議回頭檢視目前
已關閉的 story（`production/epics/*/story-*.md` 中 `Status: Complete` 的）。
在 `qa.level: minimal`（上面已解析）時測試是免除的，所以 story 關閉時沒有測試
不算問題；但 Visual/Feel 或 UI 的 story 關閉時沒有留存截圖，仍然算問題。

然後用 `AskUserQuestion` 呈現這些選項（[C] 只在 `workflow: minimal` 時出現）：

- **[A] Provide data manually**：請使用者貼上或描述 sprint 的
  任務、日期和成果，以此作為回顧的事實依據。
- **[B] Stop**：中止這個 skill。結論：**BLOCKED**，沒有可用的 sprint 資料。
- **[C] Look back over the closed stories**：把 `Status: Complete` 的 story
  當作已完成事項的紀錄。

如果使用者選 [A]，收集資料，用他們提供的內容繼續 Phase 3。
如果使用者選 [B]，到這裡就停。
如果使用者選 [C]，讀那些 story，繼續 Phase 3。需要 sprint 資料的段落
（計畫 vs 實際、velocity、carryover、估算準確度）
標成 `NOT ASSESSED — NO DATA`。

擷取：計畫的任務、估算工時、負責人和目標。

對 sprint 期間跑 git log，了解實際 commit 了什麼、什麼時候 commit 的。用 Bash 工具（在 Windows 上走的是 Git Bash，`2>/dev/null` 是 bash 語法，不是 PowerShell）：

```
Bash: git log --oneline --since="4 weeks ago" 2>/dev/null || git log --oneline -20
```

如果從 sprint 計畫知道 sprint 長度，就調整 `--since` 的日期去配合。

---

## Phase 3: Analyze Completion and Trends

比對計畫和實際交付物，掃出已完成和未完成的任務。檢查：

- 照計畫完成的任務
- 完成了但跟計畫不一樣的任務
- 被遞延（沒完成）的任務
- sprint 中途新增的任務（計畫外的工作）
- 被移除或縮減範圍的任務

`production/sprint-status.yaml` 裡每一個 `status: blocked` 的 story，
都要放進 Blockers Encountered，用它的 `blocker` 欄位當作 Blocker，
並在 Action Items for Next Iteration 裡給它一個行動項目。

掃描程式碼庫的 TODO/FIXME 趨勢：

- 計算目前的 TODO/FIXME/HACK 註解數量
- 如果有的話，跟上一個 sprint 的數量比較（看先前的回顧）
- 記下技術債是在增加還是減少

讀取 `production/retrospectives/` 裡先前的回顧（如果有），檢查：

- 先前的行動項目有處理嗎？
- 同樣的問題是不是一再發生？
- velocity 的趨勢如何？

如果沒有更早的 sprint 或回顧，Velocity Trend 只保留目前 sprint 那一列，
並寫 `NOT ASSESSED — NO DATA`，Previous Action Items
Follow-Up 就只有那一行，不要編造更早的列，也不要留空表格。

---

## Phase 4: Generate the Retrospective

```markdown
## Retrospective: [Sprint N / Milestone Name]
Period: [Start Date] -- [End Date]
Generated: [Date]

### Metrics

| Metric | Planned | Actual | Delta |
|--------|---------|--------|-------|
| Tasks | [X] | [Y] | [+/- Z] |
| Completion Rate | -- | [Z%] | -- |
| Story Points / Effort Days | [X] | [Y] | [+/- Z] |
| Bugs Found | -- | [N] | -- |
| Bugs Fixed | -- | [N] | -- |
| Unplanned Tasks Added | -- | [N] | -- |
| Commits | -- | [N] | -- |

### Velocity Trend

| Sprint | Planned | Completed | Rate |
|--------|---------|-----------|------|
| [N-2] | [X] | [Y] | [Z%] |
| [N-1] | [X] | [Y] | [Z%] |
| [N] (current) | [X] | [Y] | [Z%] |

**Trend**: [Increasing / Stable / Decreasing — or `NOT ASSESSED — NO DATA` with no earlier sprint to compare]
[One sentence explaining the trend]

### What Went Well
- [Observation backed by specific data or examples]
- [Another positive observation]
- [Recognize specific contributions or decisions that paid off]

### What Went Poorly
- [Specific issue with measurable impact -- e.g., "Feature X took 5 days
  instead of estimated 2, blocking tasks Y and Z"]
- [Another issue with impact]
- [Do not assign blame -- focus on systemic causes]

### Blockers Encountered

| Blocker | Duration | Resolution | Prevention |
|---------|----------|------------|------------|
| [What blocked progress] | [How long] | [How it was resolved] | [How to prevent recurrence] |

### Estimation Accuracy

| Task | Estimated | Actual | Variance | Likely Cause |
|------|-----------|--------|----------|--------------|
| [Most overestimated task] | [X] | [Y] | [+Z] | [Why] |
| [Most underestimated task] | [X] | [Y] | [-Z] | [Why] |

**Overall estimation accuracy**: [X%] of tasks within +/- 20% of estimate

[Analysis: Are we consistently over- or under-estimating? For which types of
tasks? What adjustment should we apply?]

### Carryover Analysis

| Task | Original Sprint | Times Carried | Reason | Action |
|------|----------------|---------------|--------|--------|
| [Task that was not completed] | [Sprint N-X] | [N] | [Why] | [Complete / Descope / Redesign] |

### Technical Debt Status
- Current TODO count: [N] (previous: [N])
- Current FIXME count: [N] (previous: [N])
- Current HACK count: [N] (previous: [N])
- Trend: [Growing / Stable / Shrinking]
- [Note any areas of concern]

### Previous Action Items Follow-Up

| Action Item (from Sprint N-1) | Status | Notes |
|-------------------------------|--------|-------|
| [Previous action] | [Done / In Progress / Not Started] | [Context] |

### Action Items for Next Iteration

| # | Action | Owner | Priority | Deadline |
|---|--------|-------|----------|----------|
| 1 | [Specific, measurable action] | [Who] | [High/Med/Low] | [When] |
| 2 | [Another action] | [Who] | [Priority] | [When] |

### Process Improvements
- [Specific change to how we work, with expected benefit]
- [Another improvement -- keep it to 2-3 actionable items, not a wish list]

### Summary
[2-3 sentence overall assessment: Was this a good sprint/milestone? What is
the single most important thing to change going forward?]
```

---

## Phase 5: Save Retrospective

把回顧和主要發現呈現給使用者（完成率、velocity 趨勢、最大的 blocker、最重要的行動項目）。

詢問："May I write this to `production/retrospectives/retro-sprint-[N]-[date].md`?"（milestone 回顧則是 `production/retrospectives/retro-[milestone-name]-[date].md`）

如果在 Phase 1b 選了 Start fresh，同一個詢問也要點名改名這件事："…and rename
`[old file]` to `[old file name]-archived-[date].md`?" 同意的話，先改名再
寫檔；不同意的話，兩件事都不做。

如果同意，就寫檔，`production/retrospectives/` 目錄不存在的話先建立。結論：**COMPLETE**，回顧已儲存。

如果不同意，到這裡就停。結論：**BLOCKED**，使用者拒絕寫入。

---

## Phase 6: Next Steps

在 `workflow: minimal`（上面已解析）時沒有 sprint，跳過這個問題：
指向回顧檔案，並說明它的行動項目會放進 brief 的 build order。

其他情況，用 `AskUserQuestion`：
- Prompt："Retrospective complete. The action items and velocity data are ready. Would you like to start sprint planning now with this data pre-loaded?"
- Options：
  - `[A] Yes — open sprint planning with retro action items and velocity delta pre-populated`
  - `[B] No — I'll reference the retrospective file manually when I'm ready`

如果使用者選 [A]：接著呼叫 `/sprint-plan new`，把回顧檔案路徑，以及行動項目和 velocity 變化的摘要傳進去，讓 sprint 規劃可以參考。

- 如果這是 milestone 回顧，跑 `/gate-check`，正式評估是否準備好進入下一階段。

### Guidelines

- 要誠實、具體。含糊的回顧（「溝通可以更好」）只會產生含糊的改進。用資料和例子。
- 把焦點放在系統性問題，不要怪個人。
- 行動項目限制在 3 到 5 個。再多就會失焦。
- 每個行動項目都要有負責人和期限。
- 檢查先前的行動項目有沒有完成。一再沒處理的項目就是流程的壞味道。
- 如果這是 milestone 回顧，也要評估 milestone 目標有沒有達成，以及這對整個專案時程代表什麼。
