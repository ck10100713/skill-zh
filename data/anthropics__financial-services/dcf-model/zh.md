---
name: dcf-model
description: 為股票估值建立真正的 DCF（現金流量折現）模型。從 SEC 申報文件和分析師報告取得財務資料，建立完整的現金流預測與正確的 WACC 計算，進行敏感度分析，並輸出附有執行摘要的專業 Excel 模型。當使用者需要用 DCF 方法為公司估值、要求內在價值分析、或要求附帶成長預測和終值計算的詳細財務建模時使用。
---

# DCF 模型建構器

## 概覽

這個 skill 依投資銀行標準建立機構等級的股票估值 DCF 模型。每次分析都會產出詳細的 Excel 模型（敏感度分析放在 DCF 工作表的底部）。

## 工具

- 預設使用使用者提供的所有資訊，以及可用的 MCP 伺服器來取得資料。

## 關鍵限制：先讀這些

這些限制適用於整個 DCF 模型建構過程。開始前先檢視：

**環境：Office JS vs Python/openpyxl：**
- **如果在 Excel 裡執行（Office Add-in / Office JS 環境）：** 直接使用 Office JS，不要用 Python/openpyxl。用 `range.formulas = [["=D19*(1+$B$8)"]]` 寫公式。不需要另外的重算步驟，Excel 原生計算。用 `range.format.*` 設定樣式。一樣適用「公式優先於寫死數值」的規則：衍生儲存格要設 `.formulas`，絕對不要設 `.values`。
- **如果是產生獨立的 .xlsx 檔案（沒有即時 Excel session）：** 照下面的說明用 Python/openpyxl，並在交付前執行 `recalc.py`。
- 這個 skill 其餘部分使用 openpyxl 範例，在 Office JS 環境下就轉換成 Office JS 的 API 呼叫，但所有原則（公式字串、儲存格註解、段落檢查點、敏感度表迴圈）一體適用。

**⚠️ Office JS 合併儲存格的陷阱：** 用合併儲存格建立段落標題時，不要先呼叫 `.merge()` 再對合併後的範圍設 `.values`，Office JS 仍會回報該範圍的原始尺寸，並丟出 `InvalidArgument: The number of rows or columns in the input array doesn't match the size or dimensions of the range`。正確做法：只把值寫進左上角的儲存格，再合併並格式化整個範圍：

```js
// 錯誤：會丟 InvalidArgument：
const hdr = ws.getRange("A7:H7");
hdr.merge();
hdr.values = [["MARKET DATA & KEY INPUTS"]];  // 1×1 陣列 vs 1×8 範圍 → 失敗

// 正確：先把值寫進單一儲存格，再合併並格式化範圍：
ws.getRange("A7").values = [["MARKET DATA & KEY INPUTS"]];
const hdr = ws.getRange("A7:H7");
hdr.merge();
hdr.format.fill.color = "#1F4E79";
hdr.format.font.bold = true;
hdr.format.font.color = "#FFFFFF";
```

這適用於 DCF 中每一個合併的段落標題（市場資料、情境區塊、現金流預測、終值、估值摘要、敏感度表）。

**公式優先於寫死數值（沒得商量）：**
- 每一個預測、利潤率、折現因子、現值（PV）和敏感度儲存格，都「必須」是即時的 Excel 公式，絕對不能是在 Python 裡算好再寫成數字的值
- 使用 openpyxl 時：`ws["D20"] = "=D19*(1+$B$8)"` 是正確的；`ws["D20"] = calculated_revenue` 是錯的
- 唯一允許寫死的數字是：(1) 原始歷史輸入、(2) 假設驅動因子（成長率、WACC 輸入、終端 g）、(3) 目前市場資料（股價、負債餘額）
- 如果你發現自己在 Python 裡計算東西然後把結果寫進去，停下來。使用者改了假設，模型就必須跟著變動。

**與使用者逐步驗證（不要從頭建到尾）：**
- 資料取得之後 → 給使用者看原始輸入區塊（營收、利潤率、股數、淨負債），確認後才做預測
- 營收預測之後 → 給使用者看預測的營業收入和成長率，確認後才建利潤率
- FCF 建好之後 → 給使用者看完整的 FCF 明細，確認邏輯後才計算 WACC
- WACC 之後 → 給使用者看計算過程和輸入，確認後才折現
- 終值 + 現值之後 → 給使用者看股權橋接（EV → 股權價值 → 每股），確認後才做敏感度表
- 每個階段都要抓錯，在敏感度表都建好之後才發現利潤率假設有誤，代表下游全部要重建

**敏感度表：**
- **使用奇數的列數和欄數**（標準：5×5，有時 7×7），這保證有真正的中心儲存格
- **中心儲存格 = base case。** 建立軸值，讓中間那一列的標題和中間那一欄的標題，精確等於模型實際的假設（例如 base WACC = 9.0%，中間列就是 9.0%；終端 g = 3.0%，中間欄就是 3.0%）。中心儲存格的輸出因此必須等於模型實際的隱含股價，這是確認表格建對了的檢查。
- **凸顯中心儲存格**：用中藍填色（`#BDD7EE`）加粗體字，讓人一眼就看出哪個儲存格是 base case。
- 用完整的 DCF 重算公式填滿所有儲存格（通常是 3 張表 × 25 格 = 75 格）
- 用 openpyxl 迴圈（或 Office JS 迴圈）以程式方式寫入公式
- 不要佔位文字、不要線性近似、不要任何需要手動的步驟
- 每個儲存格都必須針對該假設組合，重新計算完整的 DCF

**儲存格註解：**
- 每建立一個寫死的值，就同時加上儲存格註解
- 格式："Source: [System/Document], [Date], [Reference], [URL if applicable]"
- 每一個藍色輸入，在進入下一段之前都必須有註解
- 不要延到最後，也不要寫 "TODO: add source"

**模型版面規劃：**
- 在寫任何公式之前，先定義所有段落的列位置
- 先寫所有標題和標籤
- 第二步寫所有段落分隔線和空白列
- 然後用鎖定的列位置寫公式
- 建立公式後立刻測試

**公式重算：**
- 交付前執行 `python recalc.py model.xlsx 30`
- 修正所有錯誤，直到狀態為 "success"
- 必須零公式錯誤（#REF!、#DIV/0!、#VALUE! 等）

**情境區塊：**
- 為 Bear/Base/Bull 情境建立獨立的區塊
- 在每個區塊內，把假設橫向攤開在各預測年度
- 使用 IF 公式：`=IF($B$6=1,[Bear cell],IF($B$6=2,[Base cell],[Bull cell]))`
- 驗證公式參照了正確的情境區塊儲存格

## DCF 流程工作流程

### 步驟 1：資料取得與驗證

從 MCP 伺服器、使用者提供的資料和網路取得資料。

**資料來源優先順序：**
1. **MCP 伺服器**（若有設定）：來自像 Daloopa 這類提供者的結構化財務資料
2. **使用者提供的資料**：他們研究得來的歷史財務資料
3. **Web Search/Fetch**：需要時取得目前價格、beta、負債和現金

