---
name: google-workspace-ops
description: 把 Google Drive、Docs、Sheets 和 Slides 當成同一個工作介面來操作，處理計畫、追蹤表、簡報和共用文件。使用者需要在不直接下原始工具呼叫的情況下，尋找、摘要、編輯、遷移或整理 Google Workspace 的資產時使用。
metadata:
  origin: ECC
---

# Google Workspace Ops

這個 skill 是把共用的文件、試算表和簡報當成運作中的系統來操作，不只是孤立地編輯單一個檔案。

## When to Use

- 使用者需要找到某份文件、試算表或簡報，並直接就地更新
- 整併存放在 Google Drive 裡的計畫、追蹤表、筆記或客戶名單
- 清理或重新整理共用的試算表
- 匯入、修復或重新排版 Google Slides 簡報
- 從 Docs、Sheets 或 Slides 產出摘要，用來做決策

## Preferred Tool Surface

以 Google Drive 當入口，然後切換到合適的專門工具：

- 文字為主的文件用 Google Docs
- 表格工作、公式和圖表用 Google Sheets
- 簡報、匯入、範本遷移和清理用 Google Slides

不要只靠檔名去猜結構。先檢查。

## Workflow

### 1. Find the asset

從 Drive 的搜尋介面開始，找出：

- 確切的檔案
- 同層的相關資產
- 可能重複的檔案
- 最近修改過的版本

如果好幾份文件看起來很像，就用標題、擁有者、修改時間或資料夾來確認。

### 2. Inspect before editing

動手修改之前：

- 摘要目前的結構
- 辨識分頁、標題或投影片張數
- 判斷這項工作是局部清理，還是結構性的大手術

挑最小、又能安全完成工作的工具。

### 3. Edit with precision

- Docs：用感知索引位置的編輯，不要含糊地整段重寫
- Sheets：針對明確的分頁和範圍操作
- Slides：區分內容編輯，以及視覺清理或範本遷移

如果要求的工作跟視覺或版面有關，就要邊檢查邊驗證地反覆調整，不要一次盲目地做一個巨大的更新。

### 4. Keep the working system clean

當這個檔案是更大的工作流程的一部分時，也要一併指出：

- 重複的追蹤表
- 過時的簡報
- 過期的文件 vs 正式版文件
- 這份資產是否該封存、合併或改名

## Output Format

使用：

```text
ASSET
- file name
- type
- why this is the right file

CURRENT STATE
- structure summary
- key problems or blockers

ACTION
- edits made or recommended

FOLLOW-UPS
- archive / merge / duplicate cleanup / next file to update
```

## Good Use Cases

- 「Find the active planning doc and condense it」
- 「Clean up this customer spreadsheet and show me the churn-risk rows」
- 「Import this deck into Slides and make it presentable」
- 「Find the current tracker, not the stale duplicate」
