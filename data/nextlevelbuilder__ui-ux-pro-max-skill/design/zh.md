---
name: design
description: "全方位設計 skill：品牌識別、design token、UI 樣式、logo 生成（55 種風格，使用 Gemini、Atlas Cloud 或 MuAPI AI）、企業識別系統（50 項交付物、CIP 樣機）、HTML 簡報（Chart.js）、banner 設計（22 種風格，社群／廣告／網頁／印刷）、icon 設計（15 種風格、SVG、Gemini 3.1 Pro）、社群照片（HTML→截圖，多平台）。Actions: design logo, create CIP, generate mockups, build slides, design banner, generate icon, create social photos, social media images, brand identity, design system. Platforms: Facebook, Twitter, LinkedIn, YouTube, Instagram, Pinterest, TikTok, Threads, Google Ads."
argument-hint: "[design-type] [context]"
license: MIT
metadata:
  author: claudekit
  version: "2.1.0"
---

# Design

整合型設計 skill：品牌、token、UI、logo、CIP、簡報、banner、社群照片、icon。

## 何時使用

- 品牌識別、語調、素材
- 設計系統 token 與規格
- 用 shadcn/ui + Tailwind 做 UI 樣式
- Logo 設計與 AI 生成
- 企業識別系統（CIP）交付物
- 簡報與 pitch deck
- 社群媒體、廣告、網頁、印刷用的 banner 設計
- Instagram、Facebook、LinkedIn、Twitter、Pinterest、TikTok 的社群照片

## 子 skill 路由

| 任務 | 子 skill | 細節 |
|------|-----------|---------|
| 品牌識別、語調、素材 | `brand` | 內附的同層 skill |
| Token、規格、CSS 變數 | `design-system` | 內附的同層 skill |
| shadcn/ui、Tailwind、程式碼 | `ui-styling` | 內附的同層 skill |
| Logo 創作、AI 生成 | Logo（內建） | `references/logo-design.md` |
| CIP 樣機、交付物 | CIP（內建） | `references/cip-design.md` |
| 簡報、pitch deck | Slides（內建） | `references/slides.md` |
| Banner、封面、header | Banner（內建） | `references/banner-sizes-and-styles.md` |
| 社群媒體圖片／照片 | Social Photos（內建） | `references/social-photos-design.md` |
| SVG icon、icon 組 | Icon（內建） | `references/icon-design.md` |

## Script 路徑

這個 skill 及其 `references/` 裡的 script 路徑，都是相對於包含這個 SKILL.md 的目錄，不是相對於專案：`scripts/<file>` 指這個 skill 自己的 `scripts/` 資料夾，`../<skill>/scripts/<file>` 指跟它一起安裝的同層子 skill。請從那個目錄組出完整路徑（skill 載入時 Claude Code 會回報它的 base directory），而且工作目錄要維持在專案根目錄，因為 script 會讀寫相對於它的專案檔案，例如 `docs/brand-guidelines.md`、`assets/design-tokens.json` 或 `src/`。

## Logo 設計（內建）

55+ 種風格、30 組調色盤、25 份產業指南。支援 Gemini Nano Banana、Atlas
Cloud 和 MuAPI 圖像生成。

### Logo：產生設計 Brief

```bash
python3 scripts/logo/search.py "tech startup modern" --design-brief -p "BrandName"
```

### Logo：搜尋風格／顏色／產業

```bash
python3 scripts/logo/search.py "minimalist clean" --domain style
python3 scripts/logo/search.py "tech professional" --domain color
python3 scripts/logo/search.py "healthcare medical" --domain industry
```

### Logo：用 AI 生成

輸出的 logo 圖片**一定要**用白色背景。

```bash
python3 scripts/logo/generate.py --brand "TechFlow" --style minimalist --industry tech
python3 scripts/logo/generate.py --prompt "coffee shop vintage badge" --style vintage
python3 scripts/logo/generate.py --brand "TechFlow" --provider atlas
python3 scripts/logo/generate.py --brand "TechFlow" --provider muapi
python3 scripts/logo/generate.py --brand "TechFlow" --provider muapi --muapi-model nano-banana-pro
```

