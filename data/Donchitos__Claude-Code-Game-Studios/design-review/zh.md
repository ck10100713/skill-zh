---
name: design-review
description: "審查單一設計文件的完整性、內部一致性、可實作性和設計標準。交給工程師之前使用。"
argument-hint: "[path-to-design-doc] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, Bash(bash "*/.claude/skills/design-review/../../hooks/yaml-helper.sh" resolve_config *), Bash(bash .claude/scripts/review-receipts.sh check *), Bash(bash .claude/scripts/review-receipts.sh hash *), Bash(bash .claude/scripts/gdd-structure-check.sh *), Bash(grep -E '^  - name:' design/registry/entities.yaml), Bash(grep -n -i -E *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,workflow,system_overrides`

上面已經解析好了，直接用；`--review` 會覆蓋 `review_mode`。`--depth` 是
同一個旗標在 1.1 之前的舊名稱：把 `--depth <mode>` 完全當成
`--review <mode>` 處理，並且說一次它已經改名了。兩個都給的話，`--review`
勝出，`--depth` 忽略，並說明這件事。沒有這個區塊 → 用
`.claude/docs/config-resolution.md` 裡的預設值。

# Design Review


## Phase 0: 解析參數


完整的檢查流程見 `.claude/docs/director-gates.md`。各個 gate 的定義放在 `.claude/docs/director-gates/[gate-id].md`，被 spawn 出來的 agent 會自己讀自己的 gate 檔，不要在 parent session 裡讀。


每一次 `AskUserQuestion` 呼叫都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律詢問 · guided 只問重大事項 · autonomous 記錄後直接往下走；
屬於 `automation_always_ask` 的類別一律要問）。

被審查的 GDD 的 **`workflow`**：如果區塊裡有列出 `<system>`，就用它的 `system_overrides` 那一列，否則用專案的值。驗證範圍跟著 tier 走：
- `full`：全部 8 個章節都要驗證；缺任何章節都會擋住核准。
- `standard`：5 個必要章節（Overview、Detailed Rules、Edge Cases、
  Dependencies、Acceptance Criteria）缺了就擋；Formulas 只有在
  系統定義了數值規則（比率、曲線、門檻、成本，
  類別只是提示，不是判斷標準）時才擋；Player Fantasy 和
  Tuning Knobs 只是建議（警告，絕對不擋），除非 `workflow_overrides`
  有要求它們。
- `minimal`：不預期有 GDD；如果有，就以建議的方式驗證
  那 5 個標準章節。

解析後的模式決定這次審查有多徹底：

- **`full`**：完整審查：所有 phase 加上專家 agent 委派（Phase 3b）
- **`lean`**：所有 phase，沒有專家 agent，比較快，單一 session 分析
- **`solo`**：只做 Phase 1-4，不委派，沒有 Phase 5 的下一步提示，從另一個 skill 裡面呼叫時使用

---

## Phase 1: 載入文件

**先做新鮮度檢查，重新審查一份沒變的文件要付全額代價，
而且只會重現同樣的 verdict。** 執行：

```
Bash: bash .claude/scripts/review-receipts.sh check "design/gdd/reviews/[doc-name]-review-log.md" "[target-doc-path]" "design/registry/entities.yaml" ".claude/skills/design-review/SKILL.md"
```

registry 在檢查裡，是因為這次審查會查它的
跨文件事實：沒變的 GDD 對照*變了的*
registry，可能得出不同結論，所以只有在
**每一行**都顯示 `UNCHANGED` 時，跳過才安全（從來不存在的 registry
不會出現在輸出裡，也不會擋住跳過）。這個 skill 的檔案也在裡面，
因為 skill 變了，審查的方式就不同。檢查還會比對
log 蓋過章的其他每個檔案：相關的 GDD、概念或 brief，以及
先前審查讀過的 narrative 檔案，而且對已經不存在的檔案印出 `GONE:`。

然後讀最新一筆紀錄的 `Review mode:` 那行。那次審查只有在它的模式
跟現在解析出的模式相同或更深（`full` > `lean` > `solo`），而且它的 workflow 相同或更深（`full` >
`standard` > `minimal`）時，才**涵蓋**這次執行。沒有那一行的紀錄，
是在那一行出現之前寫的，什麼都不涵蓋。

