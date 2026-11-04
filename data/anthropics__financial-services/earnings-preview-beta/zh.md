---
name: earnings-preview-single
description: 為單一公司產生精簡的 4 到 5 頁股票研究財報前瞻。分析最近一次財報逐字稿、競爭對手格局、估值和近期新聞，產出專業的 HTML 報告。
---

# 單一公司財報前瞻

為單一公司產生精簡、專業的股票研究財報前瞻。輸出是一個獨立的 HTML 檔案，目標是列印成 4 到 5 頁。報告的圖表和數據密集，敘述緊湊、直奔重點。

**資料來源（零例外）：** 唯一允許的資料來源是 **Kensho Grounding MCP**（`search`）和 **S&P Global MCP**（`kfinance`）。絕對不准使用任何其他工具、資料來源或任何形式的網路存取。具體來說：
- 不准使用 `WebSearch`、`WebFetch`、`web_search`、`brave_search`、`google_search`，或任何通用的網路／網際網路搜尋工具，即使 Kensho 很慢、沒有回傳結果、或暫時無法使用也一樣。
- 不准使用任何瀏覽器、URL 擷取或網頁爬取工具。
- 如果 Kensho Grounding 對某個查詢沒有回傳結果，就換個說法重新查詢，或在報告中註明「資料無法取得」。**絕對不准退而求其次改用網路搜尋。**
- 報告中的每一項資訊，都必須能追溯到一次 `kfinance` MCP 函式呼叫或一次 Kensho `search` 呼叫。如果無法溯源到這兩者之一，就不准出現在報告中。

**關鍵規則：** 在撰寫報告的任何部分「之前」，你「必須」完成所有研究和資料蒐集（階段 1 到 5）。

**中間檔案規則：** MCP 工具呼叫的所有原始資料，都「必須」在**每次工具呼叫回傳後立刻**寫入 `/tmp/earnings-preview/` 底下的檔案，之後才能進行下一次呼叫。這是為了保護資料不被 context window 壓縮弄丟。不要只把資料放在記憶體裡。在階段 1 開始時，執行 `mkdir -p /tmp/earnings-preview` 建立目錄。**在產生 HTML 報告（階段 7）之前，你「必須」用 `cat` 指令把所有中間檔案讀回 context。報告中每一個數字、引述和來源 URL 的唯一真實來源是這些檔案，不是你對先前對話的記憶。如果你跳過讀檔，報告一定會有錯誤。**

**會計季度規則：** 絕對不要從日曆上的報告日期去推斷會計季度。很多公司的會計年度不是標準的（例如 Walmart 的會計年度在 1 月 31 日結束，所以 2026 年 2 月的報告涵蓋的是 Q4 FY2026，不是 Q4 2025 或 Q1 2026）。一律使用 `get_next_earnings_from_identifiers` 或 `get_earnings_from_identifiers` 回傳的財報電話會議名稱中所載明的會計季度和會計年度（例如「Walmart Q4 FY2026 Earnings Call」代表這個季度是 Q4 FY2026）。在報告標題、標頭、表格和所有引用處，逐字使用它。如果電話會議名稱含糊，就用 `get_financial_line_item_from_identifiers` 的期間標籤交叉比對。

**篇幅規則：** 報告必須精簡。目標是列印成 4 到 5 頁。不要寫冗長的多段落敘述。用緊湊、有力的條列。每一句話都要有存在的價值。能用更少的字說完，就用更少的字。

**逐字引述規則：** 在 `<blockquote>` 標籤中引述管理層的話時，文字「必須」**一字不差地**從逐字稿複製，包括贅詞和不完整的句子片段。不要改寫、重新排列、把逐字稿不同位置的句子拼在一起，或「整理」引述。如果在逐字稿裡找不到確切的措辭，就不要把它當作直接引述呈現。改用你自己的敘述口吻轉述，不用 blockquote 格式（例如「Management noted that data center demand remains significant」）。每一個 blockquote 都必須是可以對照逐字稿驗證的逐字、複製貼上的摘錄。

**計算完整性規則：** 對任何多步驟的計算（從年度 guidance 推算的隱含季度數字、LTM P/E、年增率、分部年增變化），把每一步明確寫出來，並在用於下一步之前驗證中間結果。如果你寫 A + B + C = X，在後續公式使用 X 之前，先驗證 X 在算術上是正確的。如果附錄顯示的總和不等於它所陳述的各組成項，那份報告就是錯的。有疑慮時，從原始資料重新計算，不要重複使用先前算出的中間值。

**比率命名規則：** 所有估值比率都必須明確標示為 **LTM**（過去十二個月）或 **NTM**（未來十二個月）。絕對不要用「trailing」或「forward」，一律用 LTM 或 NTM。LTM 比率使用最近 4 個已申報季度的總和。NTM 比率使用 `get_consensus_estimates_from_identifiers` 中**未來 4 個季度共識平均 EPS 預估的總和**，不是單一的年度數字。LTM 和 NTM 的 P/E 都必須計算，並顯示在競爭對手比較表中。

