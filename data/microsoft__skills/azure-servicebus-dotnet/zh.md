---
name: azure-servicebus-dotnet
description: |
  .NET 版的 Azure Service Bus SDK。提供 queue、topic、subscription 和 session 的企業級訊息服務。用於可靠的訊息傳遞、pub/sub 模式、dead letter 處理和背景處理。Triggers: "Service Bus", "ServiceBusClient", "ServiceBusSender", "ServiceBusReceiver", "ServiceBusProcessor", "message queue", "pub/sub .NET", "dead letter queue".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.Messaging.ServiceBus
---

# Azure.Messaging.ServiceBus (.NET)

企業級訊息 SDK，用 queue、topic、subscription 和 session 做可靠的訊息傳遞。

## 安裝

```bash
dotnet add package Azure.Messaging.ServiceBus
dotnet add package Azure.Identity
```

**目前版本**：v7.20.1（stable）

## 環境變數

```bash
AZURE_SERVICEBUS_FULLY_QUALIFIED_NAMESPACE=<namespace>.servicebus.windows.net  # 必填：Service Bus 的完整 namespace
AZURE_TOKEN_CREDENTIALS=prod  # 只有在 production 使用 DefaultAzureCredential 時才需要
AZURE_SERVICEBUS_CONNECTION_STRING=Endpoint=sb://...  # Entra ID 驗證的替代方案
```

## 驗證

### Microsoft Entra Token Credential

```csharp
using Azure.Identity;
using Azure.Messaging.ServiceBus;

string fullyQualifiedNamespace = "<namespace>.servicebus.windows.net";
// 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
var credential = new DefaultAzureCredential(
    DefaultAzureCredential.DefaultEnvironmentVariableName
);
// 或在 production 直接用特定的 credential：
// See https://learn.microsoft.com/dotnet/api/overview/azure/identity-readme?view=azure-dotnet#credential-classes
// var credential = new ManagedIdentityCredential();
await using ServiceBusClient client = new(fullyQualifiedNamespace, credential);
```

### Connection String

```csharp
string connectionString = "<connection_string>";
await using ServiceBusClient client = new(connectionString);
```

### ASP.NET Core Dependency Injection

```csharp
services.AddAzureClients(builder =>
{
    builder.AddServiceBusClientWithNamespace("<namespace>.servicebus.windows.net");
    builder.UseCredential(new DefaultAzureCredential());
});
```

## Client 階層

```
ServiceBusClient
├── CreateSender(queueOrTopicName)      → ServiceBusSender
├── CreateReceiver(queueName)           → ServiceBusReceiver
├── CreateReceiver(topicName, subName)  → ServiceBusReceiver
├── AcceptNextSessionAsync(queueName)   → ServiceBusSessionReceiver
├── CreateProcessor(queueName)          → ServiceBusProcessor
└── CreateSessionProcessor(queueName)   → ServiceBusSessionProcessor

ServiceBusAdministrationClient (separate client for CRUD)
```

## 核心工作流程

### 1. 傳送訊息

```csharp
await using ServiceBusClient client = new(fullyQualifiedNamespace, new DefaultAzureCredential());
ServiceBusSender sender = client.CreateSender("my-queue");

// 單一訊息
ServiceBusMessage message = new("Hello world!");
await sender.SendMessageAsync(message);

// 安全的批次處理（建議）
using ServiceBusMessageBatch batch = await sender.CreateMessageBatchAsync();
if (batch.TryAddMessage(new ServiceBusMessage("Message 1")))
{
    // 訊息已成功加入
}
if (batch.TryAddMessage(new ServiceBusMessage("Message 2")))
{
    // 訊息已成功加入
}
await sender.SendMessagesAsync(batch);
```

### 2. 接收訊息

```csharp
ServiceBusReceiver receiver = client.CreateReceiver("my-queue");

// 單一訊息
ServiceBusReceivedMessage message = await receiver.ReceiveMessageAsync();
string body = message.Body.ToString();
Console.WriteLine(body);

// Complete 這則訊息（從 queue 移除）
await receiver.CompleteMessageAsync(message);

// 批次接收
IReadOnlyList<ServiceBusReceivedMessage> messages = await receiver.ReceiveMessagesAsync(maxMessages: 10);
foreach (var msg in messages)
{
    Console.WriteLine(msg.Body.ToString());
    await receiver.CompleteMessageAsync(msg);
}
```

