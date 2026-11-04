---
name: funding-digest
description: "產生一張精緻的單頁 PowerPoint 投影片，彙整使用者所關注的產業或公司近期募資輪次和重要資本市場活動的重點。當使用者要求交易動態摘要、每週回顧、募資摘要、交易彙整或資本市場簡報時使用這個 skill。觸發詞包括：'deal flow digest'、'weekly funding recap'、'deal roundup'、'transaction summary this week'、'what happened in [sector] this week'、'capital markets update'，或任何要把近期募資活動整理成簡報投影片的請求。產出專業的單頁 PPTX，含關鍵重點、估值資料和 Capital IQ 交易連結。"
---

**AI 免責聲明（必要）：**
你「必須」把下列免責聲明文字放進 PowerPoint 的頁尾。這不是選用的，沒有它報告就不算完整：

> **"Analysis is AI-generated — please confirm all outputs"**

**頁尾**：在產生的投影片底部，用醒目的黃色橫幅放上："Analysis is AI-generated — please confirm all outputs"

---

# 每週 Deal Flow 摘要

使用 S&P Global Capital IQ 資料，產出分析師等級的**單頁 PowerPoint**，彙整所關注的產業或公司近期募資輪次的關鍵重點。每筆交易都連回它的 Capital IQ 檔案頁面，方便快速深入查看。

## 何時使用

出現下列任一模式時觸發：
- "Give me a deal flow digest for this week"
- "Weekly funding recap for [sector]"
- "What deals closed in [sector/companies] recently?"
- "Transaction roundup" 或 "deal roundup"
- "Capital markets update for my coverage universe"
- "Summarize recent funding activity"
- 任何關於交易、募資或輪次的定期簡報請求

## 巢狀 Skill

這個 skill 產出單頁 PPTX 簡報：
- 產生 PowerPoint 之前，**先讀** `/mnt/skills/public/pptx/SKILL.md`（以及它的子參考檔 `pptxgenjs.md`，用於從頭建立）

## 實體解析與工具穩健性

S&P Global 的識別碼系統會把公司名稱解析成法律實體。多數公司都運作良好，但有已知的失敗模式，會造成空結果。**整個工作流程都要套用這些規則，避免資料悄悄遺失。**

### 規則 0：查詢募資之前，先預先驗證所有識別碼

呼叫任何募資工具**之前**，先把每個識別碼都跑過 `get_info_from_identifiers`。這是及早抓到問題最便宜、最可靠的方式。檢查回應中的兩件事：

1. **它到底有沒有解析成功？** 如果識別碼回傳空值／錯誤，代表這個名稱不存在於 S&P Global。試試 `references/sector-seeds.md` 裡的別名、法律實體名稱，或直接用 `company_id`。
2. **`status` 欄位是什麼？**
   - `"Operating"` → 可以安全地查詢募資輪次。
   - `"Operating Subsidiary"` → 這間公司存在，但由母公司持有。它會回傳**零筆募資輪次**。在摘要中註明這點作為背景（例如「被 [Parent] 收購」），但不要查詢募資。
   - 任何其他狀態（例如已關閉、不活躍）→ 公司已不再營運。可能有歷史資料，但沒有新活動。

**光是這個預先驗證的步驟，就能避免大部分的空結果問題。** 把所有候選名單集中成一次 `get_info_from_identifiers` 呼叫（它處理大批量很順），先分流再繼續。

### 規則 1：沒有備案就不要相信空結果

如果 `get_rounds_of_funding_from_identifiers` 對一間你預期有資料的公司回傳空值：
1. **試試法律實體名稱或 company_id。** 品牌名稱通常行得通，但有些不行。已知不吻合的情況請見 `references/sector-seeds.md` 裡的別名表。常見模式："[Brand] AI" → "[Legal Name], Inc."（例如 Together AI → "Together Computer, Inc."、Character.ai → "Character Technologies, Inc."、Runway ML → "Runway AI, Inc."）。
2. **驗證這間公司存在於 S&P。** 如果你跳過了規則 0，現在就呼叫 `get_info_from_identifiers(identifiers=["Company"])`，如果這也回傳空值，這間公司可能太早期，或尚未被收錄。

### 規則 2：子公司沒有募資輪次

屬於較大公司的部門或全資子公司（例如 Alphabet 旗下的 DeepMind、Microsoft 旗下的 GitHub、Voodoo 旗下的 BeReal）會回傳**零筆募資輪次**。它們的資本事件是在母公司層級追蹤的。

