---
name: "data-dashboard-design"
description: "設計有效的資料儀表板，包含正確的 KPI 層級、圖表類型選擇與互動功能。當使用者需要建立儀表板、選擇合適的視覺化、為不同受眾整理指標，或評估儀表板工具時使用。就算使用者只說「做一個 dashboard」、「我們的報表很混亂」、「該用哪種圖表」或「主管找不到他們要的指標」也要用。"
metadata:
  category: "WP-04 數據分析"
  tags: ["data-analysis", "dashboard", "visualization", "bi"]
---

# 儀表板設計

## 框架

```
IRON LAW: One Dashboard, One Audience, One Purpose

A dashboard that tries to serve the CEO, the marketing team, AND the
engineers will serve none of them well. Each audience has different
questions, different metrics, and different time horizons.

CEO: "Are we growing?" → North Star + revenue + key trends
Marketing: "Which campaigns work?" → CAC, ROAS, conversion by channel
Engineering: "Is the system healthy?" → Latency, error rate, uptime
```

### KPI 層級（金字塔結構）

```
          [North Star Metric]
         /                    \
    [L1: 3-5 Business KPIs]
       /         |         \
  [L2: Driving Metrics per KPI]
     /     |     |     |     \
[L3: Diagnostic / Operational Metrics]
```

- **北極星指標（North Star）**：「一個」最能代表價值傳遞的指標（DAU、MRR、GMV）
- **L1**：驅動北極星的業務 KPI（留存、獲客、變現）
- **L2**：團隊可以採取行動的驅動指標（轉換率、ARPU、流失率）
- **L3**：用來除錯的診斷指標（頁面載入時間、錯誤率、漏斗各步驟的轉換）

### 圖表類型選擇

| 問題 | 圖表 | 原因 |
|----------|-------|-----|
| 趨勢如何？ | **折線圖** | 顯示隨時間的變化 |
| 各類別怎麼比較？ | **長條圖**（類別多時用橫向） | 容易比較 |
| 組成是什麼？ | **堆疊長條圖**或**圓餅圖**（少用，切片 < 5 個） | 顯示整體的各個部分 |
| 分布如何？ | **直方圖**或**箱形圖** | 顯示散布和離群值 |
| 有什麼關係？ | **散佈圖** | 顯示相關性 |
| 地理上有什麼模式？ | **地圖 / 分級統計圖** | 空間模式 |
| 單一數字是多少？ | **計分卡 / 大數字** | 一眼看到狀態 |
| 跟目標比如何？ | **儀表盤**或**子彈圖** | 追蹤進度 |

### 設計原則

1. **5 秒原則**：儀表板的主要訊息要在 5 秒內看懂
2. **首屏（above the fold）**：最重要的指標不用捲動就看得到
3. **一致的時間範圍**：同一個儀表板上的所有圖表，預設都用相同的時間區間
4. **顏色要有目的**：用顏色編碼意義（紅 = 不好、綠 = 好），不是裝飾
5. **比較的脈絡**：每個數字都需要脈絡，例如跟上一期比、跟目標比、跟基準比
6. **漸進式揭露**：上方是摘要 → 點擊/下鑽看細節

### 儀表板層級

| 層級 | 受眾 | 更新頻率 | 內容 |
|-------|---------|---------|---------|
| **高階主管** | C-suite、董事會 | 每週/每月 | 5-8 個 KPI、趨勢、警示 |
| **營運** | 組長 | 每日 | 10-15 個指標，可依團隊/產品篩選 |
| **診斷** | 分析師、工程師 | 即時到每小時 | 20 個以上指標、下鑽、可存取原始資料 |

### 工具比較

| 工具 | 最適合 | 成本 | 學習曲線 |
|------|---------|------|---------------|
| **Tableau** | 複雜分析、大型資料集 | $$$ | 中到高 |
| **Power BI** | Microsoft 生態系、企業 | $$ | 中 |
| **Looker** | 以 SQL 為主的團隊、資料建模 | $$$ | 高 |
| **Metabase** | 快速上手、開源、自助式 | 免費/$ | 低 |
| **Google Sheets/Data Studio** | 簡單、協作、免費 | 免費 | 低 |
| **Grafana** | 基礎設施/即時監控 | 免費/$ | 中 |

## 輸出格式

```markdown
# Dashboard Specification: {Name}

## Purpose & Audience
- Audience: {who}
- Key question: {what they need to answer}
- Refresh: {real-time / daily / weekly}

## KPI Hierarchy
- North Star: {metric}
- L1 KPIs: {3-5 metrics}
- L2 Driving Metrics: {per L1}

## Layout
| Position | Component | Chart Type | Metric |
|----------|-----------|-----------|--------|
| Top-left | {scorecard} | Big number | {North Star} |
| Top-right | {trend} | Line chart | {key KPI over time} |
| Mid-left | {comparison} | Bar chart | {breakdown by segment} |
| ... | ... | ... | ... |

## Filters
- Date range, product, segment, region

## Alerts
| Metric | Threshold | Alert To |
|--------|-----------|---------|
| {metric} | {value} | {team/person} |
```

## 常見陷阱

- **儀表板 ≠ 報告**：報告解釋發生了什麼（敘述）；儀表板監控「正在」發生什麼（即時狀態）。不要做出一個需要閱讀的儀表板。
- **圓餅圖幾乎都是錯的**：人類不擅長比較角度。類別超過 3 個的組成，用長條圖。圓餅圖只適用於 2 到 3 個大小差很多的切片。
- **指標太多等於沒有指標**：什麼都強調，就等於沒有強調。高階主管儀表板限制在 5 到 8 個指標。要更多就用篩選或下鑽。
- **虛榮指標會偷偷混進來**：總使用者數、頁面瀏覽數和下載數看起來很亮眼，但很少驅動行動。儀表板上的每個指標都該回答：「如果這個數字變了，我們會做什麼不一樣的事？」
- **ETL 的可靠度**：儀表板的品質取決於它的資料管線。資料過時、不完整或錯誤，儀表板就會變成負債。要顯眼地顯示「最後更新時間」。

## 參考資料

- 儀表板線框範本，見 `references/dashboard-templates.md`
- 以 SQL 定義的指標，見 `references/metric-definitions.md`
