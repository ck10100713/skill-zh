---
name: azure-web-pubsub-ts
description: 用 Azure Web PubSub 的 JavaScript SDK（@azure/web-pubsub、@azure/web-pubsub-client）建立即時訊息應用程式。實作 WebSocket 即時功能、pub/sub 訊息、群組聊天或即時通知時使用。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: '@azure/web-pubsub, @azure/web-pubsub-client'
---

# Azure Web PubSub SDKs for TypeScript

用 WebSocket 連線加 pub/sub 模式做即時訊息。

## Installation

```bash
# 伺服器端管理
npm install @azure/web-pubsub @azure/identity

# 用戶端即時訊息
npm install @azure/web-pubsub-client

# 事件處理用的 Express middleware
npm install @azure/web-pubsub-express
```

## Environment Variables

```bash
WEBPUBSUB_CONNECTION_STRING=Endpoint=https://<resource>.webpubsub.azure.com;AccessKey=<key>;Version=1.0;
WEBPUBSUB_ENDPOINT=https://<resource>.webpubsub.azure.com
AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境使用 DefaultAzureCredential 時才需要
```

## Server-Side: WebPubSubServiceClient

### Authentication

```typescript
import { WebPubSubServiceClient, AzureKeyCredential } from "@azure/web-pubsub";
import { DefaultAzureCredential, ManagedIdentityCredential } from "@azure/identity";

// 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
const credential = new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]});
// 或是在正式環境直接使用特定的 credential：
// See https://learn.microsoft.com/javascript/api/overview/azure/identity-readme?view=azure-node-latest#credential-classes
// const credential = new ManagedIdentityCredential();

// Connection string
const client = new WebPubSubServiceClient(
  process.env.WEBPUBSUB_CONNECTION_STRING!,
  "chat"  // hub 名稱
);

// Microsoft Entra Token Credential（建議使用）
const client2 = new WebPubSubServiceClient(
  process.env.WEBPUBSUB_ENDPOINT!,
  credential,
  "chat"
);

// AzureKeyCredential
const client3 = new WebPubSubServiceClient(
  process.env.WEBPUBSUB_ENDPOINT!,
  new AzureKeyCredential("<access-key>"),
  "chat"
);
```

### Generate Client Access Token

```typescript
// 基本 token
const token = await client.getClientAccessToken();
console.log(token.url);  // wss://...?access_token=...

// 帶 user ID 的 token
const userToken = await client.getClientAccessToken({
  userId: "user123",
});

// 帶權限的 token
const permToken = await client.getClientAccessToken({
  userId: "user123",
  roles: [
    "webpubsub.joinLeaveGroup",
    "webpubsub.sendToGroup",
    "webpubsub.sendToGroup.chat-room",  // 指定群組
  ],
  groups: ["chat-room"],  // 連線時自動加入
  expirationTimeInMinutes: 60,
});
```

### Send Messages

```typescript
// 廣播給 hub 內所有連線
await client.sendToAll({ message: "Hello everyone!" });
await client.sendToAll("Plain text", { contentType: "text/plain" });

// 傳給特定使用者（該使用者的所有連線）
await client.sendToUser("user123", { message: "Hello!" });

// 傳給特定連線
await client.sendToConnection("connectionId", { data: "Direct message" });

// 加 filter 傳送（OData 語法）
await client.sendToAll({ message: "Filtered" }, {
  filter: "userId ne 'admin'",
});
```

### Group Management

```typescript
const group = client.group("chat-room");

// 把使用者或連線加進群組
await group.addUser("user123");
await group.addConnection("connectionId");

// 從群組移除
await group.removeUser("user123");

// 傳給群組
await group.sendToAll({ message: "Group message" });

// 關閉群組內所有連線
await group.closeAllConnections({ reason: "Maintenance" });
```

### Connection Management

```typescript
// 檢查是否存在
const userExists = await client.userExists("user123");
const connExists = await client.connectionExists("connectionId");

// 關閉連線
await client.closeConnection("connectionId", { reason: "Kicked" });
await client.closeUserConnections("user123");
await client.closeAllConnections();

// 權限
await client.grantPermission("connectionId", "sendToGroup", { targetName: "chat" });
await client.revokePermission("connectionId", "sendToGroup", { targetName: "chat" });
```

## Client-Side: WebPubSubClient

### Connect

