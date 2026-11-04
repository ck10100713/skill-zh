---
name: "grad-emh"
description: "用效率市場假說（Fama，1970）從弱式、半強式、強式三種形式，評估資產價格對資訊的吸收程度。當使用者需要評估市場效率、判斷某個交易策略能不能產生異常報酬、評估事件研究，或問到「技術分析有用嗎」「市場是不是已經知道這件事了」「這個異常現象能拿來賺錢嗎」時，就用這個 skill。"
metadata:
  category: "WP-26 財務理論"
  tags: ["EMH", "efficient-market", "Fama", "market-efficiency", "information", "anomalies"]
---

# Efficient Market Hypothesis (EMH)

## Overview

效率市場假說（Fama，1970）主張資產價格已經充分反映可得資訊，所以不可能持續賺到異常報酬。EMH 分成三種形式，也就是弱式、半強式和強式，各自由價格所反映的資訊集合來定義。

## When to Use

- 評估某個交易策略是不是真的利用了無效率
- 設計事件研究（半強式的檢定）
- 評估主動管理相對被動指數化有沒有增加價值
- 討論技術分析或基本面分析是否有效

## When NOT to Use

- 拿來當藉口，不加調查就忽略所有市場異常現象
- 市場明顯缺乏流動性，或資訊被分割
- 做規範性的主張：EMH 描述的是價格行為，不是價格「應該」是多少

## Assumptions

```
IRON LAW: In an efficient market, prices reflect available information —
beating the market consistently requires either superior information
or accepting more risk. No free lunch.
```

關鍵假設：
1. 有大量理性、追求利潤最大化的參與者
2. 資訊沒有成本，而且同時提供給所有參與者
3. 交易成本不會阻礙根據資訊進行交易
4. 投資人對新資訊反應快速而且沒有偏誤

## Methodology

### Step 1 — Identify the Information Set

- 弱式：只有過去的價格和成交量
- 半強式：所有公開可得的資訊
- 強式：所有資訊，包括私有或內線資訊

### Step 2 — Determine the Testable Implication

| Form | Information Reflected | Implication |
|------|----------------------|-------------|
| Weak | 歷史價格 | 技術分析無法賺到超額報酬 |
| Semi-strong | 所有公開資訊 | 基本面分析無法賺到超額報酬 |
| Strong | 所有資訊（公開加私有） | 連內線人士也無法賺到超額報酬 |

### Step 3 — Select Appropriate Test

- 弱式：自相關檢定、連串檢定（runs test）、濾嘴法則
- 半強式：事件研究（公告前後的異常報酬）
- 強式：內線交易獲利研究

### Step 4 — Interpret Results with Joint-Hypothesis Awareness

任何效率檢定，同時也是在檢定用來定義「異常」報酬的資產定價模型。

## Output Format

```markdown
## EMH Assessment: [Market / Strategy]

### Efficiency Form Tested
- Form: [weak / semi-strong / strong]
- Information set: [description]

### Evidence
| Test | Result | Supports Efficiency? |
|------|--------|---------------------|
| [test name] | [finding] | [Yes/No/Ambiguous] |

### Known Anomalies in This Context
- [List relevant anomalies and their current status]

### Conclusion
- [Efficiency assessment with caveats]
- [Joint-hypothesis caveat]
```

## Gotchas

- 聯合假設問題：不假設一個均衡模型，就沒辦法檢定效率
- Grossman-Stiglitz 悖論（1980）：如果市場完全有效率，就沒有人有動機去蒐集資訊
- 異常現象（動能、價值、規模）持續存在，但可能反映風險或資料挖掘
- EMH 並沒有主張價格永遠「正確」，只是主張錯誤定價無法被系統性地利用
- 市場效率因市場區塊而異，大型股比微型股更有效率
- 行為財務學提供了系統性的反例，但不一定推翻 EMH

## References

- Fama, E. (1970). Efficient capital markets: a review of theory and empirical work. *Journal of Finance*, 25(2), 383-417.
- Grossman, S. & Stiglitz, J. (1980). On the impossibility of informationally efficient markets. *American Economic Review*, 70(3), 393-408.
- Malkiel, B. (2003). The efficient market hypothesis and its critics. *Journal of Economic Perspectives*, 17(1), 59-82.
