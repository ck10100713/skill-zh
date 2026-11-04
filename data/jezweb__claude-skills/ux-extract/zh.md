---
name: ux-extract
description: "徹底擷取參考 web app 的 UX 模式。走過每個畫面、擷取每個狀態的截圖、記錄互動模式、逐字抄下文案、鍵盤快捷鍵、響應式處理、動態效果，以及空/錯誤/載入狀態。產出可重複使用的 pattern library，供其他 audit 拿來比較。是 ux-audit 的反面：問的是「標準是什麼？」，而不是「這個符合標準嗎？」。觸發詞：'learn from X'、'extract patterns from X'、'study X's UX'、'reverse engineer the UX of X'、'build a pattern library from X'。"
compatibility: claude-code-only
---

# UX Extract

徹底研究一個參考 web app，產出可重複使用的 pattern library。走遍每個地方、擷取所有東西，再整理成一份供其他 audit 或開發參考的文件。

是 `ux-audit` 的反面：
- **Audit** 問：*這個符合標準嗎？*
- **Extract** 問：*標準是什麼？*

沒有 extract 的 audit，其實是在跟「我對其他 app 的記憶」比較，既脆弱又不一致。Extract 把那份記憶變成具體、可以瀏覽的產物。這樣 audit 就可以說：*"Empty state on /app/clients shows no CTA. Reference (claude.ai) shows 3 keyboard shortcuts plus 'New chat' in the same position"*，而不是 *"feels a bit sparse"*。

## 什麼時候用

- **做新功能之前**：研究頂尖的 app 怎麼處理
- **替開發做基準比較**：先 extract 參考，再拿來 audit
- **帶設計師或工程師上手**：具體展示「好」長什麼樣
- **競品研究**：記錄競爭對手的 UX，才能做出有意義的差異化
- **翻新舊的 app**：從現代的同類產品 extract 模式，作為更新的指引

## 範圍與倫理

開始之前，先確認目標可以研究：

1. **用你自己的帳號**：不要爬任何需要你沒有合法持有的憑證的東西
2. **尊重 `robots.txt`**，針對未登入的爬取
3. **限制頻率**：表現得像真人使用者，不要像爬蟲。頁面之間要暫停。
4. **檢查 ToS**：大多數 SaaS 的服務條款允許個人檢視，但禁止自動化爬取
5. **不要公開轉散布**上線中的競品 app 截圖，pattern library 是內部參考資料

如果目標在付費牆後面或需要試用帳號，繼續之前先問使用者是否有合法的存取權。

## 設定

### 1. 瀏覽器工具

| 目標 | 工具 | 備註 |
|--------|------|-------|
| **需登入的參考**（你有帳號） | Chrome MCP | 使用你已登入的 session |
| **公開的參考**（行銷頁、文件、公開 demo） | Playwright MCP | 不需要登入 |

指令見 [../ux-audit/references/browser-tools.md](../ux-audit/references/browser-tools.md)。

### 2. Viewport

以 1440×900 為基準（MacBook 標準）。也要擷取 768 和 375 來看響應式模式。寬度不要超過 2000px。

### 2b. 截圖後處理

在 Retina Mac 上，Chrome 以邏輯 viewport 的 2 倍擷取，1440 寬的視窗會產出 2880 寬的 PNG。每批之後做後處理，免得 library 裡塞滿過大的檔案：

```bash
img-process batch ./screenshots --action optimise --max-width 1440
```

具冪等性，對已經夠小的檔案不會有動作。在每個 route 的擷取結束時執行，或在 extract 結束時對整個 `screenshots/` 資料夾執行。Playwright MCP 的使用者可以在 context options 裡設定 `deviceScaleFactor: 1`，就能跳過這一步。

### 3. 範圍

開始之前先決定：

- **整個 app**：走過所有能到達的地方（可能要好幾個小時，產出完整的 library）
- **功能領域**：一個區塊（"the settings flow"、"the dashboard"、"the billing flow"）
- **模式類別**：只做 empty state、只做錯誤處理、只做 onboarding

範圍越窄，library 越緊湊、越有用。「整個 app」只對你要做直接類比的 app 才值得。

### 4. 焦點視角（選用）

擷取時選用的偏重。範例：
- *"Focus on patterns for data-heavy lists"*：優先擷取表格、篩選、搜尋、虛擬化的截圖
- *"Focus on onboarding and empty states"*：優先擷取首次使用流程和無資料畫面
- *"Focus on permission boundaries"*：以多個角色登入，記錄差異

沒有給焦點的話，就廣泛擷取。

