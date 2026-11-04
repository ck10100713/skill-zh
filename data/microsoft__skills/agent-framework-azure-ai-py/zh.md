---
name: agent-framework-azure-ai-py
description: 用 Microsoft Agent Framework Python SDK（agent-framework-azure-ai）建立 Azure AI Foundry agent。在用 AzureAIAgentsProvider 建立持久化 agent、使用託管工具（code interpreter、file search、web search）、整合 MCP server、管理對話 thread，或實作串流回應時使用。涵蓋 function tool、結構化輸出和多工具 agent。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: agent-framework-azure-ai
---

# Agent Framework Azure 託管 Agent

用 Microsoft Agent Framework Python SDK 在 Azure AI Foundry 上建立持久化 agent。

## 架構

```
User Query → AzureAIAgentsProvider → Azure AI Agent Service (Persistent)
                    ↓
              Agent.run() / Agent.run_stream()
                    ↓
              Tools: Functions | Hosted (Code/Search/Web) | MCP
                    ↓
              AgentThread (conversation persistence)
```

## 安裝

```bash
# 完整框架（建議）
pip install agent-framework --pre

# 或只裝 Azure 專用套件
pip install agent-framework-azure-ai --pre
```

## 環境變數

```bash
export AZURE_AI_PROJECT_ENDPOINT="https://<project>.services.ai.azure.com/api/projects/<project-id>"  # 所有認證方式都必填
export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o-mini"  # 所有認證方式都必填
export BING_CONNECTION_ID="your-bing-connection-id"  # 網頁搜尋用
export AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境用 DefaultAzureCredential 時才需要
```

## 認證與生命週期

> **🔑 下面每一段範例程式都適用兩條規則：**
>
> 1. **優先用 `DefaultAzureCredential`。** 它在本機（Azure CLI / VS Code / Developer CLI）和 Azure 上（managed identity、workload identity）都能跑，程式碼不用改。避免用 connection string、帳號金鑰或 API key，它們會繞過 Entra 的稽核和金鑰輪替。
>    - 本機開發：直接用 `DefaultAzureCredential` 就好。
>    - 正式環境：設定 `AZURE_TOKEN_CREDENTIALS=prod`（或 `AZURE_TOKEN_CREDENTIALS=<specific_credential>`），把 credential chain 限縮在適合正式環境的憑證。
> 2. **每個 client 都要包在 context manager 裡**，這樣 HTTP transport、socket 和 token cache 才會確實被釋放：
>    - 同步：`with <Client>(...) as client:`
>    - 非同步：`async with <Client>(...) as client:` **以及** `async with DefaultAzureCredential() as credential:`（來自 `azure.identity.aio`）
>
> 範例片段可能會省略這些設定，但正式環境的程式碼一定要遵守這兩條規則。

```python
from azure.identity.aio import AzureCliCredential, DefaultAzureCredential, ManagedIdentityCredential

# 開發環境
credential = AzureCliCredential()

# 正式環境
# 本機開發：用 DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在正式環境直接使用指定的 credential：
# See https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()
```

## 核心流程

### 基本 Agent

```python
import asyncio
from agent_framework.azure import AzureAIAgentsProvider
from azure.identity.aio import AzureCliCredential

async def main():
    async with (
        AzureCliCredential() as credential,
        AzureAIAgentsProvider(credential=credential) as provider,
    ):
        agent = await provider.create_agent(
            name="MyAgent",
            instructions="You are a helpful assistant.",
        )
        
        result = await agent.run("Hello!")
        print(result.text)

asyncio.run(main())
```

### 帶 Function Tool 的 Agent

```python
from typing import Annotated
from pydantic import Field
from agent_framework.azure import AzureAIAgentsProvider
from azure.identity.aio import AzureCliCredential

def get_weather(
    location: Annotated[str, Field(description="City name to get weather for")],
) -> str:
    """Get the current weather for a location."""
    return f"Weather in {location}: 72°F, sunny"

def get_current_time() -> str:
    """Get the current UTC time."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

async def main():
    async with (
        AzureCliCredential() as credential,
        AzureAIAgentsProvider(credential=credential) as provider,
    ):
        agent = await provider.create_agent(
            name="WeatherAgent",
            instructions="You help with weather and time queries.",
            tools=[get_weather, get_current_time],  # 直接傳函式
        )
        
        result = await agent.run("What's the weather in Seattle?")
        print(result.text)
```

### 帶託管工具的 Agent

```python
from agent_framework import (
    HostedCodeInterpreterTool,
    HostedFileSearchTool,
    HostedWebSearchTool,
)
from agent_framework.azure import AzureAIAgentsProvider
from azure.identity.aio import AzureCliCredential

async def main():
    async with (
        AzureCliCredential() as credential,
        AzureAIAgentsProvider(credential=credential) as provider,
    ):
        agent = await provider.create_agent(
            name="MultiToolAgent",
            instructions="You can execute code, search files, and search the web.",
            tools=[
                HostedCodeInterpreterTool(),
                HostedWebSearchTool(name="Bing"),
            ],
        )
        
        result = await agent.run("Calculate the factorial of 20 in Python")
        print(result.text)
```

### 串流回應

```python
async def main():
    async with (
        AzureCliCredential() as credential,
        AzureAIAgentsProvider(credential=credential) as provider,
    ):
        agent = await provider.create_agent(
            name="StreamingAgent",
            instructions="You are a helpful assistant.",
        )
        
        print("Agent: ", end="", flush=True)
        async for chunk in agent.run_stream("Tell me a short story"):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print()
```

### 對話 Thread