**超連結規則（嚴格執行）：** 報告中的每一項主張，不論是數字或非數字，「都必須」用指向附錄對應條目的 `<a href="#ref-N" class="data-ref">` 超連結包起來。**這不是選用的。報告中的每一個數字都必須是可點擊的連結。** 這包括：營收數字、EPS、利潤率、成長率、市值、P/E 比率、股票報酬、目標價、分部營收，以及任何其他財務指標。也包括來自逐字稿或 Kensho 搜尋的質化主張。如果你把它當作事實陳述，它就必須連結到來源。為每一個獨特的主張指派依序的參照 ID（`ref-1`、`ref-2` 等）。超連結樣式要低調：深藍色、沒有底線、hover 時顯示點狀底線。**報告內文中，不准有任何一個數字沒有被 `<a>` 標籤包起來。** 範例：寫成 `<a href="#ref-1" class="data-ref">$152.3B</a>`，絕對不要把 `$152.3B` 當純文字寫出來。

---

## 階段 1：公司概況與設定

1. 從 `$ARGUMENTS` 解析出單一公司股票代號（去除空白）。
2. 執行 `mkdir -p /tmp/earnings-preview` 建立工作目錄。
3. 呼叫 `get_latest()` 建立目前報告期間的背景。
4. 呼叫 `get_info_from_identifiers`，記錄市值、產業。
5. 呼叫 `get_company_summary_from_identifiers`，記錄業務描述。
6. 呼叫 `get_next_earnings_from_identifiers`，記錄即將到來的財報日期和會計季度名稱。

**立刻寫入** `/tmp/earnings-preview/company-info.txt`：
```
TICKER: [ticker]
COMPANY: [full name]
INDUSTRY: [industry]
MARKET_CAP: [value] (as of [date])
NEXT_EARNINGS_DATE: [date]
NEXT_EARNINGS_QUARTER: [Q# FY#### exactly as returned by API]
BUSINESS_DESCRIPTION: [2-3 sentence summary]
```

---

## 階段 2：財報逐字稿分析（必要：撰寫之前就要完成）

1. 呼叫 `get_latest_earnings_from_identifiers`，取得最近一次已完成財報電話會議的 `key_dev_id`。
2. 針對該逐字稿呼叫 `get_transcript_from_key_dev_id`。
3. **立刻寫入** `/tmp/earnings-preview/transcript-extracts.txt`，包含下列區段。趁逐字稿還在 context 裡就寫這個檔案，不要等：

```
TRANSCRIPT_SOURCE: [Call Name, e.g., "Q3 2025 Earnings Call"]
KEY_DEV_ID: [key_dev_id]
CALL_DATE: [date]
FISCAL_QUARTER: [Q# FY####]

=== VERBATIM QUOTES (copy-paste exactly — do NOT paraphrase) ===
QUOTE_1: "[exact text from transcript]"
SPEAKER_1: [Name], [Title]
CONTEXT_1: [1 sentence on where this appeared — prepared remarks or Q&A]

QUOTE_2: "[exact text from transcript]"
SPEAKER_2: [Name], [Title]
CONTEXT_2: [context]

QUOTE_3: "[exact text from transcript]"
SPEAKER_3: [Name], [Title]
CONTEXT_3: [context]

QUOTE_4: "[exact text from transcript]"
SPEAKER_4: [Name], [Title]
CONTEXT_4: [context]

=== GUIDANCE (quantitative only) ===
- [metric]: [range or point estimate as stated by management]
- [metric]: [range or point estimate]

=== KEY DRIVERS ===
- [driver 1 with supporting data point]
- [driver 2 with supporting data point]
- [driver 3 with supporting data point]

=== HEADWINDS & RISKS ===
- [risk 1 with quantification if available]
- [risk 2]

=== ANALYST Q&A THEMES ===
- [theme 1: what analysts pushed on]
- [theme 2]
- [theme 3]

=== SYNTHESIS: THEMES TO WATCH NEXT QUARTER ===
- [theme 1]
- [theme 2]
- [theme 3]
```

---

## 階段 3：競爭對手分析

1. 以 `competitor_source="all"` 呼叫 `get_competitors_from_identifiers`。
2. 選出**最相關的前 5 到 7 家上市競爭對手**。
3. 對該公司以及所有選出的競爭對手，蒐集：
   - `get_prices_from_identifiers`，`periodicity="day"`，最近 12 個月
   - `get_financial_line_item_from_identifiers`，取 `diluted_eps`，`period_type="quarterly"`，`num_periods=8`
   - `get_capitalization_from_identifiers`，`capitalization="market_cap"`（最新）
   - `get_consensus_estimates_from_identifiers`，`period_type="quarterly"`，`num_periods_forward=4`：這會回傳未來 4 個季度的共識平均 EPS 預估，加總後用來計算 NTM EPS

**每次工具呼叫回傳後，立刻把原始資料附加到對應的中間檔案：**

**寫入** `/tmp/earnings-preview/prices.csv`：每一列是一組 (ticker, date, close)。要包含 `source` 欄，填入確切的 MCP 函式呼叫。先寫主體公司的價格，再隨著取得依序寫入每個競爭對手的：
```
ticker,date,close,source
D,2025-02-19,55.67,get_prices_from_identifiers(identifier='D',periodicity='day')
D,2025-02-20,55.82,get_prices_from_identifiers(identifier='D',periodicity='day')
...
DUK,2025-02-19,111.79,get_prices_from_identifiers(identifier='DUK',periodicity='day')
...
```
注意：單次呼叫的所有列，`source` 的值都相同，每一列都要寫，確保隨時都能取得。

