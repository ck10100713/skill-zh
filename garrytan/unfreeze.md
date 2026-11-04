---
layout: "default"
skill: "unfreeze"
author: "Garry Tan"
category: "安全護欄"
summary: "清除 /freeze 設的凍結邊界，讓所有目錄都能再編輯"
source: "https://github.com/garrytan/gstack/blob/main/unfreeze/SKILL.md"
license: "MIT"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
---
name: unfreeze
version: 0.1.0
description: 清除 /freeze 設定的凍結邊界，讓所有目錄都可以再編輯。(gstack)
triggers:
  - unfreeze edits
  - unlock all directories
  - remove edit restrictions
allowed-tools:
  - Bash
  - Read
---
<!-- 由 SKILL.md.tmpl 自動產生，請勿直接編輯 -->
<!-- 重新產生：bun run gen:skill-docs -->

# /unfreeze — 清除凍結邊界

移除 `/freeze` 設定的編輯限制，讓所有目錄都可以編輯。

```bash
GSTACK_STATE_ROOT=$(~/.claude/skills/gstack/bin/gstack-paths --get GSTACK_STATE_ROOT); : "${GSTACK_STATE_ROOT:?gstack-paths failed; reinstall with ./setup or /gstack-upgrade}"
mkdir -p "$GSTACK_STATE_ROOT"/analytics
echo '{"skill":"unfreeze","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","repo":"'$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")'"}'  >> "$GSTACK_STATE_ROOT"/analytics/skill-usage.jsonl 2>/dev/null || true
```

## 清除邊界

```bash
bash "$HOME/.claude/skills/gstack/freeze/bin/freeze-state.sh" clear
```

這是使用者明確要求的移除，不是調查後的清理。共用的 writer 會把它跟取得、替換和有檢查 owner 的釋放動作序列化。遇到 `FREEZE_BUSY` 或非預期的狀態，一律原封不動、回報怎麼復原；絕對不准直接刪除狀態檔，也不准直接刪除可能還在使用中的 mutation lock。

把結果告訴使用者。注意 `/freeze` 的 hook 在這個 session 裡還是註冊著的，
只是因為沒有狀態檔，所以會放行所有操作。要重新凍結，
再跑一次 `/freeze`。
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: unfreeze
version: 0.1.0
description: Clear the freeze boundary set by /freeze, allowing edits to all directories again. (gstack)
triggers:
  - unfreeze edits
  - unlock all directories
  - remove edit restrictions
allowed-tools:
  - Bash
  - Read
---
<!-- AUTO-GENERATED from SKILL.md.tmpl — do not edit directly -->
<!-- Regenerate: bun run gen:skill-docs -->

# /unfreeze — Clear Freeze Boundary

Remove the edit restriction set by `/freeze`, allowing edits to all directories.

```bash
GSTACK_STATE_ROOT=$(~/.claude/skills/gstack/bin/gstack-paths --get GSTACK_STATE_ROOT); : "${GSTACK_STATE_ROOT:?gstack-paths failed; reinstall with ./setup or /gstack-upgrade}"
mkdir -p "$GSTACK_STATE_ROOT"/analytics
echo '{"skill":"unfreeze","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","repo":"'$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")'"}'  >> "$GSTACK_STATE_ROOT"/analytics/skill-usage.jsonl 2>/dev/null || true
```

## Clear the boundary

```bash
bash "$HOME/.claude/skills/gstack/freeze/bin/freeze-state.sh" clear
```

This is explicit user-requested removal, not investigation cleanup. The shared writer serializes it with acquisition, replacement and owner-checked release. On `FREEZE_BUSY` or unexpected state, leave everything untouched and report recovery; never delete state or a possibly active mutation lock directly.

Tell the user the result. Note that `/freeze` hooks are still registered for the
session — they will just allow everything since no state file exists. To re-freeze,
run `/freeze` again.
~~~~~
{% endraw %}

</section>
</div>
