---
name: azure-storage-queue-ts
description: |
  用於訊息 queue 操作的 Azure Queue Storage JavaScript/TypeScript SDK（@azure/storage-queue）。用於在 queue 中傳送、接收、peek 和刪除訊息。支援 visibility timeout、訊息編碼和批次操作。Triggers: "queue storage", "@azure/storage-queue", "QueueServiceClient", "QueueClient", "send message", "receive message", "dequeue", "visibility timeout".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: '@azure/storage-queue'
---

# @azure/storage-queue (TypeScript/JavaScript)

Azure Queue Storage 操作的 SDK，可在 queue 中傳送、接收、peek 並管理訊息。

## 安裝

```bash
npm install @azure/storage-queue @azure/identity
```

**目前版本**：12.x  
**Node.js**：>= 18.0.0

## 環境變數

```bash
AZURE_STORAGE_ACCOUNT_NAME=<account-name>
AZURE_STORAGE_ACCOUNT_KEY=<account-key>
# 或用 connection string
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
AZURE_TOKEN_CREDENTIALS=prod # 只有在 production 使用 DefaultAzureCredential 時才需要
```

## 驗證

### Microsoft Entra Token Credential（建議）

```typescript
import { QueueServiceClient } from "@azure/storage-queue";
import { DefaultAzureCredential, ManagedIdentityCredential } from "@azure/identity";

// 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
const credential = new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]});
// 或在 production 直接用特定的 credential：
// See https://learn.microsoft.com/javascript/api/overview/azure/identity-readme?view=azure-node-latest#credential-classes
// const credential = new ManagedIdentityCredential();

const accountName = process.env.AZURE_STORAGE_ACCOUNT_NAME!;
const client = new QueueServiceClient(
  `https://${accountName}.queue.core.windows.net`,
  credential
);
```

### Connection String

```typescript
import { QueueServiceClient } from "@azure/storage-queue";

const client = QueueServiceClient.fromConnectionString(
  process.env.AZURE_STORAGE_CONNECTION_STRING!
);
```

### StorageSharedKeyCredential（僅限 Node.js）

```typescript
import { QueueServiceClient, StorageSharedKeyCredential } from "@azure/storage-queue";

const accountName = process.env.AZURE_STORAGE_ACCOUNT_NAME!;
const accountKey = process.env.AZURE_STORAGE_ACCOUNT_KEY!;

const sharedKeyCredential = new StorageSharedKeyCredential(accountName, accountKey);
const client = new QueueServiceClient(
  `https://${accountName}.queue.core.windows.net`,
  sharedKeyCredential
);
```

### SAS Token

```typescript
import { QueueServiceClient } from "@azure/storage-queue";

const accountName = process.env.AZURE_STORAGE_ACCOUNT_NAME!;
const sasToken = process.env.AZURE_STORAGE_SAS_TOKEN!;

const client = new QueueServiceClient(
  `https://${accountName}.queue.core.windows.net${sasToken}`
);
```

## Client 階層

```
QueueServiceClient (account level)
└── QueueClient (queue level)
    └── Messages (send, receive, peek, delete)
```

## Queue 操作

### 建立 Queue

```typescript
const queueClient = client.getQueueClient("my-queue");
await queueClient.create();

// 或不存在才建立
await queueClient.createIfNotExists();
```

### 列出 Queue

```typescript
for await (const queue of client.listQueues()) {
  console.log(queue.name);
}

// 用 prefix 篩選
for await (const queue of client.listQueues({ prefix: "task-" })) {
  console.log(queue.name);
}
```

### 刪除 Queue

```typescript
await queueClient.delete();

// 或存在才刪除
await queueClient.deleteIfExists();
```

### 取得 Queue 屬性

```typescript
const properties = await queueClient.getProperties();
console.log("Approximate message count:", properties.approximateMessagesCount);
console.log("Metadata:", properties.metadata);
```

### 設定 Queue Metadata

```typescript
await queueClient.setMetadata({
  department: "engineering",
  priority: "high",
});
```

## 訊息操作

### 傳送訊息

```typescript
const queueClient = client.getQueueClient("my-queue");

// 簡單訊息
await queueClient.sendMessage("Hello, World!");

// 帶選項
await queueClient.sendMessage("Delayed message", {
  visibilityTimeout: 60, // 隱藏 60 秒
  messageTimeToLive: 3600, // 1 小時後過期
});

// JSON 訊息（必須是字串）
const task = { type: "process", data: { id: 123 } };
await queueClient.sendMessage(JSON.stringify(task));
```

### 接收訊息

```typescript
// 最多接收 32 則訊息（預設：1）
const response = await queueClient.receiveMessages({
  numberOfMessages: 10,
  visibilityTimeout: 30, // 30 秒內處理完
});

