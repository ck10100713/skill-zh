---
name: product-showcase
description: "為 web app 產生完整的行銷網站：多頁面、真實截圖、動畫 GIF 示範、功能深入介紹和工作流程展示。會瀏覽正在執行的 app，擷取畫面和操作序列，產出一個真的能讓人理解產品在做什麼、可部署的網站。對複雜或 agentic 的 app 特別有用，因為這類產品很難解釋。觸發詞：'showcase site'、'product page'、'show off the app'、'marketing site'、'demo site'、'product showcase'、'explain the app'、'how do I market this'。"
compatibility: claude-code-only
---

# Product Showcase 產生器

產生一個真正能讓人理解 web app 在做什麼的行銷網站。不只是一個 hero 加功能格狀，而是多頁面的網站：有真實截圖、工作流程的動畫 GIF 示範、功能深入介紹，並且從「這是什麼」逐步深入到「它到底是怎麼運作的」。

對複雜的 app、agentic AI 工具，以及任何靜態截圖傳達不出價值的產品特別有價值。

## 深度等級

| 深度 | 產出 | 時間 |
|-------|--------|----------|
| **quick** | 單一頁面：hero、功能、CTA。跟以前一樣。 | 15-20 分鐘 |
| **standard** | 多頁面網站：首頁、功能頁、附截圖的運作方式頁。 | 1-2 小時 |
| **thorough** | 完整網站：首頁、每個功能各一頁、動畫 GIF 示範、使用情境、比較頁、文件風格的 demo。 | 3-6 小時 |

預設：**standard**

## 偵測瀏覽器工具

開始之前，先偵測有哪些可用的瀏覽器工具：

1. **Chrome MCP**（`mcp__claude-in-chrome__*`）：需要登入的 app 優先用這個
2. **Playwright MCP**（`mcp__plugin_playwright_playwright__*`）：用於公開的 app
3. **playwright-cli**：用於腳本化的流程

## 工作流程

### 1. 蒐集輸入

| 欄位 | 必填 | 範例 |
|-------|----------|---------|
| App URL | 是 | `https://app.example.com` 或 `http://localhost:5173` |
| App 名稱 | 是 | "Acme CRM" |
| 標語 | 否 | "The CRM that gets out of your way" |
| 目標受眾 | 否 | "Small business owners" |
| 定價資訊 | 否 | 免費方案、$29/月 的 pro |
| CTA 文字 + URL | 否 | "Start Free Trial" → 註冊頁 |
| 客戶見證 | 否 | 使用者提供，不然就跳過這個區塊 |

### 2. 擷取截圖

用 `capture-screenshots`（隨附在 `bin/`）來擷取 app。這比每次都產生 Playwright script 更快、更一致。

#### 快速擷取（一次擷取所有重點頁面）：
```bash
capture-screenshots http://localhost:5173 \
  --pages /,/dashboard,/contacts,/settings \
  --output showcase/screenshots \
  --prefix screen \
  --mobile --dark
```

這一次執行就會為每個頁面產出桌機（1280x720）、手機（375px）和深色模式的版本。

#### 需要登入的 app：
```bash
capture-screenshots https://app.example.com \
  --pages /,/dashboard,/settings \
  --auth user:password \
  --output showcase/screenshots \
  --mobile --dark
```

#### 要擷取什麼：

**a. 第一印象**：主頁面/儀表板會變成 hero 圖。記下它立即傳達的價值主張。

**b. 功能**：每個主要區塊。用 `--pages` 帶入所有導覽路徑。擷取 6-10 個能說出產品故事的重點畫面。

**c. 「運作方式」流程**：依序擷取主要工作流程。操作流程步驟時，多次執行 `capture-screenshots` 並使用 `--prefix workflow-step`。

**d. 細節特寫**：放大特定的 UI 元素。可捲動的內容用 `--full-page`。

**e. 兩種模式**：`--dark` flag 會自動擷取淺色和深色的版本。hero 用比較好看的那個。

#### 擷取後的優化：
```bash
img-process batch showcase/screenshots --action optimise --max-width 1920 -o showcase/screenshots-opt
```

