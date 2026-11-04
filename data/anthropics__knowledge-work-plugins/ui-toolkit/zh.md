---
name: ui-toolkit/web
description: "Zoom Video SDK UI Toolkit 的參考 skill。導向 web 影片工作流程之後，想用現成的 React UI，而不是自己從頭做完整的 Video SDK 介面時使用。"
user-invocable: false
triggers:
  - "ui toolkit"
  - "zoom ui"
  - "prebuilt video ui"
  - "video conferencing ui"
  - "zoom video ui toolkit"
  - "uitoolkit"
  - "ready-made zoom ui"
---

# Zoom Video SDK UI Toolkit

web 版預建 Zoom Video SDK UI Toolkit 的背景參考。如果使用者可能其實需要的是 Meeting SDK，請先用 `choose-zoom-approach`。

**官方文件**：https://developers.zoom.us/docs/video-sdk/web/ui-toolkit/
**API 參考**：https://marketplacefront.zoom.us/sdk/uitoolkit/web/
**NPM 套件**：https://www.npmjs.com/package/@zoom/videosdk-zoom-ui-toolkit
**線上 Demo**：https://sdk.zoom.com/videosdk-uitoolkit

## 快速連結

**第一次用 UI Toolkit？照這條路走：**

1. **Quick Start** - 5 分鐘跑起來（見下方）
2. **JWT Authentication** - server 端產生 token（必要）
3. **Composite vs Components** - 選擇你的做法  
4. **Framework Integration** - React、Vue、Angular、Next.js 的寫法
5. **Integrated Index** - 見本檔案下方的段落

**遇到問題？**
- Session 加入不了 → 檢查 JWT Authentication（最常見的原因）
- React 18 peer dependency 錯誤 → 看 Installation 一節
- CSS 沒載入 → 看 [Troubleshooting](troubleshooting/common-issues.md)
- 元件沒顯示 → 檢查 Component Lifecycle
- 先做 preflight 檢查 → [5-Minute Runbook](RUNBOOK.md)

## 概覽

Zoom Video SDK UI Toolkit 是一個**預建的影片 UI 函式庫**，用很少的程式碼就能 render 出完整的視訊會議體驗。跟原始的 Video SDK 不同，UI Toolkit 提供：

- ✅ **現成可用的 UI** - 開箱即有專業的視訊介面
- ✅ **零 UI 程式碼** - 不用自己做影片版面、控制列或參與者管理
- ✅ **不限框架** - 支援 React、Vue、Angular、Next.js、vanilla JS
- ✅ **高度可客製** - 選擇要啟用哪些功能、客製主題
- ✅ **內建功能** - 包含聊天、螢幕分享、設定、虛擬背景

**什麼時候用 UI Toolkit：**
- 你想快速拿到完整的視訊方案
- 你需要跟 Zoom 一致的 UI
- 你不想自己做影片 UI
- 你需要標準功能（聊天、分享、參與者）

**什麼時候改用原始 Video SDK：**
- 你需要完全控制 UI
- 你在做非標準的視訊體驗
- 你需要存取原始的影像/音訊資料
- 你想自己做 rendering pipeline

## 安裝

```bash
npm install @zoom/videosdk-zoom-ui-toolkit jsrsasign
npm install -D @types/jsrsasign
```

**注意**：React 的支援依 UI Toolkit 版本而定。請看你安裝的版本的 peer dependencies（通常需要 React 18）。

## Quick Start

### 基本用法（Vanilla JS）

```javascript
import uitoolkit from "@zoom/videosdk-zoom-ui-toolkit";
import "@zoom/videosdk-ui-toolkit/dist/videosdk-zoom-ui-toolkit.css";

const container = document.getElementById("sessionContainer");

const config = {
  videoSDKJWT: "your_jwt_token",
  sessionName: "my-session",
  userName: "John Doe",
  sessionPasscode: "",
  features: ["video", "audio", "share", "chat", "users", "settings"],
};

uitoolkit.joinSession(container, config);

uitoolkit.onSessionJoined(() => {
  console.log("Session joined");
});

uitoolkit.onSessionClosed(() => {
  console.log("Session closed");
});
```

### Next.js / React 整合

