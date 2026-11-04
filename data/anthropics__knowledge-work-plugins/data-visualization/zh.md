---
name: data-visualization
description: 用 Python（matplotlib、seaborn、plotly）製作有效的資料視覺化。用在製作圖表、為資料集挑對圖表類型、製作可出版品質的圖，或套用無障礙與色彩理論等設計原則的時候。
user-invocable: false
---

# 資料視覺化 Skill

圖表選擇指引、Python 視覺化的程式碼模式、設計原則，以及無障礙考量，用來製作有效的資料視覺化。

## 圖表選擇指南

### 依資料關係選擇

| 你要呈現什麼 | 最佳圖表 | 替代方案 |
|---|---|---|
| **隨時間的趨勢** | 折線圖 | 面積圖（呈現累計或組成時） |
| **跨類別比較** | 直式長條圖 | 橫式長條圖（類別多時）、棒棒糖圖 |
| **排名** | 橫式長條圖 | 點圖、斜率圖（比較兩個時期） |
| **部分對整體的組成** | 堆疊長條圖 | 樹狀圖（階層式）、華夫圖 |
| **隨時間的組成** | 堆疊面積圖 | 100% 堆疊長條圖（著重比例時） |
| **分布** | 直方圖 | 箱形圖（比較群組）、小提琴圖、帶狀圖 |
| **相關性（2 個變數）** | 散佈圖 | 氣泡圖（用大小加入第 3 個變數） |
| **相關性（多個變數）** | 熱度圖（相關矩陣） | 成對圖（pair plot） |
| **地理模式** | 分級統計圖（choropleth） | 氣泡地圖、六角形地圖 |
| **流向／流程** | 桑基圖（Sankey） | 漏斗圖（連續的階段） |
| **關係網絡** | 網絡圖 | 弦圖 |
| **績效 vs. 目標** | 子彈圖 | 儀表圖（只限單一 KPI） |
| **同時呈現多個 KPI** | 小多圖（small multiples） | 由獨立圖表組成的儀表板 |

### 哪些情況不要用某些圖表

- **圓餅圖**：避免使用，除非少於 6 個類別，而且粗略比較比精確比例更重要。人類不擅長比較角度。改用長條圖。
- **3D 圖表**：絕對不要。它們會扭曲感知，而且不增加任何資訊。
- **雙軸圖表**：謹慎使用。它們可能暗示相關性而誤導。如果使用，要清楚標示兩條軸。
- **堆疊長條圖（類別很多）**：很難比較中間的區段。改用小多圖或分組長條圖。
- **甜甜圈圖**：比圓餅圖稍好，但有同樣的根本問題。頂多用來顯示單一 KPI。

## Python 視覺化程式碼模式

### 設定與樣式

```python
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd
import numpy as np

# 專業樣式設定
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'figure.figsize': (10, 6),
    'figure.dpi': 150,
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 16,
})

# 對色盲友善的調色盤
PALETTE_CATEGORICAL = ['#4C72B0', '#DD8452', '#55A868', '#C44E52', '#8172B3', '#937860']
PALETTE_SEQUENTIAL = 'YlOrRd'
PALETTE_DIVERGING = 'RdBu_r'
```

### 折線圖（時間序列）

```python
fig, ax = plt.subplots(figsize=(10, 6))

for label, group in df.groupby('category'):
    ax.plot(group['date'], group['value'], label=label, linewidth=2)

ax.set_title('Metric Trend by Category', fontweight='bold')
ax.set_xlabel('Date')
ax.set_ylabel('Value')
ax.legend(loc='upper left', frameon=True)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# 格式化 x 軸的日期
fig.autofmt_xdate()

plt.tight_layout()
plt.savefig('trend_chart.png', dpi=150, bbox_inches='tight')
```

### 長條圖（比較）

```python
fig, ax = plt.subplots(figsize=(10, 6))

# 依數值排序，方便閱讀
df_sorted = df.sort_values('metric', ascending=True)

bars = ax.barh(df_sorted['category'], df_sorted['metric'], color=PALETTE_CATEGORICAL[0])

# 加上數值標籤
for bar in bars:
    width = bar.get_width()
    ax.text(width + 0.5, bar.get_y() + bar.get_height()/2,
            f'{width:,.0f}', ha='left', va='center', fontsize=10)

ax.set_title('Metric by Category (Ranked)', fontweight='bold')
ax.set_xlabel('Metric Value')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('bar_chart.png', dpi=150, bbox_inches='tight')
```

### 直方圖（分布）

```python
fig, ax = plt.subplots(figsize=(10, 6))

ax.hist(df['value'], bins=30, color=PALETTE_CATEGORICAL[0], edgecolor='white', alpha=0.8)

# 加上平均值和中位數的線
mean_val = df['value'].mean()
median_val = df['value'].median()
ax.axvline(mean_val, color='red', linestyle='--', linewidth=1.5, label=f'Mean: {mean_val:,.1f}')
ax.axvline(median_val, color='green', linestyle='--', linewidth=1.5, label=f'Median: {median_val:,.1f}')

ax.set_title('Distribution of Values', fontweight='bold')
ax.set_xlabel('Value')
ax.set_ylabel('Frequency')
ax.legend()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('histogram.png', dpi=150, bbox_inches='tight')
```

### 熱度圖

```python
fig, ax = plt.subplots(figsize=(10, 8))

# 把資料轉成熱度圖需要的樞紐格式
pivot = df.pivot_table(index='row_dim', columns='col_dim', values='metric', aggfunc='sum')

sns.heatmap(pivot, annot=True, fmt=',.0f', cmap='YlOrRd',
            linewidths=0.5, ax=ax, cbar_kws={'label': 'Metric Value'})

ax.set_title('Metric by Row Dimension and Column Dimension', fontweight='bold')
ax.set_xlabel('Column Dimension')
ax.set_ylabel('Row Dimension')

plt.tight_layout()
plt.savefig('heatmap.png', dpi=150, bbox_inches='tight')
```

