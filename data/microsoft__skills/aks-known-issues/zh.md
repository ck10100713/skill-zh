---
name: aks-known-issues
license: MIT
metadata:
  author: Microsoft
  version: "1.2.1"
description: "只有在 prompt 包含完整的目錄簽章和它所有限定條件時，才查詢已記載的 AKS 修法：VMCannotFitEphemeralOSDisk；NodePoolMcVersionIncompatible；'NodeImageVersion is not accepted'；帶有 size、location 和 zone 的 AKS SkuNotAvailable；帶有 zone 容量不足的 ZonalAllocationFailed；帶有列出限制條件的 OverconstrainedAllocationRequest；巢狀的 AKS vmssCSE/CSE VMExtensionError_OutboundConnFail、VMExtensionError_K8SAPIServerConnFail 或 VMExtensionError_K8SAPIServerDNSLookupFail；或帶有完整已編目 internal-error 或區域容量不足訊息的 AllocationFailed。絕對不要用在配額錯誤、只有錯誤碼或光禿禿的外層包裝、一般症狀、不完整的簽章，或 AKS 以外的故障；這些情況改用 aks-troubleshooting 或 azure-diagnostics。"
---

# AKS 已知問題

## 速查

| 屬性 | 值 |
|---|---|
| 適用情境 | 完整簽章加上 AKS 操作 |
| 輸出 | 成因、修法和 Learn 文件引用 |

使用 [catalog](references/error-code-map.md)。

## 何時使用這個 Skill

只處理目錄裡有列名的簽章。一般的 AKS 問題交給 `aks-troubleshooting`；非 AKS 的問題
不使用任何 AKS skill。

目錄裡某一列的限定條件只要沒有全部出現，就不要用這個 skill。
這份目錄沒有任何配額錯誤的列；AKS 配額事故請交給
`aks-troubleshooting`。

## MCP 工具

不需要。使用 host 提供的唯讀 Azure 工具或 CLI 查詢。

## 流程

1. 擷取確切的錯誤碼、巢狀訊息、操作和 AKS 資源。
2. 每個限定條件都要有；錯誤碼不能只當子字串比對。
3. 給出成因、修法、引用和唯讀的驗證方式。
4. 說明跑了什麼；每一次變更之前都要有明確核准。

## 錯誤處理

| 輸入 | 處理 |
|---|---|
| 光禿禿的外層包裝／數字 | 要求提供巢狀簽章和 CSE 的 context |
| 一般 AKS 問題 | `aks-troubleshooting` |
| 非 AKS | 不使用 AKS skill |
