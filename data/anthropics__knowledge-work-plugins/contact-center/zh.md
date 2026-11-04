---
name: build-zoom-contact-center-app
description: "Zoom Contact Center 的參考 skill。在導向某個 contact-center 工作流程之後使用，適用於實作 app、web 或原生整合；engagement context 與狀態處理；campaign；callback；或版本漂移的疑難排解。"
triggers:
  - "contact center sdk"
  - "zoom contact center"
  - "zcc"
  - "engagement context"
  - "engagement status"
  - "campaign sdk"
  - "scheduled callback"
  - "getengagementcontext"
  - "onengagementstatuschange"
  - "zoom contact center app"
---

# /build-zoom-contact-center-app

Zoom Contact Center 整合的背景參考，涵蓋 app、web 和原生行動裝置三種介面。

Zoom Contact Center 的實作指引，涵蓋：
- Zoom client 裡的 Contact Center app（Zoom Apps SDK 路線）
- Web 管道嵌入（chat/video/campaign）
- 原生行動 SDK（Android/iOS）

官方文件：
- https://developers.zoom.us/docs/contact-center/
- https://developers.zoom.us/docs/contact-center/web/sdk-reference/
- https://marketplacefront.zoom.us/sdk/contact/android/index.html
- https://marketplacefront.zoom.us/sdk/contact/ios/index.html

## 路由護欄

- 如果使用者要在 Zoom Contact Center 桌面 client 裡做 app，就留在 Zoom Apps SDK 路線，使用這個 skill 加上 `zoom-apps-sdk`。
- 如果使用者要在網站上嵌入 chat/video 小工具，導向 [web/SKILL.md](web/SKILL.md)。
- 如果使用者要整合原生 Android 或 iOS 的 SDK 二進位檔，導向 [android/SKILL.md](android/SKILL.md) 或 [ios/SKILL.md](ios/SKILL.md)。
- 如果使用者需要 Contact Center 的通話控制或佇列 API，銜接 [../rest-api/SKILL.md](../rest-api/SKILL.md)。

## 快速連結

從這裡開始：
1. [concepts/architecture-and-lifecycle.md](concepts/architecture-and-lifecycle.md)
2. [scenarios/high-level-scenarios.md](scenarios/high-level-scenarios.md)
3. [references/forum-top-questions.md](references/forum-top-questions.md)
4. [references/versioning-and-compatibility.md](references/versioning-and-compatibility.md)
5. [references/samples-validation.md](references/samples-validation.md)
6. [references/environment-variables.md](references/environment-variables.md)
7. [troubleshooting/common-drift-and-breaks.md](troubleshooting/common-drift-and-breaks.md)
8. [RUNBOOK.md](RUNBOOK.md)

各平台的 skill：
- [android/SKILL.md](android/SKILL.md)
- [ios/SKILL.md](ios/SKILL.md)
- [web/SKILL.md](web/SKILL.md)

## 文件結構

```
contact-center/
├── SKILL.md
├── RUNBOOK.md
├── concepts/
│   └── architecture-and-lifecycle.md
├── scenarios/
│   └── high-level-scenarios.md
├── references/
│   ├── versioning-and-compatibility.md
│   ├── samples-validation.md
│   └── environment-variables.md
├── troubleshooting/
│   └── common-drift-and-breaks.md
├── android/
│   ├── SKILL.md
│   ├── concepts/sdk-lifecycle.md
│   ├── examples/service-patterns.md
│   ├── references/android-reference-map.md
│   └── troubleshooting/common-issues.md
├── ios/
│   ├── SKILL.md
│   ├── concepts/sdk-lifecycle.md
│   ├── examples/service-patterns.md
│   ├── references/ios-reference-map.md
│   └── troubleshooting/common-issues.md
└── web/
    ├── SKILL.md
    ├── concepts/lifecycle-and-events.md
    ├── examples/app-context-and-state.md
    ├── references/web-reference-map.md
    └── troubleshooting/common-issues.md
```

## 常見的生命週期模式

1. 及早初始化平台 context。
2. 建立管道項目（chat/video/ZVA 用 `entryId`，scheduled callback 和 campaign 流程用 `apiKey`）。
3. 取得 service/client 實例。
4. 在使用者互動之前註冊 listener/delegate。
5. 啟動流程（`fetchUI`、`startVideo`，或 web SDK 的 open/show 路徑）。
6. 處理 engagement 狀態變化（`start`、`hold`、`resume`、`end`）和 context 切換。
7. 結束流程並釋放資源（`endChat`/`endVideo`、`logout/logoff`、uninitialize/release）。

## 高階情境

- 座席側邊面板 app：依 `engagementId` 儲存備註，且在 context 切換後仍然保留。
- 從網頁標籤啟動的瀏覽器 chat/video campaign。
- 原生行動客戶 app，支援 chat/video/scheduled callback。
- 由 campaign 驅動的管道選擇（chat、ZVA、video、scheduled callback）。
- 行動裝置上斷線的 video engagement 重新加入流程。
- 使用 postMessage 事件契約的 Smart Embed CRM 軟電話。

詳情請見 [scenarios/high-level-scenarios.md](scenarios/high-level-scenarios.md)。

## 銜接

- 驗證與 client 內的 app 身分：[../zoom-apps-sdk/SKILL.md](../zoom-apps-sdk/SKILL.md) 和 [../oauth/SKILL.md](../oauth/SKILL.md)
- Contact Center REST 工作流程：[../rest-api/SKILL.md](../rest-api/SKILL.md)
- Web 語音／聊天管道上的 cobrowse：[../cobrowse-sdk/SKILL.md](../cobrowse-sdk/SKILL.md)

## 環境變數

- 標準化的 `.env` key，以及各個值要去哪裡找，請見 [references/environment-variables.md](references/environment-variables.md)。
