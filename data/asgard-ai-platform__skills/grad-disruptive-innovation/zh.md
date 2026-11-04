---
name: "grad-disruptive-innovation"
description: "用 Christensen 的破壞式創新理論，評估低階市場與新市場對既有業者的威脅。當使用者需要評估新進者是否構成破壞式威脅、分析既有業者為什麼會輸給比較差但比較便宜的替代品，或設計瞄準過度服務客戶的破壞策略時，就用這個 skill。"
metadata:
  category: "WP-24 創新與國際化"
  tags: ["disruptive-innovation", "christensen", "low-end-disruption", "new-market-foothold", "sustaining-innovation", "incumbent-failure"]
---

# Disruptive Innovation (Christensen, 1997)

## Overview

破壞式創新理論解釋資源較少的小公司，怎麼成功挑戰既有的大廠。破壞發生在新進者瞄準被忽略的區塊（低階市場或非消費者），用更簡單、更便宜的產品切入，然後隨著效能提升往高階市場移動。既有業者理性地專注在有利潤的主流客戶，等到反應過來已經太遲。

## When to Use

**觸發條件：**
- 使用者問為什麼一家產品比較差的新創公司在搶市占
- 使用者需要評估新進者是破壞式威脅還是延續式威脅
- 使用者想設計瞄準過度服務客戶的市場進入策略
- 使用者提到「disruption」、「low-end market」或「good enough product」

**When NOT to use：**
- 延續式創新的管理（漸進式改良）-> 用 stage-gate 或創新漏斗
- 以平台為基礎的競爭 -> 用 grad-platform-economics
- 分析國家層級的創新系統 -> 用 grad-diamond

## Assumptions

```
IRON LAW: Disruption Comes from BELOW

Disruption originates from the LOW END or NEW MARKET — never from a
superior product attacking head-on. Incumbents fail because they
OVER-SERVE mainstream customers, creating a performance overshoot that
opens space for simpler, cheaper alternatives.

If the entrant competes on the SAME performance dimensions as the
incumbent, it is sustaining innovation — NOT disruption.
```

- 效能的進步速度比客戶需求的演進更快
- 既有業者是理性的，會往高階市場追求更高的利潤
- 被破壞的市場有可辨識的過度服務區塊

## Methodology

### Step 1: Map Performance Trajectories

把既有業者的效能進步軌跡，和客戶需求的範圍（從低階到高階）畫在一起。找出效能超過主流客戶吸收能力的地方。

### Step 2: Identify the Foothold

為新進者的策略分類：
- **Low-end foothold**：用更便宜、更簡單、「夠用就好」的產品瞄準過度服務的客戶（例如廉價航空 vs 全服務航空）
- **New-market foothold**：瞄準以前完全買不到這個產品的非消費者（例如個人電腦 vs 大型主機）

### Step 3: Assess Disruption Potential

評估三個條件：
1. **存在效能過剩**：主流客戶沒有用到他們付錢買的所有功能
2. **新進者有往高階移動的路徑**：這個比較簡單的產品可以隨時間進步
3. **既有業者的動機不對稱**：回應就等於自己蠶食高利潤的業務

### Step 4: Recommend Response Strategy

對既有業者：成立自主的事業單位、收購破壞者，或自己推出低階產品。對新進者：躲在雷達下面、漸進改良，準備好了才往高階移動。

## Output Format

```markdown
# Disruption Assessment: {Industry/Company}

## Performance Trajectory Analysis
- Incumbent performance vector: {key dimensions}
- Customer need threshold: {what "good enough" looks like}
- Overshoot zone: {where incumbent exceeds needs}

## Entrant Classification
- Type: Low-end foothold / New-market foothold / Sustaining (NOT disruptive)
- Target segment: {who the entrant serves}
- Core advantage: {why target segment prefers entrant}

## Disruption Potential: High / Medium / Low
1. Performance overshoot: {Yes/No — evidence}
2. Upmarket path: {Yes/No — mechanism}
3. Asymmetric motivation: {Yes/No — why incumbent won't respond}

## Strategic Recommendations
- For incumbent: {specific response}
- For entrant: {next moves}
```

## Gotchas

- **不是每個創新都是破壞式的**：依 Christensen 的定義，Uber 對計程車並不是破壞式創新，因為它是從高階市場開始的。標籤要貼準。
- **破壞是一個過程，不是一個事件**：它會花好幾年甚至幾十年展開。只看一個時間點的分析，會漏掉軌跡的動態。
- **既有業者可以反應**：破壞不是注定的。自主的事業單位（例如 IBM 的 PC 部門）可以抵擋破壞。
- **光有技術不算破壞**：商業模式和技術一樣重要。賣更高價的更好捕鼠器是延續式創新。
- **小心後見之明偏誤**：很多「破壞」的敘事是事後套上去的。要用可檢驗的預測，前瞻性地套用這個框架。

## References

- 想了解效能軌跡的數學形式化，見 `references/performance-trajectory-model.md`
- 想了解案例研究（鋼鐵迷你煉鋼廠、磁碟機），見 `references/disruption-cases.md`
