---
name: zoom-mcp
description: 內建 Zoom MCP connector 的使用指引。在已經導向 MCP 工作流之後，用來規劃或排查「透過工具存取會議、錄影、會議資產或逐字稿」的問題。Zoom Docs 的需求請導向專用的 Docs MCP server，Whiteboard 相關需求請導向 `zoom-mcp/whiteboard`。
user-invocable: false
triggers:
  - "zoom mcp"
  - "zoom mcp server"
  - "zoom mcp tools"
  - "zoom tools/list"
  - "zoom tools/call"
  - "ai companion transcript"
  - "agentic retrieval"
  - "zoom semantic meeting search"
  - "zoom search meetings by content"
  - "zoom meeting assets mcp"
  - "zoom recording resource mcp"
  - "zoom docs via mcp"
  - "zoom transcript via mcp"
  - "meeting transcript via mcp"
---

# Zoom MCP

這是這個 Claude plugin 內建 Zoom MCP connector 的使用指引。建議先走 `design-mcp-workflow` 或 [setup-zoom-mcp](../setup-zoom-mcp/SKILL.md)，再回到這裡查工具介面細節、驗證方式和 MCP 專屬的限制。

# Zoom MCP Server

這個 plugin 內建 Zoom 託管的 MCP server（`mcp-us.zoom.us`），讓 AI agent 可以存取：

- 語意式會議搜尋
- 跟會議綁定的資產取得
- 錄影資源取得

Zoom Docs 由另一個內建的 server 提供：

- `zoom-docs-mcp`，位於 `mcp.zoom.us`
- 專門用來建立和取得 Zoom Docs

主要 Zoom MCP server 目前的工具名稱：

- `get_meeting_assets`
- `search_meetings`
- `get_recording_resource`
- `recordings_list`

有些 MCP client 會在介面上幫 server 工具加命名空間，例如 `zoom-mcp:recordings_list`。
以上面列的原始工具名稱為準。

Zoom Docs 相關的 MCP 工作請用專用的 `zoom-docs-mcp` server。

Whiteboard 相關的 MCP 工作由專用 skill 負責：
[whiteboard/SKILL.md](whiteboard/SKILL.md)。

## Quick Start

**1. 匯出內建 connector 需要的 token：**

```bash
export ZOOM_MCP_ACCESS_TOKEN="your_zoom_user_oauth_access_token"
```

**2. 啟用或重啟 plugin，讓 Claude 重新啟動內建的 MCP server 定義。**

**3. 驗證工具探索：**
- 確認 client 看得到 `recordings_list`、`search_meetings`、`get_meeting_assets`
  和 `get_recording_resource`。
- 如果 client 能看原始協定內容，`tools/list` 就是探索工具的權威來源。
- 目前的完整工具目錄寫在 [references/tools.md](references/tools.md)。

**4. 跑第一個有用的呼叫：**
```text
recordings_list
  userId: "me"
  from: "2026-03-01"
  to: "2026-03-06"
  page_size: 10
```

## Critical Notes

**1. 文件記載的執行路徑是 User OAuth**

要在這個 plugin 裡使用 Zoom MCP 工具，執行路徑請用 **General app** 搭配 **user-level OAuth**。
不要把 Server-to-Server OAuth 當成這裡支援的 MCP 驗證方式。

**2. Zoom MCP 使用 MCP 專屬的細粒度 scope**

Zoom MCP 的 scope 集合跟舊版的廣泛 REST scope 不一樣。
主要 Zoom MCP server 的關鍵 scope 如下：
- `ai_companion:read:search` — 跨 Zoom Meeting、Zoom Chat、Zoom Doc 搜尋，依查詢內容回傳最相關的結果
- `meeting:read:search` — 搜尋並檢視會議
- `meeting:read:assets` — 檢視會議的資產
- `cloud_recording:read:list_user_recordings` — 列出使用者的所有雲端錄影
- `cloud_recording:read:content` — 讀取錄影內容的 scope
- `docs:write:import` — 用匯入方式建立新檔案
- `docs:read:export` — 以 Markdown 格式讀取檔案內容

Zoom Docs MCP 方面，官方文件頁面針對有文件記載的工具列出這些細粒度 scope：
- `docs:write:import` — 用匯入方式建立新檔案
- `docs:read:export` — 以 Markdown 格式讀取檔案內容

**3. AI Companion 功能是前置條件，不能取代 scope**

語意式會議搜尋、會議資產和錄影內容取得，要有 **Smart Recording** 和 **Meeting Summary** 這類帳號功能，結果才有用。
這些功能設定不能取代必要的 OAuth scope。

**4. Whiteboard 是獨立的 MCP 介面**

Zoom MCP endpoint 和 Whiteboard MCP endpoint 是分開的。Whiteboard 相關需求請導向
[whiteboard/SKILL.md](whiteboard/SKILL.md)。

**5. 確定性的會議 CRUD 用 REST**

目前 Zoom MCP 的工具介面沒有提供確定性的會議建立、更新或刪除工具。
如果使用者需要明確的會議 CRUD 操作，請導向
[../rest-api/SKILL.md](../rest-api/SKILL.md)。

## Server Endpoints

| Transport | URL |
|-----------|-----|
| Streamable HTTP（建議） | `https://mcp-us.zoom.us/mcp/zoom/streamable` |
| SSE（備援） | `https://mcp-us.zoom.us/mcp/zoom/sse` |

