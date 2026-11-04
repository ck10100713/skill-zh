---
name: azure-mgmt-fabric-dotnet
description: |
  .NET 用的 Azure Resource Manager SDK，管理 Fabric。用於管理平面（MANAGEMENT PLANE）操作：透過 Azure Resource Manager 佈建、擴縮、暫停/恢復 Microsoft Fabric capacity、檢查名稱可用性，以及列出 SKU。Triggers: "Fabric capacity", "create capacity", "suspend capacity", "resume capacity", "Fabric SKU", "provision Fabric", "ARM Fabric", "FabricCapacityResource".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.ResourceManager.Fabric
---

# Azure.ResourceManager.Fabric (.NET)

管理平面 SDK，透過 Azure Resource Manager 佈建和管理 Microsoft Fabric capacity 資源。

> **只限管理平面**
> 這個 SDK 管理的是 Fabric 的 *capacity*（運算資源）。要操作 Fabric 的 workspace、lakehouse、warehouse 和資料項目，請用 Microsoft Fabric REST API 或資料平面 SDK。

## 安裝

```bash
dotnet add package Azure.ResourceManager.Fabric
dotnet add package Azure.Identity
```

**目前版本**：1.0.0（GA，2025 年 9 月）  
**API 版本**：2023-11-01  
**目標框架**：.NET 8.0、.NET Standard 2.0

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
using Azure.ResourceManager.Fabric;

// 本機開發：DefaultAzureCredential。正式環境：設 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
var credential = new DefaultAzureCredential(
    DefaultAzureCredential.DefaultEnvironmentVariableName
);
// 或在正式環境直接用特定的 credential：
// 見 https://learn.microsoft.com/dotnet/api/overview/azure/identity-readme?view=azure-dotnet#credential-classes
// var credential = new ManagedIdentityCredential();
var armClient = new ArmClient(credential);

// 取得 subscription
var subscription = await armClient.GetDefaultSubscriptionAsync();
```

## 資源階層

```
ArmClient
└── SubscriptionResource
    └── ResourceGroupResource
        └── FabricCapacityResource
```

## 核心工作流程

### 1. 建立 Fabric Capacity

```csharp
using Azure.ResourceManager.Fabric;
using Azure.ResourceManager.Fabric.Models;
using Azure.Core;

// 取得 resource group
var resourceGroup = await subscription.GetResourceGroupAsync("my-resource-group");

// 定義 capacity 設定
var administration = new FabricCapacityAdministration(
    new[] { "admin@contoso.com" }  // Capacity 管理員（UPN 或 object ID）
);

var properties = new FabricCapacityProperties(administration);

var sku = new FabricSku("F64", FabricSkuTier.Fabric);

var capacityData = new FabricCapacityData(
    AzureLocation.WestUS2,
    properties,
    sku)
{
    Tags = { ["Environment"] = "Production" }
};

// 建立 capacity（長時間執行的操作）
var capacityCollection = resourceGroup.Value.GetFabricCapacities();
var operation = await capacityCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-fabric-capacity",
    capacityData);

FabricCapacityResource capacity = operation.Value;
Console.WriteLine($"Created capacity: {capacity.Data.Name}");
Console.WriteLine($"State: {capacity.Data.Properties.State}");
```

### 2. 取得 Fabric Capacity

```csharp
// 取得既有的 capacity
var capacity = await resourceGroup.Value
    .GetFabricCapacityAsync("my-fabric-capacity");

Console.WriteLine($"Name: {capacity.Value.Data.Name}");
Console.WriteLine($"Location: {capacity.Value.Data.Location}");
Console.WriteLine($"SKU: {capacity.Value.Data.Sku.Name}");
Console.WriteLine($"State: {capacity.Value.Data.Properties.State}");
Console.WriteLine($"Provisioning State: {capacity.Value.Data.Properties.ProvisioningState}");
```

### 3. 更新 Capacity（調整 SKU 或更換管理員）

```csharp
var capacity = await resourceGroup.Value
    .GetFabricCapacityAsync("my-fabric-capacity");

