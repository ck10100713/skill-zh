---
name: "grad-platform-economics"
description: "用平台經濟學分析網絡效應、解決雞生蛋蛋生雞問題，並設計多邊平台的定價策略。當使用者需要評估平台商業模式、診斷平台為什麼規模化失敗，或為雙邊市場的冷啟動選擇補貼策略時，就用這個 skill。"
metadata:
  category: "WP-24 創新與國際化"
  tags: ["platform-economics", "network-effects", "two-sided-markets", "chicken-and-egg", "pricing-strategy", "multi-sided-platform"]
---

# Platform Economics：網絡效應與多邊市場

## Overview

平台經濟學研究透過促成兩個以上不同使用者群體之間的互動來創造價值的事業。和線性創造價值的管線型事業不同，平台有網絡效應，每多一個使用者，就會提高其他人的價值。核心挑戰是雞生蛋蛋生雞問題：任何一邊都不會在另一邊還沒來之前加入。

## When to Use

**觸發條件：**
- 使用者在設計或評估多邊平台的商業模式
- 使用者問兩邊都還沒有使用者的市集，要怎麼冷啟動
- 使用者需要決定定價：補貼誰、向誰收費
- 使用者提到「network effects」、「marketplace」、「platform strategy」或「chicken-and-egg」

**When NOT to use：**
- 線性 / 管線型的商業模式 -> 用 Porter 的價值鏈
- 平台之間的競爭動態 -> 用 grad-coopetition
- 平台內部的創新策略 -> 用 grad-ambidexterity

## Assumptions

```
IRON LAW: Value Scales with Interactions, NOT Users

A platform with 1 million users but zero transactions has ZERO value.
The unit of platform value is the INTERACTION (transaction, match,
message), not the user count. Vanity metrics (registered users, downloads)
mask platform failure.

Always measure: interactions per user per time period.
```

- 至少有兩個不同的使用者群體，需求互相依賴
- 平台不擁有生產工具，它負責協調
- 贏者通吃的動態，會隨網絡效應的強度而增強

## Methodology

### Step 1: Identify Platform Type and Sides

為平台及其各邊分類：
- **交易型平台**：促成交換（Uber、Airbnb、eBay）
- **創新型平台**：為互補品提供基礎（iOS、AWS）
- **混合型**：同時有交易和創新（Amazon、微信）

列出每一邊，以及他們想從平台得到什麼價值。

### Step 2: Map Network Effects

針對每一對邊，找出：
- **同邊（直接）效應**：A 邊的使用者增加，會不會吸引更多 A 邊的使用者？（正向：社群網路。負向：市集上賣家之間的競爭。）
- **跨邊（間接）效應**：A 邊的使用者增加，會不會吸引更多 B 邊的使用者？（乘客吸引司機，反之亦然。）

### Step 3: Solve the Chicken-and-Egg Problem

選擇冷啟動策略：
| Strategy | Mechanism | Example |
|----------|-----------|---------|
| 補貼一邊 | 讓一邊免費或便宜，以吸引另一邊 | Adobe PDF Reader 免費，Acrobat 付費 |
| 單人模式 | 在網絡效應啟動前，先提供獨立的價值 | OpenTable 給餐廳的訂位系統 |
| 播種 | 一開始自己創造供給 | Reddit 創辦人自己發早期內容 |
| 指標性使用者 | 簽下知名使用者來吸引大眾 | 遊戲主機簽下獨家遊戲 |
| 搭便車 | 借用既有的網絡 | eBay 上的 PayPal |

### Step 4: Design Pricing Architecture

決定「收錢的一邊」和「被補貼的一邊」：
- **價格彈性較低**的一邊，付比較多
- 產生**較強跨邊效應**的一邊，被補貼
- 早期階段絕不要對兩邊平均收費

## Output Format

```markdown
# Platform Analysis: {Platform Name}

## Platform Architecture
- Type: Transaction / Innovation / Hybrid
- Sides: {list each side and their value proposition}

## Network Effects Map
| Effect | Type | Direction | Strength |
|--------|------|-----------|----------|
| {Side A to Side A} | Same-side | Positive/Negative | High/Med/Low |
| {Side A to Side B} | Cross-side | Positive/Negative | High/Med/Low |

## Chicken-and-Egg Strategy
- Recommended approach: {strategy}
- Subsidy side: {which side and why}
- Money side: {which side and why}

## Key Metrics
- Core interaction: {what counts as a successful interaction}
- Interaction rate: {interactions per user per period}
- Liquidity threshold: {minimum activity for self-sustaining growth}
```

## Gotchas

- **網絡效應不是病毒效應**：病毒性是關於獲客速度；網絡效應是關於價值的增加。產品可以有病毒性卻沒有網絡效應（Hotmail），也可以有網絡效應卻沒有病毒性（Bloomberg Terminal）。
- **負向的同邊效應很重要**：市集上賣家變多，會傷害每個賣家。如果負向同邊效應的增長超過跨邊的好處，平台就會崩潰。
- **多重歸屬會破壞鎖定**：如果使用者能輕易同時使用競爭平台（司機同時在 Uber 和 Lyft），網絡效應就會減弱。要評估多重歸屬的成本。
- **贏者通吃不是必然的**：有強烈在地效應、多重歸屬成本低，或有利基差異化的市場，能支撐多個平台。
- **去中介化風險**：參與者一旦被配對上，可能繞過平台。要持續創造價值，或強制轉換成本。

## References

- 想了解網絡效應的數學模型（Metcalfe、Reed），見 `references/network-effects-math.md`
- 想了解平台定價的形式化（Rochet-Tirole），見 `references/platform-pricing-models.md`
