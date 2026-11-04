---
name: azure-local
description: "規劃、部署、維運並排除 Azure Local（前身是 Azure Stack HCI）的問題：容量規劃與前置條件、Arc 註冊、生命週期更新、工作負載（Azure Local VM、Azure Local 上的 AKS、映像、磁碟、邏輯網路）、SDN 與網路安全，以及故障分流；一律從唯讀開始，有風險的變更先確認。WHEN: Azure Local, Azure Stack HCI, Arc resource bridge, custom location, Azure Local VM, Arc VM, AKS on Azure Local, AKS hybrid, SDN, Lifecycle Manager, Azure Local update, disconnected site."
license: MIT
metadata:
  author: Microsoft
  version: "1.0.1"
---

# Azure Local

## 快速參考

| 屬性 | 值 |
| --- | --- |
| 適用於 | Azure Local 的規劃、部署、維運、工作負載 |
| MCP 工具 | 只有通用的 Azure MCP 工具；沒有 Azure Local 專屬的 namespace |
| CLI | `az graph query`、`az resource show`、Azure Local PowerShell |
| 相關 skill | azure-compute（公有雲 VM）、azure-kubernetes（公有雲 AKS） |

## 何時使用這個 Skill

用在 Azure Local、Azure Stack HCI、Azure Local VM、Azure Local 上的 AKS、AKS hybrid、SDN、生命週期更新、離線站點，或故障排除。涵蓋標準部署（1 到 16 節點的超融合，解耦式最多 64 節點）和 rack-aware 叢集。

不要用在雲端 VM 或公有雲 AKS 的指引，也不要用在 **multi-rack（rack scale）** 部署，那些用另一套控制平面和流程。這種情況轉給 `azure-local-multi-rack` skill。

## MCP 工具

Azure Local 沒有專屬的 MCP namespace。用通用的 Azure MCP 工具：`mcp_azure_mcp_extension_cli_generate`（ARG/CLI 盤點）、`mcp_azure_mcp_monitor`（需要 Log Analytics）、`mcp_azure_mcp_resourcehealth`（部分支援；不含本機叢集健康狀態）、`mcp_azure_mcp_documentation`（已知使用者的版本時要帶進去）。

範圍與限制：[mcp-and-cli-tools](references/mcp-and-cli-tools.md)。

## 工作流程

0. 確認部署規模。如果使用者提到 multi-rack、aggregation rack、Network Fabric Controller、Cluster Manager，或 `Microsoft.NetworkCloud` 資源，就停下來，改用 `azure-local-multi-rack` skill。
1. 部署 -> [plan-and-deploy](workflows/plan-and-deploy/plan-and-deploy.md)
2. 維運/更新 -> [operate-and-update](workflows/operate-and-update/operate-and-update.md)
3. VM、AKS、映像、磁碟、網路 -> [workload-management](workflows/workload-management/workload-management.md)
4. SDN、NSG、load balancer、gateway -> [networking-and-security](workflows/networking-and-security/networking-and-security.md)
5. 故障 -> [troubleshooting](workflows/troubleshooting/troubleshooting.md)

先讀對應的 workflow，並使用 [docs-map](references/docs-map.md)。從唯讀開始。更新、刪除、重灌映像、網路變更、VM 開關機/刪除操作，或 Arc bridge/custom location 變更之前，一定要先問。

## 錯誤處理

| 情境 | 處理方式 |
| --- | --- |
| 不知道規模 | 給任何流程之前，先問部署是標準還是 multi-rack。 |
| 偵測到 multi-rack | 轉給 `azure-local-multi-rack` skill；這裡的流程不適用。 |
| 不知道版本 | 問使用者 Azure Local 的版本，或用最新的文件。 |
| 偵測到有風險的變更 | 停下來，照 [safety-rules](references/safety-rules.md) 處理。 |
| 沒有本機存取權限 | 只做 Azure 控制平面的檢查。 |
| 文件 URL 404/轉址 | 用使用者的版本到 Learn 搜尋文章標題。 |
