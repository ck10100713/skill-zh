---
name: comps-analysis
description: |
  在 Excel/試算表中建立機構等級的可比公司分析，包含營運指標、估值倍數和統計標竿比較。

  **很適合用在：**
  - 上市公司估值（併購、投資分析）
  - 跟產業同業比較績效
  - IPO 或募資輪次的定價
  - 找出估值離群值（高估/低估）
  - 支援投資委員會簡報
  - 製作產業概覽報告

  **不太適合：**
  - 沒有可比較的上市同業的私人公司
  - 高度多角化的集團
  - 財務困難/破產的公司
  - 還沒有營收的新創
  - 商業模式獨特的公司
---

# 可比公司分析

## ⚠️ 關鍵：資料來源優先順序（先讀這個）

**一律遵守這個資料來源階層：**

1. **第一優先：檢查有沒有 MCP 資料來源**：如果有 S&P Kensho MCP、FactSet MCP 或 Daloopa MCP，財務與交易資訊就只用它們
2. 如果上面那些 MCP 資料來源可用，**不要使用網路搜尋**
3. **只有在 MCP 都不可用時：**才用 Bloomberg Terminal、SEC EDGAR 申報文件，或其他機構等級的來源
4. **絕對不要把網路搜尋當成主要資料來源**：它缺乏機構等級分析所需要的準確性、稽核軌跡和可靠性

**為什麼重要：**MCP 來源提供經過驗證、機構等級的資料，並附有正確的出處。網路搜尋的結果可能過時、不準確，或不適合用在財務分析。

---

## 概覽
這個 skill 教 Claude 建立機構等級的可比公司分析，結合營運指標、估值倍數和統計標竿比較。輸出是結構化的 Excel/試算表，讓人透過同業比較做出有根據的投資決策。

**參考資料與情境化：**

`examples/comps_example.xlsx` 裡附有一份可比公司分析的範例。使用這個或這個 skill 目錄裡的其他範例檔時，要聰明地使用：

**範例可以拿來：**
- 了解結構的階層（各區塊如何銜接）
- 掌握預期的嚴謹程度（統計深度、文件記錄標準）
- 學習原則（清楚的標題、透明的公式、稽核軌跡）

**範例不能拿來：**
- 一模一樣地重現格式或指標
- 不考慮情境就照抄版面
- 不管對象是誰，都套用同一種視覺風格

**一定要先問自己：**
1. **「你有偏好的格式，還是我該調整範本的風格？」**
2. **「對象是誰？」**（投資委員會、董事會簡報、快速參考、詳細備忘錄）
3. **「核心問題是什麼？」**（估值、成長分析、競爭定位、效率）
4. **「背景是什麼？」**（併購評估、投資決策、產業標竿、績效檢討）

**依具體情況調整：**
- **產業背景**：科技巨頭需要的指標，跟新興 SaaS 新創不同
- **產業特有的需求**：及早加入相關的指標（例如科技業的 cloud ARR、企業客戶數、開發者生態系）
- **對公司的熟悉程度**：知名公司可能不需要太多背景介紹，要把重點放在差異分析
- **決策類型**：併購需要的重點，跟持續的投資組合監控不同

**核心原則：**使用範本的原則（清楚的結構、統計的嚴謹、透明的公式），但依情境調整執行方式。目標是機構等級的分析，不是機構外觀的範本。

使用者提供的範例和明確的偏好，永遠優先於預設值。

## 核心理念
**「先把結構建對，再讓資料說故事。」**

從會逼你策略性思考「什麼重要」的標題開始，輸入乾淨的資料，建立透明的公式，讓統計數字自動浮現。一份好的 comps，應該讓沒參與建置的人也能馬上看懂。

---

## ⚠️ 關鍵：用公式，不要寫死數值 + 逐步驗證

