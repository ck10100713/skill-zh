---
name: pptx-slide-specification
description: "在撰寫或修復可編輯 PPTX 簡報、座標明確的 JSON 規格時使用。"
---

# PPTX Slide Specification

直接在 `layout_tree` 裡撰寫最終座標。稽核之後，不得有任何 renderer 來決定位置、縮小文字或推斷版面。

## Required contract

- 根 JSON 包含 `summary` 和 `slides`。
- 每張投影片都有穩定的 `id`、以訊息為主的 `title`、無障礙的閱讀順序，以及完整的 `layout_tree`。
- Layout tree 要宣告投影片尺寸、根 group、以 id 為 key 的 group 與物件、最終以英吋計的 bbox、樣式、z-index 與分類。
- 每個有意義的物件都有 `id`、`kind`、`role`、`classification`、`content`、`style`、`bbox` 和 `z_index`。
- 正式環境的 `summary` 要包含明確的 `layout_policy`（安全邊距、內容底線、頁尾頂線、最小間距）與無障礙 metadata。

## Authoring rules

1. 使用穩定、好讀的 ID、絕對定位的 group，以及以英吋為單位的正值尺寸。
2. 一般內容要留在安全邊距內，並且在頁尾軌道之上。只有背景的 `layout_design` 物件可以滿版出血。
3. 使用原生的 `text`、`shape`、`line`、`table` 和 `image` 物件。輔助視覺中的標籤與數值，要用原生物件重新建立。
4. 有意義的圖片要給替代文字。有來源的主張要記錄 `source_ref`。
5. 內容文字要維持在 9 pt 以上；字型要縮小之前，先精簡、調整大小或拆分過於密集的內容。
6. 使用共用的格線、一致的間距、明確的顏色、明確的字型大小，以及刻意安排的 z 順序。

## Build contract

專案內的 builder 從空白的投影片版面開始，並用 `Inches(...)` 對應所有 bbox。要明確設定換行、停用自動調整大小、文字內縮、錨點、對齊、字型、顏色、線條設定、圖片長寬比，以及隱藏投影片的狀態。加入物件之前，要拒絕零或負值的幾何。

精簡的 schema 與修復指引見 `references/layout-contract.md`。
