---
name: qa-plan
description: "替一個 sprint 產出 QA 測試計畫：把 story 分成 Logic/Integration/Visual/UI，涵蓋自動化測試、手動案例和 smoke 範圍。"
argument-hint: "[sprint | feature: system-name | story: path]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(bash "*/.claude/skills/qa-plan/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation,workflow,qa.level,system_overrides`

上面已經解析好了，直接用。沒有這個區塊的話，用
`.claude/docs/config-resolution.md` 裡的預設值。


# QA Plan

這個 skill 會替一個 sprint、feature 或單一
story 產生結構化的 QA 計畫。它會讀所有在範圍內的 story 檔和它們參照的 GDD，
依測試類型替每個 story 分類，並產出一份計畫，明確告訴開發者
哪些要自動化、哪些要手動驗證、smoke test 的範圍是什麼，以及什麼時候
該找 playtester 來。

在 sprint 開始前執行，讓團隊一開始就知道需要做哪些測試
工作。實作之後才寫的測試計畫是事後檢討，不是
計畫。

**輸出：** `production/qa/qa-plan-[sprint-slug]-[date].md`

---

每一次 `AskUserQuestion` 呼叫都遵循 `.claude/docs/automation-modes.md`
（collaborative 一律問 · guided 只問重大的 · autonomous 只記錄然後繼續；
`automation_always_ask` 的類別一律要問）。

**Workflow tier**：讀每個 GDD 時，依它所屬的 system 解析
（依 `.claude/docs/workflow-modes.md`）：如果 `workflow_overrides.system_overrides.<system>`
區塊有列出就用它，否則用專案的值。它決定測試計畫要從多少個 GDD 章節
去挖掘 — 見 Phase 2。

**`qa.level`**：在 `minimal`，只產出最精簡的 smoke
計畫 — 拿掉要求自動化測試的那幾列和測試檔的 DoD；在 `standard`，
依每個 story 類型產出完整計畫；在 `full`，再加上每個 system 的覆蓋率目標。
這是跟 `workflow`（決定要挖掘多少個 GDD 章節）不同的軸。
沒有任何等級會拿掉 Visual/Feel 和 UI 的截圖那幾列 — 測試在
`minimal` 是豁免的，外觀不是（`.claude/docs/coding-standards.md`）。

## Phase 1: Parse Scope

**參數：** `$ARGUMENTS`（留白 = 用 AskUserQuestion 問使用者）

從參數判斷範圍：

- **`sprint`** — 讀 `production/sprints/` 裡最新的檔案，擷取
  被參照的每個 story 檔路徑。如果 `production/sprint-status.yaml` 存在，
  就用它當主要的 story 清單，story 的 metadata 再退回去讀 sprint plan。
- **`feature: [system-name]`** — 用 glob 找 `production/epics/*/story-*.md`，篩選
  檔案路徑或標題包含該 system 名稱的 story。也檢查那個 system 目錄裡的
  epic 索引檔（`EPIC.md`）。
- **`story: [path]`** — 驗證路徑存在，並載入那一個檔案。
- **沒有參數** — 使用 `AskUserQuestion`：
  - "What is the scope for this QA plan?"
  - Options："Current sprint"、"Specific feature (enter system name)"、
    "Specific story (enter path)"、"Full epic"

解析完範圍之後，回報：「Building QA plan for [N] stories in [scope].」

如果有 story 檔路徑被參照，但檔案不存在，就把它記為
MISSING 並繼續處理其餘的 story。不要因為
一個缺少的檔案就讓整份計畫失敗。

> **如果解析出來的範圍包含零個 story，就停下來 — 不要建立計畫。**
> 回報 `NOT ASSESSED — no stories in scope`，點名搜尋的是哪個範圍、
> 哪個路徑是空的，並指引下一步：
> - `production/sprints/` 裡沒有檔案 →「No sprint plan found. Run `/sprint-plan new`.」
>   在 `workflow: minimal` 依設計就沒有 sprint — 改指引到
>   `/qa-plan feature: [epic-slug]` 或 `/qa-plan story: [path]`。
> - sprint plan 存在但沒有參照任何 story →「Sprint plan `[path]` lists no
>   stories. Run `/create-stories [epic-slug]`.」
> - `feature:`/`story:` 範圍沒符合任何東西 → 點名回傳空的那個 glob。
>
> **N=0 的防護是強制的。** 沒有它，空的範圍會回報「Building QA
> plan for 0 stories」並繼續進 Phase 4，產出一份表格都是空的計畫文件 — 
> 而**零個 story 的 QA 計畫，看起來跟完成的 QA 計畫一模一樣。**
> 這個 skill 把關著交給手動 QA 的交接，所以這裡的假乾淨，
> 會讓 build 憑著一份什麼都沒測的計畫就被送去 QA。
>
> 這個區塊最上面的規則仍然有效：好幾個裡面缺一個檔案，是 MISSING 然後繼續。
> 這是另一種情況，就是根本沒有*好幾個*。

---

## Phase 2: Load Inputs

先確立分母 — 用 glob 找出範圍內的 story 檔並計算 **N** —
然後用**針對章節的 grep 來蒐集下面的欄位，不要整份讀完
每個 story**。QA 計畫需要每個 story 的類型和驗收條件；
它不需要實作備註、Out-of-scope 的邊界或 ADR 的理由，
而為了拿到兩個章節就把 N 個 story 整份讀完，正是這個階段成本的所在：

```
Grep pattern="^## Acceptance Criteria" glob="production/epics/**/story-*.md" output_mode="content" -A 15
Grep pattern="^> \*\*(Type|Status|Estimate)\*\*" glob="production/epics/**/story-*.md" output_mode="content"
Grep pattern="^## (Context|Dependencies)" glob="production/epics/**/story-*.md" output_mode="content" -A 8
```

（在 `sprint` 模式下，把 glob 縮小到 sprint plan 的 story 路徑。）從這些取得：

- **Story 標題**和 story ID — 從檔名和路徑取得；完全不用讀檔
- **Story Type** 欄位 — 從標頭的 grep 取得（例如 `Type: Logic`）
- **驗收條件** — 完整的編號/條列清單，從第一個 grep 取得
- **GDD / ADR 參照**和 **Dependencies** — 從 `## Context` 的 grep 取得
- **Estimate** — 如果有的話，從標頭的 grep 取得
- **Implementation files** 和 **Engine notes** — 只有測試計畫
  真的取決於它們的 story 才需要；那些個別的 story 才整份讀

