---
name: m365-agents-py
description: |
  Microsoft 365 Agents SDK for Python。用 aiohttp hosting、AgentApplication 路由、streaming 回應和 MSAL 驗證，建立給 Teams/M365/Copilot Studio 用的多通路 agent。Triggers: "Microsoft 365 Agents SDK", "microsoft_agents", "AgentApplication", "start_agent_process", "TurnContext", "Copilot Studio client", "CloudAdapter".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: microsoft-agents-hosting-core, microsoft-agents-hosting-aiohttp, microsoft-agents-activity, microsoft-agents-authentication-msal, microsoft-agents-copilotstudio-client
---

# Microsoft 365 Agents SDK (Python)

用 Microsoft Agents SDK 搭配 aiohttp hosting、AgentApplication 路由、streaming 回應和 MSAL 驗證，為 Microsoft 365、Teams 和 Copilot Studio 建立企業級 agent。

## Before implementation

- 用 microsoft-docs MCP 驗證 AgentApplication、start_agent_process 和驗證選項的最新 API 簽章。
- 到 PyPI 確認你打算使用的 microsoft-agents-\* 套件的版本。

## Important Notice - Import Changes

> **⚠️ Breaking Change**：最近的更新把 Python 的 import 結構從 `microsoft.agents` 改成 `microsoft_agents`（用底線取代點）。

## Installation

```bash
pip install microsoft-agents-hosting-core
pip install microsoft-agents-hosting-aiohttp
pip install microsoft-agents-activity
pip install microsoft-agents-authentication-msal
pip install microsoft-agents-copilotstudio-client
pip install python-dotenv aiohttp
```

## Environment Variables (.env)

```bash
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID=<client-id>
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTSECRET=<client-secret>
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID=<tenant-id>

# 選用：自動登入用的 OAuth handler
AGENTAPPLICATION__USERAUTHORIZATION__HANDLERS__GRAPH__SETTINGS__AZUREBOTOAUTHCONNECTIONNAME=<connection-name>

# 選用：streaming 用的 Azure OpenAI（透過 DefaultAzureCredential 做 AAD 驗證）
AZURE_OPENAI_ENDPOINT=<endpoint>
AZURE_OPENAI_API_VERSION=<version>

# 選用：Copilot Studio client
COPILOTSTUDIOAGENT__ENVIRONMENTID=<environment-id>
COPILOTSTUDIOAGENT__SCHEMANAME=<schema-name>
COPILOTSTUDIOAGENT__TENANTID=<tenant-id>
COPILOTSTUDIOAGENT__AGENTAPPID=<app-id>
```

## Authentication & Lifecycle

> **🔑 下面每個程式碼範例都適用這兩條規則：**
>
> 1. **這個 SDK 是 async 優先：全程用 `async def` handler 和 `async with`。**
> 2. **使用明確的 auth manager，並用 context manager 管理網路資源。** agent 驗證用 `MsalConnectionManager`，每個 request 的 HTTP 資源要包在 `async with` 裡（例如 `aiohttp.ClientSession`）。
>
> 範例片段可能會省略這些設定，但正式環境的程式碼一定要遵守這兩條規則。

## Core Workflow: aiohttp-hosted AgentApplication

```python
import logging
from os import environ

from dotenv import load_dotenv
from aiohttp.web import Request, Response, Application, run_app

from microsoft_agents.activity import load_configuration_from_env
from microsoft_agents.hosting.core import (
    Authorization,
    AgentApplication,
    TurnState,
    TurnContext,
    MemoryStorage,
)
from microsoft_agents.hosting.aiohttp import (
    CloudAdapter,
    start_agent_process,
    jwt_authorization_middleware,
)
from microsoft_agents.authentication.msal import MsalConnectionManager

# 啟用 logging
ms_agents_logger = logging.getLogger("microsoft_agents")
ms_agents_logger.addHandler(logging.StreamHandler())
ms_agents_logger.setLevel(logging.INFO)

# 載入設定
load_dotenv()
agents_sdk_config = load_configuration_from_env(environ)

# 建立 storage 和 connection manager
STORAGE = MemoryStorage()
CONNECTION_MANAGER = MsalConnectionManager(**agents_sdk_config)
ADAPTER = CloudAdapter(connection_manager=CONNECTION_MANAGER)
AUTHORIZATION = Authorization(STORAGE, CONNECTION_MANAGER, **agents_sdk_config)

# 建立 AgentApplication
AGENT_APP = AgentApplication[TurnState](
    storage=STORAGE, adapter=ADAPTER, authorization=AUTHORIZATION, **agents_sdk_config
)


@AGENT_APP.conversation_update("membersAdded")
async def on_members_added(context: TurnContext, _state: TurnState):
    await context.send_activity("Welcome to the agent!")


@AGENT_APP.activity("message")
async def on_message(context: TurnContext, _state: TurnState):
    await context.send_activity(f"You said: {context.activity.text}")


@AGENT_APP.error
async def on_error(context: TurnContext, error: Exception):
    await context.send_activity("The agent encountered an error.")


# 伺服器設定
async def entry_point(req: Request) -> Response:
    agent: AgentApplication = req.app["agent_app"]
    adapter: CloudAdapter = req.app["adapter"]
    return await start_agent_process(req, agent, adapter)


APP = Application(middlewares=[jwt_authorization_middleware])
APP.router.add_post("/api/messages", entry_point)
APP["agent_configuration"] = CONNECTION_MANAGER.get_default_connection_configuration()
APP["agent_app"] = AGENT_APP
APP["adapter"] = AGENT_APP.adapter

if __name__ == "__main__":
    run_app(APP, host="localhost", port=environ.get("PORT", 3978))
```

