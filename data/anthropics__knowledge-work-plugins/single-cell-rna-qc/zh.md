---
name: single-cell-rna-qc
description: 依 scverse 最佳實務，用 MAD 過濾和完整視覺化，對單細胞 RNA-seq 資料（.h5ad 或 .h5 檔）做品質控制。適用於使用者要求 QC 分析、過濾低品質細胞、評估資料品質，或要依 scverse/scanpy 最佳實務做單細胞分析。
---

# 單細胞 RNA-seq 品質控制

依 scverse 最佳實務設計的單細胞 RNA-seq 自動化 QC 工作流程。

## 何時使用這個 Skill

使用者有以下需求時使用：
- 要對單細胞 RNA-seq 資料做品質控制或 QC
- 想過濾低品質細胞或評估資料品質
- 需要 QC 視覺化圖表或指標
- 要求遵循 scverse/scanpy 最佳實務
- 要求 MAD 過濾或離群值偵測

**支援的輸入格式：**
- `.h5ad` 檔（scanpy/Python 工作流程的 AnnData 格式）
- `.h5` 檔（10X Genomics Cell Ranger 的輸出）

**預設建議**：用方法 1（完整流程），除非使用者有特定的自訂需求，或明確要求非標準的過濾邏輯。

## 方法 1：完整 QC 流程（標準工作流程建議用這個）

依 scverse 最佳實務做標準 QC，使用現成的腳本 `scripts/qc_analysis.py`：

```bash
python3 scripts/qc_analysis.py input.h5ad
# or for 10X Genomics .h5 files:
python3 scripts/qc_analysis.py raw_feature_bc_matrix.h5
```

腳本會自動偵測檔案格式並用對應方式載入。

**適合用這個方法的情況：**
- 標準 QC 工作流程，閾值可調整（所有細胞用同一套方式過濾）
- 批次處理多個資料集
- 快速探索性分析
- 使用者想要「直接能用」的方案

**需求套件：** anndata, scanpy, scipy, matplotlib, seaborn, numpy

**參數：**

用命令列參數自訂過濾閾值和基因名稱模式：
- `--output-dir` - 輸出資料夾
- `--mad-counts`, `--mad-genes`, `--mad-mt` - counts／genes／MT% 的 MAD 閾值
- `--mt-threshold` - 粒線體 % 的硬性截斷值
- `--min-cells` - 基因過濾閾值
- `--mt-pattern`, `--ribo-pattern`, `--hb-pattern` - 不同物種的基因名稱模式

用 `--help` 查看目前的預設值。

**輸出：**

所有檔案預設存到 `<input_basename>_qc_results/` 資料夾（或 `--output-dir` 指定的資料夾）：
- `qc_metrics_before_filtering.png` - 過濾前的視覺化
- `qc_filtering_thresholds.png` - 疊上 MAD 閾值的圖
- `qc_metrics_after_filtering.png` - 過濾後的品質指標
- `<input_basename>_filtered.h5ad` - 乾淨、已過濾、可直接用於下游分析的資料集
- `<input_basename>_with_qc.h5ad` - 保留 QC 註解的原始資料

如果要把輸出複製給使用者，請複製個別檔案（不要複製整個資料夾），這樣使用者才能直接預覽。

### 工作流程步驟

腳本會執行以下步驟：

1. **計算 QC 指標** - 計數深度、基因偵測數、粒線體／核糖體／血紅素含量
2. **套用 MAD 過濾** - 用 counts／genes／MT% 的 MAD 閾值做寬鬆的離群值偵測
3. **過濾基因** - 移除只在少數細胞中偵測到的基因
4. **產生視覺化** - 完整的過濾前後圖表，並疊上閾值

## 方法 2：模組化積木（自訂工作流程用）

要做自訂分析流程或有非標準需求時，使用 `scripts/qc_core.py` 和 `scripts/qc_plotting.py` 的模組化工具函式：

```python
# Run from scripts/ directory, or add scripts/ to sys.path if needed
import anndata as ad
from qc_core import calculate_qc_metrics, detect_outliers_mad, filter_cells
from qc_plotting import plot_qc_distributions  # Only if visualization needed

adata = ad.read_h5ad('input.h5ad')
calculate_qc_metrics(adata, inplace=True)
# ... custom analysis logic here
```

