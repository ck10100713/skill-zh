---
name: zoom-meeting-sdk-web-component-view
description: |
  Zoom Meeting SDK Web - Component View。可嵌入的 Zoom 會議元件，採用 Promise 風格的 API，整合起來很有彈性。
  很適合 React/Vue/Angular app 和自訂版面。使用 ZoomMtgEmbedded，搭配 async/await 寫法和可嵌入的 UI 容器。
user-invocable: false
triggers:
  - "meeting sdk component view"
  - "zoommtgembedded"
  - "zoomapproot"
  - "embeddable meeting ui"
  - "component view embedded zoom"
  - "custom meeting ui"
  - "custom zoom meeting ui"
  - "custom meeting video ui"
  - "custom video ui for meeting"
---

# Zoom Meeting SDK Web - Component View

可嵌入的 Zoom 會議元件，能彈性整合進任何網頁應用程式。Component View 提供 Promise 風格的 API 和可自訂的 UI。

要在**真正的 Zoom 會議外面包一層自訂 UI**，這就是正確的 web skill。
除非使用者做的是非會議型的自訂 session 產品，否則不要導向 Video SDK。

## 概覽

Component View 用 `ZoomMtgEmbedded.createClient()` 在指定的容器元素裡建立可嵌入的會議元件。

| 面向 | 細節 |
|--------|---------|
| **API 物件** | `ZoomMtgEmbedded.createClient()`（實例） |
| **API 風格** | Promise 風格（async/await） |
| **UI** | 可嵌入任何容器 |
| **密碼參數** | `password`（小寫） |
| **事件** | `on()`/`off()` |
| **最適合** | 自訂版面、React/Vue/Angular app |

## 安裝

### NPM

```bash
npm install @zoom/meetingsdk --save
```

```javascript
import ZoomMtgEmbedded from '@zoom/meetingsdk/embedded';
```

### CDN

```html
<script src="https://source.zoom.us/{VERSION}/lib/vendor/react.min.js"></script>
<script src="https://source.zoom.us/{VERSION}/lib/vendor/react-dom.min.js"></script>
<script src="https://source.zoom.us/{VERSION}/lib/vendor/redux.min.js"></script>
<script src="https://source.zoom.us/{VERSION}/lib/vendor/redux-thunk.min.js"></script>
<script src="https://source.zoom.us/{VERSION}/lib/vendor/lodash.min.js"></script>
<script src="https://source.zoom.us/zoom-meeting-embedded-{VERSION}.min.js"></script>
```

## 完整初始化流程

```javascript
import ZoomMtgEmbedded from '@zoom/meetingsdk/embedded';

// 步驟 1：建立 client 實例（只做一次，不要每次 render 都建！）
const client = ZoomMtgEmbedded.createClient();

async function joinMeeting() {
  try {
    // 步驟 2：取得容器元素
    const meetingSDKElement = document.getElementById('meetingSDKElement');

    // 步驟 3：初始化 client
    await client.init({
      zoomAppRoot: meetingSDKElement,
      language: 'en-US',
      debug: true,
      patchJsMedia: true,
      leaveOnPageUnload: true,
    });

    // 步驟 4：加入會議
    await client.join({
      signature: signature,
      sdkKey: sdkKey,
      meetingNumber: meetingNumber,
      userName: userName,
      password: password,  // 小寫！
      userEmail: userEmail,
    });

    console.log('Joined successfully!');
  } catch (error) {
    console.error('Failed to join:', error);
  }
}
```

## client.init() - 所有選項

### 必填

| 參數 | 型別 | 說明 |
|-----------|------|-------------|
| `zoomAppRoot` | `HTMLElement` | 放會議 UI 的容器元素 |

### 顯示

| 參數 | 型別 | 預設值 | 說明 |
|-----------|------|---------|-------------|
| `language` | `string` | `'en-US'` | UI 語言 |
| `debug` | `boolean` | `false` | 啟用 debug 記錄 |

### 媒體

| 參數 | 型別 | 預設值 | 說明 |
|-----------|------|---------|-------------|
| `patchJsMedia` | `boolean` | `false` | 自動套用媒體修正 |
| `leaveOnPageUnload` | `boolean` | `false` | 頁面卸載時清理 |
| `enableHD` | `boolean` | `true` | 啟用 720p 影片 |
| `enableFullHD` | `boolean` | `false` | 啟用 1080p 影片 |

### 自訂

| 參數 | 型別 | 說明 |
|-----------|------|-------------|
| `customize` | `object` | UI 自訂選項 |
| `webEndpoint` | `string` | ZFG 用：`'www.zoomgov.com'` |
| `assetPath` | `string` | AV 函式庫的自訂路徑 |

### Customize 物件

