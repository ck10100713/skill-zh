---
name: zoom-apps-sdk
description: Zoom Apps SDK 的參考 skill。在已經導向 in-client app 工作流之後使用，適用於開發在 Zoom 會議、webinar、主 client 或 Zoom Phone 裡面跑的 web app。
user-invocable: false
triggers:
  - "zoom app"
  - "in-meeting app"
  - "app inside zoom"
  - "zoom client app"
  - "layers api"
  - "immersive mode"
  - "camera mode"
  - "collaborate mode"
  - "appssdk"
  - "in-client oauth"
  - "zoom mail"
  - "domain allowlist"
  - "domain whitelist"
  - "url whitelisting"
  - "blank panel"
  - "runningContext"
  - "zoomSdk"
---

# Zoom Apps SDK

這是在 Zoom client 裡面跑的 web app 的背景參考資料。建議先走 `choose-zoom-approach`，再回到這裡查 Layers API、Collaborate Mode、in-client OAuth 和執行環境的限制。

# Zoom Apps SDK

開發在 Zoom client 裡面跑的 web app，包含會議、webinar、主 client 和 Zoom Phone。

**官方文件**：https://developers.zoom.us/docs/zoom-apps/
**SDK 參考**：https://appssdk.zoom.us/
**NPM 套件**：https://www.npmjs.com/package/@zoom/appssdk

## Quick Links

**第一次接觸 Zoom Apps？照這個順序走：**

1. **[Architecture](concepts/architecture.md)** - 前後端模式、內嵌瀏覽器、deep linking
2. **[Quick Start](examples/quick-start.md)** - 完整可跑的 Express + SDK app
3. **[Running Contexts](concepts/running-contexts.md)** - app 會在哪裡執行（inMeeting、inMainClient 等）
4. **[Zoom Apps vs Meeting SDK](concepts/meeting-sdk-vs-zoom-apps.md)** - 別再把兩種 app 類型搞混
4. **[In-Client OAuth](examples/in-client-oauth.md)** - 搭配 PKCE 的無縫授權
5. **[API Reference](references/apis.md)** - 100 多個 SDK 方法
6. **Integrated Index** - 見本檔下方的章節
7. **[5-Minute Runbook](RUNBOOK.md)** - 深入除錯之前的 preflight 檢查

**參考資料：**
- **[API Reference](references/apis.md)** - 依類別整理的所有 SDK 方法
- **[Events Reference](references/events.md)** - 所有 SDK 事件監聽器
- **[Layers API](references/layers-api.md)** - Immersive 和 camera mode 的繪製
- **[OAuth Reference](references/oauth.md)** - Zoom Apps 的 OAuth 流程
- **[Zoom Mail](references/zmail-sdk.md)** - Mail plugin 整合

