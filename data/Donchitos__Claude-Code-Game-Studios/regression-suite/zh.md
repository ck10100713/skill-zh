---
name: regression-suite
description: "把測試覆蓋對應到 GDD 的關鍵路徑，找出修過 bug 卻沒有 regression 測試的地方，並標記新功能造成的漂移。"
argument-hint: "[update | audit | report]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(bash "*/.claude/skills/regression-suite/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation,workflow,qa.level,system_overrides`

上面已經解析好了，直接用。沒有這個區塊的話，用
`.claude/docs/config-resolution.md` 裡的預設值。


# Regression Suite

這個 skill 確保每一個 bug 修復，背後都有一個本來就能抓到原始
bug 的測試 — 而且讓 regression suite 隨著
遊戲演進保持最新。它也會偵測新功能加進來時，
沒有對應 regression 覆蓋的情況。

regression suite 不是新的測試類別 — 它是一份**精選的、
已經在 `tests/` 裡的測試清單**，合起來涵蓋遊戲的關鍵路徑
和已知的失敗點。這個 skill 負責維護那份清單。

**輸出：** `tests/regression-suite.md`

**什麼時候執行：**
- 修完 bug 之後（確認有寫 regression 測試，或找出缺口）
- phase gate 之前 — 在 `qa.level: full`，`/gate-check` 要求要有 regression suite
- 當成 sprint 收尾的一部分，偵測覆蓋漂移

---

每一次 `AskUserQuestion` 呼叫都遵循 `.claude/docs/automation-modes.md`
（collaborative 一律問 · guided 只問重大的 · autonomous 只記錄然後繼續；
`automation_always_ask` 的類別一律要問）。

**Workflow tier**：上面解析出來的 `modes.workflow` — 除非明確設定，
否則由 `modes.rigor` 提供 — 依 `.claude/docs/workflow-modes.md`；在 `audit` 模式下，讀每個 GDD 時，
要逐個 system 考慮
`workflow_overrides.system_overrides.<system>`。它
決定是要對應 GDD 的關鍵路徑，還是覆蓋範圍只有 smoke — 見 Step 2c。

**`qa.level`**：控制要不要產生這個 suite。
在 `minimal`，regression suite **不產生**（回報這點然後
停下來）；在 `standard`，在進入 Polish 階段時產生；在 `full`，在
進入 Production 階段時產生。這是跟 `workflow` 不同的軸。

## 1. Parse Arguments

**提早的 `qa.level` 防護（上面解析出來的）：** 如果 `qa.level: minimal`，
regression suite **不產生** — 回報「Regression suite not generated at
qa.level minimal」，並在**任何掃描之前就停在這裡**，每個模式都一樣
（`update` / `audit` / `report`）。這是 `qa.level` 軸；它跟
Step 2c 裡 `workflow` tier 的 `minimal` 分支不一樣（那個只改變
關鍵路徑的*來源*，不改變 suite *要不要*執行）。不要因為 `qa.level`
就進入 Step 2c 的 `minimal` 分支。這個停止的判定是
**NOT ASSESSED**（Section 7）— 這個等級不需要測試，而且什麼都沒掃描。

**Modes：**
- `/regression-suite update` — 掃描這個 sprint 新修的 bug，檢查
  有沒有 regression 測試；把新測試加進 suite manifest
- `/regression-suite audit` — 完整稽核所有 GDD 關鍵路徑 vs.
  既有的測試覆蓋；標記沒有 regression 測試的路徑
- `/regression-suite report` — 唯讀的狀態報告（不寫入）；適合
  sprint 審查
- 沒有參數 — 如果 sprint 明顯在進行中（有 sprint plan，而且有進行中的 story），就跑 `update`。如果不明確，或偵測不到進行中的 sprint，就用 `AskUserQuestion`：
  - Prompt: "No subcommand specified. Which mode do you want to run?"
  - Options:
    - `[A] update — scan new bug fixes this sprint and add missing regression tests`
    - `[B] audit — full audit of all GDD critical paths vs. existing test coverage`
    - `[C] report — read-only status report (no writes)`

---

## 2. Load Context

### Step 2a — Load existing regression suite

如果 `tests/regression-suite.md` 存在就讀它。擷取：
- 已登記的 regression 測試總數
- 最後更新日期
- 任何被標記成 `STALE` 或 `QUARANTINED` 的測試

如果它不存在：註明「No regression suite found — will create one.」

### Step 2b — Load test inventory

用 Glob 找所有測試檔：
```
tests/unit/**/*_test.*
tests/integration/**/*_test.*
tests/regression/**/*
```

對每個檔案，記下 system（從目錄路徑）和檔名。
除非為了把名稱對應到測試而需要，否則不要讀測試檔的內容。

### Step 2c — Load GDD critical paths

對 `audit` 模式：讀 `design/gdd/systems-index.md` 取得所有 system，然後
依每個 system 的 workflow tier（上面解析出來的）限縮掃描範圍：
- **`full`** — 讀 GDD，並從所有章節對應關鍵路徑。
- **`standard`** — 同上，但從必要章節（Acceptance Criteria、Edge
  Cases，以及 system 定義了數值規則時的 Formulas）。
  透過 `system_overrides` 被釘在較高 tier 的 system，用它較高的 tier 來對應。
- **`minimal`** — **跳過 GDD 關鍵路徑掃描**。改讀
  `production/qa/smoke-*.md` 裡最新的 smoke-check 報告，並把它所涵蓋的
  關鍵路徑當成 regression 範圍（Step 3 對照那些路徑來對應覆蓋，不是 GDD
  驗收條件）。如果沒有 smoke 報告，就停下來，Verdict: **NOT
  ASSESSED — no smoke report to take critical paths from** — 在 minimal 沒有它就沒有
  關鍵路徑的來源；先執行 `/smoke-check`。

（Tier 只影響 `audit` 模式；`update` 和 `report` 模式跟 tier 無關。）

依章節讀每個 GDD：用 Grep 工具（pattern
`^#`，content mode）找出你需要的標題，再用 offset 和 limit 讀那幾段範圍。在 `full`，那
就是每個章節，分段讀，因為超過 40 KB 的整檔 Read 會被拒絕。

