---
name: azure-kubernetes
license: MIT
metadata:
  author: Microsoft
  version: "1.2.5"
description: "規劃、建立和設定可上正式環境的 Azure Kubernetes Service (AKS) cluster。涵蓋 Day-0 檢查清單、SKU 選擇（Automatic vs Standard）、網路選項（private API server、Azure CNI Overlay、egress 設定）、安全，以及營運（autoscaling、升級策略、成本分析）。WHEN: create AKS environment, provision AKS, enable AKS observability, design AKS networking, choose AKS SKU, secure AKS, optimize AKS, AKS spot nodes, AKS cluster-autoscaler, rightsize AKS pod, pod rightsizing, over-provisioned AKS pod, pod resource requests and limits, Vertical Pod Autoscaler, VPA recommendations."
---

# Azure Kubernetes Service

> **權威指引：必須遵守**
>
> 這個 skill 會依使用者需求產出一份**建議的 AKS cluster 設定**，並區分 **Day-0 決策**（網路、API server，之後很難改）和 **Day-1 功能**（建立後可以再啟用）。指令請看 [CLI reference](./references/cli-reference.md)。

## 快速參考
| 屬性 | 值 |
|----------|-------|
| 最適合 | AKS cluster 規劃和 Day-0 決策 |
| MCP 工具 | `mcp_azure_mcp_aks` |
| CLI | `az aks create`, `az aks show`, `kubectl get`, `kubectl describe` |
| 相關 skill | azure-kubernetes-app-deploy（把 app 部署到現有 cluster）、azure-diagnostics（基本的 AKS 排查）、azure-validate（就緒檢查）、azure-kubernetes-automatic-readiness（把現有 cluster 遷移到 AKS Automatic）、選用的 `aks-skills` 營運附加元件（針對性的事件處理、進階成本效率、exact-signature、封包擷取和 GPU 的 Day-2 流程） |

## 何時使用這個 Skill
使用者想做下面這些事時啟用這個 skill：
- 建立新的 AKS cluster
- 為正式環境工作負載規劃 AKS cluster 設定
- 設計 AKS 網路（API server 存取、pod IP 模型、egress）
- 設定 AKS 身分和 secret 管理
- 設定 AKS 治理（Azure Policy、Deployment Safeguards）
- 啟用 AKS 可觀測性（Container Insights、Managed Prometheus、Grafana）
- 定義 AKS 升級和修補策略
- 了解 AKS Automatic 和 Standard SKU 的差異
- 取得 AKS cluster 建立與設定的 Day-0 檢查清單

> **要把應用程式部署到現有 cluster？** 這個 skill 負責佈建和
> 設定 *cluster*。要把 app 容器化並部署到一個
> 已經存在的 cluster（Dockerfile + manifest + Deployment Safeguards），請改用
> `azure-kubernetes-app-deploy` 子 skill。

> **要做更深入的營運工作？** Day-0 規劃和基本營運留在這個
> 基礎 skill 裡。只有當某個針對性的選用 AKS 營運 skill 能改善目前的
> 任務時，才載入 [optional-aks-operations.md](./references/optional-aks-operations.md)。

## 規則
1. 從使用者對佈建運算、網路、安全和其他設定的需求開始。
2. 用 `azure` MCP server，並先選 `mcp_azure_mcp_aks`，找出 client 提供的確切 AKS 專屬 MCP 工具。選符合任務、最小的那個 AKS 工具，只有在 AKS MCP 介面沒有提供需要的功能時，才退回用 Azure CLI（`az aks`）。
3. 依使用者要控制還是要方便，判斷用 AKS Automatic 還是 Standard SKU 比較合適。除非需要特定客製，預設用 AKS Automatic。
4. 記錄 cluster 設定選擇的決策和理由，特別是之後很難改的 Day-0 決策（網路、API server 存取）。


## 必要輸入（只問需要的）
使用者不確定的話，就用安全的預設值。
- AKS 環境類型：dev/test 或 production
- Region、availability zone、偏好的 node VM 大小
- 預期規模（node／cluster 數量、工作負載大小）
- 網路需求（API server 存取、pod IP 模型、ingress/egress 控制）
- 安全和身分需求，包含 image registry
- 升級和可觀測性的偏好
- 成本限制

## 工作流程

### 1. Cluster 類型
- **AKS Automatic**（預設）：最適合大多數正式環境工作負載，提供精選的體驗，預先設定好安全、可靠性和效能的最佳實務。除非你有 Node Auto-Provisioning (NAP) 不支援的網路、autoscaling 或 node pool 設定的特殊需求，否則就用這個。
- **AKS Standard**：需要完全掌控環境設定時用，代價是要多花功夫設定和管理。

