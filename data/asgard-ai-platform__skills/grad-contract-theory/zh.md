---
name: "grad-contract-theory"
description: "用契約理論設計在道德風險與逆選擇下仍能誘因相容的協議。當使用者需要設計委託人與代理人的契約、評估薪酬方案，或分析雙方無法事前寫明所有情況的不完全契約問題時，就用這個 skill。"
metadata:
  category: "WP-27 賽局與制度經濟"
  tags: ["contract-theory", "moral-hazard", "adverse-selection", "principal-agent", "incentive-design", "Hart", "Holmstrom", "incomplete-contracts"]
---

# Contract Theory：道德風險、逆選擇與誘因設計

## Overview

契約理論研究的是，在資訊不對稱的情況下，經濟行為者怎麼建構契約安排。兩個經典問題是道德風險（隱藏行動，代理人的努力程度看不到）和逆選擇（隱藏類型，代理人的特質只有他自己知道）。最佳契約要在委託人想分攤風險的需求，和激勵努力或誘出真實資訊的需求之間取得平衡。Hart 和 Holmstrom 在不完全契約與誘因設計上的貢獻，是現代契約理論的基礎。

## When to Use

- 設計員工或外包人員的薪酬、獎金或佣金結構
- 評估保險契約的道德風險（自負額、部分負擔）或逆選擇（篩選）
- 設計品質無法觀察的合夥、加盟或採購契約
- 分析無法寫明所有狀態的不完全契約

## When NOT to Use

- 雙方資訊對稱，而且已經建立信任（沒有誘因問題）
- 這是一次性的匿名交易，沒有契約執行機制
- 行為因素（互惠、內在動機）比金錢誘因影響更大

## Assumptions

```
IRON LAW: The optimal contract balances risk-sharing against incentive
provision — full insurance destroys incentives, full incentives impose
unbearable risk. There is no contract that achieves first-best when
information is asymmetric.
```

- 委託人風險中立，代理人風險趨避（標準設定）
- 代理人的行動（努力）或類型是私有資訊
- 產出是代理人努力的雜訊訊號：x = f(e) + epsilon
- 雙方都理性，而且能承諾遵守契約條款
- 法院可以驗證產出，但無法驗證努力（可契約性限制）

## Methodology

**Step 1 — 分類資訊問題**
判斷核心問題是道德風險（簽約後的隱藏行動）、逆選擇（簽約前的隱藏類型），還是兩者都有。找出誰是委託人、誰是代理人。

**Step 2 — 列出限制式**
寫下：(1) 誘因相容限制（IC），代理人偏好採取預期的行動或揭露真實類型；(2) 參與限制（PC/IR），代理人接受這份契約勝過外部選項；(3) 有限責任（LL，若適用），支付不能低於零。

**Step 3 — 求解最佳契約**
道德風險的情況：在 IC 和 PC 限制下，最大化委託人的期望利潤。最佳工資函數 w(x) 滿足 Holmstrom 資訊性原則，也就是只有當產出能反映努力的資訊時，薪酬才該取決於產出。逆選擇的情況：設計一組契約菜單，讓代理人自我選擇（篩選）。預期底層會有扭曲（低類型的配置沒有效率），頂層則有效率。

**Step 4 — 評估完整性與重新談判**
檢查契約是完整的（涵蓋所有可驗證的情況）還是不完全的（剩餘權利很重要）。如果不完全，就套用 Hart 的產權途徑：把剩餘控制權分配給投資最重要的那一方。同時考慮契約能不能抵抗重新談判。

## Output Format

```markdown
## Contract Design Analysis: [Context]

### Information Problem
- **Type**: Moral hazard / Adverse selection / Both
- **Principal**: [who]
- **Agent**: [who]
- **Hidden variable**: [effort level / agent type / quality]

### Constraints
| Constraint                  | Expression           | Binding? |
|----------------------------|----------------------|----------|
| Incentive Compatibility     |                      |          |
| Participation (IR)          |                      |          |
| Limited Liability           |                      |          |

### Optimal Contract Structure
- **Fixed component**: [base salary / premium]
- **Variable component**: [bonus / piece rate / deductible]
- **Informativeness**: [which signals are used and why]

### First-Best vs. Second-Best Gap
- **First-best outcome**: [what would happen with full information]
- **Second-best distortion**: [what is sacrificed]
- **Welfare loss**: [qualitative or quantitative]

### Recommendation
[Contract terms and implementation guidance]
```

## Gotchas

- 多工任務（Holmstrom-Milgrom）：激勵一個可衡量的任務，會排擠無法衡量任務上的努力，強激勵可能適得其反
- 棘輪效應：如果委託人根據過去表現調整期望，代理人會策略性地在早期表現不佳
- 生涯關注（Holmstrom 1999）可以取代明確的誘因，年輕代理人即使沒有獎金，也會為了累積聲譽而努力
- 有限責任限制會把權力轉移給代理人，委託人可能得留下租金（效率工資）
- 在重複關係中，關係型契約（自我執行，不靠法院強制）通常比正式契約更有效
- 外在誘因可能排擠內在動機（Benabou-Tirole），付錢給志工可能反而降低他們的努力

## References

- Holmstrom, B. (1979). "Moral Hazard and Observability." *Bell Journal of Economics*.
- Hart, O. & Moore, J. (1990). "Property Rights and the Nature of the Firm." *Journal of Political Economy*.
- Laffont, J.-J. & Martimort, D. (2002). *The Theory of Incentives: The Principal-Agent Model*.
- Bolton, P. & Dewatripont, M. (2005). *Contract Theory*. MIT Press.