**寫入** `/tmp/earnings-preview/peer-eps.csv`：每一列是一組 (ticker, period, eps)。每次 `diluted_eps` 呼叫後立刻寫入：
```
ticker,period,diluted_eps,source
D,Q4 2024,1.09,get_financial_line_item_from_identifiers(identifier='D',line_item='diluted_eps',period_type='quarterly')
D,Q1 2025,-0.11,get_financial_line_item_from_identifiers(identifier='D',line_item='diluted_eps',period_type='quarterly')
...
DUK,Q4 2024,1.52,get_financial_line_item_from_identifiers(identifier='DUK',line_item='diluted_eps',period_type='quarterly')
...
```

**寫入** `/tmp/earnings-preview/peer-market-caps.csv`：每個 ticker 一列。每次 `market_cap` 呼叫後立刻寫入：
```
ticker,market_cap,retrieval_date,source
D,55900000000,2026-02-19,get_capitalization_from_identifiers(identifier='D',capitalization='market_cap')
DUK,98300000000,2026-02-19,get_capitalization_from_identifiers(identifier='DUK',capitalization='market_cap')
...
```

**寫入** `/tmp/earnings-preview/consensus-eps.csv`：每一列是一組 (ticker, period, consensus mean EPS)。每次 `get_consensus_estimates_from_identifiers` 呼叫後立刻寫入：
```
ticker,period,consensus_mean_eps,num_estimates,source
D,Q4 2025,0.88,12,get_consensus_estimates_from_identifiers(identifier='D',period_type='quarterly',num_periods_forward=4)
D,Q1 2026,0.72,10,get_consensus_estimates_from_identifiers(identifier='D',period_type='quarterly',num_periods_forward=4)
D,Q2 2026,0.91,9,get_consensus_estimates_from_identifiers(identifier='D',period_type='quarterly',num_periods_forward=4)
D,Q3 2026,1.05,8,get_consensus_estimates_from_identifiers(identifier='D',period_type='quarterly',num_periods_forward=4)
DUK,Q4 2025,1.48,14,get_consensus_estimates_from_identifiers(identifier='DUK',period_type='quarterly',num_periods_forward=4)
...
```

4. **現在不要計算 P/E 或報酬。** 原始資料現在已經在磁碟上了。計算在階段 6（驗證）進行，從這些檔案讀取。

**日期一致性規則（股票報酬）：** 計算比較用的股票報酬（YTD %、1 年 %、30 天 %、90 天 %）時，所有 ticker「必須」使用**完全相同的起始和結束日期**。把所有價格資料寫入 `prices.csv` 後，找出所有 ticker 的資料中都有出現的第一個交易日，以它作為共同的基準日。不要對不同的 ticker 使用不同的基準日（例如主體公司從 2 月 19 日起算，同業從 2 月 28 日起算）。如果某個 ticker 的資料開始得比較晚，所有計算都使用第一個重疊的日期。每一項報酬計算，都要在附錄中載明共同的基準日。

**P/E 時效規則（LTM P/E）：** 計算每間公司的 LTM P/E 時，使用該公司在 `peer-eps.csv` 中**最近 4 個已申報的季度**，不是對所有公司套用固定的日曆區間。如果某個同業已經申報了 Q4 2025，而主體公司只申報到 Q3 2025，該同業的 LTM EPS 應該包含 Q4 2025。檢查每間公司最新的已申報期間，並對每間公司使用最近的 4 個期間。在附錄中註明每個 P/E 計算使用了哪 4 個季度。

**市值日期標註：** 報告市值時，使用 `peer-market-caps.csv` 中的 `retrieval_date`。如果與報告日期不同，要在附錄中註明。

---

## 階段 4：新聞、預估與產業情報（透過 Kensho Grounding）

對下列**每一個**類別執行這些 `search` 查詢。不准跳過任何一個。

**關鍵：擷取來源 URL：** 每一個 Kensho `search` 結果都包含底層文章、報告或資料頁面的**來源 URL**。你「必須」把 URL 與每一項發現一起記錄。

**每次搜尋呼叫之後，立刻用下面的格式，把結果附加到** `/tmp/earnings-preview/kensho-findings.txt`。不要等所有搜尋都做完，每做完一個就寫：

```
=== SEARCH: "[query used]" ===
DATE_RUN: [today's date]
CATEGORY: [estimates|analyst_ratings|risks|news|sector]

FINDING_1: [key finding or excerpt]
URL_1: [source URL from search result]
SOURCE_1: [publication name, date if available]

FINDING_2: [key finding or excerpt]
URL_2: [source URL]
SOURCE_2: [publication name, date]

[...continue for all relevant results from this search...]
```

**財報預估與分析師情緒：**
1. `search` "[TICKER] earnings estimates consensus EPS revenue upcoming quarter"
   - 記錄：共識 EPS、共識營收、過去 90 天預估修正的方向。
   - **立刻附加到 kensho-findings.txt。**
