---
name: azure-storage-blob-py
description: |
  Python 版的 Azure Blob Storage SDK。用於上傳、下載、列出 blob、管理 container 和 blob 生命週期。
  Triggers: "blob storage", "BlobServiceClient", "ContainerClient", "BlobClient", "upload blob", "download blob".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-storage-blob
---

# Python 版 Azure Blob Storage SDK

Azure Blob Storage 的 client library，Blob Storage 是用來存放非結構化資料的物件儲存。

## 安裝

```bash
pip install azure-storage-blob azure-identity
```

## 環境變數

```bash
AZURE_STORAGE_ACCOUNT_NAME=<your-storage-account>  # 所有驗證方式都必填
# 或用完整 URL
AZURE_STORAGE_ACCOUNT_URL=https://<account>.blob.core.windows.net  # account name 的替代方案
AZURE_TOKEN_CREDENTIALS=prod # 只有在 production 使用 DefaultAzureCredential 時才需要
```

## 驗證與生命週期

> **🔑 下面每個程式碼範例都適用兩條規則：**
>
> 1. **優先用 `DefaultAzureCredential`。** 它在本機（Azure CLI / VS Code / Developer CLI）和 Azure 上（managed identity、workload identity）都能用，不用改程式碼。避免用 connection string、account key 或 API key，它們會繞過 Entra 的稽核和輪替。
>    - 本機開發：直接用 `DefaultAzureCredential` 就好。
>    - Production：設定 `AZURE_TOKEN_CREDENTIALS=prod`（或 `AZURE_TOKEN_CREDENTIALS=<specific_credential>`），把 credential chain 限縮在 production 安全的 credential。
> 2. **每個 client 都用 context manager 包起來**，這樣 HTTP transport、socket 和 token cache 才會確實釋放：
>    - 同步：`with <Client>(...) as client:`
>    - 非同步：`async with <Client>(...) as client:` **而且** `async with DefaultAzureCredential() as credential:`（來自 `azure.identity.aio`）
>
> 範例片段可能會簡化這段設定，但 production 的程式碼一定要兩條規則都遵守。

```python
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient

# 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在 production 直接用特定的 credential：
# See https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()
account_url = "https://<account>.blob.core.windows.net"

with BlobServiceClient(account_url, credential=credential) as blob_service_client:
    # 在這裡使用 blob_service_client（各種操作請看後面的章節）
    ...
```

## Client 階層

| Client | 用途 | 取得方式 |
|--------|---------|----------|
| `BlobServiceClient` | Account 層級的操作 | 直接建立實例 |
| `ContainerClient` | Container 操作 | `blob_service_client.get_container_client()` |
| `BlobClient` | 單一 blob 的操作 | `container_client.get_blob_client()` |

## 核心工作流程

### 建立 Container

```python
container_client = blob_service_client.get_container_client("mycontainer")
container_client.create_container()
```

### 上傳 Blob

```python
# 從檔案路徑
blob_client = blob_service_client.get_blob_client(
    container="mycontainer",
    blob="sample.txt"
)

with open("./local-file.txt", "rb") as data:
    blob_client.upload_blob(data, overwrite=True)

# 從 bytes/字串
blob_client.upload_blob(b"Hello, World!", overwrite=True)

# 從 stream
import io
stream = io.BytesIO(b"Stream content")
blob_client.upload_blob(stream, overwrite=True)
```

### 下載 Blob

```python
blob_client = blob_service_client.get_blob_client(
    container="mycontainer",
    blob="sample.txt"
)

# 下載到檔案
with open("./downloaded.txt", "wb") as file:
    download_stream = blob_client.download_blob()
    file.write(download_stream.readall())

# 下載到記憶體
download_stream = blob_client.download_blob()
content = download_stream.readall()  # bytes

# 讀進既有的 buffer
stream = io.BytesIO()
num_bytes = blob_client.download_blob().readinto(stream)
```

### 列出 Blob

```python
container_client = blob_service_client.get_container_client("mycontainer")

# 列出所有 blob
for blob in container_client.list_blobs():
    print(f"{blob.name} - {blob.size} bytes")

# 用 prefix 列出（類似資料夾）
for blob in container_client.list_blobs(name_starts_with="logs/"):
    print(blob.name)

# 走訪 blob 階層（虛擬目錄）
for item in container_client.walk_blobs(delimiter="/"):
    if item.get("prefix"):
        print(f"Directory: {item['prefix']}")
    else:
        print(f"Blob: {item.name}")
```