**環境：Office JS 還是 Python：**
- **如果在 Excel 裡執行（Office Add-in / Office JS）：**直接用 Office JS（`Excel.run(async (context) => {...})`）。用 `range.formulas = [["=E7/C7"]]` 寫入公式，不要用 `range.values`。不需要另外的重算步驟，Excel 會原生處理。用 `range.format.*` 設定顏色/字型。
- **如果是產生獨立的 .xlsx 檔：**用 Python/openpyxl。寫 `cell.value = "=E7/C7"`（公式字串）。
- 兩種方式原則相同，只是把 API 呼叫換一下。
- **Office JS 合併儲存格的陷阱：**不要先呼叫 `.merge()` 再對合併後的範圍設定 `.values`（會丟出 `InvalidArgument`，因為範圍仍然回報合併前的尺寸）。正確做法是先只對左上角的儲存格寫值，再合併並格式化整個範圍：
  ```js
  ws.getRange("A1").values = [["TECHNOLOGY — COMPARABLE COMPANY ANALYSIS"]];
  const hdr = ws.getRange("A1:H1");
  hdr.merge();
  hdr.format.fill.color = "#1F4E79";
  hdr.format.font.color = "#FFFFFF";
  hdr.format.font.bold = true;
  ```

**用公式，不要寫死：**
- 每個推導出來的值（利潤率、倍數、統計量）**一定要**是參照輸入儲存格的 Excel 公式，絕對不能貼上預先算好的數字
- 用 Python/openpyxl 建立工作表時：寫 `cell.value = "=E7/C7"`（公式字串），**不要**寫 `cell.value = 0.687`（算好的結果）
- 唯一可以寫死的值，是原始輸入資料（營收、EBITDA、股價等），而且每一個都要加儲存格註解，註明來源
- 原因：輸入改變時，模型必須自動更新。寫死的利潤率就是一顆等著爆的悄悄 bug。

**每一步都跟使用者確認：**
- 設定好結構之後 → 在填資料之前，先給使用者看標題的版面
- 輸入完原始資料之後 → 在建立公式之前，先給使用者看輸入區塊，並確認來源/期間
- 建完營運指標公式之後 → 在進入估值之前，先給使用者看算出來的利潤率並一起做合理性檢查
- 建完估值倍數之後 → 在加入統計量之前，先給使用者看倍數，確認看起來合理
- **不要**一口氣把整份工作表從頭做到尾再交出去，每個區塊都確認，及早抓出錯誤

---

## 第 1 節：文件結構與設定

### 標題區塊（第 1-3 列）
```
Row 1: [ANALYSIS TITLE] - COMPARABLE COMPANY ANALYSIS
Row 2: [List of Companies with Tickers] • [Company 1 (TICK1)] • [Company 2 (TICK2)] • [Company 3 (TICK3)]
Row 3: As of [Period] | All figures in [USD Millions/Billions] except per-share amounts and ratios
```

**為什麼重要：**馬上建立背景。任何人打開這個檔案，都知道自己在看什麼、是什麼時候做的，以及該怎麼解讀這些數字。

### 視覺慣例標準（選用：使用者的偏好和上傳的範本永遠優先）

**重要：這些只是建議的預設值。優先順序一律是：**
1. 使用者明確的格式偏好
2. 上傳的任何範本檔案裡的格式
3. 公司/團隊的風格指南
4. 這些預設值（只有在沒有其他指引時才用）

**建議的字型與排版：**
- **字型家族**：Times New Roman（專業、好讀、業界標準）
- **字型大小**：資料儲存格 11pt，標題 12pt
- **粗體**：區塊標題、公司名稱、統計量標籤

**預設的顏色與底色：專業的藍/灰配色（越簡約越好）：**
- **保持克制**：只用藍色和灰色。**不要**加入綠色、橘色、紅色或多種強調色。一份乾淨的 comps 工作表總共用 3-4 種顏色。
- **區塊標題**（例如 "OPERATING STATISTICS & FINANCIAL METRICS"）：
  - 深藍色背景（`#1F4E79` 或 `#17365D` 海軍藍）
  - 白色粗體文字
  - 整列所有欄位都填色
- **欄位標題**（例如 "Company"、"Revenue"、"Margin"）：
  - 淺藍色背景（`#D9E1F2` 或類似的淡藍色）
  - 黑色粗體文字
  - 置中對齊
