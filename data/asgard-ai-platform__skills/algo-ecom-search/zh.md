---
name: "algo-ecom-search"
description: "最佳化電商搜尋相關性，涵蓋從查詢理解到結果呈現的完整流程。當使用者需要改善搜尋品質、實作查詢處理功能，或診斷搜尋相關性問題時使用，即使他們說的是『search results are bad』『improve product search』或『search relevance optimization』。"
metadata:
  category: "WP-43 電商搜尋演算法"
  tags: ["ecommerce", "search", "relevance", "query-understanding"]
---

# 電商搜尋相關性

## 概述

電商搜尋是一條流程：查詢理解 → 檢索 → 排序 → 呈現。每個階段都會影響相關性。最佳化要先診斷是「哪個階段」出問題，不能只調其中一個元件。零結果率、點擊率和加入購物車率是關鍵指標。

## 何時使用

**觸發條件：**
- 診斷為什麼搜尋結果不符合使用者期待
- 實作查詢處理功能（拼字檢查、同義詞、意圖偵測）
- 降低零結果搜尋、提高轉換

**不該使用的情況：**
- 只要設計排序演算法時（用電商排序 skill）
- 只要文字相關性評分時（用 BM25）

## 演算法

```
IRON LAW: Search Quality Is Determined by the WEAKEST Pipeline Stage
Query understanding, retrieval, ranking, and presentation are sequential.
Perfect ranking cannot fix bad retrieval (missing products). Perfect
retrieval cannot fix bad query understanding (wrong intent). Diagnose
which stage fails FIRST before optimizing.
```

### 階段 1：輸入驗證
稽核目前的搜尋：依搜尋量抽樣 100 個查詢。每個查詢都評估：查詢理解（意圖對嗎？）、檢索（候選集裡有相關商品嗎？）、排序（最好的商品在最上面嗎？）、呈現（顯示方式有用嗎？）。
**關卡：** 弱點已定位到特定的流程階段。

### 階段 2：核心演算法
**查詢理解：** 1. 拼字修正（編輯距離、n-gram）。2. 同義詞擴展（earbuds↔earphones）。3. 意圖分類（商品搜尋 vs 品牌搜尋 vs 分類瀏覽）。4. 查詢改寫（屬性抽取：「red shoes size 10」→ color:red, category:shoes, size:10）。

**檢索最佳化：** 1. 多欄位搜尋（標題、描述、品牌、分類、SKU）。2. 加權策略（標題命中 > 描述命中）。3. 篩選 vs 加權（硬性限制：分類、有無庫存；軟性訊號：熱門度）。

**結果品質：** 1. 零結果的備援（放寬查詢、建議替代方案）。2. 分面導覽（依價格、品牌、評分篩選）。3. Did-you-mean 建議。

### 階段 3：驗證
量測：零結果率（目標 <5%）、第一頁的 CTR（目標 >30%）、有人工判斷的查詢上的 NDCG。
**關卡：** 關鍵指標比基準提升。

### 階段 4：輸出
回傳搜尋稽核報告，附上排好優先順序的改善項目。

## 輸出格式

```json
{
  "audit": {"zero_result_rate": 0.08, "avg_ctr": 0.25, "top_failing_queries": ["earbuds wireless", "gift ideas"]},
  "recommendations": [{"stage": "query_understanding", "issue": "no_synonym_expansion", "impact": "high", "fix": "Add earbuds↔earphones synonym"}],
  "metadata": {"queries_sampled": 100, "period": "2025-Q1"}
}
```

## 範例

### 輸入輸出範例
**輸入：** 「wireles earbud」（拼錯）回傳 0 筆結果
**預期：** 拼字修正 → 「wireless earbuds」→ 顯示相關商品。建議：實作拼字修正。

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 只有分類的查詢（「shoes」） | 瀏覽意圖，顯示熱門商品 | 不是特定商品的搜尋 |
| 品牌拼錯 | 模糊的品牌比對 | 「Nikee」→「Nike」 |
| 長尾查詢（「blue cotton v-neck t-shirt men XL」） | 需要屬性解析 | 自由文字裡有多個結構化屬性 |

## 注意事項

- **同義詞維護**：同義詞表需要持續整理。「AirPods」是品牌，不是「earbuds」的同義詞。放錯同義詞會傷害精確度。
- **過度召回**：太積極的同義詞擴展和模糊比對會回傳太多不相關的結果。要在召回率（找到全部）和精確率（只留相關的）之間取得平衡。
- **語言特有的挑戰**：中文搜尋需要斷詞。「皮鞋」（leather shoes）不該比對到「拖鞋」（slippers），雖然兩者都有「鞋」。
- **搜尋分析不可少**：沒有追蹤查詢層級的 CTR、零結果查詢和轉換率，你就是在盲目最佳化。
- **搜尋的 A/B 測試很難**：搜尋的改動會影響所有查詢，有些變好、有些退步。要量測整體指標，同時依查詢類型分層。

## 參考資料

- 查詢理解流程的架構，見 `references/query-pipeline.md`
- 搜尋相關性評估方法論，見 `references/relevance-evaluation.md`
