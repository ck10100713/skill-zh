---
name: "ux-jtbd"
description: "運用 Jobs to Be Done（JTBD）框架，透過功能性、情感性和社會性的任務，來理解顧客的動機。當使用者需要了解顧客為什麼「雇用」或「解雇」某個產品、發掘未被滿足的需求、撰寫 job story，或以顧客成果重新框架產品策略時使用這個 skill，就算他們說的是「顧客為什麼買這個」、「這個滿足了什麼需求」或「顧客沒有照我們預期的方式使用產品」也一樣。"
metadata:
  category: "WP-21 設計/資訊/傳播/公衛"
  tags: ["product", "jtbd", "jobs-to-be-done", "customer-insight"]
---

# Jobs to Be Done（JTBD）

## 概述

JTBD 把產品策略重新圍繞在顧客想完成的「任務」（job）上。人們不是在買產品，而是在特定情境下「雇用」產品來取得進展。理解這個任務，就能看出真正的競爭對手（通常不是你以為的那些）和未被滿足的需求。

## 框架

```
IRON LAW: The Job Is About the Customer's Progress, Not Your Product
（鐵律：任務關乎顧客的進展，不是你的產品）

「幫我管理我的任務」是一個 job。「使用我們的任務管理 app」不是。
這個 job 獨立於任何解法而存在。你的產品只是完成這個 job 的「其中一種」方式，
顧客可以「雇用」試算表、筆記本或白板來做同一份 job。

要從「顧客」的角度定義 job，絕對不要從產品的角度。
```

### 一個任務的三個面向

| 面向 | 意思 | 例子（早晨咖啡） |
|-----------|-------------|------------------------|
| **功能性** | 要完成的實際任務 | 「攝取咖啡因，讓自己上班時保持清醒」 |
| **情感性** | 他們想要的感受 | 「覺得自己是在犒賞自己，不只是勉強撐過去」 |
| **社會性** | 他們想被怎麼看待 | 「讓同事看到我有品味（精品咖啡）」 |

### Job Story 格式

用 job story 取代 user story：

```
When [situation/trigger],
I want to [motivation/job],
so I can [expected outcome].
```

範例：「When I'm rushing to work and haven't had breakfast, I want a quick energy boost that doesn't feel unhealthy, so I can start my morning focused and not guilty about my diet.」

### 分析步驟

1. **找出情境/觸發點**：什麼狀況產生了這個需求？
2. **發掘任務**：顧客想取得什麼進展？
3. **對應三個面向**：功能性 + 情感性 + 社會性
4. **找出目前的「雇用」對象**：他們現在用什麼來完成這個任務？
5. **找出進展的力量**：推力（對現況不滿）+ 拉力（新方案的吸引力）vs 焦慮（對新方案的恐懼）+ 習慣（現況的舒適）
6. **發掘未被滿足的需求**：現有解法在哪裡不足？

### 進展的力量（轉換）

```
PUSH (away from current) + PULL (toward new) > ANXIETY (about new) + HABIT (of current)
= Customer switches
```

理解這四股力量，就能解釋顧客為什麼會轉換（或不轉換）。

## 輸出格式

```markdown
# JTBD Analysis: {Product/Category}

## The Job
When [situation], I want to [job], so I can [outcome].

## Three Dimensions
- Functional: {practical need}
- Emotional: {desired feeling}
- Social: {desired perception}

## Current Hires (Competition)
| Solution | What Job It Does | Where It Falls Short |
|----------|-----------------|---------------------|
| {product/workaround} | {what need it serves} | {unmet need} |

## Forces of Progress
- Push: {what's driving them away from current solutions}
- Pull: {what attracts them to new solutions}
- Anxiety: {what holds them back from switching}
- Habit: {what keeps them using current solutions}

## Unmet Needs & Opportunities
1. {unmet need} → {opportunity}
```

## 範例

### 正確的應用
**情境：** Airbnb 的 JTBD

**任務**：「When I'm planning a trip and want a local experience, I want to stay in a real neighborhood, so I can feel like I belong there rather than being a tourist.」

**真正的競爭對手**：不只是飯店，還包括青年旅館、借住朋友家，甚至是「不去旅行」（因為飯店感覺太「觀光客」，不值得）。Airbnb 在這個任務上真正的競爭對手，包括任何能提供「在地歸屬感體驗」的東西 ✓

### 錯誤的應用
- 「任務是使用我們的 app」 → 以產品為中心，不是以顧客為中心。違反鐵律。

## 常見陷阱

- **任務是穩定的，解法會變**：「快速從 A 到 B」幾百年來都是同一個 job。解法從馬變成汽車再變成共乘。要為 job 設計，不是為目前的解法設計。
- **一個產品可以服務多個任務**：咖啡被雇用來「提神」（早上）、「社交聯繫」（咖啡廳開會）和「有效率的休息」（下午低潮）。不同情境、不同任務、不同競爭對手。
- **不要把需求和解法搞混**：「我需要一匹更快的馬」是解法。「我需要更快到那裡」是需求。要往下挖。
- **情感性和社會性任務常常比功能性更重要**：人們買精品咖啡，不只是為了咖啡因（功能性），也為了自我犒賞（情感性）和地位（社會性）。

## 參考資料

- 轉換訪談方法論，見 `references/switch-interviews.md`
