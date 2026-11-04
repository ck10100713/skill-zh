---
name: task-management
description: 用共用的 TASKS.md 檔案做簡單的任務管理。當使用者問起自己的任務、想新增／完成任務，或需要協助追蹤承諾事項時參考這份。
user-invocable: false
---

# 任務管理

任務記在一個簡單的 `TASKS.md` 檔案裡，你和使用者都可以編輯。

## 檔案位置

**一律使用目前工作目錄下的 `TASKS.md`。**

- 如果它已經存在，就讀寫它
- 如果不存在，就用下面的範本建立

## Dashboard 設定（第一次執行）

有一個視覺化的 dashboard 可以管理任務和記憶。**第一次碰到任務相關的互動時：**

1. 檢查目前工作目錄下有沒有 `dashboard.html`
2. 如果沒有，就從 `${CLAUDE_PLUGIN_ROOT}/skills/dashboard.html` 複製到目前工作目錄
3. 告訴使用者：「I've added the dashboard. Run `/productivity:start` to set up the full system.」

這個任務看板：
- 讀寫的是同一個 `TASKS.md` 檔案
- 自動儲存變更
- 會監看外部變更（你透過 CLI 編輯時會同步）
- 支援用拖放重新排序任務和區段

## 格式與範本

建立新的 TASKS.md 時，一字不差地使用這個範本（不要放範例任務）：

```markdown
# Tasks

## Active

## Waiting On

## Someday

## Done
```

任務格式：
- `- [ ] **Task title** - context, for whom, due date`
- 額外細節用子項目（sub-bullet）
- 已完成：`- [x] ~~Task~~ (date)`

## 怎麼互動

**當使用者問「what's on my plate」／「my tasks」：**
- 讀 TASKS.md
- 摘要 Active 和 Waiting On 區段
- 標出任何逾期或緊急的項目

**當使用者說「add a task」／「remind me to」：**
- 用 `- [ ] **Task**` 格式加到 Active 區段
- 有提供的話就帶上背景資訊（是幫誰做的、截止日）

**當使用者說「done with X」／「finished X」：**
- 找到那個任務
- 把 `[ ]` 改成 `[x]`
- 加上刪除線：`~~task~~`
- 加上完成日期
- 移到 Done 區段

**當使用者問「what am I waiting on」：**
- 讀 Waiting On 區段
- 註明每個項目已經等了多久

## 慣例

- 任務標題用**粗體**，方便掃讀
- 如果是對某人的承諾，就寫上「for [person]」
- 有截止日就寫上「due [date]」
- 等待中的項目寫上「since [date]」
- 額外背景用子項目
- Done 區段留大約一週，之後清掉舊項目

## 擷取任務

整理會議或對話內容時，主動問要不要把擷取到的任務加進去：
- 使用者做出的承諾（「I'll send that over」）
- 指派給他們的待辦事項
- 提到的後續跟進

加之前要先問，沒有確認就不要自動加。