2. `search` "[TICKER] analyst ratings price target upgrades downgrades"
   - 記錄：近期升評／降評、目標價區間、多空論點摘要。
   - **立刻附加到 kensho-findings.txt。**
3. `search` "[TICKER] risks bear case concerns investors"
   - 記錄：主要爭論點、看空論點、這次財報的搖擺因素。
   - **立刻附加到 kensho-findings.txt。**

**近期新聞（必要，不准跳過）：**
4. `search` "[TICKER] [company name] recent news developments"
   - 記錄：過去 60 天的重大新聞：併購、產品發布、高階主管異動、監管行動、合作夥伴關係、法律進展、關稅，或任何可能影響即將到來的財報或前瞻 guidance 的事件。
   - 每一項都要註明日期、標題、對財報的潛在影響。
   - **立刻附加到 kensho-findings.txt。**

**產業背景：**
5. `search` "[company industry/sector] sector outlook trends"
   - 記錄：產業層級的順風／逆風、總經資料、競爭動態。
   - **立刻附加到 kensho-findings.txt。**

---

## 階段 5：財務資料蒐集

**季度財務（最近 8 個季度）：**
以 `period_type="quarterly"`、`num_periods=8` 呼叫 `get_financial_line_item_from_identifiers`，取得：
`revenue`、`gross_profit`、`operating_income`、`ebitda`、`net_income`、`diluted_eps`

**每次 line item 呼叫回傳後，立刻附加到** `/tmp/earnings-preview/financials.csv`。原始數值要寫成跟回傳的完全一樣，現在不要四捨五入或轉換。包含 `source` 欄，填入確切的 MCP 函式呼叫與參數：
```
ticker,period,line_item,value,source
D,Q4 2024,revenue,3941000000,get_financial_line_item_from_identifiers(identifier='D',line_item='revenue',period_type='quarterly')
D,Q1 2025,revenue,3400000000,get_financial_line_item_from_identifiers(identifier='D',line_item='revenue',period_type='quarterly')
D,Q2 2025,revenue,4076000000,get_financial_line_item_from_identifiers(identifier='D',line_item='revenue',period_type='quarterly')
D,Q3 2025,revenue,3810000000,get_financial_line_item_from_identifiers(identifier='D',line_item='revenue',period_type='quarterly')
D,Q4 2024,diluted_eps,1.09,get_financial_line_item_from_identifiers(identifier='D',line_item='diluted_eps',period_type='quarterly')
D,Q1 2025,diluted_eps,-0.11,get_financial_line_item_from_identifiers(identifier='D',line_item='diluted_eps',period_type='quarterly')
...
```

**現在不要計算利潤率或成長率。** 只寫原始資料。計算在階段 6 進行。

**分部資料：**
- `get_segments_from_identifiers`，`segment_type="business"`、`period_type="quarterly"`、`num_periods=8`
- 你需要 8 個季度（不是 4 個），這樣才有去年同期的季度可做年增比較。要計算 Q3 2025 的年增，你需要 Q3 2024，也就是往回數的第 5 個季度。**如果 API 回應中沒有前一年同期的分部資料，不准估計或捏造。在報告中寫明「y/y not available」。**

**立刻寫入** `/tmp/earnings-preview/segments.csv`：
```
ticker,period,segment_name,revenue,source
D,Q3 2024,Dominion Energy Virginia,2762000000,get_segments_from_identifiers(identifier='D',segment_type='business',period_type='quarterly')
D,Q3 2024,Dominion Energy South Carolina,848000000,get_segments_from_identifiers(identifier='D',segment_type='business',period_type='quarterly')
D,Q3 2024,Contracted Energy,260000000,get_segments_from_identifiers(identifier='D',segment_type='business',period_type='quarterly')
D,Q3 2025,Dominion Energy Virginia,3311000000,get_segments_from_identifiers(identifier='D',segment_type='business',period_type='quarterly')
D,Q3 2025,Dominion Energy South Carolina,945000000,get_segments_from_identifiers(identifier='D',segment_type='business',period_type='quarterly')
D,Q3 2025,Contracted Energy,297000000,get_segments_from_identifiers(identifier='D',segment_type='business',period_type='quarterly')
...
```

**財報歷史（用於股價圖表標註）：**
- `get_earnings_from_identifiers`：收集 12 個月價格區間內的過往財報日期。
- **立刻寫入** `/tmp/earnings-preview/earnings-dates.csv`：
```
ticker,earnings_date,call_name,source
D,2025-05-02,Q1 2025 Earnings Call,get_earnings_from_identifiers(identifier='D')
D,2025-08-01,Q2 2025 Earnings Call,get_earnings_from_identifiers(identifier='D')
D,2025-10-31,Q3 2025 Earnings Call,get_earnings_from_identifiers(identifier='D')
...
```

---

## 階段 6：驗證與計算（必要：不准跳過）

產生報告之前，先讀回所有中間檔案，並從乾淨的資料進行計算。這個階段從檔案而不是被壓縮過的對話 context 來作業，以確保資料完整性。

