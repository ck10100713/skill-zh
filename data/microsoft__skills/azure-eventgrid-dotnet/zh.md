---
name: azure-eventgrid-dotnet
description: |
  .NET 版 Azure Event Grid SDK。用來發佈和消費 Azure Event Grid 事件的 client 函式庫。用於事件驅動架構、pub/sub 訊息、CloudEvents 和 EventGridEvents。Triggers: "Event Grid", "EventGridPublisherClient", "CloudEvent", "EventGridEvent", "publish events .NET", "event-driven", "pub/sub".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.Messaging.EventGrid
---

# Azure.Messaging.EventGrid (.NET)

把事件發佈到 Azure Event Grid 的 topic、domain 和 namespace 的 client 函式庫。

## 安裝

```bash
# For topics and domains (push delivery)
dotnet add package Azure.Messaging.EventGrid

# For namespaces (pull delivery)
dotnet add package Azure.Messaging.EventGrid.Namespaces

# For CloudNative CloudEvents interop
dotnet add package Microsoft.Azure.Messaging.EventGrid.CloudNativeCloudEvents
```

**目前版本**：4.28.0（stable）

## 環境變數

```bash
EVENT_GRID_TOPIC_ENDPOINT=https://<topic-name>.<region>.eventgrid.azure.net/api/events  # 必須設定：Event Grid topic 或 domain 的 endpoint
EVENT_GRID_TOPIC_KEY=<access-key>  # 只有用 AzureKeyCredential 驗證時才需要
EVENT_GRID_NAMESPACE_ENDPOINT=https://<namespace>.<region>.eventgrid.azure.net  # 選用：Event Grid namespace 的 endpoint
EVENT_GRID_TOPIC_NAME=<topic-name>  # 必須設定：Event Grid topic 名稱
EVENT_GRID_SUBSCRIPTION_NAME=<subscription-name>  # 選用：Event Grid subscription 名稱
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境使用 DefaultAzureCredential 時才需要
```

## Client 階層

```
Push Delivery (Topics/Domains)
└── EventGridPublisherClient
    ├── SendEventAsync(EventGridEvent)
    ├── SendEventsAsync(IEnumerable<EventGridEvent>)
    ├── SendEventAsync(CloudEvent)
    └── SendEventsAsync(IEnumerable<CloudEvent>)

Pull Delivery (Namespaces)
├── EventGridSenderClient
│   └── SendAsync(CloudEvent)
└── EventGridReceiverClient
    ├── ReceiveAsync()
    ├── AcknowledgeAsync()
    ├── ReleaseAsync()
    └── RejectAsync()
```

## 驗證

### API Key 驗證

```csharp
using Azure;
using Azure.Messaging.EventGrid;

EventGridPublisherClient client = new(
    new Uri("https://mytopic.eastus-1.eventgrid.azure.net/api/events"),
    new AzureKeyCredential("<access-key>"));
```

### Microsoft Entra Token Credential

```csharp
using Azure.Identity;
using Azure.Messaging.EventGrid;

// 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
var credential = new DefaultAzureCredential(
    DefaultAzureCredential.DefaultEnvironmentVariableName
);
// 或是在正式環境直接用特定的 credential：
// 參考 https://learn.microsoft.com/dotnet/api/overview/azure/identity-readme?view=azure-dotnet#credential-classes
// var credential = new ManagedIdentityCredential();
EventGridPublisherClient client = new(
    new Uri("https://mytopic.eastus-1.eventgrid.azure.net/api/events"),
    credential);
```

### SAS Token 驗證

```csharp
string sasToken = EventGridPublisherClient.BuildSharedAccessSignature(
    new Uri(topicEndpoint),
    DateTimeOffset.UtcNow.AddHours(1),
    new AzureKeyCredential(topicKey));

var sasCredential = new AzureSasCredential(sasToken);
EventGridPublisherClient client = new(
    new Uri(topicEndpoint),
    sasCredential);
```