**驗證 Checklist：**
- 驗證淨負債 vs 淨現金（對估值至關重要）
- 確認稀釋後流通在外股數（檢查近期的買回／增發）
- 驗證歷史利潤率與商業模式一致
- 把營收成長率與產業基準交叉核對
- 驗證稅率合理（通常為 21 到 28%）

### 步驟 2：歷史分析（3 到 5 年）

分析並記錄：
- **營收成長趨勢**：計算 CAGR，找出驅動因素
- **利潤率演變**：追蹤毛利率、EBIT 利潤率、FCF 利潤率
- **資本密集度**：D&A 和 CapEx 占營收的百分比
- **營運資金效率**：NWC 變動占營收成長的百分比
- **報酬指標**：ROIC、ROE 趨勢

建立摘要表，顯示：
```
Historical Metrics (LTM):
Revenue: $X million
Revenue growth: X% CAGR
Gross margin: X%
EBIT margin: X%
D&A % of revenue: X%
CapEx % of revenue: X%
FCF margin: X%
```

### 步驟 3：建立營收預測

**方法：**
1. 從最新的實際營收開始（LTM 或最近的會計年度）
2. 對每個預測年度套用成長率
3. 同時顯示金額和計算出的成長 %

**成長率框架：**
- 第 1 到 2 年：較高的成長，反映近期的能見度
- 第 3 到 4 年：逐漸向產業平均放緩
- 第 5 年以後：趨近終端成長率

**公式結構：**
- Revenue(Year N) = Revenue(Year N-1) × (1 + Growth Rate)
- Growth %(Year N) = Revenue(Year N) / Revenue(Year N-1) - 1

**三情境做法：**
```
Bear Case: Conservative growth (e.g., 8-12%)
Base Case: Most likely scenario (e.g., 12-16%)
Bull Case: Optimistic growth (e.g., 16-20%)
```

### 步驟 4：營業費用建模

**固定／變動成本分析：**

營業費用應該建模出真實的營運槓桿：
- **銷售與行銷**：依商業模式，通常為營收的 15 到 40%
- **研發**：科技公司通常為 10 到 30%
- **一般與行政**：通常為營收的 8 到 15%，隨公司規模擴大而顯現槓桿

**關鍵原則：**
- 所有百分比都以「營收」為基礎，不是毛利
- 建模營運槓桿：營收規模擴大時，% 應該下降
- S&M、R&D、G&A 保持獨立的項目
- 計算 EBIT = Gross Profit - Total OpEx

**利潤率擴張框架：**
```
Current State → Target State (Year 5)
Gross Margin: X% → Y% (justify based on scale, efficiency)
EBIT Margin: X% → Y% (result of revenue growth + opex leverage)
```

### 步驟 5：自由現金流計算

**依正確的順序建立 FCF：**

```
EBIT
(-) Taxes (EBIT × Tax Rate)
= NOPAT (Net Operating Profit After Tax)
(+) D&A (non-cash expense, % of revenue)
(-) CapEx (% of revenue, typically 4-8%)
(-) Δ NWC (change in working capital)
= Unlevered Free Cash Flow
```

**營運資金建模：**
- 以營收變動額（delta revenue）的百分比計算
- 典型範圍：營收變動的 -2% 到 +2%
- 負數 = 現金來源（營運資金釋放）
- 正數 = 現金使用（營運資金累積）

**維持性 vs 成長性 CapEx：**
- 維持性 CapEx：維持目前營運（約占營收 2 到 3%）
- 成長性 CapEx：支持擴張（再加占營收 2 到 5%）
- 總 CapEx 應與公司的成長策略一致

### 步驟 6：資金成本（WACC）研究

**股權成本的 CAPM 方法：**

```
Cost of Equity = Risk-Free Rate + Beta × Equity Risk Premium

Where:
- Risk-Free Rate = Current 10-Year Treasury Yield
- Beta = 5-year monthly stock beta vs market index
- Equity Risk Premium = 5.0-6.0% (market standard)
```

**負債成本計算：**

```
After-Tax Cost of Debt = Pre-Tax Cost of Debt × (1 - Tax Rate)

Determine Pre-Tax Cost of Debt from:
- Credit rating (if available)
- Current yield on company bonds
- Interest expense / Total Debt from financials
```

**資本結構權重：**

```
Market Value Equity = Current Stock Price × Shares Outstanding
Net Debt = Total Debt - Cash & Equivalents
Enterprise Value = Market Cap + Net Debt

Equity Weight = Market Cap / Enterprise Value
Debt Weight = Net Debt / Enterprise Value

WACC = (Cost of Equity × Equity Weight) + (After-Tax Cost of Debt × Debt Weight)
```

**特殊情況：**
- **淨現金部位**：如果現金 > 負債，淨負債是「負數」
  - 負債權重可能為負
  - WACC 計算要相應調整
- **沒有負債**：WACC = 股權成本

**典型的 WACC 範圍：**
- 大型股、穩定：7 到 9%
- 成長型公司：9 到 12%
- 高成長／高風險：12 到 15%

### 步驟 7：折現率套用（5 到 10 年預測）

**年中慣例（Mid-Year Convention）：**
- 假設現金流發生在年中
- 折現期間：0.5、1.5、2.5、3.5、4.5 等
- 折現因子 = 1 / (1 + WACC)^Period

**現值計算：**
```
For each projection year:
PV of FCF = Unlevered FCF × Discount Factor

Example (Year 1):
FCF = $1,000
WACC = 10%
Period = 0.5
Discount Factor = 1 / (1.10)^0.5 = 0.9535
PV = $1,000 × 0.9535 = $954
```

**預測期間的選擇：**
- **5 年**：多數分析的標準
- **7 到 10 年**：成長跑道較長的高成長公司
- **3 年**：成熟、穩定的事業

### 步驟 8：終值計算

**永續成長法（優先使用）：**

```
Terminal FCF = Final Year FCF × (1 + Terminal Growth Rate)
Terminal Value = Terminal FCF / (WACC - Terminal Growth Rate)

Critical Constraint: Terminal Growth < WACC (otherwise infinite value)
```

**終端成長率的選擇：**
- 保守：2.0 到 2.5%（GDP 成長率）
- 中等：2.5 到 3.5%
- 積極：3.5 到 5.0%（只適用於市場領導者）

**不要超過**：無風險利率或長期 GDP 成長

**退出倍數法（替代方案）：**
```
Terminal Value = Final Year EBITDA × Exit Multiple

Where Exit Multiple comes from:
- Industry comparable trading multiples
- Precedent transaction multiples
- Typical range: 8-15x EBITDA
```

**終值的現值：**
```
PV of Terminal Value = Terminal Value / (1 + WACC)^Final Period

Where Final Period accounts for timing:
5-year model with mid-year convention: Period = 4.5
```

**終值合理性檢查：**
- 應該占企業價值的 50 到 70%
- 如果 >75%，模型可能過度依賴終端假設
- 如果 <40%，檢查終端假設是否過於保守

