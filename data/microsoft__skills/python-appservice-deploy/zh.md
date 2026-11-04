---
name: python-appservice-deploy
description: "把 Python（Flask/Django/FastAPI）程式碼 deploy 到 Azure App Service Linux。WHEN: \"Flask App Service\", \"Django App Service\", \"FastAPI App Service\", \"deploy Python to App Service\"。DO NOT USE FOR: Container Apps、Functions、非 Python、Terraform/Bicep/IaC、完整基礎設施，這些請用 azure-prepare。"
license: MIT
metadata:
  author: Microsoft
  version: "1.1.1"
---

# Python on Azure App Service：程式碼 Deploy

把 Python（Flask、Django、FastAPI、一般 Python）程式碼 deploy 到 Azure App Service Linux（P0v3、Python 3.14）。如果 RG + Plan + Web App 不存在就會建立。需要 VNet、Key Vault、資料庫或 IaC 時，交給 `azure-prepare`。

**使用的 MCP 工具**：`mcp_azure_mcp_subscription_list`、`mcp_azure_mcp_group_list`、`mcp_azure_mcp_appservice`、`mcp_azure_mcp_azd`（有 `azure.yaml` 時）。

## 流程

1. **解析 context，用聰明的預設值，盡量少問。** 只有 app 名稱需要互動輸入；RG（`<app>-rg`）、Plan（`<app>-plan`）、region（目前 `az` 的預設值或 `eastus2`）、subscription 都是推導出來的。見 [create-app.md](references/create-app.md) §1。
2. **偵測 framework**（僅供參考，絕不擋住流程）。見 [detect.md](references/detect.md)。
3. **選擇路徑**：`azure.yaml` 的 host 是 appservice → [deploy-azd.md](references/deploy-azd.md)；否則用 [deploy-azcli.md](references/deploy-azcli.md)。
4. **確保 RG → Plan（`P0v3 --is-linux`）→ Web App（`--runtime "PYTHON:3.14"`）都存在。** 遇到暫時性的 ARM 錯誤，照 [transient-retry.md](references/transient-retry.md) 處理。見 [create-app.md](references/create-app.md)。
5. **設定啟動指令**：Flask/Django 不用設（Oryx 會自動偵測）。FastAPI 一律用 `python -m uvicorn main:app --host 0.0.0.0`。其他：發出警告。見 [startup-commands.md](references/startup-commands.md)。
6. **設定 `SCM_DO_BUILD_DURING_DEPLOYMENT=true`**。
7. **Deploy**：用 `azd deploy` 或 `az webapp deploy --type zip --track-status false`。
8. **停。印出 post-deploy 訊息**（[post-deploy-message.md](references/post-deploy-message.md)），然後結束這一輪。

### 硬性規則

- ⛔ **不准做部署後驗證**：deploy 回傳之後，不要跑 `az webapp log tail`、`curl`、`Invoke-WebRequest` 或任何健康檢查。App Service 要 2 到 3 分鐘暖機，log 沒東西或早期出現 5xx 不代表失敗。
- ⛔ **Shell 安全**：`--runtime` 一律用 `"PYTHON:3.14"`（冒號）。絕對不要用 `"PYTHON|3.14"`（管線符號是 shell 運算子）。
- ⛔ **絕對不要用 `az webapp up`**：已經棄用。請用步驟 7 的指令。
- ✅ **URL 格式**：端點要以 `https://...` 的 URL 呈現。

## 錯誤處理

完整的「症狀 → 原因 → 修法」對照表見 [errors.md](references/errors.md)。快速判斷：缺少 plan/app → 重跑步驟 4；容器在 8000 port 的 ping 逾時 → 修正啟動指令（步驟 5）；deploy 後出現 `ModuleNotFoundError` → 確認步驟 6 有跑，然後重新 deploy。
