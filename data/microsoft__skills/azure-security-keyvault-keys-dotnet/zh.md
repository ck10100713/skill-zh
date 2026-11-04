---
name: azure-security-keyvault-keys-dotnet
description: |
  .NET 版的 Azure Key Vault Keys SDK。用來管理 Azure Key Vault 和 Managed HSM 裡加密金鑰的 client library。用於建立金鑰、輪替、加密、解密、簽章和驗章。Triggers: "Key Vault keys", "KeyClient", "CryptographyClient", "RSA key", "EC key", "encrypt decrypt .NET", "key rotation", "HSM".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.Security.KeyVault.Keys
---

# Azure.Security.KeyVault.Keys (.NET)

用來管理 Azure Key Vault 和 Managed HSM 裡加密金鑰的 client library。

## 安裝

```bash
dotnet add package Azure.Security.KeyVault.Keys
dotnet add package Azure.Identity
```

**目前版本**：4.7.0（stable）

## 環境變數

```bash
KEY_VAULT_NAME=<your-key-vault-name>  # 必填：Key Vault 名稱
AZURE_KEYVAULT_URL=https://<vault-name>.vault.azure.net  # 選填：完整的 Key Vault URL
AZURE_TOKEN_CREDENTIALS=prod  # 只有在 production 使用 DefaultAzureCredential 時才需要
```

## Client 階層

```
KeyClient (key management)
├── CreateKey / CreateRsaKey / CreateEcKey
├── GetKey / GetKeys
├── UpdateKeyProperties
├── DeleteKey / PurgeDeletedKey
├── BackupKey / RestoreKey
└── GetCryptographyClient() → CryptographyClient

CryptographyClient (cryptographic operations)
├── Encrypt / Decrypt
├── WrapKey / UnwrapKey
├── Sign / Verify
└── SignData / VerifyData

KeyResolver (key resolution)
└── Resolve(keyId) → CryptographyClient
```

## 驗證

### Microsoft Entra Token Credential

```csharp
using Azure.Identity;
using Azure.Security.KeyVault.Keys;

var keyVaultName = Environment.GetEnvironmentVariable("KEY_VAULT_NAME");
var kvUri = $"https://{keyVaultName}.vault.azure.net";

// 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
var credential = new DefaultAzureCredential(
    DefaultAzureCredential.DefaultEnvironmentVariableName
);
// 或在 production 直接用特定的 credential：
// See https://learn.microsoft.com/dotnet/api/overview/azure/identity-readme?view=azure-dotnet#credential-classes
// var credential = new ManagedIdentityCredential();
var client = new KeyClient(new Uri(kvUri), credential);
```

### Service Principal

```csharp
var credential = new ClientSecretCredential(
    tenantId: "<tenant-id>",
    clientId: "<client-id>",
    clientSecret: "<client-secret>");

var client = new KeyClient(new Uri(kvUri), credential);
```

## 金鑰管理

### 建立金鑰

```csharp
// 建立 RSA 金鑰
KeyVaultKey rsaKey = await client.CreateKeyAsync("my-rsa-key", KeyType.Rsa);
Console.WriteLine($"Created key: {rsaKey.Name}, Type: {rsaKey.KeyType}");

// 用選項建立 RSA 金鑰
var rsaOptions = new CreateRsaKeyOptions("my-rsa-key-2048")
{
    KeySize = 2048,
    HardwareProtected = false, // true 表示由 HSM 支援
    ExpiresOn = DateTimeOffset.UtcNow.AddYears(1),
    NotBefore = DateTimeOffset.UtcNow,
    Enabled = true
};
rsaOptions.KeyOperations.Add(KeyOperation.Encrypt);
rsaOptions.KeyOperations.Add(KeyOperation.Decrypt);

KeyVaultKey rsaKey2 = await client.CreateRsaKeyAsync(rsaOptions);

// 建立 EC 金鑰
var ecOptions = new CreateEcKeyOptions("my-ec-key")
{
    CurveName = KeyCurveName.P256,
    HardwareProtected = true // 由 HSM 支援
};
KeyVaultKey ecKey = await client.CreateEcKeyAsync(ecOptions);

// 建立用於 wrap/unwrap 的 Oct（對稱）金鑰
var octOptions = new CreateOctKeyOptions("my-oct-key")
{
    KeySize = 256,
    HardwareProtected = true
};
KeyVaultKey octKey = await client.CreateOctKeyAsync(octOptions);
```

