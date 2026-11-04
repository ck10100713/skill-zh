---
name: architecture-review
description: "把 GDD 需求對應到 ADR 的追溯矩陣。找出缺口、ADR 之間的衝突、引擎相容性。判定 PASS/CONCERNS/NOT ASSESSED/FAIL。"
argument-hint: "[focus: full | coverage | consistency | engine | rtm | single-gdd path/to/gdd.md]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Agent, AskUserQuestion, Bash(bash "*/.claude/skills/architecture-review/../../hooks/yaml-helper.sh" resolve_config *), Bash(bash .claude/scripts/review-receipts.sh check *), Bash(bash .claude/scripts/review-receipts.sh hash *), Bash(bash .claude/scripts/adr-dep-graph.sh*), Bash(bash .claude/scripts/registry.sh validate*)
model: opus
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys automation,workflow`

# Architecture Review

架構審查會驗證整體的架構決策是否涵蓋了所有遊戲設計需求、
內部是否一致，以及是否正確鎖定專案固定的引擎版本。它是從技術設定
進入前期製作（Pre-Production）之間的品質關卡。

**參數模式：**
- **沒有參數 / `full`**：完整審查，所有階段
- **`coverage`**：只做追溯，看哪些 GDD 需求沒有 ADR
- **`consistency`**：只做 ADR 之間的衝突偵測
- **`engine`**：只做引擎相容性稽核
- **`single-gdd [path]`**：審查某一份特定 GDD 的架構涵蓋度
- **`rtm`**：需求追溯矩陣（Requirements Traceability Matrix），把標準矩陣
  延伸到包含 story 檔案路徑和測試檔案路徑；輸出
  `docs/architecture/requirements-traceability.md`，內含完整的
  GDD 需求 → ADR → Story → Test 鏈。在 story 和測試都已存在的
  Production 階段使用。

---

每次呼叫 `AskUserQuestion` 都要遵循 `.claude/docs/automation-modes.md`
（collaborative 一律詢問 · guided 只問重大事項 · autonomous 記錄後直接進行；
`automation_always_ask` 的類別一律會詢問）。

**`workflow`**（見 `.claude/docs/workflow-modes.md`）：
- `full` — 涵蓋所有 GDD 和所有 ADR 的完整追溯矩陣。
- `standard` — 縮小範圍：只看架構文件 + 關鍵的 ADR。
- `minimal` — 不適用（不需要架構文件）。

## 第 1 階段：載入所有東西

**現在就讀 `references/1-load.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段被壓縮或恢復了，要重新讀一次。

## 第 2 階段：從每份 GDD 擷取技術需求

**現在就讀 `references/2-extract-requirements.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段被壓縮或恢復了，要重新讀一次。

## 第 3 階段：建立追溯矩陣

**現在就讀 `references/3-traceability.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段被壓縮或恢復了，要重新讀一次。

## 第 4 階段：ADR 之間的衝突偵測

**現在就讀 `references/4-conflicts.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段被壓縮或恢復了，要重新讀一次。

## 第 5 階段：引擎相容性交叉檢查

**現在就讀 `references/5-engine.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段被壓縮或恢復了，要重新讀一次。

## 第 6 階段：架構文件涵蓋度

**現在就讀 `references/6-document-coverage.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段被壓縮或恢復了，要重新讀一次。

## 第 7 階段：輸出審查報告

**現在就讀 `references/7-report.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段被壓縮或恢復了，要重新讀一次。

## 第 8 階段：寫入並更新追溯索引

**現在就讀 `references/8-write.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段被壓縮或恢復了，要重新讀一次。

## 第 9 階段：交接

**現在就讀 `references/9-handoff.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段被壓縮或恢復了，要重新讀一次。

## 錯誤復原協定

**先驗證產出物。** 如果回傳合約指定了路徑，在把這個階段當成完成之前，
先檢查那個路徑是否存在，**指名的產出物如果不在磁碟上，就是失敗的階段，
不管回應讀起來多流暢。** agent 可能花掉一整個階段，回傳一段看似合理的開場白，
卻什麼都沒寫，這種情況既不是 BLOCKED，也不是錯誤，也不是「無法完成」，
所以下面的觸發條件永遠不會被觸發。要用指名未達成的合約去恢復它；context
通常還在。

如果任何被派出的 agent 回傳 BLOCKED、出錯或無法完成：**要立刻浮現這件事，
不要越過它所阻擋的相依項目繼續往下走，而且一定要產出部分報告**（這裡重試的範圍 = 更少的 GDD / 單一系統）。完整程序：
`.claude/docs/error-recovery-protocol.md`。

---

## 協作協定

**適用於 `collaborative` 模式（預設）。** `guided` 和
`autonomous` 模式請見 `.claude/docs/automation-modes.md`，下面的規則
描述的是 collaborative 模式的要求，不是所有模式通用的行為。

1. **靜靜地讀** — 不要把每個檔案讀取都講出來
2. **顯示矩陣** — 在任何寫入核准之前，先呈現完整的追溯矩陣；
   讓使用者看到現況
3. **不要猜** — 如果某個需求不明確，就問：「[X] 是技術需求，
   還是設計偏好？」
4. **核准前先給草稿** — 要寫入的內容（報告、更新後的 ADR 章節、systems-index 的列），
   在請求核准之前，一定要先在對話裡直接顯示出來。絕對不要請求寫入使用者還沒看過的東西。
5. **寫入核准用 `AskUserQuestion`** — 純文字的「May I?」是不夠的。
   用結構化的工具，附上標了 [A]/[B]/[C] 的選項，讓
   使用者可以在「現在寫入」、「先顯示完整草稿」和「還不要」之間選擇。
   涉及多個檔案的變更集，必須列出每個檔案和變更內容，然後用分組的選項
   問一次，不要每個檔案各問一個純文字問題。
6. **不阻擋** — 判定結果只是建議；就算出現 CONCERNS 甚至 FAIL 的發現，
   要不要繼續，由使用者決定
