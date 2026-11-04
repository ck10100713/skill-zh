---
name: growth-pulse
description: >
  替中小企業老闆回答一個問題：成長引擎到底有沒有在運轉？
  從任何已連接的來源，拉出各通路的銷售趨勢、漏斗轉換、行銷活動回報、
  表現最好和最差的產品，以及客戶情緒，
  最後以本週值得採取的三個成長行動作結。這是 business-pulse 在成長面的
  孿生兄弟（business-pulse 負責財務面）。只要老闆問行銷或業務表現如何、
  某個活動值不值得、潛在客戶從哪裡來、為什麼 pipeline 停滯、哪些產品在動，
  或說了類似「is my marketing working」「growth check」
  「how's the funnel」或「where should I put my money next month」的話，就用它。
  即使老闆只點名單一通路，而不是整體成長，也要用。
allowed-tools: Read, WebFetch
---

# Growth Pulse

一頁回答成長引擎有沒有在運轉，以及這週該怎麼做。

老闆們說，他們得從三個儀表板拉數字，然後自己想辦法找出背後的故事。在這裡，故事才是交付物，不是儀表板。

## 步驟 1：平行拉取所有資料

把所有 connector 呼叫放在同一批送出。指標對應到工具的方式，請看 `reference/data_sources.md`。一個一個依序拉，會變成沒人願意等第二次的等待。

- **HubSpot**：依階段的 deal、新聯絡人、lead 來源、得標率、週期時間、停滯的 deal
- **PayPal、Stripe、Square**：營收趨勢、交易筆數、退款
- **Shopify**：訂單、SKU 層級的營收、回購率
- **QuickBooks**：已實現的營收，帳本認可的那個數字
- **TikTok Ads**：從原生 connector 取得上週的花費、曝光、點擊、成果，以及每個活動的單次成果成本（`report_integrated_get`，最近 7 天對比前 7 天），讓付費廣告花費和它宣稱帶動的銷售並排呈現
- **Mailchimp**：活動、電商和受眾成長的分析，附活動的營收歸因
- **Gmail 或 Microsoft 365**：進來的詢問量和回覆時間
- **公開評論**：透過網路研究取得近期的評分和評論文字

如果某個來源出錯或缺少，就記錄下來然後繼續。這個 skill 的設計是：只有一個 connector 時，也能說出有用的東西；有六個時，能說出很出色的東西。

**零個 connector 也是支援的路徑。** 請對方提供匯出檔，例如 CRM 的 deal 匯出、銷售報表、廣告成效 CSV，並用檔案做出同樣的 pulse。直接說明，不要停住。

## 步驟 2：計算五個檢視

門檻值請讀 `reference/thresholds.md`。計算每個檢視並指派一個狀態。

1. **通路趨勢**：這一期各通路的營收，對比上一期，以及有資料的話對比去年同期
2. **漏斗轉換**：進來的 lead、合格的、opportunity、成交；每個步驟之間的轉換率，以及最大的流失點在哪
3. **行銷活動回報**：每個活動的花費對比歸因營收，以及單一 lead 成本
4. **產品表現**：依營收和依成長率排序的前三名和後三名
5. **客戶情緒**：近期的評論分數、評論主題、爭議、流失訊號

沒有資料的檢視要標成「n/a」，並在附錄中點名。不要讓它默默消失。

## 步驟 3：找出真正的故事

這是這個 skill 發揮價值的地方。五個檢視本身仍然只是儀表板。工作是把它們串起來。

最重要的幾種連結：

- **花費上升、單一 lead 成本也上升**，代表這個通路正在飽和，不是在擴張
- **lead 量很強、得標率卻下降**，指向的是 lead 品質或回應速度，不是行銷
- **一個產品撐起整個趨勢**，代表成長比總數看起來的更脆弱
- **營收撐住、情緒卻下降**，是兩個月後會反映在營收上的早期警訊
- **漏斗急遽下降的某個階段**，通常比任何新活動都更有價值

找出能解釋這一期的那一句話，並把它放在最前面。

## 步驟 4：寫出三個行動

每份 pulse 都以剛好三個行動作結。不是五個，也不是列出所有注意到的事。

每個行動需要三件事，缺一個就不算行動：

- **做什麼**：具體到今天就能開始
- **為什麼**：這份 pulse 裡能證明它的那個數字
- **值多少**：機會或風險的大致規模

依影響大小排序，不是依容易程度。老闆自己可以判斷什麼容易；只有這份 pulse 能告訴他們什麼是大的。

如果誠實的答案是什麼都不用改，就這樣說。每週都硬湊出三個行動的 pulse，會訓練老闆去忽略它們。

## 步驟 5：撰寫

使用 `reference/output_template.md` 裡的確切結構。只放有真實資料的段落。

寫作規則：

