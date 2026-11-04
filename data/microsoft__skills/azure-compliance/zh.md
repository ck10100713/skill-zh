---
name: azure-compliance
description: "用 azqr 加上 Key Vault 到期檢查來執行 Azure 合規與安全稽核。涵蓋 best practice 評估、資源檢視、policy/合規驗證和安全態勢檢查。WHEN: compliance scan, security audit, BEFORE running azqr (compliance cli tool), Azure best practices, Key Vault expiration check, expired certificates, expiring secrets, orphaned resources, compliance assessment."
license: MIT
metadata:
  author: Microsoft
  version: "1.2.3"
---

# Azure Compliance & Security Auditing

## Quick Reference

| Property | Details |
|---|---|
| Best for | 合規掃描、安全稽核、Key Vault 到期檢查 |
| Primary capabilities | 全面資源評估、Key Vault 到期監控 |
| MCP tools | azqr、subscription 和 resource group 列表、Key Vault 項目檢視 |

## Prerequisites

- 驗證：使用者已用 `az login` 登入 Azure
- 具備讀取資源設定和 Key Vault metadata 的權限

## Assessments

| Assessment | Reference |
|------------|-----------|
| 全面合規（azqr） | [references/azure-quick-review.md](references/azure-quick-review.md) |
| Key Vault 到期 | [references/azure-keyvault-expiration-audit.md](references/azure-keyvault-expiration-audit.md) |
| Resource Graph 查詢 | [references/azure-resource-graph.md](references/azure-resource-graph.md) |

## MCP Tools

| Tool | Purpose |
|------|---------|
| `mcp_azure_mcp_extension_azqr` | 執行 azqr 合規掃描 |
| `mcp_azure_mcp_subscription_list` | 列出可用的 subscription |
| `mcp_azure_mcp_group_list` | 列出 resource group |
| `keyvault_key_list` | 列出 vault 裡所有的 key |
| `keyvault_key_get` | 取得 key 細節，包含到期時間 |
| `keyvault_secret_list` | 列出 vault 裡所有的 secret |
| `keyvault_secret_get` | 取得 secret 細節，包含到期時間 |
| `keyvault_certificate_list` | 列出 vault 裡所有的憑證 |
| `keyvault_certificate_get` | 取得憑證細節，包含到期時間 |

## Assessment Workflow

1. 為全面資源評估選定範圍（subscription 或 resource group）。
2. 執行 azqr 並擷取輸出的 artifact。
3. 分析掃描結果，整理發現的問題和建議。
4. 檢視 Key Vault 到期監控的輸出，包含 key、secret 和憑證。
5. 為問題分類，並針對每個發現提出修復或解決步驟。

### Priority Classification

| Priority | Guidance |
|---|---|
| Critical | 高影響的暴露風險，需要立即修復 |
| High | 在幾天內解決以降低風險 |
| Medium | 排進下個 sprint 解決 |
| Low | 追蹤並在例行維護時修復 |

## Error Handling

| Error | Message | Remediation |
|---|---|---|
| 需要驗證 | "Please login" | 執行 `az login` 後重試 |
| 存取被拒 | "Forbidden" | 確認權限並修正角色指派 |
| 找不到資源 | "Not found" | 確認 subscription 和 resource group 的選擇 |

## Best Practices

- 定期執行合規掃描（每週或每月）
- 長期追蹤發現的問題，並確認修復有效
- 把合規報告和修復執行分開
- 把 Key Vault 的到期政策寫成文件並確實執行

## SDK Quick References

要用程式存取 Key Vault，請看精簡版 SDK 指南：

- **Key Vault (Python)**: [Secrets/Keys/Certs](references/sdk/azure-keyvault-py.md)
- **Secrets**: [TypeScript](references/sdk/azure-keyvault-secrets-ts.md) | [Rust](references/sdk/azure-keyvault-secrets-rust.md) | [Java](references/sdk/azure-security-keyvault-secrets-java.md)
- **Keys**: [.NET](references/sdk/azure-security-keyvault-keys-dotnet.md) | [Java](references/sdk/azure-security-keyvault-keys-java.md) | [TypeScript](references/sdk/azure-keyvault-keys-ts.md) | [Rust](references/sdk/azure-keyvault-keys-rust.md)
- **Certificates**: [Rust](references/sdk/azure-keyvault-certificates-rust.md)

