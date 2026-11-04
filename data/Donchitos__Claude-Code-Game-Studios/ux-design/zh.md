---
name: ux-design
description: "逐章節撰寫畫面、流程或 HUD 的 UX 規格。會讀玩家旅程來取得 context；也處理專案層級的無障礙。"
argument-hint: "[screen/flow name] or 'hud' or 'patterns' or 'accessibility'"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Agent, Bash(bash "*/.claude/skills/ux-design/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation,workflow,docs.density`

上面已經解析好了，直接用。沒有這個區塊的話，就用
`.claude/docs/config-resolution.md` 裡的預設值。

# UX Design

呼叫這個 skill 時：

每一次 `AskUserQuestion` 呼叫都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律要問 · guided 只問重大的 · autonomous 記錄後直接往下走；
屬於 `automation_always_ask` 類別的一律要問）。

**撰寫指引**：下面的骨架是自給自足的，直接照著寫就好。當某個章節需要更深入的內容（實際範例、模式目錄、無障礙標準）時，對應的 guide 裡有：

| Producing | Guide |
|---|---|
| UX spec | `.claude/docs/templates/guidance/ux-spec-guide.md` |
| HUD design | `.claude/docs/templates/guidance/hud-design-guide.md` |
| Interaction patterns | `.claude/docs/templates/guidance/interaction-pattern-library-guide.md` (routes to three topic files) |
| Accessibility requirements | `.claude/docs/templates/guidance/accessibility-requirements-guide.md` |

**guide 要依章節載入，絕對不要整份載入**：每份都是依章節組織的，模板裡的指引會指出要讀的確切章節。

**`workflow`**（見 `.claude/docs/workflow-modes.md`）：
- `full` — 每個畫面都需要一份 UX 規格。
- `standard` — 只要核心畫面（主選單、HUD、主要遊戲迴圈）。
- `minimal` — 不是必要的。仍然可以自願執行。

**`docs.density`**：它控制每個章節的*深度*，而 `workflow` 控制哪些畫面要寫規格。`modes.rigor` 會同時設定這兩者；要只改變深度，就明確設定 `docs.density`：`terse`（預設，透過 `rigor: minimal`）= 線框圖描述 + 互動要點；`balanced` = 線框圖 + 流程的段落描述（`rigor: standard`）；`thorough` = 完整的文字敘述，包含使用者研究摘要和替代流程的考量。要套用到你撰寫的每一個章節。

## 1. Parse Arguments & Determine Mode

根據參數有四種撰寫模式：

| Argument | Mode | Output file |
|----------|------|-------------|
| `hud` | HUD design | `design/ux/hud.md` |
| `patterns` | Interaction pattern library | `design/ux/interaction-patterns.md` |
| `accessibility` | Project-wide accessibility requirements | `design/accessibility-requirements.md` |
| Any other value (e.g., `main-menu`, `inventory`) | UX spec for a screen or flow | `design/ux/[argument].md` |
| No argument | Ask the user | (see below) |

> **`accessibility` 是唯一會寫到 `design/ux/` 之外的模式。** 它的輸出是各畫面規格會參考的專案層級標準，不是某一個畫面的規格：`.claude/docs/workflow-catalog.yaml`、Pre-Production 和 Polish 的 gate，以及 `/architecture-review`，都是在那個確切的路徑檢查 `design/accessibility-requirements.md`。不要為了「整理」把它搬進 `design/ux/`：那些檢查全都會比對不到，Technical Setup → Pre-Production 的 gate 就會變成過不了。

**如果沒有提供參數**，不要失敗，改成問。用 `AskUserQuestion`：
- "What are we designing today?"
  - Options: "A specific screen or flow (I'll name it)", "The game HUD", "The interaction pattern library", "The project-wide accessibility requirements", "I'm not sure — help me figure it out"

如果使用者選「I'll name it」或輸入了畫面名稱，就把它正規化成 kebab-case 當檔名（例如「Main Menu」變成 `main-menu`）。

---

## 2. Gather Context (Read Phase)

**現在就讀 `references/2-gather-context.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復，要再讀一次。

## 3. Create File Skeleton

**現在就讀 `references/3-file-skeleton.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復，要再讀一次。

## 4. Section-by-Section Authoring

**現在就讀 `references/4-authoring.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復，要再讀一次。

### Section guidance — read the ONE file for the active mode

每個模式的逐章節撰寫指引，都放在各自的檔案裡。**到了 Phase 4，只讀跟 Section 1 解析出來的模式相符的那一個檔案；絕對不要載入另外兩個。**

| Mode | Guidance file |
|------|---------------|
| UX Spec (screen or flow) | `references/sections-ux-spec.md` |
| HUD Design | `references/sections-hud.md` |
| Interaction Pattern Library | `references/sections-patterns.md` |
| Accessibility Requirements | `.claude/docs/templates/guidance/accessibility-requirements-guide.md` |

> 無障礙的指引放在 `templates/guidance/` 底下，而不是這個 skill 的 `references/`，因為它所記載的模板（`.claude/docs/templates/accessibility-requirements.md`）也會被 `/ux-review` 和 gate 檔案使用。同樣的規則適用：只載入涵蓋你正在撰寫的那個章節的部分，絕對不要載入整份檔案。

把 `docs.density`（Section 1）套用到那個檔案叫你寫的內容：它控制每個章節的深度，不是控制有哪些章節。

## 5. Cross-Reference Check

**現在就讀 `references/5-crossref-handoff.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復，要再讀一次。

## 7. Recovery & Resume

如果 session 被中斷（壓縮、crash、新 session）：

1. 讀 `production/session-state/active.md`：它記錄了目前的畫面，以及哪些章節已經完成。
2. 讀 `design/ux/[filename].md`：有實際內容的章節就是完成了；還是 `[To be designed]` 的章節仍然要做。
3. 從下一個未完成的章節繼續：不需要重新討論已經完成的部分。

這就是為什麼要增量寫入：每個核准過的章節，不管遇到什麼中斷都保得住。

---

## 8. Specialist Agent Routing

這個 skill 以 `ux-designer` 作為主要 agent（在 frontmatter 設定）。針對特定的子主題，可能需要額外的 context 或協調：

| Topic | Coordinate with |
|-------|----------------|
| Visual aesthetics, color, layout feel | `art-director` — UX spec defines zones; art defines how they look |
| Implementation feasibility (engine constraints) | `ui-programmer` — before finalizing component inventory |
| Gameplay data requirements | `game-designer` — when data ownership is unclear |
| Narrative/lore visible in the UI | `narrative-director` — for flavor text, item names, lore panels |
| Accessibility tier decisions | Recorded by this session (`/ux-design accessibility`; the user picks the tier) against the criteria `accessibility-specialist` defines and audits — consult it when a requirement's criterion is unclear |

透過 `Agent` 工具委派給另一個 agent 時：
- 提供：畫面名稱、遊戲概念摘要、需要專家意見的具體問題
- agent 把分析結果回傳給這個 session
- 這個 session 把 agent 的輸出呈現給使用者
- 使用者決定；這個 session 寫入檔案
- Agent 不會直接寫檔案：所有檔案寫入都由這個 session 負責

---

## Collaborative Protocol

**在 `collaborative` 模式下（預設）。** 對 `guided` 和 `autonomous` 模式，見 `.claude/docs/automation-modes.md` 裡各模式的規則：下面的步驟描述的是 collaborative 模式的要求，不是普遍適用的。

這個 skill 在每一步都遵循協作式設計原則：

1. 每個章節都走 **Question -> Options -> Decision -> Draft -> Approval**
2. 每個決策點都用 **AskUserQuestion**（Explain -> Capture 的模式）：
   - Phase 2: "Ready to start, or need more context?"
   - Phase 3: "May I create the skeleton?"
   - Phase 4（每個章節）：設計問題、做法選項、草稿核准
   - Phase 5: "Run cross-reference check? What's next?"
3. 在骨架和每一次章節寫入之前，都要問 **"May I write to [filepath]?"**
4. **增量寫入**：每個章節在核准之後立刻寫入檔案
5. **Session state 更新**：每次章節寫入之後

**美感上的讓步**：當版面或視覺的選擇取決於個人品味時，把選項呈現出來並詢問。不要因為某個版面「很標準」就選它，一定要確認。使用者才是創意總監。

**衝突要揭露**：當 GDD 的需求和可用的畫面空間互相衝突時，把衝突揭露出來，並呈現解決選項。絕對不要悄悄丟掉一個需求。絕對不要不聲不響地擴大版面而不標出來。

**絕對不要**自動產生整份規格，然後當成既成事實丟給使用者。
**絕對不要**在沒有使用者核准的情況下寫入一個章節。
**絕對不要**在沒有標出衝突的情況下，去牴觸一份已核准的既有 UX 規格。
**一定要**顯示決策的出處（GDD 需求、玩家旅程、使用者的選擇）。

Verdict: **COMPLETE** — UX spec written and approved section by section.

---

## Recommended Next Steps

- 跑 `/ux-review [filename]`，在這份規格進入實作 pipeline 之前先驗證它
- 跑 `/ux-design [next-screen]`，繼續設計剩下的畫面或流程
- 所有關鍵畫面都有核准的 UX 規格之後，跑 `/gate-check production`
