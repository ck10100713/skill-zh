---
name: team-narrative
description: "統籌敘事團隊（narrative-director、writer、world-builder、level-designer），處理劇情、世界背景設定與敘事導向的關卡。"
argument-hint: "[narrative content description] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, TaskCreate, TaskGet, TaskList, TaskUpdate, Bash(bash "*/.claude/skills/team-narrative/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---
# Team Narrative

如果沒有帶參數，就輸出使用說明並結束，不要 spawn 任何 agent：
> 用法：`/team-narrative [narrative content description] [--review full|lean|solo]` — 描述要處理的劇情內容、場景或敘事區域（例如 `boss encounter cutscene`、`faction intro dialogue`、`tutorial narrative`）。這裡不要用 `AskUserQuestion`，直接輸出說明。

帶了參數時，就用結構化的 pipeline 來統籌敘事團隊。

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

Phase 4 的 ND-CONSISTENCY 在每個模式下都是例外：它是這條 pipeline 自己的審查，不是選用的 director gate，所以 `review_mode` 永遠不會跳過它（誰來跑它還是由 `team.size` 決定，見 Phase 4）。

`automation` 決定上面「決策點」那段的行為。各模式如何改變 pipeline 的行為，見上面的決策點說明和 `.claude/docs/automation-modes.md`。

**`team.size`**：哪些 agent 啟用（跟 review_mode 的 gate 深度和 workflow docs 互相獨立）。
- **`individual`**（預設）：只有 `writer`；`narrative-director` 只在明確出現支柱衝突時才叫。其他 agent 透過 writer 諮詢，不會另外 spawn。
- **`small`**：`narrative-director` + `writer`，加上 `review_mode` 為 `full` 時的 `localization-lead` 和 `world-builder`（在 `lean` 和 `solo` 下，它們透過 writer 諮詢）。
- **`studio`**：Team Composition 裡全部六個 agent，不管 `review_mode` 是什麼（也就是文件中寫的完整 pipeline）。
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
- **narrative-director** — 故事弧線、角色設計、對白策略、敘事願景
- **writer** — 撰寫對白、背景設定條目、道具說明、遊戲內文字
- **world-builder** — 世界規則、陣營設計、歷史、地理、環境敘事
- **art-director** — 角色視覺設計、環境視覺敘事、過場／電影化演出的基調
- **level-designer** — 為敘事服務的關卡配置、節奏、環境敘事節拍
- **localization-lead** — 在地化就緒度：標出無法在地化的字串、文化假設與 i18n 缺口

## How to Delegate

用 `Agent` 工具把每個團隊成員 spawn 成 subagent：
- `subagent_type: narrative-director` — 故事弧線、角色設計、敘事願景
- `subagent_type: writer` — 撰寫對白、背景設定條目、遊戲內文字
- `subagent_type: world-builder` — 世界規則、陣營設計、歷史、地理
- `subagent_type: art-director` — 角色視覺設定、環境視覺敘事、電影化基調
- `subagent_type: level-designer` — 為敘事服務的關卡配置、節奏
- `subagent_type: localization-lead` — 在地化就緒度：標出無法在地化的字串、文化假設與 i18n 缺口

**先讀 canon。** 在 Phase 1 之前，先讀現有的共用輸入：敘事聖經或基調指南、`design/narrative/` 底下的角色與陣營檔案，以及世界規則。絕對不要叫 agent 自己發明 canon：如果根本沒有，就講明這一點，並在開始起草之前先問使用者。

**給每個 agent 的 brief 要精簡，不要整包 context 倒過去。** 共用的輸入只讀**一次**，再把整理過的 brief 直接寫在 prompt 裡：只放每個 agent 真正需要的那幾行，你已經讀過的文件絕對不要只丟檔案路徑（agent 拿到路徑會把整份檔案重讀一遍）。只有你還沒讀、而且只有那個 agent 需要的文件，才給路徑。

**每個 agent 的 prompt 結尾都要加上回傳約定：**「Write your full output to `[path]` — that named path is your write authorisation under the bounded exception below, so write it without a separate approval prompt. Return **only** (1) the path written, (2) a ≤5-bullet summary of decisions, (3) any BLOCKED/CONCERNS items, one line each. Do not restate the documents you read.」沒有這個約定的話，agent 會把它讀過的東西全部倒回這個 session。

**`[path]` 要換成真實路徑。** Agent 把草稿寫在
`production/narrative/[content-slug]/` 底下，這在下面的有界例外之內。完成的文件屬於 `design/narrative/`，而例外**不**涵蓋那裡，所以那些由**你**在一次核准之後去寫（見「Write the finals」）：

