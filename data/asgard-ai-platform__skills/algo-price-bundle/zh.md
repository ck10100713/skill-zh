---
name: "algo-price-bundle"
description: "用純搭售、混合搭售和消費者剩餘分析來設計搭售定價策略。當使用者需要替商品組合定價、判斷搭售能不能增加獲利，或分析拆售的機會時使用，即使他們說的是『should we bundle these products』『bundle pricing』或『package deal pricing』。"
metadata:
  category: "WP-39 定價演算法"
  tags: ["pricing", "bundling", "consumer-surplus", "product-strategy"]
---

# 搭售定價策略

## 概述

搭售定價是把多個產品以合併價格一起賣，透過在各產品之間平均估值，來榨取消費者剩餘。適用於顧客估值各異、而且呈負相關的情況。三種類型：純搭售（只賣組合）、混合搭售（組合 + 單賣）、拆售。

## 何時使用

**觸發條件：**
- 決定要不要把產品 / 服務搭在一起賣
- 設定組合價相對於各單品價格的關係
- 分析目前的組合該不該拆開賣

**不該使用的情況：**
- 產品需求彼此獨立、估值沒有相關性時（搭售沒有價值）
- 法規禁止搭售安排時

## 演算法

```
IRON LAW: Bundling Increases Profit ONLY With NEGATIVELY CORRELATED Valuations
If ALL customers value the same items highly, bundling adds no surplus.
Bundling works when: Customer A values Product 1 high + Product 2 low,
while Customer B values Product 1 low + Product 2 high. The bundle
price captures both at a middle price neither would pay for their
low-value item alone.
```

### 階段 1：輸入驗證
收集：每個客群對各單品的估值（或願付價格）。計算各產品之間估值的相關性。
**關卡：** 有估值資料，相關性為負或混合。

### 階段 2：核心演算法
1. 計算最佳單品價格：讓 Σ(每個產品的營收) 最大
2. 計算最佳組合價：在聯合估值分布下，找出讓組合營收最大的價格
3. 比較：純搭售營收、混合搭售營收、單品定價營收
4. 混合搭售：組合價 < 各單品價格加總；折扣 = 搭售的誘因

### 階段 3：驗證
檢查：混合搭售應該弱優於純搭售和單品定價（Adams & Yellen, 1976）。如果不是，要重新檢視估值假設。
**關卡：** 混合搭售的獲利 ≥ max(純搭售, 單品定價)。

### 階段 4：輸出
回傳最佳定價策略，附上獲利推估。

## 輸出格式

```json
{
  "recommendation": "mixed_bundling",
  "prices": {"product_a": 299, "product_b": 199, "bundle_ab": 399},
  "profit_comparison": {"individual": 45000, "pure_bundle": 48000, "mixed_bundle": 52000},
  "metadata": {"segments": 3, "valuation_correlation": -0.35}
}
```

## 範例

### 輸入輸出範例
**輸入：** 產品 A（WTP：Seg1=$80、Seg2=$30），產品 B（WTP：Seg1=$30、Seg2=$70）。每個客群有 100 位顧客。
**預期：** 單品最佳價：A=$80、B=$70，營收=$15K。組合價 $100：兩個客群都買，營收=$20K。搭售勝出。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 完全正相關 | 單品定價勝出 | 所有顧客對兩者都估值高，或都估值低 |
| 其中一個產品是免費品 | 組合 = 付費品 + 免費品 | 軟體常見（免費試用 + 付費附加元件） |
| 組合裡有 10 個以上產品 | 混合搭售很複雜 | 組合太多，改用分級的組合 |

## 注意事項

- **自我蠶食**：組合可能蠶食高 WTP 的顧客，他們本來會以更高的總價個別購買。混合搭售可以減輕這點。
- **感知價值**：組合折扣要讓人明顯感受到。$299+$299 的產品組成 $499 的組合（折 16%），比兩個各 $260 的產品賣 $499 更容易被感知。
- **邊際成本很重要**：邊際成本為零的產品（軟體、數位產品）從搭售得到的好處最大。銷貨成本高的實體商品，利潤空間比較緊。
- **複雜度的成本**：組合選項太多會造成選擇困難。限制在 2-3 個組合層級。
- **法規上的搭售限制**：在某些市場，強迫購買某個產品才能買另一個是違法的（反壟斷）。要確保組合是折扣，不是強制條件。

## 參考資料

- Adams-Yellen 搭售理論，見 `references/bundling-theory.md`
- 多產品定價最佳化，見 `references/multi-product-pricing.md`