```javascript
await client.init({
  zoomAppRoot: element,
  customize: {
    // 顯示的會議資訊
    meetingInfo: [
      'topic',
      'host', 
      'mn',
      'pwd',
      'telPwd',
      'invite',
      'participant',
      'dc',
      'enctype'
    ],
    
    // 影片自訂
    video: {
      isResizable: true,
      viewSizes: {
        default: {
          width: 1000,
          height: 600
        },
        ribbon: {
          width: 300,
          height: 700
        }
      },
      popper: {
        disableDraggable: false
      }
    },
    
    // 自訂工具列按鈕
    toolbar: {
      buttons: [
        {
          text: 'Custom Button',
          className: 'custom-btn',
          onClick: () => {
            console.log('Custom button clicked');
          }
        }
      ]
    },
    
    // 目前發言者指示器
    activeSpaker: {
      strokeColor: '#00FF00'
    }
  }
});
```

## client.join() - 所有選項

### 必填

| 參數 | 型別 | 說明 |
|-----------|------|-------------|
| `signature` | `string` | 後端產生的 SDK JWT |
| `sdkKey` | `string` | SDK Key / Client ID |
| `meetingNumber` | `string \| number` | 會議號碼 |
| `userName` | `string` | 顯示名稱 |

### 驗證

| 參數 | 型別 | 何時必填 | 說明 |
|-----------|------|---------------|-------------|
| `password` | `string` | 有設定時 | 會議密碼（小寫！） |
| `zak` | `string` | 以主持人身分開始時 | 主持人的 ZAK token |
| `tk` | `string` | 註冊 | 註冊者 token |
| `userEmail` | `string` | 網路研討會 | 使用者 email |

## 事件監聽

### 語法

```javascript
// 訂閱
client.on('event-name', callback);

// 取消訂閱
client.off('event-name', callback);
```

### 連線事件

```javascript
client.on('connection-change', (payload) => {
  // payload.state: 'Connecting', 'Connected', 'Reconnecting', 'Closed'
  console.log('Connection state:', payload.state);
  
  if (payload.state === 'Closed') {
    console.log('Reason:', payload.reason);
  }
});
```

### 使用者事件

```javascript
client.on('user-added', (payload) => {
  // 加入的使用者陣列
  console.log('Users added:', payload);
  payload.forEach(user => {
    console.log('User ID:', user.oderId);
    console.log('Name:', user.displayName);
  });
});

client.on('user-removed', (payload) => {
  // 離開的使用者陣列
  console.log('Users removed:', payload);
});

client.on('user-updated', (payload) => {
  // 屬性有變動的使用者陣列
  console.log('Users updated:', payload);
});
```

### 音訊事件

```javascript
client.on('active-speaker', (payload) => {
  // 目前的發言者
  console.log('Active speaker:', payload);
});

client.on('audio-statistic-data-change', (payload) => {
  console.log('Audio stats:', payload);
});
```

### 影片事件

```javascript
client.on('video-active-change', (payload) => {
  // 影片狀態改變
  console.log('Video active:', payload);
});

client.on('video-statistic-data-change', (payload) => {
  console.log('Video stats:', payload);
});
```

### 分享事件

```javascript
client.on('active-share-change', (payload) => {
  console.log('Share status:', payload);
});

client.on('share-statistic-data-change', (payload) => {
  console.log('Share stats:', payload);
});
```

### 聊天事件

```javascript
client.on('chat-on-message', (payload) => {
  console.log('Chat message:', payload);
});
```

### 錄製事件

```javascript
client.on('recording-change', (payload) => {
  console.log('Recording status:', payload);
});
```

### 媒體裝置事件

```javascript
client.on('media-sdk-change', (payload) => {
  console.log('Media SDK:', payload);
});

client.on('device-change', () => {
  console.log('Device changed');
});
```

## 常用方法

### 使用者資訊

```javascript
// 取得目前使用者
const currentUser = client.getCurrentUser();
console.log('Current user:', currentUser);

// 取得所有參與者
const participants = client.getParticipantsList();
console.log('Participants:', participants);

// 檢查使用者是不是主持人
const isHost = client.isHost();
```

### 音訊控制

```javascript
// 自己靜音／取消靜音
await client.mute(true);  // 靜音
await client.mute(false); // 取消靜音

// 特定使用者靜音／取消靜音（僅主持人）
await client.muteAudio(userId, true);

// 全體靜音（僅主持人）
await client.muteAllAudio(true);
```

### 影片控制

```javascript
// 開始／停止影片
await client.startVideo();
await client.stopVideo();

// 關閉／開啟使用者的影片（僅主持人）
await client.muteVideo(userId, true);
```

### 會議控制

```javascript
// 離開會議
client.leaveMeeting();

// 結束會議（僅主持人）
client.endMeeting();
```

### 螢幕分享

```javascript
// 開始螢幕分享
await client.startShareScreen();

// 停止螢幕分享
await client.stopShareScreen();
```

### 錄製

```javascript
// 開始錄製（雲端）
await client.startCloudRecording();

// 停止錄製
await client.stopCloudRecording();
```

### 虛擬背景

```javascript
// 檢查是否支援
const isSupported = await client.isSupportVirtualBackground();

// 設定虛擬背景
await client.setVirtualBackground(imageUrl);

// 移除虛擬背景
await client.removeVirtualBackground();
```

### 改名

```javascript
// 幫使用者改名
await client.rename(userId, 'New Name');
```

## React 整合

