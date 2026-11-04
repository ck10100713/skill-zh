---
name: azure-communication-chat-java
description: 用 Azure Communication Services Chat Java SDK 建構即時聊天應用程式。適用於實作聊天 thread、訊息、參與者、已讀回條、輸入中通知，或即時聊天功能。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: com.azure:azure-communication-chat
---

# Azure Communication Chat (Java)

建構即時聊天應用程式，包含 thread 管理、訊息、參與者和已讀回條。

## Installation

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-communication-chat</artifactId>
    <version>1.6.0</version>
</dependency>
```

## Client Creation

```java
import com.azure.communication.chat.ChatClient;
import com.azure.communication.chat.ChatClientBuilder;
import com.azure.communication.chat.ChatThreadClient;
import com.azure.communication.common.CommunicationTokenCredential;

// ChatClient 需要 CommunicationTokenCredential（使用者 access token）
String endpoint = "https://<resource>.communication.azure.com";
String userAccessToken = "<user-access-token>";

CommunicationTokenCredential credential = new CommunicationTokenCredential(userAccessToken);

ChatClient chatClient = new ChatClientBuilder()
    .endpoint(endpoint)
    .credential(credential)
    .buildClient();

// 非同步 client
ChatAsyncClient chatAsyncClient = new ChatClientBuilder()
    .endpoint(endpoint)
    .credential(credential)
    .buildAsyncClient();
```

## Key Concepts

| Class | Purpose |
|-------|---------|
| `ChatClient` | 建立/刪除聊天 thread，取得 thread client |
| `ChatThreadClient` | thread 內的操作（訊息、參與者、回條） |
| `ChatParticipant` | 聊天 thread 裡帶有顯示名稱的使用者 |
| `ChatMessage` | 訊息內容、類型、發送者資訊、時間戳記 |
| `ChatMessageReadReceipt` | 每個參與者的已讀回條追蹤 |

## Create Chat Thread

```java
import com.azure.communication.chat.models.*;
import com.azure.communication.common.CommunicationUserIdentifier;
import java.util.ArrayList;
import java.util.List;

// 定義參與者
List<ChatParticipant> participants = new ArrayList<>();

ChatParticipant participant1 = new ChatParticipant()
    .setCommunicationIdentifier(new CommunicationUserIdentifier("<user-id-1>"))
    .setDisplayName("Alice");

ChatParticipant participant2 = new ChatParticipant()
    .setCommunicationIdentifier(new CommunicationUserIdentifier("<user-id-2>"))
    .setDisplayName("Bob");

participants.add(participant1);
participants.add(participant2);

// 建立 thread
CreateChatThreadOptions options = new CreateChatThreadOptions("Project Discussion")
    .setParticipants(participants);

CreateChatThreadResult result = chatClient.createChatThread(options);
String threadId = result.getChatThread().getId();

// 取得 thread client 來做操作
ChatThreadClient threadClient = chatClient.getChatThreadClient(threadId);
```

## Send Messages

```java
// 送出文字訊息
SendChatMessageOptions messageOptions = new SendChatMessageOptions()
    .setContent("Hello, team!")
    .setSenderDisplayName("Alice")
    .setType(ChatMessageType.TEXT);

SendChatMessageResult sendResult = threadClient.sendMessage(messageOptions);
String messageId = sendResult.getId();

// 送出 HTML 訊息
SendChatMessageOptions htmlOptions = new SendChatMessageOptions()
    .setContent("<strong>Important:</strong> Meeting at 3pm")
    .setType(ChatMessageType.HTML);

threadClient.sendMessage(htmlOptions);
```

## Get Messages

```java
import com.azure.core.util.paging.PagedIterable;

// 列出所有訊息
PagedIterable<ChatMessage> messages = threadClient.listMessages();

for (ChatMessage message : messages) {
    System.out.println("ID: " + message.getId());
    System.out.println("Type: " + message.getType());
    System.out.println("Content: " + message.getContent().getMessage());
    System.out.println("Sender: " + message.getSenderDisplayName());
    System.out.println("Created: " + message.getCreatedOn());
    
    // 檢查是否被編輯或刪除
    if (message.getEditedOn() != null) {
        System.out.println("Edited: " + message.getEditedOn());
    }
    if (message.getDeletedOn() != null) {
        System.out.println("Deleted: " + message.getDeletedOn());
    }
}

// 取得特定訊息
ChatMessage message = threadClient.getMessage(messageId);
```

## Update and Delete Messages

```java
// 更新訊息
UpdateChatMessageOptions updateOptions = new UpdateChatMessageOptions()
    .setContent("Updated message content");

threadClient.updateMessage(messageId, updateOptions);

// 刪除訊息
threadClient.deleteMessage(messageId);
```

## Manage Participants

```java
// 列出參與者
PagedIterable<ChatParticipant> participants = threadClient.listParticipants();