對每個在範圍內的 MVP tier system 的 GDD，擷取：
- Acceptance Criteria（它們定義了關鍵路徑）
- Formulas 章節（公式必須有 regression 測試）
- Edge Cases 章節（已知的邊界案例應該有 regression 測試）

對 `update` 模式：跳過完整的 GDD 掃描。改讀目前的 sprint plan
和 story 檔，找出這個 sprint 中 Status: Complete 的 story。

### Step 2d — Load closed bugs

用 Glob 找 `production/qa/bugs/*.md`，篩選出有 `Status: Closed`
或 `Status: Fixed` 欄位的 bug。記下：
- bug 是出在哪個 story 或 system
- 修復描述裡有沒有提到 regression 測試

---

## 3. Map Coverage — Critical Paths

只用於 `audit` 模式。（在 `minimal`，關鍵路徑來自 Step 2c 裡找到的 smoke-check
報告，不是 GDD 驗收條件 — 對照那些 smoke 路徑來對應覆蓋，
並跳過下面的 GDD 條件迴圈。）

對每個 GDD 驗收條件，判斷有沒有測試存在：

1. 用 Grep 在 `tests/unit/[system]/` 和 `tests/integration/[system]/` 裡找跟條件的關鍵
   名詞/動詞有關的檔名和函式名稱
2. 指派覆蓋狀態：

| Status | Meaning |
|--------|---------|
| **COVERED** | A test file exists that targets this criterion's logic |
| **PARTIAL** | A test exists but doesn't cover all cases (e.g. happy path only) |
| **MISSING** | No test found for this critical path |
| **EXEMPT** | Visual/Feel or UI criterion — not automatable by design |

