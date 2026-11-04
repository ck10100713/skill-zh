---
name: agent-payment-x402
description: 幫 AI agent 加上 x402 付款執行能力，附帶每個任務的預算、花費控管和非託管錢包。透過 agentwallet-sdk 支援 Base，透過 OKX Payments / OKX Agent Payments Protocol 支援 X Layer，並透過上游 x402 套件以 facilitator 結算支援 Solana 與多網路 EVM。當 agent 必須自己付錢買東西，需要每個任務的預算、花費控管和非託管錢包時使用。
metadata:
  origin: community
---

# Agent 付款執行（x402）

讓 AI agent 能做受政策把關的付款，並內建花費控管。使用 x402 HTTP 付款協定和 MCP 工具，讓 agent 能付錢給外部服務、API 或其他 agent，而且沒有託管風險。

## 何時使用

適用情境：你的 agent 需要付 API 呼叫費用、購買服務、跟其他 agent 結算、強制執行每個任務的花費上限，或管理非託管錢包。很適合搭配 cost-aware-llm-pipeline 和 security-review 這兩個 skill。

## 決策樹

依你的 agent 是在買付費 API 的存取權，還是在向別人收費，選擇整合路徑：

| 需求 | 建議路徑 |
|------|------------------|
| Agent 在 Base 或其他 agentwallet 支援的鏈上，付費給有 402 把關的 API | 把 `agentwallet-sdk` 當 MCP 付款 server 用，並搭配嚴格的花費政策 |
| Agent 在 X Layer 上付費給有 402 把關的 API | 使用 `okx/onchainos-skills` 裡的 OKX Agent Payments Protocol；`okx-x402-payment` 是已棄用的舊別名 |
| Agent 在 Solana 或其他 x402 v2 網路上付費給有 402 把關的 API | 用上游的 `@x402/fetch` 或 `@x402/axios` 套件包住 agent 的 HTTP client，並註冊 EVM/SVM scheme；由資源 server 的 facilitator 驗證並結算 |
| API 向 agent 收費，網路是 Solana 或多個網路（TypeScript、Python 或 Go） | 使用 `x402-foundation/x402` 的上游 x402 middleware：TypeScript 用 `@x402/express`、`@x402/hono`、`@x402/next` 或 `@x402/fastify`，Python 用 `x402`，Go 用 `github.com/x402-foundation/x402/go/v2` |
| TypeScript API 向 agent 收費 | 使用 OKX Payments 的 TypeScript 賣方 SDK 文件，支援 Express、Hono、Fastify 或 Next.js |
| Go API 向 agent 收費 | 使用 OKX Payments 的 Go 賣方 SDK 文件，支援 Gin、Echo 或 `net/http` |
| Rust API 向 agent 收費 | 使用 OKX Payments 的 Rust 賣方 SDK 文件，支援 Axum |
| Java API 向 agent 收費 | 使用 OKX Payments 的 Java 賣方 SDK 文件，支援 Spring Boot 2/3、Java EE 或 Jakarta |
| Python API 向 agent 收費 | 實作前先查看目前的 OKX Payments repo；可能還沒有 Python 賣方指南 |

## 支援的網路

- `agentwallet-sdk`：上正式環境前，先看套件文件確認目前的網路涵蓋範圍。Base Sepolia 是最安全的開發預設值；Base mainnet 是原版 skill 指定的正式環境路徑。
- OKX Payments / X Layer：目前的賣方文件以 X Layer（`eip155:196`）和 USDT0 結算為目標。產生正式環境的程式碼前，先抓最新的 SDK 文件，因為付款套件和 facilitator 的行為變動很快。
- 上游 x402 套件：設計上就支援多網路，同一條 route 可以同時宣告 Base 和 Solana，讓買方自己挑。套件預設使用 `x402.org` facilitator，它只支援測試網（Base Sepolia `eip155:84532`、Solana devnet `solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1`，加上 Stellar、Aptos、Hedera 和 XRPL 的測試網），不適合用在 mainnet 的 route。要上 mainnet（Solana 是 `solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp`），可以自己 facilitate、自己跑一個 facilitator，或從上游的 facilitator 清單挑一個代管的，比較請看選項 C 底下的 facilitator 比較。上正式環境前，請到 facilitator 的 `/supported` endpoint 確認即時涵蓋範圍，不要在這裡寫死。

## 運作方式

### x402 協定
x402 把 HTTP 402（Payment Required）擴充成機器可協商的流程。Server 回傳 `402` 時，agent 的付款工具會協商價格、檢查預算、簽署交易，而且只會在 orchestrator 設定的政策與確認邊界內重試。

### 花費控管
每次付款工具呼叫都會強制套用一個 `SpendingPolicy`：
- **每個任務的預算**：單次 agent 動作的最大花費
- **每個 session 的預算**：整個 session 的累計上限
- **收款對象白名單**：限制 agent 能付給哪些地址或服務
- **頻率限制**：每分鐘或每小時的最大交易數

