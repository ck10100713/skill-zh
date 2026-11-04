---
name: month-end-prep
description: >
  把會計帳本（MYOB、NetSuite、QuickBooks、Xero 或 Zoho Books）跟 PayPal、
  Shopify、Square、Stripe 的撥款結算做對帳，標出需要處理的交易、可疑的重複
  項目和缺少的收據，然後寫一份白話的損益（P&L）說明，並匯出結帳包
  （xlsx + 一頁 PDF）。這是 /close-month 指令的第一個環節；要求結算本月或
  結帳的請求會導向那裡，該指令會先執行這個 skill，再更新預測並發送結帳包。
  只有在老闆只想要對帳、不要更新預測也不要發送時，才直接使用這個 skill：
  「just reconcile, no packet」、「what's missing from the books」、
  「flag the duplicates and missing receipts」，或「write the P&L narrative
  for this month」。
allowed-tools: Read, WebFetch
---

# 月結準備（Month End Prep）

## 快速開始

連接你的記帳帳本和至少一個支付處理商，然後說「let's
close the month」。Claude 會帶你走過檢查清單的每一步，在每個關卡暫停等你的
輸入，才繼續往下。

任何已連接的帳本都能跑結帳。每一種帳本都有一份 reference 檔，說明它的讀取方式和
「需要處理」的訊號：[reference/quickbooks-reconcile.md](reference/quickbooks-reconcile.md)、
[reference/xero-reconcile.md](reference/xero-reconcile.md)、
[reference/zoho-books-reconcile.md](reference/zoho-books-reconcile.md)；NetSuite 和 MYOB
在 [reference/v2_sources.md](reference/v2_sources.md)。帳本之間地位平等
（`../../shared/connector-neutrality.md`）：如果連了兩個，就問哪一個才是要結的
帳，另一個只讀它獨有的資料，並且絕對不准把同一個數字跨兩邊加總。

每個金額都用該企業的幣別（`../../shared/currency-and-locale.md`）。
下面的門檻（0.50、0.01、25）都是以該幣別計。

如果缺少 connector，Claude 會退而請你提供 CSV 匯出檔，不會默默跳過任何一步。

## 工作流程

照順序做這些步驟。每個步驟都有完成狀態；目前這一步沒處理完就不要往下走。

### 步驟 1：確認目標月份

問使用者要結哪個月。沒指定的話，預設是上一個曆月。拉任何資料之前先確認。

### 步驟 2：拉帳本的 P&L 和明細登記簿（register）

抓取：
- 目標月份的損益表（營收、COGS、毛利、營業費用、淨利）
- 登記簿，依帳本的 reference 檔定義的範圍。QuickBooks：交易清單，每一筆收入和支出明細。Xero：帳單、發票和銀行交易待處理佇列，範圍要寫在結帳包裡。Zoho Books：發票、費用和採購單，P&L 本身要靠匯出檔，因為這個 connector 沒有報表 endpoint。

用帳本自己的「需要處理」訊號，立刻標出：
- **QuickBooks**：未分類的項目（「Uncategorized」、空白、「Ask My Accountant」）和它的 Needs Review 旗標
- **Xero**：月底仍未對帳的銀行明細
- **Zoho Books**：每個銀行帳戶上的 `uncategorized_transactions` 數量

呈現數量（「14 transactions need attention」），並列出來，讓使用者在帳本裡處理完再繼續。除非使用者明確說「skip for now」，否則有未處理項目就不要往下走。

欄位對應和 API 注意事項請見 [reference/quickbooks-reconcile.md](reference/quickbooks-reconcile.md)、
[reference/xero-reconcile.md](reference/xero-reconcile.md) 和
[reference/zoho-books-reconcile.md](reference/zoho-books-reconcile.md)。

### 步驟 3：拉支付處理商的撥款結算

從 PayPal、Square、Stripe 或 Shopify（連了哪個就用哪個）抓取同一個曆月的結算報表。

