---
name: "econ-supply-demand"
description: "運用供需分析解釋價格如何決定、市場如何均衡，以及政策干預的效果。當使用者需要分析市場裡的價格是怎麼訂出來的、預測稅/補貼/價格管制的效果，或理解供給曲線與需求曲線的移動時使用。就算使用者只說「為什麼價格漲了」、「政府設價格上限會怎樣」或「關稅對市場有什麼影響」也要用。"
metadata:
  category: "WP-17 經濟學院"
  tags: ["economics", "supply-demand", "microeconomics"]
---

# 供需分析

## 概述

供需是市場價格決定的基礎模型。它解釋價格如何從買方（需求）和賣方（供給）的互動中產生，以及外部衝擊或政策干預如何移動均衡。

## 框架

```
IRON LAW: Shift vs Movement Along the Curve

A change in PRICE causes movement ALONG the curve (quantity changes).
A change in OTHER FACTORS (income, costs, preferences, technology) causes
the entire curve to SHIFT.

"Demand increased" means the demand CURVE shifted right (more quantity
at every price), NOT that quantity demanded increased due to a price drop.
Confusing these is the #1 error in supply-demand analysis.
```

```
IRON LAW: Ceteris Paribus — Change One Thing at a Time

When analyzing a shift, hold everything else constant. If both supply
and demand shift simultaneously, the effect on price or quantity (or both)
becomes ambiguous. Analyze each shift separately first, then combine.
```

### 需求曲線的移動因素（非價格因素）
- 消費者所得（正常財：所得上升 → 需求上升；劣等財：相反）
- 相關商品的價格（替代品、互補品）
- 消費者的偏好與品味
- 人口 / 買家人數
- 對未來價格的預期

### 供給曲線的移動因素（非價格因素）
- 投入成本（原物料、勞力、能源）
- 技術進步
- 賣家人數
- 政府政策（稅、補貼、管制）
- 對未來價格的預期

### 分析步驟

1. **定義市場**：什麼商品？地理/時間範圍是什麼？
2. **找出衝擊**：什麼變了？是需求面還是供給面？
3. **判斷移動方向**：曲線是左移（減少）還是右移（增加）？
4. **找出新均衡**：新的曲線在哪裡相交？
5. **說明結果**：價格和數量會怎麼變？

### 政策分析

| 干預 | 效果 |
|-------------|--------|
| 價格上限（低於均衡價） | 短缺：需求量 > 供給量、黑市、品質下降 |
| 價格下限（高於均衡價） | 過剩：供給量 > 需求量、浪費、無效率 |
| 從量稅 | 供給曲線左移稅額的幅度，價格上升（依彈性由買賣雙方分攤） |
| 補貼 | 供給曲線右移補貼額的幅度，價格下降 |
| 關稅 | 進口供給左移，國內價格上升 |

## 輸出格式

```markdown
# Supply-Demand Analysis: {Market}

## Market Definition
- Good: ...
- Scope: ...

## Shock Identification
- Event: {what changed}
- Affected curve: Demand / Supply
- Direction: Shift left / right
- Mechanism: {why this shifts the curve}

## Equilibrium Impact
| | Before | After | Change |
|---|--------|-------|--------|
| Price | $X | $X | ↑/↓ |
| Quantity | X units | X units | ↑/↓ |

## Analysis
{Detailed explanation with diagram description}
```

## 範例

### 正確的做法
**情境：** 新的電動車補貼對台灣電動車市場的影響

- **衝擊**：政府每買一輛電動車補貼 NT$15 萬
- **受影響的曲線**：需求向右移（實質上降低了買方的價格 → 在每個市場價格下需求量都增加）
- **結果**：價格小幅上升（賣方拿走一部分補貼），數量大幅增加
- 註：供給曲線沒有移動，補貼是給買方，不是給製造商 ✓

### 錯誤的做法
- 「電動車價格下降所以需求增加了」→ 這是沿著需求曲線的移動，不是曲線的移動。需求（曲線）沒有增加，是需求量增加。違反 Iron Law。
- 同時分析電動車補貼 + 晶片短缺，沒有分開處理 → 結果模糊。必須先分別分析每個移動。違反 ceteris paribus。

## 常見陷阱

- **彈性決定誰承擔負擔**：對稅/補貼來說，「彈性較小」的那一方承擔較多的負擔。如果需求缺乏彈性（必需品），消費者會承擔大部分的加稅。
- **短期 vs 長期**：供給在長期比較有彈性（廠商可以進入/退出、建立產能）。短期分析可能高估價格變動。
- **不是所有市場都適用**：供需假設的是競爭市場。獨占、寡占和有外部性的市場，需要不同的模型。
- **「需求」不是「想要」**：需求需要「有意願」而且「有能力」付款。十億人想要 iPhone，如果他們買不起，就不是需求。

## 參考資料

- 彈性的計算，見 `references/elasticity.md`
- 福利分析（消費者/生產者剩餘），見 `references/welfare-analysis.md`
