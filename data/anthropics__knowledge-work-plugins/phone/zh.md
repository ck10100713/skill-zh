---
name: build-zoom-phone-integration
description: "Zoom Phone 的參考 skill。在導向某個 phone 工作流程之後，實作 OAuth、Phone API、webhook、Smart Embed 事件、URI scheme、CRM 或 CTI 撥號器，或通話處理自動化時使用。"
triggers:
  - "zoom phone"
  - "phone smart embed"
  - "zoom phone api"
  - "zoom phone webhook"
  - "call history"
  - "call handling"
  - "zoomphonecall"
  - "zoomphonesms"
  - "phone crm integration"
  - "call element"
---

# /build-zoom-phone-integration

橫跨 API、webhook、Smart Embed 和 URI 啟動等工作流程的 Zoom Phone 整合背景參考。

橫跨 API、webhook／事件、Smart Embed 和 URI 啟動等工作流程的 Zoom Phone 整合實作指引。

官方文件：
- https://developers.zoom.us/docs/phone/
- CRM 範例參考：https://github.com/zoom/CRM-Sample

## 導向護欄

- 如果使用者需要在 web app 裡嵌入軟體電話的行為，使用 Smart Embed（[examples/smart-embed-postmessage-bridge.md](examples/smart-embed-postmessage-bridge.md)）。
- 如果使用者需要通話紀錄、分析或自動化，使用 Phone REST API 和 webhook（[references/deprecations-and-migrations.md](references/deprecations-and-migrations.md)）。
- 如果使用者需要從外部 UI 啟動點擊撥號／簡訊，使用 URI scheme（`zoomphonecall://`、`zoomphonesms://`）。
- 如果使用者同時用到 Zoom Phone 和 Contact Center，就串接 [../contact-center/SKILL.md](../contact-center/SKILL.md)。

## 快速連結

從這裡開始：
1. [concepts/architecture-and-lifecycle.md](concepts/architecture-and-lifecycle.md)
2. [scenarios/high-level-scenarios.md](scenarios/high-level-scenarios.md)
3. [references/deprecations-and-migrations.md](references/deprecations-and-migrations.md)
4. [references/forum-top-questions.md](references/forum-top-questions.md)
5. [references/smart-embed-event-contract.md](references/smart-embed-event-contract.md)
6. [references/call-handling-patterns.md](references/call-handling-patterns.md)
7. [references/environment-variables.md](references/environment-variables.md)
8. [references/crm-sample-validation.md](references/crm-sample-validation.md)
9. [troubleshooting/common-issues.md](troubleshooting/common-issues.md)
10. [RUNBOOK.md](RUNBOOK.md)
11. [examples/smart-embed-postmessage-bridge.md](examples/smart-embed-postmessage-bridge.md)
12. [examples/phone-api-service-pattern.md](examples/phone-api-service-pattern.md)
13. [references/source-map.md](references/source-map.md)

## 常見的生命週期模式

1. 準備帳號前置條件（Zoom Phone 授權、管理員設定、簡訊就緒）。
2. 在 Marketplace 建立 OAuth app 和 scope。
3. 選擇整合介面：
- Smart Embed（iframe + postMessage）
- REST + webhook
- URI 啟動（`callto`、`tel`、`zoomphonecall`、`zoomphonesms`）
4. 擷取即時事件（Smart Embed 事件和／或 webhook）。
5. 保存通話識別碼並關聯紀錄（`call_id`、`call_history_uuid`、`call_element_id`）。
6. 套用對遷移安全的資料對應（v1 -> v2 -> v3），並處理被改名的欄位。
7. 強化安全性（origin 驗證、webhook 簽章驗證、最小權限 scope）。

## 高層情境

- 使用 Smart Embed 加聯絡人搜尋／比對 callback 的 CRM 軟體電話面板。
- 透過 `zp-make-call` 從帳號／聯絡人表格點擊撥號。
- 使用 `zp-save-log-event` 和自訂備註頁面的通話結果（disposition）工作流程。
- 使用 `zoomphonesms://` 和 `zp-sms-log-event` 的簡訊互動工作流程。
- 由 `phone.*` webhook 事件驅動的即時營運看板。
- 從舊版通話紀錄遷移到 call history／call elements 的通話分析。
- 針對使用者／自動總機／通話佇列的通話處理設定做管理員自動化。

詳情請見 [scenarios/high-level-scenarios.md](scenarios/high-level-scenarios.md)。

## 串接

- OAuth 設定／token 生命週期：[../oauth/SKILL.md](../oauth/SKILL.md)
- 透過 REST 取得 Phone 和帳號資源：[../rest-api/SKILL.md](../rest-api/SKILL.md)
- 事件傳遞和簽章驗證：[../webhooks/SKILL.md](../webhooks/SKILL.md)
- Contact Center 混合旅程：[../contact-center/SKILL.md](../contact-center/SKILL.md)

## 環境變數

- 標準化的 `.env` key 以及每個值該去哪裡找，請見 [references/environment-variables.md](references/environment-variables.md)。
