---
name: azure-cosmos-db-py
description: 用 Python/FastAPI 依照 production 等級的模式建構 Azure Cosmos DB NoSQL 服務。適用於實作雙重驗證（DefaultAzureCredential + emulator）的資料庫 client 設定、含 CRUD 操作的 service layer 類別、partition key 策略、參數化查詢，或 Cosmos 的 TDD 模式。遇到「Cosmos DB」、「NoSQL database」、「document store」、「add persistence」、「database service layer」或「Python Cosmos SDK」等說法時觸發。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-cosmos
---

# Cosmos DB Service Implementation

依照乾淨程式碼、安全 best practice 和 TDD 原則，建構 production 等級的 Azure Cosmos DB NoSQL 服務。

## Installation

```bash
pip install azure-cosmos azure-identity
```

## Environment Variables

```bash
COSMOS_ENDPOINT=https://<account>.documents.azure.com:443/  # 所有驗證方式都需要
COSMOS_DATABASE_NAME=<database-name>  # 所有驗證方式都需要
COSMOS_CONTAINER_ID=<container-id>  # 所有驗證方式都需要
# 只給 emulator 用（不是 production）
COSMOS_KEY=<emulator-key>  # 只有 key 型驗證或 emulator 才需要
AZURE_TOKEN_CREDENTIALS=prod # 只有在 production 使用 DefaultAzureCredential 時才需要
```

## Authentication & Lifecycle

> **🔑 下面每個程式範例都適用兩條規則：**
>
> 1. **優先用 `DefaultAzureCredential`。** 它在本機（Azure CLI / VS Code / Developer CLI）和 Azure 上（managed identity、workload identity）都能跑，程式碼不用改。避免用 connection string、account/API key，因為它們會繞過 Entra 的稽核和金鑰輪替。
>    - 本機開發：`DefaultAzureCredential` 直接可用。
>    - Production：設定 `AZURE_TOKEN_CREDENTIALS=prod`（或 `AZURE_TOKEN_CREDENTIALS=<specific_credential>`），把 credential chain 限縮在 production 安全的 credential。
> 2. **每個 client 都要包在 context manager 裡**，這樣 HTTP transport、socket 和 token cache 會確實被釋放：
>    - 同步：`with <Client>(...) as client:`
>    - 非同步：`async with <Client>(...) as client:` **而且** `async with DefaultAzureCredential() as credential:`（來自 `azure.identity.aio`）
>
> 範例程式碼可能會省略這部分設定，但 production 程式碼一定要兩條規則都遵守。

**DefaultAzureCredential (preferred)**:
```python
import os
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential

# 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在 production 直接用指定的 credential：
# 參考 https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()

with CosmosClient(
    url=os.environ["COSMOS_ENDPOINT"],
    credential=credential
) as client:
    # 在這裡使用 client（各項操作見後面的章節）
    ...
```

**Emulator (local development)**:
```python
from azure.cosmos import CosmosClient

with CosmosClient(
    url="https://localhost:8081",
    credential=os.environ["COSMOS_KEY"],
    connection_verify=False
) as client:
    # 在這裡使用 client（各項操作見後面的章節）
    ...
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Router                          │
│  - Auth dependencies (get_current_user, get_current_user_required)
│  - HTTP error responses (HTTPException)                         │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                        Service Layer                            │
│  - Business logic and validation                                │
│  - Document ↔ Model conversion                                  │
│  - Graceful degradation when Cosmos unavailable                 │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                     Cosmos DB Client Module                     │
│  - Singleton container initialization                           │
│  - Dual auth: DefaultAzureCredential (Azure) / Key (emulator)   │
│  - Async wrapper via run_in_threadpool                          │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Client Module Setup

建立一個支援雙重驗證的 singleton Cosmos client：

```python
# db/cosmos.py
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
from starlette.concurrency import run_in_threadpool

_cosmos_container = None

def _is_emulator_endpoint(endpoint: str) -> bool:
    return "localhost" in endpoint or "127.0.0.1" in endpoint

async def get_container():
    global _cosmos_container
    if _cosmos_container is None:
        # Singleton：client 的壽命等於 FastAPI app 的壽命；在 lifespan shutdown handler 裡關閉。
        if _is_emulator_endpoint(settings.cosmos_endpoint):
            client = CosmosClient(
                url=settings.cosmos_endpoint,
                credential=settings.cosmos_key,
                connection_verify=False
            )
        else:
            client = CosmosClient(
                url=settings.cosmos_endpoint,
                credential=DefaultAzureCredential()
            )
        db = client.get_database_client(settings.cosmos_database_name)
        _cosmos_container = db.get_container_client(settings.cosmos_container_id)
    return _cosmos_container
```

**完整實作**：見 [references/client-setup.md](references/client-setup.md)

### 2. Pydantic Model Hierarchy

用五層 model 模式做乾淨的分層：

```python
class ProjectBase(BaseModel):           # 共用欄位
    name: str = Field(..., min_length=1, max_length=200)

