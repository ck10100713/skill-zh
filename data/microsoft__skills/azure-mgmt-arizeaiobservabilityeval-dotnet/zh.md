---
name: azure-mgmt-arizeaiobservabilityeval-dotnet
description: "Azure Resource Manager SDK，用於 Arize AI Observability and Evaluation（.NET）。透過 Azure Marketplace 在 Azure 上管理 Arize AI organization、建立/更新/刪除 Arize 資源，或把 Arize 的 ML 可觀測性整合進 .NET 應用程式時使用。Triggers: \"Arize AI\", \"ML observability\", \"ArizeAIObservabilityEval\", \"Arize organization\".\n"
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.ResourceManager.ArizeAIObservabilityEval
---

# Azure.ResourceManager.ArizeAIObservabilityEval

.NET SDK，用來管理 Azure 上的 Arize AI Observability and Evaluation 資源。

## 安裝

```bash
dotnet add package Azure.ResourceManager.ArizeAIObservabilityEval --version 1.0.0
```

## 套件資訊

| 屬性 | 值 |
|----------|-------|
| 套件 | `Azure.ResourceManager.ArizeAIObservabilityEval` |
| 版本 | `1.0.0` (GA) |
| API 版本 | `2024-10-01` |
| ARM 類型 | `ArizeAi.ObservabilityEval/organizations` |
| 相依套件 | `Azure.Core` >= 1.46.2、`Azure.ResourceManager` >= 1.13.1 |

## 環境變數

```bash
AZURE_SUBSCRIPTION_ID=<your-subscription-id> # 必填：Azure subscription ID
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境用 DefaultAzureCredential 時才需要
AZURE_TENANT_ID=<your-tenant-id> # 服務主體認證用（選填）
AZURE_CLIENT_ID=<your-client-id> # 服務主體認證用（選填）
AZURE_CLIENT_SECRET=<your-client-secret> # 服務主體認證用（選填）
```

## 認證

```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.ArizeAIObservabilityEval;

// 本機開發：DefaultAzureCredential。正式環境：設 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
var credential = new DefaultAzureCredential(
    DefaultAzureCredential.DefaultEnvironmentVariableName
);
// 或在正式環境直接用特定的 credential：
// 見 https://learn.microsoft.com/dotnet/api/overview/azure/identity-readme?view=azure-dotnet#credential-classes
// var credential = new ManagedIdentityCredential();
var armClient = new ArmClient(credential);
```

## 核心工作流程

### 建立 Arize AI Organization

```csharp
using Azure.Core;
using Azure.ResourceManager.Resources;
using Azure.ResourceManager.ArizeAIObservabilityEval;
using Azure.ResourceManager.ArizeAIObservabilityEval.Models;

// 取得 subscription 和 resource group
var subscriptionId = Environment.GetEnvironmentVariable("AZURE_SUBSCRIPTION_ID");
var subscription = await armClient.GetSubscriptionResource(
    SubscriptionResource.CreateResourceIdentifier(subscriptionId)).GetAsync();
var resourceGroup = await subscription.Value.GetResourceGroupAsync("my-resource-group");

// 取得 organization 集合
var collection = resourceGroup.Value.GetArizeAIObservabilityEvalOrganizations();

// 建立 organization 資料
var data = new ArizeAIObservabilityEvalOrganizationData(AzureLocation.EastUS)
{
    Properties = new ArizeAIObservabilityEvalOrganizationProperties
    {
        Marketplace = new ArizeAIObservabilityEvalMarketplaceDetails
        {
            SubscriptionId = "marketplace-subscription-id",
            OfferDetails = new ArizeAIObservabilityEvalOfferDetails
            {
                PublisherId = "arikimlabs1649082416596",
                OfferId = "arize-liftr-1",
                PlanId = "arize-liftr-1-plan",
                PlanName = "Arize AI Plan",
                TermUnit = "P1M",
                TermId = "term-id"
            }
        },
        User = new ArizeAIObservabilityEvalUserDetails
        {
            FirstName = "John",
            LastName = "Doe",
            EmailAddress = "john.doe@example.com"
        }
    },
    Tags = { ["environment"] = "production" }
};

// 建立（長時間執行的操作）
var operation = await collection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-arize-org",
    data);

var organization = operation.Value;
Console.WriteLine($"Created: {organization.Data.Name}");
```

### 取得 Organization

