---
name: responsiveness-check
description: "用瀏覽器自動化測試網站在不同 viewport 寬度下的響應式表現。在同一個 session 裡依序調整各斷點，每個寬度截圖，偵測版面轉換（欄數變化、導覽切換、溢出）。產出比較報告，精確指出版面在哪裡壞掉。用 'responsiveness check'、'check responsive'、'breakpoint test'、'viewport test'、'responsive sweep'、'check breakpoints' 或 'test at mobile' 觸發。"
compatibility: claude-code-only
---

# Responsiveness Check

測試網站版面如何回應 viewport 寬度的變化。在單一瀏覽器 session 裡依序調整各斷點，每個寬度截圖，比較相鄰的尺寸，並回報版面在哪裡壞掉。

**這個測什麼**：版面的響應式表現：溢出、堆疊、導覽轉換、內容重排。

**這個不測什麼**：一般的無障礙（ARIA、語意化 HTML、標題階層、顏色對比）。那些不會隨 viewport 寬度改變，請改用 ux-audit skill。

## 瀏覽器工具優先順序

開始之前，先偵測有哪些可用的瀏覽器工具：

1. **playwright-cli**（優先）：支援調整大小、具名 session 和 sub-agent 平行。如果有安裝，先執行 `/playwright-cli` 載入完整的指令參考。
2. **Playwright MCP**（`mcp__plugin_playwright_playwright__*`）：用 `browser_resize` 改變 viewport。
3. **Chrome MCP**（`mcp__claude-in-chrome__*`）：用 `resize_window` 改變 viewport。使用的是使用者已登入的 Chrome session。

如果都沒有，告訴使用者，並建議安裝 playwright-cli 或 Playwright MCP。

## 運作模式

### 模式 1：標準檢查

**什麼時候**："check responsive"、"responsiveness check"、"test breakpoints"

測試涵蓋裝置範圍的 8 個關鍵斷點：

| 寬度 | 裝置情境 |
|-------|---------------|
| 320px | 小手機（iPhone SE） |
| 375px | 標準手機（iPhone 14） |
| 768px | 平板直向（iPad） |
| 1024px | 平板橫向 / 小筆電 |
| 1280px | 筆電 |
| 1440px | 桌機 |
| 1920px | Full HD |
| 2560px | 超寬 / 4K |

**流程**：

1. 在單一瀏覽器 session 裡打開 URL（高度：900px）
2. 從 320px 開始。對每個斷點寬度：
   a. 調整 viewport
   b. 稍等一下讓 CSS 重排（版面轉場）
   c. 對首屏區域截圖
   d. 如果頁面有大量首屏以下的內容，就捲動並截圖
   e. 執行 8 項版面檢查（見下方矩陣）
   f. 記下任何問題與嚴重度
3. 比較相鄰的寬度，找出版面在哪裡轉換
4. 寫報告

### 模式 2：掃描

**什麼時候**："responsive sweep"、"sweep all breakpoints"、"find where it breaks"

從 320 到 2560，每 160px 測一次（共 15 個寬度）。跟標準模式一樣用單一 session，只是資料點更多。這個模式是用來找出版面壞掉的**精確寬度**。

寬度：320、480、640、800、960、1120、1280、1440、1600、1760、1920、2080、2240、2400、2560

開始掃描模式之前要**簡短確認**（15 張截圖是個不小的 session）。

### 模式 3：指定範圍

**什麼時候**："check between 768 and 1024"、"test tablet breakpoints"、"focus on mobile widths"

以 80px 為間隔，測試使用者指定的範圍。已知某個區間有問題、需要詳細調查時使用。

範例："check between 768 and 1024" 會測：768、848、928、1008（再加上終點 1024）。

### 多個 URL

測試多個 URL 時（例如「檢查首頁、關於頁和聯絡頁」）：

- 啟動**平行的 sub-agent**，一個 URL 一個（不是一個斷點一個）
- 每個 sub-agent 在自己的具名 session 裡對它的 URL 執行標準檢查
- 把結果合併成一份報告

```
# Sub-agent pattern (playwright-cli)
playwright-cli -s=page1 open https://example.com/ &
playwright-cli -s=page2 open https://example.com/about &
```

## 版面檢查矩陣

這 8 項檢查針對的是**真的會隨 viewport 寬度變化**的問題：

| # | 檢查 | 要找什麼 |
|---|-------|-----------------|
| 1 | **水平溢出** | 內容比 viewport 寬：出現水平捲軸、元素被截掉 |
| 2 | **文字溢出** | 文字在字中間被截斷、和相鄰元素重疊、字體小到看不清楚（< 12px） |
| 3 | **導覽轉換** | 漢堡選單在正確的寬度出現/消失，兩種模式之間沒有「壞掉」的狀態 |
| 4 | **內容堆疊** | 多欄版面在窄寬度下，依合理的閱讀順序堆疊成單欄 |
| 5 | **圖片/媒體縮放** | 圖片溢出容器、長寬比變形、缺少響應式尺寸 |
| 6 | **觸控目標** | 手機寬度（< 768px）下互動元素 < 44px：按鈕、連結、表單輸入 |
| 7 | **留白平衡** | 手機上太擠（沒有喘息空間），寬螢幕上太空（內容迷失在空白裡） |
| 8 | **CTA 可見度** | 每個寬度下，主要的行動呼籲都在首屏可見，不用捲動 |

## 轉換偵測

這個 skill 獨特的價值，是**找出版面在哪裡轉換**，以及轉換乾不乾淨。

比較相鄰寬度的截圖時，遇到以下情況就標記那個寬度：
- **欄數改變**（3 欄 → 2 欄 → 1 欄的格狀）
- **導覽模式切換**（完整導覽 → 漢堡，或反過來）
- **側邊欄出現/消失**（內容寬度跳動）
- **格狀重排**（卡片換到下一列）

回報每次轉換發生的**精確寬度範圍**：

| 轉換 | 從 | 到 | 寬度範圍 |
|-----------|------|-----|-------------|
| 導覽：漢堡 → 完整 | 768px | 1024px | 約 960px 切換 |
| 格狀：1 欄 → 2 欄 | 640px | 768px | 約 700px 重排 |
| 側邊欄出現 | 1024px | 1280px | 約 1100px 顯示 |

這能讓開發者知道該在哪裡設定（或修正）他們的 CSS 斷點。

## 嚴重度等級

與 ux-audit 一致：

| 嚴重度 | 意義 |
|----------|---------|
| **Critical** | 版面壞掉：內容無法閱讀、導覽無法使用、頁面不能用 |
| **High** | 重大的版面問題：大幅溢出、關鍵內容被藏起來、轉換壞掉 |
| **Medium** | 看得出來但還能用：間距尷尬、輕微溢出、堆疊順序不理想 |
| **Low** | 精修：留白微調、輕微的對齊問題、觸控目標稍微不足 |

## 自主規則

- **直接做**：調整 viewport、截圖、分析版面、比較寬度
- **簡短確認**：掃描模式之前（15 個 viewport）、平行測試 4 個以上 URL 之前
- **先問**：與表單互動，或點過認證流程之前

## 報告輸出

把報告寫到 `docs/responsiveness-check-YYYY-MM-DD.md`（單頁快速檢查則直接內嵌回覆）。

報告結構見 [references/report-template.md](references/report-template.md)。

## 參考檔案

| 什麼時候 | 讀什麼 |
|------|------|
| 查詢斷點細節和問題區間 | [references/breakpoints.md](references/breakpoints.md) |
| 撰寫響應式報告 | [references/report-template.md](references/report-template.md) |
