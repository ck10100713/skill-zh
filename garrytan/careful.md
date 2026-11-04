---
layout: default
skill: careful
author: Garry Tan
category: 安全護欄
summary: 用 PreToolUse hook 攔截 rm -rf、force push 等破壞性指令
source: https://github.com/garrytan/gstack/blob/main/careful/SKILL.md
license: MIT
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

~~~~~markdown
---
name: careful
version: 0.1.0
description: 針對破壞性指令的安全護欄。(gstack)
triggers:
  - be careful
  - warn before destructive
  - safety mode
allowed-tools:
  - Bash
  - Read
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
---
<!-- 由 SKILL.md.tmpl 自動產生，請勿直接編輯 -->
<!-- 重新產生：bun run gen:skill-docs -->

# /careful：破壞性指令護欄

安全模式現在**已啟用**。每一個 Bash 和 PowerShell 指令在執行前都會檢查是否符合破壞性模式。如果偵測到破壞性指令，你會收到警告，可以選擇繼續或取消。

```bash
GSTACK_STATE_ROOT=$(~/.claude/skills/gstack/bin/gstack-paths --get GSTACK_STATE_ROOT); : "${GSTACK_STATE_ROOT:?gstack-paths failed; reinstall with ./setup or /gstack-upgrade}"
mkdir -p "$GSTACK_STATE_ROOT"/analytics
echo '{"skill":"careful","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","repo":"'$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")'"}'  >> "$GSTACK_STATE_ROOT"/analytics/skill-usage.jsonl 2>/dev/null || true
```

## 會保護哪些東西

| 模式 | 範例 | 風險 |
|---------|---------|------|
| `rm -rf` / `rm -r` / `rm --recursive` | `rm -rf /var/data` | 遞迴刪除 |
| `DROP TABLE` / `DROP DATABASE` | `DROP TABLE users;` | 資料遺失 |
| `TRUNCATE` | `TRUNCATE orders;` | 資料遺失 |
| `git push --force` / `-f` | `git push -f origin main` | 改寫歷史 |
| `git reset --hard` | `git reset --hard HEAD~3` | 未 commit 的工作遺失 |
| `git checkout .` / `git restore .` | `git checkout .` | 未 commit 的工作遺失 |
| `kubectl delete` | `kubectl delete pod` | 影響正式環境 |
| `docker rm -f` / `docker system prune` | `docker system prune -a` | container / image 遺失 |

## PowerShell 和 cmd（Windows）

這個 hook 也會檢查 PowerShell 工具（Claude Code 在 Windows 上的主要 shell），以及從 Bash 啟動的任何 `pwsh`/`powershell`/`cmd`。比對不分大小寫，涵蓋出現在指令位置的別名，接受參數前綴（`-r`、`-fo`），並且會去掉 cmd 的 `^` 跳脫字元。上表每一列在這裡也都適用。

| 模式 | 範例 |
|---------|---------|
| `Remove-Item`/`rm`/`ri`/`del`/`erase`/`rd`/`rmdir` 加上 `-Recurse` 或 `-Force` | `gci \| ri -r -fo` |
| cmd 的 `rd /s`、`rmdir /s`、`del /s`、`erase /s` | `cmd /c rd /s /q C:\proj` |
| `Format-Volume`、`Clear-Disk`、`Clear-Content`、`[IO.Directory]::Delete`、`[IO.File]::Delete` | `Clear-Disk -Number 1` |
| `-EncodedCommand`、`iex`、用 `Start-Process` 啟動 shell、`& $cmd`（沒辦法檢查內容） | `irm $url \| iex` |

**PowerShell 部分是盡力而為。** 字串比對看不到執行期才組出來的指令。要真正擋下來，請加上 Claude Code 的 permission deny 規則，它會解析 PowerShell 和它的別名：在 `.claude/settings.json` 裡加 `"deny": ["PowerShell(Remove-Item *)"]`。這個 hook 是透過 `bash` 執行的，所以 Windows 需要 Git Bash。

## 安全例外

以下模式不會跳警告：
- `rm -rf node_modules` / `.next` / `dist` / `__pycache__` / `.cache` / `build` / `.turbo` / `coverage`

## 運作方式

hook 從工具輸入的 JSON 讀出 `tool_name` 和指令，拿去比對上面的模式；如果有命中，就回傳一個帶有 `permissionDecision: "ask"` 和警告原因的 `hookSpecificOutput` payload（decision 一定要包在 `hookSpecificOutput` 底下，Claude Code 會忽略放在最外層的 `permissionDecision`）。MEDIUM 等級的警告你隨時可以選擇無視、繼續執行。

## HIGH 等級（直接拒絕）

有兩種災難性的形狀會被**拒絕**，不是詢問：對剛好是 `/`、`~` 或 `$HOME` 的 `rm -r`/`-R`，以及 force-push 到 repo 的**預設分支**。只限簡單指令（沒有 `;`、`&&`、`||`、`|`、換行），複合指令會掉到 MEDIUM 的詢問；`--force-with-lease` 永遠不算 HIGH。這是盡力而為的建議性硬擋，不是政策邊界：逃生口就是結束這個需要主動開啟、只在本 session 有效的 /careful。

## 專案自訂模式（只能加，不能減）

