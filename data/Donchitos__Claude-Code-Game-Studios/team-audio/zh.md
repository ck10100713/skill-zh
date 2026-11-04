---
name: team-audio
description: "統籌音訊團隊（audio-director、sound-designer、technical-artist、gameplay-programmer），從音訊方向一路帶到實作。"
argument-hint: "[feature or area to design audio for] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, TaskCreate, TaskGet, TaskList, TaskUpdate, Bash(bash "*/.claude/skills/team-audio/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

# Team Audio

如果沒有帶參數，就輸出使用說明並結束，不要 spawn 任何 agent：
> 用法：`/team-audio [feature or area to design audio for] [--review full|lean|solo]` — 指定要設計音訊的功能或區域（例如 `combat`、`main menu`、`forest biome`、`boss encounter`）。這裡不要用 `AskUserQuestion`，直接輸出說明。

帶了參數時，就用結構化的 pipeline 來統籌音訊團隊。

**決策點：** 每個步驟轉換時，用 `AskUserQuestion` 把 subagent 的提案做成可選項目給使用者選。先在對話中寫出 agent 的完整分析，再用簡短的標籤收下決定。
在 `collaborative` 模式下，使用者核准後才能進下一步。
在 `guided` 模式下，pipeline 會自動往下走，除非某個步驟 BLOCKED；
在 `autonomous` 模式下會從頭跑到尾，每個步驟的結果用 `log_decision` 記錄下來。
屬於 `automation_always_ask` 類別的決策（`is_always_ask_category` helper）不管什麼模式一律要問。參見 `.claude/docs/automation-modes.md`。

## Phase 0: Resolve Config

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,team.size`

上面已經解析好了，直接用；`--review` 會覆蓋 `review_mode`。沒有這個區塊的話，就用 `.claude/docs/config-resolution.md` 裡的預設值。

`review_mode` 決定 director gate 的深度，而這條 pipeline 沒有 director gate：
下面任何 phase 在任何 `review_mode` 下，都不會 spawn CD-、TD-、PR- 或 AD-PHASE-GATE。它的 phase gate 就是 pipeline 自己的決策點（定義在下面的 `team.size` 底下），在這些點上工作的 agent 是團隊成員，不是 director gate。

`automation` 決定上面「決策點」那段的行為。各模式如何改變 pipeline 的行為，見上面的決策點說明和 `.claude/docs/automation-modes.md`。

**`team.size`**：哪些 agent 啟用（跟 review_mode 的 gate 深度和 workflow docs 互相獨立）。
- **`individual`**（預設）：只有 `sound-designer`。其他 agent 透過 sound-designer 諮詢，不會另外 spawn。
- **`small`**：加上 `audio-director` + `technical-artist` + `gameplay-programmer`。
- **`studio`**：再加上 `accessibility-specialist` + 主要的 engine specialist（也就是文件中寫的完整 pipeline）。
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

1. **讀取參數**，取得目標功能或區域（例如 `combat`、`main menu`、`forest biome`、`boss encounter`）。

2. **蒐集 context**：
   - 讀 `design/gdd/` 裡跟這個功能相關的設計文件，要分段讀：先用 Grep 工具（pattern `^#`，content mode）找出需要的標題，再用 offset 和 limit 讀那些範圍
   - 如果 `design/audio/sound-bible.md` 存在，就讀它。如果只有 `design/gdd/sound-bible.md`（舊版本放的位置），就讀那份，並建議搬到 `design/audio/`，因為放在 `design/gdd/` 的話，GDD 檢查會把每個檔案都當成系統 GDD 來算。如果兩個都沒有，
     就用一行講出來：「No sound bible at `design/audio/sound-bible.md`; audio
     direction starts from the GDDs alone」，讓這個缺口在輸出裡看得到。
     把這個缺口帶下去：在給 audio-director 的 Step 1 brief 裡講明，並在 Next Steps 裡建議建立 sound bible。
   - 讀 `assets/audio/` 裡現有的音訊資產清單
   - 讀這個區域現有的任何 sound design 文件