### 取得金鑰

```csharp
// 取得特定金鑰（最新版本）
KeyVaultKey key = await client.GetKeyAsync("my-rsa-key");
Console.WriteLine($"Key ID: {key.Id}");
Console.WriteLine($"Key Type: {key.KeyType}");
Console.WriteLine($"Version: {key.Properties.Version}");

// 取得特定版本
KeyVaultKey keyVersion = await client.GetKeyAsync("my-rsa-key", "version-id");

// 列出所有金鑰
await foreach (KeyProperties keyProps in client.GetPropertiesOfKeysAsync())
{
    Console.WriteLine($"Key: {keyProps.Name}, Enabled: {keyProps.Enabled}");
}

// 列出金鑰的各個版本
await foreach (KeyProperties version in client.GetPropertiesOfKeyVersionsAsync("my-rsa-key"))
{
    Console.WriteLine($"Version: {version.Version}, Created: {version.CreatedOn}");
}
```

### 更新金鑰屬性

```csharp
KeyVaultKey key = await client.GetKeyAsync("my-rsa-key");

key.Properties.ExpiresOn = DateTimeOffset.UtcNow.AddYears(2);
key.Properties.Tags["environment"] = "production";

KeyVaultKey updatedKey = await client.UpdateKeyPropertiesAsync(key.Properties);
```

### 刪除與 Purge 金鑰

```csharp
// 開始刪除操作
DeleteKeyOperation operation = await client.StartDeleteKeyAsync("my-rsa-key");

// 等刪除完成（purge 之前必須先完成）
await operation.WaitForCompletionAsync();
Console.WriteLine($"Deleted key scheduled purge date: {operation.Value.ScheduledPurgeDate}");

// 立即 purge（如果有啟用 soft-delete）
await client.PurgeDeletedKeyAsync("my-rsa-key");

// 或是復原已刪除的金鑰
KeyVaultKey recoveredKey = await client.StartRecoverDeletedKeyAsync("my-rsa-key");
```

### 備份與還原

```csharp
// 備份金鑰
byte[] backup = await client.BackupKeyAsync("my-rsa-key");
await File.WriteAllBytesAsync("key-backup.bin", backup);

// 還原金鑰
byte[] backupData = await File.ReadAllBytesAsync("key-backup.bin");
KeyVaultKey restoredKey = await client.RestoreKeyBackupAsync(backupData);
```

## 加密操作

### 取得 CryptographyClient

```csharp
// 從 KeyClient 取得
KeyVaultKey key = await client.GetKeyAsync("my-rsa-key");
CryptographyClient cryptoClient = client.GetCryptographyClient(
    key.Name, 
    key.Properties.Version);

// 或用 key ID 直接建立
CryptographyClient cryptoClient = new CryptographyClient(
    new Uri("https://myvault.vault.azure.net/keys/my-rsa-key/version"),
    new DefaultAzureCredential());
```

### 加密與解密

```csharp
byte[] plaintext = Encoding.UTF8.GetBytes("Secret message to encrypt");

// 加密
EncryptResult encryptResult = await cryptoClient.EncryptAsync(
    EncryptionAlgorithm.RsaOaep256, 
    plaintext);
Console.WriteLine($"Encrypted: {Convert.ToBase64String(encryptResult.Ciphertext)}");

// 解密
DecryptResult decryptResult = await cryptoClient.DecryptAsync(
    EncryptionAlgorithm.RsaOaep256, 
    encryptResult.Ciphertext);
string decrypted = Encoding.UTF8.GetString(decryptResult.Plaintext);
Console.WriteLine($"Decrypted: {decrypted}");
```