- **資料列**：
  - 公司資料用白色背景
  - 公式用黑色文字；寫死的輸入值用藍色文字
- **統計量列**（Maximum、75th Percentile 等）：
  - 淺灰色背景（`#F2F2F2`）
  - 黑色文字，標籤靠左對齊
- **整個配色就這樣**：深藍 + 淺藍 + 淺灰 + 白色。除非使用者的範本另有指定，否則不要用別的。

**建議的格式慣例：**
- **小數精度**：
  - 百分比：1 位小數（12.3%）
  - 倍數：1 位小數（13.5x）
  - 金額：不要小數，加千分位（69,632）
  - 以百分比顯示的利潤率：1 位小數（68.7%）
- **邊框**：不要邊框（乾淨、簡約的外觀）
- **對齊**：所有指標置中對齊，看起來乾淨一致
- **儲存格尺寸**：所有欄寬要統一/均等，所有列高要一致（形成乾淨、專業的格線）

**注意：**如果使用者提供了範本檔，或指定了不同的格式，就用那個。

---

## 第 2 節：營運統計與財務指標

### 核心欄位（從這些開始）
1. **Company**：名稱格式要一致
2. **Revenue**：規模指標（依情境可以是 LTM、季度或年度）
3. **Revenue Growth**：年增率
4. **Gross Profit**：營收減去銷貨成本
5. **Gross Margin**：GP/Revenue（基本的獲利能力）
6. **EBITDA**：扣除利息、稅、折舊、攤銷前的盈餘
7. **EBITDA Margin**：EBITDA/Revenue（營運效率）

### 選用的新增項目（依產業/目的選擇）
- **季度 vs LTM**：如果季節性重要，兩個都放
- **Free Cash Flow**：用於資本密集或 SaaS 事業
- **FCF Margin**：FCF/Revenue（現金創造效率）
- **Net Income**：用於成熟、有獲利的公司
- **Operating Income**：用於 D&A 變動大的事業
- **CapEx 指標**：用於重資產產業
- **Rule of 40**：專用於 SaaS（成長 % + 利潤率 %）
- **FCF Conversion**：用於獲利品質分析（進階）

### 公式範例（以第 7 列為例）
```excel
// 核心比率：一律要計算
Gross Margin (F7): =E7/C7
EBITDA Margin (H7): =G7/C7

// 選用的比率：相關時才加入
FCF Margin: =[FCF]/[Revenue]
Net Margin: =[Net Income]/[Revenue]
Rule of 40: =[Growth %]+[FCF Margin %]
```

**黃金法則：**每個比率都應該是 [某個東西] / [Revenue]，或 [某個東西] / [這張工作表裡的另一個東西]。保持簡單。

### 統計量區塊（放在公司資料之後）

**關鍵：為所有可比較的指標（比率、利潤率、成長率、倍數）加上統計量公式。**

```
[留一個空白列，做視覺分隔]
- Maximum: =MAX(B7:B9)
- 75th Percentile: =QUARTILE(B7:B9,3)
- Median: =MEDIAN(B7:B9)
- 25th Percentile: =QUARTILE(B7:B9,1)
- Minimum: =MIN(B7:B9)
```

**需要統計量的欄位（可比較的指標）：**
- Revenue Growth %、Gross Margin %、EBITDA Margin %、EPS
- EV/Revenue、EV/EBITDA、P/E、Dividend Yield %、Beta

**不需要統計量的欄位（規模指標）：**
- Revenue、EBITDA、Net Income（絕對規模隨公司大小而異）
- Market Cap、Enterprise Value（在規模不同的公司之間沒有可比性）

**注意：**在公司資料和統計量列之間加一個空白列，做視覺分隔。**不要**加 "SECTOR STATISTICS" 或 "VALUATION STATISTICS" 的標題列。

**為什麼四分位數重要：**它們呈現的是分布，不只是平均值。75th percentile 的倍數，能告訴你「溢價」的公司是用什麼價位在交易。

---

## 第 3 節：估值倍數與投資指標

