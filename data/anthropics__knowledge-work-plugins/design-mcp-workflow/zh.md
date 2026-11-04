---
name: design-mcp-workflow
description: 為 Claude 設計 Zoom MCP 工作流程。當要判斷 Zoom MCP 適不適合某個任務、規劃以工具為基礎的 AI 工作流程，或是要切分 MCP 和 REST API 各自的職責時使用。
user-invocable: false
---

# Design MCP Workflow

使用者想讓 Claude 或其他支援 MCP 的 client 透過工具呼叫來跟 Zoom 互動，而不是只靠確定性的 API 程式碼時，就用這個 skill。

## 涵蓋範圍

- MCP 適配度評估
- REST API 與 MCP 的界線
- 混合架構
- Connector 的預期
- Whiteboard 專屬的 MCP 導向

## 流程

1. 判斷問題屬於 agentic 工具、確定性自動化，還是兩者都有。
2. 純 MCP 的任務導向 [zoom-mcp](../zoom-mcp/SKILL.md)。
3. 混合型的任務同時導向 [zoom-mcp](../zoom-mcp/SKILL.md) 和 [rest-api](../rest-api/SKILL.md)。
4. 如果 Whiteboard 是核心，就導向 [zoom-mcp/whiteboard](../zoom-mcp/whiteboard/SKILL.md)。
5. 明確點出 transport、auth 和 client 能力的假設。

## 常見錯誤

- 把應該留在 REST 的確定性後端工作丟給 MCP
- 把 MCP 當成所有 API 設計的替代品
- 忽略 client 的 transport 支援和 auth 需求
