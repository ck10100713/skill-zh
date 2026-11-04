---
name: ux-audit
description: "以真實使用者的身分走過一個上線的 web app，找出靜態 review 抓不到的可用性與行為 bug。在給出任何判定之前，必須有互動證明（打字、點擊、送出、觀察），沒有互動過的掃描只能以 'Incomplete' 判定收場。會走過各條 thread、逐一操作每個元素、執行多窗格壓力矩陣、視覺細節掃描、元件完美度檢查清單、自動化無障礙檢查（axe-core）、務實的效能預算（LCP/CLS/INP）、情境測試組（11 個情境），以及包含真實風味資料測試組的壓力測試配方。硬性關卡：console error/warning = 0、network 5xx = 0、版面崩壞 = 0、axe Critical/Serious = 0、效能預算過關。Audit-the-audit 的 meta 檢查會退回草率的報告。每個 finding 都要有重現步驟、證據路徑和疑似的程式碼位置。觸發詞：'ux audit'、'walkthrough'、'qa sweep'、'audit the app'、'dogfood this'、'check all pages'、'find what's broken'、'stress the UI'。"
compatibility: claude-code-only
---

# UX Audit

以真實使用者的身分走過一個上線的 web app。這個 audit 是**互動優先**的：打字、點擊、送出、觀察、截圖。只做靜態 DOM 掃描，不能產出判定。

## 判定狀態

Audit 只會以下面其中一種狀態結束：

- **Pass**：Critical = 0、High = 0、所有硬性關卡都過、Interaction Manifest 完整。
- **Conditional Pass**：Critical = 0、High = 0、所有硬性關卡都過，但還有 Medium/Low。
- **Fail**：至少有一個 Critical 或 High finding，或有硬性關卡沒過。
- **Incomplete**：Interaction Manifest 缺少必要項目、有階段沒跑，或 audit-the-audit meta 檢查被觸發（manifest 時間戳記擠在 < 0.5 秒內、截圖少於 2 × route 數、console 讀取少於 1 × route 數、完整 audit 的 Phase 3 花不到 1 分鐘）。就算觀察到的一切看起來都沒問題，也不准升級成 Pass。

如果工作內容沒有完整的 Interaction Manifest，唯一合法的判定就是 **Incomplete**。「看起來沒問題」不是 Pass。時間不合理的乾淨 Pass 會被退回，agent 必須用真正的互動重做 audit。

## 硬性關卡

這些會讓 audit 自動失敗，不能降級。

| 關卡 | 門檻 | 違反時的嚴重度 |
|------|-----------|----------------------|
| Walkthrough 期間的 console error | > 0 | Critical |
| Walkthrough 期間的 console warning | > 0 | High |
| Network 5xx | > 0 | Critical |
| 需登入頁面上的 Network 403 / 404 | > 0 | High |
| 任何測試的 viewport / 窗格組合出現版面崩壞 | > 0 | High |
| 任何被 audit 的頁面出現 axe-core Critical 違規 | > 0 | Critical |
| 任何被 audit 的頁面出現 axe-core Serious 違規 | > 0 | High |
| 代表性 route 的 LCP（務實預算） | > 4.0s | High |
| 代表性 route 的 CLS | > 0.25 | High |
| 代表性 route 的 INP | > 500ms | High |
| 缺少必要的 Interaction Manifest 項目 | n/a | Incomplete |
| Manifest 項目之間的中位數間隔 < 0.5s | n/a | Incomplete（根本沒有真的互動） |

Console warning 的嚴重度**最低**是 High。5xx **自動**是 Critical。這個 skill 裡沒有「Medium 的 console error」，這個類別不存在。

axe-core 的門檻是**每頁**執行（任何單一頁面有 >1 個違規就算失敗）。效能門檻只在**一個代表性 route 上執行一次**（每頁都跑太過頭了）；務實預算遠高於壞掉的程度，遠低於嚴格的 CWV。完整門檻與理由在 [references/performance-budget.md](references/performance-budget.md)。完整的無障礙接線與嚴重度對應在 [references/a11y-automation.md](references/a11y-automation.md)。

### 已知雜訊的 allowlist

有些 app 有已知會吵、但不算 bug 的 console / network 類別（Sentry 的 info log、瀏覽器擴充功能的雜訊、驗證檢查探測時預期的 401）。在 Phase 3 之前先讀 audit-config 檔，套用裡面的 allowlist。路徑的 fallback 順序：`.jez/audit-config.yml` → `audit-config.yml` → `.audit/config.yml`。在 allowlist 裡的項目仍會留在 Interaction Manifest 裡，但不會出現在 findings 裡。判定區塊會同時顯示原始數字和 allowlist 後的數字：`Console warnings: 3 (1 allowlisted, 2 reportable)`。

