---
name: team-combat
description: "統籌戰鬥團隊（game-designer、gameplay-programmer、ai-programmer、technical-artist、sound-designer、qa-tester），從設計一路帶到實作與驗證。"
argument-hint: "[combat feature description] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, TaskCreate, TaskGet, TaskList, TaskUpdate, Bash(bash "*/.claude/skills/team-combat/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---
# Team Combat

**參數檢查：** 如果沒有提供戰鬥功能描述，就輸出：
> "Usage: `/team-combat [combat feature description] [--review full|lean|solo]` — Provide a description of the combat feature to design and implement (e.g., `melee parry system`, `ranged weapon spread`)."
然後立刻停止，不要 spawn 任何 subagent，也不要讀任何檔案。

帶了有效參數時，就用結構化的 pipeline 來統籌戰鬥團隊。

**決策點：** 每個 phase 轉換時，用 `AskUserQuestion` 把 subagent 的提案做成可選項目給使用者選。先在對話中寫出 agent 的完整分析，再用簡短的標籤收下決定。
在 `collaborative` 模式下，使用者核准後才能進下一個 phase。
在 `guided` 模式下，pipeline 會自動往下走，除非某個 phase BLOCKED；
在 `autonomous` 模式下會從頭跑到尾，每個 phase 的結果用 `log_decision` 記錄下來。
屬於 `automation_always_ask` 類別的決策（`is_always_ask_category` helper）不管什麼模式一律要問。參見 `.claude/docs/automation-modes.md`。

## Phase 0: Resolve Config

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,team.size,workflow`

上面已經解析好了，直接用；`--review` 會覆蓋 `review_mode`。沒有這個區塊的話，就用 `.claude/docs/config-resolution.md` 裡的預設值。

`review_mode` 決定 director gate 的深度，而這條 pipeline 沒有 director gate：
下面任何 phase 在任何 `review_mode` 下，都不會 spawn CD-、TD-、PR- 或 AD-PHASE-GATE。它的 phase gate 就是 pipeline 自己的決策點（定義在下面的 `team.size` 底下），在這些點上工作的 agent 是團隊成員，不是 director gate。

`automation` 決定上面「決策點」那段的行為。各模式如何改變 pipeline 的行為，見上面的決策點說明和 `.claude/docs/automation-modes.md`。

`workflow` 決定 Phase 1 設計文件的份量，做法跟 `/design-system` 一樣：
`full` 要寫 `## Summary` 加全部 8 個章節；`standard` 寫 Overview、Detailed Design、Edge Cases、Dependencies 和 Acceptance Criteria，只要機制有定義數值規則（戰鬥機制幾乎一定有）就再加 Formulas；`minimal` 則以 game brief 當設計紀錄，GDD 是選用的：照樣草擬那五個章節，並告訴使用者在這個 workflow 層級它是選用的。

**`team.size`**：哪些 agent 啟用（跟 review_mode 的 gate 深度和 workflow docs 互相獨立）。
- **`individual`**（預設）：由 `gameplay-programmer` 跑整條 pipeline；只有功能涉及 AI 工作時，才升級叫 `ai-programmer`。Team Composition 裡的其他 agent 透過 gameplay-programmer 諮詢，不會另外 spawn。
- **`small`**：下面文件寫的完整 Team Composition pipeline。
- **`studio`**：完整 pipeline + 引擎 sub-specialist + 一輪對抗式審查。*引擎 sub-specialist*：primary engine specialist 的 prompt 寫明，它可以把一部分審查交給它的 `tools:` 授權所指名的 sub-specialist（例如能力系統用 `ue-gas-specialist`）；低於 `studio` 時它自己一個人回答。*對抗式審查*：Phase 5 的 qa-tester 會被告知「your job is not to confirm this works — find how it breaks」，報告也會講明這一輪有跑。
在 `individual` 下需要用到的非核心 agent，會改由最接近的核心 agent 處理，並附一則說明。**「Phase gate」指的是這條 pipeline 自己列出、以 `AskUserQuestion` 決策點收尾的任何 phase**：可能是上面「決策點」底下的某個轉換，也可能是下面 pipeline 裡寫明的 **Gate** 步驟，**不管 `automation` 是哪個模式都一樣。** `guided` 和 `autonomous` 改變的是 gate 怎麼通過（自動往下走，或用 `log_decision` 記錄），不是它算不算 gate，所以下面的有界例外條件 (3) 在每個模式下的 gate 都成立。被限制成「只在 phase gate 出場」的 agent，只會在這些時點 spawn，其他時候不會。這個「依啟用名單縮小範圍」的規則適用於下面整條 pipeline：任何 phase 只要點名了啟用名單以外的 agent，就改由最接近的核心 agent 處理，不 spawn 它。

