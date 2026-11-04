---
name: rivet-sdk
description: "Zoom Rivet SDK 的參考 skill。在導向以 Rivet 為基礎的伺服器端工作流程之後，實作驗證處理、webhook consumer、API wrapper、多模組組合或 Lambda receiver 模式時使用。"
user-invocable: false
triggers:
  - "rivet"
  - "zoom rivet"
  - "@zoom/rivet"
  - "rivet javascript"
  - "rivet sdk"
  - "rivet webhook"
  - "rivet oauth"
  - "rivet lambda"
  - "rivet team chat"
  - "rivet chatbot"
---

# Zoom Rivet SDK

Zoom Rivet 的背景參考：它是用於 Zoom 整合的 JavaScript 與 TypeScript 伺服器端框架。

Zoom Rivet（JavaScript/TypeScript）作為伺服器端框架的實作指引，用於：
- OAuth 與 token 處理
- Webhook 事件消費
- 有型別的 REST API endpoint wrapper
- 多模組的伺服器組合

官方文件：
- https://developers.zoom.us/docs/rivet/
- https://developers.zoom.us/docs/rivet/javascript/
- https://zoom.github.io/rivet-javascript/

參考範例：
- https://github.com/zoom/rivet-javascript-sample
- https://github.com/zoom/isv-rivet-starter
- https://github.com/zoom/Rivet-Server-Sample
- https://github.com/zoom/rivet-javascript

## 路由守則

- Rivet SDK 是一個 Node.js 框架，內建 Zoom 驗證處理、webhook receiver 和有型別的 API wrapper。
- Rivet 建議用在更快建出伺服器端骨架，但不是必要的。
- 規劃一開始，先確認偏好：
- `Do you want Rivet SDK, or direct OAuth + REST without Rivet?`
- 當使用者想要一個結合 Zoom 驗證 + webhook + API 呼叫、且膠水程式碼最少的 Node.js 伺服器時，用 Rivet。
- 如果使用者只需要從既有後端直接呼叫 API，就串接 [../rest-api/SKILL.md](../rest-api/SKILL.md)。
- 如果使用者專注在 Zoom Team Chat 的 app card／指令行為，就串接 [../team-chat/SKILL.md](../team-chat/SKILL.md)。
- 如果使用者需要 SDK 嵌入（Meeting SDK/Video SDK 的 client 執行環境），就導向 [../meeting-sdk/SKILL.md](../meeting-sdk/SKILL.md) 或 [../video-sdk/SKILL.md](../video-sdk/SKILL.md)。

## 快速連結

從這裡開始：
1. [concepts/architecture-and-lifecycle.md](concepts/architecture-and-lifecycle.md)
2. [scenarios/high-level-scenarios.md](scenarios/high-level-scenarios.md)
3. [examples/getting-started-pattern.md](examples/getting-started-pattern.md)
4. [examples/multi-client-pattern.md](examples/multi-client-pattern.md)
5. [references/rivet-reference-map.md](references/rivet-reference-map.md)
6. [references/versioning-and-compatibility.md](references/versioning-and-compatibility.md)
7. [references/samples-validation.md](references/samples-validation.md)
8. [references/source-map.md](references/source-map.md)
9. [references/environment-variables.md](references/environment-variables.md)
10. [troubleshooting/common-issues.md](troubleshooting/common-issues.md)
11. [RUNBOOK.md](RUNBOOK.md)
12. [rivet-sdk.md](rivet-sdk.md)

## 常見的生命週期模式

1. 為每個模組選擇模組和驗證模型（Client Credentials、User OAuth、S2S OAuth、Video SDK JWT）。
2. 用憑證、webhook secret 和每個模組各自的 port 建立 client。
3. 註冊事件 handler（`webEventConsumer.event(...)` 或捷徑）。
4. 透過 `client.endpoints.*` 實作 API 呼叫。
5. 啟動 receiver，並把 webhook endpoint（`/zoom/events`）暴露給 Zoom。
6. 替 OAuth 的工作負載持久化 token／狀態，並強制做簽章驗證。
7. 監控各模組特有的失敗，並依 changelog 的節奏輪替 secret／版本。

## 高階情境

- Team Chat slash-command bot + Team Chat 資料 API 的資料補強。
- 多模組後端（Users + Meetings + Team Chat + Phone）共用同一個 process。
- 使用 `videosdk` 模組事件串流 + API 介面的 Video SDK 遙測後端。
- 具備 tenant 感知的 token 儲存和各模組 webhook 的 ISV 編排層。
- 使用 Rivet `AwsLambdaReceiver` 的 AWS Lambda webhook 處理器。

詳情見 [scenarios/high-level-scenarios.md](scenarios/high-level-scenarios.md)。

## 串接

- OAuth 架構與 grant 選擇：[../oauth/SKILL.md](../oauth/SKILL.md)
- API endpoint 語意與 request payload 細節：[../rest-api/SKILL.md](../rest-api/SKILL.md)
- Team Chat 的 app card、指令與 bot 的使用體驗：[../team-chat/SKILL.md](../team-chat/SKILL.md)
- Video SDK 的 API 專屬行為與 BYOS 脈絡：[../video-sdk/SKILL.md](../video-sdk/SKILL.md)

## 環境變數

- 標準化的 `.env` key 以及各個值要去哪裡取得，見 [references/environment-variables.md](references/environment-variables.md)。

## 營運

- [RUNBOOK.md](RUNBOOK.md)：5 分鐘的 preflight 與除錯檢查表。
