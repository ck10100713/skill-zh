---
name: azure-communication-sms-java
description: 用 Azure Communication Services SMS Java SDK 發送簡訊。適用於實作簡訊通知、警報、OTP 發送、批次簡訊或送達報告。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: com.azure:azure-communication-sms
---

# Azure Communication SMS (Java)

發送簡訊給單一或多個收件人，並附送達回報。

## Installation

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-communication-sms</artifactId>
    <version>1.2.0</version>
</dependency>
```

## Client Creation

```java
import com.azure.communication.sms.SmsClient;
import com.azure.communication.sms.SmsClientBuilder;
import com.azure.core.credential.TokenCredential;
import com.azure.identity.AzureIdentityEnvVars;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.identity.ManagedIdentityCredentialBuilder;

// 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
TokenCredential credential = new DefaultAzureCredentialBuilder()
    .requireEnvVars(AzureIdentityEnvVars.AZURE_TOKEN_CREDENTIALS)
    .build();
// 或在 production 直接用指定的 credential：
// 參考 https://learn.microsoft.com/java/api/overview/azure/identity-readme?view=azure-java-stable#credential-classes
// TokenCredential credential = new ManagedIdentityCredentialBuilder().build();

// 使用 DefaultAzureCredential（建議）
SmsClient smsClient = new SmsClientBuilder()
    .endpoint("https://<resource>.communication.azure.com")
    .credential(credential)
    .buildClient();

// 使用 connection string
SmsClient smsClient = new SmsClientBuilder()
    .connectionString("<connection-string>")
    .buildClient();

// 使用 AzureKeyCredential
import com.azure.core.credential.AzureKeyCredential;

SmsClient smsClient = new SmsClientBuilder()
    .endpoint("https://<resource>.communication.azure.com")
    .credential(new AzureKeyCredential("<access-key>"))
    .buildClient();

// 非同步 client
SmsAsyncClient smsAsyncClient = new SmsClientBuilder()
    .connectionString("<connection-string>")
    .buildAsyncClient();
```

## Send SMS to Single Recipient

```java
import com.azure.communication.sms.models.SmsSendResult;

// 簡單發送
SmsSendResult result = smsClient.send(
    "+14255550100",      // 寄件者（你的 ACS 電話號碼）
    "+14255551234",      // 收件者
    "Your verification code is 123456");

System.out.println("Message ID: " + result.getMessageId());
System.out.println("To: " + result.getTo());
System.out.println("Success: " + result.isSuccessful());

if (!result.isSuccessful()) {
    System.out.println("Error: " + result.getErrorMessage());
    System.out.println("Status: " + result.getHttpStatusCode());
}
```

## Send SMS to Multiple Recipients

```java
import com.azure.communication.sms.models.SmsSendOptions;
import java.util.Arrays;
import java.util.List;

List<String> recipients = Arrays.asList(
    "+14255551111",
    "+14255552222",
    "+14255553333"
);

// 帶 options
SmsSendOptions options = new SmsSendOptions()
    .setDeliveryReportEnabled(true)
    .setTag("marketing-campaign-001");

Iterable<SmsSendResult> results = smsClient.sendWithResponse(
    "+14255550100",      // 寄件者
    recipients,          // 收件者清單
    "Flash sale! 50% off today only.",
    options,
    Context.NONE
).getValue();

for (SmsSendResult result : results) {
    if (result.isSuccessful()) {
        System.out.println("Sent to " + result.getTo() + ": " + result.getMessageId());
    } else {
        System.out.println("Failed to " + result.getTo() + ": " + result.getErrorMessage());
    }
}
```

## Send Options

```java
SmsSendOptions options = new SmsSendOptions();

// 啟用送達報告（透過 Event Grid 送出）
options.setDeliveryReportEnabled(true);

// 加上自訂 tag 供追蹤
options.setTag("order-confirmation-12345");
```

## Response Handling

```java
import com.azure.core.http.rest.Response;

Response<Iterable<SmsSendResult>> response = smsClient.sendWithResponse(
    "+14255550100",
    Arrays.asList("+14255551234"),
    "Hello!",
    new SmsSendOptions().setDeliveryReportEnabled(true),
    Context.NONE
);

// 檢查 HTTP 回應
System.out.println("Status code: " + response.getStatusCode());
System.out.println("Headers: " + response.getHeaders());

// 處理結果
for (SmsSendResult result : response.getValue()) {
    System.out.println("Message ID: " + result.getMessageId());
    System.out.println("Successful: " + result.isSuccessful());
    
    if (!result.isSuccessful()) {
        System.out.println("HTTP Status: " + result.getHttpStatusCode());
        System.out.println("Error: " + result.getErrorMessage());
    }
}
```

## Async Operations

```java
import reactor.core.publisher.Mono;

