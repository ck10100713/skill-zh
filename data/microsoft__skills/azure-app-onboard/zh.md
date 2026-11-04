---
name: azure-app-onboard
description: "端到端的 orchestrator：從商業點子、app 點子或既有的 app，一路到跑起來的 Azure 部署，附成本估算和部署前核准。它會分析你的 app、自動偵測合適的 Azure 服務、產生 infrastructure 程式碼骨架並部署，一切針對你的 app 量身打造，不是套模板。也能處理把既有 app 搬到 Azure，不用重寫或只需最小改動。WHEN: bring your app to Azure, plan my app, cost to run, is my code ready to deploy, deploy my app to the cloud, deploy all my services, what Azure services do I need, plan my Azure deployment, deploy my new app to Azure, one-click deploy, I have an app and want it on Azure, migrate my app to Azure, help me get started, build an app, no code yet, starter project. DO NOT USE FOR: use azd for deployment(use azure-deploy), optimizing existing costs (use cost-optimization), code readiness checks only (use azure-app-onboard-prereq)."
license: MIT
metadata:
  author: Microsoft
  version: "1.2.7"
---

# Azure App Onboard

> ⛔ **每個 repo 都要走完整條 pipeline（Step 1–10），沒有例外。** 不准跳步驟、不准拒絕，也不准憑你認得出的東西走捷徑。依序照下面的 Workflow 表走，動手之前先讀完每一步的 references。

## Quick Reference

| Property | Value |
|----------|-------|
| Best for | 知道要做什麼，但不知道該用哪些 Azure 服務的開發者 |
| Inputs | 商業點子或既有的 codebase，預算/規模偏好（選填） |
| Outputs | 架構規劃、成本估算、IaC 檔案、已部署的 Azure 資源 |
| Phases | Discover → Architect → Scaffold → Deploy（自成一體，不呼叫外部 skill） |

## When to Use This Skill

- 要部署既有程式碼，但不知道該用哪些 Azure 服務
- 檢查既有程式碼是否已準備好部署到 Azure
- 把既有的 app 搬到 Azure，不用重寫或只需最小改動
- 在投入 infrastructure 之前先拿到成本估算
- 了解架構決策和被否決的替代方案
- 取得 Azure 架構或服務選擇問題的答案（例如「我該用哪種資料庫？」）
- 在沒有經驗的情況下取得 Azure 的上手引導

## When NOT to Use

| Scenario | Use Instead |
|----------|-------------|
| 執行 `azd up` 或執行既有的部署 | `azure-deploy` |
| 優化既有的 Azure 花費 | 選用的 `azure-cost` plugin 裡的 `cost-optimization` |
| 針對已知架構產生 Bicep/Terraform | `azure-prepare` |
| 驗證 infrastructure 或跑 preflight 檢查 | `azure-validate` |
| 排查執行中的 Azure 部署問題 | `azure-diagnostics` |
| 直接部署或管理 AKS/Kubernetes | `azure-kubernetes` |
| 查詢或列出既有的 Azure 資源 | `azure-resource-lookup` |

如果 `cost-optimization` 不可用，要說明它是由選用的
`azure-cost` plugin 提供，並引導使用者走他們 client 支援的
plugin 安裝流程，不要暗示交接已經完成。

## Pipeline Rules

> ⛔ **每個 AppOnboard session 一開始，你一定要讀 [`references/pipeline-rules.md`](references/pipeline-rules.md)。** 裡面有核准關卡、phase 生命週期、session 產出物、deploy-as-is 和安全基線的規則。

## Workflow

> ⛔ **Deploy 恢復：** 在部署關卡核准之後，或在任何 `az deployment`/`az webapp deploy`/`az acr build` 之前，如果你還沒讀過 `deploy/SKILL.md`，先讀 `.copilot-azure/sessions/{id}/deploy-checklist.md`，再讀 `deploy/SKILL.md`。⛔ 絕對不准呼叫 `{"skill": "azure-deploy"}`，那是另一個 skill，用在另一套工作流程。

