---
name: azure-security-keyvault-keys-java
description: 用於加密金鑰管理的 Azure Key Vault Keys Java SDK。用於建立、管理或使用 RSA/EC 金鑰、執行加密／解密／簽章／驗章操作，或處理由 HSM 支援的金鑰。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: com.azure:azure-security-keyvault-keys
---

# Azure Key Vault Keys (Java)

在 Azure Key Vault 和 Managed HSM 裡管理加密金鑰並執行加密操作。

## 安裝

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-security-keyvault-keys</artifactId>
    <version>4.9.0</version>
</dependency>
```

## 建立 Client

```java
import com.azure.core.credential.TokenCredential;
import com.azure.identity.AzureIdentityEnvVars;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.identity.ManagedIdentityCredentialBuilder;
import com.azure.security.keyvault.keys.KeyClient;
import com.azure.security.keyvault.keys.KeyClientBuilder;
import com.azure.security.keyvault.keys.cryptography.CryptographyClient;
import com.azure.security.keyvault.keys.cryptography.CryptographyClientBuilder;

// 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
TokenCredential credential = new DefaultAzureCredentialBuilder()
    .requireEnvVars(AzureIdentityEnvVars.AZURE_TOKEN_CREDENTIALS)
    .build();
// 或在 production 直接用特定的 credential：
// See https://learn.microsoft.com/java/api/overview/azure/identity-readme?view=azure-java-stable#credential-classes
// TokenCredential credential = new ManagedIdentityCredentialBuilder().build();

// 金鑰管理 client
KeyClient keyClient = new KeyClientBuilder()
    .vaultUrl("https://<vault-name>.vault.azure.net")
    .credential(credential)
    .buildClient();

// 非同步 client
KeyAsyncClient keyAsyncClient = new KeyClientBuilder()
    .vaultUrl("https://<vault-name>.vault.azure.net")
    .credential(credential)
    .buildAsyncClient();

// 加密 client（用於加密／解密／簽章／驗章）
CryptographyClient cryptoClient = new CryptographyClientBuilder()
    .keyIdentifier("https://<vault-name>.vault.azure.net/keys/<key-name>/<key-version>")
    .credential(credential)
    .buildClient();
```

## 金鑰型別

| 型別 | 說明 |
|------|-------------|
| `RSA` | RSA 金鑰（2048、3072、4096 bits） |
| `RSA_HSM` | HSM 中的 RSA 金鑰 |
| `EC` | Elliptic Curve 金鑰 |
| `EC_HSM` | HSM 中的 Elliptic Curve 金鑰 |
| `OCT` | 對稱金鑰（僅限 Managed HSM） |
| `OCT_HSM` | HSM 中的對稱金鑰 |

## 建立金鑰

### 建立 RSA 金鑰

```java
import com.azure.security.keyvault.keys.models.*;

// 簡單的 RSA 金鑰
KeyVaultKey rsaKey = keyClient.createRsaKey(new CreateRsaKeyOptions("my-rsa-key")
    .setKeySize(2048));

System.out.println("Key name: " + rsaKey.getName());
System.out.println("Key ID: " + rsaKey.getId());
System.out.println("Key type: " + rsaKey.getKeyType());

// 帶選項的 RSA 金鑰
KeyVaultKey rsaKeyWithOptions = keyClient.createRsaKey(new CreateRsaKeyOptions("my-rsa-key-2")
    .setKeySize(4096)
    .setExpiresOn(OffsetDateTime.now().plusYears(1))
    .setNotBefore(OffsetDateTime.now())
    .setEnabled(true)
    .setKeyOperations(KeyOperation.ENCRYPT, KeyOperation.DECRYPT, 
                       KeyOperation.WRAP_KEY, KeyOperation.UNWRAP_KEY)
    .setTags(Map.of("environment", "production")));

// 由 HSM 支援的 RSA 金鑰
KeyVaultKey hsmKey = keyClient.createRsaKey(new CreateRsaKeyOptions("my-hsm-key")
    .setKeySize(2048)
    .setHardwareProtected(true));
```

### 建立 EC 金鑰

```java
// 使用 P-256 曲線的 EC 金鑰
KeyVaultKey ecKey = keyClient.createEcKey(new CreateEcKeyOptions("my-ec-key")
    .setCurveName(KeyCurveName.P_256));

// 使用其他曲線的 EC 金鑰
KeyVaultKey ecKey384 = keyClient.createEcKey(new CreateEcKeyOptions("my-ec-key-384")
    .setCurveName(KeyCurveName.P_384));

KeyVaultKey ecKey521 = keyClient.createEcKey(new CreateEcKeyOptions("my-ec-key-521")
    .setCurveName(KeyCurveName.P_521));

