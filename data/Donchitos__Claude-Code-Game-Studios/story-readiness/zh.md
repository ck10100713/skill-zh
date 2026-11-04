---
name: story-readiness
description: "檢查一個 story 是否準備好可以實作：驗收條件清楚、沒有未解決的問題、ADR 和依賴有效。使用時機：使用者問某個 story、或 sprint 的 story 是否準備好開始或建置。"
argument-hint: "[story-file-path or 'all' or 'sprint'] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, AskUserQuestion, Agent, Bash(bash "*/.claude/skills/story-readiness/../../hooks/yaml-helper.sh" resolve_config *), Bash(bash .claude/scripts/story-facts.sh *), Bash(bash .claude/scripts/adr-status.sh *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,review_gate,automation,workflow,qa.level,gate_level,story_granularity,system_overrides`

上面已經解析完畢，直接用；`--review` 會覆寫 `review_mode`。沒有這個區塊的話，
預設值看 `.claude/docs/config-resolution.md`。

用提問工具來問。沒有提問工具的話，把選項編號列出來，然後結束你的回合
等待。被略過或關閉的問題不算回答：要用純文字再問一次。

# Story Readiness

檢查一個 story 檔案是否包含開發者寫程式之前需要的所有東西：
建置到一半不用再問設計問題、不用猜、沒有含糊的驗收條件。

**唯讀。** 它絕對不會寫入或編輯任何檔案。它只回報，並提議
在對話中起草修正。

**結論**，每個 story 一個。第一個符合的勝出，依這個順序：

1. **BLOCKED**：讀的人可以清除的發現。被引用的 ADR 不存在、
   是 `Proposed`、`Deprecated` 或 `Superseded`；依賴的 story 不存在或
   是 `Draft`；或是某條條件含有沒有負責人的 UNRESOLVED 設計問題。
2. **NEEDS WORK**：有阻擋性的檢查項目沒過。這個 story 現在就可以修。
3. **NOT ASSESSED**：這個 story 無法評估。檔案讀不到、
   被引用的 ADR 沒有可讀的 `## Status`，或是它點名的設計文件
   找不到。點名無法讀取的是什麼。它絕對不會是 READY：一個
   沒人能檢查的 story，並沒有被證明是準備好的。它的排序低於那兩種失敗，
   因為已知的阻擋項目比未知的更有用。
4. **READY**：每個項目都通過、是附有理由的 N/A，或是建議性的。建議性的
   缺口仍然要列出來。

詢問遵循 `.claude/docs/automation-modes.md`（collaborative 一律詢問，guided
在重大選擇時才問，autonomous 記錄後繼續；`automation_always_ask`
類別一律要詢問）。

## Phase 1: Scope

範圍是打在 skill 名稱後面的文字，去掉任何 `--review <mode>` 成對的參數之後
剩下的部分。剩下的是一個值；路徑可以含有空格。什麼都沒打時，
使用者的請求所點名的 story、epic 或 sprint 就是範圍。

- **一個 story 路徑**：那個 story。
- **`sprint`**：目前 sprint 列出的 story（Phase 2 會讀它們）。
- **`all`**：`production/epics/` 底下每個 `story-*.md`。
- **一個 epic**（一個 slug 或它的資料夾）：那個資料夾裡的 `story-*.md` 檔案。
- **空白**：問："What would you like to check?" 選項：A specific story file /
  All stories in the current sprint / All stories in production/epics/ / The
  stories of one epic。

**範圍內沒有 story：就停下來並回報 `NOT ASSESSED — no stories in scope`。** 點名
範圍和空的那個路徑，並導向 `/create-stories`（在 `standard`
和 `full` 時，先 `/create-epics`）。絕對不要在空的清單上印出 `Ready: 0 / Needs Work: 0` 摘要：
它讀起來像乾淨的結果。對 `sprint` 來說，"no sprint plan
found" 和 "the sprint plan lists no stories" 是不同的回報；要說是哪一個。

繼續之前先說 "Checking [N] story files."

## Phase 2: Facts, read once for the run

