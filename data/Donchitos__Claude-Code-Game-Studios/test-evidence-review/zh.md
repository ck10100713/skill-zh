---
name: test-evidence-review
description: "測試檔案與佐證的品質審查：不只看有沒有，還評估斷言涵蓋度。每個 story 判定為 ADEQUATE/INCOMPLETE/MISSING/NOT ASSESSED。"
argument-hint: "[story-path | sprint | system-name]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Bash(bash "*/.claude/skills/test-evidence-review/../../hooks/yaml-helper.sh" resolve_config *), Bash(bash .claude/scripts/review-receipts.sh check *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation,workflow,qa.level,testing.strict`

**Automation mode**：解析 `modes.automation`（`project.local.yaml` →
`project.yaml` → 預設 `collaborative`）。每一次 `AskUserQuestion` 呼叫和每一次檔案寫入，都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律要問 · guided 只問重大的 · autonomous 記錄後直接往下走；
屬於 `automation_always_ask` 類別的一律要問）。

**`qa.level` 和 `testing.strict`**（上面已解析）決定這個審查可以把什麼稱為 blocker，規則跟 `/story-done` 用來結案 story 的一樣，所以這裡的 BLOCKING 項目，就是會擋住 `/story-done` 的項目：
- **`qa.level: minimal`** 免除測試。沒有測試佐證的 Logic、Integration 或 Config/Data story（Config/Data 的話，是沒有 smoke 報告）是
  `WAIVED (qa.level: minimal)`，不是 MISSING，而且不會產生 BLOCKING 項目；確實存在的測試還是會審查，但它的缺口是 ADVISORY。Visual/Feel 和 UI 的佐證（留存的截圖，以及
  Visual/Feel 的簽核）絕對不會被免除。
- **各 story 類型的 gate 層級**：從解析出來的區塊取 `testing.strict.<type>`（Logic→`logic`、Integration→`integration`、Visual/Feel→`visual`、
  UI→`ui`、Config/Data→`config`）：`true` → BLOCKING，`false` → ADVISORY，`unset`
  → 如果是單純布林值的 `testing.strict: true|false`（舊版格式），就套用到每一種類型；否則用 `.claude/docs/coding-standards.md` 裡的預設 Gate Level
  （Logic、Integration、Visual/Feel 和 UI 是 BLOCKING；
  Config/Data 是 ADVISORY）。下面每一個「BLOCKING」，指的都是那個 story 類型的 gate 層級。

# Test Evidence Review

`/smoke-check` 驗證的是測試檔案**存在**而且**通過**。這個 skill 更進一步：審查這些測試和佐證文件的**品質**。
一個存在而且通過的測試檔案，仍然可能讓關鍵行為沒被涵蓋。
一份存在的手動佐證文件，可能缺少結案所需的簽核。

**輸出：** 摘要報告（在對話中）+ 選用的 `production/qa/evidence-review-[date].md`

**什麼時候跑：**
- QA 交接簽核之前（`/team-qa` Phase 5）
- 任何對測試品質有疑慮的 story
- 當作 milestone 審查的一部分，稽核 Logic 和 Integration story 的品質

---

## 1. Parse Arguments

**模式：**
- `/test-evidence-review [story-path]` — 審查單一 story 的佐證
- `/test-evidence-review sprint` — 審查目前 sprint 的所有 story
- `/test-evidence-review [system-name]` — 審查某個 epic／系統的所有 story
- 沒有參數 — 問要審哪個範圍：「Single story」、「Current sprint」、「A system」

---

## 2. Load Stories in Scope

依參數而定：

**單一 story**：直接讀 story 檔案。擷取：Story Type、Test Evidence 章節、story slug、系統名稱。

**Sprint**：讀 `production/sprints/` 裡最近修改的檔案；從 sprint 計畫中擷取 story 檔案路徑的清單。

**System**：用 Glob 找 `production/epics/[system-name]/story-*.md`。

