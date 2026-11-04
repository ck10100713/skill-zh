---
name: finetuning
description: "在 Microsoft Foundry 上用 SFT（監督式）、DPO（偏好）或 RFT（搭配 grader 的強化學習）微調模型。涵蓋資料集準備、提交訓練 job、部署和評估。USE FOR: fine-tune, SFT, DPO, RFT, training data, grader, distillation, fine-tuned model, training job, large file upload, calibrate grader, deploy fine-tuned model, evaluate fine-tuned model. DO NOT USE FOR: general model deployment without fine-tuning (use deploy-model), agent creation (use agents), prompt optimization without training (use prompt-optimizer)."
license: MIT
metadata:
  author: Microsoft
  version: "0.0.0-placeholder"
---

# Fine-Tuning on Microsoft Foundry

用 SFT（監督式）、DPO（偏好）或 RFT（搭配 grader 的強化學習）微調模型。涵蓋資料集準備、訓練、部署和評估。

## When to Use

使用者問到這些時，用這個 sub-skill：
- 微調模型（SFT、DPO 或 RFT）
- 準備、驗證或格式化訓練資料
- 提交、監控或診斷訓練 job
- 校準 RFT 的 grader 或通過門檻
- 部署或評估微調後的模型
- 在訓練類型之間做選擇（SFT vs DPO vs RFT）
- Distillation、合成資料生成或資料集品質評分
- 訓練資料的大檔案上傳
- 清理微調相關資源（檔案、deployment）

**不要用在：** 沒有微調的一般模型部署（用 deploy-model）、建立 agent（用 agents）、不經訓練的 prompt 最佳化（用 prompt-optimizer）。

## Workflows

| Stage | Guide |
|-------|-------|
| **Quick start** | [workflows/quickstart.md](workflows/quickstart.md) |
| **Full pipeline** | [workflows/full-pipeline.md](workflows/full-pipeline.md) |
| **Create data** | [workflows/dataset-creation.md](workflows/dataset-creation.md) |
| **Iterate** | [workflows/iterative-training.md](workflows/iterative-training.md) |
| **Diagnose** | [workflows/diagnose-poor-results.md](workflows/diagnose-poor-results.md) |

## References

| Topic | File |
|-------|------|
| SFT vs DPO vs RFT | [references/training-types.md](references/training-types.md) |
| Hyperparameters | [references/hyperparameters.md](references/hyperparameters.md) |
| Data formats | [references/dataset-formats.md](references/dataset-formats.md) |
| Grader design (RFT) | [references/grader-design.md](references/grader-design.md) |
| Reward hacking | [references/reward-hacking.md](references/reward-hacking.md) |
| Agentic RFT (tools) | [references/agentic-rft.md](references/agentic-rft.md) |
| Deployment | [references/deployment.md](references/deployment.md) |
| Training curves | [references/training-curves.md](references/training-curves.md) |
| Evaluation | [references/evaluation.md](references/evaluation.md) |
| Vision fine-tuning | [references/vision-fine-tuning.md](references/vision-fine-tuning.md) |
| Large file uploads | [references/large-file-uploads.md](references/large-file-uploads.md) |
| Platform gotchas | [references/platform-gotchas.md](references/platform-gotchas.md) |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/submit_training.py` | 提交 SFT/DPO/RFT job |
| `scripts/monitor_training.py` | 輪詢 job 直到完成 |
| `scripts/calibrate_grader.py` | 找出最佳的 RFT pass_threshold |
| `scripts/check_training.py` | 分析訓練曲線、列出 checkpoint |
| `scripts/deploy_model.py` | 透過 ARM REST API 部署 |
| `scripts/evaluate_model.py` | 用 LLM judge 評估 |
| `scripts/convert_dataset.py` | 在 SFT/DPO/RFT 格式之間轉換 |
| `scripts/generate_distillation_data.py` | 生成合成訓練資料 |
| `scripts/score_dataset.py` | 對訓練資料做品質評分 |
| `scripts/cleanup.py` | 刪除舊檔案和 deployment |
| `scripts/validate/` | 資料驗證器（SFT、DPO、RFT）+ 統計 |

## Rules

1. **一定要先建立 baseline**：微調之前先評估 base model
2. **提交前先驗證資料**：執行 `scripts/validate/validate_sft.py`
3. **校準 RFT grader**：目標是 base model 有 25-50% 的失敗率
4. **評估 checkpoint**：不要不加思索就部署最後一個
5. **比較模型時，除了準確率也要量 token 成本**

## Quick Reference

| Task | Command |
|------|---------|
| Validate SFT data | `python scripts/validate/validate_sft.py data.jsonl` |
| Submit SFT job | `python scripts/submit_training.py --model gpt-4.1-mini --training-file train.jsonl --validation-file val.jsonl --type sft` |
| Monitor job | `python scripts/monitor_training.py --job-id ftjob-xxx` |
| Analyze curves | `python scripts/check_training.py --job-id ftjob-xxx` |
| Deploy model | `python scripts/deploy_model.py --model-id ft:gpt-4.1-mini:... --name my-eval` |
| Evaluate model | `python scripts/evaluate_model.py --deployment-name my-eval --test-file test.jsonl` |

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| "API version not supported" | 在 `/v1/` endpoint 上用了舊版 `openai` SDK | 升級到 `openai>=1.0` |
| "does not support fine-tuning with Standard TrainingType" | OSS 模型需要 `globalStandard` | 加 `--use-rest` 旗標，或讓 script 自動 fallback |
| Job 卡在 post-training eval | 工具 endpoint 資源不足（RFT） | 擴到 S2 以上，啟用 Always On |
| ARM 成功後出現 "DeploymentNotReady" | ARM 與 data-plane 的 race condition | 刪掉 deployment 重建，等 5 分鐘 |
| 部署時被內容安全機制擋下 | 訓練資料含大量 PII | 移除有問題的文件類型 |
