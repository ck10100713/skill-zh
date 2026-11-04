---
name: azure-containerregistry-py
description: |
  Azure Container Registry SDK for Python。用於管理容器映像檔、artifact 和 repository。
  Triggers: "azure-containerregistry", "ContainerRegistryClient", "container images", "docker registry", "ACR".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-containerregistry
---

# Azure Container Registry SDK for Python

在 Azure Container Registry 裡管理容器映像檔、artifact 和 repository。

## Installation

```bash
pip install azure-containerregistry
```

## Environment Variables

```bash
AZURE_CONTAINERREGISTRY_ENDPOINT=https://<registry-name>.azurecr.io  # 所有驗證方式都需要
AZURE_TOKEN_CREDENTIALS=prod # 只有在 production 使用 DefaultAzureCredential 時才需要
```

## Authentication & Lifecycle

> **🔑 下面每個程式範例都適用兩條規則：**
>
> 1. **優先用 `DefaultAzureCredential`。** 它在本機（Azure CLI / VS Code / Developer CLI）和 Azure 上（managed identity、workload identity）都能跑，程式碼不用改。避免用 connection string、account/API key，因為它們會繞過 Entra 的稽核和金鑰輪替。
>    - 本機開發：`DefaultAzureCredential` 直接可用。
>    - Production：設定 `AZURE_TOKEN_CREDENTIALS=prod`（或 `AZURE_TOKEN_CREDENTIALS=<specific_credential>`），把 credential chain 限縮在 production 安全的 credential。
> 2. **每個 client 都要包在 context manager 裡**，這樣 HTTP transport、socket 和 token cache 會確實被釋放：
>    - 同步：`with <Client>(...) as client:`
>    - 非同步：`async with <Client>(...) as client:` **而且** `async with DefaultAzureCredential() as credential:`（來自 `azure.identity.aio`）
>
> 範例程式碼可能會省略這部分設定，但 production 程式碼一定要兩條規則都遵守。

### Entra ID (Recommended)

```python
import os
from azure.containerregistry import ContainerRegistryClient
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential

# 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在 production 直接用指定的 credential：
# 參考 https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()

with ContainerRegistryClient(
    endpoint=os.environ["AZURE_CONTAINERREGISTRY_ENDPOINT"],
    credential=credential
) as client:
    # 在這裡使用 client（各項操作見後面的章節）
    ...
```

### Anonymous Access (Public Registry)

```python
from azure.containerregistry import ContainerRegistryClient

with ContainerRegistryClient(
    endpoint="https://mcr.microsoft.com",
    credential=None,
    audience="https://mcr.microsoft.com"
) as client:
    # 在這裡使用 client（各項操作見後面的章節）
    ...
```

## List Repositories

```python
with ContainerRegistryClient(endpoint, DefaultAzureCredential()) as client:
    for repository in client.list_repository_names():
        print(repository)
```

## Repository Operations

### Get Repository Properties

```python
properties = client.get_repository_properties("my-image")
print(f"Created: {properties.created_on}")
print(f"Modified: {properties.last_updated_on}")
print(f"Manifests: {properties.manifest_count}")
print(f"Tags: {properties.tag_count}")
```

### Update Repository Properties

```python
from azure.containerregistry import RepositoryProperties

client.update_repository_properties(
    "my-image",
    properties=RepositoryProperties(
        can_delete=False,
        can_write=False
    )
)
```

### Delete Repository

```python
client.delete_repository("my-image")
```

## List Tags

```python
for tag in client.list_tag_properties("my-image"):
    print(f"{tag.name}: {tag.created_on}")
```

### Filter by Order

```python
from azure.containerregistry import ArtifactTagOrder

# 最新的在前
for tag in client.list_tag_properties(
    "my-image",
    order_by=ArtifactTagOrder.LAST_UPDATED_ON_DESCENDING
):
    print(f"{tag.name}: {tag.last_updated_on}")
```

## Manifest Operations

### List Manifests

```python
from azure.containerregistry import ArtifactManifestOrder

for manifest in client.list_manifest_properties(
    "my-image",
    order_by=ArtifactManifestOrder.LAST_UPDATED_ON_DESCENDING
):
    print(f"Digest: {manifest.digest}")
    print(f"Tags: {manifest.tags}")
    print(f"Size: {manifest.size_in_bytes}")
```

