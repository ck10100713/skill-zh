---
name: team-ui
description: "統籌 UI 團隊走完 UX pipeline：撰寫規格、視覺設計、實作、審查、polish。會用到 /ux-design、/ux-review 和 studio 模板。"
argument-hint: "[UI feature description] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, TaskCreate, TaskGet, TaskList, TaskUpdate, Bash(bash "*/.claude/skills/team-ui/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---
# Team UI

如果沒有帶參數，就輸出使用說明並結束，不要 spawn 任何 agent，也不要讀任何設計文件：
> 用法：`/team-ui [UI feature description] [--review full|lean|solo]` — 描述要做的畫面或 UI 功能（例如 `inventory screen`、`main menu`、`combat HUD`）。這裡不要用 `AskUserQuestion`，直接輸出說明。

呼叫這個 skill 時，用結構化的 pipeline 來統籌 UI 團隊。

**決策點：** 每個 phase 轉換時，用 `AskUserQuestion` 把 subagent 的提案做成可選項目給使用者選。先在對話中寫出 agent 的完整分析，再用簡短的標籤收下決定。
在 `collaborative` 模式下，使用者核准後才能進下一個 phase。
在 `guided` 模式下，pipeline 會自動往下走，除非某個 phase BLOCKED；
在 `autonomous` 模式下會從頭跑到尾，每個 phase 的結果用 `log_decision` 記錄下來。
屬於 `automation_always_ask` 類別的決策（`is_always_ask_category` helper）不管什麼模式一律要問。參見 `.claude/docs/automation-modes.md`。

## Phase 0: Resolve Config

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,team.size`

上面已經解析好了，直接用；`--review` 會覆蓋 `review_mode`。沒有這個區塊的話，就用 `.claude/docs/config-resolution.md` 裡的預設值。

`review_mode` 決定 director gate 的深度，而這條 pipeline 沒有 director gate：
下面任何 phase 在任何 `review_mode` 下，都不會 spawn CD-、TD-、PR- 或 AD-PHASE-GATE。它的 phase gate 就是 pipeline 自己的決策點（定義在下面的 `team.size` 底下），在這些點上工作的 agent 是團隊成員，不是 director gate。

`automation` 決定上面「決策點」那段的行為。各模式如何改變 pipeline 的行為，見上面的決策點說明和 `.claude/docs/automation-modes.md`。

**`team.size`**：哪些 agent 啟用（跟 review_mode 的 gate 深度和 workflow docs 互相獨立）。
- **`individual`**（預設）：`ui-programmer` + `ux-designer`。其他 agent 透過這兩個諮詢，不會另外 spawn。
- **`small`**：加上 `accessibility-specialist` + `art-director`。
- **`studio`**：再加上引擎 UI specialist + 一輪對抗式審查：Phase 4 的審查者會被告知「your job is not to confirm this matches the spec — find where it fails it」，報告也會講明這一輪有跑。
在 `individual` 下需要用到的非核心 agent，會改由最接近的核心 agent 處理，並附一則說明。**「Phase gate」指的是這條 pipeline 自己列出、以 `AskUserQuestion` 決策點收尾的任何 phase**：可能是上面「決策點」底下的某個轉換，也可能是下面 pipeline 裡寫明的 **Gate** 步驟，**不管 `automation` 是哪個模式都一樣。** `guided` 和 `autonomous` 改變的是 gate 怎麼通過（自動往下走，或用 `log_decision` 記錄），不是它算不算 gate，所以下面的有界例外條件 (3) 在每個模式下的 gate 都成立。被限制成「只在 phase gate 出場」的 agent，只會在這些時點 spawn，其他時候不會。這個「依啟用名單縮小範圍」的規則適用於下面整條 pipeline：任何 phase 只要點名了啟用名單以外的 agent，就改由最接近的核心 agent 處理，不 spawn 它。

**在 Step 1 之前先公布啟用名單，絕對不准讓縮減悄悄發生。**
spawn 任何東西之前，先用一行講清楚這次實際會 spawn 哪些 agent，以及下面 pipeline 有點名、但在目前 `team.size` 下**不會** spawn 的有哪些。例如：

> `Active set (team.size: <resolved>): <the agents listed for that size above>.`
> `Not spawned this run: <every other agent this pipeline names> — consulted`
> `through <nearest active core agent>. Raise team.size (or modes.rigor) to widen.`

內容要直接從上面的 `team.size` 清單和這個檔案自己的 pipeline 所點名的 agent 填，不要照抄範例。每個 orchestrator 這兩組名單都不一樣。

下面這條 pipeline 看起來像多 agent 的 fan-out，但在預設值下其實只有一兩個 agent：`team-release` 點名了十個、只跑一個，`team-narrative` 在五個 phase 裡點名了六個、只跑 `writer` 一個。**這樣縮減是對的**：`team.size` 是以嚴謹度為前提的，預設收窄就是用來省 token 的。
如果不明講，讀的人就分不出「正確縮減過的 run」和「壞掉的 pipeline」，而上面那條「由最接近的核心 agent 處理並附說明」的規則是在路由當下才觸發，從來不會交代整個 run 的樣子。

這跟這個檔案其他地方的「略過的檢查要回報」是同一條規則：**一個有被執行、卻從沒被講出來的限制，對讀輸出的人來說，跟從來沒執行過的限制看起來一模一樣。**

## Team Composition
- **ux-designer** — 使用者流程、線框圖、無障礙、輸入處理
- **ui-programmer** — UI 框架、畫面、widget、資料綁定、實作
- **art-director** — 視覺風格、版面 polish、跟 art bible 保持一致
- **engine UI specialist** — 對照引擎專屬的最佳實務，驗證 UI 實作模式（取自 `project.yaml` 的 `specialists.ui`；如果沒有，就用 `.claude/docs/technical-preferences.md` 裡 `## Engine Specialists` 的 UI Specialist 那一行）
- **accessibility-specialist** — 在 Phase 4 稽核無障礙合規