### 刪除 Blob

```python
blob_client.delete_blob()

# 連同 snapshot 一起刪除
blob_client.delete_blob(delete_snapshots="include")
```

## 效能調校

```python
# 為大型上傳／下載設定 chunk 大小
with BlobClient(
    account_url=account_url,
    container_name="mycontainer",
    blob_name="large-file.zip",
    credential=credential,
    max_block_size=4 * 1024 * 1024,  # 4 MiB 的 block
    max_single_put_size=64 * 1024 * 1024  # 單次上傳上限 64 MiB
) as blob_client:
    # 平行上傳
    blob_client.upload_blob(data, max_concurrency=4)

    # 平行下載
    download_stream = blob_client.download_blob(max_concurrency=4)
```

## SAS Token（User Delegation）

SAS token 要用 Microsoft Entra ID 簽署的 **user delegation key** 來產生，絕對不要用 account key。這樣 SAS 的核發才會綁在 Entra 的稽核和輪替機制上。

```python
from datetime import datetime, timedelta, timezone
from azure.identity import DefaultAzureCredential
from azure.storage.blob import (
    BlobServiceClient,
    BlobSasPermissions,
    generate_blob_sas,
)

now = datetime.now(timezone.utc)
account_url = "https://<account>.blob.core.windows.net"

with BlobServiceClient(account_url, credential=DefaultAzureCredential()) as service:
    # 取得 user delegation key（最長有效 7 天）。呼叫者需要在 storage account 上
    # 擁有 "Storage Blob Delegator" 角色。
    udk = service.get_user_delegation_key(
        key_start_time=now,
        key_expiry_time=now + timedelta(hours=1),
    )

    sas_token = generate_blob_sas(
        account_name="<account>",
        container_name="mycontainer",
        blob_name="sample.txt",
        user_delegation_key=udk,
        permission=BlobSasPermissions(read=True),
        expiry=now + timedelta(hours=1),
    )

blob_url = f"{account_url}/mycontainer/sample.txt?{sas_token}"
```

## Blob 屬性與 Metadata

```python
# 取得屬性
properties = blob_client.get_blob_properties()
print(f"Size: {properties.size}")
print(f"Content-Type: {properties.content_settings.content_type}")
print(f"Last modified: {properties.last_modified}")

# 設定 metadata
blob_client.set_blob_metadata(metadata={"category": "logs", "year": "2024"})

# 設定 content type
from azure.storage.blob import ContentSettings
blob_client.set_http_headers(
    content_settings=ContentSettings(content_type="application/json")
)
```

## 非同步 Client

```python
from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient

async def upload_async():
    async with DefaultAzureCredential() as credential:
        async with BlobServiceClient(account_url, credential=credential) as client:
            blob_client = client.get_blob_client("mycontainer", "sample.txt")
            
            with open("./file.txt", "rb") as data:
                await blob_client.upload_blob(data, overwrite=True)

# 非同步下載
async def download_async():
    async with BlobServiceClient(account_url, credential=credential) as client:
        blob_client = client.get_blob_client("mycontainer", "sample.txt")
        
        stream = await blob_client.download_blob()
        data = await stream.readall()
```

## 最佳實務

1. **同步或非同步選一個，然後保持一致。** 同一條呼叫路徑裡，不要混用 `azure.storage.blob` 同步 client 和 `azure.storage.blob.aio` 非同步 client。每個 module 只選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都用 `with BlobServiceClient(...) as client:`（同步）或 `async with BlobServiceClient(...) as client:`（非同步）包起來。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，token 和 transport 才會清乾淨。
3. 在本機跑的程式碼**用 `DefaultAzureCredential`**（不要用 connection string）。在 Azure 上跑的程式碼用特定的 token credential。
4. 重新上傳時，**明確設定 `overwrite=True`**
5. 大檔案傳輸**用 `max_concurrency`**
6. **優先用 `readinto()`** 而不是 `readall()`，比較省記憶體
7. 階層式列出**用 `walk_blobs()`**
8. 給網頁提供的 blob **設定適當的 content type**

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 能力索引，對應主要流程和非主要流程的參考文件。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 專屬的非主要流程範例（metadata/屬性和非同步模式）。 |
