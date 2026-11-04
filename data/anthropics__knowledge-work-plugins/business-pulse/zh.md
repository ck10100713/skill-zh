---
name: business-pulse
description: >
  為中小企業老闆產出一頁式的跨部門經營快照：現金狀況（帳務系統：MYOB、NetSuite、QuickBooks、Xero 或 Zoho Books）、
  銷售趨勢（PayPal/Square/Stripe）、pipeline 變動（HubSpot）、本週的承諾事項（Calendar）、
  緊急觀察清單（Gmail 或 M365、Slack），以及今天最需要關注的那一件事。
  主動嘗試所有可用的 connector，並依照實際連上的範圍優雅地縮減：只連一個 connector 就給部分的 pulse，
  整套都連就給完整全貌。當使用者問生意做得怎麼樣、想要快照、每日簡報、週五回顧，
  或說「我是不是漏掉什麼」「幫我跟上生意的狀況」之類的話時觸發。
  一週開始的簡報會導向 /monday-brief，它把這個 skill 當作第一個環節來執行。
allowed-tools: Read, WebFetch
---

# Business Pulse

一個 prompt，一頁。從每個已連線的工具拉即時資料，綜合成一份一眼就能掃完的簡報，並點出今天最重要、該動手的那一件事。直接做事，不要請使用者幫忙找資料。

## Step 1 — 平行拉資料

**所有 connector 呼叫在同一批平行送出**，確切的工具對指標對照請看 `reference/data_sources.md`。不要一個一個依序拉，延遲會讓一個 30 秒的 skill 變成痛苦的等待。

要同時嘗試的 connector：

- **QuickBooks** — 現金餘額、本月至今營收、未收應收帳款、逾期發票
- **Xero** — 用 Xero 的店家讀同樣的帳務：現金狀況、應收帳款、損益趨勢
- **Zoho Books** — 用 Zoho 的店家讀同樣的帳務：銀行餘額、已開票營收、逾期發票（沒有損益 endpoint，所以營收那一行是已開票營收，並且要這樣註明）
- **PayPal / Square** — 7 天的撥款、銷售趨勢、失敗或待處理的交易
- **Stripe** — 撥款與銷售趨勢、失敗的付款，以及任何新的爭議款，新的爭議直接進觀察清單（如果有連線）
- **Ramp** — 本週公司卡消費與帳戶餘額，唯讀（如果有連線）
- **Gusto** — 下次發薪日與金額，本週最大的現金承諾（如果有連線）
- **TikTok Ads** — 上週廣告花費、成效與每次成效成本，讓付費支出能和它宣稱帶動的銷售並排顯示（如果有連線）
- **Expensify** — 上週的刷卡消費與任何缺收據的費用，唯讀，讓花費上的意外在月底大亂之前浮現（如果有連線）
- **HubSpot** — 各階段的 pipeline、移動或成交的 deal、變冷的 deal、新 lead
- **Google Calendar** — 本週與未來 7 天的重要會議、期限、活動
- **Gmail 或 Microsoft 365** — 標為緊急的對話串、客訴、有時效的請求
- **Slack / Teams** — 緊急的內部訊號、需要老闆關注的對話串
- **RingEx Chat** — 用 RingEx 的店家讀同樣的內部訊號：需要老闆處理的緊急團隊聊天貼文（如果有連線）
- **DocuSign** — 擱著沒簽的 envelope，超過幾天就標出來，因為那是在等簽名的錢（如果有連線）
- **Zoho Desk** — 未結案的工單、升級案件（如果有連線）
- **Shopify** — 訂單、營收、銷售趨勢和出貨問題，讓電商業者看到自己真正的一天（如果有連線）
- **Square** — 出貨問題（如果有連線）

如果某個 connector 出錯或沒回傳資料，內部記錄一下就往下走。絕對不要因為單一整合壞掉就卡住 pulse。

**QuickBooks 備案**：如果 QBO 回傳非預期的狀態（帳號沒連上、同步待處理、空回應），把 Cash 區塊標成「n/a — QuickBooks unavailable」然後繼續。不要重試，也不要請使用者重新連線。

**Gmail 備案**：Gmail 的驗證時好時壞。如果呼叫出錯，默默跳過 Watch List 區塊，並在附錄註明「Gmail unavailable」，不要在 pulse 中途把錯誤秀出來。

