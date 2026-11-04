---
name: "grad-blooms"
description: "運用 Bloom 修訂版分類學，在六個認知層次上分類學習目標並設計評量。當使用者需要寫出特定認知層次的學習目標、讓評量與教學目標對齊，或評估課程在認知複雜度上的分布時使用。就算使用者只說「怎麼寫學習目標」、「這需要什麼層次的思考」或「高階思考技能」也要用。"
metadata:
  category: "WP-33 傳播/教育/公共行政"
  tags: ["education", "blooms-taxonomy", "learning-objectives", "assessment"]
---

# Bloom 修訂版分類學

## 概述

Bloom 修訂版分類學（Anderson & Krathwohl, 2001）把認知歷程分成六個有階層的層次：記憶（Remember）、理解（Understand）、應用（Apply）、分析（Analyze）、評鑑（Evaluate）和創造（Create）。搭配知識向度（事實、概念、程序、後設認知），它提供了一個二維的框架，用來設計與評量學習。

## 何時使用

**觸發條件：**
- 寫出特定認知層次的學習目標
- 讓評量方法與預期的學習成果對齊
- 稽核課程在認知複雜度上的平衡

**何時不要用：**
- 設計有鷹架的學習經驗時（用建構主義 / ZPD）
- 在教學設計中管理認知負荷時（用認知負荷理論）
- 把科技整合進教學時（用 TPACK 框架）

## 假設

```
IRON LAW: Higher-Order Thinking REQUIRES a Foundation of Lower-Order Knowledge

You cannot analyze what you don't understand. You cannot evaluate
what you haven't analyzed. You cannot create without evaluation criteria.
The hierarchy is:
  Remember → Understand → Apply → Analyze → Evaluate → Create
Skipping levels produces superficial "higher-order" work built on
a weak knowledge foundation.
```

## 方法論

### 步驟 1：找出知識類型
分類目標知識：事實（術語、細節）、概念（類別、原理）、程序（做法、技巧），或後設認知（自我覺察、策略）。

### 步驟 2：選擇認知層次
選擇適當的認知歷程層次。每個層次都使用可觀察、可衡量的行動動詞。

### 步驟 3：寫出目標
組合：「學生將能夠 [行動動詞] [知識內容] [情境/條件]。」確保動詞與預期的認知層次一致。

### 步驟 4：對齊評量
讓評量方法與認知層次相符。記憶/理解 → 客觀測驗。應用/分析 → 個案研究、習題。評鑑/創造 → 專題、學習歷程檔案、論文。

## 輸出格式

```markdown
# Learning Objectives Analysis: {Course/Module}

## Taxonomy Mapping
| Objective | Cognitive Level | Knowledge Type | Action Verb | Assessment Method |
|-----------|----------------|---------------|-------------|-------------------|
| ... | Remember/Understand/Apply/Analyze/Evaluate/Create | Factual/Conceptual/Procedural/Metacognitive | ... | ... |

## Cognitive Level Distribution
- Lower-order (Remember, Understand, Apply): {count, %}
- Higher-order (Analyze, Evaluate, Create): {count, %}
- Balance assessment: {adequate or needs adjustment}

## Alignment Check
- Objectives ↔ Instruction: {aligned / gaps}
- Objectives ↔ Assessment: {aligned / gaps}

## Recommendations
{Specific suggestions for improving cognitive level balance and alignment}
```

## 常見陷阱

- **動詞是含糊的**：「理解」無法直接觀察。要用具體的動詞：「解釋」、「分類」、「摘要」。有多種分類學把動詞對應到層次，它們不一定一致。
- **階層不是僵硬的**：修訂版分類學承認，評鑑和創造之間的順序可以變動。有些創造性的任務不需要先評鑑，有些評鑑也不需要創造。
- **高階 ≠ 較好**：不是所有目標都該放在創造層次。基礎課程本來就合理地強調記憶和理解。目標是「適當」的層次，不是最高層次。
- **動詞配對的文化**：換上一個「較高階」的動詞，卻沒有改變實際的認知要求，只是表面功夫。如果學生只是背誦一份背好的分析，「分析這個定義」仍然是記憶層次。
- **情意與動作技能領域**：Bloom 的認知分類學是「三個」領域之一。它沒有涵蓋態度/價值觀（情意）或身體技能（動作技能）。

## 參考資料

- 各層次完整的動詞清單，見 `references/verb-taxonomy.md`
- 對齊矩陣與評量設計，見 `references/alignment-matrix.md`
