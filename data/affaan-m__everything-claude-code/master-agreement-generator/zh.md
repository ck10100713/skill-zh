---
name: master-agreement-generator
description: 用一份範本加一個 JSON spec，產出交易對手主協議的審閱用草稿，條款依角色挑選，Schedule A 流程僅限於已簽署協議所賦予的通知權限內。需要可重現的起草流程，以及另外審閱的簽署準備作業時使用。
---

# Master Agreement Generator

一份主範本、每個交易對手一個小 spec、一個草稿建置步驟。
產生器輸出一律標上 **DRAFT**，連從已填完的範本產生的文件也一樣。轉檔成功只證明成品有產出，
不代表法律上完整、有締約權限，或可以寄出、簽署。
已簽署的協議可能允許用通知的方式新增指定的商機；
要用 Schedule A 流程之前，必須先確認有這個權限。

## When to Use

- 你要對很多交易對手發出同一套條款的框架協議（NDA、介紹或引薦費、
  禁止規避、master services），只有幾個欄位因對象而異。
- 案子陸續增加，每一件都要重新做文件，成了瓶頸。
- 文件必須能從受版控的原始檔重現、可以 diff，而且沒有手動編輯。
- 簽名欄位是用自動化放置的，需要穩定的頁面版面。

## How It Works

### Template

單一份 markdown 範本，裡面有 `{{PLACEHOLDER}}` 欄位。每個因對象而異的值都是 placeholder，
其他全是固定文字。骨架放在
[references/master-template.example.md](references/master-template.example.md)。
把裡面的泛用句子換成你們法務核可的條款。

參考腳本會填入的 placeholder：

| Placeholder | 來源 |
| --- | --- |
| `{{DATE}}` | `spec.date`，預設今天 |
| `{{CP_SHORT}}` | `spec.short` |
| `{{CP_LEGAL}}`、`{{CP_JURIS}}`、`{{CP_ADDR}}` | spec 欄位；如果由交易對手在簽署時自己填，就是空白線 |
| `{{ROLE_CLAUSE}}`、`{{FEE_TITLE}}`、`{{FEE_CLAUSE}}` | 由 `spec.role` 從角色表挑選 |
| `{{SCHEDULE_ROWS}}` | `spec.schedule`，或一列「簽署時無項目」 |
| `{{SUPPLEMENT_CLAUSE}}` | `spec.supplement`，後面接分隔符號，或留空 |
| `{{CP_SIGBLOCK}}`、`{{CP_SIGNER}}`、`{{CP_TITLE}}`、`{{CP_EMAIL}}` | 簽名區塊欄位，不知道就留空白 |

### Spec

每個交易對手一個 JSON 檔：

```json
{
  "file": "AcmeSupplier",
  "short": "Acme",
  "role": "supplier",
  "legal": "Acme Compute Ltd",
  "juris": "England and Wales company",
  "addr": "1 Example Street, London",
  "signer": "A. Person",
  "title": "Director",
  "email": "signer@example.com",
  "schedule": [["1", "2026-09-01", "Lot A (16 nodes)", "introducer", "12 months", "standard"]],
  "supplement": "the Data Processing Addendum dated 2026-09-01"
}
```

草稿只要求 `file`、`short`、`role`。缺的簽名欄位會渲染成空白線，留待審閱和填寫。
見 [references/spec.example.json](references/spec.example.json)。

`file` 必須是非空、可攜的檔名，例如 `AcmeSupplier` 或
`Acme Supplier`，不能含目錄成分。建置器會拒絕兩種路徑分隔符號、
磁碟機 / UNC 語法、控制字元、Windows 保留的標點或裝置名稱，
以及結尾的句點或空白。不合法的名稱直接拒絕，不會清理或改名，
而且發生在建立輸出或呼叫 pandoc 之前。

