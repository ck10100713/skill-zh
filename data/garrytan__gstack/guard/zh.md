---
name: guard
version: 0.1.0
description: "完整安全模式：破壞性指令警告 + 限定目錄的編輯。(gstack)"
triggers:
  - full safety mode
  - guard against mistakes
  - maximum safety
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: 'bash -c "exec bash \"$HOME/.claude/skills/gstack/careful/bin/check-careful.sh\""'
          statusMessage: "Checking for destructive commands..."
    - matcher: "PowerShell"
      hooks:
        - type: command
          command: 'bash -c "exec bash \"$HOME/.claude/skills/gstack/careful/bin/check-careful.sh\""'
          statusMessage: "Checking for destructive commands..."
    - matcher: "Edit"
      hooks:
        - type: command
          command: 'bash -c "exec bash \"$HOME/.claude/skills/gstack/freeze/bin/check-freeze.sh\""'
          statusMessage: "Checking freeze boundary..."
    - matcher: "Write"
      hooks:
        - type: command
          command: 'bash -c "exec bash \"$HOME/.claude/skills/gstack/freeze/bin/check-freeze.sh\""'
          statusMessage: "Checking freeze boundary..."
    - matcher: "NotebookEdit"
      hooks:
        - type: command
          command: 'bash -c "exec bash \"$HOME/.claude/skills/gstack/freeze/bin/check-freeze.sh\""'
          statusMessage: "Checking freeze boundary..."
---
<!-- 由 SKILL.md.tmpl 自動產生，請勿直接編輯 -->
<!-- 重新產生：bun run gen:skill-docs -->

# /guard：完整安全模式

同時啟用破壞性指令警告和限定目錄的編輯限制。
這是把 `/careful` + `/freeze` 合在一個指令裡。

**相依性注意：** 這個 skill 會引用同層 `/careful` 和 `/freeze` skill 目錄裡的 hook 腳本。
兩個都要裝（gstack 的 setup 腳本會一起裝）。

```bash
GSTACK_STATE_ROOT=$(~/.claude/skills/gstack/bin/gstack-paths --get GSTACK_STATE_ROOT); : "${GSTACK_STATE_ROOT:?gstack-paths failed; reinstall with ./setup or /gstack-upgrade}"
mkdir -p "$GSTACK_STATE_ROOT"/analytics
echo '{"skill":"guard","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","repo":"'$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")'"}'  >> "$GSTACK_STATE_ROOT"/analytics/skill-usage.jsonl 2>/dev/null || true
```

## Setup

問使用者要把編輯限制在哪個目錄。用 AskUserQuestion：

- 問題：「Guard 模式：要把編輯限制在哪個目錄？破壞性指令警告一律開著。選定路徑以外的檔案會禁止編輯。」
- 文字輸入（不是選擇題），由使用者自己打路徑。

使用者給了目錄路徑之後：

用共用的 writer 設定使用者選的邊界，它會解析成實體絕對路徑，並且跟調查清理的替換動作序列化處理：
```bash
bash "$HOME/.claude/skills/gstack/freeze/bin/freeze-state.sh" set "<user-provided-path>"
```

helper 失敗的話，不要宣稱邊界已啟用。保留現有狀態並回報復原方式；絕對不准繞過共用 writer 直接寫入或刪除。

告訴使用者：
- 「**Guard 模式已啟用。** 現在有兩道保護在跑：」
- 「1. **破壞性指令護欄**：rm -rf、DROP TABLE、force-push 等在執行前會警告（可以覆寫）；災難級的形式（遞迴刪除 / 或 ~、force-push 到預設 branch）直接拒絕」
- 「2. **編輯邊界**：檔案編輯限制在 `<path>/`。這個目錄以外的編輯會被擋下。」
- 「要移除持久的編輯邊界，執行 `/unfreeze`。結束 session 只會停掉它的 hook，不會刪掉那個邊界。」

## 保護範圍

破壞性指令的完整模式清單和安全例外，請看 `/careful`。
編輯邊界怎麼強制執行，請看 `/freeze`。
