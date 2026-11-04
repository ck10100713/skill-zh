---
name: entra-app-registration
description: "引導完成 Microsoft Entra ID app registration、OAuth 2.0 驗證和 MSAL 整合。USE FOR: create app registration, register Azure AD app, configure OAuth, set up authentication, add API permissions, generate service principal, MSAL example, console app auth, Entra ID setup, Azure AD authentication. DO NOT USE FOR: Key Vault secrets (use azure-keyvault-expiration-audit), general Azure resource security guidance."
license: MIT
metadata:
  author: Microsoft
  version: "1.2.1"
---

## Overview

Microsoft Entra ID（前身是 Azure Active Directory）是 Microsoft 的雲端身分與存取管理服務。App registration 讓應用程式能驗證使用者，並安全地存取 Azure 資源。

### Key Concepts

| Concept | Description |
|---------|-------------|
| **App Registration** | 讓 app 能使用 Microsoft identity platform 的設定 |
| **Application (Client) ID** | 你的應用程式的唯一識別碼 |
| **Tenant ID** | 你的 Azure AD tenant/目錄的唯一識別碼 |
| **Client Secret** | 應用程式的密碼（只有 confidential client 才有） |
| **Redirect URI** | 驗證回應要送去的 URL |
| **API Permissions** | 你的 app 要求的存取範圍 |
| **Service Principal** | 註冊 app 時在你的 tenant 裡建立的身分 |

### Application Types

| Type | Use Case |
|------|----------|
| **Web Application** | 伺服器端 app、API |
| **Single Page App (SPA)** | JavaScript/React/Angular app |
| **Mobile/Native App** | 桌面、行動 app |
| **Daemon/Service** | 背景服務、API |

## Core Workflow

### Step 1: Register the Application

在 Azure portal 或用 Azure CLI 建立 app registration。

**Portal 做法：**
1. 前往 Azure Portal → Microsoft Entra ID → App registrations
2. 點「New registration」
3. 填入名稱、支援的帳戶類型和 redirect URI
4. 點「Register」

**CLI 做法：** 見 [references/cli-commands.md](references/cli-commands.md)
**IaC 做法：** 見 [references/BICEP-EXAMPLE.bicep](references/BICEP-EXAMPLE.bicep)

如果你的專案已經在用 IaC、需要能擴展的方式管理大量 app registration，或需要設定變更的細部稽核歷程，強烈建議用 IaC 來管理 Entra app registration。

### Step 2: Configure Authentication

依應用程式類型設定驗證。

- **Web Apps**：加入 redirect URI，需要的話啟用 ID token
- **SPAs**：加入 redirect URI，必要時啟用 implicit grant flow
- **Mobile/Desktop**：用 `http://localhost` 或自訂的 URI scheme
- **Services**：client credentials flow 不需要 redirect URI

### Step 3: Configure API Permissions

授予你的應用程式存取 Microsoft API 或你自己的 API 的權限。

**常見的 Microsoft Graph 權限：**
- `User.Read` - 讀取使用者個人資料
- `User.ReadWrite.All` - 讀寫所有使用者
- `Directory.Read.All` - 讀取目錄資料
- `Mail.Send` - 以使用者身分寄信

**詳細內容：** 見 [references/api-permissions.md](references/api-permissions.md)

### Step 4: Create Client Credentials (if needed)

confidential client 應用程式（web app、service）要建立 client secret、憑證或 federated identity credential。

**Client Secret：**
- 前往「Certificates & secrets」
- 建立新的 client secret
- 立刻複製它的值（只會顯示一次）
- 安全地保存（建議用 Key Vault）

**Certificate：** 正式環境請用憑證取代 secret，安全性更高。透過「Certificates & secrets」區塊上傳憑證。

**Federated Identity Credential：** 用於讓 confidential client 動態地向 Entra 平台驗證。

### Step 5: Implement OAuth Flow

把 OAuth flow 整合進你的應用程式程式碼。

**參考：**
- [references/oauth-flows.md](references/oauth-flows.md) - OAuth 2.0 flow 的細節
- [references/console-app-example.md](references/console-app-example.md) - Console app 實作

## Common Patterns

### Pattern 1: First-Time App Registration

一步一步帶使用者完成第一次的 app registration。

