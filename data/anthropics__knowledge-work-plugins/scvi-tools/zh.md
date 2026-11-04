---
name: scvi-tools
description: 用 scvi-tools 做單細胞分析的深度學習。當使用者需要 (1) 用 scVI/scANVI 做資料整合與 batch correction、(2) 用 PeakVI 做 ATAC-seq 分析、(3) 用 totalVI 做 CITE-seq 多模態分析、(4) 用 MultiVI 做 multiome RNA+ATAC 分析、(5) 用 DestVI 做空間轉錄體 deconvolution、(6) 用 scANVI/scArches 做 label transfer 與 reference mapping、(7) 用 veloVI 做 RNA velocity，或 (8) 任何以深度學習為基礎的單細胞方法時使用這個 skill。觸發詞包括提到 scVI、scANVI、totalVI、PeakVI、MultiVI、DestVI、veloVI、sysVI、scArches、variational autoencoder、VAE、batch correction、data integration、multi-modal、CITE-seq、multiome、reference mapping、latent space。
---

# scvi-tools 深度學習 Skill

這個 skill 提供以深度學習做單細胞分析的指引，使用的是 scvi-tools，單細胞基因體學中機率模型的主流框架。

## 如何使用這個 Skill

1. 從下面的模型／工作流程表格，找出合適的工作流程
2. 讀對應的參考檔案，了解詳細步驟和程式碼
3. 使用 `scripts/` 裡的 script，避免重寫常用的程式碼
4. 遇到安裝或 GPU 問題，查 `references/environment_setup.md`
5. 要除錯，查 `references/troubleshooting.md`

## 何時使用這個 Skill

- 提到 scvi-tools、scVI、scANVI 或相關模型時
- 需要以深度學習為基礎的 batch correction 或整合時
- 處理多模態資料（CITE-seq、multiome）時
- 需要 reference mapping 或 label transfer 時
- 分析 ATAC-seq 或空間轉錄體資料時
- 學習單細胞資料的 latent 表示時

## 模型選擇指南

| 資料類型 | 模型 | 主要使用情境 |
|-----------|-------|------------------|
| scRNA-seq | **scVI** | 非監督式整合、DE、imputation |
| scRNA-seq + 標籤 | **scANVI** | Label transfer、半監督式整合 |
| CITE-seq（RNA+蛋白質） | **totalVI** | 多模態整合、蛋白質去噪 |
| scATAC-seq | **PeakVI** | 染色質可及性分析 |
| Multiome（RNA+ATAC） | **MultiVI** | 聯合模態分析 |
| 空間 + scRNA reference | **DestVI** | 細胞類型 deconvolution |
| RNA velocity | **veloVI** | 轉錄動態 |
| 跨技術 | **sysVI** | 系統層級的 batch correction |

## 工作流程參考檔案

| 工作流程 | 參考檔案 | 說明 |
|----------|---------------|-------------|
| 環境設定 | `references/environment_setup.md` | 安裝、GPU、版本資訊 |
| 資料準備 | `references/data_preparation.md` | 為任何模型整理資料格式 |
| scRNA 整合 | `references/scrna_integration.md` | scVI/scANVI batch correction |
| ATAC-seq 分析 | `references/atac_peakvi.md` | 用 PeakVI 做可及性分析 |
| CITE-seq 分析 | `references/citeseq_totalvi.md` | 用 totalVI 做蛋白質+RNA |
| Multiome 分析 | `references/multiome_multivi.md` | 用 MultiVI 做 RNA+ATAC |
| 空間 Deconvolution | `references/spatial_deconvolution.md` | DestVI 空間分析 |
| Label Transfer | `references/label_transfer.md` | scANVI reference mapping |
| scArches Mapping | `references/scarches_mapping.md` | Query 對 reference 的 mapping |
| Batch Correction | `references/batch_correction_sysvi.md` | 進階 batch 方法 |
| RNA Velocity | `references/rna_velocity_velovi.md` | veloVI 動態 |
| 疑難排解 | `references/troubleshooting.md` | 常見問題與解法 |

## CLI Scripts

常用工作流程的模組化 script。可以串接起來，或視需要修改。

### Pipeline Scripts

