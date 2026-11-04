---
name: git-guardrails-claude-code
description: 設定 Claude Code hook，在危險的 git 指令（push、reset --hard、clean、branch -D 等）執行前就擋下來。當使用者想防止破壞性的 git 操作、加上 git 安全 hook，或在 Claude Code 裡封鎖 git push/reset 時使用。
---

# 設定 Git 護欄

設定一個 PreToolUse hook，在 Claude 執行危險的 git 指令之前攔截並擋下。

## 會擋哪些

- `git push`（所有變體，包括 `--force`）
- `git reset --hard`
- `git clean -f` / `git clean -fd`
- `git branch -D`
- `git checkout .` / `git restore .`

被擋下時，Claude 會看到一則訊息，告訴它沒有權限使用這些指令。

## 步驟

### 1. 問範圍

問使用者：要裝在**只有這個專案**（`.claude/settings.json`）還是**所有專案**（`~/.claude/settings.json`）？

### 2. 複製 hook 腳本

內附的腳本在：[scripts/block-dangerous-git.sh](scripts/block-dangerous-git.sh)

依範圍複製到目標位置：

- **專案**：`.claude/hooks/block-dangerous-git.sh`
- **全域**：`~/.claude/hooks/block-dangerous-git.sh`

用 `chmod +x` 讓它可執行。

### 3. 把 hook 加到設定檔

加到對應的設定檔：

**專案**（`.claude/settings.json`）：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```

**全域**（`~/.claude/settings.json`）：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```

如果設定檔已經存在，就把 hook 合併進現有的 `hooks.PreToolUse` 陣列，不要覆蓋其他設定。

### 4. 問要不要客製

問使用者要不要從封鎖清單增減任何 pattern。照他的回答編輯複製過去的腳本。

### 5. 驗證

跑個快速測試：

```bash
echo '{"tool_input":{"command":"git push origin main"}}' | <path-to-script>
```

應該以 exit code 2 結束，並在 stderr 印出 BLOCKED 訊息。
