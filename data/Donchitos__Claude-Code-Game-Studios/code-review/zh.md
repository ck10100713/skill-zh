---
name: code-review
description: "架構層級的 code review：程式碼規範、SOLID、可測試性、效能疑慮。"
argument-hint: "[path-to-file-or-directory]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Bash(git log *), Agent, AskUserQuestion, Bash(bash "*/.claude/skills/code-review/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation`

# Code Review



每一次 `AskUserQuestion` 呼叫都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律詢問 · guided 只問重大事項 · autonomous 記錄後直接往下走；
屬於 `automation_always_ask` 的類別一律要問）。

## 輸入不足：產出任何報告之前先檢查這個

**如果這個 skill 需要的輸入不存在，答案是「跑不了」，
不是一份填好的報告。** 先檢查，檢查不過就停。

1. 列出這個 skill 要讀的輸入（資料檔、先前的報告、profiler 輸出、
   測試結果、registry、原始碼）。
2. 每一項都記錄 `FOUND` 或 `ABSENT`，不是「假設存在」。
3. 如果某個章節需要的任何輸入是 ABSENT，那個章節就是
   **`NOT ASSESSED — NO DATA`**。不要估，不要從
   相鄰的產物推論，也不要留一個規定要填的格子讓下一個
   讀範本的人去填。
4. 如果**所有**需要的輸入都是 ABSENT，就停下來，把
   **`NOT ASSESSED — NO DATA`** 當作整份報告的 verdict 回報，並指出缺了什麼、
   哪個 skill 會產出它。

**`NOT ASSESSED` 的 verdict 是成功。** 沒有資料時，
它就是對「資料怎麼說？」最正確、最有用的答案。它要防的失敗模式
很明確：一份 verdict 列舉裡沒有「跑不了」狀態的報告，會產生
**假的乾淨通過**：一個沒有素材也沒有標準的專案，素材稽核卻回報 COMPLIANT；
或是一份效能分析，沒有任何 profiler 資料、也從沒設過預算，卻回報「對 16.67ms 預算有 >99% 的餘裕」。

**沒有證據，不代表沒有問題。** 因為沒有檔案可掃，所以掃不到任何東西，
這並沒有驗證任何事。要說清楚是這兩種情況的哪一種，
光看綠色結果，讀的人分不出來。

---

## Phase 1: 載入目標檔案

完整讀目標檔案。讀 CLAUDE.md 取得專案的程式碼規範。

---

## Phase 2: 辨識引擎專家

從 `project.yaml` 讀 `specialists` 區塊；如果不存在，就退回 `.claude/docs/technical-preferences.md` 的 `## Engine Specialists` 章節。記下：

- **Primary** 專家：從 `engine.name` 推出來的 `<engine>-specialist`（Godot→`godot-specialist`、Unity→`unity-specialist`、Unreal→`unreal-specialist`）；用於架構和廣泛的引擎議題
- **Language/Code Specialist**：`specialists.code`：審查專案主要語言的檔案時使用
- **Shader Specialist**：`specialists.shader`：審查 shader 檔案時使用
- **UI Specialist**：`specialists.ui`：審查 UI 程式碼時使用

**值是 `null` 代表未設定：把那個 key 當成不存在，並跳過它的
專家。絕對不要把它當成 agent 名稱去 spawn。** v1.0 migration 會對
舊檔案沒有點名的任何專家寫入 `null`，而且只要有*一個*成員被設定，它就會寫入整個區塊，
所以只設定了 code 專家的專案，會帶著 `shader: null` 和 `ui: null`。
設定讀取器對這些回傳的是四個字元的字串 `"null"`，它不是空的，
因此會被讀成已設定。在這裡，`null`、空的、不存在，都是同一個狀態。

如果沒有設定引擎（`project.yaml` 沒有 `engine.name`，而且 `technical-preferences.md` 內容是 `[TO BE CONFIGURED]` 或不存在），就跳過引擎專家的步驟。**要在這次執行的輸出中記錄 ``Engine validation: NOT ASSESSED — no engine configured (`engine.name` unset in `project.yaml`)``。** 沒說任何話就跳過的檢查，跟通過的檢查看起來一模一樣；
讀的人分不出引擎的建議根本沒被徵詢過。

---

## Phase 3: ADR 合規檢查

**參數：** `/code-review [file(s)]` 最後面可以選擇性地帶一個 story 檔案路徑（例如 `/code-review Assets/Scripts/Combat/Attack.cs production/epics/combat/story-001.md`）。如果有給 story 路徑，就讀它，擷取主導的 ADR 參照。

依優先順序，在這些地方搜尋 ADR 參照：
1. story 檔案（如果有當參數給）
2. 實作檔案最上面的標頭註解
3. 提到這些檔案的 commit 訊息（`git log --oneline -- [file]`）

找像 `ADR-NNNN` 或 `docs/architecture/adr-` 這樣的模式（大小寫皆可）。

如果找不到 ADR 參照，就註明："No ADR references found — ADR compliance check skipped. For full ADR compliance review, provide the story path: `/code-review [files] [story-path]`."

