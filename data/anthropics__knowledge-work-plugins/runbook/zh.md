---
name: runbook
description: 為週期性任務或流程建立或更新營運 runbook。當要記錄 on-call 或 ops 需要反覆執行的任務、把口耳相傳的經驗變成一步一步的精確指令、替既有流程補上疑難排解與 rollback 步驟，或撰寫出事時的 escalation 路徑時使用。
argument-hint: "<process or task name>"
---

# /runbook

> 如果看到不認識的 placeholder，或需要確認目前連接了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

替週期性任務或流程建立一份一步一步的營運 runbook。

## 用法

```
/runbook $ARGUMENTS
```

## 輸出

```markdown
## Runbook: [任務名稱]
**Owner:** [團隊/個人] | **Frequency:** [Daily/Weekly/Monthly/As Needed]
**Last Updated:** [日期] | **Last Run:** [日期]

### Purpose
[這份 runbook 要達成什麼，什麼時候用]

### Prerequisites
- [ ] [需要的存取權或權限]
- [ ] [需要的工具或系統]
- [ ] [需要的資料或輸入]

### Procedure

#### Step 1: [名稱]
```
[確切的指令、動作或說明]
```
**Expected result:** [應該發生什麼]
**If it fails:** [該怎麼處理]

#### Step 2: [名稱]
```
[確切的指令、動作或說明]
```
**Expected result:** [應該發生什麼]
**If it fails:** [該怎麼處理]

### Verification
- [ ] [如何確認任務成功完成]
- [ ] [要檢查什麼]

### Troubleshooting
| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| [你看到什麼] | [為什麼] | [該怎麼做] |

### Rollback
[出問題時如何復原]

### Escalation
| Situation | Contact | Method |
|-----------|---------|--------|
| [什麼時候要 escalate] | [找誰] | [怎麼聯絡] |

### History
| Date | Run By | Notes |
|------|--------|-------|
| [日期] | [人員] | [任何問題或觀察] |
```

## 如果有連接 Connector

如果有連接 **~~knowledge base**：
- 搜尋既有的 runbook 來更新，而不是從零開始寫
- 把完成的 runbook 發布到你的 ops wiki

如果有連接 **~~ITSM**：
- 把 runbook 連結到相關的事件類型和變更請求
- 從 on-call 排班表自動帶入 escalation 聯絡人

## 小提醒

1. **要具體到讓人受不了**：「執行 script」不是一個步驟。「在 ops 伺服器上執行 `python sync.py --prod --dry-run`」才是。
2. **寫出失敗模式**：每一步可能出什麼錯，以及怎麼處理。
3. **測試這份 runbook**：找一個不熟這個流程的人照著做，卡住的地方就修掉。