**如何偵測：** `get_info_from_identifiers` 回傳的 `status` 欄位會顯示 `"Operating Subsidiary"`。`references/sector-seeds.md` 檔案也用 ⚠️ 警告標出已知的子公司。募資查詢要跳過這些。

### 規則 3：用 `get_rounds_of_funding_from_identifiers` 當主要工具，不要用 `get_funding_summary_from_identifiers`

Summary 工具比較快但不太可靠，即使有詳細的輪次資料，它也可能回傳錯誤或不完整的資料。一律以詳細輪次工具作為主要資料來源。Summary 工具只適合用於快速的彙總檢查（總募資額、輪次數量），如果結果看起來偏低，要用輪次工具來驗證。

### 規則 4：小心分批並驗證

處理大型公司範圍（50 間以上）時，以 15 到 20 間為一組分批。每一批之後，檢查回傳空結果的公司，並在繼續之前，先把它們走過規則 1 的備案步驟。

### 規則 5：`role` 參數很關鍵

- `company_raising_funds` → 「X 募了哪些輪次？」（公司的視角）
- `company_investing_in_round_of_funding` → 「投資人 Y 投資了什麼？」（投資人的視角）

用錯 role 會悄悄回傳空結果。對 deal flow 摘要來說，你幾乎一定要用 `company_raising_funds`。只有在特別分析投資人的投資組合活動時，才用投資人的 role。

### 規則 6：識別碼解析不分大小寫，但對拼字敏感

S&P Global 能處理大小寫差異（"openai" = "OpenAI"），但對拼字和標點很嚴格。"Character AI" 可能失敗，而 "Character.ai" 會成功。有疑慮時，用 `company_id`（例如 `C_1829047235`），保證能解析。

## 工作流程

### 步驟 1：確立覆蓋範圍與期間

決定摘要要涵蓋什麼。有兩種情況：

**回訪使用者（有觀察清單）：**
如果使用者之前定義過要追蹤的產業或公司，就用那份清單。檢查對話歷史中有沒有先前的觀察清單。

**新使用者：**
詢問：

| 參數 | 預設值 | 備註 |
|-----------|---------|-------|
| **產業** | *（至少一個）* | 例如 "AI, Fintech, Biotech" |
| **特定公司** | 選用 | 補充產業層級的覆蓋 |
| **時間區間** | 最近 7 天 | "this week"、"last 2 weeks"、"this month" |

從時間區間計算出確切的 `start_date` 和 `end_date`。

### 步驟 2：建立公司範圍

對指定的每個產業，用經過驗證的自助擴展方式建立公司範圍：

1. **種子公司**，來自領域知識（見 `references/sector-seeds.md`）
   - 注意 seeds 檔案裡的 ⚠️ 警告和別名註記：有些知名公司是子公司、已被收購、或需要特定的法律名稱才能解析。
   - Seeds 檔案包含已知別名不吻合的 `company_id` 值。品牌名稱失敗時直接用這些。

2. **立刻預先驗證所有種子**（規則 0）：
   ```
   get_info_from_identifiers(identifiers=[all_seeds_for_this_sector])
   ```
   把結果分流成兩個桶子：
   - ✅ **已解析且營運中**（`status` = "Operating"）→ 繼續做競爭對手擴展
   - ❌ **未解析或為子公司** → 用 seeds 檔案的別名／法律名稱重試；子公司記下作為背景，但排除在募資查詢之外

3. **透過競爭對手擴展**（只用 ✅ 已解析的種子）：
   ```
   get_competitors_from_identifiers(identifiers=[resolved_seeds], competitor_source="all")
   ```

4. **驗證擴展後的範圍：**
   ```
   get_info_from_identifiers(identifiers=[new_competitors])
   ```
   套用同樣的分流。依 `simple_industry` 符合目標產業來篩選。丟掉任何未解析的名稱或子公司。

如果使用者提供特定公司，直接加進去，但仍要走過預先驗證的分流。絕對不要跳過驗證，即使是知名品牌名稱，也可能悄悄失敗。

範圍要保持可管理，每個產業目標是 15 到 40 間**已解析、營運中**的公司。多產業的摘要，總數可能達 50 到 100 間以上。

### 步驟 3：取得募資輪次

對範圍內所有公司：