### 3. 訊息結算（Settlement）

```csharp
// Complete - 從 queue 移除訊息
await receiver.CompleteMessageAsync(message);

// Abandon - 釋放 lock，訊息可以再次被接收
await receiver.AbandonMessageAsync(message);

// Defer - 阻止一般接收，要用 ReceiveDeferredMessageAsync
await receiver.DeferMessageAsync(message);

// Dead Letter - 移到 dead letter 子 queue
await receiver.DeadLetterMessageAsync(message, "InvalidFormat", "Message body was not valid JSON");
```

### 4. 用 Processor 做背景處理

```csharp
ServiceBusProcessor processor = client.CreateProcessor("my-queue", new ServiceBusProcessorOptions
{
    AutoCompleteMessages = false,
    MaxConcurrentCalls = 2
});

processor.ProcessMessageAsync += async (args) =>
{
    try
    {
        string body = args.Message.Body.ToString();
        Console.WriteLine($"Received: {body}");
        await args.CompleteMessageAsync(args.Message);
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error processing: {ex.Message}");
        await args.AbandonMessageAsync(args.Message);
    }
};

processor.ProcessErrorAsync += (args) =>
{
    Console.WriteLine($"Error source: {args.ErrorSource}");
    Console.WriteLine($"Entity: {args.EntityPath}");
    Console.WriteLine($"Exception: {args.Exception}");
    return Task.CompletedTask;
};

await processor.StartProcessingAsync();
// ... 應用程式持續執行
await processor.StopProcessingAsync();
```

### 5. Session（依序處理）

```csharp
// 傳送 session 訊息
ServiceBusMessage message = new("Hello")
{
    SessionId = "order-123"
};
await sender.SendMessageAsync(message);

// 從下一個可用的 session 接收
ServiceBusSessionReceiver receiver = await client.AcceptNextSessionAsync("my-queue");

// 或從特定的 session 接收
ServiceBusSessionReceiver receiver = await client.AcceptSessionAsync("my-queue", "order-123");

// Session state 管理
await receiver.SetSessionStateAsync(new BinaryData("processing"));
BinaryData state = await receiver.GetSessionStateAsync();

// 續期 session lock
await receiver.RenewSessionLockAsync();
```

### 6. Dead Letter Queue

```csharp
// 從 dead letter queue 接收
ServiceBusReceiver dlqReceiver = client.CreateReceiver("my-queue", new ServiceBusReceiverOptions
{
    SubQueue = SubQueue.DeadLetter
});

ServiceBusReceivedMessage dlqMessage = await dlqReceiver.ReceiveMessageAsync();

// 存取 dead letter 的 metadata
string reason = dlqMessage.DeadLetterReason;
string description = dlqMessage.DeadLetterErrorDescription;
Console.WriteLine($"Dead letter reason: {reason} - {description}");
```

### 7. Topic 與 Subscription

```csharp
// 傳送到 topic
ServiceBusSender topicSender = client.CreateSender("my-topic");
await topicSender.SendMessageAsync(new ServiceBusMessage("Broadcast message"));

// 從 subscription 接收
ServiceBusReceiver subReceiver = client.CreateReceiver("my-topic", "my-subscription");
var message = await subReceiver.ReceiveMessageAsync();
```

### 8. 管理（CRUD）

```csharp
var adminClient = new ServiceBusAdministrationClient(
    fullyQualifiedNamespace, 
    new DefaultAzureCredential());

// 建立 queue
var options = new CreateQueueOptions("my-queue")
{
    MaxDeliveryCount = 10,
    LockDuration = TimeSpan.FromSeconds(30),
    RequiresSession = true,
    DeadLetteringOnMessageExpiration = true
};
QueueProperties queue = await adminClient.CreateQueueAsync(options);

// 更新 queue
queue.LockDuration = TimeSpan.FromSeconds(60);
await adminClient.UpdateQueueAsync(queue);

// 建立 topic 和 subscription
await adminClient.CreateTopicAsync(new CreateTopicOptions("my-topic"));
await adminClient.CreateSubscriptionAsync(new CreateSubscriptionOptions("my-topic", "my-subscription"));

// 刪除
await adminClient.DeleteQueueAsync("my-queue");
```

