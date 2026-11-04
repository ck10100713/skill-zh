---
name: zoom-mcp/whiteboard
description: |
  內建 Zoom Whiteboard MCP connector 的使用指引。用於 Whiteboard MCP 的驗證、
  endpoint、ID 對應，以及 list_whiteboards、get_a_whiteboard 這類工具的工作流程。
  當請求明確是關於 Whiteboard MCP，而不是一般的 Zoom MCP 時，優先使用這個 skill。
user-invocable: false
triggers:
  - "whiteboard mcp"
  - "zoom whiteboard mcp"
  - "zoom mcp whiteboard"
  - "zoom whiteboard tools"
  - "list zoom whiteboards"
  - "get zoom whiteboard"
  - "zoom whiteboard id"
  - "zoom wb/db"
---

# Zoom MCP Whiteboard

Zoom Whiteboard MCP server 的專屬指引。

## Endpoint

| 傳輸方式 | URL |
|-----------|-----|
| Streamable HTTP（建議） | `https://mcp-us.zoom.us/mcp/whiteboard/streamable` |
| SSE（備案） | `https://mcp-us.zoom.us/mcp/whiteboard/sse` |

## 驗證

- **帶有 Whiteboard scope 的 User OAuth** 是 `list_whiteboards`
  和 `get_a_whiteboard` 已驗證可行的路徑。
- **S2S OAuth** 可以連到 Whiteboard MCP gateway 並完成 `tools/list`，但工具
  的執行必須針對你的 app 和 Whiteboard scope 另外驗證。
- 實務規則：Whiteboard MCP 先用 **user OAuth**，除非你已經
  證明你的 S2S app 能用所需的 Whiteboard scope 取得 token 並執行。
- 內建的 connector 預期 token 放在 `ZOOM_WHITEBOARD_MCP_ACCESS_TOKEN`。

參考：[references/authentication-and-identifiers.md](references/authentication-and-identifiers.md)

## 必要的 Scope

Whiteboard MCP 的讀取 scope：
- `whiteboard:read:list_whiteboards`
- `whiteboard:read:whiteboard`

Gateway 宣告的可寫入 Whiteboard metadata：
- `whiteboard:write:whiteboard`

## Whiteboard ID 對應

對 Whiteboard MCP 來說，要用 URL 裡 `/wb/db/` 後面那一段的識別碼，不是
`/p/` 後面的數字那一段。

範例：

```text
https://us05whiteboard.zoom.us/wb/db/6iktP8hJT3e5qaCuwFuAGg/p/180968285929472
                                     ^^^^^^^^^^^^^^^^^^^^^^   ^^^^^^^^^^^^^^^
                                     whiteboard_id            page/subresource id
```

## 可用的工具

目前 Whiteboard MCP 提供的工具有：

- `create_a_whiteboard_for_brainstorming`
- `list_whiteboards`
- `create_a_whiteboard`
- `get_a_whiteboard`
- `create_a_whiteboard_by_script`
- `update_a_whiteboard_metadata`
- `create_a_whiteboard_for_meeting_summary`
- `create_a_whiteboard_for_strategy_analysis`

有些 MCP client 會在 UI 裡替 server 的工具加上 namespace。以上面的原始工具名稱
為準。

參考：[references/tools.md](references/tools.md)

## 讀取工作流程

1. 使用帶有 Whiteboard 讀取 scope 的 user OAuth token。
2. 呼叫 `list_whiteboards`，找出可存取的 whiteboard 並確認正確的 `whiteboard_id`。
3. 用那個 `whiteboard_id` 呼叫 `get_a_whiteboard`。

## 串接

- 上層的 MCP skill：[../SKILL.md](../SKILL.md)
- OAuth 指引：[../concepts/oauth-setup.md](../concepts/oauth-setup.md)
- 一般的路由：[../../general/SKILL.md](../../general/SKILL.md)

## 參考資料

- [references/authentication-and-identifiers.md](references/authentication-and-identifiers.md) - 驗證行為與 Whiteboard ID 對應。
- [references/tools.md](references/tools.md) - Whiteboard MCP 工具目錄。
