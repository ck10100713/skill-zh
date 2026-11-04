---
name: sprint-plan
description: "根據目前的 milestone、已完成的工作和可用的產能，產出新的或更新後的 sprint 計畫。"
argument-hint: "[new|update|status] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, Bash(bash "*/.claude/skills/sprint-plan/../../hooks/yaml-helper.sh" resolve_config *), Bash(ls production/sprints/*)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,story_granularity,workflow`

上面已經解析完畢，直接用；`--review` 會覆寫 `review_mode`。沒有這個區塊的話，
預設值看 `.claude/docs/config-resolution.md`。

# Sprint Plan


## Existing Sprints

!`ls production/sprints/ 2>/dev/null || echo "(no production/sprints/ directory yet)"`

在這個 skill 執行之前就已經解析好了：用它在
Phase 1 找出上一個 sprint，不要重新 glob。

---

## Phase 0: Parse Arguments

擷取模式參數（`new`、`update` 或 `status`）。

完整的檢查模式見 `.claude/docs/director-gates.md`。個別 gate 的定義放在 `.claude/docs/director-gates/[gate-id].md`：被生成的 agent 自己會讀它自己的 gate 檔案；不要在父 session 裡讀它。


每一次 `AskUserQuestion` 呼叫都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律詢問 · guided 只問重大事項 · autonomous 記錄後直接進行；
屬於 `automation_always_ask` 的類別一律要詢問）。

**`story_granularity`**：它決定每個 sprint 要分配
多少個 story，並依 velocity 調整：`coarse`（預設，透過 `rigor: minimal`）是 **2–4** 個，
`balanced`（`rigor: standard`）是 **6–10** 個，`fine` 是 **15–25** 個。Ready 的 backlog
如果比這個範圍小，就整包都規劃進去，絕對不要用捏造的 story 去湊數。

**Review mode 檢查**（在 gate 執行之前）：
- 使用上面已解析區塊裡的 review mode（`--review` 在這次執行中會覆寫
  它）：不要重新解析，也不要去問它。什麼都沒設定時，它跟著 `modes.rigor`：
  `minimal` 時是 `solo`，`standard` 時是 `lean`。
- **絕對不要寫入 review mode**：不要寫到 `project.yaml`，也不要寫到
  `production/review-mode.txt`。`modes.review_mode` 是 `modes.rigor` 負責管理的設定之一：
  把它固定在 `project.yaml` 會遮蔽 rigor
  的展開，而舊版檔案位在那個展開*之上*，所以不管哪種寫入，
  都會永遠凍結 director 審查的深度。`--review` 涵蓋一次性的需求。如果
  使用者想要不同的深度並持續生效，指引他們去改
  `modes.rigor`（`/settings modes.rigor=<minimal|standard|full>`），或是有意地固定它：
  `/settings --local modes.review_mode=<full|lean|solo>`（在
  `project.local.yaml` 裡的個人覆寫）。

---

## Phase 1: Gather Context

1. **讀 `production/milestones/` 裡目前的 milestone**，**如果它存在的話**。
   沒有任何 skill 會寫這個目錄：它是依
   `.claude/docs/templates/milestone-definition.md` 手寫的。在大多數專案上
   它都不存在，這是正常狀態，不是缺口：記下 "no milestone
   defined — planning against the story backlog alone" 然後繼續。絕對不要因為它而擋住
   sprint 規劃，也絕對不要從 sprint 檔案推論出 milestone。

2. **讀上一個 sprint**（如果有的話），來自 `production/sprints/`，用來
   了解 velocity 和遞延項目。在 `new` 模式下：
   - 新 sprint 的編號 `[N]` 是 Existing Sprints 清單中最高的 `sprint-NNN.md`
     加一（沒有的話是 `001`）。它是計畫標題、它的 QA 計畫路徑和寫入詢問裡的
     `[N]`。
   - 上一個 sprint 中每個不是 `Complete` 的 story（依它在
     `production/sprint-status.yaml` 裡的狀態，否則依它 story 檔案的 Status 那一行），
     都放進 Carryover 表，附上 Reason 和 New Estimate。它只出現在
     那裡，絕對不會再當成新的 Must Have / Should Have / Nice to Have 工作出現。