1. **Story。** 對範圍執行 story helper，使用上面解析出的
   `story_granularity`：
   ```
   bash .claude/scripts/story-facts.sh --lint --granularity <story_granularity> [--sprint | --all | <path> ...]
   ```
   每個 `STORY` 列給出 story 的狀態、類型、layer、估算、TR-ID、ADR、
   驗收條件數量、測試證據那一行和依賴。每個 `LINT` 列
   是 story 觸犯的一條規則。各列是觀察；結論由你下。結束碼 3
   代表有檔案找不到。有 `NOT_FOUND` 列時，每個點名的是一個 sprint 的 `file:`
   條目，或不是檔案的路徑：把每個回報成缺少的 story，然後檢查
   其餘的。沒有 `NOT_FOUND` 列而有 `--sprint` 時，代表沒有
   `production/sprint-status.yaml`：回報 "no sprint plan found"。每個 story 檔案也要讀：下面的可測試性、範圍和
   資產項目需要它的文字。
2. **ADR。** 一次呼叫就給出每個 ADR 的狀態和 layer：
   `bash .claude/scripts/adr-status.sh`。`no_status` 或 `UNFILLED` 的狀態
   是格式有問題的 ADR：絕對不要把不存在的狀態當成失敗的狀態（導向：
   `/architecture-decision retrofit [file]`）。story 引用、但沒有對應列的 ADR 就是缺少。
3. **Control manifest。** 只讀 `docs/architecture/control-manifest.md` 裡它的
   `Manifest Version` 那一行。檔案不存在：註記一次。
4. **TR registry。** 在
   `docs/architecture/tr-registry.yaml` 裡查每個 story 的 TR-ID 和它們的 `status`。檔案不存在：註記一次；
   每個 story 的 TR-ID 項目都算通過。
5. **Sprint 優先順序**（`sprint` 範圍）：哪些 story 是 Must Have 和 Should
   Have，取自 `production/sprints/` 裡最新的計畫。

**每個 story 的等級。** `workflow` 是對每個 story 各自解析的：使用該 story 所屬系統的
`system_overrides` 那一列（它 `GDD:` 路徑的 GDD 檔名主幹；只有在沒有 GDD 路徑時，才用
`TR-[system]-NNN` ID 的 `[system]`），否則用專案的值。
同一次執行裡的 story 可以位於不同的等級。

## Phase 3: The checklist

每個 story 的每個項目都要檢查。等級決定哪些群組會阻擋：

| Group | `full` | `standard` | `minimal` |
|---|---|---|---|
| Design Completeness | blocks | blocks | blocks; `design/game-brief.md` stands in for the GDD |
| Architecture Completeness | blocks | the ADR status item blocks; the rest advisory unless it concerns a critical ADR | N/A, except the ADR status item |
| Scope Clarity | blocks | blocks | blocks, except Estimate: advisory (no sprint plan to size for) |
| Open Questions | blocks | blocks | blocks |
| Asset References | blocks | blocks | blocks |
| Definition of Done | blocks | blocks | blocks; the test evidence item follows `qa.level` |

沒過的**建議性**項目會列在 Gaps 底下，附上它的 Fix，而且絕對不會
單獨讓結論低於 READY。

### Design Completeness

- [ ] **Requirement traced**：story 點名了它的 `design/gdd/` 檔案，並引用或
  連結其中一條具體的規則或條件，不只是檔名。在
  `minimal` 時：`design/game-brief.md` 和這個 story 實作的 MVP 功能。
  被點名的設計文件不存在：NOT ASSESSED。
- [ ] **Self-contained**：驗收條件不用打開 GDD，就說明了完成代表什麼。
- [ ] **Testable**：每條條件都是具體、可觀察的狀況。不是：
  "Implement the jump mechanic." 而是："Jump reaches 5 units within 0.3 seconds
  when held." 單元測試能設定出來的條件（任何輸入值）就是可測試的，
  即使實際出貨的資料永遠不會走到那個情況。
- [ ] **No judgement calls**："feels responsive" 或 "looks good" 對 Logic、
  Integration、UI 和 Config/Data 來說不過。對 Visual/Feel 來說，這類條件是預期中的：
  當條件點名了證據檔案，例如
  `production/qa/evidence/[slug]-evidence.md` 就通過，沒有點名任何檔案就是 NEEDS WORK。

### Architecture Completeness

- [ ] **ADR status**，在每個等級都要：story 引用的每個 ADR，依 Phase 2 的
  表。
  - `Accepted`：通過。
  - `Proposed`：BLOCKED。Fix：`BLOCKED: ADR-NNNN is Proposed — accept it with
    /architecture-decision accept ADR-NNNN once decided`。
  - `Deprecated` 或 `Superseded`：BLOCKED。Fix：`BLOCKED: ADR-NNNN is [status] —
    point the story at [successor] (edit its ADR field;
    /create-stories never rewrites an existing story)`。
  - 沒有這個 ADR 檔案：BLOCKED。
  - 沒有可讀的狀態：這個項目是 NOT ASSESSED；點名那個檔案。
  在 `standard` 時，**關鍵的** ADR（它的 `layer` 是 Foundation 或缺少）
  如果不存在或是 Proposed 就會阻擋；其他 ADR 則下面的項目是建議性的。
