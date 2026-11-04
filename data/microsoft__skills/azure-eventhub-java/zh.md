---
name: azure-eventhub-java
description: 用 Java 版 Azure Event Hubs SDK 建立即時串流應用程式。實作事件串流、高吞吐量資料匯入，或建立事件驅動架構時使用。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: com.azure:azure-messaging-eventhubs
---

# Java 版 Azure Event Hubs SDK

用 Java 版 Azure Event Hubs SDK 建立即時串流應用程式。

## 安裝

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-messaging-eventhubs</artifactId>
    <version>5.19.0</version>
</dependency>

<!-- For checkpoint store (production) -->
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-messaging-eventhubs-checkpointstore-blob</artifactId>
    <version>1.20.0</version>
</dependency>
```

## 建立 Client

### EventHubProducerClient

```java
import com.azure.messaging.eventhubs.EventHubProducerClient;
import com.azure.messaging.eventhubs.EventHubClientBuilder;

// 用 connection string
EventHubProducerClient producer = new EventHubClientBuilder()
    .connectionString("<connection-string>", "<event-hub-name>")
    .buildProducerClient();

// 含 EntityPath 的完整 connection string
EventHubProducerClient producer = new EventHubClientBuilder()
    .connectionString("<connection-string-with-entity-path>")
    .buildProducerClient();
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

EventHubProducerClient producer = new EventHubClientBuilder()
    .fullyQualifiedNamespace("<namespace>.servicebus.windows.net")
    .eventHubName("<event-hub-name>")
    .credential(credential)
    .buildProducerClient();
```

### EventHubConsumerClient

```java
import com.azure.messaging.eventhubs.EventHubConsumerClient;

EventHubConsumerClient consumer = new EventHubClientBuilder()
    .connectionString("<connection-string>", "<event-hub-name>")
    .consumerGroup(EventHubClientBuilder.DEFAULT_CONSUMER_GROUP_NAME)
    .buildConsumerClient();
```

### 非同步 Client

```java
import com.azure.messaging.eventhubs.EventHubProducerAsyncClient;
import com.azure.messaging.eventhubs.EventHubConsumerAsyncClient;

EventHubProducerAsyncClient asyncProducer = new EventHubClientBuilder()
    .connectionString("<connection-string>", "<event-hub-name>")
    .buildAsyncProducerClient();

EventHubConsumerAsyncClient asyncConsumer = new EventHubClientBuilder()
    .connectionString("<connection-string>", "<event-hub-name>")
    .consumerGroup("$Default")
    .buildAsyncConsumerClient();
```

## 核心模式

### 送出單一事件

```java
import com.azure.messaging.eventhubs.EventData;

EventData eventData = new EventData("Hello, Event Hubs!");
producer.send(Collections.singletonList(eventData));
```

### 送出事件批次

```java
import com.azure.messaging.eventhubs.EventDataBatch;
import com.azure.messaging.eventhubs.models.CreateBatchOptions;

// 建立批次
EventDataBatch batch = producer.createBatch();

// 加入事件（批次滿了會回傳 false）
for (int i = 0; i < 100; i++) {
    EventData event = new EventData("Event " + i);
    if (!batch.tryAdd(event)) {
        // 批次滿了：先送出，再建新的批次
        producer.send(batch);
        batch = producer.createBatch();
        batch.tryAdd(event);
    }
}

// 送出剩下的事件
if (batch.getCount() > 0) {
    producer.send(batch);
}
```

### 送到特定 Partition

```java
CreateBatchOptions options = new CreateBatchOptions()
    .setPartitionId("0");

EventDataBatch batch = producer.createBatch(options);
batch.tryAdd(new EventData("Partition 0 event"));
producer.send(batch);
```

### 用 Partition Key 送出

```java
CreateBatchOptions options = new CreateBatchOptions()
    .setPartitionKey("customer-123");

EventDataBatch batch = producer.createBatch(options);
batch.tryAdd(new EventData("Customer event"));
producer.send(batch);
```

### 帶屬性的事件

```java
EventData event = new EventData("Order created");
event.getProperties().put("orderId", "ORD-123");
event.getProperties().put("customerId", "CUST-456");
event.getProperties().put("priority", 1);

producer.send(Collections.singletonList(event));
```

### 接收事件（簡單版）

```java
import com.azure.messaging.eventhubs.models.EventPosition;
import com.azure.messaging.eventhubs.models.PartitionEvent;

// 從特定 partition 接收
Iterable<PartitionEvent> events = consumer.receiveFromPartition(
    "0",                           // partitionId
    10,                            // maxEvents
    EventPosition.earliest(),      // startingPosition
    Duration.ofSeconds(30)         // timeout
);

for (PartitionEvent partitionEvent : events) {
    EventData event = partitionEvent.getData();
    System.out.println("Body: " + event.getBodyAsString());
    System.out.println("Sequence: " + event.getSequenceNumber());
    System.out.println("Offset: " + event.getOffset());
}
```

### EventProcessorClient（正式環境）

```java
import com.azure.messaging.eventhubs.EventProcessorClient;
import com.azure.messaging.eventhubs.EventProcessorClientBuilder;
import com.azure.messaging.eventhubs.checkpointstore.blob.BlobCheckpointStore;
import com.azure.storage.blob.BlobContainerAsyncClient;
import com.azure.storage.blob.BlobContainerClientBuilder;