> **`specialists.ui: null` 代表未設定（UNSET）。** 把它當成不存在，跳過引擎 UI specialist；絕對不要把 `null` 當成 agent 名稱去 spawn。v1.0 的 migration 只要有任何一個成員被設定，就會把整個 `specialists` 區塊寫出來，所以這裡出現 `null` 很正常，而且設定讀取器會把它以非空字串 `"null"` 回傳。

**這條 pipeline 使用的模板：**
- `ux-spec.md` — 標準的畫面／流程 UX 規格
- `hud-design.md` — HUD 專用的 UX 規格
- `interaction-pattern-library.md` — 可重複使用的互動模式
- `accessibility-requirements.md` — 已承諾的無障礙層級與需求

## How to Delegate

用 `Agent` 工具把每個團隊成員 spawn 成 subagent：
- `subagent_type: ux-designer` — 使用者流程、線框圖、無障礙、輸入處理
- `subagent_type: ui-programmer` — UI 框架、畫面、widget、資料綁定
- `subagent_type: art-director` — 視覺風格、版面 polish、art bible 一致性
- `subagent_type: [UI engine specialist]` — 引擎專屬的 UI 模式驗證（例如 unity-ui-specialist、ue-umg-specialist、godot-specialist）
- `subagent_type: accessibility-specialist` — 無障礙合規稽核

**給每個 agent 的 brief 要精簡，不要整包 context 倒過去。** 共用的輸入只讀**一次**，再把整理過的 brief 直接寫在 prompt 裡：只放每個 agent 真正需要的那幾行，你已經讀過的文件絕對不要只丟檔案路徑（agent 拿到路徑會把整份檔案重讀一遍）。只有你還沒讀、而且只有那個 agent 需要的文件，才給路徑。

