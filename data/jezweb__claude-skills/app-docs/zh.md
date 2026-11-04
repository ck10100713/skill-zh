---
name: app-docs
description: "替 web app 產出附截圖的完整使用者文件。用瀏覽器自動化瀏覽這個 app、替每個畫面截圖，產出結構化的使用指南，包含逐步說明、標註截圖、流程圖和參考表格。支援 quick（關鍵畫面）、standard（所有頁面）、thorough（每個狀態和流程）和 exhaustive（可對外發布的完整文件組）。觸發詞：'document the app', 'user guide', 'app documentation', 'screenshot docs', 'generate user docs', 'help docs', 'how-to guide', 'write the docs'。"
compatibility: claude-code-only
---

# App Documentation Generator

瀏覽一個執行中的 web app，替每個畫面截圖，產出好到可以對外發布的文件。不是截圖傾倒場，而是一份教人怎麼使用這個 app 的結構化指南。

## 瀏覽器工具偵測

跟 ux-audit 一樣：Chrome MCP、Playwright MCP 或 playwright-cli。

## URL 判斷

跟 ux-audit 一樣：優先用已部署的正式 URL，不要用 localhost。

## 深度等級

| 深度 | 截圖數 | 產出 | 時間 |
|-------|------------|-----------------|----------|
| **quick** | ~10 | 單頁快速上手指南。只有關鍵畫面和順利走完的主流程。 | 10-15 分鐘 |
| **standard** | ~30 | 完整的使用指南。所有頁面、主要工作流程、參考表格。 | 30-60 分鐘 |
| **thorough** | ~80+ | 全面的指南。所有狀態、手機版畫面、每個 CRUD 流程、疑難排解。 | 1-3 小時 |
| **exhaustive** | ~150+ | 可對外發布的完整文件組。包含 thorough 的所有內容，另外加上：入門教學、逐功能深入說明、管理員指南、鍵盤快速鍵參考、FAQ 和 HTML 版本。 | 3-6 小時 |

預設：**standard**

## 工作流程

### 1. 取得 App 資訊

問使用者：
- **App URL**（必填，或從 wrangler.jsonc / 執行中的 dev server 自動偵測）
- **App 名稱**（用在指南標題）
- **驗證**：Chrome MCP 使用他們的 session；Playwright 需要憑證
- **深度**：quick、standard、thorough 或 exhaustive
- **讀者**：誰會讀這份文件？（終端使用者、管理員、新進團隊成員、客戶）

### 2. 找出所有路由

瀏覽 app，建立完整的頁面清單：
- 讀側邊欄/導覽選單
- 逐一點過所有頂層項目和子項目
- 記下子頁面、頁面內的分頁籤和巢狀導覽
- 檢查設定、個人檔案、管理區域和說明頁面
- 記錄每個頁面的 URL 和用途
- 記下哪些頁面有互動元素（表單、按鈕、篩選器）

建立一份任務清單來追蹤文件進度。

### 3. 替每個頁面寫文件

清單裡的每個頁面：

#### a. 前往並準備
- 前往該頁面
- 等資料載入完成（截圖裡不要有骨架畫面或轉圈圈）
- 把瀏覽器調整成 1280x720，讓截圖尺寸一致
- 確認頁面有貼近真實的資料，不要是「Test Client」或空的表格

#### b. 替預設狀態截圖
- 截一張乾淨的圖，呈現資料已填好的頁面
- 用有描述性的名稱存到 `docs/screenshots/`

#### c. 寫頁面的段落

每個頁面要寫：

```markdown
## [Page Name]

[One sentence: what this page is for and when you'd use it]

![Page name](screenshots/NN-page-name.png)

### What You'll See
[Describe the key elements: sidebar shows X, main area shows Y, toolbar has Z]

### What You Can Do
[List the actions available, each as a brief description]

### How To: [Primary Action]
1. [Step with screenshot reference]
2. [Step]
3. [Step — screenshot the result]

> **Tip:** [Helpful shortcut or non-obvious feature]
```

#### d. 記錄關鍵工作流程

互動式的頁面，每個重要步驟都附截圖，逐步記錄：

```markdown
### How To: Add a New Client

1. Click the **"Add Client"** button in the top right
   ![Add button location](screenshots/12-clients-add-button.png)

2. Fill in the required fields — Name and Email are required, everything else is optional
   ![New client form](screenshots/13-clients-new-form.png)

3. Click **"Save"** — you'll be taken to the new client's detail page
   ![Client saved confirmation](screenshots/14-clients-saved.png)

> **Tip:** You can also press **Cmd+N** from anywhere to create a new client.
```

#### e. 各深度額外要做的

| 額外項目 | quick | standard | thorough | exhaustive |
|-------|-------|----------|----------|-----------|
| 空狀態 | 略過 | 記一筆 | 截圖 + 寫進文件 | 截圖 + 提出改善建議 |
| 錯誤狀態 | 略過 | 記一筆 | 觸發 + 截圖 | 每個驗證錯誤都記錄 |
| 深色模式 | 略過 | 略過 | 關鍵頁面截圖 | 每個頁面都截圖 |
| 手機（375px） | 略過 | 略過 | 關鍵頁面截圖 | 每個頁面都截圖 |
| 所有 CRUD | 略過 | 只做主要的 | 每個操作 | 每個操作 + 邊界情況 |
| 設定/組態 | 略過 | 列出選項 | 每個都記錄 | 每個都記錄並附範例 |
| 鍵盤快速鍵 | 略過 | 看得到的就列出 | 完整的參考表格 | 獨立的章節 |
| 搜尋/篩選 | 略過 | 提一下 | 記錄每個篩選器 | 記錄每種組合 |
| 權限/角色 | 略過 | 略過 | 記下差異 | 每個角色一個獨立章節 |
| API/整合 | 略過 | 略過 | 有的話提一下 | 記錄 endpoint + 範例 |

