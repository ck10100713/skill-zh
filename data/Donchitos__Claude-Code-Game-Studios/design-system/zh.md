---
name: design-system
description: "逐章撰寫單一系統的 GDD：走過每個必要章節，並交叉參照依賴。"
argument-hint: "<system-name> [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, TaskCreate, TaskGet, TaskList, TaskUpdate, Bash(bash "*/.claude/skills/design-system/../../hooks/yaml-helper.sh" resolve_config *), Bash(bash .claude/scripts/registry.sh *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,workflow,docs.density,system_overrides`

上面已經解析好了，直接用；`--review` 會覆蓋 `review_mode`。沒有這個區塊 →
用 `.claude/docs/config-resolution.md` 裡的預設值。

# Design System

這個 skill 被呼叫時：

## 1. 解析參數並驗證

**現在就讀 `references/1-parse-arguments.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復過，要再讀一次。

## 2. 蒐集 Context（讀取階段）

**現在就讀 `references/2-gather-context.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復過，要再讀一次。

## 3. 建立檔案骨架

**現在就讀 `references/3-file-skeleton.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復過，要再讀一次。

## 4. 逐章設計

**現在就讀 `references/4-section-design.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復過，要再讀一次。

## 5. 設計後驗證

**現在就讀 `references/5-post-design.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復過，要再讀一次。

## 6. 專家 Agent 路由

這個 skill 把領域專業委派給專家 agent。主 session
負責統籌整體流程；agent 提供專業內容。

**這裡的列刻意比九個 `Category` 的值切得更細**：
戰鬥適合的專家，不是尋路適合的專家，而兩者都是
`Gameplay`。分兩步解析：從 `systems-index.md` 取得系統的 `Category`，
然後在它底下挑出符合系統實際在做的事的那一列。每個分類至少有一列，
所以不會有漏網之魚。

| `Category` | Rows below to choose from |
|---|---|
| `Gameplay` | Combat/damage/health · AI/pathfinding/behavior · Animation/character movement · Character systems · Camera/input/controls |
| `Core` | Foundation/Infrastructure · Camera/input/controls |
| `Persistence` | Foundation/Infrastructure |
| `Economy` | Economy/loot/crafting |
| `Progression` | Progression/XP/skills |
| `UI` | UI systems · Visual effects (when the system is HUD-adjacent VFX) |
| `Audio` | Audio systems |
| `Narrative` | Dialogue/quests/lore |
| `Meta` | Foundation/Infrastructure (analytics, tutorial plumbing) · UI systems (accessibility options screens) |

如果有兩列都符合，就 spawn 它們 Primary agent 的聯集，並說明原因。

| System type | Primary Agent | Supporting Agent(s) |
|----------------|---------------|---------------------|
| **Foundation/Infrastructure** (event bus, save/load, scene mgmt, service locator) | `systems-designer` | `gameplay-programmer` (feasibility), `engine-programmer` (engine integration) |
| Combat, damage, health | `game-designer` | `systems-designer` (formulas), `ai-programmer` (enemy AI), `art-director` (hit feedback visual direction, VFX intent) |
| Economy, loot, crafting | `economy-designer` | `systems-designer` (curves), `game-designer` (loops) |
| Progression, XP, skills | `game-designer` | `systems-designer` (curves), `economy-designer` (sinks) |
| Dialogue, quests, lore | `game-designer` | `narrative-director` (story), `writer` (content), `art-director` (character visual profiles, cinematic tone) |
| UI systems (HUD, menus) | `game-designer` | `ux-designer` (flows), `ui-programmer` (feasibility), `art-director` (visual style direction), `technical-artist` (render/shader constraints) |
| Audio systems | `game-designer` | `audio-director` (direction), `sound-designer` (specs) |
| AI, pathfinding, behavior | `game-designer` | `ai-programmer` (implementation), `systems-designer` (scoring) |
| Level/world systems | `game-designer` | `level-designer` (spatial), `world-builder` (lore) |
| Camera, input, controls | `game-designer` | `ux-designer` (feel), `gameplay-programmer` (feasibility) |
| Animation, character movement | `game-designer` | `art-director` (animation style, pose language), `technical-artist` (rig/blend constraints), `gameplay-programmer` (feel) |
| Visual effects, particles, shaders | `game-designer` | `art-director` (VFX visual direction), `technical-artist` (performance budget, shader complexity), `systems-designer` (trigger/state integration) |
| Character systems (stats, archetypes) | `game-designer` | `art-director` (character visual archetype), `narrative-director` (character arc alignment), `systems-designer` (stat formulas) |

**透過 `Agent` 工具委派時**：
- 提供：系統名稱、遊戲概念摘要、依賴 GDD 的節錄、正在處理的
  特定章節，以及哪個問題需要專家意見
- agent 把分析／提案回傳給主 session
- 主 session 透過 `AskUserQuestion` 把 agent 的輸出呈現給使用者
- 由使用者決定；主 session 寫入檔案
- agent **不會**直接寫檔案，所有檔案寫入都由主 session 負責

---

## 7. 復原與接續

如果 session 被中斷（壓縮、當機、新 session）：

1. 讀 `production/session-state/active.md`：它記錄了目前的系統和
   哪些章節已經完成
2. 讀 `design/gdd/[system-name].md`：有真實內容的章節就是完成了；
   寫著 `[To be designed]` 的章節還需要做。按章節讀：用 Grep 工具
   （pattern `^#`、content mode）找出標題，再用 offset 和 limit 讀那幾段
   範圍。
