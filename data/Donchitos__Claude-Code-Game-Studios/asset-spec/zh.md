---
name: asset-spec
description: "從 GDD 和角色設定檔產出每個素材的視覺規格，加上 AI 生成 prompt。在 art bible 之後使用。"
argument-hint: "[system:<name> | level:<name> | character:<name>] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, Bash(bash "*/.claude/skills/asset-spec/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation`

# Asset Spec



如果沒有給參數，先檢查 `design/assets/entity-inventory.md` 是否存在：
- 存在：讀它，找出第一個狀態是 "Needed" 但還沒有規格檔的 entity 或畫面，然後用 `AskUserQuestion`：
  - Prompt: "The next unspecced item is **[name]**. Generate specs for it?"
  - 選項：`[A] Yes — spec [name]` / `[B] Pick a different item` / `[C] Stop here`
- 沒有 entity inventory：檢查 `design/assets/asset-manifest.md`。manifest 存在的話，走上面同樣的流程，只是改成從 manifest 讀。
- 兩個都不存在：**啟動 Entity & Screen Inventory 流程**（下面的 Phase 0b），不要直接失敗。

---

每一次 `AskUserQuestion` 呼叫都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律詢問 · guided 只問重大事項 · autonomous 記錄後直接往下走；
屬於 `automation_always_ask` 的類別一律要問）。**注意**：實際呼叫外部影像
生成器（呼叫影像 API）不管 `modes.automation` 是什麼，一律要問，
因為它是不可逆的外部動作，無條件把關，
跟 `external_calls` 有沒有列在 `automation_always_ask` 裡無關。
（目前這個 skill 只會輸出生成 prompt 的
*文字*；如果以後接上即時生成，這個把關就會適用。）

## Phase 0b: Entity & Screen Inventory（沒有參數、也沒有現成 inventory 時執行）

這個流程會產出 `design/assets/entity-inventory.md`，也就是這款遊戲
所有視覺需求的總清單。在開始做素材規格之前先跑一次。

### Step 1：從文件蒐集
平行讀完所有能拿到的來源資料，每份文件都按章節讀：用 Grep 工具
（pattern `^#`、content mode）找出需要的標題，再用 offset 和 limit 讀那幾段範圍。
- `design/gdd/systems-index.md`：擷取列出的每個系統
- GDD 的素材內容：**不要**把每份 GDD 都完整讀完。要的那兩個章節
  是標準標題，具名的 entity 則放在 registry：
  ```
  Grep pattern="## (Visual/Audio Requirements|UI Requirements)" glob="design/gdd/*.md" output_mode="content" -A 25
  ```
  具名的 entity（角色、敵人、建築、道具），如果 `design/registry/entities.yaml`
  （`entities`/`items`）存在而且有項目，就讀它；否則就去 GDD 裡 grep 具名內容。
  只有在某份 GDD 的 Visual/Audio 章節缺少、或內容是 `[To be designed]` 時，才完整讀它
  （Phase 1 已經處理那個情況）。VFX 事件會出現在 Visual/Audio 的 grep context 裡。
- `design/art/art-bible.md`：擷取任何具名的視覺類別、素材類型期望
- `design/narrative/`：如果有角色或世界 entity 文件，就掃一下（選用，不是必要）

### Step 2：建立建議的 inventory
把找到的所有東西整理成類別：

```
Characters / Protagonists
Enemies / Creatures
Buildings / Structures
Environment / Terrain
Items / Props
VFX / Particles
UI Screens (list each screen by name)
HUD Elements
Audio (SFX, music — descriptions only, no generation prompts)
Other
```

每個項目都要註明它是從哪份來源文件找到的。

### Step 3：呈現並協作
在對話中把完整的建議 inventory 給使用者看。然後用 `AskUserQuestion`：
- Prompt: "I found **[N] visual entities and [N] UI screens** across your GDDs and art bible. Review the list — what's missing, what's not needed?"
- 選項：
  - `[A] Looks good — save this inventory`
  - `[B] Add items I'll describe`
  - `[C] Remove items that don't apply`
  - `[D] Both add and remove — let me edit`

選 [B] 或 [D]：請使用者描述要新增的項目。簡短描述（"a medieval keep, used as a level background"）或詳細描述都可以。和使用者一起處理，直到他們滿意。

