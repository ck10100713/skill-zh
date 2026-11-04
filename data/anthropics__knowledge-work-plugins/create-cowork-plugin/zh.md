---
name: create-cowork-plugin
description: >
  在 cowork session 中，引導使用者從零開始建立新的 plugin。
  當使用者想建立 plugin、build a plugin、make a new plugin、develop a plugin、scaffold a plugin、start a plugin from scratch，或設計 plugin 時使用。
  這個 skill 需要 Cowork 模式，並能存取 outputs 目錄，才能交付最後的 .plugin 檔。
compatibility: Requires Cowork desktop app environment with access to the outputs directory for delivering .plugin files.
---

# 建立 Cowork Plugin

透過引導式對話，從零開始建立新的 plugin。帶著使用者走過探索、規劃、設計、實作和打包，最後交付一個可以直接安裝的 `.plugin` 檔。

## 概覽

plugin 是一個獨立的目錄，用 skill、agent、hook 和 MCP server 整合來擴充 Claude 的能力。這個 skill 涵蓋完整的 plugin 架構，以及用對話方式建立 plugin 的五階段工作流程。

流程：

1. **探索（Discovery）**：了解使用者想做什麼
2. **元件規劃（Component Planning）**：決定需要哪些元件類型
3. **設計與釐清問題（Design & Clarifying Questions）**：把每個元件詳細定義清楚
4. **實作（Implementation）**：建立所有 plugin 檔案
5. **審閱與打包（Review & Package）**：交付 `.plugin` 檔

> **非技術性的輸出**：所有面向使用者的對話都用平實的語言。除非使用者問起，否則不要洩漏檔案路徑、目錄結構或 schema 欄位這類實作細節。一切都用這個 plugin 會做什麼來描述。

## Plugin 架構

### 目錄結構

每個 plugin 都遵循這個配置：

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json           # 必要：plugin manifest
├── skills/                   # Skills（含 SKILL.md 的子目錄）
│   └── skill-name/
│       ├── SKILL.md
│       └── references/
├── agents/                   # Subagent 定義（.md 檔）
├── .mcp.json                 # MCP server 定義
└── README.md                 # Plugin 文件
```

> **舊式 `commands/` 格式**：較舊的 plugin 可能會有 `commands/` 目錄，裡面是單檔的 `.md` slash command。這個格式仍然可用，但新的 plugin 應該改用 `skills/*/SKILL.md`：Cowork UI 把兩者一起呈現成單一的「Skills」概念，而且 skill 格式支援透過 `references/` 做漸進式揭露。

**規則：**

- `.claude-plugin/plugin.json` 一定要有
- 元件目錄（`skills/`、`agents/`）放在 plugin 根目錄，不要放在 `.claude-plugin/` 裡面
- 只為 plugin 真正用到的元件建立目錄
- 所有目錄和檔案名稱都用 kebab-case

### plugin.json Manifest

位於 `.claude-plugin/plugin.json`。最基本的必填欄位是 `name`。

```json
{
  "name": "plugin-name",
  "version": "0.1.0",
  "description": "Brief explanation of plugin purpose",
  "author": {
    "name": "Author Name"
  }
}
```

**名稱規則：** kebab-case，小寫加連字號，不能有空格或特殊字元。
**版本：** semver 格式（MAJOR.MINOR.PATCH）。從 `0.1.0` 開始。

選填欄位：`homepage`、`repository`、`license`、`keywords`。

可以指定自訂的元件路徑（是補充自動探索，不是取代）：

```json
{
  "commands": "./custom-commands",
  "agents": ["./agents", "./specialized-agents"],
  "hooks": "./config/hooks.json",
  "mcpServers": "./.mcp.json"
}
```

### 元件 Schema

每種元件類型的詳細 schema 在 `references/component-schemas.md`。摘要：

| 元件                               | 位置                | 格式                        |
| ---------------------------------- | ------------------- | --------------------------- |
| Skills                             | `skills/*/SKILL.md` | Markdown + YAML frontmatter |
| MCP Servers                        | `.mcp.json`         | JSON                        |
| Agents（在 Cowork 不常用）         | `agents/*.md`       | Markdown + YAML frontmatter |
| Hooks（在 Cowork 很少用）          | `hooks/hooks.json`  | JSON                        |
| Commands（舊式）                   | `commands/*.md`     | Markdown + YAML frontmatter |

這個 schema 和 Claude Code 的 plugin 系統共用，但你現在是在為 Claude Cowork 建立 plugin，Cowork 是一個用來做知識工作的桌面 app。
Cowork 的使用者通常會覺得 skill 最有用。**新的 plugin 要用 `skills/*/SKILL.md` 來建立骨架，除非使用者明確需要舊式的單檔格式，否則不要建立 `commands/`。**

### 使用 `~~` 佔位符的可客製化 plugin

> **預設不要使用或詢問這個模式。** 只有使用者明確說他們想讓組織以外的人使用這個 plugin 時，才引入 `~~` 佔位符。
> 如果使用者看起來想對外散布 plugin，可以提一下這是個選項，但不要主動用 AskUserQuestion 去問。

當 plugin 打算分享給公司以外的人時，可能有些部分需要依個別使用者調整。
你可能需要用類別而不是具體產品來指稱外部工具（例如用「project tracker」而不是「Jira」）。
需要分享時，就用通用的說法，並用兩個波浪號標記這些需要客製化的地方，像是 `create an issue in ~~project tracker`。
如果用了任何工具類別，就要在 plugin 根目錄寫一個 `CONNECTORS.md` 檔來說明：

```markdown
# Connectors

