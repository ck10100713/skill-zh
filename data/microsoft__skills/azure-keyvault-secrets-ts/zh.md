---
name: azure-keyvault-secrets-ts
description: 用 JavaScript 版 Azure Key Vault Secrets SDK（@azure/keyvault-secrets）管理 secret。儲存和取得應用程式的 secret 或設定值時使用。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: '@azure/keyvault-secrets'
---

# TypeScript 版 Azure Key Vault Secrets SDK

用 Azure Key Vault 管理 secret。

## 安裝

```bash
# Secrets SDK
npm install @azure/keyvault-secrets @azure/identity
```

## 環境變數

```bash
KEY_VAULT_URL=https://<vault-name>.vault.azure.net
# Or
AZURE_KEYVAULT_NAME=<vault-name>
AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境使用 DefaultAzureCredential 時才需要
```

## 驗證

```typescript
import { DefaultAzureCredential, ManagedIdentityCredential } from "@azure/identity";
import { SecretClient } from "@azure/keyvault-secrets";

// 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
const credential = new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]});
// 或是在正式環境直接用特定的 credential：
// 參考 https://learn.microsoft.com/javascript/api/overview/azure/identity-readme?view=azure-node-latest#credential-classes
// const credential = new ManagedIdentityCredential();
const vaultUrl = `https://${process.env.AZURE_KEYVAULT_NAME}.vault.azure.net`;

const keyClient = new KeyClient(vaultUrl, credential);
const secretClient = new SecretClient(vaultUrl, credential);
```

## Secret 操作

### 建立／設定 Secret

```typescript
const secret = await secretClient.setSecret("MySecret", "secret-value");

// 帶屬性
const secretWithAttrs = await secretClient.setSecret("MySecret", "value", {
  enabled: true,
  expiresOn: new Date("2025-12-31"),
  contentType: "application/json",
  tags: { environment: "production" }
});
```

### 取得 Secret

```typescript
// 取得最新版本
const secret = await secretClient.getSecret("MySecret");
console.log(secret.value);

// 取得特定版本
const specificSecret = await secretClient.getSecret("MySecret", {
  version: secret.properties.version
});
```

### 列出 Secret

```typescript
for await (const secretProperties of secretClient.listPropertiesOfSecrets()) {
  console.log(secretProperties.name);
}

// 列出版本
for await (const version of secretClient.listPropertiesOfSecretVersions("MySecret")) {
  console.log(version.version);
}
```

### 刪除 Secret

```typescript
// Soft delete
const deletePoller = await secretClient.beginDeleteSecret("MySecret");
await deletePoller.pollUntilDone();

// Purge（永久刪除）
await secretClient.purgeDeletedSecret("MySecret");

// 復原
const recoverPoller = await secretClient.beginRecoverDeletedSecret("MySecret");
await recoverPoller.pollUntilDone();
```

## 金鑰操作

### 建立金鑰

```typescript
// 通用金鑰
const key = await keyClient.createKey("MyKey", "RSA");

// 指定大小的 RSA 金鑰
const rsaKey = await keyClient.createRsaKey("MyRsaKey", { keySize: 2048 });

// 橢圓曲線金鑰
const ecKey = await keyClient.createEcKey("MyEcKey", { curve: "P-256" });

// 帶屬性
const keyWithAttrs = await keyClient.createKey("MyKey", "RSA", {
  enabled: true,
  expiresOn: new Date("2025-12-31"),
  tags: { purpose: "encryption" },
  keyOps: ["encrypt", "decrypt", "sign", "verify"]
});
```

### 取得金鑰

```typescript
const key = await keyClient.getKey("MyKey");
console.log(key.name, key.keyType);
```

### 列出金鑰

```typescript
for await (const keyProperties of keyClient.listPropertiesOfKeys()) {
  console.log(keyProperties.name);
}
```

### 輪替金鑰

```typescript
// 手動輪替
const rotatedKey = await keyClient.rotateKey("MyKey");

// 設定輪替 policy
await keyClient.updateKeyRotationPolicy("MyKey", {
  lifetimeActions: [{ action: "Rotate", timeBeforeExpiry: "P30D" }],
  expiresIn: "P90D"
});
```

### 刪除金鑰

```typescript
const deletePoller = await keyClient.beginDeleteKey("MyKey");
await deletePoller.pollUntilDone();

// Purge
await keyClient.purgeDeletedKey("MyKey");
```

## 加密操作

### 建立 CryptographyClient

```typescript
import { CryptographyClient } from "@azure/keyvault-keys";

// 從金鑰物件
const cryptoClient = new CryptographyClient(key, credential);

// 從金鑰 ID
const cryptoClient = new CryptographyClient(key.id!, credential);
```

### 加密／解密

```typescript
// 加密
const encryptResult = await cryptoClient.encrypt({
  algorithm: "RSA-OAEP",
  plaintext: Buffer.from("My secret message")
});

// 解密
const decryptResult = await cryptoClient.decrypt({
  algorithm: "RSA-OAEP",
  ciphertext: encryptResult.result
});

console.log(decryptResult.result.toString());
```

### 簽署／驗證

```typescript
import { createHash } from "node:crypto";

// 建立 digest
const hash = createHash("sha256").update("My message").digest();

// 簽署
const signResult = await cryptoClient.sign("RS256", hash);

// 驗證
const verifyResult = await cryptoClient.verify("RS256", hash, signResult.result);
console.log("Valid:", verifyResult.result);
```

### Wrap／Unwrap 金鑰

```typescript
// Wrap 金鑰（加密後儲存）
const wrapResult = await cryptoClient.wrapKey("RSA-OAEP", Buffer.from("key-material"));

// Unwrap
const unwrapResult = await cryptoClient.unwrapKey("RSA-OAEP", wrapResult.result);
```

## 備份與還原

```typescript
// 備份
const keyBackup = await keyClient.backupKey("MyKey");
const secretBackup = await secretClient.backupSecret("MySecret");

// 還原（可以還原到不同的 vault）
const restoredKey = await keyClient.restoreKeyBackup(keyBackup!);
const restoredSecret = await secretClient.restoreSecretBackup(secretBackup!);
```

## 主要型別

```typescript
import {
  KeyClient,
  KeyVaultKey,
  KeyProperties,
  DeletedKey,
  CryptographyClient,
  KnownEncryptionAlgorithms,
  KnownSignatureAlgorithms
} from "@azure/keyvault-keys";

import {
  SecretClient,
  KeyVaultSecret,
  SecretProperties,
  DeletedSecret
} from "@azure/keyvault-secrets";
```

## 錯誤處理

```typescript
try {
  const secret = await secretClient.getSecret("NonExistent");
} catch (error: any) {
  if (error.code === "SecretNotFound") {
    console.log("Secret does not exist");
  } else {
    throw error;
  }
}
```

## 最佳實務

1. **本機開發用 `DefaultAzureCredential`；正式環境用 `ManagedIdentityCredential` 或 `WorkloadIdentityCredential`**
2. **啟用 soft-delete**：正式環境的 vault 必須啟用
3. **設定到期日**：金鑰和 secret 都要設
4. **用金鑰輪替 policy**：自動化金鑰輪替
5. **限制金鑰操作**：只授予需要的操作（encrypt、sign 等）
6. **不支援瀏覽器**：這些 SDK 只能在 Node.js 用
