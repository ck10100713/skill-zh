---
name: xlsx-author
description: 在磁碟上產出 .xlsx 檔案（headless），而不是操作開著的 Excel 活頁簿。適用於沒有開啟 Office app 的 managed-agent session。
---

# xlsx-author

在 **headless** 模式（managed-agent / CMA 模式）下執行，而且需要把 Excel 活頁簿當成**檔案成品**交付，而不是透過 `mcp__office__excel_*` 編輯開著的活頁簿時，就用這個 skill。

## 輸出約定

- 寫到 `./out/<name>.xlsx`。如果 `./out/` 不存在就建立它。
- 在最後的訊息裡回傳相對路徑，讓編排層可以收走檔案。

## 怎麼建立活頁簿

寫一個簡短的 Python script，用 Bash 執行。使用 `openpyxl`：

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

wb = Workbook()
ws = wb.active; ws.title = "Inputs"
ws["B2"] = "Revenue"; ws["C2"] = 1_250_000_000
ws["C2"].font = Font(color="0000FF")           # blue = hardcoded input
calc = wb.create_sheet("DCF")
calc["C5"] = "=Inputs!C2*(1+Inputs!C3)"        # black = formula
wb.save("./out/model.xlsx")
```

## 慣例（比照 `audit-xls`）

- **藍／黑／綠。** 藍 = 寫死的輸入、黑 = 公式、綠 = 連到其他工作表／檔案的連結。
- **計算儲存格不准有寫死的值。** 每個計算儲存格都是公式；每個輸入都放在 Inputs 分頁。
- 任何會被簡報或備忘錄引用的值，都要用**具名範圍**。
- **平衡檢查。** 放一個 Checks 分頁，檢查是否勾稽（資產負債表平衡、現金流量表對得上現金等），並顯示 TRUE/FALSE。
- **一個檔案一個模型。** 除非明確要求，不要往現有活頁簿裡追加內容。

## 什麼時候不要用

如果有 `mcp__office__excel_*` 工具可用（Cowork plugin 模式），就改用那些，它們會操作使用者開著的活頁簿，並有審查檢查點。這個 skill 只是 headless 執行時產出檔案的備案。