**在 Phase 1 之前先公布啟用名單，絕對不准讓縮減悄悄發生。**
spawn 任何東西之前，先用一行講清楚這次實際會 spawn 哪些 agent，以及下面 pipeline 有點名、但在目前 `team.size` 下**不會** spawn 的有哪些。例如：

> `Active set (team.size: <resolved>): <the agents listed for that size above>.`
> `Not spawned this run: <every other agent this pipeline names> — consulted`
> `through <nearest active core agent>. Raise team.size (or modes.rigor) to widen.`

內容要直接從上面的 `team.size` 清單和這個檔案自己的 pipeline 所點名的 agent 填，不要照抄範例。每個 orchestrator 這兩組名單都不一樣。

下面這條 pipeline 看起來像多 agent 的 fan-out，但在預設值下其實只有一兩個 agent：`team-release` 點名了十個、只跑一個，`team-narrative` 在五個 phase 裡點名了六個、只跑 `writer` 一個。**這樣縮減是對的**：`team.size` 是以嚴謹度為前提的，預設收窄就是用來省 token 的。
如果不明講，讀的人就分不出「正確縮減過的 run」和「壞掉的 pipeline」，而上面那條「由最接近的核心 agent 處理並附說明」的規則是在路由當下才觸發，從來不會交代整個 run 的樣子。

這跟這個檔案其他地方的「略過的檢查要回報」是同一條規則：**一個有被執行、卻從沒被講出來的限制，對讀輸出的人來說，跟從來沒執行過的限制看起來一模一樣。**

## Team Composition
- **game-designer** — 設計機制，定義公式與邊界情況
- **gameplay-programmer** — 實作核心遊戲玩法程式碼
- **ai-programmer** — 為這個功能實作 NPC／敵人的 AI 行為
- **technical-artist** — 製作 VFX、shader 特效與視覺回饋
- **sound-designer** — 定義音訊事件、打擊音效與戰鬥環境音
- **engine specialist**（primary）— 驗證架構與實作模式對該引擎來說是慣用做法（primary specialist 是由 `engine.name` 推導的 `<engine>-specialist`：Godot→`godot-specialist`、Unity→`unity-specialist`、Unreal→`unreal-specialist`；找不到時，退回 `technical-preferences.md` 裡 `## Engine Specialists` 的 Primary 那一行）
- **qa-tester** — 撰寫測試案例並驗證實作

## How to Delegate

用 `Agent` 工具把每個團隊成員 spawn 成 subagent：
- `subagent_type: game-designer` — 設計機制，定義公式與邊界情況
- `subagent_type: gameplay-programmer` — 實作核心遊戲玩法程式碼
- `subagent_type: ai-programmer` — 實作 NPC／敵人的 AI 行為
- `subagent_type: technical-artist` — 製作 VFX、shader 特效、視覺回饋
- `subagent_type: sound-designer` — 定義音訊事件、打擊音效、環境音
- `subagent_type: [primary engine specialist]` — 驗證架構與實作是否符合引擎慣用做法
- `subagent_type: qa-tester` — 撰寫測試案例並驗證實作

**給每個 agent 的 brief 要精簡，不要整包 context 倒過去。** 共用的輸入只讀**一次**，再把整理過的 brief 直接寫在 prompt 裡：只放每個 agent 真正需要的那幾行，你已經讀過的文件絕對不要只丟檔案路徑（agent 拿到路徑會把整份檔案重讀一遍）。只有你還沒讀、而且只有那個 agent 需要的文件，才給路徑。