在 `~/.gstack/careful-patterns.txt`（全域）或 `~/.gstack/projects/<slug>/careful-patterns.txt`（單一專案）裡加警告規則，一行一個 POSIX ERE，可以用 `#` 寫註解。這些規則在內建規則之後才查，所以設定只能**增加**規則，永遠不能壓掉基本警告。不合法的 regex 行會被跳過。

要關閉的話，結束這段對話或開一段新的就好。hook 只在當前 session 有效。
~~~~~

</section>
<section markdown="1">

## 英文原文

~~~~~markdown
---
name: careful
version: 0.1.0
description: Safety guardrails for destructive commands. (gstack)
triggers:
  - be careful
  - warn before destructive
  - safety mode
allowed-tools:
  - Bash
  - Read
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
---
<!-- AUTO-GENERATED from SKILL.md.tmpl — do not edit directly -->
<!-- Regenerate: bun run gen:skill-docs -->

# /careful — Destructive Command Guardrails

Safety mode is now **active**. Every Bash and PowerShell command will be checked
for destructive patterns before running. If a destructive command is detected, you'll be warned
and can choose to proceed or cancel.

```bash
GSTACK_STATE_ROOT=$(~/.claude/skills/gstack/bin/gstack-paths --get GSTACK_STATE_ROOT); : "${GSTACK_STATE_ROOT:?gstack-paths failed; reinstall with ./setup or /gstack-upgrade}"
mkdir -p "$GSTACK_STATE_ROOT"/analytics
echo '{"skill":"careful","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","repo":"'$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")'"}'  >> "$GSTACK_STATE_ROOT"/analytics/skill-usage.jsonl 2>/dev/null || true
```

## What's protected

| Pattern | Example | Risk |
|---------|---------|------|
| `rm -rf` / `rm -r` / `rm --recursive` | `rm -rf /var/data` | Recursive delete |
| `DROP TABLE` / `DROP DATABASE` | `DROP TABLE users;` | Data loss |
| `TRUNCATE` | `TRUNCATE orders;` | Data loss |
| `git push --force` / `-f` | `git push -f origin main` | History rewrite |
| `git reset --hard` | `git reset --hard HEAD~3` | Uncommitted work loss |
| `git checkout .` / `git restore .` | `git checkout .` | Uncommitted work loss |
| `kubectl delete` | `kubectl delete pod` | Production impact |
| `docker rm -f` / `docker system prune` | `docker system prune -a` | Container/image loss |

## PowerShell and cmd (Windows)

The hook also checks the PowerShell tool (Claude Code's main Windows shell)
and any `pwsh`/`powershell`/`cmd` launched from Bash. Matching ignores case,
covers aliases in command position, accepts parameter prefixes (`-r`, `-fo`)
and strips cmd `^` escapes. All rows above apply there too.

| Pattern | Example |
|---------|---------|
| `Remove-Item`/`rm`/`ri`/`del`/`erase`/`rd`/`rmdir` + `-Recurse` or `-Force` | `gci \| ri -r -fo` |
| cmd `rd /s`, `rmdir /s`, `del /s`, `erase /s` | `cmd /c rd /s /q C:\proj` |
| `Format-Volume`, `Clear-Disk`, `Clear-Content`, `[IO.Directory]::Delete`, `[IO.File]::Delete` | `Clear-Disk -Number 1` |
| `-EncodedCommand`, `iex`, `Start-Process` of a shell, `& $cmd` (can't be inspected) | `irm $url \| iex` |

**Best-effort on PowerShell.** String matching can't see a command built at
runtime. For a hard stop, add Claude Code permission deny rules, which parse
PowerShell and its aliases: `"deny": ["PowerShell(Remove-Item *)"]` in
`.claude/settings.json`. The hook runs through `bash`, so Windows needs Git Bash.

## Safe exceptions

These patterns are allowed without warning:
- `rm -rf node_modules` / `.next` / `dist` / `__pycache__` / `.cache` / `build` / `.turbo` / `coverage`

## How it works

The hook reads `tool_name` and the command from the tool input JSON, checks it against the
patterns above, and returns a `hookSpecificOutput` payload with
`permissionDecision: "ask"` and a warning reason if a match is found (the
decision must be nested under `hookSpecificOutput` — Claude Code ignores a
top-level `permissionDecision`). You can always override a MEDIUM warning and
proceed.

## HIGH tier (hard deny)

Two catastrophic shapes are **denied**, not asked: `rm -r`/`-R` of exactly
`/`, `~`, or `$HOME`, and force-push to the repo's **default branch**. SIMPLE
commands only (no `;`, `&&`, `||`, `|`, newline) — compound shapes fall
through to the MEDIUM ask; `--force-with-lease` is never HIGH. A best-effort
advisory hard-stop, not a policy boundary: the escape hatch is ending the
opt-in, session-scoped /careful session.

## Project patterns (additive only)

Add warn rules — one POSIX ERE per line, `#` comments OK — in
`~/.gstack/careful-patterns.txt` (global) or
`~/.gstack/projects/<slug>/careful-patterns.txt` (per-project). Consulted
after the built-in families, so config can only ADD rules, never suppress a
baseline warning. Invalid regex lines are skipped.

To deactivate, end the conversation or start a new one. Hooks are session-scoped.
~~~~~

</section>
</div>
