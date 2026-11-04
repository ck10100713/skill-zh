---
name: azure-mgmt-apicenter-dotnet
description: |
  Azure API Center SDK for .NET。集中式的 API 清冊管理，含治理、版本控制和探索。用於建立 API 服務、workspace、API、版本、定義、環境、部署和 metadata schema。Triggers: "API Center", "ApiCenterService", "ApiCenterWorkspace", "ApiCenterApi", "API inventory", "API governance", "API versioning", "API catalog", "API discovery".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.ResourceManager.ApiCenter
---

# Azure.ResourceManager.ApiCenter (.NET)

集中式的 API 清冊與治理 SDK，用來管理整個組織的 API。

## 安裝

```bash
dotnet add package Azure.ResourceManager.ApiCenter
dotnet add package Azure.Identity
```

**目前版本**：v1.0.0 (GA)  
**API 版本**：2024-03-01

## 環境變數

```bash
AZURE_SUBSCRIPTION_ID=<your-subscription-id>  # 必填：Azure subscription ID
AZURE_RESOURCE_GROUP=<your-resource-group>  # 必填：resource group 名稱
AZURE_APICENTER_SERVICE_NAME=<your-apicenter-service>  # 必填：API Center 服務名稱
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境用 DefaultAzureCredential 時才需要
```

## 認證

```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.ApiCenter;

// 本機開發：DefaultAzureCredential。正式環境：設 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
var credential = new DefaultAzureCredential(
    DefaultAzureCredential.DefaultEnvironmentVariableName
);
// 或在正式環境直接用特定的 credential：
// 見 https://learn.microsoft.com/dotnet/api/overview/azure/identity-readme?view=azure-dotnet#credential-classes
// var credential = new ManagedIdentityCredential();
ArmClient client = new ArmClient(credential);
```

## 資源階層

```
Subscription
└── ResourceGroup
    └── ApiCenterService                    # API 清冊服務
        ├── Workspace                       # API 的邏輯分組
        │   ├── Api                         # API 定義
        │   │   └── ApiVersion              # API 的版本
        │   │       └── ApiDefinition       # OpenAPI/GraphQL 等規格
        │   ├── Environment                 # 部署目標（dev/staging/prod）
        │   └── Deployment                  # 部署到環境的 API
        └── MetadataSchema                  # 自訂 metadata 定義
```

## 核心工作流程

### 1. 建立 API Center 服務

```csharp
using Azure.ResourceManager.ApiCenter;
using Azure.ResourceManager.ApiCenter.Models;

ResourceGroupResource resourceGroup = await client
    .GetDefaultSubscriptionAsync()
    .Result
    .GetResourceGroupAsync("my-resource-group");

ApiCenterServiceCollection services = resourceGroup.GetApiCenterServices();

ApiCenterServiceData data = new ApiCenterServiceData(AzureLocation.EastUS)
{
    Identity = new ManagedServiceIdentity(ManagedServiceIdentityType.SystemAssigned)
};

ArmOperation<ApiCenterServiceResource> operation = await services
    .CreateOrUpdateAsync(WaitUntil.Completed, "my-api-center", data);

ApiCenterServiceResource service = operation.Value;
```

### 2. 建立 Workspace

```csharp
ApiCenterWorkspaceCollection workspaces = service.GetApiCenterWorkspaces();

ApiCenterWorkspaceData workspaceData = new ApiCenterWorkspaceData
{
    Title = "Engineering APIs",
    Description = "APIs owned by the engineering team"
};

ArmOperation<ApiCenterWorkspaceResource> operation = await workspaces
    .CreateOrUpdateAsync(WaitUntil.Completed, "engineering", workspaceData);

ApiCenterWorkspaceResource workspace = operation.Value;
```

### 3. 建立 API

```csharp
ApiCenterApiCollection apis = workspace.GetApiCenterApis();

ApiCenterApiData apiData = new ApiCenterApiData
{
    Title = "Orders API",
    Description = "API for managing customer orders",
    Kind = ApiKind.Rest,
    LifecycleStage = ApiLifecycleStage.Production,
    TermsOfService = new ApiTermsOfService
    {
        Uri = new Uri("https://example.com/terms")
    },
    ExternalDocumentation = 
    {
        new ApiExternalDocumentation
        {
            Title = "Documentation",
            Uri = new Uri("https://docs.example.com/orders")
        }
    },
    Contacts =
    {
        new ApiContact
        {
            Name = "API Support",
            Email = "api-support@example.com"
        }
    }
};

// 加上自訂 metadata
apiData.CustomProperties = BinaryData.FromObjectAsJson(new
{
    team = "orders-team",
    costCenter = "CC-1234"
});

ArmOperation<ApiCenterApiResource> operation = await apis
    .CreateOrUpdateAsync(WaitUntil.Completed, "orders-api", apiData);

ApiCenterApiResource api = operation.Value;
```

