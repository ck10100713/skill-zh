---
name: "tw-ecom-payment-newebpay"
description: "透過 mcp-newebpay，替台灣電商串接 NewebPay（藍新金流）。當要在 NewebPay 上收信用卡 / ATM / 超商 / LINE Pay / 定期定額付款、處理 3DS 2.0 流程、計算 TradeSha 簽章，或對帳 callback webhook 時使用。比較金流（看 tw-payment-integration）或非 NewebPay 業者（TapPay、ECPay 各有自己的 skill）「不要」用這個。"
metadata:
  category: "WP-05 台灣創業"
  domain: "ecommerce-tw"
  layer: "payment"
  related_mcps: ["mcp-newebpay"]
  related_skills: ["tw-payment-integration", "tw-ecom-payment-dispute", "tw-ecom-invoice-ezpay"]
  last_verified: "2026-04"
  tags: ["taiwan", "payment", "newebpay", "fintech"]
---

# NewebPay 串接方法論

## 何時使用這個 skill

- 在台灣店面透過 NewebPay（藍新金流）收款：信用卡、ATM（虛擬帳號）、超商條碼、LINE Pay、Apple Pay、Taiwan Pay、Samsung Pay
- 設定定期定額（信用卡定期扣款），像訂閱盒、SaaS、內容網站、捐款平台
- 把 NewebPay 的 callback webhook 和內部訂單狀態對帳，或除錯為什麼訂單「在 NewebPay 已付款」但「在我們 DB 還是未結」
- 透過 `mcp-newebpay` 處理退款、取消授權，或信用卡交易的請款
- 除錯 AES-256-CBC / TradeSha 簽章不符、3DS 2.0 責任轉移行為，或 `MPGGateway` 表單送出失敗

## 何時「不要」使用

- 問題是「我們該選哪個金流？」，請用 `tw-payment-integration`（NewebPay / ECPay / TapPay / LINE Pay Direct 的比較）
- 商家用的是 ECPay（綠界）或 TapPay，它們有自己的 skill，API / 簽章機制也不同
- 你只需要某個 NDNF/NDNP endpoint 的精確 API schema，請讀 `mcp-newebpay` 的 tool 描述，或 NewebPay 官方 PDF（`線上交易─幕前支付技術串接手冊_NDNF` / `信用卡定期定額串接技術手冊_NDNP`）
- 糾紛是關於拒付 / 爭議款處理，請看 `tw-ecom-payment-dispute`

## 核心概念

NewebPay（藍新金流）是台灣三大主流金流之一（另外兩個是 ECPay 和 TapPay）。它是**聚合型**業者：一份商家合約涵蓋信用卡、ATM、超商和錢包管道，各自有自己的結算週期。`mcp-newebpay` 包了 8 個官方 tool，涵蓋兩個 API 系列：

- **NDNF（線上交易）**：一次性交易。Tool：`create_mpg_payment`、`query_trade`、`cancel_authorization`、`close_refund`、`ewallet_refund`。
- **NDNP（定期定額）**：信用卡定期扣款授權。Tool：`create_period_payment`、`alter_period_status`、`alter_period_content`。

NDNF 和 NDNP 是**分開的商家帳號**，各有自己的 `MerchantID` + `HashKey` + `HashIV` 三件組。設定一個不會啟用另一個。

**簽章機制。** 每個請求 body 都用商家的 `HashKey`（32 字元）和 `HashIV`（16 字元）以 AES-256-CBC 加密成 `TradeInfo`，再對 `HashKey=…&{TradeInfo}&HashIV=…` 計算 SHA-256 的 `TradeSha`，結果轉大寫（是這個固定格式，不是一般的參數排序，見常見陷阱）。版本是 `2.0`。3DS 2.0 的責任轉移由 NewebPay 託管的 MPG 頁面處理；商家看不到卡號 PAN。

**信任邊界。** `create_mpg_payment` / `create_period_payment` 回傳加密過的表單資料，要由**瀏覽器端 POST** 到 `https://ccore.newebpay.com/MPG/mpg_gateway`（production 是 `core.newebpay.com`）。商家後端永遠看不到卡號 PAN。付款結果透過兩個管道送達：**NotifyURL**（server 對 server 的 webhook）和 **ReturnURL**（瀏覽器重新導向）。這兩個可能亂序抵達。

## 決策樹

```
What is the user asking for?
│
├─ New one-time payment (credit card / ATM / CVS / wallet)?
│    → NDNF: create_mpg_payment
│      Returns {url, form_data} → merchant must render an auto-submit form
│      Result arrives via NotifyURL (trust) + ReturnURL (display only)
│
├─ Subscription / 定期定額 / recurring membership?
│    → NDNP: create_period_payment
│      Separate MerchantID from NDNF — verify both credential sets exist
│      Changes after go-live: alter_period_status (pause/resume/terminate),
│                              alter_period_content (amount/cycle/expiry)
│
├─ "Did this order get paid?" / reconciliation?
│    → NDNF: query_trade  (canonical source of truth for a single MerchantOrderNo)
│      Use this whenever NotifyURL was missed, duplicated, or suspect
│
├─ Refund / cancellation?
│    ├─ Credit card, before close (請款)? → cancel_authorization (NPA-B01)
│    ├─ Credit card, after close?         → close_refund (NPA-B03x)
│    └─ LINE Pay / Taiwan Pay / e-wallet? → ewallet_refund (NPA-B06)
│
└─ Recurring mandate state change?
     ├─ Pause / resume / terminate      → alter_period_status
     └─ Change amount / cycle / expiry  → alter_period_content
```

