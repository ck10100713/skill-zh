---
name: azure-eventgrid-py
description: |
  Python 版 Azure Event Grid SDK。用於發佈事件、處理 CloudEvents 和事件驅動架構。
  Triggers: "event grid", "EventGridPublisherClient", "CloudEvent", "EventGridEvent", "publish events".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-eventgrid
---

# Python 版 Azure Event Grid SDK

事件路由服務，用 pub/sub 語意來建立事件驅動應用程式。

## 安裝

```bash
pip install azure-eventgrid azure-identity
```

## 環境變數

```bash
EVENTGRID_TOPIC_ENDPOINT=https://<topic-name>.<region>.eventgrid.azure.net/api/events  # 發佈到 Event Grid topic 時必須設定
EVENTGRID_NAMESPACE_ENDPOINT=https://<namespace>.<region>.eventgrid.azure.net  # namespace 操作必須設定
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
from azure.eventgrid import EventGridPublisherClient

# 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或是在正式環境直接用特定的 credential：
# 參考 https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()

endpoint = "https://<topic-name>.<region>.eventgrid.azure.net/api/events"

with EventGridPublisherClient(endpoint, credential) as client:
    # 在這裡使用 client（操作請看後面的段落）
    ...
```

## 事件類型

| 格式 | 類別 | 使用情境 |
|--------|-------|----------|
| Cloud Events 1.0 | `CloudEvent` | 標準、可互通（建議） |
| Event Grid Schema | `EventGridEvent` | Azure 原生格式 |

## 發佈 CloudEvents

```python
from azure.eventgrid import EventGridPublisherClient, CloudEvent
from azure.identity import DefaultAzureCredential

with EventGridPublisherClient(endpoint, DefaultAzureCredential()) as client:
    # 單一事件
    event = CloudEvent(
        type="MyApp.Events.OrderCreated",
        source="/myapp/orders",
        data={"order_id": "12345", "amount": 99.99}
    )
    client.send(event)

    # 多個事件
    events = [
        CloudEvent(
            type="MyApp.Events.OrderCreated",
            source="/myapp/orders",
            data={"order_id": f"order-{i}"}
        )
        for i in range(10)
    ]
    client.send(events)
```

## 發佈 EventGridEvents

```python
from azure.eventgrid import EventGridEvent
from datetime import datetime, timezone

event = EventGridEvent(
    subject="/myapp/orders/12345",
    event_type="MyApp.Events.OrderCreated",
    data={"order_id": "12345", "amount": 99.99},
    data_version="1.0"
)

client.send(event)
```

## 事件屬性

### CloudEvent 屬性

```python
event = CloudEvent(
    type="MyApp.Events.ItemCreated",      # 必填：事件類型
    source="/myapp/items",                 # 必填：事件來源
    data={"key": "value"},                 # 事件 payload
    subject="items/123",                   # 選填：subject／路徑
    datacontenttype="application/json",   # 選填：content type
    dataschema="https://schema.example",  # 選填：schema URL
    time=datetime.now(timezone.utc),      # 選填：時間戳記
    extensions={"custom": "value"}         # 選填：自訂屬性
)
```

### EventGridEvent 屬性

```python
event = EventGridEvent(
    subject="/myapp/items/123",            # 必填：subject
    event_type="MyApp.ItemCreated",        # 必填：事件類型
    data={"key": "value"},                 # 必填：事件 payload
    data_version="1.0",                    # 必填：schema 版本
    topic="/subscriptions/.../topics/...", # 選填：自動設定
    event_time=datetime.now(timezone.utc)  # 選填：時間戳記
)
```

## 非同步 Client

```python
from azure.eventgrid.aio import EventGridPublisherClient
from azure.identity.aio import DefaultAzureCredential

async def publish_events():
    credential = DefaultAzureCredential()
    
    async with EventGridPublisherClient(endpoint, credential) as client:
        event = CloudEvent(
            type="MyApp.Events.Test",
            source="/myapp",
            data={"message": "hello"}
        )
        await client.send(event)

import asyncio
asyncio.run(publish_events())
```

## Namespace Topic（Event Grid Namespace）

用於 Event Grid Namespace（pull delivery）：

```python
from azure.eventgrid import EventGridPublisherClient
from azure.identity import DefaultAzureCredential

# Namespace endpoint（跟自訂 topic 的不一樣）
namespace_endpoint = "https://<namespace>.<region>.eventgrid.azure.net"
topic_name = "my-topic"

with EventGridPublisherClient(
    endpoint=namespace_endpoint,
    credential=DefaultAzureCredential()
) as client:
    client.send(
        event,
        namespace_topic=topic_name
    )
```

## 最佳實務

1. **同步或非同步選一種，並保持一致。** 同一條呼叫路徑裡不要混用 `azure.xxx` 的同步 client 和 `azure.xxx.aio` 的非同步 client。每個 module 選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都用 `with Client(...) as client:`（同步）或 `async with Client(...) as client:`（非同步）包起來。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，這樣 token 和 transport 才會被清掉。
3. **用 `DefaultAzureCredential`**，在本機開發和 Azure 之間驗證方式可以通用（盡量避免 connection string／API key）。
4. **新應用程式用 CloudEvents**（業界標準）
5. **發佈多個事件時用批次**
6. **帶有意義的 subject**，方便篩選
7. **高吞吐量情境用非同步 client**
8. **處理重試**：Event Grid 有內建重試
9. **設定適當的事件類型**，用於路由和篩選

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打的功能、各 operation group 的涵蓋範圍，以及正式環境檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 次要／進階情境的專屬非主打範例。 |
