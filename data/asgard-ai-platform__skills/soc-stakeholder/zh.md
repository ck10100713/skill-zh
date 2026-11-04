---
name: "soc-stakeholder"
description: "用識別、權力—利益矩陣分類和影響策略擬定，進行利害關係人分析。使用者需要為專案描繪利害關係人、處理互相衝突的利益、排定溝通的優先順序，或建立利害關係人參與計畫時使用，就算他們說的是「這需要誰核准」、「我要怎麼取得支持」或「誰可能擋下這個專案」也一樣。"
metadata:
  category: "WP-18 社會科學院"
  tags: ["social-science", "stakeholder-analysis", "project-management"]
---

# 利害關係人分析

## 概述

利害關係人分析會找出所有影響某個決策、或受其影響的人，依權力和利益把他們分類，並為每個群體設計參與策略。它能避免因為忘了某些利害關係人而出狀況，並讓力氣集中在最重要的關係上。

## 框架

```
IRON LAW: Map ALL Stakeholders Before Engaging Any

Identify the full stakeholder landscape FIRST. Engaging one powerful
stakeholder before understanding the others' positions can create
unintended alliances against you. A stakeholder you forgot to include
becomes your biggest risk.
```

### 權力—利益矩陣

| | 低利益 | 高利益 |
|---|---|---|
| **高權力** | **讓他滿意（Keep Satisfied）**：監控、主動告知，不要拿細節煩他 | **密切管理（Manage Closely）**：積極參與、定期溝通、讓他參與決策 |
| **低權力** | **監控（Monitor）**：投入最少心力，留意權力或利益的變化 | **保持知情（Keep Informed）**：定期更新、回應疑慮、借力成為擁護者 |

### 分析步驟

1. **找出**所有利害關係人（內部與外部）
2. **評估**每個人的權力（影響結果的能力）和利益（關切的程度）
3. **分類**到四個象限
4. **了解**每個利害關係人的立場：支持、中立或抗拒
5. **設計**依象限和立場而定的參與策略
6. **監控**權力或利益隨時間產生的變化

### 依立場區分的參與策略

| 立場 | 策略 |
|----------|---------|
| **支持者** | 賦權給他們，提供資訊讓他們能替你發聲 |
| **中立者** | 說明效益、降低他們感受到的風險、及早回應疑慮 |
| **抗拒者** | 深入了解他們的疑慮、找出共同點、讓他們參與設計 |

### 衝突管理

當利害關係人的利益互相衝突時：
1. 找出具體的衝突點
2. 把立場（他們說自己想要什麼）和利益（他們為什麼想要）分開
3. 找出能處理雙方底層利益的解決方案
4. 談判失敗時才升級，而且要升級到對雙方都有權力的利害關係人

## 輸出格式

```markdown
# Stakeholder Analysis: {Project/Decision}

## Stakeholder Map
| Stakeholder | Role | Power | Interest | Position | Quadrant |
|-------------|------|-------|----------|----------|----------|
| {name/role} | {relationship} | H/M/L | H/M/L | Support/Neutral/Resist | {strategy} |

## Power-Interest Matrix
| | Low Interest | High Interest |
|---|---|---|
| **High Power** | {names} | {names} |
| **Low Power** | {names} | {names} |

## Engagement Plan
| Stakeholder | Strategy | Frequency | Channel | Key Message |
|-------------|---------|-----------|---------|-------------|
| {name} | {approach} | {weekly/monthly/ad-hoc} | {meeting/email/report} | {tailored message} |

## Conflict Points
| Conflict | Stakeholders | Resolution Approach |
|----------|-------------|-------------------|
| {issue} | {A vs B} | {proposed resolution} |
```

## 範例

### 正確的應用
**情境：** 在一家中型公司導入新 CRM 系統的利害關係人分析
| 利害關係人 | 權力 | 利益 | 立場 | 策略 |
|-------------|-------|----------|----------|----------|
| CEO | 高 | 低 | 中立 | 讓他滿意：每月摘要，聚焦 ROI |
| 業務副總 | 高 | 高 | 支持者 | 密切管理：共同設計、擔任推動者 |
| IT 主管 | 高 | 高 | 抗拒（擔心整合問題） | 密切管理：及早讓他參與、回應技術疑慮 |
| 業務人員 | 低 | 高 | 抗拒（不想換工具） | 保持知情：訓練、展示省下的時間、回應疑慮 |
| 財務 | 中 | 低 | 中立 | 監控：需要時再告知預算 |

關鍵洞察：IT 主管是高權力 + 抗拒 = 最大的風險。在專案被擋下之前，先處理整合的疑慮 ✓

### 錯誤的應用
- 只描繪了內部的利害關係人，忘了 CRM 供應商、既有工具的供應商（可能會抗拒），以及關鍵客戶（會受到轉換影響）也都是利害關係人。違反鐵律：要描繪「所有」利害關係人。

## 注意事項

- **權力會轉移**：今天低權力的利害關係人，可能會獲得權力（升遷、組織變動）。每季重新評估。
- **隱藏的利害關係人**：執行助理、董事會成員的顧問、工會代表，也就是有非正式但真實影響力的人。
- **不要在低權力的利害關係人身上投入過度**：很容易把時間花在最大聲的批評者身上，但如果他們權力低，他們的抗拒擋不了你。要把精力集中在高權力的象限。
- **抗拒 ≠ 敵人**：抗拒的利害關係人通常有正當的疑慮。他們的意見可以改善專案。把抗拒當成資料，不是對立。
- **利害關係人疲乏**：對每個人過度溝通，既浪費他們的時間，也浪費你的。要讓溝通頻率配合所在的象限。

## 參考資料

- 與抗拒的利害關係人談判的技巧請看 `references/negotiation-tactics.md`
