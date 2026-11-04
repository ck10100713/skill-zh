---
name: create-control-manifest
description: "從已接受的 ADR 整理出每個系統「一定要做」和「絕對不准做」的簡短程式規則清單。使用者想要從 ADR 得到給工程師的規則或小抄，或 ADR 改了需要重新產生時使用。"
argument-hint: "[update — regenerate from current ADRs] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Agent, AskUserQuestion, Bash(bash "*/.claude/skills/create-control-manifest/../../hooks/yaml-helper.sh" resolve_config *), Bash(bash .claude/scripts/adr-status.sh*), Bash(bash .claude/scripts/md-section.sh *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,review_gate,automation`

上面已經解析好了，直接用；`--review` 在這次執行覆蓋 `review_mode`。沒有
這個區塊 → 用 `.claude/docs/config-resolution.md` 裡的預設值。

提問要用提問工具。沒有的話，把選項編號列出來，然後結束你這一輪
等回覆。被跳過或被關掉的問題不算回答：用純文字再問一次。

# Create Control Manifest

control manifest 是一份給程式設計師的扁平規則表：依架構分層列出該做什麼、
絕對不准做什麼，內容來自 Accepted 的 ADR、專案的
技術偏好，還有引擎參考文件。ADR 講的是*為什麼*；
manifest 講的是*做什麼*。

**寫入：** `docs/architecture/control-manifest.md`，要在使用者說 yes 之後。
**何時：** 在 `/architecture-review` 通過、而且 ADR 都是 Accepted 之後。每當有 ADR 被接受或修訂，
就再跑一次。

提問遵循 `.claude/docs/automation-modes.md`（collaborative 一律會問、guided
遇到重大選擇才問、autonomous 記錄後繼續；`automation_always_ask`
的類別一律要問）。

## Phase 1: 載入輸入

### ADR

`bash .claude/scripts/adr-status.sh` 一次讀完所有 `docs/architecture/adr-*.md`：
先給數量（`adrs`，然後是 `accepted`、`proposed`、`deprecated`、
`superseded`、`unfilled`、`other`、`no_status`），再每個 ADR 一列，附它的
狀態和分層。先確立分母：在讀任何 ADR 之前，先依數量決定：

| Counts | Meaning | Action |
|---|---|---|
| `adrs 0` | 沒有 ADR。 | "No ADRs found — run `/architecture-decision` before building a control manifest." 停。 |
| `accepted` ≥ 1 | 正常。 | Accepted 的那幾列就是集合 **A**。其他每個 ADR 都要連同狀態在 Phase 4 的預覽裡點名：使用者核准 manifest 時要知道它漏掉了什麼。 |
| `accepted 0`、有些有狀態 | 沒有 Accepted 的 ADR。 | "[N] ADRs found, none Accepted. A manifest built from Proposed ADRs would encode decisions that may still change." 問是要用 Proposed 的繼續，還是停。**絕對不准默默寫出一份空的 manifest。** |
| 每個 ADR 都是 `no_status` | **ADR 格式不正確，不是空的 Accepted 集合。** | "[N] ADRs found, none has a `## Status` section, so acceptance cannot be told. Run `/architecture-decision retrofit [file]` on each." 停。絕對不要把它們當成 Accepted。 |

上面每一個「停」，都以 `Verdict: BLOCKED — [the reason]` 結尾。記下每條規則
來自哪個 ADR 的編號和標題。

### 專案設定

- 從 `project.yaml` 讀 `naming.*` 和 `performance.*`；任何 key 不存在或是空的，
  就用 `.claude/docs/technical-preferences.md`。
- 核准的函式庫和禁用的模式，來自
  `.claude/docs/technical-preferences.md`（沒有 migrate 到 `project.yaml`）。

### 引擎參考

- `docs/engine-reference/[engine]/VERSION.md`，取得引擎和版本。
- `docs/engine-reference/[engine]/deprecated-apis.md`：這些會變成禁用的 API。
- `docs/engine-reference/[engine]/current-best-practices.md`，如果存在的話。

### 已經存在的東西

`docs/architecture/control-manifest.md` 已存在：這次執行是重新產生它；在 Phase 5 的寫入
（會取代它）之前先讀它。`production/epics/*/EPIC.md` 已存在：
代表 epic 已經存在。Phase 6 兩者都看，來決定下一步。

回報："Loaded [A] Accepted ADRs of [N], engine: [name + version]."

## Phase 2: 從每個 ADR 擷取規則

**A** 裡的每個 ADR，只讀四個章節，絕對不要讀整個檔案：

```
bash .claude/scripts/md-section.sh extract docs/architecture/[adr-file].md "Decision"
```

