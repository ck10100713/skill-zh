---
name: build-dashboard
description: 建置帶有圖表、篩選器和表格的互動式 HTML dashboard。當要做有 KPI 卡片的主管總覽、把查詢結果變成可分享的獨立報告、建立團隊監控快照，或需要在一個能用瀏覽器開啟的檔案裡放多張帶篩選器的圖表時使用。
argument-hint: "<description> [data source]"
---

# /build-dashboard - 建置互動式 Dashboard

> 如果看到不熟的 placeholder，或需要確認目前連了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

建置一個獨立的互動式 HTML dashboard，包含圖表、篩選器、表格和專業的樣式。直接在瀏覽器開啟就能用，不需要 server 或任何相依套件。

## 用法

```
/build-dashboard <dashboard 的描述> [資料來源]
```

## 工作流程

### 1. 了解 Dashboard 的需求

要確認：

- **目的**：主管總覽、營運監控、深入分析、團隊報告
- **使用者**：誰會用這個 dashboard？
- **關鍵指標**：哪些數字最重要？
- **維度**：使用者應該能依什麼來篩選或切分？
- **資料來源**：即時查詢、貼上的資料、CSV 檔，或範例資料

### 2. 取得資料

**如果有連線 data warehouse：**
1. 查詢需要的資料
2. 把結果以 JSON 的形式嵌進 HTML 檔

**如果資料是貼上或上傳的：**
1. 解析並清理資料
2. 以 JSON 嵌進 dashboard

**如果只有描述、沒有資料：**
1. 建立一份符合所述 schema 的擬真範例資料集
2. 在 dashboard 上註明用的是範例資料
3. 提供換成真實資料的說明

### 3. 設計 Dashboard 版面

依循標準的 dashboard 版面模式：

```
┌──────────────────────────────────────────────────┐
│  Dashboard 標題                      [篩選器 ▼]  │
├────────────┬────────────┬────────────┬───────────┤
│  KPI Card  │  KPI Card  │  KPI Card  │ KPI Card  │
├────────────┴────────────┼────────────┴───────────┤
│                         │                        │
│    主要圖表              │   次要圖表              │
│    （最大區塊）          │                        │
│                         │                        │
├─────────────────────────┴────────────────────────┤
│                                                  │
│    明細表格（可排序、可捲動）                     │
│                                                  │
└──────────────────────────────────────────────────┘
```

**版面要配合內容調整：**
- 最上面放 2 到 4 張 KPI 卡片，顯示重點數字
- 中間放 1 到 3 張圖表，呈現趨勢和拆解
- 底部可選擇放明細表格，給往下鑽取的資料
- 篩選器依複雜度放在標題列或側邊欄

### 4. 建置 HTML Dashboard

用下面的基本模板產生單一的獨立 HTML 檔。這個檔案包含：

**結構（HTML）：**
- 語意化的 HTML5 版面
- 用 CSS Grid 或 Flexbox 做的響應式網格
- 篩選控制項（下拉選單、日期選擇器、切換開關）
- 帶數值和標籤的 KPI 卡片
- 圖表容器
- 表頭可排序的資料表

**樣式（CSS）：**
- 專業的配色（乾淨的白與灰，資料用強調色）
- 卡片式版面，搭配輕微陰影
- 一致的字體排印（用系統字型，載入快）
- 能適應不同螢幕尺寸的響應式設計
- 適合列印的樣式

**互動（JavaScript）：**
- 用 Chart.js 做互動式圖表（透過 CDN 引入）
- 篩選下拉選單會同時更新所有圖表和表格
- 可排序的表格欄位
- 圖表上的 hover 提示
- 數字格式化（千分位、貨幣、百分比）

**資料（嵌入的 JSON）：**
- 所有資料直接以 JavaScript 變數嵌在 HTML 裡
- 不需要抓取外部資料
- Dashboard 完全可以離線運作

### 5. 實作圖表類型

所有圖表都用 Chart.js。常見的 dashboard 圖表模式：

- **折線圖**：時間序列趨勢
- **長條圖**：類別比較
- **甜甜圈圖**：組成比例（類別少於 6 個時）
- **堆疊長條圖**：組成隨時間的變化
- **混合圖（長條加折線）**：用量疊上比率

