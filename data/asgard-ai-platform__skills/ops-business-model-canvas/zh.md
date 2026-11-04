---
name: "ops-business-model-canvas"
description: "用商業模式圖（BMC）的九大構面來描繪與評估商業模式。使用者需要設計新的商業模式、評估現有的商業模式、比較不同的商業模式選項，或為策略會議做準備時使用，就算他們說的是「描述我們的商業模式」、「我們怎麼賺錢」、「填一張 BMC」或「設計新的營收模式」也一樣。"
metadata:
  category: "WP-10 通用商業"
  tags: ["business", "business-model-canvas", "strategy"]
---

# 商業模式圖（Business Model Canvas）

## 框架

```
IRON LAW: All Nine Blocks Must Be Completed and Consistent

The BMC is a SYSTEM — each block depends on others. A value proposition
without a matching customer segment is an invention, not a business.
Revenue streams without cost structure analysis is wishful thinking.
Fill ALL nine blocks and check that they tell a coherent story.
```

### 九大構面

| # | 構面 | 問題 | 右側（價值）／左側（效率） |
|---|-------|---------|---------------------------------------------|
| 1 | **客戶區隔（Customer Segments）** | 我們在為誰創造價值？ | 右 |
| 2 | **價值主張（Value Propositions）** | 我們提供什麼價值？ | 中 |
| 3 | **通路（Channels）** | 我們如何觸及客戶？ | 右 |
| 4 | **客戶關係（Customer Relationships）** | 我們如何與客戶互動？ | 右 |
| 5 | **收益流（Revenue Streams）** | 我們如何賺錢？ | 右 |
| 6 | **關鍵資源（Key Resources）** | 我們需要什麼才能提供價值？ | 左 |
| 7 | **關鍵活動（Key Activities）** | 我們必須把什麼做好？ | 左 |
| 8 | **關鍵合作夥伴（Key Partnerships）** | 誰在幫我們？ | 左 |
| 9 | **成本結構（Cost Structure）** | 主要成本是什麼？ | 左 |

### 逐構面指南

**客戶區隔**：列出有不同需求的不同群體。大眾市場？利基市場？多邊平台？

**價值主張**：針對「每一個」區隔，你解決什麼問題、或滿足什麼需求？要具體：「品質」不是價值主張。「有機雜貨當日送達」才是。

**通路**：客戶如何發現、評估、購買、收貨和取得支援？把整個旅程畫出來。

**客戶關係**：自助服務？個人協助？社群？自動化？共同創造？

**收益流**：針對每個區隔：他們付什麼？怎麼付？（訂閱、交易、授權、廣告、freemium）

**關鍵資源**：實體、智慧財產（IP、資料）、人力、財務，哪些是不可或缺的？

**關鍵活動**：生產？平台管理？解決問題？銷售？

**關鍵合作夥伴**：供應商、策略聯盟、合資。「為什麼」要合作？（最佳化、降低風險、取得資源）

**成本結構**：固定 vs 變動。最大的成本驅動因素是什麼？是成本驅動還是價值驅動的模式？

### 分析步驟

1. 用便利貼等級的細節（短句）填滿全部 9 個構面
2. 檢查「一致性」：價值主張跟區隔對得上嗎？通路觸及得到區隔嗎？收益流撐得起成本結構嗎？
3. 找出「風險」：哪些構面的不確定性最高？那些就是你風險最大的假設。
4. 「比較」：把目前的模式和提議的新模式並排對照

## 輸出格式

```markdown
# Business Model Canvas: {Business}

## Canvas

| Block | Description |
|-------|-----------|
| **Customer Segments** | {who} |
| **Value Propositions** | {what value, for which segment} |
| **Channels** | {how you reach and serve} |
| **Customer Relationships** | {type of relationship} |
| **Revenue Streams** | {how you make money} |
| **Key Resources** | {essential assets} |
| **Key Activities** | {critical operations} |
| **Key Partnerships** | {key partners and why} |
| **Cost Structure** | {major cost categories} |

## Consistency Check
| Connection | Consistent? | Notes |
|-----------|------------|-------|
| Value Prop ↔ Segments | ✓/✗ | {match?} |
| Channels ↔ Segments | ✓/✗ | {reachable?} |
| Revenue ↔ Cost | ✓/✗ | {profitable?} |

## Riskiest Assumptions
1. {block: assumption that needs validation}
```

## 注意事項

- **BMC 是起點，不是答案**：它能讓思考有結構，但不會驗證假設。每個有風險的構面都需要 Lean Startup 式的測試。
- **收益模式是最難的構面**：「用戶會付費」是一個假設。付多少？多常付？根據什麼證據願意付？
- **多邊平台需要分開的區隔**：Uber 有司機「和」乘客。每個區隔都有自己的價值主張、通路和收益模式。兩邊都要畫。
- **不要把活動和資源搞混**：「軟體開發」是活動。「工程團隊」是資源。「原始碼」是資源。要把它們分開。
- **BMC 應該是活的文件**：每季檢視並更新。商業模式會演化，這張圖應該反映目前的現實，不是最初的計畫。

## 參考資料

- 價值主張設計的深入探討請看 `references/value-prop-canvas.md`
