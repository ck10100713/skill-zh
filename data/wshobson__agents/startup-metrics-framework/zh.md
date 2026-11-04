---
name: startup-metrics-framework
description: 追蹤、計算並優化 SaaS、marketplace、消費性和 B2B 新創從 seed 到 Series A 的關鍵績效指標，包含單位經濟學、成長效率和現金管理。在定義指標框架、計算 CAC/LTV/burn multiple、對事業健康度做基準比較，或為投資人或董事會報告準備指標儀表板時使用這個 skill。
version: 1.0.0
---

# Startup Metrics Framework

一份完整的指南，教你追蹤、計算並優化不同新創商業模式從 seed 到 Series A 的關鍵績效指標。

## Overview

在對的階段追蹤對的指標。專注在對募資和卓越營運來說重要的單位經濟學、成長效率和現金管理指標。

每一次新創分析，都要先讀[通用的營收、單位經濟學和現金指標](references/universal-and-saas-metrics.md)；相關時也要套用其中的 SaaS 段落。

## Marketplace Metrics

### GMV (Gross Merchandise Value)

**總交易量：**

```
GMV = Σ (Transaction Value)
```

**成長率：**

```
GMV Growth Rate = (Current Period GMV - Prior Period GMV) / Prior Period GMV
```

**目標：** 早期階段月增（MoM）20% 以上

### Take Rate

```
Take Rate = Net Revenue / GMV
```

**典型範圍：**

- 支付處理商：2-3%
- 電商 marketplace：10-20%
- 服務 marketplace：15-25%
- 高單價 B2B：5-15%

### Marketplace Liquidity

**Time to Transaction**
從刊登到成交/配對要多久？

**Fill Rate**
產生交易的請求佔多少 %

**Repeat Rate**
多次交易的使用者佔多少 %

**基準：**

- Fill rate > 80% = 流動性強
- Repeat rate > 60% = 留存強

### Marketplace Balance

**供給/需求比：**
追蹤供給方和需求方的相對成長。

**警訊：**

- 供給太多：fill rate 低、供應商受挫
- 需求太多：等待時間長、客戶受挫

**目標：** 平衡的成長（理想是 1:1，但依模式而異）

## Consumer/Mobile Metrics

### Engagement Metrics

**DAU (Daily Active Users)**
每天活躍的不重複使用者

**MAU (Monthly Active Users)**
每月活躍的不重複使用者

**DAU/MAU Ratio**

```
DAU/MAU = DAU / MAU
```

**基準：**

- > 50% = 極佳（每天的習慣）
- 20-50% = 好
- < 20% = 參與度弱

**Session Frequency**
每位使用者每天/每週的平均 session 數

**Session Duration**
每個 session 平均花的時間

### Retention Curves

**Day 1 Retention：** 隔天回來的使用者 %
**Day 7 Retention：** 註冊 7 天後仍活躍的使用者 %
**Day 30 Retention：** 註冊 30 天後仍活躍的使用者 %

**基準（Day 30）：**

- > 40% = 優秀
- 25-40% = 好
- < 25% = 弱

**留存曲線的形狀：**

- 曲線趨於平緩 = 好（使用者養成習慣）
- 急遽下滑 = product-market fit 不佳

### Viral Coefficient (K-Factor)

```
K-Factor = Invites per User × Invite Conversion Rate
```

**範例：**
每位使用者 10 個邀請 × 20% 轉換率 = 2.0 K-factor

**基準：**

- K > 1.0 = 病毒式成長
- K = 0.5-1.0 = 推薦效果強
- K < 0.5 = 病毒性弱

## B2B Metrics

### Sales Efficiency

**Win Rate**

```
Win Rate = Deals Won / Total Opportunities
```

**目標：** 新業務團隊 20-30%，成熟團隊 30-40%

**Sales Cycle Length**
從商機到成交的平均天數

**越短越好：**

- SMB：30-60 天
- 中型市場：60-120 天
- 企業：120-270 天

**Average Contract Value (ACV)**

```
ACV = Total Contract Value / Contract Length (years)
```

### Pipeline Metrics

**Pipeline Coverage**

```
Pipeline Coverage = Total Pipeline Value / Quota
```

