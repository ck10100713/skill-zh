---
name: slidex-deck-design
description: 把 prompt、筆記、文件、研究報告、資料簡報或既有的 deck，轉成精緻、可編輯的 OpenSlideX 簡報。用於敘事規劃、資訊整合、版面系統、字體排印、色彩、圖像、圖表、表格或重新設計。
---

# OpenSlideX Deck Design

從意義往外設計。每張投影片只傳達一個主張，在故事中有存在的理由，而且用原生 MotionDoc 圖層維持可編輯。

## Progressive route

1. 讀 [source to story](references/source-to-story.md)，把輸入分類、保留證據，並定義受眾、決策和缺少的資訊。使用者提供文件或報告時，先搜尋所選 deck 的 `knowledge/` 資源，只讀相關的證據，再決定視覺方向。
2. 讀 [narrative patterns](references/narrative-patterns.md)，從六種核心 deck 模式中選一種。如果最適合的不明確，就把 brief、受眾、證據類型和預期結果當作 `templateQuery` 傳給 `open_slidex_read`，然後只檢視推薦排名第一的 TSX 參考檔。MCP 會使用[六個範本的目錄](references/template-catalog.json)；如果回傳的推薦已經指出符合的範本，就不要載入它。做顧問、投資、財報或財務週報類的工作時，也要讀 [consulting financial report](references/consulting-financial-report.md)。
3. 讀 [visual direction](references/visual-direction.md)，確立構圖、字體、色彩、圖像和資料的規則。
4. 剛好讀一份最接近的核心參考檔：

   - 顧問、投資、財報、財務週報：[consulting financial report](references/consulting-financial-report.tsx)
   - 主題演講、願景、品牌故事：[editorial story](references/editorial-story.tsx)
   - KPI、研究、狀態、營運：[data brief](references/data-brief.tsx)
   - 產品、銷售、功能發表：[product launch](references/product-launch.tsx)
   - 建議、董事會備忘錄、計畫：[strategy proposal](references/strategy-proposal.tsx)
   - 課程、新人訓練、工作坊：[training workshop](references/training-workshop.tsx)

這六個元件化的 TSX 資源各有 30 頁，總共 180 頁持續維護、可編輯的教學投影片。它們是完整的敘事與視覺系統，不是要整份照抄的內容。借用最接近的閱讀路徑、構圖邏輯和動態語法，不要借範例的文字、數字、ID 或主張。除非使用者要求 30 頁的成品，否則要保留來源 deck 需要的長度。使用者明確指定的品牌要求，優先於參考檔的 token。

要做瀏覽器原生的 HTML 時，這個 skill 只用在故事、證據和視覺系統的決策。實作要透過 `slidex-html-authoring` 完成；不要把 HTML DOM 轉成可編輯的 MotionDoc，也不要撰寫 `HtmlEmbedBlock`。

## Design pass

1. 寫一句話的受眾成果，和一句話的視覺概念。
2. 建立以主張為主的投影片大綱。把重複的段落合併；不要每個來源標題就做一張投影片。
3. 給每張投影片一個不同的視覺任務：吸引注意、解釋、比較、證明、排序、決策或收尾。
4. 建立一套一致的字體系統、克制的配色、間距節奏和媒體處理方式。相鄰投影片之間，焦點位置和資訊密度要有變化。每張封面都需要一個刻意安排、經過驗證且可攜的 `ImageBlock` 素材；用有意義的裁切當主視覺，不要用裝飾性的幾何圖形。
5. 依每張投影片實際的主張來構圖。不要預設把內容單元變成大小一樣的卡片，也不要在整份 deck 重複同一種範本幾何。在參考檔驅動的工作中，用 `Shape` 做語意上的卡片背景，卡片裡的原生子元素共用具名的 group。對於真正重複出現的能力、人物、步驟或機會，才適合用多張卡片。不要把 Shape 用在裝飾、分隔線、假圖示、抽象藝術或手工拼出來的圖表。
6. 量化比較、分布或趨勢用原生的 `Chart`；需要精確查詢時用 `Table`。標籤、單位、來源和主要結論要放在擁擠的圖表區域之外；當原生圖表就能傳達證據時，絕對不要用裝飾形狀畫假圖表。
7. 依預期渲染出的行數預留文字框。先修好溢出、CJK 孤字、英文孤行、低對比和薄弱的字體層次，再考慮縮小字體。
8. 檢視通過的 montage，看層次、節奏、對比、密度、重複，以及意外出現的空白區域。要修改的是弱的投影片，不只是錯誤。

絕對不要捏造數據、引言、客戶、引用或媒體。把缺口和不確定性標示出來，不要用看似合理的虛構內容填滿。
