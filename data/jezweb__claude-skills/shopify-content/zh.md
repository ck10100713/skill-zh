---
name: shopify-content
description: "透過 Admin API 或瀏覽器自動化，建立並管理 Shopify 的頁面、部落格文章、導覽選單、redirect 和 SEO metadata。只要使用者想在 Shopify 商店新增頁面、寫 Shopify 部落格文章、更新店面導覽、管理 redirect，或調整 Shopify 網站的 SEO metadata，就用這個 skill。"
compatibility: claude-code-only
---

# Shopify Content

建立並管理 Shopify 商店的內容：頁面、部落格文章、導覽選單和 SEO metadata。透過 Admin API 或瀏覽器自動化，直接在商店產生上線的內容。

## 前置條件

- 有 `read_content`、`write_content` scope 的 Admin API access token（用 **shopify-setup** skill 取得）
- 導覽選單需要：`read_online_store_navigation`、`write_online_store_navigation` scope

## 工作流程

### 步驟 1：判斷內容類型

| 內容類型 | API 支援 | 方法 |
|-------------|-------------|--------|
| 頁面 | 完整 | GraphQL Admin API |
| 部落格文章 | 完整 | GraphQL Admin API |
| 導覽選單 | 有限 | 優先用瀏覽器自動化 |
| Redirect | 完整 | REST Admin API |
| SEO metadata | 依資源而定 | 對該資源下 GraphQL |
| Metaobject | 完整 | GraphQL Admin API |

### 步驟 2a：建立頁面

```bash
curl -s https://{store}/admin/api/2025-01/graphql.json \
  -H "Content-Type: application/json" \
  -H "X-Shopify-Access-Token: {token}" \
  -d '{
    "query": "mutation pageCreate($page: PageCreateInput!) { pageCreate(page: $page) { page { id title handle } userErrors { field message } } }",
    "variables": {
      "page": {
        "title": "About Us",
        "handle": "about",
        "body": "<h2>Our Story</h2><p>Content here...</p>",
        "isPublished": true,
        "seo": {
          "title": "About Us | Store Name",
          "description": "Learn about our story and mission."
        }
      }
    }
  }'
```

**頁面 body** 接受 HTML。保持語意化：
- 標題用 `<h2>` 到 `<h6>`（頁面標題本身是 `<h1>`）
- 內文用 `<p>`、`<ul>`、`<ol>`
- 連結用 `<a href="...">`
- 避免 inline style，樣式交給 theme 處理

### 步驟 2b：建立部落格文章

Shopify 部落格是兩層結構：**Blog**（容器）> **Article**（文章）。

**找到或建立 blog**：

```graphql
{
  blogs(first: 10) {
    edges {
      node { id title handle }
    }
  }
}
```

多數商店都有一個預設的 blog，叫 "News"。在裡面建立文章：

```graphql
mutation {
  articleCreate(article: {
    blogId: "gid://shopify/Blog/123"
    title: "New Product Launch"
    handle: "new-product-launch"
    contentHtml: "<p>We're excited to announce...</p>"
    author: { name: "Store Team" }
    tags: ["news", "products"]
    isPublished: true
    publishDate: "2026-02-22T00:00:00Z"
    seo: {
      title: "New Product Launch | Store Name"
      description: "Announcing our latest product range."
    }
    image: {
      src: "https://example.com/blog-image.jpg"
      altText: "New product collection"
    }
  }) {
    article { id title handle }
    userErrors { field message }
  }
}
```

### 步驟 2c：更新導覽選單

導覽選單的 API 支援有限，用瀏覽器自動化：

1. 前往 `https://{store}.myshopify.com/admin/menus`
2. 選要編輯的選單（通常是 "Main menu" 或 "Footer menu"）
3. 新增、重新排序或移除選單項目
4. 儲存變更

或者，如果 API 版本支援，可以用 GraphQL 的 `menuUpdate` mutation：

```graphql
mutation menuUpdate($id: ID!, $items: [MenuItemInput!]!) {
  menuUpdate(id: $id, items: $items) {
    menu { id title }
    userErrors { field message }
  }
}
```

### 步驟 2d：建立 redirect

URL redirect 用 REST API：

```bash
curl -s https://{store}/admin/api/2025-01/redirects.json \
  -H "Content-Type: application/json" \
  -H "X-Shopify-Access-Token: {token}" \
  -d '{
    "redirect": {
      "path": "/old-page",
      "target": "/new-page"
    }
  }'
```

### 步驟 2e：更新 SEO metadata

SEO 欄位在各個資源上（商品、頁面、文章）。用該資源的 mutation 更新：

```graphql
mutation {
  pageUpdate(page: {
    id: "gid://shopify/Page/123"
    seo: {
      title: "Updated SEO Title"
      description: "Updated meta description under 160 chars."
    }
  }) {
    page { id title }
    userErrors { field message }
  }
}
```

### 步驟 3：驗證

把內容查回來確認：

```graphql
{
  pages(first: 10, reverse: true) {
    edges {
      node { id title handle isPublished createdAt }
    }
  }
}
```

提供後台網址和前台網址讓使用者檢查：
- 後台：`https://{store}.myshopify.com/admin/pages`
- 前台：`https://{store}.myshopify.com/pages/{handle}`

---

## 關鍵模式

### 頁面 vs Metaobject

簡單內容（關於我們、聯絡、FAQ）用 **page**。結構化、會重複出現的內容（團隊成員、顧客評價、據點）用 **metaobject**，它有型別化的欄位，也能用程式查詢。

### 部落格 SEO

每篇部落格文章都要有：
- **SEO title**：60 字元以內，含主要關鍵字
- **Meta description**：160 字元以內，有吸引力的摘要
- **Handle**：乾淨、含關鍵字的 URL slug
- **有 alt text 的圖片**：給社群分享和無障礙使用

### 排程發布

文章用 `publishDate` 做排程發布。頁面在 `isPublished: true` 時會立刻發布。

### 大量內容

要建很多頁面（例如據點頁、服務頁）時，用迴圈並控制呼叫頻率：

```bash
for page in pages_data:
    create_page(page)
    sleep(0.5)  # Respect rate limits
```

---

## 參考檔案

- `references/content-types.md`：API endpoint、metaobject 模式，以及只能用瀏覽器做的操作
