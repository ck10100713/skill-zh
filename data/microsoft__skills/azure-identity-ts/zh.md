---
name: azure-identity-ts
description: 用 JavaScript 版 Azure Identity 函式庫（@azure/identity）對 Azure 服務做驗證。設定 DefaultAzureCredential、managed identity、service principal 或互動式瀏覽器登入的驗證時使用。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: '@azure/identity'
---

# TypeScript 版 Azure Identity 函式庫

用 Microsoft Entra ID 為 Azure SDK client 做驗證的函式庫。

## 安裝

```bash
npm install @azure/identity

# For Visual Studio Code credential support
npm install @azure/identity-vscode
```

## 環境變數

### Service Principal（Secret）

```bash
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<client-id>
AZURE_CLIENT_SECRET=<client-secret>
AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境使用 DefaultAzureCredential 時才需要
```

### Service Principal（憑證）

```bash
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<client-id>
AZURE_CLIENT_CERTIFICATE_PATH=/path/to/cert.pem
AZURE_CLIENT_CERTIFICATE_PASSWORD=<optional-password>
```

### Workload Identity（Kubernetes）

```bash
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<client-id>
AZURE_FEDERATED_TOKEN_FILE=/var/run/secrets/tokens/azure-identity
```

## DefaultAzureCredential（本機開發建議用）

```typescript
import { DefaultAzureCredential, ManagedIdentityCredential } from "@azure/identity";

// 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
const credential = new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]});
// 或是在正式環境直接用特定的 credential：
// 參考 https://learn.microsoft.com/javascript/api/overview/azure/identity-readme?view=azure-node-latest#credential-classes
// const credential = new ManagedIdentityCredential();

// 搭配任何 Azure SDK client 使用
import { BlobServiceClient } from "@azure/storage-blob";
const blobClient = new BlobServiceClient(
  "https://<account>.blob.core.windows.net",
  credential
);
```

