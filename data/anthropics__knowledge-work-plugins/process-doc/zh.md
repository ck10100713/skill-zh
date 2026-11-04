---
name: process-doc
description: 把業務流程文件化，包含流程圖、RACI 和 SOP。在要把只存在某人腦中的流程正式化、建立 RACI 釐清誰負責什麼、為交接或稽核撰寫 SOP，或記錄工作實際進行時的例外與邊界情況時使用。
argument-hint: "<process name or description>"
---

# /process-doc

> 如果看到不熟的佔位符，或需要確認目前連了哪些工具，請見 [CONNECTORS.md](../../CONNECTORS.md)。

把業務流程記錄成完整的標準作業程序（SOP）。

## 用法

```
/process-doc $ARGUMENTS
```

## 運作方式

帶我走過這個流程：描述它、貼上現有的文件，或只告訴我名稱，我會問對的問題。我會產出一份完整的 SOP。

## 輸出

```markdown
## Process Document: [Process Name]
**Owner:** [Person/Team] | **Last Updated:** [Date] | **Review Cadence:** [Quarterly/Annually]

### Purpose
[Why this process exists and what it accomplishes]

### Scope
[What's included and excluded]

### RACI Matrix
| Step | Responsible | Accountable | Consulted | Informed |
|------|------------|-------------|-----------|----------|
| [Step] | [Who does it] | [Who owns it] | [Who to ask] | [Who to tell] |

### Process Flow
[ASCII flowchart or step-by-step description]

### Detailed Steps

#### Step 1: [Name]
- **Who**: [Role]
- **When**: [Trigger or timing]
- **How**: [Detailed instructions]
- **Output**: [What this step produces]

#### Step 2: [Name]
[Same format]

### Exceptions and Edge Cases
| Scenario | What to Do |
|----------|-----------|
| [Exception] | [How to handle it] |

### Metrics
| Metric | Target | How to Measure |
|--------|--------|----------------|
| [Metric] | [Target] | [Method] |

### Related Documents
- [Link to related process or policy]
```

## 如果有可用的 Connector

如果 **~~knowledge base** 已連接：
- 搜尋既有的流程文件，用更新取代重複建立
- 把完成的 SOP 發佈到你的 wiki

如果 **~~project tracker** 已連接：
- 把流程連結到相關的專案和工作流程
- 為流程改善的行動項目建立任務

## 小技巧

1. **從亂的開始**：你不需要一份完美的描述。告訴我現在是怎麼運作的，我來整理結構。
2. **把例外也放進去**：「通常我們做 X，但有時候是 Y」是最值得記錄的部分。
3. **寫出人名**：就算角色會變，知道現在誰做什麼，有助於把流程弄對。
