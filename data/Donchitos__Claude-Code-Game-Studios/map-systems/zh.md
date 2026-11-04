---
name: map-systems
description: "把一個概念拆解成各個獨立的系統、梳理相依關係、排定設計順序，並建立系統索引。"
argument-hint: "[next | system-name] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, TaskCreate, TaskGet, TaskList, TaskUpdate, Agent, Bash(bash "*/.claude/skills/map-systems/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,workflow,docs.density,project.stage`

上面已經解析好了，直接用；`--review` 會覆蓋 `review_mode`。沒有這個區塊的話，
用 `.claude/docs/config-resolution.md` 裡的預設值。

# Map Systems


叫用這個 skill 時：

## Parse Arguments

兩種模式：

- **沒有參數**：`/map-systems` — 跑完整的拆解流程（Phase 1-5），
  建立或更新系統索引。
- **`next`**：`/map-systems next` — 從索引裡挑出優先順序最高、還沒設計的系統，
  交給 `/design-system`（Phase 6）。


完整的檢查模式見 `.claude/docs/director-gates.md`。各個 gate 的定義放在 `.claude/docs/director-gates/[gate-id].md` — 被派出的 agent 會自己讀它的 gate 檔；不要在父 session 裡讀。


每一次 `AskUserQuestion` 呼叫都遵循 `.claude/docs/automation-modes.md`
（collaborative 一律問 · guided 只問重大的 · autonomous 只記錄然後繼續；
`automation_always_ask` 的類別一律要問）。在 collaborative 模式下，
系統清單、相依關係、優先順序和寫入核准是各自獨立的問題：
每一個都要等到有答案，才能進下一步。

**`docs.density`** — 它控制每個章節的*深度*，而 `workflow`
控制有哪些章節。`modes.rigor` 會兩個一起設；想只調整深度，就明確設定
`docs.density`：`terse`（預設，透過 `rigor: minimal`）= 每個系統一行描述；
`balanced` = 每個系統一小段文字 + 相依備註（`rigor: standard`）；
`thorough` = 完整的逐系統理由 + 關係分析。套用到
你撰寫的每個章節。

> **每個系統的敘述文字要放哪裡。** `templates/systems-index.md` 的 Systems
> Enumeration 是固定欄位的表格，沒有描述欄，所以在
> `balanced` 和 `thorough`，敘述文字要放在 `## Overview` 裡 — `balanced` 每個系統一小段，
> `thorough` 再加上關係分析 —
> 以及 `## Dependency Map` 的 layer 備註裡。**不要替 enumeration 表格加欄位**
> — 它是 `.claude/docs/templates/systems-index.md` 裡的固定契約，
> 而它的使用端（`/design-system` §6 和 §7、`/create-epics`）都是針對
> 它定義的欄位寫的。加寬它是 schema 變更，不是排版選擇。
>
> **使用端實際上怎麼讀它。** 沒有任何東西是依位置解析這張表的。
> 提到 `systems-index.md` 的兩支 script
> （`gdd-structure-check.sh:51`、`review-scope.sh:40`）是在 `case` 陳述式裡**依檔名**比對，
> 完全不解析任何欄位；兩個 skill 則是依**欄位名稱 `Category`** 取值
> （`design-system:229`、`:780`）。所以 `Category` 是
> 絕對不能改名或拿掉的欄位，而這張表維持固定契約，是因為每個使用端
> 都是針對範本定義的那組欄位寫的。
> 在 `terse`，這張表加上一段話的 `## Overview` 就是全部輸出。

**`workflow`**（見 `.claude/docs/workflow-modes.md`）：
- `full` / `standard` — 在 `/design-system` 之前是必要的（要先梳理好系統，
  才能撰寫各系統的 GDD）。
- `minimal` — 不必要（game brief 取代了系統索引）。
  還是可以自願執行。

---

## Phase 1: Read Concept (Required Context)

