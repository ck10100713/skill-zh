---
name: azure-deploy
description: "對「已經準備好」、且有現成 .azure/deployment-plan.md 和基礎設施檔案的應用程式執行 Azure 部署。使用者要求「建立」新應用程式時不要用這個 skill，改用 azure-prepare。這個 skill 會執行 azd up、azd deploy、terraform apply 和 az deployment 指令，並內建錯誤復原。需要 azure-prepare 產生的 .azure/deployment-plan.md，以及 azure-validate 驗證過的狀態。WHEN: \"run azd up\", \"run azd deploy\", \"execute deployment\", \"push to production\", \"push to cloud\", \"go live\", \"ship it\", \"bicep deploy\", \"terraform apply\", \"publish to Azure\", \"launch on Azure\". DO NOT USE WHEN: \"create and deploy\", \"build and deploy\", \"create a new app\", \"set up infrastructure\", \"create and deploy to Azure using Terraform\"，這些情況改用 azure-prepare。"
license: MIT
metadata:
  author: Microsoft
  version: "1.2.2"
---

# Azure Deploy

> **權威指引：必須遵守**
>
> **前置條件**：執行這個 skill 之前，**必須**已經呼叫 **azure-validate** skill，並且完成、狀態為 `Validated`。

> **⛔ 停：必須先檢查前置條件**
> 繼續之前，確認兩個前置條件都滿足：
>
> 1. **azure-prepare** 已呼叫並完成 → `.azure/deployment-plan.md` 存在
> 2. **azure-validate** 已呼叫並通過 → plan 狀態 = `Validated`
>
> 只要缺任何一個，**立刻停下來**：
> - 沒有 plan？ → 先呼叫 **azure-prepare** skill
> - 狀態不是 `Validated`？ → 先呼叫 **azure-validate** skill
>
> **⛔ 不准手動更新 plan 狀態**
>
> **禁止**你自己把 plan 狀態改成 `Validated`。只有 **azure-validate** skill 在跑過實際的驗證檢查之後，才有權設定這個狀態。沒跑驗證就改狀態，部署一定會失敗。
>
> **不准假設**app 已經準備好。**不准跳過**驗證來省時間。跳步驟會造成部署失敗。完整流程才能確保成功：
>
> `azure-prepare` → `azure-validate` → `azure-deploy`

## 觸發條件

使用者想做下面這些事時啟用這個 skill：
- 對已經準備好的應用程式執行部署（azure.yaml 和 infra/ 都已存在）
- 把更新推到現有的 Azure 部署
- 在已準備好的專案上執行 `azd up`、`azd deploy` 或 `az deployment`
- 把已經建置好的程式碼上線到正式環境
- 部署一個已包含 API Management (APIM) gateway 基礎設施的應用程式

> **範圍**：這個 skill 負責執行部署，不負責建立應用程式、產生基礎設施程式碼或建立專案骨架。這些事請用 **azure-prepare**。

> **APIM / AI Gateway**：這個 skill 用來部署那些 APIM/AI gateway 基礎設施已在 **azure-prepare** 階段建好的應用程式。要建立或修改 APIM 資源，請看 [APIM 部署指南](https://learn.microsoft.com/azure/api-management/get-started-create-service-instance)。AI 治理 policy 的部分，呼叫 **azure-aigateway** skill。

## 規則

1. 在 azure-prepare 和 azure-validate 之後執行
2. `.azure/deployment-plan.md` 必須存在，且狀態為 `Validated`
3. **必須做部署前檢查清單**：[Pre-Deploy Checklist](references/pre-deploy-checklist.md)
4. ⛔ **破壞性動作必須先 `ask_user`**：[global-rules](references/global-rules.md)
5. **範圍：只負責執行部署**：這個 skill 擁有 `azd up`、`azd deploy`、`terraform apply` 和 `az deployment` 指令的執行權。這些指令都要經過這個 skill 的錯誤復原和驗證流程。

---

## 步驟

| # | 動作 | 參考 |
|---|--------|-----------|
| 1 | **檢查 Plan**：讀 `.azure/deployment-plan.md`，確認狀態 = `Validated` 而且 **Validation Proof** 區段有內容 | `.azure/deployment-plan.md` |
| 2 | **部署前檢查清單**：每一步都必須完成 | [Pre-Deploy Checklist](references/pre-deploy-checklist.md) |
| 3 | **載入 Recipe**：依 `.azure/deployment-plan.md` 裡的 `recipe.type` 決定 | [recipes/README.md](references/recipes/README.md) |
| 4 | **RBAC 健康檢查**：對使用 managed identity 的 Container Apps + ACR，先跑 `azd provision --no-prompt`，再確認 `AcrPull` 角色已經生效，才能繼續（見檢查清單） | [Pre-Deploy Checklist — Container Apps RBAC](references/pre-deploy-checklist.md#container-apps--acr--pre-deploy-rbac-health-check) |
| 5 | **執行部署**：照 recipe 的步驟做 | Recipe README |
| 6 | **部署後**：設定 SQL managed identity，適用的話再套用 EF migration | [Post-Deployment](references/recipes/azd/post-deployment.md) |
| 7 | **處理錯誤**：看 recipe 的 `errors.md` | — |
| 8 | **確認成功**：確認部署完成，endpoint 也連得到 | [Verification](references/recipes/azd/verify.md) |
| 9 | **即時角色驗證**：查詢 Azure，確認佈建出來的 RBAC 角色正確而且夠用 | [live-role-verification.md](references/live-role-verification.md) |
| 10 | **回報結果**：把部署好的 endpoint URL 用完整的 `https://` 連結呈現給使用者 | [Verification](references/recipes/azd/verify.md) |

> **⛔ URL 格式規則**
>
> 呈現 endpoint URL 給使用者時，**一定要**用帶 `https://` scheme 的完整 URL（例如 `https://myapp.azurewebsites.net`，不是 `myapp.azurewebsites.net`）。很多 Azure CLI 指令只回傳沒有 scheme 的 hostname，呈現之前一律先補上 `https://`。

> **⛔ 驗證證明檢查**
>
> 檢查 plan 時，確認 **Validation Proof** 區段（第 7 節）裡有實際的驗證結果，包含執行過的指令和時間戳記。如果這個區段是空的，代表驗證被跳過了，要先呼叫 **azure-validate** skill。

## SDK 快速參考

- **Azure Developer CLI**：[azd](references/sdk/azd-deployment.md)
- **Azure Identity**：[Python](references/sdk/azure-identity-py.md) | [.NET](references/sdk/azure-identity-dotnet.md) | [TypeScript](references/sdk/azure-identity-ts.md) | [Java](references/sdk/azure-identity-java.md)

## MCP 工具

| 工具 | 用途 |
|------|---------|
| `mcp_azure_mcp_subscription_list` | 列出可用的訂閱 |
| `mcp_azure_mcp_group_list` | 列出訂閱中的資源群組 |
| `mcp_azure_mcp_azd` | 執行 AZD 指令 |
| `azure__role` | 列出角色指派，用於即時 RBAC 驗證（步驟 9） |

## 參考

- [Troubleshooting](references/troubleshooting.md)：常見問題和解法
- [Post-Deployment Steps](references/recipes/azd/post-deployment.md)：SQL + EF Core 設定
