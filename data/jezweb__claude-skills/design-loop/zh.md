---
name: design-loop
description: "用接力棒（baton-passing）迴圈自主建構多頁網站。每一輪從 .design/next-prompt.md 讀取任務，用 HTML/Tailwind 產生一個頁面，整合進網站，用視覺方式驗證，然後寫下下一個任務讓迴圈持續下去。只要使用者要求自主建構整個網站、建構網站的所有頁面、依序產生多個頁面，或執行 'design loop' / 'baton loop' / 'autonomous site build'，就使用，即使他們只是在流程中途說 'just keep going' 或 'build the next page' 或 'next page' 也一樣。"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
compatibility: claude-code-only
---

# Design Loop — 自主網站建構器

透過自主迴圈建構完整的多頁網站。每一輪讀取一個任務、產生一個頁面、整合進去、用視覺方式驗證，然後寫下下一個任務繼續跑。

## 概觀

Design Loop 採用「接力棒」模式：一個檔案（`.design/next-prompt.md`）當作每一輪之間傳遞的接力棒。每個循環：

1. 從接力棒讀取目前的任務
2. 產生頁面（透過 Claude 或 Google Stitch）
3. 整合進網站結構（導覽、連結）
4. 透過瀏覽器自動化做視覺驗證（如果可用）
5. 更新網站文件
6. 把**下一個**任務寫進接力棒，讓迴圈持續下去

這跟編排方式無關。迴圈可以由下列方式驅動：
- **有人在迴圈中**：使用者檢視每個頁面，然後說「next」或「keep going」
- **完全自主**：Claude 持續執行，直到網站完成
- **CI/CD**：在 `.design/next-prompt.md` 變動時觸發

## 生成後端

| 後端 | 設定 | 品質 | 速度 | 最適合 |
|---------|-------|---------|-------|----------|
| **Claude**（預設） | 零相依 | 很好：可上線的 HTML/Tailwind | 快 | 大多數專案、完整掌控程式碼 |
| **Google Stitch** | `npm install @google/stitch-sdk` + API key | 更高擬真度的 AI 設計 | 每個畫面約 10-20 秒 | 重視設計的專案、視覺精緻度 |

### 偵測 Stitch

每個迴圈開始時，檢查 Stitch 是否可用：

1. 檢查有沒有安裝 `@google/stitch-sdk`：`ls node_modules/@google/stitch-sdk 2>/dev/null`
2. 檢查 `.dev.vars` 或環境變數裡有沒有設定 `STITCH_API_KEY`
3. 檢查有沒有 `.design/metadata.json`（裡面有 Stitch 專案 ID）

三個都有就用 Stitch。否則退回 Claude 生成。

### Stitch SDK 參考

安裝：`npm install @google/stitch-sdk`。把 `STITCH_API_KEY` 設在環境變數或 `.dev.vars`。

```typescript
import { stitch } from "@google/stitch-sdk";

// Create a project
const result = await stitch.callTool("create_project", { title: "My Site" });

// Reference an existing project
const project = stitch.project("4044680601076201931");

// Generate a screen
const screen = await project.generate("A modern landing page with hero section", "DESKTOP");

// Get assets
const htmlUrl = await screen.getHtml();    // Download URL for HTML
const imageUrl = await screen.getImage();  // Download URL for screenshot

// Edit an existing screen (prefer this for refinements)
const edited = await screen.edit("Make the background dark and enlarge the CTA button");

// Generate variants
const variants = await screen.variants("Try different colour schemes", {
  variantCount: 3,
  creativeRange: "EXPLORE",     // "REFINE" | "EXPLORE" | "REIMAGINE"
  aspects: ["COLOR_SCHEME"],    // "LAYOUT" | "COLOR_SCHEME" | "IMAGES" | "TEXT_FONT" | "TEXT_CONTENT"
});
```