**絕對不要把缺少的章節當成缺少的 story。** 如果某個 story 沒有符合
`## Acceptance Criteria`，就整份讀那一個並說明 — 沒有
可測試條件的 story，本身就是 QA 的發現，不是要跳過的 story。

讀完 story 之後，一次載入支援的脈絡（不是每個 story 各一次）：

- `design/gdd/systems-index.md` — 了解 system 的優先順序，以及哪些
  GDD 已核准
- 對所有 story 之間參照到的每個不重複的 GDD：依該
  system 的 workflow tier（上面解析出來的）去挖掘測試素材 — 在 `full`，挖掘全部 8 個章節；在
  `standard`，挖掘必要章節中跟測試有關的子集
  （**Acceptance Criteria** 和 **Edge Cases** 一律要，再加上任何定義了數值規則的
  system 的 **Formulas**）；在 `minimal`，**只有 Acceptance
  Criteria**。不要載入完整的 GDD
  文字。用 Grep 工具（pattern `^#`，content mode）找出章節標題，再用 offset 和 limit 讀
  那幾段範圍。這些章節包含可測試的需求、要驗證的
  數學，以及測試必須涵蓋的邊界條件。如果沒有 Edge Cases 章節（或
  在 minimal 本來就不預期有），就針對每個 GDD 註明：「No Edge Cases section found — edge case
  coverage will be inferred from acceptance criteria only.」
- `docs/architecture/control-manifest.md` — 如果檔案存在，掃描
  自動化測試應該防範的禁用模式

如果某個 story 沒有參照任何 GDD，就把它記為缺口，但不要擋住計畫。
這個 story 只用驗收條件來分類。

---

## Phase 3: Classify Each Story

替每個 story 指派一個 Story Type：

- **如果 story 的標頭已經有 `Type:` 欄位**：照單全收。不要重新分類，也不要對照下面的條件去驗證 — Type 是 lead-programmer 在建立 story 時設定的，具有權威性。照原樣記錄。
- **如果缺少 `Type:` 欄位**：用下表從驗收條件推斷類型，並在報告裡註明類型是推斷的（不是宣告的）。把這標記成缺口 — story 在開始實作之前，應該明確宣告它的 Type。

