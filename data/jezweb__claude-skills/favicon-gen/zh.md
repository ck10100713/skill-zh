---
name: favicon-gen
description: "用 logo、文字或品牌色產生自訂 favicon。會產出 favicon.svg、favicon.ico、apple-touch-icon.png、icon-192/512.png 和 web manifest。只要使用者想要 favicon、提到要換掉 CMS 預設 favicon、想把 logo 轉成 favicon、想做品牌縮寫圖示，或在排查 favicon 不顯示 / iOS 黑方塊 / 缺少 manifest，就用這個 skill。"
compatibility: claude-code-only
---

# Favicon 產生器

用 logo、縮寫字母或品牌色，產生一整包 favicon。會輸出所有需要的格式，以及 HTML 整合用的程式碼。

## 工作流程

### 步驟 1：選擇做法

```
有帶圖示元素的 logo？
 有 -> 從 logo 抽出圖示
 沒有 -> 有文字/縮寫？
         有 -> 做縮寫字母 favicon
         沒有 -> 用品牌形狀
```

### 步驟 2：建立來源 SVG

**抽出的圖示**：從 logo 複製圖示的 path，在 32x32 的 viewBox 裡置中，並簡化到小尺寸也看得清楚。

**縮寫字母**：用 `assets/` 裡的範本：
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <circle cx="16" cy="16" r="16" fill="#0066cc"/>
  <text x="16" y="21" font-size="16" font-weight="bold"
        text-anchor="middle" fill="#ffffff" font-family="sans-serif">AC</text>
</svg>
```

**品牌形狀**：圓形（通用）、圓角方形（現代感）、盾牌（資安）、六角形（科技）。

SVG 範本放在 `assets/` 資料夾。

### 步驟 3：產生所有格式

需要 ImageMagick（`convert` 指令）。沒裝的話：`brew install imagemagick`（macOS）或 `apt install imagemagick`（Linux）。

```bash
# ICO (16x16 + 32x32)
convert favicon.svg -define icon:auto-resize=16,32 favicon.ico

# Apple Touch Icon (180x180, SOLID background — transparent = black on iOS)
convert favicon.svg -resize 180x180 -background "#0066cc" -alpha remove apple-touch-icon.png

# Android/PWA icons
convert favicon.svg -resize 192x192 icon-192.png
convert favicon.svg -resize 512x512 icon-512.png
```

**沒有 ImageMagick？** 改用 https://favicon.io 從 SVG 轉換。

### 步驟 4：建立 Web Manifest

複製 `assets/manifest.webmanifest` 並改成自己的內容：
```json
{
  "name": "Your Business Name",
  "short_name": "Business",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ],
  "theme_color": "#0066cc",
  "background_color": "#ffffff",
  "display": "standalone"
}
```

### 步驟 5：加上 HTML 標籤

```html
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#0066cc">
```

所有檔案都放在網站根目錄（Vite/React 是 `/public/`）。

---

## 關鍵規則

- **一定要產生所有格式**：SVG、ICO、apple-touch-icon、192、512、manifest
- **iOS 圖示一定要有實色背景**：透明會變成黑方塊
- **縮寫字母一定要用粗體**（一般字重在 16x16 會看不見）
- **用 16x16 測試**：看不清楚就再簡化
- **絕對不要帶著 CMS 預設圖示上線**（WordPress 的「W」之類）

## 格式速查

| 格式 | 尺寸 | 透明 | 用途 |
|--------|------|-------------|---------|
| `favicon.svg` | 向量 | 是 | 現代瀏覽器 |
| `favicon.ico` | 16+32 | 是 | 舊版瀏覽器 |
| `apple-touch-icon.png` | 180x180 | **否** | iOS 主畫面 |
| `icon-192.png` | 192x192 | 是 | Android |
| `icon-512.png` | 512x512 | 是 | PWA |

## 資產檔案

- `assets/favicon-svg-circle.svg`：圓形縮寫範本
- `assets/favicon-svg-square.svg`：圓角方形範本
- `assets/favicon-svg-shield.svg`：盾牌範本
- `assets/manifest.webmanifest`：Web manifest 範本

## 參考檔案

- `references/format-guide.md`：完整格式規格
- `references/extraction-methods.md`：從 logo 抽出圖示的步驟
- `references/monogram-patterns.md`：進階縮寫字母設計
- `references/shape-templates.md`：各行業適用的形狀與 SVG 程式碼