### 核心估值欄位（從這些開始）
1. **Company**：順序跟營運區塊相同
2. **Market Cap**：目前的市場估值
3. **Enterprise Value**：Market Cap ± 淨負債/現金
4. **EV/Revenue**：市場為每一塊錢營收付多少
5. **EV/EBITDA**：市場為每一塊錢盈餘付多少
6. **P/E Ratio**：價格相對於淨利

### 選用的估值指標（依情境選擇）
- **FCF Yield**：FCF/Market Cap（用於以現金為重點的分析）
- **PEG Ratio**：P/E/成長率（用於成長型公司）
- **Price/Book**：市值 vs. 帳面價值（用於重資產事業）
- **ROE/ROA**：報酬指標（用於獲利能力比較）
- **Revenue/EBITDA CAGR**：歷史成長率（用於趨勢分析）
- **Asset Turnover**：Revenue/Assets（用於營運效率）
- **Debt/Equity**：槓桿（用於資本結構分析）

**關鍵原則：**納入 3-5 個對你的產業重要的核心倍數。不要因為能放就把所有可能的指標都放進去。

### 公式範例
```excel
// 核心倍數：一律包含
EV/Revenue: =[Enterprise Value]/[LTM Revenue]
EV/EBITDA: =[Enterprise Value]/[LTM EBITDA]
P/E Ratio: =[Market Cap]/[Net Income]

// 選用的倍數：有資料時才加入
FCF Yield: =[LTM FCF]/[Market Cap]
PEG Ratio: =[P/E]/[Growth Rate %]
```

### 交叉參照規則
**關鍵：**估值倍數**一定要**參照營運指標區塊。絕對不要把同樣的原始資料輸入兩次。如果營收在 C7，EV/Revenue 公式就要參照 C7。

### 統計量區塊
結構跟營運區塊相同：每個指標都有 Max、75th、Median、25th、Min。在公司資料和統計量之間加一個空白列做視覺分隔。**不要**加 "VALUATION STATISTICS" 的標題列。

---

## 第 4 節：備註與方法論文件

### 必要的組成

**資料來源與品質：**
- 資料從哪裡來？（S&P Kensho MCP、FactSet MCP、Daloopa MCP、Bloomberg、SEC 申報文件）
- 涵蓋哪個期間？（Q4 2024、經查核的數字）
- 如何驗證？（對照 10-K/10-Q 交叉檢查）
- 注意：如果有 MCP 資料來源（S&P Kensho、FactSet、Daloopa），優先使用，準確性和可追溯性更好

**關鍵定義：**
- EBITDA 的計算方法（Gross Profit + D&A，或 Operating Income + D&A）
- Free Cash Flow 的公式（Operating CF - CapEx）
- 特殊指標的說明（Rule of 40、FCF Conversion）
- 時間期間的定義（LTM、CAGR 的計算期間）

**估值方法論：**
- Enterprise Value 是怎麼計算的？（Market Cap + Net Debt）
- 用了哪些成長率？（歷史 CAGR、未來預估）
- 有做哪些調整？（排除一次性項目、標準化的利潤率）

**分析框架：**
- 投資論點是什麼？（Cloud/SaaS 效率）
- 哪些指標最重要？（現金創造、資本效率）
- 讀者該如何解讀這些統計量？（四分位數提供背景脈絡）

---

## 第 5 節：選擇正確的指標（決策框架）

### 從「我在回答什麼問題？」開始

**「哪家公司被低估？」**
→ 聚焦：EV/Revenue、EV/EBITDA、P/E、Market Cap
→ 略過：營運細節、成長指標

**「哪家公司最有效率？」**
→ 聚焦：Gross Margin、EBITDA Margin、FCF Margin、Asset Turnover
→ 略過：規模指標、絕對金額

**「哪家公司成長最快？」**
→ 聚焦：Revenue Growth %、EBITDA CAGR、使用者/客戶成長
→ 略過：利潤率指標、槓桿比率

