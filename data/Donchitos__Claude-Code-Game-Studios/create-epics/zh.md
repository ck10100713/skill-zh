---
name: create-epics
description: "把 GDD 和架構拆成 epic，每個架構模組一個。使用者想把遊戲拆成 epic，或在寫 story 之前先規劃工作時使用。不適用於把單一 epic 拆成 story。"
argument-hint: "[system-name | layer: foundation|core|feature|presentation | all] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, Bash(bash "*/.claude/skills/create-epics/../../hooks/yaml-helper.sh" resolve_config *), Bash(bash .claude/scripts/gdd-structure-check.sh*), Bash(bash .claude/scripts/adr-status.sh*), Bash(bash .claude/scripts/md-section.sh *), Bash(bash .claude/scripts/write-guard.sh overwrite *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,review_gate,automation,workflow,docs.density,engine_values,system_overrides`

上面已經解析好了，直接用；`--review` 會覆蓋 `review_mode`。沒有這個區塊 →
用 `.claude/docs/config-resolution.md` 裡的預設值。

提問要用提問工具。沒有的話，把選項編號列出來，然後結束你這一輪
等回覆。被跳過或被關掉的問題不算回答：用純文字再問一次。

# Create Epics

epic 是針對一個架構模組的一包有界限的工作：**做什麼**，
以及由哪些決策主導。怎麼做是 story 的事。每當開發推進到某一層時，
就針對那一層跑一次：Core 快做完之前就寫好的 Feature epic，
描述的是一個之後會變掉的設計。

**寫入：** 每個 epic 一份 `production/epics/[epic-slug]/EPIC.md`，以及它在
`production/epics/index.md` 的那一列，各自在它自己的 yes 之後寫。
**下一步：** 每個 epic 跑 `/create-stories [epic-slug]`。這個 skill 絕對不寫 story。

提問遵循 `.claude/docs/automation-modes.md`（collaborative 一律會問、guided
遇到重大選擇才問、autonomous 記錄後繼續；`automation_always_ask`
的類別一律要問）。

檢查清單（複製下來，邊做邊打勾）：

```
- [ ] Phase 1: scope and tier
- [ ] Phase 2: inputs loaded and reported
- [ ] Phase 3: each epic shown, "Shall I create Epic: …?" asked one at a time
- [ ] Phase 4: producer review run, or its skip noted
- [ ] Phase 5: each EPIC.md and index row written after its own yes
- [ ] Phase 6: closing block printed
```

## Phase 1: 範圍與 tier

skill 名稱後面輸入的文字，把任何 `--review <mode>` 組合拿掉之後：

- `all`：每個系統，依分層順序。
- `layer: foundation`（或 `core`、`feature`、`presentation`）：只做那一層。
- 一個系統名稱：只做那個系統。
- 什麼都沒有：要求本身的字句如果有指名分層或系統（「foundation
  and core」）就用它；否則問 "Which layer or system would you like epics for?"

**Tier。** 專案的 `workflow` 值決定什麼是必要的（Phase 2）。每個
範圍內系統自己的 GDD 門檻，如果它有 `system_overrides` 那一列，就來自那一列。

**在 `minimal`，先告訴使用者：** 這一步在這個 tier 是選用的，因為
`/create-stories` 會自己從 `design/game-brief.md` 建立 epic。如果他們要求了 epic，
再繼續。

## Phase 2: 載入輸入

### `minimal`：brief

讀 `design/game-brief.md`。沒有的話就停："No `design/game-brief.md` — run `/start`
or `/brainstorm` first." 絕對不要要 GDD、systems index、架構
文件、ADR、TR registry 或 control manifest，也絕對不要叫使用者先去
跑 `/design-system`、`/map-systems` 或 `/create-architecture`：這個 tier 依設計
就沒有這些東西。

先回報，一字不差：

```
Loaded: design/game-brief.md · engine [name version from the engine_values line]
At minimal this step is optional: /create-stories builds the epic from the brief by itself.
```

epic 來自 brief 的 MVP 功能清單，依它的 **Build order**。短的
brief 就是一個 epic，slug 取自 brief 的 working title（沒輸入任何東西時，
`/create-stories` 用的那個 slug）。當使用者要求分組時，每組一起交付的 MVP 功能
做一個 epic。每個 epic 都要寫出它的 slug，因為 `/create-stories` 需要把它打出來。

### `standard` 和 `full`：設計與架構

1. **系統 GDD。** `bash .claude/scripts/gdd-structure-check.sh` 會列出每份系統
   GDD；遊戲概念、systems index、pillars、交叉審查，以及其他
   非系統的文件，已經替你排除了。它們的數量是 **N**。N 是 0：停，
   "No system GDDs found in `design/gdd/` — run `/design-system` first."
