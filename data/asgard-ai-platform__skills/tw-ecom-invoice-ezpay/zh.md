---
name: "tw-ecom-invoice-ezpay"
description: "透過 mcp-ezpay-einvoice，用 ezPay（加值服務中心）開立與管理台灣電子發票。當要開立 B2B/B2C 發票、處理載具（手機條碼、自然人憑證）、在同一雙月期間內作廢，或跨期開立折讓時使用。直接串接財政部 API（看 tw-einvoice-guide）或以 UniversalEC 為底的流程（看 tw-ecom-invoice-universalec）「不要」用這個。"
metadata:
  category: "WP-05 台灣創業"
  domain: "ecommerce-tw"
  layer: "invoice"
  related_mcps: ["mcp-ezpay-einvoice"]
  related_skills: ["tw-einvoice-guide", "tw-ecom-invoice-carrier", "tw-ecom-invoice-void", "tw-tax-basics"]
  last_verified: "2026-04"
  tags: ["taiwan", "e-invoice", "ezpay", "tax-compliance"]
---

# ezPay 電子發票方法論

## 何時使用這個 skill

- 從台灣的店面、POS 或 SaaS 後台，透過 ezPay（藍新系）作為加值服務中心，開立 B2B 或 B2C 統一發票
- 附上消費者載具（手機條碼 (`/XXXXXXX`)、自然人憑證或會員載具），讓發票不用印紙本
- 在同一雙月期間內作廢開錯的發票，或在作廢期限已過時開立折讓
- 開立或觸發要在之後某天生效的排程發票（`status="3"`）（例如訂閱續約）
- 每天把 ezPay 開立的發票和財政部電子發票整合服務平台對帳，抓出上傳延遲或遺失的紀錄
- 除錯 ezPay 難以理解的回應：`LIB10002` 加密失敗、`INV20002` 作廢期限錯誤、`ALW10001` 折讓超過發票金額的錯誤

## 何時「不要」使用

- 商家直接連財政部平台（沒有加值中心），財政部直連的模式和概念請用 `tw-einvoice-guide`
- 店面用的是 UniversalEC（統一發票整合服務）或其他加值中心（ECPay 綠界、銓葳），它們的 tool 形狀不同；這個 skill 的陷阱都是 ezPay 專屬
- 你只需要某個 ezPay endpoint 的 API schema，請讀 `mcp-ezpay-einvoice` 的 tool 描述，或 ezPay 開發者入口 https://inv.ezpay.com.tw/
- 問題是「什麼是手機條碼」或「B2B 與 B2C 發票格式」，那是 `tw-einvoice-guide` 已涵蓋的基礎內容。這個 skill 假設你已經懂整體脈絡

## 核心概念

ezPay 是加值服務中心，也就是中間人：它把商家的開票請求批次處理，代替商家上傳到財政部電子發票整合服務平台，並把載具 / 捐贈碼的查詢結果回傳。就稅務而言，商家的法律對象**仍然是財政部**；ezPay 只是營運上的便利，不是事實來源。

`mcp-ezpay-einvoice` 把 ezPay API 包成 7 個 tool：

- 發票生命週期：`issue_invoice`、`trigger_invoice`、`void_invoice`、`query_invoice`
- 折讓生命週期：`issue_allowance`、`trigger_allowance`、`void_allowance`

**類別。** `category="B2B"` 需要 `buyer_ubn`（統編），漏掉的話發票會無聲地變成 B2C（可對獎、稅務申報也錯）。`category="B2C"` 會附上載具或印紙本。

**載具。** `carrier_type="0"` + `carrier_num="/ABC1234"` 是手機條碼（斜線 + 7 個字元）。`carrier_type="1"` 是自然人憑證（2 個字母 + 14 位數字）。`carrier_type="2"` 是 ezPay 會員載具。`love_code`（3-7 位數字）是捐贈碼，和載具互斥。

**字軌。** 財政部每個雙月期間會配發發票號碼區間（字軌）（例如 `TE00000000-TE99999999`）。ezPay 開票時從這個池子取號。區間用完就無法開票，財政部會提前配發下一期的區間，但前提是你有申請。

