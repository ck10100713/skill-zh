---
name: canva-creator
description: >
  拿一份核准的內容企劃，端到端執行整個活動：建立發文行事曆、為社群貼文產生 Canva 設計、草擬文案和 email 內容，
  並把社群發文排進 HubSpot。Canva 只用在社群貼文（Instagram、Facebook、X、LinkedIn），
  email 內容以純文字草擬，直接顯示在對話裡，讓老闆從自己的工具寄出。
  每一步都需要老闆明確核准。這是一次到位的活動執行器：放進一份完成的企劃，產出一整個完整的活動。
  當老闆交出核准的企劃或指向某一份時使用，例如「run this brief」「execute the campaign」
  「turn this brief into posts」「build the campaign from the plan we approved」。
  至於沒有企劃的日常發文，例如「I need to post more」「what should we post」，請改用 social-content-engine，
  由它負責常態行事曆。
allowed-tools: Read, WebFetch
---

# Canva Creator

## 範圍

這個 skill 分五個依序進行的階段處理一個活動，每個階段都由老闆核准把關：

```
brief → calendar → asset inventory → Canva designs → copy → HubSpot staging
```

| 路徑 | 通路 | 這個 skill 產出什麼 |
|------|----------|--------------------------|
| Canva（社群） | Instagram、Facebook、X/Twitter、LinkedIn | Canva 設計 + 文案 + 排程的 HubSpot 貼文 |
| 純文字 | Email（電子報、行銷信、drip） | 主旨 + preheader + 內文，直接顯示在對話裡讓老闆寄出 |

**任何情況下，Canva 都不用在 email 那幾列**：不用模板、不用 autofill、不複製設計、不上傳素材、不匯出。
Email 圖像不在這個 skill 的範圍內，因為當圖片欄位多過可用的照片時，email 模板的 autofill 會產生佔位圖，
而且變化版縮圖在聊天預覽裡會顯示失敗。如果老闆要求 Canva 的 email 設計，導向的措辭請看 `reference/gotchas.md`。

---

## 事前確認

在 Stage 1 之前，先確認：

1. **企劃。** 使用者已經引用或貼上一份核准的企劃。如果沒有：
   「我需要先有內容企劃，才能建立活動。你有 content-strategy skill 產出的嗎？還是你想現在寫一份？」

2. **Canva 方案。** Pro/Teams 需要從使用者的資料庫手動選模板（沒有 autofill API）。Enterprise 可以從品牌模板 autofill。

3. **HubSpot 方案。** 社群排程需要 Marketing Hub Professional。Starter 或 Free 就跳過 Stage 5，改匯出 CSV
   （見 [reference/hubspot-staging.md](reference/hubspot-staging.md)）。

4. **品牌素材。** 如果有連線店面（Shopify 或 Square，兩者是平等的，`../../shared/connector-neutrality.md`），
   先讀商品清單：企劃裡提到的每個商品的標題、圖片 URL 和價格。
   只讀取，在 Stage 2 步驟 5 之前不會有任何東西上傳到 Canva，而且上傳的也只有核准的行事曆時段需要的圖片。
   那份清單就是起始的照片庫存；只問店裡沒有圖片的商品。
   拉取規則（哪些欄位、價格宣稱規則）寫在
   [../social-content-engine/reference/shopify-assets.md](../social-content-engine/reference/shopify-assets.md)
   （是針對 Shopify 寫的；Square 的目錄圖片依相同步驟，從工具清單取得）。
   沒有店面的話，要確認商品照片在硬碟上的路徑，或品牌套件已經在 Canva 裡設定好。

5. **產生額度。** 估算活動的 Canva 用量，並在 Stage 1 開始之前秀出來。預設是每個走 Canva 的列產生 3 個候選；
   每個設計大約花 5 次 API 呼叫（autofill + export + polling）。

   ```
   這個活動的產生額度：
     Canva（社群）列數：   8
     每列候選數：          3   （預設，說「single candidate」改成 1）
     設計總數：            24
     API 呼叫（約）：      ~120  （autofill + export + polling）

   Canva 上限：每分鐘 100 次請求。這大約需要 2 到 3 分鐘的產生時間，
   完全在你的方案上限之內。要繼續嗎？
   ```

   如果預估的設計總數超過 30，一開始就建議用單一候選模式，大型活動的餘裕很快就會用完。
   在 Stage 1 開始之前，老闆可以把預設改成每列 1、2 或 3 個候選。選好的值在整個 session 都鎖定。

