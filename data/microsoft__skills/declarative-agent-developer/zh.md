---
name: declarative-agent-developer
description: >
  建立、建置、部署並在地化 M365 Copilot 和 Teams 的 declarative agent。
  只要任務跟 declarative agent 有關就用這個 skill，包括在地化、
  建立專案骨架、編輯 manifest、新增 capability 和部署。
  在地化需要 tokenized manifest 和語言檔，只有這個 skill 知道怎麼產生。
  Triggers: "create agent", "create a declarative agent", "new declarative agent",
  "scaffold an agent", "new agent project", "add a capability", "add a plugin",
  "configure my agent", "deploy my agent", "fix my agent manifest", "edit my agent",
  "localize my agent", "add localization", "translate my agent", "multi-language agent",
  "add an API plugin", "add an MCP plugin", "add OAuth to my plugin",
  "review instructions", "improve instructions", "fix my instructions"
---

# M365 Agent Developer

## Telemetry Tagging

執行任何 `atk` CLI 指令之前，先設定 session 環境變數，讓所有 CLI 呼叫都被標記為 skill 發起的：
```bash
export ATK_CLI_SKILL=true
```
在 session 開頭跑一次就好。同一個終端機之後所有的 `atk` 指令都會繼承它。

## ⛔ Workspace Check — MANDATORY FIRST STEP

**做任何事之前，先檢查 workspace 的檔案，辨識這是什麼專案：**

1. 執行 `npx -y --package @microsoft/m365agentstoolkit-cli atk --version`，確認有安裝 ATK CLI。找不到 → **停下來。** 告訴使用者要先安裝 ATK。
2. 檢查專案根目錄有沒有 `m365agents.yml` 或 `teamsApp.yml`。
3. 檢查有沒有 `appPackage/declarativeAgent.json`。
4. 檢查有沒有非 agent 專案的跡象（有 express/react/next 的 `package.json`、`src/index.js`、`app.py` 等）。

**然後照這個決策閘門走：**

| Condition | Gate | Action |
|-----------|------|--------|
| 有非 agent 專案的檔案，沒有 `appPackage/` | **Reject** | 只回文字。不建檔案，不執行指令。 |
| 沒有 manifest，使用者想編輯/部署 | **Reject** | 只回文字。說明 manifest 不見了。 |
| 沒有 manifest，使用者想建新專案 | **Scaffold** | → [Scaffolding Workflow](references/scaffolding-workflow.md) |
| Manifest 存在但有錯誤 | **Fix** | Detect → Inform → Ask（見下面）。不准 deploy。 |
| 專案有效，使用者回報行為有問題 | **Review** | → [Instruction Review](references/instruction-review.md)，跑完整的 5 階段 review 流程 |
| 有效的 agent 專案 | **Edit** | → [Editing Workflow](references/editing-workflow.md) |

> **詳細的閘門規則、範例和反模式：** [Workspace Gates](references/workspace-gates.md)

### 🚫 HARD REJECTION RULES — No Exceptions

**這些規則凌駕所有其他指示。** 只要符合其中任何一條，你就一定要立刻停下來。

1. **絕對不准自己建立 `declarativeAgent.json`。** 如果 manifest 不見了，而使用者要的是編輯/修改/部署，就只回文字：說明 manifest 不見了，建議用 `npx -y --package @microsoft/m365agentstoolkit-cli atk new`，或是從頭開始。不要建立那個檔案，不要建立 `appPackage/`，不要為了「幫忙」就偷偷幫他 scaffold。

2. **絕對不准在非 agent 專案裡建檔案。** 如果 workspace 是 Express/React/Django 之類沒有 `appPackage/` 的 app，你的回應一定只能有文字。不要建任何檔案，不要執行任何指令。

3. **有錯誤的時候絕對不准 deploy。** 如果 agent manifest 有錯誤，就停下來。不要執行 `npx -y --package @microsoft/m365agentstoolkit-cli atk provision`，不管是「為了測試」、「為了示範錯誤」還是「看看會怎樣」都不行。回報錯誤，然後問使用者要怎麼處理。

### 🔍 Detect → Inform → Ask (Error-Handling Protocol)

遇到**任何**問題（檔案不見、JSON 格式錯誤、驗證錯誤、功能不相容），你一定要**依序**照這個流程走：

1. **Detect** — 找出具體的問題。JSON 的問題就試著 parse 檔案並回報語法錯誤。欄位缺漏就拿 manifest 對照 [Schema](references/schema.md) 檢查。
2. **Inform** — 在採取任何動作**之前**先告訴使用者。要精確描述哪裡有問題（「declarativeAgent.json 的 JSON 格式有誤：第 12 行缺逗號，第 18 行陣列沒有關閉」）。
3. **Ask** — 等使用者回應再做修改。不准默默修好、自動校正或繞過問題。