3. 從下一個還沒完成的章節接續，不需要重新討論已完成的章節

這就是為什麼要漸進式寫入：每個核准過的章節都能撐過任何
中斷。

---

## 協作協定

**在 `collaborative` 模式（預設）下。** `guided` 和 `autonomous`
模式見 `.claude/docs/automation-modes.md` 裡各模式的規則，下面
"Never" 那幾行描述的是 collaborative 模式的要求，不是
普遍適用的規則。

這個 skill 在每一步都遵循協作設計原則：

1. 每個章節都走 **Question -> Options -> Decision -> Draft -> Approval**
2. 每個決策點都用 **AskUserQuestion**（Explain -> Capture 模式）：
   - Phase 2: "Ready to start, or need more context?"
   - Phase 3: "May I create the skeleton?"
   - Phase 4（每個章節）：設計問題、做法選項、草稿核准
   - Phase 5: "May I update the entity registry? May I update the systems
     index? What's next?"，**不是** "Run design review?"：§5c 禁止在這裡直接提議
     `/design-review`，因為審查的 agent 絕對不能繼承這個
     session 的設計歷史。Phase 5c 呈現的是交接，絕對不問。
3. 在骨架之前、每次章節寫入之前，都要問 **"May I write to [filepath]?"**
4. **漸進式寫入**：每個章節在核准後立刻寫進檔案
5. **Session 狀態更新**：每次章節寫入之後
6. **交叉參照**：每個章節都對照現有的 GDD 檢查衝突
7. **專家路由**：複雜的章節取得專家 agent 的意見，呈現給
   使用者決定，絕對不默默寫入

**絕對不准**自動產生完整的 GDD，然後當成既成事實呈現。
**絕對不准**在沒有使用者核准的情況下寫入章節。
**絕對不准**在沒有標出衝突的情況下，跟現有已核准的 GDD 矛盾。
**一定要**顯示決策是從哪裡來的（依賴的 GDD、pillars、使用者的選擇）。

## Context Window 意識

這是個長時間執行的 skill。每寫完一個章節，檢查狀態列是否顯示 context
在 70% 以上。如果是，就把這個通知附加到回覆中：

> **Context is approaching the limit (≥70%).** Your progress is saved — all approved
> sections are written to `design/gdd/[system-name].md`. When you're ready to continue,
> open a fresh Claude Code session and run `/design-system [system-name]` — it will
> detect which sections are complete and resume from the next one.

---

## 建議的下一步

- 在**全新的 session** 跑 `/design-review design/gdd/[system-name].md`，獨立驗證完成的 GDD
- 跑 `/consistency-check`，確認這份 GDD 的值沒有跟其他 GDD 衝突
- 跑 `/map-systems next`，進到下一個優先度最高、還沒設計的系統
- 所有 MVP GDD 都寫完並審查過之後，跑 `/gate-check technical-setup`
