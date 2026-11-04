---
name: azure-resource-manager-cosmosdb-dotnet
description: |
  .NET 版 Cosmos DB 的 Azure Resource Manager SDK。用於 MANAGEMENT PLANE（管理平面）操作：透過 Azure Resource Manager 建立／管理 Cosmos DB 帳號、資料庫、container、throughput 設定與 RBAC。NOT 用於 data plane 操作（文件的 CRUD），那種請用 Microsoft.Azure.Cosmos。Triggers: "Cosmos DB account", "create Cosmos account", "manage Cosmos resources", "ARM Cosmos", "CosmosDBAccountResource", "provision Cosmos DB".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.ResourceManager.CosmosDB
---

# Azure.ResourceManager.CosmosDB (.NET)

管理平面 SDK，透過 Azure Resource Manager 佈建與管理 Azure Cosmos DB 資源。

> **⚠️ 管理平面 vs Data Plane**
> - **這個 SDK（Azure.ResourceManager.CosmosDB）**：建立帳號、資料庫、container、設定 throughput、管理 RBAC
> - **Data Plane SDK（Microsoft.Azure.Cosmos）**：文件的 CRUD 操作、查詢、執行 stored procedure

## 安裝

```bash
dotnet add package Azure.ResourceManager.CosmosDB
dotnet add package Azure.Identity
```

**目前版本**：Stable v1.4.0、Preview v1.4.0-beta.13

## 環境變數

```bash
AZURE_SUBSCRIPTION_ID=<your-subscription-id> # 必填：Azure subscription ID
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境使用 DefaultAzureCredential 時才需要
AZURE_TENANT_ID=<tenant-id> # 用於 service principal 驗證（選填）
AZURE_CLIENT_ID=<client-id> # 用於 service principal 驗證（選填）
AZURE_CLIENT_SECRET=<client-secret> # 用於 service principal 驗證（選填）
```

## 驗證

```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.CosmosDB;

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
        └── CosmosDBAccountResource
            ├── CosmosDBSqlDatabaseResource
            │   └── CosmosDBSqlContainerResource
            │       ├── CosmosDBSqlStoredProcedureResource
            │       ├── CosmosDBSqlTriggerResource
            │       └── CosmosDBSqlUserDefinedFunctionResource
            ├── CassandraKeyspaceResource
            ├── GremlinDatabaseResource
            ├── MongoDBDatabaseResource
            └── CosmosDBTableResource
```

## 核心流程

### 1. 建立 Cosmos DB 帳號

```csharp
using Azure.ResourceManager.CosmosDB;
using Azure.ResourceManager.CosmosDB.Models;

// 取得 resource group
var resourceGroup = await subscription
    .GetResourceGroupAsync("my-resource-group");

// 定義帳號
var accountData = new CosmosDBAccountCreateOrUpdateContent(
    location: AzureLocation.EastUS,
    locations: new[]
    {
        new CosmosDBAccountLocation
        {
            LocationName = AzureLocation.EastUS,
            FailoverPriority = 0,
            IsZoneRedundant = false
        }
    })
{
    Kind = CosmosDBAccountKind.GlobalDocumentDB,
    ConsistencyPolicy = new ConsistencyPolicy(DefaultConsistencyLevel.Session),
    EnableAutomaticFailover = true
};

// 建立帳號（長時間執行的操作）
var accountCollection = resourceGroup.Value.GetCosmosDBAccounts();
var operation = await accountCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-cosmos-account",
    accountData);

CosmosDBAccountResource account = operation.Value;
```

### 2. 建立 SQL 資料庫

```csharp
var databaseData = new CosmosDBSqlDatabaseCreateOrUpdateContent(
    new CosmosDBSqlDatabaseResourceInfo("my-database"));

var databaseCollection = account.GetCosmosDBSqlDatabases();
var dbOperation = await databaseCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-database",
    databaseData);

CosmosDBSqlDatabaseResource database = dbOperation.Value;
```

### 3. 建立 SQL Container