### 步驟 9：企業價值到股權價值的橋接

**估值摘要結構：**

```
(+) Sum of PV of Projected FCFs = $X million
(+) PV of Terminal Value = $Y million
= Enterprise Value = $Z million

(-) Net Debt [or + Net Cash if negative] = $A million
= Equity Value = $B million

÷ Diluted Shares Outstanding = C million shares
= Implied Price per Share = $XX.XX

Current Stock Price = $YY.YY
Implied Return = (Implied Price / Current Price) - 1 = XX%
```

**關鍵調整：**
- **淨負債 = 總負債 - 現金及約當現金**
  - 如果為正：從 EV 中減去（降低股權價值）
  - 如果為負（淨現金）：加到 EV（提高股權價值）
- **使用稀釋後股數**：包含選擇權、RSU、可轉換證券
- **其他調整**（如適用）：
  - 少數股權
  - 退休金負債
  - 營業租賃義務

**估值輸出格式：**
```csv
Valuation Component,Amount ($M)
PV Explicit FCFs,X.X
PV Terminal Value,Y.Y
Enterprise Value,Z.Z
(-) Net Debt,A.A
Equity Value,B.B
,,
Shares Outstanding (M),C.C
Implied Price per Share,$XX.XX
Current Share Price,$YY.YY
Implied Upside/(Downside),+XX%
```

### 步驟 10：敏感度分析

在 DCF 工作表底部建立**三張敏感度表**，顯示估值如何隨不同假設而變化：

1. **WACC vs 終端成長率**：顯示企業價值對折現率和永續成長率的敏感度
2. **營收成長 vs EBIT 利潤率**：顯示營業收入成長和營運槓桿的影響
3. **Beta vs 無風險利率**：顯示對股權成本各組成項的敏感度

**實作方式**：這些是簡單的二維網格（不是 Excel 的「資料表」功能），每個儲存格裡都有公式。每個儲存格都必須針對該特定的假設組合，包含完整的 DCF 重算。關於用 openpyxl 以程式方式填滿全部 75 個儲存格的詳細要求，請見「關鍵限制」段落。

<correct_patterns>

這個段落包含建構 DCF 模型時要遵循的所有「正確」模式。

### 情境區塊選擇模式：照這個做法

**假設依每個情境分別組織成獨立的區塊：**

**關鍵結構：每個段落標題有三列：**

```csv
BEAR CASE ASSUMPTIONS (section header, merge cells across)
Assumption,FY1,FY2,FY3,FY4,FY5
Revenue Growth (%),12%,10%,9%,8%,7%
EBIT Margin (%),45%,44%,43%,42%,41%

BASE CASE ASSUMPTIONS (section header, merge cells across)
Assumption,FY1,FY2,FY3,FY4,FY5
Revenue Growth (%),16%,14%,12%,10%,9%
EBIT Margin (%),48%,49%,50%,51%,52%

BULL CASE ASSUMPTIONS (section header, merge cells across)
Assumption,FY1,FY2,FY3,FY4,FY5
Revenue Growth (%),20%,18%,15%,13%,11%
EBIT Margin (%),50%,51%,52%,53%,54%
```

**每個情境區塊「必須」有一列欄位標題**，緊接在段落標題的下方，顯示預測年度（FY2025E、FY2026E 等）。沒有這個，使用者就看不出哪個假設值對應哪一年。

**如何參照假設：建立一個彙整欄：**
1. 情境選擇儲存格（例如 B6）包含 1=Bear、2=Base 或 3=Bull
2. 建立一個彙整欄，用 INDEX 或 OFFSET 公式從正確的情境區塊取值
3. 預測公式參照彙整欄（乾淨的儲存格參照）
4. 每個情境區塊在各預測年度都包含完整的一組 DCF 假設

**建議的彙整欄模式（使用 INDEX）：**
`=INDEX(B10:D10, 1, $B$6)`

**不要這樣做：到處散落 IF 敘述：**
`=IF($B$6=1,[Bear block cell],IF($B$6=2,[Base block cell],[Bull block cell]))`

彙整欄的做法把邏輯集中，讓模型更容易稽核。

### 正確的營收預測模式

**建立一個含 INDEX 公式的彙整欄，再在預測中參照它：**

**步驟 1：FY1 成長的彙整欄：**
`=INDEX([Bear FY1 growth]:[Bull FY1 growth], 1, $B$6)`

**步驟 2：營收預測參照彙整欄：**
`Revenue Year 1: =D29*(1+$E$10)`

其中：
- D29 = 前一年營收
- $E$10 = FY1 成長的彙整欄儲存格（包含 INDEX 公式）
- $B$6 = 情境選擇器（1=Bear、2=Base、3=Bull）

**這個做法比在每個預測公式裡嵌入 IF 敘述乾淨**，也更容易稽核目前用的是哪個情境的假設。

### 正確的 FCF 公式模式

**使用含 INDEX 公式的彙整欄，再在 FCF 計算中參照它們：**

**彙整欄做法：**
```csv
Item,Formula,Reference
D&A,=E29*$E$21,$E$21 = consolidation column for D&A %
CapEx,=E29*$E$22,$E$22 = consolidation column for CapEx %
Δ NWC,=(E29-D29)*$E$23,$E$23 = consolidation column for NWC %
Unlevered FCF,=E57+E58-E60-E62,E57=NOPAT E58=D&A E60=CapEx E62=Δ NWC
```

**每個彙整欄儲存格都包含一個 INDEX 公式**，依情境選擇器從適當的情境區塊取值。這讓預測公式保持乾淨、可稽核。

寫公式之前，先確認情境區塊的列位置，並設定好彙整欄。

### 正確的儲存格註解格式

**每個寫死的值都需要這個格式：**

"Source: [System/Document], [Date], [Reference], [URL if applicable]"

**範例：**
```csv
Item,Source Comment
Stock price,Source: Market data script 2025-10-12 Close price
Shares outstanding,Source: 10-K FY2024 Page 45 Note 12
Historical revenue,Source: 10-K FY2024 Page 32 Consolidated Statements
Beta,Source: Market data script 2025-10-12 5-year monthly beta
Consensus estimates,Source: Management guidance Q3 2024 earnings call
```

### 正確的假設表結構

**關鍵：每個情境區塊需要三個結構元素：**

1. **段落標題列**（合併儲存格）：例如 "BEAR CASE ASSUMPTIONS"
2. **顯示年度的欄位標題列**：這是必要的，不准跳過
3. **資料列**，放假設值

