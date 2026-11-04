---
name: azure-resource-manager-durabletask-dotnet
description: |
  .NET 版 Durable Task Scheduler 的 Azure Resource Manager SDK。用於 MANAGEMENT PLANE（管理平面）操作：透過 Azure Resource Manager 建立／管理 Durable Task Scheduler、Task Hub 與保留政策。Triggers: "Durable Task Scheduler", "create scheduler", "task hub", "DurableTaskSchedulerResource", "provision Durable Task", "orchestration scheduler".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.ResourceManager.DurableTask
---

# Azure.ResourceManager.DurableTask (.NET)

管理平面 SDK，透過 Azure Resource Manager 佈建與管理 Azure Durable Task Scheduler 資源。

> **⚠️ 管理平面 vs Data Plane**
> - **這個 SDK（Azure.ResourceManager.DurableTask）**：建立 scheduler、task hub，設定保留政策
> - **Data Plane SDK（Microsoft.DurableTask.Client.AzureManaged）**：啟動 orchestration、查詢 instance、傳送事件

## 安裝

```bash
dotnet add package Azure.ResourceManager.DurableTask
dotnet add package Azure.Identity
```

**目前版本**：Stable v1.0.0 (2025-11-03)、Preview v1.0.0-beta.1 (2025-04-24)
**API 版本**：2025-11-01

## 環境變數

```bash
AZURE_SUBSCRIPTION_ID=<your-subscription-id> # 必填：Azure subscription ID
AZURE_RESOURCE_GROUP=<your-resource-group> # 必填：Azure resource group 名稱
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境使用 DefaultAzureCredential 時才需要
AZURE_TENANT_ID=<tenant-id> # 用於 service principal 驗證（選填）
AZURE_CLIENT_ID=<client-id> # 用於 service principal 驗證（選填）
AZURE_CLIENT_SECRET=<client-secret> # 用於 service principal 驗證（選填）
```

## 驗證

```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.DurableTask;

// 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
var credential = new DefaultAzureCredential(
    DefaultAzureCredential.DefaultEnvironmentVariableName
);
// 或在正式環境直接使用特定的 credential：
// See https://learn.microsoft.com/dotnet/api/overview/azure/identity-readme?view=azure-dotnet#credential-classes
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
        └── DurableTaskSchedulerResource
            ├── DurableTaskHubResource
            └── DurableTaskRetentionPolicyResource
```

## 核心流程

### 1. 建立 Durable Task Scheduler

```csharp
using Azure.ResourceManager.DurableTask;
using Azure.ResourceManager.DurableTask.Models;

// 取得 resource group
var resourceGroup = await subscription
    .GetResourceGroupAsync("my-resource-group");

// 定義使用 Dedicated SKU 的 scheduler
var schedulerData = new DurableTaskSchedulerData(AzureLocation.EastUS)
{
    Properties = new DurableTaskSchedulerProperties
    {
        Sku = new DurableTaskSchedulerSku(DurableTaskSchedulerSkuName.Dedicated)
        {
            Capacity = 1  // instance 數量
        },
        // 選用：用於網路安全的 IP 允許清單
        IPAllowlist = { "10.0.0.0/24", "192.168.1.0/24" }
    }
};

// 建立 scheduler（長時間執行的操作）
var schedulerCollection = resourceGroup.Value.GetDurableTaskSchedulers();
var operation = await schedulerCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-scheduler",
    schedulerData);

DurableTaskSchedulerResource scheduler = operation.Value;
Console.WriteLine($"Scheduler created: {scheduler.Data.Name}");
Console.WriteLine($"Endpoint: {scheduler.Data.Properties.Endpoint}");
```

### 2. 用 Consumption SKU 建立 Scheduler

```csharp
// Consumption SKU（serverless）
var consumptionSchedulerData = new DurableTaskSchedulerData(AzureLocation.EastUS)
{
    Properties = new DurableTaskSchedulerProperties
    {
        Sku = new DurableTaskSchedulerSku(DurableTaskSchedulerSkuName.Consumption)
        // consumption 不需要設定容量
    }
};

var operation = await schedulerCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-serverless-scheduler",
    consumptionSchedulerData);
```

### 3. 建立 Task Hub

```csharp
// Task hub 建立在 scheduler 底下
var taskHubData = new DurableTaskHubData
{
    // 基本的 task hub 不一定要設定 Properties
};

var taskHubCollection = scheduler.GetDurableTaskHubs();
var hubOperation = await taskHubCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-taskhub",
    taskHubData);

DurableTaskHubResource taskHub = hubOperation.Value;
Console.WriteLine($"Task Hub created: {taskHub.Data.Name}");
```

