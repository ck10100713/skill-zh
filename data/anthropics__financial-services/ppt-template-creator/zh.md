---
name: ppt-template-creator
description: 從使用者提供的 PowerPoint 範本建立自給自足的 PPT 範本 SKILL（不是簡報）。只有在使用者想把自己的範本做成可重複使用的 skill 時才用。要建立實際的簡報，請改用 pptx skill。
---

# PPT 範本建立器

**這個 skill 建立的是 SKILL，不是簡報。** 當使用者想把自己的 PowerPoint 範本變成之後可以重複產生簡報的 skill 時，才用這個。如果使用者只是要做一份簡報，請改用 `pptx` skill。

產生出來的 skill 包含：
- `assets/template.pptx`：範本檔
- `SKILL.md`：完整的使用說明（不需要再參照這個 meta skill）

**關於建立 skill 的一般最佳實務**，請參考 `skill-creator` skill。這個 skill 只專注在 PPT 專屬的做法。

## 工作流程

1. **使用者提供範本**（.pptx 或 .potx）
2. **分析範本**：萃取版面配置、佔位符、尺寸
3. **初始化 skill**：用 `skill-creator` skill 建立 skill 的結構
4. **加入範本**：把 .pptx 複製到 `assets/template.pptx`
5. **撰寫 SKILL.md**：照下面的範本，填入 PPT 專屬的細節
6. **建立範例**：產生一份範例簡報來驗證
7. **打包**：用 `skill-creator` skill 打包成 .skill 檔

## 步驟 2：分析範本

**關鍵：要萃取精確的佔位符位置**，這決定了內容區域的邊界。

```python
from pptx import Presentation

prs = Presentation(template_path)
print(f"Dimensions: {prs.slide_width/914400:.2f}\" x {prs.slide_height/914400:.2f}\"")
print(f"Layouts: {len(prs.slide_layouts)}")

for idx, layout in enumerate(prs.slide_layouts):
    print(f"\n[{idx}] {layout.name}:")
    for ph in layout.placeholders:
        try:
            ph_idx = ph.placeholder_format.idx
            ph_type = ph.placeholder_format.type
            # 重要：以英吋為單位萃取精確位置
            left = ph.left / 914400
            top = ph.top / 914400
            width = ph.width / 914400
            height = ph.height / 914400
            print(f"    idx={ph_idx}, type={ph_type}")
            print(f"        x={left:.2f}\", y={top:.2f}\", w={width:.2f}\", h={height:.2f}\"")
        except:
            pass
```

**要記錄的關鍵尺寸：**
- **標題位置**：標題佔位符在哪裡？
- **副標題／說明**：副標題那一行在哪裡？
- **頁尾佔位符**：頁尾／來源出現在哪裡？
- **內容區域**：副標題和頁尾「之間」的空間就是你的內容區域

### 找出內容真正的起始位置

**關鍵：** 內容區域不一定緊接在副標題佔位符之後開始。很多範本在副標題和內容區域之間有視覺邊框、線條或保留空間。

**最佳做法：** 找 Layout 2 或類似、有 OBJECT 佔位符的「內容」版面配置，這個佔位符的 `y` 位置就是內容實際該開始的地方。

```python
# 找出 OBJECT 佔位符，以決定內容真正的起始位置
for idx, layout in enumerate(prs.slide_layouts):
    for ph in layout.placeholders:
        try:
            if ph.placeholder_format.type == 7:  # OBJECT type
                top = ph.top / 914400
                print(f"Layout [{idx}] {layout.name}: OBJECT starts at y={top:.2f}\"")
                # 這個 y 值就是你的內容該開始的位置！
        except:
            pass
```

**範例：** 某個範本可能是：
- 副標題結束在 y=1.38"
- 但 OBJECT 佔位符從 y=1.90" 開始
- 中間的空隙（0.52"）是保留給邊框／線條用的，**不要把內容放進去**

內容起始位置要用 OBJECT 佔位符的 `y`，不要用副標題的結束位置。

## 步驟 5：撰寫 SKILL.md

產生出來的 skill 應該有這個結構：
```
[company]-ppt-template/
├── SKILL.md
└── assets/
    └── template.pptx
```

### 產生的 SKILL.md 範本

產生的 SKILL.md 必須**自給自足**，所有說明都內嵌在裡面。使用下面這個範本，把方括號的值用你分析的結果填進去：

````markdown
---
name: [company]-ppt-template
description: [Company] PowerPoint template for creating presentations. Use when creating [Company]-branded pitch decks, board materials, or client presentations.
---

# [Company] PPT Template

Template: `assets/template.pptx` ([WIDTH]" x [HEIGHT]", [N] layouts)

## Creating Presentations

