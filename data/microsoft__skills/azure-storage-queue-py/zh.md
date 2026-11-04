---
name: azure-storage-queue-py
description: |
  Python 版的 Azure Queue Storage SDK。用於可靠的訊息排隊、任務分配和非同步處理。
  Triggers: "queue storage", "QueueServiceClient", "QueueClient", "message queue", "dequeue".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-storage-queue
---

# Python 版 Azure Queue Storage SDK

簡單、划算的訊息排隊服務，用於非同步通訊。

## 安裝

```bash
pip install azure-storage-queue azure-identity
```

## 環境變數

```bash
AZURE_STORAGE_ACCOUNT_URL=https://<account>.queue.core.windows.net  # 所有驗證方式都必填
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
from azure.storage.queue import QueueServiceClient, QueueClient

# 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在 production 直接用特定的 credential：
# See https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()
account_url = "https://<account>.queue.core.windows.net"

# Service client
with QueueServiceClient(account_url=account_url, credential=credential) as service_client:
    # 在這裡使用 service_client（各種操作請看後面的章節）
    ...

# Queue client
with QueueClient(account_url=account_url, queue_name="myqueue", credential=credential) as queue_client:
    # 在這裡使用 queue_client（各種操作請看後面的章節）
    ...
```

## Queue 操作

```python
# 建立 queue
service_client.create_queue("myqueue")

# 取得 queue client
queue_client = service_client.get_queue_client("myqueue")

# 刪除 queue
service_client.delete_queue("myqueue")

# 列出 queue
for queue in service_client.list_queues():
    print(queue.name)
```

## 傳送訊息

```python
# 傳送訊息（字串）
queue_client.send_message("Hello, Queue!")

# 帶選項傳送
queue_client.send_message(
    content="Delayed message",
    visibility_timeout=60,  # 隱藏 60 秒
    time_to_live=3600       # 1 小時後過期
)

# 傳送 JSON
import json
data = {"task": "process", "id": 123}
queue_client.send_message(json.dumps(data))
```

## 接收訊息

```python
# 接收訊息（會讓它們暫時不可見）
messages = queue_client.receive_messages(
    messages_per_page=10,
    visibility_timeout=30  # 30 秒內處理完
)

for message in messages:
    print(f"ID: {message.id}")
    print(f"Content: {message.content}")
    print(f"Dequeue count: {message.dequeue_count}")
    
    # 處理訊息...
    
    # 處理完後刪除
    queue_client.delete_message(message)
```

## Peek 訊息

```python
# Peek 但不隱藏（不影響可見性）
messages = queue_client.peek_messages(max_messages=5)

for message in messages:
    print(message.content)
```

## 更新訊息

```python
# 延長可見時間或更新內容
messages = queue_client.receive_messages()
for message in messages:
    # 延長逾時時間（需要更多時間）
    queue_client.update_message(
        message,
        visibility_timeout=60
    )
    
    # 更新內容和逾時時間
    queue_client.update_message(
        message,
        content="Updated content",
        visibility_timeout=60
    )
```

## 刪除訊息

```python
# 處理成功後刪除
messages = queue_client.receive_messages()
for message in messages:
    try:
        # 處理...
        queue_client.delete_message(message)
    except Exception:
        # 逾時後訊息會再變成可見
        pass
```

## 清空 Queue

```python
# 刪除所有訊息
queue_client.clear_messages()
```

## Queue 屬性

```python
# 取得 queue 屬性
properties = queue_client.get_queue_properties()
print(f"Approximate message count: {properties.approximate_message_count}")

# 設定／取得 metadata
queue_client.set_queue_metadata(metadata={"environment": "production"})
properties = queue_client.get_queue_properties()
print(properties.metadata)
```

## 非同步 Client

```python
from azure.storage.queue.aio import QueueServiceClient, QueueClient
from azure.identity.aio import DefaultAzureCredential

async def queue_operations():
    credential = DefaultAzureCredential()
    
    async with QueueClient(
        account_url="https://<account>.queue.core.windows.net",
        queue_name="myqueue",
        credential=credential
    ) as client:
        # 傳送
        await client.send_message("Async message")
        
        # 接收
        async for message in client.receive_messages():
            print(message.content)
            await client.delete_message(message)

import asyncio
asyncio.run(queue_operations())
```

## Base64 編碼

```python
from azure.storage.queue import QueueClient, BinaryBase64EncodePolicy, BinaryBase64DecodePolicy

# 用於二進位資料
with QueueClient(
    account_url=account_url,
    queue_name="myqueue",
    credential=credential,
    message_encode_policy=BinaryBase64EncodePolicy(),
    message_decode_policy=BinaryBase64DecodePolicy()
) as queue_client:
    # 傳送 bytes
    queue_client.send_message(b"Binary content")
```

## 最佳實務

1. **同步或非同步選一個，然後保持一致。** 同一條呼叫路徑裡，不要混用 `azure.xxx` 同步 client 和 `azure.xxx.aio` 非同步 client。每個 module 只選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都用 `with Client(...) as client:`（同步）或 `async with Client(...) as client:`（非同步）包起來。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，token 和 transport 才會清乾淨。
3. **用 `DefaultAzureCredential`**，在本機開發和 Azure 之間都能用同一套驗證（盡量避免 connection string／API key）。
4. **處理完要刪除訊息**，避免重複處理
5. **依處理時間設定適當的 visibility timeout**
6. **處理 `dequeue_count`**，用來偵測 poison message
7. 高吞吐量的情境**用非同步 client**
8. 監控時**用 `peek_messages`**，才不會影響 queue
9. **設定 `time_to_live`**，避免訊息過期還留著
10. 需要進階功能（session、topic）時**考慮改用 Service Bus**

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主要的能力、operation group 涵蓋範圍，以及 production 檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 次要／進階情境的專屬非主要流程範例。 |