### 2. 網路（Pod IP、Egress、Ingress、Dataplane）

**Pod IP 模型**（關鍵的 Day-0 決策）：
- **Azure CNI Overlay**（建議）：pod IP 來自私有的 overlay 範圍，VNet 無法路由，能擴展到大型環境，適合大多數工作負載
- **Azure CNI（VNet 可路由）**：pod IP 直接來自 VNet（pod subnet 或 node subnet），當 pod 必須能從 VNet 或地端直接定址時用
  - 文件：https://learn.microsoft.com/azure/aks/azure-cni-overlay

**Dataplane 與 Network Policy**：
- **Azure CNI powered by Cilium**（建議）：以 eBPF 為基礎，提供高效能的封包處理、network policy 和可觀測性

**Egress**：
- **Static Egress Gateway**，取得穩定、可預測的對外 IP
- 受限的 egress：UDR + Azure Firewall 或 NVA

**Ingress**：
- **搭配 Gateway API 的 App Routing addon**：HTTP/HTTPS 工作負載的建議預設選項
- **搭配 Gateway API 的 Istio service mesh**：用於進階流量管理、mTLS、canary 發佈
- **Application Gateway for Containers**：用於整合 WAF 的 L7 負載平衡

**DNS**：
- 在所有 node pool 啟用 **LocalDNS**，取得可靠、高效能的 DNS 解析

### 3. 安全
- 到處都用 **Microsoft Entra ID**（控制平面、給 pod 用的 Workload Identity、node 存取）。避免靜態憑證。
- 用 **Secrets Store CSI Driver** 接 Azure Key Vault 來管 secret
- 啟用 **Azure Policy** + **Deployment Safeguards**
- 啟用 etcd/API server 的**靜態加密**；node 之間的**傳輸中加密**
- 只允許經過簽署、符合 policy 的 image（Azure Policy + Ratify），優先用 **Azure Container Registry**
- **隔離**：用 namespace、network policy、限定範圍的 logging

### 4. 可觀測性
- AKS 的可觀測性（log + metrics）用 Managed Prometheus 和 Container Insights 搭配 Grafana。
- 啟用 Diagnostic Settings，把控制平面 log 和稽核 log 收集到 Log Analytics workspace，用於安全監控和排查。
- 其他監控和排查工具，可以用 Agentic CLI for AKS、Application Insights、Resource Health Center、AppLens detector 和 Azure Advisor 這些功能。

### 5. 升級與修補
- 設定 **Maintenance Window** 來控制升級時間
- 啟用控制平面和 node OS 的 **auto-upgrade**，保持安全修補和 Kubernetes 版本在最新
- 企業要穩定的話，考慮 **LTS 版本**（2 年支援），做法是把 AKS 環境升級到 Premium tier
- **Fleet 升級**：用 **AKS Fleet Manager** 在測試到正式環境之間分階段推出

### 6. 效能
- 用 **Ephemeral OS disk**（`--node-osdisk-type Ephemeral`）加快 node 啟動
- 選 **Azure Linux** 當 node OS（佔用空間較小、開機較快）
- 啟用 **KEDA**，做 HPA 以外的事件驅動 autoscaling

### 7. Node Pool 與運算
- **專用的 system node pool**：至少 2 個 node，加 taint 只給 system 工作負載用（`CriticalAddonsOnly`）
- **Node Auto Provisioning (NAP)** 是以 cluster 為單位啟用的，當動態容量符合工作負載需求時
  可以降低成本；但不保證一定省錢。
  新 cluster 要啟用 NAP。現有 cluster 的話，用
  [optional AKS operations](./references/optional-aks-operations.md)，有的話呼叫
  `aks-cost-optimization` 來看 NAP 就緒度。否則就繼續看
  [base NAP readiness](./references/azure-aks-nap-readiness.md)。
- 用**最新世代的 SKU（v5/v6）**，取得 host 層級的最佳化
- **避免 B 系列 VM**：burstable SKU 會造成效能和可靠性問題
- 正式環境工作負載用**至少 4 個 vCPU** 的 SKU
- 設定 **topology spread constraint**，依 SLO 把 pod 分散到不同 host/zone

### 8. 可靠性
- 部署到 **3 個 Availability Zone**（`--zones 1 2 3`）
- 用 **Standard tier**，取得 zone 冗餘的控制平面，以及 API server 99.95% 的 SLA 可用性
- 啟用 **Microsoft Defender for Containers**，做 runtime 防護
- 為所有正式環境工作負載設定 **PodDisruptionBudget**
- 用 **topology spread constraint** 確保 pod 分散在不同的故障網域