## Discovery

### Sitemap 爬取

建立完整的 route 清單：

1. **公開 sitemap**：檢查 `/sitemap.xml`、`/robots.txt` 看有沒有可探索的資訊
2. **導覽爬取**：點過頂部導覽、側邊欄、頁尾裡看得到的每個區塊
3. **App 內探索**：進去之後，記下出現的每個連結（麵包屑、tab、情境選單）
4. **URL 檢查**：有些 app 在 `/settings`、`/preferences`、`/admin` 裡有有用的模式，但不在主導覽裡

記錄每個 route 和它的用途：`/settings/billing — subscription plan, payment method, invoice history`。

### 模式清單

在深入擷取之前，先掃過 app 一遍，列出你要記錄的模式類型。典型的類別：

- Wayfinding（導覽、麵包屑、目前位置、返回）
- 列表與表格（列、hover、動作顯示、選取、排序、篩選、分頁、空狀態）
- 表單（標籤、驗證、錯誤、必填、行內說明）
- Modal 與對話框（觸發、focus、escape、捲動、確認）
- 回饋（toast、行內、進度、載入、已儲存）
- Onboarding 與 empty state（首次使用、無資料時的 CTA、導覽教學）
- 權限與角色（受限的畫面、拒絕存取、角色指示）
- 文案與微文案（按鈕、標題、錯誤、placeholder、tooltip）
- 鍵盤（快捷鍵清單、focus、tab 順序、command palette）
- 動態（轉場、顯示、載入、手勢）
- 響應式（breakpoint、行動版專屬：bottom sheet、tab、滑動）

不是每個 app 都會用到每個類別。標記哪些適用。

## 擷取階段

對每個 route，徹底擷取。截圖很便宜，寧可多拍。

### 截下所有狀態

每個有意義的元素都要擷取：

| 狀態 | 觸發方式 |
|-------|---------|
| Default | 頁面載入完成，沒有任何互動 |
| Hover | 滑鼠移到按鈕、列、導覽項目上 |
| Focus | 用 Tab 讓鍵盤 focus |
| Active | 按鈕點擊到一半、輸入框正在輸入 |
| Open | 下拉選單展開、選單展開 |
| Closed | 下拉選單收合、選單收合 |
| Expanded | 手風琴展開、詳細面板展開 |
| Collapsed | 手風琴收合 |
| Selected | checkbox 勾選、列被選取、tab 啟用 |
| Loading | skeleton、spinner、等待中狀態 |
| Empty | 沒有項目的列表 |
| Populated | 有很多項目的列表 |
| Error | 行內、toast，或整頁錯誤 |
| Success | 動作之後的確認 |

完整的各模式檢查清單見 [references/capture-checklist.md](references/capture-checklist.md)。

### 逐字擷取文案

把文字完全照抄，包括標點、刪節號和語氣：

- 按鈕標籤：`"Start chat"`、`"Upgrade plan"`、`"Delete forever"`
- Empty state：*"No conversations yet. Start one to see it here."*
- 錯誤訊息：*"We couldn't save that change. Try again, or contact support if it keeps happening."*
- 確認對話框：*"Delete this project? All 14 tasks and 3 members will be removed. This cannot be undone."*
- Placeholder 文字：`"e.g. smith@company.com"`
- Tooltip：`"Pressing Cmd+K opens this from anywhere"`

原始文案對寫作者來說是黃金，也能幫你的 app 找到自己的語氣。

### 擷取互動

對每個可互動的元素，記下：
- **Trigger**：點擊 / hover / 鍵盤 / 長按 / 拖曳
- **Target**：影響什麼（開啟 modal、篩選列表、導覽跳轉）
- **Feedback**：有立即的視覺回應嗎？延遲的確認？
- **Reversibility**：可以復原嗎？是破壞性的嗎？

### 擷取鍵盤模式

- **快捷鍵清單**：有沒有 `?` 或 `Cmd+/` 可以叫出快捷鍵列表？擷取下來。
- **Command palette**：有 `Cmd+K` 或類似的嗎？擷取 palette 開啟、搜尋中、選中一個結果、執行一個動作的畫面。
- **Focus 指示**：用 tab 走過整個頁面，記下外框的樣式、顏色、粗細
- **Tab 順序**：合邏輯嗎？有沒有出乎意料的跳躍？

### 擷取響應式處理