## 發佈事件

### EventGridEvent Schema

```csharp
EventGridPublisherClient client = new(
    new Uri(topicEndpoint),
    new AzureKeyCredential(topicKey));

// 單一事件
EventGridEvent egEvent = new(
    subject: "orders/12345",
    eventType: "Order.Created",
    dataVersion: "1.0",
    data: new { OrderId = "12345", Amount = 99.99 });

await client.SendEventAsync(egEvent);

// 一批事件
List<EventGridEvent> events = new()
{
    new EventGridEvent(
        subject: "orders/12345",
        eventType: "Order.Created",
        dataVersion: "1.0",
        data: new OrderData { OrderId = "12345", Amount = 99.99 }),
    new EventGridEvent(
        subject: "orders/12346",
        eventType: "Order.Created",
        dataVersion: "1.0",
        data: new OrderData { OrderId = "12346", Amount = 149.99 })
};

await client.SendEventsAsync(events);
```

### CloudEvent Schema

```csharp
CloudEvent cloudEvent = new(
    source: "/orders/system",
    type: "Order.Created",
    data: new { OrderId = "12345", Amount = 99.99 });

cloudEvent.Subject = "orders/12345";
cloudEvent.Id = Guid.NewGuid().ToString();
cloudEvent.Time = DateTimeOffset.UtcNow;

await client.SendEventAsync(cloudEvent);

// 一批 CloudEvent
List<CloudEvent> cloudEvents = new()
{
    new CloudEvent("/orders", "Order.Created", new { OrderId = "1" }),
    new CloudEvent("/orders", "Order.Updated", new { OrderId = "2" })
};

await client.SendEventsAsync(cloudEvents);
```

### 發佈到 Event Grid Domain

```csharp
// 事件必須指定 Topic 屬性，domain 才能做路由
List<EventGridEvent> events = new()
{
    new EventGridEvent(
        subject: "orders/12345",
        eventType: "Order.Created",
        dataVersion: "1.0",
        data: new { OrderId = "12345" })
    {
        Topic = "orders-topic"  // Domain topic 名稱
    },
    new EventGridEvent(
        subject: "inventory/item-1",
        eventType: "Inventory.Updated",
        dataVersion: "1.0",
        data: new { ItemId = "item-1" })
    {
        Topic = "inventory-topic"
    }
};

await client.SendEventsAsync(events);
```

### 自訂序列化

```csharp
using System.Text.Json;

var serializerOptions = new JsonSerializerOptions
{
    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
};

var customSerializer = new JsonObjectSerializer(serializerOptions);

EventGridEvent egEvent = new(
    subject: "orders/12345",
    eventType: "Order.Created",
    dataVersion: "1.0",
    data: customSerializer.Serialize(new OrderData { OrderId = "12345" }));

await client.SendEventAsync(egEvent);
```

## Pull Delivery（Namespace）

### 把事件送到 Namespace Topic

```csharp
using Azure;
using Azure.Messaging;
using Azure.Messaging.EventGrid.Namespaces;

var senderClient = new EventGridSenderClient(
    new Uri(namespaceEndpoint),
    topicName,
    new AzureKeyCredential(topicKey));

// 送單一事件
CloudEvent cloudEvent = new("employee_source", "Employee.Created", 
    new { Name = "John", Age = 30 });
await senderClient.SendAsync(cloudEvent);

// 批次送出
await senderClient.SendAsync(new[]
{
    new CloudEvent("source", "type", new { Name = "Alice" }),
    new CloudEvent("source", "type", new { Name = "Bob" })
});
```

### 接收並處理事件

