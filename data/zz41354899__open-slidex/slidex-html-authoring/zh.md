---
name: slidex-html-authoring
description: 讀取、建立、替換或修復瀏覽器原生的 OpenSlideX HTML 簡報。用於標準的 .html 來源、封裝好的離線資源、HTML 頁面對應或不透明來源（opaque-origin）播放；不適用於可編輯的原生 MotionDoc MDX。
---

# OpenSlideX HTML Authoring

把瀏覽器原生的 HTML 當成標準來源保留下來，不要把它的 DOM、CSS 或 JavaScript 轉成原生 MotionDoc 圖層。

## Progressive route

在建立或修改會載入 script、圖片、影片、字型、frame、worker 或連線的 HTML 之前，先讀 [browser runtime](references/browser-runtime.md)。

要做精緻的顧問、投資、財務或長篇 HTML deck，也要讀 [the IDAEO and Nov reference grammar](references/ref-idaeo-nov.md)。它從兩份核准的參考 deck 提煉出可重複使用的構圖和節奏，但沒有抄它們的主張、品牌或私人內容。然後遵循 HTML manifest 回傳的 `slidex-deck-design`、`slidex-motion-direction` 和 `slidex-deck-qa` 建議指引。

## Read and write through the six-tool MCP

1. 在 Workspace 範圍內，用 `open_slidex_workspace` 選擇目標 deck。
2. 呼叫 `open_slidex_read`，帶上 `sourceFormat: "html"`。回傳 `nextCursor` 時，要把每個 chunk 都讀完，並保留最新的 `revision` 和 `htmlSource`。
3. 要做替換，就呼叫 `open_slidex_edit`，帶上 `target: "html"`、放在 `source` 的完整 HTML、回傳的 `htmlSource`，以及 `expectedRevision`。只有在用新的 HTML deck 替換所選 deck 時，才省略 `htmlSource`。`source` 裡含有相對路徑的本機圖片時，也要把它們在所選 deck 內的實際目錄當作 `htmlAssetRoot` 傳入。絕對路徑、`file:` URL、symlink 和遠端網路資源都會被拒絕。這次編輯會把核准的圖片複製到 `assets/`，把 PNG 轉成 WebP，並改寫標準 HTML。
4. 再讀一次儲存後的 HTML，並在播放中檢視每個對應的頁面。確認回傳的 `pageCount` 和來源 deck 一致，包含單純的 `.slide` HTML 匯出。長的 deck 要驗證每頁縮圖，加上全螢幕播放的第一頁、中間頁和最後一頁狀態。

## Authored HTML contract

- 每一頁優先用一個明確的 `[data-slidex-page]` 元素。舊的 `.gcard.page` 和單純的 `.slide` 匯出仍然支援，但明確的標記是最具決定性的撰寫規約。
- 使用 16:9 的舞台、語意化 HTML、共用的 CSS design token、穩定的頁碼，以及完整的靜態最終狀態。互動和動畫只限於文件內部，並要遵守 `prefers-reduced-motion`。
- 行內 SVG 和 CSS 仍然屬於標準 HTML，所以不會以獨立檔案的形式出現在 `assets/`。只有被引用的本機附屬檔案才會複製到那裡。絕對不要為了讓資料夾看起來有東西，就憑空製造重複的素材檔。
- 全螢幕投影不能依賴編輯器的 chrome、本機絕對路徑、Base64 文件儲存或瀏覽器擴充功能。

絕對不要撰寫產生出來的 `HtmlEmbedBlock` 包裝。絕對不要用 `open_slidex_edit` 把任意的 HTML 轉成可編輯的 React 圖層。如果需要原生編輯或可攜的 PPTX，要用 `slidex-react-authoring` 另外重建看得見的內容意義。
