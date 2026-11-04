---
name: tax-season-organizer
description: >
  為老闆的會計師準備報稅季的資料，不是稅務建議。
  採美國聯邦稅制；非美國企業改拿結清帳務的資料包。有兩種模式：
  (1) 根據總帳（MYOB、NetSuite、QuickBooks、Xero 或 Zoho Books）的 YTD 淨利，
  計算季度預估稅款；(2) 年底 1099 準備，掃描總帳、PayPal 和 Stripe，
  找出付款超過 USD 600 的承包商，整理成 1099-NEC 名單並標出缺 W-9 的人。

  任何稅務請求都會先導向 /tax-prep，由它確認帳已經結清、對帳完畢，
  再跑這個 skill。只有在老闆說該期間的帳已經結清時，才直接使用這個 skill：
  「books are closed, now do the 1099s」、「run the quarterly estimate off the closed
  numbers」，或「just the contractor W-9 list」。
allowed-tools: Read, WebFetch
---

# 報稅季整理（Tax Season Organizer）

> **框架：** 這個 skill 產出的是給 CPA 的準備資料，不是稅務建議。要早點說明這點，
> 並明確寫出每一個假設，讓會計師可以調整。

## 快速開始

判斷使用者需要哪一種模式，拉出相關資料，計算或彙整，然後交付一份會計師可以直接拿去用的結構化文件。

```
User: "what do I owe for estimated taxes this quarter?"
→ Pull YTD P&L from QuickBooks
→ Calculate estimated federal income tax + SE tax
→ Subtract payments already made this year
→ Show Q-specific amount due with due date and assumptions stated
→ Output: "Estimated Q2 payment due June 16: USD X — see full breakdown below"

User: "I need to send out 1099s"
→ Pull all contractor/vendor payments from QuickBooks + PayPal + Stripe
→ Identify contractors paid ≥ USD 600 YTD
→ Flag records missing W-9 / EIN
→ Output: 1099-NEC candidate list + missing W-9 action list
```

## Step 0：先檢查國家

下面兩條路徑都是**美國聯邦稅制**：自僱稅（self-employment tax）、聯邦稅率級距表、1099-NEC 和 W-9。選擇模式之前，先從 `## Business context` 區塊讀 `Country`（規則：`../../shared/currency-and-locale.md`）。如果沒有，就問。

- **美國** → 繼續做「判斷模式」。
- **其他任何國家** → 用一句話說明並停止美國的計算：*「這裡的季度預估和 1099 路徑是為美國聯邦稅制設計的。你的帳在英國，所以我會改幫你準備給會計師的結清帳務資料包，而不是美國的預估稅款。」* 然後針對範圍內的期間提議 `/close-month`。不要對非美國企業跑美國的計算，也不要把它改貼成泛用的估算。

輸出裡的每個金額都用企業的幣別代碼；USD 600 那條線是美國法律，要標明這點。

## 判斷模式

讀使用者的訊息和背景，判斷適用哪條路徑：

- **季度預估**：關鍵字：estimated payment、quarterly taxes、how much to set aside、safe harbor、Q1/Q2/Q3/Q4
- **年底 1099 準備**：關鍵字：1099、1099-NEC、year-end、contractors、W-9、send 1099s、file 1099s
- **合併**：有些使用者會問「year-end summary」，兩個都需要。季度預估最後做；先做 1099 準備，因為它帶出最多的待辦事項。

如果意圖不明確，就問：「你是要看這一季的預估稅款，還是在幫承包商準備 1099，還是兩個都要？」

---

## 路徑 1：季度預估稅款

### 1. 拉 YTD 財務資料

用連上的總帳（MYOB、NetSuite、QuickBooks、Xero 或 Zoho Books，它們是平等的，依 `../../shared/connector-neutrality.md`）拉一份損益表（Profit & Loss），範圍從今年 1 月 1 日到最近一個完整季度的最後一天。擷取：
- **總營收**（總收入）
- **總費用**（營運費用、COGS 等）
- **一般淨收入** = 營收 − 費用

如果沒有連總帳，就請使用者上傳 CSV 格式的損益表，或貼上關鍵數字。各總帳的欄位名稱和查詢方式，請看 [reference/connector-queries.md](reference/connector-queries.md)。

### 2. 詢問先前已付的預估稅款

計算之前先問：「今年到目前為止，你已經付了多少預估稅款？」如果使用者不知道，就註明你會計算總稅負，他們可以自己扣掉已付的款項，或跟會計師確認。

### 3. 計算預估稅負

完整的算式，以及輸出中必須包含的假設表，請看 [reference/calculation-assumptions.md](reference/calculation-assumptions.md)。

**先做年化。** 計算是以預計的全年淨利為基礎，不是 YTD：
`年化淨利 = YTD 淨利 ÷ 已過月數 × 12`。兩個都要顯示，並標上標籤。季節性的企業：要去問，不要直接線性推估。