### 4. 列出 Scheduler

```csharp
// 列出 subscription 內所有 scheduler
await foreach (var sched in subscription.GetDurableTaskSchedulersAsync())
{
    Console.WriteLine($"Scheduler: {sched.Data.Name}");
    Console.WriteLine($"  Location: {sched.Data.Location}");
    Console.WriteLine($"  SKU: {sched.Data.Properties.Sku?.Name}");
    Console.WriteLine($"  Endpoint: {sched.Data.Properties.Endpoint}");
}

// 列出 resource group 內的 scheduler
var schedulers = resourceGroup.Value.GetDurableTaskSchedulers();
await foreach (var sched in schedulers.GetAllAsync())
{
    Console.WriteLine($"Scheduler: {sched.Data.Name}");
}
```

### 5. 依名稱取得 Scheduler

```csharp
// 取得既有的 scheduler
var existingScheduler = await schedulerCollection.GetAsync("my-scheduler");
Console.WriteLine($"Found: {existingScheduler.Value.Data.Name}");

// 或使用 extension method
var schedulerResource = armClient.GetDurableTaskSchedulerResource(
    DurableTaskSchedulerResource.CreateResourceIdentifier(
        subscriptionId,
        "my-resource-group",
        "my-scheduler"));
var scheduler = await schedulerResource.GetAsync();
```

### 6. 更新 Scheduler

```csharp
// 取得目前的 scheduler
var scheduler = await schedulerCollection.GetAsync("my-scheduler");

// 用新設定更新
var updateData = new DurableTaskSchedulerData(scheduler.Value.Data.Location)
{
    Properties = new DurableTaskSchedulerProperties
    {
        Sku = new DurableTaskSchedulerSku(DurableTaskSchedulerSkuName.Dedicated)
        {
            Capacity = 2  // 擴充
        },
        IPAllowlist = { "10.0.0.0/16" }  // 更新 IP 允許清單
    }
};

var updateOperation = await schedulerCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-scheduler",
    updateData);
```

### 7. 刪除資源

```csharp
// 先刪除 task hub
var taskHub = await scheduler.GetDurableTaskHubs().GetAsync("my-taskhub");
await taskHub.Value.DeleteAsync(WaitUntil.Completed);

// 再刪除 scheduler
await scheduler.DeleteAsync(WaitUntil.Completed);
```

### 8. 管理保留政策

```csharp
// 取得保留政策集合
var retentionPolicies = scheduler.GetDurableTaskRetentionPolicies();

// 建立或更新保留政策
var retentionData = new DurableTaskRetentionPolicyData
{
    Properties = new DurableTaskRetentionPolicyProperties
    {
        // 設定保留相關參數
    }
};

var retentionOperation = await retentionPolicies.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "default",  // 政策名稱
    retentionData);
```

## 主要型別參考

| 型別 | 用途 |
|------|---------|
| `ArmClient` | 所有 ARM 操作的進入點 |
| `DurableTaskSchedulerResource` | 代表一個 Durable Task Scheduler |
| `DurableTaskSchedulerCollection` | scheduler CRUD 的集合 |
| `DurableTaskSchedulerData` | scheduler 建立／更新的 payload |
| `DurableTaskSchedulerProperties` | Scheduler 設定（SKU、IPAllowlist） |
| `DurableTaskSchedulerSku` | SKU 設定（Name、Capacity、RedundancyState） |
| `DurableTaskSchedulerSkuName` | SKU 選項：`Dedicated`、`Consumption` |
| `DurableTaskHubResource` | 代表一個 Task Hub |
| `DurableTaskHubCollection` | task hub CRUD 的集合 |
| `DurableTaskHubData` | task hub 建立的 payload |
| `DurableTaskRetentionPolicyResource` | 保留政策管理 |
| `DurableTaskRetentionPolicyData` | 保留政策設定 |
| `DurableTaskExtensions` | ARM client 的 extension method |

## SKU 選項

| SKU | 說明 | 使用情境 |
|-----|-------------|----------|
| `Dedicated` | 固定容量，instance 數量可設定 | 正式環境工作負載、需要可預期的效能 |
| `Consumption` | Serverless、自動擴縮 | 開發、變動的工作負載 |

## Extension Method

SDK 在 `SubscriptionResource` 和 `ResourceGroupResource` 上提供 extension method：

