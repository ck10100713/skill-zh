---
name: azure-eventhub-ts
description: 用 JavaScript 版 Azure Event Hubs SDK（@azure/event-hubs）建立事件串流應用程式。實作高吞吐量事件匯入、即時分析、IoT 遙測，或搭配 partition consumer 的事件驅動架構時使用。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: '@azure/event-hubs'
---

# TypeScript 版 Azure Event Hubs SDK

高吞吐量的事件串流和即時資料匯入。

## 安裝

```bash
npm install @azure/event-hubs @azure/identity
```

要搭配 consumer group 做 checkpoint：
```bash
npm install @azure/eventhubs-checkpointstore-blob @azure/storage-blob
```

## 環境變數

```bash
EVENTHUB_NAMESPACE=<namespace>.servicebus.windows.net
EVENTHUB_NAME=my-eventhub
STORAGE_ACCOUNT_NAME=<storage-account>
STORAGE_CONTAINER_NAME=checkpoints
AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境使用 DefaultAzureCredential 時才需要
```

## 驗證

```typescript
import { EventHubProducerClient, EventHubConsumerClient } from "@azure/event-hubs";
import { DefaultAzureCredential, ManagedIdentityCredential } from "@azure/identity";

const fullyQualifiedNamespace = process.env.EVENTHUB_NAMESPACE!;
const eventHubName = process.env.EVENTHUB_NAME!;
// 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
const credential = new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]});
// 或是在正式環境直接用特定的 credential：
// 參考 https://learn.microsoft.com/javascript/api/overview/azure/identity-readme?view=azure-node-latest#credential-classes
// const credential = new ManagedIdentityCredential();

// Producer
const producer = new EventHubProducerClient(fullyQualifiedNamespace, eventHubName, credential);

// Consumer
const consumer = new EventHubConsumerClient(
  "$Default", // Consumer group
  fullyQualifiedNamespace,
  eventHubName,
  credential
);
```

## 核心流程

### 送出事件

```typescript
const producer = new EventHubProducerClient(namespace, eventHubName, credential);

// 建立批次並加入事件
const batch = await producer.createBatch();
batch.tryAdd({ body: { temperature: 72.5, deviceId: "sensor-1" } });
batch.tryAdd({ body: { temperature: 68.2, deviceId: "sensor-2" } });

await producer.sendBatch(batch);
await producer.close();
```

### 送到特定 Partition

```typescript
// 用 partition ID
const batch = await producer.createBatch({ partitionId: "0" });

// 用 partition key（一致性 hash）
const batch = await producer.createBatch({ partitionKey: "device-123" });
```

### 接收事件（簡單版）

```typescript
const consumer = new EventHubConsumerClient("$Default", namespace, eventHubName, credential);

const subscription = consumer.subscribe({
  processEvents: async (events, context) => {
    for (const event of events) {
      console.log(`Partition: ${context.partitionId}, Body: ${JSON.stringify(event.body)}`);
    }
  },
  processError: async (err, context) => {
    console.error(`Error on partition ${context.partitionId}: ${err.message}`);
  },
});

// 一段時間後停止
setTimeout(async () => {
  await subscription.close();
  await consumer.close();
}, 60000);
```

### 搭配 Checkpoint 接收（正式環境）

```typescript
import { EventHubConsumerClient } from "@azure/event-hubs";
import { ContainerClient } from "@azure/storage-blob";
import { BlobCheckpointStore } from "@azure/eventhubs-checkpointstore-blob";

const containerClient = new ContainerClient(
  `https://${storageAccount}.blob.core.windows.net/${containerName}`,
  credential
);

const checkpointStore = new BlobCheckpointStore(containerClient);

const consumer = new EventHubConsumerClient(
  "$Default",
  namespace,
  eventHubName,
  credential,
  checkpointStore
);

