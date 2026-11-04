---
name: "grad-fama-french"
description: "用 Fama-French 三因子模型，把資產報酬拆解成市場、規模與價值因子。當使用者需要解釋報酬的橫斷面差異、評估基金在 CAPM alpha 之外的績效、評估投資組合的小型股或價值股傾斜，或問到「為什麼小型股報酬比較高」「價值溢酬是真的嗎」「什麼因子驅動報酬」時，就用這個 skill。"
metadata:
  category: "WP-26 財務理論"
  tags: ["Fama-French", "three-factor", "SMB", "HML", "factor-model", "asset-pricing"]
---

# Fama-French Three-Factor Model

## Overview

Fama 和 French（1993）在 CAPM 上加了兩個因子，也就是規模（SMB）和價值（HML），用來解釋 CAPM 單獨無法捕捉的股票報酬橫斷面變異。這個模型顯示，小型股和高帳面市值比的股票會賺到系統性的溢酬。

## When to Use

- 解釋為什麼某些投資組合的 CAPM alpha 不為零
- 在控制因子曝險之後，評估基金經理人的能力
- 建構傾斜特定因子的投資組合
- 資產定價異常現象的學術研究

## When NOT to Use

- 固定收益或衍生性商品定價（這些是股票導向的因子）
- 該市場沒有可用的因子資料
- 當作完整的模型：獲利能力和投資因子也可能重要（五因子）

## Assumptions

```
IRON LAW: Single-factor models (CAPM) underestimate expected returns
for small-cap and value stocks. Size and value represent systematic
risk factors that command their own premia.
```

關鍵假設：
1. SMB 和 HML 捕捉的是系統性風險，不是錯誤定價
2. 因子溢酬在不同時期和市場中是持續的
3. 因子是由可觀察、有再平衡的投資組合建構出來的

## Methodology

### Step 1 — Obtain Factor Data

- Rm-Rf：市場超額報酬
- SMB（Small Minus Big）：小型股投資組合報酬減大型股投資組合報酬
- HML（High Minus Low）：高 B/M 投資組合報酬減低 B/M 投資組合報酬

### Step 2 — Run Time-Series Regression

Ri - Rf = ai + bi(Rm-Rf) + si(SMB) + hi(HML) + ei。建構細節見 `references/`。

### Step 3 — Interpret Factor Loadings

- bi：對市場的敏感度（和 CAPM 的 beta 相同）
- si：規模曝險（正值 = 傾向小型股）
- hi：價值曝險（正值 = 傾向價值股，負值 = 傾向成長股）

### Step 4 — Evaluate Alpha

如果 alpha（ai）在統計上不顯著，報酬就是由因子曝險解釋，表示沒有經理人的能力。

## Output Format

```markdown
## Fama-French Analysis: [Fund / Portfolio]

### Regression Results
| Factor | Loading | t-stat | Interpretation |
|--------|---------|--------|----------------|
| Market (Rm-Rf) | x.xx | x.xx | [market exposure] |
| SMB | x.xx | x.xx | [size tilt] |
| HML | x.xx | x.xx | [value tilt] |
| Alpha | x.xx% | x.xx | [skill or luck] |

### R-squared
- Three-factor R2: x% vs CAPM R2: x%

### Conclusions
- [Factor attribution summary]
- [Manager skill assessment]
```

## Gotchas

- 因子溢酬會隨國家和時期而變，不保證會持續
- HML 在論文發表後減弱了，有人把這歸因於套利
- 五因子模型（2015）加入了獲利能力（RMW）和投資（CMA），三因子可能不夠
- 因子的建構方法很重要，不同的切分點會得出不同結果
- 高 R-squared 不代表模型「正確」，只代表因子解釋了變異
- 因子代表風險還是錯誤定價，爭論還在持續

## References

- Fama, E. & French, K. (1993). Common risk factors in the returns on stocks and bonds. *Journal of Financial Economics*, 33(1), 3-56.
- Fama, E. & French, K. (2015). A five-factor asset pricing model. *Journal of Financial Economics*, 116(1), 1-22.
- Fama, E. & French, K. (1992). The cross-section of expected stock returns. *Journal of Finance*, 47(2), 427-465.
