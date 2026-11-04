---
name: "ecom-analytics"
description: "用 GA4 指標、轉換漏斗分析和關鍵電商 KPI 分析電商績效。當使用者需要評估網路商店表現、診斷轉換流失、設定電商追蹤，或建立績效儀表板時使用。就算使用者只說「為什麼業績下滑」、「最佳化我們的網路商店」、「幫電商設定 GA4」或「該追蹤哪些指標」也要用。"
metadata:
  category: "WP-01 電商"
  tags: ["e-commerce", "analytics", "ga4", "conversion"]
---

# 電商分析

## 概述

電商分析從流量、轉換和營收三個面向衡量網路商店的表現。這個 skill 涵蓋 GA4 電商追蹤設定、漏斗分析，以及關鍵指標的解讀，用來診斷商店為什麼表現好或不好。

## 框架

```
IRON LAW: Diagnose by Funnel Stage, Not by Symptom

"Sales are down" is a symptom, not a diagnosis. Decompose into funnel stages:
Traffic × Conversion Rate × AOV = Revenue

If revenue drops 20%, is it because traffic dropped (acquisition problem),
conversion dropped (UX/pricing problem), or AOV dropped (product mix problem)?
Each requires a completely different fix.
```

### 電商漏斗與關鍵指標

| 階段 | 指標 | 它告訴你什麼 |
|-------|---------|------------------|
| **獲客（Acquisition）** | Sessions、Users、流量來源、CPC、CAC | 吸引到足夠的訪客了嗎？從哪裡來？成本多少？ |
| **互動（Engagement）** | 每次工作階段頁數、停留時間、跳出率、商品瀏覽數 | 訪客有興趣嗎？有在逛嗎？ |
| **轉換（Conversion）** | 加入購物車率、發起結帳率、購買轉換率 | 漏斗中哪個環節在流失？ |
| **營收（Revenue）** | 營收、AOV、每筆訂單件數、每次工作階段營收 | 他們花多少錢？商品組合健康嗎？ |
| **留存（Retention）** | 回購率、購買頻率、客戶終身價值 | 他們會回來嗎？ |

### GA4 電商事件

| 事件 | 觸發時機 | 關鍵參數 |
|-------|---------|---------------|
| `view_item` | 瀏覽商品頁 | item_id, item_name, price, category |
| `add_to_cart` | 點擊加入購物車 | items array, value, currency |
| `begin_checkout` | 開始結帳 | items, value, coupon |
| `add_payment_info` | 輸入付款資訊 | payment_type |
| `purchase` | 訂單完成 | transaction_id, value, tax, shipping, items |

### 診斷框架

**階段 1：檢查流量**
- 總流量跟上一期比，是上升、下降還是持平？
- 哪些管道有變化？（自然搜尋、付費、社群、直接、推薦）
- 流量品質有在下滑嗎？（各來源的跳出率、每次工作階段頁數）

**階段 2：檢查轉換**
- 漏斗中最大的流失在哪裡？
- 比較：瀏覽 → 加入購物車 → 結帳 → 購買
- 產業基準轉換率：整體 1-3%，加入購物車 5-10%

**階段 3：檢查營收**
- AOV 趨勢：上升（追加銷售有效）還是下降（折扣在侵蝕價值）？
- 商品組合：營收是否轉向低毛利商品？
- 每次工作階段營收：主指標（流量品質 × 轉換 × AOV）

**階段 4：檢查留存**
- 各世代的回購率
- 第一次和第二次購買之間的時間
- 各獲客管道的 LTV 趨勢

## 輸出格式

```markdown
# E-Commerce Performance Report: {Store}

## Summary Dashboard
| Metric | Current | Prior Period | Change | Status |
|--------|---------|-------------|--------|--------|
| Sessions | {N} | {N} | {%} | 🟢/🟡/🔴 |
| Conversion Rate | {%} | {%} | {%} | 🟢/🟡/🔴 |
| AOV | ${X} | ${X} | {%} | 🟢/🟡/🔴 |
| Revenue | ${X} | ${X} | {%} | 🟢/🟡/🔴 |

## Funnel Analysis
| Stage | Volume | Rate | Drop-off | Benchmark |
|-------|--------|------|----------|-----------|
| Sessions | {N} | 100% | — | — |
| Product Views | {N} | {%} | {%} | — |
| Add to Cart | {N} | {%} | {%} | 5-10% |
| Checkout | {N} | {%} | {%} | 40-60% of ATC |
| Purchase | {N} | {%} | {%} | 1-3% overall |

## Diagnosis
- Primary issue: {funnel stage} — {specific problem}
- Root cause: {analysis}

## Recommendations
1. {action targeting the diagnosed stage}
```

## 常見陷阱

- **不看流量品質，轉換率就沒有意義**：email（高意圖）轉換率 5%、展示型廣告（低意圖）轉換率 0.5%，兩者都算正常。不要跨管道比較。
- **GA4 的 sessions ≠ Universal Analytics 的 sessions**：GA4 採用事件導向模型，工作階段逾時和歸因規則都不一樣。遷移期間預期會有 5-15% 的差異。
- **手機的轉換率永遠比較低**：手機 1-2%、桌機 3-5% 是常態。不要混成一個數字，要分開分析。
- **季節性很重要**：要跟去年同期比，不要只看月對月。電商有很強的季節模式（雙 11、聖誕節、農曆新年）。
- **營收 ≠ 利潤**：靠大力折扣換來的 20% 營收成長，可能反而降低利潤。追蹤營收時要連毛利一起看。

## 參考資料

- GA4 設定指南，見 `references/ga4-setup.md`
- 各產業的電商基準資料，見 `references/ecom-benchmarks.md`