`Alternatives Considered`、`Performance Implications` 和 `Engine
Compatibility` 也一樣。Context、Consequences、Migration Plan 和 Validation Criteria 講的是
為什麼做某個決定；manifest 記錄的是該做什麼。ADR 缺少的章節：就替那個 ADR
記下來，然後繼續。如果 A 裡**每一個** ADR 都缺某個章節，就回報 "No
Accepted ADR has a `[section]` section — the manifest's [category] rules will be
empty. Verify this is intended." 只有當某個章節指向它自己以外的地方（「受 Context 裡的限制約束」）時，
才去讀這四個以外的，而且只讀那一個章節。

從每個 ADR 擷取：

- **Required patterns**（Decision）：每個「must」、「should」、「required to」、
  「always」，以及它強制要求的每個模式或做法，包含裡面的任何 `### Implementation
  Guidelines`。絕對不要只找那個子標題：很多 ADR 直接把強制要求寫在 Decision 底下，
  只掃子標題就會得到一個空的章節。
- **Forbidden approaches**（Alternatives Considered）：每個被否決的替代方案，
  把它被否決的原因當成規則（「never use X because Y」），以及任何具名的
  anti-pattern。
- **Performance guardrails**（Performance Implications）：預算（「max N ms per
  frame for this system」）和記憶體上限。
- **Engine API constraints**（Engine Compatibility）：需要驗證的 post-cutoff API、
  跟模型預期不同的行為、釘住版本中有變動的欄位或
  方法。

**分層。** 每條規則放在它所管轄系統所屬的分層底下，
有 `layer` 欄的話就用 ADR 的 `layer` 欄：

- **Foundation：** scene 管理、event 架構、存讀檔、引擎啟動
- **Core：** 核心 gameplay 迴圈、主要玩家系統、物理與碰撞
- **Feature：** 次要系統與機制、AI
- **Presentation：** 渲染、音訊、UI、VFX、shader

橫跨多層的 ADR，就把它的規則放進每一層。

## Phase 3: 加入全域規則

適用每一層的規則，每條都要附來源（`project.yaml` 的 key、
`technical-preferences.md`，或引擎參考檔），跟分層規則一樣：

- **Naming**，來自 `naming.*`：類別、變數、signal 和 event、檔案、
  常數。
- **Performance budgets**，來自 `performance.*`：目標幀率、幀預算、
  draw call、記憶體上限。
- **Forbidden APIs**，來自 `deprecated-apis.md`，**只放適用於這個
  專案會蓋的東西的。** 絕對不要整張表照抄：它的 `GodotPhysics3D → Jolt Physics
  3D` 那一列只適用 3D，而 2D 專案不會用那個引擎。當你判斷不出某個項目適不適用
  （2D 還是 3D、專案可能不含的模組），就限定規則的範圍（「when using 3D physics: …」），
  或不放，並把它列為未解決。`/create-stories` 會讀這個檔案，而不適用的規則
  就是沒人會讀的規則。
- **Required patterns**，來自 `current-best-practices.md`，如果存在的話。
- **Forbidden patterns**，來自 `technical-preferences.md`，照原文複製。

## Phase 4: 顯示摘要，再做審查

```
## Control Manifest Preview
Engine: [name + version]
ADRs covered: [ADR numbers]
ADRs left out: [ADR-NNNN ([status]), … — every ADR not in A, or "None"]
Rules extracted:
  - Foundation layer: [N] required, [M] forbidden, [P] guardrails
  - Core layer: [N] required, [M] forbidden, [P] guardrails
  - Feature layer: …
  - Presentation layer: …
  - Global: [N] naming conventions, [M] forbidden APIs, [P] approved libraries
Unresolved: [engine entries left out because whether they apply is unclear, or "None"]
```

問："Does this rule summary look complete?" 選項：Yes — review and write it /
Add rules — I have more to include / Remove rules — some should be dropped / Stop —
I need to review the ADRs first.

**技術審查。** 讀上面的 `review_gate` 那行。`skill-gates=skip`
（solo 或 lean）：不用 agent；註明 `TD-MANIFEST skipped — [Solo | Lean] mode`。
`skill-gates=run`：把審查交給 `technical-director` agent，使用 gate
**TD-MANIFEST**（`.claude/docs/director-gates/td-manifest.md`；agent 自己會讀它）。Brief：

- **目標：** 在寫入之前檢查擷取出來的規則。
- **提供給它：** 上面的預覽加上完整的規則清單、涵蓋的 ADR、
  引擎版本，以及取自技術偏好或引擎
  參考的規則。
- **檢查：** 每一個強制的 ADR 模式都有被擷取、敘述正確；
  禁用的做法完整、出處歸屬正確；沒有任何規則缺少來源
  ADR 或偏好文件；guardrail 跟 ADR 的限制一致。
- **回傳：** APPROVE、CONCERNS、REJECT，或是點名缺少輸入的 NOT ASSESSED。
- **界線：** 它不寫任何檔案。

