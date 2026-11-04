---
name: azure-servicebus-py
description: |
  Python 版的 Azure Service Bus 訊息 SDK。用於 queue、topic、subscription 和企業級訊息模式。
  Triggers: "service bus", "ServiceBusClient", "queue", "topic", "subscription", "message broker".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-servicebus
---

# Python 版 Azure Service Bus SDK

企業級訊息服務，用 queue 和 pub/sub topic 做可靠的雲端通訊。

## 安裝

```bash
pip install azure-servicebus azure-identity
```

## 環境變數

```bash
SERVICEBUS_FULLY_QUALIFIED_NAMESPACE=<namespace>.servicebus.windows.net  # 所有驗證方式都必填
SERVICEBUS_QUEUE_NAME=myqueue  # queue 操作必填
SERVICEBUS_TOPIC_NAME=mytopic  # topic 操作必填
SERVICEBUS_SUBSCRIPTION_NAME=mysubscription  # subscription 操作必填
AZURE_TOKEN_CREDENTIALS=prod # 只有在 production 使用 DefaultAzureCredential 時才需要
```

## 驗證與生命週期

> **🔑 下面每個程式碼範例都適用兩條規則：**
>
> 1. **優先用 `DefaultAzureCredential`。** 它在本機（Azure CLI / VS Code / Developer CLI）和 Azure 上（managed identity、workload identity）都能用，不用改程式碼。避免用 connection string、account key 或 API key，它們會繞過 Entra 的稽核和輪替。
>    - 本機開發：直接用 `DefaultAzureCredential` 就好。
>    - Production：設定 `AZURE_TOKEN_CREDENTIALS=prod`（或 `AZURE_TOKEN_CREDENTIALS=<specific_credential>`），把 credential chain 限縮在 production 安全的 credential。
> 2. **每個 client 都用 context manager 包起來**，這樣 HTTP transport、socket 和 token cache 才會確實釋放：
>    - 同步：`with <Client>(...) as client:`
>    - 非同步：`async with <Client>(...) as client:` **而且** `async with DefaultAzureCredential() as credential:`（來自 `azure.identity.aio`）
>
> 範例片段可能會簡化這段設定，但 production 的程式碼一定要兩條規則都遵守。

```python
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.servicebus import ServiceBusClient

# 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在 production 直接用特定的 credential：
# See https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()
namespace = "<namespace>.servicebus.windows.net"

with ServiceBusClient(
    fully_qualified_namespace=namespace,
    credential=credential
) as client:
    # 在這裡使用 client（各種操作請看後面的章節）
    ...
```

## Client 類型

| Client | 用途 | 取得方式 |
|--------|---------|----------|
| `ServiceBusClient` | 連線管理 | 直接建立實例 |
| `ServiceBusSender` | 傳送訊息 | `client.get_queue_sender()` / `get_topic_sender()` |
| `ServiceBusReceiver` | 接收訊息 | `client.get_queue_receiver()` / `get_subscription_receiver()` |

## 傳送訊息（非同步）

```python
import asyncio
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage
from azure.identity.aio import DefaultAzureCredential

async def send_messages():
    credential = DefaultAzureCredential()
    
    async with ServiceBusClient(
        fully_qualified_namespace="<namespace>.servicebus.windows.net",
        credential=credential
    ) as client:
        sender = client.get_queue_sender(queue_name="myqueue")
        
        async with sender:
            # 單一訊息
            message = ServiceBusMessage("Hello, Service Bus!")
            await sender.send_messages(message)
            
            # 一批訊息
            messages = [ServiceBusMessage(f"Message {i}") for i in range(10)]
            await sender.send_messages(messages)
            
            # Message batch（用來控制大小）
            batch = await sender.create_message_batch()
            for i in range(100):
                try:
                    batch.add_message(ServiceBusMessage(f"Batch message {i}"))
                except ValueError:  # Batch 滿了
                    await sender.send_messages(batch)
                    batch = await sender.create_message_batch()
                    batch.add_message(ServiceBusMessage(f"Batch message {i}"))
            await sender.send_messages(batch)

asyncio.run(send_messages())
```

## 接收訊息（非同步）

```python
async def receive_messages():
    credential = DefaultAzureCredential()
    
    async with ServiceBusClient(
        fully_qualified_namespace="<namespace>.servicebus.windows.net",
        credential=credential
    ) as client:
        receiver = client.get_queue_receiver(queue_name="myqueue")
        
        async with receiver:
            # 批次接收
            messages = await receiver.receive_messages(
                max_message_count=10,
                max_wait_time=5  # 秒
            )
            
            for msg in messages:
                print(f"Received: {str(msg)}")
                await receiver.complete_message(msg)  # 從 queue 移除

asyncio.run(receive_messages())
```

## 接收模式