目前的 credential chain 順序和預設值，請看 [DefaultAzureCredential 概觀](https://aka.ms/azsdk/js/identity/credential-chains#defaultazurecredential-overview)。

## Managed Identity

### System-Assigned

```typescript
import { ManagedIdentityCredential } from "@azure/identity";

const credential = new ManagedIdentityCredential();
```

### User-Assigned（用 Client ID）

```typescript
const credential = new ManagedIdentityCredential({
  clientId: "<user-assigned-client-id>"
});
```

### User-Assigned（用 Resource ID）

```typescript
const credential = new ManagedIdentityCredential({
  resourceId: "/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.ManagedIdentity/userAssignedIdentities/<name>"
});
```

### User-Assigned（用 Object ID）

```typescript
const credential = new ManagedIdentityCredential({
  objectId: "<user-assigned-object-id>"
});
```

## Service Principal

### Client Secret

```typescript
import { ClientSecretCredential } from "@azure/identity";

const credential = new ClientSecretCredential(
  "<tenant-id>",
  "<client-id>",
  "<client-secret>"
);
```

### Client Certificate

```typescript
import { ClientCertificateCredential } from "@azure/identity";

const credential = new ClientCertificateCredential(
  "<tenant-id>",
  "<client-id>",
  { certificatePath: "/path/to/cert.pem" }
);

// 帶密碼
const credentialWithPwd = new ClientCertificateCredential(
  "<tenant-id>",
  "<client-id>",
  { 
    certificatePath: "/path/to/cert.pem",
    certificatePassword: "<password>"
  }
);
```

## 互動式驗證

### 瀏覽器登入

```typescript
import { InteractiveBrowserCredential } from "@azure/identity";

const credential = new InteractiveBrowserCredential({
  clientId: "<client-id>",
  tenantId: "<tenant-id>",
  loginHint: "user@example.com"
});
```

### Device Code 流程

```typescript
import { DeviceCodeCredential } from "@azure/identity";

const credential = new DeviceCodeCredential({
  clientId: "<client-id>",
  tenantId: "<tenant-id>",
  userPromptCallback: (info) => {
    console.log(info.message);
    // "To sign in, use a web browser to open..."
  }
});
```

## 自訂 Credential Chain

```typescript
import { 
  ChainedTokenCredential,
  ManagedIdentityCredential,
  AzureCliCredential
} from "@azure/identity";

// 先試 managed identity，失敗再退回 CLI
const credential = new ChainedTokenCredential(
  new ManagedIdentityCredential(),
  new AzureCliCredential()
);
```

## 開發者 Credential

### Visual Studio Code

```typescript
import { useIdentityPlugin, VisualStudioCodeCredential } from "@azure/identity";
import { vsCodePlugin } from "@azure/identity-vscode";

useIdentityPlugin(vsCodePlugin);

const credential = new VisualStudioCodeCredential();
```

### Azure CLI

```typescript
import { AzureCliCredential } from "@azure/identity";

const credential = new AzureCliCredential();
// 用的是：az login
```

### Azure Developer CLI

```typescript
import { AzureDeveloperCliCredential } from "@azure/identity";

const credential = new AzureDeveloperCliCredential();
// 用的是：azd auth login
```

### Azure PowerShell

```typescript
import { AzurePowerShellCredential } from "@azure/identity";

const credential = new AzurePowerShellCredential();
// 用的是：Connect-AzAccount
```

## 主權雲端

```typescript
import { ClientSecretCredential, AzureAuthorityHosts } from "@azure/identity";

// Azure Government
const credential = new ClientSecretCredential(
  "<tenant>", "<client>", "<secret>",
  { authorityHost: AzureAuthorityHosts.AzureGovernment }
);

// Azure China
const credentialChina = new ClientSecretCredential(
  "<tenant>", "<client>", "<secret>",
  { authorityHost: AzureAuthorityHosts.AzureChina }
);
```

## Bearer Token Provider

```typescript
import { DefaultAzureCredential, getBearerTokenProvider } from "@azure/identity";

const credential = new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]});

// 建立一個會回傳 token 的函式
const getAccessToken = getBearerTokenProvider(
  credential,
  "https://cognitiveservices.azure.com/.default"
);

// 搭配需要 bearer token 的 API 使用
const token = await getAccessToken();
```

## 主要型別

```typescript
import type { 
  TokenCredential, 
  AccessToken, 
  GetTokenOptions 
} from "@azure/core-auth";

import {
  DefaultAzureCredential,
  DefaultAzureCredentialOptions,
  ManagedIdentityCredential,
  ClientSecretCredential,
  ClientCertificateCredential,
  InteractiveBrowserCredential,
  ChainedTokenCredential,
  AzureCliCredential,
  AzurePowerShellCredential,
  AzureDeveloperCliCredential,
  DeviceCodeCredential,
  AzureAuthorityHosts
} from "@azure/identity";
```

## 自訂 Credential 實作

```typescript
import type { TokenCredential, AccessToken, GetTokenOptions } from "@azure/core-auth";

class CustomCredential implements TokenCredential {
  async getToken(
    scopes: string | string[],
    options?: GetTokenOptions
  ): Promise<AccessToken | null> {
    // 自訂的 token 取得邏輯
    return {
      token: "<access-token>",
      expiresOnTimestamp: Date.now() + 3600000
    };
  }
}
```

## 除錯

```typescript
import { setLogLevel, AzureLogger } from "@azure/logger";

setLogLevel("verbose");

// 自訂 log handler
AzureLogger.log = (...args) => {
  console.log("[Azure]", ...args);
};
```

## 最佳實務

1. **本機開發用 `DefaultAzureCredential`；正式環境用 `ManagedIdentityCredential` 或 `WorkloadIdentityCredential`**
2. **絕對不要寫死憑證**：用環境變數或 managed identity
3. **優先用 managed identity**：正式環境不用管 secret
4. **適當限定 credential 的範圍**：多 tenant 情境用 user-assigned identity
5. **處理 token 更新**：Azure SDK 會自動處理
6. **用 ChainedTokenCredential**：自訂 fallback 的情境
