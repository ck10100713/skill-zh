---
name: deployment-pipeline-design
description: 設計帶有審核關卡、安全檢查與 deploy 編排的多階段 CI/CD pipeline。適用於設計零停機 deploy pipeline、實作 canary rollout 策略、建立多環境 promotion 流程，或除錯 CI/CD 中失敗的 deploy 關卡。
---

# Deploy Pipeline 設計

多階段 CI/CD pipeline 的架構模式，包含審核關卡、deploy 策略與環境 promotion 流程。

## 目的

透過適當的階段劃分、自動化品質關卡與漸進式交付策略，設計出穩健又安全、兼顧速度與安全性的 deploy pipeline。這個 skill 同時涵蓋 pipeline 架構的結構設計，以及讓 production deploy 可靠的營運模式。

## 輸入 / 輸出

### 你要提供的東西

- **應用程式類型**：語言/runtime、容器化或 bare-metal、monolith 或 microservices
- **Deploy 目標**：Kubernetes、ECS、VM、serverless，或 platform-as-a-service
- **環境拓樸**：環境數量（dev/staging/prod）、region 配置、air-gap 需求
- **Rollout 需求**：可接受的停機時間、rollback SLA、流量切分需求、偏好 canary 還是 blue-green
- **關卡限制**：審核的團隊、要求的測試覆蓋率門檻、合規掃描（SAST、DAST、SCA）
- **監控堆疊**：Prometheus、Datadog、CloudWatch，或其他用於自動 promotion 決策的指標來源

### 這個 Skill 會產出什麼

- **Pipeline 設定**：階段定義、job 相依關係、平行度與快取策略
- **Deploy 策略**：選定的 rollout 模式，並附上註解過的設定（canary 權重、blue-green 切換、rolling 參數）
- **健康檢查設定**：淺層與深層的 readiness probe、deploy 後的 smoke test 腳本
- **關卡定義**：自動化的指標門檻與人工審核流程
- **Rollback 計畫**：自動 rollback 的觸發條件與手動 runbook 步驟

## 什麼時候用

- 為新服務或平台 migration 設計 CI/CD 架構
- 在環境之間實作 deploy 關卡
- 設定強制安全掃描的多環境 pipeline
- 用 canary 或 blue-green 策略建立漸進式交付
- 除錯各階段都成功、但 production 行為不對的 pipeline
- 透過指標惡化時自動 rollback，縮短平均復原時間

## 詳細模式與實作範例

詳細的模式文件放在 `references/details.md`，上面這一層導覽不夠用的時候再去讀那份檔案。

## 疑難排解

### Pipeline 裡健康檢查通過，但 production 的服務卻不健康

Pipeline 的健康檢查打的是淺層的 `/ping` endpoint，就算資料庫連不上它也會回 200。要改用會驗證實際相依項目的深層 readiness 檢查（見上面的健康檢查章節）。

### Canary deploy 永遠沒有 promote 到 100%

Argo Rollouts 需要有效的 `AnalysisTemplate` 才能自動 promote。如果 Prometheus query 沒有回傳資料（例如 metric 名稱改了），分析會一直是 inconclusive，promotion 就卡住。加上 `inconclusiveLimit`，讓 rollout 快速失敗，不要一直掛著：

```yaml
spec:
  metrics:
  - name: error-rate
    failureCondition: "result[0] > 0.05"
    inconclusiveLimit: 2   # inconclusive 兩次後就失敗，不要無限期掛著
    provider:
      prometheus:
        query: |
          sum(rate(http_requests_total{status=~"5.."}[2m]))
          / sum(rate(http_requests_total[2m]))
```

### Staging deploy 成功，但 production job 一直沒啟動

檢查 production 環境的保護規則有沒有設定好。沒指派 reviewer 的話，審核關卡會一直等下去，而且不會有任何通知。在 GitHub Actions 中，確認 **Settings → Environments → production** 的 `Required reviewers` 已設為既有的使用者或團隊。

### Docker layer cache 每次都失效，導致 build 很慢

如果 `COPY . .` 出現在安裝相依套件之前，任何一個原始碼檔案有變動，都會讓相依套件那一層失效。調整順序，先複製相依套件的 manifest：

```dockerfile
# 好的做法：相依套件和原始碼分開快取
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
```

### Rollback 之後資料庫 migration 還留在舊程式碼上

只 rollback 服務、沒有 rollback migration，會造成 schema 和程式碼不一致的錯誤。至少在一個 release 週期內，migration 一律要保持向下相容（只做新增），並把 undo 腳本跟 migration 一起版本化：

```bash
# migrations/V20240315__add_nullable_column.sql       （正向）
# migrations/V20240315__add_nullable_column.undo.sql  （反向）
```

在舊版程式碼完全從所有環境下線之前，絕對不准執行破壞性的 migration（DROP COLUMN、ALTER NOT NULL）。

## 進階主題

平台專屬的 pipeline 設定、多 region promotion 流程，以及進階的 Argo Rollouts 模式，請見：

- [`references/advanced-strategies.md`](references/advanced-strategies.md)：延伸的 YAML 範例、平台專屬設定（GitHub Actions、GitLab CI、Azure Pipelines）、多 region canary 模式，以及資料庫 migration 的 rollback 策略

## 相關 Skill

- `github-actions-templates`：GitHub Actions 實作模式與可重用 workflow
- `gitlab-ci-patterns`：GitLab CI/CD pipeline 實作
- `secrets-management`：CI/CD pipeline 中的 secret 處理
