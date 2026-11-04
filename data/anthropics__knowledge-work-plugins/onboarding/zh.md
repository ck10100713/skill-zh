---
name: onboarding
description: 為新進員工產生入職檢查清單和第一週計畫。當有人即將到職、要建立到職前的待辦清單（帳號、設備、buddy）、安排第一天和第一週，或為新團隊成員設定 30/60/90 天目標時使用。
argument-hint: "<new hire name and role>"
---

# /onboarding

> 如果看到不熟的佔位符，或需要確認目前連了哪些工具，請見 [CONNECTORS.md](../../CONNECTORS.md)。

為新的團隊成員產生完整的入職計畫。

## 用法

```
/onboarding $ARGUMENTS
```

## 我需要你提供什麼

- **新進員工姓名**：誰要來報到？
- **職位**：什麼職位？
- **團隊**：加入哪個團隊？
- **到職日**：什麼時候開始？
- **主管**：直屬主管是誰？

## 輸出

```markdown
## Onboarding Plan: [Name] — [Role]
**Start Date:** [Date] | **Team:** [Team] | **Manager:** [Manager]

### Pre-Start (Before Day 1)
- [ ] Send welcome email with start date, time, and logistics
- [ ] Set up accounts: email, Slack, [tools for role]
- [ ] Order equipment (laptop, monitor, peripherals)
- [ ] Add to team calendar and recurring meetings
- [ ] Assign onboarding buddy: [Suggested person]
- [ ] Prepare desk / remote setup instructions

### Day 1
| Time | Activity | With |
|------|----------|------|
| 9:00 | Welcome and orientation | Manager |
| 10:00 | IT setup and tool walkthrough | IT / Buddy |
| 11:00 | Team introductions | Team |
| 12:00 | Welcome lunch | Manager + Team |
| 1:30 | Company overview and values | Manager |
| 3:00 | Role expectations and 30/60/90 plan | Manager |
| 4:00 | Free time to explore tools and docs | Self |

### Week 1
- [ ] Complete required compliance training
- [ ] Read key documentation: [list for role]
- [ ] 1:1 with each team member
- [ ] Shadow key meetings
- [ ] First small task or project assigned
- [ ] End-of-week check-in with manager

### 30-Day Goals
1. [Goal aligned to role]
2. [Goal aligned to role]
3. [Goal aligned to role]

### 60-Day Goals
1. [Goal]
2. [Goal]

### 90-Day Goals
1. [Goal]
2. [Goal]

### Key Contacts
| Person | Role | For What |
|--------|------|----------|
| [Manager] | Manager | Day-to-day guidance |
| [Buddy] | Onboarding Buddy | Questions, culture, navigation |
| [IT Contact] | IT | Tool access, equipment |
| [HR Contact] | HR | Benefits, policies |

### Tools Access Needed
| Tool | Access Level | Requested |
|------|-------------|-----------|
| [Tool] | [Level] | [ ] |
```

## 如果有可用的 Connector

如果 **~~HRIS** 已連接：
- 拉取新進員工資料和團隊組織圖
- 依職位自動填入需要的工具存取清單

如果 **~~knowledge base** 已連接：
- 連結到相關的入職文件、團隊 wiki 和 runbook
- 拉取團隊現有的入職檢查清單來客製化

如果 **~~calendar** 已連接：
- 自動建立第一天的行事曆事件和第一週的會議邀請

## 小技巧

1. **依職位客製化**：工程師的入職流程跟設計師的不一樣。
2. **第一天不要塞太滿**：重點放在環境設定和認識人。深度工作從第二週開始。
3. **指派一位 buddy**：有一個不是主管的人可以隨時問，差別非常大。
