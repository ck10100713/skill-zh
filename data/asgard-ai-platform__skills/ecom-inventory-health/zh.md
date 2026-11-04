---
name: "ecom-inventory-health"
description: "用週轉率、ABC 分類、安全庫存計算，以及缺貨與庫存過多的診斷，分析庫存健康度。當使用者需要最佳化庫存水位、降低持有成本、避免缺貨，或依庫存優先順序為商品分類時使用。就算使用者只說「我們庫存太多了」、「熱銷品老是缺貨」、「安全庫存要多少」或「該把心力放在哪些商品」也要用。"
metadata:
  category: "WP-01 電商"
  tags: ["e-commerce", "inventory", "supply-chain", "abc-analysis"]
---

# 庫存健康度分析

## 概述

庫存健康度要在兩種風險之間取得平衡：缺貨（流失銷售、客戶不滿）和庫存過多（持有成本、過時報廢）。這個 skill 提供衡量、分類和最佳化庫存水位的工具。

## 框架

```
IRON LAW: Not All SKUs Deserve Equal Attention

ABC classification shows that ~20% of SKUs drive ~80% of revenue.
Treat A-items (top 20% revenue) with tight control and frequent review.
C-items (bottom 50% revenue) get simple rules and less attention.
Equal treatment of all SKUs wastes resources on low-impact items.
```

### 關鍵指標

| 指標 | 公式 | 健康範圍 |
|--------|---------|--------------|
| **庫存週轉率** | COGS / 平均庫存 | 每年 4-12 次（依產業而異） |
| **庫存天數（DOI）** | 365 / 庫存週轉率 | 30-90 天 |
| **缺貨率** | 缺貨次數 / 總需求次數 | < 2-5% |
| **滿足率（Fill Rate）** | 完整出貨的訂單 / 總訂單 | > 95% |
| **持有成本** | 平均庫存 × 持有成本率（通常每年 20-30%） | 越低越好 |
| **呆滯庫存比例** | 6 個月以上零銷售的品項 / 總 SKU | < 10% |

### ABC 分類

| 等級 | 營收占比 | SKU 占比 | 策略 |
|-------|----------|-------|----------|
| **A** | 約 80% | 約 20% | 嚴格控管、頻繁檢視、最佳化安全庫存 |
| **B** | 約 15% | 約 30% | 適度控管、定期檢視 |
| **C** | 約 5% | 約 50% | 簡單規則、最小/最大庫存量、考慮淘汰 |

### 安全庫存計算

```
Safety Stock = Z × σ_d × √(Lead Time)

Where:
- Z = service level factor (1.65 for 95%, 2.33 for 99%)
- σ_d = standard deviation of daily demand
- Lead Time = supplier lead time in days
```

### 再訂購點

```
Reorder Point = (Average Daily Demand × Lead Time) + Safety Stock
```

### 診斷步驟

**階段 1：整體健康檢查**
- 計算整體庫存的週轉率和 DOI
- 跟產業基準比較
- 找出趨勢：在改善還是惡化？

**階段 2：ABC 分類**
- 依營收貢獻替所有 SKU 排名
- 分成 A/B/C
- 檢查：A 類商品庫存充足嗎？C 類商品是不是囤太多？

**階段 3：找出問題**
- **庫存過多**：DOI > 90 天、呆滯庫存 > 10%、持有成本上升
- **缺貨**：滿足率 < 95%、有流失銷售的紀錄、客訴
- **失衡**：A 類商品庫存不足，C 類商品卻庫存過多

**階段 4：最佳化**
- 依 ABC 等級設定安全庫存
- 對 A 類商品導入再訂購點
- 清掉呆滯庫存（折扣、組合包、捐贈）
- 透過跟供應商談判縮短前置時間

## 輸出格式

```markdown
# Inventory Health Report: {Business}

## Summary
| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Turnover | {X}x | {X}x | 🟢/🟡/🔴 |
| DOI | {X} days | {X} days | 🟢/🟡/🔴 |
| Fill Rate | {X%} | >95% | 🟢/🟡/🔴 |
| Dead Stock | {X%} | <10% | 🟢/🟡/🔴 |

## ABC Distribution
| Class | SKUs | Revenue % | Avg DOI | Issue |
|-------|------|----------|---------|-------|
| A | {N} | {%} | {days} | {stockout risk?} |
| B | {N} | {%} | {days} | ... |
| C | {N} | {%} | {days} | {overstock?} |

## Top Issues
1. {issue with specific SKUs and data}

## Recommendations
1. {action with expected impact}
```

## 常見陷阱

- **季節性商品要另外處理**：1 月的泳裝會顯示成「呆滯庫存」，但不該清倉。要做季節調整，或依季節分開分析。
- **庫存週轉率因產業差異極大**：生鮮雜貨每年 20-50 次，時尚 4-6 次，電子產品 6-12 次。一定要在同產業內比較。
- **週轉低不一定不好，如果是刻意的**：策略性庫存（在漲價前先進貨、確保貨源）可以合理化較低的週轉。
- **ABC 分類會變動**：去年是 A 類的商品，今年可能變成 C 類。每季重新分類。
- **持有成本常被低估**：要包含倉庫租金、保險、過時報廢、資金成本（被綁住的錢的機會成本）、搬運人力。總計通常是每年庫存價值的 20-30%。

## 參考資料

- EOQ（經濟訂購量）模型，見 `references/eoq-model.md`
- 季節性需求預測，見 `references/seasonal-forecasting.md`