var patch = new FabricCapacityPatch
{
    Sku = new FabricSku("F128", FabricSkuTier.Fabric),  // 擴大
    Properties = new FabricCapacityUpdateProperties
    {
        Administration = new FabricCapacityAdministration(
            new[] { "admin@contoso.com", "newadmin@contoso.com" }
        )
    }
};

var updateOperation = await capacity.Value.UpdateAsync(
    WaitUntil.Completed,
    patch);

Console.WriteLine($"Updated SKU: {updateOperation.Value.Data.Sku.Name}");
```

### 4. 暫停與恢復 Capacity

```csharp
// 暫停 capacity（停止運算計費）
await capacity.Value.SuspendAsync(WaitUntil.Completed);
Console.WriteLine("Capacity suspended");

// 恢復 capacity
var resumeOperation = await capacity.Value.ResumeAsync(WaitUntil.Completed);
Console.WriteLine($"Capacity resumed. State: {resumeOperation.Value.Data.Properties.State}");
```

### 5. 刪除 Capacity

```csharp
await capacity.Value.DeleteAsync(WaitUntil.Completed);
Console.WriteLine("Capacity deleted");
```

### 6. 列出所有 Capacity

```csharp
// 在 resource group 裡
await foreach (var cap in resourceGroup.Value.GetFabricCapacities())
{
    Console.WriteLine($"- {cap.Data.Name} ({cap.Data.Sku.Name})");
}

// 在 subscription 裡
await foreach (var cap in subscription.GetFabricCapacitiesAsync())
{
    Console.WriteLine($"- {cap.Data.Name} in {cap.Data.Location}");
}
```

### 7. 檢查名稱可用性

```csharp
var checkContent = new FabricNameAvailabilityContent
{
    Name = "my-new-capacity",
    ResourceType = "Microsoft.Fabric/capacities"
};

var result = await subscription.CheckFabricCapacityNameAvailabilityAsync(
    AzureLocation.WestUS2,
    checkContent);

if (result.Value.IsNameAvailable == true)
{
    Console.WriteLine("Name is available!");
}
else
{
    Console.WriteLine($"Name unavailable: {result.Value.Reason} - {result.Value.Message}");
}
```

### 8. 列出可用的 SKU

```csharp
// 列出 subscription 裡所有可用的 SKU
await foreach (var skuDetails in subscription.GetSkusFabricCapacitiesAsync())
{
    Console.WriteLine($"SKU: {skuDetails.Name}");
    Console.WriteLine($"  Resource Type: {skuDetails.ResourceType}");
    foreach (var location in skuDetails.Locations)
    {
        Console.WriteLine($"  Location: {location}");
    }
}

