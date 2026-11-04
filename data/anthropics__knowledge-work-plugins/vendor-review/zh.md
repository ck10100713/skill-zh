---
name: vendor-review
description: 評估供應商：成本分析、風險評估和建議。在審閱新供應商的提案、決定要續約還是換掉合約、並排比較兩家供應商，或在採購簽核前建立 TCO 拆解和談判要點時使用。
argument-hint: "<供應商名稱或提案>"
---

# /vendor-review

> 如果看到不認識的 placeholder，或想確認目前連了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

用結構化分析評估供應商，涵蓋成本、風險、表現和契合度。

## 用法

```
/vendor-review $ARGUMENTS
```

## 我需要你提供什麼

- **供應商名稱**：你在評估誰？
- **情境**：新供應商評估、續約決策，還是比較？
- **細節**：合約條款、定價、提案文件，或目前的表現資料

## 評估框架

### 成本分析（總擁有成本）
- 總擁有成本（不只是授權費）
- 導入和遷移成本
- 訓練和 onboarding 成本
- 持續的支援與維護
- 退出成本（資料遷移、合約終止）

### 風險評估
- 供應商的財務穩定性
- 資安與合規狀況
- 集中風險（依賴單一供應商）
- 合約綁定與退出條款
- 業務持續運作與災難復原

### 績效指標
- SLA 遵守狀況
- 支援回應時間
- 運作時間與可靠度
- 功能交付節奏
- 客戶滿意度

### 比較矩陣
比較供應商時，產出並排矩陣，涵蓋：定價、功能、整合、資安、支援、合約條款和參考對象。

## 輸出

```markdown
## Vendor Review: [Vendor Name]
**Date:** [Date] | **Type:** [New / Renewal / Comparison]

### Summary
[2-3 sentence recommendation]

### Cost Analysis
| Component | Annual Cost | Notes |
|-----------|-------------|-------|
| License/subscription | $[X] | [Per seat, flat, usage-based] |
| Implementation | $[X] | [One-time] |
| Support/maintenance | $[X] | [Included or add-on] |
| **Total Year 1** | **$[X]** | |
| **Total 3-Year** | **$[X]** | |

### Risk Assessment
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [Risk] | High/Med/Low | High/Med/Low | [Mitigation] |

### Strengths
- [Strength 1]
- [Strength 2]

### Concerns
- [Concern 1]
- [Concern 2]

### Recommendation
[Proceed / Negotiate / Pass] — [Reasoning]

### Negotiation Points
- [Leverage point 1]
- [Leverage point 2]
```

## 如果有連接 Connector

如果有連接 **~~knowledge base**：
- 搜尋現有的供應商評估、合約和績效審閱
- 拉出採購政策和核准門檻

如果有連接 **~~procurement**：
- 拉出目前的合約條款、支出歷史和續約日期
- 把定價跟現有的供應商合約比較

## 小訣竅

1. **上傳提案**：我可以從供應商文件中抽出定價、條款和 SLA。
2. **比較供應商**：「Compare Vendor A vs Vendor B」可以拿到並排分析。
3. **附上目前的支出**：續約時，知道你現在付多少，有助於評估價格變動。
