---
name: "fin-earnings-summary"
description: "摘要並分析法說會，包含財務亮點、管理層談話、財測（guidance）與分析師 Q&A 的重點。當使用者需要消化法說會逐字稿、擷取關鍵財務數據與前瞻財測、比較實際結果與市場共識預期，或準備投資人會議時使用。就算使用者只說「幫我摘要這場法說會」、「管理層對下一季怎麼說」、「有超出預期嗎」或「法說會的重點」也要用。"
metadata:
  category: "WP-08 財務投資"
  tags: ["finance", "earnings", "investor-relations", "analysis"]
---

# 法說會摘要與分析

## 框架

```
IRON LAW: Separate Facts from Spin

Management presentations emphasize positives and downplay negatives.
Your job is to extract: (1) hard numbers, (2) forward guidance with
specificity level, and (3) what management DIDN'T say (notable omissions).

"Strong momentum" without numbers is spin.
"Revenue grew 15% to NT$2.3B" is a fact.
```

### 法說會結構

| 段落 | 時長 | 要擷取什麼 |
|---------|----------|----------------|
| **準備好的談話（Prepared Remarks）** | 15-20 分鐘 | 營收、EPS、毛利率、關鍵指標，並比較實際 vs 財測 vs 市場共識 |
| **管理層評論** | 10-15 分鐘 | 前瞻財測、策略性計畫、市場展望 |
| **Q&A** | 20-30 分鐘 | 分析師在擔心什麼（從他們的問題可以看出來）、管理層的坦率程度 |

### 要擷取的關鍵數據點

**財務亮點（對比市場共識）**
| 指標 | 實際 | 共識 | 超出/不及 | 年增 |
|--------|--------|----------|-----------|-----------|
| 營收 | ${X} | ${X} | 超出/不及 {%} | {%} |
| EPS | ${X} | ${X} | 超出/不及 {%} | {%} |
| 毛利率 | {%} | {%} | ±{pp} | ±{pp} |
| 營業利益率 | {%} | {%} | ±{pp} | ±{pp} |

**前瞻財測**
| 指標 | 財測 | 先前財測 | 變化 | 具體程度 |
|--------|---------|---------------|--------|------------|
| 下一季營收 | ${X}-${X} | ${X}-${X} | 上調/維持/下調 | 具體/籠統 |
| 全年 EPS | ${X}-${X} | ... | ... | ... |

**質化訊號**
- 新產品/新計畫的宣布
- 市場/需求的評論（轉強、穩定、轉弱）
- 競爭地位的更新
- 資本配置（庫藏股、股利、併購、資本支出）
- 語氣：有信心、謹慎、防禦、閃躲

### 分析步驟

**階段 1：擷取數字**
- 營收、EPS、毛利率：實際 vs 共識 vs 先前財測
- 每個項目是超出還是不及

**階段 2：評估財測**
- 財測是上調、維持還是下調？
- 財測有多具體？（區間 vs 籠統）
- 隱含的假設（成長率、毛利率走向）

**階段 3：讀 Q&A**
- 分析師在問什麼？（反映市場的擔憂）
- 管理層在哪裡迴避或給模糊的答案？（警訊）
- 準備好的談話中沒有的新資訊

**階段 4：對照市場反應**
- 法說後的股價變動
- 市場反應跟數字吻合嗎？（有時候超出預期卻被賣出 = 財測令人失望）

## 輸出格式

```markdown
# Earnings Summary: {Company} — {Quarter}

## Headline
{One sentence: beat/miss + most important takeaway}

## Financial Highlights
| Metric | Actual | Consensus | vs Consensus | YoY |
|--------|--------|----------|-------------|-----|
| Revenue | ... | ... | ... | ... |
| EPS | ... | ... | ... | ... |

## Forward Guidance
| Metric | New Guidance | Prior | Change |
|--------|------------|-------|--------|
| ... | ... | ... | Raised/Maintained/Lowered |

## Management Commentary (Key Points)
1. {key point with quote}
2. {key point}

## Q&A Highlights
- **Analyst concern**: {topic} → **Management response**: {summary}
- **Notable omission**: {what wasn't addressed}

## Market Reaction
- Post-earnings move: {+/-X%}
- Interpretation: {why the market reacted this way}

## Investment Implication
{What this means for the investment thesis — bullish/neutral/bearish signal}
```

## 常見陷阱

- **超出預期也可能是「低品質」的**：靠砍成本讓 EPS 超出預期，營收卻不及，是低品質的超出。營收超出預期、毛利率又擴張，才是高品質。要區分。
- **財測比實際數字更重要**：市場價格已經反映預期。一家公司第 3 季超出預期、卻下調第 4 季財測，股價常常會下跌。要專注在前瞻的訊號。
- **台灣法說會的特殊性**：許多台灣公司（尤其是台積電、聯發科）會辦英語法說會，其他則只有中文。就算你無法即時參加，公開資訊觀測站（MOPS）也有摘要說明。
- **市場共識預估可能過時**：如果預估很久沒更新，「超出預期」可能只是門檻設太低。要確認共識最近一次修正是什麼時候。
- **一季不構成趨勢**：不要對單一季度反應過度。看 3-4 季才能分辨真正的趨勢和雜訊。

## 參考資料

- 財務報表分析，見 data-financial-analysis skill
- 台灣股票資料來源，見 tw-stock-analysis skill
