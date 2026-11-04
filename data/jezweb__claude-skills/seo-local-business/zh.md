---
name: seo-local-business
description: "為在地商家網站產生完整的 SEO 設定：HTML head 標籤、JSON-LD LocalBusiness schema、robots.txt、sitemap.xml。針對澳洲最佳化，含 +61 電話、ABN、suburb 寫法。只要使用者想幫在地商家（水電工、咖啡店、診所、代理商、零售店）做 SEO、需要 JSON-LD 結構化資料、要 LocalBusiness schema，或要幫服務特定 suburb 的商家寫 meta 標籤 / robots.txt / sitemap，就用這個 skill。"
---

# SEO Local Business

為在地商家網站產生一整包 SEO 內容：meta 標籤、結構化資料、robots.txt 和 sitemap.xml。

## 產出內容

1. 完整的 `<head>` 區塊，含 meta 標籤、Open Graph、Twitter Cards
2. JSON-LD 結構化資料（LocalBusiness + Service + FAQ schema）
3. `robots.txt`
4. `sitemap.xml`

## 工作流程

### 步驟 1：收集商家資訊

向使用者詢問（或從現有網站擷取）：

| 必填 | 選填 |
|----------|----------|
| 商家名稱 | ABN |
| 主要服務 | 營業時間 |
| 地點（城市/suburb） | 社群媒體網址 |
| 電話號碼 | 價格區間 |
| 網站網址 | 服務範圍（suburb） |
| 商家簡介 | GPS 座標 |

### 步驟 2：產生 head 標籤

把這個模板的佔位符填好：

```html
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <!-- Primary Meta Tags -->
  <title>{{PAGE_TITLE}} | {{BUSINESS_NAME}}</title>
  <meta name="title" content="{{PAGE_TITLE}} | {{BUSINESS_NAME}}">
  <meta name="description" content="{{META_DESCRIPTION}}">

  <!-- Canonical URL -->
  <link rel="canonical" href="{{CANONICAL_URL}}">

  <!-- Open Graph / Facebook -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="{{CANONICAL_URL}}">
  <meta property="og:title" content="{{PAGE_TITLE}} | {{BUSINESS_NAME}}">
  <meta property="og:description" content="{{META_DESCRIPTION}}">
  <meta property="og:image" content="{{OG_IMAGE_URL}}">

  <!-- Twitter -->
  <meta property="twitter:card" content="summary_large_image">
  <meta property="twitter:url" content="{{CANONICAL_URL}}">
  <meta property="twitter:title" content="{{PAGE_TITLE}} | {{BUSINESS_NAME}}">
  <meta property="twitter:description" content="{{META_DESCRIPTION}}">
  <meta property="twitter:image" content="{{OG_IMAGE_URL}}">

  <!-- Geo Tags (Local SEO) -->
  <meta name="geo.region" content="{{GEO_REGION}}">
  <meta name="geo.placename" content="{{CITY}}">
  <meta name="geo.position" content="{{LATITUDE}};{{LONGITUDE}}">
  <meta name="ICBM" content="{{LATITUDE}}, {{LONGITUDE}}">

  <!-- Favicons -->
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png">
  <link rel="apple-touch-icon" href="apple-touch-icon.png">

  <!-- Structured Data -->
  <script type="application/ld+json">
    {{JSON_LD_SCHEMA}}
  </script>
</head>
```

**Title 標籤寫法**（最多 50-60 字元）：

| 頁面 | 格式 | 範例 |
|------|---------|---------|
| 首頁 | `Brand - Tagline` | `Newcastle Plumbing - 24/7 Emergency Service` |
| 服務頁 | `Service in Location \| Brand` | `Hot Water Repairs Newcastle \| ABC Plumbing` |
| 關於我們 | `About Us \| Brand` | `About Us \| ABC Plumbing Newcastle` |
| 聯絡我們 | `Contact \| Brand` | `Contact Us \| ABC Plumbing Newcastle` |

**Meta description 寫法**（150-160 字元）：

| 頁面 | 格式 |
|------|---------|
| 首頁 | `[USP]. [Service] in [Location]. [CTA]. Call [phone].` |
| 服務頁 | `Professional [service] in [location]. [Benefit]. [Trust signal]. Get a free quote today.` |
| 關於我們 | `[X] years serving [location]. [Team info]. [Credentials]. Learn about [brand].` |
| 聯絡我們 | `Contact [brand] for [service] in [location]. [Hours]. Call [phone] or request a quote online.` |

### 步驟 3：產生結構化資料

**LocalBusiness**（首頁，一定要放）：

用 `LocalBusiness`，或更具體的子類型：

| 子類型 | 適用於 |
|---------|---------|
| `Plumber` | 水管服務 |
| `Electrician` | 電工服務 |
| `RoofingContractor` | 屋頂工程 |
| `HVACBusiness` | 空調/暖氣 |
| `AutoRepair` | 汽車維修 |
| `BeautySalon` | 美髮/美容 |
| `Dentist` | 牙醫診所 |
| `LegalService` | 律師事務所 |
| `AccountingService` | 會計師 |
| `RealEstateAgent` | 房仲 |
| `Restaurant` | 餐廳/咖啡店 |
| `BarOrPub` | 酒吧 |
| `Hotel` | 住宿 |
| `Store` | 零售店 |
| `ProfessionalService` | 一般專業服務 |

LocalBusiness schema 屬性：

