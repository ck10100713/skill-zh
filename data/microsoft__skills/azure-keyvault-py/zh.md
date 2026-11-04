---
name: azure-keyvault-py
description: |
  Python 版 Azure Key Vault SDK。用於 secret、金鑰和憑證的管理與安全儲存。
  Triggers: "key vault", "SecretClient", "KeyClient", "CertificateClient", "secrets", "encryption keys".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-keyvault-secrets, azure-keyvault-keys, azure-keyvault-certificates
---

# Python 版 Azure Key Vault SDK

安全地儲存和管理 secret、加密金鑰和憑證。

## 安裝

```bash
# Secrets
pip install azure-keyvault-secrets azure-identity

# Keys (cryptographic operations)
pip install azure-keyvault-keys azure-identity

# Certificates
pip install azure-keyvault-certificates azure-identity

# All
pip install azure-keyvault-secrets azure-keyvault-keys azure-keyvault-certificates azure-identity
```

## 環境變數

```bash
AZURE_KEYVAULT_URL=https://<vault-name>.vault.azure.net/  # 所有驗證方式都必須設定
AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境使用 DefaultAzureCredential 時才需要
```

## 驗證與生命週期

> **🔑 下面每個範例都適用兩條規則：**
>
> 1. **優先用 `DefaultAzureCredential`。** 它在本機（Azure CLI / VS Code / Developer CLI）和 Azure 上（managed identity、workload identity）都能跑，程式碼不用改。避免用 connection string、帳號金鑰或 API key，因為它們會繞過 Entra 的稽核和輪替。
>    - 本機開發：`DefaultAzureCredential` 直接可用。
>    - 正式環境：設定 `AZURE_TOKEN_CREDENTIALS=prod`（或 `AZURE_TOKEN_CREDENTIALS=<specific_credential>`），把 credential chain 限制在正式環境安全的 credential。
> 2. **每個 client 都用 context manager 包起來**，這樣 HTTP transport、socket 和 token 快取才會確定被釋放：
>    - 同步：`with <Client>(...) as client:`
>    - 非同步：`async with <Client>(...) as client:` **而且** `async with DefaultAzureCredential() as credential:`（來自 `azure.identity.aio`）
>
> 範例片段可能會簡化這段設定，但正式環境的程式碼一定要遵守這兩條規則。

## Secret

### SecretClient 設定

```python
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient

# 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或是在正式環境直接用特定的 credential：
# 參考 https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()
vault_url = "https://<vault-name>.vault.azure.net/"

with SecretClient(vault_url=vault_url, credential=credential) as client:
    # 所有 secret 操作都放在這個區塊裡（範例見下面）
    ...
```

### Secret 操作

```python
# 設定 secret
secret = client.set_secret("database-password", "super-secret-value")
print(f"Created: {secret.name}, version: {secret.properties.version}")

# 取得 secret
secret = client.get_secret("database-password")
print(f"Value: {secret.value}")

# 取得特定版本
secret = client.get_secret("database-password", version="abc123")

# 列出 secret（只有名稱，沒有值）
for secret_properties in client.list_properties_of_secrets():
    print(f"Secret: {secret_properties.name}")

# 列出版本
for version in client.list_properties_of_secret_versions("database-password"):
    print(f"Version: {version.version}, Created: {version.created_on}")

# 刪除 secret（soft delete）
poller = client.begin_delete_secret("database-password")
deleted_secret = poller.result()

# Purge（永久刪除，需啟用 soft-delete）
client.purge_deleted_secret("database-password")

# 復原已刪除的 secret
client.begin_recover_deleted_secret("database-password").result()
```

## 金鑰

### KeyClient 設定

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient

credential = DefaultAzureCredential()
vault_url = "https://<vault-name>.vault.azure.net/"

with KeyClient(vault_url=vault_url, credential=credential) as client:
    # 所有金鑰操作都放在這個區塊裡（範例見下面）
    ...
```

### 金鑰操作

```python
from azure.keyvault.keys import KeyType

# 建立 RSA 金鑰
rsa_key = client.create_rsa_key("rsa-key", size=2048)

# 建立 EC 金鑰
ec_key = client.create_ec_key("ec-key", curve="P-256")

# 取得金鑰
key = client.get_key("rsa-key")
print(f"Key type: {key.key_type}")

# 列出金鑰
for key_properties in client.list_properties_of_keys():
    print(f"Key: {key_properties.name}")