沒有設定檔時的預設：每一個 console error / warning 都是 finding。格式、語意、各 surface 的覆寫方式在 [references/audit-config.md](references/audit-config.md)。

## 階段（依序）

1. **Pre-flight**：Persona Lock、瀏覽器工具、URL、viewport、能力測試
2. **Discovery**：sitemap、thread 清單、元素清單
3. **Walkthrough**：Interaction Manifest、thread、逐一操作元素、多窗格壓力測試、首次使用者視角、即時互動 smoke 測試
4. **Polish**：視覺細節掃描、元件完美度檢查清單
5. **Stress**：情境測試組（11 個情境）+ 延伸的壓力測試配方
6. **Verdict**：判定狀態、硬性關卡計分表、完美度路線圖、附重現步驟的 findings
7. **Fix-and-verify**：修補 findings、重新走過受影響的部分、更新報告

如果只是要在部署前做 30 秒的快速檢查，用這個檔案最下面的 dogfood drill，那是專案層級的規則，不是呼叫 skill。

## Phase 1：Pre-flight

五道關卡。任何一道沒過就停下來。

### 1. Persona Lock

Audit 在做任何事之前都需要一個 persona。沒有鎖定 persona 的話，findings 會漂向泛泛的「看起來沒問題」。

依下列順序取得 persona：

1. **參數**：使用者有給的話（"ux audit as a busy insurance broker"）
2. **專案 persona**：讀既有的 persona 檔案（fallback 順序：`.jez/audit-personas/<slug>.md` → `docs/personas/<slug>.md` → `personas/<slug>.md` → `.audit/personas/<slug>.md`）。第一個找到的就用。
3. **問一次**：*"Who uses this app and what are they trying to get done?"*

記錄：角色、對科技的熟悉程度、時間壓力、情緒狀態、使用裝置的情境。好的 persona 能預測他們會漏掉什麼（"A receptionist between phone calls won't scroll below the fold"）。

把選定的 persona 寫在 audit 報告的最上面來鎖定。每個 finding 都必須站得住腳，要能從這個 persona 的角度成立。如果你發現自己在想 *"a developer would know..."*，停下來。你的 persona 不知道。

**不管明確指定的 persona 是誰，一律也要執行首次使用者視角**（強制，見 Phase 3），每個多頁面功能都要做。這是 AI / 內部工具最大的盲點。

persona 資料庫與撰寫方式見 [references/persona-lock.md](references/persona-lock.md)。

### 2. 瀏覽器工具

| 目標 | 工具 | 原因 |
|--------|------|-----|
| **需登入的 app** | Chrome MCP | 用你真正登入的 Chrome session，OAuth、cookie、RBAC 都直接能用 |
| **公開網站** | Playwright MCP | 不需要登入 |
| **兩個都沒有** | **停下來** | 請使用者連接 Chrome MCP 或安裝 Playwright |

**不要**悄悄退回用全新的 Playwright session 去測需登入的 app，登不進去的話 audit 就沒有價值。如果 Chrome MCP 沒連上，就停下來說：*"Open Chrome, click Connect in the Claude extension, then rerun."*

指令見 [references/browser-tools.md](references/browser-tools.md)。

### 3. URL

優先用已部署/上線的版本：真實的驗證、真實的延遲、真實的 CDN 和 CORS。找 URL 的方式：讀專案的 CLAUDE.md / README 找 "URL" → 檢查技術堆疊設定（`wrangler.jsonc`、`vite.config.ts`、`next.config.js`、`config/database.yml`、`manage.py`、`.env` 的 `APP_URL`、`wp-config.php`）→ `lsof -i :PORT`（常見：5173 Vite、3000 Next/Rails、8000 Django/Laravel、8787 Wrangler、4321 Astro）→ 問使用者。各技術堆疊的指南在 [references/project-adaptation.md](references/project-adaptation.md)。只有使用者要求，或該功能還沒部署時，才用本機。

### 4. Viewport

一開始把視窗固定在 1440×900。Phase 3 的多窗格壓力測試會測 375 / 768 / 1024 / 1280 / 1440 / 1920。**不要超過 2000px**，會讓測試工具壞掉。

### 5. 能力測試

在任何 walkthrough 之前，先證明工具能用，各呼叫一次：

- 一張截圖
- 一次 console 讀取
- 一次 network request 清單
- 一次元素 selector 查詢

任何一個失敗，就先停下來修好連線再開始 audit。看不到 console 輸出的 audit 毫無價值。

## Phase 2：Discovery

### Sitemap 爬取

在 audit 任何頁面之前，先建立完整的頁面清單。

1. **Router 設定**：讀 app 的 route 定義（React Router、TanStack Router、Next.js app 目錄）
2. **導覽爬取**：點過側邊欄/選單的每個區塊和子區塊
3. **Deep link**：CLAUDE.md、文件或先前的 audit 報告裡的 URL

