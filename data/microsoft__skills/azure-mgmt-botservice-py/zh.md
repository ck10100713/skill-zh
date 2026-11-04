---
name: azure-mgmt-botservice-py
description: |-
  Azure Bot Service Management SDK for Python。用於建立、管理和設定 Azure Bot Service 資源。
  Triggers: "azure-mgmt-botservice", "AzureBotService", "bot management", "conversational AI", "bot channels".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# Azure Bot Service Management SDK for Python

管理 Azure Bot Service 資源，包括 bot、channel 和連線。

## 安裝

```bash
pip install azure-mgmt-botservice
pip install azure-identity
```

## 環境變數

```bash
AZURE_SUBSCRIPTION_ID=<your-subscription-id>  # 所有認證方式都必填
AZURE_RESOURCE_GROUP=<your-resource-group>  # 所有認證方式都必填
AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境用 DefaultAzureCredential 時才需要
```

## 認證與生命週期

> **🔑 底下每個程式碼範例都適用兩條規則：**
>
> 1. **優先用 `DefaultAzureCredential`。** 它在本機（Azure CLI / VS Code / Developer CLI）和 Azure 上（managed identity、workload identity）都能運作，程式碼不用改。避免用連線字串、帳號/API key，它們會繞過 Entra 的稽核和輪替。
>    - 本機開發：`DefaultAzureCredential` 直接可用。
>    - 正式環境：設 `AZURE_TOKEN_CREDENTIALS=prod`（或 `AZURE_TOKEN_CREDENTIALS=<specific_credential>`），把 credential 鏈限制在適合正式環境的 credential。
> 2. **每個 client 都要包在 context manager 裡**，這樣 HTTP transport、socket 和 token cache 才會確實釋放：
>    - 同步：`with <Client>(...) as client:`
>    - 非同步：`async with <Client>(...) as client:` **而且**要 `async with DefaultAzureCredential() as credential:`（來自 `azure.identity.aio`）
>
> 範例片段可能會簡化這段設定，但正式環境的程式碼一定要遵守這兩條規則。

```python
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.mgmt.botservice import AzureBotService
import os

# 本機開發：DefaultAzureCredential。正式環境：設 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在正式環境直接用特定的 credential：
# 見 https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()

with AzureBotService(
    credential=credential,
    subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"]
) as client:
    # 後續所有操作都用 `client`（見下面的範例）
    ...
```

## 建立 Bot

```python
from azure.mgmt.botservice import AzureBotService
from azure.mgmt.botservice.models import Bot, BotProperties, Sku
from azure.identity import DefaultAzureCredential
import os

resource_group = os.environ["AZURE_RESOURCE_GROUP"]
bot_name = "my-chat-bot"

credential = DefaultAzureCredential()
with AzureBotService(
    credential=credential,
    subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"]
) as client:
    bot = client.bots.create(
        resource_group_name=resource_group,
        resource_name=bot_name,
        parameters=Bot(
            location="global",
            sku=Sku(name="F0"),  # 免費層
            kind="azurebot",
            properties=BotProperties(
                display_name="My Chat Bot",
                description="A conversational AI bot",
                endpoint="https://my-bot-app.azurewebsites.net/api/messages",
                msa_app_id="<your-app-id>",
                msa_app_type="MultiTenant"
            )
        )
    )

print(f"Bot created: {bot.name}")
```

## 取得 Bot 詳細資料

```python
bot = client.bots.get(
    resource_group_name=resource_group,
    resource_name=bot_name
)

print(f"Bot: {bot.properties.display_name}")
print(f"Endpoint: {bot.properties.endpoint}")
print(f"SKU: {bot.sku.name}")
```

## 列出 Resource Group 裡的 Bot

```python
bots = client.bots.list_by_resource_group(resource_group_name=resource_group)

for bot in bots:
    print(f"Bot: {bot.name} - {bot.properties.display_name}")
```

## 列出 Subscription 裡所有 Bot

```python
all_bots = client.bots.list()

for bot in all_bots:
    print(f"Bot: {bot.name} in {bot.id.split('/')[4]}")
```

## 更新 Bot

```python
bot = client.bots.update(
    resource_group_name=resource_group,
    resource_name=bot_name,
    properties=BotProperties(
        display_name="Updated Bot Name",
        description="Updated description"
    )
)
```

## 刪除 Bot

```python
client.bots.delete(
    resource_group_name=resource_group,
    resource_name=bot_name
)
```

## 設定 Channel

### 加入 Teams Channel

```python
from azure.mgmt.botservice.models import (
    BotChannel,
    MsTeamsChannel,
    MsTeamsChannelProperties
)

channel = client.channels.create(
    resource_group_name=resource_group,
    resource_name=bot_name,
    channel_name="MsTeamsChannel",
    parameters=BotChannel(
        location="global",
        properties=MsTeamsChannel(
            properties=MsTeamsChannelProperties(
                is_enabled=True
            )
        )
    )
)
```

