---
name: setup-zoom-mcp
description: 判斷 Zoom MCP 什麼時候適合用，並替 Claude 產出一份安全的設定計畫。在規劃以 Zoom 資料為基礎的 AI 工作流程、在 MCP 和 REST 之間做選擇，或定義混合式 MCP 架構時使用。
argument-hint: "<AI workflow or MCP use case>"
---

# /setup-zoom-mcp

> 如果看到不認識的 placeholder，或需要確認目前連接了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

規劃 Zoom MCP 工作流程，並判斷什麼時候只用 MCP、什麼時候用 REST API + MCP 的混合架構。

## 用法

```text
/setup-zoom-mcp $ARGUMENTS
```

## 工作流程

1. 判斷目標是確定性的自動化、AI 工具編排，還是混合型。
2. 如果適合用 MCP，找出可能用到的 Zoom MCP 介面和傳輸層的假設。
3. 如果只靠 MCP 不夠，另外定義 REST API 負責的部分。
4. 點出驗證、scope 和 client 能力的限制。
5. 以一個最小的 proof-of-concept 步驟順序收尾。

## 輸出

- 建議的 MCP 策略
- Connector 的預期
- 如果也需要 REST，混合架構的邊界
- 風險與設定備註
- 相關的 skill 連結

## 相關 Skills

- [design-mcp-workflow](../design-mcp-workflow/SKILL.md)
- [choose-zoom-approach](../choose-zoom-approach/SKILL.md)
