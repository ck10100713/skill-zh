---
name: azure-resource-manager-sql-dotnet
description: |
  .NET 版 Azure SQL 的 Azure Resource Manager SDK。用於 MANAGEMENT PLANE（管理平面）操作：透過 Azure Resource Manager 建立／管理 SQL server、資料庫、elastic pool、防火牆規則與 failover group。NOT 用於 data plane 操作（執行查詢），那種請用 Microsoft.Data.SqlClient。Triggers: "SQL server", "create SQL database", "manage SQL resources", "ARM SQL", "SqlServerResource", "provision Azure SQL", "elastic pool", "firewall rule".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.ResourceManager.Sql
---

# Azure.ResourceManager.Sql (.NET)

管理平面 SDK，透過 Azure Resource Manager 佈建與管理 Azure SQL 資源。

> **⚠️ 管理平面 vs Data Plane**
> - **這個 SDK（Azure.ResourceManager.Sql）**：建立 server、資料庫、elastic pool、設定防火牆規則、管理 failover group
> - **Data Plane SDK（Microsoft.Data.SqlClient）**：執行查詢、stored procedure、管理連線

## 安裝

```bash
dotnet add package Azure.ResourceManager.Sql
dotnet add package Azure.Identity
```

**目前版本**：Stable v1.3.0、Preview v1.4.0-beta.3

## 環境變數

```bash
AZURE_SUBSCRIPTION_ID=<your-subscription-id>  # 必填：Azure subscription ID
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境使用 DefaultAzureCredential 時才需要
AZURE_TENANT_ID=<tenant-id>  # 用於 service principal 驗證（選填）
AZURE_CLIENT_ID=<client-id>  # 用於 service principal 驗證（選填）
AZURE_CLIENT_SECRET=<client-secret>  # 用於 service principal 驗證（選填）
```

## 驗證

```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.Sql;

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
        └── SqlServerResource
            ├── SqlDatabaseResource
            ├── ElasticPoolResource
            │   └── ElasticPoolDatabaseResource
            ├── SqlFirewallRuleResource
            ├── FailoverGroupResource
            ├── ServerBlobAuditingPolicyResource
            ├── EncryptionProtectorResource
            └── VirtualNetworkRuleResource
```

## 核心流程

### 1. 建立 SQL Server

```csharp
using Azure.ResourceManager.Sql;
using Azure.ResourceManager.Sql.Models;

// 取得 resource group
var resourceGroup = await subscription
    .GetResourceGroupAsync("my-resource-group");

// 定義 server
var serverData = new SqlServerData(AzureLocation.EastUS)
{
    AdministratorLogin = "sqladmin",
    AdministratorLoginPassword = "YourSecurePassword123!",
    Version = "12.0",
    MinimalTlsVersion = SqlMinimalTlsVersion.Tls1_2,
    PublicNetworkAccess = ServerNetworkAccessFlag.Enabled
};

// 建立 server（長時間執行的操作）
var serverCollection = resourceGroup.Value.GetSqlServers();
var operation = await serverCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-sql-server",
    serverData);

SqlServerResource server = operation.Value;
```

### 2. 建立 SQL 資料庫

```csharp
var databaseData = new SqlDatabaseData(AzureLocation.EastUS)
{
    Sku = new SqlSku("S0") { Tier = "Standard" },
    MaxSizeBytes = 2L * 1024 * 1024 * 1024, // 2 GB
    Collation = "SQL_Latin1_General_CP1_CI_AS",
    RequestedBackupStorageRedundancy = SqlBackupStorageRedundancy.Local
};

var databaseCollection = server.GetSqlDatabases();
var dbOperation = await databaseCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-database",
    databaseData);

SqlDatabaseResource database = dbOperation.Value;
```

### 3. 建立 Elastic Pool

```csharp
var poolData = new ElasticPoolData(AzureLocation.EastUS)
{
    Sku = new SqlSku("StandardPool")
    {
        Tier = "Standard",
        Capacity = 100 // 100 eDTU
    },
    PerDatabaseSettings = new ElasticPoolPerDatabaseSettings
    {
        MinCapacity = 0,
        MaxCapacity = 100
    }
};

var poolCollection = server.GetElasticPools();
var poolOperation = await poolCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-elastic-pool",
    poolData);

ElasticPoolResource pool = poolOperation.Value;
```

### 4. 把資料庫加入 Elastic Pool

```csharp
var databaseData = new SqlDatabaseData(AzureLocation.EastUS)
{
    ElasticPoolId = pool.Id
};

await databaseCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "pooled-database",
    databaseData);
```

### 5. 設定防火牆規則

```csharp
// 允許 Azure 服務
var azureServicesRule = new SqlFirewallRuleData
{
    StartIPAddress = "0.0.0.0",
    EndIPAddress = "0.0.0.0"
};

var firewallCollection = server.GetSqlFirewallRules();
await firewallCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "AllowAzureServices",
    azureServicesRule);

// 允許特定的 IP 範圍
var clientRule = new SqlFirewallRuleData
{
    StartIPAddress = "203.0.113.0",
    EndIPAddress = "203.0.113.255"
};

await firewallCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "AllowClientIPs",
    clientRule);
```

### 6. 列出資源

