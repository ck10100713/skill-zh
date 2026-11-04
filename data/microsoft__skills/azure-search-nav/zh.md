---
name: azure-search-nav
description: "用 aks-search-direct-mid 語意搜尋 API，為支援的 Microsoft.ContainerService、Microsoft.Kubernetes 和 Microsoft.Compute 資源，產生直達特定 blade／選單項目的 Azure portal 連結。WHEN: 'find where in the Azure portal to do something', 'search the portal for an operation', 'construct a portal link from a search query and a resource'."
license: MIT
metadata:
  author: Microsoft
  version: "1.0.1"
---

# Azure Portal 搜尋連結產生器

## 快速參考

| 項目 | 值 |
|------|-------|
| Script | [`references/Invoke-PortalSearchNav.ps1`](references/Invoke-PortalSearchNav.ps1) |
| 資源對照表 | [`references/resource-types.json`](references/resource-types.json) |
| 前置需求 | `Az.Accounts` PowerShell module |
| 驗證 | 互動式 Microsoft 登入（`Connect-AzAccount`），或搭配 `-UseDeviceAuthentication` 用 device code |

## 何時使用這個 Skill

- 使用者想知道，要對支援的 Container Service、Arc-enabled Kubernetes 或 Compute 資源做某個操作，該去 Azure portal 的哪裡。
- 使用者想要直達特定 blade／選單項目的 portal 連結。
- 使用者提供資源 URL 或 ARM resource ID，加上一段自然語言的搜尋 query。

## 工作流程

1. 向使用者收集**資源連結**（portal URL 或單純的 ARM resource ID）和**搜尋 query**。
2. 執行 `references/Invoke-PortalSearchNav.ps1 -ResourceUrl '<link>' -Query '<query>'`。
3. Script 會登入（預設開瀏覽器；在 headless／CLI 環境要加 `-UseDeviceAuthentication`）、呼叫搜尋 API，然後印出一律以 `https://portal.azure.com` 開頭的 portal 連結。

完整的參數說明和 API 細節請看 [references/README.md](references/README.md)。

## 錯誤處理

| 錯誤 | 原因 | 修正 |
|-------|-------|-----|
| Resource type not enabled | `armProvider` 不在 `references/resource-types.json` 裡 | 確認這個類型在已啟用的 provider 清單內 |
| API 回 401 | token 無效，或選錯 tenant | 重跑一次，選有權限存取目標 subscription 所屬 tenant 的帳號 |
| 結果是空的 | 沒有符合 query 的導覽項目 | 換個搜尋詞試試 |
| 找不到 `Az.Accounts` | 沒裝這個 module | `Install-Module Az.Accounts -Scope CurrentUser` |
| 瀏覽器登入失敗（no window handle） | Headless／CLI 環境 | 加上 `-UseDeviceAuthentication` 重跑 |
