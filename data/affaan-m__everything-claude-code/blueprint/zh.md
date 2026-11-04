---
name: blueprint
description: "把一句話的目標，變成多 session、多 agent 工程專案的逐步施工計畫：每一步都是一個 PR 的大小，附有自成一體的 context 簡報、能偵測平行步驟的相依圖、對抗式的 review 關卡，以及計畫變更協定。規劃橫跨多個 PR 或 session 的大型功能、重構或路線圖時使用；單一 PR 的任務，或使用者說「直接做就好」時不要用。"
metadata:
  origin: community
---

# Blueprint：施工計畫產生器

把一句話的目標，變成任何 coding agent 都能冷啟動執行的逐步施工計畫。

## 何時使用

- 把大型功能拆成多個 PR，並有清楚的相依順序
- 規劃橫跨多個 session 的重構或遷移
- 協調跨 sub-agent 的平行工作流
- 任何 session 之間遺失 context 會造成重工的任務

**不要用在**一個 PR 就能完成的任務、少於 3 次工具呼叫的任務，或使用者說「直接做就好」的時候。

## 運作方式

Blueprint 執行五個階段的 pipeline：

1. **Research**：先做事前檢查（git、gh 驗證、remote、預設 branch），然後讀專案結構、既有的計畫和記憶檔案，蒐集 context。
2. **Design**：把目標拆成一個 PR 大小的步驟（通常 3 到 12 步）。替每一步指定相依關係、平行/循序順序、模型等級（最強的對預設的），以及 rollback 策略。
3. **Draft**：把自成一體的 Markdown 計畫檔案寫到 `plans/`。每一步都包含 context 簡報、任務清單、驗證指令和完成條件，這樣全新的 agent 不用讀前面的步驟，就能執行任何一步。
4. **Review**：把對抗式 review 委派給最強模型的 sub-agent（例如 Opus），依檢查表和反面模式目錄進行。定稿之前，修好所有嚴重的發現。
5. **Register**：儲存計畫、更新記憶索引，並向使用者呈現步驟數和平行度的摘要。

Blueprint 會自動偵測 git/gh 是否可用。有 git + GitHub CLI 時，它會產生完整的 branch/PR/CI 工作流程計畫。沒有的話，就切換到直接模式（原地編輯，不開 branch）。

## 範例

### 基本用法

```
/blueprint myapp "migrate database to PostgreSQL"
```

會產生 `plans/myapp-migrate-database-to-postgresql.md`，裡面的步驟像是：
- Step 1: 加上 PostgreSQL driver 和連線設定
- Step 2: 為每個資料表建立 migration script
- Step 3: 更新 repository 層以使用新的 driver
- Step 4: 加上針對 PostgreSQL 的整合測試
- Step 5: 移除舊的資料庫程式碼和設定

### 多 agent 專案

```
/blueprint chatbot "extract LLM providers into a plugin system"
```

會產生一份計畫，其中在可能的地方設有平行步驟（例如在 plugin 介面那一步完成之後，「實作 Anthropic plugin」和「實作 OpenAI plugin」平行執行）、模型等級的指派（介面設計那一步用最強的，實作用預設的），以及每一步之後都要驗證的不變條件（例如「所有既有測試都通過」「核心裡沒有 provider 的 import」）。

## 主要功能

- **冷啟動執行**：每一步都包含自成一體的 context 簡報。不需要先前的 context。
- **對抗式 review 關卡**：每份計畫都由最強模型的 sub-agent，依涵蓋完整性、相依正確性和反面模式偵測的檢查表來 review。
- **Branch/PR/CI 工作流程**：內建在每一步裡。沒有 git/gh 時，會平順降級成直接模式。
- **平行步驟偵測**：相依圖會找出沒有共用檔案或輸出相依的步驟。
- **計畫變更協定**：步驟可以被拆分、插入、跳過、重新排序或放棄，並有正式的協定和稽核軌跡。
- **零 runtime 風險**：純 Markdown 的 skill。整個 repo 只有 `.md` 檔案，沒有 hook、沒有 shell script、沒有可執行程式碼、沒有 `package.json`、沒有 build 步驟。安裝或呼叫時，除了 Claude Code 原生的 Markdown skill 載入器之外，沒有任何東西會執行。

## 安裝

這個 skill 隨 ECC 一起發布。安裝了 ECC 就不需要另外安裝。

### 完整的 ECC 安裝

如果你是從 ECC repo 的 checkout 工作，用這個指令確認 skill 存在：

```bash
test -f skills/blueprint/SKILL.md
```

之後要更新時，更新之前先審視 ECC 的 diff：

```bash
cd /path/to/ECC
git fetch origin main
git log --oneline HEAD..origin/main       # 更新之前，先審視新的 commit
git checkout <reviewed-full-sha>          # 固定到特定審視過的 commit
```

### 獨立的 vendored 安裝

如果你只在完整 ECC 安裝之外，vendor 這一個 skill，就把審視過的檔案從 ECC repo 複製到 `~/.claude/skills/blueprint/SKILL.md`。Vendored 的副本沒有 git remote，所以更新時要從審視過的 ECC commit 重新複製檔案，不要執行 `git pull`。

## 需求

- Claude Code（用於 `/blueprint` slash command）
- Git + GitHub CLI（選用，能啟用完整的 branch/PR/CI 工作流程；Blueprint 偵測到沒有時，會自動切換到直接模式）

## 來源

靈感來自 antbotlab/blueprint，是上游專案與參考設計。
