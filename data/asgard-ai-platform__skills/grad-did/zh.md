---
name: "grad-did"
description: "用雙重差分法（DID）比較處理組與對照組的結果變化，估計因果處理效果。當使用者要評估政策介入、自然實驗或法規變動、需要檢定平行趨勢，或問到「這個政策有沒有用」「沒有隨機分派要怎麼識別因果效果」「處理效果是多少」時，就用這個 skill。"
metadata:
  category: "WP-31 量化方法"
  tags: ["DID", "difference-in-differences", "causal-inference", "parallel-trends", "policy-evaluation", "treatment-effect"]
---

# 雙重差分法 (Difference-in-Differences)

## Overview

雙重差分法（DID）比較處理組（受介入影響）和對照組（不受影響）在一段時間內的結果變化，藉此估計因果效果。它同時扣掉不隨時間變動的組間差異，以及共同的時間趨勢，所以在平行趨勢假設下，可以把處理效果單獨分離出來。

## When to Use

- 評估政策、法規或介入措施的影響
- 自然實驗在群體層級（州、產業、公司）分派處理
- 有處理前後期間的 panel 或重複橫斷面資料
- 無法做隨機實驗，但存在合理的對照組

## When NOT to Use

- 平行趨勢假設被違反，而且無法補救
- 處理組和對照組的差異會隨時間改變
- 處理是根據預期結果自我選擇的（預期效應）
- 只有處理後的資料（沒有處理前的基準）

## Assumptions

```
IRON LAW: DID is valid ONLY if the parallel trends assumption holds —
without it, the estimated treatment effect is biased by differential
pre-existing trends.
```

關鍵假設：
1. 平行趨勢：沒有處理的話，處理組和對照組會沿著相同的軌跡走
2. 處理單位不會對對照單位產生外溢效應（SUTVA）
3. 處理時點明確且外生
4. 各組的組成隨時間穩定（沒有差別性的流失）

## Methodology

### Step 1 — Establish Treatment and Control Groups

定義誰被處理、什麼時候被處理。驗證兩組在處理前的可觀察特徵上是可比較的。記錄處理事件與其時點。

### Step 2 — Test Parallel Trends

畫出處理組與對照組在處理前期間的結果趨勢。跑一個含 leads 和 lags 的 event-study 設定。處理前的係數在統計上應該不顯著。

### Step 3 — Estimate the DID Model

Y = β₀ + β₁×Treat + β₂×Post + β₃×(Treat×Post) + Controls + ε。係數 β₃ 就是 DID 估計量。標準誤要在處理分派的層級做 cluster。交錯採用（staggered adoption）的延伸見 `references/`。

### Step 4 — Robustness Checks

跑安慰劑檢定（假的處理日期、假的處理組）。測試結果對對照組選擇的敏感度。交錯 DID 要用 Callaway-Sant'Anna 或 Sun-Abraham 估計量。

## Output Format

```markdown
## DID Analysis: [Policy / Intervention]

### Research Design
| Element | Description |
|---------|-------------|
| Treatment group | [who] |
| Control group | [who] |
| Treatment date | [when] |
| Pre-treatment periods | [range] |

### Parallel Trends Test
| Pre-period lead | Coefficient | S.E. | p-value |
|-----------------|-------------|------|---------|
| t-3 | x.xx | x.xx | x.xx |
| t-2 | x.xx | x.xx | x.xx |
| t-1 | x.xx | x.xx | x.xx |

### DID Estimate
| Specification | β (Treat×Post) | S.E. | p-value | N |
|---------------|----------------|------|---------|---|
| Baseline | x.xx | x.xx | x.xx | xxx |
| With controls | x.xx | x.xx | x.xx | xxx |

### Robustness
- Placebo test result: [pass/fail]
- Alternative control group: [result]

### Limitations
- [Note any assumption violations]
```

## Gotchas

- 目視平行趨勢是必要條件，不是充分條件，因為這個假設講的是反事實的趨勢
- cluster 太少時，對標準誤做 cluster 會膨脹第一型錯誤（cluster < 50 時用 wild bootstrap）
- 交錯採用會讓標準的雙向固定效果 DID 估計量產生偏誤（改用近期發展的穩健估計量）
- 預期效應違反了處理時點明確的假設
- 處理前趨勢不同，常用加入組別專屬趨勢來「修正」，但這很脆弱
- DID 估計的是對受處理者的局部平均處理效果（ATT），不是 ATE

## References

- Angrist, J. D., & Pischke, J.-S. (2009). *Mostly Harmless Econometrics*. Princeton University Press.
- Callaway, B., & Sant'Anna, P. H. C. (2021). Difference-in-differences with multiple time periods. *Journal of Econometrics*, 225(2), 200-230.
- Goodman-Bacon, A. (2021). Difference-in-differences with variation in treatment timing. *Journal of Econometrics*, 225(2), 254-277.
