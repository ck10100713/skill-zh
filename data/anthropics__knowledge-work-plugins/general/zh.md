---
name: zoom-general
description: 跨產品的 Zoom 參考 skill。當工作流程已經明確、需要共通的平台指引、app 模型比較、認證背景、scope、marketplace 考量，或 API 與 MCP 的路由判斷時使用。
user-invocable: false
triggers:
  - "zoom integration"
  - "getting started"
  - "which zoom sdk"
  - "zoom platform"
  - "choose zoom api"
  - "zoom scopes"
  - "marketplace"
  - "cross-product"
  - "apis vs mcp"
  - "api vs mcp"
---

# Zoom General (Cross-Product Skills)

跨產品 Zoom 問題的背景參考。先用工作流程類的 skill，再用這份檔案取得共通的平台指引和路由細節。

## `zoom-general` 如何路由複雜的開發者查詢

把 `zoom-general` 當成分類器和串接層來用：

1. 偵測查詢裡的產品訊號
2. 挑一個主要 skill
3. 針對 auth、事件或 deploy 的邊緣，附加次要 skill
4. 只有兩條路線的符合信心差不多時，才問一個簡短的釐清問題

最精簡的實作：

```ts
type SkillId =
  | 'zoom-general'
  | 'zoom-rest-api'
  | 'zoom-webhooks'
  | 'zoom-oauth'
  | 'zoom-meeting-sdk-web-component-view'
  | 'zoom-video-sdk'
  | 'zoom-mcp';

const hasAny = (q: string, words: string[]) => words.some((w) => q.includes(w));

function detectSignals(rawQuery: string) {
  const q = rawQuery.toLowerCase();
  return {
    meetingCustomUi: hasAny(q, ['zoom meeting', 'custom ui', 'component view', 'embed meeting']),
    customVideo: hasAny(q, ['video sdk', 'custom video session', 'peer-video-state-change']),
    restApi: hasAny(q, ['rest api', '/v2/', 'create meeting', 'list users', 's2s oauth']),
    webhooks: hasAny(q, ['webhook', 'x-zm-signature', 'event subscription', 'crc']),
    oauth: hasAny(q, ['oauth', 'pkce', 'token refresh', 'account_credentials']),
    mcp: hasAny(q, ['zoom mcp', 'agentic retrieval', 'tools/list', 'semantic meeting search']),
  };
}

function pickPrimarySkill(s: ReturnType<typeof detectSignals>): SkillId {
  if (s.meetingCustomUi) return 'zoom-meeting-sdk-web-component-view';
  if (s.mcp) return 'zoom-mcp';
  if (s.restApi) return 'zoom-rest-api';
  if (s.customVideo) return 'zoom-video-sdk';
  return 'zoom-general';
}

function buildChain(primary: SkillId, s: ReturnType<typeof detectSignals>): SkillId[] {
  const chain = [primary];
  if (s.oauth && !chain.includes('zoom-oauth')) chain.push('zoom-oauth');
  if (s.webhooks && !chain.includes('zoom-webhooks')) chain.push('zoom-webhooks');
  return chain;
}
```

範例：

- `Create a meeting, configure webhooks, and handle OAuth token refresh` ->
  `zoom-rest-api -> zoom-oauth -> zoom-webhooks`
- `Build a custom video UI for a Zoom meeting on web` ->
  `zoom-meeting-sdk-web-component-view`

完整的 TypeScript 實作和交接契約（handoff contract），請看
[references/routing-implementation.md](references/routing-implementation.md)。

## 選擇你的路徑

