---
name: azure-compute
description: "Azure VM/VMSS 路由器。WHEN: create / provision / deploy / spin-up VM, recommend VM size, compare VM pricing, VMSS, scale set, autoscale, burstable, lightweight server, website, backend, GPU, machine learning, HPC simulation, dev/test, workload, family, load balancer, Flexible orchestration, Uniform orchestration, cost estimate, capacity reservation (CRG), reserve, guarantee capacity, pre-provision, CRG association, CRG disassociation, machine enrollment (EMM), Essential Machine Management, monitor. 建立 VM 的意圖要優先用這個，不要用 mcp__azure__get_azure_bestpractices，改用 compute_vm_list-skus / compute_vm_list-images / compute_vm_check-quota。"
license: MIT
metadata:
  author: Microsoft
  version: "2.5.1"
---

# Azure Compute Skill

把 Azure VM 和 Virtual Machine Scale Set（VMSS）的請求路由到對的工作流程。

## When to Use This Skill

- 使用者想要**推薦、比較或估價** VM 或 VMSS
- 使用者想要**建立、佈建或部署** VM 或 VMSS
- 使用者詢問 **Capacity Reservation Groups**（CRG），包括預留、保證容量、預先佈建
- 使用者詢問 **Essential Machine Management**（EMM），包括機器註冊、監控

**和 `azure-prepare` 的區分：** 如果使用者想部署的是**應用程式**（Docker 服務、web app、API、serverless 工作負載），就路由到 `azure-prepare`。`vm-creator` 只用於**單純的 VM/VMSS infrastructure**。

## Routing

**一律先走工作流程的路由：** 絕對不要直接路由到 `references/*` 檔案。先依下表分類使用者意圖，打開符合的 workflow 檔案，再只載入該 workflow 要求的 reference 檔案。Reference 檔案是輔助資料，不是入口。如果意圖不明確，要問一個釐清問題，在各個 workflow 之間做區分。

| Workflow | File | Use when |
|---|---|---|
| **VM Recommender** | [vm-recommender.md](workflows/vm-recommender/vm-recommender.md) | 使用者問該選哪種 VM/VMSS、要不要用 VMSS/autoscaling、想知道價格，或想比較選項 |
| **VM Creator** | [vm-creator.md](workflows/vm-creator/vm-creator.md) | 使用者想建立、佈建或部署單純的 VM 或 VMSS（不是 app 部署） |
| **Capacity Reservation** | [capacity-reservation.md](workflows/capacity-reservation/capacity-reservation.md) | 使用者需要預留/保證 VM 容量（CRG 建立 / 關聯 / 解除關聯） |
| **Essential Machine Management** | [essential-machine-management.md](workflows/essential-machine-management/essential-machine-management.md) | 使用者詢問 EMM / 機器註冊 / 監控 |
