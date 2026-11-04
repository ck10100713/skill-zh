---
name: azure-cloud-migrate
description: "評估跨雲工作負載並遷移到 Azure，附報告和程式碼轉換。支援 Lambda→Functions、Beanstalk/Heroku/App Engine→App Service、Fargate/Kubernetes/Cloud Run/Spring Boot→Container Apps。WHEN: migrate Lambda to Functions, AWS to Azure, migrate Beanstalk, migrate Heroku, migrate App Engine, Cloud Run migration, Fargate to ACA, ECS/Kubernetes/GKE/EKS to Container Apps, Spring Boot to Container Apps, cross-cloud migration."
license: MIT
metadata:
  author: Microsoft
  version: "1.3.2"
---

# Azure Cloud Migrate

> 這個 skill 負責既有雲端工作負載遷移到 Azure 的**評估和程式碼遷移**。

## Rules

1. 依序走完各個 phase，不准跳過
2. 在做任何程式碼遷移之前，先產生評估報告
3. 載入對應情境的 reference，並遵守裡面的規則
4. 使用 `mcp_azure_mcp_get_azure_bestpractices` 和 `mcp_azure_mcp_documentation` MCP tools
5. 目標服務要用最新支援的 runtime
6. 破壞性動作需要 `ask_user`：[functions global-rules](references/services/functions/global-rules.md) | [app-service global-rules](references/services/app-service/global-rules.md)
7. **向使用者回報進度**：執行耗時操作（部署、推 image）時，要提供資源層級的狀態更新，不要讓使用者乾等沒有回饋，見 [workflow-details.md](references/workflow-details.md)
8. **稽核 app 程式碼裡的 service discovery**：Kubernetes DNS 名稱（例如 `http://order-service:3001`）在 Container Apps 裡無法解析。評估時要掃描原始碼中 HTTP client 寫死的 hostname/port，並標記出來，改成用環境變數注入 URL

## Migration Scenarios

| Source | Target | Reference |
|--------|--------|-----------|
| AWS Lambda | Azure Functions | [lambda-to-functions.md](references/services/functions/lambda-to-functions.md) ([assessment](references/services/functions/assessment.md), [code-migration](references/services/functions/code-migration.md)) |
| AWS Elastic Beanstalk | Azure App Service | [beanstalk-to-app-service.md](references/services/app-service/beanstalk-to-app-service.md) |
| Heroku | Azure App Service | [heroku-to-app-service.md](references/services/app-service/heroku-to-app-service.md) |
| Google App Engine | Azure App Service | [app-engine-to-app-service.md](references/services/app-service/app-engine-to-app-service.md) |
| AWS Fargate (ECS) | Azure Container Apps | [fargate-to-container-apps.md](references/services/container-apps/fargate-to-container-apps.md) ([assessment](references/services/container-apps/fargate-assessment-guide.md), [deployment](references/services/container-apps/fargate-deployment-guide.md)) |
| Kubernetes (GKE/EKS/Self-hosted) | Azure Container Apps | [k8s-to-container-apps.md](references/services/container-apps/k8s-to-container-apps.md) |
| GCP Cloud Run | Azure Container Apps | [cloudrun-to-container-apps.md](references/services/container-apps/cloudrun-to-container-apps.md) |
| Spring Boot (Azure Spring Apps/VMs) | Azure Container Apps | [spring-apps-to-aca.md](references/services/container-apps/spring-apps-to-aca.md) |

> 沒有符合的情境？用 `mcp_azure_mcp_documentation` 和 `mcp_azure_mcp_get_azure_bestpractices` tools。

## Output Directory

所有輸出都放在 workspace 根目錄的 `<workspace-root-basename>-azure/`，其中 `<workspace-root-basename>` 是最上層 workspace 目錄本身的名稱（不是裡面的子目錄）。絕對不准修改原始碼目錄。

## Steps

1. **建立** workspace 根目錄下的 `<workspace-root-basename>-azure/`
2. **評估**：分析原始碼、對應服務，並用對應情境的評估指南產生報告 → [functions assessment](references/services/functions/assessment.md) | [app-service assessment](references/services/app-service/assessment.md)
3. **遷移**：用對應情境的遷移指南轉換程式碼/設定 → [functions code-migration](references/services/functions/code-migration.md) | [app-service code-migration](references/services/app-service/code-migration.md)
4. **詢問使用者**：「遷移完成。要在本機測試還是部署到 Azure？」
5. **交接**給 azure-prepare，處理 infrastructure、測試和部署

在 `migration-status.md` 裡追蹤進度，見 [workflow-details.md](references/workflow-details.md)。
