---
name: copilot-sdk
description: 用 Copilot SDK 建立由 GitHub Copilot 驅動的應用程式。要在 Node.js/TypeScript、Python、Go 或 .NET 以程式方式整合 Copilot 時使用。涵蓋 session 管理、自訂工具、streaming、hook、MCP server、BYOK provider、session 持久化、自訂 agent、skill 與部署模式。需要安裝 GitHub Copilot CLI 並有 GitHub Copilot 訂閱（使用 BYOK 則不需要）。
---

# GitHub Copilot SDK

建立能以程式方式和 GitHub Copilot 互動的應用程式。這個 SDK 透過 JSON-RPC 包裝 Copilot CLI，在 Node.js、Python、Go 和 .NET 上提供 session 管理、自訂工具、hook、MCP server 整合和 streaming。

## Prerequisites

- 已安裝並登入 **GitHub Copilot CLI**（`copilot --version`）
- **GitHub Copilot 訂閱**（Individual、Business 或 Enterprise），BYOK 不需要
- **Runtime:** Node.js 18+ / Python 3.8+ / Go 1.21+ / .NET 8.0+

## Installation

| Language | Package | Install |
|----------|---------|---------|
| Node.js | `@github/copilot-sdk` | `npm install @github/copilot-sdk` |
| Python | `github-copilot-sdk` | `pip install github-copilot-sdk` |
| Go | `github.com/github/copilot-sdk/go` | `go get github.com/github/copilot-sdk/go` |
| .NET | `GitHub.Copilot.SDK` | `dotnet add package GitHub.Copilot.SDK` |

## Architecture

SDK 透過 stdio（預設）或 TCP 上的 JSON-RPC 和 Copilot CLI 溝通。CLI 負責管理模型呼叫、工具執行、session 狀態和 MCP server 的生命週期。

```
Your App → SDK Client → [stdio/TCP] → Copilot CLI → Model Provider
                                          ↕
                                     MCP Servers
```

**Transport modes:**

| Mode | Description | Use Case |
|------|-------------|----------|
| **Stdio**（預設） | CLI 當成 subprocess，用 pipe 溝通 | 本機開發、單一 process |
| **TCP** | CLI 當成網路伺服器 | 多個 client、後端服務 |

---

## Core Pattern: Client → Session → Message

所有 SDK 用法都是同一個流程：建立 client、建立 session、傳送訊息。

### Node.js / TypeScript

```typescript
import { CopilotClient } from "@github/copilot-sdk";

const client = new CopilotClient();
const session = await client.createSession({ model: "gpt-4.1" });

const response = await session.sendAndWait({ prompt: "What is 2 + 2?" });
console.log(response?.data.content);

await client.stop();
```

### Python

```python
import asyncio
from copilot import CopilotClient

async def main():
    client = CopilotClient()
    await client.start()
    session = await client.create_session({"model": "gpt-4.1"})
    response = await session.send_and_wait({"prompt": "What is 2 + 2?"})
    print(response.data.content)
    await client.stop()

asyncio.run(main())
```

### Go

```go
client := copilot.NewClient(nil)
if err := client.Start(ctx); err != nil { log.Fatal(err) }
defer client.Stop()

session, _ := client.CreateSession(ctx, &copilot.SessionConfig{Model: "gpt-4.1"})
response, _ := session.SendAndWait(ctx, copilot.MessageOptions{Prompt: "What is 2 + 2?"})
fmt.Println(*response.Data.Content)
```

### .NET

```csharp
await using var client = new CopilotClient();
await using var session = await client.CreateSessionAsync(new SessionConfig { Model = "gpt-4.1" });
var response = await session.SendAndWaitAsync(new MessageOptions { Prompt = "What is 2 + 2?" });
Console.WriteLine(response?.Data.Content);
```

---

## Streaming Responses

設定 `streaming: true` 並訂閱 delta 事件，就能即時輸出。

### Node.js

```typescript
const session = await client.createSession({ model: "gpt-4.1", streaming: true });

session.on("assistant.message_delta", (event) => {
    process.stdout.write(event.data.deltaContent);
});
session.on("session.idle", () => console.log());

await session.sendAndWait({ prompt: "Tell me a joke" });
```