每個被參照的 ADR，**只載入這個檢查需要的章節，絕對不要做沒有範圍限制的完整讀取。** 內容多的 ADR 會超過 `Read` 的 25k token 上限，而被截斷的讀取唯一的補救是分頁讀剩下的，那是讀檔最貴的方式。用跟 `/dev-story` 和 `/create-stories` 一樣的做法：

1. **先對應標題**（便宜，只有行號）：`Grep pattern="^## " path="[adr-file]" output_mode="content" -n`
2. **只用有範圍限制的方式讀 `## Decision` 和 `## Consequences`**，用行號設定 `Read(offset, limit)` 的範圍，到下一個標題開始的地方結束。如果標題對應是空的（早於範本的非標準 ADR），就退回做一次完整的 `Read`；如果它在上限被截斷，就直接 grep 決策／後果的內容，不要分頁讀剩下的。

被參照的 ADR 如果檔案不存在或讀不了，ADR
Compliance 就是 `NOT ASSESSED — [ADR] could not be read`：要點名它。完全沒有
參照則是 `NO ADRS FOUND`，這是不同的結果。

從這兩個章節，分類任何偏差：

- **ARCHITECTURAL VIOLATION**（BLOCKING）：用了 ADR 明確否決的模式
- **ADR DRIFT**（WARNING）：明顯偏離選定的做法，但沒有用禁用的模式
- **MINOR DEVIATION**（INFO）：跟 ADR 的指引有小差異，不影響整體架構

---

## Phase 4: 規範合規

辨識系統類別（引擎、gameplay、AI、網路、UI、工具）並評估：

- [ ] 公開的方法和類別有文件註解
- [ ] 每個方法的循環複雜度低於 10
- [ ] 沒有方法超過 40 行（資料宣告不算）
- [ ] 依賴是注入的（遊戲狀態不用 static singleton）
- [ ] 設定值從資料檔載入
- [ ] 系統暴露介面（不依賴具體類別）

---

## Phase 5: 架構與 SOLID

**架構：**
- [ ] 依賴方向正確（engine <- gameplay，不是反過來）
- [ ] 模組之間沒有循環依賴
- [ ] 分層恰當（UI 不擁有遊戲狀態）
- [ ] 跨系統溝通用 event/signal
- [ ] 跟程式碼庫裡已建立的模式一致

**SOLID：**
- [ ] Single Responsibility：每個類別只有一個該被改動的理由
- [ ] Open/Closed：不用修改就能擴充
- [ ] Liskov Substitution：子型別可以替換基底型別
- [ ] Interface Segregation：沒有肥大的介面
- [ ] Dependency Inversion：依賴抽象，不依賴具體實作

---

## Phase 6: 遊戲專屬的疑慮

- [ ] 與幀率無關（有使用 delta time）
- [ ] 熱路徑（update 迴圈）裡沒有記憶體配置
- [ ] 妥善處理 null／空狀態
- [ ] 需要的地方有 thread safety
- [ ] 資源清理（沒有洩漏）

---

## Phase 7: 專家審查（平行）

用 `Agent` 同時 spawn 所有適用的專家，不要等一個做完才開始下一個。

> **每個專家的發現，在回報之前都要先驗證。不要把發現
> 原封不動轉出去。** 每個發現都要在報告裡記錄：
>
> - 它指的**檔案和行號**。
> - **證據**：引用的程式碼，或是觸發它的具體輸入／狀態。
> - **信心程度**：`VERIFIED`（你自己檢查過）或 `UNVERIFIED —
>   specialist claim`（你查不了）。
>
> 驗證不了的發現，要回報成未驗證，或直接丟掉，絕對不能因為
> 語氣很有把握就升級成缺陷。
>
> **為什麼這是強制的。** agent 在推導時很可靠，在診斷既有程式碼時
> 不可靠：對一個短函式的**錯誤**說法，可以流暢到讓人一眼掃過就放行，
> 而聲稱的 bug 在你把輸入逐一列舉之後可能就站不住腳。沒有這一步，
> parent 的審查就是一條洗白管道：猜測以專家發現的身分進來，
> 出去時卻變成審查過的缺陷。

### 引擎專家

如果有設定引擎，判斷每個檔案適用哪位專家，並平行 spawn：

- 主要語言檔案（`.gd`、`.cs`、`.cpp`）→ Language/Code Specialist
- Shader 檔案（`.gdshader`、`.hlsl`、shader graph）→ Shader Specialist
- UI 畫面／widget 程式碼 → UI Specialist
- 跨領域或不明確 → Primary Specialist

任何牽涉引擎架構的檔案（scene 結構、node 階層、生命週期 hook），也要 spawn **Primary Specialist**。

### QA 可測試性審查

對 Logic 和 Integration 的 story，也要用 `Agent` spawn `qa-tester`，跟引擎專家平行。傳入：
- 被審查的實作檔案
- story 的 `## QA Test Cases` 章節（qa-lead 預先寫好的測試規格）
- story 的 `## Acceptance Criteria`

