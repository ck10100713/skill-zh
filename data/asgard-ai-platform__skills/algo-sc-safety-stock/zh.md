---
name: "algo-sc-safety-stock"
description: "計算安全庫存水準，用來緩衝需求和前置時間的不確定性。當使用者需要設定庫存緩衝、權衡服務水準，或在多個 SKU 之間最佳化安全庫存時就用這個 skill，即使他們說的是「要留多少緩衝庫存」「避免缺貨」或「服務水準計算」。"
metadata:
  category: "WP-41 供應鏈演算法"
  tags: ["supply-chain", "safety-stock", "inventory", "service-level"]
---

# Safety Stock Calculation

## Overview

安全庫存是為了應付需求和前置時間變異而多留的緩衝庫存。公式：SS = z × √(LT × σ²_d + d² × σ²_LT)，其中 z = 服務係數，LT = 前置時間，σ_d = 需求標準差，d = 平均需求，σ_LT = 前置時間標準差。它直接拿庫存成本去換缺貨風險。

## When to Use

**觸發條件：**
- 為需求會波動的品項設定庫存緩衝
- 選定目標服務水準，並算出所需的安全庫存
- 在一整組 SKU 之間最佳化安全庫存

**不適用的情況：**
- 需求是確定的時候（直接用 EOQ，不需要安全庫存）
- 一次性採購決策（用 newsvendor 模型）

## Algorithm

```
IRON LAW: Safety Stock Is a TRADE-OFF, Not a Target
More safety stock = fewer stockouts but higher holding cost.
The relationship is non-linear: going from 95% to 99% service level
roughly DOUBLES safety stock. Going from 99% to 99.9% doubles it
again. Always quantify the cost of each service level increment.
z-values: 90%→1.28, 95%→1.65, 99%→2.33, 99.9%→3.09.
```

### Phase 1: Input Validation
收集：歷史需求資料（週／月）、前置時間資料（平均與變異）、目標服務水準、單位成本與持有率。
**Gate：** 至少有 12 期的需求資料，而且有前置時間的估計值。

### Phase 2: Core Algorithm
1. 計算需求統計量：平均需求（d）、需求標準差（σ_d）
2. 計算前置時間統計量：平均 LT、LT 標準差（σ_LT）
3. 計算合併變異：σ_combined = √(LT × σ²_d + d² × σ²_LT)
4. 查出目標服務水準對應的 z
5. 安全庫存 = z × σ_combined
6. 再訂購點 = d × LT + SS

### Phase 3: Verification
模擬：用歷史需求來看，算出來的 SS 能不能在目標服務水準下避免缺貨？
**Gate：** 模擬出來的服務水準符合目標（±2%）。

### Phase 4: Output
回傳安全庫存，附上成本影響和服務水準分析。

## Output Format

```json
{
  "safety_stock": 250,
  "reorder_point": 850,
  "service_level": 0.95,
  "annual_holding_cost": 5000,
  "metadata": {"avg_demand_weekly": 120, "demand_cv": 0.3, "avg_lead_time_weeks": 5}
}
```

## Examples

### Sample I/O
**輸入：** 每週需求：平均 = 100，σ = 30。前置時間：平均 = 4 週，σ = 1 週。目標：95%。
**預期結果：** σ_combined = √(4×900 + 10000×1) = √(3600+10000) = √13600 = 116.6。SS = 1.65 × 116.6 = 192 單位。

### Edge Cases
| 輸入 | 預期結果 | 原因 |
|-------|----------|-----|
| 需求完全沒有變異 | SS 只來自前置時間的變異 | σ_d = 0，只剩前置時間的風險 |
| 前置時間完全沒有變異 | SS 只來自需求的變異 | σ_LT = 0，標準公式簡化 |
| 前置時間很長 | SS 很高 | 期間越長，累積的不確定性越多 |

## Gotchas

- **常態分布假設**：公式假設需求服從常態分布。高度間歇性的需求（很多期是零）要用別的方法（Poisson、negative binomial）。
- **要看預測誤差，不是需求變異**：如果用了預測值，SS 要緩衝的是預測「誤差」（σ_error），不是原始需求的變異。
- **服務水準的定義**：週期服務水準（cycle service level，每個週期不缺貨的機率）≠ 滿足率（fill rate，需求中由庫存滿足的比例）。公司常常想要的是 fill rate，算的卻是 cycle SL。
- **前置時間資料品質**：前置時間的變異常常沒有好好追蹤。低估 σ_LT 會讓安全庫存不夠。
- **ABC 分類**：不要所有 SKU 都用同一個服務水準。A 類品項（營收高）值得 99%，C 類品項 90% 可能就夠了。

## Scripts

| Script | Description | Usage |
|--------|-------------|-------|
| `scripts/safety_stock.py` | 計算安全庫存和再訂購點，把需求與前置時間的變異合併考慮 | `python scripts/safety_stock.py --help` |

執行 `python scripts/safety_stock.py --verify` 可以跑內建的基本檢查測試。

## References

- 多階層（multi-echelon）安全庫存最佳化，請見 `references/multi-echelon.md`
- 間歇性需求的處理方法，請見 `references/intermittent-demand.md`