```csharp
var receiverClient = new EventGridReceiverClient(
    new Uri(namespaceEndpoint),
    topicName,
    subscriptionName,
    new AzureKeyCredential(topicKey));

// 接收事件
ReceiveResult result = await receiverClient.ReceiveAsync(maxEvents: 10);

List<string> lockTokensToAck = new();
List<string> lockTokensToRelease = new();

foreach (ReceiveDetails detail in result.Details)
{
    CloudEvent cloudEvent = detail.Event;
    string lockToken = detail.BrokerProperties.LockToken;
    
    try
    {
        // 處理事件
        Console.WriteLine($"Event: {cloudEvent.Type}, Data: {cloudEvent.Data}");
        lockTokensToAck.Add(lockToken);
    }
    catch (Exception)
    {
        // 釋放，等著重試
        lockTokensToRelease.Add(lockToken);
    }
}

// Acknowledge 處理成功的事件
if (lockTokensToAck.Any())
{
    await receiverClient.AcknowledgeAsync(lockTokensToAck);
}

// 釋放事件，等著重試
if (lockTokensToRelease.Any())
{
    await receiverClient.ReleaseAsync(lockTokensToRelease);
}
```

### 拒絕事件（Dead Letter）

```csharp
// 拒絕無法處理的事件
await receiverClient.RejectAsync(new[] { lockToken });
```

## 消費事件（Azure Functions）

### EventGridEvent Trigger

```csharp
using Azure.Messaging.EventGrid;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.EventGrid;

public static class EventGridFunction
{
    [FunctionName("ProcessEventGridEvent")]
    public static void Run(
        [EventGridTrigger] EventGridEvent eventGridEvent,
        ILogger log)
    {
        log.LogInformation($"Event Type: {eventGridEvent.EventType}");
        log.LogInformation($"Subject: {eventGridEvent.Subject}");
        log.LogInformation($"Data: {eventGridEvent.Data}");
    }
}
```

### CloudEvent Trigger

```csharp
using Azure.Messaging;
using Microsoft.Azure.Functions.Worker;

public class CloudEventFunction
{
    [Function("ProcessCloudEvent")]
    public void Run(
        [EventGridTrigger] CloudEvent cloudEvent,
        FunctionContext context)
    {
        var logger = context.GetLogger("ProcessCloudEvent");
        logger.LogInformation($"Event Type: {cloudEvent.Type}");
        logger.LogInformation($"Source: {cloudEvent.Source}");
        logger.LogInformation($"Data: {cloudEvent.Data}");
    }
}
```

## 解析事件

### 解析 EventGridEvent

```csharp
// 從 JSON 字串
string json = "..."; // Event Grid webhook 的 payload
EventGridEvent[] events = EventGridEvent.ParseMany(BinaryData.FromString(json));

foreach (EventGridEvent egEvent in events)
{
    if (egEvent.TryGetSystemEventData(out object systemEvent))
    {
        // 處理系統事件
        switch (systemEvent)
        {
            case StorageBlobCreatedEventData blobCreated:
                Console.WriteLine($"Blob created: {blobCreated.Url}");
                break;
        }
    }
    else
    {
        // 處理自訂事件
        var customData = egEvent.Data.ToObjectFromJson<MyCustomData>();
    }
}
```

### 解析 CloudEvent

```csharp
CloudEvent[] cloudEvents = CloudEvent.ParseMany(BinaryData.FromString(json));

foreach (CloudEvent cloudEvent in cloudEvents)
{
    var data = cloudEvent.Data.ToObjectFromJson<MyEventData>();
    Console.WriteLine($"Type: {cloudEvent.Type}, Data: {data}");
}
```

## 系統事件

```csharp
// 常見的系統事件類型
using Azure.Messaging.EventGrid.SystemEvents;

// Storage 事件
StorageBlobCreatedEventData blobCreated;
StorageBlobDeletedEventData blobDeleted;

// 資源事件
ResourceWriteSuccessEventData resourceCreated;
ResourceDeleteSuccessEventData resourceDeleted;

// App Service 事件
WebAppUpdatedEventData webAppUpdated;

// Container Registry 事件
ContainerRegistryImagePushedEventData imagePushed;

// IoT Hub 事件
IotHubDeviceCreatedEventData deviceCreated;
```