### 基本模式

```tsx
import { useEffect, useRef, useState, useCallback } from 'react';
import ZoomMtgEmbedded from '@zoom/meetingsdk/embedded';

type ZoomClient = ReturnType<typeof ZoomMtgEmbedded.createClient>;

function ZoomMeeting({ meetingNumber, password, userName }: Props) {
  const clientRef = useRef<ZoomClient | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isJoined, setIsJoined] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 只建立一次 client
  useEffect(() => {
    if (!clientRef.current) {
      clientRef.current = ZoomMtgEmbedded.createClient();
    }
  }, []);

  const joinMeeting = useCallback(async () => {
    if (!clientRef.current || !containerRef.current) return;

    try {
      // 從後端取得 signature
      const { signature, sdkKey } = await fetchSignature(meetingNumber);
      
      await clientRef.current.init({
        zoomAppRoot: containerRef.current,
        language: 'en-US',
        patchJsMedia: true,
        leaveOnPageUnload: true,
      });

      await clientRef.current.join({
        signature,
        sdkKey,
        meetingNumber,
        password,
        userName,
      });

      setIsJoined(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to join');
    }
  }, [meetingNumber, password, userName]);

  return (
    <div>
      <div 
        ref={containerRef} 
        style={{ width: '100%', height: '500px' }} 
      />
      {!isJoined && (
        <button onClick={joinMeeting}>Join Meeting</button>
      )}
      {error && <div className="error">{error}</div>}
    </div>
  );
}
```

### 在 React 裡處理事件

```tsx
useEffect(() => {
  if (!clientRef.current) return;
  
  const handleConnectionChange = (payload: any) => {
    if (payload.state === 'Connected') {
      setIsJoined(true);
    } else if (payload.state === 'Closed') {
      setIsJoined(false);
    }
  };

  const handleUserAdded = (payload: any) => {
    console.log('Users joined:', payload);
  };

  clientRef.current.on('connection-change', handleConnectionChange);
  clientRef.current.on('user-added', handleUserAdded);

  return () => {
    clientRef.current?.off('connection-change', handleConnectionChange);
    clientRef.current?.off('user-added', handleUserAdded);
  };
}, []);
```

## 定位與調整大小

### 初始大小

```javascript
await client.init({
  zoomAppRoot: element,
  customize: {
    video: {
      viewSizes: {
        default: { width: 1000, height: 600 }
      }
    }
  }
});
```

### 動態調整大小

容器元素的大小決定會議 UI 的大小。要調整的話：

```javascript
// 直接調整容器大小就好
document.getElementById('meetingSDKElement').style.width = '1200px';
document.getElementById('meetingSDKElement').style.height = '800px';
```

### 讓它可以調整大小

```javascript
customize: {
  video: {
    isResizable: true
  }
}
```

## 支援的功能

Component View 支援核心的會議功能。Client View 的部分功能可能無法使用。

| 功能 | 是否支援 |
|---------|-----------|
| 音訊／影片 | ✅ |
| 螢幕分享 | ✅ |
| 聊天 | ✅ |
| 虛擬背景 | ✅ |
| 分組討論室 | ✅ |
| 雲端錄製 | ✅ |
| 字幕 | ✅ |
| 即時逐字稿 | ✅ |
| 等候室 | ✅ |
| 圖庫檢視 | ✅ |
| 表情回應 | ✅ |
| 舉手 | ✅ |

需要其他功能的話，請聯絡 Zoom Developer Support。

## 錯誤處理

```javascript
try {
  await client.join({
    // ... 選項
  });
} catch (error) {
  // error.reason 含有錯誤碼
  // error.message 含有說明
  
  switch (error.reason) {
    case 'WRONG_MEETING_PASSWORD':
      console.error('Incorrect password');
      break;
    case 'MEETING_NOT_START':
      console.error('Meeting has not started');
      break;
    case 'INVALID_PARAMETERS':
      console.error('Invalid join parameters');
      break;
    default:
      console.error('Join failed:', error.message);
  }
}
```

## 與 Client View 的比較

| 功能 | Component View | Client View |
|---------|----------------|-------------|
| **API 風格** | Promises | Callbacks |
| **密碼參數** | `password` | `passWord` |
| **容器** | 自訂元素 | 自動使用 `#zmmtg-root` |
| **UI** | 可嵌入 | 整頁 |
| **預先載入** | 不需要 | `preLoadWasm()` |
| **語言** | init 選項 | `i18n.load()` |
| **事件** | `on()`/`off()` | `inMeetingServiceListener()` |

## 資源

- [Main Web SDK Skill](../SKILL.md)
- [Reference Index](references/README.md)
- [Error Codes](../troubleshooting/error-codes.md)
- [Common Issues](../troubleshooting/common-issues.md)
- [SharedArrayBuffer Setup](../concepts/sharedarraybuffer.md)
- [Official API Reference](https://marketplacefront.zoom.us/sdk/meeting/web/components/index.html)

## 營運

- [RUNBOOK.md](RUNBOOK.md) - 5 分鐘的 preflight 與除錯檢查清單。
