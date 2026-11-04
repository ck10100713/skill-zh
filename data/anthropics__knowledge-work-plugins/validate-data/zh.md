---
name: validate-data
description: 在分享之前對分析做 QA：方法論、正確性和偏誤檢查。在對利害關係人簡報前審閱分析、抽查計算和彙總邏輯、確認 SQL 查詢結果看起來對不對，或評估結論是否真的有資料支持時使用。
argument-hint: "<要審閱的分析>"
---

# /validate-data - 分享前驗證分析

> 如果看到不認識的 placeholder，或想確認目前連了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

在跟利害關係人分享之前，審閱分析的正確性、方法論和潛在偏誤。產出信心評估和改進建議。

## 用法

```
/validate-data <要審閱的分析>
```

分析可以是：
- 對話裡的文件或報告
- 檔案（markdown、notebook、試算表）
- SQL 查詢及其結果
- 圖表及其底層資料
- 對方法論和發現的描述

## 工作流程

### 1. 審閱方法論和假設

檢視：

- **問題的界定**：這份分析回答的是對的問題嗎？問題有沒有可能被不同方式解讀？
- **資料的選擇**：用的資料表/資料集對嗎？時間範圍合適嗎？
- **母體的定義**：分析的母體定義正確嗎？有沒有非預期的排除？
- **指標的定義**：指標定義得清楚且一致嗎？跟利害關係人的理解一致嗎？
- **基準與比較**：比較公平嗎？時間區間、cohort 大小和情境可以比嗎？

### 2. 跑一遍交付前 QA 檢查清單

照著下面的檢查清單走：資料品質、計算、合理性和呈現檢查。

### 3. 檢查常見的分析陷阱

依照下面詳細的陷阱目錄系統性地檢查（join 爆炸、存活者偏誤、不完整期間比較、分母漂移、平均的平均、時區不一致、選擇偏誤）。

### 4. 驗證計算和彙總

做得到的話，抽查：

- 獨立重算幾個關鍵數字
- 驗證小計加起來等於總計
- 檢查該加總為 100% 的百分比有沒有加到 100%（或接近）
- 確認 YoY/MoM 比較用的是正確的基期
- 驗證所有指標套用的 filter 是一致的

套用下面的結果合理性檢查技巧（數量級檢查、交叉驗證、紅旗偵測）。

### 5. 評估視覺化

如果分析包含圖表：

- 座標軸是從合適的值開始嗎（長條圖要從零開始）？
- 比較用的圖表之間刻度一致嗎？
- 圖表標題準確描述了呈現的內容嗎？
- 這個視覺化會不會誤導匆匆瀏覽的讀者？
- 有沒有截斷的座標軸、不一致的間隔，或扭曲感知的 3D 效果？

### 6. 評估敘事和結論

檢視：

- 結論有沒有被呈現的資料支持
- 有沒有承認其他可能的解釋
- 不確定性有沒有被適當地傳達
- 建議是不是從發現合乎邏輯地推導出來
- 信心程度跟證據強度相符嗎

### 7. 建議改進

提供具體、可執行的建議：

- 能強化結論的額外分析
- 應該註明的但書或限制
- 針對重點更好的視覺化或呈現方式
- 利害關係人會想要的缺漏脈絡

### 8. 產出信心評估

用三個等級評分：

**Ready to share** -- 分析在方法論上站得住腳、計算已驗證、但書已註明。有一些小的改進建議，但沒有阻擋分享的問題。

**Share with noted caveats** -- 分析大致正確，但有特定的限制或假設，必須傳達給利害關係人。列出必須附上的但書。

**Needs revision** -- 發現了具體的錯誤、方法論問題或缺漏的分析，分享前應該先處理。依優先順序列出必須做的修改。

## 輸出格式

```
## Validation Report

### Overall Assessment: [Ready to share | Share with caveats | Needs revision]

### Methodology Review
[Findings about approach, data selection, definitions]

### Issues Found
1. [Severity: High/Medium/Low] [Issue description and impact]
2. ...

### Calculation Spot-Checks
- [Metric]: [Verified / Discrepancy found]
- ...

### Visualization Review
[Any issues with charts or visual presentation]

### Suggested Improvements
1. [Improvement and why it matters]
2. ...

### Required Caveats for Stakeholders
- [Caveat that must be communicated]
- ...
```

---

## 交付前 QA 檢查清單

在跟利害關係人分享任何分析之前，先跑一遍這份檢查清單。

### 資料品質檢查

- [ ] **來源驗證**：確認用了哪些資料表/資料來源。它們對這個問題來說是對的嗎？
- [ ] **新鮮度**：資料夠新，足以做這份分析。已註明「as of」日期。
- [ ] **完整性**：時間序列沒有非預期的缺口，也沒有缺少的區段。
- [ ] **Null 處理**：檢查了關鍵欄位的 null 比例。null 有被適當處理（排除、補值或標記）。
- [ ] **去重**：確認沒有因為錯誤的 join 或重複的來源紀錄而重複計算。
- [ ] **Filter 驗證**：所有 WHERE 子句和 filter 都正確，沒有非預期的排除。