3. 把對應到公式或狀態機的 MISSING 項目提升為
   **HIGH PRIORITY** 缺口 — 這些最有可能是 regression 的來源。

---

## 4. Map Coverage — Fixed Bugs

對每個已關閉的 bug：

1. 從 bug 的 metadata 擷取 system slug
2. 用 Grep 在 `tests/unit/[system]/` 和 `tests/integration/[system]/` 裡找
   參照了 bug ID 或那個具體失敗情境的測試
3. 指派：
   - **HAS REGRESSION TEST** — 找到了能抓到這個 bug 的測試
   - **MISSING REGRESSION TEST** — bug 修好了，但沒有測試防止它再次發生

對 MISSING REGRESSION TEST 的項目：
- 把它們標記成 regression 缺口
- 建議測試檔路徑：`tests/unit/[system]/[bug-slug]_regression_test.[ext]`
- 註明：「Without this test, this bug can silently return in a future sprint.」

---

## 5. Detect Coverage Drift

覆蓋漂移發生在遊戲成長了，但 regression suite 沒有跟上的時候。

檢查漂移的跡象：
- 這個 sprint 完成的 story，在 `tests/` 裡沒有對應的測試檔
- 自從上次更新 regression suite 之後，新加進 `systems-index.md` 的系統
- 自從上次更新 regression suite 之後，新增或修訂過的 GDD 章節
  （如果有的話，用 Grep 看 GDD 檔案的修改線索，或者問使用者）
- `tests/regression-suite.md` 的最後更新日期 vs. 目前日期 — 如果差距 >
  2 個 sprint，就標記為可能已經過時

---

## 6. Generate Report and Suite Manifest

### Report format (in conversation)

```
## Regression Suite Status

**Mode**: [update | audit | report]
**Existing registered tests**: [N]
**Test files scanned**: [N]

### Critical Path Coverage (audit mode only)
| System | Total ACs | Covered | Partial | Missing | Exempt |
|--------|-----------|---------|---------|---------|--------|
| [name] | [N] | [N] | [N] | [N] | [N] |

**Coverage rate (non-exempt)**: [N]%

### Bug Regression Coverage
| Bug ID | System | Severity | Has Regression Test? |
|--------|--------|----------|----------------------|
| BUG-NNNN | [system] | S[N] | YES / NO ⚠ |

**Bugs without regression tests**: [N]

### Coverage Drift Indicators
[List new systems or stories with no test coverage, or "None detected."]

### Recommended New Regression Tests
| Priority | System | Suggested Test File | Covers |
|----------|--------|---------------------|--------|
| HIGH | [system] | `tests/unit/[system]/[slug]_regression_test.[ext]` | BUG-NNNN / AC-[N] |
| MEDIUM | [system] | `tests/unit/[system]/[slug]_test.[ext]` | [criterion] |
```

### Suite manifest format (`tests/regression-suite.md`)

> **在計算覆蓋率之前，先檢查分母。** 如果 GDD
> glob 回傳**零個關鍵路徑**，或測試 glob 回傳**零個測試
> 檔**，就不要輸出百分比 — 回報
> `Coverage: NOT ASSESSED — [no GDDs found | no test files found]`，並點名是哪一邊
> 是空的，以及產生它的 skill（GDD 用 `/map-systems` 和
> `/design-system`，測試骨架用 `/test-setup`）。
>
> 用空的分母算出來的百分比，不是低分；它根本不是
> 數字。`0%` 讀起來像「量過了，而且很糟」，`100%` 讀起來像「量過了，而且完美」—
> 兩者都是在宣稱一個從來沒發生過的比較。這跟 `/scope-check` 在 Phase 4 用
> 同樣的措辭防範的缺陷是同一個：
> *「a percentage computed from no baseline items is not a small number; it is not
> a number.」*

