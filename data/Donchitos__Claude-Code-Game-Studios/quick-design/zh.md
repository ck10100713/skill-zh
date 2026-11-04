---
name: quick-design
description: "給小改動用的輕量 spec：調數值、小機制。直接內嵌進 story，跳過完整的 GDD。"
argument-hint: "[brief description of the change]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(bash "*/.claude/skills/quick-design/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation,workflow`



# Quick Design

這是給不需要完整 GDD 的變更用的**輕量設計路徑**。
透過 `/design-system` 撰寫完整 GDD 是重量級的路徑。這個 skill 用在
實作時間不到大約一週的工作 — 調整數值、小幅的
行為微調、對既有系統的小幅新增，或是小到不值得寫完整文件的獨立功能。
大部分的微調只要幾個小時；一週的上限是
New Small System 的極限（見下面的分類）。

**輸出：** `design/quick-specs/[name]-[date].md`

**什麼時候執行：** 只要變更小到不需要 `/design-system`，但
重要到沒有書面理由就不該實作，就可以執行。

---

每一次 `AskUserQuestion` 呼叫都遵循 `.claude/docs/automation-modes.md`
（collaborative 一律問 · guided 只問重大的 · autonomous 只記錄然後繼續；
`automation_always_ask` 的類別一律要問）。

## 1. Classify the Change

首先，讀參數並判斷這個變更屬於哪個類別：

- **Tuning** — 改既有系統裡的數字或平衡值，沒有
  行為上的改變（最精簡的路徑）。範例：「increase jump height from 5
  to 6 units」、「reduce enemy patrol speed by 10%」。
- **Tweak** — 對既有系統的小幅行為變更，不引入
  新的狀態、分支或系統。範例：「make dash invincible on frame 1」、
  「allow combo to cancel into roll」。
- **Addition** — 對既有系統加上一個小機制，可能引入
  1-2 個新狀態或互動。範例：「add a parry window to the block
  mechanic」、「add a charge variant to the basic attack」。
- **New Small System** — 一個獨立的功能，小到沒有
  既有的 GDD，而且實作工作不到大約一週。
  範例：「achievement popup system」、「simple day/night visual cycle」。

如果變更不屬於這些類別 — 它引入了有重大跨系統相依的新系統、
需要超過一週的實作，或從根本上改變既有系統的核心規則 — 就停下來，
改指引到 `/design-system`。Verdict: **REDIRECTED** — 這個變更請用
`/design-system`。

如果沒有參數，請使用者描述這個變更（純文字提示），然後用上面的條件分類。

用 `AskUserQuestion` 呈現推論出來的分類：
- Prompt: "I've classified this as **[inferred type]** — [brief reason]. Is that correct?"
- Options:
  - `[A] Yes — [inferred type] is correct`
  - `[B] Tuning — changing numbers or balance values only`
  - `[C] Tweak — small behavioral change to an existing system`
  - `[D] Addition — adding a small mechanic to an existing system`
  - `[E] New Small System — standalone feature, under one week of work`
  - `[F] This is too large — redirect me to /design-system`

選 [F]：停下來。Verdict: **REDIRECTED** — 這個變更請用 `/design-system`。
否則：照選擇的類型繼續。

---

## 2. Context Scan

在起草任何東西之前，先讀相關脈絡。依章節讀 GDD 和 systems
index：用 Grep 工具（pattern `^#`，
content mode）找出你需要的標題，再用 offset 和 limit 讀那幾段範圍。

- 在 `design/gdd/` 搜尋跟這個變更最相關的 GDD。讀
  這個變更會影響的章節。如果沒有 GDD 涵蓋這個 system — 通常是
  `workflow: minimal` 的情況，那裡 `design/game-brief.md` 和 story 就是
  設計紀錄 — 就改讀 brief 裡跟它有關的那幾行，以及這個變更
  碰到的 story，回報「No GDD for [system] — using the brief and [story
  path]」，並把 brief 當成 spec 的 GDD Reference。
- 檢查 `design/gdd/systems-index.md` 存不存在。如果存在，就讀它，了解
  這個 system 在相依圖裡的位置，以及它屬於哪個 tier。如果不存在，就註明「No systems index found — skipping
  dependency tier check.」然後繼續。
- 檢查 `design/quick-specs/` 裡有沒有任何先前碰過這個
  system 的 quick spec — 避免跟它們矛盾。
- 如果這是 Tuning 變更，也要檢查 `assets/data/` 裡放有相關數值的資料檔。

回報找到了什麼：「Found GDD at [path]. Relevant section: [section name].
Prior quick specs for this system: [each path, and whether it agrees or
conflicts with this change — or "none"].」就算先前的 spec 跟這次一致，也要點名它 —
光說「no conflicts」，讀起來跟「no prior specs」一模一樣。

---

## 3. Draft the Quick Design Spec

依變更類別使用合適的 spec 格式。

### For Tuning changes

產出一張表：

```markdown
# Quick Design Spec: [Title]

**Type**: Tuning
**System**: [System name]
**GDD Reference**: `design/gdd/[filename].md` — Tuning Knobs section
**Date**: [today]

## Change

| Parameter | Old Value | New Value | Rationale |
|-----------|-----------|-----------|-----------|
| [param]   | [old]     | [new]     | [why]     |

## Tuning Knob Mapping

Maps to GDD Tuning Knob: [knob name and its documented range].
New value is [within / at the edge of / outside] the documented range.
[If outside: explain why the range should be extended.]

## Acceptance Criteria

- [ ] [Parameter] reads [new value] from `assets/data/[file]`
- [ ] Behavior difference is observable in [specific context]
- [ ] No regression in [related behavior]
```

### For Tweak and Addition changes

