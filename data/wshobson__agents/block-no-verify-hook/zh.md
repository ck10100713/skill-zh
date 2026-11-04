---
name: block-no-verify-hook
description: 設定 PreToolUse hook，防止 AI agent 用 --no-verify 和其他繞過旗標跳過 git 的 pre-commit hook。在設定要強制執行 commit 品質關卡的 Claude Code 專案時使用。
---

# Block No-Verify Hook

PreToolUse hook 設定，會在執行前攔截並擋下繞過旗標的使用，確保 AI agent 無法跳過 pre-commit hook、GPG 簽署，或其他 git 的安全機制。

## 概覽

AI 寫程式的 agent（Claude Code、Codex 等）可以執行帶有 `--no-verify` 這類旗標的 shell 指令，繞過 pre-commit hook。這會讓 pre-commit hook 裡設定的 lint、格式化、測試和安全檢查全部失去意義。block-no-verify hook 加上一道 PreToolUse 防護，在執行之前拒絕任何包含繞過旗標的 tool call。

## 問題

AI agent 在 commit 程式碼時，可能為了避開 hook 失敗而使用繞過旗標：

```bash
# These commands skip pre-commit hooks entirely
git commit --no-verify -m "quick fix"
git push --no-verify
git commit --no-gpg-sign -m "unsigned commit"
git merge --no-verify feature-branch
```

這會導致：
- 沒格式化的程式碼進到 repo
- lint 錯誤繞過檢查
- 安全掃描被跳過
- 未簽署的 commit 繞過簽署政策
- 測試套件被規避

## 解法

在 `.claude/settings.json` 加一個 `PreToolUse` hook，檢查每一個 Bash tool call，並擋下包含繞過旗標的指令。

### 設定

把下面這段加到專案的 `.claude/settings.json`：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if grep -qE '\"command\"[[:space:]]*:[[:space:]]*\"([^\"\\\\]|\\\\.)*(--no-(ver|g)|commit([^\"\\\\]|\\\\.)*([[:space:]]|\\\\[tn])-[a-zA-Z]*n)'; then echo 'BLOCKED: --no-verify and --no-gpg-sign flags are not allowed. Run the commit without bypass flags so that pre-commit hooks execute properly.' >&2; exit 2; fi"
          }
        ]
      }
    ]
  }
}
```

### 運作方式

1. **Matcher**：這個 hook 只針對 `Bash` 的 tool call，所以不會干擾其他工具（Read、Edit、Grep 等）。
2. **檢查**：Claude Code 會把 tool call 以 JSON 的形式從 stdin 送給 hook，而且不會設定 `$TOOL_INPUT` 變數。hook 用 `grep -E` 在那段 JSON 裡搜尋 `command` 的值，所以不需要 `jq` 或 `node`，而且其他欄位裡的文字（例如 `cwd` 或 tool call 的描述）不會觸發它。它會擋下 `--no-verify`、`--no-gpg-sign`，以及 git 接受的任何更短前綴，例如 `--no-veri`。它也會擋下同一個指令裡接在 `commit` 之後、含有 `n` 的短選項組合，例如 `-n` 或 `-nm`，因為 `-n` 是 `--no-verify` 的簡寫。hook 不會去找 `git` 這個字，所以也能抓到 `if git ...`、`sudo git ...` 和 `g=git; $g commit --no-verify`。誤判，例如 commit 訊息裡剛好提到某個旗標，也會擋下呼叫，這是比較安全的失敗方式。
3. **擋下**：如果在 git 指令裡找到繞過旗標，hook 會以 exit code 2 結束並印出錯誤訊息。exit code 2 會通知 Claude Code 完全拒絕這個 tool call。
4. **放行**：如果沒有找到繞過旗標，hook 會以 exit code 0 結束，指令正常執行。
5. **限制**：hook 檢查的是文字，所以它擋得住出於習慣去用繞過旗標的 agent，擋不住刻意想要規避它的 agent，例如把旗標拆成片段再組合，或是執行 `git -c core.hooksPath=/dev/null commit`。

### Exit Code

| Code | 意義 |
|------|---------|
| 0 | 允許 tool call 繼續 |
| 1 | 錯誤（tool call 仍然繼續，並顯示警告） |
| 2 | 完全擋下 tool call |

## 被擋下的旗標

| 旗標 | 用途 | 為什麼擋 |
|------|---------|-------------|
| `--no-verify` | 跳過 pre-commit 和 commit-msg hook | 繞過 lint、格式化、測試、安全檢查 |
| `--no-gpg-sign` | 跳過 GPG 的 commit 簽署 | 繞過 commit 簽署政策 |

## 安裝

### 每個專案各自設定

在專案根目錄建立或更新 `.claude/settings.json`：

```bash
mkdir -p .claude
cat > .claude/settings.json << 'EOF'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if grep -qE '\"command\"[[:space:]]*:[[:space:]]*\"([^\"\\\\]|\\\\.)*(--no-(ver|g)|commit([^\"\\\\]|\\\\.)*([[:space:]]|\\\\[tn])-[a-zA-Z]*n)'; then echo 'BLOCKED: --no-verify and --no-gpg-sign flags are not allowed. Run the commit without bypass flags so that pre-commit hooks execute properly.' >&2; exit 2; fi"
          }
        ]
      }
    ]
  }
}
EOF
```

### 全域設定

要對所有專案強制執行，就加到 `~/.claude/settings.json`：

```bash
mkdir -p ~/.claude
cat > ~/.claude/settings.json << 'EOF'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if grep -qE '\"command\"[[:space:]]*:[[:space:]]*\"([^\"\\\\]|\\\\.)*(--no-(ver|g)|commit([^\"\\\\]|\\\\.)*([[:space:]]|\\\\[tn])-[a-zA-Z]*n)'; then echo 'BLOCKED: --no-verify and --no-gpg-sign flags are not allowed. Run the commit without bypass flags so that pre-commit hooks execute properly.' >&2; exit 2; fi"
          }
        ]
      }
    ]
  }
}
EOF
```

## 驗證

測試 hook 有沒有擋下繞過旗標：

```bash
# This should be blocked by the hook:
git commit --no-verify -m "test"