for (const message of response.receivedMessageItems) {
  console.log("Message ID:", message.messageId);
  console.log("Content:", message.messageText);
  console.log("Dequeue Count:", message.dequeueCount);
  console.log("Pop Receipt:", message.popReceipt);
  
  // 處理訊息...
  
  // 處理完後刪除
  await queueClient.deleteMessage(message.messageId, message.popReceipt);
}
```

### Peek 訊息

Peek 但不從 queue 移除（沒有 visibility timeout）。

```typescript
const response = await queueClient.peekMessages({
  numberOfMessages: 5,
});

for (const message of response.peekedMessageItems) {
  console.log("Message ID:", message.messageId);
  console.log("Content:", message.messageText);
  // 注意：沒有 popReceipt，peek 到的訊息不能刪除
}
```

### 更新訊息

延長 visibility timeout 或更新內容。

```typescript
// 接收一則訊息
const response = await queueClient.receiveMessages();
const message = response.receivedMessageItems[0];

if (message) {
  // 更新內容並延長可見時間
  const updateResponse = await queueClient.updateMessage(
    message.messageId,
    message.popReceipt,
    "Updated content",
    60 // 新的 visibility timeout（秒）
  );
  
  // 後續操作要用新的 popReceipt
  console.log("New pop receipt:", updateResponse.popReceipt);
}
```

### 刪除訊息

```typescript
// 接收之後
const response = await queueClient.receiveMessages();
const message = response.receivedMessageItems[0];

if (message) {
  await queueClient.deleteMessage(message.messageId, message.popReceipt);
}
```

### 清除所有訊息

```typescript
await queueClient.clearMessages();
```

## 訊息處理模式

### 基本 Worker 模式

```typescript
async function processQueue(queueClient: QueueClient): Promise<void> {
  while (true) {
    const response = await queueClient.receiveMessages({
      numberOfMessages: 10,
      visibilityTimeout: 30,
    });

    if (response.receivedMessageItems.length === 0) {
      // 沒有訊息，等一下再輪詢
      await sleep(5000);
      continue;
    }

    for (const message of response.receivedMessageItems) {
      try {
        await processMessage(message.messageText);
        await queueClient.deleteMessage(message.messageId, message.popReceipt);
      } catch (error) {
        console.error(`Failed to process message ${message.messageId}:`, error);
        // 逾時後訊息會再變成可見
      }
    }
  }
}

