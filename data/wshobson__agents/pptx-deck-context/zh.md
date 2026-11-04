---
name: pptx-deck-context
description: "在為新的可編輯 PPTX 簡報準備敘事、資料來源與設計 context 時使用。"
---

# PPTX Deck Context

在撰寫座標或 PPTX 物件之前，先把簡報準備好。這個 skill 負責商業敘事、資料來源的脈絡，以及設計定案。

## Decision sequence

1. 確認受眾、要做的決策、投影片張數、語言、資料來源與品牌需求。
2. 使用使用者選定的敘事框架。如果沒有指定，就提供 `mckinsey`、`scqa`、`pyramid`、`mece`、`action-title`、`assertion-evidence`、`exec-summary-first` 或 `custom` 讓使用者選，不要默默自己決定。
3. 指定穩定的來源 ID，並為每個指標、引述、圖表數值與事實主張規劃一個 `source_ref`。
4. 選擇一個有文件依據的設計方向。優先用使用者的品牌指南，其次是唯讀的參考簡報證據，再其次是 `references/design-profiles.md` 中可重用的 profile。
5. 在開始撰寫投影片之前，把框架、假設、來源清單、色盤、字體排版、間距和招牌元素記錄在 `summary` 裡。

## Rules

- 一張投影片只傳達一個訊息，框架要求時就用行動式標題。
- 把設計參考當成設計證據，不是內容或素材的來源。
- 沒有記錄授權證據，就不要複製外部的字型、圖片、圖示或 logo。
- 把設計訊號轉成明確的填色、字體排版、間距與 bbox，不要依賴自動排版引擎。
- 長的來源素材要保持精簡。請對方提供摘要或與決策相關的節錄，不要把簡報規格變成文件傾倒場。

可重用 profile 的指引見 `references/design-profiles.md`。