3. **找出要規劃的 story**：這是真正的 backlog，也是這個階段
   少了就做不下去的唯一輸入：
   ```
   Glob production/epics/**/story-*.md
   Grep pattern="^> \*\*Status\*\*" glob="production/epics/**/story-*.md" output_mode="content"
   ```
   story 放在 `production/epics/[epic-slug]/story-NNN-[slug].md`：這是
   `/create-stories` 寫入的地方，也是 `/dev-story` 去找的地方。從
   標為 `Ready` 的 story 來規劃。用 grep，不要逐一讀每個 story：在這個
   階段你需要的是狀態和標題，不是內文。

   如果 glob 什麼都沒回傳："No stories found under `production/epics/`. Run
   `/create-stories` first (at `standard`/`full`, `/create-epics` before it)."
   不要繼續去捏造工作項目：一份引用不存在的 story 的 sprint 計畫，
   是沒辦法實作的。結論：**BLOCKED**，沒有 story 可規劃。

4. **掃描 `design/gdd/` 裡的設計文件**，取得這些 story 所實作功能的額外背景。
   每份都分段讀：用 Grep 工具（pattern `^#`、content mode）找出你需要的標題，再用 offset 和 limit
   讀那些範圍。在 `workflow: minimal` 時沒有
   各系統的 GDD：改用 `design/game-brief.md`，而且不要把沒有的
   GDD 當成缺少的工作。（註：`/sprint-plan` 在
   `minimal` 時是**選用的**：brief 的 Build order 本身就是計畫。）

5. **檢查 `production/risk-register/` 的風險登記冊**，**如果它存在的話**。
   跟上面的 milestone 一樣，沒有任何 skill 會寫它：條目是依
   `.claude/docs/templates/risk-register-entry.md` 手寫的。如果目錄
   不存在，要說一次（"no risk register — risks assessed from the sprint
   contents only"），不要默默跳過風險評估。

---

## Phase 2: Generate Output

對 `new`：

**依這個格式產生 sprint 計畫**，並呈現給使用者。先不要問要不要寫入：gate 階段會先執行，而且可能要在寫檔之前先修改：producer 可行性 gate（Phase 4，只在 `full` review mode 生成，`lean`/`solo` 會跳過）和 QA 計畫檢查（Phase 5，所有模式）。

```markdown
# Sprint [N] — [Start Date] to [End Date]

## Sprint Goal
[One sentence describing what this sprint achieves toward the milestone]

## Goal Prerequisites
| Needed to show the goal | Status |
|-------------------------|--------|

## Capacity
- Total days: [X]
- Buffer (20%): [Y days reserved for unplanned work]
- Available: [Z days]

## Tasks

### Must Have (Critical Path)
| ID | Task | Agent/Owner | Est. Days | Dependencies | Acceptance Criteria |
|----|------|-------------|-----------|-------------|-------------------|

### Should Have
| ID | Task | Agent/Owner | Est. Days | Dependencies | Acceptance Criteria |
|----|------|-------------|-----------|-------------|-------------------|

### Nice to Have
| ID | Task | Agent/Owner | Est. Days | Dependencies | Acceptance Criteria |
|----|------|-------------|-----------|-------------|-------------------|

## Carryover from Previous Sprint
| Task | Reason | New Estimate |
|------|--------|-------------|

## Risks
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|

## Dependencies on External Factors
- [List any external dependencies]

## Definition of Done for this Sprint
- [ ] All Must Have tasks completed
- [ ] All tasks pass acceptance criteria
- [ ] QA plan exists (`production/qa/qa-plan-[sprint-slug]-[date].md`, from `/qa-plan sprint`)
- [ ] All Logic/Integration stories have passing unit/integration tests
- [ ] Smoke check passed (`/smoke-check sprint`)
- [ ] QA sign-off report: APPROVED or APPROVED WITH CONDITIONS (`/team-qa sprint`)
- [ ] No S1 or S2 bugs in delivered features
- [ ] Design documents updated for any deviations
- [ ] Code reviewed and merged
```

### Check the goal's prerequisites

在你呈現 `new` 計畫之前，先檢查它的目標能不能在
sprint 結束前被展示出來。一個目標可能需要沒有任何 story 去建的東西：playtest
需要有場景可以跑。這項檢查只回報，絕對不擋。它不會自己新增問題，
也不會新增 story。

1. **確定目標。** 如果有 milestone，就引用它的目標；否則
   根據挑選的 story 寫一句話。
