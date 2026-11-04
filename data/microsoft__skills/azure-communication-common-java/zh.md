---
name: azure-communication-common-java
description: Azure Communication Services 的 Java 共用工具。適用於處理 CommunicationTokenCredential、使用者識別碼、token 更新，或跨 ACS 服務的共用驗證。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: com.azure:azure-communication-common
---

# Azure Communication Common (Java)

Azure Communication Services 的共用驗證工具和資料結構。

## Installation

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-communication-common</artifactId>
    <version>1.4.0</version>
</dependency>
```

## Key Concepts

| Class | Purpose |
|-------|---------|
| `CommunicationTokenCredential` | 向 ACS 服務驗證使用者 |
| `CommunicationTokenRefreshOptions` | 設定自動 token 更新 |
| `CommunicationUserIdentifier` | 識別 ACS 使用者 |
| `PhoneNumberIdentifier` | 識別 PSTN 電話號碼 |
| `MicrosoftTeamsUserIdentifier` | 識別 Teams 使用者 |
| `UnknownIdentifier` | 未知類型的通用識別碼 |

## CommunicationTokenCredential

### Static Token (Short-lived Clients)

```java
import com.azure.communication.common.CommunicationTokenCredential;

// 簡單的靜態 token，不會更新
String userToken = "<user-access-token>";
CommunicationTokenCredential credential = new CommunicationTokenCredential(userToken);

// 搭配 Chat、Calling 等使用
ChatClient chatClient = new ChatClientBuilder()
    .endpoint("https://<resource>.communication.azure.com")
    .credential(credential)
    .buildClient();
```

### Proactive Token Refresh (Long-lived Clients)

```java
import com.azure.communication.common.CommunicationTokenRefreshOptions;
import java.util.concurrent.Callable;

// Token refresher callback：token 快過期時會被呼叫
Callable<String> tokenRefresher = () -> {
    // 呼叫你的 server 取得新的 token
    return fetchNewTokenFromServer();
};

// 啟用主動更新
CommunicationTokenRefreshOptions refreshOptions = new CommunicationTokenRefreshOptions(tokenRefresher)
    .setRefreshProactively(true)      // 在過期前更新
    .setInitialToken(currentToken);    // 選填的初始 token

CommunicationTokenCredential credential = new CommunicationTokenCredential(refreshOptions);
```

### Async Token Refresh

```java
import java.util.concurrent.CompletableFuture;

// 非同步 token 取得器
Callable<String> asyncRefresher = () -> {
    CompletableFuture<String> future = fetchTokenAsync();
    return future.get();  // 阻塞到 token 可用為止
};

CommunicationTokenRefreshOptions options = new CommunicationTokenRefreshOptions(asyncRefresher)
    .setRefreshProactively(true);

CommunicationTokenCredential credential = new CommunicationTokenCredential(options);
```

## Entra ID (Azure AD) Authentication

```java
import com.azure.identity.InteractiveBrowserCredentialBuilder;
import com.azure.communication.common.EntraCommunicationTokenCredentialOptions;
import java.util.Arrays;
import java.util.List;

// 用於 Teams Phone Extensibility
InteractiveBrowserCredential entraCredential = new InteractiveBrowserCredentialBuilder()
    .clientId("<your-client-id>")
    .tenantId("<your-tenant-id>")
    .redirectUrl("<your-redirect-uri>")
    .build();

String resourceEndpoint = "https://<resource>.communication.azure.com";
List<String> scopes = Arrays.asList(
    "https://auth.msft.communication.azure.com/TeamsExtension.ManageCalls"
);

EntraCommunicationTokenCredentialOptions entraOptions = 
    new EntraCommunicationTokenCredentialOptions(entraCredential, resourceEndpoint)
        .setScopes(scopes);

CommunicationTokenCredential credential = new CommunicationTokenCredential(entraOptions);
```

## Communication Identifiers

### CommunicationUserIdentifier

```java
import com.azure.communication.common.CommunicationUserIdentifier;

// 為 ACS 使用者建立識別碼
CommunicationUserIdentifier user = new CommunicationUserIdentifier("8:acs:resource-id_user-id");

// 取得原始 ID
String rawId = user.getId();
```

### PhoneNumberIdentifier

```java
import com.azure.communication.common.PhoneNumberIdentifier;

// E.164 格式的電話號碼
PhoneNumberIdentifier phone = new PhoneNumberIdentifier("+14255551234");

String phoneNumber = phone.getPhoneNumber();  // "+14255551234"
String rawId = phone.getRawId();              // "4:+14255551234"
```

### MicrosoftTeamsUserIdentifier

```java
import com.azure.communication.common.MicrosoftTeamsUserIdentifier;

// Teams 使用者識別碼
MicrosoftTeamsUserIdentifier teamsUser = new MicrosoftTeamsUserIdentifier("<teams-user-id>")
    .setCloudEnvironment(CommunicationCloudEnvironment.PUBLIC);

// 匿名的 Teams 使用者
MicrosoftTeamsUserIdentifier anonymousTeamsUser = new MicrosoftTeamsUserIdentifier("<teams-user-id>")
    .setAnonymous(true);
