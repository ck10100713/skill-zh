---
name: fsi-strip-profile
description: |
  為 pitch book、交易文件和客戶簡報製作專業的投資銀行 strip profile（公司簡介）。產生 1-4 張資訊密度高的投影片，包含四象限版面、圖表和表格。
---

## 工作流程

### 1. 釐清需求
- **問使用者**：單張還是多張投影片（3-4 張）？
- **問使用者**：有沒有特定想強調的重點領域或主題？
- **使用者確認之後**才開始研究

### 2. 研究與規劃
**資料來源：**
- **主要**：公司申報文件（BamSEC、SEC EDGAR - "Item 1. Business"、MD&A）、投資人簡報、公司官網
- **市場資料**：Bloomberg、FactSet、CapIQ（股價、股數、市值、淨負債、EV、持股結構）
- **預估**：FactSet/CapIQ 對 NTM 營收、EBITDA、EPS 的共識預期
- **新聞**：近 90 天的新聞稿、併購活動、財測調整

**必要指標：**
- **財務**：前後 ±3 年的營收、EBITDA、利潤率（%）、EPS、FCF
- **估值**：市值、EV、EV/Revenue、EV/EBITDA、P/E 倍數
- **成長**：年增率（%）
- **持股結構**：前 5 大股東及持股 %
- **業務區隔**：產品組合和／或地區組合（% 拆分）

**標準化：**
- 所有金額轉成一致的幣別
- 單位統一（全部用 $mm 或全部用 $bn，不要混用）

**動手建立之前：**
- 把大綱印在對話裡，每個項目 4-5 個重點（用實際數字，不要佔位符）
- 把風格選擇印出來：字型、顏色（hex 色碼）、每組資料使用的圖表類型
- 取得使用者的認同："這份大綱和視覺策略符合你的想法嗎？"

### 3. 逐張建立投影片
**關鍵：你「一定要」一次只建立「一張」投影片，並取得使用者核准之後才能做下一張。**

**每一張投影片：**
1. 用 PptxGenJS「只」建立這一張
2. **強制：轉成圖片審閱**：你「一定要」把投影片轉成圖片，才能用眼睛檢查：
   ```bash
   soffice --headless --convert-to pdf presentation.pptx
   pdftoppm -jpeg -r 150 -f 1 -l 1 presentation.pdf slide
   ```
3. **強制目視審閱**：繼續之前，你「一定要」仔細檢查渲染出來的投影片圖片：
   - **文字重疊檢查**：掃過每個文字元素，有沒有標籤、項目符號或標題互相碰撞？
   - **文字截斷檢查**：有沒有文字在邊界被截掉？每個字都完整看得到嗎？
   - **圖表邊界檢查**：圖表有沒有留在容器內？「所有」座標軸標籤都完整可見嗎？
   - **象限完整性**：某個象限的內容有沒有溢到相鄰象限？
4. **如果偵測到「任何」重疊或截斷**：立刻照下面的順序處理：
   - **先**：縮小字體（降 1-2pt）
   - **再**：縮短文字（縮寫、拿掉次要資訊）
   - **最後**：調整元素位置或容器大小
   - **重新渲染再驗證一次**，所有文字都乾淨地放得下之前不准繼續
5. 把投影片圖片連同下載連結給使用者看
6. **停下來，等使用者明確核准**才建立下一張投影片。使用者確認之前「絕對不准」繼續。

**每一頁你「一定要」檢查這些具體問題：**
- 表格列撞到下方的文字
- 圖表 x 軸標籤在底部被截掉
- 太長的項目符號換行後擠進相鄰內容
- 象限內容溢到相鄰象限
- 標題文字跟下方內容重疊
- 圖例文字跟圖表元素重疊
- 頁尾／來源文字撞到主要內容

---

## 投影片格式要求

### 資訊密度是關鍵

**第一目標是「最大」的資訊密度。** 忙碌的主管要在 30 秒內看懂整家公司的故事。每個象限都要塞滿。

**每個象限的目標：**
- **公司概覽**：至少 6-8 個重點（總部、成立時間、員工數、CEO/CFO、市值、股票代號、產業、一個關鍵數字）
- **業務與定位**：6-8 個重點（營收驅動因素、產品、市占率 %、競爭護城河、客戶數、地區組合）
- **關鍵財務**：8-10 列的表格，或圖表加 4-5 個關鍵指標（營收、EBITDA、利潤率、EPS、FCF、成長率、估值倍數）
- **第四象限**：5-7 個重點（持股 %、近期併購、近況、催化劑）

**塞資訊的技巧：**
- 合併相關事實："HQ: Austin, TX; Founded: 2003; 140K employees"
- 一定要有數字："$50B revenue" 而不是 "large revenue"
- 加上脈絡："EBITDA margin: 25% (vs. 18% industry avg)"
- 加入年增變化："Revenue: $125M (+28% YoY)"
- 用百分比："Enterprise: 62% of revenue"