## How to Delegate

用 `Agent` 工具把每個團隊成員 spawn 成 subagent：
- `subagent_type: audio-director` — 聲音識別、情緒基調、音訊調色盤
- `subagent_type: sound-designer` — SFX 規格、音訊事件、混音群組
- `subagent_type: accessibility-specialist` — 關鍵音訊的視覺備援與字幕、聽覺敏感
- `subagent_type: technical-artist` — 音訊 middleware、bus 結構、記憶體預算
- `subagent_type: [primary engine specialist]` — 驗證該引擎的音訊整合模式
- `subagent_type: gameplay-programmer` — 音訊管理器、遊戲玩法觸發、自適應音樂

**給每個 agent 的 brief 要精簡，不要整包 context 倒過去。** 共用的輸入只讀**一次**，再把整理過的 brief 直接寫在 prompt 裡：只放每個 agent 真正需要的那幾行，你已經讀過的文件絕對不要只丟檔案路徑（agent 拿到路徑會把整份檔案重讀一遍）。只有你還沒讀、而且只有那個 agent 需要的文件，才給路徑。

**每個 agent 的 prompt 結尾都要加上回傳約定：**「Write your full output to `[path]` — that named path is your write authorisation under the bounded exception below, so write it without a separate approval prompt. Return **only** (1) the path written, (2) a ≤5-bullet summary of decisions, (3) any BLOCKED/CONCERNS items, one line each. Do not restate the documents you read.」沒有這個約定的話，agent 會把它讀過的東西全部倒回這個 session。**實作檔案是例外：** 寫程式或資產的 agent 要先回傳它打算建立或修改的檔案，而它的回傳約定要等你把整組檔案問過一次、使用者也答應之後才能指名這些檔案（File Write Protocol）。授權這些寫入的是那個答覆，不是有界例外。

**`[path]` 要換成真實路徑。** 工作中的產出放在
`production/audio/[feature]/` 底下，`[feature]` 是參數轉成的 slug：
全小寫、空格換成連字號（`boss encounter` → `boss-encounter`），跟「Save to」步驟用的是同一個 slug。每個 agent 一個檔案，這樣平行的步驟就不會共用同一個檔：

| Step / agent | Writes to |
|---|---|
| 1 audio-director | `production/audio/[feature]/direction.md` |
| 2 sound-designer | `production/audio/[feature]/sfx-spec.md` |
| 2 accessibility-specialist | `production/audio/[feature]/accessibility.md` |
| 3 technical-artist | `production/audio/[feature]/integration-plan.md` |
| 3 engine specialist | `production/audio/[feature]/engine-notes.md` |
| 4 gameplay-programmer | the code root and the engine's test root — the files the one implementation ask lists (File Write Protocol), outside the bounded exception |

這些是工作草稿；真正留存的紀錄，是你用它們彙整出來的音訊設計文件。

> **為什麼這不違反 Collaboration Protocol。** `CLAUDE.md` 要求 agent 在 Write/Edit 之前先問「May I write this to [filepath]?」。這裡 spawn 出來的 subagent **不問**就寫，這是刻意設計的有界例外，不是疏忽，跟 `consistency-check` 附加寫入 `active.md` 是同一個決定。這個例外只在三個條件**同時**成立時才有效：(1) 路徑是**你**在 prompt 裡指定的，所以使用者核准這個 phase 的時候，就等於核准了目的地；(2) 它是 `production/`、`docs/` 或 `tests/` 底下的新產物，絕對不是改既有的原始碼或設定；(3) 產生它的那個 phase，本身在 pipeline 往下走之前有 `AskUserQuestion` 把關。這三條以外，agent 一定要先問。**不要靠「每個 subagent 都問一次」來「修」這件事**：每個 agent 每個 phase 都跳一次提示，會讓 orchestrator 根本沒辦法用，這就是這個例外存在的原因。

3. **依序統籌音訊團隊**：

