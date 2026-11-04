---
name: report-builder
description: >
  把一段白話描述的週期性報表，變成真正可重複產出的報表：定義指標、從已連接的資料來源拉資料、交付聊天摘要加一份 XLSX 活頁簿，並把定義存起來，之後同一份報表可以隨時重跑或排程重跑。從「各據點銷售額對比去年」到應收帳款帳齡、人事成本佔營收百分比都能處理。沒有 connector 時，只靠上傳的 CSV 或 XLSX 也能完整運作。只要老闆要報表、dashboard、KPI 包、指標摘要或週期性數字就用這個，包括「can you track this every week」、「I need to see these numbers monthly」、「build me a report on」、「same report as last time」或「put together a KPI dashboard」這類說法。就算老闆只說了指標、沒提到「報表」兩個字，也要用。
allowed-tools: Read, WebFetch
---

# Report Builder

老闆只要描述一次報表。你負責建出來、跑出來，並且把定義存起來，之後再也不用重講一次。

老闆們現在是從三個 dashboard 手動撈數字，還要自己找出背後的故事。這個 skill 的任務就是結束這種狀況。

## Step 1 — 檢查有沒有現成的定義

最先做的事：讀 `reference/saved_reports.md`，確認這份報表是不是已經存在。也要看工作目錄裡有沒有 `report-definitions.md`，skill 資料夾寫不進去時，定義會存到那裡（見 Step 7）。

如果老闆說「same report as last time」、「run the weekly one」，或點名了你已經有定義的報表，直接跳到 Step 4 執行。對已經定義過的報表再訪談一次，是讓這個 skill 顯得壞掉最快的方法。

如果沒有符合的，繼續往下。

## Step 2 — 把描述轉成 spec

老闆描述報表通常很鬆散：「every Monday, sales by location versus last year, AR aging, and labor percent」。這一句話裡有四個獨立的決定。用 `reference/report_spec.md` 的格式把它們整理成 spec：

- **Metrics（指標）**：每一個都要命名，附上公式和來源
- **Grouping（分組）**：依據點、產品、客戶、通路、業務
- **Comparison（比較）**：對比上一期、對比去年、對比目標
- **Period（期間）**：每次執行涵蓋的時間窗
- **Cadence（頻率）**：一次性、每週、每月、每季

合理能推斷的就推斷。「Sales by location vs last year」已經給了指標、分組和比較，這些不要再問。只問真正有歧義的地方，而且一次問完，不要一題一題問。

幾乎每次都值得問的兩個問題：

- 每次執行涵蓋哪個期間：日曆月、近 30 天，還是月初至今？
- 像「labor percent」這種數字，是對營收算，還是對總成本算？

這兩個答錯，會做出一份看起來對、實際上默默出錯的報表，那比多問一句更糟。

## Step 3 — 確認 spec，只確認一次

用精簡的區塊把整理好的 spec 秀給老闆看。要一次確認，然後就開始做。不要帶著老闆逐欄位走過 spec，他們只用一句話描述，期待的也是一句話的回答。

如果他們修正了什麼，套用後就繼續。不要再確認第二次。

## Step 4 — 拉資料

所有資料來源的呼叫，一次用平行批次送出。指標對應到工具的方式見 `reference/data_sources.md`。

來源，同時嘗試：

- **帳務系統**：MYOB、NetSuite、QuickBooks、Xero 或 Zoho Books，哪個有連就用哪個；彼此平等，依 `../../shared/connector-neutrality.md`。P&L 科目、營收、費用、應收帳款帳齡、應付帳款、class 與據點拆分。MYOB 只有 P&L、應收和應付，往回三個會計年度。如果連了兩套帳務系統，就問哪一套是正式帳，總數以那一套為準
- **HubSpot**：deal、階段、負責人、成交日期、pipeline 金額
- **PayPal、Square、Stripe**：結算、手續費、退款、交易明細
- **Shopify**：訂單、SKU 層級的營收、出貨狀態
- **Ramp、Expensify**：刷卡支出和費用明細。這裡兩者都只當讀取來源；Expensify 只能唯讀搜尋

如果某個來源出錯或沒回傳東西，記下來就繼續。絕對不要因為一個壞掉的 connector 卡住整份報表。

**完全沒有 connector 是被支援的路徑，不是失敗。** 請對方給 CSV 或 XLSX 匯出檔，讀進來，用檔案做出一模一樣的報表。要直說：「我沒看到已連接的資料來源。請從你的系統匯出銷售報表丟到這裡，我會用它做出同一份報表。」工具很分散的老闆就是活在這種模式裡，而這樣做出來的報表一樣好。

## Step 5 — 計算並做合理性檢查

把 spec 裡列出的每個指標都算出來。然後在秀出結果之前先檢查。讀 `reference/gotchas.md`，裡面是真的會發生的失敗模式。

能抓到真正錯誤的檢查：

