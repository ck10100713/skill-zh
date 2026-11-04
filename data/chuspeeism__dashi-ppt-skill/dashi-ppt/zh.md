---
name: dashi-ppt
description: 製作 PPT、簡報、幻燈片、彙報材料時使用。Dashi PPT 基於預置視覺主題組合頁面,生成可離線開啟、可在瀏覽器編輯的 HTML 演示,支援匯出 PPTX / PDF 檔案。
---

# Dashi PPT

Dashi PPT 生成靜態 HTML 橫向翻頁 PPT。使用本 skill 時,先把使用者的自然語言需求整理成 JSON 計劃,再呼叫本地專案生成器輸出 `index.html` 和 `assets/`。


## 版本

當前版本: `0.4.14`

每次完成使用者請求、準備最終回覆前,執行:

```bash
node <skill-root>/scripts/check_latest_version.mjs
```

如果指令碼有輸出,把輸出內容附在最終回覆末尾提醒使用者更新;如果指令碼無輸出或檢查失敗,保持靜默,不要提版本檢查。

## Skill 目錄

當前 `SKILL.md` 所在目錄就是 Skill 根目錄,下文記為 `<skill-root>`。

內建生成器目錄:

`<skill-root>/project`

渲染指令碼:

- macOS / Linux: `<skill-root>/scripts/render_goal_deck.sh`
- Windows PowerShell: `<skill-root>/scripts/render_goal_deck.ps1`

版本檢查指令碼:

`<skill-root>/scripts/check_latest_version.mjs`

## 生成原則

本 Skill 為每個邏輯頁生成 3 個模板方案和 1 個 Agent 定製方案,輸出可離線開啟的 HTML PPT。

前三個模板方案使用“鎖模板填文案”:保留所選頁面元件的原始視覺、結構、數量、顯隱、強調、配色、圖表型別和圖片槽位,只替換可見文字內容。除非使用者明確要求調整頁面屬性,不要改任何非文案 props。第四個方案由 Agent 在當前主題視覺語言內按本頁內容定製,不屬於模板候選。

成果驗收是預設流程。每次生成後都要判斷最終產物是否達到使用者目標;預設檢查目標、內容、結構、明顯可見問題和交付完整性,不做截圖審美精修,不因普通斷行反覆返工。使用者明確要求“視覺精修”“100% 檢查”“幫我調到滿意”時,再擴充套件為視覺 QA。

## 使用規則

