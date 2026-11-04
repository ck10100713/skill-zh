---
name: sprint-planning
description: 規劃 sprint：界定工作範圍、估算產能、設定目標，並起草 sprint 計畫。適用於啟動新 sprint、依團隊可用時間（含請假和會議）評估 backlog 的份量、決定哪些是 P0、哪些是 stretch，或處理上個 sprint 的延遞項目。
argument-hint: "[sprint name or date range]"
---

# /sprint-planning

> 如果看到不熟悉的佔位符，或需要確認哪些工具已連接，請見 [CONNECTORS.md](../../CONNECTORS.md)。

規劃 sprint：界定工作範圍、估算產能、設定明確的目標。

## 用法

```
/sprint-planning $ARGUMENTS
```

## 運作方式

```
┌─────────────────────────────────────────────────────────────────┐
│                    SPRINT PLANNING                                 │
├─────────────────────────────────────────────────────────────────┤
│  獨立運作（永遠可用）                                              │
│  ✓ 定義 sprint 目標和成功標準                                     │
│  ✓ 估算團隊產能（含請假、會議）                                   │
│  ✓ 界定範圍並排定 backlog 項目的優先順序                          │
│  ✓ 找出相依性和風險                                               │
│  ✓ 產生 sprint 計畫文件                                           │
├─────────────────────────────────────────────────────────────────┤
│  加強版（連接工具之後）                                            │
│  + 專案追蹤工具：拉 backlog、建立 sprint、指派項目                │
│  + 行事曆：把請假和會議算進產能                                   │
│  + 聊天：把 sprint 計畫分享給團隊                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 我需要你提供什麼

- **團隊**：團隊有誰？這個 sprint 各自的可用時間？
- **Sprint 長度**：幾天／幾週？
- **Backlog**：優先順序是什麼？（從追蹤工具拉、貼上，或用說的）
- **延遞項目**：上個 sprint 有沒有沒做完的？
- **相依性**：有沒有卡在其他團隊的事？

## 輸出

```markdown
## Sprint Plan: [Sprint Name]
**Dates:** [Start] — [End] | **Team:** [X] engineers
**Sprint Goal:** [One clear sentence about what success looks like]

### Capacity
| Person | Available Days | Allocation | Notes |
|--------|---------------|------------|-------|
| [Name] | [X] of [Y] | [X] points/hours | [PTO, on-call, etc.] |
| **Total** | **[X]** | **[X] points** | |

### Sprint Backlog
| Priority | Item | Estimate | Owner | Dependencies |
|----------|------|----------|-------|--------------|
| P0 | [Must ship] | [X] pts | [Person] | [None / Blocked by X] |
| P1 | [Should ship] | [X] pts | [Person] | [None] |
| P2 | [Stretch] | [X] pts | [Person] | [None] |

### Planned Capacity: [X] points | Sprint Load: [X] points ([X]% of capacity)

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk] | [What happens] | [What to do] |

### Definition of Done
- [ ] Code reviewed and merged
- [ ] Tests passing
- [ ] Documentation updated (if applicable)
- [ ] Product sign-off

### Key Dates
| Date | Event |
|------|-------|
| [Date] | Sprint start |
| [Date] | Mid-sprint check-in |
| [Date] | Sprint end / Demo |
| [Date] | Retro |
```

## 小提醒

1. **留緩衝**：規劃到產能的 70-80% 就好。一定會有插進來的事。
2. **一個明確的 sprint 目標**：如果一句話講不完，這個 sprint 就沒有焦點。
3. **找出 stretch 項目**：事情比預期久的時候，要知道該砍什麼。
4. **誠實地延遞**：如果有東西沒出貨，重新承諾之前先搞清楚原因。
