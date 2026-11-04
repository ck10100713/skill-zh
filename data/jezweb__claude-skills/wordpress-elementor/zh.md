---
name: wordpress-elementor
description: "透過瀏覽器自動化（用於視覺/結構上的變更）或 WP-CLI（用於安全的文字取代），在 WordPress 網站上編輯 Elementor 頁面並管理 template。只要使用者想編輯 Elementor 頁面、更新 Elementor widget 裡的文字、套用或管理 Elementor template，或對用 Elementor 頁面編輯器建的頁面做內容變更，就用這個 skill。"
compatibility: claude-code-only
---

# WordPress Elementor

在既有的 WordPress 網站上編輯 Elementor 頁面並管理 template。透過瀏覽器自動化（用於視覺/結構上的變更）或 WP-CLI（用於安全的文字取代）產出更新後的頁面內容。

## 前置條件

- 可用的 WP-CLI 連線或後台存取權（用 **wordpress-setup** skill）
- 已安裝並啟用 Elementor：`wp @site plugin status elementor`

## 工作流程

### 步驟 1：找出頁面

```bash
# List Elementor pages
wp @site post list --post_type=page --meta_key=_elementor_edit_mode --meta_value=builder \
  --fields=ID,post_title,post_name,post_status

# Editor URL format: https://example.com/wp-admin/post.php?post={ID}&action=elementor
```

### 步驟 2：選擇編輯方法

| 變更類型 | 方法 | 風險 |
|-------------|--------|------|
| 文字內容更新 | WP-CLI search-replace | 低（有備份的話） |
| 圖片 URL 替換 | WP-CLI meta update | 低（有備份的話） |
| Widget 樣式 | 瀏覽器自動化 | 無 |
| 新增/移除區塊 | 瀏覽器自動化 | 無 |
| 版面變更 | 瀏覽器自動化 | 無 |
| 套用 template | 瀏覽器自動化 | 無 |

**經驗法則**：如果只是改既有 widget 裡的文字或 URL，WP-CLI 比較快。任何結構上的變更，就透過瀏覽器用視覺編輯器。

### 步驟 3a：透過 WP-CLI 更新文字

**一定要先備份**：

```bash
wp @site post meta get {post_id} _elementor_data > /tmp/elementor-backup-{post_id}.json
```

**事前檢查清單**：

1. 備份 postmeta（如上）
2. 先 dry run 取代
3. 確認 dry run 的結果符合預期（取代的次數正確）
4. 執行
5. 清除 CSS 快取
6. 用肉眼確認

**簡單的文字取代**：

```bash
# Dry run
wp @site search-replace "Old Heading Text" "New Heading Text" wp_postmeta \
  --include-columns=meta_value --dry-run --precise

# Execute (after confirming dry run looks correct)
wp @site search-replace "Old Heading Text" "New Heading Text" wp_postmeta \
  --include-columns=meta_value --precise
```

**更新之後**，清除 Elementor 的 CSS 快取：

```bash
wp @site elementor flush-css
```

如果沒有 `elementor` 這個 WP-CLI 指令：

```bash
wp @site option delete _elementor_global_css
wp @site post meta delete-all _elementor_css
```

**哪些可以安全取代**：

| 安全 | 有風險 |
|------|-------|
| 標題文字 | HTML 結構 |
| 段落文字 | Widget ID |
| 按鈕文字與 URL | Section/column 設定 |
| 圖片 URL（尺寸相同） | 版面屬性 |
| 電話號碼、email | CSS class |
| 地址 | 元素順序 |

### 步驟 3b：透過瀏覽器自動化做視覺編輯

結構上的變更，用瀏覽器自動化操作 Elementor 的視覺編輯器。

**登入流程**（如果已經透過 Chrome MCP 登入就跳過）：

1. 前往 `https://example.com/wp-admin/`
2. 輸入使用者名稱和密碼
3. 點 "Log In"
4. 等待 dashboard 載入

**開啟編輯器**：

1. 前往 `https://example.com/wp-admin/post.php?post={ID}&action=elementor`
2. 等待 Elementor 的載入遮罩消失（可能要 5-10 秒）
3. 左側邊欄出現 widget 面板時，編輯器就準備好了

**編輯文字內容**：

1. 在頁面預覽（右側面板）裡點文字元素
2. 元素會被選取（藍色邊框）
3. 左側邊欄會顯示該元素的設定
4. 在 "Content" tab 下，編輯編輯器欄位裡的文字
5. 變更會即時顯示在預覽中
6. 點 "Update"（綠色按鈕，左下角）或按 Ctrl+S

**編輯標題**：

1. 在預覽中點標題
2. 左側邊欄 > Content tab > "Title" 欄位
3. 編輯文字
4. 可選擇調整：HTML 標籤（H1-H6）、對齊、連結
5. 儲存

**更換圖片**：

1. 在預覽中點圖片 widget
2. 左側邊欄 > Content tab > 點圖片縮圖
3. 媒體庫會開啟
4. 選擇新圖片或上傳
5. 點 "Insert Media"
6. 儲存

**編輯按鈕**：