## AgentApplication Routing

```python
import re
from microsoft_agents.hosting.core import (
    AgentApplication, TurnState, TurnContext, MessageFactory
)
from microsoft_agents.activity import ActivityTypes

AGENT_APP = AgentApplication[TurnState](
    storage=STORAGE, adapter=ADAPTER, authorization=AUTHORIZATION, **agents_sdk_config
)

# 歡迎訊息 handler
@AGENT_APP.conversation_update("membersAdded")
async def on_members_added(context: TurnContext, _state: TurnState):
    await context.send_activity("Welcome!")

# 以 regex 比對的訊息 handler
@AGENT_APP.message(re.compile(r"^hello$", re.IGNORECASE))
async def on_hello(context: TurnContext, _state: TurnState):
    await context.send_activity("Hello!")

# 單純字串比對的訊息 handler
@AGENT_APP.message("/status")
async def on_status(context: TurnContext, _state: TurnState):
    await context.send_activity("Status: OK")

# 受驗證保護的訊息 handler
@AGENT_APP.message("/me", auth_handlers=["GRAPH"])
async def on_profile(context: TurnContext, state: TurnState):
    token_response = await AGENT_APP.auth.get_token(context, "GRAPH")
    if token_response and token_response.token:
        # 用 token 呼叫 Graph API
        await context.send_activity("Profile retrieved")

# Invoke activity handler
@AGENT_APP.activity(ActivityTypes.invoke)
async def on_invoke(context: TurnContext, _state: TurnState):
    invoke_response = Activity(
        type=ActivityTypes.invoke_response, value={"status": 200}
    )
    await context.send_activity(invoke_response)

# 備援的訊息 handler
@AGENT_APP.activity("message")
async def on_message(context: TurnContext, _state: TurnState):
    await context.send_activity(f"Echo: {context.activity.text}")

# 錯誤 handler
@AGENT_APP.error
async def on_error(context: TurnContext, error: Exception):
    await context.send_activity("An error occurred.")
```

## Streaming Responses with Azure OpenAI

```python
from openai import AsyncAzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from microsoft_agents.activity import SensitivityUsageInfo

# AAD token provider（優先於 AZURE_OPENAI_API_KEY）
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default",
)

# 模組層級的 singleton：client 的壽命和 agent app 一樣長。
CLIENT = AsyncAzureOpenAI(
    api_version=environ["AZURE_OPENAI_API_VERSION"],
    azure_endpoint=environ["AZURE_OPENAI_ENDPOINT"],
    azure_ad_token_provider=token_provider,
)

@AGENT_APP.message("poem")
async def on_poem_message(context: TurnContext, _state: TurnState):
    # 設定 streaming 回應
    context.streaming_response.set_feedback_loop(True)
    context.streaming_response.set_generated_by_ai_label(True)
    context.streaming_response.set_sensitivity_label(
        SensitivityUsageInfo(
            type="https://schema.org/Message",
            schema_type="CreativeWork",
            name="Internal",
        )
    )
    context.streaming_response.queue_informative_update("Starting a poem...\n")

    # 從 Azure OpenAI 串流
    streamed_response = await CLIENT.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a creative assistant."},
            {"role": "user", "content": "Write a poem about Python."}
        ],
        stream=True,
    )

    try:
        async for chunk in streamed_response:
            if chunk.choices and chunk.choices[0].delta.content:
                context.streaming_response.queue_text_chunk(
                    chunk.choices[0].delta.content
                )
    finally:
        await context.streaming_response.end_stream()
```