### Wrap 與 Unwrap 金鑰

```csharp
// 要 wrap 的金鑰（例如 AES 金鑰）
byte[] keyToWrap = new byte[32]; // 256-bit 金鑰
RandomNumberGenerator.Fill(keyToWrap);

// Wrap 金鑰
WrapResult wrapResult = await cryptoClient.WrapKeyAsync(
    KeyWrapAlgorithm.RsaOaep256, 
    keyToWrap);

// Unwrap 金鑰
UnwrapResult unwrapResult = await cryptoClient.UnwrapKeyAsync(
    KeyWrapAlgorithm.RsaOaep256, 
    wrapResult.EncryptedKey);
```

### 簽章與驗章

```csharp
// 要簽章的資料
byte[] data = Encoding.UTF8.GetBytes("Data to sign");

// 簽章資料（內部會計算 hash）
SignResult signResult = await cryptoClient.SignDataAsync(
    SignatureAlgorithm.RS256, 
    data);

// 驗證簽章
VerifyResult verifyResult = await cryptoClient.VerifyDataAsync(
    SignatureAlgorithm.RS256, 
    data, 
    signResult.Signature);
Console.WriteLine($"Signature valid: {verifyResult.IsValid}");

// 或是簽章預先算好的 hash
using var sha256 = SHA256.Create();
byte[] hash = sha256.ComputeHash(data);

SignResult signHashResult = await cryptoClient.SignAsync(
    SignatureAlgorithm.RS256, 
    hash);
```

## Key Resolver

```csharp
using Azure.Security.KeyVault.Keys.Cryptography;

var resolver = new KeyResolver(new DefaultAzureCredential());

// 用 ID 解析金鑰，取得 CryptographyClient
CryptographyClient cryptoClient = await resolver.ResolveAsync(
    new Uri("https://myvault.vault.azure.net/keys/my-key/version"));

// 用來加密
EncryptResult result = await cryptoClient.EncryptAsync(
    EncryptionAlgorithm.RsaOaep256, 
    plaintext);
```

## 金鑰輪替

```csharp
// 輪替金鑰（會建立新版本）
KeyVaultKey rotatedKey = await client.RotateKeyAsync("my-rsa-key");
Console.WriteLine($"New version: {rotatedKey.Properties.Version}");

// 取得輪替政策
KeyRotationPolicy policy = await client.GetKeyRotationPolicyAsync("my-rsa-key");

// 更新輪替政策
policy.ExpiresIn = "P90D"; // 90 天
policy.LifetimeActions.Add(new KeyRotationLifetimeAction
{
    Action = KeyRotationPolicyAction.Rotate,
    TimeBeforeExpiry = "P30D" // 到期前 30 天輪替
});

await client.UpdateKeyRotationPolicyAsync("my-rsa-key", policy);
```

## 金鑰型別參考

| 型別 | 用途 |
|------|---------|
| `KeyClient` | 金鑰管理操作 |
| `CryptographyClient` | 加密操作 |
| `KeyResolver` | 把 key ID 解析成 CryptographyClient |
| `KeyVaultKey` | 帶有加密素材的金鑰 |
| `KeyProperties` | 金鑰 metadata（沒有加密素材） |
| `CreateRsaKeyOptions` | RSA 金鑰建立選項 |
| `CreateEcKeyOptions` | EC 金鑰建立選項 |
| `CreateOctKeyOptions` | 對稱金鑰選項 |
| `EncryptResult` | 加密結果 |
| `DecryptResult` | 解密結果 |
| `SignResult` | 簽章結果 |
| `VerifyResult` | 驗章結果 |
| `WrapResult` | 金鑰 wrap 結果 |
| `UnwrapResult` | 金鑰 unwrap 結果 |

