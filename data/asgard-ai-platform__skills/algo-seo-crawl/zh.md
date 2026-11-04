---
name: "algo-seo-crawl"
description: "實作網頁爬蟲 pipeline，涵蓋 URL 探索、抓取、解析和儲存。當使用者需要建立網站爬蟲、稽核網站結構、或有系統地蒐集網頁資料時使用，即使他們說的是「爬網站」、「爬所有頁面」或「網站稽核蜘蛛」也一樣。"
metadata:
  category: "WP-35 SEO 演算法"
  tags: ["seo", "web-crawler", "scraping", "site-audit"]
---

# 網頁爬蟲（Web Crawler）

## 概述

網頁爬蟲透過探索 URL、抓取內容、解析 HTML 和儲存結果，有系統地走訪網頁。使用 BFS 或以優先順序為基礎的 frontier 管理。效能受 I/O 限制，通常卡在禮貌性限制（politeness），而不是運算。

## 何時使用

**觸發條件：**
- 要建立網站稽核工具，探索所有頁面及其連結結構
- 要大規模地從網站蒐集結構化資料
- 要為 SEO 分析繪製網站架構

**何時不要用：**
- 只需要單一個 API 端點的資料時（直接用 HTTP client）
- sitemap.xml 已提供所有需要的 URL 時（改為解析 sitemap）

## 演算法

```
鐵律：遵守 robots.txt 和速率限制
爬蟲「必須」：
1. 在爬任何路徑之前，先解析並遵守 robots.txt
2. 強制執行 crawl-delay（沒指定時預設 1 秒）
3. 用具描述性的 User-Agent 表明自己的身分
無視這些既不道德，也會讓你的 IP 被封鎖。
```

### 階段 1：輸入驗證
解析種子 URL，替每個網域抓取並解析 robots.txt，設定爬取範圍（同網域、子網域或跨網域）。
**關卡：** 種子 URL 有效、robots.txt 規則已載入、範圍已定義。

### 階段 2：核心演算法
1. 用種子 URL 初始化 URL frontier（優先佇列或 FIFO）
2. 取出 URL，檢查：沒造訪過、robots.txt 允許、在範圍內
3. 抓取頁面，附帶逾時和重試邏輯，並遵守 crawl-delay
4. 解析 HTML：擷取連結（正規化、去重）、擷取內容／metadata
5. 把探索到的 URL 放進佇列，儲存解析後的資料
6. 重複直到 frontier 清空或達到上限

### 階段 3：驗證
檢查：爬取紀錄裡沒有違反 robots.txt、沒有儲存重複的頁面、所有探索到的 URL 都有交代。
**關卡：** 爬取在範圍內完成、維持了禮貌性。

### 階段 4：輸出
回傳網站地圖，包含頁面、連結圖和擷取到的 metadata。

## 輸出格式

```json
{
  "pages": [{"url": "...", "status": 200, "title": "...", "links_out": 15, "depth": 2}],
  "metadata": {"pages_crawled": 500, "errors": 12, "duration_seconds": 300, "domain": "example.com"}
}
```

## 範例

### 輸入輸出範例
**輸入：** 種子："https://example.com"、max_depth: 2、max_pages: 100
**預期：** 爬取樹，首頁在深度 0，連結頁面在深度 1-2，並遵守 robots.txt

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| robots.txt 不允許 / | 爬到零個頁面 | 必須遵守完全禁止 |
| 重新導向迴圈 | 5 次重新導向後停止 | 避免無限迴圈 |
| Soft 404（200 但是是錯誤頁面） | 標記為 soft 404 | 光看狀態碼不夠 |

## 常見陷阱

- **URL 正規化**：`http://Example.COM/path/` 和 `http://example.com/path` 是同一個 URL。要正規化：host 轉小寫、移除預設 port、移除結尾斜線、排序 query 參數。
- **JavaScript 渲染的內容**：基本的 HTTP 抓取會漏掉 JS 渲染的內容。SPA 要用 headless browser（Playwright/Puppeteer）。
- **陷阱偵測**：日曆頁面、URL 裡的 session ID 和無限分頁，都會造成爬蟲陷阱。要設定最大深度和 URL 模式限制。
- **自我限速**：平行抓取卻沒有每個網域的速率限制，會壓垮小型伺服器。要用每個網域的 semaphore。
- **字元編碼**：不是所有頁面都是 UTF-8。要從 HTTP header 和 meta 標籤偵測編碼，不行時再退回字元集偵測函式庫。

## 參考資料

- URL 正規化的規則（RFC 3986），見 `references/url-normalization.md`
- 分散式爬取架構，見 `references/distributed-crawl.md`
