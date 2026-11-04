---
name: search-strategy
description: 查詢拆解與多來源搜尋的統籌。把自然語言的問題拆成各來源的目標搜尋，把查詢轉換成各來源專屬的語法，依相關性排序結果，並處理含糊情況和備案策略。
user-invocable: false
---

# 搜尋策略

> 如果看到不認識的 placeholder，或需要確認目前連接了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

企業搜尋的核心智慧。把單一自然語言問題，轉成平行的、各來源專屬的搜尋，並產出排序過、去重過的結果。

## 目標

把這個：
```
"What did we decide about the API migration timeline?"
```

變成跨每個已連接來源的目標搜尋：
```
~~chat:  "API migration timeline decision" (semantic) + "API migration" in:#engineering after:2025-01-01
~~knowledge base: semantic search "API migration timeline decision"
~~project tracker:  text search "API migration" in relevant workspace
```

然後把結果綜合成一個連貫的答案。

## 查詢拆解

### Step 1：辨識查詢類型

把使用者的問題分類，以決定搜尋策略：

| 查詢類型 | 範例 | 策略 |
|-----------|---------|----------|
| **Decision（決定）** | "What did we decide about X?" | 優先找對話（~~chat、email），找結論的訊號 |
| **Status（狀態）** | "What's the status of Project Y?" | 優先找近期活動、任務追蹤工具、狀態更新 |
| **Document（文件）** | "Where's the spec for Z?" | 優先找 Drive、wiki、共用文件 |
| **Person（人）** | "Who's working on X?" | 搜尋任務指派、訊息作者、文件協作者 |
| **Factual（事實）** | "What's our policy on X?" | 優先找 wiki、官方文件，再找佐證的對話 |
| **Temporal（時間）** | "When did X happen?" | 用寬的日期範圍搜尋，找時間戳 |
| **Exploratory（探索）** | "What do we know about X?" | 跨所有來源廣泛搜尋，並綜合 |

### Step 2：擷取搜尋要素

從查詢中擷取：

- **關鍵字**：結果裡一定要出現的核心詞
- **實體**：人、專案、團隊、工具（有 memory 系統就用）
- **意圖訊號**：決定相關的詞、狀態相關的詞、時間標記
- **限制**：時間範圍、來源提示、作者篩選
- **否定**：要排除的東西

### Step 3：為每個來源產生子查詢

針對每個可用的來源，建立一或多個目標明確的查詢：

**這些情況優先用語意搜尋：**
- 概念性問題（「What do we think about...」）
- 不知道確切關鍵字的問題
- 探索類查詢

**這些情況優先用關鍵字搜尋：**
- 已知的詞、專案名稱、縮寫
- 使用者引用的精確片語
- 篩選條件很多的查詢（from:、in:、after:）

**當同一個主題可能有不同稱呼時，產生多個查詢變體：**
```
User: "Kubernetes setup"
Queries: "Kubernetes", "k8s", "cluster", "container orchestration"
```

## 各來源的查詢轉換

### ~~chat

**語意搜尋**（自然語言問題）：
```
query: "What is the status of project aurora?"
```

**關鍵字搜尋：**
```
query: "project aurora status update"
query: "aurora in:#engineering after:2025-01-15"
query: "from:<@UserID> aurora"
```

**篩選條件對應：**
| 企業篩選條件 | ~~chat 語法 |
|------------------|--------------|
| `from:sarah` | `from:sarah` 或 `from:<@USERID>` |
| `in:engineering` | `in:engineering` |
| `after:2025-01-01` | `after:2025-01-01` |
| `before:2025-02-01` | `before:2025-02-01` |
| `type:thread` | `is:thread` |
| `type:file` | `has:file` |

### ~~knowledge base (Wiki)

**語意搜尋**：用在概念性查詢：
```
descriptive_query: "API migration timeline and decision rationale"
```

**關鍵字搜尋**：用在精確的詞：
```
query: "API migration"
query: "\"API migration timeline\""  (exact phrase)
```

### ~~project tracker

**任務搜尋：**
```
text: "API migration"
workspace: [workspace_id]
completed: false  (for status queries)
assignee_any: "me"  (for "my tasks" queries)
```

**篩選條件對應：**
| 企業篩選條件 | ~~project tracker 參數 |
|------------------|----------------|
| `from:sarah` | `assignee_any` 或 `created_by_any` |
| `after:2025-01-01` | `modified_on_after: "2025-01-01"` |
| `type:milestone` | `resource_subtype: "milestone"` |

## 結果排序

### 相關性評分

依這些因素替每個結果評分（權重依查詢類型而定）：

| 因素 | 權重（Decision） | 權重（Status） | 權重（Document） | 權重（Factual） |
|--------|-------------------|------------------|--------------------|-------------------|
| 關鍵字比對 | 0.3 | 0.2 | 0.4 | 0.3 |
| 新鮮度 | 0.3 | 0.4 | 0.2 | 0.1 |
| 權威性 | 0.2 | 0.1 | 0.3 | 0.4 |
| 完整性 | 0.2 | 0.3 | 0.1 | 0.2 |

### 權威性階層

依查詢類型而定：

**事實／政策類的問題：**
```
Wiki/Official docs > Shared documents > Email announcements > Chat messages
```

**「what happened」／決定類的問題：**
```
Meeting notes > Thread conclusions > Email confirmations > Chat messages
```

**狀態類的問題：**
```
Task tracker > Recent chat > Status docs > Email updates
```

## 處理含糊情況

當查詢含糊時，優先問一個聚焦的釐清問題，而不是用猜的：

```
Ambiguous: "search for the migration"
→ "I found references to a few migrations. Are you looking for:
   1. The database migration (Project Phoenix)
   2. The cloud migration (AWS → GCP)
   3. The email migration (Exchange → O365)"
```

只有在這些情況才問釐清問題：
- 確實有不同的解讀，會產生非常不同的結果
- 含糊會顯著影響要搜尋哪些來源

這些情況不要問釐清問題：
- 查詢已經夠清楚，可以產出有用的結果
- 輕微的含糊可以靠回傳多種解讀的結果來化解

## 備案策略

當來源不可用或沒有結果時：

1. **來源不可用**：跳過它，搜尋其餘來源，並註明缺口
2. **某個來源沒有結果**：試更寬的查詢詞、拿掉日期篩選、試替代的關鍵字
3. **所有來源都沒有結果**：向使用者建議修改查詢
4. **被 rate limit**：註明限制，回傳其他來源的結果，並建議稍後再試

### 查詢放寬

如果最初的查詢回傳的結果太少：
```
Original: "PostgreSQL migration Q2 timeline decision"
Broader:  "PostgreSQL migration"
Broader:  "database migration"
Broadest: "migration"
```

依這個順序移除限制：
1. 日期篩選（搜尋所有時間）
2. 來源／位置篩選
3. 比較不重要的關鍵字
4. 只保留核心的實體／主題詞

## 平行執行

一律跨來源平行執行搜尋，絕對不要依序執行。總搜尋時間應該大約等於最慢的單一來源，而不是所有來源的總和。

```
[User query]
     ↓ decompose
[~~chat query] [~~email query] [~~cloud storage query] [Wiki query] [~~project tracker query]
     ↓            ↓            ↓              ↓            ↓
  (parallel execution)
     ↓
[Merge + Rank + Deduplicate]
     ↓
[Synthesized answer]
```
