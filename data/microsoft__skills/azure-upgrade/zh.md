---
name: azure-upgrade
description: "評估並升級 Azure 工作負載的 plan、tier 或 SKU，或是把原始碼裡的 Azure SDK 相依套件現代化。WHEN: upgrade Consumption to Flex Consumption, upgrade Azure Functions plan, change hosting plan, function app SKU, migrate App Service to Container Apps, modernize legacy Azure Java SDKs (com.microsoft.azure to com.azure), migrate Azure Cache for Redis (ACR/ACRE) to Azure Managed Redis (AMR)."
license: MIT
compatibility: python3.10+
metadata:
  author: Microsoft
  version: "1.2.3"
---

# Azure Upgrade

> 這個 skill 負責**評估和自動化升級**既有的 Azure 工作負載，從一個 Azure 服務、hosting plan 或 SKU 換到另一個，全部都在 Azure 內進行。範圍包含 plan／tier 升級（例如 Consumption → Flex Consumption）、跨服務遷移（例如 App Service → Container Apps）和 SKU 變更。也涵蓋 **Azure SDK for Java 的原始碼現代化**（例如舊的 Java `com.microsoft.azure.*` → 新的 `com.azure.*`）。這個 skill 不處理跨雲遷移，那要用 `azure-cloud-migrate`。

## 觸發情境

| 使用者意圖 | 範例 Prompt |
|-------------|-----------------|
| 升級 Azure Functions plan | "Upgrade my function app from Consumption to Flex Consumption" |
| 找出 Functions 可升級的候選對象 | "What Consumption Function Apps do I have that can be upgraded to Flex Consumption?" |
| 變更 hosting tier | "Move my function app to a better plan" |
| 評估升級就緒度 | "Is my function app ready for Flex Consumption?" |
| 自動化 plan 遷移 | "Automate the steps to upgrade my Functions plan" |
| 把舊的 Azure Java SDK 現代化 | "Migrate legacy Azure SDKs for Java", "Upgrade legacy Azure Java SDK", "Migrate my Java project from com.microsoft.azure to com.azure" |
| 把 Azure Cache for Redis (ACR/OSS) 遷移到 Azure Managed Redis (AMR) | "Migrate my Redis cache to AMR", "ACR to AMR", "OSS to AMR", "Upgrade my Premium P2 cache to Managed Redis", "Pick an AMR SKU", "Convert my Redis IaC template to AMR" |
| 把 Azure Cache for Redis Enterprise (ACRE) 遷移到 Azure Managed Redis (AMR) | "Migrate my Enterprise_E10 cache to AMR", "ACRE to AMR", "Update my ACRE IaC template for AMR", "Migrate EnterpriseFlash to AMR", "Migrate my geo-replicated Enterprise Redis" |

## 規則

1. 依序執行各階段。只有在所選情境明確允許時才能跳過或延後工作，並把原因記錄在 migration status 裡
2. 在進行任何升級操作之前，先產出評估報告
3. 載入該情境的 reference，並遵守其中的規則
4. 使用 `mcp_azure_mcp_get_azure_bestpractices` 和 `mcp_azure_mcp_documentation` 這兩個 MCP 工具
5. 破壞性的操作需要 `ask_user`，見 [global-rules](references/global-rules.md)
6. 繼續之前，一定要先跟使用者確認目標 plan/SKU
7. **為任何新資源提議一個名稱**（預設：`<source>-<target-suffix>`，例如 Flex Consumption 遷移用 `<source>-flex`），並且**在建立之前先向使用者宣告提議的名稱**，讓他們不需要被卡在提問上就能改掉。其他新建的資源（storage account、App Insights 等）也用同樣的做法，各服務的預設值請看該情境的 reference。
8. **Windows Consumption → Flex 的來源變更關卡**：預設把來源 app 當成唯讀。在每個會改變它的設定、trigger、狀態、部署、binding 或存在與否的指令執行之前，立刻用 `ask_user` 描述確切的變更並取得明確同意。同意只對該次動作有效，不能拿來給之後的來源變更重複使用。
9. 沒有使用者明確確認，絕對不要刪除或停止原本的 app
10. **讓需要核准的工作流程持續推進**：每完成一個步驟，就立刻執行下一個唯讀的 preflight。如果下一個動作需要核准，就在同一個 turn 裡呼叫 `ask_user`，絕對不要只宣告下一步就停下來，等使用者再回來接手。
11. 所有自動化 script 都必須是 idempotent 而且可以續跑

## 升級情境