manifest 是精選的索引 — 不是測試本身，而是
一份登記冊，記錄哪些測試在 release 之前應該一律通過：

```markdown
# Regression Suite Manifest

> Last Updated: [date]
> Total registered tests: [N]
> Coverage: [N]% of GDD critical paths

## How to run

[Engine-specific command to run all regression tests]

## Registered Regression Tests

### [System Name]

| Test File | Test Function (if known) | Covers | Added |
|-----------|--------------------------|--------|-------|
| `tests/unit/[system]/[file]_test.[ext]` | `test_[scenario]` | AC-N / BUG-NNNN | [date] |

## Known Gaps

Tests that should exist but don't yet:

| Priority | System | Suggested Path | Covers | Reason Not Yet Written |
|----------|--------|----------------|--------|------------------------|
| HIGH | [system] | `tests/unit/[system]/[path]` | BUG-NNNN | Bug fixed without test |

## Quarantined Tests

Tests that are flaky or disabled (do not run in CI):

| Test File | Function | Reason | Quarantined Since |
|-----------|----------|--------|-------------------|
| (none) | | | |
```

---

## 7. Write Output

在 `update` 或 `audit` 模式，問：「May I write/update `tests/regression-suite.md` with the current
regression suite manifest?」

對 `update` 模式：附加新條目；絕對不要移除既有條目
（用 `Edit` 做有針對性的插入）。
對 `audit` 模式：用更新過的覆蓋資料重寫整份 manifest。
對 `report` 模式：什麼都不寫。

寫完之後（如果有核准）：

- 對每個 HIGH priority 缺口：「Consider creating the missing regression test
  before the next sprint. Run `/test-helpers` to scaffold the test file.」
- 如果 bug 的 regression 缺口 > 0：「These bugs can silently return without regression
  tests. The next sprint should include a story to write the missing tests.」
- 如果偵測到覆蓋漂移：「Regression suite may be drifting. Consider
  running `/regression-suite audit` at the next sprint boundary.」

在沒有 sprint 的 `workflow: minimal`，上面三行裡把「next sprint」改說「next story」。

判定，第一個符合的條件勝出：
- **NOT ASSESSED** — Section 1 在 `qa.level: minimal` 的停止：「Regression
  suite not generated at qa.level minimal」。這個等級不需要
  測試；什麼都沒掃描，也沒寫入。
- **NOT ASSESSED** — 上面的 `minimal` 停止：沒有 smoke 報告可以取得關鍵
  路徑；點名 `/smoke-check` 作為修法。
- **NOT ASSESSED** — 覆蓋率回傳 `Coverage: NOT ASSESSED — [reason]`（沒有 GDD 或
  沒有測試檔）；點名原因。絕對不要在沒算出來的覆蓋率數字上
  回報 COMPLETE。
- **BLOCKED** — `update` 或 `audit` 模式，而且使用者拒絕寫入。
- **COMPLETE** — `update` / `audit`：regression suite 已更新；`report`：覆蓋
  報告已顯示（report 模式不寫任何東西）。

---

## Collaborative Protocol

**適用於 `collaborative` 模式（預設）。** `guided` 和
`autonomous` 模式請見 `.claude/docs/automation-modes.md` — 下面的規則
描述的是 collaborative 模式的要求，不是通用行為。

- **沒有使用者的明確核准，絕對不要從 manifest 移除既有的 regression 測試** —
  移除一個刻意寫下來的測試，本身就是 regression 風險
- **缺口是建議性的，不是阻擋性的** — 清楚地呈現它們，但不要阻止
  其他工作繼續（除了 `qa.level: full`，那裡 phase gate 要求要有 regression suite）
- **Quarantine 不是刪除** — 間歇性失敗的測試應該被
  quarantine（在 manifest 裡註明），而不是移除；它們應該由
  `/test-flakiness` 修好
- **寫入前先問** — 建立或更新 manifest 之前一律先確認