### Python

```python
from copilot.generated.session_events import SessionEventType

session = await client.create_session({"model": "gpt-4.1", "streaming": True})

def handle_event(event):
    if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
        sys.stdout.write(event.data.delta_content)
        sys.stdout.flush()
    if event.type == SessionEventType.SESSION_IDLE:
        print()

session.on(handle_event)
await session.send_and_wait({"prompt": "Tell me a joke"})
```

### Event Subscription

| Method | Description |
|--------|-------------|
| `on(handler)` | 訂閱所有事件；回傳取消訂閱的函式 |
| `on(eventType, handler)` | 訂閱特定事件類型（僅限 Node.js） |

要取消訂閱就呼叫回傳的函式。在 .NET 裡，對回傳的 disposable 呼叫 `.Dispose()`。

---

## Custom Tools

定義 Copilot 可以呼叫的工具，擴充它的能力。

### Node.js

```typescript
import { CopilotClient, defineTool } from "@github/copilot-sdk";

const getWeather = defineTool("get_weather", {
    description: "Get the current weather for a city",
    parameters: {
        type: "object",
        properties: { city: { type: "string", description: "The city name" } },
        required: ["city"],
    },
    handler: async ({ city }) => ({ city, temperature: "72°F", condition: "sunny" }),
});

const session = await client.createSession({
    model: "gpt-4.1",
    tools: [getWeather],
});
```

### Python

```python
from copilot.tools import define_tool
from pydantic import BaseModel, Field

class GetWeatherParams(BaseModel):
    city: str = Field(description="The city name")

@define_tool(description="Get the current weather for a city")
async def get_weather(params: GetWeatherParams) -> dict:
    return {"city": params.city, "temperature": "72°F", "condition": "sunny"}

session = await client.create_session({"model": "gpt-4.1", "tools": [get_weather]})
```

### Go

```go
type WeatherParams struct {
    City string `json:"city" jsonschema:"The city name"`
}

getWeather := copilot.DefineTool("get_weather", "Get weather for a city",
    func(params WeatherParams, inv copilot.ToolInvocation) (WeatherResult, error) {
        return WeatherResult{City: params.City, Temperature: "72°F"}, nil
    },
)

session, _ := client.CreateSession(ctx, &copilot.SessionConfig{
    Model: "gpt-4.1",
    Tools: []copilot.Tool{getWeather},
})
```

### .NET

```csharp
using Microsoft.Extensions.AI;
using System.ComponentModel;

var getWeather = AIFunctionFactory.Create(
    ([Description("The city name")] string city) => new { city, temperature = "72°F" },
    "get_weather", "Get the current weather for a city");

await using var session = await client.CreateSessionAsync(new SessionConfig {
    Model = "gpt-4.1", Tools = [getWeather],
});
```

### Tool Requirements

- handler 必須回傳可 JSON 序列化的資料（不能是 `undefined`）
- 參數必須符合 JSON Schema 格式
- 工具的 description 要清楚說明什麼時候該用這個工具

---

## Hooks

在 session 生命週期的關鍵時間點攔截並客製化行為。

| Hook | Trigger | Use Case |
|------|---------|----------|
| `onPreToolUse` | 工具執行前 | 權限控管、修改參數 |
| `onPostToolUse` | 工具執行後 | 轉換結果、記錄 log、遮蔽敏感資料 |
| `onUserPromptSubmitted` | 使用者送出訊息 | 修改 prompt、過濾、注入 context |
| `onSessionStart` | Session 開始（新建或恢復） | 加入 context、設定 session |
| `onSessionEnd` | Session 結束 | 清理、分析、metrics |
| `onErrorOccurred` | 發生錯誤 | 自訂錯誤處理、重試邏輯、監控 |

### Pre-Tool Use Hook

在工具執行前控制工具權限、修改參數或注入 context。

```typescript
const session = await client.createSession({
    hooks: {
        onPreToolUse: async (input) => {
            if (["shell", "bash"].includes(input.toolName)) {
                return { permissionDecision: "deny", permissionDecisionReason: "Shell access not permitted" };
            }
            return { permissionDecision: "allow" };
        },
    },
});
```

