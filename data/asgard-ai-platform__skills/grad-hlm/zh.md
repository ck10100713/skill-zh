---
name: "grad-hlm"
description: "用階層線性模型（HLM）分析具有隨機截距與隨機斜率的巢狀資料結構，並處理組內相關與跨層級交互作用。當使用者的資料是學生巢套在學校、員工巢套在公司，或個人身上的重複測量，需要把變異拆到不同層級，或問到「巢狀資料怎麼處理」「ICC 是什麼」「群體層級的因素會調節個人層級的關係嗎」時，就用這個 skill。"
metadata:
  category: "WP-31 量化方法"
  tags: ["HLM", "multilevel-model", "nested-data", "ICC", "random-intercept", "random-slope", "cross-level"]
---

# 階層線性模型 (Hierarchical Linear Modeling)

## Overview

階層線性模型（HLM），也叫多層次模型，處理資料的巢狀結構，也就是低層級單位（例如學生、員工）集中在高層級單位（例如學校、公司）之內。它把變異拆成組內和組間兩個部分，並允許截距和斜率隨機變動，所以能產生無偏的估計和正確的標準誤。

## When to Use

- 資料有階層或巢狀結構（個人在群體之內）
- 組內相關（ICC）不可忽略（經驗法則：ICC > 0.05）
- 研究問題涉及跨層級交互作用（群體層級的變數調節個人層級的效果）
- 巢套在受試者之內的重複測量或縱貫資料（成長模型）

## When NOT to Use

- 資料沒有巢狀，或集群效應可以忽略（ICC 接近零）
- 群體數很少（Level-2 單位少於 20 個）
- 只關心固定效果，沒有群體層級的預測變數
- 巢狀結構是交叉的，不是階層式的（改用交叉隨機效果）

## Assumptions

```
IRON LAW: Ignoring nested structure when ICC is non-trivial produces
UNDERESTIMATED standard errors — leading to inflated Type I error rates.
OLS treats clustered observations as independent, overstating precision.
```

關鍵假設：
1. Level-1 殘差呈常態分布，而且組內變異數固定
2. 隨機效果（截距、斜率）在各組之間呈常態分布
3. 隨機效果和 Level-1、Level-2 的預測變數獨立（除非有建模處理）
4. 有足夠數量的 Level-2 單位，才能穩定估計變異成分

## Methodology

### Step 1 — Estimate the Null Model (Unconditional)

跑只有截距的模型，計算 ICC = τ₀₀ / (τ₀₀ + σ²)。這告訴你總變異中有多大比例落在組間。如果 ICC 接近零，可能就不需要 HLM。

### Step 2 — Add Level-1 Predictors (Random Intercept Model)

加入個人層級的預測變數，並用隨機截距。如果研究問題要區分組內和組間效果，就對 Level-1 預測變數做組平均置中。置中的決定與公式見 `references/`。

### Step 3 — Add Level-2 Predictors and Cross-Level Interactions

加入群體層級的預測變數，解釋截距的組間變異。加入跨層級交互作用，檢驗群體特徵是否調節個人層級的斜率。如果理論上說得通，就讓斜率隨機變動。

### Step 4 — Evaluate Model and Report

用 deviance（-2LL）、AIC、BIC 比較模型。報告含穩健標準誤的固定效果、變異成分，以及各層級解釋的變異比例。

## Output Format

```markdown
## HLM Analysis: [Study Title]

### Data Structure
| Level | Unit | N |
|-------|------|---|
| Level 1 | [individual] | xxx |
| Level 2 | [group] | xxx |

### ICC (Null Model)
- ICC = x.xx (x% of variance is between groups)

### Fixed Effects
| Predictor | Level | γ | S.E. | t | p-value |
|-----------|-------|---|------|---|---------|
| Intercept | — | x.xx | x.xx | x.xx | x.xx |
| [L1 var] | 1 | x.xx | x.xx | x.xx | x.xx |
| [L2 var] | 2 | x.xx | x.xx | x.xx | x.xx |
| [Cross-level] | 1×2 | x.xx | x.xx | x.xx | x.xx |

### Random Effects
| Component | Variance | SD | p-value |
|-----------|----------|-----|---------|
| Intercept (τ₀₀) | x.xx | x.xx | x.xx |
| Slope (τ₁₁) | x.xx | x.xx | x.xx |
| Residual (σ²) | x.xx | x.xx | — |

### Model Comparison
| Model | -2LL | AIC | Parameters | Δ deviance (p) |
|-------|------|-----|------------|---------------|
| Null | x.xx | x.xx | x | — |
| Final | x.xx | x.xx | x | x.xx (x.xx) |

### Limitations
- [Note any assumption violations]
```

## Gotchas

- 總平均置中和組平均置中回答的是根本不同的研究問題
- Level-2 單位太少（< 20）會讓變異成分的估計有偏
- 沒有理論依據就加入隨機斜率，可能造成不收斂
- 加入 Level-1 預測變數會重新分配變異時，Level-2 的 pseudo-R² 可能是負的
- 如果存在 Level-3 巢狀（學生在班級、班級在學校）卻忽略它，會讓 Level-2 的估計有偏
- Level-1 和 Level-2 預測變數之間的共線性，會膨脹跨層級交互作用的標準誤

## References

- Raudenbush, S. W., & Bryk, A. S. (2002). *Hierarchical Linear Models* (2nd ed.). Sage.
- Hox, J. J., Moerbeek, M., & van de Schoot, R. (2018). *Multilevel Analysis* (3rd ed.). Routledge.
- Snijders, T. A. B., & Bosker, R. J. (2012). *Multilevel Analysis* (2nd ed.). Sage.
