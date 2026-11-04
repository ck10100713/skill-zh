---
name: create-stories
description: "把一個 epic 拆成可實作的 story，附驗收標準。使用者想要某個 epic 的 story，或下一批要做的工作時使用。不適用於把整份設計拆成 epic。"
argument-hint: "[epic-slug | epic-path] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, Bash(bash "*/.claude/skills/create-stories/../../hooks/yaml-helper.sh" resolve_config *), Bash(bash .claude/scripts/adr-status.sh *), Bash(bash .claude/scripts/md-section.sh extract *), Bash(bash .claude/scripts/md-section.sh list *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,review_gate,automation,workflow,docs.density,story_granularity,qa.level,system_overrides`

上面已經解析好了，直接用；`--review` 會覆蓋 `review_mode`。沒有這個區塊 →
用 `.claude/docs/config-resolution.md` 裡的預設值。

提問要用提問工具。沒有的話，把選項編號列出來，然後結束你這一輪
等回覆。被跳過或被關掉的問題不算回答：用純文字再問一次。

# Create Stories

story 是一個可實作的行為：小到符合 `story_granularity` 設定的大小、
自成一體，並且能追溯到一條需求和主導它的
決策。每個 epic 跑一次這個 skill，依依賴順序：
先 Foundation epic，然後 Core、Feature、Presentation。

**寫入：** `production/epics/[epic-slug]/story-NNN-[slug].md`、該 epic 的
`EPIC.md` Stories 表，以及它在 `production/epics/index.md` 的那一列。
**下一步：** `workflow: minimal` 時用 `/dev-story [story-path]`；否則
先 `/story-readiness [story-path]`，再 `/dev-story`。

提問遵循 `.claude/docs/automation-modes.md`（collaborative 一律會問、guided
遇到重大選擇才問、autonomous 記錄後繼續；`automation_always_ask`
的類別一律要問）。

檢查清單（複製下來，邊做邊打勾）：

```
- [ ] Phase 1: epic found, tier resolved
- [ ] Phase 2: inputs loaded, each ADR's status reported
- [ ] Phase 3-4: stories drafted, typed, Ready or Blocked
- [ ] Phase 5: QA lead review run, or its skip noted
- [ ] Phase 6: story list shown, one ask to write
- [ ] Phase 7: stories, EPIC.md and index.md written (or index absence said)
- [ ] Phase 8: next step asked, closing block printed
```

## Phase 1: Epic 與設定

**Tier。** 這個 epic 所屬系統的 `workflow`：如果有 epic slug
（它的 GDD 系統）對應的 `system_overrides` 那一列，就用那一列，否則用專案的值。

**`story_granularity`** 決定每個 story 的驗收標準負載。把標準
合併或拆分來達到它：

| `story_granularity` | ACs per story | Size |
|---|---|---|
| `coarse`（預設，`rigor: minimal`） | 5-10 | 一整個功能，要好幾天 |
| `balanced`（`rigor: standard`） | 2-4 | 一個 task，大約一個 session |
| `fine` | 1 | 一條標準；story 名稱就是把它重述一遍 |

**`docs.density`** 決定每個 story 文字說明（context、實作
筆記、ADR 摘要）的深度，絕對不影響 AC 的數量或 AC 的文字：`terse`（預設）= 條列
筆記，沒有開場白；`balanced` = 一小段 context 加筆記；`thorough` =
完整的 context、指引和 ADR 理由。TR-ID、ADR Version 和驗收
標準絕對不能刪減。

**哪個 epic。** skill 名稱後面輸入的文字，把任何 `--review <mode>`
組合拿掉之後：一個 epic slug（`combat`）或一個路徑（`production/epics/combat/EPIC.md`）。
什麼都沒輸入時，使用者的要求裡點名的 epic（「the loot epic」）就算有指名。

- **有指名，但那裡沒有 `EPIC.md`：** 在 `standard` 和 `full`，停："No epic at
  `production/epics/[slug]/EPIC.md`. Run `/create-epics` to create it, or check the
  slug with `ls production/epics/`." 絕對不要憑猜測去拆。在 `minimal`，
  說明這個 tier 不需要 `/create-epics` 的 epic，走 Phase 2 的 `minimal` 分支，
  並點名它用的 slug。
- **`minimal` 時沒給：** 走 Phase 2 的 `minimal` 分支。
- **`standard` 或 `full` 時沒給：** 列出 `production/epics/*/EPIC.md` 以及每個的
  狀態，然後問："Which epic would you like to break into stories?"，每個 epic 一個
  選項。**找不到 epic：** 停並說 "No epics found under
  `production/epics/`. Run `/create-epics layer: foundation` first." 絕對不要問
  一個沒有選項的問題。

