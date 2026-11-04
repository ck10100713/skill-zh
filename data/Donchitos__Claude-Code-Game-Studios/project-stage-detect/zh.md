---
name: project-stage-detect
description: "分析專案狀態、偵測所處階段、找出缺口並建議下一步。「我們開發到哪了？」"
argument-hint: "[optional: role filter like 'programmer' or 'designer']"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Bash(bash "*/.claude/skills/project-stage-detect/../../hooks/yaml-helper.sh" resolve_config *), Bash(bash .claude/scripts/artifact-check.sh), Bash(bash ".claude/scripts/artifact-check.sh"), Bash(bash ./.claude/scripts/artifact-check.sh), Bash(bash .claude/scripts/artifact-check.sh *), Bash(bash ".claude/scripts/artifact-check.sh" *), Bash(bash ./.claude/scripts/artifact-check.sh *)
model: haiku
# 唯讀的診斷 skill，不需要委派給專業 agent
---

# Project Stage Detection

這個 skill 會掃描你的專案，判斷目前的開發階段、產出物的
完整度，以及需要注意的缺口。它特別適合用在：
- 接手一個既有專案
- 熟悉一個程式碼庫
- 在 milestone 之前檢查缺了什麼
- 了解「我們現在在哪？」

---

## Workflow

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys workflow,automation`

**Automation mode**：解析 `modes.automation`（`project.local.yaml` →
`project.yaml` → 預設 `collaborative`）。每一次 `AskUserQuestion` 呼叫和
每一次檔案寫入，都遵循 `.claude/docs/automation-modes.md`
（collaborative 一律問 · guided 只問重大的 · autonomous 只記錄然後繼續；
`automation_always_ask` 的類別一律要問）。

上面已經解析好了，直接用。沒有這個區塊的話，用
`.claude/docs/config-resolution.md` 裡的預設值。

> **要解析 tier — 不要假設。** tier 決定了什麼才算缺口：
> 在 `full`，每個缺少的文件都是缺口；在 `minimal`，沒有一個是，
> 因為有 brief 加上 engine 就是正常狀態，而程式碼是預期的
> 下一步。往高猜，會告訴一個 jam 專案它缺 GDD、美術聖經和 ADR，
> 這正是 `modes.rigor` 存在的目的要防的
> 「流程跟我的專案不搭」的體驗。

**`workflow`**（依 `.claude/docs/workflow-modes.md`）。tier 決定
哪些缺少的文件算缺口（step 3）— 低於 `full` 時，選用文件
不會被標記。

### 1. Scan Key Directories

**從確定性的檢查開始 — 一次呼叫就能回答每個已編入 catalog 的產出物
「存不存在」：**

```
Bash: bash .claude/scripts/artifact-check.sh
```

照寫的樣子執行 — 從專案根目錄、相對路徑、不帶參數、
不要 `cd`、不要 `2>&1`。這個 skill 的權限授權就是比對這個形式；
其他形式都會要使用者核准。

沒帶 `--phase` 時它會回報每個階段，所以一次呼叫就涵蓋整個
專案：每個步驟是 `PRESENT` / `ABSENT` / `SHORT`（附 `count=` 和 `min=`）/
`PATTERN_MISS` / `NO_CHECK`。用它來取代下面
對每個產出物手動 glob，並把它的 `NO_CHECK` 總數當成
「存在性檢查能告訴你多少」的誠實上限。

它只回報觀察結果 — 這些觀察結果意味著哪個階段，還是由這個 skill 決定，
而哪些缺席才算缺口，還是由 tier 決定
（見下面的 workflow-tier 註記）。

然後分析 script 做不到的部分：內容品質、它沒追蹤的計數，
以及需要判斷的地方。

**Design Documentation**（`design/`）：
- 計算 `design/gdd/*.md` 裡的 GDD 檔數量
- 檢查有沒有 game-concept.md（在 `minimal` 是 `design/game-brief.md`）、game-pillars.md、systems-index.md
- 如果 systems-index.md 存在，計算系統總數 vs. 已設計的系統數
- 分析完整度（Overview、Detailed Design、Edge Cases 等）。依章節讀 GDD：
  用 Grep 工具（pattern `^#`，content
  mode）找出你需要的標題，再用 offset 和 limit 讀那幾段範圍。
- 計算 `design/narrative/` 裡的敘事文件數量
- 計算 `design/levels/` 裡的關卡設計數量

**Source Code**（code root — Godot 是 `src/`，Unity 是 `Assets/`，Unreal 是 `Source/`；依 `.claude/docs/code-root-resolution.md` 解析）：
- 計算原始碼檔數量（不分語言）
- 找出主要系統（有 5 個以上檔案的目錄）
- 檢查有沒有 core/、gameplay/、ai/、networking/、ui/ 目錄
- 估計程式碼行數（粗略的規模）
- root 解析不出來，代表這些都沒執行：回報
  `NOT ASSESSED — code root unresolved`，絕對不要回報零個原始碼檔 — 零個檔案
  會被讀成全新專案，而階段表裡原始碼檔數量那幾列
  沒有這個計數就沒辦法判定

**Production Artifacts**（`production/`）：
- 檢查有沒有進行中的 sprint plan。在 `workflow: minimal` 沒有 sprint：
  改依 brief 的 build order 讀 story 檔的進度，
  而且絕對不要把缺少 sprint plan、milestone 或 roadmap 回報成缺口
- 找 milestone 定義
- 找 roadmap 文件

**Prototypes**（`prototypes/`）：
- 計算 prototype 目錄的數量
- 檢查有沒有 README（有文件 vs 沒文件）
- 評估 prototype 是已封存還是還在進行

**Architecture Docs**（`docs/architecture/`）：
- 計算 ADR（Architecture Decision Record）的數量
- 檢查有沒有概覽/索引文件

**Tests**（`tests/`）：
- 計算測試檔數量
- 估計測試覆蓋率（粗略的啟發式）

### 2. Classify Project Stage

依掃描到的產出物判斷階段。先檢查 `project.yaml` 裡的 `project.stage`（如果有）；否則檢查 `production/stage.txt`（舊版退路）— 兩者都是 `/gate-check` 的明確覆蓋值。否則，用這些啟發式自動偵測（從最前進的階段往回檢查）：

> **一律要跑啟發式，即使已經設定了階段 — 然後做比較。**
> 設定的值對於階段「是什麼」是權威的；它不是
> 產出物支持這個階段的證據。兩者都要回報，而當它們不一致時要
> 明確講出來：
>
> > "Configured stage: **Release**. Observed artifacts indicate
> > **Pre-Production** (2 source files, 0 ADRs, no architecture doc, no epics).
> > These disagree — the configured stage may be stale, or work exists outside
> > this repo."
>
> 讀 config 再把它報回去，不是偵測。這個 skill 自己的描述承諾了
> 「analyze project state, detect stage」，而一個
> 不能反駁自己輸入的階段偵測器，是它絕對不能變成的東西 —
> 它會對一個產出物符合自己 Pre-Production 那一列、差了四個階段的專案
> 回報 `Release`，而且什麼都不說。
>
> **不一致會讓 Stage Confidence 變成 CONCERNS**（step 4）— 就定義來說，
> 這是模糊的訊號 — 不管產出物有多完整。有一個例外：在
> `workflow: minimal`，沒有任何東西會跑 `/gate-check`，所以設定的階段會停在
> `/start` 設定的位置。在那裡，要回報觀察到的階段，並說明設定的
> 階段在這個 tier 不會前進；那個落後是預期中的，不是不一致。

| Stage | Indicators |
|-------|-----------|
| **Concept** | No game concept doc, brainstorming phase |
| **Systems Design** | Game concept exists, systems index missing or incomplete |
| **Technical Setup** | Systems index exists, engine not configured |
| **Pre-Production** | Engine configured, code root has <10 source files |
| **Production** | code root has 10+ source files, active development |
| **Polish** | Explicit only (set by `/gate-check` Production → Polish gate) |
| **Release** | Explicit only (set by `/gate-check` Polish → Release gate) |

### 3. Collaborative Gap Identification

**依解析出來的 workflow tier 呈現缺口：**
- **`full`** — 把每個缺少的文件類型（GDD、美術聖經、UX spec、ADR）都標記成缺口。
- **`standard`** — 只標記必要的文件：已建置系統缺少的 GDD，以及
  缺少的關鍵（Foundation 層）ADR。除非有視覺資產的 story 存在，否則不要標記缺少美術聖經，
  也不要標記非核心的 UX spec。
- **`minimal`** — 有 `design/game-brief.md` + engine 就是正常狀態。不要把
  缺少 GDD、美術聖經、UX spec、ADR、epic 或 sprint plan 標記成缺口：brief 的 build
  order 就是計畫，而預期的下一步是程式碼。

**不要**只是列出缺少的檔案。而是要**問釐清的問題**（只針對
上面 tier 說要呈現的缺口）：

- "I see combat code (`<code root>/gameplay/combat/`) but no `design/gdd/combat-system.md`. Was this prototyped first, or should we reverse-document?"
- "You have 15 ADRs but no architecture overview. Should I create one to help new contributors?"
- （只限 `standard`/`full`）"I see [N] systems under `<code root>/` but no ADRs in `docs/architecture/`. Were those decisions recorded somewhere else, or should we write the critical ones with `/architecture-decision`?"
- （只限 `standard`/`full`）"No sprint plans in `production/`. Are you tracking work elsewhere (Jira, Trello, etc.)?"
- "I found a game concept but no systems index. Have you decomposed the concept into individual systems yet, or should we run `/map-systems`?"
- "Prototypes directory has 3 projects with no READMEs. Were these experiments, or do they need documentation?"

### 4. Generate Stage Report

使用範本：`.claude/docs/templates/project-stage-report.md`

**報告結構**：
```markdown
# Project Stage Analysis

**Date**: [date]
**Stage**: [Concept/Systems Design/Technical Setup/Pre-Production/Production/Polish/Release]
**Stage Confidence**: [PASS — clearly detected / CONCERNS — ambiguous signals / NOT ASSESSED — a check the stage depends on did not run / FAIL — critical gaps block progress]

## Completeness Overview
- Design: [X%] ([N] docs, [gaps])
- Code: [X%] ([N] files, [systems])
- Architecture: [X%] ([N] ADRs, [gaps])
- Production: [X%] ([status] — at `minimal`: stories complete in the brief's build order, never "no sprint plan")
- Tests: [X%] ([coverage estimate])

## Gaps Identified
1. [Gap description + clarifying question]
2. [Gap description + clarifying question]

## Recommended Next Steps
[Priority-ordered list based on stage and role]
```

**Stage Confidence — 第一個符合的條件勝出：** 如果關鍵缺口擋住了
進度，就是 **FAIL**；否則，如果蒐集到的訊號是模糊的 — 
它們符合不只一個階段，或設定的階段和觀察到的階段不一致
（step 2）— 就是 **CONCERNS**；否則，如果階段所依賴的某個檢查沒有執行，就是 **NOT ASSESSED** — 
要點名它（code root 解析不出來，包括有兩個候選 root 的情況，會讓
原始碼檔數量，以及連帶讓表格裡的 Production 那一列，無法判定）；否則就是
**PASS**。NOT ASSESSED 的優先順序高於 PASS — 沒人能檢查的階段，不是
清楚偵測到的階段 — 而低於 CONCERNS 和 FAIL，所以已知的問題
永遠不會被它蓋住。

### 5. Role-Filtered Recommendations (Optional)

如果使用者有給角色參數（例如 `/project-stage-detect programmer`）：

**Programmer**：
- 聚焦在架構文件、測試覆蓋、缺少的 ADR
- 程式碼和文件之間的缺口

**Designer**：
- 聚焦在 GDD 完整度、缺少的設計章節
- Prototype 文件

**Producer**：
- 聚焦在 sprint plan、milestone 追蹤、roadmap
- 跨團隊協調文件

**General**（沒有角色）：
- 所有缺口的整體視角
- 跨領域最高優先順序的項目

### 6. Request Approval Before Writing

**協作式協定**：
```
I've analyzed your project. Here's what I found:

[Show summary]

Gaps identified:
1. [Gap 1 + question]
2. [Gap 2 + question]

Recommended next steps:
- [Priority 1]
- [Priority 2]
- [Priority 3]

May I write the full stage analysis to production/project-stage-report.md?
```

建立檔案之前，等使用者核准。

---

## Example Usage

```bash
# General project analysis
/project-stage-detect

# Programmer-focused analysis
/project-stage-detect programmer

# Designer-focused analysis
/project-stage-detect designer
```

---

## Follow-Up Actions

產生報告之後，建議相關的下一步 — **只針對
解析出來的 workflow tier 呈現的缺口**（step 3）。在 `standard`/`minimal`，不要
建議撰寫選用文件（例如在 `minimal` 不要為缺少的 GDD 建議 `/reverse-document`，
因為在那裡程式碼才是預期的下一步）：

- **在 `minimal` 沒有 `design/game-brief.md`？** → 當 code root 已經有這款遊戲（10 個以上原始碼檔）時，用 `/reverse-document design <code root>`：
  它會依已經做好的東西寫出 brief。程式碼很少或沒有，就用 `/brainstorm`。
- **概念存在但沒有系統索引？** → `/map-systems` 來拆解成各個系統
- **缺少設計文件？** → `/reverse-document design <code root>/[system]`
- **缺少架構文件？** → `/architecture-decision` 或 `/reverse-document architecture`
- **Prototype 需要文件？** → `/reverse-document concept prototypes/[name]`
- **沒有 sprint plan？** → `/sprint-plan`（在 `rigor: minimal` 不用，那裡 brief 的 build order 就是計畫）
- **快到 milestone 了？** → `/milestone-review`

---

## Collaborative Protocol

這個 skill 遵循協作式設計原則：

1. **先問問題**：問缺口，不要假設
2. **呈現選項**：「Should I create X, or is it tracked elsewhere?」
3. **使用者決定**：等待指示
4. **展示草稿**：顯示報告摘要
5. **取得核准**：「May I write to production/project-stage-report.md?」

**絕對不要**默默寫檔。**一律**先展示發現，並在建立產出物之前先問。
