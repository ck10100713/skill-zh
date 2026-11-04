---
name: build-zoom-meeting-sdk-app
description: Zoom Meeting SDK 的參考 skill。在已經導向會議嵌入工作流程之後使用，適用於實作真正的 Zoom 會議加入、各平台 SDK 的行為、驗證與加入流程、等候室問題，或會議機器人模式。
triggers:
  - "embed meeting"
  - "embed zoom meeting"
  - "integrate meeting"
  - "meeting in web app"
  - "meeting in website"
  - "add zoom to website"
  - "meeting sdk"
  - "join meeting programmatically"
  - "meeting bot"
  - "bot joins meeting"
  - "joining meeting timeout"
  - "join meeting failed"
  - "waiting room"
  - "hide meeting info"
  - "hide meeting password"
---

# /build-zoom-meeting-sdk-app

跨網頁、行動、桌面和 Linux 機器人環境的內嵌 Zoom 會議背景參考。優先使用 `build-zoom-meeting-app` 或 `build-zoom-bot`，再轉到這裡看各平台的細節。

# Zoom Meeting SDK

把完整的 Zoom 會議體驗嵌入到網頁、行動、桌面和無介面（headless）的整合裡。

## 強制的路由護欄（先讀這個）

- 如果使用者要求在自己 app 的 UI 裡嵌入/加入會議，就導向 Meeting SDK 的實作。
- 除非使用者明確要求管理會議資源，或要瀏覽器的 `join_url` 連結，否則不要改用只靠 REST 的會議連結流程。
- Meeting SDK 的加入路徑需要 SDK signature 加上 SDK 的 join 呼叫；REST 的 `join_url` 不是 Meeting SDK 的加入 payload。

## 前置需求

- 擁有 Meeting SDK 憑證的 Zoom app
- 從 Marketplace 取得的 SDK Key 和 Secret
- 各平台的開發環境（Web、Android、iOS、macOS、Unreal、Electron、Linux 或 Windows）

> **OAuth 或 signature 需要協助？** 驗證流程請看 **[zoom-oauth](../oauth/SKILL.md)** skill。

> **需要網頁的加入前診斷？** 在 Meeting SDK 初始化/加入之前，先用 **[probe-sdk](../probe-sdk/SKILL.md)**，把準備度低的裝置/網路擋在外面。

> **快速開始排查：** 深入除錯之前，先用 **[5 分鐘 Runbook](RUNBOOK.md)**。

## 快速開始（Web，透過 CDN 的 Client View）

```html
<script src="https://source.zoom.us/3.1.6/lib/vendor/react.min.js"></script>
<script src="https://source.zoom.us/3.1.6/lib/vendor/react-dom.min.js"></script>
<script src="https://source.zoom.us/3.1.6/lib/vendor/redux.min.js"></script>
<script src="https://source.zoom.us/3.1.6/lib/vendor/redux-thunk.min.js"></script>
<script src="https://source.zoom.us/3.1.6/lib/vendor/lodash.min.js"></script>
<script src="https://source.zoom.us/3.1.6/zoom-meeting-3.1.6.min.js"></script>

<script>
// CDN 提供的是 ZoomMtg（Client View，整頁）
// 要用 ZoomMtgEmbedded（Component View），請改用 npm

ZoomMtg.preLoadWasm();
ZoomMtg.prepareWebSDK();

ZoomMtg.init({
  leaveUrl: window.location.href,
  patchJsMedia: true,
  disableCORP: !window.crossOriginIsolated,
  success: function() {
    ZoomMtg.join({
      sdkKey: 'YOUR_SDK_KEY',
      signature: 'YOUR_SIGNATURE',  // 要在伺服器端產生！
      meetingNumber: 'MEETING_NUMBER',
      userName: 'User Name',
      passWord: '',  // 注意：camelCase，W 要大寫
      success: function(res) { console.log('Joined'); },
      error: function(err) { console.error(err); }
    });
  },
  error: function(err) { console.error(err); }
});
</script>
```

## 重要注意事項（Web）

### 1. CDN 和 npm 的 API 不一樣！

| 發行方式 | 全域物件 | 檢視類型 | API 風格 |
|--------------|---------------|-----------|-----------|
| CDN（`zoom-meeting-{ver}.min.js`） | `ZoomMtg` | Client View（整頁） | Callbacks |
| npm（`@zoom/meetingsdk`） | `ZoomMtgEmbedded` | Component View（可嵌入） | Promises |