### 計算檢查

- [ ] **彙總邏輯**：GROUP BY 包含所有未被彙總的欄位。彙總層級跟分析的粒度一致。
- [ ] **分母正確性**：比率和百分比的計算用了正確的分母，且分母不為零。
- [ ] **日期對齊**：比較用的是相同長度的時間區間。不完整的區間已排除或註明。
- [ ] **Join 正確性**：JOIN 類型適當（INNER vs LEFT）。多對多的 join 沒有讓計數膨脹。
- [ ] **指標定義**：指標跟利害關係人的定義一致。任何偏離都已註明。
- [ ] **小計加總**：部分加起來等於整體。如果沒有，要解釋原因（例如有重疊）。

### 合理性檢查

- [ ] **數量級**：數字在合理範圍內。營收不是負的。百分比介於 0-100%。
- [ ] **趨勢連續性**：時間序列沒有無法解釋的暴增或暴跌。
- [ ] **交叉比對**：關鍵數字跟其他已知來源一致（dashboard、之前的報告、財務資料）。
- [ ] **數量級概估**：總營收落在合理的大致範圍。使用者數跟已知的數字吻合。
- [ ] **Edge case**：邊界會發生什麼事？空的區段、零活動的期間、新的實體。

### 呈現檢查

- [ ] **圖表正確性**：長條圖從零開始。座標軸有標示。各面板刻度一致。
- [ ] **數字格式**：精確度適當。貨幣/百分比格式一致。需要的地方有千分位符號。
- [ ] **標題清晰**：標題寫出洞察，不只是指標。有標明日期範圍。
- [ ] **但書透明**：已知的限制和假設都明確寫出來。
- [ ] **可重現**：別人能依照提供的文件重做這份分析。

## 常見的資料分析陷阱

### Join 爆炸

**問題**：多對多的 join 默默地讓列數倍增，使計數和總和膨脹。

**怎麼偵測**：
```sql
-- 檢查 join 前後的列數
SELECT COUNT(*) FROM table_a;  -- 1,000
SELECT COUNT(*) FROM table_a a JOIN table_b b ON a.id = b.a_id;  -- 3,500 (糟了)
```

**怎麼預防**：
- join 之後一定要檢查列數
- 如果計數增加，調查 join 的關係（真的是 1:1 還是 1:many？）
- 透過 join 計算實體數量時，用 `COUNT(DISTINCT a.id)`，不要用 `COUNT(*)`

### 存活者偏誤

**問題**：只分析現在還存在的實體，忽略被刪除、流失或失敗的。

**範例**：
- 分析「現有使用者」的行為，會漏掉已流失的使用者
- 看「使用我們產品的公司」，忽略了評估過後離開的公司
- 只研究「成功」結果的特性，沒有「不成功」的

**怎麼預防**：下結論前先問「誰不在這個資料集裡？」

### 不完整期間比較

**問題**：拿不完整的期間跟完整的期間比較。

**範例**：
- 「一月營收 $500K，十二月是 $800K」-- 但一月還沒結束
- 「這週的註冊數下降」-- 週三查的，卻跟完整的上一週比

**怎麼預防**：一律只取完整的期間，或比較每月同一天/相同天數。

### 分母漂移

**問題**：不同期間的分母改變了，讓比率沒辦法比較。

**範例**：
- 轉換率變好，是因為你改了「符合資格」使用者的計算方式
- 流失率改變，是因為「活躍」的定義更新了

**怎麼預防**：所有被比較的期間都用一致的定義。註明任何定義的變動。

### 平均的平均

**問題**：各組大小不同時，把預先算好的平均再拿來平均，會得到錯誤的結果。

**範例**：
- A 組：100 位使用者，平均營收 $50
- B 組：10 位使用者，平均營收 $200
- 錯誤：平均的平均 = ($50 + $200) / 2 = $125
- 正確：加權平均 = (100*$50 + 10*$200) / 110 = $63.64

**怎麼預防**：一律從原始資料彙總。絕對不要拿預先彙總好的平均再去平均。

### 時區不一致

**問題**：不同的資料來源用不同的時區，造成對不齊。

**範例**：
- 事件時間戳是 UTC，但面向使用者的日期是當地時間
- 每日彙總用了不同的截止時間

**怎麼預防**：分析前先把所有時間戳統一成單一時區（建議用 UTC）。記錄所用的時區。

### 分群時的選擇偏誤

**問題**：用你要衡量的結果來定義分群，形成循環邏輯。