**作廢 vs 折讓。** `void_invoice` 只在發票開立的同一個雙月期間內有效（見常見陷阱）。期間結束後，更正必須走 `issue_allowance` → `trigger_allowance`（狀態 `C`=確認，`D`=取消）。

## 決策樹

```
What is the user asking for?
│
├─ Issue a NEW invoice?
│    ├─ Buyer has 統編?  → issue_invoice(category="B2B", buyer_ubn=...)
│    └─ Consumer?         → issue_invoice(category="B2C", carrier_type/carrier_num
│                                         OR love_code OR print_flag="Y")
│
├─ Scheduled invoice (issue on a future date)?
│    → issue_invoice(status="3", create_status_time="YYYY-MM-DD")
│      Later: trigger_invoice(invoice_trans_no, merchant_order_no, total_amt)
│
├─ Correct a WRONG invoice?
│    ├─ Issued in the CURRENT bimonthly period?
│    │    → void_invoice(invoice_number, invalid_reason)
│    │      (Then re-issue fresh if needed)
│    └─ Issued in a PAST bimonthly period?
│         → issue_allowance(invoice_no, items, total_amt)
│             → trigger_allowance(allowance_no, allowance_status="C")
│           (Voiding the allowance later: void_allowance)
│
├─ Partial refund (return 1 of 3 items)?
│    → issue_allowance against the original invoice for the returned portion only
│
└─ "Did this invoice issue?" / "What's the status of order X?"
     → query_invoice(search_type="0" by invoice number, "1" by merchant_order_no)
       Treat ezPay's answer as a local cache — MOF platform is the authority
```

作廢期限的邊界：依 README，截止時間大約是「下個奇數月 14 號之前」（例如 3-4 月的發票必須在 5 月 14 日前作廢）。確切的截止日要對照當期的財政部日曆確認，它會隨國定假日移動。

## 實作指引

三種流程。每個都標出確切的 `mcp-ezpay-einvoice` tool。設定串接見 `references/issuance-flow.md`，端到端的 Shopline → ezPay → 折讓完整範例見 `examples/sample_scenario.md`。

**開立發票（一次性，付款後）**

1. 從付款成功的 callback（NewebPay / ECPay / TapPay 的 NotifyURL）觸發。絕對不要從瀏覽器的 ReturnURL 開票，見 `tw-ecom-payment-newebpay` 的 IRON LAW。
2. 呼叫 `issue_invoice` 之前，先在 client 端驗證載具：手機條碼是 `/` + 7 個英數字；自然人憑證是 2 個字母 + 14 位數字。載具字串無效時，ezPay 只會回一般性的錯誤，而且發票不會建立。
3. 呼叫 `issue_invoice`，帶上 `category`、`tax_type="1"`（應稅）、`amt`（未稅）、`tax_amt`、`total_amt`（`amt + tax_amt`）、以 pipe 分隔的品項陣列，有提供載具時 `print_flag="N"`。
4. 以你內部的 `merchant_order_no` 為 key，保存回傳的 `InvoiceNumber`、`InvoiceTransNo` 和 `RandomNumber`。之後對照中獎時需要隨機碼。

**作廢發票（同期更正）**

1. 先呼叫 `query_invoice` 確認發票仍可作廢：已作廢過的發票會回 `INV20001`；超出期限的發票會回 `INV20002`。
2. 呼叫 `void_invoice(invoice_number, invalid_reason)`。原因字串是自由文字的稽核欄位，要寫具體（例如「買家出貨前取消」，不要寫「誤開」）。
3. 需要重開的話，用**新的** `merchant_order_no` 呼叫 `issue_invoice`，舊的現在已永久綁定在作廢的發票上，重複使用會回 `INV10001`（商家訂單編號重複）。

**折讓（跨期更正或部分退款）**

