---
name: plan-zoom-integration
description: 把一個 Zoom 整合的點子變成包含架構、驗證和交付里程碑的實作計畫。需要務實的建置計畫、分階段的交付順序、風險清單和下一步建議時使用。
argument-hint: "<what you want to build>"
user-invocable: false
---

# /plan-zoom-integration

> 如果看到不熟的佔位符，或需要確認目前連了哪些工具，請見 [CONNECTORS.md](../../CONNECTORS.md)。

為 Zoom 整合或 app 建立務實的建置計畫。

## 用法

```text
/plan-zoom-integration $ARGUMENTS
```

## 工作流程

1. 掌握目標使用者流程和成功標準。
2. 選擇正確的 Zoom 介面和輔助服務。
3. 定義驗證需求、scope 和帳號假設。
4. 把實作拆成幾個階段：原型、核心整合、可靠性和上線。
5. 及早點出困難的風險：OAuth 設定、webhook 驗證、SDK 環境限制、marketplace 審核，或 MCP client 的限制。
6. 最後以能證明架構可行的最小交付物收尾。

## 輸出

- 架構摘要
- 需要的 Zoom 產品和 API
- 驗證與 scope 檢查清單
- 交付階段
- 風險、未解決的問題，以及立即的下一步行動

## 相關 Skill

- [start](../start/SKILL.md)
- [setup-zoom-oauth](../setup-zoom-oauth/SKILL.md)
- [build-zoom-meeting-app](../build-zoom-meeting-app/SKILL.md)
- [build-zoom-bot](../build-zoom-bot/SKILL.md)
