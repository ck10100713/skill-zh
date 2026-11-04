---
name: claude-agent-sdk-typescript
description: >
  用 TypeScript/JavaScript 搭配 Claude Agent SDK 建構 AI agent 的專家指引。
  當使用者用 TypeScript 或 JavaScript 寫 SDK 程式碼、從
  "@anthropic-ai/claude-agent-sdk" import、使用 query()、allowedTools、permissionMode、用
  createSdkMcpServer 建立自訂工具、設定 hook、整合 MCP server、管理
  session，或是在 TypeScript/Node.js 裡除錯 SDK 問題時使用。
  也會在這些字串出現時觸發："@anthropic-ai/claude-agent-sdk"、"allowedTools"、"permissionMode"、
  "npm install"、"for await"、"AgentDefinition"，或是 "settingSources"。
---

# Claude Agent SDK — TypeScript Guide

用 TypeScript 搭配 Claude Agent SDK 建構 AI agent 的 production 級指引。

> **命名**：Claude Code SDK 已改名為 Claude Agent SDK（v0.1.0+）。
> 套件：`npm install @anthropic-ai/claude-agent-sdk` · Import：`import { query } from "@anthropic-ai/claude-agent-sdk"`

## Quick Reference — Two Interaction Modes

### 1. `query()` — Stateless, One-Shot

最適合：獨立任務、自動化 script、CI pipeline。

```typescript
import { query, type ClaudeAgentOptions } from "@anthropic-ai/claude-agent-sdk";

const options: ClaudeAgentOptions = {
  allowedTools: ["Read", "Edit", "Glob"],
  permissionMode: "acceptEdits",
};

for await (const message of query({
  prompt: "Review utils.ts for bugs. Fix any issues you find.",
  options,
})) {
  if (message.type === "assistant") {
    for (const block of message.message.content) {
      if ("text" in block) console.log(block.text);
      else if ("name" in block) console.log(`Tool: ${block.name}`);
    }
  }
  if (message.type === "result") {
    console.log(`Done: ${message.subtype}`);
  }
}
```

### 2. `ClaudeSDKClient` — Stateful, Multi-Turn

最適合：對話、追問、互動式應用。

```typescript
import { ClaudeSDKClient } from "@anthropic-ai/claude-agent-sdk";

const client = new ClaudeSDKClient({
  options: {
    allowedTools: ["Read", "Write", "Bash"],
    permissionMode: "acceptEdits",
  },
});

try {
  await client.query("Analyze the codebase structure");
  for await (const msg of client.receiveMessages()) {
    console.log(msg);
  }
  // 保留 context 繼續對話
  await client.query("Now refactor the largest file you found");
  for await (const msg of client.receiveMessages()) {
    console.log(msg);
  }
} finally {
  await client.close();
}
```

## ClaudeAgentOptions — Complete Configuration

所有選項都是選填。主要欄位（全部是 camelCase）：

| 欄位 | 型別 | 說明 |
|-------|------|-------------|
| `allowedTools` | `string[]` | Claude 可以使用的工具。見下方 Built-in Tools。 |
| `disallowedTools` | `string[]` | 明確封鎖特定工具。 |
| `permissionMode` | `string` | `"default"`、`"acceptEdits"` 或 `"bypassPermissions"`。 |
| `systemPrompt` | `string \| object` | 自訂指示。要用 CC 預設的話，用 `{ type: "preset", preset: "claude_code" }`。 |
| `model` | `string` | 例如 `"sonnet"`、`"opus"`、`"haiku"`，或完整的 model 字串。 |
| `cwd` | `string` | agent 的工作目錄。 |
| `maxTurns` | `number` | agentic 迴圈的最大迭代次數。 |
| `settingSources` | `string[]` | 用 `["user", "project"]` 從檔案系統載入 Skills/CLAUDE.md。 |
| `mcpServers` | `Record<string, McpServerConfig>` | MCP server 設定。 |
| `agents` | `Record<string, AgentDefinition>` | 具名的 subagent 定義。 |
| `hooks` | `object` | 生命週期 hook 的 callback。 |

### Built-in Tools

給 `allowedTools` 用的工具名稱：

- **檔案操作**：`Read`、`Write`、`Edit`、`MultiEdit`
- **搜尋**：`Glob`、`Grep`
- **執行**：`Bash`
- **網路**：`WebSearch`、`WebFetch`
- **委派**：`Task`（subagent 必要）
- **Skills**：`Skill`（需要 `settingSources`）

## Custom Tools via SDK MCP Server

不需要另外的 MCP server 行程，就能定義行程內（in-process）的工具：

