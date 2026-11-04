---
name: zoom-meeting-sdk-web-client-view
description: |
  Zoom Meeting SDK Web - Client View。熟悉的 Zoom 介面，提供整頁的 Zoom 會議體驗。
  使用 ZoomMtg 全域 singleton，採用 callback 式 API。適合用最少的客製化快速整合。
  提供跟 Zoom Web Client 相同的 UI。
user-invocable: false
triggers:
  - "meeting sdk client view"
  - "zoommtg"
  - "full page zoom ui"
  - "password"
  - "preparewebsdk"
---

# Zoom Meeting SDK Web - Client View

把整頁的 Zoom 會議體驗嵌進你的網頁應用程式。Client View 提供熟悉的 Zoom 介面，幾乎不需要客製化。

## 概覽

Client View 使用 `ZoomMtg` 全域 singleton，渲染出跟 Zoom Web Client 一模一樣的整頁會議體驗。

| 面向 | 細節 |
|--------|---------|
| **API 物件** | `ZoomMtg`（全域 singleton） |
| **API 風格** | 以 callback 為基礎 |
| **UI** | 整頁接管 |
| **密碼參數** | `passWord`（W 要大寫） |
| **事件** | `inMeetingServiceListener()` |
| **最適合** | 快速整合、標準的 Zoom UI |

## 安裝

### NPM

```bash
npm install @zoom/meetingsdk --save
```

```javascript
import { ZoomMtg } from '@zoom/meetingsdk';
```

### CDN

```html
<script src="https://source.zoom.us/{VERSION}/lib/vendor/react.min.js"></script>
<script src="https://source.zoom.us/{VERSION}/lib/vendor/react-dom.min.js"></script>
<script src="https://source.zoom.us/{VERSION}/lib/vendor/redux.min.js"></script>
<script src="https://source.zoom.us/{VERSION}/lib/vendor/redux-thunk.min.js"></script>
<script src="https://source.zoom.us/{VERSION}/lib/vendor/lodash.min.js"></script>
<script src="https://source.zoom.us/zoom-meeting-{VERSION}.min.js"></script>
```

## 完整的初始化流程

```javascript
// Step 1：檢查瀏覽器相容性
console.log('Requirements:', ZoomMtg.checkSystemRequirements());

// Step 2：設定 CDN 路徑（選用，給中國或自行代管用）
// ZoomMtg.setZoomJSLib('https://source.zoom.us/{VERSION}/lib', '/av');

// Step 3：預先載入 WebAssembly 模組
ZoomMtg.preLoadWasm();
ZoomMtg.prepareWebSDK();

// Step 4：載入語言資源
ZoomMtg.i18n.load('en-US');
ZoomMtg.i18n.onLoad(() => {
  
  // Step 5：初始化 SDK
  ZoomMtg.init({
    leaveUrl: '/meeting-ended',
    patchJsMedia: true,
    disableCORP: !window.crossOriginIsolated,
    success: () => {
      console.log('SDK initialized');
      
      // Step 6：加入會議
      const joinPayload = {
        signature: signature,
        meetingNumber: meetingNumber,
        userName: userName,
        passWord: passWord,
        success: (res) => {
          console.log('Joined meeting');

          // Step 7：加入後的操作
          ZoomMtg.getAttendeeslist({});
          ZoomMtg.getCurrentUser({
            success: (res) => console.log('Current user:', res.result.currentUser)
          });
        },
        error: (err) => console.error('Join failed:', err)
      };

      // 重要：選填欄位只有在有實際的值時才放進去
      // 對某些選填欄位傳 undefined，可能造成執行時的加入錯誤
      if (userEmail) joinPayload.userEmail = userEmail;
      if (tk) joinPayload.tk = tk;
      if (zak) joinPayload.zak = zak;

      ZoomMtg.join(joinPayload);
    },
    error: (err) => console.error('Init failed:', err)
  });
});
```

## ZoomMtg.init()：所有選項

### 必填

| 參數 | 型別 | 說明 |
|-----------|------|-------------|
| `leaveUrl` | `string` | 離開會議後要導向的 URL |

### UI 客製化