### 9. 跨 Entity 交易

```csharp
var options = new ServiceBusClientOptions { EnableCrossEntityTransactions = true };
await using var client = new ServiceBusClient(connectionString, options);

ServiceBusReceiver receiverA = client.CreateReceiver("queueA");
ServiceBusSender senderB = client.CreateSender("queueB");

ServiceBusReceivedMessage receivedMessage = await receiverA.ReceiveMessageAsync();

using (var ts = new TransactionScope(TransactionScopeAsyncFlowOption.Enabled))
{
    await receiverA.CompleteMessageAsync(receivedMessage);
    await senderB.SendMessageAsync(new ServiceBusMessage("Forwarded"));
    ts.Complete();
}
```

## 重要型別參考

| 型別 | 用途 |
|------|---------|
| `ServiceBusClient` | 主要進入點，管理連線 |
| `ServiceBusSender` | 傳送訊息到 queue／topic |
| `ServiceBusReceiver` | 從 queue／subscription 接收訊息 |
| `ServiceBusSessionReceiver` | 接收 session 訊息 |
| `ServiceBusProcessor` | 背景訊息處理 |
| `ServiceBusSessionProcessor` | 背景 session 處理 |
| `ServiceBusAdministrationClient` | queue／topic／subscription 的 CRUD |
| `ServiceBusMessage` | 要傳送的訊息 |
| `ServiceBusReceivedMessage` | 帶 metadata 的已接收訊息 |
| `ServiceBusMessageBatch` | 一批訊息 |

## 最佳實務

1. **用 singleton** — Client、sender、receiver 和 processor 都是 thread-safe
2. **一定要 dispose** — 用 `await using` 或呼叫 `DisposeAsync()`
3. **Dispose 順序** — 先關 sender／receiver／processor，再關 client
4. **用 DefaultAzureCredential** — production 優先用它，不要用 connection string
5. **背景工作用 processor** — 它會自動處理 lock 續期
6. **用安全的批次處理** — `CreateMessageBatchAsync()` 和 `TryAddMessage()`
7. **處理暫時性錯誤** — 用 `ServiceBusException.Reason`
8. **設定 transport** — 如果 port 5671/5672 被擋，用 `AmqpWebSockets`
9. **設定適當的 lock 時間** — 預設是 30 秒
10. **要順序就用 session** — 同一個 session 內是 FIFO

## 錯誤處理

```csharp
try
{
    await sender.SendMessageAsync(message);
}
catch (ServiceBusException ex) when (ex.Reason == ServiceBusFailureReason.ServiceBusy)
{
    // 用 backoff 重試
}
catch (ServiceBusException ex)
{
    Console.WriteLine($"Service Bus Error: {ex.Reason} - {ex.Message}");
}
```

## 相關 SDK

| SDK | 用途 | 安裝 |
|-----|---------|---------|
| `Azure.Messaging.ServiceBus` | Service Bus（本 SDK） | `dotnet add package Azure.Messaging.ServiceBus` |
| `Azure.Messaging.EventHubs` | 事件串流 | `dotnet add package Azure.Messaging.EventHubs` |
| `Azure.Messaging.EventGrid` | 事件路由 | `dotnet add package Azure.Messaging.EventGrid` |

## 參考連結

| 資源 | URL |
|----------|-----|
| NuGet Package | https://www.nuget.org/packages/Azure.Messaging.ServiceBus |
| API Reference | https://learn.microsoft.com/dotnet/api/azure.messaging.servicebus |
| GitHub Source | https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/servicebus/Azure.Messaging.ServiceBus |
| Troubleshooting | https://github.com/Azure/azure-sdk-for-net/blob/main/sdk/servicebus/Azure.Messaging.ServiceBus/TROUBLESHOOTING.md |
