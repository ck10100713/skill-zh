---
name: "grad-sem"
description: "用結構方程模型（SEM），結合測量模型（CFA）和結構模型（路徑分析），檢驗假設的因果結構。當使用者需要驗證潛在構念、檢驗中介或調節路徑、用 CFI/TLI/RMSEA/SRMR 評估模型適配度，或問到「這些變數形成因果鏈嗎」「怎麼檢驗我的理論模型」「我的測量模型有效嗎」時，就用這個 skill。"
metadata:
  category: "WP-31 量化方法"
  tags: ["SEM", "structural-equation-modeling", "CFA", "path-analysis", "model-fit", "latent-variable"]
---

# SEM 結構方程模型

## Overview

結構方程模型（SEM）同時估計測量模型（觀察指標如何對應到潛在構念）和結構模型（構念之間的方向性路徑）。它把驗證性因素分析和路徑分析整合起來，檢驗經驗資料是否和假設的理論結構一致。

## When to Use

- 檢驗一個有潛在構念和方向性路徑的完整理論模型
- 評估有多個中介變數的中介鏈（X → M → Y）
- 評估問卷題項是否適當反映其預期的構念（CFA）
- 在同一份資料上比較替代的理論模型

## When NOT to Use

- 樣本數低於 200（或每個估計參數少於 10 個個案）
- 沒有事先理論模型的探索性研究
- 所有變數都是觀察變數，模型只是簡單迴歸
- 資料嚴重非常態，而且你沒有穩健的估計方法

## Assumptions

```
IRON LAW: SEM does NOT prove causation — it tests whether data is CONSISTENT
with a hypothesized causal structure. Good fit does NOT mean the model is
correct; it means the model cannot be rejected.
```

關鍵假設：
1. 模型設定正確，遺漏路徑或構念會讓估計產生偏誤
2. ML 估計需要多變量常態性（或使用穩健估計方法）
3. 樣本數夠大（經驗法則是 N ≥ 200）
4. 指標之間沒有過度的共線性

## Methodology

### Step 1 — Specify the Measurement Model

定義潛在構念及其觀察指標。跑 CFA 來確認因素負荷量，評估收斂效度（AVE ≥ 0.50）和區辨效度。

### Step 2 — Assess Measurement Model Fit

評估適配度指標：CFI ≥ 0.90、TLI ≥ 0.90、RMSEA ≤ 0.08、SRMR ≤ 0.08。謹慎檢視修正指標，只有在有理論依據時才重新設定模型。

### Step 3 — Specify and Estimate the Structural Model

根據理論，加入潛在構念之間的方向性路徑。估計路徑係數及其顯著性。用卡方差異檢定比較巢套模型。

### Step 4 — Report and Interpret

報告標準化路徑係數、內生構念的 R²，以及整體適配度。如果假設有中介，就討論間接效果。數學記號和估計細節見 `references/estimation.md`。

## Output Format

```markdown
## SEM Analysis: [Study Title]

### Measurement Model (CFA)
| Construct | Indicator | Std. Loading | AVE | CR |
|-----------|-----------|-------------|-----|-----|
| [name] | [item] | x.xx | x.xx | x.xx |

### Model Fit
| Index | Value | Threshold | Assessment |
|-------|-------|-----------|------------|
| CFI | x.xx | ≥ 0.90 | [pass/fail] |
| TLI | x.xx | ≥ 0.90 | [pass/fail] |
| RMSEA | x.xx | ≤ 0.08 | [pass/fail] |
| SRMR | x.xx | ≤ 0.08 | [pass/fail] |

### Structural Paths
| Path | Std. β | S.E. | p-value | Supported? |
|------|--------|------|---------|------------|
| X → M | x.xx | x.xx | x.xx | [Yes/No] |

### Key Findings
- [Interpretation of results]

### Limitations
- [Note any assumption violations]
```

## Gotchas

- 一定存在適配度相同、但因果方向不同的等價模型，SEM 無法區分它們
- 修正指標會誘使人做資料驅動的重新設定，利用的是機運
- 把題項打包（parceling）會掩蓋測量模型的設定錯誤
- N > 500 時，卡方檢定過度敏感，要靠近似適配度指標
- 非常態的資料需要用 MLR 或 bootstrapping，不要用預設的 ML
- 只報告顯著的路徑，沒有完整的假設模型，是選擇性報告

## References

- Kline, R. B. (2016). *Principles and Practice of Structural Equation Modeling* (4th ed.). Guilford Press.
- Hu, L., & Bentler, P. M. (1999). Cutoff criteria for fit indexes. *Structural Equation Modeling*, 6(1), 1-55.
- Anderson, J. C., & Gerbing, D. W. (1988). Structural equation modeling in practice. *Psychological Bulletin*, 103(3), 411-423.
