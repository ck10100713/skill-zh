---
name: on-call-handoff-patterns
description: 精通 on-call 輪班交接，包含 context 傳遞、升級程序與文件記錄。在工程師之間交接 on-call 責任並確保接手的人掌握完整狀況、撰寫涵蓋進行中事件、調查中問題與近期變更的班次摘要、在事件處理到一半時交接讓新工程師能接下 incident commander 角色而不遺失 context、首次讓新工程師加入 on-call 輪值，或稽核並改善各團隊現有交接流程的品質時使用。
---

# On-Call Handoff Patterns

on-call 班次轉換的有效模式，確保跨班次的連續性、context 傳遞與可靠的事件應變。

## When to Use This Skill

- 交接 on-call 責任
- 撰寫班次交接摘要
- 記錄進行中的調查
- 建立 on-call 輪值程序
- 改善交接品質
- 讓新的 on-call 工程師上手

## Core Concepts

### 1. Handoff Components

| Component                  | Purpose                 |
| -------------------------- | ----------------------- |
| **Active Incidents**       | 目前壞掉的東西 |
| **Ongoing Investigations** | 正在除錯的問題   |
| **Recent Changes**         | 部署、設定變更    |
| **Known Issues**           | 已經採用的替代做法    |
| **Upcoming Events**        | 維護、發布   |

### 2. Handoff Timing

```
Recommended: 30 min overlap between shifts

Outgoing:
├── 15 min: Write handoff document
└── 15 min: Sync call with incoming

Incoming:
├── 15 min: Review handoff document
├── 15 min: Sync call with outgoing
└── 5 min: Verify alerting setup
```

## Templates and detailed worked examples

完整的範本庫與詳細的範例放在 `references/details.md`。需要具體範本時，再去讀那個檔案。

## Troubleshooting

**接手的工程師因為交接文件不完整，漏掉了一個關鍵問題。**
把交班檢查清單當作關卡：每個段落至少要有一筆內容（或明確寫「無」），才能標記為交接完成。把不完整的交接列為 blameless postmortem 的行動項目。

**因為時區差異，沒辦法開 30 分鐘的同步通話。**
退而使用非同步的快速交接範本（Template 2）。再補上一段簡短的 Loom 或語音備忘，帶過觀察清單。確保接手的工程師有直接的聯絡方式，萬一有後續問題可以問。

**接手的工程師一接班就碰上處理到一半的事件，立刻不知所措。**
專門使用事件交接範本（Template 3）。交班的工程師在交接後的 15 分鐘內，即使已經下班，也應該留在 Slack 上待命，回答釐清用的問題。

**各團隊的 on-call 交接文件格式不一致。**
全組織採用班次交接範本，並把完成的交接文件存放在共用位置（wiki、Notion、Confluence）。在 PagerDuty 的 on-call 排班條目中連結每一份交接文件。

**接手的工程師在交班的人下線前，無法確認自己的警報有在運作。**
加入一個標準步驟：交班的工程師發送一則測試警報，確認接手的工程師在 PagerDuty 和 Slack 都收到了，才結束重疊的時間窗口。

## Related Skills

- [incident-runbook-templates](../incident-runbook-templates/SKILL.md) — 處理中途交接的事件所用的 runbook
- [postmortem-writing](../postmortem-writing/SKILL.md) — 把班次中已解決的事件整理成結構化的 postmortem