| 模式 | 行為 | 使用情境 |
|------|----------|----------|
| `PEEK_LOCK`（預設） | 訊息會被鎖住，必須 complete 或 abandon | 可靠處理 |
| `RECEIVE_AND_DELETE` | 一接收就立刻移除 | 最多一次（at-most-once）傳遞 |

```python
from azure.servicebus import ServiceBusReceiveMode

receiver = client.get_queue_receiver(
    queue_name="myqueue",
    receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE
)
```

## 訊息結算（Settlement）

```python
async with receiver:
    messages = await receiver.receive_messages(max_message_count=1)
    
    for msg in messages:
        try:
            # 處理訊息...
            await receiver.complete_message(msg)  # 成功 - 從 queue 移除
        except ProcessingError:
            await receiver.abandon_message(msg)  # 稍後重試
        except PermanentError:
            await receiver.dead_letter_message(
                msg,
                reason="ProcessingFailed",
                error_description="Could not process"
            )
```

| 動作 | 效果 |
|--------|--------|
| `complete_message()` | 從 queue 移除（成功） |
| `abandon_message()` | 釋放 lock，立刻重試 |
| `dead_letter_message()` | 移到 dead-letter queue |
| `defer_message()` | 先擱置，之後用 sequence number 接收 |

## Topic 與 Subscription

```python
# 傳送到 topic
sender = client.get_topic_sender(topic_name="mytopic")
async with sender:
    await sender.send_messages(ServiceBusMessage("Topic message"))

# 從 subscription 接收
receiver = client.get_subscription_receiver(
    topic_name="mytopic",
    subscription_name="mysubscription"
)
async with receiver:
    messages = await receiver.receive_messages(max_message_count=10)
```

## Session（FIFO）

```python
# 帶 session 傳送
message = ServiceBusMessage("Session message")
message.session_id = "order-123"
await sender.send_messages(message)

# 從特定 session 接收
receiver = client.get_queue_receiver(
    queue_name="session-queue",
    session_id="order-123"
)

# 從下一個可用的 session 接收
from azure.servicebus import NEXT_AVAILABLE_SESSION
receiver = client.get_queue_receiver(
    queue_name="session-queue",
    session_id=NEXT_AVAILABLE_SESSION
)
```

## 排程訊息

```python
from datetime import datetime, timedelta, timezone

message = ServiceBusMessage("Scheduled message")
scheduled_time = datetime.now(timezone.utc) + timedelta(minutes=10)

# 排程訊息
sequence_number = await sender.schedule_messages(message, scheduled_time)

# 取消排程的訊息
await sender.cancel_scheduled_messages(sequence_number)
```

## Dead-Letter Queue

```python
from azure.servicebus import ServiceBusSubQueue

# 從 dead-letter queue 接收
dlq_receiver = client.get_queue_receiver(
    queue_name="myqueue",
    sub_queue=ServiceBusSubQueue.DEAD_LETTER
)

async with dlq_receiver:
    messages = await dlq_receiver.receive_messages(max_message_count=10)
    for msg in messages:
        print(f"Dead-lettered: {msg.dead_letter_reason}")
        await dlq_receiver.complete_message(msg)
```

## 同步 Client（適合簡單的 script）

```python
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.identity import DefaultAzureCredential

with ServiceBusClient(
    fully_qualified_namespace="<namespace>.servicebus.windows.net",
    credential=DefaultAzureCredential()
) as client:
    with client.get_queue_sender("myqueue") as sender:
        sender.send_messages(ServiceBusMessage("Sync message"))
    
    with client.get_queue_receiver("myqueue") as receiver:
        for msg in receiver:
            print(str(msg))
            receiver.complete_message(msg)
```

## 最佳實務

1. **同步或非同步選一個，然後保持一致。** 同一條呼叫路徑裡，不要混用 `azure.xxx` 同步 client 和 `azure.xxx.aio` 非同步 client。每個 module 只選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都用 `with Client(...) as client:`（同步）或 `async with Client(...) as client:`（非同步）包起來，才能正確清理。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，token 和 transport 才會清乾淨。
3. **用 `DefaultAzureCredential`**，在本機開發和 Azure 之間都能用同一套驗證（盡量避免 connection string／API key）。
4. production 的工作負載**用非同步 client**
5. 處理成功後要 **complete 訊息**
6. poison message 要**用 dead-letter queue**
7. 要依序、FIFO 處理就**用 session**
8. 高吞吐量的情境**用 message batch**
9. **設定 `max_wait_time`**，避免無限期卡住

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/patterns.md](references/patterns.md) | Competing consumer、session、重試模式、request-response、交易 |
| [references/dead-letter.md](references/dead-letter.md) | DLQ 處理、poison message、重新處理策略 |
| [scripts/setup_servicebus.py](scripts/setup_servicebus.py) | 管理 queue／topic／subscription 和監控 DLQ 的 CLI |
