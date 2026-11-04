---
name: tear-sheet
description: "透過 Kensho LLM-ready API MCP server，用 S&P Capital IQ 資料產生專業的公司 tear sheet。只要使用者要求 tear sheet、公司一頁式簡介、公司簡介、fact sheet、公司快照或公司概覽文件，就使用這個 skill，尤其是使用者提到特定公司名稱或股票代號時。另外，當使用者要求股票研究摘要、併購的公司簡介、企業發展（corporate development）標的簡介、業務／BD 會議準備文件，或任何簡明的單一公司財務摘要時也要觸發。這個 skill 支援四種對象類型：股票研究、投資銀行／併購、企業發展，以及業務／商務開發。如果使用者沒有指定對象，要問。上市與未上市公司都適用。"
---

# 財務 Tear Sheet 產生器

透過 S&P Global MCP 工具從 S&P Capital IQ 拉即時資料，產生針對特定對象的公司 tear sheet，並把結果排成專業的 Word 文件。

## 樣式設定

這些是合理的預設值。要客製成貴公司的品牌，修改這一節即可，常見的改法包括換色盤、換字型（很多銀行標準用 Calibri）和更新免責聲明文字。

**顏色：**
- 主色（標題橫幅背景、區段標題文字）：#1F3864
- 強調色（招牌區段的重點標示）：#2E75B6
- 表格標題列底色：#D6E4F0
- 表格交替列底色：#F2F2F2
- 表格邊框：#CCCCCC
- 標題橫幅文字：#FFFFFF

**字體排印（docx-js 的大小單位是半點）：**
- 字型：Arial
- 公司名稱：18pt 粗體（size: 36）
- 區段標題：11pt 粗體（size: 22），主色
- 內文：9pt（size: 18）
- 表格文字：8.5pt（size: 17）
- 頁尾／免責聲明：7pt 斜體（size: 14）
- 各範本的個別覆寫，寫在每個參考檔的 Formatting Notes。

**公司標題橫幅：**
- 標題是橫跨整頁寬度的深藍（#1F3864）橫幅，公司名稱用白字。
- **橫幅下方，key-value 配對「一定要」用橫跨整頁寬度的兩欄無框表格呈現。** 左欄：公司識別資訊（股票代號、總部、成立時間、員工數、板塊）。右欄：財務識別資訊（市值、EV、股價、流通股數）。每個儲存格都在同一行放粗體標籤和一般粗細的值（例如 "**Market Cap** $124.7B"）。不要把所有欄位都靠左擠在同一欄，這樣浪費水平空間，看起來也不專業。兩欄展開，是區分專業 tear sheet 和預設文件最重要的單一視覺訊號。
  - **實作方式：** 建立 2 欄的表格，所有儲存格都設 `borders: none` 和 `shading: none`。各欄寬度設為 50%。左欄欄位（股票代號、總部、成立時間、員工數）以獨立段落放在左儲存格。右欄欄位（市值、EV、股價、流通股數）放在右儲存格。每個欄位是單一段落：標籤用粗體 run，值用一般 run。
  - 每一欄放哪些欄位，依對象而異，見參考檔的標題規格。原則永遠是：橫向展開，不要全擠在左邊。
- **標題的 key-value 區塊不要用有邊框的表格。** 有邊框的表格只保留給財務資料。
- 標題裡的關鍵指標（市值、EV、股價）要用行內 key-value 配對顯示，不要放進獨立的有邊框表格。

**區段標題：**
- 每個區段標題正下方都要有一條水平線（細線、#CCCCCC、0.5pt），讓各區段之間有乾淨的視覺分隔。
- **這條線要渲染成標題段落本身的下框線**，不要為這條線另外插入一個段落元素。另外的段落會自帶前後間距，導致區段標題下方留白過多。
- **實作方式：** 在 docx-js 中，用 `paragraph.borders.bottom = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" }` 對區段標題段落套用下框線。不要用 `doc.addParagraph()` 另外加水平線元素。不要用 `thematicBreak`。框線必須在標題段落本身，且段後間距為 0pt，這樣線才會緊貼標題文字。
- 間距：標題段落前 12pt、標題段落後 0pt、下一個內容元素前 4pt。