讀遊戲概念和任何既有的設計工作。這提供了系統拆解的原始素材。
每份文件都依章節讀：用 Grep 工具（pattern `^#`，content mode）找出你需要的標題，
再用 offset 和 limit 讀那幾段範圍。

**必要：**
- 讀 `design/gdd/game-concept.md`（在 `minimal`，改讀 `design/game-brief.md`）
  — **兩個都找不到的話，要用清楚的訊息失敗**：
  > "No game concept found. Run `/brainstorm` first to create one, then come back
  > to decompose it into systems."

**選用（存在就讀）：**
- 讀 `design/gdd/game-pillars.md` — pillar 會限制優先順序和範圍
- 讀 `design/gdd/systems-index.md` — 如果存在，就**從上次中斷的地方繼續**
  （更新它，不要從頭重建）
- 用 Glob 找 `design/gdd/*.md` — 檢查哪些系統的 GDD 已經存在

**如果系統索引已經存在：**
- 讀它，並把目前的狀態呈現給使用者
- 用 `AskUserQuestion` 問：
  "The systems index already exists with [N] systems ([M] designed, [K] not started).
  What would you like to do?"
  - Options："Update the index with new systems"、"Design the next undesigned system"、
    "Review and revise priorities"

---

## Phase 2: Systems Enumeration (Collaborative)

擷取並找出遊戲需要的所有系統。這是這個 skill 創意的核心 —
它需要人的判斷，因為概念文件很少把每個系統都明確列出來。

### Step 2a: Extract Explicit Systems

掃描遊戲概念，找直接提到的系統和機制：
- Core Mechanics 章節（最明確）
- Core Loop 章節（暗示每一層迴圈由哪些系統驅動）
- Technical Considerations 章節（網路、程序化生成等）
- MVP Definition 章節（必要功能 = 必要系統）

### Step 2b: Identify Implicit Systems

對每個明確的系統，找出它暗示的**隱藏系統**。遊戲永遠需要
比概念文件提到的更多系統。用這個推論模式：

- 「Inventory」暗示：道具資料庫、裝備欄位、重量/容量規則、
  背包 UI、存讀檔用的道具序列化
- 「Combat」暗示：傷害計算、生命值系統、命中判定、狀態效果、
  敵人 AI、戰鬥 UI（血條、傷害數字）、死亡/重生
- 「Open world」暗示：串流/分塊、LOD 系統、快速移動、地圖/小地圖、
  興趣點追蹤、世界狀態持久化
- 「Multiplayer」暗示：網路層、大廳/配對、狀態同步、
  防作弊、網路 UI（ping、玩家清單）
- 「Crafting」暗示：配方資料庫、素材採集、製作 UI、
  成功/失敗機制、配方探索/學習
- 「Dialogue」暗示：對話樹系統、對話 UI、選擇追蹤、NPC
  狀態管理、在地化掛鉤
- 「Progression」暗示：XP 系統、升級機制、技能樹、解鎖
  追蹤、成長 UI、成長存檔資料

要在對話文字裡說明為什麼需要每個隱含的系統（附範例）。

### Step 2c: User Review

依類別整理並呈現這份清單。對每個系統，顯示：
- 名稱
- 類別
- 簡短描述（1 句話）
- 它是明確的（來自概念）還是隱含的（推論出來的）

然後用 `AskUserQuestion` 取得回饋：
- "Are there systems missing from this list?"
- "Should any of these be combined or split?"
- "Are there systems listed that this game does NOT need?"

**在 `collaborative`** — 反覆進行，直到使用者核准這份清單。
**在 `guided`** — 問一次，套用答案，然後繼續；不要重複詢問。
**在 `autonomous`** — 不要問。透過 `log_decision` 記錄這份清單和它推論出來的系統，
然後繼續。

---

## Phase 3: Dependency Mapping (Collaborative)

對每個系統，判斷它依賴什麼。如果一個系統
沒有另一個系統先存在就無法運作，就叫它「依賴」那個系統。

