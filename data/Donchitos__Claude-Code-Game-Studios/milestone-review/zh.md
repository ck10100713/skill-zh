---
name: milestone-review
description: "Milestone 進度審查：完成度、品質指標、風險，並給出 go/no-go 建議。用在檢查點或截止日前。"
argument-hint: "[milestone-name|current] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Agent, AskUserQuestion, Bash(bash "*/.claude/skills/milestone-review/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,workflow`

上面已經解析好了，直接用；`--review` 在這次執行會覆蓋 `review_mode`。沒有
這個區塊的話，用 `.claude/docs/config-resolution.md` 裡的預設值。

# Milestone Review



## Insufficient input — check this before producing any report

**如果這個 skill 需要的輸入不存在，答案就是「跑不起來」，
不是一份填好的報告。** 先檢查，檢查沒過就停下來。

1. 列出這個 skill 會讀的輸入（資料檔、先前的報告、profiler 輸出、
   測試結果、registry、原始碼）。
2. 對每一項，記錄 `FOUND` 或 `ABSENT` — 不是「假設存在」。
3. 如果某個章節需要的任何輸入是 ABSENT，那個章節就是
   **`NOT ASSESSED — NO DATA`**。不要估算它、不要從
   相鄰的產出物去推斷它，也不要把一個強制要填的格子留給
   下一個讀範本的人去填。
4. 如果**每一個**必要的輸入都是 ABSENT，就停下來，並把
   **`NOT ASSESSED — NO DATA`** 當成整份判定回報，點名缺了什麼，
   以及哪個 skill 會產生它。

**`NOT ASSESSED` 的判定是一種成功。** 當沒有資料時，它就是對
「資料怎麼說？」正確又有用的答案。這條規定要防的失誤很具體：
判定列舉裡沒有「跑不起來」狀態的報告，會產生
**假的乾淨通過** — 在沒有資產也沒有標準的專案上，資產稽核回傳 COMPLIANT；
或者效能分析在零 profiler 資料、也從來沒設過預算的情況下，回報「>99% headroom against
a 16.67ms budget」。

**沒有證據，不等於證據不存在。** 因為沒有檔案可掃，所以沒找到任何
符合項目的掃描，什麼都沒驗證。要說清楚到底是這兩者中的哪一個 — 讀的人
光看綠色結果是分辨不出來的。

---

## Phase 0: Parse Arguments

擷取 milestone 名稱（`current` 或指定的名稱）。

完整的檢查模式見 `.claude/docs/director-gates.md`。各個 gate 的定義放在 `.claude/docs/director-gates/[gate-id].md` — 被派出的 agent 會自己讀它的 gate 檔；不要在父 session 裡讀。


每一次 `AskUserQuestion` 呼叫都遵循 `.claude/docs/automation-modes.md`
（collaborative 一律問 · guided 只問重大的 · autonomous 只記錄然後繼續；
`automation_always_ask` 的類別一律要問）。

---

## Phase 1: Load Milestone Data

如果 `production/milestones/` 裡有 milestone 定義，就讀它。如果
參數是 `current`，就用最近修改過的 milestone 檔。

> **沒有任何 skill 會寫 `production/milestones/`** — 定義是從
> `.claude/docs/templates/milestone-definition.md` 手寫的，所以大部分專案
> 都沒有。當目錄不存在或是空的，就講出來，並只依 sprint 報告來審查；
> 不要捏造定義。用 `current` 時要小心：
> 這個 skill 會把自己的輸出寫成 `[milestone-name]-review.md`，所以
> 最近修改的符合項目可能是之前的*審查*，不是定義。
> 挑選時要跳過以 `-review.md` 結尾的檔案。

從 `production/sprints/` 蒐集這個 milestone 範圍內各個 sprint 的報告。先確立分母（用 glob 找出來，計數 **N**），然後
掃描 milestone 審查真正會彙總的那些章節，而不是把每份
報告整份讀完：

```
Grep pattern="^## (Sprint Goal|Capacity|Tasks|Carryover|Risks|Progress|Burndown Assessment|Emerging Risks|Definition of Done)" glob="production/sprints/sprint-*.md" output_mode="content" -A 12
```

> **這些候選項是 `/sprint-plan` 產出的標題**（`## Sprint Goal`，
> 不是 `## Goal`）— 不是 milestone 審查可能預期的那些。只符合一個真實標題的 pattern，
> 仍然會回傳非零的計數，所以下面「零符合」的退路
> 永遠不會觸發，審查就只彙總了每份報告的一小部分，卻回報
> 涵蓋完整。