const subscription = consumer.subscribe({
  processEvents: async (events, context) => {
    for (const event of events) {
      console.log(`Processing: ${JSON.stringify(event.body)}`);
    }
    // 處理完一批之後做 checkpoint
    if (events.length > 0) {
      await context.updateCheckpoint(events[events.length - 1]);
    }
  },
  processError: async (err, context) => {
    console.error(`Error: ${err.message}`);
  },
});
```

### 從特定位置接收

```typescript
const subscription = consumer.subscribe({
  processEvents: async (events, context) => { /* ... */ },
  processError: async (err, context) => { /* ... */ },
}, {
  startPosition: {
    // 從頭開始
    "0": { offset: "@earliest" },
    // 從尾端開始（只讀新事件）
    "1": { offset: "@latest" },
    // 從特定 offset 開始
    "2": { offset: "12345" },
    // 從特定時間開始
    "3": { enqueuedOn: new Date("2024-01-01") },
  },
});
```

## Event Hub 屬性

```typescript
// 取得 hub 資訊
const hubProperties = await producer.getEventHubProperties();
console.log(`Partitions: ${hubProperties.partitionIds}`);

// 取得 partition 資訊
const partitionProperties = await producer.getPartitionProperties("0");
console.log(`Last sequence: ${partitionProperties.lastEnqueuedSequenceNumber}`);
```

## 批次處理選項

```typescript
const subscription = consumer.subscribe(
  {
    processEvents: async (events, context) => { /* ... */ },
    processError: async (err, context) => { /* ... */ },
  },
  {
    maxBatchSize: 100,           // 每批最多幾個事件
    maxWaitTimeInSeconds: 30,    // 等待一批的最長時間
  }
);
```

## 主要型別

```typescript
import {
  EventHubProducerClient,
  EventHubConsumerClient,
  EventData,
  ReceivedEventData,
  PartitionContext,
  Subscription,
  SubscriptionEventHandlers,
  CreateBatchOptions,
  EventPosition,
} from "@azure/event-hubs";

import { BlobCheckpointStore } from "@azure/eventhubs-checkpointstore-blob";
```

## 事件屬性

```typescript
// 帶屬性送出
const batch = await producer.createBatch();
batch.tryAdd({
  body: { data: "payload" },
  properties: {
    eventType: "telemetry",
    deviceId: "sensor-1",
  },
  contentType: "application/json",
  correlationId: "request-123",
});

// 在接收端讀取
consumer.subscribe({
  processEvents: async (events, context) => {
    for (const event of events) {
      console.log(`Type: ${event.properties?.eventType}`);
      console.log(`Sequence: ${event.sequenceNumber}`);
      console.log(`Enqueued: ${event.enqueuedTimeUtc}`);
      console.log(`Offset: ${event.offset}`);
    }
  },
});
```

## 錯誤處理

```typescript
consumer.subscribe({
  processEvents: async (events, context) => {
    try {
      for (const event of events) {
        await processEvent(event);
      }
      await context.updateCheckpoint(events[events.length - 1]);
    } catch (error) {
      // 出錯時不要做 checkpoint，事件會被重新處理
      console.error("Processing failed:", error);
    }
  },
  processError: async (err, context) => {
    if (err.name === "MessagingError") {
      // 暫時性錯誤：SDK 會重試
      console.warn("Transient error:", err.message);
    } else {
      // 致命錯誤
      console.error("Fatal error:", err);
    }
  },
});
```

## 最佳實務

1. **用 checkpoint**：正式環境一定要做 checkpoint，才能做到 exactly-once 處理
2. **批次送出**：用 `createBatch()` 才能有效率地送
3. **Partition key**：用 partition key 確保相關事件的順序
4. **Consumer group**：不同的處理 pipeline 用各自獨立的 consumer group
5. **優雅處理錯誤**：處理失敗時不要做 checkpoint
6. **關閉 client**：用完 producer/consumer 一定要關
7. **監控 lag**：追蹤 `lastEnqueuedSequenceNumber` 和已處理的 sequence 的差距