1. **用 bash `cat` 指令讀取所有中間檔案：**
   - `cat /tmp/earnings-preview/company-info.txt`
   - `cat /tmp/earnings-preview/transcript-extracts.txt`
   - `cat /tmp/earnings-preview/financials.csv`
   - `cat /tmp/earnings-preview/segments.csv`
   - `cat /tmp/earnings-preview/prices.csv`
   - `cat /tmp/earnings-preview/peer-eps.csv`
   - `cat /tmp/earnings-preview/peer-market-caps.csv`
   - `cat /tmp/earnings-preview/consensus-eps.csv`
   - `cat /tmp/earnings-preview/kensho-findings.txt`
   - `cat /tmp/earnings-preview/earnings-dates.csv`

2. **從現在在 context 裡的原始資料計算衍生指標：**
   - 毛利率 % = gross_profit / revenue（每季）
   - 營業利益率 % = operating_income / revenue（每季）
   - 營收年增 % = (當季營收 - 去年同期營收) / 去年同期營收
   - EPS 年增 % = 同樣的邏輯；如果基期為負，用 "n.m."
   - 分部年增 % = 依名稱比對去年同期的分部；如果缺少，註明 "y/y not available"
   - 每間公司的 LTM P/E = 最新價格 / 最近 4 個季度 EPS 的總和（用 `peer-eps.csv` 檢查每個 ticker 有哪 4 個季度可用）
   - 每間公司的 NTM P/E = 最新價格 / NTM EPS，其中 **NTM EPS = `consensus-eps.csv` 中未來 4 個季度共識平均 EPS 預估的總和**。把每個 ticker 4 個季度的 consensus_mean_eps 值加起來。如果某個同業可用的未來季度少於 4 個，把 NTM P/E 標為 "n/a"。在附錄中註明加總了哪 4 個季度。
   - 股票報酬（YTD、1 年、30 天、90 天）= 在 `prices.csv` 中找出**所有 ticker 共同的第一個日期**，再從那個日期起算報酬

3. **交叉檢查**：
   - 驗證每一個分部年增，在 `segments.csv` 中都有實際的前一年度列。如果沒有，標為 "y/y not available."
   - 驗證所有股票報酬的基準日在各 ticker 之間都完全相同。
   - 透過重新加總各組成項，驗證任何多步驟的計算（例如 LTM EPS 的總和與 4 個季度的值吻合）。
   - 驗證 `transcript-extracts.txt` 中所有逐字引述都是精確的複製貼上（不是改寫）。

4. **寫入** `/tmp/earnings-preview/calculations.csv`，放入所有衍生值：
```
ticker,metric,value,formula,components
D,gross_margin_Q3_2025,32.5%,gross_profit/revenue,"gross_profit=1238100000,revenue=3810000000"
D,revenue_yoy_Q3_2025,+9.3%,(Q3_2025-Q3_2024)/Q3_2024,"Q3_2025=3810000000,Q3_2024=3486000000"
D,ltm_pe,24.2x,price/ltm_eps,"price=65.46,ltm_eps=2.70,quarters=Q4_2024+Q1_2025+Q2_2025+Q3_2025"
D,ntm_pe,18.5x,price/ntm_eps,"price=65.46,ntm_eps=3.56,quarters=Q4_2025(0.88)+Q1_2026(0.72)+Q2_2026(0.91)+Q3_2026(1.05),source=get_consensus_estimates_from_identifiers"
D,yoy_return,+17.6%,(end-start)/start,"end=65.46,start=55.67,base_date=2025-02-19"
DUK,yoy_return,+13.0%,(end-start)/start,"end=126.32,start=111.79,base_date=2025-02-19"
...
```

這個檔案是報告中所有數字的唯一真實來源。

---

## 階段 7：產生 HTML 報告

**停：在撰寫任何 HTML 之前，你「必須」先讀取所有中間檔案。這是會擋住後續動作的前置條件。**

這不是選用的。你「必須」把下面每一個 `cat` 指令，各自當作**獨立的 bash 工具呼叫**來執行（不要合併成一個）。這樣才能確保每個檔案的內容都被個別載入，並在對話中看得到。不要把它們合併成單一指令。不要跳過任何檔案。

**一次一個**執行這些指令，每個都是自己的 bash 呼叫：

1. `cat /tmp/earnings-preview/company-info.txt`
2. `cat /tmp/earnings-preview/transcript-extracts.txt`
3. `cat /tmp/earnings-preview/financials.csv`
4. `cat /tmp/earnings-preview/segments.csv`
5. `cat /tmp/earnings-preview/prices.csv`
6. `cat /tmp/earnings-preview/peer-eps.csv`
7. `cat /tmp/earnings-preview/peer-market-caps.csv`
8. `cat /tmp/earnings-preview/consensus-eps.csv`
9. `cat /tmp/earnings-preview/kensho-findings.txt`
10. `cat /tmp/earnings-preview/earnings-dates.csv`
11. `cat /tmp/earnings-preview/calculations.csv`

**讀完所有檔案之後，你「必須」向使用者印出一則摘要訊息**，列出每個檔案和它的狀態。完全使用這個格式：