### 4. 建立 API 版本

```csharp
ApiCenterApiVersionCollection versions = api.GetApiCenterApiVersions();

ApiCenterApiVersionData versionData = new ApiCenterApiVersionData
{
    Title = "v1.0.0",
    LifecycleStage = ApiLifecycleStage.Production
};

ArmOperation<ApiCenterApiVersionResource> operation = await versions
    .CreateOrUpdateAsync(WaitUntil.Completed, "v1-0-0", versionData);

ApiCenterApiVersionResource version = operation.Value;
```

### 5. 建立 API 定義（上傳 OpenAPI 規格）

```csharp
ApiCenterApiDefinitionCollection definitions = version.GetApiCenterApiDefinitions();

ApiCenterApiDefinitionData definitionData = new ApiCenterApiDefinitionData
{
    Title = "OpenAPI Specification",
    Description = "Orders API OpenAPI 3.0 definition"
};

ArmOperation<ApiCenterApiDefinitionResource> operation = await definitions
    .CreateOrUpdateAsync(WaitUntil.Completed, "openapi", definitionData);

ApiCenterApiDefinitionResource definition = operation.Value;

// 匯入規格
string openApiSpec = await File.ReadAllTextAsync("orders-api.yaml");

ApiSpecImportContent importContent = new ApiSpecImportContent
{
    Format = ApiSpecImportSourceFormat.Inline,
    Value = openApiSpec,
    Specification = new ApiSpecImportSpecification
    {
        Name = "openapi",
        Version = "3.0.1"
    }
};

await definition.ImportSpecificationAsync(WaitUntil.Completed, importContent);
```

### 6. 匯出 API 規格

```csharp
ApiCenterApiDefinitionResource definition = await client
    .GetApiCenterApiDefinitionResource(definitionResourceId)
    .GetAsync();

ArmOperation<ApiSpecExportResult> operation = await definition
    .ExportSpecificationAsync(WaitUntil.Completed);

ApiSpecExportResult result = operation.Value;

// result.Format - 例如 "inline"
// result.Value - 規格內容
```

### 7. 建立環境

```csharp
ApiCenterEnvironmentCollection environments = workspace.GetApiCenterEnvironments();

ApiCenterEnvironmentData envData = new ApiCenterEnvironmentData
{
    Title = "Production",
    Description = "Production environment",
    Kind = ApiCenterEnvironmentKind.Production,
    Server = new ApiCenterEnvironmentServer
    {
        ManagementPortalUris = { new Uri("https://portal.azure.com") }
    },
    Onboarding = new EnvironmentOnboardingModel
    {
        Instructions = "Contact platform team for access",
        DeveloperPortalUris = { new Uri("https://developer.example.com") }
    }
};

ArmOperation<ApiCenterEnvironmentResource> operation = await environments
    .CreateOrUpdateAsync(WaitUntil.Completed, "production", envData);
```

### 8. 建立部署

```csharp
ApiCenterDeploymentCollection deployments = workspace.GetApiCenterDeployments();

// 取得環境的 resource ID
ResourceIdentifier envResourceId = ApiCenterEnvironmentResource.CreateResourceIdentifier(
    subscriptionId, resourceGroupName, serviceName, workspaceName, "production");

// 取得 API 定義的 resource ID
ResourceIdentifier definitionResourceId = ApiCenterApiDefinitionResource.CreateResourceIdentifier(
    subscriptionId, resourceGroupName, serviceName, workspaceName, 
    "orders-api", "v1-0-0", "openapi");

ApiCenterDeploymentData deploymentData = new ApiCenterDeploymentData
{
    Title = "Orders API - Production",
    Description = "Production deployment of Orders API v1.0.0",
    EnvironmentId = envResourceId,
    DefinitionId = definitionResourceId,
    State = ApiCenterDeploymentState.Active,
    Server = new ApiCenterDeploymentServer
    {
        RuntimeUris = { new Uri("https://api.example.com/orders") }
    }
};

ArmOperation<ApiCenterDeploymentResource> operation = await deployments
    .CreateOrUpdateAsync(WaitUntil.Completed, "orders-api-prod", deploymentData);
```

### 9. 建立 Metadata Schema