### 非託管錢包
Agent 透過 ERC-4337 smart account 自己持有金鑰。Orchestrator 在委派前先設好政策，agent 只能在界線內花錢。沒有集中資金池，沒有託管風險。

## MCP 整合

付款層提供標準的 MCP 工具，能接進任何 Claude Code 或 agent harness 的設定。

> **安全提醒**：一定要固定套件版本。這個工具會管理私鑰，沒固定版本的 `npx` 安裝會帶來供應鏈風險。

### 選項 A：agentwallet-sdk（Base / 多鏈）

```json
{
  "mcpServers": {
    "agentpay": {
      "command": "npx",
      "args": ["agentwallet-sdk@6.0.0"]
    }
  }
}
```

### 可用工具（agent 可呼叫）

| 工具 | 用途 |
|------|---------|
| `get_balance` | 查詢 agent 錢包餘額 |
| `send_payment` | 付款到地址或 ENS |
| `check_spending` | 查詢剩餘預算 |
| `list_transactions` | 所有付款的稽核軌跡 |

> **注意**：花費政策是由 **orchestrator** 在委派給 agent 前設定的，不是 agent 自己設。這樣可以防止 agent 自己調高花費上限。請在你的 orchestration 層或 pre-task hook 裡透過 `set_policy` 設定政策，絕對不要把它做成 agent 可呼叫的工具。

### 選項 B：OKX Agent Payments Protocol（X Layer）

X Layer 的 x402、Multi-Party Payment（MPP）、session 付款、charge 和 A2A charge 流程都走這條路。

買方 agent 流程：

1. 安裝或參考目前的 `okx/onchainos-skills` repo。
2. 以 `skills/okx-agent-payments-protocol/SKILL.md` 作為調度入口。
3. 把 `skills/okx-x402-payment/SKILL.md` 當成已棄用的相容別名，不是正式的 skill。
4. 在檢查錢包狀態或執行付款動作前，一定要有使用者明確確認。不要把付款執行藏在一般的工具呼叫後面。

賣方 API 流程：產生程式碼前，先抓最新的各語言指南：

| Runtime | 目前的指南 |
|---------|---------------|
| TypeScript | `https://raw.githubusercontent.com/okx/payments/main/typescript/SELLER.md` |
| Go | `https://raw.githubusercontent.com/okx/payments/main/go/x402/SELLER.md` |
| Rust | `https://raw.githubusercontent.com/okx/payments/main/rust/x402/SELLER.md` |
| Java | `https://raw.githubusercontent.com/okx/payments/main/java/SELLER.md` |

沒對照目前的 OKX repo 前，不要複製舊文件的範例。OKX 現行的指引以 `okx-agent-payments-protocol` 作為調度入口，而且 Java 賣方文件現在已經有了。

### 選項 C：上游 x402 套件（Solana + Base/EVM）