### Step 3a: Map Dependencies

對每個系統，列出它的相依項目。用這些相依性的啟發式：
- **輸入/輸出相依**：系統 A 產生系統 B 需要的資料
- **結構相依**：系統 A 提供系統 B 掛上去的框架
- **UI 相依**：每個遊戲玩法系統都有一個對應的 UI 系統
  依賴它（但 UI 是在玩法系統之後設計的）

### Step 3b: Sort by Dependency Order

把系統排成幾個層：
1. **Foundation**：零相依的系統（最先設計和建置）
2. **Core**：只依賴 Foundation 系統的系統
3. **Feature**：依賴 Core 系統的系統
4. **Presentation**：包裹遊戲玩法系統的 UI 和回饋系統
5. **Polish**：元系統、教學、分析、無障礙

### Step 3c: Detect Circular Dependencies

檢查相依圖裡有沒有循環。如果找到：
- 向使用者標示出來
- 提出解法（介面抽象、同時設計、
  在兩個系統之間定義契約來打破循環）

### Step 3d: Present to User

把相依地圖呈現成分層清單。標示：
- 任何循環相依
- 任何「瓶頸」系統（很多其他系統依賴它們 — 風險高）
- 任何沒有被依賴的系統（葉節點 — 風險較低，可以晚點設計）

用 `AskUserQuestion` 問：「Does this dependency ordering look right? Any
dependencies I'm missing or that should be removed?」

**Review mode 檢查** — 在派出 TD-SYSTEM-BOUNDARY 之前套用：
- `solo` → 跳過。註明：「TD-SYSTEM-BOUNDARY skipped — Solo mode.」進入優先順序分配。
- `lean` → 跳過（它不是 PHASE-GATE）。註明：「TD-SYSTEM-BOUNDARY skipped — Lean mode.」進入優先順序分配。
- `full` → 照常派出。

**相依地圖核准之後，在進入優先順序分配之前，用 `Agent` 派出 `technical-director`，使用 gate TD-SYSTEM-BOUNDARY（`.claude/docs/director-gates/td-system-boundary.md`）。**

傳入：相依圖（每個系統 → 它依賴什麼）、layer 分配、瓶頸系統，以及任何循環相依和它們提議的解法。

呈現評估結果。如果是 REJECT，就跟使用者一起修訂系統邊界，顯示修訂後的相依地圖，然後才進入優先順序分配。如果是 CONCERNS，就在系統索引裡以行內方式註明，然後繼續。如果是 NOT ASSESSED [missing input]，它就不是 APPROVE：點名缺了什麼，然後補上並重跑 gate，或繼續並在索引草稿裡註明 `TD-SYSTEM-BOUNDARY: NOT ASSESSED — [input]`。

---

## Phase 4: Priority Assignment (Collaborative)

依每個系統是哪個 milestone 需要的，把它分配到一個優先順序 tier。

### Step 4a: Auto-Assign Based on Concept

用這些啟發式做初步分配：
- **MVP**：概念的「Required for MVP」章節提到的系統，加上它們的
  Foundation 層相依項目
- **Vertical Slice**：在某一個區域做出完整體驗所需的系統
- **Alpha**：所有剩下的遊戲玩法系統
- **Full Vision**：Polish、元系統和錦上添花的系統

### Step 4b: User Review

用表格呈現優先順序的分配。對每個 tier，說明為什麼把這些系統
放在那裡。

用 `AskUserQuestion` 問：「Do these priority assignments match your vision?
Which systems should be higher or lower priority?」

在對話裡解釋理由：「I placed [system] in MVP because the core loop
requires it — without [system], the 30-second loop can't function.」

**理由要怎麼措辭** — 這規範的是你*說*什麼，不是你要寫進去的欄位。
兩張表都沒有 `Why` 欄：Systems Enumeration 是
`# / Name / Category / Priority / Status / Design Doc / Depends On`，
Recommended Design Order 是 `Order / System / Priority / Layer / Agent(s) /
Est. Effort`。理由放在上面的對話裡，而任何
使用者在 session 結束後還應該看到的內容，就放在索引的 `## Overview`
段落。不要替它發明一個欄位。

