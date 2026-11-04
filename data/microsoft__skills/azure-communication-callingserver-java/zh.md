---
name: azure-communication-callingserver-java
description: Azure Communication Services CallingServer（舊版）Java SDK。注意：這個 SDK 已棄用，新專案請改用 azure-communication-callautomation。只有在維護舊版程式碼時才用這個 skill。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: com.azure:azure-communication-callingserver
---

# Azure Communication CallingServer (Java) - DEPRECATED

> **⚠️ DEPRECATED**：這個 SDK 已改名為 **Call Automation**。新專案請改用 `azure-communication-callautomation`。這個 skill 只用來維護舊版程式碼。

## Migration to Call Automation

```xml
<!-- OLD (deprecated) -->
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-communication-callingserver</artifactId>
    <version>1.0.0-beta.5</version>
</dependency>

<!-- NEW (use this instead) -->
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-communication-callautomation</artifactId>
    <version>1.6.0</version>
</dependency>
```

## Class Name Changes

| CallingServer (Old) | Call Automation (New) |
|---------------------|----------------------|
| `CallingServerClient` | `CallAutomationClient` |
| `CallingServerClientBuilder` | `CallAutomationClientBuilder` |
| `CallConnection` | `CallConnection`（相同） |
| `ServerCall` | 已移除，改用 `CallConnection` |

## Legacy Client Creation

```java
// OLD WAY (deprecated)
import com.azure.communication.callingserver.CallingServerClient;
import com.azure.communication.callingserver.CallingServerClientBuilder;

CallingServerClient client = new CallingServerClientBuilder()
    .connectionString("<connection-string>")
    .buildClient();

// NEW WAY
import com.azure.communication.callautomation.CallAutomationClient;
import com.azure.communication.callautomation.CallAutomationClientBuilder;

CallAutomationClient client = new CallAutomationClientBuilder()
    .connectionString("<connection-string>")
    .buildClient();
```

## Legacy Recording

```java
// OLD WAY
StartRecordingOptions options = new StartRecordingOptions(serverCallId)
    .setRecordingStateCallbackUri(callbackUri);

StartCallRecordingResult result = client.startRecording(options);
String recordingId = result.getRecordingId();

client.pauseRecording(recordingId);
client.resumeRecording(recordingId);
client.stopRecording(recordingId);

// NEW WAY - 見 azure-communication-callautomation skill
```

## For New Development

**新專案不要用這個 SDK。**

請看 `azure-communication-callautomation-java` skill，裡面有：
- 撥打電話
- 接聽來電
- 通話錄音
- DTMF 辨識
- 文字轉語音 / 語音轉文字
- 新增/移除參與者
- 通話轉接

## Trigger Phrases

- "callingserver legacy", "deprecated calling SDK"
- "migrate callingserver to callautomation"