```csharp
// 在 SubscriptionResource 上
subscription.GetDurableTaskSchedulers();           // 列出 subscription 內全部
subscription.GetDurableTaskSchedulersAsync();      // 非同步 enumerable

// 在 ResourceGroupResource 上
resourceGroup.GetDurableTaskSchedulers();          // 取得集合
resourceGroup.GetDurableTaskSchedulerAsync(name);  // 依名稱取得

// 在 ArmClient 上
armClient.GetDurableTaskSchedulerResource(id);     // 依 resource ID 取得
armClient.GetDurableTaskHubResource(id);           // 依 ID 取得 task hub
```

## 最佳實務

1. **需要等操作完成才能繼續時，用 `WaitUntil.Completed`**
2. **想自己輪詢或平行執行操作時，用 `WaitUntil.Started`**
3. **使用 `DefaultAzureCredential`**：絕對不要寫死 key
4. **處理 `RequestFailedException`**，因應 ARM API 的錯誤
5. **使用 `CreateOrUpdateAsync`** 做冪等操作
6. **先刪 task hub，再刪 scheduler**：還有 task hub 的 scheduler 無法刪除
7. **正式環境使用 IP 允許清單**，加強網路安全

## 錯誤處理

```csharp
using Azure;

try
{
    var operation = await schedulerCollection.CreateOrUpdateAsync(
        WaitUntil.Completed, schedulerName, schedulerData);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("Scheduler already exists");
}
catch (RequestFailedException ex) when (ex.Status == 404)
{
    Console.WriteLine("Resource group not found");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"ARM Error: {ex.Status} - {ex.ErrorCode}: {ex.Message}");
}
```

## 完整範例

```csharp
using Azure;
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.DurableTask;
using Azure.ResourceManager.DurableTask.Models;
using Azure.ResourceManager.Resources;

// 設定
var credential = new DefaultAzureCredential();
var armClient = new ArmClient(credential);

var subscriptionId = Environment.GetEnvironmentVariable("AZURE_SUBSCRIPTION_ID")!;
var resourceGroupName = Environment.GetEnvironmentVariable("AZURE_RESOURCE_GROUP")!;

var subscription = armClient.GetSubscriptionResource(
    new ResourceIdentifier($"/subscriptions/{subscriptionId}"));
var resourceGroup = await subscription.GetResourceGroupAsync(resourceGroupName);

// 建立 scheduler
var schedulerData = new DurableTaskSchedulerData(AzureLocation.EastUS)
{
    Properties = new DurableTaskSchedulerProperties
    {
        Sku = new DurableTaskSchedulerSku(DurableTaskSchedulerSkuName.Dedicated)
        {
            Capacity = 1
        }
    }
};

var schedulerCollection = resourceGroup.Value.GetDurableTaskSchedulers();
var schedulerOp = await schedulerCollection.CreateOrUpdateAsync(
    WaitUntil.Completed, "my-scheduler", schedulerData);
var scheduler = schedulerOp.Value;

Console.WriteLine($"Scheduler endpoint: {scheduler.Data.Properties.Endpoint}");

// 建立 task hub
var taskHubData = new DurableTaskHubData();
var taskHubOp = await scheduler.GetDurableTaskHubs().CreateOrUpdateAsync(
    WaitUntil.Completed, "my-taskhub", taskHubData);
var taskHub = taskHubOp.Value;

Console.WriteLine($"Task Hub: {taskHub.Data.Name}");

// 清理
await taskHub.DeleteAsync(WaitUntil.Completed);
await scheduler.DeleteAsync(WaitUntil.Completed);
```

## 相關 SDK

| SDK | 用途 | 安裝 |
|-----|---------|---------|
| `Azure.ResourceManager.DurableTask` | 管理平面（本 SDK） | `dotnet add package Azure.ResourceManager.DurableTask` |
| `Microsoft.DurableTask.Client.AzureManaged` | Data plane（orchestration、activity） | `dotnet add package Microsoft.DurableTask.Client.AzureManaged` |
| `Microsoft.DurableTask.Worker.AzureManaged` | 執行 orchestration 的 worker | `dotnet add package Microsoft.DurableTask.Worker.AzureManaged` |
| `Azure.Identity` | 驗證 | `dotnet add package Azure.Identity` |
| `Azure.ResourceManager` | 基礎 ARM SDK | `dotnet add package Azure.ResourceManager` |

## 來源參考

- [GitHub: Azure.ResourceManager.DurableTask](https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/durabletask/Azure.ResourceManager.DurableTask)
- [NuGet: Azure.ResourceManager.DurableTask](https://www.nuget.org/packages/Azure.ResourceManager.DurableTask)