每種圖表類型都用下面的 Chart.js 整合模式。

### 6. 加上互動

下拉篩選、日期區間篩選、組合篩選邏輯、可排序表格和圖表更新，都用下面的篩選與互動實作模式。

### 7. 儲存並開啟

1. 把 dashboard 存成 HTML 檔，檔名要有描述性（例如 `sales_dashboard.html`）
2. 用使用者預設的瀏覽器開啟
3. 確認顯示正確
4. 提供更新資料或客製化的說明

---

## 基本模板

每個 dashboard 都遵循這個結構：

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Title</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.1" integrity="sha384-jb8JQMbMoBUzgWatfe6COACi2ljcDdZQ2OxczGA3bGNeWe+6DChMTBJemed7ZnvJ" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0" integrity="sha384-cVMg8E3QFwTvGCDuK+ET4PD341jF3W8nO1auiXfuZNQkzbUUiBGLsIQUE+b1mxws" crossorigin="anonymous"></script>
    <style>
        /* Dashboard 樣式放這裡 */
    </style>
</head>
<body>
    <div class="dashboard-container">
        <header class="dashboard-header">
            <h1>Dashboard Title</h1>
            <div class="filters">
                <!-- 篩選控制項 -->
            </div>
        </header>

        <section class="kpi-row">
            <!-- KPI 卡片 -->
        </section>

        <section class="chart-row">
            <!-- 圖表容器 -->
        </section>

        <section class="table-section">
            <!-- 資料表 -->
        </section>

        <footer class="dashboard-footer">
            <span>Data as of: <span id="data-date"></span></span>
        </footer>
    </div>

    <script>
        // 嵌入的資料
        const DATA = [];

        // Dashboard 邏輯
        class Dashboard {
            constructor(data) {
                this.rawData = data;
                this.filteredData = data;
                this.charts = {};
                this.init();
            }

            init() {
                this.setupFilters();
                this.renderKPIs();
                this.renderCharts();
                this.renderTable();
            }

            applyFilters() {
                // 篩選邏輯
                this.filteredData = this.rawData.filter(row => {
                    // 套用每個啟用中的篩選器
                    return true; // 佔位用
                });
                this.renderKPIs();
                this.updateCharts();
                this.renderTable();
            }

            // ... 每個區塊各自的 method
        }

        const dashboard = new Dashboard(DATA);
    </script>
</body>
</html>
```

## KPI 卡片模式

```html
<div class="kpi-card">
    <div class="kpi-label">Total Revenue</div>
    <div class="kpi-value" id="kpi-revenue">$0</div>
    <div class="kpi-change positive" id="kpi-revenue-change">+0%</div>
</div>
```

```javascript
function renderKPI(elementId, value, previousValue, format = 'number') {
    const el = document.getElementById(elementId);
    const changeEl = document.getElementById(elementId + '-change');

    // 格式化數值
    el.textContent = formatValue(value, format);

    // 計算並顯示變化
    if (previousValue && previousValue !== 0) {
        const pctChange = ((value - previousValue) / previousValue) * 100;
        const sign = pctChange >= 0 ? '+' : '';
        changeEl.textContent = `${sign}${pctChange.toFixed(1)}% vs prior period`;
        changeEl.className = `kpi-change ${pctChange >= 0 ? 'positive' : 'negative'}`;
    }
}

function formatValue(value, format) {
    switch (format) {
        case 'currency':
            if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
            if (value >= 1e3) return `$${(value / 1e3).toFixed(1)}K`;
            return `$${value.toFixed(0)}`;
        case 'percent':
            return `${value.toFixed(1)}%`;
        case 'number':
            if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
            if (value >= 1e3) return `${(value / 1e3).toFixed(1)}K`;
            return value.toLocaleString();
        default:
            return value.toString();
    }
}
```

## Chart.js 整合

### 圖表容器模式

```html
<div class="chart-container">
    <h3 class="chart-title">Monthly Revenue Trend</h3>
    <canvas id="revenue-chart"></canvas>