| 參數 | 型別 | 預設 | 說明 |
|-----------|------|---------|-------------|
| `showMeetingHeader` | `boolean` | `true` | 顯示會議號碼和主題 |
| `disableInvite` | `boolean` | `false` | 隱藏邀請按鈕 |
| `disableCallOut` | `boolean` | `false` | 隱藏撥出選項 |
| `disableRecord` | `boolean` | `false` | 隱藏錄影按鈕 |
| `disableJoinAudio` | `boolean` | `false` | 隱藏加入音訊選項 |
| `disablePreview` | `boolean` | `false` | 跳過音訊/視訊預覽 |
| `audioPanelAlwaysOpen` | `boolean` | `false` | 讓音訊面板保持開啟 |
| `showPureSharingContent` | `boolean` | `false` | 避免在分享內容上出現疊層 |
| `videoHeader` | `boolean` | `true` | 顯示視訊磚的標頭 |
| `isLockBottom` | `boolean` | `true` | 顯示/隱藏頁尾 |
| `videoDrag` | `boolean` | `true` | 啟用拖曳視訊磚 |
| `sharingMode` | `string` | `'both'` | `'both'` 或 `'fit'` |
| `screenShare` | `boolean` | `true` | 啟用瀏覽器 URL 分享 |
| `hideShareAudioOption` | `boolean` | `false` | 隱藏「分享分頁音訊」核取方塊 |
| `disablePictureInPicture` | `boolean` | `false` | 停用 PiP 模式 |
| `disableZoomLogo` | `boolean` | `false` | 移除 Zoom logo（已棄用） |
| `defaultView` | `string` | `'speaker'` | `'gallery'`、`'speaker'`、`'multiSpeaker'` |

### 功能開關

| 參數 | 型別 | 預設 | 說明 |
|-----------|------|---------|-------------|
| `isSupportAV` | `boolean` | `true` | 啟用音訊/視訊 |
| `isSupportChat` | `boolean` | `true` | 啟用會議中聊天 |
| `isSupportQA` | `boolean` | `true` | 啟用網路研討會 Q&A |
| `isSupportCC` | `boolean` | `true` | 啟用字幕 |
| `isSupportPolling` | `boolean` | `true` | 啟用投票 |
| `isSupportBreakout` | `boolean` | `true` | 啟用 breakout rooms |
| `isSupportNonverbal` | `boolean` | `true` | 啟用非語言回饋 |
| `isSupportSimulive` | `boolean` | `false` | 啟用 Simulive |
| `disableVoIP` | `boolean` | `false` | 停用 VoIP |
| `disableReport` | `boolean` | `false` | 停用回報功能 |

### 視訊品質

| 參數 | 型別 | 預設 | 說明 |
|-----------|------|---------|-------------|
| `enableHD` | `boolean` | `true` (≥2.8.0) | 啟用 720p 視訊 |
| `enableFullHD` | `boolean` | `false` | 為網路研討會參加者啟用 1080p |

### 進階

| 參數 | 型別 | 預設 | 說明 |
|-----------|------|---------|-------------|
| `debug` | `boolean` | `false` | 啟用除錯記錄 |
| `patchJsMedia` | `boolean` | `false` | 自動套用媒體修正 |
| `disableCORP` | `boolean` | `false` | 停用 web isolation |
| `helper` | `string` | `''` | helper.html 的路徑 |
| `externalLinkPage` | `string` | - | 外部連結用的頁面 |
| `webEndpoint` | `string` | - | 給 ZFG 環境用 |
| `leaveOnPageUnload` | `boolean` | `false` | 頁面關閉時自動清理 |
| `isShowJoiningErrorDialog` | `boolean` | `true` | 加入失敗時顯示錯誤對話框 |
| `meetingInfo` | `Array<string>` | `[...]` | 要顯示的會議資訊 |
| `inviteUrlFormat` | `string` | `''` | 自訂的邀請 URL 格式 |
| `loginWindow` | `object` | `{width: 400, height: 380}` | 登入彈出視窗的大小 |

### Callbacks

| 參數 | 型別 | 說明 |
|-----------|------|-------------|
| `success` | `Function` | 初始化成功時呼叫 |
| `error` | `Function` | 初始化失敗時呼叫 |

