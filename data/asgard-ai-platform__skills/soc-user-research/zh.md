---
name: "soc-user-research"
description: "用訪談、焦點團體、問卷和現場觀察來設計並執行使用者研究。使用者需要了解客戶需求、驗證產品假設、蒐集質性洞察，或設計研究時使用，就算他們說的是「我們需要跟使用者聊聊」、「我們怎麼驗證這個想法」或「我們的客戶實際上怎麼想」也一樣。"
metadata:
  category: "WP-18 社會科學院"
  tags: ["social-science", "user-research", "qualitative-methods"]
---

# 使用者研究方法

## 概述

使用者研究是透過直接的觀察和對話，而不是假設，來找出人們需要什麼、想要什麼、做什麼。這個 skill 涵蓋四種核心方法：深度訪談、焦點團體、問卷和現場觀察，以及各自該在什麼時候用。

## 框架

```
IRON LAW: Method Follows Question

Choose the method based on what you need to learn, not what's convenient.
"Why" questions → Interviews/Observation (qualitative)
"How many" questions → Surveys (quantitative)
"What do they really do" → Observation (behavioral)

Running a survey to answer "why" produces misleading data.
```

### 方法選擇

| 方法 | 最適合 | 樣本 | 深度 | 成本 |
|--------|---------|--------|-------|------|
| **深度訪談** | 了解動機、痛點、心智模型 | 8-15 人 | 非常高 | 中 |
| **焦點團體** | 探索反應、產生點子、社會動態 | 每組 6-10 人，2-3 組 | 中 | 中 |
| **問卷** | 大規模衡量普及程度、偏好、人口統計 | 100 份以上的回覆 | 低 | 低-中 |
| **現場觀察** | 了解情境中的實際行為（不是自己回報的） | 5-10 場 | 非常高 | 高 |

### 深度訪談指南

1. **暖身**：建立融洽關係（2 分鐘）：「跟我聊聊你的角色／你的一天」
2. **情境**：了解他們的世界（5 分鐘）：「帶我走一遍你上次…的經過」
3. **核心問題**：探索主題（20 分鐘）：開放式、不用引導式問題
4. **追問**：對有趣的線索深入挖掘：「多說一點」、「為什麼？」
5. **收尾**：總結並確認（3 分鐘）：「我理解得對嗎，你的意思是…？」

**規則**：
- 問過去的行為，不要問假設的未來（問「你當時做了什麼？」，不要問「你會怎麼做？」）
- 絕對不要問「你會用這個嗎？」，人在預測自己的行為上糟透了
- 沉默是一種工具，讓他們自己把空白填滿

### 問卷設計

1. 從篩選問題開始（確認受訪者資格）
2. 從一般到具體
3. 敏感的／人口統計的問題放最後
4. 限制在 15-20 題（5-7 分鐘填完）
5. 盡可能使用已驗證的量表（Likert、NPS、SUS）

**要避免的題型**：
- 雙重問題：「這個產品快速而且可靠嗎？」（是指哪一個？）
- 引導式：「你不覺得我們的 app 很容易用嗎？」
- 假設式：「你願意為這個功能每月付 $10 嗎？」

### 分析

**質性**（訪談、觀察）：
- 親和圖：把觀察結果分組成主題
- 在 5 位以上的受訪者之間找模式
- 逐字引用，不要轉述

**量化**（問卷）：
- 先看描述統計（平均數、分布）
- 依區隔做交叉分析
- 比較時看統計顯著性（p < 0.05）

## 輸出格式

```markdown
# User Research Plan: {Project}

## Research Questions
1. {what we need to learn}

## Method
- Type: {interview / focus group / survey / observation}
- Rationale: {why this method for this question}
- Sample: {who, how many, recruitment criteria}
- Timeline: {duration}

## Discussion Guide / Survey Instrument
{Key questions or survey structure}

## Analysis Plan
{How findings will be synthesized}
```

## 範例

### 正確的應用
**情境：** 了解使用者為什麼在結帳時放棄一個外送 app
- **方法**：深度訪談（需要了解「為什麼」，不是「有多少」）
- **樣本**：過去 30 天內放棄結帳的 10 位使用者（透過 app 內資料招募）
- **關鍵問題**：「帶我走一遍你上一筆沒有完成的訂單。發生了什麼事？」（行為性、過去式、開放式 ✓）

### 錯誤的應用
- 問卷問「如果我們取消外送費，你會完成訂單嗎？」→ 假設式。使用者會說會，但行為不一定會改變。應該觀察實際行為，或用真正的實驗來測試。

## 注意事項

- **5 位使用者能找出 85% 的可用性問題**（Nielsen）：對可用性測試來說，超過 5 位之後邊際效益遞減。要了解動機的話，需要 8-15 位。
- **自己回報的行為 ≠ 實際行為**：人們會高估自己吃得多健康、多常運動，以及願意付多少錢。觀察和行為資料 > 自己回報。
- **招募偏誤**：如果你招募的是「我們 app 的使用者」，就會漏掉非使用者和已流失的使用者。要小心定義母體。
- **訪談者偏誤**：訪談者的反應（點頭、「太棒了！」）會影響回答。要保持中立。
- **問卷衡量的是你問的東西，不是重要的東西**：如果你沒想到要問某個痛點，問卷就不會揭露它。要先用質性研究找出對的問題。

## 參考資料

- 訪談腳本範本請看 `references/interview-templates.md`
- 問卷設計最佳實務請看 `references/survey-design.md`
