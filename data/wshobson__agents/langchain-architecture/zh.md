---
name: langchain-architecture
description: 用 LangChain 1.x 和 LangGraph 設計 LLM 應用，涵蓋 agent、memory 與工具整合。在建立 LangChain 應用、實作 AI agent 或打造複雜 LLM 工作流程時使用。
---

# LangChain & LangGraph Architecture

精通現代的 LangChain 1.x 與 LangGraph，用來打造具備 agent、狀態管理、memory 與工具整合的複雜 LLM 應用。

## When to Use This Skill

- 建立能使用工具的自主 AI agent
- 實作複雜的多步驟 LLM 工作流程
- 管理對話 memory 與狀態
- 把 LLM 整合到外部資料來源與 API
- 打造模組化、可重用的 LLM 應用元件
- 實作文件處理 pipeline
- 建立正式環境等級的 LLM 應用

## Package Structure (LangChain 1.x)

```
langchain (1.2.x)         # High-level orchestration
langchain-core (1.2.x)    # Core abstractions (messages, prompts, tools)
langchain-community       # Third-party integrations
langgraph                 # Agent orchestration and state management
langchain-openai          # OpenAI integrations
langchain-anthropic       # Anthropic/Claude integrations
langchain-voyageai        # Voyage AI embeddings
langchain-pinecone        # Pinecone vector store
```

## Core Concepts

### 1. LangGraph Agents

LangGraph 是 2026 年建立 agent 的標準做法，提供：

**主要功能：**

- **StateGraph**：用有型別的 state 做明確的狀態管理
- **Durable Execution**：agent 遇到失敗也能延續執行
- **Human-in-the-Loop**：可以在任何時間點檢查並修改 state
- **Memory**：跨 session 的短期與長期記憶
- **Checkpointing**：儲存並恢復 agent 的 state

**Agent 模式：**

- **ReAct**：用 `create_react_agent` 做推理加行動
- **Plan-and-Execute**：把規劃和執行拆成不同節點
- **Multi-Agent**：由 supervisor 在各個專門 agent 之間分派
- **Tool-Calling**：用 Pydantic schema 做結構化的工具呼叫

### 2. State Management

LangGraph 用 TypedDict 表示明確的 state：

```python
from typing import Annotated, TypedDict
from langgraph.graph import MessagesState

# Simple message-based state
class AgentState(MessagesState):
    """Extends MessagesState with custom fields."""
    context: Annotated[list, "retrieved documents"]

# Custom state for complex agents
class CustomState(TypedDict):
    messages: Annotated[list, "conversation history"]
    context: Annotated[dict, "retrieved context"]
    current_step: str
    results: list
```

### 3. Memory Systems

現代的 memory 實作：

- **ConversationBufferMemory**：儲存所有訊息（適合短對話）
- **ConversationSummaryMemory**：把較舊的訊息做摘要（適合長對話）
- **ConversationTokenBufferMemory**：依 token 數量做視窗
- **VectorStoreRetrieverMemory**：用語意相似度檢索
- **LangGraph Checkpointers**：跨 session 的持久化 state

### 4. Document Processing

載入、轉換並儲存文件：

**元件：**

- **Document Loaders**：從各種來源載入
- **Text Splitters**：聰明地切分文件
- **Vector Stores**：儲存並檢索 embedding
- **Retrievers**：取得相關文件

### 5. Callbacks & Tracing

LangSmith 是可觀測性的標準：

- 請求/回應記錄
- Token 用量追蹤
- 延遲監控
- 錯誤追蹤
- Trace 視覺化

## Quick Start

### Modern ReAct Agent with LangGraph

```python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
import ast
import operator

# Initialize LLM (Claude Sonnet 5 recommended)
llm = ChatAnthropic(model="claude-sonnet-5")

# Define tools with Pydantic schemas
@tool
def search_database(query: str) -> str:
    """Search internal database for information."""
    # Your database search logic
    return f"Results for: {query}"

@tool
def calculate(expression: str) -> str:
    """Safely evaluate a mathematical expression.

    Supports: +, -, *, /, **, %, parentheses
    Example: '(2 + 3) * 4' returns '20'
    """
    # Safe math evaluation using ast
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
    }

    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            return allowed_operators[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            return allowed_operators[type(node.op)](operand)
        else:
            raise ValueError(f"Unsupported operation: {type(node)}")

    try:
        tree = ast.parse(expression, mode='eval')
        return str(_eval(tree.body))
    except Exception as e:
        return f"Error: {e}"

tools = [search_database, calculate]

# Create checkpointer for memory persistence
checkpointer = MemorySaver()

# Create ReAct agent
agent = create_react_agent(
    llm,
    tools,
    checkpointer=checkpointer
)

# Run agent with thread ID for memory
config = {"configurable": {"thread_id": "user-123"}}
result = await agent.ainvoke(
    {"messages": [("user", "Search for Python tutorials and calculate 25 * 4")]},
    config=config
)
```

## Detailed patterns and worked examples

詳細的模式文件放在 `references/details.md`。上面的導覽層不夠用時，再去讀那個檔案。

## Testing Strategies

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_agent_tool_selection():
    """Test agent selects correct tool."""
    with patch.object(llm, 'ainvoke') as mock_llm:
        mock_llm.return_value = AsyncMock(content="Using search_database")

        result = await agent.ainvoke({
            "messages": [("user", "search for documents")]
        })

        # Verify tool was called
        assert "search_database" in str(result)

@pytest.mark.asyncio
async def test_memory_persistence():
    """Test memory persists across invocations."""
    config = {"configurable": {"thread_id": "test-thread"}}

    # First message
    await agent.ainvoke(
        {"messages": [("user", "Remember: the code is 12345")]},
        config
    )

    # Second message should remember
    result = await agent.ainvoke(
        {"messages": [("user", "What was the code?")]},
        config
    )

    assert "12345" in result["messages"][-1].content
```

## Performance Optimization

### 1. Caching with Redis

```python
from langchain_community.cache import RedisCache
from langchain_core.globals import set_llm_cache
import redis

redis_client = redis.Redis.from_url("redis://localhost:6379")
set_llm_cache(RedisCache(redis_client))
```

### 2. Async Batch Processing

```python
import asyncio
from langchain_core.documents import Document

async def process_documents(documents: list[Document]) -> list:
    """Process documents in parallel."""
    tasks = [process_single(doc) for doc in documents]
    return await asyncio.gather(*tasks)

async def process_single(doc: Document) -> dict:
    """Process a single document."""
    chunks = text_splitter.split_documents([doc])
    embeddings = await embeddings_model.aembed_documents(
        [c.page_content for c in chunks]
    )
    return {"doc_id": doc.metadata.get("id"), "embeddings": embeddings}
```

### 3. Connection Pooling

```python
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

# Reuse Pinecone client
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index("my-index")

# Create vector store with existing index
vectorstore = PineconeVectorStore(index=index, embedding=embeddings)
```
