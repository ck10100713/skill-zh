# Prepare：架構規劃與成本估算

## 快速參考

| 屬性 | 值 |
|----------|-------|
| 最適合 | 把應用程式元件對應到 Azure 服務，並做成本估算與配額驗證 |
| 輸入 | `.copilot-azure/sessions/{id}/` 底下的 `prereq-output.json` + `context.json` |
| 輸出 | 寫到 session 目錄的 `prepare-plan.json` |
| 上層 | [azure-app-onboard](../SKILL.md) |

## 什麼時候用這個 Skill

由 `azure-app-onboard` orchestrator 在 Phase 2 呼叫，前提是 `prereq-output.json` 已存在。使用者不能直接呼叫。

> **回到 orchestrator：** 完成後，把控制權交回 `azure-app-onboard`。絕對不要直接呼叫 scaffold 或 deploy。

## 什麼時候不要用

| 情境 | 改用 |
|----------|-------------|
| 程式碼就緒度或 prereq 掃描 | `azure-app-onboard` 步驟 3（prereq） |
| 從已完成的計畫產生 IaC | `azure-app-onboard` 步驟 7（scaffold） |
| 把資源 deploy 到 Azure | `azure-app-onboard` 步驟 9（deploy） |
| 最佳化現有的 Azure 花費 | 選用的 `azure-cost` plugin 裡的 `cost-optimization` |
| 估算 VM 專屬的成本 | `azure-compute` |
| 企業級 landing zone 架構 | `azure-enterprise-infra-planner` |

如果 `cost-optimization` 無法使用，就說明它是由選用的 `azure-cost` plugin 提供，並引導使用者走他們 client 支援的 plugin 安裝流程；不要暗示交接已經完成。

## MCP 工具

| 工具 | 用途 |
|------|----------|
| `mcp_azure_mcp_pricing` / `azure-pricing`（router → `command: pricing_get`） | 成本估算（inline，見步驟 6）。備案：派出 [`subagent-pricing.md`](references/subagent-pricing.md) |
| `mcp_azure_mcp_policy` | 訂閱的 policy 限制 |
| `az rest` | 配額驗證（透過 sub-agent，見步驟 5） |
| `mcp_azure_mcp_cloudarchitect` → `cloudarchitect_design` | 符合 WAF 的架構設計 |
| `mcp_azure_mcp_wellarchitectedframework` | 各服務的 WAF 指引 |
| `mcp_azure_mcp_advisor` → `advisor_recommendation_list` | 最佳化建議 |

## 流程

