# Azure App Onboard Scaffold：產生 IaC + 自我審查

依照架構計畫產生可以直接 deploy 的基礎設施程式碼，用對抗式自我審查來驗證，再銜接到驗證階段，整個過程完全不 deploy。

## 快速參考

| 屬性 | 值 |
|----------|-------|
| 上層 | [azure-app-onboard](../SKILL.md) |
| 最適合 | 把 `prepare-plan.json` 的服務清單變成預設安全的 Bicep 範本 |
| 輸入 | `prepare-plan.json`（服務、命名、配額）、`context.json`（overrides、元件、repo 資訊） |
| 輸出 | `scaffold-manifest.json`、`infra/` 裡產生的 IaC 檔案 |
| Pipeline 位置 | 四個階段中的第 3 階段：prereq → prepare → **scaffold** → deploy |
| IaC 格式 | Bicep（v1 預設）。偵測到現有 `.tf` 或使用者 override 時用 Terraform。 |

## 什麼時候用這個 Skill

由 `azure-app-onboard` orchestrator 在 Phase 3 呼叫，前提是 `prepare-plan.json` 存在且有 `services[]`。v1 中使用者不能直接呼叫。

> **回到 orchestrator：** 完成後，把控制權交回 `azure-app-onboard`。絕對不要直接呼叫 deploy，階段轉換由 orchestrator 管理。

## 什麼時候不要用

| 情境 | 改用 |
|----------|-------------|
| 使用者觸發的 IaC（沒有 `prepare-plan.json`） | `azure-prepare` |
| Subscription 層級的 landing zone | `azure-enterprise-infra-planner` |
| 執行 deployment（`azd up`） | `azure-deploy`（不要從 AppOnboard pipeline 呼叫） |

## MCP 工具

> 跨階段工具和全域參數請看 [shared tools](../references/mcp-tool-reference.md)。完整的參數表請看 [scaffold tools](references/mcp-tools.md)。

| 工具 | 子指令 | 用途 | 參數 |
|------|-----------|---------|------------|
| `mcp_azure_mcp_bicepschema` | `bicepschema_get` | ARM 資源類型 schema | `resource_type`（必填）、`api_version`（選填） |
| `mcp_bicep_list_avm_metadata` | *(flat)* | AVM 模組目錄 | 無 |
| `mcp_bicep_get_bicep_best_practices` | *(flat)* | Bicep 最佳實務 | 無 |
| `mcp_bicep_get_az_resource_type_schema` | *(flat)* | ARM 資源類型 JSON schema | `azResourceType`、`apiVersion`（必填） |
| `mcp_bicep_build_bicep` | *(flat)* | 驗證 `.bicep` 檔案（自我審查 L3） | `filePath`（必填） |
| `mcp_bicep_format_bicep_file` | *(flat)* | 格式化 `.bicep` 檔案（強制 LF） | `filePath`（必填） |
| `mcp_azure_mcp_deploy` | `deploy_iac_rules_get` | IaC 最佳實務和規則 | `deployment-tool`、`iac-type`、`resource-types` |
| `mcp_azure_mcp_deploy` | `deploy_pipeline_guidance_get` | CI/CD pipeline 設定 | `is-azd-project`、`pipeline-platform`、`deploy-option` |
| `mcp_azure_mcp_get_azure_bestpractices` | `get_azure_bestpractices_get` | SDK/Functions 最佳實務 | `resource`、`action` |
| `mcp_azure_mcp_azureterraformbestpractices` | *(flat)* | Terraform 寫法（只在 TF 路徑用） | `resource_type`（必填） |

## 流程

**Session 資料夾：** `.copilot-azure/sessions/{uuid}/`：讀取 `prepare-plan.json` + `context.json`，寫入 `scaffold-manifest.json`。

### DETECT（步驟 1 到 4）