**每個 agent 的 prompt 結尾都要加上回傳約定：**「Write your full output to `[path]` — that named path is your write authorisation under the bounded exception below, so write it without a separate approval prompt. Return **only** (1) the path written, (2) a ≤5-bullet summary of decisions, (3) any BLOCKED/CONCERNS items, one line each. Do not restate the documents you read.」沒有這個約定的話，agent 會把它讀過的東西全部倒回這個 session。**實作檔案是例外：** 寫程式或資產的 agent 要先回傳它打算建立或修改的檔案，而它的回傳約定要等你把整組檔案問過一次、使用者也答應之後才能指名這些檔案（File Write Protocol）。授權這些寫入的是那個答覆，不是有界例外。

**`[path]` 要換成真實路徑。** 工作中的產出放在
`production/ui/[feature-name]/` 底下，slug 跟 Phase 1b 的 `design/ux/[feature-name].md` 用的一樣。每個 agent 一個檔案，這樣平行的 Phase 4 審查就不會共用同一個檔：

| Phase / agent | Writes to |
|---|---|
| 2 art-director | `production/ui/[feature-name]/visual-design.md` |
| 3 engine UI specialist | `production/ui/[feature-name]/engine-notes.md` |
| 3 ui-programmer | the code root — the files the one implementation ask lists (File Write Protocol), outside the bounded exception |
| 4 ux-designer, art-director, accessibility-specialist | `production/ui/[feature-name]/review-[agent].md`, one each |

UX 規格本身（Phase 1b）和任何 pattern library 的更新都在 `design/` 底下，在有界例外之外：`/ux-design` 或 agent 寫入前要先問。

> **為什麼這不違反 Collaboration Protocol。** `CLAUDE.md` 要求 agent 在 Write/Edit 之前先問「May I write this to [filepath]?」。這裡 spawn 出來的 subagent **不問**就寫，這是刻意設計的有界例外，不是疏忽，跟 `consistency-check` 附加寫入 `active.md` 是同一個決定。這個例外只在三個條件**同時**成立時才有效：(1) 路徑是**你**在 prompt 裡指定的，所以使用者核准這個 phase 的時候，就等於核准了目的地；(2) 它是 `production/`、`docs/` 或 `tests/` 底下的新產物，絕對不是改既有的原始碼或設定；(3) 產生它的那個 phase，本身在 pipeline 往下走之前有 `AskUserQuestion` 把關。這三條以外，agent 一定要先問。**不要靠「每個 subagent 都問一次」來「修」這件事**：每個 agent 每個 phase 都跳一次提示，會讓 orchestrator 根本沒辦法用，這就是這個例外存在的原因。

只要 pipeline 允許，就把互相獨立的 agent 平行啟動（例如 Phase 4 的審查 agent 可以同時跑）。

## Pipeline

### Phase 1a: Context Gathering

設計任何東西之前，先讀並整理。每份 GDD 都要分段讀：用 Grep 工具（pattern `^#`，content mode）找出需要的標題，再用 offset 和 limit 讀那些範圍。
- `design/gdd/game-concept.md` — 平台目標與預期受眾（或
  `design/game-brief.md`，在 `rigor: minimal` 時取代它的一頁式 brief，它的「Who it's for」那一行給出受眾；它沒有寫平台）
- `design/player-journey.md` — 玩家到達這個畫面時的狀態與情境
- 所有跟這個功能有關的 GDD UI Requirements 章節
- `design/ux/interaction-patterns.md` — 要重複使用（不要重新發明）的既有模式
- `design/accessibility-requirements.md` — 已承諾的無障礙層級（Basic、Standard、Comprehensive 或 Exemplary）

**設計任何東西之前，先回報上面每份文件的狀態。** Phase 1a 讀五份輸入，任何一份都可能不存在。把每一份都列成 present 或 ABSENT。

**`design/accessibility-requirements.md` 是絕對不能悄悄放過的那一份。** 它載明已承諾的無障礙層級，**Phase 3 照它實作**，**Phase 4 用它把關**（「verify compliance against the committed accessibility tier … flag any violations as blockers」）。如果這個檔案不存在，就沒有層級，那個 gate 就沒有判準，會在什麼都沒檢查的情況下通過：一個由缺席的標準構成的 gate，跟永遠不可能失敗的斷言是同一種形狀。它不存在的時候：
- 在這裡講明，並帶下去：**Phase 4 必須回報
  `Accessibility: NOT ASSESSED — no committed tier (design/accessibility-requirements.md absent)`，而且絕對不能把無障礙 gate 回報成通過。**