async function processMessage(content: string): Promise<void> {
  const task = JSON.parse(content);
  // 處理 task...
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
```

### Poison Message 處理

```typescript
const MAX_DEQUEUE_COUNT = 5;

async function processWithPoisonHandling(
  queueClient: QueueClient,
  poisonQueueClient: QueueClient
): Promise<void> {
  const response = await queueClient.receiveMessages({
    numberOfMessages: 10,
    visibilityTimeout: 30,
  });

  for (const message of response.receivedMessageItems) {
    if (message.dequeueCount > MAX_DEQUEUE_COUNT) {
      // 移到 poison queue
      await poisonQueueClient.sendMessage(message.messageText);
      await queueClient.deleteMessage(message.messageId, message.popReceipt);
      console.log(`Moved message ${message.messageId} to poison queue`);
      continue;
    }

    try {
      await processMessage(message.messageText);
      await queueClient.deleteMessage(message.messageId, message.popReceipt);
    } catch (error) {
      console.error(`Processing failed (attempt ${message.dequeueCount}):`, error);
    }
  }
}
```

### 搭配 Visibility 延長的批次處理

```typescript
async function processBatchWithExtension(queueClient: QueueClient): Promise<void> {
  const response = await queueClient.receiveMessages({
    numberOfMessages: 1,
    visibilityTimeout: 60,
  });

  const message = response.receivedMessageItems[0];
  if (!message) return;

  let popReceipt = message.popReceipt;

  // 啟動 visibility 延長計時器
  const extensionInterval = setInterval(async () => {
    try {
      const updateResponse = await queueClient.updateMessage(
        message.messageId,
        popReceipt,
        message.messageText,
        60 // 再延長 60 秒
      );
      popReceipt = updateResponse.popReceipt;
    } catch (error) {
      console.error("Failed to extend visibility:", error);
    }
  }, 45000); // 每 45 秒延長一次

  try {
    await longRunningProcess(message.messageText);
    await queueClient.deleteMessage(message.messageId, popReceipt);
  } finally {
    clearInterval(extensionInterval);
  }
}
```

## 訊息編碼

預設情況下，訊息會用 Base64 編碼。你可以自訂：

```typescript
import { QueueClient } from "@azure/storage-queue";

// 純文字的自訂 encoder/decoder
const queueClient = new QueueClient(
  `https://${accountName}.queue.core.windows.net/my-queue`,
  credential,
  {
    messageEncoding: "text", // "base64"（預設）或 "text"
  }
);

// 或用自訂 encoder
const customQueueClient = new QueueClient(
  `https://${accountName}.queue.core.windows.net/my-queue`,
  credential,
  {
    messageEncoding: {
      encode: (message: string) => Buffer.from(message).toString("base64"),
      decode: (message: string) => Buffer.from(message, "base64").toString(),
    },
  }
);
```

## 產生 SAS Token（僅限 Node.js）

### 產生 Queue SAS

```typescript
import {
  QueueSASPermissions,
  generateQueueSASQueryParameters,
  StorageSharedKeyCredential,
} from "@azure/storage-queue";

const sharedKeyCredential = new StorageSharedKeyCredential(accountName, accountKey);

const sasToken = generateQueueSASQueryParameters(
  {
    queueName: "my-queue",
    permissions: QueueSASPermissions.parse("raup"), // read, add, update, process
    startsOn: new Date(),
    expiresOn: new Date(Date.now() + 3600 * 1000), // 1 小時
  },
  sharedKeyCredential
).toString();

const sasUrl = `https://${accountName}.queue.core.windows.net/my-queue?${sasToken}`;
```

### 產生 Account SAS

```typescript
import {
  AccountSASPermissions,
  AccountSASResourceTypes,
  AccountSASServices,
  generateAccountSASQueryParameters,
} from "@azure/storage-queue";

const sasToken = generateAccountSASQueryParameters(
  {
    services: AccountSASServices.parse("q").toString(), // queue
    resourceTypes: AccountSASResourceTypes.parse("sco").toString(),
    permissions: AccountSASPermissions.parse("rwdlacupi"),
    expiresOn: new Date(Date.now() + 24 * 3600 * 1000),
  },
  sharedKeyCredential
).toString();
```

## 錯誤處理

```typescript
import { RestError } from "@azure/storage-queue";

try {
  await queueClient.sendMessage("test");
} catch (error) {
  if (error instanceof RestError) {
    switch (error.statusCode) {
      case 404:
        console.log("Queue not found");
        break;
      case 400:
        console.log("Bad request - message too large or invalid");
        break;
      case 403:
        console.log("Access denied");
        break;
      case 409:
        console.log("Queue already exists or being deleted");
        break;
      default:
        console.error(`Storage error ${error.statusCode}: ${error.message}`);
    }
  }
  throw error;
}
```

## TypeScript 型別參考

```typescript
import {
  // Clients
  QueueServiceClient,
  QueueClient,

  // Authentication
  StorageSharedKeyCredential,
  AnonymousCredential,

  // SAS
  QueueSASPermissions,
  AccountSASPermissions,
  AccountSASServices,
  AccountSASResourceTypes,
  generateQueueSASQueryParameters,
  generateAccountSASQueryParameters,

  // Messages
  DequeuedMessageItem,
  PeekedMessageItem,
  QueueSendMessageResponse,
  QueueReceiveMessageResponse,
  QueueUpdateMessageResponse,

  // Queue
  QueueItem,
  QueueGetPropertiesResponse,

  // Errors
  RestError,
} from "@azure/storage-queue";
```

## 訊息限制

| 限制 | 值 |
|-------|-------|
| 訊息大小上限 | 64 KB |
| Visibility timeout 上限 | 7 天 |
| Time-to-live 上限 | 7 天（或 -1 代表無限期） |
| 每次接收的訊息數上限 | 32 |
| 預設 visibility timeout | 30 秒 |

## 最佳實務

1. **本機開發用 `DefaultAzureCredential`；production 用 `ManagedIdentityCredential` 或 `WorkloadIdentityCredential`**
2. **處理完一定要刪除** — 避免重複處理
3. **處理 poison message** — 把失敗的訊息移到 dead-letter queue
4. **用適當的 visibility timeout** — 依預期的處理時間設定
5. **長時間任務要延長 visibility** — 更新訊息，避免逾時
6. **結構化資料用 JSON** — 把物件序列化成 JSON 字串
7. **檢查 dequeueCount** — 偵測一再失敗的訊息
8. **用批次接收** — 一次接收多則訊息比較有效率

## 平台差異

| 功能 | Node.js | 瀏覽器 |
|---------|---------|---------|
| `StorageSharedKeyCredential` | ✅ | ❌ |
| SAS 產生 | ✅ | ❌ |
| DefaultAzureCredential | ✅ | ❌ |
| Anonymous/SAS 存取 | ✅ | ✅ |
| 所有訊息操作 | ✅ | ✅ |
