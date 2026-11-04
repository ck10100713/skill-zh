---
name: instrument-data-to-allotrope
description: 把實驗室儀器輸出檔（PDF、CSV、Excel、TXT）轉成 Allotrope Simple Model（ASM）JSON 格式，或攤平成 2D CSV。當科學家需要把儀器資料標準化，以便匯入 LIMS 系統、data lake 或做後續分析時使用。支援自動偵測儀器類型。輸出包含完整的 ASM JSON、方便匯入的攤平 CSV，以及給資料工程師用、可匯出的 Python 程式碼。常見的觸發情境包括轉換儀器檔案、標準化實驗室資料、準備資料上傳到 LIMS/ELN 系統，或是為正式的 pipeline 產生 parser 程式碼。
---

# Instrument Data to Allotrope Converter

把儀器檔案轉成標準化的 Allotrope Simple Model（ASM）格式，用於上傳 LIMS、data lake，或交接給資料工程團隊。

> **注意：這是一個範例 Skill**
>
> 這個 skill 示範 skill 如何支援你的資料工程工作：自動做 schema 轉換、解析儀器輸出、產生可上線的程式碼。
>
> **要依你的組織客製化：**
> - 修改 `references/` 底下的檔案，放進貴公司特有的 schema 或 ontology 對應
> - 用 MCP server 連到定義你們 schema 的系統（例如你的 LIMS、資料目錄，或 schema registry）
> - 擴充 `scripts/` 來處理專有的儀器格式或內部資料標準
>
> 這個模式可以套用到任何需要在格式之間轉換、或依組織標準做驗證的資料轉換流程。

## 工作流程總覽

1. **偵測儀器類型**，從檔案內容判斷（自動偵測或由使用者指定）
2. **解析檔案**，用 allotropy 函式庫（原生）或彈性的備援 parser
3. **產生輸出**：
   - ASM JSON（完整的語意結構）
   - 攤平的 CSV（2D 表格格式）
   - Python parser 程式碼（交接給資料工程師用）
4. **交付**檔案，附上摘要和使用說明

> **不確定的時候：** 如果你不確定某個欄位要怎麼對應到 ASM（例如這是原始資料還是計算出來的？是設備設定還是環境條件？），就問使用者釐清。可以參考 `references/field_classification_guide.md`，但還是有歧義時，就跟使用者確認，不要用猜的。

## 快速開始

```python
# 先安裝需要的套件
pip install allotropy pandas openpyxl pdfplumber --break-system-packages

# 核心轉換
from allotropy.parser_factory import Vendor
from allotropy.to_allotrope import allotrope_from_file

# 用 allotropy 轉換
asm = allotrope_from_file("instrument_data.csv", Vendor.BECKMAN_VI_CELL_BLU)
```

## 輸出格式的選擇

**ASM JSON（預設）**：帶有 ontology URI 的完整語意結構
- 最適合：預期收到 ASM 的 LIMS 系統、data lake、長期封存
- 會依 Allotrope schema 驗證

**攤平的 CSV**：2D 表格呈現
- 最適合：快速分析、Excel 使用者、不支援 JSON 的系統
- 每筆量測變成一列，metadata 重複出現在每一列

**兩者都要**：兩種格式都產生，彈性最大

## 計算資料的處理

**重要：** 要把原始量測值和計算出來的衍生值分開。

- **原始資料** → `measurement-document`（儀器直接讀到的數值）
- **計算資料** → `calculated-data-aggregate-document`（衍生值）

計算值一定要透過 `data-source-aggregate-document` 保留可追溯性：

```json
"calculated-data-aggregate-document": {
  "calculated-data-document": [{
    "calculated-data-identifier": "SAMPLE_B1_DIN_001",
    "calculated-data-name": "DNA integrity number",
    "calculated-result": {"value": 9.5, "unit": "(unitless)"},
    "data-source-aggregate-document": {
      "data-source-document": [{
        "data-source-identifier": "SAMPLE_B1_MEASUREMENT",
        "data-source-feature": "electrophoresis trace"
      }]
    }
  }]
}
```