**每個 agent 的 prompt 結尾都要加上回傳約定：**「Write your full output to `[path]` — that named path is your write authorisation under the bounded exception below, so write it without a separate approval prompt. Return **only** (1) the path written, (2) a ≤5-bullet summary of decisions, (3) any BLOCKED/CONCERNS items, one line each. Do not restate the documents you read.」沒有這個約定的話，agent 會把它讀過的東西全部倒回這個 session。**實作檔案是例外：** 寫程式或資產的 agent 要先回傳它打算建立或修改的檔案，而它的回傳約定要等你把整組檔案問過一次、使用者也答應之後才能指名這些檔案（File Write Protocol）。授權這些寫入的是那個答覆，不是有界例外。

**`[path]` 要換成真實路徑。** 每個會產出產物的 phase 都要指名一個路徑；大部分已經由讀取它們的 skill 固定好了：

| Phase / agent | Writes to | Destination fixed by |
|---|---|---|
| 1 game-designer (draft) | `production/combat/[feature]-gdd-draft.md` | this skill — you write the final `design/gdd/[feature].md` (Phase 1) |
| 2 gameplay-programmer | `docs/architecture/[feature]-sketch.md` | see note below |
| 2 engine specialist | `docs/architecture/[feature]-engine-notes.md` | see note below |
| 3 gameplay-programmer, ai-programmer, technical-artist | the code root and `assets/` — the files the Phase 3 approval lists | outside the bounded exception: asked once for the set (File Write Protocol) |
| 3 sound-designer | `production/combat/[feature]-audio-events.md` | this skill |
| 5 qa-tester (test cases) | `production/qa/test-cases/[feature]-cases.md` | `/team-qa` Phase 4 |
| 5 qa-tester (bugs) | `production/qa/bugs/BUG-[NNNN].md` | `/team-qa` Phase 5 |

Phase 6 是口頭的狀態報告，不是產物，所以不需要路徑，也沒有路徑。

> **上面每個 phase 都刻意指名了具體的目的地。** 下面的 Error Recovery Protocol 說「指名的產物不在磁碟上，就是失敗的 phase」，而沒有指名路徑的話，這個檢查根本跑不起來。
>
> **兩個 `docs/architecture/` 項目是判斷後的選擇，不是慣例。** 那個目錄放的是 ADR（`adr-NNNN-*.md`）；sketch 是 ADR 的前身，本身不是 ADR，而且 **repo 裡沒有任何東西會讀這兩個檔案**。回報的時候要講明這點，讓人知道 sketch 是一份紀錄，不是後面某個 gate 的輸入。

> **為什麼這不違反 Collaboration Protocol。** `CLAUDE.md` 要求 agent 在 Write/Edit 之前先問「May I write this to [filepath]?」。這裡 spawn 出來的 subagent **不問**就寫，這是刻意設計的有界例外，不是疏忽，跟 `consistency-check` 附加寫入 `active.md` 是同一個決定。這個例外只在三個條件**同時**成立時才有效：(1) 路徑是**你**在 prompt 裡指定的，所以使用者核准這個 phase 的時候，就等於核准了目的地；(2) 它是 `production/`、`docs/` 或 `tests/` 底下的新產物，絕對不是改既有的原始碼或設定；(3) 產生它的那個 phase，本身在 pipeline 往下走之前有 `AskUserQuestion` 把關。這三條以外，agent 一定要先問。**不要靠「每個 subagent 都問一次」來「修」這件事**：每個 agent 每個 phase 都跳一次提示，會讓 orchestrator 根本沒辦法用，這就是這個例外存在的原因。

只要 pipeline 允許，就把互相獨立的 agent 平行啟動（例如 Phase 3 的 agent 可以同時跑）。

## Pipeline