省略 `schedule` 或用 `[]`，就會出現「簽署時無項目」的 placeholder。有提供的
schedule 必須是密集的陣列，每個元素是六格的陣列，順序為：
編號、日期、受保護的交易對手或批次、角色、條件、費用。每格必須是
合法的 Unicode 字串或有限數字；刻意留白可以用空字串。
null、布林值、物件、巢狀的格子陣列、缺格和非有限數字，
都會在任何成品寫入或 pandoc 動作之前，連同列 / 格索引一起被拒絕。
未配對的 UTF-16 surrogate 也一樣直接拒絕，不會在 UTF-8 輸出時被替換；
合法的補充字元（例如 emoji）仍然支援。

格子內容是純文字，不是 Markdown 或 HTML。建置器會把語法字元編碼，
讓字面上的直線、反斜線、反引號和標記留在原本的欄位裡。
每個 CRLF、單獨的 CR 或 LF 都會變成一個空白；換行前後的文字保留。
其他空白和字面標點在渲染後的格子裡原樣保留。
來源 spec 不會被修改。正常合法的 schedule 會保留六欄；
格式錯誤的輸入絕不會被默默換成空 schedule。

### Role table

`spec.role` 會挑出三個字串：常設安排條款、費用章節標題，以及費用條款的開頭。

| Role | 誰付費 | 條款的形狀 |
| --- | --- | --- |
| buyer | 交易對手就與被介紹對象的交易付費 | 交易對手以非專屬方式委任我們尋找並介紹 |
| supplier | 交易對手就與被介紹對象的交易付費；我們以本人身分購買時，依 schedule 條件簽約 | 交易對手向我們和我們介紹的買方提供產能 |
| mutual | 靠對方介紹成交的一方付費 | 雙方都可以介紹；成交的一方付費 |

未知的角色在建置時會被拒絕。

### Build

只使用經營運人員審閱過的範本和 spec。Schedule A 以外的一般範本替換
可以帶標記語法，它不是處理不受信任文件的 sanitizer。
Pandoc 可以讀取引用的本機或遠端資源；這個產生器不會對轉換器的檔案系統或網路存取做 sandbox。
請自行審閱那些引用，並在你自己適當受限的環境裡做轉換。
針對性的測試用的是模擬的轉換器，不保證真實 DOCX 的版面或隔離。

```sh
node skills/master-agreement-generator/scripts/build-agreement.js \
  skills/master-agreement-generator/references/master-template.example.md \
  specs/AcmeSupplier.json \
  out/
```

腳本會填入 placeholder、渲染 schedule 表格，並寫出
`out/<file> MASTER.md`，附上強制的 DRAFT 聲明。預設（或加 `--require-docx`）
它需要已安裝的 pandoc 來產生非空的一般檔案 `.docx`。找不到 pandoc、轉換失敗，
或輸出缺漏 / 為空，都會回傳 exit code 1。每次 pandoc 探測或轉換都限制在十秒內。
未知、重複或互相衝突的旗標會回傳 exit code 2。

要成功產出只有 Markdown 的草稿，必須明確加 `--markdown-only`。這個模式
絕不探測或呼叫 pandoc，在函式庫裡回傳 `docxSkipped: true`，
而且不提供 DOCX 給電子簽署流程。函式庫呼叫端必須傳
`{ markdownOnly: true }`；只傳 `{ pandoc: false }` 現在會因為不滿足 DOCX 要求而失敗。
結果一律回報 `documentStatus: 'draft'`。重建 Markdown 時，
既有產生的 DOCX 會被移除，轉換失敗也不會留下殘缺的 DOCX，
所以舊成品不可能冒充現在的輸出。兩個產生的檔案都不要進版控；
範本和 spec 才是原始檔。

沒有「正式簽署版」模式。範例刻意保留了未解決的
方括號起草指示；填完 `{{PLACEHOLDER}}` 並不會讓
那些法律條文完整。準備簽署文件之前，要另外請人審閱填好的條款、當事人資料、
有權簽署的人、商業條件和確切的文件版本。
草稿和審閱過的簽署版要當作兩份不同的紀錄保存。就算 DOCX 轉換成功，
也不代表可以上傳、寄出或簽署。見 esign-field-placement 的核准流程。