## Phase 2: 載入輸入

### `minimal`：從 brief 建立 epic

1. **沒有 `design/game-brief.md`：** 停。"There is no brief to build stories from
   yet: run `/brainstorm` first; it writes the one-page brief." 如果 code root
   已經有這款遊戲了（10 個以上原始碼檔案），就改點名 `/reverse-document design
   [code root]`。
2. 完整讀 `design/game-brief.md`（一頁）。
3. **Epic。** `<slug>` 是 brief 的 working title 轉成 slug（沒有的話就是 `mvp`），
   或是使用者指名的 epic。
   - `production/epics/<slug>/EPIC.md` 已存在：它就是 epic。使用它的範圍，仍然
     追溯到 brief，絕對不要重寫它。
   - 不存在：起草一份，只在 Phase 6 的詢問點名它之後，才在 Phase 7 寫入。
     目標 = brief 的一句話 pitch；範圍 = 它的 MVP 功能清單；
     順序 = 它的 **Build order**。保持精簡。
   - 資料夾裡已經有 story（回頭再來）：絕對不要重寫既有的
     `story-*.md`。只替 brief 裡它們沒涵蓋的項目，或使用者點名的新項目加 story，
     編號從現有最大的 `story-NNN` 接下去。
4. **每個 MVP 功能一個 story，依 Build order**，每個都追溯到 brief。沒有
   story 會因為 ADR 的理由被擋住：這個 tier 沒有 ADR。

`minimal` 時不讀 GDD、control manifest、TR registry 或 ADR。進 Phase 3。

### `standard` 和 `full`：epic 和主導它的東西

1. **Epic：** 完整讀 `production/epics/[epic-slug]/EPIC.md`（它的分層、GDD、
   主導的 ADR，以及帶有 TR-ID 的 GDD Requirements 表）。
2. **GDD：** 按標題讀它的章節，絕對不要整份讀：
   `bash .claude/scripts/md-section.sh extract design/gdd/[file].md "Acceptance Criteria"`，
   `Formulas`、`Edge Cases` 和 `Detailed Design` 也一樣（exit 3：試 `Detailed Rules`，
   設計標準對同一個章節的稱呼）；在 `full`
   其他必要章節也要讀（`list` 會顯示標題）。
3. **Control manifest：** 只讀這個 epic 的分層，以及版本：
   `bash .claude/scripts/md-section.sh extract docs/architecture/control-manifest.md "[Layer] Layer Rules"`，
   加上它的 `Manifest Version` 那行。
4. **TR registry：** 只讀這個系統的項目：在
   `docs/architecture/tr-registry.yaml` 裡，符合 `system: <slug>\s*$` 的那些行，
   連同每個項目上面的 `id` 和下面的文字。錨點讓 `combat` 不會
   比對到 `combat-ai`；`\s*` 處理 Windows 的換行字元。
5. **ADR**，epic 提到的每一個（主導的，或在它的需求表裡的，
   包含 Proposed 的），一次呼叫：
   ```
   bash .claude/scripts/adr-status.sh ADR-0001 ADR-0003 ...
   ```
   每一列給出狀態、分層、`version`（story 的 ADR Version 戳記）、
   `depends_on`，以及缺少的章節。然後只讀每個 ADR 的 `Summary`、`Decision`（裡面的
   Implementation Guidelines）和 `Engine Compatibility`，用
   `md-section.sh extract`。Engine Notes 是 story 的欄位，取自 Engine
   Compatibility，不是 ADR 的章節。這些章節都沒有的 ADR 早於
   範本：讀它一次，並標記它要用 `/architecture-decision retrofit
   [file]` 處理。

**被指名的 ADR 沒有檔案**（`NOT_FOUND`）：

- `full`：在拆任何 story 之前就停。
- `standard`：只有它是關鍵的（Foundation 層）才停；否則警告、繼續，並把
  它主導的 story 寫成 `Blocked`，直到它存在。
- 停下來時："Epic references [ADR-NNNN: title] but no file for it was found in
  `docs/architecture/`. Check the epic's Governing ADRs list, or run
  `/architecture-decision` to create it. Cannot create stories until the
  referenced ADR files exist."

**起草之前先回報**，反映真實狀態，每個 ADR 單獨列出，附上它的
狀態：

```
Loaded: epic [name] · GDD [file] · manifest v[date], [layer] rules
ADRs: ADR-0001 Accepted · ADR-0002 Accepted · ADR-0003 Accepted · ADR-0004 Proposed · [ADR-NNNN missing]
```

絕對不要在有一個缺少時說 "all present"，也不要在根本沒有時點名 manifest 版本。

## Phase 3: 替每個 story 分型

