---
name: reverse-document
description: "從既有的實作反推出缺少的設計或架構文件：從程式碼和原型往回推。"
argument-hint: "<type> <path> (e.g., 'design src/gameplay/combat' or 'architecture Assets/Scripts/Core')"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash(bash "*/.claude/skills/reverse-document/../../hooks/yaml-helper.sh" resolve_config *)
model: sonnet
# 唯讀的診斷型 skill，不需要委派給專家 agent
---

# Reverse Documentation

這個 skill 會分析既有的實作（程式碼、原型、系統），並產出
適當的設計或架構文件。適合用在這些情況：
- 你做了一個功能，但事先沒寫設計文件
- 你接手了一個沒有文件的程式碼庫
- 你做了一個機制的原型，需要把它正式化
- 你需要記錄既有程式碼背後的「為什麼」

---

## Workflow

## Phase 1: Parse Arguments

**格式**：`/reverse-document <type> <path>`

**Type 選項**：
- `design` → 產出遊戲設計文件（GDD 段落）
- `architecture` → 產出 Architecture Decision Record（ADR）
- `concept` → 從原型產出概念文件

**Path**：要分析的目錄或檔案，位於程式碼根目錄底下：Godot 是 `src/`，
Unity 是 `Assets/`，Unreal 是 `Source/<Module>/`（`.claude/docs/code-root-resolution.md`）
- `src/gameplay/combat/` → 所有戰鬥相關的程式碼（Godot）
- `Assets/Scripts/Core/EventSystem.cs` → 特定檔案（Unity）
- `Source/MyGame/Private/AI/` → 一個模組資料夾（Unreal）
- `prototypes/stealth-mech/` → 原型目錄

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys workflow,system_overrides,automation`

**自動化模式**：解析 `modes.automation`（`project.local.yaml` →
`project.yaml` → 預設 `collaborative`）。每一次 `AskUserQuestion` 呼叫和
每一次寫檔，都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律詢問 · guided 只問重大事項 · autonomous 記錄後直接進行；
屬於 `automation_always_ask` 的類別一律要詢問）。

上面已經解析完畢，直接用。沒有這個區塊的話，預設值看
`.claude/docs/config-resolution.md`。

**解析目標系統的 workflow 等級**：把 `<path>` 對應到一個系統
名稱，如果上面的區塊有列出該系統的 `system_overrides` 那一列，就用它，
否則用專案的 `workflow` 值。它決定要產生多詳細的文件，
見 Phase 5。各等級的語意在
`.claude/docs/workflow-modes.md`。

> **要解析等級，不要假設。** `workflow-modes.md` 定義的是每個等級
> 的*意義*，但它沒辦法告訴你*這個專案*設成哪一級；要從上面的區塊取得。
> 這裡的影響很大：在 `full` 時這個 skill
> 會寫 8 段的 GDD，在 `minimal` 時寫一頁的 brief，等級判錯
> 就整個產出錯誤的東西。

**範例**：
```bash
/reverse-document design src/gameplay/magic-system
/reverse-document architecture Source/MyGame/Private/EntityComponent
/reverse-document concept prototypes/vehicle-combat
```

## Phase 2: Analyze Implementation

**讀懂程式碼/原型**：

**設計文件（GDD）：**
- 找出機制、規則、公式
- 擷取遊戲數值（傷害、冷卻、射程）
- 找出狀態機、技能系統、成長機制
- 偵測程式碼中處理的邊界情況
- 對應依賴關係（哪些系統會互相影響？）

**架構文件（ADR）：**
- 找出模式（ECS、singleton、observer 等）
- 理解技術決策（threading、serialization 等）
- 對應依賴與耦合
- 評估效能特性
- 找出限制和取捨

**概念文件（原型分析）：**
- 找出核心機制
- 擷取湧現式的遊玩模式
- 記下哪些有效、哪些沒效
- 找出技術可行性的洞見
- 記錄玩家幻想 / 手感

## Phase 3: Ask Clarifying Questions

**不要**只是描述程式碼。要**問**意圖：

**設計問題**：
- "I see a [resource] system that depletes during [activity]. Was this for:
  - Pacing (prevent spam)?
  - Resource management (strategic depth)?
  - Or something else?"
- "The [mechanic] seems central. Is this a core pillar, or supporting feature?"
- "[Value] scales exponentially with [factor]. Intentional design, or needs rebalancing?"

**架構問題**：
- "You're using a service locator pattern. Was this chosen for:
  - Testability (mock dependencies)?
  - Decoupling (reduce hard references)?
  - Or inherited from existing code?"
- "I see manual memory management instead of smart pointers. Performance requirement, or legacy?"

**概念問題**：
- "The prototype emphasizes stealth over combat. Is that the intended pillar?"
- "Players seem to exploit the grappling hook for speed. Feature or bug?"

## Phase 3b: Sufficiency Check — is there enough here to document?

**進 Phase 4 之前先跑這一步，沒過就停在這裡。** 這個 skill 是從實作推論出
設計，所以當實作太單薄時，就沒有東西可以拿來推論，
而下面的範本會很樂意接受捏造的內容，因為它每一段都是必填。

計算 Phase 2 實際找到的東西：

| Signal | What counts |
|---|---|
| Mechanics | A named behaviour with observable rules — not a stub, not an empty class |
| Formulas | An expression computing a gameplay value from inputs |
| Values | A tuning constant with a use site |

**如果三個計數都是零，或是目標路徑的非樣板程式碼不到約 20 行，就停下來並說明：**

> "`[path]` does not contain enough implementation to reverse-document.
> Found: [N] mechanics, [N] formulas, [N] tuning values.
> Reverse-documentation infers design from behaviour; with no behaviour to read,
> anything I produce would be invention wearing the format of a design document.
> If the design exists only in your head, `/design-system [name]` is the skill
> that captures it — it asks rather than infers."

**不要在只有部分計數的情況下，把剩下的硬補完再往下走。** 一個有兩個
機制、沒有公式的路徑，就產出一份有兩個機制、並明確寫
`FORMULAS DISCOVERED: none found in the source` 的文件，見 Phase 4。

## Phase 4: Present Findings

動筆起草之前，先把你發現的東西秀出來：

```
I've analyzed [path]/. Here's what I found:

MECHANICS IMPLEMENTED:
- [mechanic-a] with [property] (e.g. timing windows, cooldowns)
- [mechanic-b] (e.g. interaction between two states)
- [resource] system (depletes on [action], regens on [condition])
- [state] system (builds up, triggers [effect])

FORMULAS DISCOVERED:
- [Output] = [formula using discovered variables]
- [Secondary output] = [formula]

UNCLEAR INTENT AREAS:
1. [Resource] system — pacing or resource management?
2. [Mechanic] — core pillar or supporting feature?
3. [Value] scaling — intentional design or needs tuning?

Before I draft the design doc, could you clarify these points?
```

> **上面每一段都可能是空的，空的就要明講。** 在標題下面寫
> `none found in the source`，絕對不要省略標題（那會被解讀成「沒去找」），
> 也絕對不要拿這類系統通常會有的東西來填。方括號裡的列只是*形狀*，不是配額：
> 只有一個機制的原始碼就產出一列，不是四列。
>
> 這在這裡比在一般報告更重要，因為這個 skill 的輸出不是
> 報告，而是**設計文件**，`/design-review`、`/create-epics` 和
> `/create-stories` 會把它當成作者意圖的陳述來讀。GDD 裡一個捏造的
> 公式不會只停留在文件錯誤，它會變成需求，
> 然後變成 story，然後變成為了滿足它而寫的程式碼。

等使用者釐清意圖後再起草。

**如果使用者沒回答 `UNCLEAR INTENT AREAS` 的問題，也不要硬寫出
已經解決的版本。** 這些問題存在的原因是**程式碼不會告訴你為什麼**：
它記錄的是做了什麼，不是想做什麼，而這兩者之間的差距，正是設計文件的全部內容。
沒有回答的項目要原樣帶進草稿，當作文件裡的開放問題，標成
`INTENT UNKNOWN — inferred from implementation, not confirmed`。
把推論出來的意圖當成確定的意圖呈現，就是這整個 skill 的失敗模式。

## Phase 5: Draft Document Using Template

依類型使用適當的範本：

| Type | Template | Output Path |
|------|----------|-------------|
| `design` | `templates/design-doc-from-implementation.md` | `design/gdd/[system-name].md` |
| `architecture` | `templates/architecture-doc-from-code.md` | `docs/architecture/[decision-name].md` |
| `concept` | `templates/concept-doc-from-prototype.md` | `prototypes/[name]/CONCEPT.md` or `design/concepts/[name].md` |

**`design` 的輸出會隨 workflow 等級調整**（在 Phase 1 解析）：
- **`full`**：產出完整的 8 段 GDD。
- **`standard`**：產出 5 段的 GDD（Overview、Detailed Design、Edge Cases、
  Dependencies、Acceptance Criteria；如果還原出來的系統定義了
  數值規則，再加 Formulas）。跳過 Player Fantasy 和 Tuning Knobs。
- **`minimal`**：產出一頁格式的 **game brief**
  （`.claude/docs/templates/game-brief.md`），不是 GDD。整個遊戲
  （路徑就是程式碼根目錄本身）寫成 `design/game-brief.md`；單一個
  反推出來的系統則寫成
  `design/[system-name]-brief.md`。

（`architecture` 和 `concept` 的輸出跟等級無關。）

**草稿結構**：
- 記錄**現有的東西**（機制、模式、實作）
- 記錄**為什麼存在**（跟使用者釐清過的意圖）
- 找出**缺了什麼**（沒處理的邊界情況、設計上的缺口）
- 標出**後續工作**（平衡調整、缺少的功能）

### 標註來源：必做，放在這個 skill 寫出的每份文件最上面

這裡產出的文件，會落在跟設計師手寫文件相同的路徑、相同的格式，
而且**所有下游使用者都會一視同仁地對待它們**。`/design-review` 檢查它是否完整，
`/create-epics` 從它衍生出 epic，`/create-stories` 把它的內容轉成
驗收條件。沒有任何地方會問它是從哪來的。

差別不只是表面上的：手寫的 GDD 陳述的是**意圖**，而這份陳述的是
**觀察到的行為加上推論**。兩者不一致時，前者要改的是程式碼，
後者要改的是文件，而讀的人除非文件自己說明，否則分不出手上拿的是哪一種。

緊接在標題底下輸出這段：

```markdown
> **Reverse-documented from implementation** — generated by `/reverse-document`
> from `[path]` on `[date]`, at commit `[short-sha]`.
> This records what the code **does**; intent marked `INTENT UNKNOWN` below was
> inferred, not confirmed by the author. Where this document and the code
> disagree, do not assume the document is the requirement.
```

修訂時要保留這個橫幅。如果之後有人類確認了意圖，並把這份文件
採納為正式的設計，移除橫幅是他們明確的動作，不是下一次編輯的副作用。

## Phase 6: Show Draft and Request Approval

**協作流程**：
```
I've drafted the [system-name] design doc based on your code and clarifications.