選 [C] 或 [D]：問要移除哪些項目、為什麼，然後從清單中移除。

### Step 4：寫入 inventory
使用者核准後，問："May I write the entity inventory to `design/assets/entity-inventory.md`?"

寫入檔案：

```markdown
# Visual Entity & Screen Inventory

> Generated: [date]
> Sources: [list of source docs read]

## Entities

| # | Name | Type | Description | Source | Status |
|---|------|------|-------------|--------|--------|
| 1 | [name] | Character / Enemy / Building / Environment / Item / Other | [brief description] | [source doc] | Needed |

## UI Screens

| # | Screen Name | Description | Source | Status |
|---|-------------|-------------|--------|--------|
| 1 | Main Menu | [description] | [source] | Needed |

## HUD Elements

| # | Element | Description | Source | Status |
|---|---------|-------------|--------|--------|

## Audio

| # | Name | Type (SFX / Music / Ambient) | Description | Source | Status |
|---|------|------------------------------|-------------|--------|--------|
```

寫完後，告訴使用者：
> "Entity inventory saved. Next steps:
> - Run `/ux-design [screen name]` for each UI screen in the inventory
> - Run `/asset-spec system:[name]`, `level:[name]` or `character:[name]` for each
>   visual entity — whichever of the three the entity belongs to
> - Or run `/asset-spec` again to work through the inventory one item at a time"

---

## Phase 0: 解析參數

擷取：
- **Target type**：`system`、`level` 或 `character`
- **Target name**：冒號後面的名稱（正規化成 kebab-case）
- **Review mode**：如果有給 `--review [full|lean|solo]`

實際生效的模式，是這個 skill 開頭透過
`resolve_config --keys review_mode` 已經解析好的那個，它會套用完整的優先順序；什麼都沒設的話，
就跟著 `modes.rigor`：`minimal`（預設）是 `solo`、`standard` 是 `lean`、
`full` 是 `full`。`--review` 參數只在這次執行覆蓋它。

**各模式的行為：**
- `full`：平行 spawn `art-director` 和 `technical-artist`
- `lean`：只 spawn `art-director`，比較快，跳過技術限制那一輪
- `solo`：不 spawn agent，由主 session 單靠 art bible 規則寫規格。用在簡單的素材類別，或是速度比深度重要的時候。

---

## Phase 1: 蒐集 Context

**在問使用者任何問題之前**，先把所有來源資料讀完。art bible 和
GDD 都按章節讀：用 Grep 工具（pattern `^#`、
content mode）找出需要的標題，再用 offset 和 limit 讀那幾段範圍。

### 必讀：
- **Art bible**：讀 `design/art/art-bible.md`，不存在就失敗：
  > "No art bible found. Run `/art-bible` first — asset specs are anchored to the art bible's visual rules and asset standards."

  **例外：最精簡路徑。** 如果沒有 art bible，但
  `design/game-brief.md` 存在（在 `rigor: minimal` 時不需要 art bible），
  就不要失敗：把規格錨定在 brief 的 **Art & audio direction** 那行，
  並且在輸出最上面講清楚："Anchored to the brief's one-line art
  direction; there is no art bible, so colour, shape and asset-standard rules
  below are proposals, not constraints." 只提一次 `/art-bible`，標明是選用。
  寫出來的規格也跟著同一個 anchor：它的標頭寫成
  `> **Art direction**: design/game-brief.md (Art & audio direction) — no art bible`
  ，取代 `> **Art Bible**:` 那行，每個素材帶
  `**Brief anchor:** [the brief line applied]`，取代 **Art Bible
  Anchors** 區塊，而且沒有任何規格會引用 Art Bible 章節或 §8 tier。
  擷取：Visual Identity Statement、Color System（語意色彩）、Shape Language、Asset Standards（art bible 第 8 章，包含尺寸、格式、面數預算、貼圖解析度分級）。

- **專案設定**：從 `project.yaml` 讀 `performance.*` 和 `naming.*`；任何 key 不存在或是空的（包含 `project.yaml` 沒有 `performance` 或 `naming` 區塊的情況），就退回 `.claude/docs/technical-preferences.md`。擷取效能預算和命名規則。

