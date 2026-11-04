---
name: contact-center/android
description: "Zoom Contact Center SDK for Android。用於原生 Android 的聊天／視訊／ZVA／預約回電整合、campaign 模式、服務生命週期，以及重新加入（rejoin）的處理。"
user-invocable: false
triggers:
  - "contact center android"
  - "zcc android"
  - "zoomccinterface android"
  - "zoomccchatservice"
  - "zoomccvideoservice"
  - "releasezoomccservice"
  - "android rejoin"
---

# Zoom Contact Center SDK - Android

官方文件：
- https://developers.zoom.us/docs/contact-center/android/
- https://marketplacefront.zoom.us/sdk/contact/android/index.html

## 快速連結

1. [concepts/sdk-lifecycle.md](concepts/sdk-lifecycle.md)
2. [examples/service-patterns.md](examples/service-patterns.md)
3. [references/android-reference-map.md](references/android-reference-map.md)
4. [troubleshooting/common-issues.md](troubleshooting/common-issues.md)

## SDK 介面摘要

- SDK 管理器：`ZoomCCInterface`
- 管道服務（Channel services）：
- `getZoomCCChatService()`
- `getZoomCCVideoService()`
- `getZoomCCZVAService()`
- `getZoomCCScheduledCallbackService()`
- Campaign 支援透過 web campaign service 和 campaign metadata。

## 硬性護欄

- 在 `Application.onCreate` 初始化 SDK。
- 用 `ZoomCCItem` 定義管道和識別碼。
- 聊天／視訊／ZVA 用 `entryId`。
- 預約回電和 campaign 模式用 `apiKey`。
- 結束時要釋放服務。

## 常見串接

- Contact Center app 與互動 context：[../../zoom-apps-sdk/SKILL.md](../../zoom-apps-sdk/SKILL.md)
- Contact Center API 自動化：[../../rest-api/SKILL.md](../../rest-api/SKILL.md)

## 維運

- [RUNBOOK.md](RUNBOOK.md)：5 分鐘的啟動前檢查和除錯清單。