```typescript
'use client';

import { useEffect, useRef } from 'react';

export default function VideoSession({ jwt, sessionName, userName }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const uitoolkitRef = useRef<any>(null);

  useEffect(() => {
    let isMounted = true;

    const init = async () => {
      const uitoolkitModule = await import('@zoom/videosdk-zoom-ui-toolkit');
      const uitoolkit = uitoolkitModule.default;
      uitoolkitRef.current = uitoolkit;
      
      // 如果 TypeScript 對 CSS import 報錯，請設定你的 app 允許它們
      // （例如用全域的 `declare module \"*.css\";`），或是改從
      // 全域進入點（Next.js layout/_app）import CSS，不要在這裡 inline。
      await import('@zoom/videosdk-ui-toolkit/dist/videosdk-zoom-ui-toolkit.css');

      if (!isMounted || !containerRef.current) return;

      const config: any = {
        videoSDKJWT: jwt,
        sessionName: sessionName,
        userName: userName,
        sessionPasscode: '',
        features: ['video', 'audio', 'share', 'chat', 'users', 'settings'],
      };

      uitoolkit.joinSession(containerRef.current, config);
      uitoolkit.onSessionJoined(() => console.log('Joined'));
      uitoolkit.onSessionClosed(() => console.log('Closed'));
    };

    init();

    return () => {
      isMounted = false;
      if (uitoolkitRef.current && containerRef.current) {
        try {
          uitoolkitRef.current.closeSession(containerRef.current);
        } catch (e) {}
      }
    };
  }, [jwt, sessionName, userName]);

  return <div ref={containerRef} style={{ width: '100%', height: '100vh' }} />;
}
```

## 可用功能

| 功能 | 說明 |
|---------|-------------|
| `video` | 啟用影片版面，並傳送/接收影片 |
| `audio` | 顯示音訊按鈕，傳送/接收音訊 |
| `share` | 螢幕分享 |
| `chat` | session 內的訊息 |
| `users` | 參與者列表 |
| `settings` | 裝置選擇、虛擬背景 |
| `preview` | 加入前的鏡頭/麥克風預覽 |
| `recording` | 雲端錄影（付費方案） |
| `leave` | 離開/結束 session 按鈕 |

## 疑難排解

- **[troubleshooting/common-issues.md](troubleshooting/common-issues.md)** - CSS、SSR、JWT/session 加入、客製化限制

## JWT Token 產生（Server 端）

**必要**：JWT token 一定要在你的 server 上產生，絕對不要把 SDK secret 暴露在 client 端。

### Node.js / Next.js API Route

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { KJUR } from 'jsrsasign';

const ZOOM_VIDEO_SDK_KEY = process.env.ZOOM_VIDEO_SDK_KEY;
const ZOOM_VIDEO_SDK_SECRET = process.env.ZOOM_VIDEO_SDK_SECRET;

export async function POST(request: NextRequest) {
  const { sessionName, role, userName } = await request.json();

  if (!sessionName || role === undefined) {
    return NextResponse.json({ error: 'Missing params' }, { status: 400 });
  }

  const iat = Math.floor(Date.now() / 1000);
  const exp = iat + 60 * 60 * 2; // 2 小時

  const oHeader = { alg: 'HS256', typ: 'JWT' };
  const oPayload = {
    app_key: ZOOM_VIDEO_SDK_KEY,
    role_type: role, // 0 = 參與者, 1 = 主持人
    tpc: sessionName,
    version: 1,
    iat,
    exp,
    user_identity: userName || 'User',
  };

  const signature = KJUR.jws.JWS.sign(
    'HS256',
    JSON.stringify(oHeader),
    JSON.stringify(oPayload),
    ZOOM_VIDEO_SDK_SECRET
  );

  return NextResponse.json({ signature });
}
```

### JWT Payload 欄位

| 欄位 | 必填 | 說明 |
|-------|----------|-------------|
| `app_key` | 是 | 你的 Video SDK Key |
| `role_type` | 是 | 0 = 參與者, 1 = 主持人 |
| `tpc` | 是 | Session/topic 名稱 |
| `version` | 是 | 固定為 1 |
| `iat` | 是 | 簽發時間（Unix timestamp） |
| `exp` | 是 | 到期時間（Unix timestamp） |
| `user_identity` | 否 | 使用者識別 |

