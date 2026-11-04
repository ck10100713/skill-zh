---
name: azure-data-tables-py
description: |
  Python 版 Azure Tables SDK（Storage 和 Cosmos DB）。用於 NoSQL key-value 儲存、entity CRUD 和批次操作。
  Triggers: "table storage", "TableServiceClient", "TableClient", "entities", "PartitionKey", "RowKey".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-data-tables
---

# Python 版 Azure Tables SDK

用來存結構化資料的 NoSQL key-value store（Azure Storage Tables 或 Cosmos DB Table API）。

## 安裝

```bash
pip install azure-data-tables azure-identity
```

## 環境變數

```bash
# Azure Storage Tables
AZURE_STORAGE_ACCOUNT_URL=https://<account>.table.core.windows.net  # Azure Storage Tables 必須設定

# Cosmos DB Table API
COSMOS_TABLE_ENDPOINT=https://<account>.table.cosmos.azure.com  # Cosmos DB Table API 必須設定
AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境使用 DefaultAzureCredential 時才需要
```

## 驗證與生命週期

> **🔑 下面每個範例都適用兩條規則：**
>
> 1. **優先用 `DefaultAzureCredential`。** 它在本機（Azure CLI / VS Code / Developer CLI）和 Azure 上（managed identity、workload identity）都能跑，程式碼不用改。避免用 connection string、帳號金鑰或 API key，因為它們會繞過 Entra 的稽核和輪替。
>    - 本機開發：`DefaultAzureCredential` 直接可用。
>    - 正式環境：設定 `AZURE_TOKEN_CREDENTIALS=prod`（或 `AZURE_TOKEN_CREDENTIALS=<specific_credential>`），把 credential chain 限制在正式環境安全的 credential。
> 2. **每個 client 都用 context manager 包起來**，這樣 HTTP transport、socket 和 token 快取才會確定被釋放：
>    - 同步：`with <Client>(...) as client:`
>    - 非同步：`async with <Client>(...) as client:` **而且** `async with DefaultAzureCredential() as credential:`（來自 `azure.identity.aio`）
>
> 範例片段可能會簡化這段設定，但正式環境的程式碼一定要遵守這兩條規則。

```python
import os
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.data.tables import TableServiceClient, TableClient

# 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或是在正式環境直接用特定的 credential：
# 參考 https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()

endpoint = "https://<account>.table.core.windows.net"

# Service client（管理 table）
with TableServiceClient(endpoint=endpoint, credential=credential) as service_client:
    # 在這裡使用 service_client（操作請看後面的段落）
    ...

# Table client（處理 entity）
with TableClient(endpoint=endpoint, table_name="mytable", credential=credential) as table_client:
    # 在這裡使用 table_client（操作請看後面的段落）
    ...
```

## Client 類型

| Client | 用途 |
|--------|---------|
| `TableServiceClient` | 建立／刪除 table、列出 table |
| `TableClient` | Entity CRUD、查詢 |

## Table 操作

```python
# 建立 table
service_client.create_table("mytable")

# 不存在才建立
service_client.create_table_if_not_exists("mytable")

# 刪除 table
service_client.delete_table("mytable")

# 列出 table
for table in service_client.list_tables():
    print(table.name)

# 取得 table client
table_client = service_client.get_table_client("mytable")
```

## Entity 操作

**重要**：每個 entity 都需要 `PartitionKey` 和 `RowKey`（兩者合起來是唯一 ID）。

### 建立 Entity

```python
entity = {
    "PartitionKey": "sales",
    "RowKey": "order-001",
    "product": "Widget",
    "quantity": 5,
    "price": 9.99,
    "shipped": False
}

# Create（已存在會失敗）
table_client.create_entity(entity=entity)

# Upsert（建立或取代）
table_client.upsert_entity(entity=entity)
```

### 取得 Entity

```python
# 用 key 取得（最快）
entity = table_client.get_entity(
    partition_key="sales",
    row_key="order-001"
)
print(f"Product: {entity['product']}")
```

