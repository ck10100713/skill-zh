---
name: k8s-manifest-generator
description: 依照最佳實務與安全標準，建立可上 production 的 Kubernetes manifest，包含 Deployment、Service、ConfigMap 與 Secret。適用於產生 Kubernetes YAML manifest、建立 K8s 資源，或實作 production 等級的 Kubernetes 設定的時候。
---

# Kubernetes Manifest 產生器

逐步指引，用於建立可上 production 的 Kubernetes manifest，包含 Deployment、Service、ConfigMap、Secret 和 PersistentVolumeClaim。

## 目的

這個 skill 提供完整的指引，依照雲原生最佳實務與 Kubernetes 慣例，產生結構良好、安全且可上 production 的 Kubernetes manifest。

## 什麼時候用這個 Skill

需要做下面這些事情的時候，就用這個 skill：

- 建立新的 Kubernetes Deployment manifest
- 定義提供網路連線的 Service 資源
- 產生用於設定管理的 ConfigMap 和 Secret 資源
- 為有狀態的工作負載建立 PersistentVolumeClaim manifest
- 遵循 Kubernetes 最佳實務與命名慣例
- 實作資源限制、健康檢查和 security context
- 設計多環境 deploy 的 manifest

## 詳細模式與實作範例

詳細的模式文件放在 `references/details.md`，上面這一層導覽不夠用的時候再去讀那份檔案。

## 最佳實務摘要

1. **一定要設定資源 request 和 limit**：避免資源被搶光
2. **實作健康檢查**：確保 Kubernetes 能管理你的應用
3. **使用特定的 image tag**：避免不可預期的 deploy
4. **套用 security context**：以非 root 身分執行、移除多餘的 capability
5. **使用 ConfigMap 和 Secret**：把設定與程式碼分開
6. **所有東西都加 label**：方便過濾與組織
7. **遵循命名慣例**：使用標準的 Kubernetes label
8. **套用之前先驗證**：使用 dry-run 和驗證工具
9. **為 manifest 做版本控制**：放在 Git 並做版本控制
10. **用 annotation 寫文件**：為其他開發者補充脈絡

## 疑難排解

**Pod 無法啟動：**

- 檢查 image pull 錯誤：`kubectl describe pod <pod-name>`
- 確認資源是否足夠：`kubectl get nodes`
- 檢查 event：`kubectl get events --sort-by='.lastTimestamp'`

**Service 無法存取：**

- 確認 selector 符合 pod 的 label：`kubectl get endpoints <service-name>`
- 檢查 service 的類型與 port 設定
- 從 cluster 內部測試：`kubectl run debug --rm -it --image=busybox -- sh`

**ConfigMap/Secret 沒有載入：**

- 確認 Deployment 裡的名稱相符
- 檢查 namespace
- 確保資源存在：`kubectl get configmap,secret`

## 下一步

建立 manifest 之後：

1. 存放到 Git repository
2. 為 deploy 設定 CI/CD pipeline
3. 考慮用 Helm 或 Kustomize 做模板
4. 用 ArgoCD 或 Flux 實作 GitOps
5. 加入監控與 observability

## 相關 Skill

- `helm-chart-scaffolding`：用於模板化與打包
- `gitops-workflow`：用於自動化 deploy
- `k8s-security-policies`：用於進階的安全設定
