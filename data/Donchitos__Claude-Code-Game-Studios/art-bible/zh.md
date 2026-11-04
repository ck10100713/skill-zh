---
name: art-bible
description: "撰寫 Art Bible（美術聖經），也就是為素材製作把關的視覺識別規範。要在 /map-systems 之前跑。"
argument-hint: "[--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, Bash(bash "*/.claude/skills/art-bible/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,workflow,docs.density`

上面已經解析好了，直接用；`--review` 會覆蓋 `review_mode`。沒有這個區塊的話，
用 `.claude/docs/config-resolution.md` 裡的預設值。

# Art Bible


## Phase 0: 解析參數與檢查 Context


完整的檢查流程見 `.claude/docs/director-gates.md`。各個 gate 的定義放在 `.claude/docs/director-gates/[gate-id].md`，被 spawn 出來的 agent 會自己讀自己的 gate 檔，不要在 parent session 裡讀。


每一次 `AskUserQuestion` 呼叫都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律詢問 · guided 只問重大事項 · autonomous 記錄後直接往下走；
屬於 `automation_always_ask` 的類別一律要問）。

**`docs.density`**：控制每個章節的*深度*，`workflow`
則控制有哪些章節。`modes.rigor` 會同時設定兩者；要只調整深度的話，
就明確設定 `docs.density`：`terse`（預設，來自 `rigor: minimal`）= 每個章節是一份條列的
限制條件加參考資料；`balanced` = 用段落解釋每個視覺選擇
（`rigor: standard`）；`thorough` = 完整散文，包含風格探索、參考資料，
以及每個選擇的理由。你寫的每個章節都要套用這個設定。

**`workflow`**（見 `.claude/docs/workflow-modes.md`）：
- `full`：9 個 art bible 章節全部必寫。
- `standard`：只有專案裡有視覺素材的 story 時才需要；
  需要的話最少寫第 1–4 章。`workflow_overrides.art_bible_strict:
  true` 會不管 tier，強制要求全部 9 章。
- `minimal`：不需要。仍然可以自願執行。

讀 `design/gdd/game-concept.md`，或是 `design/game-brief.md`（在 `rigor: minimal` 時取代它的
一頁式 brief）。要按章節讀：用 Grep 工具（pattern `^#`、content mode）找出你要的標題，
再用 offset 和 limit 讀那幾段範圍。兩份都不存在的話，直接失敗並顯示：
> "No game concept found. Run `/brainstorm` first — the art bible is authored after the game concept is approved."

從 game-concept.md 擷取（如果是 brief：working title、pitch、「Who it's for /
what they feel」那行，還有「Art & audio direction」那行，它沒有 pillars、Visual
Identity Anchor 或平台）：
- 遊戲名稱（working title）
- 核心幻想（core fantasy）與電梯簡報（elevator pitch）
- 遊戲 pillars（全部）
- **Visual Identity Anchor** 章節（如果有的話，來自 brainstorm Phase 4 art-director 的產出）
- 目標平台（如果有註明）

**Retrofit 模式偵測**：Glob `design/art/art-bible.md`。如果檔案存在，
就**不要讀整份文件**直接建立狀態表，因為你只要寫*還沒完成*的章節，
把完成的章節載進來，載的正好是你不會碰的東西：

```
Grep pattern="^## " path="design/art/art-bible.md" output_mode="content" -n
Grep pattern="\[To be designed\]|\[TBD\]|\[To be written\]|^_?TODO" path="design/art/art-bible.md" output_mode="content" -n
```

- 第一個 grep 給你章節標題和行號，相鄰兩個標題之間的距離就是該章節的大小。
- 第二個 grep 給你 placeholder 標記和它們落在哪。
- 章節如果跟下一個標題之間有實質距離、而且裡面沒有 placeholder 標記，就是 **Complete**；
  有標記落在它的範圍內，就是 **Placeholder**；
  連續兩個標題緊貼著，就是 **Empty**。
- 兩個 grep 對某個章節還是真的判斷不出來時，用 `Read(offset, limit)` 讀*那個章節*
  的行範圍，絕對不要讀整份檔案。
