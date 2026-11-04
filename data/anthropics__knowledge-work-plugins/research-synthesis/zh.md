---
name: research-synthesis
description: 把使用者研究整理成主題、洞察與建議。手上有訪談逐字稿、問卷結果、可用性測試筆記、客服工單或 NPS 回覆，需要提煉成模式、使用者分群和有優先順序的下一步時使用。
argument-hint: "<research data, transcripts, or survey results>"
---

# /research-synthesis

> 如果看到不認識的 placeholder，或需要確認目前連接了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

把使用者研究資料整理成可以行動的洞察。研究方法、訪談指南和分析框架請看 **user-research** skill。

## 用法

```
/research-synthesis $ARGUMENTS
```

## 我接受的輸入

- 訪談逐字稿或筆記
- 問卷結果（CSV、貼上的資料）
- 可用性測試錄影或筆記
- 客服工單或回饋
- NPS/CSAT 回覆
- App store 評論

## 輸出

```markdown
## Research Synthesis: [研究名稱]
**Method:** [Interviews / Survey / Usability Test] | **Participants:** [X]
**Date:** [日期範圍] | **Researcher:** [姓名]

### Executive Summary
[3 到 4 句話概述主要發現]

### Key Themes

#### Theme 1: [名稱]
**Prevalence:** [Y 位參與者中的 X 位]
**Summary:** [這個主題在講什麼]
**Supporting Evidence:**
- "[引言]" — P[X]
- "[引言]" — P[X]
**Implication:** [這對產品代表什麼]

#### Theme 2: [名稱]
[格式相同]

### Insights → Opportunities

| Insight | Opportunity | Impact | Effort |
|---------|-------------|--------|--------|
| [我們學到什麼] | [我們可以做什麼] | High/Med/Low | High/Med/Low |

### User Segments Identified
| Segment | Characteristics | Needs | Size |
|---------|----------------|-------|------|
| [名稱] | [描述] | [主要需求] | [大約佔比 %] |

### Recommendations
1. **[高優先]** — [為什麼，依據哪些發現]
2. **[中優先]** — [為什麼]
3. **[低優先]** — [為什麼]

### Questions for Further Research
- [我們還不知道的事]

### Methodology Notes
[研究是怎麼進行的，有哪些限制或偏誤要註明]
```

## 如果有連接 Connector

如果有連接 **~~user feedback**：
- 拉出客服工單、功能需求和 NPS 回覆來補充研究資料
- 把主題和真實的使用者抱怨與需求交叉比對

如果有連接 **~~product analytics**：
- 用使用量資料和行為指標驗證質性發現
- 量化已找出的痛點影響

如果有連接 **~~knowledge base**：
- 搜尋過去的研究與發現來比對
- 把這份整理發布到你的研究資料庫

## 小提醒

1. **放進原始引言**：直接引用參與者的話，會讓洞察更可信、更令人印象深刻。
2. **把觀察和詮釋分開**：「8 位使用者中有 5 位點錯按鈕」是觀察。「按鈕位置讓人困惑」是詮釋。
3. **能量化就量化**：「大部分使用者」很模糊。「10 位使用者中有 7 位」才具體。