```
--- DATA FILE VERIFICATION ---
1. company-info.txt        ✓ loaded ([N] lines)
2. transcript-extracts.txt ✓ loaded ([N] lines)
3. financials.csv          ✓ loaded ([N] rows)
4. segments.csv            ✓ loaded ([N] rows)
5. prices.csv              ✓ loaded ([N] rows)
6. peer-eps.csv            ✓ loaded ([N] rows)
7. peer-market-caps.csv    ✓ loaded ([N] rows)
8. consensus-eps.csv       ✓ loaded ([N] rows)
9. kensho-findings.txt     ✓ loaded ([N] lines)
10. earnings-dates.csv     ✓ loaded ([N] rows)
11. calculations.csv       ✓ loaded ([N] rows)

All intermediate data files loaded successfully.
Generating report using file data as the single source of truth.
---
```

如果任何檔案遺失或是空的，就停下來，告訴使用者是哪個檔案失敗。不要在資料缺漏的情況下繼續產生報告。

**HTML 報告中的每一個數字、引述、來源 URL 和 MCP 函式呼叫參照，都必須來自這些檔案，不是來自你對先前對話輪次的記憶。** 檔案是唯一的真實來源。先前的對話 context 可能已被壓縮或摘要，如果依賴它，就一定會有錯誤。如果某個資料點不在檔案裡，就不該出現在報告中。

完整的 HTML 範本、CSS 和 Chart.js 設定請見 [report-template.md](report-template.md)。

**必要：使用範本的輔助函式來畫圖表：**
report-template.md 提供了預先建好、已除錯的 Chart.js 輔助函式。你「必須」使用這些確切的函式來建立圖表。不要自己寫行內的 Chart.js 程式碼。這些輔助函式是：
- `createRevEpsChart(canvasId, labels, revenueData, epsData, revLabel)`：用於圖 1
- `createMarginChart(canvasId, labels, grossMargins, opMargins)`：用於圖 2
- `createRevGrowthChart(canvasId, labels, growthData)`：用於圖 3
- `createAnnotatedPriceChart(canvasId, labels, prices, earningsDates, ticker)`：用於圖 5
- `createCompPerfChart(canvasId, labels, datasets)`：用於圖 6
- `createPEChart(canvasId, companies)`：用於圖 7

每一個圖表呼叫「必須」放在自己的 `<script>` 標籤裡，並用 try-catch 區塊包起來。這樣可確保一個圖表的 bug 不會阻止其他圖表渲染。範例：
```html
<script>
try {
  createRevEpsChart('chart-rev-eps', [...], [...], [...], 'Revenue ($B)');
} catch(e) { console.error('Figure 1 error:', e); }
</script>
<script>
try {
  createMarginChart('chart-margins', [...], [...], [...]);
} catch(e) { console.error('Figure 2 error:', e); }
</script>
```

### 報告結構（總共 4 到 5 頁）

報告有兩個部分：**敘述**（第 1 到 2 頁）和**圖表**（第 3 到 5 頁）。要讓兩者緊密整合。

---

**AI 免責聲明（必要：必須出現在 3 個地方）：**
你「必須」把下列免責聲明文字放進報告 HTML。這不是選用的，沒有它報告就不算完整：

> **"Analysis is AI-generated — please confirm all outputs"**

必須剛好出現在這 3 個位置：
1. **標頭橫幅**：緊接在封面標頭之前，用置中的黃色橫幅：`<div class="ai-disclaimer">Analysis is AI-generated — please confirm all outputs</div>`
2. **頁尾**：在 page-footer div 裡面，用醒目的黃色橫幅：`<div class="footer-disclaimer">Analysis is AI-generated — please confirm all outputs</div>`
3. **附錄**：作為附錄區段的第一行，放在表格之前：`<div class="ai-disclaimer">Analysis is AI-generated — please confirm all outputs</div>`

---

**第 1 頁：封面與論點**

- **AI 免責聲明橫幅**（黃色、置中，見上面的 AI 免責聲明規則）
- **標頭**：公司名稱（TICKER）| 產業 | 報告日期
- **標題**：主題式、針對該季度的具體標題（例如 "Walmart Inc. (WMT) Q4 FY2026 Earnings Preview: Holiday Harvest — Can Furner's First Print Confirm the $1T Thesis?"）
- **執行論點**（最多 2 到 3 個短段落，搭配條列）：
  - 用 1 到 2 句話講我們預期這次財報會是什麼
  - 4 到 6 個條列，涵蓋：我們的 EPS 預估 vs 共識、guidance 預期、要關注的關鍵指標、什麼會讓股價動起來、主要爭論點
  - 要直接、有觀點，要表態，不要什麼都模稜兩可
- **關鍵管理層引述**，來自最近一次財報電話會議，在相關處穿插在敘述中。不要放在獨立的標題下。把它們自然地整合，作為你論點的佐證。格式為縮排的 blockquote。

---

**第 2 頁：預估、主題與新聞**

- **共識預估表**（單一表格，標為圖表）：
  - 欄位：Metric | Consensus | Our Estimate | y/y Change
  - 列：Revenue、EPS、Gross Margin、Operating Income，以及 2 到 3 個重要的公司專屬 KPI（例如同店銷售、電商成長、會員營收，也就是市場對**這間**公司關心的東西）
  - **顏色標示嚴格依機械規則：** 如果 y/y 變動值為負，用 `class="neg"`（紅色）。如果為正，用 `class="pos"`（綠色）。如果是零或 N/A，用 `class="neutral"`。數字的正負號決定 class，不要依解讀而覆寫。-1.1% 一律是紅色，即使下滑幅度很小。
  - 這是唯一的 guidance／預估區段。不要在其他地方重複預估資料。