## ZoomMtg.join()：所有選項

### 必填

| 參數 | 型別 | 說明 |
|-----------|------|-------------|
| `signature` | `string` | 從後端取得的 SDK JWT（v5.0+：必須包含 appKey 前綴） |
| `meetingNumber` | `string \| number` | 會議或網路研討會的號碼 |
| `userName` | `string` | 顯示名稱 |
| `passWord` | `string` | 會議密碼（W 要大寫！） |

### 驗證

| 參數 | 型別 | 何時必填 | 說明 |
|-----------|------|---------------|-------------|
| `zak` | `string` | 以主持人身分開始時 | 主持人的 Zoom Access Key |
| `tk` | `string` | 需要註冊時 | 註冊者 token |
| `userEmail` | `string` | 網路研討會 | 使用者 email |
| `obfToken` | `string` | 2026 年 3 月起 | App Privilege Token |

### 選填

| 參數 | 型別 | 說明 |
|-----------|------|-------------|
| `customerKey` | `string` | 自訂 ID（最多 36 字元） |
| `recordingToken` | `string` | 本機錄影權限 |

### Callbacks

| 參數 | 型別 | 說明 |
|-----------|------|-------------|
| `success` | `Function` | 加入成功時呼叫 |
| `error` | `Function` | 加入失敗時呼叫 |

## 事件監聽器

### 使用者事件

```javascript
ZoomMtg.inMeetingServiceListener('onUserJoin', (data) => {
  console.log('User joined:', data);
  // { userId, userName, ... }
});

ZoomMtg.inMeetingServiceListener('onUserLeave', (data) => {
  console.log('User left:', data);
  // 原因代碼：
  // 0: OTHER
  // 1: HOST_ENDED_MEETING
  // 2: SELF_LEAVE_FROM_IN_MEETING
  // 3: SELF_LEAVE_FROM_WAITING_ROOM
  // 4: SELF_LEAVE_FROM_WAITING_FOR_HOST_START
  // 5: MEETING_TRANSFER
  // 6: KICK_OUT_FROM_MEETING
  // 7: KICK_OUT_FROM_WAITING_ROOM
  // 8: LEAVE_FROM_DISCLAIMER
});

ZoomMtg.inMeetingServiceListener('onUserUpdate', (data) => {
  console.log('User updated:', data);
});

ZoomMtg.inMeetingServiceListener('onUserIsInWaitingRoom', (data) => {
  console.log('User in waiting room:', data);
});
```

### 會議狀態

```javascript
ZoomMtg.inMeetingServiceListener('onMeetingStatus', (data) => {
  // status: 1=連線中, 2=已連線, 3=已斷線, 4=重新連線中
  console.log('Status:', data.status);
});
```

### 音訊/視訊事件

```javascript
ZoomMtg.inMeetingServiceListener('onActiveSpeaker', (data) => {
  // [{userId, userName}]
  console.log('Active speaker:', data);
});

ZoomMtg.inMeetingServiceListener('onNetworkQualityChange', (data) => {
  // {level: 0-5, userId, type: 'uplink'}
  // 0-1=差, 2=一般, 3-5=好
  console.log('Network quality:', data);
});

ZoomMtg.inMeetingServiceListener('onAudioQos', (data) => {
  console.log('Audio QoS:', data);
});

ZoomMtg.inMeetingServiceListener('onVideoQos', (data) => {
  console.log('Video QoS:', data);
});
```

### 聊天與通訊

```javascript
ZoomMtg.inMeetingServiceListener('onReceiveChatMsg', (data) => {
  console.log('Chat message:', data);
});

ZoomMtg.inMeetingServiceListener('onReceiveTranscriptionMsg', (data) => {
  console.log('Transcription:', data);
});

ZoomMtg.inMeetingServiceListener('onReceiveTranslateMsg', (data) => {
  console.log('Translation:', data);
});
```

### 錄影與分享

```javascript
ZoomMtg.inMeetingServiceListener('onRecordingChange', (data) => {
  console.log('Recording status:', data);
});

ZoomMtg.inMeetingServiceListener('onShareContentChange', (data) => {
  console.log('Share content:', data);
});

ZoomMtg.inMeetingServiceListener('receiveSharingChannelReady', (data) => {
  console.log('Sharing channel ready:', data);
});
```

