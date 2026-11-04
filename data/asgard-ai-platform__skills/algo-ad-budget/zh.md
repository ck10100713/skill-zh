---
name: "algo-ad-budget"
description: "用邊際報酬分析，最佳化各廣告活動之間的預算分配。當使用者需要把預算分給多個廣告活動、最佳化花費節奏，或在預算限制下讓整體 ROAS 最大時使用，即使他們說的是『how to split my ad budget』『campaign budget optimization』或『diminishing returns on ad spend』。"
metadata:
  category: "WP-37 廣告演算法"
  tags: ["advertising", "budget-optimization", "allocation", "marginal-returns"]
---

# 廣告預算分配最佳化

## 概述

預算分配是把一筆廣告總預算分給各個廣告活動，讓整體報酬最大。用的是邊際報酬相等原則：一路分配到所有廣告活動的邊際 CPA（或邊際 ROAS）都相等為止。同時處理報酬遞減和預算限制。

## 何時使用

**觸發條件：**
- 把固定預算分給多個廣告活動或管道
- 找出報酬遞減點，以及每個廣告活動的最佳花費水準
- 成效變動後重新平衡預算

**不該使用的情況：**
- 最佳化單一廣告活動內的出價時（用出價策略）
- 只有一個廣告活動時（沒有東西可以分配）

## 演算法

```
IRON LAW: Equal Marginal Returns Principle
Optimal allocation makes the MARGINAL return of the last dollar
equal across ALL campaigns. If Campaign A's marginal CPA is $5
and Campaign B's is $15, shift budget from B to A until they equalize.
Total budget constraint: Σ budget_i = total_budget.
```

### 階段 1：輸入驗證
每個廣告活動要收集：歷史花費、轉換數、多個花費水準下的營收。每個廣告活動至少要有 3 個資料點，才能擬合反應曲線。
**關卡：** 歷史資料足以估計反應曲線。

### 階段 2：核心演算法
1. 為每個廣告活動擬合反應曲線：conversions = f(spend)。常見模型：對數曲線、冪函數曲線、S 曲線
2. 計算邊際報酬曲線：每個廣告活動的 f'(spend)
3. 分配：用 Lagrangian 最佳化或迭代式貪婪法，把下一塊錢分給邊際報酬最高的廣告活動
4. 套用限制：最低花費下限、最高上限、各管道的專屬規則

### 階段 3：驗證
檢查：分配總額 = 總預算、沒有廣告活動低於下限或超過上限、邊界處的邊際報酬大致相等。
**關卡：** 分配加總等於預算，限制條件全部滿足。

### 階段 4：輸出
回傳分配表，附上預期成效推估。

## 輸出格式

```json
{
  "allocation": [{"campaign": "Search-Brand", "budget": 50000, "expected_conversions": 200, "expected_cpa": 250}],
  "total": {"budget": 200000, "expected_conversions": 650, "blended_cpa": 308},
  "metadata": {"optimization_method": "lagrangian", "response_model": "log_curve"}
}
```

## 範例

### 輸入輸出範例
**輸入：** 預算：$100K，廣告活動：Search（$50K，100 次轉換）、Social（$30K，60 次轉換）、Display（$20K，20 次轉換）
**預期：** 把預算從 Display（邊際 CPA 高）挪到 Search（邊際 CPA 低）。例如 Search $60K、Social $30K、Display $10K。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 有一個廣告活動遠遠勝出 | 大部分預算給贏家 | 但其他活動還是要保留最低下限 |
| 所有廣告活動都飽和了 | 降低總花費 | 多花也沒用 |
| 新廣告活動，沒有資料 | 用最低測試預算 | 要先有資料才能最佳化 |

## 注意事項

- **反應曲線外推**：不要在觀察過的花費範圍之外做最佳化。花費更高時，曲線形狀可能會變。
- **歸因重疊**：使用者可能在不同廣告活動都看到廣告。Last-click 歸因會重複計算，把上層漏斗廣告活動的 CPA 墊高。要用多點觸擊歸因（multi-touch attribution）。
- **報酬遞減的假設**：不是每個廣告活動都符合平滑的報酬遞減。有些是階梯函數（例如花費超過某個門檻才觸及到新的受眾區隔）。
- **時間動態**：反應曲線會隨季節和競爭狀況位移。每月重新擬合曲線，或用滾動視窗。
- **最低可行花費**：每個廣告活動都需要足夠的預算才能走出學習階段。分得太薄，就是沒有任何一個活動拿到足夠的資料。

## 參考資料

- 反應曲線的擬合方法，見 `references/response-curves.md`
- 多點觸擊歸因整合，見 `references/attribution-integration.md`