2. **列出展示它需要什麼。** 玩家看得到或玩得到的目標（可玩的
   循環、端到端運作的功能、playtest）需要它
   執行所在的場景或關卡，以及啟動它的設定：`project.godot` 裡的 `run/main_scene`、
   Unity 的 `ProjectSettings/EditorBuildSettings.asset` 裡的場景清單，或
   Unreal 的 `Config/DefaultEngine.ini` 裡的 `GameDefaultMap`。再加上任何
   被挑選的 story 的驗收條件、備註或依賴所點名、但沒有任何挑選的 story 去建立的檔案、場景
   或系統。沒有東西可以跑或展示的目標（只有邏輯
   和測試）就不需要。
3. **逐一檢查。** 當它已經存在專案裡，或有挑選的 story 會建它時，就算涵蓋。
   依引擎的場景檔找場景（`project.yaml` 裡的 `engine.name`）：
   Godot 是 `*.tscn`，Unity 是 `Assets/**/*.unity`，
   Unreal 是 `Content/**/*.umap`。其他東西依 story
   使用的路徑或名稱去找。如果沒有設引擎，就只依名稱檢查，並說明場景搜尋
   沒有執行。
4. **填入 Goal Prerequisites 段落**：每一項需求寫上 `exists`、
   `built by [story ID]` 或 **missing**，或是只有一列 "None: the goal has
   nothing to run or show"。把每個 missing 的複製進 Risks。呈現
   計畫時，點名每個 missing 的，以及使用者可選的三種修正方式：
   把會建它的 Ready story 拉進來（點名它，並說明這樣會不會讓 sprint 超出
   它的 `story_granularity` 範圍，或是需要它所依賴的 story），先用 `/create-stories`
   為它寫一個 story，或是改寫目標，只承諾 sprint 能展示的東西。把它們當作計畫的一部分給出去，
   不要當作問題：寫入詢問仍然是唯一的問題，
   想要修正的使用者會在回覆它時說出來。**回報缺口，不要去解決它。**
   缺少的前置條件在這份計畫裡仍然是缺少的，不管它看起來多小（
   一個平坦的測試關卡、一個 input map）：不要為它規劃任何任務，也不要把它的任何工作
   放進挑選的 story，連當作設定也不行。它的工作要先有 story，
   那是 `/create-stories` 的工作。絕對不要新增 backlog 裡
   沒有的 story，也絕對不要為了涵蓋缺口去擴大挑選的 story 或編輯 story 檔案。

對 `update`：

**更新既有的 sprint 計畫**：

1. 從 `production/sprints/` 讀最近的 sprint 計畫。
2. 呈現目前的 story 清單，以及它們在 `production/sprint-status.yaml` 裡目前的狀態。
3. 問使用者要改什麼：要新增、移除、重新排序優先順序或重新估算的 story。用 `AskUserQuestion` 收集改動。
4. 套用改動，並重新呈現完整的修訂後計畫供審閱。如果
   目標或 Must Have 的 story 有改變，先重新檢查目標的前置條件。
5. 對修訂後的計畫重跑 producer 可行性 gate（Phase 4）。
6. 把更新後的 markdown 計畫和 yaml 一起寫入（跟 `new` 模式相同的核准）。

註：`update` 模式不會重置 story 狀態。已經標為 `in-progress` 或 `done` 的 story 保留它們的狀態。只有 `backlog` 和 `ready-for-dev` 的 story 可以自由移除或重新排序優先順序。

對 `status`：

**產生狀態報告**：

```markdown
# Sprint [N] Status -- [Date]

## Progress: [X/Y tasks complete] ([Z%])

### Completed
| Task | Completed By | Notes |
|------|-------------|-------|

### In Progress
| Task | Owner | % Done | Blockers |
|------|-------|--------|----------|

### Not Started
| Task | Owner | At Risk? | Notes |
|------|-------|----------|-------|

### Blocked
| Task | Blocker | Owner of Blocker | ETA |
|------|---------|-----------------|-----|

## Burndown Assessment
[On track / Behind / Ahead]
[If behind: What is being cut or deferred]

## Emerging Risks
- [Any new risks identified this sprint]
```

---

## Phase 3: Prepare Sprint Status File

