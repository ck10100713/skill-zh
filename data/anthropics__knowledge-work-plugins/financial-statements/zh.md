---
name: financial-statements
description: 產生財務報表（損益表、資產負債表、現金流量表），附期間對比與差異分析。準備月度或季度損益表（P&L）、結帳時要標記重大差異、比對實際值與預算、為管理層審閱製作財務摘要，或查詢 GAAP 表達要求和期末調整時使用。
argument-hint: "<frequency> <period>"
---

# /financial-statements

> 如果看到不熟悉的佔位符，或需要確認目前連接了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

**重要**：這個指令協助處理財務報表的工作流程，但不提供財務建議。所有報表在用於申報或送件之前，都應該由合格的財務專業人員審閱。

產生附期間對比和差異分析的財務報表。下面的流程會帶你走過損益表的產生；資產負債表和現金流量表的參考格式、GAAP 表達要求（ASC 220/210/230），以及常見的期末調整，都收錄在後面當作輔助參考資料。

## 用法

```
/financial-statements <period-type> <period>
```

### 參數

- `period-type`：報告期間類型：
  - `monthly`：單月損益表，與上個月和去年同月比較
  - `quarterly`：季度損益表，與上一季和去年同季比較
  - `annual`：全年損益表，與去年比較
  - `ytd`：年初至今損益表，與去年同期的年初至今比較
- `period`：要報告的期間（例如 `2024-12`、`2024-Q4`、`2024`）

## 流程

### 1. 蒐集財務資料

如果有連接 ~~erp 或 ~~data warehouse：
- 拉出指定期間的試算表（trial balance）或損益表資料
- 拉出比較期間的資料（上一期、去年同期、預算／預測）
- 拉出科目階層和分組，用於呈現

如果沒有連接資料來源：
> 連接 ~~erp 或 ~~data warehouse，就能自動拉取財務資料。你也可以貼上試算表資料、上傳試算表，或提供損益表資料來分析。

請使用者提供：
- 本期的營收和費用資料（依科目或類別）
- 比較期間的資料（上一期、去年同期，以及／或預算）
- 任何已知的調整或重分類

### 2. 產生損益表

用標準的多欄格式呈現：

```
INCOME STATEMENT
Period: [Period description]
(in thousands, unless otherwise noted)

                              Current    Prior      Variance   Variance   Budget    Budget
                              Period     Period     ($)        (%)        Amount    Var ($)
                              --------   --------   --------   --------   --------  --------
REVENUE
  Product revenue             $XX,XXX    $XX,XXX    $X,XXX     X.X%       $XX,XXX   $X,XXX
  Service revenue             $XX,XXX    $XX,XXX    $X,XXX     X.X%       $XX,XXX   $X,XXX
  Other revenue               $XX,XXX    $XX,XXX    $X,XXX     X.X%       $XX,XXX   $X,XXX
                              --------   --------   --------              --------  --------
TOTAL REVENUE                 $XX,XXX    $XX,XXX    $X,XXX     X.X%       $XX,XXX   $X,XXX

COST OF REVENUE
  [Cost items]                $XX,XXX    $XX,XXX    $X,XXX     X.X%       $XX,XXX   $X,XXX
                              --------   --------   --------              --------  --------
GROSS PROFIT                  $XX,XXX    $XX,XXX    $X,XXX     X.X%       $XX,XXX   $X,XXX
  Gross Margin                XX.X%      XX.X%

OPERATING EXPENSES
  Research & development      $XX,XXX    $XX,XXX    $X,XXX     X.X%       $XX,XXX   $X,XXX
  Sales & marketing           $XX,XXX    $XX,XXX    $X,XXX     X.X%       $XX,XXX   $X,XXX
  General & administrative    $XX,XXX    $XX,XXX    $X,XXX     X.X%       $XX,XXX   $X,XXX
                              --------   --------   --------              --------  --------
TOTAL OPERATING EXPENSES      $XX,XXX    $XX,XXX    $X,XXX     X.X%       $XX,XXX   $X,XXX

OPERATING INCOME (LOSS)       $XX,XXX    $XX,XXX    $X,XXX     X.X%       $XX,XXX   $X,XXX
  Operating Margin            XX.X%      XX.X%

OTHER INCOME (EXPENSE)
  Interest income             $XX,XXX    $XX,XXX    $X,XXX     X.X%
  Interest expense           ($XX,XXX)  ($XX,XXX)   $X,XXX     X.X%
  Other, net                  $XX,XXX    $XX,XXX    $X,XXX     X.X%
                              --------   --------   --------
TOTAL OTHER INCOME (EXPENSE)  $XX,XXX    $XX,XXX    $X,XXX     X.X%

INCOME BEFORE TAXES           $XX,XXX    $XX,XXX    $X,XXX     X.X%
  Income tax expense          $XX,XXX    $XX,XXX    $X,XXX     X.X%
                              --------   --------   --------

NET INCOME (LOSS)             $XX,XXX    $XX,XXX    $X,XXX     X.X%       $XX,XXX   $X,XXX
  Net Margin                  XX.X%      XX.X%
```