// 由 HSM 支援的 EC 金鑰
KeyVaultKey ecHsmKey = keyClient.createEcKey(new CreateEcKeyOptions("my-ec-hsm-key")
    .setCurveName(KeyCurveName.P_256)
    .setHardwareProtected(true));
```

### 建立對稱金鑰（僅限 Managed HSM）

```java
KeyVaultKey octKey = keyClient.createOctKey(new CreateOctKeyOptions("my-symmetric-key")
    .setKeySize(256)
    .setHardwareProtected(true));
```

## 取得金鑰

```java
// 取得最新版本
KeyVaultKey key = keyClient.getKey("my-key");

// 取得特定版本
KeyVaultKey keyVersion = keyClient.getKey("my-key", "<version-id>");

// 只取得金鑰屬性（不含金鑰素材）
KeyProperties keyProps = keyClient.getKey("my-key").getProperties();
```

## 更新金鑰屬性

```java
KeyVaultKey key = keyClient.getKey("my-key");

// 更新屬性
key.getProperties()
    .setEnabled(false)
    .setExpiresOn(OffsetDateTime.now().plusMonths(6))
    .setTags(Map.of("status", "archived"));

KeyVaultKey updatedKey = keyClient.updateKeyProperties(key.getProperties(),
    KeyOperation.ENCRYPT, KeyOperation.DECRYPT);
```

## 列出金鑰

```java
import com.azure.core.util.paging.PagedIterable;

// 列出所有金鑰
for (KeyProperties keyProps : keyClient.listPropertiesOfKeys()) {
    System.out.println("Key: " + keyProps.getName());
    System.out.println("  Enabled: " + keyProps.isEnabled());
    System.out.println("  Created: " + keyProps.getCreatedOn());
}

// 列出金鑰的各個版本
for (KeyProperties version : keyClient.listPropertiesOfKeyVersions("my-key")) {
    System.out.println("Version: " + version.getVersion());
    System.out.println("Created: " + version.getCreatedOn());
}
```

## 刪除金鑰

```java
import com.azure.core.util.polling.SyncPoller;

// 開始刪除（有啟用 soft-delete 的 vault）
SyncPoller<DeletedKey, Void> deletePoller = keyClient.beginDeleteKey("my-key");

// 等待刪除完成
DeletedKey deletedKey = deletePoller.poll().getValue();
System.out.println("Deleted: " + deletedKey.getDeletedOn());

deletePoller.waitForCompletion();

// Purge 已刪除的金鑰（永久刪除）
keyClient.purgeDeletedKey("my-key");

// 復原已刪除的金鑰
SyncPoller<KeyVaultKey, Void> recoverPoller = keyClient.beginRecoverDeletedKey("my-key");
recoverPoller.waitForCompletion();
```

## 加密操作

### 加密／解密

```java
import com.azure.security.keyvault.keys.cryptography.models.*;

CryptographyClient cryptoClient = new CryptographyClientBuilder()
    .keyIdentifier("https://<vault>.vault.azure.net/keys/<key-name>")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildClient();

byte[] plaintext = "Hello, World!".getBytes(StandardCharsets.UTF_8);

// 加密
EncryptResult encryptResult = cryptoClient.encrypt(EncryptionAlgorithm.RSA_OAEP, plaintext);
byte[] ciphertext = encryptResult.getCipherText();
System.out.println("Ciphertext length: " + ciphertext.length);

// 解密
DecryptResult decryptResult = cryptoClient.decrypt(EncryptionAlgorithm.RSA_OAEP, ciphertext);
String decrypted = new String(decryptResult.getPlainText(), StandardCharsets.UTF_8);
System.out.println("Decrypted: " + decrypted);
```

### 簽章／驗章

```java
import java.security.MessageDigest;

// 建立資料的 digest
byte[] data = "Data to sign".getBytes(StandardCharsets.UTF_8);
MessageDigest md = MessageDigest.getInstance("SHA-256");
byte[] digest = md.digest(data);

// 簽章
SignResult signResult = cryptoClient.sign(SignatureAlgorithm.RS256, digest);
byte[] signature = signResult.getSignature();

// 驗章
VerifyResult verifyResult = cryptoClient.verify(SignatureAlgorithm.RS256, digest, signature);
System.out.println("Valid signature: " + verifyResult.isValid());
```

### Wrap／Unwrap 金鑰

```java
// 要 wrap 的金鑰（例如 AES 金鑰）
byte[] keyToWrap = new byte[32];  // 256-bit 金鑰
new SecureRandom().nextBytes(keyToWrap);

// Wrap
WrapResult wrapResult = cryptoClient.wrapKey(KeyWrapAlgorithm.RSA_OAEP, keyToWrap);
byte[] wrappedKey = wrapResult.getEncryptedKey();