**項目符號格式：**
- 所有 tear sheet 類型的所有項目符號內容，都用單一項目符號字元（•）。同一份或不同份 tear sheet 之間，不要混用 •、-、▸ 或編號清單。
- **綜合／分析型項目符號**（Earnings Highlights、Strategic Fit、Integration Considerations、Conversation Starters）：區塊式縮排，左縮排 360 DXA（0.25"），項目符號字元用懸掛縮排（hanging indent）。這些要在視覺上跟內文有區隔，因為它們是詮釋性內容，看起來應該跟資料表和散文段落不一樣。
- 關係區段內的**資訊型項目符號**：標準內文縮排（180 DXA），不用懸掛縮排。
- **任何項目符號區段都不要套用左側框線強調。** 左側框線樣式在 docx-js 中渲染不一致，會產生視覺瑕疵。要區別招牌區段，改用縮排和文字大小的差異。

**表格（只用於財務資料）：**
- 標題列：表格標題底色（#D6E4F0）搭配粗體深色文字
- 內文列：白色／表格交替底色（#F2F2F2）交替
- 邊框：表格邊框顏色（#CCCCCC），細線（BorderStyle.SINGLE, size 1）
- 儲存格內距：上下 40 DXA，左右 80 DXA
- 所有數字欄靠右對齊
- 一律用 ShadingType.CLEAR（絕對不要用 SOLID，SOLID 會造成黑色背景）

**版面：**
- US Letter 直式，邊界 0.75"（四邊都是 1080 DXA）

**數字格式：**
- 幣別：USD。用百萬為單位，除非公司營收 > $50B（那就用十億，小數點一位）。單位標在欄位標題（例如 "Revenue ($M)"），不要標在個別儲存格。
- **表格儲存格：純數字加千分位逗號，不加貨幣符號。** 例如：營收儲存格顯示 "4,916"，不是 "$4,916"。單位由欄位標題負責。
- 會計年度：用實際年份（FY2022、FY2023、FY2024），絕對不要用相對標籤（FY-2、FY-1）。
- 負數：用括號，例如 (2.3%)
- 百分比：小數點一位
- 大數字：用逗號當千分位分隔

**頁尾（文件頁尾，不是行內文字）：**
把資料來源標註和免責聲明放在真正的文件頁尾（每頁重複），不要當成行內內文放在底部。頁尾剛好兩行，置中，每頁都有：
- 第 1 行："Data: S&P Capital IQ via Kensho | Analysis: AI-generated | [Month Day, Year]"
- 第 2 行："For informational purposes only. Not investment advice."
- 樣式：7pt 斜體、置中、文字顏色 #666666
- 同一家公司的所有 tear sheet 類型，這段頁尾文字都必須完全相同。不要依對象改措辭。
- **每份 tear sheet、每種對象類型、每一頁都必須有這個頁尾。** 不准省略。

## 元件函式

**你「一定要」使用這些確切的函式來建立文件元素。「不要」自己寫客製的 docx-js 樣式程式碼。** 把這些函式複製到你產生的 Node script 裡再呼叫。上面的樣式設定文字說明仍作為文件保留，這些函式才是強制執行的機制。

