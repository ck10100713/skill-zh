---
name: azure-reliability
description: "評估並改善 PaaS 應用程式（Azure Functions 與 Azure App Service）的可靠性狀態。掃描已部署的資源，檢查 zone redundancy、ZRS 儲存、health probe 與多 region failover。先呈現以功能為軸的檢查清單，再經使用者確認，分階段端到端執行修復（CLI 或 IaC patch）。WHEN: \"assess reliability\", \"check reliability\", \"zone redundant\", \"multi-region failover\", \"high availability\", \"disaster recovery\", \"single points of failure\", \"reliability posture\", \"resiliency\"."
license: MIT
metadata:
  author: Microsoft
  version: "1.1.2"
---

# Azure 可靠性評估與設定

## 快速參考

| 屬性 | 細節 |
|---|---|
| 最適合 | 可靠性狀態評估、啟用 zone redundancy、設定多 region failover |
| 主要能力 | 可靠性評估表、Zone Redundancy 設定、多 region IaC 產生 |
| 支援的服務 | Azure Functions、App Service（Container Apps 預計在未來版本支援） |
| MCP 工具 | Azure Resource Graph 查詢、Azure CLI 指令 |

## 何時使用這個 Skill

使用者想做以下事情時啟用這個 skill：
- 「評估我的 Function app 的可靠性」
- 「評估我的 Web app 的可靠性」
- 「檢查我的 resource group 的可靠性」（僅限 App Service 與 Functions 資源）
- 「我的 app 有 zone redundant 嗎？」（僅限 App Service 與 Functions 資源）
- 「我的 app service plan 有 zone redundant 嗎？」 
- 「讓我的 app 具備 zone redundant」（僅限 App Service 與 Functions 資源）
- 「讓我的 app service plan 具備 zone redundant」
- 「替我的 app 設定多 region failover」（僅限 App Service 與 Functions 資源）
- 「檢查我的可靠性狀態」
- 「找出 single point of failure」（僅限 App Service 與 Functions 資源）
- 「替我的 app 啟用高可用性」（僅限 App Service 與 Functions 資源）
- 「檢查災難復原的準備程度」
- 「提升我的 app 的韌性」（僅限 App Service 與 Functions 資源）

> **範圍說明：**這個 skill 目前只涵蓋 **Azure Functions 與 Azure App Service**。如果使用者問 Azure Container Apps 的可靠性，要告知這部分已規劃但還沒提供，並且只處理範圍內屬於 App Service 與 Functions 資源的部分。

## 前置條件

- 驗證：使用者已透過 `az login` 登入 Azure
- 權限：目標 subscription/resource group 的 Reader 權限（用於評估）
- 權限：Contributor 權限（用於變更設定）
- Azure Resource Graph extension：`az extension add --name resource-graph`

## MCP 工具

| 工具 | 用途 |
|------|---------|
| `mcp_azure_mcp_extension_cli_generate` | 產生用於資源查詢與設定的 `az` CLI 指令 |
| `mcp_azure_mcp_subscription_list` | 列出可用的 subscription |
| `mcp_azure_mcp_group_list` | 列出 resource group |

主要的查詢方式：透過 `az graph query` 使用 Azure Resource Graph（需要 `az extension add --name resource-graph`）。

## 評估流程

### Phase 1：探索資源

1. **確認範圍**：問使用者 resource group、subscription 或 app 名稱
2. **查詢 Azure Resource Graph**，探索範圍內的所有資源
3. **依服務類型分類資源**（Functions、Storage 等）。如果發現 Container Apps，**記下來但不要深入處理**。

**重要：**查詢一律要限縮在使用者指定的 resource group 或 subscription。每個 Resource Graph 查詢都要加上這些過濾條件：
- Resource group：`| where resourceGroup =~ '<rg-name>'`
- Subscription：在 `az graph query` 上用 `--subscriptions <sub-id>` 旗標
- App 名稱：`| where name =~ '<app-name>'`

### Phase 2：評估可靠性

兩步驟評估：**先做平台層級探索，再逐個服務深入檢查。**

**Step 1：平台探索（找出有什麼）。**用這些來列舉範圍內的資源，並偵測跨服務的可靠性缺口：

