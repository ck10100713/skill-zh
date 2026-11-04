---
name: azure-identity-java
description: 用於 Java 對 Azure 服務做驗證的 Azure Identity 函式庫。在 Java 應用程式中實作 DefaultAzureCredential、managed identity、service principal 或任何 Azure 驗證模式時使用。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: com.azure:azure-identity
---

# Java 版 Azure Identity 函式庫

用 Microsoft Entra ID 為 Azure SDK client 做驗證的函式庫。

## 安裝

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-identity</artifactId>
    <version>1.15.0</version>
</dependency>
```

## 關鍵概念

| Credential | 使用情境 |
|------------|----------|
| `DefaultAzureCredential` | **建議**：開發和正式環境都能用 |
| `ManagedIdentityCredential` | 託管在 Azure 的應用程式（App Service、Functions、VM） |
| `EnvironmentCredential` | 用環境變數的 CI/CD pipeline |
| `ClientSecretCredential` | 使用 secret 的 service principal |
| `ClientCertificateCredential` | 使用憑證的 service principal |
| `AzureCliCredential` | 本機開發，用 `az login` |
| `InteractiveBrowserCredential` | 互動式登入流程 |
| `DeviceCodeCredential` | 無頭裝置的驗證 |

## DefaultAzureCredential（建議）

`DefaultAzureCredential` 會依序嘗試多種驗證方式。目前的 credential chain 順序和預設值，請看 [DefaultAzureCredential 概觀](https://aka.ms/azsdk/java/identity/credential-chains#defaultazurecredential-overview)。

```java
import com.azure.identity.DefaultAzureCredential;
import com.azure.identity.DefaultAzureCredentialBuilder;

// 簡單用法
DefaultAzureCredential credential = new DefaultAzureCredentialBuilder().build();

// 搭配任何 Azure client 使用
BlobServiceClient blobClient = new BlobServiceClientBuilder()
    .endpoint("https://<storage-account>.blob.core.windows.net")
    .credential(credential)
    .buildClient();

KeyClient keyClient = new KeyClientBuilder()
    .vaultUrl("https://<vault-name>.vault.azure.net")
    .credential(credential)
    .buildClient();
```

### 設定 DefaultAzureCredential

```java
DefaultAzureCredential credential = new DefaultAzureCredentialBuilder()
    .managedIdentityClientId("<user-assigned-identity-client-id>")  // user-assigned MI 用
    .tenantId("<tenant-id>")                                        // 限定特定 tenant
    .excludeEnvironmentCredential()                                 // 跳過環境變數
    .excludeAzureCliCredential()                                    // 跳過 Azure CLI
    .build();
```

## Managed Identity

給託管在 Azure 的應用程式用（App Service、Functions、AKS、VM）。

```java
import com.azure.identity.ManagedIdentityCredential;
import com.azure.identity.ManagedIdentityCredentialBuilder;

// System-assigned managed identity
ManagedIdentityCredential credential = new ManagedIdentityCredentialBuilder()
    .build();

// User-assigned managed identity（用 client ID）
ManagedIdentityCredential credential = new ManagedIdentityCredentialBuilder()
    .clientId("<user-assigned-client-id>")
    .build();

// User-assigned managed identity（用 resource ID）
ManagedIdentityCredential credential = new ManagedIdentityCredentialBuilder()
    .resourceId("/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.ManagedIdentity/userAssignedIdentities/<name>")
    .build();
```

## 使用 Secret 的 Service Principal

```java
import com.azure.identity.ClientSecretCredential;
import com.azure.identity.ClientSecretCredentialBuilder;

ClientSecretCredential credential = new ClientSecretCredentialBuilder()
    .tenantId("<tenant-id>")
    .clientId("<client-id>")
    .clientSecret("<client-secret>")
    .build();
```

## 使用憑證的 Service Principal

```java
import com.azure.identity.ClientCertificateCredential;
import com.azure.identity.ClientCertificateCredentialBuilder;

