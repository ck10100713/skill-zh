---
name: image-processing
description: "處理網頁開發用的圖片：縮放、裁切、去除空白邊、轉換格式（PNG/WebP/JPG）、優化檔案大小、產生縮圖、製作 OG 卡片圖。使用 Pillow（Python），不需要 ImageMagick。用 'resize image'、'convert to webp'、'trim logo'、'optimise images'、'make thumbnail'、'create OG image'、'crop whitespace'、'process image' 或 'image too large' 觸發。"
compatibility: claude-code-only
---

# Image Processing

常見操作用 `img-process`（隨附在 `bin/`）。複雜或自訂的流程，就依使用者的環境產生一個 Pillow script。

## 速查：img-process CLI

```bash
img-process resize hero.png --width 1920
img-process convert logo.png --format webp
img-process trim logo-raw.jpg -o logo-clean.png --padding 10
img-process thumbnail photo.jpg --size 200
img-process optimise hero.jpg --quality 85 --max-width 1920
img-process og-card -o og.png --title "My App" --subtitle "Built for speed"
img-process batch ./images --action convert --format webp -o ./optimised
```

**用 `img-process` 的時機**：操作是標準的（縮放、轉換、去邊、縮圖、優化、OG 卡片、批次）。這樣比較快，也不用每次都產生 script。

**改產生自訂 script 的時機**：操作需要 `img-process` 沒涵蓋的邏輯（合成多張圖、浮水印、複雜的文字排版、條件式處理）。

## 前置條件

`img-process` 和自訂 script 都需要 Pillow：

```bash
pip install Pillow
```

如果沒有 Pillow，用這些替代方案：

| 替代方案 | 平台 | 安裝 | 最適合 |
|-------------|----------|---------|----------|
| `sips` | macOS（內建） | 不用裝 | 縮放、轉換（不能去邊/OG） |
| `sharp` | Node.js | `npm install sharp` | 功能完整、效能高 |
| `ffmpeg` | 跨平台 | `brew install ffmpeg` | 縮放、轉換 |

## 輸出格式指南

| 使用情境 | 格式 | 原因 |
|----------|--------|-----|
| 照片、hero 圖 | WebP | 壓縮最好，瀏覽器支援廣 |
| Logo、圖示（需要透明） | PNG | 無損，支援 alpha |
| 舊瀏覽器的 fallback | JPG | 通用支援 |
| 縮圖 | WebP 或 JPG | 以檔案小為優先 |
| OG 卡片 | PNG | 社群平台對 PNG 處理得最好 |

## 核心模式

### 依格式設定品質並儲存

不同格式的儲存參數不一樣。一定要處理 RGBA 轉 JPG 的合成，JPG 不支援透明，所以要先合成到白色背景上。

```python
from PIL import Image
import os

def save_image(img, output_path, quality=None):
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    kwargs = {}
    ext = output_path.lower().rsplit(".", 1)[-1]

    if ext == "webp":
        kwargs = {"quality": quality or 85, "method": 6}
    elif ext in ("jpg", "jpeg"):
        kwargs = {"quality": quality or 90, "optimize": True}
        # RGBA → RGB: composite onto white background
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img = bg
    elif ext == "png":
        kwargs = {"optimize": True}

    img.save(output_path, **kwargs)
```

### 保持長寬比縮放

只給寬或高其中一個時，用長寬比算出另一個。高品質縮小用 `Image.LANCZOS`。

```python
def resize_image(img, width=None, height=None):
    if width and height:
        return img.resize((width, height), Image.LANCZOS)
    elif width:
        ratio = width / img.width
        return img.resize((width, int(img.height * ratio)), Image.LANCZOS)
    elif height:
        ratio = height / img.height
        return img.resize((int(img.width * ratio), height), Image.LANCZOS)
    return img
```

### 去除空白邊（自動裁切）

移除 logo 和圖示周圍的空白。先轉成 RGBA，再用 `getbbox()` 找出內容的邊界。

```python
img = Image.open(input_path)
if img.mode != "RGBA":
    img = img.convert("RGBA")
bbox = img.getbbox()  # Bounding box of non-zero pixels
if bbox:
    img = img.crop(bbox)
```

### 縮圖

在最大尺寸內縮放，並保持長寬比：

```python
img.thumbnail((size, size), Image.LANCZOS)
```

### 為網頁優化

縮放 + 壓縮一步完成。轉成 WebP 可得到最好的壓縮。一般設定：寬度 1920、品質 85。

### 跨平台字型尋找

系統字型路徑因作業系統而異。試多個路徑，找不到就退回 Pillow 的預設字型。在 Linux 上可以用 `fc-list` 動態找字型。

```python
from PIL import ImageFont

def get_font(size):
    font_paths = [
        # macOS
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSText.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        # Windows
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()
```

### OG 卡片產生（1200x630）

把文字合成到背景圖或純色上。疊一層半透明遮罩讓文字好讀。文字水平置中。

```python
from PIL import Image, ImageDraw, ImageFont

width, height = 1200, 630

# Background: image or solid colour
if background_path:
    img = Image.open(background_path).resize((width, height), Image.LANCZOS)
else:
    img = Image.new("RGB", (width, height), bg_color or "#1a1a2e")

# Semi-transparent overlay for text readability
overlay = Image.new("RGBA", (width, height), (0, 0, 0, 128))
img = img.convert("RGBA")
img = Image.alpha_composite(img, overlay)

draw = ImageDraw.Draw(img)
font_title = get_font(48)
font_sub = get_font(24)

# Centre title
if title:
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw) // 2, height // 2 - 60), title, fill="white", font=font_title)

img = img.convert("RGB")
```

## 常見工作流程

### Logo 清理（客戶給的白底 JPG）

```bash
img-process trim logo-raw.jpg -o logo-trimmed.png --padding 10
img-process thumbnail logo-trimmed.png --size 512 -o favicon-512.png
```

### 準備上線用的 Hero 圖

```bash
img-process optimise hero.jpg --max-width 1920 --quality 85
# Outputs hero.webp — resized and compressed
```

### 批次處理

```bash
img-process batch ./raw-images --action convert --format webp --quality 85 -o ./optimised
img-process batch ./photos --action resize --width 800 -o ./thumbnails
```

### 搭配 Gemini 圖片生成的流程

先用 gemini-image-gen skill 產生圖片，再處理它們：

```bash
# After generating with Gemini (raw PNG output):
img-process optimise generated-image.png --max-width 1920 --quality 85
# Or batch process all generated images:
img-process batch ./generated --action optimise -o ./production
```