- 建立章節狀態表：

```
Section | Status
--------|--------
1. Visual Identity Statement | [Complete / Empty / Placeholder]
2. Mood & Atmosphere | ...
3. Shape Language | ...
4. Color System | ...
5. Character Design Direction | ...
6. Environment Design Language | ...
7. UI/HUD Visual Direction | ...
8. Asset Standards | ...
9. Reference Direction | ...
```

- 把這張表給使用者看：
  > "Found existing art bible at `design/art/art-bible.md`. [N] sections are complete, [M] need content. I'll work on the incomplete sections only — existing content will not be touched."
- 只處理狀態是 Empty 或 Placeholder 的章節。已經完成的章節不要重寫。

如果檔案不存在，這就是全新的撰寫 session。第一個通過核准的章節要用
`.claude/docs/templates/art-bible.md` 建立檔案，
retrofit 模式讀的那九個 `## N. Name` 標題就來自這份範本，所以要先問：
"May I create `design/art/art-bible.md` from the art bible template?" 之後每個
通過核准的章節，用 `Edit` 把自己那行 `[To be designed]` 換掉；
標題維持範本原樣。

**章節的核准就是寫入的授權。** 每個章節都要透過
`AskUserQuestion` 核准，而代表核准的選項是 `[A] Lock this in and write it to
design/art/art-bible.md`（第 1 章的完整選項清單在下面）。選了它就是核准寫入那個章節；
沒有這個核准，任何章節都不准寫，全新撰寫或 retrofit 都一樣。

擷取效能預算和引擎，作為素材標準的限制條件：從 `project.yaml` 讀 `performance.*` 和 `engine.name`；任何 key 不存在或是空的（包含 `project.yaml` 沒有 `performance` 或 `engine` 區塊的情況），就退回 `.claude/docs/technical-preferences.md`。

---

## Phase 1: 框定範圍

先把 session 的背景說明給使用者，並在動筆前問兩個問題：

用 `AskUserQuestion` 開兩個分頁：
- 分頁 **"Scope"**：「Which sections need to be authored today?」
  選項：`Full bible — all 9 sections` / `Visual identity core (sections 1–4 only)` / `Asset standards only (section 8)` / `Resume — fill in missing sections`

  **把解析後的 `workflow` tier 實際要求的那個選項標成
  (Recommended)，並說明原因**，因為 tier 已經決定了答案，
  使用者不該為了回答還得先懂 tier 對照表：
  - `full` → **Full bible**：這個 tier 需要全部 9 章。
  - `standard` → **Visual identity core (sections 1–4 only)**：那是
    有要求 art bible 時文件寫的最低限度。要說：「Sections 1–4
    are what `standard` requires; 5–9 are available if you want them.」
  - `minimal` → 不需要 art bible。問之前先這樣講，
    然後把第 1–4 章當成「想要的話很有用」的選項，不要預設選 9 章。
  - `workflow_overrides.art_bible_strict: true` → 不管 tier，一律 **Full bible**。

  這是這個 skill 最大的成本槓桿：每個要寫的章節都要 spawn 一次專家，
  tier 只需要 4 章卻寫 9 章，執行成本會多一倍以上，
  而多出來的產物下游根本不會檢查。
- 分頁 **"References"**：「Do you have reference games, films, or art that define the visual direction?」
  （自由輸入，讓使用者自己打具體作品名稱。這裡不要預設選項。）

如果 game-concept.md 有 Visual Identity Anchor 章節，要提出來：
> "Found a visual identity anchor from brainstorm: '[anchor name] — [one-line rule]'. I'll use this as the foundation for the art bible."

**只寫選定範圍內的章節。** Phase 2–4 只跑
範圍內的章節（`Resume` 的話，就是 retrofit 表裡 Empty 和 Placeholder 的那幾列），
其他章節全部跳過，沒有章節可跑的 phase 也跳過。
Phase 6 要逐一說明這次沒寫的章節和原因。

---

## Phase 2: 視覺識別基礎（第 1–4 章）

