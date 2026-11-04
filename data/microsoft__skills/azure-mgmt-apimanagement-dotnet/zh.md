---
name: azure-mgmt-apimanagement-dotnet
description: |
  .NET 用的 Azure Resource Manager SDK，管理 API Management。用於管理平面（MANAGEMENT PLANE）操作：透過 Azure Resource Manager 建立/管理 APIM 服務、API、product、subscription、policy、使用者、群組、gateway 和 backend。Triggers: "API Management", "APIM service", "create APIM", "manage APIs", "ApiManagementServiceResource", "API policies", "APIM products", "APIM subscriptions".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.ResourceManager.ApiManagement
---

# Azure.ResourceManager.ApiManagement (.NET)

管理平面 SDK，透過 Azure Resource Manager 佈建和管理 Azure API Management 資源。

> **⚠️ 管理平面 vs 資料平面**
> - **這個 SDK（Azure.ResourceManager.ApiManagement）**：建立服務、API、product、subscription、policy、使用者、群組
> - **資料平面**：直接呼叫你的 APIM gateway endpoint 上的 API

## 安裝

```bash
dotnet add package Azure.ResourceManager.ApiManagement
dotnet add package Azure.Identity
```

**目前版本**：v1.3.0

## 環境變數

```bash
AZURE_SUBSCRIPTION_ID=<your-subscription-id> # 必填：Azure subscription ID
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境用 DefaultAzureCredential 時才需要
AZURE_TENANT_ID=<tenant-id> # 服務主體認證用（選填）
AZURE_CLIENT_ID=<client-id> # 服務主體認證用（選填）
AZURE_CLIENT_SECRET=<client-secret> # 服務主體認證用（選填）
```

## 認證

```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.ApiManagement;

// 本機開發：DefaultAzureCredential。正式環境：設 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
var credential = new DefaultAzureCredential(
    DefaultAzureCredential.DefaultEnvironmentVariableName
);
// 或在正式環境直接用特定的 credential：
// 見 https://learn.microsoft.com/dotnet/api/overview/azure/identity-readme?view=azure-dotnet#credential-classes
// var credential = new ManagedIdentityCredential();
var armClient = new ArmClient(credential);

// 取得 subscription
var subscriptionId = Environment.GetEnvironmentVariable("AZURE_SUBSCRIPTION_ID");
var subscription = armClient.GetSubscriptionResource(
    new ResourceIdentifier($"/subscriptions/{subscriptionId}"));
```

## 資源階層

```
ArmClient
└── SubscriptionResource
    └── ResourceGroupResource
        └── ApiManagementServiceResource
            ├── ApiResource
            │   ├── ApiOperationResource
            │   │   └── ApiOperationPolicyResource
            │   ├── ApiPolicyResource
            │   ├── ApiSchemaResource
            │   └── ApiDiagnosticResource
            ├── ApiManagementProductResource
            │   ├── ProductApiResource
            │   ├── ProductGroupResource
            │   └── ProductPolicyResource
            ├── ApiManagementSubscriptionResource
            ├── ApiManagementPolicyResource
            ├── ApiManagementUserResource
            ├── ApiManagementGroupResource
            ├── ApiManagementBackendResource
            ├── ApiManagementGatewayResource
            ├── ApiManagementCertificateResource
            ├── ApiManagementNamedValueResource
            └── ApiManagementLoggerResource
```

## 核心工作流程

### 1. 建立 API Management 服務

```csharp
using Azure.ResourceManager.ApiManagement;
using Azure.ResourceManager.ApiManagement.Models;

// 取得 resource group
var resourceGroup = await subscription
    .GetResourceGroupAsync("my-resource-group");

// 定義服務
var serviceData = new ApiManagementServiceData(
    location: AzureLocation.EastUS,
    sku: new ApiManagementServiceSkuProperties(
        ApiManagementServiceSkuType.Developer, 
        capacity: 1),
    publisherEmail: "admin@contoso.com",
    publisherName: "Contoso");

// 建立服務（長時間執行的操作，可能超過 30 分鐘）
var serviceCollection = resourceGroup.Value.GetApiManagementServices();
var operation = await serviceCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-apim-service",
    serviceData);

ApiManagementServiceResource service = operation.Value;
```

### 2. 建立 API

```csharp
var apiData = new ApiCreateOrUpdateContent
{
    DisplayName = "My API",
    Path = "myapi",
    Protocols = { ApiOperationInvokableProtocol.Https },
    ServiceUri = new Uri("https://backend.contoso.com/api")
};

var apiCollection = service.GetApis();
var apiOperation = await apiCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-api",
    apiData);

ApiResource api = apiOperation.Value;
```

### 3. 建立 Product

```csharp
var productData = new ApiManagementProductData
{
    DisplayName = "Starter",
    Description = "Starter tier with limited access",
    IsSubscriptionRequired = true,
    IsApprovalRequired = false,
    SubscriptionsLimit = 1,
    State = ApiManagementProductState.Published
};

var productCollection = service.GetApiManagementProducts();
var productOperation = await productCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "starter",
    productData);

ApiManagementProductResource product = productOperation.Value;

// 把 API 加進 product
await product.GetProductApis().CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-api");
```

### 4. 建立 Subscription