### Step 1: Audio Direction (audio-director)
Spawn `audio-director` agent 來：
- 定義這個功能／區域的聲音識別
- 指定情緒基調與音訊調色盤
- 設定音樂方向（自適應 layer、stem、轉場）
- 定義音訊優先順序與混音目標
- 建立所有自適應音訊規則（戰鬥強度、探索、緊張感）

### Step 2: Sound Design and Audio Accessibility (parallel)
Spawn `sound-designer` agent 來：
- 為每一個音訊事件寫出詳細的 SFX 規格
- 定義聲音類別（環境音、UI、遊戲玩法、音樂、對白）
- 指定每個聲音的參數（音量範圍、音高變化、衰減）
- 規劃含觸發條件的音訊事件清單
- 定義混音群組與 ducking 規則

同時平行 spawn `accessibility-specialist` agent 來：
- 找出哪些音訊事件帶有關鍵的遊戲資訊（受到傷害、附近有敵人、目標完成），需要為聽障玩家提供視覺替代方案
- 指定字幕需求：哪些音訊事件需要字幕、文字格式、畫面上停留多久
- 檢查沒有任何遊戲狀態只靠音訊傳達（每個都必須有視覺備援）
- 檢視音訊事件清單，找出可能讓聽覺敏感的玩家不舒服的項目（高頻警示音、突然的大聲事件）
- 輸出：整合進音訊事件規格的音訊無障礙需求清單

影響遊戲玩法的關鍵音訊事件，如果沒有視覺提示或字幕，在報告裡要標成
**BLOCKING**，不是參考建議。Step 3 要等使用者解決它，或在 Step 2 的決策點明確接受它之後才能開始；這個決策點會提供修法（視覺提示、字幕或觸覺備援）和一個「停止」選項；接受下來的缺口要列在摘要的待解問題裡。

### Step 3: Technical Implementation (parallel)
Spawn `technical-artist` agent 來：
- 設計音訊 middleware 的整合（Wwise/FMOD/原生）
- 定義音訊 bus 結構與路由
- 指定各平台的音訊資產記憶體預算
- 規劃 streaming 與預載資產的策略
- 設計任何跟音訊連動的視覺特效

同時平行 spawn **primary engine specialist**（`<engine>-specialist` 由 `engine.name` 推導：Godot→`godot-specialist`、Unity→`unity-specialist`、Unreal→`unreal-specialist`；找不到時，退回 `.claude/docs/technical-preferences.md` 裡 `## Engine Specialists` 的 Primary 那一行）來驗證整合做法：
- 提議的音訊 middleware 整合方式，對這個引擎來說算不算慣用做法？（例如 Godot 內建的 AudioStreamPlayer vs FMOD、Unity 的 Audio Mixer vs Wwise、Unreal 的 MetaSounds vs FMOD）
- 有沒有該採用的引擎專屬音訊 node／component 模式？
- 鎖定的引擎版本裡，有沒有已知的音訊系統變更會影響整合計畫？
- 輸出：要跟 technical-artist 的計畫合併的引擎音訊整合筆記

如果沒有設定引擎，就跳過 specialist 的 spawn。**在這次 run 的輸出裡記下 ``Engine validation: NOT ASSESSED — no engine configured (`engine.name` unset in `project.yaml`)``。** 被略過卻不吭聲的檢查，跟通過的檢查看起來一模一樣；讀的人沒辦法知道根本沒有徵詢過引擎方面的意見。

### Step 4: Code Integration (gameplay-programmer)
Spawn `gameplay-programmer` agent 來：
- 實作音訊管理系統，或檢視現有的
- 把音訊事件接到遊戲玩法觸發點
- 實作自適應音樂系統（如果有指定）
- 設定音訊遮蔽／殘響區域
- 為音訊事件觸發寫 unit test

4. **彙整音訊設計文件**，合併所有團隊成員的產出。