#### f. 提煉價值主張
不要只是列功能。對每一個功能，回答：**使用者為什麼在乎？**
- 不好："Contact management page"
- 好："See every client, their history, and what needs attention — in one view"
- 不好："Search functionality"
- 好："Find anything in seconds — semantic search understands what you mean, not just what you type"

### 3. 產生網站

#### Quick 模式：單一頁面（跟以前一樣）
一個 HTML 檔：hero + 功能格狀 + CTA。用於 MVP 和快速行銷。

#### Standard 模式：多頁面網站

```
showcase/
├── index.html              # Home — hero, overview, feature highlights, CTA
├── features.html           # All features with screenshots and descriptions
├── how-it-works.html       # Step-by-step workflow walkthrough with screenshots
├── screenshots/            # All captured images
│   ├── hero.png
│   ├── feature-*.png
│   ├── workflow-step-*.png
│   └── *.gif               # Animated walkthroughs
└── styles.css              # Shared styles (or inline Tailwind CDN)
```

**首頁**：hero 搭配動畫 GIF 或重點截圖、3-4 個功能亮點（不是全部功能，只挑最好的）、「運作方式」摘要（3 步）、CTA。

**功能頁**：每個功能都有真實截圖和以好處為主的描述。有 6 個以上就依類別分組。每個功能都要留足夠的空間，真的把它在做什麼解釋清楚。

**運作方式頁**：把主要工作流程做成一步一步的視覺指南。每一步有一張截圖（或動畫 GIF）、一個標題和 2-3 句話。這一頁要回答「好，但實際用起來到底是什麼樣子？」

#### Thorough 模式：完整網站

```
showcase/
├── index.html              # Home — hero, overview, value proposition
├── features/
│   ├── index.html          # Feature overview grid
│   ├── [feature-1].html    # Deep-dive: one page per major feature
│   ├── [feature-2].html    # Each with screenshots, GIFs, use cases
│   └── [feature-n].html
├── how-it-works.html       # Full workflow walkthrough
├── use-cases/
│   ├── [use-case-1].html   # Scenario: "A day in the life of..."
│   └── [use-case-2].html   # Scenario: "When a new client calls..."
├── compare.html            # "Why [app] vs alternatives" (optional)
├── screenshots/
│   ├── hero.png
│   ├── feature-*/           # Per-feature screenshot sets
│   └── workflows/           # Animated GIFs
└── styles.css
```

**每個功能的深入介紹頁**：每個主要功能都有自己的一頁，包含：
- 該功能實際運作的 hero 截圖
- 「它做什麼」：1-2 段解釋價值
- 「怎麼運作」：搭配截圖或 GIF 的步驟說明
- 「為什麼重要」：它解決的問題
- 邊緣情況或進階使用者的小技巧
- 連到下一個功能的連結（讓頁面之間有流動感）

**使用情境頁**：以故事為主的頁面，在真實情境中展示 app：
- 「週一早上。你打開儀表板，看到……」
- 帶著讀者走過寫實的工作流程，每一步都有截圖
- 展示結果：因為用了這個 app，有什麼不同
- 對難以解釋的 app 來說，這些是最有說服力的頁面

**比較頁**（選用）："Why [app] vs [alternatives]"：誠實的比較，不是行銷廢話。功能表、關鍵差異點、最適合誰用。

### 4. 動畫 GIF 示範

靜態截圖傳達不出工作流程。對關鍵功能，擷取能呈現實際互動的動畫 GIF：

**如何擷取**（使用 Playwright 或 Chrome MCP）：
1. 導覽到起始狀態
2. 開始以約 2fps 錄製截圖
3. 執行工作流程（點擊、輸入、導覽）
4. 停止錄製
5. 把畫面合成 GIF

**產生 GIF**：先擷取連續的截圖，再合成：
```bash
# Capture each step with a sequential prefix
capture-screenshots http://localhost:5173/clients \
  --prefix workflow-01 --output .jez/screenshots
# ... navigate to next state ...
capture-screenshots http://localhost:5173/clients/new \
  --prefix workflow-02 --output .jez/screenshots

# Combine frames into GIF (Python one-liner using Pillow)
python3 -c "
from PIL import Image; import glob
frames = [Image.open(f) for f in sorted(glob.glob('.jez/screenshots/workflow-*.png'))]
frames[0].save('showcase/screenshots/workflows/create-client.gif',
    save_all=True, append_images=frames[1:], duration=500, loop=0)
"
```

