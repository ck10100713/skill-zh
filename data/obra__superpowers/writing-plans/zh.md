---
name: writing-plans
description: 當你有多步驟任務的規格或需求，在動手碰程式碼之前使用
---

# Writing Plans

## 概述

為一位沒看過這個程式碼庫、也沒看過這份規格的工程師寫實作計畫。假設他們一旦知道確切的 interface 和確切的測試，就會用專案所用語言的慣用寫法寫程式，而且在計畫留白的地方，他們會做出合理的選擇。他們沒辦法知道的，是你決定了什麼：哪些檔案、哪些名稱和簽章、規格裡的哪些值、哪些測試證明每個任務。把這些寫下來。把整份計畫拆成一口大小的任務交給他們。DRY。YAGNI。TDD。頻繁 commit。

**開始時宣告：**「I'm using the writing-plans skill to create the implementation plan.」

**Context：** 如果在隔離的 worktree 裡工作，它應該已經在執行時，透過 `superpowers:using-git-worktrees` skill 建立好了。

**計畫存放位置：** `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`
- （使用者對計畫位置的偏好，優先於這個預設值）

## 範圍檢查

如果規格涵蓋多個獨立的子系統，它在 brainstorming 時就應該被拆成子專案的規格。如果沒有，建議把它拆成各別的計畫，每個子系統一份。每份計畫單獨就應該能產出可運作、可測試的軟體。

## 檔案結構

定義任務之前，先畫出哪些檔案會被建立或修改，以及每個檔案負責什麼。拆解的決定就在這裡鎖定。

- 設計邊界清楚、interface 定義明確的單元。每個檔案都該有一個明確的職責。
- 你對能一次放進 context 的程式碼推理得最好，而且檔案聚焦時，你的修改也更可靠。偏好較小、聚焦的檔案，而不是做太多事的大檔案。
- 一起改動的檔案應該放在一起。依職責拆分，不要依技術層拆分。
- 在既有的程式碼庫裡，遵循已建立的模式。如果程式碼庫用的是大檔案，不要單方面重組，但如果你要修改的檔案已經長到難以掌控，把拆分納入計畫是合理的。

這個結構會影響任務的拆解。每個任務都應該產出自成一體的改動，獨立來看也說得通。

## 任務大小

一個任務是帶有自己測試循環、而且值得讓全新 reviewer 把關的最小單位。劃定任務邊界時：把設定、組態、腳手架和文件的步驟，併進交付物需要它們的那個任務；只有在 reviewer 能有意義地否決一個任務、同時核准它隔壁的任務時，才拆開。每個任務都以一個可獨立測試的交付物收尾。

## 步驟粒度

**每個步驟是一個動作，帶有可檢查的結果：**
- 「Write the failing test」：一個步驟
- 「Run it to make sure it fails」：一個步驟
- 「Implement the minimal code to make the test pass」：一個步驟
- 「Run the tests and make sure they pass」：一個步驟
- 「Commit」：一個步驟

## 計畫文件的標頭

**每份計畫「一定要」以這個標頭開頭：**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

**Spec:** [path to the spec/design doc this plan implements — the plan
argues from the spec, so the spec travels with it; executors read both]

## Global Constraints

[The spec's project-wide requirements — version floors, dependency limits,
naming and copy rules, platform requirements — one line each, with exact
values copied verbatim from the spec. Every task's requirements implicitly
include this section.]

## Review Focus

