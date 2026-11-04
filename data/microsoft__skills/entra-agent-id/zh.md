---
name: entra-agent-id
description: |
  Microsoft Entra Agent ID（preview），透過 Microsoft Graph beta API 建立具備 OAuth2 能力的 AI agent 身分。
  涵蓋 Agent Identity Blueprint、BlueprintPrincipal、Agent Identity、所需權限、sponsor 和 Workload Identity Federation。
  也包含 Microsoft Entra SDK for AgentID（容器化的 sidecar），用於多語言 agent 驗證（Docker/Kubernetes）、第三方 agent 整合，以及自主與互動式 agent 模式。
  Triggers: "agent identity", "agent id", "Agent Identity Blueprint", "BlueprintPrincipal", "entra agent", "agent identity provisioning", "Graph agent identity", "entra sidecar", "agent id sidecar", "auth sidecar", "3P agent", "third-party agent identity", "polyglot agent auth".
---

# Microsoft Entra Agent ID

用 Microsoft Graph beta API 為 AI agent 建立並管理具備 OAuth2 能力的身分。

> **Preview API**：所有 Agent Identity endpoint 都只在 `/beta` 底下，`/v1.0` 沒有。

## Before You Start

用 `microsoft-docs` MCP 搜尋最新的 Agent ID 文件：
- Query："Microsoft Entra agent identity setup"
- 驗證：API 參數是否符合目前 preview 的行為

## Conceptual Model

```
Agent Identity Blueprint (application)        ← one per agent type/project
  └── BlueprintPrincipal (service principal)   ← MUST be created explicitly
        ├── Agent Identity (SP): agent-1       ← one per agent instance
        ├── Agent Identity (SP): agent-2
        └── Agent Identity (SP): agent-3
```

## Prerequisites

### PowerShell (recommended for interactive setup)

```powershell
# Requires PowerShell 7+
Install-Module Microsoft.Graph.Beta.Applications -Scope CurrentUser -Force
```

### Python (for programmatic provisioning)

```bash
pip install azure-identity requests
```

### Required Entra Roles

下列其中一個：**Agent Identity Developer**、**Agent Identity Administrator** 或 **Application Administrator**。

## Environment Variables

```bash
AZURE_TENANT_ID=<your-tenant-id>
AZURE_CLIENT_ID=<app-registration-client-id>
AZURE_CLIENT_SECRET=<app-registration-secret>
```

## Authentication

> **⚠️ 不支援 `DefaultAzureCredential`。** Azure CLI 的 token 含有
> `Directory.AccessAsUser.All`，Agent Identity API 會明確拒絕它（403）。
> 你一定要用專用的 app registration 搭配 `client_credentials` flow，
> 或是用 `Connect-MgGraph` 並明確指定 delegated scope。

### PowerShell (delegated permissions)

```powershell
Connect-MgGraph -Scopes @(
    "AgentIdentityBlueprint.Create",
    "AgentIdentityBlueprint.ReadWrite.All",
    "AgentIdentityBlueprintPrincipal.Create",
    "User.Read"
)
Set-MgRequestContext -ApiVersion beta

$currentUser = (Get-MgContext).Account
$userId = (Get-MgUser -UserId $currentUser).Id
```

### Python (application permissions)

```python
import os
import requests
from azure.identity import ClientSecretCredential

credential = ClientSecretCredential(
    tenant_id=os.environ["AZURE_TENANT_ID"],
    client_id=os.environ["AZURE_CLIENT_ID"],
    client_secret=os.environ["AZURE_CLIENT_SECRET"],
)
token = credential.get_token("https://graph.microsoft.com/.default")

GRAPH = "https://graph.microsoft.com/beta"
headers = {
    "Authorization": f"Bearer {token.token}",
    "Content-Type": "application/json",
    "OData-Version": "4.0",  # Required for all Agent Identity API calls
}
```

## Core Workflow

### Step 1: Create Agent Identity Blueprint

Sponsor 是必填，而且**一定要是 User 物件**，ServicePrincipal 和 Group 會被拒絕。

```python
import subprocess

# Get sponsor user ID (client_credentials has no user context, so use az CLI)
result = subprocess.run(
    ["az", "ad", "signed-in-user", "show", "--query", "id", "-o", "tsv"],
    capture_output=True, text=True, check=True,
)
user_id = result.stdout.strip()

blueprint_body = {
    "@odata.type": "Microsoft.Graph.AgentIdentityBlueprint",
    "displayName": "My Agent Blueprint",
    "sponsors@odata.bind": [
        f"https://graph.microsoft.com/beta/users/{user_id}"
    ],
}
resp = requests.post(f"{GRAPH}/applications", headers=headers, json=blueprint_body)
resp.raise_for_status()

blueprint = resp.json()
app_id = blueprint["appId"]
blueprint_obj_id = blueprint["id"]
```

### Step 2: Create BlueprintPrincipal

> **這一步是必要的。** 建立 Blueprint 並**不會**自動建立它的
> service principal。沒有這一步的話，建立 Agent Identity 會失敗：
> `400: The Agent Blueprint Principal for the Agent Blueprint does not exist.`

```python
sp_body = {
    "@odata.type": "Microsoft.Graph.AgentIdentityBlueprintPrincipal",
    "appId": app_id,
}
resp = requests.post(f"{GRAPH}/servicePrincipals", headers=headers, json=sp_body)
resp.raise_for_status()
```

