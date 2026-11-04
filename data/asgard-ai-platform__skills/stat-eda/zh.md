---
name: "stat-eda"
description: "用描述統計、視覺化和資料品質檢查進行探索式資料分析（EDA）。使用者手上有一份資料集，需要了解它的結構、找出模式、偵測異常，或為進一步的分析準備資料時使用，就算他們說的是「這份資料長什麼樣子」、「找出有趣的模式」、「清理這份資料」或「摘要這份資料集」也一樣。"
metadata:
  category: "WP-21 設計/資訊/傳播/公衛"
  tags: ["data-analysis", "eda", "statistics", "visualization"]
---

# 探索式資料分析（EDA）

## 框架

```
IRON LAW: Perform EDA Only AFTER Train/Test Split — Or You Leak the Future

Agents know "do EDA first." But they almost always do EDA on the FULL
dataset before splitting. This is information leakage: you've seen the
test set's distributions, outliers, and correlations, and your subsequent
modeling choices (feature scaling, outlier treatment, imputation strategy)
are now informed by data the model shouldn't see. Split first, then EDA
only on the training set. Apply the same transformations to the test set
without re-examining it.

Exception: data quality checks (nulls, dtypes, duplicates) CAN run on
the full dataset since they don't inform model hyperparameters.
```

### EDA 工作流程

標準的五階段流程（結構 → 品質 → 單變量 → 雙變量 → 發現摘要）。假設 agent 已經知道這些步驟。重點放在下面那些不明顯的陷阱。

**多數 EDA 指南漏掉的關鍵補充：**

1. **先切分，再探索**（見上面的鐵律）
2. **缺失資料的模式比數量更重要**：MCAR 可以放心插補；MNAR（例如高收入的受訪者會跳過收入題）需要領域建模，不能用平均值填補
3. **辛普森悖論檢查**：如果某個趨勢在整體成立、但在子群組內反轉，整體趨勢就是誤導的。在報告任何雙變量發現之前，一定要先依最明顯的干擾因子分層
4. **特徵中的資料洩漏**：一個和目標完美相關的特徵，通常是從目標「衍生」出來的（例如用「refund_amount」預測流失，它是結果，不是原因）。凡是 r > 0.95 的特徵，都要標記出來做因果審查

視覺化的選擇指南請看 [`references/missing-data.md`](references/missing-data.md)。

## 輸出格式

```markdown
# EDA Report: {Dataset Name}

## Dataset Overview
- Rows: {N}, Columns: {N}
- Date range: {if applicable}
- Key columns: {description}

## Data Quality
| Issue | Columns Affected | Count/% | Action |
|-------|-----------------|---------|--------|
| Missing values | {cols} | {N / %} | {drop / impute / investigate} |
| Outliers | {cols} | {N} | {cap / remove / keep} |
| Duplicates | — | {N} | {remove} |

## Key Statistics
| Variable | Mean | Median | Std | Min | Max | Distribution |
|----------|------|--------|-----|-----|-----|-------------|
| {var} | ... | ... | ... | ... | ... | {normal/skewed/bimodal} |

## Key Findings
1. {insight with supporting data}
2. {insight}
3. {insight}

## Recommendations
- {next analysis step or data issue to resolve}
```

## 注意事項

- **相關 ≠ 因果**：EDA 找到的是關聯。要確立因果，需要對照實驗或因果推論的方法。
- **離群值可能是資料錯誤，也可能是真正的訊號**：不要自動移除，要去調查。一筆 $1M 的交易金額，可能是打錯字，也可能是你最大的客戶。
- **缺失資料有意義**：某一欄缺的資料，可能跟另一欄的值有關。「收入缺失」可能代表「失業」，不是隨機的。要檢查模式。
- **視覺化會說謊**：被截斷的 Y 軸、挑選過的時間範圍和誤導的尺度，都可能扭曲洞察。一定要使用適當的尺度並註明限制。

## 參考資料

- 缺失資料處理策略請看 `references/missing-data.md`
