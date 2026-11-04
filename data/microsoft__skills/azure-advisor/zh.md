---
name: azure-advisor
description: "使用 Azure Advisor 的建議。WHEN: \"show Advisor recommendations\", \"service retirements\", \"update recommendation status\"。不要用在：修復或補救（用 azure-advisor-actionability）。"
license: MIT
metadata:
  author: Microsoft
  version: "1.0.1"
---

# Azure Advisor

## 速查

優先用 Azure Advisor MCP 工具，不要用 Resource Graph 或一般的 ARM 工具。

| 意圖 | 工具 |
|---|---|
| 數量、分類統計、排名或前幾大類型 | `advisor_recommendation_summary` |
| 個別建議或受影響的資源 | `advisor_recommendation_list` |
| 完成、忽略、延後或重新啟用 | `advisor_recommendation_update` |
| 瀏覽建議類型 | `advisor_metadata_list` |
| 用 ID 取得單一類型 | `advisor_metadata_get` |
| 取得修復方式 | `advisor_remediation_get`，然後 `azure-advisor-actionability` |

## 流程

1. 確認 subscription 或 service group 的範圍。Resource group 範圍需要指定 subscription。
2. 重複使用已知的範圍和識別碼，只問缺少的值。
3. 彙總用 `summary`，逐筆紀錄用 `list`。絕對不要去數一份被截斷上限的 list。
4. 只呈現回傳的資料，包括截斷、存取限制和錯誤。

要修復單一建議的請求，導向 `azure-advisor-actionability` skill。其他情況就從表格挑工具，服務汰除（service retirements）也用 `summary` 或 `list`。

## 安全

更新建議狀態之前要先確認。修復的安全防護由 actionability skill 負責。
