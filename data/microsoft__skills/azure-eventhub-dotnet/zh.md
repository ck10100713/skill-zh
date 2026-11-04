---
name: azure-eventhub-dotnet
description: |
  .NET 版 Azure Event Hubs SDK。用於高吞吐量的事件串流：送出事件（EventHubProducerClient、EventHubBufferedProducerClient）、接收事件（帶 checkpoint 的 EventProcessorClient）、partition 管理，以及即時資料匯入。Triggers: "Event Hubs", "event streaming", "EventHubProducerClient", "EventProcessorClient", "send events", "receive events", "checkpointing", "partition".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.Messaging.EventHubs
---

# Azure.Messaging.EventHubs (.NET)

透過 Azure Event Hubs 收發事件的高吞吐量事件串流 SDK。

## 安裝

```bash
# Core package (sending and simple receiving)
dotnet add package Azure.Messaging.EventHubs

# Processor package (production receiving with checkpointing)
dotnet add package Azure.Messaging.EventHubs.Processor

# Authentication
dotnet add package Azure.Identity

# For checkpointing (required by EventProcessorClient)
dotnet add package Azure.Storage.Blobs
```

**目前版本**：Azure.Messaging.EventHubs v5.12.2、Azure.Messaging.EventHubs.Processor v5.12.2

## 環境變數

```bash
EVENTHUB_FULLY_QUALIFIED_NAMESPACE=<namespace>.servicebus.windows.net  # 必須設定：Event Hubs 的完整 namespace 名稱
EVENTHUB_NAME=<event-hub-name>  # 必須設定：Event Hub 名稱
BLOB_STORAGE_CONNECTION_STRING=<storage-connection-string>  # Entra ID 驗證的替代方案
BLOB_CONTAINER_NAME=<checkpoint-container>  # 必須設定：checkpoint container 名稱
EVENTHUB_CONNECTION_STRING=Endpoint=sb://<namespace>.servicebus.windows.net/;SharedAccessKeyName=...  # Entra ID 驗證的替代方案
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境使用 DefaultAzureCredential 時才需要
```

## 驗證

```csharp
using Azure.Identity;
using Azure.Messaging.EventHubs;
using Azure.Messaging.EventHubs.Producer;

// 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
var credential = new DefaultAzureCredential(
    DefaultAzureCredential.DefaultEnvironmentVariableName
);
// 或是在正式環境直接用特定的 credential：
// 參考 https://learn.microsoft.com/dotnet/api/overview/azure/identity-readme?view=azure-dotnet#credential-classes
// var credential = new ManagedIdentityCredential();

var fullyQualifiedNamespace = Environment.GetEnvironmentVariable("EVENTHUB_FULLY_QUALIFIED_NAMESPACE");
var eventHubName = Environment.GetEnvironmentVariable("EVENTHUB_NAME");

var producer = new EventHubProducerClient(
    fullyQualifiedNamespace,
    eventHubName,
    credential);
```

**需要的 RBAC 角色**：
- **送出**：`Azure Event Hubs Data Sender`
- **接收**：`Azure Event Hubs Data Receiver`
- **兩者都要**：`Azure Event Hubs Data Owner`

## Client 類型

| Client | 用途 | 何時使用 |
|--------|---------|-------------|
| `EventHubProducerClient` | 立刻分批送出事件 | 即時傳送，完全掌控批次 |
| `EventHubBufferedProducerClient` | 自動批次，在背景送出 | 大量、送出後不管的情境 |
| `EventHubConsumerClient` | 簡單的事件讀取 | 只限做原型，**不要**用在正式環境 |
| `EventProcessorClient` | 正式環境的事件處理 | **正式環境接收一律用這個** |

## 核心流程

### 1. 送出事件（批次）

