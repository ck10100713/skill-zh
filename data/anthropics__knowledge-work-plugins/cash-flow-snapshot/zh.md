---
name: cash-flow-snapshot
description: >
  從帳務系統（MYOB、NetSuite、QuickBooks、Xero 或 Zoho Books）、PayPal、Square、Stripe，或上傳的 CSV
  讀取應收/應付帳款、歷史收款時間和已知的固定成本，產出 30/60/90 天的現金流預測，
  附上以百分比變異表示的信心區間和點名的風險標記。交付聊天摘要和可下載的 XLSX。
  當使用者問「forecast my cash flow」「will I make payroll」，提到「runway」或說「cash crunch」時使用。
  沒有可用的 connector 時，退回 CSV 上傳。
compatibility: "Requires one or more of: a ledger MCP (MYOB, NetSuite, QuickBooks, Xero, Zoho Books), PayPal MCP, Shopify MCP, Square MCP, Stripe MCP, file upload (CSV fallback). Output uses xlsx skill."
allowed-tools: Read, WebFetch
---

# Cash Flow Snapshot

產出 30/60/90 天的現金流預測，附上以百分比變異表示的信心區間和點名的風險標記。
交付兩部分的輸出：精簡的聊天摘要，和可下載的 XLSX 活頁簿。

**快速開始**

> 「Will I make payroll next month?」

Claude 從已連線的來源拉出目前的銀行餘額、應收/應付帳款和固定成本，
計算 30、60 和 90 天各個區間的預期流入與流出，依每個客戶的付款變異套用信心區間，
並用名字標出具體的風險。

---

## 工作流程

### Step 1 — 確認可用的資料來源

檢查哪些 connector 有連線。有連線的每一個都要拉，一批送出：

1. 帳務系統：MYOB、NetSuite、QuickBooks、Xero 或 Zoho Books，連了哪個就用哪個，用來取得 AR aging、AP、固定成本和現金餘額。帳務系統之間是平等的（`../../shared/connector-neutrality.md`）；如果連了兩個，就問哪一個是記錄來源，總額只取那一個的
2. PayPal：交易紀錄和撥款時間
3. Square：銷售和撥款紀錄
4. Stripe：收款和撥款紀錄
5. Shopify：用訂單（`list-orders`）當作流入，再加上撥款時間。單靠 Shopify 就足以執行：對電商業者來說它通常是最大的流入。撥款讀取可能會失敗，因為 connector 的權限範圍不包含 Shopify Payments；這時就向老闆要他們的撥款時程，並依此建模，絕對不要自己推測延遲天數（`reference/v2_sources.md`）
6. CSV 上傳：沒有任何 connector 連線時

如果沒有 connector 連線，也沒有附檔案，就請使用者連接一個來源，或上傳 CSV（收入/支出表格資料，任何合理的格式都可以）。
在輸出裡註明用了哪些來源，這會影響信心區間的寬度。

**一定要確立起始的現金餘額**：「will I make payroll」問的是餘額，不是淨額。
在 Step 2 拉出來，或問：「公司帳戶現在有多少錢？是哪一天的數字？」**絕對不要自己假設一個。**
如果沒人知道，就把輸出的標題寫成「no opening balance — net change only」，並把手上現金從風險標記裡拿掉。

### Step 2 — 拉資料

**從帳務系統：**
- 資產負債表：銀行和現金餘額，附上截止日期，這就是起始餘額
  （MYOB 完全沒有；見 `reference/v2_sources.md`）
- AR aging 報表：客戶名稱、發票金額、發票日期、到期日、逾期天數
- AP：廠商名稱、應付金額、到期日
- 週期性固定成本：房租、薪資、訂閱（找週期性交易）

**從 Gusto（有連線時）：**
- 下次發薪的日期和預期金額，以及固定的發薪週期，
  這是最大一筆固定成本的真實數字，不用再從週期性交易推測薪資。
  當 Gusto 和帳務系統在薪資上不一致時，時間和金額以 Gusto 為準，並在輸出裡說明

**從 PayPal / Stripe / Square：**
- 撥款紀錄：交易日期、金額、撥款日期
- 用撥款延遲（交易日期 → 撥款日期）計算每個來源的平均和變異付款延遲

**從 CSV 上傳：**
- 當作收入/支出的表格資料解析
- 必要欄位（名稱可彈性）：date、amount、type（income 或 expense）、description
- 如果欄位有歧義，就顯示標題列，請使用者確認對應

### Step 3 — 計算歷史付款時間