- ux-designer 要把它設計時依據的層級，當成明確的假設講出來，這樣之後的讀者看得出那是假設的，不是承諾過的。
- 建議用 `/ux-design accessibility` 來建立層級。

缺少概念文件（`design/gdd/game-concept.md` 和 `design/game-brief.md` 都沒有）、`design/player-journey.md` 或 `design/ux/hud.md`，並不會擋住流程，但要在傳給 ux-designer 的 brief 裡，逐一點名缺了哪些，讓他們設計時知道自己缺了哪些 context，而不是自己去推測。

**如果 `design/ux/interaction-patterns.md` 不存在**，要立刻把缺口揭露出來：
> "interaction-patterns.md does not exist — no existing patterns to reuse."

然後用 `AskUserQuestion` 提供選項：
- (a) 先跑 `/ux-design patterns` 建立 pattern library，再繼續
- (b) 不用 pattern library 繼續：ui-programmer 會把建立的所有模式都當成新的，並在完成時把每個模式加進一份新的 `design/ux/interaction-patterns.md`

絕對不准光憑功能名稱或 GDD 就發明或假設模式。如果使用者選 (b)，要在 Phase 3 明確指示 ui-programmer 把所有模式都當成新的，並在實作完成時記錄到 `design/ux/interaction-patterns.md`。在最終摘要報告裡註記 pattern library 的狀態（created / absent / updated）。

把 context 整理成給 ux-designer 的 brief：玩家正在做什麼、需要什麼、有哪些限制條件、哪些既有模式有關。

### Phase 1b: UX Spec Authoring

呼叫 `/ux-design [feature name]` skill，或直接委派給 ux-designer，依照 `ux-spec.md` 模板產出 `design/ux/[feature-name].md`。

如果是設計 HUD，改用 `hud-design.md` 模板，不用 `ux-spec.md`。

> **特殊情況的備註：**
> - 設計 HUD 時，用 `argument: hud` 呼叫 `/ux-design`（例如 `/ux-design hud`）。
> - 互動模式的 pattern library，在專案開始時跑一次 `/ux-design patterns`，之後在後面的 phase 每次引入新模式時就更新它。

輸出：所有必要規格章節都填好的 `design/ux/[feature-name].md`。

### Phase 1c: UX Review

規格完成之後，呼叫 `/ux-review design/ux/[feature-name].md`。

**Gate**：在 verdict 是 APPROVED 之前，不要進 Phase 2。如果 verdict 是 NEEDS REVISION，ux-designer 必須在同一份規格裡處理被標出的問題，這份規格要保留並修改，絕對不能丟掉重來，然後重跑審查。使用者可以明確接受 NEEDS REVISION 的風險並繼續，但這必須是有意識的決定：在問要不要繼續之前，先透過 `AskUserQuestion` 呈現具體的疑慮。

**NOT ASSESSED** 的 verdict 一樣會擋住，使用者也可以用同樣的方式放行。它的修法是補輸入，不是修改：呈現 `/ux-review` 無法評估的維度，以及每個維度缺的輸入（例如尚未承諾層級的話，用 `/ux-design accessibility`）。沒補那個輸入就重跑審查，只會得到同樣的 verdict，所以要提議先把輸入做出來。

當使用者越過 NEEDS REVISION 或 NOT ASSESSED 繼續往下走時，最終報告要記錄這次放行：verdict、還沒解決的疑慮或未評估的維度，以及使用者選擇繼續這件事。

### Phase 2: Visual Design

