---
name: "data-cohort-analysis"
description: "做世代分析（cohort analysis），追蹤使用者行為隨時間的變化、建立留存矩陣並比較各世代表現。當使用者需要衡量留存、了解使用者獲取後行為如何變化、比較產品版本對參與度的影響，或預測 LTV 時使用。就算使用者只說「我們的留存率多少」、「新使用者的行為跟以前不一樣嗎」、「做一張留存表」或「客戶會待多久」也要用。"
metadata:
  category: "WP-04 數據分析"
  tags: ["data-analysis", "cohort", "retention", "product-analytics"]
---

# 世代分析（Cohort Analysis）

## 框架

```
IRON LAW: Aggregate Metrics Hide Cohort Differences

A 70% monthly retention rate OVERALL can mask that January cohort retains
at 85% while June cohort retains at 50%. Aggregate metrics blend improving
and deteriorating cohorts together, hiding both problems and progress.
ALWAYS analyze by cohort before drawing conclusions.
```

### 核心概念

**世代（Cohort）**：在特定時間段內具有共同特徵的一群使用者。最常見的是獲取世代（依註冊月份分組）。

**留存矩陣（Retention Matrix）**：列 = 世代（依註冊月份），欄 = 註冊後的時間區間（第 0、1、2 個月...）。儲存格 = 該世代仍然活躍的百分比。

```
           Month 0  Month 1  Month 2  Month 3
Jan cohort   100%     65%     48%      40%
Feb cohort   100%     60%     42%      35%
Mar cohort   100%     70%     55%      48%  ← Improvement!
```

### 留存類型

| 類型 | 定義 | 使用情境 |
|------|-----------|----------|
| **N 日（N-day）** | 剛好在第 N 天活躍的比例 | 遊戲、每天使用的 App |
| **N 日有界（N-day bounded）** | 前 N 天內有活躍的比例 | 一般產品使用 |
| **週/月** | 第 N 週/月活躍的比例 | SaaS、訂閱制 |
| **無界（Unbounded）** | 第 N 天之後曾經回來過的比例 | 低頻率產品 |

### 分析步驟

**階段 1：定義世代和活躍行為**
- 世代定義：註冊日期、首次購買日期，或其他里程碑
- 活躍定義：登入、購買、特定動作，必須符合產品的核心價值
- 時間粒度：每日（每天使用的產品）、每週或每月

**階段 2：建立留存矩陣**
- 把使用者分進各世代
- 對每個世代，計算每個時間區間的留存率
- 畫成熱圖（顏色越深 = 留存越高）

**階段 3：找出模式**
- **留存曲線形狀**：會趨平（好，有穩定的核心使用者）還是持續下滑（不好，最後大家都流失）？
- **世代比較**：新世代的留存比舊世代好還是差？
- **斷崖式流失**：有沒有哪個時期留存率大幅下降？（例如第 1 天 → 第 7 天掉 50%）

**階段 4：連結到行動**
- 變好/變差的世代之間改變了什麼？（產品更新、行銷管道轉變、onboarding 調整）
- 能不能用 A/B 測試或事件分析把原因隔離出來？

**階段 5：LTV 預測**
- 用世代留存曲線預測各世代未來的營收
- LTV = Σ (retention_month_n × ARPU_month_n)，對所有未來月份加總

## 輸出格式

```markdown
# Cohort Analysis: {Product}

## Cohort Definition
- Cohort: {signup month / first purchase}
- Activity: {what counts as "active"}
- Period: {daily / weekly / monthly}

## Retention Matrix
| Cohort | M0 | M1 | M2 | M3 | M4 | M5 | M6 |
|--------|-----|-----|-----|-----|-----|-----|-----|
| {month} | 100% | {%} | {%} | {%} | {%} | {%} | {%} |

## Key Findings
1. {retention curve shape}
2. {cohort trend — improving or deteriorating}
3. {critical drop-off point}

## Cohort Comparison
| Metric | Oldest Cohort | Newest Cohort | Delta |
|--------|-------------|-------------|-------|
| M1 retention | {%} | {%} | {±pp} |
| M3 retention | {%} | {%} | {±pp} |
| Projected LTV | ${X} | ${X} | {%} |

## Recommendations
1. {action to improve retention at critical drop-off point}
```

## 常見陷阱

- **「活躍」要定義清楚**：登入 ≠ 傳遞價值。使用者有登入但沒完成核心動作（購買、傳訊息、建立文件），就不該算「留存」。
- **世代人數很重要**：10 個人的世代、留存 50%，沒有意義（只有 5 人）。要確保世代的人數在統計上有意義。
- **總體數字的倖存者偏誤**：「平均留存在改善」可能只是新使用者變多（他們永遠在 M0 = 100%），稀釋了分母。
- **季節性世代的行為不同**：12 月世代（節慶購物者）的留存通常比 3 月世代（自然發現）差。要跟去年同季的世代比。
- **留存 ≠ 參與深度**：一個每月回來一次但用 5 小時的使用者，跟一個每天回來但只用 30 秒的使用者，留存相同，參與度卻差很多。要再加上活動深度指標。

## 參考資料

- SQL 留存查詢範本，見 `references/retention-sql.md`
- 用世代資料預測 LTV，見 `references/cohort-ltv.md`