把技術必要性和玩家體驗的理由混在一起說。純技術的
理由 — 「the damage system needs damage math」— 在系統直接
影響玩家感受時，單獨講是不夠的。好的理由兩者都會點出，並引用
它服務的 pillar：
- "Required for the core loop — without it the player's main choice has no
  consequence (Pillar [N]: [pillar name])"
- "This is where [system]'s identity is established — the stat definitions here
  are what make it feel different from [the sibling system]"
- "Foundation for every later economy decision — the player must understand
  costs before any of the choices built on top of it mean anything"

> **方括號要用*這個*專案的內容填。** 方括號裡的空格不是
> 裝飾。從別的遊戲範例照抄來的理由，帶的是那款遊戲的詞彙，不是
> 這款的。

**Review mode 檢查** — 在派出 PR-SCOPE 之前套用：
- `solo` → 跳過。註明：「PR-SCOPE skipped — Solo mode.」進入 Step 4c。
- `lean` → 跳過（它不是 PHASE-GATE）。註明：「PR-SCOPE skipped — Lean mode.」進入 Step 4c。
- `full` → 照常派出。

**優先順序核准之後，在寫索引之前，用 `Agent` 派出 `producer`，使用 gate PR-SCOPE（`.claude/docs/director-gates/pr-scope.md`）。**

從索引傳入 gate 要的欄位：完整願景的範圍（索引裡的每個系統）、MVP 定義（MVP tier 的系統）、範圍 tier（每個 milestone tier 的系統數量，附估計的實作量 — 系統數 × 平均複雜度）、把專案宣告的時程當成時程估計，還有團隊規模。

呈現評估結果。PR-SCOPE 的回答是 REALISTIC / OPTIMISTIC / UNREALISTIC。
如果是 UNREALISTIC，提議在寫索引之前修訂優先順序 tier 的分配。如果是 OPTIMISTIC，顯示 producer 建議的調整，並問要不要
在寫入前套用到 tier 上；如果使用者拒絕，就記下來然後
繼續。如果是 NOT ASSESSED [missing input] — 通常是團隊規模或時程 — 它
就不是 REALISTIC：點名缺了什麼，然後補上並重跑 gate，或
繼續並在索引草稿裡註明 `PR-SCOPE: NOT ASSESSED — [input]`。

### Step 4c: Determine Design Order

把相依排序 + 優先順序 tier 結合，產生最終的設計順序：
1. 先 MVP Foundation 系統
2. 再 MVP Core 系統
3. 第三是 MVP Feature 系統
4. Vertical Slice Foundation/Core 系統
5. ……依此類推

這就是團隊應該寫 GDD 的順序。

---

## Phase 5: Create Systems Index (Write)

### Step 5a: Draft the Document

用 `.claude/docs/templates/systems-index.md` 的範本，把 Phase 2-4 的所有資料
填進系統索引：
- 填 enumeration 表格
- 填相依地圖
- 填建議的設計順序
- 填高風險系統
- 填進度追蹤表（所有系統一開始都是 "Not Started"，除非 GDD 已經存在）

### Step 5b: Approval

呈現文件的摘要：
- 依類別的系統總數
- MVP 系統數
- 設計順序的前 3 個系統
- 任何高風險項目

**在 `automation: collaborative`** — 問：「May I write the systems index to
`design/gdd/systems-index.md`?」等待核准。只有在
「yes」之後才寫檔。

**在 `automation: guided`** — **新的**索引要問同樣的「May I write …?」
問題，因為 `.claude/docs/automation-modes.md` 規定 `guided` 對新檔案要問「May I
write?」。索引已經存在的話，就呈現上面的摘要、
點名目的地（`design/gdd/systems-index.md`），然後不用等明確的「yes」就寫入更新。
事後要說明你寫了什麼。

