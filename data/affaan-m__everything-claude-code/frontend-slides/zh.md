---
name: frontend-slides
description: 從零開始，或轉換 PowerPoint 檔案，做出驚豔、動畫豐富的 HTML 簡報。使用者想做簡報、把 PPT/PPTX 轉成網頁，或為演講/提案做投影片時使用。透過視覺探索，而不是抽象的選項，幫非設計師找到自己喜歡的美感。
metadata:
  origin: ECC
---

# Frontend Slides

做出零依賴、動畫豐富、完全在瀏覽器裡執行的 HTML 簡報。

靈感來自 zarazhangrui 的作品所展示的視覺探索做法（致謝：@zarazhangrui）。

## When to Activate

- 製作演講 deck、提案 deck、工作坊 deck 或內部簡報
- 把 `.ppt` 或 `.pptx` 投影片轉成 HTML 簡報
- 改善既有 HTML 簡報的版面、動態或字體
- 跟還不知道自己設計偏好的使用者一起探索簡報風格

## Non-Negotiables

1. **零依賴**：預設輸出單一個自給自足的 HTML 檔，CSS 和 JS 都 inline。
2. **一定要塞進 viewport**：每張投影片都必須完整放進一個 viewport，內部不能捲動。
3. **用看的，不要用講的**：用視覺預覽取代抽象的風格問卷。
4. **有辨識度的設計**：避免千篇一律的紫色漸層、白底 Inter 字體、看起來像套版的 deck。
5. **Production 品質**：程式碼要有註解、無障礙、響應式、有效能。

產生之前，先讀 `STYLE_PRESETS.md`，裡面有 viewport 安全的 CSS 基底、密度上限、預設風格目錄，以及 CSS 的雷區。

## Workflow

### 1. Detect Mode

選一條路徑：
- **新簡報**：使用者有主題、筆記或完整草稿
- **PPT 轉換**：使用者有 `.ppt` 或 `.pptx`
- **強化**：使用者已經有 HTML 投影片，想要改進

### 2. Discover Content

只問最少必要的問題：
- 目的：提案、教學、研討會演講、內部更新
- 長度：短（5-10 張）、中（10-20 張）、長（20 張以上）
- 內容狀態：完成的文案、粗略的筆記、只有主題

如果使用者有內容，先請他貼上來，再處理樣式。

### 3. Discover Style

預設走視覺探索。

如果使用者已經知道想要哪個預設風格，就跳過預覽，直接用。

否則：
1. 問這份 deck 想營造什麼感覺：令人印象深刻、充滿活力、專注、受到啟發。
2. 在 `.ecc-design/slide-previews/` 產生 **3 個單張投影片的預覽檔**。
3. 每個預覽都必須自給自足，清楚呈現字體/色彩/動態，投影片內容大約控制在 100 行以內。
4. 問使用者要留哪一個預覽，或想混搭哪些元素。

把情緒對應到風格時，參考 `STYLE_PRESETS.md` 裡的預設風格指南。

### 4. Build the Presentation

輸出下列其中一種：
- `presentation.html`
- `[presentation-name].html`

只有當 deck 含有擷取出來的或使用者提供的圖片時，才使用 `assets/` 資料夾。

必要的結構：
- 語意化的投影片 section
- 來自 `STYLE_PRESETS.md` 的 viewport 安全 CSS 基底
- 用 CSS custom properties 放主題值
- 一個簡報控制器 class，負責鍵盤、滾輪和觸控導覽
- 用 Intersection Observer 做進場動畫
- 支援減少動態效果

### 5. Enforce Viewport Fit

把這當成硬性關卡。

規則：
- 每個 `.slide` 都必須使用 `height: 100vh; height: 100dvh; overflow: hidden;`
- 所有字體和間距都要用 `clamp()` 縮放
- 內容放不下時，就拆成多張投影片
- 絕對不要用把文字縮到難以閱讀的大小來解決溢出
- 絕對不要讓投影片裡出現捲軸

使用 `STYLE_PRESETS.md` 裡的密度上限和必備的 CSS 區塊。

### 6. Validate

用下列尺寸檢查完成的 deck：
- 1920x1080
- 1280x720
- 768x1024
- 375x667
- 667x375

如果有瀏覽器自動化可用，就用它確認沒有任何投影片溢出，而且鍵盤導覽能正常運作。

### 7. Deliver

交付時：
- 刪除暫時的預覽檔，除非使用者想留著
- 有用的話，用該平台適合的開啟方式打開 deck
- 摘要說明檔案路徑、用了哪個預設風格、投影片張數，以及容易自訂主題的地方

依目前的作業系統使用正確的開啟指令：
- macOS：`open file.html`
- Linux：`xdg-open file.html`
- Windows：`start "" file.html`

## PPT / PPTX Conversion

轉換 PowerPoint 時：
1. 優先用 `python3` 搭配 `python-pptx` 來擷取文字、圖片和備註。
2. 如果沒有 `python-pptx`，先問要不要安裝，或是改走手動/匯出的流程。
3. 保留投影片順序、講者備註和擷取出來的素材。
4. 擷取完成後，跑跟新簡報一樣的風格選擇流程。

轉換流程要跨平台。Python 能做的事，不要依賴只有 macOS 才有的工具。

## Implementation Requirements

### HTML / CSS

- 除非使用者明確要多檔案專案，否則 CSS 和 JS 都用 inline。
- 字體可以來自 Google Fonts 或 Fontshare。
- 優先用有氛圍感的背景、強烈的字體層級，以及明確的視覺方向。
- 用抽象形狀、漸層、網格、雜訊和幾何圖形，不要用插圖。

### JavaScript

要包含：
- 鍵盤導覽
- 觸控 / 滑動導覽
- 滑鼠滾輪導覽
- 進度指示器或投影片索引
- 進場時觸發的顯示動畫

### Accessibility

- 使用語意化結構（`main`、`section`、`nav`）
- 對比要夠清楚好讀
- 支援只用鍵盤的導覽
- 尊重 `prefers-reduced-motion`

## Content Density Limits

除非使用者明確要求更密集的投影片，而且可讀性仍然能維持，否則請遵守這些上限：

| Slide type | Limit |
|------------|-------|
| Title | 1 個標題 + 1 個副標 + 可選的標語 |
| Content | 1 個標題 + 4-6 個重點，或 2 小段文字 |
| Feature grid | 最多 6 張卡片 |
| Code | 最多 8-10 行 |
| Quote | 1 句引言 + 出處 |
| Image | 1 張受 viewport 限制的圖片 |

## Anti-Patterns

- 沒有視覺辨識度的通用新創公司漸層
- 系統字體的 deck，除非是刻意走編輯風
- 一大面牆的長條列重點
- 需要捲動的程式碼區塊
- 在矮螢幕上會壞掉的固定高度內容框
- 無效的負號 CSS 函式，例如 `-clamp(...)`

## Related ECC Skills

- `frontend-patterns`：deck 周邊的元件與互動模式
- `liquid-glass-design`：簡報刻意借用 Apple 玻璃質感美學時使用
- `e2e-testing`：需要對最終 deck 做自動化瀏覽器驗證時使用

## Deliverable Checklist

- 簡報能在瀏覽器裡從本機檔案直接執行
- 每張投影片都放進 viewport，不需捲動
- 風格有辨識度而且是刻意的
- 動畫有意義，不吵雜
- 有尊重減少動態效果的設定
- 交付時有說明檔案路徑和自訂的地方
