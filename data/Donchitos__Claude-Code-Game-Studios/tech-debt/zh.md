---
name: tech-debt
description: "追蹤、分類並排定整個 codebase 的技術債優先順序：掃描債務跡象，並維護一份登記表。"
argument-hint: "[scan|add|prioritize|report]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(bash "*/.claude/skills/tech-debt/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation,workflow`

# Tech Debt



每一次 `AskUserQuestion` 呼叫都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律要問 · guided 只問重大的 · autonomous 記錄後直接往下走；
屬於 `automation_always_ask` 類別的一律要問）。

## Phase 1: Parse Subcommand

從參數判斷模式：

- `scan` — 掃描 codebase 找技術債的跡象
- `add` — 手動新增一筆技術債條目
- `prioritize` — 重新排定現有債務登記表的優先順序
- `report` — 產生目前債務狀況的摘要報告

如果沒有帶子指令，就輸出用法然後停止。Verdict: **FAIL** — missing required subcommand.

---

## Phase 2A: Scan Mode

在 **code root** 裡（依 `.claude/docs/code-root-resolution.md` 解析：
依引擎而定是 `src/`、`Assets/` 或 `Source/`）搜尋債務跡象：

- `TODO` 註解（計數並分類）
- `FIXME` 註解（這些是偽裝成債務的 bug）
- `HACK` 註解（需要正式解法的 workaround）
- `@deprecated` 標記
- 重複的程式碼區塊（多個檔案裡出現類似的寫法）
- 超過 500 行的檔案（可能是 god object）
- 超過 50 行的函式（可能過於複雜）

把每個發現分類：

- **Architecture Debt**：抽象錯誤、缺少模式、耦合問題
- **Code Quality Debt**：重複、複雜度、命名、缺少型別
- **Test Debt**：缺少測試、不穩定的測試、沒測的邊界情況
- **Documentation Debt**：缺少文件、過時文件、沒有文件的 API
- **Dependency Debt**：過時的套件、被棄用的 API、版本衝突
- **Performance Debt**：已知的慢路徑、沒最佳化的查詢、記憶體問題

**在呈現任何東西之前，先確認真的有東西可掃。** 數一下掃描實際涵蓋的原始碼檔案數。如果 code root 沒有解析出來，就回報 `NOT ASSESSED — code root unresolved` 並照下面的方式停止。如果那個數字是**零**（code root 不存在，或裡面沒有原始碼檔案），就回報：

> **NOT ASSESSED — no source files to scan.** The code root contains no code, so
> "no debt indicators found" would be a statement about an empty search, not
> about the codebase. Run this once implementation is under way.

然後停止。不要寫入登記表，也不要發出 COMPLETE verdict。

這個區別正是掃描的重點：**400 個檔案掃出零個發現，代表 codebase 很乾淨；零個檔案掃出零個發現，代表完全沒有資訊。** 把兩者都呈現成「COMPLETE — scan findings written to register」，讀起來就像是第一種。回報發現的時候，一定要講明分母，即使分母很大、而且發現數量確實是零也一樣。

把發現呈現給使用者。

問：「May I write these findings to `docs/tech-debt-register.md`?」

如果同意，就更新登記表，絕對不要覆蓋它。**附加之前先比對：** 如果某個發現跟既有 `Open` 條目是同一個檔案、同一種債務，就更新那個條目，不要新增重複的。如果既有的 `Open` 條目，它的模式已經不在那個檔案裡了，就提議把它標成 `Resolved [date]`：把這些列出來，併入同一次核准。Verdict: **COMPLETE** — scan findings written to register.

如果不同意，就在這裡停止。Verdict: **BLOCKED** — user declined write.

---

## Phase 2B: Add Mode

向使用者詢問描述和受影響的檔案（用純文字提問）。

**是不是以 subagent 的身分在跑？** `lead-programmer` 會預先載入這個 skill，而 subagent 沒有 `AskUserQuestion`。把下面三個問題（類別、工作量、影響）一次在同一則回覆裡回傳，每題都附上簡短的選項清單，然後停止：由呼叫你的那一方去問使用者。在答案回來之前，什麼都不要寫進登記表。

然後用 `AskUserQuestion` 收集**類別**：
- Prompt: "What category does this tech debt belong to?"
- Options:
  - `[A] Architecture Debt — wrong abstractions, missing patterns, coupling issues`
  - `[B] Code Quality Debt — duplication, complexity, naming, missing types`
  - `[C] Test Debt — missing tests, flaky tests, untested edge cases`
  - `[D] Documentation Debt — missing/outdated docs, undocumented APIs`
  - `[E] Dependency Debt — outdated packages, deprecated APIs, version conflicts`
  - `[F] Performance Debt — known slow paths, memory issues, unoptimized queries`

然後用 `AskUserQuestion` 收集**預估修復工作量**：
- Prompt: "What is the estimated effort to fix this item?"
- Options:
  - `[A] S — Small (under 1 day)`
  - `[B] M — Medium (1–3 days)`
  - `[C] L — Large (3–7 days)`
  - `[D] XL — Extra Large (over 1 week)`

然後用 `AskUserQuestion` 收集**不修的話會有什麼影響**，也就是登記表的 Impact 欄，`/tech-debt prioritize` 會依它計分：
- Prompt: "What does this cost if it is never fixed?"
- Options: `[A] Low` / `[B] Med` / `[C] High` / `[D] Critical`

把完整的新條目呈現給使用者。

**附加之前先比對：** 如果既有的 `Open` 條目已經有同一個檔案、同一個類別，就把它秀給使用者看，問要不要改成更新那個條目，而不是新增重複的。

問：「May I append this entry to `docs/tech-debt-register.md`?」（或者有比對到的話，問「May I update the existing entry instead?」）

如果同意，就附加這個條目（或更新比對到的那個）。Verdict: **COMPLETE** — entry added to register.

如果不同意，就在這裡停止。Verdict: **BLOCKED** — user declined write.

---

## Phase 2C: Prioritize Mode

讀 `docs/tech-debt-register.md` 的債務登記表。如果它不存在：
Verdict: **NOT ASSESSED** — no register at `docs/tech-debt-register.md`; run
`/tech-debt scan` first. 然後停止。

用每個項目自己的欄位計分：`impact ÷ effort`，Impact 的 `Low` 是 1、`Med` 是 2、`High` 是 3、`Critical` 是 4，Effort 的 `S` 是 1、`M` 是 2、`L` 是 3、`XL` 是 4，四捨五入到小數點後一位，寫進 Priority。分數高的排前面；同分的，`Added` 日期較早的排前面。Impact 或 Effort 是 `—` 的項目不計分：把它們列在有計分的項目後面，標成「not scored — [column] not judged」，不要亂猜一個分數。

依優先分數重新排序登記表，並建議下一個 sprint 要納入哪些項目（在沒有 sprint 的 `workflow: minimal` 下，改成建議接下來要做哪些）。

把重新排序後的登記表呈現給使用者。

問：「May I write the re-prioritized register back to `docs/tech-debt-register.md`?」

如果同意，就寫入更新後的檔案。Verdict: **COMPLETE** — register re-prioritized and saved.

如果不同意，就在這裡停止。Verdict: **BLOCKED** — user declined write.

---

## Phase 2D: Report Mode

讀債務登記表。如果它不存在：Verdict: **NOT ASSESSED** — no
register to report on; run `/tech-debt scan` first. 然後停止。

產生摘要統計：

- 依類別統計未結項目，以及它們預估的總修復工作量
- 目前 sprint 期間新增的項目與已解決的項目，依各條目的 `Added` 日期和它的 `Resolved [date]` 狀態計算
- 趨勢方向（成長 / 穩定 / 縮減）：那段期間新增 vs 已解決

標出在登記表裡待超過 3 個 sprint 的任何項目。

把報告輸出給使用者。這個模式是唯讀的，不會寫任何檔案。Verdict: **COMPLETE** — debt report generated.

---

## Phase 3: Next Steps

- 跑 `/sprint-plan`，把高優先的債務項目排進下一個 sprint（在沒有 sprint 的 `workflow: minimal` 下，改把它們加進 brief 的 build order）。
- 每個 sprint 開始時跑 `/tech-debt report`，追蹤債務隨時間的趨勢。

### Debt Register Format

```markdown
## Technical Debt Register
Last updated: [Date]
Total items: [N] | Estimated total effort: [T-shirt sizes summed]

