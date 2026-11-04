---
name: "grad-event-study"
description: "用事件研究法衡量公司或市場事件前後的異常報酬與累積異常報酬（CAR）。當使用者需要量化公告對市場的影響、設計事件窗口與估計窗口，或問到「這個事件有沒有影響股價」「怎麼計算異常報酬」「市場對這個公告的反應是什麼」時，就用這個 skill。"
metadata:
  category: "WP-31 量化方法"
  tags: ["event-study", "abnormal-return", "CAR", "market-reaction", "event-window", "finance"]
---

# 事件研究法 (Event Study)

## Overview

事件研究法（Fama 等人，1969；MacKinlay，1997）把實際報酬和預期（正常）報酬的模型相比，分離出可歸因於特定事件的異常報酬。事件窗口內的累積異常報酬（CAR）量化了市場的整體反應。

## When to Use

- 衡量市場對財報公告、併購、政策變動或監管事件的反應
- 檢定半強式的市場效率
- 量化公司揭露資訊的經濟顯著性
- 比較市場對不同事件類型或公司特徵的反應

## When NOT to Use

- 事件日期不明確，或資訊是逐漸洩漏的
- 有干擾事件和事件窗口重疊
- 該公司股票流動性差，有很多零報酬的日子
- 事件早就被廣泛預期，在事件窗口之前就已完全反映在價格上

## Assumptions

```
IRON LAW: Event study validity requires that the event was UNANTICIPATED —
if the market priced it in before the event window, abnormal returns will
be zero even if the event matters.
```

關鍵假設：
1. 事件日期可以精確識別，而且事件是出乎意料的
2. 事件窗口內沒有干擾事件
3. 正常報酬模型在估計窗口內設定正確
4. 市場微結構效應（交易清淡、買賣價差跳動）不會扭曲報酬

## Methodology

### Step 1 — Define Event and Windows

找出事件日（第 0 天）。設定估計窗口（例如 [-250, -11]）來估計正常報酬。設定事件窗口（例如 [-1, +1] 或 [-5, +5]）來捕捉反應。

### Step 2 — Estimate Normal Returns

使用市場模型：Ri,t = αi + βi × Rm,t + εi,t，在估計窗口內估計。替代方案包括固定平均報酬或 Fama-French 因子。模型設定見 `references/`。

### Step 3 — Compute Abnormal and Cumulative Abnormal Returns

AR = 事件窗口內每一天的實際報酬 - 預期報酬。CAR = 事件窗口內 AR 的加總。跨公司計算 CAAR（累積平均異常報酬）。

### Step 4 — Statistical Testing

用參數檢定（橫斷面 t 檢定、Patell 檢定）和無母數檢定（符號檢定、秩檢定）檢定 H₀: CAR = 0。兩種都報告，確保穩健。

## Output Format

```markdown
## Event Study: [Event Description]

### Window Design
| Window | Period | Rationale |
|--------|--------|-----------|
| Estimation | [-250, -11] | [rationale] |
| Event | [-1, +1] | [rationale] |

### Abnormal Returns
| Day | AR (%) | t-stat |
|-----|--------|--------|
| -1 | x.xx | x.xx |
| 0 | x.xx | x.xx |
| +1 | x.xx | x.xx |

### Cumulative Abnormal Returns
| Window | CAR (%) | t-stat | p-value | Significant? |
|--------|---------|--------|---------|-------------|
| [-1, +1] | x.xx | x.xx | x.xx | [Yes/No] |

### Cross-Sectional Analysis
- [If applicable: regression of CAR on firm characteristics]

### Limitations
- [Note any confounding events or assumption violations]
```

## Gotchas

- 事件日期集中（例如全產業的法規）會違反橫斷面獨立性
- 估計窗口太短，會讓正常報酬的參數很吵
- 事件窗口太長，會提高出現干擾事件的機率
- 低價股和流動性差的證券，會人為墊高異常報酬
- 市場模型假設 beta 固定，結構性斷裂會讓這個假設失效
- 發表偏誤：發現 CAR 為零的研究很少被發表

## References

- MacKinlay, A. C. (1997). Event studies in economics and finance. *Journal of Economic Literature*, 35(1), 13-39.
- Fama, E. F., Fisher, L., Jensen, M. C., & Roll, R. (1969). The adjustment of stock prices to new information. *International Economic Review*, 10(1), 1-21.
- Kolari, J. W., & Pynnönen, S. (2010). Event study testing with cross-sectional correlation of abnormal returns. *Review of Financial Studies*, 23(11), 3996-4025.
