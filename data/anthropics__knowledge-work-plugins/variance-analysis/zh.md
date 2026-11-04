---
name: variance-analysis
description: 把財務差異拆解成各項驅動因素，附上敘述說明和 waterfall 分析。分析預算對實際、期間對期間的變化、營收或費用差異，或替管理層準備差異說明時使用。
argument-hint: "<項目> <期間> vs <比較基準>"
---

# 差異分析

**重要**：這個 skill 協助差異分析的工作流程，但不提供財務建議。所有分析在用於報告之前，都應該由合格的財務專業人員審閱。

差異拆解的技巧、重大性門檻、敘述產生、waterfall 圖的方法，以及預算 vs 實際 vs 預測的比較。

## 差異拆解技巧

### 價格 / 數量拆解

最基本的差異拆解。用於營收、銷貨成本，以及任何能表示成 價格 x 數量 的指標。

**公式：**
```
Total Variance = Actual - Budget (or Prior)

Volume Effect  = (Actual Volume - Budget Volume) x Budget Price
Price Effect   = (Actual Price - Budget Price) x Actual Volume
Mix Effect     = Residual (interaction term), or allocated proportionally

Verification:  Volume Effect + Price Effect = Total Variance
               (when mix is embedded in the price/volume terms)
```

**三向拆解（把 mix 分開）：**
```
Volume Effect = (Actual Volume - Budget Volume) x Budget Price x Budget Mix
Price Effect  = (Actual Price - Budget Price) x Budget Volume x Actual Mix
Mix Effect    = Budget Price x Budget Volume x (Actual Mix - Budget Mix)
```

**範例：營收差異**
- 預算：10,000 單位，每單位 $50 = $500,000
- 實際：11,000 單位，每單位 $48 = $528,000
- 總差異：+$28,000 有利
  - 數量效應：+1,000 單位 x $50 = +$50,000（有利，賣出更多單位）
  - 價格效應：-$2 x 11,000 單位 = -$22,000（不利，ASP 較低）
  - 淨額：+$28,000

### 費率 / Mix 拆解

用於分析各分群單位經濟效益不同的混合費率。

**公式：**
```
Rate Effect = Sum of (Actual Volume_i x (Actual Rate_i - Budget Rate_i))
Mix Effect  = Sum of (Budget Rate_i x (Actual Volume_i - Expected Volume_i at Budget Mix))
```

**範例：毛利差異**
- 產品 A：毛利率 60%，產品 B：毛利率 40%
- 預算 mix：50% A、50% B → 混合毛利率 50%
- 實際 mix：40% A、60% B → 混合毛利率 48%
- Mix 效應解釋了 2 個百分點的毛利壓縮

### 人數 / 薪酬拆解

用於分析薪資和人事成本差異。

```
Total Comp Variance = Actual Compensation - Budget Compensation

Decompose into:
1. Headcount variance    = (Actual HC - Budget HC) x Budget Avg Comp
2. Rate variance         = (Actual Avg Comp - Budget Avg Comp) x Budget HC
3. Mix variance          = Difference due to level/department mix shift
4. Timing variance       = Hiring earlier/later than planned (partial-period effect)
5. Attrition impact      = Savings from unplanned departures (partially offset by backfill costs)
```

### 支出類別拆解

用於價格/數量不適用時的營運費用分析。

```
Total OpEx Variance = Actual OpEx - Budget OpEx

Decompose by:
1. Headcount-driven costs    (salaries, benefits, payroll taxes, recruiting)
2. Volume-driven costs       (hosting, transaction fees, commissions, shipping)
3. Discretionary spend       (travel, events, professional services, marketing programs)
4. Contractual/fixed costs   (rent, insurance, software licenses, subscriptions)
5. One-time / non-recurring  (severance, legal settlements, write-offs, project costs)
6. Timing / phasing          (spend shifted between periods vs plan)
```

## 重大性門檻與調查觸發條件

### 設定門檻

重大性門檻決定哪些差異需要調查和敘述說明。門檻的設定依據：

1. **財務報表重大性：** 通常是某個關鍵基準（營收、總資產、淨利）的 1-5%
2. **項目大小：** 金額較大的項目適用較低的百分比門檻
3. **波動性：** 波動較大的項目可能需要較高的門檻，避免雜訊
4. **管理層關注：** 多大的差異會改變決策？

### 建議的門檻框架

| 比較類型 | 金額門檻 | 百分比門檻 | 觸發條件 |
|----------------|-----------------|---------------------|---------|
| 實際 vs 預算 | 依組織而定 | 10% | 任一超過 |
| 實際 vs 前期 | 依組織而定 | 15% | 任一超過 |
| 實際 vs 預測 | 依組織而定 | 5% | 任一超過 |
| 連續期間（MoM） | 依組織而定 | 20% | 任一超過 |

*金額門檻依你的組織規模設定。常見做法：損益表項目取營收的 0.5%-1%。*

### 調查的優先順序

當多項差異都超過門檻時，依下列順序決定調查優先順序：

1. **絕對金額差異最大的**：對損益影響最大
2. **百分比差異最大的**：可能表示流程問題或錯誤
3. **方向出乎意料的**：差異與趨勢或預期相反
4. **新出現的差異**：原本照計畫走、現在偏離的項目
5. **累積/趨勢性差異**：每一期都在擴大

## 差異說明的敘述產生

### 每則差異敘述的結構

```
[Line Item]: [Favorable/Unfavorable] variance of $[amount] ([percentage]%)
vs [comparison basis] for [period]

Driver: [Primary driver description]
[2-3 sentences explaining the business reason for the variance, with specific
quantification of contributing factors]

Outlook: [One-time / Expected to continue / Improving / Deteriorating]
Action: [None required / Monitor / Investigate further / Update forecast]
```

