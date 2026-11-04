---
name: plan-payroll
description: 從頭到尾跑完「有把握發薪」這條串接：先用 cash-flow-snapshot 預測發薪期間的現金，再用 invoice-chase 排序並擬好逾期發票的催款提醒來補任何缺口，然後用 payroll-prep 彙整工時、標出每個異常並排好發薪批次。在 Gusto 上，發薪批次排好後由老闆送出；在 QuickBooks Payroll 上，或沒有薪資系統時，最後一步是驗證過、由老闆鍵入的發薪清單。這條串接絕不按下發薪的按鈕。以帳本（MYOB、NetSuite、QuickBooks、Xero 或 Zoho Books）為基礎，搭配 Gmail 或 M365、PayPal、Square、Stripe，以及 Gusto 或 QuickBooks Payroll 補充細節，並備有 CSV 和工時表上傳作為退路。只要發薪是擔心的事就用，包括「can I make payroll」、「payroll is due Friday」、「plan payroll」、「will I have enough to pay the crew」，或「I need to run payroll but money is tight」。可接受選用的期間（horizon）和發薪日參數。
allowed-tools: Read, WebFetch
---

# 規劃發薪（Plan Payroll）

依序三個 skill：確認發薪有著落，沒有的話補上缺口，然後執行。

老闆在這裡不會問兩個分開的問題。「Can I make payroll」和「run payroll」是同一個擔心，把它們拆到兩個 session，就會變成晚上 11 點有人在沒查過銀行餘額的情況下就把發薪批次鍵入。

解析參數：

- `--horizon`（預設 `30`）：預測的天數視窗：30、60 或 90
- `--payroll-date`（選填）：發薪執行的日期；預設為下一個排定的發薪日

## 步驟 1：發薪有著落嗎？（cash-flow-snapshot）

呼叫 `cash-flow-snapshot`。預測的運算、信賴區間和 CSV 備援都歸它管，這裡一項都不要重建。

- **輸入：** 預測期間和發薪日。
- **輸出：** 30/60/90 天預測、點名的風險旗標、一段聊天摘要，以及一份 XLSX。

在其他任何事情之前，先用一句話說出結論：夠、吃緊，或在某個明確的日期短缺某個明確的金額。

**關卡：串接接下來往哪裡走。** 如果發薪綽綽有餘，就問要不要跳過催收步驟，直接進入執行。如果有缺口，就呈現出來，等到明確的「see what we can collect」才進入步驟 2。

## 步驟 2：補上缺口（invoice-chase）

呼叫 `invoice-chase`。排序、語氣配合，以及依發票類型的寄送路徑都歸它管。

- **輸入：** 步驟 1 得出的缺口金額和它出現的日期。
- **輸出：** 排好名次的逾期發票，每張附一份擬好的提醒，PayPal 開立的發票排成 PayPal 寄送，其他的則成為信件草稿。

把排序跟步驟 1 連起來：顯示在預測期間內會收回多少，以及這是否真的補上了發薪缺口。一份 45 天後才會付款的提醒，對週五的發薪毫無幫助，要直說。

**關卡：沒有核准，什麼都不准寄。** 老闆說寄之前，都只是草稿，逐封或以他們指名的批次核准。

## 步驟 3：排好發薪批次（payroll-prep）

呼叫 `payroll-prep`。期間設定、工時加總、異常檢查和帳務同步都歸它管。

- **輸入：** 發薪期間、名單，以及步驟 1 的現金結論。
- **輸出：** 逐人的發薪清單，每個異常都標在所屬的那個人身上，總計，以及發薪日需要的現金。

沿用步驟 1 的結果，不要重算。當 `payroll-prep` 回報這批發薪付不付得出來時，用的是這條串接已經產生的預測，再加上步驟 2 預期會收到的任何款項。

**關卡：旗標，一次一個。** `payroll-prep` 會逐一走過每個異常。不要把它們合併成一個「看起來沒問題嗎？」，每一個都是某個人的薪水。

**關卡：發薪本身。** 連了 Gusto 時，發薪批次排在 Gusto 裡（`payroll-prep` 用 `update_payroll` 寫入核准的輸入；絕不呼叫 `run_payroll`）。連了 QuickBooks Payroll 時，connector 只有讀取、沒有排發薪批次的寫入，所以成果是驗證過、由老闆鍵入的發薪清單，這是 connector 目前擁有的，不是比較差的路徑。排程只有在來源真的回傳了名單和排程時才成立：當已連接的來源回報有員工卻沒交付任何員工時，payroll-prep 會停下排程路徑，這條串接就以發薪清單收尾，並明白說出來。**由老闆送出。** 兩者都沒有時，交付物是供手動輸入的驗證過的發薪清單，這是完整的成果，不是降級的成果。這也包括 Gusto 回報 blocker 的情況，發薪清單會從 `payroll-prep` 繼承 blocker 清單。