**Review mode 檢查** — 在派出 CD-SYSTEMS 之前套用：
- `solo` → 跳過。註明：「CD-SYSTEMS skipped — Solo mode.」進入 Step 5c。
- `lean` → 跳過（它不是 PHASE-GATE）。註明：「CD-SYSTEMS skipped — Lean mode.」進入 Step 5c。
- `full` → 照常派出。

**系統索引寫好之後，用 `Agent` 派出 `creative-director`，使用 gate CD-SYSTEMS（`.claude/docs/director-gates/cd-systems.md`）。**

傳入：系統索引的路徑；遊戲 pillar 和核心幻想 — 來自 `design/gdd/game-concept.md`，或在 `minimal` 時取 `design/game-brief.md` 的 pitch 和「what they feel」那行（它沒有 pillar）；每個 tier（MVP / Vertical Slice / Alpha / Full Vision）的優先順序分配；還有相依地圖裡的高風險和瓶頸系統。

呈現評估結果。如果是 REJECT，在開始撰寫 GDD 之前，先跟使用者一起修訂系統集合。如果是 CONCERNS，顯示它們，並用 `AskUserQuestion`：`Revise the system set` / `Accept — record them in the index` / `Discuss further`。選 *Revise*，就跟使用者一起重做受影響的系統，並在重寫索引之前再問一次。選 *Accept* — 這個選項本身就點名了這個編輯，所以選它就等於已經問過了 — 就把它們記在系統索引裡，寫成一則 `> **Creative Director Note**`，
放在 **`## Priority Tiers` 表格的正下方**，並點名每個疑慮適用的 tier — 例如 `> **Creative Director Note** (MVP): …`。
`templates/systems-index.md` 有的是 Priority Tiers 的*定義表*，不是每個 tier 一個
章節，所以沒有「tier 章節的最上面」可以寫 — 不要
叫寫的人去那裡。如果是 NOT ASSESSED [missing input]，它就不是 APPROVE
（`.claude/docs/director-gates.md`）：點名缺了什麼，然後補上並
重跑 gate，或先問過，再在同一個位置記下 `> **Creative Director Note**:
CD-SYSTEMS NOT ASSESSED — [input]`。

### Step 5c: Update Session State

寫完之後，如果 `production/session-state/active.md` 不存在就建立它，然後用下列內容更新：
- Task: Systems decomposition
- Status: Systems index created
- File: design/gdd/systems-index.md
- Next: Design individual system GDDs

**Verdict: COMPLETE** — systems index written to `design/gdd/systems-index.md`.
如果使用者拒絕：**Verdict: BLOCKED** — user did not approve the write.

---

## Phase 6: Design Individual Systems (Handoff to /design-system)

在下列情況會進入這個階段：
- 使用者在建立索引之後，對設計系統說「yes」
- 使用者叫用 `/map-systems [system-name]`
- 使用者叫用 `/map-systems next`

### Step 6a: Select the System

- 如果有提供系統名稱，就在系統索引裡找它
- 如果用了 `next`，就挑優先順序最高、還沒設計的系統（依設計順序）
- 如果使用者剛做完索引，問：
  "Would you like to start designing individual systems now? The first system in
  the design order is [name]. Or would you prefer to stop here and come back later?"

用 `AskUserQuestion` 問：「Start designing [system-name] now, pick a different
system, or stop here?」

### Step 6b: Hand Off to /design-system

選好系統之後，叫用 `/design-system [system-name]` skill。

`/design-system` skill 處理完整的 GDD 撰寫流程：
- 從遊戲概念、系統索引和相依的 GDD 蒐集脈絡
- 立刻建立檔案骨架
- 一次一個地走完所有 8 個必要章節（協作式、漸進式）
- 交叉參照既有文件，避免互相矛盾
- 轉給專業 agent 取得領域專業知識
- 每個章節一核准就立刻寫進檔案
- 完成時跑 `/design-review`
- 更新系統索引