**遇到問題？**
- App 在 Zoom 裡載不出來 → 看下面的 [Domain Allowlist](#url-whitelisting-required)
- SDK 錯誤 → [Common Issues](troubleshooting/common-issues.md)
- 本機開發環境設定 → [Debugging Guide](troubleshooting/debugging.md)
- 版本升級 → [Migration Guide](troubleshooting/migration.md)
- 從論壇整理出來的 FAQ → [Forum Top Questions](troubleshooting/forum-top-questions.md)

**想做 immersive 體驗？**
- [Layers Immersive Mode](examples/layers-immersive.md) - 自訂視訊版面
- [Camera Mode](examples/layers-camera.md) - 虛擬鏡頭覆蓋層

> **OAuth 需要協助？** 驗證流程請看 **[zoom-oauth](../oauth/SKILL.md)** skill。

## SDK Overview

Zoom Apps SDK（`@zoom/appssdk`）提供 JavaScript API，給在 Zoom 內嵌瀏覽器裡執行的 web app 使用：

- **Context APIs** - 取得會議、使用者和參與者資訊
- **Meeting Actions** - 分享 app、邀請參與者、開啟 URL
- **Authorization** - 搭配 PKCE 的 In-Client OAuth（不用瀏覽器 redirect）
- **Layers API** - Immersive 視訊版面和 camera mode 覆蓋層
- **Collaborate Mode** - 參與者之間共用 app 狀態
- **App Communication** - app 實例之間傳訊（主 client <-> 會議）
- **Media Controls** - 虛擬背景、列出鏡頭、錄影控制
- **UI Controls** - 展開 app、通知、popout
- **Events** - 回應會議狀態、參與者、分享等變化

## Prerequisites

- 在 [Marketplace](https://marketplace.zoom.us/) 把 Zoom app 設成 **"Zoom App"** 類型
- 有 Zoom Apps scope 的 OAuth 憑證（Client ID + Secret）
- Web 應用程式（建議用 Node.js + Express）
- **你的網域已加入** Marketplace 的 domain allowlist
- 本機開發用 ngrok 或 HTTPS tunnel
- Node.js 18+（後端 server 用）

## Quick Start

### Option A: NPM（框架專案建議用這個）

```bash
npm install @zoom/appssdk
```

```javascript
import zoomSdk from '@zoom/appssdk';

async function init() {
  try {
    const configResponse = await zoomSdk.config({
      capabilities: [
        'shareApp',
        'getMeetingContext',
        'getUserContext',
        'openUrl'
      ],
      version: '0.16'
    });

    console.log('Running context:', configResponse.runningContext);
    // 'inMeeting' | 'inMainClient' | 'inWebinar' | 'inImmersive' | ...

    const context = await zoomSdk.getMeetingContext();
    console.log('Meeting ID:', context.meetingID);
  } catch (error) {
    console.error('Not running inside Zoom:', error.message);
    showDemoMode();
  }
}
```

### Option B: CDN（Vanilla JS）

```html
<script src="https://appssdk.zoom.us/sdk.js"></script>

<script>
// CRITICAL：不要宣告 "let zoomSdk"，SDK 已經在全域定義了 window.zoomSdk
// 用 "let zoomSdk = ..." 會造成：SyntaxError: redeclaration of non-configurable global property
let sdk = window.zoomSdk;  // 換一個變數名稱

async function init() {
  try {
    const configResponse = await sdk.config({
      capabilities: ['shareApp', 'getMeetingContext', 'getUserContext'],
      version: '0.16'
    });

    console.log('Running context:', configResponse.runningContext);
  } catch (error) {
    console.error('Not running inside Zoom:', error.message);
    showDemoMode();
  }
}

function showDemoMode() {
  document.body.innerHTML = '<h1>Preview Mode</h1><p>Open this app inside Zoom to use.</p>';
}

document.addEventListener('DOMContentLoaded', () => {
  init();
  setTimeout(() => { if (!sdk) showDemoMode(); }, 3000);
});
</script>
```

## Critical: Global Variable Conflict

CDN script 會在全域定義 `window.zoomSdk`。**不要重新宣告它：**

```javascript
// WRONG - 在 Zoom 的內嵌瀏覽器裡會造成 SyntaxError
let zoomSdk = null;
zoomSdk = window.zoomSdk;

// CORRECT - 用不同的變數名稱
let sdk = window.zoomSdk;

// ALSO CORRECT - NPM import（不會衝突）
import zoomSdk from '@zoom/appssdk';
```

這只會發生在 CDN 的做法。NPM import 建立的是 module 範圍的變數，不會衝突。

## Browser Preview / Demo Mode

SDK 只有在 Zoom client 裡面才能運作。用一般瀏覽器開啟時：
- `window.zoomSdk` 存在，但 `sdk.config()` 會丟出錯誤
- 一定要用 try/catch 搭配 fallback UI
- 加上 timeout（3 秒），避免 SDK 卡住

## URL Whitelisting (Required)

**網域沒有加入白名單，你的 app 就不會在 Zoom 裡載入。**

1. 前往 [Zoom Marketplace](https://marketplace.zoom.us/)
2. 打開你的 app -> **Feature** 分頁
3. 在 **Zoom App** 底下找到 **Add Allow List**
4. 加入你的網域（例如正式環境用 `yourdomain.com`，開發用 `xxxxx.ngrok.io`）

沒做這步，Zoom client 會顯示空白面板，而且沒有任何錯誤訊息。

## OAuth Scopes (Required)

Capability 需要在 Marketplace 啟用對應的 OAuth scope：

| Capability | Required Scope |
|------------|----------------|
| `getMeetingContext` | `zoomapp:inmeeting` |
| `getUserContext` | `zoomapp:inmeeting` |
| `shareApp` | `zoomapp:inmeeting` |
| `openUrl` | `zoomapp:inmeeting` |
| `sendAppInvitation` | `zoomapp:inmeeting` |
| `runRenderingContext` | `zoomapp:inmeeting` |
| `authorize` | `zoomapp:inmeeting` |
| `getMeetingParticipants` | `zoomapp:inmeeting` |

**加 scope 的方法：** Marketplace -> 你的 App -> **Scopes** 分頁 -> 加入需要的 scope。

少了 scope，capability 會無聲失敗或丟出錯誤。新增 scope 之後，使用者必須重新授權。

## Running Contexts

你的 app 會在 Zoom 裡的不同介面執行。`configResponse.runningContext` 會告訴你現在在哪：

| Context | Surface | Description |
|---------|---------|-------------|
| `inMeeting` | 會議側邊欄 | 最常見。可使用完整的會議 API |
| `inMainClient` | 主 client 面板 | 首頁分頁。沒有會議 context API |
| `inWebinar` | Webinar 側邊欄 | 主持人/panelist。有會議 + webinar API |
| `inImmersive` | Layers API | 全螢幕自訂渲染 |
| `inCamera` | Camera mode | 虛擬鏡頭覆蓋層 |
| `inCollaborate` | Collaborate mode | 共用狀態的 context |
| `inPhone` | Zoom Phone | 電話通話 app |
| `inChat` | Team Chat | 聊天側邊欄 |

各 context 的行為和可用 API，請看 **[Running Contexts](concepts/running-contexts.md)**。

## SDK Initialization Pattern

每個 Zoom App 都從 `config()` 開始：

```javascript
import zoomSdk from '@zoom/appssdk';

const configResponse = await zoomSdk.config({
  capabilities: [
    // 列出你會用到的「所有」API
    'getMeetingContext',
    'getUserContext',
    'shareApp',
    'openUrl',
    'authorize',
    'onAuthorized'
  ],
  version: '0.16'
});

// configResponse 包含：
// {
//   runningContext: 'inMeeting',
//   clientVersion: '5.x.x',
//   unsupportedApis: []  // 這個 client 版本不支援的 API
// }
```

**規則：**
1. 呼叫任何其他 SDK 方法之前，**一定要**先呼叫 `config()`
2. 只有列在 `config()` 裡的 capability 才能用
3. Capability 必須對應 Marketplace 裡的 OAuth scope
4. 檢查 `unsupportedApis`，讓功能可以優雅降級

## In-Client OAuth (Summary)

授權的最佳 UX，不用瀏覽器 redirect：

```javascript
// 1. 從你的後端取得 code challenge
const { codeChallenge, state } = await fetch('/api/auth/challenge').then(r => r.json());

// 2. 觸發 in-client 授權
await zoomSdk.authorize({ codeChallenge, state });

// 3. 監聽授權結果
zoomSdk.addEventListener('onAuthorized', async (event) => {
  const { code, state } = event;
  // 4. 把 code 送到後端換 token
  await fetch('/api/auth/token', {
    method: 'POST',
    body: JSON.stringify({ code, state })
  });
});
```

完整實作請看 **[In-Client OAuth Guide](examples/in-client-oauth.md)**。

## Layers API (Summary)

建立 immersive 視訊版面和鏡頭覆蓋層：

```javascript
// 啟動 immersive mode，取代 gallery view
await zoomSdk.runRenderingContext({ view: 'immersive' });

// 擺放參與者的視訊畫面
await zoomSdk.drawParticipant({
  participantUUID: 'user-uuid',
  x: 0, y: 0, width: 640, height: 480, zIndex: 1
});

// 加上覆蓋用的圖片
await zoomSdk.drawImage({
  imageData: canvas.toDataURL(),
  x: 0, y: 0, width: 1280, height: 720, zIndex: 0
});

// 離開 immersive mode
await zoomSdk.closeRenderingContext();
```

請看 **[Layers Immersive](examples/layers-immersive.md)** 和 **[Camera Mode](examples/layers-camera.md)**。

## Environment Variables

| Variable | Description | Where to Find |
|----------|-------------|---------------|
| `ZOOM_APP_CLIENT_ID` | App client ID | Marketplace -> App -> App Credentials |
| `ZOOM_APP_CLIENT_SECRET` | App client secret | Marketplace -> App -> App Credentials |
| `ZOOM_APP_REDIRECT_URI` | OAuth redirect URL | 你的 server URL + `/auth` |
| `SESSION_SECRET` | Cookie 簽章用的 secret | 產生一個隨機字串 |
| `ZOOM_HOST` | Zoom host URL | `https://zoom.us`（或 `https://zoomgov.com`） |

## Common APIs

| API | Description |
|-----|-------------|
| `config()` | 初始化 SDK，申請 capability |
| `getMeetingContext()` | 取得會議 ID、主題、狀態 |
| `getUserContext()` | 取得使用者名稱、角色、參與者 ID |
| `getRunningContext()` | 取得目前的 running context |
| `getMeetingParticipants()` | 列出參與者 |
| `shareApp()` | 把 app 畫面分享給參與者 |
| `openUrl({ url })` | 在外部瀏覽器開啟 URL |
| `sendAppInvitation()` | 邀請使用者開啟你的 app |
| `authorize()` | 觸發 In-Client OAuth |
| `connect()` | 連接到其他 app 實例 |
| `postMessage()` | 傳訊息給已連接的實例 |
| `runRenderingContext()` | 啟動 Layers API（immersive/camera） |
| `expandApp({ action })` | 展開/收合 app 面板 |
| `showNotification()` | 在 Zoom 裡顯示通知 |

## Complete Documentation Library

### Core Concepts
- **[Architecture](concepts/architecture.md)** - 前後端模式、內嵌瀏覽器、deep linking、X-Zoom-App-Context
- **[Running Contexts](concepts/running-contexts.md)** - 所有 context、各 context 專屬的 API、多實例通訊
- **[Security](concepts/security.md)** - OWASP headers、CSP、cookie 安全、PKCE、token 儲存

### Complete Examples
- **[Quick Start](examples/quick-start.md)** - Hello World 的 Express + SDK app
- **[In-Client OAuth](examples/in-client-oauth.md)** - PKCE 授權流程
- **[Layers Immersive](examples/layers-immersive.md)** - 自訂視訊版面
- **[Camera Mode](examples/layers-camera.md)** - 虛擬鏡頭覆蓋層
- **[Collaborate Mode](examples/collaborate-mode.md)** - 參與者之間共用狀態
- **[Guest Mode](examples/guest-mode.md)** - 未驗證/已驗證/已授權的狀態
- **[Breakout Rooms](examples/breakout-rooms.md)** - 分組討論室偵測與跨房間狀態
- **[App Communication](examples/app-communication.md)** - 實例之間用 connect + postMessage 溝通

### Troubleshooting
- **[Common Issues](troubleshooting/common-issues.md)** - 快速診斷與錯誤碼
- **[Debugging](troubleshooting/debugging.md)** - 本機開發、ngrok、瀏覽器預覽
- **[Migration](troubleshooting/migration.md)** - SDK 版本升級筆記

### References
- **[API Reference](references/apis.md)** - 所有 100 多個 SDK 方法
- **[Events Reference](references/events.md)** - 所有 SDK 事件監聽器
- **[Layers API Reference](references/layers-api.md)** - 繪製與渲染方法
- **[OAuth Reference](references/oauth.md)** - Zoom Apps 的 OAuth 流程
- **[Zoom Mail](references/zmail-sdk.md)** - Mail plugin 整合

## Sample Repositories

### Official (by Zoom)

| Repository | Type | Last Updated | Status | SDK Version |
|-----------|------|-------------|--------|-------------|
| [zoomapps-sample-js](https://github.com/zoom/zoomapps-sample-js) | Hello World (Vanilla JS) | Dec 2025 | Active | ^0.16.26 |
| [zoomapps-advancedsample-react](https://github.com/zoom/zoomapps-advancedsample-react) | Advanced (React + Redis) | Oct 2025 | Active | 0.16.0 |
| [zoomapps-customlayout-js](https://github.com/zoom/zoomapps-customlayout-js) | Layers API | Nov 2023 | Stale | ^0.16.8 |
| [zoomapps-texteditor-vuejs](https://github.com/zoom/zoomapps-texteditor-vuejs) | Collaborate (Vue + Y.js) | Oct 2023 | Stale | ^0.16.7 |
| [zoomapps-serverless-vuejs](https://github.com/zoom/zoomapps-serverless-vuejs) | Serverless (Firebase) | Aug 2024 | Stale | ^0.16.21 |
| [zoomapps-cameramode-vuejs](https://github.com/zoom/zoomapps-cameramode-vuejs) | Camera Mode | - | - | - |
| [zoomapps-workshop-sample](https://github.com/zoom/zoomapps-workshop-sample) | Workshop | - | - | - |

**新專案建議：** 使用 `@zoom/appssdk` 版本 `^0.16.26`。

### Community

| Type | Repository | Description |
|------|------------|-------------|
| Library | [harvard-edtech/zaccl](https://github.com/harvard-edtech/zaccl) | Zoom App Complete Connection Library |

**完整清單**：請看 [general/references/community-repos.md](../general/references/community-repos.md)

### Learning Path

1. **起步**：`zoomapps-sample-js` - 最簡單、也最新
2. **進階**：`zoomapps-advancedsample-react` - 內容最完整（In-Client OAuth、Guest Mode、Collaborate）
3. **專項**：依功能挑選（Layers、Serverless、Camera Mode）

## Critical Gotchas (From Real Development)

### 1. Global Variable Conflict
CDN script 會定義 `window.zoomSdk`。在你的程式碼裡宣告 `let zoomSdk` 會造成 `SyntaxError: redeclaration of non-configurable global property`。請用 `let sdk = window.zoomSdk` 或 NPM import。

### 2. Domain Allowlist
你的 app URL **一定要**在 Marketplace 的 domain allowlist 裡。沒有的話，Zoom 會顯示空白面板，而且不會有任何錯誤。另外也要加入 `appssdk.zoom.us` 和你用到的任何 CDN 網域。

### 3. Capabilities Must Be Listed
只有列在 `config({ capabilities: [...] })` 裡的 API 才能用。呼叫沒列出的 API 會丟出錯誤。事件監聽器也一樣。

### 4. SDK Only Works Inside Zoom
在 Zoom client 外面呼叫 `zoomSdk.config()` 會丟出錯誤。一定要用 try/catch 包起來，並準備瀏覽器 fallback：
```javascript
try { await zoomSdk.config({...}); } catch { showBrowserPreview(); }
```

### 5. ngrok URL Changes
免費版 ngrok 的 URL 每次重啟都會變。你必須在 Marketplace 更新 4 個地方：Home URL、Redirect URL、OAuth Allow List、Domain Allow List。可以考慮買 ngrok 付費方案，拿固定的子網域。

### 6. In-Client OAuth vs Web OAuth
使用 `zoomSdk.authorize()`（In-Client）可以得到最好的 UX，不用瀏覽器 redirect。只有從 Marketplace 初次安裝時才改用 web redirect。

### 7. Camera Mode CEF Race Condition
Camera mode 使用 CEF，初始化需要時間。太早呼叫 `drawImage`/`drawWebView` 可能會失敗。請實作 exponential backoff 的重試。

### 8. Cookie Configuration
Zoom 的內嵌瀏覽器要求 cookie 設成 `SameSite=None` 和 `Secure=true`。沒設的話，session 會無聲壞掉。

### 9. State Validation
一定要驗證 OAuth 的 `state` 參數，防止 CSRF 攻擊。要產生密碼學等級的隨機 state、存起來，並在 callback 時比對。

## Resources

- **官方文件**：https://developers.zoom.us/docs/zoom-apps/
- **SDK 參考**：https://appssdk.zoom.us/
- **NPM 套件**：https://www.npmjs.com/package/@zoom/appssdk
- **開發者論壇**：https://devforum.zoom.us/
- **GitHub SDK 原始碼**：https://github.com/zoom/appssdk

---

**需要協助？** 先看下方的 Integrated Index 章節，裡面有完整的導覽。

---

## Integrated Index

_這個章節是從 `SKILL.md` 搬過來的。_

## Quick Start Path

**如果你是 Zoom Apps 新手，照這個順序：**

1. **先跑 preflight 檢查** -> [RUNBOOK.md](RUNBOOK.md)

2. **讀架構** -> [concepts/architecture.md](concepts/architecture.md)
   - 前後端模式、內嵌瀏覽器、deep linking
   - 了解 Zoom 怎麼載入你的 app、怎麼跟它溝通

3. **做出第一個 app** -> [examples/quick-start.md](examples/quick-start.md)
   - 完整的 Express + SDK Hello World
   - 本機開發的 ngrok 設定

4. **搞懂 running context** -> [concepts/running-contexts.md](concepts/running-contexts.md)
   - app 會在哪裡執行（inMeeting、inMainClient、inWebinar 等）
   - 各 context 專屬的 API 和限制

5. **實作 OAuth** -> [examples/in-client-oauth.md](examples/in-client-oauth.md)
   - 搭配 PKCE 的 In-Client OAuth（UX 最好）
   - Token 交換與儲存

6. **加功能** -> [references/apis.md](references/apis.md)
   - 依類別整理的 100 多個 SDK 方法
   - 每個都有程式碼範例

7. **排查問題** -> [troubleshooting/common-issues.md](troubleshooting/common-issues.md)
   - 常見問題的快速診斷

---

## Documentation Structure

```
zoom-apps-sdk/
├── SKILL.md                           # 主要 skill 總覽
├── SKILL.md                           # 就是這份檔案，導覽指南
│
├── concepts/                          # 核心架構模式
│   ├── architecture.md               # 前後端、內嵌瀏覽器、OAuth 流程
│   ├── running-contexts.md           # app 在哪裡執行 + 各 context 專屬的 API
│   └── security.md                   # OWASP headers、CSP、資料存取層
│
├── examples/                          # 完整可跑的程式碼
│   ├── quick-start.md                # Hello World，最小的 Express + SDK app
│   ├── in-client-oauth.md            # 搭配 PKCE 的 In-Client OAuth
│   ├── layers-immersive.md           # Layers API，immersive mode（自訂版面）
│   ├── layers-camera.md              # Layers API，camera mode（虛擬鏡頭）
│   ├── collaborate-mode.md           # Collaborate mode（共用狀態）
│   ├── guest-mode.md                 # Guest mode（未驗證 -> 已授權）
│   ├── breakout-rooms.md             # 分組討論室整合
│   └── app-communication.md          # 實例之間用 connect + postMessage
│
├── troubleshooting/                   # 問題排解指南
│   ├── common-issues.md              # 快速診斷、錯誤碼
│   ├── debugging.md                  # 本機開發設定、ngrok、瀏覽器預覽
│   └── migration.md                  # SDK 版本遷移筆記
│
└── references/                        # 參考文件
    ├── apis.md                        # 完整 API 參考（100 多個方法）
    ├── events.md                      # 所有 SDK 事件
    ├── layers-api.md                  # Layers API 詳細參考
    ├── oauth.md                       # Zoom Apps 的 OAuth 流程
    └── zmail-sdk.md                   # Zoom Mail 整合
```

---

## By Use Case

### I want to build a basic Zoom App
1. [Architecture](concepts/architecture.md) - 了解整體模式
2. [Quick Start](examples/quick-start.md) - 做出 Hello World
3. [In-Client OAuth](examples/in-client-oauth.md) - 加上授權
4. [Security](concepts/security.md) - 必要的 headers

### I want immersive video layouts (Layers API)
1. [Layers Immersive](examples/layers-immersive.md) - 自訂視訊位置
2. [Layers API Reference](references/layers-api.md) - 所有繪製方法
3. [App Communication](examples/app-communication.md) - 在參與者之間同步版面

### I want a virtual camera overlay
1. [Camera Mode](examples/layers-camera.md) - Camera mode 渲染
2. [Layers API Reference](references/layers-api.md) - 繪製方法

### I want real-time collaboration
1. [Collaborate Mode](examples/collaborate-mode.md) - 共用狀態 API
2. [App Communication](examples/app-communication.md) - 實例之間傳訊

### I want guest/anonymous access
1. [Guest Mode](examples/guest-mode.md) - 三種授權狀態
2. [In-Client OAuth](examples/in-client-oauth.md) - promptAuthorize 流程

### I want breakout room support
1. [Breakout Rooms](examples/breakout-rooms.md) - 討論室偵測與狀態同步

### I want to sync between main client and meeting
1. [App Communication](examples/app-communication.md) - connect + postMessage
2. [Running Contexts](concepts/running-contexts.md) - 多實例的行為

### I want serverless deployment
1. [Quick Start](examples/quick-start.md) - 先了解基本模式
2. 範例：[zoomapps-serverless-vuejs](https://github.com/zoom/zoomapps-serverless-vuejs) - Firebase 做法

### I want to add Zoom Mail integration
1. [Zoom Mail Reference](references/zmail-sdk.md) - REST API + mail plugin

### I'm getting errors
1. [Common Issues](troubleshooting/common-issues.md) - 快速診斷表
2. [Debugging](troubleshooting/debugging.md) - 本機開發設定、DevTools
3. [Migration](troubleshooting/migration.md) - 版本相容性

---

## Most Critical Documents

### 1. Architecture (FOUNDATION)
**[concepts/architecture.md](concepts/architecture.md)**

搞懂 Zoom Apps 怎麼運作：前端在內嵌瀏覽器裡跑，後端處理 OAuth/API，SDK 是中間的橋。沒搞懂這個，其他東西都看不懂。

### 2. Quick Start (FIRST APP)
**[examples/quick-start.md](examples/quick-start.md)**

完整可跑的程式碼。先讓東西跑起來，再去看進階功能。

### 3. Common Issues (MOST COMMON PROBLEMS)
**[troubleshooting/common-issues.md](troubleshooting/common-issues.md)**

九成的 Zoom Apps 問題都是這三種：domain allowlist、全域變數衝突，或缺少 capability。

---

## Key Learnings

### Critical Discoveries:

1. **Global Variable Conflict is the #1 Gotcha**
   - CDN script 會在全域定義 `window.zoomSdk`
   - `let zoomSdk = ...` 會在 Zoom 的瀏覽器裡造成 SyntaxError
   - 用 `let sdk = window.zoomSdk` 或 NPM import

2. **Domain Allowlist is Non-Negotiable**
   - 網域沒進白名單，app 會顯示空白面板，完全沒有錯誤
   - 必須包含你的網域、`appssdk.zoom.us`，以及任何 CDN 網域
   - ngrok URL 重啟就會變，每次都要去 Marketplace 更新

3. **config() Gates Everything**
   - 一定要最先呼叫，而且要列出所有 capability
   - 沒列出的 capability 會丟出錯誤
   - 檢查 `unsupportedApis` 確認 client 版本相容

4. **In-Client OAuth > Web OAuth for UX**
   - `authorize()` 讓使用者留在 Zoom 裡（沒有瀏覽器 redirect）
   - 只有從 Marketplace 初次安裝才需要 web redirect
   - 一定要實作 PKCE（code_verifier + code_challenge）

5. **Two App Instances Can Run Simultaneously**
   - 主 client 實例 + 會議實例
   - 用 `connect()` + `postMessage()` 讓兩邊同步
   - 會前設定在主 client 做，會議中使用

6. **Camera Mode Has CEF Quirks**
   - CEF 初始化需要時間
   - 太早呼叫 draw 可能會失敗
   - 用 exponential backoff 重試

7. **Cookie Settings Matter**
   - 必須設定 `SameSite=None` + `Secure=true`
   - 沒設的話，session 在內嵌瀏覽器裡會無聲失敗

---

## Quick Reference

### "App shows blank panel"
-> [Domain Allowlist](troubleshooting/common-issues.md) - 把網域加到 Marketplace

### "SyntaxError: redeclaration"
-> [Global Variable](troubleshooting/common-issues.md) - 用 `let sdk = window.zoomSdk`

### "config() throws error"
-> [Browser Preview](troubleshooting/debugging.md) - SDK 只能在 Zoom 裡面運作

### "API call fails silently"
-> [OAuth Scopes](troubleshooting/common-issues.md) - 在 Marketplace 加入需要的 scope

### "How do I implement [feature]?"
-> [API Reference](references/apis.md) - 找到對應的方法，確認需要的 capability

### "How do I test locally?"
-> [Debugging Guide](troubleshooting/debugging.md) - ngrok + Marketplace 設定

---

## Document Version

基於 **@zoom/appssdk v0.16.x**（最新：0.16.26+）

---

**Happy coding!**

先看 [Architecture](concepts/architecture.md) 搞懂整體模式，再看 [Quick Start](examples/quick-start.md) 做出第一個 app。