SmsAsyncClient asyncClient = new SmsClientBuilder()
    .connectionString("<connection-string>")
    .buildAsyncClient();

// 發送單一訊息
asyncClient.send("+14255550100", "+14255551234", "Async message!")
    .subscribe(
        result -> System.out.println("Sent: " + result.getMessageId()),
        error -> System.out.println("Error: " + error.getMessage())
    );

// 帶 options 發給多個收件人
SmsSendOptions options = new SmsSendOptions()
    .setDeliveryReportEnabled(true);

asyncClient.sendWithResponse(
    "+14255550100",
    Arrays.asList("+14255551111", "+14255552222"),
    "Bulk async message",
    options)
    .subscribe(response -> {
        for (SmsSendResult result : response.getValue()) {
            System.out.println("Result: " + result.getTo() + " - " + result.isSuccessful());
        }
    });
```

## Error Handling

```java
import com.azure.core.exception.HttpResponseException;

try {
    SmsSendResult result = smsClient.send(
        "+14255550100",
        "+14255551234",
        "Test message"
    );
    
    // 個別訊息的錯誤不會拋出 exception
    if (!result.isSuccessful()) {
        handleMessageError(result);
    }
    
} catch (HttpResponseException e) {
    // Request 層級的失敗（驗證、網路等）
    System.out.println("Request failed: " + e.getMessage());
    System.out.println("Status: " + e.getResponse().getStatusCode());
} catch (RuntimeException e) {
    System.out.println("Unexpected error: " + e.getMessage());
}

private void handleMessageError(SmsSendResult result) {
    int status = result.getHttpStatusCode();
    String error = result.getErrorMessage();
    
    if (status == 400) {
        System.out.println("Invalid phone number: " + result.getTo());
    } else if (status == 429) {
        System.out.println("Rate limited - retry later");
    } else {
        System.out.println("Error " + status + ": " + error);
    }
}
```

## Delivery Reports

送達報告是透過 Azure Event Grid 發送。要為你的 ACS 資源設定 Event Grid subscription。

```java
// Event Grid webhook handler（在你的 endpoint 裡）
public void handleDeliveryReport(String eventJson) {
    // 解析 Event Grid 事件
    // 事件類型：Microsoft.Communication.SMSDeliveryReportReceived
    
    // 事件資料包含：
    // - messageId：對應 SmsSendResult.getMessageId()
    // - from：寄件者號碼
    // - to：收件者號碼
    // - deliveryStatus："Delivered"、"Failed" 等
    // - deliveryStatusDetails：詳細狀態
    // - receivedTimestamp：收到狀態的時間
    // - tag：你在 SmsSendOptions 設定的自訂 tag
}
```

## SmsSendResult Properties

| Property | Type | Description |
|----------|------|-------------|
| `getMessageId()` | String | 唯一的訊息識別碼 |
| `getTo()` | String | 收件者電話號碼 |
| `isSuccessful()` | boolean | 發送是否成功 |
| `getHttpStatusCode()` | int | 這位收件者的 HTTP 狀態 |
| `getErrorMessage()` | String | 失敗時的錯誤細節 |
| `getRepeatabilityResult()` | RepeatabilityResult | 冪等性結果 |

## Environment Variables

```bash
AZURE_COMMUNICATION_ENDPOINT=https://<resource>.communication.azure.com  # 所有驗證方式都需要
AZURE_COMMUNICATION_CONNECTION_STRING=endpoint=https://...;accesskey=...  # Entra ID 驗證的替代方案
SMS_FROM_NUMBER=+14255550100  # 寄件者電話號碼必填
AZURE_TOKEN_CREDENTIALS=prod  # 只有在 production 使用 DefaultAzureCredential 時才需要
```

## Best Practices

1. **電話號碼格式**：用 E.164 格式：`+[國碼][號碼]`
2. **送達報告**：重要訊息（OTP、警報）要開啟
3. **Tag**：用 tag 把訊息和業務 context 對應起來
4. **錯誤處理**：每位收件人都要個別檢查 `isSuccessful()`
5. **速率限制**：遇到 429 回應要實作帶 backoff 的重試
6. **批次發送**：多個收件人用批次發送（比較有效率）

## Trigger Phrases

- "send SMS Java", "text message Java"
- "SMS notification", "OTP SMS", "bulk SMS"
- "delivery report SMS", "Azure Communication Services SMS"
