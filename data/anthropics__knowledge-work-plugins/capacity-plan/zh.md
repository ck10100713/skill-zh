---
name: capacity-plan
description: 規劃資源容量，做工作量分析和使用率預測。當進入季度規劃、團隊覺得負荷過重而你需要數字、要決定該招人還是降低優先順序，或要壓力測試即將到來的專案塞不塞得進現有人力時使用。
argument-hint: "<team or project scope>"
---

# /capacity-plan

> 如果看到不熟的 placeholder，或需要確認目前連了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

分析團隊容量，規劃資源分配。

## 用法

```
/capacity-plan $ARGUMENTS
```

## 我需要你提供什麼

- **團隊規模與角色**：你有哪些人？
- **目前的工作量**：他們在做什麼？（從專案追蹤工具上傳，或自己描述）
- **即將到來的工作**：下一季有什麼要做？
- **限制條件**：預算、招聘時程、技能需求

## 規劃面向

### 人
- 可用的人數與技能
- 目前的分配與使用率
- 計畫中的招聘與時程
- 外包人員與廠商的容量

### 預算
- 各類別的營運預算
- 專案專屬預算
- 差異追蹤
- 預測 vs. 實際

### 時間
- 專案時程與相依關係
- 關鍵路徑分析
- 緩衝與應變規劃
- 期限管理

## 使用率目標

| 角色類型 | 目標使用率 | 備註 |
|-----------|-------------------|-------|
| IC / 專家 | 75-80% | 留空間給突發工作和成長 |
| 主管 | 60-70% | 管理負擔、會議、1:1 |
| On-call / 支援 | 50-60% | 被打斷的工作無法預測 |

## 常見陷阱

- 規劃到 100% 使用率（沒有緩衝應付意外）
- 忽略會議量和切換情境的成本
- 沒算進休假、假日和病假
- 把所有工時當成一樣（創意工作 ≠ 行政工作）

## 輸出

```markdown
## Capacity Plan: [Team/Project]
**Period:** [Date range] | **Team Size:** [X]

### Current Utilization
| Person/Role | Capacity | Allocated | Available | Utilization |
|-------------|----------|-----------|-----------|-------------|
| [Name/Role] | [hrs/wk] | [hrs/wk] | [hrs/wk] | [X]% |

### Capacity Summary
- **Total capacity**: [X] hours/week
- **Currently allocated**: [X] hours/week ([X]%)
- **Available**: [X] hours/week ([X]%)
- **Overallocated**: [X people above 100%]

### Upcoming Demand
| Project/Initiative | Start | End | Resources Needed | Gap |
|--------------------|-------|-----|-----------------|-----|
| [Project] | [Date] | [Date] | [X FTEs] | [Covered/Gap] |

### Bottlenecks
- [Skill or role that's oversubscribed]
- [Time period with a crunch]

### Recommendations
1. [Hire / Contract / Reprioritize / Delay]
2. [Specific action]

### Scenarios
| Scenario | Outcome |
|----------|---------|
| Do nothing | [What happens] |
| Hire [X] | [What changes] |
| Deprioritize [Y] | [What frees up] |
```

## 如果有連接 connector

如果有連接 **~~project tracker**：
- 自動拉目前的工作量和工單分配
- 顯示每個人即將到來的 sprint 或季度承諾

如果有連接 **~~calendar**：
- 把 PTO、假日和固定會議量納入考量
- 計算每個人實際的可用工時

## 小提醒

1. **把所有工作都算進去**：BAU、專案、支援、會議。人不會 100% 都能投入專案工作。
2. **規劃緩衝**：目標使用率抓 80%。100% 代表沒有空間應付意外。
3. **定期更新**：容量計畫很快就過時。每月檢視一次。
