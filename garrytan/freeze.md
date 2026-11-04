---
layout: "default"
skill: "freeze"
author: "Garry Tan"
category: "安全護欄"
summary: "把這個 session 的檔案編輯鎖在指定目錄，目錄外一律擋掉"
source: "https://github.com/garrytan/gstack/blob/main/freeze/SKILL.md"
license: "MIT"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: freeze
version: 0.1.0
description: 在這個 session 裡，把檔案編輯限制在特定目錄內。(gstack)
triggers:
  - freeze edits to directory
  - lock editing scope
  - restrict file changes
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
hooks:
  PreToolUse:
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

# /freeze：把編輯限制在某個目錄

把檔案編輯鎖在特定目錄。任何 Edit、Write 或 NotebookEdit 操作，只要目標檔案在允許的路徑之外，就會被**擋掉**（不只是警告）。

```bash
GSTACK_STATE_ROOT=$(~/.claude/skills/gstack/bin/gstack-paths --get GSTACK_STATE_ROOT); : "${GSTACK_STATE_ROOT:?gstack-paths failed; reinstall with ./setup or /gstack-upgrade}"
mkdir -p "$GSTACK_STATE_ROOT"/analytics
echo '{"skill":"freeze","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","repo":"'$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")'"}'  >> "$GSTACK_STATE_ROOT"/analytics/skill-usage.jsonl 2>/dev/null || true
```

## 設定

問使用者要把編輯限制在哪個目錄。用 AskUserQuestion：

- 問題："Which directory should I restrict edits to? Files outside this path will be blocked from editing."
- 文字輸入（不是選擇題），使用者自己打路徑。

使用者給了目錄路徑之後：

用共用的 state writer 設定使用者選的邊界。它會解析出實際的絕對路徑，並且把取代動作和 investigation 清理流程序列化：
```bash
bash "$HOME/.claude/skills/gstack/freeze/bin/freeze-state.sh" set "<user-provided-path>"
```

只有 helper 成功時才回報成功。遇到 `FREEZE_BUSY` 或非預期的狀態，就保留現狀，請使用者等目前的寫入者結束後再去檢查復原；絕對不要直接寫入或刪除 state 檔。

告訴使用者："Edits are now restricted to `<path>/`. Any Edit, Write or
NotebookEdit outside this directory will be blocked. To change the boundary, run `/freeze`
again. To remove it, run `/unfreeze`."

## 運作方式

hook 會從 Edit/Write 工具輸入的 JSON 讀 `file_path`，NotebookEdit（Jupyter notebook）呼叫則讀 `notebook_path`（跟 /careful 共用同一個真正的 JSON 擷取器，只有一份程式碼，兩個 hook 都 source 它），然後檢查路徑是不是以 freeze 目錄開頭。如果不是，就回傳帶有 `permissionDecision: "deny"` 的 `hookSpecificOutput` payload 來擋掉這個操作（要巢狀放在 `hookSpecificOutput` 底下，Claude Code 會忽略最上層的 `permissionDecision`）。

極性是 fail-closed：hook 解析不了的工具 payload 會被拒絕，不是放行，因為會 fail open 的邊界就不叫邊界。payload 解析得出來但兩個路徑欄位都沒有（非檔案類工具），就放行。拒絕訊息會寫出工具、路徑欄位、邊界和 `/unfreeze`。檢查之前會先解析路徑：`~`、`..`、相對路徑，以及每一層的 symlink，連還不存在的資料夾也一樣處理。hook 無法定位的路徑（symlink 迴圈、換行字元、Windows 的 drive-relative 路徑、超過 4096 字元）一律拒絕。

freeze 邊界會一直存在，直到透過 state 檔明確移除。hook 腳本每次 Edit/Write/NotebookEdit 呼叫都會讀它。邊界含空白也支援。

## 備註

