---
name: create-viz
description: 用 Python 製作可出版品質的視覺化圖表。用在把查詢結果或 DataFrame 變成圖表、為趨勢或比較挑對圖表類型、為報告或簡報產生圖，或需要有 hover 和縮放的互動式圖表時。
argument-hint: "<data source> [chart type]"
---

# /create-viz - 建立視覺化圖表

> 如果看到不熟的佔位符，或需要確認目前連了哪些工具，請看 [CONNECTORS.md](../../CONNECTORS.md)。

用 Python 製作可出版品質的資料視覺化。依據資料產生圖表，遵循清晰、準確和設計上的最佳實務。

## 用法

```
/create-viz <data source> [chart type] [additional instructions]
```

## 工作流程

### 1. 了解需求

要判斷：

- **資料來源**：查詢結果、貼上的資料、CSV/Excel 檔，或需要去查詢的資料
- **圖表類型**：使用者明確指定的，或需要推薦的
- **目的**：探索、簡報、報告、儀表板元件
- **受眾**：技術團隊、高階主管、外部利害關係人

### 2. 取得資料

**如果有連接資料倉儲，而且資料需要查詢：**
1. 寫好並執行查詢
2. 把結果載入 pandas DataFrame

**如果資料是貼上或上傳的：**
1. 把資料解析成 pandas DataFrame
2. 視需要清理和準備（型別轉換、處理空值）

**如果資料來自對話中先前的分析：**
1. 直接參照現有的資料

### 3. 選擇圖表類型

如果使用者沒指定圖表類型，就根據資料和問題推薦一種：

| 資料關係 | 建議圖表 |
|---|---|
| 隨時間的趨勢 | 折線圖 |
| 跨類別比較 | 長條圖（類別多時用橫向） |
| 部分對整體的組成 | 堆疊長條圖或面積圖（除非少於 6 個類別，否則避免圓餅圖） |
| 數值的分布 | 直方圖或箱形圖 |
| 兩個變數的相關性 | 散佈圖 |
| 兩個變數隨時間的比較 | 雙軸折線圖或分組長條圖 |
| 地理資料 | 分級統計圖（choropleth） |
| 排名 | 橫向長條圖 |
| 流向或流程 | 桑基圖（Sankey） |
| 關係矩陣 | 熱度圖 |

如果使用者沒有指定，就簡短說明推薦的理由。

### 4. 產生視覺化圖表

依需求，用下列其中一個函式庫寫 Python 程式碼：

- **matplotlib + seaborn**：最適合靜態、可出版品質的圖表。預設選擇。
- **plotly**：最適合互動式圖表，或使用者要求互動性的時候。

**程式碼要求：**

```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# 設定專業的樣式
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# 建立大小適當的圖
fig, ax = plt.subplots(figsize=(10, 6))

# [圖表專屬的程式碼]

# 一定要包含：
ax.set_title('Clear, Descriptive Title', fontsize=14, fontweight='bold')
ax.set_xlabel('X-Axis Label', fontsize=11)
ax.set_ylabel('Y-Axis Label', fontsize=11)

# 適當地格式化數字
# - 百分比：'45.2%'，不是 '0.452'
# - 貨幣：'$1.2M'，不是 '1200000'
# - 大數字：'2.3K' 或 '1.5M'，不是 '2300' 或 '1500000'

# 移除多餘的圖表雜訊
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('chart_name.png', dpi=150, bbox_inches='tight')
plt.show()
```

### 5. 套用設計最佳實務

**顏色：**
- 使用一致、對色盲友善的調色盤
- 顏色要有意義（不是裝飾用）
- 用對比色突顯關鍵的資料點或趨勢
- 把比較不重要的參考資料調成灰色

**字體排印：**
- 標題要寫出洞察，而不只是指標（例如「營收年增 23%」，而不是「每月營收」）
- 軸標籤要易讀（盡量不要旋轉 90 度）
- 在關鍵點加上資料標籤，只要能讓圖更清楚

**版面：**
- 適當的留白和邊距
- 圖例位置不要遮住資料
- 類別依數值排序（不要依字母排序），除非有自然的順序

**準確性：**
- 長條圖的 Y 軸要從零開始
- 沒有清楚標註的話，不要用會誤導的軸截斷
- 比較多個面板時要用一致的刻度
- 適當的精確度（不要顯示 10 位小數）

### 6. 儲存與呈現

1. 把圖表存成 PNG 檔，取一個有描述性的檔名
2. 把圖表顯示給使用者看
3. 附上用到的程式碼，讓他們可以修改
4. 建議變化版本（不同的圖表類型、不同的分組、放大的時間範圍）

## 範例

```
/create-viz Show monthly revenue for the last 12 months as a line chart with the trend highlighted
```

```
/create-viz Here's our NPS data by product: [pastes data]. Create a horizontal bar chart ranking products by score.
```

```
/create-viz Query the orders table and create a heatmap of order volume by day-of-week and hour
```

## 小提醒

- 想要互動式圖表（hover、縮放、篩選），就提到「interactive」，Claude 會改用 plotly
- 需要較大的字體和較高的對比，就指定「presentation」
- 可以一次要求多張圖表（例如「create a 2x2 grid of charts showing...」）
- 圖表會以 PNG 檔存到你目前的目錄
