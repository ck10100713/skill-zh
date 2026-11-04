---
name: claude-agent-sdk-python
description: >
  用 Python 搭配 Claude Agent SDK 建構 AI agent 的專家指引。
  當使用者用 Python 寫 SDK 程式碼、import claude_agent_sdk、使用 query()、
  ClaudeSDKClient、ClaudeAgentOptions、AgentDefinition、建立自訂的 @tool 函式、
  設定 hook、整合 MCP server、管理 session，或是在 Python 裡除錯 SDK 問題時使用。
  也會在這些字串出現時觸發："claude_agent_sdk"、"ClaudeAgentOptions"、"from claude_agent_sdk import"、
  "pip install claude-agent-sdk"、"asyncio.run"，或是 "async for message in query"。
---

# Claude Agent SDK — Python Guide

用 Python 搭配 Claude Agent SDK 建構 AI agent 的 production 級指引。

> **命名**：Claude Code SDK 已改名為 Claude Agent SDK（v0.1.0 起）。
> 套件：`pip install claude-agent-sdk` · Import：`from claude_agent_sdk import ...`

## Message Types

所有訊息類型，供型別檢查和 `isinstance()` 檢查使用：

```python
from claude_agent_sdk import (
    AssistantMessage,     # Claude 的文字／工具回應
    ResultMessage,        # 最終結果，帶有 subtype（success/error/cancelled）
    SystemMessage,        # 系統事件（session_id 等）
    UserMessage,          # 使用者的 prompt
    ToolUseMessage,       # 工具呼叫請求
    ToolResultMessage,    # 工具執行結果
)
```

## Quick Reference — Two Interaction Modes

### 1. `query()` — Stateless, One-Shot

最適合：獨立任務、自動化 script、CI pipeline。

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

async def main():
    async for message in query(
        prompt="Review utils.py for bugs. Fix any issues you find.",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Edit", "Glob"],
            permission_mode="acceptEdits",
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)
                elif hasattr(block, "name"):
                    print(f"Tool: {block.name}")
        elif isinstance(message, ResultMessage):
            print(f"Done: {message.subtype}")

asyncio.run(main())
```

### 2. `ClaudeSDKClient` — Stateful, Multi-Turn

最適合：對話、追問、互動式應用。

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async with ClaudeSDKClient(
    options=ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Bash"],
        permission_mode="acceptEdits",
    )
) as client:
    await client.query("Analyze the codebase structure")
    async for msg in client.receive_messages():
        print(msg)
    # 保留 context 繼續對話
    await client.query("Now refactor the largest file you found")
    async for msg in client.receive_messages():
        print(msg)
```

## ClaudeAgentOptions — Complete Configuration

所有選項都是選填。主要欄位：

| 欄位 | 型別 | 說明 |
|-------|------|-------------|
| `allowed_tools` | `list[str] \| None` | Claude 可以使用的工具。見下方 Built-in Tools。 |
| `disallowed_tools` | `list[str] \| None` | 明確封鎖特定工具。 |
| `permission_mode` | `"default" \| "acceptEdits" \| "bypassPermissions"` | 權限策略。 |
| `system_prompt` | `str \| dict \| None` | 自訂指示。要用 CC 預設的話，用 `{"type": "preset", "preset": "claude_code"}`。 |
| `model` | `str \| None` | 例如 `"sonnet"`、`"opus"`、`"haiku"`，或完整的 model 字串。 |
| `cwd` | `str \| Path \| None` | agent 的工作目錄。 |
| `max_turns` | `int \| None` | agentic 迴圈的最大迭代次數。 |
| `setting_sources` | `list[Literal["user", "project"]] \| None` | 用 `["user", "project"]` 從檔案系統載入 Skills/CLAUDE.md。 |
| `mcp_servers` | `dict \| None` | MCP server 設定。 |
| `agents` | `dict[str, AgentDefinition] \| None` | 具名的 subagent 定義。 |
| `hooks` | `dict \| None` | 生命週期 hook 的 callback。 |

### Built-in Tools

給 `allowed_tools` 用的工具名稱：

- **檔案操作**：`Read`、`Write`、`Edit`、`MultiEdit`
- **搜尋**：`Glob`、`Grep`
- **執行**：`Bash`
- **網路**：`WebSearch`、`WebFetch`
- **委派**：`Task`（subagent 必要）
- **Skills**：`Skill`（需要 `setting_sources`）

## Custom Tools via SDK MCP Server

