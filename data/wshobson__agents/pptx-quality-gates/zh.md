---
name: pptx-quality-gates
description: "在驗證或修復可編輯的 PPTX 簡報，檢查幾何、無障礙、原生可編輯性、資料來源脈絡與 OOXML 套件完整性時使用。"
---

# PPTX Quality Gates

在交付產生出來的 PPTX 之前使用這個 skill。把確定性的失敗當成待修復的工作，不是例外。

## Workflow

1. 確認 spec、builder、PPTX、來源清單與稽核檔的路徑。
2. 在建置之前，把 `references/audit-checklist.md` 套用到座標契約上。
3. 重新開啟 PPTX，並把投影片張數、實際邊界、隱藏的投影片與要求的幾何，跟 layout tree 比對。
4. 正式環境的簡報要執行 `pptx-reference-deck-analysis/scripts/validate_package.py`，並儲存 JSON 報告。
5. 檢查文件語言、投影片標題、有意義圖片的替代文字、閱讀順序、表格標題列與來源參照。
6. 如果已經有相容的 renderer，就檢查預覽有沒有裁切、字型替換、對比、裁剪與層次的問題。不要額外加入 renderer 相依套件。
7. 修復 spec 或專案內的 builder、重新建置，並重跑同樣的檢查。

## Required artifacts

把 spec、PPTX、建置紀錄、幾何稽核、無障礙稽核、套件報告與來源清單放在一起。任何有記錄的例外都要回報，附上投影片 ID、物件 ID、負責人、原因與審查日期。

## Pass criteria

內容碰撞、文字溢出、不安全的內容邊界、無效的正向幾何與套件完整性錯誤都必須是零。有意義的投影片內容必須維持是原生可編輯的物件，圖片只能輔助，不能取代它。

完整的檢查清單見 `references/audit-checklist.md`。
