---
name: "meta-scenario-planning"
description: "用驅動力、不確定性軸線和 2x2 情境矩陣做情境規劃，為多種可能的未來做準備。使用者面對高度不確定性、需要拿不同的未來來壓力測試某個策略，或要準備應變計畫時使用，就算他們說的是「萬一出問題怎麼辦」、「未來可能長什麼樣子」、「我們要怎麼為不確定性做準備」或「幫我們的策略做壓力測試」也一樣。"
metadata:
  category: "WP-22 跨學科"
  tags: ["meta-thinking", "scenario-planning", "strategy", "uncertainty"]
---

# 情境規劃

## 框架

```
IRON LAW: Scenarios Are Not Predictions

Scenarios are PLAUSIBLE futures, not forecasts. The goal is NOT to predict
which future will happen, but to prepare strategies that work across
MULTIPLE possible futures. A strategy that only works in one scenario
is fragile.
```

### 2×2 情境矩陣法

1. **找出驅動力**：哪些宏觀力量最會形塑未來？（技術、法規、經濟、人口結構、競爭）
2. **選出兩個關鍵不確定性**：影響最大、結果又最不確定的兩個力量
3. **建立 2×2 矩陣**：每條軸是一個不確定性，有兩個端點（例如「法規：嚴格 vs 寬鬆」）
4. **為四個情境命名並描述**：每個象限都是一個不同的合理未來
5. **用四個情境全部測試策略**：哪些策略在大部分／所有情境下都行得通？哪些只在一個情境下有用？

### 流程

**Step 1：驅動力（腦力激盪 10-15 個）**
- 政治、經濟、社會、技術、環境、競爭
- 每一個都評：影響（H/M/L）× 不確定性（H/M/L）
- 高影響 + 高不確定性 → 候選的軸線

**Step 2：選兩條軸**
- 選兩個既高影響、又高不確定性的力量
- 它們彼此要獨立（不相關）

**Step 3：建立四個情境**
- 給每個情境一個好記的名字（不要叫「情境 1」）
- 每個寫一段敘事：5-10 年後，這個世界是什麼樣子？

**Step 4：策略測試**
- 針對每個策略選項，評估：它在這個情境下行得通嗎？（Yes / Partial / No）
- 穩健的策略在 3-4 個情境下行得通。脆弱的策略只在 1 個情境下行得通。

## 輸出格式

```markdown
# Scenario Planning: {Context}

## Driving Forces
| Force | Impact | Uncertainty | Selected? |
|-------|--------|------------|-----------|
| {force} | H/M/L | H/M/L | ✓/— |

## Scenario Matrix
- Axis 1: {Uncertainty A} — {endpoint 1} vs {endpoint 2}
- Axis 2: {Uncertainty B} — {endpoint 1} vs {endpoint 2}

| | {A: endpoint 1} | {A: endpoint 2} |
|---|---|---|
| **{B: endpoint 1}** | **"{Scenario Name}"**: {narrative} | **"{Scenario Name}"**: {narrative} |
| **{B: endpoint 2}** | **"{Scenario Name}"**: {narrative} | **"{Scenario Name}"**: {narrative} |

## Strategy Robustness Test
| Strategy | Scenario 1 | Scenario 2 | Scenario 3 | Scenario 4 |
|----------|-----------|-----------|-----------|-----------|
| {strategy A} | ✓/△/✗ | ✓/△/✗ | ✓/△/✗ | ✓/△/✗ |

## Robust Strategies
{Strategies that work in most scenarios}

## Contingency Triggers
- If {early signal}, activate {contingency plan for scenario X}
```

## 注意事項

- **情境應該讓人不舒服**：如果四個情境都讓人覺得舒服，代表你探索的不確定性還不夠。至少要有一個你寧可不去想的情境。
- **避免「好／壞」的框架**：情境不是樂觀 vs 悲觀。每個情境都同時有機會和威脅。「嚴格法規」的世界對某些人不利，對另一些人有利。
- **早期預警訊號**：找出可觀察的指標，用來判斷哪個情境正在展開。這樣情境才會變成可行動的情報。
- **兩條軸是簡化**：現實有很多不確定性。2×2 是用來讓事情更清楚的工具，不是用來求完整。其他驅動力可以當成情境內部的變化來考慮。

## 參考資料

- Shell 原始的情境規劃方法論請看 `references/shell-method.md`
