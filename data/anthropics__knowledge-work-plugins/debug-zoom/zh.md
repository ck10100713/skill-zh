---
name: debug-zoom
description: 隔離故障點並導向對應的 Zoom 參考資料，來除錯壞掉的 Zoom 整合。當 auth、API、webhook、SDK 或 MCP 行為出問題，而你需要一份依可能性排序的假設清單和驗證步驟時使用。
argument-hint: "<symptoms, error, or failing flow>"
---

# /debug-zoom

> 如果看到不熟悉的佔位符，或需要確認目前連接了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

除錯 Zoom 的 auth、API、webhook、SDK 或 MCP 問題，不用在整套文件裡繞來繞去。

## 用法

```text
/debug-zoom $ARGUMENTS
```

## 流程

1. 找出出問題的那一層：auth、API request、webhook、SDK 初始化、media/session 行為，或 MCP transport。
2. 只要最少的缺漏證據：確切的錯誤、平台、request/response、事件 payload，或程式路徑。
3. 提出 2 到 4 個合理的原因，依可能性排序。
4. 導向 `skills/` 裡最相關的深入參考。
5. 給一份簡短的驗證計畫，讓使用者能確認修好了。

## 輸出

- 最可能出問題的那一層
- 依可能性排序的假設
- 針對性的修復步驟
- 驗證檢查清單
- 相關的 skill 連結

## 相關 skill

- [debug-zoom-integration](../debug-zoom-integration/SKILL.md)
- [setup-zoom-oauth](../setup-zoom-oauth/SKILL.md)
- [design-mcp-workflow](../design-mcp-workflow/SKILL.md)