</div>
```

### 折線圖

```javascript
function createLineChart(canvasId, labels, datasets) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets.map((ds, i) => ({
                label: ds.label,
                data: ds.data,
                borderColor: COLORS[i % COLORS.length],
                backgroundColor: COLORS[i % COLORS.length] + '20',
                borderWidth: 2,
                fill: ds.fill || false,
                tension: 0.3,
                pointRadius: 3,
                pointHoverRadius: 6,
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: { usePointStyle: true, padding: 20 }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${formatValue(context.parsed.y, 'currency')}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatValue(value, 'currency');
                        }
                    }
                }
            }
        }
    });
}
```

### 長條圖

```javascript
function createBarChart(canvasId, labels, data, options = {}) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const isHorizontal = options.horizontal || labels.length > 8;

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: options.label || 'Value',
                data: data,
                backgroundColor: options.colors || COLORS.map(c => c + 'CC'),
                borderColor: options.colors || COLORS,
                borderWidth: 1,
                borderRadius: 4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: isHorizontal ? 'y' : 'x',
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return formatValue(context.parsed[isHorizontal ? 'x' : 'y'], options.format || 'number');
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: { display: isHorizontal },
                    ticks: isHorizontal ? {
                        callback: function(value) {
                            return formatValue(value, options.format || 'number');
                        }
                    } : {}
                },
                y: {
                    beginAtZero: !isHorizontal,
                    grid: { display: !isHorizontal },
                    ticks: !isHorizontal ? {
                        callback: function(value) {
                            return formatValue(value, options.format || 'number');
                        }
                    } : {}
                }
            }
        }
    });
}
```

### 甜甜圈圖

```javascript
function createDoughnutChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: COLORS.map(c => c + 'CC'),
                borderColor: '#ffffff',
                borderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: { usePointStyle: true, padding: 15 }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${formatValue(context.parsed, 'number')} (${pct}%)`;
                        }
                    }
                }
            }
        }
    });
}
```

### 篩選變更時更新圖表

```javascript
function updateChart(chart, newLabels, newData) {
    chart.data.labels = newLabels;

    if (Array.isArray(newData[0])) {
        // 多個資料集
        newData.forEach((data, i) => {
            chart.data.datasets[i].data = data;
        });
    } else {
        chart.data.datasets[0].data = newData;
    }

    chart.update('none'); // 'none' 會停用動畫，立即更新
}
```

## 篩選與互動實作

### 下拉篩選

```html
<div class="filter-group">
    <label for="filter-region">Region</label>
    <select id="filter-region" onchange="dashboard.applyFilters()">
        <option value="all">All Regions</option>
    </select>
</div>
```

```javascript
function populateFilter(selectId, data, field) {
    const select = document.getElementById(selectId);
    const values = [...new Set(data.map(d => d[field]))].sort();

    // 保留「All」選項，再加入不重複的值
    values.forEach(val => {
        const option = document.createElement('option');
        option.value = val;
        option.textContent = val;
        select.appendChild(option);
    });
}

function getFilterValue(selectId) {
    const val = document.getElementById(selectId).value;
    return val === 'all' ? null : val;
}
```

### 日期區間篩選

```html
<div class="filter-group">
    <label>Date Range</label>
    <input type="date" id="filter-date-start" onchange="dashboard.applyFilters()">
    <span>to</span>
    <input type="date" id="filter-date-end" onchange="dashboard.applyFilters()">
</div>
```

```javascript
function filterByDateRange(data, dateField, startDate, endDate) {
    return data.filter(row => {
        const rowDate = new Date(row[dateField]);
        if (startDate && rowDate < new Date(startDate)) return false;
        if (endDate && rowDate > new Date(endDate)) return false;
        return true;
    });
}
```

### 組合篩選邏輯

```javascript
applyFilters() {
    const region = getFilterValue('filter-region');
    const category = getFilterValue('filter-category');
    const startDate = document.getElementById('filter-date-start').value;
    const endDate = document.getElementById('filter-date-end').value;

    this.filteredData = this.rawData.filter(row => {
        if (region && row.region !== region) return false;
        if (category && row.category !== category) return false;
        if (startDate && row.date < startDate) return false;
        if (endDate && row.date > endDate) return false;
        return true;
    });

    this.renderKPIs();
    this.updateCharts();
    this.renderTable();
}
```