```javascript
const docx = require("docx");
const {
  Document, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, AlignmentType, BorderStyle, ShadingType,
  Header, Footer, PageNumber, HeadingLevel, TableLayoutType,
  convertInchesToTwip
} = docx;

// ── Color constants ──
const COLORS = {
  PRIMARY: "1F3864",
  ACCENT: "2E75B6",
  TABLE_HEADER_FILL: "D6E4F0",
  TABLE_ALT_ROW: "F2F2F2",
  TABLE_BORDER: "CCCCCC",
  HEADER_TEXT: "FFFFFF",
  FOOTER_TEXT: "666666",
};

const FONT = "Arial";

// ── 1. createHeaderBanner ──
// Returns an array of docx elements: [banner paragraph, key-value table]
function createHeaderBanner(companyName, leftFields, rightFields) {
  // leftFields / rightFields: arrays of { label: string, value: string }
  const banner = new Paragraph({
    children: [
      new TextRun({
        text: companyName,
        bold: true,
        size: 36, // 18pt
        color: COLORS.HEADER_TEXT,
        font: FONT,
      }),
    ],
    shading: { type: ShadingType.CLEAR, color: "auto", fill: COLORS.PRIMARY },
    spacing: { after: 0 },
    alignment: AlignmentType.LEFT,
  });

  function buildCellParagraphs(fields) {
    return fields.map(
      (f) =>
        new Paragraph({
          children: [
            new TextRun({ text: f.label + "  ", bold: true, size: 18, font: FONT }),
            new TextRun({ text: f.value, size: 18, font: FONT }),
          ],
          spacing: { after: 40 },
        })
    );
  }

  const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };
  const noShading = { type: ShadingType.CLEAR, color: "auto", fill: "FFFFFF" };

  const kvTable = new Table({
    rows: [
      new TableRow({
        children: [
          new TableCell({
            children: buildCellParagraphs(leftFields),
            width: { size: 50, type: WidthType.PERCENTAGE },
            borders: noBorders,
            shading: noShading,
          }),
          new TableCell({
            children: buildCellParagraphs(rightFields),
            width: { size: 50, type: WidthType.PERCENTAGE },
            borders: noBorders,
            shading: noShading,
          }),
        ],
      }),
    ],
    width: { size: 100, type: WidthType.PERCENTAGE },
  });

  return [banner, kvTable];
}

// ── 2. createSectionHeader ──
// Returns a single Paragraph with bottom border rule
function createSectionHeader(text) {
  return new Paragraph({
    children: [
      new TextRun({
        text: text,
        bold: true,
        size: 22, // 11pt
        color: COLORS.PRIMARY,
        font: FONT,
      }),
    ],
    spacing: { before: 240, after: 0 }, // 12pt before, 0pt after
    border: {
      bottom: { style: BorderStyle.SINGLE, size: 1, color: COLORS.TABLE_BORDER },
    },
  });
}

// ── 3. createTable ──
// headers: string[], rows: string[][], options: { accentHeader?, fontSize? }
function createTable(headers, rows, options = {}) {
  const fontSize = options.fontSize || 17; // 8.5pt default
  const headerFill = options.accentHeader ? COLORS.ACCENT : COLORS.TABLE_HEADER_FILL;
  const headerTextColor = options.accentHeader ? COLORS.HEADER_TEXT : "000000";

  const cellBorders = {
    top: { style: BorderStyle.SINGLE, size: 1, color: COLORS.TABLE_BORDER },
    bottom: { style: BorderStyle.SINGLE, size: 1, color: COLORS.TABLE_BORDER },
    left: { style: BorderStyle.SINGLE, size: 1, color: COLORS.TABLE_BORDER },
    right: { style: BorderStyle.SINGLE, size: 1, color: COLORS.TABLE_BORDER },
  };

  const cellMargins = { top: 40, bottom: 40, left: 80, right: 80 };

  function isNumeric(val) {
    if (typeof val !== "string") return false;
    const cleaned = val.replace(/[,$%()]/g, "").trim();
    return cleaned !== "" && !isNaN(cleaned);
  }

  // Header row
  const headerRow = new TableRow({
    children: headers.map(
      (h) =>
        new TableCell({
          children: [
            new Paragraph({
              children: [
                new TextRun({
                  text: h,
                  bold: true,
                  size: fontSize,
                  color: headerTextColor,
                  font: FONT,
                }),
              ],
            }),
          ],
          shading: { type: ShadingType.CLEAR, color: "auto", fill: headerFill },
          borders: cellBorders,
          margins: cellMargins,
        })
    ),
  });

  // Data rows with alternating shading
  const dataRows = rows.map((row, rowIdx) => {
    const fill = rowIdx % 2 === 1 ? COLORS.TABLE_ALT_ROW : "FFFFFF";
    return new TableRow({
      children: row.map((cell, colIdx) => {
        const align = colIdx > 0 && isNumeric(cell)
          ? AlignmentType.RIGHT
          : AlignmentType.LEFT;
        return new TableCell({
          children: [
            new Paragraph({
              children: [
                new TextRun({ text: cell, size: fontSize, font: FONT }),
              ],
              alignment: align,
            }),
          ],
          shading: { type: ShadingType.CLEAR, color: "auto", fill: fill },
          borders: cellBorders,
          margins: cellMargins,
        });
      }),
    });
  });

  return new Table({
    rows: [headerRow, ...dataRows],
    width: { size: 100, type: WidthType.PERCENTAGE },
  });
}

// ── 4. createBulletList ──
// items: string[], style: "synthesis" | "informational"
function createBulletList(items, style = "synthesis") {
  const indent =
    style === "synthesis"
      ? { left: 360, hanging: 180 }   // 360 DXA left, hanging indent for bullet
      : { left: 180 };                 // 180 DXA, no hanging

  return items.map(
    (item) =>
      new Paragraph({
        children: [
          new TextRun({ text: "•  ", font: FONT, size: 18 }),
          new TextRun({ text: item, font: FONT, size: 18 }),
        ],
        indent: indent,
        spacing: { after: 60 },
      })
  );
}

// ── 5. createFooter ──
// date: string (e.g., "February 23, 2026")
function createFooter(date) {
  return new Footer({
    children: [
      new Paragraph({
        children: [
          new TextRun({
            text: `Data: S&P Capital IQ via Kensho | Analysis: AI-generated | ${date}`,
            italics: true,
            size: 14, // 7pt
            color: COLORS.FOOTER_TEXT,
            font: FONT,
          }),
        ],
        alignment: AlignmentType.CENTER,
      }),
      new Paragraph({
        children: [
          new TextRun({
            text: "For informational purposes only. Not investment advice.",
            italics: true,
            size: 14,
            color: COLORS.FOOTER_TEXT,
            font: FONT,
          }),
        ],
        alignment: AlignmentType.CENTER,
      }),
    ],
  });
}
```