---

## 工作流程

### Stage 1 — 發文行事曆

從企劃裡取出：內容主題、通路、頻率、固定日期（上市、促銷、節日）。

建立一個帶 `Path` 欄的行事曆表格，把每一列導向 Canva 或純文字草擬：

| Date | Channel | Path | Theme | Asset type | Caption/Subject angle |
|------|---------|------|-------|------------|-----------------------|
| Jun 2 | Instagram feed | Canva (social) | Linen launch | Square post | "finally, a dress…" |
| Jun 5 | Email | Text-only | Linen launch | Email body | "Linen that actually breathes" |

呈現之前，要把每個 email 通路的列都標成 `Text-only`。除非企劃另有指定，否則上限 30 天。
排程衝突（同一天針對同一個商品發兩篇）要事先標出來。

**Checkpoint 1。** 呈現行事曆。問：「這符合計畫嗎？有要調整的日期、要加的通路，或要換的主題嗎？」
反覆調整直到核准，然後在進入下一步之前把拆分大聲複述一次：「N 列走 Canva，M 列走純文字草擬」。
在這裡抓到分類錯誤是免費的；等設計都產生完才抓到就不是了。

---

### Stage 2 — 素材盤點（只針對 Canva 的列）

Email 的列完全跳過這個階段。對每個 `Canva (social)` 列，建立一份清單，列出模板需要什麼、已經有什麼。

1. **逐一用名稱列出每個圖片欄位。** 正方形的 Instagram 貼文通常有 1 到 2 個圖片欄位；
   輪播和商品格狀版面可能有 5 個以上。要一個一個列出
   （`Header_Image`、`Product1_Image`、`Product2_Image`、…），絕對不要籠統地歸成「商品圖片」。
   - Enterprise：從品牌模板的 `dataset[].label` 讀取欄位名稱（`GET /v1/brand-templates/{id}`）。
   - Pro/Teams：數模板裡每一個不同的圖片矩形。

2. **盤點可用的素材。** 企劃裡的文字內容（商品名稱、優惠文案、標語、價格）、
   事前確認時從連線店面讀到的商品圖片 URL（在步驟 5 上傳，只傳缺口表需要的欄位，並在那時用 `asset.id` 記錄）、
   已經上傳到 Canva 的商品照片（`GET /v1/assets`）或老闆硬碟上的照片、
   品牌套件的顏色和字型（Enterprise）。文案裡的價格要來自店面回傳的值或企劃，絕對不能憑記憶。

3. **建立逐欄位的缺口表。** 每個設計的每個欄位一列，不是每個設計一列。

   | Date | Slot name | Slot kind | Available asset | Status |
   |------|-----------|-----------|-----------------|--------|
   | Jun 2 | Hero_Image | image | bloom_summer.jpg → asset_id pending | upload |
   | Jun 2 | Headline | text | "Summer linen, finally" | ready |
   | Jun 9 | Product1_Image | image | — | **MISSING** |

4. **跟老闆解決欄位和素材不吻合的問題。** 如果模板的圖片欄位比企劃提供的照片多，就暫停並詢問：

   ```
   「Summer Carousel」模板有 5 個圖片欄位。企劃只給了我 1 張照片
   （bloom_summer.jpg）。其他 4 個要怎麼填？

     1. 5 個欄位都重複用同一張照片
     2. 你再給我 4 張照片（檔案路徑）
     3. 換一個欄位比較少的簡單模板
   ```

   老闆選好之前，不要做任何產生呼叫。帶著空欄位去產生，會得到一堆填滿 Canva 預設風景佔位圖的設計。

5. **上傳缺少的照片，並取得驗證過的 asset ID。** 透過 `POST /v1/asset-uploads` 上傳，
   然後輪詢 `GET /v1/asset-uploads/{job_id}` 直到 `status == "success"`。
   記錄回應裡的 `asset.id`，這是唯一能用在 autofill 圖片欄位的值。
   傳空字串、URL、檔案路徑或過期的 ID，都會默默渲染成 Canva 的預設風景圖，而不是那張照片。