**重要：** script 壞掉的時候，直接試著修好它。

生成之後，**一定要**透過 `AskUserQuestion` 問使用者要不要 HTML 預覽。如果要，就用內附的 `ui-ux-pro-max` skill 做圖庫。

## CIP 設計（內建）

50+ 項交付物、20 種風格、20 個產業。使用 Gemini Nano Banana（Flash/Pro）。

### CIP：產生 Brief

```bash
python3 scripts/cip/search.py "tech startup" --cip-brief -b "BrandName"
```

### CIP：搜尋各領域

```bash
python3 scripts/cip/search.py "business card letterhead" --domain deliverable
python3 scripts/cip/search.py "luxury premium elegant" --domain style
python3 scripts/cip/search.py "hospitality hotel" --domain industry
python3 scripts/cip/search.py "office reception" --domain mockup
```

### CIP：產生樣機

```bash
# With logo (RECOMMENDED)
python3 scripts/cip/generate.py --brand "TopGroup" --logo /path/to/logo.png --deliverable "business card" --industry "consulting"

# Full CIP set
python3 scripts/cip/generate.py --brand "TopGroup" --logo /path/to/logo.png --industry "consulting" --set

# Pro model (4K text)
python3 scripts/cip/generate.py --brand "TopGroup" --logo logo.png --deliverable "business card" --model pro

# Without logo
python3 scripts/cip/generate.py --brand "TechFlow" --deliverable "business card" --no-logo-prompt
```

模型：`flash`（預設，`gemini-2.5-flash-image`）、`pro`（`gemini-3-pro-image`）。可以用 `GEMINI_FLASH_IMAGE_MODEL` / `GEMINI_PRO_IMAGE_MODEL` 覆寫 id。

### CIP：渲染 HTML 簡報

```bash
python3 scripts/cip/render-html.py --brand "TopGroup" --industry "consulting" --images /path/to/cip-output
```

**提示：** 如果還沒有 logo，先用上面的 Logo 設計章節做一個。

## Slides（內建）

用 Chart.js、design token 和文案公式做策略性 HTML 簡報。

建立流程請載入 `references/slides-create.md`。

### Slides：知識庫

| 主題 | 檔案 |
|-------|------|
| 建立指南 | `references/slides-create.md` |
| 版面模式 | `references/slides-layout-patterns.md` |
| HTML 範本 | `references/slides-html-template.md` |
| 文案 | `references/slides-copywriting-formulas.md` |
| 策略 | `references/slides-strategies.md` |

## Banner 設計（內建）

涵蓋社群、廣告、網頁、印刷的 22 種美術方向風格。這個工作流程不需要包裹以外的任何東西：風格和調色盤的指引用 `references/banner-sizes-and-styles.md` 和內附的 `ui-ux-pro-max` skill。瀏覽器研究、圖像生成和截圖擷取都是選用的執行環境能力；沒有的時候，就用使用者提供的素材、CSS 打造的視覺，以及執行環境標準的預覽或擷取流程。

完整的尺寸與風格參考，請載入 `references/banner-sizes-and-styles.md`。

### Banner：工作流程

1. 透過 `AskUserQuestion` **蒐集需求**：用途、平台、內容、品牌、風格、數量
2. **研究**：讀 `references/banner-sizes-and-styles.md`，風格和調色盤的指引用內附的 `ui-ux-pro-max` skill；如果有瀏覽器研究的能力而且被允許，蒐集 3–5 個參考
3. **設計**：用確切的平台尺寸做出 HTML/CSS banner；用使用者提供的素材或 CSS 打造的視覺，或執行環境有提供的話，用經授權的圖像生成能力
4. **匯出**：用執行環境的瀏覽器或截圖能力，以確切尺寸擷取 PNG；沒辦法的話，就交付 HTML/CSS 原始碼，並標明 PNG 匯出待處理
5. **呈現**：把所有選項並排顯示，依回饋迭代

### Banner：尺寸速查

