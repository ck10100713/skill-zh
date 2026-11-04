---
name: build-zoom-meeting-app
description: 建置或嵌入 Zoom 會議流程。當實作 Meeting SDK 加入會議、網頁或行動裝置的會議嵌入、會議生命週期流程，或要在 Meeting SDK 和 Video SDK 之間做選擇時使用。
---

# /build-zoom-meeting-app

這個 skill 用在嵌入式會議體驗和會議生命週期的實作。

## 涵蓋範圍

- Meeting SDK 的選擇與平台導向
- 加入與驗證的實作規劃
- 會議建立加上加入流程的設計
- 網頁與原生平台的考量
- Meeting SDK 與 Video SDK 的界線判斷

## 工作流程

1. 確認使用者要的是 Zoom 會議，還是自訂的視訊 session。
2. 如果使用者需要真正的 Zoom 會議，導向 Meeting SDK。
3. 引入相關的平台參考資料。
4. 只在建立會議、資源管理或報表時才加上 REST API。
5. 只有使用情境明確需要時，才加上 webhooks 或 RTMS。

## 主要參考

- [meeting-sdk](../meeting-sdk/SKILL.md)
- [rest-api](../rest-api/SKILL.md)
- [webhooks](../webhooks/SKILL.md)
- [rtms](../rtms/SKILL.md)
- [video-sdk](../video-sdk/SKILL.md)

## 常見錯誤

- 用 Video SDK 做一般的 Zoom 會議嵌入
- 沒有理由就把資源管理 API 混進核心的加入流程
- 拖到太晚才處理各平台 SDK 的限制
