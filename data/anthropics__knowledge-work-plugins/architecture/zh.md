---
name: architecture
description: 建立或評估架構決策紀錄（ADR）。適用於在多個技術之間做選擇（例如 Kafka vs SQS）、把設計決策連同取捨和後果記錄下來、審查系統設計提案，或根據需求和限制設計新元件。
argument-hint: "<decision or system to design>"
---

# /architecture

> 如果看到不熟悉的佔位符，或需要確認目前連了哪些工具，請見 [CONNECTORS.md](../../CONNECTORS.md)。

建立架構決策紀錄（ADR）或評估系統設計。

## 用法

```
/architecture $ARGUMENTS
```

## 模式

**建立 ADR**："Should we use Kafka or SQS for our event bus?"
**評估設計**："Review this microservices proposal"
**系統設計**："Design the notification system for our app"

需求蒐集、可擴充性分析和取捨評估的詳細框架，請見 **system-design** skill。

## 輸出：ADR 格式

```markdown
# ADR-[number]: [Title]

**Status:** Proposed | Accepted | Deprecated | Superseded
**Date:** [Date]
**Deciders:** [Who needs to sign off]

## Context
[What is the situation? What forces are at play?]

## Decision
[What is the change we're proposing?]

## Options Considered

### Option A: [Name]
| Dimension | Assessment |
|-----------|------------|
| Complexity | [Low/Med/High] |
| Cost | [Assessment] |
| Scalability | [Assessment] |
| Team familiarity | [Assessment] |

**Pros:** [List]
**Cons:** [List]

### Option B: [Name]
[Same format]

## Trade-off Analysis
[Key trade-offs between options with clear reasoning]

## Consequences
- [What becomes easier]
- [What becomes harder]
- [What we'll need to revisit]

## Action Items
1. [ ] [Implementation step]
2. [ ] [Follow-up]
```

## 如果有連接器可用

如果有連接 **~~knowledge base**：
- 搜尋先前的 ADR 和設計文件
- 找出相關的技術背景

如果有連接 **~~project tracker**：
- 連結到相關的 epic 和工單
- 建立實作任務

## 小技巧

1. **先講清楚限制**："We need to ship in 2 weeks" 或 "Must handle 10K rps" 會左右答案。
2. **把選項列出名字**：即使你已經傾向某一邊，有明確的替代方案，我也能給出更平衡的分析。
3. **把非功能需求也放進來**：延遲、成本、團隊專長和維護負擔，跟功能一樣重要。
