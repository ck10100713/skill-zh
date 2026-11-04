---
name: estimate
description: "依複雜度、相依項目、velocity 和風險來估算任務工時，產出帶信心等級的結構化估算。"
argument-hint: "[task-description]"
user-invocable: true
allowed-tools: Read, Glob, Grep
model: sonnet
---

# Estimate

## Phase 1: Understand the Task

從參數讀取任務描述。如果描述太模糊，沒辦法做有意義的估算，先請對方釐清再繼續。

讀 CLAUDE.md 取得專案脈絡：技術堆疊、coding standard、架構模式，還有任何估算準則。

如果任務跟某個有文件的功能或系統有關，就讀 `design/gdd/` 裡相關的設計文件。要按章節讀：用 Grep 工具（pattern `^#`，content mode）找出你需要的標題，再用 offset 和 limit 讀那幾段範圍。

---

## Phase 2: Scan Affected Code

找出需要改動的檔案和模組：

- 用 Grep 對每個受影響的檔案量測大小和分支數 — 這個 skill 只有 Read、Glob 和 Grep
  三個工具，所以這些計數就是量測：
  - **Size：** `Grep pattern="[^[:space:]]" path="[file]" output_mode="count"` —
    非空白行數。
  - **Branching：** `Grep pattern="(^|[^A-Za-z0-9_])(if|elif|for|foreach|while|match|switch|case|catch)([^A-Za-z0-9_]|$)|&&|[|][|]" path="[file]" output_mode="count"` —
    含有分支或布林運算子的行數。這個計數
    只是 cyclomatic complexity 的近似值（註解和字串也會被算進去）；要講成近似值，
    絕對不要講成實測的複雜度。
  - **Dependencies：** 每個檔案引入了什麼 — `preload`/`load(`（GDScript）、
    `using`（C#）、`#include`（C++）— 以及還有哪些檔案參照它。
  - Grep 算不出來的檔案（不存在、二進位、讀不了），要在 Notes
    and Assumptions 底下點名，不要直接從總數裡漏掉。
- 找出跟其他系統的整合點
- 檢查受影響區域現有的測試覆蓋
- 從 `production/sprints/` 讀過去的 sprint 資料，找類似的已完成任務和歷史 velocity。
  **如果沒有**，要在 Notes and Assumptions 底下講明 — 「No sprint history found;
  this estimate is not calibrated to the team's velocity」— 並且把它當成信心等級裡的風險，
  不要默默把數字加大來墊。

---

## Phase 3: Analyze Complexity Factors

**Code Complexity:**
- 受影響檔案的大小和分支數（Phase 2 的 Grep 計數）
- 相依項目的數量和耦合程度
- 這是動到 core/engine 程式碼，還是 leaf/feature 程式碼
- 能不能沿用現有模式，還是需要新模式

**Scope:**
- 動到的系統數量
- 新增程式碼 vs 修改現有程式碼
- 需要新增多少測試覆蓋
- 需不需要資料遷移或設定變更

**Risk:**
- 新技術或不熟的函式庫
- 需求不清楚或有歧義
- 依賴還沒完成的工作
- 跨系統整合的複雜度
- 對效能敏感

---

## Phase 4: Generate the Estimate

```markdown
## Task Estimate: [Task Name]
Generated: [Date]

### Task Description
[Restate the task clearly in 1-2 sentences]

### Complexity Assessment

| Factor | Assessment | Notes |
|--------|-----------|-------|
| Systems affected | [List] | [Core, gameplay, UI, etc.] |
| Files likely modified | [Count] | [Key files listed below] |
| Size of affected files | [N non-blank lines; M branch lines] | Grep counts; branch lines approximate complexity |
| New code vs modification | [Ratio] | |
| Integration points | [Count] | [Which systems interact] |
| Test coverage needed | [Low / Medium / High] | |
| Existing patterns available | [Yes / Partial / No] | |

**Key files likely affected:**
- `[path/to/file1]` -- [what changes here]

### Effort Estimate

| Scenario | Days | Assumption |
|----------|------|------------|
| Optimistic | [X] | Everything goes right, no surprises |
| Expected | [Y] | Normal pace, minor issues, one round of review |
| Pessimistic | [Z] | Significant unknowns surface, blocked for a day |

**Recommended budget: [Y days]**

### Confidence: [High / Medium / Low]

[Explain which factors drive the confidence level for this specific task.]

### Risk Factors

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|

### Dependencies

| Dependency | Status | Impact if Delayed |
|-----------|--------|-------------------|

### Suggested Breakdown

| # | Sub-task | Estimate | Notes |
|---|----------|----------|-------|
| 1 | [Research / spike] | [X days] | |
| 2 | [Core implementation] | [X days] | |
| 3 | [Testing and validation] | [X days] | |
| | **Total** | **[Y days]** | |

### Notes and Assumptions
- [Key assumption that affects the estimate]
- [Any caveats about scope boundaries]
```

輸出估算時附一段簡短摘要：建議預算、信心等級，以及最大的單一風險因素。

這個 skill 是唯讀的 — 不會寫任何檔案。Verdict: **COMPLETE** — estimate generated.

---

## Phase 5: Next Steps

- 信心等級是 Low：建議在承諾之前先做一個限時的 spike（`/prototype`）。
- 任務超過 10 天：建議用 `/create-stories` 拆成比較小的 story。
- 要排進行程：跑 `/sprint-plan update`，把它加進下一個 sprint（如果專案沒有 sprint plan，像預設的 minimal workflow，就改加進 brief 的 build order）。

### Guidelines

- 一律給範圍（optimistic / expected / pessimistic），絕對不要只給單一數字
- 建議預算要用 expected 的估算，不要用 optimistic 的
- 四捨五入到半天為單位 — 超過一天的任務用小時來估，會給人錯誤的精確感
- 不要默默加估算的水分 — 把風險明講出來，讓團隊自己決定
- 只要做法還沒決定，或核心需求還是 TBD，信心就是 Low — 建立在還沒做的決定上的範圍，就是用猜的