**Input fields:** `timestamp`, `cwd`, `toolName`, `toolArgs`

**Output fields:**

| Field | Type | Description |
|-------|------|-------------|
| `permissionDecision` | `"allow"` \| `"deny"` \| `"ask"` | 是否允許這次工具呼叫 |
| `permissionDecisionReason` | string | deny/ask 的原因說明 |
| `modifiedArgs` | object | 修改後要傳入的參數 |
| `additionalContext` | string | 加進對話的額外 context |
| `suppressOutput` | boolean | 不要在對話中顯示工具輸出 |

### Post-Tool Use Hook

工具執行後轉換結果、遮蔽敏感資料，或記錄工具活動。

```typescript
hooks: {
    onPostToolUse: async (input) => {
        // 遮蔽結果中的敏感資料
        if (typeof input.toolResult === "string") {
            let redacted = input.toolResult;
            for (const pattern of SENSITIVE_PATTERNS) {
                redacted = redacted.replace(pattern, "[REDACTED]");
            }
            if (redacted !== input.toolResult) {
                return { modifiedResult: redacted };
            }
        }
        return null; // 原樣放行
    },
}
```

**Output fields:** `modifiedResult`, `additionalContext`, `suppressOutput`

### User Prompt Submitted Hook

在處理之前修改或強化使用者的 prompt。適合用在 prompt 範本、注入 context 和輸入驗證。

```typescript
hooks: {
    onUserPromptSubmitted: async (input) => {
        return {
            modifiedPrompt: `[User from engineering team] ${input.prompt}`,
            additionalContext: "Follow company coding standards.",
        };
    },
}
```

**Output fields:** `modifiedPrompt`, `additionalContext`, `suppressOutput`

### Session Lifecycle Hooks

```typescript
hooks: {
    onSessionStart: async (input, invocation) => {
        // input.source: "startup" | "resume" | "new"
        console.log(`Session ${invocation.sessionId} started (${input.source})`);
        return { additionalContext: "Project uses TypeScript and React." };
    },
    onSessionEnd: async (input, invocation) => {
        // input.reason: "complete" | "error" | "abort" | "timeout" | "user_exit"
        await recordMetrics({ sessionId: invocation.sessionId, reason: input.reason });
        return null;
    },
}
```

### Error Handling Hook

```typescript
hooks: {
    onErrorOccurred: async (input) => {
        // input.errorContext: "model_call" | "tool_execution" | "system" | "user_input"
        // input.recoverable: boolean
        if (input.errorContext === "model_call" && input.error.includes("rate")) {
            return { errorHandling: "retry", retryCount: 3, userNotification: "Rate limited. Retrying..." };
        }
        return null; // 預設的錯誤處理
    },
}
```

**Output fields:** `suppressOutput`, `errorHandling` (`"retry"` | `"skip"` | `"abort"`), `retryCount`, `userNotification`

### Python Hook Example

```python
async def on_pre_tool_use(input_data, invocation):
    if input_data["toolName"] in ["shell", "bash"]:
        return {"permissionDecision": "deny", "permissionDecisionReason": "Not permitted"}
    return {"permissionDecision": "allow"}

session = await client.create_session({
    "hooks": {"on_pre_tool_use": on_pre_tool_use}
})
```

### Go Hook Example

```go
session, _ := client.CreateSession(ctx, &copilot.SessionConfig{
    Hooks: &copilot.SessionHooks{
        OnPreToolUse: func(input copilot.PreToolUseHookInput, inv copilot.HookInvocation) (*copilot.PreToolUseHookOutput, error) {
            return &copilot.PreToolUseHookOutput{PermissionDecision: "allow"}, nil
        },
    },
})
```

---

## MCP Server Integration

連接 MCP（Model Context Protocol）server，取得現成的工具能力。

### Local Stdio Server

```typescript
const session = await client.createSession({
    mcpServers: {
        filesystem: {
            type: "local",
            command: "npx",
            args: ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"],
            tools: ["*"],
            env: { DEBUG: "true" },
            cwd: "./servers",
            timeout: 30000,
        },
    },
});
```

### Remote HTTP Server

