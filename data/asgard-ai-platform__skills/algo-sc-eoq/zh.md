---
name: "algo-sc-eoq"
description: "計算經濟訂購量（Economic Order Quantity），把總庫存成本（訂購成本 + 持有成本）壓到最低。當使用者需要決定最佳訂購量、在訂購頻率與倉儲成本之間取得平衡，或設定再訂購點時就用這個 skill，即使他們說的是「要訂多少」「最佳批量」或「庫存成本最小化」。"
metadata:
  category: "WP-41 供應鏈演算法"
  tags: ["supply-chain", "eoq", "inventory", "ordering"]
---

# 經濟訂購量（Economic Order Quantity, EOQ）

## Overview

EOQ 要找出讓總庫存成本最小的訂購量，總庫存成本 = 訂購成本 + 持有成本。公式：EOQ = √(2DS/H)，其中 D = 年需求量，S = 每次訂購成本，H = 每單位每年的持有成本。前提是需求固定，而且補貨瞬間完成。

## When to Use

**觸發條件：**
- 設定庫存補貨的標準訂購量
- 在訂購頻率與倉儲成本之間取得平衡
- 在加上安全庫存調整之前，先算出基準值

**不適用的情況：**
- 需求高度不確定時（改用 newsvendor 模型）
- 商品會腐壞、保存期限很短
- 數量折扣讓成本結構大幅改變

## Algorithm

```
IRON LAW: EOQ Assumes CONSTANT, KNOWN Demand
If demand is variable or uncertain, EOQ gives the wrong answer.
Real-world application: use EOQ as a starting point, then add
safety stock for demand variability and lead time uncertainty.
Total cost curve is flat near EOQ — ±20% from optimal Q changes
total cost by only ~2%.
```

### Phase 1: Input Validation
確認：D（年需求量，單位數）、S（每次訂購的固定成本）、H（每單位每年持有成本 = 單位成本 × 持有率，通常是單位價值的 20-30%）。
**Gate：** 所有成本都是正數，需求估計合理。

### Phase 2: Core Algorithm
1. EOQ = √(2 × D × S / H)
2. 每年訂購次數 = D / EOQ
3. 再訂購點 = d × L（每日需求 × 前置時間天數）
4. 在 Q = EOQ 時，年總成本 = (D/Q × S) + (Q/2 × H)

### Phase 3: Verification
檢查：訂購成本項 ≈ 持有成本項（在 EOQ 時兩者相等），而且總成本在最低點。
**Gate：** 訂購成本 ≈ 持有成本（±5%）。

### Phase 4: Output
回傳 EOQ，附上成本拆解和再訂購點。

## Output Format

```json
{
  "eoq": 500,
  "orders_per_year": 20,
  "reorder_point": 150,
  "annual_cost": {"ordering": 2000, "holding": 2000, "total": 4000},
  "metadata": {"demand": 10000, "order_cost": 100, "holding_cost": 4.0}
}
```

## Examples

### Sample I/O
**輸入：** D=10,000 單位/年，S=$100/次，H=$4/單位/年
**預期結果：** EOQ = √(2×10000×100/4) = √500000 = 707 單位

### Edge Cases
| 輸入 | 預期結果 | 原因 |
|-------|----------|-----|
| S 很高、H 很低 | EOQ 很大，訂購次數少 | 把昂貴的訂購次數降到最低 |
| S 很低、H 很高 | EOQ 很小，訂購頻繁 | 把昂貴的持有成本降到最低 |
| D = 0 | EOQ = 0，不用訂購 | 沒有需求，就不需要訂購 |

## Gotchas

- **低估持有成本**：H 應該包含資金成本、倉儲、保險、過時報廢、搬運。公司常常只算倉庫租金，結果 H 被低估。
- **成本曲線很平**：在 EOQ 附近，總成本對訂購量不敏感。把 EOQ 湊成方便的數字（整個棧板、整個貨櫃）幾乎不會多花錢。
- **數量折扣**：在特定數量有價格門檻時，訂得比 EOQ「更多」可能反而更便宜。要比較 EOQ 和各個折扣門檻的總成本。
- **前置時間的變異**：EOQ 只管「訂多少」，不管「何時訂」。要加安全庫存：SS = z × σ_demand × √(lead time)。
- **多品項協調**：多個品項共用訂購成本（同一個供應商）時，要用聯合補貨模型，不要各算各的 EOQ。

## Scripts

| Script | Description | Usage |
|--------|-------------|-------|
| `scripts/eoq.py` | 計算經濟訂購量與成本拆解 | `python scripts/eoq.py --help` |

執行 `python scripts/eoq.py --verify` 可以跑內建的基本檢查測試。

## References

- 含數量折扣的 EOQ，請見 `references/eoq-discounts.md`
- 安全庫存計算，請見 algo-sc-safety-stock
