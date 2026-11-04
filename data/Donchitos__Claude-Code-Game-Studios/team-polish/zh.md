---
name: team-polish
description: "統籌 polish 團隊（performance-analyst、technical-artist、sound-designer、qa-tester），把一個功能或區域最佳化並加固。"
argument-hint: "[feature or area to polish] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, TaskCreate, TaskGet, TaskList, TaskUpdate, Bash(bash "*/.claude/skills/team-polish/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---
# Team Polish

如果沒有帶參數，就輸出使用說明並結束，不要 spawn 任何 agent：
> 用法：`/team-polish [feature or area to polish] [--review full|lean|solo]` — 指定要 polish 的功能或區域（例如 `combat`、`main menu`、`inventory system`、`level-1`）。這裡不要用 `AskUserQuestion`，直接輸出說明。

帶了參數時，就用結構化的 pipeline 來統籌 polish 團隊。

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

**`team.size`**：哪些 agent 啟用（跟 review_mode 的 gate 深度和 workflow docs 互相獨立）。
- **`individual`**（預設）：`performance-analyst` + `technical-artist`。其他 agent 透過這兩個諮詢，不會另外 spawn。沒有任何 programmer 啟用，所以最佳化清單裡屬於 programmer 的項目在這次 run 不會實作，報告會寫明這份清單已交給 `/dev-story`（Phase 2）。
- **`small`**：加上 `sound-designer` + `qa-tester` + `engine-programmer`，以及當 Phase 1 把原因追到某個內容製作工具時的 `tools-programmer`（也就是文件中寫的完整 pipeline）。
- **`studio`**：`small` 的名單（含 `engine-programmer`），再加一輪對抗式審查：Phase 5 的 qa-tester 會被告知「your job is not to confirm this holds — find how it breaks」，報告也會講明這一輪有跑。這條 pipeline 沒有 engine specialist 可以擴充；引擎層級的工作仍由 `engine-programmer` 負責。
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
- **performance-analyst** — 效能剖析、記憶體分析、frame 預算，以及最佳化清單，它不寫任何遊戲程式碼
- **engine-programmer** — 實作最佳化清單裡屬於引擎層級的項目：渲染管線、記憶體、資源載入、熱點路徑（當 performance-analyst 找出底層根因時叫它）
- **technical-artist** — VFX polish、shader 最佳化、視覺品質
- **sound-designer** — 音訊 polish、混音、環境音 layer、回饋音效
- **tools-programmer** — 內容管線工具驗證、編輯器工具穩定性、自動化修正（Phase 2，當 Phase 1 把原因追到某個內容製作工具時）
- **qa-tester** — 邊界情況測試、回歸測試、浸泡測試

## How to Delegate

用 `Agent` 工具把每個團隊成員 spawn 成 subagent：
- `subagent_type: performance-analyst` — 效能剖析、記憶體分析、最佳化清單
- `subagent_type: engine-programmer` — 最佳化清單裡的引擎層級修正：渲染、記憶體、資源載入
- `subagent_type: technical-artist` — VFX polish、shader 最佳化、視覺品質
- `subagent_type: sound-designer` — 音訊 polish、混音、環境音 layer
- `subagent_type: tools-programmer` — 最佳化清單裡的內容管線與編輯器工具修正
- `subagent_type: qa-tester` — 邊界情況測試、回歸測試、浸泡測試

**給每個 agent 的 brief 要精簡，不要整包 context 倒過去。** 共用的輸入只讀**一次**，再把整理過的 brief 直接寫在 prompt 裡：只放每個 agent 真正需要的那幾行，你已經讀過的文件絕對不要只丟檔案路徑（agent 拿到路徑會把整份檔案重讀一遍）。只有你還沒讀、而且只有那個 agent 需要的文件，才給路徑。