對每個 route，在 1440、768、375 各截一張圖。記下**改變了什麼**，而不只是「它能用」：
- 導覽在 [breakpoint] 從側邊欄變成漢堡選單
- 表格在 [breakpoint] 收合成堆疊的卡片
- Modal 在 [breakpoint] 變成全螢幕
- 多欄表單在 [breakpoint] 變成單欄

### 擷取動態

為任何值得記錄的動畫錄一個 GIF（Chrome MCP 的 `gif_creator`）：
- 頁面轉場
- Modal 進場/退場
- 列表項目進場/退場
- 載入中 → 載入完成
- 成功動畫（彩帶、打勾）
- 拖放的回饋

一個 3 秒的 GIF 勝過一段文字描述。

## 去重階段

擷取完之後，許多模式會出現在多個頁面。去重：

- **5 個列表頁都有相同的列模式** → 一個「list row」條目，附註 *"used on: /clients, /projects, /invoices, /reports, /team"*
- **相同的 empty state 版面但文案不同** → 一個「empty state」條目，列出文案的變化
- **相同的 modal 外框** → 一個「modal」條目；特定的 modal 列為使用範例

每個模式記兩個數字：
- **Occurrences**：這個模式出現幾次
- **Variants**：有意義的差異（有 icon vs 沒有、小 vs 大、有 CTA vs 沒有）

只出現一次的模式很少值得記錄，除非它很獨特、值得注意。

## 輸出

寫到 `docs/ux-extracts/<app-name>/`（如果 `.jez/artifacts/ux-extracts/<app-name>/` 這個目錄存在，就寫到那裡）：

```
docs/ux-extracts/claude-ai/
├── pattern-library.md      ← main document
├── copy-corpus.md          ← optional, raw copy by page (for writers)
└── screenshots/
    ├── 001-home-default.png
    ├── 002-home-hover-cta.png
    ├── 003-new-chat-empty.png
    └── ...
```

輸出結構見 [references/pattern-library-template.md](references/pattern-library-template.md)。

這份 pattern library 應該要：
- **可瀏覽**：最上面有目錄，每個區塊都有跳轉連結
- **交叉參照**："see also: [Modal Chrome](#modal-chrome)"
- **截圖密集**：每個論述都有引用的截圖支撐
- **文案準確**：逐字的文字放在 code block 或 blockquote 裡，不要改寫
- **誠實**：要記下*缺少*或*弱*的地方，也要記下好的地方。參考用的 library 不是聖經。

## ux-audit 如何使用它

`ux-audit` 會檢查 `.jez/artifacts/ux-extracts/<ref>/pattern-library.md` 或 `docs/ux-extracts/<ref>/pattern-library.md` 有沒有 pattern library。找到的話，就把它當作比較的標準。這樣 audit 的 findings 就可以引用特定的模式：

> *"Empty state on /app/clients has no explanatory copy and no CTA. Reference library [claude.ai § Empty States] shows CTA + 2 example prompts in the same position."*

只要把 library 產出在預期的路徑，不需要其他整合。

## 自主權

- **直接做**：導覽、截圖、複製文字、注入 JavaScript 讀取 computed style、下載靜態資產（logo、icon）作為參考
- **先問**：任何需要使用者沒有授權你使用的憑證的登入，以及任何 ToS 或頻率限制不明確的網站爬取
- **停下來確認**：如果目標有登入牆，而你沒有明確的授權，繼續之前先停下來確認

## 參考檔案

| 時機 | 讀這個 |
|------|------|
| 建立 pattern-library.md 的輸出 | [references/pattern-library-template.md](references/pattern-library-template.md) |
| 各模式的擷取檢查清單（要截什麼、要記什麼） | [references/capture-checklist.md](references/capture-checklist.md) |
| 瀏覽器工具指令 | [../ux-audit/references/browser-tools.md](../ux-audit/references/browser-tools.md) |

## 小技巧

- **截圖很便宜**，大方擷取。把一張截圖從 library 裡拿掉，比為了拿到一張而重跑 extract 容易得多。
- **看到文案的當下就擷取**，不要打算之後再回來，等你回來時它會在不同的狀態後面。
- **記下缺少的東西**：如果某個 app 沒有快捷鍵清單，那也是值得記錄的模式決策。
- **把觀察和評價分開**：extract 記錄存在什麼，而不是它好不好。意見屬於 audit，不屬於 extract。
- **Extract 會衰退**：app 會變。在 library 上加上時間戳記，可能的話連結到 archive.org 上的那個日期，對你常拿來比較的 app，計畫每 6–12 個月重新 extract 一次。
- **漸進式建立**：一開始就打開 library 檔案，邊做邊追加。不要打算最後才一次整理結構。