- **全部 `UNCHANGED`**，而且 log 最新的紀錄帶有 verdict：把它拿出來說：
  *"This document is byte-identical to its last review on [date] ([mode]
  review, verdict: [verdict])."* 如果那個 verdict 是 APPROVED、而且那次審查
  涵蓋這次執行，就透過 `AskUserQuestion` 提供：
  `[A] Use the prior verdict (Recommended)` / `[B] Re-review anyway`：
  `guided` 用 [A] 繼續並註明；`autonomous` 透過
  `log_decision` 記錄，並使用先前的 verdict。如果它是 APPROVED，但現在
  要求的審查比記錄的那次更深，就說出來：*"That was a
  [mode] review at workflow [tier]; this run asks for [mode] at [tier]."*，
  並提供 `[A] Re-review at [mode] (Recommended)` / `[B] Use the prior
  [mode] verdict`；`guided` 和 `autonomous` 會重新審查（`autonomous` 透過 `log_decision` 記錄）。如果它是 NEEDS REVISION 或
  MAJOR REVISION NEEDED，就直說：文件自從審查不過之後
  就沒改過，先前的發現依然成立；下一步是修改文件，不是重新審查。
  主動提議從 log 顯示先前的發現。
- **目標文件和這個 skill 的檔案 `UNCHANGED`，只有 registry 或
  其他有蓋章的跨文件檔案是 `CHANGED`、`NEW` 或 `GONE`**：先前的
  verdict 除了跨文件事實之外依然成立：拿文件的值去對照變了的
  檔案重新驗證，並重新發出 verdict；如果出現衝突，或那次審查沒有涵蓋這次執行，
  就升級成完整的重新審查。
- **目標文件或這個 skill 的檔案是 `CHANGED` 或 `NEW`，或 `RECEIPT: NONE`**：
  繼續下面的完整審查。**不要提供會跳過讀取或重新分析沒變章節的部分／差異式重新審查。**
  以章節為範圍的重新審查
  會漏掉完整審查找得到的缺陷，而且省不了多少甚至沒省。
  「自上次審查以來沒變」只代表
  跟當時審查的東西一模一樣，它並沒有說明
  先前那一輪本身是否完整，而且即使指示要全部掃過，注意力還是會縮到被標記的
  那個變更上。

完整讀目標設計文件。這一步需要整份 GDD：用它的標題（用 Grep 工具找：pattern `^#`、content mode）分段讀，因為超過 40 KB 的整檔 Read 會被拒絕。讀 CLAUDE.md 了解專案的 context 和標準。

**跨文件的事實，優先用 registry，不要讀同層的 GDD。** 如果
`design/registry/entities.yaml` 存在，**而且有列出這個系統的項目**，
就 grep 它：這些是這份 GDD 不准矛盾的既定事實，
用它們就不必去讀同層的 GDD 重新發現：
```
Grep pattern="source: design/gdd/[system].md" path="design/registry/entities.yaml" output_mode="content" -A 6
Grep pattern="design/gdd/[system].md" path="design/registry/entities.yaml" output_mode="content" -B 8
```
第一個找出這個系統**擁有**的項目：`-A 6` 的 context 包含它們的
`referenced_by:` 區塊。第二個找出**參照**這個系統的項目：
`referenced_by:` 是個區塊序列（key 和它的路徑在不同的
行），所以要用 `-B 8` 的 context 比對路徑，才看得到擁有它的項目，不要用
`referenced_by.*name` 這種單行寫法（它永遠比對不到區塊形式）。

**如果 `design/registry/entities.yaml` 不存在，或沒有列出這個
系統的項目**：檔案出貨時是個空的 stub，所以在
`/design-system` 填入之前這是預設情況，就退回去讀目標文件在它的 Dependencies 章節
點名的相關 GDD。讀取範圍限於那些，不要擴大到
所有「隱含」的東西。不要 glob 讀整個 `design/gdd/`。

**依賴圖驗證：** Dependencies 章節裡列出的每個系統，都用 Glob 檢查它的 GDD 檔案是否存在於 `design/gdd/`。標記任何還不存在的，這些是下游作者會踩到的壞掉的參照。