**適合用這個方法的情況：**
- 需要不同的流程（跳過步驟、改順序、對子集套用不同閾值）
- 有條件邏輯（例如神經元和其他細胞用不同方式過濾）
- 只跑一部分（只算指標／視覺化，不過濾）
- 要整合進更大流程裡的其他分析步驟
- 需要命令列參數無法支援的自訂過濾條件

**可用的工具函式：**

`qc_core.py`（核心 QC 操作）：
- `calculate_qc_metrics(adata, mt_pattern, ribo_pattern, hb_pattern, inplace=True)` - 計算 QC 指標並註解到 adata
- `detect_outliers_mad(adata, metric, n_mads, verbose=True)` - 以 MAD 偵測離群值，回傳布林遮罩
- `apply_hard_threshold(adata, metric, threshold, operator='>', verbose=True)` - 套用硬性截斷值，回傳布林遮罩
- `filter_cells(adata, mask, inplace=False)` - 套用布林遮罩來過濾細胞
- `filter_genes(adata, min_cells=20, min_counts=None, inplace=True)` - 依偵測數過濾基因
- `print_qc_summary(adata, label='')` - 印出摘要統計

`qc_plotting.py`（視覺化）：
- `plot_qc_distributions(adata, output_path, title)` - 產生完整的 QC 圖
- `plot_filtering_thresholds(adata, outlier_masks, thresholds, output_path)` - 視覺化過濾閾值
- `plot_qc_after_filtering(adata, output_path)` - 產生過濾後的圖

**自訂工作流程範例：**

**範例 1：只算指標和視覺化，先不過濾**
```python
adata = ad.read_h5ad('input.h5ad')
calculate_qc_metrics(adata, inplace=True)
plot_qc_distributions(adata, 'qc_before.png', title='Initial QC')
print_qc_summary(adata, label='Before filtering')
```

**範例 2：只套用 MT% 過濾，其他指標維持寬鬆**
```python
adata = ad.read_h5ad('input.h5ad')
calculate_qc_metrics(adata, inplace=True)

# Only filter high MT% cells
high_mt = apply_hard_threshold(adata, 'pct_counts_mt', 10, operator='>')
adata_filtered = filter_cells(adata, ~high_mt)
adata_filtered.write('filtered.h5ad')
```

**範例 3：不同子集用不同閾值**
```python
adata = ad.read_h5ad('input.h5ad')
calculate_qc_metrics(adata, inplace=True)

# Apply type-specific QC (assumes cell_type metadata exists)
neurons = adata.obs['cell_type'] == 'neuron'
other_cells = ~neurons

# Neurons tolerate higher MT%, other cells use stricter threshold
neuron_qc = apply_hard_threshold(adata[neurons], 'pct_counts_mt', 15, operator='>')
other_qc = apply_hard_threshold(adata[other_cells], 'pct_counts_mt', 8, operator='>')
```

## 最佳實務

1. **過濾要寬鬆** - 預設閾值刻意保留大部分細胞，避免丟掉稀有族群
2. **檢查視覺化結果** - 一定要看過濾前後的圖，確認過濾在生物學上說得通
3. **考慮資料集本身的特性** - 有些組織的粒線體含量天生就比較高（例如神經元、心肌細胞）
4. **確認基因註解** - 粒線體基因前綴因物種而異（小鼠是 mt-，人類是 MT-）
5. **需要時反覆調整** - QC 參數可能要依特定實驗或組織類型調整

## 參考資料

詳細的 QC 方法、參數依據和疑難排解，請見 `references/scverse_qc_guidelines.md`。這份參考資料包含：
- 每個 QC 指標的詳細說明，以及為什麼重要
- 用 MAD 閾值的理由，以及為什麼比固定截斷值好
- 如何解讀 QC 視覺化圖表（直方圖、小提琴圖、散佈圖）
- 基因註解的物種別注意事項
- 何時以及如何調整過濾參數
- 進階 QC 考量（環境 RNA 校正、雙細胞偵測）

使用者需要更深入了解方法，或在排查 QC 問題時，載入這份參考資料。

## QC 之後的下一步

典型的下游分析步驟：
- 環境 RNA 校正（SoupX、CellBender）
- 雙細胞偵測（scDblFinder）
- 正規化（log-normalize、scran）
- 特徵選擇和降維
- 分群和細胞類型註解