## 主要型別參考

| 型別 | 用途 |
|------|---------|
| `EventGridPublisherClient` | 發佈到 topic／domain |
| `EventGridSenderClient` | 送到 namespace topic |
| `EventGridReceiverClient` | 從 namespace subscription 接收 |
| `EventGridEvent` | Event Grid 原生 schema |
| `CloudEvent` | CloudEvents 1.0 schema |
| `ReceiveResult` | Pull delivery 的回應 |
| `ReceiveDetails` | 帶 broker 屬性的事件 |
| `BrokerProperties` | Lock token、遞送次數 |

## 事件 Schema 比較

| 特性 | EventGridEvent | CloudEvent |
|---------|----------------|------------|
| 標準 | Azure 專屬 | CNCF 標準 |
| 必填欄位 | subject, eventType, dataVersion, data | source, type |
| 擴充性 | 有限 | 有擴充屬性 |
| 互通性 | 只限 Azure | 跨平台 |

## 最佳實務

1. **用 CloudEvents**：新的實作優先用 CloudEvents（業界標準）
2. **批次送事件**：一次呼叫送多個事件比較有效率
3. **用 Entra ID**：優先用 managed identity，不要用 access key
4. **Handler 要冪等**：事件可能會被遞送不只一次
5. **設定事件 TTL**：為 namespace 事件設定 time-to-live
6. **處理部分失敗**：逐一 acknowledge／release 事件
7. **用 dead-letter**：為失敗的事件設定 dead-letter
8. **驗證 schema**：處理之前先驗證事件資料

## 錯誤處理

```csharp
using Azure;

try
{
    await client.SendEventAsync(cloudEvent);
}
catch (RequestFailedException ex) when (ex.Status == 401)
{
    Console.WriteLine("Authentication failed - check credentials");
}
catch (RequestFailedException ex) when (ex.Status == 403)
{
    Console.WriteLine("Authorization failed - check RBAC permissions");
}
catch (RequestFailedException ex) when (ex.Status == 413)
{
    Console.WriteLine("Payload too large - max 1MB per event, 1MB total batch");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Event Grid error: {ex.Status} - {ex.Message}");
}
```

## Failover 模式

```csharp
try
{
    var primaryClient = new EventGridPublisherClient(primaryUri, primaryKey);
    await primaryClient.SendEventsAsync(events);
}
catch (RequestFailedException)
{
    // Failover 到次要 region
    var secondaryClient = new EventGridPublisherClient(secondaryUri, secondaryKey);
    await secondaryClient.SendEventsAsync(events);
}
```

## 相關 SDK

| SDK | 用途 | 安裝 |
|-----|---------|---------|
| `Azure.Messaging.EventGrid` | Topic／Domain（本 SDK） | `dotnet add package Azure.Messaging.EventGrid` |
| `Azure.Messaging.EventGrid.Namespaces` | Pull delivery | `dotnet add package Azure.Messaging.EventGrid.Namespaces` |
| `Azure.Identity` | 驗證 | `dotnet add package Azure.Identity` |
| `Microsoft.Azure.WebJobs.Extensions.EventGrid` | Azure Functions trigger | `dotnet add package Microsoft.Azure.WebJobs.Extensions.EventGrid` |

## 參考連結

| 資源 | URL |
|----------|-----|
| NuGet Package | https://www.nuget.org/packages/Azure.Messaging.EventGrid |
| API Reference | https://learn.microsoft.com/dotnet/api/azure.messaging.eventgrid |
| Quickstart | https://learn.microsoft.com/azure/event-grid/custom-event-quickstart |
| Pull Delivery | https://learn.microsoft.com/azure/event-grid/pull-delivery-overview |
| GitHub Source | https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/eventgrid/Azure.Messaging.EventGrid |
