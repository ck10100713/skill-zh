---
name: people-report
description: 產生人力編制、離職率、多元性或組織健康報告。需要為管理層拉出人力編制快照、依團隊分析離職趨勢、準備多元代表性指標，或評估整個組織的管理幅度和離職風險時使用。
argument-hint: "<report type — headcount, attrition, diversity, org health>"
---

# /people-report

> 如果看到不熟的佔位符，或需要確認目前連了哪些工具，請見 [CONNECTORS.md](../../CONNECTORS.md)。

用你的 HR 資料產生人才分析（people analytics）報告。分析人力資料，找出趨勢、風險和機會。

## 用法

```
/people-report $ARGUMENTS
```

## 報告類型

**人力編制（Headcount）**：目前的組織快照，依團隊、地點、職級、年資
**離職率（Attrition）**：離職分析，自願／非自願、依團隊、趨勢
**多元性（Diversity）**：代表性指標，依職級、團隊、人才管道
**組織健康（Org Health）**：管理幅度、管理層級、團隊規模、離職風險

## 關鍵指標

### 留任
- 整體離職率（自願加非自願）
- 可惜離職率（regrettable attrition）
- 平均年資
- 離職風險指標

### 多元性
- 依職級、團隊和職能的代表性
- 人才管道多元性（依族群區分的招募漏斗）
- 各群體的升遷率
- 薪酬公平分析

### 敬業度（Engagement）
- 調查分數與趨勢
- eNPS（員工淨推薦值）
- 參與率
- 開放式回饋的主題

### 生產力
- 每位員工的營收
- 管理幅度效率
- 新進員工達到生產力的時間

## 做法

1. 了解他們想回答什麼問題
2. 找出正確的資料（上傳、貼上，或從 ~~HRIS 拉取）
3. 用適當的統計方法分析
4. 呈現發現，並附上脈絡和注意事項
5. 根據資料建議具體的行動

## 我需要你提供什麼

上傳 CSV，或描述你的資料。有幫助的欄位：
- 員工姓名／ID、部門、團隊
- 職稱、職級、地點
- 到職日、離職日（如適用）
- 主管、薪酬（如相關）
- 人口統計資料（做多元性報告時，如果有的話）

## 輸出

```markdown
## People Report: [Type] — [Date]

### Executive Summary
[2-3 key takeaways]

### Key Metrics
| Metric | Value | Trend |
|--------|-------|-------|
| [Metric] | [Value] | [up/down/flat] |

### Detailed Analysis
[Charts, tables, and narrative for the specific report type]

### Recommendations
- [Data-driven recommendation]
- [Action item]

### Methodology
[How the numbers were calculated, any caveats]
```

## 如果有可用的 Connector

如果 **~~HRIS** 已連接：
- 拉取即時的員工資料：人力編制、年資、部門、職級
- 不需要上傳 CSV 就能產生報告

如果 **~~chat** 已連接：
- 主動提議把報告摘要分享到相關頻道