| 平台檢查 | 參考 |
|---|---|
| Zone redundancy：探索 | [references/zone-redundancy-checks.md](references/zone-redundancy-checks.md) |
| 儲存 redundancy（跨服務） | [references/storage-redundancy-checks.md](references/storage-redundancy-checks.md) |
| 多 region 與全域 load balancer | [references/multi-region-checks.md](references/multi-region-checks.md) |
| Front Door / Traffic Manager / App Insights probe | [references/health-probe-checks.md](references/health-probe-checks.md) |

**Step 2：逐個服務深入檢查。**對 Step 1 找到的每個運算資源，載入對應的服務參考文件。服務參考文件是該服務 plan/SKU 規則、評估查詢、CLI 指令、IaC patch（Bicep + Terraform + AVM）與報告提示的唯一事實來源。

這個版本的 skill **只內建 Azure Functions 與 App Service** 的逐服務參考文件。其他運算服務在下面明確列出，讓分派邏輯不會有歧義：如果資源符合不支援的那幾列，**不准**嘗試載入參考文件、編造 CLI 指令，或替它產生 IaC patch。

| 偵測到的服務 | 參考 |
|---|---|
| Azure Functions（`microsoft.web/serverfarms` 且 `kind contains 'functionapp'`） | [references/services/functions/reliability.md](references/services/functions/reliability.md) |
| Azure App Service（非 Functions 的 site：`microsoft.web/sites` 且沒有 `kind contains 'functionapp'`、`microsoft.web/serverfarms` 且沒有 `kind contains 'functionapp'`） | [references/services/app-service/reliability.md](references/services/app-service/reliability.md) |
| Azure Container Apps（`microsoft.app/containerapps`、`microsoft.app/managedenvironments`） | ⚪ 尚未提供，預計在未來版本支援 |

> **處理不支援的服務：**如果資源符合上面不支援的那幾列，要在探索摘要中列出來，在 Phase 3 的表格標成 `⚪ not assessed (planned)`，並跳過它的逐服務修復步驟。**不准**嘗試替那些服務編造 CLI 指令或 IaC patch。

### Phase 3：產生可靠性檢查清單

用**以功能為軸**的表格呈現結果：每個可靠性功能一列（運算的 zone redundancy、zone-redundant 儲存、health probe、多 region failover），附上單一狀態指示，以及與該功能相關的**具體資源**。這樣可以避免一個資源一列、多數格子都是 `n/a` 的雜訊。**不准**給數字分數或等級。

```
🔍 可靠性評估 — {scope}
─────────────────────────────────────────────────────────────────────────────────────────────
可靠性功能                         狀態        資源
─────────────────────────────────────────────────────────────────────────────────────────────
運算的 zone redundancy             🔴 OFF      • plan-web-ii5trxva2ark4 (P1v3)
                                              • plan-ii5trxva2ark4 (FC1)

Zone-redundant 儲存                🔴 GRS      • stii5trxva2ark4（預設值；IaC 中沒設定 SKU）

Health probe                      🔴 OFF      • func-api-ii5trxva2ark4 — 需要修改程式碼 (FC1)
                                              • app-web-ii5trxva2ark4 — 沒有 health check path

多 region failover                 🔴 OFF      • 只有單一 region (eastus)，沒有設定 Front Door
─────────────────────────────────────────────────────────────────────────────────────────────

要我修復那些 🔴 項目嗎？我會先做快速見效的部分（App
plan 的 zone redundancy，以及支援的 plan 上的 health check），再詢問要不要做
儲存遷移與多 region 設定。(yes/no)
```

**表格規則：**

- **四個功能列，依這個順序：**運算的 zone redundancy · Zone-redundant 儲存 · Health probe · 多 region failover。只有當範圍內沒有任何資源可能適用某一列時，才能整列省略。
- **狀態欄**是一個符號加一個簡短單字，不要有其他字元：
  - `🟢 ON`：範圍內所有相關資源都已完整啟用該功能
  - `🟡 PARTIAL`：有些資源有、有些沒有（或只有部分設定，例如只有 liveness）
  - `🔴 OFF`：所有相關資源都沒有該功能
  - 儲存的話，相關時把 `OFF` 換成目前的 SKU（`🔴 LRS`、`🔴 GRS`、`🟢 ZRS`、`🟢 GZRS`）。如果 IaC 沒設定 SKU，標成 `🔴 GRS`（ARM/AVM 預設值），並在資源那行註明。