**各儀器類型常見的計算欄位：**
| 儀器 | 計算欄位 |
|------------|-------------------|
| 細胞計數儀 | 存活率 %、經稀釋校正的細胞密度值 |
| 分光光度計 | 濃度（由吸光度算出）、260/280 比值 |
| 微孔盤讀取儀 | 由標準曲線算出的濃度、%CV |
| 電泳 | DIN/RIN、各區段濃度、平均大小 |
| qPCR | 相對定量、倍數變化 |

原始值與計算值怎麼分類，詳細說明請看 `references/field_classification_guide.md`。

## 驗證

交給使用者之前，一定要先驗證 ASM 輸出：

```bash
python scripts/validate_asm.py output.json
python scripts/validate_asm.py output.json --reference known_good.json  # 跟參考檔比對
python scripts/validate_asm.py output.json --strict  # 把警告當成錯誤
```

**驗證規則：**
- 依據 Allotrope ASM 規格（2024 年 12 月）
- 最後更新：2026-01-07
- 來源：https://gitlab.com/allotrope-public/asm

**柔性驗證方式：**
未知的技術、單位或樣本角色只會產生**警告**（不是錯誤），以保留向前相容性。如果 Allotrope 在 2024 年 12 月之後新增了值，驗證器不會擋掉，而是標出來請人工確認。需要更嚴格的驗證時，用 `--strict` 模式把警告當成錯誤。

**檢查項目：**
- 技術選擇是否正確（例如 multi-analyte profiling 對比 plate reader）
- 欄位命名慣例（用空格分隔，不是連字號）
- 計算資料有可追溯性（`data-source-aggregate-document`）
- 量測值和計算值都有唯一識別碼
- 必要的 metadata 都在
- 單位和樣本角色有效（未知值用柔性驗證）

## 支援的儀器

完整清單請看 `references/supported_instruments.md`。主要儀器：

| 類別 | 儀器 |
|----------|-------------|
| 細胞計數 | Vi-CELL BLU、Vi-CELL XR、NucleoCounter |
| 分光光度法 | NanoDrop One/Eight/8000、Lunatic |
| 微孔盤讀取儀 | SoftMax Pro、EnVision、Gen5、CLARIOstar |
| ELISA | SoftMax Pro、BMG MARS、MSD Workbench |
| qPCR | QuantStudio、Bio-Rad CFX |
| 層析 | Empower、Chromeleon |

## 偵測與解析策略

### 第 1 層：allotropy 原生解析（優先使用）
**一定先試 allotropy。** 直接檢查有哪些可用的 vendor：

```python
from allotropy.parser_factory import Vendor

# 列出所有支援的 vendor
for v in Vendor:
    print(f"{v.name}")

# 常見的 vendor：
# AGILENT_TAPESTATION_ANALYSIS  (for TapeStation XML)
# BECKMAN_VI_CELL_BLU
# THERMO_FISHER_NANODROP_EIGHT
# MOLDEV_SOFTMAX_PRO
# APPBIO_QUANTSTUDIO
# ... many more
```

**使用者提供檔案時，先確認 allotropy 支不支援，再退回手動解析。** `scripts/convert_to_asm.py` 的自動偵測只涵蓋 allotropy vendor 的一部分。

### 第 2 層：彈性備援解析
**只有 allotropy 不支援該儀器時才用。** 這個備援方式：
- 不會產生 `calculated-data-aggregate-document`
- 不包含完整的可追溯性
- 產出簡化的 ASM 結構

彈性 parser 的做法：
- 欄位名稱模糊比對
- 從標題列擷取單位
- 從檔案結構擷取 metadata

### 第 3 層：PDF 擷取
對只有 PDF 的檔案，先用 pdfplumber 擷取表格，再套用第 2 層的解析。