```csharp
// 列出 subscription 內所有 server
await foreach (var srv in subscription.GetSqlServersAsync())
{
    Console.WriteLine($"Server: {srv.Data.Name} in {srv.Data.Location}");
}

// 列出 server 內的資料庫
await foreach (var db in server.GetSqlDatabases())
{
    Console.WriteLine($"Database: {db.Data.Name}, SKU: {db.Data.Sku?.Name}");
}

// 列出 elastic pool
await foreach (var ep in server.GetElasticPools())
{
    Console.WriteLine($"Pool: {ep.Data.Name}, DTU: {ep.Data.Sku?.Capacity}");
}
```

### 7. 取得 Connection String

```csharp
// 組出 connection string（server 的 FQDN 是可預期的）
var serverFqdn = $"{server.Data.Name}.database.windows.net";
var connectionString = $"Server=tcp:{serverFqdn},1433;" +
    $"Initial Catalog={database.Data.Name};" +
    "Persist Security Info=False;" +
    $"User ID={server.Data.AdministratorLogin};" +
    "Password=<your-password>;" +
    "MultipleActiveResultSets=False;" +
    "Encrypt=True;" +
    "TrustServerCertificate=False;" +
    "Connection Timeout=30;";
```

## 主要型別參考

| 型別 | 用途 |
|------|---------|
| `ArmClient` | 所有 ARM 操作的進入點 |
| `SqlServerResource` | 代表一個 Azure SQL server |
| `SqlServerCollection` | server CRUD 的集合 |
| `SqlDatabaseResource` | 代表一個 SQL 資料庫 |
| `SqlDatabaseCollection` | 資料庫 CRUD 的集合 |
| `ElasticPoolResource` | 代表一個 elastic pool |
| `ElasticPoolCollection` | elastic pool CRUD 的集合 |
| `SqlFirewallRuleResource` | 代表一條防火牆規則 |
| `SqlFirewallRuleCollection` | 防火牆規則 CRUD 的集合 |
| `SqlServerData` | server 建立／更新的 payload |
| `SqlDatabaseData` | 資料庫建立／更新的 payload |
| `ElasticPoolData` | elastic pool 建立／更新的 payload |
| `SqlFirewallRuleData` | 防火牆規則建立／更新的 payload |
| `SqlSku` | SKU 設定（tier、capacity） |

## 常見 SKU

### 資料庫 SKU

| SKU 名稱 | 層級 | 說明 |
|----------|------|-------------|
| `Basic` | Basic | 5 DTU，最大 2 GB |
| `S0`-`S12` | Standard | 10-3000 DTU |
| `P1`-`P15` | Premium | 125-4000 DTU |
| `GP_Gen5_2` | GeneralPurpose | 以 vCore 為基礎，2 個 vCore |
| `BC_Gen5_2` | BusinessCritical | 以 vCore 為基礎，2 個 vCore |
| `HS_Gen5_2` | Hyperscale | 以 vCore 為基礎，2 個 vCore |

### Elastic Pool SKU

| SKU 名稱 | 層級 | 說明 |
|----------|------|-------------|
| `BasicPool` | Basic | 50-1600 eDTU |
| `StandardPool` | Standard | 50-3000 eDTU |
| `PremiumPool` | Premium | 125-4000 eDTU |
| `GP_Gen5_2` | GeneralPurpose | 以 vCore 為基礎 |
| `BC_Gen5_2` | BusinessCritical | 以 vCore 為基礎 |

## 最佳實務

1. **需要等操作完成才能繼續時，用 `WaitUntil.Completed`**
2. **想自己輪詢或平行執行操作時，用 `WaitUntil.Started`**
3. **一律使用 `DefaultAzureCredential`**：正式環境絕對不要寫死密碼
4. **處理 `RequestFailedException`**，因應 ARM API 的錯誤
5. **使用 `CreateOrUpdateAsync`** 做冪等操作
6. **透過 `Get*` 方法走訪階層**（例如 `server.GetSqlDatabases()`）
7. **管理多個資料庫時用 elastic pool**，節省成本
8. **先設定防火牆規則**，再嘗試連線

## 錯誤處理

```csharp
using Azure;

try
{
    var operation = await serverCollection.CreateOrUpdateAsync(
        WaitUntil.Completed, serverName, serverData);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("Server already exists");
}
catch (RequestFailedException ex) when (ex.Status == 400)
{
    Console.WriteLine($"Invalid request: {ex.Message}");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"ARM Error: {ex.Status} - {ex.ErrorCode}: {ex.Message}");
}
```

## 參考檔案

| 檔案 | 何時閱讀 |
|------|--------------|
| [references/server-management.md](references/server-management.md) | Server CRUD、管理員憑證、Azure AD 驗證、網路 |
| [references/database-operations.md](references/database-operations.md) | 資料庫 CRUD、調整規格、備份、還原、複製 |
| [references/elastic-pools.md](references/elastic-pools.md) | Pool 管理、新增／移除資料庫、調整規格 |

## 相關 SDK

| SDK | 用途 | 安裝 |
|-----|---------|---------|
| `Microsoft.Data.SqlClient` | Data plane（執行查詢、stored procedure） | `dotnet add package Microsoft.Data.SqlClient` |
| `Azure.ResourceManager.Sql` | 管理平面（本 SDK） | `dotnet add package Azure.ResourceManager.Sql` |
| `Microsoft.EntityFrameworkCore.SqlServer` | SQL Server 的 ORM | `dotnet add package Microsoft.EntityFrameworkCore.SqlServer` |