```typescript
import { query, tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";

const searchOrders = tool(
  "search_orders",
  "Search orders by customer ID",
  { customer_id: "string", status: "string" },
  async (args) => {
    const results = await db.queryOrders(args.customer_id, args.status);
    return { content: [{ type: "text", text: JSON.stringify(results) }] };
  }
);

const sendEmail = tool(
  "send_email",
  "Send an email notification",
  { to: "string", subject: "string", body: "string" },
  async (args) => {
    await emailService.send(args.to, args.subject, args.body);
    return { content: [{ type: "text", text: `Email sent to ${args.to}` }] };
  }
);

const server = createSdkMcpServer({
  name: "business-tools",
  tools: [searchOrders, sendEmail],
});

for await (const msg of query({
  prompt: "Find recent orders for customer C-123",
  options: {
    mcpServers: { biz: server },
    allowedTools: ["mcp__biz__search_orders", "mcp__biz__send_email"],
  },
})) {
  console.log(msg);
}
```

**工具命名慣例**：MCP 工具的存取名稱是 `mcp__<server-name>__<tool-name>`。

## Subagents

把專門的任務委派給隔離的 agent，它們有自己的 context 和工具權限：

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Review auth module for security issues, then write tests",
  options: {
    allowedTools: ["Read", "Grep", "Glob", "Task"], // Task 是必要的
    agents: {
      "security-reviewer": {
        description: "Security specialist. Use for vulnerability analysis.",
        prompt: "You are a security expert. Analyze code for OWASP Top 10...",
        tools: ["Read", "Grep", "Glob"],
        model: "opus",
      },
      "test-writer": {
        description: "Test specialist. Use to generate test suites.",
        prompt: "You are a testing expert. Write comprehensive unit tests...",
        tools: ["Read", "Write", "Bash"],
        model: "sonnet",
      },
    },
  },
})) {
  if (message.type === "result") console.log(message.result);
}
```

動態產生 agent 的 **Factory 模式**：

```typescript
import type { AgentDefinition } from "@anthropic-ai/claude-agent-sdk";

function createReviewer(language: string): AgentDefinition {
  return {
    description: `${language} code review specialist`,
    prompt: `You are an expert ${language} developer...`,
    tools: ["Read", "Grep", "Glob"],
    model: ["rust", "c++"].includes(language) ? "opus" : "sonnet",
  };
}
```

## Hooks — Lifecycle Callbacks

可用的事件：`PreToolUse`、`PostToolUse`、`Stop`、`SessionStart`、`SessionEnd`、`UserPromptSubmit`。

```typescript
import { query, type HookCallback } from "@anthropic-ai/claude-agent-sdk";
import { appendFileSync } from "node:fs";

const blockDangerousCommands: HookCallback = async (input) => {
  if (input.tool_name === "Bash") {
    const cmd = input.tool_input?.command ?? "";
    const dangers = ["rm -rf /", "DROP TABLE", "mkfs"];
    if (dangers.some((d) => cmd.includes(d))) {
      return {
        hookSpecificOutput: {
          hookEventName: "PreToolUse",
          permissionDecision: "deny",
          permissionDecisionReason: `Blocked dangerous command: ${cmd}`,
        },
      };
    }
  }
  return {};
};

const auditLog: HookCallback = async (input) => {
  appendFileSync(
    "audit.log",
    `${new Date().toISOString()}: ${input.tool_name}: ${JSON.stringify(input.tool_input)}\n`
  );
  return {};
};

for await (const msg of query({
  prompt: "Refactor utils.ts",
  options: {
    permissionMode: "acceptEdits",
    hooks: {
      PreToolUse: [
        { matcher: "Bash", hooks: [blockDangerousCommands] },
        { matcher: ".*", hooks: [auditLog] },
      ],
    },
  },
})) {
  if (message.type === "result") console.log(msg.result);
}
```

## MCP Integration (External Servers)

```typescript
for await (const msg of query({
  prompt: "List open issues in the repo",
  options: {
    mcpServers: {
      github: {
        type: "stdio",
        command: "npx",
        args: ["-y", "@modelcontextprotocol/server-github"],
        env: { GITHUB_TOKEN: process.env.GITHUB_TOKEN! },
      },
      postgres: {
        type: "stdio",
        command: "docker",
        args: ["run", "mcp-postgres-server"],
        env: { DATABASE_URL: process.env.DATABASE_URL! },
      },
    },
    allowedTools: ["mcp__github", "mcp__postgres"],
  },
})) {
  console.log(msg);
}
```

同一份設定裡可以混用 SDK MCP server（行程內）和外部 MCP server。

## Using Skills in the SDK

Skills 是以檔案系統為基礎，必須明確啟用：

```typescript
for await (const msg of query({
  prompt: "Help me process this PDF",
  options: {
    cwd: "/path/to/project",
    settingSources: ["user", "project"], // 必要：從檔案系統載入 Skills
    allowedTools: ["Skill", "Read", "Write", "Bash"],
  },
})) {
  console.log(msg);
}
```

**常見錯誤**：忘了 `settingSources`。沒有它，就算 `allowedTools` 裡有 `"Skill"`，Skills 也不會被發現。

Skill 的位置：
- **Project**：`.claude/skills/*/SKILL.md`（透過 git 共用）
- **User**：`~/.claude/skills/*/SKILL.md`（個人的，跨專案）

注意：SKILL.md frontmatter 裡的 `allowed-tools` 欄位**只在 Claude Code CLI 有效**，在 SDK 裡無效。要控制工具存取，請用 options 裡的 `allowedTools`。

## Sessions and Conversation Management

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

let sessionId: string | undefined;

// 第一次互動：抓取 sessionId
for await (const msg of query({
  prompt: "Review this codebase and identify the top 3 issues",
  options: { allowedTools: ["Read", "Glob", "Grep"] },
})) {
  if (msg.type === "system" && "session_id" in msg) {
    sessionId = msg.session_id;
  }
  console.log(msg);
}

// 帶著 context 接續
for await (const msg of query({
  prompt: "Now fix issue #1 that you found",
  options: {
    sessionId,
    allowedTools: ["Read", "Edit", "Bash"],
    permissionMode: "acceptEdits",
  },
})) {
  console.log(msg);
}
```

