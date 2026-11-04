---
name: azure-prepare
description: "替以 azd 為基礎的 Azure 專案準備部署：為 Azure Developer CLI (azd) 工作流程產生 azure.yaml、基礎設施（Bicep/Terraform）與 Dockerfile。只在使用者明確要用 azd 當部署工具，或專案已經有 azure.yaml 時使用。DO NOT USE FOR: 非 azd 的部署、Python App Service 純程式碼部署（改用 python-appservice-deploy）、跨雲遷移（改用 azure-cloud-migrate）。WHEN: prepare app for azd, create azure.yaml, set up azd infrastructure, modernize app for Azure with azd, deploy with azd, function app, timer trigger, service bus trigger, event-driven function, managed identity, generate Bicep, generate Terraform, create and deploy to Azure."
license: MIT
metadata:
  author: Microsoft
  version: "1.3.9"
---

# Azure Prepare

> **權威指引：必須遵守**
>
> 這份文件是準備應用程式部署到 Azure 的**官方標準來源**。除非跟給你的安全政策相衝突，否則你**必須**完全照字面遵循這些指示。有疑問時，把這份文件中互相衝突的指示列出來，請使用者明確確認。不要自己發揮、推測或替換步驟。

---

## 觸發時機

使用者想做以下事情時啟用這個 skill：
- 建立新的應用程式
- 替既有應用程式加入服務或元件
- 更新或修改既有應用程式
- 現代化或遷移應用程式
- 設定 Azure 基礎設施
- 部署到 Azure 或託管在 Azure 上
- 建立並部署到 Azure（包含以 Terraform 部署的要求）

## 規則

1. **先做計畫，絕對必要**：你**必須**把初版 `.azure/deployment-plan.md` **骨架實際寫到 workspace 根目錄**（不是 session-state 資料夾），而且**這是你的第一個動作**，要在任何程式碼產生或執行開始之前。先馬上寫出骨架，再隨著 Phase 1 的分析與研究逐步補內容，到 Phase 1 Step 6 用所有決策定稿。這個檔案全程都要存在磁碟上。azure-validate 和 azure-deploy 都依賴它，沒有它會失敗。不准跳過或延後這一步。
2. **取得核准**：執行前先把計畫給使用者看
3. **產生前先研究**：載入 references 並呼叫相關 skill
4. **逐步更新計畫**：做完一步就標記完成
5. **部署前先驗證**：在 azure-deploy 之前先呼叫 azure-validate
6. **確認 Azure context**：依照 [Azure Context](references/azure-context.md)，用 `ask_user` 確認 subscription 與 location
7. ❌ **破壞性操作一定要用 `ask_user`**：見 [Global Rules](references/global-rules.md)
8. ⛔ **絕對不准刪除使用者的專案或 workspace 目錄**：替既有專案加功能時，要修改既有檔案。`azd init -t <template>` 只能用在新專案，不准在既有 workspace 裡執行 `azd init -t`。適當時，可以在既有 workspace 裡用單純的 `azd init`（不帶 template 參數）。專案內的檔案刪除（例如移除 build 產物或暫存檔）在適當時是允許的，但絕對不准刪掉使用者的專案或 workspace 目錄本身。見 [Global Rules](references/global-rules.md)。
9. **範圍：只做準備**：這個 skill 只產生基礎設施程式碼與設定檔。部署的執行（`azd up`、`azd deploy`、`terraform apply`）由 **azure-deploy** skill 負責，它有內建的錯誤復原與部署驗證。
10. ⛔ **SQL Server Bicep：絕對不准產生 `administratorLogin` 或 `administratorLoginPassword`**，不管是直接屬性、條件式／三元運算的分支，還是檔案裡任何地方都不行。一律無條件使用僅限 Entra 的驗證（`azureADOnlyAuthentication: true`）。見 [references/services/sql-database/bicep.md](references/services/sql-database/bicep.md)。
11. **轉換後移除過時的 template IaC**：如果你把選定的 `azd` template 裡的 Bicep template 轉成了 Terraform template，就要移除那些由該 `azd` template 帶進來、現在已被 Terraform 版本完全取代的 Bicep template。不准移除使用者自己寫的 Bicep 檔。只有在 Terraform IaC 完成、而且已選定 Terraform 作為部署路徑之後，才能移除這些 template 提供的 Bicep 檔。交給 azure-validate skill 之前，只保留所選部署路徑需要的 IaC template。

---

