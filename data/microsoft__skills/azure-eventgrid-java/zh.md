---
name: azure-eventgrid-java
description: 用 Java 版 Azure Event Grid SDK 建立事件驅動應用程式。發佈事件、實作 pub/sub 模式，或透過事件整合 Azure 服務時使用。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: com.azure:azure-messaging-eventgrid
---

# Java 版 Azure Event Grid SDK

用 Java 版 Azure Event Grid SDK 建立事件驅動應用程式。

## 安裝

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-messaging-eventgrid</artifactId>
    <version>4.27.0</version>
</dependency>
```

## 建立 Client

### EventGridPublisherClient

```java
import com.azure.messaging.eventgrid.EventGridPublisherClient;
import com.azure.messaging.eventgrid.EventGridPublisherClientBuilder;
import com.azure.core.credential.AzureKeyCredential;

// 用 API Key
EventGridPublisherClient<EventGridEvent> client = new EventGridPublisherClientBuilder()
    .endpoint("<topic-endpoint>")
    .credential(new AzureKeyCredential("<access-key>"))
    .buildEventGridEventPublisherClient();

// 給 CloudEvents 用
EventGridPublisherClient<CloudEvent> cloudClient = new EventGridPublisherClientBuilder()
    .endpoint("<topic-endpoint>")
    .credential(new AzureKeyCredential("<access-key>"))
    .buildCloudEventPublisherClient();
```

### 用 DefaultAzureCredential

```java
import com.azure.core.credential.TokenCredential;
import com.azure.identity.AzureIdentityEnvVars;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.identity.ManagedIdentityCredentialBuilder;

// 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
TokenCredential credential = new DefaultAzureCredentialBuilder()
    .requireEnvVars(AzureIdentityEnvVars.AZURE_TOKEN_CREDENTIALS)
    .build();
// 或是在正式環境直接用特定的 credential：
// 參考 https://learn.microsoft.com/java/api/overview/azure/identity-readme?view=azure-java-stable#credential-classes
// TokenCredential credential = new ManagedIdentityCredentialBuilder().build();

EventGridPublisherClient<EventGridEvent> client = new EventGridPublisherClientBuilder()
    .endpoint("<topic-endpoint>")
    .credential(credential)
    .buildEventGridEventPublisherClient();
```

### 非同步 Client

```java
import com.azure.messaging.eventgrid.EventGridPublisherAsyncClient;

EventGridPublisherAsyncClient<EventGridEvent> asyncClient = new EventGridPublisherClientBuilder()
    .endpoint("<topic-endpoint>")
    .credential(new AzureKeyCredential("<access-key>"))
    .buildEventGridEventPublisherAsyncClient();
```

## 事件類型

| 類型 | 說明 |
|------|-------------|
| `EventGridEvent` | Azure Event Grid 原生 schema |
| `CloudEvent` | CNCF CloudEvents 1.0 規格 |
| `BinaryData` | 自訂 schema 的事件 |

## 核心模式

### 發佈 EventGridEvent

```java
import com.azure.messaging.eventgrid.EventGridEvent;
import com.azure.core.util.BinaryData;

EventGridEvent event = new EventGridEvent(
    "resource/path",           // subject
    "MyApp.Events.OrderCreated", // eventType
    BinaryData.fromObject(new OrderData("order-123", 99.99)), // data
    "1.0"                      // dataVersion
);

client.sendEvent(event);
```

### 發佈多個事件

```java
List<EventGridEvent> events = Arrays.asList(
    new EventGridEvent("orders/1", "Order.Created", 
        BinaryData.fromObject(order1), "1.0"),
    new EventGridEvent("orders/2", "Order.Created", 
        BinaryData.fromObject(order2), "1.0")
);

client.sendEvents(events);
```

### 發佈 CloudEvent

```java
import com.azure.core.models.CloudEvent;
import com.azure.core.models.CloudEventDataFormat;

CloudEvent cloudEvent = new CloudEvent(
    "/myapp/orders",           // source
    "order.created",           // type
    BinaryData.fromObject(orderData), // data
    CloudEventDataFormat.JSON  // dataFormat
);
cloudEvent.setSubject("orders/12345");
cloudEvent.setId(UUID.randomUUID().toString());

cloudClient.sendEvent(cloudEvent);
```

### 批次發佈 CloudEvent

```java
List<CloudEvent> cloudEvents = Arrays.asList(
    new CloudEvent("/app", "event.type1", BinaryData.fromString("data1"), CloudEventDataFormat.JSON),
    new CloudEvent("/app", "event.type2", BinaryData.fromString("data2"), CloudEventDataFormat.JSON)
);

cloudClient.sendEvents(cloudEvents);
```

### 非同步發佈

```java
asyncClient.sendEvent(event)
    .subscribe(
        unused -> System.out.println("Event sent successfully"),
        error -> System.err.println("Error: " + error.getMessage())
    );