// 從 PEM 檔
ClientCertificateCredential credential = new ClientCertificateCredentialBuilder()
    .tenantId("<tenant-id>")
    .clientId("<client-id>")
    .pemCertificate("<path-to-cert.pem>")
    .build();

// 從有密碼的 PFX 檔
ClientCertificateCredential credential = new ClientCertificateCredentialBuilder()
    .tenantId("<tenant-id>")
    .clientId("<client-id>")
    .pfxCertificate("<path-to-cert.pfx>", "<pfx-password>")
    .build();

// 為了 SNI 送出憑證鏈
ClientCertificateCredential credential = new ClientCertificateCredentialBuilder()
    .tenantId("<tenant-id>")
    .clientId("<client-id>")
    .pemCertificate("<path-to-cert.pem>")
    .sendCertificateChain(true)
    .build();
```

## Environment Credential

從環境變數讀取憑證。

```java
import com.azure.identity.EnvironmentCredential;
import com.azure.identity.EnvironmentCredentialBuilder;

EnvironmentCredential credential = new EnvironmentCredentialBuilder().build();
```

### 必要的環境變數

**使用 secret 的 service principal：**

```bash
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<client-id>
AZURE_CLIENT_SECRET=<client-secret>
```

**使用憑證的 service principal：**

```bash
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<client-id>
AZURE_CLIENT_CERTIFICATE_PATH=/path/to/cert.pem
AZURE_CLIENT_CERTIFICATE_PASSWORD=<optional-password>
```

## Azure CLI Credential

給本機開發用，透過 `az login`。

```java
import com.azure.identity.AzureCliCredential;
import com.azure.identity.AzureCliCredentialBuilder;

AzureCliCredential credential = new AzureCliCredentialBuilder()
    .tenantId("<tenant-id>")  // 選填：指定 tenant
    .build();
```

## Interactive Browser

給需要使用者登入的桌面應用程式用。

```java
import com.azure.identity.InteractiveBrowserCredential;
import com.azure.identity.InteractiveBrowserCredentialBuilder;

InteractiveBrowserCredential credential = new InteractiveBrowserCredentialBuilder()
    .clientId("<client-id>")
    .redirectUrl("http://localhost:8080")  // 必須跟 app registration 一致
    .build();
```

## Device Code

給無頭裝置用（IoT、CLI 工具）。

```java
import com.azure.identity.DeviceCodeCredential;
import com.azure.identity.DeviceCodeCredentialBuilder;

DeviceCodeCredential credential = new DeviceCodeCredentialBuilder()
    .clientId("<client-id>")
    .challengeConsumer(challenge -> {
        // 顯示給使用者
        System.out.println(challenge.getMessage());
    })
    .build();
```

## Chained Credential

建立自訂的驗證 chain。

```java
import com.azure.identity.ChainedTokenCredential;
import com.azure.identity.ChainedTokenCredentialBuilder;

ChainedTokenCredential credential = new ChainedTokenCredentialBuilder()
    .addFirst(new ManagedIdentityCredentialBuilder().build())
    .addLast(new AzureCliCredentialBuilder().build())
    .build();
```

## Workload Identity (AKS)

給有 workload identity 的 Azure Kubernetes Service 用。

```java
import com.azure.identity.WorkloadIdentityCredential;
import com.azure.identity.WorkloadIdentityCredentialBuilder;

// 從 AZURE_TENANT_ID、AZURE_CLIENT_ID、AZURE_FEDERATED_TOKEN_FILE 讀取
WorkloadIdentityCredential credential = new WorkloadIdentityCredentialBuilder().build();

// 或明確設定
WorkloadIdentityCredential credential = new WorkloadIdentityCredentialBuilder()
    .tenantId("<tenant-id>")
    .clientId("<client-id>")
    .tokenFilePath("/var/run/secrets/azure/tokens/azure-identity-token")
    .build();