**世界觀／敘事一致性：** 如果 `design/gdd/game-concept.md`（或在 `rigor: minimal` 時，一頁式 brief `design/game-brief.md`）或 `design/narrative/` 裡有任何檔案，就讀它。記下這份 GDD 裡任何牴觸既定世界規則、語氣或設計 pillars 的機制選擇。在 Phase 3b 把這個 context 傳給 `game-designer`。

**先前審查檢查：** 檢查 `design/gdd/reviews/[doc-name]-review-log.md` 是否存在。如果存在，讀最近的一筆，記下給了什麼 verdict、列了哪些擋住的項目。這個 session 是重新審查；追蹤先前的項目有沒有被處理。

---

## Phase 2: 完整性檢查

**Step 2a：用確定性的方式取得章節是否存在（不讀文件）：**

```
Bash: bash .claude/scripts/gdd-structure-check.sh [target-doc-path]
```

它會印出 `PRESENT:` 清單，適用時還有 `ABSENT:` 清單和
`PLACEHOLDER:` 清單（存在、但只有 `[To be designed]` 的章節：還沒
寫，所以在檢查清單裡當成缺少）。它回報的
**只有是否存在**，不做 REQUIRED/ADVISORY 的判斷，那是 Step 2b 的
工作。它已經接受 `## Detailed Design` 滿足 `Detailed Rules`
的要求，所以不要把那個標成缺少。

**Step 2b：套用 tier。** 用 Step 2a 的清單，對照下面的
設計文件標準檢查清單評估。**依解析出的 workflow tier（Phase 0），把每個章節標成 REQUIRED 或
ADVISORY。** 缺少 REQUIRED 章節會擋住核准；缺少 ADVISORY 章節
會當成建議呈現，但不擋。

被回報 PRESENT 的章節，如果只是個空標題，仍然可能審查不過：
verdict 真正取決的章節，要抽查讀一下。

- [ ] 有 Overview 章節（一段摘要）：所有 tier 都是 REQUIRED
- [ ] 有 Player Fantasy 章節（預期的感受）：`full` 是 REQUIRED；`standard` 是 ADVISORY
- [ ] 有 Detailed Rules 章節（不含糊的機制）：`full`/`standard` 是 REQUIRED。GDD 範本把這個章節叫做 `## Detailed Design`（它帶有 Core Rules / States / Interactions 子標題）；接受**任一**標題都算滿足這個要求，當 `## Detailed Design` 章節存在時，不要把 "Detailed Rules" 標成缺少。
- [ ] 有 Formulas 章節（所有數學都用變數定義）：`full` 是 REQUIRED；`standard` 時只要系統定義了數值規則（比率、曲線、門檻、成本、傷害、掉落權重）就是 REQUIRED，否則 ADVISORY。系統的 `Category` 只是提示，不是判斷標準，不要光憑一個類別字眼就放行
- [ ] 有 Edge Cases 章節（處理了不尋常的情況）：`full`/`standard` 是 REQUIRED
- [ ] 有 Dependencies 章節（列出其他系統）：`full`/`standard` 是 REQUIRED
- [ ] 有 Tuning Knobs 章節（找出可設定的值）：`full` 是 REQUIRED；`standard` 是 ADVISORY，除非有 `workflow_overrides.tuning_knobs`
- [ ] 有 Acceptance Criteria 章節（可測試的成功條件）：`full`/`standard` 是 REQUIRED

---

## Phase 3: 一致性與可實作性

**內部一致性：**
- 公式產出的值跟描述的行為相符嗎？
- 邊界情況有跟主要規則矛盾嗎？
- 依賴是雙向的嗎（另一個系統知道這個系統嗎）？

**可實作性：**
- 規則精確到工程師不用猜就能實作嗎？
- 有沒有任何缺少細節的「含糊帶過」章節？
- 有考慮效能影響嗎？
- 每條驗收標準都能獨立測試嗎？把每個不能的都標記出來，
  引用原文，「感覺平衡」、「運作正確」、「效能良好」都不算標準，
  並附上可量測的改寫。在 `full` 模式 `qa-lead` 也會檢查它們
  （Phase 3b）；在 `lean` 和 `solo` 沒有專家執行，所以
  主審查的這個檢查就是唯一的檢查。

