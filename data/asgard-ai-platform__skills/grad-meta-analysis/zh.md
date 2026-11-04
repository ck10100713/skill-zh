---
name: "grad-meta-analysis"
description: "用後設分析整合多項研究的效果量、評估異質性，並檢查發表偏誤。當使用者需要彙整既有研究的發現、比較固定效果與隨機效果模型、計算合併效果量，或問到「整體證據怎麼說」「怎麼合併多項研究的結果」「有沒有發表偏誤」時，就用這個 skill。"
metadata:
  category: "WP-31 量化方法"
  tags: ["meta-analysis", "effect-size", "heterogeneity", "publication-bias", "I-squared", "systematic-review"]
---

# 後設分析 (Meta-Analysis)

## Overview

後設分析用統計方法合併多個獨立研究的效果量，得到精確度和概化性都更高的合併估計。它量化研究之間的異質性，並檢驗發表偏誤，提供比敘事性文獻回顧更嚴謹的證據綜合。

## When to Use

- 彙整針對同一個研究問題的多項研究的量化發現
- 化解各研究之間互相衝突的結果
- 用更窄的信賴區間估計整體效果量
- 找出能解釋研究間異質性的調節變數

## When NOT to Use

- 研究在構念、測量或母群體上差異太大，無法有意義地合併
- 可用的研究少於 5 個（合併估計變得不可靠）
- 原始研究的設計根本不同（把 RCT 和觀察性研究混在一起）
- 研究問題是質性或概念性的，不是量化的

## Assumptions

```
IRON LAW: A meta-analysis is only as good as the studies it includes —
garbage in, garbage out. Publication bias inflates pooled effect sizes
because non-significant findings go unpublished.
```

關鍵假設：
1. 各研究估計的是同一個底層構念（概念上的同質性）
2. 效果量在統計上獨立（每個研究一個效果，或用多層次模型）
3. 研究層級的調節變數編碼可靠而且沒有偏誤
4. 搜尋策略涵蓋了相關的研究母群體（沒有系統性的遺漏）

## Methodology

### Step 1 — Extract and Code Effect Sizes

把各研究的發現轉換成共同的效果量指標（Cohen's d、Hedges' g、r、OR）。為研究層級的調節變數編碼（樣本數、設計、脈絡）。轉換公式見 `references/`。

### Step 2 — Choose Fixed-Effect vs Random-Effects Model

固定效果假設只有一個真實效果；隨機效果假設效果會因研究而異。如果各研究橫跨不同的母群體或脈絡，幾乎都該用隨機效果。

### Step 3 — Assess Heterogeneity

計算 Q 統計量（同質性檢定）、I²（由異質性造成的變異比例）和 τ²（研究間變異數）。I² > 75% 表示有相當大的異質性，值得做調節變數分析。

### Step 4 — Test for Publication Bias and Report

使用漏斗圖、Egger 迴歸檢定和 trim-and-fill 法。報告合併效果、信賴區間、預測區間，以及偏誤評估的結果。

## Output Format

```markdown
## Meta-Analysis: [Research Question]

### Study Inclusion
| Criterion | Value |
|-----------|-------|
| Studies included (k) | xx |
| Total sample size (N) | xxxx |
| Effect size metric | [d / r / OR] |

### Pooled Effect Size
| Model | Effect | 95% CI | z | p-value |
|-------|--------|--------|---|---------|
| Fixed-effect | x.xx | [x.xx, x.xx] | x.xx | x.xx |
| Random-effects | x.xx | [x.xx, x.xx] | x.xx | x.xx |

### Heterogeneity
| Statistic | Value | Interpretation |
|-----------|-------|----------------|
| Q | x.xx (p = x.xx) | [significant/not] |
| I² | x.xx% | [low/moderate/high] |
| τ² | x.xx | [between-study variance] |

### Publication Bias
| Test | Result | Interpretation |
|------|--------|----------------|
| Funnel plot | [symmetric/asymmetric] | [bias suspected?] |
| Egger's test | p = x.xx | [significant?] |
| Trim-and-fill | adjusted effect = x.xx | [studies imputed: x] |

### Limitations
- [Note any assumption violations]
```

## Gotchas

- 拿蘋果和橘子一起比：統計上做得到，但如果構念不同，概念上沒有意義
- 隨機效果模型會給小型研究更多權重，而小型研究的品質常常比較低
- I² 取決於納入研究的精確度，不精確的研究帶來低 I²，不代表同質
- 漏斗圖不對稱可能由發表偏誤以外的因素造成（小研究效應）
- 檔案抽屜問題：未發表的虛無結果會系統性地缺漏
- 子群很多、每個子群研究很少的調節變數分析，檢定力不足而且不可靠

## References

- Borenstein, M., Hedges, L. V., Higgins, J. P. T., & Rothstein, H. R. (2009). *Introduction to Meta-Analysis*. Wiley.
- Higgins, J. P. T., & Thompson, S. G. (2002). Quantifying heterogeneity in a meta-analysis. *Statistics in Medicine*, 21(11), 1539-1558.
- Rothstein, H. R., Sutton, A. J., & Borenstein, M. (2005). *Publication Bias in Meta-Analysis*. Wiley.
