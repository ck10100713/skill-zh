---
name: slidex-react-authoring
description: 建立、改寫或修復標準的 OpenSlideX React 簡報。用於 presentation.tsx、deck 本地元件、原生圖層撰寫、TSX 遷移，或對 revision 安全的 MCP 編輯。
---

# OpenSlideX React Authoring

把所選 deck 的 `presentation.tsx` 當作唯一可編輯的簡報來源。舊的 `presentation.mdx` 只是匯入輸入或唯讀的遷移備份，絕對不是第二個真實來源。

## Load only what the task needs

- 輸出 TSX 之前，先讀 [the React presentation contract](references/react-presentation-contract.md)。
- 處理圖片、影片、SVG 場景、圖表、表格或匯入的資料時，也要讀 [media and data](references/media-and-data.md)。
- 要做完整的建立或重新設計，動筆之前先啟用 `slidex-deck-design`。

## Non-negotiable rules

- 簡報的基本元件只能從 `@open-slidex/sdk/react` 匯入。
- 使用 `definePresentation()`，搭配一個 `Deck` 根節點，以及原生的 `Slide`、`Text`、`Image`、`Video`、`Svg`、`Chart`、`Table`、`Shape`，或受控的 `HtmlEmbed` 元素。
- 每個可見的原生圖層都要給穩定且唯一的 `id`，以及用字面百分比表示的 `x`、`y`、`w`、`h`；`fontSize` 用 point。
- 把重複的結構抽成相對路徑的 `components/*.tsx` 檔案。可編輯/可匯出的自訂元件，要用 `defineSlideXComponent()`、runtime 的 props schema、素材參照和 `toMotionDoc()` 來註冊。
- 條件式、迴圈、hook、計算出來的變數、spread 和其他動態運算式，都視為只能用 code 處理。不要承諾它們能在 Inspector 中來回轉換（round-trip）。
- 只使用 React、`@open-slidex/sdk/react` 和相對路徑的 deck 匯入。絕對不要使用 Node API、外部 npm 匯入、跨 deck 的路徑、網路呼叫、事件處理函式、任意 HTML、Base64、blob URL 或絕對素材路徑。
- 絕對不要寫已移除的 `Card`、`Metric`、`Stack`、`Group`、`Title`、`Icon` 或 `Notes` 元件。

## Edit transaction

1. 在 Workspace 範圍內，列出並明確選擇目標 deck。
2. 呼叫 `open_slidex_read`，帶上 `sourceFormat: "tsx"`，取得最新的 revision 和完整的 deck、目標投影片或本機元件。
3. 只讀任務需要的指引資源。
4. 保留穩定的 ID，以及不相關的匯入、投影片、元件和素材。
5. 把一份完整的 `presentation.tsx` 或一段完整的 `Slide` JSX 區塊，連同最新的 `expectedRevision` 提交給 `open_slidex_edit`。
6. 依據編譯、驗證、素材或渲染 QA 的發現，修復被拒絕的候選版本。絕對不要重試過期的 revision。
7. 把通過的編輯所帶的驗證、視覺報告和預覽，當作最終結果。

MDX 匯出是一項可攜性操作。沒有 `toMotionDoc()` 的自訂元件，必須擋下 MDX 和可編輯 PPTX 的匯出；絕對不要悄悄把它攤平成圖片或 HTML。