裝置類型：`"MOBILE"` | `"DESKTOP"` | `"TABLET"` | `"AGNOSTIC"`。選擇模型：把 `"GEMINI_3_PRO"` | `"GEMINI_3_FLASH"` 當作 `generate()` 的第三個參數傳入。

其他操作：`stitch.projects()` 列出專案，`project.screens()` 列出畫面，`project.getScreen("id")` 取得單一畫面。

`getHtml()` 和 `getImage()` 回傳的是下載 URL。在圖片 URL 後面加上 `=w1280` 可取得完整解析度。驗證：需要 `STITCH_API_KEY`（或 OAuth 用 `STITCH_ACCESS_TOKEN` + `GOOGLE_CLOUD_PROJECT`）。錯誤會拋出 `StitchError`，錯誤碼有：`AUTH_FAILED`、`NOT_FOUND`、`RATE_LIMITED`。

### Stitch 專案的持久化

把 Stitch 的識別碼存到 `.design/metadata.json`，讓之後的迭代可以參照：

```json
{
  "projectId": "4044680601076201931",
  "screens": {
    "index": { "screenId": "d7237c7d78f44befa4f60afb17c818c1" },
    "about": { "screenId": "bf6a3fe5c75348e58cf21fc7a9ddeafb" }
  }
}
```

Stitch 整合的小技巧：
1. 把專案 ID 存在 `.design/metadata.json`，不要每一輪都建新專案
2. 要微調就用 `screen.edit()`，不要整個重新生成
3. 對 Stitch 的 HTML 做後處理：把 header/footer 換成你共用的元素
4. 在 prompt 裡帶入 DESIGN.md 的脈絡，Stitch 在有明確設計系統指示時，產出的結果更好

## 開始使用

### 第一次執行：初始化專案

如果 `.design/` 還不存在，建立專案骨架：

1. **詢問使用者**：
   - 網站名稱和目的
   - 目標受眾
   - 想要的美學風格（極簡、大膽、溫暖等）
   - 他們想要的頁面清單
   - 品牌色（或用 `/design-system` 從現有網站萃取）

2. **建立專案檔案**：

```
project/
├── .design/
│   ├── SITE.md           # Vision, sitemap, roadmap — the project's long-term memory
│   ├── DESIGN.md         # Visual design system — the source of truth for consistency
│   └── next-prompt.md    # The baton — current task with page frontmatter
└── site/
    └── public/           # Production pages live here
```

3. **寫 SITE.md**，用下面「SITE.md 範本」那一節的範本
4. **寫 DESIGN.md**，可以根據使用者的輸入手動寫，也可以用 `design-system` skill 從現有網站萃取
5. **為首頁寫第一根接力棒**（`.design/next-prompt.md`）

### 後續執行：讀取接力棒

如果 `.design/next-prompt.md` 已經存在，就解析它並繼續迴圈。

## 接力棒檔案

`.design/next-prompt.md` 有 YAML frontmatter 加上 prompt 本文：

```markdown
---
page: about
layout: standard
---
An about page for Acme Plumbing describing the company's 20-year history in Newcastle.

**DESIGN SYSTEM:**
[Copied from .design/DESIGN.md Section 6]

**Page Structure:**
1. Header with navigation (consistent with index.html)
2. Hero with company photo and tagline
3. Story timeline showing company milestones
4. Team section with photo grid
5. CTA section: "Get a Free Quote"
6. Footer (consistent with index.html)
```

| 欄位 | 必填 | 用途 |
|-------|----------|---------|
| `page` | 是 | 輸出檔名（不含 .html） |
| `layout` | 否 | `standard`、`wide`、`sidebar`，預設是 `standard` |

## 執行流程

### Step 1：讀取接力棒

```
Read .design/next-prompt.md
Extract: page name, layout, prompt body
```

### Step 2：查閱脈絡檔案

產生之前，先讀：