**完全沒有任何東西連線，是支援的路徑，不是失敗。** 如果所有 connector 都不能用，不要停下來，也不要叫老闆去連。只問一次，用一則簡短的訊息，要幾個撐起 pulse 的數字：

- 銀行現在有多少現金，以及大約一週前是多少
- 任何逾期的東西：別人欠他們的發票、他們欠別人的帳單
- 這週的銷售對比一般的一週，粗估也行
- 這週有沒有任何已經讓他們擔心的事

用這些答案建出同樣的一頁式 pulse，把來源那行標成「owner-supplied, not pulled」，沒有數字的區塊就跳過。如果他們不想打數字，就指向靠檔案匯出運作的同類 skill：`cash-flow-snapshot` 和 `report-builder` 都吃 CSV，並明說這樣只能給部分的圖像，不是完整的。

## Step 2 — 計算指標

讀 `reference/thresholds.md` 取得紅黃綠的切分點。計算：

- **AR aging** — 未結清的 QuickBooks 發票，依距到期日的天數分組（0–30、31–60、61+）
- **Pipeline coverage** — HubSpot 加權 pipeline ÷ 月營收目標
- **營收趨勢** — 本月 QBO 營收對上個月（或最近 7 天的 PayPal/Square 對前 7 天）

為每個區塊指定 🟢/🟡/🔴 狀態。如果某個來源沒回傳東西，把該指標標成「n/a」並在附錄註明。

## Step 3 — 主動標出風險

掃描可行動的項目。每一筆風險都必須指名一筆具體的記錄和下一步，「有些逾期發票」沒用；「Acme Corp 的 USD 3,400，逾期 47 天，自 3 月 12 日起沒有回應」才能行動。

- 帳務系統裡逾期超過 30 天的發票，要指名客戶、金額、逾期天數
- HubSpot 裡 7 天以上沒有活動，或預計成交日已過但仍是開啟狀態的 deal
- 標為緊急，或含有「escalation」「complaint」「cancel」「refund」的郵件對話串
- 失敗或待處理、且超過 `reference/thresholds.md` 門檻（以該公司的幣別計為 200）的 PayPal/Square/Stripe 交易

## Step 4 — 組合輸出

使用 `reference/output_template.md` 裡的確切模板。只放有真實資料的區塊，沒連上的 connector 就省略對應標題。深度依情境調整：隨口一句「我們現在怎麼樣」就給比較完整的報告；「通話前快速看一下」就給精簡的。

跨 connector 的綜合，是這個 skill 真正值錢的地方。如果某則 Slack 訊息跟卡住的 HubSpot deal 有關，就在 #1 Priority 區塊把這個關聯點出來。有綜合，pulse 才會比一個一個工具去看更有用。

寫作規則：
- 數字在前，文字在後。絕對不要寫「營收健康」，要寫「這個月 USD 43k，▲ 8% MoM」，讓老闆自己判斷。
- 每個數字都要附上跟上一期的差異（有的話）。像現金餘額這種絕對值快照，也要顯示 WoW 差異。
- 用名字和金額，不要用形容詞。「Acme 的 USD 4,200，逾期 23 天」勝過「一些令人擔心的應收帳款」。
- 不要灌水。如果某個區塊沒有值得報告的，就寫「No material changes」然後往下走。

## Step 5 — 交付 pulse 頁面

在聊天裡的 pulse 之外（絕對不是取代它），依老闆存下來的輸出偏好交付完整的 pulse，
絕對不要預設用 markdown 檔。
檢查 `## Business context` 區塊的 `Output preference`（共用的風格指南規則，
`../../shared/artifact-style.md`）：

- **視覺化 artifact（預設）：** 用 house style 把 pulse 渲染成 HTML 頁面。
  現金餘額、本月至今營收和加權 pipeline 做成數字卡，差異放在輔助說明行；
  每個區塊的 🟢/🟡/🔴 變成狀態標籤（good、warn、critical）；
  觀察清單的風險做成表格，金額欄用 tabular-nums；
  #1 Priority 在最上面獨佔一個面板；
  不能用的 connector 放進附錄裡低調的一行。
- **docx / md / notion / canva 偏好：** 用該形式交付同樣的內容，
  可以是 DOCX 或 markdown 檔、透過 connector 建立的 Notion 頁面（要有指名的位置，絕對不覆蓋）、
  或透過 Canva connector 建立的 Canva Doc（每次執行都建新的設計，以日期命名；表格改成清單）；
  如果 Notion 或 Canva 沒連線，就退回視覺化 artifact，並說明是因為這個原因。