```

## Token 快取

啟用持久的 token 快取來改善效能。

```java
// 啟用 token 快取（預設在記憶體內）
DefaultAzureCredential credential = new DefaultAzureCredentialBuilder()
    .enableAccountIdentifierLogging()
    .build();

// 搭配共用的 token 快取（多個 credential 的情境）
SharedTokenCacheCredential credential = new SharedTokenCacheCredentialBuilder()
    .clientId("<client-id>")
    .build();
```

## 主權雲端

```java
import com.azure.identity.AzureAuthorityHosts;

// Azure Government
DefaultAzureCredential govCredential = new DefaultAzureCredentialBuilder()
    .authorityHost(AzureAuthorityHosts.AZURE_GOVERNMENT)
    .build();

// Azure China
DefaultAzureCredential chinaCredential = new DefaultAzureCredentialBuilder()
    .authorityHost(AzureAuthorityHosts.AZURE_CHINA)
    .build();
```

## 錯誤處理

```java
import com.azure.identity.CredentialUnavailableException;
import com.azure.core.exception.ClientAuthenticationException;

try {
    DefaultAzureCredential credential = new DefaultAzureCredentialBuilder().build();
    AccessToken token = credential.getToken(new TokenRequestContext()
        .addScopes("https://management.azure.com/.default"));
} catch (CredentialUnavailableException e) {
    // 沒有任何 credential 能驗證
    System.out.println("Authentication failed: " + e.getMessage());
} catch (ClientAuthenticationException e) {
    // 驗證錯誤（憑證錯誤、過期等等）
    System.out.println("Auth error: " + e.getMessage());
}
```

## Logging

啟用驗證 logging 來除錯。

```java
// 用環境變數
// AZURE_LOG_LEVEL=verbose

// 或用程式設定
DefaultAzureCredential credential = new DefaultAzureCredentialBuilder()
    .enableAccountIdentifierLogging()  // 記錄帳號資訊
    .build();
```

## 環境變數

```bash
# DefaultAzureCredential configuration
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<client-id>
AZURE_CLIENT_SECRET=<client-secret>

# Managed Identity
AZURE_CLIENT_ID=<user-assigned-mi-client-id>

# Workload Identity (AKS)
AZURE_FEDERATED_TOKEN_FILE=/var/run/secrets/azure/tokens/azure-identity-token

# Logging
AZURE_LOG_LEVEL=verbose

# Authority host
AZURE_AUTHORITY_HOST=https://login.microsoftonline.com/
```

## 最佳實務

1. **用 DefaultAzureCredential**：從開發到正式環境都能順暢運作
2. **正式環境用 Managed Identity**：不用管 secret，會自動輪替
3. **本機開發用 Azure CLI**：跑 app 之前先 `az login`
4. **最小權限**：只授予 service principal 需要的權限
5. **Token 快取**：預設啟用，能減少驗證的往返
6. **環境變數**：用在 CI/CD，不要把 secret 寫死

## Credential 選擇矩陣

| 環境 | 建議的 Credential |
|-------------|----------------------|
| 本機開發 | `DefaultAzureCredential`（會用 Azure CLI） |
| Azure App Service | `DefaultAzureCredential`（會用 Managed Identity） |
| Azure Functions | `DefaultAzureCredential`（會用 Managed Identity） |
| Azure Kubernetes Service | `WorkloadIdentityCredential` |
| Azure VM | `DefaultAzureCredential`（會用 Managed Identity） |
| CI/CD Pipeline | `EnvironmentCredential` |
| 桌面 App | `InteractiveBrowserCredential` |
| CLI 工具 | `DeviceCodeCredential` |

## 觸發詞

- "Azure authentication Java", "DefaultAzureCredential Java"
- "managed identity Java", "service principal Java"
- "Azure login Java", "Azure credentials Java"
- "AZURE_CLIENT_ID", "AZURE_TENANT_ID"
