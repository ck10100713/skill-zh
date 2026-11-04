---
name: "algo-seo-schema"
description: "用 JSON-LD 格式實作 Schema.org 結構化資料標記，強化搜尋結果。當使用者需要替網頁加上 rich snippet、實作 FAQ／Product／Article schema、或驗證結構化資料時使用，即使他們說的是「rich snippets」、「結構化資料」或「Google 豐富結果」也一樣。"
metadata:
  category: "WP-35 SEO 演算法"
  tags: ["seo", "schema-org", "json-ld", "structured-data"]
---

# Schema.org 結構化資料

## 概述

Schema.org 結構化資料透過 JSON-LD，向搜尋引擎提供機器可讀的頁面脈絡。能讓 SERP 出現豐富結果（星等、FAQ、麵包屑、產品卡片）。每個頁面的實作複雜度是 O(1)，這是標記工作，不是運算工作。

## 何時使用

**觸發條件：**
- 要讓網頁符合 rich snippet 的資格
- 要實作 product、article、FAQ、HowTo 或 event 標記
- 要除錯 Google Search Console 的結構化資料錯誤

**何時不要用：**
- 要最佳化頁面內容或關鍵字時（用內容 SEO）
- 要提升頁面速度時（用 Core Web Vitals 最佳化）

## 演算法

```
鐵律：Schema 標記必須「符合」可見內容
標記使用者看不到的內容，違反 Google 指南，
還有被人工處罰的風險。每個結構化資料欄位
都必須對應到頁面上看得見的內容。
```

### 階段 1：輸入驗證
辨識頁面類型（Article、Product、FAQ、HowTo、Event 等）。把可見內容對應到 schema 必要和建議的屬性。
**關卡：** 頁面類型已辨識、所有必要屬性都有可見內容。

### 階段 2：核心演算法
1. 從詞彙表選出正確的 Schema.org 類型
2. 把頁面內容對應到 schema 屬性（name、description、image 等）
3. 建立帶有 @context 和 @type 的 JSON-LD 物件
4. 處理巢狀類型（例如 Product 包含 Offer 包含 Price）
5. 把 JSON-LD 放在 `<head>` 裡的 `<script type="application/ld+json">`

### 階段 3：驗證
用 Google Rich Results Test 驗證。檢查：沒有錯誤、所有必要欄位都在、和可見內容沒有不一致。
**關卡：** 通過 Google Rich Results Test，零錯誤。

### 階段 4：輸出
回傳完整、可直接插入的 JSON-LD 標記。

## 輸出格式

```json
{
  "schema": {"@context": "https://schema.org", "@type": "Product", "name": "...", "offers": {"@type": "Offer", "price": "29.99", "priceCurrency": "TWD"}},
  "validation": {"errors": 0, "warnings": 1, "eligible_rich_results": ["Product snippet"]}
}
```

## 範例

### 輸入輸出範例
**輸入：** 有 3 個問答的 FAQ 頁面
**預期：** JSON-LD 中的 FAQPage schema，包含 3 組 Question/Answer

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 沒有明確類型的頁面 | 退回用 WebPage | 最通用的有效類型 |
| 需要多個 schema | JSON-LD 物件的陣列 | 一個頁面可以有多種類型 |
| 缺少必要欄位 | 報錯，不要產生 | 不完整的 schema 比沒有更糟 |

## 常見陷阱

- **必要 vs 建議**：Google 對每種類型要求特定欄位。缺少必要欄位 = 整個 schema 被忽略。要查每種類型的文件。
- **巢狀深度**：很深的巢狀 schema（Product > Offer > Seller > Address）很容易出錯。每一層巢狀都要驗證。
- **Schema 垃圾資訊**：為頁面上沒有的內容加 schema（假評論、不存在的價格）會觸發人工處罰。
- **類型的具體程度**：用最具體的類型。「Article」比「WebPage」好；新聞內容的話，「NewsArticle」比「Article」好。
- **測試的落差**：Google Rich Results Test 顯示的是 Google 看到的內容，但不是所有有效的 schema 都會觸發豐富結果。符合資格 ≠ 保證顯示。

## 參考資料

- 依類型整理的完整屬性參考，見 `references/type-properties.md`
- 常見的驗證錯誤與修正，見 `references/validation-errors.md`
