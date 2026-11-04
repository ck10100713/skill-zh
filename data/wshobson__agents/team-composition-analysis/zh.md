---
name: team-composition-analysis
description: 為早期新創（從 pre-seed 到 Series A）設計最佳的團隊結構、招募計畫、薪酬策略和股權分配。在規劃人力、決定下一個要招哪個職位、設定薪酬或股權範圍、設計組織架構，或建立與募資里程碑對齊的招募預算時使用這個 skill。
version: 1.0.0
---

# Team Composition Analysis

為早期新創（從 pre-seed 到 Series A）設計最佳的團隊結構、招募計畫、薪酬策略和股權分配。

## Overview

在對的時間建立對的團隊，搭配適當的薪酬和股權。依營收里程碑、預算限制和市場基準，規劃逐個職位的招募。

## Team Structure by Stage

### Pre-Seed (0-$500K ARR)

**團隊規模：2-5 人**

**核心職位：**

- 創辦人（2-3 位）：產品、工程、商業
- 第一位工程師（如果需要）
- 外包職位：設計、行銷

**聚焦：** 打造並驗證 product-market fit

### Seed ($500K-$2M ARR)

**團隊規模：5-15 人**

**關鍵招募：**

- 工程負責人 + 2-3 位工程師
- 第一位業務/商務開發
- 產品經理
- 行銷/成長負責人

**聚焦：** 擴大產品規模，並證明銷售是可重複的

### Series A ($2M-$10M ARR)

**團隊規模：15-50 人**

**部門的建置：**

- 工程（40%）：6-20 人
- 銷售與行銷（30%）：5-15 人
- 客戶成功（10%）：2-5 人
- G&A（10%）：2-5 人
- 產品（10%）：2-5 人

**聚焦：** 擴大營收規模並建立可重複的流程

## Detailed section: Role-by-Role Planning

原本是這份 SKILL.md 裡一段 1720 bytes 的內容，為了符合 Codex 對 skill 本文 8 KB 的上限，已經搬到 `references/details.md`。

## Compensation Strategy

### Base Salary Benchmarks (US, 2024)

**工程：**

- Junior：$90K-$120K
- Mid-Level：$120K-$150K
- Senior：$150K-$180K
- Staff/Principal：$180K-$220K
- Engineering Manager：$160K-$200K
- VP Engineering：$180K-$250K

**業務：**

- SDR/BDR：$50K-$70K 底薪 + $50K-$70K 佣金
- Account Executive：$80K-$120K 底薪 + $80K-$120K 佣金
- Sales Manager：$120K-$160K 底薪 + $80K-$120K 佣金
- VP Sales：$150K-$200K 底薪 + $150K-$200K 佣金

**產品：**

- Product Manager：$120K-$150K
- Senior PM：$150K-$180K
- Head of Product：$150K-$180K
- VP Product：$180K-$220K

**行銷：**

- Marketing Manager：$90K-$130K
- Content/Demand Gen：$70K-$100K
- Head of Marketing：$130K-$170K
- VP Marketing：$150K-$200K

**客戶成功：**

- CS Representative：$60K-$90K
- CS Manager：$100K-$130K
- VP Customer Success：$140K-$180K

### Total Compensation Formula

```
Total Comp = Base Salary × 1.30 (benefits & taxes) + Equity Value
```

**完全負擔成本：**

- 底薪
- 薪資稅（7.65% FICA）
- 福利（健保、401k）：每位員工 $10K-$15K
- 其他（工作空間、設備、軟體）：每位員工 $5K-$10K

**經驗法則：** 底薪乘以 1.3-1.4，就是完全負擔成本

### Geographic Adjustments

**舊金山 / 紐約：** 比基準高 +20-30%
**西雅圖 / 波士頓 / 洛杉磯：** +10-20%
**奧斯汀 / 丹佛 / 芝加哥：** +0-10%
**遠端 / 其他美國城市：** -10-20%
**國際：** 依國家差異很大

## Equity Allocation

### Equity by Role and Stage

**創辦人：**

- 第一位創辦人：40-60%
- 第二位創辦人：20-40%
- 第三位創辦人：10-20%
- Vesting：4 年，1 年 cliff

**早期員工（Pre-Seed）：**

- 第一位工程師：0.5-2.0%
- 前 5 位員工：每人 0.25-1.0%

**Seed 階段的招募：**

- VP/Head 層級：0.5-1.5%
- Senior IC：0.1-0.5%
- Mid-level：0.05-0.25%
- Junior：0.01-0.1%

**Series A 的招募：**