```typescript
const session = await client.createSession({
    mcpServers: {
        github: {
            type: "http",
            url: "https://api.githubcopilot.com/mcp/",
            headers: { Authorization: "Bearer ${TOKEN}" },
            tools: ["*"],
        },
    },
});
```

### MCP Config Fields

**Local/Stdio:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"local"` | No | 預設為 local |
| `command` | string | Yes | 可執行檔路徑 |
| `args` | string[] | Yes | 指令參數 |
| `env` | object | No | 環境變數 |
| `cwd` | string | No | 工作目錄 |
| `tools` | string[] | No | `["*"]` 代表全部，`[]` 代表都不要 |
| `timeout` | number | No | Timeout，單位毫秒 |

**Remote HTTP:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"http"` | Yes | Server 類型 |
| `url` | string | Yes | Server URL |
| `headers` | object | No | HTTP header |
| `tools` | string[] | No | 工具過濾 |
| `timeout` | number | No | Timeout，單位毫秒 |

### MCP Debugging

整合之前，先單獨測試 MCP server：

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | /path/to/your/mcp-server
```

用 MCP Inspector 做互動式除錯：

```bash
npx @modelcontextprotocol/inspector /path/to/your/mcp-server
```

**常見的 MCP 問題：**
- 工具沒出現 → 設 `tools: ["*"]`，並確認 server 有回應 `tools/list`
- Server 啟動不了 → 用指令的絕對路徑，檢查 `cwd`
- Stdout 被污染 → debug 輸出一定要送到 stderr，不能送到 stdout

---

## Authentication

### Methods (Priority Order)

1. **Explicit token** — constructor 裡的 `githubToken`
2. **HMAC key** — `CAPI_HMAC_KEY` 或 `COPILOT_HMAC_KEY` 環境變數
3. **Direct API token** — `GITHUB_COPILOT_API_TOKEN` 搭配 `COPILOT_API_URL`
4. **Environment variables** — `COPILOT_GITHUB_TOKEN` → `GH_TOKEN` → `GITHUB_TOKEN`
5. **Stored OAuth** — 來自 `copilot auth login`
6. **GitHub CLI** — `gh auth` 的憑證

### Programmatic Token

```typescript
const client = new CopilotClient({ githubToken: process.env.GITHUB_TOKEN });
```

### OAuth GitHub App

給使用者用 GitHub 登入的多使用者應用：

```typescript
const client = new CopilotClient({
    githubToken: userAccessToken,    // gho_ or ghu_ token from OAuth flow
    useLoggedInUser: false,          // Don't use stored CLI credentials
});
```

**支援的 token 類型：** `gho_`（OAuth）、`ghu_`（GitHub App）、`github_pat_`（fine-grained PAT）。
**不支援：** `ghp_`（classic PAT，已棄用）。

### Disable Auto-Login

不讓 SDK 使用已儲存的憑證：

```typescript
const client = new CopilotClient({ useLoggedInUser: false });
```

---

## BYOK (Bring Your Own Key)

用你自己的 API key，不需要 Copilot 訂閱。CLI 只當作 agent runtime。

### Provider Configurations

**OpenAI:**
```typescript
provider: { type: "openai", baseUrl: "https://api.openai.com/v1", apiKey: process.env.OPENAI_API_KEY }
```

**Azure AI Foundry (OpenAI-compatible):**
```typescript
provider: {
    type: "openai",
    baseUrl: "https://your-resource.openai.azure.com/openai/v1/",
    apiKey: process.env.FOUNDRY_API_KEY,
    wireApi: "responses",  // Use "responses" for GPT-5 series, "completions" for others
}
```

**Azure OpenAI (native endpoint):**
```typescript
provider: {
    type: "azure",
    baseUrl: "https://my-resource.openai.azure.com",  // Just the host — no /openai/v1
    apiKey: process.env.AZURE_OPENAI_KEY,
    azure: { apiVersion: "2024-10-21" },
}
```

**Anthropic:**
```typescript
provider: { type: "anthropic", baseUrl: "https://api.anthropic.com", apiKey: process.env.ANTHROPIC_API_KEY }
```

**Ollama (local):**
```typescript
provider: { type: "openai", baseUrl: "http://localhost:11434/v1" }
```

### Provider Config Reference

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"openai"` \| `"azure"` \| `"anthropic"` | Provider 類型 |
| `baseUrl` | string | **必填。** API endpoint URL |
| `apiKey` | string | API key（本機 provider 可省略） |
| `bearerToken` | string | Bearer token 驗證（優先於 apiKey） |
| `wireApi` | `"completions"` \| `"responses"` | API 格式（預設：`"completions"`） |
| `azure.apiVersion` | string | Azure API 版本（預設：`"2024-10-21"`） |