- 執行生成器需要 Node.js 20+ 和 npm;首次生成時渲染指令碼會在 Skill 內建 `project/` 目錄安裝依賴。Windows 用 `render_goal_deck.ps1`(直接 PowerShell,不經 WSL/bash);macOS / Linux 用 `render_goal_deck.sh`。
- 風格選擇提問:使用者可見回覆必須嵌入 `<skill-root>/assets/skill/theme-style-grid.png` 的 Markdown 圖片,先展開絕對路徑;這是回覆展示用內建風格圖,不可寫入 `goal.json` 或任何 media 欄位;列出當前可選風格和極簡“適合/人群”,不能只在內部進度提示中提到風格圖。
- 開工前確認兩件事:主題風格、是否需要圖片/影片。使用者未明確表達且非整體委託時,先提問等答覆,不得代選;無法提問的環境(指令碼/批處理)才自選,並在交付說明中列出所選與理由。
- 委託模式:僅當使用者對整體明確委託(“都你來定”“不用問,直接開幹”)時,才自選主題、預設 HTML、預設不使用 image-gen,最終說明假設。使用者只說內容/文案“隨意”“自擬”時,僅自擬內容;風格、頁數、媒體等已給的不得擅自改變,未給的按上一條先問。
- 非互動/一次性執行(無法追問)時:未指定風格按內容主題自選已驗收主題;無真實素材且不能生圖時優先選無媒體頁,不調 image-gen;最終說明全部假設。
- Deck 語言跟隨使用者溝通語言:非中文使用者在 `goal.json` 頂層加 `"language": "en"`;全部文案欄位用目標語言撰寫,頁面自帶的預設中文文案(含結尾頁“感謝閱讀”類裝飾欄位)一律覆蓋,不得殘留中文。編輯器介面語言自動跟隨開啟者的系統語言,右上角可手動切換,無需在生成時處理。
- 交付格式:預設 HTML;“生成 PPT”“做 PPT”“做一個 PPT”“製作 ppt”表示 PPT 呈現形態。只有明確 `PPTX`、`PowerPoint`、`可編輯 PPTX`、`匯出 PPTX`、`PPT 格式` 或“格式/檔案型別為 PPT/PPTX”時才交付 PPTX 檔案。
- PPTX 檔案:仍先生成 HTML 並啟動本機預覽服務,再呼叫本機 HTTP 匯出服務;最終只給 PPTX 檔案路徑或下載結果。
- 當前可選風格: `theme01` 輕擬態風、`theme02` 炫光紫綠風、`theme03` 深淺程式碼風、`theme04` 玻璃糖果風、`theme05` 色譜圖表風、`theme06` 深色圖譜風、`theme07` 冷白調研風、`theme08` 黑金實驗風、`theme09` 深藍雜誌風、`theme10` 金色指數風、`theme11` 高能增長風、`theme12` 聲波霓虹風。
- 普通自動選擇不選 `theme10`;只有使用者明確指定,或金融/投資指數內容強相關且 inspect 確認可填時才用。
<!-- theme-choice-hints:start -->
  - `theme01` 輕擬態風 | 適合: 產品介紹 / 企業彙報 | 人群: 創業團隊 / 產品經理
  - `theme02` 炫光紫綠風 | 適合: 科技釋出會 / AI/自動駕駛/機器人主題 | 人群: 科技公司創始人 / 技術負責人
  - `theme03` 深淺程式碼風 | 適合: 技術方案 / 開發者大會 | 人群: 工程師 / 技術管理者
  - `theme04` 玻璃糖果風 | 適合: 年輕化品牌 / 消費產品 | 人群: 品牌團隊 / 設計師
  - `theme05` 色譜圖表風 | 適合: 資料包告 / 市場分析 | 人群: 資料分析師 / 諮詢顧問
  - `theme06` 深色圖譜風 | 適合: 高密度資料展示 / 戰略分析 | 人群: 戰略團隊 / 投資人
  - `theme07` 冷白調研風 | 適合: 調研報告 / 白皮書 | 人群: 研究機構 / 諮詢團隊
  - `theme08` 黑金實驗風 | 適合: 高階釋出 / 品牌提案 | 人群: 高階品牌 / 創意總監
  - `theme09` 深藍雜誌風 | 適合: 品牌故事 / 人物訪談 | 人群: 公關團隊 / 媒體編輯
  - `theme10` 金色指數風 | 適合: 金融資料 / 投資報告 | 人群: 投資機構 / 金融分析師
  - `theme11` 高能增長風 | 適合: 增長覆盤 / 商業計劃 | 人群: 創業者 / 增長團隊
  - `theme12` 聲波霓虹風 | 適合: 音樂娛樂 / 潮流活動 | 人群: 娛樂品牌 / 活動策劃
