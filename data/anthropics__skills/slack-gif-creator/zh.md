---
name: slack-gif-creator
description: 建立針對 Slack 最佳化的動態 GIF 所需的知識與工具。提供限制條件、驗證工具和動畫概念。當使用者要求做給 Slack 用的動態 GIF 時使用，例如「幫我做一個 X 在做 Y 的 GIF 給 Slack 用」。
license: Complete terms in LICENSE.txt
---

# Slack GIF 製作工具

一套工具包，提供建立針對 Slack 最佳化的動態 GIF 所需的工具和知識。

## Slack 的要求

**尺寸：**
- 表情符號 GIF：128x128（建議）
- 訊息 GIF：480x480

**參數：**
- FPS：10-30（越低檔案越小）
- 顏色數：48-128（越少檔案越小）
- 長度：表情符號 GIF 要控制在 3 秒以內

## 核心流程

```python
from core.gif_builder import GIFBuilder
from PIL import Image, ImageDraw

# 1. 建立 builder
builder = GIFBuilder(width=128, height=128, fps=10)

# 2. 產生 frame
for i in range(12):
    frame = Image.new('RGB', (128, 128), (240, 248, 255))
    draw = ImageDraw.Draw(frame)

    # 用 PIL 的基本繪圖功能畫你的動畫
    # （圓形、多邊形、線條等）

    builder.add_frame(frame)

# 3. 最佳化後儲存
builder.save('output.gif', num_colors=48, optimize_for_emoji=True)
```

## 繪製圖形

### 處理使用者上傳的圖片
如果使用者上傳了圖片，要判斷他想要的是：
- **直接使用**（例如「讓這張圖動起來」、「把這個拆成 frame」）
- **當作靈感**（例如「做一個像這樣的東西」）

用 PIL 載入並處理圖片：
```python
from PIL import Image

uploaded = Image.open('file.png')
# 直接使用，或只拿來參考顏色和風格
```

### 從零開始畫
從零開始畫圖形時，使用 PIL ImageDraw 的基本繪圖功能：

```python
from PIL import ImageDraw

draw = ImageDraw.Draw(frame)

# 圓形／橢圓
draw.ellipse([x1, y1, x2, y2], fill=(r, g, b), outline=(r, g, b), width=3)

# 星星、三角形，任何多邊形
points = [(x1, y1), (x2, y2), (x3, y3), ...]
draw.polygon(points, fill=(r, g, b), outline=(r, g, b), width=3)

# 線條
draw.line([(x1, y1), (x2, y2)], fill=(r, g, b), width=5)

# 矩形
draw.rectangle([x1, y1, x2, y2], fill=(r, g, b), outline=(r, g, b), width=3)
```

**不要用：** 表情符號字型（跨平台不穩定），也不要假設這個 skill 裡有預先打包好的圖形。

### 讓圖形好看

圖形要看起來精緻又有創意，不能只是基本款。做法如下：

**用粗一點的線**：輪廓和線條一律設 `width=2` 或更高。細線（width=1）看起來斷斷續續、很業餘。

**加上視覺深度**：
- 背景用漸層（`create_gradient_background`）
- 疊多個形狀增加複雜度（例如星星裡面再放一顆小星星）

**讓形狀更有趣**：
- 不要只畫一個單純的圓，要加高光、圓環或花紋
- 星星可以有光暈（在後面畫更大的半透明版本）
- 組合多個形狀（星星加閃光、圓形加圓環）

**注意顏色**：
- 用鮮豔、互補的顏色
- 加對比（淺色形狀配深色輪廓，深色形狀配淺色輪廓）
- 考慮整體構圖

**複雜形狀**（愛心、雪花等）：
- 組合多邊形和橢圓
- 仔細計算各點位置，讓它對稱
- 加細節（愛心可以有一道高光曲線，雪花有細緻的分枝）

發揮創意、做細緻一點！好的 Slack GIF 應該看起來精緻，而不是像佔位用的圖。

## 可用的工具

### GIFBuilder（`core.gif_builder`）
組合 frame 並針對 Slack 最佳化：
```python
builder = GIFBuilder(width=128, height=128, fps=10)
builder.add_frame(frame)  # 加入 PIL Image
builder.add_frames(frames)  # 加入 frame 的 list
builder.save('out.gif', num_colors=48, optimize_for_emoji=True, remove_duplicates=True)
```