```csharp
var containerData = new CosmosDBSqlContainerCreateOrUpdateContent(
    new CosmosDBSqlContainerResourceInfo("my-container")
    {
        PartitionKey = new CosmosDBContainerPartitionKey
        {
            Paths = { "/partitionKey" },
            Kind = CosmosDBPartitionKind.Hash
        },
        IndexingPolicy = new CosmosDBIndexingPolicy
        {
            Automatic = true,
            IndexingMode = CosmosDBIndexingMode.Consistent
        },
        DefaultTtl = 86400 // 24 小時
    });

var containerCollection = database.GetCosmosDBSqlContainers();
var containerOperation = await containerCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-container",
    containerData);

CosmosDBSqlContainerResource container = containerOperation.Value;
```

### 4. 設定 Throughput

```csharp
// 手動 throughput
var throughputData = new ThroughputSettingsUpdateData(
    new ThroughputSettingsResourceInfo
    {
        Throughput = 400
    });

// Autoscale throughput
var autoscaleData = new ThroughputSettingsUpdateData(
    new ThroughputSettingsResourceInfo
    {
        AutoscaleSettings = new AutoscaleSettingsResourceInfo
        {
            MaxThroughput = 4000
        }
    });

// 套用到資料庫
await database.CreateOrUpdateCosmosDBSqlDatabaseThroughputAsync(
    WaitUntil.Completed,
    throughputData);
```

### 5. 取得連線資訊

```csharp
// 取得 key
var keys = await account.GetKeysAsync();
Console.WriteLine($"Primary Key: {keys.Value.PrimaryMasterKey}");

// 取得連線字串
var connectionStrings = await account.GetConnectionStringsAsync();
foreach (var cs in connectionStrings.Value.ConnectionStrings)
{
    Console.WriteLine($"{cs.Description}: {cs.ConnectionString}");
}
```

## 主要型別參考

| 型別 | 用途 |
|------|---------|
| `ArmClient` | 所有 ARM 操作的進入點 |
| `CosmosDBAccountResource` | 代表一個 Cosmos DB 帳號 |
| `CosmosDBAccountCollection` | 帳號 CRUD 的集合 |
| `CosmosDBSqlDatabaseResource` | SQL API 資料庫 |
| `CosmosDBSqlContainerResource` | SQL API container |
| `CosmosDBAccountCreateOrUpdateContent` | 建立帳號的 payload |
| `CosmosDBSqlDatabaseCreateOrUpdateContent` | 建立資料庫的 payload |
| `CosmosDBSqlContainerCreateOrUpdateContent` | 建立 container 的 payload |
| `ThroughputSettingsUpdateData` | Throughput 設定 |

## 最佳實務

1. **需要等操作完成才能繼續時，用 `WaitUntil.Completed`**
2. **想自己輪詢或平行執行操作時，用 `WaitUntil.Started`**
3. **使用 `DefaultAzureCredential`**：絕對不要寫死 key
4. **處理 `RequestFailedException`**，因應 ARM API 的錯誤
5. **使用 `CreateOrUpdateAsync`** 做冪等操作
6. **透過 `Get*` 方法走訪階層**（例如 `account.GetCosmosDBSqlDatabases()`）

## 錯誤處理

```csharp
using Azure;

try
{
    var operation = await accountCollection.CreateOrUpdateAsync(
        WaitUntil.Completed, accountName, accountData);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("Account already exists");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"ARM Error: {ex.Status} - {ex.ErrorCode}: {ex.Message}");
}
```

## 參考檔案

| 檔案 | 何時閱讀 |
|------|--------------|
| [references/account-management.md](references/account-management.md) | 帳號 CRUD、failover、key、連線字串、網路 |
| [references/sql-resources.md](references/sql-resources.md) | SQL 資料庫、container、stored procedure、trigger、UDF |
| [references/throughput.md](references/throughput.md) | 手動／autoscale throughput、模式間的遷移 |

## 相關 SDK

| SDK | 用途 | 安裝 |
|-----|---------|---------|
| `Microsoft.Azure.Cosmos` | Data plane（文件 CRUD、查詢） | `dotnet add package Microsoft.Azure.Cosmos` |
| `Azure.ResourceManager.CosmosDB` | 管理平面（本 SDK） | `dotnet add package Azure.ResourceManager.CosmosDB` |