依 verdict 行動：

- **APPROVE：** 進 Phase 5。
- **CONCERNS：** 問："The technical director raised concerns. How do you want to go
  on?" 選項：Revise the flagged rules / Accept and go on / Discuss further.
- **REJECT：** 什麼都不寫；修正被標記的規則，再次顯示摘要。
- **NOT ASSESSED：** 它不算核准（`.claude/docs/director-gates.md`）。指出
  缺了什麼，然後補上並再跑一次審查；或者，當使用者
  選擇不補就繼續，就進 Phase 5，並在回覆和最後的 verdict 行都寫上 `TD-MANIFEST: NOT ASSESSED —
  [input]`。

## Phase 5: 寫出 control manifest

問："May I write the control manifest to `docs/architecture/control-manifest.md`?"
選項：Yes, write it / Show me the full draft first, then ask again / Not yet — I
want more changes. 只有明確回答 yes 才寫。

```markdown
# Control Manifest

> **Engine**: [name + version]
> **Last Updated**: [date]
> **Manifest Version**: [date]
> **ADRs Covered**: [ADR-NNNN, ADR-MMMM, ...]
> **Status**: Active — regenerate with `/create-control-manifest update` when ADRs change

`Manifest Version` is the date this manifest was generated. Stories embed it when
they are written, and `/story-readiness` compares a story's version with this one
to find stories written against old rules. It always equals `Last Updated`: the
same date, for different readers.

This manifest is a programmer's quick reference taken from the Accepted ADRs, the
technical preferences and the engine reference docs. For the reason behind a rule,
read its ADR.

---

## Foundation Layer Rules

*Applies to: scene management, event architecture, save/load, engine start-up*

### Required Patterns
- **[rule]** — source: [ADR-NNNN]

### Forbidden Approaches
- **Never [anti-pattern]** — [brief reason] — source: [ADR-NNNN]

### Performance Guardrails
- **[system]**: max [N]ms/frame — source: [ADR-NNNN]

---

## Core Layer Rules

*Applies to: core gameplay loop, main player systems, physics, collision*

### Required Patterns
...

### Forbidden Approaches
...

### Performance Guardrails
...

---

## Feature Layer Rules

*Applies to: secondary mechanics, AI systems, secondary features*

### Required Patterns
...

### Forbidden Approaches
...

---

## Presentation Layer Rules

*Applies to: rendering, audio, UI, VFX, shaders, animations*

### Required Patterns
...

### Forbidden Approaches
...

---

## Global Rules (All Layers)

### Naming Conventions
| Element | Convention | Example | Source |
|---------|-----------|---------|--------|
| Classes | [convention] | [example] | [`naming.classes` in project.yaml, or technical-preferences.md] |
| Variables | [convention] | [example] | [`naming.variables` in project.yaml, or technical-preferences.md] |
| Signals/Events | [convention] | [example] | [`naming.signals` in project.yaml, or technical-preferences.md] |
| Files | [convention] | [example] | [`naming.files` in project.yaml, or technical-preferences.md] |
| Constants | [convention] | [example] | [`naming.constants` in project.yaml, or technical-preferences.md] |

### Performance Budgets
| Target | Value | Source |
|--------|-------|--------|
| Framerate | [value] | [`performance.target_framerate` in project.yaml, or technical-preferences.md] |
| Frame budget | [value] | [`performance.frame_budget_ms` in project.yaml, or technical-preferences.md] |
| Draw calls | [value] | [`performance.draw_call_limit` in project.yaml, or technical-preferences.md] |
| Memory ceiling | [value] | [`performance.memory_ceiling_mb` in project.yaml, or technical-preferences.md] |

### Approved Libraries / Addons
- [library] — approved for [purpose] — source: technical-preferences.md

### Forbidden APIs ([engine version])
These APIs are deprecated or unverified for [engine + version]:
- `[api name]` — deprecated since [version] / unverified post-cutoff
- Source: `docs/engine-reference/[engine]/deprecated-apis.md`

### Cross-Cutting Constraints
- [constraint that applies in every layer] — source: [ADR-NNNN, preference key or engine-reference file]
```

## Phase 6: 下一步

- 還沒有 epic："Run `/create-epics layer: foundation`, then `/create-stories
  [epic-slug]`: stories embed this manifest's rules and version."
- 重新產生的情況："Updated. Tell the team about the changed rules, above all any
  new Forbidden entries."

每條規則都能追溯到 ADR、技術偏好或引擎參考文件；
沒有一條是編出來的，也沒有一條被改寫成意思有變。寫入之後以
`Verdict: COMPLETE — control manifest written` 收尾，使用者拒絕的話就以 `Verdict:
BLOCKED — user declined the write` 收尾。
