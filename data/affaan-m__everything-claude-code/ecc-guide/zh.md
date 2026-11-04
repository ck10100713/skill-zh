---
name: ecc-guide
description: 靠讀即時的 repo 內容（agent、skill、command、hook、rule、install profile 與文件）來回答 ECC 相關問題，不靠記憶。在使用者問 ECC 包含什麼、怎麼安裝或重置、哪個 skill 或 command 適合某個任務，或專案 onboarding 怎麼進行時使用。
metadata:
  origin: community
---

# ECC 指南

當使用者需要理解、瀏覽、安裝或挑選 ECC 的各個部分時，就用這個 skill。

## 何時使用

使用者出現下列情況時使用：

- 問 ECC 包含什麼
- 想找某個 skill、command、agent、hook、rule 或 install profile
- 剛接觸這個 repo，需要有人帶路
- 問「我要怎麼用 ECC 做 X？」
- 問哪些 ECC 元件適合某個專案
- 需要簡短說明 command、skill、agent、hook 和 rule 之間的關係
- 被安裝路徑、重複安裝、重置/解除安裝，或選擇性安裝的選項搞混

## 核心原則

從現在的檔案回答，不要靠記憶。ECC 變動很快，寫死的目錄數量、功能清單和安裝說明都會過時。

當 ECC repo 可用時，給出具體答案之前先檢查相關檔案：

```bash
node scripts/ci/catalog.js --json
find skills -maxdepth 2 -name SKILL.md | sort
find commands -maxdepth 1 -name '*.md' | sort
find agents -maxdepth 1 -name '*.md' | sort
node scripts/install-plan.js --list-profiles
node scripts/install-plan.js --list-components --json
```

只讀回答使用者問題所需的最少檔案。

## Repo 地圖

- `README.md`：安裝路徑、解除安裝/重置指引、對外定位、FAQ
- `AGENTS.md`：貢獻者指引與專案結構
- `agent.yaml`：匯出的 gitagent 介面與 command 清單
- `commands/`：維護中的 slash-command 相容 shim
- `skills/*/SKILL.md`：可重用的工作流與領域 playbook
- `agents/*.md`：委派用的 subagent 角色 prompt
- `rules/`：語言與 harness 的規則
- `hooks/README.md`、`hooks/hooks.json`、`scripts/hooks/`：hook 的行為與安全 gate
- `manifests/install-*.json`：選擇性安裝的模組、元件、profile 與 target 支援
- `docs/`：harness 指南、架構筆記、翻譯文件、發布文件

## 回應風格

先給答案，再給下一步行動。大多數使用者不需要整份目錄傾倒。

好的第一個回應的形式：

1. 該用什麼
2. 為什麼適合
3. 要檢查的確切檔案或指令
4. 一個下一步指令或問題

避免：

- 預設就列出每個 skill 或 command
- 重複貼大段 README
- 已有 skill 優先的路徑時，還推薦已退役的 command shim
- 沒檢查檔案系統就宣稱某個元件存在
- 受管的 installer 支援該 target 時，卻用手動複製指令取代安裝指引

## 常見任務

### 新使用者 Onboarding

給一份簡短的選單：

- 安裝或重置 ECC
- 為專案挑選 skill
- 理解 command 和 skill 的差別
- 檢視 hook 與安全行為
- 跑 harness 稽核
- 找特定的工作流

安裝/重置請指向 `README.md`，專案專屬的 onboarding 請指向 `/project-init`。

### 功能探索

針對「我該用什麼來做 X？」：

1. 搜尋 `skills/`、`commands/` 和 `agents/`。
2. 優先把 skill 當作主要的工作流入口。
3. 只有在 command 是維護中的相容 shim，或使用者明確要 slash-command 的行為時，才用 command。
4. 委派有幫助時，提到 agent。

好用的搜尋：

```bash
rg -n "<query>" skills commands agents docs
find skills -maxdepth 2 -name SKILL.md | sort
```

### 安裝指引

使用受管的安裝路徑：

```bash
node scripts/install-plan.js --list-profiles
node scripts/install-plan.js --profile minimal --target claude --json
node scripts/install-apply.js --profile minimal --target claude --dry-run
```

安裝特定 skill：

```bash
node scripts/install-plan.js --skills <skill-id> --target claude --json
node scripts/install-apply.js --skills <skill-id> --target claude --dry-run
```

警告使用者，不要把 plugin 安裝和完整的手動/profile 安裝疊在一起，除非他們刻意想要重複的介面。

### 專案 Onboarding

當使用者想替目標 repo 設定 ECC 時，用 `/project-init`。預期的順序是：

1. 從專案檔案偵測技術棧
2. 解析出一個 dry-run 的安裝計畫
3. 檢視現有的 `CLAUDE.md` 和設定檔
4. 套用變更前先問
5. 讓產生的指引保持精簡，並針對該 repo

### 疑難排解

先問目標 harness 和安裝路徑，再檢查：

- plugin 安裝的 metadata
- `.claude/`、`.cursor/`、`.codex/`、`.gemini/`、`.opencode/`、`.codebuddy/`、`.joycode/` 或 `.qwen/`
- `hooks/hooks.json`
- install-state 檔案
- 相關的 command/skill 檔案

檢查 repo 健康度時，建議：

```bash
npm run harness:audit -- --format text
npm run observability:ready
npm test
```

## 輸出範本

### 簡短建議

```text
Use <skill-or-command>. It fits because <reason>.

Canonical file: <path>
Verify with: <command>
Next: <one concrete action>
```

### 搜尋結果

```text
Best matches:
- <path>: <why it matters>
- <path>: <why it matters>

Recommendation: <which one to use first and why>
```

### 安裝計畫摘要

```text
Detected: <stack evidence>
Target: <harness>
Plan: <profile/modules/skills>
Dry run: <command>
Would change: <paths>
Needs approval before apply: <yes/no>
```

## 相關介面

- `/project-init`：針對目標 repo、感知技術棧的 onboarding 計畫
- `/harness-audit`：可重現的就緒度評分表
- `/skill-health`：skill 品質 review
- `/skill-create`：從本地 git 歷史產生新 skill
- `/security-scan`：檢查 Claude/OpenCode 設定的安全性
