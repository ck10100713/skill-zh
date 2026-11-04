---
name: azure-security-keyvault-secrets-java
description: 用於 secret 管理的 Azure Key Vault Secrets Java SDK。用於儲存、取得或管理密碼、API key、connection string 或其他敏感的設定資料。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: com.azure:azure-security-keyvault-secrets
---

# Azure Key Vault Secrets (Java)

安全地儲存和管理密碼、API key 和 connection string 這類 secret。

## 安裝

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-security-keyvault-secrets</artifactId>
    <version>4.9.0</version>
</dependency>
```

## 建立 Client

```java
import com.azure.core.credential.TokenCredential;
import com.azure.identity.AzureIdentityEnvVars;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.identity.ManagedIdentityCredentialBuilder;
import com.azure.security.keyvault.secrets.SecretClient;
import com.azure.security.keyvault.secrets.SecretClientBuilder;

// 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
TokenCredential credential = new DefaultAzureCredentialBuilder()
    .requireEnvVars(AzureIdentityEnvVars.AZURE_TOKEN_CREDENTIALS)
    .build();
// 或在 production 直接用特定的 credential：
// See https://learn.microsoft.com/java/api/overview/azure/identity-readme?view=azure-java-stable#credential-classes
// TokenCredential credential = new ManagedIdentityCredentialBuilder().build();

// 同步 client
SecretClient secretClient = new SecretClientBuilder()
    .vaultUrl("https://<vault-name>.vault.azure.net")
    .credential(credential)
    .buildClient();

// 非同步 client
SecretAsyncClient secretAsyncClient = new SecretClientBuilder()
    .vaultUrl("https://<vault-name>.vault.azure.net")
    .credential(credential)
    .buildAsyncClient();
```

## 建立／設定 Secret

```java
import com.azure.security.keyvault.secrets.models.KeyVaultSecret;

// 簡單的 secret
KeyVaultSecret secret = secretClient.setSecret("database-password", "P@ssw0rd123!");
System.out.println("Secret name: " + secret.getName());
System.out.println("Secret ID: " + secret.getId());

// 帶選項的 secret
KeyVaultSecret secretWithOptions = secretClient.setSecret(
    new KeyVaultSecret("api-key", "sk_live_abc123xyz")
        .setProperties(new SecretProperties()
            .setContentType("application/json")
            .setExpiresOn(OffsetDateTime.now().plusYears(1))
            .setNotBefore(OffsetDateTime.now())
            .setEnabled(true)
            .setTags(Map.of(
                "environment", "production",
                "service", "payment-api"
            ))
        )
);
```

## 取得 Secret

```java
// 取得最新版本
KeyVaultSecret secret = secretClient.getSecret("database-password");
String value = secret.getValue();
System.out.println("Secret value: " + value);

// 取得特定版本
KeyVaultSecret specificVersion = secretClient.getSecret("database-password", "<version-id>");

// 只取得屬性（不含值）
SecretProperties props = secretClient.getSecret("database-password").getProperties();
System.out.println("Enabled: " + props.isEnabled());
System.out.println("Created: " + props.getCreatedOn());
```

## 更新 Secret 屬性

```java
// 取得 secret
KeyVaultSecret secret = secretClient.getSecret("api-key");

// 更新屬性（不能更新值，要改成建立新版本）
secret.getProperties()
    .setEnabled(false)
    .setExpiresOn(OffsetDateTime.now().plusMonths(6))
    .setTags(Map.of("status", "rotating"));

SecretProperties updated = secretClient.updateSecretProperties(secret.getProperties());
System.out.println("Updated: " + updated.getUpdatedOn());
```

## 列出 Secret

```java
import com.azure.core.util.paging.PagedIterable;
import com.azure.security.keyvault.secrets.models.SecretProperties;

// 列出所有 secret（只有屬性，沒有值）
for (SecretProperties secretProps : secretClient.listPropertiesOfSecrets()) {
    System.out.println("Secret: " + secretProps.getName());
    System.out.println("  Enabled: " + secretProps.isEnabled());
    System.out.println("  Created: " + secretProps.getCreatedOn());
    System.out.println("  Content-Type: " + secretProps.getContentType());
    
    // 需要時再取得值
    if (secretProps.isEnabled()) {
        KeyVaultSecret fullSecret = secretClient.getSecret(secretProps.getName());
        System.out.println("  Value: " + fullSecret.getValue().substring(0, 5) + "...");
    }
}