| 我想要…… | 使用這個 skill |
|--------------|----------------|
| 圍繞真正的 Zoom 會議，建一個自訂的網頁 UI | **[zoom-meeting-sdk-web-component-view](../meeting-sdk/web/component-view/SKILL.md)** |
| 建構確定性的自動化／設定／報表，並明確控制 request | **[zoom-rest-api](../rest-api/SKILL.md)** |
| 接收事件通知（HTTP push） | **[zoom-webhooks](../webhooks/SKILL.md)** |
| 接收事件通知（WebSocket，低延遲） | **[zoom-websockets](../websockets/SKILL.md)** |
| 在我的 app 裡嵌入 Zoom 會議 | **[zoom-meeting-sdk](../meeting-sdk/SKILL.md)** |
| 建構自訂的視訊體驗（Web、React Native、Flutter、Android、iOS、macOS、Unity、Linux） | **[zoom-video-sdk](../video-sdk/SKILL.md)** |
| 建一個在 Zoom client 內執行的 app | **[zoom-apps-sdk](../zoom-apps-sdk/SKILL.md)** |
| 用 AI Services Scribe 轉錄上傳或儲存的媒體 | **[scribe](../scribe/SKILL.md)** |
| 存取會議的即時音訊／視訊／逐字稿 | **[zoom-rtms](../rtms/SKILL.md)** |
| 啟用協作式瀏覽來提供客服支援 | **[zoom-cobrowse-sdk](../cobrowse-sdk/SKILL.md)** |
| 建構 Contact Center app 和管道整合 | **[contact-center](../contact-center/SKILL.md)** |
| 建構 Virtual Agent 的網頁／行動版聊天機器人體驗 | **[virtual-agent](../virtual-agent/SKILL.md)** |
| 建構 Zoom Phone 整合（Smart Embed、Phone API、webhook、URI 流程） | **[phone](../phone/SKILL.md)** |
| 建構 Team Chat app 和整合 | **[zoom-team-chat](../team-chat/SKILL.md)** |
| 用 Rivet 建構 server 端整合（auth + webhook + API） | **[rivet-sdk](../rivet-sdk/SKILL.md)** |
| 在加入之前，執行瀏覽器／裝置／網路的 preflight 診斷 | **[probe-sdk](../probe-sdk/SKILL.md)** |
| 為 Video SDK 加入預建的 UI 元件 | **[zoom-ui-toolkit](../ui-toolkit/SKILL.md)** |
| 實作 OAuth 認證（所有 grant type） | **[zoom-oauth](../oauth/SKILL.md)** |
| 在 Zoom 資料上建構 AI 驅動的工具工作流程（AI Companion／agent） | **[zoom-mcp](../zoom-mcp/SKILL.md)** |
| 透過 Zoom Whiteboard MCP 建構 AI 驅動的 Whiteboard 工作流程 | **[zoom-mcp/whiteboard](../zoom-mcp/whiteboard/SKILL.md)** |
| 建構穩定 API 核心加上 AI 工具層的企業 AI 系統 | **[zoom-rest-api](../rest-api/SKILL.md)** + **[zoom-mcp](../zoom-mcp/SKILL.md)** |

## 規劃檢查點：Rivet SDK（選用）

使用者開始規劃結合 auth + webhook + API 呼叫的 server 端整合時，先問這個：

- `Rivet SDK is a Node.js framework that bundles Zoom auth handling, webhook receivers, and typed API wrappers.`
- `Do you want to use Rivet SDK for faster scaffolding, or do you prefer a direct OAuth + REST implementation without Rivet?`

回答之後的路由：

- 如果使用者選 Rivet：串接 `rivet-sdk` + `oauth` + `rest-api`。
- 如果使用者拒絕 Rivet：串接 `oauth` + `rest-api`（視需要再加 `webhooks` 或產品 skill）。

### SDK vs REST 路由矩陣（硬性停止點）

| 使用者意圖 | 正確路徑 | 不要路由到 |
|-------------|--------------|-----------------|
| 在 app UI 裡嵌入 Zoom 會議 | `zoom-meeting-sdk` | 只用 REST 的 `join_url` 流程 |
| 為真正的 Zoom 會議建自訂網頁 UI | `zoom-meeting-sdk-web-component-view` | `zoom-video-sdk` |
| 建構自訂視訊 UI／session app | `zoom-video-sdk` | Meeting SDK 或 REST 會議連結 |
| 取得瀏覽器加入連結／管理會議資源 | `zoom-rest-api` | Meeting SDK 加入的實作 |