### Get Manifest Properties

```python
manifest = client.get_manifest_properties("my-image", "latest")
print(f"Digest: {manifest.digest}")
print(f"Architecture: {manifest.architecture}")
print(f"OS: {manifest.operating_system}")
```

### Update Manifest Properties

```python
from azure.containerregistry import ArtifactManifestProperties

client.update_manifest_properties(
    "my-image",
    "latest",
    properties=ArtifactManifestProperties(
        can_delete=False,
        can_write=False
    )
)
```

### Delete Manifest

```python
# 用 digest 刪除
client.delete_manifest("my-image", "sha256:abc123...")

# 用 tag 刪除
manifest = client.get_manifest_properties("my-image", "old-tag")
client.delete_manifest("my-image", manifest.digest)
```

## Tag Operations

### Get Tag Properties

```python
tag = client.get_tag_properties("my-image", "latest")
print(f"Digest: {tag.digest}")
print(f"Created: {tag.created_on}")
```

### Delete Tag

```python
client.delete_tag("my-image", "old-tag")
```

## Upload and Download Artifacts

```python
from azure.containerregistry import ContainerRegistryClient

with ContainerRegistryClient(endpoint, DefaultAzureCredential()) as client:
    # 下載 manifest
    manifest = client.download_manifest("my-image", "latest")
    print(f"Media type: {manifest.media_type}")
    print(f"Digest: {manifest.digest}")

    # 下載 blob
    blob = client.download_blob("my-image", "sha256:abc123...")
    with open("layer.tar.gz", "wb") as f:
        for chunk in blob:
            f.write(chunk)
```

## Async Client

```python
from azure.containerregistry.aio import ContainerRegistryClient
from azure.identity.aio import DefaultAzureCredential

async def list_repos():
    async with DefaultAzureCredential() as credential:
        async with ContainerRegistryClient(endpoint, credential) as client:
            async for repo in client.list_repository_names():
                print(repo)
```

## Clean Up Old Images

```python
from datetime import datetime, timedelta, timezone

cutoff = datetime.now(timezone.utc) - timedelta(days=30)

for manifest in client.list_manifest_properties("my-image"):
    if manifest.last_updated_on < cutoff and not manifest.tags:
        print(f"Deleting {manifest.digest}")
        client.delete_manifest("my-image", manifest.digest)
```

## Client Operations

| Operation | Description |
|-----------|-------------|
| `list_repository_names` | 列出所有 repository |
| `get_repository_properties` | 取得 repository 的 metadata |
| `delete_repository` | 刪除 repository 和所有映像檔 |
| `list_tag_properties` | 列出 repository 裡的 tag |
| `get_tag_properties` | 取得 tag 的 metadata |
| `delete_tag` | 刪除特定 tag |
| `list_manifest_properties` | 列出 repository 裡的 manifest |
| `get_manifest_properties` | 取得 manifest 的 metadata |
| `delete_manifest` | 用 digest 刪除 manifest |
| `download_manifest` | 下載 manifest 內容 |
| `download_blob` | 下載 layer blob |

## Best Practices

1. **同步或非同步擇一，並保持一致。** 同一條呼叫路徑裡不要混用 `azure.xxx` 同步 client 和 `azure.xxx.aio` 非同步 client。每個 module 只選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都包在 `with Client(...) as client:`（同步）或 `async with Client(...) as client:`（非同步）裡。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，這樣 token 和 transport 才會被清掉。
3. **production 驗證用 Microsoft Entra ID**
4. **用 digest 刪除，不要用 tag**，避免留下孤立的映像檔
5. **用 can_delete=False 鎖住 production 映像檔**
6. **定期清理沒有 tag 的 manifest**
7. **高吞吐量操作用非同步 client**
8. **依 last_updated 排序**，找出最新/最舊的映像檔
9. **刪除前檢查 manifest.tags**，避免誤刪有 tag 的映像檔

## Reference Files

| File | Contents |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打功能、operation group 涵蓋範圍，以及 production 檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 次要與進階情境的專屬非主打範例。 |
