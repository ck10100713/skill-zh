---
name: nextflow-development
description: 對定序資料執行 nf-core 生物資訊 pipeline（rnaseq、sarek、atacseq）。分析 RNA-seq、WGS/WES 或 ATAC-seq 資料時使用，本地 FASTQ 或 GEO/SRA 的公開資料集都可以。觸發詞包括 nf-core、Nextflow、FASTQ 分析、variant calling、基因表現、差異表現、GEO 重新分析、GSE/GSM/SRR 編號，或建立 samplesheet。
---

# nf-core Pipeline 部署

對本地或公開的定序資料執行 nf-core 生物資訊 pipeline。

**目標使用者：** 沒有專門生物資訊訓練、但需要跑大規模 omics 分析（差異表現、variant calling 或染色質可及性分析）的實驗室科學家和研究人員。

## 工作流程檢查清單

```
- [ ] Step 0: Acquire data (if from GEO/SRA)
- [ ] Step 1: Environment check (MUST pass)
- [ ] Step 2: Select pipeline (confirm with user)
- [ ] Step 3: Run test profile (MUST pass)
- [ ] Step 4: Create samplesheet
- [ ] Step 5: Configure & run (confirm genome with user)
- [ ] Step 6: Verify outputs
```

---

## Step 0：取得資料（只限 GEO/SRA）

**如果使用者有本地 FASTQ 檔案，就跳過這一步。**

公開資料集要先從 GEO/SRA 抓取。完整流程請見 [references/geo-sra-acquisition.md](references/geo-sra-acquisition.md)。

**快速開始：**

```bash
# 1. Get study info
python scripts/sra_geo_fetch.py info GSE110004

# 2. Download (interactive mode)
python scripts/sra_geo_fetch.py download GSE110004 -o ./fastq -i

# 3. Generate samplesheet
python scripts/sra_geo_fetch.py samplesheet GSE110004 --fastq-dir ./fastq -o samplesheet.csv
```

**決策點：** 抓完研究資訊之後，跟使用者確認：
- 要下載哪個樣本子集（如果有多種資料類型）
- 建議的基因組和 pipeline

然後繼續 Step 1。

---

## Step 1：環境檢查

**最先執行。環境沒通過，pipeline 一定會失敗。**

```bash
python scripts/check_environment.py
```

所有關鍵檢查都必須通過。如果有任何失敗，提供修復指示：

### Docker 問題

| 問題 | 修法 |
|---------|-----|
| 沒安裝 | 從 https://docs.docker.com/get-docker/ 安裝 |
| Permission denied | `sudo usermod -aG docker $USER`，然後重新登入 |
| Daemon 沒在跑 | `sudo systemctl start docker` |

### Nextflow 問題

| 問題 | 修法 |
|---------|-----|
| 沒安裝 | `curl -s https://get.nextflow.io \| bash && mv nextflow ~/bin/` |
| 版本 < 23.04 | `nextflow self-update` |

### Java 問題

| 問題 | 修法 |
|---------|-----|
| 沒安裝 / < 11 | `sudo apt install openjdk-11-jdk` |

**檢查沒全部通過，就不要往下走。** HPC/Singularity 的情況請見 [references/troubleshooting.md](references/troubleshooting.md)。

---

## Step 2：選擇 Pipeline

**決策點：往下之前先跟使用者確認。**

| 資料類型 | Pipeline | 版本 | 目標 |
|-----------|----------|---------|------|
| RNA-seq | `rnaseq` | 3.22.2 | 基因表現 |
| WGS/WES | `sarek` | 3.7.1 | Variant calling |
| ATAC-seq | `atacseq` | 2.1.2 | 染色質可及性 |

從資料自動偵測：
```bash
python scripts/detect_data_type.py /path/to/data
```

各 pipeline 的詳細說明：
- [references/pipelines/rnaseq.md](references/pipelines/rnaseq.md)
- [references/pipelines/sarek.md](references/pipelines/sarek.md)
- [references/pipelines/atacseq.md](references/pipelines/atacseq.md)

---

## Step 3：執行測試 Profile

**用小資料驗證環境。真實資料之前，這一步一定要通過。**

```bash
nextflow run nf-core/<pipeline> -r <version> -profile test,docker --outdir test_output
```

| Pipeline | 指令 |
|----------|---------|
| rnaseq | `nextflow run nf-core/rnaseq -r 3.22.2 -profile test,docker --outdir test_rnaseq` |
| sarek | `nextflow run nf-core/sarek -r 3.7.1 -profile test,docker --outdir test_sarek` |
| atacseq | `nextflow run nf-core/atacseq -r 2.1.2 -profile test,docker --outdir test_atacseq` |

驗證：
```bash
ls test_output/multiqc/multiqc_report.html
grep "Pipeline completed successfully" .nextflow.log
```

如果測試失敗，請見 [references/troubleshooting.md](references/troubleshooting.md)。

---

## Step 4：建立 Samplesheet

### 自動產生

```bash
python scripts/generate_samplesheet.py /path/to/data <pipeline> -o samplesheet.csv
```

這個 script 會：
- 找出 FASTQ/BAM/CRAM 檔案
- 配對 R1/R2 reads
- 推斷樣本 metadata
- 寫入之前先驗證