路由護欄：
- 如果使用者問的是 SDK 嵌入／加入行為，就留在 SDK 路徑。
- 如果 prompt 說的是 **meeting** 加上 **custom UI/video/layout/embed**，優先選 `zoom-meeting-sdk-web-component-view`。
- 只有在使用者建構的是自訂 session 產品、而不是 Zoom 會議時，才用 `zoom-video-sdk`。
- 除非使用者明確要求混合架構，否則只有資源管理、報表或連結發送才走 REST 路徑。
- 可執行的分類／串接邏輯和錯誤處理，請看 [references/routing-implementation.md](references/routing-implementation.md)。

### API vs MCP 路由矩陣（硬性停止點）

| 使用者意圖 | 正確路徑 | 原因 |
|-------------|--------------|-----|
| 確定性的後端自動化、帳戶／使用者設定、報表、排程工作 | `zoom-rest-api` | 明確的 request/response 控制和可重複的行為 |
| AI agent 動態挑選工具、跨平台的 AI 工具互通 | `zoom-mcp` | MCP 針對動態工具探索和 agentic 工作流程做了最佳化 |
| 企業 AI 架構（穩定的核心加上有彈性的 AI 層） | `zoom-rest-api + zoom-mcp` | API 負責核心系統動作；MCP 提供經過篩選的 AI 工具／脈絡 |

路由護欄：
- 不要把確定性的後端 API 換成只走 MCP 的路由。
- 任務是 AI agent 的工具編排時，不要硬套 REST 優先的路由。
- 使用者同時需要穩定的自動化和 AI 驅動的互動時，優先用混合路由。
- MCP remote server 透過 Streamable HTTP/SSE 運作；目標 client/agent 支援 MCP transport 時（例如 Claude 或 VS Code），就用這條路徑。
- 不要設計「每個 tenant 一個自訂 MCP endpoint」的佈建方式；Zoom MCP endpoint 是在 instance/cluster 層級共用的。
- 來源：https://developers.zoom.us/docs/mcp/library/resources/apis-vs-mcp/

### 歧義處理（路由之前先問）

當 prompt 同時符合 API 和 MCP 路徑、信心差不多時，執行前先問一個簡短的釐清問題：

- `Do you want deterministic REST API automation, AI-agent MCP tooling, or a hybrid of both?`

然後依回答路由：
- 回答 REST → `zoom-rest-api`
- 回答 MCP → `zoom-mcp`
- 回答混合 → `zoom-rest-api + zoom-mcp`

### MCP 可用性與拓撲備註

- Zoom 託管的 MCP 存取還在演進；文件顯示的模型是由 Zoom 提供以產品為範圍的 MCP server（例如 Meetings、Team Chat、Whiteboard）。
- 以 `zoom-mcp` 作為上層的 MCP 入口。
- Whiteboard 專屬的 MCP 請求，導向 **[zoom-mcp/whiteboard](../zoom-mcp/whiteboard/SKILL.md)**。
- 請求是針對特定產品、且已有 MCP 涵蓋時，先導向該 MCP 的產品介面；否則用 REST/SDK skill 做確定性的實作。

### Webhooks vs WebSockets

兩者都能接收事件通知，但做法不同：

| 面向 | webhooks | zoom-websockets |
|--------|---------------|-----------------|
| 連線 | HTTP POST 到你的 endpoint | 持續的 WebSocket |
| 延遲 | 較高 | 較低 |
| 安全性 | 需要公開的 endpoint | 不需要暴露 endpoint |
| 設定 | 較簡單 | 較複雜 |
| 最適合 | 大多數使用情境 | 即時、對安全性敏感的情境 |

