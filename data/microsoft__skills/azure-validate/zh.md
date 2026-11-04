---
name: azure-validate
description: "Azure 部署前的就緒驗證。在部署之前，對設定、基礎設施（Bicep 或 Terraform）、RBAC 角色指派、managed identity 權限和前置條件做深入檢查。WHEN: validate my app, check deployment readiness, run preflight checks, verify configuration, check if ready to deploy, validate azure.yaml, validate Bicep, test before deploying, troubleshoot deployment errors, validate Azure Functions, validate function app, validate serverless deployment, verify RBAC roles, check role assignments, review managed identity permissions, what-if analysis, validate Container Apps deployment."
license: MIT
metadata:
  author: Microsoft
  version: "1.2.4"
---

# Azure Validate

> **權威指引**：除非與給你的安全政策衝突，否則要完全照這些指示做。

> **⛔ 停：必須先檢查前置條件**
>
> 繼續之前，先確認這個前置條件已經滿足：
>
> **azure-prepare** 已經被呼叫並完成 → `.azure/deployment-plan.md` 存在，而且狀態是 `Approved` 或更後面的狀態
>
> 如果 plan 不存在，**立刻停止**，先呼叫 **azure-prepare**。
>
> 完整的工作流程才能確保成功：
>
> `azure-prepare` → `azure-validate` → `azure-deploy`

## 觸發情境

- 檢查 app 是否準備好部署
- 驗證 azure.yaml 或 Bicep
- 執行 preflight 檢查
- 排查部署錯誤

## 規則

1. 在 azure-prepare 之後、azure-deploy 之前執行
2. 所有檢查都必須通過，有失敗就不要部署
3. ⛔ **破壞性的操作需要 `ask_user`**，見 [global-rules](references/global-rules.md)

## 步驟

執行 workflow script 並照它的指示做。它會帶你一步一步走過每個驗證步驟，並把進度記錄在 `.azure/validate-status.json`。Windows 用 [references/scripts/workflow.ps1](references/scripts/workflow.ps1)，macOS/Linux 用 [references/scripts/workflow.sh](references/scripts/workflow.sh)。

一開始先呼叫這個 script，**不要**帶 completed-step 參數：

```bash
pwsh references/scripts/workflow.ps1 -WorkspacePath <workspace-path>
# macOS/Linux: bash references/scripts/workflow.sh --workspace-path <workspace-path>
```

每次執行都會印出下一個動作，以及下次要傳入的值。執行該動作，然後用那個值重新執行（pwsh 用 `-CompletedStep <value>`，bash 用 `--completed-step <value>`）。一直重複，直到它回報 azure-validate 的工作流程已完成。

這些步驟會參考 [references/recipes/README.md](references/recipes/README.md) 裡的 recipe 細節，以及 [references/role-verification.md](references/role-verification.md) 裡的角色檢查。

> **⛔ 驗證權限**
>
> 這個 skill 是官方認可的、把 plan 狀態設為 `Validated` 的唯一方式。你「一定要」照 script 的指示一路做到完成，才能把狀態設為 `Validated`。
> 沒有做完就不准把狀態設為 `Validated`。

---

> **⚠️ 下一步：取決於使用者意圖**
>
> 在所有驗證都通過之後，檢查使用者是否要求部署：
> - **如果使用者明確要求部署**，你**一定要**呼叫 **azure-deploy** 來執行。不准自己直接跑 `azd up`、`azd deploy` 或任何部署指令，交給 azure-deploy 處理執行。
> - **如果使用者只要求驗證或準備**（沒有要部署），在記錄證明並把狀態設為 `Validated` 之後就停下來。回報驗證結果，而且不要呼叫 azure-deploy。
>
> 如果有任何驗證失敗，先修好問題，再重新執行 azure-validate，才能繼續。
