---
name: "meta-systems-thinking"
description: "用系統思考（因果迴路圖、存量流量模型、系統基模、槓桿點分析）處理組織、經濟或社會問題，適用於回饋迴路、時間延遲或湧現行為在多個互動主體之間造成反覆失敗的情況。使用者描述的是一個多方參與、線性解法行不通的情境時使用：政策介入反而適得其反、組織層級的修正弄壞其他團隊、市場症狀解決後又回來，或有時間落差的二階後果，就算他們說的是「為什麼修了 X 反而讓 Y 更糟」或「找出這個系統的槓桿點」也一樣。不要用在單一原因的軟體 bug、不穩定的測試或 regression，那些是除錯問題，不是系統思考的問題，就算說成「這個問題一直回來」也一樣。"
metadata:
  category: "WP-22 跨學科"
  tags: ["meta-thinking", "systems-thinking", "complexity"]
---

# 系統思考

## 框架

```
IRON LAW: First-Order Fixes in Complex Systems Produce Second-Order
Backlash Within 2 Cycles — Map the Feedback Loop BEFORE Intervening

Agents default to "fix the symptom directly" (e.g., high turnover → raise
salaries). In systems with feedback loops, the direct fix triggers a
compensating response that makes the original problem worse OR creates
a new one (raise salaries → budget squeeze → cut training → worse
onboarding → higher turnover). Before recommending any intervention,
draw the causal loop diagram and identify at least one reinforcing and
one balancing loop. If you can't find any, the problem may not be a
systems problem — don't force the framework.
```

### 分析步驟

假設已經知道的關鍵概念：回饋迴路（增強／平衡）、湧現、延遲、槓桿點、存量與流量。系統基模（Fixes That Fail、Shifting the Burden、Limits to Growth 等）請看
[`references/system-archetypes.md`](references/system-archetypes.md)。

1. **定義系統邊界**：哪些在裡面、哪些在外面？
2. **描繪關鍵變數**：重要的存量（會累積的量）有哪些？
3. **找出回饋迴路**：哪些是增強迴路？哪些是平衡迴路？
4. **找出延遲**：哪裡的因和果在時間上是分開的？
5. **找出槓桿點**：在哪裡做小幅介入，能帶來最大的轉變？
6. **檢查意外後果**：這個介入可能會在系統的其他地方弄壞什麼？

## 輸出格式

```markdown
# Systems Analysis: {Problem}

## System Boundary
- In scope: ...
- Out of scope: ...

## Key Variables
- {Variable A}: {description}

## Feedback Loops
- Reinforcing: {A → B → A (amplifying)}
- Balancing: {A → B → C → opposes A (stabilizing)}

## Delays
- {Input} → {Effect} (delay: {timeframe})

## Leverage Points
1. {where small change = big impact}

## Unintended Consequences Risk
- If we {intervention}, it might also {side effect} because {loop/connection}
```

## 範例

### 正確的應用
**情境：** 為什麼多雇用工程師，專案沒有變快？

**增強迴路（預期的）**：更多工程師 → 更多程式碼 → 進度更快
**平衡迴路（非預期的）**：更多工程師 → 更多溝通成本 → 更多會議 → 寫程式的時間更少 → 進度更慢（Brooks 定律）
**延遲**：新工程師需要 3-6 個月才能有產出

**槓桿點**：不要加人，而是降低溝通成本（更小的團隊、更清楚的權責、更好的文件）✓

### 錯誤的應用
- 「營收下降。增加行銷預算。」→ 線性、單一原因的思考。忽略了：營收為什麼下降？是需求問題（飽和造成的平衡迴路）？還是流失問題（品質差 → 客訴 → 更多流失的增強迴路）？不同的根本原因需要不同的介入。

## 注意事項

- **系統會抗拒改變**：平衡回饋迴路會維持現狀。不處理迴路結構就硬推，會導致「修了也沒用」（fixes that fail）。
- **心智模型是片面的**：每個人對系統的心智模型都不完整。找不同的利害關係人一起描繪系統，能看出盲點。
- **意外後果是常態，不是例外**：在複雜系統裡，介入一定會產生副作用。問題只在於你有沒有找出重要的那些。
- **不是所有事都是系統**：因果關係清楚的簡單問題，不需要系統思考。留給線性思考行不通的問題。

## 參考資料

- 系統基模（Limits to Growth、Shifting the Burden 等）請看 `references/system-archetypes.md`
