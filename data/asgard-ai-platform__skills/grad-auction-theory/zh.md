---
name: "grad-auction-theory"
description: "運用拍賣理論比較四種經典拍賣形式，並評估收益等價。當使用者需要選擇拍賣形式、評估競標策略，或判斷收益等價在風險趨避、不對稱或相關價值之下何時失效時使用。"
metadata:
  category: "WP-27 賽局與制度經濟"
  tags: ["auction-theory", "revenue-equivalence", "Vickrey-auction", "English-auction", "Dutch-auction", "first-price-sealed-bid", "winners-curse"]
---

# 拍賣理論：四種經典形式與收益等價

## 概述

拍賣理論分析在不同銷售機制下的策略性競標行為。四種經典形式（英式（遞增）、荷式（遞減）、第一價格密封競標，以及第二價格密封競標（Vickrey））在標準假設下會產生相同的預期收益。收益等價定理（Revenue Equivalence Theorem，RET）是核心的基準，一切實務上的拍賣設計決策，都來自於偏離它的假設。

## 何時使用

- 為銷售商品、頻譜、採購或廣告版位，在各種拍賣形式之間做選擇
- 分析特定形式下的競標者策略（出價保留、狙擊出價、跳價）
- 評估一個擬議的拍賣是否達到最佳收益或效率

## 何時不要用

- 定價銷售或協商銷售，沒有競爭性的競標
- 有複雜互補性的多單位拍賣（要用組合拍賣的框架）
- 賣方沒有承諾能力去落實拍賣規則

## 假設

```
IRON LAW: Revenue equivalence holds ONLY with risk-neutral bidders,
independent private values (IPV), and symmetric bidders — violate ANY
assumption and auction format matters.
```

- 只賣單一、不可分割的標的
- 競標者是風險中立的預期效用極大化者
- 價值是獨立且同分配的（IPV）
- 競標者是對稱的（價值的分配相同）
- 支付只是出價的函數（沒有外部性）

## 方法論

**步驟 1：找出價值模型**
分類情境：獨立私有價值（IPV）、共同價值，或相關聯價值。IPV 是指每位競標者確切知道自己的價值；共同價值是指標的物只有一個所有人都不知道的真實價值；相關聯價值則是兩者的推廣。

**步驟 2：推導均衡競標策略**
對每一種拍賣形式，求解貝氏納許均衡。在 IPV 之下的第二價格 / 英式拍賣中，出真實價值是優勢策略。在第一價格 / 荷式拍賣中，競標者會出低於真實價值的價格：b(v) = E[Y1 | Y1 < v]，其中 Y1 是最高的競爭價值。

**步驟 3：套用收益等價，或找出違反之處**
在 RET 的假設下，四種形式產生相同的預期收益。檢查是否有違反：(a) 風險趨避會讓第一價格優於第二價格；(b) 不對稱的競標者打破等價；(c) 共同價值引入贏者的詛咒，並有利於英式拍賣（Milgrom-Weber 連結原則）；(d) 預算限制、進入成本或底價會造成依形式而異的效果。

**步驟 4：建議形式與參數**
根據找出的偏離之處，建議拍賣形式、最佳底價（在 IPV 的情況下 r* 滿足 r* = v0 + [1 - F(r*)] / f(r*)），以及任何額外的設計功能（例如進場費、資訊揭露政策）。

## 輸出格式

```markdown
## Auction Analysis: [Context]

### Value Model
- **Type**: IPV / Common / Affiliated
- **Distribution**: [bidder value distribution]
- **Number of bidders**: [N]
- **Risk attitude**: risk-neutral / risk-averse

### Format Comparison
| Format              | Equilibrium Strategy         | Expected Revenue | Notes        |
|--------------------|------------------------------|-----------------|--------------|
| English (ascending) |                              |                 |              |
| Dutch (descending)  |                              |                 |              |
| First-price sealed  |                              |                 |              |
| Second-price sealed |                              |                 |              |

### Revenue Equivalence Assessment
- **RET holds?** Yes / No
- **Violation source**: [risk aversion / asymmetry / common values / other]
- **Ranking**: [which format generates highest revenue and why]

### Optimal Reserve Price
- **r*** = [value]
- **Derivation**: [brief]

### Recommendation
[Chosen format, reserve price, and rationale]
```

## 常見陷阱

- 贏者的詛咒是共同價值的現象，在純 IPV 的情境中不適用，但競標者常常表現得好像適用
- 收益等價講的是「預期」收益；各形式之間的變異數不同（第一價格的變異數較低）
- 最佳底價會排除一些有效率的交易，賣方是犧牲效率來換取收益
- 實務上，英式拍賣會揭露較多資訊，這對相關聯價值有幫助（Milgrom-Weber 連結原則）
- 第二價格和英式拍賣比較容易共謀；第一價格對競標者聯盟比較有抵抗力
- 線上拍賣（eBay 式）不是純粹的英式拍賣，固定的截止時間、代理出價和狙擊出價都會改變均衡行為

## 參考資料

- Vickrey, W. (1961). "Counterspeculation, Auctions, and Competitive Sealed Tenders." *Journal of Finance*.
- Riley, J. & Samuelson, W. (1981). "Optimal Auctions." *American Economic Review*.
- Milgrom, P. & Weber, R. (1982). "A Theory of Auctions and Competitive Bidding." *Econometrica*.
- Krishna, V. (2010). *Auction Theory*, 2nd ed. Academic Press.
