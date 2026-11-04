---
name: slack-search
description: 有效搜尋 Slack 來找訊息、檔案、頻道和人員的指引
---

# Slack 搜尋

這個 skill 提供有效搜尋 Slack 來找訊息、檔案和資訊的指引。

## 何時使用

只要需要在 Slack 裡找資訊，就套用這個 skill，包括使用者要你找訊息、對話、檔案或人，或你需要先蒐集 Slack 裡的脈絡才能回答問題的時候。

## 搜尋工具總覽

| Tool | Use When |
|------|----------|
| `slack_search_public` | 只搜公開頻道。不需要使用者同意。 |
| `slack_search_public_and_private` | 搜所有頻道，包括私人頻道、私訊和群組私訊。需要使用者同意。 |
| `slack_search_channels` | 依名稱或描述找頻道。 |
| `slack_search_users` | 依姓名、email 或角色找人。 |

## 搜尋策略

### 先廣再窄

1. 從簡單的關鍵字或自然語言問題開始。
2. 結果太多，就加篩選條件（`in:`、`from:`、日期範圍）。
3. 結果太少，就拿掉篩選條件，改試同義詞或相關詞。

### 選對搜尋模式

- **自然語言問題**（例如「What is the deadline for project X?」）：適合模糊、概念性的搜尋，你不知道確切關鍵字的時候。
- **關鍵字搜尋**（例如 `project X deadline`）：適合找特定、精確的內容。

### 多搜幾次

不要只靠一次搜尋。把複雜的問題拆成幾個小搜尋：
- 先搜主題
- 再搜特定人員的發言
- 再搜特定頻道

## 搜尋修飾詞參考

### 位置篩選
- `in:channel-name` — 在特定頻道內搜尋
- `in:<#C123456>` — 用 ID 在頻道內搜尋
- `-in:channel-name` — 排除某個頻道
- `in:<@U123456>` — 搜尋和某位使用者的私訊

### 使用者篩選
- `from:<@U123456>` — 特定使用者（用 ID）發的訊息
- `from:username` — 某位使用者（用 Slack 使用者名稱）發的訊息
- `to:me` — 直接傳給你的訊息

### 內容篩選
- `is:thread` — 只找討論串內的訊息
- `has:pin` — 已釘選的訊息
- `has:link` — 含連結的訊息
- `has:file` — 含檔案附件的訊息
- `has::emoji:` — 有特定表情反應的訊息

### 日期篩選
- `before:YYYY-MM-DD` — 某日期之前的訊息
- `after:YYYY-MM-DD` — 某日期之後的訊息
- `on:YYYY-MM-DD` — 特定日期的訊息
- `during:month` — 特定月份的訊息（例如 `during:january`）

### 文字比對
- `"exact phrase"` — 比對精確片語
- `-word` — 排除含某個字的訊息
- `wild*` — 萬用字元比對（`*` 前面至少要 3 個字元）

## 檔案搜尋

搜尋檔案時，用 `content_types="files"` 參數加上類型篩選：
- `type:images` — 圖片檔
- `type:documents` — 文件檔
- `type:pdfs` — PDF 檔
- `type:spreadsheets` — 試算表檔
- `type:canvases` — Slack Canvases

範例：`content_types="files" type:pdfs budget after:2025-01-01`

## 追蹤搜尋結果

找到相關訊息之後：
- 用 `slack_read_thread` 取得任何討論串訊息的完整脈絡。
- 用 `slack_read_channel` 搭配 `oldest`/`latest` 時間戳，讀取前後的訊息來補脈絡。
- 結果裡出現使用者 ID 時，用 `slack_read_user_profile` 查那個人是誰。

## 常見陷阱

- **布林運算子沒用。** 不支援 `AND`、`OR`、`NOT`。用空格（隱含 AND）和 `-` 來排除。
- **括號沒用。** 不要想用 `()` 把搜尋詞分組。
- **搜尋不是即時的。** 最新的訊息（最近幾秒內）可能不會出現在搜尋結果裡。要看最新訊息就用 `slack_read_channel`。
- **私人頻道的存取。** 需要包含私人頻道時用 `slack_search_public_and_private`，但注意這需要使用者同意。
