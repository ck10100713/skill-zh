---
name: azure-advisor-actionability
description: "修復 Azure Advisor 的建議。WHEN: \"fix Advisor recommendation\"。"
license: MIT
metadata:
  author: Microsoft
  version: "1.0.1"
---

# Azure Advisor 可執行修復

## 速查

把修復方式呈現給客戶自己執行；沒有明確確認絕對不要執行。需要 `recommendationTypeId` GUID 和完整的受影響 `resourceId`；已知的值就重複使用，缺的就問，絕對不要猜。

`resourceId` 從使用者那邊取得，或從 `advisor_recommendation_list` 回傳的受影響資源紀錄中精確取得。有歧義就問是哪個資源；絕對不要使用建議的 instance ID。

## 流程

1. 只用 `recommendationTypeId` 呼叫一次 `advisor_remediation_get`，絕對不要帶 `resourceId`，之後才產生指引或代入數值。
2. 遇到 `RemediationNotFound`、空回應或沒有可用的修復方式時，說明 Advisor 的修復方式不可用。去取得相關的公開 Microsoft Learn 文件；如果不知道是什麼建議，就請使用者提供建議說明。如果都找不到，就直說；絕對不要編造指引。其他工具錯誤要回報，但不要透露內部細節，也不要當作空結果。
3. 只使用回傳的修復方式或取得的 Learn 指引，包括警告和驗證步驟。
4. 取得之後，從確切的受影響 `resourceId` 或已確認的 context 代入沒有歧義的佔位符：subscription、resource group、資源名稱、完整的 resource ID。無法解析的佔位符要保留並說明。
5. 保留步驟順序；Azure CLI 和 PowerShell 分開寫。

遇到 Advisor 的 `guidance` 就不要產生指令。遇到 `hybrid` 或 `executable`，要包含每一個手動、決策和指令步驟。省略原始 JSON 和內部標籤。

## 最終回應

標明來源：「Guidance source: Azure Advisor remediation tool」或「Guidance source: publicly available Microsoft Learn documentation」，並附上取得的 `learn.microsoft.com` 引用。絕對不要把備援指引說成來自 Advisor，也不要宣稱已經執行。