[Show key sections: Overview, Mechanics, Formulas, Design Intent]

ADDITIONS I MADE:
- Documented [mechanic] as "[intent]" per your clarification
- Added edge cases not in code (e.g., what if [resource] hits 0 mid-[action]?)
- Flagged balance concern: [scaling type] scaling at [boundary condition]

SECTIONS MARKED AS INCOMPLETE:
- "[System] interaction with [other-system]" (not fully implemented yet)
- "[Variant or feature]" (only [subset] implemented so far)

May I write this to [output path]?
```

詢問裡要用符合等級的輸出路徑：`full`/`standard` 的 GDD 用 `design/gdd/[system-name].md`，
`minimal` 的 brief 用 `design/[system-name]-brief.md`。

**在 `collaborative`** 時，等待核准；使用者寫檔前可能會要求修改。**在 `guided`** 時，這是*新*檔案，所以 `automation-modes.md:81`
仍然要詢問（"May I write?" 只在新檔案時才問）；如果目標
已經存在，就呈現 diff 並直接進行，不用等明確的
"yes"。**在 `autonomous`** 時，直接寫入並記錄這個決定。

## Phase 7: Write Document with Metadata

核准後，寫入檔案並加上特殊標記：

```markdown
---
status: reverse-documented
source: [path/]
date: [today]
verified-by: [User name]
---