```
get_rounds_of_funding_from_identifiers(
    identifiers=[batch],
    role="company_raising_funds",
    start_date="YYYY-MM-DD",
    end_date="YYYY-MM-DD"
)
```

如果範圍很大，以 15 到 20 間為一批處理。

**每一批之後，找出回傳空結果的公司。** 對任何預期有活動的公司：
1. 用法律實體名稱或其他識別碼重試（見上面的實體解析規則）。
2. 只有在用盡備案之後，才把這間公司記錄為「無資料」。

從成功的結果收集所有 `transaction_id` 值，再用詳細輪次資訊補充：

```
get_rounds_of_funding_info_from_transaction_ids(
    transaction_ids=[all_funding_ids]
)
```

把所有交易 ID 放進單一呼叫（或少數幾次呼叫），不要一筆交易一次，這個工具處理批量很有效率。

**從每個輪次擷取下列資料（對投影片至關重要）：**
- `transaction_id`：Capital IQ 交易連結需要
- **公告日期**：這個輪次公開宣布的時間
- **交割日期**：這個輪次正式完成的時間
- 募資金額
- **投前估值**（若有揭露）
- **投後估值**（若有揭露）
- 領投投資人
- 輪次類型（Series A、B、C 等）
- 證券條款
- 顧問
- 定價趨勢（up-round / down-round / flat）

> **日期是必要的。** 公告日期和交割日期必須一律出現在最終投影片的交易表裡。如果只有一個日期，就顯示那個，並把另一個標為「—」。

### 步驟 4：取得重要交易的公司背景

對任何涉及重大交易的公司（大額輪次、顯著估值變動），取得簡短的描述：

```
get_company_summary_from_identifiers(identifiers=[notable_companies])
```

這會為敘事加入背景（例如「這間公司是 2021 年成立的 AI 基礎設施新創，正在擴展到…」）。

### 步驟 5：找出亮點與趨勢

設計投影片之前，先分析資料來挖出故事：

**標記為「Notable」：**
- 輪次 ≥ $100M
- Down round（定價趨勢 = down）
- 新的獨角獸（投後估值超過 $1B）
- 顯著的估值跳升（投後估值 ≥ 上一次已知估值的 2 倍）
- 重複募資者（同一間公司在 6 個月內再次募資）
- 異常龐大的投資人聯貸團

**找出趨勢：**
- 本期投入的總資本 vs. 一般水準（如果有歷史資料）
- 哪些次產業最熱門（輪次最多、資本最多）
- 輪次階段分布（是早期還是後期主導？）
- 整份摘要中最活躍的投資人
- 地理集中度
- 估值趨勢（投前估值是在壓縮還是擴張？）

**選出關鍵重點（3 到 5 個）：**
把最重要的訊號提煉成 3 到 5 個精簡的條列式重點。這些是投影片的核心。每個重點應該是一句話、有力、有資料支撐。

範例：
- "AI sector raised $2.4B across 8 rounds — 3x the prior week, led by a $800M mega-round from [Company] at a $12B post-money valuation."
- "[Company] closed a $200M Series D at $3.5B pre-money, up from $1.8B in its Series C — signaling strong demand for AI developer tools."
- "Down-round activity ticked up: 2 of 6 late-stage rounds priced below prior valuations."

### 步驟 6：產生公司 Logo

對關鍵重點或重要交易中出現的每間公司，用兩層的本地流程產生 logo。**不要用 Clearbit**（`logo.clearbit.com`），它已被棄用且一直失敗。外部的 logo CDN（Brandfetch、logo.dev、Google Favicons）需要 API key，或被網路限制擋住。改用下面的做法：

#### 第 1 層：`simple-icons` npm 套件（3,300 個以上的品牌 SVG，不需要網路）

`simple-icons` 套件內含數千個知名品牌的高品質 SVG 圖示。完全離線運作，不需要 API key，也不需要網路呼叫。連同用來把 SVG 轉成 PNG 的 `sharp` 一起安裝：

```bash
npm install simple-icons sharp
```

**查找策略：**