**先檢查銀行 feed。** 當處理商是透過銀行 feed 撥款時，這筆撥款已經是帳本裡的一行，問題只在於它有沒有被配對。在做任何 CSV 比對之前，先找出提到某個處理商的未對帳銀行明細，依處理商列出來當作待辦項目。這適用於任何帶有銀行 feed、且有已對帳狀態的帳本，Xero 通常是這樣，QuickBooks 的銀行 feed 明細則要看 connector 有沒有開放。MYOB 沒有銀行端資料，Zoho Books 只開放餘額、沒有銀行交易清單，所以 MYOB 或 Zoho Books 的結帳會直接進入下面的 CSV 比對。

**要拿淨額對淨額，否則每一行看起來都壞掉。** 帳本記錄的是淨銀行入帳；處理商的報表顯示的是銷售毛額。直接拿這兩個比，每一列都會出現剛好等於手續費的差額。要用處理商的**淨撥款額**（毛額扣掉手續費），請見 [reference/gotchas.md](reference/gotchas.md)。

把每筆結算入帳跟帳本的銀行入帳明細做配對：
- **相符**：金額和日期在 2 天內一致 → 標為已對帳
- **差額 < 0.50**：四捨五入或手續費；記下來但不標記
- **差額 ≥ 0.50**：標記，並附上差額
- **有結算、帳本沒有入帳**：標記為「missing in the ledger」
- **帳本有入帳、沒有結算**：標記為「deposit not in processor data」

結算報表的欄位對應（PayPal、Square、Stripe）請見
[reference/paypal-settlements.md](reference/paypal-settlements.md)，Shopify 請見
[reference/v2_sources.md](reference/v2_sources.md)。

### 步驟 4：偵測可疑的重複項目

掃描登記簿，找出可能重複的扣款或入帳。**三項全部**符合時，把交易標為可疑重複：
- 金額相同（誤差 0.01 以內）
- 廠商或客戶名稱相同
- 入帳日期彼此相差 5 個曆日以內

掃描帳本實際存放的東西。在 QuickBooks 是交易清單，先依交易 id 把拆分列歸在一起。在 Xero，同一張帳單鍵入兩次會產生兩張未付款文件、沒有銀行明細，所以要掃帳單和發票（同一個聯絡人、同樣總額、5 天內，兩張都未付款，或其中一張在該區間內已付款），不是掃銀行明細，對應方式在 [reference/xero-reconcile.md](reference/xero-reconcile.md)。Zoho Books 是同樣的形態：把發票和費用當文件來掃（[reference/zoho-books-reconcile.md](reference/zoho-books-reconcile.md)）。

把被標記的配對呈現給使用者。由他們判斷每一組是合理的（例如每週的定期訂閱），還是需要作廢的真正重複。

**5 天的視窗是過濾條件，不是保證。** 它能抓到同一筆被鍵入兩次的款項，又不會被每週定期帳單淹沒，但相隔三週的真正重複付款會漏掉。要說明掃了什麼（「repeats within 5 days」），而且對他們懷疑的廠商要放寬視窗，不要直接說帳是乾淨的。

常見的誤判樣態以及怎麼區分，請見 [reference/gotchas.md](reference/gotchas.md)。

### 步驟 5：檢查收據

先查帳本：交易上有附件就算有收據存檔（QuickBooks 的 `AttachmentCount`；Xero 的 `has_attachments`，只有在 `include_line_items=true` 時才會回傳；Zoho Books 發票和費用上的 `has_attachment`）。然後，如果有 Desktop connector，就掃描收據資料夾（路徑問使用者；預設 `~/Documents/Receipts`）中目標月份的檔案。

針對每一筆超過 25 且沒有附件的費用交易：
- 找有沒有符合的收據檔（依金額 ± 0.50 且日期在 3 天內比對）
- **有配到** → 記為「receipt on file」
- **沒配到** → 標記為「missing receipt」

列出缺少的收據。使用者可以提供檔案，或標記為「receipt not required」（例如沒有收據的定期自動扣款）。

