---
name: shopify-setup
description: "為商店設定 Shopify CLI 驗證和 Admin API 存取。安裝 CLI、驗證、建立 custom app、儲存 access token、驗證連線。只要使用者想連接 Shopify 商店、設定 Shopify API 存取、安裝 Shopify CLI，或排查 Shopify 驗證 / Admin API token 問題，就用這個 skill。"
compatibility: claude-code-only
---

# Shopify Setup

為商店設定可用的 Shopify CLI 驗證和 Admin API 存取。產出一條驗證過的 API 連線，可以直接拿來管理商品和內容。

## 工作流程

### 步驟 1：檢查前置條件

確認 Shopify CLI 已安裝：

```bash
shopify version
```

沒裝的話：

```bash
npm install -g @shopify/cli
```

### 步驟 2：驗證商店身分

```bash
shopify auth login --store mystore.myshopify.com
```

這會開瀏覽器走 OAuth。使用者必須是店主，或有適當權限的員工。

登入後驗證：

```bash
shopify store info
```

### 步驟 3：建立 Custom App 以取得 API 存取

Custom app 提供穩定的 Admin API access token（不像 CLI session token 會過期）。

**先檢查 app 是否已存在**：問使用者有沒有設定過 custom app。有的話跳到步驟 4。

**如果還沒有 custom app**，引導使用者在瀏覽器裡建立：

1. 前往 `https://{store}.myshopify.com/admin/settings/apps/development`
2. 點 **Create an app**
3. 取個名字（例如 "Claude Code Integration"）
4. 點 **Configure Admin API scopes**
5. 啟用這些 scope（細節看 `references/api-scopes.md`）：
   - `read_products`、`write_products`
   - `read_content`、`write_content`
   - `read_product_listings`
   - `read_inventory`、`write_inventory`
   - `read_files`、`write_files`
6. 點 **Save**，再點 **Install app**
7. 複製 **Admin API access token**（只會顯示一次）

如果使用者希望有人協助操作後台，可以用瀏覽器自動化（Chrome MCP 或 playwright-cli）。

### 步驟 4：儲存 Access Token

安全地存好 token。絕對不要 commit 到 git。

**專案內使用**：建立 `.dev.vars`：

```
SHOPIFY_STORE=mystore.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_xxxxxxxxxxxxxxxxxxxxx
```

確認 `.dev.vars` 在 `.gitignore` 裡。

**跨專案使用**：存在你慣用的 secrets 管理工具（環境變數、1Password CLI 等）。

### 步驟 5：驗證 API 存取

用簡單的 GraphQL 查詢測試連線：

```bash
curl -s https://{store}.myshopify.com/admin/api/2025-01/graphql.json \
  -H "Content-Type: application/json" \
  -H "X-Shopify-Access-Token: {token}" \
  -d '{"query": "{ shop { name primaryDomain { url } } }"}' | jq .
```

預期回應會包含商店名稱和網域。如果拿到 401，代表 token 無效或過期，要重新建立 app。

### 步驟 6：儲存商店設定

在專案根目錄建立 `shopify.config.json`，讓其他 skill 參考：

```json
{
  "store": "mystore.myshopify.com",
  "apiVersion": "2025-01",
  "tokenSource": ".dev.vars"
}
```

---

## 關鍵模式

### API 版本

一定要指定明確的 API 版本（例如 `2025-01`）。在正式環境用 `unstable` 會無預警壞掉。Shopify 每季會淘汰舊的 API 版本。

### Token 類型

| Token | 格式 | 用途 |
|-------|--------|-----|
| Admin API access token | `shpat_*` | Custom app，穩定、長效 |
| CLI session token | 短效 | 只給 Shopify CLI 指令用 |
| Storefront API token | `shpca_*` | 公開的店面查詢 |

這個 skill 設定的是 **Admin API access token**，管理商品和內容用這個才對。

### Rate Limit

Shopify 用 leaky bucket 限流：
- **REST**：瞬間 40 req/秒，持續 2 req/秒
- **GraphQL**：每秒 1,000 cost points，單次查詢最多 2,000 points

大量操作時，用 `bulkOperationRunQuery` mutation，不要用迴圈。

---

## 參考檔案

- `references/api-scopes.md`：管理商品和內容所需的 Admin API scope