當 `mcp-newebpay` 回報「tool not configured」錯誤，代表對應的 NDNF 或 NDNP 環境變數群組沒設定，見 README 的 `Environment variables` 表。

## 實作指引

三種流程。每個都標出確切的 `mcp-newebpay` tool。完整串接見 `references/integration-flow.md`，端到端的訂閱完整範例見 `examples/sample_scenario.md`。

**一次性付款（NDNF）**

1. 商家後端呼叫 `create_mpg_payment`，帶上 `MerchantOrderNo`（你的冪等 key）、`Amt`（整數 TWD）、`ItemDesc`、`Email`、`NotifyURL`、`ReturnURL`，以及要啟用哪些付款方式（`CREDIT`、ATM 用 `VACC`、`CVS`、`BARCODE`、`LINEPAY`、`APPLEPAY`……）
2. 回傳值是 `{url, form_data}`。商家**一定要渲染一個自動送出的 HTML 表單**，把 `form_data` POST 到 `url`。不要試著在 server 端跟隨重新導向，顧客一定要在自己的瀏覽器上進到 NewebPay 的託管頁面，3DS 2.0 才能運作。
3. 顧客付款後，NewebPay 會觸發 **NotifyURL**（server 對 server 的 POST，解密 `TradeInfo`，檢查 `Status == "SUCCESS"`）。這是權威事件。顧客的瀏覽器也會被導向 **ReturnURL**，這只能當作 UI 提示，絕對不能當完成訊號。
4. 對帳有疑慮時，呼叫 `query_trade(MerchantOrderNo, Amt)` 在 server 端重新確認。

**定期扣款 / 定期定額（NDNP）**

1. `create_period_payment`：建立授權。需要 NDNP 憑證。回傳同樣的 `{url, form_data}` 形狀；顧客要在 NewebPay 的託管頁面完成一次互動式驗證來授權。之後 NewebPay 會依週期自動扣款，並在每個週期觸發 NotifyURL。
2. 每個扣款週期：NewebPay 對儲存的卡扣款，並 post 到 NotifyURL。商家要分別處理 `Status == "SUCCESS"`（給予服務期間）和失敗（卡過期、餘額不足、收單行拒絕），失敗不會自動重試。
3. 授權生命週期：用 `alter_period_status` 暫停/恢復/終止；用 `alter_period_content` 改金額/週期/到期日。要把 `PeriodNo`（例如 `P260403144725zl3MVV`）當作標準識別碼，不是商家訂單編號。

**退款**

- 信用卡路徑要看請款狀態。請款前：`cancel_authorization` 釋放預授權。請款後：用 `close_refund`，operation 帶 `refund` / `cancel_refund`。請款本身也是用 `close_refund`，operation 帶 `close` / `cancel_close`。
- 電子錢包（LINE Pay / Taiwan Pay）的路徑不同：`ewallet_refund`，信用卡的 close_refund tool 對錢包管道無效。
- 選退款 tool 之前，一定要先用 `query_trade` 確認 `CloseStatus`（3 = 已結算）。

## 常見陷阱

- **TradeSha 不是一般依字母排序的 HMAC。** 它是 `SHA256("HashKey={key}&{TradeInfo blob}&HashIV={iv}").upper()`：`HashKey` 在最前、`HashIV` 在最後，中間夾著原樣的加密 `TradeInfo`，結果是大寫的十六進位。把它當成「參數依字母排序後做 HMAC」的開發者，做出來的東西什麼都驗證不過。`mcp-newebpay` 已經幫你處理了；如果你要自己手寫 NotifyURL 的驗證器，要原封不動複製這個格式。
- **NotifyURL 可能比 ReturnURL 早到、晚到或同時到。** 絕對不要只靠 ReturnURL 就結掉訂單，瀏覽器可能被關掉、重新導向可能失敗，或 NotifyURL 比重新導向更早到你的 server。ReturnURL 的用途是「給顧客看感謝頁」；NotifyURL 的意思是「錢已經動了」。如果你的訂單狀態機依賴先後順序，就會出現重複出貨或幽靈未結訂單。
- **NDNF 和 NDNP 用不同的 MerchantID / HashKey / HashIV。** 搞混會產生簽章有效但商家錯誤的請求，NewebPay 會用一般性的錯誤拒絕。`mcp-newebpay` 用分開的環境變數群組（`NEWEBPAY_NDNF_*` vs `NEWEBPAY_NDNP_*`）就是為了避免這件事；不要在包裝程式碼裡把它們合併。
- **HashIV 必須剛好 16 bytes；HashKey 必須剛好 32 bytes。** 從舊的 MPG1 協定遷移過來的商家，常常重用長度不對的 MPG1 金鑰，AES-256-CBC 就會無聲地補齊/截斷，每個請求在 NewebPay 那邊都解密失敗，只回一個含糊的「參數錯誤」。如果所有請求都失敗，先檢查長度再說。
- **定期定額不會自動處理卡片過期。** 顧客的卡過期時，NewebPay 會在下個週期把授權標記為失敗並用失敗碼觸發 NotifyURL，但不會自動暫停授權。你的後端必須偵測失敗碼、通知顧客（SMS / email 附上更新卡片的連結），並決定要不要用 `alter_period_status` 暫停。無聲的失敗會累積成未收的訂閱月份。
- **測試 endpoint 是 `ccore.newebpay.com`；production 是 `core.newebpay.com`。** 兩者接受的是分開配發的 MerchantID / HashKey 組合；拿測試金鑰打 production endpoint（或反過來）會回「MerchantID 不存在」，看起來像憑證錯誤，其實是 endpoint 錯了。`mcp-newebpay` 透過 `NEWEBPAY_ENV=test|production` 切換；除錯憑證之前，先確認這個。