```csharp
using Azure.Identity;
using Azure.Messaging.EventHubs;
using Azure.Messaging.EventHubs.Producer;

await using var producer = new EventHubProducerClient(
    fullyQualifiedNamespace,
    eventHubName,
    new DefaultAzureCredential());

// 建立批次（自動遵守大小上限）
using EventDataBatch batch = await producer.CreateBatchAsync();

// 把事件加進批次
var events = new[]
{
    new EventData(BinaryData.FromString("{\"id\": 1, \"message\": \"Hello\"}")),
    new EventData(BinaryData.FromString("{\"id\": 2, \"message\": \"World\"}"))
};

foreach (var eventData in events)
{
    if (!batch.TryAdd(eventData))
    {
        // 批次滿了：先送出，再建新的
        await producer.SendAsync(batch);
        batch = await producer.CreateBatchAsync();
        
        if (!batch.TryAdd(eventData))
        {
            throw new Exception("Event too large for empty batch");
        }
    }
}

// 送出剩下的事件
if (batch.Count > 0)
{
    await producer.SendAsync(batch);
}
```

### 2. 送出事件（Buffered，大量）

```csharp
using Azure.Messaging.EventHubs.Producer;

var options = new EventHubBufferedProducerClientOptions
{
    MaximumWaitTime = TimeSpan.FromSeconds(1)
};

await using var producer = new EventHubBufferedProducerClient(
    fullyQualifiedNamespace,
    eventHubName,
    new DefaultAzureCredential(),
    options);

// 處理送出成功／失敗
producer.SendEventBatchSucceededAsync += args =>
{
    Console.WriteLine($"Batch sent: {args.EventBatch.Count} events");
    return Task.CompletedTask;
};

producer.SendEventBatchFailedAsync += args =>
{
    Console.WriteLine($"Batch failed: {args.Exception.Message}");
    return Task.CompletedTask;
};

// 把事件排入佇列（在背景自動送出）
for (int i = 0; i < 1000; i++)
{
    await producer.EnqueueEventAsync(new EventData($"Event {i}"));
}

// dispose 之前先 flush 剩下的事件
await producer.FlushAsync();
```

### 3. 接收事件（正式環境：EventProcessorClient）

```csharp
using Azure.Identity;
using Azure.Messaging.EventHubs;
using Azure.Messaging.EventHubs.Consumer;
using Azure.Messaging.EventHubs.Processor;
using Azure.Storage.Blobs;

// 用來做 checkpoint 的 Blob container
var blobClient = new BlobContainerClient(
    Environment.GetEnvironmentVariable("BLOB_STORAGE_CONNECTION_STRING"),
    Environment.GetEnvironmentVariable("BLOB_CONTAINER_NAME"));

await blobClient.CreateIfNotExistsAsync();

// 建立 processor
var processor = new EventProcessorClient(
    blobClient,
    EventHubConsumerClient.DefaultConsumerGroup,
    fullyQualifiedNamespace,
    eventHubName,
    new DefaultAzureCredential());

// 處理事件
processor.ProcessEventAsync += async args =>
{
    Console.WriteLine($"Partition: {args.Partition.PartitionId}");
    Console.WriteLine($"Data: {args.Data.EventBody}");
    
    // 處理完之後做 checkpoint（或批次做 checkpoint）
    await args.UpdateCheckpointAsync();
};

// 處理錯誤
processor.ProcessErrorAsync += args =>
{
    Console.WriteLine($"Error: {args.Exception.Message}");
    Console.WriteLine($"Partition: {args.PartitionId}");
    return Task.CompletedTask;
};

// 開始處理
await processor.StartProcessingAsync();

// 跑到被取消為止
await Task.Delay(Timeout.Infinite, cancellationToken);

// 優雅停止
await processor.StopProcessingAsync();
```

### 4. Partition 操作

```csharp
// 取得 partition ID
string[] partitionIds = await producer.GetPartitionIdsAsync();

// 送到特定 partition（少用）
var options = new SendEventOptions
{
    PartitionId = "0"
};
await producer.SendAsync(events, options);

// 用 partition key（要保證順序時建議用）
var batchOptions = new CreateBatchOptions
{
    PartitionKey = "customer-123"  // key 相同的事件會進同一個 partition
};
using var batch = await producer.CreateBatchAsync(batchOptions);
```

## EventPosition 選項

