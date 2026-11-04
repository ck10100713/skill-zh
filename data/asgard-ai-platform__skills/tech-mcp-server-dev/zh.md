---
name: "tech-mcp-server-dev"
description: "開發 MCP（Model Context Protocol）server，包括 tool 定義、schema 設計、認證、錯誤處理和 Claude Code 整合。當使用者需要建立 MCP server、把 API 或資料庫開放給 AI agent、設計 tool schema 或整合 Claude Code 時使用這個 skill，就算他們說的是「做一個 MCP server」、「讓 Claude 連我們的資料庫」、「把我們的 API 開放給 AI」或「幫 Claude Code 做一個 tool」也一樣。"
metadata:
  category: "WP-11 通用技術"
  tags: ["technology", "mcp", "claude-code", "ai-agents"]
---

# MCP Server 開發

## 框架

```
IRON LAW: Tools Must Be Self-Describing
（鐵律：Tool 必須能自我說明）

每個 MCP tool 都必須有清楚的名稱、描述和輸入 schema，
讓 AI 模型不用看任何外部文件，就能理解「何時」以及「如何」使用它。
如果模型光看名稱和描述，還是搞不清楚什麼時候該呼叫你的 tool，
那這個 tool 就是設計得不好。
```

### MCP 架構

```
Claude Code / AI Agent
    ↓ (stdio JSON-RPC 2.0)
MCP Server (your code)
    ↓
Your Data Source (DB, API, file system, etc.)
```

### 協定基礎

| 概念 | 是什麼 |
|---------|-----------|
| **Transport** | stdio（stdin/stdout），本機 server 最常見 |
| **Protocol** | JSON-RPC 2.0 |
| **Tools** | 模型可以呼叫的函式（讀資料、執行動作） |
| **Resources** | 模型可以讀取的資料（檔案、資料庫紀錄） |
| **Prompts** | 模型可以使用的預建 prompt 範本 |

### Tool 設計原則

1. **原子操作**：每個 tool 只做「一件事」。要叫 "search_users"，不要叫 "search_and_update_users"
2. **命名清楚**：用 verb_noun 格式，像 "get_customer"、"create_order"、"search_products"
3. **描述要具體**：除了它做什麼，還要寫「什麼時候」該用
4. **嚴格的 schema**：所有參數都要定義型別、描述，以及必填/選填
5. **有意義的錯誤**：回傳模型看得懂、也能據此行動的錯誤訊息

### Tool Schema 範例

```json
{
  "name": "search_customers",
  "description": "Search for customers by name, email, or phone number. Use when the user asks to find or look up a specific customer.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search term — can be customer name, email, or phone"
      },
      "limit": {
        "type": "number",
        "description": "Maximum results to return (default: 10)",
        "default": 10
      }
    },
    "required": ["query"]
  }
}
```

### 實作步驟（Python/TypeScript）

**階段 1：設定**
1. 選 SDK：`@modelcontextprotocol/sdk`（TypeScript）或 `mcp`（Python）
2. 用 schema 定義 tool
3. 實作 tool handler
4. 用 `mcp dev` 或 `claude mcp add` 在本機測試

**階段 2：資料連線**
5. 連到你的資料來源（DB、API 等）
6. 實作認證（機密放環境變數）
7. 所有資料操作都加上錯誤處理
8. 加 logging 方便除錯

**階段 3：整合**
9. 在 `.mcp.json` 裡設定給 Claude Code 用
10. 用真實查詢測試
11. 加進專案的 CLAUDE.md，讓 Claude 知道有哪些 tool 可用

### .mcp.json 設定

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["path/to/server.js"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

### 錯誤處理

```
Tool handler should:
1. Validate input (check required fields, types)
2. Try the operation
3. On success: return structured data (JSON)
4. On error: return { "error": "Human-readable message", "code": "ERROR_CODE" }
   - NOT stack traces or internal error details
   - The MODEL needs to understand the error to retry or inform the user
```

## 輸出格式

```markdown
# MCP Server Spec: {Server Name}

## Purpose
{What data/capability this server exposes}

## Tools
| Tool | Description | Parameters | Returns |
|------|-----------|-----------|---------|
| {name} | {when to use} | {params} | {return type} |

## Data Source
- Type: {database / API / file system}
- Connection: {how to connect}
- Auth: {env vars needed}

## .mcp.json
```json
{config}
```

## Testing Plan
1. {test case for each tool}
```

## 常見陷阱

- **機密用環境變數**：絕對不要把 API key 或資料庫密碼寫死。用 .mcp.json 裡的 `env` 把環境變數裡的機密傳進去。
- **Tool 描述的品質**：模型「完全」只看名稱 + 描述來決定要不要用你的 tool。描述寫不好，tool 就永遠不會被呼叫（或是被拿去做錯誤的事）。
- **回傳資料量**：不要回傳 10,000 筆。模型的 context window 有限，要回傳摘要或分頁後的結果。預設上限 = 10-20 筆。
- **讀取要冪等，寫入要確認**：讀取操作要能安全地重複呼叫。寫入操作（建立、更新、刪除）在執行前要先跟使用者確認。
- **用真實的模型互動來測試**：單元測試不夠。真正的考驗是 Claude 在對話裡有沒有正確使用你的 tool。要用各種不同的 prompt 測。

## 參考資料

- MCP SDK 文件，見 `references/mcp-sdk.md`
- 進階 MCP 模式（resources、prompts），見 `references/mcp-advanced.md`
