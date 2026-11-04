---
name: source-management
description: 管理企業搜尋用的已連接 MCP 來源。偵測可用的來源、引導使用者連接新來源、處理來源的優先順序，並留意頻率限制。
user-invocable: false
---

# 來源管理

> 如果看到不熟悉的佔位符，或需要確認哪些工具已連接，請見 [CONNECTORS.md](../../CONNECTORS.md)。

知道有哪些來源可用、協助連接新來源，並管理查詢來源的方式。

## 檢查可用來源

檢查可用的工具，判斷哪些 MCP 來源已連接。每個來源對應一組 MCP 工具：

| Source | Key capabilities |
|--------|-----------------|
| **~~chat** | 搜尋訊息、讀取頻道和討論串 |
| **~~email** | 搜尋訊息、讀取單封 email |
| **~~cloud storage** | 搜尋檔案、取得文件內容 |
| **~~project tracker** | 搜尋任務、輸入即時搜尋 |
| **~~CRM** | 查詢紀錄（帳戶、聯絡人、商機） |
| **~~knowledge base** | 語意搜尋、關鍵字搜尋 |

如果有某個工具前綴，代表那個來源已連接，可以搜尋。

## 引導使用者連接來源

使用者搜尋時，如果已連接的來源很少或沒有：

```
You currently have [N] source(s) connected: [list].

To expand your search, you can connect additional sources in your MCP settings:
- ~~chat — messages, threads, channels
- ~~email — emails, conversations, attachments
- ~~cloud storage — docs, sheets, slides
- ~~project tracker — tasks, projects, milestones
- ~~CRM — accounts, contacts, opportunities
- ~~knowledge base — wiki pages, knowledge base articles

The more sources you connect, the more complete your search results.
```

使用者問到某個沒連接的特定工具時：

```
[Tool name] isn't currently connected. To add it:
1. Open your MCP settings
2. Add the [tool] MCP server configuration
3. Authenticate when prompted

Once connected, it will be automatically included in future searches.
```

## 來源優先順序

不同類型的查詢，先搜某些來源效果比較好。用這些優先順序來加權結果，不是用來跳過來源：

### 依查詢類型

**決策類查詢**（「What did we decide...」）：
```
1. ~~chat (conversations where decisions happen)
2. ~~email (decision confirmations, announcements)
3. ~~cloud storage (meeting notes, decision logs)
4. Wiki (if decisions are documented)
5. Task tracker (if decisions are captured in tasks)
```

**狀態類查詢**（「What's the status of...」）：
```
1. Task tracker (~~project tracker — authoritative status)
2. ~~chat (real-time discussion)
3. ~~cloud storage (status docs, reports)
4. ~~email (status update emails)
5. Wiki (project pages)
```

**文件類查詢**（「Where's the doc for...」）：
```
1. ~~cloud storage (primary doc storage)
2. Wiki / ~~knowledge base (knowledge base)
3. ~~email (docs shared via email)
4. ~~chat (docs shared in channels)
5. Task tracker (docs linked to tasks)
```

**人員類查詢**（「Who works on...」／「Who knows about...」）：
```
1. ~~chat (message authors, channel members)
2. Task tracker (task assignees)
3. ~~cloud storage (doc authors, collaborators)
4. ~~CRM (account owners, contacts)
5. ~~email (email participants)
```

**事實／政策類查詢**（「What's our policy on...」）：
```
1. Wiki / ~~knowledge base (official documentation)
2. ~~cloud storage (policy docs, handbooks)
3. ~~email (policy announcements)
4. ~~chat (policy discussions)
```

### 預設優先順序（一般查詢）

查詢類型不明確時：
```
1. ~~chat (highest volume, most real-time)
2. ~~email (formal communications)
3. ~~cloud storage (documents and files)
4. Wiki / ~~knowledge base (structured knowledge)
5. Task tracker (work items)
6. CRM (customer data)
```

## 留意頻率限制

MCP 來源可能有頻率限制。要從容處理：

### 偵測

頻率限制的回應通常長這樣：
- HTTP 429 回應
- 提到「rate limit」、「too many requests」或「quota exceeded」的錯誤訊息
- 被節流或延遲的回應

### 處理

來源被頻率限制時：

1. **不要馬上重試**：尊重限制
2. **繼續用其他來源**：不要讓整個搜尋卡住
3. **告知使用者**：
```
Note: [Source] is temporarily rate limited. Results below are from
[other sources]. You can retry in a few minutes to include [source].
```
4. **做 digest 時**：如果掃到一半被限制，要註明在限制發生前涵蓋了哪個時間範圍

### 預防

- 避免不必要的 API 呼叫：查詢之前，先判斷這個來源是否可能有相關結果
- 盡量用有針對性的查詢，少用大範圍掃描
- 做 digest 時，API 支援的話就批次請求
- 注意快取：剛跑過的搜尋，不要馬上重跑同一個查詢

## 來源健康狀態

在 session 期間追蹤來源的可用性：

```
Source Status:
  ~~chat:        ✓ Available
  ~~email:        ✓ Available
  ~~cloud storage:  ✓ Available
  ~~project tracker:        ✗ Not connected
  ~~CRM:   ✗ Not connected
  ~~knowledge base:      ⚠ Rate limited (retry in 2 min)
```

回報搜尋結果時，要寫出搜了哪些來源，讓使用者知道答案的涵蓋範圍。

## 新增自訂來源

企業搜尋 plugin 可搭配任何透過 MCP 連接的來源。新的 MCP server 出現後，可以加到 `.mcp.json` 設定裡。搜尋和 digest 指令會依可用的工具，自動偵測並納入新來源。

新增來源的步驟：
1. 把 MCP server 設定加進 `.mcp.json`
2. 需要的話完成認證
3. 之後的搜尋會自動納入這個來源