1. 在預覽中點按鈕
2. 左側邊欄 > Content tab：Text（標籤）、Link（URL）、Icon（選用）
3. Style tab：顏色、字型、邊框、padding
4. 儲存

**使用 playwright-cli**：

```bash
playwright-cli -s=wp-editor open "https://example.com/wp-admin/"
# Login first, then navigate to Elementor editor
playwright-cli -s=wp-editor navigate "https://example.com/wp-admin/post.php?post={ID}&action=elementor"
```

或者如果要用使用者已登入的 session，就用 Chrome MCP。

### 步驟 4：管理 Template

**列出已儲存的 template**：

```bash
wp @site post list --post_type=elementor_library --fields=ID,post_title,post_status
```

**匯出 template**（瀏覽器）：

1. 前往：`https://example.com/wp-admin/edit.php?post_type=elementor_library`
2. 把滑鼠移到 template 上 > "Export Template"
3. 會下載成 .json 檔案

**匯入 template**（瀏覽器）：

1. 前往：`https://example.com/wp-admin/edit.php?post_type=elementor_library`
2. 點上方的 "Import Templates"
3. 選擇檔案 > 上傳 .json
4. Template 會出現在資源庫裡

**把 template 套用到新頁面**：

1. 建立頁面：`wp @site post create --post_type=page --post_title="New Page" --post_status=draft`
2. 透過瀏覽器在 Elementor 中開啟
3. 點資料夾 icon（Add Template）
4. 從 "My Templates" tab 選擇
5. 點 "Insert"
6. 客製化並儲存

**用 WP-CLI 複製既有頁面**：

```bash
# Get source page's Elementor data
SOURCE_DATA=$(wp @site post meta get {source_id} _elementor_data)
SOURCE_CSS=$(wp @site post meta get {source_id} _elementor_page_settings)

# Create new page
NEW_ID=$(wp @site post create --post_type=page --post_title="Duplicated Page" --post_status=draft --porcelain)

# Copy Elementor data
wp @site post meta update $NEW_ID _elementor_data "$SOURCE_DATA"
wp @site post meta update $NEW_ID _elementor_edit_mode "builder"
wp @site post meta update $NEW_ID _elementor_page_settings "$SOURCE_CSS"

# Regenerate CSS
wp @site elementor flush-css
```

**用 WP-CLI 在頁面之間套用 template**：

```bash
# Get source data
SOURCE=$(wp @site post meta get {source_id} _elementor_data)
SETTINGS=$(wp @site post meta get {source_id} _elementor_page_settings)

# Apply to target
wp @site post meta update {target_id} _elementor_data "$SOURCE"
wp @site post meta update {target_id} _elementor_edit_mode "builder"
wp @site post meta update {target_id} _elementor_page_settings "$SETTINGS"

# Clear cache
wp @site elementor flush-css
```

### 步驟 5：驗證

```bash
# Check the page status
wp @site post get {post_id} --fields=ID,post_title,post_status,guid

# Get live URL
wp @site post get {post_id} --field=guid
```

截圖確認視覺上的變更：

```bash
playwright-cli -s=verify open "https://example.com/{page-slug}/"
playwright-cli -s=verify screenshot --filename=page-verify.png
playwright-cli -s=verify close
```

---

## 關鍵模式

### Elementor 資料格式

Elementor 把頁面內容以 JSON 形式存在 `_elementor_data` postmeta 裡。結構是：

```
Section > Column > Widget
```

每個元素都有 `id`、`elType`、`widgetType` 和 `settings` 物件。直接操作這個 JSON 是可行的，但很脆弱，一定要先備份，而且優先用 `search-replace`，不要手動編輯 JSON。

### CSS 快取

任何用 WP-CLI 改動 Elementor 資料之後，都必須清除 CSS 快取。Elementor 會根據 widget 設定預先產生 CSS。快取過期 = 視覺上的變更不會出現。

```bash
wp @site elementor flush-css
# OR if elementor CLI not available:
wp @site option delete _elementor_global_css
wp @site post meta delete-all _elementor_css
```

### Global Widget

Global widget 是跨頁面共用的。編輯一個會更新所有使用它的地方。

```bash
# List global widgets
wp @site post list --post_type=elementor_library --meta_key=_elementor_template_type \
  --meta_value=widget --fields=ID,post_title
```

**注意**：取代 global widget 資料裡的文字，會影響每一個用到它的頁面。

### Elementor Pro vs Free

| 功能 | Free | Pro |
|---------|------|-----|
| 基本 widget | 有 | 有 |
| Theme Builder | 沒有 | 有 |
| 自訂字型 | 沒有 | 有 |
| Form widget | 沒有 | 有 |
| WooCommerce widget | 沒有 | 有 |
| 動態內容 | 沒有 | 有 |

Theme Builder 的 template（header、footer、archive）會以 `elementor_library` post type 儲存，並附上指定其顯示條件的特定 meta。

### 常用的 Elementor WP-CLI 指令

如果有 Elementor CLI 擴充功能：

```bash
wp @site elementor flush-css          # Clear CSS cache
wp @site elementor library sync       # Sync with template library
wp @site elementor update db          # Update database after version change
```
