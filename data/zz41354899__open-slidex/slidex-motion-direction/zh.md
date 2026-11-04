---
name: slidex-motion-direction
description: 在靜態設計完成後，加入或審查刻意設計的 OpenSlideX 動畫。用於進場、Action Tween、退場、Shared Morph、錯開的逐項顯示、投影片轉場、圖表動態、時間控制、減少動態（reduced-motion）行為，或動態的潤飾。
---

# OpenSlideX Motion Direction

先把靜態構圖做完並驗證。動態必須用來釐清層次、順序、因果、回饋或狀態變化；否則就用 `none`。

## Required reference

在加入或修改動態之前，先讀 [motion patterns](references/motion-patterns.md)。它包含有效的詞彙、時間範圍和模式選擇。超過 20 頁的動畫 deck，也要讀 [long-deck motion](references/long-deck-motion.md)，讓每一頁都有動畫，又不會產生重複或讓人疲乏的動態。

## Workflow

1. 讀完受影響投影片的完整內容，以及它的最新 revision。
2. 用一句話說明這個動態要解釋什麼。
3. 一般投影片最多用兩種進場類型，並保留完整的靜態最終畫面。
4. 做 Action Tween 時，在 `motion` 裡撰寫一個驗證過的 `MotionSequenceV1` JSON 字串；每個 action ID 和整張投影片的順序都要唯一，而且最後一個 tween 的 `to` 要等於該圖層原生的最終幾何和不透明度。
5. 做組合式的 build 時，要讓物件的序列清楚可讀：進場、一個以上的 tween，然後是選用的退場。退場播放絕對不會改變原生的靜態最終狀態。
6. 做 Shared Morph 時，在來源投影片上使用 `slideTransition="morph"`，而且只在相鄰投影片上相容的圖層重複使用 `sharedId`。把 N 張投影片的 Morph 視為 N-1 條各自有效的相鄰邊：除了最後一張，每張投影片都帶 Morph 轉場，而且每條邊至少有一對同類型的 `sharedId`。要讀取並提交完整受影響的序列，這樣修復某一條邊時，才不會斷掉後面的邊。Shape 配對可以使用不同的、受支援的形狀預設值；要保留有用的最終狀態，而且只在能釐清轉換的時候才用柔化效果。優先使用具名的 Morph easing；只有自訂速度曲線確實能解釋狀態變化時，才使用四個 `morphCurve*` 三次貝茲控制點。
7. 做互動式頁面或電子書時，在原生圖層上使用有版本的 `interaction` prop，做點擊導覽或安全的連結。絕對不要嵌入事件程式碼。
8. 做原生的 `SvgBlock` 場景時，只有在它沒有 script 的 SVG 和靜態最終狀態通過之後，才使用 `sharedScene`、`stage` 和 `stageDuration`。
9. 透過 `open_slidex_edit` 提交完整更新後的投影片。
10. 檢視通過的預覽，並驗證減少動態、點陣化（raster）和 PPTX 輸出都不會隱藏資訊。

絕對不要嵌入動畫程式碼、使用不支援的動態名稱或已移除的元件，也不要用動態去掩蓋太擁擠的靜態版面。
