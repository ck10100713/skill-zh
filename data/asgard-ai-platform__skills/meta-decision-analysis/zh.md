---
name: "meta-decision-analysis"
description: "用決策矩陣、決策樹、期望值和多準則決策分析（MCDA）做結構化的決策分析。使用者面對有多個選項和多項準則的複雜決策、需要客觀比較替代方案、量化風險與報酬，或要帶領團體做決定時使用，就算他們說的是「我們該選哪個」、「幫我決定」、「這些選項怎麼比較」或「預期結果是什麼」也一樣。"
metadata:
  category: "WP-22 跨學科"
  tags: ["meta-thinking", "decision-analysis", "decision-matrix"]
---

# 決策分析

## 框架

```
IRON LAW: Make Criteria and Weights Explicit BEFORE Evaluating Options

Choosing criteria after seeing the options lets bias sneak in — you
unconsciously weight criteria that favor your preferred option.
Define criteria, assign weights, THEN score options.
```

### 決策矩陣（加權評分）

1. **列出替代方案**（3-6 個選項，包含「什麼都不做」）
2. **定義準則**（4-8 個重要的因素）
3. **幫準則加權**（加起來必須是 100%）
4. **每個選項在每項準則上評分**（1-5 或 1-10）
5. **計算加權總分** = Σ(分數 × 權重)
6. **敏感度檢查**：如果調整權重最高的那項準則，贏家會變嗎？

### 決策樹（不確定情況下的連續決策）

適用於有不確定性、而且要分步驟做的決策：
1. 畫出決策節點（方形）和機會節點（圓形）
2. 為每個機會結果指定機率（加起來必須是 1.0）
3. 為終端節點指定報酬
4. 計算期望值 = Σ(機率 × 報酬)
5. 選期望值最高的分支（或風險調整後結果最好的）

### 多準則決策分析（MCDA）

適用於利害關係人優先順序互相衝突的複雜決策：
1. 每個利害關係人獨立定義自己的準則和權重
2. 彙整成一個合併的加權矩陣
3. 找出利害關係人哪裡一致（容易的決定）、哪裡不一致（需要協商）

## 輸出格式

```markdown
# Decision Analysis: {Decision}

## Alternatives
1. {Option A}
2. {Option B}
3. {Option C}

## Decision Matrix
| Criterion | Weight | Option A | Option B | Option C |
|-----------|--------|----------|----------|----------|
| {criterion 1} | {X%} | {1-5} | {1-5} | {1-5} |
| **Weighted Total** | 100% | **{total}** | **{total}** | **{total}** |

## Sensitivity Analysis
- If {criterion} weight changes from X% to Y%, winner changes from {A} to {B}

## Recommendation
{Winner with rationale and key trade-offs acknowledged}
```

## 注意事項

- **「什麼都不做」永遠是個選項**：把它放進來當基準線。有時候最好的決定就是等。
- **分數是主觀的**：一個人給的「4」不等於另一個人給的「4」。評分之前先定義每個分數代表什麼，把標準校準好。
- **期望值忽略風險偏好**：$50（確定）的期望值和「50% 機率拿 $0、50% 機率拿 $100」的期望值，用 EV 算是一樣的，但感覺差很多。高風險的決策要用風險調整後的指標。
- **分析癱瘓**：決策分析應該是加快決策，不是拖慢。給分析設一個時間限制。

## 參考資料

- 決策樹軟體工具請看 `references/decision-tools.md`
