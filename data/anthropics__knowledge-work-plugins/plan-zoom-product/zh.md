---
name: plan-zoom-product
description: 針對某個使用情境選出正確的 Zoom 建置介面，並清楚說明取捨。在針對某個產品點子或整合目標，要在 REST API、Webhooks、WebSockets、Meeting SDK、Video SDK、Zoom Apps SDK、Phone、Contact Center 或 MCP 之間做決定時使用。
argument-hint: "<product idea, app type, or integration goal>"
user-invocable: false
---

# /plan-zoom-product

> 如果看到不熟的佔位符，或需要確認目前連了哪些工具，請見 [CONNECTORS.md](../../CONNECTORS.md)。

針對特定使用情境，在 Zoom REST API、Webhooks、WebSockets、Meeting SDK、Video SDK、Zoom Apps SDK、Phone、Contact Center 或 MCP 之間做選擇。

## 用法

```text
/plan-zoom-product $ARGUMENTS
```

## 工作流程

1. 找出使用者真正的目標。
2. 分類這個問題屬於自動化、嵌入式會議、自訂視訊、client 內的 app 行為、事件傳遞、AI 工具，還是客服／電話／contact center 的工作。
3. 如果需求含糊不清，在鎖定建議之前先問一個簡短的釐清問題。
4. 推薦主要的 Zoom 介面，並列出最少需要的輔助元件。
5. 說明為什麼被淘汰的替代方案對這個情況比較差。
6. 最後以具體的下一步計畫收尾。

## 輸出

- 推薦的 Zoom 介面
- 需要的輔助元件
- 關鍵的取捨與限制
- 建議的實作順序
- 下一步相關的 skill 連結

## 相關 Skill

- [start](../start/SKILL.md)
- [choose-zoom-approach](../choose-zoom-approach/SKILL.md)
- [design-mcp-workflow](../design-mcp-workflow/SKILL.md)
