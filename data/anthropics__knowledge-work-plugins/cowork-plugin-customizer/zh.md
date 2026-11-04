---
name: cowork-plugin-customizer
description: >
  針對特定組織的工具和工作流程，客製化 Claude Code plugin。
  Use when: customize plugin, set up plugin, configure plugin, tailor plugin, adjust plugin settings,
  customize plugin connectors, customize plugin skill, tweak plugin, modify plugin configuration.
compatibility: Requires Cowork desktop app environment with access to mounted plugin directories (mnt/.local-plugins, mnt/.plugins).
---

# Cowork Plugin 客製化

針對特定組織客製化 plugin：可以是第一次把通用的 plugin 範本設定好，也可以是微調、改進已經設定過的 plugin。

> **找到 plugin**：要找 plugin 的原始檔，執行 `find mnt/.local-plugins mnt/.plugins -type d -name "*<plugin-name>*"` 找出 plugin 目錄，然後先讀它的檔案、搞懂結構，再動手修改。如果找不到 plugin 目錄，使用者很可能是在遠端容器裡進行這段對話。這時要中止，並告訴他們：「Customizing plugins is currently only available in the desktop app's Cowork mode.」

## 判斷客製化模式

找到 plugin 之後，檢查有沒有 `~~` 開頭的佔位符：`grep -rn '~~\w' /path/to/plugin --include='*.md' --include='*.json'`

> **預設規則**：如果有 `~~` 佔位符，除非使用者明確要求客製化 plugin 的某個特定部分，否則預設走**通用 plugin 設定**。

**1. 通用 plugin 設定**：plugin 裡有 `~~` 開頭的佔位符。這些是範本中需要換成真實值的客製化點（例如 `~~Jira` → `Asana`、`~~your-team-channel` → `#engineering`）。

**2. 限定範圍的客製化**：沒有 `~~` 佔位符，而且使用者要求客製化 plugin 的某個特定部分（例如「customize the connectors」「update the standup skill」「change the ticket tool」）。讀 plugin 的檔案找出相關的段落，只專注在那些地方。不要掃描整個 plugin，也不要拿不相關的客製化項目來問。

> **舊式 `commands/` 目錄**：有些 plugin 會附 `commands/` 目錄。Cowork UI 現在把這些和 skill 一起呈現成單一的「Skills」概念，所以客製化時，`commands/*.md` 檔案要和 `skills/*/SKILL.md` 檔案用同樣的方式處理。

**3. 一般客製化**：沒有 `~~` 佔位符，而且使用者想大範圍修改 plugin。讀 plugin 的檔案了解目前的設定，再問使用者想改什麼。

> **重要**：絕對不要改被客製化的 plugin 或 skill 的名稱。不要重新命名目錄、檔案，或 plugin／skill 的 name 欄位。

> **非技術性的輸出**：所有面向使用者的輸出（待辦清單項目、問題、摘要）都必須用平實、非技術性的語言寫。絕對不要向使用者提到 `~~` 前綴、佔位符或客製化點。一切都用 plugin 的功能和組織的工具來描述。

## 客製化工作流程

### 階段 0：收集使用者意圖（僅限限定範圍和一般客製化）

對於**限定範圍的客製化**和**一般客製化**（不含通用 plugin 設定），檢查使用者在提出要求的同時，有沒有附上自由格式的背景說明（例如「customize the standup skill — we do async standups in #eng-updates every morning」）。

- **如果使用者有提供背景**：記下來，用它預先填好階段 3 的答案，使用者已經回答過的問題就跳過不問。
- **如果使用者沒有提供背景**：繼續之前，先用 AskUserQuestion 問一個開放式問題。問題要依使用者要求客製化的內容調整，例如「What changes do you have in mind for the brief skill?」或「What would you like to change about how this plugin works?」保持簡短，並針對他們的要求。

  使用他們的回答（如果有的話）作為後續階段的額外背景。

### 階段 1：從知識類 MCP 收集背景

用公司內部的知識類 MCP 蒐集和客製化範圍相關的資訊。各類別的詳細查詢模式請見 `references/search-strategies.md`。

**要收集什麼**（範圍限縮到相關的部分）：

- 組織使用的工具名稱和服務
- 組織的流程和工作流程
- 團隊慣例（命名、狀態、估點尺度）
- 設定值（workspace ID、專案名稱、團隊識別碼）

**要搜尋的來源：**

1. **聊天／Slack MCP**：工具的提及、整合、工作流程討論
2. **文件 MCP**：新人訓練文件、工具指南、設定說明
3. **Email MCP**：授權通知、管理員郵件、設定邀請

把所有發現記下來，供階段 3 使用。

### 階段 2：建立待辦清單

建立一份要做的修改的待辦清單，範圍要適當：