- freeze 目錄尾端的 `/` 可以避免 `/src` 誤配到 `/src-old`
- freeze 只管 Edit、Write 和 NotebookEdit，Read、Bash、PowerShell、Glob、Grep 不受影響
- 這是防止手滑編輯，不是安全邊界，Bash 或 PowerShell 指令（像 `sed` 或 `Set-Content`）還是能改到邊界外的檔案
- 要解除就跑 `/unfreeze`；結束或殺掉對話不會移除已持久化的狀態
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: freeze
version: 0.1.0
description: Restrict file edits to a specific directory for the session. (gstack)
triggers:
  - freeze edits to directory
  - lock editing scope
  - restrict file changes
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
hooks:
  PreToolUse:
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

# /freeze — Restrict Edits to a Directory

Lock file edits to a specific directory. Any Edit, Write or NotebookEdit
operation targeting a file outside the allowed path will be **blocked** (not
just warned).

```bash
GSTACK_STATE_ROOT=$(~/.claude/skills/gstack/bin/gstack-paths --get GSTACK_STATE_ROOT); : "${GSTACK_STATE_ROOT:?gstack-paths failed; reinstall with ./setup or /gstack-upgrade}"
mkdir -p "$GSTACK_STATE_ROOT"/analytics
echo '{"skill":"freeze","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","repo":"'$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")'"}'  >> "$GSTACK_STATE_ROOT"/analytics/skill-usage.jsonl 2>/dev/null || true
```

## Setup

Ask the user which directory to restrict edits to. Use AskUserQuestion:

- Question: "Which directory should I restrict edits to? Files outside this path will be blocked from editing."
- Text input (not multiple choice) — the user types a path.

Once the user provides a directory path:

Set the user-selected boundary with the shared state writer. It resolves the physical absolute path and serializes replacement with investigation cleanup:
```bash
bash "$HOME/.claude/skills/gstack/freeze/bin/freeze-state.sh" set "<user-provided-path>"
```

Only report success if the helper succeeds. On `FREEZE_BUSY` or unexpected state, preserve it and ask the user to inspect recovery after any active writer finishes; never write or delete the state file directly.

Tell the user: "Edits are now restricted to `<path>/`. Any Edit, Write or
NotebookEdit outside this directory will be blocked. To change the boundary, run `/freeze`
again. To remove it, run `/unfreeze`."

## How it works

The hook reads `file_path` from the Edit/Write tool input JSON, or
`notebook_path` from a NotebookEdit (Jupyter notebook) call (shared
real-JSON extractor with /careful — one copy, sourced by both hooks), then
checks whether the path starts with the freeze directory. If not, it returns a
`hookSpecificOutput` payload with `permissionDecision: "deny"` to block the
operation (nested under `hookSpecificOutput` — Claude Code ignores a top-level
`permissionDecision`).

Polarity is fail-closed: a tool payload the hook cannot parse is DENIED, not
allowed — a boundary that fails open is not a boundary. A payload that parses
but has neither path field (a non-file tool) is allowed. A deny names the
tool, the path field, the boundary and `/unfreeze`. The path is resolved before
the check: `~`, `..` and relative paths, and symlinks at every depth, even
through folders that do not exist yet. A path the hook cannot place (a symlink
loop, a line break, a Windows drive-relative path, over 4096 characters) is
denied.

The freeze boundary persists until explicitly removed via the state file. The hook
script reads it on every Edit/Write/NotebookEdit invocation. Boundaries containing spaces
are supported.

## Notes

- The trailing `/` on the freeze directory prevents `/src` from matching `/src-old`
- Freeze applies to Edit, Write and NotebookEdit only — Read, Bash, PowerShell, Glob, Grep are unaffected
- This prevents accidental edits, not a security boundary — Bash or PowerShell commands like `sed` or `Set-Content` can still modify files outside the boundary
- To deactivate, run `/unfreeze`; ending or killing a conversation does not remove persisted state
~~~~~
{% endraw %}

</section>
</div>
