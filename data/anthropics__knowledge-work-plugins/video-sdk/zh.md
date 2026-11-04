---
name: build-zoom-video-sdk-app
description: Zoom Video SDK 的參考 skill。導向自訂 session 工作流程之後，使用者需要完全掌控影片體驗，而不是真正的 Zoom 會議時使用。
triggers:
  - "custom video"
  - "video sdk"
  - "build video app"
  - "video session"
  - "video chat"
  - "video call"
  - "video conferencing"
  - "custom video ui"
  - "twitter spaces"
  - "clubhouse alternative"
  - "audio-only room"
  - "screen sharing"
  - "virtual background"
  - "native video sdk"
---

# /build-zoom-video-sdk-app

完全自訂的視訊 session 產品的背景參考。如果 Meeting SDK 和 Video SDK 之間的界線還不清楚，請先用 `plan-zoom-product`。

用 Zoom 的基礎設施打造自訂的視訊體驗。

## 硬性路由護欄（先讀這個）

- 如果使用者要的是自訂的即時視訊 app 行為（topic/session 加入、自訂 rendering、attach/detach），導向 Video SDK。
- Video SDK 的加入流程，不要改用 REST 的 meeting endpoint。
- Video SDK 不使用 Meeting ID、`join_url`，也不使用 Meeting SDK 加入 payload 的欄位（`meetingNumber`、`passWord`）。

## Meeting SDK vs Video SDK

| 功能 | Meeting SDK | Video SDK |
|---------|-------------|-----------|
| UI | 預設 Zoom UI 或自訂 UI | **完全自訂 UI**（你自己做） |
| 體驗 | Zoom 會議 | 視訊 session |
| 品牌 | 客製化有限 | **完全掌控品牌** |
| 功能 | 完整的 Zoom 功能 | 核心視訊功能 |

## UI 選項（Web）

Video SDK 讓你**完全掌控 UI**：

| 選項 | 說明 |
|--------|-------------|
| **UI Toolkit** | 預建的 React 元件（low-code） |
| **Custom UI** | 用 SDK API 自己做 UI |

## 先決條件

- 從 Marketplace 取得 Zoom Video SDK 憑證
- SDK Key 和 Secret
- Web 開發環境

> **需要 OAuth 或簽章的協助？** 驗證流程請看 **[zoom-oauth](../oauth/SKILL.md)** skill。

> **需要 web 上的加入前診斷？** 在 Video SDK `join()` 之前用 **[probe-sdk](../probe-sdk/SKILL.md)**，減少第一分鐘就失敗的情況。

> **快速開始排查：** 深入除錯之前，先用 **[5-Minute Runbook](RUNBOOK.md)**。

## Quick Start（Web）

### NPM 用法（用 Vite/Webpack 這類 bundler）

```javascript
import ZoomVideo from '@zoom/videosdk';

const client = ZoomVideo.createClient();
await client.init('en-US', 'Global', { patchJsMedia: true });
await client.join(topic, signature, userName, password);

// 重要：getMediaStream() 只有在 join() 之後才有用
const stream = client.getMediaStream();
await stream.startVideo();
await stream.startAudio();
```

### CDN 用法（不用 bundler）

> **警告：廣告攔截器會擋掉 `source.zoom.us`**。請自行 host SDK 來避免問題。

```bash
# 把 SDK 下載到本地
curl "https://source.zoom.us/videosdk/zoom-video-1.12.0.min.js" -o js/zoom-video-sdk.min.js
```

```html
<script src="js/zoom-video-sdk.min.js"></script>
```

```javascript
// CDN 匯出的是 WebVideoSDK，不是 ZoomVideo
// 必須用 .default 屬性
const ZoomVideo = WebVideoSDK.default;
const client = ZoomVideo.createClient();

await client.init('en-US', 'Global', { patchJsMedia: true });
await client.join(topic, signature, userName, password);

// 重要：getMediaStream() 只有在 join() 之後才有用
const stream = client.getMediaStream();
await stream.startVideo();
await stream.startAudio();
```