### 2. 正式環境需要後端

**絕對不要把 SDK Secret 暴露在用戶端程式碼裡。** 在伺服器端產生 signature：

```javascript
// server.js（Node.js 範例）
const KJUR = require('jsrsasign');

app.post('/api/signature', (req, res) => {
  const { meetingNumber, role } = req.body;
  const iat = Math.floor(Date.now() / 1000) - 30;
  const exp = iat + 60 * 60 * 2;
  
  const header = { alg: 'HS256', typ: 'JWT' };
  const payload = {
    sdkKey: process.env.ZOOM_SDK_KEY,
    mn: String(meetingNumber).replace(/\D/g, ''),
    role: parseInt(role, 10),
    iat, exp, tokenExp: exp
  };
  
  const signature = KJUR.jws.JWS.sign('HS256',
    JSON.stringify(header),
    JSON.stringify(payload),
    process.env.ZOOM_SDK_SECRET
  );
  
  res.json({ signature, sdkKey: process.env.ZOOM_SDK_KEY });
});
```

### 3. CSS 衝突：避免全域 reset

全域的 `* { margin: 0; }` 會弄壞 Zoom 的 UI。要限縮你的樣式範圍：

```css
/* 錯誤 */
* { margin: 0; padding: 0; }

/* 正確 */
.your-app, .your-app * { box-sizing: border-box; }
```

### 4. Client View 工具列被裁切的修正

如果工具列掉到畫面外，就縮小 Zoom 的 UI：

```css
#zmmtg-root {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  /* 對 SPA（React/Next 等）很關鍵：確保 Zoom UI 不會在你的 app 外殼/覆蓋層後面。 */
  z-index: 9999 !important;
  transform: scale(0.95) !important;
  transform-origin: top center !important;
}
```

### 5. 會議開始時隱藏你的 App

Client View 會佔滿整個頁面。要隱藏你的 UI：

```javascript
// 在 ZoomMtg.init 的 success callback 裡：
document.documentElement.classList.add('meeting-active');
document.body.classList.add('meeting-active');
```

```css
body.meeting-active .your-app { display: none !important; }
body.meeting-active { background: #000 !important; }
```

## UI 選項（Web）

Meeting SDK 提供的是**可客製化的 Zoom UI**：

| 檢視 | 說明 |
|------|-------------|
| **Component View** | 可抽出、可客製化的 UI，把會議嵌進一個 div |
| **Client View** | 整頁的 Zoom UI 體驗 |

**注意**：跟 Video SDK 要從零開始自己做 UI 不同，Meeting SDK 是以 Zoom 的 UI 為基礎，再在上面做客製化。

## 關鍵概念

| 概念 | 說明 |
|---------|-------------|
| SDK Key/Secret | 從 Marketplace 取得的憑證 |
| Signature | 用 SDK Secret 簽署的 JWT |
| Component View | 可抽出、可客製化的 UI（Web） |
| Client View | 整頁的 Zoom UI（Web） |

## 詳細參考