當某份 sprint 報告被掃描到的章節指向它們自己以外的地方，
或它什麼都沒符合時，就整份讀它 — 零符合的報告是在範本之前寫的，
必須讀，絕對不能默默從 milestone 的歷史裡丟掉。
回報任何沒有貢獻內容的 sprint：默默漏掉一個 sprint 的 milestone 摘要，
會同時低估工作量和延誤。

**Blocked story** — 傳給 PR-MILESTONE 的 Blocked 表格和 blocked story 數量 —
不在 sprint 報告被掃描的章節裡。去它們被記錄的地方讀：
`production/sprint-status.yaml` 裡 `status: blocked` 的 story
（連同它們的 `blocker` 欄位），而對那個 sprint 以外的 story，用一次 grep：

```
Grep pattern="^> \*\*Status\*\*: Blocked|BLOCKED:" glob="production/epics/**/story-*.md" output_mode="content"
```

每個 blocked story 都放進 Blocked 表格，歸在它 epic 資料夾所實作的 feature 底下，
並附上它的 blocker（yaml 的 `blocker` 欄位或 story 的 `BLOCKED:`
備註）。沒有 story 檔也沒有 `sprint-status.yaml` 時，Blocked 表格和
blocked story 數量就是 `NOT ASSESSED — NO DATA`，不是零。

---

## Phase 2: Scan Codebase Health

- 掃描代表工作未完成的 `TODO`、`FIXME`、`HACK` 標記
- 從 `production/qa/bugs/` 依嚴重度計算 Quality Metrics 的未解 bug 數（對 `**Severity**` 和 `**Status**` 行做一次 grep，就像 `/bug-triage` 做的）；沒有 bug 檔的話，bug 那幾行是 `NOT ASSESSED — NO DATA`，不是零
- 如果 `production/risk-register/` 的風險登記冊存在就檢查它（從 `.claude/docs/templates/risk-register-entry.md` 手寫；沒有 skill 會寫它，所以不存在是正常的 — 註明這點，不要默默跳過風險評估）

---

## Phase 3: Generate the Milestone Review

```markdown
# Milestone Review: [Milestone Name]

## Overview
- **Target Date**: [Date]
- **Current Date**: [Today]
- **Days Remaining**: [N]
- **Sprints Completed**: [X/Y]

## Feature Completeness

### Fully Complete
Only a feature whose Status is `Complete` goes here or counts toward the completion percentage; a Deferred feature stays in its denominator, named with the milestone it moved to.

| Feature | Acceptance Criteria | Test Status |
|---------|-------------------|-------------|

### Partially Complete
| Feature | % Done | Remaining Work | Risk to Milestone |
|---------|--------|---------------|------------------|

### Blocked
A started feature whose stories are Blocked goes here, not under Partially
Complete — name the blocker, so the review says why it stalled, not only that
the count moved.

| Feature | Blocked Stories | Blocker | Next Action / Owner |
|---------|----------------|---------|---------------------|

### Not Started
| Feature | Priority | Can Cut? | Impact of Cutting |
|---------|----------|----------|------------------|

## Quality Metrics
- **Open S1 Bugs**: [N] -- [List]
- **Open S2 Bugs**: [N]
- **Open S3 Bugs**: [N]
- **Test Coverage**: [X%]
- **Performance**: [Within budget? Details]

## Code Health
- **TODO count**: [N across codebase]
- **FIXME count**: [N]
- **HACK count**: [N]
- **Technical debt items**: [List critical ones]

## Risk Assessment
| Risk | Status | Impact if Realized | Mitigation Status |
|------|--------|-------------------|------------------|

## Velocity Analysis
- **Planned vs Completed** (across all sprints): [X/Y tasks = Z%]
- **Trend**: [Improving / Stable / Declining]
- **Adjusted estimate for remaining work**: [Days needed at current velocity]

## Scope Recommendations
### Protect (Must ship with milestone)
- [Feature and why]

### At Risk (May need to cut or simplify)
- [Feature and risk]

### Cut Candidates (Can defer without compromising milestone)
- [Feature and impact of cutting]

## Go/No-Go Assessment

**Recommendation**: [NOT ASSESSED / GO / CONDITIONAL GO / NO-GO]

**Conditions** (if conditional):
- [Condition 1 that must be met]
- [Condition 2 that must be met]

**Rationale**: [Explanation of the recommendation]

## Action Items
| # | Action | Owner | Deadline |
|---|--------|-------|----------|
```