// 建立 checkpoint store
BlobContainerAsyncClient blobClient = new BlobContainerClientBuilder()
    .connectionString("<storage-connection-string>")
    .containerName("checkpoints")
    .buildAsyncClient();

// 建立 processor
EventProcessorClient processor = new EventProcessorClientBuilder()
    .connectionString("<eventhub-connection-string>", "<event-hub-name>")
    .consumerGroup("$Default")
    .checkpointStore(new BlobCheckpointStore(blobClient))
    .processEvent(eventContext -> {
        EventData event = eventContext.getEventData();
        System.out.println("Processing: " + event.getBodyAsString());
        
        // 處理完之後做 checkpoint
        eventContext.updateCheckpoint();
    })
    .processError(errorContext -> {
        System.err.println("Error: " + errorContext.getThrowable().getMessage());
        System.err.println("Partition: " + errorContext.getPartitionContext().getPartitionId());
    })
    .buildEventProcessorClient();

// 開始處理
processor.start();

// 持續執行...
Thread.sleep(Duration.ofMinutes(5).toMillis());

// 優雅停止
processor.stop();
```

### 批次處理

```java
EventProcessorClient processor = new EventProcessorClientBuilder()
    .connectionString("<connection-string>", "<event-hub-name>")
    .consumerGroup("$Default")
    .checkpointStore(new BlobCheckpointStore(blobClient))
    .processEventBatch(eventBatchContext -> {
        List<EventData> events = eventBatchContext.getEvents();
        System.out.printf("Received %d events%n", events.size());
        
        for (EventData event : events) {
            // 處理每個事件
            System.out.println(event.getBodyAsString());
        }
        
        // 批次處理完之後做 checkpoint
        eventBatchContext.updateCheckpoint();
    }, 50) // maxBatchSize
    .processError(errorContext -> {
        System.err.println("Error: " + errorContext.getThrowable());
    })
    .buildEventProcessorClient();
```

### 非同步接收

```java
asyncConsumer.receiveFromPartition("0", EventPosition.latest())
    .subscribe(
        partitionEvent -> {
            EventData event = partitionEvent.getData();
            System.out.println("Received: " + event.getBodyAsString());
        },
        error -> System.err.println("Error: " + error),
        () -> System.out.println("Complete")
    );
```

### 取得 Event Hub 屬性

```java
// 取得 hub 資訊
EventHubProperties hubProps = producer.getEventHubProperties();
System.out.println("Hub: " + hubProps.getName());
System.out.println("Partitions: " + hubProps.getPartitionIds());

// 取得 partition 資訊
PartitionProperties partitionProps = producer.getPartitionProperties("0");
System.out.println("Begin sequence: " + partitionProps.getBeginningSequenceNumber());
System.out.println("Last sequence: " + partitionProps.getLastEnqueuedSequenceNumber());
System.out.println("Last offset: " + partitionProps.getLastEnqueuedOffset());
```

## 事件位置

```java
// 從頭開始
EventPosition.earliest()

// 從尾端開始（只讀新事件）
EventPosition.latest()

// 從特定 offset
EventPosition.fromOffset(12345L)

// 從特定 sequence number
EventPosition.fromSequenceNumber(100L)

// 從特定時間
EventPosition.fromEnqueuedTime(Instant.now().minus(Duration.ofHours(1)))
```

## 錯誤處理

```java
import com.azure.messaging.eventhubs.models.ErrorContext;

.processError(errorContext -> {
    Throwable error = errorContext.getThrowable();
    String partitionId = errorContext.getPartitionContext().getPartitionId();
    
    if (error instanceof AmqpException) {
        AmqpException amqpError = (AmqpException) error;
        if (amqpError.isTransient()) {
            System.out.println("Transient error, will retry");
        }
    }
    
    System.err.printf("Error on partition %s: %s%n", partitionId, error.getMessage());
})
```

## 資源清理

```java
// 一定要關閉 client
try {
    producer.send(batch);
} finally {
    producer.close();
}

// 或用 try-with-resources
try (EventHubProducerClient producer = new EventHubClientBuilder()
        .connectionString(connectionString, eventHubName)
        .buildProducerClient()) {
    producer.send(events);
}
```

## 環境變數

```bash
EVENT_HUBS_CONNECTION_STRING=Endpoint=sb://<namespace>.servicebus.windows.net/;SharedAccessKeyName=...  # Entra ID 驗證的替代方案
EVENT_HUBS_NAME=<event-hub-name>  # Event hub 名稱，必須設定
STORAGE_CONNECTION_STRING=<for-checkpointing>  # checkpoint 用，Entra ID 驗證的替代方案
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境使用 DefaultAzureCredential 時才需要
```

## 最佳實務

1. **用 EventProcessorClient**：正式環境用它，有負載平衡和 checkpoint
2. **批次事件**：用 `EventDataBatch` 才能有效率地送出
3. **Partition Key**：用來保證同一個 partition 內的順序
4. **Checkpoint**：處理完之後再做 checkpoint，避免重複處理
5. **錯誤處理**：暫時性錯誤用重試處理
6. **關閉 Client**：用完 producer/consumer 一定要關

## 觸發詞

- "Event Hubs Java"
- "event streaming Azure"
- "real-time data ingestion"
- "EventProcessorClient"
- "event hub producer consumer"
- "partition processing"