- **限定範圍的客製化**：只列和使用者問到的那個特定段落相關的項目。
- **通用 plugin 設定**：執行 `grep -rn '~~\w' /path/to/plugin --include='*.md' --include='*.json'` 找出所有佔位符客製化點。依主題分組。
- **一般客製化**：讀 plugin 的檔案，了解目前的設定，並根據使用者的要求，找出需要改什麼。

用對使用者友善、聚焦在 plugin 用途的描述：

- **好**：「Learn how standup prep works at Company」
- **不好**：「Replace placeholders in skills/standup-prep/SKILL.md」

### 階段 3：完成待辦項目

用階段 0 和階段 1 的背景逐項處理。

**如果使用者的自由格式輸入（階段 0）或知識類 MCP（階段 1）已經給出明確的答案**：直接套用，不用確認。

**否則**：使用 AskUserQuestion。不要假設「業界標準」的預設值是對的，如果使用者的輸入和知識類 MCP 都沒有給出具體答案，就問。注意：AskUserQuestion 一定會附一個 Skip 按鈕和一個讓人填自訂答案的文字輸入框，所以不要把 `None` 或 `Other` 放進選項。

**修改的類型：**

1. **佔位符替換**（通用設定）：`~~Jira` → `Asana`、`~~your-org-channel` → `#engineering`
2. **內容更新**：修改指示、skill、工作流程或參考資料，讓它們符合組織
3. **URL 格式更新**：`tickets.example.com/your-team/123` → `app.asana.com/0/PROJECT_ID/TASK_ID`
4. **設定值**：workspace ID、專案名稱、團隊識別碼

如果使用者不知道或跳過，就保持原值不變（通用設定的話，就保留 `~~` 開頭的佔位符）。

### 階段 4：搜尋有用的 MCP

客製化項目都處理完之後，為已經找出或更動的工具連接 MCP。完整流程、類別對關鍵字的對照表和設定檔格式，請見 `references/mcp-servers.md`。

針對客製化過程中找出的每個工具：

1. 搜尋 registry：用 `references/mcp-servers.md` 裡的類別關鍵字執行 `search_mcp_registry(keywords=[...])`，如果已經知道具體的工具名稱，就直接搜它
2. 如果尚未連接：執行 `suggest_connectors(directoryUuids=["chosen-uuid"])`，由使用者完成驗證
3. 更新 plugin 的 MCP 設定檔（先檢查 `plugin.json` 有沒有自訂位置，否則用根目錄的 `.mcp.json`）

把所有 MCP 的結果收集起來，一起放在摘要輸出裡呈現（見下方），不要在這個階段一個一個地呈現 MCP。

## 打包 Plugin

所有客製化都套用完之後，把 plugin 打包成 `.plugin` 檔交給使用者：

1. **把 plugin 目錄壓成 zip**（排除 `setup/`，因為它已經用不到了）：
   ```bash
   cd /path/to/plugin && zip -r /tmp/plugin-name.plugin . -x "setup/*" && cp /tmp/plugin-name.plugin /path/to/outputs/plugin-name.plugin
   ```
2. **把檔案以 `.plugin` 副檔名呈現給使用者**，讓他們可以直接安裝。（呈現 .plugin 檔案時，使用者會看到豐富的預覽，可以瀏覽 plugin 的檔案，並按一個按鈕接受這些客製化。）

> **重要**：一定要先在 `/tmp/` 建立 zip，再複製到 outputs 資料夾。直接寫進 outputs 資料夾可能會因為權限問題失敗，還會留下暫存檔。

> **命名**：`.plugin` 檔要使用原本的 plugin 目錄名稱（例如 plugin 目錄是 `coder`，輸出檔就該是 `coder.plugin`）。客製化過程中不要重新命名 plugin 或它的檔案，只替換佔位符的值和更新內容。

## 摘要輸出

客製化完成後，向使用者呈現一份依來源分組、說明學到什麼的摘要。一定要包含 MCP 的段落，說明設定過程中連接了哪些 MCP，以及使用者還該連接哪些：

```markdown
## From searching Slack

- You use Asana for project management
- Sprint cycles are 2 weeks

## From searching documents

- Story points use T-shirt sizes

## From your answers

- Ticket statuses are: Backlog, In Progress, In Review, Done
```

然後呈現設定過程中已連接的 MCP，以及使用者還該連接的 MCP，並附上連接的方法。

如果階段 1 沒有可用的知識類 MCP，而且使用者至少有一個問題得手動回答，就在結尾加上一則備註：

> By the way, connecting sources like Slack or Microsoft Teams would let me find answers automatically next time you customize a plugin.

## 其他資源

- **`references/mcp-servers.md`**：MCP 探索流程、類別對關鍵字的對照、設定檔位置
- **`references/search-strategies.md`**：用來找工具名稱和組織設定值的知識類 MCP 查詢模式
- **`examples/customized-mcp.json`**：已完整設定好的 `.mcp.json` 範例