## System Prompt Configuration

```typescript
// 1. 自訂 system prompt（v0.1.0+ 的預設：精簡 prompt）
const options = { systemPrompt: "You are a senior TypeScript engineer..." };

// 2. Claude Code 完整的 system prompt（需要主動選用）
const options = {
  systemPrompt: { type: "preset", preset: "claude_code" },
};

// 3. 沒有 system prompt：SDK 預設（精簡）
const options = {}; // 使用內建的精簡 prompt
```

**v0.1.0 的破壞性變更**：SDK 預設不再載入 Claude Code 的 system prompt。如果你需要舊的行為，要明確設定 `preset: "claude_code"`。

## Authentication

```bash
# Direct API (default)
export ANTHROPIC_API_KEY=your-api-key

# Amazon Bedrock
export CLAUDE_CODE_USE_BEDROCK=1
# + configure AWS credentials

# Google Vertex AI
export CLAUDE_CODE_USE_VERTEX=1
# + configure GCP credentials

# Microsoft Azure AI Foundry
export CLAUDE_CODE_USE_FOUNDRY=1
# + configure Azure credentials
```

## Common Patterns

### Batch Processing (Parallel Agents)

```typescript
async function processFile(filepath: string): Promise<string | undefined> {
  for await (const msg of query({
    prompt: `Review ${filepath} for security issues`,
    options: {
      allowedTools: ["Read", "Grep"],
      maxTurns: 50,
    },
  })) {
    if (msg.type === "result") return msg.result;
  }
}

const results = await Promise.all([
  processFile("auth.ts"),
  processFile("payments.ts"),
  processFile("users.ts"),
]);
```

### Structured Output Collection

```typescript
const messages: Message[] = [];
for await (const msg of query({ prompt: "Analyze this codebase", options })) {
  messages.push(msg);
}

// 擷取最終結果
const result = messages.findLast((m) => "result" in m)?.result;
```

### Error Handling

```typescript
import { CLINotFoundError, CLIConnectionError } from "@anthropic-ai/claude-agent-sdk";

try {
  for await (const msg of query({ prompt: "...", options })) {
    console.log(msg);
  }
} catch (error) {
  if (error instanceof CLINotFoundError) {
    console.error("Claude Code CLI not found. Install: curl -fsSL https://claude.ai/install.sh | bash");
  } else if (error instanceof CLIConnectionError) {
    console.error(`Connection error: ${error.message}`);
  } else {
    throw error;
  }
}
```

## Migration from Claude Code SDK (< v0.1.0)

主要變更：
1. `@anthropic-ai/claude-code` → `@anthropic-ai/claude-agent-sdk`
2. `ClaudeCodeOptions` → `ClaudeAgentOptions`（型別名稱）
3. System prompt 預設不再載入 Claude Code 的 prompt
4. `settingSources` 必須明確設定（以前是自動載入）

## Best Practices

1. **最小權限原則**：只給 agent 真正需要的工具。
2. **自動化用 `permissionMode: "acceptEdits"`**，互動使用用 `"default"`。
3. **自訂工具優先用 SDK MCP server**，不要用外部的：開銷較小，也比較好除錯。
4. **專門的任務用 subagent**：隔離 context，並依任務套用合適的 model。
5. **加 hook 來確保安全**：在 production 封鎖危險指令並稽核工具使用。
6. **設定 `maxTurns`**，防止 agent 在 production 環境失控。
7. **用 `cwd`** 把 agent 限定在特定目錄。
8. **從 system 訊息抓取 `sessionId`**，如果你需要對話的連續性。

> 常見問題的排解，見 `references/troubleshooting.md`。

## Official Resources

- Overview: https://platform.claude.com/docs/en/agent-sdk/overview
- Quickstart: https://platform.claude.com/docs/en/agent-sdk/quickstart
- TypeScript reference: https://platform.claude.com/docs/en/agent-sdk/typescript
- Migration guide: https://platform.claude.com/docs/en/agent-sdk/migration-guide
- TypeScript SDK repo: https://github.com/anthropics/claude-agent-sdk-typescript
- Demo agents: https://github.com/anthropics/claude-agent-sdk-demos
- Cookbook: https://platform.claude.com/cookbook