// 多個事件
asyncClient.sendEvents(events)
    .doOnSuccess(unused -> System.out.println("All events sent"))
    .doOnError(error -> System.err.println("Failed: " + error))
    .block(); // 需要的話才 block
```

### 自訂事件資料類別

```java
public class OrderData {
    private String orderId;
    private double amount;
    private String customerId;
    
    public OrderData(String orderId, double amount) {
        this.orderId = orderId;
        this.amount = amount;
    }
    
    // Getter 和 setter
}

// 用法
OrderData order = new OrderData("ORD-123", 150.00);
EventGridEvent event = new EventGridEvent(
    "orders/" + order.getOrderId(),
    "MyApp.Order.Created",
    BinaryData.fromObject(order),
    "1.0"
);
```

## 接收事件

### 解析 EventGridEvent

```java
import com.azure.messaging.eventgrid.EventGridEvent;

// 從 JSON 字串（例如 webhook 的 payload）
String jsonPayload = "[{\"id\": \"...\", ...}]";
List<EventGridEvent> events = EventGridEvent.fromString(jsonPayload);

for (EventGridEvent event : events) {
    System.out.println("Event Type: " + event.getEventType());
    System.out.println("Subject: " + event.getSubject());
    System.out.println("Event Time: " + event.getEventTime());
    
    // 取得資料
    BinaryData data = event.getData();
    OrderData orderData = data.toObject(OrderData.class);
}
```

### 解析 CloudEvent

```java
import com.azure.core.models.CloudEvent;

String cloudEventJson = "[{\"specversion\": \"1.0\", ...}]";
List<CloudEvent> cloudEvents = CloudEvent.fromString(cloudEventJson);

for (CloudEvent event : cloudEvents) {
    System.out.println("Type: " + event.getType());
    System.out.println("Source: " + event.getSource());
    System.out.println("ID: " + event.getId());
    
    MyEventData data = event.getData().toObject(MyEventData.class);
}
```

### 處理系統事件

```java
import com.azure.messaging.eventgrid.systemevents.*;

for (EventGridEvent event : events) {
    if (event.getEventType().equals("Microsoft.Storage.BlobCreated")) {
        StorageBlobCreatedEventData blobData = 
            event.getData().toObject(StorageBlobCreatedEventData.class);
        System.out.println("Blob URL: " + blobData.getUrl());
    }
}
```

## Event Grid Namespace（MQTT/Pull）

### 從 Namespace Topic 接收

```java
import com.azure.messaging.eventgrid.namespaces.EventGridReceiverClient;
import com.azure.messaging.eventgrid.namespaces.EventGridReceiverClientBuilder;
import com.azure.messaging.eventgrid.namespaces.models.*;

EventGridReceiverClient receiverClient = new EventGridReceiverClientBuilder()
    .endpoint("<namespace-endpoint>")
    .credential(new AzureKeyCredential("<key>"))
    .topicName("my-topic")
    .subscriptionName("my-subscription")
    .buildClient();

// 接收事件
ReceiveResult result = receiverClient.receive(10, Duration.ofSeconds(30));

for (ReceiveDetails detail : result.getValue()) {
    CloudEvent event = detail.getEvent();
    System.out.println("Event: " + event.getType());
    
    // Acknowledge 這個事件
    receiverClient.acknowledge(Arrays.asList(detail.getBrokerProperties().getLockToken()));
}
```

### 拒絕或釋放事件

```java
// Reject（不重試）
receiverClient.reject(Arrays.asList(lockToken));

// Release（稍後重試）
receiverClient.release(Arrays.asList(lockToken));

// 延遲後 release
receiverClient.release(Arrays.asList(lockToken), 
    new ReleaseOptions().setDelay(ReleaseDelay.BY_60_SECONDS));
```

## 錯誤處理

```java
import com.azure.core.exception.HttpResponseException;

try {
    client.sendEvent(event);
} catch (HttpResponseException e) {
    System.out.println("Status: " + e.getResponse().getStatusCode());
    System.out.println("Error: " + e.getMessage());
}
```

## 環境變數

```bash
EVENT_GRID_TOPIC_ENDPOINT=https://<topic-name>.<region>.eventgrid.azure.net/api/events  # 所有驗證方式都必須設定
EVENT_GRID_ACCESS_KEY=<your-access-key>  # 只有用 AzureKeyCredential 驗證時才需要
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境使用 DefaultAzureCredential 時才需要
```

## 最佳實務

1. **批次事件**：可以的話，一次呼叫送多個事件
2. **冪等性**：帶上唯一的事件 ID 以便去重
3. **Schema 驗證**：用強型別的事件資料類別
4. **重試邏輯**：SDK 有內建，但失敗的事件還是要考慮 dead-letter
5. **事件大小**：事件保持在 1MB 以下（basic tier 是 64KB）

## 觸發詞

- "Event Grid Java"
- "publish events Azure"
- "CloudEvent SDK"
- "event-driven messaging"
- "pub/sub Azure"
- "webhook events"
