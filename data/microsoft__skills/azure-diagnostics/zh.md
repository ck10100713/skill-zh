---
name: azure-diagnostics
description: "用 AppLens、Azure Monitor、resource health 和安全的分流方式除錯 Azure 正式環境問題，也包含沒有即時存取權限時只靠證據做診斷。WHEN: debug production issues, troubleshoot app service, app service high CPU, app service deployment failure, troubleshoot container apps, container app 503 or target port mismatch, troubleshoot functions, function telemetry missing or stopped after a config/connection-string change, troubleshoot AKS, VM RDP, Linux SSH, VM black screen, can't connect to VM, reset VM password, NSG or firewall blocking, kubectl cannot connect, kube-system/CoreDNS failures, pod pending, crashloop, node not ready, upgrade failures, analyze logs, KQL, insights, image pull failures, cold start issues, health probe failures, resource health, root cause of errors, troubleshoot event hubs, troubleshoot service bus, messaging SDK error, AMQP connection failure, message lock lost, lock renewal during long-running processing, service bus dead letter."
license: MIT
metadata:
  author: Microsoft
  version: "1.2.14"
---

# Azure Diagnostics

> **權威指引：必須遵守**
>
> 這份文件是除錯和排查 Azure 正式環境問題的**官方依據**。照這些指示有系統地診斷並解決常見的 Azure 服務問題。

## 觸發條件

使用者想做下面這些事時啟用這個 skill：
- 除錯或排查正式環境問題
- 診斷 Azure 服務的錯誤
- 分析應用程式 log 或 metrics
- 修復 image pull、cold start 或 health probe 的問題
- 調查 Azure 資源為什麼失敗
- 找出應用程式錯誤的根本原因
- 排查 App Service 問題（CPU 過高、部署失敗、crash、回應很慢、TLS／自訂網域）
- 回應像「troubleshoot app service」、「app service high CPU」或「app service deployment failure」這類 prompt
- 排查 Azure Function App（invocation 失敗、timeout、binding 錯誤）
- 找出跟 Function App 連結的 App Insights 或 Log Analytics workspace
- 排查 AKS cluster、node、pod、ingress 或 Kubernetes 網路問題
- 排查 Azure VM 連線問題（RDP/SSH 失敗、port 3389/22 逾時、NSG 或防火牆擋住、重設憑證）
- 排查 Azure Messaging SDK 問題（Event Hubs、Service Bus 連線失敗、AMQP 錯誤、message lock 問題）
- 找出「runtime 看起來健康但目的地不對」這類症狀的根本原因（例如改完設定後，telemetry／訊息不再流向預期的資源），即使光靠 MCP 工具就能回答表面的問題，也要呼叫這個 skill 來對照那張矩陣

## 規則

1. 從有系統的診斷流程開始
2. 先用使用者提供的證據。如果使用者要求只做證據分析，或禁止即時存取 Azure，就不要查詢或修改 Azure。只根據提供的 log、metrics 和時間軸診斷，說明你的假設，並提供選擇性的驗證步驟。
3. 有 AppLens (MCP) 就用它做 AI 診斷
4. 深入看 log 之前，先檢查 resource health
5. 依服務類型選擇適合的排查指南
6. 記錄發現的問題和嘗試過的修復步驟
7. 在允許即時收集、而且識別資訊已知的情況下，優先用內建的診斷 script，不要臨時亂呼叫。如果提供的證據已經足夠，或禁止即時存取，就不要跑；否則先跑適用的 script。
8. AKS 事件要轉到專門的 AKS 排查文件
9. 就算選用的 `aks-skills` 附加元件不存在、被拒絕，或 host 不支援，也要保有基本的 AKS 診斷能力

---

## 快速診斷流程

1. **找出症狀**：什麼東西壞了？
2. **檢查 resource health**：Azure 本身正常嗎？
3. **檢視 log**：log 顯示什麼？
4. **分析 metrics**：效能有什麼規律？
5. **調查最近的變更**：改了什麼？