> ⛔ **Scaffold 之後的轉場（必做）：** `scaffold-manifest.json` 一寫完，你的下一個動作一定是 Step 8（Deploy Approval Gate），不是總結報告、不是「這是產生的檔案」訊息、也不是完成訊號。確認 `context.json` 有 `completedPhases: [...,"scaffold"]` + `currentPhase: "deploy"`（如果 scaffold subagent 沒更新就自己更新）。如果 context 被擠掉了（scaffold 載入 reference 很吃空間），要重讀 [approval-gates.md § Deploy Gate](references/approval-gates.md)，然後原封不動地顯示這段提示：**"🚀 Ready to deploy? (Yes / Run manually / Edit plan / Cancel)"**。這個關卡必須是你回應的最後一段內容，然後等使用者回覆。

| # | Step | Action | Reference |
|---|------|--------|-----------|
| 1 | **Session check + Azure login** | 建立/恢復 session，驗證 Azure CLI 驗證狀態，解析 subscription 和使用者身分 | ⛔ **你一定要讀 [session-protocol.md](references/session-protocol.md)** |
| 2 | **Scope triage** | 檢查 azd 標記，做 triage 提問。空的 workspace 或只有程式碼（沒有 infra）→ 直接到 Step 3。 | ⛔ 讀 [intent-gathering.md](references/intent-gathering.md) § Scope Triage |
| 3 | **Prereq scan** | ⛔ 如果 `completedPhases` 包含 `"prereq"` 就跳過。否則：呼叫 `{"skill": "azure-app-onboard-prereq"}`。寫入 `prereq-output.json`，更新 `context.json`。**以下情況要停下來：** `overallHealth: "blocked"` 或有設定 `routeToSkill`。 | |
| 4 | **Gather intent** | 呈現 prereq 結果，確認技術棧和 Azure 服務，問剩下的問題。 | ⛔ 讀 [intent-gathering.md](references/intent-gathering.md) § After Prereq Returns |
| 5 | **Plan architecture** | 寫入 `prepare-plan.json`。 | ⛔ **你一定要讀 [prepare/SKILL.md](prepare/SKILL.md)** |
| 6 | **Scaffold approval gate** | 在產生任何檔案之前，先顯示規劃讓使用者核准。 | ⛔ 讀 [approval-gates.md](references/approval-gates.md) § Scaffold Gate |
| 7 | **Scaffold** | 產生 IaC，自我 review。寫入 `scaffold-manifest.json`。更新 `context.json`。 | ⛔ **你一定要讀 [scaffold/SKILL.md](scaffold/SKILL.md)** |
| 8 | **Deploy approval gate** | 顯示驗證摘要。⛔ 核准之後：先讀 deploy-checklist.md → deploy/SKILL.md。絕對不准 `{"skill": "azure-deploy"}`。 | ⛔ 讀 [approval-gates.md](references/approval-gates.md) § Deploy Gate |
| 9 | **Deploy** | 執行 IaC，做 health-check。寫入 `deploy-result.json`。 | ⛔ **你一定要讀 [deploy/SKILL.md](deploy/SKILL.md)** |
| 10 | **Handoff** | 呈現部署身分、清理指令和下一步。 | ⛔ **你一定要讀 [`handoff-protocol.md`](references/handoff-protocol.md)** |

## Error Handling

| Error | Remediation |
|-------|-------------|
| Phase 失敗 | 停下來，回報 phase 和錯誤。由使用者決定：重試、跳過或中止。 |
| MCP server 無法使用 | 跳過受影響的檢查，在 `costEstimate.assumptions[]` 和每個核准關卡加上免責聲明。 |
| 缺少 RBAC | 回報需要的角色和 `az role assignment` 指令。 |

> **共用 references：** [MCP tools](references/mcp-tool-reference.md)（跨 phase 的 tool 參數）| [IaC resources](references/iac-resources.md)（排查問題用的 Azure 資源文件）
