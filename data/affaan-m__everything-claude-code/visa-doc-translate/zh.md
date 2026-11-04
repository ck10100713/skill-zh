---
name: visa-doc-translate
description: 透過 OCR 把簽證文件圖片（銀行存款證明、在職證明、收入證明、退休證明；HEIC、PNG 或 JPG）翻成英文，並產出雙語 PDF，把原始圖片和格式化的認證風格譯文放在一起。簽證申請需要把文件翻成英文、對官方證明做 OCR 與翻譯，或需要移民文件用的雙語翻譯 PDF 時使用。
---

你在協助翻譯簽證申請用的文件。

## 指示

當使用者提供圖片檔案路徑時，**自動**執行以下步驟，**不要**先問確認：

1. **圖片轉檔**：如果檔案是 HEIC，用 `sips -s format png <input> --out <output>` 轉成 PNG

2. **圖片旋轉**：
   - 檢查 EXIF 方向資料
   - 依 EXIF 資料自動旋轉圖片
   - 如果 EXIF 方向是 6，逆時針轉 90 度
   - 視需要再多轉（文件看起來上下顛倒就試 180 度）

3. **OCR 文字擷取**：
   - 自動嘗試多種 OCR 方法：
     - macOS Vision framework（macOS 優先）
     - EasyOCR（跨平台，不需要 tesseract）
     - Tesseract OCR（有裝的話）
   - 擷取文件上所有文字資訊
   - 辨識文件類型（存款證明、在職證明、退休證明等）

4. **翻譯**：
   - 把所有文字內容專業地翻成英文
   - 保持原文件的結構與格式
   - 使用適合簽證申請的專業用語
   - 專有名詞保留原文，英文放在括號裡
   - 中文姓名用拼音格式（例如 WU Zhengye）
   - 所有數字、日期、金額都要精確保留

5. **PDF 產生**：
   - 用 PIL 和 reportlab 寫一支 Python script
   - 第 1 頁：顯示旋轉後的原始圖片，置中並縮放到符合 A4 頁面
   - 第 2 頁：顯示排版整齊的英文譯文：
     - 標題置中、粗體
     - 內文靠左，間距適當
     - 適合正式文件的專業版面
   - 在底部加註："This is a certified English translation of the original document"
   - 執行 script 產生 PDF

6. **輸出**：在同一個資料夾建立名為 `<original_filename>_Translated.pdf` 的 PDF 檔

## 支援的文件

- 銀行存款證明（存款证明）
- 收入證明（收入证明）
- 在職證明（在职证明）
- 退休證明（退休证明）
- 房產證明（房产证明）
- 營業執照（营业执照）
- 身分證與護照
- 其他官方文件

## 技術實作

### OCR 方法（依序嘗試）

1. **macOS Vision Framework**（僅限 macOS）：
   ```python
   import Vision
   from Foundation import NSURL
   ```

2. **EasyOCR**（跨平台）：
   ```bash
   pip install easyocr
   ```

3. **Tesseract OCR**（有裝的話）：
   ```bash
   brew install tesseract tesseract-lang
   pip install pytesseract
   ```

### 需要的 Python 函式庫

```bash
pip install pillow reportlab
```

macOS Vision framework 要另外裝：
```bash
pip install pyobjc-framework-Vision pyobjc-framework-Quartz
```

## 重要準則

- **不要**每個步驟都問使用者確認
- 自動判斷最合適的旋轉角度
- 一種 OCR 方法失敗就換下一種
- 確保所有數字、日期、金額都翻譯正確
- 排版乾淨、專業
- 把整個流程做完，並回報最終 PDF 的位置

## 使用範例

```bash
/visa-doc-translate RetirementCertificate.PNG
/visa-doc-translate BankStatement.HEIC
/visa-doc-translate EmploymentLetter.jpg
```

## 輸出範例

這個 skill 會：
1. 用可用的 OCR 方法擷取文字
2. 翻成專業的英文
3. 產生 `<filename>_Translated.pdf`，內容包含：
   - 第 1 頁：原始文件圖片
   - 第 2 頁：專業英文譯文

很適合用在澳洲、美國、加拿大、英國，以及其他要求附上翻譯文件的國家的簽證申請。