## 解析前的檢查清單

寫自訂 parser 之前，一定要：

1. **確認 allotropy 支不支援**：有原生 parser 就用原生的
2. **找一份參考的 ASM 檔**：查 `references/examples/` 或問使用者
3. **看儀器專屬的指南**：查 `references/instrument_guides/`
4. **跟參考檔驗證**：執行 `validate_asm.py --reference <file>`

## 要避免的常見錯誤

| 錯誤 | 正確做法 |
|---------|------------------|
| Manifest 用物件 | 用 URL 字串 |
| 偵測類型用小寫 | 用 "Absorbance"，不要用 "absorbance" |
| "emission wavelength setting" | emission 要用 "detector wavelength setting" |
| 所有量測放在同一個文件 | 依孔位或樣本位置分組 |
| 缺少程序的 metadata | 每筆量測都要擷取所有設備設定 |

## 給資料工程師的程式碼匯出

產生獨立的 Python 腳本，讓科學家可以交接出去：

```python
# 匯出 parser 程式碼
python scripts/export_parser.py --input "data.csv" --vendor "VI_CELL_BLU" --output "parser_script.py"
```

匯出的腳本：
- 除了 pandas/allotropy 以外沒有其他外部相依套件
- 內含行內文件
- 可以在 Jupyter notebook 裡跑
- 可直接用於資料 pipeline 上線

## 檔案結構

```
instrument-data-to-allotrope/
├── SKILL.md                          # 就是這個檔案
├── scripts/
│   ├── convert_to_asm.py            # 主要轉換腳本
│   ├── flatten_asm.py               # ASM → 2D CSV 轉換
│   ├── export_parser.py             # 產生獨立的 parser 程式碼
│   └── validate_asm.py              # 驗證 ASM 輸出品質
└── references/
    ├── supported_instruments.md     # 完整儀器清單與 Vendor enum
    ├── asm_schema_overview.md       # ASM 結構參考
    ├── field_classification_guide.md # 不同類型的欄位該放哪裡
    └── flattening_guide.md          # 攤平的運作方式
```

## 使用範例

### 範例 1：Vi-CELL BLU 檔案
```
User: "把這份細胞計數資料轉成 Allotrope 格式"
[上傳 viCell_Results.xlsx]

Claude:
1. 偵測到 Vi-CELL BLU（信心度 95%）
2. 用 allotropy 原生 parser 轉換
3. 輸出：
   - viCell_Results_asm.json（完整 ASM）
   - viCell_Results_flat.csv（2D 格式）
   - viCell_parser.py（可匯出的程式碼）
```

### 範例 2：要求交接程式碼
```
User: "我需要給我們的資料工程師一份解析 NanoDrop 檔案的程式碼"

Claude:
1. 產生自成一體的 Python 腳本
2. 附上範例輸入和輸出
3. 記錄所有假設
4. 提供 Jupyter notebook 版本
```

### 範例 3：可直接匯入 LIMS 的攤平輸出
```
User: "把這份 ELISA 資料轉成可以上傳到我們 LIMS 的 CSV"

Claude:
1. 解析微孔盤讀取儀資料
2. 產生攤平的 CSV，欄位包含：
   - sample_identifier, well_position, measurement_value, measurement_unit
   - instrument_serial_number, analysis_datetime, assay_type
3. 依常見的 LIMS 匯入需求驗證
```

## 實作筆記

### 安裝 allotropy
```bash
pip install allotropy --break-system-packages
```

### 處理解析失敗
如果 allotropy 原生解析失敗：
1. 記錄錯誤以便除錯
2. 退回彈性 parser
3. 向使用者回報 metadata 完整度降低
4. 建議從儀器匯出其他格式

### ASM Schema 驗證
有 schema 可用時，依 Allotrope schema 驗證輸出：
```python
import jsonschema
# Schema URL 在 references/asm_schema_overview.md
```