委派給 **art-director**：
- 檢視完整的 UX 規格（流程、線框圖、互動模式、無障礙筆記），不只是線框圖的圖片
- 套用 art bible 的視覺處理：顏色、字型、間距、動畫風格
- 檢查視覺設計沒有破壞無障礙合規：驗證色彩對比度，並確認顏色絕對不是狀態的唯一指標（形狀、文字或圖示必須加強它）
- 指定從美術管線需要的所有資產需求：指定尺寸的圖示、背景貼圖、字型、裝飾元素，附上精確的尺寸與格式要求
- 確保跟既有已實作的 UI 畫面一致
- 輸出：附風格筆記與資產清單的視覺設計規格

### Phase 3: Implementation

實作開始之前，先 spawn **engine UI specialist**（取自 `project.yaml` 的 `specialists.ui`；如果沒有，就用 `.claude/docs/technical-preferences.md` 裡 `## Engine Specialists` 的 UI Specialist 那一行），審視 UX 規格和視覺設計規格，給出引擎專屬的實作指引：
- 這個畫面該用哪個引擎 UI 框架？（例如 Unity 的 UI Toolkit vs UGUI、Godot 的 Control node vs CanvasLayer、Unreal 的 UMG vs CommonUI）
- 提議的版面或互動模式有沒有什麼引擎專屬的陷阱？
- 建議給這個引擎用的 widget／node 結構？
- 輸出：在 ui-programmer 開始之前交給他們的引擎 UI 實作筆記

如果沒有設定引擎，就跳過這個步驟。**在這次 run 的輸出裡記下 ``Engine validation: NOT ASSESSED — no engine configured (`engine.name` unset in `project.yaml`)``。** 被略過卻不吭聲的檢查，跟通過的檢查看起來一模一樣；讀的人沒辦法知道根本沒有徵詢過引擎方面的意見。

委派給 **ui-programmer**：
- 依照 UX 規格和視覺設計規格實作 UI
- **使用 `design/ux/interaction-patterns.md` 裡的模式**：已經規定好的模式不要重新發明。如果某個模式差不多能用、但需要修改，就註記偏離之處，並標出來給 ux-designer 審查。
- **UI 絕對不擁有、也不修改遊戲狀態**：只負責顯示；所有玩家動作都發出事件
- 所有文字都透過在地化系統：不准寫死面向玩家的字串
- 兩種輸入方式都要支援（鍵盤／滑鼠「以及」遊戲手把）
- 依照 `design/accessibility-requirements.md` 裡已承諾的層級，實作無障礙功能
- 把資料綁定接到遊戲狀態
- **如果實作期間建立了任何新的互動模式**（也就是 pattern library 裡還沒有的東西），在標記實作完成之前，先把它加進 `design/ux/interaction-patterns.md`
- 輸出：實作好的 UI 功能

### Phase 4: Review (parallel)

平行委派：
- **ux-designer**：驗證實作跟線框圖與互動規格一致。測試純鍵盤和純遊戲手把的導覽。檢查無障礙功能運作正確。
- **art-director**：驗證視覺跟 art bible 一致。在支援的最小與最大解析度下檢查。
- **accessibility-specialist**：對照 `design/accessibility-requirements.md` 裡記載的已承諾無障礙層級，驗證合規。任何違規都標成 blocker。**如果那個檔案不存在，就沒有已承諾的層級，這個 gate 沒有判準：回報 `Accessibility: NOT ASSESSED — no committed tier (design/accessibility-requirements.md absent)`，而且絕對不能把 gate 回報成通過**。把 Phase 1a 記錄為假設的層級帶下去，並明講那是假設的。

三條審查線都回報完畢，才能進 Phase 5。

### Phase 5: Polish

- 處理所有審查回饋
- 驗證動畫可以跳過，而且尊重玩家的減少動態偏好設定
- 確認 UI 音效是透過音訊事件系統觸發（不能直接呼叫音訊）
- 在所有支援的解析度與長寬比下測試
- **驗證 `design/ux/interaction-patterns.md` 是最新的**：如果這個功能實作期間引入了任何新模式，確認它們已經加進 library
- **確認所有 HUD 元素都遵守** `design/ux/hud.md` 裡定義的視覺預算（元素數量、畫面區域配置、最大不透明度）

