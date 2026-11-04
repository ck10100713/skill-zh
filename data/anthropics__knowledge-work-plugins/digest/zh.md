---
name: digest
description: 產生跨所有已連接來源的每日或每週活動摘要。離開一陣子回來補進度、一天開始想看提及和待辦事項的總結，或回顧一週的決策和文件更新（依專案分組）時使用。
argument-hint: "[--daily | --weekly | --since <date>]"
---

# Digest Command

> 如果看到不熟悉的佔位符，或需要確認目前連接了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

掃描所有已連接來源的近期活動，產生一份突顯重點的結構化摘要。

## 指示

### 1. 解析 flag

從使用者的輸入決定時間範圍：

- `--daily`：最近 24 小時（沒指定 flag 時的預設值）
- `--weekly`：最近 7 天

使用者也可以指定自訂範圍：
- `--since yesterday`
- `--since Monday`
- `--since 2025-01-20`

### 2. 檢查可用的來源

找出有哪些 MCP 來源已連接（做法跟 search 指令一樣）：

- **~~chat**：頻道、私訊、提及
- **~~email**：收件匣、寄件備份、對話串
- **~~cloud storage**：最近修改、且分享給使用者的文件
- **~~project tracker**：指派、完成、被留言的任務
- **~~CRM**：opportunity 更新、帳戶活動
- **~~knowledge base**：最近更新的 wiki 頁面

如果沒有連接任何來源，就引導使用者：
```
To generate a digest, you'll need at least one source connected.
Check your MCP settings to add ~~chat, ~~email, ~~cloud storage, or other tools.
```

### 3. 從各個來源蒐集活動

**~~chat：**
- 搜尋提到使用者的訊息（`to:me`）
- 檢查使用者所在頻道的近期活動
- 找出使用者參與過的對話串
- 找出重點頻道裡的新訊息

**~~email：**
- 搜尋近期的收件匣訊息
- 找出有新回覆的對話串
- 標記含有待辦事項或直接問使用者問題的信件

**~~cloud storage：**
- 找出最近修改或分享給使用者的文件
- 注意使用者擁有或協作的文件上的新留言

**~~project tracker：**
- 指派給使用者的任務（新的或有更新的）
- 使用者追蹤的任務中，別人完成的
- 使用者有參與的任務上的留言

**~~CRM：**
- Opportunity 的階段變更
- 使用者擁有的帳戶上新記錄的活動
- 更新過的聯絡人或帳戶

**~~knowledge base：**
- 相關集合中最近更新的文件
- 在關注區域新建立的文件

### 4. 找出關鍵項目

從蒐集到的所有活動中，擷取並分類：

**待辦事項：**
- 直接對使用者提出的請求（"Can you..."、"Please..."、"@user"）
- 已指派或快到期的任務
- 在等使用者回覆的問題
- Review 請求

**決策：**
- 在對話串或信件中得出的結論
- 核准或否決
- 政策或方向的改變

**提及：**
- 使用者被提到或被引用的時候
- 關於使用者專案或負責領域的討論

**更新：**
- 使用者追蹤的專案的狀態變更
- 使用者負責領域的文件更新
- 使用者在等的已完成項目

### 5. 依主題分組

依主題、專案或議題來整理摘要，不要依來源。把跨來源的相關活動合併：

```
## Project Aurora
- ~~chat: Design review thread concluded — team chose Option B (#design, Tuesday)
- ~~email: Sarah sent updated spec incorporating feedback (Wednesday)
- ~~cloud storage: "Aurora API Spec v3" updated by Sarah (Wednesday)
- ~~project tracker: 3 tasks moved to In Progress, 2 completed

## Budget Planning
- ~~email: Finance team requesting Q2 projections by Friday
- ~~chat: Todd shared template in #finance (Monday)
- ~~cloud storage: "Q2 Budget Template" shared with you (Monday)
```

### 6. 排版摘要

把輸出結構排清楚：

```
# [Daily/Weekly] Digest — [Date or Date Range]

Sources scanned: ~~chat, ~~email, ~~cloud storage, [others]

## Action Items (X items)
- [ ] [Action item 1] — from [person], [source] ([date])
- [ ] [Action item 2] — from [person], [source] ([date])

## Decisions Made
- [Decision 1] — [context] ([source], [date])
- [Decision 2] — [context] ([source], [date])

## [Topic/Project Group 1]
[Activity summary with source attribution]

## [Topic/Project Group 2]
[Activity summary with source attribution]

## Mentions
- [Mention context] — [source] ([date])

## Documents Updated
- [Doc name] — [who modified, what changed] ([date])
```

### 7. 處理無法使用的來源

如果任何來源失敗或連不上：
```
Note: Could not reach [source name] for this digest.
The following sources were included: [list of successful sources].
```

不要因為一個來源失敗就讓摘要產不出來。用可用的來源盡量產出最好的摘要。

### 8. 統計摘要

最後附上一段快速統計：
```
---
[X] action items · [Y] decisions · [Z] mentions · [W] doc updates
Across [N] sources · Covering [time range]
```

## 備註

- 沒指定 flag 時，預設用 `--daily`
- 依主題／專案分組，不要依來源：使用者在意的是發生了什麼事，不是在哪裡發生
- 待辦事項永遠放最前面：這是摘要裡最能直接行動的部分
- 跨來源的重複活動要去重（同一個決策出現在 ~~chat 和 email，只算一筆）
- 每週摘要要重視重要性而非完整性：突顯重要的，略過雜訊
- 如果使用者有記憶系統（CLAUDE.md），就用它來解讀人名和專案代稱
- 每個項目都要附上足夠的脈絡，讓使用者不用點進去，就能判斷要不要深入看