## API 參考

### 核心方法

```javascript
uitoolkit.joinSession(container, config);
uitoolkit.closeSession(container);
```

### 事件監聽

```javascript
uitoolkit.onSessionJoined(callback);
uitoolkit.onSessionClosed(callback);
uitoolkit.offSessionJoined(callback);
uitoolkit.offSessionClosed(callback);
```

### 元件方法

```javascript
uitoolkit.showChatComponent(container);
uitoolkit.hideChatComponent(container);
uitoolkit.showUsersComponent(container);
uitoolkit.hideUsersComponent(container);
uitoolkit.showControlsComponent(container);
uitoolkit.hideControlsComponent(container);
uitoolkit.showSettingsComponent(container);
uitoolkit.hideSettingsComponent(container);
uitoolkit.hideAllComponents();
```

## CDN 用法（不需要 build）

```html
<link rel="stylesheet" href="https://source.zoom.us/uitoolkit/2.3.5-1/videosdk-zoom-ui-toolkit.css" />
<script src="https://source.zoom.us/uitoolkit/2.3.5-1/videosdk-zoom-ui-toolkit.min.umd.js"></script>

<div id="sessionContainer"></div>

<script>
  const uitoolkit = window.UIToolkit;
  
  uitoolkit.joinSession(document.getElementById('sessionContainer'), {
    videoSDKJWT: 'your_jwt',
    sessionName: 'my-session',
    userName: 'User',
    features: ['video', 'audio', 'chat']
  });
</script>
```

## 搭配 basePath 的 Next.js

把 Next.js deploy 在子路徑底下時：

```typescript
// next.config.ts
const nextConfig = {
  basePath: "/your-app-path",
  assetPrefix: "/your-app-path",
};
```

呼叫 API route 時用完整路徑：
```typescript
fetch('/your-app-path/api/token', { ... })
```

## 先決條件