<!-- theme-choice-hints:end -->
- 不使用舊 token、舊主題、舊媒體槽、舊風格分支或舊入場動畫控制。
- 選頁先用 `npm --prefix <skill-root>/project run layout:query -- --theme <themePack> --role <role> --limit 8 --seed <randomSeed>:slide-<n>`;每個邏輯頁的 3 個模板方案必須是結構指紋不同的 layout。相同 seed 和輸入必須穩定,也不要固定只用未打雜湊表的前三條。跨邏輯頁允許在候選稀缺時複用,由既有跨頁 layout/組合/family 軟懲罰降低重複。需要媒體槽時加 `--needs-media`、`--planned-images <n>`、`--provided-images <n>` 或 `--image-gen`。
- 欄位不清楚、物件/陣列/count、圖片/媒體:先執行 `npm --prefix <skill-root>/project run inspect:layout -- --compact <layout...>` 檢查該頁 3 個模板方案;單 layout 寫 props 時執行 `props:safe`;schema v2 結構投影 goal 執行 goal spec 校驗,不要用 `props:safe --write` 回填 props。
- 把 `layout:query` / `inspect:layout` 的 JSON 管道給程式解析時,改用 `node <skill-root>/project/scripts/layout-query.mjs` / `node <skill-root>/project/scripts/inspect-layout.mjs`:`npm run` 會在 stdout 前列印生命週期 banner,汙染 JSON。
- 標準 3+1 deck:必須先逐頁寫 `output/<deck-name>/page-content-pack.json`,每頁使用穩定 id 和下列完整 PageContentPack 結構;再執行 `npm --prefix <skill-root>/project run goal:scaffold -- --title <title> --goal <goal> --theme <themePack> --pages <n> --layout-variants 3 --content-plan output/<deck-name>/page-content-pack.json --seed <randomSeed> --chunk-size 5 --out output/<deck-name>/goal.json`。schema v2 的 3 個模板方案和 v4 定製方案必須由該 content plan 生成;沒有 `--content-plan` 時不要使用 `--layout-variants 3`。
  ```json
  {
    "pages": [{
      "id": "page-1",
      "presentation": {
        "pageIntent": "cover",
        "coreMessage": "本頁唯一核心結論",
        "title": {"full": "完整標題", "short": "短標題"},
        "summary": {"full": "完整摘要", "short": "短摘要"},
        "items": [{"id": "fact-1", "label": "指標名稱", "detail": {"full": "完整說明", "short": "短說明"}, "value": 42, "displayValue": "42", "unit": "%", "required": true, "priority": "high"}],
        "chartData": [{"id": "fact-1", "label": "指標名稱", "value": 42, "displayValue": "42", "unit": "%"}],
        "media": [{"src": "assets/example.png", "kind": "image", "type": "image/png", "alt": "圖片說明"}]
      }
    }]
  }
  ```