| 來源 | 目標 | Reference |
|--------|--------|-----------|
| Azure Functions Consumption Plan (Linux) | Azure Functions Flex Consumption Plan | [workflow.md](references/services/functions/consumption-to-flex/linux/workflow.md) |
| Azure Functions Consumption Plan (Windows) | Azure Functions Flex Consumption Plan | [workflow.md](references/services/functions/consumption-to-flex/windows/workflow.md) |
| 舊的 Azure Java SDK (`com.microsoft.azure.*`) | 新的 Azure Java SDK (`com.azure.*`) | [languages/java/README.md](references/languages/java/README.md) |
| Azure Cache for Redis (ACR/OSS) Basic/Standard/Premium | Azure Managed Redis (AMR) | [services/redis/redis-to-amr.md](references/services/redis/redis-to-amr.md) |
| Azure Cache for Redis Enterprise (ACRE) / Enterprise Flash | Azure Managed Redis (AMR) | [services/redis/redis-to-amr.md](references/services/redis/redis-to-amr.md) |

> **Functions Consumption-to-Flex 的路由：** 如果指定了某個 app，先檢查它的 Azure 平台，只載入對應的 Linux 或 Windows workflow。如果是整個 subscription 的探索，兩個平台都要評估：Linux 用 `az functionapp flex-migration list`，Windows 用 Windows workflow 裡的手動探索和相容性檢查。在針對每個 app 評估過程式碼相容性之前，Windows 的結果都要標示成候選。

> SDK 升級情境（例如 Java 舊版 → 新版）走的是**原始碼現代化流程**，跟 Azure 服務／plan／SKU 升級不一樣：要照該情境的 reference 做，**不要**照下面的步驟。

> 沒有符合的情境？用 `mcp_azure_mcp_documentation` 和 `mcp_azure_mcp_get_azure_bestpractices` 這兩個工具去研究升級路徑。

## MCP 工具

| 工具 | 用途 |
|------|---------|
| `mcp_azure_mcp_get_azure_bestpractices` | 取得目標服務的 Azure 最佳實務 |
| `mcp_azure_mcp_documentation` | 查詢升級情境的 Azure 文件 |
| `mcp_azure_mcp_appservice` | 查詢 App Service 和 Functions plan 的細節 |
| `mcp_azure_mcp_applicationinsights` | 驗證監控設定 |

## 步驟

1. **Identify**：確定來源和目標的 Azure plan/SKU，請使用者確認。
2. **Assess**：分析既有 app 的升級就緒度 → 載入該情境的 reference（例如 [workflow.md](references/services/functions/consumption-to-flex/linux/workflow.md)）
3. **Pre-migrate**：從既有的 app 收集設定、身分和 config
4. **Upgrade**：執行自動化的升級步驟（建立新資源、遷移設定、部署程式碼）
5. **Validate**：使用所選情境定義的檢查，包含驗證目標資源的狀態、適用的 HTTP endpoint 和非 HTTP trigger，以及監控。如果因為存取限制或沒有測試資源而無法執行，就把驗證記錄為延後，絕對不要自動放寬安全設定，也不要回報功能成功。
6. **Ask User**：提供效能驗證和 IaC 更新的選項。只有在所選情境確認 production cutover 且所有清理前置條件都完成時，才提供清除來源的選項。
7. **Hand off**：交給 `azure-validate` 做深入驗證，或交給 `azure-deploy` 設定 CI/CD

進度記錄在 `<UPGRADE_DIR>/upgrade-status.md`，路徑解析方式請看 [Artifact Output Policy](references/global-rules.md#artifact-output-policy)。

## 參考資料

- [Global Rules](references/global-rules.md)
- [Workflow Details](references/workflow-details.md)
- **Functions**
  - Linux
    - [Consumption to Flex Consumption](references/services/functions/consumption-to-flex/linux/workflow.md)
    - [Assessment](references/services/functions/consumption-to-flex/linux/assessment.md)
    - [Automation Scripts](references/services/functions/consumption-to-flex/linux/automation.md)
  - Windows
    - [Consumption to Flex Consumption](references/services/functions/consumption-to-flex/windows/workflow.md)
    - [Assessment](references/services/functions/consumption-to-flex/windows/assessment.md)
    - [Automation Scripts](references/services/functions/consumption-to-flex/windows/automation.md)
- **Redis**
  - [Redis (ACR or ACRE) to AMR Migration](references/services/redis/redis-to-amr.md)，會轉到專用的 [amr-migration-skill](https://github.com/AzureManagedRedis/amr-migration-skill)（ACR/OSS）或 [acre-to-amr-migration-skill](https://github.com/AzureManagedRedis/acre-to-amr-migration-skill)（Enterprise）
- **Java SDK 遷移範本**
  - [Plan Template](references/languages/java/templates/PLAN_TEMPLATE.md)
  - [Progress Template](references/languages/java/templates/PROGRESS_TEMPLATE.md)
  - [Summary Template](references/languages/java/templates/SUMMARY_TEMPLATE.md)

## 下一步

升級驗證完成後，交給：
- `azure-validate`：做完整的升級後驗證
- `azure-deploy`：如果使用者想為新 app 設定 CI/CD