當 agent 要付款，或你的 API 要收費，網路是 Solana、Base 或上游協定實作支援的其他網路時，走這條路。標準的 x402 monorepo [`x402-foundation/x402`](https://github.com/x402-foundation/x402) 持續有人維護，並直接發布 client 和 middleware 套件。跟選項 A、B 不一樣，這不是獨立的 MCP server：你要包住 agent 自己的 HTTP client，由資源 server 選的 facilitator 負責驗證並結算。

買方 agent 流程：

1. 從維護中的範例 [`examples/typescript/clients`](https://github.com/x402-foundation/x402/tree/main/examples/typescript/clients)（fetch、axios、MCP）開始，不要複製舊文件的片段。
2. 在簽署或送出第一個付費請求前，一定要有使用者明確確認，跟選項 B 對 OKX 流程的要求一樣。不要把付款執行藏在一般的工具呼叫後面。
3. 固定套件版本（例如 `@x402/fetch@2.22.0`）；所有上游套件的版本是同步的。
4. 用註冊在 client 上的 `PaymentPolicy` 來強制執行預算，這樣每次呼叫都會針對 server 實際給出的 challenge 檢查。拿你自己傳進去的數字來比對預算，什麼都證明不了：金額、資產和網路都來自 server，所以簽名產生之前這三者都要驗證。

5. 另外設定一份精確的資源 origin 白名單，跟收款對象和預算政策分開。下面所有啟用付款的 fetch 都拒絕 redirect。Session 核准會列出核准的 origin、網路、資產、收款對象，以及用人類單位表示的花費上限；並行的呼叫共用同一個決定。這個 client 和它的政策要保持私有，只給 orchestrator 用。

```typescript
import { x402Client, wrapFetchWithPayment } from "@x402/fetch";
import { ExactEvmScheme } from "@x402/evm/exact/client";
import { ExactSvmScheme } from "@x402/svm/exact/client";
import { privateKeyToAccount } from "viem/accounts";
import { createKeyPairSignerFromBytes } from "@solana/kit";
import { base58 } from "@scure/base";

// 簽署用的金鑰屬於 ORCHESTRATOR 的環境變數：絕對不寫死，也絕對不讓 agent 能寫入。
const evmKey = process.env.EVM_PRIVATE_KEY as `0x${string}`;
const svmKey = process.env.SVM_PRIVATE_KEY;
if (!evmKey || !svmKey) {
  throw new Error("Signer keys are not set — refusing to start payment client");
}

// 一個 client 涵蓋兩種網路家族：402 提供哪條鏈，買方就付哪條鏈。
const client = new x402Client();
client.register("eip155:*", new ExactEvmScheme(privateKeyToAccount(evmKey)));
client.register("solana:*", new ExactSvmScheme(await createKeyPairSignerFromBytes(base58.decode(svmKey))));

// PaymentPolicy 會在任何簽名產生之前，先過濾 SERVER 的付款需求。
// 回傳空陣列代表「這裡沒有任何可接受的選項」，
// client 會拒絕付款，不會退而求其次。
const ALLOWED_NETWORKS = new Set([
  "solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp",      // Solana mainnet
  "eip155:8453",                                   // Base
]);
const MAX_AMOUNT = 10_000n;      // 最小單位，6 位小數的 USDC：每次呼叫 0.01 USDC
const SESSION_CAP = 50_000n;     // 整個 session 0.05 USDC

// EVM 地址不分大小寫，所以比對時轉成小寫。Solana
// 地址是 base58，而且「分」大小寫，絕對不要轉小寫，否則
// 別的帳號可能會混過去。
const normalizeAddress = (a: string) => (a.startsWith("0x") ? a.toLowerCase() : a);
const ALLOWED_ASSETS = new Set(
  [
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  // USDC, Solana mainnet
    "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",    // USDC, Base
  ].map(normalizeAddress),
);
// 你願意付錢給誰。沒有這個的話，agent 碰到的任何 402
// 都能自己指定收款對象。
const ALLOWED_PAY_TO = new Set(
  ["7pr7NCaQRz5PEhPy7BAeB3Z72TVkiShhjRyVCN5DA6yC"].map(normalizeAddress),
);

client.registerPolicy((_x402Version, requirements) =>
  requirements.filter(r => {
    if (!ALLOWED_NETWORKS.has(r.network)) return false;                   // 鏈不對
    if (!ALLOWED_ASSETS.has(normalizeAddress(r.asset))) return false;     // 代幣不對
    if (!ALLOWED_PAY_TO.has(normalizeAddress(r.payTo))) return false;     // 收款對象不對
    try {
      const amount = BigInt(r.amount);
      return amount >= 0n && amount <= MAX_AMOUNT;                        // 超過預算 / 負數
    } catch {
      return false;                                                       // 金額無法解析
    }
  }),
);

// 政策一次只看到一個 challenge，所以它沒辦法強制執行 session
// 總額，也不能問人任何事。讓啟用付款的 client 保持私有，
// 所有付費呼叫都要經過下面的 payOnce 邊界。

// 這個要由你的 harness 提供：要是真的會問人的 prompt，絕對不能是永遠回傳 true 的空殼。
declare function confirmWithUser(prompt: string): Promise<boolean>;

// 資源授權跟收款對象與預算政策是獨立的。
// 委派之前，由 ORCHESTRATOR 提供精確核准的 HTTPS origin；
// 絕對不要用 server 的 challenge 或 agent 控制的輸入來填這個 set。
const ALLOWED_ORIGINS = new Set(["https://api.example.com"]);
function requireAllowedOrigin(url: string): void {
  const parsed = new URL(url);
  if (!ALLOWED_ORIGINS.has(parsed.origin) || parsed.username || parsed.password) {
    throw new Error("Resource origin is not authorized");
  }
}

// 上面核准的兩個資產都是 6 位小數的 USDC。如果你要支援其他資產或小數位數，
// 要跟資產白名單一起更新這個受信任的格式化政策。
const USDC_SCALE = 1_000_000n;
const humanUSDC = (amount: bigint) =>
  `${amount / USDC_SCALE}.${(amount % USDC_SCALE).toString().padStart(6, "0").replace(/0+$/, "") || "0"} USDC`;

let sessionSpent = 0n;
let sessionApproval: Promise<boolean> | undefined;

async function payOnce(url: string, init?: RequestInit): Promise<Response> {
  requireAllowedOrigin(url); // 在預留額度、prompt、fetch 或簽名之前先檢查。
  // 預留政策允許的最壞情況。結算回應不會
  // 帶金額，所以每次呼叫都算 MAX_AMOUNT 是刻意高估，
  // 只會提早擋，不會太晚擋。要在任何 await 之前預留，
  // 這樣並行的呼叫才不會全部通過檢查。
  if (sessionSpent + MAX_AMOUNT > SESSION_CAP) {
    throw new Error("Session budget exhausted — blocked");
  }
  sessionSpent += MAX_AMOUNT;
  // 只有在沒有任何已簽名的付款離開這個 process 時才釋放預留：
  // 被拒絕或失敗的 prompt、被政策拒絕的 challenge，或免費
  // 回應。已簽名的請求一旦送出就可能結算，所以要繼續算著。
  let signedRequestSent = false;
  const trackingFetch: typeof fetch = async (input, reqInit) => {
    // 在 challenge 和已簽名的重試兩邊都覆蓋呼叫者的選項。原生
    // fetch 會拒絕 redirect，所以未授權的 host 無法透過自動 redirect
    // 回傳 402 或收到付款 header。
    const req = new Request(input, { ...reqInit, redirect: "error" });
    requireAllowedOrigin(req.url);
    if (req.headers.has("PAYMENT-SIGNATURE") || req.headers.has("X-PAYMENT")) {
      signedRequestSent = true;
    }
    const response = await fetch(req);
    // 對於回傳 redirect 回應而不是直接拒絕的 adapter，同樣 fail closed。
    if (response.redirected || (response.status >= 300 && response.status < 400)) {
      throw new Error("Paid request redirects are blocked");
    }
    return response;
  };
  try {
    // 在 await prompt 之前先裝好一個 promise。並行的呼叫共用
    // 同一個決定，包含拒絕或失敗；絕對不自動重問。
    sessionApproval ??= Promise.resolve().then(() => confirmWithUser(
      `Allow paid requests to origins: ${[...ALLOWED_ORIGINS].join(", ")}? ` +
      `Networks: ${[...ALLOWED_NETWORKS].join(", ")}. ` +
      `Assets: ${[...ALLOWED_ASSETS].join(", ")} (6-decimal USDC). ` +
      `Recipients (payTo): ${[...ALLOWED_PAY_TO].join(", ")}. ` +
      `Per-call cap: ${humanUSDC(MAX_AMOUNT)}; session cap: ${humanUSDC(SESSION_CAP)}.`,
    ));
    if (!await sessionApproval) {
      throw new Error("User declined: no payment attempted");
    }
    return await wrapFetchWithPayment(trackingFetch, client)(url, init);
  } finally {
    if (!signedRequestSent) sessionSpent -= MAX_AMOUNT;
  }
}

const res = await payOnce("https://api.example.com/data", { method: "GET" });
```

註冊政策之後，超過預算的金額、非預期的代幣、或沒註冊的鏈都會 fail closed：`createPaymentPayload` 會直接丟錯而不是簽名，因為所有候選項都被過濾掉了。Devnet USDC 是 `4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU`；只有開發時才把它加進 `ALLOWED_ASSETS`。要用對抗式的方式測試這個政策：餵它一個要求 `5000000` 最小單位的 challenge、一個報價用了不同 mint 的 challenge，和一個在你從沒註冊過的鏈上的 challenge，並斷言這三個都不會產生簽名。在 exact-SVM scheme 裡，facilitator 是交易的手續費支付者，所以買方錢包只要放 USDC 就好，不需要 SOL 當 gas。

**Facilitator 的選擇。** Facilitator 代表資源 server 驗證並結算，所以這是資源 server 的決定，不是買方的。依委託出去的信任程度，大致從低到高排列：

| 選項 | 適用時機 |
|--------|--------------|
| [在 process 內自己 facilitate](https://github.com/x402-foundation/x402/tree/main/examples/typescript/servers/self-facilitation) | 你不想讓任何第三方參與結算流程，而且自己能管好金鑰和 RPC 存取 |
| 自己跑一個 facilitator | 你想要同樣的控制權，但要在多個服務之間共用 |
| [`x402.org` facilitator](https://x402.org/facilitator) | 開發與測試網：它是套件預設值，不用設定，而且上游文件寫明它不適合用在 mainnet 的 route |
| 代管的正式環境 facilitator | 你想要 mainnet 涵蓋範圍，但不想自己維運基礎設施 |

要選代管的選項，請從上游文件的 [facilitator 清單](https://docs.x402.org/dev-tools/facilitators)挑，不要照這裡抄來的名字選：那份清單有人維護，但並不完整，涵蓋範圍也會變。截至撰寫時，清單包含 Coinbase 的 CDP（每筆交易都做 KYT/OFAC 篩查）、PayAI、Corbits、Dexter、Solvador 等；其中有幾個除了 EVM 也涵蓋 Solana mainnet。不管挑哪個，上正式環境前都要到它的 `/supported` endpoint 確認即時涵蓋範圍，新增網路時也要重新檢查。

> **揭露**：這個段落是由在 PayAI 工作的人貢獻的，PayAI 是清單上的 facilitator 之一。它只是數個選項之一，自行代管和上游預設的路徑特意列在前面。

**賣方（API 向 agent 收費）。** 使用上游 middleware；同一條 route 可以同時宣告 Base 和 Solana（可執行的版本請看 [`examples/typescript/servers`](https://github.com/x402-foundation/x402/tree/main/examples/typescript/servers)）：

| Runtime | 套件 |
|---------|---------|
| Express / Hono / Next.js / Fastify | `@x402/express@2.22.0`、`@x402/hono@2.22.0`、`@x402/next@2.22.0`、`@x402/fastify@2.22.0` |
| Python（FastAPI、Flask） | PyPI 上的 `x402` |
| Go（Gin、Echo、`net/http`） | `github.com/x402-foundation/x402/go/v2` |

**Solana 賣方：`payTo` 地址要先有它的標準 token account。** Exact-SVM client 會用 `findAssociatedTokenPda` 推導出 `payTo` 的 *associated token account*（ATA）並轉帳過去，它從不負責建立這個帳號。如果那個確切的帳號不存在，結算會在模擬階段失敗，402 會帶著 `transaction_simulation_failed` 回來，看起來像 client 的 bug，其實是收款帳號不存在。要檢查推導出來的那個地址本身：掃描擁有者的 token account 並不等價，因為同一個 mint 的非標準輔助帳號會通過檢查，但 client 要轉去的 ATA 仍然不存在：

```typescript
import { findAssociatedTokenPda, TOKEN_PROGRAM_ADDRESS } from "@solana-program/token";

const [ata] = await findAssociatedTokenPda({
  mint: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",   // USDC mainnet
  owner: payToAddress,
  tokenProgram: TOKEN_PROGRAM_ADDRESS,                     // Token-2022 的 mint 要用 TOKEN_2022_PROGRAM_ADDRESS
});
```

接著確認那個確切的地址存在：`value: null` 代表不存在，結算到那裡會失敗：

```bash
curl -s https://api.mainnet-beta.solana.com -X POST -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"getAccountInfo",
       "params":["<DERIVED_ATA>",{"encoding":"base64"}]}' \
  | jq '.result.value != null'
```

要建立它（誰建立誰付那一小筆 rent，不是付款方）：

- 用程式的話，把 `@solana-program/token` 的 `getCreateAssociatedTokenIdempotentInstruction` 加進你的 onboarding 流程：idempotent 版本重跑也安全，而且是唯一具有確定性的做法。
- 用 spl-token CLI 執行 `spl-token create-account <MINT> --owner <PAYTO_ADDRESS>`。
- 把那個 token 轉給 `payTo` 也行，但前提是發送方有包含建立指令：錢包和 `spl-token transfer --fund-recipient` 有；對一個不存在的 ATA 直接做 `transferChecked` 會跟結算一樣失敗。

當款項付給剛建立或託管型的錢包時，這個問題最容易踩到，因為它們通常還沒有該資產的 ATA。

**賣方：每個付款授權只能跑一次 route。** Middleware 會驗證付款、執行你的 handler，然後結算。驗證不會消耗授權（結算才會），所以同一個已簽名的付款同時送好幾次，每次都會通過驗證，也每次都會執行你的 handler。Facilitator 只會結算其中一份，其他份會收到沒有回應內容的 402，所以沒有人拿到免費的輸出。但是 handler 裡的每個副作用（LLM 呼叫、排進佇列的 job、鏈上交易）每份都會發生一次。在一個正式環境的賣方（Python `x402` 2.9.0、FastAPI）上，同一個授權並行送三次，產生了三次 handler 執行和一次結算。Handler 裡的付費呼叫計數器也會同樣高估營收，請改成結算之後再計數。更廣泛的 verify 到 settle 之間的 race，在 [x402#1169](https://github.com/x402-foundation/x402/issues/1169) 有討論。

每個授權要在 facilitator 驗證之後、handler 執行之前認領一次。資源 server 的 `onAfterVerify` hook 正好在那個時間點執行，它回傳的 `abort` 會變成 402，而且不會執行 handler：

```typescript
import { createHash } from "node:crypto";
import express from "express";
import { paymentMiddleware, x402ResourceServer } from "@x402/express";
import { HTTPFacilitatorClient } from "@x402/core/server";
import { ExactEvmScheme } from "@x402/evm/exact/server";
import { getBase64Encoder, getTransactionDecoder } from "@solana/kit";
import { createClient } from "redis";

// 用共用、持久、不會被淘汰資料的認領儲存庫。單靠原子插入
// 並不能在儲存庫重置或淘汰後保住認領紀錄；要宣稱有持久的重放防護之前，
// 請另外測試那個營運上的約定。
// 認領儲存庫絕對不能是讓賣方掛掉的原因。關掉離線
// 佇列後，斷線時送出的指令會馬上失敗；佇列上限
// 在儲存庫有連線但不回應時也是一樣；error listener
// 讓 client 的錯誤不會使 process 崩潰；連線在背景建立，
// 所以啟動時不會等它。
const redis = createClient({
  url: process.env.REDIS_URL,
  disableOfflineQueue: true,
  commandsQueueMaxLength: 1_000,
  socket: { connectTimeout: 2_000 },
});
redis.on("error", (err) => console.warn(`replay store: ${err.message}`));
redis.connect().catch(() => {});

const CLAIM_MIN_S = 900;          // 要比 maxTimeoutSeconds 加上你最慢的 handler 執行時間還長
const CLAIM_MAX_S = 366 * 86_400; // 簽名者自訂到期時間的上限
const CLAIM_TIMEOUT_MS = 250;     // 慢的儲存庫不能拖住付費請求
// 儲存庫不可用時：在 handler 執行前拒絕（true），或在沒有
// 重複防護的情況下執行（false）。只有 handler 是冪等的，
// 或它自己有副作用邊界時，才 fail open。
const FAIL_CLOSED = true;

// 辨識一個已驗證的授權，不管它的 JSON 怎麼編碼，並且保留
// 認領紀錄，直到該授權不可能再結算：到期時間是簽名者
// 選的，驗證時不會把它限制在 maxTimeoutSeconds 內。
function claimOf(
  paymentPayload: { payload: Record<string, any> },
  requirements: { network: string; asset: string },
): { key: string; until: number } | undefined {
  const now = Math.floor(Date.now() / 1000);
  const keep = (expiry: unknown) => {
    // 拒絕超出我們保留約定的授權；絕對不縮短
    // 仍有效的授權的認領期限，否則會悄悄重新打開它的重放視窗。
    const validUntil = BigInt(String(expiry));
    if (validUntil < 0n || validUntil + 60n > BigInt(now + CLAIM_MAX_S)) {
      throw new Error("Authorization expiry exceeds the replay retention horizon");
    }
    return Math.max(now + CLAIM_MIN_S, Number(validUntil + 60n));
  };
  const p = paymentPayload.payload;
  if (p.authorization?.nonce) {
    // EVM exact, EIP-3009：每個 token 合約對一組 (from, nonce) 只接受一次。
    const { from, nonce, validBefore } = p.authorization;
    const asset = requirements.asset.toLowerCase();
    return {
      key: `x402:${requirements.network}:${asset}:${from.toLowerCase()}:${nonce.toLowerCase()}`,
      until: keep(validBefore),
    };
  }
  if (p.permit2Authorization?.nonce !== undefined) {
    // EVM exact, Permit2：每個 owner 的 uint256 nonce，跨 token 共用。簽署的
    // 值是 BigInt(nonce)，所以 "1"、"01" 和 "0x1" 是同一個授權。
    const { from, nonce, deadline } = p.permit2Authorization;
    return {
      key: `x402:${requirements.network}:permit2:${from.toLowerCase()}:${BigInt(nonce)}`,
      until: keep(deadline),
    };
  }
  if (typeof p.transaction === "string") {
    // SVM exact：對付款方簽署的 message 做 hash，不是整筆交易。
    // 手續費支付者的簽名欄位不在付款方的簽名範圍內。
    const tx = getTransactionDecoder().decode(getBase64Encoder().encode(p.transaction));
    const digest = createHash("sha256").update(new Uint8Array(tx.messageBytes)).digest("hex");
    return { key: `x402:${requirements.network}:${digest}`, until: now + CLAIM_MIN_S };
  }
  return undefined;
}

function withTimeout<T>(promise: Promise<T>, ms: number): Promise<T> {
  return Promise.race([
    promise,
    new Promise<T>((_, reject) => setTimeout(reject, ms, new Error("timeout")).unref()),
  ]);
}

const resourceServer = new x402ResourceServer(
  new HTTPFacilitatorClient({ url: process.env.FACILITATOR_URL }),
)
  .register("eip155:8453", new ExactEvmScheme())
  .onAfterVerify(async ({ paymentPayload, requirements, result }) => {
    if (!result.isValid) return; // 無效的付款絕對不佔認領
    let claim: ReturnType<typeof claimOf>;
    let set: Promise<string | null> | undefined;
    try {
      claim = claimOf(paymentPayload, requirements);
      if (!claim) {
        return { abort: true, reason: "claim_unsupported", message: "Authorization cannot be guarded." };
      }
      // NX 是原子操作：兩份同時送來的副本，剛好只有一份會成功。
      set = redis.set(claim.key, "1", {
        condition: "NX",
        expiration: { type: "EXAT", value: claim.until },
      });
      if ((await withTimeout(set, CLAIM_TIMEOUT_MS)) === "OK") return;
      return {
        abort: true,
        reason: "payment_replayed",
        message: "This payment authorization was already presented.",
      };
    } catch {
      // 用 return，不要 throw：resource server 遇到丟錯的 hook 會記 log 然後略過，
      // 結果 handler 就在沒有防護的情況下執行了。
      if (FAIL_CLOSED) {
        // 逾時的寫入仍然可能成功。這個請求被拒絕，
        // handler 不會執行，所以要釋放遲到的認領，否則
        // 重試會被當成重放，拒絕一件根本沒做過的工作。
        set?.then((reply) => (reply === "OK" && claim ? redis.del(claim.key) : 0)).catch(() => {});
        return { abort: true, reason: "claim_unavailable", message: "Retry shortly." };
      }
    }
  });

const app = express();
app.use(express.json());
app.use(
  paymentMiddleware(
    {
      "POST /report": {
        accepts: [{ scheme: "exact", price: "$0.01", network: "eip155:8453", payTo: process.env.PAY_TO! }],
      },
    },
    resourceServer,
  ),
);
app.post("/report", async (req, res, next) => {
  try {
    res.json(await buildReport(req.body));
  } catch (error) {
    // 保留認領：失敗的 handler 可能已經產生過副作用。
    next(error);
  }
});
```

任何支援原子條件插入的儲存庫都行：DynamoDB 的 `PutItem` 加 `attribute_not_exists`，或 Postgres 的 unique index。有兩件事這個防護不會替你決定。第一，儲存庫掛掉時，`FAIL_CLOSED` 用可用性換來「每個授權只執行一次」的保證；fail open 會讓 route 繼續運作，但儲存庫恢復前每份副本都會執行 handler，所以只有冪等的 handler 才能這樣用。第二，`payment_replayed` 的意思是這個授權之前出現過，不代表第一次嘗試失敗：如果 client 遺失了第一次的回應，工作可能已經執行、付款可能已經結算，所以它在簽署新授權之前，應該先核對原本的請求。這只能擋下同一個授權的重複副本。付款方如果在 verify 和 settle 之間讓付款失效（例如把資金轉走），仍然會讓 handler 執行一次；對成本高的 route，要先扣住資金再做工作。

**Discovery。** 實作了 x402 bazaar extension 的 facilitator 會提供 `/discovery/resources` endpoint：CDP 目錄在 `https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources`，PayAI 目錄在 `https://facilitator.payai.network/discovery/resources`。Solana 上可付費的服務，還有 Solana Foundation 精選的目錄 [pay.sh](https://pay.sh)。

## 範例

### 在 MCP client 裡強制執行預算

建構會呼叫 agentpay MCP server 的 orchestrator 時，要在派送付費工具呼叫前先強制執行預算。

> **前置條件**：加入 MCP 設定前先安裝套件：不帶 `-y` 的 `npx` 在非互動環境會等待確認，導致 server 卡住：`npm install -g agentwallet-sdk@6.0.0`

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

async function main() {
  // 1. 建構 transport 之前先驗證憑證。
  //    缺少金鑰必須馬上失敗，絕對不能讓子 process 在沒有驗證的情況下啟動。
  const walletKey = process.env.WALLET_PRIVATE_KEY;
  if (!walletKey) {
    throw new Error("WALLET_PRIVATE_KEY is not set — refusing to start payment server");
  }

  // 透過 stdio transport 連到 agentpay MCP server。
  // 只放行 server 需要的環境變數，絕對不要把整個 process.env
  // 轉給管理私鑰的第三方子 process。
  const transport = new StdioClientTransport({
    command: "npx",
    args: ["agentwallet-sdk@6.0.0"],
    env: {
      PATH: process.env.PATH ?? "",
      NODE_ENV: process.env.NODE_ENV ?? "production",
      WALLET_PRIVATE_KEY: walletKey,
    },
  });
  const agentpay = new Client({ name: "orchestrator", version: "1.0.0" });
  await agentpay.connect(transport);

  // 2. 委派給 agent 之前先設定花費政策。
  //    一定要確認成功：靜默失敗代表沒有任何控管生效。
  const policyResult = await agentpay.callTool({
    name: "set_policy",
    arguments: {
      per_task_budget: 0.50,
      per_session_budget: 5.00,
      allowlisted_recipients: ["api.example.com"],
    },
  });
  if (policyResult.isError) {
    throw new Error(
      `Failed to set spending policy — do not delegate: ${JSON.stringify(policyResult.content)}`
    );
  }

  // 3. 任何付費動作之前先用 preToolCheck
  await preToolCheck(agentpay, 0.01);
}

// Pre-tool hook：fail-closed 的預算強制檢查，有四條不同的錯誤路徑。
async function preToolCheck(agentpay: Client, apiCost: number): Promise<void> {
  // 路徑 1：拒絕無效輸入（NaN/Infinity 會繞過 < 比較）
  if (!Number.isFinite(apiCost) || apiCost < 0) {
    throw new Error(`Invalid apiCost: ${apiCost} — action blocked`);
  }

  // 路徑 2：transport/連線失敗
  let result;
  try {
    result = await agentpay.callTool({ name: "check_spending" });
  } catch (err) {
    throw new Error(`Payment service unreachable — action blocked: ${err}`);
  }

  // 路徑 3：工具回傳錯誤（例如驗證失敗、錢包尚未初始化）
  if (result.isError) {
    throw new Error(
      `check_spending failed — action blocked: ${JSON.stringify(result.content)}`
    );
  }

  // 路徑 4：解析並驗證回應的格式
  let remaining: number;
  try {
    const parsed = JSON.parse(
      (result.content as Array<{ text: string }>)[0].text
    );
    if (!Number.isFinite(parsed?.remaining)) {
      throw new TypeError("missing or non-finite 'remaining' field");
    }
    remaining = parsed.remaining;
  } catch (err) {
    throw new Error(
      `check_spending returned unexpected format — action blocked: ${err}`
    );
  }

  // 路徑 5：超出預算
  if (remaining < apiCost) {
    throw new Error(
      `Budget exceeded: need $${apiCost} but only $${remaining} remaining`
    );
  }
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
```

## 最佳實務

- **委派前先設預算**：派生 sub-agent 時，透過你的 orchestration 層附上 SpendingPolicy。絕對不要給 agent 無限的花費額度。
- **固定你的相依套件版本**：MCP 設定裡一定要指定確切版本（例如 `agentwallet-sdk@6.0.0`）。上正式環境前要驗證套件完整性。
- **稽核軌跡**：在 post-task hook 裡用 `list_transactions` 記錄花了多少、為什麼花。
- **Fail closed**：付款工具連不上時，擋掉付費動作，不要退回成不受計量的存取。
- **搭配 security-review**：付款工具是高權限的。要用跟 shell 存取一樣的標準來審視。
- **先用測試網測**：開發用 Base Sepolia，上線再切到 Base mainnet。在 Solana 上，先用 Solana devnet（`solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1`）和免費的 x402.org facilitator 開發，再換到 mainnet 的正式 facilitator。
- **在 Solana 上要放 USDC，不是 SOL**：Exact-SVM scheme 讓 facilitator 當交易手續費支付者，所以沒有 SOL 的錢包一樣能付款。簽名前，要用預期的 USDC mint（mainnet `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`、devnet `4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU`）驗證每個 challenge 的 `asset`：什麼資產都付的包裝 client，就是你預算上的漏洞。

## 正式環境參考

- **npm**：[`agentwallet-sdk`](https://www.npmjs.com/package/agentwallet-sdk)
- **已合併進 NVIDIA NeMo Agent Toolkit**：[PR #17](https://github.com/NVIDIA/NeMo-Agent-Toolkit-Examples/pull/17)，給 NVIDIA agent 範例用的 x402 付款工具
- **協定規格**：[x402.org](https://x402.org)
- **OKX Payments SDK**：[`okx/payments`](https://github.com/okx/payments)，涵蓋 X Layer x402 的 TypeScript、Go、Rust 和 Java 賣方整合
- **OKX Agent Payments Protocol skill**：[`okx/onchainos-skills`](https://github.com/okx/onchainos-skills/tree/main/skills/okx-agent-payments-protocol)
- **OKX Payments 概覽**：[web3.okx.com/onchainos/dev-docs/payments/overview](https://web3.okx.com/onchainos/dev-docs/payments/overview)
- **上游 x402 monorepo**：[`x402-foundation/x402`](https://github.com/x402-foundation/x402)，包含 TypeScript、Python 和 Go 實作，以及維護中的 client 和 server 範例
- **x402 文件**：[docs.x402.org](https://docs.x402.org)；正式環境 facilitator 清單在 [docs.x402.org/dev-tools/facilitators](https://docs.x402.org/dev-tools/facilitators)
- **`@x402` 套件**：[npmjs.com/org/x402](https://www.npmjs.com/org/x402)，包含 `@x402/fetch`、`@x402/axios`、`@x402/express`、`@x402/hono`、`@x402/next`、`@x402/fastify`、`@x402/evm`、`@x402/svm`
- **Facilitator**：[自行 facilitate 範例](https://github.com/x402-foundation/x402/tree/main/examples/typescript/servers/self-facilitation)（沒有第三方）、[x402.org facilitator](https://x402.org/facilitator)（測試網預設），以及維護中的[正式環境清單](https://docs.x402.org/dev-tools/facilitators)
- **Discovery**：`/discovery/resources` 上的 CDP 和 PayAI bazaar；Solana 上可付費的服務請看 [pay.sh](https://pay.sh)