| 檔案 | 要檢查什麼 |
|------|---------------|
| `.design/SITE.md` | 第 4 節（Sitemap）：不要重做已經存在的頁面 |
| `.design/DESIGN.md` | 色票、字型、元件樣式 |
| `site/public/` 裡既有的頁面 | 要對齊的 header/footer/nav 寫法 |

**關鍵**：讀最近一個頁面的 HTML，取出完全一樣的 header、導覽和 footer 標記。新頁面必須使用完全相同的共用元素。

### Step 3：產生頁面

#### 選項 A：Claude 生成（預設）

用 Tailwind CSS（透過 CDN）產生完整的 HTML 檔案。頁面必須：

- **完全符合** `.design/DESIGN.md` 的設計系統
- **重用**既有頁面的相同 header/nav/footer（逐字複製）
- **自給自足**：單一 HTML 檔案，用 Tailwind CDN，不需要 build 步驟
- **響應式**：手機優先，在所有斷點都能運作
- 如果設計系統有指定，就**包含深色模式**
- **使用語意化 HTML**：正確的標題階層、landmark、alt 文字
- **接上真實的導覽**：所有導覽連結都指向實際的頁面（已存在或已規劃）

把產生的檔案寫到 `site/public/{page}.html`。

#### 選項 B：Stitch 生成（如果可用）

如果 Stitch SDK 可用：

1. 把接力棒本文和 DESIGN.md 的系統區塊合併，組成 prompt
2. 呼叫 `project.generate(prompt, deviceType)` 產生畫面
3. 把 `screen.getHtml()` 的 HTML 下載到 `.design/designs/{page}.html`
4. 把 `screen.getImage()` 的截圖下載到 `.design/screenshots/{page}.png`
5. 對 Stitch 的 HTML 做後處理：
   - 把 header/nav/footer 換成你專案的共用元素
   - 確保 Tailwind 設定一致
   - 接上內部導覽連結
6. 把處理好的檔案存到 `site/public/{page}.html`
7. 用新的畫面 ID 更新 `.design/metadata.json`

要對既有的 Stitch 畫面做反覆編輯，就用 `screen.edit(prompt)`，不要重新生成。

### Step 4：整合進網站

產生新頁面之後：

1. **更新所有既有頁面的導覽**：把新頁面加進導覽選單
2. **修正佔位連結**：把任何 `href="#"` 換成真實的頁面 URL
3. **確認跨頁一致性**：header、footer、nav 在每個地方都必須一模一樣
4. **檢查內部連結**：頁面之間不能有壞掉的連結

### Step 5：視覺驗證（如果有瀏覽器可用）

如果有 Playwright CLI 或 Chrome MCP：

1. 啟動本機伺服器：`npx serve site/public -p 3456`
2. 用桌面（1280px）和手機（375px）寬度替新頁面截圖
3. 把截圖存到 `.design/screenshots/{page}-desktop.png` 和 `{page}-mobile.png`
4. 對照設計系統做視覺比對
5. 修正任何問題（版面壞掉、顏色錯誤、導覽不一致）
6. 關掉伺服器

如果沒有瀏覽器自動化可用，直接跳到 Step 6。

### Step 6：更新網站文件

編輯 `.design/SITE.md`：

- 在第 4 節（Sitemap）把該頁面標為完成：`[x] {page}.html — {description}`
- 把第 5 節（Roadmap）或第 6 節（Ideas）裡已用掉的項目移除
- 加入生成過程中發現的任何新點子

### Step 7：寫下一根接力棒（關鍵）

**結束之前，你一定要更新 `.design/next-prompt.md`。**這樣才能讓迴圈持續下去。

1. **選下一個頁面**：
   - 第一優先：檢查第 5 節（Roadmap）有沒有待處理的高優先級項目
   - 第二優先：檢查第 5 節有沒有中優先級項目
   - 第三優先：從第 6 節（Ideas）挑
   - 最後手段：自己想一個符合網站願景的東西