1. 呼叫 `issue_allowance(invoice_no, items[], total_amt)`，只帶被退貨/退款的品項。折讓的 `total_amt` 同時包含商品和稅額（依 README 範例：商品 65 + 稅 3 = 總計 68）。
2. 折讓一開始是待處理狀態。呼叫 `trigger_allowance(allowance_no, allowance_status="C")` 確認（或在向財政部申報前用 `"D"` 取消）。
3. 如果折讓本身開錯了，`void_allowance(allowance_no, invalid_reason)` 可以撤銷，但只限在折讓自己的可作廢期限內（類似發票作廢，但是分開追蹤）。
4. 折讓金額不能超過原發票金額，超過就會觸發 `ALW10001`。如果全額退款超過單張發票，每張發票要各開一張折讓，不能合併。

## 常見陷阱

- **字軌用完會無聲地擋住開票。** 財政部每個雙月期間配發號碼區間；ezPay 從中取號。如果你沒有提前申請下一期的區間（透過 ezPay 商家入口或財政部平台），換期後第一次開票就會失敗，而且錯誤訊息不明。要每週監控剩餘號碼數，並至少提前 1 個雙月期間申請下一個區間。（TODO: 對照目前的 ezPay 商家入口，確認確切的入口路徑和 ezPay 有沒有自動補號選項。）
- **作廢期限只限同一雙月；跨期更正需要折讓。** 依 README，3-4 月開立的發票大約可在 5 月 14 日前作廢。3 月的發票到 6 月才發現有誤就不能作廢，`void_invoice` 會回 `INV20002`（作廢期間已過）。唯一的更正路徑是 `issue_allowance` + `trigger_allowance`。無限重試 `void_invoice` 的 agent 永遠解決不了這個錯誤。
- **手機條碼格式很嚴格：`/` + 剛好 7 個英數字元。** `ABC1234`（沒有斜線）、`/ABC12345`（8 個字元）、小寫，或前面帶空白的掃描條碼都會失敗。呼叫 `issue_invoice` 前要在 client 端驗證，ezPay 對無效載具的錯誤是一般性的，而且發票不會建立，所以事後無法靠修補來補救。很多 POS 掃描器也需要設定成輸出 `/` 前綴；要用真的手機條碼來測，不要用手打輸入。
- **B2B 銷售漏了 `buyer_ubn` 會無聲地變成 B2C。** `category="B2B"` 沒帶 `buyer_ubn` 會被拒絕，但 `category="B2C"` 對上「本來應該有統編」的企業買家，就會開出 B2C 發票，這種發票可對獎、課稅方式也不同。當買家在你的 CRM 裡是公司時，要在後端強制 `category="B2B"` + `buyer_ubn`，不要只靠 UI。只在 UI 強制的話，會被 webhook 重播舊的 payload 繞過。
- **ezPay 的狀態可能落後財政部平台，要對財政部對帳，不是對 ezPay。** `query_invoice` 回傳的是 ezPay 的內部紀錄。稅務責任是在財政部電子發票整合服務平台成立的，而 ezPay 是批次上傳。`query_invoice` 成功不代表發票已在財政部平台上。要跑每日對帳 job，抓財政部的上傳狀態（逐張或逐批），並和你的 DB 對帳。報稅時，ezPay 的本地狀態和你自己的 DB 都不能當作事實來源。（TODO: 從 ezPay 商家入口的報表儀表板，確認 ezPay 到財政部的確切上傳延遲。）
- **以 pipe 分隔的品項陣列是依位置對應的，一個欄位錯位就會弄壞每個品項。** `item_name="拿鐵|蛋糕"`、`item_count="2|1"`、`item_price="65|85"`、`item_amt="130|85"` 的 pipe 數量和順序必須完全一致。前面或後面多一個 `|`，或某一行少一個欄位，後面每個品項的價格都會錯位到別的名稱上。ezPay 不會驗證對齊，你送什麼它就存什麼。每次流程變更後，都要開完票再用 `query_invoice` 稽核。

## IRON LAW