```python
from agent_framework.azure import AzureAIAgentsProvider
from azure.identity.aio import AzureCliCredential

async def main():
    async with (
        AzureCliCredential() as credential,
        AzureAIAgentsProvider(credential=credential) as provider,
    ):
        agent = await provider.create_agent(
            name="ChatAgent",
            instructions="You are a helpful assistant.",
            tools=[get_weather],
        )
        
        # 建立 thread 來保存對話
        thread = agent.get_new_thread()
        
        # 第一輪
        result1 = await agent.run("What's the weather in Seattle?", thread=thread)
        print(f"Agent: {result1.text}")
        
        # 第二輪，context 會被保留
        result2 = await agent.run("What about Portland?", thread=thread)
        print(f"Agent: {result2.text}")
        
        # 存下 thread ID，之後可以接續
        print(f"Conversation ID: {thread.conversation_id}")
```

### 結構化輸出

```python
from pydantic import BaseModel, ConfigDict
from agent_framework.azure import AzureAIAgentsProvider
from azure.identity.aio import AzureCliCredential

class WeatherResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    location: str
    temperature: float
    unit: str
    conditions: str

async def main():
    async with (
        AzureCliCredential() as credential,
        AzureAIAgentsProvider(credential=credential) as provider,
    ):
        agent = await provider.create_agent(
            name="StructuredAgent",
            instructions="Provide weather information in structured format.",
            response_format=WeatherResponse,
        )
        
        result = await agent.run("Weather in Seattle?")
        weather = WeatherResponse.model_validate_json(result.text)
        print(f"{weather.location}: {weather.temperature}°{weather.unit}")
```

## Provider 方法

| 方法 | 說明 |
|--------|-------------|
| `create_agent()` | 在 Azure AI 服務上建立新 agent |
| `get_agent(agent_id)` | 用 ID 取得現有的 agent |
| `as_agent(sdk_agent)` | 包裝 SDK 的 Agent 物件（不發 HTTP 請求） |

## 託管工具速查

| 工具 | Import | 用途 |
|------|--------|---------|
| `HostedCodeInterpreterTool` | `from agent_framework import HostedCodeInterpreterTool` | 執行 Python 程式碼 |
| `HostedFileSearchTool` | `from agent_framework import HostedFileSearchTool` | 搜尋 vector store |
| `HostedWebSearchTool` | `from agent_framework import HostedWebSearchTool` | Bing 網頁搜尋 |
| `HostedMCPTool` | `from agent_framework import HostedMCPTool` | 由服務端管理的 MCP |
| `MCPStreamableHTTPTool` | `from agent_framework import MCPStreamableHTTPTool` | 由 client 端管理的 MCP |

## 完整範例

```python
import asyncio
from typing import Annotated
from pydantic import BaseModel, Field
from agent_framework import (
    HostedCodeInterpreterTool,
    HostedWebSearchTool,
    MCPStreamableHTTPTool,
)
from agent_framework.azure import AzureAIAgentsProvider
from azure.identity.aio import AzureCliCredential


def get_weather(
    location: Annotated[str, Field(description="City name")],
) -> str:
    """Get weather for a location."""
    return f"Weather in {location}: 72°F, sunny"


class AnalysisResult(BaseModel):
    summary: str
    key_findings: list[str]
    confidence: float


async def main():
    async with (
        AzureCliCredential() as credential,
        MCPStreamableHTTPTool(
            name="Docs MCP",
            url="https://learn.microsoft.com/api/mcp",
        ) as mcp_tool,
        AzureAIAgentsProvider(credential=credential) as provider,
    ):
        agent = await provider.create_agent(
            name="ResearchAssistant",
            instructions="You are a research assistant with multiple capabilities.",
            tools=[
                get_weather,
                HostedCodeInterpreterTool(),
                HostedWebSearchTool(name="Bing"),
                mcp_tool,
            ],
        )
        
        thread = agent.get_new_thread()
        
        # 非串流
        result = await agent.run(
            "Search for Python best practices and summarize",
            thread=thread,
        )
        print(f"Response: {result.text}")
        
        # 串流
        print("\nStreaming: ", end="")
        async for chunk in agent.run_stream("Continue with examples", thread=thread):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print()
        
        # 結構化輸出
        result = await agent.run(
            "Analyze findings",
            thread=thread,
            response_format=AnalysisResult,
        )
        analysis = AnalysisResult.model_validate_json(result.text)
        print(f"\nConfidence: {analysis.confidence}")


if __name__ == "__main__":
    asyncio.run(main())
```

## 慣例

- 一律使用 async context manager：`async with provider:`
- 直接把函式傳給 `tools=` 參數（會自動轉成 AIFunction）
- 函式參數用 `Annotated[type, Field(description=...)]`
- 多輪對話用 `get_new_thread()`
- 服務端管理的 MCP 優先用 `HostedMCPTool`，client 端管理的用 `MCPStreamableHTTPTool`

## 最佳實務

1. **這個 SDK 以非同步為優先，全程使用 `async def` handler 和 `async with`。**
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都包在 `with Client(...) as client:`（同步）或 `async with Client(...) as client:`（非同步）裡。來自 `azure.identity.aio` 的非同步 `DefaultAzureCredential` 也要用 `async with credential:`，token 和 transport 才會被清掉。

## 參考檔案

- [references/tools.md](references/tools.md)：託管工具的詳細用法
- [references/mcp.md](references/mcp.md)：MCP 整合（託管 + 本機）
- [references/threads.md](references/threads.md)：Thread 與對話管理
- [references/advanced.md](references/advanced.md)：OpenAPI、引用、結構化輸出