```csharp
var subscriptionData = new ApiManagementSubscriptionCreateOrUpdateContent
{
    DisplayName = "My Subscription",
    Scope = $"/products/{product.Data.Name}",
    State = ApiManagementSubscriptionState.Active
};

var subscriptionCollection = service.GetApiManagementSubscriptions();
var subOperation = await subscriptionCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-subscription",
    subscriptionData);

ApiManagementSubscriptionResource subscription = subOperation.Value;

// 取得 subscription key
var keys = await subscription.GetSecretsAsync();
Console.WriteLine($"Primary Key: {keys.Value.PrimaryKey}");
```

### 5. 設定 API Policy

```csharp
var policyXml = @"
<policies>
    <inbound>
        <rate-limit calls=""100"" renewal-period=""60"" />
        <set-header name=""X-Custom-Header"" exists-action=""override"">
            <value>CustomValue</value>
        </set-header>
        <base />
    </inbound>
    <backend>
        <base />
    </backend>
    <outbound>
        <base />
    </outbound>
    <on-error>
        <base />
    </on-error>
</policies>";

var policyData = new PolicyContractData
{
    Value = policyXml,
    Format = PolicyContentFormat.Xml
};

await api.GetApiPolicy().CreateOrUpdateAsync(
    WaitUntil.Completed,
    policyData);
```

### 6. 備份與還原

```csharp
// 備份
var backupParams = new ApiManagementServiceBackupRestoreContent(
    storageAccount: "mystorageaccount",
    containerName: "apim-backups",
    backupName: "backup-2024-01-15")
{
    AccessType = StorageAccountAccessType.SystemAssignedManagedIdentity
};

await service.BackupAsync(WaitUntil.Completed, backupParams);

// 還原
await service.RestoreAsync(WaitUntil.Completed, backupParams);
```

## 主要型別參考

| 型別 | 用途 |
|------|---------|
| `ArmClient` | 所有 ARM 操作的進入點 |
| `ApiManagementServiceResource` | 代表一個 APIM 服務執行個體 |
| `ApiManagementServiceCollection` | 服務 CRUD 用的集合 |
| `ApiResource` | 代表一個 API |
| `ApiManagementProductResource` | 代表一個 product |
| `ApiManagementSubscriptionResource` | 代表一個 subscription |
| `ApiManagementPolicyResource` | 服務層級的 policy |
| `ApiPolicyResource` | API 層級的 policy |
| `ApiManagementUserResource` | 代表一個使用者 |
| `ApiManagementGroupResource` | 代表一個群組 |
| `ApiManagementBackendResource` | 代表一個 backend 服務 |
| `ApiManagementGatewayResource` | 代表一個自行代管的 gateway |

## SKU 類型

| SKU | 用途 | 容量 |
|-----|---------|----------|
| `Developer` | 開發/測試（沒有 SLA） | 1 |
| `Basic` | 入門級正式環境 | 1-2 |
| `Standard` | 中等工作負載 | 1-4 |
| `Premium` | 高可用性、多區域 | 每個區域 1-12 |
| `Consumption` | Serverless，依呼叫次數計費 | N/A |

## 最佳實務

1. 操作必須完成才能繼續時，用 **`WaitUntil.Completed`**
2. 像建立服務這種長時間操作（30 分鐘以上），用 **`WaitUntil.Started`**
3. **一律用 `DefaultAzureCredential`**，絕對不要把 key 寫死在程式碼裡
4. ARM API 錯誤要處理 **`RequestFailedException`**
5. 冪等的操作用 **`CreateOrUpdateAsync`**
6. 透過 `Get*` 方法**往下走階層**（例如 `service.GetApis()`）
7. **Policy 格式**：policy 用 XML 格式；也支援 JSON
8. **建立服務**：測試用 Developer SKU 最快（約 15-30 分鐘）

## 錯誤處理

```csharp
using Azure;

try
{
    var operation = await serviceCollection.CreateOrUpdateAsync(
        WaitUntil.Completed, serviceName, serviceData);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("Service already exists");
}
catch (RequestFailedException ex) when (ex.Status == 400)
{
    Console.WriteLine($"Bad request: {ex.Message}");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"ARM Error: {ex.Status} - {ex.ErrorCode}: {ex.Message}");
}
```

## 參考檔案

| 檔案 | 何時閱讀 |
|------|--------------|
| [references/service-management.md](references/service-management.md) | 服務 CRUD、SKU、網路、備份/還原 |
| [references/apis-operations.md](references/apis-operations.md) | API、operation、schema、版本控制 |
| [references/products-subscriptions.md](references/products-subscriptions.md) | Product、subscription、存取控制 |
| [references/policies.md](references/policies.md) | Policy XML 範式、scope、常用 policy |

## 相關資源

| 資源 | 用途 |
|----------|---------|
| [API Management 文件](https://learn.microsoft.com/en-us/azure/api-management/) | Azure 官方文件 |
| [Policy 參考](https://learn.microsoft.com/en-us/azure/api-management/api-management-policies) | 完整的 policy 參考 |
| [SDK 參考](https://learn.microsoft.com/en-us/dotnet/api/azure.resourcemanager.apimanagement) | .NET API 參考 |
