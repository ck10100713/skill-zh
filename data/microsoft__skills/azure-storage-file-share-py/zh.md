---
name: azure-storage-file-share-py
description: |-
  Python 版的 Azure Storage File Share SDK。用於雲端的 SMB 檔案共用、目錄和檔案操作。
  Triggers: "azure-storage-file-share", "ShareServiceClient", "ShareClient", "file share", "SMB".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# Python 版 Azure Storage File Share SDK

管理 SMB 檔案共用，適用於 cloud-native 和 lift-and-shift 的情境。

## 安裝

```bash
pip install azure-storage-file-share
```

## 環境變數

```bash
AZURE_STORAGE_ACCOUNT_URL=https://<account>.file.core.windows.net  # Entra ID 驗證必填
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
from azure.storage.fileshare import ShareServiceClient
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential

# 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在 production 直接用特定的 credential：
# See https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()

with ShareServiceClient(
    account_url=os.environ["AZURE_STORAGE_ACCOUNT_URL"],
    credential=credential
) as service:
    # 在這裡使用 service（各種操作請看後面的章節）
    ...
```

## Share 操作

### 建立 Share

```python
share = service.create_share("my-share")
```

### 列出 Share

```python
for share in service.list_shares():
    print(f"{share.name}: {share.quota} GB")
```

### 取得 Share Client

```python
share_client = service.get_share_client("my-share")
```

### 刪除 Share

```python
service.delete_share("my-share")
```

## 目錄操作

### 建立目錄

```python
share_client = service.get_share_client("my-share")
share_client.create_directory("my-directory")

# 巢狀目錄
share_client.create_directory("my-directory/sub-directory")
```

### 列出目錄和檔案

```python
directory_client = share_client.get_directory_client("my-directory")

for item in directory_client.list_directories_and_files():
    if item["is_directory"]:
        print(f"[DIR] {item['name']}")
    else:
        print(f"[FILE] {item['name']} ({item['size']} bytes)")
```

### 刪除目錄

```python
share_client.delete_directory("my-directory")
```

## 檔案操作

### 上傳檔案

```python
file_client = share_client.get_file_client("my-directory/file.txt")

# 從字串
file_client.upload_file("Hello, World!")

# 從檔案
with open("local-file.txt", "rb") as f:
    file_client.upload_file(f)

# 從 bytes
file_client.upload_file(b"Binary content")
```

### 下載檔案

```python
file_client = share_client.get_file_client("my-directory/file.txt")

# 下載成 bytes
data = file_client.download_file().readall()

# 下載到檔案
with open("downloaded.txt", "wb") as f:
    data = file_client.download_file()
    data.readinto(f)

# 以 chunk 串流
download = file_client.download_file()
for chunk in download.chunks():
    process(chunk)
```

### 取得檔案屬性

```python
properties = file_client.get_file_properties()
print(f"Size: {properties.size}")
print(f"Content type: {properties.content_settings.content_type}")
print(f"Last modified: {properties.last_modified}")
```

### 刪除檔案

```python
file_client.delete_file()
```

### 複製檔案

```python
source_url = "https://account.file.core.windows.net/share/source.txt"
dest_client = share_client.get_file_client("destination.txt")
dest_client.start_copy_from_url(source_url)
```

## Range 操作

### 上傳 Range

```python
# 上傳到特定 range
file_client.upload_range(data=b"content", offset=0, length=7)
```

### 下載 Range

```python
# 下載特定 range
download = file_client.download_file(offset=0, length=100)
data = download.readall()
```

## Snapshot 操作

### 建立 Snapshot

```python
snapshot = share_client.create_snapshot()
print(f"Snapshot: {snapshot['snapshot']}")
```

### 存取 Snapshot

```python
snapshot_client = service.get_share_client(
    "my-share",
    snapshot=snapshot["snapshot"]
)
```

## 非同步 Client

```python
from azure.storage.fileshare.aio import ShareServiceClient
from azure.identity.aio import DefaultAzureCredential

async def upload_file():
    async with DefaultAzureCredential() as credential:
        async with ShareServiceClient(account_url, credential=credential) as service:
            share = service.get_share_client("my-share")
            file_client = share.get_file_client("test.txt")
            
            await file_client.upload_file("Hello!")
```

## Client 類型

| Client | 用途 |
|--------|---------|
| `ShareServiceClient` | Account 層級的操作 |
| `ShareClient` | Share 操作 |
| `ShareDirectoryClient` | 目錄操作 |
| `ShareFileClient` | 檔案操作 |

## 最佳實務

1. **同步或非同步選一個，然後保持一致。** 同一條呼叫路徑裡，不要混用 `azure.storage.fileshare` 同步 client 和 `azure.storage.fileshare.aio` 非同步 client。每個 module 只選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都用 `with ShareServiceClient(...) as client:`（同步）或 `async with ShareServiceClient(...) as client:`（非同步）包起來。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，token 和 transport 才會清乾淨。
3. **用 `DefaultAzureCredential`**，在本機開發和 Azure 之間都能用同一套驗證（盡量避免 connection string／API key）。
4. production **用 Microsoft Entra ID** 搭配 RBAC
5. 大檔案**用 chunks() 串流**，避免記憶體問題
6. 做重大變更之前**先建立 snapshot**
7. **設定 quota**，避免意外的儲存費用
8. 部分更新檔案時**用 range**

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主要的能力、operation group 涵蓋範圍，以及 production 檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 次要／進階情境的專屬非主要流程範例。 |
