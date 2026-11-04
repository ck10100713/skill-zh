---
name: discover-brand
description: >
  這個 skill 負責協調在各企業平台（Notion、Confluence、Google Drive、Box、SharePoint、Figma、Gong、Granola、Slack）
  上自主探索品牌素材。當使用者要求「discover brand materials」、
  「find brand documents」、「search for brand guidelines」、「audit brand content」、
  「what brand materials do we have」、「find our style guide」、「where are our brand docs」、
  「do we have a style guide」、「discover brand voice」、「brand content audit」，
  或「find brand assets」時使用。
---

# Brand Discovery

協調在各企業平台上自主探索品牌素材。這個 skill 會調度 discover-brand agent，去搜尋已連接的平台（Notion、Confluence、Google Drive、Box、Microsoft 365、Figma、Gong、Granola、Slack）、篩選來源，並產出一份附有待釐清問題的結構化探索報告。

## 探索流程

### 0. 先讓使用者了解流程

開始之前，先簡短說明接下來會發生什麼，讓使用者知道該預期什麼：

"Here's how brand discovery works:

1. **Search** — I'll search your connected platforms (Notion, Google Drive, Slack, etc.) for brand-related materials: style guides, pitch decks, templates, transcripts, and more.
2. **Analyze** — I'll categorize and rank what I find, pull the best sources, and produce a discovery report with what I found, any conflicts, and open questions.
3. **Generate guidelines** — Once you've reviewed the report, I can generate a structured brand voice guideline document from the results.
4. **Save** — Guidelines are saved to `.claude/brand-voice-guidelines.md` in your working folder once you approve them. Nothing is written until that step.

The search usually takes a few minutes depending on how many platforms are connected. Ready to get started?"

等使用者確認後才繼續。如果他們對流程有疑問，先回答。

### 1. 檢查設定

如果 `.claude/brand-voice.local.md` 存在，就讀取它。擷取：
- 公司名稱
- 啟用了哪些平台（notion、confluence、google-drive、box、microsoft-365、figma、gong、granola、slack）
- 搜尋深度偏好（standard 或 deep）
- 來源數量上限
- 列在「Known Brand Materials」底下的任何已知品牌素材位置

如果沒有設定檔，就用所有已連接的平台和標準搜尋深度繼續。

### 2. 驗證平台覆蓋度

確認範圍之前，先檢查實際連接了哪些平台並加以分類：

**文件平台**（品牌指南、風格指南、範本和簡報所在的地方）：
- Notion、Confluence、Google Drive、Box、Microsoft 365（SharePoint/OneDrive）

**輔助平台**（對找 pattern 有價值，但不是存放品牌文件的地方）：
- Slack、Gong、Granola、Figma

套用這些規則：

1. **如果一個文件平台都沒連接**：**停下來。** 告訴使用者：「You don't have any document storage platforms connected (Google Drive, SharePoint, Notion, Confluence, or Box). Brand guidelines and style guides almost always live on one of these. Please connect at least one before running discovery. Gong/Granola/Slack transcripts are valuable supplements but unlikely to contain formal brand documents.」

2. **如果 Google Drive、Microsoft 365 和 Box 都沒連接**：**警告**（但繼續）：「None of your primary file storage platforms (Google Drive, SharePoint, Box) are connected. Brand documents frequently live on these platforms. Discovery will proceed with [connected platforms], but results may have significant gaps. Consider connecting Google Drive or SharePoint.」

3. **如果總共只連接了一個平台**：**警告**（但繼續）：「Only [platform] is connected. Discovery works best with 2+ platforms for cross-source validation. Results from a single platform will have lower confidence scores.」

### 3. 跟使用者確認範圍

啟動探索之前，先確認：
- 要搜尋哪些平台（預設：所有已連接的）
- 要不要包含對話逐字稿（Gong、Granola），還是只看文件
- 有沒有要優先看的已知位置

保持簡短：只問一個問題，不要變成問卷。

### 4. 委派給 Discover-Brand Agent

透過 Task 工具啟動 discover-brand agent。提供：
- 公司名稱（來自設定或使用者輸入）
- 啟用的平台
- 搜尋深度
- 要優先檢查的任何已知 URL 或位置

這個 agent 會自主執行四階段的探索演算法：
1. **Broad Discovery**：跨平台平行搜尋
2. **Source Triage**：來源分類與排序
3. **Deep Fetch**：從最優先的來源取回並擷取內容
4. **Discovery Report**：附有待釐清問題的結構化輸出

### 5. 呈現探索報告

agent 回傳後，把報告連同摘要呈現給使用者：
- 找到並分析的來源總數
- 發現的關鍵品牌元素
- 來源之間的任何衝突
- 需要團隊決定的待釐清問題

### 6. 提供後續步驟

呈現報告之後，提供這些選項：
1. **現在就產生 guideline**：以探索報告當輸入，接到 `/brand-voice:generate-guidelines`
2. **先解決待釐清問題**：產生之前，先處理高優先級的問題
3. **儲存報告**：把探索報告存到 Notion 或本機檔案
4. **擴大搜尋**：覆蓋度偏低時，搜尋更多平台或搜得更深

## 待釐清問題

探索 agent 遇到無法自行解決的模糊之處時，就會產生待釐清問題：
- 互相衝突的文件（例如 2023 年的風格指南 vs. 2024 年的品牌更新）
- 缺少關鍵段落（例如找不到社群媒體指南）
- 各平台之間用詞不一致

每個待釐清問題都附帶一個 agent 的建議。把問題呈現成「確認或推翻」，不要讓它變成死路。

## 與其他 skill 的整合

- **Guideline Generation**：探索報告由 discover-brand agent 透過 Task 工具回傳。直接把它當成結構化輸入交給 guideline-generation skill，就不需要使用者手動蒐集來源。
- **Brand Voice Enforcement**：探索產生 guideline 之後，enforcement 會自動使用它們。

## 錯誤處理

- 如果一個平台都沒連接，就告訴使用者這個 plugin 支援哪些平台，以及怎麼連接。
- 如果所有搜尋都回傳空結果，就把這次探索標記為「low coverage」，並建議使用者手動提供文件或檢查平台連線。
- 如果某個平台已連接但回傳權限錯誤，就註明這個缺口，並繼續處理其他平台。

## 參考檔案

詳細的探索 pattern 和演算法，請參考：

- **`references/search-strategies.md`**：各平台專屬的搜尋查詢、各平台的查詢 pattern，以及把探索覆蓋度拉到最高的訣竅
- **`references/source-ranking.md`**：來源類別定義、排序演算法的權重，以及篩選決策的標準
