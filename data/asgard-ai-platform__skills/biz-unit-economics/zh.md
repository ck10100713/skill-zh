---
name: "biz-unit-economics"
description: "分析單位經濟（unit economics），評估單位獲利能力與商業模式的可擴展性。當使用者需要評估每筆交易、每位客戶或每個產品單位是否賺錢、評估新創可行性，或最佳化邊際貢獻時使用。就算使用者只說「我們的商業模式行得通嗎」、「每張訂單的毛利多少」或「能不能賺錢地擴張」也要用。"
metadata:
  category: "WP-15 商學院—財務"
  tags: ["finance", "unit-economics", "business-model"]
---

# 單位經濟（Unit Economics）

## 概述

單位經濟衡量的是單一單位層級的獲利能力：每位客戶、每筆交易或每個產品。如果單位經濟是負的，規模越大虧越多。單位經濟為正，是永續成長的前提。

## 框架

```
IRON LAW: If Unit Economics Are Negative, Growth = Faster Death

Scaling a business with negative unit economics means losing more money
faster. "We'll make it up in volume" only works if variable costs per unit
decrease with scale (economies of scale). If they don't, more volume = more losses.

Prove unit economics are positive BEFORE investing in growth.
```

### 各商業模式的關鍵指標

**訂閱制 / SaaS：**
| 指標 | 公式 |
|--------|---------|
| CAC | 總獲客支出 / 新客戶數 |
| LTV | ARPU × 毛利率 × (1/流失率) |
| LTV:CAC | 必須 > 3:1 |
| 回收期（Payback Period） | CAC / (月 ARPU × 毛利率) |
| 淨營收留存率（Net Revenue Retention） | (期初 MRR + 擴張 - 縮減 - 流失) / 期初 MRR |

**電商 / 平台市集：**
| 指標 | 公式 |
|--------|---------|
| AOV | 總營收 / 訂單數 |
| 每筆訂單邊際貢獻 | AOV - COGS - 運費 - 金流手續費 - 退貨 |
| 回購率 | 回頭客 / 總客戶數 |
| 完全分攤 CAC | 總行銷費用 / 新客戶數 |

**即時服務 / 外送：**
| 指標 | 公式 |
|--------|---------|
| 每趟營收 | 訂單金額 × 抽成率 |
| 每趟成本 | 司機薪酬 + 客服 + 保險 + 獎勵金 |
| 每趟貢獻 | 營收 - 每趟成本 |
| 每位司機每日訂單數 | 使用率指標 |

### 分析步驟

1. **定義單位**：一個「單位」是什麼？（客戶、訂單、趟次、座位）
2. **算每單位營收**：每個單位產生多少收入？
3. **算每單位變動成本**：每個單位要花多少？
4. **算邊際貢獻**：營收 - 變動成本
5. **疊上固定成本**：要到多少量才能攤平固定成本？（→ 損益兩平）
6. **評估可擴展性**：量放大 10 倍後，單位經濟會變好還是變差？

## 輸出格式

```markdown
# Unit Economics: {Business}

## Unit Definition
- Unit: {customer / order / trip}
- Time period: {monthly / per-transaction}

## Per-Unit Economics
| Metric | Value |
|--------|-------|
| Revenue per unit | ${X} |
| Variable cost per unit | ${X} |
| Contribution margin | ${X} ({X%}) |

## Scalability Assessment
| Volume | Unit Revenue | Unit Cost | CM | Notes |
|--------|-------------|-----------|-----|-------|
| Current ({N}) | ${X} | ${X} | {X%} | baseline |
| 3x ({N}) | ${X} | ${X} | {X%} | {economies of scale?} |
| 10x ({N}) | ${X} | ${X} | {X%} | {what changes?} |

## Verdict
{Positive/negative unit economics, scalability assessment, key lever to improve}
```

## 範例

### 正確的做法
**情境：** 一家台灣外送新創的單位經濟
- 每單營收：NT$350 × 30% 抽成 = NT$105
- 變動成本：司機薪酬 NT$65 + 金流手續費 NT$10 + 客服 NT$5 = NT$80
- **邊際貢獻：每單 NT$25（23.8%）** ✓
- 規模放大 10 倍：司機薪酬降到 NT$55（路線更優），邊際貢獻提升到 NT$35（33%）
- 結論：勉強為正，要靠規模，需要量才站得住

### 錯誤的做法
- 「每位客戶營收 NT$500，每位客戶成本 NT$200，所以每位客戶賺 NT$300」，但這漏掉了客服（NT$150）和金流處理（NT$50）。真正的毛利是 NT$100。每單位的變動成本「全部」都要算進去。

## 常見陷阱

- **「我們會達到規模經濟」**：也許。要指出「哪些」成本會隨規模下降、降多少。外送司機薪酬可能不會降，SaaS 的伺服器成本通常會降。
- **邊際貢獻 ≠ 獲利**：邊際貢獻只涵蓋變動成本。總邊際貢獻還是要夠付固定成本（見損益兩平分析）。
- **混合 vs 世代**：把所有客戶混在一起算單位經濟，會藏住一個事實：早期客戶（自然流量）可能賺錢，近期客戶（付費獲客）卻不賺錢。
- **負的單位經濟也可能是策略**：在有網路效應、搶地盤的市場（共乘、平台市集）可以暫時接受。但轉正的路徑必須講清楚。

## Scripts

| Script | 說明 | 用法 |
|--------|-------------|-------|
| `scripts/unit_economics.py` | 計算 SaaS 單位經濟（NRR、GRR、LTV、CAC 回收期、magic number、burn multiple） | `python scripts/unit_economics.py --help` |

執行 `python scripts/unit_economics.py --verify` 可跑內建的合理性測試。

## 參考資料

- CAC-LTV 深入分析，見 biz-cac-ltv skill
- 損益兩平分析，見 biz-breakeven skill