```markdown
# Quick Design Spec: [Title]

**Type**: [Tweak / Addition]
**System**: [System name]
**GDD Reference**: `design/gdd/[filename].md`
**Date**: [today]

## Change Summary

[1-2 sentences describing what changes and why.]

## Motivation

[Why is this change needed? What player experience problem does it solve?
Reference the relevant MDA aesthetic or player feedback if applicable.]

## Design Delta

Current GDD says (quoting `design/gdd/[filename].md`, [section]):

> [exact quote of the relevant rule or description]

This spec changes that to:

[New rule or description, written with the same precision as a GDD Detailed
Rules section. A programmer should be able to implement from this text alone.]

## New Rules / Values

[Full unambiguous statement of the replacement content. If this introduces
new states, list them. If it introduces new parameters, define their ranges.]

## Affected Systems

| System | Impact | Action Required |
|--------|--------|-----------------|
| [system] | [how it is affected] | [update GDD / update data file / no action] |

## Acceptance Criteria

- [ ] [Specific, testable criterion 1]
- [ ] [Specific, testable criterion 2]
- [ ] [Specific, testable criterion 3]
- [ ] No regression: [the original behavior this must not break]

## GDD Update Required?

[Yes / No]
[If yes: which file, which section, and what the update should say.]
```

### For New Small System changes

使用精簡過的 GDD 結構。只放直接
必要的章節 — 除非這個系統特別需要，否則跳過 Player Fantasy、完整的 Formulas 和 Edge Cases。

```markdown
# Quick Design Spec: [Title]

**Type**: New Small System
**Scope**: [1-2 sentence description of what this system does and doesn't do]
**Date**: [today]
**Estimated Implementation**: [hours]

## Overview

[One paragraph a new team member could understand. What does this system do,
when does it activate, and what does it produce?]

## Core Rules

[Unambiguous rules for the system. Use numbered lists for sequential behavior
and bullet lists for conditions. Be precise enough that a programmer can
implement without asking questions.]

## Tuning Knobs

| Knob | Default | Range | Category | Rationale |
|------|---------|-------|----------|-----------|
| [name] | [value] | [min–max] | [feel/curve/gate] | [why this default] |

All values must live in `assets/data/[appropriate-file].json`, not hardcoded.

## Acceptance Criteria

- [ ] [Functional criterion: does the right thing]
- [ ] [Functional criterion: handles the edge case]
- [ ] [Experiential criterion: feels right — what a playtest validates]
- [ ] [Regression criterion: does not break adjacent system]

## Systems Index

This system is not currently in `design/gdd/systems-index.md`.
[If it should be added: suggest which layer and priority tier.]
[If it is too small to track: state "This system is below systems-index
tracking threshold — quick spec is sufficient."]
```

---

## 4. Approval and Filing

把草稿完整呈現給使用者。然後用 `AskUserQuestion`：
- Prompt: "Here's the Quick Design Spec draft. How do you want to proceed?"
- Options:
  - `[A] Approve — write it as shown`
  - `[B] Revise — I'll describe what to change`
  - `[C] This grew too large — redirect to /design-system instead`

選 [B]：收集要求的修改，修訂草稿，並重新呈現這個選單。
選 [C]：停下來。Verdict: **REDIRECTED** — 這個變更請用 `/design-system`。

選 [A]：問「May I write this Quick Design Spec to
`design/quick-specs/[kebab-case-title]-[YYYY-MM-DD].md`?」

檔名用今天的日期。標題要是這個變更的 kebab-case 描述
（例如 `jump-height-tuning-2026-03-10`、
`parry-window-addition-2026-03-10`）。

使用者答應就建立 `design/quick-specs/` 目錄（如果它不存在），然後
寫檔。

如果需要更新 GDD（spec 裡有標記），在寫完 quick spec 之後另外問：

「This spec modifies rules in [System Name]. May I update
`design/gdd/[filename].md` — specifically the [section name] section?」

問之前要先顯示會被改的確切文字（舊的 vs. 新的）。沒有明確核准，
不准編輯 GDD。

---

## 5. Handoff

寫完檔之後，輸出：

```
Quick Design Spec written to: design/quick-specs/[filename].md
Type: [Tuning / Tweak / Addition / New Small System]
System: [system name]
GDD update: [Required — pending approval / Applied / Not required]

Next step: This spec is ready for `/story-readiness` validation before
implementation (at `workflow: minimal`, go straight to `/dev-story`). Reference this spec in the story's GDD Reference field.
```

### Pipeline Notes

Verdict: **COMPLETE** — quick design spec written and ready for implementation.

Quick Design Spec 依設計**繞過** `/design-review` 和 `/review-all-gdds`。
它們是給小的、低風險、範圍明確的變更用的，這類變更跑完整審查流程的成本
超過變更本身的風險。

如果符合下列任何一項，就改走完整流程：
- 變更加了一個應該放進 systems index 的新系統
- 變更大幅改變跨系統的行為，或一個系統
  對其他系統的契約
- 變更引入了影響遊戲 MDA aesthetic 平衡的
  新的玩家面向機制
- 實作很可能超過一週的工作量

這些情況下：「This change has grown beyond quick-spec scope. I recommend
using `/design-system` to author a full GDD for this.」

---

## Recommended Next Steps

- 執行 `/story-readiness [story-path]`，在實作開始前驗證 story（在 `rigor: minimal` 跳過 — 直接 `/dev-story`）— 在 story 的 GDD Reference 欄位裡參照這份 spec
- story 通過就緒檢查之後，執行 `/dev-story [story-path]` 來實作
- 如果變更比預期的大，就改執行 `/design-system [system-name]` 來撰寫完整的 GDD