- 文案長度和陣列數量:優先按 `fillPlan.text[].maxChars`、`fillPlan.arrays[].visibleCount`、`fillPlan.arrays[].nestedArrays` 寫;`display` / `metric` 欄位只寫短詞、短句或數字。
- Html 欄位(如 `headlineHtml` / `quoteHtml`)寫文案只用 `<br>` 換行加 `<b>` / `<em>` 行內強調,禁止 `<span>` 等自由 HTML;主題預設值裡的 `<span class>` 依賴主題 CSS,只是佔位,不要照抄。`validate:goal-spec` 會攔截自由 HTML。
- 可見陣列項必須寫實文案;被 count/顯隱控制隱藏的尾項可保留“請輸入文字”佔位。
- 元素出現動畫使用頁面元件自帶的原生效果。
- 頁面切換動畫可以在預覽控制面板裡調整。
- 面向使用者交付的 deck 預設不顯示風格/主題切換選項;風格切換隻保留在內部除錯 demo 頁面。使用者明確要求保留主題切換時,在 goal 頂層寫 `preview: {"themeSwitcher": true}`。
- 不手寫自由 HTML slide。新生成 deck 使用 `schemaVersion: 2`;每個邏輯頁只儲存一份 `content`,前三項只儲存 `{kind:"template", layout, contentMap, projection}` 的結構目標與 source binding,第四項儲存 `{kind:"bespoke", adjustable:false, composition, contentMap, projection}` 的網格/type/style 與 source binding;goal 不持久化模板 props 或 bespoke 文案、指標、列表、圖表、media src/alt 業務副本。v4 不寫 `layout`、`props` 或 `controls`。
- 每套主題的前 5 頁 `themeXX_page001` 到 `themeXX_page005` 都是封面候選。一個 deck 只能有 1 個邏輯封面頁;標準 PageContentPack 3+1 中 `pageIntent=cover` 優先使用可承載的封面候選,只有前 5 頁能形成 3 個結構不同的真實模板時才整頁使用封面佈局,否則整頁回退到第 6 頁以後的真實正文佈局,同一邏輯頁禁止混用封面與正文佈局。
- 同一邏輯頁的 3 個模板方案必須結構不同;不要只換頁碼或映象同一結構。跨邏輯頁不要求 3N 個 layout 絕對唯一,保留 scaffold 既有的 layout、組合和 family 複用軟懲罰。
- 面向使用者交付的 deck 不能依賴頁面預設文案。除非使用者明確要預設 demo,每一頁業務內容都必須先寫入 PageContentPack,不直接寫入 variant props/composition。
- `slide.content.presentation` 是唯一業務事實源;模板在執行時按 `contentMap + projection.structure` 即時生成 props,bespoke 按 `contentMap + itemBindings/chartBindings/mediaBindings` 即時注入 composition。修改 canonical content 後 4 個方案必須一起更新。
- v4 必須獨立分析使用者目標、受眾、本頁敘事作用、重點資訊和當前主題特徵後設計;繼承主題顏色、字型、間距、形狀、媒體和圖表語言,使用受限 `composition` 元素,不新增事實、不寫自由 HTML/JSX,也不是前三個模板的小改。生成失敗時仍輸出安全的 `kind:"bespoke"` 組合。
- v4 `composition` 寫 `designIntent`、主題背景語義和 12×8 網格元素;元素型別只用 `text` / `metric` / `list` / `quote` / `media` / `shape` / `chart`。
- 3 個模板方案各自的可見文案槽必須由 `contentMap` 或 `projection.structure` 繫結 canonical content,未使用槽位由結構投影顯式關閉或置空;遺漏會交付模板演示文案。
- 優先只寫 `layout:query` / `inspect:layout` 暴露的文案欄位。欄位是物件或陣列時按 `fillPlan` 和 `propShapes` 填內部 key。`copyKeys` 已展開巢狀路徑(如 `copy.quote`、`items[].label`),按列出的路徑直接填。
- `inspect:layout` 標 `contentLocked: true` 的頁正文由元件固定、props 填不進:換一頁能填正文的佈局,或僅當使用者接受其預設正文時使用。陣列按 `fillPlan.arrays[].visibleCount` 填滿可見項;`decorativeKeys` 是裝飾位,不要填。
- 不要改頁面後設資料、元件原始碼、className、CSS、樣式欄位或預設視覺結構來完成內容填充。schema v2 業務內容只寫 PageContentPack,結構目標與 binding 由 scaffold 生成。
- 允許用頂層 `text` 覆蓋可見文字槽位,但只用於替換文字內容。不要在普通生成中啟動瀏覽器批次抽取全頁面文字槽位;只有使用者明確要求“徹底清除所有模板預設文案/逐頁校對可見文案”時才做執行時槽位抽取。
- 禁止複用 `output/` 裡已有的舊 `goal.json` 或舊 HTML。每次請求都新建本次輸出目錄和本次 JSON 計劃。
- 輸出目錄寫在當前會話工作目錄,不要寫入 `<skill-root>/project/output`。
- HTML 交付:給使用者的預覽地址只給 `http://127.0.0.1:<port>/`(不給 https 或 .local 變體);本機 HTTP 可匯出 HTML/PDF/PPTX,本地 HTML 或 `file://` 不能匯出可編輯 PPTX。不要返回 `theme-preview`。在自帶瀏覽器的 Agent APP(如 Codex)裡生成時,提醒使用者匯出 PDF/PPTX 前把該地址在系統瀏覽器中開啟。
- PPTX 交付:呼叫 `/api/export-editable-pptx`;最終只給 PPTX 檔案路徑或下載結果。
- 無瀏覽器會話、指令碼直調、或預覽匯出介面返回 403/5xx 時:改用 `npm run export:pptx -- <deck>/ppt <out.pptx>`(PDF 用 `export:pdf`)直接產出檔案,不需要先起瀏覽器會話。
- 如果輸出正文裡出現與使用者主題無關的預設文案,例如 AI Capital / 投融資 / SoundWave / 聲浪 / Key Metrics / Roadmap / End of Report 等,必須重寫 JSON 後重新渲染,不能交付。

## 媒體工作流

