---
name: slidex-source-import
description: 匯入提供的 Markdown、舊版 MDX、PDF、圖片或 PowerPoint 證據，並轉成可編輯、以 React 為主的 OpenSlideX deck。
---

# OpenSlideX Source Intake

在組成原生 MotionDoc 之前，先把提供的證據帶進所選的 deck。來源文字放在 `knowledge/`，視覺證據放在 `assets/`，保留它的意義，但不要把外來的版面當成可攜的程式碼。

## Read the source safely

1. 在 Workspace 範圍內，用 `open_slidex_workspace` 選擇目的地 deck，然後呼叫 `open_slidex_read`，帶上 `intent: "import"`，並保留它的最新 revision。
2. MD、Markdown、文字、CSV、PDF 或圖片輸入，要把本機附件暫存在設定好的根目錄的 `.open-slidex-inbox/` 底下，然後呼叫 `open_slidex_media`，帶上 `action: "ingest-source"`、相對於 inbox 的 `filePath`，以及最新的 `expectedRevision`。單一個公開的 HTTPS 圖片 URL 可以直接當作 `filePath` 傳入。
3. 規劃之前，要透過 `open_slidex_read` 讀每一個回傳的 `knowledge/...` 資源。原生 `ImageBlock` 圖層要使用回傳的 `assets/...` 路徑；它們可能代表本機附件、公開的 Notion 或 AI 圖片 URL、PDF 圖片，或 PDF 頁面的備援圖。把警告當成證據的缺口。
4. 提供的是 PPTX 時，使用下面專用的流程。

## Import PowerPoint evidence

1. PPTX 來源檔案必須在所選的 deck 目錄內。
2. 呼叫 `open_slidex_read`，帶上 `intent: "import"`，然後讀這個 skill 和它所指名、與任務相關的參考檔。
3. 呼叫 `open_slidex_source_import`，帶上 `action: "inspect"`，檢視投影片順序、還原出的文字框、字體排印提示和圖片幾何。再用 `action: "import-media"` 和最新的 `expectedRevision` 呼叫一次；只使用回傳的圖片中 `status` 為 `imported` 且 `source` 為 `assets/...` 的那些。
4. 編輯之前，立刻再呼叫一次 `open_slidex_read`，取得最新的 revision 和完整的目的地來源。

## Rebuild, do not transplant

- 只有 PPTX 的情況，規劃遷移之前先讀 [PPTX conversion](references/pptx.md)。
- 把來源有順序的段落、標題層次、文案和有意義的媒體，當作遷移的輸入。針對目標投影片重新組成視覺系統，不要為每個來源頁面各產生一頁籠統的文字傾倒。
- 每個輸出的圖層都遵循 `slidex-react-authoring`。舊的 MDX 會被解析成原生圖層，並只寫成一次 `presentation.tsx`；絕對不要讓 MDX 和 TSX 保持同步。做整份 deck 的轉換時，之後依序載入 `slidex-deck-design`、`slidex-motion-direction` 和 `slidex-deck-qa`。
- 只保留原生的 `Text`、`ImageBlock`、`VideoBlock`、`SvgBlock`、`Chart`、`Table` 和 `Shape` 圖層。每個可見圖層都需要穩定的 `id` 和明確的百分比 `x`、`y`、`w`、`h`；`fontSize` 用 point。
- 只有在已驗證、可在本機重建成可攜素材的宣告式 SVG 時，才使用 `SvgBlock`。絕對不要移植外來的 script、事件處理函式、SMIL 動畫或外部 SVG 參照。
- 在刻意重新組成投影片之前，用回傳的 `textFrames` 保留閱讀順序、幾何、字級、字重、對齊和標題提示。把每個回傳的 `textBlock` 當作可審查的原生證據，不是要你複製一個薄弱的來源版面。
- 在 `ImageBlock` 裡，保留每個匯入的 PPTX 圖片框所回傳的 `x`、`y`、`w`、`h` 和 z-order。不要為 `missing` 或 `unsupported` 的圖片輸出 `ImageBlock`。

## Commit one validated result

寫入之前，先規劃好完整的目標 deck。要做重新設計的話，用 `open_slidex_read.templateQuery` 從六個三十頁的核心參考檔中剛好選一個，然後保留來源的投影片數量，除非使用者要求重新調整結構。把一份完整的 deck 連同它最新的 `expectedRevision` 提交給 `open_slidex_edit`；被拒絕的候選版本，依據針對特定 node 的視覺 QA 發現來修復。絕對不要在 `presentation.tsx` 裡保存來源 URL、Base64、PowerPoint XML、外來元件或本機絕對路徑。
