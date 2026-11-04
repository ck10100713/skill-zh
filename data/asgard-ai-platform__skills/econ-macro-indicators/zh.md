---
name: "econ-macro-indicators"
description: "解讀總體經濟指標（GDP、通膨、失業率、利率、匯率），評估經濟體質並預測趨勢。當使用者需要評估一個國家的經濟前景、了解貨幣/財政政策的影響，或把商業決策放進總體經濟環境來看時使用。就算使用者只說「經濟現在好嗎」、「升息對我們代表什麼」或「解釋一下今天的經濟數據」也要用。"
metadata:
  category: "WP-17 經濟學院"
  tags: ["economics", "macroeconomics", "economic-indicators"]
---

# 總體經濟指標

## 概述

總體經濟指標衡量整體經濟的表現。它們分成領先（預測未來）、同時（反映現況）和落後（確認過去）三類指標。了解這些指標，有助於把商業決策放進更大的經濟環境中來看。

## 框架

```
IRON LAW: Leading, Coincident, or Lagging — Know Which Type

GDP growth is LAGGING — by the time it's published, the economy has already
changed. Stock markets and PMI are LEADING — they predict future direction.
Unemployment is LAGGING — it rises after a recession starts.

Using a lagging indicator to predict the future is looking in the rearview mirror.
Match the indicator type to your analysis purpose.
```

### 關鍵指標

**GDP（國內生產毛額）**
- 類型：落後
- 衡量：整體經濟產出
- 關鍵訊號：連續 2 季負成長 = 技術性衰退
- 台灣：由主計總處每季公布

**通膨（CPI/PPI）**
- 類型：同時
- CPI = 消費者物價，PPI = 生產者物價（CPI 的領先指標）
- 目標：大多數央行的目標約 2%
- 台灣：CPI 由主計總處每月公布

**失業率**
- 類型：落後
- 自然失業率因國家而異（台灣約 3.5-4%）
- 要注意 U-3（官方數字）與包含不完全就業在內的更廣義指標

**利率**
- 央行政策利率（台灣央行重貼現率）
- 升息 → 減緩經濟、對抗通膨、使貨幣走強
- 降息 → 刺激經濟、有通膨風險、使貨幣走弱

**匯率**
- 以台灣為中心的分析，看 TWD/USD、TWD/JPY、TWD/CNY
- 貶值 → 出口變便宜，進口變貴
- 要看實質有效匯率（REER）來判斷貿易競爭力

**PMI（採購經理人指數）**
- 類型：領先
- 高於 50 = 擴張，低於 50 = 收縮
- 每月公布，比 GDP 資料更早取得

### 指標之間的關係

```
Central bank raises rates
  → Borrowing costs rise
    → Consumer spending slows + Business investment slows
      → GDP growth slows
        → Unemployment rises (with lag)
          → Inflation falls (the goal)
```

### 分析步驟

1. **蒐集** 5-6 個關鍵指標的**最新資料**
2. 把每個指標**分類**為領先/同時/落後
3. **找出趨勢**（改善、穩定、惡化）
4. **檢查背離**（領先指標跟落後指標的方向不同 = 轉折點）
5. 針對特定的企業/產業情境**評估意涵**

## 輸出格式

```markdown
# Macroeconomic Assessment: {Country/Region}

## Indicator Dashboard
| Indicator | Current | Previous | Trend | Type |
|-----------|---------|----------|-------|------|
| GDP Growth | X% | X% | ↑/↓/→ | Lagging |
| CPI Inflation | X% | X% | ↑/↓/→ | Coincident |
| Unemployment | X% | X% | ↑/↓/→ | Lagging |
| Policy Rate | X% | X% | ↑/↓/→ | — |
| PMI | XX | XX | ↑/↓/→ | Leading |
| Exchange Rate | X.XX | X.XX | ↑/↓/→ | — |

## Economic Phase
{Expansion / Peak / Contraction / Trough}

## Key Signals
- Leading indicators suggest: {direction}
- Divergence: {if any — e.g., PMI falling while GDP still positive = slowdown ahead}

## Business Implications
- For {industry}: {specific impact}
```

## 範例

### 正確的做法
**情境：** 2025 年第 4 季的台灣總體經濟評估
| 指標 | 數值 | 訊號 |
|-----------|-------|--------|
| GDP 成長 | 年增 3.2% | 穩健，但從 4.1% 減速 |
| CPI | 2.1% | 接近目標、穩定 |
| 失業率 | 3.6% | 接近充分就業 |
| 政策利率 | 2.0% | 連續 3 季維持不變 |
| PMI | 48.5 | 低於 50，**預示放緩的領先指標** |

診斷：GDP 看起來健康（落後），但 PMI 預示接下來會收縮。經濟很可能處於或接近**高峰**階段 ✓

### 錯誤的做法
- 「上一季 GDP 成長 3.2%，所以下一季經濟也會成長」→ GDP 是落後指標。PMI 48.5 顯示情況並非如此。違反 Iron Law：用落後指標預測未來。

## 常見陷阱

- **整體 vs 核心通膨**：整體 CPI 包含波動大的食品和能源，核心 CPI 則排除它們。央行做政策決定時看的是核心。
- **實質 vs 名目**：一定要註明。「GDP 成長 5%」是名目還是實質？實質 GDP 會扣掉通膨，顯示真正的成長。
- **季節調整**：失業率、零售銷售和許多指標都做過季節調整。要用調整後跟調整後比，絕對不要拿調整後的跟原始值比。
- **台灣特有**：台灣經濟高度依賴出口。台積電的營收指引，可以說是比一般 PMI 更好的台灣領先指標。
- **資料修正**：GDP 的初估值會被修正 2-3 次。不要對第一次公布的數字反應過度。

## 參考資料

- 景氣循環理論，見 econ-business-cycle skill
- 台灣專屬的經濟資料來源，見 `references/taiwan-data-sources.md`