### 依目標類型讀來源文件：
- **system**：讀 `design/gdd/[target-name].md`。擷取 **Visual/Audio Requirements** 章節。如果它不存在，或內容是 `[To be designed]`：
  > "The Visual/Audio section of `design/gdd/[target-name].md` is empty. Either run `/design-system [target-name]` to complete the GDD, or describe the visual needs manually."
  用 `AskUserQuestion`：`[A] Describe needs manually` / `[B] Stop — complete the GDD first`
- **level**：讀 `design/levels/[target-name].md`。擷取美術需求、素材清單、VFX 需求，以及 art-director 在 Step 4 產出的製作概念規格。
- **character** 或 **entity**：讀 `design/narrative/characters/[target-name].md`，或在 `design/narrative/` 和 `design/assets/entity-inventory.md` 裡搜尋對應的項目。擷取視覺描述、角色定位，和任何有指定的區別特徵。
  - **如果沒有來源文件**：不要失敗。改用 `AskUserQuestion`：
    - Prompt: "No profile found for **[name]**. Describe it briefly — a sentence or two is enough."
    - 選項：`[A] Describe it now` / `[B] Skip this entity` / `[C] Stop here`
    - 選 [A]：使用者的描述就是來源。簡短的回答產出簡潔的規格，詳細的回答產出詳細的規格。使用者給多少細節就接受多少，照著做。

### 選讀：
- **這個目標已存在的規格**：如果 `design/assets/specs/[target-name]-assets.md` 存在就讀它，這是重跑，Phase 2 只提出之後新增或變動的內容（Phase 5 會就地更新檔案）。
- **現有的 manifest**：如果 `design/assets/asset-manifest.md` 存在就讀它，擷取這個目標已經做過規格的素材，避免重複。
- **相關規格**：Glob `design/assets/specs/*.md`，掃描有沒有可以共用的素材（例如替某個系統做過規格的通用 UI 元素，可能這裡也適用）。

### 呈現 context 摘要：
> **Asset Spec: [Target Type] — [Target Name]**
> - Source doc: [path] — [N] asset types identified
> - Art bible: found — Asset Standards at Section 8
> - Existing specs for this target: [N already specced / none]
> - Shared assets found in other specs: [list or "none"]

---

## Phase 2: 辨識素材

從來源文件擷取提到的每一種素材類型，明講的和隱含的都要。

**系統**：找 VFX 事件、sprite 參照、UI 元素、音訊觸發、粒子特效、圖示需求，還有任何「視覺回饋」的描述。

**關卡**：找獨有的環境道具、氛圍 VFX、燈光配置、環境音、天空盒／背景，還有任何區域專屬的材質。

**角色**：找 sprite sheet（idle、walk、attack、death）、肖像／頭像、附在技能上的 VFX、UI 上的呈現（圖示、血條外觀）。

把素材分組成類別：
- **Sprite / 2D Art**：角色 sprite、UI 圖示、tile sheet
- **VFX / Particles**：命中效果、環境粒子、螢幕特效
- **Environment**：道具、tile、背景、天空盒
- **UI**：HUD 元素、選單美術、字型（如果是自訂的）
- **Audio**：SFX、音樂曲目、環境循環音 *（注意：音訊規格只有描述，沒有生成 prompt）*
- **3D Assets**：mesh、材質（依引擎而定，如果適用）

把完整辨識出來的清單給使用者看。用 `AskUserQuestion`：
- Prompt: "I identified [N] assets across [N] categories for **[target]**. Review before speccing:"
- 先在對話文字裡顯示分組後的清單
- 選項：`[A] Proceed — spec all of these` / `[B] Remove some assets` / `[C] Add assets I didn't catch` / `[D] Adjust categories`

使用者沒有確認素材清單之前，絕對不准進 Phase 3。

---

## Phase 3: 產生規格

依 review mode spawn 專家 agent。**所有 `Agent` 呼叫要同時發出，不要等一個做完才開始下一個。**

### Full 模式：平行 spawn：