**在產生的 script 中的用法：**
1. 把上面所有函式和常數複製到產生的 Node.js script
2. 呼叫 `createHeaderBanner(...)`，不要手動建橫幅段落和表格
3. 每個區段標題都呼叫 `createSectionHeader(...)`，絕對不要手動設定段落框線
4. **所有**表格資料都呼叫 `createTable(...)`：財務摘要、交易可比公司、併購活動、關係表、融資歷史等等。M&A 活動表（IB/M&A 範本）要傳入 `{ accentHeader: true }`。對於非數字的表格（例如關係、持股結構），這個函式一樣能正常運作，它只會把含數字的儲存格靠右對齊。
5. 對 earnings highlights、strategic fit、integration considerations 和 conversation starters，呼叫 `createBulletList(items, "synthesis")`
6. 對關係條目，呼叫 `createBulletList(items, "informational")`
7. 把 `createFooter(date)` 傳給 Document 建構子的 `footers.default` 屬性

**這些函式杜絕了什麼：**
- 黑色背景的表格（到處強制使用 `ShadingType.CLEAR`）
- 區段標題下另外的水平線段落（強制在段落本身使用 `border.bottom`）
- 標題中有邊框的 key-value 表格（強制 `borders: none`）
- 不一致的項目符號樣式（強制只能用 `•` 字元）
- 缺少頁尾（提供確切的頁尾結構）

## 工作流程

### 步驟 1：確認輸入