這四章定義核心視覺語言。**其他所有章節都從它們延伸。** 每章寫完、存進檔案，才能做下一章。

> **這個 phase 的 spawn 策略。** 第 1 章要單獨委派，因為它是
> 基礎，使用者要先在幾個 anchor 方向之間做選擇，其他東西才蓋得上去。
> 第 2–4 章則合併成**一次** `art-director`
> 呼叫，不是三次：同一個 agent、同樣的輸入（Visual
> Identity Statement + pillars），而且氛圍、造型和色彩互相牽動，
> art director 是一起定義它們的，不是各自獨立。分開呼叫
> 等於叫 agent 在不知道自己剛寫的造型語言的情況下去推敲色彩。
>
> **這不是減少專家的參與**：每個章節仍然由專家撰寫，
> 這正是 `.claude/docs/effects-map.md` 說 art bible
> 委派是強制的那個重點。只是同樣三個章節，一次呼叫取代三次。
> 每章使用者核准、核准後立刻寫入檔案，這兩點都不變。

### Section 1: Visual Identity Statement

**目標**：一句視覺規則，加上 2–3 條輔助原則，用來化解視覺上的模糊地帶。

如果 game-concept.md 有 visual anchor：把它拿出來，然後問：
- "Build directly from this anchor?"
- "Revise it before expanding?"
- "Start fresh with new options?"

**Agent 委派（強制）**：用 `Agent` spawn `art-director`：
- 提供：遊戲概念（elevator pitch、core fantasy）、完整的 pillar 組合、目標平台、Phase 1 框定時拿到的任何參考遊戲／美術、visual anchor（如果有）
- 要求："Draft a Visual Identity Statement for this game. Provide: (1) a one-line visual rule that could resolve any visual decision ambiguity, (2) 2–3 supporting visual principles, each with a one-sentence design test ('when X is ambiguous, this principle says choose Y'). Anchor all principles directly in the stated pillars — each principle must serve a specific pillar. (From a one-page brief, which has no pillars, anchor them in its pitch and "what they feel" line.)"

把 art-director 的草稿給使用者看。用 `AskUserQuestion`：
- 選項：`[A] Lock this in and write it to design/art/art-bible.md` / `[B] Revise the one-liner` / `[C] Revise a supporting principle` / `[D] Describe my own direction`

核准的章節立刻寫進檔案。

### Section 2: Mood & Atmosphere

**目標**：依遊戲狀態列出情緒目標，具體到燈光美術可以直接照著做。

對每個主要遊戲狀態（例如探索、戰鬥、勝利、失敗、選單，依這款遊戲的狀態調整），定義：
- 主要情緒／氛圍目標
- 燈光特性（時段、色溫、對比程度）
- 氛圍形容詞（3–5 個）
- 能量程度（狂亂 / 有節制 / 沉思 / 等等）

**第 2–4 章的 agent 委派：一次呼叫，在這裡發出。** 用 `Agent` spawn
`art-director`，給它已鎖定的 Visual Identity Statement 和 pillar 組合，
用一份 brief 要三個章節：

1. **Mood & atmosphere**："Define mood and atmosphere targets for each major game state in this game. Be specific — 'dark and foreboding' is not enough. Name the exact emotional target, the lighting character (warm/cool, high/low contrast, time of day direction), and at least one visual element that carries the mood. Each game state must feel visually distinct from the others."
2. **Shape language**："Define the shape language for this game. Connect each shape principle back to the visual identity statement and a specific game pillar. Explain what these shape choices communicate to the player emotionally."
3. **Colour system**："Design the color system for this game. Every semantic color assignment must be explained — why does this color mean danger/safety/reward in this world? Identify which color pairs might fail colorblind players and specify what backup cues are needed."

要求三者**彼此一致**（調色盤要服務氛圍
目標和造型層級），並且分成三個各自標記的區塊回傳，
這樣每個區塊都能單獨核准、單獨寫入。

然後把**第 2 章**給使用者看，核准後，在進第 3 章之前
立刻寫進檔案。不要三章一起給：
批次處理只發生在委派，不是在審閱。

### Section 3: Shape Language

