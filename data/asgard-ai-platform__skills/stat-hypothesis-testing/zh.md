---
name: "stat-hypothesis-testing"
description: "進行統計假設檢定，包括虛無/對立假設的擬定、p 值、第一型/第二型錯誤，以及檢定統計量的選擇。當使用者需要判斷結果是否具統計顯著性、挑選合適的統計檢定、正確解讀 p 值或評估研究發現時使用這個 skill，就算他們說的是「這個結果顯著嗎」、「我該用哪種統計檢定」或「這個 p 值是什麼意思」也一樣。"
metadata:
  category: "WP-21 設計/資訊/傳播/公衛"
  tags: ["statistics", "hypothesis-testing", "p-value", "inference"]
---

# 假設檢定

## 框架

```
IRON LAW: Statistical Significance ≠ Practical Significance
（鐵律：統計顯著 ≠ 實務顯著）

p 值 < 0.05 的意思是：在虛無假設成立的前提下，這個結果不太可能出現。
它「不代表」這個結果重要、很大，或有實務意義。
只要樣本夠大，0.1% 的轉換率差異也會變成「統計顯著」，
但實務上一點價值都沒有。

報告 p 值時，一定要同時報告效果量（effect size）。
```

```
IRON LAW: State Hypotheses BEFORE Looking at Data
（鐵律：先定假設，再看資料）

H₀（虛無假設）和 H₁（對立假設）必須在分析資料之前就定義好。
看完資料才選假設 = p-hacking = 學術造假。
「我們發現一個有趣的模式，來用同一批資料測測看」是無效的做法。
```

### 核心概念

| 概念 | 定義 |
|---------|-----------|
| **H₀（虛無假設）** | 預設假設：沒有效果、沒有差異 |
| **H₁（對立假設）** | 你想證明的：確實有效果/差異 |
| **p-value** | 假設 H₀ 為真，看到這個結果（或更極端結果）的機率 |
| **α（顯著水準）** | 拒絕 H₀ 的門檻（通常是 0.05） |
| **第一型錯誤（α）** | H₀ 其實為真卻拒絕它（偽陽性） |
| **第二型錯誤（β）** | H₁ 為真卻沒能拒絕 H₀（偽陰性） |
| **檢定力 Power（1-β）** | 偵測到真實效果的機率（目標：≥ 0.8） |
| **效果量 Effect size** | 差異的大小（Cohen's d、odds ratio、R²） |

### 檢定選擇指南

| 資料類型 | 組別 | 檢定 |
|-----------|--------|------|
| 連續、常態、2 組 | 獨立 | 獨立樣本 t 檢定 |
| 連續、常態、2 組 | 成對/前後測 | 成對樣本 t 檢定 |
| 連續、常態、3 組以上 | 獨立 | 單因子 ANOVA |
| 連續、非常態 | 2 組 | Mann-Whitney U |
| 類別 | 2 組以上 | 卡方檢定 |
| 連續、看關聯性 | 2 個變數 | Pearson 相關（常態）/ Spearman（非常態） |
| 二元結果 | 預測變數 | Logistic regression |

### 檢定流程

1. **陳述假設**：H₀ 和 H₁，要帶具體參數
2. **選檢定**：依資料類型、分布和組別來選（用上面的指南）
3. **設 α**：通常 0.05（不一樣的話要說明理由）
4. **計算**：跑檢定，取得檢定統計量和 p 值
5. **決策**：p < α → 拒絕 H₀；p ≥ α → 無法拒絕 H₀
6. **報告**：效果量 + 信賴區間 + p 值（不要只寫「顯著」）

## 輸出格式

```markdown
# Hypothesis Test: {Research Question}

## Hypotheses
- H₀: {null — no effect/difference}
- H₁: {alternative — there IS an effect/difference}
- α = {0.05 or other}

## Test Selection
- Test: {name}
- Rationale: {why this test fits the data}
- Assumptions checked: {normality, independence, equal variance}

## Results
- Test statistic: {value}
- p-value: {value}
- Effect size: {value and interpretation}
- 95% CI: [{lower}, {upper}]

## Decision
{Reject / Fail to reject H₀}

## Interpretation
{What this means in practical terms, with effect size context}
```

## 常見陷阱

- **「無法拒絕 H₀」≠「H₀ 為真」**：沒有證據不等於證據不存在。你可能只是檢定力不夠，偵測不到真實的效果。
- **多重比較會膨脹第一型錯誤**：用 α=0.05 測 20 個假設，光靠運氣就預期會有 1 個偽陽性。要套用 Bonferroni 或 FDR 校正。
- **檢定前先檢查假設條件**：t 檢定假設常態和變異數相等，違反假設會讓結果失效。假設不成立時，改用無母數的替代方法。
- **樣本數決定檢定力**：樣本太小會漏掉真實效果（第二型錯誤）。收資料「之前」就要先算出所需樣本數。
- **p 值「不是」H₀ 為真的機率**：它是在 H₀ 成立下出現這份資料的機率，兩者本質上不同（基率謬誤）。

## 參考資料

- 樣本數計算，見 `references/sample-size.md`
- 無母數檢定替代方案，見 `references/nonparametric-tests.md`
