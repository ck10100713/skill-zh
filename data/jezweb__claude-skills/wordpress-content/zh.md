---
name: wordpress-content
description: "透過 WP-CLI 或 REST API 建立並管理 WordPress 的文章、頁面、媒體、分類、標籤和選單。只要使用者想在 WordPress 發布部落格文章、更新頁面、上傳媒體、管理分類或標籤、更新導覽選單、排程文章，或對 WordPress 網站做大量內容操作，就用這個 skill。"
compatibility: claude-code-only
---

# WordPress Content

建立、更新並管理 WordPress 內容：文章、頁面、媒體、分類、標籤和選單。透過 WP-CLI 或 REST API，直接在網站上產生上線的內容。

## 前置條件

- 可用的 WP-CLI SSH 連線，或 REST API 憑證（用 **wordpress-setup** skill）
- 來自 `wordpress.config.json` 或 `wp-cli.yml` 的網站設定

## 工作流程

### 步驟 1：判斷操作類型

| 任務 | 最佳方法 |
|------|-------------|
| 建立/編輯單一文章或頁面 | WP-CLI `wp post create/update` |
| 大量建立文章 | WP-CLI 迴圈或 REST API batch |
| 上傳圖片/媒體 | WP-CLI `wp media import` |
| 管理分類/標籤 | WP-CLI `wp term` |
| 更新導覽選單 | WP-CLI `wp menu` |
| 排程文章 | WP-CLI 加上 `--post_date` |
| 複雜的 HTML 內容 | 寫到暫存檔，再傳給 WP-CLI |
| 沒有 SSH 可用 | 用 Application Password 的 REST API |

### 步驟 2：建立內容

#### 部落格文章

```bash
# Simple post
wp @site post create \
  --post_type=post \
  --post_title="My New Blog Post" \
  --post_content="<p>Post content here.</p>" \
  --post_status=draft \
  --post_category=3,5

# Post from HTML file (better for long content)
wp @site post create ./post-content.html \
  --post_type=post \
  --post_title="My New Blog Post" \
  --post_status=draft \
  --post_excerpt="A brief summary of the post." \
  --post_category=3,5 \
  --tags_input="tag1,tag2"
```

**文章狀態**：`draft`、`publish`、`pending`、`future`（搭配 `--post_date` 使用）

#### 頁面

```bash
wp @site post create \
  --post_type=page \
  --post_title="About Us" \
  --post_content="<h2>Our Story</h2><p>Content here...</p>" \
  --post_status=publish \
  --post_parent=0 \
  --menu_order=10
```

#### 排程文章

```bash
wp @site post create \
  --post_type=post \
  --post_title="Scheduled Post" \
  --post_content="<p>This goes live tomorrow.</p>" \
  --post_status=future \
  --post_date="2026-02-23 09:00:00"
```

### 步驟 3：上傳媒體

```bash
# Upload from URL
wp @site media import "https://example.com/image.jpg" \
  --title="Product Photo" \
  --alt="Product front view" \
  --caption="Our latest product"

# Upload from local file (requires SCP first for remote sites)
scp ./image.jpg user@host:/tmp/image.jpg
wp @site media import /tmp/image.jpg --title="Local Upload"

# Import and set as featured image in one step
wp @site media import "https://example.com/hero.jpg" \
  --title="Hero" --featured_image --post_id={id}

# List media
wp @site post list --post_type=attachment --fields=ID,post_title,guid

# Regenerate thumbnails
wp @site media regenerate --yes
```

**替文章設定特色圖片**：

```bash
# Get the attachment ID from the import output, then:
wp @site post meta update {post_id} _thumbnail_id {attachment_id}
```

### 步驟 4：管理 Taxonomy

#### 分類

```bash
# List categories
wp @site term list category --fields=term_id,name,slug,count

# Create category
wp @site term create category "News" --slug=news --description="Company news and updates"

# Create child category
wp @site term create category "Product News" --slug=product-news --parent=5

# Update category
wp @site term update category {term_id} --name="Updated Name"

# Assign category to post
wp @site post term add {post_id} category news
```

#### 標籤

```bash
# List tags
wp @site term list post_tag --fields=term_id,name,slug,count

# Create tag
wp @site term create post_tag "new-tag"

# Add tags during post creation
wp @site post create --post_title="..." --tags_input="seo,marketing,tips"

# Add tags to existing post
wp @site post term add {post_id} post_tag seo marketing tips
```

### 步驟 5：管理選單

```bash
# List menus
wp @site menu list --fields=term_id,name,slug,count

# List items in a menu
wp @site menu item list main-menu --fields=db_id,type,title,link,position

# Add page to menu
wp @site menu item add-post main-menu {page_id} --title="About Us"

# Add custom link
wp @site menu item add-custom main-menu "Contact" "https://example.com/contact/"

# Add category archive to menu
wp @site menu item add-term main-menu category {term_id}

# Reorder (set position)
wp @site menu item update {item_id} --position=3

# Delete menu item
wp @site menu item delete {item_id}
```

### 步驟 6：更新既有內容

```bash
# Update post title and content
wp @site post update {post_id} \
  --post_title="Updated Title" \
  --post_content="<p>New content.</p>"

# Update from file
wp @site post update {post_id} ./updated-content.html

# Search posts
wp @site post list --s="search term" --fields=ID,post_title

# Bulk update status
wp @site post list --post_type=post --post_status=draft --field=ID | \
  xargs -I {} wp @site post update {} --post_status=publish

# Delete (trash)
wp @site post delete {post_id}

# Delete permanently
wp @site post delete {post_id} --force
```

### 步驟 7：文章 Meta 與自訂欄位