## IRON LAW

**NotifyURL 才是事實來源，不是 ReturnURL。** 絕對不要根據 ReturnURL 的參數或瀏覽器重新導向，就把訂單轉成「已付款」，也不要觸發下游的效果，像是開電子發票、出貨或啟用訂閱。這能防止兩種具體的失敗：(1) 顧客提早關掉瀏覽器再重試，導致 ReturnURL 抵達兩次而重複出貨；(2) NotifyURL 已觸發但瀏覽器從未到達 ReturnURL（飛航模式、網路中斷）造成幽靈未結訂單。如果 NotifyURL 還沒收到並在 server 端驗證過，訂單就是未結，不管 ReturnURL 頁面怎麼說。有疑問時，呼叫 `query_trade` 重新確認；把那個 server 回應視同 NotifyURL 的重試。

### 合理化藉口對照表

| "但是…" | 為什麼錯 |
|---|---|
| 客戶已經在感謝頁了，付款應該成功了 | ReturnURL 可以被重新整理重放、也可以在付款失敗後仍然跳轉（NewebPay 某些錯誤路徑仍會跳回 ReturnURL）|
| NotifyURL 和 ReturnURL 幾乎同時到，先用 ReturnURL 更新再等 NotifyURL 確認就好 | 非同步順序無法保證；高流量期間兩者可差數分鐘，先更新會產生競態條件導致雙重履行 |
| 我需要立刻給客戶看訂單確認，等 NotifyURL 太慢 | ReturnURL 完全可以用於顯示 UI（「處理中，請稍候」），訂單狀態變更必須等 NotifyURL；這兩件事不衝突 |
| 我們的 NotifyURL 偶爾收不到，所以 ReturnURL 是備援 | 備援邏輯應是「若 N 分鐘內未收到 NotifyURL，呼叫 `query_trade` 主動查詢」，而非信任 ReturnURL |

## 輸出格式

完成 NewebPay 任務時，產出這個結構：

```markdown
# NewebPay Task: {one-line summary}

## Context
- API family: {NDNF one-off | NDNP recurring | mixed}
- Environment: {test (ccore) | production (core)}
- Payment methods enabled: {CREDIT, VACC, CVS, LINEPAY, ...}
- MerchantOrderNo scheme: {…}

## Tool Plan
| Step | Tool | Family | Purpose |
|------|------|--------|---------|
| 1 | create_mpg_payment | NDNF | Build encrypted form for browser redirect |
| 2 | (browser POSTs form) | — | Customer completes 3DS 2.0 on NewebPay |
| 3 | NotifyURL handler | — | Decrypt TradeInfo, verify TradeSha, update order |
| 4 | query_trade | NDNF | Reconciliation on doubt |
| … | … | … | … |

## Callback Handling
- NotifyURL verification: TradeSha recomputed with HashKey={…}&{TradeInfo}&HashIV={…} uppercased: Y/N
- ReturnURL treated as UI-only (no state mutation): Y/N
- query_trade fallback on missed NotifyURL: Y/N
- Idempotency key: MerchantOrderNo

## Assumptions & Open Questions
- {assumption grounded in a NewebPay constraint}
- TODO: {anything that needs verification against NewebPay merchant portal or NDNF/NDNP PDF}

## Deliverable
{the actual integration, reconciliation report, or change summary}
```

## 相關

- **MCP**：`mcp-newebpay`
- **Skill**：`tw-payment-integration`（金流比較的決策）、`tw-ecom-payment-dispute`（拒付 / 爭議款處理）、`tw-ecom-invoice-ezpay`（付款成功後的電子發票交接）、`tw-ecom-dtc-shopline`（店面整合）
- **參考資料**：`references/integration-flow.md`（商家設定 → 第一筆交易 → callback → 對帳）、`examples/sample_scenario.md`（搭配 ezPay 發票和糾紛處理的訂閱收款）

_Last verified: 2026-04_