```

### UnknownIdentifier

```java
import com.azure.communication.common.UnknownIdentifier;

// 用於未知類型的識別碼
UnknownIdentifier unknown = new UnknownIdentifier("some-raw-id");
```

## Identifier Parsing

```java
import com.azure.communication.common.CommunicationIdentifier;
import com.azure.communication.common.CommunicationIdentifierModel;

// 把原始 ID 解析成對應的類型
public CommunicationIdentifier parseIdentifier(String rawId) {
    if (rawId.startsWith("8:acs:")) {
        return new CommunicationUserIdentifier(rawId);
    } else if (rawId.startsWith("4:")) {
        String phone = rawId.substring(2);
        return new PhoneNumberIdentifier(phone);
    } else if (rawId.startsWith("8:orgid:")) {
        String teamsId = rawId.substring(8);
        return new MicrosoftTeamsUserIdentifier(teamsId);
    } else {
        return new UnknownIdentifier(rawId);
    }
}
```

## Type Checking Identifiers

```java
import com.azure.communication.common.CommunicationIdentifier;

public void processIdentifier(CommunicationIdentifier identifier) {
    if (identifier instanceof CommunicationUserIdentifier) {
        CommunicationUserIdentifier user = (CommunicationUserIdentifier) identifier;
        System.out.println("ACS User: " + user.getId());
        
    } else if (identifier instanceof PhoneNumberIdentifier) {
        PhoneNumberIdentifier phone = (PhoneNumberIdentifier) identifier;
        System.out.println("Phone: " + phone.getPhoneNumber());
        
    } else if (identifier instanceof MicrosoftTeamsUserIdentifier) {
        MicrosoftTeamsUserIdentifier teams = (MicrosoftTeamsUserIdentifier) identifier;
        System.out.println("Teams User: " + teams.getUserId());
        System.out.println("Anonymous: " + teams.isAnonymous());
        
    } else if (identifier instanceof UnknownIdentifier) {
        UnknownIdentifier unknown = (UnknownIdentifier) identifier;
        System.out.println("Unknown: " + unknown.getId());
    }
}
```

## Token Access

```java
import com.azure.core.credential.AccessToken;

// 取得目前的 token（用於除錯/log，不要外洩！）
CommunicationTokenCredential credential = new CommunicationTokenCredential(token);

// 同步存取
AccessToken accessToken = credential.getToken();
System.out.println("Token expires: " + accessToken.getExpiresAt());

// 非同步存取
credential.getTokenAsync()
    .subscribe(token -> {
        System.out.println("Token: " + token.getToken().substring(0, 20) + "...");
        System.out.println("Expires: " + token.getExpiresAt());
    });
```

## Dispose Credential

```java
// 用完要清理
credential.close();

// 或用 try-with-resources
try (CommunicationTokenCredential cred = new CommunicationTokenCredential(options)) {
    // 使用 credential
    chatClient.doSomething();
}
```

## Cloud Environments

```java
import com.azure.communication.common.CommunicationCloudEnvironment;

// 可用的環境
CommunicationCloudEnvironment publicCloud = CommunicationCloudEnvironment.PUBLIC;
CommunicationCloudEnvironment govCloud = CommunicationCloudEnvironment.GCCH;
CommunicationCloudEnvironment dodCloud = CommunicationCloudEnvironment.DOD;

// 設定在 Teams 識別碼上
MicrosoftTeamsUserIdentifier teamsUser = new MicrosoftTeamsUserIdentifier("<user-id>")
    .setCloudEnvironment(CommunicationCloudEnvironment.GCCH);
```

## Environment Variables

```bash
AZURE_COMMUNICATION_ENDPOINT=https://<resource>.communication.azure.com
AZURE_COMMUNICATION_USER_TOKEN=<user-access-token>
```

## Best Practices

1. **主動更新**：長時間運作的 client 一定要用 `setRefreshProactively(true)`
2. **Token 安全**：絕對不要 log 或外洩完整的 token
3. **關閉 credential**：不再需要時要釋放 credential
4. **錯誤處理**：好好處理 token 更新失敗
5. **識別碼類型**：用具體的識別碼類型，不要用原始字串

## Common Usage Patterns

```java
// 模式：為 Chat/Calling client 建立 credential
public ChatClient createChatClient(String token, String endpoint) {
    CommunicationTokenRefreshOptions refreshOptions = 
        new CommunicationTokenRefreshOptions(this::refreshToken)
            .setRefreshProactively(true)
            .setInitialToken(token);
    
    CommunicationTokenCredential credential = 
        new CommunicationTokenCredential(refreshOptions);
    
    return new ChatClientBuilder()
        .endpoint(endpoint)
        .credential(credential)
        .buildClient();
}

private String refreshToken() {
    // 呼叫你的 token endpoint
    return tokenService.getNewToken();
}
```

## Trigger Phrases

- "ACS authentication", "communication token credential"
- "user access token", "token refresh"
- "CommunicationUserIdentifier", "PhoneNumberIdentifier"
- "Azure Communication Services authentication"
