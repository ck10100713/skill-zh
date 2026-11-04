---
name: "ecom-rfm-analysis"
description: "用交易資料做 RFM（Recency、Frequency、Monetary）客戶分群。當使用者需要依購買行為分群、找出高價值買家、設計留存活動，或依客戶價值排定行銷預算的優先順序時使用。就算使用者只說「我們最好的客戶是誰」、「哪些客戶有流失風險」或「行銷該怎麼鎖定對象」也要用。"
metadata:
  category: "WP-01 電商"
  tags: ["e-commerce", "rfm", "segmentation", "customer-analytics"]
---

# RFM 分析

## 概述

RFM 依三個行為面向替客戶分群：Recency（最近一次購買是什麼時候）、Frequency（多常購買）、Monetary（花多少錢）。它把原始交易資料轉成可以行動的客群，用來做精準行銷。

## 框架

```
IRON LAW: RFM Uses ACTUAL Behavior, Not Demographics

RFM is behavioral segmentation — it classifies by what customers DO,
not who they ARE. A 25-year-old and a 65-year-old in the same RFM segment
should receive the same treatment. Never mix RFM with demographic
assumptions.
```

### 三個面向

| 面向 | 衡量什麼 | 如何計算 |
|-----------|-----------------|-----------------|
| **Recency（R）** | 距離上次購買的天數 | 今天 - 最後一次購買日期 |
| **Frequency（F）** | 期間內的購買次數 | 不重複交易的筆數 |
| **Monetary（M）** | 期間內的總消費 | 交易金額加總 |

### 評分方法（五等分）

1. 每個面向都把所有客戶排名，切成 5 個大小相等的組（五等分）
2. 分數從 5（最好）到 1（最差）：R=5 代表最近買過，F=5 代表買最頻繁，M=5 代表花最多
3. 組合成 3 位數的 RFM 分數（例如 R5-F4-M5 = 最近買過、很頻繁、高價值）

**注意**：Recency 是天數「越少」分數「越高」（越近期越好）。

### 主要客群

| 客群 | RFM 模式 | 說明 | 策略 |
|---------|------------|-------------|----------|
| **冠軍客戶（Champions）** | R5, F5, M5 | 最好的客戶，最近買、買得多、高價值 | 回饋、忠誠計畫、搶先體驗 |
| **忠誠客戶（Loyal）** | R4-5, F4-5, M3-5 | 穩定購買的客戶 | 追加銷售、交叉銷售、推薦計畫 |
| **潛力忠誠客戶（Potential Loyalists）** | R4-5, F2-3, M2-3 | 最近買過、頻率中等 | 培養以提高頻率 |
| **有流失風險（At Risk）** | R2-3, F3-5, M3-5 | 以前很頻繁/高價值，最近沒在買 | 喚回活動、專屬優惠 |
| **休眠客戶（Hibernating）** | R1-2, F1-2, M1-2 | 沉寂很久、價值低 | 低成本重新啟動，或放手 |
| **新客戶（New Customers）** | R5, F1, M1-2 | 剛完成第一次購買 | 新客引導、二次購買誘因 |

### 實作步驟

**階段 1：資料準備**
- 必要欄位：客戶 ID、交易日期、交易金額
- 清理：移除退款、測試訂單、內部訂單
- 設定分析視窗（通常 12-24 個月）

**階段 2：計算 RFM 分數**
- 計算每位客戶的 R、F、M
- 為每個面向指派五等分分數（1-5）
- 組合成客群

**階段 3：分群並行動**
- 把每位客戶對應到有名稱的客群（Champions、At Risk 等）
- 針對每個客群設計行動
- 衡量成果：被鎖定的客戶行為有不一樣嗎？

## 輸出格式

```markdown
# RFM Analysis: {Business}

## Data Summary
- Customers analyzed: {N}
- Analysis window: {start} to {end}
- Transactions: {N}

## Segment Distribution
| Segment | Count | % | Avg R (days) | Avg F | Avg M |
|---------|-------|---|-------------|-------|-------|
| Champions | {N} | {%} | {days} | {count} | ${X} |
| At Risk | {N} | {%} | ... | ... | ... |
| ... | ... | ... | ... | ... | ... |

## Key Findings
- Top 20% customers contribute {X%} of revenue
- {N} customers at risk of churning (were high-value, now dormant)
- {N} new customers need second-purchase nurturing

## Recommended Actions
| Segment | Action | Channel | Expected Impact |
|---------|--------|---------|----------------|
| Champions | {loyalty reward} | {email/app} | Increase AOV by X% |
| At Risk | {win-back offer} | {email/SMS} | Recover X% of dormant revenue |
```

## 常見陷阱

- **RFM 是回頭看的**：它告訴你客戶「做過」什麼，不是他們「會」做什麼。要搭配預測模型（CLV 預測）才有前瞻的洞察。
- **等量五等分不一定合理**：如果 80% 的客戶只買過一次，第 1 到 4 等分全都是「單次購買者」。可以考慮依業務脈絡自訂切分點。
- **訂閱制的 Monetary 可能有誤導性**：如果每個人付的訂閱費都一樣，M 面向就沒有提供任何資訊。把它拿掉，只用 RF。
- **B2B 和 B2C 的頻率不同**：每季採購一次的 B2B 客戶算「頻繁」；每季購買一次的 B2C 客戶可能是「有流失風險」。要依業務脈絡校準。
- **不要對 At Risk 客戶過度轟炸**：對沉寂的客戶狂發 email 可能讓退訂增加。一場精心設計的喚回活動，比每週發 email 好。

## Scripts

| Script | 說明 | 用法 |
|--------|-------------|-------|
| `scripts/rfm_score.py` | 對客戶的 R/F/M 評分並指派客群標籤 | `python scripts/rfm_score.py --help` |

執行 `python scripts/rfm_score.py --verify` 可跑內建的合理性測試。

## 參考資料

- Python/SQL 的實作程式碼，見 `references/rfm-implementation.md`
- 延伸 RFM 的 CLV 預測，見 `references/clv-prediction.md`