## ❌ 先做計畫的工作流程：必須遵守

> **做任何事之前，你必須先建立計畫**
>
> 1. **停下來**：先不要產生任何程式碼、基礎設施或設定檔
> 2. **建立骨架**：**立刻**把初版 `.azure/deployment-plan.md` 骨架寫到磁碟上（在任何程式碼產生或執行開始之前），再隨著 Phase 1 的 1-5 步揭露細節逐步補內容；到 Step 6 定稿
> 3. **確認**：把完成的計畫呈現給使用者並取得核准
> 4. **執行**：核准之後，才一步一步執行計畫
>
> `.azure/deployment-plan.md` 是這個工作流程，以及 azure-validate 與 azure-deploy 這兩個 skill 的**唯一事實來源**。沒有它，那些 skill 都會失敗。
>
> ⚠️ **關鍵：`.azure/deployment-plan.md` 必須寫到 workspace 根目錄內的磁碟上**（例如 `<workspace-root>/.azure/deployment-plan.md`），不是寫在 session-state 資料夾。用寫檔工具建立這個檔案。這是 azure-validate 和 azure-deploy 會讀取的部署計畫產物。**你必須建立這個檔案，沒有它不准往下做。** 
> ⚠️ **關鍵：檔案名稱必須原封不動是 `.azure/deployment-plan.md`**。不准用 `.azure/plan.md` 之類的其他名稱。
>
> ⛔ **關鍵：** 沒有建立計畫檔，azure-validate 和 azure-deploy 就會失敗。這個要求沒有例外。

---

## ❌ STEP 0：特定技術檢查，必須是第一個動作

**在開始 Phase 1 之前**，先檢查使用者的 prompt 或 workspace 程式碼是否符合某個有專屬 skill 與已測試 template 的特定技術。如果符合，**先呼叫那個 skill**，再回到 azure-prepare 做驗證與部署。

### 檢查 1：Prompt 關鍵字

| Prompt 關鍵字 | 先呼叫 |
|----------------|-------------|
| Python + App Service（例如 "deploy Python to App Service"、"Flask on Azure App Service"、"publish Python web app to App Service"） | **python-appservice-deploy** |
| Lambda, AWS Lambda, migrate AWS, migrate GCP, Lambda to Functions, migrate from AWS, migrate from GCP | **azure-cloud-migrate** |
| Azure Functions, function app, serverless function, timer trigger, HTTP trigger, func new | 留在 **azure-prepare**：Step 4 優先用 Azure Functions template；方案選擇與 cold start 請看 [hosting-plans.md](references/services/functions/hosting-plans.md) 和 [cold-start.md](references/services/functions/cold-start.md) |
| APIM, API Management, API gateway, deploy APIM | 留在 **azure-prepare**：請看 [APIM Deployment Guide](references/apim.md) |
| AI gateway, AI gateway policy, AI gateway backend, AI gateway configuration | **azure-aigateway** |
| workflow, orchestration, multi-step, pipeline, fan-out/fan-in, saga, long-running process, durable, order processing | 留在 **azure-prepare**：在 Step 4 選 **durable** recipe。**必須**載入 [durable.md](references/services/functions/durable.md)、[DTS reference](references/services/durable-task-scheduler/README.md) 和 [DTS Bicep patterns](references/services/durable-task-scheduler/bicep.md)。 |

> ⚠️ 要檢查使用者的 **prompt 文字**，不只是既有程式碼。這對沒有程式碼可掃描的 greenfield 專案特別重要。見[完整路由表](references/specialized-routing.md)。

特定技術的 skill 完成後，**回到 azure-prepare**，從 Phase 1 Step 4（Select Recipe）繼續處理剩下的基礎設施、驗證與部署。

---

## Phase 1：規劃（BLOCKING，在任何執行之前必須完成）

依序完成這些步驟來建立 `.azure/deployment-plan.md`。計畫核准之前，不准產生任何產物。