## How tool references work

Plugin files use `~~category` as a placeholder for whatever tool the user
connects in that category. Plugins are tool-agnostic — they describe
workflows in terms of categories rather than specific products.

## Connectors for this plugin

| Category        | Placeholder         | Options                         |
| --------------- | ------------------- | ------------------------------- |
| Chat            | `~~chat`            | Slack, Microsoft Teams, Discord |
| Project tracker | `~~project tracker` | Linear, Asana, Jira             |
```

### ${CLAUDE_PLUGIN_ROOT} 變數

hook 和 MCP 設定裡所有 plugin 內部的路徑參照，都用 `${CLAUDE_PLUGIN_ROOT}`。絕對不要寫死絕對路徑。

## 引導式工作流程

要問使用者問題時，用 AskUserQuestion。不要假設「業界標準」的預設值是對的。注意：AskUserQuestion 一定會附一個 Skip 按鈕和一個讓人填自訂答案的文字輸入框，所以不要把 `None` 或 `Other` 放進選項。

### 階段 1：探索

**目標**：了解使用者想做什麼，以及為什麼。

要問的（只問不清楚的，如果使用者一開始的要求已經回答了，就跳過）：

- 這個 plugin 該做什麼？它解決什麼問題？
- 誰會用它、在什麼情境下用？
- 它需要整合任何外部工具或服務嗎？
- 有沒有類似的 plugin 或工作流程可以參考？

總結你的理解，確認之後再繼續。

**產出**：對 plugin 用途和範圍的清楚陳述。

### 階段 2：元件規劃

**目標**：決定 plugin 需要哪些元件類型。

根據探索階段的答案，判斷：

- **Skills**：需要 Claude 依需求載入的專門知識，或使用者主動發起的動作嗎？（領域專業、參考 schema、工作流程指南、deploy／設定／分析／審閱類的動作）
- **MCP Servers**：需要外部服務整合嗎？（資料庫、API、SaaS 工具）
- **Agents（不常用）**：有自主的多步驟任務嗎？（驗證、產生、分析）
- **Hooks（很少用）**：在某些事件發生時，需要自動做點什麼嗎？（強制執行政策、載入 context、驗證操作）

呈現一張元件規劃表，包括你決定不建立的元件類型：

```
| Component | Count | Purpose |
|-----------|-------|---------|
| Skills    | 3     | Domain knowledge for X, /do-thing, /check-thing |
| Agents    | 0     | Not needed |
| Hooks     | 1     | Validate writes |
| MCP       | 1     | Connect to service Y |
```

取得使用者的確認或調整之後再繼續。

**產出**：確認過的要建立的元件清單。

### 階段 3：設計與釐清問題

**目標**：把每個元件詳細定義清楚。在實作之前把所有歧義解決掉。

針對規劃裡的每種元件類型，提出有針對性的設計問題。問題依元件類型分組呈現。等答案回來再繼續。

**Skills：**

- 哪些使用者的提問應該觸發這個 skill？
- 它涵蓋哪些知識領域？
- 需要附參考檔案放詳細內容嗎？
- 如果這個 skill 代表使用者主動發起的動作：它接受哪些參數、需要哪些工具？（Read、Write、Bash、Grep 等）

**Agents：**

- 每個 agent 應該主動觸發，還是只在被要求時才觸發？
- 它需要哪些工具？
- 輸出格式應該是什麼？

**Hooks：**

- 哪些事件？（PreToolUse、PostToolUse、Stop、SessionStart 等）
- 什麼行為：驗證、阻擋、修改、補充 context？
- 以 prompt 為基礎（由 LLM 驅動），還是以指令為基礎（確定性的 script）？

**MCP Servers：**

- 什麼 server 類型？（本機用 stdio、有 OAuth 的託管服務用 SSE、REST API 用 HTTP）
- 什麼驗證方式？
- 要公開哪些工具？

如果使用者說「你覺得怎樣最好就怎樣」，就提供具體的建議，並取得明確的確認。

**產出**：每個元件的詳細規格。

### 階段 4：實作

**目標**：遵循最佳實務建立所有 plugin 檔案。

**操作順序：**

1. 建立 plugin 的目錄結構
2. 建立 `plugin.json` manifest
3. 建立每個元件（確切的格式請見 `references/component-schemas.md`）
4. 建立 `README.md`，說明這個 plugin

**實作準則：**

- **Skills** 採用漸進式揭露：精簡的 SKILL.md 本文（3,000 字以內），詳細內容放在 `references/`。Frontmatter 的 description 必須用第三人稱，並包含具體的觸發語。Skill 本文是給 Claude 的指示，不是寫給使用者的訊息，所以要寫成「該做什麼」的指令。
- **Agents** 需要一段包含 `<example>` 區塊、展示觸發條件的 description，加上 markdown 本文裡的 system prompt。
- **Hooks** 設定放在 `hooks/hooks.json`。script 路徑用 `${CLAUDE_PLUGIN_ROOT}`。複雜的邏輯優先用以 prompt 為基礎的 hook。
- **MCP 設定**放在 plugin 根目錄的 `.mcp.json`。本機 server 路徑用 `${CLAUDE_PLUGIN_ROOT}`。必要的環境變數要記在 README 裡。

### 階段 5：審閱與打包

**目標**：交付完成的 plugin。

1. 總結建立了什麼：列出每個元件和它的用途
2. 問使用者要不要做任何調整
3. 執行 `claude plugin validate <path-to-plugin-json>` 檢查 plugin 結構。如果這個指令不能用（例如在 Cowork 裡執行時），就手動驗證結構：
   - `.claude-plugin/plugin.json` 存在，而且包含有效的 JSON，至少有 `name` 欄位
   - `name` 欄位是 kebab-case（只有小寫字母、數字和連字號）
   - plugin 引用的任何元件目錄（`commands/`、`skills/`、`agents/`、`hooks/`）真的存在，而且裡面的檔案格式正確：commands/skills/agents 用 `.md`，hooks 用 `.json`
   - 每個 skill 子目錄都有 `SKILL.md`
   - 回報通過什麼、沒通過什麼，就像 CLI 驗證器會做的那樣

   進入下一步之前，先修好任何錯誤。
4. 打包成 `.plugin` 檔：

```bash
cd /path/to/plugin-dir && zip -r /tmp/plugin-name.plugin . -x "*.DS_Store" && cp /tmp/plugin-name.plugin /path/to/outputs/plugin-name.plugin
```

> **重要**：一定要先在 `/tmp/` 建立 zip，再複製到 outputs 資料夾。直接寫進 outputs 資料夾可能會因為權限問題失敗。

> **命名**：`.plugin` 檔要用 `plugin.json` 裡的 plugin 名稱（例如名稱是 `code-reviewer`，就輸出 `code-reviewer.plugin`）。

`.plugin` 檔會以豐富預覽的形式出現在聊天裡，使用者可以瀏覽檔案，並按一個按鈕接受這個 plugin。

## 最佳實務

- **從小處開始**：從最小可行的元件組合開始。只有一個做得很好的 skill 的 plugin，比有五個半成品元件的 plugin 更有用。
- **Skill 的漸進式揭露**：核心知識放在 SKILL.md，詳細的參考資料放在 `references/`，可運作的範例放在 `examples/`。
- **清楚的觸發語**：Skill 的 description 應該包含使用者實際會說的具體詞句。Agent 的 description 應該包含 `<example>` 區塊。
- **Skill 是寫給 Claude 的**：Skill 本文要寫成 Claude 要遵循的指示，不是寫給使用者讀的文件。
- **祈使句的寫作風格**：skill 裡的指示用動詞開頭（「Parse the config file」，不是「You should parse the config file」）。
- **可攜性**：plugin 內部的路徑一律用 `${CLAUDE_PLUGIN_ROOT}`，絕對不要寫死路徑。
- **安全性**：憑證用環境變數、遠端 server 用 HTTPS、工具存取遵循最小權限。

## 其他資源

- **`references/component-schemas.md`**：每種元件類型的詳細格式規格（skills、agents、hooks、MCP、舊式 commands、CONNECTORS.md）
- **`references/example-plugins.md`**：三個不同複雜度的完整 plugin 結構範例
