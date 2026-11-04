---
name: review-agent-setup
description: 在 Claude Code 裡為 AI agent 的 review 動作設定 human-in-the-loop 把關。在設定一個 agent 可能發 PR review、留言、merge 或編輯 CI 設定的專案，而你想要有密碼學上可稽核的核准軌跡、並由 Cedar 強制把關時使用。
---

# review-agent-governance — Setup

把 AI agent 的 review 動作（PR review、留言、merge、CI 編輯）擋在明確的人工核准之後。每一次嘗試，不管核准還是拒絕，都會產生一份 Ed25519 簽章的收據。

## When to use this plugin

安裝在 Claude Code agent 會做以下事情的專案：

- Review、留言或 merge pull request（`gh pr review`、`gh pr merge`）
- 分流 issue（`gh issue comment`、`gh issue close`）
- 發布 release（`gh release create`）
- 修改 CI 設定（`.github/workflows/`、`.gitlab-ci.yml`）
- 推送到受保護的 branch（`main`、`master`、`release`、`production`）
- 發佈到外部通知管道（Slack webhook、Discord），前提是你要為發佈用的指令加規則（預設 policy 不會把關它們）

如果 agent 只是在改本機檔案和跑測試，這個 plugin 就太過頭了。一般的工具呼叫 policy 強制執行請用 `protect-mcp`，這個就不用裝。

## One-time setup

### 1. Install the plugin

```bash
claude plugin install wshobson/agents/review-agent-governance
```

### 2. Copy the default policy to your project

```bash
cp .claude/plugins/review-agent-governance/policies/review-agent-governance.cedar \
   ./review-governance.cedar
```

你可以編輯這個檔案，讓它符合專案自己的規則。怎麼撰寫 review policy，請看 `../agents/review-policy-author.md`。

### 3. Create a receipts directory and sign key

```bash
mkdir -p ./review-receipts
echo "/review-receipts/" >> .gitignore
echo "/review-governance.key" >> .gitignore
echo "/.review-approved" >> .gitignore
if [ ! -e ./review-governance.key ]; then
  d=$(mktemp -d) && npx protect-mcp@0.7.4 init --dir "$d" && mv "$d/keys/gateway.json" ./review-governance.key
fi
```

protect-mcp 0.7.4 的 `sign` 不會建立 key，所以最後那行指令負責建立，而且絕對不會覆蓋現有的 key。沒有 key 的話，收據就是未簽章的。要輪替 key 時，先把 `./review-governance.key` 和 `./review-receipts/receipts.jsonl` 封存起來，再重跑一次那行指令。要給稽核人員的是 `./review-governance.key` 裡的 `publicKey` 值。不要 commit 這個檔案，因為它同時也存著私鑰。

## Per-session workflow

Cedar policy 會無條件拒絕 review 範圍內的動作。要核准某個特定動作，就在動作之前開一個核准視窗，動作結束後再關掉。

### Flag file (simplest)

```bash
# Before the action you want to approve
touch ./.review-approved

# Let Claude Code run the review / comment / merge

# Immediately after
rm ./.review-approved
```

### Slash command (from within Claude Code)

```
/approve-review "Reviewing PR #123 authored by contributor X"
```

這會建立 `./.review-approved`，並把給定的理由寫成註記放進去，同時把理由記錄在 `./review-receipts/approvals/` 底下一份未簽章的核准 log。之後還是要手動 `rm` 才能關閉視窗。

### Dry-run everything (force full policy evaluation)

如果你想讓每一個工具呼叫都經過 Cedar、不留任何核准的繞過口：

```bash
export REVIEW_APPROVAL_FLAG=./.never-approve
```

任何符合 forbid 規則的工具呼叫都會被拒絕，核准視窗不會有任何作用。適合 CI 或鎖死的稽核執行。

## Verifying the receipts

列出所有收據：

```bash
ls -la ./review-receipts/
```

用公鑰離線驗證每一份收據：

```bash
PUB=$(node -p 'JSON.parse(require("fs").readFileSync("./review-governance.key")).publicKey')
npx @veritasacta/verify@0.9.2 --replay-chain ./review-receipts/receipts.jsonl --key "$PUB"
```

Exit 0 代表每一份收據都驗證通過。Exit 1 代表有收據驗證失敗，原因可能是被竄改、key 錯了，或某一行格式不對。Exit 2 代表讀不到收據檔。

被拒絕的呼叫不會執行，所以沒有收據。想看 policy 擋了什麼，在 Claude Code 裡執行：

```
/list-pending
```

它會列出 PreToolUse hook 在目前 session 裡擋下的工具呼叫，附上工具名稱以及指令或路徑。

## Example: approving a PR review

```bash
# 1. Human reviews the agent's proposed comment
$ /list-pending
  Blocked in this session:
  - Bash "gh pr review 42 --approve --body 'LGTM'"
  - Bash "gh pr comment 42 --body 'Looking good'"

# 2. Human decides the first one is appropriate, approves it
$ /approve-review "Approving LGTM on PR 42 after visual inspection"
  ./.review-approved created

# 3. Agent retries the action; this time it succeeds
$ agent: gh pr review 42 --approve --body "LGTM"
  [receipt appended to ./review-receipts/receipts.jsonl, decision=allow]

# 4. Human closes the window
$ rm ./.review-approved
```

被允許的呼叫有一份簽章收據，任何拿到公鑰的人都可以離線驗證。被拒絕的嘗試沒有收據，而核准 log 也沒有簽章，所以把軌跡拿給稽核人員看的時候，這兩點要記得說清楚。

## Composing with protect-mcp

如果兩個 plugin 都裝了，各個 plugin 的 `hooks/hooks.json` 會註冊自己的 PreToolUse hook，Claude Code 在每次工具呼叫時兩個都會跑：

```json
{ "type": "command", "command": "\"${CLAUDE_PLUGIN_ROOT}\"/hooks/evaluate.sh" }
```

每個 `evaluate.sh` 會從 stdin 的 hook payload 讀取 `tool_name` 和 `tool_input`（Claude Code 不會設定 `TOOL_NAME` 變數），並評估自己的 policy：protect-mcp 用 `./protect.cedar`，這裡用 `./review-governance.cedar`。

兩個 hook 都通過，工具呼叫才能繼續。任何一邊的 policy 判定 Cedar deny，就會被擋下。

## Standards

- **Ed25519** — RFC 8032（數位簽章）
- **JCS** — RFC 8785（確定性的 JSON 正規化）
- **Cedar** — AWS 的開源授權 policy 語言
- **IETF draft** — [draft-farley-acta-signed-receipts](https://datatracker.ietf.org/doc/draft-farley-acta-signed-receipts/)