| 平台 | 類型 | 尺寸 (px) |
|----------|------|-----------|
| Facebook | Cover | 820 x 312 |
| Twitter/X | Header | 1500 x 500 |
| LinkedIn | Personal | 1584 x 396 |
| YouTube | Channel art | 2560 x 1440 |
| Instagram | Story | 1080 x 1920 |
| Instagram | Post | 1080 x 1080 |
| Google Ads | Med Rectangle | 300 x 250 |
| Website | Hero | 1920 x 600-1080 |

### Banner：主要美術風格

| 風格 | 最適合 |
|-------|----------|
| Minimalist | SaaS、科技 |
| Bold Typography | 公告 |
| Gradient | 現代品牌 |
| Photo-Based | 生活風格、電商 |
| Geometric | 科技、金融科技 |
| Glassmorphism | SaaS、App |
| Neon/Cyberpunk | 遊戲、活動 |

### Banner：設計規則

- 安全區：關鍵內容放在中央 70-80%
- 每個 banner 一個 CTA，放右下角，高度至少 44px
- 最多 2 種字體，內文至少 16px，標題 ≥32px
- 廣告的文字比例低於 20%（Meta 會扣分）
- 印刷：300 DPI、CMYK、3-5mm 出血

## Icon 設計（內建）

15 種風格、12 個分類。Gemini 3.1 Pro Preview 以文字輸出的方式生成 SVG。

### Icon：生成單一 Icon

```bash
python3 scripts/icon/generate.py --prompt "settings gear" --style outlined
python3 scripts/icon/generate.py --prompt "shopping cart" --style filled --color "#6366F1"
python3 scripts/icon/generate.py --name "dashboard" --category navigation --style duotone
```

### Icon：批次生成變體

```bash
python3 scripts/icon/generate.py --prompt "cloud upload" --batch 4 --output-dir ./icons
```

### Icon：多尺寸匯出

```bash
python3 scripts/icon/generate.py --prompt "user profile" --sizes "16,24,32,48" --output-dir ./icons
```

### Icon：主要風格

| 風格 | 最適合 |
|-------|----------|
| outlined | UI 介面、網頁 App |
| filled | 手機 App、導覽列 |
| duotone | 行銷、landing page |
| rounded | 親切的 App、健康 |
| sharp | 科技、金融科技、企業 |
| flat | Material design、Google 風格 |
| gradient | 現代品牌、SaaS |

**模型：** `gemini-3.1-pro-preview`，只輸出文字（SVG 是 XML 文字）。不需要圖像生成 API。

## 社群照片（內建）

多平台社群圖片設計：HTML/CSS → 截圖匯出。使用內附的 `ui-ux-pro-max`、`brand` 和 `design-system` skill；截圖匯出透過 Chrome headless、Playwright 或 Puppeteer 執行（見參考資料）。

尺寸、範本和最佳實務，請載入 `references/social-photos-design.md`。

### 社群照片：工作流程

1. **統籌**：用執行環境原生的任務清單追蹤下面的步驟；獨立的工作可以用平行 subagent
2. **分析**：解析 prompt：主題、平台、風格、品牌脈絡、內容元素
3. **發想**：3-5 個概念，透過 `AskUserQuestion` 呈現
4. **設計**：內附的 `brand` → `design-system` → `ui-ux-pro-max` skill；每個點子 × 每種尺寸各做一份 HTML
5. **匯出**：用 Chrome headless、Playwright 或 Puppeteer 以確切像素截圖（工具支援的話用 2x 裝置縮放；見參考資料）
6. **驗證**：用可用的瀏覽器或圖片檢視器開啟匯出的 PNG 並檢查；修好版面／樣式問題後重新匯出
7. **回報**：把設計決策的摘要寫到 `plans/reports/`
8. **整理**：把輸出檔案和報告分類放進專案的素材目錄

### 社群照片：主要尺寸

| 平台 | 尺寸 (px) | 平台 | 尺寸 (px) |
|----------|-----------|----------|-----------|
| IG Post | 1080×1080 | FB Post | 1200×630 |
| IG Story | 1080×1920 | X Post | 1200×675 |
| IG Carousel | 1080×1350 | LinkedIn | 1200×627 |
| YT Thumb | 1280×720 | Pinterest | 1000×1500 |

