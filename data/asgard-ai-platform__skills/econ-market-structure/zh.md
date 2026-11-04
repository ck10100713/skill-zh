---
name: "econ-market-structure"
description: "分析完全競爭、壟斷性競爭、寡占、獨占這幾種市場結構，預測廠商行為與市場結果。當使用者需要判斷市場的競爭結構、預測定價行為、評估反托拉斯的影響，或想了解某個產業為什麼是這樣運作時使用。就算使用者只說「他們為什麼能收這麼貴」、「這個市場有競爭嗎」或「價格會降下來嗎」也要用。"
metadata:
  category: "WP-17 經濟學院"
  tags: ["economics", "market-structure", "industrial-organization"]
---

# 市場結構分析

## 概述

市場結構決定了廠商怎麼競爭、怎麼定價、怎麼賺錢。這四種結構（完全競爭、壟斷性競爭、寡占、獨占）隨著集中度升高、差異化增加，所預測的行為差異越來越大。

## 框架

```
IRON LAW: Structure Determines Behavior, Not Vice Versa

Classify the market structure FIRST based on structural characteristics
(number of firms, barriers, differentiation), THEN predict behavior.
"This company charges high prices" does not mean it's a monopoly —
high prices can occur in oligopolies and even monopolistic competition.
```

### 四種結構

| 特徵 | 完全競爭 | 壟斷性競爭 | 寡占 | 獨占 |
|---------|-------------------|------------------------|-----------|----------|
| 廠商數 | 非常多 | 很多 | 少數 | 一家 |
| 產品 | 同質 | 有差異 | 同質或有差異 | 獨特、沒有相近的替代品 |
| 進入障礙 | 無 | 低 | 高 | 非常高 |
| 定價能力 | 無（價格接受者） | 有一些（受替代品限制） | 顯著（互相依賴） | 完全（價格制定者） |
| 長期利潤 | 零（經濟利潤） | 零（經濟利潤） | 可能為正 | 為正 |
| 例子 | 農產品、外匯 | 餐廳、服飾 | 航空、電信、汽車 | 公用事業、專利 |

### 分類步驟

1. **算賣方數量**：這個市場有多少家重要的廠商？
2. **評估差異化**：產品是相同的還是有差異的？
3. **評估進入障礙**：新廠商容易進來嗎？
4. **檢查互相依賴性**：廠商會對彼此的動作做出反應嗎？

### 各結構的行為預測

**完全競爭**：價格 = 邊際成本。廠商是價格接受者。不需要廣告。長期經濟利潤 = 0。

**壟斷性競爭**：靠差異化，短期可能有利潤。長期：新進者會把利潤侵蝕到零。廠商在品牌、品質、地點上競爭。

**寡占**：廠商互相依賴，每家都盯著對手的動作。適用賽局理論。可能共謀（默契式或明示）。有拗折需求曲線或 Cournot/Bertrand 模型。

**獨占**：價格 > 邊際成本。存在無謂損失。可能受到管制（公用事業）或是暫時的（專利）。當平均成本隨規模遞減時，會形成自然獨占。

## 輸出格式

```markdown
# Market Structure Analysis: {Industry}

## Classification
- Structure: {type}
- Evidence:
  - Number of firms: ...
  - Product differentiation: ...
  - Entry barriers: ...
  - Interdependence: ...

## Predicted Behavior
- Pricing: {price-taking / markup / strategic}
- Long-run profit: {zero / positive}
- Competition type: {price / quality / advertising / innovation}

## Policy Implications
{Antitrust concerns, regulation needs, consumer impact}
```

## 範例

### 正確的做法
**情境：** 台灣的電信市場
- **廠商**：3 家主要業者（中華電信、台灣大、遠傳）+ 2 家小的 → **少數**
- **差異化**：中等（速度/涵蓋範圍有差別，但大致可互相替代）
- **進入障礙**：非常高（頻譜執照、基礎建設成本約 NT$1,000 億以上）
- **互相依賴**：高（一家調價，其他家立刻有反應）
- **分類：寡占** ✓
- **預測行為**：默契式的價格協調，在套餐組合和服務而非價格上競爭，穩定的高毛利

### 錯誤的做法
- 「iPhone 沒有競爭對手，所以 Apple 是獨占」→ 智慧型手機有很多競爭對手（Samsung、Google、小米）。Apple 靠差異化擁有市場力量，但智慧型手機市場是**寡占**，不是獨占。結構看的是市場，不是單一廠商產品的獨特性。

## 常見陷阱

- **市場定義會改變答案**：「智慧型手機」是寡占，「iOS 裝置」是獨占。市場界線決定了結構的分類。
- **完全競爭只存在於理論中**：幾乎沒有真實的市場是完全競爭的。把它當基準，不要拿來分類真實的產業。
- **寡占最複雜**：賽局理論、共謀和策略行為，讓寡占分析比其他結構更難。假設要講得清楚。
- **可競爭市場**：就算是獨占，只要進入障礙低，也可能表現得像競爭市場（新進者的威脅會約束定價）。障礙跟目前的廠商數量一樣重要。
- **動態市場**：科技市場現在可能看起來像獨占（Google 搜尋），卻面臨顛覆（AI 聊天）帶來的競爭壓力。要看發展軌跡，不只是當下的快照。

## 參考資料

- 寡占的賽局模型（Cournot、Bertrand、Stackelberg），見 `references/oligopoly-models.md`