每個 route 一行，附上用途：`/app/clients — list of clients, search, add new`。

### Thread 清單

找出 3–5 個構成使用者一天的真實任務。這些是 audit 的主幹。

怎麼找：問使用者、讀 CLAUDE.md / README、從頂層導覽推斷。範例：保險經紀人 → 續保一張保單、建立一個客戶、處理今天的佇列。專案管理 → 早上的分流、更新一個任務、寄客戶摘要。Spaces / 聊天 app → 建立一個 space、送出一則訊息、開一個 thread。

### 元素清單

走到每個 route 時，列出每一個可互動的元素。清單是邊走邊建，每頁走到時才建，不要一開始就全部建好。這會驅動覆蓋率指標：*"tested 29 of 31 elements on /app/clients"*。

## Phase 3：Walkthrough（audit 本身）

### Interaction Manifest（強制）

每次 walkthrough 都要產出一份 manifest。沒有它，判定 = Incomplete。

```
INTERACTION MANIFEST — /dashboard/spaces/marketing-pod
  Persona: SME owner, time-pressed, low tech comfort
  [✓] 14:32:01 Typed "@assistant test" into message input (textarea[placeholder*="message"])
  [✓] 14:32:03 Picked @assistant from autocomplete (li[data-mention-id="assistant"])
  [✓] 14:32:05 Clicked Send (button[aria-label="Send"])
  [✓] 14:32:06 Verified input cleared within 1000ms (textarea.value === "")
  [✓] 14:32:08 Verified message appeared in transcript ([data-message-id] count +1)
  [✓] 14:32:12 Opened thread on the message ([data-thread-trigger])
  [✓] 14:32:13 Verified main column width ≥ 200px after thread open (getBoundingClientRect().width)
  [✓] Console read after each step (0 warnings, 0 errors)
  [✓] Screenshot before + after each step
  [✓] Network requests inventoried (0 5xx, 0 403/404 on auth pages)
```

每個勾選都需要一次工具呼叫（一次點擊、一張截圖、一次 console 讀取），並且要記錄時間戳記和 selector。沒有完整的 manifest，agent 就不能產出「Pass」報告。

**每個被 audit 的頁面必須有的項目**：

- ≥ 1 個輸入框打了字（真的文字，不是只有點擊）
- ≥ 1 個主要動作被觸發（Send / Save / Submit / Create / Publish，看哪個適用）
- ≥ 1 個 modal 或詳細面板被開啟
- ≥ 1 次主要動作之後的 console 讀取
- 主要動作之前**和**之後各 ≥ 1 張截圖
- 驗證預期的動作後狀態（輸入框清空、成功 toast、route 切換、列表更新）

完整模板與重播流程在 [references/interaction-manifest.md](references/interaction-manifest.md)。

### Thread 走查

對每個 thread：

1. **從 app 的入口點開始**，不要從 thread 中間開始。真實使用者會落在 `/` 或 `/dashboard`。
2. **以 persona 的身分走**：如果他們會快速掃過，你就快速掃過。如果他們會看錯標籤，你也看錯。記下遲疑的地方。
3. **每個狀態變化都截圖**：預設 → hover/focus → active → 點擊後 → 載入後 → 確認。這一連串的畫面就是證據。
4. **追蹤成本**：點擊次數、決策點、死路、中斷後恢復（在第 3 步關掉分頁、第 4 步再回來，狀態還在嗎？）
5. **每個 thread 結束時，把截圖交給 sub-agent 審視。**

每個 thread 結束時，以 persona 的身分回答：*Did it end clearly? Would I come back? One thing to make this twice as easy?*

見 [references/walkthrough-checklist.md](references/walkthrough-checklist.md) 和 [references/workflow-comprehension.md](references/workflow-comprehension.md)。

### 逐一操作元素

對每個 route，把元素清單處理完。跳過已經在 thread 走查時操作過的元素。細節在 [references/walkthrough-checklist.md](references/walkthrough-checklist.md)。

對**每個列表/表格**，資料允許的話，測 0 / 1 / 100 / 1000+ 筆的量。

### 多窗格壓力測試（有可收合 UI 的 app 強制執行）

窗格的組合會藏住最嚴重的版面 bug。2026-04-29 那個 spaces 裡文字直排的 bug，只有在 1024-1280px 且三個窗格全開時才出現。對有側邊欄 / 成員 / thread / drawer / sheet 的 app，要跑這個矩陣：1920 / 1440 / **1280（高 bug 率）** / **1024（災難級 bug）** / 768 / 375 × 全開、2 窗格、1 窗格、預設。每個組合都要：捲到最長的內容、截圖、執行版面偵測用的 JS，檢查溢出 / 被裁切 / 文字直排堆疊。完整矩陣 + JS 片段 + 自動化在 [references/multi-pane-stress.md](references/multi-pane-stress.md)。