**這個流程適用於：**
- 缺少 `declarativeAgent.json` → Detect（找不到檔案）→ Inform（「找不到 manifest」）→ Ask（「要不要建立新的 agent？」）
- JSON 格式錯誤 → Detect（parse 錯誤）→ Inform（列出具體的語法問題）→ Ask（「要我修這些語法錯誤嗎？」）
- 驗證錯誤 → Detect（parse 並檢查 manifest）→ Inform（列出所有錯誤）→ Ask（「你想怎麼修這些問題？」）
- 版本不相容 → Detect（功能需要較新的版本）→ Inform（「這個功能需要 v1.6，你的 agent 是 v1.4」）→ Ask（「要升級嗎？」）

---

## Phase Routing

| Scenario | Workflow Reference |
|----------|-------------------|
| 從頭建立**新**專案 | [Scaffolding Workflow](references/scaffolding-workflow.md) |
| 處理現有的 `.json` manifest | [Editing Workflow](references/editing-workflow.md) |
| 新增 API plugin | [API Plugins](references/api-plugins.md) |
| 新增 MCP server | [MCP Plugin](references/mcp-plugin.md) |
| 為 MCP 或 API plugin 加上 OAuth | [Authentication](references/authentication.md) |
| 檢視或改進現有的 agent instructions | [Instruction Review](references/instruction-review.md) |
| 使用者回報 agent 給出籠統/錯誤的答案 | [Instruction Review](references/instruction-review.md) |
| 把 agent 在地化成多種語言 | [Localization](references/localization.md) |
| 為已經在地化的 agent 新增語言 | [Localization](references/localization.md) |
| 撰寫 agent instructions | [Conversation Design](references/conversation-design.md) |

---

## ATK CLI Setup

執行任何 ATK 指令之前，先跑 `npx -y --package @microsoft/m365agentstoolkit-cli atk --version` 檢查 ATK CLI 能不能用。找不到的話，**停下來告訴使用者**，不要自己去安裝。

所有指令都用 `npx -y --package @microsoft/m365agentstoolkit-cli atk` 當前綴（例如 `npx -y --package @microsoft/m365agentstoolkit-cli atk provision --env local`）。

---

## Critical Rules

### 1. Deploy After EVERY Edit

只要改了 `appPackage/` 裡的任何檔案，回應之前一定要 deploy 並附上測試連結：

```bash
npx -y --package @microsoft/m365agentstoolkit-cli atk provision --env local --interactive false
```

然後從 `env/.env.local` 讀取 `M365_TITLE_ID`，並且**一定**要呈現這個 review UX：

```
✅ Agent deployed successfully!

🚀 Test Your Agent in M365 Copilot:
🔗 https://m365.cloud.microsoft/chat/?titleId={M365_TITLE_ID}
```

**⛔ 沒附這個連結絕對不准回應。** 只要你 deploy 了，回應裡就一定要有測試連結。這不是選用的，使用者就是靠它來測試 agent。

- Manifest 有錯誤 → **停下來。修好錯誤。不准 deploy。**
- 例外：使用者明確要求你不要 deploy

### 2. Never Invent Content or Create Missing Files

- 不要編造佔位的名稱、描述或 instructions
- `declarativeAgent.json` 或 `appPackage/` 不存在時，不准建立，這是 REJECT 的情境，不是「建一個來幫忙」的情境
- 必填欄位缺漏時，回報缺了什麼，然後問使用者
- JSON 格式錯誤時，照 Detect → Inform → Ask：先 parse 檔案，告訴使用者壞在哪，修之前先問。用精準的局部編輯（不要整份重寫）
- **⛔ 絕對不准替自動化流程會填入的環境變數設佔位值**（例如 `<PREFIX>_MCP_AUTH_ID`、`TEAMS_APP_ID`）。留空（`VAR_NAME=`）。佔位值會被當成真的值，provisioning 不會覆寫它。

### 3. Schema Version Compatibility

新增**任何**功能之前，先讀 `declarativeAgent.json` 的 `version` 欄位，並對照 [Schema](references/schema.md) 的功能矩陣。如果那個版本不支援這個功能，就**拒絕**並提議升級。