**「誰是最好的現金創造者？」**
→ 聚焦：FCF、FCF Margin、FCF Conversion、CapEx 強度
→ 略過：EBITDA、P/E 比率

### 依產業選擇指標

**軟體/SaaS：**
必備：Revenue Growth、Gross Margin、Rule of 40
選用：ARR、Net Dollar Retention、CAC Payback
略過：Asset Turnover、庫存指標

**製造/工業：**
必備：EBITDA Margin、Asset Turnover、CapEx/Revenue
選用：ROA、Inventory Turns、Backlog
略過：Rule of 40、SaaS 指標

**金融服務：**
必備：ROE、ROA、Efficiency Ratio、P/E
選用：Net Interest Margin、Loan Loss Reserves
略過：Gross Margin、EBITDA（對銀行沒有意義）

**零售/電商：**
必備：Revenue Growth、Gross Margin、Inventory Turnover
選用：Same-Store Sales、Customer Acquisition Cost
略過：高 R&D 或 CapEx 的指標

### 「5-10 法則」

**5 個營運指標**：Revenue、Growth、2-3 個利潤率/效率指標
**5 個估值指標**：Market Cap、EV、3 個倍數
**= 總共 10 欄**：足以說完故事，又不會多到讓人失去主線

如果你有超過 15 個指標，大概就混進雜訊了。要狠心刪減。

---

## 第 6 節：最佳實務與品質檢查

### 開始之前
1. **定義同業群組**：公司必須真正可比較（類似的商業模式、規模、地理）
2. **選擇正確的期間**：LTM 能抹平季節性；季度能顯示趨勢
3. **一開始就統一單位**：選百萬還是十億，會影響所有東西
4. **對應資料來源**：知道每個數字來自哪裡

### 建置過程中
1. **先輸入所有原始資料**：寫公式之前，先把藍色文字全部完成
2. **為所有寫死的輸入值加上儲存格註解**：右鍵點儲存格 → 插入註解 → 記錄來源或假設

   **有來源的資料，要精確標明出處：**
   - 範例："Bloomberg Terminal - MSFT Equity DES, accessed 2024-10-02"
   - 範例："Q4 2024 10-K filing, page 42, line item 'Total Revenue'"
   - 範例："FactSet consensus estimate as of 2024-10-02"
   - **可以的話加上超連結**：右鍵點儲存格 → 連結 → 貼上 SEC 申報文件、資料來源或報告的 URL

   **假設則要解釋理由：**
   - 範例："Assumed 15% EBITDA margin based on peer median, company does not disclose"
   - 範例："Estimated Enterprise Value as Market Cap + $50M net debt (from Q3 balance sheet, Q4 not yet available)"
   - 範例："Forward P/E based on street consensus EPS of $3.45 (average of 12 analyst estimates)"

   **為什麼重要**：能建立稽核軌跡、資料驗證、假設透明度，也方便日後更新
3. **一列一列建立公式**：每個計算都先測試過，再往下做
4. **標題用絕對參照**：$C$6 能鎖住標題列
5. **格式要一致**：百分比就用百分比格式，不要用小數
6. **加上條件式格式**：自動標示離群值

### 合理性檢查
- **利潤率測試**：Gross margin > EBITDA margin > Net margin（依定義永遠成立）
- **倍數的合理性**：
  - EV/Revenue：通常 0.5-20x（不同產業差異很大）
  - EV/EBITDA：通常 8-25x（各產業之間相當一致）
  - P/E：通常 10-50x（取決於成長率）
- **成長與倍數的相關性**：成長越高，通常倍數越高
- **規模與效率的取捨**：越大的公司，利潤率通常越好（規模效益）

### 要避免的常見錯誤
❌ 在公式裡把市值和企業價值混用
❌ 分子和分母使用不同的時間期間（LTM vs 季度）
❌ 在公式裡寫死數字，而不是用儲存格參照
❌ **寫死的輸入值沒有儲存格註解來註明來源或解釋假設**
❌ 有 SEC 申報文件或資料來源時，卻沒加超連結
❌ 沒有明確目的，卻放入太多指標
❌ 放入不可比較的公司（不同的商業模式）
❌ 使用過時的資料卻沒有揭露
❌ 百分比的平均計算不正確（應該用中位數）