2. **寫接力棒**，內容包含：
   - YAML frontmatter（`page`，選填的 `layout`）
   - 頁面目的和內容的描述
   - 從 `.design/DESIGN.md` 第 6 節複製過來的設計系統區塊
   - 詳細的頁面結構（編號的各個區塊）

3. **如果網站已經完成**（roadmap 的項目都做完了、沒有更多點子）：
   - 寫一根 `page: _complete` 的接力棒，並附上已建構內容的摘要
   - 這是在示意迴圈已經結束

## 迴圈結束

迴圈在下列情況結束：
- Roadmap 裡的所有頁面都建好了（SITE.md 第 4 節裡是 `[x]`）
- 使用者說要停
- 接力棒包含 `page: _complete`

結束時，輸出一份摘要：
- 已建構的頁面（附連結）
- 截圖（如果有擷取）
- 之後還可以做的任何點子

## 跨頁一致性規則

多頁生成最大的風險是**漂移**：頁面之間看起來略有不同。這樣預防：

| 元素 | 規則 |
|---------|------|
| **Header/Nav** | 從最近的頁面複製完全一樣的 HTML。絕對不要重新生成。 |
| **Footer** | 一樣，逐字複製，只改目前頁面的指示標記 |
| **Tailwind 設定** | 如果用 `<script>` 設定區塊，跨頁面必須完全一致 |
| **色彩值** | 一律用 DESIGN.md 裡確切的 hex 碼，絕對不要用近似值 |
| **字型引入** | 所有頁面用同一個 Google Fonts `<link>` 標籤 |
| **間距級距** | 一致的 padding/margin 值（記錄在 DESIGN.md） |

## 設計對照表

寫接力棒 prompt 時，用這些把模糊的使用者請求轉成精確的設計指示。

### UI/UX 關鍵字精煉

| 模糊的說法 | 專業術語 |
|:---|:---|
| "menu at the top" | "sticky navigation bar with logo and menu items" |
| "big photo" | "full-width hero section with focal-point imagery" |
| "list of things" | "responsive card grid with hover states and subtle elevation" |
| "button" | "primary call-to-action button with hover transition" |
| "form" | "form with labelled input fields, validation states, and submit button" |
| "picture area" | "hero section with background image or video" |
| "sidebar" | "collapsible side navigation with icon-label pairings" |
| "popup" | "modal dialog with overlay and smooth entry animation" |
| "footer stuff" | "footer with sitemap links, contact info, and legal notices" |
| "cards" | "content cards with consistent padding, rounded corners, and shadow" |
| "tabs" | "tabbed interface with active indicator and smooth content transition" |
| "search" | "search input with icon, placeholder text, and results dropdown" |
| "pricing" | "pricing comparison cards with highlighted recommended tier" |
| "testimonials" | "testimonial carousel or grid with avatar, quote, and attribution" |

### 氛圍與調性描述詞

| 基本調性 | 加強後的描述 |
|:---|:---|
| "Modern" | "Clean, minimal, generous whitespace, high-contrast typography" |
| "Professional" | "Sophisticated, trustworthy, subtle shadows, restricted premium palette" |
| "Fun / Playful" | "Vibrant, rounded corners, bold accent colours, bouncy animations" |
| "Dark Mode" | "High-contrast accents on deep slate or near-black backgrounds" |
| "Luxury" | "Elegant, spacious, fine lines, serif headers, high-fidelity photography" |
| "Tech / Cyber" | "Futuristic, neon accents, glassmorphism, monospaced typography" |
| "Warm / Friendly" | "Soft colours, rounded shapes, handwritten accents, inviting imagery" |
| "Bold / Industrial" | "Strong typography, high contrast, geometric shapes, dark backgrounds" |
| "Organic / Natural" | "Earth tones, soft textures, organic shapes, nature photography" |
| "Editorial" | "Magazine-like layouts, strong typographic hierarchy, generous leading" |

