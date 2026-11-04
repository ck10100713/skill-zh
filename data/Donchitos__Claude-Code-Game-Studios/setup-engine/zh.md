---
name: setup-engine
description: "設定引擎和版本。把它固定寫進 CLAUDE.md；當版本超出 LLM 訓練資料範圍時，用 WebSearch 補齊參考文件。"
argument-hint: "[engine] | [engine version] | refresh | upgrade [old-version] [new-version] | no args for guided selection"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, WebSearch, WebFetch, Agent, AskUserQuestion, Bash(bash "*/.claude/skills/setup-engine/../../hooks/yaml-helper.sh" resolve_config *), Bash(godot --version), Bash(godot --headless --path . --import), Bash(command -v godot), Bash(uname -s), Bash(bash .claude/scripts/project-coherence.sh*)
model: sonnet
---

# Engine Setup

呼叫這個 skill 時：

!`bash "${CLAUDE_SKILL_DIR}/../../hooks/yaml-helper.sh" resolve_config --keys workflow`

**留意等級。** 上面解析出來的 `workflow` 等級，決定這個 skill 預期哪一種設計
產出物，以及它在 §12 建議的收尾路徑：
- **`minimal`**：設計產出物是一頁的 `design/game-brief.md`
  （這個等級沒有 GDD、系統拆解或各系統設計）。
  `/setup-engine` 在 minimal 路徑中是*最先*跑的，所以這裡缺少 brief
  是正常的，不是漏洞。收尾路徑是 4 步驟的最低標準。
- **`standard` / `full`**：設計產出物是 `design/gdd/game-concept.md`，
  收尾路徑是完整的流程。

如果這個區塊沒有被渲染出來（shell 預處理被停用），就假設是 `minimal`（預設值）。

## 1. Parse Arguments

四種模式：

- **完整規格**：`/setup-engine godot 4.7`：同時提供引擎和版本
- **只給引擎**：`/setup-engine unity`：有提供引擎，版本會去查
- **沒有參數**：`/setup-engine`：完全引導模式（引擎推薦加版本）
- **Refresh**：`/setup-engine refresh`：更新參考文件（見第 10 節）
- **Upgrade**：`/setup-engine upgrade [old-version] [new-version]`：遷移到新的引擎版本（見第 11 節）

---

## 2. Guided Mode (No Arguments)

**現在讀 `references/2-guided-mode.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

## 3. Look Up Current Version

**現在讀 `references/3-version.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

## 4. Update CLAUDE.md Technology Stack

**現在讀 `references/4-claude-md-stack.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

## 5. Populate Technical Preferences

**現在讀 `references/5-technical-preferences.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

## 5.5 Populate `project.yaml` (Primary Config Store)

**現在讀 `references/5.5-project-yaml.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

## 6. Determine Knowledge Gap

**現在讀 `references/6-knowledge-gap.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

## 7. Populate Engine Reference Docs

**現在讀 `references/7-reference-docs.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

## 7.5 Scaffold the Engine Project

**現在讀 `references/7.5-scaffold.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

## 8. Verify the CLAUDE.md Import

**現在讀 `references/8-verify.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

## 9. Update Agent Instructions

先問："May I add a Version Awareness section to the engine specialist agent files?"，才能做任何編輯。

對所選引擎的專家 agent，確認它們有
"Version Awareness" 段落。如果沒有，就照現有 Godot 專家 agent 裡
的模式加一個。

這個段落應該指示 agent：
1. 讀 `docs/engine-reference/<engine>/VERSION.md`
2. 在建議程式碼之前，先檢查已棄用的 API
3. 檢查相關版本轉換的重大變更
4. 用 WebSearch 驗證不確定的 API

---

## 10. Refresh Subcommand

如果是以 `/setup-engine refresh` 呼叫：

1. 讀既有的 `docs/engine-reference/<engine>/VERSION.md`，取得
   目前的引擎和版本
2. 用 WebSearch 檢查：
   - 上次驗證之後有沒有新的引擎發布
   - 更新的遷移指南
   - 新近被棄用的 API
3. 用新的發現更新所有參考文件
4. 更新所有被修改檔案的 "Last verified" 日期
5. 回報有什麼改變

---

## 11. Upgrade Subcommand

**現在讀 `references/11-upgrade.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

## 12. Output Summary

**現在讀 `references/12-output-summary.md` 並照著做**：這個階段的步驟在那個檔案裡，不在這裡。如果對話在這個階段中被壓縮或恢復，要再讀一次。

## Guardrails

- 絕對不准猜引擎版本：一律用 WebSearch 或使用者確認來驗證
- `project.yaml` 是主要的設定儲存處（v1.1）。引擎設定一律要雙寫到
  `project.yaml`（主要）和 `technical-preferences.md`（舊版
  鏡像）。如果兩者出現分歧，以 `project.yaml` 為準。
- 沒問過就絕對不准覆寫既有的參考文件：要用附加或更新的方式
- 如果已經有另一個引擎的參考文件，替換前要先問
- 在編輯 CLAUDE.md 之前，一定要先讓使用者看到你要改什麼
- 如果 WebSearch 回傳的結果不明確，要給使用者看，讓他們決定
- 當使用者選的是 **GDScript** 時：把 `references/godot-language-config.md` 裡 **A1** 的 GDScript CLAUDE.md 範本原封不動複製過去。絕對不准在 Language 欄位加上 "C++ via GDExtension"。GDScript 專案可以用 GDExtension，但它不是主要的專案語言。路由表裡的 `godot-gdextension-specialist` 是在需要原生擴充時才用，它不會讓 C++ 變成專案語言。

---

## Appendix A — Godot Language Configuration

已經從這個檔案搬出去了，這樣在非 Godot 的執行中完全不會花費成本。

**當選擇的引擎是 Godot 時，讀**
`references/godot-language-config.md`
並使用對應所選語言的小節：

- **A1**：CLAUDE.md Technology Stack 範本（GDScript / C# / Both）
- **A2**：命名慣例
- **A3**：引擎專家的路由和副檔名對照表

**載入紀律。** 在 Godot 以外的任何引擎上，**絕對不要載入它**：第 4、5 或 5.5 節沒有任何地方需要它，硬去讀它只會浪費這次拆分要節省的 token。在 Godot 上，第一次到第 4 節時讀一次，然後在第 5 和 5.5 節繼續使用；不要每次參照都重讀。
