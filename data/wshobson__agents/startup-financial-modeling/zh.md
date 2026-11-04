---
name: startup-financial-modeling
description: 為早期新創建立完整的 3-5 年財務模型，包含營收預測、成本結構、現金流分析和情境規劃。在建立財務預測、計算 burn rate 或 runway、模擬募資情境，或為 seed 或 Series A 募資準備讓投資人看得懂的財務報表時使用這個 skill。
version: 1.0.0
---

# Startup Financial Modeling

為早期新創建立完整的 3-5 年財務模型，包含營收預測、成本結構、現金流分析和情境規劃。

## Overview

財務模型為新創的策略、募資和營運規劃提供量化的基礎。用以 cohort 為基礎的營收建模、詳細的成本結構和情境分析，建立務實的預測，來支持決策和投資人簡報。

## Core Components

### Revenue Model

**以 Cohort 為基礎的預測：**
依 cohort 從客戶獲取和留存來推算營收。

**公式：**

```
MRR = Σ (Cohort Size × Retention Rate × ARPU)
ARR = MRR × 12
```

**關鍵輸入：**

- 每月新增客戶數
- 各月份的客戶留存率
- 每位使用者平均營收（ARPU）
- 定價和方案組合的假設
- 擴張營收（upsell、cross-sell）

### Cost Structure

**營運費用類別：**

1. **銷貨成本（Cost of Goods Sold, COGS）**
   - 主機代管和基礎設施
   - 支付處理手續費
   - 客戶支援（變動的部分）
   - 每位客戶的第三方服務

2. **銷售與行銷（Sales & Marketing, S&M）**
   - 客戶獲取成本（CAC）
   - 行銷活動和廣告
   - 業務團隊薪酬
   - 行銷工具和軟體

3. **研發（Research & Development, R&D）**
   - 工程團隊薪酬
   - 產品管理
   - 設計和 UX
   - 開發工具和基礎設施

4. **一般與行政（General & Administrative, G&A）**
   - 高階主管團隊
   - 財務、法務、人資
   - 辦公室和設施
   - 保險和合規

### Cash Flow Analysis

**組成：**

- 期初現金餘額
- 現金流入（營收、募資）
- 現金流出（營運費用、資本支出）
- 期末現金餘額
- 每月 burn rate
- Runway（剩餘現金可支撐的月數）

**公式：**

```
Runway = Current Cash Balance / Monthly Burn Rate
Monthly Burn = Monthly Revenue - Monthly Expenses
```

### Headcount Planning

**依職位的招募計畫：**
依部門和職位追蹤人力。

**關鍵指標：**

- 每位員工的完全負擔成本
- 每位員工的營收
- 各部門人力（佔總數的 %）

**典型比例（早期 SaaS）：**

- 工程：40-50%
- 銷售與行銷：25-35%
- G&A：10-15%
- 客戶成功：5-10%

## Financial Model Structure

### Three-Scenario Framework

**保守情境（P10）：**

- 客戶獲取較慢
- 定價或轉換率較低
- 流失率較高
- 銷售週期較長
- 用於現金管理

**基準情境（P50）：**

- 最可能的結果
- 務實的假設
- 主要的規劃情境
- 用於董事會報告

**樂觀情境（P90）：**

- 成長較快
- 單位經濟學較好
- 流失率較低
- 用於上檔規劃

### Time Horizon

**詳細預測：3 年**

- 第 1 年以月為單位
- 第 2 年以月為單位
- 第 3 年以季為單位

**高階預測：第 4-5 年**

- 年度預測
- 只列關鍵指標
- 支持長期規劃

## Detailed section: Step-by-Step Process

原本是這份 SKILL.md 裡一段 2763 bytes 的內容，為了符合 Codex 對 skill 本文 8 KB 的上限，已經搬到 `references/details.md`。

## Business Model Templates

### SaaS Financial Model

**營收驅動因素：**

- 新增 MRR（客戶數 × ARPU）
- 擴張 MRR（upsell）
- 收縮 MRR（降級）
- 流失 MRR（流失的客戶）

**關鍵比率：**

- 毛利率：75-85%
- S&M 佔營收的比例：40-60%（早期）
- CAC 回收期：< 12 個月
- 淨留存率：100-120%

**預測範例：**

