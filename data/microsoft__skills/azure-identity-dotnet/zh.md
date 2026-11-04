---
name: azure-identity-dotnet
description: |
  .NET 版 Azure Identity 函式庫。用 Microsoft Entra ID 為 Azure SDK client 做驗證的函式庫。用於 DefaultAzureCredential、managed identity、service principal 和開發者 credential。Triggers: "Azure Identity", "DefaultAzureCredential", "ManagedIdentityCredential", "ClientSecretCredential", "authentication .NET", "Azure auth", "credential chain".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.Identity
---

# .NET 版 Azure Identity 函式庫

用 Microsoft Entra ID 為 Azure SDK client 做驗證的函式庫。

## 安裝

```bash
dotnet add package Azure.Identity

# For ASP.NET Core integration
dotnet add package Microsoft.Extensions.Azure

# For brokered authentication and Visual Studio Code credential support
dotnet add package Azure.Identity.Broker
```

## 環境變數

### 使用 Secret 的 Service Principal

```bash
AZURE_CLIENT_ID=<application-client-id>
AZURE_TENANT_ID=<directory-tenant-id>
AZURE_CLIENT_SECRET=<client-secret-value>
```

### 使用憑證的 Service Principal

```bash
AZURE_CLIENT_ID=<application-client-id>
AZURE_TENANT_ID=<directory-tenant-id>
AZURE_CLIENT_CERTIFICATE_PATH=<path-to-pfx-or-pem>
AZURE_CLIENT_CERTIFICATE_PASSWORD=<certificate-password>  # 選填
```

### Managed Identity

```bash
AZURE_CLIENT_ID=<user-assigned-managed-identity-client-id>  # 只有 user-assigned 才需要
```

## DefaultAzureCredential