| Agent | Drafts to (`[path]`) | Final document (you write it) |
|---|---|---|
| narrative-director | `production/narrative/[content-slug]/brief.md` | `design/narrative/[content-slug]-brief.md` |
| world-builder | `production/narrative/[content-slug]/lore-[topic].md` | `design/narrative/lore/[topic].md` |
| writer | `production/narrative/[content-slug]/dialogue-[scene-slug].md` | `design/narrative/dialogue/[scene-slug].md` |
| art-director | `production/narrative/[content-slug]/visual-direction.md` | `design/narrative/[content-slug]-visual-direction.md` |
| level-designer | `production/narrative/[content-slug]/level-integration.md` | `design/narrative/[content-slug]-level-integration.md` |
| localization-lead | `production/narrative/[content-slug]/i18n-review.md` | stays in `production/` — a review, not a design document |

> **最終目的地不能隨便選。** `design/narrative/` 會被
> `/asset-spec`、`/design-review`、`/localize`、`/onboard`、
> `/project-stage-detect`、`/team-level` 和 `cd-narrative` director gate 讀取。
> 寫到其他地方的產物，這七個全都看不到。
>
> 上面 `[path]` 約定有個前提：路徑是*你*指定的。一個 skill 如果講了這個約定、卻沒指名具體的目的地，每次 run 都得自己發明一個，約定就形同虛設。`/team-qa` 的 Phase 4 基於同樣的理由，也有同樣的要求。

> **為什麼這不違反 Collaboration Protocol。** `CLAUDE.md` 要求 agent 在 Write/Edit 之前先問「May I write this to [filepath]?」。這裡 spawn 出來的 subagent **不問**就寫，這是刻意設計的有界例外，不是疏忽，跟 `consistency-check` 附加寫入 `active.md` 是同一個決定。這個例外只在三個條件**同時**成立時才有效：(1) 路徑是**你**在 prompt 裡指定的，所以使用者核准這個 phase 的時候，就等於核准了目的地；(2) 它是 `production/`、`docs/` 或 `tests/` 底下的新產物，絕對不是改既有的原始碼或設定；(3) 產生它的那個 phase，本身在 pipeline 往下走之前有 `AskUserQuestion` 把關。這三條以外，agent 一定要先問。**不要靠「每個 subagent 都問一次」來「修」這件事**：每個 agent 每個 phase 都跳一次提示，會讓 orchestrator 根本沒辦法用，這就是這個例外存在的原因。

只要 pipeline 允許，就把互相獨立的 agent 平行啟動（例如 Phase 2 的 agent 可以同時跑）。

## Pipeline

### Phase 1: Narrative Direction
委派給 **narrative-director**：
- 定義這份內容的敘事目的：它服務哪個劇情節拍？
- 找出涉及的角色、他們的動機，以及這跟整體弧線怎麼搭
- 設定情緒基調與節奏目標
- 指明任何背景設定的依賴項，或這份內容引入的新背景設定
- 輸出：附劇情需求的敘事 brief

### Phase 2: World Foundation (parallel)
平行委派：三個 `Agent` 呼叫要同時發出去，才去等任何結果：
- **world-builder**：為跟這份內容相關的陣營、地點和歷史建立或更新背景設定條目。對照既有的背景設定檢查有沒有矛盾。為新條目設定 canon 等級。
- **writer**：用聲音設定檔起草角色對白。確保每句都在 120 個字元以內、變數用具名佔位符、而且已為在地化做好準備。
- **art-director**：為這份內容中出現的關鍵角色定義角色視覺設計方向（剪影、視覺原型、辨識特徵）。為每個關鍵空間指定環境視覺敘事的元素（道具構成、光照筆記、空間安排）。為任何過場或腳本化的段落定義色調盤與電影化方向。

**Phase gate：** 收齊 Phase 2 的三份產出，然後在開始 Phase 3 之前套用「決策點」的規則：呈現背景設定、對白和視覺方向的摘要，在 `collaborative` 模式下透過 `AskUserQuestion` 取得核准（`guided` 下自動往下走，除非某個結果是 BLOCKED；`autonomous` 下用 `log_decision` 記錄）。

### Phase 3: Level Narrative Integration
委派給 **level-designer**：
- 檢視敘事 brief 與背景設定基礎
- 設計關卡裡的環境敘事元素
- 放置敘事觸發點、對白區域與發現點
- 確保節奏同時服務遊戲玩法和劇情

### Phase 4: Review and Consistency
透過 `Agent` spawn `narrative-director`，使用 gate **ND-CONSISTENCY**
（`.claude/docs/director-gates/nd-consistency.md`）。這個 phase 在每個 review mode 下都會跑：它是這條 pipeline 自己的審查，不是選用的 director gate。傳入那個 gate 列出的 context（Phase 2–3 的草稿路徑、敘事聖經或基調指南、世界規則、受影響的角色與陣營設定檔），這些已經在這裡點名了，所以不要在這個 session 裡讀 gate 檔案，然後再加上：
- 確認敘事節奏跟關卡設計一致
- 檢查所有謎團都有記錄在案的「真正答案」

