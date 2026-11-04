---
name: airunway-aks-setup
description: "在 AKS 上設定 AI Runway，從空白 cluster 一路到模型跑起來。涵蓋 cluster 驗證、controller 安裝、GPU 評估、provider 設定和第一次部署。WHEN: \"setup AI Runway\", \"onboard AKS cluster\", \"install AI Runway\", \"airunway setup\", \"deploy model to AKS\", \"GPU inference on AKS\", \"KAITO setup on AKS\", \"run LLM on AKS\", \"vLLM on AKS\", \"set up model serving on AKS\", \"AI Runway controller\"。"
license: MIT
metadata:
  author: Microsoft
  version: "1.1.2"
argument-hint: "[skip-to-step N]"
---

# AI Runway AKS 設定

這個 skill 帶使用者從空白的 Kubernetes cluster 一路走到 AI 模型部署完成。照順序一步一步來，除非使用者給了 `skip-to-step N`，才從指定的階段接著做。

> **成本意識：** GPU node pool 的運算費用很高（A100-80GB 每小時可能 $3–5 美元以上）。建立 GPU 資源之前，先確認使用者了解成本。

## 前置條件

這個 skill 假設 AKS cluster 已經存在。如果使用者還沒有 cluster，先交給 `azure-kubernetes` skill 建一個（除非純 CPU 推論就夠，否則要帶 GPU node pool），再回到這裡。

## 速查

| 屬性 | 值 |
|----------|-------|
| 適用情境 | 在 AKS 上完整走完 AI Runway 上線流程 |
| CLI 工具 | `kubectl`、`make`、`curl` |
| MCP 工具 | 無 |
| 相關 skill | `azure-kubernetes`（cluster 設定）、`azure-diagnostics`（基本疑難排解）、選用的 `aks-gpu-inference`（只處理既有 GPU／推論的 Day-2 事故） |

## 何時使用這個 Skill

使用者想做以下事情時用這個 skill：
- 在既有的 AKS cluster 上從零開始設定 AI Runway
- 安裝 AI Runway controller 和 CRD
- 評估 GPU 硬體對模型部署的相容性
- 選擇並安裝推論 provider（KAITO、Dynamo、KubeRay）
- 透過 AI Runway 把第一個 AI 模型部署到 AKS
- 從指定的步驟接續做到一半的 AI Runway 設定

## GPU 設定 vs. Day-2 事故

最初的 GPU node pool、provider、controller 和模型設定都在這個 skill 裡處理。
如果是影響既有 GPU 或推論部署的事故，先載入
[optional-gpu-day2.md](references/optional-gpu-day2.md)，再決定要不要
提供那個專門的選用附加功能。

## MCP 工具

這個 skill 不用任何 MCP 工具。所有 cluster 操作都直接用 `kubectl` 和 `make` 完成。

## 規則

1. 照順序執行步驟，走到哪一步就載入那一步的 reference
2. 每一步都回報 cluster 狀態：✓ 正常、✗ 缺少／失敗
3. 任何安裝或部署動作之前，都要先問使用者確認
4. 如果某一步已經完成，回報狀態後直接跳到下一步
5. 如果使用者給了 `skip-to-step N`，就從第 N 步開始，並假設前面的步驟都已完成

## 步驟

| # | 步驟 | Reference |
|---|------|-----------|
| 1 | **Cluster 驗證**：檢查 context、盤點 node、偵測 GPU | [step-1-verify.md](references/steps/step-1-verify.md) |
| 2 | **Controller 安裝**：部署 CRD 和 controller | [step-2-controller.md](references/steps/step-2-controller.md) |
| 3 | **GPU 評估**：偵測 GPU 型號，標出 dtype／attention 的限制 | [step-3-gpu.md](references/steps/step-3-gpu.md) |
| 4 | **Provider 設定**：推薦並安裝推論 provider | [step-4-provider.md](references/steps/step-4-provider.md) |
| 5 | **第一次部署**：選模型、部署、確認進入 Ready | [step-5-deploy.md](references/steps/step-5-deploy.md) |
| 6 | **總結**：回顧、smoke test、後續步驟 | [step-6-summary.md](references/steps/step-6-summary.md) |

## 錯誤處理

| 錯誤／症狀 | 可能原因 | 處理方式 |
|-----------------|--------------|-------------|
| 沒有 kubeconfig context | 沒連上 cluster | 執行 `az aks get-credentials` 或同等指令 |
| Controller 處於 CrashLoopBackOff | 設定或 RBAC 問題 | `kubectl logs -n airunway-system -l control-plane=controller-manager --previous` |
| Provider 還沒 ready | Image pull 或 RBAC 問題 | 對 provider 的 pod 執行 `kubectl logs <pod-name> -n <namespace>` |
| ModelDeployment 卡在 Pending | GPU 排程失敗或 provider 還沒 ready | 看 `kubectl describe modeldeployment <name> -n <namespace>` 的 events |
| 推論時出現 `bfloat16` 錯誤 | T4 或 V100 不支援 bfloat16 | 在 serving 參數加上 `--dtype float16` |

完整的錯誤處理和 rollback 流程，請看 [troubleshooting.md](references/troubleshooting.md)。