**要做成動畫的內容**：
- 主要的「建立東西」流程（2-4 秒）
- 搜尋/篩選的互動（顯示結果出現）
- 拖放或重新排序的操作
- 深色模式切換（視覺上很療癒）
- 任何 app 做了很驚艷的事的「魔法時刻」（AI 分類、即時搜尋、即時更新）

**GIF 準則**：
- 最長 10 秒 / 20 張畫面，越短越好
- 以 1280x720 擷取，以 640x360 顯示（為了檔案大小縮成一半）
- 在最後狀態多停留一下（3 張畫面），讓觀看者看到結果
- 持續循環播放，不要「點擊播放」
- 如果 GIF 會超過 5MB，就減少畫面或裁切到相關區域

**在 HTML 中顯示**：
```html
<div class="browser-frame">
  <div class="browser-frame-bar">
    <span class="browser-frame-dot"></span>
    <span class="browser-frame-dot"></span>
    <span class="browser-frame-dot"></span>
  </div>
  <img src="screenshots/workflows/create-client.gif"
       alt="Creating a new client in 3 clicks"
       loading="lazy" width="640" height="360">
</div>
```

### 5. 解釋 Agentic / AI app

Agentic app 特別難行銷，因為價值是看不見的：AI 做了使用者從沒看到的工作。標準的截圖只會顯示一個聊天介面，那沒有說服力。

**對 agentic app 有效的模式**：

| 模式 | 展示什麼 | 範例 |
|---------|-------------|---------|
| **前後對比** | 使用者以前手動做的，對比 agent 現在做的 | "Used to: copy-paste from 3 systems. Now: agent does it in background." |
| **時間軸** | 隨時間發生什麼，展示 agent 跨越數小時/數天的工作 | "8am: agent checks inbox. 9am: classifies 47 emails. 10am: flags 3 urgent." |
| **成果展示** | 跳過過程，直接展示產出 | "Agent mined 1,200 emails → 89 clients, 340 contacts, 2,100 knowledge facts" |
| **並排對照** | 把 agent 的成果和人類會做的並排展示 | 分割畫面：左邊是原始 email，右邊是擷取出的結構化資料 |
| **魔法時刻 GIF** | 一段最驚艷的動畫 | 使用者提問 → agent 搜尋知識 → 回傳附上來源的答案 |

**agentic app 的文案技巧**：
- 先講成果，不要講技術（"Know every client's history"，不是 "AI-powered CRM"）
- 展示數量（"Processed 1,200 emails" 比 "Processes your emails" 更有說服力）
- 用時間對比（"What took 2 hours now takes 30 seconds"）
- 避免行話（"Finds connections in your data"，不是 "Semantic vector search with RAG"）

### 5. 截圖的呈現方式

截圖用 CSS 做的瀏覽器外框 mockup 來顯示：

```css
.browser-frame {
  border-radius: 8px;
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
  overflow: hidden;
  border: 1px solid rgba(0,0,0,0.1);
}
.browser-frame-bar {
  background: #f1f5f9;
  padding: 8px 12px;
  display: flex;
  gap: 6px;
}
.browser-frame-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #e2e8f0;
}
```

這樣不用編輯圖片，就能讓截圖有精緻的「瀏覽器裡的 app」質感。

### 6. 網站導覽（多頁面）

多頁面網站需要一致的導覽：

```html
<nav>
  <a href="/">Home</a>
  <a href="/features/">Features</a>
  <a href="/how-it-works.html">How It Works</a>
  <a href="/use-cases/">Use Cases</a>  <!-- thorough only -->
  <a href="#pricing">Pricing</a>
  <button>Get Started</button>
</nav>
```

- 所有頁面都有黏頂的導覽列
- 標示目前所在頁面
- 手機版漢堡選單
- 導覽列上的 CTA 按鈕永遠可見

### 7. 輸出

產生之後，告訴使用者：
- 預覽：`python3 -m http.server -d showcase`，然後打開 `http://localhost:8000`
- 部署：把 `showcase/` 資料夾拖到 Cloudflare Pages、Netlify 或任何靜態主機
- 列出需要替換的佔位內容
- 說明產生了哪些 GIF 以及它們的檔案大小

