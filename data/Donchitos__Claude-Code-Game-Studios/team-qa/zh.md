---
name: team-qa
description: "統籌 QA 團隊跑完整測試週期：qa-lead 訂策略與測試計畫、qa-tester 寫測試案例、執行、簽核。"
argument-hint: "[sprint | feature: system-name] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Agent, AskUserQuestion, Bash(bash "*/.claude/skills/team-qa/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

# Team QA

呼叫這個 skill 時，用結構化的測試週期來統籌 QA 團隊。

**決策點：** 每個 phase 轉換時，用 `AskUserQuestion` 把 subagent 的提案做成可選項目給使用者選。先在對話中寫出 agent 的完整分析，再用簡短的標籤收下決定。
在 `collaborative` 模式下，使用者核准後才能進下一個 phase。
在 `guided` 模式下，pipeline 會自動往下走，除非某個 phase BLOCKED；
在 `autonomous` 模式下會從頭跑到尾，每個 phase 的結果用 `log_decision` 記錄下來。
屬於 `automation_always_ask` 類別的決策（`is_always_ask_category` helper）不管什麼模式一律要問。參見 `.claude/docs/automation-modes.md`。

## Phase 0: Resolve Config

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,team.size,qa.level`

上面已經解析好了，直接用；`--review` 會覆蓋 `review_mode`。沒有這個區塊的話，就用 `.claude/docs/config-resolution.md` 裡的預設值。

`qa.level` 決定 Logic、Integration 或 Config/Data story 的佐證是什麼：在 `standard` 和 `full` 下是它的自動化測試；在 `minimal` 下測試被免除（`.claude/docs/coding-standards.md`），佐證就是 Phase 5 的驗收標準逐項走查，沒有測試的 story 這時是 WAIVED，不是缺佐證。UI 和 Visual/Feel 的截圖在每個層級都必須要有。

`review_mode` 決定 director gate 的深度，而這條 pipeline 沒有 director gate：
下面任何 phase 在任何 `review_mode` 下，都不會 spawn CD-、TD-、PR- 或 AD-PHASE-GATE。它的 phase gate 就是 pipeline 自己的決策點（定義在下面的 `team.size` 底下），在這些點上工作的 agent 是團隊成員，不是 director gate。

`automation` 決定上面「決策點」那段的行為。各模式如何改變 pipeline 的行為，見上面的決策點說明和 `.claude/docs/automation-modes.md`。

**`team.size`**：哪些 agent 啟用（跟 review_mode 的 gate 深度和 workflow docs 互相獨立）。
- **`individual`**（預設）：只有 `qa-tester`；`qa-lead` 只在 phase gate 才叫。
- **`small`**：`qa-lead` + `qa-tester` 的 pipeline（如文件所述）。
- **`studio`**：`qa-lead` + 每個 story 各 spawn 一個 `qa-tester` + 簽核。
在 `individual` 下需要用到的非核心 agent，會改由最接近的核心 agent 處理，並附一則說明。**「Phase gate」指的是這條 pipeline 自己列出、以 `AskUserQuestion` 決策點收尾的任何 phase**：可能是上面「決策點」底下的某個轉換，也可能是下面 pipeline 裡寫明的 **Gate** 步驟，**不管 `automation` 是哪個模式都一樣**：在 `guided` 或 `autonomous` 下，那個問題被略過或只是記錄，這個 phase 仍然是 gate。不是每個 phase 都算。要照字面套用這個測試：如果下面某個 phase 沒有列出決策點，它就不是 gate，被限制成「只在 phase gate 出場」的 agent 就不會為它 spawn。這個「依啟用名單縮小範圍」的規則適用於下面整條 pipeline：任何 phase 只要點名了啟用名單以外的 agent，就改由最接近的核心 agent 處理，不 spawn 它。

**在 Phase 1 之前先公布啟用名單，絕對不准讓縮減悄悄發生。**
spawn 任何東西之前，先用一行講清楚這次實際會 spawn 哪些 agent，以及下面 pipeline 有點名、但在目前 `team.size` 下**不會** spawn 的有哪些。例如：

> `Active set (team.size: <resolved>): <the agents listed for that size above>.`
> `Not spawned this run: <every other agent this pipeline names> — consulted`
> `through <nearest active core agent>. Raise team.size (or modes.rigor) to widen.`

內容要直接從上面的 `team.size` 清單和這個檔案自己的 pipeline 所點名的 agent 填，不要照抄範例。每個 orchestrator 這兩組名單都不一樣。
如果解析出來的 size 只在 phase gate 才 spawn 某個 agent（`individual` 下的 `qa-lead`），它要連同這個但書一起列進啟用名單：它是被 spawn 的，不是透過別的 agent 諮詢。

下面這條 pipeline 看起來像多 agent 的 fan-out，但在預設值下其實只有一兩個 agent：`team-release` 點名了十個、只跑一個，`team-narrative` 在五個 phase 裡點名了六個、只跑 `writer` 一個。**這樣縮減是對的**：`team.size` 是以嚴謹度為前提的，預設收窄就是用來省 token 的。
如果不明講，讀的人就分不出「正確縮減過的 run」和「壞掉的 pipeline」，而上面那條「由最接近的核心 agent 處理並附說明」的規則是在路由當下才觸發，從來不會交代整個 run 的樣子。

這跟這個檔案其他地方的「略過的檢查要回報」是同一條規則：**一個有被執行、卻從沒被講出來的限制，對讀輸出的人來說，跟從來沒執行過的限制看起來一模一樣。**

## Team Composition

- **qa-lead** — QA 策略、測試計畫產出、story 分類、簽核報告
- **qa-tester** — 撰寫測試案例、撰寫 bug 報告、手動 QA 文件

## How to Delegate

用 `Agent` 工具把每個團隊成員 spawn 成 subagent：
- `subagent_type: qa-lead` — 策略、規劃、分類、簽核
- `subagent_type: qa-tester` — 撰寫測試案例與 bug 報告

**給每個 agent 的 brief 要精簡，不要整包 context 倒過去。** 共用的輸入只讀**一次**，再把整理過的 brief 直接寫在 prompt 裡：只放每個 agent 真正需要的那幾行，你已經讀過的文件絕對不要只丟檔案路徑（agent 拿到路徑會把整份檔案重讀一遍）。只有你還沒讀、而且只有那個 agent 需要的文件，才給路徑。

**每個 agent 的 prompt 結尾都要加上回傳約定：**「Write your full output to `[path]` — that named path is your write authorisation under the bounded exception below, so write it without a separate approval prompt. Return **only** (1) the path written, (2) a ≤5-bullet summary of decisions, (3) any BLOCKED/CONCERNS items, one line each. Do not restate the documents you read.」沒有這個約定的話，agent 會把它讀過的東西全部倒回這個 session。

> **為什麼這不違反 Collaboration Protocol。** `CLAUDE.md` 要求 agent 在 Write/Edit 之前先問「May I write this to [filepath]?」。這裡 spawn 出來的 subagent **不問**就寫，這是刻意設計的有界例外，不是疏忽，跟 `consistency-check` 附加寫入 `active.md` 是同一個決定。這個例外只在三個條件**同時**成立時才有效：(1) 路徑是**你**在 prompt 裡指定的，所以使用者核准這個 phase 的時候，就等於核准了目的地；(2) 它是 `production/`、`docs/` 或 `tests/` 底下的新產物，絕對不是改既有的原始碼或設定；(3) 產生它的那個 phase 是上面定義的 phase gate，也就是 pipeline 列出在往下走之前以 `AskUserQuestion` 收尾的那種，不管 automation 是什麼模式。這三條以外，agent 一定要先問。**不要靠「每個 subagent 都問一次」來「修」這件事**：每個 agent 每個 phase 都跳一次提示，會讓 orchestrator 根本沒辦法用，這就是這個例外存在的原因。

在 `team.size: studio` 下，Phase 4 會為每個 story 各 spawn 一個 qa-tester，平行執行；低於這個層級，一次 spawn 涵蓋整組。

## Pipeline

### Phase 1: Load Context

做任何事之前，先把完整範圍蒐集起來：

1. 從參數判斷目前的 sprint 或 feature 範圍：
   - 如果參數是 sprint 識別碼（例如 `sprint-03`）：用 Glob 找 `production/sprints/sprint-*.md`，依 sprint 編號比對：`sprint-3`、`sprint-03` 和 `sprint-003` 指的都是 sprint 3（`/sprint-plan` 寫的是 `sprint-NNN.md`）。讀取比對到的檔案。如果有多個符合，用最近修改的那個。
   - 如果參數是 `feature: [system-name]`：用 glob 找出標記了該系統的 story 檔案
   - 如果沒有參數：讀 `production/session-state/active.md` 和 `production/sprint-status.yaml`（如果有的話）來推斷目前啟用的 sprint。如果沒有 sprint（`rigor: minimal` 時就沒有），就問要涵蓋哪個 epic，並用 `feature: [epic-slug]`；不要自己發明一個 sprint

2. 從 `project.yaml` 讀 `project.stage`（退而求其次用 `production/stage.txt`），確認目前的專案階段。

3. **讀取範圍內的未結 bug**：也就是 QA 找出新 bug 之前，已經登記在檔案裡的 bug：跟 `/bug-triage` 一樣，用 grep 抓 `production/qa/bugs/*.md` 裡的 `**Severity**`、`**Status**` 和 `**System**` 這幾行。除非 Status 是 `Closed` 或 `Verified Fixed`，否則這個 bug 就是未結；當它的 System 是範圍內 story 所屬的系統，或它提到某個範圍內的 story 時，它就在範圍內；不確定的話就列進去。這些要以 **Open bugs in scope** 的名義放進 Phase 2 和 Phase 6 的 brief：這裡只要有一個未結的 S1 或 S2，不管 QA 又找到什麼，簽核就已經是 NOT APPROVED（Phase 6）。沒有 bug 檔案就寫「Open bugs in scope: none on file」。

4. 數出找到的 story 數量，並回報給使用者：
   > "QA cycle starting for [sprint/feature]. Found [N] stories. Open bugs in scope: [N — S1: n, S2: n, or none on file]. Current stage: [stage]. Ready to begin QA strategy?"

### Phase 2: QA Strategy (qa-lead)

透過 `Agent` spawn `qa-lead`，檢視所有範圍內的 story 並產出 QA 策略。

把 Phase 1 的 **Open bugs in scope**（ID、嚴重程度、story 或系統）傳給 qa-lead，然後指示它：
- 讀每個 story 檔案
- 把每個 story 依類型分類：**Logic** / **Integration** / **Visual/Feel** / **UI** / **Config/Data**
- 找出哪些 story 需要自動化測試佐證、哪些需要手動 QA；在 `qa.level: minimal` 下沒有任何 story 需要測試：沒有測試的 Logic、Integration 或 Config/Data story，在 Automated Required 欄寫 `WAIVED`，並在手動 QA 中逐項走查它的驗收標準
- 標出任何缺少驗收標準、或缺少測試佐證而會阻擋 QA 的 story
- 估算手動 QA 的工作量（需要幾次測試 session）
- **評估 smoke 狀態之前，先檢查有沒有現成的 smoke check 報告**：用 Glob 找 `production/qa/smoke-*.md`，讀最近修改的那個檔案（如果有找到）。如果有報告，直接用它的 verdict 和發現，不要再去訪問使用者。如果沒有報告，就註記：「No prior smoke check report found — run `/smoke-check sprint` before proceeding.」並把 smoke check 狀態設成 UNKNOWN（為了繼續往下走，視同 PASS WITH WARNINGS）。產出一個 smoke check verdict：**PASS** / **PASS WITH WARNINGS [list]** / **NOT ASSESSED [what did not run]** / **FAIL [list of failures]** / **UNKNOWN (no report found)**
- 產出策略摘要表和 smoke check 結果：

  | Story | Type | Automated Required | Manual Required | Blocker? |
  |-------|------|--------------------|-----------------|----------|

  **Smoke Check**: [PASS / PASS WITH WARNINGS / NOT ASSESSED / FAIL / UNKNOWN] — [source: `production/qa/smoke-[date].md` or "no report found"] — [details if not PASS]

  **Open bugs in scope**: [BUG-ID — S[n] — story or system, one per line; or "none on file"] — an open S1 or S2 is named here as a known failure

如果 smoke check 結果是 **FAIL**，qa-lead 必須醒目地列出失敗項目。smoke check 失敗的話，QA 不能越過策略 phase 往下走。

把 qa-lead 的完整策略呈現給使用者，然後用 `AskUserQuestion`：

```
question: "QA Strategy Review"
options:
  - "Looks good — proceed to test plan"
  - "Adjust story types before proceeding"
  - "Skip blocked stories and proceed with the rest"
  - "Smoke check failed — fix issues and re-run /team-qa"
  - "Cancel — resolve blockers first"
```

smoke check **FAIL**：不要進 Phase 3。把 smoke check 報告裡的失敗項目揭露出來然後停止。使用者必須先修好、重跑 `/smoke-check sprint`，再重跑 `/team-qa`。
smoke check **UNKNOWN**：揭露警告：「No smoke check report found. Recommend running `/smoke-check sprint` before QA. Proceeding with caution.」
smoke check **NOT ASSESSED**：揭露報告所說沒跑的部分：「The last smoke check could not assess [what did not run]. Recommend re-running `/smoke-check sprint` once it can. Proceeding with caution.」然後比照 UNKNOWN 繼續；簽核不能因此而 APPROVED（Phase 6）。
smoke check **PASS WITH WARNINGS**：把警告記下來放進簽核報告，然後繼續。
如果有 blocker：明確列出來。使用者可以選擇跳過被擋住的 story，或取消這個週期。

### Phase 3: Test Plan Generation

用 Phase 2 的策略，產出結構化的測試計畫文件。

測試計畫應該涵蓋：
- **Scope**：sprint／feature 名稱、story 數量、日期
- **Story Classification Table**：來自 Phase 2 的策略
- **Automated Test Requirements**：哪些 story 需要測試檔案、預期在 `tests/` 裡的路徑（`qa.level: minimal` 下沒有：改把被免除的 story 列在 Manual QA Scope 底下）
- **Manual QA Scope**：哪些 story 需要手動走查、以及要驗證什麼
- **Out of Scope**：這個週期明確不測的東西，以及原因
- **Entry Criteria**：QA 開始前必須成立的條件。一律要包含：(1) 在 `production/qa/smoke-*.md` 有 PASS 或 PASS WITH WARNINGS 的 smoke check 報告，(2) build 穩定（啟動時不會 crash），(3) 在 sprint 範圍下，`production/sprint-status.yaml` 裡所有 Must Have story 都是 `in-progress`、`review` 或 `done`；在 `feature:` 範圍下，每個範圍內 story 檔案的 Status 都是 In Progress、In Review 或 Complete。除了這些之外，再加上任何該 sprint 專屬的條件。
- **Exit Criteria**：怎樣算完成一個 QA 週期（所有 story 都是 PASS，或 FAIL 並已登記 bug）

問：「May I write the QA plan to `production/qa/qa-plan-[sprint]-[date].md`?」

核准之後才寫。

### Phase 4: Test Case Writing (qa-tester)

> **Smoke check** 是在 Phase 2（QA Strategy）進行的。如果 smoke check 在 Phase 2 回傳 FAIL，週期在那裡就已經停了。這個 phase 只有在 Phase 2 的 smoke check 是 PASS、PASS WITH WARNINGS、NOT ASSESSED 或 UNKNOWN 時才會跑。

對每個需要手動 QA 的 story（Visual/Feel、UI、沒有自動化測試的 Integration；而在測試被免除的 `qa.level: minimal` 下，則是每個沒有測試的 Logic、Integration 和 Config/Data story：它的案例就是逐項走查它的驗收標準）：

透過 `Agent` spawn `qa-tester`：在 `team.size: studio` 下每個 story 各一個、平行執行；在 `small` 和 `individual` 下，一次 spawn 涵蓋整組。針對每個 story 提供：
- story 檔案路徑
- QA 計畫中跟該 story 有關的部分
- 受測系統的 GDD 驗收標準（如果有的話）
- 指示它撰寫涵蓋所有驗收標準的詳細測試案例
- **輸出路徑：`production/qa/test-cases/[story-slug]-cases.md`。** 要在 prompt 裡明確指名，每個 story 一個。

> **為什麼路徑要寫在這裡，而不是留給 orchestrator。** 上面的有界寫入例外只在「路徑是**你**在 prompt 裡指定的」時才成立。這個 phase 是*平行* spawn agent 的地方，所以沒指名目的地在這裡傷害最大：每個 agent 各自即興決定，兩次 run 就把同一種產物放在兩個不同的地方。這個 phase 一路讀起來都沒問題，直到兩個 agent 需要一個地方放它們的輸出。

每組測試案例應該包含：
- **Preconditions**：開始測試前需要的遊戲狀態
- **Steps**：編號的、不含糊的動作
- **Expected Result**：應該發生什麼
- **Actual Result**：留空，讓測試人員填寫的欄位
- **Pass/Fail**：留空的欄位

在執行之前，把測試案例呈現給使用者審閱。依 story 分組。

每個 story 群組用一次 `AskUserQuestion`（每批 3-4 個）：

```
question: "Test cases ready for [Story Group]. Review before manual QA begins?"
options:
  - "Approved — begin manual QA for these stories"
  - "Revise test cases for [story name]"
  - "Skip manual QA for [story name] — not ready"
```

### Phase 5: Manual QA Execution

逐一走過核准的手動 QA 清單中的每個 story。

把 story 分成每批 3-4 個，每批用一次 `AskUserQuestion`。**等測試人員回答**，而且只記下他們說的：測試人員沒給的結果，絕對不能替他們填。沒人回答的 story 維持未執行，這會讓簽核變成 NOT ASSESSED，除非他們說是 BLOCKED，否則不算 BLOCKED。

```
question: "Manual QA — [Story Title]\n[brief description of what to test]"
options:
  - "PASS — all acceptance criteria verified"
  - "PASS WITH NOTES — minor issues found (describe after)"
  - "FAIL — criteria not met (describe after)"
  - "BLOCKED — cannot test yet (reason)"
```

每個 FAIL 結果之後：用 `AskUserQuestion` 收集失敗描述，然後透過 `Agent` spawn `qa-tester`，在 `production/qa/bugs/` 裡用 `/bug-report` 的格式寫一份正式的 bug 報告，Severity 和 Priority 標籤要跟那個模板列的一模一樣（`S2-High`、`P1-Fix this sprint`……），因為 `/bug-triage` 會解析它們。

**Visual/Feel 或 UI story 每次 PASS 或 PASS WITH NOTES 之後，要把它的佐證記錄在 `production/qa/evidence/`。** 留存下來的截圖就是佐證：請測試人員把 story 碰到的每個畫面或特效各存一張到 `production/qa/evidence/[story-slug]/`，並確認它真的在磁碟上，因為 `/story-done` 檢查的是有沒有留存的圖片，不只是文字說明。UI story 靠這些截圖來結案；Visual/Feel story 另外還需要 lead 的簽核。
然後問「May I write the evidence for [story titles] to
`production/qa/evidence/`?」，每個 story 群組問一次，並依 `.claude/docs/templates/test-evidence.md` 寫出佐證產物 `production/qa/evidence/[story-slug]-evidence.md`，簽核表要原封不動帶進去，並參照那些截圖。如果沒有存任何截圖，就在 Phase 5 的摘要裡點名這個 story 缺少留存佐證，不要寫一份暗示有截圖的文件。

> **這不是可有可無的記帳，這是下一個 skill 用來把關的產物。** `/story-done` 會 glob `production/qa/evidence/` 來找 Visual/Feel 和 UI story 的佐證，並讀簽核表；`/story-readiness`、`/test-evidence-review` 和 `gate-release` 讀的是同一個目錄。寫到別的地方的話，一個 story 可能在這裡通過了完整的手動 QA 週期，卻被 `/story-done` 告知沒有視覺佐證。Visual/Feel 和 UI 的 gate **預設是 BLOCKING**，所以這是個死結：QA 通過了、story 卻無法結案。只有在 `testing.strict.ui` 或 `.visual` 被明確設成 `false` 的地方，它才只是一個讓人困惑的旗標。
>
> 簽核列要保持**不勾選**，除非簽核真的在這個 session 裡發生過。預先勾好核准的佐證檔，比沒有還糟：它把缺少的簽名變成了一筆被記錄下來的簽名。

Bug 報告命名：`BUG-[NNNN].md`，編號方式跟 `/bug-report` 一樣：`production/qa/bugs/` 裡最大的 ID 加一，補零到四位數，這樣 `/bug-report verify` 和 `close` 才能用 ID 找到它。

收集完所有結果之後，做個摘要：
- Stories PASS: [count]
- Stories PASS WITH NOTES: [count]
- Stories FAIL: [count] — bugs filed: [IDs]
- Stories BLOCKED: [count]

### Phase 6: QA Sign-Off Report

透過 `Agent` spawn `qa-lead`，用 Phase 2–5 的所有結果起草簽核報告。**這裡的回傳約定是它回覆中的報告文字，不是檔案：** orchestrator 會在這個 phase 結尾詢問之後自己寫簽核，所以 qa-lead 什麼都不寫。

**給 qa-lead 的 brief 要放佐證和下面的 verdict 規則，絕對不能放 verdict。** 傳入策略表、smoke check 的 verdict 與來源、每個 story 的結果、Phase 5 登記的 bug 和 Phase 1 的 **Open bugs in scope**，以及下面的 verdict 規則，一字不改。不要點名某個 verdict、不要預先填好 `### Verdict:` 那一行，也不要說哪個事實決定了它：qa-lead 要自己把規則套到佐證上。然後在問要不要寫之前，用同一套規則檢查它的 verdict；如果兩邊不一致，就把兩個都秀出來並詢問，絕對不要悄悄換成你自己的。

簽核報告的格式：

```markdown
## QA Sign-Off Report: [Sprint/Feature]
**Date**: [date]

### Test Coverage Summary
| Story | Type | Auto Test | Manual QA | Result |
|-------|------|-----------|-----------|--------|
| [title] | Logic | PASS | — | PASS |
| [title] | Logic | WAIVED (qa.level: minimal) | PASS — criteria walked | PASS |
| [title] | Visual | — | PASS | PASS |
| [title] | Integration | — | BLOCKED | BLOCKED — [reason]; no executed evidence |

### Bugs Found
| ID | Story | Severity | Status |
|----|-------|----------|--------|
| BUG-0001 | [story] | S2 | Open |

[every open bug in scope — those Phase 1 found on file and those filed in Phase 5]

### Verdict: NOT ASSESSED / APPROVED / APPROVED WITH CONDITIONS / NOT APPROVED

**Conditions** (if any): [list what must be fixed before the build advances]

### Next Step
[guidance based on verdict]
```

**範圍內的每個 story 都要在 Test Coverage Summary 有一列**，BLOCKED 和未執行的 story 也包含在內，原因寫在 Result 裡，這樣沒跑過的 story 才不會從報告裡消失。

Verdict 規則：

**順序。** **先檢查 NOT APPROVED**：範圍內只要有任何未結的 S1/S2 bug（Phase 1 就已登記在檔案裡的，跟 Phase 5 登記的一樣算），或有 story FAIL 而沒有記錄在案的 workaround，不管其他還有什麼沒執行，verdict 都是 NOT APPROVED：已知的失敗比未知的優先，把它降級成 NOT ASSESSED 會把它埋掉（`.claude/rules/skill-authoring.md`，obligation 1）。

**然後是前提條件。** APPROVED 和 APPROVED WITH CONDITIONS 都要求**範圍內每個 story 都產出了執行過的佐證**：跑過的測試，或走查過的手動案例。在 `qa.level: minimal` 下，Logic、Integration 或 Config/Data story 的驗收標準走查就是它執行過的佐證：它的測試是 WAIVED，不是缺失。只要有任何 story 是 BLOCKED、未執行或沒有佐證，verdict 就是 **NOT ASSESSED**，不是任何一種 APPROVED。如果 smoke check 在 Phase 2 是 UNKNOWN（找不到報告）或 NOT ASSESSED，也同樣讓它變成 NOT ASSESSED：build 的健康狀況從來沒被檢查過。

- **NOT ASSESSED — NO EVIDENCE**：一個或多個 story 沒有產出執行過的佐證（BLOCKED、在 `qa.level` 為 standard/full 時沒寫測試、案例沒走查，或 smoke check 是 FAIL / UNKNOWN / NOT ASSESSED）。這**不是**通過，也**不是**失敗；它的意思是 QA 根本沒有發生。要講明是哪些 story 以及原因。
- **APPROVED**：所有 story 都是 PASS 或 PASS WITH NOTES；沒有未結的 S1/S2 bug
- **APPROVED WITH CONDITIONS**：有未結的 S3/S4 bug，或有記錄在案的 PASS WITH NOTES 問題；沒有 S1/S2 bug
- **NOT APPROVED**：有任何未結的 S1/S2 bug；或有 story FAIL 而沒有記錄在案的 workaround

> **為什麼要有這個前提條件。** 它下面那三條規則都假設每個 story 最後不是 PASS 就是 FAIL。一個什麼都沒執行的 sprint，不會觸發任何 NOT APPROVED 的條件，還會**空洞地滿足「沒有未結的 S1/S2 bug」**，因為零個執行過的測試，就代表零個觀察到的失敗。照字面讀、又沒有這個前提條件的話，這些規則會讓一個完全沒測過的 build 拿到 APPROVED，而一個基於直覺判成 NOT APPROVED 的 `qa-lead`，會發現規則的字面並不支持它。簽核宣稱的是驗證過的品質；沒有這個前提條件，規則就分不出「驗證過是好的」和「根本沒看過」。

依 verdict 的下一步指引：
- NOT ASSESSED: "QA did not run to completion. Produce the missing evidence — write the Logic tests (at `qa.level` standard/full) or walk the waived stories' acceptance criteria (at `minimal`), walk the manual cases, run `/smoke-check` — then re-run `/team-qa`. Do not advance the build on this verdict."
- APPROVED: "Build is ready for the next phase. Run `/gate-check` to validate advancement."
- APPROVED WITH CONDITIONS: "Resolve conditions before advancing. S3/S4 bugs may be deferred to polish."
- NOT APPROVED: "Resolve S1/S2 bugs and re-run `/team-qa` or targeted manual QA before advancing."

問：「May I write this QA sign-off report to `production/qa/qa-signoff-[sprint]-[date].md`?」

核准之後才寫。

## Error Recovery Protocol

**先驗證產物。** 如果回傳約定指定了路徑，在把這個 phase 當成做完之前，先確認該路徑真的存在：**指名的產物不在磁碟上，就是失敗的 phase，不管回覆讀起來多流暢。** agent 可能耗掉整個 phase，回你一段看似合理的開場白，卻什麼都沒寫；這既不是 BLOCKED、也不是錯誤、也不是「無法完成」，所以下面的觸發條件永遠不會被觸發。要叫它繼續，並指明沒達成的約定；context 通常還在。

如果任何 spawn 出去的 agent 回傳 BLOCKED、出錯或無法完成：**立刻揭露，不要越過它所阻擋的依賴項繼續往下走，而且一定要產出部分報告。** 完整流程：`.claude/docs/error-recovery-protocol.md`。

常見的阻擋原因：
- 輸入檔案缺失（找不到 story、GDD 不存在）→ 導向建立它的 skill
- ADR 狀態是 Proposed → 不要實作；決定之後，用 `/architecture-decision accept ADR-NNNN` 接受它
- 範圍太大 → 用 `/create-stories` 拆成兩個 story
- ADR 和 story 的指示互相衝突 → 把衝突揭露出來，不要猜

## Output

一份摘要，涵蓋：範圍內的 story、smoke check 結果、手動 QA 結果、登記的 bug（附 ID 和嚴重程度），以及最終的 APPROVED / APPROVED WITH CONDITIONS / NOT APPROVED / NOT ASSESSED verdict。

Verdict: **COMPLETE** — QA cycle finished.
Verdict: **BLOCKED** — smoke check failed or critical blocker prevented cycle completion; partial report produced.

## Session State Update

最後一個 phase 完成之後（簽核報告寫好，或得出 BLOCKED verdict），悄悄地把這行附加到 `production/session-state/active.md`：

```
<!-- QA RUN: [date] | Sprint: [sprint identifier or "ad-hoc"] | Verdict: [APPROVED/APPROVED WITH CONDITIONS/NOT APPROVED/NOT ASSESSED/BLOCKED] | Report: production/qa/qa-signoff-[sprint]-[date].md -->
```