[The five input classes or failure modes the spec implies but no task's
tests exercise that are most likely to bite a person using this software
— one line each, naming the input or condition and the behavior a
reasonable person would expect, most likely first. The spec is a vision
document: it says what the software must do, not everything it will
meet, and its silence on an input is not permission for that input to
break the program. Write the list here, once, with the spec in front of
you. Then, for each line, add the test that pins it to the task that
owns the code, in that task's own step style.]

---
```

## 任務結構

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Interfaces:**
- Consumes: [what this task uses from earlier tasks — exact signatures]
- Produces: [what later tasks rely on — exact function names, parameter
  and return types. A task's implementer sees only their own task; this
  block is how they learn the names and types neighboring tasks use.]

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Implement `function(input: InputType) -> ResultType` in `exact/path/to/file.py`**

One line on the approach when the signature and the test leave a choice
(which library call, which data structure); a code block only for an
algorithm they do not determine.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## 一個步驟包含什麼

當 implementer 能從步驟中寫出「恰好一件」合理的事，這個步驟就完成了。這就是全部的要求：無歧義，不是完整。每一種步驟，只帶著讓它無歧義的東西，不多帶：

- **測試步驟：** 測試的名稱和它的斷言，寫成程式碼，裡面放規格的確切值。
- **程式碼步驟：** 確切的簽章（名稱、參數、回傳型別）、它所在的檔案，以及規格釘死的特定值。Implementer 寫函式本體。只有在簽章和測試沒有決定的演算法，或規格固定的確切文案，才會出現本體。
- **驗證步驟：** 要執行的指令，以及代表通過的輸出。
- **參照另一個任務：** 該任務的 Interfaces 區塊會說明要用什麼；計畫不重複那個任務的程式碼。

計畫就是 implementer 沒辦法獨自做的決定的集合。比它所描述的程式碼還長的計畫，是把程式碼寫成了計畫。什麼都沒決定的行（「TBD」、「handle edge cases」、「add appropriate validation」、「write tests for the above」、沒有任何任務定義的型別或函式）則是相反的失敗，自我審查要抓出這兩種。

## 自我審查

寫完整份計畫之後，用全新的眼光看規格，並對照規格檢查計畫。這是你自己跑的檢查表，不是派 subagent。

**1. 規格涵蓋：** 略讀規格的每個段落／需求。你能指出實作它的任務嗎？列出任何缺口。

**2. 步驟掃描：** 每個步驟都必須讓 implementer 寫出恰好一件合理的事，而且任何步驟都不能帶超過這個：什麼都沒決定的行是缺口，簽章和測試已經決定了的函式本體，則是照抄的逐字稿。兩種都要修。

**3. 型別一致性：** 你在後面任務用的型別、方法簽章和屬性名稱，跟你在前面任務定義的一致嗎？Task 3 呼叫 `clearLayers()`，Task 7 卻叫 `clearFullLayers()`，就是 bug。

**4. Review Focus：** 對規格暗示的每個輸入類別或失敗模式，有沒有哪個任務的測試涵蓋它？最可能咬到使用者的那五個沒涵蓋的，放進 Review Focus 區段，而且那裡每一行，都要把它的測試加到擁有該程式碼的任務裡。空的區段表示你檢查過、而且沒找到，不是表示你跳過了檢查。

**5. 比例：** 把計畫的長度跟規格比較。比它所實作的規格長好幾倍的計畫，是程式的逐字稿，不是計畫。如果程式碼區塊佔了文件的大部分，就把本體換成簽章、測試名稱和斷言，並確認每個步驟仍然無歧義。

如果發現問題，就當場修。不需要重新審查，修好就繼續。如果你發現有規格需求沒有對應的任務，就加上那個任務。

## 執行交接

儲存並自我審查完計畫之後，附上連結讓你的搭檔去讀。如果他們已經明確指定了執行方式，就請他們審閱計畫，並確認它符合他們想要的；實作之前先等那次審閱，然後使用保留下來的方式。否則，就請他們審閱計畫，並在實作之前選擇執行方式。

**當還沒有指定任何執行方式時：**

**「Plan complete and saved to `docs/superpowers/plans/<filename>.md`. Please review the plan. Which execution approach would you prefer?**

- **Subagent-driven** - A fresh subagent implements each task and a fresh reviewer checks it before the next one starts, then a whole-branch review at the end. Most thorough; costs a fresh context per task and per review.
- **Native** - I implement every task myself in this session, the way this harness runs work, then one fresh reviewer on the most capable model checks the whole branch. Cheapest and fastest; no independent review until the end. Runs well with a mid-tier session model, since the plan carries the design.

**For this plan I recommend <one of the two>, because <one sentence from the plan: how much the tasks depend on each other's interfaces, how many there are, what a shipped mistake would cost>. Does the plan capture what you want, and which approach should we use?」**

**當已經指定了執行方式時：**

**「Plan complete and saved to `docs/superpowers/plans/<filename>.md`. Please review the plan. Does it capture what you want?」**

**如果選了 Subagent-driven：**
- **必要的子 skill：** 使用 superpowers:subagent-driven-development

**如果選了 Native：**
- **必要的子 skill：** 使用 superpowers:executing-plans