---

## Phase 3b: Producer Risk Assessment

**Review mode 檢查** — 在派出 PR-MILESTONE 之前套用：
- `solo` → 跳過。註明：「PR-MILESTONE skipped — Solo mode.」呈現 Go/No-Go 章節，不附 producer 判定。
- `lean` → 跳過（它不是 PHASE-GATE）。註明：「PR-MILESTONE skipped — Lean mode.」呈現 Go/No-Go 章節，不附 producer 判定。
- `full` → 照常派出。

在產生 Go/No-Go 建議之前，用 `Agent` 派出 `producer`，使用 gate **PR-MILESTONE**（`.claude/docs/director-gates/pr-milestone.md`）。

傳入：milestone 名稱和目標日期、目前的完成百分比、blocked story 數量、sprint 報告裡的 velocity 資料（如果有的話）、可砍項目清單。

把 producer 的評估以行內方式呈現在 Go/No-Go 章節裡。producer 的判定（ON TRACK / AT RISK / OFF TRACK）會影響整體建議。

如果是 OFF TRACK，在產生建議之前用 `AskUserQuestion`：
- Prompt: "Producer verdict: OFF TRACK. The milestone is in jeopardy. This review will recommend NO-GO. How do you want to proceed?"
- Options:
  - `[A] Accept NO-GO — generate the full review with that recommendation`
  - `[B] Override to CONDITIONAL GO — I'll document the accepted risks myself`
  - `[C] Stop — I want to address blockers before generating the review`

如果是 AT RISK，用 `AskUserQuestion`：
- Prompt: "Producer verdict: AT RISK. Milestone may slip. How should the Go/No-Go section be framed?"
- Options:
  - `[A] CONDITIONAL GO — include producer's conditions in the review`
  - `[B] NO-GO — conditions cannot be met in time`
  - `[C] GO — I accept the risk and want to proceed`

如果是 NOT ASSESSED：點名缺少的輸入 — 它不是 ON TRACK，而且絕對不要在它上面建議 GO。補上輸入並重跑 PR-MILESTONE，或建議 NOT ASSESSED — 或是審查本身的發現需要時，建議 CONDITIONAL GO / NO-GO（排序見 `.claude/docs/director-gates.md`）。

不准在 OFF TRACK 的判定上發出 GO；只有在使用者明確選了上面的 [B] 時，才能發出 CONDITIONAL GO。

---

## Phase 4: Save Review

把審查呈現給使用者。

問：「May I write this to `production/milestones/[milestone-name]-review.md`?」

使用者答應就寫檔，目錄不存在的話先建立。Verdict: **COMPLETE** — milestone review saved.

如果不答應，就在這裡停下來。Verdict: **BLOCKED** — user declined write.

---

## Phase 5: Next Steps

- 如果這個 milestone 標記了某個開發階段的邊界，就執行 `/gate-check` 取得正式的 phase gate 判定。
- 依上面的範圍建議執行 `/sprint-plan`，調整下一個 sprint（在沒有 sprint 的 `workflow: minimal`，改調整 brief 的 build order）。
