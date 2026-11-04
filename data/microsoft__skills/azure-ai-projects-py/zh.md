---
name: azure-ai-projects-py
description: 用 Azure AI Projects Python SDK（azure-ai-projects）建立 AI 應用程式。在使用 Foundry project client、用 PromptAgentDefinition 建立版本化 agent、執行 evaluation、管理 connection／deployment／dataset／index，或使用相容 OpenAI 的 client 時使用。這是高階的 Foundry SDK；低階 agent 操作請用 azure-ai-agents-python skill。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-ai-projects
---

# Azure AI Projects Python SDK（Foundry SDK）

用 `azure-ai-projects` SDK 在 Microsoft Foundry 上建立 AI 應用程式。

## 安裝

```bash
pip install azure-ai-projects azure-identity
```

## 環境變數

```bash
AZURE_AI_PROJECT_ENDPOINT="https://<resource>.services.ai.azure.com/api/projects/<project>"  # 所有認證方式都必填
AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4o-mini"  # 所有認證方式都必填
AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境用 DefaultAzureCredential 時才需要
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
import os
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.ai.projects import AIProjectClient

# 本機開發：用 DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential()
# 或在正式環境直接使用指定的 credential：
# See https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()
with AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=credential,
) as client:
    deployments = list(client.deployments.list())
```

## Client 操作總覽

| 操作 | 存取方式 | 用途 |
|-----------|--------|---------|
| `client.agents` | `.agents.*` | Agent 的 CRUD、版本、thread、run |
| `client.connections` | `.connections.*` | 列出／取得 project connection |
| `client.deployments` | `.deployments.*` | 列出模型 deployment |
| `client.datasets` | `.datasets.*` | Dataset 管理 |
| `client.indexes` | `.indexes.*` | Index 管理 |
| `client.evaluations` | `.evaluations.*` | 執行 evaluation |
| `client.red_teams` | `.red_teams.*` | Red team 操作 |

## 兩種 Client 做法

### 1. AIProjectClient（原生 Foundry）

```python
from azure.ai.projects import AIProjectClient

with AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
) as client:
    # 使用 Foundry 原生操作
    agent = client.agents.create_agent(
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are helpful.",
    )
```

### 2. 相容 OpenAI 的 Client

```python
# 從 project 取得相容 OpenAI 的 client
openai_client = client.get_openai_client()

# 使用標準的 OpenAI API
response = openai_client.chat.completions.create(
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    messages=[{"role": "user", "content": "Hello!"}],
)
```

## Agent 操作

### 建立 Agent（基本）

```python
agent = client.agents.create_agent(
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    name="my-agent",
    instructions="You are a helpful assistant.",
)
```

### 建立帶工具的 Agent

```python
from azure.ai.agents.models import CodeInterpreterTool, FileSearchTool

agent = client.agents.create_agent(
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    name="tool-agent",
    instructions="You can execute code and search files.",
    tools=[CodeInterpreterTool(), FileSearchTool()],
)
```

### 用 PromptAgentDefinition 建立版本化 Agent

```python
from azure.ai.projects.models import PromptAgentDefinition

# 建立版本化 agent
agent_version = client.agents.create_version(
    agent_name="customer-support-agent",
    definition=PromptAgentDefinition(
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        instructions="You are a customer support specialist.",
        tools=[],  # 視需要加入工具
    ),
    version_label="v1.0",
)
```

詳細的 agent 用法請看 [references/agents.md](references/agents.md)。

## 工具總覽

| 工具 | Class | 使用情境 |
|------|-------|----------|
| Code Interpreter | `CodeInterpreterTool` | 執行 Python、產生檔案 |
| File Search | `FileSearchTool` | 對上傳的文件做 RAG |
| Bing Grounding | `BingGroundingTool` | 網頁搜尋（需要 connection） |
| Azure AI Search | `AzureAISearchTool` | 搜尋你自己的 index |
| Function Calling | `FunctionTool` | 呼叫你的 Python 函式 |
| OpenAPI | `OpenApiTool` | 呼叫 REST API |
| MCP | `McpTool` | Model Context Protocol server |
| Memory Search | `MemorySearchTool` | 搜尋 agent 的 memory store |
| SharePoint | `SharepointGroundingTool` | 搜尋 SharePoint 內容 |

所有工具的用法請看 [references/tools.md](references/tools.md)。

## Thread 與 Message 流程

```python
# 1. 建立 thread
thread = client.agents.threads.create()

# 2. 加入 message
client.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content="What's the weather like?",
)

# 3. 建立並處理 run
run = client.agents.runs.create_and_process(
    thread_id=thread.id,
    agent_id=agent.id,
)

# 4. 取得回應
if run.status == "completed":
    messages = client.agents.messages.list(thread_id=thread.id)
    for msg in messages:
        if msg.role == "assistant":
            print(msg.content[0].text.value)
```