### 更新 Entity

```python
# 整個 entity 取代
entity["quantity"] = 10
table_client.update_entity(entity=entity, mode="replace")

# Merge（只更新特定欄位）
update = {
    "PartitionKey": "sales",
    "RowKey": "order-001",
    "shipped": True
}
table_client.update_entity(entity=update, mode="merge")
```

### 刪除 Entity

```python
table_client.delete_entity(
    partition_key="sales",
    row_key="order-001"
)
```

## 查詢 Entity

### 在 Partition 內查詢

```python
# 依 partition 查詢（有效率）
entities = table_client.query_entities(
    query_filter="PartitionKey eq 'sales'"
)
for entity in entities:
    print(entity)
```

### 帶篩選條件的查詢

```python
# 依屬性篩選
entities = table_client.query_entities(
    query_filter="PartitionKey eq 'sales' and quantity gt 3"
)

# 帶參數（比較安全）
entities = table_client.query_entities(
    query_filter="PartitionKey eq @pk and price lt @max_price",
    parameters={"pk": "sales", "max_price": 50.0}
)
```

### 選取特定屬性

```python
entities = table_client.query_entities(
    query_filter="PartitionKey eq 'sales'",
    select=["RowKey", "product", "price"]
)
```

### 列出所有 Entity

```python
# 列出全部（跨 partition，少用）
for entity in table_client.list_entities():
    print(entity)
```

## 批次操作

```python
from azure.data.tables import TableTransactionError

# 批次操作（只限同一個 partition！）
operations = [
    ("create", {"PartitionKey": "batch", "RowKey": "1", "data": "first"}),
    ("create", {"PartitionKey": "batch", "RowKey": "2", "data": "second"}),
    ("upsert", {"PartitionKey": "batch", "RowKey": "3", "data": "third"}),
]

try:
    table_client.submit_transaction(operations)
except TableTransactionError as e:
    print(f"Transaction failed: {e}")
```

## 非同步 Client

```python
from azure.data.tables.aio import TableServiceClient, TableClient
from azure.identity.aio import DefaultAzureCredential

async def table_operations():
    async with DefaultAzureCredential() as credential:
        async with TableClient(
            endpoint="https://<account>.table.core.windows.net",
            table_name="mytable",
            credential=credential
        ) as client:
            # 建立
            await client.create_entity(entity={
                "PartitionKey": "async",
                "RowKey": "1",
                "data": "test"
            })
            
            # 查詢
            async for entity in client.query_entities("PartitionKey eq 'async'"):
                print(entity)

import asyncio
asyncio.run(table_operations())
```

## 資料型別

| Python 型別 | Table Storage 型別 |
|-------------|-------------------|
| `str` | String |
| `int` | Int64 |
| `float` | Double |
| `bool` | Boolean |
| `datetime` | DateTime |
| `bytes` | Binary |
| `UUID` | Guid |

## 最佳實務

1. **同步或非同步選一種，並保持一致。** 同一條呼叫路徑裡不要混用 `azure.data.tables` 的同步 client 和 `azure.data.tables.aio` 的非同步 client。每個 module 選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都用 `with TableClient(...) as client:`（同步）或 `async with TableClient(...) as client:`（非同步）包起來。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，這樣 token 和 transport 才會被清掉。
3. **用 `DefaultAzureCredential`**，在本機開發和 Azure 之間驗證方式可以通用（盡量避免 connection string／API key）。
4. **依查詢模式設計 partition key**，並讓資料分布平均
5. **盡量在 partition 內查詢**（跨 partition 很貴）
6. **同一個 partition 的多個 entity 用批次操作**
7. **用 `upsert_entity`** 讓寫入具冪等性
8. **用參數化查詢**防止 injection
9. **entity 保持小**，每個 entity 最大 1MB
10. **高吞吐量情境用非同步 client**

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打的功能、各 operation group 的涵蓋範圍，以及正式環境檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 次要／進階情境的專屬非主打範例。 |