如果沒有 Desktop connector，就請使用者確認哪些費用有收據，不要默默跳過這一步。

### 步驟 5a：薪資交叉檢查

只有在連了薪資 connector（Gusto 或 QuickBooks Payroll，兩者地位平等，連了哪個用哪個）時才執行。否則跳過，並說明結帳包沒有薪資欄。

拉出當月實際付出的金額，只要總額：

- **Gusto**：用 `include=totals` 呼叫 `list_payrolls`，保留 `check_date` 落在目標月份的薪資批次。從每個 `totals` 取 `gross_pay`、`employer_taxes`、`employee_taxes`、`net_pay`。接著對同一個日期範圍呼叫 `list_contractor_payments`，帶 `group_by_date=true`，取 `total.wages` 和 `total.reimbursements`。外包人員的總額只涵蓋美國外包人員，要在結帳包的註腳裡說明。
- **QuickBooks Payroll**：用 `qbo_payroll_get_company_last_payroll_run` 取最近一次發薪；當月更早的發薪批次要從薪資摘要匯出檔取得。
  （第一次結帳前先確認。）

跟帳本交叉檢查：實發薪資加雇主稅加外包人員薪資，應該會出現在當月的薪資費用明細裡。差額超過 0.50 就是一個對帳項目，通常是某次發薪記到錯的月份，或薪資傳票還沒入帳。

**只看總額，絕對不看個人。** 結帳包只放當月總額和發薪次數。任何員工姓名、費率或個人金額都不准離開 connector，那是薪資資料，該放的地方是 `payroll-prep`。欄位對應請見 [reference/v2_sources.md](reference/v2_sources.md)。

### 步驟 6：老闆簽核關卡

往下之前先呈現摘要：

```
Needs attention (uncategorized or unreconciled):  X of X resolved
Settlement discrepancies:                        X flagged, X resolved
Suspicious duplicates:                           X flagged, X cleared
Missing receipts:                                X outstanding
Payroll cross-check:                             matched / X difference / no payroll connector
```

問：「Ready to write the P&L summary and export the close packet?」

**沒有明確確認，絕對不准進入步驟 7 到 8。**

### 步驟 7：撰寫 P&L 說明

用白話寫一份這個月的摘要，就是老闆會拿給另一半或會計師看的那種，不是 CFO 備忘錄。目標 150 到 250 字。

結構：
1. **標題句**：一句話：「March came in at AUD 12,400 net, up 6% from February.」要用幣別代碼，絕對不要只放符號。
2. **營收**：是什麼推動了這個數字；如果資料顯示有集中現象，就點出產品、服務或客戶的名字。
3. **毛利**：是持平、上升還是被壓縮，以及主要原因。
4. **主要費用**：任何月增減超過 10% 或超出正常範圍的項目；每項一句話。
5. **底線**：淨利跟上個月比；問他們有沒有目標可以拿來比。
6. **觀察清單**：下個月要盯的 1 到 3 件事。

避免行話；任何不是白話的詞都要解釋（「MoM」= month over month，月對月）。

完整範例請見 [reference/examples/pl-narrative.md](reference/examples/pl-narrative.md)。

### 步驟 8：匯出結帳包

產出兩個檔案：

**`close-packet-[YYYY-MM].xlsx`**：三個工作表，連了薪資 connector 時是四個：
- `P&L`：帳本的 P&L 資料，已排版
- `Reconciliation`：已配對和被標記的交易並排呈現
- `Action Items`：任何尚未處理的標記（未分類、缺收據等）
- `Payroll`：步驟 5a 的總額，放在帳本薪資費用旁邊，附差額

**`close-packet-[YYYY-MM]-summary.pdf`**：一頁：
- 最上面是月份和企業名稱
- 關鍵數字（營收、毛利率 %、淨利）
- 步驟 7 的 P&L 說明
- 未處理待辦項目的數量（如果有的話）

兩個檔案都存到 Desktop（或使用者指定的路徑）。確認檔案位置。