### Breakout Rooms

```javascript
ZoomMtg.inMeetingServiceListener('onRoomStatusChange', (data) => {
  // status: 2=進行中, 3=關閉中, 4=已關閉
  console.log('Breakout room status:', data);
});
```

### 其他事件

```javascript
ZoomMtg.inMeetingServiceListener('onJoinSpeed', (data) => {
  console.log('Join metrics:', data);
});

ZoomMtg.inMeetingServiceListener('onVbStatusChange', (data) => {
  console.log('Virtual background status:', data);
});

ZoomMtg.inMeetingServiceListener('onFocusModeStatusChange', (data) => {
  console.log('Focus mode:', data);
});

ZoomMtg.inMeetingServiceListener('onPictureInPicture', (data) => {
  console.log('PiP status:', data);
});

ZoomMtg.inMeetingServiceListener('onClaimStatus', (data) => {
  console.log('Host claim status:', data);
});
```

## 常用 Method

### 會議資訊

```javascript
// 取得目前使用者
ZoomMtg.getCurrentUser({
  success: (res) => console.log(res.result.currentUser)
});

// 取得所有參加者
ZoomMtg.getAttendeeslist({});

// 取得會議資訊
ZoomMtg.getCurrentMeetingInfo({
  success: (res) => console.log(res)
});

// 取得 SDK 版本
ZoomMtg.getWebSDKVersion({
  success: (version) => console.log(version)
});
```

### 音訊/視訊控制

```javascript
// 靜音/取消靜音特定使用者
ZoomMtg.mute({ userId, mute: true });

// 全部靜音/取消全部靜音
ZoomMtg.muteAll({ muteAll: true });

// 停止接收音訊
ZoomMtg.stopIncomingAudio({ stop: true });

// 鏡像視訊
ZoomMtg.mirrorVideo({ mirror: true });
```

### 聊天

```javascript
// 傳送聊天訊息
ZoomMtg.sendChat({
  message: 'Hello!',
  userId: 0  // 0 = 所有人
});
```

### 會議控制

```javascript
// 離開會議
ZoomMtg.leaveMeeting({});

// 結束會議（只有主持人）
ZoomMtg.endMeeting({});

// 鎖定會議
ZoomMtg.lockMeeting({ lock: true });
```

### 主持人控制

```javascript
// 指定為主持人
ZoomMtg.makeHost({ userId });

// 指定為共同主持人
ZoomMtg.makeCoHost({ userId });

// 移除共同主持人
ZoomMtg.withdrawCoHost({ userId });

// 移除參加者
ZoomMtg.expel({ userId });

// 暫時保留
ZoomMtg.putOnHold({ userId, bHold: true });

// 用主持人金鑰取得主持人身分
ZoomMtg.claimHostWithHostKey({ hostKey: '123456' });

// 重新取回主持人身分
ZoomMtg.reclaimHost({});

// 讓等候室裡的所有人進入
ZoomMtg.admitAll({});
```

### 舉手

```javascript
// 舉手
ZoomMtg.raiseHand({ userId });

// 放下手
ZoomMtg.lowerHand({ oderId });

// 放下所有人的手
ZoomMtg.lowerAllHands({});
```

### Spotlight 與 Pin

```javascript
// Spotlight 視訊
ZoomMtg.operateSpotlight({ oderId, action: 'add' }); // 或 'remove'

// Pin 視訊
ZoomMtg.operatePin({ oderId, action: 'add' }); // 或 'remove'

// 允許多重 pin
ZoomMtg.allowMultiPin({ allow: true });
```

### 螢幕分享

```javascript
// 開始螢幕分享
ZoomMtg.startScreenShare({});

// 分享特定來源（Electron）
ZoomMtg.shareSource({ source });
```

### 錄影

```javascript
// 開始/停止錄影
ZoomMtg.record({ record: true }); // 或 false

// 顯示/隱藏錄影按鈕
ZoomMtg.showRecordFunction({ show: true });
```

### Breakout Rooms