依 verdict 處理：**APPROVE** → Phase 5。**CONCERNS** → 秀出列出的不一致處，並透過 `AskUserQuestion` 問要修改（重新 spawn 負責各項的 agent）還是接受。**REJECT** → 不要開始 Phase 5；矛盾要先修掉。**NOT ASSESSED [missing input]** → 指出缺的輸入，然後補上輸入再重跑這個 gate，或是把 `ND-CONSISTENCY: NOT ASSESSED — [input]` 帶進報告的一致性審查結果；絕對不能把它當成 APPROVE 來讀（`.claude/docs/director-gates.md`）。

**在 `team.size: individual` 下**，narrative-director 不在啟用名單內，所以不會 spawn 這個 gate。改由 writer 依同樣的標準檢查草稿，而且輸出要直接講明：「ND-CONSISTENCY not run — narrative-director is not
active at `team.size: individual`; consistency self-checked by writer.」自我檢查不是 gate 的 verdict，報告絕對不能把它當成 verdict 呈現。

### Phase 5: Polish (parallel)
平行委派：每個 `Agent` 呼叫都要發出去，才去等任何結果：
- **writer**：最後的自我審查：確認沒有任何一句超過對話框的限制、所有文字都用字串 key（不是原始字串）、佔位變數名稱一致
- **localization-lead**：驗證 i18n 合規性：檢查字串 key 的命名慣例、標出任何寫死格式、翻譯後會壞掉的字串、確認會變長的語言（德文／芬蘭文通常多 30%）有足夠的字元上限餘裕、確認文字中沒有需要地區專屬版本的文化假設
- **world-builder**：為所有新的背景設定條目定案 canon 等級

### Write the finals
所有草稿都在你手上。把上面表格裡的最終文件列出來，然後透過 `AskUserQuestion` 一次問清楚：「May I write these [N] narrative documents to
`design/narrative/`?」核准後再寫。`production/narrative/[content-slug]/` 底下的草稿保留下來當作工作紀錄。

## Error Recovery Protocol

**先驗證產物。** 如果回傳約定指定了路徑，在把這個 phase 當成做完之前，先確認該路徑真的存在：**指名的產物不在磁碟上，就是失敗的 phase，不管回覆讀起來多流暢。** agent 可能耗掉整個 phase，回你一段看似合理的開場白，卻什麼都沒寫；這既不是 BLOCKED、也不是錯誤、也不是「無法完成」，所以下面的觸發條件永遠不會被觸發。要叫它繼續，並指明沒達成的約定；context 通常還在。

如果任何 spawn 出去的 agent 回傳 BLOCKED、出錯或無法完成：**立刻揭露，不要越過它所阻擋的依賴項繼續往下走，而且一定要產出部分報告。** 被略過的 agent 那一節要留成一個有名字的缺口，絕對不准用你自己的內容填進去。完整流程：`.claude/docs/error-recovery-protocol.md`。

常見的阻擋原因：
- 輸入檔案缺失（找不到 story、GDD 不存在）→ 導向建立它的 skill
- ADR 狀態是 Proposed → 不要實作；決定之後，用 `/architecture-decision accept ADR-NNNN` 接受它
- 範圍太大 → 用 `/create-stories` 拆成兩個 story
- ADR 和 story 的指示互相衝突 → 把衝突揭露出來，不要猜

## File Write Protocol

Sub-agent 把它們的草稿寫到你指定的 `production/narrative/[content-slug]/` 路徑，依據的是上面「為什麼這不違反 Collaboration Protocol」所記載的**有界例外**：路徑是你指定的、產物是 `production/`、`docs/` 或 `tests/` 底下的新檔案、而且這個 phase 有 `AskUserQuestion` 把關。在這些範圍內，sub-agent **不會**每次寫入都問；範圍之外就一定要問。**唯一的例外是 `design/narrative/` 底下的最終文件**：所有草稿都在你手上，所以你在「Write the finals」那一次「May I write …?」之後，自己去寫。

## Output

一份摘要報告，涵蓋：敘事 brief 的狀態、建立／更新的背景設定條目、寫了多少對白、關卡敘事的整合點、一致性審查結果，以及任何未解決的矛盾，包括使用者選擇不修的在地化問題，要以字串 key 逐一列出。

Verdict: **COMPLETE** — narrative content delivered.

如果 ND-CONSISTENCY 回答 NOT ASSESSED、而且這件事已帶進報告（Phase 4），verdict 要講明，絕對不能只寫一個 COMPLETE：

Verdict: **COMPLETE — consistency NOT ASSESSED ([input])** — narrative content delivered; the consistency review could not run for want of [input].

如果 pipeline 因為有依賴項沒解決而停下來（例如使用者沒解決的背景設定矛盾或缺漏的前置條件）：

Verdict: **BLOCKED** — [reason]

## Next Steps

- 對敘事文件跑 `/design-review` 做一致性驗證。
- 對白定案之後，跑 `/localize extract` 把新字串抽出來交給翻譯。
- 跑 `/dev-story` 在引擎內實作對白觸發點和敘事事件。