進行之前先蒐集最多四項資訊：

1. **公司**：名稱或股票代號。如果只有代號，先用一次初步查詢解析出公司全名（例如使用公司資訊工具）。
2. **對象**：四種類型之一：
   - **Equity Research**：給評估投資的買方／賣方分析師
   - **IB / M&A**：給在交易情境下建立公司簡介的銀行家
   - **Corp Dev**：給評估收購標的的內部策略團隊
   - **Sales / BD**：給準備客戶會議的商務團隊
3. **可比公司**（選填）：如果使用者心中有特定的可比公司，記下來。否則這個 skill 會從 S&P Global 資料找出同業。這對 Equity Research、IB/M&A 和 Corp Dev 的 tear sheet 很重要。
4. **頁數偏好**（選填）：預設值依對象而異（見下方），但使用者可以覆寫。

如果使用者沒有指定對象，要問。

### 步驟 2：讀取對應對象的參考檔

從這個 skill 的目錄讀取對應的參考檔：

- Equity Research → `references/equity-research.md`
- IB / M&A → `references/ib-ma.md`
- Corp Dev → `references/corp-dev.md`
- Sales / BD → `references/sales-bd.md`

每個參考檔都定義了區段、查詢計畫、格式指引和預設頁數。

### 步驟 3：透過 S&P Global MCP 拉資料

**首先：** 建立中間檔案目錄：
```bash
mkdir -p /tmp/tear-sheet/
```

使用 **S&P Global** MCP 工具（也就是 Kensho LLM-ready API）。Claude 可以使用結構化工具取得財務資料、公司資訊、市場資料、共識預期、財報電話會議逐字稿、併購交易和商業關係。每個參考檔的查詢計畫會描述每個區段要取回什麼資料，把它們對應到對話中可用的適當 S&P Global 工具。

**每個查詢步驟之後，立刻把取回的資料寫進參考檔查詢計畫指定的中間檔案。** 不要延後寫入，寫到磁碟上的資料可以免受長對話中 context 退化的影響。

**查詢策略：**
每個參考檔都包含 4-6 個資料擷取步驟的查詢計畫。這些是起點，不是死板的限制。資料完整度優先於減少呼叫次數：

- **一律拉 4 個會計年度的財務資料**，即使只顯示 3 年。第四年（最早的那年）是用來計算第一個顯示年度的營收年增率。沒有它，最早那年的成長率會顯示 "N/A"，看起來像資料缺漏，而不是設計上的選擇。
- 照寫的執行查詢計畫，使用符合所需資料的任何 S&P Global 工具。
- 如果某次工具呼叫回傳不完整的結果，試試別的工具或更窄的查詢。例如，公司摘要沒有包含業務區隔細節，就直接試區隔工具。
- 如果針對性重試之後還是沒回傳某個資料點，就繼續往下，標記為 "N/A" 或 "Not disclosed"。
- 絕對不准捏造資料。工具沒回傳數字的話，不要用訓練知識來估。

**使用者指定的可比公司：** 如果使用者提供了可比公司，要明確查詢每家可比公司的財務和倍數。如果沒有提供，就用工具回傳的任何同業資料，或用競爭對手工具從公司的板塊找出同業。

**使用者提供的選用 context：** 留意使用者自然提供的額外 context。如果他們提到收購方是誰（"我們在看這家公司，要併進我們的平台"）、他們賣什麼（"我們賣資料分析給銀行"），或可能的買家是誰（"這家公司 Salesforce 或 Microsoft 可能會有興趣"），就把這些 context 融入相關的綜合區段（Strategic Fit、Conversation Starters、Deal Angle）。不要主動索取這些資訊，對方有提供才用。

**未上市公司的處理：**
CIQ 含有未上市公司資料，所以查詢方式一樣。不過預期結果會比較稀疏。為未上市公司產出時：
- 略過：股價、52 週區間、beta、股價表現、共識預期、交易可比公司
- 著重：業務概覽、關係、持股結構、能取得的任何財務資料
- 在標題顯著標註 "Private Company"

