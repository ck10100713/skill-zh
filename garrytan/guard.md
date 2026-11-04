---
layout: "default"
skill: "guard"
author: "Garry Tan"
category: "安全護欄"
summary: "同時開破壞性指令警告和限定目錄編輯的完整安全模式"
source: "https://github.com/garrytan/gstack/blob/main/guard/SKILL.md"
license: "MIT"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
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
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: guard
version: 0.1.0
description: "Full safety mode: destructive command warnings + directory-scoped edits. (gstack)"
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
<!-- AUTO-GENERATED from SKILL.md.tmpl — do not edit directly -->
<!-- Regenerate: bun run gen:skill-docs -->

# /guard — Full Safety Mode

Activates both destructive command warnings and directory-scoped edit restrictions.
This is the combination of `/careful` + `/freeze` in a single command.

**Dependency note:** This skill references hook scripts from the sibling `/careful`
and `/freeze` skill directories. Both must be installed (they are installed together
by the gstack setup script).

```bash
GSTACK_STATE_ROOT=$(~/.claude/skills/gstack/bin/gstack-paths --get GSTACK_STATE_ROOT); : "${GSTACK_STATE_ROOT:?gstack-paths failed; reinstall with ./setup or /gstack-upgrade}"
mkdir -p "$GSTACK_STATE_ROOT"/analytics
echo '{"skill":"guard","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","repo":"'$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")'"}'  >> "$GSTACK_STATE_ROOT"/analytics/skill-usage.jsonl 2>/dev/null || true
```

## Setup

Ask the user which directory to restrict edits to. Use AskUserQuestion:

- Question: "Guard mode: which directory should edits be restricted to? Destructive command warnings are always on. Files outside the chosen path will be blocked from editing."
- Text input (not multiple choice) — the user types a path.

Once the user provides a directory path:

Set the user-selected boundary with the shared writer, which resolves a physical absolute path and serializes replacement with investigation cleanup:
```bash
bash "$HOME/.claude/skills/gstack/freeze/bin/freeze-state.sh" set "<user-provided-path>"
```

On helper failure, do not claim the boundary is active. Preserve the state and report recovery; never bypass the shared writer with a direct write or deletion.

Tell the user:
- "**Guard mode active.** Two protections are now running:"
- "1. **Destructive command guard** — rm -rf, DROP TABLE, force-push, etc. warn before executing (overridable); catastrophic shapes (recursive delete of / or ~, force-push to the default branch) are hard-denied"
- "2. **Edit boundary** — file edits restricted to `<path>/`. Edits outside this directory are blocked."
- "To remove the persistent edit boundary, run `/unfreeze`. Ending the session stops its hooks but does not delete that boundary."

## What's protected

See `/careful` for the full list of destructive command patterns and safe exceptions.
See `/freeze` for how edit boundary enforcement works.
~~~~~
{% endraw %}

</section>
</div>
