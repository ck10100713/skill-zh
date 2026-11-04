---
name: "ops-meeting-minutes"
description: "製作結構化的會議紀錄，包含決議、待辦事項和後續追蹤。使用者需要有效記錄會議、追蹤待辦事項、提升會議的生產力，或建立會議筆記系統時使用，就算他們說的是「幫這場會議做筆記」、「剛剛決定了什麼」、「誰負責什麼」或「我們開會都沒有後續」也一樣。"
metadata:
  category: "WP-10 通用商業"
  tags: ["business", "meetings", "documentation", "productivity"]
---

# 會議紀錄

## 框架

```
IRON LAW: Every Meeting Must Produce Decisions + Action Items

If a meeting ends with no documented decisions and no action items with
owners and deadlines, the meeting was a waste of time. Capture these
DURING the meeting, not after. Minutes without action items are a diary.
```

### 會議紀錄範本

```markdown
# Meeting: {Title}
Date: {YYYY-MM-DD} | Time: {HH:MM-HH:MM} | Location: {room/link}
Attendees: {names}
Absent: {names}
Facilitator: {name} | Note-taker: {name}

## Agenda
1. {topic 1} — {presenter} ({X min})
2. {topic 2} — {presenter} ({X min})
3. {topic 3} — {presenter} ({X min})

## Discussion Notes
### {Topic 1}
- {Key point discussed}
- {Different viewpoints raised}
- **DECISION**: {what was decided}

### {Topic 2}
- {Key point}
- **DECISION**: {what was decided} / **DEFERRED**: {to when/what condition}

## Action Items
| # | Action | Owner | Deadline | Status |
|---|--------|-------|----------|--------|
| 1 | {specific task} | {name} | {date} | Open |
| 2 | {specific task} | {name} | {date} | Open |

## Next Meeting
- Date: {next meeting date}
- Agenda items for next time: {carry-over items}
```

### 待辦事項格式：WHO + WHAT + WHEN

不好：「跟進定價的問題」
好：「**@Sarah** 在 **4 月 10 日**前準備好與 3 家競爭對手的定價比較表」

### 提升會議效率的小技巧

1. **先有議程**：在會議開始前 24 小時以上發出議程
2. **限定時間**：為每個議題設定時間上限。用看得見的計時器。
3. **停車場（Parking lot）**：離題的事項放進「停車場」清單留待之後處理，不要讓會議偏掉
4. **最後 5 分鐘**：留來總結決議和待辦事項
5. **24 小時內發出**：當天或隔天早上就把紀錄寄出，趁大家還記得

### AI 會議工具

| 工具 | 能力 | 最適合 |
|------|-----------|----------|
| **Otter.ai** | 逐字稿 + 摘要 | 英文會議 |
| **Fireflies.ai** | 逐字稿 + 擷取待辦事項 | 團隊會議 |
| **Claude/GPT** | 摘要逐字稿、擷取決議 | 會後處理 |
| **Notion AI** | 在情境中做會議筆記 | 用 Notion 的團隊 |

就算有 AI 逐字稿，還是要有一位真人記錄者即時記下「決議」和「待辦事項」。AI 記錄的是說了什麼；人記錄的是「決定」了什麼。

## 輸出格式

```markdown
# Meeting Minutes: {Title} — {Date}

## Decisions Made
1. {decision + context}
2. {decision}

## Action Items
| # | Action | Owner | Deadline |
|---|--------|-------|----------|
| 1 | {task} | {name} | {date} |

## Key Discussion Points
- {summary of important discussion, not verbatim}

## Parking Lot (for future discussion)
- {deferred topic}
```

## 注意事項

- **會議紀錄 ≠ 逐字稿**：不要把說的每句話都記下來。要記的是：決議、待辦事項、關鍵的意見分歧，以及日後理解這些決議所需要的脈絡。
- **沒有期限的待辦事項不會被完成**：「ASAP」不是期限。每個待辦事項都需要具體的日期。
- **記錄者有權力**：他們決定什麼被記成「決議」。要有意識地指派這個角色。
- **要追蹤待辦事項**：寄出後沒有追蹤的紀錄會被忽略。在下一次會議「一開始」就檢視待辦事項的狀態。
- **定期會議需要結構**：每週站會、每月檢討和每季規劃，各自需要不同的紀錄格式。一種格式不適用所有情況。

## 參考資料

- 會議主持技巧請看 `references/facilitation.md`
