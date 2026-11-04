---
name: design-system
description: Token 架構、元件規格與投影片生成。三層 token（primitive→semantic→component）、CSS 變數、間距／字體級距、元件規格、策略性投影片製作。用於 design token、系統化設計、符合品牌規範的簡報。
argument-hint: "[component or token]"
license: MIT
metadata:
  author: claudekit
  version: "1.0.0"
---

# Design System

Token 架構、元件規格、系統化設計、投影片生成。

## 何時使用

- 建立 design token
- 定義元件狀態
- CSS 變數系統
- 間距／字體級距
- 設計到程式碼的交接
- Tailwind 主題設定
- **投影片／簡報生成**

## Token 架構

載入：`references/token-architecture.md`

### 三層結構

```
Primitive (raw values)
       ↓
Semantic (purpose aliases)
       ↓
Component (component-specific)
```

**範例：**
```css
/* Primitive */
--color-blue-600: #2563EB;

/* Semantic */
--color-primary: var(--color-blue-600);

/* Component */
--button-bg: var(--color-primary);
```

## Script 路徑

這個 skill 及其 `references/` 裡的 script 路徑，都是相對於包含這個 SKILL.md 的目錄，不是相對於專案：`scripts/<file>` 指這個 skill 自己的 `scripts/` 資料夾，`../<skill>/scripts/<file>` 指跟它一起安裝的同層子 skill。請從那個目錄組出完整路徑（skill 載入時 Claude Code 會回報它的 base directory），而且工作目錄要維持在專案根目錄，因為 script 會讀寫相對於它的專案檔案，例如 `docs/brand-guidelines.md`、`assets/design-tokens.json` 或 `src/`。

## 快速開始

**產生 token：**
```bash
node scripts/generate-tokens.cjs --config tokens.json -o tokens.css
```

**驗證使用情況：**
```bash
node scripts/validate-tokens.cjs --dir src/
```

## 參考資料

| 主題 | 檔案 |
|-------|------|
| Token 架構 | `references/token-architecture.md` |
| Primitive Token | `references/primitive-tokens.md` |
| Semantic Token | `references/semantic-tokens.md` |
| Component Token | `references/component-tokens.md` |
| 元件規格 | `references/component-specs.md` |
| 狀態與變體 | `references/states-and-variants.md` |
| Tailwind 整合 | `references/tailwind-integration.md` |

## 元件規格模式

| 屬性 | 預設 | Hover | Active | Disabled |
|----------|---------|-------|--------|----------|
| Background | primary | primary-dark | primary-darker | muted |
| Text | white | white | white | muted-fg |
| Border | none | none | none | muted-border |
| Shadow | sm | md | none | none |

## Scripts

| Script | 用途 |
|--------|---------|
| `generate-tokens.cjs` | 從 JSON token 設定產生 CSS |
| `validate-tokens.cjs` | 檢查程式碼裡有沒有寫死的值 |
| `search-slides.py` | BM25 搜尋 + 情境化推薦 |
| `slide-token-validator.py` | 驗證投影片 HTML 是否符合 token 規範 |
| `fetch-background.py` | 從 Pexels/Unsplash 抓圖 |

## 範本

| 範本 | 用途 |
|----------|---------|
| `design-tokens-starter.json` | 具備三層結構的起始 JSON |

## 整合

**搭配 brand：** 從品牌色彩／字體擷取 primitive
**搭配 ui-styling：** Component token → Tailwind config

**Skill 依賴：** brand、ui-styling
**主要 Agent：** ui-ux-designer、frontend-developer

## 投影片系統

用 design token + Chart.js + 情境化決策系統，製作符合品牌規範的簡報。

### 唯一事實來源（Source of Truth）

| 檔案 | 用途 |
|------|---------|
| `docs/brand-guidelines.md` | 品牌識別、語調、色彩 |
| `assets/design-tokens.json` | Token 定義（primitive→semantic→component） |
| `assets/design-tokens.css` | CSS 變數（在投影片裡 import） |
| `assets/css/slide-animations.css` | CSS 動畫函式庫 |