### 小多圖（Small Multiples）

```python
categories = df['category'].unique()
n_cats = len(categories)
n_cols = min(3, n_cats)
n_rows = (n_cats + n_cols - 1) // n_cols

fig, axes = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4*n_rows), sharex=True, sharey=True)
axes = axes.flatten() if n_cats > 1 else [axes]

for i, cat in enumerate(categories):
    ax = axes[i]
    subset = df[df['category'] == cat]
    ax.plot(subset['date'], subset['value'], color=PALETTE_CATEGORICAL[i % len(PALETTE_CATEGORICAL)])
    ax.set_title(cat, fontsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# 隱藏空的子圖
for j in range(i+1, len(axes)):
    axes[j].set_visible(False)

fig.suptitle('Trends by Category', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('small_multiples.png', dpi=150, bbox_inches='tight')
```

### 數字格式化的輔助函式

```python
def format_number(val, format_type='number'):
    """Format numbers for chart labels."""
    if format_type == 'currency':
        if abs(val) >= 1e9:
            return f'${val/1e9:.1f}B'
        elif abs(val) >= 1e6:
            return f'${val/1e6:.1f}M'
        elif abs(val) >= 1e3:
            return f'${val/1e3:.1f}K'
        else:
            return f'${val:,.0f}'
    elif format_type == 'percent':
        return f'{val:.1f}%'
    elif format_type == 'number':
        if abs(val) >= 1e9:
            return f'{val/1e9:.1f}B'
        elif abs(val) >= 1e6:
            return f'{val/1e6:.1f}M'
        elif abs(val) >= 1e3:
            return f'{val/1e3:.1f}K'
        else:
            return f'{val:,.0f}'
    return str(val)

# 搭配軸格式化器使用
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: format_number(x, 'currency')))
```

### 用 Plotly 做互動式圖表

```python
import plotly.express as px
import plotly.graph_objects as go

# 簡單的互動式折線圖
fig = px.line(df, x='date', y='value', color='category',
              title='Interactive Metric Trend',
              labels={'value': 'Metric Value', 'date': 'Date'})
fig.update_layout(hovermode='x unified')
fig.write_html('interactive_chart.html')
fig.show()

# 帶有 hover 資料的互動式散佈圖
fig = px.scatter(df, x='metric_a', y='metric_b', color='category',
                 size='size_metric', hover_data=['name', 'detail_field'],
                 title='Correlation Analysis')
fig.show()
```

## 設計原則

### 顏色

- **有目的地使用顏色**：顏色應該用來編碼資料，不是裝飾
- **突顯故事**：關鍵洞察用明亮的強調色，其他都用灰色
- **順序資料**：有順序的數值用單一色相的漸層（由淺到深）
- **發散資料**：有意義中心點的資料，用雙色相漸層加上中性的中點
- **類別資料**：用明顯不同的色相，最多 6-8 個，再多就會混淆
- **避免只用紅／綠**：8% 的男性有紅綠色盲。以藍／橘作為主要的配對

### 字體排印

- **標題要說出洞察**：「Revenue grew 23% YoY」勝過「Revenue by Month」
- **副標題補充背景**：日期範圍、套用的篩選、資料來源
- **軸標籤要易讀**：盡量不要旋轉 90 度。改用縮短或換行
- **資料標籤增加精確度**：用在關鍵的點，不要每根長條都放
- **註解突顯重點**：用文字註解標出特定的點

### 版面

- **減少圖表雜訊**：移除沒有承載資訊的格線、邊框、背景
- **有意義地排序**：類別依數值排序（不要依字母），除非有自然的順序（月份、階段）
- **適當的長寬比**：時間序列寬大於高（3:1 到 2:1）；比較類的可以接近方形
- **留白是好事**：不要把圖表擠在一起。讓每個視覺化都有喘息的空間

### 準確性

- **長條圖從零開始**：一定要。從 95 到 100 的長條會誇大 5% 的差異
- **折線圖可以有非零的基線**：當變動範圍本身有意義時
- **跨面板用一致的刻度**：比較多張圖表時，使用相同的軸範圍
- **顯示不確定性**：資料不確定時，用誤差線、信賴區間或範圍
- **標示你的軸**：絕對不要讓讀者猜數字代表什麼

## 無障礙考量

### 色盲

- 絕對不要只靠顏色來區分資料序列
- 加上圖案填充、不同的線條樣式（實線、虛線、點線），或直接標示
- 用色盲模擬器測試（例如 Coblis、Sim Daltonism）
- 使用對色盲友善的調色盤：`sns.color_palette("colorblind")`

### 螢幕閱讀器

- 附上描述圖表關鍵發現的替代文字（alt text）
- 在視覺化旁邊提供資料表作為替代
- 使用語意化的標題和標籤

### 一般無障礙

- 資料元素和背景之間要有足夠的對比
- 文字大小：標籤至少 10pt，標題至少 12pt
- 避免只透過空間位置來傳達資訊（加上標籤）
- 考慮列印：這張圖在黑白下還能用嗎？

### 無障礙檢查清單

分享視覺化之前：
- [ ] 圖表不靠顏色也能運作（用圖案、標籤或線條樣式區分序列）
- [ ] 文字在標準縮放比例下可讀
- [ ] 標題描述的是洞察，不只是資料
- [ ] 軸有標示單位
- [ ] 圖例清楚，位置不遮住資料
- [ ] 已註明資料來源和日期範圍