# 刪除金鑰
poller = client.begin_delete_key("rsa-key")
deleted_key = poller.result()
```

### 加密操作

```python
from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm

# 取得特定金鑰的 crypto client
# crypto_client = CryptographyClient(key, credential=credential)
# 或從金鑰 ID
with CryptographyClient(
    "https://<vault>.vault.azure.net/keys/<key-name>/<version>",
    credential=credential
) as crypto_client:
    # 加密
    plaintext = b"Hello, Key Vault!"
    result = crypto_client.encrypt(EncryptionAlgorithm.rsa_oaep, plaintext)
    ciphertext = result.ciphertext

    # 解密
    result = crypto_client.decrypt(EncryptionAlgorithm.rsa_oaep, ciphertext)
    decrypted = result.plaintext

    # 簽署
    from azure.keyvault.keys.crypto import SignatureAlgorithm
    import hashlib

    digest = hashlib.sha256(b"data to sign").digest()
    result = crypto_client.sign(SignatureAlgorithm.rs256, digest)
    signature = result.signature

    # 驗證
    result = crypto_client.verify(SignatureAlgorithm.rs256, digest, signature)
    print(f"Valid: {result.is_valid}")
```

## 憑證

### CertificateClient 設定

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient, CertificatePolicy

credential = DefaultAzureCredential()
vault_url = "https://<vault-name>.vault.azure.net/"

with CertificateClient(vault_url=vault_url, credential=credential) as client:
    # 所有憑證操作都放在這個區塊裡（範例見下面）
    ...
```

### 憑證操作

```python
# 建立自簽憑證
policy = CertificatePolicy.get_default()
poller = client.begin_create_certificate("my-cert", policy=policy)
certificate = poller.result()

# 取得憑證
certificate = client.get_certificate("my-cert")
print(f"Thumbprint: {certificate.properties.x509_thumbprint.hex()}")

# 取得含私鑰的憑證（以 secret 的形式）
from azure.keyvault.secrets import SecretClient
with SecretClient(vault_url=vault_url, credential=credential) as secret_client:
    cert_secret = secret_client.get_secret("my-cert")
    # cert_secret.value 內容是 PEM 或 PKCS12

# 列出憑證
for cert in client.list_properties_of_certificates():
    print(f"Certificate: {cert.name}")

# 刪除憑證
poller = client.begin_delete_certificate("my-cert")
deleted = poller.result()
```

## Client 類型表

| Client | 套件 | 用途 |
|--------|---------|---------|
| `SecretClient` | `azure-keyvault-secrets` | 儲存／取得 secret |
| `KeyClient` | `azure-keyvault-keys` | 管理加密金鑰 |
| `CryptographyClient` | `azure-keyvault-keys` | 加密／解密／簽署／驗證 |
| `CertificateClient` | `azure-keyvault-certificates` | 管理憑證 |

## 非同步 Client

```python
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.secrets.aio import SecretClient

async def get_secret():
    async with DefaultAzureCredential() as credential:
        async with SecretClient(vault_url=vault_url, credential=credential) as client:
            secret = await client.get_secret("my-secret")
            print(secret.value)

import asyncio
asyncio.run(get_secret())
```

## 錯誤處理

```python
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

try:
    secret = client.get_secret("nonexistent")
except ResourceNotFoundError:
    print("Secret not found")
except HttpResponseError as e:
    if e.status_code == 403:
        print("Access denied - check RBAC permissions")
    raise
```

## 最佳實務

1. **同步或非同步選一種，並保持一致。** 同一條呼叫路徑裡不要混用 `azure.xxx` 的同步 client 和 `azure.xxx.aio` 的非同步 client。每個 module 選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都用 `with Client(...) as client:`（同步）或 `async with Client(...) as client:`（非同步）包起來。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，這樣 token 和 transport 才會被清掉。
3. **在本機跑的程式碼用 `DefaultAzureCredential`。** 在 Azure 上跑的程式碼用特定的 token credential。
4. **託管在 Azure 的應用程式用 managed identity**
5. **啟用 soft-delete** 以便復原（預設就是啟用）
6. **用 RBAC 而不是 access policy**，控制比較細
7. **定期輪替 secret**，用版本管理
8. **在 App Service/Functions 的設定裡用 Key Vault reference**
9. **適當快取 secret**，減少 API 呼叫
10. **高吞吐量情境用非同步 client**

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打的功能、各 operation group 的涵蓋範圍，以及正式環境檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 次要／進階情境的專屬非主打範例。 |