**跨系統一致性：**
- 這跟任何既有的機制衝突嗎？
- 這會跟其他系統產生非預期的交互作用嗎？
- 這跟遊戲既定的語氣和 pillars 一致嗎？

**Registry 的值，不管 GDD 在哪裡寫到它們。** 在表格、
目錄項目或變體備註裡重述的值，跟 registry 矛盾的程度
跟寫在 Detailed Rules 裡的一樣，而按章節讀很容易漏看那些內文。列出
registry 的項目名稱（`grep -E '^  - name:' design/registry/entities.yaml`），
然後在整份目標文件裡，一次搜尋所有這些名稱，加上它們帶的數值
key，不分大小寫，把每個 `_` 寫成 `[_ ]`，這樣 `goblin_scout`
也會比對到 "Goblin scouts"：

```
grep -n -i -E 'goblin[_ ]scout|iron[_ ]sword|health|value[_ ]gold' [target-doc-path]
```

不管它在哪個章節，都把它印出的每一行對照 registry 檢查。
任何一行給了項目不同的值，即使只是針對某個房間、變體、關卡
或例外，都跟擁有它的 GDD 矛盾：把它列在 Required Before
Implementation 底下，附上行號、這份文件的值和 registry 的值。
沒有 registry 項目的話，就對相關 GDD 定義的 entity 和數值，跑同樣的搜尋。

---

## Phase 3b: 對抗式專家審查（只限 full 模式）

**在 `lean` 或 `solo` 模式跳過這個 phase。**

**這個 phase 在 full 模式是強制的。** 不准跳過。

**在 spawn 任何 agent 之前**，先印出這個通知：
> "Full review: spawning specialist agents in parallel. This typically takes 8–15 minutes. Use `--review lean` for faster single-session analysis."

### Step 1：找出 GDD 涉及的所有領域

用**已經在 Phase 1 載入**的 GDD，不要再讀一次，找出出現的每個領域。一份 GDD 可以同時涉及多個領域，要徹底。常見的訊號：

| If the GDD contains... | Spawn these agents |
|------------------------|-------------------|
| Costs, prices, drops, rewards, economy | `economy-designer` |
| Combat stats, damage, health, DPS | `game-designer`, `systems-designer` |
| AI behaviour, pathfinding, targeting | `ai-programmer` |
| Level layout, spawning, wave structure | `level-designer` |
| Player progression, XP, unlocks | `economy-designer`, `game-designer` |
| UI, HUD, menus, player-facing displays | `ux-designer`, `ui-programmer` |
| Dialogue, quests, story, lore | `narrative-director` |
| Animation, feel, timing, juice | `gameplay-programmer` |
| Multiplayer, sync, replication | `network-programmer` |
| Audio cues, music triggers | `audio-director` |
| Performance, draw calls, memory | `performance-analyst` |
| Engine-specific patterns or APIs | Primary engine specialist (`<engine>-specialist` from `engine.name` — Godot→`godot-specialist`, Unity→`unity-specialist`, Unreal→`unreal-specialist`; fall back to the Primary line of `## Engine Specialists` in `technical-preferences.md`) |
| Acceptance criteria, test coverage | `qa-lead` |
| Data schema, resource structure | `systems-designer` |
| Any gameplay system | `game-designer` (always) |

凡是描述 gameplay 機制或玩家看得到的規則的 GDD，都要 spawn `game-designer`。
凡是含有公式或系統交互規則的 GDD，都要 spawn `systems-designer`。
這是最常見的基準，但純 UI 規格、音訊規格或世界觀文件不一定需要。用上面的領域表來決定哪些專家真正相關。

### Step 2：平行 spawn 所有相關的專家

**關鍵：這個 skill 裡的 `Agent` 是 spawn 一個 SUBAGENT，一個獨立的、有自己
context window 的 Claude session。它不是任務追蹤。不要在內部模擬專家的
觀點。不要自己推演各領域的看法。你一定要發出
真正的 `Agent` 呼叫。模擬出來的審查不是專家審查。**

同時發出所有 `Agent` 呼叫。不要一個一個 spawn。

