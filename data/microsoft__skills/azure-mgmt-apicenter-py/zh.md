---
name: azure-mgmt-apicenter-py
description: |
  Azure API Center Management SDK for Python。用於管理整個組織的 API 清冊、metadata 和治理。
  Triggers: "azure-mgmt-apicenter", "ApiCenterMgmtClient", "API Center", "API inventory", "API governance".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-mgmt-apicenter
---

# Azure API Center Management SDK for Python

在 Azure API Center 裡管理 API 清冊、metadata 和治理。

## 安裝

```bash
pip install azure-mgmt-apicenter
pip install azure-identity
```

## 環境變數

```bash
AZURE_SUBSCRIPTION_ID=your-subscription-id  # 所有認證方式都必填
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
from azure.mgmt.apicenter import ApiCenterMgmtClient
import os

# 本機開發：DefaultAzureCredential。正式環境：設 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在正式環境直接用特定的 credential：
# 見 https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()

with ApiCenterMgmtClient(
    credential=credential,
    subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"]
) as client:
    # 後續所有操作都用 `client`（見下面的範例）
    ...
```

## 建立 API Center

```python
from azure.mgmt.apicenter.models import Service

api_center = client.services.create_or_update(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    resource=Service(
        location="eastus",
        tags={"environment": "production"}
    )
)

print(f"Created API Center: {api_center.name}")
```

## 列出 API Center

```python
api_centers = client.services.list_by_subscription()

for api_center in api_centers:
    print(f"{api_center.name} - {api_center.location}")
```

## 註冊 API

```python
from azure.mgmt.apicenter.models import Api, ApiKind, ApiProperties

api = client.apis.create_or_update(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default",
    api_name="my-api",
    resource=Api(
        properties=ApiProperties(
            title="My API",
            description="A sample API for demonstration",
            kind=ApiKind.REST,
            terms_of_service={"url": "https://example.com/terms"},
            contacts=[{"name": "API Team", "email": "api-team@example.com"}],
        )
    ),
)

print(f"Registered API: {api.properties.title}")
```

## 建立 API 版本

```python
from azure.mgmt.apicenter.models import ApiVersion, ApiVersionProperties, LifecycleStage

version = client.api_versions.create_or_update(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default",
    api_name="my-api",
    version_name="v1",
    resource=ApiVersion(
        properties=ApiVersionProperties(
            title="Version 1.0",
            lifecycle_stage=LifecycleStage.PRODUCTION,
        )
    ),
)

print(f"Created version: {version.properties.title}")
```

## 新增 API 定義

```python
from azure.mgmt.apicenter.models import ApiDefinition, ApiDefinitionProperties

definition = client.api_definitions.create_or_update(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default",
    api_name="my-api",
    version_name="v1",
    definition_name="openapi",
    resource=ApiDefinition(
        properties=ApiDefinitionProperties(
            title="OpenAPI Definition",
            description="OpenAPI 3.0 specification",
        )
    ),
)
```

## 匯入 API 規格

```python
from azure.mgmt.apicenter.models import ApiSpecImportRequest, ApiSpecImportSourceFormat

# 從 inline 內容匯入
client.api_definitions.begin_import_specification(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default",
    api_name="my-api",
    version_name="v1",
    definition_name="openapi",
    body=ApiSpecImportRequest(
        format=ApiSpecImportSourceFormat.INLINE,
        value='{"openapi": "3.0.0", "info": {"title": "My API", "version": "1.0"}, "paths": {}}',
    )
).result()
```

## 列出 API

```python
apis = client.apis.list(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default"
)

for api in apis:
    print(f"{api.name}: {api.title} ({api.kind})")
```

## 建立環境

```python
from azure.mgmt.apicenter.models import Environment, EnvironmentKind, EnvironmentProperties

environment = client.environments.create_or_update(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default",
    environment_name="production",
    resource=Environment(
        properties=EnvironmentProperties(
            title="Production",
            description="Production environment",
            kind=EnvironmentKind.PRODUCTION,
            server={"type": "Azure API Management", "management_portal_uri": ["https://portal.azure.com"]},
        )
    ),
)
```

## 建立部署

```python
from azure.mgmt.apicenter.models import Deployment, DeploymentProperties, DeploymentState

deployment = client.deployments.create_or_update(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    workspace_name="default",
    api_name="my-api",
    deployment_name="prod-deployment",
    resource=Deployment(
        properties=DeploymentProperties(
            title="Production Deployment",
            description="Deployed to production APIM",
            environment_id="/workspaces/default/environments/production",
            definition_id="/workspaces/default/apis/my-api/versions/v1/definitions/openapi",
            state=DeploymentState.ACTIVE,
            server={"runtime_uri": ["https://api.example.com"]},
        )
    ),
)
```

## 定義自訂 Metadata

```python
from azure.mgmt.apicenter.models import MetadataSchema, MetadataSchemaProperties

metadata = client.metadata_schemas.create_or_update(
    resource_group_name="my-resource-group",
    service_name="my-api-center",
    metadata_schema_name="data-classification",
    resource=MetadataSchema(
        properties=MetadataSchemaProperties(
            schema='{"type": "string", "title": "Data Classification", "enum": ["public", "internal", "confidential"]}'
        )
    ),
)
```

## Client 類型

| Client | 用途 |
|--------|---------|
| `ApiCenterMgmtClient` | 所有操作的主要 client |

## 操作

| Operation Group | 用途 |
|----------------|---------|
| `services` | API Center 服務管理 |
| `workspaces` | Workspace 管理 |
| `apis` | API 註冊與管理 |
| `api_versions` | API 版本管理 |
| `api_definitions` | API 定義管理 |
| `deployments` | 部署追蹤 |
| `environments` | 環境管理 |
| `metadata_schemas` | 自訂 metadata 定義 |

## 最佳實務

1. **同步或非同步擇一，並保持一致。** 同一條呼叫路徑裡，不要混用 `azure.xxx` 同步 client 和 `azure.xxx.aio` 非同步 client。每個 module 選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都包在 `with Client(...) as client:`（同步）或 `async with Client(...) as client:`（非同步）裡。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，這樣 token 和 transport 才會清理乾淨。
3. **用 workspace** 依團隊或領域組織 API
4. **定義 metadata schema**，讓治理一致
5. **追蹤部署**，掌握 API 跑在哪裡
6. **匯入規格**，才能做 API 分析和 lint
7. **用生命週期階段**追蹤 API 的成熟度
8. **加上聯絡人**，標明 API 的負責人和支援窗口

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打的功能、operation group 涵蓋範圍，以及正式環境檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 次要/進階情境的專屬非主打範例。 |