1. 從 [Zoom Marketplace](https://marketplace.zoom.us/) 取得 **Zoom Video SDK 憑證**
2. **React** 版本要跟你安裝的 UI Toolkit 套件相容（看 peer deps，React 18 很常見）
3. **Server 端產生 JWT**（絕對不要暴露 SDK secret）
4. 支援 WebRTC 的**現代瀏覽器**

## 瀏覽器支援

| 瀏覽器 | 版本 |
|---------|---------|
| Chrome | 78+ |
| Firefox | 76+ |
| Safari | 14.1+ |
| Edge | 79+ |

## 常見問題

| 問題 | 解法 |
|-------|----------|
| `peer react@"^18.0.0"` 錯誤 | 使用你安裝的 UI Toolkit 套件要求的 React 版本（看 peer deps，React 18 很常見） |
| CSS import 的 TypeScript 錯誤 | 設定 TS/CSS 的處理方式（優先用全域的 `*.css` module 宣告）；除了用完即丟的 demo，避免用 `@ts-ignore` |
| Config 型別錯誤 | 把 config 的型別設成 `any` |
| API 回傳 HTML 而不是 JSON | 檢查 fetch URL 裡的 basePath |

## 資源

- **GitHub**: https://github.com/zoom/videosdk-zoom-ui-toolkit-web
- **UI Toolkit 文件**: https://developers.zoom.us/docs/video-sdk/web/ui-toolkit/
- **Auth Endpoint 範例**: https://github.com/zoom/videosdk-auth-endpoint-sample
- **Marketplace**: https://marketplace.zoom.us/

---

## 整合索引

_這一節是從 `SKILL.md` 遷移過來的。_

UI Toolkit 所有文件的完整導覽。

## 📚 從這裡開始

第一次用 UI Toolkit？照這條學習路徑：

1. **[SKILL.md](SKILL.md)** - 主要概覽與 quick start
2. **[5-Minute Runbook](RUNBOOK.md)** - 深入除錯前先做的 preflight 檢查
3. **Quick Start Guide** - 5 分鐘內拿到可跑的程式碼（見 skill.md）
4. **JWT Authentication** - server 端產生 token（見 skill.md）
5. **Choose Your Mode** - Composite vs Components（見 skill.md）

## 🎯 核心概念

了解 UI Toolkit 怎麼運作：

- **Composite vs Components** - 使用 UI Toolkit 的兩種方式（見 skill.md）
- **UI Toolkit Architecture** - 它內部怎麼包裝 Video SDK
- **Feature Configuration** - 了解 featuresOptions 的結構
- **Session Lifecycle** - Join → Active → Leave/Close → Destroy 的流程

## 📖 完整指南

### 入門
- **Installation** - NPM 安裝與 React 18 設定（見 skill.md）
- **Quick Start - Composite** - 一個 container 裡放完整 UI（見 skill.md）
- **Quick Start - Components** - 個別的 UI 元件（見 skill.md）
- **JWT Authentication** - server 端產生 token（見 skill.md）

### 框架整合
- **React Integration** - Hooks、useEffect 寫法（見 skill.md）
- **Vue.js Integration** - Composition API 與 Options API（見 skill.md）
- **Angular Integration** - 元件生命週期（見 skill.md）
- **Next.js Integration** - App Router、Server Components（見 skill.md）
- **Vanilla JavaScript** - 不用框架的用法（見 skill.md）

### 進階主題
- **Component Lifecycle** - mount、unmount、cleanup 的寫法
- **Event Listeners** - 回應 session 事件
- **Session Management** - 用程式控制
- **Quality Statistics** - 監控連線品質
- **Custom Themes** - 主題客製化
- **Virtual Backgrounds** - 自訂背景圖片

## 📚 API 參考

完整的 API 文件：

- **核心方法**（見 skill.md）
  - `joinSession()` - 開始影片 session
  - `closeSession()` - 結束 session 並移除 UI
  - `destroy()` - 清理 UI Toolkit instance
  - `leaveSession()` - 離開但不銷毀 UI

- **元件方法**（見 skill.md）
  - `showControlsComponent()` - 顯示控制列
  - `showChatComponent()` - 顯示聊天面板
  - `showUsersComponent()` - 顯示參與者列表
  - `showSettingsComponent()` - 顯示設定面板
  - `hideAllComponents()` - 隱藏所有元件

- **事件監聽**（見 skill.md）
  - `onSessionJoined()` - 成功加入 session
  - `onSessionClosed()` - Session 結束
  - `onSessionDestroyed()` - UI Toolkit 已銷毀
  - `onViewTypeChange()` - 檢視模式改變
  - `on()` - 訂閱 Video SDK 事件
  - `off()` - 取消訂閱事件

- **資訊方法**（見 skill.md）
  - `getSessionInfo()` - 取得 session 詳細資料
  - `getCurrentUserInfo()` - 取得目前使用者
  - `getAllUser()` - 取得所有參與者
  - `getClient()` - 取得底層的 Video SDK client
  - `version()` - 取得版本資訊

- **控制方法**（見 skill.md）
  - `changeViewType()` - 切換檢視模式
  - `mirrorVideo()` - 鏡像自己的影像
  - `isSupportCustomLayout()` - 檢查裝置支援

- **統計方法**（見 skill.md）
  - `subscribeAudioStatisticData()` - 音訊品質統計
  - `subscribeVideoStatisticData()` - 影像品質統計
  - `subscribeShareStatisticData()` - 分享品質統計

## 🔧 設定

- **Feature Configuration**（見 skill.md）
  - `featuresOptions` 結構
  - 音訊/影像選項
  - 聊天、使用者、設定
  - 虛擬背景
  - 錄影、字幕（付費功能）
  - 主題客製化
  - 檢視模式

- **Session Configuration**（見 skill.md）
  - 必填：`videoSDKJWT`、`sessionName`、`userName`
  - 選填：`sessionPasscode`、`sessionIdleTimeoutMins`
  - Debug 模式
  - Web endpoint
  - 語言設定

## ⚠️ 疑難排解

### 常見問題
- React 18 peer dependency 錯誤
- JWT token 無效
- CSS 沒載入
- 元件沒顯示
- Session 加入失敗

見：**[troubleshooting/common-issues.md](troubleshooting/common-issues.md)**

### 各框架的問題
- React：SSR、hydration、cleanup
- Vue：reactivity、生命週期
- Angular：module import、AOT
- Next.js：App Router、basePath

### Session 問題
- 驗證失敗
- 連線問題
- 影像/音訊不能用
- 螢幕分享問題

## 📦 範例應用程式

**官方 Repo**：

| 框架 | Repository | 重點功能 |
|-----------|------------|--------------|
| React | [videosdk-zoom-ui-toolkit-react-sample](https://github.com/zoom/videosdk-zoom-ui-toolkit-react-sample) | Hooks、TypeScript |
| Vue.js | [videosdk-zoom-ui-toolkit-vuejs-sample](https://github.com/zoom/videosdk-zoom-ui-toolkit-vuejs-sample) | Composition API |
| Angular | [videosdk-zoom-ui-toolkit-angular-sample](https://github.com/zoom/videosdk-zoom-ui-toolkit-angular-sample) | Services、Guards |
| JavaScript | [videosdk-zoom-ui-toolkit-javascript-sample](https://github.com/zoom/videosdk-zoom-ui-toolkit-javascript-sample) | Vanilla JS |
| Auth Endpoint | [videosdk-auth-endpoint-sample](https://github.com/zoom/videosdk-auth-endpoint-sample) | Node.js JWT |

## 🌐 外部資源

- **官方文件**: https://developers.zoom.us/docs/video-sdk/web/ui-toolkit/
- **API 參考**: https://marketplacefront.zoom.us/sdk/uitoolkit/web/
- **NPM 套件**: https://www.npmjs.com/package/@zoom/videosdk-zoom-ui-toolkit
- **Marketplace**: https://marketplace.zoom.us/
- **開發者論壇**: https://devforum.zoom.us/
- **線上 Demo**: https://sdk.zoom.com/videosdk-uitoolkit
- **Changelog**: https://developers.zoom.us/changelog/ui-toolkit/web/

## 🎓 學習路徑

### 初學者
1. 讀 [SKILL.md](SKILL.md) 的概覽
2. 照著做 Quick Start - Composite
3. 在 server 上產生 JWT
4. 加入你的第一個 session
5. 探索可用的功能

### 中階
1. 試試 Component 模式
2. 加上事件監聽
3. 客製主題
4. 加上虛擬背景
5. 跟你的框架整合

### 進階
1. 存取底層的 Video SDK
2. 訂閱品質統計
3. 處理所有 edge case
4. 實作自訂版面
5. 做出可上 production 的 app

## 📋 快速參考卡

### 最小可執行範例

```javascript
import uitoolkit from "@zoom/videosdk-zoom-ui-toolkit";
import "@zoom/videosdk-ui-toolkit/dist/videosdk-zoom-ui-toolkit.css";

const config = {
  videoSDKJWT: "YOUR_JWT",
  sessionName: "test-session",
  userName: "User",
  featuresOptions: {
    video: { enable: true },
    audio: { enable: true }
  }
};

uitoolkit.joinSession(document.getElementById("container"), config);
uitoolkit.onSessionJoined(() => console.log("Joined"));
uitoolkit.onSessionClosed(() => uitoolkit.destroy());
```

### 一定要記住的規則

1. ✅ **一律**在 server 端產生 JWT
2. ✅ **一律**在 cleanup 時呼叫 `destroy()`
3. ✅ **一律**用 React 18（不是 17/19）
4. ✅ **一律**import CSS 檔
5. ❌ **絕對不要**把 SDK secret 暴露在 client 端
6. ❌ **絕對不要**略過 `onSessionClosed` 的 cleanup
7. ❌ **絕對不要**在 `joinSession` 之前呼叫元件

## 📞 支援

- **開發者論壇**: https://devforum.zoom.us/
- **開發者支援**: https://developers.zoom.us/support/
- **Premier Support**: https://explore.zoom.us/en/support-plans/developer/

---

**導覽**：[← 回到 SKILL.md](SKILL.md)

## 環境變數

- 標準化的 `.env` key，以及每個值要去哪裡找，請看 [references/environment-variables.md](references/environment-variables.md)。