### 搭配 CDN 的 ES Module（race condition 修正）

用 `<script type="module">` 搭配 CDN 時，SDK 可能還沒載入完：

```javascript
// 等 SDK 載入完成再使用
function waitForSDK(timeout = 10000) {
  return new Promise((resolve, reject) => {
    if (typeof WebVideoSDK !== 'undefined') {
      resolve();
      return;
    }
    const start = Date.now();
    const check = setInterval(() => {
      if (typeof WebVideoSDK !== 'undefined') {
        clearInterval(check);
        resolve();
      } else if (Date.now() - start > timeout) {
        clearInterval(check);
        reject(new Error('SDK failed to load'));
      }
    }, 100);
  });
}

// 用法
await waitForSDK();
const ZoomVideo = WebVideoSDK.default;
const client = ZoomVideo.createClient();
```

## SDK 生命週期（順序至關重要）

SDK 有嚴格的生命週期。違反順序會造成無聲的失敗。

```
1. Create client:     client = ZoomVideo.createClient()
2. Initialize:        await client.init('en-US', 'Global', options)
3. Join session:      await client.join(topic, signature, userName, password)
4. Get stream:        stream = client.getMediaStream()  ← ONLY AFTER JOIN
5. Start media:       await stream.startVideo() / await stream.startAudio()
```

**常見錯誤（無聲失敗）：**

```javascript
// ❌ 錯誤：在加入之前取得 stream
const client = ZoomVideo.createClient();
await client.init('en-US', 'Global');
const stream = client.getMediaStream();  // 回傳 undefined！
await client.join(...);

// ✅ 正確：加入之後再取得 stream
const client = ZoomVideo.createClient();
await client.init('en-US', 'Global');
await client.join(...);
const stream = client.getMediaStream();  // 可以用！
```

## 影像 Rendering（事件驅動）

**SDK 是事件驅動的。** 你必須監聽事件，並據此 render 影像。

### 用 `attachVideo()`，不要用 `renderVideo()`

```javascript
import { VideoQuality } from '@zoom/videosdk';

// 開啟你自己的鏡頭
await stream.startVideo();

// Attach 影像：回傳要 append 到 DOM 的元素
const element = await stream.attachVideo(userId, VideoQuality.Video_360P);
container.appendChild(element);

// 用完後 detach
await stream.detachVideo(userId);
```

### 必要的事件

```javascript
// 其他參與者的影像開啟/關閉時
client.on('peer-video-state-change', async (payload) => {
  const { action, userId } = payload;
  if (action === 'Start') {
    const el = await stream.attachVideo(userId, VideoQuality.Video_360P);
    container.appendChild(el);
  } else {
    await stream.detachVideo(userId);
  }
});

// 參與者加入/離開時
client.on('user-added', (payload) => { /* 檢查 bVideoOn */ });
client.on('user-removed', (payload) => { stream.detachVideo(payload.userId); });
```

完整的事件處理寫法請看 [web/references/web.md](web/references/web.md)。

## 關鍵概念

| 概念 | 說明 |
|---------|-------------|
| Session | 視訊 session（不是會議） |
| Topic | Session 識別碼（你自己選的任意字串） |
| Signature | 用於授權的 JWT |
| MediaStream | 音訊/影像 stream 的控制 |

## Session 建立模式

**重要**：Video SDK 的 session 是**即時（just-in-time）**建立的，不用事先建立。

| 面向 | Video SDK | Meeting SDK |
|--------|-----------|-------------|
| 預先建立 | 不需要 | 先透過 API 建立 meeting |
| Session 開始 | 第一位參與者帶著 topic 加入 | 加入既有的 meeting ID |
| Topic | 任意字串（你自己定義） | 來自 API 的 meeting ID |
| 排程 | 不適用，session 是臨時的 | Meeting 可以排程 |

