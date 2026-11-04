---
name: slidex-deck-qa
description: 驗證並以視覺檢查可編輯的 OpenSlideX deck。在完成前、來源或設計有重大變更後，以及要審查溢出、重疊、對比、素材、montage、動態、證據或匯出就緒程度時使用。
---

# OpenSlideX Deck QA

來源格式有效是必要條件，但絕對不能取代渲染後的實際證明。

## Required reference

讀 [the review matrix](references/review-matrix.md)。套用每一項 release blocker，以及和 deck 來源類型相關的檢查。

## Acceptance loop

1. 用 `open_slidex_read` 確認所選的 deck、目前的 revision 和確切的來源範圍。
2. 做編輯時，依賴 `open_slidex_edit`：它會驗證、渲染、做視覺檢查，而且只有候選版本通過時才會以原子方式寫入。
3. 如果被拒絕，用回報的投影片、code、node ID 和指標修正同一個候選版本。做了兩次有針對性的修正嘗試後就停下，並回報剩下的阻礙。
4. 純審查的工作，呼叫 `open_slidex_review`，並檢視完整的 montage 加上每一張有實質變動的投影片。
5. 做一輪證據檢查和一輪視覺檢查。兩者都通過，而且編譯後的 React deck 保有預期的層次，這份 deck 才算完成。

超過 20 頁的 deck，要檢視完整的 montage 和每一張投影片，不是只抽樣檢查。瀏覽器原生的 HTML，要驗證標準頁數、每個對應頁面都有一張縮圖，以及在全螢幕播放中檢查第一頁、中間頁、最後一頁和章節交界頁。

只要有視覺 QA 可用，沒有通過的渲染預覽就絕對不要宣告完成。