專用的 Docs MCP server：

| Transport | URL |
|-----------|-----|
| Streamable HTTP（建議） | `https://mcp.zoom.us/mcp/docs/streamable` |
| SSE（備援） | `https://mcp.zoom.us/mcp/docs/sse` |

專用的 Whiteboard MCP skill：
- [whiteboard/SKILL.md](whiteboard/SKILL.md)

## Search and Retrieval Model

`search_meetings` 用的是 AI Companion 檢索，不是單純的 metadata 過濾。實際使用時，
回應 schema 和 scope 行為以線上的 MCP server 為準。

最重要的兩類結果：

- **以 recap 為主的結果**：AI 摘要、跟會議綁定的文件、錄影和相關資產
- **以錄影為主的結果**：雲端錄影的參照，以及可取得逐字稿的資源

主要的檢索流程請看 [examples/transcript-retrieval.md](examples/transcript-retrieval.md)。

## Tool Catalog

| Tool | Key Parameters | Required Scope |
|------|---------------|----------------|
| `get_meeting_assets` | `meetingId`* | `meeting:read:assets` |
| `search_meetings` | `q`, `from`, `to`, `page_size`, `next_page_token` | `meeting:read:search` |
| `get_recording_resource` | `meetingId`*, `types`, `clip_num`, `play_time`, `raw_passcode`, `encode_passcode` | `cloud_recording:read:content` |
| `recordings_list` | `userId`*, `from`, `to`, `meeting_id`, `trash`, `trash_type`, `page_size`, `next_page_token` | `cloud_recording:read:list_user_recordings` |

\* 必填參數

完整的參數和輸出說明：[references/tools.md](references/tools.md)

## Key Workflows

**搜尋會議內容，再取得資產：**
```text
search_meetings
  q: "Q4 planning discussion"
  from: "2026-03-01"
  to: "2026-03-06"
→ choose a returned meeting
→ get_meeting_assets  meetingId: "MEETING_ID_OR_UUID"
```

**列出錄影，再取得錄影資源：**
```text
recordings_list
  userId: "me"
  from: "2026-03-01"
  to: "2026-03-06"
→ choose a recording target
→ get_recording_resource  meetingId: "MEETING_UUID_OR_RECORDING_ID"
```

**建立或取得 Zoom Doc：**
- 用專用的 `zoom-docs-mcp` server，不要用主要的 `zoom-mcp` server
- Zoom Docs MCP 頁面上有文件記載的官方工具是：
  - `create_file_with_content`
  - `get_file_content`

## Error Reference

| Code | Meaning | Fix |
|------|---------|-----|
| `401 Unauthorized` | endpoint 缺少 bearer token，或 token 被拒絕 | 設定 `ZOOM_MCP_ACCESS_TOKEN`，然後重啟 Claude 或重新啟用 plugin |
| `-32001 Invalid access token` | Token 過期、格式錯誤，或缺少必要的 scope | 更新 OAuth token，並確認 MCP 專屬的 scope |
| `-32602 Can not found tool` | 目前的 MCP server 沒有提供你要求的工具名稱 | 重新跑 `tools/list`，使用該 endpoint 目前的工具名稱 |
| `404` | 可能是下游資源找不到的回應 | 用 `search_meetings` 或 `recordings_list` 重新找目標 |

完整的錯誤參考：[references/error-codes.md](references/error-codes.md)

## Documentation

### Concepts
- [concepts/mcp-architecture.md](concepts/mcp-architecture.md) — MCP 協定、託管 endpoint、工具探索和能力模型
- [concepts/oauth-setup.md](concepts/oauth-setup.md) — 建立 OAuth app、MCP 專屬 scope、AI Companion 前置條件、token 生命週期

### Examples
- [examples/transcript-retrieval.md](examples/transcript-retrieval.md) — 搜尋/資產和錄影資源的工作流
- [examples/create-zoom-doc.md](examples/create-zoom-doc.md) — 已驗證的 Zoom Docs 建立流程
- [examples/search-and-act.md](examples/search-and-act.md) — 搜尋、檢視資產，必要時把 CRUD 工作交給 REST
- [examples/meeting-lifecycle.md](examples/meeting-lifecycle.md) — 為什麼會議 CRUD 該放在 REST，以及 MCP 轉交 REST 的模式

### References
- [references/tools.md](references/tools.md) — 目前的 Zoom MCP 工具參考
- [references/error-codes.md](references/error-codes.md) — MCP 和 Zoom API 的錯誤與解法
- [whiteboard/SKILL.md](whiteboard/SKILL.md) — 專用的 Whiteboard MCP skill

### Troubleshooting
- [troubleshooting/common-errors.md](troubleshooting/common-errors.md) — scope 失敗、endpoint 搞混、搜尋/錄影問題

### Operations
- [RUNBOOK.md](RUNBOOK.md) — 5 分鐘的 preflight 與除錯清單

## Related Skills

- [zoom-rest-api](../rest-api/SKILL.md) — 確定性的 REST API 存取，包含會議 CRUD
- [zoom-oauth](../oauth/SKILL.md) — OAuth 實作模式
- [zoom-webhooks](../webhooks/SKILL.md) — 事件驅動的錄影與會議工作流
- [zoom-rtms](../rtms/SKILL.md) — 會議進行中的即時媒體與逐字稿串流