// 列出某個 secret 的各個版本
for (SecretProperties version : secretClient.listPropertiesOfSecretVersions("database-password")) {
    System.out.println("Version: " + version.getVersion());
    System.out.println("Created: " + version.getCreatedOn());
    System.out.println("Enabled: " + version.isEnabled());
}
```

## 刪除 Secret

```java
import com.azure.core.util.polling.SyncPoller;
import com.azure.security.keyvault.secrets.models.DeletedSecret;

// 開始刪除（有啟用 soft-delete 的 vault 會回傳 poller）
SyncPoller<DeletedSecret, Void> deletePoller = secretClient.beginDeleteSecret("old-secret");

// 等待刪除完成
DeletedSecret deletedSecret = deletePoller.poll().getValue();
System.out.println("Deleted on: " + deletedSecret.getDeletedOn());
System.out.println("Scheduled purge: " + deletedSecret.getScheduledPurgeDate());

deletePoller.waitForCompletion();
```

## 復原已刪除的 Secret

```java
// 列出已刪除的 secret
for (DeletedSecret deleted : secretClient.listDeletedSecrets()) {
    System.out.println("Deleted: " + deleted.getName());
    System.out.println("Deletion date: " + deleted.getDeletedOn());
}

// 復原已刪除的 secret
SyncPoller<KeyVaultSecret, Void> recoverPoller = secretClient.beginRecoverDeletedSecret("old-secret");
recoverPoller.waitForCompletion();

KeyVaultSecret recovered = recoverPoller.getFinalResult();
System.out.println("Recovered: " + recovered.getName());
```

## Purge 已刪除的 Secret

```java
// 永久刪除（無法復原）
secretClient.purgeDeletedSecret("old-secret");

// 先取得已刪除 secret 的資訊
DeletedSecret deleted = secretClient.getDeletedSecret("old-secret");
System.out.println("Will purge: " + deleted.getName());
secretClient.purgeDeletedSecret("old-secret");
```

## 備份與還原

```java
// 備份 secret（所有版本）
byte[] backup = secretClient.backupSecret("important-secret");

// 存成檔案
Files.write(Paths.get("secret-backup.blob"), backup);

// 從備份還原
byte[] backupData = Files.readAllBytes(Paths.get("secret-backup.blob"));
KeyVaultSecret restored = secretClient.restoreSecretBackup(backupData);
System.out.println("Restored: " + restored.getName());
```

## 非同步操作

```java
SecretAsyncClient asyncClient = new SecretClientBuilder()
    .vaultUrl("https://<vault>.vault.azure.net")
    .credential(new DefaultAzureCredentialBuilder().build())
    .buildAsyncClient();

// 非同步設定 secret
asyncClient.setSecret("async-secret", "async-value")
    .subscribe(
        secret -> System.out.println("Created: " + secret.getName()),
        error -> System.out.println("Error: " + error.getMessage())
    );

// 非同步取得 secret
asyncClient.getSecret("async-secret")
    .subscribe(secret -> System.out.println("Value: " + secret.getValue()));

// 非同步列出 secret
asyncClient.listPropertiesOfSecrets()
    .doOnNext(props -> System.out.println("Found: " + props.getName()))
    .subscribe();
```

## 設定模式

### 載入多個 Secret

```java
public class ConfigLoader {
    private final SecretClient client;
    
    public ConfigLoader(String vaultUrl) {
        this.client = new SecretClientBuilder()
            .vaultUrl(vaultUrl)
            .credential(new DefaultAzureCredentialBuilder().build())
            .buildClient();
    }
    
    public Map<String, String> loadSecrets(List<String> secretNames) {
        Map<String, String> secrets = new HashMap<>();
        for (String name : secretNames) {
            try {
                KeyVaultSecret secret = client.getSecret(name);
                secrets.put(name, secret.getValue());
            } catch (ResourceNotFoundException e) {
                System.out.println("Secret not found: " + name);
            }
        }
        return secrets;
    }
}