不需要另外的 MCP server 行程，就能定義行程內（in-process）的工具：

```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions

@tool("search_orders", "Search orders by customer ID", {"customer_id": str, "status": str})
async def search_orders(args):
    results = await db.query_orders(args["customer_id"], args.get("status"))
    return {"content": [{"type": "text", "text": json.dumps(results)}]}

@tool("send_email", "Send an email notification", {"to": str, "subject": str, "body": str})
async def send_email(args):
    await email_service.send(args["to"], args["subject"], args["body"])
    return {"content": [{"type": "text", "text": f"Email sent to {args['to']}"}]}

server = create_sdk_mcp_server(name="business-tools", tools=[search_orders, send_email])

options = ClaudeAgentOptions(
    mcp_servers={"biz": server},
    allowed_tools=["mcp__biz__search_orders", "mcp__biz__send_email"],
)
```

**工具命名慣例**：MCP 工具的存取名稱是 `mcp__<server-name>__<tool-name>`。

## Subagents

把專門的任務委派給隔離的 agent，它們有自己的 context 和工具權限：

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition

async for message in query(
    prompt="Review auth module for security issues, then write tests",
    options=ClaudeAgentOptions(
        allowed_tools=["Read", "Grep", "Glob", "Task"],  # Task 是必要的
        agents={
            "security-reviewer": AgentDefinition(
                description="Security specialist. Use for vulnerability analysis.",
                prompt="You are a security expert. Analyze code for OWASP Top 10...",
                tools=["Read", "Grep", "Glob"],
                model="opus",
            ),
            "test-writer": AgentDefinition(
                description="Test specialist. Use to generate test suites.",
                prompt="You are a testing expert. Write comprehensive unit tests...",
                tools=["Read", "Write", "Bash"],
                model="sonnet",
            ),
        },
    ),
):
    print(message)
```

動態產生 agent 的 **Factory 模式**：

```python
def create_reviewer(language: str) -> AgentDefinition:
    return AgentDefinition(
        description=f"{language} code review specialist",
        prompt=f"You are an expert {language} developer...",
        tools=["Read", "Grep", "Glob"],
        model="opus" if language in ["rust", "c++"] else "sonnet",
    )
```

## Hooks — Lifecycle Callbacks

可用的事件：`PreToolUse`、`PostToolUse`、`Stop`、`SessionStart`、`SessionEnd`、`UserPromptSubmit`。

```python
from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher

async def block_dangerous_commands(input_data, tool_use_id, context):
    """Block destructive bash commands."""
    if input_data.get("tool_name") == "Bash":
        cmd = input_data.get("tool_input", {}).get("command", "")
        if any(danger in cmd for danger in ["rm -rf /", "DROP TABLE", "mkfs"]):
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Blocked dangerous command: {cmd}",
                }
            }
    return {}

async def audit_log(input_data, tool_use_id, context):
    """Log all tool usage for auditing."""
    with open("audit.log", "a") as f:
        f.write(f"{input_data.get('tool_name')}: {input_data.get('tool_input')}\n")
    return {}

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[block_dangerous_commands]),
            HookMatcher(matcher=".*", hooks=[audit_log]),
        ]
    }
)
```

## MCP Integration (External Servers)

```python
options = ClaudeAgentOptions(
    mcp_servers={
        "github": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_TOKEN": os.getenv("GITHUB_TOKEN")},
        },
        "postgres": {
            "type": "stdio",
            "command": "docker",
            "args": ["run", "mcp-postgres-server"],
            "env": {"DATABASE_URL": os.getenv("DATABASE_URL")},
        },
    },
    allowed_tools=["mcp__github", "mcp__postgres"],
)
```

同一份設定裡可以混用 SDK MCP server（行程內）和外部 MCP server。

## Using Skills in the SDK

Skills 是以檔案系統為基礎，必須明確啟用：

```python
options = ClaudeAgentOptions(
    cwd="/path/to/project",
    setting_sources=["user", "project"],  # 必要：從檔案系統載入 Skills
    allowed_tools=["Skill", "Read", "Write", "Bash"],
)
```

**常見錯誤**：忘了 `setting_sources`。沒有它，就算 `allowed_tools` 裡有 `"Skill"`，Skills 也不會被發現。

Skill 的位置：
- **Project**：`.claude/skills/*/SKILL.md`（透過 git 共用）
- **User**：`~/.claude/skills/*/SKILL.md`（個人的，跨專案）

注意：SKILL.md frontmatter 裡的 `allowed-tools` 欄位**只在 Claude Code CLI 有效**，在 SDK 裡無效。要控制工具存取，請用 `ClaudeAgentOptions` 裡的 `allowed_tools`。

## Sessions and Conversation Management

```python
from claude_agent_sdk import query, ClaudeAgentOptions