**用對抗式的方式對每位專家下指令：**
> "Here is the GDD for [system] and the main review's structural findings so far.
> Your job is NOT to validate this design — your job is to find problems.
> Challenge the design choices from your domain expertise. What is wrong,
> underspecified, likely to cause problems, or missing entirely?
> Be specific and critical. Disagreement with the main review is welcome.
> Read the GDD by section: find the headings with the Grep tool (pattern `^#`,
> content mode) and Read those ranges with offset and limit."

**各 agent 類型的額外指示：**

- **`game-designer`**：把你的審查錨定在這份 GDD 的 Section B 所寫的 Player Fantasy。這個設計真的交付了那個幻想嗎？玩家會感受到預期的體驗嗎？標出任何為了可實作性、卻損害所述感受的規則。

- **`systems-designer`**：GDD 裡的每個公式，都代入邊界值（合理輸入的最小值和最大值）。回報有沒有任何輸出退化，也就是負值、除以零、無限大，或是在極端情況下沒有意義的結果。

- **`qa-lead`**：審查每條驗收標準。標出任何不能獨立測試的，像「感覺平衡」、「運作正確」、「效能良好」這類說法都不是 AC。對沒通過這個測試的，建議具體的改寫。

### Step 3：資深主管審查

所有專家都回應之後，spawn `creative-director` 當作**資深審查者**：
- 提供：GDD、所有專家的發現、他們之間的任何分歧
- 問："Synthesise these findings. What are the most important issues? Do you agree with the specialists? What is your overall verdict on this design — APPROVED, NEEDS REVISION or MAJOR REVISION NEEDED?"
- creative-director 的綜合結論，就是 Phase 4 的**最終 verdict**，用這個 skill 的 verdict 用詞，絕對不用像 READY 或 REJECT 這種 director-gate 的用詞。

### Step 4：呈現分歧

如果專家彼此意見不同，或跟 creative-director 意見不同，絕對不要默默挑一邊。在 Phase 4 明確呈現這個分歧，讓使用者裁決。

每個發現都要標上來源：`[game-designer]`、`[economy-designer]`、`[creative-director]` 等。

---

## Phase 4: 輸出審查結果

```
## Design Review: [Document Title]
Specialists consulted: [list agents spawned]
Re-review: [Yes — prior verdict was X on YYYY-MM-DD / No — first review]

### Completeness: [X/N sections present, where N is the count REQUIRED at this project's `modes.workflow`]
[List only sections missing that are REQUIRED at this tier. Mark ADVISORY gaps
separately as "advisory at `standard`" — do not list them as missing.]

> **N is not 8 unless `workflow: full`.** The tier table earlier in this skill is
> authoritative: 8 required at `full`, 5 at `standard` (+ Formulas when the system
> defines numeric rules), 0 at `minimal`. Do not hardcode `/8` here: reporting a
> `standard` project as "5/8 missing Player Fantasy, Formulas, Tuning Knobs"
> warns about three sections that project's own configuration says it does not
> need, which trains the reader to ignore the review.

### Dependency Graph
[List each declared dependency and whether its GDD file exists on disk]
- ✓ enemy-definition-data.md — exists
- ✗ loot-system.md — NOT FOUND (file does not exist yet)

### Registry Values
[The whole-document search from Phase 3: the terms searched, how many lines it
printed, and each conflict with its line number. With nothing to search, say so:
"No registry entries or related-GDD values: values not cross-checked."]

### Required Before Implementation
[Numbered list — blocking issues only. Each item tagged with source agent.]

### Recommended Revisions
[Numbered list — important but not blocking. Source-tagged.]

### Specialist Disagreements
[Any cases where agents disagreed with each other or with the main review.
Present both sides — do not silently resolve.]

### Nice-to-Have
[Minor improvements, low priority.]

### Senior Verdict [creative-director]
[Creative director's synthesis and overall assessment.]

### Scope Signal
Estimate implementation scope based on: dependency count, formula count,
systems touched, and whether new ADRs are required.
- **S** — single system, no formulas, no new ADRs, <3 dependencies
- **M** — moderate complexity, 1-2 formulas, 3-6 dependencies
- **L** — multi-system integration, 3+ formulas, may require new ADR
- **XL** — cross-cutting concern, 5+ dependencies, multiple new ADRs likely
Label clearly: "Rough scope signal: M (producer should verify before sprint planning)"

### Verdict: [APPROVED / NEEDS REVISION / MAJOR REVISION NEEDED / NOT ASSESSED]

> **`NOT ASSESSED` when the review could not actually be performed.**
> The other three verdicts are all claims about the design's quality, so each one
> asserts that the document was read and judged. Use `NOT ASSESSED` instead when
> the target document is absent, unreadable, or empty of the sections being
> reviewed, or when a document it depends on is missing so the criteria cannot be
> applied. **Name what was unavailable and which skill produces it.**
>
> `APPROVED` is the dangerous default here: a review that could not find its
> input has not approved anything, and this verdict is consumed downstream as a
> sign-off. `NOT ASSESSED` outranks `APPROVED` in any aggregate — it does not
> outrank the two revision verdicts, because a known problem is more actionable
> than an unknown one.
```