**結構：**
```csv
BEAR CASE ASSUMPTIONS (section header - merge across columns A:G)
Assumption,FY1,FY2,FY3,FY4,FY5
Revenue Growth (%),X%,X%,X%,X%,X%
EBIT Margin (%),X%,X%,X%,X%,X%
Terminal Growth,X%,,,,
WACC,X%,,,,

BASE CASE ASSUMPTIONS (section header - merge across columns A:G)
Assumption,FY1,FY2,FY3,FY4,FY5
Revenue Growth (%),X%,X%,X%,X%,X%
EBIT Margin (%),X%,X%,X%,X%,X%
Terminal Growth,X%,,,,
WACC,X%,,,,

BULL CASE ASSUMPTIONS (section header - merge across columns A:G)
Assumption,FY1,FY2,FY3,FY4,FY5
Revenue Growth (%),X%,X%,X%,X%,X%
EBIT Margin (%),X%,X%,X%,X%,X%
Terminal Growth,X%,,,,
WACC,X%,,,,
```

**沒有顯示預測年度（FY2025E、FY2026E 等）的欄位標題列，使用者就看不出哪個假設值對應哪一年。這一列是強制的。**

**然後建立一個彙整欄**（通常是右邊緊鄰的那一欄），用 INDEX 公式依情境選擇器，從選定的情境區塊取值。你的預測公式參照的就是這個彙整欄。

### 正確的列規劃流程

**1. 先寫所有標題和標籤：**
```csv
Row,Content
1,[Company Name] DCF Model
2,Ticker | Date | Year End
4,Case Selector
7,KEY ASSUMPTIONS
26,Assumption headers
27-31,Growth assumptions
...,...
```

**2. 寫所有段落分隔線和空白列**

**3. 然後用鎖定的列位置寫公式**

**4. 建立公式後立刻測試**

**把它想成蓋房子：**
- 好：先打地基，再蓋牆（結構穩固）
- 壞：先蓋牆，再打地基（牆會倒）

**Excel 版本：**
- 好：先加標題，再寫公式（公式穩定）
- 壞：先寫公式，再加標題（公式壞掉）

### 正確的敏感度表實作

**重要**：這些不是 Excel 的「資料表（Data Table）」功能。這些是用 openpyxl 寫一般公式的簡單網格。沒錯，這代表總共約 75 個公式（3 張表 × 每張 25 格），但這很直接，而且是必要的。

**以公式程式化填入：**

每張敏感度表都必須完整填入公式，針對每一種假設組合重新計算隱含股價。**不要使用 Excel 的資料表功能**（它需要手動介入，無法透過 openpyxl 自動化）。

**實作做法：具體範例：**

**表格結構：5×5 網格（奇數維度，base case 置中）：**

如果模型的 base WACC = 9.0%、base 終端成長 = 3.0%，就圍繞這些值對稱地建立軸：

```csv
WACC vs Terminal Growth,  2.0%,  2.5%,  3.0%,  3.5%,  4.0%
              8.0%,       [fml], [fml], [fml], [fml], [fml]
              8.5%,       [fml], [fml], [fml], [fml], [fml]
              9.0%,       [fml], [fml], [★  ], [fml], [fml]   ← middle row = base WACC
              9.5%,       [fml], [fml], [fml], [fml], [fml]
             10.0%,       [fml], [fml], [fml], [fml], [fml]
                                   ↑
                          middle col = base terminal g
```

**★ = 中心儲存格。** 它的公式輸出「必須」等於模型實際的隱含股價（來自估值摘要）。對這個儲存格套用中藍填色（`#BDD7EE`）和粗體字，讓 base case 在視覺上有錨點。

**軸值的規則：** `axis_values = [base - 2*step, base - step, base, base + step, base + 2*step]`，以 base 為中心對稱，奇數個數保證有中心。

**公式模式：儲存格 B88（WACC=8.0%、終端成長=2.0%）：**

B88 的公式應該用下列值重新計算隱含價格：
- 來自列標題的 WACC：`$A88`（8.0%）
- 來自欄標題的終端成長：`B$87`（2.0%）

**建議做法：** 參照主要的 DCF 計算，但替換這些值。

**範例公式結構：**
`=([SUM of PV FCFs using $A88 as discount rate] + [Terminal Value using B$87 as growth rate and $A88 as WACC] - [Net Debt]) / [Shares]`

**關鍵：為 5x5 網格中「每一個」儲存格寫公式（每張表 25 格，總共 75 格）。** 用 openpyxl 以迴圈程式化地寫這些公式。不准跳過這一步，也不准留下佔位文字。

**Python 實作模式：**
```python
# 填入敏感度表的虛擬碼
for row_idx, wacc_value in enumerate(wacc_range):
    for col_idx, term_growth_value in enumerate(term_growth_range):
        # 建立使用 wacc_value 和 term_growth_value 的公式
        formula = f"=<DCF recalc using {wacc_value} and {term_growth_value}>"
        ws.cell(row=start_row+row_idx, column=start_col+col_idx).value = formula
```

**敏感度表在模型一打開時就必須能運作，不需要使用者做任何手動步驟。**

</correct_patterns>

<common_mistakes>

這個段落包含建構 DCF 模型時要避免的所有「錯誤」模式。

### 錯誤：簡化的敏感度表近似值或佔位文字

**不要使用線性近似：**

```
// 錯誤：線性近似
B97: =B88*(1+(0.096-0.116))    // 假設是線性關係

// 錯誤：除法捷徑
B105: =B88/(1+(E48-0.07))      // 沒有重新計算完整的 DCF
```

**不要留下佔位文字：**
```
// 錯誤：佔位備註
"Note: Use Excel Data Table feature (Data → What-If Analysis → Data Table) to populate sensitivity tables."

// 錯誤：空白儲存格
[leaving cells blank because "this is complex"]
```

**不要搞混術語：**
- ❌「敏感度表需要 Excel 的 Data Table 功能」（不對，那是我們不能用的特定 Excel 工具）
- ✅「敏感度表是每個儲存格都有公式的簡單網格」（對，這是我們要建的）

**為什麼這些捷徑是錯的：**
- 線性近似公式並沒有真的重新計算 DCF，只是套用簡單的數學調整
- 這些關係不是線性的，所以結果不準確
- 佔位文字需要使用者手動介入
- 模型交付時無法立即使用
- 不專業，也不能直接交給客戶
- 空白儲存格 = 交付物不完整

**要拒絕的常見合理化藉口：**
「寫 75 個以上的公式感覺很複雜，所以我留一則備註，讓使用者自己手動完成。」

**現實：** 用 Python 的 openpyxl 寫迴圈，寫 75 個公式很直接。每個公式都遵循同一個模式，只要替換列／欄的值。這是交付物必要的一部分。

**正確做法：** 每個敏感度儲存格都填入公式，針對該特定的假設組合重新計算完整的 DCF

### 錯誤：缺少儲存格註解

**不要這樣做：**
- 建立所有寫死的輸入卻沒有註解
- 心想「我晚點再補」
- 寫 "TODO: add source"
- 讓藍色輸入沒有文件說明

**為什麼是錯的：**
- 無法驗證資料來自哪裡
- 不符合 xlsx skill 的要求
- 無法通過稽核
- 事後修補浪費時間

**正確做法：** 每建立一個寫死的值，就同時加上儲存格註解

### 錯誤：公式的列參照跑掉

