---
name: "grad-oli"
description: "用 Dunning 的 OLI 典範（折衷理論），根據所有權、區位與內部化優勢，評估對外直接投資決策。當使用者需要決定要不要到海外投資、在 FDI 模式（獨資子公司、合資、授權）之間選擇，或解釋為什麼公司用 FDI 國際化，而不是出口或授權時，就用這個 skill。"
metadata:
  category: "WP-24 創新與國際化"
  tags: ["OLI-paradigm", "dunning", "eclectic-theory", "FDI", "ownership-advantage", "location-advantage", "internalization-advantage"]
---

# OLI Paradigm (Dunning, 1977)：FDI 的折衷理論

## Overview

OLI 典範解釋為什麼公司會進行對外直接投資（FDI），而不是出口或授權。三個條件必須同時成立：公司擁有所有權優勢（專有資產）、海外區位比本國市場有優勢，而且內部化比市場型交易（授權 / 加盟）更好。OLI 優勢的組合，也決定了 FDI 的模式。

## When to Use

**觸發條件：**
- 使用者正在決定要不要透過 FDI 投資海外市場
- 使用者問為什麼公司該擁有海外營運，而不是出口或授權
- 使用者需要在獨資子公司、合資或授權之間選擇
- 使用者提到「FDI decision」、「OLI」、「internationalization mode」或「eclectic theory」

**When NOT to use：**
- 漸進式的國際化過程 -> 用 grad-uppsala
- 早期快速國際化 -> 用 grad-born-global
- 國家競爭優勢分析 -> 用 grad-diamond

## Assumptions

```
IRON LAW: ALL Three OLI Advantages Must Be Present to Justify FDI

- Ownership (O) alone -> License or export (no need to be there)
- Ownership + Location (O+L) -> Export (no need to internalize)
- Ownership + Internalization (O+I) -> Domestic production (no location pull)

Only when O + L + I are ALL present does FDI make economic sense.
If ANY one is missing, a different entry mode is optimal.
```

- 公司是理性的行為者，尋求最小化交易成本
- 市場不完美（資訊不對稱、機會主義）驅動內部化
- OLI 優勢是公司特定、產業特定、國家特定的

## Methodology

### Step 1: Assess Ownership Advantages (O)

找出海外競爭者沒有的公司特定優勢：資產型（Oa：專利、技術、品牌）和交易型（Ot：管理能力、規模經濟）。如果沒有明確的 O 優勢，就停下來，公司沒有做 FDI 的基礎。

### Step 2: Assess Location Advantages (L)

評估為什麼海外據點比從本國服務更好：
- **尋求市場**：市場規模大、需求成長、貿易障礙讓出口行不通
- **尋求資源**：低成本勞工、原物料、專門人才
- **尋求效率**：規模經濟、有利的稅制、供應鏈最佳化
- **尋求策略性資產**：接觸技術群聚、研發生態系、知識網絡

如果沒有明確的 L 優勢 -> 從本國出口就夠了。

### Step 3: Assess Internalization Advantages (I)

評估為什麼內部治理比授權或加盟更好：
- **高交易成本**：難以編碼和轉移的隱性知識
- **品質控制**：品牌聲譽需要嚴格的營運控制
- **機會主義風險**：被授權者可能變成競爭者，或降低品質
- **契約不完全**：無法寫出涵蓋所有突發狀況的契約

如果沒有明確的 I 優勢 -> 用授權或加盟，不要做 FDI。

### Step 4: Determine Entry Mode

| OLI Configuration | Recommended Mode |
|-------------------|-----------------|
| O + L + I（全都強） | 獨資子公司（綠地投資或收購） |
| O + L + I（I 中等） | 合資（分享控制權，降低風險） |
| O + L（沒有 I） | 授權 / 加盟 |
| 只有 O（沒有 L、沒有 I） | 從本國出口 |
| 沒有 O | 不要國際化 |

## Output Format

```markdown
# OLI Assessment: {Firm} -> {Target Country/Market}

## Ownership Advantages (O)
- Asset-based: {list with strength rating}
- Transaction-based: {list with strength rating}
- O assessment: Strong / Moderate / Weak

## Location Advantages (L)
- Motivation: Market / Resource / Efficiency / Strategic asset
- Key L factors: {list}
- L assessment: Strong / Moderate / Weak

## Internalization Advantages (I)
- Transaction cost drivers: {list}
- Opportunism risk: High / Medium / Low
- I assessment: Strong / Moderate / Weak

## OLI Configuration: {O+L+I / O+L / O only / etc.}

## Recommended Entry Mode: {mode with rationale}
```

## Gotchas

- **OLI 是靜態的快照**：優勢會演變。區位優勢（廉價勞工）可能消退。要定期重新評估。
- **O 優勢可能被模仿**：專利會到期，知識會擴散。可持續的 O 需要持續創新。
- **政府政策可以一夜之間改變 L**：稅務優惠、貿易協定或政治不穩，都可能翻轉 L 的評估。
- **合資是獨立的策略，不是折衷**：不要因為不確定就預設選合資。合資有它自己的風險。
- **OLI 不處理時機**：它回答「該不該做 FDI？」，不回答「什麼時候？」。要排順序的話，結合 Uppsala。

## References

- 想了解 OLI 的數學形式化與延伸，見 `references/oli-formalization.md`
- 想了解 OLI 在服務業 FDI 的應用，見 `references/oli-services.md`
