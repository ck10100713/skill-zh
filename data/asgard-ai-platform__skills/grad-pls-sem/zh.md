---
name: "grad-pls-sem"
description: "用偏最小平方結構方程模型（PLS-SEM），搭配反映性與形成性測量模型，最大化內生構念的解釋變異。當使用者樣本小、有形成性指標或是探索性模型，需要評估 AVE/CR/HTMT，或問到「該用 PLS 還是 CB-SEM」「形成性構念怎麼處理」「路徑係數的顯著性怎麼看」時，就用這個 skill。"
metadata:
  category: "WP-31 量化方法"
  tags: ["PLS-SEM", "partial-least-squares", "SmartPLS", "formative", "reflective", "AVE", "HTMT"]
---

# PLS-SEM 偏最小平方法結構方程模型

## Overview

PLS-SEM（Wold，1982；Hair 等人，2017）是以變異為基礎的結構方程模型取徑，估計以組合（composite）為基礎的路徑模型。和 CB-SEM 不同，它最大化內生構念的解釋變異，並且能輕易處理反映性和形成性兩種測量模型。

## When to Use

- 研究設計中有形成性測量模型
- 樣本數小（PLS 在 N ≥ 指向任一構念的最大路徑數的 10 倍時可行）
- 研究目標是預測和解釋變異，不是驗證理論
- 結構模型複雜，有很多構念和指標

## When NOT to Use

- 研究目標是嚴格的理論檢驗和模型適配度評估
- 所有構念都是反映性的，而且樣本數足夠做 CB-SEM
- 需要整體模型適配度指標（卡方、CFI、RMSEA）
- 假設有循環關係（非遞迴模型）

## Assumptions

```
IRON LAW: PLS-SEM maximizes VARIANCE EXPLAINED, not model fit — it does NOT
test overall model fit like CB-SEM. A high R² does not mean the model
structure is correct.
```

關鍵假設：
1. 預測變數的設定：每個構念都必須正確設定為反映性或形成性
2. 結構模型中沒有循環（非遞迴）關係
3. 觀察值彼此獨立（沒有擴充方法的話，不能有巢狀結構）
4. 資料不需要是常態分布（PLS 不假設分配）

## Methodology

### Step 1 — Specify Measurement Models

把每個構念分類為反映性（箭頭從構念指向指標）或形成性（箭頭從指標指向構念）。形成性構念至少需要兩個指標，並有理論依據。

### Step 2 — Assess Reflective Measurement

評估指標信度（載荷 ≥ 0.70）、內部一致性（CR ≥ 0.70）、收斂效度（AVE ≥ 0.50），以及區辨效度（HTMT < 0.90）。

### Step 3 — Assess Formative Measurement

透過 bootstrapping 檢查指標權重是否顯著。檢查指標之間的 VIF（VIF < 5.0）。評估內容效度，因為拿掉一個形成性指標，會改變構念的意義。

### Step 4 — Evaluate Structural Model

報告路徑係數、R²、f² 效果量、Q² 預測相關性（透過 blindfolding），以及 bootstrap 信賴區間。演算法細節見 `references/`。

## Output Format

```markdown
## PLS-SEM Analysis: [Study Title]

### Reflective Measurement Assessment
| Construct | Indicator | Loading | CR | AVE | HTMT |
|-----------|-----------|---------|-----|-----|------|
| [name] | [item] | x.xx | x.xx | x.xx | x.xx |

### Formative Measurement Assessment
| Construct | Indicator | Weight | VIF | p-value |
|-----------|-----------|--------|-----|---------|
| [name] | [item] | x.xx | x.xx | x.xx |

### Structural Model
| Path | β | t-value | p-value | f² | Supported? |
|------|---|---------|---------|-----|------------|
| X → Y | x.xx | x.xx | x.xx | x.xx | [Yes/No] |

### Model Quality
| Endogenous Construct | R² | Q² |
|---------------------|-----|-----|
| [name] | x.xx | x.xx |

### Limitations
- [Note any assumption violations]
```

## Gotchas

- PLS-SEM 不是小樣本的萬靈丹，它仍然需要足夠的統計檢定力
- 把反映性誤設為形成性（或反過來），會從根本上改變結果
- 在 PLS-SEM 中，區辨效度偏好用 HTMT，不用 Fornell-Larcker
- PLS 會高估載荷、低估路徑係數（大樣本一致性 PLSc 可以修正）
- Blindfolding 的 Q² > 0 顯示有預測相關性，但不能驗證模型結構
- 用 CB-SEM 的標準（CFI、RMSEA）報告 PLS 的結果，在方法上是錯的

## References

- Hair, J. F., Hult, G. T. M., Ringle, C. M., & Sarstedt, M. (2017). *A Primer on Partial Least Squares Structural Equation Modeling* (2nd ed.). Sage.
- Henseler, J., Ringle, C. M., & Sarstedt, M. (2015). A new criterion for assessing discriminant validity. *Journal of the Academy of Marketing Science*, 43(1), 115-135.
- Hair, J. F., Risher, J. J., Sarstedt, M., & Ringle, C. M. (2019). When to use and how to report PLS-SEM. *European Business Review*, 31(1), 2-24.