```python
from pptx import Presentation

prs = Presentation("path/to/skill/assets/template.pptx")

# DELETE all existing slides first
while len(prs.slides) > 0:
    rId = prs.slides._sldIdLst[0].rId
    prs.part.drop_rel(rId)
    del prs.slides._sldIdLst[0]

# Add slides from layouts
slide = prs.slides.add_slide(prs.slide_layouts[LAYOUT_IDX])
```

## Key Layouts

| Index | Name | Use For |
|-------|------|---------|
| [0] | [Layout Name] | [Cover/title slide] |
| [N] | [Layout Name] | [Content with bullets] |
| [N] | [Layout Name] | [Two-column layout] |

## Placeholder Mapping

**CRITICAL: Include exact positions (x, y coordinates) for each placeholder.**

### Layout [N]: [Name]
| idx | Type | Position | Use |
|-----|------|----------|-----|
| [idx] | TITLE (1) | y=[Y]" | Slide title |
| [idx] | BODY (2) | y=[Y]" | Subtitle/description |
| [idx] | BODY (2) | y=[Y]" | Footer |
| [idx] | BODY (2) | y=[Y]" | Source/notes |

### Content Area Boundaries

**Document the safe content area for custom shapes/tables/charts:**

```
Content Area (for Layout [N]):
- Left margin: [X]" (content starts here)
- Top: [Y]" (below subtitle placeholder)
- Width: [W]"
- Height: [H]" (ends before footer)

For 4-quadrant layouts:
- Left column: x=[X]", width=[W]"
- Right column: x=[X]", width=[W]"
- Top row: y=[Y]", height=[H]"
- Bottom row: y=[Y]", height=[H]"
```

**Why this matters:** Custom content (textboxes, tables, charts) must stay within these boundaries to avoid overlapping with template placeholders like titles, footers, and source lines.

## Filling Content

**Do NOT add manual bullet characters** - slide master handles formatting.

```python
# Fill title
for shape in slide.shapes:
    if hasattr(shape, 'placeholder_format'):
        if shape.placeholder_format.type == 1:  # TITLE
            shape.text = "Slide Title"

# Fill content with hierarchy (level 0 = header, level 1 = bullet)
for shape in slide.shapes:
    if hasattr(shape, 'placeholder_format'):
        idx = shape.placeholder_format.idx
        if idx == [CONTENT_IDX]:
            tf = shape.text_frame
            for para in tf.paragraphs:
                para.clear()

            content = [
                ("Section Header", 0),
                ("First bullet point", 1),
                ("Second bullet point", 1),
            ]

            tf.paragraphs[0].text = content[0][0]
            tf.paragraphs[0].level = content[0][1]
            for text, level in content[1:]:
                p = tf.add_paragraph()
                p.text = text
                p.level = level
```

## Example: Cover Slide

```python
slide = prs.slides.add_slide(prs.slide_layouts[[COVER_IDX]])
for shape in slide.shapes:
    if hasattr(shape, 'placeholder_format'):
        idx = shape.placeholder_format.idx
        if idx == [TITLE_IDX]:
            shape.text = "Company Name"
        elif idx == [SUBTITLE_IDX]:
            shape.text = "Presentation Title | Date"
```

## Example: Content Slide

```python
slide = prs.slides.add_slide(prs.slide_layouts[[CONTENT_IDX]])
for shape in slide.shapes:
    if hasattr(shape, 'placeholder_format'):
        ph_type = shape.placeholder_format.type
        idx = shape.placeholder_format.idx
        if ph_type == 1:
            shape.text = "Executive Summary"
        elif idx == [BODY_IDX]:
            tf = shape.text_frame
            for para in tf.paragraphs:
                para.clear()
            content = [
                ("Key Findings", 0),
                ("Revenue grew 40% YoY to $50M", 1),
                ("Expanded to 3 new markets", 1),
                ("Recommendation", 0),
                ("Proceed with strategic initiative", 1),
            ]
            tf.paragraphs[0].text = content[0][0]
            tf.paragraphs[0].level = content[0][1]
            for text, level in content[1:]:
                p = tf.add_paragraph()
                p.text = text
                p.level = level
```
````

## 步驟 6：建立範例輸出

產生一份範例簡報來驗證這個 skill 能用。把它跟 skill 放在一起，當作參考。

## 產生的 skill 要遵守的 PPT 專屬規則

1. **範本放在 assets/**：一定要把 .pptx 檔一起打包
2. **SKILL.md 自給自足**：所有說明都內嵌，不參照外部檔案
3. **不要手動加項目符號**：用 `paragraph.level` 表示階層
4. **先刪投影片**：加新投影片之前，一定要先清掉現有的投影片
5. **用 idx 記錄佔位符**：佔位符的 idx 值是各範本專屬的
