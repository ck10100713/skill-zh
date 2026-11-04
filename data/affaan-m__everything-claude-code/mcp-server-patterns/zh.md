---
name: mcp-server-patterns
description: 用 Node/TypeScript SDK 建 MCP server：tools、resources、prompts、Zod 驗證、stdio 對 Streamable HTTP。要最新 API 就用 Context7 或官方 MCP 文件。建置或除錯 MCP server（tools、resources、prompts、驗證或 transport 選擇）時使用。
metadata:
  origin: ECC
---

# MCP Server Patterns

Model Context Protocol（MCP）讓 AI 助理可以呼叫你 server 上的 tools、讀 resources、使用 prompts。建置或維護 MCP server 時用這個 skill。SDK 的 API 會演進；要查目前的方法名稱和簽章，請看 Context7（對 "MCP" 做 query-docs）或官方 MCP 文件。

至於某個能力該做成 rule、skill、MCP 還是單純的 CLI/API 流程，更完整的判斷請看 [docs/capability-surface-selection.md](../../docs/capability-surface-selection.md)。

## When to Use

使用時機：實作新的 MCP server、新增 tools 或 resources、選 stdio 還是 HTTP、升級 SDK，或除錯 MCP 註冊和 transport 問題。

## How It Works

### Core concepts

- **Tools**：模型可以呼叫的動作（例如搜尋、執行指令）。依 SDK 版本用 `registerTool()` 或 `tool()` 註冊。
- **Resources**：模型可以讀取的唯讀資料（例如檔案內容、API 回應）。用 `registerResource()` 或 `resource()` 註冊。handler 通常會收到 `uri` 參數。
- **Prompts**：client 可以呈現出來（例如在 Claude Desktop）的可重複使用、帶參數的 prompt 範本。用 `registerPrompt()` 或同等的方法註冊。
- **Transport**：本機 client（例如 Claude Desktop）用 stdio；遠端（Cursor、雲端）偏好 Streamable HTTP。舊版 HTTP/SSE 只為了向下相容。

Node/TypeScript SDK 可能提供 `tool()` / `resource()`，也可能是 `registerTool()` / `registerResource()`；官方 SDK 一直在變。一定要對照目前的 [MCP 文件](https://modelcontextprotocol.io)或 Context7 驗證。

### Connecting with stdio

本機 client 的話，建立 stdio transport，再傳給 server 的 connect 方法。確切的 API 依 SDK 版本而異（例如建構子對 factory）。目前的寫法請看官方 MCP 文件，或用 "MCP stdio server" 查 Context7。

讓 server 邏輯（tools + resources）和 transport 互相獨立，這樣在進入點才能接上 stdio 或 HTTP。

### Remote (Streamable HTTP)

Cursor、雲端或其他遠端 client，用 **Streamable HTTP**（依現行規格，每個 MCP 只有單一 HTTP 端點）。只有真的需要向下相容時，才支援舊版 HTTP/SSE。

## Examples

### Install and server setup

```bash
npm install @modelcontextprotocol/sdk zod
```

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({ name: "my-server", version: "1.0.0" });
```

用你的 SDK 版本提供的 API 來註冊 tools 和 resources：有些版本用 `server.tool(name, description, schema, handler)`（位置參數），有些用 `server.tool({ name, description, inputSchema }, handler)` 或 `registerTool()`。resources 也一樣，API 有提供 `uri` 的話，handler 裡要帶。去看官方 MCP 文件或 Context7 上目前 `@modelcontextprotocol/sdk` 的簽章，避免複製貼上出錯。

輸入驗證用 **Zod**（或 SDK 偏好的 schema 格式）。

## Best Practices

- **Schema first**：每個 tool 都先定義輸入 schema；參數和回傳形狀都要寫文件。
- **Errors**：回傳模型看得懂的結構化錯誤或訊息；避免原始的 stack trace。
- **Idempotency**：盡量用 idempotent 的 tool，這樣重試才安全。
- **Rate and cost**：會呼叫外部 API 的 tool，要考慮速率限制和成本，並寫在 tool 的描述裡。
- **Versioning**：在 package.json 裡釘住 SDK 版本；升級時看 release notes。

## Official SDKs and Docs

- **JavaScript/TypeScript**：`@modelcontextprotocol/sdk`（npm）。用函式庫名稱 "MCP" 查 Context7，看目前的註冊和 transport 寫法。
- **Go**：GitHub 上的官方 Go SDK（`modelcontextprotocol/go-sdk`）。
- **C#**：給 .NET 的官方 C# SDK。
