---
name: signed-audit-trails-recipe
description: 一步一步的 cookbook，教你在 Claude Code 的工具呼叫上設定有密碼學簽章的稽核軌跡。在正式採用 protect-mcp runtime hook 之前，需要說明、評估或展示這個模式時使用。涵蓋 Cedar policy、Ed25519 收據、離線驗證、竄改偵測、CI/CD 整合，以及跟 SLSA 的組合。
---

# Signed Audit Trails for Claude Code Tool Calls

用 cookbook 的方式，一步步帶你走過替每一次 Claude Code 工具呼叫產生密碼學簽章收據的做法。這是教學用的 skill。要看 runtime 的實作，請安裝 [`protect-mcp`](../../../protect-mcp/) plugin。

## What this gives you

每一次工具呼叫（`Bash`、`Edit`、`Write`、`WebFetch`）都會：

1. 在執行前**對照 Cedar policy 評估**。如果 policy 拒絕這次呼叫，工具就不會執行。
2. 在執行後**簽成一份 Ed25519 收據**。收據是 JCS 正規化的，任何拿到公鑰的人都能離線驗證。

稽核人員、監管機關或交易對手之後都可以驗證每一份收據（Step 5）。不需要網路呼叫，不需要向廠商查詢，也不必信任營運者。

## When to use the pattern

- **受管制的環境**（金融、醫療、關鍵基礎設施），需要 agent 行為的防竄改證據
- **CI/CD pipeline**，想證明每個自動化建置步驟都有通過 policy 關卡
- **多方協作**，交易對手想驗證你 agent 的行為，又不想信任你的營運者
- **合規情境**（EU AI Act 第 12 條、agent 所建構軟體的 SLSA provenance），一般的 logging 不夠用的時候

## Step 1: Install the hook configuration

用 `/plugin install protect-mcp` 安裝 `protect-mcp` plugin。它的 hook 會在每次工具呼叫之前執行 `evaluate.sh`，之後執行 `sign.sh`。兩個腳本都是從 stdin 讀取 hook 事件，因為 Claude Code 不會設定 `TOOL_NAME` 或 `TOOL_INPUT` 變數。hook 設定，以及每個腳本傳給 protect-mcp 的內容，請看 [`references/hook-wiring.md`](references/hook-wiring.md)。

protect-mcp 0.7.4 不會建立簽章用的 key，沒有 key 的話，收據就是未簽章的。要建立一次 `./protect-mcp.key`。這個指令絕對不會覆蓋現有的 key：

```bash
if [ ! -e ./protect-mcp.key ]; then
  d=$(mktemp -d) && npx protect-mcp@0.7.4 init --dir "$d" && mv "$d/keys/gateway.json" ./protect-mcp.key
fi
```

要給稽核人員的是那個檔案裡的 `publicKey` 值。不要 commit 這個檔案，因為它同時也存著私鑰。

把私鑰和收據目錄加進 `.gitignore`：

```bash
echo "/protect-mcp.key" >> .gitignore
echo "/receipts/" >> .gitignore
```

## Step 2: Write a Cedar policy

用 [`references/cedar-policy.md`](references/cedar-policy.md) 裡的範例建立 `./protect.cedar`。它允許唯讀的工具和一小份 Bash 指令清單，拒絕 shell 串接和破壞性指令，並把寫入限制在專案內，含有 `..` 的路徑一律拒絕。

## Step 3: Use Claude Code normally

啟動 Claude Code。每一次工具呼叫都會經過兩個 hook：

```
You: Please read the README and summarize it.

Claude: I will read README.md.
  [PreToolUse: Read ./README.md -> allow]
  [Tool: Read executes]
  [PostToolUse: receipt rcpt-a8f3c9d2 signed to ./receipts/]

... summary of README ...
```

一個有 20 次工具呼叫的 session，會在 `./receipts/receipts.jsonl` 附加 20 份收據。

## Step 4: Inspect a receipt

protect-mcp 0.7.4 會把每份收據以一行的形式附加到 `./receipts/receipts.jsonl`。印出最新的一份：

```bash
tail -n 1 ./receipts/receipts.jsonl | python3 -m json.tool
```

收據是簽章過的 v2 envelope，裡面會標明工具名稱，而且不包含公鑰。範例和被簽章的欄位，請看 [`references/receipt-format.md`](references/receipt-format.md)。

## Step 5: Verify the receipts

把 `./protect-mcp.key` 裡的 `publicKey` 值傳給 verifier：

```bash
PUB=$(node -p 'JSON.parse(require("fs").readFileSync("./protect-mcp.key")).publicKey')
npx @veritasacta/verify@0.9.2 --replay-chain ./receipts/receipts.jsonl --key "$PUB"
```

Exit code：

| Code | Meaning |
|------|---------|
| `0`  | 每一份收據都驗證通過 |
| `1`  | 有收據驗證失敗（被竄改、key 錯誤，或某一行格式不對） |
| `2`  | 讀不到收據檔 |

## Step 6: Demonstrate tamper detection

把最新一份收據的 `decision` 從 `allow` 改成 `deny`：

```bash
python3 -c "
import json
path = './receipts/receipts.jsonl'
lines = open(path).read().splitlines()
r = json.loads(lines[-1])
r['payload']['decision'] = 'deny'
lines[-1] = json.dumps(r)
open(path, 'w').write('\n'.join(lines) + '\n')
"

npx @veritasacta/verify@0.9.2 --replay-chain ./receipts/receipts.jsonl --key "$PUB"
```

verifier 會以 exit code `1` 結束，並指出哪一行失敗。Ed25519 簽章跟被竄改過的 payload 的 JCS 正規化 byte 已經對不上了。

把欄位還原，驗證就會再次通過。