| Type | When its criteria reference |
|---|---|
| **Logic** | 公式、門檻、狀態轉換、AI 決策、計算 |
| **Integration** | 兩個以上的系統、跨邊界的 signal、存讀檔的來回流程 |
| **Visual/Feel** | 動畫、VFX、「手感靈敏」、時間點、螢幕震動、音訊同步 |
| **UI** | 選單、HUD、按鈕、畫面、對話框、tooltip |
| **Config/Data** | 只有平衡數值和資料檔，沒有新邏輯 |

混合型的 story 取實作風險最高的那個型。型別決定
`/story-done` 需要的證據。

## Phase 4: 起草 story

把需要同樣核心實作的需求歸成一個 story，負載符合
`story_granularity`。順序：基礎行為先、邊界情況在後、
UI 最後。每個 story：

- **Requirement：** registry 的 TR-ID，透過 epic 的 GDD
  Requirements 表對應。只有在沒有項目符合時，才寫 `TR-[system]-???` 並
  說明這件事。
- **ADR：** 主導怎麼實作它的那個（需求表會點名它）。
  - `Accepted`：嵌入它。
  - `Proposed`：`Status: Blocked`，並寫 "BLOCKED: ADR-NNNN is Proposed — accept it
    with `/architecture-decision accept ADR-NNNN` once decided"。
  - `Deprecated` 或 `Superseded`：`Status: Blocked`，並寫 "BLOCKED: ADR-NNNN is
    [status] — point the story at [successor] (edit its ADR field;
    `/create-stories` never rewrites an existing story) before implementing"。
  - `Accepted` 的 ADR，但它的 `depends_on` 點名的 ADR 不是 Accepted：用同樣方式標成
    Blocked，並點名那個 ADR。
  - 適用的有好幾個：全部列出，最直接的放前面。
  - 都不適用：`ADR: N/A — [reason]`，例如 "pure data configuration"。絕對不能
    留白：留白代表沒檢查過。
- **ADR Version：** story 的 **ADR Version** 是 ADR 的 `## Last Verified`
  日期，沒有就用它的 `## Date`，再沒有就是 `unversioned`（`version` 欄）。`/dev-story`
  在這個版本仍然對得上 ADR 時，會信任 story 的 ADR 摘要。
- **Engine risk：** 取自 ADR 的 Engine Compatibility（它的知識風險）。
- **Estimate：** 根據標準和 story 會動到的檔案，提出一個 t-shirt 尺寸：
  `S`（幾小時）、`M`（大約一天）或 `L`（好幾天）。這只是
  提案：Phase 6 會顯示它，使用者可以改。`/story-readiness` 會讓
  Estimate 還是範本括號的 story 不通過，所以絕對不能留著。

## Phase 5: QA lead 審查

讀上面的 `review_gate` 那行。`skill-gates=skip`（solo 或 lean）：不審查；
在 Phase 6 的清單和收尾區塊註明 "QL-STORY-READY skipped — [Solo | Lean] mode"。`skill-gates=run`：讀 `references/qa-lead-gate.md` 和
`.claude/docs/director-gates.md`，並現在就執行，在 Phase 6 的詢問之前。跳過的話，
不要載入它。

## Phase 6: 顯示 story，問一次

```
## Stories for Epic: [name]
ADRs: ADR-0001 Accepted · ADR-0002 Accepted · ADR-0004 Proposed   (every ADR, from Phase 2)

Story 001: [title] — Logic — ADR-0001 — Ready — Estimate M
  Covers: TR-[system]-001 ([one-line requirement])
  Test required: tests/unit/[system]/[slug]_test.[ext]

Story 002: [title] — Integration — ADR-0004 — BLOCKED (ADR-0004 is Proposed) — Estimate L
  Covers: TR-[system]-002, TR-[system]-003
  Test required: tests/integration/[system]/[slug]_test.[ext]

Story 003: [title] — Visual/Feel — ADR-0001 — Ready — Estimate S
  Covers: TR-[system]-004
  Evidence required: retained screenshot + sign-off in production/qa/evidence/[slug]-evidence.md

[N stories: N Logic, N Integration, N Visual/Feel, N UI, N Config/Data; N Blocked]
QL-STORY-READY: [skipped — Solo mode | its verdicts]
```

在 `minimal`，每一行追溯到 `Brief MVP feature N`，沒有 ADRs 那行，而且
每個 MVP 功能一個 story：不為 MVP 清單以外的 brief 項目加額外的 story。然後
問："May I write these [N] stories to `production/epics/[epic-slug]/`, and
[create | update] `production/epics/[epic-slug]/EPIC.md` and update
`production/epics/index.md`?" 選項：Yes, write all [N] / Not yet, I want to
adjust first；調整可以改任何一個 estimate。要點名 Phase 7 動到的每個檔案：只有在
`EPIC.md` 不存在時才 *create* 它，而 `index.md` 不存在時就不要把它列進去。在 yes 之前什麼都不寫。