// 用法
ConfigLoader loader = new ConfigLoader("https://my-vault.vault.azure.net");
Map<String, String> config = loader.loadSecrets(
    Arrays.asList("db-connection-string", "api-key", "jwt-secret")
);
```

### Secret 輪替模式

```java
public void rotateSecret(String secretName, String newValue) {
    // 取得目前的 secret
    KeyVaultSecret current = secretClient.getSecret(secretName);
    
    // 停用舊版本
    current.getProperties().setEnabled(false);
    secretClient.updateSecretProperties(current.getProperties());
    
    // 用新的值建立新版本
    KeyVaultSecret newSecret = secretClient.setSecret(secretName, newValue);
    System.out.println("Rotated to version: " + newSecret.getProperties().getVersion());
}
```

## 錯誤處理

```java
import com.azure.core.exception.HttpResponseException;
import com.azure.core.exception.ResourceNotFoundException;

try {
    KeyVaultSecret secret = secretClient.getSecret("my-secret");
    System.out.println("Value: " + secret.getValue());
} catch (ResourceNotFoundException e) {
    System.out.println("Secret not found");
} catch (HttpResponseException e) {
    int status = e.getResponse().getStatusCode();
    if (status == 403) {
        System.out.println("Access denied - check permissions");
    } else if (status == 429) {
        System.out.println("Rate limited - retry later");
    } else {
        System.out.println("HTTP error: " + status);
    }
}
```

## Secret 屬性

| 屬性 | 說明 |
|----------|-------------|
| `name` | Secret 名稱 |
| `value` | Secret 的值（字串） |
| `id` | 完整的識別 URL |
| `contentType` | MIME type 提示 |
| `enabled` | secret 是否可被取得 |
| `notBefore` | 啟用時間 |
| `expiresOn` | 到期時間 |
| `createdOn` | 建立時間戳 |
| `updatedOn` | 最後更新時間戳 |
| `recoveryLevel` | Soft-delete 的復原等級 |
| `tags` | 使用者自訂的 metadata |

## 環境變數

```bash
AZURE_KEYVAULT_URL=https://<vault-name>.vault.azure.net  # vault URL 必填
AZURE_TOKEN_CREDENTIALS=prod  # 只有在 production 使用 DefaultAzureCredential 時才需要
```

## 最佳實務

1. **啟用 Soft Delete** - 防止誤刪
2. **使用 Tag** - 用 environment、service、owner 幫 secret 加 tag
3. **設定到期日** - 需要輪替的憑證要用 `setExpiresOn()`
4. **Content Type** - 設定 `contentType` 標示格式（例如 `application/json`）
5. **版本管理** - 輪替時不要馬上刪掉舊版本
6. **存取記錄** - 在 Key Vault 啟用診斷記錄
7. **最小權限** - 不同環境用不同的 vault

## 常見的 Secret 類型

```java
// 資料庫 connection string
secretClient.setSecret(new KeyVaultSecret("db-connection", 
    "Server=myserver.database.windows.net;Database=mydb;...")
    .setProperties(new SecretProperties()
        .setContentType("text/plain")
        .setTags(Map.of("type", "connection-string"))));

// API key
secretClient.setSecret(new KeyVaultSecret("stripe-api-key", "sk_live_...")
    .setProperties(new SecretProperties()
        .setContentType("text/plain")
        .setExpiresOn(OffsetDateTime.now().plusYears(1))));

// JSON 設定
secretClient.setSecret(new KeyVaultSecret("app-config", 
    "{\"endpoint\":\"https://...\",\"key\":\"...\"}")
    .setProperties(new SecretProperties()
        .setContentType("application/json")));

// 憑證密碼
secretClient.setSecret(new KeyVaultSecret("cert-password", "CertP@ss!")
    .setProperties(new SecretProperties()
        .setContentType("text/plain")
        .setTags(Map.of("certificate", "my-cert"))));
```

## 觸發用語

- "Key Vault secrets Java", "secret management Java"
- "store password", "store API key", "connection string"
- "retrieve secret", "rotate secret"
- "Azure secrets", "vault secrets"