### 9. 成本控制
- 批次／可中斷的工作負載用 **Spot node pool**（最多省 90%）
- dev/test cluster 用 **Stop/Start**：`az aks stop/start`

#### 針對性的 AKS 成本流程

針對性的請求，只載入相關的參考檔案。

| 情境 | 觸發關鍵字 | 參考 |
|----------|-----------------|-----------|
| Pod Rightsizing | over-provisioned pods, CPU requests, memory requests, rightsize workloads | [azure-aks-rightsizing.md](./references/azure-aks-rightsizing.md) |
| VPA 設定 | vertical pod autoscaler, VPA recommendations, VPA enable | [azure-aks-vpa.md](./references/azure-aks-vpa.md) |
| Cluster Autoscaler | idle nodes, CAS off, enable autoscaler, scale-down profile, node utilization | [azure-aks-autoscaler.md](./references/azure-aks-autoscaler.md) |
| Spot Node Pool | Spot VMs, Spot nodes, batch workloads, cheaper nodes | [azure-aks-spot.md](./references/azure-aks-spot.md) |
| 進階 AKS 成本效率 | NAP readiness, node-pool bin packing, blocked scale-down, Kubernetes storage cost | [optional AKS operations](./references/optional-aks-operations.md) |

> **釐清歧義：** 如果一個 prompt 同時符合多列（例如「cheaper nodes」可能同時指 Spot 和 autoscaler），優先選最具體的那個。如果還是不明確，先請使用者說清楚意圖，再載入參考檔案。

#### 完整的 AKS 成本檢視

當使用者要的是整體的 AKS 成本評估，而不是單一的針對性流程時，
這個 skill 負責分流，並協調一份統一的檢視：

1. 確認目標的 subscription、resource group 和 AKS cluster。如果有 `cost-analysis`，就針對該範圍收集一份帳單成本基準，整個檢視過程都重複使用。
2. 評估適用的 rightsizing、VPA、Cluster Autoscaler 和 Spot 流程。
3. 需要 NAP 就緒度、node pool bin packing、node 擴縮瓶頸，或 Kubernetes 到 Azure 的儲存最佳化時，有的話就呼叫 `aks-cost-optimization`。
4. 檢查是否有穩定的非 Spot 需求。如果有，有的話就呼叫 `cost-optimization` 做承諾用量分析。如果沒有這個能力或證據，就把承諾用量分析回報為缺口。光憑這份檢視不要建議購買。

調查所有適用的槓桿，回傳一份依序排名的報告。有可比較的
預估成本影響時就依它排名；不知道金額影響的就維持未知，
不要當成零。不要把單一的窄範圍分析當成完整的檢視。
把沒有的能力或證據標成缺口。

| 排名 | 槓桿 | 證據 | 預估成本影響與依據 | 風險 | 需要核准 | 信心度 |
|---|---|---|---|---|---|---|

## 護欄／安全
- 不要要求或輸出 secret（token、金鑰）。
- 不要請使用者貼上 subscription ID。透過 MCP 工具（例如列出 subscription、列出 resource group）或 `az account show` / `az account list` 找出 subscription 和資源範圍，這樣 agent 不用暴露識別碼就能解析 context。
- 如果 Day-0 關鍵決策的需求不明確，就問使用者釐清問題。對於 Day-1 啟用的功能，提出 2 到 3 個附帶取捨的安全選項，並選一個保守的預設值。
- 不要承諾零停機；要建議工作負載的保護措施（PDB、probe、replica）和分階段升級，以及可靠性和效能的最佳實務。

## MCP 工具
| 工具 | 用途 | 關鍵參數 |
|------|---------|----------------|
| `mcp_azure_mcp_aks` | AKS MCP 的入口，用來找出 client 提供的確切 AKS 專屬工具 | 先找出可呼叫的 AKS 工具，再用那個工具的參數 |

## 錯誤處理
| 錯誤／症狀 | 可能原因 | 修復方式 |
|-----------------|--------------|-------------|
| MCP 工具呼叫失敗或 timeout | 憑證、subscription 或 AKS context 無效 | 確認 `az login`，用 `az account show` 確認目前的 subscription context，並檢查目標 resource group，不要把 subscription 識別碼回顯給使用者 |
| 超出配額 | Region 的 vCPU 或資源上限 | 申請提高配額，或改選不同的 region／VM SKU |
| 網路衝突（IP 耗盡） | Pod subnet 對 overlay/CNI 來說太小 | 重新規劃 IP 範圍；可能需要重建 cluster（Day-0） |
| Workload Identity 沒作用 | 缺少 OIDC issuer 或 federated credential | 啟用 `--enable-oidc-issuer --enable-workload-identity`，設定 federated identity |
