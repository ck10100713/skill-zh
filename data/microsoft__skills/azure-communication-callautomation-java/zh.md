---
name: azure-communication-callautomation-java
description: 用 Azure Communication Services Call Automation Java SDK 建構通話自動化流程。適用於實作 IVR 系統、通話路由、通話錄音、DTMF 辨識、文字轉語音，或 AI 驅動的通話流程。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: com.azure:azure-communication-callautomation
---

# Azure Communication Call Automation (Java)

建構伺服器端的通話自動化流程，包括 IVR 系統、通話路由、錄音和 AI 驅動的互動。

## Installation

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-communication-callautomation</artifactId>
    <version>1.6.0</version>
</dependency>
```

## Client Creation

```java
import com.azure.communication.callautomation.CallAutomationClient;
import com.azure.communication.callautomation.CallAutomationClientBuilder;
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

// 使用 DefaultAzureCredential
CallAutomationClient client = new CallAutomationClientBuilder()
    .endpoint("https://<resource>.communication.azure.com")
    .credential(credential)
    .buildClient();

// 使用 connection string
CallAutomationClient client = new CallAutomationClientBuilder()
    .connectionString("<connection-string>")
    .buildClient();
```

## Key Concepts

| Class | Purpose |
|-------|---------|
| `CallAutomationClient` | 撥打電話、接聽/拒接來電、轉接通話 |
| `CallConnection` | 已建立通話中的動作（加入參與者、結束通話） |
| `CallMedia` | 媒體操作（播放音訊、辨識 DTMF/語音） |
| `CallRecording` | 開始/停止/暫停錄音 |
| `CallAutomationEventParser` | 解析來自 ACS 的 webhook 事件 |

## Create Outbound Call

```java
import com.azure.communication.callautomation.models.*;
import com.azure.communication.common.CommunicationUserIdentifier;
import com.azure.communication.common.PhoneNumberIdentifier;

// 撥打 PSTN 號碼
PhoneNumberIdentifier target = new PhoneNumberIdentifier("+14255551234");
PhoneNumberIdentifier caller = new PhoneNumberIdentifier("+14255550100");

CreateCallOptions options = new CreateCallOptions(
    new CommunicationUserIdentifier("<user-id>"),  // 來源
    List.of(target))                                // 目標
    .setSourceCallerId(caller)
    .setCallbackUrl("https://your-app.com/api/callbacks");

CreateCallResult result = client.createCall(options);
String callConnectionId = result.getCallConnectionProperties().getCallConnectionId();
```

## Answer Incoming Call

```java
// 來自 Event Grid webhook 的 IncomingCall 事件
String incomingCallContext = "<incoming-call-context-from-event>";

AnswerCallOptions options = new AnswerCallOptions(
    incomingCallContext,
    "https://your-app.com/api/callbacks");

AnswerCallResult result = client.answerCall(options);
CallConnection callConnection = result.getCallConnection();
```

## Play Audio (Text-to-Speech)

```java
CallConnection callConnection = client.getCallConnection(callConnectionId);
CallMedia callMedia = callConnection.getCallMedia();

// 播放文字轉語音
TextSource textSource = new TextSource()
    .setText("Welcome to Contoso. Press 1 for sales, 2 for support.")
    .setVoiceName("en-US-JennyNeural");

PlayOptions playOptions = new PlayOptions(
    List.of(textSource),
    List.of(new CommunicationUserIdentifier("<target-user>")));

callMedia.play(playOptions);

// 播放音訊檔
FileSource fileSource = new FileSource()
    .setUrl("https://storage.blob.core.windows.net/audio/greeting.wav");

callMedia.play(new PlayOptions(List.of(fileSource), List.of(target)));
```

## Recognize DTMF Input

```java
// 辨識 DTMF 按鍵音
DtmfTone stopTones = DtmfTone.POUND;

CallMediaRecognizeDtmfOptions recognizeOptions = new CallMediaRecognizeDtmfOptions(
    new CommunicationUserIdentifier("<target-user>"),
    5)  // 最多收集幾個按鍵音
    .setInterToneTimeout(Duration.ofSeconds(5))
    .setStopTones(List.of(stopTones))
    .setInitialSilenceTimeout(Duration.ofSeconds(15))
    .setPlayPrompt(new TextSource().setText("Enter your account number followed by pound."));