### 4. 寫輔助章節

除了逐頁的文件之外：

**Getting Started**（所有深度）：
```markdown
## Getting Started

### Accessing [App Name]
- URL: [production URL]
- Supported browsers: Chrome, Firefox, Safari, Edge
- Mobile: [responsive / PWA / not supported]

### Logging In
[Screenshot of login page + steps]

### Your First 5 Minutes
1. [First thing to do after logging in]
2. [Second thing — the quick win]
3. [Third thing — explore the main feature]
```

**導覽指南**（standard 以上）：
```markdown
## Navigation

### Sidebar
[Screenshot with annotations describing each section]

### Quick Actions
- **Cmd+K**: Quick switcher — jump to any page or record
- **Cmd+N**: Create new [item]
[Other shortcuts]

### Breadcrumbs / Back Navigation
[How to navigate back, where breadcrumbs appear]
```

**鍵盤快速鍵參考**（thorough 以上）：
```markdown
## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Cmd+K | Quick switcher |
| Cmd+N | New [item] |
| Cmd+S | Save |
| Escape | Close dialog / cancel |
```

**疑難排解**（thorough 以上）：
```markdown
## Troubleshooting

### [Error message or symptom]
**What it means**: [explanation]
**How to fix**: [steps]

### Common Questions
[FAQ generated from what would confuse a new user — based on the documentation process itself]
```

**管理員指南**（exhaustive）：
```markdown
## Admin Guide

### User Management
[How to invite users, set roles, remove access]

### Settings Reference
| Setting | What it does | Default | Recommendation |
[Every setting documented]

### Data Management
[Export, import, backup, delete account]
```

### 5. 輸出格式

**Markdown**（預設）：`docs/USER_GUIDE.md`
- 圖片用相對路徑：`![alt](screenshots/NN-description.png)`
- GitHub 風格的 markdown，在 GitHub、VS Code、Obsidian 都能正常渲染

**HTML**（exhaustive 深度，或使用者要求時）：`docs/user-guide.html`
- 單一、自給自足的 HTML 檔案，用 Tailwind CDN
- 截圖用相對路徑（不用 base64，檔案大小才合理）
- 帶平滑捲動的目錄側邊欄
- 友善列印的 CSS（`@media print`）
- 支援深色模式

**截圖命名**：`docs/screenshots/NN-section-description.png`
- 用數字決定排序：`01-`、`02-`、`03-`
- 章節前綴：`01-dashboard-`、`05-clients-`、`12-settings-`
- 描述性的後綴：`-overview.png`、`-add-form.png`、`-saved-confirmation.png`

### 6. Mockup 與圖表

在有助於理解的地方，把截圖和圖表混搭：

**流程圖**（純文字，不需要外部工具）：
```markdown
### How a Client Moves Through the System

```
New Enquiry → Create Client → Add Policy → Send Renewal → Archive
     ↓              ↓              ↓             ↓            ↓
  [Email]    [Client Page]   [Policy Page]  [Email Outbox]  [Archive]
```
```

**標註截圖**：截圖需要標註說明時，在文字裡描述：
```markdown
![Dashboard](screenshots/01-dashboard.png)

The dashboard shows:
- **A** (top left): Your client count and active policies
- **B** (centre): Items needing attention today
- **C** (right): Recent activity feed
```

**UI 元素參考**：複雜的頁面，附一張有標籤的圖會有幫助：
```markdown
### Editor Layout

| Area | What it does |
|------|-------------|
| Left panel | Folder tree — organise your notes |
| Centre panel | Note list — shows notes in the selected folder |
| Right panel | Editor — write and preview your note |
| Top bar | Navigation, search (Cmd+K), and view toggles |
```

## 截圖品質

- **解析度**：1280x720（桌面）、375x812（手機）
- **資料**：用貼近真實的資料。不要「Test」或「Lorem ipsum」。照這個 app 實際會被使用的方式來用。
- **時機**：等資料載入完成。最終的截圖不要有轉圈圈，也不要有骨架畫面。
- **狀態**：讓頁面呈現在有用的狀態，資料已填好、相關區塊已展開、關鍵功能看得到
- **一致性**：全程使用同樣的 viewport 尺寸、同樣的縮放比例、同一個瀏覽器
- **深色模式**：要記錄深色模式的話，在截圖**之前**就切換好，不要在同一個章節裡混用兩種模式

## 自主權規則

- **直接做**：瀏覽頁面、截圖、讀頁面內容、寫文件
- **簡短確認**：寫大型文件檔案之前
- **先問**：送出含真實資料的表單之前、點擊刪除之前
- **Thorough/exhaustive 模式**：寫檔案和用測試資料填表單時，不用確認

## 品質標準

文件要好到：

1. **新使用者照著指南就能完成任何任務**，不用求助
2. **每張截圖都有脈絡**：我在看什麼？我該做什麼？
3. **步驟是原子的**：每個編號步驟一個動作，絕對不要寫成「點 X 然後填 Y 和 Z」
4. **小提示能揭露隱藏的價值**：快速鍵、進階功能，以及使用者自己不會發現的東西
5. **疑難排解是真的**：根據寫文件過程中實際遇到的困惑時刻，不是憑空假設的 FAQ
6. **容易掃讀**：標題、截圖、表格、小提示。沒有人會從頭讀到尾，他們是搜尋自己需要的東西。