**目標**：讓這款遊戲的世界在視覺上前後一致又容易區分的幾何語彙。

涵蓋：
- 角色剪影哲學（縮圖大小下要多好辨認？每個原型有什麼區別特徵？）
- 環境幾何（有稜角 / 曲線 / 有機 / 幾何，哪一種為主、為什麼？）
- UI 造型語法（UI 是呼應世界美學，還是獨立的 HUD 語言？）
- 主角造型 vs. 配角造型（什麼吸引視線、什麼退到後面？）

**草稿來源**：第 2 章底下發出的第 2–4 章委派，用它回傳的
造型語言區塊。不要再 spawn 一次。

核准的章節立刻寫進檔案。

### Section 4: Color System

**目標**：一套完整、做得出來的調色盤系統，同時滿足美感和溝通需求。

涵蓋：
- 主色盤（5–7 個顏色與其角色，不只是 hex 色碼，還要講每個顏色在這個世界裡代表什麼）
- 語意色彩用法（紅色傳達什麼？金色？藍色？白色？建立色彩詞彙）
- 各 biome 或各區域的色溫規則（如果遊戲有不同的區域）
- UI 調色盤（可以跟世界調色盤不同，要明確定義兩者的差異）
- 色盲安全：哪些語意色彩需要造型／圖示／聲音作為備援

**草稿來源**：第 2 章底下發出的第 2–4 章委派，用它回傳的
色彩系統區塊。不要再 spawn 一次。

核准的章節立刻寫進檔案。

---

## Phase 3: 製作指南（第 5–8 章）

這幾章把視覺識別轉成具體的製作規則。要具體到外包團隊不需要額外說明就能照做。

### Section 5: Character Design Direction

**第 5–6 章的 agent 委派：一次呼叫，在這裡發出。** 兩章
需要**同一個 agent、同樣的輸入**（`sections 1–4`），第二次呼叫
只會把整套視覺識別再送一遍。用第 1–4 章 spawn `art-director` 一次，
要兩個章節：

1. **Character design direction**："Cover: visual archetype for the player character (if any), distinguishing feature rules per character type (how do players tell enemies/NPCs/allies apart at a glance?), expression/pose style targets (stiff/expressive/realistic/exaggerated), and LOD philosophy (how much detail is preserved at game camera distance?)."
2. **Environment design language**："Cover: architectural style and its relationship to the world's culture/history, texture philosophy (painted vs. PBR vs. stylized — why this choice for this game?), prop density rules (sparse/dense — what drives the choice per area type?), and environmental storytelling guidelines (what visual details should tell the story without text?)."

要求角色和環境**彼此看得清楚**：角色
剪影在同一份 brief 定義的環境貼圖密度下也要讀得出來。回傳兩個各自標記的區塊。

先給**第 5 章**，核准、寫進檔案，再做第 6 章。

### Section 6: Environment Design Language

**草稿來源**：第 5 章底下發出的第 5–6 章委派，用它回傳的
環境區塊。不要再 spawn 一次。

核准的章節寫進檔案。

### Section 7: UI/HUD Visual Direction

**Agent 委派**：平行 spawn：
- **`art-director`**：UI 的視覺風格：diegetic vs. screen-space HUD、字體方向（字型個性、粗細、大小層級）、圖示風格（扁平 / 線框 / 插畫 / 擬真）、UI 元素的動畫手感
- **`ux-designer`**：UX 對齊檢查：這個視覺方向撐得住這款遊戲需要的互動模式嗎？標出美術方向和可讀性／無障礙需求之間的任何衝突。

兩邊都收回來。如果兩邊衝突（例如 art-director 想要精緻的 diegetic UI，但 ux-designer 指出會降低戰鬥可讀性），要把衝突明確呈現出來，兩邊立場都寫。絕對不准默默擺平，用 `AskUserQuestion` 讓使用者決定。

核准的章節寫進檔案。

### Section 8: Asset Standards

