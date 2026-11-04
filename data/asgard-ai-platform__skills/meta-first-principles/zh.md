---
name: "meta-first-principles"
description: "用第一原理思考，把問題拆解到最基本的事實，再從那裡往上推理。使用者卡在慣性思維、需要挑戰假設、想找突破性的解法，或要評估某件事是真的不可能還是只是被假設成不可能時使用，就算他們說的是「大家都這樣做」、「有沒有根本上更好的做法」、「為什麼一定要這麼貴」或「挑戰我的假設」也一樣。"
metadata:
  category: "WP-22 跨學科"
  tags: ["meta-thinking", "first-principles", "problem-solving"]
---

# 第一原理思考

## 框架

```
IRON LAW: Assumptions Are Not Facts

Most "constraints" are assumed, not physical. "We can't do X" usually means
"We haven't seen anyone do X" or "The current method doesn't allow X."
First principles thinking distinguishes between:
- Physical laws (actual constraints: gravity, thermodynamics)
- Conventions (assumed constraints: "this is how it's done")
```

### 方法

**1. 找出假設**：「大家都知道」或「大家都這樣做」的是什麼？

**2. 拆解到最基本的事實**：那些最基本、無法再拆的事實是什麼？
- 技巧：「五個為什麼」（連問 5 次為什麼）、成本拆解、物理層級的分析

**3. 從基本事實往上推理**：只憑這些基本事實，最好的解法是什麼？

### 範例：Elon Musk 談電池成本（2010 年代）

- **慣例**：「電池要 $600/kWh。電動車永遠會太貴。」
- **第一原理**：電池是什麼做的？鈷、鎳、鋰、碳、金屬、聚合物。這些原料值多少錢？以大宗商品價格算，約 $80/kWh。
- **往上推理**：如果我們自己買材料、自己做電池，成本有機會降到接近 $80/kWh。那 $520 的差距是製造上的低效率和供應鏈加價，不是物理限制。

### 用五個為什麼挖掘假設

1. 「為什麼我們的產品定價 $100？」：因為我們的 COGS 是 $60，而我們需要 40% 的毛利。
2. 「為什麼 COGS 是 $60？」：因為零件 Y 我們用的是供應商 X。
3. 「為什麼用供應商 X？」：因為我們一直都用他們。
4. 「為什麼沒有去看替代方案？」：因為採購團隊沒被要求去做。
5. 「為什麼沒有？」：**沒有真正的理由。就只是慣例。**

→ 找到的根本限制：COGS 裡包含了一段沒被檢視過的供應商關係，不是物理限制。

### 成本拆解範本

針對任何「成本太高」的問題：
1. 列出每一個成本組成
2. 對每一項，判斷：這項成本是來自物理（材料、能源），還是來自慣例（加價、低效率、舊流程）？
3. 質疑每一項來自慣例的成本

## 輸出格式

```markdown
# First Principles Analysis: {Problem}

## The Assumption
{What "everyone knows" or the conventional constraint}

## Decomposition
| Component | Cost/Fact | Physics or Convention? |
|-----------|----------|----------------------|
| {element} | {value} | Physics / Convention |

## Fundamental Truths
{What remains after stripping away assumptions}

## Reasoning Up
{Given only fundamental truths, what's the best approach?}

## Proposed Solution
{What changes if we ignore conventions and reason from fundamentals}
```

## 注意事項

- **不要什麼都重新發明輪子**：第一原理很貴（時間、精力）。留給傳統做法明顯行不通的高風險問題。例行的決定，用最佳實務和經驗法則就夠了。
- **物理限制是真的**：不要把第一原理思考和無視物理現實搞混。你沒辦法靠推理繞過熱力學。
- **「慣例」有價值**：慣例編碼了集體的經驗。把所有慣例都當成「假設」打發掉是傲慢，不是第一原理思考。重點是要檢視慣例，不是自動否定它們。
- **執行力很重要**：沒有執行能力的話，第一原理的洞見一文不值。SpaceX 不只是「想」便宜的火箭，他們還「蓋」出了垂直整合的製造體系。

## 參考資料

- 蘇格拉底式提問法（互補）請看 hum-socratic skill
