---
name: choose-zoom-approach
description: 為某個使用情境選擇對的 Zoom 架構。當要在 REST API、Webhooks、WebSockets、Meeting SDK、Video SDK、Zoom Apps SDK、Zoom MCP、Phone、Contact Center 或混合方案之間做決定時使用。
user-invocable: false
---

# Choose Zoom Approach

替這份工作挑最小而正確的 Zoom 介面，再只疊上真正需要的輔助元件。

## 決策框架

| 問題類型 | 主要的 Zoom 介面 |
|---|---|
| 確定性的後端自動化、帳號管理、報表、排程工作 | [rest-api](../rest-api/SKILL.md) |
| 把事件送到你的後端 | [webhooks](../webhooks/SKILL.md) 或 [websockets](../websockets/SKILL.md) |
| 把 Zoom 會議嵌進你的 app | [meeting-sdk](../meeting-sdk/SKILL.md) |
| 建立完全客製的視訊體驗 | [video-sdk](../video-sdk/SKILL.md) |
| 在 Zoom 用戶端裡面開發 | [zoom-apps-sdk](../zoom-apps-sdk/SKILL.md) |
| 針對 Zoom 資料的 AI agent 工具工作流程 | [zoom-mcp](../zoom-mcp/SKILL.md) |
| 即時媒體擷取或會議機器人 | [rtms](../rtms/SKILL.md)，需要時加上 [meeting-sdk](../meeting-sdk/SKILL.md) |
| 電話工作流程 | [phone](../phone/SKILL.md) |
| Contact Center 或 Virtual Agent 流程 | [contact-center](../contact-center/SKILL.md) 或 [virtual-agent](../virtual-agent/SKILL.md) |

## 護欄

- 當使用者實際上需要的是 Zoom 會議的語意時，不要推薦 Video SDK。
- 當使用者需要的是完全客製的 session 產品時，不要推薦 Meeting SDK。
- 不要用只靠 MCP 的做法，取代確定性的後端自動化。
- 當使用者同時需要穩定的系統動作和 AI 驅動的探索時，優先採用 `rest-api + zoom-mcp` 的混合方案。

## 要產出什麼

- 一條推薦的路徑
- 最少的輔助元件
- 硬性限制與取捨
- 立即的下一個實作步驟
