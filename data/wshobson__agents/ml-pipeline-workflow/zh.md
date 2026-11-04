---
name: ml-pipeline-workflow
description: 建構端到端的 MLOps pipeline，從資料準備、模型訓練、驗證一路到正式環境部署。在建立 ML pipeline、實踐 MLOps，或自動化模型訓練與部署工作流程時使用。
---

# ML Pipeline Workflow

完整的端到端 MLOps pipeline 編排，從資料準備到模型部署。

## Overview

這個 skill 提供完整的指引，用來建構涵蓋整個生命週期的正式環境 ML pipeline：資料擷取 → 準備 → 訓練 → 驗證 → 部署 → 監控。

## When to Use This Skill

- 從零開始建立新的 ML pipeline
- 為 ML 系統設計工作流程編排
- 實作 資料 → 模型 → 部署 的自動化
- 建立可重現的訓練工作流程
- 建立以 DAG 為基礎的 ML 編排
- 把 ML 元件整合進正式環境系統

## What This Skill Provides

### Core Capabilities

1. **Pipeline Architecture**
   - 端到端工作流程設計
   - DAG 編排模式（Airflow、Dagster、Kubeflow）
   - 元件相依性與資料流
   - 錯誤處理與 retry 策略

2. **Data Preparation**
   - 資料驗證與品質檢查
   - 特徵工程 pipeline
   - 資料版本控管與 lineage
   - Train/validation/test 切分策略

3. **Model Training**
   - 訓練 job 編排
   - 超參數管理
   - 整合實驗追蹤
   - 分散式訓練模式

4. **Model Validation**
   - 驗證框架與指標
   - A/B 測試基礎設施
   - 效能退化偵測
   - 模型比較工作流程

5. **Deployment Automation**
   - 模型 serving 模式
   - Canary 部署
   - Blue-green 部署策略
   - Rollback 機制

### Reference Documentation

詳細指南請見 `references/` 目錄：

- **data-preparation.md** - 資料清理、驗證與特徵工程
- **model-training.md** - 訓練工作流程與最佳實務
- **model-validation.md** - 驗證策略與指標
- **model-deployment.md** - 部署模式與 serving 架構

### Assets and Templates

`assets/` 目錄包含：

- **pipeline-dag.yaml.template** - 工作流程編排用的 DAG 範本
- **training-config.yaml** - 訓練設定範本
- **validation-checklist.md** - 部署前的驗證檢查清單

## Usage Patterns

### Basic Pipeline Setup

```python
# 1. Define pipeline stages
stages = [
    "data_ingestion",
    "data_validation",
    "feature_engineering",
    "model_training",
    "model_validation",
    "model_deployment"
]

# 2. Configure dependencies
# See assets/pipeline-dag.yaml.template for full example
```

### Production Workflow

1. **Data Preparation Phase**
   - 從來源擷取原始資料
   - 執行資料品質檢查
   - 套用特徵轉換
   - 為處理後的資料集做版本控管

2. **Training Phase**
   - 載入已版本化的訓練資料
   - 執行訓練 job
   - 追蹤實驗與指標
   - 儲存訓練好的模型

3. **Validation Phase**
   - 執行驗證測試套件
   - 與 baseline 比較
   - 產生效能報告
   - 核准部署

4. **Deployment Phase**
   - 封裝模型 artifact
   - 部署到 serving 基礎設施
   - 設定監控
   - 驗證正式環境流量

## Best Practices

### Pipeline Design

- **Modularity**：每個階段都應該能獨立測試
- **Idempotency**：重跑階段應該是安全的
- **Observability**：每個階段都要記錄指標
- **Versioning**：追蹤資料、程式碼與模型的版本
- **Failure Handling**：實作 retry 邏輯與警報

### Data Management

- 使用資料驗證函式庫（Great Expectations、TFX）
- 用 DVC 或類似工具為資料集做版本控管
- 記錄特徵工程的轉換
- 維持資料 lineage 追蹤

### Model Operations

- 把訓練與 serving 的基礎設施分開
- 使用 model registry（MLflow、Weights & Biases）
- 新模型採漸進式 rollout
- 監控模型效能飄移
- 保留 rollback 能力

### Deployment Strategies

- 從 shadow 部署開始
- 用 canary 發布做驗證
- 實作 A/B 測試基礎設施
- 設定自動 rollback 觸發條件
- 監控延遲與吞吐量

## Integration Points

### Orchestration Tools

- **Apache Airflow**：以 DAG 為基礎的工作流程編排
- **Dagster**：以 asset 為基礎的 pipeline 編排
- **Kubeflow Pipelines**：Kubernetes 原生的 ML 工作流程
- **Prefect**：現代的 dataflow 自動化

### Experiment Tracking

- MLflow 用於實驗追蹤與 model registry
- Weights & Biases 用於視覺化與協作
- TensorBoard 用於訓練指標

### Deployment Platforms

- AWS SageMaker：託管的 ML 基礎設施
- Google Vertex AI：GCP 部署
- Azure ML：Azure 雲端
- OCI Data Science：Oracle Cloud Infrastructure 部署
- Kubernetes + KServe：不綁定雲端的 serving

## Progressive Disclosure

從基礎開始，逐步增加複雜度：

1. **Level 1**：簡單的線性 pipeline（資料 → 訓練 → 部署）
2. **Level 2**：加入驗證與監控階段
3. **Level 3**：實作超參數調校
4. **Level 4**：加入 A/B 測試與漸進式 rollout
5. **Level 5**：搭配 ensemble 策略的多模型 pipeline

## Common Patterns

### Batch Training Pipeline

```yaml
# See assets/pipeline-dag.yaml.template
stages:
  - name: data_preparation
    dependencies: []
  - name: model_training
    dependencies: [data_preparation]
  - name: model_evaluation
    dependencies: [model_training]
  - name: model_deployment
    dependencies: [model_evaluation]
```

### Real-time Feature Pipeline

```python
# Stream processing for real-time features
# Combined with batch training
# See references/data-preparation.md
```

### Continuous Training

```python
# Automated retraining on schedule
# Triggered by data drift detection
# See references/model-training.md
```

## Troubleshooting

### Common Issues

- **Pipeline 失敗**：檢查相依性與資料是否可用
- **訓練不穩定**：檢視超參數與資料品質
- **部署問題**：驗證模型 artifact 與 serving 設定
- **效能下降**：監控資料飄移與模型指標

### Debugging Steps

1. 檢查每個階段的 pipeline log
2. 驗證各階段交界處的輸入/輸出資料
3. 單獨測試各元件
4. 檢視實驗追蹤的指標
5. 檢查模型 artifact 與 metadata

## Next Steps

設定好 pipeline 之後：

1. 到 **hyperparameter-tuning** skill 探索最佳化
2. 學習 **experiment-tracking-setup** 來整合 MLflow/W&B
3. 檢視 **model-deployment-patterns** 了解 serving 策略
4. 用可觀測性工具實作監控

## Related Skills

- **experiment-tracking-setup**：MLflow 與 Weights & Biases 整合
- **hyperparameter-tuning**：自動化超參數最佳化
- **model-deployment-patterns**：進階部署策略
