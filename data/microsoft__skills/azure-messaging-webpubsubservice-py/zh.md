---
name: azure-messaging-webpubsubservice-py
description: |
  Azure Web PubSub Service SDK for Python。用於即時訊息傳遞、WebSocket 連線和 pub/sub 模式。
  Triggers: "azure-messaging-webpubsubservice", "WebPubSubServiceClient", "real-time", "WebSocket", "pub/sub".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-messaging-webpubsubservice
---

# Azure Web PubSub Service SDK for Python

用 WebSocket 連線做大規模的即時訊息傳遞。

## 安裝

```bash
# Service SDK（伺服器端）
pip install azure-messaging-webpubsubservice

# Client SDK（給 Python WebSocket client 用）
pip install azure-messaging-webpubsubclient
```

## 環境變數

```bash
AZURE_WEBPUBSUB_HUB=my-hub  # 所有認證方式都必填
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

## Service Client（伺服器端）

### 認證

```python
from azure.messaging.webpubsubservice import WebPubSubServiceClient
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential

# 本機開發：DefaultAzureCredential。正式環境：設 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在正式環境直接用特定的 credential：
# 見 https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()

with WebPubSubServiceClient(
    endpoint="https://<name>.webpubsub.azure.com",
    hub="my-hub",
    credential=credential
) as client:
    # 後續所有操作都用 `client`（見下面的範例）
    ...
```

### 產生 Client Access Token

```python
# 匿名使用者的 token
token = client.get_client_access_token()
print(f"URL: {token['url']}")

# 帶 user ID 的 token
token = client.get_client_access_token(
    user_id="user123",
    roles=["webpubsub.sendToGroup", "webpubsub.joinLeaveGroup"]
)

# 帶 group 的 token
token = client.get_client_access_token(
    user_id="user123",
    groups=["group1", "group2"]
)
```

### 傳送給所有 Client

```python
# 傳送文字
client.send_to_all(message="Hello everyone!", content_type="text/plain")

# 傳送 JSON
client.send_to_all(
    message={"type": "notification", "data": "Hello"},
    content_type="application/json"
)
```

### 傳送給 User

```python
client.send_to_user(
    user_id="user123",
    message="Hello user!",
    content_type="text/plain"
)
```

### 傳送給 Group

```python
client.send_to_group(
    group="my-group",
    message="Hello group!",
    content_type="text/plain"
)
```

### 傳送給 Connection

```python
client.send_to_connection(
    connection_id="abc123",
    message="Hello connection!",
    content_type="text/plain"
)
```

### Group 管理

```python
# 把使用者加進 group
client.add_user_to_group(group="my-group", user_id="user123")

# 把使用者移出 group
client.remove_user_from_group(group="my-group", user_id="user123")

# 把連線加進 group
client.add_connection_to_group(group="my-group", connection_id="abc123")

# 把連線移出 group
client.remove_connection_from_group(group="my-group", connection_id="abc123")
```

### 連線管理

```python
# 檢查連線是否存在
exists = client.connection_exists(connection_id="abc123")

# 檢查使用者是否有連線
exists = client.user_exists(user_id="user123")

# 檢查 group 是否有連線
exists = client.group_exists(group="my-group")

# 關閉連線
client.close_connection(connection_id="abc123", reason="Session ended")

# 關閉使用者的所有連線
client.close_all_connections(user_id="user123")
```

### 授予/撤銷權限

```python
from azure.messaging.webpubsubservice import WebPubSubServiceClient

# 授予權限
client.grant_permission(
    permission="joinLeaveGroup",
    connection_id="abc123",
    target_name="my-group"
)

# 撤銷權限
client.revoke_permission(
    permission="joinLeaveGroup",
    connection_id="abc123",
    target_name="my-group"
)

# 檢查權限
has_permission = client.check_permission(
    permission="joinLeaveGroup",
    connection_id="abc123",
    target_name="my-group"
)
```

## Client SDK（Python WebSocket Client）

```python
from azure.messaging.webpubsubclient import WebPubSubClient

with WebPubSubClient(credential=token["url"]) as client:
    @client.on("connected")
    def on_connected(e):
        print(f"Connected: {e.connection_id}")

    @client.on("server-message")
    def on_message(e):
        print(f"Message: {e.data}")

    @client.on("group-message")
    def on_group_message(e):
        print(f"Group {e.group}: {e.data}")

    client.send_to_group("my-group", "Hello from Python!")
```

## 非同步 Service Client

```python
from azure.messaging.webpubsubservice.aio import WebPubSubServiceClient
from azure.identity.aio import DefaultAzureCredential

async def broadcast():
    async with DefaultAzureCredential() as credential:
        async with WebPubSubServiceClient(
            endpoint="https://<name>.webpubsub.azure.com",
            hub="my-hub",
            credential=credential
        ) as client:
            await client.send_to_all("Hello async!", content_type="text/plain")
```

## Client 操作

| 操作 | 說明 |
|-----------|-------------|
| `get_client_access_token` | 產生 WebSocket 連線 URL |
| `send_to_all` | 廣播給所有連線 |
| `send_to_user` | 傳送給特定使用者 |
| `send_to_group` | 傳送給 group 成員 |
| `send_to_connection` | 傳送給特定連線 |
| `add_user_to_group` | 把使用者加進 group |
| `remove_user_from_group` | 把使用者移出 group |
| `close_connection` | 中斷 client 連線 |
| `connection_exists` | 檢查連線狀態 |

## 最佳實務

1. **同步或非同步擇一，並保持一致。** 同一條呼叫路徑裡，不要混用 `azure.xxx` 同步 client 和 `azure.xxx.aio` 非同步 client。每個 module 選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都包在 `with Client(...) as client:`（同步）或 `async with Client(...) as client:`（非同步）裡。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，這樣 token 和 transport 才會清理乾淨。
3. **用 `DefaultAzureCredential`**，在本機開發和 Azure 之間可攜的認證方式（盡量避免連線字串 / access key）。
4. **用角色**限制 client 權限
4. **用 group** 做有針對性的訊息傳遞
5. **產生短效的 token**，比較安全
6. **用 user ID**，才能跨連線傳送給使用者
7. **在 client 應用程式裡處理重新連線**
8. 結構化資料用 **JSON** content type
9. 優雅地**關閉連線**，並附上原因

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打的功能、operation group 涵蓋範圍，以及正式環境檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 次要/進階情境的專屬非主打範例。 |