**每個 agent 的 prompt 結尾都要加上回傳約定：**「Write your full output to `[path]` — that named path is your write authorisation under the bounded exception below, so write it without a separate approval prompt. Return **only** (1) the path written, (2) a ≤5-bullet summary of decisions, (3) any BLOCKED/CONCERNS items, one line each. Do not restate the documents you read.」沒有這個約定的話，agent 會把它讀過的東西全部倒回這個 session。**實作檔案是例外：** 寫程式或資產的 agent 要先回傳它打算建立或修改的檔案，而它的回傳約定要等你把整組檔案問過一次、使用者也答應之後才能指名這些檔案（File Write Protocol）。授權這些寫入的是那個答覆，不是有界例外。

**`[path]` 要換成真實路徑，這個 skill 的目的地是
`production/polish/`。** 依 agent 各自命名，一人一個檔案：

| Agent | Writes to |
|---|---|
| performance-analyst | `production/polish/[area]-report-[date].md` |
| technical-artist | `production/polish/[area]-render-notes-[date].md` |
| engine-programmer | `production/polish/[area]-engine-fixes-[date].md` |
| tools-programmer | `production/polish/[area]-tool-fixes-[date].md` |
| sound-designer | `production/polish/[area]-audio-notes-[date].md` |
| qa-tester | `production/polish/[area]-verification-[date].md` |

> **為什麼是 `production/` 不是 `docs/`。** 這些是單次 run 加上日期戳記的量測結果，形式跟 `production/qa/smoke-[date].md` 一樣，不是像 `docs/architecture/` 那種長期留存的規格。把它們放在其他某個時間點的流程產物旁邊，後續才有辦法做比較。
>
> 上面 `[path]` 約定有個前提：路徑是*你*指定的，所以這裡必須寫明具體的目的地，否則每次 run 都得自己發明一個。跟 `/team-qa` 和 `/team-narrative` 不同，它們的目的地是由消費者固定好的，而這個位置在 repo 裡沒有任何讀者，是刻意選的。
> **目前沒有任何東西會讀 `production/polish/`**，回報時要講明這點，讓使用者知道這份報告是一份紀錄，不是後續某個 gate 的輸入。

> **為什麼這不違反 Collaboration Protocol。** `CLAUDE.md` 要求 agent 在 Write/Edit 之前先問「May I write this to [filepath]?」。這裡 spawn 出來的 subagent **不問**就寫，這是刻意設計的有界例外，不是疏忽，跟 `consistency-check` 附加寫入 `active.md` 是同一個決定。這個例外只在三個條件**同時**成立時才有效：(1) 路徑是**你**在 prompt 裡指定的，所以使用者核准這個 phase 的時候，就等於核准了目的地；(2) 它是 `production/`、`docs/` 或 `tests/` 底下的新產物，絕對不是改既有的原始碼或設定；(3) 產生它的那個 phase，本身在 pipeline 往下走之前有 `AskUserQuestion` 把關。這三條以外，agent 一定要先問。**不要靠「每個 subagent 都問一次」來「修」這件事**：每個 agent 每個 phase 都跳一次提示，會讓 orchestrator 根本沒辦法用，這就是這個例外存在的原因。

只要 pipeline 允許，就把互相獨立的 agent 平行啟動（例如 Phase 3 和 4 可以同時跑）。

## Pipeline

### Phase 1: Assessment
委派給 **performance-analyst**：
- 用 `/perf-profile` 對目標功能／區域做效能剖析
- 找出效能瓶頸與違反 frame 預算的地方
- 量測記憶體用量並檢查有沒有洩漏
- 對照目標硬體規格做 benchmark
- 輸出：附有優先順序的**最佳化清單**的效能報告，每一項要寫明改動內容、對照預算的預期收益，以及負責人（渲染端的改動歸 technical-artist、引擎系統與熱點路徑歸 engine-programmer、內容製作工具歸 tools-programmer，其他歸擁有該系統的 programmer）

