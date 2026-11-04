---
name: "grad-real-options"
description: "用實質選擇權分析，評估投資決策中內含的管理彈性價值。當使用者需要評估高度不確定、具有彈性的專案、評估延後或擴大投資的價值、比較傳統 NPV 和擴展 NPV，或問到「我們該等一等再投資嗎」「放棄選擇權值多少」「為什麼 NPV 低估了這個專案」時，就用這個 skill。"
metadata:
  category: "WP-26 財務理論"
  tags: ["real-options", "NPV", "managerial-flexibility", "option-to-defer", "investment-decision", "uncertainty"]
---

# Real Options

## Overview

實質選擇權理論把金融選擇權的定價邏輯，套用到公司的投資決策上。它承認經理人可以隨著不確定性的消解調整決策，包括延後、擴大、縮小或放棄專案。傳統的 NPV 假設要嘛現在就承諾，要嘛就錯過，會系統性地低估有重大彈性的專案。

## When to Use

- 評估高度不確定、有管理彈性的投資
- 比較分階段與一次承諾的投資策略
- 評價天然資源開採、研發或平台投資
- NPV 接近零，但專案有策略性的選擇權

## When NOT to Use

- 例行、低不確定性的投資，NPV 就夠了
- 彈性在契約上或實務上並不存在
- 選擇權的執行條件不明確，或無法量化

## Assumptions

```
IRON LAW: Traditional NPV undervalues projects with significant
managerial flexibility. Expanded NPV = Static NPV + Option Value.
Ignoring optionality leads to systematic underinvestment in
high-uncertainty, high-flexibility projects.
```

關鍵假設：
1. 經理人能夠、也會最佳地運用彈性
2. 標的資產價值遵循隨機過程
3. 選擇權的執行是可行的（法律、組織、技術上）
4. 存在市場（或有代理指標）可以估計波動度

## Methodology

### Step 1 — Identify Embedded Options

| Option Type | Description | Example |
|-------------|-------------|---------|
| Defer | 等待更好的資訊 | 土地開發 |
| Expand | 成功的話就擴大規模 | 平台投資 |
| Contract | 情況惡化就縮小規模 | 模組化生產 |
| Abandon | 退出並回收殘值 | 研發專案 |
| Switch | 改變投入或產出 | 彈性燃料電廠 |

### Step 2 — Map to Option Parameters

- 標的資產價值（S）：專案現金流的現值
- 履約價格（K）：投資成本或殘值
- 到期時間（T）：決策窗口
- 波動度（sigma）：專案價值的不確定性
- 無風險利率（r）：選擇權定價的折現率

### Step 3 — Value the Option

使用二項樹狀模型或 Black-Scholes 的類比。數學公式見 `references/`。

### Step 4 — Compute Expanded NPV

Expanded NPV = Static NPV + Option Value。如果擴展 NPV 為正，專案就值得投資，或值得保留這個選擇權。

## Output Format

```markdown
## Real Options Analysis: [Project]

### Static NPV
- NPV = $X (using traditional DCF)

### Embedded Options Identified
| Option | Type | Value Driver |
|--------|------|-------------|
| [name] | [defer/expand/abandon/...] | [key uncertainty] |

### Option Valuation
| Parameter | Value |
|-----------|-------|
| Underlying (S) | $X |
| Exercise price (K) | $X |
| Volatility | x% |
| Time (T) | X years |
| Option value | $X |

### Expanded NPV
- Static NPV + Option Value = $X
- Decision: [invest / defer / preserve option]
```

## Gotchas

- 估計實質資產的波動度，比估計有交易的證券困難得多
- 假設會最佳地執行，行為偏誤可能造成過早或過晚執行
- 選擇權之間的交互作用很重要：執行一個可能殺掉另一個（例如擴大會殺掉放棄）
- 實質選擇權可能被拿來替拖延找藉口，包裝成「保留彈性」
- Black-Scholes 的假設（連續交易、對數常態報酬）很少適用於實質資產
- 組織真正有能力執行選擇權的程度，常常被高估

## References

- Dixit, A. & Pindyck, R. (1994). *Investment Under Uncertainty*. Princeton University Press.
- Trigeorgis, L. (1996). *Real Options: Managerial Flexibility and Strategy*. MIT Press.
- Myers, S. (1977). Determinants of corporate borrowing. *Journal of Financial Economics*, 5(2), 147-175.
