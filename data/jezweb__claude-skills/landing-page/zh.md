---
name: landing-page
description: "根據簡報需求產生一個完整、可部署的 landing page。產出單一獨立 HTML 檔，使用 Tailwind CSS（透過 CDN）、響應式設計、深色模式、語意化 HTML 和 OG meta 標籤。區塊包含：附 CTA 的 hero、功能、社會證明、定價（選用）、FAQ、頁尾。用於建立行銷頁、產品上市頁、coming soon 頁，或任何獨立的 landing page。觸發詞：'landing page'、'create a page'、'marketing page'、'launch page'、'coming soon page'、'one-page site'。"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
compatibility: claude-code-only
---

# Landing Page 產生器

產生一個完整、可部署的 landing page，放在單一 HTML 檔裡。不用 build、沒有相依套件，用瀏覽器打開或部署到任何地方都行。

## 工作流程

### 1. 蒐集簡報需求

向使用者詢問：

| 欄位 | 必填 | 範例 |
|-------|----------|---------|
| 商業/產品名稱 | 是 | "Acme Plumbing" |
| 價值主張 | 是 | "24/7 emergency plumbing across Newcastle" |
| 目標受眾 | 是 | "Homeowners in the Hunter Valley" |
| 主要 CTA | 是 | "Call Now" / "Get a Quote" / "Sign Up" |
| 次要 CTA | 否 | "Learn More" / "View Pricing" |
| 品牌色 | 否 | Primary: #1E40AF, accent: #F59E0B |
| Logo URL 或文字 | 否 | logo 圖片的 URL，或直接用商業名稱 |
| 電話 / email | 否 | 給聯絡區塊用 |
| 想要的區塊 | 否 | 預設：hero、features、testimonials、FAQ、footer |

如果沒有提供品牌色，建議用 `color-palette` skill 產生，或用合理的預設（slate/blue）。

### 2. 產生 HTML

產出**單一 HTML 檔**，結構如下：

```
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <!-- Meta, OG tags, favicon -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>tailwind config with custom colours</script>
</head>
<body>
  <!-- Nav -->
  <!-- Hero -->
  <!-- Features -->
  <!-- Social Proof -->
  <!-- Pricing (optional) -->
  <!-- FAQ -->
  <!-- Footer -->
  <!-- Dark mode toggle script -->
</body>
</html>
```

### 3. 區塊模式

#### 導覽列
- 黏在頂端的導覽列，放 logo/名稱 + 指向各區塊的錨點連結
- 手機版漢堡選單（純 CSS 或極簡 JS）
- 導覽列上放 CTA 按鈕（靠右）

#### Hero
- 滿版寬度，在不用捲動就看得到的範圍內
- 標題（h1）：寫價值主張，不是商業名稱
- 副標題：補充細節，1-2 句
- 主要 CTA 按鈕（大、對比色）
- 選用：hero 圖片佔位或漸層背景
- 模式：桌機版文字靠左（和圖片 60/40 分割），手機版置中

#### 功能 / 服務
- 3-6 個項目，放在響應式格狀中（手機 1 欄，桌機 2-3 欄）
- 每個項目：圖示佔位 + 標題 + 簡短描述
- 使用語意化標題（區塊用 h2，項目用 h3）

#### 社會證明 / 客戶見證
- 2-3 張見證卡片，含引言、姓名、職稱/公司
- 適用的話加星等
- 替代做法：客戶/合作夥伴 logo 列

#### 定價（選用）
- 2-3 張方案卡片（basic/pro/enterprise 模式）
- 突出「推薦」方案
- 每個方案列出功能比較清單
- 每個方案各有一個 CTA 按鈕

#### FAQ
- 手風琴模式（details/summary，不需要 JS）
- 4-6 個常見問題
- 加上 Schema.org FAQPage 標記以利 SEO

#### 頁尾
- 商業名稱、聯絡資訊、社群連結
- 法律連結（隱私權、條款）先放佔位
- 版權年份（用 JS 自動更新）

### 4. 技術需求

**響應式**：Mobile-first，三個斷點
```
Default: mobile (< 640px)
sm: 640px+ (tablet)
lg: 1024px+ (desktop)
```

**深色模式**：三態切換（light/dark/system）
- 顏色用 CSS custom property
- 在 `<html>` 上加 `.dark` class，不要用 CSS media query
- 用一小段 JS 處理切換 + localStorage 持久化

**無障礙**：
- 標題階層正確（h1 → h2 → h3，不跳級）
- 所有圖片都有 alt 文字佔位
- 互動元素有 focus-visible 樣式
- 足夠的顏色對比（至少 4.5:1）
- 跳到主要內容的連結

**SEO**：
- 語意化 HTML5 元素（header、main、section、footer）
- OG meta 標籤（title、description、image、url）
- Twitter card meta 標籤
- Canonical URL
- 如果是在地商家，加 LocalBusiness 的 JSON-LD（參考 `seo-local-business` skill）

**效能**：
- 核心內容的渲染不需要 JS
- 圖片 lazy-load（`loading="lazy"`）
- 系統字型堆疊（不對外請求字型）
- 單一檔案，除了 Tailwind CDN 之外沒有外部 CSS/JS

### 5. 套用顏色

如果使用者提供品牌色，用內嵌方式設定 Tailwind：

```html
<script>
tailwind.config = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: '#1E40AF', light: '#3B82F6', dark: '#1E3A8A' },
        accent: { DEFAULT: '#F59E0B', light: '#FBBF24', dark: '#D97706' },
      }
    }
  }
}
</script>
```

如果沒有提供顏色，用 Tailwind 內建色盤（中性色用 slate，主色用 blue）。

### 6. 輸出

把檔案寫到使用者指定的位置，沒指定就預設寫到 `./index.html`。

產生之後：
1. 告訴使用者怎麼預覽：`open index.html`（macOS），或用 `python3 -m http.server` 開本機伺服器
2. 建議部署方式：拖到 Cloudflare Pages、Netlify drop，或 Workers 用 `wrangler deploy`
3. 列出需要替換的佔位內容（圖片、見證、電話號碼）

## 品質規則

1. **不要放 lorem ipsum 佔位字**：根據商業類型產生像真的佔位文字
2. **版面不能壞**：在腦中檢查響應式格狀：1 欄 → 2 欄 → 3 欄
3. **不要 inline style**：全部只用 Tailwind class
4. **要有真的互動**：平滑捲動到區塊、可運作的手風琴、可運作的深色模式切換
5. **預設就要無障礙**：不要為了美觀犧牲無障礙
6. **澳洲慣例**：如果商家在澳洲，用 +61 電話格式、澳式拼字、ABN 佔位

## 變化型

| 需求 | 做法 |
|---------|----------|
| "Coming soon page" | 只有 Hero + email 訂閱表單 + 倒數計時 |
| "Product launch" | Hero + features + pricing + 大量 CTA |
| "Portfolio" | Hero + 作品格狀 + about + contact |
| "Event page" | Hero + 議程 + 講者 + 場地 + 報名 CTA |
| "App download" | Hero + features + 截圖 + app store 徽章 |

依頁面用途調整要選的區塊。不是每個頁面都需要 pricing 或 FAQ。
