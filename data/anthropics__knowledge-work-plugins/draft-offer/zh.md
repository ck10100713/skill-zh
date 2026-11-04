---
name: draft-offer
description: 起草附薪酬細節和條款的 offer letter。候選人準備好發 offer、要組出總薪酬方案（base、equity、簽約金）、撰寫 offer letter 本文，或為用人主管準備談判指引時使用。
argument-hint: "<role and level>"
---

# /draft-offer

> 如果看到不熟悉的佔位符，或需要確認目前連接了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

為新進員工起草一份完整的 offer letter。

## 用法

```
/draft-offer $ARGUMENTS
```

## 我需要你提供什麼

- **職位與職稱**：什麼職位？
- **職級**：Junior、Mid、Senior、Staff 等
- **地點**：他們會在哪裡工作？（會影響薪酬和福利）
- **薪酬**：Base salary、equity、簽約金（如適用）
- **到職日**：什麼時候開始？
- **用人主管**：他們要向誰報告？

如果你沒有所有細節，我會幫你一起想。

## 輸出

```markdown
## Offer Letter Draft: [Role] — [Level]

### Compensation Package
| Component | Details |
|-----------|---------|
| **Base Salary** | $[X]/year |
| **Equity** | [X shares/units], [vesting schedule] |
| **Signing Bonus** | $[X] (if applicable) |
| **Target Bonus** | [X]% of base (if applicable) |
| **Total First-Year Comp** | $[X] |

### Terms
- **Start Date**: [Date]
- **Reports To**: [Manager]
- **Location**: [Office / Remote / Hybrid]
- **Employment Type**: [Full-time, Exempt]

### Benefits Summary
[Key benefits highlights relevant to the candidate]

### Offer Letter Text

Dear [Candidate Name],

We are pleased to offer you the position of [Title] at [Company]...

[Complete offer letter text]

### Notes for Hiring Manager
- [Negotiation guidance if needed]
- [Comp band context]
- [Any flags or considerations]
```

## 如果有連接 connector

如果有連接 **~~HRIS**：
- 拉出該職級／職位的薪資級距資料
- 確認 headcount 已核准
- 自動帶入福利細節

如果有連接 **~~ATS**：
- 從應徵資料拉出候選人詳細資訊
- 在 pipeline 裡更新 offer 狀態

## 小提醒

1. **要列出總薪酬**：候選人比的是總薪酬，不只是 base。
2. **equity 要具體**：股數、目前的估值方式、vesting 時程。
3. **要個人化**：引用面試過程中的某件事，讓它有溫度。