| # | 步驟 | 動作 | 參考 |
|---|------|--------|-----------|
| 1 | **讀取 session 狀態** | 載入 `prereq-output.json` + `context.json`。解析 subscription | 需要時交叉參考 [subscription-resolution.md](../references/subscription-resolution.md) |
| 2 | **查詢 policy 限制** | Inline MCP：取得 policy + advisor 建議 | `mcp_azure_mcp_policy` + `mcp_azure_mcp_advisor` |
| 3 | **把元件對應到服務** | 逐一元件選擇 Azure 服務、Dockerfile 路由、原樣 deploy | ⛔ **你一定要讀 [service-mapping.md](references/service-mapping.md) 和 [deploy-strategy.md](references/deploy-strategy.md)** |
| 4 | **選擇 SKU + WAF 分析** | 考慮預算的 SKU 選擇、inline 的 WAF 服務指引 | ⛔ **你一定要讀 [sku-matrix.md](references/sku-matrix.md)** |
| 5 | **驗證配額 + region 容量** | ⛔ 讀 [`subagent-quota.md`](references/subagent-quota.md) → 以 `task` 派出（下一個動作一定要是 `task`，⛔ agent_type：`"task"`，絕對不要用 `"general-purpose"`）。把**完整且未經修改**的範本文字，放在 `<<<TEMPLATE_START>>>` / `<<<TEMPLATE_END>>>` 分隔符號之間複製進 task prompt，不准摘要。把 [`subagent-quota.md`](references/subagent-quota.md) 輸入表格列出的呼叫端輸入，附加在範本區塊**之後**。⛔ **派出之後，趁 subagent 執行時繼續做步驟 6（成本估算）。不要自己跑配額檢查，subagent 會處理。在步驟 9（寫入計畫）之前，要先收回 subagent 的結果。** | ⛔ **你一定要讀 [`subagent-quota.md`](references/subagent-quota.md)** |
| 6 | **估算成本** | ⛔ **你一定要先讀 [pricing-guide.md](references/pricing-guide.md)** 了解方法，再讀 [pricing-guide-services.md](references/pricing-guide-services.md) 看各服務的篩選條件。對每個付費服務，用 `command: "pricing_get"` + inline 的 `parameters{}` 物件呼叫 pricing router（`mcp_azure_mcp_pricing`/`azure-pricing`）。如果 MCP 無法使用或失敗 → ⛔ 讀 [`subagent-pricing.md`](references/subagent-pricing.md) → 以 `task` 派出（下一個動作一定要是 `task`，⛔ agent_type：`"task"`，絕對不要用 `"general-purpose"`）。把**完整且未經修改**的範本文字，放在 `<<<TEMPLATE_START>>>` / `<<<TEMPLATE_END>>>` 分隔符號之間複製進 task prompt，不准摘要。把資料（services[]、region、預算等級）附加在範本區塊**之後**。把結果寫到 `prepare-plan.json.costEstimate`。 | [pricing-guide.md](references/pricing-guide.md) |
| 7 | **產生命名** | 集中式命名：suffix、prefix、所有資源名稱 | ⛔ **你一定要讀 [naming-patterns.md](references/naming-patterns.md)** |
| 8 | **決定 IaC 格式** | 已有非 Azure 的 `.tf` → 用 `ask_user` 問 Bicep 還是 TF，寫到 `overrides[].iacFormat`。沒有 `.tf` → 預設 Bicep。 | （inline） |
| 9 | **寫入 prepare-plan.json** | 依 `PreparePlan` schema。包含 postDeployRecommendations、deploymentVariables | ⛔ **你一定要讀 [prepare-schemas.ts](references/prepare-schemas.ts)** 了解 `PreparePlan` schema |
| 10 | **回傳摘要** | 為 orchestrator 的核准關卡提供結構化摘要 | （inline，1 行） |
| 11 | **驗證計畫** | 四個面向的檢查：目標一致性、WAF 一致性、相依性完整度、部署可行性。失敗就 inline 修正，並把取捨記錄在 `assumptions[]`。 | 全部通過才能寫入 |

### 步驟 5：配額驗證之後

> ⛔ **沒檢查配額之前，絕對不要提出任何 region。** 跳過配額驗證會造成連鎖的 deploy 失敗和冗長的修復迴圈。
> ⛔ 如果計畫包含 PostgreSQL/MySQL，要確認 `offerRestrictionsVerified: true`，如果是 false 或缺少，代表該 region 被擋住。不要帶著沒檢查過的 DB 服務進入 scaffold。
> ⛔ **免費不等於無限。** 每個運算 SKU（包括 F1、Consumption 和 Serverless 層級）都有每個 subscription、每個 region 的配額。不要因為 SKU 免費就跳過配額檢查。
> ⛔ region 換成備案之後，要更新 `prepare-plan.json` 裡**所有**的 `services[].region`。不要留下過時的值。

## 錯誤處理

| 錯誤 | 處理方式 |
|-------|-------------|
| Pricing API 400 | 確認有帶 `--sku`。免費層級：跳過 API |
| MCP pricing 無法使用 | 以 `task` 派出 [`subagent-pricing.md`](references/subagent-pricing.md) 當備案（直接用 HTTP 呼叫 `prices.azure.com`） |
| 缺少 prereq 輸出 | 觸發 prereq 補跑 |
| 配額檢查失敗 | 退回盡力估算，並附上免責聲明 |
| Override 衝突 | 帶著新的限制從步驟 3 重跑 |
