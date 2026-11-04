---
name: aks-network-capture
description: "從 AKS node 蒐集有範圍限制的封包擷取，並取得 Azure 網路設定，作為線路層級的證據。WHEN: \"capture packets on an AKS node\", \"take a pcap\", \"run tcpdump on AKS\", \"prove where packets drop\"。在唯讀診斷做完後、使用者明確要抓封包時使用，不適用一般的 AKS 連線或 ingress 疑難排解。"
license: MIT
metadata:
  author: Microsoft
  version: "1.0.1"
---

# AKS 網路封包擷取

## 速查

| 用途 | 需要 | 安全性 |
| --- | --- | --- |
| AKS pcap 證據 | `kubectl`；Azure 證據需要 `az` | 有範圍限制、固定版本、最小權限 |

## 何時使用這個 Skill

在唯讀檢查做完後，使用者明確要抓封包時才用，不用在一般的連線失敗。

## MCP 工具

Azure MCP 的 AKS 區塊只提供 cluster 和 node pool 的 metadata，不提供 Kubernetes
指令執行或封包擷取。

## Host 能力檢查關卡

執行流程之前，先確認 host 允許所需的
Bash 或 PowerShell 執行、對綁定 cluster 的 `kubectl` 存取、用於
Azure 證據的 `az`、附帶 script 的存取，以及核准的 artifact
存放位置。光有一個受管控的 Azure CLI 工具，並不代表支援 shell、
Kubernetes 指令或 artifact 操作。

如果缺少必要能力或被禁止，就說明在這個 host 上
無法執行擷取。分析使用者提供、經過適當
遮蔽的證據，或給操作人員一份綁定目標的蒐集／擷取計畫；
不要宣稱自己跑過。絕對不要透過 Azure MCP 去跑 `kubectl`，不要新增
未經核准的執行路徑，也不要繞過 host 的政策。Host 支援並不能取代
下面的變更與敏感資料核准。

通過這個檢查關卡之後，才從 skill 根目錄執行附帶的 script。

## 流程／步驟

0. 先檢查 host 能力，再完成[授權與目標綁定](references/capture-authorization.md)。
   想擷取封包不等於同意變更。在使用任何 debug container 備案之前，
   要停下來另外取得核准。
1. 安裝 [Bash](scripts/setup-capture-configmap.sh) / [PowerShell](scripts/setup-capture-configmap.ps1) 版。
2. 用 [Bash](scripts/create-capture.sh) / [PowerShell](scripts/create-capture.ps1) 對 node 或 pod 擷取。
3. 經核准的話，用 [Bash](scripts/generate-test-traffic.sh) / [PowerShell](scripts/generate-test-traffic.ps1) 產生流量。
4. 用 [Bash](scripts/retrieve-captures.sh) / [PowerShell](scripts/retrieve-captures.ps1) 取回確切那一次執行的結果。
5. 用 [Bash](scripts/collect-azure-network-info.sh) / [PowerShell](scripts/collect-azure-network-info.ps1) 蒐集 Azure 證據。

ConfigMap 會在它固定版本的 Linux image 裡執行 [run-capture.sh](scripts/run-capture.sh)。

## 錯誤處理

| 錯誤 | 處理 |
| --- | --- |
| 輸入無效 | 先修正再重試。 |
| ConfigMap 缺少或過期 | 重新執行 setup。 |
| 擷取／取回失敗 | 檢查 Job 的 log；缺少證據不算成功。 |
