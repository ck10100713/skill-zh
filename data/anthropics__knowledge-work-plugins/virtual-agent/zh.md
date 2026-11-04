---
name: build-zoom-virtual-agent
description: "Zoom Virtual Agent 的參考 skill。導向 virtual-agent 工作流程之後，在實作 web 嵌入、Android 或 iOS wrapper 整合、knowledge-base 同步、生命週期處理，或排查問題時使用。"
triggers:
  - "virtual agent"
  - "zva"
  - "virtual assistant sdk"
  - "knowledge base sync"
---

# /build-zoom-virtual-agent

Zoom Virtual Agent 的背景參考，涵蓋：
- Web 活動/聊天嵌入。
- Android WebView wrapper。
- iOS WKWebView wrapper。
- Knowledge-base 同步和自訂 API 匯入。

官方文件：
- https://developers.zoom.us/docs/virtual-agent/
- https://developers.zoom.us/docs/virtual-agent/web/
- https://developers.zoom.us/docs/virtual-agent/android/
- https://developers.zoom.us/docs/virtual-agent/ios/

## 路由護欄

- 如果使用者在實作 Zoom client 內的 Contact Center app 介面，串接 [../contact-center/SKILL.md](../contact-center/SKILL.md)。
- 如果使用者需要 backend 的 knowledge-base CRUD 或自動化 script，串接 [../rest-api/SKILL.md](../rest-api/SKILL.md) 和 [../oauth/SKILL.md](../oauth/SKILL.md)。
- 如果使用者只要網站 bot 嵌入和活動控制，留在 [web/SKILL.md](web/SKILL.md)。
- 如果使用者要在 web 聊天外面包行動原生 wrapper，導向 [android/SKILL.md](android/SKILL.md) 或 [ios/SKILL.md](ios/SKILL.md)。

## 快速連結

1. [concepts/architecture-and-lifecycle.md](concepts/architecture-and-lifecycle.md)
2. [scenarios/high-level-scenarios.md](scenarios/high-level-scenarios.md)
3. [references/versioning-and-drift.md](references/versioning-and-drift.md)
4. [references/samples-validation.md](references/samples-validation.md)
5. [references/environment-variables.md](references/environment-variables.md)
6. [troubleshooting/common-drift-and-breaks.md](troubleshooting/common-drift-and-breaks.md)
7. [RUNBOOK.md](RUNBOOK.md)

平台 skill：
- [web/SKILL.md](web/SKILL.md)
- [android/SKILL.md](android/SKILL.md)
- [ios/SKILL.md](ios/SKILL.md)

## 常見的生命週期模式

1. 在 Virtual Agent 管理後台設定活動或入口 ID。
2. 在 web 或 WebView 容器裡初始化 SDK。
3. 呼叫 API 之前，先等就緒（`zoomCampaignSdk:ready` 或 `waitForReady()`）。
4. 需要原生協調時，註冊 bridge handler（`exitHandler`、`commonHandler`、`support_handoff`）。
5. 處理對話生命週期（`engagement_started`、`engagement_ended`）和 UI 狀態。
6. 結束聊天（`endChat`）並清理 listener。

## 高階情境

- 帶有客戶屬性脈絡的網站活動啟動器。
- 有原生關閉/轉接 bridge 的行動 app WebView 聊天。
- 外部 URL 處理：系統瀏覽器 vs app 內瀏覽器的政策。
- 用自訂 API connector，從外部系統同步 knowledge base。
- 從 bot 升級到真人客服、並帶著轉接 payload 的跨團隊支援流程。

## 串接

- Contact Center app/web/行動端的模式：[../contact-center/SKILL.md](../contact-center/SKILL.md)
- OAuth app 設定與 token：[../oauth/SKILL.md](../oauth/SKILL.md)
- KB 自動化的 API 工作流程：[../rest-api/SKILL.md](../rest-api/SKILL.md)
- 事件驅動的 backend 後續處理：[../webhooks/SKILL.md](../webhooks/SKILL.md)

## 操作

- [RUNBOOK.md](RUNBOOK.md) - 5 分鐘 preflight 與除錯檢查清單。