- **超越標題 EPS 的關鍵指標**（條列清單，3 到 5 項）：
  - 除了 EPS 數字之外，會決定這季是好是壞的具體指標
  - 每一項要寫：這個指標是什麼、共識／管理層預期什麼、為什麼重要
  - 要具體："Walmart Connect ad revenue growth (consensus ~30% y/y, 3Q was 33%)"

- **要關注的主題**（3 到 5 點）：
  - 針對即將發布的報告的前瞻項目
  - 管理層需要兌現什麼、什麼可能帶來驚喜、看空者關注什麼
  - 每個主題：最多 1 到 2 句

- **近期新聞與發展**（3 到 5 點）：
  - 過去 60 天的重大新聞，每則一行
  - 日期 + 標題 + 簡短的影響評估
  - 只放可能影響即將到來的財報或 guidance 的項目

---

**第 3 到 5 頁：圖表（所有圖表和表格）**

所有圖表依序編號。每張圖都有標題和來源列。

- **圖 1：季度營收與稀釋 EPS**：長條／折線組合圖，8 個季度
- **圖 2：利潤率趨勢（毛利率與營業利益率 %）**：雙折線圖，8 個季度
- **圖 3：營收年增 %**：長條圖，依條件用綠／紅上色。**只納入當期與去年同期資料都存在的季度**（通常是取回的 8 個季度中最近的 4 個）。不要納入無法計算年增的季度，圖表應該有 4 根長條，不是 8 根。
- **圖 4：事業分部營收**：表格：Segment | Latest Q Rev ($M) | % of Total | y/y Change
- **圖 5：附財報日期的 1 年股價**：價格線，在財報日期畫垂直標註線，標示季度和財報後 1 天的漲跌
- **圖 6：相對競爭對手的股價表現（指數化到 100）**：多折線圖，主體公司用粗實線，競爭對手用較細的虛線
- **圖 7：LTM P/E vs. 競爭對手**：水平長條圖，主體公司用深藍色凸顯
- **圖 8：競爭對手比較表**：Ticker | Company | Mkt Cap | LTM P/E | NTM P/E | YTD % | 1-Yr %

---

**附錄：資料來源與計算（必要：不准跳過或縮寫）**

附錄「必須」以 AI 免責聲明橫幅開頭：`<div class="ai-disclaimer">Analysis is AI-generated — please confirm all outputs</div>`

報告最後的頁面「必須」包含一張附錄表格，記錄報告中引用的**每一項主張**，不論是數字或非數字。**報告內文中出現的每一個數字，在這個附錄都必須有對應的一列，而且報告內文中的每一個這類數字，都必須是可點擊的 `<a href="#ref-N">` 超連結，捲動到它的附錄列。** 如果報告中有數字沒有連到附錄的超連結，這份報告就不完整。