**財政部是事實來源；ezPay 的狀態可能落後。** 絕對不要只憑 ezPay 回傳 `SUCCESS` 或 `query_invoice` 查得到，就結帳、就申報 401（營業稅），或告訴客戶「發票已開立」。ezPay 是批次處理的加值中心，它的本地紀錄可能領先、落後，或無聲地和財政部電子發票整合服務平台不同步。對前 48 小時內開立的每張發票，都要每天對財政部平台的上傳狀態對帳。任何沒有確認上傳到財政部的 ezPay 紀錄，都是待處理，不是已開立。這能防止兩種失敗：(1) 營業稅申報帶著財政部從未收到的幽靈發票（稽核發現、罰款）；(2) 對客戶宣稱「發票已開立」，但載具/對獎紀錄在財政部根本不存在（消費者客訴、品牌受損）。有疑問時，財政部說了算。

### 合理化藉口對照表

| "但是…" | 為什麼錯 |
|---|---|
| `issue_invoice` 回傳 `SUCCESS`，發票一定開出去了 | `SUCCESS` 只代表 ezPay 本地接受請求；上傳財政部是非同步批次，可能延遲數小時或靜默失敗 |
| `query_invoice` 查得到這張發票，代表 MOF 也有 | `query_invoice` 查的是 ezPay 本地快取，不是財政部電子發票整合服務平台 |
| 客戶手機條碼已經收到通知，所以發票在 MOF 上了 | 載具通知由 ezPay 發送，與 MOF 上傳是不同的非同步流程，兩者可不同步 |
| 每張都對帳太耗效能，ezPay 不太會出錯 | 出錯頻率低不等於零；稅務申報錯誤的代價（罰款、重審）遠高於每日對帳的成本 |

## 輸出格式

完成 ezPay 發票任務時，產出這個結構：

```markdown
# ezPay Invoice Task: {one-line summary}

## Context
- Environment: {test (cinv.ezpay.com.tw) | production (inv.ezpay.com.tw)}
- Category: {B2B | B2C | mixed}
- Carrier strategy: {手機條碼 | 自然人憑證 | 會員載具 | 捐贈碼 | 紙本}
- Trigger source: {payment NotifyURL | scheduled | manual | reconciliation}

## Tool Plan
| Step | Tool | Purpose |
|------|------|---------|
| 1 | query_invoice | Pre-check for duplicate merchant_order_no |
| 2 | issue_invoice | B2B/B2C issuance with validated carrier |
| 3 | (MOF reconciliation) | Confirm upload status against MOF platform |
| … | … | … |

## Correction Path (if applicable)
- Same-period: void_invoice → (optionally) re-issue_invoice with new merchant_order_no
- Cross-period or partial: issue_allowance → trigger_allowance (status="C")

## Assumptions & Open Questions
- Tax semantics: {tax_type="1" 應稅 with tax_rate=5, amt/tax_amt/total_amt consistent}
- Carrier validated client-side before API call: Y/N
- 統編 validated against company registry (if B2B): Y/N
- TODO: {anything that needs verification against ezPay merchant portal or MOF platform}

## Reconciliation
- ezPay → MOF upload check window: {24h / 48h / …}
- Mismatch handling: {retry / manual portal fix / support ticket}
- Daily reconciliation job: Y/N, cron at {…}

## Deliverable
{the actual issuance record, correction summary, or reconciliation report}
```

## 相關

- **MCP**：`mcp-ezpay-einvoice`
- **Skill**：`tw-einvoice-guide`（財政部平台概覽、B2B/B2C/載具基礎）、`tw-ecom-invoice-carrier`（載具專屬模式，skeleton）、`tw-ecom-invoice-void`（作廢 vs 折讓的決策，skeleton）、`tw-tax-basics`（營業稅 401 申報對帳）、`tw-ecom-payment-newebpay`（透過付款 NotifyURL 的上游觸發）、`tw-ecom-dtc-shopline`（訂單到發票的交接）
- **參考資料**：`references/issuance-flow.md`（註冊 → 字軌 → sandbox → prod → 每日對帳）、`examples/sample_scenario.md`（Shopline 手機條碼訂單 → ezPay 發票 → 跨期退款 → 折讓）

_Last verified: 2026-04_
