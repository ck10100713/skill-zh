---
name: search
description: 用一次查詢搜尋所有已連接的來源。用「find that doc about...」、「what did we decide on...」、「where was the conversation about...」觸發，或在找可能存在於聊天、email、雲端儲存或專案追蹤工具裡的決定、文件或討論時使用。
argument-hint: "<query>"
---

# Search 指令

> 如果看到不認識的 placeholder，或需要確認目前連接了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

用單一查詢搜尋所有已連接的 MCP 來源。拆解使用者的問題、平行執行搜尋，並綜合結果。

## 指示

### 1. 檢查可用的來源

搜尋之前，先判斷有哪些 MCP 來源可用。試著從可用的工具清單辨識已連接的工具。常見的來源：

- **~~chat**：聊天平台工具
- **~~email**：email 工具
- **~~cloud storage**：雲端儲存工具
- **~~project tracker**：專案追蹤工具
- **~~CRM**：CRM 工具
- **~~knowledge base**：知識庫工具

如果沒有連接任何 MCP 來源：
```
To search across your tools, you'll need to connect at least one source.
Check your MCP settings to add ~~chat, ~~email, ~~cloud storage, or other tools.

Supported sources: ~~chat, ~~email, ~~cloud storage, ~~project tracker, ~~CRM, ~~knowledge base,
and any other MCP-connected service.
```

### 2. 解析使用者的查詢

分析搜尋查詢，了解：

- **意圖**：使用者在找什麼？（一個決定、一份文件、一個人、一則狀態更新、一段對話）
- **實體**：提到的人、專案、團隊、工具
- **時間限制**：新近度的訊號（「this week」、「last month」、特定日期）
- **來源提示**：對特定工具的指涉（「in ~~chat」、「that email」、「the doc」）
- **篩選條件**：從查詢中擷取明確的篩選條件：
  - `from:`：依寄件人／作者篩選
  - `in:`：依頻道、資料夾或位置篩選
  - `after:`：只要這個日期之後的結果
  - `before:`：只要這個日期之前的結果
  - `type:`：依內容類型篩選（message、email、doc、thread、file）

### 3. 拆解成各來源的子查詢

針對每個可用的來源，用該來源原生的搜尋語法建立一個目標明確的子查詢：

**~~chat：**
- 使用你的聊天平台可用的搜尋和讀取工具
- 轉換篩選條件：`from:` 對應到寄件人，`in:` 對應到頻道／房間，日期對應到時間範圍篩選
- 適合時使用自然語言查詢做語意搜尋
- 要精確比對時使用關鍵字查詢

**~~email：**
- 使用可用的 email 搜尋工具
- 轉換篩選條件：`from:` 對應到寄件人，日期對應到時間範圍篩選
- 視情況把 `type:` 對應到附件篩選或主旨搜尋

**~~cloud storage：**
- 使用可用的檔案搜尋工具
- 轉換成檔案查詢語法：名稱包含、全文包含、修改日期、檔案類型
- 檔名和內容兩者都要考慮

**~~project tracker：**
- 使用可用的任務搜尋或 typeahead 工具
- 對應到任務文字搜尋、負責人篩選、日期篩選、專案篩選

**~~CRM：**
- 使用可用的 CRM 查詢工具
- 跨 Account、Contact、Opportunity 和其他相關物件搜尋

**~~knowledge base：**
- 概念性問題用語意搜尋
- 精確比對用關鍵字搜尋

### 4. 平行執行搜尋

在所有可用的來源上同時執行所有子查詢。不要等一個來源跑完才搜尋另一個。

對每個來源：
- 執行轉換後的查詢
- 連同 metadata（時間戳、作者、連結、來源類型）一起擷取結果
- 記下任何失敗或回傳錯誤的來源，不要讓一個失敗卡住其他的

### 5. 排序並去重

**去重：**
- 找出跨來源出現的相同資訊（例如在 ~~chat 討論過、並在 email 確認的決定）
- 把相關的結果群組在一起，而不是顯示重複
- 優先採用最具權威性或最完整的版本

**排序因素：**
- **相關性**：結果和查詢意圖符合的程度？
- **新鮮度**：對狀態／決定類的查詢，越新的結果排越前面
- **權威性**：事實類問題，官方文件 > wiki > 聊天訊息；「what did we discuss」類的查詢，對話 > 文件
- **完整性**：脈絡越多的結果排越前面

### 6. 呈現統一的結果

把回應整理成綜合過的答案，不是原始結果的清單：

**事實／決定類的查詢：**
```
[對問題的直接答案]

Sources:
- [Source 1: 簡短描述] (~~chat, #channel, date)
- [Source 2: 簡短描述] (~~email, from person, date)
- [Source 3: 簡短描述] (~~cloud storage, doc name, last modified)
```

**探索類的查詢（「what do we know about X」）：**
```
[綜合所有來源資訊的摘要]

Found across:
- ~~chat: X relevant messages in Y channels
- ~~email: X relevant threads
- ~~cloud storage: X related documents
- [其他適用的來源]

Key sources:
- [最重要的來源，附連結／參照]
- [第二重要的來源]
```

**「find」類的查詢（找特定的東西）：**
```
[他們要找的東西，附直接參照]

Also found:
- [來自其他來源的相關項目]
```

### 7. 處理邊緣情況

**含糊的查詢：**
如果查詢可能有多種意思，搜尋之前先問一個釐清問題：
```
"API redesign" could refer to a few things. Are you looking for:
1. The REST API v2 redesign (Project Aurora)
2. The internal SDK API changes
3. Something else?
```

**沒有結果：**
```
I couldn't find anything matching "[query]" across [list of sources searched].

Try:
- Broader terms (e.g., "database" instead of "PostgreSQL migration")
- Different time range (currently searching [time range])
- Checking if the relevant source is connected (currently searching: [sources])
```

**部分結果（有些來源失敗）：**
```
[成功來源的結果]

Note: I couldn't reach [failed source(s)] during this search.
Results above are from [successful sources] only.
```

## 備註

- 一律平行搜尋多個來源，絕對不要依序搜尋
- 把結果綜合成答案，不要只列出原始搜尋結果
- 附上來源出處，讓使用者可以深入挖掘
- 尊重使用者的篩選語法，並依各來源適當地套用
- 當查詢提到特定的人時，跨所有來源搜尋他的訊息／文件／被提及的地方
- 對時效性的查詢，排序時優先考慮新近度
- 如果只連接了一個來源，仍要從該來源提供有用的結果