> **如果解析出來的範圍內有零個 story，就在這裡停止。** 回報
> `NOT ASSESSED — no stories in scope`，指出搜尋的是哪個範圍、哪個路徑是空的，並導向：沒有 sprint 檔案 → `/sprint-plan new`（在沒有 sprint 的 `workflow: minimal` 下，改用 `/test-evidence-review [epic-slug]`）；sprint 計畫沒列出任何 story → `/create-stories [epic-slug]`；`[system-name]` 的 glob 沒比對到任何東西 → 指出那個 glob。不要繼續進 Section 3。
>
> **要防的是空範圍，不只是單一 story 的未知。** 這裡的 verdict 詞彙（ADEQUATE / INCOMPLETE / MISSING）需要一個「無法檢查」的值，否則一個無法驗證的 story 會拿到一個宣稱有人驗證過它的 verdict；這就是 `NOT ASSESSED` 的用途。**但是幫單一 story 的未知找到安身之處，對空範圍的未知一點幫助都沒有。** 沒有 story 的時候，Section 6 的報告會渲染出一個空的 Summary 表，然後以
> `BLOCKING items: 0 / ADVISORY items: 0` 收尾，讀起來像是*全部審查過、全部沒問題*。這個 skill 負責把關 story 結案，而 `coding-standards.md` 把 Logic、Integration、Visual/Feel 和 UI 的佐證標為 BLOCKING，所以一個假的全乾淨，會讓沒人審查過的 story 被結案。

針對得到的 story 集合，用**針對章節的 grep 來蒐集下面的欄位，不要把每個 story 整份讀完**：
```
Grep pattern="## Test Evidence" glob="production/epics/**/story-*.md" output_mode="content" -A 8
Grep pattern="## Acceptance Criteria" glob="production/epics/**/story-*.md" output_mode="content" -A 15
```
- **Story Type**（Logic / Integration / Visual/Feel / UI / Config/Data）和寫明的佐證路徑，兩者都在 `## Test Evidence` 底下，所以第一個 grep 的 `-A 8` 就抓得到。
- 驗收標準清單：第二個 grep 的 `## Acceptance Criteria` 區塊。
- story slug（從檔名）和 System（從目錄路徑），不用讀檔。
只有在 story 的 Test Evidence 章節缺失或含糊時，才整份讀它。
（在 Sprint 模式下，把 glob 限縮在 sprint 計畫列出的 story 路徑。）

---

## 3. Locate Evidence Files

對每個 story，找出佐證。**先檢查 story 寫明的佐證路徑**，也就是 Section 2 從它的 `## Test Evidence` 章節抓到的那個。如果存在，就用它。只有在沒寫明路徑、或找不到的時候，才退回去搜尋：

**Logic story**：在引擎的 unit-test 根目錄搜尋，`tests/unit/[system]/`
（Godot）、`Assets/Tests/EditMode/`（Unity）、`Source/<Module>/Private/Tests/`
（Unreal）；見 `.claude/docs/directory-structure.md`，找檔名含有 story slug 或其系統名稱的檔案。測試檔案是依 `.claude/rules/test-standards.md` 命名的，不一定是 `[story-slug]_test.*`。

**Integration story**：同樣的做法，在 integration 根目錄底下（`tests/integration/[system]/`、
`Assets/Tests/PlayMode/`，或 Unreal 的測試根目錄）
  - 也要檢查 `production/qa/playtests/` 裡有沒有提到這個 story 的試玩紀錄

**Visual/Feel 和 UI story**：用 Glob 在 `production/qa/evidence/` 找屬於這個 story 的留存圖片
（`*.png`、`*.jpg`、`*.gif`），以及 `[story-slug]-evidence.*`

**Config/Data story**：用 Glob 找 `production/qa/smoke-*.md`（任何 smoke check 報告）

記下每個 story 找到了什麼（路徑）或沒找到什麼（缺口）。

---

## 4. Review Automated Test Quality (Logic / Integration)

對找到的每個測試檔案，讀它並評估：

### Assertion coverage

數出不同斷言的數量（含有 assert、expect、check、verify，或引擎專屬斷言寫法的行）。斷言數量少是一個品質訊號：每個測試函式只有 1 個斷言的測試，可能涵蓋不到預期行為的範圍。

門檻：
- **每個測試函式 3 個以上斷言** → 正常
- **每個測試函式 1-2 個斷言** → 標註為可能偏薄
- **0 個斷言**（測試存在、但沒有 assert）→ 標成 BLOCKING（story 類型的 gate 層級；在 `qa.level: minimal` 下是 ADVISORY）：這個測試是空洞地通過，什麼都證明不了

### Edge case coverage

針對 story 裡每一條含有數字、門檻、或「當 X 發生時」條件句的驗收標準：檢查有沒有測試函式名稱或測試內容提到那個特定情況。

啟發式規則：
- 在測試檔案裡 grep「zero」、「max」、「null」、「empty」、「min」、「invalid」、「boundary」、「edge」，有出現任何一個都是正面訊號
- 如果 story 有帶具體上下界的 Formulas 章節：檢查測試有沒有用到最小／最大值

### Naming quality

測試函式名稱應該描述：情境 + 預期結果。
各引擎的寫法（`.claude/rules/test-standards.md`）：Godot
`test_[scenario]_[expected]`、Unity `[Scenario]_[Expected]`、Unreal
`<Project>.[System].[Scenario]`。