1. **讀取 `prepare-plan.json`**：確認 `services[]` 存在，讀取 `naming` 設定（尤其是 `naming.resourcePrefix`、`naming.suffix`、`naming.resources[]`）。從 `context.json.azure.resourceGroup` 讀取 resource group 名稱。⛔ **在產生的 IaC 裡要一字不差地使用這些名稱，不准自己發明名稱、不准從 `environmentName` 推導、不准自己加 suffix。** ⛔ **要一字不差地使用 `prepare-plan.json.naming.resources[]` 的名稱當作 Bicep 參數。不准用 `take()`、`substring()` 或字串操作來推導名稱。計畫就是唯一的資料來源。** 缺少 → 透過 `azure-app-onboard` orchestrator 觸發 prepare 補跑。
2. **讀取 `context.json`**：檢查 `overrides[]` 有沒有 `iacFormat` 偏好，`detectedInfra[]` 有沒有現有的 `.tf`，`detectedInfraProvider` 的雲端供應商分類。
3. **檢查 workspace 有沒有現有的 IaC**：⛔ 如果 `context.json.overrides[]` 包含 `ignoreExistingInfra: true`，**跳過**。否則：
   - **Azure IaC**（`.bicep`、`azure.yaml`、帶 `azurerm` 的 `.tf`）：用 `ask_user` 問「Start fresh」（把 `infra/` 改名成 `infra.bak/`）或「Use existing」（導向 `azure-prepare`，停止 pipeline）。
   - **非 Azure IaC**（GCP/AWS 的 `.tf`）：遵照 prepare 階段的 `context.json.overrides[].iacFormat`。預設：在現有 TF 旁邊用 Bicep。
   - **未知的 TF**（`detectedInfraProvider.terraform` == `"unknown"`）：先問使用者是哪個 provider 再導向。
   - **沒有 IaC**：繼續。
4. **決定運算目標**：檢查計畫裡有哪些運算目標（App Service/Functions、Container Apps，或兩者都有），以及有沒有 PostgreSQL/Redis。不要讀任何參考檔案，在步驟 5 把這些資訊傳給 sub-agent。
4b. **預先檢查 API 版本（主執行緒）**：MCP 工具在 `task` agent 裡不可靠，所以要在派出前先在主執行緒呼叫。對 `prepare-plan.json.services[]` 裡每個 provider namespace（例如 `Microsoft.Web`、`Microsoft.App`、`Microsoft.DBforPostgreSQL`、`Microsoft.Cache`、`Microsoft.KeyVault`、`Microsoft.ContainerRegistry`），各呼叫一次 `mcp_bicep_list_az_resource_types_for_provider`（或 `bicep-list_az_resource_types_for_provider`）。為每個資源類型取出最新的 GA API 版本（不含 `-preview`）。建立 `apiVersions` map，在步驟 5 傳給 IaC 產生用的 sub-agent。備案：如果 MCP 無法使用，就對每個資源類型執行 `az provider show --namespace {ns} --query "resourceTypes[?resourceType=='{type}'].apiVersions[?!contains(@, 'preview')] | [0][0]" -o tsv`，這會篩成只有 GA 並選出最新的。只有 MCP 和 CLI 都失敗時，才傳 `"MCP unavailable"`。Sub-agent 仍然會用 `az bicep build` 驗證產生的 Bicep。

### ACTION（步驟 5 到 12）

> ⛔ **檔案邊界：** 絕對不准修改 `infra/`、`.copilot-azure/` 以外的檔案。Scaffold 只寫檔案，不跑 install/build 指令。

> ⛔ **步驟 5、6 到 9、10 到 12 一定要委派給 sub-agent。** 每個步驟都要先讀它的 `subagent-*.md` 範本，再派出 `task` 呼叫。這些步驟沒有明確點名的參考檔案，一個都不要讀。
>
> ⛔ **派出類型：只能用 `task`，絕對不要用 `general-purpose`。** `general-purpose` 會把 sub-agent 的 context 漏到主執行緒，加速 compaction 並把 orchestrator 的流程擠掉。`task` 會隔離 sub-agent 的 context。
>
> ⛔ **派出方式：一定要逐字複製：**
> 1. 用 `view` 看 `subagent-*.md` 範本檔
> 2. 你的**下一個動作一定要是 `task` 工具呼叫**，不能是 `view`、`powershell`、`create` 或任何其他工具
> 3. task prompt 一定要包含**完整且未經修改**的範本文字。要照下面的樣子，把範本放在 `<<<TEMPLATE_START>>>` / `<<<TEMPLATE_END>>>` 分隔符號之間原封不動複製。不准摘要、改寫、換字或省略任何部分，sub-agent 需要每一個「Read [file]」和「Do:」指示才能產出正確結果
> 4. 範本區塊**之後**，再附加資料段落（計畫 JSON、overrides 等）
>
> **反模式（會造成退化）：** 自己寫一個 prompt，列出流程步驟或描述要產生什麼。範本已經包含完整的流程，你的工作是複製它，不是重寫它。