- C-level（CTO、CFO）：1.0-3.0%
- VP 層級：0.3-1.0%
- Director 層級：0.1-0.5%
- Senior IC：0.05-0.2%
- Mid-level：0.01-0.1%
- Junior：0.005-0.05%

### Equity Pool Sizing

**各輪的選擇權池（Option Pool）：**

- Pre-Seed：預留 10-15%
- Seed：補充 10-15%
- Series A：補充 10-15%
- Series B+：每輪 5-10%

**募資前的稀釋：**
投資人常常要求在投資前先建立選擇權池，這會稀釋創辦人。

**範例：**

```
Pre-money: $10M
Investors want 15% option pool post-money

Calculation:
Post-money: $15M ($10M + $5M investment)
Option pool: $2.25M (15% × $15M)
Founders diluted by pool creation before new money
```

## Organizational Design

### Reporting Structure

**Pre-Seed：**

```
Founders (flat structure)
├── Contractors
└── First hires (report to founders)
```

**Seed：**

```
CEO
├── Engineering Lead (2-4 engineers)
├── Sales/Growth Lead (1-2 reps)
├── Product Manager
└── Operations
```

**Series A：**

```
CEO
├── CTO / VP Engineering (6-20 people)
│   ├── Engineering Manager(s)
│   └── Individual Contributors
├── VP Sales (5-15 people)
│   ├── Sales Manager
│   ├── Account Executives
│   └── SDRs
├── Head of Product (2-5 people)
│   ├── Product Managers
│   └── Designers
├── Head of Customer Success (2-5 people)
└── CFO / Finance Lead (2-5 people)
    ├── Recruiter
    └── Operations
```

### Span of Control

**主管比例：**

- 第一線主管：4-8 位直屬部屬
- Director：3-5 位直屬部屬（主管）
- VP：3-5 位直屬部屬（director）
- CEO：5-8 位直屬部屬（高階主管團隊）

## Full-Time vs. Contract

### Use Full-Time for:

- 核心產品開發
- 銷售（創造營收的職位）
- 攸關任務成敗的營運
- 承載組織知識的職位

### Use Contractors for:

- 專門的短期需求（法務、會計）
- 工作量不固定（設計、行銷活動）
- 核心能力之外的技能
- 在轉正職前先試這個職位
- 在建立常設據點之前先做地理擴張

### Cost Comparison

**正職：**

- 時薪成本較低
- 有福利和管銷
- 長期承諾
- 文化契合度很重要

**外包：**

- 時薪較高（$75-$200/小時，相對於約當正職的 $40-$100/小時）
- 沒有福利或管銷
- 彈性的合作方式
- 比較容易擴編/縮編

## Hiring Velocity

### Realistic Timeline

**從開出職缺到招到人：**

- Junior：6-8 週
- Mid-Level：8-12 週
- Senior：12-16 週
- Executive：16-24 週

**達到生產力的時間：**

- Junior：4-6 個月
- Mid-Level：2-4 個月
- Senior：1-3 個月
- Executive：3-6 個月

### Planning Buffer

招募計畫一定要加 2-3 個月的緩衝。

**範例：**
如果 7 月 1 日前需要工程師：

- 開始招募：4 月 1 日（12 週）
- 達到生產力：9 月 1 日（2 個月的爬坡期）

## Budget Planning

### Compensation as % of Revenue

**早期階段（Seed）：**

- 總薪酬：營收的 120-150%（燒錢換成長）
- 工程：50-60%
- 銷售：30-40%
- 其他：20-30%

**成長階段（Series A）：**

- 總薪酬：營收的 70-100%
- 工程：35-45%
- 銷售：25-35%
- 其他：20-30%

### Headcount Budget Formula

```
Total Comp Budget = Σ (Role Count × Fully-Loaded Cost × % of Year)

Example:
3 Engineers × $202K × 100% = $606K
2 AEs × $230K × 75% (mid-year start) = $345K
1 PM × $162K × 100% = $162K
Total: $1.1M
```


## Quick Start

規劃團隊組成：

1. **找出階段** - Pre-seed、seed 還是 Series A
2. **定義職位** - 現在需要哪些職能
3. **排定招募的優先順序** - 達成商業目標的關鍵路徑
4. **設定薪酬** - 依級別訂底薪 + 股權
5. **規劃時程** - 把招募和爬坡的時間算進去
6. **計算預算** - 完全負擔成本 × 人數
7. **設計組織圖** - 匯報結構和管理幅度
8. **分配股權** - 公平的分配，並保留選擇權池
