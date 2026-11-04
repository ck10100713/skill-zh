---
name: view-pdf
description: 互動式 PDF 檢視器。使用者想開啟、顯示或檢視 PDF，並一起以視覺方式協作時使用：加註解、標螢光、蓋章、填表單欄位、放置簽名/縮寫，或一起審閱標記。不適合用來摘要或擷取文字（那種情況改用原生的 Read）。
---

# PDF 檢視器：互動式文件工作流程

你可以使用一個本地的 PDF server，它會在即時檢視器裡 render 文件，
讓你加註解、填表單、放置簽名，並提供即時的視覺回饋。

## 什麼時候用這個 skill

**使用者想要互動時，才用 PDF 檢視器：**
- 「給我看這份合約」/「打開這篇論文」
- 「把重要條款標起來，讓我審閱」
- 「幫我填這份表單」
- 「在第 3 頁簽名」/「每一頁都加上我的縮寫」
- 「蓋上機密章」/「標記為已核准」
- 「帶我看這份文件，把重要的部分加上註解」

**純粹要讀取內容時，不要用檢視器：**
- 「摘要這份 PDF」→ 直接用原生的 Read 工具
- 「第 5 頁寫了什麼？」→ 用 Read
- 「擷取第 3 節的表格」→ 用 Read

檢視器的價值在於把文件展示給使用者，並一起協作標記，
不是把文字串流回給你。

## 工具

### `list_pdfs`
列出可用的本地 PDF 和允許的本地目錄。沒有參數。

### `display_pdf`
在互動式檢視器中開啟 PDF。**每份文件只呼叫一次。**
- `url` — 本地檔案路徑或 HTTPS URL
- `page` — 起始頁面（選填，預設 1）
- `elicit_form_inputs` — 如果是 `true`，會在顯示之前提示使用者填寫表單
  欄位（用於互動式填表）

會回傳 `viewUUID`，要把它傳給每一次 `interact` 呼叫。再次呼叫
`display_pdf` 會建立**另一個**檢視器；用新 UUID 做的 interact 呼叫
不會傳到使用者正在看的那一個。

如果 PDF 有可填寫的欄位，也會回傳 `formFields`（名稱、類型、頁面、邊界框），
放置簽名時就用這些座標。

### `interact`
`display_pdf` 之後的所有後續動作。傳入 `viewUUID` 加上一個或
多個指令。透過 `commands` 陣列**把多個指令批次放在同一次呼叫**，
它們會依序執行。批次的最後要加上
`get_screenshot`，用視覺方式驗證變更。

**註解動作：**
- `add_annotations` — 新增標記（類型見下方）
- `update_annotations` — 修改既有的（需要 id + type）
- `remove_annotations` — 用 id 陣列刪除
- `highlight_text` — 依查詢自動找到文字並標螢光
  （文字標記時優先用這個，不要手動指定 rect）

**導覽動作：**
- `navigate` (page)、`search` (query)、`find` (query, silent)、
  `search_navigate` (matchIndex)、`zoom` (scale 0.5–3.0)

**擷取動作：**
- `get_text` — 從頁面範圍擷取文字（最多 20 頁）。用來
  閱讀內容、決定要加什麼註解，不是用來做摘要。
- `get_screenshot` — 把一頁擷取成圖片（驗證你的註解）

**表單動作：**
- `fill_form` — 填寫具名欄位：`fields: [{name, value}, ...]`

## 註解類型

所有註解都需要 `id`（唯一字串）、`type`、`page`（從 1 開始）。
座標單位是 PDF point（1/72 英吋），原點在**左上角**，Y 往下遞增。
US Letter 是 612×792pt。

| 類型 | 主要屬性 | 用途 |
|------|----------------|---------|
| `highlight` | `rects`, `color?`, `content?` | 標記重要文字 |
| `underline` | `rects`, `color?` | 強調用語 |
| `strikethrough` | `rects`, `color?` | 標記刪除 |
| `note` | `x`, `y`, `content`, `color?` | 便利貼式的註解 |
| `freetext` | `x`, `y`, `content`, `fontSize?` | 頁面上看得到的文字 |
| `rectangle` | `x`, `y`, `width`, `height`, `color?`, `fillColor?` | 框出區域 |
| `circle` | `x`, `y`, `width`, `height`, `color?`, `fillColor?` | 圈出區域 |
| `line` | `x1`, `y1`, `x2`, `y2`, `color?` | 畫線/箭頭 |
| `stamp` | `x`, `y`, `label`, `color?`, `rotation?` | APPROVED、DRAFT、CONFIDENTIAL 等 |
| `image` | `imageUrl`, `x?`, `y?`, `width?`, `height?` | **簽名、縮寫**、logo |

**圖片註解**接受本地檔案路徑或 HTTPS URL（不支援 data:
URI）。省略尺寸時會自動偵測。使用者也可以直接把圖片
拖放到檢視器上。

## 互動式工作流程

### 協作註解（AI 主導）
1. 用 `display_pdf` 開啟文件
2. `interact` → 對相關頁面範圍用 `get_text` 了解內容
3. 向使用者提出一批註解（描述你要標記什麼）
4. 核准後，`interact` → `add_annotations` + `get_screenshot`
5. 給使用者看，詢問要不要修改，反覆調整
6. 完成後，提醒他們可以從檢視器的工具列
   下載加了註解的 PDF

### 填表單（視覺化，不是程式化）
不像 headless 的表單工具，這個方式讓使用者有**即時的視覺
回饋**，也能處理欄位名稱晦澀/沒命名、標籤是印在頁面上
而不是在欄位 metadata 裡的表單。

1. `display_pdf` — 檢查回傳的 `formFields`（名稱、類型、頁面、
   邊界框）
2. 如果欄位名稱很晦澀（`Text1`、`Field_7`），對那些頁面用 `get_screenshot`，
   再把邊界框對應到畫面上的標籤
3. 用**畫面上的**標籤向使用者問值，或從
   脈絡推斷
4. `interact` → `fill_form`，然後 `get_screenshot` 顯示結果
5. 使用者直接在檢視器裡確認或修改

對於簡單、標籤清楚的表單，用 `display_pdf` 搭配
`elicit_form_inputs: true`，一開始就提示使用者。

### 簽名（視覺化，不具認證效力）
1. 詢問簽名/縮寫的圖片路徑
2. `display_pdf`，檢查 `formFields` 裡有沒有簽名類型的欄位，或詢問
   要放在哪一頁/位置
3. `interact` → 用 `type: "image"` 的 `add_annotations`，放在目標
   座標
4. 用 `get_screenshot` 確認位置

**免責聲明：** 這只是放置一張視覺的簽名圖片。它**不是**
經過認證或密碼學的數位簽章。

## 支援的來源

- 本地檔案（client MCP root 底下的路徑）
- arXiv（`/abs/` URL 會自動轉成 PDF）
- 任何直接的 HTTPS PDF URL（bioRxiv、Zenodo、OSF 等，要用
  直接的 PDF 連結，不是 landing page）

## 範圍外

- **摘要 / 文字擷取** — 改用原生的 Read
- **認證的數位簽章** — 只做圖片蓋章
- **建立 PDF** — 只能處理既有的 PDF
