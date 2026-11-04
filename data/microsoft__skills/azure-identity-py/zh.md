---
name: azure-identity-py
description: |
  Python 用 Microsoft Entra ID 做驗證的 Azure Identity SDK。用於 DefaultAzureCredential、managed identity、service principal 和 token 快取。
  Triggers: "azure-identity", "DefaultAzureCredential", "authentication", "managed identity", "service principal", "credential".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-identity
---

# Python 版 Azure Identity 函式庫

用 Microsoft Entra ID 為 Azure SDK client 做驗證的函式庫。

這些情況用這個 skill：
- App 需要從 Python 對 Azure 服務做驗證
- 需要 `DefaultAzureCredential`，同時涵蓋本機開發和 Azure 部署
- 需要 `ManagedIdentityCredential`，給託管在 Azure 的工作負載用
- 需要用 secret 或憑證做 service principal 驗證
- 需要用 `get_token()` 直接取得 token
- 需要排查 credential chain 的失敗

## 安裝

```bash
pip install azure-identity
```

要用 VS Code 或 broker 型的桌面驗證：

```bash
pip install azure-identity-broker
```

## Python 版本

`azure-identity` 支援 Python 3.9+。

## 環境變數

```bash
# Service principal with client secret
AZURE_TENANT_ID=<your-tenant-id>
AZURE_CLIENT_ID=<your-client-id>
AZURE_CLIENT_SECRET=<your-client-secret>

# Service principal with certificate
AZURE_TENANT_ID=<your-tenant-id>
AZURE_CLIENT_ID=<your-client-id>
AZURE_CLIENT_CERTIFICATE_PATH=/path/to/cert.pem
AZURE_CLIENT_CERTIFICATE_PASSWORD=<optional-password>

# Authority (sovereign clouds)
AZURE_AUTHORITY_HOST=login.microsoftonline.com  # 預設值；也可以是 login.chinacloudapi.cn、login.microsoftonline.us

# User-assigned managed identity
AZURE_CLIENT_ID=<managed-identity-client-id>

# Credential selection (new)
AZURE_TOKEN_CREDENTIALS=dev|prod|<credential-name>  # 選填，限制 DAC chain
```

## 驗證與生命週期

> **🔑 下面每個範例都適用兩條規則：**
>
> 1. **優先用 `DefaultAzureCredential`。** 它在本機（Azure CLI / VS Code / Developer CLI）和 Azure 上（managed identity、workload identity）都能跑，程式碼不用改。避免用 connection string、帳號金鑰或 API key，因為它們會繞過 Entra 的稽核和輪替。
>    - 本機開發：`DefaultAzureCredential` 直接可用。
>    - 正式環境：設定 `AZURE_TOKEN_CREDENTIALS=prod`（或 `AZURE_TOKEN_CREDENTIALS=<specific_credential>`），把 credential chain 限制在正式環境安全的 credential。
> 2. **當 credential 和 client 擁有 token 快取／transport 時，用 context manager 包起來**：
>    - 同步：`with DefaultAzureCredential() as credential:`
>    - 非同步：`async with DefaultAzureCredential() as credential:`（來自 `azure.identity.aio`）
>
> 範例片段可能會簡化這段設定，但正式環境的程式碼一定要遵守這兩條規則。

### DefaultAzureCredential

大多數情境建議用的 credential。它會依序嘗試多種驗證方式：

```python
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# 本機開發和正式環境都能用，程式碼不用改
credential = DefaultAzureCredential()

with BlobServiceClient(
    account_url="https://<account>.blob.core.windows.net",
    credential=credential
) as client:
    containers = list(client.list_containers())
```

### Credential Chain 順序

