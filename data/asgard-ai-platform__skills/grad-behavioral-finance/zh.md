---
name: "grad-behavioral-finance"
description: "運用行為財務學理論，找出投資人的系統性偏誤及其對資產價格的影響。當使用者需要分析非理性的市場行為、用認知偏誤解釋定價異常、診斷投資人的決策錯誤，或問到「為什麼投資人把賠錢的股票抱太久」、「損失趨避如何影響定價」或「是什麼偏誤驅動了這個市場模式」時使用。"
metadata:
  category: "WP-26 財務理論"
  tags: ["behavioral-finance", "prospect-theory", "loss-aversion", "disposition-effect", "overconfidence", "Kahneman"]
---

# 行為財務學

## 概述

行為財務學挑戰「行為者是理性的」這個假設，記錄影響投資人決策與市場價格的系統性認知偏誤。它以 Kahneman 和 Tversky 的展望理論（1979）為基礎，解釋傳統財務學無法解釋的持續性異常現象。

## 何時使用

- 用投資人心理解釋市場異常（動能、泡沫、崩盤）
- 診斷投資組合管理中的決策偏誤
- 為投資流程設計去偏誤的策略
- 評估「理性」策略為什麼表現不如預期

## 何時不要用

- 拿來當作任何價格變動的萬用解釋，偏誤必須明確指出是哪一種
- 標準的理性模型已經足以解釋該現象
- 做規範性的投資組合建構，卻沒有考慮套利的限制

## 假設

```
IRON LAW: Investors are NOT rational — systematic biases create
predictable pricing errors. These errors persist because arbitrage
is limited (costs, risk, horizon constraints).
```

關鍵假設：
1. 認知偏誤是系統性的，不是隨機的，它們會造成有方向性的價格效應
2. 套利的限制讓理性交易者無法完全糾正錯誤定價
3. 參考點和框架會顯著影響決策

## 方法論

### 步驟 1：找出行為異常

觀察偏離理性預期的定價模式或決策。

### 步驟 2：對應到具體的偏誤

| 偏誤 | 說明 | 市場效應 |
|------|-------------|---------------|
| 損失趨避 | 損失帶來的痛，約是等量獲得的 2 倍 | 處分效應、股權溢酬之謎 |
| 過度自信 | 高估私有資訊的精確度 | 過度交易、分散不足 |
| 羊群行為 | 不管自己的私有訊號，跟著群眾走 | 泡沫、動能、崩盤 |
| 錨定 | 過度依賴最初的參考點 | 對盈餘驚喜反應不足 |
| 心理帳戶 | 依金錢的來源/標籤區別對待 | 投資組合分隔、賭場賺來的錢效應（house-money effect） |

### 步驟 3：評估套利的限制

- 基本面風險、雜訊交易者風險、執行成本
- 放空限制、模型風險、期限錯配

### 步驟 4：提出去偏誤或利用偏誤的策略

- 去偏誤：事先承諾的規則、系統化的再平衡、檢查清單
- 利用偏誤：逆向策略，但只有在套利的限制可控時才適用

## 輸出格式

```markdown
## Behavioral Finance Analysis: [Context]

### Observed Anomaly
- [Description of pricing pattern or decision error]

### Bias Diagnosis
| Bias | Evidence | Severity |
|------|----------|----------|
| [bias name] | [specific observation] | [High/Medium/Low] |

### Limits to Arbitrage
- [Why rational traders cannot fully correct this]

### Recommendations
1. [De-biasing strategy or trading implication]
2. [Process improvement]
```

## 常見陷阱

- 行為偏誤能解釋模式，但很少能預測時機：「市場保持非理性的時間，可以比你保持償付能力的時間更長」
- 並非所有異常都是行為造成的，有些反映的是合理的風險補償
- 展望理論是描述性的，不是規範性的，它解釋行為，不是最佳決策
- 偏誤會互相作用，損失趨避加上過度自信可能產生互相矛盾的預測
- 發表偏誤可能讓「真正的」行為異常數量被誇大
- 機構投資人展現的偏誤跟散戶不同

## 參考資料

- Kahneman, D. & Tversky, A. (1979). Prospect theory: an analysis of decision under risk. *Econometrica*, 47(2), 263-292.
- Shleifer, A. & Vishny, R. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55.
- Barberis, N. & Thaler, R. (2003). A survey of behavioral finance. *Handbook of the Economics of Finance*, 1, 1053-1128.