## 常見使用情境

| 使用情境 | 說明 | 需要的 Skill |
|----------|-------------|---------------|
| [Meeting + Webhooks + OAuth Refresh](references/meeting-webhooks-oauth-refresh-orchestration.md) | 在一個設計裡建立會議、處理即時更新，並安全地刷新 OAuth token | [zoom-rest-api](../rest-api/SKILL.md) + [zoom-oauth](../oauth/SKILL.md) + [zoom-webhooks](../webhooks/SKILL.md) |
| [Scribe Transcription Pipeline](use-cases/scribe-transcription-pipeline.md) | 用 AI Services Scribe 的快速模式或批次工作，轉錄上傳的檔案或 S3 封存檔 | [scribe](../scribe/SKILL.md) + 選用的 [zoom-rest-api](../rest-api/SKILL.md) + 選用的 [zoom-webhooks](../webhooks/SKILL.md) |
| [APIs vs MCP Routing](use-cases/apis-vs-mcp-routing.md) | 決定要路由到確定性的 Zoom API、AI 驅動的 MCP，還是混合設計 | [zoom-rest-api](../rest-api/SKILL.md) 以及／或 [zoom-mcp](../zoom-mcp/SKILL.md) |
| [Custom Meeting UI (Web)](use-cases/custom-meeting-ui-web.md) | 在網頁 app 裡用 Meeting SDK Component View，為真正的 Zoom 會議建自訂視訊 UI | [zoom-meeting-sdk-web-component-view](../meeting-sdk/web/component-view/SKILL.md) + [zoom-oauth](../oauth/SKILL.md) |
| [Meeting Automation](use-cases/meeting-automation.md) | 以程式排程、更新、刪除會議 | [zoom-rest-api](../rest-api/SKILL.md) |
| [Meeting Bots](use-cases/meeting-bots.md) | 建構加入會議做 AI／轉錄／錄影的機器人 | [meeting-sdk/linux](../meeting-sdk/linux/SKILL.md) + [zoom-rest-api](../rest-api/SKILL.md) + 選用的 [zoom-webhooks](../webhooks/SKILL.md) |
| [High-Volume Meeting Platform](use-cases/high-volume-meeting-platform.md) | 設計帶有重試、佇列和對帳機制的分散式會議建立與事件處理 | [zoom-rest-api](../rest-api/SKILL.md) + [zoom-webhooks](../webhooks/SKILL.md) + [zoom-oauth](../oauth/SKILL.md) |
| [Recording & Transcription](use-cases/recording-transcription.md) | 下載錄影、取得逐字稿 | [zoom-webhooks](../webhooks/SKILL.md) + [zoom-rest-api](../rest-api/SKILL.md) |
| [Recording Download Pipeline](use-cases/recording-download-pipeline.md) | 自動把錄影下載到你自己的儲存空間（S3、GCS 等） | [zoom-webhooks](../webhooks/SKILL.md) + [zoom-rest-api](../rest-api/SKILL.md) |
| [Real-Time Media Streams](use-cases/real-time-media-streams.md) | 透過 WebSocket 存取即時音訊、視訊、逐字稿 | [zoom-rtms](../rtms/SKILL.md) + [zoom-webhooks](../webhooks/SKILL.md) |
| [In-Meeting Apps](use-cases/in-meeting-apps.md) | 建構在 Zoom 會議內執行的 app | [zoom-apps-sdk](../zoom-apps-sdk/SKILL.md) + [zoom-oauth](../oauth/SKILL.md) |
| [React Native Meeting Embed](use-cases/react-native-meeting-embed.md) | 把會議嵌入 iOS/Android 的 React Native app | [zoom-meeting-sdk-react-native](../meeting-sdk/react-native/SKILL.md) + [zoom-oauth](../oauth/SKILL.md) |
| [Native Meeting SDK Multi-Platform Delivery](use-cases/native-meeting-sdk-multi-platform.md) | 在同一套 auth／版本策略下，對齊 Android、iOS、macOS 和 Unreal 的 Meeting SDK 實作 | [zoom-meeting-sdk](../meeting-sdk/SKILL.md) + 各平台 skill |
| [Native Video SDK Multi-Platform Delivery](use-cases/native-video-sdk-multi-platform.md) | 在同一套 auth／版本策略下，對齊 Android、iOS、macOS 和 Unity 的 Video SDK 實作 | [zoom-video-sdk](../video-sdk/SKILL.md) + 各平台 skill |
| [Electron Meeting Embed](use-cases/electron-meeting-embed.md) | 把會議嵌入桌面的 Electron app | [zoom-meeting-sdk-electron](../meeting-sdk/electron/SKILL.md) + [zoom-oauth](../oauth/SKILL.md) |
| [Flutter Video Sessions](use-cases/flutter-video-sessions.md) | 在 Flutter 建構自訂的行動視訊 session | [zoom-video-sdk-flutter](../video-sdk/flutter/SKILL.md) + [zoom-oauth](../oauth/SKILL.md) |
| [React Native Video Sessions](use-cases/react-native-video-sessions.md) | 在 React Native 建構自訂的行動視訊 session | [zoom-video-sdk-react-native](../video-sdk/react-native/SKILL.md) + [zoom-oauth](../oauth/SKILL.md) |
| [Immersive Experiences](use-cases/immersive-experiences.md) | 用 Layers API 做自訂的視訊版面 | [zoom-apps-sdk](../zoom-apps-sdk/SKILL.md) |
| [Collaborative Apps](use-cases/collaborative-apps.md) | 會議中的即時共享狀態 | [zoom-apps-sdk](../zoom-apps-sdk/SKILL.md) |
| [Contact Center App Lifecycle and Context Switching](use-cases/contact-center-app-lifecycle-and-context-switching.md) | 建構能處理 engagement 事件和多重 engagement 狀態的 Contact Center app | [contact-center](../contact-center/SKILL.md) + [zoom-apps-sdk](../zoom-apps-sdk/SKILL.md) |
| [Virtual Agent Campaign Web and Mobile Wrapper](use-cases/virtual-agent-campaign-web-mobile-wrapper.md) | 在網頁和原生行動 wrapper 上，提供同一套由 campaign 驅動的機器人流程 | [virtual-agent](../virtual-agent/SKILL.md) + [contact-center](../contact-center/SKILL.md) |
| [Virtual Agent Knowledge Base Sync Pipeline](use-cases/virtual-agent-knowledge-base-sync-pipeline.md) | 用網頁同步或自訂 API connector，把外部知識內容同步進 Zoom Virtual Agent | [virtual-agent](../virtual-agent/SKILL.md) + [zoom-rest-api](../rest-api/SKILL.md) + [zoom-oauth](../oauth/SKILL.md) |
| [Zoom Phone Smart Embed CRM Integration](use-cases/zoom-phone-smart-embed-crm.md) | 用 Smart Embed 加 Phone API，建構 CRM 撥號和通話記錄流程 | [phone](../phone/SKILL.md) + [zoom-oauth](../oauth/SKILL.md) + [zoom-webhooks](../webhooks/SKILL.md) |
| [Rivet Event-Driven API Orchestrator](use-cases/rivet-event-driven-api-orchestrator.md) | 建構一個透過 Rivet 模組 client，結合 webhook 和 API 動作的 Node.js 後端 | [rivet-sdk](../rivet-sdk/SKILL.md) + [zoom-oauth](../oauth/SKILL.md) + [zoom-rest-api](../rest-api/SKILL.md) |
| [Probe SDK Preflight Readiness Gate](use-cases/probe-sdk-preflight-readiness-gate.md) | 在 Meeting SDK 或 Video SDK 加入之前，加上瀏覽器／裝置／網路診斷和就緒政策 | [probe-sdk](../probe-sdk/SKILL.md) + [zoom-meeting-sdk](../meeting-sdk/SKILL.md) 或 [zoom-video-sdk](../video-sdk/SKILL.md) |

