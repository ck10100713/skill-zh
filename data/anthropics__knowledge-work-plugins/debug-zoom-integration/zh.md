---
name: debug-zoom-integration
description: 快速除錯壞掉的 Zoom 實作。當 auth、webhook、SDK 加入會議、MCP transport 或即時媒體流程出問題，而你需要在提出修法之前先隔離出是哪一層時使用。
user-invocable: false
---

# Debug Zoom Integration

使用者已經做出東西、而且它壞了的時候，就用這個 skill。

## 排查順序

1. Auth 和 app 設定
2. Request 的組成或事件驗證
3. SDK 初始化或平台不相符
4. Media/session 行為
5. MCP transport 和能力（capability）假設

## 要索取的證據

- 確切的錯誤文字
- 平台和 SDK/runtime
- 相關的 request 或 payload 範例
- 哪些正常、哪些失敗
- 問題是每次都能重現，還是時有時無

## 參考資料導向

- [oauth](../oauth/SKILL.md)
- [rest-api](../rest-api/SKILL.md)
- [webhooks](../webhooks/SKILL.md)
- [meeting-sdk](../meeting-sdk/SKILL.md)
- [video-sdk](../video-sdk/SKILL.md)
- [rtms](../rtms/SKILL.md)
- [zoom-mcp](../zoom-mcp/SKILL.md)

## 輸出

- 最可能出問題的那一層
- 依可能性排序的假設
- 簡短的修復計畫
- 驗證步驟