---

## 第 6 節：進階功能

### 動態標題
對於顯示計算結果的欄位，用清楚的單位標籤：
```
Revenue Growth (YoY) % | EBITDA Margin | FCF Margin | Rule of 40
```

### 四分位數分析的好處
比起只看平均數/中位數，四分位數能顯示：
- **75th percentile** = 「溢價」的公司在這個價位交易
- **Median** = 一般的市場估值
- **25th percentile** = 「折價」的區間

這有助於回答：「相對同業，我們的標的公司交易價格是貴還是便宜？」

### 依產業的調整

**軟體/SaaS：**
- 新增：ARR、Net Dollar Retention、CAC Payback Period
- 強調：Rule of 40、FCF margin、gross margin >70%

**醫療保健：**
- 新增：R&D/Revenue、管線價值、監管狀態
- 強調：EBITDA margin、成長率、給付（reimbursement）風險

**工業：**
- 新增：Backlog、訂單趨勢、地理組成
- 強調：ROIC、asset turnover、景氣循環調整

**消費：**
- 新增：Same-store sales、客戶取得成本、品牌價值
- 強調：營收成長、gross margin、庫存週轉

---

## 第 7 節：工作流程與實用技巧

### 逐步流程
1. **建立結構**（30 分鐘）
   - 建立所有標題
   - 設定儲存格格式（輸入用藍色、公式用黑色）
   - 鎖定單位和日期參照

2. **蒐集資料**（60-90 分鐘）
   - 從第一手來源取得（有的話用 S&P Kensho MCP、FactSet MCP、Daloopa MCP；否則用 Bloomberg、SEC）
   - 所有原始數字都用藍色輸入
   - 在備註區記錄來源

3. **建立公式**（30 分鐘）
   - 從簡單的比率開始（利潤率）
   - 再進展到倍數（EV/Revenue）
   - 加上交叉檢查（利潤率合理嗎？）

4. **加入統計量**（15 分鐘）
   - 把公式結構複製到所有欄位
   - 確認範圍正確（B7:B9，不是 B7:B10）
   - 檢查四分位數的邏輯

5. **品質管控**（30 分鐘）
   - 執行合理性檢查
   - 驗證公式參照
   - 檢查有沒有 #DIV/0! 或 #REF! 錯誤
   - 對照已知的基準

6. **文件記錄**（15 分鐘）
   - 完成備註區
   - 加入資料來源
   - 定義方法論
   - 在分析上標註日期

### 專業小技巧
- **存成範本**：建一次，永遠重複使用
- **用顏色標示離群值**：對超過 2 個標準差的值用條件式格式
- **連結到來源檔案**：超連結到 Bloomberg 截圖或 SEC 申報文件
- **版本控制**：存成「Comps_v1_2024-12-15」，日期要清楚
- **協作檢閱**：請別人檢查你的公式

### Excel 格式檢查清單（選用：依使用者偏好調整）
- [ ] 字型設為使用者偏好的樣式（預設：Times New Roman，資料 11pt、標題 12pt）
- [ ] 區塊標題依使用者的範本設定格式（預設：深藍 #17365D 搭配白色粗體文字）
- [ ] 欄位標題依使用者的範本設定格式（預設：淺藍/灰 #D9E2F3 搭配黑色粗體文字）
- [ ] 統計量列依使用者的範本設定格式（預設：淺灰 #F2F2F2）
- [ ] 不套用邊框（乾淨、簡約的外觀）
- [ ] **欄寬設為統一/均等的寬度**（呈現乾淨、專業的外觀）
- [ ] **列高設為一致的高度**（資料列通常 20-25pt）
- [ ] 數字設定適當的小數精度和千分位
- [ ] **所有指標置中對齊**，看起來乾淨一致
- [ ] **公司資料和統計量列之間留一個空白列做分隔**
- [ ] **不要另外加 "SECTOR STATISTICS" 或 "VALUATION STATISTICS" 的標題列**
- [ ] **每個寫死的輸入儲存格都有註解，內容是：(1) 確切的資料來源，或 (2) 假設的說明**
- [ ] **在適用的儲存格加上超連結**（SEC 申報文件、資料提供者頁面、報告）

