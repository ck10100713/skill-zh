---
name: "algo-ad-gsp"
description: "實作 Generalized Second Price 拍賣，用於廣告版位的分配與定價。當使用者需要理解搜尋廣告拍賣、計算廣告排名與每次點擊成本，或分析出價動態時使用，即使他們說的是『how does Google Ads auction work』『ad rank calculation』或『second price auction for ads』。"
metadata:
  category: "WP-37 廣告演算法"
  tags: ["advertising", "auction", "gsp", "ad-pricing"]
---

# Generalized Second Price 拍賣

## 概述

GSP 把 K 個廣告版位分配給 N 個出價者：出價最高的拿第一個版位，第二高的拿第二個，以此類推。每個得標者付的是排在他「下一個位置」的廣告主的出價（每個版位各自的第二價格）。Google Ads 和 Bing Ads 都在用。排序出價的複雜度是 O(N log N)。

## 何時使用

**觸發條件：**
- 理解搜尋引擎廣告拍賣的運作機制
- 從出價和品質資料計算廣告排名與每次點擊成本
- 分析贊助搜尋中的出價策略

**不該使用的情況：**
- 需要誘因相容、誠實出價時（用 VCG 機制）
- 分析展示型 / 程式化廣告拍賣時（通常是 first-price）

## 演算法

```
IRON LAW: GSP Is NOT Incentive-Compatible
Unlike Vickrey (single-item second-price) auctions, truthful bidding
is NOT a dominant strategy in GSP. Bidders may strategically shade
bids below their true value. The equilibrium depends on competitor bids.
Ad Rank = Bid × Quality Score (Google's variant adds format/extensions).
```

### 階段 1：輸入驗證
收集：所有競爭廣告主的出價、品質分數（或廣告排名分數）。定義可用的版位位置，以及各自的點擊率乘數。
**關卡：** 所有出價為正數，品質分數落在有效範圍內。

### 階段 2：核心演算法
1. 計算每個廣告主的 Ad Rank：AdRank_i = Bid_i × QualityScore_i
2. 依 Ad Rank 由高到低排序廣告主
3. 前 K 名依序分配到版位 1 到 K
4. 計算付款：CPC_i = AdRank_{i+1} / QualityScore_i（維持目前排名所需的價格）
5. 最後一個版位的得標者付最低出價門檻

### 階段 3：驗證
檢查：所有付款 ≤ 出價、排名依 Ad Rank 排序、沒有廣告主付超過自己的出價。
**關卡：** 所有得標者的付款 ≤ 出價，排名一致。

### 階段 4：輸出
回傳版位分配結果，包含排名、CPC 和預估點擊數。

## 輸出格式

```json
{
  "slots": [{"advertiser": "A", "position": 1, "ad_rank": 8.5, "cpc": 2.10, "est_clicks": 100}],
  "metadata": {"total_bidders": 15, "slots_available": 4, "auction_type": "gsp"}
}
```

## 範例

### 輸入輸出範例
**輸入：** 出價者：A(bid=3, QS=8)、B(bid=4, QS=5)、C(bid=2, QS=9)。版位：2 個。
**預期：** 排名分數：A=24、C=18、B=20。順序：A（第 1）、B（第 2）。CPC_A = 20/8 = 2.50，CPC_B = 18/5 = 3.60。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| Ad Rank 平手 | 由平台的 tiebreaker 決定（歷史 CTR 等） | GSP 需要嚴格的排序 |
| 只有一個出價者 | 拿下版位 1，付最低 CPC | 沒有競爭，就是底價 |
| 出價低於門檻 | 沒有資格 | 強制執行最低出價要求 |

## 注意事項

- **Quality Score 是黑盒子**：Google 的 QS 包含預期 CTR、廣告相關性和到達網頁體驗，確切公式是專有的。
- **策略性壓低出價**：因為 GSP 不是誠實機制，老練的廣告主會壓低出價。也就是說，觀察到的出價不代表真實的願付價格。
- **排名 ≠ 價值**：排名越高點擊越多，但 CPC 也越高。最划算的位置可能是第 2 或第 3，不一定是第 1。
- **預算限制**：GSP 不考慮每日預算。受預算限制的廣告主必須在一天之中自己調整出價節奏。
- **廣泛比對擴展**：拍賣會包含查詢擴展後的比對，這些的轉換率可能和完全比對不同。

## 參考資料

- GSP 的 Nash 均衡分析，見 `references/gsp-equilibrium.md`
- 與 VCG 機制的比較，見 `references/gsp-vs-vcg.md`