## Connection

```python
# 列出所有 connection
connections = client.connections.list()
for conn in connections:
    print(f"{conn.name}: {conn.connection_type}")

# 取得指定的 connection
connection = client.connections.get(connection_name="my-search-connection")
```

Connection 的用法請看 [references/connections.md](references/connections.md)。

## Deployment

```python
# 列出可用的模型 deployment
deployments = client.deployments.list()
for deployment in deployments:
    print(f"{deployment.name}: {deployment.model}")
```

Deployment 的用法請看 [references/deployments.md](references/deployments.md)。

## Dataset 與 Index

```python
# 列出 dataset
datasets = client.datasets.list()

# 列出 index
indexes = client.indexes.list()
```

資料操作請看 [references/datasets-indexes.md](references/datasets-indexes.md)。

## Evaluation

```python
# 用 OpenAI client 跑 eval
openai_client = client.get_openai_client()

# 用內建的 evaluator 建立 evaluation
eval_run = openai_client.evals.runs.create(
    eval_id="my-eval",
    name="quality-check",
    data_source={
        "type": "custom",
        "item_references": [{"item_id": "test-1"}],
    },
    testing_criteria=[
        {"type": "fluency"},
        {"type": "task_adherence"},
    ],
)
```

Evaluation 的用法請看 [references/evaluation.md](references/evaluation.md)。

## 非同步 Client

```python
from azure.ai.projects.aio import AIProjectClient

async with AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
) as client:
    agent = await client.agents.create_agent(...)
    # ... 非同步操作
```

非同步的用法請看 [references/async-patterns.md](references/async-patterns.md)。

## Memory Store

```python
# 為 agent 建立 memory store
memory_store = client.agents.create_memory_store(
    name="conversation-memory",
)

# 掛到 agent 上做持久記憶
agent = client.agents.create_agent(
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    name="memory-agent",
    tools=[MemorySearchTool()],
    tool_resources={"memory": {"store_ids": [memory_store.id]}},
)
```

## 最佳實務

1. **同步或非同步擇一，並保持一致。** 同一條呼叫路徑裡，不要混用 `azure.ai.projects` 的同步 client 和 `azure.ai.projects.aio` 的非同步 client。每個模組選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都包在 `with AIProjectClient(...) as client:`（同步）或 `async with AIProjectClient(...) as client:`（非同步）裡。來自 `azure.identity.aio` 的非同步 `DefaultAzureCredential` 也要用 `async with credential:`，token 和 transport 才會被清掉。
3. 用完要**清理 agent**：`client.agents.delete_agent(agent.id)`
4. 簡單的 run **用 `create_and_process`**，要即時體驗就**用串流**
5. 正式環境部署**用版本化 agent**
6. 整合外部服務（AI Search、Bing 等）時**優先用 connection**

## SDK 比較

| 功能 | `azure-ai-projects` | `azure-ai-agents` |
|---------|---------------------|-------------------|
| 層級 | 高階（Foundry） | 低階（Agents） |
| Client | `AIProjectClient` | `AgentsClient` |
| 版本管理 | `create_version()` | 沒有 |
| Connection | 有 | 沒有 |
| Deployment | 有 | 沒有 |
| Dataset／Index | 有 | 沒有 |
| Evaluation | 透過 OpenAI client | 沒有 |
| 何時使用 | 完整的 Foundry 整合 | 獨立的 agent 應用程式 |

## 參考檔案

- [references/agents.md](references/agents.md)：用 PromptAgentDefinition 的 agent 操作
- [references/tools.md](references/tools.md)：所有 agent 工具與範例
- [references/evaluation.md](references/evaluation.md)：Evaluation 操作總覽
- [references/built-in-evaluators.md](references/built-in-evaluators.md)：完整的內建 evaluator 參考
- [references/custom-evaluators.md](references/custom-evaluators.md)：以程式碼和 prompt 為基礎的 evaluator 模式
- [references/connections.md](references/connections.md)：Connection 操作
- [references/deployments.md](references/deployments.md)：Deployment 列舉
- [references/datasets-indexes.md](references/datasets-indexes.md)：Dataset 和 index 操作
- [references/async-patterns.md](references/async-patterns.md)：非同步 client 的用法
- [references/api-reference.md](references/api-reference.md)：全部 373 個 SDK 匯出項目的完整 API 參考（v2.0.0b4）
- [scripts/run_batch_evaluation.py](scripts/run_batch_evaluation.py)：批次 evaluation 用的 CLI 工具
