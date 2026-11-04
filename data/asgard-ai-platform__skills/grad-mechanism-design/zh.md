---
name: "grad-mechanism-design"
description: "用機制設計（反向賽局理論）為分配問題設計誘因相容的規則。當使用者需要設計拍賣、投票系統或配對市場，或要評估某個提議的機制是否滿足誘因相容與個人理性限制時，就用這個 skill。"
metadata:
  category: "WP-27 賽局與制度經濟"
  tags: ["mechanism-design", "incentive-compatibility", "revelation-principle", "Myerson-Satterthwaite", "auction-design", "matching-markets"]
---

# Mechanism Design：反向賽局理論與誘因相容

## Overview

機制設計是賽局理論的工程面：不是分析給定的賽局，而是設計規則，讓自利的行為者產生期望的結果。核心工具是顯示原理，它指出任何可實施的結果，都能透過一個讓說真話成為最佳選擇的直接機制來達成。這個領域支撐了拍賣設計、投票系統、配對市場和監管框架。

## When to Use

- 設計參與者擁有私有資訊的分配規則（拍賣、配對、資源分享）
- 評估某個提議的制度或平台，是否誘使人們誠實行事
- 評估效率、預算平衡和參與限制之間的取捨

## When NOT to Use

- 行為者完全合作，沒有私有資訊（不存在誘因問題）
- 環境太複雜，無法為行為者的類型建模（改用行為實驗）
- 你要的是快速的捷思法，不是正式的保證

## Assumptions

```
IRON LAW: A mechanism is incentive-compatible ONLY if truth-telling is a
dominant strategy — no mechanism can simultaneously maximize efficiency,
budget balance, and individual rationality (Myerson-Satterthwaite theorem).
```

- 行為者是理性的，並最大化期望效用
- 每個行為者都有私有資訊（類型），來自已知的先驗分配
- 設計者在行為者行動之前，就承諾機制規則
- 移轉（支付）是可行的，並適用準線性效用

## Methodology

**Step 1 — 定義設計問題**
指明行為者的集合、他們的類型空間、結果空間，以及你想實施的社會選擇函數。找出目標：效率、收益、公平，或加權組合。

**Step 2 — 套用顯示原理**
把注意力限縮在直接顯示機制。對每個行為者，機制會請他報告類型，並把報告的組合對應到結果和移轉。檢查誠實報告是否構成 Bayesian Nash 均衡（BNE-IC）或占優策略均衡（DSIC）。

**Step 3 — 驗證限制式**
檢查三個核心限制：(1) 誘因相容，沒有行為者能靠謊報獲益；(2) 個人理性，每個行為者參與的處境至少不比不參與差；(3) 預算平衡，設計者不會虧損。套用 Myerson-Satterthwaite 判斷哪些限制可以並存。

**Step 4 — 刻畫與最佳化**
用包絡定理，從分配規則推導支付規則。在有效的限制式下，最佳化目標。報告哪些取捨是無法避免的。

## Output Format

```markdown
## Mechanism Design Analysis: [Context]

### Design Problem
- **Agents**: [who participates]
- **Type space**: [private information each agent holds]
- **Outcome space**: [possible allocations]
- **Objective**: [efficiency / revenue / fairness]

### Proposed Mechanism
- **Allocation rule**: [how outcomes map to reports]
- **Payment rule**: [transfers as function of reports]

### Constraint Verification
| Constraint                | Satisfied? | Notes |
|--------------------------|------------|-------|
| Incentive Compatibility  | Yes / No   |       |
| Individual Rationality   | Yes / No   |       |
| Budget Balance           | Yes / No   |       |

### Impossibility Trade-offs
[Which constraints conflict per Myerson-Satterthwaite; what the designer must sacrifice]

### Recommendation
[Chosen mechanism and rationale]
```

## Gotchas

- 顯示原理保證直接機制存在，但對實務上的簡潔性什麼都沒說，現實中的機制常因為行為上的理由用間接形式
- Myerson-Satterthwaite 不可能定理適用於私有價值的雙邊交易，多邊情境可能逃過它
- DSIC 比 BNE-IC 更強，很多實務上的機制（例如 VCG）是 DSIC，但可能違反預算平衡
- 行為者類型之間的相關性可以被利用（Cremer-McLean）來榨取全部剩餘，但需要很強的分配知識
- 在未被占優的策略下實施、完全實施和部分實施是不同的解概念，要說明你指的是哪一種
- 有行為特徵的行為者（有限理性、惡意、公平考量）會破壞理論上誘因相容的機制

## References

- Myerson, R. (1981). "Optimal Auction Design." *Mathematics of Operations Research*.
- Myerson, R. & Satterthwaite, M. (1983). "Efficient Mechanisms for Bilateral Trading." *Journal of Economic Theory*.
- Mas-Colell, A., Whinston, M. & Green, J. (1995). *Microeconomic Theory*, Ch. 23.
- Borgers, T. (2015). *An Introduction to the Theory of Mechanism Design*.