### 加入 Direct Line Channel

```python
from azure.mgmt.botservice.models import (
    BotChannel,
    DirectLineChannel,
    DirectLineChannelProperties,
    DirectLineSite
)

channel = client.channels.create(
    resource_group_name=resource_group,
    resource_name=bot_name,
    channel_name="DirectLineChannel",
    parameters=BotChannel(
        location="global",
        properties=DirectLineChannel(
            properties=DirectLineChannelProperties(
                sites=[
                    DirectLineSite(
                        site_name="Default Site",
                        is_enabled=True,
                        is_v1_enabled=False,
                        is_v3_enabled=True
                    )
                ]
            )
        )
    )
)
```

### 加入 Web Chat Channel

```python
from azure.mgmt.botservice.models import (
    BotChannel,
    WebChatChannel,
    WebChatChannelProperties,
    WebChatSite
)

channel = client.channels.create(
    resource_group_name=resource_group,
    resource_name=bot_name,
    channel_name="WebChatChannel",
    parameters=BotChannel(
        location="global",
        properties=WebChatChannel(
            properties=WebChatChannelProperties(
                sites=[
                    WebChatSite(
                        site_name="Default Site",
                        is_enabled=True
                    )
                ]
            )
        )
    )
)
```

## 取得 Channel 詳細資料

```python
channel = client.channels.get(
    resource_group_name=resource_group,
    resource_name=bot_name,
    channel_name="DirectLineChannel"
)
```

## 列出 Channel Key

```python
keys = client.channels.list_with_keys(
    resource_group_name=resource_group,
    resource_name=bot_name,
    channel_name="DirectLineChannel"
)

# 存取 Direct Line key
if hasattr(keys.properties, 'properties'):
    for site in keys.properties.properties.sites:
        print(f"Site: {site.site_name}")
        print(f"Key: {site.key}")
```

## Bot 連線（OAuth）

### 建立連線設定

```python
from azure.mgmt.botservice.models import (
    ConnectionSetting,
    ConnectionSettingProperties
)

connection = client.bot_connection.create(
    resource_group_name=resource_group,
    resource_name=bot_name,
    connection_name="graph-connection",
    parameters=ConnectionSetting(
        location="global",
        properties=ConnectionSettingProperties(
            client_id="<oauth-client-id>",
            client_secret="<oauth-client-secret>",
            scopes="User.Read",
            service_provider_id="<service-provider-id>"
        )
    )
)
```

### 列出連線

```python
connections = client.bot_connection.list_by_bot_service(
    resource_group_name=resource_group,
    resource_name=bot_name
)

for conn in connections:
    print(f"Connection: {conn.name}")
```

## Client 操作

| 操作 | 方法 |
|-----------|--------|
| `client.bots` | Bot CRUD 操作 |
| `client.channels` | Channel 設定 |
| `client.bot_connection` | OAuth 連線設定 |
| `client.direct_line` | Direct Line channel 操作 |
| `client.email` | Email channel 操作 |
| `client.operations` | 可用的操作 |
| `client.host_settings` | Host 設定操作 |

## SKU 選項

| SKU | 說明 |
|-----|-------------|
| `F0` | 免費層（訊息有限） |
| `S1` | 標準層（訊息不限） |

## Channel 類型

| Channel | Class | 用途 |
|---------|-------|---------|
| `MsTeamsChannel` | Microsoft Teams | Teams 整合 |
| `DirectLineChannel` | Direct Line | 自訂 client 整合 |
| `WebChatChannel` | Web Chat | 可嵌入的網頁小工具 |
| `SlackChannel` | Slack | Slack workspace 整合 |
| `FacebookChannel` | Facebook | Messenger 整合 |
| `EmailChannel` | Email | Email 溝通 |

## 最佳實務

1. **同步或非同步擇一，並保持一致。** 同一條呼叫路徑裡，不要混用 `azure.xxx` 同步 client 和 `azure.xxx.aio` 非同步 client。每個 module 選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都包在 `with Client(...) as client:`（同步）或 `async with Client(...) as client:`（非同步）裡。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，這樣 token 和 transport 才會清理乾淨。
3. 在本機執行的程式碼用 **`DefaultAzureCredential`**。在 Azure 上執行的程式碼用特定的 token credential。
4. **開發時從 F0 SKU 開始**，正式環境再升級到 S1
5. **安全地儲存 MSA App ID/Secret**：用 Key Vault
6. **只啟用需要的 channel**：縮小攻擊面
7. **定期輪替 Direct Line key**
8. bot 連線**盡量用 managed identity**
9. Web Chat channel 要**設定正確的 CORS**

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打的功能、operation group 涵蓋範圍，以及正式環境檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 次要/進階情境的專屬非主打範例。 |