欄位規格和 PDF 版面細節請見 [reference/close-packet-format.md](reference/close-packet-format.md)。

另外也要依老闆儲存的輸出偏好，把結帳結果做成一個頁面交付，絕對不要預設產出 markdown 檔。檢查 `## Business context` 區塊裡的 `Output preference`（共用風格指南規則，`../../shared/artifact-style.md`）：

- **視覺化 artifact（預設）：** 用 house style 把結帳結果渲染成 HTML 頁面，是附加在聊天摘要和檔案之外的，絕對不是取代它們。營收、毛利率百分比和淨利做成數字卡片（stat tile），月對月變化放在脈絡行；對帳結果是一張表，金額用 tabular-nums；每個標記帶一個狀態標籤，已對帳用 good，缺收據和未分類項目用 warn，未解決的結算缺口和重複項目用 critical；P&L 說明和未完成項目檢查清單各自放進一個面板。
- **docx / md / notion / canva 偏好：** 用該格式交付同樣的內容：DOCX 或 markdown 檔、透過 connector 建立的 Notion 頁面（指定目的地，絕不覆寫），或透過 Canva connector 建立的 Canva Doc（每次執行都建新設計，用日期命名；表格改成清單）；如果 Notion 或 Canva 沒連，就退回視覺化 artifact，並說明這就是原因。結帳包的 xlsx 和 PDF 維持原本格式。
- **Best for skill：** 用視覺化 artifact，因為結帳結果在送給會計師之前，要先在螢幕上檢視。

### 步驟 9：結帳之後

用一行說明什麼已經結掉、什麼還沒結。然後提議最相關的一個下一步，附近再加最多兩個：

- 「Cash forecast」會用剛結好的數字執行 `cash-flow-snapshot`。
- 「Build me a report」會執行 `report-builder` 來發佈並發送結帳包。
- 「Taxes」在季末或年底接近時執行 `/tax-prep`，只有在企業背景說 Country 是 US 時才提議，因為那條串接的稅務計算是美國聯邦稅。

最多三個提議。這個 session 裡老闆拒絕過的提議，絕對不要再提。

## 核准關卡

- **絕對不要對已經申報過的月份執行對帳。** 拉資料之前，先確認帳還是開著的。
- **絕對不要直接作廢或修改帳本交易。** 只呈現標記；由老闆自己在帳本裡修改。
- **產出任何結果之前，一定要在步驟 6 暫停。** 未解決的標記必須被確認，或被明確跳過。
- **絕對不要在結帳包裡重現個人薪資、SSN 或銀行帳號**，傳票總額以外都不行（`../../shared/personal-data.md`）。

## 優雅降級

| 缺少的 connector | 替代做法 |
|---|---|
| QuickBooks | 請對方提供**兩份各自獨立的匯出檔**：損益表（Profit & Loss report），以及 Transaction Detail by Account 報表。一份檔案放不下兩者；只說「一份 QB 匯出檔」只會拿到其中一個，還要多來回一趟 |
| Xero | 請對方提供**兩份匯出檔**：損益表（Profit and Loss report），以及選取所有帳戶的 Account Transactions 報表，再加上銀行對帳畫面上的未對帳明細數量，因為沒有任何匯出檔會帶這個數字 |
| NetSuite 或 MYOB | 請對方把當月的 P&L 和交易明細分成兩份匯出檔提供；MYOB 沒有銀行餘額，所以銀行端要靠對帳單 |
| Zoho Books | 即使已連接，也要請對方提供 **Profit and Loss** 匯出檔（沒有報表 endpoint）和**銀行對帳單**（沒有銀行交易 feed）；登記簿和未分類數量則從 connector 取得。沒連接時：再加上 Account Transactions 匯出檔 |
| 支付處理商 | 請對方從處理商網站下載結算 CSV。必須包含手續費欄位，不能只有毛額，否則步驟 3 的淨額對淨額比對就做不了 |
| 支付處理商已連接但該期間回傳零筆撥款 | 當作資料缺口，不要當成乾淨的零。要說明 connector 這個月什麼都沒回傳，請對方提供同樣的結算 CSV（含手續費欄位），並在報告中點名這個缺口，不要拿空集合去對帳 |
| 薪資 connector（Gusto、QuickBooks Payroll） | 跳過步驟 5a。結帳包沒有 Payroll 工作表，摘要寫「no payroll connector」；帳本的薪資費用明細仍會出現在 P&L 裡，但沒有被檢查 |
| Desktop（收據） | 請使用者逐一確認每筆被標記費用的收據狀態 |