這個 skill 是唯讀的，Phase 4 期間不會寫任何檔案。

---

## Phase 5: 下一步

所有收尾的互動都用 `AskUserQuestion`。絕對不要用純文字。

**第一個 widget：接下來做什麼：**

如果是 APPROVED（第一次就過，不需要修改），直接進 systems-index widget、review-log widget，然後是最後的收尾 widget。不要顯示獨立的「要做什麼」widget，最後的收尾 widget 已經涵蓋下一步。

如果是 NOT ASSESSED，什麼都沒審查：不提供追蹤更新，直接進
最後的收尾 widget，把產出缺少輸入的 skill 放在最前面
（例如，GDD 不存在時用 `/design-system [system]`）。

如果是 NEEDS REVISION 或 MAJOR REVISION NEEDED，根據發現建立選項：
- `[A] Revise the GDD now — address blocking items together`
- `[B] Stop here — revise in a separate session`
- `[C] Accept as-is and move on`：只有當每個發現都只是建議
  （Required Before Implementation 是空的）時才放。有任何擋住的項目，
  就只提供 [A] 和 [B]。

**如果使用者選 [A]：現在修改：**

處理所有擋住的項目，只有在光靠 GDD 和現有文件解決不了問題時，才請教設計決策。把所有設計決策的問題集中成單一的多分頁 `AskUserQuestion`，之後才動手改，不要在修改到一半時，為每個擋住的項目各別打斷。

所有修改完成之後，顯示一張摘要表（擋住的項目 → 套用的修正），並用 `AskUserQuestion` 做**修改後的收尾 widget**：

- Prompt："Revisions complete — [N] blockers resolved. What next?"
- 註明目前的 context 使用量：如果 context 超過 ~50%，就加上："(Recommended: /clear before re-review — this session has used X% context. A full re-review runs 5 agents and needs clean context.)"
- 選項：
  - `[A] Re-review in a new session — run /design-review [doc-path] after /clear`
  - `[B] Accept revisions for now — mark In Review in the systems index; a re-review decides Approved`
  - `[C] Move to next system — /design-system [next-system] (#N in design order)`
  - `[D] Stop here`

在 collaborative 和 guided 模式，絕對不要用純文字結束修改流程，
一定要用這個 widget 收尾。在 autonomous 模式，摘要結果並
用 `log_decision` 記錄。

**第二個 widget：追蹤紀錄（合併，用於 APPROVED 路徑）：**

verdict 是 APPROVED 時，用單一個帶 `multiSelect: true` 的 `AskUserQuestion`，把兩個追蹤更新合在一起：
- Prompt："Verdict: APPROVED. I can update the tracking records now. Select any you'd like me to complete:"
- 選項：
  - `Update systems-index.md status to 'Approved' for [system]`
  - `Append approval entry to design/gdd/reviews/[doc-name]-review-log.md`

如果選了 review-log 的選項，就用下面同樣的格式附加。在顯示最後的收尾 widget 之前，先執行選取的兩個動作。

verdict 是 NEEDS REVISION 或 MAJOR REVISION NEEDED 時，照之前那樣用各別的 widget：

