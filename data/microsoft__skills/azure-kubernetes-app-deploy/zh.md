---
name: azure-kubernetes-app-deploy
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
description: "要把現有的 web 應用程式或 API 部署到已經在跑的 Azure Kubernetes Service cluster 時使用。會偵測 framework、產生 Dockerfile 和 Kubernetes manifest、對照 AKS Deployment Safeguards 驗證，並在部署後做驗證。WHEN: deploy app to AKS, deploy to existing AKS cluster, containerize app for Kubernetes, generate K8s manifests for Azure, set up CI/CD for AKS, my AKS deployment is failing safeguard checks, I have a Django/Express/Spring Boot app to run on AKS. DO NOT USE FOR: 建立或佈建 AKS cluster（用 azure-kubernetes）、評估遷移到 AKS Automatic（用 azure-kubernetes-automatic-readiness），或部署到非 AKS 的目標，像 Web Apps、Container Apps 或 Functions。"
---

# 部署到 AKS

**何時使用：** 把 web app/API 部署到 AKS；為 Kubernetes 做容器化；產生 manifest；AKS CI/CD；DS001–DS013 失敗。

**不適用：** 佈建 cluster（`azure-kubernetes`）、AKS Automatic 就緒度（`azure-kubernetes-automatic-readiness`）、非 AKS 的目標。

## 工作流程

需要：現有的 AKS cluster、`az login`、已設定好的 `kubectl`。照 `phases/quick-deploy.md` 做。失敗時看：`references/rollback.md`。

## 參考

- [detection.md](./references/detection.md)：framework／port／health 偵測
- [safeguards.md](./references/safeguards.md)：DS001-DS013 檢查清單
- [workload-identity.md](./references/workload-identity.md)：Workload Identity 設定
- [rollback.md](./references/rollback.md)：復原程序
- [base-images.md](./references/base-images.md)：base image 政策，以及 `<LATEST_STABLE_*>` 的解析

## Knowledge Pack

依偵測到的 framework 載入 `knowledge-packs/frameworks/<framework>.md`。可用的有：`spring-boot`、`express`、`nextjs`、`fastapi`、`django`、`nestjs`、`aspnet-core`、`go`、`flask`

## 範本

`templates/`（dockerfiles/、k8s/、github-actions/、mermaid/）。