for (ChatParticipant participant : participants) {
    CommunicationUserIdentifier user = 
        (CommunicationUserIdentifier) participant.getCommunicationIdentifier();
    System.out.println("User: " + user.getId());
    System.out.println("Display Name: " + participant.getDisplayName());
}

// 新增參與者
List<ChatParticipant> newParticipants = new ArrayList<>();
newParticipants.add(new ChatParticipant()
    .setCommunicationIdentifier(new CommunicationUserIdentifier("<new-user-id>"))
    .setDisplayName("Charlie")
    .setShareHistoryTime(OffsetDateTime.now().minusDays(7))); // 分享最近 7 天

threadClient.addParticipants(newParticipants);

// 移除參與者
CommunicationUserIdentifier userToRemove = new CommunicationUserIdentifier("<user-id>");
threadClient.removeParticipant(userToRemove);
```

## Read Receipts

```java
// 送出已讀回條
threadClient.sendReadReceipt(messageId);

// 取得已讀回條
PagedIterable<ChatMessageReadReceipt> receipts = threadClient.listReadReceipts();

for (ChatMessageReadReceipt receipt : receipts) {
    System.out.println("Message ID: " + receipt.getChatMessageId());
    System.out.println("Read by: " + receipt.getSenderCommunicationIdentifier());
    System.out.println("Read at: " + receipt.getReadOn());
}
```

## Typing Notifications

```java
import com.azure.communication.chat.models.TypingNotificationOptions;

// 送出輸入中通知
TypingNotificationOptions typingOptions = new TypingNotificationOptions()
    .setSenderDisplayName("Alice");

threadClient.sendTypingNotificationWithResponse(typingOptions, Context.NONE);

// 簡單的輸入中通知
threadClient.sendTypingNotification();
```

## Thread Operations

```java
// 取得 thread 屬性
ChatThreadProperties properties = threadClient.getProperties();
System.out.println("Topic: " + properties.getTopic());
System.out.println("Created: " + properties.getCreatedOn());

// 更新主題
threadClient.updateTopic("New Project Discussion Topic");

// 刪除 thread
chatClient.deleteChatThread(threadId);
```

## List Threads

```java
// 列出使用者所有的聊天 thread
PagedIterable<ChatThreadItem> threads = chatClient.listChatThreads();

for (ChatThreadItem thread : threads) {
    System.out.println("Thread ID: " + thread.getId());
    System.out.println("Topic: " + thread.getTopic());
    System.out.println("Last message: " + thread.getLastMessageReceivedOn());
}
```

## Pagination

```java
import com.azure.core.http.rest.PagedResponse;

// 分頁瀏覽訊息
int maxPageSize = 10;
ListChatMessagesOptions listOptions = new ListChatMessagesOptions()
    .setMaxPageSize(maxPageSize);

PagedIterable<ChatMessage> pagedMessages = threadClient.listMessages(listOptions);

pagedMessages.iterableByPage().forEach(page -> {
    System.out.println("Page status code: " + page.getStatusCode());
    page.getElements().forEach(msg -> 
        System.out.println("Message: " + msg.getContent().getMessage()));
});
```

## Error Handling

```java
import com.azure.core.exception.HttpResponseException;

try {
    threadClient.sendMessage(messageOptions);
} catch (HttpResponseException e) {
    switch (e.getResponse().getStatusCode()) {
        case 401:
            System.out.println("Unauthorized - check token");
            break;
        case 403:
            System.out.println("Forbidden - user not in thread");
            break;
        case 404:
            System.out.println("Thread not found");
            break;
        default:
            System.out.println("Error: " + e.getMessage());
    }
}
```

## Message Types

| Type | Description |
|------|-------------|
| `TEXT` | 一般聊天訊息 |
| `HTML` | HTML 格式的訊息 |
| `TOPIC_UPDATED` | 系統訊息：主題已變更 |
| `PARTICIPANT_ADDED` | 系統訊息：有參與者加入 |
| `PARTICIPANT_REMOVED` | 系統訊息：有參與者離開 |

## Environment Variables

```bash
AZURE_COMMUNICATION_ENDPOINT=https://<resource>.communication.azure.com
AZURE_COMMUNICATION_USER_TOKEN=<user-access-token>
```

## Best Practices

1. **Token 管理**：使用者 token 會過期，要用 `CommunicationTokenRefreshOptions` 實作更新邏輯
2. **分頁**：對大型 thread，用帶有 `maxPageSize` 的 `listMessages(options)`
3. **分享歷史**：新增參與者時設定 `shareHistoryTime`，控制訊息的可見範圍
4. **訊息類型**：把系統訊息（`PARTICIPANT_ADDED` 等）和使用者訊息分開過濾
5. **已讀回條**：只有在使用者真的看過訊息時才送回條

## Trigger Phrases

- "chat application Java", "real-time messaging Java"
- "chat thread", "chat participants", "chat messages"
- "read receipts", "typing notifications"
- "Azure Communication Services chat"