### 步驟 3b：計算衍生指標

所有資料蒐集完成、中間檔案都寫好之後，在一次專門的流程中計算所有衍生指標。這是純計算步驟，不做新的 MCP 查詢。

**把所有中間檔案讀回 context**，然後計算：

- **利潤率：** 毛利率 %、EBITDA 利潤率 %、FCF 利潤率 %、營業利潤率 %
- **成長率：** 營收年增率、各區隔營收年增率、EPS 年增率
- **效率比率：** FCF 轉換率（FCF/EBITDA）、R&D 佔營收 %、資本支出佔營收 %
- **資本結構：** 淨負債（總負債 − 現金及約當現金）、淨負債 / EBITDA
- **區隔組合：** 每個區隔營收佔合併總營收的 %（依資料完整性規則 8，用合併營收當分母）

**驗證（從算術驗證移過來）：** 在這個計算流程中，強制執行所有算術檢查：

- **利潤率計算：** 驗證 EBITDA 利潤率 = EBITDA / 營收、毛利率 = 毛利 / 營收，依此類推。如果算出來的利潤率跟原始數字對不上，就用原始組成項目重新計算的結果。
- **成長率：** 驗證年增率 = (本期 − 前期) / 前期。如果有底層數值，不要倚賴預先算好的成長率。
- **區隔合計：** 如果呈現各區隔營收，驗證各區隔加總等於總營收（在四捨五入容許範圍內）。如果對不上，就省略合計列，不要發布不一致的算術。
- **百分比欄位：** 驗證「佔總額 %」欄位加總約 100%。
- **估值交叉檢查：** 如果同時顯示 EV 和 EV/Revenue，驗證 EV / 營收 ≈ 所述的倍數。

如果驗證失敗：嘗試用原始資料重新計算。仍不一致的話，就把該指標標為 "N/A"，不要發布不正確的數字。tear sheet 裡悄悄藏著的算術錯誤會毀掉可信度。

**把結果寫到** `/tmp/tear-sheet/calculations.csv`，欄位為：`metric,value,formula,components`

範例列：
```
metric,value,formula,components
gross_margin_fy2024,72.4%,gross_profit/revenue,"9524/13159"
revenue_growth_fy2024,12.3%,(current-prior)/prior,"13159/11716"
net_debt_fy2024,2150,total_debt-cash,"4200-2050"
```

### 步驟 3c：驗證資料檔

產生文件之前，驗證所有中間檔案都存在且有內容。

**用個別的讀取操作讀取每個中間檔案**，並印出驗證摘要：

```
=== Tear Sheet Data Verification ===
company-profile.txt: ✓ (12 fields)
financials.csv:      ✓ (36 rows)
segments.csv:        ✓ (8 rows)
valuation.csv:       ✓ (5 rows)
calculations.csv:    ✓ (18 rows)
earnings.txt:        ✓ (populated)
relationships.txt:   ⚠ MISSING
peer-comps.csv:      ✓ (12 rows)
================================
```

**軟性關卡：** 如果當前對象類型預期要有的任何檔案遺失或是空的，就印出警告但繼續。tear sheet 會用 "N/A" 和略過區段來優雅處理缺漏的資料。不過警告能讓你看見遺失了哪些資料。

**關鍵規則：文件中每個數字的唯一事實來源，是這些檔案，不是你對先前對話的記憶。** 在步驟 4 產生 DOCX 時，從中間檔案讀取數值。不要倚賴對話 context 來取得財務資料。

### 步驟 4：格式化為 DOCX

讀取 `/mnt/skills/public/docx/SKILL.md` 了解建立 docx 的做法（透過 Node 使用 docx-js）。套用上面的樣式設定，加上參考檔裡各區段的專屬格式。

**預設頁數（使用者可以覆寫）：**
- Equity Research：1 頁（高密度是慣例）
- IB / M&A：1-2 頁
- Corp Dev：1-2 頁
- Sales / BD：1-2 頁