5. **IaC 產生**：⛔ **你一定要把 [`subagent-iac-gen.md`](references/subagent-iac-gen.md) 當作 `task` 派出。** ⛔ agent_type：`"task"`，絕對不要用 `"general-purpose"`。
   ```
   <<<TEMPLATE_START>>>
   {paste the ENTIRE content of subagent-iac-gen.md here — unmodified}
   <<<TEMPLATE_END>>>

   ## Data (appended by orchestrator)
   ### prepare-plan.json
   {full JSON}
   ### context.json.overrides
   {overrides array}
   ### prereq-output.json.buildRequirements
   {buildRequirements object}
   ### prereq-output.json.warnings[]
   {warnings array}
   ### Compute targets
   {App Service/Functions, Container Apps, or both + whether PostgreSQL/Redis present}
   ### apiVersions
   {map from Step 4b, e.g. {"Microsoft.KeyVault/vaults": "2023-07-01", ...} — or "MCP unavailable" if skipped}
   ### Working directory
   {absolute path}
   ```
   - **預期結果：** IaC 檔案寫到 `infra/`，並回傳檔案清單，供 `scaffold-manifest.json.files[]` 使用
   - 產生的 Bicep 裡，一定要原封不動出現 `app-onboard-skill: 'true'` 這個 tag。

5b. **Deploy 檢查清單（和步驟 5 平行）**：和上面的 IaC 產生 subagent **平行**以 `task` 派出。⛔ agent_type：`"task"`，絕對不要用 `"general-purpose"`。
   ```
   <<<TEMPLATE_START>>>
   You are a deploy-checklist generator. Do NOT invoke any skills.

   1. Read the deploy-checklist-template at: plugin/skills/azure-app-onboard/deploy/references/deploy-checklist-template.md
   2. Fill in {placeholders} with real values from prepare-plan.json (appName, rgName, subscriptionId, sessionId).
   3. Delete sections that don't apply to this deployment's compute target (e.g., remove App Service section for Container Apps deploys). The template section headers indicate which to delete.
   4. Write the result to the session folder using the `create` tool. This file survives conversation compaction — deploy re-reads it after every long-running command.
   <<<TEMPLATE_END>>>

   ## Data (appended by orchestrator)
   ### prepare-plan.json
   {full JSON}
   ### Session path
   {.copilot-azure/sessions/{uuid}/}
   ### Compute targets
   {App Service, Container Apps, Static Web Apps, or combination}
   ```
   - **預期結果：** `deploy-checklist.md` 寫到 session 資料夾。如果這個 subagent 失敗，validate subagent（步驟 10b 到 12.5）會抓到缺少的檔案。

6 到 9. **自我審查**：⛔ **你一定要把 [`subagent-review.md`](references/subagent-review.md) 當作 `task` 派出。** ⛔ agent_type：`"task"`，絕對不要用 `"general-purpose"`。
   ```
   <<<TEMPLATE_START>>>
   {paste the ENTIRE content of subagent-review.md here — unmodified}
   <<<TEMPLATE_END>>>

   ## Data (appended by orchestrator)
   ### Generated IaC files
   {full content of every .bicep/.tf file}
   ### prepare-plan.json (services, naming, deploymentVariables)
   {relevant sections}
   ### prereq-output.json.warnings[]
   {warnings array}
   ```
   - **預期結果：** findings JSON → 寫到 `scaffold-manifest.json.selfReview`
   - L1/L3 被標記（FLAGGED）→ 先修好 IaC 再繼續

### VALIDATE → MANIFEST → APPROVE（步驟 10 到 12.5）

10a. **格式化 IaC（主執行緒）**：對 `infra/`（包含 `modules/`）裡每個 `.bicep` 檔案，用 `{ filePath: "<absolute path>" }` 呼叫 `mcp_bicep_format_bicep_file`（或 `bicep-format_bicep_file`）。這會透過 IaC 產生時寫下的 `bicepconfig.json` 強制使用 LF 換行。備案：無法使用就跳過。