**如果某個象限看起來太空，就補：**
- 附 % 的業務區隔拆分
- 地區營收拆分
- 客戶集中度（前 10 大 = X%）
- 附金額的近期合約得標
- 財測 vs. 共識預期
- 內部人持股 %

**行距：每個區段用單一 textbox：**
```python
def add_section(slide, x, y, w, header_text, bullets, header_size=10, bullet_size=8):
    """Header + bullets in single textbox with natural spacing"""
    tb = slide.shapes.add_textbox(x, y, w, Inches(len(bullets) * 0.18 + 0.3))
    tf = tb.text_frame
    tf.word_wrap = True

    # Header paragraph
    p = tf.paragraphs[0]
    p.text = header_text
    p.font.bold = True
    p.font.size = Pt(header_size)
    p.font.color.rgb = RGBColor(0, 51, 102)
    p.space_after = Pt(6)  # Small gap after header

    # Bullet paragraphs
    for bullet in bullets:
        p = tf.add_paragraph()
        p.text = bullet
        p.font.size = Pt(bullet_size)
        p.space_after = Pt(3)
    return tb
```

**關鍵的間距原則：**
- 標題和項目符號放在「同一個」textbox（不要另外放一個標題 textbox）
- 標題後用 `space_after = Pt(6)`，項目符號之間用 `Pt(3)`
- 不要寫死間距，讓段落間距自然處理
- 內容溢出時，縮小 1pt 字體，不要刪內容

---

- **3-4 張高密度投影片**：用象限、欄位、表格、圖表
- **所有內文都用項目符號**：絕對不要寫成段落。**每個區段用一個 textbox，所有項目符號都放在裡面**，不要為每個項目符號各建一個 textbox。使用 PptxGenJS 的項目符號格式：
  ```javascript
  // CORRECT: Single textbox with bullet list - each array item becomes a bullet
  // Position in top-left quadrant (Company Overview) - after header with accent bar
  slide.addText(
    [
      { text: 'Headquarters: Austin, Texas; Founded 2003', options: { bullet: { indent: 10 }, breakLine: true } },
      { text: 'Employees: 140,000+ globally across 6 continents', options: { bullet: { indent: 10 }, breakLine: true } },
      { text: 'CEO: Elon Musk; CFO: Vaibhav Taneja', options: { bullet: { indent: 10 }, breakLine: true } },
      { text: 'Market Cap: $850B (#6 globally by market cap)', options: { bullet: { indent: 10 }, breakLine: true } },
      { text: 'Segments: Automotive (85%), Energy (10%), Services (5%)', options: { bullet: { indent: 10 } } }
    ],
    { x: 0.45, y: 0.95, w: 4.5, h: 2.6, fontSize: 11, fontFace: 'Arial', valign: 'top', paraSpaceAfter: 6 }
  );

  // WRONG: Multiple separate textboxes for each bullet - causes alignment issues
  // slide.addText('Headquarters: Austin', { x: 0.5, y: 1.0, bullet: true });
  ```

  **項目符號格式小技巧：**
  - `bullet: { indent: 10 }`：控制項目符號縮排（越小越緊）
  - `paraSpaceAfter: 6`：每段後的間距（單位 pt）
  - 每個項目符號塞進多個相關事實（例如 "HQ: Austin; Founded: 2003"）
  - 放進具體的數字和百分比來提高資訊密度
- 標題用 **Title case**（不要全大寫），靠左對齊
- **所有地方字型一致**，包括表格
- **公司的品牌色**：建立投影片之前，你「一定要」用網路搜尋查出實際的品牌色。不要用猜的或自己假設。
- **有提供品牌指南就照做**

### 視覺參考
版面配置的靈感請看 `examples/Nike_Strip_Profile_Example.pptx`。顏色要依各公司的品牌調整。

---

## 第一頁版面

必須通過忙碌主管的「30 秒理解測試」。

### 投影片設定（關鍵）
**使用 4:3 長寬比**（標準的投行 pitch book 格式）：
```javascript
const pptx = new pptxgen();
pptx.layout = 'LAYOUT_4x3';  // 10" wide × 7.5" tall - MUST USE THIS
```

### 投影片座標系統
PptxGenJS 用英吋。4:3 投影片 = **寬 10" × 高 7.5"**。
- **x**：從左邊緣算起的水平位置（0 = 最左，10 = 最右）
- **y**：從上邊緣算起的垂直位置（0 = 最上，7.5 = 最下）
- **內容必須留在邊界內**：四邊都留 0.3" 邊距