大多數情境建議用的 credential。它會依序嘗試多種驗證方式。目前的 credential chain 順序和預設值，請看 [DefaultAzureCredential 概觀](https://aka.ms/azsdk/net/identity/credential-chains#defaultazurecredential-overview)。

### 基本用法

```csharp
using Azure.Identity;
using Azure.Storage.Blobs;

var credential = new DefaultAzureCredential();
var blobClient = new BlobServiceClient(
    new Uri("https://myaccount.blob.core.windows.net"),
    credential);
```

### 搭配 Dependency Injection 的 ASP.NET Core

```csharp
using Azure.Identity;
using Microsoft.Extensions.Azure;

builder.Services.AddAzureClients(clientBuilder =>
{
    clientBuilder.AddBlobServiceClient(
        new Uri("https://myaccount.blob.core.windows.net"));
    clientBuilder.AddSecretClient(
        new Uri("https://myvault.vault.azure.net"));
    
    // 預設使用 DefaultAzureCredential
    clientBuilder.UseCredential(new DefaultAzureCredential());
});
```

### 自訂 DefaultAzureCredential

```csharp
var credential = new DefaultAzureCredential(
    new DefaultAzureCredentialOptions
    {
        ExcludeEnvironmentCredential = true,
        ExcludeManagedIdentityCredential = false,
        ExcludeVisualStudioCredential = false,
        ExcludeAzureCliCredential = false,
        ExcludeInteractiveBrowserCredential = false, // 啟用互動式
        TenantId = "<tenant-id>",
        ManagedIdentityClientId = "<user-assigned-mi-client-id>"
    });
```

## Credential 類型

### ManagedIdentityCredential（正式環境）

```csharp
// System-assigned managed identity
var credential = new ManagedIdentityCredential(ManagedIdentityId.SystemAssigned);

// 用 client ID 指定 user-assigned
var credential = new ManagedIdentityCredential(
    ManagedIdentityId.FromUserAssignedClientId("<client-id>"));

// 用 resource ID 指定 user-assigned
var credential = new ManagedIdentityCredential(
    ManagedIdentityId.FromUserAssignedResourceId("<resource-id>"));

// 用 object ID 指定 user-assigned
var credential = new ManagedIdentityCredential(
    ManagedIdentityId.FromUserAssignedObjectId("<object-id>"));
```

### ClientSecretCredential

```csharp
var credential = new ClientSecretCredential(
    tenantId: "<tenant-id>",
    clientId: "<client-id>",
    clientSecret: "<client-secret>");

var client = new SecretClient(
    new Uri("https://myvault.vault.azure.net"),
    credential);
```

### ClientCertificateCredential

```csharp
var certificate = X509CertificateLoader.LoadCertificateFromFile("MyCertificate.pfx");
var credential = new ClientCertificateCredential(
    tenantId: "<tenant-id>",
    clientId: "<client-id>",
    certificate);
```

### ChainedTokenCredential（自訂 Chain）

```csharp
var credential = new ChainedTokenCredential(
    new ManagedIdentityCredential(),
    new AzureCliCredential());

var client = new SecretClient(
    new Uri("https://myvault.vault.azure.net"),
    credential);
```

### 開發者 Credential

```csharp
// Azure CLI
var credential = new AzureCliCredential();

// Azure PowerShell
var credential = new AzurePowerShellCredential();

// Azure Developer CLI (azd)
var credential = new AzureDeveloperCliCredential();

// Visual Studio
var credential = new VisualStudioCredential();

// Interactive Browser
var credential = new InteractiveBrowserCredential();
```

## 依環境設定

```csharp
// 正式環境 vs 開發環境
TokenCredential credential = builder.Environment.IsProduction()
    ? new ManagedIdentityCredential("<client-id>")
    : new DefaultAzureCredential();
```

## 主權雲端

```csharp
var credential = new DefaultAzureCredential(
    new DefaultAzureCredentialOptions
    {
        AuthorityHost = AzureAuthorityHosts.AzureGovernment
    });

// 可用的 authority host：
// AzureAuthorityHosts.AzurePublicCloud (default)
// AzureAuthorityHosts.AzureGovernment
// AzureAuthorityHosts.AzureChina
```

## Credential 類型參考

| 分類 | Credential | 用途 |
|----------|------------|---------|
| **Chain** | `DefaultAzureCredential` | 預先設定好的 chain，從開發一路用到正式 |
| | `ChainedTokenCredential` | 自訂 credential chain |
| **Azure 託管** | `ManagedIdentityCredential` | Azure managed identity |
| | `WorkloadIdentityCredential` | Kubernetes workload identity |
| | `EnvironmentCredential` | 環境變數 |
| **Service Principal** | `ClientSecretCredential` | Client ID + secret |
| | `ClientCertificateCredential` | Client ID + 憑證 |
| | `ClientAssertionCredential` | 簽署過的 client assertion |
| **使用者** | `InteractiveBrowserCredential` | 透過瀏覽器驗證 |
| | `DeviceCodeCredential` | Device code 流程 |
| | `OnBehalfOfCredential` | 委派身分 |
| **開發者** | `AzureCliCredential` | Azure CLI |
| | `AzurePowerShellCredential` | Azure PowerShell |
| | `AzureDeveloperCliCredential` | Azure Developer CLI |
| | `VisualStudioCredential` | Visual Studio |

## 最佳實務

### 1. 正式環境用確定性的 Credential

```csharp
// 開發
var devCredential = new DefaultAzureCredential();

// 正式環境：用特定的 credential
var prodCredential = new ManagedIdentityCredential(
    ManagedIdentityId.FromUserAssignedClientId("<client-id>"));
```

### 2. 重複使用 Credential 實例

```csharp
// 好的做法：單一 credential 實例在各 client 之間共用
var credential = new DefaultAzureCredential();
var blobClient = new BlobServiceClient(blobUri, credential);
var secretClient = new SecretClient(vaultUri, credential);
```

### 3. 設定重試 Policy

```csharp
var options = new ManagedIdentityCredentialOptions(
    ManagedIdentityId.FromUserAssignedClientId(clientId))
{
    Retry =
    {
        MaxRetries = 3,
        Delay = TimeSpan.FromSeconds(0.5),
    }
};
var credential = new ManagedIdentityCredential(options);
```

### 4. 除錯時啟用 Logging

```csharp
using Azure.Core.Diagnostics;

using AzureEventSourceListener listener = new((args, message) =>
{
    if (args is { EventSource.Name: "Azure-Identity" })
    {
        Console.WriteLine(message);
    }
}, EventLevel.LogAlways);
```

## 錯誤處理

```csharp
using Azure.Identity;
using Azure.Security.KeyVault.Secrets;

var client = new SecretClient(
    new Uri("https://myvault.vault.azure.net"),
    new DefaultAzureCredential());

try
{
    KeyVaultSecret secret = await client.GetSecretAsync("secret1");
}
catch (AuthenticationFailedException e)
{
    Console.WriteLine($"Authentication Failed: {e.Message}");
}
catch (CredentialUnavailableException e)
{
    Console.WriteLine($"Credential Unavailable: {e.Message}");
}
```

## 主要 Exception

| Exception | 說明 |
|-----------|-------------|
| `AuthenticationFailedException` | 驗證錯誤的基底 exception |
| `CredentialUnavailableException` | Credential 在目前環境無法驗證 |
| `AuthenticationRequiredException` | 需要互動式驗證 |

## Managed Identity 支援

支援的 Azure 服務：
- Azure App Service 和 Azure Functions
- Azure Arc
- Azure Cloud Shell
- Azure Kubernetes Service (AKS)
- Azure Service Fabric
- Azure Virtual Machines
- Azure Virtual Machine Scale Sets

## Thread Safety

所有 credential 實作都是 thread-safe 的。單一 credential 實例可以安全地在多個 client 和 thread 之間共用。

## 相關套件

| 套件                         | 用途                          | 安裝                                            |
|------------------------------|-------------------------------|-------------------------------------------------|
| `Azure.Identity`             | 驗證（本函式庫）              | `dotnet add package Azure.Identity`             |
| `Microsoft.Extensions.Azure` | DI 整合                       | `dotnet add package Microsoft.Extensions.Azure` |
| `Azure.Identity.Broker`      | Brokered 驗證                 | `dotnet add package Azure.Identity.Broker`      |

## 參考連結

| 資源 | URL |
|----------|-----|
| NuGet Package | https://www.nuget.org/packages/Azure.Identity |
| API Reference | https://learn.microsoft.com/dotnet/api/azure.identity |
| Credential Chains | https://aka.ms/azsdk/net/identity/credential-chains |
| Best Practices | https://learn.microsoft.com/dotnet/azure/sdk/authentication/best-practices |
| GitHub Source | https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/identity/Azure.Identity |