### 3. 差異分析

對每個項目計算並標記重大差異。

#### 差異計算

對每個項目計算：
- **金額差異：** 本期 - 上一期（或本期 - 預算）
- **百分比差異：** (本期 - 上一期) / |上一期| x 100
- **基點（basis point）變動：** 對利潤率和比率，用基點表示變動（1 bp = 0.01%）

#### 重大性門檻

定義什麼才算需要調查的「重大」差異。常見的做法：

- **固定金額門檻：** 差異超過設定的金額（例如 $50K、$100K）
- **百分比門檻：** 差異超過設定的百分比（例如 10%、15%）
- **合併：** 金額門檻或百分比門檻，任一個超過就算
- **分級：** 依項目的大小和波動性，用不同的門檻

*門檻範例（請依你的組織調整）：*

| 項目大小 | 金額門檻 | 百分比門檻 |
|---------------|-----------------|---------------------|
| > $10M        | $500K           | 5%                  |
| $1M - $10M    | $100K           | 10%                 |
| < $1M         | $50K            | 15%                 |

#### 差異拆解

把總差異拆成各個組成的驅動因素：

- **量／數量效應：** 以上一期的費率計算，量的變化
- **費率／價格效應：** 以本期的量計算，費率／價格的變化
- **組合（mix）效應：** 費率／利潤率不同的項目之間，組成的轉移
- **新增／停止的項目：** 只出現在其中一期的項目
- **一次性／非經常性項目：** 預期不會重複的項目
- **時間效應：** 在期間之間移動的項目（不是營運 run rate 真正的變化）
- **匯率效應：** 匯率變動對換算後結果的影響

#### 調查與敘述

對每個重大差異：
1. 量化差異（金額和百分比）
2. 判斷是有利還是不利
3. 用上面的類別拆解成各個驅動因素
4. 提供業務原因的敘述說明
5. 評估這個差異是暫時的，還是代表趨勢改變
6. 註明需要的行動（進一步調查、更新預測、流程變更）

### 4. 關鍵指標摘要

```
KEY METRICS
                              Current    Prior      Change
Revenue growth (%)                                  X.X%
Gross margin (%)              XX.X%      XX.X%      X.X pp
Operating margin (%)          XX.X%      XX.X%      X.X pp
Net margin (%)                XX.X%      XX.X%      X.X pp
OpEx as % of revenue          XX.X%      XX.X%      X.X pp
Effective tax rate (%)        XX.X%      XX.X%      X.X pp
```

### 5. 重大差異摘要

列出所有需要調查的重大差異：

| Line Item | Variance ($) | Variance (%) | Direction | Preliminary Driver | Action |
|-----------|-------------|-------------|-----------|-------------------|--------|
| [Item]    | $X,XXX      | X.X%        | Unfav.    | [If known]        | Investigate |

### 6. 輸出

提供：
1. 附比較的格式化損益表
2. 關鍵指標摘要
3. 附調查標記的重大差異清單
4. 針對無法解釋的差異，建議後續要問的問題
5. 主動提議用 `/flux` 深入研究任何特定的差異

## GAAP 表達要求

### 損益表（ASC 220 / IAS 1）

- 呈現某一期間認列的所有收益和費損項目
- 費用依性質（材料、人工、折舊）或依功能（COGS、R&D、S&M、G&A）分類，美國公司比較常用功能別
- 如果依功能別分類，要在附註中依性質揭露折舊、攤銷和員工福利成本
- 營業項目和非營業項目要分開呈現
- 所得稅費用要單獨一行列示
- 美國 GAAP 和 IFRS 都禁止列示非常項目（extraordinary items）
- 停業單位（discontinued operations）要單獨呈現，並扣除稅後淨額

**常見的表達考量：**

- **營收細分：** ASC 606 要求把營收細分成能反映經濟因素如何影響營收的性質、金額、時點和不確定性的類別
- **股票報酬（SBC）：** 歸類在各功能別費用類別（R&D、S&M、G&A）內，並在附註中揭露 SBC 總額
- **重組費用：** 重大的話要單獨呈現，或併入營業費用並在附註中揭露
- **非 GAAP 調整：** 如果呈現非 GAAP 指標（在財報發布中很常見），要明確標示並調節回 GAAP

### 資產負債表（ASC 210 / IAS 1）

