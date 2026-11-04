---
name: "algo-ad-vcg"
description: "實作 VCG 機制，做到誘因相容、誠實出價的廣告版位分配。當使用者需要設計誠實的拍賣機制、計算以外部性為基礎的付款，或想了解平台為什麼可能偏好 GSP 而不是 VCG 時使用，即使他們說的是『truthful auction design』『VCG payments』或『incentive-compatible mechanism』。"
metadata:
  category: "WP-37 廣告演算法"
  tags: ["advertising", "auction", "vcg", "mechanism-design"]
---

# VCG 機制（Vickrey-Clarke-Groves）

## 概述

VCG 分配版位以最大化整體社會福利，並向每個得標者收取他對其他人造成的外部性。誠實出價是優勢策略。複雜度為 O(N log N + K × N)，N=出價者數、K=版位數。

## 何時使用

**觸發條件：**
- 設計誘因相容（誠實）的多版位拍賣
- 計算福利最大化的分配，並以外部性定價
- 做 VCG 與 GSP 拍賣比較的學術分析

**不該使用的情況：**
- 營收最大化比誠實更重要時（GSP 通常賺得比較多）
- 單一標的拍賣（標準 Vickrey 就夠了）

## 演算法

```
IRON LAW: VCG Guarantees Truthful Bidding BUT May Not Maximize Revenue
VCG payments are based on externality (harm to others), not competition.
This makes VCG payments often LOWER than GSP payments. Platforms
choose GSP because it typically generates higher revenue despite
strategic bidding. Truthfulness has a revenue cost.
```

### 階段 1：輸入驗證
收集每個廣告主的每次點擊真實估值，以及每個版位的 CTR。估值必須非負。
**關卡：** 所有估值非負，版位 CTR 隨排名遞減。

### 階段 2：核心演算法
1. 計算福利最大化的分配：把廣告主分配到版位，使 Σ(value_i × CTR_slot_i) 最大
2. 對版位 s 的每個得標者 i：計算「沒有廣告主 i」時的總福利（重新最佳化其餘出價者）
3. VCG payment_i = （沒有 i 時其他人的福利）-（有 i 在場時其他人的福利）
4. 這等於：對所有較低位置 j 加總 (value_{j+1} × (CTR_j - CTR_{j+1}))

### 階段 3：驗證
檢查：所有付款 ≤ 估值（個體理性）、誠實出價是優勢策略、分配使福利最大。
**關卡：** 滿足 IR，福利為最佳。

### 階段 4：輸出
回傳分配結果，附上 VCG 付款與福利指標。

## 輸出格式

```json
{
  "allocation": [{"advertiser": "A", "slot": 1, "vcg_payment_per_click": 1.80, "total_welfare_contribution": 500}],
  "metadata": {"total_welfare": 1500, "total_revenue": 420, "mechanism": "vcg"}
}
```

## 範例

### 輸入輸出範例
**輸入：** 3 個出價者的估值 [10, 8, 2]，2 個版位的 CTR [0.5, 0.3]
**預期：** 分配：出價者1→版位1，出價者2→版位2。VCG 付款：出價者1 = 8×(0.5-0.3)+2×0.3 = 2.20，出價者2 = 2×0.3 = 0.60。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 所有估值相同 | 全部付 0 | 沒有造成外部性，沒有邊際傷害 |
| 一個出價者，一個版位 | 付 0 | 沒有其他出價者受害 |
| 出價者 < 版位數 | 全部得標，全部付 0 | 沒有競爭就沒有外部性 |

## 注意事項

- **營收不足**：VCG 常常賺得比 GSP 少。有些情況下得標者一毛都不用付（外部性為零）。
- **計算複雜度**：一般的組合拍賣中，VCG 要解 NP-hard 的福利最大化問題。版位拍賣則是多項式時間。
- **容易被串通**：出價者串通、協調彼此的外部性，就能操縱 VCG。
- **非單調性**：多加一個版位，有時反而會讓營收減少（所謂的「lonely bidder」病態）。
- **實務上很少見**：幾乎沒有大型廣告平台用純 VCG。理論上漂亮，商業上不是最佳解。

## 參考資料

- VCG 與 GSP 的營收比較，見 `references/revenue-comparison.md`
- 組合式 VCG 的延伸，見 `references/combinatorial-vcg.md`