### Azure Managed Identity with BYOK

用 `DefaultAzureCredential` 取得 Azure 部署用的短效 bearer token：

```python
from azure.identity import DefaultAzureCredential
from copilot import CopilotClient, ProviderConfig, SessionConfig

credential = DefaultAzureCredential()
token = credential.get_token("https://cognitiveservices.azure.com/.default").token

session = await client.create_session(SessionConfig(
    model="gpt-4.1",
    provider=ProviderConfig(
        type="openai",
        base_url=f"{foundry_url}/openai/v1/",
        bearer_token=token,
        wire_api="responses",
    ),
))
```

> **Note:** Bearer token 會過期（約 1 小時）。長時間執行的應用要在每個新 session 之前重新取得 token。SDK 不會自動更新 token。

### BYOK Limitations

- **只支援靜態憑證**：沒有原生的 Entra ID、OIDC 或 managed identity 支援
- **不會自動更新**：token 過期後得建立新的 session
- **Key 不會被保存**：恢復 session 時要重新提供 `provider` 設定
- **模型可用性**：只能用你的 provider 有提供的模型

---

## Session Persistence

自己提供 session ID，就能在重啟後恢復 session。

```typescript
// Create with explicit ID
const session = await client.createSession({
    sessionId: "user-123-task-456",
    model: "gpt-4.1",
});

// Resume later (even from a different client instance)
const resumed = await client.resumeSession("user-123-task-456");
await resumed.sendAndWait({ prompt: "What did we discuss?" });
```

### Session Management

```typescript
const sessions = await client.listSessions();           // List all
const lastId = await client.getLastSessionId();          // Get most recent
await client.deleteSession("user-123-task-456");         // Delete from storage
await session.destroy();                                 // Destroy active session
```

### Resume Options

恢復 session 時可以重新設定：`model`、`systemMessage`、`availableTools`、`excludedTools`、`provider`（BYOK 必填）、`reasoningEffort`、`streaming`、`mcpServers`、`customAgents`、`skillDirectories`、`infiniteSessions`。

### Session ID Best Practices

| Pattern | Example | Use Case |
|---------|---------|----------|
| `user-{userId}-{taskId}` | `user-alice-pr-review-42` | 多使用者應用 |
| `tenant-{tenantId}-{workflow}` | `tenant-acme-onboarding` | 多租戶 SaaS |
| `{userId}-{taskType}-{timestamp}` | `alice-deploy-1706932800` | 依時間清理 |

### What Gets Persisted

Session 狀態會存到 `~/.copilot/session-state/{sessionId}/`：

| Data | Persisted? | Notes |
|------|------------|-------|
| 對話歷史 | ✅ Yes | 完整的訊息串 |
| 工具呼叫結果 | ✅ Yes | 快取起來當 context |
| Agent 規劃狀態 | ✅ Yes | `plan.md` 檔案 |
| Session 產物 | ✅ Yes | 放在 `files/` 目錄 |
| Provider/API key | ❌ No | 恢復時要重新提供 |
| 記憶體內的工具狀態 | ❌ No | 工具要設計成 stateless |

### Infinite Sessions

長時間執行、可能超過 context 上限的工作流程，可以開啟自動 compaction：

```typescript
const session = await client.createSession({
    infiniteSessions: {
        enabled: true,
        backgroundCompactionThreshold: 0.80,  // Start background compaction at 80%
        bufferExhaustionThreshold: 0.95,       // Block and compact at 95%
    },
});
```

> 門檻值是 context 使用率（0.0–1.0），不是絕對的 token 數量。

---

## Custom Agents

定義專門的 AI 角色：