## 工作流程

### 完整品牌套件

1. **Logo** → `scripts/logo/generate.py` → 產生 logo 變體
2. **CIP** → `scripts/cip/generate.py --logo ...` → 建立交付物樣機
3. **簡報** → 載入 `references/slides-create.md` → 製作 pitch deck

### 新的設計系統

1. **品牌**（brand skill）→ 定義色彩、字體、語調
2. **Token**（design-system skill）→ 建立語意化的 token 層
3. **實作**（ui-styling skill）→ 設定 Tailwind、shadcn/ui

## 參考資料

| 主題 | 檔案 |
|-------|------|
| 設計路由 | `references/design-routing.md` |
| Logo 設計指南 | `references/logo-design.md` |
| Logo 風格 | `references/logo-style-guide.md` |
| Logo 色彩 | `references/logo-color-psychology.md` |
| Logo Prompt | `references/logo-prompt-engineering.md` |
| CIP 設計指南 | `references/cip-design.md` |
| CIP 交付物 | `references/cip-deliverable-guide.md` |
| CIP 風格 | `references/cip-style-guide.md` |
| CIP Prompt | `references/cip-prompt-engineering.md` |
| 簡報建立 | `references/slides-create.md` |
| 簡報版面 | `references/slides-layout-patterns.md` |
| 簡報範本 | `references/slides-html-template.md` |
| 簡報文案 | `references/slides-copywriting-formulas.md` |
| 簡報策略 | `references/slides-strategies.md` |
| Banner 尺寸與風格 | `references/banner-sizes-and-styles.md` |
| 社群照片指南 | `references/social-photos-design.md` |
| Icon 設計指南 | `references/icon-design.md` |

## Scripts

| Script | 用途 |
|--------|---------|
| `scripts/logo/search.py` | 搜尋 logo 風格、顏色、產業 |
| `scripts/logo/generate.py` | 用 Gemini AI 生成 logo |
| `scripts/logo/core.py` | logo 資料用的 BM25 搜尋引擎 |
| `scripts/cip/search.py` | 搜尋 CIP 交付物、風格、產業 |
| `scripts/cip/generate.py` | 用 Gemini 生成 CIP 樣機 |
| `scripts/cip/render-html.py` | 從 CIP 樣機渲染 HTML 簡報 |
| `scripts/cip/core.py` | CIP 資料用的 BM25 搜尋引擎 |
| `scripts/icon/generate.py` | 用 Gemini 3.1 Pro 生成 SVG icon |

## 前置需求

**Python：** 這個 skill 使用 Python script。在 Windows 上，請用 `python` 取代 `python3`（例如用 `python scripts/logo/search.py`，而不是 `python3 scripts/logo/search.py`）。

檢查有沒有安裝 Python：
```bash
python3 --version || python --version
```

## 設定

```bash
export GEMINI_API_KEY="your-key"  # https://aistudio.google.com/apikey
pip install google-genai pillow

# Optional MuAPI provider (no extra Python package required)
export MUAPI_API_KEY="your-key"
```

MuAPI 使用非同步的模型端點和預測結果 API。認證請見
[MuAPI API reference](https://muapi.ai/docs/api-reference)，目前各模型專屬的 schema 請見
[nano-banana model contract](https://api.muapi.ai/api/v1/models/nano-banana)
或 [nano-banana-pro model contract](https://api.muapi.ai/api/v1/models/nano-banana-pro)。
logo 生成器支援這兩個文件上有寫的模型 slug，並送出它們共通必填的 `prompt`，加上選填的 `aspect_ratio`
欄位；Pro 模型還接受選填的 `resolution` 欄位，這個專注於 logo 的工作流程
就維持在供應商的預設值。

> **Windows 注意事項：** 需要的地方用 `python` 取代 `pip`（例如 `python -m pip install ...`）。

## 整合

**內附的子 skill：** brand、design-system、ui-styling
**相關 skill：** ui-ux-pro-max