## How the cryptography works

兩個不變條件，讓收據可以在任何符合規範的實作之間離線驗證：

1. 簽章前先做 **JCS 正規化（RFC 8785）**。Key 依 UTF-16 code unit 排序、空白最少化、字串不做正規化。兩個獨立的實作，對同樣的收據內容會產生逐 byte 一致的簽章 payload。
2. 對正規化後的 byte 做 **Ed25519 簽章（RFC 8032）**。確定性、固定大小、不依賴 nonce。

protect-mcp 0.7.4 的收據沒有連結到前一份收據，所以被刪掉的收據不會被發現。

正式的 wire format 請看 [draft-farley-acta-signed-receipts](https://datatracker.ietf.org/doc/draft-farley-acta-signed-receipts/)。

## Cross-implementation interop

這個收據格式目前有四個獨立的實作：

| Implementation | Language | Use case |
|----------------|----------|----------|
| [protect-mcp](https://www.npmjs.com/package/protect-mcp) | TypeScript | Claude Code, Cursor, MCP hosts |
| [protect-mcp-adk](https://pypi.org/project/protect-mcp-adk/) | Python | Google Agent Development Kit |
| [sb-runtime](https://github.com/ScopeBlind/sb-runtime) | Rust | OS-level sandbox (Landlock + seccomp) |
| APS governance hook | Python | CrewAI, LangChain |

任何一個實作產生的收據，都能用 [`@veritasacta/verify`](https://www.npmjs.com/package/@veritasacta/verify) 驗證。稽核人員不需要信任營運者選了什麼工具，格式本身就是合約。

## CI/CD integration

在 CI 裡驗證收據，讓被竄改的收據讓建置失敗。[`references/ci-cd.md`](references/ci-cd.md) 有一份 GitHub Actions workflow，在 push 到預設 branch 時執行。它從限定 branch 的 environment 安裝簽章 key、執行 agent、驗證收據，再把收據上傳。它不會在 pull request 上執行，因為那樣會把 key 交給還沒審查過的程式碼。

## Composition with SLSA provenance for agent-built software

當 Claude Code 建構並發布軟體時（把 `npm install`、`npm build`、`npm publish` 當成工具呼叫來執行），收據鏈就是逐步驟的建置紀錄。SLSA Provenance v1 為此留了一個擴充點：`byproducts` 欄位可以跟建置證明（build attestation）並列，引用收據鏈。

[agent-commit build type](https://refs.arewm.com/agent-commit/v0.2) 用 ResourceDescriptor 的形狀記錄了這個模式：

```json
{
  "name": "decision-receipts",
  "digest": { "sha256": "..." },
  "uri": "oci://registry/org/build-xyz/receipts:sha256-...",
  "annotations": {
    "predicateType": "https://veritasacta.com/attestation/decision-receipt/v0.1",
    "signerRole": "supervisor-hook"
  }
}
```

SLSA provenance 由 builder 身分簽章；收據的證明（attestation）則由 supervisor-hook 身分簽章。兩個信任域，在 byproduct 這一層互相交叉引用。組合方式的討論請看 [slsa-framework/slsa#1594](https://github.com/slsa-framework/slsa/issues/1594)。

## Common pitfalls

**私鑰被放進版本控制。** 產生出來的 `./protect-mcp.key` 絕對不能 commit。上面的範例已經把它加進 `.gitignore`。如果 key 不小心被 commit 了，要立刻輪替。把 key 和 `./receipts/receipts.jsonl` 移到封存位置，再重新執行 Step 1 的指令。封存的收據要用舊的公鑰驗證。

**Hook 的 payload 在 stdin。** Claude Code 不會設定 `$TOOL_NAME` 或 `$TOOL_INPUT` 變數。如果 hook 指令傳了 `--tool "$TOOL_NAME"`，送出去的工具名稱會是空的，所以 policy 會拒絕每一次呼叫。要像 plugin 腳本那樣，從 stdin 讀取 payload。

**CI 裡的收據目錄。** 如果 Claude Code 在 CI 裡執行，要在 job 結束時把收據上傳成 artifact，不然收據會在 job 結束時消失。

**Policy 不存在。** 當 `./protect.cedar` 不存在時，`evaluate.sh` 會往 stderr 印出警告，然後放行這次呼叫。在你於 Step 2 建立 policy 之前，沒有任何呼叫會被把關。

## Related in this marketplace

- [`protect-mcp`](../../../protect-mcp/) — runtime 的 hook 實作
  （正式環境請用這個 plugin）
- [`review-agent-governance`](../../../review-agent-governance/) — 在 review 範圍內的動作之前要求
  人工核准；可以跟 protect-mcp 組合使用

## References

- [`draft-farley-acta-signed-receipts`](https://datatracker.ietf.org/doc/draft-farley-acta-signed-receipts/) — IETF draft，收據的 wire format
- [RFC 8032](https://datatracker.ietf.org/doc/html/rfc8032) — Ed25519
- [RFC 8785](https://datatracker.ietf.org/doc/html/rfc8785) — JCS
- [Cedar policy language](https://docs.cedarpolicy.com/)
- [protect-mcp on npm](https://www.npmjs.com/package/protect-mcp)
- [@veritasacta/verify on npm](https://www.npmjs.com/package/@veritasacta/verify)
- [in-toto/attestation#549](https://github.com/in-toto/attestation/pull/549) — Decision Receipt predicate 提案
- [agent-commit build type](https://refs.arewm.com/agent-commit/v0.2) — agent 產生的 commit 所用的 SLSA provenance
- [Microsoft Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit) (`examples/protect-mcp-governed/`)
- [AWS Cedar for Agents](https://github.com/cedar-policy/cedar-for-agents)
