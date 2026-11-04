---
name: analyze
description: 回答資料相關的問題，從快速查詢到完整分析都行。適用於查單一指標、調查趨勢或下滑的原因、比較不同區隔隨時間的變化，或為利害關係人準備正式的資料報告。
argument-hint: "<question>"
---

# /analyze - 回答資料問題

> 如果看到不熟悉的佔位符，或需要確認目前連了哪些工具，請見 [CONNECTORS.md](../../CONNECTORS.md)。

回答資料問題，從快速查詢、完整分析到正式報告都行。

## 用法

```
/analyze <natural language question>
```

## 工作流程

### 1. 理解問題

解析使用者的問題，並判斷：

- **複雜度**：
  - **快速回答**：單一指標、簡單篩選、事實查詢（例如 "How many users signed up last week?"）
  - **完整分析**：多維度探索、趨勢分析、比較（例如 "What's driving the drop in conversion rate?"）
  - **正式報告**：附方法論、注意事項和建議的完整調查（例如 "Prepare a quarterly business review of our subscription metrics"）
- **資料需求**：需要哪些資料表、指標、維度和時間範圍
- **輸出格式**：數字、表格、圖表、敘述，或組合

### 2. 蒐集資料

**如果有連接資料倉儲 MCP server：**

1. 探索 schema，找出相關的資料表和欄位
2. 撰寫 SQL 查詢來取出需要的資料
3. 執行查詢並取得結果
4. 如果查詢失敗，除錯後重試（檢查欄位名稱、資料表參照，以及特定 SQL 方言的語法）
5. 如果結果看起來不對勁，繼續之前先跑 sanity check

**如果沒有連接資料倉儲：**

1. 請使用者用下列其中一種方式提供資料：
   - 直接貼上查詢結果
   - 上傳 CSV 或 Excel 檔
   - 描述 schema，讓你寫查詢給他們去跑
2. 如果寫的查詢是要讓人手動執行，使用 `sql-queries` skill 取得各 SQL 方言的最佳實務
3. 拿到資料後，繼續做分析

### 3. 分析

- 計算相關指標、彙總和比較
- 找出模式、趨勢、離群值和異常
- 跨維度比較（時間區間、區隔、類別）
- 複雜的分析要把問題拆成子問題，逐一處理

### 4. 呈現前先驗證

分享結果之前，先跑過驗證檢查：

- **筆數合理性**：紀錄筆數合理嗎？
- **Null 檢查**：有沒有可能讓結果失真的意外 null？
- **量級檢查**：數字落在合理範圍嗎？
- **趨勢連續性**：時間序列有沒有意外的缺口？
- **彙總邏輯**：小計加起來等於總計嗎？

只要任何一項檢查讓你起疑，就去調查並註明注意事項。

### 5. 呈現發現

**快速回答：**
- 直接講答案並附上相關背景
- 附上使用的查詢（收合或放在 code block），方便重現

**完整分析：**
- 先講關鍵發現或洞察
- 用資料表和／或視覺化來支撐
- 註明方法論和任何注意事項
- 建議後續的問題

**正式報告：**
- 附關鍵結論的執行摘要
- 說明做法和資料來源的方法論章節
- 附佐證的詳細發現
- 注意事項、限制和資料品質備註
- 建議和後續步驟

### 6. 適合的時候做視覺化

當圖表比表格更能有效傳達結果時：

- 使用 `data-visualization` skill 選擇正確的圖表類型
- 產生 Python 視覺化，或把它做進 HTML 儀表板
- 遵循視覺化的最佳實務，確保清楚和正確

## 範例

**快速回答：**
```
/analyze How many new users signed up in December?
```

**完整分析：**
```
/analyze What's causing the increase in support ticket volume over the past 3 months? Break down by category and priority.
```

**正式報告：**
```
/analyze Prepare a data quality assessment of our customer table -- completeness, consistency, and any issues we should address.
```

## 小技巧

- 盡量明確說明時間範圍、區隔或指標
- 如果你知道資料表名稱，就說出來，可以加快流程
- 對於複雜的問題，Claude 可能會拆成多個查詢
- 結果在呈現之前一定會經過驗證，如果有哪裡看起來怪怪的，Claude 會標出來