```javascript
const si = require('simple-icons');
const sharp = require('sharp');

// 以完全符合的標題尋找圖示（不分大小寫）
function findSimpleIcon(companyName) {
    // 先試完全符合
    for (const [key, val] of Object.entries(si)) {
        if (!key.startsWith('si') || !val || !val.title) continue;
        if (val.title.toLowerCase() === companyName.toLowerCase()) return val;
    }
    // 再試去掉常見字尾（AI、Inc.、Corp.）
    const stripped = companyName.replace(/\s*(AI|Inc\.?|Corp\.?|Ltd\.?)$/i, '').trim();
    if (stripped !== companyName) {
        for (const [key, val] of Object.entries(si)) {
            if (!key.startsWith('si') || !val || !val.title) continue;
            if (val.title.toLowerCase() === stripped.toLowerCase()) return val;
        }
    }
    return null;
}

// 用品牌官方顏色把 SVG 轉成 PNG
async function simpleIconToPng(icon, outputPath) {
    const coloredSvg = icon.svg.replace('<svg', `<svg fill="#${icon.hex}"`);
    await sharp(Buffer.from(coloredSvg))
        .resize(128, 128, { fit: 'contain', background: { r: 255, g: 255, b: 255, alpha: 0 } })
        .png()
        .toFile(outputPath);
}
```

**涵蓋率：** 約 43% 的一般 deal flow 公司（對 Stripe、Anthropic、Databricks、Snowflake、Discord、Shopify、SpaceX、Mistral AI、Hugging Face 這類大型科技品牌很強；對小眾金融科技、生技或早期公司較弱）。

#### 第 2 層：透過 `sharp` 的首字母備案（100% 涵蓋）

對於在 `simple-icons` 找不到的公司，產生乾淨的首字母 logo PNG：

```javascript
async function generateInitialLogo(companyName, outputPath) {
    const initial = companyName.charAt(0).toUpperCase();
    const svg = `
    <svg width="128" height="128" xmlns="http://www.w3.org/2000/svg">
        <circle cx="64" cy="64" r="64" fill="#BDBDBD"/>
        <text x="64" y="64" font-family="Arial, Helvetica, sans-serif"
              font-size="56" font-weight="bold" fill="#FFFFFF"
              text-anchor="middle" dominant-baseline="central">${initial}</text>
    </svg>`;
    await sharp(Buffer.from(svg)).png().toFile(outputPath);
}
```

#### 完整流程

```javascript
async function fetchLogo(companyName, outputDir) {
    const fileName = companyName.toLowerCase().replace(/[\s.]+/g, '-') + '.png';
    const outPath = path.join(outputDir, fileName);

    // 第 1 層：試 simple-icons
    const icon = findSimpleIcon(companyName);
    if (icon) {
        await simpleIconToPng(icon, outPath);
        return { path: outPath, source: 'simple-icons' };
    }

    // 第 2 層：產生首字母備案
    await generateInitialLogo(companyName, outPath);
    return { path: outPath, source: 'initial-fallback' };
}
```

**Logo 準則：**
- 所有 logo 都存到 `/home/claude/logos/[company-name].png`
- 所有 logo 都是 128×128 的透明背景 PNG
- 在投影片上，logo 顯示高度為 0.35" 到 0.5"，它們是點綴，不是焦點
- 首字母備案的圓形使用灰色（`BDBDBD`）填色配白字，與單色調色盤一致
- 不要隨意混用 logo 風格：如果多數公司都解析成品牌圖示，少數備案就該自然融入

### 步驟 7：產生單頁 PPTX

建立投影片之前，先讀 `/mnt/skills/public/pptx/SKILL.md` 和 `/mnt/skills/public/pptx/pptxgenjs.md`。

用 `pptxgenjs` 建立**單頁**的 PowerPoint。投影片應該資訊密集但視覺乾淨，要像「主管儀表板」，不是「文字牆」。

#### 投影片版面

```
┌─────────────────────────────────────────────────────────────┐
│  DEAL FLOW DIGEST                                           │
│  [Period] · [Sectors]                           [Date]      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │  $X.XB  │  │  N      │  │  $X.XB  │  │  $X.XB  │       │
│  │ Raised  │  │ Rounds  │  │ Avg Pre │  │ Largest │       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
│                                                             │
│  KEY TAKEAWAYS                                              │
│  ─────────────────────────────────────────────────          │
│  [Logo] Takeaway 1 text goes here...                        │
│  [Logo] Takeaway 2 text goes here...                        │
│  [Logo] Takeaway 3 text goes here...                        │
│  [Logo] Takeaway 4 text goes here...                        │
│                                                             │
│  TOP DEALS                                                  │
│  ┌──────────────────────────────────────────────────────────┐│
│  │Company│Type │Announced│Closed│Amount│Pre-$│Post-$│Lead│🔗││
│  │───────│─────│─────────│──────│──────│─────│──────│────│──││
│  │ ...   │ ... │  ...    │ ...  │ ...  │ ... │ ...  │... │🔗││
│  └──────────────────────────────────────────────────────────┘│
│                                                             │
│  [Footer: Deal Flow Digest · Sources: S&P Global Capital IQ]│
│  [Footer: AI Disclaimer]                                    │
└─────────────────────────────────────────────────────────────┘
```

