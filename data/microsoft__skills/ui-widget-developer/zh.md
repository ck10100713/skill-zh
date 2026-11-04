---
name: ui-widget-developer
description: |
  使用 OpenAI Apps SDK 或 MCP Apps SDK 的 widget 渲染支援（任何語言），為 Copilot Chat 建立 MCP server。符合以下情況時使用這個 skill：
  - 建立與 M365 Copilot declarative agent 整合的 MCP server
  - 建立在 Copilot Chat 中渲染的豐富互動式 widget（React + Fluent UI）
  - 實作會回傳 structuredContent 供 widget 渲染的工具
  - 把現有的 MCP server 改成支援 Copilot widget 渲染
  - 設定 devtunnel 來暴露 localhost 的 MCP server
  - 設定使用 RemoteMCPServer runtime 的 mcpPlugin.json manifest
  一般的 agent 開發（scaffold、manifest、deploy）不要用這個 skill，請改用 declarative-agent-developer。這個 skill 只負責 MCP server + widget 開發。
  Triggers: "MCP server for Copilot", "OpenAI Apps SDK", "Copilot widget", "structuredContent", "MCP plugin", "devtunnels MCP", "OAI app", "widget rendering", "UI widget"
---

# Copilot MCP Server 開發

## Telemetry 標記

跑任何 `atk` CLI 指令之前，先設定 session 環境變數，讓所有 CLI 呼叫都標記成由 skill 發起：
```bash
export ATK_CLI_SKILL=true
```
在 session 開頭執行一次。同一個終端機裡之後所有的 `atk` 指令都會繼承它。

## 🔀 選擇路徑

**繼續之前，先用 AskUserQuestion 問使用者想走哪條路徑。** 兩條路徑都支援 M365 Copilot 的 widget 渲染。把取捨攤開來，讓他們選：

| | **OAI Apps**（這個 skill） | **MCP Apps Extension**（`modelcontextprotocol/ext-apps`） |
|---|---|---|
| **標準** | OpenAI 專屬 | 官方 MCP 標準 |
| **可用於** | ChatGPT + M365 Copilot | M365 Copilot、ChatGPT、VSCode 等等 |
| **成熟度** | 久經考驗，可上正式環境 | 新的官方標準，生態系成長中 |
| **設計** | OpenAI Apps SDK | MCP Apps 協定（跨平台） |
| **什麼時候選** | 已經投資了現有的 OAI app | 偏好開放標準，想要最廣的 client 支援 |

**要問的問題：** _"Would you like to build an OAI app (OpenAI Apps SDK — battle-tested, works in ChatGPT and M365 Copilot) or an MCP app (new official standard — works in M365 Copilot, ChatGPT, VSCode, and more)?"_

- **OAI apps** → 繼續往下。這個 skill 涵蓋你需要的所有東西。
- **MCP apps** → 安裝 `modelcontextprotocol/ext-apps` plugin（見下方），再用該 plugin 裡適當的 skill。

### MCP Apps：安裝 ext-apps Plugin

如果使用者選 MCP Apps，就自動做這些事（不要只停在說明）：

1. 執行 `/plugin marketplace add modelcontextprotocol/ext-apps`
2. 執行 `/plugin install mcp-apps@mcp-apps`
3. 確認 plugin 可用，然後依使用者意圖呼叫正確的 ext-apps skill

如果目前環境無法使用 plugin 指令，就提供下面的確切指令，請使用者執行一次，然後繼續呼叫選定的 ext-apps skill。

參考指令：

```
To build an MCP App, install the ext-apps plugin from the marketplace:

1. /plugin marketplace add modelcontextprotocol/ext-apps
2. /plugin install mcp-apps@mcp-apps

Then use one of these skills from that plugin:
- create-mcp-app      — Scaffold a new MCP App with interactive UI from scratch
- add-app-to-server   — Add interactive UI to an existing MCP server's tools
- migrate-oai-app     — Convert an existing OAI app to use MCP Apps
- convert-web-app     — Turn a web app into a hybrid web + MCP App

After installing, invoke the relevant skill to continue.
```

> **注意：** ext-apps plugin 放在外部的 `modelcontextprotocol/ext-apps` marketplace，它不屬於這個 plugin 集合。