**症狀：**
FCF 區段參照了錯誤的假設列：
`D&A:  =E29*$E$34    // 應該是 $E$21，但參照到錯的列`
`CapEx: =E29*$E$41   // 應該是 $E$22，但列位移了`

**為什麼會發生：**
1. 先寫了公式
2. 然後插入標題
3. 所有列參照都位移了
4. 現在公式指向錯的儲存格 → #REF! 錯誤

**正確做法：** 先鎖定列版面，再寫公式

### 錯誤：各情境的每個假設只用單獨一列

**不要把假設這樣結構化：**
```csv
Assumption,Bear,Base,Bull
Revenue Growth FY1,10%,13%,16%
Revenue Growth FY2,9%,12%,15%
```
這種垂直版面很難看出每個情境內各年度的演進。

**為什麼是錯的：**
- 很難看出每個情境內假設跨年度的演變
- 更難在完整的預測期間比較各情境的假設
- 檢視情境邏輯時比較不直覺

**正確做法：**
- 為每個情境（Bear、Base、Bull）建立獨立的區塊
- 在每個區塊內，把假設橫向攤開在各預測年度
- 這樣每個情境的假設比較容易當作一個完整的組合來檢視

### 錯誤：沒有框線

**不要交付沒有框線的模型：**
- 沒有段落劃分
- 所有儲存格混在一起
- 難以閱讀且不專業

**為什麼是錯的：**
- 不能直接交給客戶
- 難以瀏覽
- 看起來很業餘

**正確做法：** 在所有主要段落周圍加上框線

### 錯誤：字體顏色錯誤，或沒有區分字體顏色

**不要這樣做：**
- 所有文字都是黑色
- 只用填色（沒有字體顏色的變化）
- 搞混哪些儲存格是藍色、哪些是黑色

**為什麼是錯的：**
- 無法區分輸入和公式
- 稽核變得不可能
- 違反 xlsx skill 的要求

**正確做法：** 所有寫死的輸入用藍色文字，所有公式用黑色文字，工作表連結用綠色

### 錯誤：營業費用以毛利為基礎

**不要這樣做：**
`S&M: =E33*0.15    // E33 = Gross Profit (WRONG)`

**為什麼是錯的：**
- 營業費用隨營收擴張，不是隨毛利
- 會產生不切實際的利潤率演變
- 企業實際上不是這樣運作的

**正確做法：**
`S&M: =E29*0.15    // E29 = Revenue (CORRECT)`

### 前 5 大錯誤摘要

1. **公式列參照跑掉** → 在寫公式之前，先定義所有列位置
2. **缺少儲存格註解** → 建立儲存格時就加註解，不要等到最後
3. **簡化的敏感度表** → 用完整的 DCF 重算公式填滿所有儲存格，不要用近似值
4. **情境區塊參照錯誤** → 確保 IF 公式從正確的 Bear/Base/Bull 區塊取值
5. **沒有框線** → 加上專業的段落框線，讓外觀可直接交給客戶

此外，也要留意這些錯誤：

### WACC 計算錯誤
- 在資本結構中混用帳面價值和市場價值
- 不當地使用股權 beta，而非資產／去槓桿 beta
- 對負債成本套用錯誤的稅率
- 無風險利率不正確（必須使用目前的 10 年期公債）
- 沒有針對淨負債 vs 淨現金部位做調整

### 成長假設缺陷
- 終端成長 > WACC（會產生無限大的價值）
- 預測成長率與歷史表現不一致
- 忽略產業成長的限制
- 營收成長與單位經濟（unit economics）不一致
- 沒有營運上的依據就假設利潤率擴張

### 終值錯誤
- 使用錯誤的成長方法（永續 vs 退出倍數）
- 終值 > 企業價值的 80%（顯示過度依賴）
- 終端利潤率與穩態假設不一致
- 終值使用錯誤的折現期間

### 現金流預測錯誤
- 營業費用以毛利而非營收為基礎
- D&A/CapEx 百分比與商業模式不符
- 營運資金變動沒有正確計算
- 各年度稅率不一致
- NOPAT 計算錯誤

**這些是最常見的錯誤。開始任何 DCF 建構之前，請重讀這個段落。**

</common_mistakes>

## Excel 檔案建立

**這個 skill 所有試算表操作都使用 `xlsx` skill。** xlsx skill 提供：
- 標準化的公式建構規則
- 數字格式慣例
- 透過 `recalc.py` 腳本自動重算公式
- 完整的錯誤檢查與驗證

這個 skill 建立的所有 Excel 檔案都必須遵循 xlsx skill 的要求，包括零公式錯誤和正確的重算。

## 品質評分標準

每個 DCF 模型都必須在下列項目上做到最好：
1. **符合現實的營收和利潤率假設**，以歷史表現為基礎
2. **適當的資金成本計算**，使用正確的 CAPM 方法
3. **全面的敏感度分析**，顯示估值區間
4. **清楚的終值計算**，附上佐證理由
5. **專業的模型結構**，能支援情境分析
6. **所有關鍵假設都有透明的文件說明**

## 輸入要求

### 最低必要輸入
1. **公司識別**：股票代號或公司名稱
2. **成長假設**：預測期間的營收成長率（或「使用共識」）
3. **選用參數**：
   - 預測期間（預設：5 年）
   - 情境案例（Bear/Base/Bull 的成長與利潤率假設）
   - 終端成長率（預設：2.5 到 3.0%）
   - 若不使用 CAPM，則提供特定的 WACC 輸入

## Excel 模型結構

### 工作表架構

建立**兩張工作表**：

1. **DCF**：主要估值模型，底部附敏感度分析
2. **WACC**：資金成本計算

**關鍵**：敏感度表放在 DCF 工作表的「底部」（不是獨立的工作表）。這樣能把所有估值輸出放在一起。

### 公式重算（強制）
建立或修改 Excel 模型之後，使用 xlsx skill 的 recalc.py 腳本**重算所有公式**：

```bash
python recalc.py [path_to_excel_file] [timeout_seconds]
```

範例：
```bash
python recalc.py AAPL_DCF_Model_2025-10-12.xlsx 30
```

這個腳本會：
- 使用 LibreOffice 重算所有工作表中的所有公式
- 掃描「所有」儲存格是否有 Excel 錯誤（#REF!、#DIV/0!、#VALUE!、#NAME?、#NULL!、#NUM!、#N/A）
- 回傳含錯誤位置和數量的詳細 JSON

**預期的輸出格式：**
```json
{
  "status": "success",           // 或 "errors_found"
  "total_errors": 0,              // 錯誤總數
  "total_formulas": 42,           // 檔案中的公式數量
  "error_summary": {}             // 只有在發現錯誤時才會出現
}
```

**如果發現錯誤**，輸出會包含細節：
```json
{
  "status": "errors_found",
  "total_errors": 2,
  "total_formulas": 42,
  "error_summary": {
    "#REF!": {
      "count": 2,
      "locations": ["DCF!B25", "DCF!C25"]
    }
  }
}
```

**修正所有錯誤**，並重新執行 recalc.py，直到狀態為 "success"，才能交付模型。

