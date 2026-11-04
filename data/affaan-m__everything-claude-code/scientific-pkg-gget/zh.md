---
name: scientific-pkg-gget
description: 用 gget CLI 與 Python 工作流程快速查詢基因體資料庫、序列、BLAST 類型搜尋、富集檢查，並留下可重現的生物資訊證據紀錄。任務需要用 gget CLI 或 Python 套件，在基因體參考資料庫之間快速做生物資訊查找時使用。
metadata:
  origin: community
---

# gget

任務需要用 `gget` CLI 或 Python 套件，在基因體參考資料庫之間快速做生物資訊查找時，使用這個 skill。

## 何時使用

- 找 Ensembl ID、基因 metadata、轉錄本細節或序列。
- 不用建完整的本地 pipeline，就快速跑 BLAST 或 BLAT 查找。
- 從 Ensembl 取得參考基因體連結和註解。
- 透過單一介面查詢蛋白質結構、pathway、癌症、表現量或疾病關聯模組。
- 在轉用 Biopython、Snakemake、Nextflow、BLAST+ 或資料庫專用 client 等較重的工具之前，先建立可重現的第一輪證據紀錄。

任務需要受監管的臨床判讀、高吞吐量的正式 pipeline，或需要精細控制資料庫版本與本地索引時，改用專屬的工作流程，不要用 `gget`。

## 安裝

用乾淨的 Python 環境。

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --upgrade gget
gget --help
```

有 `uv` 的話：

```bash
uv venv
. .venv/bin/activate
uv pip install gget
```

依賴比較舊的環境之前，先升級 `gget` 並重新確認模組文件。`gget` 查詢的上游資料庫會隨時間改變。

## 基本模式

CLI 的形式：

```bash
gget <module> [arguments] [options]
```

Python 的形式：

```python
import gget

result = gget.search(["BRCA1"], species="human")
print(result)
```

常見流程：

1. 確定需要的物種、組裝版本、基因 ID 類型和資料庫。
2. 查看目前的模組文件，確認參數。
3. 先跑一個小查詢。
4. 輸出存成有明確檔名和日期的檔案。
5. 記錄模組名稱、版本、參數和對資料庫的假設。

## 常用模組

精確的參數請看最新的上游文件。這些模組是常見的首選：

- `gget search`：用搜尋詞找 Ensembl ID。
- `gget info`：取得 Ensembl、UniProt 或相關 ID 的 metadata。
- `gget seq`：抓取核苷酸或胺基酸序列。
- `gget ref`：取得參考基因體的下載連結。
- `gget blast`：跑快速的 BLAST 查詢。
- `gget blat`：在支援的基因體組裝版本中定位序列。
- `gget muscle`：執行多序列比對。
- `gget diamond`：對參考序列執行本地序列比對。
- `gget alphafold` 和 `gget pdb`：查看蛋白質結構的參考資料。
- `gget enrichr`、`gget opentargets`、`gget archs4`、`gget bgee`、`gget cbio` 和 `gget cosmic`：探索富集、標靶、表現量、癌症和疾病關聯資料。

不要假設每個模組都支援每個 Python 版本或每組相依套件。有些選用的科學計算相依套件，支援的版本範圍比核心套件窄。

## 快速範例

找基因：

```bash
gget search -s human brca1 dna repair -o brca1-search.json
```

取得基因 metadata：

```bash
gget info ENSG00000012048 -o brca1-info.json
```

抓序列：

```bash
gget seq ENSG00000012048 -o brca1-seq.fa
```

跑一個小的 BLAST 查詢：

```bash
gget blast "MEEPQSDPSVEPPLSQETFSDLWKLLPEN" -l 10 -o blast-results.json
```

Python 範例：

```python
import gget

genes = gget.search(["BRCA1", "DNA repair"], species="human")
info = gget.info(["ENSG00000012048"])
sequence = gget.seq("ENSG00000012048")
```

## 可重現性紀錄

科學產出要附上足夠的 metadata，讓查詢能重播。

```markdown
| Date | gget version | Module | Query | Species/assembly | Output | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-05-11 | `gget --version` | search | `BRCA1 DNA repair` | human | `brca1-search.json` | Docs checked before run |
```

另外也要記錄：

- Python 版本和環境管理工具。
- 透過 `gget setup` 安裝的任何選用相依套件。
- 查詢回傳的資料庫專屬識別碼。
- 輸出是 JSON、CSV、FASTA，還是 DataFrame 匯出。
- 靠升級 `gget` 才解決的任何失敗。

## Review 檢查清單

- 有升級或確認已安裝的 `gget` 版本嗎？
- 使用參數之前，有查看目前的上游模組文件嗎？
- 物種或組裝版本有明確寫出嗎？
- 識別碼有原封不動保留，包含 Ensembl/UniProt 前綴嗎？
- 結果有標示為資料庫輸出，而不是臨床判讀嗎？
- 查詢能從儲存的指令或 Python 片段重現嗎？
- 選用相依套件有裝在隔離的環境裡嗎？

## 參考資料

- [gget documentation](https://pachterlab.github.io/gget/)
- [gget updates](https://pachterlab.github.io/gget/en/updates.html)
- [gget GitHub repository](https://github.com/pachterlab/gget)
- [gget Bioinformatics paper](https://doi.org/10.1093/bioinformatics/btac836)