### 投影片搜尋（BM25）

```bash
# Basic search (auto-detect domain)
python scripts/search-slides.py "investor pitch"

# Domain-specific search
python scripts/search-slides.py "problem agitation" -d copy
python scripts/search-slides.py "revenue growth" -d chart

# Contextual search (Premium System)
python scripts/search-slides.py "problem slide" --context --position 2 --total 9
python scripts/search-slides.py "cta" --context --position 9 --prev-emotion frustration
```

### 決策系統 CSV

| 檔案 | 用途 |
|------|---------|
| `data/slide-strategies.csv` | 15 種簡報結構 + 情緒弧線 + sparkline 節拍 |
| `data/slide-layouts.csv` | 25 種版面 + 元件變體 + 動畫 |
| `data/slide-layout-logic.csv` | 目標 → 版面 + break_pattern 旗標 |
| `data/slide-typography.csv` | 內容類型 → 字體級距 |
| `data/slide-color-logic.csv` | 情緒 → 色彩處理 |
| `data/slide-backgrounds.csv` | 投影片類型 → 圖片分類（Pexels/Unsplash） |
| `data/slide-copy.csv` | 25 種文案公式（PAS、AIDA、FAB） |
| `data/slide-charts.csv` | 25 種圖表類型與 Chart.js 設定 |

### 情境化決策流程

```
1. Parse goal/context
        ↓
2. Search slide-strategies.csv → Get strategy + emotion beats
        ↓
3. For each slide:
   a. Query slide-layout-logic.csv → layout + break_pattern
   b. Query slide-typography.csv → type scale
   c. Query slide-color-logic.csv → color treatment
   d. Query slide-backgrounds.csv → image if needed
   e. Apply animation class from slide-animations.css
        ↓
4. Generate HTML with design tokens
        ↓
5. Validate with slide-token-validator.py
```

### 打破模式（Duarte Sparkline）

高品質的簡報會在不同情緒之間交替，維持參與感：
```
"What Is" (frustration) ↔ "What Could Be" (hope)
```

系統會在 1/3 和 2/3 的位置計算要打破模式的地方。

### 投影片需求

**所有投影片一定要：**
1. import `assets/design-tokens.css`，當作唯一事實來源
2. 使用 CSS 變數：`var(--color-primary)`、`var(--slide-bg)` 等
3. 圖表用 Chart.js（不要只用 CSS 做的長條）
4. 包含導覽（鍵盤方向鍵、點擊、進度條）
5. 內容置中對齊
6. 聚焦在說服／轉換

### Chart.js 整合

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>

<canvas id="revenueChart"></canvas>
<script>
new Chart(document.getElementById('revenueChart'), {
    type: 'line',
    data: {
        labels: ['Sep', 'Oct', 'Nov', 'Dec'],
        datasets: [{
            data: [5, 12, 28, 45],
            borderColor: '#FF6B6B',  // Use brand coral
            backgroundColor: 'rgba(255, 107, 107, 0.1)',
            fill: true,
            tension: 0.4
        }]
    }
});
</script>
```

### Token 合規

```css
/* CORRECT - uses token */
background: var(--slide-bg);
color: var(--color-primary);
font-family: var(--typography-font-heading);

/* WRONG - hardcoded */
background: #0D0D0D;
color: #FF6B6B;
font-family: 'Space Grotesk';
```

### 參考實作

具備所有功能的可運作範例：
```
assets/designs/slides/claudekit-pitch-251223.html
```

### 指令

```bash
/slides:create "10-slide investor pitch for ClaudeKit Marketing"
```

## 最佳實務

1. 元件裡絕對不要用原始的 hex，一律參照 token
2. Semantic 層讓你可以切換主題（淺色／深色）
3. Component token 讓每個元件都能個別客製
4. 用 HSL 格式，方便控制透明度
5. 為每個 token 記錄它的用途
6. **投影片一定要 import design-tokens.css，而且只用 var()**