### 可排序表格

```javascript
function renderTable(containerId, data, columns) {
    const container = document.getElementById(containerId);
    let sortCol = null;
    let sortDir = 'desc';

    function render(sortedData) {
        let html = '<table class="data-table">';

        // 表頭
        html += '<thead><tr>';
        columns.forEach(col => {
            const arrow = sortCol === col.field
                ? (sortDir === 'asc' ? ' ▲' : ' ▼')
                : '';
            html += `<th onclick="sortTable('${col.field}')" style="cursor:pointer">${col.label}${arrow}</th>`;
        });
        html += '</tr></thead>';

        // 表身
        html += '<tbody>';
        sortedData.forEach(row => {
            html += '<tr>';
            columns.forEach(col => {
                const value = col.format ? formatValue(row[col.field], col.format) : row[col.field];
                html += `<td>${value}</td>`;
            });
            html += '</tr>';
        });
        html += '</tbody></table>';

        container.innerHTML = html;
    }

    window.sortTable = function(field) {
        if (sortCol === field) {
            sortDir = sortDir === 'asc' ? 'desc' : 'asc';
        } else {
            sortCol = field;
            sortDir = 'desc';
        }
        const sorted = [...data].sort((a, b) => {
            const aVal = a[field], bVal = b[field];
            const cmp = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
            return sortDir === 'asc' ? cmp : -cmp;
        });
        render(sorted);
    };

    render(data);
}
```

## Dashboard 的 CSS 樣式

### 色彩系統

```css
:root {
    /* 背景層 */
    --bg-primary: #f8f9fa;
    --bg-card: #ffffff;
    --bg-header: #1a1a2e;

    /* 文字 */
    --text-primary: #212529;
    --text-secondary: #6c757d;
    --text-on-dark: #ffffff;

    /* 資料用的強調色 */
    --color-1: #4C72B0;
    --color-2: #DD8452;
    --color-3: #55A868;
    --color-4: #C44E52;
    --color-5: #8172B3;
    --color-6: #937860;

    /* 狀態色 */
    --positive: #28a745;
    --negative: #dc3545;
    --neutral: #6c757d;

    /* 間距 */
    --gap: 16px;
    --radius: 8px;
}
```

### 版面

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.5;
}

.dashboard-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: var(--gap);
}

.dashboard-header {
    background: var(--bg-header);
    color: var(--text-on-dark);
    padding: 20px 24px;
    border-radius: var(--radius);
    margin-bottom: var(--gap);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}

.dashboard-header h1 {
    font-size: 20px;
    font-weight: 600;
}
```

### KPI 卡片

```css
.kpi-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--gap);
    margin-bottom: var(--gap);
}

.kpi-card {
    background: var(--bg-card);
    border-radius: var(--radius);
    padding: 20px 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.kpi-label {
    font-size: 13px;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

.kpi-value {
    font-size: 28px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 4px;
}

.kpi-change {
    font-size: 13px;
    font-weight: 500;
}

.kpi-change.positive { color: var(--positive); }
.kpi-change.negative { color: var(--negative); }
```

### 圖表容器

```css
.chart-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: var(--gap);
    margin-bottom: var(--gap);
}

.chart-container {
    background: var(--bg-card);
    border-radius: var(--radius);
    padding: 20px 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.chart-container h3 {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 16px;
}

.chart-container canvas {
    max-height: 300px;
}
```

### 篩選器

```css
.filters {
    display: flex;
    gap: 12px;
    align-items: center;
    flex-wrap: wrap;
}

.filter-group {
    display: flex;
    align-items: center;
    gap: 6px;
}

.filter-group label {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.7);
}

.filter-group select,
.filter-group input[type="date"] {
    padding: 6px 10px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.1);
    color: var(--text-on-dark);
    font-size: 13px;
}

.filter-group select option {
    background: var(--bg-header);
    color: var(--text-on-dark);
}
```

### 資料表

```css
.table-section {
    background: var(--bg-card);
    border-radius: var(--radius);
    padding: 20px 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    overflow-x: auto;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}