目前的 credential chain 順序和預設值，請看 [DefaultAzureCredential 概觀](https://aka.ms/azsdk/python/identity/credential-chains#defaultazurecredential-overview)。

### 自訂 DefaultAzureCredential

```python
# 排除你不需要的 credential
credential = DefaultAzureCredential(
    exclude_environment_credential=True,
    exclude_shared_token_cache_credential=True,
    managed_identity_client_id="<user-assigned-mi-client-id>"  # user-assigned MI 用（也接受 object ID 或 resource ID）
)

# 啟用互動式瀏覽器（預設是關的）
credential = DefaultAzureCredential(
    exclude_interactive_browser_credential=False
)

# 設定 CLI 型 credential 的 subprocess timeout（預設：10 秒）
credential = DefaultAzureCredential(process_timeout=30)

# 要求一定要設定 AZURE_TOKEN_CREDENTIALS 環境變數
credential = DefaultAzureCredential(require_envvar=True)
```

### Exclude 參數

| 參數 | 預設 | 效果 |
|-----------|---------|--------|
| `exclude_environment_credential` | False | 跳過用環境變數的驗證 |
| `exclude_workload_identity_credential` | False | 跳過 Kubernetes workload identity |
| `exclude_managed_identity_credential` | False | 跳過 managed identity |
| `exclude_shared_token_cache_credential` | False | 跳過共用 token 快取 |
| `exclude_visual_studio_code_credential` | False | 跳過 VS Code credential |
| `exclude_cli_credential` | False | 跳過 Azure CLI |
| `exclude_powershell_credential` | False | 跳過 Azure PowerShell |
| `exclude_developer_cli_credential` | False | 跳過 Azure Developer CLI |
| `exclude_interactive_browser_credential` | **True** | 跳過互動式瀏覽器 |
| `exclude_broker_credential` | False | 跳過 WAM broker |

## get_bearer_token_provider

把 credential 包成一個會回傳 bearer token 字串的 callable 的 helper。對 OpenAI SDK 和其他非 Azure SDK 的 client 來說不可或缺：

```python
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

credential = DefaultAzureCredential()
token_provider = get_bearer_token_provider(
    credential, "https://cognitiveservices.azure.com/.default"
)

# 搭配 OpenAI SDK 使用
from openai import AzureOpenAI

with AzureOpenAI(
    azure_endpoint="https://<resource>.openai.azure.com/",
    azure_ad_token_provider=token_provider,
    api_version="2024-10-21",
) as client:
    # response = client.chat.completions.create(...)
    ...
```

## Credential 類型

### Credential Chain

| Credential | 使用情境 |
|------------|----------|
| `DefaultAzureCredential` | 大多數情境：自動偵測環境 |
| `ChainedTokenCredential` | 明確指定順序的自訂 credential chain |

### 託管在 Azure 的應用程式

| Credential | 使用情境 |
|------------|----------|
| `EnvironmentCredential` | 透過 AZURE_CLIENT_SECRET / AZURE_CLIENT_CERTIFICATE_PATH 環境變數驗證 |
| `ManagedIdentityCredential` | Azure VM、App Service、Functions、AKS、Arc、Service Fabric |
| `WorkloadIdentityCredential` | 搭配 Microsoft Entra Workload ID 的 Kubernetes |

### Service Principal

| Credential | 使用情境 |
|------------|----------|
| `ClientSecretCredential` | 使用 client secret 的 service principal |
| `CertificateCredential` | 使用 PEM/PKCS12 憑證的 service principal |
| `ClientAssertionCredential` | 使用簽署過的 JWT assertion 的 service principal |
| `AzurePipelinesCredential` | 使用 workload identity federation 的 Azure Pipelines |
| `OnBehalfOfCredential` | 中介層的 on-behalf-of 流程（委派使用者身分） |

### 使用者驗證

| Credential | 使用情境 |
|------------|----------|
| `InteractiveBrowserCredential` | 互動式瀏覽器 OAuth 登入 |
| `DeviceCodeCredential` | 無頭／SSH 的 device code 流程 |
| `AuthorizationCodeCredential` | 事先取得的 authorization code |

### 開發者工具

| Credential | 使用情境 |
|------------|----------|
| `AzureCliCredential` | `az login` |
| `AzureDeveloperCliCredential` | `azd auth login` |
| `AzurePowerShellCredential` | `Connect-AzAccount` |
| `VisualStudioCodeCredential` | VS Code 的 Azure Resources 擴充套件 |

## 特定 Credential 範例

### ManagedIdentityCredential

給託管在 Azure 的資源用（VM、App Service、Functions、AKS）：

```python
from azure.identity import ManagedIdentityCredential

# System-assigned managed identity
credential = ManagedIdentityCredential()

# User-assigned managed identity（client_id、object_id 或 resource_id）
credential = ManagedIdentityCredential(
    client_id="<user-assigned-mi-client-id>"
)
# 這樣也可以：
# credential = ManagedIdentityCredential(object_id="<object-id>")
# credential = ManagedIdentityCredential(resource_id="<resource-id>")
```

### ClientSecretCredential

```python
import os
from azure.identity import ClientSecretCredential

credential = ClientSecretCredential(
    tenant_id=os.environ["AZURE_TENANT_ID"],
    client_id=os.environ["AZURE_CLIENT_ID"],
    client_secret=os.environ["AZURE_CLIENT_SECRET"],
)
```

### CertificateCredential

> **注意：** 類別名稱是 `CertificateCredential`，**不是** `ClientCertificateCredential`。

```python
from azure.identity import CertificateCredential

# 從檔案路徑
credential = CertificateCredential(
    tenant_id="<tenant-id>",
    client_id="<client-id>",
    certificate_path="/path/to/cert.pem",
)

# 從 bytes 加密碼
credential = CertificateCredential(
    tenant_id="<tenant-id>",
    client_id="<client-id>",
    certificate_data=cert_bytes,
    password="<cert-password>",
    send_certificate_chain=True,  # SNI 驗證必須設定
)
```

### AzureCliCredential

```python
from azure.identity import AzureCliCredential

credential = AzureCliCredential()
# 限制 tenant
credential = AzureCliCredential(tenant_id="<tenant-id>")
```

### ChainedTokenCredential

自訂 credential chain：

```python
from azure.identity import (
    ChainedTokenCredential,
    ManagedIdentityCredential,
    AzureCliCredential,
)

# 先試 managed identity，失敗再退回 CLI
credential = ChainedTokenCredential(
    ManagedIdentityCredential(client_id="<user-assigned-mi-client-id>"),
    AzureCliCredential(),
)
```

### WorkloadIdentityCredential

給有 workload identity 的 Azure Kubernetes Service 用：

```python
from azure.identity import WorkloadIdentityCredential

# 從 AZURE_TENANT_ID、AZURE_CLIENT_ID、AZURE_FEDERATED_TOKEN_FILE 讀取
credential = WorkloadIdentityCredential()

# 或明確設定
credential = WorkloadIdentityCredential(
    tenant_id="<tenant-id>",
    client_id="<client-id>",
    token_file_path="/var/run/secrets/azure/tokens/azure-identity-token",
)
```

### DeviceCodeCredential

給無頭裝置用（IoT、SSH、CLI 工具）：

```python
from azure.identity import DeviceCodeCredential

credential = DeviceCodeCredential()
# 預設會把 device code 提示印到 stdout

# 搭配自訂的提示 callback
def prompt_callback(verification_uri, user_code, expires_on):
    print(f"Go to {verification_uri} and enter code {user_code}")

credential = DeviceCodeCredential(
    client_id="<client-id>",
    prompt_callback=prompt_callback,
)
```

### InteractiveBrowserCredential

給互動式 OAuth 瀏覽器登入用：

```python
from azure.identity import InteractiveBrowserCredential

credential = InteractiveBrowserCredential()

# 指定 tenant 和 client
credential = InteractiveBrowserCredential(
    tenant_id="<tenant-id>",
    client_id="<client-id>",
)
```

### OnBehalfOfCredential

給需要傳遞使用者身分的中介層服務用：

```python
from azure.identity import OnBehalfOfCredential

credential = OnBehalfOfCredential(
    tenant_id="<tenant-id>",
    client_id="<client-id>",
    client_secret="<client-secret>",
    user_assertion="<access-token-from-client>",
)
```

### AzurePipelinesCredential

給使用 workload identity federation 的 Azure DevOps pipeline 用：

```python
import os
from azure.identity import AzurePipelinesCredential

credential = AzurePipelinesCredential(
    tenant_id="<tenant-id>",
    client_id="<client-id>",
    service_connection_id="<service-connection-id>",
    system_access_token=os.environ["SYSTEM_ACCESSTOKEN"],
)
```

## 直接取得 Token

```python
from azure.identity import DefaultAzureCredential

with DefaultAzureCredential() as credential:
    # 取得特定 scope 的 token
    token = credential.get_token("https://management.azure.com/.default")
    print(f"Token expires: {token.expires_on}")

    # 給 Azure Database for PostgreSQL 用
    token = credential.get_token("https://ossrdbms-aad.database.windows.net/.default")
```

## 非同步 Credential

非同步的 credential 在 `azure.identity.aio` 裡。一定要關閉它們，或用 `async with`：

```python
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient

async def main():
    # 建議：credential 和 client 都用非同步 context manager
    async with DefaultAzureCredential() as credential:
        async with BlobServiceClient(
            account_url="https://<account>.blob.core.windows.net",
            credential=credential,
        ) as client:
            # ... 非同步操作
            pass
```

> 非同步的 `get_bearer_token_provider` 在 `azure.identity.aio.get_bearer_token_provider`。

## 主權雲端

用 `AzureAuthorityHosts` 或 `AZURE_AUTHORITY_HOST` 環境變數：

```python
from azure.identity import DefaultAzureCredential, AzureAuthorityHosts

# Azure Government
credential = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_GOVERNMENT)

# Azure China
credential = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_CHINA)
```

| 常數 | Authority |
|----------|-----------|
| `AzureAuthorityHosts.AZURE_PUBLIC_CLOUD` | `login.microsoftonline.com`（預設） |
| `AzureAuthorityHosts.AZURE_GOVERNMENT` | `login.microsoftonline.us` |
| `AzureAuthorityHosts.AZURE_CHINA` | `login.chinacloudapi.cn` |

## 持久化 Token 快取

用 `TokenCachePersistenceOptions` 選擇啟用磁碟快取：

```python
from azure.identity import DefaultAzureCredential, TokenCachePersistenceOptions

credential = DefaultAzureCredential(
    cache_persistence_options=TokenCachePersistenceOptions()
)

# 允許退回未加密的儲存（正式環境不建議）
credential = DefaultAzureCredential(
    cache_persistence_options=TokenCachePersistenceOptions(allow_unencrypted_storage=True)
)
```

儲存位置：Windows (DPAPI)、macOS (Keychain)、Linux (Keyring)。

## 多 Tenant 支援

允許取得已設定的 tenant 之外的其他 tenant 的 token：

```python
from azure.identity import ClientSecretCredential

credential = ClientSecretCredential(
    tenant_id="<home-tenant>",
    client_id="<client-id>",
    client_secret="<secret>",
    additionally_allowed_tenants=["<other-tenant>", "*"],  # "*" 允許任何 tenant
)
```

## 錯誤處理

```python
from azure.identity import DefaultAzureCredential, CredentialUnavailableError
from azure.core.exceptions import ClientAuthenticationError

with DefaultAzureCredential() as credential:
    try:
        token = credential.get_token("https://management.azure.com/.default")
    except CredentialUnavailableError:
        # chain 裡沒有任何 credential 能嘗試驗證
        pass
    except ClientAuthenticationError as e:
        # 有嘗試驗證但失敗了
        # e.message 包含 chain 裡每個 credential 的詳細資訊
        pass
```

## Logging

啟用驗證 logging 來除錯：

```python
import logging

# 啟用詳細的 Azure Identity logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("azure.identity")
logger.setLevel(logging.DEBUG)
```

```bash
# 或用環境變數
AZURE_LOG_LEVEL=debug
```

## Credential 選擇矩陣

| 環境 | 建議的 Credential |
|-------------|------------------------|
| 本機開發 | `DefaultAzureCredential`（會用 Azure CLI） |
| Azure App Service | `DefaultAzureCredential`（會用 Managed Identity） |
| Azure Functions | `DefaultAzureCredential`（會用 Managed Identity） |
| Azure Kubernetes Service | `WorkloadIdentityCredential` |
| Azure VM | `DefaultAzureCredential`（會用 Managed Identity） |
| CI/CD Pipeline | `EnvironmentCredential` 或 `AzurePipelinesCredential` |
| 桌面 App | `InteractiveBrowserCredential` |
| CLI／無頭工具 | `DeviceCodeCredential` |
| 中介層服務 | `OnBehalfOfCredential` |

## 最佳實務

1. **同步或非同步選一種，並保持一致。** 同一條呼叫路徑裡不要混用 `azure.xxx` 的同步 client 和 `azure.xxx.aio` 的非同步 client。每個 module 選一種模式。
2. **把 credential 當 context manager 用**（`with DefaultAzureCredential() as credential:`），特別是它們擁有你想清掉的 token 快取／HTTP transport 時；非同步的話，對來自 `azure.identity.aio` 的 credential 用 `async with`。
3. **在本機跑的程式碼用 `DefaultAzureCredential`。** 在 Azure 上跑的程式碼用特定的 token credential。
4. **絕對不要寫死憑證**，用環境變數或 managed identity
5. **正式環境的 Azure 部署優先用 managed identity**
6. **非 Azure SDK 的 client（OpenAI、REST API）用 `get_bearer_token_provider`**
7. **需要自訂 credential 順序時用 `ChainedTokenCredential`**
8. **user-assigned managed identity 要設定 `AZURE_CLIENT_ID`**（object ID 和 resource ID 也是有效的識別碼）
9. **排除不用的 credential**，加快 `DefaultAzureCredential` 的驗證速度
10. **用 `CertificateCredential`**（不是 `ClientCertificateCredential`，這個名稱不存在）
11. **長時間執行的服務要啟用 `cache_persistence_options`**，減少 token 請求
12. **重複使用 credential 實例**：同一個 credential 可以在多個 client 之間共用

## 參考連結

| 資源 | URL |
|----------|-----|
| PyPI Package | https://pypi.org/project/azure-identity/ |
| API Reference | https://learn.microsoft.com/python/api/azure-identity |
| GitHub Source | https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity |
| Credential Chains | https://aka.ms/azsdk/python/identity/credential-chains |

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打的功能、各 operation group 的涵蓋範圍，以及正式環境檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 次要／進階情境的專屬非主打範例。 |