### Phase 2: Optimization
performance-analyst 不寫任何遊戲程式碼（「recommend and assign」，見它的 agent 檔案），所以 Phase 2 要透過啟用名單內的負責人，來實作它 Phase 1 的清單：
- **engine-programmer**：只有 Phase 1 找出引擎層級的根因（渲染管線、資源載入、記憶體配置器、核心迴圈的熱點路徑）時才 spawn：實作那些項目、修掉配置壓力、驗證遊戲行為沒有改變。輸出：附前後指標與 profiler 驗證的引擎層級修正
- **tools-programmer**：只有 Phase 1 把原因追到某個內容製作工具時才用：修那個工具。輸出：附前後指標的工具修正
- **technical-artist**：渲染端的項目（draw call、overdraw、粒子、shader、LOD）併入它 Phase 3 的 brief

Phase 2–4 每個負責實作的 agent，都要先回傳它打算建立或修改的檔案，而在任何檔案被編輯之前，你要對整個 Phase 2–4 的檔案組一次問清楚（File Write Protocol）。

**負責人不在啟用名單內的項目，這次 run 不實作。**
在 `team.size: individual` 下，這代表每個 programmer 的項目，因為沒有任何 programmer 啟用；不管什麼 size，只要某項由這條 pipeline 沒有點名的 programmer 負責（例如遊戲腳本熱點歸 gameplay-programmer），也包含在內。報告要把這些項目連同負責人列在
「Optimisation list handed to `/dev-story`: `production/polish/[area]-report-[date].md`」底下。
它們針對的指標如果超出預算，到 Phase 6 仍然算已知問題。

### Phase 3: Visual Polish (parallel with Phase 2)
委派給 **technical-artist**：
- 檢視 VFX 的品質，以及跟 art bible 的一致性
- 最佳化粒子系統與 shader 特效
- 在適當的地方加入螢幕震動、鏡頭效果與視覺 juice
- 確保特效在較低的畫質設定下能平順降級
- 輸出：polish 過的視覺特效

### Phase 4: Audio Polish (parallel with Phase 2)
委派給 **sound-designer**：
- 檢視音訊事件是否完整（有沒有哪些動作缺少聲音回饋？）
- 檢查混音音量，相對於整體混音，不能有太大聲或太小聲的東西
- 加入環境音 layer 來營造氣氛
- 驗證音訊的空間定位播放正確
- 輸出：音訊 polish 清單與混音筆記

### Phase 5: Hardening
委派給 **qa-tester**：
- 測試所有邊界情況：邊界條件、快速連按輸入、不尋常的操作順序
- 浸泡測試：讓功能長時間運行，檢查有沒有效能退化
- 壓力測試：實體數量上限、最糟的情境
- 回歸測試：驗證 polish 的改動沒有弄壞既有功能，Phase 2–4 的每項改動都要逐一點名，包括引擎層級的修正
- 在最低規格的硬體上測試（如果有的話）
- 輸出：附剩餘問題的測試結果

### Phase 6: Sign-off
- 收集所有團隊成員的結果
- 把效能指標跟預算做比較
- 回報：READY FOR RELEASE / NOT ASSESSED / NEEDS MORE WORK
- 列出每個剩餘問題，附嚴重程度（S1–S4）、有的話附實測差距（例如「9 ms against a 6 ms budget — 3 ms over」）以及建議；回歸問題還要點名壞掉的行為，和造成它的 polish 改動

**NOT ASSESSED 的排序高於 READY FOR RELEASE，低於 NEEDS MORE WORK。** 有已知問題（指標超出預算、未解決的回歸）時，不管其他還有什麼沒檢查，都是 NEEDS MORE WORK。除此之外，如果範圍內有任何部分無法檢查，結果就是 NOT ASSESSED，絕對不是 READY FOR RELEASE，而且報告要點名每個缺口：
- 沒有已提交預算的指標。`performance.target_framerate`、`performance.frame_budget_ms`、`performance.draw_call_limit` 和 `performance.memory_ceiling_mb` 都沒有預設值，而 `/perf-profile` 會把沒設定的回報為 NOT ASSESSED：什麼都沒比較，所以也談不上達標。
- 沒有執行的 phase：BLOCKED、被略過，或它的 agent 不在啟用名單內。在 `team.size: individual` 下，sound-designer 的音訊 polish 和 qa-tester 的 hardening 只是透過啟用中的 agent 諮詢，並沒有真的跑，而且 Phase 2 的 programmer 項目是交給 `/dev-story`，而不是實作。