callMedia.startRecognizing(recognizeOptions);
```

## Recognize Speech

```java
// 用 AI 做語音辨識
CallMediaRecognizeSpeechOptions speechOptions = new CallMediaRecognizeSpeechOptions(
    new CommunicationUserIdentifier("<target-user>"))
    .setEndSilenceTimeout(Duration.ofSeconds(2))
    .setSpeechLanguage("en-US")
    .setPlayPrompt(new TextSource().setText("How can I help you today?"));

callMedia.startRecognizing(speechOptions);
```

## Call Recording

```java
CallRecording callRecording = client.getCallRecording();

// 開始錄音
StartRecordingOptions recordingOptions = new StartRecordingOptions(
    new ServerCallLocator("<server-call-id>"))
    .setRecordingChannel(RecordingChannel.MIXED)
    .setRecordingContent(RecordingContent.AUDIO_VIDEO)
    .setRecordingFormat(RecordingFormat.MP4);

RecordingStateResult recordingResult = callRecording.start(recordingOptions);
String recordingId = recordingResult.getRecordingId();

// 暫停/繼續/停止
callRecording.pause(recordingId);
callRecording.resume(recordingId);
callRecording.stop(recordingId);

// 下載錄音（在 RecordingFileStatusUpdated 事件之後）
callRecording.downloadTo(recordingUrl, Paths.get("recording.mp4"));
```

## Add Participant to Call

```java
CallConnection callConnection = client.getCallConnection(callConnectionId);

CommunicationUserIdentifier participant = new CommunicationUserIdentifier("<user-id>");
AddParticipantOptions addOptions = new AddParticipantOptions(participant)
    .setInvitationTimeout(Duration.ofSeconds(30));

AddParticipantResult result = callConnection.addParticipant(addOptions);
```

## Transfer Call

```java
// 盲轉（blind transfer）
PhoneNumberIdentifier transferTarget = new PhoneNumberIdentifier("+14255559999");
TransferCallToParticipantResult result = callConnection.transferCallToParticipant(transferTarget);
```

## Handle Events (Webhook)

```java
import com.azure.communication.callautomation.CallAutomationEventParser;
import com.azure.communication.callautomation.models.events.*;

// 在你的 webhook endpoint 裡
public void handleCallback(String requestBody) {
    List<CallAutomationEventBase> events = CallAutomationEventParser.parseEvents(requestBody);
    
    for (CallAutomationEventBase event : events) {
        if (event instanceof CallConnected) {
            CallConnected connected = (CallConnected) event;
            System.out.println("Call connected: " + connected.getCallConnectionId());
        } else if (event instanceof RecognizeCompleted) {
            RecognizeCompleted recognized = (RecognizeCompleted) event;
            // 處理 DTMF 或語音辨識結果
            DtmfResult dtmfResult = (DtmfResult) recognized.getRecognizeResult();
            String tones = dtmfResult.getTones().stream()
                .map(DtmfTone::toString)
                .collect(Collectors.joining());
            System.out.println("DTMF received: " + tones);
        } else if (event instanceof PlayCompleted) {
            System.out.println("Audio playback completed");
        } else if (event instanceof CallDisconnected) {
            System.out.println("Call ended");
        }
    }
}
```

## Hang Up Call

```java
// 所有參與者都掛斷
callConnection.hangUp(true);

// 只掛斷這一端
callConnection.hangUp(false);
```

## Error Handling

```java
import com.azure.core.exception.HttpResponseException;

try {
    client.answerCall(options);
} catch (HttpResponseException e) {
    if (e.getResponse().getStatusCode() == 404) {
        System.out.println("Call not found or already ended");
    } else if (e.getResponse().getStatusCode() == 400) {
        System.out.println("Invalid request: " + e.getMessage());
    }
}
```

## Environment Variables

```bash
AZURE_COMMUNICATION_ENDPOINT=https://<resource>.communication.azure.com  # 所有驗證方式都需要
AZURE_COMMUNICATION_CONNECTION_STRING=endpoint=https://...;accesskey=...  # Entra ID 驗證的替代方案
CALLBACK_BASE_URL=https://your-app.com/api/callbacks  # webhook callback 需要
AZURE_TOKEN_CREDENTIALS=prod  # 只有在 production 使用 DefaultAzureCredential 時才需要
```

## Trigger Phrases

- "call automation Java", "IVR Java", "interactive voice response"
- "call recording Java", "DTMF recognition Java"
- "text to speech call", "speech recognition call"
- "answer incoming call", "transfer call Java"
- "Azure Communication Services call automation"