如果要實作 idempotent 的 script，就算 Blueprint 已經存在，也要檢查並建立 BlueprintPrincipal
（上一次執行可能建好了 Blueprint，但在建立 SP 之前就當掉了）。

### Step 3: Create Agent Identities

```python
agent_body = {
    "@odata.type": "Microsoft.Graph.AgentIdentity",
    "displayName": "my-agent-instance-1",
    "agentIdentityBlueprintId": app_id,
    "sponsors@odata.bind": [
        f"https://graph.microsoft.com/beta/users/{user_id}"
    ],
}
resp = requests.post(f"{GRAPH}/servicePrincipals", headers=headers, json=agent_body)
resp.raise_for_status()
agent = resp.json()
```

## API Reference

| Operation | Method | Endpoint | OData Type |
|-----------|--------|----------|------------|
| Create Blueprint | `POST` | `/applications` | `Microsoft.Graph.AgentIdentityBlueprint` |
| Create BlueprintPrincipal | `POST` | `/servicePrincipals` | `Microsoft.Graph.AgentIdentityBlueprintPrincipal` |
| Create Agent Identity | `POST` | `/servicePrincipals` | `Microsoft.Graph.AgentIdentity` |
| List Agent Identities | `GET` | `/servicePrincipals?$filter=...` | — |
| Delete Agent Identity | `DELETE` | `/servicePrincipals/{id}` | — |
| Delete Blueprint | `DELETE` | `/applications/{id}` | — |

所有 endpoint 的 base URL：`https://graph.microsoft.com/beta`

## Required Permissions

| Permission | Purpose |
|-----------|---------|
| `Application.ReadWrite.All` | Blueprint 的 CRUD（application 物件） |
| `AgentIdentityBlueprint.Create` | 建立新的 Blueprint |
| `AgentIdentityBlueprint.ReadWrite.All` | 讀取/更新 Blueprint |
| `AgentIdentityBlueprintPrincipal.Create` | 建立 BlueprintPrincipal |
| `AgentIdentity.Create.All` | 建立 Agent Identity |
| `AgentIdentity.ReadWrite.All` | 讀取/更新 Agent Identity |

Graph application permission 裡有 **18 個 Agent Identity 專屬的**權限。全部查出來：
```bash
az ad sp show --id 00000003-0000-0000-c000-000000000000 \
  --query "appRoles[?contains(value, 'AgentIdentity')].{id:id, value:value}" -o json
```

授予 admin consent（application permission 必須）：
```bash
az ad app permission admin-consent --id <client-id>
```

> 如果 service principal 還沒複寫完成，admin consent 可能會回 404。用 10–40 秒的 backoff 重試。

## Cleanup

```python
# Delete Agent Identity
requests.delete(f"{GRAPH}/servicePrincipals/{agent['id']}", headers=headers)

# Delete BlueprintPrincipal (get SP ID first)
sps = requests.get(
    f"{GRAPH}/servicePrincipals?$filter=appId eq '{app_id}'",
    headers=headers,
).json()
for sp in sps.get("value", []):
    requests.delete(f"{GRAPH}/servicePrincipals/{sp['id']}", headers=headers)

# Delete Blueprint
requests.delete(f"{GRAPH}/applications/{blueprint_obj_id}", headers=headers)
```

## Best Practices

1. **建立 Blueprint 之後一定要建立 BlueprintPrincipal**：它不會自動建立；兩邊都要實作 idempotent 檢查
2. **用 User 物件當 sponsor**：ServicePrincipal 和 Group 會被拒絕
3. **處理權限傳播的延遲**：admin consent 之後等 30–120 秒；遇到 403 就用 backoff 重試
4. **每個 Graph 請求都要帶 `OData-Version: 4.0` header**
5. **正式環境驗證用 Workload Identity Federation**：本機開發則在 Blueprint 上用 client secret（見 [references/oauth2-token-flow.md](references/oauth2-token-flow.md)）
6. **在使用 OAuth2 scoping 之前，先設定 Blueprint 的 `identifierUris`**（`api://{app-id}`）
7. **絕對不要用 Azure CLI token** 呼叫 API：它們含有 `Directory.AccessAsUser.All`，會被直接拒絕
8. **建立之前先檢查資源是否已存在**：實作 idempotent 的 provisioning

## References

| File | Contents |
|------|----------|
| [references/oauth2-token-flow.md](references/oauth2-token-flow.md) | 正式環境（Managed Identity + WIF）和本機開發（client secret）的 token flow |
| [references/known-limitations.md](references/known-limitations.md) | 依類別整理的 29 個已知問題（來自官方 preview 已知問題頁面） |
| [references/sdk-sidecar.md](references/sdk-sidecar.md) | Microsoft Entra SDK for AgentID：endpoint、第三方 agent 模式、Docker/K8s 部署、安全 |

### External Links

| Resource | URL |
|----------|-----|
| Official Setup Guide | https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/agent-id-setup-instructions |
| AI-Guided Setup | https://learn.microsoft.com/en-us/entra/agent-id/identity-platform/agent-id-ai-guided-setup |
| Microsoft Entra SDK for AgentID — Overview | https://learn.microsoft.com/en-us/entra/msidweb/agent-id-sdk/overview |
| Microsoft Entra SDK for AgentID — Endpoints | https://learn.microsoft.com/en-us/entra/msidweb/agent-id-sdk/endpoints |