產生新的 sprint 計畫之後，也要準備 `production/sprint-status.yaml` 的內容。
這是 story 狀態的機器可讀事實來源：`/sprint-status`、`/story-done` 和 `/help`
不用解析 markdown 就能讀它。

**先不要寫 yaml**：把它留在 context 裡。producer 可行性 gate（Phase 4，只在 `full` review mode）可能會修改 story 清單；QA 計畫檢查（Phase 5）在每種模式都會跑。兩個檔案會在 Phase 5 之後，用單一一次的寫入核准一起寫入。

格式：

```yaml
# Auto-generated by /sprint-plan. Updated by /story-done and /dev-story.
# DO NOT edit manually — use /story-done to update story status.
#
# Status value mapping (yaml ↔ story file Status field):
#   backlog        ↔  Not Started
#   ready-for-dev  ↔  Ready
#   in-progress    ↔  In Progress
#   review         ↔  In Review
#   done           ↔  Complete
#   blocked        ↔  Blocked

sprint: [N]
goal: "[sprint goal]"
start: "[YYYY-MM-DD]"
end: "[YYYY-MM-DD]"
generated: "[YYYY-MM-DD]"
updated: "[YYYY-MM-DD]"

stories:
  - id: "[epic-story, e.g. 1-1]"
    name: "[story name]"
    file: "[production/epics/[epic-slug]/story-NNN-[slug].md]"   # the real path, verbatim from the Glob above
    priority: must-have        # must-have | should-have | nice-to-have
    status: ready-for-dev      # backlog | ready-for-dev | in-progress | review | done | blocked
    owner: ""
    estimate_days: 0
    blocker: ""
    completed: ""
```

從 sprint 計畫的任務表初始化每個 story：
- Must Have 任務 → `priority: must-have`、`status: ready-for-dev`
- Should Have 任務 → `priority: should-have`、`status: backlog`
- Nice to Have 任務 → `priority: nice-to-have`、`status: backlog`
- Carryover 的列 → story 之前的 `priority`，以及它現在的 `status`

對 `update`：讀既有的 `sprint-status.yaml`，沿用沒有改變的
story 的狀態，加入新的 story，移除被捨棄的。

---

## Phase 4: Producer Feasibility Gate

**Review mode 檢查**：在生成 PR-SPRINT 之前套用：
- `solo` → 跳過。註記："PR-SPRINT skipped — Solo mode." 繼續到 Phase 5（QA 計畫 gate）。
- `lean` → 跳過（它不是 PHASE-GATE）。註記："PR-SPRINT skipped — Lean mode." 繼續到 Phase 5（QA 計畫 gate）。
- `full` → 照常生成。

在定案 sprint 計畫之前，用 `Agent` 以 gate **PR-SPRINT**（`.claude/docs/director-gates/pr-sprint.md`）生成 `producer`。

傳入：提議的 story 清單（標題、估算、依賴）、以小時/天計的團隊總產能、上一個 sprint 的任何遞延項目、milestone 的限制和截止日期，以及任何缺少的目標前置條件。

呈現 producer 的評估。

如果是 UNREALISTIC：修改 story 的選擇（把 story 延後到 Should Have 或 Nice to Have），並重新呈現更新後的計畫，然後繼續到 Phase 5。

如果是 NOT ASSESSED：點名缺少的輸入，它不等於 REALISTIC。補上它並重跑 PR-SPRINT，或是在計畫的標頭裡為 PR-SPRINT 記錄 `NOT ASSESSED — [missing input]`（`.claude/docs/director-gates.md`），然後繼續到 Phase 5，並在寫入詢問時重複說明。

如果是 CONCERNS，用 `AskUserQuestion`：
- Prompt："Producer flagged concerns with this sprint plan. How do you want to proceed?"
- Options：
  - `[A] Proceed as planned — I accept the risk`
  - `[B] Adjust scope — defer some Should Have stories`
  - `[C] Extend the sprint timeline`

如果是 [A]：繼續到 Phase 5。
如果是 [B]：修改 story 清單，重新呈現更新後的計畫，然後繼續到 Phase 5。
如果是 [C]：調整 sprint 日期和產能，重新呈現更新後的計畫，然後繼續到 Phase 5。

處理完 producer 的結論之後，繼續到 Phase 5。寫入發生在
它的結尾，所以你核准的檔案已經包含 Phase 5 加進去的所有東西。

