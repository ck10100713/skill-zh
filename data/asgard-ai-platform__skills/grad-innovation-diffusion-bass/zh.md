---
name: "grad-innovation-diffusion-bass"
description: "用 Bass 擴散模型（1969），透過創新係數與模仿係數預測創新的採用。當使用者需要預測新產品的採用曲線、估計市場滲透的時間點、根據擴散動態校準上市策略，或問到「這會擴散得多快」「採用什麼時候會起飛」「預期的 S 曲線長什麼樣」時，就用這個 skill。"
metadata:
  category: "WP-25 行銷理論"
  tags: ["Bass-model", "diffusion", "innovation", "adoption", "S-curve", "forecasting", "new-product"]
---

# Bass Diffusion Model

## Overview

Bass 模型（1969）描述新產品如何透過兩股力量被採用：創新（外部影響，係數 p）和模仿（內部 / 口碑影響，係數 q）。由此得到的採用曲線呈 S 型，形狀完全由 p、q 和市場潛量 m 決定。

## When to Use

- 預測新產品或新技術的採用軌跡
- 估計銷量達到高峰的時間和總市場滲透率
- 在廣告（p）和口碑（q）之間校準行銷花費
- 比較不同產品類別或市場的擴散模式

## When NOT to Use

- 重複購買或消耗性產品（Bass 只模擬首次採用）
- 有強烈網絡效應、需要明確網絡模型的市場
- 沒有類似產品的資料，無法估計 p 和 q

## Assumptions

```
IRON LAW: The ratio q/p determines adoption shape. High q/p means
word-of-mouth dominates and adoption exhibits a sharp peak; low q/p
means advertising-driven gradual uptake. This ratio is the single
most diagnostic parameter.
```

關鍵假設：
1. 市場潛量（m）固定而且已知
2. 採用者不會停用（基本模型沒有流失）
3. 產品在擴散期間不會改變
4. 創新效應和模仿效應互相獨立，而且可以相加

## Methodology

### Step 1 — Define market potential (m)

估計總可觸及市場。可以用類似產品、問卷或由上而下的市場規模估算。這是累積採用的上限。

### Step 2 — Estimate p and q coefficients

估計的來源：
- **類比**：用類似產品的 p 和 q（Sultan、Farley 與 Lehmann 1990 年的統合分析：平均 p = 0.03，q = 0.38）
- **歷史資料**：用非線性最小平方法，把 Bass 模型擬合到早期的採用資料
- **專家判斷**：根據行銷計畫的強度來校準

### Step 3 — Generate the adoption curve

Bass 模型的風險率：

f(t) / [1 - F(t)] = p + q * F(t)

其中 F(t) = 時間 t 的累積採用比例。

關鍵的衍生指標：
- **Time to peak**：t* = [ln(q) - ln(p)] / (p + q)
- **Peak adoption rate**：f(t*) = m(p + q)^2 / (4q)
- **Inflection point**：當 F(t) = (q - p) / (2q) 時

### Step 4 — Interpret and strategize

| q/p Ratio | Pattern | Strategy Implication |
|-----------|---------|---------------------|
| q/p > 20 | 高峰陡峭，口碑驅動 | 積極培植早期採用者 |
| q/p = 5-20 | 中等高峰 | 在廣告與口碑之間取得平衡 |
| q/p < 5 | 緩慢，廣告驅動 | 持續大眾媒體活動 |

## Output Format

```markdown
## Bass Diffusion Forecast: [Product/Innovation]

### Parameters
- Market potential (m): [value]
- Innovation coefficient (p): [value] (source: [analogy/data/expert])
- Imitation coefficient (q): [value] (source: [analogy/data/expert])
- q/p ratio: [value] — [interpretation]

### Forecast
- Time to peak sales: t* = [value]
- Peak adoption rate: [value] units/period
- Time to 50% penetration: [value]
- Time to 90% penetration: [value]

### Strategic Implications
1. [Launch strategy based on q/p ratio]
2. [Marketing mix recommendation]
3. [Timing considerations]
```

## Gotchas

- 市場潛量（m）是最敏感但也最難估計的參數，要做敏感度測試
- 基本的 Bass 模型假設期間內沒有價格變動、競爭者進入或產品更新
- 廣義 Bass 模型（Bass 等人，1994）納入了行銷組合變數，有價格或廣告資料時就用它
- 數位產品因為社群媒體的放大效應，q 值通常比較高
- 沒有做文化調整，不要把一個地區的 p 和 q 外推到另一個地區
- 早期資料（拐點之前）得到的參數估計不穩定，至少等 3 到 4 期的銷售資料

## References

- Bass, F. M. (1969). A new product growth for model consumer durables. *Management Science*, 15(5), 215-227.
- Bass, F. M., Krishnan, T. V., & Jain, D. C. (1994). Why the Bass model fits without decision variables. *Marketing Science*, 13(3), 203-223.
- Sultan, F., Farley, J. U., & Lehmann, D. R. (1990). A meta-analysis of applications of diffusion models. *Journal of Marketing Research*, 27(1), 70-77.