#### 設計規格

**色彩理念：極簡、單色優先。** 投影片應該感覺像高端的財經簡報，以黑、白、灰為主。顏色**只**用在有意義的地方（例如 down round 用紅色指示、突出的指標用綠色指示），或讀者自然會預期有顏色的地方（公司 logo）。絕對不要把顏色用在純裝飾的用途，像是背景填色、強調色條或漸層效果。

**調色盤：單色主管風格（Monochrome Executive）：**
- 主要背景：`FFFFFF`（白）：乾淨、開闊的投影片背景
- 標題列：`1A1A1A`（近黑）：標題區塊要有強烈對比
- 主要文字：`1A1A1A`（近黑）：所有內文、統計數字、重點
- 次要文字：`6B6B6B`（中灰）：標籤、說明文字、頁尾、日期戳記
- 邊框與分隔線：`D0D0D0`（淺灰）：細微的結構線、卡片外框、表格邊框
- 卡片背景：`F5F5F5`（米白／很淺的灰）：統計卡片填色、表格交錯列
- 連結文字：`2B5797`（低飽和藍）：表格中的 Capital IQ 交易連結（投影片上唯一的藍色）
- **語意色彩（節制使用）：**
  - Down round 或負面訊號：`C0392B`（低飽和紅）：只當作小圓點、標籤或單一個字的強調，絕對不要當作填色或背景
  - 突出的正面指標（新獨角獸、超大輪次）：`2E7D32`（低飽和綠）：一樣是最少量的使用：一個圓點、一個小標籤、或單一個被強調的數字
  - 如果沒有任何資料點值得用顏色指示，**就完全不要用顏色**。完全單色的投影片是完全正確的。

**字體排印：**
- 標題：28 到 32pt、粗體，近黑標題列上用白字
- 統計數字：36 到 44pt、粗體、近黑
- 統計標籤：10 到 12pt、中灰（`6B6B6B`）
- 重點文字：12 到 14pt、近黑、靠左對齊
- 表格文字：9 到 11pt、近黑，次要欄位用灰色（`6B6B6B`）
- 連結文字：9 到 10pt、低飽和藍（`2B5797`）
- 頁尾：8pt、中灰

**統計卡片（最上排）：**
- 4 個關鍵指標用大數字呈現：Total Raised、# Rounds、Avg Pre-Money Valuation、Largest Round
- 每個放在 `F5F5F5` 填色、有細的 `D0D0D0` 邊框的卡片裡，不要陰影、不要彩色填色
- 如果某個統計數字令人意外或極端（例如 3 倍於正常量、創紀錄的交易），可以在那一個數字旁邊放一個小的彩色圓點或底線，否則維持完全單色
- 如果投前估值大多沒有揭露，就換成別的指標（例如 Median Round Size、# New Unicorns）

**關鍵重點（中間區塊）：**
- 3 到 5 個一行式的重點，每個前面加上相關公司的 logo（小，高度約 0.35"）
- 如果沒有 logo，使用**灰色圓形**配白色的公司首字母，不要用彩色圓形
- 靠左對齊，留足夠的間距讓版面透氣
- Down round 或負面重點可以用小紅點當前綴，否則不用顏色
- 有資料時要加入估值脈絡（例如「at a $5B post-money valuation」）

**Top Deals 表格（下方區塊）：**
- 精簡的表格，顯示 4 到 6 筆最重要的交易
- 欄位：Company、Type（Series X）、Announced（日期）、Closed（日期）、Amount ($M)、Pre-Money ($M)、Post-Money ($M)、Lead Investor、Deal Link
- **Announced** 和 **Closed** 欄位以 `MMM DD` 格式顯示日期（例如 "Jan 15"）。這兩欄是必要的，一定要有。如果沒有日期，顯示 "—"。
- **Deal Link** 欄包含可點擊的 "View →" 文字，連到 Capital IQ：
  ```
  https://www.capitaliq.spglobal.com/web/client?#offering/capitalOfferingProfile?id=<transaction_id>
  ```
  其中 `<transaction_id>` 是 `get_rounds_of_funding_from_identifiers` 回傳的 `transaction_id`。
