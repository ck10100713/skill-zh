---
name: adopt
description: "既有專案（brownfield）稽核：現有的產出物真的能用嗎？產出編號的遷移計畫。和 /project-stage-detect 不同，它檢查的是合規性，不是有沒有存在。"
argument-hint: "[focus: full | gdds | adrs | stories | infra]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, AskUserQuestion, Bash(bash "*/.claude/skills/adopt/../../hooks/yaml-helper.sh" resolve_config *), Bash(bash .claude/scripts/gdd-structure-check.sh *), Bash(bash .claude/scripts/migrate-v1-config.sh --dry-run*)
model: sonnet
---

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys review_mode,automation,automation_always_ask,workflow`

上面已解析完成，直接使用。`/adopt` 在回報和寫入遷移狀態時，也會直接檢視 `project.yaml` 和舊版
設定檔；那種原始檢視是刻意的，和上面解析出來的值是分開的。

# Adopt：既有專案採用範本

這個 skill 會稽核既有專案的產出物，看它們是否**符合格式**，能不能配合範本的
skill 流程，然後產出排好優先順序的遷移計畫。

**這不是 `/project-stage-detect`。**
`/project-stage-detect` 回答的是：*有什麼東西存在？*
`/adopt` 回答的是：*現有的東西真的能配合範本的 skill 運作嗎？*

一個專案可以有 GDD、ADR 和 story，但如果這些產出物的內部格式不對，
每個對格式敏感的 skill 還是會默默失敗，或產出錯誤的結果。

**輸出：** `docs/adoption-plan-[date].md`，一份持續存在、可勾選的遷移計畫。

**參數模式：**

**稽核模式：** `$ARGUMENTS`（空白 = `full`）

- **沒有參數 / `full`**：完整稽核，涵蓋所有產出物類型
- **`gdds`**：只檢查 GDD 的格式合規
- **`adrs`**：只檢查 ADR 的格式合規
- **`stories`**：只檢查 story 的格式合規
- **`infra`**：只檢查基礎設施產出物的缺口（registry、manifest、sprint-status、stage.txt）

---

**自動化模式**：解析 `modes.automation`（`project.local.yaml` →
`project.yaml` → 預設 `collaborative`）。每次呼叫 `AskUserQuestion` 都要遵循 `.claude/docs/automation-modes.md`
（collaborative 一律詢問 · guided 只問重大事項 · autonomous 記錄後直接進行；
`automation_always_ask` 的類別一律會詢問）。

**`workflow`**（依 `.claude/docs/workflow-modes.md`）。它決定第 2 階段稽核的範圍和
第 3 階段的嚴重度：`full` 以完整結構稽核所有文件類型；`standard` 只稽核
必要的文件/章節（選用的章節只是資訊，不算缺口）；
`minimal` 只做 `design/game-brief.md` 的格式檢查，不期待有 GDD/ADR/UX。見第 2 階段。

## 第 1 階段：偵測專案狀態

**現在就讀 `references/1-detect.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段被壓縮或恢復了，要重新讀一次。

## 第 2 階段：格式稽核

**現在就讀 `references/2-format-audit.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段被壓縮或恢復了，要重新讀一次。

## 第 3 階段：為缺口分類並排優先順序

**現在就讀 `references/3-classify.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段被壓縮或恢復了，要重新讀一次。

## 第 4 階段：建立遷移計畫

**現在就讀 `references/4-migration-plan.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段被壓縮或恢復了，要重新讀一次。

## 第 5 階段：呈現摘要並詢問是否寫入

**現在就讀 `references/5-summary.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段被壓縮或恢復了，要重新讀一次。

## 第 6 階段：寫入採用計畫

**現在就讀 `references/6-write.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段被壓縮或恢復了，要重新讀一次。

## 第 7 階段：提供第一步行動

**現在就讀 `references/7-first-action.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段被壓縮或恢復了，要重新讀一次。

## 協作協定

**適用於 `collaborative` 模式（預設）。** `guided` 和
`autonomous` 模式請見 `.claude/docs/automation-modes.md`，下面的規則
描述的是 collaborative 模式的要求，不是所有模式通用的行為。

1. **靜靜地讀** — 完整稽核做完，才呈現任何東西
2. **先給摘要** — 在詢問要不要寫入之前，先讓使用者看到範圍
3. **寫入前先問** — 建立採用計畫檔案之前，一定要先確認
4. **提供，不強迫** — 計畫只是建議，要修什麼、什麼時候修，由使用者決定
5. **一次一個行動** — 交出計畫之後，提供一個具體的下一步，
   不要一次列出六件要同時做的事
6. **絕對不要重新產生既有的產出物** — 只補現有內容的缺口；
   不要重寫已經有內容的 GDD、ADR 或 story