# This should succeed normally:
git commit -m "test"
```

## 擴充 Hook

### 加入更多要擋的旗標

要擋更多旗標（例如 `--force`），就擴充 grep 的 pattern：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if grep -qE '\"command\"[[:space:]]*:[[:space:]]*\"([^\"\\\\]|\\\\.)*(--no-(ver|g)|commit([^\"\\\\]|\\\\.)*([[:space:]]|\\\\[tn])-[a-zA-Z]*n|git([[:space:]]|\\\\t)([^\"\\\\]|\\\\.)*--force)'; then echo 'BLOCKED: Bypass flags are not allowed.' >&2; exit 2; fi"
          }
        ]
      }
    ]
  }
}
```

### 與其他 Hook 合用

block-no-verify hook 可以跟其他 PreToolUse hook 並用：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if grep -qE '\"command\"[[:space:]]*:[[:space:]]*\"([^\"\\\\]|\\\\.)*(--no-(ver|g)|commit([^\"\\\\]|\\\\.)*([[:space:]]|\\\\[tn])-[a-zA-Z]*n)'; then echo 'BLOCKED: Bypass flags not allowed.' >&2; exit 2; fi"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if grep -qE 'rm[[:space:]]+-rf[[:space:]]+/'; then echo 'BLOCKED: Dangerous rm command.' >&2; exit 2; fi"
          }
        ]
      }
    ]
  }
}
```

## 最佳實務

1. **把設定檔 commit 進去** -- 把 `.claude/settings.json` 加進版本控制，讓所有團隊成員都受益於這個 hook。
2. **寫進新人導覽** -- 在專案的貢獻指南裡提到這個 hook，讓開發者了解為什麼繞過旗標會被擋。
3. **搭配 pre-commit hook** -- block-no-verify hook 確保 pre-commit hook 會執行；要確定你有設定有意義的 pre-commit hook。
4. **設定完要測試** -- 故意在測試 commit 裡觸發它，確認 hook 有效。