### Session 怎麼運作

1. **不需要預先建立**：有人加入之前，session 並不存在
2. **Topic = Session ID**：任何帶著相同 `topic` 字串加入的參與者，都會進入同一個 session
3. **第一次加入就建立**：第一位參與者加入時，session 就被建立
4. **沒有 meeting ID**：不像 Zoom Meetings，沒有數字的 meeting ID

```javascript
// 第一位使用者加入時，session 就當場建立
// 任何字串都可以當 topic，它會變成 session 識別碼
await client.join('my-custom-session-123', signature, 'User Name');

// 其他參與者用「相同」的 topic 加入「同一個」session
await client.join('my-custom-session-123', signature, 'Another User');
```

### Signature Endpoint 設定

Signature endpoint 必須讓你的 frontend 能存取，而且不會有 CORS 問題。

**選項 1：同源 Proxy（建議）**

```nginx
# Nginx 設定
location /api/ {
    proxy_pass http://YOUR_BACKEND_HOST:3005/api/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
}
```

```javascript
// Frontend 用相對 URL（同源）
const response = await fetch('/api/signature', { ... });
```

**選項 2：CORS 設定**

```javascript
// Express.js backend
const cors = require('cors');
app.use(cors({
  origin: ['https://your-domain.com'],
  credentials: true
}));
```

**警告：** 混合內容（HTTPS 頁面 → HTTP API）會被瀏覽器擋掉。

## 使用情境

| 使用情境 | 說明 |
|----------|-------------|
| [Video SDK BYOS (Bring Your Own Storage)](../general/use-cases/video-sdk-bring-your-own-storage.md) | 把錄影直接存到你自己的 S3 bucket |

## BYOS (Bring Your Own Storage)

Video SDK 的功能：Zoom 把雲端錄影**直接**存到你的 Amazon S3 bucket。不用下載。

> **官方文件：** https://developers.zoom.us/docs/build/storage/

**先決條件：**
- 有 Cloud Recording add-on 的 Video SDK 帳號（Universal Credit 已包含）
- AWS S3 bucket

**驗證選項：**
1. **AWS Access Key** - 設定較簡單
2. **Cross Account Access** - 較安全（IAM role assumption）

**S3 路徑結構：**
```
Buckets/{bucketName}/cmr/byos/{YYYY}/{MM}/{DD}/{GUID}/cmr_byos/
```

**主要好處：**
- 零下載頻寬成本
- 錄影時直接儲存
- 只要設定（不需要 webhook/下載的程式碼）

**設定位置：** Developer Portal → Account Settings → General → Communications Content Storage Location

完整的設定指南請看 **[../general/use-cases/video-sdk-bring-your-own-storage.md](../general/use-cases/video-sdk-bring-your-own-storage.md)**。

## 詳細參考

### UI 與元件
- **[references/ui-toolkit.md](references/ui-toolkit.md)** - 預建的 UI 元件（Web）
- **[references/triage-intake.md](references/triage-intake.md)** - 要先問什麼（把模糊的回報變成答案）
- **[references/session-lifecycle.md](references/session-lifecycle.md)** - 正確的 API 順序 + 事件驅動的 rendering
- **[references/licensing-and-entitlements.md](references/licensing-and-entitlements.md)** - 授權/管理員的先決條件
- **[references/token-contract-test-spec.md](references/token-contract-test-spec.md)** - 共用的 backend token 契約與跨平台 smoke test

### 平台指南
- **[references/authorization.md](references/authorization.md)** - Video SDK JWT 產生
- **[web/SKILL.md](web/SKILL.md)** - Web Video SDK（JavaScript/TypeScript）
  - **[web/SKILL.md](web/SKILL.md)** - 完整的文件導覽
  - **[web/examples/react-hooks.md](web/examples/react-hooks.md)** - 官方 React hooks 函式庫
  - **[web/examples/framework-integrations.md](web/examples/framework-integrations.md)** - Next.js、Vue/Nuxt 的寫法
