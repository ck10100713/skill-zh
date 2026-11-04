---
name: "grad-public-choice"
description: "用公共選擇理論，把政治決策當作理性自利的行為來分析。當使用者需要評估政府政策的失靈、尋租成本、投票結果或官僚誘因，尤其是「政府仁慈」這個假設有疑問的時候，就用這個 skill。"
metadata:
  category: "WP-27 賽局與制度經濟"
  tags: ["public-choice", "Buchanan", "Tullock", "rent-seeking", "median-voter", "logrolling", "government-failure", "constitutional-economics"]
---

# Public Choice Theory：理性政治、尋租與政府失靈

## Overview

公共選擇把經濟學的推理，包括理性自利、策略行為和均衡分析，套用到政治決策上。政治人物、官僚、選民和說客都被建模成效用最大化者，不是仁慈的社會計畫者。這個理論解釋了尋租、互投贊成票（logrolling）、肉桶支出、管制俘虜，以及公共利益和政治結果之間系統性的偏離。Buchanan 和 Tullock 的奠基性著作，把憲法規則視為終極的機制設計問題。

## When to Use

- 分析為什麼某項政府政策產生的結果，和宣稱的目標有落差
- 估計尋租和遊說活動造成的無謂損失
- 用中位數選民或空間模型預測選舉結果或立法協商
- 設計憲法規則或制度改革，以約束政治上的機會主義

## When NOT to Use

- 分析本來就假設有仁慈的社會計畫者（規範性福利經濟學）
- 政治行為者確實受到強大的規範、法院或透明度所約束（代理問題極小）
- 問題是關於市場失靈，不是政府失靈

## Assumptions

```
IRON LAW: Public officials are NOT benevolent social planners — they
respond to incentives just like market participants. Policy outcomes
reflect the preferences of those with political power, not the
preferences of society at large.
```

- 政治人物最大化選票（或連任的機率）
- 官僚最大化預算規模或裁量權（Niskanen 模型）
- 選民是理性無知的，取得資訊的成本超過一張選票的預期效益
- 當集中的利益超過組織成本時，利益團體就會形成（Olson 的集體行動邏輯）
- 憲法規則是塑造所有後續政治賽局的元賽局

## Methodology

**Step 1 — 找出政治市場**
描繪行為者：選民、政治人物、官僚、利益團體。指明每個行為者最大化什麼，以及他們面對的限制（選舉週期、預算規則、資訊成本）。

**Step 2 — 套用相關模型**
從中選擇：(a) 中位數選民定理，在單一維度、單峰偏好的空間中，多數決下會是中位數選民偏好的政策勝出；(b) 尋租模型，行為者花費真實資源去爭取移轉，耗散掉的資源最高可達租金的全部價值；(c) 互投贊成票 / 選票交易，少數派跨議題交易選票，通過在各議題上單獨都得不到多數支持的立法；(d) 官僚模型，追求預算最大化的機關，產出超過有效率的水準。

**Step 3 — 估計政府失靈的成本**
量化：(a) Tullock 矩形，花在尋租上的資源；(b) 政策反映政治而非經濟效率所造成的配置扭曲；(c) 缺乏競爭壓力的政府機關內部的 X 無效率。拿這些和政策想要矯正的市場失靈比較。

**Step 4 — 提出制度上的補救**
建議憲法或制度設計的改變：絕對多數要求、落日條款、獨立機構、財政規則、透明度規定，或地方分權（Tiebout 競爭）。評估彈性與約束之間的取捨。

## Output Format

```markdown
## Public Choice Analysis: [Policy / Institution]

### Political Actors
| Actor           | Objective             | Key Constraint         |
|----------------|-----------------------|------------------------|
| Voters          |                       |                        |
| Politicians     |                       |                        |
| Bureaucrats     |                       |                        |
| Interest groups |                       |                        |

### Model Applied
- **Framework**: Median voter / Rent-seeking / Logrolling / Bureaucracy
- **Prediction**: [what the model predicts will happen]
- **Observed outcome**: [what actually happens — consistent?]

### Government Failure Costs
| Cost Category          | Estimate / Description |
|-----------------------|----------------------|
| Rent-seeking expenditure |                    |
| Allocative distortion    |                    |
| X-inefficiency           |                    |

### Market Failure vs. Government Failure
- **Market failure being addressed**: [externality / public good / monopoly]
- **Government failure introduced**: [rent-seeking / capture / inefficiency]
- **Net assessment**: [intervention improves welfare? or worsens it?]

### Institutional Recommendations
[Specific reforms with rationale]
```

## Gotchas

- 理性無知不代表選民笨，而是代表在一張選票的影響力之下，資訊的邊際成本超過邊際效益
- 中位數選民定理需要單峰偏好和單一政策維度，多維度時可能出現循環（Arrow 不可能定理）
- 當競爭者喜歡冒險，或對競爭的資訊有誤時，尋租的耗散可能超過租金的 100%
- 公共選擇並不主張所有政府行動都不好，而是主張必須分析誘因結構，不能假設政府仁慈
- Buchanan 區分了「沒有浪漫色彩的政治」（實證分析）和憲政政治經濟學（規則的規範性設計）
- 管制俘虜（Stigler）是尋租的一種特定形式，被管制的產業控制了管制者，光有獨立性是不夠的

## References

- Buchanan, J. & Tullock, G. (1962). *The Calculus of Consent*. University of Michigan Press.
- Tullock, G. (1967). "The Welfare Costs of Tariffs, Monopolies, and Theft." *Western Economic Journal*.
- Olson, M. (1965). *The Logic of Collective Action*. Harvard University Press.
- Mueller, D. (2003). *Public Choice III*. Cambridge University Press.
