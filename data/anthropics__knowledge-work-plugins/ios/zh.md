---
name: contact-center/ios
description: "Zoom Contact Center SDK for iOS。用於原生 iOS 的聊天、視訊、ZVA、預約回電整合，app 生命週期橋接、重新加入流程，以及回電處理。"
user-invocable: false
triggers:
  - "contact center ios"
  - "zcc ios"
  - "zoomccinterface ios"
  - "handleRejoinVideoOpenURL"
  - "zoomccservicedelegate"
  - "scheduled callback ios"
---

# Zoom Contact Center SDK - iOS

官方文件：
- https://developers.zoom.us/docs/contact-center/ios/
- https://marketplacefront.zoom.us/sdk/contact/ios/index.html

## 快速連結

1. [concepts/sdk-lifecycle.md](concepts/sdk-lifecycle.md)
2. [examples/service-patterns.md](examples/service-patterns.md)
3. [references/ios-reference-map.md](references/ios-reference-map.md)
4. [troubleshooting/common-issues.md](troubleshooting/common-issues.md)

## SDK 介面摘要

- Manager：`ZoomCCInterface.sharedInstance()`
- Context：`ZoomCCContext`
- Items：`ZoomCCItem`
- Services：
- `chatService`
- `zvaService`
- `videoService`
- `scheduledCallbackService`

## 硬性護欄

- 在進行任何 channel 操作之前，先設定 `ZoomCCContext`。
- 轉發 app 生命週期的呼叫（`appDidBecomeActive`、`appDidEnterBackgroud`、`appWillResignActive`、`appWillTerminate`）。
- channel 用 item 為基礎的方式初始化。
- 重新加入的 URL 處理要接到 video service 的路徑上。

## 常見的串接

- Zoom 用戶端裡的 Contact Center app：[../../zoom-apps-sdk/SKILL.md](../../zoom-apps-sdk/SKILL.md)
- OAuth 和身分：[../../oauth/SKILL.md](../../oauth/SKILL.md)

## 營運

- [RUNBOOK.md](RUNBOOK.md)：5 分鐘的事前檢查和除錯檢查清單。
