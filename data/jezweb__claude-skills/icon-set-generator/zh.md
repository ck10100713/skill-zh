---
name: icon-set-generator
description: "為網站和應用程式產生風格一致、貼合專案的 SVG 圖示組。只要使用者需要自訂圖示、網站或 app 的圖示組、客戶專案用的圖示，或提到需要看起來一致的 SVG 圖示，就用這個 skill。使用者描述一個專案、而圖示自然會是交付物的一部分時也要觸發，例如「我在幫水電師傅做網站」就代表會需要服務圖示。觸發詞：'icons for'、'icon set'、'custom icons'、'SVG icons'、'make me icons'、'I need icons'、'website icons'、'project icons'，或任何替網頁專案要一致視覺資產的需求。產出的是套用統一風格規格的獨立 SVG 檔案，不是去通用圖示庫查現成的。"
compatibility: claude-code-only
---

# Icon Set Generator

產生客製化、視覺一致的 SVG 圖示組，量身為特定專案打造。每一組都從共用的風格規格建出來，讓每個圖示都像是同一套的：線條粗細一樣、轉角處理一樣、視覺密度一樣。

## 為什麼重要

通用圖示庫（Lucide、Heroicons）很好用，但每個用它們的網站看起來都差不多。一組客製圖示能讓專案有獨特的視覺辨識度。難的是一致性：一個一個畫 20 個以上的圖示，風格會慢慢跑掉。這個 skill 的解法是把風格規則定義一次，然後套用到每個圖示上。

## 工作流程

### 步驟 1：了解專案

問專案的事。你需要足夠的資訊來建議圖示和挑風格：

- 這是什麼商業/專案？（產業、名稱、調性）
- 有品牌規範或色票嗎？（就算 SVG 用的是 currentColor，也會影響風格選擇）
- 想要什麼感覺？（現代、友善、企業、極簡、粗獷）
- 大概要多少圖示？（一般小型網站：15-25 個）

像「紐卡索的水電師傅，現代感」這樣簡短的描述就夠往下做了。不要問太多。

### 步驟 2：建議圖示

讀 `references/industry-icons.md`，取得各產業的建議。整理成幾組：

- **導覽**：選單、關閉、箭頭、搜尋
- **溝通**：電話、email、位置、時鐘
- **信任**：星星、盾牌、獎項、使用者
- **動作**：下載、分享、行事曆、表單
- **產業專屬**：這種商業類型獨有的圖示

把清單給使用者看。讓他在產生之前新增、移除或改名。

### 步驟 3：定義風格規格

讀 `references/style-presets.md` 看完整的預設定義。挑一個當起點：

| 預設 | 最適合 | 線寬 | 端點/接合 | 圓角 |
|--------|----------|--------|------------|---------|
| Clean | 大多數商業網站 | 1.5px | round/round | 2px |
| Sharp | 企業/技術類 | 1.5px | square/miter | 0px |
| Soft | 友善/親切 | 2px | round/round | 4px |
| Minimal | 優雅/編輯風 | 1px | round/round | 0px |
| Bold | 高衝擊/無障礙 | 2.5px | round/round | 2px |

告訴使用者你推薦哪個預設、為什麼，然後請他確認。

### 步驟 4：產生圖示

照下面的 SVG 規則產生每一個圖示。輸出到專案根目錄的 `icons/` 資料夾（或使用者偏好的位置）。

產生之前先讀 `references/svg-examples.md`，裡面有參考實作，示範合適的複雜度，以及常見圖示形狀怎麼處理。

每批大約 5 個。每批做完，先用眼睛檢查一致性再繼續。全部圖示做完後，建立預覽頁和 style-spec.json。

### 步驟 5：交付

輸出結構：
```
icons/
├── style-spec.json
├── preview.html
├── home.svg
├── phone.svg
└── ...
```

先呈現 `preview.html`，讓使用者一眼看到完整的圖示組。

---

## SVG 規則

一組裡的每個圖示都**一定要**遵守以下所有規則。就算是很小的不一致（線寬稍微不同、別人都是尖角它卻是圓角），整組看起來都會很不專業。

### SVG 範本

每個圖示都使用這個一模一樣的外層結構：

