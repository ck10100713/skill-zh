---
name: design-system
description: "從現有的網站或截圖萃取完整的設計系統，寫成 DESIGN.md 檔案。透過瀏覽器自動化和 HTML 檢查，分析色彩、字型、元件樣式、間距和氛圍。產出針對一致性頁面生成而最佳化的語意化設計系統文件。觸發詞：'extract design system', 'design system', 'create DESIGN.md', 'analyse the design', 'what design does this site use', 'extract styles from', 'reverse engineer the design'。"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
compatibility: claude-code-only
---

# Design System Extractor

分析現有的網站、HTML 檔案或截圖，把語意化的設計系統整理成 `DESIGN.md` 檔案。輸出針對搭配 `design-loop` skill 和一般的頁面生成做了最佳化。

## 什麼時候用

- 要根據現有網站的視覺語言開始一個新專案
- 替一個從沒被正式寫下來的網站設計系統建立文件
- 在執行 design loop 之前準備 `.design/DESIGN.md`
- 從客戶現有的網站萃取品牌規範
- 替多頁專案建立一致性文件
- 從 Google Stitch 專案萃取設計 token

## 工作流程

### Step 1：確認來源

請使用者提供下列其中一種：

| 來源 | 方法 |
|--------|--------|
| **線上 URL** | 用 Playwright CLI 或爬蟲瀏覽，截圖 + 萃取 HTML |
| **本機 HTML 檔案** | 直接讀檔案 |
| **截圖圖片** | 用視覺方式分析（有限：無法取得確切的 hex） |
| **既有專案** | 掃描 `site/public/` 裡的 HTML 檔案來分析 |
| **Stitch 專案** | 用 `@google/stitch-sdk` 抓取畫面 HTML + 設計主題 |

### Step 2：萃取原始設計資料

#### 從線上 URL

1. **用 Playwright CLI 瀏覽網站**：
   ```
   playwright-cli -s=design open {url}
   playwright-cli -s=design screenshot --filename=.design/screenshots/source-desktop.png
   ```

2. **萃取完整的 HTML**：透過爬蟲 MCP，或直接讀頁面原始碼

3. **調整大小並截手機版**（375px）：
   ```
   playwright-cli -s=design resize 375 812
   playwright-cli -s=design screenshot --filename=.design/screenshots/source-mobile.png
   ```

4. 關閉 session：`playwright-cli -s=design close`

#### 從本機 HTML 檔案

直接讀檔案，從原始碼萃取設計 token。

#### 只有截圖

用視覺方式分析圖片。注意：沒有 HTML 原始碼的話，顏色萃取只會是近似值。要在輸出中標明這個限制。

#### 從 Google Stitch 專案

如果有安裝 `@google/stitch-sdk` 而且設定了 `STITCH_API_KEY`：

```typescript
import { stitch } from "@google/stitch-sdk";

// List projects to find the target
const projects = await stitch.projects();

// Get project details (includes designTheme)
const project = stitch.project(projectId);
const screens = await project.screens();

// Get HTML from the main screen
const screen = screens[0]; // or find by title
const htmlUrl = await screen.getHtml();
const imageUrl = await screen.getImage();
```

Stitch 的 `designTheme` 物件直接提供結構化的 token：

```json
{
  "colorMode": "DARK",
  "font": "INTER",
  "roundness": "ROUND_EIGHT",
  "customColor": "#40baf7",
  "saturation": 3
}
```

把這些對應到 DESIGN.md 的各個章節：
- `colorMode` → 主題（Light/Dark）
- `font` → 字型家族
- `roundness` → 元件的 border-radius（`ROUND_EIGHT` = 8px、`ROUND_SIXTEEN` = 16px 等）
- `customColor` → 主要品牌色
- `saturation` → 色彩鮮豔度（1-5 級）

然後也要下載並分析 HTML 來取得完整的色票（Stitch 的主題物件只有主要色，完整的色票在生成的 CSS 裡）。

### Step 3：分析設計 Token

從 HTML/CSS 原始碼萃取這些：

#### 色彩

在這些位置尋找（依優先順序）：

1. **CSS 自訂屬性**：`:root { --primary: #hex; }` 或 `@theme` 區塊
2. **Tailwind 設定**：有 `tailwind.config` 的 `<script>` 區塊，或 `<style>` 裡的 `@theme`
3. **行內樣式**：`style="color: #hex"` 或 `style="background: #hex"`
4. **Tailwind class**：`bg-blue-600`、`text-gray-900`（對應到色票）
5. **從截圖推算**：最後手段，只是近似值

找到的每個顏色，都要判斷它的**角色**：