2. **什麼在範圍內。** 每份 GDD 的 `## Summary` 速查表給出它的分層和
   優先度。沒有 Summary 的 GDD（較舊的 GDD 早於它）從
   `design/gdd/systems-index.md` 取得它的分層。絕對不要把沒有 `## Summary` 當成系統不存在：
   它絕對不會讓任何系統掉出範圍。
3. **架構。** `docs/architecture/architecture.md` 在兩個 tier 都是必要的：
   不存在就停，並說
   "No `docs/architecture/architecture.md` — run `/create-architecture` first." 絕對不要自己編模組邊界。
4. **只針對範圍內的系統**，按章節讀，絕對不要整份讀：
   - 每份 GDD 的 Overview 和 Acceptance Criteria
     （`bash .claude/scripts/md-section.sh extract design/gdd/<file>.md "Overview"`）；
   - `bash .claude/scripts/adr-status.sh`，取得每個 ADR 的狀態、分層和缺少的
     章節；然後是涵蓋範圍內系統的那些 ADR 的 GDD Requirements Addressed、Decision 和 Engine
     Compatibility 章節；
   - `docs/architecture/tr-registry.yaml`：`system:` 是範圍內系統的那些項目；
   - control manifest 的 `Manifest Version` 那行（`standard` 時有就讀，
     `full` 時必要）；
   - `docs/engine-reference/<engine>/VERSION.md`，取得引擎的風險等級。

在定義任何東西之前先回報，反映真實狀態：

```
Loaded: [N] system GDDs, [n] in scope ([names]) · [M] ADRs ([A] Accepted, [P] Proposed) · manifest v[date | absent] · engine [name version from the engine_values line]
```

在 `full`，每份範圍內的 GDD 都要有全部 8 個章節和 Approved 狀態，而且 TR
registry 和 control manifest 是必要的。在 `standard`，GDD 要有它們的 5 個
必要章節，而且只期待關鍵（Foundation 層）的 ADR。

## Phase 3: 定義每個 epic，一次問一個

依分層處理：Foundation，然後 Core、Feature、Presentation；同一層裡，依
systems index 的順序（在 `minimal`，依 brief 的 Build order）。每個系統，用它
在 `architecture.md` 裡的模組（在 `minimal`，用 brief 的功能組）。

**需求涵蓋率**（`minimal` 不做）。系統的每個 TR-ID 是：

- **covered**：有一個 **Accepted** 的 ADR 處理了它；
- 否則就是 **untraced**。只有 `Proposed`（或任何其他狀態）ADR 的需求
  是 untraced，絕對不算 covered：它那一列寫 `❌ No ADR (ADR-NNNN Proposed)`，
  這樣 `/create-stories` 仍然看得到那個 ADR，並擋住它的 story。

untraced 的需求列在 **Untraced Requirements** 底下。下面的 ⚠️ 警告
在 `full` 時針對每個 untraced 的需求，在 `standard` 時只針對 untraced 的
Foundation 層需求；`standard` 時任何其他 untraced 的需求
只當成資訊列出，不給警告。

```
## Epic: [System Name]
**Layer**: [Foundation | Core | Feature | Presentation]
**GDD**: design/gdd/[file].md   (at minimal: design/game-brief.md, MVP features [list])
**Architecture Module**: [module]
**Governing ADRs**: [Accepted ADRs, or "none"]
**Engine Risk**: [LOW | MEDIUM | HIGH — the highest among governing ADRs, else VERSION.md's]
**Requirements covered by Accepted ADRs**: [n / total]
**Untraced Requirements**: [TR-IDs with why, or "None"]
```

警告，適用時："⚠️ [N] requirements in [system] have no Accepted ADR.
Their stories will be written with no governing ADR, or Blocked on a Proposed one.
Run `/architecture-decision` first if they need a decision, or go on and accept the
gap."

然後，**只針對這一個 epic** 問："Shall I create Epic: [name]?" 選項：Yes,
create it / Skip this epic / Pause — I need to write ADRs first. 要等這個答案之後，
才顯示並問下一個 epic。絕對不要把好幾個 epic 併成一個問題。

一個 yes 只涵蓋它回答的那個 epic，也只有那一個，即使措辭是針對全部
（「全部」、「通通照做」）：epic 是看過才核准的。顯示
下一個 epic 的區塊並再問一次，直到範圍內每個 epic 都顯示過
也回答過。

## Phase 4: Producer 審查