## 完整使用情境索引

- [APIs vs MCP Routing](use-cases/apis-vs-mcp-routing.md)：依 Zoom 官方標準，選擇只用 API、只用 MCP，或混合路由。
- [AI Companion Integration](use-cases/ai-companion-integration.md)：把 Zoom AI Companion 的能力接進你 app 的工作流程。
- [AI Integration](use-cases/ai-integration.md)：用 Zoom 資料介面加入摘要、轉錄或助理邏輯。
- [Backend Automation (S2S OAuth)](use-cases/backend-automation-s2s-oauth.md)：用帳戶層級的 OAuth 憑證執行 server 端工作。
- [Collaborative Apps](use-cases/collaborative-apps.md)：建構會議中共享的 app 狀態和互動。
- [Contact Center Integration](use-cases/contact-center-integration.md)：把 Zoom Contact Center 的訊號接到外部系統。
- [Contact Center App Lifecycle and Context Switching](use-cases/contact-center-app-lifecycle-and-context-switching.md)：在 Contact Center app 裡實作事件驅動的 engagement 狀態和安全的情境切換。
- [Virtual Agent Campaign Web and Mobile Wrapper](use-cases/virtual-agent-campaign-web-mobile-wrapper.md)：在網站和 Android/iOS WebView wrapper 上，部署以 campaign 為基礎的 Virtual Agent 聊天。
- [Virtual Agent Knowledge Base Sync Pipeline](use-cases/virtual-agent-knowledge-base-sync-pipeline.md)：用網頁同步策略或自訂 API connector，自動化知識庫的匯入。
- [Zoom Phone Smart Embed CRM Integration](use-cases/zoom-phone-smart-embed-crm.md)：整合 Smart Embed 事件、Phone API 和 CRM 工作流程，並做到遷移時資料處理安全。
- [Rivet Event-Driven API Orchestrator](use-cases/rivet-event-driven-api-orchestrator.md)：用 Rivet 建構一個結合 webhook 處理和 API 編排的 Node.js 後端。
- [Probe SDK Preflight Readiness Gate](use-cases/probe-sdk-preflight-readiness-gate.md)：在啟動會議或視訊 session 工作流程之前，執行瀏覽器／裝置／網路診斷。
- [Custom Video](use-cases/custom-video.md)：決定自訂 session 體驗要用 Video SDK 還是相關元件。
- [Custom Meeting UI (Web)](use-cases/custom-meeting-ui-web.md)：用 Meeting SDK Component View，在真正的 Zoom 會議外圍做自訂 UI。
- [Scribe Transcription Pipeline](use-cases/scribe-transcription-pipeline.md)：用 AI Services Scribe 做隨選的檔案轉錄和批次封存處理。
- [Video SDK Bring Your Own Storage](use-cases/video-sdk-bring-your-own-storage.md)：設定 Video SDK 的雲端錄影直接寫入你自己的 S3 bucket。
- [Customer Support Cobrowsing](use-cases/customer-support-cobrowsing.md)：實作客戶與客服人員協作瀏覽的支援流程。
- [Embed Meetings](use-cases/embed-meetings.md)：把 Zoom 會議體驗嵌入你的 app。
- [Form Completion Assistant](use-cases/form-completion-assistant.md)：建構表單填寫和填寫協助的引導流程。
- [HD Video Resolution](use-cases/hd-video-resolution.md)：啟用高畫質視訊的需求並排除相關問題。
- [High-Volume Meeting Platform](use-cases/high-volume-meeting-platform.md)：建構分散式的會議建立和事件處理，附具體的備援做法。
- [Immersive Experiences](use-cases/immersive-experiences.md)：用 Zoom Apps Layers API 做自訂的會議中視覺效果。
- [In-Meeting Apps](use-cases/in-meeting-apps.md)：建構直接在會議和 webinar 情境中執行的 Zoom Apps。
- [Marketplace Publishing](use-cases/marketplace-publishing.md)：準備 Zoom app 並透過 Marketplace 審核上架。
- [Meeting Automation](use-cases/meeting-automation.md)：以程式建立、更新和管理會議。
- [Meeting Bots](use-cases/meeting-bots.md)：建構加入會議、擷取內容和即時分析的機器人。
- [Native Meeting SDK Multi-Platform Delivery](use-cases/native-meeting-sdk-multi-platform.md)：以共用的 auth 和版本控管，標準化 Android、iOS、macOS 和 Unreal 的 Meeting SDK 交付。
- [Native Video SDK Multi-Platform Delivery](use-cases/native-video-sdk-multi-platform.md)：以共用的 auth 和版本控管，標準化 Android、iOS、macOS 和 Unity 的 Video SDK 交付。
- [Meeting Details with Events](use-cases/meeting-details-with-events.md)：結合 REST 查詢和 webhook 事件串流。
- [Minutes Calculation](use-cases/minutes-calculation.md)：計算跨會議／session 的用量和分鐘數指標。
- [Prebuilt Video UI](use-cases/prebuilt-video-ui.md)：用 UI Toolkit 更快交付以 Video SDK 為基礎的 UI。
- [QSS Monitoring](use-cases/qss-monitoring.md)：監控 Zoom 的品質統計和效能指標。
- [Raw Recording](use-cases/raw-recording.md)：擷取原始串流，用於自訂錄影和處理流程。
- [Electron Meeting Embed](use-cases/electron-meeting-embed.md)：把會議嵌入 Electron 桌面應用程式。
- [Flutter Video Sessions](use-cases/flutter-video-sessions.md)：在 Flutter 行動 app 建構 Video SDK session。
- [React Native Meeting Embed](use-cases/react-native-meeting-embed.md)：把 Meeting SDK 嵌入 React Native app。
- [React Native Video Sessions](use-cases/react-native-video-sessions.md)：在 React Native 建構自訂視訊 session。
- [Real-Time Media Streams](use-cases/real-time-media-streams.md)：透過 RTMS 取用即時媒體／逐字稿串流。
- [Recording Download Pipeline](use-cases/recording-download-pipeline.md)：自動化錄影取回和儲存的流程。
- [Recording & Transcription](use-cases/recording-transcription.md)：管理會後的錄影和逐字稿工作流程。
- [Retrieve Meeting and Subscribe Events](use-cases/retrieve-meeting-and-subscribe-events.md)：把 REST 的會議查詢和事件訂閱結合起來。
- [SaaS App OAuth Integration](use-cases/saas-app-oauth-integration.md)：在多租戶 SaaS app 裡實作使用者層級的 OAuth。
- [SDK Size Optimization](use-cases/sdk-size-optimization.md)：縮減以 SDK 為基礎的 app 的 bundle／runtime 佔用空間。
- [SDK Wrappers and GUI](use-cases/sdk-wrappers-gui.md)：評估圍繞 SDK 的 wrapper 模式和 GUI 框架。
- [Team Chat LLM Bot](use-cases/team-chat-llm-bot.md)：建構由 LLM 驅動回覆的 Team Chat 機器人。
- [Testing and Development](use-cases/testing-development.md)：本機測試模式、mock，以及安全的開發循環。
- [Token and Scope Troubleshooting](use-cases/token-and-scope-troubleshooting.md)：除錯 OAuth scope 和 token 不相符的問題。
- [Transcription Bot (Linux)](use-cases/transcription-bot-linux.md)：執行 Linux 會議機器人處理即時轉錄的工作負載。
- [Usage Reporting and Analytics](use-cases/usage-reporting-analytics.md)：蒐集並分析用量／報表資料。
- [User and Meeting Creation](use-cases/user-and-meeting-creation.md)：在同一個流程裡佈建使用者並排程會議。
- [Web SDK Embedding](use-cases/web-sdk-embedding.md)：在瀏覽器型的網頁 app 裡嵌入會議體驗。
- [Server-to-Server OAuth with Webhooks](use-cases/server-to-server-oauth-with-webhooks.md)：結合帳戶層級的 OAuth 和事件驅動的後端處理。
- [Meeting Links vs Embedding](use-cases/meeting-links-vs-embedding.md)：在 `join_url` 發送和 SDK 嵌入之間做選擇。
- [Enterprise App Deployment](use-cases/enterprise-app-deployment.md)：在企業規模下部署、治理和營運 Zoom 整合。