class ProjectCreate(ProjectBase):       # 建立請求
    workspace_id: str = Field(..., alias="workspaceId")

class ProjectUpdate(BaseModel):         # 部分更新（全部選填）
    name: Optional[str] = Field(None, min_length=1)

class Project(ProjectBase):             # API 回應
    id: str
    created_at: datetime = Field(..., alias="createdAt")

class ProjectInDB(Project):             # 內部使用，含 docType
    doc_type: str = "project"
```

### 3. Service Layer Pattern

```python
class ProjectService:
    def _use_cosmos(self) -> bool:
        return get_container() is not None
    
    async def get_by_id(self, project_id: str, workspace_id: str) -> Project | None:
        if not self._use_cosmos():
            return None
        doc = await get_document(project_id, partition_key=workspace_id)
        if doc is None:
            return None
        return self._doc_to_model(doc)
```

**完整模式**：見 [references/service-layer.md](references/service-layer.md)

## Core Principles

### Security Requirements

1. **RBAC 驗證**：在 Azure 上用 `DefaultAzureCredential`，絕對不要把 key 存在程式碼裡
2. **Key 只給 emulator**：只有本機開發才可以寫死那個眾所周知的 emulator key
3. **參數化查詢**：一律用 `@parameter` 語法，絕對不要字串串接
4. **Partition key 驗證**：驗證 partition key 的存取權限和使用者授權一致

### Clean Code Conventions

1. **單一職責**：client module 負責連線，service 負責業務邏輯
2. **優雅降級**：Cosmos 無法使用時，service 回傳 `None`/`[]`
3. **一致的命名**：`_doc_to_model()`、`_model_to_doc()`、`_use_cosmos()`
4. **型別提示**：所有 public method 都要有完整的型別標註
5. **CamelCase 別名**：JSON 序列化用 `Field(alias="camelCase")`

### TDD Requirements

用下面的模式，在實作之前先寫測試：

```python
@pytest.fixture
def mock_cosmos_container(mocker):
    container = mocker.MagicMock()
    mocker.patch("app.db.cosmos.get_container", return_value=container)
    return container

@pytest.mark.asyncio
async def test_get_project_by_id_returns_project(mock_cosmos_container):
    # Arrange
    mock_cosmos_container.read_item.return_value = {"id": "123", "name": "Test"}
    
    # Act
    result = await project_service.get_by_id("123", "workspace-1")
    
    # Assert
    assert result.id == "123"
    assert result.name == "Test"
```

**完整測試指南**：見 [references/testing.md](references/testing.md)

## Best Practices

1. **同步或非同步擇一，並保持一致。** 同一條呼叫路徑裡不要混用 `azure.xxx` 同步 client 和 `azure.xxx.aio` 非同步 client。每個 module 只選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 把 client 包在 `async with CosmosClient(...) as client:` 裡（或透過 FastAPI lifespan 管理它的壽命並明確關閉）。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，這樣 token 和 transport 才會被清掉。

## Reference Files

| File | When to Read |
|------|--------------|
| [references/client-setup.md](references/client-setup.md) | 設定支援雙重驗證的 Cosmos client、SSL 設定、singleton 模式 |
| [references/service-layer.md](references/service-layer.md) | 實作完整的 service 類別，含 CRUD、轉換和優雅降級 |
| [references/testing.md](references/testing.md) | 寫 pytest 測試、mock Cosmos、設定整合測試 |
| [references/partitioning.md](references/partitioning.md) | 選擇 partition key、跨 partition 查詢、搬移操作 |
| [references/error-handling.md](references/error-handling.md) | 處理 CosmosResourceNotFoundError、logging、HTTP 錯誤對應 |

## Template Files

| File | Purpose |
|------|---------|
| [assets/cosmos_client_template.py](assets/cosmos_client_template.py) | 可直接使用的 client module |
| [assets/service_template.py](assets/service_template.py) | Service 類別骨架 |
| [assets/conftest_template.py](assets/conftest_template.py) | 用於 mock Cosmos 的 pytest fixture |

## Quality Attributes (NFRs)

### Reliability
- Cosmos 無法使用時優雅降級
- 暫時性失敗用指數退避的重試邏輯
- 透過 singleton 模式做連線池

### Security
- 程式碼裡沒有任何 secret（透過 DefaultAzureCredential 做 RBAC）
- 參數化查詢防止 injection
- Partition key 隔離確保資料邊界

### Maintainability
- 五層 model 模式讓 schema 能演進
- Service layer 讓業務邏輯和儲存解耦
- 所有 entity service 都用一致的模式

### Testability
- 透過 `get_container()` 做 dependency injection
- 用 module 層級的全域變數就能輕鬆 mock
- 清楚的分層讓你不需要 Cosmos 就能做單元測試

### Performance
- 用 partition key 查詢可避免跨 partition 掃描
- 非同步包裝避免阻塞 FastAPI 的 event loop
- 文件轉換的額外負擔很小