---

## Phase 5: QA Plan Gate

在結束 sprint 計畫之前，檢查這個 sprint 有沒有 QA 計畫。

對 `production/qa/qa-plan-*.md` 用 `Glob`（`/qa-plan` 寫的是 `qa-plan-[sprint-slug]-[date].md`），並保留名稱或內容有引用這個 sprint 編號的檔案。

**如果找到 QA 計畫**：在 sprint 計畫的輸出裡註記，"QA Plan: `[path]`"，然後繼續。

**如果沒有 QA 計畫**：不要默默繼續。要明確地提出來：

> "This sprint has no QA plan. A sprint plan without a QA plan means test requirements are undefined — developers won't know what 'done' looks like from a QA perspective, and the sprint cannot pass the Production → Polish gate without one.
>
> Run `/qa-plan sprint` now, before starting any implementation. It takes one session and produces the test case requirements each story needs."

用 `AskUserQuestion`：
- Prompt："No QA plan found for this sprint. How do you want to proceed?"
- Options：
  - `[A] Run /qa-plan sprint now — I'll do that before starting implementation (Recommended)`
  - `[B] Skip for now — I understand QA sign-off will be blocked at the Production → Polish gate`

等這個答案出來，才進行下面的寫入詢問：這是兩個獨立的問題。
這裡的回答絕對不是寫入的核准，即使是 "yes, go ahead" 或 "once the plan is written"：
接著問寫入的問題，只有在對它回答 yes 之後才寫。

如果是 [A]：在計畫裡註記 "QA plan: run `/qa-plan sprint` before implementation begins."
如果是 [B]：在 sprint 計畫文件加上一個警告區塊：

```markdown
> ⚠️ **No QA Plan**: This sprint was started without a QA plan. Run `/qa-plan sprint`
> before the last story is implemented. The Production → Polish gate requires a QA
> sign-off report, which requires a QA plan.
```

### Write the plan

詢問："May I write the sprint plan to `production/sprints/sprint-NNN.md` (`[N]` zero-padded to three digits) and
`production/sprint-status.yaml`?" 即使先前的回答聽起來像是 yes，也要問。如果同意，就寫入兩個檔案（需要時建立目錄）。結論：**COMPLETE**，sprint 計畫和狀態檔案已建立。如果不同意：
結論：**BLOCKED**，使用者拒絕寫入。

寫完之後，補上：

> **Scope check:** If this sprint includes stories added beyond the original epic scope, run `/scope-check [epic]` to detect scope creep before implementation begins.

如果使用者在 Phase 5 選了 `Run /qa-plan sprint now`，就以 "Sprint plan written. Run `/qa-plan sprint` next — then begin implementation." 結尾。

---

## Phase 6: Next Steps

sprint 計畫寫完、QA 計畫的狀態也解決之後：

- `/qa-plan sprint`：**開始實作之前必須做**，它為每個 story 定義測試案例，讓開發者依 QA 規格去實作，而不是面對一張白紙
- `/story-readiness [story-file]`：在開始一個 story 之前，驗證它是否準備好了
- `/dev-story [story-file]`：開始實作第一個 story
- `/sprint-status`：sprint 中途檢查進度
- `/scope-check [epic]`：在實作開始之前，確認沒有範圍蔓延

**Review mode 設定：** 所有 director gate（producer 可行性、QA 審查、程式碼審查）都遵守專案的 review mode，它在這個 skill 最上面的區塊解析（`--review` 旗標 → `project.local.yaml` → `project.yaml` 的 `modes.review_mode` → `production/review-mode.txt` → `modes.rigor` 展開，在 standard rigor 下得到 `lean`，在 minimal 下得到 `solo`）。這個 skill 絕對不會去問它，也不會寫它；Phase 0 說明了想要不同深度的使用者該指向哪裡。模式是以下之一：
- `lean`：跳過非 phase-gate 的 director gate（`rigor: standard` 的值）
- `full`：以生成的 sub-agent 執行所有 director gate
- `solo`：無條件跳過所有 gate 的生成（單一開發者，不審查）

`project.yaml` 裡的 `modes.review_mode` 是主要來源；`production/review-mode.txt` 是舊版的備援。`/sprint-plan`、`/story-readiness`、`/story-done` 和其他使用 gate 的 skill 在啟動時都會讀這兩者。