**sarek：** 如果無法自動偵測，script 會詢問 tumor/normal 狀態。

### 驗證既有的 samplesheet

```bash
python scripts/generate_samplesheet.py --validate samplesheet.csv <pipeline>
```

### Samplesheet 格式

**rnaseq：**
```csv
sample,fastq_1,fastq_2,strandedness
SAMPLE1,/abs/path/R1.fq.gz,/abs/path/R2.fq.gz,auto
```

**sarek：**
```csv
patient,sample,lane,fastq_1,fastq_2,status
patient1,tumor,L001,/abs/path/tumor_R1.fq.gz,/abs/path/tumor_R2.fq.gz,1
patient1,normal,L001,/abs/path/normal_R1.fq.gz,/abs/path/normal_R2.fq.gz,0
```

**atacseq：**
```csv
sample,fastq_1,fastq_2,replicate
CONTROL,/abs/path/ctrl_R1.fq.gz,/abs/path/ctrl_R2.fq.gz,1
```

---

## Step 5：設定並執行

### 5a. 檢查基因組是否可用

```bash
python scripts/manage_genomes.py check <genome>
# If not installed:
python scripts/manage_genomes.py download <genome>
```

常用基因組：GRCh38（人類）、GRCh37（舊版）、GRCm39（小鼠）、R64-1-1（酵母）、BDGP6（果蠅）

### 5b. 決策點

**決策點：跟使用者確認：**

1. **基因組：** 要用哪個參考基因組
2. **各 pipeline 專屬選項：**
   - **rnaseq：** aligner（建議 star_salmon，記憶體少時用 hisat2）
   - **sarek：** 工具（germline 用 haplotypecaller，somatic 用 mutect2）
   - **atacseq：** read_length（50、75、100 或 150）

### 5c. 執行 pipeline

```bash
nextflow run nf-core/<pipeline> \
    -r <version> \
    -profile docker \
    --input samplesheet.csv \
    --outdir results \
    --genome <genome> \
    -resume
```

**關鍵參數：**
- `-r`：鎖定版本
- `-profile docker`：使用 Docker（HPC 用 `singularity`）
- `--genome`：iGenomes key
- `-resume`：從 checkpoint 繼續

**資源上限（需要時）：**
```bash
--max_cpus 8 --max_memory '32.GB' --max_time '24.h'
```

---

## Step 6：驗證輸出

### 檢查是否完成

```bash
ls results/multiqc/multiqc_report.html
grep "Pipeline completed successfully" .nextflow.log
```

### 各 pipeline 的關鍵輸出

**rnaseq：**
- `results/star_salmon/salmon.merged.gene_counts.tsv` - 基因 counts
- `results/star_salmon/salmon.merged.gene_tpm.tsv` - TPM 值

**sarek：**
- `results/variant_calling/*/` - VCF 檔案
- `results/preprocessing/recalibrated/` - BAM 檔案

**atacseq：**
- `results/macs2/narrowPeak/` - Peak calls
- `results/bwa/mergedLibrary/bigwig/` - Coverage tracks

---

## 快速參考

常見的 exit code 和修法，請見 [references/troubleshooting.md](references/troubleshooting.md)。

### 恢復失敗的執行

```bash
nextflow run nf-core/<pipeline> -resume
```

---

## 參考資料

- [references/geo-sra-acquisition.md](references/geo-sra-acquisition.md) - 下載公開的 GEO/SRA 資料
- [references/troubleshooting.md](references/troubleshooting.md) - 常見問題與修法
- [references/installation.md](references/installation.md) - 環境設定
- [references/pipelines/rnaseq.md](references/pipelines/rnaseq.md) - RNA-seq pipeline 細節
- [references/pipelines/sarek.md](references/pipelines/sarek.md) - Variant calling 細節
- [references/pipelines/atacseq.md](references/pipelines/atacseq.md) - ATAC-seq 細節

---

## 免責聲明

這個 skill 是以原型範例的形式提供，示範如何把 nf-core 生物資訊 pipeline 整合進 Claude Code，做自動化分析工作流程。目前的實作支援三個 pipeline（rnaseq、sarek 和 atacseq），作為基礎，讓社群能把支援擴充到完整的 nf-core pipeline 集合。

它是為教育和研究目的而設計，沒有針對你的特定使用情境做適當驗證之前，不應該被視為可用於正式環境。使用者要自行確保運算環境符合 pipeline 的需求，並驗證分析結果。

Anthropic 不保證生物資訊輸出的正確性，使用者應該遵循標準做法來驗證運算分析。這個整合並未獲得 nf-core 社群的官方背書，也與其無關。

## 出處標示

發表結果時，請引用適當的 pipeline。引用資訊可以在各個 nf-core repository 的 CITATIONS.md 檔案中找到（例如 https://github.com/nf-core/rnaseq/blob/3.22.2/CITATIONS.md）。

## 授權

- **nf-core pipelines：** MIT License (https://nf-co.re/about)
- **Nextflow：** Apache License, Version 2.0 (https://www.nextflow.io/about-us.html)
- **NCBI SRA Toolkit：** Public Domain (https://github.com/ncbi/sra-tools/blob/master/LICENSE)
