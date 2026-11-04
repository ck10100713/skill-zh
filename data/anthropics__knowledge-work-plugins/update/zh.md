---
name: update
description: 依你目前的活動同步任務並更新 memory。要把專案追蹤工具裡的新指派拉進 TASKS.md、整理過期或逾期的任務、補上不認識的人或專案的 memory 缺口，或做全面掃描找出藏在聊天和 email 裡的待辦時使用。
argument-hint: "[--comprehensive]"
---

# Update 指令

> 如果看到不認識的 placeholder，或想確認目前連了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

讓你的任務清單和 memory 保持最新。兩種模式：

- **預設：** 從外部工具同步任務、整理過期項目、檢查 memory 的缺口
- **`--comprehensive`：** 深度掃描聊天、email、行事曆、文件，標出漏掉的待辦並建議新增 memory

## 用法

```bash
/productivity:update
/productivity:update --comprehensive
```

## 預設模式

### 1. 載入目前狀態

讀 `TASKS.md` 和 `memory/` 目錄。如果它們不存在，建議先跑 `/productivity:start`。

### 2. 從外部來源同步任務

檢查有哪些任務來源可用：
- **專案追蹤工具**（例如 Asana、Linear、Jira）（有 MCP 的話）
- **GitHub Issues**（在 repo 裡的話）：`gh issue list --assignee=@me`

如果沒有可用的來源，跳到步驟 3。

**抓取指派給使用者的任務**（open/in-progress），再跟 TASKS.md 比對：

| 外部任務 | TASKS.md 有對應嗎？ | 動作 |
|---------------|-----------------|--------|
| 找到，但不在 TASKS.md | 沒有對應 | 提議新增 |
| 找到，已經在 TASKS.md | 以標題比對（模糊） | 略過 |
| 在 TASKS.md，但外部沒有 | 沒有對應 | 標記為可能已過期 |
| 在外部已完成 | 在 Active 區塊 | 提議標為完成 |

把差異呈現出來，讓使用者決定要新增或完成哪些。

### 3. 整理過期項目

檢視 TASKS.md 裡的 Active 任務，標記：
- 到期日已經過了的任務
- 在 Active 放了 30 天以上的任務
- 沒有脈絡的任務（沒有人、沒有專案）

逐一呈現給使用者整理：標為完成？重新排程？移到 Someday？

### 4. 為 Memory 缺口解碼任務

對每個任務，試著解出所有實體（人、專案、縮寫、工具、連結）：

```
Task: "Send PSR to Todd re: Phoenix blockers"

Decode:
- PSR → ✓ Pipeline Status Report (in glossary)
- Todd → ✓ Todd Martinez (in people/)
- Phoenix → ? Not in memory
```

記下哪些已經完全解碼、哪些還有缺口。

### 5. 補上缺口

把不認識的詞分組呈現：
```
I found terms in your tasks I don't have context for:

1. "Phoenix" (from: "Send PSR to Todd re: Phoenix blockers")
   → What's Phoenix?

2. "Maya" (from: "sync with Maya on API design")
   → Who is Maya?
```

把答案加進對應的 memory 檔案（people/、projects/、glossary.md）。

### 6. 擷取補充資訊

任務裡常常比 memory 有更豐富的脈絡。抽出來並更新：
- 任務裡的**連結** → 加到專案/人物檔案
- **狀態變更**（「launch done」）→ 更新專案狀態，從 CLAUDE.md 降級
- **關係**（「Todd 對 Maya 提案的簽核」）→ 交叉參照人物
- **截止日** → 加到專案檔案

### 7. 回報

```
Update complete:
- Tasks: +3 from project tracker (e.g. Asana), 1 completed, 2 triaged
- Memory: 2 gaps filled, 1 project enriched
- All tasks decoded ✓
```

## 全面模式（`--comprehensive`）

包含預設模式的一切，再加上對最近活動的深度掃描。

### 額外步驟：掃描活動來源

從可用的 MCP 來源蒐集資料：
- **聊天：** 搜尋最近的訊息、讀取活躍的頻道
- **Email：** 搜尋已寄出的訊息
- **文件：** 列出最近動過的文件
- **行事曆：** 列出最近和即將到來的事件

### 額外步驟：標出漏掉的待辦

把活動和 TASKS.md 比對，找出沒有被追蹤的行動項目：

```
## Possible Missing Tasks

From your activity, these look like todos you haven't captured:

1. From chat (Jan 18):
   "I'll send the updated mockups by Friday"
   → Add to TASKS.md?

2. From meeting "Phoenix Standup" (Jan 17):
   You have a recurring meeting but no Phoenix tasks active
   → Anything needed here?

3. From email (Jan 16):
   "I'll review the API spec this week"
   → Add to TASKS.md?
```

讓使用者挑要新增哪些。

### 額外步驟：建議新的 Memory

找出不在 memory 裡的新實體：

```
## New People (not in memory)
| Name | Frequency | Context |
|------|-----------|---------|
| Maya Rodriguez | 12 mentions | design, UI reviews |
| Alex K | 8 mentions | DMs about API |

## New Projects/Topics
| Name | Frequency | Context |
|------|-----------|---------|
| Starlight | 15 mentions | planning docs, product |

## Suggested Cleanup
- **Horizon project** — No mentions in 30 days. Mark completed?
```

依信心程度分組呈現。高信心的項目提議直接新增；低信心的項目先問使用者。

## 備註

- 沒有使用者確認，絕對不要自動新增任務或 memory
- 有外部來源連結的話就保留
- 任務標題用模糊比對，可以容忍用字上的小差異
- 可以放心頻繁執行，只有在有新資訊時才會更新
- `--comprehensive` 一律互動式執行