6. **確認清單。** 把完成的逐欄位表格給老闆看，每個欄位都已解決、每張圖片的 `asset.id` 都已確認。
   這是呼叫 Canva API 之前的最後一站。

---

### Stage 3 — Canva 設計產生

在任何 Canva API 呼叫之前，重新讀一次行事曆，把 `Path` 不是 `Canva (social)` 的列全部剔除。
Email 的列不會經過這個階段。

**一次一個行事曆列**地產生設計，每列 3 個候選（或事前確認時選的值）。每一列都跑同一個迴圈：
產生候選 → 驗證 → 匯出 → 目視檢查 → 重試失敗的 → 呈現 → 等老闆挑 → 下一列。
列與列之間暫停 30 秒。這樣能把突發流量壓在大約每 30 秒 3 次產生 + 3 次匯出，遠低於 Canva 每分鐘 100 次請求的上限。
不要同時平行處理多列；一次一列，是避免老闆在活動進行到一半就撞到額度的保護。

**輪詢頻率。** 每 3 到 5 秒輪詢一次工作狀態，不要更快。更密的間隔只會耗額度，不會讓完成變快。

**預覽 URL：只有一種類型能安全嵌入。** Autofill 回應回傳的 `design.canva.ai` 縮圖幾分鐘內就會過期；
把它們嵌成 markdown 圖片，會出現壞掉的「Show Image」佔位。
永久的匯出 URL（`export-download.canva.com` 或 `export-design` MCP 工具）不會過期。
原生 Cowork 輪播會用 connector 已驗證的 session 直接渲染 autofill 結果，讓它們自己渲染，不要重新嵌入。

#### 每列的迴圈

1. **決定模板。**（每個 session 做一次，除非行事曆混用了不同素材類型，否則各列用同一個模板。）
   - Enterprise：`GET /v1/brand-templates`，依素材類型篩選。
   - Pro/Teams：`GET /v1/designs?ownership=any&query={template name}`，把前 3 名給老闆看，產生前先確認一個。

2. **平行產生該列的候選。** 同時發出該列的 3 個候選（或事前確認時的 N 個）。
   - Enterprise：每個候選各自 `POST /v1/autofills`，帶模板 ID 和欄位值。同時輪詢所有工作。
   - Pro/Teams：`POST /v1/designs` 建立副本。說明老闆要在 Canva 裡套用的文字和圖片編輯；把設計 ID 收回來。

3. **驗證工作狀態。** 對每個候選，確認 `GET /autofills/{job_id}` 回傳 `status == "success"`，而且 `result.design.id` 存在。
   錯誤逐個設計處理：
   - `JOB_FAILED` → 讀 `job.error.message`，修正欄位值或素材 ID，重試一次。
   - `RATE_LIMIT_EXCEEDED`（這個 session 第一次碰到）→ 等 60 秒，只對那一個候選重試一次。這是處理暫時性的尖峰。
   - `RATE_LIMIT_EXCEEDED`（這個 session 第二次碰到）**或**任何 `quota_exceeded` / 每日上限錯誤 → 立刻停止產生。
     不要重試。秀出進度並詢問：

     ```
     Canva 正在對這個活動限流。目前狀態：
       ✓ 已產生：  貼文 1-4（12 個設計）
       ⏸ 剩餘：    貼文 5-8（12 個設計還沒產生）

     要怎麼進行？
       1. 剩下的列改成每列 1 個候選（共 4 個設計），現在就能做完
       2. 暫停活動，額度重新補充後（60 分鐘）再繼續
       3. 停止產生，用現有的東西繼續做文案
     ```

     等老闆選擇。不要陷入重試迴圈。

4. **把每個成功的候選匯出成永久的 PNG。** 平行發出該列的匯出。
   - REST：`POST /v1/exports`，帶 `format.type: "png"`，輪詢 `GET /v1/exports/{job_id}` 直到成功，取得 `urls[0]`。
   - Canva MCP：用設計 ID 呼叫 `export-design`。

   這些永久 URL 就是之後嵌入預覽、附到 HubSpot 貼文的東西。Autofill 回應的縮圖在下游絕對不使用。