---

## 第 8 節：範本版面範例

**簡單版本（從這裡開始）：**
```
┌─────────────────────────────────────────────────────────────┐
│ TECHNOLOGY - COMPARABLE COMPANY ANALYSIS                    │
│ Microsoft • Alphabet • Amazon                               │
│ As of Q4 2024 | All figures in USD Millions                │
├─────────────────────────────────────────────────────────────┤
│ OPERATING METRICS                                           │
├──────────┬─────────┬─────────┬──────────┬──────────────────┤
│ Company  │ Revenue │ Growth  │ Gross    │ EBITDA  │ EBITDA │
│          │ (LTM)   │ (YoY)   │ Margin   │ (LTM)   │ Margin │
├──────────┼─────────┼─────────┼──────────┼─────────┼────────┤
│ MSFT     │ 261,400 │ 12.3%   │ 68.7%    │ 205,100 │ 78.4%  │
│ GOOGL    │ 349,800 │ 11.8%   │ 57.9%    │ 239,300 │ 68.4%  │
│ AMZN     │ 638,100 │ 10.5%   │ 47.3%    │ 152,600 │ 23.9%  │
│          │         │         │          │         │        │ [blank row]
│ Median   │ =MEDIAN │ =MEDIAN │ =MEDIAN  │ =MEDIAN │=MEDIAN │
│ 75th %   │ =QUART  │ =QUART  │ =QUART   │ =QUART  │=QUART  │
│ 25th %   │ =QUART  │ =QUART  │ =QUART   │ =QUART  │=QUART  │
├─────────────────────────────────────────────────────────────┤
│ VALUATION MULTIPLES                                         │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│ Company  │ Mkt Cap  │ EV       │ EV/Rev   │ EV/EBITDA │ P/E│
├──────────┼──────────┼──────────┼──────────┼───────────┼────┤
│ MSFT     │3,550,000 │3,530,000 │ 13.5x    │ 17.2x     │36.0│
│ GOOGL    │2,030,000 │1,960,000 │  5.6x    │  8.2x     │24.5│
│ AMZN     │2,226,000 │2,320,000 │  3.6x    │ 15.2x     │58.3│
│          │          │          │          │           │    │ [blank row]
│ Median   │ =MEDIAN  │ =MEDIAN  │ =MEDIAN  │ =MEDIAN   │=MED│
│ 75th %   │ =QUART   │ =QUART   │ =QUART   │ =QUART    │=QRT│
│ 25th %   │ =QUART   │ =QUART   │ =QUART   │ =QUART    │=QRT│
└──────────┴──────────┴──────────┴──────────┴───────────┴────┘
```

**需要時才增加複雜度：**
- 如果季節性重要，同時放季度和 LTM
- 如果現金創造是核心故事，加入 FCF 指標
- 納入產業特有的指標（例如 SaaS 的 Rule of 40）
- 如果公司超過 5 家，多加幾列統計量

---

## 第 9 節：依產業的額外項目（選用）

只有在這些對你的分析很關鍵時才加。大部分 comps 只用核心指標就夠了。

**軟體/SaaS：**
相關時加入：ARR、Net Dollar Retention、Rule of 40

**金融服務：**
相關時加入：ROE、Net Interest Margin、Efficiency Ratio

**電商：**
相關時加入：GMV、Take Rate、Active Buyers

**醫療保健：**
相關時加入：R&D/Revenue、管線價值、專利時程

**製造：**
相關時加入：Asset Turnover、Inventory Turns、Backlog

---

## 第 10 節：警訊與警告徵兆

### 資料品質問題
🚩 時間期間不一致（季度和年度混用）  
🚩 缺少資料卻沒有解釋  
🚩 不同資料來源之間差異很大（誤差 >10%）