- **表格欄位**：Ref # | Fact | Value | Source & Derivation
- **Ref #**：與報告內文超連結錨點相符的依序 ID（`ref-1`、`ref-2` 等）。每一列都有 `id="ref-N"` 屬性，讓超連結能捲動到它。
- **Fact**：人類可讀的標籤（例如 "Q3 FY2026 Revenue"、"LTM P/E — WMT"、"Management flagged tariff headwinds"、"Barclays upgraded to Overweight"）
- **Value**：報告中顯示的確切數字（例如 "$152.3B"、"24.5%"、"28.1x"）。非數字的事實，留空或寫 "N/A"。
- **Source & Derivation**：這是關鍵的一欄。**每一列都必須有具體、詳細的來源，不能只是個標籤。** 嚴格遵循這些規則：

  **來自 S&P Capital IQ 的原始財務資料（營收、EPS、毛利、營業利益、淨利、EBITDA、價格、市值等）：**
  - 註明所使用的 MCP 函式及其關鍵參數。格式：`S&P Capital IQ — [function_name](identifier='[TICKER]', line_item='[item]', period_type='[type]', period='[Q# FY####]')`
  - 範例：
    - `S&P Capital IQ — get_financial_line_item_from_identifiers(identifier='WMT', line_item='revenue', period_type='quarterly', period='Q3 FY2026')`
    - `S&P Capital IQ — get_financial_line_item_from_identifiers(identifier='WMT', line_item='diluted_eps', period_type='quarterly', period='Q3 FY2026')`
    - `S&P Capital IQ — get_prices_from_identifiers(identifier='WMT', periodicity='day')`
    - `S&P Capital IQ — get_capitalization_from_identifiers(identifier='WMT', capitalization='market_cap')`
  - **不要只寫 "S&P Capital IQ" 而沒有細節。** 讀者必須確切知道是哪一次工具呼叫的哪一個資料點產生了這個數字。

  **計算出來的值（利潤率、成長率、P/E、報酬、年增變動）：**
  - 顯示完整公式，並讓**各組成項帶有超連結**：每一個組成項都必須是 `<a href="#ref-N">` 連結，連回該原始資料點的附錄列。這點很關鍵：讀者必須能從計算出的值點進它的每一個輸入。
  - 範例：`Gross Margin = <a href='#ref-5'>Gross Profit $37.2B</a> / <a href='#ref-1'>Revenue $152.3B</a> = 24.4%. Source: S&P Capital IQ (calculated)`
  - 範例：`LTM P/E = <a href='#ref-20'>Price $172.35</a> / (<a href='#ref-8'>Q1 EPS $1.47</a> + <a href='#ref-9'>Q2 EPS $1.84</a> + <a href='#ref-10'>Q3 EPS $1.53</a> + <a href='#ref-11'>Q4 EPS $1.80</a>) = $172.35 / $6.64 = 25.9x`
  - 範例：`Revenue y/y growth = (<a href='#ref-12'>Q3 FY26 Rev $165.8B</a> - <a href='#ref-3'>Q3 FY25 Rev $160.8B</a>) / <a href='#ref-3'>Q3 FY25 Rev $160.8B</a> = +3.1%`
  - **每一個公式組成項都必須是可點擊的超連結。** 不要把公式寫成純文字數字。

  **來自逐字稿的主張（引述、管理層評論、guidance）：**
  - 寫出逐字稿中的**逐字摘錄句子**。
  - 用完整名稱和取得它所用的 `key_dev_id` 來參照逐字稿。
  - 格式：`"[verbatim quote]" — [Speaker], [Title]. Source: [Q# FY#### Earnings Call Transcript] (key_dev_id: [ID])`
  - 範例：`"We expect comp sales growth of 3-4% in Q4" — CEO John Furner. Source: Q3 FY2026 Earnings Call Transcript (key_dev_id: 12345678)`

  **來自 Kensho Grounding 搜尋結果的主張（新聞、分析師評等、共識預估）：**
  - 寫出搜尋結果中的關鍵發現或摘錄。
  - **必要：包含** Kensho `search` 工具回傳的來源 URL，作為可點擊的 `<a href="[URL]" target="_blank">` 超連結。這是最重要的部分，讀者必須能點進原始來源。
  - 格式：`"[finding/excerpt]" — <a href="[URL]" target="_blank">[Source Title or Publication]</a>. Query: search("[query used]")`
  - 範例：`"Barclays upgraded WMT to Overweight with $210 price target on Jan 15, 2026." — <a href="https://www.investing.com/news/barclays-upgrades-wmt" target="_blank">Investing.com, Jan 15 2026</a>. Query: search("WMT analyst ratings price target upgrades downgrades")`
  - 如果某個結果沒有回傳 URL，寫 "Source URL not available"，並仍然附上搜尋查詢。

**完整性檢查：** 定稿報告之前，掃描報告內文的每一個數字。如果有任何數字沒有被 `<a href="#ref-N" class="data-ref">` 包起來，就修正。如果有任何附錄列的 Source & Derivation 只是像 "S&P Capital IQ" 這種沒有函式呼叫細節的空標籤，就修正。如果有任何計算值的公式缺少帶超連結的組成項，就修正。如果有任何來自 Kensho 的主張缺少來源 URL，就修正。

把附錄列依區段（Financials、Valuation、Estimates & Consensus、Transcript Claims、News & Analyst Commentary、Stock Performance）分組，並加上小標題。使用較小的字級（10 到 11px）。

---

## 階段 8：輸出

1. 把完整的 HTML 檔案寫到目前工作目錄的 `earnings-preview-[TICKER]-YYYY-MM-DD.html`。
2. 在瀏覽器中開啟：`open earnings-preview-[TICKER]-YYYY-MM-DD.html`
3. 告訴使用者檔案已建立，並摘要重點發現。

---

## 寫作準則

- **不准用表情符號**：報告中任何地方都不准使用表情符號。這是專業的研究文件。
- **精簡**：目標是列印 4 到 5 頁。每一句話都要有份量。盡可能用條列，不要用段落。如果某個區段感覺太長，就砍掉。
- **數字要具體**：寫「$52.4B revenue, up 5.2% y/y」，不要寫「strong revenue growth」。
- **要有觀點**：這是財報前瞻，不是摘要。說明你預期什麼、什麼重要、為什麼。要有主見，但要用資料支撐。
- **管理層引述不加標題**：把最近一次電話會議中的 3 到 4 則關鍵管理層引述，以 blockquote 方式直接穿插在敘述中。不要建立「Key Management Quotes」區段標題，讓它們自然地作為佐證流動。
- **專業語氣**：賣方股票研究風格：分析性、直接、以資料為本。
- **圖表必須使用真實資料**：每個圖表都用實際的 MCP 資料填入。絕對不准捏造。
- **競爭對手脈絡**：估值要相對同業來框定。不知道同業是 20 倍還是 35 倍，25 倍 P/E 就沒有意義。
- **主張都要有超連結**：每一項事實主張，不論數字或質化，都必須是連到其附錄條目的 `<a class="data-ref">` 標籤。數字：`<a href="#ref-1" class="data-ref">$152.3B</a>`。質化：`<a href="#ref-25" class="data-ref">management flagged tariff headwinds as the primary margin risk</a>`。不該有任何事實在附錄中沒有可追溯的來源。