// Unwrap
UnwrapResult unwrapResult = cryptoClient.unwrapKey(KeyWrapAlgorithm.RSA_OAEP, wrappedKey);
byte[] unwrappedKey = unwrapResult.getKey();
```

## 備份與還原

```java
// 備份
byte[] backup = keyClient.backupKey("my-key");

// 把備份存成檔案
Files.write(Paths.get("key-backup.blob"), backup);

// 還原
byte[] backupData = Files.readAllBytes(Paths.get("key-backup.blob"));
KeyVaultKey restoredKey = keyClient.restoreKeyBackup(backupData);
```

## 金鑰輪替

```java
// 輪替成新版本
KeyVaultKey rotatedKey = keyClient.rotateKey("my-key");
System.out.println("New version: " + rotatedKey.getProperties().getVersion());

// 設定輪替政策
KeyRotationPolicy policy = new KeyRotationPolicy()
    .setExpiresIn("P90D")  // 90 天後到期
    .setLifetimeActions(Arrays.asList(
        new KeyRotationLifetimeAction(KeyRotationPolicyAction.ROTATE)
            .setTimeBeforeExpiry("P30D")));  // 到期前 30 天輪替

keyClient.updateKeyRotationPolicy("my-key", policy);

// 取得輪替政策
KeyRotationPolicy currentPolicy = keyClient.getKeyRotationPolicy("my-key");
```

## 匯入金鑰

```java
import com.azure.security.keyvault.keys.models.ImportKeyOptions;
import com.azure.security.keyvault.keys.models.JsonWebKey;

// 匯入既有的金鑰素材
JsonWebKey jsonWebKey = new JsonWebKey()
    .setKeyType(KeyType.RSA)
    .setN(modulus)
    .setE(exponent)
    .setD(privateExponent)
    // ... 其他 RSA 元件
    ;

ImportKeyOptions importOptions = new ImportKeyOptions("imported-key", jsonWebKey)
    .setHardwareProtected(false);

KeyVaultKey importedKey = keyClient.importKey(importOptions);
```

## 加密演算法

| 演算法 | 金鑰型別 | 說明 |
|-----------|----------|-------------|
| `RSA1_5` | RSA | RSAES-PKCS1-v1_5 |
| `RSA_OAEP` | RSA | 搭配 OAEP 的 RSAES（建議使用） |
| `RSA_OAEP_256` | RSA | 搭配 OAEP 並使用 SHA-256 的 RSAES |
| `A128GCM` | OCT | AES-GCM 128-bit |
| `A256GCM` | OCT | AES-GCM 256-bit |
| `A128CBC` | OCT | AES-CBC 128-bit |
| `A256CBC` | OCT | AES-CBC 256-bit |

## 簽章演算法

| 演算法 | 金鑰型別 | Hash |
|-----------|----------|------|
| `RS256` | RSA | SHA-256 |
| `RS384` | RSA | SHA-384 |
| `RS512` | RSA | SHA-512 |
| `PS256` | RSA | SHA-256 (PSS) |
| `ES256` | EC P-256 | SHA-256 |
| `ES384` | EC P-384 | SHA-384 |
| `ES512` | EC P-521 | SHA-512 |

## 錯誤處理

```java
import com.azure.core.exception.HttpResponseException;
import com.azure.core.exception.ResourceNotFoundException;

try {
    KeyVaultKey key = keyClient.getKey("non-existent-key");
} catch (ResourceNotFoundException e) {
    System.out.println("Key not found: " + e.getMessage());
} catch (HttpResponseException e) {
    System.out.println("HTTP error " + e.getResponse().getStatusCode());
    System.out.println("Message: " + e.getMessage());
}
```

## 環境變數

```bash
AZURE_KEYVAULT_URL=https://<vault-name>.vault.azure.net  # vault URL 必填
AZURE_TOKEN_CREDENTIALS=prod  # 只有在 production 使用 DefaultAzureCredential 時才需要
```

## 最佳實務

1. **Production 用 HSM 金鑰** - 敏感金鑰要設 `setHardwareProtected(true)`
2. **啟用 Soft Delete** - 防止誤刪
3. **金鑰輪替** - 設定自動輪替政策
4. **最小權限** - 不同操作用不同的金鑰
5. **盡量在本地做加密** - 搭配本地金鑰素材使用 `CryptographyClient`，減少來回的 round-trip

## 觸發用語

- "Key Vault keys Java", "cryptographic keys Java"
- "encrypt decrypt Java", "sign verify Java"
- "RSA key", "EC key", "HSM key"
- "key rotation", "wrap unwrap key"