對每個 AR 客戶（或 CSV 裡的每個收入來源），計算：
- **平均付款延遲** — 從發票/交易日期到收款的平均天數
- **付款變異** — 最近 6 到 12 筆付款的付款延遲標準差
- 用變異來設定信心區間的寬度（見 Step 4）

如果某個客戶的付款少於 3 筆，就用整體平均作為點估計，並套用 ±30% 的變異區間作為預設。
當用 CSV 資料執行、而且歷史足夠（每個來源 ≥3 筆付款）時，要用實際的付款變異來計算區間，不要假設 ±30%。

### Step 4 — 建立 30/60/90 天預測

產出三個時間區間：0–30 天、31–60 天、61–90 天。

每個區間都要計算：

| 項目 | 方法 |
|---|---|
| 預期流入 | 在該區間到期的 AR，依平均付款延遲調整 |
| 預期流出 | 在該區間到期的 AP + 落在該區間的固定成本 |
| 淨現金部位 | 流入 − 流出 |
| 信心區間 | ± 加權平均付款變異，以預期流入的百分比表示 |

信心區間公式：
```
band_pct = weighted_avg_stddev_days / avg_payment_lag_days
low  = net_cash × (1 − band_pct)
high = net_cash × (1 + band_pct)
```

把 band_pct 四捨五入到小數點後一位。上限 ±50%：變異再高，代表資料太少、沒辦法建模，要改成標記出來（見 Step 5）。

### Step 5 — 標出點名的風險

掃描會讓低區間估計變成負數，或造成資金周轉壓力的狀況。每找到一個風險，就產出一行標記：

- **客戶遲付風險：**「客戶 X 歷來都晚 18 天付款；這會把他們 USD 8,400 的發票從 30 天區間推到第 48 天。」
- **發薪壓力：**「薪資（USD 22,000）在 4 月 15 日發放。4 月 1 日的起始餘額 USD 31,000，
  加上流入、減去流出，4 月 14 日的低區間手上現金是 USD 19,200。缺口風險：USD 2,800。」需要有來源的餘額。
- **資料太少警告：**「客戶 Y 只有 2 筆付款紀錄，信心區間設成預設的 ±30%。」
- **沒有 connector 的警告：**「只用 CSV 資料執行，沒有即時的 AP 或週期性成本資料。信心區間比平常寬。」

依嚴重程度只留前 5 個風險（金額影響最大的優先）。

### Step 6 — 交付輸出

**聊天摘要**（一定要有）。預測用 markdown 表格，不要用 fenced code block，
聊天介面會渲染 markdown 表格；fenced block 會顯示成原始的等寬文字。格式：

- 標題行：Cash Flow Snapshot — <日期範圍>
- 來源：<用到的 connector>
- 起始餘額：AUD X,XXX（截至 <日期>）（或：none on file — net change only）

接著把預測做成 markdown 表格，金額要帶公司的幣別代碼
（`../../shared/currency-and-locale.md`），絕對不要只用符號：

| Window | Expected | Low | High |
|---|---|---|---|
| 30-day net | AUD X,XXX | AUD X,XXX | AUD X,XXX |
| 60-day net | AUD X,XXX | AUD X,XXX | AUD X,XXX |
| 90-day net | AUD X,XXX | AUD X,XXX | AUD X,XXX |

然後把風險列成簡短的項目清單，放在「⚠ Risks flagged: <數量>」底下。

**XLSX 活頁簿**（一定要有）：先讀 `xlsx/SKILL.md`，然後產出三個工作表：

1. **Summary** — 30/60/90 預測表，附信心區間。在每個區間那一列的下面，展開內嵌的子列，
   顯示組成它流入（綠色）和流出（紅色）的各筆交易。這樣不用離開 Summary 工作表，就能稽核估算。

2. **Detail** — 所有交易依區間分組，每組內依日期排序。包含一個累計淨額欄（該區間內累計的流入減流出），
   以及每個區間底部的小計列，顯示總流入、總流出和淨額。過去的交易用灰色顯示，放在底部另開一個區塊供參考。
   確保三個區間都有列，就算其中一個是空的，也要顯示一列「No transactions in this window」佔位列。

3. **Risks** — 被標記的風險，附上金額影響和受影響的區間。

存成 `cash-flow-snapshot-[YYYY-MM-DD].xlsx`。