## Phase 7: 寫入

### story 檔案

**每個 story** 是 `production/epics/[epic-slug]/story-[NNN]-[slug].md`，格式
依照 `.claude/docs/templates/story.md`。絕對不要重複使用 story 編號。每個檔案都
當成檔案來寫，絕對不要透過 shell 指令：用 shell 寫入會跳過專案的寫入檢查。

在 `minimal` 沒有 GDD、ADR、TR registry 或 manifest。這些欄位要
照下表填：

| Field | Value at `minimal` |
|---|---|
| GDD | `design/game-brief.md` |
| Requirement | `Brief MVP feature N`，絕對不是 TR-ID |
| ADR Governing Implementation, ADR Decision Summary, ADR Version | `N/A (minimal — no ADRs)` |
| Manifest Version, Control Manifest Rules | `N/A (minimal — no control manifest)` |
| Engine | `engine.name` + `engine.version` |
| Risk | `docs/engine-reference/<engine>/VERSION.md` 對釘住版本給的等級（它的時間軸那一列，或它的整體評級）。沒有檔案或沒有等級：`NOT ASSESSED (no VERSION.md risk rating)`，絕對不要猜。`/dev-story` 會把 NOT ASSESSED 讀成 HIGH |
| Engine Notes | `none (no ADR engine-compatibility analysis at minimal)` |
| Acceptance Criteria | 來自 brief 的 **Player goal & fail state** 和 MVP 功能，寫成具體、可測試的；絕對不要憑一個光禿禿的條列項目編出來 |

每個 tier 都一樣：
- **QA Test Cases：** 當審查被跳過時，寫
  `*N/A — no qa-lead specs at this tier; implement against the Acceptance Criteria above*`。
  絕對不要自己即興編測試案例。
- **Test Evidence：** 由 `qa.level` 決定。`qa.level: minimal` 時測試
  被免除（只供參考），但 Visual/Feel 或 UI story 保留的截圖不能免。
- **Estimate：** Phase 6 的尺寸，加上使用者做的任何更改。
- **Dependencies：** 用路徑點名這個 story 需要的每個 story。
- **Files：** story 計畫建立或修改的程式碼和測試檔案，
  在 code root 和 test root 底下。`/dev-story` 會用真實的清單取代它們。

### `EPIC.md`

在 `minimal` 還沒有的話，寫 Phase 2 的草稿，加上下面的
表格。否則把它的 "Stories: Not yet created" 那行換成表格，或是
回頭再來時，每個新 story 附加一列，其餘檔案保持
原樣：

```markdown
## Stories

| # | Story | Type | Status | ADR |
|---|-------|------|--------|-----|
| 001 | [title] | Logic | Ready | ADR-0001 |
| 002 | [title] | Integration | Blocked | ADR-0004 |
```

### `production/epics/index.md`

把這個 epic 的 `Stories` 欄設成 `[N] stories`，
也就是這次執行之後這個 epic 的總數。檔案不存在時，要說明：
`Epics index not updated: production/epics/index.md absent`。

## Phase 8: 收尾

如果 `production/epics/` 裡有其他 epic 還沒有 story，就列出來。然後問：
"[N] stories written to `production/epics/[epic-slug]/`. What next?" 選項，列出適用的：

- 開始實作：`minimal` 時是 `/dev-story [first-story-path]`，
  否則是 `/story-readiness [first-story-path]`（建議）
- 為 [next epic] 建立 story：`/create-stories [slug]`（只有當某個 epic
  還沒有 story 時）
- 規劃 sprint：`/sprint-plan new`（只有當每個 epic 都有 story 時；`minimal`
  絕對不放，那時 brief 的 build order 就是計畫）
- 這個 session 到此為止

絕對不要開始實作或寫程式：這個 skill 停在 story 檔案。
驗收標準來自 GDD（`minimal` 時是 brief）、實作
筆記來自 ADR、規則來自 manifest；沒有一個是編出來的。

**這次執行的最後一則回覆要以這個區塊結尾**，在上面的問題
被回答之後（如果之前顯示過，就再重複一次）：

```
Verdict: COMPLETE — [N] stories written to production/epics/[epic-slug]/ ([N] Ready, [N] Blocked)
Review: [QL-STORY-READY skipped — Solo mode | skipped — Lean mode | its verdicts]
Index: [production/epics/index.md updated | Epics index not updated: production/epics/index.md absent]
Next step: [/dev-story [first-story-path] | /story-readiness [first-story-path]]
```

使用者拒絕寫入時：`Verdict: BLOCKED — user declined. No story
files written.`
