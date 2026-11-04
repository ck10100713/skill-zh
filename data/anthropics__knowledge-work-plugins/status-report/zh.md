---
name: status-report
description: 產生包含 KPI、風險和待辦事項的狀態報告。適用於撰寫給領導層的週報或月報、用 green/yellow/red 狀態摘要專案健康度、浮出需要利害關係人注意的風險和決策，或把一堆專案追蹤工具的活動整理成好讀的敘述。
argument-hint: "[weekly | monthly | quarterly] [project or team]"
---

# /status-report

> 如果看到不熟悉的佔位符，或需要確認哪些工具已連接，請見 [CONNECTORS.md](../../CONNECTORS.md)。

為領導層或利害關係人產生一份完整的狀態報告。風險矩陣框架和嚴重度定義請見 **risk-assessment** skill。

## 用法

```
/status-report $ARGUMENTS
```

## 輸出

```markdown
## Status Report: [Project/Team] — [Period]
**Author:** [Name] | **Date:** [Date]

### Executive Summary
[3-4 sentence overview — what's on track, what needs attention, key wins]

### Overall Status: 🟢 On Track / 🟡 At Risk / 🔴 Off Track

### Key Metrics
| Metric | Target | Actual | Trend | Status |
|--------|--------|--------|-------|--------|
| [KPI] | [Target] | [Actual] | [up/down/flat] | 🟢/🟡/🔴 |

### Accomplishments This Period
- [Win 1]
- [Win 2]

### In Progress
| Item | Owner | Status | ETA | Notes |
|------|-------|--------|-----|-------|
| [Item] | [Person] | [Status] | [Date] | [Context] |

### Risks and Issues
| Risk/Issue | Impact | Mitigation | Owner |
|------------|--------|------------|-------|
| [Risk] | [Impact] | [What we're doing] | [Who] |

### Decisions Needed
| Decision | Context | Deadline | Recommended Action |
|----------|---------|----------|--------------------|
| [Decision] | [Why it matters] | [When] | [What I recommend] |

### Next Period Priorities
1. [Priority 1]
2. [Priority 2]
3. [Priority 3]
```

## 有連接器時

如果已連接 **~~project tracker**：
- 自動拉專案狀態、已完成項目和即將到來的里程碑
- 找出有風險的項目和逾期的任務

如果已連接 **~~chat**：
- 掃描近期團隊討論，找出要放進來的決策和阻礙
- 提議把完成的報告貼到頻道

如果已連接 **~~calendar**：
- 引用報告期間內的重要會議和決策

## 小提醒

1. **先講標題重點**：忙碌的領導者只讀前 3 行。要讓它們有份量。
2. **對風險誠實**：早點浮出問題能建立信任。意外會侵蝕信任。
3. **讓決策容易做**：每個需要的決策，都要提供脈絡和建議。
