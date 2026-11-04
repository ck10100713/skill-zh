---
name: "fin-modeling"
description: "建立三大報表財務模型（損益表、資產負債表、現金流量表），包含營收預測、假設管理與情境分析。當使用者需要財務預測、建立募資用的模型、為商業計畫書製作財務預估，或評估併購標的時使用。就算使用者只說「建一個財務模型」、「預測我們的營收」、「明年會賺多少錢」或「幫這個收購案建模」也要用。"
metadata:
  category: "WP-08 財務投資"
  tags: ["finance", "financial-modeling", "forecasting", "three-statement"]
---

# 三大報表財務建模

## 框架

```
IRON LAW: The Three Statements Must Balance

Assets = Liabilities + Equity (Balance Sheet identity)
Net Income flows from IS to BS (retained earnings)
Cash flow bridges IS and BS through working capital and capex

If your model doesn't balance, there's an error. Check the cash line on
the BS against the ending cash on the CF statement. They MUST match.
```

### 模型架構

```
[Assumptions Page] → drives everything
    ↓
[Income Statement] → Revenue, costs, taxes → Net Income
    ↓
[Balance Sheet] → Assets, liabilities, equity → must balance
    ↓
[Cash Flow Statement] → Start cash + Operating + Investing + Financing = End cash
    ↓
[Outputs: DCF, Returns, Scenarios]
```

### 營收預測方法

| 方法 | 做法 | 最適合 |
|--------|-----|----------|
| **由上而下（Top-down）** | 市場規模 × 市占率 × 價格 | 新市場、受總體因素驅動 |
| **由下而上（Bottom-up）** | 數量 × 價格，或客戶數 × ARPU | 成熟產品、SaaS |
| **Run-rate** | 目前的月營收 × 12，再依成長調整 | 近期的預測 |
| **世代式（Cohort-based）** | 新世代營收 + 既有世代的留存 | 訂閱制業務 |

### 要記錄的關鍵假設

| 類別 | 假設 |
|----------|------------|
| **營收** | 成長率、定價、數量、流失率（訂閱制） |
| **COGS** | 毛利率走向、投入成本的通膨 |
| **OpEx** | 人力計畫、薪資通膨、行銷費用占營收的比例 |
| **營運資金** | DSO（應收帳款天數）、DPO（應付帳款天數）、DIO（庫存天數） |
| **CapEx** | 資本支出占營收的比例，或具體專案 |
| **稅** | 有效稅率、虧損扣抵 |
| **融資** | 債務時程、利率、增資 |

### 建構步驟

**階段 1：假設**
1. 把所有假設記錄在專門的一頁
2. 顏色標示：藍色 = 輸入、黑色 = 公式、綠色 = 從其他工作表連結
3. 每個假設都必須有來源或理由

**階段 2：損益表**
4. 從假設建立營收項目
5. COGS 和毛利
6. 依類別列出營業費用
7. EBITDA、折舊、EBIT
8. 利息、稅、淨利

**階段 3：資產負債表**
9. 營運資金項目由損益表的驅動因子推算（DSO × 營收/365 等）
10. 固定資產：前期 + 資本支出 - 折舊
11. 債務時程：前期 + 新借款 - 還款
12. 權益：前期 + 淨利 - 股利 + 增資
13. **檢查：資產 = 負債 + 權益**

**階段 4：現金流量**
14. 從淨利開始
15. 加回非現金項目（折舊、攤銷）
16. 營運資金的變動（由資產負債表的期間對期間變化得出）
17. 資本支出（投資）
18. 債務與權益的變動（融資）
19. **檢查：期末現金 = 資產負債表的現金項目**

**階段 5：情境**
20. 基本情境（最可能的假設）
21. 樂觀情境（較高的成長、較好的毛利率）
22. 悲觀情境（較低的成長、毛利率承壓）

## 輸出格式

```markdown
# Financial Model: {Company} — {Projection Period}

## Key Assumptions
| Assumption | Y1 | Y2 | Y3 | Y4 | Y5 | Source |
|-----------|-----|-----|-----|-----|-----|--------|
| Revenue growth | {%} | {%} | {%} | {%} | {%} | {basis} |
| Gross margin | {%} | ... | ... | ... | ... | ... |
| OpEx growth | {%} | ... | ... | ... | ... | ... |

## Projected Income Statement
| | Y1 | Y2 | Y3 | Y4 | Y5 |
|---|-----|-----|-----|-----|-----|
| Revenue | ${X} | ... | ... | ... | ... |
| Gross Profit | ${X} | ... | ... | ... | ... |
| EBITDA | ${X} | ... | ... | ... | ... |
| Net Income | ${X} | ... | ... | ... | ... |

## Scenario Comparison
| Metric (Y5) | Bear | Base | Bull |
|-------------|------|------|------|
| Revenue | ${X} | ${X} | ${X} |
| Net Income | ${X} | ${X} | ${X} |
| FCF | ${X} | ${X} | ${X} |

## Balance Check
- BS balances: ✓/✗
- CF ending cash = BS cash: ✓/✗
```

## 常見陷阱

- **營收是最敏感的假設**：成長率差 2%，在 5 年內複利下來差距非常大。永遠要呈現一個範圍，不要只給單一點估計。
- **營運資金常被遺忘**：高速成長的公司會在營運資金上消耗現金（建立庫存、放寬賒帳）。如果沒有為營運資金建模，一家有獲利的公司也可能現金燒光。
- **利息造成循環參照**：利息費用取決於債務餘額，債務餘額取決於現金（可能需要更多債務）。用迭代計算或前期的債務餘額來打破循環。
- **粒度要符合確定性**：第 1 年用月、第 2 年用季、第 3-5 年用年。第 5 年做詳細的月預測是假精準。
- **假設頁是最重要的一頁**：沒有人應該需要翻公式才能了解是什麼在驅動你的模型。所有假設都要可見、有記錄，而且能在同一個地方修改。

## 參考資料

- 建立在三大報表模型之上的 DCF 估值，見 biz-dcf skill
- 試算表的最佳實務，見 `references/modeling-best-practices.md`
