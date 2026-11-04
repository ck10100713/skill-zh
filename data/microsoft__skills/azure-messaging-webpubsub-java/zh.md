---
name: azure-messaging-webpubsub-java
description: 用 Azure Web PubSub SDK for Java 建立即時 web 應用程式。實作 WebSocket 訊息傳遞、即時更新、聊天應用程式，或伺服器到 client 的推播通知時使用。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: com.azure:azure-messaging-webpubsub
---

# Azure Web PubSub SDK for Java

用 Azure Web PubSub SDK for Java 建立即時 web 應用程式。

## 安裝

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-messaging-webpubsub</artifactId>
    <version>1.5.0</version>
</dependency>
```

## 建立 Client

### 用連線字串

```java
import com.azure.messaging.webpubsub.WebPubSubServiceClient;
import com.azure.messaging.webpubsub.WebPubSubServiceClientBuilder;

WebPubSubServiceClient client = new WebPubSubServiceClientBuilder()
    .connectionString("<connection-string>")
    .hub("chat")
    .buildClient();
```

### 用 Access Key

```java
import com.azure.core.credential.AzureKeyCredential;

WebPubSubServiceClient client = new WebPubSubServiceClientBuilder()
    .credential(new AzureKeyCredential("<access-key>"))
    .endpoint("<endpoint>")
    .hub("chat")
    .buildClient();
```

### 用 DefaultAzureCredential

```java
import com.azure.core.credential.TokenCredential;
import com.azure.identity.AzureIdentityEnvVars;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.identity.ManagedIdentityCredentialBuilder;

// 本機開發：DefaultAzureCredential。正式環境：設 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
TokenCredential credential = new DefaultAzureCredentialBuilder()
    .requireEnvVars(AzureIdentityEnvVars.AZURE_TOKEN_CREDENTIALS)
    .build();
// 或在正式環境直接用特定的 credential：
// 見 https://learn.microsoft.com/java/api/overview/azure/identity-readme?view=azure-java-stable#credential-classes
// TokenCredential credential = new ManagedIdentityCredentialBuilder().build();

WebPubSubServiceClient client = new WebPubSubServiceClientBuilder()
    .credential(credential)
    .endpoint("<endpoint>")
    .hub("chat")
    .buildClient();
```

### 非同步 Client

```java
import com.azure.messaging.webpubsub.WebPubSubServiceAsyncClient;

WebPubSubServiceAsyncClient asyncClient = new WebPubSubServiceClientBuilder()
    .connectionString("<connection-string>")
    .hub("chat")
    .buildAsyncClient();
```

## 核心概念

- **Hub**：連線的邏輯隔離單位
- **Group**：hub 裡連線的子集合
- **Connection**：單一 WebSocket client 連線
- **User**：可以有多個連線的實體

## 核心模式

### 傳送給所有連線

```java
import com.azure.messaging.webpubsub.models.WebPubSubContentType;

// 傳送文字訊息
client.sendToAll("Hello everyone!", WebPubSubContentType.TEXT_PLAIN);

// 傳送 JSON
String jsonMessage = "{\"type\": \"notification\", \"message\": \"New update!\"}";
client.sendToAll(jsonMessage, WebPubSubContentType.APPLICATION_JSON);
```

### 帶過濾條件傳送給所有連線

```java
import com.azure.core.http.rest.RequestOptions;
import com.azure.core.util.BinaryData;

BinaryData message = BinaryData.fromString("Hello filtered users!");

// 依 userId 過濾
client.sendToAllWithResponse(
    message,
    WebPubSubContentType.TEXT_PLAIN,
    message.getLength(),
    new RequestOptions().addQueryParam("filter", "userId ne 'user1'"));

// 依 group 過濾
client.sendToAllWithResponse(
    message,
    WebPubSubContentType.TEXT_PLAIN,
    message.getLength(),
    new RequestOptions().addQueryParam("filter", "'GroupA' in groups and not('GroupB' in groups)"));
```

### 傳送給 Group

```java
// 傳送給 group 裡所有連線
client.sendToGroup("java-developers", "Hello Java devs!", WebPubSubContentType.TEXT_PLAIN);

// 傳送 JSON 給 group
String json = "{\"event\": \"update\", \"data\": {\"version\": \"2.0\"}}";
client.sendToGroup("subscribers", json, WebPubSubContentType.APPLICATION_JSON);
```

### 傳送給特定連線

```java
// 依 ID 傳送給特定連線
client.sendToConnection("connectionId123", "Private message", WebPubSubContentType.TEXT_PLAIN);
```

### 傳送給 User

```java
// 傳送給特定使用者的所有連線
client.sendToUser("andy", "Hello Andy!", WebPubSubContentType.TEXT_PLAIN);
```

### 管理 Group

```java
// 把連線加進 group
client.addConnectionToGroup("premium-users", "connectionId123");

// 把連線移出 group
client.removeConnectionFromGroup("premium-users", "connectionId123");

// 把使用者加進 group（他的所有連線）
client.addUserToGroup("admin-group", "userId456");

// 把使用者移出 group
client.removeUserFromGroup("admin-group", "userId456");