```typescript
const session = await client.createSession({
    customAgents: [{
        name: "pr-reviewer",
        displayName: "PR Reviewer",
        description: "Reviews pull requests for best practices",
        prompt: "You are an expert code reviewer. Focus on security, performance, and maintainability.",
    }],
});
```

---

## System Message

控制 AI 的行為和個性：

```typescript
const session = await client.createSession({
    systemMessage: { content: "You are a helpful assistant. Always be concise." },
});
```

---

## Skills Integration

載入 skill 目錄來擴充 Copilot 的能力：

```typescript
const session = await client.createSession({
    skillDirectories: ["./skills/code-review", "./skills/documentation"],
    disabledSkills: ["experimental-feature"],
});
```

Skill 可以和自訂 agent、MCP server 搭配使用：

```typescript
const session = await client.createSession({
    skillDirectories: ["./skills/security"],
    customAgents: [{ name: "auditor", prompt: "Focus on OWASP Top 10." }],
    mcpServers: { postgres: { type: "local", command: "npx", args: ["-y", "@modelcontextprotocol/server-postgres"], tools: ["*"] } },
});
```

---

## Permission & Input Handlers

用程式處理工具權限和使用者輸入請求。SDK 採用 **deny-by-default** 的權限模型，除非你提供 handler，否則所有權限請求都會被拒絕。

```typescript
const session = await client.createSession({
    onPermissionRequest: async (request) => {
        if (request.kind === "shell") {
            return { approved: request.command.startsWith("git") };
        }
        return { approved: true };
    },
    onUserInputRequest: async (request) => {
        return { response: "yes" };
    },
});
```

### Token Usage Tracking

訂閱 usage 事件，不要用 CLI 的 `/usage`：

```typescript
session.on("assistant.usage", (event) => {
    console.log("Tokens:", { input: event.data.inputTokens, output: event.data.outputTokens });
});
```

---

## Deployment Patterns

### Local CLI (Default)

SDK 會自動把 CLI 當 subprocess 啟動。最簡單，零設定。

```typescript
const client = new CopilotClient(); // Auto-manages CLI process
```

### External CLI Server (Backend Services)

用 headless 模式跑 CLI，SDK 透過 TCP 連線：

```bash
copilot --headless --port 4321
```

```typescript
const client = new CopilotClient({ cliUrl: "localhost:4321" });
```

**支援多個 client：** 多個 SDK client 可以共用一個 CLI server。

### Bundled CLI (Desktop Apps)

把 CLI binary 跟著你的應用一起發佈：

```typescript
const client = new CopilotClient({ cliPath: path.join(__dirname, "vendor", "copilot") });
```

### Docker Compose

```yaml
services:
  copilot-cli:
    image: ghcr.io/github/copilot-cli:latest
    command: ["--headless", "--port", "4321"]
    environment:
      - COPILOT_GITHUB_TOKEN=${COPILOT_GITHUB_TOKEN}
    volumes:
      - session-data:/root/.copilot/session-state
  api:
    build: .
    environment:
      - CLI_URL=copilot-cli:4321
    depends_on: [copilot-cli]
volumes:
  session-data:
```

### Session Isolation Patterns

| Pattern | Isolation | Resources | Best For |
|---------|-----------|-----------|----------|
| **CLI per user** | 完全隔離 | 高 | 多租戶 SaaS、合規需求 |
| **Shared CLI + session IDs** | 邏輯隔離 | 低 | 內部工具 |
| **Shared sessions** | 無隔離 | 低 | 團隊協作（需要加鎖） |

### Production Checklist

- Session 清理：定期刪除過期的 session
- Health check：ping CLI server，沒回應就重啟
- 持久儲存：容器要掛載 `~/.copilot/session-state/`
- Secret 管理：token 用 Vault/K8s Secrets 管理
- Session 加鎖：共用 session 時用 Redis 之類的機制
- 優雅關閉：停止 CLI 之前先讓進行中的 session 收尾

---

## Client Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `cliPath` | string | 自動偵測 | Copilot CLI 執行檔的路徑 |
| `cliUrl` | string | — | 外部 CLI server 的 URL |
| `githubToken` | string | — | 驗證用的 GitHub token |
| `useLoggedInUser` | boolean | `true` | 使用已儲存的 CLI 憑證 |
| `logLevel` | string | `"none"` | `"none"` \| `"error"` \| `"warning"` \| `"info"` \| `"debug"` |
| `autoRestart` | boolean | `true` | CLI 當掉時自動重啟 |
| `useStdio` | boolean | `true` | 使用 stdio transport |