讀上面的 `review_gate` 那行。`skill-gates=skip`（solo 或 lean）：不用 agent；在回覆和收尾區塊
註明
`PR-EPIC skipped — [Solo | Lean] mode`。
`skill-gates=run`：讀 `references/pr-epic-gate.md` 和
`.claude/docs/director-gates.md`，並現在就執行它，在範圍內每個 epic 都定義完之後、
任何寫入之前。跳過的話，不要載入它。

## Phase 5: 寫出每個 epic

使用者說 yes 的每個 epic，依序：

**已經有 `EPIC.md`：** 絕對不要覆寫。問 "An EPIC.md already exists for
[name]. Update it in place, or skip it?" 選項：Update in place / Skip this epic.
更新只改這個 skill 擁有的部分（Stories 以外的標頭欄位、
Overview、Governing ADRs、GDD Requirements、Definition of Done），而
`**Stories**` 那行和任何 `## Stories` 表保持原樣：那是 `/create-stories` 寫的，
把它們重設會讓已經在那裡的 story 變成孤兒。

**新的：** 問 "May I write `production/epics/[epic-slug]/EPIC.md` and add its row to
`production/epics/index.md`[, creating it]?" 這是它自己的詢問，每個 epic 一次，在
Phase 3 的 yes 之後：那個 yes 核准的是 epic，不是寫入。只有對它明確回答 yes 才寫。寫入
之前，跑 `bash .claude/scripts/write-guard.sh overwrite
production/epics/[epic-slug]/EPIC.md`。它一定會印一列 `checked`；回來的
`OVERWRITE` 列代表檔案其實已經存在，所以什麼都不要寫，改問
更新的問題。

`docs.density` 決定 Overview 的深度（`terse` 條列、`balanced` 一小段、
`thorough` 完整散文，含 ADR 的理由和風險）；不管哪種密度，表格都要完整。

```markdown
# Epic: [System Name]

> **Layer**: [Foundation | Core | Feature | Presentation]
> **GDD**: design/gdd/[file].md
> **Architecture Module**: [module]
> **Status**: Ready
> **Stories**: Not yet created — run `/create-stories [epic-slug]`

## Overview

[What this epic implements, from the GDD Overview and the module's responsibilities]

## Governing ADRs

| ADR | Decision Summary | Engine Risk |
|-----|------------------|-------------|
| ADR-NNNN: [title] | [one line] | LOW/MEDIUM/HIGH |

## GDD Requirements

| TR-ID | Requirement | ADR Coverage |
|-------|-------------|--------------|
| TR-[system]-001 | [requirement text from the registry] | ADR-NNNN ✅ |
| TR-[system]-002 | [requirement text] | ❌ No ADR (ADR-NNNN Proposed) |

## Definition of Done

- Every story implemented, reviewed and closed with `/story-done`
- Every acceptance criterion of design/gdd/[file].md verified
- Logic and Integration stories have passing tests in the test root
- Visual/Feel and UI stories have retained screenshots in `production/qa/evidence/`
  (a lead sign-off too for Visual/Feel)
```

在 `minimal`，GDD 那行寫 `design/game-brief.md`，Governing ADRs 和 GDD
Requirements 的表格省略，並加一份 **Scope** 清單，依 Build order 列出這個 epic 的 MVP
功能。

**`production/epics/index.md`：** 每個 epic 一列。已經有一列的 epic
保留那一列：就地更新，絕對不要多加第二列，絕對不要重設它的 Stories 欄。

```markdown
# Epics Index

Last Updated: [date]
Engine: [name version]

| Epic | Layer | System | GDD | Stories | Status |
|------|-------|--------|-----|---------|--------|
| [name] | [layer] | [system] | [file] | Not yet created | Ready |
```

## Phase 6: 收尾

在 `standard` 和 `full`，一旦 Foundation 和 Core 的 epic 都存在，就加上："Foundation and
Core epics are what the Pre-Production → Production gate needs. `/gate-check
production` checks readiness." `minimal` 絕對不加。

每個 epic 的內容都來自 GDD、ADR 和架構文件（`minimal` 是 brief）；
沒有一個是編出來的。

**這次執行的最後一則回覆要以這個區塊結尾**（如果之前顯示過，就再重複一次）：

```
Verdict: COMPLETE — [N] epics written: [slugs]
Review: [PR-EPIC skipped — Solo mode | skipped — Lean mode | its verdict]
Index: production/epics/index.md [created | updated]
Next step: /create-stories [first-epic-slug]
```

當使用者跳過或拒絕了每一個 epic：`Verdict: BLOCKED — no epic written
([why])`。找不到範圍內的系統：`Verdict: BLOCKED — no eligible systems in
[scope]`。