## 更多來源

請閱讀 `reference/v2_sources.md` 取得對應方式：

- **Shopify**：把結算對帳當作一等公民的環節。訂單、撥款和手續費各自的入帳方式不同，是許多說不清楚的缺口的常見來源
- **NetSuite**：正式帳本，常見於這個客群中偏大的企業；報表和 SuiteQL 提供 P&L 和登記簿
- **Xero**：正式帳本，有自己的登記簿形態（帳單、發票、銀行佇列）和自己的注意訊號（未對帳銀行明細）；對應方式寫在 `reference/xero-reconcile.md`
- **MYOB**：P&L 和應收／應付餘額；沒有銀行餘額，所以結帳的銀行端要靠對帳單
- **Zoho Books**：正式帳本，有文件式登記簿（發票、費用、採購單）、帶有未分類數量作為注意訊號的銀行餘額，而且沒有報表或銀行 feed 的 endpoint，所以 P&L 和撥款比對要靠匯出檔；對應方式寫在 `reference/zoho-books-reconcile.md`
- **Ramp、Expensify**：信用卡和費用明細，補上「花了多少」和「記了哪個科目」之間的缺口
- **Gusto、QuickBooks Payroll**：實際發出的薪資：以月總額呈現毛薪、雇主稅、實發薪資和外包人員付款，讓步驟 5a 拿帳本的薪資費用跟實際付出的金額對帳，而不是跟計畫的金額對帳。只有總額；任何個人資料都不會進入結帳包

同樣的結帳順序，同樣的結帳包。只是對帳的來源更多。

**QuickBooks 的摘要欄位會騙人。** 引用任何 QuickBooks 摘要物件的總額之前，先讀 `../../shared/quickbooks-report-traps.md`：應付帳款帳齡摘要會把廠商信用額度淨額計入各個區間，可能顯示負的逾期金額，而 P&L 摘要可能在實際有明細列的情況下把費用報成零。要自己加總明細列，或改用明細呼叫。

## Reference 檔案

- [reference/quickbooks-reconcile.md](reference/quickbooks-reconcile.md)：QB 欄位對應、API 分頁、常見資料問題
- [reference/xero-reconcile.md](reference/xero-reconcile.md)：Xero 登記簿定義、未對帳明細訊號、文件層級的重複掃描、附件
- [reference/zoho-books-reconcile.md](reference/zoho-books-reconcile.md)：Zoho Books 登記簿定義、未分類數量訊號、哪些需要匯出檔
- [reference/paypal-settlements.md](reference/paypal-settlements.md)：PayPal、Square 和 Stripe 的結算報表結構
- [reference/close-packet-format.md](reference/close-packet-format.md)：xlsx 欄位規格、PDF 版面、檔案命名慣例
- [reference/gotchas.md](reference/gotchas.md)：重複項目的誤判、拆分交易、非整月的邊界情況
- [reference/examples/pl-narrative.md](reference/examples/pl-narrative.md)：P&L 說明的實際範例

## 使用沒列出來的工具

這個 skill 裡提到的 connector 是測試過的路徑，不是一道牆。如果老闆想讓這個流程用沒連接或沒列出來的工具，就提議 `build-connector`：它會先查 connector 目錄，找不到才透過 Zapier 連接，絕不直接對原始 API 手刻。連線建立之後，這個工具就像任何其他選用的 connector 一樣加入這個 skill，並遵守同樣的核准關卡。