- 區分流動和非流動的資產與負債
- 流動：預期在 12 個月內（或營業週期更長時用營業週期）變現、消耗或清償
- 資產依流動性排序（流動性最高的在前），這是美國的標準做法
- 應收帳款以扣除信用損失備抵後的淨額列示（ASC 326）
- 不動產及設備以扣除累計折舊後的淨額列示
- 商譽不攤銷，每年測試減損（ASC 350）
- 租賃：對營業租賃和融資租賃都要認列使用權資產和租賃負債（ASC 842）

### 現金流量表（ASC 230 / IAS 7）

- 間接法最常見（從淨利出發，調整非現金項目）
- 直接法也允許，但很少用（需要補充間接法的調節表）
- 必須揭露已付利息和已付所得稅（列在報表本身或附註皆可）
- 非現金的投資和籌資活動要單獨揭露（例如以租賃取得的資產、為併購發行的股票）
- 約當現金：原始到期日 3 個月或更短的短期高流動性投資

## 資產負債表參考格式

```
ASSETS
Current Assets
  Cash and cash equivalents
  Short-term investments
  Accounts receivable, net
  Inventory
  Prepaid expenses and other current assets
Total Current Assets

Non-Current Assets
  Property and equipment, net
  Operating lease right-of-use assets
  Goodwill
  Intangible assets, net
  Long-term investments
  Other non-current assets
Total Non-Current Assets

TOTAL ASSETS

LIABILITIES AND STOCKHOLDERS' EQUITY
Current Liabilities
  Accounts payable
  Accrued liabilities
  Deferred revenue, current portion
  Current portion of long-term debt
  Operating lease liabilities, current portion
  Other current liabilities
Total Current Liabilities

Non-Current Liabilities
  Long-term debt
  Deferred revenue, non-current
  Operating lease liabilities, non-current
  Other non-current liabilities
Total Non-Current Liabilities

Total Liabilities

Stockholders' Equity
  Common stock
  Additional paid-in capital
  Retained earnings (accumulated deficit)
  Accumulated other comprehensive income (loss)
  Treasury stock
Total Stockholders' Equity

TOTAL LIABILITIES AND STOCKHOLDERS' EQUITY
```

## 現金流量表參考格式（間接法）

```
CASH FLOWS FROM OPERATING ACTIVITIES
Net income (loss)
Adjustments to reconcile net income to net cash from operations:
  Depreciation and amortization
  Stock-based compensation
  Amortization of debt issuance costs
  Deferred income taxes
  Loss (gain) on disposal of assets
  Impairment charges
  Other non-cash items
Changes in operating assets and liabilities:
  Accounts receivable
  Inventory
  Prepaid expenses and other assets
  Accounts payable
  Accrued liabilities
  Deferred revenue
  Other liabilities
Net Cash Provided by (Used in) Operating Activities

CASH FLOWS FROM INVESTING ACTIVITIES
  Purchases of property and equipment
  Purchases of investments
  Proceeds from sale/maturity of investments
  Acquisitions, net of cash acquired
  Other investing activities
Net Cash Provided by (Used in) Investing Activities

CASH FLOWS FROM FINANCING ACTIVITIES
  Proceeds from issuance of debt
  Repayment of debt
  Proceeds from issuance of common stock
  Repurchases of common stock
  Dividends paid
  Payment of debt issuance costs
  Other financing activities
Net Cash Provided by (Used in) Financing Activities

Effect of exchange rate changes on cash

Net Increase (Decrease) in Cash and Cash Equivalents
Cash and cash equivalents, beginning of period
Cash and cash equivalents, end of period
```

## 常見的調整與重分類

### 期末調整

1. **應計（Accruals）：** 記錄已發生但尚未支付的費用（應付帳款應計、薪資應計、利息應計）
2. **遞延（Deferrals）：** 調整該期的預付費用、遞延收入和遞延成本
3. **折舊與攤銷：** 依固定資產和無形資產明細表，入帳該期的折舊／攤銷
4. **呆帳提列：** 依帳齡分析和歷史損失率，調整信用損失備抵
5. **存貨調整：** 對過時、滯銷或減損的存貨，記錄跌價損失
6. **匯率重估：** 以期末匯率，重新評價以外幣計價的貨幣性資產和負債
7. **所得稅提列：** 記錄當期和遞延所得稅費用
8. **公允價值調整：** 對投資、衍生工具和其他公允價值項目做市價評價

### 重分類

1. **流動／非流動重分類：** 把 12 個月內到期的長期負債重分類為流動負債
2. **抵銷科目淨額化：** 備抵與應收帳款總額相抵，累計折舊與資產總額相抵
3. **公司間沖銷：** 在合併時沖銷公司間的餘額和交易
4. **停業單位：** 把停業單位的結果重分類到單獨的項目
5. **權益法調整：** 對權益法投資，記錄應享有被投資者的損益
6. **部門重分類：** 確保交易依營運部門正確分類