**`art-director`**，透過 `Agent`：
- 提供：Phase 2 的完整素材清單、art bible 的 Visual Identity Statement、Color System、Shape Language、來源文件的視覺需求，以及 art bible 第 9 章提到的任何參考遊戲／美術
- 要求："For each asset in this list, produce: (1) a 2–3 sentence visual description anchored to the art bible's shape language and color system — be specific enough that two different artists would produce consistent results; (2) a generation prompt ready for use with AI image tools (Midjourney/Stable Diffusion style — include style keywords, composition, color palette anchors, negative prompts); (3) which art bible rules directly govern this asset (cite by section). For audio assets, describe the sonic character instead of a generation prompt."

**`technical-artist`**，透過 `Agent`：
- 提供：完整素材清單、art bible 的 Asset Standards（第 8 章）、效能預算（`project.yaml` 的 `performance.*`，否則用 `technical-preferences.md`）、引擎名稱和版本
- 要求："For each asset in this list, specify: (1) exact dimensions or polycount (match the art bible Asset Standards tiers — do not invent new sizes); (2) file format and export settings; (3) naming convention (`naming.*` from `project.yaml`, else `technical-preferences.md`); (4) any engine-specific constraints this asset type must respect; (5) LOD requirements if applicable. Flag any asset type where the art bible's preferred standard conflicts with the engine's constraints."

### Lean 模式：只 spawn art-director（跳過 technical-artist）。

### Solo 模式：兩個都跳過。只靠 art bible 規則推導規格，並註明技術限制沒有驗證過。

**在規格之前，在輸出裡逐一點名每個被跳過的 agent**：
"technical-artist skipped — Lean mode: technical constraints not validated." /
"art-director and technical-artist skipped — Solo mode: specs derived in this
session; technical constraints not validated." 沒有 agent 參與起草的規格，
絕對不能看起來像是 agent 審過的。

**進 Phase 4 之前，兩邊的回應都要收齊。** 如果 art-director 和 technical-artist 之間有任何衝突（例如 art-director 指定 4K 貼圖，但 technical-artist 指出引擎預算要求 512px），要明確呈現出來，絕對不准默默擺平。

---

## Phase 4: 彙整與審閱

把 agent 的輸出彙整成每個素材的規格草稿。用下面這個格式，把所有規格呈現在對話文字裡：

```
## ASSET-[NNN] — [Asset Name]

| Field | Value |
|-------|-------|
| Category | [Sprite / VFX / Environment / UI / Audio / 3D] |
| Dimensions | [e.g. 256×256px, 4-frame sprite sheet] |
| Format | [PNG / SVG / WAV / etc.] |
| Naming | [e.g. vfx_frost_hit_01.png] |
| Polycount | [if 3D — e.g. <800 tris] |
| Texture Res | [e.g. 512px — matches Art Bible §8 Tier 2] |

**Visual Description:**
[2–3 sentences. Specific enough for two artists to produce consistent results.]

**Art Bible Anchors:**
- §3 Shape Language: [relevant rule applied]
- §4 Color System: [color role — e.g. "uses Threat Blue per semantic color rules"]

**Generation Prompt:**
[Ready-to-use prompt. Include: style keywords, composition notes, color palette anchors, lighting direction, negative prompts.]

**Status:** Needed
```

呈現完所有規格後，用 `AskUserQuestion`：
- Prompt: "Asset specs for **[target]** — [N] assets. Review complete?"
- 選項：`[A] Approve all — write to file` / `[B] Revise a specific asset` / `[C] Regenerate with different direction`

選 [B]：問是哪個素材、要改什麼。就地修改後重新呈現。小幅文字修改**不要**重新 spawn agent，只有視覺方向本身要改的時候才重新 spawn。

選 [C]：問要改什麼方向。用更新過的 brief 重新 spawn 相關的 agent。

---

## Phase 5: 寫入規格檔

核准後，問："May I write the spec to `design/assets/specs/[target-name]-assets.md`?"

**如果那個檔案已經存在**（同一個目標的重跑），就地更新，
絕對不要整份覆寫。保留它現有的 `ASSET-NNN` 區塊和
ID，只套用使用者核准的變更，新素材接在後面，用整個專案
下一個編號的 ID。先顯示變更內容，再問 "May I update
`design/assets/specs/[target-name]-assets.md`?"，不要問 "May I write"。

寫入檔案的內容：