### 敘述品質檢查清單

好的差異敘述應該：

- [ ] **具體：** 寫出實際的驅動因素，不是只說「比預期高」
- [ ] **量化：** 包含每個驅動因素的金額和百分比影響
- [ ] **有因果：** 解釋為什麼會發生，不只是發生了什麼
- [ ] **有前瞻性：** 說明這個差異預期會不會持續
- [ ] **可行動：** 指出需要的後續動作或決策
- [ ] **簡潔：** 2-4 句，不是一整段廢話

### 要避免的常見敘述反模式

- 「營收比預算高，是因為營收比較高」（循環論證，沒有實際解釋）
- 「這一期的費用偏高」（模糊，哪些費用？為什麼？）
- 只寫「時間差」，卻沒說明什麼提早或延後、何時會恢復正常
- 只寫「一次性」，卻沒解釋那個項目是什麼
- 對重大差異只寫「各種小項目」（必須再進一步拆解）
- 只聚焦在最大的驅動因素，忽略互相抵銷的項目

## Waterfall 圖的方法

### 概念

waterfall（或 bridge）圖顯示如何透過一連串正向和負向的貢獻項目，從一個值走到另一個值。用來視覺化差異拆解。

### 資料結構

```
Starting value:  [Base/Budget/Prior period amount]
Drivers:         [List of contributing factors with signed amounts]
Ending value:    [Actual/Current period amount]

Verification:    Starting value + Sum of all drivers = Ending value
```

### 純文字 Waterfall 格式

沒有圖表工具時，以純文字 waterfall 呈現：

```
WATERFALL: Revenue — Q4 Actual vs Q4 Budget

Q4 Budget Revenue                                    $10,000K
  |
  |--[+] Volume growth (new customers)               +$800K
  |--[+] Expansion revenue (existing customers)      +$400K
  |--[-] Price reductions / discounting               -$200K
  |--[-] Churn / contraction                          -$350K
  |--[+] FX tailwind                                  +$50K
  |--[-] Timing (deals slipped to Q1)                 -$150K
  |
Q4 Actual Revenue                                    $10,550K

Net Variance: +$550K (+5.5% favorable)
```

### Bridge 調節表

用調節表來補充 waterfall：

| 驅動因素 | 金額 | 佔差異 % | 累計 |
|--------|--------|---------------|------------|
| Volume growth | +$800K | 145% | +$800K |
| Expansion revenue | +$400K | 73% | +$1,200K |
| Price reductions | -$200K | -36% | +$1,000K |
| Churn / contraction | -$350K | -64% | +$650K |
| FX tailwind | +$50K | 9% | +$700K |
| Timing (deal slippage) | -$150K | -27% | +$550K |
| **Total variance** | **+$550K** | **100%** | |

*注意：當有互相抵銷的項目時，個別驅動因素的百分比可以超過 100%。*

### Waterfall 最佳實務

1. 驅動因素從最大的正向排到最大的負向（或依合乎邏輯的業務順序）
2. 最多保留 5-8 個驅動因素，較小的項目併成「Other」
3. 驗證 waterfall 有對平（起點 + 驅動因素 = 終點）
4. 用顏色標示：有利用綠色、不利用紅色（視覺化圖表中）
5. 每根長條都標上金額和簡短說明
6. 加上一根「Total Variance」的總結長條

## 預算 vs 實際 vs 預測的比較

### 三向比較框架

| 指標 | 預算 | 預測 | 實際 | 預算差異 ($) | 預算差異 (%) | 預測差異 ($) | 預測差異 (%) |
|--------|--------|----------|--------|-------------|-------------|---------------|---------------|
| Revenue | $X | $X | $X | $X | X% | $X | X% |
| COGS | $X | $X | $X | $X | X% | $X | X% |
| Gross Profit | $X | $X | $X | $X | X% | $X | X% |

### 什麼時候用哪一種比較

- **實際 vs 預算：** 年度績效衡量、薪酬決策、董事會報告。預算在年初設定，通常不會更動。
- **實際 vs 預測：** 營運管理、找出浮現中的問題。預測會定期（每月或每季）更新，反映目前的預期。
- **預測 vs 預算：** 了解自規劃以來預期如何改變。適合用來找出規劃準確度的問題。
- **實際 vs 前期：** 趨勢分析、連續期間績效。預算沒有意義時很有用（新業務線、收購後）。
- **實際 vs 去年同期：** 年增長分析、排除季節性的比較。

### 預測準確度分析

追蹤預測隨時間的準確度，以改善規劃：

```
Forecast Accuracy = 1 - |Actual - Forecast| / |Actual|

MAPE (Mean Absolute Percentage Error) = Average of |Actual - Forecast| / |Actual| across periods
```

| 期間 | 預測 | 實際 | 差異 | 準確度 |
|--------|----------|--------|----------|----------|
| Jan    | $X       | $X     | $X (X%)  | XX%      |
| Feb    | $X       | $X     | $X (X%)  | XX%      |
| ...    | ...      | ...    | ...      | ...      |
| **Avg**|          |        | **MAPE** | **XX%**  |

### 差異趨勢

追蹤差異在一年中如何演變，找出系統性偏差：

- **持續有利：** 預算可能太保守（藏私）
- **持續不利：** 預算可能太積極，或是執行有問題
- **不利持續擴大：** 績效惡化或目標不切實際
- **差異縮小：** 預測準確度隨年度進行而改善（正常的模式）
- **波動大：** 業務難以預測，或預測方法有問題
