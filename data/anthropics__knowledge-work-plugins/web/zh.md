---
name: contact-center/web
description: "Zoom Contact Center SDK 的 Web 版。用於 web 聊天/視訊/活動嵌入、engagement 事件處理、app-context 整合，以及 Smart Embed 的 postMessage 工作流程。"
user-invocable: false
triggers:
  - "contact center web"
  - "zcc web sdk"
  - "getengagementcontext web"
  - "onengagementcontextchange"
  - "contact center smart embed"
  - "zcc-init-config-request"
---

# Zoom Contact Center SDK - Web

官方文件：
- https://developers.zoom.us/docs/contact-center/web/
- https://developers.zoom.us/docs/contact-center/web/sdk-reference/

## 快速連結

1. [concepts/lifecycle-and-events.md](concepts/lifecycle-and-events.md)
2. [examples/app-context-and-state.md](examples/app-context-and-state.md)
3. [references/web-reference-map.md](references/web-reference-map.md)
4. [troubleshooting/common-issues.md](troubleshooting/common-issues.md)

## 整合模式

1. Zoom client 裡的 Contact Center App：
- Zoom Apps SDK 的 engagement API/事件。

2. 外部網站嵌入：
- Campaign SDK/web script（`zoomCampaignSdk` 模式）。
- Video client 初始化模式。

3. Smart Embed：
- iframe + `postMessage` 事件契約。

## 硬性護欄

- 使用 campaign SDK 時，所有呼叫都要等 `zoomCampaignSdk:ready` 之後。
- 依 `engagementId` 保存狀態。
- 要預期會有 context 切換和背景 app 的行為。
- 除錯邏輯之前，先驗證 CSP 和 allow-list 設定。

## 串接

- 客戶端內 app API 和驗證流程：[../../zoom-apps-sdk/SKILL.md](../../zoom-apps-sdk/SKILL.md)
- 身分與 OAuth：[../../oauth/SKILL.md](../../oauth/SKILL.md)
- Cobrowse 工作流程：[../../cobrowse-sdk/SKILL.md](../../cobrowse-sdk/SKILL.md)

## 操作

- [RUNBOOK.md](RUNBOOK.md) - 5 分鐘 preflight 與除錯檢查清單。
