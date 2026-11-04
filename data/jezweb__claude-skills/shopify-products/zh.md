---
name: shopify-products
description: "透過 Admin GraphQL API 或 CSV 匯入，建立並管理 Shopify 商品。流程：收集資料、選方法、執行、驗證。只要使用者想新增商品到 Shopify、從 CSV/試算表/網址大量匯入商品目錄、更新 variant 或價格、管理庫存數量、上傳商品圖片，或把商品加進 collection，就用這個 skill。"
compatibility: claude-code-only
---

# Shopify Products

建立、更新、大量匯入 Shopify 商品。透過 GraphQL Admin API 或 CSV 匯入，直接在商店產生上線的商品。

## 前置條件

- Admin API access token（還沒設定的話，用 **shopify-setup** skill）
- 從 `shopify.config.json` 或 `.dev.vars` 取得商店網址和 API 版本

## 工作流程

### 步驟 1：收集商品資料

判斷使用者想建立或更新什麼：

- **商品基本資料**：標題、描述（HTML）、商品類型、vendor、tag
- **Variant**：選項（尺寸、顏色、材質）、價格、SKU、庫存數量
- **圖片**：要上傳的網址，或本機檔案
- **SEO**：頁面標題、meta description、URL handle
- **組織方式**：collection、商品類型、tag

資料來源可以是：
- 直接對話（使用者描述商品）
- 試算表/CSV 檔案（使用者提供檔案）
- 網站爬取（使用者給網址讓你擷取）

### 步驟 2：選方法

| 情境 | 方法 |
|----------|--------|
| 1-5 個商品 | GraphQL mutation |
| 6-20 個商品 | GraphQL 搭配分批 |
| 20 個以上 | 透過後台做 CSV 匯入 |
| 更新既有商品 | GraphQL mutation |
| 調整庫存 | `inventorySetQuantities` mutation |

---

### 步驟 3a：用 GraphQL 建立（建議）

#### productCreate

```graphql
mutation productCreate($product: ProductCreateInput!) {
  productCreate(product: $product) {
    product {
      id
      title
      handle
      status
      variants(first: 100) {
        edges {
          node { id title price sku inventoryQuantity }
        }
      }
    }
    userErrors { field message }
  }
}
```

Variables：

```json
{
  "product": {
    "title": "Example T-Shirt",
    "descriptionHtml": "<p>Premium cotton tee</p>",
    "vendor": "My Brand",
    "productType": "T-Shirts",
    "tags": ["summer", "cotton"],
    "status": "DRAFT",
    "options": ["Size", "Colour"],
    "variants": [
      {
        "optionValues": [
          {"optionName": "Size", "name": "S"},
          {"optionName": "Colour", "name": "Black"}
        ],
        "price": "29.95",
        "sku": "TSHIRT-S-BLK",
        "inventoryPolicy": "DENY",
        "inventoryItem": { "tracked": true }
      },
      {
        "optionValues": [
          {"optionName": "Size", "name": "M"},
          {"optionName": "Colour", "name": "Black"}
        ],
        "price": "29.95",
        "sku": "TSHIRT-M-BLK"
      },
      {
        "optionValues": [
          {"optionName": "Size", "name": "L"},
          {"optionName": "Colour", "name": "Black"}
        ],
        "price": "29.95",
        "sku": "TSHIRT-L-BLK"
      }
    ],
    "seo": {
      "title": "Example T-Shirt | My Brand",
      "description": "Premium cotton tee in multiple sizes"
    }
  }
}
```

curl 範例：

```bash
curl -s https://{store}/admin/api/2025-01/graphql.json \
  -H "Content-Type: application/json" \
  -H "X-Shopify-Access-Token: {token}" \
  -d '{"query": "mutation productCreate($product: ProductCreateInput!) { productCreate(product: $product) { product { id title } userErrors { field message } } }", "variables": { ... }}'
```

**分批建立多個商品**：依序建立商品，每個之間稍微等一下，以符合 rate limit（每秒 1,000 cost points）。

#### productUpdate

```graphql
mutation productUpdate($input: ProductInput!) {
  productUpdate(input: $input) {
    product { id title }
    userErrors { field message }
  }
}
```

Variables 要包含 `id`（必填），再加上要更新的欄位。

#### productDelete

```graphql
mutation productDelete($input: ProductDeleteInput!) {
  productDelete(input: $input) {
    deletedProductId
    userErrors { field message }
  }
}
```