```javascript
// 建立 breakout room
ZoomMtg.createBreakoutRoom({
  rooms: [{ name: 'Room 1' }, { name: 'Room 2' }]
});

// 開啟 breakout rooms
ZoomMtg.openBreakoutRooms({});

// 關閉 breakout rooms
ZoomMtg.closeBreakoutRooms({});

// 加入 breakout room
ZoomMtg.joinBreakoutRoom({ roomId });

// 離開 breakout room
ZoomMtg.leaveBreakoutRoom({});

// 把使用者移到 breakout room
ZoomMtg.moveUserToBreakoutRoom({ oderId, roomId });

// 取得 breakout room 狀態
ZoomMtg.getBreakoutRoomStatus({
  success: (res) => console.log(res)
});
```

### 虛擬背景

```javascript
// 檢查是否支援
ZoomMtg.isSupportVirtualBackground({
  success: (data) => console.log(data.result.isSupport)
});

// 設定虛擬背景
ZoomMtg.setVirtualBackground({ imageUrl: '...' });

// 取得虛擬背景狀態
ZoomMtg.getVirtualBackgroundStatus({
  success: (data) => console.log(data)
});

// 鎖定虛擬背景（主持人）
ZoomMtg.lockVirtualBackground({ lock: true });
```

### UI 控制

```javascript
// 顯示/隱藏會議標頭
ZoomMtg.showMeetingHeader({ show: true });

// 顯示/隱藏邀請按鈕
ZoomMtg.showInviteFunction({ show: true });

// 顯示/隱藏加入音訊按鈕
ZoomMtg.showJoinAudioFunction({ show: true });

// 顯示/隱藏撥出按鈕
ZoomMtg.showCalloutFunction({ show: true });

// 用新選項重新渲染
ZoomMtg.reRender({ lang: 'de-DE' });
```

### 語言

```javascript
// 載入語言
ZoomMtg.i18n.load('de-DE');

// 重新載入語言
ZoomMtg.i18n.reload('de-DE');

// 取得目前語言
ZoomMtg.i18n.getCurrentLang();

// 取得所有翻譯
ZoomMtg.i18n.getAll();
```

## 速率限制

| Method | 限制 |
|--------|-------|
| `join()` | 10 秒 |
| `callOut()` | 10 秒 |
| `mute()` | 1 秒 |
| `muteAll()` | 5 秒 |

## DOM 元素

SDK 會自動加入這些元素：
- `#zmmtg-root` - 會議主容器
- `#aria-notify-area` - 無障礙公告

**絕對不要**手動建立或移除這些元素。

### SPA（React/Next）疊層陷阱

如果你「加入」了，卻只看到空白或黑色區域，或是你的 app 外框而不是會議 UI，可能是 Zoom UI 渲染在你的 app 版面**後面**。要確保 `#zmmtg-root` 佔滿 viewport，並且在其他固定元素之上：

```css
#zmmtg-root {
  position: fixed !important;
  inset: 0 !important;
  z-index: 9999 !important;
}
```

### Join Payload 清理陷阱

如果 `ZoomMtg.join()` 只成功一半，畫面變黑，而且 console 出現像 `Cannot read properties of undefined (reading 'toString')` 的錯誤，就在呼叫 join 之前先清理選填欄位。

不要傳值為 `undefined` 的選填 key（`userEmail`、`tk`、`zak` 等）。先組好 payload，只有在那些 key 是非空字串時才附上去。

另外，除非你已經完整設定好 SharedArrayBuffer/gallery-view 的前置條件，否則 `ZoomMtg.init()` 時優先用 `defaultView: 'speaker'`。

## 資源

- [Web SDK 主 Skill](../SKILL.md)
- [參考索引](references/README.md)
- [錯誤碼](../troubleshooting/error-codes.md)
- [常見問題](../troubleshooting/common-issues.md)
- [SharedArrayBuffer 設定](../concepts/sharedarraybuffer.md)
- [官方 API 參考](https://marketplacefront.zoom.us/sdk/meeting/web/index.html)

## 操作

- [RUNBOOK.md](RUNBOOK.md) - 5 分鐘的事前檢查與除錯清單。