**安裝後的交接對應：**
- 從零開始的新 MCP app → `create-mcp-app`
- 為現有的 MCP server 加 app UI → `add-app-to-server`
- 遷移現有的 OAI app → `migrate-oai-app`
- 轉換現有的 web app → `convert-web-app`

---

## 📛 專案偵測 📛

當為 Microsoft 365 Copilot Chat 建立帶有 OAI app 或 widget 渲染的 MCP server 時，會觸發這個 skill。MCP server 可以用任何支援 MCP 協定的語言撰寫（TypeScript、Python、C# 等）。Agent 專案和 MCP server 可以放在同一個 repo、不同資料夾，或完全不同的專案。

## 情境路由

| 起點 | 你需要什麼 | 路徑 |
|---------------|---------------|------|
| **偏好 MCP Apps 標準** | 跨平台的 widget 支援（M365 Copilot、ChatGPT、VSCode 等等） | 安裝 `modelcontextprotocol/ext-apps`，再用 `create-mcp-app` 或 `add-app-to-server`，見上方[選擇路徑](#-path-selection) |
| **從零開始**（沒有 agent、沒有 MCP server） | 完整的 OAI app 設定 | 先把 agent scaffold 委派給 `declarative-agent-developer`，再回到這裡做 MCP server + widget |
| **已有 M365 agent，要新的 MCP server** | MCP server + widget + mcpPlugin.json | 從[實作](#implementation)開始 |
| **已有 MCP server，要加 Copilot widget** | 為現有 server 加上 widget 支援 | 從 [Copilot Widget Protocol](references/copilot-widget-protocol.md#adaptation-checklist-existing-mcp-server) 開始 |
| **語言選擇**（非 TypeScript） | 協定要求 | 要實作什麼請看 [Copilot Widget Protocol](references/copilot-widget-protocol.md)，參考範例請看 [MCP Server Pattern (TypeScript)](references/mcp-server-pattern.md) |

---

## 🚨 關鍵執行規則 🚨


**強制使用 FLUENT UI（必要）：** Widget 實作一定要使用 React + Fluent UI 元件。寫任何 widget 程式碼之前，agent 一定要先讀並遵守：
- `references/widget-patterns.md`
- `references/best-practices.md`
**FLUENT UI 套件要求（必要）：** 實作之前，widget 專案一定要包含 Fluent UI 相依套件。至少要安裝這些，並留在 widget 的套件相依裡：
- `@fluentui/react-components`
- `react`
- `react-dom`

如果缺少其中任何一個，在繼續產生 widget 程式碼之前要自動安裝。

如果產生出來的 widget 沒有 React 進入點檔案（例如 `widgets/src/<widget-name>/main.tsx` 和一個 React 元件檔），也沒有從 `@fluentui/react-components` import Fluent，這個任務就算沒完成，回報結果之前一定要修正。

**不要做純 HTML 的 WIDGET（預設）：** 不要用靜態 HTML 範本加 inline JS 直接實作 app 內容，當作最終的 widget 方案。只有在當作載入 build 後 React 資產的 loader 時，才允許用最小的 shell HTML 檔案。只有使用者明確要求非 React 的 prototype 時，才允許純 HTML、自成一體的 widget。

**背景程序：** MCP server 和 devtunnel 一定要以獨立的 OS 程序啟動，不能跑在 agent 的 shell session 裡。`isBackground: true`、`mode: "async"` 和 `Start-Job` 全都是跑在 agent 的 shell session 裡，訊息之間會被砍掉。唯一可靠的做法是啟動一個脫離的 OS 程序。

**Windows：用 `Start-Process -WindowStyle Hidden`：**
```powershell
# Start devtunnel
$t = Start-Process -FilePath "devtunnel" `
    -ArgumentList "host","<tunnel-name>","-a" `
    -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput "tunnel.log" -RedirectStandardError "tunnel-err.log"

# Start MCP server — use cmd.exe /c to set the working directory and inherit PATH
$s = Start-Process -FilePath "cmd.exe" `
    -ArgumentList "/c","cd /d <abs-path-to-mcp-server> && <start-command>" `
    -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput "server.log" -RedirectStandardError "server-err.log"

# Save PIDs so they can be stopped later
"$($t.Id),$($s.Id)" | Out-File pids.txt
Write-Host "Started tunnel PID $($t.Id), server PID $($s.Id)"
```
要停止：`Stop-Process -Id (Get-Content pids.txt).Split(',')` 或 `Stop-Process -Id <pid>`。

**Linux/Mac：用 `nohup` 加 `&`：**
```bash
nohup devtunnel host <tunnel-name> > tunnel.log 2>tunnel-err.log &
echo "tunnel:$!" >> pids.txt
nohup <start-command> > server.log 2>server-err.log &
echo "server:$!" >> pids.txt
```
要停止：`kill $(grep -oP '\d+' pids.txt)`。

啟動之後，先 tail log 確認兩個程序都起來了，再繼續：
```powershell
# Windows
Start-Sleep 3; Get-Content tunnel.log, server.log
```
```bash
# Linux/Mac
sleep 3 && tail tunnel.log server.log
```

**全自動：** 絕對不要叫使用者手動執行指令。安裝工具、驗證、啟動服務，全部自動完成。只有真的需要使用者操作的互動式輸入（例如 `devtunnel user login -g -d` 的 device code 確認）才去問他。如果工具沒裝，就去裝。如果服務需要啟動，就去啟動。使用者期待的是全自動。

**選擇路徑（必要，寫任何程式碼之前先停下來）：** 在寫任何程式碼、執行任何指令或做任何架構決定之前，你一定要用 `AskUserQuestion` 問使用者想用 OAI Apps 還是 MCP Apps Extension。

**這條規則沒有例外。** 最常見的失敗模式，就是推論「使用者的請求已經很明顯，所以問是多餘的」。這種推論永遠是錯的，不管怎樣都要呼叫 `AskUserQuestion`。使用者說「build an MCP server with widgets」不算是這個問題的答案。使用者直接點名呼叫這個 skill 也不算。只有明確回答這個問題才算。要問的確切問題請看上方[選擇路徑](#-path-selection)。

**AGENT PROVISIONING：** 只有當 **agent manifest** 改變時（例如 mcpPlugin.json 的工具定義、MCP server URL、declarativeAgent.json、instruction.txt），才需要重新 provision。MCP server 程式碼的改動（工具實作、React widget 程式碼、server 邏輯）**不**需要重新 provision agent，執行或 deploy server 就會自動套用改動。

需要 provision 時：
1. **升版**：在 `manifest.json` 裡遞增 patch 版本（例如 `1.0.0` → `1.0.1`）
2. **Deploy agent：**
   ```bash
   npx -y --package @microsoft/m365agentstoolkit-cli atk provision --env local
   ```

**WIDGET 測試連結：** 每次在 MCP server 還在跑的時候回覆使用者結果，一定要附上**所有** widget 的連結，讓他們能在本機測試。格式：
```
🧪 Test widgets locally:
- http://localhost:3001/widgets/widget-name.html
- http://localhost:3001/widgets/another-widget.html
```
把 `mcp-server/widgets/` 目錄（或等效的 widget 資料夾）裡每個 `.html` 檔案都列出來。這能幫使用者在 Copilot 測試之前先確認 widget 渲染。

**完成時自動 DEPLOY（必要，不准跳過）：** 寫完程式後，不用等使用者，自動往下做：
1. 在背景啟動 MCP server + devtunnel（照上面的「背景程序」）
2. 用 MCP Inspector 跑 E2E 驗證（照下面的「MCP 工具設定規則」），有失敗要先修好才能繼續
3. 需要的話 provision agent（照上面的 AGENT PROVISIONING）
4. 用這個格式印出專案摘要：
```
## ✅ <Project Name> — Ready

### Widgets
- [widget-name.html](http://localhost:<PORT>/widgets/widget-name.html)
- [widget-name2.html](http://localhost:<PORT>/widgets/widget-name2.html)

### Endpoints
- MCP server: http://localhost:<PORT>/mcp
- MCP via tunnel: https://<tunnel-url>/mcp

### Test in Copilot
Local:      https://m365.cloud.microsoft/chat/?titleId={M365_TITLE_ID from env/.env.local}
Other envs: {SHARE_LINK from env/.env.{environment}}
```

**AGENT 專案委派：** 這個 skill 建的是 MCP server 和 widget，不是 declarative agent 專案。如果使用者的請求涉及建立或設定 declarative agent 本身（scaffold、`m365agents.yml`、`m365agents.local.yml`、`declarativeAgent.json`、manifest 生命週期），就委派給 `declarative-agent-developer` skill。

**MCP RESOURCE 註冊：** 每個 widget 一定要有對應的 MCP resource。沒有 resource，Copilot 就無法透過 MCP 協定取得 widget shell，widget 也就不會渲染。

每個新 widget 都要完成這份檢查清單：
1. ☐ 在 `widgets/` 建立 widget shell HTML 檔，並在 `widgets/src/<widget-name>/` 底下建立 React widget 進入點（見 widget-patterns.md）
2. ☐ 定義一個 `ui://widget/<name>.html` URI 常數
3. ☐ 在 `resources` 陣列加入一筆 `Resource`，包含：
   - `uri`：`ui://widget/<name>.html` URI
   - `mimeType`：`"text/html+skybridge"`
   - `_meta`：帶有 `openai/widgetDomain` 和 `openai/widgetCSP` 的 CSP 設定（來自環境）
4. ☐ 加一個 `resources/read` 的 handler，針對這個 URI 回傳 widget shell HTML
5. ☐ 加入工具，並讓 `_meta.openai/outputTemplate` 指向同一個 `ui://widget/<name>.html` URI
6. ☐ 確認 server 的 initialize 回應裡，capabilities 有包含 `resources: {}`

**Widget shell 與資產的考量：**
- **偏好（React + Fluent UI）**：Resource HTML 應該是最小的 shell，連結到由 MCP server 的 `/assets/` 路由提供的 build 後 JS/CSS 資產。
- **僅限例外**：透過 `resources/read` 提供自成一體的 HTML，只用於使用者明確要求的 prototype。預設和正式環境的路徑是 React + Fluent UI。

React build 輸出的 shell 範例：
  ```html
  <!doctype html><html><head>
    <script type="module" src="${serverUrl}/assets/my-widget.js"></script>
    <link rel="stylesheet" href="${serverUrl}/assets/my-widget.css">
  </head><body>
    <div id="widget-root"></div>
  </body></html>
  ```
  資產 URL 的 base 用 `WIDGET_BASE_URL` 或 `MCP_SERVER_URL` 環境變數（見 mcp-server-pattern.md 的「Configurable Widget Base URL」段落）。

完整的 resource 和資產提供模式請看 [mcp-server-pattern.md](references/mcp-server-pattern.md)。

---

## ⚠️ MCP 工具設定規則 ⚠️

**絕對不要手動在 `mcpPlugin.json` 寫工具定義。** 一律用 MCP Inspector 從執行中的 MCP server 取得完整的工具定義。

**工具命名慣例：** 工具名稱一定要符合 `^[A-Za-z0-9_]+$` 這個 pattern（只能有字母、數字和底線）。**絕對不要在工具名稱裡用連字號（-）。** 改用底線（例如用 `render_profile`，不要用 `render-profile`）。

**強制流程：**
1. **啟動 MCP server**（在背景）
2. **用 MCP Inspector** 取得最新的工具定義：
   ```bash
   npx @modelcontextprotocol/inspector@0.20.0 --cli https://my-mcp-server.example.com --transport http --method tools/list
   ```
3. 從 inspector **複製完整的工具定義**（包含 `name`、`description`、`inputSchema`、`_meta`、`annotations`、`title`）
4. **貼到 `mcpPlugin.json`** 的 `runtimes[].spec.mcp_tool_description.tools` 底下（在 `RemoteMCPServer` runtime 的 `spec` 物件裡）
5. 透過 devtunnel **跑 E2E 驗證**：呼叫每個工具，確認回應包含 `structuredContent` 和 `_meta.openai/widgetAccessible: true`：
   ```bash
   npx @modelcontextprotocol/inspector@0.20.0 --cli https://<tunnel-url>/mcp --transport http --method tools/call --tool-name <tool_name>
   ```
   同時確認 `GET https://<tunnel-url>/health` 回傳 `{"status":"ok"}`。provision 之前要先修好所有失敗。

MCP Inspector 會顯示你的 server 的確切工具 schema。要完整複製，不要手動寫或修改這些定義。這樣才能確保 `mcpPlugin.json` 和 MCP server 保持同步。

---

建立與 Microsoft 365 Copilot Chat 整合、並渲染豐富互動式 widget 的 MCP server。

## 架構

```
M365 Copilot ──▶ mcpPlugin.json ──▶ MCP Server ──▶ structuredContent ──▶ React + Fluent UI Widget
     │              (RemoteMCPServer)    (Streamable HTTP)                  (window.openai.toolOutput)
     │
     └── Capabilities (People, etc.) provide data to pass to MCP tools
```

## 專案結構

專案結構範例，不是硬性規定，只是組織 MCP server + widget 開發常見的做法：

```
project/
├── appPackage/
│   ├── manifest.json           # Teams manifest (bump version on deploy)
│   ├── declarativeAgent.json   # Agent config + capabilities
│   ├── mcpPlugin.json          # Tool definitions with _meta
│   └── instruction.txt         # Agent behavior instructions
├── mcp-server/
│   ├── src/index.ts            # Server with Streamable HTTP
│   ├── widgets/                # Widget shells + React source
│   │   ├── my-widget.html      # Minimal shell returned by resources/read
│   │   └── src/my-widget/      # React + Fluent UI source
│   ├── assets/                 # Built widget bundles served at /assets
│   └── package.json
├── scripts/
│   ├── setup-devtunnel.sh      # Linux/Mac devtunnel setup
│   └── setup-devtunnel.ps1     # Windows devtunnel setup
└── env/.env.local              # MCP_SERVER_URL, MCP_SERVER_DOMAIN
```

**語言備註**：這裡呈現的是 TypeScript 專案的結構。如果是 Python，把 `mcp-server/src/index.ts` 換成你的 Python 進入點（例如 `server.py`）。如果是 C#，就用標準的 .NET 專案結構。`appPackage/`、`widgets/`、`scripts/` 和 `env/` 目錄跟語言無關。

## Copilot Widget Protocol

你的 MCP server 必須實作這些協定要求，才能在 Copilot Chat 裡渲染 widget。不管用什麼語言都適用：

1. **Streamable HTTP transport**：`/mcp` endpoint 處理 POST、GET、DELETE，並帶有 session 管理
2. **CORS headers**：在 `/mcp` 檢查 Origin，允許 `m365.cloud.microsoft` 和 `*.m365.cloud.microsoft`，並帶有必要的 MCP headers
3. **Server capabilities**：`initialize` 回應一定要宣告 `resources: {}` 和 `tools: {}`
4. **MCP resources**：用 `ui://widget/<name>.html` URI、`text/html+skybridge` mime type 和 CSP `_meta` 註冊 widget
5. **工具回應格式**：回傳 `content`（文字）+ `structuredContent`（widget 資料）+ 帶有 `openai/outputTemplate` 的 `_meta`
6. **Widget 提供**：shell 檔案用 `/widgets/*.html` 的 HTTP 路由，build 後的 bundle 用 `/assets/*`，兩者都要有檢查 origin 的 CORS

完整的協定細節、JSON 結構，以及現有 MCP server 的改寫檢查清單，請看 [references/copilot-widget-protocol.md](references/copilot-widget-protocol.md)。

## 實作

### MCP Server Pattern（TypeScript 參考）

完整實作請看 [references/mcp-server-pattern.md](references/mcp-server-pattern.md)。

> 其他語言請用該語言的 MCP SDK，實作 [Copilot Widget Protocol](references/copilot-widget-protocol.md) 裡描述的要求。SDK 套件請看 [Language SDK References](references/copilot-widget-protocol.md#language-sdk-references) 表格。

核心要求：
- 在 `/mcp` 提供 Streamable HTTP transport
- 回傳 `structuredContent` + 帶有 `openai/outputTemplate` 的 `_meta`
- 透過 HTTP endpoint 提供 widget
- 處理跨來源請求的 CORS
- 優雅地處理不完整的資料（缺少的欄位填入「Unknown」）

工具回應格式：
```typescript
return {
  content: [{ type: "text", text: "Summary" }],
  structuredContent: { /* widget data */ },
  _meta: { "openai/outputTemplate": "ui://widget/name.html", "openai/widgetAccessible": true }
};
```

### 處理不完整的資料

輸入資料一定要先正規化，以處理缺少的欄位：

```typescript
server.setRequestHandler(CallToolRequestSchema, async (request: CallToolRequest) => {
  const args = request.params.arguments as { title?: string; items?: Partial<Item>[] };

  // Normalize data - fill in "Unknown" for missing fields
  const title = args.title || "Default Title";
  const items = (args.items || []).map(item => ({
    name: item.name || "Unknown",
    value: item.value || "Unknown",
  }));

  // Build structuredContent for widget
  const structuredContent = { title, items };
  // ...
});
```

### Widget Pattern

完整範例請看 [references/widget-patterns.md](references/widget-patterns.md)。

核心要求：
- 使用 React + Fluent UI 元件（`@fluentui/react-components`）
- 確保 widget 的套件相依包含 `@fluentui/react-components`、`react` 和 `react-dom`
- 用 `FluentProvider`（`webLightTheme`/`webDarkTheme`）和 Fluent `tokens` 做主題
- 透過共用的 hook 存取資料（例如 `useOpenAiGlobal("toolOutput")`）
- Debug 備案：`window.openai` 不存在時使用內嵌的 mock 資料
- 優雅地處理「Unknown」值（例如隱藏動作按鈕）

### Plugin Schema

mcpPlugin.json 的格式請看 [references/plugin-schema.md](references/plugin-schema.md)。

核心要求：
- 帶有 `RemoteMCPServer` runtime 的 Schema `v2.4`
- 和工具名稱相符的 `run_for_functions` 陣列
- 工具定義裡用 `_meta` 做 widget 綁定
- `inputSchema`：屬性設為選填以保持彈性，預設值寫在 description 裡

## DevTunnels 設定

> **只用於本機測試。** DevTunnels 是用來在你自己的機器上開發和測試。在更廣泛地分享 agent 之前，要把 MCP server 和 widget 資產都 deploy 到託管環境（例如 Azure App Service、Azure Static Web Apps 或其他 hosting 供應商），並相應更新 agent manifest 的 URL。

DevTunnels 用**具名 tunnel** 取得穩定的 URL，把你 localhost 的 MCP server 暴露給 M365 Copilot。設定 script、指令參考和疑難排解請看 [references/devtunnels.md](references/devtunnels.md)。

設定 script（`npm run tunnel` / `npm run tunnel:win`）會：
1. 第一次執行時建立具名 tunnel（或重用現有的）
2. 開始在設定的 port 上 host 這個 tunnel
3. 用 `MCP_SERVER_URL` 和 `MCP_SERVER_DOMAIN` 更新 `env/.env.local`（只有第一次）
4. 持續 host 這個 tunnel

### 快速開始

**終端機 1：啟動 MCP Server：**
```bash
cd mcp-server
npm install
npm run dev
```

**終端機 2：啟動 DevTunnel：**
```bash
npm run tunnel
# Or on Windows:
npm run tunnel:win
```

第一次執行時，等 tunnel 起來後要 provision 一次 agent（見 AGENT PROVISIONING 規則）。之後的執行，tunnel URL 是穩定的，除非 agent manifest 有改變，否則不用重新 provision。

## 開發流程

1. **啟動 MCP server**（開發模式，支援 hot reload）：
   - TypeScript：`cd mcp-server && npm install && npm run dev`
   - Python：`cd mcp-server && pip install -r requirements.txt && python server.py`
   - C#：`cd mcp-server && dotnet run`

2. **啟動 devtunnel**（第一次執行時建立具名 tunnel，之後重用）：
   ```bash
   npm run tunnel
   ```

3. **Provision + 測試**：什麼時候需要請看 AGENT PROVISIONING 規則；如果 Copilot 沒反映出改動，就把 manifest.json 的 `version` 升版

## 最佳實務

詳細指引請看 [references/best-practices.md](references/best-practices.md)。

重點：
1. **渲染工具**：接收資料當輸入，不要在內部去抓資料
2. **Instructions**：告訴 agent 先用 capabilities，再把資料傳給 MCP 工具
3. **主題**：用 `FluentProvider` + Fluent `tokens` 支援深色/淺色模式
4. **Debug 模式**：包含備用資料，方便在本機測試 widget
5. **不完整的資料**：缺少的欄位用「Unknown」預設值處理
6. **動作按鈕**：資料是「Unknown」時隱藏 email/聊天按鈕
7. **升版**：改動沒有反映在 Copilot 時，就升 manifest 版本
