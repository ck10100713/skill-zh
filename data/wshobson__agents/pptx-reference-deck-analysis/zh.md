---
name: pptx-reference-deck-analysis
description: "在以唯讀方式分析參考用 PPTX 的結構、主題、字體排版、版面節奏、診斷資訊、衍生的範本目錄，或安全地檢查 OOXML 套件時使用。"
---

# PPTX Reference Deck Analysis

把參考簡報當成設計證據來檢視。這個 skill 絕不複製、cloning 或修改來源簡報。

## Contract

需要擷取時，就用一支小型的、專案內的 `python-pptx` 腳本即時實作。只擷取新簡報所需的資訊：

- 精簡的 prompt context：投影片張數與尺寸、文字摘要、形狀數量、樣式、品牌訊號、範本使用情形與版面節奏；
- 完整擷取：`summary`、投影片，以及唯讀的 `layout_tree` 證據；
- 資料夾診斷：每份簡報一筆結果，加上一份 manifest；
- 樣式母片分析：顏色、字型、大小分布、母片/版面的使用，以及流程模式；
- 衍生的範本目錄：從 0 起算的來源索引、版面角色、可用區域、placeholder、視覺結構與限制。

## Rules

- 讓來源簡報保持唯讀，並獨立撰寫每個目標投影片的座標。
- 只有在高階擷取無法取得原始的主題、relationship、備註、註解、動畫、媒體、母片或版面時，才使用內附的 OOXML 工具。
- 把檢查過的 part 與解析時的例外記錄在分析 manifest 裡。
- 沒有明確的許可與授權證據，就不要把擷取出來的內容、字型、圖片或專有素材用在產生的簡報裡。

## OOXML package inspection

使用內附的工具之前，先從 `requirements.txt` 安裝 `defusedxml`。

1. 執行 `scripts/inspect.py <deck.pptx>`，取得精簡的 JSON 報告，內容包含投影片順序、文字、主題 token、relationship、備註、註解、動畫與媒體。
2. 執行 `scripts/validate_package.py <deck.pptx> --output <report.json>`，檢查格式錯誤的 XML、壞掉的內部 relationship、content-type 缺漏、重複的 layout 連結與孤立的 part。
3. 只有在需要原始套件證據時，才執行 `scripts/unpack.py <deck.pptx> <output-dir>`。
4. relationship 的目標要相對於 `.rels` 的擁有者來解析；絕對不要從檔名推斷投影片順序。

### Safety

- 絕對不要修改提供的簡報，也不要不加判斷就把套件 part 複製到新簡報。
- 在受信任的工作區執行這些腳本；它們會拒絕 path traversal、symlink、過大的成員與壓縮炸彈。
- 用 `defusedxml` 解析不受信任的 XML；不要啟用 entity 展開、DTD 載入或網路存取。
- 除非已經對照色彩配置完整解析，否則把主題色當成 token 處理。

輸出的形狀見 `references/reference-deck-analysis.md`，僅供文件參考的模式見 `references/reference-deck-analysis-patterns.md`，套件 part 的對照圖見 `references/ooxml-parsing.md`。