```xml
<svg xmlns="http://www.w3.org/2000/svg"
  width="{grid}" height="{grid}"
  viewBox="0 0 {grid} {grid}"
  fill="none"
  stroke="currentColor"
  stroke-width="{strokeWidth}"
  stroke-linecap="{strokeLinecap}"
  stroke-linejoin="{strokeLinejoin}">
  <!-- icon paths here -->
</svg>
```

### 硬性規則

1. **只用 `currentColor`**：絕對不要寫死顏色。SVG 從 CSS 繼承顏色。不准有 `fill="#000"` 或 `stroke="blue"`。如果某個形狀需要填色，用 `fill="currentColor"`。

2. **viewBox 完全相同**：每個圖示都用同一個 `viewBox`。沒有例外。

3. **根層級的線條屬性完全相同**：`<svg>` 元素上的 `stroke-width`、`stroke-linecap`、`stroke-linejoin` 在所有圖示之間都要一致。只有真的必要時，才在個別元素上覆寫。

4. **根層級不准有 transform**：不要 `translate`、`rotate`、`scale`。位置直接算進座標裡。

5. **不要 ID 或 class**：讓 SVG 保持乾淨，方便外部套樣式。

6. **座標精度**：最多小數點後 2 位。對齊半像素格線（例如 `12`、`12.5`，不要 `12.333`）。

7. **留白一致**：和 viewBox 邊緣保持設定好的留白。24px 格線、留白 2px 的話，就在座標 2 到 22 的範圍內畫。

8. **元素精簡**：在可行範圍內，`<path>`、`<circle>`、`<rect>`、`<line>` 越少越好。越簡單，檔案越小、渲染越快。

9. **視覺置中**：要看起來置中，而不只是數學上置中。向左的箭頭要稍微往右移。有煙囪的房子要針對不對稱做調整。

### 視覺修正

很細微但對專業感很關鍵：

- **曲線線寬補償**：同樣線寬下，曲線看起來比直線細。對以曲線為主的圖示（電話、地球），把路徑畫得稍微大一點，而不是改線寬。
- **尖角形狀過衝**：箭頭、人字形、三角形要比正方形會停的位置多伸出約 0.5px，看起來才一樣大。
- **視覺重量平衡**：簡單的圖示（單一人字形）看起來比複雜的（齒輪）輕。把簡單圖示在格線裡畫得稍微大一點，或用稍微厚實一點的路徑。不能有任何圖示看起來明顯比其他的輕或重。

---

## style-spec.json

```json
{
  "name": "project-name-icons",
  "preset": "clean",
  "grid": 24,
  "strokeWidth": 1.5,
  "strokeLinecap": "round",
  "strokeLinejoin": "round",
  "cornerRadius": 2,
  "padding": 2,
  "opticalBalance": true,
  "iconCount": 20,
  "icons": ["home", "phone", "email"],
  "generated": "2026-02-15"
}
```

---

## 預覽頁

產生一個自成一體的 HTML 檔，顯示所有圖示供視覺檢查。範本讀 `references/preview-template.md`。需求：

- 所有圖示以原始尺寸（24px）排成格狀，附標籤
- 同一個格狀再用 2 倍（48px）顯示，方便檢查細節
- 深色背景區塊（深底白圖示），檢查對比
- 最上方有風格規格摘要
- 內嵌 CSS、沒有相依套件，直接在瀏覽器打開就能看
- 所有 SVG 直接內嵌進 HTML（不要參照外部檔案）

---

## 品質檢查清單

交付前逐項確認：

- [ ] 所有 SVG 的 `viewBox`、`stroke-width`、`stroke-linecap`、`stroke-linejoin` 完全相同
- [ ] 所有 SVG 只用 `currentColor`
- [ ] 整組的視覺重量平衡
- [ ] 留白一致（沒有東西碰到 viewBox 邊緣）
- [ ] 所有圖示視覺置中
- [ ] 檔名是小寫 kebab-case（`arrow-right.svg`）
- [ ] 預覽 HTML 能正確顯示所有圖示
- [ ] style-spec.json 準確，並列出所有圖示

---

## 參考檔案

產生之前先讀這些：

- `references/style-presets.md`：詳細的預設定義和選擇指引
- `references/industry-icons.md`：各產業的圖示建議
- `references/preview-template.md`：預覽頁的 HTML 範本
- `references/svg-examples.md`：不同複雜度的範例 SVG，示範正確的構造