## 設計模式

**顏色**：如果 app 有明確的品牌色，就擷取出來當主色。不然預設用中性色盤（slate/blue）。

**字型**：系統字型堆疊（不對外請求）。做法跟 `landing-page` 一樣。

**響應式**：Mobile-first，截圖會優雅地縮小。手機上截圖改成垂直堆疊，不用格狀。

**深色模式**：用 CSS custom property 做三態切換（light/dark/system）。

**效能**：截圖圖片 lazy-load。樣式用 Tailwind CDN。不用 build。

## 讓它看起來有質感

### 截圖強化
- **乾淨的資料**：截圖之前，確保 app 裡是寫實的資料，不是 "Test Client" 和 "asdf@example.com"
- **一致的視窗大小**：所有截圖都用同樣的 viewport 寬度（1280x720）
- **截圖裡不要有瀏覽器外框**：用 CSS 的瀏覽器外框 mockup，不要擷取真的 Chrome 工具列
- **突顯動作**：如果截圖要展示某個功能，就讓那個功能處於啟用/開啟狀態（modal 打開、套用了篩選、選中了項目）

### 視覺敘事
- **以儀表板開場**：hero 截圖應該顯示 app 裡有資料、看起來活生生又有用
- **展示 app 在做事**：結果的截圖比空表單的截圖好
- **漸進揭露**：hero 展示大局，運作方式展示流程，功能展示細節
- **以成果收尾**：CTA 之前的最後一個區塊，要展示結果：產出的報告、完成的任務、管理好的客戶

### 混用截圖與 Mockup
真實截圖證明產品是真的。Mockup 證明產品很精緻。兩者並用：
- **Hero**：瀏覽器外框 mockup 裡放真實截圖，證明 app 存在而且看起來很好
- **運作方式**：流程步驟可以用簡化的 mockup 插圖（CSS 形狀、圖示、箭頭），細節處搭配真實截圖
- **功能格狀**：真實截圖，使用者想看實際的 UI
- **手機版展示**：在手機截圖外面套 CSS 裝置外框 mockup（手機輪廓）
- **儀表板/總覽**：真實截圖，這是最關鍵的一張

**手機 mockup 外框**（CSS）：
```css
.phone-frame {
  border: 8px solid #1f2937;
  border-radius: 32px;
  overflow: hidden;
  max-width: 280px;
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.3);
}
.phone-frame-notch {
  background: #1f2937;
  height: 24px;
  border-radius: 0 0 16px 16px;
  width: 120px;
  margin: 0 auto;
}
```

### 動畫（純 CSS，不需要 JS）
```css
/* Fade in sections as user scrolls (intersection observer via CSS) */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.section { animation: fadeInUp 0.6s ease-out both; }

/* Subtle float on hero screenshot */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}
.hero-screenshot { animation: float 6s ease-in-out infinite; }
```

### 漸層點綴
擷取 app 的主色，用在區塊的細緻漸層背景：
```css
.hero { background: linear-gradient(135deg, var(--primary) 0%, transparent 60%); }
.cta-banner { background: linear-gradient(135deg, var(--primary), var(--primary-dark)); color: white; }
```

## 部署

Showcase 網站需要放在真正的地方，不能只是從檔案開啟。依手邊有的資源選擇：

### 選項 1：帶 Static Assets 的 Cloudflare Workers（建議）

如果要展示的 app 已經在 Cloudflare 上，就把 showcase 也部署成 Worker：

```bash
# In the showcase/ directory, create a minimal wrangler.jsonc:
{
  "name": "myapp-showcase",
  "main": "src/index.ts",  // or use static-only pattern
  "compatibility_date": "2026-03-01",
  "assets": { "directory": "./" }
}

npx wrangler deploy
```

也可以綁自訂網域：`showcase.myapp.com`，或 `myapp.com`（如果 app 本身在 `app.myapp.com`）。

### 選項 2：Cloudflare Pages（拖放）

Dashboard → Pages → Create → Upload assets → 拖入 `showcase/` 資料夾。馬上就會得到一個 `.pages.dev` 網址。

### 選項 3：靜態主機（Netlify、Vercel、GitHub Pages）

