---
name: "grad-diamond"
description: "用 Porter 鑽石模型分析某個特定產業的國家競爭優勢。當使用者需要評估為什麼某些國家主導特定產業、評估一個國家對產業投資的吸引力，或用四大決定因素加上政府與機會來診斷國家競爭力的缺口時，就用這個 skill。"
metadata:
  category: "WP-24 創新與國際化"
  tags: ["porter-diamond", "national-competitive-advantage", "factor-conditions", "demand-conditions", "related-industries", "firm-strategy"]
---

# Diamond Model (Porter, 1990)：國家競爭優勢

## Overview

Porter 的鑽石模型解釋為什麼某些國家會成為具全球競爭力產業的大本營。四個互相連動的決定因素，分別是要素條件、需求條件、相關與支援產業，以及企業策略、結構與競爭，組成一個自我強化的系統。政府和機會是外部變數，會影響鑽石，但本身不是決定因素。最關鍵的是，國家優勢是針對特定產業的，不是整個經濟體都有。

## When to Use

**觸發條件：**
- 使用者問為什麼某個國家主導某個特定產業（例如瑞士手錶、韓國半導體）
- 使用者需要評估一個國家作為特定產業基地的條件
- 使用者在比較各國環境，要做投資或遷移決策
- 使用者提到「national competitiveness」、「diamond model」、「Porter's diamond」或「country advantage」

**When NOT to use：**
- 公司層級的競爭策略 -> 用 Porter 五力
- 公司層級的 FDI 決策 -> 用 grad-oli
- 漸進式的市場進入 -> 用 grad-uppsala

## Assumptions

```
IRON LAW: National Competitive Advantage Is INDUSTRY-SPECIFIC,
          NOT Country-Wide

A country does not have "competitive advantage" in general.
Germany has advantage in automotive and chemicals, NOT in software.
The US has advantage in tech and finance, NOT in consumer electronics
manufacturing.

NEVER assess a country's competitiveness without specifying the
industry. A "strong diamond" for one industry may be a weak diamond
for another in the SAME country.
```

- 競爭優勢是創造出來的，不是繼承來的，高級要素比基本要素更重要
- 國內競爭是國際競爭力的關鍵驅動力
- 四個決定因素會像系統一樣互相強化，只有單點優勢是不夠的
- 政府的角色是影響這些決定因素，不是挑贏家

## Methodology

### Step 1: Define the Industry Scope

把產業範圍界定得窄一點。「製造業」太廣，「精密儀器」或「半導體製造」才合適。鑽石分析一定要針對特定產業。

### Step 2: Analyze the Four Determinants

**1. Factor Conditions**：基本要素（天然資源、非技術勞工）是繼承來的，很容易被複製。高級要素（研究機構、技術工程師、創投生態系）是創造出來的，才能帶來可持續的優勢。

**2. Demand Conditions**：規模帶來規模經濟；需求的挑剔程度逼出創新；前瞻性需求（預告全球趨勢）讓國內企業搶得先機。

**3. Related and Supporting Industries**：具國際競爭力的供應商、地理群聚、知識外溢，以及快速的創新週期。

**4. Firm Strategy, Structure, and Rivalry**：國家文化塑造管理方式；激烈的國內競爭推動創新；資本市場結構影響時間視野。

### Step 3: Assess Government and Chance

- **Government**：強化決定因素的政策（教育投資、研發補貼、競爭政策、基礎建設）。政府該扮演催化劑，不是控制者。
- **Chance**：會重塑鑽石的外生事件（戰爭、石油衝擊、技術斷層、疫情）。

### Step 4: Evaluate Diamond System Strength

替每個決定因素評分，並評估整個系統有沒有互相強化：
- 強勁的需求條件有沒有拉動高級要素的創造？
- 國內競爭有沒有推動創新，再由挑剔的客戶來驗證？
- 相關產業有沒有形成群聚，吸引專業人才？

強的鑽石有互相強化的迴圈。弱的鑽石只有孤立的優勢，沒辦法複利累積。

## Output Format

```markdown
# Diamond Analysis: {Industry} in {Country}

## Determinant Ratings
| Determinant | Key Evidence | Rating |
|-------------|-------------|--------|
| Factor Conditions (basic/advanced) | {assessment} | Strong/Moderate/Weak |
| Demand Conditions | {assessment} | Strong/Moderate/Weak |
| Related & Supporting Industries | {assessment} | Strong/Moderate/Weak |
| Firm Strategy, Structure & Rivalry | {assessment} | Strong/Moderate/Weak |

## External Variables
- Government: {policies} | Chance: {events}

## System Assessment
- Reinforcing loops: {which determinants strengthen each other}
- Weak links: {gaps} | Overall: Strong/Moderate/Weak for {industry}
- Recommendations: {how to strengthen weak determinants}
```

## Gotchas

- **國家 GDP 不等於產業競爭力**：富裕的國家在特定產業上也可能是弱鑽石。一定要在產業層級分析。
- **基本要素是陷阱**：依賴廉價勞工或原物料會掉進「資源詛咒」。高級要素才能帶來可持續的優勢。
- **國內競爭違反直覺**：保護企業免於競爭會削弱鑽石。競爭很痛，但不可或缺。
- **鑽石是動態的**：曾經很強的鑽石（底特律的汽車）也會衰退。要用長期角度重新評估。
- **多國鑽石是存在的**：在小型開放經濟體，鑽石可能橫跨國界。不要硬套單一國家的框架。

## References

- 想了解 Porter 原始的鑽石要素分類，見 `references/diamond-factor-taxonomy.md`
- 想了解雙鑽石模型（Rugman）與其延伸，見 `references/double-diamond-extensions.md`