### Phase 1: Design
委派給 **game-designer**：
- 根據 `.claude/docs/templates/game-design-document.md`，建立或更新 `design/gdd/[feature].md` 的設計文件，內容包含 `## Summary` 和 `workflow` 要求的章節（Phase 0）。在 `full` 下：機制概述、玩家幻想、詳細規則、帶變數定義的公式、邊界情況、依賴項、帶安全範圍的調校參數，以及驗收標準
- 輸出：完成的設計文件，草稿寫到 `production/combat/[feature]-gdd-draft.md`

`design/` 在上面的有界寫入例外之外，所以由 game-designer 起草，**你**來寫 GDD，也就是 `/team-level` 和 `/team-narrative` 用的模式。在 Phase 1 的決策點，把草稿呈現出來，並透過 `AskUserQuestion` 問：「May I write the design document to
`design/gdd/[feature].md`?」核准後再寫；在得到這個答覆之前，`design/` 底下什麼都不能寫。

### Phase 2: Architecture
委派給 **gameplay-programmer**（如果涉及 AI，再加上 **ai-programmer**）：
- 檢視設計文件，要分段讀：先用 Grep 工具（pattern `^#`，content mode）找出需要的標題，再用 offset 和 limit 讀那些範圍
- 設計程式架構：class 結構、介面、資料流
- 找出跟現有系統的整合點
- 輸出：附檔案清單與介面定義的架構草圖

接著 spawn **primary engine specialist** 來驗證提議的架構：
- class／node／component 的結構，對鎖定的引擎來說是慣用做法嗎？（例如 Godot 的 node 階層、Unity 的 MonoBehaviour vs DOTS、Unreal 的 Actor/Component 設計）
- 有沒有該用引擎原生系統、而不是自己做的地方？
- 提議的 API 有沒有在鎖定的引擎版本裡被棄用或改動？
- 輸出：引擎架構筆記，在 Phase 3 開始前併入架構

如果沒有設定引擎，就跳過 specialist 的 spawn。**在這次 run 的輸出裡記下 ``Engine validation: NOT ASSESSED — no engine configured (`engine.name` unset in `project.yaml`)``。** 被略過卻不吭聲的檢查，跟通過的檢查看起來一模一樣。

使用 `AskUserQuestion`：
- Prompt: "Architecture sketch complete. Approve to proceed with parallel implementation."
- Options:
  - `[A] Proceed — spawn implementation agents (gameplay-programmer, ai-programmer, technical-artist, sound-designer)`
  - `[B] Revise the architecture first — I'll describe what needs to change`
  - `[C] Stop here — I'll continue later`

使用者選 [A] 才 spawn 實作 agent。（在 `guided`／`autonomous` 模式下，這個架構 gate 就是一般的 phase 轉換：除非架構草圖回傳 BLOCKED，否則直接進入實作，autonomous 模式下用 `log_decision` 記錄這個決定。這個 gate 不是對發布有關鍵影響、或不可逆的決策，所以照標準的 pipeline 規則走。）

### Phase 3: Implementation (parallel where possible)
平行委派：
- **gameplay-programmer**：實作核心戰鬥機制的程式碼
- **ai-programmer**：實作 AI 行為（如果功能涉及 NPC 反應）
- **technical-artist**：製作 VFX 和 shader 特效
- **sound-designer**：定義音訊事件清單與混音筆記，草稿寫到 `production/combat/[feature]-audio-events.md`

程式碼、VFX 和 shader 的工作在有界寫入例外之外：這些 agent 各自先回傳它們打算建立或修改的檔案，你對整組檔案問一次，答應之後它們才寫（File Write Protocol）。

### Phase 4: Integration
- 把遊戲玩法程式碼、AI、VFX 和音訊串在一起
- 確保所有調校參數都有公開出來，而且是資料驅動的
- 驗證這個功能跟現有的戰鬥系統能一起運作

**Gate**：用 `AskUserQuestion` 呈現整合結果，確認後再進 Phase 5。

### Phase 5: Validation
委派給 **qa-tester**：
- 根據驗收標準撰寫測試案例
- 測試設計裡記載的所有邊界情況
- 驗證效能影響在預算內
- 發現的任何問題都要開 bug 回報

