---
name: create-architecture
description: "在寫程式之前撰寫架構藍圖。拿釘住版本的引擎驗證各項決策，標出知識缺口。"
argument-hint: "[focus-area: full | layers | data-flow | api-boundaries | adr-audit] [--review full|lean|solo]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Agent, Bash(bash "*/.claude/skills/create-architecture/../../hooks/yaml-helper.sh" resolve_config *), Bash(bash .claude/scripts/registry.sh *)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,workflow,docs.density`

上面已經解析好了，直接用；`--review` 會覆蓋 `review_mode`。沒有這個區塊 →
用 `.claude/docs/config-resolution.md` 裡的預設值。

# Create Architecture

這個 skill 產出 `docs/architecture/architecture.md`，也就是把所有核准過的 GDD
轉成具體技術藍圖的主架構文件。
它介於設計和實作之間，而且在 sprint planning 開始之前就必須存在。

**跟 `/architecture-decision` 不一樣**：ADR 記錄的是單一個別的決策。
這個 skill 建立的是整個系統的藍圖，替 ADR 提供脈絡。

完整的檢查流程見 `.claude/docs/director-gates.md`。各個 gate 的定義放在 `.claude/docs/director-gates/[gate-id].md`，被 spawn 出來的 agent 會自己讀自己的 gate 檔，不要在 parent session 裡讀。

每一次 `AskUserQuestion` 呼叫都要遵守 `.claude/docs/automation-modes.md`
（collaborative 一律詢問 · guided 只問重大事項 · autonomous 記錄後直接往下走；
屬於 `automation_always_ask` 的類別一律要問）。

**`docs.density`**：控制每個章節的*深度*，`workflow`
則控制有哪些章節。`modes.rigor` 會同時設定兩者；要只調整深度的話，
就明確設定 `docs.density`：`terse`（預設，來自 `rigor: minimal`）= 分層圖加決策條列，
不寫長篇大論；`balanced` = 圖加上對分層選擇的段落說明
（`rigor: standard`）；`thorough` = 完整散文，每一層都附理由、取捨，和考慮過的
替代方案。你寫的每個章節都要套用這個設定。

**`workflow`**（見 `.claude/docs/workflow-modes.md`）：
- `full`：完整架構：所有分層、模組歸屬、資料流、API
  邊界、完整的 ADR 稽核。
- `standard`：簡化版：只有系統分層圖加上關鍵 ADR 清單。
- `minimal`：不需要。仍然可以自願執行。

**參數模式：**
- **沒有參數 / `full`**：完整的引導式逐步走過：所有章節，從頭到尾
- **`layers`**：只聚焦在系統分層圖
- **`data-flow`**：只聚焦在模組之間的資料流
- **`api-boundaries`**：只聚焦在 API 邊界定義
- **`adr-audit`**：只稽核既有 ADR 有沒有引擎相容性的缺口

---

## Phase 0: 載入所有 Context

**現在就讀 `references/0-load-context.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復過，要再讀一次。

## Phase 1: 系統分層對應

**現在就讀 `references/1-layers.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復過，要再讀一次。

## Phase 2: 模組歸屬圖

**現在就讀 `references/2-module-ownership.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復過，要再讀一次。

## Phase 3: 資料流

**現在就讀 `references/3-data-flow.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復過，要再讀一次。

## Phase 4: API 邊界

**現在就讀 `references/4-api-boundaries.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復過，要再讀一次。

## Phase 5: ADR 稽核 + 可追溯性檢查

**現在就讀 `references/5-adr-audit.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復過，要再讀一次。

## Phase 6: 缺少的 ADR 清單

**現在就讀 `references/6-missing-adrs.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復過，要再讀一次。

## Phase 7: 寫出主架構文件

**現在就讀 `references/7-write.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復過，要再讀一次。

## Phase 8: 交接

**現在就讀 `references/8-handoff.md` 並照著做**：這個 phase 的步驟在那個檔案裡，不在這裡。如果對話在這個 phase 期間被壓縮或恢復過，要再讀一次。

## 協作協定

**在 `collaborative` 模式（預設）下適用。** `guided` 和
`autonomous` 模式見 `.claude/docs/automation-modes.md`，下面這些規則
描述的是 collaborative 模式的要求，不是通用行為。

這個 skill 在每個 phase 都遵循協作設計原則：

1. **靜默載入 context**：不要把讀檔案的過程講出來
2. **呈現發現**：給使用者看知識缺口清單和分層提案
3. **決定之前先問**：每個架構選擇都先提出選項
4. **先起草，核准在後**：在問是否寫入之前，先把內容直接顯示出來。
   使用者還沒看過的章節，絕對不要要求核准。
5. **寫入的核准用 `AskUserQuestion`**：純文字的 "May I?" 不夠。
   要用結構化的工具，附上標好的選項 [A]/[B]/[C]（現在寫入 /
   先顯示完整草稿 / 還不要）。多檔案的變更，列出每個檔案
   和它改了什麼，然後一次分組詢問，不要每個檔案各自用純文字問。
6. **每個章節都核准後，只寫一次**：文件只在 Phase 7 寫一次；
   Phase 7b 的 Step 4 只會在它自己的詢問之後更新文件的 Document Status。邊做邊把每個核准章節的決策記錄在
   `production/session-state/active.md`，這樣當機也不會丟失任何決策。
   Phase 7b 逼出來的修訂也用同樣方式寫：在重新起草的章節
   核准之後，只寫一次；而更新（Phase 0e）只寫它選的那些章節。

沒有使用者的意見，絕對不要做出有約束力的架構決策。如果使用者
不確定，要在請他們決定之前，先提出 2-4 個附優缺點的選項。

---

## 建議的下一步

- 針對 Phase 6 列出的每個必要 ADR，跑 `/architecture-decision [title]`，先做 Foundation 層的 ADR
- 跑 `/architecture-review`：根據剛寫好的 ADR 建立 Requirements Traceability Matrix 和 TR registry，並給每個暫定的 TR-ID 一個正式的編號。Pre-Production gate 之前必做。
- 跑 `/test-setup`，建立 `tests/unit/`、`tests/integration/`、CI workflow 和一個範例測試的骨架（gate-check 必要）
- 跑 `/ux-design`，初始化 `design/ux/interaction-patterns.md` 和 `design/accessibility-requirements.md`（gate-check 必要）
- 必要的 ADR 都寫好之後，跑 `/create-control-manifest`，產出分層規則清單
- 所有必要的 ADR、`/test-setup` 和 `/ux-design` 都完成後，跑 `/gate-check pre-production`