### 第一頁的位置配置（單位：英吋）
```
┌─────────────────────────────────────────────────────────────────┐
│ y=0.2  Title: Company Name (Ticker)                             │
├────────────────────────────┬────────────────────────────────────┤
│ y=0.6  Company Overview    │ y=0.6  Business & Positioning      │
│ x=0.3, w=4.7               │ x=5.0, w=4.7                       │
│ h=3.0                      │ h=3.0                              │
├────────────────────────────┼────────────────────────────────────┤
│ y=3.7  Key Financials      │ y=3.7  Stock/Recent Developments   │
│ x=0.3, w=4.7               │ x=5.0, w=4.7                       │
│ h=3.5                      │ h=3.5                              │
└────────────────────────────┴────────────────────────────────────┘
                                                            y=7.5
```

### 標題區（y=0.2）
**公司名稱（股票代號）**，例如：`Tesla, Inc. (TSLA)`
```javascript
slide.addText('Tesla, Inc. (TSLA)', { x: 0.3, y: 0.2, w: 9.4, h: 0.35, fontSize: 18, bold: true });
```

### 四象限版面（y=0.6 到 y=7.2）

| 象限 | 位置 | 內容 |
|----------|----------|---------|
| **1** | x=0.3, y=0.6, w=4.7, h=3.0 | **公司概覽**：總部、成立時間、關鍵數字、業務摘要（4-5 個重點） |
| **2** | x=5.0, y=0.6, w=4.7, h=3.0 | **業務與定位**：營收驅動因素、產品／服務、競爭地位、成長驅動因素（4-5 個重點） |
| **3** | x=0.3, y=3.7, w=4.7, h=3.5 | **關鍵財務**：營收、EBITDA、利潤率、EPS、FCF + 估值（市值、EV、倍數）：**表格或圖表擇一，不要兩個都放** |
| **4** | x=5.0, y=3.7, w=4.7, h=3.5 | **上市公司**：1 年股價走勢圖 + 主要股東。**未上市公司**：近況或持股結構／併購歷史 |

### 字體大小：就用這些確切的值
| 元素 | 大小 | 備註 |
|---------|------|-------|
| 投影片標題 | 24pt | 粗體，用公司品牌色 |
| 象限標題 | 14pt | 粗體，附強調色條 |
| 內文／項目符號文字 | 11pt | 一般粗細 |
| 表格文字 | 10pt | 密集的表格用 9pt |
| 圖表標籤 | 9pt | 標籤要短 |
| 來源／頁尾 | 8pt | 放在投影片底部 |

**關鍵：如果文字溢出，把字體縮小 1pt 再重新渲染。**

### 視覺強調（必要）
每個象限標題的左邊「一定要」有一條彩色強調色條：
```javascript
// Add accent bar for quadrant header
slide.addShape(pptx.shapes.RECTANGLE, {
  x: 0.3, y: 0.6, w: 0.08, h: 0.25,
  fill: { color: 'E31937' }  // Use company brand color
});
slide.addText('Company Overview', {
  x: 0.45, y: 0.6, w: 4.5, h: 0.3, fontSize: 14, bold: true, fontFace: 'Arial'
});
```

**要放進去的視覺元素：**
- 所有區段標題旁的強調色條（品牌色）
- 上下象限之間的細水平分隔線
- 有的話，右上角放公司 logo
- 表格內淡淡的格線（淺灰 #CCCCCC）

### 第一頁格式
- **字型：Arial**（或依使用者／品牌指南指定）
- **象限標題**：Title Case（不要全大寫），例如 "Company Overview" 而不是 "COMPANY OVERVIEW"
- **項目符號**：開頭的關鍵詞要粗體，例如 "**Market Position:** Leading global manufacturer..."
- 只能用白色背景，不要框、填色或底紋
- 區段標題：粗體文字，樣式依品牌指南
- 所有象限大小相同、互相對齊

---

## 後續頁面：自由版面

- 雙欄（40/60 或 50/50）、整頁圖表，或側欄版面
- 每一頁都是對第一頁內容的延伸說明
- 維持一致的字體排印和配色
- 建議的順序：產品／市場 → 財務分析 → 領導團隊

---

## 圖表（多張投影片的簡介）

**多張投影片的簡介**：放入 2-3 個真正的 PptxGenJS 圖表。絕對不要用佔位用的 div 或靜態圖片。

**單張投影片的簡介**：財務資料用表格（更省空間）。只有在圖表取代表格時才加圖表，不要兩個都放。

| 資料類型 | 圖表類型 |
|-----------|------------|
| 營收趨勢 | 折線或直條（多年度） |
| 地區拆分 | 水平長條 |
| 產品組合 | 附百分比的圓餅圖 |
| 財務比較 | 直條 |
| 股價（1 年日資料） | 折線 |

### 圖表程式碼範例