### 幾何、深度與間距

| 描述 | Tailwind | 視覺效果 |
|:---|:---|:---|
| 膠囊形 | `rounded-full` | 按鈕、標籤、徽章 |
| 柔和圓角 | `rounded-xl` | 卡片、容器、modal |
| 微圓角 | `rounded-lg` | 輸入框、較小的元素 |
| 銳利 / 精準 | `rounded-none` 或 `rounded-sm` | 技術感、粗獷主義美學 |
| 毛玻璃（Glassmorphism） | `backdrop-blur-md bg-white/10 border border-white/20` | 覆蓋層、導覽列 |
| 霧面 | `backdrop-blur-sm bg-white/80` | 淡淡的玻璃效果 |

| 立體層級 | 描述 | Tailwind |
|:---|:---|:---|
| 平面 | 沒有陰影，用色塊和邊框 | `shadow-none` |
| 輕如耳語 | 擴散的、幾乎看不見的浮起感 | `shadow-sm` |
| 細緻 | 卡片浮起用的柔和陰影 | `shadow-md` |
| 懸浮 | 高偏移、柔和的陰影 | `shadow-lg` 或 `shadow-xl` |
| 戲劇性 | 給 hero 元素或 modal 用的強烈陰影 | `shadow-2xl` |
| 內凹 | 給被按下或巢狀元素用的內陰影 | `shadow-inner` |

| 區塊密度 | 描述 | Tailwind |
|:---|:---|:---|
| 緊湊 | 精簡、資訊密集 | `py-8 md:py-12` |
| 均衡 | 標準的區塊間距 | `py-12 md:py-16` |
| 寬鬆 | 有呼吸空間、高級感 | `py-16 md:py-24` |
| 戲劇性 | 宣示性的間距，奢華/編輯風 | `py-24 md:py-32` |

## SITE.md 範本

初始化新專案時使用。寫到 `.design/SITE.md`：

```markdown
# Project Vision

> **AGENT INSTRUCTION:** Read this file before every iteration. It is the project's long-term memory.

## 1. Core Identity

| Field | Value |
|-------|-------|
| **Project Name** | [Name] |
| **Mission** | [What the site achieves] |
| **Target Audience** | [Who uses this site] |
| **Voice & Tone** | [Personality descriptors — warm, professional, playful, etc.] |
| **Region** | [Australia / US / UK — affects spelling, phone format, imagery] |

## 2. Visual Language

Reference these when writing baton prompts.

- **Primary Vibe**: [Main aesthetic — e.g. "Clean and modern"]
- **Secondary Vibe**: [Supporting aesthetic — e.g. "Warm and approachable"]
- **Anti-Vibes**: [What to avoid — e.g. "Not corporate, not cluttered"]

## 3. Technical Setup

- **Output Directory**: `site/public/`
- **CSS**: Tailwind CSS via CDN (no build step)
- **Dark Mode**: [Yes/No] — if yes, via class toggle
- **Fonts**: [Google Fonts import URL]

## 4. Live Sitemap

Update this when a page is successfully generated.

- [x] `index.html` — Homepage with hero, features, CTA
- [ ] `about.html` — Company story and team
- [ ] `services.html` — Service offerings with pricing
- [ ] `contact.html` — Contact form and location map

## 5. Roadmap (Backlog)

Pick the next task from here. Remove items as they're completed.

### High Priority
- [ ] Build about page with team section
- [ ] Build services page with pricing cards

### Medium Priority
- [ ] Build contact page with form
- [ ] Build FAQ page

### Low Priority
- [ ] Blog index page
- [ ] Individual blog post template

## 6. Creative Freedom

When the roadmap is empty, follow these guidelines to add pages:

1. **Stay on-brand** — new pages must fit the established vibe
2. **Enhance the core** — support the site mission
3. **Naming convention** — lowercase, descriptive filenames (e.g. `team.html`)

### Ideas to Explore
- [ ] `testimonials.html` — Customer reviews and case studies
- [ ] `gallery.html` — Project portfolio with image grid
- [ ] `faq.html` — Frequently asked questions with accordion

## 7. Rules of Engagement

1. Do NOT recreate pages already marked `[x]` in Section 4
2. ALWAYS update `.design/next-prompt.md` before completing an iteration
3. Remove consumed ideas from Section 6
4. Copy header/nav/footer from existing pages — never regenerate
5. All internal links must point to real pages
```

