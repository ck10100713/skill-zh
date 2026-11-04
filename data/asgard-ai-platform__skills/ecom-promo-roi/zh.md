---
name: "ecom-promo-roi"
description: "計算並分析促銷的 ROI，包含增量銷售提升、毛利影響與促銷類型比較。當使用者需要評估一場促銷有沒有賺錢、比較促銷類型、模擬促銷情境，或最佳化促銷預算時使用。就算使用者只說「這次特賣值得嗎」、「哪種促銷最有效」、「我們是不是折扣給太多了」或「規劃下一場促銷」也要用。"
metadata:
  category: "WP-01 電商"
  tags: ["e-commerce", "promotion", "roi", "marketing"]
---

# 促銷 ROI 分析

## 框架

```
IRON LAW: Measure INCREMENTAL Sales, Not Total Sales During Promo

A promotion that generates $100K in revenue during a sale week looks great —
until you realize $80K would have happened anyway (baseline). The incremental
lift is only $20K. If the discount cost $25K in margin, the promo LOST money.

Promo ROI = (Incremental Revenue × Margin - Promo Cost) / Promo Cost
```

### 關鍵指標

| 指標 | 公式 |
|--------|---------|
| **增量營收（Incremental Revenue）** | 促銷期間營收 - 基準營收（沒有促銷時本來會有的營收） |
| **促銷成本** | 折扣金額 + 行銷支出 + 營運成本 |
| **促銷 ROI** | (增量毛利 - 促銷成本) / 促銷成本 |
| **蠶食率（Cannibalization Rate）** | 就算不打折也會以原價成交的促銷銷售比例 |
| **提前消費率（Pull-Forward Rate）** | 只是提早購買的促銷銷售比例（客戶下週本來就會買） |

### 促銷類型比較

| 類型 | 機制 | 優點 | 缺點 |
|------|-----------|------|------|
| % 折扣 | 全館 8 折 | 簡單、流量高 | 侵蝕品牌、養成等折扣的習慣 |
| 滿額折 | 滿 NT$1000 折 NT$200 | 拉高 AOV | 對低客單價的客戶吸引力較小 |
| 買一送一 | 買一送一 | 快速消化庫存 | 毛利直接砍 50%、吸引只愛撿便宜的人 |
| 滿額贈 | 消費滿額送贈品 | 保護價格認知 | 贈品成本，不一定帶來增量 |
| 限時閃購 | 限時深度折扣 | 急迫感、互動高 | 營運壓力、蠶食 |
| 會員點數 | 賺點/兌點 | 建立留存、成本遞延 | 管理複雜、有兌換負債 |

### 分析步驟

**階段 1：建立基準**
- 沒有促銷的話，營收本來會是多少？（前一期、去年同期，或對照組）
- 考慮季節性、星期幾的效應和趨勢

**階段 2：計算增量影響**
- 促銷總營收 - 基準 = 增量
- 扣掉蠶食和提前消費的估計值
- 計算增量的毛利（不是營收）

**階段 3：計算完整成本**
- 讓出去的折扣金額
- 行銷支出（廣告、email、創意製作）
- 營運成本（倉庫加班、客服量暴增）

**階段 4：計算 ROI 並決策**
- ROI > 0：促銷有賺錢
- ROI < 0 但有策略考量（拉新客戶、清庫存）：仍可能合理
- ROI < 0 又沒有策略理由：不要再辦

## 輸出格式

```markdown
# Promo ROI Report: {Promotion Name}

## Promo Summary
- Type: {discount type}
- Period: {dates}
- Offer: {details}

## Results
| Metric | Value |
|--------|-------|
| Total Revenue (promo period) | ${X} |
| Baseline Revenue (estimated) | ${X} |
| **Incremental Revenue** | **${X}** |
| Incremental Gross Profit | ${X} |
| Promo Cost (discount + marketing + ops) | ${X} |
| **Promo ROI** | **{X%}** |

## Profitability Assessment
{Profitable / Unprofitable — with context}

## Recommendation
{Repeat / Modify / Discontinue — with rationale}
```

## 常見陷阱

- **估計基準是最難的部分**：你的 ROI 準不準，取決於你對「沒有促銷時會怎樣」估得多好。可以用去年同期當起點，再依趨勢調整。
- **促銷後的低谷是真的**：促銷結束後，銷售常常掉到基準「以下」（客戶把購買提前了）。分析時要把低谷期也算進去。
- **折扣會上癮**：客戶學會等特賣。追蹤以原價賣出的營收占比的長期變化，如果持續下滑，就是有折扣依賴的問題。
- **新舊客戶的組合很重要**：一場促銷以負 ROI 換來 500 位新客戶，如果他們的 LTV 撐得起獲客成本，可能還是值得的。要分開追蹤。

## 參考資料

- 促銷優惠的 A/B 測試，見 `references/promo-testing.md`