**範例**：
- 「完成 onboarding 的使用者留存率較高」-- 當然，他們是自我篩選的
- 「重度使用者創造更多營收」-- 他們就是因為創造營收才變成重度使用者

**怎麼預防**：用處理前的特徵來定義分群，不要用結果。

### 其他統計陷阱

- **Simpson's paradox**：資料彙總與分群後，趨勢反轉
- **把相關當成因果**，卻沒有佐證
- **樣本數太小**，導致結論不可靠
- **離群值不成比例地影響平均**（是不是該改用中位數？）
- **多重檢定 / 挑選**顯著的結果
- **Look-ahead bias**：用未來的資訊來解釋過去的事件
- **挑選有利於特定敘事的時間範圍**

## 結果合理性檢查

### 數量級檢查

分析中的任何關鍵數字，都要驗證它通過「直覺測試」：

| 指標類型 | 合理性檢查 |
|---|---|
| 使用者數 | 跟已知的 MAU/DAU 數字吻合嗎？ |
| 營收 | 跟已知的 ARR 相比，數量級對嗎？ |
| 轉換率 | 介於 0% 到 100% 嗎？跟 dashboard 的數字吻合嗎？ |
| 成長率 | 50% 以上的 MoM 成長實際嗎，還是資料有問題？ |
| 平均值 | 就你對分佈的了解，這個平均合理嗎？ |
| 百分比 | 各分群的百分比加起來約 100% 嗎？ |

### 交叉驗證技巧

1. **用兩種不同方式計算同一個指標**，驗證結果一致
2. **抽查個別紀錄**：挑幾個特定實體，手動追蹤它們的資料
3. **跟已知的基準比較**：對照已發布的 dashboard、財務報告或先前的分析
4. **反推**：如果總營收是 X，每位使用者營收乘以使用者數大約等於 X 嗎？
5. **邊界檢查**：篩選到單一天、單一使用者或單一類別時會怎樣？這些微觀的結果合理嗎？

### 需要調查的紅旗

- 任何環比變動超過 50%、卻沒有明顯原因的指標
- 剛好是整數的計數或總和（暗示 filter 或預設值有問題）
- 剛好是 0% 或 100% 的比率（可能表示資料不完整）
- 完美印證假設的結果（現實通常比較雜亂）
- 跨時間區間或分群出現完全相同的值（暗示查詢忽略了某個維度）

## 可重現性的文件標準

### 分析文件範本

每份不是微不足道的分析都應該包含：

```markdown
## Analysis: [Title]

### Question
[The specific question being answered]

### Data Sources
- Table: [schema.table_name] (as of [date])
- Table: [schema.other_table] (as of [date])
- File: [filename] (source: [where it came from])

### Definitions
- [Metric A]: [Exactly how it's calculated]
- [Segment X]: [Exactly how membership is determined]
- [Time period]: [Start date] to [end date], [timezone]

### Methodology
1. [Step 1 of the analysis approach]
2. [Step 2]
3. [Step 3]

### Assumptions and Limitations
- [Assumption 1 and why it's reasonable]
- [Limitation 1 and its potential impact on conclusions]

### Key Findings
1. [Finding 1 with supporting evidence]
2. [Finding 2 with supporting evidence]

### SQL Queries
[All queries used, with comments]

### Caveats
- [Things the reader should know before acting on this]
```

### 程式碼文件

任何可能被重複使用的程式碼（SQL、Python）：

```python
"""
Analysis: Monthly Cohort Retention
Author: [Name]
Date: [Date]
Data Source: events table, users table
Last Validated: [Date] -- results matched dashboard within 2%

Purpose:
    Calculate monthly user retention cohorts based on first activity date.

Assumptions:
    - "Active" means at least one event in the month
    - Excludes test/internal accounts (user_type != 'internal')
    - Uses UTC dates throughout

Output:
    Cohort retention matrix with cohort_month rows and months_since_signup columns.
    Values are retention rates (0-100%).
"""
```

### 分析的版本控制

- 把查詢和程式碼存在版本控制（git）或共用的文件系統裡
- 註明所用資料快照的日期
- 如果分析用更新後的資料重跑，記錄改了什麼、為什麼
- 連到週期性分析的先前版本，方便比較趨勢

## 範例

```
/validate-data Review this quarterly revenue analysis before I send it to the exec team: [analysis]
```

```
/validate-data Check my churn analysis -- I'm comparing Q4 churn rates to Q3 but Q4 has a shorter measurement window
```

```
/validate-data Here's a SQL query and its results for our conversion funnel. Does the logic look right? [query + results]
```

## 小訣竅

- 任何高風險的簡報或決策之前，都先跑 /validate-data
- 就算是快速的分析，也值得做合理性檢查，只要一分鐘，卻能保住你的信譽
- 如果驗證發現問題，修好之後再重新驗證
- 把驗證的輸出跟分析一起分享，建立利害關係人的信心