### 首次使用者視角（強制）

在鎖定的 persona 之外，每個多頁面功能都必須通過**首次使用者**檢查。這能抓出內部/AI 工具最大的 UX 失敗模式：設計它的人做出來的功能，對他們自己好用，但第一次登入同一個畫面的全新使用者，完全不知道任何控制項是什麼意思。

採用*第一次登入這個 app、沒有任何先前背景、沒有原始碼可看、沒有內部文件*的人的 persona。每個畫面都問：

| 問題 | 能抓到什麼 |
|---|---|
| 不讀程式碼或文件，我能完成任務嗎？ | 藏在表單裡的技術知識 |
| 欄位標籤是白話，不是內部用語嗎？ | `agentClass`、`slug`、`webhook_id` 洩漏到 UI 上 |
| 下拉選單 / 挑選器顯示的是**每個選項做什麼**，而不只是一個 ID 嗎？ | snake_case enum、原始 class 名稱、看不懂的 slug |
| 預設值好到我可以直接留著繼續嗎？ | 沒有預設值的必填欄位、強制要輸入的 ID 欄位 |
| 需要輸入東西時，有沒有可以找得到的合法值清單？ | 該用 combobox 卻用自由輸入的欄位 |
| 如果我因為看不懂某個設定而想說「點 Skip」，那就是 UX bug。 | 選填但令人困惑的設定，被當成主要輸入暴露出來 |

當這個視角被觸發時，就算畫面在技術上能運作，也要記一個 finding。常見的修法：把文字輸入改成挑選器、顯示 metadata、自動推導數值、把內部 ID 藏到 "Advanced" 底下、加上行內引導。

當一個全新的 persona 不需要場外協助就能完成任務，這個畫面才算通過這個視角。

### 即時互動 Smoke 測試

讀程式碼只能確認按鈕存在、有 `onClick`。無法確認點下去真的會有可觀察的結果。對每一頁的每一個可互動控制項：

1. **點它。** 指標移動、元素 highlight、點擊命中。
2. **看 Network 分頁。** 有送出 request 嗎？URL 對嗎？method + body 正確嗎？
3. **看 DOM。** 有沒有可見的變化：新元素、被移除的元素、狀態轉換？
4. **如果 (2) 或 (3) 都沒變化，那就是 bug。**

已知會無聲失敗的控制項（tool-call 卡片上的 Approve/Deny、對話框裡的 OAuth 被彈出視窗攔截、非同步驗證的表單、樂觀 UI 的刪除、差一的分頁、搭配過期 TanStack Query 的篩選 chip、沒有 Message-ID 的 Reply/Forward）：完整的無聲失敗清單和 SDK 契約檢查（`@ai-sdk/react`、better-auth、TanStack Query、React Router v7、Radix Dialog、zodResolver）見 [references/live-interaction-smoke.md](references/live-interaction-smoke.md)。

### 往返工作流程完整性（強制）

由 battery 裡的情境 10 涵蓋（Phase 5）。在 Phase 3 的 walkthrough 也要跑：走 thread 時遇到的每個 A→B→A 流程，在繼續之前都要做往返檢查。完整流程在 [references/round-trip-workflows.md](references/round-trip-workflows.md)。

### 響應式掃描

在每個寬度都跑版面偵測 JS（溢出、被裁切、看不見的文字）。記錄轉換點。搭配上面的多窗格壓力測試，才算完整涵蓋。

### Audit 途中驗證過期

如果導覽或 API 呼叫在先前已驗證的 route 上回傳 401/403，代表 session 掉了。**不要悄悄重新驗證**，因為之後的每個觀察都被污染了。停下來，記錄壞掉的那一步（無聲過期本身就是一個 finding），以 `Incomplete` 判定終止，建議重新驗證並重新開始。完整流程與 finding 的條件在 [references/auth-expired-handling.md](references/auth-expired-handling.md)。

## Phase 4：Polish

### 視覺細節掃描

逐頁的微細節打磨，涵蓋十種 AI 痕跡類別：視覺置中、巢狀圓角規則、不在刻度上的間距、氛圍灰、邊框粗細漂移、drop-shadow 方向、動畫時間偏離標準值、hover 差異校準、底線 / 大寫字母的字距、對稱 vs 編輯式的節奏。

再加上對按鈕、badge、輸入框、下拉選單、卡片、tab、頭像、toast 的逐元件視覺檢查。

含 DevTools 工作流程、嚴重度指南和校準用參考 app 的完整流程，在 [references/visual-polish.md](references/visual-polish.md)。

### 元件完美度檢查清單

頁面層級的 audit 抓不到的元件層級細節。六個類別，每個都有具體的是/否檢查，需要證據：