- **Best for skill：** 用視覺化 artifact，因為 pulse 是用來掃的，不是用來歸檔的。

## Step 6 — 匯出與分享（只問一次）

呈現 pulse 之後，提議一次：
- 「要我把這個存成檔案嗎？」（有 Files connector 就用，意思是在他們的雲端硬碟存一份，不是在 artifact 旁邊再多一個 HTML 下載）
- 「要我貼到你的 Slack 嗎？」（只有 Slack 已連線且使用者確認時才做，Slack 寫入需要明確核准）

如果他們說好，就做。如果他們說不要或沒回應，就繼續往下，不要再問。

## 執行之後

收尾用一行說明這次 pulse 涵蓋了什麼，然後給一個最相關的下一步，以及最多兩個相近的：

- 如果現金或 AR 標紅：「誰欠我錢」會執行 `invoice-chase`。
- 如果成長問題居多：「我的行銷有用嗎」會執行 `growth-pulse`。
- 要做成定期的：「Monday brief」會每週執行 `/monday-brief`。

最多三個提議。這個 session 裡老闆拒絕過的提議絕對不要重複。

## 範圍變體

老闆可能要求比較窄的切法：

- **「Just cash」/「financial check」** → 只要 Cash & Finance 加上跟 AR 相關的風險
- **「Pipeline only」/「deals check」** → 只要 Pipeline 區塊加上卡住的 deal 風險
- **「Watch list」/「anything urgent」** → 只要 Watch List 加上所有風險，不放指標區塊
- **「Quick snapshot before a call」** → 只要 TL;DR 加 #1 Priority，不放完整區塊

## 不要做的事

- **拉資料之前不要問許可。** skill 既然被叫了，就直接跑。問「要不要我查 QuickBooks？」整個重點就沒了。
- **不要捏造或估算數字。** 如果某個來源沒回傳東西，就明確說「n/a」。絕對不要用猜的補上缺口。
- **不要省略差異。** 沒有比較的數字是錯失的洞察。如果沒有上一期的基準，就寫「(no prior baseline)」，不要把那個欄位省掉。
- **不要在 pulse 中途秀 connector 的錯誤。** 記到附錄。pulse 要以實際交付的內容為主。
- **不要相信 QuickBooks 的 summary 物件。** 費用、毛利和 AP aging 的分段，要從資料列或明細呼叫取得（`../../shared/quickbooks-report-traps.md`）。

## 更多來源與排程預設

對照關係請讀 `reference/v2_sources.md`：

- **Shopify** — 訂單、營收和出貨狀態，讓電商業者在 pulse 裡看到自己真正的一天
- **任何帳務系統** — MYOB、NetSuite、QuickBooks、Xero 或 Zoho Books 都能餵 Cash & Finance 區塊；它們是平等的（`../../shared/connector-neutrality.md`）。連了兩個時，由老闆指定哪一個是總額的記錄來源

pulse 仍然用有連上的東西來建，並優雅地降級：只有一個 connector 就給部分的 pulse，整套都連就給完整全貌。

### 排程預設

這個 skill 可以排程，由預設決定形式：

| 預設 | 時機 | 形式 |
|---|---|---|
| Monday | 一週開始 | 完整 pulse，向前看。接下來有什麼、什麼需要關注 |
| Friday | 一週結束 | 回顧。什麼有進展、什麼成交、什麼延誤 |

排程是這個 skill 的屬性，不需要另外開一個指令。

在老闆覺得有用的 pulse 之後，提議一次頻率。不要問兩次。

## 參考檔案

- `reference/data_sources.md` — connector 工具對指標的確切對照，附備案
- `reference/thresholds.md` — 🟢/🟡/🔴 的切分點，可依老闆調整
- `reference/output_template.md` — 確切的 markdown 結構，不要偏離
- `reference/gotchas.md` — 已知的失敗模式（QB 狀態、Gmail 驗證、Slack 寫入）

## 使用沒列出的工具

這個 skill 裡提到的 connector 是測試過的路徑，不是一道牆。如果老闆想讓這個流程用某個沒連線或沒列出的工具，就提議 `build-connector`，它會先查 connector 目錄，沒有的話再透過 Zapier 連接，絕對不手工對著原始 API 硬幹。連線建好之後，這個工具就像其他任何可選的 connector 一樣加入這個 skill，受同樣的核准關卡約束。
