---
name: parcel-tracking
description: "追蹤包裹並查詢澳洲及國際快遞業者的配送狀態。搜尋 Gmail 裡的出貨/寄送 email，並提供所有主要澳洲快遞業者的追蹤連結，包括 AusPost、StarTrack、Aramex、CouriersPlease、Sendle、Toll、Team Global Express、DHL、FedEx、TNT、Hunter Express、Border Express、Direct Freight Express 和 UPS。觸發詞：'where is my parcel'、'track my order'、'has my package arrived'、'tracking status'、'check tracking'、'where is my delivery'。"
---

# Parcel Tracking

從 Gmail 的出貨 email 找出追蹤單號，並查詢澳洲及國際快遞業者的配送狀態。

## 什麼時候用

- 「我的包裹 / 包裹 / 訂單在哪？」
- 「我的 [商品] 到了 / 出貨了嗎？」
- 「追蹤我在 [商店] 的訂單」
- 「我的配送狀態是什麼？」
- 「我有 [商品] 的追蹤單號嗎？」
- 使用者貼上或提到追蹤單號
- 「查 StarTrack / AusPost / Aramex / Toll 的追蹤」

## 工作流程

### 步驟 1：找出追蹤單號

如果使用者已經提供追蹤單號，跳到步驟 2。

否則，搜尋 Gmail 裡的出貨 email。找符合以下條件的近期郵件：

```
dispatched OR shipped OR "tracking number" OR "consignment number" newer_than:30d
```

如果是特定商店或訂單，縮小搜尋範圍：
```
from:mwave.com.au dispatched
from:amazon.com.au shipped
```

讀 email 內文並擷取：
- 追蹤 / 託運單號
- 快遞業者名稱
- 訂單編號
- 出貨日期
- 配送備註（需要簽收等）

**Gmail 存取**：用現有的任何 Gmail 工具（Gmail MCP、gws CLI 的 `gws gmail`，或請使用者自己去查並貼上追蹤單號）。

### 步驟 2：辨識快遞業者並組出追蹤連結

用下面的表，從追蹤單號格式或出貨 email 辨識快遞業者，並盡可能組出直接的追蹤連結。

| 快遞業者 | 單號格式 / 範例 | 直接追蹤連結 |
|---------|------------------------|----------------------|
| **AusPost / StarTrack** | 英數混合，例如 `36VJ65064757`、`JD123456789AU` | `https://auspost.com.au/mypost/track/details/{NUMBER}` |
| **Sendle** | 6-8 個英數字元，例如 `SNFJJ3` | `https://track.sendle.com/tracking?ref={NUMBER}` |
| **DHL** | 10-12 位數字，例如 `1234567890` | `https://www.dhl.com/au-en/home/tracking.html?tracking-id={NUMBER}` |
| **FedEx** | 12-15 位數字，或 AU+10 位數字 | `https://www.fedex.com/apps/fedextrack/?tracknumbers={NUMBER}` |
| **TNT**（現在是 FedEx） | 9 位數字，例如 `907384999` | `https://www.tnt.com/express/en_au/site/shipping-tools/tracking.html`（貼上單號） |
| **UPS** | 以 1Z 開頭，18 個字元 | `https://www.ups.com/track?tracknum={NUMBER}` |
| **Aramex**（前身是 Fastway） | 數字標籤號碼，長度不一 | `https://www.aramex.com.au/tools/track`（貼上單號） |
| **CouriersPlease** | 數字或 CP 開頭 | `https://www.couriersplease.com.au/tools-track`（貼上單號） |
| **Toll / MyToll** | 數字託運單號，長度不一 | `https://mytoll.com/`（貼上單號） |
| **Team Global Express** | 數字，長度不一 | `https://myteamge.com/`（貼上單號） |
| **Hunter Express** | 英數混合，例如 `AIM478695` | `https://www.hunterexpress.com.au/tracking/`（貼上單號） |
| **Border Express** | 數字，長度不一 | `https://www.borderexpress.com.au/tracking/`（貼上單號） |
| **Direct Freight Express** | 數字託運單號 | `https://www.directfreight.com.au/ConsignmentStatus.aspx`（貼上單號） |

**深層連結**（追蹤單號直接放在 URL 裡）：AusPost/StarTrack、Sendle、DHL、FedEx、UPS。

**表單式**（連結和單號分開提供）：Aramex、CouriersPlease、Toll、Team Global Express、Hunter Express、Border Express、Direct Freight Express、TNT。

