---
name: aks-cost-optimization
license: MIT
metadata:
  author: Microsoft
  version: "1.0.10"
description: "分析進階的 AKS 成本效率。WHEN: \"AKS NAP readiness\", \"AKS bin packing\", \"AKS node scaling bottleneck\", \"AKS blocked scale-down\", \"AKS storage cost\"。不要當作以下情境的直接入口：整體 AKS 成本評估或 rightsizing／VPA／CAS／Spot（用 azure-kubernetes）；花費／異常／承諾用量（用 cost-analysis／cost-optimization）；事故（用 aks-troubleshooting）。"
---

# AKS 成本最佳化

## 何時使用這個 Skill

用在需要排程、放置（placement）或
經過驗證的儲存對應的進階既有 cluster 分析。整體 AKS 成本評估交給
`azure-kubernetes`，花費／異常交給 `cost-analysis`，承諾用量交給
`cost-optimization`，事故交給 `aks-troubleshooting`（這些 skill 可用時）。如果是從整體評估呼叫進來的，就把發現回傳給它的排序報告。

## MCP 工具

優先用合適的 Azure MCP 讀取。絕對不要自己發明工具，也不要在沒有
核准的 shell 存取和綁定目標的 context 下使用 `az`／`kubectl`。

## 流程／步驟

1. 綁定 subscription、cluster、resource group 和 kube context。
2. 依情況導向 [NAP readiness](references/aks-nap.md)、
   [bin-packing](references/aks-bin-packing.md)、
   [node-scaling bottlenecks](references/node-scaling-bottlenecks.md) 或
   [storage optimization](references/aks-storage-optimization.md)。
3. 為了 AKS 承諾用量的背景而被呼叫時，使用
   [commitment-demand handoff](references/aks-savings-plans-reservations.md)，
   只回傳需求證據，不做效益分析，也不執行交易。
4. 讀取一律不改動任何東西；每一項變更都要經過核准。

## 錯誤處理

- 缺少能力：分析使用者提供的證據，或給一份蒐集計畫；
  相依的成本或承諾用量結果標示為無法取得。
- 證據互相矛盾：把結論標示為未確認。