#### productVariantsBulkCreate

替既有商品新增 variant：

```graphql
mutation productVariantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
  productVariantsBulkCreate(productId: $productId, variants: $variants) {
    productVariants { id title price }
    userErrors { field message }
  }
}
```

#### productVariantsBulkUpdate

```graphql
mutation productVariantsBulkUpdate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
  productVariantsBulkUpdate(productId: $productId, variants: $variants) {
    productVariants { id title price }
    userErrors { field message }
  }
}
```

---

### 步驟 3b：用 CSV 大量匯入

20 個以上的商品，產生 CSV 再透過 Shopify 後台匯入。

#### CSV 欄位參考

**必填欄位：**

| 欄位 | 說明 | 範例 |
|--------|-------------|---------|
| `Handle` | URL slug（每個商品唯一） | `classic-tshirt` |
| `Title` | 商品名稱（每個商品的第一列） | `Classic T-Shirt` |
| `Body (HTML)` | HTML 格式的描述 | `<p>Premium cotton</p>` |
| `Vendor` | 品牌或製造商 | `My Brand` |
| `Product Category` | Shopify 標準分類 | `Apparel & Accessories > Clothing > Shirts & Tops` |
| `Type` | 自訂商品類型 | `T-Shirts` |
| `Tags` | 用逗號分隔的 tag | `summer, cotton, casual` |
| `Published` | 商品是否可見 | `TRUE` 或 `FALSE` |

**Variant 欄位：**

| 欄位 | 說明 | 範例 |
|--------|-------------|---------|
| `Option1 Name` | 第一個選項名稱 | `Size` |
| `Option1 Value` | 第一個選項值 | `Medium` |
| `Option2 Name` | 第二個選項名稱 | `Colour` |
| `Option2 Value` | 第二個選項值 | `Black` |
| `Option3 Name` | 第三個選項名稱 | `Material` |
| `Option3 Value` | 第三個選項值 | `Cotton` |
| `Variant SKU` | 庫存單位編號 | `TSHIRT-M-BLK` |
| `Variant Grams` | 重量（公克） | `200` |
| `Variant Inventory Qty` | 庫存數量 | `50` |
| `Variant Price` | Variant 價格 | `29.95` |
| `Variant Compare At Price` | 原價（用於特價） | `39.95` |
| `Variant Requires Shipping` | 是否為實體商品 | `TRUE` |
| `Variant Taxable` | 是否課稅 | `TRUE` |

**圖片欄位：**

| 欄位 | 說明 | 範例 |
|--------|-------------|---------|
| `Image Src` | 圖片網址 | `https://example.com/img.jpg` |
| `Image Position` | 顯示順序（從 1 開始） | `1` |
| `Image Alt Text` | 無障礙用的 alt text | `Classic T-Shirt front view` |

**SEO 欄位：**

| 欄位 | 說明 | 範例 |
|--------|-------------|---------|
| `SEO Title` | 頁面 title 標籤 | `Classic T-Shirt | My Brand` |
| `SEO Description` | Meta description | `Premium cotton tee in 5 colours` |

#### 多 variant 的列格式

第一列放商品標題和詳細資料。同一商品的後續列只放 `Handle` 和 variant 專屬的欄位：

```csv
Handle,Title,Body (HTML),Vendor,Type,Tags,Published,Option1 Name,Option1 Value,Variant SKU,Variant Price,Variant Inventory Qty,Image Src
classic-tshirt,Classic T-Shirt,<p>Premium cotton</p>,My Brand,T-Shirts,"summer,cotton",TRUE,Size,Small,TSH-S,29.95,50,https://example.com/tshirt.jpg
classic-tshirt,,,,,,,,Medium,TSH-M,29.95,75,
classic-tshirt,,,,,,,,Large,TSH-L,29.95,60,
```

#### CSV 規則

- 一定要 UTF-8 編碼
- 檔案最大 50MB
- Handle 每個商品必須唯一。重複的 handle 會更新既有商品
- Variant 列裡沒有變動的欄位留空
- 圖片可以放在任何一列，會用 Handle 關聯起來
- `Published` = `TRUE` 會讓商品立刻可見

#### 匯入步驟