1. **按鈕與觸發元件**：狀態清晰、意圖對應、微文案、載入狀態、層級
2. **輸入與表單**：持續顯示的標籤、遮罩、行內驗證、錯誤清楚、預設值
3. **導覽與層級**：我在哪裡？、點擊深度、搜尋邏輯、固定的標頭
4. **視覺一致性**：icon 一致、空狀態、圓角、對比度
5. **行動裝置與觸控**：可點擊面積（≥ 48×48）、鍵盤最佳化、滑動手勢
6. **效能與回饋**：skeleton 畫面、成功 toast、只有高風險才用確認 modal

再加上每個主要元件的六種視覺狀態（default、skeleton、empty、partial、error、disabled），空白上放個 skeleton 不算 skeleton。

報告裡的每個勾選都要引用一個證據（截圖、console 那一行、DOM selector、程式碼參照）。沒有證據就不算。

完整檢查清單在 [references/perfection-checklist.md](references/perfection-checklist.md)。

### 自動化無障礙檢查（axe-core，強制）

手動只用鍵盤走（情境 5）能抓到 focus trap 和 tab 順序。但會漏掉約 80% 的結構性無障礙 bug（標題層級跳過、hover/focus 對比失敗、缺少 aria-label、role 不符）。axe-core 每頁不到 1 秒就能涵蓋這 80%。

對每個被 audit 的頁面：

1. 透過 CDN 注入 axe-core（一個 script 標籤）。
2. 頁面穩定後執行 `axe.run()`。
3. 把違規對應成 audit 的 finding（axe `critical` → audit Critical，axe `serious` → audit High，以此類推）。
4. 硬性關卡：任何一頁有 > 0 個 axe Critical 或 > 0 個 axe Serious = audit 失敗。

16 個 route 的 audit 總執行時間約 16 秒。建構者模式的參考頁面（Components、Style guide）可以透過專案的 audit-config 設定 allowlist（路徑 fallback 順序見 [references/audit-config.md](references/audit-config.md)）。完整片段、嚴重度對應和 findings 格式在 [references/a11y-automation.md](references/a11y-automation.md)。

### 效能預算（務實版，強制）

在一個代表性 route（真實使用者最常去的頁面，通常是 dashboard 或主要工作畫面）上執行一次 Performance API 擷取。務實門檻（LCP < 4.0s、CLS < 0.25、INP < 500ms）遠高於壞掉的程度，遠低於 Google CWV 的「Good」等級。CWV 嚴格版是給 landing page 和行銷團隊用的，對真實使用者長時間待在裡面的 app 內部頁面，務實版才是對的標準。

加進判定區塊。任何門檻被突破都是硬性關卡失敗。用 Chrome DevTools 的 Performance trace 診斷（大型 hero、晚載入的字型、沉重的 click handler、hydration 成本）。完整的測量片段、節流規格和常見元凶在 [references/performance-budget.md](references/performance-budget.md)。

## Phase 5：Stress

### 情境測試組（11 個情境）

十一個全部都要跑，一個都不能少。它們能抓到逐畫面測試漏掉的東西。完整流程在 [references/scenario-tests.md](references/scenario-tests.md)。

1. **First Contact**：在完全沒有先備知識的情況下摸清 app，為每個 thread 寫一份兩分鐘的白話指南。
2. **Interrupted Workflow**：開始一個任務，關掉分頁、重新整理、在表單填到一半時離開。狀態還在嗎？
3. **Wrong Turn Recovery**：故意點錯。要點幾次才能恢復？
4. **Returning User**：重複一個 thread。有變快嗎？有捷徑嗎？看得出從上次造訪後有什麼變了嗎？
5. **Keyboard Only**：每個 thread 都只用鍵盤。focus 看得見、tab 順序合理、Escape 能關閉。
6. **Heavy Data**：塞 500+ 筆資料。列表有虛擬化、搜尋回傳對的東西、篩選有縮小範圍。
7. **Destructive Confidence**：每個刪除/送出/發布/付款/分享：同意流程清楚、文案具體、可以復原。
8. **Second User (Role)**：受限的角色（viewer 不是 editor、client 不是 staff）。唯讀畫面、權限錯誤。
9. **Lifecycle Position**：同一個角色，分別在使用者 #1（創辦人）、#2（第一個被邀請的人，部分狀態）、#N（後來加入的人，工作區已有內容）。每個人看到的現實不同。
10. **Round-Trip Workflow Integrity**：每個 A→B→A 流程：在 B 完成變更，驗證回到 A 時不用重新整理就反映新狀態。找得到返回的入口。標頭的 badge 有更新。這是「我回去之後專案怎麼是空的」這類問題最大的來源。
11. **Data Seasoning**：Day 0 / 1 / 7 / 30 的資料時間範圍。有時間形狀的資料能抓到只有數量的 seed 抓不到的東西：時間分隔線、依最近排序、cron 觸發的副作用、通知 badge 溢出、有歷史紀錄時的搜尋效能、圖表分桶。只有在完全沒有依時間分布的資料時才可以跳過。