```typescript
import { WebPubSubClient } from "@azure/web-pubsub-client";

// 直接給 URL
const client = new WebPubSubClient("<client-access-url>");

// 從 negotiate endpoint 動態取得 URL
const client2 = new WebPubSubClient({
  getClientAccessUrl: async () => {
    const response = await fetch("/negotiate");
    const { url } = await response.json();
    return url;
  },
});

// 一定要在 start 之前註冊 handler
client.on("connected", (e) => {
  console.log(`Connected: ${e.connectionId}`);
});

client.on("group-message", (e) => {
  console.log(`${e.message.group}: ${e.message.data}`);
});

await client.start();
```

### Send Messages

```typescript
// 先加入群組
await client.joinGroup("chat-room");

// 傳給群組
await client.sendToGroup("chat-room", "Hello!", "text");
await client.sendToGroup("chat-room", { type: "message", content: "Hi" }, "json");

// 傳送選項
await client.sendToGroup("chat-room", "Hello", "text", {
  noEcho: true,        // 不要回傳給寄件者
  fireAndForget: true, // 不等 ack
});

// 傳事件給伺服器
await client.sendEvent("userAction", { action: "typing" }, "json");
```

### Event Handlers

```typescript
// 連線生命週期
client.on("connected", (e) => {
  console.log(`Connected: ${e.connectionId}, User: ${e.userId}`);
});

client.on("disconnected", (e) => {
  console.log(`Disconnected: ${e.message}`);
});

client.on("stopped", () => {
  console.log("Client stopped");
});

// 訊息
client.on("group-message", (e) => {
  console.log(`[${e.message.group}] ${e.message.fromUserId}: ${e.message.data}`);
});

client.on("server-message", (e) => {
  console.log(`Server: ${e.message.data}`);
});

// 重新加入失敗
client.on("rejoin-group-failed", (e) => {
  console.log(`Failed to rejoin ${e.group}: ${e.error}`);
});
```

## Express Event Handler

```typescript
import express from "express";
import { WebPubSubEventHandler } from "@azure/web-pubsub-express";

const app = express();

const handler = new WebPubSubEventHandler("chat", {
  path: "/api/webpubsub/hubs/chat/",
  
  // 阻塞式：核准或拒絕連線
  handleConnect: (req, res) => {
    if (!req.claims?.sub) {
      res.fail(401, "Authentication required");
      return;
    }
    res.success({
      userId: req.claims.sub[0],
      groups: ["general"],
      roles: ["webpubsub.sendToGroup"],
    });
  },
  
  // 阻塞式：處理自訂事件
  handleUserEvent: (req, res) => {
    console.log(`Event from ${req.context.userId}:`, req.data);
    res.success(`Received: ${req.data}`, "text");
  },
  
  // 非阻塞式
  onConnected: (req) => {
    console.log(`Client connected: ${req.context.connectionId}`);
  },
  
  onDisconnected: (req) => {
    console.log(`Client disconnected: ${req.context.connectionId}`);
  },
});

app.use(handler.getMiddleware());

// Negotiate endpoint
app.get("/negotiate", async (req, res) => {
  const token = await serviceClient.getClientAccessToken({
    userId: req.user?.id,
  });
  res.json({ url: token.url });
});

app.listen(8080);
```

## Key Types

```typescript
// 伺服器端
import {
  WebPubSubServiceClient,
  WebPubSubGroup,
  GenerateClientTokenOptions,
  HubSendToAllOptions,
} from "@azure/web-pubsub";

// 用戶端
import {
  WebPubSubClient,
  WebPubSubClientOptions,
  OnConnectedArgs,
  OnGroupDataMessageArgs,
} from "@azure/web-pubsub-client";

// Express
import {
  WebPubSubEventHandler,
  ConnectRequest,
  UserEventRequest,
  ConnectResponseHandler,
} from "@azure/web-pubsub-express";
```

## Best Practices

1. **使用 Microsoft Entra Token Credential** - 本機開發用 `DefaultAzureCredential`；正式環境用 `ManagedIdentityCredential` 或 `WorkloadIdentityCredential`
2. **在 start 之前註冊 handler** - 才不會漏掉一開始的事件
3. **用 group 當作頻道** - 依主題或房間整理訊息
4. **處理重新連線** - 用戶端預設會自動重連
5. **在 handleConnect 裡驗證** - 盡早拒絕未授權的連線
6. **使用 noEcho** - 需要時避免訊息回傳給寄件者