### 格式標準

**重要**：公式建構規則和數字格式慣例請遵循 xlsx skill。DCF skill 另外加上特定的視覺呈現標準。

**色彩配置：兩層**：

**第 1 層：字體顏色（xlsx skill 的強制要求）**
- **藍色文字（RGB: 0,0,255）**：所有寫死的輸入（股價、股數、歷史資料、假設）
- **黑色文字（RGB: 0,0,0）**：所有公式和計算
- **綠色文字（RGB: 0,128,0）**：連到其他工作表的連結（WACC 工作表的參照）

**第 2 層：填色：專業的藍／灰色盤（除非使用者另有指定，否則為預設）**
- **保持極簡**：填色只用藍和灰。不要加入綠、黃、橘或多種強調色。顏色太多的模型看起來很業餘。
- **預設填色色盤：**
  - **段落標題**：深藍（RGB: 31,78,121 / `#1F4E79`）背景配白色粗體字
  - **子標題／欄位標題**：淺藍（RGB: 217,225,242 / `#D9E1F2`）背景配黑色粗體字
  - **輸入儲存格**：淺灰（RGB: 242,242,242 / `#F2F2F2`）背景配藍色字體，或者想要最極簡的話，就白色背景配藍色字體
  - **計算儲存格**：白色背景配黑色字體
  - **輸出／摘要列**（每股價值、EV 等）：中藍（RGB: 189,215,238 / `#BDD7EE`）背景配黑色粗體字
- **就這樣：3 種藍 + 1 種灰 + 白。** 忍住不要再加。
- 使用者提供的範本或明確的顏色偏好，「一律」優先於這些預設值。

**兩層如何搭配運作：**
- 輸入儲存格：藍色字體 + 淺灰填色 = 「寫死的輸入」
- 公式儲存格：黑色字體 + 白色背景 = 「計算出的值」
- 工作表連結：綠色字體 + 白色背景 = 「來自另一張工作表的參照」
- 關鍵輸出：黑色粗體字 + 中藍填色 = 「這就是答案」

**字體顏色告訴你它是什麼（輸入／公式／連結）。填色告訴你你在哪裡（標題／資料／輸出）。**

### 框線標準（專業外觀的必要條件）

**粗框線**（1.5pt）包住主要段落：
- KEY INPUTS 段落
- PROJECTION ASSUMPTIONS 段落
- 5-YEAR CASH FLOW PROJECTION 段落
- TERMINAL VALUE 段落
- VALUATION SUMMARY 段落
- 每一張 SENSITIVITY ANALYSIS 表

**中等框線**（1pt）用於子段落之間：
- Company Details vs Historical Performance
- Growth Assumptions vs EBIT Margin vs FCF Parameters

**細框線**（0.5pt）包住資料表：
- 情境假設表（Bear | Base | Bull | Selected）
- 歷史 vs 預測的財務矩陣

**不加框線：** 表格內的個別儲存格（保持乾淨、好掃讀）

**框線是強制的**，沒有專業框線的模型不能直接交給客戶。

**數字格式**（遵循 xlsx skill 標準）：
- **年份**：格式化為文字字串（例如 "2024"，不是 "2,024"）
- **百分比**：`0.0%`（一位小數）
- **貨幣**：百萬用 `$#,##0`；每股用 `$#,##0.00`，標題一律要註明單位（"Revenue ($mm)"）
- **零**：用數字格式讓所有零顯示為 "-"（例如 `$#,##0;($#,##0);-`）
- **大數字**：`#,##0`，附千分位分隔符號
- **負數**：用括號 `(#,##0)`（不要用負號）

**儲存格註解（所有寫死的輸入強制要求）**：

依照 xlsx skill，所有寫死的值都必須有儲存格註解，記錄來源。格式："Source: [System/Document], [Date], [Reference], [URL if applicable]"

**關鍵**：建立儲存格時就加註解。不要延到最後。

### DCF 工作表詳細結構

**段落 1：標頭**
```csv
Row,Content
1,[Company Name] DCF Model
2,Ticker: [XXX] | Date: [Date] | Year End: [FYE]
3,Blank
4,Case Selector Cell (1=Bear 2=Base 3=Bull)
5,Case Name Display (formula: =IF([Selector]=1"Bear"IF([Selector]=2"Base""Bull")))
```

**段落 2：市場資料（不隨情境變動）**
```csv
Item,Value
Current Stock Price,$XX.XX
Shares Outstanding (M),XX.X
Market Cap ($M),[Formula]
Net Debt ($M),XXX [or Net Cash if negative]
```

**段落 3：DCF 情境假設**

為每個情境（Bear、Base、Bull）建立獨立的假設區塊，包含 DCF 專屬的假設（Revenue Growth %、EBIT Margin %、Tax Rate %、D&A % of Revenue、CapEx % of Revenue、NWC Change % of ΔRev、Terminal Growth Rate、WACC），橫向攤開在各預測年度。每個區塊都必須包含段落標題、顯示預測年度（FY1、FY2 等）的欄位標題列，以及資料列。確切的版面請見 `<correct_patterns>` 段落中的「正確的假設表結構」。

**段落 4：歷史與預測財務**

**參照一個從情境區塊取值的彙整欄（例如 "Selected Case"）**，不要在每個預測列散落 IF 公式。

```csv
Income Statement ($M),2020A,2021A,2022A,2023A,2024E,2025E,2026E
Revenue,XXX,XXX,XXX,XXX,[=E29*(1+$E$10)],[=F29*(1+$E$11)],[=G29*(1+$E$12)]
  % growth,XX%,XX%,XX%,XX%,[=E29/D29-1],[=F29/E29-1],[=G29/F29-1]
,,,,,,
Gross Profit,XXX,XXX,XXX,XXX,[=E29*E33],[=F29*F33],[=G29*G33]
  % margin,XX%,XX%,XX%,XX%,[=E33/E29],[=F33/F29],[=G33/G29]
,,,,,,
Operating Expenses:,,,,,,,
  S&M,XXX,XXX,XXX,XXX,[=E29*0.15],[=F29*0.14],[=G29*0.13]
  R&D,XXX,XXX,XXX,XXX,[=E29*0.12],[=F29*0.11],[=G29*0.10]
  G&A,XXX,XXX,XXX,XXX,[=E29*0.08],[=F29*0.07],[=G29*0.07]
  Total OpEx,XXX,XXX,XXX,XXX,[=E36+E37+E38],[=F36+F37+F38],[=G36+G37+G38]
,,,,,,
EBIT,XXX,XXX,XXX,XXX,[=E33-E39],[=F33-F39],[=G33-G39]
  % margin,XX%,XX%,XX%,XX%,[=E41/E29],[=F41/F29],[=G41/G29]
,,,,,,
Taxes,(XX),(XX),(XX),(XX),[=E41*$E$24],[=F41*$E$24],[=G41*$E$24]
  Tax rate,XX%,XX%,XX%,XX%,[=E43/E41],[=F43/F41],[=G43/G41]
,,,,,,
NOPAT,XXX,XXX,XXX,XXX,[=E41-E43],[=F41-F43],[=G41-G43]
```

