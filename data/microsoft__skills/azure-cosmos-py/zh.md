---
name: azure-cosmos-py
description: |
  Azure Cosmos DB SDK for Python（NoSQL API）。用於文件 CRUD、查詢、container 和全球分散的資料。
  Triggers: "cosmos db", "CosmosClient", "container", "document", "NoSQL", "partition key".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-cosmos
---

# Azure Cosmos DB SDK for Python

Azure Cosmos DB NoSQL API 的 client library，這是全球分散的多模型資料庫。

## Installation

```bash
pip install azure-cosmos azure-identity
```

## Environment Variables

```bash
COSMOS_ENDPOINT=https://<account>.documents.azure.com:443/  # 所有驗證方式都需要
COSMOS_DATABASE=mydb  # 所有驗證方式都需要
COSMOS_CONTAINER=mycontainer  # 所有驗證方式都需要
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

```python
import os
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.cosmos import CosmosClient

# 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在 production 直接用指定的 credential：
# 參考 https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()

endpoint = "https://<account>.documents.azure.com:443/"

with CosmosClient(url=endpoint, credential=credential) as client:
    # 在這裡使用 client（各項操作見後面的章節）
    ...
```

## Client Hierarchy

| Client | Purpose | Get From |
|--------|---------|----------|
| `CosmosClient` | 帳號層級的操作 | 直接建立實例 |
| `DatabaseProxy` | 資料庫操作 | `client.get_database_client()` |
| `ContainerProxy` | Container/item 操作 | `database.get_container_client()` |

## Core Workflow

### Setup Database and Container

```python
# 取得或建立資料庫
database = client.create_database_if_not_exists(id="mydb")

# 取得或建立帶有 partition key 的 container
container = database.create_container_if_not_exists(
    id="mycontainer",
    partition_key=PartitionKey(path="/category")
)

# 取得既有的
database = client.get_database_client("mydb")
container = database.get_container_client("mycontainer")
```

### Create Item

```python
item = {
    "id": "item-001",           # 必填：在 partition 內要唯一
    "category": "electronics",   # Partition key 的值
    "name": "Laptop",
    "price": 999.99,
    "tags": ["computer", "portable"]
}

created = container.create_item(body=item)
print(f"Created: {created['id']}")
```

### Read Item

```python
# 讀取需要 id 和 partition key
item = container.read_item(
    item="item-001",
    partition_key="electronics"
)
print(f"Name: {item['name']}")
```

### Update Item (Replace)

```python
item = container.read_item(item="item-001", partition_key="electronics")
item["price"] = 899.99
item["on_sale"] = True

updated = container.replace_item(item=item["id"], body=item)
```

### Upsert Item

```python
# 不存在就建立，存在就取代
item = {
    "id": "item-002",
    "category": "electronics",
    "name": "Tablet",
    "price": 499.99
}

result = container.upsert_item(body=item)
```

### Delete Item

```python
container.delete_item(
    item="item-001",
    partition_key="electronics"
)
```

## Queries

### Basic Query

```python
# 在單一 partition 內查詢（有效率）
query = "SELECT * FROM c WHERE c.price < @max_price"
items = container.query_items(
    query=query,
    parameters=[{"name": "@max_price", "value": 500}],
    partition_key="electronics"
)

for item in items:
    print(f"{item['name']}: ${item['price']}")
```

### Cross-Partition Query

```python
# 跨 partition（比較貴，少用）
query = "SELECT * FROM c WHERE c.price < @max_price"
items = container.query_items(
    query=query,
    parameters=[{"name": "@max_price", "value": 500}],
    enable_cross_partition_query=True
)

for item in items:
    print(item)
```

### Query with Projection

```python
query = "SELECT c.id, c.name, c.price FROM c WHERE c.category = @category"
items = container.query_items(
    query=query,
    parameters=[{"name": "@category", "value": "electronics"}],
    partition_key="electronics"
)
```

### Read All Items

```python
# 讀取 partition 內的全部
items = container.read_all_items()  # 跨 partition
# 或指定 partition key
items = container.query_items(
    query="SELECT * FROM c",
    partition_key="electronics"
)
```

## Partition Keys

**重要**：要有效率地操作，一定要帶 partition key。

```python
from azure.cosmos import PartitionKey

# 單一 partition key
container = database.create_container_if_not_exists(
    id="orders",
    partition_key=PartitionKey(path="/customer_id")
)

# 階層式 partition key（preview）
container = database.create_container_if_not_exists(
    id="events",
    partition_key=PartitionKey(path=["/tenant_id", "/user_id"])
)
```

## Throughput

```python
# 建立帶有預佈建吞吐量的 container
container = database.create_container_if_not_exists(
    id="mycontainer",
    partition_key=PartitionKey(path="/pk"),
    offer_throughput=400  # RU/s
)

# 讀取目前的吞吐量
offer = container.read_offer()
print(f"Throughput: {offer.offer_throughput} RU/s")

# 更新吞吐量
container.replace_throughput(throughput=1000)
```

## Async Client

```python
from azure.cosmos.aio import CosmosClient
from azure.identity.aio import DefaultAzureCredential

async def cosmos_operations():
    async with DefaultAzureCredential() as credential:
        async with CosmosClient(endpoint, credential=credential) as client:
            database = client.get_database_client("mydb")
            container = database.get_container_client("mycontainer")
            
            # Create
            await container.create_item(body={"id": "1", "pk": "test"})
            
            # Read
            item = await container.read_item(item="1", partition_key="test")
            
            # Query
            async for item in container.query_items(
                query="SELECT * FROM c",
                partition_key="test"
            ):
                print(item)

import asyncio
asyncio.run(cosmos_operations())
```

## Error Handling

```python
from azure.cosmos.exceptions import CosmosHttpResponseError

try:
    item = container.read_item(item="nonexistent", partition_key="pk")
except CosmosHttpResponseError as e:
    if e.status_code == 404:
        print("Item not found")
    elif e.status_code == 429:
        print(f"Rate limited. Retry after: {e.headers.get('x-ms-retry-after-ms')}ms")
    else:
        raise
```

## Best Practices

1. **同步或非同步擇一，並保持一致。** 同一條呼叫路徑裡不要混用 `azure.cosmos` 同步 client 和 `azure.cosmos.aio` 非同步 client。每個 module 只選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都包在 `with CosmosClient(...) as client:`（同步）或 `async with CosmosClient(...) as client:`（非同步）裡。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，這樣 token 和 transport 才會被清掉。
3. **用 `DefaultAzureCredential`**：本機開發和 Azure 都能用的可攜式驗證（盡量避免 connection string / API key）。
4. **一定要指定 partition key**：point read 和查詢都要
5. **用參數化查詢**，防止 injection 並提高快取命中率
6. **盡可能避免跨 partition 查詢**
7. **冪等寫入用 `upsert_item`**
8. **高吞吐量情境用非同步 client**
9. **設計 partition key** 讓資料均勻分佈
10. **取得單一文件用 `read_item`**，不要用查詢

## Reference Files

| File | Contents |
|------|----------|
| [references/partitioning.md](references/partitioning.md) | Partition key 策略、階層式 key、熱點 partition 的偵測與緩解 |
| [references/query-patterns.md](references/query-patterns.md) | 查詢最佳化、聚合、分頁、交易、change feed |
| [scripts/setup_cosmos_container.py](scripts/setup_cosmos_container.py) | 用來建立 container 的 CLI 工具，涵蓋 partition、吞吐量和索引 |
