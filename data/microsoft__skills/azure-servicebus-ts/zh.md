---
name: azure-servicebus-ts
description: 用 JavaScript 版的 Azure Service Bus SDK（@azure/service-bus）建構訊息應用。用於實作 queue、topic/subscription、訊息 session、dead-letter 處理或企業級訊息模式。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: '@azure/service-bus'
---

# TypeScript 版 Azure Service Bus SDK

用 queue、topic 和 subscription 做企業級訊息服務。

## 安裝

```bash
npm install @azure/service-bus @azure/identity
```

## 環境變數

```bash
SERVICEBUS_NAMESPACE=<namespace>.servicebus.windows.net
SERVICEBUS_QUEUE_NAME=my-queue
SERVICEBUS_TOPIC_NAME=my-topic
SERVICEBUS_SUBSCRIPTION_NAME=my-subscription
AZURE_TOKEN_CREDENTIALS=prod # 只有在 production 使用 DefaultAzureCredential 時才需要
```

## 驗證

```typescript
import { ServiceBusClient } from "@azure/service-bus";
import { DefaultAzureCredential, ManagedIdentityCredential } from "@azure/identity";

// 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
const credential = new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]});
// 或在 production 直接用特定的 credential：
// See https://learn.microsoft.com/javascript/api/overview/azure/identity-readme?view=azure-node-latest#credential-classes
// const credential = new ManagedIdentityCredential();

const fullyQualifiedNamespace = process.env.SERVICEBUS_NAMESPACE!;
const client = new ServiceBusClient(fullyQualifiedNamespace, credential);
```

## 核心工作流程

### 傳送訊息到 Queue

```typescript
const sender = client.createSender("my-queue");

// 單一訊息
await sender.sendMessages({
  body: { orderId: "12345", amount: 99.99 },
  contentType: "application/json",
});

// 批次訊息
const batch = await sender.createMessageBatch();
batch.tryAddMessage({ body: "Message 1" });
batch.tryAddMessage({ body: "Message 2" });
await sender.sendMessages(batch);

await sender.close();
```

### 從 Queue 接收訊息

```typescript
const receiver = client.createReceiver("my-queue");

// 批次接收
const messages = await receiver.receiveMessages(10, { maxWaitTimeInMs: 5000 });
for (const message of messages) {
  console.log(`Received: ${message.body}`);
  await receiver.completeMessage(message);
}

await receiver.close();
```

### 訂閱訊息（事件驅動）

```typescript
const receiver = client.createReceiver("my-queue");

const subscription = receiver.subscribe({
  processMessage: async (message) => {
    console.log(`Processing: ${message.body}`);
    // 成功時訊息會自動 complete
  },
  processError: async (args) => {
    console.error(`Error: ${args.error}`);
  },
});

// 一段時間後停止
setTimeout(async () => {
  await subscription.close();
  await receiver.close();
}, 60000);
```

### Topic 與 Subscription

```typescript
// 傳送到 topic
const topicSender = client.createSender("my-topic");
await topicSender.sendMessages({
  body: { event: "order.created", data: { orderId: "123" } },
  applicationProperties: { eventType: "order.created" },
});

// 從 subscription 接收
const subscriptionReceiver = client.createReceiver("my-topic", "my-subscription");
const messages = await subscriptionReceiver.receiveMessages(10);
```

## 訊息 Session

```typescript
// 傳送 session 訊息
const sender = client.createSender("session-queue");
await sender.sendMessages({
  body: { step: 1, data: "First step" },
  sessionId: "workflow-123",
});

// 接收 session 訊息
const sessionReceiver = await client.acceptSession("session-queue", "workflow-123");
const messages = await sessionReceiver.receiveMessages(10);

// 取得／設定 session state
const state = await sessionReceiver.getSessionState();
await sessionReceiver.setSessionState(Buffer.from(JSON.stringify({ progress: 50 })));

await sessionReceiver.close();
```

## Dead-Letter 處理

```typescript
// 移到 dead-letter
await receiver.deadLetterMessage(message, {
  deadLetterReason: "Validation failed",
  deadLetterErrorDescription: "Missing required field: orderId",
});

// 處理 dead-letter queue
const dlqReceiver = client.createReceiver("my-queue", { subQueueType: "deadLetter" });
const dlqMessages = await dlqReceiver.receiveMessages(10);
for (const msg of dlqMessages) {
  console.log(`DLQ Reason: ${msg.deadLetterReason}`);
  // 重新處理或記錄
  await dlqReceiver.completeMessage(msg);
}
```

## 排程訊息

```typescript
const sender = client.createSender("my-queue");

// 排程在未來傳送
const scheduledTime = new Date(Date.now() + 60000); // 從現在起 1 分鐘後
const sequenceNumber = await sender.scheduleMessages(
  { body: "Delayed message" },
  scheduledTime
);

// 取消排程的訊息
await sender.cancelScheduledMessages(sequenceNumber);
```

## 訊息延後（Deferral）

```typescript
// 延後訊息，稍後再處理
await receiver.deferMessage(message);

// 用 sequence number 接收被延後的訊息
const deferredMessage = await receiver.receiveDeferredMessages(message.sequenceNumber!);
await receiver.completeMessage(deferredMessage[0]);
```

## Peek 訊息（不會移除）

```typescript
const receiver = client.createReceiver("my-queue");

// Peek，不移除訊息
const peekedMessages = await receiver.peekMessages(10);
for (const msg of peekedMessages) {
  console.log(`Peeked: ${msg.body}`);
}
```

## 重要型別

```typescript
import {
  ServiceBusClient,
  ServiceBusSender,
  ServiceBusReceiver,
  ServiceBusSessionReceiver,
  ServiceBusMessage,
  ServiceBusReceivedMessage,
  ProcessMessageCallback,
  ProcessErrorCallback,
} from "@azure/service-bus";
```

## 接收模式

```typescript
// Peek-Lock（預設）- 訊息會被鎖住，直到 complete／abandon
const receiver = client.createReceiver("my-queue", { receiveMode: "peekLock" });
await receiver.completeMessage(message);   // 從 queue 移除
await receiver.abandonMessage(message);    // 放回 queue
await receiver.deferMessage(message);      // 延後處理
await receiver.deadLetterMessage(message); // 移到 DLQ

// Receive-and-Delete - 訊息一接收就立刻移除
const receiver = client.createReceiver("my-queue", { receiveMode: "receiveAndDelete" });
```

## 最佳實務

1. **用 Microsoft Entra Token Credential** - 本機開發用 `DefaultAzureCredential`；production 用 `ManagedIdentityCredential` 或 `WorkloadIdentityCredential`
2. **重複使用 client** - `ServiceBusClient` 只建立一次，讓各個 sender／receiver 共用
3. **關閉資源** - sender／receiver 用完一定要關閉
4. **處理錯誤** - subscription receiver 要實作 `processError` callback
5. **要順序就用 session** - 當同一組訊息的順序很重要時
6. **設定 dead-letter** - DLQ 裡的訊息一定要處理
7. **批次傳送** - 多則訊息用 `createMessageBatch()`

## 參考文件

詳細的模式請看：

- [Queues vs Topics Patterns](references/queues-topics.md) - Queue／topic 模式、session、接收模式、訊息結算
- [Error Handling and Reliability](references/error-handling.md) - ServiceBusError 代碼、DLQ 處理、lock 續期、graceful shutdown
