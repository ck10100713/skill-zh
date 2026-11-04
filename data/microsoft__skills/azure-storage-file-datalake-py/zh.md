---
name: azure-storage-file-datalake-py
description: |
  Python 版的 Azure Data Lake Storage Gen2 SDK。用於階層式檔案系統、大數據分析，以及檔案／目錄操作。
  Triggers: "data lake", "DataLakeServiceClient", "FileSystemClient", "ADLS Gen2", "hierarchical namespace".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-storage-file-datalake
---

# Python 版 Azure Data Lake Storage Gen2 SDK

給大數據分析工作負載用的階層式檔案系統。

## 安裝

```bash
pip install azure-storage-file-datalake azure-identity
```

## 環境變數

```bash
AZURE_STORAGE_ACCOUNT_URL=https://<account>.dfs.core.windows.net  # 所有驗證方式都必填
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
from azure.storage.filedatalake import DataLakeServiceClient

# 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在 production 直接用特定的 credential：
# See https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()
account_url = "https://<account>.dfs.core.windows.net"

with DataLakeServiceClient(account_url=account_url, credential=credential) as service_client:
    # 在這裡使用 service_client（各種操作請看後面的章節）
    ...
```

## Client 階層

| Client | 用途 |
|--------|---------|
| `DataLakeServiceClient` | Account 層級的操作 |
| `FileSystemClient` | Container（檔案系統）操作 |
| `DataLakeDirectoryClient` | 目錄操作 |
| `DataLakeFileClient` | 檔案操作 |

## 檔案系統操作

```python
# 建立檔案系統（container）
file_system_client = service_client.create_file_system("myfilesystem")

# 取得既有的
file_system_client = service_client.get_file_system_client("myfilesystem")

# 刪除
service_client.delete_file_system("myfilesystem")

# 列出檔案系統
for fs in service_client.list_file_systems():
    print(fs.name)
```

## 目錄操作

```python
file_system_client = service_client.get_file_system_client("myfilesystem")

# 建立目錄
directory_client = file_system_client.create_directory("mydir")

# 建立巢狀目錄
directory_client = file_system_client.create_directory("path/to/nested/dir")

# 取得目錄 client
directory_client = file_system_client.get_directory_client("mydir")

# 刪除目錄
directory_client.delete_directory()

# 重新命名／移動目錄
directory_client.rename_directory(new_name="myfilesystem/newname")
```

## 檔案操作

### 上傳檔案

```python
# 取得檔案 client
file_client = file_system_client.get_file_client("path/to/file.txt")

# 從本機檔案上傳
with open("local-file.txt", "rb") as data:
    file_client.upload_data(data, overwrite=True)

# 上傳 bytes
file_client.upload_data(b"Hello, Data Lake!", overwrite=True)

# 附加資料（用於大檔案）
file_client.append_data(data=b"chunk1", offset=0, length=6)
file_client.append_data(data=b"chunk2", offset=6, length=6)
file_client.flush_data(12)  # 提交資料
```

### 下載檔案

```python
file_client = file_system_client.get_file_client("path/to/file.txt")

# 下載全部內容
download = file_client.download_file()
content = download.readall()

# 下載到檔案
with open("downloaded.txt", "wb") as f:
    download = file_client.download_file()
    download.readinto(f)

# 下載指定範圍
download = file_client.download_file(offset=0, length=100)
```

### 刪除檔案

```python
file_client.delete_file()
```

## 列出內容

```python
# 列出路徑（檔案和目錄）
for path in file_system_client.get_paths():
    print(f"{'DIR' if path.is_directory else 'FILE'}: {path.name}")

# 列出目錄裡的路徑
for path in file_system_client.get_paths(path="mydir"):
    print(path.name)

# 遞迴列出
for path in file_system_client.get_paths(path="mydir", recursive=True):
    print(path.name)
```

## 檔案／目錄屬性

```python
# 取得屬性
properties = file_client.get_file_properties()
print(f"Size: {properties.size}")
print(f"Last modified: {properties.last_modified}")

# 設定 metadata
file_client.set_metadata(metadata={"processed": "true"})
```

## 存取控制（ACL）

```python
# 取得 ACL
acl = directory_client.get_access_control()
print(f"Owner: {acl['owner']}")
print(f"Permissions: {acl['permissions']}")

# 設定 ACL
directory_client.set_access_control(
    owner="user-id",
    permissions="rwxr-x---"
)

# 更新 ACL 項目
from azure.storage.filedatalake import AccessControlChangeResult
directory_client.update_access_control_recursive(
    acl="user:user-id:rwx"
)
```

## 非同步 Client

```python
from azure.storage.filedatalake.aio import DataLakeServiceClient
from azure.identity.aio import DefaultAzureCredential

async def datalake_operations():
    async with DefaultAzureCredential() as credential:
        async with DataLakeServiceClient(
            account_url="https://<account>.dfs.core.windows.net",
            credential=credential
        ) as service_client:
            file_system_client = service_client.get_file_system_client("myfilesystem")
            file_client = file_system_client.get_file_client("test.txt")
            
            await file_client.upload_data(b"async content", overwrite=True)
            
            download = await file_client.download_file()
            content = await download.readall()

import asyncio
asyncio.run(datalake_operations())
```

## 最佳實務

1. **同步或非同步選一個，然後保持一致。** 同一條呼叫路徑裡，不要混用 `azure.storage.filedatalake` 同步 client 和 `azure.storage.filedatalake.aio` 非同步 client。每個 module 只選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都用 `with DataLakeServiceClient(...) as client:`（同步）或 `async with DataLakeServiceClient(...) as client:`（非同步）包起來。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，token 和 transport 才會清乾淨。
3. **用 `DefaultAzureCredential`**，在本機開發和 Azure 之間都能用同一套驗證（盡量避免 connection string／API key）。
4. 要有檔案系統語意，就**用 hierarchical namespace**
5. 大檔案上傳**用 `append_data` + `flush_data`**
6. **在目錄層級設定 ACL**，讓子項目繼承
7. 高吞吐量的情境**用非同步 client**
8. 要完整列出目錄，**用 `get_paths` 搭配 `recursive=True`**
9. 自訂檔案屬性要**設定 metadata**
10. 簡單的物件儲存情境，**考慮改用 Blob API**

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主要的能力、operation group 涵蓋範圍，以及 production 檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 次要／進階情境的專屬非主要流程範例。 |