session_id = None

# 第一次互動：抓取 session_id
async for message in query(
    prompt="Review this codebase and identify the top 3 issues",
    options=ClaudeAgentOptions(allowed_tools=["Read", "Glob", "Grep"]),
):
    if message.type == "system" and hasattr(message, "session_id"):
        session_id = message.session_id
    print(message)

# 帶著 context 接續
async for message in query(
    prompt="Now fix issue #1 that you found",
    options=ClaudeAgentOptions(
        session_id=session_id,
        allowed_tools=["Read", "Edit", "Bash"],
        permission_mode="acceptEdits",
    ),
):
    print(message)
```

## System Prompt Configuration

```python
# 1. 自訂 system prompt（v0.1.0+ 的預設：精簡 prompt）
options = ClaudeAgentOptions(system_prompt="You are a senior Python engineer...")

# 2. Claude Code 完整的 system prompt（需要主動選用）
options = ClaudeAgentOptions(
    system_prompt={"type": "preset", "preset": "claude_code"}
)

# 3. 沒有 system prompt：SDK 預設（精簡）
options = ClaudeAgentOptions()  # 使用內建的精簡 prompt
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

```python
import asyncio

async def process_file(filepath: str):
    async for msg in query(
        prompt=f"Review {filepath} for security issues",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Grep"],
            max_turns=50,
        ),
    ):
        if isinstance(msg, ResultMessage):
            return msg.result

results = await asyncio.gather(
    process_file("auth.py"),
    process_file("payments.py"),
    process_file("users.py"),
)
```

### Structured Output Collection

```python
messages = []
async for msg in query(prompt="Analyze this codebase", options=options):
    messages.append(msg)

# 擷取最終結果
result = next((m for m in reversed(messages) if hasattr(m, "result")), None)
```

### Error Handling

可用的例外類型：
- `CLINotFoundError`：在 PATH 裡找不到 Claude Code CLI 執行檔
- `CLIConnectionError`：無法連接到 CLI 行程
- 也可能拋出標準的 Python 例外（例如 `asyncio.TimeoutError`）

```python
from claude_agent_sdk import CLINotFoundError, CLIConnectionError

try:
    async for msg in query(prompt="...", options=options):
        print(msg)
except CLINotFoundError:
    print("Claude Code CLI not found. Install: curl -fsSL https://claude.ai/install.sh | bash")
except CLIConnectionError as e:
    print(f"Connection error: {e}")
```

## Migration from Claude Code SDK (< v0.1.0)

主要變更：
1. `ClaudeCodeOptions` → `ClaudeAgentOptions`
2. System prompt 預設不再載入 Claude Code 的 prompt
3. `setting_sources` 必須明確設定（以前是自動載入）
4. Import 路徑不變（`claude_agent_sdk`），但類別名稱變了

## Best Practices

1. **最小權限原則**：只給 agent 真正需要的工具。
2. **自動化用 `permission_mode="acceptEdits"`**，互動使用用 `"default"`。
3. **自訂工具優先用 SDK MCP server**，不要用外部的：開銷較小，也比較好除錯。
4. **專門的任務用 subagent**：隔離 context，並依任務套用合適的 model。
5. **加 hook 來確保安全**：在 production 封鎖危險指令並稽核工具使用。
6. **設定 `max_turns`**，防止 agent 在 production 環境失控。
7. **用 `cwd`** 把 agent 限定在特定目錄。
8. **從 system 訊息抓取 `session_id`**，如果你需要對話的連續性。

> 常見問題的排解，見 `references/troubleshooting.md`。

## Official Resources

- Overview: https://platform.claude.com/docs/en/agent-sdk/overview
- Quickstart: https://platform.claude.com/docs/en/agent-sdk/quickstart
- Python reference: https://platform.claude.com/docs/en/agent-sdk/python
- Migration guide: https://platform.claude.com/docs/en/agent-sdk/migration-guide
- Python SDK repo: https://github.com/anthropics/claude-agent-sdk-python
- Demo agents: https://github.com/anthropics/claude-agent-sdk-demos
- Cookbook: https://platform.claude.com/cookbook