### 延伸壓力測試配方

除了情境之外，還要跑 [references/stress-test-recipes.md](references/stress-test-recipes.md) 裡每一個相關的配方：

| 壓力測試 | 能抓到什麼 |
|--------|-----------------|
| 空的 / 飽和的 / 超長內容 | AI 開發時很少看到的邊緣版面 |
| Race condition（連點兩下、快速輸入後立刻 blur、慢網路） | 樂觀 UI 的 bug、debounce 失效 |
| 慢網路（3G 節流） | 載入狀態、skeleton 節奏、逾時 UX |
| 減少動態（`prefers-reduced-motion: reduce`） | 無視這個偏好設定的動畫 |
| i18n（很長的德文、RTL 阿拉伯文、CJK 字寬） | 對文字長度的版面假設 |
| 離線模式 | 重試 / 佇列 / 未儲存狀態的 UX |
| 列印樣式表 | 被遺忘的 media query |
| 高對比模式 | forced-colors media query 的處理 |
| **真實風味資料測試組**（任何接受表單的 app 強制執行） | 默默去掉字元的驗證（撇號、重音符號、RTL）；沒有警告就被截斷的長度；沒被 escape 的 SQL/XSS canary；放不進去的檔案上傳（.heic、8000×8000 的 PNG、50MB 的 PDF）。AI 做出來的 UI 出了名的只吃乾淨的開發資料。 |

## Phase 6：Verdict

### 判定區塊（強制放在報告最上面）

```
═══════════════════════════════════════════════════════════
VERDICT: [Pass / Conditional Pass / Fail / Incomplete]

Persona: [locked persona slug]
Surfaces audited: N / M routes
Interaction Manifest: complete / incomplete (X of Y required entries)

Hard Gates: console errors [N], warnings [N], network 5xx [N], 403/404 auth [N], layout-collapse [N], axe Critical [N], axe Serious [N]   (all must be 0; allowlisted counts shown in parens)
Performance (on /[route]): LCP [N]s / CLS [N] / INP [N]ms — thresholds 4.0s / 0.25 / 500ms

Findings:
  Critical: [count]    High: [count]    Medium: [count]    Low: [count]

Self-critique pass (sub-agent): Drafted: [N]  Kept: [N]  Generic: [N]  Duplicate: [N]

Time per phase: Phase 3 [N]m / Total [N]m   (Phase 3 ≥ 5m for exhaustive)
Manifest plausibility: [N] entries (≥ 6/route), median gap [N]s (< 0.5s = Incomplete), [N] screenshots (≥ 2/route)

TOP 5 (ranked by impact × ease, senior-designer pick):
  1-5. [F-id] Title — one-sentence reason this edges out the others
═══════════════════════════════════════════════════════════
```

Top 5、Self-critique pass，以及（Phase 7 之後的）Hold-this-in-your-hands 結尾段落都是強制的。缺少的話，判定就是 `Incomplete`。完整規範、格式和反模式在 [references/audit-output-discipline.md](references/audit-output-discipline.md)。

### Self-critique pass（發布前強制）

Findings 草稿寫完之後，派一個全新的 sub-agent，給它草稿清單和這段 prompt：

> *"Read these audit findings. For each, mark KEEP / GENERIC / DUPLICATE. KEEP = specific to this app, this persona, this surface. GENERIC = would apply to any web app. DUPLICATE = same root cause as another finding. Drop GENERIC and DUPLICATE before publishing."*

用全新的 sub-agent 才有效，因為原本的起草者會護著自己的產出。在原本 context 裡做的自我批判，往往是在辯護而不是修剪。記錄這次 pass：`Drafted: 23  Kept: 14  Generic: 5  Duplicate: 4`。

### Audit-the-audit 觸發條件（不可妥協，自動翻成 Incomplete）

| 訊號 | 代表 |
|---|---|
| 完整 audit 的 Phase 3 花不到 1 分鐘 / manifest 首尾跨度 < 5 分鐘 | Walkthrough 被跳過或太趕 |
| Manifest 項目之間的中位數間隔 < 0.5s | 項目是批次產出的，沒有真正互動 |
| 截圖少於 2 × route 數 / console 讀取少於 1 × route 數 | 頁面其實沒有真的被檢查 |
| Top 5 缺少，或用填充的名額湊數 | 規範被破壞（見 [audit-output-discipline.md](references/audit-output-discipline.md)） |
| 沒有記錄 self-critique pass | 填充的東西沒被修剪 |
| Findings 用了 "Suggested fix" / "Consider X" / "Improve Y" | 是填充型的修補，不能直接 commit |
| `[✓]` PASS 列沒有一句話的證明 + 證據 | 憑感覺的 PASS |
| 缺少 Hold-this-in-your-hands 段落 | 沒有做整體判斷 |