- 媒體欄位只寫 `mediaSlots[].canPresetMedia: true` 的槽,按該槽 `presetProp` / `fieldPath` 寫路徑;`goal.json` 只引用 deck 內相對媒體路徑,不可引用臨時目錄、外部絕對路徑、`file://` 或遠端 URL。
- 視覺素材任務先判斷意圖:無圖但需要視覺素材時先問是否預留圖片槽;無真實素材且不能生圖時優先選無媒體頁。使用者提供素材庫/素材目錄路徑即視為有圖意圖:至少選 2 個帶媒體槽頁面並填入合適素材。素材路徑不可訪問時改選無媒體頁並在交付說明中告知,不在頁面內留佔位提示文字。使用者同意用 `--planned-images <n>` / `--needs-media`,使用者給素材用 `--provided-images <n>` / `--provided-media`,使用者明確要求原創視覺圖/生圖時,Codex 環境用 image-gen 生成圖片並加 `--image-gen`;未明確生圖時先詢問使用者。`plannedImages` / `needsVisual` / `imageGen` 只表示選頁意圖,除非使用者明確選擇預留空槽,交付前必須寫入真實媒體路徑,不能交付空媒體槽或偽造路徑。
- 使用者本地圖片/影片先執行 `npm --prefix <skill-root>/project run media:stage -- <deck-output-dir-or-ppt-dir> <media-file...>`,使用返回的 `relative` 路徑;AVIF 會轉成瀏覽器可用格式。image-gen 輸出也先落到本次 deck 目錄。
- 渲染後核對 goal 引用的每個圖片/影片:`ppt/<relative>` 存在且 HTML 包含檔名;缺失時只補最終 `ppt/assets` 並重跑校驗。圖片/影片素材每個最多使用一次;同一邏輯頁的 4 個方案共用同一份素材,算 1 次邏輯使用,不同邏輯頁不要重複填充同一素材。素材用完後,媒體插槽留空或改選無媒體插槽頁面。
- 需要 image-gen 生成 2 張以上獨立圖片時,用多個 subagent 並行生成,不要序列逐張等待;每張圖獨立生成,不要用一張拼圖/素材板再拆分。subagent 只用於生圖,不用於選題、文案、選頁或校驗。

## 工作流

1. 提煉使用者目標: `title`、`goal`、`audience`、`owner`、頁數、內容重點和最終產物格式;同時形成驗收清單,記錄使用者顯式要求、已確認選項和必要假設。使用者未指定頁數時預設 10 頁左右,不少於 8 頁。
2. 確認 `themePack`。使用者未指定時先詢問風格;使用者選定後生成 `randomSeed`,例如 `<主題>-<日期>-<3位隨機詞>`,保證隨機選頁可復現。
3. 判斷圖片意圖:無圖但需要視覺素材時先問是否預留圖片槽;使用者給本地素材先 `media:stage`;明確生圖時用 image-gen。
4. 先按上方 `{"pages":[...]}` JSON 骨架和逐頁語義 brief 寫完整 `output/<deck-name>/page-content-pack.json`,再把該 JSON 和 `--seed <randomSeed>` 透過 `--content-plan` 傳給 `goal:scaffold`;不要另走手寫 3+1 骨架路徑。
5. 每頁只承載一個主要資訊角色。業務值只寫一次到 PageContentPack;scaffold 僅儲存 3 個模板的結構投影/source binding 和 v4 的結構 composition/source binding,不要手工複製 props、文案、指標、列表、圖表或 media 值。
6. scaffold 把 schema v2 JSON 寫入本次工作目錄的 `output/<deck-name>/goal.json`;每頁包含 `selectedVariant: "v1"` 和恰好 3 template + 1 bespoke。渲染前執行 goal spec 校驗;不要對該結構投影 goal 執行 `props:safe --write`,以免把執行時 props 寫回儲存模型。
7. 圖表頁填入自己的資料後,頁內 insight/讀圖/結論類文案欄位必須據新資料一併改寫,不保留預設結論。
8. 執行渲染指令碼輸出 `output/<deck-name>/ppt/index.html`;指令碼會使用 Skill 內建生成器,不要切回外部專案目錄。
9. 渲染後核對素材路徑,缺失時補最終 `ppt/assets`。
10. 確認指令碼完成 `validate:swiss` 和 `validate:goal-copy` 校驗。
11. 渲染指令碼會啟動本地 HTTP 預覽服務並輸出 `http://127.0.0.1:<port>/`;需要指定埠時設定 `DASHI_PPT_PREVIEW_PORT` 後再執行指令碼(埠用 5200-5999 段,4178/4300/4400 為使用者保留埠不可用)。只能用該預覽服務,不得用 `python -m http.server`、`npx serve` 等靜態伺服器替代:靜態伺服器沒有匯出和自動儲存介面。預覽服務下編輯自動儲存到 `index.html` 本體;`file://` 開啟的本地檔案不自動儲存,交付前需匯出。
12. 對最終產物執行成果驗收:預設 comparison 應按邏輯頁連續輸出全部 4N 頁,selected-only 輸出 N 頁;逐組核對 4 個方案內容一致、構圖不同,並確認 v4 無模板屬性控制元件但可選擇、儲存和匯出。
13. 狀態為“待修正”時定位不合格頁,修改文案/資料/媒體,必要時更換 layout 或重新生成對應頁;重新渲染、執行全部校驗並複驗。
14. 執行 `node <skill-root>/scripts/check_latest_version.mjs` 做靜默版本檢查。
15. 驗收透過後按交付格式回覆:HTML 只給 `http://127.0.0.1:<port>/`;PPTX 呼叫 `/api/export-editable-pptx` 後只給檔案路徑或下載結果。