把用通用名稱命名的函式（`test_1`、`test_run`、`testBasic`）標成**命名問題**：這會讓失敗更難診斷。

### Formula traceability

對 GDD 有 Formulas 章節的 Logic story：檢查測試檔案至少有一個測試，它的名稱或註解提到公式名稱或公式的某個數值。一個測試了公式、卻沒有用名稱提到它的測試，在公式改動時比較難維護。

---

## 5. Review Manual Evidence Quality (Visual/Feel / UI)

對找到的每份佐證文件，讀它並評估下面的檢查項目。

**UI story 不需要佐證文件。** 沒有的話，它留存的截圖就是佐證：只套用 Screenshot / artefact completeness（這個 story 改動的每個畫面各一張圖，如果某個畫面只是某條標準會導航到的地方，例如 Quit 之後的標題畫面，就不需要它自己的圖）和 Date coverage（圖片的日期）。UI story 在這兩項上通過就是 ADEQUATE，絕對不會因為缺少文件、標準對應或簽核而被判成 INCOMPLETE。

### Criterion linkage

佐證文件應該引用 story 裡的每一條驗收標準。檢查：佐證文件有包含每一條標準（或清楚的改寫）嗎？缺少的標準代表那條標準從來沒被驗證過。

### Sign-off completeness

怎樣才算結案，依照 `.claude/docs/coding-standards.md` 裡的佐證表，也就是 `/story-done` 套用的同一條規則，在每個 `qa.level` 下都一樣：
- **Visual/Feel**：佐證文件（來自 test-evidence 模板）的每一列簽核都必須是
  `[x] Approved`。空白或缺少的列就是 INCOMPLETE。
- **UI**：不需要簽核，留存的截圖就能結案。如果有簽核，就記下來；絕對不要因為沒有簽核，就把 UI story 標成 INCOMPLETE。

### Screenshot / artefact completeness

對 Visual/Feel story：用 Glob 在 `production/qa/evidence/` 找屬於這個 story 的留存圖片
（`*.png`、`*.jpg`、`*.gif`）。一份描述了視覺檢查、卻沒留存任何圖片的文件是 INCOMPLETE：這個 gate 預設是 BLOCKING，而描述只是一個主張，不是佐證。

對 UI story：要求同樣每個被碰到的畫面都有留存的截圖。操作走查紀錄有的話很好，但不是必要的。

### Evidence older than its code

對每個有留存圖片的 story，執行
`bash .claude/scripts/review-receipts.sh check production/qa/evidence/[story-slug]/stamp.txt`。
把每個 `CHANGED:` 或 `GONE:` 的檔案列為 POTENTIALLY STALE：它在佐證被擷取之後改動過。`RECEIPT: NONE`：就說「no stamp」，改用下面的日期檢查。這只是報告裡的一行：它絕對不會改變這個 story 的 verdict。

### Date coverage

佐證文件應該有日期。如果日期早於 story 最後一次大改動（啟發式：跟 sprint 計畫裡的 sprint 開始日期比較），就標成 POTENTIALLY STALE：佐證可能沒涵蓋最終的實作。

---

## 6. Build the Review Report

為每個 story 指派一個 verdict：

| Verdict | Meaning |
|---------|---------|
| **ADEQUATE** | Test/evidence exists, passes quality checks, all criteria covered |
| **INCOMPLETE** | Test/evidence exists but has quality gaps (thin assertions, missing sign-offs) |
| **MISSING** | No test or evidence found for a story type that requires it at this `qa.level` |
| **NOT ASSESSED** | The review could not be performed for this story — see below |
| **WAIVED (qa.level: minimal)** | A Logic, Integration or Config/Data story with no test evidence at `qa.level: minimal` — tests are not required, so nothing is missing; name it as waived |

> **`NOT ASSESSED` 是必要的，它不是比較溫和的 `MISSING`。** 另外三個 verdict 都預設審查真的有跑。`MISSING` 的意思是
> *我看過了，那裡什麼都沒有*，是一個真實、可回報的失敗。它絕對不能被拿來表示*我沒辦法看*，因為那根本不是關於這個 story 的發現。在以下情況使用 `NOT ASSESSED`：
>
> - story 的**類型無法判斷**，所以需要什麼佐證是未知的
>   （`.claude/docs/coding-standards.md` 裡的類型→佐證對應，才是讓其他任何 verdict 有意義的東西）；
> - 佐證路徑有寫明，但**讀不到，或超出這次 run 的範圍**；
> - story 檔案本身無法解析。
>
> **逐個 story 講明是其中哪一種。** 讀的人沒辦法對一個光禿禿的 `NOT ASSESSED` 採取行動，而把它跟 `MISSING` 分開的全部意義，就是兩者的修法不同：一個需要寫測試，另一個需要讓審查者拿到存取權，或把 story 分類。

