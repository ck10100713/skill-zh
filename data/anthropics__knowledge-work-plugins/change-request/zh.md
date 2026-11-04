---
name: change-request
description: 建立附有影響分析和回復計畫的變更管理申請。當要提出需要核准的系統或流程變更、為 CAB 審查準備變更紀錄、在 deploy 之前記錄風險和回復步驟，或為上線規劃利害關係人溝通時使用。
argument-hint: "<change description>"
---

# /change-request

> 如果看到不熟的 placeholder，或需要確認目前連了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

建立結構化的變更申請，附上影響分析、風險評估和回復計畫。

## 用法

```
/change-request $ARGUMENTS
```

## 變更管理框架

建立申請時，套用 assess-plan-execute-sustain 框架：

### 1. Assess（評估）
- 要變更的是什麼？
- 誰會受影響？
- 這個變更有多重大？（低 / 中 / 高）
- 預期會有哪些抗拒？

### 2. Plan（規劃）
- 溝通計畫（誰、什麼、何時、怎麼做）
- 訓練計畫（需要哪些技能、怎麼傳達）
- 支援計畫（help desk、推動者、FAQ）
- 附里程碑的時程

### 3. Execute（執行）
- 宣布並解釋「為什麼」
- 訓練與支援
- 監控採用情況
- 處理抗拒

### 4. Sustain（維持）
- 衡量採用率和成效
- 強化新的行為
- 處理遺留的問題
- 記錄經驗教訓

## 溝通原則

- 先解釋**為什麼**，再講**是什麼**
- 及早、頻繁地溝通
- 使用多個管道
- 承認正在失去的東西，而不只是得到的
- 為提問和疑慮提供明確的管道

## 輸出

```markdown
## Change Request: [Title]
**Requester:** [Name] | **Date:** [Date] | **Priority:** [Critical/High/Medium/Low]
**Status:** Draft | Pending Approval | Approved | In Progress | Complete

### Description
[What is changing and why]

### Business Justification
[Why this change is needed — cost savings, compliance, efficiency, risk reduction]

### Impact Analysis
| Area | Impact | Details |
|------|--------|---------|
| Users | [High/Med/Low/None] | [Who is affected and how] |
| Systems | [High/Med/Low/None] | [What systems are affected] |
| Processes | [High/Med/Low/None] | [What workflows change] |
| Cost | [High/Med/Low/None] | [Budget impact] |

### Risk Assessment
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [Risk] | [H/M/L] | [H/M/L] | [How to mitigate] |

### Implementation Plan
| Step | Owner | Timeline | Dependencies |
|------|-------|----------|--------------|
| [Step] | [Person] | [Date] | [What it depends on] |

### Communication Plan
| Audience | Message | Channel | Timing |
|----------|---------|---------|--------|
| [Who] | [What to tell them] | [How] | [When] |

### Rollback Plan
[Step-by-step plan to reverse the change if needed]
- Trigger: [When to roll back]
- Steps: [How to roll back]
- Verification: [How to confirm rollback worked]

### Approvals Required
| Approver | Role | Status |
|----------|------|--------|
| [Name] | [Role] | Pending |
```

## 如果有連接 connector

如果有連接 **~~ITSM**：
- 自動建立變更申請工單
- 拉出 change advisory board 的排程和核准流程

如果有連接 **~~project tracker**：
- 連結相關的實作任務和相依項目
- 對照里程碑追蹤變更進度

如果有連接 **~~chat**：
- 為溝通計畫草擬利害關係人通知
- 把變更更新貼到相關的團隊頻道

## 小提醒

1. **影響要講具體**：「所有人」不是影響評估。「帳務團隊的 200 位使用者」才是。
2. **一定要有回復計畫**：就算你很有把握，也要為失敗做準備。
3. **及早溝通**：意外會製造抗拒。預告會帶來認同。