5. **儲存到** `design/audio/audio-[feature].md`，**但要先問。** `design/` 不在有界寫入例外涵蓋的三個目錄（`production/`、`docs/`、`tests/`）裡，所以拿到這個路徑的 sub-agent 一定得先問。不要靠放寬例外來解決。改用 `team-level` 用的同一個模式：**你**已經握有每個 sub-agent 的輸出，所以自己彙整文件，直接用 `AskUserQuestion` 問「May I write the
   audio design to `design/audio/audio-[feature].md`?」，核准後再寫。Sub-agent 的工作產物留在 `production/` 底下，例外可以涵蓋到那裡。

   注意：如果 `design/audio/` 不存在，寫檔時會一併建立。

6. **輸出摘要**，包含：音訊事件數量、預估資產數量、實作任務，以及團隊成員之間任何尚待解決的問題。

Verdict: **COMPLETE** — audio design document produced and team pipeline finished.

如果引擎驗證被略過（沒有設定引擎），verdict 要講明，絕對不能只寫一個 COMPLETE：

Verdict: **COMPLETE — engine validation NOT ASSESSED ([reason])** — audio design document produced; the engine specialist never reviewed the integration plan.

如果 pipeline 因為有依賴項沒解決而停下來（例如關鍵的無障礙缺口，或使用者沒解決的缺漏 GDD）：

Verdict: **BLOCKED** — [reason]

## File Write Protocol

每個 agent 的產出（SFX 規格、整合計畫）由產出它的 sub-agent 自己寫，依據的是上面「為什麼這不違反 Collaboration Protocol」所記載的**有界例外**：路徑是你指定的、產物是 `production/`、`docs/` 或 `tests/` 底下的新檔案、而且這個 phase 有 `AskUserQuestion` 把關。在這些範圍內，sub-agent **不會**每次寫入都問；範圍之外就一定要問。**實作檔案**（gameplay-programmer 的音訊整合程式碼，以及 code root 或 `assets/` 底下的任何東西）在這些範圍之外：agent 先回傳它打算建立或修改的檔案，你對整組檔案問一次，答應之後它才寫。**唯一的例外是最後彙整出來的音訊設計文件**：orchestrator 已經握有所有輸入，所以它自己彙整，並在自己的「May I write …?」提示之後，親自寫入 `design/audio/audio-[feature].md`（上面的「Save to」步驟）。

## Next Steps

- 實作開始前，先跟 audio-director 一起審這份音訊設計文件。
- 設計核准後，用 `/dev-story` 來實作音訊管理器和事件系統。
- 音訊資產建好之後，跑 `/asset-audit` 確認命名和格式合規。
- 如果之前沒有 sound bible，在下一輪音訊工作之前先建一份：請
  `audio-director` agent 根據 `.claude/docs/templates/sound-bible.md`，從這次 run 的 Step 1 方向出發，草擬 `design/audio/sound-bible.md`（寫到 `design/` 底下前它會先問）。

## Error Recovery Protocol

**先驗證產物。** 如果回傳約定指定了路徑，在把這個 phase 當成做完之前，先確認該路徑真的存在：**指名的產物不在磁碟上，就是失敗的 phase，不管回覆讀起來多流暢。** agent 可能耗掉整個 phase，回你一段看似合理的開場白，卻什麼都沒寫；這既不是 BLOCKED、也不是錯誤、也不是「無法完成」，所以下面的觸發條件永遠不會被觸發。要叫它繼續，並指明沒達成的約定；context 通常還在。

如果任何 spawn 出去的 agent 回傳 BLOCKED、出錯或無法完成：**立刻揭露，不要越過它所阻擋的依賴項繼續往下走，而且一定要產出部分報告。** 被略過的 agent 那一節要留成一個有名字的缺口，絕對不准用你自己的內容填進去。完整流程：`.claude/docs/error-recovery-protocol.md`。

常見的阻擋原因：
- 輸入檔案缺失（找不到 story、GDD 不存在）→ 導向建立它的 skill
- ADR 狀態是 Proposed → 不要實作；決定之後，用 `/architecture-decision accept ADR-NNNN` 接受它
- 範圍太大 → 用 `/create-stories` 拆成兩個 story
- ADR 和 story 的指示互相衝突 → 把衝突揭露出來，不要猜