| 角色 | 怎麼辨認 |
|------|-----------------|
| Primary | 按鈕、連結、active 狀態、品牌元素 |
| Background | `<body>` 或 `<html>` 的背景 |
| Surface | 卡片、容器、浮起的元素 |
| Text Primary | `<h1>`、`<h2>`、主要內文 |
| Text Secondary | 圖說、metadata、弱化的文字 |
| Border | 分隔線、輸入框邊框、卡片邊框 |
| Accent | 徽章、通知、強調 |

#### 字型

萃取：

| Token | 在哪裡找 |
|-------|---------------|
| 字型家族 | Google Fonts `<link>`、`@import`、CSS 裡的 `font-family` |
| 標題字重 | `font-bold`、`font-semibold`，或明確的 `font-weight` |
| 內文大小 | `<body>` 或根元素的基礎 `font-size` |
| 行高 | `leading-*` class 或 `line-height` CSS |
| 字距 | `tracking-*` class 或 `letter-spacing` CSS |

#### 元件

找出這些的模式：

- **按鈕**：形狀（rounded-full、rounded-lg）、顏色、padding、hover 狀態
- **卡片**：背景、邊框、陰影、border-radius、padding
- **導覽**：固定/靜態、背景處理、active 指示
- **表單**：輸入框樣式、focus 外框、標籤位置
- **Hero 區塊**：版面模式、覆蓋層處理、CTA 位置

#### 間距與版面

- **內容最大寬度**：找 `max-w-*` 或明確的 `max-width`
- **區塊 padding**：區塊之間典型的垂直 padding
- **Grid 系統**：欄數、gap 值
- **留白哲學**：緊湊、均衡、寬鬆或戲劇性

### Step 4：整理成自然語言

**關鍵**：DESIGN.md 應該用**語意化的自然語言**描述設計，並以確切的數值為佐證。這不是 CSS 傾倒，而是一份設計師或 AI 讀了就能理解並重現視覺語言的文件。

| 不要這樣寫 | 改成這樣寫 |
|-------------|---------------|
| `rounded-xl` | 「柔和的圓角（12px）」 |
| `shadow-md` | 「帶有擴散陰影的細緻浮起感」 |
| `#1E40AF` | 「深海藍（#1E40AF），用於主要動作」 |
| `py-16` | 「寬鬆的區塊間距，有呼吸空間」 |

### Step 5：寫 DESIGN.md

把檔案輸出到 `.design/DESIGN.md`（或使用者指定的路徑）。

照 `design-loop` skill 的 `references/site-template.md` 的結構走，特別是 DESIGN.md Template 那一節。關鍵章節有：

1. **Visual Theme & Atmosphere**：氛圍、調性、哲學
2. **Colour Palette & Roles**：包含角色、名稱、hex、用途的表格
3. **Typography**：字型家族、字重、大小、行高
4. **Component Styles**：按鈕、卡片、導覽、表單
5. **Layout Principles**：最大寬度、間距、grid、留白
6. **Design System Notes for Generation**：給接力棒 prompt 複製貼上的區塊

### Step 6：驗證準確度

如果有瀏覽器自動化可用：

1. 用萃取出來的設計系統產生一個小區塊來測試（例如一張卡片 + 按鈕 + 標題）
2. 跟原始網站並排截圖
3. 用視覺方式比對，調整任何不吻合的值

### Step 7：回報給使用者

呈現：
- 萃取出的 token 摘要（顏色數量、字型、元件模式）
- 產生的 DESIGN.md 位置
- 任何只是近似值的 token（用 ⚠️ 標記）
- 建議人工複查的項目（從截圖得到的顏色、模糊的字型）

## 處理多個頁面

如果網站有多個樣式不同的頁面：

1. **先分析首頁**，它通常有最完整的設計語言
2. 抽查 2-3 個內頁確認一致性
3. 在 Component Styles 章節裡記下任何**頁面專屬的覆寫**
4. 如果各頁面差異很大，問使用者要用哪個頁面當作標準來源

## 小提醒

- **Tailwind 網站最容易**：設定區塊裡什麼都有
- **Google Fonts 連結是寶藏**：它們指定了確切的字型家族和字重
- **CSS 自訂屬性很可靠**：它們代表刻意設計的 token
- **行內的 Tailwind class 需要詮釋**：`bg-slate-900` 需要對應到一個角色
- **截圖是最後手段**：從圖片準確取得 hex 並不可靠
- **深色模式**：檢查有沒有 `.dark` class 的覆寫或 `prefers-color-scheme` media query

## 常見陷阱

- ❌ 只列出原始 CSS 值，沒有語意化的描述
- ❌ 漏掉深色模式的色票（檢查 `.dark` class 或 media query）
- ❌ 忽略元件模式（只列出顏色是不夠的）
- ❌ 沒有包含第 6 節（可複製貼上的生成區塊）
- ❌ 從截圖得到近似的顏色，卻沒有標明不確定性