### 估值警訊
🚩 EBITDA 為負的公司卻用 EBITDA 倍數來估值（應該改用營收倍數）  
🚩 P/E 超過 100x，卻沒有超高成長的故事  
🚩 利潤率對這個產業來說不合理

### 可比性問題
🚩 會計年度結束日不同（會造成時間點的問題）  
🚩 純業者和集團混在一起  
🚩 把商業模式明顯不同的公司標成「comps」

**有疑慮就排除該公司。**3 個完美的可比公司，勝過 6 個有疑問的。

---

## 第 11 節：公式參考指南

### 必備的 Excel 公式
```excel
// 統計函數
=AVERAGE(range)          // 簡單平均數
=MEDIAN(range)           // 中位數
=QUARTILE(range, 1)      // 25th percentile
=QUARTILE(range, 3)      // 75th percentile
=MAX(range)              // 最大值
=MIN(range)              // 最小值
=STDEV.P(range)          // 標準差

// 財務計算
=B7/C7                   // 簡單比率（利潤率）
=SUM(B7:B9)/3            // 多家公司的平均
=IF(B7>0, C7/B7, "N/A")  // 條件式計算
=IFERROR(C7/D7, 0)       // 處理除以零

// 跨工作表參照
='Sheet1'!B7             // 參照另一個工作表
=VLOOKUP(A7, Table1, 2)  // 從資料表查詢
=INDEX(MATCH())          // 進階查詢

// 格式化
=TEXT(B7, "0.0%")        // 格式化為百分比
=TEXT(C7, "#,##0")       // 千分位
```

### 常見的比率公式
```excel
Gross Margin = Gross Profit / Revenue
EBITDA Margin = EBITDA / Revenue
FCF Margin = Free Cash Flow / Revenue
FCF Conversion = FCF / Operating Cash Flow
ROE = Net Income / Shareholders' Equity
ROA = Net Income / Total Assets
Asset Turnover = Revenue / Total Assets
Debt/Equity = Total Debt / Shareholders' Equity
```

---

## 核心原則摘要

1. **結構帶出洞見**：對的標題會逼你想對的事
2. **少即是多**：5-10 個重要的指標，勝過 20 個不重要的
3. **依你的問題選擇指標**：估值分析 ≠ 效率分析
4. **統計量顯示模式**：中位數/四分位數比平均數揭露更多
5. **透明勝過複雜**：用人人都懂的簡單公式
6. **可比性最重要**：寧可排除，也不要硬塞一個不好的可比公司
7. **記錄你的選擇**：在備註區說明選了哪些指標、為什麼

---

## 輸出檢查清單

交付 comp 分析之前，確認：
- [ ] 所有公司都真正可比較
- [ ] 資料來自一致的時間期間
- [ ] 單位有清楚標示（百萬/十億）
- [ ] 公式參照的是儲存格，不是寫死的值
- [ ] **所有寫死的輸入儲存格都有註解，內容是：(1) 附出處的確切資料來源，或 (2) 附解釋的清楚假設**
- [ ] **在相關處加上超連結**（SEC EDGAR 申報文件、Bloomberg 頁面、研究報告）
- [ ] 統計量至少包含 5 個指標（Max、75th、Med、25th、Min）
- [ ] 備註區記錄了來源和方法論
- [ ] 視覺格式遵循慣例（藍色 = 輸入，黑色 = 公式）
- [ ] 合理性檢查通過（利潤率合乎邏輯、倍數合理）
- [ ] 日期標記是最新的（"As of [Date]"）
- [ ] 公式稽核顯示沒有錯誤（#DIV/0!、#REF!、#N/A）

---

## 持續改進

完成 comp 分析之後，問自己：
1. 統計量有沒有揭露出意料之外的洞見？
2. 有沒有資料缺口限制了分析？
3. 利害關係人有沒有要求你沒放進去的指標？
4. 實際花的時間，跟應該花的時間比起來如何？
5. 下次怎麼做會更有用？

最好的 comp 分析會隨著每次迭代而演進。把範本存起來，從回饋中學習，並根據決策者實際會用到的東西來調整結構。