任何靜態主機都可以，反正只是 HTML + CSS + 圖片。沒有伺服器端程式碼。

### 自訂網域

要呈現專業的 showcase，一定要用自訂網域：
- `myapp.com`：showcase 是主站，app 在 `app.myapp.com`
- `www.myapp.com` → showcase，`app.myapp.com` → 實際的 app

## 聯絡 / 詢問表單

每個 showcase 都需要讓有興趣的人聯絡你的方式。不要只放「寄 email 給我們」，要加一個真的表單。

### 模式 1：Formspree / Formsubmit（不需要後端）

```html
<form action="https://formspree.io/f/YOUR_FORM_ID" method="POST">
  <input type="text" name="name" placeholder="Your name" required>
  <input type="email" name="email" placeholder="Your email" required>
  <textarea name="message" placeholder="Tell us about your needs"></textarea>
  <button type="submit">Get in Touch</button>
</form>
```

免費方案就能應付大部分 showcase 的流量。送出的內容會寄到你的 email。

### 模式 2：Cloudflare Worker endpoint

如果 showcase 在 Workers 上，加一個 `/api/enquiry` route：

```typescript
app.post('/api/enquiry', async (c) => {
  const { name, email, message } = await c.req.json();
  // Send via SMTP2Go, Resend, or store in D1
  await sendEmail({ to: 'hello@company.com', subject: `Enquiry from ${name}`, body: message });
  return c.json({ success: true });
});
```

### 模式 3：Turnstile + email（防垃圾訊息）

加上 Cloudflare Turnstile 來防止機器人送出：
```html
<div class="cf-turnstile" data-sitekey="YOUR_SITE_KEY"></div>
```

處理送出的內容之前，先在伺服器端驗證 token。

### 表單該收集什麼

| 欄位 | 必填 | 為什麼 |
|-------|----------|-----|
| 姓名 | 是 | 讓後續聯絡更個人化 |
| Email | 是 | 回覆管道 |
| 公司/職稱 | 否，但有幫助 | 篩選潛在客戶 |
| 訊息 / "What are you looking for?" | 否，但有幫助 | 回覆時的背景資訊 |
| 電話 | 否 | 有些人偏好打電話 |

**送出之後**：導向感謝頁，或顯示行內確認。不要只是默默地重設表單。

## 值得額外產生的頁面

| 頁面 | 什麼時候放 | 它做什麼 |
|------|----------------|-------------|
| **定價** | 有定義定價時 | 方案卡片、功能比較、計費相關 FAQ |
| **關於** | 有故事的產品 | 誰做的、為什麼做、一路走來的歷程（搭配 jez-voice） |
| **更新日誌** | 已上線的產品 | 最近的更新，顯示產品持續在開發 |
| **文件連結** | 有 app-docs 時 | 連到 `/app-docs` 產生的使用者指南 |
| **部落格 / 文章** | 有內容時 | 連到電子報存檔或關於產品的部落格文章 |
| **隱私權 / 條款** | 一律放 | 就算只是佔位，也能顯示正當性 |
| **狀態頁** | SaaS | 連到服務可用性監控（Cloudflare 健康檢查） |

## SEO 基本功

每個 showcase 頁面都應該有：
```html
<title>[App Name] — [Tagline]</title>
<meta name="description" content="[One sentence value proposition]">
<meta property="og:title" content="[App Name]">
<meta property="og:description" content="[Value proposition]">
<meta property="og:image" content="screenshots/hero.png">
<link rel="canonical" href="https://myapp.com/">
```

多頁面時：每頁都要有自己的 title 和 description。不要所有頁面都用同樣的 meta。

如果產品服務特定地點，用 `seo-local-business` skill 產生 JSON-LD。

## 品質規則

1. **只截真的有的功能**：不要捏造 app 沒有的能力
2. **挑最好的截圖**：不是每個頁面都值得展示。挑能說出產品故事的
3. **寫以好處為主的文案**："See all your contacts in one place"，不是 "Contact list page"
4. **不要假的客戶見證**：沒有提供就把這個區塊拿掉
5. **不要編造統計數字**：沒有真實資料，統計區塊就留空
6. **部署到真正的 URL**：不要只留成本機檔案。showcase 需要能分享
