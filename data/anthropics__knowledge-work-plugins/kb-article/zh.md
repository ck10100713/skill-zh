---
name: kb-article
description: 根據已解決的問題或常見問題，擬一篇知識庫文章。用於某張工單的解法值得整理成自助文件、同一個問題一再出現、需要發布暫時解法，或是要向客戶公告已知問題的時候。
argument-hint: "<resolved issue or ticket>"
---

# /kb-article

> 如果看到不認識的佔位符，或需要確認目前連了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

根據已解決的支援問題、常見問題或有文件記錄的暫時解法，擬一篇可以直接發布的知識庫文章。內容的結構要方便搜尋和自助使用。

## 用法

```
/kb-article <resolved issue, ticket reference, or topic description>
```

範例：
- `/kb-article How to configure SSO with Okta — resolved this for 3 customers last month`
- `/kb-article Ticket #4521 — customer couldn't export data over 10k rows`
- `/kb-article Common question: how to set up webhook notifications`
- `/kb-article Known issue: dashboard charts not loading on Safari 16`

## 工作流程

### 1. 了解來源素材

解析輸入，找出：

- **問題是什麼？** 最初的問題、疑問或錯誤
- **解法是什麼？** 解決方式、暫時解法或答案
- **影響誰？** 使用者類型、方案等級或設定
- **有多常見？** 一次性還是反覆出現的問題
- **哪種文章類型最適合？** How-to、疑難排解、FAQ、已知問題或參考資料（見下方的文章類型）

如果有提供工單參照，就查完整的來龍去脈：

- **~~support platform**：拉出工單討論串、解決方式和任何內部備註
- **~~knowledge base**：檢查是否已有類似的文章（更新還是新建）
- **~~project tracker**：檢查是否有相關的 bug 或功能需求

### 2. 擬文章

依照下面的文章結構、格式標準和搜尋最佳實務：

- 依所選的文章類型（how-to、疑難排解、FAQ、已知問題或參考資料）套用範本
- 套用搜尋最佳實務：用客戶用語寫標題、用白話寫開頭第一句、放上確切的錯誤訊息、放常見的同義詞
- 保持容易瀏覽：標題、編號步驟、短段落

### 3. 產生文章

連同 metadata 一起呈現草稿：

```
## KB Article Draft

**Title:** [文章標題]
**Type:** [How-to / Troubleshooting / FAQ / Known Issue / Reference]
**Category:** [產品領域或主題]
**Tags:** [可搜尋的標籤]
**Audience:** [所有使用者 / 管理員 / 開發者 / 特定方案]

---

[完整文章內容，用下方適當的範本]

---

### Publishing Notes
- **Source:** [工單編號、客戶對話或內部討論]
- **Existing articles to update:** [如果跟既有內容重疊]
- **Review needed from:** [技術正確性需要確認時，列出 SME 或團隊]
- **Suggested review date:** [何時回頭檢查正確性]
```

### 4. 提供下一步

產生文章之後：
- 「要我幫你檢查 ~~knowledge base 裡是否已經有類似的文章嗎？」
- 「要不要為不同的讀者調整技術深度？」
- 「要我擬一篇配套文章嗎（例如搭配這份疑難排解指南的 how-to）？」
- 「要不要做一份只供內部使用、技術細節更多的版本？」

---

## 文章結構與格式標準

### 通用的文章元素

每篇 KB 文章都應該包含：

1. **標題**：清楚、可搜尋，描述結果或問題（不要用內部行話）
2. **概述**：1 到 2 句話，說明這篇文章涵蓋什麼、給誰看
3. **本文**：適合該文章類型的結構化內容
4. **相關文章**：連到相關的配套內容
5. **Metadata**：類別、標籤、讀者、最後更新日期

### 格式規則