### Findings 格式（每個 finding 強制）

每個 finding 都必須包含：**ID**（嚴重度字母 + 編號）、**Layer**（Architecture / Interaction / Visual / Feedback / Delight）、**Severity**、**Surface**（route + viewport + 窗格）、**Persona**、**Reproduce**（編號步驟）、**Observed**、**Expected**、**Evidence**（截圖路徑 + console / network 擷取）、**Suspected location**（`file:line`）、**Smallest possible patch**（具體且可 commit，*不是* "Suggested fix" / "Consider X"）。沒有重現步驟 + 證據 + 疑似位置的 finding 會被退回。填充型的修補（"improve X"、"consider Y"、"make Z better"）會被 self-critique pass 翻成 Incomplete。實際範例和 Five-Layer Hierarchy 在 [references/report-template.md](references/report-template.md) 和 [references/perfection-checklist.md](references/perfection-checklist.md)。規範細則在 [references/audit-output-discipline.md](references/audit-output-discipline.md)。

### Hold this in your hands（強制的結尾段落）

每個 audit 都以一段話收尾，沒有模板，回答：*if this app were a physical object, would I want to hold it?* 這是唯一一個「感覺」就是重點的地方，是任何檢查清單都抓不到的整體判斷。格式和實際範例在 [references/audit-output-discipline.md](references/audit-output-discipline.md)。

### 完美度路線圖（強制）

把 findings 分成：

- **Quick Wins（24-48 小時）**：微文案、hover 狀態、對比修正、一行 CSS 調整
- **Structural（1-2 週）**：替換基礎元件、重組 route、多窗格重構
- **Advanced Polish（上線後）**：微動畫、skeleton 變化、個人化的空狀態

完整報告結構在 [references/report-template.md](references/report-template.md)。

## Phase 7：Fix-and-verify

報告之後，提議這個循環：

> *"Found N Critical and M High issues. Fix them now and re-verify?"*

如果使用者同意：
1. 把 findings 依檔案/區域分組
2. 一個一個修補
3. **只重新走受影響的部分**（不是整個 app），包括當初發現 bug 的那個互動，並重新截圖
4. 更新報告：標記 `✓ fixed`、`✗ still present`，或 `⚠ new issue found`
5. 以「本次 session 修好的項目」摘要收尾

在一個 session 裡就把循環收掉，不用等明天再 audit。

## 與 ux-extract 和 brains-trust 的交叉參考

如果已經有 pattern library（fallback：`.jez/artifacts/ux-extracts/<ref>.md` → `docs/ux-extracts/<ref>.md` → `audits/extracts/<ref>.md`），開始前先讀，並把它當作 findings 的標準。

判定之後，可以選擇性地跑 `dev-tools:brains-trust` 做第二意見的 review（每 4-6 週一次）。合併 findings 回來時，**用 `(reproduction-steps, suspected-location)` 去重**，同一個 bug 被第二個模型也找到，算是一個 finding 有兩次確認，不是兩個 finding。加一行 `Confirmed by:`。不要把第二份報告原封不動貼上去，會產生雜訊並讓嚴重度膨脹。

## 30 秒 Dogfood Drill（專案層級規則）

Audit 很重。每次改動的部署前檢查，建議在 CLAUDE.md 裡放一條專案規則：

> **Before declaring any UI change "done", run the 30-second dogfood drill:**
> 1. Open the affected page
> 2. Type into any input
> 3. Click the primary action
> 4. Watch the next state for 2 seconds
> 5. Open a related view (thread, modal, detail)
> 6. Read the console
> If any step shows unexpected behaviour, the change isn't done.

六個步驟，約 30 秒。能抓到立刻浮現的行為 bug。搭配每週一次的完整 ux-audit。

## Playwright 關鍵流程測試

Audit 找出現在壞掉的東西。測試防止 regression。建議為關鍵流程寫 10-15 個 Playwright 測試，起手範例見 [references/playwright-killer-flows.md](references/playwright-killer-flows.md)（送出後輸入框清空、掛載時沒有 console warning、開 thread 後訊息欄寬度 ≥ 200px、@-mention 剛好一個 pill 等）。每次部署都用 CI 執行。

## 自主權

- **直接做**：導覽、截圖、讀頁面、注入版面偵測 JS、用假的測試資料送出表單、寫報告檔、派出審視截圖的 sub-agent。
- **先問**：破壞性動作（刪除、送出、發布、付款）。做 Destructive Confidence 測試時，在跑那個情境之前先問一次。
- **停下來確認**：任何會寄 email / 通知外部人員的事。

## 執行紀律