**關鍵公式模式**：
- 營收成長：`=E29*(1+$E$10)`，其中 $E$10 是第 1 年成長的彙整欄
- 不要這樣：`=E29*(1+IF($B$6=1,$B$10,IF($B$6=2,$C$10,$D$10)))`

這個做法更乾淨、更容易稽核，並透過集中情境邏輯來避免公式錯誤。

**段落 5：自由現金流建構**

**關鍵**：驗證列參照指向「正確的」假設列。建立公式後立刻測試。

```csv
Cash Flow ($M),2020A,2021A,2022A,2023A,2024E,2025E,2026E
NOPAT,XXX,XXX,XXX,XXX,[=E45],[=F45],[=G45]
(+) D&A,XXX,XXX,XXX,XXX,[=E29*$E$21],[=F29*$E$21],[=G29*$E$21]
    % of Rev,XX%,XX%,XX%,XX%,[=E58/E29],[=F58/F29],[=G58/G29]
(-) CapEx,(XX),(XX),(XX),(XX),[=E29*$E$22],[=F29*$E$22],[=G29*$E$22]
    % of Rev,XX%,XX%,XX%,XX%,[=E60/E29],[=F60/F29],[=G60/G29]
(-) Δ NWC,(XX),(XX),(XX),(XX),[=(E29-D29)*$E$23],[=(F29-E29)*$E$23],[=(G29-F29)*$E$23]
    % of Δ Rev,XX%,XX%,XX%,XX%,[=E62/(E29-D29)],[=F62/(F29-E29)],[=G62/(G29-F29)]
,,,,,,
Unlevered FCF,XXX,XXX,XXX,XXX,[=E57+E58-E60-E62],[=F57+F58-F60-F62],[=G57+G58-G60-G62]
```

**列參照範例**（依版面規劃）：
- $E$21 = D&A % 假設（彙整欄，第 21 列）
- $E$22 = CapEx % 假設（彙整欄，第 22 列）
- $E$23 = NWC % 假設（彙整欄，第 23 列）
- E29 = 當年營收（第 29 列）
- E45 = 當年 NOPAT（第 45 列）

**寫公式之前**：確認這些列號與實際版面相符。先測試一欄，再複製到其他欄。

**段落 6：折現與估值**
```csv
DCF Valuation,2024E,2025E,2026E,2027E,2028E,Terminal
Unlevered FCF ($M),XXX,XXX,XXX,XXX,XXX,
Period,0.5,1.5,2.5,3.5,4.5,
Discount Factor,0.XX,0.XX,0.XX,0.XX,0.XX,
PV of FCF ($M),XXX,XXX,XXX,XXX,XXX,
,,,,,,
Terminal FCF ($M),,,,,,,XXX
Terminal Value ($M),,,,,,,XXX
PV Terminal Value ($M),,,,,,,XXX
,,,,,,
Valuation Summary ($M),,,,,,
Sum of PV FCFs,XXX,,,,,
PV Terminal Value,XXX,,,,,
Enterprise Value,XXX,,,,,
(-) Net Debt,(XX),,,,,
Equity Value,XXX,,,,,
,,,,,,
Shares Outstanding (M),XX.X,,,,,
IMPLIED PRICE PER SHARE,$XX.XX,,,,,
Current Stock Price,$XX.XX,,,,,
Implied Upside/(Downside),XX%,,,,,
```

### WACC 工作表結構

```csv
COST OF EQUITY CALCULATION,,
Risk-Free Rate (10Y Treasury),X.XX%,[Yellow input]
Beta (5Y monthly),X.XX,[Yellow input]
Equity Risk Premium,X.XX%,[Yellow input]
Cost of Equity,X.XX%,[Calculated blue]
,,
COST OF DEBT CALCULATION,,
Credit Rating,AA-,[Yellow input]
Pre-Tax Cost of Debt,X.XX%,[Yellow input]
Tax Rate,XX.X%,[Link to DCF sheet]
After-Tax Cost of Debt,X.XX%,[Calculated blue]
,,
CAPITAL STRUCTURE,,
Current Stock Price,$XX.XX,[Link to DCF]
Shares Outstanding (M),XX.X,[Link to DCF]
Market Capitalization ($M),"X,XXX",[Calculated]
,,
Total Debt ($M),XXX,[Yellow input]
Cash & Equivalents ($M),XXX,[Yellow input]
Net Debt ($M),XXX,[Calculated]
,,
Enterprise Value ($M),"X,XXX",[Calculated]
,,
WACC CALCULATION,Weight,Cost,Contribution
Equity,XX.X%,X.X%,X.XX%
Debt,XX.X%,X.X%,X.XX%
,,
WEIGHTED AVERAGE COST OF CAPITAL,X.XX%,[Green output]
```

**關鍵 WACC 公式：**
```
Market Cap = Price × Shares
Net Debt = Total Debt - Cash
Enterprise Value = Market Cap + Net Debt
Equity Weight = Market Cap / EV
Debt Weight = Net Debt / EV
WACC = (Cost of Equity × Equity Weight) + (After-tax Cost of Debt × Debt Weight)
```

### 敏感度分析（DCF 工作表底部）

**術語提醒**：「敏感度表」= 簡單的二維網格，有列標題、欄標題，每個資料儲存格裡都有公式。不是 Excel 的「資料表（Data Table）」功能（Data → What-If Analysis → Data Table）。你要用 openpyxl 在每個儲存格寫入一般的 Excel 公式。

**位置**：DCF 工作表的第 87 列以後（不是獨立的工作表）

**三張敏感度表，垂直堆疊：**

1. **WACC vs 終端成長**（第 87 到 100 列）：5x5 網格 = 25 個含公式的儲存格
2. **營收成長 vs EBIT 利潤率**（第 102 到 115 列）：5x5 網格 = 25 個含公式的儲存格
3. **Beta vs 無風險利率**（第 117 到 130 列）：5x5 網格 = 25 個含公式的儲存格

**要寫的公式總數：75**（這是必要的，不是選用的）

**關鍵**：所有敏感度表的儲存格，都必須用 openpyxl 以程式方式填入公式。不准使用線性近似的捷徑。不准留下佔位文字或手動步驟的備註。不准以「這很複雜」為由合理化留下空白儲存格，用 Python 迴圈來產生公式。

**表格設定：**
1. 建立含列／欄標題的表格結構（要測試的假設值）
2. 每一個資料儲存格都填入公式，該公式要：
   - 使用列標題的值（例如 WACC = 9.0%）
   - 使用欄標題的值（例如 Terminal Growth = 3.0%）
   - 以這些特定假設重新計算完整的 DCF
   - 回傳該情境的隱含股價
3. 交付時所有儲存格都必須含有可運作的公式
4. 以條件式格式設定儲存格：較高的值用綠色色階，較低的值用紅色色階
5. base case 儲存格用粗體
6. 表格之間留 1 到 2 個空白列