- **期間邊界。** 拿不完整的當月去比完整的上個月，永遠看起來像崩盤。要嘛比對同口徑，要嘛明確標示這是不完整的期間。
- **重複計算。** 一筆 Shopify 訂單和它的 Stripe 結算是同一筆銷售。如果兩個來源都有連，挑一個當營收來源，並註明是哪個。
- **空的分組。** 這個期間沒有銷售的據點要顯示為零，不要消失。一列消失會被讀成資料有問題。
- **對不上的總計。** 如果分組列加起來不等於總數，就直說，不要發布一個你守不住的數字。

## Step 6 — 交付

一定是兩份成品，照這個順序。

**聊天摘要先給。** 照 `reference/output_template.md` 的格式。先講什麼變了、代表什麼意思，不要一開頭就丟一堆表格。老闆要報表是因為想做決定，不是想要一份試算表。

寫作規則，和這個 plugin 裡每個報表 skill 一樣：

- 數字在前，文字在後。不要寫「sales were strong」，要寫「USD 43,200，比去年增加 8%」。
- 每個數字都要帶著它的比較基準。沒有基準的數字是錯過的洞察。
- 點名離群值。「Portland 下降 22%，是唯一低於去年的據點」比「結果好壞參半」好。
- 摘要最多三個發現。其餘的都放在活頁簿裡。

**接著是 XLSX。** 每個指標群組一個分頁，摘要分頁放最前面，拉回來的原始資料放在最後一個分頁，讓老闆可以驗算。用 script 產生，不要手工做。

**然後是報表頁面，依老闆儲存的輸出偏好決定，絕對不要預設成 markdown 檔。** 檢查 `## Business context` 區塊裡的 `Output preference`（共用風格指南規則，`../../shared/artifact-style.md`）：

- **Visual artifact（預設）：** 把報表渲染成符合 house style 的 HTML 頁面：每個主要指標是一個 stat tile，比較基準放在說明行；分組列（依據點、產品、業務）是表格，數字靠右對齊並用等寬數字；任何對比目標的指標都帶狀態 pill（good 達標、warn 落後、critical 未達）；三個發現放在頁面開頭自己的 panel；「n/a」的來源集中放在一行低調的頁尾。這是加在聊天摘要和活頁簿之外的，絕對不能取代它們。
- **docx / md / notion / canva 偏好：** 用該格式交付同樣的內容：DOCX 或 markdown 檔、透過 connector 建立的 Notion 頁面（指定目的地，絕對不覆寫），或透過 Canva connector 建立的 Canva Doc（每次執行建立新設計，用日期命名；表格改成清單）；如果沒連 Notion 或 Canva，就退回 visual artifact，並說明這是原因。XLSX 還是要一起交付。
- **Best for skill：** 用 visual artifact，因為報表是在螢幕上讀、一週一週比較的。

## Step 7 — 儲存定義

把 spec 附加到 `reference/saved_reports.md`，註明建立日期和頻率。這樣報表才會是週期性的，而不是一次性的。

如果那個檔案寫不進去（大多數安裝後的執行環境裡 skill 資料夾是唯讀的），就改把定義寫到老闆工作目錄裡的 `report-definitions.md`，並說明存到哪裡。定義默默存失敗，等於從來沒存，是同一個 bug。

如果老闆要求了頻率，用一行確認：「Saved. I'll run this the first Monday of each month.」排程是這個 skill 本身的屬性，不需要另外的指令。

## 執行之後

一行：報表跑完了、定義存好了。接著給一個最相關的下一步，附近最多再加兩個：

- 「The weekly pack, on schedule」執行 `/report-pack`，把這份報表加上脈絡後排成固定頻率。
- 「How's the business doing?」執行 `business-pulse`，看這些數字周圍的全貌。
- 「Cash forecast」執行 `cash-flow-snapshot`，當報表引出了現金問題時用。

最多三個建議。這個 session 裡老闆拒絕過的建議不要再提。

## 不要做的事

- **不要訪談老闆一份他已經定義過的報表。** 每次都先檢查 `saved_reports.md`。
- **不要問能不能拉資料。** skill 已經被叫起來了，直接跑。
- **不要編造數字。** 如果來源沒回傳東西，就寫「n/a」並點名來源。老闆會轉寄給銀行的報表裡放一個看起來合理的猜測，是嚴重的失敗。
- **不要一開頭就放表格。** 摘要才是成品，活頁簿只是附錄。
- **不要把「沒有 connector」當成阻礙。** CSV 路徑是一等公民的模式。

## 參考檔案

- `reference/report_spec.md`：spec 格式，附實作範例
- `reference/data_sources.md`：指標對應 connector 的方式，附備案
- `reference/output_template.md`：聊天摘要和活頁簿的確切結構
- `reference/saved_reports.md`：已儲存的報表定義，隨時間持續附加
- `reference/gotchas.md`：會產出「自信但錯誤」報表的失敗模式

## 使用沒列在清單上的工具

這個 skill 裡提到的 connector 是測試過的路徑，不是一道牆。如果老闆想讓這個流程用一個沒連接或沒列出的工具，就提供 `build-connector`：它會先查 connector 目錄，找不到再透過 Zapier 連接，絕對不會對著原始 API 手刻。連線建立之後，這個工具就像其他可選的 connector 一樣加入這個 skill，並受相同的核准關卡約束。
