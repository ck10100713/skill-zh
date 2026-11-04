---
name: risk-metrics-calculation
description: 計算投資組合的風險指標，包含 VaR、CVaR、Sharpe、Sortino 和 drawdown 分析。在衡量投資組合風險、實作風險限額或建構風險監控系統時使用。
---

# Risk Metrics Calculation

投資組合管理用的完整風險衡量工具箱，包含 Value at Risk、Expected Shortfall 和 drawdown 分析。

## When to Use This Skill

- 衡量投資組合風險
- 實作風險限額
- 建構風險儀表板
- 計算風險調整後報酬
- 設定部位大小
- 法規申報

## Core Concepts

### 1. Risk Metric Categories

| Category          | Metrics         | Use Case             |
| ----------------- | --------------- | -------------------- |
| **Volatility**    | Std Dev, Beta   | 一般風險         |
| **Tail Risk**     | VaR, CVaR       | 極端虧損       |
| **Drawdown**      | Max DD, Calmar  | 資本保全 |
| **Risk-Adjusted** | Sharpe, Sortino | 績效          |

### 2. Time Horizons

```
Intraday:   Minute/hourly VaR for day traders
Daily:      Standard risk reporting
Weekly:     Rebalancing decisions
Monthly:    Performance attribution
Annual:     Strategic allocation
```

## Detailed patterns and worked examples

詳細的 pattern 文件放在 `references/details.md`。上面這層導覽不夠用的時候，再去讀那個檔案。

## Best Practices

### Do's

- **用多種指標** - 沒有哪個單一指標能涵蓋所有風險
- **考慮尾部風險** - 只有 VaR 不夠，要用 CVaR
- **做滾動分析** - 風險會隨時間改變
- **做壓力測試** - 歷史情境和假設情境都要
- **把假設寫成文件** - 分佈、回看期間等等

### Don'ts

- **不要只靠 VaR** - 它會低估尾部風險
- **不要假設常態分佈** - 報酬有肥尾
- **不要忽略相關性** - 壓力時相關性會上升
- **不要用太短的回看期間** - 會錯過市場狀態的轉變
- **不要忘了交易成本** - 它會影響實際承擔的風險