## 前置條件

1. Zoom 帳戶（Pro、Business 或 Enterprise）
2. 在 [Zoom App Marketplace](https://marketplace.zoom.us/) 建立的 app
3. OAuth 憑證（Client ID 和 Secret）

## 參考資料

- [Known Limitations & Quirks](references/known-limitations.md)

## 快速開始

1. 前往 [marketplace.zoom.us](https://marketplace.zoom.us/)
2. 點選 **Develop** → **Build App**
3. 選擇 app 類型（見 [references/app-types.md](references/app-types.md)）
4. 設定 OAuth 和 scope
5. 把憑證複製到你的應用程式

## 詳細參考資料

- **[references/authentication.md](references/authentication.md)** - OAuth 2.0、S2S OAuth、JWT 的做法
- **[references/app-types.md](references/app-types.md)** - app 類型的決策指南
- **[references/scopes.md](references/scopes.md)** - OAuth scope 參考
- **[references/marketplace.md](references/marketplace.md)** - Marketplace 入口網站導覽
- **[references/query-routing-playbook.md](references/query-routing-playbook.md)** - 把複雜的查詢路由到對的專門 skill
- **[references/interview-answer-routing.md](references/interview-answer-routing.md)** - zoom-general 路由的簡短、可直接用於面試的回答模式
- **[references/routing-implementation.md](references/routing-implementation.md)** - 具體的 TypeScript 查詢分類和 skill 交接契約
- **[references/automatic-skill-chaining-rest-webhooks.md](references/automatic-skill-chaining-rest-webhooks.md)** - REST + webhook 串接工作流程的可執行流程
- **[references/meeting-webhooks-oauth-refresh-orchestration.md](references/meeting-webhooks-oauth-refresh-orchestration.md)** - 會議建立 + webhook 更新 + OAuth token 刷新的具體設計
- **[references/distributed-meeting-fallback-architecture.md](references/distributed-meeting-fallback-architecture.md)** - 帶有重試、circuit breaker 和對帳備援的高流量分散式架構
- **[references/community-repos.md](references/community-repos.md)** - 依產品整理的 Zoom 官方範例 repo 精選清單

## SDK 維護

- **[references/sdk-upgrade-guide.md](references/sdk-upgrade-guide.md)** - 版本政策、升級步驟
- **[references/sdk-upgrade-workflow.md](references/sdk-upgrade-workflow.md)** - Changelog + RSS，逐版本可重複使用的升級流程
- **[references/sdk-logs-troubleshooting.md](references/sdk-logs-troubleshooting.md)** - 蒐集 SDK log

## 資源

- **官方文件**：https://developers.zoom.us/
- **Marketplace**：https://marketplace.zoom.us/
- **開發者論壇**：https://devforum.zoom.us/

## 環境變數

- 標準化的 `.env` key 以及每個值在哪裡找，請看 [references/environment-variables.md](references/environment-variables.md)。

## 營運

- [RUNBOOK.md](RUNBOOK.md) - 5 分鐘的上線前檢查和除錯清單。