```bash
# Get all meta for a post
wp @site post meta list {post_id} --fields=meta_key,meta_value

# Get specific meta
wp @site post meta get {post_id} meta_key

# Set meta
wp @site post meta update {post_id} meta_key "meta_value"

# Add meta (allows duplicates)
wp @site post meta add {post_id} meta_key "meta_value"

# Delete meta
wp @site post meta delete {post_id} meta_key
```

ACF 會同時儲存欄位的值和一個參照 key（`_field_name` -> `field_abc123`）。

### 步驟 8：搜尋與取代

```bash
# Dry run first — always
wp @site search-replace "old text" "new text" --dry-run

# Execute
wp @site search-replace "old text" "new text" --precise

# Limit to specific table
wp @site search-replace "old" "new" wp_posts --precise

# Limit to specific column
wp @site search-replace "old" "new" wp_posts post_content --precise
```

### 步驟 9：匯出與匯入

```bash
# Export all content
wp @site export --dir=/tmp/

# Export specific post type
wp @site export --post_type=post --dir=/tmp/

# Import
wp @site import /path/to/file.xml --authors=mapping.csv
```

### 步驟 10：驗證

```bash
# Check the post
wp @site post get {post_id} --fields=ID,post_title,post_status,guid

# Get the live URL
wp @site post get {post_id} --field=guid

# List recent posts
wp @site post list --post_type=post --posts_per_page=5 --fields=ID,post_title,post_status,post_date
```

提供後台網址和前台網址：
- 後台：`https://example.com/wp-admin/post.php?post={id}&action=edit`
- 前台：`https://example.com/{slug}/`

---

## REST API 參考

沒有 WP-CLI 時，使用 WordPress REST API 搭配 Application Password 驗證。

### 驗證

```bash
# Base64 encode credentials
AUTH=$(echo -n "username:xxxx xxxx xxxx xxxx xxxx xxxx" | base64)

# Use in requests
curl -s https://example.com/wp-json/wp/v2/posts \
  -H "Authorization: Basic $AUTH" \
  -H "Content-Type: application/json"
```

### Endpoint

| 資源 | Endpoint |
|----------|----------|
| 文章 | `/wp-json/wp/v2/posts` |
| 頁面 | `/wp-json/wp/v2/pages` |
| 媒體 | `/wp-json/wp/v2/media` |
| 分類 | `/wp-json/wp/v2/categories` |
| 標籤 | `/wp-json/wp/v2/tags` |

全部都支援 GET（列表/單筆）、POST（建立）、PUT（更新）、DELETE。

### 透過 REST 建立文章

```bash
curl -s https://example.com/wp-json/wp/v2/posts \
  -H "Authorization: Basic $AUTH" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My New Post",
    "content": "<p>Post content here.</p>",
    "status": "draft",
    "categories": [3, 5],
    "tags": [10, 12],
    "excerpt": "Brief summary",
    "featured_media": 456
  }' | jq '{id, link, status}'
```

### 透過 REST 建立頁面

```bash
curl -s https://example.com/wp-json/wp/v2/pages \
  -H "Authorization: Basic $AUTH" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "About Us",
    "content": "<h2>Our Story</h2><p>Content...</p>",
    "status": "publish",
    "parent": 0
  }'
```

### 透過 REST 上傳媒體

```bash
curl -s https://example.com/wp-json/wp/v2/media \
  -H "Authorization: Basic $AUTH" \
  -H "Content-Disposition: attachment; filename=photo.jpg" \
  -H "Content-Type: image/jpeg" \
  --data-binary @photo.jpg | jq '{id, source_url}'
```

### 透過 REST 建立分類

```bash
curl -s https://example.com/wp-json/wp/v2/categories \
  -H "Authorization: Basic $AUTH" \
  -H "Content-Type: application/json" \
  -d '{"name": "News", "slug": "news", "description": "Company updates"}'
```

### 查詢參數

| 參數 | 用途 | 範例 |
|-----------|---------|---------|
| `per_page` | 每頁結果數（最多 100） | `?per_page=50` |
| `page` | 分頁 | `?page=2` |
| `search` | 搜尋詞 | `?search=keyword` |
| `status` | 依狀態篩選 | `?status=draft` |
| `categories` | 依分類 ID 篩選 | `?categories=3` |
| `orderby` | 排序欄位 | `?orderby=date` |
| `order` | 排序方向 | `?order=desc` |
| `_fields` | 限制回傳的欄位 | `?_fields=id,title,link` |

**選單**：導覽選單的 REST API 支援有限。`/wp-json/wp/v2/navigation` endpoint 是給 FSE 主題的區塊式導覽用的。傳統選單請用 WP-CLI。

---

## 關鍵模式

### WP-CLI 裡的 HTML 內容

超過一句話的內容，就把 HTML 寫到暫存檔再傳進去：

```bash
cat > /tmp/post-content.html << 'EOF'
<h2>Section Heading</h2>
<p>Paragraph content with <strong>bold</strong> and <a href="/link">links</a>.</p>
<ul>
  <li>List item one</li>
  <li>List item two</li>
</ul>
EOF

wp @site post create /tmp/post-content.html --post_title="My Post" --post_status=draft
```

複雜的 HTML 放在 `--post_content` 裡，shell 的引號處理很脆弱。

### 大量操作

要建立很多文章時，用迴圈並做驗證：

```bash
while IFS=, read -r title slug content_file category; do
  wp @site post create "$content_file" \
    --post_type=post \
    --post_title="$title" \
    --post_name="$slug" \
    --post_category="$category" \
    --post_status=draft
  sleep 0.5
done < posts.csv
```

一定要先以 `draft` 建立，檢查過後再大量發布。
