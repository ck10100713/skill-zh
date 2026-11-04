---
name: "grad-capm"
description: "運用資本資產定價模型（CAPM）估計預期報酬並評估風險與報酬的取捨。當使用者需要計算資產的預期報酬、把 beta 解讀為系統性風險暴險、評估一項投資是否補償了風險，或問到「我該預期多少報酬」、「風險溢酬是多少」或「beta 如何影響定價」時使用。"
metadata:
  category: "WP-26 財務理論"
  tags: ["CAPM", "beta", "systematic-risk", "expected-return", "Sharpe", "risk-premium"]
---

# 資本資產定價模型（CAPM）

## 概述

CAPM（Sharpe, 1964；Lintner, 1965）建立了系統性風險與預期報酬之間的線性關係。這個模型指出，任何資產的預期報酬等於無風險利率，加上承擔市場風險的溢酬（再乘上該資產的 beta）。

## 何時使用

- 為股權估值估計必要報酬率
- 計算 WACC 中的股權成本
- 透過 beta 比較資產風險
- 對照證券市場線（SML）評估投資組合績效

## 何時不要用

- 資產對規模、價值或市場風險以外的其他因子有顯著暴險時
- 對缺乏流動性或未公開交易的資產，beta 的估計不可靠
- 市場投資組合的代理變數有疑慮時（Roll 的批評）

## 假設

```
IRON LAW: CAPM only prices SYSTEMATIC risk — diversifiable (unsystematic)
risk earns NO premium. An asset's expected return depends solely on its
beta with the market portfolio.
```

關鍵假設：
1. 投資人是具有同質預期的均值-變異數最佳化者
2. 存在一個無風險資產，可以無限制地借入與貸出
3. 市場是無摩擦的：沒有稅、交易成本或放空限制
4. 所有資產都是無限可分割且公開交易的

## 方法論

### 步驟 1：找出輸入值

- 無風險利率（Rf）：與投資期間相符的政府公債殖利率
- 市場報酬 E(Rm)：歷史平均或前瞻性的估計
- Beta：資產報酬對市場報酬做迴歸

### 步驟 2：計算預期報酬

E(Ri) = Rf + Bi x (E(Rm) - Rf)。從均值-變異數最佳化推導的過程，見 `references/derivation.md`。

### 步驟 3：畫在證券市場線上

在 SML 之上的資產被低估（正的 alpha），在其下則被高估（負的 alpha）。

### 步驟 4：解讀並決策

- Beta > 1：放大市場的波動，風險較高、預期報酬較高
- Beta < 1：減弱市場的波動，風險較低、預期報酬較低
- Beta = 0：報酬等於無風險利率

## 輸出格式

> ⚠️ **小數 vs 百分比**：傳值給隨附的 script 或從它取值時，所有利率
> （`risk_free`、`market_return`、`beta_contribution`、`expected_return`、`alpha`）都是
> **小數**，`0.05` 代表 5%，不是 `5.0`。下面的敘述型報告為了方便人閱讀，會以
> 百分比呈現，但同一個 JSON 物件裡絕對不要把兩種混用。

```markdown
## CAPM Analysis: [Asset / Portfolio]

### Inputs
| Parameter | Value | Source |
|-----------|-------|--------|
| Risk-free rate (Rf) | x% | [source] |
| Market return E(Rm) | x% | [source] |
| Beta | x.xx | [estimation method] |

### Expected Return
- E(Ri) = Rf + B x (E(Rm) - Rf) = x%

### SML Assessment
- Alpha = Actual return - Expected return = x%
- Interpretation: [undervalued / overvalued / fairly priced]

### Limitations in This Context
- [Note any assumption violations]
```

## 常見陷阱

- Beta 是回頭看的，未來的 beta 可能跟歷史估計不同
- 市場代理變數的選擇影響極大（Roll 的批評，1977）
- CAPM 假設只有單一風險因子，實證證據支持多因子模型
- 無風險利率的選擇（短期國庫券 vs 長期公債）對結果有顯著影響
- Beta 的估計對報酬頻率（日 vs 月）和樣本期間很敏感
- CAPM 無法解釋低 beta 異常（低 beta 股票的表現優於預測）

## Scripts

| Script | 說明 | 用法 |
|--------|-------------|-------|
| `scripts/capm.py` | 計算 CAPM 預期報酬與 alpha | `python scripts/capm.py --help` |

執行 `python scripts/capm.py --verify` 可跑內建的合理性測試。

## 參考資料

- Sharpe, W. (1964). Capital asset prices. *Journal of Finance*, 19(3), 425-442.
- Lintner, J. (1965). The valuation of risk assets. *Review of Economics and Statistics*, 47(1), 13-37.
- Roll, R. (1977). A critique of the asset pricing theory's tests. *Journal of Financial Economics*, 4(2), 129-176.
