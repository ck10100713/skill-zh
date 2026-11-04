---
name: prototype
description: 做一個用完即丟的 prototype 來回答設計問題。當使用者想確認某個狀態模型或邏輯感覺對不對，或想探索 UI 該長什麼樣子時使用。
---

# Prototype

prototype 是**用來回答一個問題的用完即丟程式碼**。問題決定它的形狀。

## 選一條分支

從使用者的 prompt、周圍的程式碼來判斷正在回答哪個問題，使用者在的話也可以直接問：

- **「這個邏輯 / 狀態模型感覺對嗎？」** → [LOGIC.md](LOGIC.md)。做一個可分享的單一 HTML 檔（自由操作的按鈕加上分頁式的引導導覽），把 state machine 推過那些光靠紙上推演很難想清楚的情況，而且非開發者也能自己操作。
- **「這個該長什麼樣子？」** → [UI.md](UI.md)。在單一路由上產生好幾個截然不同的 UI 變體，用 URL search param 和浮動的底部工具列來切換。

兩條分支產出的東西差很多，選錯會讓整個 prototype 白做。如果問題真的有歧義、又聯絡不到使用者，就預設選比較符合周圍程式碼的那條分支（後端 module → 邏輯；頁面或 component → UI），並在 prototype 最上面寫明這個假設。

## 兩條分支都適用的規則

1. **一開始就是用完即丟，而且清楚標示。** prototype 的程式碼放在靠近實際會用到的地方（在它正在做 prototype 的那個 module 或頁面旁邊），讓 context 一目了然，但命名要讓隨便看一眼的人就知道這是 prototype，不是 production。用完即丟的 UI 路由，遵守專案既有的路由慣例；不要發明新的頂層結構。
2. **跑起來要很簡單。** UI prototype 從專案的 task runner 一個指令就能啟動：`pnpm <name>`、`python <path>`、`bun <path>` 等等。邏輯 demo 是使用者雙擊就能開的單一 HTML 檔。不管哪種，都不需要動腦就能啟動。
3. **預設不做 persistence。** 狀態放在記憶體。persistence 是 prototype 要_檢驗_的東西，不是它該依賴的東西。如果問題明確牽涉到資料庫，就用一個暫時的 DB 或本地檔案，名字要清楚標示「PROTOTYPE, wipe me」。
4. **跳過潤飾。** 不寫測試，除了讓 prototype _能跑_ 之外不做錯誤處理，不做抽象。重點是快速學到東西。
5. **把狀態亮出來。** 每個動作之後（邏輯）或每次切換變體時（UI），印出或渲染完整的相關狀態，讓使用者看得到什麼變了。
6. **做完要留存。** 把驗證過的決策併進真正的程式碼，然後把 prototype 本身留存成**第一手來源**：commit 到一個用完即丟的 branch，不要進 main，並在實作的 issue 上留一個指向那個 branch 的 context 指標。答案也要留存（結論，以及它解決的問題），放在 issue 或 commit 裡。main branch 只留下驗證過的決策。
