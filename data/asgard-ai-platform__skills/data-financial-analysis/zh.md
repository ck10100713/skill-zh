---
name: "data-financial-analysis"
description: "解讀三大財務報表（損益表、資產負債表、現金流量表），評估企業體質與績效。當使用者需要讀財報、理解獲利與現金流的差異、評估公司財務狀況，或準備投資人/董事會會議時使用。就算使用者只說「幫我解釋這些財務數字」、「我們有賺錢嗎」、「幫我看這份年報」或「這些數字代表什麼」也要用。"
metadata:
  category: "WP-04 數據分析"
  tags: ["data-analysis", "financial-statements", "accounting"]
---

# 財務報表分析

## 框架

```
IRON LAW: Read All Three Statements Together

A company can be profitable (Income Statement) but cash-poor (Cash Flow Statement).
A company can have high assets (Balance Sheet) funded entirely by debt.
Reading one statement alone gives an incomplete — and potentially misleading — picture.
ALWAYS read all three and check for consistency.
```

### 三大報表

**損益表（Income Statement，損益表）**：「這段期間」有賺錢嗎？
- 營收 → 毛利 → 營業利益 → 淨利
- 重點：認列營收 ≠ 收到現金。權責發生制是在賺得時記錄營收，不是在收到款項時。

**資產負債表（Balance Sheet，資產負債表）**：「現在這一刻」我們擁有什麼、欠什麼？
- 資產 = 負債 + 股東權益
- 重點：這是某個時間點的「快照」，不是一段期間。

**現金流量表（Cash Flow Statement，現金流量表）**：現金從哪裡來、流到哪裡去？
- 營業活動（核心業務產生的現金）
- 投資活動（資本支出、併購、出售資產）
- 融資活動（債務、股權、股利）
- 重點：營業現金流最重要，它顯示核心業務是否產生現金。

### 跨報表的警訊

| 警訊 | 代表什麼 |
|----------|-------------|
| 營收成長但營業現金流下滑 | 可能有營收認列問題，或應收帳款增加 |
| 淨利為正但自由現金流為負 | 盈餘是由應計項目驅動而非現金；資本支出龐大 |
| 資產成長快過營收 | 資產使用效率不佳 |
| 債務成長快過權益 | 槓桿風險增加 |
| 存貨成長快過營收 | 可能有存貨過時、需求放緩的問題 |

### 分析步驟

1. **讀損益表**：公司有獲利嗎？在哪個層級（毛利、營業、淨利）？
2. **讀資產負債表**：資本結構如何？流動性好不好？
3. **讀現金流量表**：營業現金流是正的嗎？現金流向哪裡？
4. **交叉檢查**：營收成長 vs 現金流成長、淨利 vs 營業現金流
5. **趨勢**：關鍵指標看 3 到 5 年的趨勢
6. **基準比較**：跟同業比較

## 輸出格式

```markdown
# Financial Statement Analysis: {Company} — {Period}

## Income Statement Highlights
| Metric | Current | Prior Year | Change |
|--------|---------|-----------|--------|
| Revenue | ${X} | ${X} | {%} |
| Gross Margin | {%} | {%} | {±pp} |
| Operating Margin | {%} | {%} | {±pp} |
| Net Income | ${X} | ${X} | {%} |

## Balance Sheet Highlights
| Metric | Current | Prior Year |
|--------|---------|-----------|
| Total Assets | ${X} | ${X} |
| Total Debt | ${X} | ${X} |
| D/E Ratio | {X} | {X} |
| Current Ratio | {X} | {X} |

## Cash Flow Highlights
| Category | Amount |
|----------|--------|
| Operating CF | ${X} |
| Investing CF | ${X} |
| Financing CF | ${X} |
| Free Cash Flow | ${X} |

## Red Flags
- {any detected}

## Overall Assessment
{Financial health verdict with key rationale}
```

## 常見陷阱

- **營收 ≠ 現金**：在權責發生制下，營收是在賺得時（產品交付）記錄，不是在收到現金時。看應收帳款，就能知道還有多少營收沒收回來。
- **EBITDA 不是現金流**：EBITDA 忽略資本支出、營運資金變動和稅，而這些都是實際的現金成本。做現金分析要用自由現金流。
- **一次性項目會扭曲趨勢**：重組費用、出售資產、法律和解，會造成一次性的暴增或下跌。做趨勢分析要用「調整後」或「正常化」的數字。
- **台灣 IFRS vs 美國 GAAP**：台灣上市公司用 IFRS（TIFRSs）。部分處理方式跟美國 GAAP 不同（租賃會計、營收認列細節）。要註明適用哪套準則。

## 參考資料

- 財務比率的深入分析，見 biz-financial-ratios skill
- 杜邦 ROE 拆解，見 biz-dupont skill