### Phase 6: Sign-off
- 收集所有團隊成員的結果
- 回報功能狀態：COMPLETE / NEEDS WORK / BLOCKED
- 列出所有未解決的問題與指派的負責人

## Error Recovery Protocol

**先驗證產物。** 如果回傳約定指定了路徑，在把這個 phase 當成做完之前，先確認該路徑真的存在：**指名的產物不在磁碟上，就是失敗的 phase，不管回覆讀起來多流暢。** agent 可能耗掉整個 phase，回你一段看似合理的開場白，卻什麼都沒寫；這既不是 BLOCKED、也不是錯誤、也不是「無法完成」，所以下面的觸發條件永遠不會被觸發。要叫它繼續，並指明沒達成的約定；context 通常還在。

如果任何 spawn 出去的 agent 回傳 BLOCKED、出錯或無法完成：**立刻揭露，不要越過它所阻擋的依賴項繼續往下走，而且一定要產出部分報告。** 被略過的 agent 那一節要留成一個有名字的缺口，絕對不准用你自己的內容填進去。完整流程：`.claude/docs/error-recovery-protocol.md`。

常見的阻擋原因：
- 輸入檔案缺失（找不到 story、GDD 不存在）→ 導向建立它的 skill
- ADR 狀態是 Proposed → 不要實作；決定之後，用 `/architecture-decision accept ADR-NNNN` 接受它
- 範圍太大 → 用 `/create-stories` 拆成兩個 story
- ADR 和 story 的指示互相衝突 → 把衝突揭露出來，不要猜

## File Write Protocol

所有檔案寫入（設計草稿、實作檔案、測試案例）都委派給透過 `Agent` spawn 的 sub-agent，並遵守兩條規則：

- **草稿、sketch 和 QA 產物**，也就是路徑表裡 `production/`、`docs/` 或 `tests/` 底下的目的地，適用上面「為什麼這不違反 Collaboration Protocol」所記載的**有界例外**：路徑是你指定的、產物是新的、而且這個 phase 有 `AskUserQuestion` 把關。sub-agent 寫這些檔案時，不會每次寫入都問。
- **實作檔案**，也就是 Phase 3 的程式碼、VFX 和 shader 檔案，以及 Phase 4 的任何整合修改，位於 code root 和 `assets/` 底下，在那個例外之外，這點 agent 自己的檔案也都有寫。每個負責實作的 agent 先回傳它打算建立或修改的檔案，每個附一行摘要；你對整組檔案問一次（「May I have [agents] write these [N] files?」），答應之後它們才寫。修改既有檔案一定要列在那份清單上，不能當作 Phase 3 之前的那個 gate 已經隱含同意了。

**唯一的例外是設計文件**：orchestrator 根據 game-designer 的草稿，在自己的「May I write …?」提示之後（Phase 1），親自寫入 `design/gdd/[feature].md`。除此之外它不寫任何檔案。

## Output

一份摘要報告，涵蓋：設計完成狀態、各團隊成員的實作狀態、測試結果，以及任何未解決的問題。

Verdict: **COMPLETE** — combat feature designed, implemented, and validated.

如果引擎驗證被略過（Phase 2，沒有設定引擎），verdict 要講明，絕對不能只寫一個 COMPLETE：

Verdict: **COMPLETE — engine validation NOT ASSESSED ([reason])** — combat feature designed, implemented, and validated; the engine specialist never reviewed the architecture.

Verdict: **NEEDS WORK** — every phase ran, but Phase 5 validation left failures or open bugs unresolved; the report lists each with its owner.

Verdict: **BLOCKED** — one or more phases could not complete, or an agent was skipped (`.claude/docs/error-recovery-protocol.md` step 5); partial report produced with unresolved items listed.

## Next Steps

- 結案 story 之前，先對實作好的戰鬥程式碼跑 `/code-review`。
- 跑 `/balance-check` 驗證戰鬥公式和調校數值。
- 如果需要 VFX、音訊或效能的 polish，跑 `/team-polish`。