**目標：** 3-5 倍覆蓋（需要 3-5 倍的 pipeline 才能達到配額）

**各階段的轉換率：**

- Lead → Opportunity：10-20%
- Opportunity → Demo：50-70%
- Demo → Proposal：30-50%
- Proposal → Close：20-40%

## Metrics by Stage

### Pre-Seed (Product-Market Fit)

**聚焦的指標：**

1. 活躍使用者成長
2. 使用者留存（Day 7、Day 30）
3. 核心參與度（session、使用的功能）
4. 質性回饋（NPS、訪談）

**不用擔心：**

- 營收（可能是零）
- CAC（還沒到優化的階段）
- 單位經濟學

### Seed ($500K-$2M ARR)

**聚焦的指標：**

1. MRR 成長率（月增 15-20%）
2. CAC 和 LTV（建立基準線）
3. 毛留存率（> 85%）
4. 核心產品參與度

**開始追蹤：**

- 銷售效率
- Burn rate 和 runway

### Series A ($2M-$10M ARR)

**聚焦的指標：**

1. ARR 成長（年增 3-5 倍）
2. 單位經濟學（LTV:CAC > 3、回收期 < 18 個月）
3. 淨美元留存率（> 100%）
4. Burn multiple（< 2.0）
5. Magic number（> 0.5）

**成熟的追蹤：**

- Rule of 40
- 銷售效率
- Pipeline coverage

## Metric Tracking Best Practices

### Data Infrastructure

**需求：**

- 單一事實來源（分析平台）
- 即時或每日更新
- 自動化計算
- 歷史追蹤

**工具：**

- Mixpanel、Amplitude（產品分析）
- ChartMogul、Baremetrics（SaaS 指標）
- Looker、Tableau（BI 儀表板）

### Reporting Cadence

**每天：**

- MRR、活躍使用者
- 註冊數、轉換數

**每週：**

- 成長率
- 留存 cohort
- 銷售 pipeline

**每月：**

- 完整的指標套組
- 董事會報告
- 投資人更新

**每季：**

- 趨勢分析
- 基準比較
- 策略檢視

### Common Mistakes

**錯誤 1：虛榮指標**
不要只關注：

- 總使用者數（沒有留存）
- 頁面瀏覽數（沒有參與度）
- 下載數（沒有啟用）

要專注在跟價值連結、可以付諸行動的指標。

**錯誤 2：指標太多**
要密集追蹤 5-7 個核心指標，不要鬆散地追蹤 50 個。

**錯誤 3：忽略單位經濟學**
就算在 seed 階段，CAC 和 LTV 也很關鍵。

**錯誤 4：沒有分群**
指標要依客戶族群、通路、cohort 拆開來看。

**錯誤 5：操弄指標**
為真正的商業成果優化，不要為儀表板上的數字優化。

## Investor Metrics

### What VCs Want to See

**Seed 輪：**

- MRR 成長率
- 使用者留存
- 早期單位經濟學
- 產品參與度

**Series A：**

- ARR 和成長率
- CAC 回收期 < 18 個月
- LTV:CAC > 3.0
- 淨美元留存率 > 100%
- Burn multiple < 2.0

**Series B+：**

- Rule of 40 > 40%
- 有效率的成長（magic number）
- 通往獲利的路徑
- 市場領導地位的指標

### Metric Presentation

**儀表板格式：**

```
Current MRR: $250K (↑ 18% MoM)
ARR: $3.0M (↑ 280% YoY)
CAC: $1,200 | LTV: $4,800 | LTV:CAC = 4.0x
NDR: 112% | Logo Retention: 92%
Burn: $180K/mo | Runway: 18 months
```

**要包含：**

- 目前的數值
- 成長率或趨勢
- 脈絡（目標、基準）


## Quick Start

實作新創指標框架：

1. **找出商業模式** - SaaS、marketplace、消費性、B2B
2. **選出 5-7 個核心指標** - 依階段和模式
3. **建立追蹤** - 設定分析和儀表板
4. **計算單位經濟學** - CAC、LTV、回收期
5. **設定目標** - 用基準值當目標
6. **定期檢視** - 核心指標每週檢視
7. **跟團隊分享** - 對齊目標和進度
8. **更新投資人** - 每月/每季報告