## 成果驗收與返工

機器校驗透過只是技術基線,不等於成果達標。最終驗收以使用者原始需求、已確認選項、明示假設和最終渲染產物為準:

- 目標一致性:Deck 回答使用者的核心問題,重點、結論和語氣適合目標受眾。
- 內容覆蓋:指定的主題、必含要點、頁數、風格、語言、媒體和產物格式都已落實,無跑題、缺項或無關模板文案。
- 逐頁檢查:每頁都服務於整體目標;標題、正文、資料、圖表和 insight 相互一致,沒有重複、斷層、空白頁或明顯不匹配的 layout。
- 敘事完整性:開場、論證/展開和結論/行動順序清晰,頁與頁之間有邏輯承接。
- 交付完整性:最終檔案存在且能開啟,頁數和格式正確,素材可用,首尾頁非空白。

有瀏覽器能力時,最終一輪必須逐頁開啟預覽,檢查內容可見、媒體正常,無明顯溢位、遮擋或裁切;不建立專用 Chrome profile,不預設做截圖審美精修。無瀏覽器能力的指令碼/批處理環境至少複核 `goal.json`、校驗結果和輸出檔案,並不得聲稱已完成視覺驗收。

驗收狀態只有“透過”“待修正”“阻塞”。發現任一不合格項就標記“待修正”:文案、資料、insight 或媒體錯誤時改對應 props;頁面資訊角色或容量不匹配時重新 `layout:query` 並更換 layout;內容缺失時補寫或重新生成對應頁。修正後從 `props:safe`、`validate:goal-spec`、渲染、素材核對、`validate:swiss`、`validate:goal-copy` 到成果驗收全部重跑。

預設最多修正 2 輪。驗收透過後才能交付;兩輪後仍不透過則標記“阻塞”,說明未達標項和阻塞原因,不得將其表述為已完成成果。

示例命令(macOS / Linux):

```bash
<skill-root>/scripts/render_goal_deck.sh \
  output/client-review/goal.json \
  output/client-review/ppt/index.html
```

Windows PowerShell:

```powershell
& "<skill-root>/scripts/render_goal_deck.ps1" `
  "output/client-review/goal.json" `
  "output/client-review/ppt/index.html"
```

## JSON 結構

```json
{
  "schemaVersion": 2,
  "title": "美國 AI 融資調研",
  "goal": "面向投資團隊彙報 2024-2026 年美國 AI 大額融資結構、資本流向和後續判斷",
  "audience": "投資團隊 / 產業研究團隊",
  "owner": "研究團隊",
  "randomSeed": "ai-funding-20260609-a7k",
  "pageCount": 1,
  "themePack": "theme01",
  "variantOutputMode": "comparison",
  "slides": [
    {
      "id": "s1",
      "content": {
        "section": "融資調研",
        "title": "美國 AI 融資調研",
        "titleTop": "美國 AI",
        "titleBottom": "融資調研",
        "summary": "2024-2026 年大額融資結構、資本流向與後續判斷",
        "year": "2026",
        "points": ["融資結構", "資本流向", "後續判斷"]
      },
      "selectedVariant": "v1",
      "variants": [
        {"id": "v1", "kind": "template", "layout": "theme01_page001", "props": {}, "contentMap": {"kicker": "section", "titleTop": "titleTop", "titleBottom": "titleBottom", "lead": "summary"}},
        {"id": "v2", "kind": "template", "layout": "theme01_page002", "props": {}, "contentMap": {"enKicker": "section", "titleTop": "titleTop", "titleBottom": "titleBottom", "subtitle": "summary"}},
        {"id": "v3", "kind": "template", "layout": "theme01_page003", "props": {}, "contentMap": {"kicker": "section", "titleTop": "titleTop", "titleBottom": "titleBottom", "bigNumber": "year"}},
        {
          "id": "v4",
          "kind": "bespoke",
          "adjustable": false,
          "composition": {
            "designIntent": {
              "objective": "快速建立調研範圍",
              "audience": "投資團隊",
              "narrativeRole": "封面定調",
              "emphasis": "研究物件與決策價值",
              "rationale": "用單一標題中心和三項範圍提示縮短理解路徑"
            },
            "background": "dark",
            "elements": [
              {"id": "title", "type": "text", "grid": {"column": 1, "row": 1, "width": 10, "height": 2}, "role": "title", "text": ""},
              {"id": "scope", "type": "list", "grid": {"column": 1, "row": 4, "width": 7, "height": 3}, "items": []}
            ]
          },
          "contentMap": {"elements[0].text": "title", "elements[1].items": "points"}
        }
      ]
    }
  ]
}
```