| ID | Category | Description | Files | Effort | Impact | Priority | Status | Added | Sprint |
|----|----------|-------------|-------|--------|--------|----------|--------|-------|--------|
| TD-001 | [Cat] | [Description] | [files] | [S/M/L/XL] | [Low/Med/High/Critical] | [Score] | [Open / Resolved YYYY-MM-DD / Accepted — reason] | [YYYY-MM-DD] | [Sprint to fix or "Backlog"] |
```

每個會新增一列的 skill，包括這一個，以及把偏離項目記成債務的 `/story-done`，都要依這個順序寫滿全部十個欄位，而建立這個檔案的 skill，要先寫出上面的標頭和表頭：

- **ID** — `TD-` 加三位數字，比登記表裡現有的最大 ID 大一（新登記表從 `TD-001` 開始）。ID 絕對不重複使用。
- **Category** — Scan Mode 底下六個類別之一，不加「Debt」來寫：`Architecture`、`Code Quality`、`Test`、`Documentation`、`Dependency`、`Performance`，跟 `/story-done` 寫的拼法一致，這樣 Report Mode 才能把它們歸成同一組。
- **Description** — 這筆債是什麼，以及為什麼會背上它。
- **Files** — 受影響的路徑，用逗號分隔；債務沒有單一檔案時寫 `—`。
- **Effort** — `S`、`M`、`L` 或 `XL`，跟 Add Mode 一樣；還沒估算就寫 `—`。
- **Impact** — `Low`、`Med`、`High` 或 `Critical`：不修的話要付出的代價；還沒判斷就寫 `—`。
- **Priority** — `/tech-debt prioritize` 寫入的分數；在它跑之前是 `—`。
- **Status** — 新增時是 `Open`。`Resolved YYYY-MM-DD` 記錄債務被修掉的那天；`Accepted — reason` 記錄有意識地決定留著它。
- **Added** — 這列被寫入的那天，`YYYY-MM-DD`。Report Mode 依這個日期和 `Resolved` 日期，統計新增與已解決的項目。
- **Sprint** — 排定要修它的 sprint，或 `Backlog`。

### Rules
- 技術債本身不是壞事，它是一種工具。登記表追蹤的是有意識的決定。
- 每一筆債務條目都必須說明為什麼接受它（deadline、原型、資訊不足）
- 「Scan」至少每個 sprint 跑一次，才能抓到新的債務
- 超過 3 個 sprint 都沒動作的項目，要嘛修掉，要嘛附上書面理由有意識地接受
