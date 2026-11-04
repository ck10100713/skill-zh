---
name: nutrient-document-processing
description: 用 Nutrient DWS API 處理、轉換、OCR、擷取、遮蔽、簽署和填寫文件。支援 PDF、DOCX、XLSX、PPTX、HTML 和圖片。透過 Nutrient DWS API 轉換、OCR、擷取、遮蔽、簽署或填寫文件時使用。
metadata:
  origin: ECC
---

# Nutrient Document Processing

> **注意：** 這個 skill 整合的是 Nutrient 的商業 API。使用前請先看過他們的條款。

用 [Nutrient DWS Processor API](https://www.nutrient.io/api/) 處理文件。轉換格式、擷取文字和表格、對掃描文件做 OCR、遮蔽 PII、加浮水印、數位簽署，以及填寫 PDF 表單。

## Setup

到 **[nutrient.io](https://dashboard.nutrient.io/sign_up/?product=processor)** 免費取得 API key

```bash
export NUTRIENT_API_KEY="pdf_live_..."
```

所有請求都用 multipart POST 送到 `https://api.nutrient.io/build`，並帶一個 `instructions` JSON 欄位。

## Operations

### Convert Documents

```bash
# DOCX 轉 PDF
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.docx=@document.docx" \
  -F 'instructions={"parts":[{"file":"document.docx"}]}' \
  -o output.pdf

# PDF 轉 DOCX
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"output":{"type":"docx"}}' \
  -o output.docx

# HTML 轉 PDF
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "index.html=@index.html" \
  -F 'instructions={"parts":[{"html":"index.html"}]}' \
  -o output.pdf
```

支援的輸入：PDF、DOCX、XLSX、PPTX、DOC、XLS、PPT、PPS、PPSX、ODT、RTF、HTML、JPG、PNG、TIFF、HEIC、GIF、WebP、SVG、TGA、EPS。

### Extract Text and Data

```bash
# 擷取純文字
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"output":{"type":"text"}}' \
  -o output.txt

# 把表格擷取成 Excel
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"output":{"type":"xlsx"}}' \
  -o tables.xlsx
```

### OCR Scanned Documents

```bash
# OCR 成可搜尋的 PDF（支援 100 種以上語言）
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "scanned.pdf=@scanned.pdf" \
  -F 'instructions={"parts":[{"file":"scanned.pdf"}],"actions":[{"type":"ocr","language":"english"}]}' \
  -o searchable.pdf
```

語言：透過 ISO 639-2 代碼支援 100 種以上語言（例如 `eng`、`deu`、`fra`、`spa`、`jpn`、`kor`、`chi_sim`、`chi_tra`、`ara`、`hin`、`rus`）。像 `english` 或 `german` 這樣的完整語言名稱也可以用。所有支援的代碼請見[完整的 OCR 語言表](https://www.nutrient.io/guides/document-engine/ocr/language-support/)。

### Redact Sensitive Information

```bash
# 以樣式為基礎（SSN、email）
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"actions":[{"type":"redaction","strategy":"preset","strategyOptions":{"preset":"social-security-number"}},{"type":"redaction","strategy":"preset","strategyOptions":{"preset":"email-address"}}]}' \
  -o redacted.pdf

# 以 regex 為基礎
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"actions":[{"type":"redaction","strategy":"regex","strategyOptions":{"regex":"\\b[A-Z]{2}\\d{6}\\b"}}]}' \
  -o redacted.pdf
```

預設樣式：`social-security-number`、`email-address`、`credit-card-number`、`international-phone-number`、`north-american-phone-number`、`date`、`time`、`url`、`ipv4`、`ipv6`、`mac-address`、`us-zip-code`、`vin`。

### Add Watermarks

```bash
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"actions":[{"type":"watermark","text":"CONFIDENTIAL","fontSize":72,"opacity":0.3,"rotation":-45}]}' \
  -o watermarked.pdf
```

### Digital Signatures

```bash
# 自簽的 CMS 簽章
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "document.pdf=@document.pdf" \
  -F 'instructions={"parts":[{"file":"document.pdf"}],"actions":[{"type":"sign","signatureType":"cms"}]}' \
  -o signed.pdf
```

### Fill PDF Forms

```bash
curl -X POST https://api.nutrient.io/build \
  -H "Authorization: Bearer $NUTRIENT_API_KEY" \
  -F "form.pdf=@form.pdf" \
  -F 'instructions={"parts":[{"file":"form.pdf"}],"actions":[{"type":"fillForm","formFields":{"name":"Jane Smith","email":"jane@example.com","date":"2026-02-06"}}]}' \
  -o filled.pdf
```

## MCP Server (Alternative)

想要原生的工具整合，就用 MCP server 取代 curl：

```json
{
  "mcpServers": {
    "nutrient-dws": {
      "command": "npx",
      "args": ["-y", "@nutrient-sdk/dws-mcp-server"],
      "env": {
        "NUTRIENT_DWS_API_KEY": "YOUR_API_KEY",
        "SANDBOX_PATH": "/path/to/working/directory"
      }
    }
  }
}
```

## When to Use

- 在不同格式之間轉換文件（PDF、DOCX、XLSX、PPTX、HTML、圖片）
- 從 PDF 擷取文字、表格或鍵值對
- 對掃描文件或圖片做 OCR
- 分享文件之前遮蔽 PII
- 替草稿或機密文件加浮水印
- 對合約或協議做數位簽署
- 以程式填寫 PDF 表單

## Links

- [API Playground](https://dashboard.nutrient.io/processor-api/playground/)
- [Full API Docs](https://www.nutrient.io/guides/dws-processor/)
- [npm MCP Server](https://www.npmjs.com/package/@nutrient-sdk/dws-mcp-server)