## Session Configuration

| Option | Type | Description |
|--------|------|-------------|
| `model` | string | 要用的模型（例如 `"gpt-4.1"`、`"claude-sonnet-4"`） |
| `sessionId` | string | 可恢復 session 的自訂 ID |
| `streaming` | boolean | 啟用 streaming 回應 |
| `tools` | Tool[] | 自訂工具 |
| `mcpServers` | object | MCP server 設定 |
| `hooks` | object | Session hook |
| `provider` | object | BYOK provider 設定 |
| `customAgents` | object[] | 自訂 agent 定義 |
| `systemMessage` | object | 覆寫 system message |
| `skillDirectories` | string[] | 載入 skill 的目錄 |
| `disabledSkills` | string[] | 要停用的 skill |
| `reasoningEffort` | string | Reasoning effort 等級 |
| `availableTools` | string[] | 限制可用的工具 |
| `excludedTools` | string[] | 排除特定工具 |
| `infiniteSessions` | object | 自動 compaction 設定 |
| `workingDirectory` | string | 工作目錄 |

---

## SDK vs CLI Feature Comparison

### ✅ Available in SDK

Session 管理、訊息傳送（`send`/`sendAndWait`/`abort`）、訊息歷史（`getMessages`）、自訂工具、工具權限 hook、MCP server（本機 + HTTP）、streaming、模型選擇、BYOK provider、自訂 agent、system message、skill、infinite session、權限 handler、40 種以上的事件類型。

### ❌ CLI-Only Features

Session 匯出（`--share`）、slash command、互動式 UI、終端機渲染、YOLO 模式、登入/登出流程、`/compact`（改用 `infiniteSessions`）、`/usage`（改用 usage 事件）、`/review`、`/delegate`。

**替代做法：**
- Session 匯出 → 用 `session.on()` + `session.getMessages()` 手動收集事件
- 權限控管 → 用 `onPermissionRequest` handler，取代 `--allow-all-paths`
- Context compaction → 用 `infiniteSessions` 設定，取代 `/compact`

---

## Debugging

啟用 debug log：

```typescript
const client = new CopilotClient({ logLevel: "debug" });
```

自訂 log 目錄：

```typescript
const client = new CopilotClient({ cliArgs: ["--log-dir", "/path/to/logs"] });
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `CLI not found` | CLI 沒安裝或不在 PATH 裡 | 安裝 CLI 或設定 `cliPath` |
| `Not authenticated` | 沒有有效的憑證 | 執行 `copilot auth login` 或提供 `githubToken` |
| `Session not found` | `destroy()` 之後還在用 session | 用 `listSessions()` 確認有效的 ID |
| `Connection refused` | CLI process 當掉 | 開啟 `autoRestart: true`，檢查 port 衝突 |
| MCP tools missing | Server 初始化失敗，或工具沒啟用 | 設 `tools: ["*"]`，單獨測試 server |

### Connection State

```typescript
console.log("State:", client.getState());  // "connected" after start()
client.on("stateChange", (state) => console.log("Changed to:", state));
```

---

## Key API Summary

| Language | Client | Session Create | Send | Resume | Stop |
|----------|--------|---------------|------|--------|------|
| Node.js | `new CopilotClient()` | `client.createSession()` | `session.sendAndWait()` | `client.resumeSession()` | `client.stop()` |
| Python | `CopilotClient()` | `client.create_session()` | `session.send_and_wait()` | `client.resume_session()` | `client.stop()` |
| Go | `copilot.NewClient(nil)` | `client.CreateSession()` | `session.SendAndWait()` | `client.ResumeSession()` | `client.Stop()` |
| .NET | `new CopilotClient()` | `client.CreateSessionAsync()` | `session.SendAndWaitAsync()` | `client.ResumeSessionAsync()` | `client.DisposeAsync()` |

## References

- [GitHub Copilot SDK](https://github.com/github/copilot-sdk)