- **[react-native/SKILL.md](react-native/SKILL.md)** - React Native Video SDK（行動端 wrapper、helper/事件架構）
  - **[react-native/SKILL.md](react-native/SKILL.md)** - React Native 文件導覽
  - **[react-native/examples/session-join-pattern.md](react-native/examples/session-join-pattern.md)** - 帶 token 的 session 加入流程
- **[flutter/SKILL.md](flutter/SKILL.md)** - Flutter Video SDK（行動端 wrapper、事件驅動架構）
  - **[flutter/SKILL.md](flutter/SKILL.md)** - Flutter 文件導覽
  - **[flutter/examples/session-join-pattern.md](flutter/examples/session-join-pattern.md)** - 帶 token 的 session 加入流程
- **[android/SKILL.md](android/SKILL.md)** - Android Video SDK（原生行動端自訂 UI、帶 token 的 session）
- **[ios/SKILL.md](ios/SKILL.md)** - iOS Video SDK（原生行動端自訂 UI、delegate 驅動的生命週期）
- **[macos/SKILL.md](macos/SKILL.md)** - macOS Video SDK（桌面原生 app、自訂 session 視窗）
- **[unity/SKILL.md](unity/SKILL.md)** - Unity Video SDK wrapper（遊戲引擎整合、場景驅動的 UX）
- **[linux/SKILL.md](linux/SKILL.md)** - Linux Video SDK 概覽（C++ headless bot）
- **[linux/linux.md](linux/linux.md)** - Linux C++ SDK（headless bot、原始媒體擷取/注入）
- **[linux/references/linux-reference.md](linux/references/linux-reference.md)** - Linux API 參考
- **[windows/SKILL.md](windows/SKILL.md)** - Windows C++ SDK（桌面應用程式、原始媒體擷取/注入）
- **[windows/references/windows-reference.md](windows/references/windows-reference.md)** - Windows API 參考
- **[references/troubleshooting.md](references/troubleshooting.md)** - 常見問題與解法
- **[references/forum-top-questions.md](references/forum-top-questions.md)** - 論壇常見的問題模式（要涵蓋什麼）

## 範例 Repo

### 官方（Zoom 出品）

| 類型 | Repository | Stars |
|------|------------|-------|
| Web | [videosdk-web-sample](https://github.com/zoom/videosdk-web-sample) | 137 |
| Web NPM | [videosdk-web](https://github.com/zoom/videosdk-web) | 56 |
| Auth | [videosdk-auth-endpoint-sample](https://github.com/zoom/videosdk-auth-endpoint-sample) | 23 |
| UI Toolkit Web | [videosdk-zoom-ui-toolkit-web](https://github.com/zoom/videosdk-zoom-ui-toolkit-web) | 17 |
| UI Toolkit React | [videosdk-zoom-ui-toolkit-react-sample](https://github.com/zoom/videosdk-zoom-ui-toolkit-react-sample) | 17 |
| Next.js | [videosdk-nextjs-quickstart](https://github.com/zoom/videosdk-nextjs-quickstart) | 16 |
| Telehealth | [VideoSDK-Web-Telehealth](https://github.com/zoom/VideoSDK-Web-Telehealth) | 11 |
| Linux | [videosdk-linux-raw-recording-sample](https://github.com/zoom/videosdk-linux-raw-recording-sample) | - |

**完整清單**：見 [general/references/community-repos.md](../general/references/community-repos.md)

## 資源

- **官方文件**：https://developers.zoom.us/docs/video-sdk/
- **開發者論壇**：https://devforum.zoom.us/

## 環境變數

- 標準化的 `.env` key，以及每個值要去哪裡找，請看 [references/environment-variables.md](references/environment-variables.md)。

## Linux 操作

- [linux/RUNBOOK.md](linux/RUNBOOK.md) - Linux 平台的 preflight 與除錯檢查清單。