| 屬性 | 必填 | 備註 |
|----------|----------|-------|
| `@type` | 是 | `LocalBusiness` 或上面的子類型 |
| `name` | 是 | 顧客看到的商家名稱 |
| `image` | 是 | 商家主圖或 logo |
| `description` | 是 | 1-2 句商家簡介 |
| `@id` | 是 | 唯一 ID，用 `{url}/#organization` |
| `url` | 是 | 網站首頁網址 |
| `telephone` | 是 | 國際格式：`+61-2-4900-1234` |
| `address` | 是 | PostalAddress（見下方） |
| `email` | 建議 | 主要聯絡信箱 |
| `priceRange` | 建議 | `$` 到 `$$$$` |
| `geo` | 建議 | GeoCoordinates：經緯度 |
| `openingHoursSpecification` | 建議 | 見下方營業時間格式 |
| `areaServed` | 建議 | 服務的城市/suburb |
| `sameAs` | 建議 | 社群媒體個人檔案網址 |
| `taxID` | 選填 | 澳洲商家填 ABN |
| `logo` | 選填 | 商家 logo 網址 |
| `foundingDate` | 選填 | ISO 8601 日期 |
| `paymentAccepted` | 選填 | 例如 "Cash, Credit Card, EFTPOS" |
| `currenciesAccepted` | 選填 | `AUD` |

PostalAddress：

| 屬性 | 範例 |
|----------|---------|
| `streetAddress` | `123 Hunter Street` |
| `addressLocality` | `Newcastle` |
| `addressRegion` | `NSW` |
| `postalCode` | `2300` |
| `addressCountry` | `AU` |

範例：

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "ABC Plumbing Newcastle",
  "image": "https://www.abcplumbing.com.au/og-image.jpg",
  "description": "Professional plumbing services in Newcastle and Lake Macquarie.",
  "@id": "https://www.abcplumbing.com.au/#organization",
  "url": "https://www.abcplumbing.com.au",
  "telephone": "+61-2-4900-1234",
  "email": "info@abcplumbing.com.au",
  "priceRange": "$$",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Hunter Street",
    "addressLocality": "Newcastle",
    "addressRegion": "NSW",
    "postalCode": "2300",
    "addressCountry": "AU"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": -32.9283,
    "longitude": 151.7817
  },
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      "opens": "07:00",
      "closes": "17:00"
    },
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Saturday"],
      "opens": "08:00",
      "closes": "12:00"
    }
  ],
  "areaServed": [
    { "@type": "City", "name": "Newcastle" },
    { "@type": "City", "name": "Lake Macquarie" }
  ],
  "sameAs": [
    "https://www.facebook.com/abcplumbing",
    "https://www.instagram.com/abcplumbing"
  ]
}
```

**Service**（服務頁，每項服務各加一個）：

| 屬性 | 必填 | 備註 |
|----------|----------|-------|
| `name` | 是 | 服務名稱 |
| `description` | 是 | 這項服務提供什麼 |
| `provider` | 是 | `{ "@id": "{url}/#organization" }` |
| `areaServed` | 建議 | 城市或地區 |
| `serviceType` | 建議 | 服務類別 |
| `offers` | 選填 | 價格/供應狀況 |

```json
{
  "@context": "https://schema.org",
  "@type": "Service",
  "name": "Hot Water System Installation",
  "description": "Professional hot water system installation and replacement in Newcastle.",
  "provider": { "@id": "https://www.abcplumbing.com.au/#organization" },
  "areaServed": { "@type": "City", "name": "Newcastle" },
  "serviceType": "Plumbing",
  "offers": {
    "@type": "Offer",
    "availability": "https://schema.org/InStock",
    "priceRange": "$$"
  }
}
```

**FAQ**（有 FAQ 區塊的頁面）：

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How much does a plumber cost in Newcastle?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Plumber callout fees in Newcastle typically range from $80-150."
      }
    }
  ]
}
```

### 步驟 4：產生 robots.txt 和 sitemap.xml

**robots.txt：**

```
User-agent: *
Allow: /

Sitemap: {{SITE_URL}}/sitemap.xml
```

**sitemap.xml：**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{{SITE_URL}}/</loc>
    <lastmod>{{DATE}}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <!-- 每個頁面加一個 <url>。Priority：首頁 1.0、服務頁 0.8、其他 0.6 -->
</urlset>
```

### 步驟 5：驗證

結構化資料到這裡測試：https://validator.schema.org/

常見的驗證錯誤：
- 漏掉 `@context`：每個 JSON-LD 區塊都要有
- 電話格式錯誤：一定要用國際格式（`+61-...`）
- 漏掉 `@id`：schema 之間要互相參照時會用到
- `areaServed` 是空的：至少放一個城市

## 澳洲專用寫法

### 電話號碼

```html
<!-- Link: international format. Display: local format. -->
<a href="tel:+61249001234">(02) 4900 1234</a>
```

Schema 的 telephone：`"+61-2-4900-1234"`

| 前綴 | 國際格式 |
|--------|---------------|
| 02 | +612 |
| 04 | +614 |
| 1300 | 維持原樣 |

### ABN

有的話就加到 LocalBusiness schema：

```json
{ "taxID": "12 345 678 901" }
```

### 澳洲州代碼

| 州 | 代碼 | Geo Region |
|-------|------|------------|
| New South Wales | NSW | AU-NSW |
| Victoria | VIC | AU-VIC |
| Queensland | QLD | AU-QLD |
| South Australia | SA | AU-SA |
| Western Australia | WA | AU-WA |
| Tasmania | TAS | AU-TAS |
| Northern Territory | NT | AU-NT |
| ACT | ACT | AU-ACT |

### 服務範圍

`areaServed` 用澳洲的城市和 suburb 名稱（見上面的 LocalBusiness 範例）。
