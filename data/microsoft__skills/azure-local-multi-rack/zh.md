---
name: azure-local-multi-rack
description: "規劃、部署、維運並排除 Azure Local multi-rack（rack scale）部署的問題：預先整合好的機櫃，可擴展到數百台機器，建構在 Network Fabric Controller、Cluster Manager、SAN 儲存和受管網路 fabric 上。用於 Microsoft.NetworkCloud 和 Microsoft.ManagedNetworkFabric 控制平面。不適用於標準的 1 到 16 節點 Azure Local，也不適用於 rack-aware 叢集（兩個機櫃當可用性區域，最多 8 節點，同步複寫），那些屬於標準規模。WHEN: multi-rack, rack scale Azure Local, aggregation rack, compute rack, Network Fabric Controller, NFC, Cluster Manager, network fabric, isolation domain, az networkcloud, az networkfabric, multi-rack logical network, multi-rack Arc VM."
license: MIT
metadata:
  author: Microsoft
  version: "1.0.1"
---

# Azure Local Multi-Rack

> Multi-rack 目前是 **preview**，要跟使用者講清楚，而且在敲定設計之前，先從文件確認是否已開放使用。

## 快速參考

| 屬性 | 值 |
| --- | --- |
| 適用於 | Rack-scale 的 Azure Local：100 台以上機器、預先整合的機櫃、SAN、受管 fabric |
| 規模 | 至少四個機櫃：一個 aggregation rack 加三個以上的 compute rack |
| Provider | `Microsoft.NetworkCloud`、`Microsoft.ManagedNetworkFabric`、`Microsoft.AzureStackHCI` |
| CLI | `az networkcloud`、`az networkfabric`、`az stack-hci-vm` |
| 相關 skill | 標準 1 到 16 節點和 rack-aware 部署用 `azure-local` |

## 何時使用這個 Skill

部署是 multi-rack / rack scale 時用：預先整合的機櫃、aggregation rack、Network Fabric Controller、Cluster Manager、SAN 儲存，或 `networkcloud` / `managednetworkfabric` 這兩個 CLI extension。

標準的 Azure Local（1 到 16 節點超融合，解耦式最多 64 節點）或 rack-aware 叢集**不要**用這個，轉給 `azure-local` skill。規模不清楚的話先問：兩者對聽起來一樣的工作（邏輯網路、建 VM、NSG）有各自獨立、不能互換的流程。

## MCP 工具

沒有專屬的 MCP namespace。用通用的 Azure MCP 工具：`mcp_azure_mcp_extension_cli_generate`（先確認 `networkcloud`/`networkfabric` extension 有裝）、`mcp_azure_mcp_monitor`（需要 Log Analytics）、`mcp_azure_mcp_resourcehealth`（部分支援；不含 fabric 或 SAN 的健康狀態）、`mcp_azure_mcp_documentation`（只查 multi-rack 的文章，標準 Azure Local 的頁面不適用）。

細節：[cli-and-prereqs](references/cli-and-prereqs.md)。

## 工作流程

1. 確認這是 multi-rack，不是標準的 Azure Local，見「何時使用這個 Skill」。
2. 規劃/部署 -> [plan-and-deploy](workflows/plan-and-deploy/plan-and-deploy.md)
3. VM、AKS、映像、磁碟 -> [workload-management](workflows/workload-management/workload-management.md)
4. Fabric、isolation domain、load balancer、NSG -> [networking](workflows/networking/networking.md)
5. 監控、指標、序列主控台、故障 -> [operate-and-monitor](workflows/operate-and-monitor/operate-and-monitor.md)

先讀對應的 workflow，並使用 [docs-map](references/docs-map.md)。從唯讀開始。fabric 變更、isolation domain 編輯、VM 開關機/刪除操作，或任何會動到 aggregation rack 或 SAN 的事，一定要先問。

## 錯誤處理

| 情境 | 處理方式 |
| --- | --- |
| 不知道規模 | 推薦任何流程之前，先問部署是 multi-rack 還是標準。 |
| 偵測到標準 Azure Local | 轉給 `azure-local` skill；multi-rack 的流程不適用。 |
| 缺少 CLI extension | 執行指令之前，先照 [cli-and-prereqs](references/cli-and-prereqs.md) 安裝。 |
| 有風險的 fabric 或 SAN 變更 | 停下來，照 [safety-rules](references/safety-rules.md) 處理。 |
| 文件 URL 404/轉址 | 到 Learn 搜尋標題，範圍限定在 Azure Local 的 multi-rack 部署。 |
