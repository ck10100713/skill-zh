---
name: "grad-info-economics"
description: "用資訊經濟學診斷並修補由資訊不對稱造成的市場失靈。當使用者需要分析逆選擇、道德風險，或訊號傳遞與篩選機制，尤其是在保險、勞動、信用或產品品質市場時，就用這個 skill。"
metadata:
  category: "WP-27 賽局與制度經濟"
  tags: ["information-economics", "adverse-selection", "moral-hazard", "signaling", "screening", "market-for-lemons", "Akerlof", "Spence", "Stiglitz"]
---

# Information Economics：逆選擇、道德風險與訊號傳遞

## Overview

資訊經濟學研究雙方之間的資訊不對稱，如何造成市場失靈，並塑造制度上的回應。Akerlof 的「檸檬市場」顯示逆選擇可以讓整個市場崩潰；Spence 的訊號傳遞模型顯示有資訊的一方可以透過有成本的行動，可信地傳達品質；Rothschild-Stiglitz 的篩選顯示沒資訊的一方可以設計菜單，誘導自我選擇。這些框架合起來，解釋了為什麼保險、信用、勞動和二手商品市場會系統性地偏離競爭的理想狀態，也解釋了保固、證書和監管這類制度為什麼存在。

## When to Use

- 診斷為什麼某個市場在失靈或萎縮（品質崩壞、信用配給、保險死亡螺旋）
- 評估某個訊號（學位、認證、保固）是否可信而且有效率
- 設計篩選機制（菜單、自負額、試用期）來區分異質的行為者
- 評估政策介入（強制揭露、最低標準、補貼保險）

## When NOT to Use

- 資訊是對稱的，或能以零成本驗證（沒有不對稱的問題）
- 產品是純粹的經驗財，聲譽和重複購買就能完全解決品質不確定性
- 分析需要建模雙邊以外的策略互動（用完整的賽局理論模型）

## Assumptions

```
IRON LAW: Information asymmetry causes market failure — without
corrective mechanisms (signals, screens, warranties), bad drives out
good. Markets with severe adverse selection can unravel completely
(Akerlof's lemons result).
```

- 一方（有資訊的一方）擁有品質、風險或努力程度的私有資訊
- 另一方（沒資訊的一方）無法直接觀察相關的特徵
- 行為者是理性的，會針對資訊結構做出策略性的回應
- 訊號是有成本的，而且成本因類型而異（單交叉 / Spence-Mirrlees 條件）
- 在競爭市場中，不同類型之間的交叉補貼無法持續

## Methodology

**Step 1 — 找出資訊不對稱**
分類：(a) 逆選擇（隱藏類型，簽約前），有資訊一方的類型會影響沒資訊一方的報酬；(b) 道德風險（隱藏行動，簽約後），有資訊一方的努力無法觀察；(c) 兩者同時存在。找出誰有資訊、誰沒有。

**Step 2 — 建模市場失靈**
逆選擇：說明混同（提供單一契約）如何吸引不成比例的壞類型，推高成本、拉高價格，讓好類型退出，也就是解體動態。道德風險：說明保險或契約如何降低代理人付出努力或採取預防措施的誘因，提高期望成本。

**Step 3 — 評估矯正機制**
訊號傳遞（有資訊的一方行動）：找出訊號，驗證單交叉條件（高類型覺得訊號的成本較低），並檢查是否存在分離均衡。篩選（沒資訊的一方設計菜單）：設計能誘導自我選擇的契約，通常高類型拿到有效率的契約，低類型則面對數量扭曲。其他機制：保固、聲譽、認證、強制揭露、監管。

**Step 4 — 評估效率與政策**
把結果和完全資訊的基準比較。計算福利損失的來源：(a) 錯失的交易（好類型被定價擠出市場）；(b) 訊號的浪費（花在沒有直接價值的證書上的資源）；(c) 篩選的扭曲（對低類型的無效率契約）。建議市場機制是否足夠，還是需要政府介入。

## Output Format

```markdown
## Information Economics Analysis: [Market / Context]

### Information Structure
- **Asymmetry type**: Adverse selection / Moral hazard / Both
- **Informed party**: [who knows what]
- **Uninformed party**: [who lacks what information]
- **Hidden variable**: [quality / risk type / effort level]

### Market Failure Diagnosis
- **Unraveling risk**: [high / medium / low]
- **Pooling outcome**: [what happens if all types are treated identically]
- **Separating outcome**: [what happens if types are distinguished]

### Corrective Mechanisms
| Mechanism      | Who Initiates | How It Works            | Effective? |
|---------------|---------------|-------------------------|------------|
| Signaling      | Informed      | [e.g., education]       |            |
| Screening      | Uninformed    | [e.g., deductible menu] |            |
| Warranty       | Informed      | [e.g., money-back]      |            |
| Regulation     | Government    | [e.g., mandatory disclosure] |       |

### Efficiency Assessment
- **Full-information benchmark**: [first-best outcome]
- **Welfare loss sources**: [missing trades / signaling waste / screening distortion]
- **Net welfare**: [second-best outcome vs. unregulated market]

### Recommendation
[Which mechanisms to deploy; whether policy intervention is warranted]
```

## Gotchas

- 訊號傳遞在社會上可能是浪費的，如果教育只是訊號（不是人力資本），花在上面的資源就是純粹的無謂損失
- 當高類型比例很大時，Rothschild-Stiglitz 模型在純策略下可能沒有 Nash 均衡，Wilson 預期均衡或 Riley 反應均衡是替代方案
- 道德風險和逆選擇會互相影響：附自負額的保險（針對逆選擇的篩選）也能減輕道德風險，但這兩個問題可能需要互相衝突的契約設計
- 強制揭露可能適得其反，如果它導致原本穩定的混同均衡解體
- 在重複互動中，聲譽可以取代正式的訊號，但聲譽很脆弱，也會受到終局效應影響
- 數位平台和大數據在某些市場減少了資訊不對稱（信用評分、評論），卻在其他市場創造了新的不對稱（演算法定價、資料隱私）

## References

- Akerlof, G. (1970). "The Market for Lemons: Quality Uncertainty and the Market Mechanism." *Quarterly Journal of Economics*.
- Spence, M. (1973). "Job Market Signaling." *Quarterly Journal of Economics*.
- Rothschild, M. & Stiglitz, J. (1976). "Equilibrium in Competitive Insurance Markets." *Quarterly Journal of Economics*.
- Riley, J. (2001). "Silver Signals: Twenty-Five Years of Screening and Signaling." *Journal of Economic Literature*.