**不需要手動介入**：使用者打開檔案時，敏感度表就必須完全可運作。

## 情境選擇器實作

**三情境框架：**

### Bear Case
- 保守的營收成長（歷史區間的低端）
- 利潤率壓縮或沒有擴張
- 較高的 WACC（風險溢酬提高）
- 較低的終端成長率
- 較高的 CapEx 假設

### Base Case
- 共識或管理層 guidance 的營收成長
- 依營運槓桿的適度利潤率擴張
- 目前市場隱含的 WACC
- 與 GDP 一致的終端成長（2.5 到 3.0%）
- 標準的 CapEx 假設

### Bull Case
- 樂觀的營收成長（預測的高端）
- 顯著的利潤率擴張
- 較低的 WACC（風險溢酬降低）
- 較高的終端成長（3.5 到 5.0%）
- 降低 CapEx 密集度

**公式實作：**

**不要到處散落巢狀的 IF 公式。** 改為建立一個彙整欄，用 INDEX 或 OFFSET 公式從適當的情境區塊取值。

**建議模式（使用 INDEX）：**
`=INDEX(B10:D10, 1, $B$6)`，其中 `B10:D10` = Bear/Base/Bull 的值，`1` = 列偏移，`$B$6` = 情境選擇儲存格（1、2 或 3）

**然後在所有預測中參照彙整欄：**
`Revenue Year 1: =D29*(1+$E$10)`，其中 $E$10 是第 1 年成長的彙整欄值。

這個做法把情境邏輯集中，讓模型更容易稽核和維護。

## 交付物結構

**檔案命名**：`[Ticker]_DCF_Model_[Date].xlsx`

**兩張工作表**：
1. **DCF**：完整模型，含 Bear/Base/Bull 情境，加上底部的三張敏感度表（WACC vs Terminal Growth、Revenue Growth vs EBIT Margin、Beta vs Risk-Free Rate）
2. **WACC**：資金成本計算

**主要特色**：情境選擇器（1/2/3）、含 INDEX/OFFSET 公式的彙整欄、顏色標示的儲存格、所有輸入都有儲存格註解、專業框線

## 最佳實務

### 模型建構
1. **逐步建立**：完成每個段落後才進入下一個
2. **邊建邊測**：輸入範例數字來驗證公式
3. **使用一致的結構**：相似的計算遵循相似的模式
4. **為複雜公式加註解**：為不尋常的計算加備註
5. **內建檢查**：適用時加入加總檢查和平衡檢查

### 文件記錄
1. **記錄所有假設**：說明關鍵輸入背後的理由
2. **引用資料來源**：註明每個資料點來自哪裡
3. **說明方法論**：描述任何非標準的做法
4. **標出不確定性**：凸顯能見度有限的領域

### 品質控管
1. **交叉核對計算**：用多種方式驗證數學
2. **壓力測試假設**：跑敏感度確保模型穩健
3. **同儕審閱**：讓別人檢查公式
4. **版本控制**：工作進行中儲存各版本

## 常見變化

### 高成長科技公司
- 較長的預測期間（7 到 10 年）
- 較高的初始成長率（20 到 30%）
- 隨時間顯著的利潤率擴張
- 較高的 WACC（12 到 15%）
- 建模單位經濟（使用者、ARPU 等）

### 成熟／穩定的公司
- 較短的預測期間（3 到 5 年）
- 溫和的成長率（GDP +1 到 3%）
- 穩定的利潤率
- 較低的 WACC（7 到 9%）
- 聚焦現金創造與資本配置

### 景氣循環型公司
- 跨越整個經濟週期建模
- 以週期中段正常化利潤率
- 考慮谷底和高峰情境
- 針對景氣循環性調整 beta

### 多分部公司
- 為每個事業單位分別做 DCF
- 各分部有不同的成長率和利潤率
- 分部加總估值（sum-of-parts）
- 考慮綜效

## 疑難排解

**如果遇到錯誤或不合理的結果，請閱讀 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)，取得詳細的除錯指引。**

## 工作流程整合

### DCF 建構開始時

1. **蒐集市場資料**：
   - 檢查有沒有可用的 MCP 伺服器提供目前的市場資料
   - 用 web search/fetch 取得股價、beta 和其他市場指標
   - 如果需要特定資料，向使用者索取

2. **蒐集歷史財務資料**：
   - 檢查有沒有可用的 MCP 伺服器（Daloopa 等）
   - 如果 MCP 沒有，就向使用者索取
   - 必要時從 10-K 手動擷取

3. **開始建構模型**，使用這個 skill 中詳述的 DCF 方法

### 模型建構期間

1. **用 openpyxl 建立 Excel 模型**，使用公式（不是寫死的值）
2. **遵循 xlsx skill 的慣例**來建構公式和格式化
3. **只有在使用者要求，或有提供特定品牌規範時，才套用填色**

### 交付模型之前（強制）

1. **驗證結構**：
   - Bear/Base/Bull 的情境區塊，假設橫跨各預測年度
   - 情境選擇器可運作，公式參照正確的情境區塊
   - 敏感度表在 DCF 工作表底部（不是獨立的工作表）
   - 字體顏色：藍色輸入、黑色公式、綠色工作表連結
   - 所有寫死的輸入都有儲存格註解
   - 主要段落周圍有專業框線

2. **重算公式**：執行 `python recalc.py model.xlsx 30`

3. **檢查輸出**：
   - 如果 `status` 是 `"success"` → 繼續步驟 4
   - 如果 `status` 是 `"errors_found"` → 檢查 `error_summary`，並閱讀 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) 取得除錯指引

4. **修正錯誤並重新執行 recalc.py**，直到狀態為 "success"

5. **抽查公式**：
   - 測試一個 FCF 公式，它有參照正確的假設列嗎？
   - 切換情境選擇器，彙整欄有正確更新嗎？
   - 驗證營收公式參照的是彙整欄（不是巢狀 IF 公式）

6. **交付模型**

### 可用的資料來源

- **MCP 伺服器**：若有設定（Daloopa 提供歷史財務資料）
- **Web search/fetch**：取得目前股價、beta 和市場資料
- **使用者提供的資料**：歷史財務資料、共識預估
- **手動擷取**：以 SEC EDGAR 申報文件作為備案

## 最終輸出 Checklist

交付 DCF 模型之前：

**必要：**
- 執行 `python recalc.py model.xlsx 30`，直到狀態為 "success"（零公式錯誤）
- 兩張工作表：DCF（底部附敏感度）、WACC
- 字體顏色：藍色=輸入、黑色=公式、綠色=工作表連結
- 所有寫死的輸入都有儲存格註解
- 敏感度表以公式完整填入
- 主要段落周圍有專業框線

**驗證：**
- OpEx 以營收為基礎（不是毛利）
- 終值占 EV 的 50 到 70%
- 終端成長 < WACC
- 稅率 21 到 28%
- 檔名：`[Ticker]_DCF_Model_[Date].xlsx`