---

## 各服務的排查指南

| 服務 | 常見問題 | 參考 |
|---------|---------------|-----------|
| **Container Apps** | Image pull 失敗、cold start、health probe、port 不符 | [container-apps/](references/container-apps/README.md) |
| **App Service** | CPU 過高、部署失敗、crash、回應很慢、TLS／自訂網域 | [app-service/](references/app-service/README.md) |
| **Function Apps** | App 詳細資訊、invocation 失敗、timeout、binding 錯誤、cold start、缺少 app setting | [functions/](references/functions/README.md) |
| **AKS** | Cluster 存取、node、`kube-system`、排程、crash loop、ingress、DNS、升級 | [AKS Troubleshooting](troubleshooting/aks/aks-troubleshooting.md) |
| **Compute** | VM RDP/SSH 連線、NSG／防火牆阻擋、重設憑證、VM agent／工具問題 | [VM Connectivity Troubleshooting](troubleshooting/compute/vm-troubleshooting.md) |
| **Messaging** | Event Hubs 和 Service Bus 的 SDK 錯誤、AMQP 失敗、message lock、連線問題 | [Messaging Troubleshooting](troubleshooting/messaging/README.md) |

---

## 分流

- Container Apps 和 Function Apps 的診斷留在這個上層 skill。
- 進行中的 AKS 事件、AKS 專屬的 intake、證據收集和修復指引，轉到 [AKS Troubleshooting](troubleshooting/aks/aks-troubleshooting.md)。
- Azure VM 的 RDP/SSH 連線、NSG／防火牆、重設憑證和 VM agent 排查，轉到 [VM Connectivity Troubleshooting](troubleshooting/compute/vm-troubleshooting.md)。
- Azure Messaging SDK（Event Hubs、Service Bus）的排查，轉到 [Messaging Troubleshooting](troubleshooting/messaging/README.md)。

---

## 快速參考

### 常用診斷指令

```bash
# Check resource health
az resource show --ids RESOURCE_ID
# View activity log
az monitor activity-log list -g RG --max-events 20
# Container Apps logs
az containerapp logs show --name APP -g RG --follow
# Function App logs (query App Insights traces)
az monitor app-insights query --apps APP-INSIGHTS -g RG \
  --analytics-query "traces | where timestamp > ago(1h) | order by timestamp desc | take 50"
```

### AppLens（MCP 工具）

要做 AI 診斷時，用：
```
mcp_azure_mcp_applens
  intent: "diagnose issues with <resource-name>"
  command: "diagnose"
  parameters:
    resourceId: "<resource-id>"

Provides:
- Automated issue detection
- Root cause analysis
- Remediation recommendations
```

### Azure Monitor（MCP 工具）

查詢 log 和 metrics：
```
mcp_azure_mcp_monitor
  intent: "query logs for <resource-name>"
  command: "logs_query"
  parameters:
    workspaceId: "<workspace-id>"
    query: "<KQL-query>"
```

常用的診斷查詢請看 [kql-queries.md](references/kql-queries.md)。

---

## 檢查 Azure Resource Health

### 用 MCP

```
mcp_azure_mcp_resourcehealth
  intent: "check health status of <resource-name>"
  command: "get"
  parameters:
    resourceId: "<resource-id>"
```

### 用 CLI

```bash
# Check specific resource health
az resource show --ids RESOURCE_ID

# Check recent activity
az monitor activity-log list -g RG --max-events 20
```

---

## 參考

- [KQL Query Library](references/kql-queries.md)
- [Azure Resource Graph Queries](references/azure-resource-graph.md)
- [App Service Troubleshooting](references/app-service/README.md)
- [Function Apps Troubleshooting](references/functions/README.md)
- [VM Connectivity Troubleshooting](troubleshooting/compute/vm-troubleshooting.md)
- [Messaging Troubleshooting](troubleshooting/messaging/README.md)