5. **目視驗證每個匯出。** 看圖片，只要出現下列任何一種就拒絕，它們都代表欄位沒填或素材錯誤：
   - 有雲和綠色山丘的通用風景圖（Canva 的預設佔位圖）
   - 該放照片的地方是純灰色矩形
   - Lorem-ipsum 或模板預設文字
   - 主題跟企劃不符（錯的商品、錯的品牌）

   如果候選沒通過驗證：重新檢查受影響欄位的清單，修正 `asset.id`，只重新產生那一個候選，重新匯出、重新驗證。

6. **部分失敗時，逐個候選重試。** 如果該列 N 個候選中有 1 個在步驟 3 或 5 失敗，就只重新產生那一個，
   不要整列重做，也不要呈現一個壞掉的輪播。如果第二次嘗試也失敗：

   ```
   6/9 貼文的第三個候選一直失敗，Canva 回傳了
   [錯誤 / 渲染出佔位圖]。要怎麼進行？

     1. 跳過它，呈現另外 2 個並繼續
     2. 只針對這個候選換成較簡單的模板
     3. 換一張不同的照片再試一次
   ```

7. **呈現該列的候選。** 讓原生 Cowork 輪播渲染 autofill 工具的結果。在它下面加一段文字提示：

   ```
   6/9 的候選都好了，請在上面的輪播裡捲動看看。
   6/9 的貼文要用哪一個？
   ```

   如果輪播沒有渲染，或有一個位置壞掉，就改嵌入步驟 4 的永久匯出 PNG URL。
   最後的備案：連到設計的 Canva 編輯 URL（`https://www.canva.com/d/{design_id}`）。
   絕對不要重新嵌入 `design.canva.ai` URL。

8. **暫停 30 秒，然後進到下一列。**

**Checkpoint 2。** 老闆為每個行事曆列挑好一個設計就算完成。如果他們想重新產生，只重新產生那一個候選。

---

### Stage 4 — 文案草擬

為每個行事曆列草擬文案。社群的列要寫貼文文案；email 的列要寫完整的 email。

**社群貼文文案**（Instagram、Facebook、X、LinkedIn）：

- 長度：符合通路（Instagram ≤ 2,200 字元；Facebook 建議 ≤ 500；X ≤ 280）。
- 結構：hook → 一個商品好處 → CTA → 3 到 5 個 hashtag（不是 30 個）。
- 語氣：符合企劃的語氣標記。如果企劃說「輕鬆友善」，就不要寫企業腔的文案。
- 不要灌水。不要寫「Exciting news!」或「We're thrilled to announce」。開頭就講價值。

**Email 內容**：整封 email 由 Claude 寫，不用 Canva：

- 主旨：≤ 50 字元，具體，不要標題黨。「Spring projects are booking up」勝過「Don't miss out!」
- Preheader：≤ 90 字元，補充主旨但不重複。
- 內文：純文字敘述，100 到 250 字。開頭一句要讓人願意讀下去 → 1 到 2 段有內容的文字 → 單一明確的 CTA → 結尾問候。
- 語氣：跟社群用同樣的語氣標記。老闆希望 email 聽起來像他們自己，而不是像套版的電子報。
- 不要提到圖片。不要寫「見上圖」。如果老闆要視覺素材，他們在自己的 email 工具裡加。
- 每封 email 一個 CTA。挑最重要的動作，並把它放在最前面。

把文案直接放在每個社群列的下方。把完整的 email 直接放在每個 email 列的下方：

```
Subject: <subject line>
Preheader: <preheader text>

<body text>
```

實際範例請看
[reference/examples/boutique-brief-campaign.md](reference/examples/boutique-brief-campaign.md)。

**Checkpoint 3。**「有要重寫的文案或 email 嗎？標出日期和要改的地方。」反覆調整直到核准。

---

### Stage 5 — HubSpot 排程 + email 交接

把社群貼文排進 HubSpot。Email 內容不排程，直接顯示在對話裡，讓老闆複製到自己的 email 工具。
API 欄位參考請看 [reference/hubspot-staging.md](reference/hubspot-staging.md)。

1. **建立活動。** `POST /marketing/v3/campaigns`，帶活動名稱和行事曆裡的開始/結束日期。