## OAuth / Auto Sign-In

```python
@AGENT_APP.message("/logout")
async def logout(context: TurnContext, state: TurnState):
    await AGENT_APP.auth.sign_out(context, "GRAPH")
    await context.send_activity(MessageFactory.text("You have been logged out."))


@AGENT_APP.message("/me", auth_handlers=["GRAPH"])
async def profile_request(context: TurnContext, state: TurnState):
    user_token_response = await AGENT_APP.auth.get_token(context, "GRAPH")
    if user_token_response and user_token_response.token:
        # 用 token 呼叫 Microsoft Graph
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {user_token_response.token}",
                "Content-Type": "application/json",
            }
            async with session.get(
                "https://graph.microsoft.com/v1.0/me", headers=headers
            ) as response:
                if response.status == 200:
                    user_info = await response.json()
                    await context.send_activity(f"Hello, {user_info['displayName']}!")
```

## Copilot Studio Client (Direct to Engine)

```python
import asyncio
from msal import PublicClientApplication
from microsoft_agents.activity import ActivityTypes, load_configuration_from_env
from microsoft_agents.copilotstudio.client import (
    ConnectionSettings,
    CopilotClient,
)

# Token cache（互動流程用的本機檔案）
class LocalTokenCache:
    # 完整實作見範例
    pass

def acquire_token(settings, app_client_id, tenant_id):
    pca = PublicClientApplication(
        client_id=app_client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
    )

    token_request = {"scopes": ["https://api.powerplatform.com/.default"]}
    accounts = pca.get_accounts()

    if accounts:
        response = pca.acquire_token_silent(token_request["scopes"], account=accounts[0])
        return response.get("access_token")
    else:
        response = pca.acquire_token_interactive(**token_request)
        return response.get("access_token")


async def main():
    settings = ConnectionSettings(
        environment_id=environ.get("COPILOTSTUDIOAGENT__ENVIRONMENTID"),
        agent_identifier=environ.get("COPILOTSTUDIOAGENT__SCHEMANAME"),
    )

    token = acquire_token(
        settings,
        app_client_id=environ.get("COPILOTSTUDIOAGENT__AGENTAPPID"),
        tenant_id=environ.get("COPILOTSTUDIOAGENT__TENANTID"),
    )

    # CopilotClient 沒有實作 context manager protocol。
    copilot_client = CopilotClient(settings, token)

    # 開始對話
    act = copilot_client.start_conversation(True)
    async for action in act:
        if action.text:
            print(action.text)

    # 提問
    replies = copilot_client.ask_question("Hello!", action.conversation.id)
    async for reply in replies:
        if reply.type == ActivityTypes.message:
            print(reply.text)


asyncio.run(main())
```

## Best Practices

1. **這個 SDK 是 async 優先：全程用 `async def` handler 和 `async with`。**
2. **client 和 async credential 一律用 context manager。** 每個 client 都包在 `with Client(...) as client:`（同步）或 `async with Client(...) as client:`（非同步）裡。`azure.identity.aio` 的 async `DefaultAzureCredential` 也要用 `async with credential:`，這樣 token 和 transport 才會被清理。
3. 用 `microsoft_agents` 這個 import 前綴（底線，不是點）。
4. `MemoryStorage` 只在開發時用；正式環境用 BlobStorage 或 CosmosDB。
5. 一律用 `load_configuration_from_env(environ)` 載入 SDK 設定。
6. 在 aiohttp Application 的 middleware 裡加入 `jwt_authorization_middleware`。
7. MSAL 驗證用 `MsalConnectionManager`。
8. 用 streaming 回應時，要在 finally 區塊裡呼叫 `end_stream()`。
9. 受 OAuth 保護的路由，在訊息 decorator 上用 `auth_handlers` 參數。
10. secret 放在環境變數，不要放在原始碼裡。

## Reference Links

| Resource                      | URL                                                                           |
| ----------------------------- | ----------------------------------------------------------------------------- |
| Microsoft 365 Agents SDK      | https://learn.microsoft.com/en-us/microsoft-365/agents-sdk/                   |
| GitHub samples (Python)       | https://github.com/microsoft/Agents-for-python                                |
| PyPI packages                 | https://pypi.org/search/?q=microsoft-agents                                   |
| Integrate with Copilot Studio | https://learn.microsoft.com/en-us/microsoft-365/agents-sdk/integrate-with-mcs |

## Reference Files

| File | Contents |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打的功能、各 operation group 的涵蓋範圍，以及正式環境檢查清單。 |