**Agent 委派**：平行 spawn：
- **`art-director`**：檔案格式偏好、命名規則方向、貼圖解析度分級、LOD 等級期望、輸出設定的理念
- **`technical-artist`**：引擎層面的硬性限制：各素材類別的面數預算、貼圖記憶體上限、材質 slot 數量、importer 限制，以及效能預算裡的任何東西（`project.yaml` 的 `performance.*`，退回 `.claude/docs/technical-preferences.md`）

如果有任何美術偏好跟技術限制衝突（例如 art-director 想要 4K 貼圖，但效能預算要求手機用 2K），要把衝突明確呈現，兩邊立場都寫：理想標準、受限標準，還有取捨。絕對不准默默擺平，用 `AskUserQuestion` 讓使用者選（選項：理想標準、受限標準，或兩個都記錄下來，由各素材自行判斷）。素材標準裡的模糊地帶，就是製作成本冒出來的地方。

核准的章節寫進檔案。

---

## Phase 4: 參考方向（第 9 章）

**目標**：一組精挑細選的參考資料，每個來源都具體說明要取什麼、要避開什麼。

**Agent 委派**：用 `Agent` spawn `art-director`，給它已完成的第 1–8 章。要求："Compile a reference direction for this game. Provide 3–5 reference sources (games, films, art styles, or specific artists). For each: name it, specify exactly what visual element to draw from it (not 'the general aesthetic' — a specific technique, color choice, or compositional rule), and specify what to explicitly avoid or diverge from (to prevent the 'trying to copy X' reading). References should be additive — no two references should be pointing in exactly the same direction."

核准的章節寫進檔案。

---

## Phase 5: Art Director 簽核

**Review mode 檢查**：spawn AD-ART-BIBLE 之前先套用：
- `solo` → 跳過。註明："AD-ART-BIBLE skipped — Solo mode." 然後記錄這次跳過
  （見下面），再進 Phase 6。
- `lean` → 跳過（它不是 PHASE-GATE）。註明："AD-ART-BIBLE skipped — Lean mode."
  然後記錄這次跳過（見下面），再進 Phase 6。
- `full` → 照常 spawn。

不管是哪種跳過，都要問 "May I record the skipped sign-off in
`design/art/art-bible.md`'s header?"，使用者答應的話，把標頭裡的
`> **Art Director Sign-Off (AD-ART-BIBLE)**: [Not yet reviewed]` 換成
`> **Art Director Sign-Off (AD-ART-BIBLE)**: SKIPPED [date] — [solo|lean] mode`
，gate 這兩種格式都接受為已記錄的簽核。

所有章節都完成之後（或 Phase 1 選定的範圍都完成之後），用 `Agent` spawn `art-director`，使用 gate **AD-ART-BIBLE**（`.claude/docs/director-gates/ad-art-bible.md`）。

要傳入：art bible 的路徑（`design/art/art-bible.md`）；遊戲 pillars 和核心幻想；
平台和效能限制（`project.yaml` 的 `platform.*` 和
`performance.*`，退回
`.claude/docs/technical-preferences.md`）；還有 visual identity anchor。如果
Phase 0 讀的是一頁式 brief，就把它的 pitch 和「what they feel」那行當成
pillars 和 fantasy 傳入，把它的「Art & audio direction」那行當成 anchor。

依 `director-gates.md` 的標準規則處理 verdict。
遇到 `Revise flagged items`，或要解決 REJECT 時，該章節自己的專家
（`art-director`，第 7 章加 `ux-designer`，第 8 章加 `technical-artist`）
重寫每個被標記的章節，然後和其他章節一樣呈現、核准、寫入，之後才記錄 `REVISED [date]`。
`NOT ASSESSED` 的回答絕對不算核准：指出缺少的輸入，
然後補上輸入、重跑 gate，或是記錄 `NOT ASSESSED`。
把 verdict 記錄在 art bible 的狀態標頭：
`> **Art Director Sign-Off (AD-ART-BIBLE)**: APPROVED [date] / CONCERNS (accepted) [date] / REVISED [date] / NOT ASSESSED [date] — [missing input]`

---

## Phase 6: 收尾