## 步驟 4：收尾

一份回顧，依這個順序：現金結論、寄了什麼給誰、如果提醒轉換成收款後預估的狀況，以及排好的發薪批次：人數、總工時、總毛薪、離開帳戶的現金、發薪日，以及任何還沒處理的旗標。

Ray Okonkwo 四行就看完：15 日現金短缺 USD 4,200，寄出三則提醒涵蓋 USD 6,800，其中兩筆很可能在期間內到帳，發薪批次排好 9 個人、USD 18,340，Marcus 還有一筆漏打卡尚未處理。

## 輸出

**依老闆儲存的輸出偏好交付步驟 4 的回顧，絕對不要預設產出 markdown 檔。** 檢查 `## Business context` 區塊裡的 `Output preference`（共用風格指南規則，`../../shared/artifact-style.md`）：

- **視覺化 artifact（預設）：** 用 house style 把回顧渲染成 HTML 頁面，現金結論做成最前面的數字卡片（stat tile），寄出的提醒和它們預估的收款用 tabular-nums，排好的發薪批次的總計，任何還沒處理的旗標都帶標籤。預估的現金要標示為預估。
- **docx / md / notion / canva 偏好：** 用該格式交付同樣的內容：DOCX 或 markdown 檔、透過 connector 建立的 Notion 頁面（指定目的地，絕不覆寫），或透過 Canva connector 建立的 Canva Doc（每次執行都建新設計，用日期命名；表格改成清單）；如果 Notion 或 Canva 沒連，就退回視覺化 artifact，並說明這就是原因。
- **Best for skill：** 用視覺化 artifact，因為這份輸出是一個畫面，回答「can I make payroll」。

## Connector 失敗

如果連不到任何帳本（MYOB、NetSuite、QuickBooks、Xero 或 Zoho Books，老闆用哪個就是哪個），就停下來，並依類別說明，因為預測是這條串接的基礎。如果支付 connector 或信件 connector（Gmail 或 M365）失敗，就點名它，其餘繼續。如果薪資系統失敗，就退到發薪清單路徑，不要中止；老闆仍然能拿到一份可以執行的薪資。當發薪批次無法排好或同步進帳務時（blocker、缺少寫入權限），就在步驟 4 的回顧中說明，並交付發薪清單加上傳票摘要，由記帳人員鍵入；由 `payroll-prep` 的 blocker 檢查決定適用哪條路徑。

## 不要做的事

- **不要送出薪資。** 串接負責排好；由老闆送出。就算老闆要求直接做下去，這一點也不變。
- **沒有核准不要寄提醒。** 在被告知之前都是草稿。
- **不要因為老闆要求「just run payroll」就跳過步驟 1。** 現金檢查只要三十秒，而且是這條串接存在的理由。
- **不要在步驟 3 裡重算預測。** 現金數字只有一組，只有一個來源。
- **不要批次檢視異常。** 每個人每個問題一個決定。
- **不要把缺少薪資 connector 當成阻礙。** 發薪清單是設計好的路徑。在斷定沒有薪資來源之前，先查有沒有 QuickBooks Payroll；用 QuickBooks 的企業常常有它，但沒有 Gusto。
- **不要把還沒收到的款項當成已經到帳來承諾。** 預估就是預估；要標示出來。
- **不要在這條串接的任何輸出中重現任何人的 SSN、生日、住家地址或銀行帳號**（`../../shared/personal-data.md`）。

## 串接之後

發薪有著落，提醒已經寄出，發薪批次已排好等老闆送出。很自然的下一步是「pay the bills」，`/pay-the-bills` 會在同一份現金狀況擺在畫面上的情況下處理廠商那一端。附近還有：「cash forecast」（`cash-flow-snapshot`）在提醒轉換成收款的過程中追蹤現金狀況，以及期間結束時的「close the month」（`/close-month`）。最多提議三個，而且這個 session 裡老闆已經拒絕過的提議就跳過。

## 使用沒列出來的工具

這個 skill 裡提到的 connector 是測試過的路徑，不是一道牆。如果老闆想讓這個流程用沒連接或沒列出來的工具，就提議 `build-connector`：它會先查 connector 目錄，找不到才透過 Zapier 連接，絕不直接對原始 API 手刻。連線建立之後，這個工具就像任何其他選用的 connector 一樣加入這個 skill，並遵守同樣的核准關卡。
