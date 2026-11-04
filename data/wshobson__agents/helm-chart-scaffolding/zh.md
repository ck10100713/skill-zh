---
name: helm-chart-scaffolding
description: 設計、組織並管理 Helm chart，用可重複使用的設定來模板化並打包 Kubernetes 應用。適用於建立 Helm chart、打包 Kubernetes 應用，或實作模板化 deploy 的時候。
---

# Helm Chart 腳手架

建立、組織並管理 Helm chart 的完整指引，用於打包並 deploy Kubernetes 應用。

## 目的

這個 skill 提供逐步的說明，用來建立可上 production 的 Helm chart，包含 chart 結構、模板模式、values 管理與驗證策略。

## 什麼時候用這個 Skill

需要做下面這些事情的時候，就用這個 skill：

- 從零開始建立新的 Helm chart
- 打包 Kubernetes 應用以便散布
- 用 Helm 管理多環境 deploy
- 為可重複使用的 Kubernetes manifest 實作模板
- 設定 Helm chart repository
- 遵循 Helm 最佳實務與慣例

## 詳細模式與實作範例

詳細的模式文件放在 `references/details.md`，上面這一層導覽不夠用的時候再去讀那份檔案。

## 最佳實務

1. **使用 semantic versioning** 管理 chart 與 app 的版本
2. **在 values.yaml 中用註解記錄所有 value**
3. **對重複的邏輯使用 template helper**
4. **打包之前先驗證 chart**
5. **明確釘住相依套件的版本**
6. **對選用的資源使用 condition**
7. **遵循命名慣例**（小寫、連字號）
8. **附上 NOTES.txt** 說明用法
9. **用 helper 一致地加上 label**
10. **在所有環境中測試安裝**

## 疑難排解

**模板渲染錯誤：**

```bash
helm template my-app ./my-app --debug
```

**相依套件問題：**

```bash
helm dependency update
helm dependency list
```

**安裝失敗：**

```bash
helm install my-app ./my-app --dry-run --debug
kubectl get events --sort-by='.lastTimestamp'
```


## 相關 Skill

- `k8s-manifest-generator`：用於建立基礎的 Kubernetes manifest
- `gitops-workflow`：用於自動化 Helm chart deploy