簡短版，六個步驟全都以**年化**淨利來跑：
1. **自僱稅（SE tax）** = 年化淨利 × 0.9235 × 0.153（然後取一半，可扣除的那一半用來抵減收入）
2. **調整後淨利** = 年化淨利 − (SE tax / 2)
3. **聯邦所得稅** = 套用適合使用者企業型態和預估年收入的稅率級距（預設為 22%，除非使用者告訴你他們的級距；要明確註明這個假設）
4. **全年總稅負** = 聯邦所得稅 + SE tax
5. **每季付款** = （全年總稅負 − 已付款項）÷ 還剩的季數
6. **Safe harbor 檢查**：註明使用者是否應該對照前一年的稅額驗證（前一年的 100%，或 AGI 超過 USD 150k 時為 110%）

**如果有到期日已經過了還沒付**，要點名，並把補繳的金額獨立列成一行，跟下一次付款分開。罰款和利息交給會計師，要標出它們會適用，絕不估算。如果沒有剩下的季度，就是隨申報書一起繳。

### 4. 說明假設並交付輸出

逐段的完整文件結構在 [reference/output-formats.md](reference/output-formats.md)。

有兩件事沒有商量的餘地：**標題裡要出現稅務年度**，以及 **Assumptions 區段列出每一個假設**：稅率級距、企業結構、排除的州稅、可扣除的 SE 一半，以及沒有套用的扣除額。會計師就是從這些槓桿去調整的，少列一個就害他們得重做一次。

---

## 路徑 2：年底 1099 準備

### 1. 從所有來源拉承包商付款

查詢每一個連上的來源，找出稅務年度中**為服務而付給個人或企業的所有款項**。不要包含為商品而付的款項、退款或內部轉帳。

**總帳：先試即時的 connector，再退回 CSV 匯出。** QuickBooks 可能只回傳類別層級的合計，沒有 payee 明細，這時你需要使用者匯出依廠商分類的 Transaction List。Xero 提供依聯絡人的帳單和付款，以及美國組織的 1099 報表摘要。偵測邏輯、要問的確切措辭，以及每個總帳的欄位對應，都在 [reference/connector-queries.md](reference/connector-queries.md)。

**PayPal：** 拉所有送出的「Goods & Services」付款。注意：PayPal 會對超過門檻的承包商自己開 1099-K，要在輸出裡把這些獨立標出來，讓會計師判斷是否還需要 1099-NEC。

**Stripe：** 拉所有轉給外部對象的轉帳／撥款。適用跟 PayPal 一樣的 1099-K 但書。

**Square：** 透過 connector 沒有任何付給外部對象的款項（撥款是進老闆自己的銀行；承包商薪資在 Square Payroll，而它碰不到）。要把它列為沒有東西可提供的來源，不要默默漏掉；1099-K 的提醒適用於企業自己的收款。細節在 [reference/connector-queries.md](reference/connector-queries.md)。

**桌面版／CSV：** 如果使用者直接上傳 CSV（沒有經過 QuickBooks 匯出），要對應欄位：payee 名稱、金額、日期、付款方式、EIN/SSN 狀態。

### 2. 依 payee 彙總

跨來源合併，並依個人或企業實體加總付款。依名稱去除重複（注意「John Smith」和「John A. Smith」，把可能的重複標記出來交給人檢視，不要自動合併）。

### 3. 套用 USD 600 門檻

- **標記為 1099-NEC：** 任何因服務（承包商、自由工作者、顧問）而被付款 ≥ USD 600 的 payee
- **標記為 1099-MISC：** 任何因租金、律師費、獎項／獎金而被付款 ≥ USD 600 的 payee
- **接近門檻的警示：** 標出被付款 USD 400 到 USD 599 的 payee，接近門檻，會計師可能想驗證

公司（Inc.、Corp.，以及被課徵為 C 或 S corp 的 LLC）通常不需要 1099-NEC，要註明這點，但仍要標記讓會計師確認。

### 4. 檢查 W-9 狀態

針對每個被標記的 payee，註明總帳裡是否有 W-9 / EIN 的紀錄。標記為：
- ✅ 已有 W-9（EIN/SSN 記錄在總帳的廠商或聯絡人紀錄中）
- ⚠️ 缺少：沒有 W-9；申報前必須收齊
- ❓ 未知：無法從現有資料判斷

### 5. 交付 1099 準備資料包

逐段的完整結構在 [reference/output-formats.md](reference/output-formats.md)。

最重要的部分：**缺 W-9 的待辦清單**，因為這些會擋住申報，而期限是 1 月 31 日；以及**支付處理商備註**，因為只透過 PayPal 或 Stripe 付款的承包商，可能已經收到 1099-K 了，會計師得決定是否還需要 1099-NEC。

---

## 護欄

