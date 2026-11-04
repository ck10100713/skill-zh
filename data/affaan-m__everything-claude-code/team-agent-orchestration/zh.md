---
name: team-agent-orchestration
description: "替 agent 小隊做以團隊為單位的編排：有負責人和範圍的工作項目、agent Kanban 狀態、branch 隔離、control pane 可視性，以及 merge 關卡。跨 branch 或 worktree 平行協調多個 agent 時使用：多 agent fan-out、agent Kanban、小隊協調，或是把 agent 的產出合併成一個產品。"
metadata:
  origin: ECC
---

# Team Agent Orchestration

當 agent 是被當成一個團隊在管理，而不是單一助理時，就用這個 skill。目的是讓以團隊為單位的編排變得可靠：清楚的工作項目、明確的負責人、agent Kanban 狀態、branch 隔離、control pane 可視性，還有 merge 關卡。

## 何時啟用

- 任務橫跨多個 agent、工具、harness、branch 或 worktree。
- 使用者提到團隊編排、agent Kanban、小隊、conductor、control pane、manager、桌面 app、Zellij、tmux、Hermes、Devin、Codex、Claude Code，或多 agent 工作。
- 專案需要在人和 agent 之間共用 workflow 狀態。
- 現有的 agent fan-out 有產出，但產出無法合併成產品。

## 運作模型

把每個 agent 都當成有狹窄合約的隊友：

- **Owner**：對這個工作項目負責的人或 agent。
- **Scope**：檔案、branch、工具範圍，以及禁區。
- **State**：backlog、ready、running、review、blocked、merged 或 archived。
- **Evidence**：測試、截圖、log、review 筆記，或 eval 報告。
- **Merge gate**：允許整合的確切條件。

## Agent Kanban

當工作必須跨 session 都看得到時，就用 agent Kanban。

| 欄位 | 意義 | 離開條件 |
| --- | --- | --- |
| Backlog | 候選的工作項目，還沒成形 | 驗收條件寫好了 |
| Ready | 已成形、可以指派 | 已指派 owner 和 branch/worktree |
| Running | Agent 正在作業 | 有交接產出物和變更的檔案 |
| Review | 工作完成但還沒 merge | 測試、diff review 和風險檢查通過 |
| Blocked | 需要外部輸入，或關卡沒過 | 阻礙有 owner 和下一步動作 |
| Merged | 已整合進主線 | PR 已 merge，或本機 main 已更新 |
| Archived | 不再相關 | 已記錄原因 |

每張卡片都應該符合這個 schema：

```json
{
  "id": "agent-card-001",
  "title": "Build dynamic workflow skill",
  "owner": "codex",
  "state": "running",
  "branch": "product/dynamic-workflow-team-orchestration",
  "worktree": ".",
  "acceptance": [
    "Skill exists",
    "Tests cover required concepts",
    "Content artifact contains video and article angles"
  ],
  "merge_gate": "lint, focused tests, and catalog check pass",
  "handoff": "path/to/handoff.md"
}
```

## 以團隊為單位的編排流程

1. **整理看板**：把模糊的野心轉成有 owner 和 merge 關卡的工作項目。
2. **選執行模式**：單一 agent、動態 workflow 模式、dmux/tmux、worktree fan-out，或外部桌面編排器。
3. **指派邊界**：每張卡一個 owner、明確的檔案範圍，沒有 integrator 就不准有重疊的寫入。
4. **執行 agent**：每個 agent 都要留下證據和交接筆記，不只是程式碼。
5. **依序 review**：先測試，再 diff review，再安全/風險檢查，最後是內容/產品的打磨。
6. **刻意地 merge**：由一個 integrator 解決衝突，並更新 control pane 或狀態產出物。
7. **抽出可重用的 skill**：如果卡片的模式重複出現，就把它升級成 `skills/` 裡的 skill。

## Control Pane 需求

一個對團隊編排有用的 control pane 應該顯示：

- 進行中的工作項目，以及它們的 agent Kanban 狀態。
- Owner、harness、branch、worktree 和最後一次 heartbeat。
- 交接產出物、測試、截圖和 PR 的連結。
- 依 owner 和解除阻礙的動作分組的阻礙。
- 用關卡判斷 merge 就緒度，不是憑感覺。
- 應該變成共用 skill 的可重用 workflow 候選。

在操作者能回答這幾個問題之前，不要再加更多自動化：誰負責這個、改了什麼、哪個關卡沒過、什麼可以安全 merge？

## 動態 Workflow 相容性

當一張卡需要動態 workflow 模式時：

- 把任務專屬的 harness 放在卡片 owner 底下。
- 把輸入和輸出存在卡片上。
- 從 Running 移到 Review 之前，要求先跑 eval。
- 重複使用過之後，才把 harness 升級成共用 skill。

## 要留意的失敗模式

- **Agent 大雜燴**：很多 agent 在跑，卻沒有 owner 或 merge 關卡。
- **看不見的工作**：有用的產出只存在聊天紀錄裡。
- **看板劇場**：有 Kanban 看板，但卡片沒有驗收條件。
- **重疊的寫入**：平行的 agent 沒有 worktree，卻編輯同一批檔案。
- **沒有產品產出物**：流程產出了文件，卻沒有可執行或可發布的東西。

## 輸出標準

每一輪編排結束時要交出：

- 看板 / 卡片的變更。
- 已 merge 或待處理的 branch。
- 測試和 eval 的證據。
- 有 owner 和下一步動作的阻礙。
- 新的共用 skill 候選。