## DESIGN.md 範本

用 `design-system` skill 產生，或手動建立。寫到 `.design/DESIGN.md`：

```markdown
# Design System: [Project Name]

## 1. Visual Theme & Atmosphere

[Describe the mood, density, and aesthetic philosophy. Use evocative language.]

## 2. Colour Palette & Roles

| Role | Name | Value | Usage |
|------|------|-------|-------|
| Primary | [Name] | `#hexcode` | Buttons, links, active states |
| Primary Foreground | [Name] | `#hexcode` | Text on primary backgrounds |
| Secondary | [Name] | `#hexcode` | Supporting elements, badges |
| Background | [Name] | `#hexcode` | Page background |
| Surface | [Name] | `#hexcode` | Cards, containers |
| Text Primary | [Name] | `#hexcode` | Headings, body text |
| Text Secondary | [Name] | `#hexcode` | Captions, metadata |
| Border | [Name] | `#hexcode` | Dividers, input borders |
| Accent | [Name] | `#hexcode` | Highlights, notifications |

## 3. Typography

| Element | Font | Weight | Size | Line Height |
|---------|------|--------|------|-------------|
| H1 | [Font] | 700 | 3rem | 1.1 |
| H2 | [Font] | 600 | 2rem | 1.2 |
| H3 | [Font] | 600 | 1.5rem | 1.3 |
| Body | [Font] | 400 | 1rem | 1.6 |
| Small | [Font] | 400 | 0.875rem | 1.5 |

## 4. Component Styles

Document each component: Buttons (primary, secondary, hover), Cards (bg, border, radius, shadow, padding), Navigation (sticky/static, active indicator, mobile pattern), Forms (input style, labels, validation colours).

## 5. Layout Principles

Max content width, section padding, grid system, whitespace philosophy.

## 6. Design System Notes for Generation

**Copy this entire block into every baton prompt:**

**DESIGN SYSTEM (REQUIRED):**
- Platform: Web, Desktop-first, responsive
- Theme: [Light/Dark], [descriptors]
- Background: [Description] (#hex)
- Surface: [Description] (#hex)
- Primary: [Description] (#hex) for [role]
- Text: [Description] (#hex)
- Font: [Font name] via Google Fonts
- Corners: [Description]
- Shadows: [Description]
- Spacing: [Description]
```

## 檔案結構

```
project/
├── .design/
│   ├── SITE.md              # Project vision, sitemap, roadmap
│   ├── DESIGN.md            # Visual design system (source of truth)
│   ├── next-prompt.md       # The baton — current/next task
│   ├── metadata.json        # Stitch project/screen IDs (if using Stitch)
│   └── screenshots/         # Visual verification captures
├── site/
│   └── public/              # Production pages
└── .gitignore               # Add .design/screenshots/
```

## 常見陷阱

- 忘記更新 `.design/next-prompt.md`（會讓迴圈中斷）
- 重做已經在 SITE.md sitemap 標為 `[x]` 的頁面
- 重新生成 header/nav，而不是從既有頁面複製
- 接力棒 prompt 裡漏掉設計系統區塊
- 導覽裡留著 `href="#"` 佔位符，沒換成真實的 URL
- 各頁面的 Tailwind 設定不一致
- 一輪產生多個頁面（一個迴圈永遠只做一頁）
