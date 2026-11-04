---
name: "soc-policy-analysis"
description: "進行結構化的政策分析，包含問題定義、替代方案評估和以證據為基礎的建議。使用者需要評估政策選項、比較不同介入措施、評估法規影響，或提出公部門的建議時使用，就算他們說的是「我們該採用哪個政策」、「這個公共問題最好的做法是什麼」或「評估這些政策替代方案」也一樣。"
metadata:
  category: "WP-18 社會科學院"
  tags: ["social-science", "policy-analysis", "public-policy"]
---

# 政策分析

## 概述

政策分析是一套系統性的方法，用來評估處理公共問題的各種替代行動方案。它遵循結構化的流程：定義問題 → 找出替代方案 → 建立標準 → 評估 → 建議。適用於政府政策、企業政策和組織決策。

## 框架

```
IRON LAW: Problem Definition Determines Everything

How you define the problem determines which solutions are considered.
"Traffic congestion" suggests road-building. "Excessive car dependency"
suggests public transit. "Inefficient land use" suggests zoning reform.

The same observable situation can be framed as different problems,
leading to completely different policy responses. Make the framing
explicit and examine alternatives.
```

### 六個步驟

**1. 定義問題**
- 問題是什麼？（可觀察的證據，不只是症狀）
- 誰受到影響？嚴重程度如何？
- 原因是什麼？（根本原因，不是近因）
- 問題是怎麼被框架的？有其他的框架嗎？

**2. 找出替代方案**
- 現狀（什麼都不做，永遠要包含作為基準）
- 漸進式選項（修改既有政策）
- 轉型式選項（根本上全新的做法）
- 目標是 3-5 個真正的替代方案，不是稻草人

**3. 建立評估標準**
常見的標準：
| 標準 | 問題 |
|-----------|---------|
| **有效性（Effectiveness）** | 它能解決問題嗎？ |
| **效率（Efficiency）** | 相對於成本，效益如何？ |
| **公平性（Equity）** | 誰承擔成本？誰得到好處？ |
| **可行性（Feasibility）** | 政治、行政和技術上可行嗎？ |
| **永續性（Sustainability）** | 能長期維持嗎？ |

**4. 評估替代方案**
把每個替代方案對每個標準評分。盡可能使用證據（資料、案例研究、研究）。承認不確定性。

**5. 建議**
選出整體條件最好的替代方案。要明確說明取捨的理由，沒有任何替代方案會在每個標準上都拿最高分。

**6. 執行上的考量**
- 政治可行性：誰需要核准？誰可能反對？
- 行政能力：既有機構做得來嗎？
- 時程與分階段
- 監測與評估計畫

## 輸出格式

```markdown
# Policy Analysis: {Problem}

## Problem Definition
- Problem: {description}
- Affected population: {who}
- Root cause: {analysis}
- Alternative framings: {other ways to define this problem}

## Alternatives
1. Status quo
2. {Option A}
3. {Option B}
4. {Option C}

## Evaluation Matrix
| Criterion | Status Quo | Option A | Option B | Option C |
|-----------|-----------|----------|----------|----------|
| Effectiveness | L/M/H | L/M/H | L/M/H | L/M/H |
| Efficiency | L/M/H | ... | ... | ... |
| Equity | L/M/H | ... | ... | ... |
| Feasibility | L/M/H | ... | ... | ... |

## Recommendation
**{Selected option}** — {justification including trade-off acknowledgment}

## Implementation Plan
- Political path: {approval process}
- Timeline: {phases}
- Monitoring: {how to measure success}
```

## 範例

### 正確的應用
**情境：** 降低台北外送員傷亡的政策分析
- **問題**：外送員交通事故傷亡增加 45%（2023-2024）
- **替代方案**：(1) 現狀、(2) 強制保險 + 訓練、(3) 尖峰時段對外送 app 設定速限、(4) 平台對外送員傷害負責
- **評估**：方案 2 在可行性（漸進式）和有效性（直接處理風險）上得分最高；方案 4 最有效，但在政治上困難（平台會遊說）
- **建議**：方案 2 作為立即行動，方案 4 作為中期的立法目標 ✓

### 錯誤的應用
- 「問題是外送員騎太快」→ 這是症狀，不是根本原因。他們「為什麼」騎得快？因為平台演算法獎勵速度、按單計酬鼓勵趕時間，而且不安全駕駛沒有任何懲罰。不同的根本原因會導向不同的解法。違反鐵律：問題定義決定一切。

## 注意事項

- **永遠要包含現狀**：「什麼都不做」是個有效的選項，也是比較的基準。如果替代方案更糟，有時它就是最好的選項。
- **避免稻草人替代方案**：為了讓你偏好的選項看起來好，而放進明顯很爛的選項，在智識上是不誠實的。所有替代方案都應該是真正的選項。
- **公平性常常被拿來換效率**：最有效率的政策，往往有不平等的分配影響。要把這個取捨講明白。
- **執行會殺死好政策**：再精彩的政策，執行不了就一文不值。可行性不是次要的標準，而是先決條件。
- **證據層級**：RCT > 準實驗 > 案例研究 > 專家意見 > 軼事。要使用手上最強的證據，並明確說明證據的品質。

## 參考資料

- 成本效益分析方法論請看 `references/cost-benefit.md`
- 以證據為基礎的政策框架請看 `references/evidence-hierarchy.md`