- **用標題（H2、H3）** 把內容切成容易瀏覽的段落
- **循序的步驟用編號清單**
- **不分先後的項目用項目符號清單**
- **UI 元素名稱、關鍵詞和強調用粗體**
- **指令、API 呼叫、錯誤訊息和設定值用程式碼區塊**
- **比較、選項或參考資料用表格**
- **警告、提示和重要的但書用提示框/備註**
- **段落要短**：最多 2 到 4 句
- **一個段落一個重點**：如果一個段落涵蓋兩個主題，就拆開

## 為搜尋而寫

客戶找不到的文章就沒有用。每篇文章都要為搜尋最佳化：

### 標題最佳實務

| 好標題 | 壞標題 | 原因 |
|------------|-----------|-----|
| 「How to configure SSO with Okta」 | 「SSO Setup」 | 具體，包含客戶會搜尋的工具名稱 |
| 「Fix: Dashboard shows blank page」 | 「Dashboard Issue」 | 包含客戶遇到的症狀 |
| 「API rate limits and quotas」 | 「API Information」 | 包含客戶會搜尋的具體詞彙 |
| 「Error: 'Connection refused' when importing data」 | 「Import Problems」 | 包含確切的錯誤訊息 |

### 關鍵字最佳化

- **放上確切的錯誤訊息**：客戶會把錯誤文字複製貼上去搜尋
- **用客戶的語言**，不要用內部術語：用「can't log in」，不要用「authentication failure」
- **放上常見的同義詞**：「delete/remove」、「dashboard/home page」、「export/download」
- **加上替代的說法**：在概述裡從不同角度講同一個問題
- **用產品領域加標籤**：確保類別和標籤符合客戶看待產品的方式

### 開頭句公式

每篇文章都用一句話開頭，用白話重述問題或任務：

- **How-to**：「This guide shows you how to [accomplish X].」
- **疑難排解**：「If you're seeing [symptom], this article explains how to fix it.」
- **FAQ**：「[用客戶的話寫的問題]? Here's the answer.」
- **已知問題**：「Some users are experiencing [symptom]. Here's what we know and how to work around it.」

## 文章類型範本

### How-to 文章

**目的**：完成某項任務的逐步指示。

**結構**：
```
# How to [完成任務]

[概述：這份指南涵蓋什麼，以及什麼時候會用到]

## Prerequisites
- [開始前需要什麼]

## Steps
### 1. [動作]
[附具體細節的指示]

### 2. [動作]
[指示]

## Verify It Worked
[如何確認成功]

## Common Issues
- [問題]：[解法]

## Related Articles
- [連結]
```

**最佳實務**：
- 每個步驟以動詞開頭
- 寫出具體的路徑：「Go to Settings > Integrations > API Keys」
- 每個步驟之後，說明使用者應該看到什麼（「You should see a green confirmation banner」）
- 自己測試這些步驟，或是對照最近的工單解決紀錄來驗證

### 疑難排解文章

**目的**：診斷並解決特定問題。

**結構**：
```
# [問題描述：使用者看到什麼]

## Symptoms
- [使用者觀察到什麼]

## Cause
[為什麼會發生：簡短、不用行話的解釋]

## Solution
### Option 1: [主要的修正]
[步驟]

### Option 2: [方案一不管用時的替代方案]
[步驟]

## Prevention
[未來怎麼避免]

## Still Having Issues?
[怎麼取得協助]
```

**最佳實務**：
- 先講症狀，不是原因：客戶搜尋的是他們看到的東西
- 可以的話提供多個解法（最可能有效的放最前面）
- 加上「Still having issues?」段落，指向支援管道
- 如果根本原因很複雜，給客戶看的解釋要保持簡單

### FAQ 文章

**目的**：對常見問題的快速回答。

**結構**：
```
# [問題：用客戶的話寫]

[直接的答案：1 到 3 句話]

## Details
[需要時補充的背景、細節或說明]

## Related Questions
- [連到相關的 FAQ]
- [連到相關的 FAQ]
```

**最佳實務**：
- 第一句就回答問題
- 保持簡潔：如果答案需要逐步講解，那是 how-to，不是 FAQ
- 把相關的 FAQ 分組，並互相連結

### 已知問題文章

