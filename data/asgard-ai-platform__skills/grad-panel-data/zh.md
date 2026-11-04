---
name: "grad-panel-data"
description: "用固定效果、隨機效果與動態 GMM 做追蹤資料分析，利用縱貫變異並控制未觀察到的異質性。當使用者有多個個體跨時間的重複觀察、需要用 Hausman 檢定在 FE 和 RE 之間選擇，或問到「怎麼控制公司特有的效果」「固定還是隨機效果」「面板資料的內生性怎麼處理」時，就用這個 skill。"
metadata:
  category: "WP-31 量化方法"
  tags: ["panel-data", "fixed-effects", "random-effects", "Hausman-test", "GMM", "longitudinal"]
---

# 追蹤資料分析 (Panel Data Analysis)

## Overview

追蹤資料分析同時利用橫斷面和時間上的變異來估計因果效果，同時控制未觀察到的異質性。固定效果透過個體內去平均來排除不隨時間變動的干擾因素，隨機效果則假設未觀察到的異質性和自變數無關，在有效時能得到更有效率的估計。

## When to Use

- 資料有同一批個體（公司、個人、國家）跨時間的重複觀察
- 未觀察到、不隨時間變動的因素，很可能干擾所關心的關係
- 檢驗政策或處理效果是否隨時期而異
- 動態模型，落後的應變數是迴歸變數（用 GMM）

## When NOT to Use

- 純橫斷面資料，沒有時間維度
- 想估計不隨時間變動的變數的效果（FE 會把它們消掉）
- 面板極短（T = 2），而且有很多內生的迴歸變數
- 樣本流失是非隨機的，造成存活者偏誤

## Assumptions

```
IRON LAW: Fixed effects ONLY controls for TIME-INVARIANT unobservables —
time-varying confounders remain a threat. FE does not solve all
endogeneity problems.
```

關鍵假設：
1. FE/RE 的嚴格外生性：過去、現在和未來的誤差都和迴歸變數無關
2. 特異誤差沒有序列相關（或用 cluster 穩健標準誤）
3. RE 另外假設個體效果和迴歸變數無關
4. 動態 GMM：工具變數有效，而且不要太多（工具變數擴散）

## Methodology

### Step 1 — Explore Panel Structure

報告 N（個體數）、T（時期數）、是否平衡。檢查關鍵變數的組內和組間變異。把各個體層級的趨勢視覺化。

### Step 2 — Estimate FE and RE Models

跑固定效果（組內估計量）和隨機效果（GLS）。如果有共同衝擊，就加入時間固定效果。在個體層級使用 cluster 穩健標準誤。

### Step 3 — Hausman Test for Model Selection

檢定 H₀：RE 是一致的（個體效果和迴歸變數無關）。拒絕時支持 FE。檢定統計量的推導見 `references/`。

### Step 4 — Dynamic Extensions (if needed)

如果納入落後的應變數，就用 Arellano-Bond 或 System GMM。報告 AR(1)、AR(2) 檢定，以及檢查工具變數有效性的 Hansen/Sargan 檢定。留意工具變數的數量。

## Output Format

```markdown
## Panel Data Analysis: [Study Title]

### Panel Structure
| Dimension | Value |
|-----------|-------|
| Entities (N) | xxx |
| Time periods (T) | xxx |
| Balanced? | [Yes/No] |

### Estimation Results
| Variable | FE (β) | RE (β) | GMM (β) |
|----------|--------|--------|---------|
| [var] | x.xx (x.xx) | x.xx (x.xx) | x.xx (x.xx) |

### Model Selection
| Test | Statistic | p-value | Decision |
|------|-----------|---------|----------|
| Hausman | x.xx | x.xx | [FE/RE] |
| AR(2) | x.xx | x.xx | [pass/fail] |
| Hansen J | x.xx | x.xx | [pass/fail] |

### Key Findings
- [Interpretation]

### Limitations
- [Note any assumption violations]
```

## Gotchas

- FE 會丟掉所有個體間的變異，如果大部分變異是在個體之間，FE 的估計就不精確
- Hausman 檢定在小樣本中檢定力低，不顯著不代表 RE 有效
- 工具變數太多的動態面板 GMM 會造成過度配適，並削弱 Hansen 檢定
- 當 T 很小，帶有落後應變數的 FE 估計會受 Nickell 偏誤影響
- 雙向 FE（個體 + 時間）通常是必要的，但軟體很少把它當預設
- Cluster 穩健標準誤需要足夠數量的 cluster（經驗上 N ≥ 50）

## References

- Wooldridge, J. M. (2010). *Econometric Analysis of Cross Section and Panel Data* (2nd ed.). MIT Press.
- Arellano, M., & Bond, S. (1991). Some tests of specification for panel data. *Review of Economic Studies*, 58(2), 277-297.
- Baltagi, B. H. (2013). *Econometric Analysis of Panel Data* (5th ed.). Wiley.