- 數字領頭，文字跟隨。不要寫「paid social performed well」，要寫「paid social drove 41 leads at USD 18 each, down from USD 31 last month.」
- 每個數字都附帶比較。沒有基準線的數字，是錯失的洞察。
- 指名具體的活動、產品、通路或客戶。「Some campaigns underperformed」無法使用。
- 不要用老闆平常不用的行銷術語。不要寫「top of funnel velocity」，要寫「how many new leads came in and how fast.」
- 如果某個段落沒有值得說的，就寫「No material change」然後繼續。

## 步驟 6：交付 pulse 頁面

除了聊天裡的 pulse 之外，另外交付完整的 pulse（是額外附上，絕對不是取代），並依老闆儲存的輸出偏好，絕對不要預設用 markdown 檔案。檢查 `## Business context` 區塊的 `Output preference`（共用風格指南的規則，`../../shared/artifact-style.md`）：

- **視覺化 artifact（預設）：** 以 house style 把 pulse 渲染成 HTML 頁面。五個檢視各有一個面板；營收趨勢、單一 lead 成本和得標率是統計 tile，並以它們的比較當成脈絡行；活動回報和產品表現是表格，花費和營收欄位用 tabular-nums；每個檢視的狀態變成狀態標籤（good、warn、critical，或以純文字寫 n/a）；三個行動排好名次，放在自己的面板，作為頁面的結尾。
- **docx / md / notion / canva 偏好：** 用那種形式交付相同內容：DOCX 或 markdown 檔案、透過 connector 建立的 Notion 頁面（指定目的地，絕對不覆寫）、或透過 Canva connector 建立的 Canva Doc（每次執行都是新的設計，以日期命名；表格變成清單）；如果沒有連接 Notion 或 Canva，就退回用視覺化 artifact，並說明原因。
- **Best for skill：** 用視覺化 artifact，因為五個檢視並排在同一個畫面上最好比較。

## 步驟 7：提議儲存，只提一次

呈現之後，只提議一次把 pulse 存成檔案或貼到 Slack。貼到 Slack 是對外寫入，所以只有在明確說「好」時才會發生，這個提議本身就是核准關卡。說好就做。說不或沒回應就繼續往下。不要問兩次。

然後用一行總結 pulse 的發現，再加上最相關的一個下一步，以及附近最多另外兩個：

- 如果行動指向內容或推廣：「what should I promote」會執行 `content-strategy`。
- 如果問題出在漏斗：「fill my funnel」會執行 `/grow-pipeline`。
- 想看財務面的孿生 skill：「how's the business doing」會執行 `business-pulse`。

最多三項提議。這個 session 裡老闆婉拒過的提議，絕對不再重複。

## 範圍變體

老闆常常只想要其中一塊，不是整份 pulse：

- **「How did the campaign do」**：只做活動回報，再加情緒檢查
- **「How's the pipeline」**：只做漏斗轉換和停滯的 deal
- **「What's selling」**：只做產品表現
- **「Are we getting reviews」**：只做情緒
- **「Where should I spend next month」**：通路趨勢和活動回報，三個行動偏重預算

給他們問的那一塊。不要拿完整的 pulse 硬套在一個狹窄的問題上。

## 不要做什麼

- **拉資料之前不要先問許可。** 這個 skill 已經被呼叫了。直接執行。
- **不要編造歸因。** 如果活動的營收追蹤不到，就說歸因無法取得，不要用猜的把營收分配過去。假的歸因曾經挪動過真實的預算。
- **不要把 CRM 的預測金額當成營收回報。** Deal 金額是期望；發票是事實。要標明哪個是哪個。
- **不要跨來源重複計算。** 一筆在 Stripe 結算的 Shopify 訂單，算一筆銷售。選一個營收來源並點名它。
- **不要在同一個來源內重複計算。** 依客戶彙總的銷售報表，對同一個客戶會同時回傳一列上層摘要列和另一列單獨的總計列。在你替客戶排名或計算集中度之前，要先過濾掉標為總計的列，否則同一個客戶會在清單裡出現兩次，集中度的數字也會偏高。
- **不要製造急迫感。** 如果成長平穩，pulse 讀起來就該是平穩的。
- **不要從 QuickBooks 的損益摘要讀費用或利潤率。** 要把各列加總（`../../shared/quickbooks-report-traps.md`，Trap 2）。

## 參考檔案

- `reference/data_sources.md`：connector 對應到指標，附備案
- `reference/thresholds.md`：五個檢視各自的狀態門檻
- `reference/output_template.md`：確切的輸出結構
- `reference/gotchas.md`：會產生「很有自信、卻是錯的」成長建議的失敗模式

## 使用沒有列出的工具

這個 skill 裡提到的 connector 是測試過的路徑，不是一道牆。如果老闆想讓這個流程用某個沒連接、也沒列出的工具，就提供 `build-connector`：它會先檢查 connector 目錄，沒有的話再透過 Zapier 連接，絕對不要對著原始 API 手工打造。連線建立之後，這個工具就跟其他任何選用的 connector 一樣加入這個 skill，並受同樣的核准關卡約束。
