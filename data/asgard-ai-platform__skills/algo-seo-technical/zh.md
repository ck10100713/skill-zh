---
name: "algo-seo-technical"
description: "最佳化 Core Web Vitals（LCP、INP、CLS），提升搜尋排名和使用者體驗。當使用者需要診斷頁面速度問題、改善 Largest Contentful Paint、減少版面位移、或通過 Google 的頁面體驗訊號時使用，即使他們說的是「我的網站很慢」、「Core Web Vitals 沒過」或「頁面速度最佳化」也一樣。"
metadata:
  category: "WP-35 SEO 演算法"
  tags: ["seo", "core-web-vitals", "performance", "page-speed"]
---

# Core Web Vitals 最佳化

## 概述

Core Web Vitals 是 Google 的頁面體驗指標：LCP（載入）、INP（互動性）和 CLS（視覺穩定性）。以真實使用者資料（CrUX）衡量。通過門檻：LCP < 2.5s、INP < 200ms、CLS < 0.1。

## 何時使用

**觸發條件：**
- 要診斷網站為什麼沒通過 Core Web Vitals 評估
- 要為了 SEO 最佳化頁面載入效能
- 要減少版面位移或改善互動性

**何時不要用：**
- 問題是內容相關性，不是速度時（用內容 SEO）
- 要分析連結權威度時（用 PageRank／反向連結分析）

## 演算法

```
鐵律：CrUX 的實際使用者資料才是真相
實驗室分數（Lighthouse）通過，在實際環境仍可能「沒過」。
Google 是依「真實使用者」資料（第 75 百分位）排名：
- LCP < 2.5s（良好）、2.5-4.0s（需要改善）、> 4.0s（差）
- INP < 200ms（良好）、200-500ms（需要改善）、> 500ms（差）
- CLS < 0.1（良好）、0.1-0.25（需要改善）、> 0.25（差）
```

### 階段 1：輸入驗證
從 CrUX API 或 Search Console 蒐集實際使用者資料。跑 Lighthouse 取得實驗室基準。找出哪些指標沒過。
**關卡：** 同時有實際使用者資料和實驗室資料；沒過的指標已辨識。

### 階段 2：核心演算法
**LCP 修正：** 1. 最佳化最大的元素（主視覺圖片／文字）。2. 預先載入關鍵資源。3. 降低伺服器回應時間（TTFB）。4. 消除阻擋渲染的資源。

**INP 修正：** 1. 把長任務（> 50ms）拆成較小的區塊。2. 減少 JavaScript 執行時間。3. 非關鍵的工作用 `requestIdleCallback`。4. 把主執行緒的阻塞降到最低。

**CLS 修正：** 1. 替圖片／影片設定明確的尺寸。2. 為廣告／嵌入內容預留空間。3. 避免把內容插入到現有內容的上方。4. 動態元素用 CSS `contain`。

### 階段 3：驗證
重跑 Lighthouse、部署，然後監控 CrUX 28 天滾動平均的改善。
**關卡：** 實驗室分數通過；等待實際使用者資料確認（28 天週期）。

### 階段 4：輸出
回傳稽核結果，附上具體的修正建議，並依影響大小排定優先順序。

## 輸出格式

```json
{
  "audit": {"lcp": {"value_ms": 3200, "status": "poor", "element": "hero-image.jpg", "fixes": ["preload", "compress"]}},
  "metadata": {"url": "...", "data_source": "crux", "device": "mobile"}
}
```

## 範例

### 輸入輸出範例
**輸入：** LCP=4.1s、CLS=0.32、INP=150ms 的 URL
**預期：** LCP 和 CLS 被標為差；INP 通過。修正優先順序：CLS（圖片尺寸）→ LCP（主視覺圖片預先載入）

### 邊界情況
| 輸入 | 預期 | 原因 |
|-------|----------|-----|
| 用客戶端渲染的 SPA | LCP 很可能偏高 | LCP 元素沒有伺服器端渲染的內容 |
| 有廣告的頁面 | CLS 很可能偏高 | 廣告版位會動態注入內容 |
| 實驗室所有指標都通過 | 實際環境仍可能沒過 | 網路慢的真實裝置和實驗室不同 |

## 常見陷阱

- **實驗室 vs 實際環境的落差**：Lighthouse 跑在模擬的高速裝置上。真實使用者用 3G 加舊手機，數字會差很多。
- **LCP 元素會變**：LCP 元素在不同次的頁面載入可能不同（圖片 vs 文字）。要針對「最常見」的 LCP 元素最佳化，不是只針對其中一個。
- **CLS 歸因**：版面位移會算在移動的元素上，但「原因」常常是插入在它上方的元素。要追根因，不要追症狀。
- **INP 取代了 FID**：2024 年 3 月起，INP 取代 FID。舊的 FID 參考資料已經過時。
- **28 天的延遲**：CrUX 使用 28 天的滾動視窗。修正要最久一個月才會反映在實際使用者資料上。

## 參考資料

- 針對特定元素的最佳化技巧，見 `references/optimization-techniques.md`
- CrUX API 的用法和監控設定，見 `references/crux-monitoring.md`