# [System Name] Design

> **Note**: This document was reverse-engineered from the existing implementation.
> It captures current behavior and clarified design intent. Some sections may be
> incomplete where implementation is partial or intent was unclear.

[Rest of document...]
```

## Phase 8: Flag Follow-Up Work

寫完之後，建議下一步：

```
✅ Written to design/gdd/combat-system.md

FOLLOW-UP RECOMMENDED:
1. Run /balance-check on combat formulas (exponential scaling concern)
2. Create ADR for stamina system architecture decision
3. Implement missing edge cases:
   - Stamina depletion mid-combo behavior
   - Stagger state during dodge
4. Extend design doc when weapon variety is implemented

Would you like me to tackle any of these now?
```

---

## Template Selection Logic

| If analyzing... | Use template... | Because... |
|----------------|-----------------|------------|
| `<code root>/gameplay/*` | design-doc-from-implementation.md | Gameplay mechanics → GDD |
| `<code root>/core/*`, `<code root>/ai/*` | architecture-doc-from-code.md | Core systems → ADR |
| `prototypes/*` | concept-doc-from-prototype.md | Experiments → concept doc |
| `<code root>/networking/*` | architecture-doc-from-code.md | Technical systems → ADR |
| `<code root>/ui/*` | design-doc-from-implementation.md | UI/UX → design spec |

---

## Example Session: Reverse-Document a System

```
User: /reverse-document design <code root>/gameplay/[system]

Agent: I'll analyze your [system] implementation to create a design doc.
       [Reads code, discovers mechanics, formulas]

Agent: I've analyzed <code root>/gameplay/[system]/. Here's what I found:
       [Shows mechanics, formulas, unclear areas]

       Before drafting, could you clarify:
       1. [Resource] system intent?
       2. Is [mechanic] a core pillar?
       3. [Value] scaling — intentional or needs tuning?

User: 1. [Resource] is for pacing, prevent [unwanted behavior]
      2. [Mechanic] is core — I want [design intent]
      3. Yeah, exponential is too much, should be linear

Agent: Perfect, that clarifies the vision. Let me draft the design doc.
       [Shows draft with clarified intent]

       May I write this to design/gdd/[system-name].md?

User: Yes, write it.

Agent: ✅ Written to design/gdd/[system-name].md
       ✅ Marked as [REVERSE-DOCUMENTED]
       ✅ Flagged [value] scaling for rebalancing

       Next steps:
       - Update [formula] to [corrected scaling]
       - Run /balance-check to validate [curve]
       - Document [mechanic] as core pillar in game-pillars.md
```

---

## Collaborative Protocol

這個 skill 遵循協作式設計原則：

1. **先分析**：讀程式碼，理解實作
2. **質疑意圖**：問「為什麼」，不只是「是什麼」
3. **呈現發現**：展示你的發現，標出不清楚的地方
4. **使用者釐清**：把意圖和意外分開
5. **起草文件**：根據現實加上意圖來建立文件
6. **展示草稿**：顯示關鍵段落，說明新增的內容
7. **取得核准**："May I write to [filepath]?" 核准時：結論：**COMPLETE**，文件已產生。拒絕時：結論：**BLOCKED**，使用者拒絕寫入。
8. **標出後續工作**：建議相關的工作，不要自動執行

**絕對不要假設意圖。記錄「為什麼」之前，一定要先問。**