**目的**：記錄已知的 bug 或限制，並附上暫時解法。

**結構**：
```
# [Known Issue]: [簡短描述]

**Status:** [Investigating / Workaround Available / Fix In Progress / Resolved]
**Affected:** [誰/什麼受到影響]
**Last updated:** [日期]

## Symptoms
[使用者遇到什麼]

## Workaround
[繞過這個問題的步驟，或「No workaround available」]

## Fix Timeline
[預計修正日期或目前狀態]

## Updates
- [日期]：[更新]
```

**最佳實務**：
- 狀態要保持最新：沒有什麼比過時的已知問題文章更快損害信任
- 修正上線時更新文章，並標為已解決
- 如果已解決，文章要保留上線 30 天，給還在搜尋舊症狀的客戶

## 審閱與維護頻率

知識庫不維護就會腐壞。照這個時程走：

| 活動 | 頻率 | 誰 |
|----------|-----------|-----|
| **新文章審閱** | 發布前 | 同儕審閱，技術內容再加 SME |
| **正確性稽核** | 每季 | 支援團隊審閱流量最高的文章 |
| **過時內容檢查** | 每月 | 標記 6 個月以上沒更新的文章 |
| **已知問題更新** | 每週 | 更新所有未結已知問題的狀態 |
| **分析審閱** | 每月 | 檢查哪些文章的有幫助評分低或跳出率高 |
| **缺口分析** | 每季 | 找出沒有 KB 文章的熱門工單主題 |

### 文章生命週期

1. **Draft**：寫好了，需要審閱
2. **Published**：已上線，客戶可以看到
3. **Needs update**：標記要修訂（產品變更、回饋或年代久遠）
4. **Archived**：不再相關，但保留供參考
5. **Retired**：從知識庫移除

### 什麼時候更新、什麼時候新建

**更新既有文章**的時機：
- 產品變了，步驟需要更新
- 文章大致正確，但少了某個細節
- 回饋顯示客戶對某個特定段落感到困惑
- 找到了更好的暫時解法或解決方案

**新建文章**的時機：
- 新功能或新產品領域需要文件
- 已解決的工單顯示有缺口：這個主題沒有文章
- 既有文章涵蓋太多主題，應該拆開
- 不同的讀者需要用不同方式解釋同樣的資訊

## 連結與分類體系

### 分類結構

把文章組織成符合客戶思考方式的階層：

```
Getting Started
├── Account setup
├── First-time configuration
└── Quick start guides

Features & How-tos
├── [Feature area 1]
├── [Feature area 2]
└── [Feature area 3]

Integrations
├── [Integration 1]
├── [Integration 2]
└── API reference

Troubleshooting
├── Common errors
├── Performance issues
└── Known issues

Billing & Account
├── Plans and pricing
├── Billing questions
└── Account management
```

### 連結最佳實務

- **從疑難排解連到 how-to**：「For setup instructions, see [How to configure X]」
- **從 how-to 連到疑難排解**：「If you encounter errors, see [Troubleshooting X]」
- **從 FAQ 連到詳細文章**：「For a full walkthrough, see [Guide to X]」
- **從已知問題連到暫時解法**：讓從問題到解法的路徑保持短
- **在 KB 內使用相對連結**：它們比絕對 URL 更能撐過重組
- **避免循環連結**：如果 A 連到 B，B 不該連回 A，除非兩者真的都是有用的入口

## KB 寫作最佳實務

1. 為了那位正在受挫、搜尋答案的客戶而寫：要清楚、直接、有幫助
2. 每篇文章都應該能用客戶會打的字搜尋到
3. 測試你的文章：自己照著步驟做，或找不熟悉這個主題的人來做
4. 文章要聚焦：一個問題，一個解法。文章越寫越長就拆開
5. 積極維護：錯誤的文章比沒有文章更糟
6. 追蹤缺了什麼：每一張本來可以變成 KB 文章的工單，都是內容缺口
7. 衡量影響：沒有流量、或沒有減少工單的文章，需要改進或下架
