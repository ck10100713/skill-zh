---
name: azure-mgmt-mongodbatlas-dotnet
description: 用 Azure.ResourceManager.MongoDBAtlas SDK，把 MongoDB Atlas Organization 當成 Azure ARM 資源來管理。透過 Azure Marketplace 整合建立、更新、列出或刪除 MongoDB Atlas organization 時使用。這個 SDK 管理的是 Azure 端的 organization 資源，不直接管理 Atlas 的叢集/資料庫。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.ResourceManager.MongoDBAtlas
---

# Azure.ResourceManager.MongoDBAtlas SDK

把 MongoDB Atlas Organization 當成 Azure ARM 資源來管理，並透過 Azure Marketplace 統一計費。

## 套件資訊

| 屬性 | 值 |
|----------|-------|
| 套件 | `Azure.ResourceManager.MongoDBAtlas` |
| 版本 | 1.0.0 (GA) |
| API 版本 | 2025-06-01 |
| 資源類型 | `MongoDB.Atlas/organizations` |
| NuGet | [Azure.ResourceManager.MongoDBAtlas](https://www.nuget.org/packages/Azure.ResourceManager.MongoDBAtlas) |

## 安裝

```bash
dotnet add package Azure.ResourceManager.MongoDBAtlas
dotnet add package Azure.Identity
dotnet add package Azure.ResourceManager
```

## 重要的範圍限制

這個 SDK 管理的是為了 marketplace 整合而存在的、**當成 Azure ARM 資源的 MongoDB Atlas Organization**。它**不**直接管理：
- Atlas 叢集
- 資料庫
- Collection
- 使用者/角色

要管理叢集，建立好 organization 之後，直接用 MongoDB Atlas API。

## 環境變數

```bash
AZURE_SUBSCRIPTION_ID=<your-subscription-id> # 必填：Azure subscription ID
AZURE_RESOURCE_GROUP=<your-resource-group> # 必填：Azure resource group 名稱
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境用 DefaultAzureCredential 時才需要
AZURE_TENANT_ID=<your-tenant-id> # 服務主體認證用（選填）
AZURE_CLIENT_ID=<your-client-id> # 服務主體認證用（選填）
AZURE_CLIENT_SECRET=<your-client-secret> # 服務主體認證用（選填）
```

## 認證

```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.MongoDBAtlas;
using Azure.ResourceManager.MongoDBAtlas.Models;

// 本機開發：DefaultAzureCredential。正式環境：設 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
var credential = new DefaultAzureCredential(
    DefaultAzureCredential.DefaultEnvironmentVariableName
);
// 或在正式環境直接用特定的 credential：
// 見 https://learn.microsoft.com/dotnet/api/overview/azure/identity-readme?view=azure-dotnet#credential-classes
// var credential = new ManagedIdentityCredential();
var armClient = new ArmClient(credential);
```

## 核心型別

| 型別 | 用途 |
|------|---------|
| `MongoDBAtlasOrganizationResource` | 代表 Atlas organization 的 ARM 資源 |
| `MongoDBAtlasOrganizationCollection` | Resource group 裡 organization 的集合 |
| `MongoDBAtlasOrganizationData` | Organization 資源的資料模型 |
| `MongoDBAtlasOrganizationProperties` | Organization 專屬屬性 |
| `MongoDBAtlasMarketplaceDetails` | Azure Marketplace subscription 詳細資料 |
| `MongoDBAtlasOfferDetails` | Marketplace offer 設定 |
| `MongoDBAtlasUserDetails` | Organization 的使用者資訊 |
| `MongoDBAtlasPartnerProperties` | MongoDB 專屬屬性（org 名稱、ID） |

## 工作流程

### 取得 Organization 集合

```csharp
// 取得 resource group
var subscription = await armClient.GetDefaultSubscriptionAsync();
var resourceGroup = await subscription.GetResourceGroupAsync("my-resource-group");

// 取得 organization 集合
MongoDBAtlasOrganizationCollection organizations = 
    resourceGroup.Value.GetMongoDBAtlasOrganizations();
```

### 建立 Organization

```csharp
var organizationName = "my-atlas-org";
var location = AzureLocation.EastUS2;

// 建立 organization 資料
var organizationData = new MongoDBAtlasOrganizationData(location)
{
    Properties = new MongoDBAtlasOrganizationProperties(
        marketplace: new MongoDBAtlasMarketplaceDetails(
            subscriptionId: "your-azure-subscription-id",
            offerDetails: new MongoDBAtlasOfferDetails(
                publisherId: "mongodb",
                offerId: "mongodb_atlas_azure_native_prod",
                planId: "private_plan",
                planName: "Pay as You Go (Free) (Private)",
                termUnit: "P1M",
                termId: "gmz7xq9ge3py"
            )
        ),
        user: new MongoDBAtlasUserDetails(
            emailAddress: "admin@example.com",
            upn: "admin@example.com"
        )
        {
            FirstName = "Admin",
            LastName = "User"
        }
    )
    {
        PartnerProperties = new MongoDBAtlasPartnerProperties
        {
            OrganizationName = organizationName
        }
    },
    Tags = { ["Environment"] = "Production" }
};

// 建立 organization（長時間執行的操作）
var operation = await organizations.CreateOrUpdateAsync(
    WaitUntil.Completed,
    organizationName,
    organizationData
);

MongoDBAtlasOrganizationResource organization = operation.Value;
Console.WriteLine($"Created: {organization.Id}");
```

### 取得既有 Organization

```csharp
// 做法 1：從集合取得
MongoDBAtlasOrganizationResource org = 
    await organizations.GetAsync("my-atlas-org");

// 做法 2：從 resource identifier 取得
var resourceId = MongoDBAtlasOrganizationResource.CreateResourceIdentifier(
    subscriptionId: "subscription-id",
    resourceGroupName: "my-resource-group",
    organizationName: "my-atlas-org"
);
MongoDBAtlasOrganizationResource org2 = 
    armClient.GetMongoDBAtlasOrganizationResource(resourceId);
await org2.GetAsync(); // 抓取資料
```

### 列出 Organization

```csharp
// 列出 resource group 裡的
await foreach (var org in organizations.GetAllAsync())
{
    Console.WriteLine($"Org: {org.Data.Name}");
    Console.WriteLine($"  Location: {org.Data.Location}");
    Console.WriteLine($"  State: {org.Data.Properties?.ProvisioningState}");
}

// 列出整個 subscription 的
await foreach (var org in subscription.GetMongoDBAtlasOrganizationsAsync())
{
    Console.WriteLine($"Org: {org.Data.Name} in {org.Data.Id}");
}
```

### 更新 Tag

```csharp
// 新增單一 tag
await organization.AddTagAsync("CostCenter", "12345");

// 取代所有 tag
await organization.SetTagsAsync(new Dictionary<string, string>
{
    ["Environment"] = "Production",
    ["Team"] = "Platform"
});

// 移除 tag
await organization.RemoveTagAsync("OldTag");
```

### 更新 Organization 屬性

```csharp
var patch = new MongoDBAtlasOrganizationPatch
{
    Tags = { ["UpdatedAt"] = DateTime.UtcNow.ToString("o") },
    Properties = new MongoDBAtlasOrganizationUpdateProperties
    {
        // 需要的話，更新使用者資料
        User = new MongoDBAtlasUserDetails(
            emailAddress: "newadmin@example.com",
            upn: "newadmin@example.com"
        )
    }
};

var updateOperation = await organization.UpdateAsync(
    WaitUntil.Completed,
    patch
);
```

### 刪除 Organization

```csharp
// 刪除（長時間執行的操作）
await organization.DeleteAsync(WaitUntil.Completed);
```

## Model 屬性參考

### MongoDBAtlasOrganizationProperties

| 屬性 | 型別 | 說明 |
|----------|------|-------------|
| `Marketplace` | `MongoDBAtlasMarketplaceDetails` | 必填。Marketplace subscription 詳細資料 |
| `User` | `MongoDBAtlasUserDetails` | 必填。Organization 管理員使用者 |
| `PartnerProperties` | `MongoDBAtlasPartnerProperties` | MongoDB 專屬屬性 |
| `ProvisioningState` | `MongoDBAtlasResourceProvisioningState` | 唯讀。目前的佈建狀態 |

### MongoDBAtlasMarketplaceDetails

| 屬性 | 型別 | 說明 |
|----------|------|-------------|
| `SubscriptionId` | `string` | 必填。計費用的 Azure subscription ID |
| `OfferDetails` | `MongoDBAtlasOfferDetails` | 必填。Marketplace offer 設定 |
| `SubscriptionStatus` | `MarketplaceSubscriptionStatus` | 唯讀。Subscription 狀態 |

### MongoDBAtlasOfferDetails

| 屬性 | 型別 | 說明 |
|----------|------|-------------|
| `PublisherId` | `string` | 必填。Publisher ID（通常是 "mongodb"） |
| `OfferId` | `string` | 必填。Offer ID |
| `PlanId` | `string` | 必填。Plan ID |
| `PlanName` | `string` | 必填。方案的顯示名稱 |
| `TermUnit` | `string` | 必填。計費期間單位（例如 "P1M"） |
| `TermId` | `string` | 必填。期間識別碼 |

### MongoDBAtlasUserDetails

| 屬性 | 型別 | 說明 |
|----------|------|-------------|
| `EmailAddress` | `string` | 必填。使用者 email 地址 |
| `Upn` | `string` | 必填。使用者主體名稱 |
| `FirstName` | `string` | 選填。使用者名字 |
| `LastName` | `string` | 選填。使用者姓氏 |

### MongoDBAtlasPartnerProperties

| 屬性 | 型別 | 說明 |
|----------|------|-------------|
| `OrganizationName` | `string` | MongoDB Atlas organization 的名稱 |
| `OrganizationId` | `string` | 唯讀。MongoDB Atlas organization 的 ID |

## 佈建狀態

| 狀態 | 說明 |
|-------|-------------|
| `Succeeded` | 資源佈建成功 |
| `Failed` | 佈建失敗 |
| `Canceled` | 佈建被取消 |
| `Provisioning` | 資源佈建中 |
| `Updating` | 資源更新中 |
| `Deleting` | 資源刪除中 |
| `Accepted` | 請求已接受，即將開始佈建 |

## Marketplace Subscription 狀態

| 狀態 | 說明 |
|--------|-------------|
| `PendingFulfillmentStart` | Subscription 等待啟用 |
| `Subscribed` | Subscription 有效 |
| `Suspended` | Subscription 已暫停 |
| `Unsubscribed` | Subscription 已取消 |

## 最佳實務

### 用 Async 方法

```csharp
// 所有操作都優先用 async
var org = await organizations.GetAsync("my-org");
await org.Value.AddTagAsync("key", "value");
```

### 處理長時間執行的操作

```csharp
// 等到完成
var operation = await organizations.CreateOrUpdateAsync(
    WaitUntil.Completed,  // 阻塞直到完成
    name,
    data
);

// 或先開始，之後再輪詢
var operation = await organizations.CreateOrUpdateAsync(
    WaitUntil.Started,  // 立刻回傳
    name,
    data
);

// 輪詢是否完成
while (!operation.HasCompleted)
{
    await Task.Delay(TimeSpan.FromSeconds(5));
    await operation.UpdateStatusAsync();
}
```

### 檢查佈建狀態

```csharp
var org = await organizations.GetAsync("my-org");
if (org.Value.Data.Properties?.ProvisioningState == 
    MongoDBAtlasResourceProvisioningState.Succeeded)
{
    Console.WriteLine("Organization is ready");
}
```

### 用 Resource Identifier

```csharp
// 不用呼叫 API 就建立 identifier
var resourceId = MongoDBAtlasOrganizationResource.CreateResourceIdentifier(
    subscriptionId,
    resourceGroupName,
    organizationName
);

// 取得資源 handle（還沒有資料）
var orgResource = armClient.GetMongoDBAtlasOrganizationResource(resourceId);

// 需要時再抓資料
var response = await orgResource.GetAsync();
```

## 常見錯誤

| 錯誤 | 原因 | 解法 |
|-------|-------|----------|
| `ResourceNotFound` | Organization 不存在 | 確認名稱和 resource group |
| `AuthorizationFailed` | 權限不足 | 檢查 resource group 上的 RBAC 角色 |
| `InvalidParameter` | 缺少必要屬性 | 確保所有必填欄位都有設定 |
| `MarketplaceError` | Marketplace subscription 的問題 | 確認 offer 詳細資料和 subscription |

## 相關資源

- [Microsoft Learn: MongoDB Atlas on Azure](https://learn.microsoft.com/en-us/azure/partner-solutions/mongodb-atlas/)
- [API 參考](https://learn.microsoft.com/en-us/dotnet/api/azure.resourcemanager.mongodbatlas)
- [Azure SDK for .NET](https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/mongodbatlas)
