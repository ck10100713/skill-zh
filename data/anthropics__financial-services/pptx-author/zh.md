---
name: pptx-author
description: 在磁碟上產出 .pptx 檔案（headless），而不是操作開著的 PowerPoint 文件。適用於沒有開啟 Office app 的 managed-agent session。
---

# pptx-author

在 **headless** 模式（managed-agent / CMA 模式）下執行，而且需要把 PowerPoint 簡報當成**檔案成品**交付，而不是透過 `mcp__office__powerpoint_*` 編輯開著的文件時，就用這個 skill。

## 輸出約定

- 寫到 `./out/<name>.pptx`。如果 `./out/` 不存在就建立它。
- 在最後的訊息裡回傳相對路徑，讓編排層可以收走檔案。

## 怎麼建立簡報

寫一個簡短的 Python script，用 Bash 執行。使用 `python-pptx`：

```python
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation("./templates/firm-template.pptx")  # 如果有提供範本
# or: prs = Presentation()

slide = prs.slides.add_slide(prs.slide_layouts[5])    # title-only
slide.shapes.title.text = "Valuation Summary"
# ... add tables / charts / text boxes ...

prs.save("./out/pitch-<target>.pptx")
```

## 慣例（比照即時 Office 版的 `pitch-deck` skill）

- **一張投影片一個重點。** 標題講結論，內文支撐它。
- **每個數字都要能追溯到模型。** 如果數字來自 `./out/model.xlsx`，在註腳註明工作表和儲存格。
- **`./templates/` 有掛載公司範本就用它**，沒有的話用預設版面配置。
- **圖表**：需要高擬真度時，優先嵌入從模型渲染出來的 PNG，不要用 pptx 原生圖表。
- **不對外傳送。** 這個 skill 只寫檔案，絕對不會寄信或上傳。

## 什麼時候不要用

如果有 `mcp__office__powerpoint_*` 工具可用（Cowork plugin 模式），就改用那些，它們會操作使用者開著的文件，並有審查檢查點。這個 skill 只是 headless 執行時產出檔案的備案。