- 如果投前或投後估值沒有揭露，在該儲存格顯示 "—"
- 標題列用近黑（`1A1A1A`）填色配白字；交錯列使用 `F5F5F5` 和 `FFFFFF`
- **讓表格在投影片上水平置中。** 計算表格的總寬度，再設定 `x`，讓它在投影片寬度內置中：`x = (slideWidth - tableWidth) / 2`。對於 16:9 版面（寬 13.33"），如果表格寬 12"，用 `x = 0.67`。絕對不要把表格靠左貼著投影片邊緣。
- 保持緊湊，這是參考資料，不是焦點
- 表格儲存格不要彩色填色。如果某筆交易是 down round，可以在金額旁邊放一個小的紅色文字標籤 "(↓ down)"，這是表格中唯一允許的顏色。

**Deal Link 實作（pptxgenjs）：**
在 pptxgenjs 中，用儲存格物件的 `options.hyperlink` 屬性，替表格儲存格加上超連結：
```javascript
// 帶有 Capital IQ 交易連結的表格儲存格
{
  text: "View →",
  options: {
    hyperlink: {
      url: `https://www.capitaliq.spglobal.com/web/client?#offering/capitalOfferingProfile?id=${transactionId}`
    },
    color: "2B5797",
    fontSize: 9,
    fontFace: "Arial"
  }
}
```

**表格置中（pptxgenjs）：**
一律讓交易表格在投影片上置中。動態計算 x 位置：
```javascript
const SLIDE_W = 13.33; // 16:9 投影片寬度
const TABLE_W = 12.5;  // 表格總寬度（所有欄寬的總和）
const TABLE_X = (SLIDE_W - TABLE_W) / 2; // ≈ 0.42"

slide.addTable(tableRows, {
  x: TABLE_X,
  y: tableY,
  w: TABLE_W,
  colW: [1.8, 0.9, 0.9, 0.9, 1.0, 1.1, 1.2, 1.6, 0.7], // Company, Type, Announced, Closed, Amount, Pre-$, Post-$, Lead, Link
  // ... 其他選項
});
```
可依需要調整 `colW` 的值，但一定要用 `(SLIDE_W - sum(colW)) / 2` 重新計算 `TABLE_X`，讓表格保持置中。

**頁尾：**
- 中灰色小字："Deal Flow Digest · [Period] · Sources: S&P Global Capital IQ · Generated [Date]"

**一般色彩規則（嚴格執行）：**
- 公司 logo 是投影片上唯一「全彩」的元素，直接用來源的原樣呈現。
- Deal 連結使用低飽和藍（`2B5797`），這是除了語意紅／綠之外，唯一非單色的文字顏色。
- 除了 logo 和連結之外，這張投影片用黑白印表機印出來也應該是正確的。
- 絕對不要把顏色用在背景、強調色條、裝飾圖形或段落分隔線上。
- 有疑慮就用灰色。

#### 程式碼結構

```javascript
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "Deal Flow Digest";

const slide = pres.addSlide();
const SLIDE_W = 13.33; // 16:9 投影片寬度（英吋）

// 1. 深色標題列，含標題與期間
// 2. 統計卡片列（4 張卡片：Total Raised、# Rounds、Avg Pre-Money、Largest Round）
// 3. 含 logo 的關鍵重點區塊（要加入估值脈絡）
// 4. Top deals 表格，含 Announced、Closed、Pre-Money、Post-Money 欄位和 Capital IQ 交易連結
//    - 表格置中：x = (SLIDE_W - tableWidth) / 2
// 5. 頁尾

