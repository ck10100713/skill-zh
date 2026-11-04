---
name: hookify-rules
description: 建立與設定 hookify 規則：用帶 YAML frontmatter 的 markdown 檔，透過 regex 或條件比對 bash、檔案、prompt 或 stop 事件，並對 agent 顯示警告或阻擋訊息。建立 hookify 規則、撰寫 hook 規則語法、設定 hookify，或加入樣式護欄（例如阻擋危險指令、編輯 .env、除錯用程式碼）時使用。
---

# Writing Hookify Rules

## Overview

ECC 用內建的 Node runtime 來評估專案本地的 Hookify 規則。啟用 ECC hook 之後，
不需要另外安裝 Hookify plugin 或 Python。

Hookify 規則是帶 YAML frontmatter 的 markdown 檔，定義要監看的樣式，以及樣式比對到時要顯示的訊息。規則存放在 `.claude/hookify.{rule-name}.local.md` 檔案裡。

## Rule File Format

### Basic Structure

```markdown
---
name: rule-identifier
enabled: true
event: bash|file|stop|prompt|all
pattern: regex-pattern-here
---

Message to show Claude when this rule triggers.
Can include markdown formatting, warnings, suggestions, etc.
```

### Frontmatter Fields

| Field | Required | Values | Description |
|-------|----------|--------|-------------|
| name | Yes | kebab-case string | 唯一識別碼（動詞開頭：warn-*、block-*、require-*） |
| enabled | Yes | true/false | 不用刪除就能開關 |
| event | Yes | bash/file/stop/prompt/all | 由哪個 hook 事件觸發 |
| action | No | warn/block | warn（預設）只顯示訊息；block 會阻止該操作 |
| pattern | Yes* | regex string | 要比對的樣式（*複雜規則可改用 conditions） |

### Advanced Format (Multiple Conditions)

```markdown
---
name: warn-env-api-keys
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.env$
  - field: new_text
    operator: contains
    pattern: API_KEY
---

You're adding an API key to a .env file. Ensure this file is in .gitignore!
```

**各事件可用的條件欄位：**
- bash：`command`
- file：`file_path`、`new_text`、`old_text`、`content`
- prompt：`user_prompt`

**運算子：** `regex_match`、`contains`、`equals`、`not_contains`、`starts_with`、`ends_with`

所有條件都要符合，規則才會觸發。

## Event Type Guide

### bash Events
比對 Bash 指令的樣式：
- 危險指令：`rm\s+-rf`、`dd\s+if=`、`mkfs`
- 提權：`sudo\s+`、`su\s+`
- 權限問題：`chmod\s+777`

### file Events
比對 Edit/Write/MultiEdit 操作：
- 除錯用程式碼：`console\.log\(`、`debugger`
- 安全風險：`eval\(`、`innerHTML\s*=`
- 敏感檔案：`\.env$`、`credentials`、`\.pem$`

### stop Events
完成度檢查和提醒。樣式 `.*` 永遠會比對成功。

### prompt Events
比對使用者 prompt 的內容，用來強制執行工作流程。

## Pattern Writing Tips

### Regex Basics
- 特殊字元要跳脫：`.` 寫成 `\.`，`(` 寫成 `\(`
- `\s` 空白字元，`\d` 數字，`\w` 單字字元
- `+` 一個以上，`*` 零個以上，`?` 可有可無
- `|` OR 運算子

### Common Pitfalls
- **太寬**：`log` 會比對到 "login"、"dialog"，要用 `console\.log\(`
- **太窄**：`rm -rf /tmp`，要用 `rm\s+-rf`
- **YAML 跳脫**：用不加引號的樣式；加引號的字串要寫 `\\s`

### Testing
```bash
python3 -c "import re; print(re.search(r'your_pattern', 'test text'))"
```

避免巢狀量詞，例如 `(a+)+`。Runtime 會拒絕有常見災難性回溯形狀的樣式，
因為規則是在 hook 路徑上同步執行的，而且每次 regex 評估都有 25 ms 的硬性 timeout。
無效、是 symlink 或過大的本地規則會 fail open 並輸出
診斷訊息，不會讓其他 Hookify 規則一起失效。

被 git 追蹤的本地規則預設是停用的。要先審查過那些檔案，才設定
`ECC_HOOKIFY_ALLOW_TRACKED=1`；在本地建立、被 gitignore 的一般規則，
不需要這個覆寫就會保持啟用。

## Runtime Behavior

- `warn` 會把訊息當成該事件專屬的額外 context 注入，不會阻擋。
- `block` 會在執行前拒絕符合條件的 Bash、PowerShell、Write、Edit 或 MultiEdit 呼叫。
- 在 prompt、post-tool 和 stop 事件上，`block` 使用 Claude Code 的結構化 block decision。
- Stop 規則會跳過遞迴的 `stop_hook_active` 事件，避免無限繼續的迴圈。

## File Organization

- **位置**：專案根目錄下的 `.claude/` 資料夾
- **命名**：`.claude/hookify.{descriptive-name}.local.md`
- **Gitignore**：把 `.claude/*.local.md` 加進 `.gitignore`

## Commands

- `/hookify [description]` - 建立新規則（沒給參數就自動分析對話）
- `/hookify-list` - 用表格列出所有規則
- `/hookify-configure` - 用互動方式開關規則
- `/hookify-help` - 完整文件

## Quick Reference

最精簡可用的規則：
```markdown
---
name: my-rule
enabled: true
event: bash
pattern: dangerous_command
---
Warning message here
```