2. **排程每則社群貼文。** 每個 `Canva (social)` 列對 HubSpot Social API 做一次 `POST`：
   - `channel`：把行事曆的通路對應到 HubSpot 帳號 ID
   - `scheduledAt`：ISO 8601 日期時間，呼叫之前先確認是未來的時間
   - `content.body`：核准的文案
   - `attachments`：Stage 3 的永久 Canva 匯出 PNG URL
   - `status`：`SCHEDULED`（絕對不用 `PUBLISHED`）

3. **確認佇列。** 呼叫 `GET /marketing/v3/social/posts?status=SCHEDULED`，秀出清單，並提供 HubSpot 活動檢視的直接連結。

4. **秀出 email 內容做交接。** 每個 email 列，依寄送日期分組，直接呈現核准的主旨 + preheader + 內文。
   老闆把這些複製到自己的 email 工具（HubSpot Marketing Email、Mailchimp、Gmail 或 M365）。

**最後的 checkpoint。**

```
你的社群貼文已經在 HubSpot 排程好了：[link]
它們會照排程發出，你可以在 HubSpot 裡取消或編輯任何一則貼文。

Email 內容草擬在下面，準備好要寄的時候，把每一封複製到你的 email 工具：

  Jun 5 — "Spring projects are booking up"
  Jul 15 — "Summer maintenance windows are filling"

結束之前有要改的嗎？
```

在這份摘要之外（絕對不是取代它），依 house style（`../../shared/artifact-style.md`）把活動渲染成一個 HTML artifact：
發文行事曆做成表格，每一列有各通路的狀態標籤（scheduled / drafted / handoff），
每列還有一個已排程貼文的面板，放核准的文案或 email 內容，以及它的匯出 PNG 連結。

**收尾提議。** 用一行說明活動現在包含什麼，然後給一個最相關的下一步和它的觸發說法，
通常是貼文開始發出之後的「is my marketing working?」（`growth-pulse`）。
最多再加兩個：「make the content」（`social-content-engine`）處理常態行事曆，或「my ads」（`ad-manager`）。
最多三個；這個 session 裡老闆拒絕過的就不要再提。

---

## 核准關卡

- **email 的列不能呼叫 Canva。** 每次 API 呼叫前都要重新檢查 `Path` 欄。
- **不能發布。** 每則 HubSpot 貼文都排成 `SCHEDULED`；上線由老闆控制。
- **事前確認時一定要秀出產生額度。** Stage 1 開始之前，老闆要看到設計總數並核准。
- **Stage 3 一次一列。** 同一列裡的候選平行發出，但列與列之間依序進行，中間隔 30 秒，這是額度的保護。
- **第二次碰到額度錯誤，就暫停並詢問。** 絕對不要陷入重試迴圈。
- **呈現之前，一定要先匯出成永久的 PNG。** 工作成功不代表設計渲染正確。
- **絕對不要在訊息裡嵌入 `design.canva.ai` URL。** 它們會過期。
- **當一個候選失敗時，絕對不要重新產生整列。** 只做逐個候選的重試。
- **絕對不要替 Pro/Teams 使用者自動選模板。** 一定要確認。
- **絕對不要跳過逐欄位的盤點。** 多欄位的模板只要有任何欄位是空的，就會渲染出風景佔位圖。
- **絕對不要跳過 Checkpoint 1。** 行事曆還沒核准就開始產生，是這個 skill 裡浪費工作最大的來源。

---

## 參考

- [reference/canva-api.md](reference/canva-api.md) — Canva Connect API 的 endpoint、素材上傳、匯出格式、MCP 對應工具
- [reference/hubspot-staging.md](reference/hubspot-staging.md) — HubSpot Social API，以及非 Pro 方案的 CSV 備案
- [reference/gotchas.md](reference/gotchas.md) — 常見失敗模式的好壞做法對照
- [reference/examples/boutique-brief-campaign.md](reference/examples/boutique-brief-campaign.md)
  — 完整的實際範例（單一欄位的社群貼文、多欄位模板）

## 使用沒列出的工具

這個 skill 裡提到的 connector 是測試過的路徑，不是一道牆。如果老闆想讓這個流程用某個沒連線或沒列出的工具，就提議 `build-connector`，它會先查 connector 目錄，沒有的話再透過 Zapier 連接，絕對不手工對著原始 API 硬幹。連線建好之後，這個工具就像其他任何可選的 connector 一樣加入這個 skill，受同樣的核准關卡約束。