| Script | 用途 | 用法 |
|--------|---------|-------|
| `prepare_data.py` | QC、過濾、HVG 選擇 | `python scripts/prepare_data.py raw.h5ad prepared.h5ad --batch-key batch` |
| `train_model.py` | 訓練任何 scvi-tools 模型 | `python scripts/train_model.py prepared.h5ad results/ --model scvi` |
| `cluster_embed.py` | Neighbors、UMAP、Leiden | `python scripts/cluster_embed.py adata.h5ad results/` |
| `differential_expression.py` | DE 分析 | `python scripts/differential_expression.py model/ adata.h5ad de.csv --groupby leiden` |
| `transfer_labels.py` | 用 scANVI 做 label transfer | `python scripts/transfer_labels.py ref_model/ query.h5ad results/` |
| `integrate_datasets.py` | 多資料集整合 | `python scripts/integrate_datasets.py results/ data1.h5ad data2.h5ad` |
| `validate_adata.py` | 檢查資料相容性 | `python scripts/validate_adata.py data.h5ad --batch-key batch` |

### 範例工作流程

```bash
# 1. 驗證輸入資料
python scripts/validate_adata.py raw.h5ad --batch-key batch --suggest

# 2. 準備資料（QC、HVG 選擇）
python scripts/prepare_data.py raw.h5ad prepared.h5ad --batch-key batch --n-hvgs 2000

# 3. 訓練模型
python scripts/train_model.py prepared.h5ad results/ --model scvi --batch-key batch

# 4. 分群並視覺化
python scripts/cluster_embed.py results/adata_trained.h5ad results/ --resolution 0.8

# 5. Differential expression
python scripts/differential_expression.py results/model results/adata_clustered.h5ad results/de.csv --groupby leiden
```

### Python 工具函式

`scripts/model_utils.py` 提供可 import 的函式，用於自訂工作流程：

| 函式 | 用途 |
|----------|---------|
| `prepare_adata()` | 資料準備（QC、HVG、layer 設定） |
| `train_scvi()` | 訓練 scVI 或 scANVI |
| `evaluate_integration()` | 計算整合指標 |
| `get_marker_genes()` | 擷取 DE marker |
| `save_results()` | 儲存模型、資料、圖表 |
| `auto_select_model()` | 建議最適合的模型 |
| `quick_clustering()` | Neighbors + UMAP + Leiden |

## 關鍵需求

1. **需要原始 count**：scvi-tools 模型需要整數的 count 資料
   ```python
   adata.layers["counts"] = adata.X.copy()  # 在 normalization 之前
   scvi.model.SCVI.setup_anndata(adata, layer="counts")
   ```

2. **HVG 選擇**：使用 2000 到 4000 個高變異基因
   ```python
   sc.pp.highly_variable_genes(adata, n_top_genes=2000, batch_key="batch", layer="counts", flavor="seurat_v3")
   adata = adata[:, adata.var['highly_variable']].copy()
   ```

3. **Batch 資訊**：整合時要指定 batch_key
   ```python
   scvi.model.SCVI.setup_anndata(adata, layer="counts", batch_key="batch")
   ```

## 快速決策樹

```
Need to integrate scRNA-seq data?
├── Have cell type labels? → scANVI (references/label_transfer.md)
└── No labels? → scVI (references/scrna_integration.md)

Have multi-modal data?
├── CITE-seq (RNA + protein)? → totalVI (references/citeseq_totalvi.md)
├── Multiome (RNA + ATAC)? → MultiVI (references/multiome_multivi.md)
└── scATAC-seq only? → PeakVI (references/atac_peakvi.md)

Have spatial data?
└── Need cell type deconvolution? → DestVI (references/spatial_deconvolution.md)

Have pre-trained reference model?
└── Map query to reference? → scArches (references/scarches_mapping.md)

Need RNA velocity?
└── veloVI (references/rna_velocity_velovi.md)

Strong cross-technology batch effects?
└── sysVI (references/batch_correction_sysvi.md)
```

## 重要資源

- [scvi-tools Documentation](https://docs.scvi-tools.org/)
- [scvi-tools Tutorials](https://docs.scvi-tools.org/en/stable/tutorials/index.html)
- [Model Hub](https://huggingface.co/scvi-tools)
- [GitHub Issues](https://github.com/scverse/scvi-tools/issues)