### 平台指南
- **[android/SKILL.md](android/SKILL.md)**：Android SDK（預設/自訂 UI、加入/開始/驗證生命週期、行動端整合）
- **[android/references/android-reference-map.md](android/references/android-reference-map.md)**：Android API 介面地圖和變動觀察點
- **[ios/SKILL.md](ios/SKILL.md)**：iOS SDK（預設/自訂 UI、加入/開始/驗證生命週期、行動端整合）
- **[ios/references/ios-reference-map.md](ios/references/ios-reference-map.md)**：iOS API 介面地圖和變動觀察點
- **[macos/SKILL.md](macos/SKILL.md)**：macOS SDK（桌面預設/自訂 UI、服務 controller、主持人流程）
- **[macos/references/macos-reference-map.md](macos/references/macos-reference-map.md)**：macOS API 介面地圖和變動觀察點
- **[unreal/SKILL.md](unreal/SKILL.md)**：Unreal Engine 封裝（C++/Blueprint 封裝的行為和 SDK 對應）
- **[unreal/references/unreal-reference-map.md](unreal/references/unreal-reference-map.md)**：Unreal 封裝的參考地圖和版本落後說明
- **[references/android.md](references/android.md)**：Android 指引文件，用於從廣泛的 Meeting SDK 查詢快速導向
- **[references/ios.md](references/ios.md)**：iOS 指引文件，用於從廣泛的 Meeting SDK 查詢快速導向
- **[references/macos.md](references/macos.md)**：macOS 指引文件，用於從廣泛的 Meeting SDK 查詢快速導向
- **[references/unreal.md](references/unreal.md)**：Unreal 指引文件，用於從廣泛的 Meeting SDK 查詢快速導向
- **[linux/SKILL.md](linux/SKILL.md)**：Linux SDK 無介面機器人 skill 的入口
- **[linux/linux.md](linux/linux.md)**：Linux SDK（C++ 無介面機器人、原始媒體存取）
- **[linux/references/linux-reference.md](linux/references/linux-reference.md)**：Linux 相依套件、Docker、疑難排解
- **[react-native/SKILL.md](react-native/SKILL.md)**：React Native SDK（iOS/Android 封裝、加入/開始流程、bridge 設定）
- **[react-native/SKILL.md](react-native/SKILL.md)**：React Native 完整導覽
- **[electron/SKILL.md](electron/SKILL.md)**：Electron SDK（桌面封裝、驗證/加入流程、模組 controller、原始資料）
- **[electron/SKILL.md](electron/SKILL.md)**：Electron 完整導覽
- **[windows/SKILL.md](windows/SKILL.md)**：Windows SDK（C++ 桌面應用程式、原始媒體存取）
- **[windows/references/windows-reference.md](windows/references/windows-reference.md)**：Windows 相依套件、Visual Studio 設定、疑難排解
- **[web/references/web.md](web/references/web.md)**：Web SDK（Component + Client View）
- **[web/references/web-tracking-id.md](web/references/web-tracking-id.md)**：Tracking ID 設定

### 功能
- **[references/authorization.md](references/authorization.md)**：SDK JWT 的產生
- **[references/bot-authentication.md](references/bot-authentication.md)**：機器人的 ZAK、OBF 和 JWT token 比較
- **[references/breakout-rooms.md](references/breakout-rooms.md)**：以程式管理分組討論室
- **[references/ai-companion.md](references/ai-companion.md)**：會議中的 AI Companion 控制
- **[references/webinars.md](references/webinars.md)**：Webinar SDK 功能
- **[references/forum-top-questions.md](references/forum-top-questions.md)**：論壇常見的問題模式（該涵蓋什麼）
- **[references/triage-intake.md](references/triage-intake.md)**：該先問什麼（把模糊的回報變成答案）
- **[references/signature-playbook.md](references/signature-playbook.md)**：Signature 與根本原因的作戰手冊
- **[references/multiple-meetings.md](references/multiple-meetings.md)**：同時加入多場會議 / 多個實例
- **[references/troubleshooting.md](references/troubleshooting.md)**：常見問題與解法

## 範例 Repo

### 官方（Zoom 提供）

| 類型 | Repo | Stars |
|------|------------|-------|
| Linux Headless | [meetingsdk-headless-linux-sample](https://github.com/zoom/meetingsdk-headless-linux-sample) | 4 |
| Linux Raw Data | [meetingsdk-linux-raw-recording-sample](https://github.com/zoom/meetingsdk-linux-raw-recording-sample) | 0 |
| Web | [meetingsdk-web-sample](https://github.com/zoom/meetingsdk-web-sample) | 643 |
| Web NPM | [meetingsdk-web](https://github.com/zoom/meetingsdk-web) | 324 |
| React | [meetingsdk-react-sample](https://github.com/zoom/meetingsdk-react-sample) | 177 |
| Auth | [meetingsdk-auth-endpoint-sample](https://github.com/zoom/meetingsdk-auth-endpoint-sample) | 124 |
| Angular | [meetingsdk-angular-sample](https://github.com/zoom/meetingsdk-angular-sample) | 60 |
| Vue.js | [meetingsdk-vuejs-sample](https://github.com/zoom/meetingsdk-vuejs-sample) | 42 |

**完整清單**：見 [general/references/community-repos.md](../general/references/community-repos.md)

## 資源

- **官方文件**：https://developers.zoom.us/docs/meeting-sdk/
- **開發者論壇**：https://devforum.zoom.us/

## 環境變數

- 標準化的 `.env` key，以及各個值在哪裡找，見 [references/environment-variables.md](references/environment-variables.md)。