10a-conf. **Conformance 關卡（主執行緒，Bicep 一定要做）**：⛔ **如果 scaffold 輸出的是 Terraform（沒有 `infra/main.bicep`），整個步驟跳過**，這些檢查只適用 Bicep（Terraform 由 validate subagent 用 `terraform validate` 做語法驗證）。否則，執行這個 skill `scripts/` 目錄裡的 conformance script，它能確定性地抓到 `az bicep build` 抓不到、但 ARM 會拒絕的值（無效的 Bicep 值、錯誤的 DB 版本、保留的 DB 登入名稱、`enablePurgeProtection`）：
   ```
   {scaffoldDir}/scripts/scaffold-conformance.ps1 -SessionPath ".copilot-azure/sessions/{uuid}" -InfraPath infra   # pwsh (preferred)
   bash {scaffoldDir}/scripts/scaffold-conformance.sh ".copilot-azure/sessions/{uuid}" infra                       # bash (only if pwsh unavailable; needs jq for the plan-dependent checks)
   ```
   ⛔ **有 `pwsh` 就優先用 `.ps1`**，它會無條件跑完所有檢查。`.sh` 版本在沒有 `jq` 時，會跳過依賴計畫的檢查（`DB-VERSION-MATCH`、`SERVICES-COMPLETE`、`DB-NAME-PRESENT`、`WARN-FIXED`）。
   ⛔ 只要有任何 BLOCK 失敗 → 修好 IaC 再重跑（最多 3 次）；只要還有未解決的 BLOCK，絕對不准出現 deploy 關卡。要在這裡的主執行緒跑，不要委派給 validate subagent，有 shell 的時候也不要靠人工判斷結果。把 JSON 傳給 validate subagent，供 `scaffold-manifest.json.conformance` 使用。

10b 到 12.5. **驗證 + manifest**：⛔ **你一定要把 [`subagent-validate.md`](references/subagent-validate.md) 當作 `task` 派出。** ⛔ agent_type：`"task"`，絕對不要用 `"general-purpose"`。
   ```
   <<<TEMPLATE_START>>>
   {paste the ENTIRE content of subagent-validate.md here — unmodified}
   <<<TEMPLATE_END>>>

   ## Data (appended by orchestrator)
   ### IaC file paths
   {list of generated files}
   ### Self-review findings (from Steps 6–9)
   {findings JSON}
   ### prepare-plan.json
   {full JSON}
   ### prereq-output.json.warnings[]
   {warnings array}
   ### prereq-output.json.healthEndpoint
   {detected health path string or null}
   ### Conformance result
   {JSON from Step 10a-conf}
   ### Session path
   {.copilot-azure/sessions/{uuid}/}
   ```
   - **預期結果：** 產生帶有 `validationResult` 的 `scaffold-manifest.json`，以及 deploy 檢查清單
   - 確認 `deploy-checklist.md` 存在（步驟 5b 寫的），如果缺少，現在就從 [`deploy-checklist-template.md`](../deploy/references/deploy-checklist-template.md) 建立。確認 `deploy-result.json` 存在，如果缺少，就從 [`deploy-schemas.ts`](../deploy/references/deploy-schemas.ts) 建立。
   - ⛔ **確認 `context.json` 有更新（主執行緒，不要委派）。** 讀 `.copilot-azure/sessions/{uuid}/context.json`。如果 `completedPhases` 不含 `"scaffold"`，或 `currentPhase` 不是 `"deploy"`，就自己用 `edit` / `create` 寫入：把 `"scaffold"` 加進 `completedPhases`，把 `currentPhase` 設成 `"deploy"`，把 `lastModifiedUtc` 更新成目前的 UTC ISO 8601 時間。這是 [pipeline-rules.md](../references/pipeline-rules.md) 要求的階段邊界寫入，不准跳過。
   - ⛔ **回到 orchestrator 做步驟 8（Deploy 核准關卡）。** 你的下一個動作一定要是依照 orchestrator SKILL.md 顯示 Deploy 關卡，不要寫「已產生檔案的摘要」訊息，不要送出完成報告。Deploy 關卡的提示（`🚀 Ready to deploy? ...`）是唯一正確的下一個輸出。

## 自我修復迴圈

驗證失敗時 → 讀 [`scaffold-healing-rules.md`](references/scaffold-healing-rules.md)（修復節奏、PLAN_LEVEL_CHANGE、產出物一致性）。不要預先讀。

## 錯誤處理

- **缺少 `prepare-plan.json`：** 透過 orchestrator 觸發補跑。
- **已有 IaC：** 在 DETECT 步驟 3 處理。
- **MCP 無法使用：** 退回參考範例的寫法，並標記為「未驗證」。
- 被標記的 FLAGGED 發現和修復次數用盡：見 [scaffold-healing-rules.md](references/scaffold-healing-rules.md)。
