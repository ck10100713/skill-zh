---
name: seo
description: 稽核、規劃並實作 SEO 改善，涵蓋技術 SEO、頁面內優化、結構化資料、Core Web Vitals 和內容策略。使用者想提升搜尋能見度、修補 SEO 問題、做 schema markup、處理 sitemap/robots，或做關鍵字對應時使用。
metadata:
  origin: ECC
---

# SEO

靠技術正確、效能和內容相關性提升搜尋能見度，不耍花招。

## 何時使用

在這些情況使用這個 skill：
- 稽核可爬取性、可索引性、canonical 或轉址
- 改善 title 標籤、meta description 和標題結構
- 新增或驗證結構化資料
- 改善 Core Web Vitals
- 做關鍵字研究，並把關鍵字對應到 URL
- 規劃內部連結，或 sitemap / robots 的變更

## 運作方式

### 原則

1. 先修技術上的阻礙，再做內容優化。
2. 一個頁面應該只有一個明確的主要搜尋意圖。
3. 優先看長期的品質訊號，不要用操弄式的手法。
4. 要以 mobile-first 為前提，因為索引是 mobile-first。
5. 建議要針對特定頁面，而且做得到。

### 技術 SEO 檢查清單

#### 可爬取性

- `robots.txt` 應該放行重要頁面，並擋掉低價值的區塊
- 不應該有重要頁面被意外設成 `noindex`
- 重要頁面應該在較淺的點擊深度內就能到達
- 避免超過兩跳的轉址鏈
- canonical 標籤應該自我一致，而且不要形成迴圈

#### 可索引性

- 偏好的 URL 格式應該一致
- 多語系頁面如果有用，需要正確的 hreflang
- sitemap 應該反映你想公開的範圍
- 不應該有重複的 URL 在沒有 canonical 控制下互相競爭

#### 效能

- LCP < 2.5s
- INP < 200ms
- CLS < 0.1
- 常見的修法：預載主視覺資源、減少會阻擋渲染的工作、預留版面空間、瘦身過重的 JS

#### 結構化資料

- 首頁：適合的話用 organization 或 business schema
- 編輯類頁面：`Article` / `BlogPosting`
- 商品頁：`Product` 和 `Offer`
- 內層頁面：`BreadcrumbList`
- 問答區塊：內容真的相符才用 `FAQPage`

### 頁面內規則

#### Title 標籤

- 目標大約 50 到 60 個字元
- 把主要關鍵字或概念放在前面
- 標題要讓人讀得懂，不要為了機器人塞滿關鍵字

#### Meta description

- 目標大約 120 到 160 個字元
- 誠實描述這個頁面
- 自然地帶入主要主題

#### 標題結構

- 一個清楚的 `H1`
- `H2` 和 `H3` 要反映真正的內容層級
- 不要只為了視覺樣式就跳過結構

### 關鍵字對應

1. 定義搜尋意圖
2. 蒐集貼近實際的關鍵字變體
3. 依意圖吻合度、可能的價值和競爭程度排優先順序
4. 一個主要關鍵字/主題對應一個 URL
5. 偵測並避免關鍵字自相蠶食

### 內部連結

- 從強勢頁面連到你想讓它排名的頁面
- 使用有描述性的錨點文字
- 能用更具體的錨點時，就避免泛用的錨點
- 新頁面要回頭補連結到相關的既有頁面

## 範例

### Title 公式

```text
Primary Topic - Specific Modifier | Brand
```

### Meta description 公式

```text
Action + topic + value proposition + one supporting detail
```

### JSON-LD 範例

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Page Title Here",
  "author": {
    "@type": "Person",
    "name": "Author Name"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Brand Name"
  }
}
```

### 稽核輸出格式

```text
[HIGH] Duplicate title tags on product pages
Location: src/routes/products/[slug].tsx
Issue: Dynamic titles collapse to the same default string, which weakens relevance and creates duplicate signals.
Fix: Generate a unique title per product using the product name and primary category.
```

## 反模式

| 反模式 | 修法 |
| --- | --- |
| 關鍵字堆砌 | 先為使用者而寫 |
| 單薄、近乎重複的頁面 | 合併或做出差異 |
| 為實際不存在的內容加 schema | 讓 schema 符合實際內容 |
| 沒看實際頁面就給內容建議 | 先讀真正的頁面 |
| 泛泛的「改善 SEO」輸出 | 每一條建議都要對應到某個頁面或資源 |

## 相關 Skill

- `seo-specialist`
- `frontend-patterns`
- `brand-voice`
- `market-research`