**預測頁面**（一定要有，跟聊天摘要並行，絕對不是取代它），
依老闆存下來的輸出偏好交付，絕對不要預設用 markdown 檔。
檢查 `## Business context` 區塊的 `Output preference`（共用的風格指南規則，`../../shared/artifact-style.md`）：

- **視覺化 artifact（預設）：** 用 house style 把完整預測渲染成 HTML 頁面。
  30/60/90 天的淨額做成數字卡，信心範圍放在每張卡的輔助說明行；
  交易明細是表格，金額靠右對齊並用 tabular-nums；
  每個風險標記帶一個狀態標籤：預計出現缺口的用 critical，客戶遲付和資料太少的標記用 warn；
  來源和起始餘額放在一個小的標頭面板。
- **docx / md / notion / canva 偏好：** 用該形式交付同樣的內容，
  可以是 DOCX 或 markdown 檔、透過 connector 建立的 Notion 頁面（要有指名的位置，絕對不覆蓋）、
  或透過 Canva connector 建立的 Canva Doc（每次執行都建新的設計，以日期命名；表格改成清單）；
  如果 Notion 或 Canva 沒連線，就退回視覺化 artifact，並說明是因為這個原因。XLSX 仍然一併交付。
- **Best for skill：** 用視覺化 artifact，因為預測是一眼掃過、而且會常常重跑。

---

## 執行之後

用一行說明剛剛發生了什麼：預測建好了，風險也點名了。
然後給一個最相關的下一步，加上最多兩個相近的：

- 如果標出了發薪壓力：「can I make payroll」會執行 `/plan-payroll`。
- 「Who owes me money?」會執行 `invoice-chase`，把收款提前。
- 「Close the month」會執行 `/close-month`，讓下一次預測用乾淨的帳來跑。

最多三個提議，這個 session 裡老闆拒絕過的提議絕對不要重複。

## 核准關卡

這個 skill 是唯讀的，產生預測之前不需要核准關卡。

交付之後要提醒使用者：
> 「這份預測是依據 [列出的來源]。它不能取代會計建議，在做任何融資決定之前，請先跟你的記帳人員確認。」

---

## 更多來源，以及排程

完整的對照請讀 `reference/v2_sources.md`：

- **Shopify** — 付款流入的時間，對電商業者來說通常是最大的單一流入，而且撥款有延遲，值得建模
- **NetSuite** — 記錄用的帳務系統，常見於這個族群中規模較大的一端：透過報表和 SuiteQL 取得 AR、AP、固定成本和現金餘額
- **Xero** — 記錄用的帳務系統：應收帳款帳齡、帳單、銀行餘額，以及組織的幣別和會計年度
- **Ramp** — 還沒入帳的刷卡消費，這是預測默默偏樂觀最常見的原因
- **Ramp balances** — 真實的企業和資金帳戶餘額與歷史。當老闆在 Ramp 開戶時，這就是一個有來源的起始餘額，不用靠他們自己記
- **MYOB** — 給 MYOB 店家的 AR 和 AP 這兩段。唯讀，而且它**完全沒有銀行或現金餘額**，絕對不要從它取得起始餘額

預測的邏輯完全不變。這些只是進入同一個模型的額外來源。

### 排程執行

這個 skill 可以排程。每月的預設是月底前的現金預警。

在老闆覺得有用的預測之後，提議一次：

```
想要每個月、在月底前幾天自動跑嗎？那時候最有用，
而且跟你剛剛拿到的是同一份預測。
```

排程是這個 skill 的屬性。沒有另外的指令。

**QuickBooks 的 summary 欄位會騙人。** 引用 QuickBooks summary 物件裡的任何總額之前，先讀 `../../shared/quickbooks-report-traps.md`：AP aging summary 會把廠商信用額度沖進各個區間，可能顯示出負的逾期金額，而 P&L summary 可能在有真實資料列的情況下把費用回報成零。要自己加總資料列，或使用明細呼叫。

## 參考檔案

| 檔案 | 何時載入 |
|---|---|
| `reference/gotchas.md` | connector 回傳非預期資料，或變異極端時 |
| `reference/examples/worked-example.md` | 為新的資料形態設計輸出格式時 |

## 使用沒列出的工具

這個 skill 裡提到的 connector 是測試過的路徑，不是一道牆。如果老闆想讓這個流程用某個沒連線或沒列出的工具，就提議 `build-connector`，它會先查 connector 目錄，沒有的話再透過 Zapier 連接，絕對不手工對著原始 API 硬幹。連線建好之後，這個工具就像其他任何可選的 connector 一樣加入這個 skill，受同樣的核准關卡約束。