- [ ] **ADR cited or N/A stated**：一個 ADR，或是附有理由的明確 N/A
  （`ADR: N/A — [reason]`，或 `N/A (minimal — no ADRs)`）。空白就不過。
- [ ] **TR-ID valid**：每個 `TR-[system]-NNN` 都在 registry 裡，而且 `status:
  active`。`deprecated` 或 `superseded-by`（有沒有加引號都一樣）：NEEDS WORK，Fix：把
  story 指向目前的需求。不在 registry 裡：NEEDS WORK（story
  可能比它還早，或是 registry 需要 `/architecture-review`）。沒有 TR-ID，或沒有 registry 時通過。
- [ ] **Manifest Version current**：story 的 `Manifest Version` 對照
  manifest 的。比較舊：這是缺口，因為之後新增的規則可能適用。即使
  新規則看起來不相關，它仍然是缺口：說明改了什麼，並把判斷留給
  使用者。在 `full` 時，不管新規則涵蓋什麼，都是 NEEDS WORK；在
  `standard` 時是建議性的。Fix，三個步驟都要有："Review the manifest rules added since
  [story's date]; update the story's rules if any apply; then set its Manifest
  Version to [current date]." 沒有 `Manifest Version` 欄位，或沒有
  manifest 時通過。
- [ ] **Engine notes**：story 碰到的、超過訓練截止日的引擎 API 有備註或驗證步驟，
  或是 story 寫明 "N/A — no engine API involved"。
- [ ] **Manifest rules noted**：列出該 layer 的規則，或寫 "N/A — manifest
  not yet created"。沒有 manifest 時通過。

### Scope Clarity

- [ ] **Estimate**：小時、點數或 t-shirt 尺寸。`unfilled Estimate`（仍然是
  範本的方括號）不過。在 `minimal` 時是建議性的。
- [ ] **Out of scope stated**：有 Out of Scope 段落，或是讓
  邊界沒有歧義的文字。
- [ ] **Dependencies listed**：這個 story 需要的每個 story，或寫明 "None"。

### Open Questions

- [ ] **No open markers**：沒有 `marker` 列（TBD、TODO 或 UNRESOLVED，以全大寫的完整單字出現）。
  `?` 不是標記：像 `crit ? 2 : 1` 這樣的公式通過。
  寫成開放性問題的條件仍然不通過 Testable。
- [ ] **Dependencies exist and are not Draft**：依賴的 story 不存在或是
  `Draft`，會讓這個 story 是 BLOCKED。`Story NNN` 指的是同一個
  epic 資料夾裡那個編號；路徑則確切指定一個。

### Asset References

- [ ] **Assets the story uses exist**：`assets/` 底下的路徑，或是副檔名是 `.png`、
  `.jpg`、`.svg`、`.wav`、`.ogg`、`.mp3`、`.glb`、`.gltf`、`.tres`、`.tscn` 或
  `.res`，而且是 story 讀取或建立在其上的。story 說它自己會建立的檔案
  （新場景、新資料檔）不檢查。缺少：NEEDS WORK；點名
  路徑。回報 "Referenced assets verified: [N] found"，或 "No asset references"。
  只檢查是否存在。

### Definition of Done

- [ ] **Enough acceptance criteria**：沒有 `ac_below_min` 列。最少數量依
  `story_granularity`，因為 `/create-stories` 是依它來寫的：

  | `story_granularity` | Logic, Integration | Visual/Feel, UI | Config/Data |
  |---|---|---|---|
  | `coarse` | 3 | 2 | 1 |
  | `balanced` | 2 | 2 | 1 |
  | `fine` | 1 | 1 | 1 |

- [ ] **Performance noted**：碰到遊戲玩法循環、渲染或
  物理的 story，要說明預算，或寫 "no performance impact expected — [reason]"。
- [ ] **Type declared**：沒有 `type_missing` 或 `type_unknown` 列。Fix：在標頭加上
  `Type: [Logic|Integration|Visual/Feel|UI|Config/Data]`。
- [ ] **Test evidence clear**：有一個 `## Test Evidence` 段落，說明證據放在哪裡：
  Logic 和 Integration 是測試檔案；UI 是 `production/qa/evidence/` 底下
  每個畫面的保留截圖；Visual/Feel 是那個加上
  `production/qa/evidence/[story-slug]-evidence.md`。
  - 在 `qa.level: minimal` 時，Logic、Integration 和 Config/Data 通過：測試
    被免除。不要列缺口，也不要加備註，說缺少測試檔案、`tests/`
    資料夾或測試執行器。UI 和
    Visual/Feel 仍然要檢查：它們的截圖在每個等級都是必要的。
  - 否則由上面的 `gate_level` 那一行決定該 story 類型的等級。
    `blocking`：缺少段落就是 NEEDS WORK。`advisory`：只是列出的缺口。
    Fix：加上 `## Test Evidence`，寫明該 story 類型的證據位置。

## Phase 4: Verdict

對每個 story 套用最上面的順序。BLOCKED 的 story 可能同時有 NEEDS WORK
的項目：兩者都要列。

## Phase 5: QA lead review

讀上面的 `review_gate` 那一行。`skill-gates=skip`（solo 或 lean）：跳過，
並且回覆說 "QL-STORY-READY skipped — [Solo | Lean] mode"。`skill-gates=run`：
讀 `references/qa-lead-gate.md` 和 `.claude/docs/director-gates.md`，並在回報之前
執行它。跳過時，不要載入它。

## Phase 6: Report and close

單一 story：

```
## Story Readiness: [story title]
File: [path]
Verdict: [READY / NEEDS WORK / BLOCKED / NOT ASSESSED]

### Passing Checks (N/[total])
Design Completeness: [passing items]
Architecture Completeness: [passing items, or "N/A at minimal (ADR status checked)"]
Scope Clarity: [passing items]
Open Questions: [passing items]
Asset References: [passing items, or "no asset references"]
Definition of Done: [passing items]

### Gaps
- [Checklist item]: [what is missing or wrong]
  Fix: [the text that resolves it]

### Blockers (if BLOCKED)
- [What blocks]: [the story, ADR or question that must clear first]
```

每次都要用這些確切的名稱點名全部六個群組。沒有任何項目通過的群組
寫 "none — see Gaps"，讓讀的人看到它有被檢查過。

Gaps 只列沒過的檢查項目：絕對不列通過或 N/A 的項目，也絕對不列
檢查清單之外的觀察（sprint 狀態、另一份文件）。

多個 story：先給摘要，然後對每個不是 READY 的 story 各給一個
單一 story 的區塊。

```
## Story Readiness Summary — [scope] — [date]
Ready: [N] · Needs Work: [N] · Blocked: [N] · Not Assessed: [N]

Ready: [title] ([path]), ...
Needs Work: [title]: [main gap]
Blocked: [title]: blocked by [story, ADR or question]
Not Assessed: [title]: [what could not be read]
```

`sprint` 範圍：當有 Must Have 的 story 不是 READY 時，把這段放在最前面：
`WARNING: [N] Must Have stories are not ready to implement: [each with its main
gap]. Fix them before the sprint starts, or replan with /sprint-plan update.`

**然後，對單一 story：** 找其他可以開始的 story。在
`production/sprints/` 最新的計畫裡，找最多 3 個是 Ready 或 Not Started 的，不是這一個、
不是在等未完成的依賴、而且是 Must Have 或 Should Have 的。每個
列出一行說明和它的估算。沒有的時候，說明是哪種情況：
`Next ready stories: no sprint file found` 或 `Next ready stories: none ready in
[sprint]`。

**提供協助。** 問："Would you like me to draft the missing parts for any of
these stories?" 選項：Yes, draft them / No, that's all。選 yes 時，只起草
缺少的部分，在對話中進行。由使用者或 `/create-stories` 寫入它們。

導向：
- Story 檔案不存在：執行 `/create-stories [epic-slug]`（在 `standard` 和
  `full` 時，先 `/create-epics`）。
- 沒有設計參考，而且變更很小（約一週以內）：執行
  `/quick-design [description]`，並在 story 中引用那份規格。
- 範圍長大超出了它的估算：拆分 story，或是跟 producer 提出來。

**以這個結束回覆：**

```
Review: [QL-STORY-READY skipped — Solo mode | skipped — Lean mode | its verdict]
Next ready stories: [up to 3 | no sprint file found | none ready in [sprint]]   (one-story scope)
Next step: [/dev-story [path] when READY | fix the gaps above, then /story-readiness [path]]
Files changed: none
```