```csharp
ApiCenterMetadataSchemaCollection schemas = service.GetApiCenterMetadataSchemas();

string jsonSchema = """
{
    "type": "object",
    "properties": {
        "team": {
            "type": "string",
            "title": "Owning Team"
        },
        "costCenter": {
            "type": "string",
            "title": "Cost Center"
        },
        "dataClassification": {
            "type": "string",
            "enum": ["public", "internal", "confidential"],
            "title": "Data Classification"
        }
    },
    "required": ["team"]
}
""";

ApiCenterMetadataSchemaData schemaData = new ApiCenterMetadataSchemaData
{
    Schema = jsonSchema,
    AssignedTo =
    {
        new MetadataAssignment
        {
            Entity = MetadataAssignmentEntity.Api,
            Required = true
        }
    }
};

ArmOperation<ApiCenterMetadataSchemaResource> operation = await schemas
    .CreateOrUpdateAsync(WaitUntil.Completed, "api-metadata", schemaData);
```

### 10. 列出與搜尋 API

```csharp
// 列出 workspace 裡所有 API
ApiCenterWorkspaceResource workspace = await client
    .GetApiCenterWorkspaceResource(workspaceResourceId)
    .GetAsync();

await foreach (ApiCenterApiResource api in workspace.GetApiCenterApis())
{
    Console.WriteLine($"API: {api.Data.Title}");
    Console.WriteLine($"  Kind: {api.Data.Kind}");
    Console.WriteLine($"  Stage: {api.Data.LifecycleStage}");
    
    // 列出版本
    await foreach (ApiCenterApiVersionResource version in api.GetApiCenterApiVersions())
    {
        Console.WriteLine($"  Version: {version.Data.Title}");
    }
}

// 列出環境
await foreach (ApiCenterEnvironmentResource env in workspace.GetApiCenterEnvironments())
{
    Console.WriteLine($"Environment: {env.Data.Title} ({env.Data.Kind})");
}

// 列出部署
await foreach (ApiCenterDeploymentResource deployment in workspace.GetApiCenterDeployments())
{
    Console.WriteLine($"Deployment: {deployment.Data.Title}");
    Console.WriteLine($"  State: {deployment.Data.State}");
}
```

## 主要型別參考

| 型別 | 用途 |
|------|---------|
| `ApiCenterServiceResource` | API Center 服務執行個體 |
| `ApiCenterWorkspaceResource` | API 的邏輯分組 |
| `ApiCenterApiResource` | 單一 API |
| `ApiCenterApiVersionResource` | API 的版本 |
| `ApiCenterApiDefinitionResource` | API 規格（OpenAPI 等） |
| `ApiCenterEnvironmentResource` | 部署環境 |
| `ApiCenterDeploymentResource` | API 部署到環境 |
| `ApiCenterMetadataSchemaResource` | 自訂 metadata schema |
| `ApiKind` | rest, graphql, grpc, soap, webhook, websocket, mcp |
| `ApiLifecycleStage` | design, development, testing, preview, production, deprecated, retired |
| `ApiCenterEnvironmentKind` | development, testing, staging, production |
| `ApiCenterDeploymentState` | active, inactive |

## 最佳實務

1. **用 workspace 來組織**：依團隊、領域或產品把 API 分組
2. **用 metadata schema**：為治理定義自訂屬性
3. **追蹤生命週期階段**：隨時更新 API 狀態（design → production → deprecated）
4. **記錄環境**：包含上線指引和入口網站 URI
5. **版本一致**：API 版本用語意化版本號
6. **匯入規格**：上傳 OpenAPI/GraphQL 規格，方便探索
7. **串起部署**：把 API 連到它們的執行環境
8. **用 managed identity**：啟用 SystemAssigned identity，讓整合更安全

## 錯誤處理

```csharp
using Azure;

try
{
    ArmOperation<ApiCenterApiResource> operation = await apis
        .CreateOrUpdateAsync(WaitUntil.Completed, "my-api", apiData);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("API already exists with conflicting configuration");
}
catch (RequestFailedException ex) when (ex.Status == 400)
{
    Console.WriteLine($"Invalid request: {ex.Message}");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Azure error: {ex.Status} - {ex.Message}");
}
```

## 相關 SDK

| SDK | 用途 | 安裝 |
|-----|---------|---------|
| `Azure.ResourceManager.ApiCenter` | API Center 管理（就是這個 SDK） | `dotnet add package Azure.ResourceManager.ApiCenter` |
| `Azure.ResourceManager.ApiManagement` | API gateway 和 policy | `dotnet add package Azure.ResourceManager.ApiManagement` |

## 參考連結

| 資源 | URL |
|----------|-----|
| NuGet 套件 | https://www.nuget.org/packages/Azure.ResourceManager.ApiCenter |
| API 參考 | https://learn.microsoft.com/dotnet/api/azure.resourcemanager.apicenter |
| 產品文件 | https://learn.microsoft.com/azure/api-center/ |
| GitHub 原始碼 | https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/apicenter/Azure.ResourceManager.ApiCenter |