- **資源欄**只列出與該功能相關的東西，每個資源一個項目：
  - 「需要修復」的資源，附上簡短的行內原因（`(FC1)`、`(defaulted; no SKU set)`、`liveness only`、`needs code change (FC1)`）。
  - 該功能**已經是 ON** 的資源，也在同一列用 `— already ON` 提到，讓使用者看到做對的部分。
- **不准**放 `n/a`、`—` 或空白的格子。如果某個功能不適用於範圍內任何資源，就把那一列拿掉。
- **不准**放數字分數、等級或總分。
- 評估結尾要有**一個是非題**，用來啟動分階段修復流程。不要在這裡列出每個資源的修復清單，使用者說 yes 之後才會看到（Configuration Workflow Step 1）。

> **UX 說明：**如果評估發現 app **已經具備**所有核心可靠性功能（zone redundancy、ZRS/GZRS 儲存、health probe），就跳過修復的問題，直接進入 Configuration Workflow 的 [Step 3](#step-3-both-paths-multi-region-followup--ask-and-wait)（多 region 後續）。沒有使用者明確同意，**不准**開始任何多 region 的工作。

## 設定流程

當使用者想**修復**評估發現的問題時：

> **⛔ 執行變更前，一定要先跟使用者確認。**要列出會變更什麼、任何成本影響，以及任何破壞性操作（例如重建環境）。

### Step 1：呈現修復計畫並選擇路徑

評估之後，如果使用者說「fix it」/「improve my reliability」/「enable zone redundancy」：

1. 列出每個可修復的發現，以及具體動作
2. 標出任何成本影響或 breaking change
3. **問使用者要走哪條路徑：**

```
我會先做快速見效的部分（沒有 downtime，很快）：

1. ✏️  在 plan-ii5trxva2ark4 啟用 zone redundancy（Flex Consumption，成本不變）
2. ✏️  把 func-api-ii5trxva2ark4 的 health check path 設為 /api/health

接著，我會另外問你要不要升級儲存：

3. 🕒  把 stii5trxva2ark4 從 LRS 升級到 ZRS（成本小幅增加，遷移要好幾個小時）
   — 這是完整 zone redundancy 所必需的，但開始前我會先跟你確認。

你想用哪種方式套用這些變更？

  A) 立即修復：對你的線上資源執行 az CLI 指令（立即生效、一次性）
  B) 修改我的 IaC：更新你的 Bicep/Terraform 檔案，讓變更在每次部署後都保留

（如果你用 azd 或 Terraform，建議選 B，這樣 `azd up` 才不會覆蓋變更。）
```

### Path A：立即修復（CLI）

用 `az` CLI 指令對線上資源執行修復。**先做快速見效的，再詢問是否進行耗時的儲存遷移。**

各服務的實際 CLI 指令放在逐服務參考文件裡，請挑出與 Phase 2 探索到的資源相符的那幾份：

| 修復 | 參考 |
|---|---|
| 啟用 zone redundancy / 設定 health probe（Functions） | [references/services/functions/reliability.md](references/services/functions/reliability.md) |
| 啟用 zone redundancy / 設定 health probe（App Service） | [references/services/app-service/reliability.md](references/services/app-service/reliability.md) |
| 升級儲存複寫（跨服務） | [references/configure-storage.md](references/configure-storage.md) |
| 設定多 region（跨服務） | [references/configure-multi-region.md](references/configure-multi-region.md) |
| 平台概覽 / 驗證 | [references/configure-zone-redundancy.md](references/configure-zone-redundancy.md)、[references/configure-health-probes.md](references/configure-health-probes.md) |

**執行順序：一律先做快速見效的：**

1. **運算的 zone redundancy**（快，直接就地更新 App plan 的屬性）。
2. **Health probe**（僅限 Premium / Dedicated，就地更新；FC1 / Consumption 則依照 [configure-health-probes.md](references/configure-health-probes.md) 的同意關卡處理）。
3. **驗證**運算的變更成功之後，再做其他事。
4. **⛔ 停下來：詢問是否升級儲存。**運算現在已經 zone-redundant，但儲存可能還是 LRS 或 GRS。要明確問使用者：

   ```
   ✅ 運算現在已經是 zone-redundant。

   要達到**完整的 zone redundancy**，你的儲存帳號也需要升級：
     • stii5trxva2ark4：目前是 `Standard_LRS` → 需要 `Standard_ZRS`

   ⚠️  這是線上儲存 redundancy 的轉換：
      • 依資料量而定，需要數小時到數天
      • 持續成本小幅增加（每月約多 $0.01/GB）
      • 只支援 Standard general-purpose v2 帳號

   要我現在開始儲存遷移嗎？(yes / no / later)
   ```

    - **yes** → 執行 `az storage account update --sku Standard_ZRS`（必要時用 `migration start`）；輪詢 `az storage account show --query sku.name`，直到回報 `Standard_ZRS`。
    - **no / later** → 儲存維持現狀；在重新評估中註明 ZR 儲存仍是缺口。

5. **多 region**：不要自動執行。在重新評估之後，於下面的 **Step 3** 作為明確的後續步驟處理。

> **⚠️ 警告：**如果使用者之後用 `azd up` 或 `terraform apply`，只用 CLI 做的變更可能會被 IaC 的定義覆蓋。建議在 CLI 修復之後，同時也 patch IaC。

### Path B：Patch IaC

更新使用者的 Bicep 或 Terraform 檔案，讓可靠性設定能持續保留。

**Step 1：偵測 IaC 類型**
1. 在專案根目錄找 `infra/` 資料夾
2. 找不到的話，在專案根目錄找 `*.bicep` 或 `*.tf` 檔案
3. 還是找不到，就問使用者：「你的 IaC 檔案放在哪裡？」
4. 有 `*.bicep` 檔案 → 用 Bicep patch
5. 有 `*.tf` 檔案 → 用 Terraform patch
6. 兩種都有的話，問使用者要 patch 哪一種
7. 完全沒有 IaC，就退回 Path A（CLI）並告知使用者

**Step 2：依風險等級分類每個修復**

| 修復 | 風險等級 | 會發生什麼 |
|-----|-----------|--------------|
| Zone redundancy（App plan） | 🟢 安全的 patch | 下次部署時就地更新屬性 |
| 儲存 LRS → ZRS | 🟡 需要先遷移 | 必須先完成線上儲存遷移，才能部署 IaC 的 SKU 變更。**絕對不要跟安全的 patch 綁在一起**，要用 Step 3–5 的兩次部署流程。 |
| Health check path（Basic/Standard/Premium / Dedicated） | 🟢 安全的 patch | 就地更新，但會造成 app 重啟 |
| Health check path（FC1 / Consumption） | ⚪ 僅限程式碼：先問 | 不支援 `healthCheckPath`。要加 health endpoint，需要在 **app 程式碼**裡加一個 HTTP 觸發的 `/api/health` function。**碰原始碼之前，一定要先取得使用者的明確同意。** **不准** patch IaC。 |

**Step 3：分兩次部署套用 patch（先做快速見效的）**

IaC patch 框架（偵測、AVM 模組指引、部署順序規則、儲存 SKU patch）放在：

| IaC 類型 | 框架參考 |
|---|---|
| Bicep | [references/iac-patching-bicep.md](references/iac-patching-bicep.md) |
| Terraform | [references/iac-patching-terraform.md](references/iac-patching-terraform.md) |

實際的**逐服務運算 patch**（Function App plan 的 ZR、App Service Plan 的 ZR 等）放在逐服務參考文件裡，請載入 Phase 2 對應的服務檔案，取得確切的 Bicep / Terraform / AVM 程式碼片段。這個版本的 skill 只有 Azure Functions 與 App Service 有逐服務參考文件，Container Apps 不在範圍內。

**Deploy 1：只做快速見效的部分。**patch 🟢 安全的項目（App Service/Function App plan 的 zone redundancy、Basic/Standard/Premium / Dedicated 上的 health probe）。這次部署**不要**包含儲存 SKU 的 patch。

patch 完之後，**由這個 skill 自己執行部署**（不要停下來叫使用者自己跑）。先偵測部署工具，並在執行前確認一次：

```
📦 已替你的 IaC 套用 patch。準備部署：
   偵測到的工具：azd（找到 azure.yaml）
   指令：         azd up

要進行部署嗎？(yes / no)
```

選 **yes** 就執行對應的指令，把輸出串流給使用者，成功後繼續下一步：
- AZD 專案（有 `azure.yaml`）：`azd up`
- 只有 Bicep：`az deployment group create --resource-group <rg> --template-file infra/main.bicep --parameters @infra/main.parameters.json`
- Terraform：`terraform plan -out tfplan` → （顯示計畫摘要）→ `terraform apply tfplan`

選 **no** 就停下來並回報已 patch 的檔案；不要繼續到 Step 4 / Re-Assess。

如果部署失敗，要把錯誤呈現出來並停止，不要繼續到儲存那一步。

**⛔ 停下來：在 Deploy 2 之前，先詢問是否升級儲存。**Deploy 1 成功後，要明確問使用者：

```
✅ 快速見效的 patch 已部署。運算現在已經是 zone-redundant。

要達到**完整的 zone redundancy**，你的儲存帳號也需要升級：
  • stii5trxva2ark4：目前是 `Standard_LRS` → 需要 `Standard_ZRS`

⚠️  這是分兩部分的變更：
   1. 線上儲存遷移（`az storage account migration start`），需要數小時到數天
   2. 第二次部署，把你 IaC 裡的儲存 SKU 更新成一致

要我現在開始儲存遷移嗎？(yes / no / later)
```

- **yes** → 由這個 skill 自己執行遷移指令、輪詢到完成，接著 patch IaC 裡的儲存 SKU 並執行 **Deploy 2**（此時只是 no-op 確認）。使用者不需要手動執行任何東西。
- **no / later** → 不套用儲存 SKU 的 patch。在重新評估中註明 ZR 儲存仍是缺口，並建議之後再回頭處理。

**Step 4：儲存遷移（只有在使用者於 Step 3 回答 yes 時）**

這個 skill 自己執行這些指令，不要叫使用者去跑。過程中要顯示進度：

```
🔄 開始儲存遷移（最多可能需要 72 小時）...

   az storage account migration start --name stii5trxva2ark4 \
     --resource-group rg-example --sku Standard_ZRS --no-wait

   輪詢中：az storage account show --name stii5trxva2ark4 --query sku.name
   ...
   ✅ 遷移完成：sku.name = Standard_ZRS
```

資料遷移很久的話，可以向使用者提供一個檢查點（「這個還在跑，晚點再回來看」），而不是讓整段對話一直卡著。

**Step 5：Deploy 2：儲存 SKU patch**

遷移完成後，這個 skill 會 patch IaC 裡的儲存 SKU，並執行跟 Step 3 一樣的部署指令（例如 `azd up`）。這次部署是 no-op 確認，確認 IaC 與線上狀態一致。執行前跟使用者確認一次，然後直接執行。

### Step 2（兩條路徑都要）：重新評估

變更套用（CLI）或部署（IaC）完成後，自動重新執行評估，並顯示跟 Phase 3 **一樣的以功能為軸的表格**，每個功能列的狀態更新成新狀態。簡短點出跟上次相比有什麼變化。

```
🔄 可靠性重新評估 — rg-eventhubs-python-jan13 (eastus)
───────────────────────────────────────────────────────────────────────────────────────
可靠性功能                         狀態        資源
───────────────────────────────────────────────────────────────────────────────────────
運算的 zone redundancy             🟢 ON       • plan-ii5trxva2ark4 (FC1)              — 現在是 ON
                                              • plan-web-ii5trxva2ark4 (P1v3)         — 現在是 ON

Zone-redundant 儲存                🟢 ZRS      • stii5trxva2ark4                       — GRS → ZRS

Health probe                      🟡 PARTIAL  • func-api-ii5trxva2ark4                — 仍然是 off（FC1，拒絕修改程式碼）
                                              • app-web-ii5trxva2ark4                 — 現在是 ON

多 region failover                 🔴 OFF      • 只有單一 region (eastus)
───────────────────────────────────────────────────────────────────────────────────────

變更內容：Function App 與 App Service plan 的 zone redundancy、儲存複寫，以及 App Service 的 health probe。
（接下來會提供多 region，見 Step 3。）
```

### Step 3（兩條路徑都要）：多 region 後續：詢問並等待

多 region 是成本與複雜度都很高的一步。**不要**自動開始。重新評估之後，只有在**所有核心單一 region 可靠性功能都是 🟢 ON**（zone-redundant 運算、ZRS/GZRS 儲存、health probe）時，才明確詢問使用者，並在做任何事之前**等他回應**：

```
🟢 你的 app 現在在 {region} 已經完全 zone-redundant。

下一步（選用）是用 Azure Front Door 做多 region failover：
   • 在第二個 region 部署運算與儲存（建議用 paired region）
   • 加入 Azure Front Door 做全域 load balancing，並由 health probe 驅動 failover
   • 防範整個 region 中斷
   • 預估額外成本：運算約 2 倍（active-passive）；Front Door 基本費約 $35/月

要我現在設定多 region failover 嗎？(yes / no / later)
```

- **yes** → 繼續 [references/configure-multi-region.md](references/configure-multi-region.md)。跟使用者確認第二個 region 的選擇，然後：
  1. 產生多 region IaC（第二個 region 的 Bicep / Terraform 新增內容，加上 Front Door）。
  2. 跟使用者確認一次：`📦 Multi-region IaC generated. Ready to deploy with \`azd up\`. Proceed? (yes / no)`
  3. 選 **yes** 就由 **skill 自己執行部署**（`azd up` / `az deployment group create` / `terraform apply`）並串流輸出。不要停下來叫使用者自己跑。
  4. 部署成功後，執行最後一次重新評估，讓使用者看到多 region failover 變成 🟢 ON。
- **no / later** → 維持目前的部署狀態。註明單一 region 的 zone-redundant 本身就是可靠的終點狀態；多 region 隨時可以再回頭考慮。

> **⛔ 不准跳過等待。**使用者明確說 yes 之前，不准產生多 region IaC、部署 Front Door 或修改任何檔案。如果核心可靠性還沒全部是 🟢，**不要**問多 region，先把核心缺口補完。

## 優先級分類

| 優先級 | 條件 | 動作 |
|---|---|---|
| Critical | 沒有 zone redundancy 且是正式環境的工作負載 | 立即修復 |
| High | zone-redundant 運算上用 LRS 儲存 | 數天內修復 |
| Medium | 沒有多 region（單一 region 但有 zone redundancy） | 排入下個 sprint |
| Low | 缺少 health probe 或監控有缺口 | 追蹤並修復 |

## 錯誤處理

| 錯誤 | 訊息 | 修復方式 |
|---|---|---|
| 需要驗證 | "Please login" | 執行 `az login` 後重試 |
| 存取被拒 | "Forbidden" | 確認 Reader/Contributor 角色指派 |
| Plan 不支援 ZR | "Upgrade required" | 告知使用者 plan 的升級路徑與成本差異 |
| Region 不支援 AZ | "Region limitation" | 建議支援的 region |

## 最佳實務

- 每次重大基礎設施變更之後，都要執行可靠性評估
- 定期測試 failover 情境（至少每季一次）

## Skill 邊界

| 動作 | 這個 skill 會做 | 交給 |
|---|---|---|
| 評估可靠性狀態 | ✅ 會 | — |
| 建議改善項目 | ✅ 會 | — |
| 啟用 zone redundancy（CLI 指令） | ✅ 會 | — |
| Patch Bicep/Terraform 以提升可靠性 | ✅ 會 | — |
| 產生多 region IaC | ✅ 會（第二個 region 的新增內容 + Front Door） | 完整的新 app IaC scaffolding 交給 `azure-prepare` |
| 為可靠性變更部署 IaC | ✅ 會（確認後由它自己執行 `azd up` / `terraform apply` / `az deployment`） | 一般／非可靠性的部署交給 `azure-deploy` |
| 部署前驗證 | 只做可靠性檢查 | 完整驗證交給 `azure-validate` |