## Quick Reference — When to Use Which Skill

- `/ux-design` — 從零開始為畫面、流程或 HUD 撰寫新的 UX 規格
- `/ux-review` — 實作前驗證已完成的 UX 規格
- `/team-ui [feature]` — 從概念到 polish 的完整 pipeline（內部會呼叫 `/ux-design` 和 `/ux-review`）
- `/quick-design` — 不需要完整新 UX 規格的小型 UI 修改

## Error Recovery Protocol

**先驗證產物。** 如果回傳約定指定了路徑，在把這個 phase 當成做完之前，先確認該路徑真的存在：**指名的產物不在磁碟上，就是失敗的 phase，不管回覆讀起來多流暢。** agent 可能耗掉整個 phase，回你一段看似合理的開場白，卻什麼都沒寫；這既不是 BLOCKED、也不是錯誤、也不是「無法完成」，所以下面的觸發條件永遠不會被觸發。要叫它繼續，並指明沒達成的約定；context 通常還在。

如果任何 spawn 出去的 agent 回傳 BLOCKED、出錯或無法完成：**立刻揭露，不要越過它所阻擋的依賴項繼續往下走，而且一定要產出部分報告。** 被略過的 agent 那一節要留成一個有名字的缺口，絕對不准用你自己的內容填進去。完整流程：`.claude/docs/error-recovery-protocol.md`。

常見的阻擋原因：
- 輸入檔案缺失（找不到 story、GDD 不存在）→ 導向建立它的 skill
- ADR 狀態是 Proposed → 不要實作；決定之後，用 `/architecture-decision accept ADR-NNNN` 接受它
- 範圍太大 → 用 `/create-stories` 拆成兩個 story
- ADR 和 story 的指示互相衝突 → 把衝突揭露出來，不要猜

## File Write Protocol

所有檔案寫入（UX 規格、互動模式 library 的更新、實作檔案）都委派給 sub-agent 和 sub-skill。兩者遵守**不同**的規則：

- **透過 `Agent` spawn 的 sub-agent**（例如 `ui-programmer`）適用上面「為什麼這不違反 Collaboration Protocol」所記載的**有界例外**：路徑是你指定的、產物是 `production/`、`docs/` 或 `tests/` 底下的新檔案、而且這個 phase 有 `AskUserQuestion` 把關。在這些範圍內，sub-agent **不會**每次寫入都問；範圍之外就一定要問。
  **實作檔案**（ui-programmer 在 code root 底下的程式碼）在這些範圍之外：ui-programmer 先回傳它打算建立或修改的檔案，你對整組檔案問一次，答應之後它才寫。
- **Sub-skill**（`/ux-design`）不是 sub-agent，例外不適用於它們。它們遵守一般的 Collaboration Protocol，寫入前要先問。

這個 orchestrator 不會直接寫檔案。

## Output

一份摘要報告，涵蓋：UX 規格狀態、UX 審查 verdict、視覺設計狀態、實作狀態、無障礙合規、輸入方式支援、互動模式 library 的更新狀態，以及任何未解決的問題。

Verdict: **COMPLETE** — UI feature delivered through full pipeline (UX spec → visual → implementation → review → polish).

如果無障礙 gate（沒有已承諾的層級）或引擎驗證（沒有設定引擎）是 NOT ASSESSED，verdict 要點名每一項，絕對不能只寫一個 COMPLETE：

Verdict: **COMPLETE — [accessibility | engine validation] NOT ASSESSED ([reason])** — UI feature delivered; the named check could not run.

Verdict: **BLOCKED** — pipeline halted; surface the blocker and its phase before stopping.

## Next Steps

- 如果最終規格還沒通過，跑 `/ux-review`。
- 結案 story 之前，先對 UI 實作跑 `/code-review`。
- 如果需要視覺或音訊 polish，跑 `/team-polish`。