pres.writeFile({ fileName: "/home/claude/deal-flow-digest.pptx" });
```

依照 pptxgenjs 陷阱指南，陰影和重複使用的樣式要用工廠函式（factory function），不要共用物件。

### 步驟 8：對投影片做 QA

依照 PPTX skill 的 QA 流程：

1. **內容 QA：** `python -m markitdown deal-flow-digest.pptx`，驗證所有文字、數字、公司名稱、估值數字和交易連結都正確
2. **視覺 QA：** 轉成圖片並檢查：
   ```bash
   python /mnt/skills/public/pptx/scripts/office/soffice.py --headless --convert-to pdf deal-flow-digest.pptx
   pdftoppm -jpeg -r 200 deal-flow-digest.pdf slide
   ```
   檢查元素重疊、文字溢出、對齊問題、低對比文字、logo 尺寸問題，以及交易連結文字是否可見。
3. **連結 QA：** 驗證表格中的 Capital IQ URL 格式正確，transaction ID 也正確。
4. **修正並重新驗證**：在宣告完成之前，至少要做一輪修正與驗證。

### 步驟 9：呈現結果

1. 把最終的 `.pptx` 複製到 `/mnt/user-data/outputs/`
2. 用 `present_files` 分享投影片
3. 提供 2 到 3 句話的口頭摘要：
   - 「你的摘要涵蓋了 X 個輪次，在 [產業] 共募資 $Y。」
   - 點出最重要的單筆交易和它的估值
   - 標出任何令人擔憂的趨勢（down round、估值壓縮等）

## 錯誤處理

### 實體解析失敗
- **已知公司回傳空結果：** 先檢查 `get_info_from_identifiers`，如果那也失敗，就試 `references/sector-seeds.md` 裡的別名，或直接用 `company_id`。常見的品牌→法律名稱不吻合：Together AI → "Together Computer, Inc."、Character.ai → "Character Technologies, Inc."、Runway ML → "Runway AI, Inc."。
- **子公司：** DeepMind、GitHub、Instagram、WhatsApp、YouTube、BeReal 等是子公司，它們沒有獨立的募資輪次。在背景中把它們註記為「acquired/subsidiary」，但不要把它們回報成「無活動」。
- **已倒閉的公司：** 像 Convoy（2023 年 10 月關閉）這類公司在 S&P Global 中仍能解析，但永遠不會有新活動。`references/sector-seeds.md` 檔案有標記這些，納入公司之前先檢查它。
- **`get_funding_summary_from_identifiers` 出錯或回傳零：** 退回使用 `get_rounds_of_funding_from_identifiers`，summary 工具比較不可靠。絕對不要把 summary 工具當作唯一的資料來源。
- **`role` 參數錯誤：** 如果投資人視角的查詢回傳空值，確認你用的是 `company_investing_in_round_of_funding`，不是 `company_raising_funds`（反之亦然）。

### 資料品質問題
- **期間內沒有活動：** 如果某個產業完全沒有募資輪次，要在投影片上明確註明（"No transactions recorded in [Sector] during the period"），沒有活動本身就是資訊。
- **估值資料稀少：** 如果多數交易的投前和投後估值都沒有揭露，在頁尾註解中註明資料限制，並在表格中使用 "—"。調整統計卡片改顯示不同的指標（例如 Median Round Size），取代 Avg Pre-Money。
- **Logo 取得失敗：** `simple-icons` npm 套件對一般 deal flow 公司約有 43% 的涵蓋率。其餘的用 `sharp` 產生的首字母備案。保持一致的圖示風格，不要隨意混用做法。如果 `simple-icons` 或 `sharp` 安裝失敗，退回使用 pptxgenjs 以圖形為基礎的首字母（灰色橢圓 + 疊上白色文字），不需要外部相依。
- **單張投影片放不下這麼多交易：** 如果重要交易超過 6 筆，在表格中顯示前 6 筆，並加註腳："+N additional deals not shown."。依交易規模排優先順序。
- **大型範圍：** 對有 100 間以上公司的多產業摘要，所有 API 呼叫以 15 到 20 為一批。重要交易寧可求深，不必求次要交易的完整。
- **種子過時：** 如果競爭對手擴展對某個產業只回傳很少的結果，種子公司可能太小眾。多加 2 到 3 個知名名稱，重新擴展以拓寬範圍。
- **連結用的交易 ID 無效：** 如果募資工具回傳的 `transaction_id` 產生不出有效的 Capital IQ URL，該列就省略連結儲存格，不要放壞掉的連結。

## 範例提示

- "Give me a weekly deal flow digest for AI and fintech"
- "Summarize this week's funding in biotech"
- "Deal roundup for my coverage — cybersecurity, cloud infrastructure, and dev tools — last 2 weeks"
- "What happened in venture this week across all sectors I follow?"
