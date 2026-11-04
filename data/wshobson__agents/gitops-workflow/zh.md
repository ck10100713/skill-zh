---
name: gitops-workflow
description: 用 ArgoCD 和 Flux 實作 GitOps 工作流程，達成自動化、宣告式、持續調和的 Kubernetes deploy。適用於實作 GitOps 實務、自動化 Kubernetes deploy，或設定宣告式的基礎設施管理的時候。
---

# GitOps 工作流程

用 ArgoCD 和 Flux 實作 GitOps 工作流程，自動化 Kubernetes deploy 的完整指南。

## 目的

依循 OpenGitOps 原則，使用 ArgoCD 或 Flux CD，為 Kubernetes 實作宣告式、以 Git 為基礎的持續交付。

## 什麼時候用這個 Skill

- 為 Kubernetes cluster 設定 GitOps
- 從 Git 自動 deploy 應用程式
- 實作漸進式交付策略
- 管理多 cluster deploy
- 設定自動同步政策
- 在 GitOps 中設定 secret 管理

## OpenGitOps 原則

1. **宣告式（Declarative）**：整個系統以宣告的方式描述
2. **版本化且不可變（Versioned and Immutable）**：期望狀態存放在 Git
3. **自動拉取（Pulled Automatically）**：軟體 agent 拉取期望狀態
4. **持續調和（Continuously Reconciled）**：agent 持續調和實際狀態與期望狀態

## ArgoCD 設定

### 1. 安裝

```bash
# 建立 namespace
kubectl create namespace argocd

# 安裝 ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 取得 admin 密碼
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

**參考：** 詳細設定請見 `references/argocd-setup.md`

### 2. Repository 結構

```
gitops-repo/
├── apps/
│   ├── production/
│   │   ├── app1/
│   │   │   ├── kustomization.yaml
│   │   │   └── deployment.yaml
│   │   └── app2/
│   └── staging/
├── infrastructure/
│   ├── ingress-nginx/
│   ├── cert-manager/
│   └── monitoring/
└── argocd/
    ├── applications/
    └── projects/
```

### 3. 建立 Application

```yaml
# argocd/applications/my-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/gitops-repo
    targetRevision: main
    path: apps/production/my-app
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

### 4. App of Apps 模式

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: applications
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/gitops-repo
    targetRevision: main
    path: argocd/applications
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated: {}
```

## Flux CD 設定

### 1. 安裝

這個範例使用 Homebrew。其他系統請依照
[官方 Flux 安裝指南](https://fluxcd.io/flux/installation/)。

```bash
# 用 Homebrew 安裝 Flux CLI
brew install fluxcd/tap/flux
flux check --pre

# Bootstrap Flux
flux bootstrap github \
  --owner=org \
  --repository=gitops-repo \
  --branch=main \
  --path=clusters/production \
  --personal
```

### 2. 建立 GitRepository

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/org/my-app
  ref:
    branch: main
```

### 3. 建立 Kustomization

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 5m
  path: ./deploy
  prune: true
  sourceRef:
    kind: GitRepository
    name: my-app
```

## 同步政策

### 自動同步設定

**ArgoCD：**

```yaml
syncPolicy:
  automated:
    prune: true # 刪除 Git 中不存在的資源
    selfHeal: true # 調和手動做的變更
    allowEmpty: false
  retry:
    limit: 5
    backoff:
      duration: 5s
      factor: 2
      maxDuration: 3m
```

**Flux：**

```yaml
spec:
  interval: 1m
  prune: true
  wait: true
  timeout: 5m
```

**參考：** 請見 `references/sync-policies.md`

## 漸進式交付

### 用 ArgoCD Rollouts 做 Canary Deploy

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
spec:
  replicas: 5
  strategy:
    canary:
      steps:
        - setWeight: 20
        - pause: { duration: 1m }
        - setWeight: 50
        - pause: { duration: 2m }
        - setWeight: 100
```

### Blue-Green Deploy

```yaml
strategy:
  blueGreen:
    activeService: my-app
    previewService: my-app-preview
    autoPromotionEnabled: false
```

## Secret 管理

### External Secrets Operator

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: db-credentials
  data:
    - secretKey: password
      remoteRef:
        key: prod/db/password
```

### Sealed Secrets

```bash
# 加密 secret
kubeseal --format yaml < secret.yaml > sealed-secret.yaml

# 把 sealed-secret.yaml commit 到 Git
```

## 最佳實務

1. **不同環境使用獨立的 repo 或 branch**
2. **為 Git repository 實作 RBAC**
3. **為同步失敗啟用通知**
4. **為自訂資源使用健康檢查**
5. **為 production 實作審核關卡**
6. **不要把 secret 放進 Git**（使用 External Secrets）
7. **使用 App of Apps 模式**做組織
8. **為 release 打 tag**，方便 rollback
9. **用警報監控同步狀態**
10. **先在 staging 測試變更**

## 疑難排解

**同步失敗：**

```bash
argocd app get my-app
argocd app sync my-app --prune
```

**狀態為 Out of sync：**

```bash
argocd app diff my-app
argocd app sync my-app --force
```

## 相關 Skill

- `k8s-manifest-generator`：用於建立 manifest
- `helm-chart-scaffolding`：用於打包應用程式