.data-table thead th {
    text-align: left;
    padding: 10px 12px;
    border-bottom: 2px solid #dee2e6;
    color: var(--text-secondary);
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
    user-select: none;
}

.data-table thead th:hover {
    color: var(--text-primary);
    background: #f8f9fa;
}

.data-table tbody td {
    padding: 10px 12px;
    border-bottom: 1px solid #f0f0f0;
}

.data-table tbody tr:hover {
    background: #f8f9fa;
}

.data-table tbody tr:last-child td {
    border-bottom: none;
}
```

### 響應式設計

```css
@media (max-width: 768px) {
    .dashboard-header {
        flex-direction: column;
        align-items: flex-start;
    }

    .kpi-row {
        grid-template-columns: repeat(2, 1fr);
    }

    .chart-row {
        grid-template-columns: 1fr;
    }

    .filters {
        flex-direction: column;
        align-items: flex-start;
    }
}

@media print {
    body { background: white; }
    .dashboard-container { max-width: none; }
    .filters { display: none; }
    .chart-container { break-inside: avoid; }
    .kpi-card { border: 1px solid #dee2e6; box-shadow: none; }
}
```

## 大型資料集的效能考量

### 資料量指引

| 資料量 | 做法 |
|---|---|
| <1,000 筆 | 直接嵌進 HTML。互動功能完整。 |
| 1,000 - 10,000 筆 | 嵌進 HTML。圖表可能需要先預先聚合。 |
| 10,000 - 100,000 筆 | 在 server 端預先聚合，只嵌入聚合後的資料。 |
| >100,000 筆 | 不適合做成 client-side dashboard。改用 BI 工具或分頁。 |

### 預先聚合模式

不要嵌入原始資料再到瀏覽器裡聚合：

```javascript
// 不要：嵌入 50,000 筆原始資料
const RAW_DATA = [/* 50,000 rows */];

// 要：先預先聚合再嵌入
const CHART_DATA = {
    monthly_revenue: [
        { month: '2024-01', revenue: 150000, orders: 1200 },
        { month: '2024-02', revenue: 165000, orders: 1350 },
        // ... 12 筆，而不是 50,000 筆
    ],
    top_products: [
        { product: 'Widget A', revenue: 45000 },
        // ... 10 筆
    ],
    kpis: {
        total_revenue: 1980000,
        total_orders: 15600,
        avg_order_value: 127,
    }
};
```

### 圖表效能

- 折線圖每個 series 限制在 500 個資料點以內（必要時降低取樣）
- 長條圖限制在 50 個類別以內
- 散布圖上限 1,000 個點（更大的資料集用取樣）
- 圖表很多的 dashboard 要停用動畫：Chart.js options 裡設 `animation: false`
- 篩選觸發的更新用 `Chart.update('none')`，不要用 `Chart.update()`

### DOM 效能

- 資料表可見的列數限制在 100 到 200 列，更多就加分頁
- 用 `requestAnimationFrame` 協調圖表更新
- 篩選變更時不要重建整個 DOM，只更新有變的元素

```javascript
// 有效率的表格分頁
function renderTablePage(data, page, pageSize = 50) {
    const start = page * pageSize;
    const end = Math.min(start + pageSize, data.length);
    const pageData = data.slice(start, end);
    // 只渲染 pageData
    // 顯示分頁控制項：「Showing 1-50 of 2,340」
}
```

## 範例

```
/build-dashboard 做一個月銷售 dashboard，要有營收趨勢、熱銷產品和各區域拆解。資料在 orders 表。
```

```
/build-dashboard 這是我們的客服工單資料 [貼上 CSV]。做一個 dashboard，顯示各優先級的數量、回應時間趨勢和解決率。
```

```
/build-dashboard 幫 SaaS 公司做一個主管 dashboard 範本，顯示 MRR、流失率、新客戶和 NPS。用範例資料。
```

## 小提醒

- Dashboard 是完全獨立的 HTML 檔，直接把檔案寄給任何人就能分享
- 要做即時 dashboard 的話，考慮改接 BI 工具。這些 dashboard 只是某個時間點的快照
- 可以要求「dark mode」或「presentation mode」來換不同的樣式
- 可以指定配色來配合你的品牌