1. 用上面的欄位格式產生 CSV
2. 有的話，用 `assets/product-csv-template.csv` 的模板
3. 前往 `https://{store}.myshopify.com/admin/products/import`
4. 上傳 CSV 檔案
5. 檢查預覽，確認匯入

需要的話，可以用瀏覽器自動化協助上傳。

---

### 步驟 4：上傳商品圖片

圖片要分兩步：先 staged upload，再 attach。

#### stagedUploadsCreate

```graphql
mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
  stagedUploadsCreate(input: $input) {
    stagedTargets {
      url
      resourceUrl
      parameters { name value }
    }
    userErrors { field message }
  }
}
```

每個檔案的 input：

```json
{
  "filename": "product-image.jpg",
  "mimeType": "image/jpeg",
  "httpMethod": "POST",
  "resource": "IMAGE"
}
```

接著上傳到 staged URL，再用 `productCreateMedia` attach：

#### productCreateMedia

```graphql
mutation productCreateMedia($productId: ID!, $media: [CreateMediaInput!]!) {
  productCreateMedia(productId: $productId, media: $media) {
    media { alt status }
    mediaUserErrors { field message }
  }
}
```

**捷徑**：如果圖片已經放在公開網址，建立商品時直接傳 `src` 就好：

```json
{
  "images": [
    { "src": "https://example.com/image.jpg", "alt": "Product front view" }
  ]
}
```

---

### 步驟 5：加進 collection

#### collectionAddProducts

```graphql
mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
  collectionAddProducts(id: $id, productIds: $productIds) {
    collection { title productsCount }
    userErrors { field message }
  }
}
```

找 collection ID：

```graphql
{
  collections(first: 50) {
    edges {
      node { id title handle productsCount }
    }
  }
}
```

---

### 步驟 6：設定庫存

#### inventorySetQuantities

```graphql
mutation inventorySetQuantities($input: InventorySetQuantitiesInput!) {
  inventorySetQuantities(input: $input) {
    inventoryAdjustmentGroup { reason }
    userErrors { field message }
  }
}
```

Input：

```json
{
  "reason": "correction",
  "name": "available",
  "quantities": [{
    "inventoryItemId": "gid://shopify/InventoryItem/123",
    "locationId": "gid://shopify/Location/456",
    "quantity": 50
  }]
}
```

找 location ID：

```graphql
{
  locations(first: 10) {
    edges {
      node { id name isActive }
    }
  }
}
```

---

### 步驟 7：驗證

把建立好的商品查回來確認：

```graphql
{
  products(first: 50) {
    edges {
      node {
        id title handle status productType vendor
        variants(first: 10) {
          edges { node { id title price sku inventoryQuantity } }
        }
        images(first: 3) { edges { node { url altText } } }
      }
    }
    pageInfo { hasNextPage endCursor }
  }
}
```

提供後台網址讓使用者檢查：`https://{store}.myshopify.com/admin/products`

---

## 關鍵模式

### 商品狀態

新商品預設是 `DRAFT`。要讓它可見：

```json
{ "status": "ACTIVE" }
```

把狀態設成 `ACTIVE` 之前，一定要先跟使用者確認。

### Variant 上限

Shopify 每個商品最多 **100 個 variant**、**3 個選項**（例如 Size、Colour、Material）。需要更多的話，拆成不同商品。

### 價格格式

價格是字串，不是數字。一定要加引號：`"price": "29.95"`，不是 `"price": 29.95`。

### HTML 描述

商品描述接受 HTML。保持簡單，Shopify 的編輯器只處理基本標籤：
- `<p>`、`<strong>`、`<em>`、`<ul>`、`<ol>`、`<li>`、`<h2>`-`<h6>`
- 連結用 `<a href="...">`
- `<img>` 會被移除，請改用商品圖片

### 大量匯入用 Bulk Operation

透過 API 匯入 50 個以上的商品時，用 Shopify 的 bulk operation：

```graphql
mutation {
  bulkOperationRunMutation(
    mutation: "mutation ($input: ProductInput!) { productCreate(input: $input) { product { id } userErrors { message } } }"
    stagedUploadPath: "tmp/bulk-products.jsonl"
  ) {
    bulkOperation { id status }
    userErrors { message }
  }
}
```

這個接受 JSONL 檔案，一行一個商品，非同步處理。

---

## 資產檔案

- `assets/product-csv-template.csv`：空白的 CSV 模板，含 Shopify 匯入用的標頭