控制從哪裡開始讀：

```csharp
// 從頭開始
EventPosition.Earliest

// 從尾端開始（只讀新事件）
EventPosition.Latest

// 從特定 offset 開始
EventPosition.FromOffset(12345)

// 從特定 sequence number 開始
EventPosition.FromSequenceNumber(100)

// 從特定時間開始
EventPosition.FromEnqueuedTime(DateTimeOffset.UtcNow.AddHours(-1))
```

## ASP.NET Core 整合

```csharp
// Program.cs
using Azure.Identity;
using Azure.Messaging.EventHubs.Producer;
using Microsoft.Extensions.Azure;

builder.Services.AddAzureClients(clientBuilder =>
{
    clientBuilder.AddEventHubProducerClient(
        builder.Configuration["EventHub:FullyQualifiedNamespace"],
        builder.Configuration["EventHub:Name"]);
    
    clientBuilder.UseCredential(new DefaultAzureCredential());
});

// 注入到 controller/service
public class EventService
{
    private readonly EventHubProducerClient _producer;
    
    public EventService(EventHubProducerClient producer)
    {
        _producer = producer;
    }
    
    public async Task SendAsync(string message)
    {
        using var batch = await _producer.CreateBatchAsync();
        batch.TryAdd(new EventData(message));
        await _producer.SendAsync(batch);
    }
}
```

## 最佳實務

1. **接收用 `EventProcessorClient`**：正式環境絕對不要用 `EventHubConsumerClient`
2. **有策略地做 checkpoint**：每 N 個事件或每隔一段時間做一次，不要每個事件都做
3. **用 partition key**：保證同一個 partition 內的順序
4. **重複使用 client**：建一次，當 singleton 用（thread-safe）
5. **用 `await using`**：確保正確 dispose
6. **處理 `ProcessErrorAsync`**：一定要註冊錯誤 handler
7. **批次送事件**：用 `CreateBatchAsync()` 來遵守大小上限
8. **用 buffered producer**：大量情境下可以自動批次

## 錯誤處理

```csharp
using Azure.Messaging.EventHubs;

try
{
    await producer.SendAsync(batch);
}
catch (EventHubsException ex) when (ex.Reason == EventHubsException.FailureReason.ServiceBusy)
{
    // 用 backoff 重試
    await Task.Delay(TimeSpan.FromSeconds(5));
}
catch (EventHubsException ex) when (ex.IsTransient)
{
    // 暫時性錯誤：可以安全重試
    Console.WriteLine($"Transient error: {ex.Message}");
}
catch (EventHubsException ex)
{
    // 非暫時性錯誤
    Console.WriteLine($"Error: {ex.Reason} - {ex.Message}");
}
```

## Checkpoint 策略

| 策略 | 何時使用 |
|----------|-------------|
| 每個事件 | 低流量、關鍵資料 |
| 每 N 個事件 | 吞吐量和可靠性之間取得平衡 |
| 依時間 | 固定的 checkpoint 間隔 |
| 批次完成 | 處理完一個邏輯批次之後 |

```csharp
// 每 100 個事件做一次 checkpoint
private int _eventCount = 0;

processor.ProcessEventAsync += async args =>
{
    // 處理事件...
    
    _eventCount++;
    if (_eventCount >= 100)
    {
        await args.UpdateCheckpointAsync();
        _eventCount = 0;
    }
};
```

## 相關 SDK

| SDK | 用途 | 安裝 |
|-----|---------|---------|
| `Azure.Messaging.EventHubs` | 核心收發 | `dotnet add package Azure.Messaging.EventHubs` |
| `Azure.Messaging.EventHubs.Processor` | 正式環境處理 | `dotnet add package Azure.Messaging.EventHubs.Processor` |
| `Azure.ResourceManager.EventHubs` | Management plane（建立 hub） | `dotnet add package Azure.ResourceManager.EventHubs` |
| `Microsoft.Azure.WebJobs.Extensions.EventHubs` | Azure Functions binding | `dotnet add package Microsoft.Azure.WebJobs.Extensions.EventHubs` |