// 檢查使用者是否在 group 裡
boolean exists = client.userExistsInGroup("admin-group", "userId456");
```

### 管理連線

```java
// 檢查連線是否存在
boolean connected = client.connectionExists("connectionId123");

// 關閉連線
client.closeConnection("connectionId123");

// 帶原因關閉
client.closeConnection("connectionId123", "Session expired");

// 檢查使用者是否存在（有任何連線）
boolean userOnline = client.userExists("userId456");

// 關閉使用者的所有連線
client.closeUserConnections("userId456");

// 關閉 group 裡的所有連線
client.closeGroupConnections("inactive-group");
```

### 產生 Client Access Token

```java
import com.azure.messaging.webpubsub.models.GetClientAccessTokenOptions;
import com.azure.messaging.webpubsub.models.WebPubSubClientAccessToken;

// 基本 token
WebPubSubClientAccessToken token = client.getClientAccessToken(
    new GetClientAccessTokenOptions());
System.out.println("URL: " + token.getUrl());

// 帶 user ID
WebPubSubClientAccessToken userToken = client.getClientAccessToken(
    new GetClientAccessTokenOptions().setUserId("user123"));

// 帶角色（權限）
WebPubSubClientAccessToken roleToken = client.getClientAccessToken(
    new GetClientAccessTokenOptions()
        .setUserId("user123")
        .addRole("webpubsub.joinLeaveGroup")
        .addRole("webpubsub.sendToGroup"));

// 帶連線時要加入的 group
WebPubSubClientAccessToken groupToken = client.getClientAccessToken(
    new GetClientAccessTokenOptions()
        .setUserId("user123")
        .addGroup("announcements")
        .addGroup("updates"));

// 自訂到期時間
WebPubSubClientAccessToken expToken = client.getClientAccessToken(
    new GetClientAccessTokenOptions()
        .setUserId("user123")
        .setExpiresAfter(Duration.ofHours(2)));
```

### 授予/撤銷權限

```java
import com.azure.messaging.webpubsub.models.WebPubSubPermission;

// 授予傳送給 group 的權限
client.grantPermission(
    WebPubSubPermission.SEND_TO_GROUP,
    "connectionId123",
    new RequestOptions().addQueryParam("targetName", "chat-room"));

// 撤銷權限
client.revokePermission(
    WebPubSubPermission.SEND_TO_GROUP,
    "connectionId123",
    new RequestOptions().addQueryParam("targetName", "chat-room"));

// 檢查權限
boolean hasPermission = client.checkPermission(
    WebPubSubPermission.SEND_TO_GROUP,
    "connectionId123",
    new RequestOptions().addQueryParam("targetName", "chat-room"));
```

### 非同步操作

```java
asyncClient.sendToAll("Async message!", WebPubSubContentType.TEXT_PLAIN)
    .subscribe(
        unused -> System.out.println("Message sent"),
        error -> System.err.println("Error: " + error.getMessage())
    );

asyncClient.sendToGroup("developers", "Group message", WebPubSubContentType.TEXT_PLAIN)
    .doOnSuccess(v -> System.out.println("Sent to group"))
    .doOnError(e -> System.err.println("Failed: " + e))
    .subscribe();
```

## 錯誤處理

```java
import com.azure.core.exception.HttpResponseException;

try {
    client.sendToConnection("invalid-id", "test", WebPubSubContentType.TEXT_PLAIN);
} catch (HttpResponseException e) {
    System.out.println("Status: " + e.getResponse().getStatusCode());
    System.out.println("Error: " + e.getMessage());
}
```

## 環境變數

```bash
WEB_PUBSUB_CONNECTION_STRING=Endpoint=https://<resource>.webpubsub.azure.com;AccessKey=...  # 可替代 Entra ID 認證
WEB_PUBSUB_ENDPOINT=https://<resource>.webpubsub.azure.com  # 用 AzureKeyCredential 或 TokenCredential 認證時必填
WEB_PUBSUB_ACCESS_KEY=<your-access-key>  # 只有用 AzureKeyCredential 認證時才需要
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境用 DefaultAzureCredential 時才需要
```

## Client 角色

| 角色 | 權限 |
|------|------------|
| `webpubsub.joinLeaveGroup` | 加入/離開任何 group |
| `webpubsub.sendToGroup` | 傳送給任何 group |
| `webpubsub.joinLeaveGroup.<group>` | 加入/離開特定 group |
| `webpubsub.sendToGroup.<group>` | 傳送給特定 group |

## 最佳實務

1. **善用 Group**：把連線組織成 group，做有針對性的訊息傳遞
2. **User ID**：把連線關聯到 user ID，才能做使用者層級的訊息傳遞
3. **Token 到期時間**：設定合適的 token 到期時間，確保安全
4. **角色**：透過角色只授予最少必要的權限
5. **Hub 隔離**：不同的應用程式功能用不同的 hub
6. **連線管理**：清理不活動的連線

## 觸發詞

- "Web PubSub Java"
- "WebSocket messaging Azure"
- "real-time push notifications"
- "server-sent events"
- "chat application backend"
- "live updates broadcasting"