1. **從主 session 驅動 audit，不要交給 sub-agent。** 跨互動的狀態活在一路看下來的那個 session 裡。全新的 sub-agent 是冷啟動，會漏掉二階的 findings。
2. **直接使用瀏覽器工具。** 從主 session 用 Chrome MCP 或 Playwright MCP。不要把截圖交給全新的 agent 要它的意見。
3. **用變化版本一直跑到窮盡為止。** 每一輪之後，產生一個新角度（不同的 persona、不同的工作流程、不同的輸入量、不同的起點）。只有在完整跑完一輪都沒有新 finding 時才停。

預計跑超過 30 分鐘的 audit，在主 session 旁邊設定一個 15 分鐘的 `/loop` check-in，它會記錄 findings、讓 session 保持踏實，並提供自然的終止訊號。見 [references/long-running-check-in-pattern.md](references/long-running-check-in-pattern.md)。

## 參考檔案

| 時機 | 讀這個 |
|------|------|
| **跨 skill 的輸出規範**（Top 5、self-critique、最小修補、有證據的 PASS、hold-this） | [references/audit-output-discipline.md](references/audit-output-discipline.md) |
| **專案適配**：非預設的技術堆疊（NextAuth/Lucia/Devise/Django auth、Prisma/TypeORM/ActiveRecord seed、WordPress/Rails/Django 的 URL 探索、依 app 類型分的 persona 資料庫） | [references/project-adaptation.md](references/project-adaptation.md) |
| Persona 資料庫 + 撰寫流程 + persona 過載的處理模式 | [references/persona-lock.md](references/persona-lock.md) |
| Audit 途中驗證過期：流程 + 無頭測試驗證的恢復 | [references/auth-expired-handling.md](references/auth-expired-handling.md) |
| 資料 seasoning 的時間範圍（Day 0 / 1 / 7 / 30）+ 專案 seed 腳本的架構 | [references/data-seasoning.md](references/data-seasoning.md) |
| Audit-config allowlist 的格式 + 語意 + 各 surface 的覆寫 | [references/audit-config.md](references/audit-config.md) |
| Interaction Manifest 模板 + 重播流程 | [references/interaction-manifest.md](references/interaction-manifest.md) |
| 多窗格壓力矩陣 + 自動化片段 | [references/multi-pane-stress.md](references/multi-pane-stress.md) |
| 每個畫面的評估問題、版面偵測 JS | [references/walkthrough-checklist.md](references/walkthrough-checklist.md) |
| 導引、心智模型、頁面之間的連貫性 | [references/workflow-comprehension.md](references/workflow-comprehension.md) |
| 11 個情境各自的完整流程 | [references/scenario-tests.md](references/scenario-tests.md) |
| 延伸壓力測試配方（race、慢網路、減少動態、i18n） | [references/stress-test-recipes.md](references/stress-test-recipes.md) |
| 元件層級的完美度檢查清單（6 個類別 + 6 種狀態） | [references/perfection-checklist.md](references/perfection-checklist.md) |
| AI 痕跡目錄、視覺置中、design token 紀律 | [references/visual-polish.md](references/visual-polish.md) |
| 無聲失敗的控制項 + SDK 契約檢查 | [references/live-interaction-smoke.md](references/live-interaction-smoke.md) |
| Playwright 關鍵流程測試的起手範例 | [references/playwright-killer-flows.md](references/playwright-killer-flows.md) |
| 報告格式、判定區塊、嚴重度標準、重現步驟格式 | [references/report-template.md](references/report-template.md) |
| 瀏覽器工具指令與 viewport 備註 | [references/browser-tools.md](references/browser-tools.md) |
| 往返工作流程完整性（A→B→A 模式） | [references/round-trip-workflows.md](references/round-trip-workflows.md) |
| 自動化無障礙檢查（axe-core 注入 + 嚴重度對應） | [references/a11y-automation.md](references/a11y-automation.md) |
| 務實的效能預算（透過 Performance API 取得 LCP/CLS/INP） | [references/performance-budget.md](references/performance-budget.md) |
| 用 15 分鐘 `/loop` 監督長時間 audit | [references/long-running-check-in-pattern.md](references/long-running-check-in-pattern.md) |

## 小技巧

- **每一次遲疑都是一個 finding。** 如果你停下來想該點哪裡，那就是值得回報的摩擦。
- **多用滴管工具。** 這是找氛圍灰、不在 token 裡的顏色、design system 漂移最快的方法。
- **覆蓋率是算術。** 清單中的數量 ÷ 測過的數量。把比例公布在報告裡。
- **截圖審視和寫 findings 交給 sub-agent，並且邊做邊寫。** 不要在同一個迴圈裡又驅動瀏覽器、又分析 200 張截圖。報告檔案是比你的 context 更便宜的記憶體。
