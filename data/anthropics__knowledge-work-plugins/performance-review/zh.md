---
name: performance-review
description: 規劃績效考核的結構，包含自評、主管評核範本和校準（calibration）準備。在考核季開始、需要自評範本、為直屬下屬撰寫主管評核、為校準會議準備評等分布和升遷案例，或把模糊的回饋改寫成具體的行為例子時使用。
argument-hint: "<employee name or review cycle>"
---

# /performance-review

> 如果看到不熟的佔位符，或需要確認目前連了哪些工具，請見 [CONNECTORS.md](../../CONNECTORS.md)。

產生績效考核範本，並協助整理回饋的結構。

## 用法

```
/performance-review $ARGUMENTS
```

## 模式

```
/performance-review self-assessment       # 產生自評範本
/performance-review manager [employee]    # 針對特定人員的主管評核範本
/performance-review calibration           # 校準準備文件
```

如果沒有指定模式，就問他們需要哪一種考核。

## 輸出：自評範本

```markdown
## Self-Assessment: [Review Period]

### Key Accomplishments
[List your top 3-5 accomplishments this period. For each, describe the situation, your contribution, and the impact.]

1. **[Accomplishment]**
   - Situation: [Context]
   - Contribution: [What you did]
   - Impact: [Measurable result]

### Goals Review
| Goal | Status | Evidence |
|------|--------|----------|
| [Goal from last period] | Met / Exceeded / Missed | [How you know] |

### Growth Areas
[Where did you grow? New skills, expanded scope, leadership moments.]

### Challenges
[What was hard? What would you do differently?]

### Goals for Next Period
1. [Goal — specific and measurable]
2. [Goal]
3. [Goal]

### Feedback for Manager
[How can your manager better support you?]
```

## 輸出：主管評核

```markdown
## Performance Review: [Employee Name]
**Period:** [Date range] | **Manager:** [Your name]

### Overall Rating: [Exceeds / Meets / Below Expectations]

### Performance Summary
[2-3 sentence overall assessment]

### Key Strengths
- [Strength with specific example]
- [Strength with specific example]

### Areas for Development
- [Area with specific, actionable guidance]
- [Area with specific, actionable guidance]

### Goal Achievement
| Goal | Rating | Comments |
|------|--------|----------|
| [Goal] | [Rating] | [Specific observations] |

### Impact and Contributions
[Describe their biggest contributions and impact on the team/org]

### Development Plan
| Skill | Current | Target | Actions |
|-------|---------|--------|---------|
| [Skill] | [Level] | [Level] | [How to get there] |

### Compensation Recommendation
[Promotion / Equity refresh / Adjustment / No change — with justification]
```

## 輸出：校準

```markdown
## Calibration Prep: [Review Cycle]
**Manager:** [Your name] | **Team:** [Team] | **Period:** [Date range]

### Team Overview
| Employee | Role | Level | Tenure | Proposed Rating | Notes |
|----------|------|-------|--------|-----------------|-------|
| [Name] | [Role] | [Level] | [X years] | [Rating] | [Key context] |

### Rating Distribution
| Rating | Count | % of Team | Company Target |
|--------|-------|-----------|----------------|
| Exceeds Expectations | [X] | [X]% | ~15-20% |
| Meets Expectations | [X] | [X]% | ~60-70% |
| Below Expectations | [X] | [X]% | ~10-15% |

### Calibration Discussion Points
1. **[Employee]** — [Why this rating may need discussion, e.g., borderline, first review at level, recent role change]
2. **[Employee]** — [Discussion point]

### Promotion Candidates
| Employee | Current Level | Proposed Level | Justification |
|----------|-------------|----------------|---------------|
| [Name] | [Current] | [Proposed] | [Evidence of next-level performance] |

### Compensation Actions
| Employee | Action | Justification |
|----------|--------|---------------|
| [Name] | [Promotion / Equity refresh / Market adjustment / Retention] | [Why] |

### Manager Notes
[Context the calibration group should know — team changes, org shifts, project impacts]
```

## 如果有可用的 Connector

如果 **~~HRIS** 已連接：
- 拉取過往的考核紀錄和目標追蹤資料
- 預先填入員工資料和目前的職務資訊

如果 **~~project tracker** 已連接：
- 拉取考核期間完成的工作與貢獻
- 引用具體的 ticket 和專案里程碑作為佐證

## 小技巧

1. **要具體**：「做得很好」不算回饋。「你導入新的 CI pipeline，把部署時間縮短了 40%」才是。
2. **正面與建設性並重**：兩者都不可少。兩者都不該讓人意外。
3. **聚焦行為，不談人格**：說「你的文件一直不完整」，而不是「你很粗心」。
4. **讓發展可以執行**：「改善溝通」很模糊。「在下次團隊全體會議上做簡報」才是可執行的。
