---
name: "grad-cultivation"
description: "用涵化理論（Gerbner）分析長期接觸媒體如何塑造世界觀。當使用者需要研究媒體對受眾信念的累積效應、評估主流化與共鳴現象，或評估媒體使用模式與社會現實認知的關聯時，就用這個 skill，即使他們說的是「看新聞會讓人更恐懼嗎」「媒體怎麼塑造世界觀」或「惡劣世界症候群」。"
metadata:
  category: "WP-33 傳播/教育/公共行政"
  tags: ["communication", "cultivation", "media-effects", "television"]
---

# Cultivation Theory

## Overview

涵化理論（Gerbner 等人）主張，長期、累積地接觸電視一致的訊息，會逐漸塑造觀眾對社會現實的認知。重度觀眾的世界觀會向「電視世界」靠攏，和真實世界的實際狀況無關。

## When to Use

**觸發條件：**
- 分析媒體對受眾現實認知的長期影響
- 研究大量使用媒體是否和扭曲的信念有關
- 評估不同受眾子群體的主流化或共鳴效應

**When NOT to use：**
- 研究短期說服（用 ELM 或框架理論）
- 分析哪些議題會被注意（用議題設定）
- 研究個人處理訊息的方式（用雙歷程理論）

## Assumptions

```
IRON LAW: Cultivation Is a LONG-TERM, Cumulative Effect

Single exposures do NOT cultivate. It is the PATTERN across thousands
of consistent messages over months and years that gradually shapes
worldviews. Key mechanisms:
1. MAINSTREAMING: Heavy viewing overrides demographic differences,
   creating a homogeneous worldview
2. RESONANCE: When TV messages match a viewer's lived experience,
   the cultivation effect is amplified (double dose)
```

## Methodology

### Step 1: Content Analysis
進行訊息系統分析，有系統地整理媒體內容中反覆出現的主題、描繪方式和人口特徵，找出「電視世界」。

### Step 2: Measure Exposure
依總媒體使用量把受訪者分類（重度與輕度觀眾）。依原始理論，用整體使用量，不要用特定類型。

### Step 3: Survey Beliefs
測量對社會現實的認知。把「電視答案」（反映媒體描繪）和「真實世界答案」（反映實際統計）拿來比較。

### Step 4: Calculate Cultivation Differential
比較重度與輕度觀眾的回答，並控制人口變項。能歸因於收看的差異，就是涵化差距。

## Output Format

```markdown
# Cultivation Analysis: {Topic/Context}

## Media World
- Content analyzed: {media type, sample, period}
- Key portrayal patterns: {recurring themes, over/under-representations}
- "Television answer": {what media suggests is true}

## Real World
- Actual statistics: {objective data on the topic}
- Gap: {difference between media portrayal and reality}

## Cultivation Differential
- Heavy viewers: {beliefs/perceptions}
- Light viewers: {beliefs/perceptions}
- Differential: {magnitude, controlling for demographics}

## Mainstreaming/Resonance
- Mainstreaming: {evidence of worldview convergence among heavy viewers}
- Resonance: {subgroups where lived experience amplifies effect}

## Limitations
{Confounders, third variables, directionality concerns}
```

## Gotchas

- **因果的挑戰**：涵化研究大多是相關性的。重度觀眾可能本來就有某些信念（選擇性接觸），很難證明是媒體造成了這些信念。
- **類型與總收看量**：原始涵化理論強調總收看量，不是特定類型。不過現代研究顯示類型有影響，暴力節目比喜劇更容易涵化出恐懼。
- **數位媒體帶來的複雜性**：涵化理論是為選擇有限的廣播電視發展出來的。在碎片化、隨選的媒體環境中，「訊息一致」的假設會變弱。
- **效果量很小**：在橫斷面調查中，涵化效果通常很小。Gerbner 認為，大量人口中小但一致的效果在社會上是重要的，批評者不同意。
- **文化差異**：涵化效果因媒體系統而異。在媒體所有權多元、有公共廣播的國家，效果可能和以美國為中心的研究發現不同。

## References

- 想了解 Cultural Indicators 研究計畫的方法，見 `references/cultural-indicators.md`
- 想了解數位媒體環境中的涵化，見 `references/digital-cultivation.md`
