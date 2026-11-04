# Deploy — IaC Execution & Health Verification

## Quick Reference

| Property | Value |
|----------|-------|
| Best for | 對 Azure 執行已驗證的 IaC，並對部署好的資源做健康檢查 |
| Inputs | `.copilot-azure/sessions/{id}/` 裡的 `prepare-plan.json` + `scaffold-manifest.json` |
| Outputs | 寫到 session 目錄的 `deploy-result.json` |
| Parent | [azure-app-onboard](../SKILL.md) |

## When to Use This Skill

當 `scaffold-manifest.json` 存在、而且有 `files[]` 和 `validationResult` 時，由 `azure-app-onboard` orchestrator 在 Phase 4 呼叫。使用者不能直接觸發。

> **回到 orchestrator：** 完成後，把控制權交還給 `azure-app-onboard` 做 handoff（Step 10）。不要開始新的 phase。

## When NOT to Use

| Scenario | Use Instead |
|----------|-------------|
| 規劃架構、對應服務、估算成本 | [prepare](../prepare/SKILL.md) |
| 從 plan 產生 IaC 檔案 | `azure-app-onboard` Step 7 (scaffold) |
| 執行 `azd up` 或既有的部署範本 | `azure-deploy` |
| 部署後除錯正在跑的 app | `azure-diagnostics` |
| 最佳化現有的 Azure 支出 | 選用的 `azure-cost` plugin 裡的 `cost-optimization` |

如果 `cost-optimization` 不能用，要說明它是由選用的 `azure-cost` plugin 提供，
並引導使用者走他們的 client 所支援的 plugin 安裝流程；不要暗示 handoff 已經完成。

## Workflow

> ⛔ **Step 0 一定要委派給 sub-agent。** 讀 `subagent-preflight.md`，然後把 `<<<TEMPLATE_START>>>` / `<<<TEMPLATE_END>>>` 分隔符號之間**完整且未修改**的範本文字，當成 `task` 派出去。不准摘要或改寫範本，sub-agent 需要每一條「Read [file]」的指示，才能產生正確的 `deploy-checklist.md`。Session artifact 的資料要附在範本區塊**後面**。如果你讀完範本之後的下一個動作不是 `task`，就代表你是在 inline 自己執行，而不是委派。

> ⛔ **Healing loop：** 嘗試 3 次後問使用者，之後每 5 次問一次（計數 = `healingAttempts[].length`）。

> ⛔ **Region lock：** 重試 `az deployment` 之前，把 `--location` 和 `prepare-plan.json.deploymentVariables.location` 比對。如果變了 → 需要重新核准的 gate。核准後更新 plan。

> ⛔ **compaction 之後，或任何 `az deployment`/`az webapp deploy`/`az acr build`/health check 失敗之後：重新讀 `deploy-checklist.md`。** 如果檔案不見了 → 從 [`deploy-checklist-template.md`](references/deploy-checklist-template.md) 填一份。如果 context 大量遺失：也要重新讀這份 SKILL.md。

