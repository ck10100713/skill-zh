---
name: azure-appconfiguration-py
description: |
  Azure App Configuration SDK for Python。用於集中管理設定、feature flag 和動態設定。
  Triggers: "azure-appconfiguration", "AzureAppConfigurationClient", "feature flags", "configuration", "key-value settings".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-appconfiguration
---

# Azure App Configuration SDK for Python

集中管理設定，支援 feature flag 和動態設定。

## Installation

```bash
pip install azure-appconfiguration
```

## Environment Variables

```bash
AZURE_APPCONFIGURATION_ENDPOINT=https://<name>.azconfig.io  # Entra ID 驗證需要
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

```python
import os
from azure.appconfiguration import AzureAppConfigurationClient
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential

# 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在 production 直接用指定的 credential：
# 參考 https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()

with AzureAppConfigurationClient(
    base_url=os.environ["AZURE_APPCONFIGURATION_ENDPOINT"],
    credential=credential
) as client:
    # 在這裡使用 client（各項操作見後面的章節）
    ...
```

## Configuration Settings

### Get Setting

```python
setting = client.get_configuration_setting(key="app:settings:message")
print(f"{setting.key} = {setting.value}")
```

### Get with Label

```python
# Label 可以讓不同環境有不同的值
setting = client.get_configuration_setting(
    key="app:settings:message",
    label="production"
)
```

### Set Setting

```python
from azure.appconfiguration import ConfigurationSetting

setting = ConfigurationSetting(
    key="app:settings:message",
    value="Hello, World!",
    label="development",
    content_type="text/plain",
    tags={"environment": "dev"}
)

client.set_configuration_setting(setting)
```

### Delete Setting

```python
client.delete_configuration_setting(
    key="app:settings:message",
    label="development"
)
```

## List Settings

### All Settings

```python
settings = client.list_configuration_settings()
for setting in settings:
    print(f"{setting.key} [{setting.label}] = {setting.value}")
```

### Filter by Key Prefix

```python
settings = client.list_configuration_settings(
    key_filter="app:settings:*"
)
```

### Filter by Label

```python
settings = client.list_configuration_settings(
    label_filter="production"
)
```

## Feature Flags

### Set Feature Flag

```python
from azure.appconfiguration import ConfigurationSetting
import json

feature_flag = ConfigurationSetting(
    key=".appconfig.featureflag/beta-feature",
    value=json.dumps({
        "id": "beta-feature",
        "enabled": True,
        "conditions": {
            "client_filters": []
        }
    }),
    content_type="application/vnd.microsoft.appconfig.ff+json;charset=utf-8"
)

client.set_configuration_setting(feature_flag)
```

### Get Feature Flag

```python
setting = client.get_configuration_setting(
    key=".appconfig.featureflag/beta-feature"
)
flag_data = json.loads(setting.value)
print(f"Feature enabled: {flag_data['enabled']}")
```

### List Feature Flags

```python
flags = client.list_configuration_settings(
    key_filter=".appconfig.featureflag/*"
)
for flag in flags:
    data = json.loads(flag.value)
    print(f"{data['id']}: {'enabled' if data['enabled'] else 'disabled'}")
```

## Read-Only Settings

```python
# 把設定改成唯讀
client.set_read_only(
    configuration_setting=setting,
    read_only=True
)

# 移除唯讀
client.set_read_only(
    configuration_setting=setting,
    read_only=False
)
```

## Snapshots

### Create Snapshot

```python
from azure.appconfiguration import ConfigurationSnapshot, ConfigurationSettingFilter

snapshot = ConfigurationSnapshot(
    name="v1-snapshot",
    filters=[
        ConfigurationSettingFilter(key="app:*", label="production")
    ]
)

created = client.begin_create_snapshot(
    name="v1-snapshot",
    snapshot=snapshot
).result()
```

### List Snapshot Settings

```python
settings = client.list_configuration_settings(
    snapshot_name="v1-snapshot"
)
```

## Async Client

```python
from azure.appconfiguration.aio import AzureAppConfigurationClient
from azure.identity.aio import DefaultAzureCredential

async def main():
    async with DefaultAzureCredential() as credential:
        async with AzureAppConfigurationClient(
            base_url=endpoint,
            credential=credential
        ) as client:
            setting = await client.get_configuration_setting(key="app:message")
            print(setting.value)
```

## Client Operations

| Operation | Description |
|-----------|-------------|
| `get_configuration_setting` | 取得單一設定 |
| `set_configuration_setting` | 建立或更新設定 |
| `delete_configuration_setting` | 刪除設定 |
| `list_configuration_settings` | 搭配 filter 列出設定 |
| `set_read_only` | 鎖定/解鎖設定 |
| `begin_create_snapshot` | 建立某時間點的 snapshot |
| `list_snapshots` | 列出所有 snapshot |

## Best Practices

1. **同步或非同步擇一，並保持一致。** 同一條呼叫路徑裡不要混用 `azure.xxx` 同步 client 和 `azure.xxx.aio` 非同步 client。每個 module 只選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都包在 `with Client(...) as client:`（同步）或 `async with Client(...) as client:`（非同步）裡。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，這樣 token 和 transport 才會被清掉。
3. **用 label** 區分環境（dev、staging、prod）
4. **用 key 前綴**做邏輯分組（app:database:*、app:cache:*）
5. **把 production 設定設成唯讀**，避免意外修改
6. **部署前建立 snapshot**，以便回滾
7. **production 用 Entra ID**，不要用 connection string
8. **長時間執行的應用程式要定期重新整理設定**
9. **用 feature flag** 做漸進式推出和 A/B 測試

## Reference Files

| File | Contents |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打功能、operation group 涵蓋範圍，以及 production 檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 次要與進階情境的專屬非主打範例。 |