用第二個 `AskUserQuestion`：
- Prompt："May I update `design/gdd/systems-index.md` to mark [system] as [Needs Revision / In Review]?"：修改還沒完成時是 `Needs Revision`（就是這個字串），修改套用完、等重新審查時是 `In Review`。這個提示絕對不提供 `Approved`：需要修改的 verdict 不是核准。
- 選項：`[A] Yes — update it` / `[B] No — leave it as-is`

用第三個 `AskUserQuestion`：
- Prompt："May I append this review summary to `design/gdd/reviews/[doc-name]-review-log.md`? This creates a revision history so future re-reviews can track what changed."
- 選項：`[A] Yes — append to review log` / `[B] No — skip`

回答 yes 的話，用這個格式附加一筆紀錄：
```
## Review — [YYYY-MM-DD] — Verdict: [APPROVED / NEEDS REVISION / MAJOR REVISION NEEDED]
Review mode: [full / lean / solo] · Workflow: [full / standard / minimal]
Scope signal: [S/M/L/XL]
Specialists: [list]
Blocking items: [count] | Recommended: [count]
Summary: [2-3 sentence summary of key findings from creative-director verdict]
Prior verdict resolved: [Yes / No / First review]
Findings:
- [BLOCKING] [section]: [one-line finding]
- [RECOMMENDED] [section]: [one-line finding]
[output of: Bash: bash .claude/scripts/review-receipts.sh hash "[target-doc-path]" "design/registry/entities.yaml" ".claude/skills/design-review/SKILL.md" [every other file this review read for cross-document facts: the related GDDs in design/gdd/, design/gdd/game-concept.md or design/game-brief.md, the design/narrative/ files] — a file that does not exist prints `not stamped, no such file` and is left out]
```

Findings 的規則：每個發現一行，用它所在的章節命名；
verdict 沒有任何發現時就寫 `- none`。這是寫給修訂歷史的
人類讀者看的文件，不是這個 skill 會讀回來的機制。

hash 那行是 Phase 1 下次執行時讀的收據，用來偵測一模一樣的
重新審查，這是唯一真正安全的跳過形式，
因為輸入可證明是相同的，而不是只被相信
已經被先前一輪充分涵蓋。審查讀過的每個檔案都要蓋章：
Phase 1 的檢查下次執行時會比對每個蓋過章的檔案，不管它有沒有點名。不管 verdict 是什麼都一定要放：一份
沒變、而且先前審查不過的文件，正是跳過多餘的重新審查省最多的情況
（先前的發現原封不動地成立）。

---

**最後的收尾 widget：所有檔案寫入完成後一定要顯示：**

systems-index 和 review-log 的 widget 都回答之後，檢查專案狀態，並顯示最後一個 `AskUserQuestion`：

建立選項之前，先讀：
- `design/gdd/systems-index.md`：找出（剛審查的那個以外）Status 是 In Review 或 Needs Revision 的任何系統。按章節讀：用 Grep 工具（pattern `^#`、content mode）找出標題，再用 offset 和 limit 讀那幾段範圍。
- 數 `design/gdd/` 裡的 `.md` 檔案（排除 game-concept.md、systems-index.md），判斷 `/review-all-gdds` 值不值得提供（≥2 份 GDD）
- 依設計順序找下一個 Status 是 Not Started 的系統

動態建立選項清單，只放真正是下一步的選項：
- `[_] Run /design-review [other-gdd-path] — [system name] is still [In Review / Needs Revision]`（有另一份 GDD 需要審查就放）
- `[_] Run /consistency-check — verify this GDD's values don't conflict with existing GDDs`（有 ≥1 份其他 GDD 就一定放）
- `[_] Run /review-all-gdds — holistic design-theory review across all designed systems`（有 ≥2 份 GDD 就放）
- `[_] Run /design-system [next-system] — next in design order`（一定放，要寫出實際的系統名稱）
- `[_] Stop here`

字母 A、B、C… 只分配給放進去的選項。把最能推進 pipeline 的那個選項標成 `(recommended)`。

在 collaborative 和 guided 模式，檔案寫入之後絕對不要用純文字結束這個 skill，
一定要用這個 widget 收尾。在 autonomous 模式，印出下一步並
用 `log_decision` 記錄。