## Error Recovery Protocol

**先驗證產物。** 如果回傳約定指定了路徑，在把這個 phase 當成做完之前，先確認該路徑真的存在：**指名的產物不在磁碟上，就是失敗的 phase，不管回覆讀起來多流暢。** agent 可能耗掉整個 phase，回你一段看似合理的開場白，卻什麼都沒寫；這既不是 BLOCKED、也不是錯誤、也不是「無法完成」，所以下面的觸發條件永遠不會被觸發。要叫它繼續，並指明沒達成的約定；context 通常還在。

如果任何 spawn 出去的 agent 回傳 BLOCKED、出錯或無法完成：**立刻揭露，不要越過它所阻擋的依賴項繼續往下走，而且一定要產出部分報告。** 被略過的 agent 那一節要留成一個有名字的缺口，絕對不准用你自己的內容填進去。完整流程：`.claude/docs/error-recovery-protocol.md`。

常見的阻擋原因：
- 輸入檔案缺失（找不到 story、GDD 不存在）→ 導向建立它的 skill
- ADR 狀態是 Proposed → 不要實作；決定之後，用 `/architecture-decision accept ADR-NNNN` 接受它
- 範圍太大 → 用 `/create-stories` 拆成兩個 story
- ADR 和 story 的指示互相衝突 → 把衝突揭露出來，不要猜

## File Write Protocol

所有檔案寫入（效能報告、測試結果、佐證文件）都委派給透過 `Agent` spawn 的 sub-agent。這些寫入適用上面「為什麼這不違反 Collaboration Protocol」所記載的**有界例外**：路徑是你指定的、產物是 `production/`、`docs/` 或 `tests/` 底下的新檔案、而且這個 phase 有 `AskUserQuestion` 把關。在這些範圍內，sub-agent **不會**每次寫入都問；範圍之外就一定要問。Phase 2–4 的最佳化與 polish 改動是在修改既有的程式碼、shader、音訊或資產，所以在那些範圍之外：每個負責實作的 agent 先回傳它打算建立或修改的檔案，你對整個 Phase 2–4 的檔案組問一次（「May I have [agents]
change these [N] files?」），每個 agent 在得到肯定答覆後才編輯，整組只問一次，不是每個 phase 問一次。這個 orchestrator 不會直接寫檔案。

## Output

一份摘要報告，涵蓋：效能前後指標、視覺 polish 的改動、音訊 polish 的改動、測試結果、任何交給 `/dev-story` 的最佳化清單，以及發布就緒度的評估。

## Next Steps

- 如果是 READY FOR RELEASE：跑 `/release-checklist` 做發布前的最終驗證。
- 如果是 NEEDS MORE WORK：把剩餘問題排進 `/sprint-plan update`（在沒有 sprint 的 `workflow: minimal` 下，改加進 brief 的 build order），修好之後重跑 `/team-polish`。
- 如果是 NOT ASSESSED：補上缺的東西：在 `project.yaml` 提交沒設定的 `performance.*` 預算（`/settings`），或把沒跑的 phase 跑完（提高 `team.size`），然後重跑 `/team-polish`。不要把這個區域當成可以發布。
- 如果報告把最佳化清單交給了 `/dev-story`：在那邊實作這些項目，再重跑 `/team-polish` 量測收益。
- 交接給發布之前，跑 `/gate-check` 取得正式的 phase gate verdict。