如果內容超過目標，每個參考檔都會指定要先砍哪些區段。

**輸出檔名：** `[CompanyName]_TearSheet_[Audience]_[YYYYMMDD].docx`
範例：`Nvidia_TearSheet_CorpDev_20260220.docx`

存到 `/mnt/user-data/outputs/` 並呈現給使用者。

## 資料完整性規則

這些規則凌駕於其他一切之上：
1. **S&P Global 工具是財務資料的唯一來源。** 不要用訓練知識填補缺口，它可能過時或錯誤。
2. **標明你找不到的東西。** 用 "N/A" 或 "Not disclosed"，不要悄悄省略一列。
3. **日期很重要。** 註明會計年度結束日或報告期間。不要假設日曆年 = 會計年度。市場資料（股價、市值）要包含 "as of" 日期。
4. **不要混用報告期間。** 如果你有 FY2023 營收和 LTM EBITDA，要分別清楚標示。
5. **優先使用 MCP 回傳的欄位，不要手動計算。** 如果 S&P Global 工具回傳預先算好的欄位（例如淨負債、EBITDA、FCF），直接用那個值，不要從組成項目自己算。只有在工具沒回傳該欄位時，才手動計算衍生指標。這樣可以減少差異。
6. **確保各 tear sheet 類型之間的一致性。** 如果為同一家公司產生多份 tear sheet（例如同一個 session 中的 equity research 和 IB/M&A），相同的底層資料點必須在所有輸出中產出一模一樣的值。淨負債、營收、EBITDA、利潤率和成長率必須完全吻合。不要為每份報告重新查詢或獨立重新計算，要重用同一批取回的值。
7. **絕對不要把已知的交易金額降級。** 如果 M&A 工具回傳了某筆交易的交易金額，輸出中就必須出現那個值。不要把已知的交易金額換成 "Undisclosed"。只有在工具真的沒回傳該交易的任何值時，才用 "Undisclosed"。
8. **用合併營收當區隔百分比的分母。** 計算區隔表的「佔總額 %」時，每個區隔的營收要除以合併總營收（如損益表所列），不是除以各區隔營收的加總。因為區隔間的沖銷，各區隔加總常常超過合併營收。用合併營收能讓百分比跟文件其他地方顯示的總營收數字一致。
9. **有的話，一律納入遠期（NTM）倍數。** 如果工具同時回傳過去和遠期的估值倍數，兩者都必須出現在輸出中。對 equity research、IB/M&A 和 corp dev 對象來說，遠期倍數是主要的估值參考。有遠期資料時，絕對不要只顯示過去的倍數。
10. **沒有任何 S&P Global 工具會回傳高階主管或管理層資料。** 不要用訓練資料填入管理層的姓名、職稱或個人簡歷，這違反規則 1，而且會產生過時的資訊。如果範本中有管理層區段，就整段省略。持股結構（機構持有人、內部人持股 %、PE 贊助者）只有在工具有回傳時才能納入，並以 "data permitting" 為前提。

## 中間檔案規則

所有從 MCP 工具取得的資料，在產生文件之前，都必須儲存到結構化的中間檔案。這些檔案，而不是對話 context，才是文件中每個數字的唯一事實來源。

**設定：** 在步驟 3 開始時，建立工作目錄：
```
mkdir -p /tmp/tear-sheet/
```

**查詢後立刻寫入的規定：** 每個 MCP 查詢步驟完成後，立刻把取回的資料寫進適當的中間檔案。不要等到所有查詢都結束。每個參考檔的查詢計畫會指定每個步驟後要寫哪些檔案。

**檔案 schema：**