**如果不知道快遞業者：** 預設用 AusPost（在澳洲最常見），或請使用者去看他的出貨 email。

### 步驟 3：嘗試取得即時狀態

如果有網頁爬取工具，試著爬追蹤頁面：

```
url: {direct tracking URL}
wait_for: 3000 (many tracking pages are JS-rendered)
```

很多追蹤頁面被爬時只會回傳有限的資料。AusPost 尤其重度依賴 JS。如果爬到有用的狀態資訊，就放進去。沒有的話，就只提供直接連結。不要跟使用者提起爬取失敗的事。

如果有瀏覽器自動化工具（Chrome MCP、Playwright），就直接導覽到追蹤頁面讀取狀態。

如果沒有爬取/瀏覽器工具，就跳過這個步驟，只提供連結。

### 步驟 4：呈現結果

一定要包含：
1. **目前狀態**（有爬到就用爬到的，不然用出貨 email 裡的）
2. **直接追蹤連結**（一定要有）
3. **預計送達時段**（知道的話）
4. **配送備註**（需要簽收、通知卡取件等）

#### 範例：有深層連結的快遞業者

```
Order IN03069870 — Mac mini x 2
Dispatched by Mwave via AusPost/StarTrack on 17 Mar

Tracking: 36VJ65064757
Status: In transit — processed at Sydney sorting facility
Expected: Thu 19 – Fri 20 Mar
Note: Signature required. If no one home, parcel goes to local post office.

Track live: https://auspost.com.au/mypost/track/details/36VJ65064757
```

#### 範例：表單式的快遞業者

```
Order 12345 — [item]
Dispatched via Toll on 15 Mar

Consignment: TXY9876543
Expected: 3-5 business days

Track at: https://mytoll.com/
Paste consignment number: TXY9876543
```

### 處理多個包裹

廣泛搜尋：
```
(dispatched OR shipped OR "on its way" OR "tracking number") newer_than:30d
```

每個包裹各列成一個獨立的區塊。

## 快遞業者聯絡電話（澳洲）

| 快遞業者 | 電話 | 服務時間（AEST/AEDT） |
|---------|-------|-------------------|
| AusPost / StarTrack eParcel | 13 13 18 | 週一至週五 8am-6pm |
| StarTrack（帳戶客戶） | 13 23 45 | 營業時間 |
| CouriersPlease | 13 00 36 16 | 營業時間 |
| Toll Priority | 13 15 31 | 週一至週五 7am-10pm，週六日 7am-5pm |
| Toll IPEC | 1300 865 547 | 營業時間 |
| Hunter Express | 02 9780 4099 | 營業時間 |
| DHL | 13 14 06 | 營業時間 |
| FedEx / TNT | 13 26 10 | 營業時間 |
| UPS | 13 26 77 | 營業時間 |
| Aramex | 見 aramex.com.au/contact-us | 營業時間 |
| Sendle | 只有線上（客服表單） | — |
| Team Global Express | myteamge.com 的聯絡表單 | — |

## 各快遞業者的注意事項

**AusPost / StarTrack**
- URL 格式：`https://auspost.com.au/mypost/track/details/{TRACKING_NUMBER}`，追蹤單號直接放在路徑裡
- 區域配送在雪梨（Lidcombe/Chullora）處理之後，追蹤事件很少是正常的
- 出貨後最多要等 24 小時，追蹤資訊才會出現
- 需簽收的包裹如果沒送達，會送到當地郵局

**Sendle**
- Sendle 在 2025 年初停止了所有包裹收件，並引導客戶改用 Aramex。既有的 Sendle 貨件仍然可以追蹤。
- 深層連結：`https://track.sendle.com/tracking?ref={SENDLE_REFERENCE}`

**Toll vs Team Global Express**
- Toll Global Express 已被出售並更名為 Team Global Express，追蹤系統不同
- 國內的 Toll 包裹（IPEC、Priority、Express）仍然用 MyToll

## 工具彈性

這個 skill 配合手上有什麼工具就用什麼：

| 工具 | 能做到什麼 |
|------|----------------|
| Gmail 存取（任何 MCP 或 CLI） | 搜尋出貨 email 找追蹤單號 |
| 網頁爬取工具（任何 MCP） | 嘗試從追蹤頁面取得即時狀態 |
| 瀏覽器自動化（Chrome MCP、Playwright） | 導覽到追蹤頁面取得 JS 渲染的狀態 |
| 以上皆無 | 使用者提供追蹤單號，skill 提供正確的連結 |