```csharp
// 做法 1：從集合取得
var org = await collection.GetAsync("my-arize-org");

// 做法 2：先檢查是否存在
var exists = await collection.ExistsAsync("my-arize-org");
if (exists.Value)
{
    var org = await collection.GetAsync("my-arize-org");
}

// 做法 3：GetIfExists（找不到時回傳 null）
var response = await collection.GetIfExistsAsync("my-arize-org");
if (response.HasValue)
{
    var org = response.Value;
}
```

### 列出 Organization

```csharp
// 列出 resource group 裡的
await foreach (var org in collection.GetAllAsync())
{
    Console.WriteLine($"Org: {org.Data.Name}, State: {org.Data.Properties?.ProvisioningState}");
}

// 列出 subscription 裡的
await foreach (var org in subscription.Value.GetArizeAIObservabilityEvalOrganizationsAsync())
{
    Console.WriteLine($"Org: {org.Data.Name}");
}
```

### 更新 Organization

```csharp
// 更新 tag
var org = await collection.GetAsync("my-arize-org");
var updateData = new ArizeAIObservabilityEvalOrganizationPatch
{
    Tags = { ["environment"] = "staging", ["team"] = "ml-ops" }
};
var updated = await org.Value.UpdateAsync(updateData);
```

### 刪除 Organization

```csharp
var org = await collection.GetAsync("my-arize-org");
await org.Value.DeleteAsync(WaitUntil.Completed);
```

## 主要型別

| 型別 | 用途 |
|------|---------|
| `ArizeAIObservabilityEvalOrganizationResource` | Arize organization 的主要 ARM 資源 |
| `ArizeAIObservabilityEvalOrganizationCollection` | CRUD 操作用的集合 |
| `ArizeAIObservabilityEvalOrganizationData` | 資源資料模型 |
| `ArizeAIObservabilityEvalOrganizationProperties` | Organization 屬性 |
| `ArizeAIObservabilityEvalMarketplaceDetails` | Azure Marketplace subscription 資訊 |
| `ArizeAIObservabilityEvalOfferDetails` | Marketplace offer 設定 |
| `ArizeAIObservabilityEvalUserDetails` | 使用者聯絡資訊 |
| `ArizeAIObservabilityEvalOrganizationPatch` | 更新用的 patch 模型 |
| `ArizeAIObservabilityEvalSingleSignOnPropertiesV2` | SSO 設定 |

## Enum

| Enum | 值 |
|------|--------|
| `ArizeAIObservabilityEvalOfferProvisioningState` | `Succeeded`, `Failed`, `Canceled`, `Provisioning`, `Updating`, `Deleting`, `Accepted` |
| `ArizeAIObservabilityEvalMarketplaceSubscriptionStatus` | `PendingFulfillmentStart`, `Subscribed`, `Suspended`, `Unsubscribed` |
| `ArizeAIObservabilityEvalSingleSignOnState` | `Initial`, `Enable`, `Disable` |
| `ArizeAIObservabilityEvalSingleSignOnType` | `Saml`, `OpenId` |

## 最佳實務

1. **用 async 方法**：所有操作都支援 async/await
2. **處理長時間執行的操作**：用 `WaitUntil.Completed`，或自己輪詢
3. **用 GetIfExistsAsync**：條件判斷時避免靠例外處理
4. **實作重試策略**：透過 `ArmClientOptions` 設定
5. **用 resource identifier**：不用列舉就能直接存取資源
6. **正確關閉 client**：用 `using` 陳述式或明確 dispose

## 錯誤處理

```csharp
try
{
    var org = await collection.GetAsync("my-arize-org");
}
catch (Azure.RequestFailedException ex) when (ex.Status == 404)
{
    Console.WriteLine("Organization not found");
}
catch (Azure.RequestFailedException ex)
{
    Console.WriteLine($"Azure error: {ex.Message}");
}
```

## 直接存取資源

```csharp
// 直接用 ID 存取資源（不用列舉）
var resourceId = ArizeAIObservabilityEvalOrganizationResource.CreateResourceIdentifier(
    subscriptionId,
    "my-resource-group",
    "my-arize-org");

var org = armClient.GetArizeAIObservabilityEvalOrganizationResource(resourceId);
var data = await org.GetAsync();
```

## 連結

- [NuGet 套件](https://www.nuget.org/packages/Azure.ResourceManager.ArizeAIObservabilityEval)
- [Azure SDK for .NET](https://github.com/Azure/azure-sdk-for-net)
- [Arize AI](https://arize.com/)