**水平長條圖（4:3 投影片中放得進右下象限）：**
```javascript
slide.addChart(pptx.charts.BAR, [{
  name: 'FY2024 Revenue by Region',
  labels: ['North America', 'EMEA', 'China', 'APLA'],
  values: [21.4, 13.6, 7.6, 6.7]
}], {
  x: 5.0, y: 4.1, w: 4.5, h: 3.0,  // Fits in bottom-right quadrant (4:3)
  barDir: 'bar', chartColors: ['FF6B35'], showValue: true,
  dataLabelFontSize: 10, catAxisLabelFontSize: 10, valAxisLabelFontSize: 10,
  dataLabelFormatCode: '$#,##0.0B',
  title: 'Revenue by Geography', titleFontSize: 12, titleBold: true
});
```

**圓餅圖（4:3 投影片中放得進右下象限）：**
```javascript
slide.addChart(pptx.charts.PIE, [{
  name: 'Product Mix',
  labels: ['Footwear', 'Apparel', 'Equipment'],
  values: [68, 29, 3]
}], {
  x: 5.0, y: 4.1, w: 4.5, h: 3.0,  // Fits in bottom-right quadrant (4:3)
  showPercent: true, showLegend: true, legendPos: 'r',
  dataLabelFontSize: 10, legendFontSize: 10,
  chartColors: ['FF6B35', '2C2C2C', '4A4A4A'],
  title: 'Revenue Mix FY24', titleFontSize: 12, titleBold: true
});
```

**折線圖（後續投影片用的滿版寬度）：**
```javascript
slide.addChart(pptx.charts.LINE, [{
  name: 'Revenue ($B)',
  labels: ['FY21', 'FY22', 'FY23', 'FY24', 'FY25E'],
  values: [44.5, 46.7, 48.5, 51.4, 54.2]
}], {
  x: 0.3, y: 1.2, w: 9.4, h: 5.5,  // Full width for 4:3 slide
  chartColors: ['FF6B35'], showValue: true, lineSmooth: true,
  dataLabelFontSize: 11, catAxisLabelFontSize: 11, valAxisLabelFontSize: 11,
  title: 'Revenue Trend & Forecast', titleFontSize: 14, titleBold: true
});
```

---

## 財務資料格式

**一律使用原生的 PptxGenJS 表格或圖表，絕對不要用純文字敘述或 HTML 表格。**

財務資料用 `slide.addTable()`（4:3 投影片中放得進左下象限）：
```javascript
// Add header with accent bar first
slide.addShape(pptx.shapes.RECTANGLE, {
  x: 0.3, y: 3.7, w: 0.08, h: 0.25, fill: { color: 'E31937' }
});
slide.addText('Key Financials & Valuation', {
  x: 0.45, y: 3.7, w: 4.5, h: 0.3, fontSize: 14, bold: true, fontFace: 'Arial'
});

// Financial data table
slide.addTable([
  [{ text: 'Metric', options: { bold: true, fill: '003366', color: 'FFFFFF' } },
   { text: 'FY24', options: { bold: true, fill: '003366', color: 'FFFFFF' } },
   { text: 'FY25E', options: { bold: true, fill: '003366', color: 'FFFFFF' } }],
  ['Revenue', '$51.4B', '$54.2B'],
  ['YoY Growth', '+6.0%', '+5.5%'],
  ['EBITDA', '$8.9B', '$9.5B'],
  ['EBITDA Margin', '17.3%', '17.5%'],
  ['EPS', '$3.42', '$3.75'],
  ['Market Cap', '$185B', '—'],
  ['EV/EBITDA', '12.5x', '11.7x']
], {
  x: 0.45, y: 4.1, w: 4.3, h: 3.0,  // Below header in bottom-left quadrant
  fontFace: 'Arial', fontSize: 10,
  border: { pt: 0.5, color: 'CCCCCC' },
  valign: 'middle',
  colW: [1.8, 1.25, 1.25]  // Column widths
});
```

❌ **錯誤示範：** 像 `Note: FY2024 revenue growth +1.0%, Net Income $5.1B...` 這種純文字
❌ **錯誤示範：** 無法正確轉成 PowerPoint 的 HTML 表格

做預測時，用結構化表格呈現 Bear/Base/Bull 三種情境。

---

## 品質檢查清單

### 第一頁
- [ ] 標題區有公司名稱、股票代號、產業
- [ ] 標題下方剛好是 4 個大小相同的象限
- [ ] 全部是項目符號，沒有段落，每個最多 1 行
- [ ] 財務用表格或圖表（不要兩個都放）

### 所有投影片
- [ ] 沒有文字溢出或被截斷
- [ ] 字型和顏色全程一致
- [ ] 圖表渲染正確
- [ ] 沒有佔位文字，全部是實際資料
- [ ] 單位一致（$mm 或 $bn，不要混用）
- [ ] 有標註來源
- [ ] 投資銀行等級的品質（GS/MS/JPM 標準）

**注意：** 建立 PowerPoint 檔案時，參考 **PPTX skill**。
