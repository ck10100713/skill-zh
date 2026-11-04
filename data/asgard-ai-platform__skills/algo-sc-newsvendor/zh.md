---
name: "algo-sc-newsvendor"
description: "解報童問題（newsvendor problem），處理需求不確定下的單期訂購決策。當使用者需要決定易腐商品、季節性商品或一次性採購的最佳訂購量時就用這個 skill，即使他們說的是「這一季要訂多少」「易腐庫存」或「單期訂購」。"
metadata:
  category: "WP-41 供應鏈演算法"
  tags: ["supply-chain", "newsvendor", "inventory", "demand-uncertainty"]
---

# Newsvendor Model

## Overview

Newsvendor 模型用來決定單一銷售期、需求不確定時的最佳訂購量。它要在過剩成本（Co = 成本 - 殘值）和缺貨成本（Cu = 售價 - 成本）之間取得平衡。最佳 Q* 滿足：P(D ≤ Q*) = Cu / (Cu + Co)，也就是所謂的臨界比率（critical ratio）解。

## When to Use

**觸發條件：**
- 一次性或季節性的採購決策（時尚商品、節慶商品、活動門票）
- 沒有機會補貨的易腐商品
- 在還看不到需求之前，先設定初始備貨水準

**不適用的情況：**
- 需求穩定、持續補貨的情況（改用 EOQ）
- 可以接受延後交貨（backorder）、需求會順延到下一期時（用多期模型）

## Algorithm

```
IRON LAW: The Critical Ratio Determines Optimal Service Level
Q* = F⁻¹(Cu / (Cu + Co)) where F⁻¹ is the inverse demand CDF.
If margin is high relative to cost (Cu >> Co), order MORE (high service level).
If margin is low relative to excess cost (Co >> Cu), order LESS (low service level).
The optimal solution almost NEVER equals expected demand.
```

### Phase 1: Input Validation
定義：單位成本（c）、售價（p）、殘值（v）、需求分布（平均 μ、標準差 σ）。計算：Cu = p - c，Co = c - v。
**Gate：** p > c > v（有獲利，且過剩成本為正），需求分布已經估計出來。

### Phase 2: Core Algorithm
1. 臨界比率：CR = Cu / (Cu + Co) = (p - c) / (p - v)
2. 如果需求 ~ Normal(μ, σ)：Q* = μ + z(CR) × σ，其中 z(CR) 是 CR 對應的標準常態分布反函數值
3. 期望利潤 = Cu × E[min(Q,D)] - Co × E[max(Q-D, 0)]
4. 期望銷售量 = μ - σ × L(z)，其中 L(z) 是標準損失函數（standard loss function）

### Phase 3: Verification
檢查：Q* > 0，CR 介於 0 和 1 之間，而且依 CR 大於或小於 0.5，Q* 要相對應地高於或低於 μ。
**Gate：** Q* 相對於平均需求的方向正確。

### Phase 4: Output
回傳最佳訂購量，附上利潤分析。

## Output Format

```json
{
  "optimal_quantity": 130,
  "critical_ratio": 0.71,
  "expected_profit": 2800,
  "expected_leftover": 15,
  "expected_stockout_probability": 0.29,
  "metadata": {"price": 50, "cost": 20, "salvage": 5, "demand_mean": 100, "demand_std": 30}
}
```

## Examples

### Sample I/O
**輸入：** p=$50, c=$20, v=$5, D~Normal(100, 30)
**預期結果：** Cu=30, Co=15, CR=30/45=0.667, z=0.43, Q*=100+0.43×30=113 單位。

### Edge Cases
| 輸入 | 預期結果 | 原因 |
|-------|----------|-----|
| v = 0（全額損失） | Q* 較低，偏保守 | 過剩成本高，把訂購量往下推 |
| p >> c（高毛利） | Q* 遠高於平均值 | 值得冒著過剩的風險，避免損失銷售 |
| σ = 0（需求確定） | Q* 剛好等於 μ | 沒有不確定性，需求多少就訂多少 |

## Gotchas

- **分布的選擇很重要**：常態分布會出現負需求。平均值低的品項要用 Poisson 或截斷常態分布（truncated normal）。變異係數（CV）高時用 lognormal。
- **需求估計**：最難的是估 μ 和 σ。可以用歷史資料、專家判斷，或是用早期銷售訊號做貝氏更新（Bayesian updating）。
- **風險趨避**：Newsvendor 模型是風險中立的。風險趨避的決策者相對於 Q* 會系統性地少訂，要針對這種行為偏誤做調整。
- **多產品限制**：多個產品共用預算限制時，要解帶限制的 newsvendor（Lagrangian relaxation）。
- **殘值假設**：模型假設所有過剩的貨都能以 v 的價格處理掉。如果處理要花錢（v < 0），模型仍然成立，但 Q* 會再往下掉。

## Scripts

| Script | Description | Usage |
|--------|-------------|-------|
| `scripts/newsvendor.py` | 計算 newsvendor 最佳訂購量、期望利潤和滿足率（fill rate） | `python scripts/newsvendor.py --help` |

執行 `python scripts/newsvendor.py --verify` 可以跑內建的基本檢查測試。

## References

- 多產品帶限制的 newsvendor，請見 `references/constrained-newsvendor.md`
- 需求分布的配適，請見 `references/demand-fitting.md`