- **每份輸出都要寫明稅務年度。** [reference/calculation-assumptions.md](reference/calculation-assumptions.md) 裡的稅率級距、工資基數和到期日是 **2025 年的數字**。準備的是不同年度：在顯示任何數字之前，先大聲說出來，然後引用 IRS.gov 上目前的數字，或問老闆。**絕不編造稅率級距、工資基數或到期日。**
- **不是稅務建議。** 每份交付物的開頭都要寫：「Prepared for review by your accountant — not tax advice.」要放在文件標題裡，不是只放在聊天中。
- **說明每一個假設。** 如果你假設了 22% 的級距，就說出來。如果你排除了州稅，就說出來。會計師會調整；把槓桿給他們。
- **不要自動合併 payee。** 把可能的重複標記出來給人檢視。
- **不要申報任何東西。** 輸出是準備資料。申報不在範圍內。
- **公司豁免是需要判斷的事。** 註明它；不要自動排除。
- **絕不要在資料包、聊天或渲染的頁面中重現承包商的 SSN，或完整的銀行或卡號。** 1099 上的企業 EIN 是唯一設計好的例外（`../../shared/personal-data.md`）。

## 更多來源

- **Gusto**：實際跑過的薪資：工資、扣繳款和承包商付款。這會讓兩種模式都更深入：季度預估不再用猜的薪資數字，1099 準備也能把承包商付款跟 Gusto 已經申報的內容對帳。當 Gusto 顯示某個 payee 已經開過 1099，就標記出來，不要重複準備。
- **Xero**：季度路徑用的損益表；做 payee 名單用的依聯絡人帳單和付款；對美國組織來說，還有 1099 報表摘要，一次讀取就是路徑 2 預期的輸出。查詢寫在 `reference/connector-queries.md`。
- **Ramp、Expensify**：卡片消費和支出明細，用在季度預估的扣除額那一側，以及能幫忙確認 1099 名單完整的廠商付款明細。Expensify 的收據篩選會找出經不起佐證的支出，那正是會計師在申報前最想要的標記。
- **MYOB**：只有損益表，給用 MYOB 的店家。唯讀、三個財務年度的歷史，**而且沒有承包商或廠商 payee 明細**，所以它供應季度預估，在 1099 準備中沒有任何作用。

同樣的稅額計算、同樣的會計師資料包。來源越多，需要說明的假設越少。

## 輸出

**依老闆儲存的輸出偏好交付預估稅款或 1099 資料包，絕對不要預設產出 markdown 檔。** 檢查 `## Business context` 區塊裡的 `Output preference`（共用的風格指南規則，`../../shared/artifact-style.md`）：

- **Visual artifact（預設）：** 用 house 風格把摘要渲染成 HTML 頁面：預估稅款或 1099 數量當主要的數字卡、假設表、缺 W-9 的人各自成列並附一個標籤，期限放在最上面。開頭放 not-tax-advice 那句。會計師文件本身維持 `reference/output-formats.md` 裡的結構。
- **docx / md / notion / canva 偏好：** 用該格式交付同樣的內容：DOCX 或 markdown 檔、透過 connector 建立的 Notion 頁面（要有指定的目的地，絕不覆寫既有頁面），或透過 Canva connector 建立的 Canva Doc（每次執行都建新設計、用日期命名，表格改成清單）。如果 Notion 或 Canva 沒連上，就退回 visual artifact，並說明是因為這個原因。
- **Best for skill：** 用 visual artifact，因為這份輸出是一個蓋在要交給會計師的文件之上的狀態頁。

## 資料包之後

預估稅款或 1099 資料包已經在會計師手上，假設都已說明。自然的下一步是「close the month」，`/close-month` 讓下一次預估繼續建立在對完帳的數字上，而不是原始的 register。另外相關的還有：「cash forecast」（`cash-flow-snapshot`），確認付款在到期日付得出來；以及「who owes me money」（`invoice-chase`），如果需要靠催收來支應。最多提三個，這次對話裡老闆已經拒絕過的就跳過。

## 參考檔案

- [reference/calculation-assumptions.md](reference/calculation-assumptions.md)：完整的稅額算式、2025 年稅率級距表、SE tax 逐步說明、YTD 對年化、漏繳的季度
- [reference/output-formats.md](reference/output-formats.md)：季度摘要和 1099 資料包兩者的文件結構
- [reference/connector-queries.md](reference/connector-queries.md)：如何從每個總帳（MYOB、NetSuite、QuickBooks、Xero、Zoho Books）、PayPal、Square 和 Stripe 拉資料，包含廠商層級的備案
- [reference/gotchas.md](reference/gotchas.md)：常見失敗模式的好／壞做法
- [reference/examples/quarterly-estimate.md](reference/examples/quarterly-estimate.md)：季度預估的實作範例
- [reference/examples/year-end-1099.md](reference/examples/year-end-1099.md)：年底 1099 準備的實作範例

## 使用沒列出來的工具

這個 skill 裡提到的 connector 是測試過的路徑，不是硬性限制。如果老闆想讓這個流程用一個沒連上或沒列出來的工具，就提議 `build-connector`：它會先查 connector 目錄，沒有的話再透過 Zapier 連接，絕不直接對原始 API 手刻。連線建好之後，這個工具就跟其他選用的 connector 一樣加入這個 skill，並遵守同樣的核准關卡。