### 驗證器（`core.validators`）
檢查 GIF 是否符合 Slack 的要求：
```python
from core.validators import validate_gif, is_slack_ready

# 詳細驗證
passes, info = validate_gif('my.gif', is_emoji=True, verbose=True)

# 快速檢查
if is_slack_ready('my.gif'):
    print("Ready!")
```

### 緩動函式（`core.easing`）
讓動作平滑，不要線性：
```python
from core.easing import interpolate

# 進度從 0.0 到 1.0
t = i / (num_frames - 1)

# 套用緩動
y = interpolate(start=0, end=400, t=t, easing='ease_out')

# 可用：linear, ease_in, ease_out, ease_in_out,
#      bounce_out, elastic_out, back_out
```

### Frame 輔助函式（`core.frame_composer`）
方便處理常見需求的函式：
```python
from core.frame_composer import (
    create_blank_frame,         # 純色背景
    create_gradient_background,  # 垂直漸層
    draw_circle,                # 畫圓的輔助函式
    draw_text,                  # 簡單的文字繪製
    draw_star                   # 五角星
)
```

## 動畫概念

### 震動／顫抖
用振盪來偏移物件的位置：
- 搭配 frame 編號使用 `math.sin()` 或 `math.cos()`
- 加一點小的隨機變化，看起來比較自然
- 套用在 x 和（或）y 位置

### 脈動／心跳
讓物件大小有節奏地縮放：
- 用 `math.sin(t * frequency * 2 * math.pi)` 做平滑的脈動
- 心跳的話：快速兩下然後停頓（調整正弦波）
- 在基本大小的 0.8 到 1.2 倍之間縮放

### 彈跳
物件落下再彈起：
- 落地用 `interpolate()` 搭配 `easing='bounce_out'`
- 下墜（加速）用 `easing='ease_in'`
- 每個 frame 增加 y 方向的速度來模擬重力

### 旋轉
繞著中心旋轉物件：
- PIL：`image.rotate(angle, resample=Image.BICUBIC)`
- 要做搖晃的話：角度改用正弦波，不要用線性

### 淡入／淡出
逐漸出現或消失：
- 建立 RGBA 圖片，調整 alpha 通道
- 或用 `Image.blend(image1, image2, alpha)`
- 淡入：alpha 從 0 到 1
- 淡出：alpha 從 1 到 0

### 滑動
把物件從畫面外移動到定位：
- 起始位置：在畫面範圍之外
- 結束位置：目標位置
- 用 `interpolate()` 搭配 `easing='ease_out'`，讓停下來時比較平滑
- 想要衝過頭再回來：用 `easing='back_out'`

### 縮放
縮放並調整位置來做出放大縮小效果：
- 放大：縮放從 0.1 到 2.0，裁切中心
- 縮小：縮放從 2.0 到 1.0
- 可以加動態模糊來增加戲劇效果（PIL filter）

### 爆炸／粒子迸發
產生向外放射的粒子：
- 用隨機的角度和速度產生粒子
- 更新每個粒子：`x += vx`、`y += vy`
- 加上重力：`vy += gravity_constant`
- 讓粒子隨時間淡出（降低 alpha）

## 最佳化策略

只有在被要求把檔案縮小時，才從下面的方法裡挑幾個來做：

1. **減少 frame**：降低 FPS（用 10 而不是 20），或縮短長度
2. **減少顏色**：用 `num_colors=48` 而不是 128
3. **縮小尺寸**：用 128x128 而不是 480x480
4. **移除重複**：在 save() 裡設 `remove_duplicates=True`
5. **表情符號模式**：`optimize_for_emoji=True` 會自動最佳化

```python
# 表情符號的最大最佳化
builder.save(
    'emoji.gif',
    num_colors=48,
    optimize_for_emoji=True,
    remove_duplicates=True
)
```

## 理念

這個 skill 提供：
- **知識**：Slack 的要求和動畫概念
- **工具**：GIFBuilder、驗證器、緩動函式
- **彈性**：動畫邏輯由你自己用 PIL 基本繪圖功能來寫

它不提供：
- 死板的動畫範本或現成的函式
- 表情符號字型的繪製（跨平台不穩定）
- 內建在 skill 裡、預先打包好的圖形庫

**關於使用者上傳的說明**：這個 skill 不含預先做好的圖形，但如果使用者上傳了圖片，就用 PIL 載入並處理，依照他的要求判斷是要直接使用，還是只當靈感。

發揮創意！組合各種概念（彈跳加旋轉、脈動加滑動等等），把 PIL 的功能用到極致。

## 相依套件

```bash
pip install pillow imageio numpy
```