| Story Type | Classification Indicators |
|---|---|
| **Logic** | Acceptance criteria reference calculations, formulas, numerical thresholds, state transitions, AI decisions, data validation, buff/debuff stacking, economy transactions, or any testable computation |
| **Integration** | Criteria involve two or more systems interacting, signals or events propagating across system boundaries, save/load round-trips, network sync, or persistence |
| **Visual/Feel** | Criteria reference animation behaviour, VFX, shader output, "feels responsive", perceived timing, screen shake, particle effects, audio sync, or visual feedback quality |
| **UI** | Criteria reference menus, HUD elements, buttons, screens, dialogue boxes, inventory panels, tooltips, or any player-facing interface element |
| **Config/Data** | Changes are limited to balance tuning values, data files, or configuration — no new code logic is involved |

**混合型 story**（例如同時加了公式和 UI 顯示的 story）：
依哪些驗收條件的實作風險最高來指派主要類型，並註明次要類型。
Logic+Integration 或 Visual+UI 的組合最常見。

替所有 story 分類之後，在進入 Phase 4 之前，先在對話中產出一張分類摘要表。
這讓使用者看得到測試會怎麼分配。

---

## Phase 4: Generate Test Plan

組出完整的 QA 計畫文件。使用這個結構：

````markdown
# QA Plan: [Sprint/Feature Name]
**Date**: [date]
**Generated by**: /qa-plan
**Scope**: [N stories across [N systems]]
**Engine**: [engine name — `engine.name` from project.yaml if present and non-empty, else the Engine field from .claude/docs/technical-preferences.md, else "Not configured"]
**Sprint File**: [path to sprint plan if applicable]

---

## Test Summary

| Story | Type | Automated Test Required | Manual Verification Required |
|-------|------|------------------------|------------------------------|
| [story title] | Logic | Unit test — `tests/unit/[system]/` | None |
| [story title] | Integration | Integration test — `tests/integration/[system]/` | Smoke check |
| [story title] | Visual/Feel | None (not automatable) | Screenshot + lead sign-off |
| [story title] | UI | None (verified by its screenshots) | Retained screenshot of each screen touched |
| [story title] | Config/Data | Data validation test | Spot-check in-game values |

---

## Automated Tests Required

*(At `qa.level: minimal`, omit this entire section and blank the Test Summary's
"Automated Test Required" column — automated tests are not required there; list
manual/smoke verification only.)*

### [Story Title] — [Type]
**Test file path**: `tests/[unit|integration]/[system]/[story-slug]_test.[ext]`
**What to test**:
- [Specific formula or rule from the GDD Formulas section]
- [Each named state transition or decision branch]
- [Each side effect that should or should not occur]

**Edge cases to cover**:
- Zero/minimum input values (e.g., 0 damage, empty inventory)
- Maximum/boundary input values (e.g., max level, stat cap)
- Invalid or null input (e.g., missing target, dead entity)
- [Any edge case explicitly called out in the GDD Edge Cases section]

**Estimated test count**: ~[N] unit tests

[If no GDD formula reference was found for this story, note:]
*No formula found in referenced GDD — test cases must be derived from acceptance
criteria directly. Review the GDD Formulas section before writing tests.*

---

## Manual QA Checklist

### [Story Title] — [Type]
**Verification method**: [Screenshot + designer sign-off | Playtest session |
Manual step-through | Comparison against reference footage]
**Who must sign off**: [designer / lead-programmer / qa-lead / art-director]
**Evidence to capture**: [screenshot of X | video clip of Y | written playtest
notes | side-by-side comparison]

Checklist:
- [ ] [Specific observable condition — concrete and falsifiable]
- [ ] [Another condition]
- [ ] [Every acceptance criterion translated into a manual check item]

*If any criterion uses subjective language ("feels", "looks", "seems"), it must
be supplemented with a specific benchmark or a playtest protocol note.*

---

## Smoke Test Scope

Critical paths to verify before any QA hand-off for this sprint:

1. Game launches to main menu without crash
2. New game / new session can be started
3. [Primary mechanic introduced or changed this sprint]
4. [Any system with a regression risk from this sprint's changes]
5. Save / load cycle completes without data loss (if save system exists)
6. Performance is within budget on target hardware (no new frame spikes)

*Smoke tests are verified by the developer via `/smoke-check`. Reference this
list when running that skill.*

---

## Playtest Requirements

| Story | Playtest Goal | Min Sessions | Target Player Type |
|-------|--------------|--------------|-------------------|
| [story] | [What question must the session answer?] | [N] | [new player / experienced] |

**Sign-off requirement**: Playtest notes must be written with `/playtest-report` to
`production/qa/playtests/` (naming the story) and reviewed by
the [designer / qa-lead] before the story can be marked COMPLETE.

If no stories require playtest validation: *No playtest sessions required for
this sprint.*

---

## Definition of Done — This Sprint

A story is DONE when ALL of the following are true (at `qa.level: minimal`, drop
the test-file and smoke rows below — tests are waived there; the screenshot and
sign-off rows stay at every level, because the look is not):

- [ ] All acceptance criteria verified — via automated test result OR documented
      manual evidence (screenshot, video, or playtest notes with sign-off)
- [ ] Test file exists at the specified path for all Logic and Integration stories *(qa.level standard/full)*
- [ ] Retained screenshot of each screen touched, in `production/qa/evidence/`, for all Visual/Feel and UI stories *(every qa.level)*
- [ ] Signed-off evidence doc at `production/qa/evidence/[story-slug]-evidence.md` for all Visual/Feel stories *(every qa.level)*
- [ ] Smoke check passes (run `/smoke-check sprint` before QA hand-off) *(qa.level standard/full)*
- [ ] No regressions introduced
- [ ] Code reviewed (via `/code-review` or documented peer review)
- [ ] Story file updated to `Status: Complete` (via `/story-done`)
````

產生內容時，使用 Phase 2 擷取到的實際 story 標題、GDD 公式文字和
驗收條件。不要用 placeholder 文字 — 每個
測試條目都應該反映這些特定 story 的真實需求。

---

## Phase 5: Write Output

在對話中顯示完整計畫（計畫很長的話就顯示摘要），
然後用 `AskUserQuestion` 一次問兩個問題：

```
question: "Ready to write the QA plan. Choose output options:"
multiSelect: true
options:
  - "Write QA plan to production/qa/qa-plan-[sprint-slug]-[date].md"
  - "Also back-fill test case specs into each story file's ## QA Test Cases section (Recommended — enables /dev-story and /code-review traceability)"
```

如果選了「Write QA plan」：照產生的樣子寫入計畫檔 — 不要截斷。

如果選了「Also back-fill story files」：對範圍內的每個 Logic 和 Integration story，編輯它路徑上的 story 檔。找到 `## QA Test Cases` 章節，把它的內容換成 Phase 4 替那個 story 產生的測試案例規格。如果 story 沒有 `## QA Test Cases` 章節，就把它附加在 `## Test Evidence` 之前。對 Visual/Feel 和 UI 的 story，改寫手動驗證步驟，不要寫測試規格。

寫完之後：

"QA plan written to `production/qa/qa-plan-[sprint-slug]-[date].md`.

Next steps:
- Share this plan with the team before sprint implementation begins
- Once all sprint stories are implemented, run `/smoke-check sprint` to gate QA hand-off — not yet, only after implementation is complete
- For Logic/Integration stories, create the test files at the listed paths
  before marking stories done — `/story-done` checks for them"

默默附加到 `production/session-state/active.md`（檔案不存在就建立）：

```
<!-- QA-PLAN: [date] | System: [system/sprint identifier] | Plan written: production/qa/qa-plan-[identifier]-[date].md -->
```

以判定收尾：**COMPLETE** — QA plan written（如果寫入被拒絕，則是 **COMPLETE** — QA plan
shown, not written）。唯一的另一種結果，是 Phase 1 裡的
`NOT ASSESSED — no stories in scope` 路徑。

---

## Collaborative Protocol

**適用於 `collaborative` 模式（預設）。** `guided` 和
`autonomous` 模式請見 `.claude/docs/automation-modes.md` — 下面的規則
描述的是 collaborative 模式的要求，不是通用行為。

- **沒問就絕對不要寫計畫** — Phase 5 需要明確的核准。
- **分類要保守**：當 story 在 Logic 和
  Integration 之間模稜兩可時，分類成 Integration — 它需要單元測試和
  整合測試兩者。
- **不要憑空發明測試案例**，超出驗收條件和 GDD 公式
  能支持的範圍。如果 GDD 裡沒有公式，就標記出來，不要猜。
- **Playtest 需求只是建議**：邊界的 Visual/Feel story 要不要做 playtest，由使用者決定。
  標出這個情況；不要強制。
- 沒有給參數時，用 `AskUserQuestion` 選擇範圍。
  其他所有階段都保持非互動 — 呈現發現，然後問一次
  是否核准寫入。