**不要在這裡重複 /design-system 的流程。** 這個 skill 負責系統
*索引*；`/design-system` 負責個別系統的 *GDD*。

### Step 6c: Loop or Stop

`/design-system` 完成之後，用 `AskUserQuestion`：
- "Continue to the next system ([next system name])?"
- "Pick a different system?"
- "Stop here for this session?"

如果繼續，回到 Step 6a。

---

## Phase 7: Suggest Next Steps

系統索引建立之後（或設計了一些系統之後），用 `AskUserQuestion` 呈現下一步動作：

- "Systems index is written. What would you like to do next?"
  - [A] Start designing GDDs — run `/design-system [first-system-in-order]`
  - [B] Run `/gate-check systems-design` — the Concept → Systems Design gate; offer this only while `project.stage` is still Concept
  - [C] Run `/gate-check technical-setup` — the Systems Design → Technical Setup gate, once the MVP systems have GDDs
  - [D] Stop here for this session

**gate-check 選項（[C]）值得知道**：`/gate-check technical-setup` 會檢查 Systems Design 階段的必備產出物是否存在，並在你投入架構之前執行 phase-gate 的 director。CD-SYSTEMS 和 TD-SYSTEM-BOUNDARY 是這個 skill 自己的 gate — 它們在 `full` review 模式下在這裡執行，不是在 `/gate-check` 裡。

任何單一 GDD 完成之後：
- "Run `/design-review design/gdd/[system].md` in a fresh session to validate quality"
- "Run `/gate-check technical-setup` when all MVP GDDs are complete"

---

## Collaborative Protocol

**適用於 `collaborative` 模式（預設）。** `guided` 和
`autonomous` 模式請見 `.claude/docs/automation-modes.md` — 下面的規則
描述的是 collaborative 模式的要求，不是通用行為。

這個 skill 在每個階段都遵循協作式設計原則：

1. 每一步都是 **Question -> Options -> Decision -> Draft -> Approval**
2. 每個決策點都用 **AskUserQuestion**（Explain -> Capture 模式）：
   - Phase 2: "Missing systems? Combine or split?"
   - Phase 3: "Dependency ordering correct?"
   - Phase 4: "Priority assignments match your vision?"
   - Phase 5: "May I write the systems index?"
   - Phase 6: "Start designing, pick different, or stop?" 然後交給 `/design-system`
3. 每次寫檔之前都要問 **"May I write to [filepath]?"**
4. **漸進式寫入**：每設計完一個系統就更新系統索引
5. **交接**：個別 GDD 的撰寫由 `/design-system` 負責，它處理
   漸進式章節寫入、交叉參照、設計審查和索引更新
6. **Session state 更新**：每個里程碑之後（索引建立、系統設計完成、優先順序變更）
   都寫入 `production/session-state/active.md`

**絕對不要**自動產生完整的系統清單然後不經審查就寫入。
**絕對不要**在使用者沒確認的情況下開始設計系統。
**一律**把 enumeration、相依關係和優先順序秀給使用者驗證。

## Context Window Awareness

如果 context 在任何時候達到或超過 70%，就附上這則通知：

> **Context is approaching the limit (≥70%).** The systems index is saved to
> `design/gdd/systems-index.md`. Open a fresh Claude Code session to continue
> designing individual GDDs — run `/map-systems next` to pick up where you left off.

---

## Recommended Next Steps

- 執行 `/design-system [first-system-in-order]` 來撰寫第一份 GDD（用索引裡的設計順序）
- 執行 `/map-systems next`，永遠自動挑出優先順序最高、還沒設計的系統
- 每寫完一份 GDD，就在全新的 session 裡執行 `/design-review design/gdd/[system].md`
- 所有 MVP GDD 都寫完並審查過之後，執行 `/gate-check technical-setup`