// 列出既有 capacity 可用的 SKU（用於擴縮）
await foreach (var skuDetails in capacity.Value.GetSkusForCapacityAsync())
{
    Console.WriteLine($"Can scale to: {skuDetails.Sku.Name}");
}
```

## SKU 參考

| SKU 名稱 | Capacity Unit (CU) | 對應的 Power BI |
|----------|---------------------|---------------------|
| F2 | 2 | - |
| F4 | 4 | - |
| F8 | 8 | EM1/A1 |
| F16 | 16 | EM2/A2 |
| F32 | 32 | EM3/A3 |
| F64 | 64 | P1/A4 |
| F128 | 128 | P2/A5 |
| F256 | 256 | P3/A6 |
| F512 | 512 | P4/A7 |
| F1024 | 1024 | P5/A8 |
| F2048 | 2048 | - |

## 主要型別參考

| 型別 | 用途 |
|------|---------|
| `ArmClient` | 所有 ARM 操作的進入點 |
| `FabricCapacityResource` | 代表一個 Fabric capacity 執行個體 |
| `FabricCapacityCollection` | Capacity CRUD 操作用的集合 |
| `FabricCapacityData` | Capacity 建立/讀取的資料模型 |
| `FabricCapacityPatch` | Capacity 更新的 payload |
| `FabricCapacityProperties` | Capacity 屬性（管理員、狀態） |
| `FabricCapacityAdministration` | 管理員成員設定 |
| `FabricSku` | SKU 設定（名稱和層級） |
| `FabricSkuTier` | 定價層（目前只有 "Fabric"） |
| `FabricProvisioningState` | 佈建狀態（Succeeded、Failed 等） |
| `FabricResourceState` | 資源狀態（Active、Suspended 等） |
| `FabricNameAvailabilityContent` | 名稱可用性檢查請求 |
| `FabricNameAvailabilityResult` | 名稱可用性檢查回應 |

## 佈建狀態與資源狀態

### 佈建狀態（`FabricProvisioningState`）
- `Succeeded`：操作成功完成
- `Failed`：操作失敗
- `Canceled`：操作被取消
- `Deleting`：Capacity 刪除中
- `Provisioning`：初始佈建進行中
- `Updating`：更新操作進行中

### 資源狀態（`FabricResourceState`）
- `Active`：Capacity 運作中且可用
- `Provisioning`：佈建中
- `Failed`：處於失敗狀態
- `Updating`：更新中
- `Deleting`：刪除中
- `Suspending`：轉換成暫停中
- `Suspended`：已暫停（不計運算費用）
- `Pausing`：轉換成暫停（paused）中
- `Paused`：已暫停（paused）
- `Resuming`：從 suspended/paused 恢復中
- `Scaling`：正在調整成不同 SKU
- `Preparing`：準備資源中

## 最佳實務

1. 操作必須完成才能繼續時，用 **`WaitUntil.Completed`**
2. 想自己輪詢或平行執行操作時，用 **`WaitUntil.Started`**
3. **用 `DefaultAzureCredential`**，絕對不要把憑證寫死在程式碼裡
4. ARM API 錯誤要處理 **`RequestFailedException`**
5. 冪等的操作用 **`CreateOrUpdateAsync`**
6. **不用的時候就暫停**：Fabric capacity 即使閒置也會計算運算費用
7. 對 capacity 做操作之前，**先檢查佈建狀態**
8. **選合適的 SKU**：開發/測試從小的（F2/F4）開始，正式環境再擴大

## 錯誤處理

```csharp
using Azure;

try
{
    var operation = await capacityCollection.CreateOrUpdateAsync(
        WaitUntil.Completed, capacityName, capacityData);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("Capacity already exists or conflict");
}
catch (RequestFailedException ex) when (ex.Status == 400)
{
    Console.WriteLine($"Invalid configuration: {ex.Message}");
}
catch (RequestFailedException ex) when (ex.Status == 403)
{
    Console.WriteLine("Insufficient permissions or quota exceeded");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"ARM Error: {ex.Status} - {ex.ErrorCode}: {ex.Message}");
}
```

## 常見陷阱

1. **Capacity 名稱必須全域唯一**：Fabric capacity 名稱在所有 Azure subscription 之間必須唯一
2. **Suspend 不是刪除**：暫停的 capacity 依然存在，只是不計運算費用
3. **SKU 變更可能需要停機**：擴縮操作可能要花好幾分鐘
4. **管理員 UPN 必須有效**：Capacity 管理員必須是有效的 Azure AD 使用者
5. **位置限制**：不是每個區域都有所有 SKU；用 `GetSkusFabricCapacitiesAsync` 檢查
6. **佈建時間很長**：建立 capacity 可能要 5 到 15 分鐘

## 相關 SDK

| SDK | 用途 | 安裝 |
|-----|---------|---------|
| `Azure.ResourceManager.Fabric` | 管理平面（就是這個 SDK） | `dotnet add package Azure.ResourceManager.Fabric` |
| `Microsoft.Fabric.Api` | 資料平面操作（beta） | `dotnet add package Microsoft.Fabric.Api --prerelease` |
| `Azure.ResourceManager` | 核心 ARM SDK | `dotnet add package Azure.ResourceManager` |
| `Azure.Identity` | 認證 | `dotnet add package Azure.Identity` |

## 參考資料

- [Azure.ResourceManager.Fabric NuGet](https://www.nuget.org/packages/Azure.ResourceManager.Fabric)
- [GitHub 原始碼](https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/fabric/Azure.ResourceManager.Fabric)
- [Microsoft Fabric 文件](https://learn.microsoft.com/fabric/)
- [Fabric Capacity 管理](https://learn.microsoft.com/fabric/admin/service-admin-portal-capacity-settings)