| # | Step | Action | Artifact | Reference |
|---|------|--------|----------|-----------|
| 0 | **Dispatch preflight sub-agent** | ⛔ **你一定要把 [`subagent-preflight.md`](references/subagent-preflight.md) 當成 `task` 派出去。** ⛔ agent_type：`"task"`，絕對不是 `"general-purpose"`。讀完範本後，你的下一個動作一定要是 `task`。如果讀完範本後你的下一個動作是 `powershell`、`view` 或任何不是 `task` 的東西，就停下來，你是在 inline 執行，不是在委派。它會寫出 `deploy-checklist.md`。**回來之後立刻 `view` 它。** | `deploy-checklist.md` | ⛔ **你一定要讀 [`subagent-preflight.md`](references/subagent-preflight.md)** |
| 1 | **Read upstream artifacts** | 載入 `prepare-plan.json` + `scaffold-manifest.json`。檢查 `validationResult`。解析 subscription 和部署變數。 | — | — |
| 3 | **Preflight checks** | 依 `deploy-checklist.md` § Preflight 做 Auth、**強制的 what-if 預覽**、RBAC、RG。 | — | ⛔ **你一定要讀 `deploy-checklist.md`**（發生 compaction 就重讀） |
| 4 | **Deploy approval gate** | 依 `deploy-checklist.md` § Deploy approval gate 的格式，呈現成本和資源摘要。 | — | — |
| 5b | **Write deploy-result.json skeleton** | ⛔ 讀 [`deploy-schemas.ts`](references/deploy-schemas.ts)，寫出 skeleton（`status: "in-progress"`）。一定要在第一個 `az` 指令**之前**就存在。 | `deploy-result.json` | ⛔ **你一定要讀 [`deploy-schemas.ts`](references/deploy-schemas.ts)** |
| 6 | **Execute deployment** | ⛔ **在 `az deployment sub create` 之前：** 產生 portal 連結：`$dn="{deploymentName}"; $r="/subscriptions/{subId}/providers/Microsoft.Resources/deployments/$dn"; $l="https://portal.azure.com/#view/Microsoft_Azure_Resources/DeploymentDetails.MenuView/~/overview/id/$($r.Replace('/','%2F'))"; Write-Output "LINK=$l"`。⛔ **自動在瀏覽器開啟連結：** `Start-Process $l 2>$null`。在聊天裡印出純 URL（可以 ctrl-click）。<br>自動產生**所有** `@secure()` 參數（`openssl rand -base64 32 \| tr -d '/+='`），絕對不要用 `ask_user` 問密碼；重試時從 `deploy-secrets.env` 或 Key Vault 重用，絕對不要重新產生（見 deploy-safety.md § Deploy Checklist）。然後才部署 IaC。 | — | ⛔ **你一定要讀 `deploy-checklist.md`** § Execute deployment |
| 6b | **Deploy application code** | ⛔ 為 `prepare-plan.json.services[]` 裡的**每一個**服務部署程式碼。照 `deploy-checklist.md` § Code deploy 做。 | — | ⛔ **你一定要讀 `deploy-checklist.md`** § Code deploy |
| 7 | **Health-check + SCM re-disable** | 對每個 endpoint 做 HTTP GET（最多 3 輪）。⛔ **多服務的 app：** 還要檢查回應內容有沒有錯誤特徵（`connection refused`、`MODULE_NOT_FOUND`、`localhost`、`SET-IN-DEPLOY-PHASE`），當 app 依賴另一個服務或 KV secret 時，光是 HTTP 200 不代表功能正常。然後 ⛔ 對**每一個** App Service/Functions app 執行下面兩個指令，沒有例外：`az rest --method put --url "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Web/sites/{app}/basicPublishingCredentialsPolicies/scm?api-version=2023-12-01" --headers "Content-Type=application/json" --body '{"properties":{"allow":false}}'`，再驗證：`az rest --method get --url "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Web/sites/{app}/basicPublishingCredentialsPolicies/scm?api-version=2023-12-01" --query properties.allow -o tsv`（一定要回傳 `false`）。 | `deploy-result.json` 完整版 | ⛔ **你一定要讀 `deploy-checklist.md`** § Health check |
| 8 | **Finalize artifacts** | ⛔ 讀 [`deploy-schemas.ts`](references/deploy-schemas.ts)。⛔ 重讀 `deploy-checklist.md` § Artifact verification，做完**全部 5 項**檢查。⛔ **在你覆寫掉 skeleton 的 `deploy-result.json` 之前，不准發出「live」或 handoff 訊息**：把 `status` 從 `"in-progress"` 改掉（→ `succeeded`/`failed`），並填入 healthStatus、endpoints、completedUtc、deploymentNames、healingAttempts。寫 `deployment-summary.md`（狀態表 + 健康狀況 + portal 連結 + 清理指令，內容和你的 handoff 訊息一樣）。更新 `context.json`：把 `"deploy"` 加進 `completedPhases`，`currentPhase: null`，更新 `lastModifiedUtc`。讀回來確認 `status != "in-progress"` 而且 `"deploy"` ∈ `completedPhases`。⛔ **然後停下來，回到 orchestrator。不要再執行任何 CLI 指令。** | `deploy-result.json` 最終版 + `deployment-summary.md` + `context.json` 更新 | ⛔ **你一定要讀 [`deploy-schemas.ts`](references/deploy-schemas.ts)** + ⛔ **重讀 `deploy-checklist.md` § Artifact verification** |
| 9 | **Error handling + healing** | ⛔ **只有在 Step 6/6b/7 回傳非零 exit code 或 health check 失敗時才做。** 順利部署就整個跳過。依 `deploy-checklist.md` § During healing 對錯誤分類、跑 healing loop、處理 PLAN_LEVEL_CHANGE 的重新核准。⛔ **就算無法復原的失敗也一樣：** 回到 orchestrator 之前，要寫出 `status: "failed"` 並帶 `errorDetails` 的 `deploy-result.json`，這個 artifact 一定要存在。 | — | ⛔ **你一定要讀 [`error-classification.md`](references/error-classification.md)** |