| 檔案 | 格式 | 欄位／結構 | 使用者 |
|---|---|---|---|
| `/tmp/tear-sheet/company-profile.txt` | Key-value 文字 | name, ticker, exchange, HQ, sector, industry, founded, employees, market_cap, enterprise_value, stock_price, 52wk_high, 52wk_low, shares_outstanding, beta, ownership | 全部 |
| `/tmp/tear-sheet/financials.csv` | CSV | `period,line_item,value,source` | 全部 |
| `/tmp/tear-sheet/segments.csv` | CSV | `period,segment_name,revenue,source` | ER, IB, CD |
| `/tmp/tear-sheet/valuation.csv` | CSV | `metric,trailing,forward,source` | ER, IB, CD |
| `/tmp/tear-sheet/consensus.csv` | CSV | `metric,fy_year,value,source` | ER |
| `/tmp/tear-sheet/earnings.txt` | 結構化文字 | Quarter, date, key quotes, guidance, key drivers | ER, IB, Sales |
| `/tmp/tear-sheet/relationships.txt` | 結構化文字 | Customers, suppliers, partners, competitors，各附說明 | IB, CD, Sales |
| `/tmp/tear-sheet/peer-comps.csv` | CSV | `ticker,metric,value,source` | ER, IB, CD |
| `/tmp/tear-sheet/ma-activity.csv` | CSV | `date,target,deal_value,type,rationale,source` | IB, CD |
| `/tmp/tear-sheet/calculations.csv` | CSV | `metric,value,formula,components` | 全部（在步驟 3b 寫入） |

**縮寫：** ER = Equity Research，IB = IB/M&A，CD = Corp Dev，Sales = Sales/BD。

並非每種對象類型都會用到每個檔案，參考檔會定義哪些查詢步驟適用。與當前對象類型無關的檔案不需要建立。

**只存原始值。** 中間檔案存的是工具回傳的原始值。不要在這些檔案裡預先計算利潤率、成長率或其他衍生指標，那是步驟 3b 的事。

**頁數預算的強制執行：** 每個參考檔都指定預設頁數和編號的刪減順序。如果渲染出來的文件超過目標，就依指定的順序刪減，不要嘗試把字體大小或邊界縮到範本的最小值以下。刪減順序是嚴格的優先順序堆疊：先把區段 1 整個砍完，才能動區段 2。

## 內容品質規則

11. **針對對象重寫每個敘述區段。** CIQ 的公司摘要是輸入，不是輸出。每種對象類型需要不同的描述：equity research 要簡潔、以論點為導向，IB 要 pitchbook 風格的行文，Corp Dev 要以產品為重點，Sales/BD 要用白話。絕對不要把 CIQ 摘要原封不動貼進任何 tear sheet。
12. **依對象區分 earnings highlights。** 同一場財報電話會議，對不同讀者會有不同的重點。Equity research 要區隔層級的表現和共識預期的超出／不及。IB 要利潤率軌跡和策略性評論。Sales/BD 要能創造對話切入點的策略主題。不要在不同的 tear sheet 類型之間重複使用同樣的項目符號。
13. **綜合區段才是差異化所在。** Strategic Fit Analysis、Integration Considerations、Conversation Starters 和 Business Overview 段落，是 tear sheet 體現價值的地方。這些區段需要分析推理，把資料點串成一段敘事，只列出公司名稱而沒有脈絡，不算綜合。
14. **在區隔表中標記待完成的出售。** 如果公司已宣布要出售某個區隔或事業單位，在區隔表加註腳或括號說明這筆待完成的交易（例如 "Mobility* — *Pending divestiture, expected mid-2026"）。對 Corp Dev 和 IB/M&A 的 tear sheet，在區隔表下方加一行註記，顯示排除被出售區隔後的 pro-forma 營收和營收組合。這能幫助讀者評估「往後」的事業，不必自己算。

### 算術驗證

**→ 算術驗證現在改在步驟 3b（計算衍生指標）強制執行。** 所有利潤率計算、成長率、區隔合計、百分比欄位和估值交叉檢查，都在文件產生開始之前的專門計算流程中驗證。完整的驗證清單見步驟 3b。