**需要的資訊：**
- 應用程式名稱
- 應用程式類型（web、SPA、mobile、service）
- Redirect URI（如果適用）
- 需要的權限

**Script：** 見 [references/first-app-registration.md](references/first-app-registration.md)

### Pattern 2: Console Application with User Authentication

建立一個會驗證使用者的 .NET/Python/Node.js console app。

**需要的資訊：**
- 程式語言（C#、Python、JavaScript 等）
- 驗證函式庫（建議用 MSAL）
- 需要的權限

**範例：** 見 [references/console-app-example.md](references/console-app-example.md)

### Pattern 3: Service-to-Service Authentication

設定不需要使用者互動的 daemon/service 驗證。

**需要的資訊：**
- Service/app 名稱
- 目標 API/資源
- 要用 secret 還是憑證

**實作：** 使用 Client Credentials flow（見 [references/oauth-flows.md#client-credentials-flow](references/oauth-flows.md#client-credentials-flow)）

## MCP Tools and CLI

### Azure CLI Commands

| Command | Purpose |
|---------|---------|
| `az ad app create` | 建立新的 app registration |
| `az ad app list` | 列出 app registration |
| `az ad app show` | 顯示 app 詳細資訊 |
| `az ad app permission add` | 新增 API 權限 |
| `az ad app credential reset` | 產生新的 client secret |
| `az ad sp create` | 建立 service principal |

**完整參考：** 見 [references/cli-commands.md](references/cli-commands.md)

### Microsoft Authentication Library (MSAL)

MSAL 是整合 Microsoft identity platform 的建議函式庫。

**支援的語言：**
- .NET/C# - `Microsoft.Identity.Client`
- JavaScript/TypeScript - `@azure/msal-browser`、`@azure/msal-node`
- Python - `msal`

**範例：** 見 [references/console-app-example.md](references/console-app-example.md)

## Security Best Practices

| Practice | Recommendation |
|----------|---------------|
| **Never hardcode secrets** | 用環境變數、Azure Key Vault 或 managed identity |
| **Rotate secrets regularly** | 設定到期時間，自動輪替 |
| **Use certificates over secrets** | 正式環境更安全 |
| **Least privilege permissions** | 只要求必要的 API 權限 |
| **Enable MFA** | 要求使用者使用多重要素驗證 |
| **Use managed identity** | Azure 上託管的 app 完全避開 secret |
| **Validate tokens** | 一定要驗證 issuer、audience、到期時間 |
| **Use HTTPS only** | 所有 redirect URI 都必須用 HTTPS（localhost 除外） |
| **Monitor sign-ins** | 用 Entra ID 的登入 log 偵測異常 |

## SDK Quick References

- **Azure Identity**: [Python](references/sdk/azure-identity-py.md) | [.NET](references/sdk/azure-identity-dotnet.md) | [TypeScript](references/sdk/azure-identity-ts.md) | [Java](references/sdk/azure-identity-java.md) | [Rust](references/sdk/azure-identity-rust.md)
- **Key Vault (secrets)**: [Python](references/sdk/azure-keyvault-py.md) | [TypeScript](references/sdk/azure-keyvault-secrets-ts.md)
- **Auth Events**: [.NET](references/sdk/microsoft-azure-webjobs-extensions-authentication-events-dotnet.md)

## References

- [OAuth Flows](references/oauth-flows.md) - OAuth 2.0 flow 的詳細說明
- [CLI Commands](references/cli-commands.md) - app registration 的 Azure CLI 參考
- [Console App Example](references/console-app-example.md) - 完整可運作的範例
- [First App Registration](references/first-app-registration.md) - 給初學者的逐步指南
- [API Permissions](references/api-permissions.md) - 了解並設定權限
- [Troubleshooting](references/troubleshooting.md) - 常見問題與解法

## External Resources

- [Microsoft Identity Platform Documentation](https://learn.microsoft.com/entra/identity-platform/)
- [OAuth 2.0 and OpenID Connect protocols](https://learn.microsoft.com/entra/identity-platform/v2-protocols)
- [MSAL Documentation](https://learn.microsoft.com/entra/msal/)
- [Microsoft Graph API](https://learn.microsoft.com/graph/)