## 演算法參考

### 加密演算法
| 演算法 | 金鑰型別 | 說明 |
|-----------|----------|-------------|
| `RsaOaep` | RSA | RSA-OAEP |
| `RsaOaep256` | RSA | RSA-OAEP-256 |
| `Rsa15` | RSA | RSA 1.5（舊式） |
| `A128Gcm` | Oct | AES-128-GCM |
| `A256Gcm` | Oct | AES-256-GCM |

### 簽章演算法
| 演算法 | 金鑰型別 | 說明 |
|-----------|----------|-------------|
| `RS256` | RSA | RSASSA-PKCS1-v1_5 SHA-256 |
| `RS384` | RSA | RSASSA-PKCS1-v1_5 SHA-384 |
| `RS512` | RSA | RSASSA-PKCS1-v1_5 SHA-512 |
| `PS256` | RSA | RSASSA-PSS SHA-256 |
| `ES256` | EC | ECDSA P-256 SHA-256 |
| `ES384` | EC | ECDSA P-384 SHA-384 |
| `ES512` | EC | ECDSA P-521 SHA-512 |

### 金鑰 Wrap 演算法
| 演算法 | 金鑰型別 | 說明 |
|-----------|----------|-------------|
| `RsaOaep` | RSA | RSA-OAEP |
| `RsaOaep256` | RSA | RSA-OAEP-256 |
| `A128KW` | Oct | AES-128 Key Wrap |
| `A256KW` | Oct | AES-256 Key Wrap |

## 最佳實務

1. **用 Managed Identity** — 優先用 `DefaultAzureCredential`，不要用 secret
2. **啟用 soft-delete** — 防止誤刪
3. **用 HSM 支援的金鑰** — 敏感金鑰要設 `HardwareProtected = true`
4. **實作金鑰輪替** — 用自動輪替政策
5. **限制金鑰操作** — 只啟用需要的 `KeyOperations`
6. **設定到期日** — 金鑰一定要設 `ExpiresOn`
7. **指定版本** — production 要固定在特定版本
8. **快取 CryptographyClient** — 多次操作時重複使用

## 錯誤處理

```csharp
using Azure;

try
{
    KeyVaultKey key = await client.GetKeyAsync("my-key");
}
catch (RequestFailedException ex) when (ex.Status == 404)
{
    Console.WriteLine("Key not found");
}
catch (RequestFailedException ex) when (ex.Status == 403)
{
    Console.WriteLine("Access denied - check RBAC permissions");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Key Vault error: {ex.Status} - {ex.Message}");
}
```

## 必要的 RBAC 角色

| 角色 | 權限 |
|------|-------------|
| Key Vault Crypto Officer | 完整的金鑰管理 |
| Key Vault Crypto User | 使用金鑰做加密操作 |
| Key Vault Reader | 讀取金鑰 metadata |

## 相關 SDK

| SDK | 用途 | 安裝 |
|-----|---------|---------|
| `Azure.Security.KeyVault.Keys` | Keys（本 SDK） | `dotnet add package Azure.Security.KeyVault.Keys` |
| `Azure.Security.KeyVault.Secrets` | Secrets | `dotnet add package Azure.Security.KeyVault.Secrets` |
| `Azure.Security.KeyVault.Certificates` | Certificates | `dotnet add package Azure.Security.KeyVault.Certificates` |
| `Azure.Identity` | 驗證 | `dotnet add package Azure.Identity` |

## 參考連結

| 資源 | URL |
|----------|-----|
| NuGet Package | https://www.nuget.org/packages/Azure.Security.KeyVault.Keys |
| API Reference | https://learn.microsoft.com/dotnet/api/azure.security.keyvault.keys |
| Quickstart | https://learn.microsoft.com/azure/key-vault/keys/quick-create-net |
| GitHub Source | https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/keyvault/Azure.Security.KeyVault.Keys |