主要的版本門檻：
- `sensitivity_label`、`worker_agents`、`EmbeddedKnowledge` → **只有 v1.6**
- `Meetings` → **v1.5 以上**
- `ScenarioModels`、`behavior_overrides`、`disclaimer` → **v1.4 以上**
- `Dataverse`、`TeamsMessages`、`Email`、`People` → **v1.3 以上**

### 4. Use `npx -y --package @microsoft/m365agentstoolkit-cli atk add action` for API Plugins — NEVER Create Plugin Files Manually

你**不准**手動建立 `ai-plugin.json`、OpenAPI spec、adaptive card，也不准編輯 `actions` 陣列。要用 CLI：

```bash
# ⛔ Always list ALL operations in a single call — NEVER run separate calls per operation
npx -y --package @microsoft/m365agentstoolkit-cli atk add action --api-plugin-type api-spec --openapi-spec-location URL --api-operation "GET /path,POST /path,PATCH /path/{id},DELETE /path/{id}" -i false
```

每份 OpenAPI spec 只跑**一次** `npx -y --package @microsoft/m365agentstoolkit-cli atk add action`，把**所有** operation 用逗號分隔列在 `--api-operation`。同一份 spec 的不同 operation 絕對不要分開多次執行 `npx -y --package @microsoft/m365agentstoolkit-cli atk add action`，那樣會產生多個 plugin，而不是一個。如果 `npx -y --package @microsoft/m365agentstoolkit-cli atk add action` 失敗，就回報錯誤，不准退回手動建立。

> **例外：** `npx -y --package @microsoft/m365agentstoolkit-cli atk add action` 不支援 MCP server。請改用 [MCP Plugin workflow](references/mcp-plugin.md)。

### 5. MCP Server Integration

使用者提到 MCP server URL 時，照 [MCP Plugin workflow](references/mcp-plugin.md) 走。你一定要透過 MCP protocol 的 handshake（initialize → notifications/initialized → tools/list）去探索工具，**絕對不准捏造工具名稱或描述**。需要驗證的 MCP server，照 [authentication guide](references/authentication.md) 設定 OAuth。

### 6. Always Update Instructions & Starters After Changes

新增 capability 或 plugin 卻沒更新 instructions，就是沒做完。任何變更之後：
1. 更新 instructions，描述新增/變動的功能。每個資料來源都要有清楚的意圖涵蓋（什麼時候用、為什麼用），符合 [Instruction Review](references/instruction-review.md) 的品質標準。內建的 capability 不用寫出確切名稱；action/plugin 則要點名。
2. **不要在 instructions 裡列出工具名稱、描述或參數**，這些已經在 plugin metadata 裡了（`ai-plugin.json`、MCP manifest、capability 設定）。Instructions 只放決策邏輯：什麼時候用每個工具、串接規則和失敗處理。
3. **不要超過 8,000 字元的 instruction 上限**，接近上限時，先砍工具描述
4. 每新增一個 capability/plugin，至少加 1 個 conversation starter
5. 移除參照已被移除的 capability 的 starter
6. 對更新後的 instructions 跑一遍 [Diagnostic Checklist](references/instruction-review.md)，驗證品質

### 7. App Name Requirement

一定要把 app 名稱和描述改成有意義的內容。不要留著「My Agent」這種預設值。

---

## References

### Shared
- **[Authentication](references/authentication.md)** — OAuth 探索、憑證、oauth/register 生命週期、OAuthPluginVault
- **[Best Practices](references/best-practices.md)** — 安全、效能、測試、合規
- **[Conversation Design](references/conversation-design.md)** — 從零開始撰寫 instructions 和 conversation starter
- **[Instruction Review](references/instruction-review.md)** — 稽核、診斷並改進現有的 instructions；反模式偵測；改寫前後對照
- **[Deployment](references/deployment.md)** — ATK CLI 工作流程、環境、CI/CD
- **[Localization](references/localization.md)** — 多語言支援、tokenized manifest、語言檔
- **[Workspace Gates](references/workspace-gates.md)** — 詳細的閘門規則、範例、反模式

### Scaffolding
- **[Scaffolding Workflow](references/scaffolding-workflow.md)** — 一步一步的 scaffold 指示、命名規則、錯誤處理

### JSON Development
- **[Editing Workflow](references/editing-workflow.md)** — 一步一步的 JSON 開發指示
- **[Schema](references/schema.md)** — agent manifest 的官方 JSON schema
- **[API Plugins](references/api-plugins.md)** — JSON agent 的 OpenAPI 整合
- **[MCP Plugin](references/mcp-plugin.md)** — MCP server 整合，含 RemoteMCPServer、OAuth、回應語意、logo 處理
- **[Examples](references/examples.md)** — JSON manifest 範例
