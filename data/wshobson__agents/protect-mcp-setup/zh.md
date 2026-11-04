---
name: protect-mcp-setup
description: 為 Claude Code 的工具呼叫設定 Cedar 政策強制執行與 Ed25519 簽章收據。在設定需要密碼學稽核軌跡、由政策把關工具執行，或需要符合合規要求的 agent 行為證據的專案時使用。
---

# protect-mcp — Policy Enforcement + Signed Receipts

對每一次 Claude Code 工具呼叫做密碼學治理。每次呼叫都會
依 Cedar 政策評估，並產生一份 Ed25519 簽章的收據，
任何人都可以離線驗證。

## Overview

Claude Code 會執行強大的工具：`Bash`、`Edit`、`Write`、`WebFetch`。預設情況下
沒有稽核軌跡、沒有政策強制執行，事後也沒有辦法證明
當時做了什麼決定。`protect-mcp` 補上這三個缺口：

- **Cedar 政策**（AWS 的開源授權引擎）在每次工具呼叫執行之前
  就做評估。Cedar 的 deny 具有最終決定權。
- **Ed25519 收據**記錄每個執行過的工具名稱，並用
  你的金鑰簽章。
- 透過 `npx @veritasacta/verify` **離線驗證**。不需要伺服器、不需要帳號，
  也不需要信任營運者。

## Problem

AI agent 做出的決定會影響金錢、安全與權利。Claude Code 的
session log 記錄了發生什麼事，但這份 log：

- 可以被修改：任何有存取權的人都能編輯
- 沒有簽章：沒有辦法證明完整性
- 綁定營運者：驗證時必須信任保管 log 的人

在合規情境（金融、醫療、受監管的研究）下，這樣是不夠的。
你需要有篡改跡象可查的證據，讓第三方不必信任你
也能驗證。

## Solution

把 `protect-mcp` 加到你的 Claude Code 專案：

```bash
# 1. Install the plugin (adds hooks + skill to your project)
claude plugin install wshobson/agents/protect-mcp

# 2. Create ./protect.cedar (see below). The plugin installs the hooks.

# 3. Create the signing key once (protect-mcp 0.7.4 sign does not create it).
#    An existing key is never replaced. See references/receipt-format.md to rotate.
if [ ! -e ./protect-mcp.key ]; then
  d=$(mktemp -d) && npx protect-mcp@0.7.4 init --dir "$d" && mv "$d/keys/gateway.json" ./protect-mcp.key
fi
echo "/protect-mcp.key" >> .gitignore

# 4. Use Claude Code normally. Every tool call is now policy-evaluated
#    and produces a signed receipt in ./receipts/
```

## Hook Configuration

安裝 plugin 會加入 `hooks/hooks.json` 裡的兩個 hook。每個 hook 執行
plugin 內附的一支腳本：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          { "type": "command", "command": "\"${CLAUDE_PLUGIN_ROOT}\"/hooks/evaluate.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          { "type": "command", "command": "\"${CLAUDE_PLUGIN_ROOT}\"/hooks/sign.sh" }
        ]
      }
    ]
  }
}
```

Claude Code 會把 hook 事件以 JSON 透過 stdin 傳給指令，不會
設定 `TOOL_NAME` 或 `TOOL_INPUT` 變數。`evaluate.sh` 從那份 payload 讀取 `tool_name` 和
`tool_input`，並以 flag 傳給 `protect-mcp`；`sign.sh` 只讀取
`tool_name`，因為 0.7.4 的簽章器不記錄其他東西。設定
`PROTECT_MCP_POLICY`、`PROTECT_MCP_RECEIPTS` 和 `PROTECT_MCP_KEY` 可以改變
預設路徑。當政策檔不存在時，PreToolUse hook 會在 stderr 印出
警告，並允許這次呼叫。

### What each hook does

**PreToolUse**：在工具執行之前執行。依你的 Cedar
政策檔評估這次工具呼叫。如果 Cedar 回傳 `deny`，hook 會以 exit code 2 結束，
Claude Code 就會完全阻擋這次工具呼叫。

**PostToolUse** 在工具完成之後執行。它會簽出一份寫明
工具名稱的收據，並附加到 `./receipts/receipts.jsonl`。protect-mcp 0.7.4
不會記錄工具的輸入或輸出。

## Cedar Policy File

在專案根目錄建立 `./protect.cedar`：

```cedar
// Read-only tools: one rule can name several tools in `when`. Add WebFetch
// with your own URL rule.
permit (principal, action == Action::"MCP::Tool::call", resource) when {
    resource == Tool::"Read" || resource == Tool::"Glob" || resource == Tool::"Grep"
};