```
Year 1: $500K ARR, 50 customers, $100K MRR by Dec
Year 2: $2.5M ARR, 200 customers, $208K MRR by Dec
Year 3: $8M ARR, 600 customers, $667K MRR by Dec
```

### Marketplace Financial Model

**營收驅動因素：**

- GMV（Gross Merchandise Value）
- 抽成率（take rate，佔 GMV 的 %）
- 淨營收 = GMV × 抽成率

**關鍵比率：**

- 抽成率：10-30%，依類別而異
- 買家 vs. 賣家的 CAC
- 邊際貢獻率：60-70%

**預測範例：**

```
Year 1: $5M GMV, 15% take rate = $750K revenue
Year 2: $20M GMV, 15% take rate = $3M revenue
Year 3: $60M GMV, 15% take rate = $9M revenue
```

### E-Commerce Financial Model

**營收驅動因素：**

- 流量（訪客數）
- 轉換率
- 平均訂單金額（AOV）
- 購買頻率

**關鍵比率：**

- 毛利率：40-60%
- 邊際貢獻率：20-35%
- CAC 回收期：3-6 個月

### Services / Agency Financial Model

**營收驅動因素：**

- 可計費的時數或專案
- 時薪或專案費用
- 使用率（utilization）
- 團隊產能

**關鍵比率：**

- 毛利率：50-70%
- 使用率：70-85%
- 每位員工的營收

## Fundraising Integration

### Funding Scenario Modeling

**Pre-Money 估值：**
根據指標和可比公司。

**稀釋：**

```
Post-Money = Pre-Money + Investment
Dilution % = Investment / Post-Money
```

**資金用途：**
分配資金以延長 runway 並達成里程碑。

**範例：**

```
Raise: $5M at $20M pre-money
Post-Money: $25M
Dilution: 20%

Use of Funds:
- Product Development: $2M (40%)
- Sales & Marketing: $2M (40%)
- G&A and Operations: $0.5M (10%)
- Working Capital: $0.5M (10%)
```

### Milestone-Based Planning

**找出關鍵里程碑：**

- 產品上線
- 第一個 $1M ARR
- CAC 損益兩平
- Series A 募資

**募資金額：**
確保 runway 足夠達成下一個里程碑，再加 6 個月的緩衝。

## Common Pitfalls

**陷阱 1：營收過度樂觀**

- 新創很少達到激進的預測
- 客戶獲取的假設要保守
- 流失率要用務實的數字來建模

**陷阱 2：低估成本**

- 費用估算要加 20% 的緩衝
- 要包含完全負擔的薪酬
- 要把軟體和工具算進去

**陷阱 3：忽略現金流的時間點**

- 營收 ≠ 現金（付款條件）
- 費用在營收收回之前就要先付
- 要仔細建模現金轉換

**陷阱 4：人力靜態不變**

- 招募需要時間（補一個職缺要 3-6 個月）
- 生產力需要爬坡時間（3-6 個月）
- 要考慮離職率（每年 10-15%）

**陷阱 5：沒有做情境規劃**

- 單一情境從來都不準
- 一定要建模保守的情況
- 要規劃基準情境失敗時你會怎麼做

## Model Validation

**健全性檢查：**

- [ ] 營收成長率是做得到的（第 2 年 3 倍、第 3 年 2 倍）
- [ ] 單位經濟學是務實的（LTV/CAC > 3、回收期 < 18 個月）
- [ ] Burn multiple 是合理的（第 2-3 年 < 2.0）
- [ ] 人力隨營收擴張（每位員工的營收持續成長）
- [ ] 毛利率符合商業模式
- [ ] S&M 支出跟 CAC 和成長目標一致

**跟同業做基準比較：**
把關鍵指標跟處於類似階段的相似公司做比較。

**投資人回饋：**
把模型分享給顧問或投資人，聽取他們對假設的回饋。


## Quick Start

建立新創財務模型：

1. **定義商業模式** - 營收驅動因素和定價
2. **預測營收** - 以 cohort 為基礎，納入留存
3. **建模成本** - 依月份列出 COGS、S&M、R&D、G&A
4. **規劃人力** - 依職位和部門招募
5. **計算現金流** - 營收 - 費用 = burn/runway
6. **計算指標** - CAC、LTV、burn multiple、runway
7. **建立情境** - 保守、基準、樂觀
8. **驗證假設** - 健全性檢查和基準比較
9. **整合募資** - 模擬募資輪次和里程碑