```markdown
# Asset Specs — [Target Type]: [Target Name]

> **Source**: [path to source GDD/level/character doc]
> **Art Bible**: design/art/art-bible.md
> **Generated**: [date]
> **Status**: [N] assets specced / [N] approved / [N] in production / [N] done

[all asset specs in ASSET-NNN format]
```

接著更新 `design/assets/asset-manifest.md`。如果它不存在，就建立：

```markdown
# Asset Manifest

> Last updated: [date]

## Progress Summary

| Total | Needed | In Progress | Done | Approved |
|-------|--------|-------------|------|----------|
| [N] | [N] | [N] | [N] | [N] |

## Assets by Context

### [Target Type]: [Target Name]
| Asset ID | Name | Category | Status | Spec File |
|----------|------|----------|--------|-----------|
| ASSET-001 | [name] | [category] | Needed | design/assets/specs/[target]-assets.md |
```

如果 manifest 已經存在，就把新的 context 區塊接在後面。如果是這個目標的重跑，就把新的列加進它現有的區塊，不要再接第二個區塊。並且更新 Progress Summary 的數字。

問："May I update `design/assets/asset-manifest.md`?"

---

## Phase 6: 收尾

用 `AskUserQuestion`：
- Prompt: "Asset specs complete for **[target]**. What's next?"
- 選項：
  - `[A] Spec another system — /asset-spec system:[next-system]`
  - `[B] Spec a level — /asset-spec level:[level-name]`
  - `[C] Spec a character — /asset-spec character:[character-name]`
  - `[D] Run /asset-audit — validate delivered assets against specs`
  - `[E] Stop here`

---

## 素材 ID 的指派

素材 ID 是整個專案依序指派的，不是依 context 各自編。指派 ID 之前先讀 manifest，找出目前最大的編號：

```
Grep pattern="ASSET-" path="design/assets/asset-manifest.md"
```

新素材從 `ASSET-[highest + 1]` 開始。這樣能確保 ID 在整個專案裡穩定而且唯一。

如果還沒有 manifest，就從 `ASSET-001` 開始。

---

## 共用素材協定

替素材做規格之前，先檢查別的 context 的規格裡有沒有等價的素材：

- 通用 UI 元素（血條、分數顯示）常常跨系統共用
- 通用的環境道具可能出現在多個關卡
- 角色 VFX（命中火花、死亡效果）可能是同一個基礎規格加上顏色變體

如果找到對應的：引用既有的 ASSET-ID，不要建立重複的。把共用情況記錄在 manifest 的 referenced-by 欄。

> "ASSET-012 (Generic Hit Spark) already specced for Combat system. Reusing for Tower Defense — adding tower-defense to referenced-by."

---

## 錯誤復原協定

如果任何被 spawn 的 agent 回傳 BLOCKED 或無法完成：

1. 馬上呈現出來："[AgentName]: BLOCKED — [reason]"
2. 在 `lean` 模式，或是 `technical-artist` 卡住時：只用 art-director 的輸出繼續，並註明技術限制沒有驗證過
3. 在 `solo` 模式，或是 `art-director` 卡住時：從 art bible 規則推導描述，並標記為 "Art director not consulted — verify against art bible before production"
4. 一定要產出部分規格，絕對不要因為一個 agent 卡住就把做完的工作丟掉

---

## 協作協定

**在 `collaborative` 模式（預設）下適用。** `guided` 和
`autonomous` 模式見 `.claude/docs/automation-modes.md`，下面這些規則
描述的是 collaborative 模式的要求，不是通用行為。

每個 phase 都照這個流程走：**Identify → Confirm → Generate → Review → Approve → Write**

- 沒有先跟使用者確認素材清單，絕對不准替素材做規格
- 規格一定要錨定在 art bible，跟 art bible 矛盾的規格就是錯的
- 把所有 agent 之間的意見分歧呈現出來，不要默默挑一邊
- 一定要有明確核准才能寫規格檔
- 寫完規格後立刻更新 manifest

---

## 建議的下一步

- 跑 `/asset-spec [next-context]`，繼續替剩下的系統、關卡或角色做規格
- 跑 `/asset-audit`，用寫好的規格驗證已交付的素材，找出缺口或不一致