// Safe commands only; git limited to read subcommands
permit (principal, action == Action::"MCP::Tool::call", resource == Tool::"Bash") when {
    context has input && context.input has command &&
    (context.input.command like "git status*" || context.input.command like "git diff*" ||
     context.input.command like "git log*" || context.input.command like "git show*" ||
     context.input.command like "npm*" || context.input.command like "ls*" ||
     context.input.command like "cat*" || context.input.command like "echo*" ||
     context.input.command like "pwd*" || context.input.command like "test*")
};

// No chaining (`&` also denies `2>&1`), `$` expansion, redirection (`>` or
// `<`, which covers `<(`), file output (`git diff --output`), or rm -rf
forbid (principal, action == Action::"MCP::Tool::call", resource == Tool::"Bash") when {
    context has input && context.input has command &&
    (context.input.command like "*;*" || context.input.command like "*&*" ||
     context.input.command like "*|*" || context.input.command like "*$*" ||
     context.input.command like "*`*" || context.input.command like "*>*" ||
     context.input.command like "*<*" || context.input.command like "*\n*" ||
     context.input.command like "*--output*" || context.input.command like "*rm -rf*")
};

// Writes only inside the project (paths are absolute), never via `..`
permit (principal, action == Action::"MCP::Tool::call", resource) when {
    (resource == Tool::"Write" || resource == Tool::"Edit") &&
    context has input && context.input has file_path &&
    context.input.file_path like "/path/to/project/*"
};
forbid (principal, action == Action::"MCP::Tool::call", resource) when {
    (resource == Tool::"Write" || resource == Tool::"Edit") &&
    context has input && context.input has file_path &&
    (context.input.file_path like "*/../*" || context.input.file_path like "*/..")
};
```

字串比對是盡力而為的做法：`like` 檢查的是原始字串，不是
解析過的路徑，而且 `npm*` 的 permit 會執行任意程式碼，所以它的安全程度
只取決於專案的腳本。

## Verification

對照 `./protect-mcp.key` 裡的公鑰驗證每一份收據：

```bash
PUB=$(node -p 'JSON.parse(require("fs").readFileSync("./protect-mcp.key")).publicKey')
npx @veritasacta/verify@0.9.2 --replay-chain ./receipts/receipts.jsonl --key "$PUB"
# Exit 0 = every receipt verified
# Exit 1 = a receipt failed (tampered, wrong key, or malformed line)
# Exit 2 = the file could not be read
```

plugin 的 slash command 在 Claude Code 裡做一樣的事。`/verify-receipt`
接受放在自己檔案裡的單一收據，例如從
`tail -n 1 ./receipts/receipts.jsonl > receipt.json` 取得。

```
/verify-receipt receipt.json
/audit-chain --last 20
```

## Receipt Format

每份收據是 `./receipts/receipts.jsonl` 的一行。範例見
[`references/receipt-format.md`](references/receipt-format.md)。

- 對除了 `signature` 以外的所有欄位做 **Ed25519** 簽章（RFC 8032）
- 簽章前先做 **JCS 正規化**（RFC 8785）
- 收據裡**沒有公鑰**，所以要用 `--key` 傳入
- **沒有連到前一份收據的連結**，所以被刪掉的一行不會被發現

## Why This Matters

| Before | After |
|--------|-------|
| 「相信我，agent 只讀了檔案」 | 可用密碼學證明：每次 Read 都有記錄並簽章 |
| 「log 顯示這件事發生過」 | 收據證明這件事發生過，而且沒有人能編輯它 |
| 「你得稽核我們的系統」 | 任何人都能離線驗證每一份收據 |
| 「log 現在可能已經不一樣了」 | Ed25519 簽章把紀錄鎖死在簽章當下 |

## Standards

- **Ed25519**：RFC 8032（數位簽章）
- **JCS**：RFC 8785（確定性的 JSON 正規化）
- **Cedar**：AWS 的開源授權政策語言
- **IETF draft**：[draft-farley-acta-signed-receipts](https://datatracker.ietf.org/doc/draft-farley-acta-signed-receipts/)

## Related

- **npm**：[protect-mcp](https://www.npmjs.com/package/protect-mcp)
- **Verify CLI**：[@veritasacta/verify](https://www.npmjs.com/package/@veritasacta/verify)
- **Source**：[github.com/ScopeBlind/scopeblind-gateway](https://github.com/ScopeBlind/scopeblind-gateway)
- **Protocol**：[veritasacta.com](https://veritasacta.com)
- **Integrations**：Microsoft Agent Governance Toolkit (PR #667)、AWS cedar-policy/cedar-for-agents (PR #64)