整個 sprint／系統的 verdict 是出現過的 story verdict 裡最差的那個，而且 **`NOT ASSESSED` 的排序高於 `ADEQUATE`**：一次無法評估部分範圍的 run，沒有確立那個範圍是 adequate 的。它的排序不高於 `INCOMPLETE` 或 `MISSING`：已知的失敗比未知的更能採取行動，把真正的失敗降級到存取問題後面，會把它埋掉。`WAIVED` 的排序低於 `ADEQUATE`：只有範圍內每個 story 都被免除時，整體 verdict 才會是 WAIVED，而不管哪一種情況，報告都要點名每個被免除的 story。

> 為什麼這很重要：佐證審查會**把關 story 結案**，而且
> `coding-standards.md` 把 Logic、Integration、Visual/Feel 和 UI 的佐證標成 BLOCKING。一套沒辦法表達「我沒辦法檢查」的 verdict 詞彙，會逼每個未知都歸進三種關於這個 story 的宣稱之一，這就是一個沒人驗證過的 story，為什麼會拿到一個說有人驗證過的 verdict。

```markdown
## Test Evidence Review

> **Date**: [date]
> **Scope**: [single story path | Sprint [N] | [system name]]
> **Stories reviewed**: [N]
> **Overall verdict**: ADEQUATE / INCOMPLETE / MISSING / NOT ASSESSED / WAIVED
> **qa.level**: [minimal | standard | full] — **testing.strict**: [the resolved per-type values, or "unset — coding-standards.md defaults"]

---

### Story-by-Story Results

#### [Story Title] — [Type] — [ADEQUATE/INCOMPLETE/MISSING/NOT ASSESSED/WAIVED]

**Test/evidence path**: `[path]` (found) / (not found)

**Automated test quality** *(Logic/Integration only)*:
- Assertion coverage: [N per function on average] — [adequate / thin / none]
- Edge cases: [covered / partial / not found]
- Naming: [consistent / [N] generic names flagged]
- Formula traceability: [yes / no — formula names not referenced in tests]

**Manual evidence quality** *(Visual/Feel/UI only)*:
- Criterion linkage: [N/M criteria referenced]
- Lead sign-off: [✓ approved | ✗ missing | deferred — reason] *(Visual/Feel only; a UI story needs none)*
- Artefacts: [screenshots present / missing / N/A]
- Freshness: [dated [date] — current / potentially stale]

**Issues**:
- BLOCKING: [description] *(prevents story-done)*
- ADVISORY: [description] *(should fix before release)*

---

### Summary

| Story | Type | Verdict | Issues |
|-------|------|---------|--------|
| [title] | Logic | ADEQUATE | None |
| [title] | Integration | INCOMPLETE | Thin assertions (avg 1.2/function) |
| [title] | Visual/Feel | INCOMPLETE | Lead sign-off missing |
| [title] | Logic | MISSING | No test file found |
| [title] | Logic | WAIVED | No test — waived at `qa.level: minimal` |

**BLOCKING items** (must resolve before story can be closed): [N]
**ADVISORY items** (should address before release): [N]
```

---

## 7. Write Output (Optional)

在對話中呈現報告。

問：「May I write this test evidence review to
`production/qa/evidence-review-[date].md`?」

這是選用的，報告單獨拿來用就有價值。只有在使用者想要一份留存紀錄時才寫。

報告之後：

- 對 BLOCKING 項目：「These must be resolved before `/story-done` can mark the
  story Complete. Would you like to address any of them now?」
- 對偏薄的斷言：「Consider running `/test-helpers [system]` to see
  scaffolded assertion patterns for common cases.」
- 對缺少的簽核：「Manual sign-off is required from [role]. Share
  `[evidence-path]` with them to complete sign-off.」

Verdict: **COMPLETE** — evidence review finished. 如果發現了 BLOCKING 項目，就用 CONCERNS。

---

## Collaborative Protocol

- **回報品質問題，不要去修** — 這個 skill 只讀取和評估；它不會修改測試檔案或佐證文件
- **ADEQUATE 的意思是夠出貨用，不是完美** — 不要對運作正常、而且夠完整到能讓人有信心的測試吹毛求疵
- **BLOCKING 和 ADVISORY 的區別很重要** — 只有當缺口讓 story 的某條標準確實沒被驗證時，才標成 BLOCKING
- **寫入前要先問** — 報告檔案是選用的；寫之前一定要先確認