請 qa-tester 評估：
- [ ] 所有測試 hook 和介面都有暴露出來（沒有藏在 private/internal 存取後面）？
- [ ] story 的 `## QA Test Cases` 章節裡的 QA 測試案例，能對應到可測試的程式碼路徑嗎？
- [ ] 照目前的實作，有沒有任何驗收標準是不可測試的（例如寫死的數值、沒有注入用的 seam）？
- [ ] 這個實作有沒有引入現有 QA 測試案例沒涵蓋的新邊界情況？
- [ ] 有沒有任何應該要有測試、卻沒有的可觀察副作用？

對 Visual/Feel 和 UI 的 story：qa-tester 要審查 `## QA Test Cases` 裡的手動驗證步驟，照目前寫的實作做得到嗎？例如「手動檢查的人需要到達的狀態，真的到得了嗎？」

產出輸出之前，先收齊所有專家的發現。

---

## Phase 8: 輸出審查結果

```
## Code Review: [File/System Name]

### Engine Specialist Findings: [N/A — no engine configured / CLEAN / ISSUES FOUND]
[Findings from engine specialist(s), or "No engine configured." if skipped]

### Testability: [N/A — no story path given / N/A — Visual/Feel or Config story / TESTABLE / GAPS / BLOCKING]
[qa-tester findings: test hooks, coverage gaps, untestable paths, new edge cases]
[If BLOCKING: implementation must expose [X] before tests in ## QA Test Cases can run]

### ADR Compliance: [NOT ASSESSED / NO ADRS FOUND / COMPLIANT / DRIFT / VIOLATION]
[List each ADR checked, result, and any deviations with severity]

### Standards Compliance: [X/6 passing]
[List failures with line references; a missing doc comment names the method or class]

### Architecture: [NOT ASSESSED / CLEAN / MINOR ISSUES / VIOLATIONS FOUND]
[List specific architectural concerns]

### SOLID: [NOT ASSESSED / COMPLIANT / ISSUES FOUND]
[List specific violations]

### Game-Specific Concerns
[List game development specific issues]

### Positive Observations
[What is done well -- always include this section]

### Required Changes
[Must-fix items before approval — ARCHITECTURAL VIOLATIONs always appear here]

### Suggestions
[Nice-to-have improvements]

### Verdict: [NOT ASSESSED / APPROVED / APPROVED WITH SUGGESTIONS / CHANGES REQUIRED]
```

選 verdict，先符合的先贏：
- **CHANGES REQUIRED**：Required Changes 底下有任何東西
- **NOT ASSESSED**：沒東西可審查（上面的沒資料路徑）、引擎
  專家審查沒跑（沒設定引擎，或有專家無法被 spawn），或任何報告章節寫的是 `NOT ASSESSED`（ADR
  Compliance 有被參照但讀不了的 ADR、Architecture、SOLID）；
  要點名是哪一個。NOT ASSESSED 的順位低於 CHANGES REQUIRED，因為已知的
  缺陷比被跳過的檢查更能立刻採取行動，同時又高於兩種核准：略過引擎檢查的
  審查，沒有核准這份程式碼。（`NO ADRS
  FOUND` 不是 NOT ASSESSED：沒有 ADR 可檢查，並不會擋住
  核准。）
- **APPROVED WITH SUGGESTIONS**：只有 Suggestions
- **APPROVED**：沒有必須修改的項目，也沒有建議

這個 skill 是唯讀的，不會寫任何檔案。

---

## Phase 9: 下一步

用 `AskUserQuestion`：
- Prompt: "Code review complete — verdict: [NOT ASSESSED / APPROVED / APPROVED WITH SUGGESTIONS / CHANGES REQUIRED]. How would you like to proceed?"（Phase 8 的 verdict，一字不差）
- 選項（依 verdict 調整）：
  - 如果是 APPROVED：
    - `[A] Run /story-done to mark the story complete`
    - `[B] Stop here`
  - 如果是 APPROVED WITH SUGGESTIONS：
    - `[A] Apply the suggestions, then run /story-done`
    - `[B] Run /story-done now — suggestions noted for later`
    - `[C] Stop here`
  - 如果是 CHANGES REQUIRED：
    - `[A] Fix the issues and re-run /code-review`
    - `[B] Run /story-done anyway with noted exceptions`
    - `[C] Stop here`
  - 如果是 NOT ASSESSED：
    - `[A] Fix what stopped the review (point me at the code, run /setup-engine, or fix the unreadable ADR reference), then re-run /code-review`
    - `[B] Stop here`

如果發現 ARCHITECTURAL VIOLATION：
- 如果違規牴觸**既有的 ADR**：修正實作，使其符合 `docs/architecture/[adr-file].md`。如果設計確實有合理的改變，就跑 `/architecture-decision` 正式*修訂*既有的 ADR，不要另建一個互相競爭的。
- 如果被違反的那個模式**沒有 ADR**：先跑 `/architecture-decision` 把正確的做法記錄下來，再去修程式碼。