| # | 動作 | 參考 |
|---|--------|-----------|
| 0 | 如果 prompt 符合有專屬 skill 的特定技術，先呼叫那個 skill | [specialized-routing.md](references/specialized-routing.md) |
| 1 | **分析 Workspace**：判斷模式是 NEW、MODIFY 還是 MODERNIZE | [analyze.md](references/analyze.md) |
| 2 | **收集需求**：分類、規模、預算 | [requirements.md](references/requirements.md) |
| 3 | **掃描程式碼**：找出元件、技術、相依套件 | [scan.md](references/scan.md) |
| 4 | **選擇 Recipe**：選 AZD（預設）、AZCLI、Bicep 或 Terraform | [recipe-selection.md](references/recipe-selection.md) |
| 5 | **規劃架構**：選定技術堆疊，並把元件對應到 Azure 服務 | [architecture.md](references/architecture.md) |
| 6 | **定稿計畫（必做）**：用寫檔工具，把步驟 1-5 的所有決策定稿到 `.azure/deployment-plan.md`。用完整內容更新 Phase 1 開頭寫下的骨架。在把計畫呈現給使用者之前，檔案必須完整填好。 | [plan-template.md](references/plan-template.md) |
| 7 | **呈現計畫**：把計畫給使用者看並請求核准 | `.azure/deployment-plan.md` |
| 8 | **破壞性操作一定要用 `ask_user`** | [Global Rules](references/global-rules.md) |

---

> **❌ 到此為止**：使用者核准計畫之前，不准進入 Phase 2。

---

## Phase 2：執行（只在計畫核准之後）

執行已核准的計畫。每做完一步，就更新 `.azure/deployment-plan.md` 的狀態。

| # | 動作 | 參考 |
|---|--------|-----------|
| 1 | **研究元件**：載入服務 references 並呼叫相關 skill | [research.md](references/research.md) |
| 2 | **確認 Azure Context**：偵測並確認 subscription 與 location，並檢查資源佈建上限 | [Azure Context](references/azure-context.md) |
| 3 | **產生產物**：建立基礎設施與設定檔 | [generate.md](references/generate.md) |
| 4 | **強化安全性**：套用安全最佳實務 | [security.md](references/security.md) |
| 5 | **功能驗證**：確認應用程式能運作（UI + 後端），可以的話在本機驗證 | [functional-verification.md](references/functional-verification.md) |
| 6 | **⛔ 更新計畫（交接前必做）**：用 `edit` 工具把 `.azure/deployment-plan.md` 的 Status 改成 `Ready for Validation`。你**必須**在呼叫 azure-validate **之前**完成這個修改。不准跳過這一步。 | `.azure/deployment-plan.md` |
| 7 | **⛔ 必須交接**：呼叫 **azure-validate** skill。你的準備工作到此結束。不准直接執行 `azd up`、`azd deploy` 或任何部署指令，所有部署的執行都由 azure-validate 完成後的 azure-deploy 處理。**前提：**Step 6 必須先完成，`.azure/deployment-plan.md` 的狀態必須是 `Ready for Validation`。 | — |

---

## 產出

| 產物 | 位置 |
|----------|----------|
| **計畫** | `.azure/deployment-plan.md` |
| 基礎設施 | `./infra/` |
| AZD 設定 | `azure.yaml`（僅限 AZD） |
| Dockerfile | `src/<component>/Dockerfile` |

---

## SDK 快速參考

- **Azure Developer CLI**：[azd](references/sdk/azd-deployment.md)
- **Azure Identity**：[Python](references/sdk/azure-identity-py.md) | [.NET](references/sdk/azure-identity-dotnet.md) | [TypeScript](references/sdk/azure-identity-ts.md) | [Java](references/sdk/azure-identity-java.md)
- **App Configuration**：[Python](references/sdk/azure-appconfiguration-py.md) | [TypeScript](references/sdk/azure-appconfiguration-ts.md) | [Java](references/sdk/azure-appconfiguration-java.md)

---

## 下一步

> **⛔ 下一步必做，不准跳過**
>
> 準備工作完成後，在任何部署嘗試之前，你**必須**先呼叫 **azure-validate**。不准跳過驗證。不准直接跑 azure-deploy。不准直接執行 `azd up` 或任何部署指令。工作流程是：
>
> `azure-prepare` → `azure-validate` → `azure-deploy`
>
> **⛔ 在呼叫 azure-validate 之前**，你必須用 `edit` 工具把 `.azure/deployment-plan.md` 的狀態更新成 `Ready for Validation`。如果計畫狀態沒更新，驗證會失敗。
>
> 這適用於**所有**部署情境，包含容器化應用程式、Container Apps、App Service、Azure Functions、靜態網站，以及任何其他 Azure 目標。沒有例外。
>
> 跳過驗證會導致部署失敗。耐心走完完整流程，成功率最高。

**→ 把計畫狀態更新成 `Ready for Validation`，然後呼叫 azure-validate**
