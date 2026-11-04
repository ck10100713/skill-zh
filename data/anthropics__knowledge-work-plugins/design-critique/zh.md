---
name: design-critique
description: 針對易用性、層級和一致性取得結構化的設計回饋。用「review 這個設計」「critique 這個 mockup」「你覺得這個畫面如何？」觸發，或在從探索到最後修飾的任何階段，分享 Figma 連結或截圖來求回饋時使用。
argument-hint: "<Figma URL, screenshot, or description>"
---

# /design-critique

> 如果看到不熟悉的佔位符，或需要確認目前連接了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

從多個面向取得結構化的設計回饋。

## 用法

```
/design-critique $ARGUMENTS
```

Review 這個設計：@$1

如果有給 Figma URL，就從 Figma 把設計拉下來。如果參照的是檔案，就讀取它。否則請使用者描述或分享他們的設計。

## 我需要你提供什麼

- **設計本身**：Figma URL、截圖，或詳細的描述
- **脈絡**：這是什麼？給誰用？現在是哪個階段（探索、精修、定稿）？
- **重點**（選填）：「著重在 mobile」或「著重在 onboarding 流程」

## Critique 框架

### 1. 第一印象（2 秒）
- 視線最先被什麼吸引？這樣對嗎？
- 情緒上的反應是什麼？
- 用途是不是一眼就清楚？

### 2. 易用性
- 使用者能達成他的目標嗎？
- 導覽直覺嗎？
- 可互動的元素夠明顯嗎？
- 有沒有多餘的步驟？

### 3. 視覺層級
- 有沒有清楚的閱讀順序？
- 該強調的元素有被強調嗎？
- 留白用得有效嗎？
- 字體排印有建立出對的層級嗎？

### 4. 一致性
- 有遵守 design system 嗎？
- 間距、顏色和字體排印一致嗎？
- 相似的元素行為也相似嗎？

### 5. 無障礙
- 顏色對比度
- 觸控目標大小
- 文字可讀性
- 圖片的替代文字

## 怎麼給回饋

- **要具體**：說「CTA 跟導覽列在搶焦點」，不要說「版面很亂」
- **解釋原因**：把回饋連到設計原則或使用者需求
- **提出替代方案**：不要只指出問題，要提解法
- **肯定做得好的地方**：好的回饋也包含正面的觀察
- **配合階段**：早期探索和最後修飾，給的回饋不一樣

## 輸出

```markdown
## Design Critique: [Design Name]

### Overall Impression
[1-2 sentence first reaction — what works, what's the biggest opportunity]

### Usability
| Finding | Severity | Recommendation |
|---------|----------|----------------|
| [Issue] | 🔴 Critical / 🟡 Moderate / 🟢 Minor | [Fix] |

### Visual Hierarchy
- **What draws the eye first**: [Element] — [Is this correct?]
- **Reading flow**: [How does the eye move through the layout?]
- **Emphasis**: [Are the right things emphasized?]

### Consistency
| Element | Issue | Recommendation |
|---------|-------|----------------|
| [Typography/spacing/color] | [Inconsistency] | [Fix] |

### Accessibility
- **Color contrast**: [Pass/fail for key text]
- **Touch targets**: [Adequate size?]
- **Text readability**: [Font size, line height]

### What Works Well
- [Positive observation 1]
- [Positive observation 2]

### Priority Recommendations
1. **[Most impactful change]** — [Why and how]
2. **[Second priority]** — [Why and how]
3. **[Third priority]** — [Why and how]
```

## 如果有連接 connector

如果有連接 **~~design tool**：
- 直接從 Figma 拉設計，檢查元件、token 和圖層
- 對照現有的 design system 檢查一致性

如果有連接 **~~user feedback**：
- 把設計決策跟近期的使用者回饋和客服 ticket 交叉比對

## 小提醒

1. **分享脈絡**：說「這是 B2B SaaS 的結帳流程」，我就能給更貼切的回饋。
2. **說明你在哪個階段**：早期探索和最後修飾，給的回饋不一樣。
3. **請我聚焦**：說「只看導覽列」，我就能在那一塊給你更深入的意見。