兩個輸出位置都必須是解析後輸出目錄的直接子項。
任一位置如果已有 symlink（包括懸空的連結），在寫出任何成品之前就會被拒絕，
即使 DOCX 轉換已停用也一樣。一般的
regular file 可以重建。請用你自己控制的輸出目錄；這些檢查
不能對抗同時發生的惡意檔案系統變動。回傳的
成品路徑是絕對路徑。

### Signature page geometry

範本用 OpenXML 分頁符號結束本文，讓簽名區塊
在相容的 DOCX 渲染器裡另起一頁：

````markdown
```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```
````

簽名頁的結構（我方區塊，接著交易對手區塊，各有
By、Name、Title、Email、Date）是固定的，但分頁會隨文字、
字型、渲染器或格式而變。放置欄位之前，要檢查實際審閱過的文件和它的頁面
幾何；見 esign-field-placement skill。

### Schedule A append workflow

依已簽署協議實際的權限和通知要求來做：

1. 在**內部**的協商 / 核准管道審閱商機的經濟條件和協商策略。
   寄出合約內容之前，先取得承諾核准。共用的交易對手管道不算內部管道。
2. 確認提議的項目、角色、條件、費用和生效日，都落在
   協議明文的 Schedule A 通知權限內。常設條款的變更，
   或超出該權限的變動，要走適用的
   修訂程序；通知不能替自己製造例外。
3. 草擬一份經核准、針對該交易對手、有日期的通知，收件人和
   通知管道要符合已簽署協議的授權。放進有用的商業
   內容：受保護的交易對手或批次、授權的角色、商業條件
   和適用的費用。不要放內部利潤、協商策略、其他
   當事人的經濟條件、系統追蹤紀錄、原始錯誤和內部歸檔通知。
4. 寄出前，把這份通知的確切內容歸檔，送營運人員核准；見
   operator-approval-loop。在缺少核准或參與權限的期間，
   交易對手管道上保持沉默。核准和「有授權的寄件人確實送出通知」的證據是兩回事。
5. 依已簽署協議實際的要求，記錄授權送達的證據、生效日和任何
   異議。範例中的期間不是預設值。已簽署的文件保持不可變；更新受版控的 schedule
   紀錄，重建一份**草稿合併檢視**供內部審閱，並附上
   已簽署版本和已核准通知的參照。這次重建不會
   取代簽署的協議，也不證明有法律效力。

## Examples

### Notice text

僅為示意草稿：只有在已簽署的
協議授權這些條件和日期，而且營運人員核准這份確切的收件人通知時，才能使用。

```text
Schedule A notice, 2026-09-02
Agreement: Master Agreement dated 2026-08-14 between Us and Acme
Entry 2: Lot B, 8 nodes, region EU-West
Role: introducer
Terms: 6 month term, start no later than 2026-10-01
Fee: standard
This entry takes effect today unless you object within ten business days
with dated written evidence of a prior relationship with the counterparty.
```

### Adding the entry to the spec

```json
"schedule": [
  ["1", "2026-08-20", "Lot A (16 nodes)", "introducer", "12 months", "standard"],
  ["2", "2026-09-02", "Lot B (8 nodes, EU-West)", "introducer", "6 months", "standard"]
]
```

重建、diff 草稿 Markdown，再把合併草稿附到
內部紀錄裡，和未更動的已簽署文件、通知證據放在一起。

### Counterparty fills its own details at signing

起草時，從 spec 省略 `legal`、`juris`、`addr`、`signer`、`title`、`email`，
就會渲染成空白線。要由另外審閱的簽署流程來決定
哪些資料可以由交易對手填寫，並驗證實際欄位；
產生器不會建立或核准電子簽署 envelope。
