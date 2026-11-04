---
name: azure-eventhub-py
description: |
  Python 版 Azure Event Hubs SDK，用於串流。用於高吞吐量事件匯入、producer、consumer 和 checkpoint。
  Triggers: "event hubs", "EventHubProducerClient", "EventHubConsumerClient", "streaming", "partitions".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-eventhub
---

# Python 版 Azure Event Hubs SDK

用於高吞吐量事件匯入的大數據串流平台。

## 安裝

```bash
pip install azure-eventhub azure-identity
# For checkpointing with blob storage
pip install azure-eventhub-checkpointstoreblob-aio
```

## 環境變數

```bash
EVENT_HUB_FULLY_QUALIFIED_NAMESPACE=<namespace>.servicebus.windows.net  # 所有驗證方式都必須設定
EVENT_HUB_NAME=my-eventhub  # 所有驗證方式都必須設定
STORAGE_ACCOUNT_URL=https://<account>.blob.core.windows.net  # checkpoint 儲存必須設定
CHECKPOINT_CONTAINER=checkpoints  # checkpoint 儲存必須設定
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
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.eventhub import EventHubProducerClient, EventHubConsumerClient

# 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或是在正式環境直接用特定的 credential：
# 參考 https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()
namespace = "<namespace>.servicebus.windows.net"
eventhub_name = "my-eventhub"

# Producer
with EventHubProducerClient(
    fully_qualified_namespace=namespace,
    eventhub_name=eventhub_name,
    credential=credential
) as producer:
    # 在這裡使用 producer（操作請看後面的段落）
    ...

# Consumer
with EventHubConsumerClient(
    fully_qualified_namespace=namespace,
    eventhub_name=eventhub_name,
    consumer_group="$Default",
    credential=credential
) as consumer:
    # 在這裡使用 consumer（操作請看後面的段落）
    ...
```

## Client 類型

| Client | 用途 |
|--------|---------|
| `EventHubProducerClient` | 把事件送到 Event Hub |
| `EventHubConsumerClient` | 從 Event Hub 接收事件 |
| `BlobCheckpointStore` | 追蹤 consumer 的進度 |

## 送出事件

```python
from azure.eventhub import EventHubProducerClient, EventData
from azure.identity import DefaultAzureCredential

with EventHubProducerClient(
    fully_qualified_namespace="<namespace>.servicebus.windows.net",
    eventhub_name="my-eventhub",
    credential=DefaultAzureCredential()
) as producer:
    # 建立批次（會處理大小上限）
    event_data_batch = producer.create_batch()
    
    for i in range(10):
        try:
            event_data_batch.add(EventData(f"Event {i}"))
        except ValueError:
            # 批次滿了：先送出，再建新的
            producer.send_batch(event_data_batch)
            event_data_batch = producer.create_batch()
            event_data_batch.add(EventData(f"Event {i}"))
    
    # 送出剩下的
    producer.send_batch(event_data_batch)
```

### 送到特定 Partition

```python
# 用 partition ID
event_data_batch = producer.create_batch(partition_id="0")

# 用 partition key（一致性 hash）
event_data_batch = producer.create_batch(partition_key="user-123")
```

## 接收事件

### 簡單接收

```python
from azure.eventhub import EventHubConsumerClient

def on_event(partition_context, event):
    print(f"Partition: {partition_context.partition_id}")
    print(f"Data: {event.body_as_str()}")
    partition_context.update_checkpoint(event)

with EventHubConsumerClient(
    fully_qualified_namespace="<namespace>.servicebus.windows.net",
    eventhub_name="my-eventhub",
    consumer_group="$Default",
    credential=DefaultAzureCredential()
) as consumer:
    consumer.receive(
        on_event=on_event,
        starting_position="-1",  # 串流的起點
    )
```

### 搭配 Blob Checkpoint Store（正式環境）

```python
from azure.eventhub import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore
from azure.identity import DefaultAzureCredential

checkpoint_store = BlobCheckpointStore(
    blob_account_url="https://<account>.blob.core.windows.net",
    container_name="checkpoints",
    credential=DefaultAzureCredential()
)

with EventHubConsumerClient(
    fully_qualified_namespace="<namespace>.servicebus.windows.net",
    eventhub_name="my-eventhub",
    consumer_group="$Default",
    credential=DefaultAzureCredential(),
    checkpoint_store=checkpoint_store
) as consumer:
    def on_event(partition_context, event):
        print(f"Received: {event.body_as_str()}")
        # 處理完之後做 checkpoint
        partition_context.update_checkpoint(event)

    consumer.receive(on_event=on_event)
```

## 非同步 Client

```python
from azure.eventhub.aio import EventHubProducerClient, EventHubConsumerClient
from azure.identity.aio import DefaultAzureCredential
import asyncio

async def send_events():
    credential = DefaultAzureCredential()
    
    async with EventHubProducerClient(
        fully_qualified_namespace="<namespace>.servicebus.windows.net",
        eventhub_name="my-eventhub",
        credential=credential
    ) as producer:
        batch = await producer.create_batch()
        batch.add(EventData("Async event"))
        await producer.send_batch(batch)

async def receive_events():
    async def on_event(partition_context, event):
        print(event.body_as_str())
        await partition_context.update_checkpoint(event)
    
    async with EventHubConsumerClient(
        fully_qualified_namespace="<namespace>.servicebus.windows.net",
        eventhub_name="my-eventhub",
        consumer_group="$Default",
        credential=DefaultAzureCredential()
    ) as consumer:
        await consumer.receive(on_event=on_event)

asyncio.run(send_events())
```

## 事件屬性

```python
event = EventData("My event body")

# 設定屬性
event.properties = {"custom_property": "value"}
event.content_type = "application/json"

# 讀取屬性（接收時）
print(event.body_as_str())
print(event.sequence_number)
print(event.offset)
print(event.enqueued_time)
print(event.partition_key)
```

## 取得 Event Hub 資訊

```python
with producer:
    info = producer.get_eventhub_properties()
    print(f"Name: {info['name']}")
    print(f"Partitions: {info['partition_ids']}")
    
    for partition_id in info['partition_ids']:
        partition_info = producer.get_partition_properties(partition_id)
        print(f"Partition {partition_id}: {partition_info['last_enqueued_sequence_number']}")
```

## 最佳實務

1. **同步或非同步選一種，並保持一致。** 同一條呼叫路徑裡不要混用 `azure.xxx` 的同步 client 和 `azure.xxx.aio` 的非同步 client。每個 module 選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都用 `with Client(...) as client:`（同步）或 `async with Client(...) as client:`（非同步）包起來，才能正確清理。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，這樣 token 和 transport 才會被清掉。
3. **用 `DefaultAzureCredential`**，在本機開發和 Azure 之間驗證方式可以通用（盡量避免 connection string／API key）。
4. **送多個事件時用批次**
5. **正式環境用 checkpoint store**，處理才可靠
6. **高吞吐量情境用非同步 client**
7. **用 partition key**，同一個 partition 內才能依序遞送
8. **處理批次大小上限**：批次滿了會丟 ValueError，要接住
9. **為不同的應用程式設定適當的 consumer group**

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/checkpointing.md](references/checkpointing.md) | Checkpoint store 模式、blob checkpoint、checkpoint 策略 |
| [references/partitions.md](references/partitions.md) | Partition 管理、負載平衡、起始位置 |
| [scripts/setup_consumer.py](scripts/setup_consumer.py) | 查 Event Hub 資訊、設定 consumer，以及收發事件的 CLI |
