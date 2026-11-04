---
name: scope-check
description: "範圍蔓延檢查：目前的範圍對比原始計畫。標出新增項目、量化膨脹程度、建議要砍什麼。'Any scope creep?'"
argument-hint: "[feature-name or sprint-N]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Bash(git log *)
model: haiku
---

# Scope Check

這個 skill 是唯讀的：它會回報發現，但不寫任何檔案。

比對原本規劃的範圍和目前的狀態，偵測、量化並分級
範圍蔓延（scope creep）。

**參數：** `$ARGUMENTS`：整個字串，可以是功能名稱（可能是好幾個字）、sprint 編號或 milestone 名稱。

---

## Phase 1: Find the Original Plan

針對給定的參數，找出基準的範圍文件：

- **功能名稱** → 讀 `design/gdd/[feature].md` 或 `design/` 裡符合的檔案
- **Sprint 編號**（例如 `sprint-3`）→ 讀 `production/sprints/sprint-003.md`（`/sprint-plan` 寫出來的名稱）或類似檔案
- **Milestone** → 讀 `production/milestones/[name].md`

如果找不到文件，回報缺少的檔案然後停下來。沒有
可以比對的基準就不要繼續。要分段讀 GDD：用
Grep 工具（pattern `^#`、content mode）找出你需要的標題，再用 offset 和
limit 讀那些範圍。

---

## Phase 2: Read the Current State

檢查實際上已經實作或進行中的東西：

- 掃描程式碼庫中跟這個功能/sprint 有關的檔案
- 讀 git log 中跟這項工作有關的 commit（`git log --oneline --since=[start-date]`）
- 檢查有沒有 TODO/FIXME 註解，這些暗示著尚未完成的範圍新增
- 如果功能在 sprint 中途，檢查目前進行中的 sprint 計畫

---

## Phase 3: Compare Original vs Current Scope

產出比較報告：

```markdown
## Scope Check: [Feature/Sprint Name]
Generated: [Date]

### Original Scope
[List of items from the original plan]

### Current Scope
[List of items currently implemented or in progress]

> **If Phase 4 will return NOT ASSESSED, do not render the numeric block below.**
> Replace the counts and the Bloat Score with
> `[Baseline | Current state] unusable — see verdict` (whichever side could not
> be read) and give the reason. A rendered
> `Original items: 0 / Net scope change: 0%` one section above a NOT ASSESSED
> verdict re-creates the exact "0% reads as on track" hazard Phase 4 exists to
> kill, one phase earlier — and readers trust a number over a caveat.

### Scope Additions (not in original plan)
| Addition | Source | When | Justified? | Effort |
|----------|--------|------|------------|--------|
| [item] | [commit/person] | [date] | [Yes/No/Unclear] | [S/M/L] |

### Scope Removals (in original but dropped)
| Removed Item | Reason | Impact |
|-------------|--------|--------|
| [item] | [why removed] | [what's affected] |

### Bloat Score
- Original items: [N]
- Current items: [N]
- Items added: [N] (+[X]%)
- Items removed: [N]
- Net scope change: [+/-N] ([X]%)

### Risk Assessment
- **Schedule Risk**: [Low/Medium/High] — [explanation]
- **Quality Risk**: [Low/Medium/High] — [explanation]
- **Integration Risk**: [Low/Medium/High] — [explanation]

### Recommendations
1. **Cut**: [Items that should be removed to stay on schedule]
2. **Defer**: [Items that can move to a future sprint/version]
3. **Keep**: [Additions that are genuinely necessary]
4. **Flag**: [Items that need a decision from producer/creative-director]
```

---

## Phase 4: Verdict

依淨範圍變化給出標準結論：

| Net Change | Verdict | Meaning |
|-----------|---------|---------|
| ≤10% | **PASS** | On Track — within acceptable variance |
| >10–25% | **CONCERNS** | Minor Creep — manageable with targeted cuts |
| >25–50% | **FAIL** | Significant Creep — must cut or formally extend timeline |
| >50% | **FAIL** | Out of Control — stop, re-plan, escalate to producer |

**套用上面那張表之前，先檢查這個百分比有沒有意義。** 只要符合下列任一
情況，就輸出 **NOT ASSESSED**，絕對不要輸出算出來的百分比：

- **基準文件存在，但沒有列舉任何範圍項目**（全是標題、
  佔位符，或 `[TO BE CONFIGURED]`）。Phase 1 只在檔案*不存在*時停下來；
  這是檔案存在但內容是空的情況，而且更危險，
  因為零個項目算出 0% 的淨變化，會被呈現成 **PASS — On
  Track**。什麼都沒比對，什麼都沒有「在軌道上」。
- **無法判斷目前的狀態**：沒有相關的原始碼檔案、時間範圍內沒有 commit、
  沒有任何進行中的東西可讀。把真正的基準拿去比一個
  讀不到的現狀，不是 0% 的變化，也不是零個目前項目算出來的 −100%；
  那張表會把兩者都讀成 PASS。
- 分母因為其他任何原因變成零。用沒有任何基準項目算出來的百分比，
  不是一個小數字，它根本不是數字。

`NOT ASSESSED` **優先於 PASS**（沒有發生過的比對，不能證明
範圍在軌道上），**排在 CONCERNS 和 FAIL 之後**（已量測到的蔓延
比無法量測的基準更值得處理）。

把結論顯眼地輸出：

```
**Scope Verdict: [PASS / CONCERNS / NOT ASSESSED / FAIL]**
Net change: [+X%] — [On Track / Minor Creep / Significant Creep / Out of Control]
           [or: NOT ASSESSED — [which side could not be read, and why]]
```

---

## Phase 5: Next Steps

呈現報告之後，提供具體的後續動作：

- **PASS** → 不需要動作。建議在下一個 milestone 之前再跑一次。
- **NOT ASSESSED** → 說明哪一邊讀不到、怎麼修才會讀得到（補上
  基準文件，或把 skill 指向工作實際所在的地方）。
  不要提議用同樣的輸入再跑一次，只會產生一樣
  的非答案。
- **CONCERNS** → 提議找出 2–3 個砍掉效益最高的新增項目。參照 `/sprint-plan update` 來正式重新界定範圍（如果專案沒有 sprint 計畫，像預設的 minimal workflow，就去編輯 brief 的 build order 來重新界定範圍）。
- **FAIL** → 建議升級給 producer。參照 `/sprint-plan update` 重新規劃（如果專案沒有 sprint 計畫，像預設的 minimal workflow，就編輯 brief 的 build order），或用 `/estimate` 重新建立時程基準。

除了 NOT ASSESSED 之外，每個結論都以這句結尾：
> "Run `/scope-check [name]` again after cuts are made to verify the verdict improves."

（NOT ASSESSED 的結尾是上面那段「怎麼做才會變得可評估」；對同樣的輸入
再跑一次，只會重複那個非答案。）

---

### Rules

- 範圍蔓延就是沒有對應的砍減或時程延長的新增項目
- 不是所有新增都不好，有些是後來發現的需求。但它們必須被承認並納入計算
- 建議要砍什麼時，優先保住核心的玩家體驗，其次才是錦上添花的東西
- 一定要量化範圍變化：「感覺變大了」沒辦法行動，「+35% 項目」才可以