先逐一說明這次沒寫的那幾章和原因（九章裡沒寫的）：
在選定範圍之外，或是已經完成，例如 *"Not authored this run: sections
5–9 (outside the chosen scope; `standard` requires 1–4)."* 只做到
第 4 章就停的話，看起來絕對不能像一份完成的 bible。

在呈現下一步之前，先檢查專案狀態：
- `design/gdd/systems-index.md` 存在嗎？→ map-systems 已經做過，跳過那個選項
- 有沒有設定引擎，也就是 `project.yaml` 裡有 `engine.name`，或 `.claude/docs/technical-preferences.md` 裡有設定好的 Engine 欄位（不是 `[TO BE CONFIGURED]`）？→ setup-engine 已經做過，跳過那個選項
- `design/gdd/` 裡有任何 `*.md` 嗎？→ design-system 已經跑過，跳過那個選項
- `design/gdd/gdd-cross-review-*.md` 存在嗎？→ review-all-gdds 已經做過
- GDD 存在嗎（看上面的檢查）？→ 加入 /consistency-check 選項

用 `AskUserQuestion` 問下一步。只放根據上面狀態檢查真的是下一步的選項：

在 `workflow: minimal` 時，選項池是 `/create-stories`（還沒有 story）或
`/dev-story [next story]`，再加 Stop here；下面那個 GDD／架構的選項池只給
`standard`/`full`。

**選項池：只放還沒做過的：**
- `[_] Run /map-systems — decompose the concept into systems before writing GDDs`（systems-index.md 存在就跳過）
- `[_] Run /setup-engine — configure the engine (asset standards may need revisiting after engine is set)`（引擎已設定就跳過）
- `[_] Run /design-system — start the first GDD`（有任何 GDD 就跳過）
- `[_] Run /review-all-gdds — cross-GDD consistency check (required before Technical Setup gate)`（gdd-cross-review-*.md 存在就跳過）
- `[_] Run /asset-spec — generate per-asset visual specs and AI generation prompts from approved GDDs`（有 GDD 就放進去）
- `[_] Run /consistency-check — scan existing GDDs against the art bible for visual direction conflicts`（有 GDD 就放進去）
- `[_] Run /create-architecture — author the master architecture document (next Technical Setup step)`
- `[_] Stop here`

字母 A、B、C… 只分配給實際放進去的選項。把最合理、能推進 pipeline 的那個選項標成 `(recommended)`。

> **一定要放**（只限 `standard`/`full`）`/create-architecture` 和 Stop here 這兩個選項，art bible 完成後，它們永遠是合理的下一步。

---

## 協作協定

**在 `collaborative` 模式（預設）下適用。** `guided` 和
`autonomous` 模式見 `.claude/docs/automation-modes.md`，下面這些規則
描述的是 collaborative 模式的要求，不是通用行為。

每個章節都照這個流程走：**Question → Options → Decision → Draft（來自 art-director agent）→ Approval → Write to file**

- 絕對不准自己起草章節，每個章節的內容都要來自
  對應的專家。一次委派可以涵蓋好幾章（第 2–4 章共用
  一次呼叫，第 5–6 章也是），但沒有任何章節可以靠 orchestrator 自己的
  判斷寫出來取代 agent。
- 每章核准後立刻寫進檔案，不要把**寫入和核准**
  攢在一起批次做。批次只適用於委派呼叫；
  使用者還是一次看一個章節、核准一個、提交一個。
- 把 agent 之間所有的意見分歧都呈現給使用者，絕對不要默默解決 art-director 和 technical-artist 之間的衝突
- art bible 是一份限制性文件：它用限制未來的決策來換取視覺上的一致。每個章節都該讓解空間有成效地縮小。

---

## 建議的下一步

art bible 核准之後：
- 跑 `/map-systems`，在撰寫 GDD 之前先把概念拆解成遊戲系統
- 如果還沒設定引擎，跑 `/setup-engine`（選完引擎後，素材標準可能需要重新檢視）
- 跑 `/design-system [first-system]`，開始撰寫各系統的 GDD
- GDD 出來之後，跑 `/consistency-check`，用 art bible 的視覺規則驗證它們
- 跑 `/create-architecture`，產出主架構文件