如果 `slides` 為空,`pageCount` 只適合臨時草稿預覽。新生成 deck 面向使用者交付前必須落成 schema v2 的 3 template + 1 bespoke;舊單版式和舊 3 候選 goal 仍可讀取。

## 頁面角色

`role` 只用於草稿選頁,最終 JSON 的前三個方案必須落成具體 `layout`,v4 必須落成無 layout 的 bespoke composition。角色說明見 `references/layout-roles.md`;真實模板候選以 `layout:query` 輸出為準。

單版式草稿的 `cover` 只能從當前主題前 5 頁選擇；標準 PageContentPack 3+1 按上文的真實候選承載規則選擇同質模板池。`image` / `media` 候選基於真實 `mediaSlots`,不是頁面標題關鍵詞。動態背景頁可用 `ambient` 作為氛圍頁或章節頁。

可以直接指定頁面:

```json
{"layout": "theme01_page030", "props": {"title": "典型案例"}}
```

## 交付能力

生成後的預覽頁預設把 N 個邏輯頁展開為 4N 個方案頁。右側面板可在同組 4 頁之間跳轉或標記最終方案;前三個模板方案可調 props,v4 顯示為固定的 Agent 定製方案。`variantOutputMode:"comparison"` 匯出 4N 頁,`"selected-only"` 匯出 N 頁。面向使用者交付的頁面底部不顯示頁碼標識、翻頁引導、圓點導航或索引提示。

## 頁面屬性契約

普通生成不要讀 `layout-manifest.json`。先用 `layout:query` 輸出的候選摘要。只有需要更細契約時,再用 `npm --prefix <skill-root>/project run inspect:layout -- --compact <layout...>` 看頁面契約:

- `copyKeys`: 可安全改寫的文案/資料欄位。
- `copyBudgets`: 文案長度預算;`display` / `metric` 超長會被 goal spec 攔截。
- `propShapes`: `copyKeys` / 陣列欄位的內部形狀;寫 `copy`、`cells`、`items`、`rows` 等物件欄位時只使用這裡列出的 key。
- `fillPlan.arrays[].itemFields[].enum`: 該欄位為結構列舉,只能從列出的值中選,不是自由文案。
- `mediaSlots`: 圖片/影片寫入欄位、count key、預設數量和最大數量。
- `countBindings`: 數量引數與陣列欄位的繫結。
- `fillPlan` 裡數值欄位看 `numericBounds` 填數:`enforced:false` 是提示、真實資料可超出,`enforced:true` 必須遵守,`semantics:'normalized'` 填 0-1 比例;定長巢狀陣列看 `fixedLength`/`fixedLengths` 按下標填,不試錯。
- `controlKeys`: 右側面板可操作欄位,不是普通內容填充清單;僅使用者明確要求調整頁面屬性時使用。預設只填 `copyKeys`、可見陣列和真實媒體槽。

## 校驗

- 渲染前必須執行 `validate:goal-spec`。
- 輸出後必須執行 `validate:swiss`。
- 輸出後必須執行 `validate:goal-copy`。
- 改動展示 demo 後執行 `npm run showcase:update`。
