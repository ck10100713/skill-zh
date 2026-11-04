---
name: azure-resource-manager-postgresql-dotnet
description: |
  .NET 版 Azure PostgreSQL Flexible Server SDK。管理 PostgreSQL Flexible Server 部署的資料庫。用於建立 server、資料庫、防火牆規則、設定、備份與高可用性。Triggers: "PostgreSQL", "PostgreSqlFlexibleServer", "PostgreSQL Flexible Server", "Azure Database for PostgreSQL", "PostgreSQL database management", "PostgreSQL firewall", "PostgreSQL backup", "Postgres".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.ResourceManager.PostgreSql
---

# Azure.ResourceManager.PostgreSql (.NET)

用來管理 PostgreSQL Flexible Server 部署的 Azure Resource Manager SDK。

## 安裝

```bash
dotnet add package Azure.ResourceManager.PostgreSql
dotnet add package Azure.Identity
```

**目前版本**：v1.2.0 (GA)  
**API 版本**：2023-12-01-preview

> **Note**：這個 skill 專注在 PostgreSQL Flexible Server。Single Server 已棄用，預定退役。

## 環境變數

```bash
AZURE_SUBSCRIPTION_ID=<your-subscription-id>  # 必填：Azure subscription ID
AZURE_RESOURCE_GROUP=<your-resource-group>  # 必填：resource group 名稱
AZURE_POSTGRESQL_SERVER_NAME=<your-postgresql-server>  # 必填：PostgreSQL Flexible Server 名稱
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境使用 DefaultAzureCredential 時才需要
```

## 驗證

```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.PostgreSql;
using Azure.ResourceManager.PostgreSql.FlexibleServers;

// 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
var credential = new DefaultAzureCredential(
    DefaultAzureCredential.DefaultEnvironmentVariableName
);
// 或在正式環境直接使用特定的 credential：
// See https://learn.microsoft.com/dotnet/api/overview/azure/identity-readme?view=azure-dotnet#credential-classes
// var credential = new ManagedIdentityCredential();
ArmClient client = new ArmClient(credential);
```

## 資源階層

```
Subscription
└── ResourceGroup
    └── PostgreSqlFlexibleServer              # PostgreSQL Flexible Server instance
        ├── PostgreSqlFlexibleServerDatabase  # server 內的資料庫
        ├── PostgreSqlFlexibleServerFirewallRule # IP 防火牆規則
        ├── PostgreSqlFlexibleServerConfiguration # Server 參數
        ├── PostgreSqlFlexibleServerBackup    # 備份資訊
        ├── PostgreSqlFlexibleServerActiveDirectoryAdministrator # Entra ID 管理員
        └── PostgreSqlFlexibleServerVirtualEndpoint # 唯讀 replica endpoint
```

## 核心流程

### 1. 建立 PostgreSQL Flexible Server

```csharp
using Azure.ResourceManager.PostgreSql.FlexibleServers;
using Azure.ResourceManager.PostgreSql.FlexibleServers.Models;

ResourceGroupResource resourceGroup = await client
    .GetDefaultSubscriptionAsync()
    .Result
    .GetResourceGroupAsync("my-resource-group");

PostgreSqlFlexibleServerCollection servers = resourceGroup.GetPostgreSqlFlexibleServers();

PostgreSqlFlexibleServerData data = new PostgreSqlFlexibleServerData(AzureLocation.EastUS)
{
    Sku = new PostgreSqlFlexibleServerSku("Standard_D2ds_v4", PostgreSqlFlexibleServerSkuTier.GeneralPurpose),
    AdministratorLogin = "pgadmin",
    AdministratorLoginPassword = "YourSecurePassword123!",
    Version = PostgreSqlFlexibleServerVersion.Ver16,
    Storage = new PostgreSqlFlexibleServerStorage
    {
        StorageSizeInGB = 128,
        AutoGrow = StorageAutoGrow.Enabled,
        Tier = PostgreSqlStorageTierName.P30
    },
    Backup = new PostgreSqlFlexibleServerBackupProperties
    {
        BackupRetentionDays = 7,
        GeoRedundantBackup = PostgreSqlFlexibleServerGeoRedundantBackupEnum.Disabled
    },
    HighAvailability = new PostgreSqlFlexibleServerHighAvailability
    {
        Mode = PostgreSqlFlexibleServerHighAvailabilityMode.ZoneRedundant,
        StandbyAvailabilityZone = "2"
    },
    AvailabilityZone = "1",
    AuthConfig = new PostgreSqlFlexibleServerAuthConfig
    {
        ActiveDirectoryAuth = PostgreSqlFlexibleServerActiveDirectoryAuthEnum.Enabled,
        PasswordAuth = PostgreSqlFlexibleServerPasswordAuthEnum.Enabled
    }
};

ArmOperation<PostgreSqlFlexibleServerResource> operation = await servers
    .CreateOrUpdateAsync(WaitUntil.Completed, "my-postgresql-server", data);

PostgreSqlFlexibleServerResource server = operation.Value;
Console.WriteLine($"Server created: {server.Data.FullyQualifiedDomainName}");
```

### 2. 建立資料庫

```csharp
PostgreSqlFlexibleServerResource server = await resourceGroup
    .GetPostgreSqlFlexibleServerAsync("my-postgresql-server");

PostgreSqlFlexibleServerDatabaseCollection databases = server.GetPostgreSqlFlexibleServerDatabases();

PostgreSqlFlexibleServerDatabaseData dbData = new PostgreSqlFlexibleServerDatabaseData
{
    Charset = "UTF8",
    Collation = "en_US.utf8"
};

ArmOperation<PostgreSqlFlexibleServerDatabaseResource> operation = await databases
    .CreateOrUpdateAsync(WaitUntil.Completed, "myappdb", dbData);

PostgreSqlFlexibleServerDatabaseResource database = operation.Value;
Console.WriteLine($"Database created: {database.Data.Name}");
```

### 3. 設定防火牆規則

```csharp
PostgreSqlFlexibleServerFirewallRuleCollection firewallRules = server.GetPostgreSqlFlexibleServerFirewallRules();

// 允許特定的 IP 範圍
PostgreSqlFlexibleServerFirewallRuleData ruleData = new PostgreSqlFlexibleServerFirewallRuleData
{
    StartIPAddress = System.Net.IPAddress.Parse("10.0.0.1"),
    EndIPAddress = System.Net.IPAddress.Parse("10.0.0.255")
};

ArmOperation<PostgreSqlFlexibleServerFirewallRuleResource> operation = await firewallRules
    .CreateOrUpdateAsync(WaitUntil.Completed, "allow-internal", ruleData);

// 允許 Azure 服務
PostgreSqlFlexibleServerFirewallRuleData azureServicesRule = new PostgreSqlFlexibleServerFirewallRuleData
{
    StartIPAddress = System.Net.IPAddress.Parse("0.0.0.0"),
    EndIPAddress = System.Net.IPAddress.Parse("0.0.0.0")
};

await firewallRules.CreateOrUpdateAsync(WaitUntil.Completed, "AllowAllAzureServicesAndResourcesWithinAzureIps", azureServicesRule);
```

### 4. 更新 Server 設定

```csharp
PostgreSqlFlexibleServerConfigurationCollection configurations = server.GetPostgreSqlFlexibleServerConfigurations();

// 取得目前的設定
PostgreSqlFlexibleServerConfigurationResource config = await configurations
    .GetAsync("max_connections");

// 更新設定
PostgreSqlFlexibleServerConfigurationData configData = new PostgreSqlFlexibleServerConfigurationData
{
    Value = "500",
    Source = "user-override"
};

ArmOperation<PostgreSqlFlexibleServerConfigurationResource> operation = await configurations
    .CreateOrUpdateAsync(WaitUntil.Completed, "max_connections", configData);

// 常見要調整的 PostgreSQL 設定
string[] commonParams = { 
    "max_connections", 
    "shared_buffers", 
    "work_mem", 
    "maintenance_work_mem",
    "effective_cache_size",
    "log_min_duration_statement"
};
```

### 5. 設定 Entra ID 管理員

```csharp
PostgreSqlFlexibleServerActiveDirectoryAdministratorCollection admins = 
    server.GetPostgreSqlFlexibleServerActiveDirectoryAdministrators();

PostgreSqlFlexibleServerActiveDirectoryAdministratorData adminData = 
    new PostgreSqlFlexibleServerActiveDirectoryAdministratorData
{
    PrincipalType = PostgreSqlFlexibleServerPrincipalType.User,
    PrincipalName = "aad-admin@contoso.com",
    TenantId = Guid.Parse("<tenant-id>")
};

ArmOperation<PostgreSqlFlexibleServerActiveDirectoryAdministratorResource> operation = await admins
    .CreateOrUpdateAsync(WaitUntil.Completed, "<entra-object-id>", adminData);
```

### 6. 列出與管理 Server

```csharp
// 列出 resource group 內的 server
await foreach (PostgreSqlFlexibleServerResource server in resourceGroup.GetPostgreSqlFlexibleServers())
{
    Console.WriteLine($"Server: {server.Data.Name}");
    Console.WriteLine($"  FQDN: {server.Data.FullyQualifiedDomainName}");
    Console.WriteLine($"  Version: {server.Data.Version}");
    Console.WriteLine($"  State: {server.Data.State}");
    Console.WriteLine($"  SKU: {server.Data.Sku.Name} ({server.Data.Sku.Tier})");
    Console.WriteLine($"  HA: {server.Data.HighAvailability?.Mode}");
}

// 列出 server 內的資料庫
await foreach (PostgreSqlFlexibleServerDatabaseResource db in server.GetPostgreSqlFlexibleServerDatabases())
{
    Console.WriteLine($"Database: {db.Data.Name}");
}
```

### 7. 備份與時間點還原

```csharp
// 列出可用的備份
await foreach (PostgreSqlFlexibleServerBackupResource backup in server.GetPostgreSqlFlexibleServerBackups())
{
    Console.WriteLine($"Backup: {backup.Data.Name}");
    Console.WriteLine($"  Type: {backup.Data.BackupType}");
    Console.WriteLine($"  Completed: {backup.Data.CompletedOn}");
}

// 還原到某個時間點
PostgreSqlFlexibleServerData restoreData = new PostgreSqlFlexibleServerData(AzureLocation.EastUS)
{
    CreateMode = PostgreSqlFlexibleServerCreateMode.PointInTimeRestore,
    SourceServerResourceId = server.Id,
    PointInTimeUtc = DateTimeOffset.UtcNow.AddHours(-2)
};

ArmOperation<PostgreSqlFlexibleServerResource> operation = await servers
    .CreateOrUpdateAsync(WaitUntil.Completed, "my-postgresql-restored", restoreData);
```

### 8. 建立唯讀 Replica

```csharp
PostgreSqlFlexibleServerData replicaData = new PostgreSqlFlexibleServerData(AzureLocation.WestUS)
{
    CreateMode = PostgreSqlFlexibleServerCreateMode.Replica,
    SourceServerResourceId = server.Id,
    Sku = new PostgreSqlFlexibleServerSku("Standard_D2ds_v4", PostgreSqlFlexibleServerSkuTier.GeneralPurpose)
};

ArmOperation<PostgreSqlFlexibleServerResource> operation = await servers
    .CreateOrUpdateAsync(WaitUntil.Completed, "my-postgresql-replica", replicaData);
```

### 9. 停止與啟動 Server

```csharp
PostgreSqlFlexibleServerResource server = await resourceGroup
    .GetPostgreSqlFlexibleServerAsync("my-postgresql-server");

// 停止 server（不使用時可省成本）
await server.StopAsync(WaitUntil.Completed);

// 啟動 server
await server.StartAsync(WaitUntil.Completed);

// 重新啟動 server
await server.RestartAsync(WaitUntil.Completed, new PostgreSqlFlexibleServerRestartParameter
{
    RestartWithFailover = true,
    FailoverMode = PostgreSqlFlexibleServerFailoverMode.PlannedFailover
});
```

### 10. 更新 Server（調整規格）

```csharp
PostgreSqlFlexibleServerResource server = await resourceGroup
    .GetPostgreSqlFlexibleServerAsync("my-postgresql-server");

PostgreSqlFlexibleServerPatch patch = new PostgreSqlFlexibleServerPatch
{
    Sku = new PostgreSqlFlexibleServerSku("Standard_D4ds_v4", PostgreSqlFlexibleServerSkuTier.GeneralPurpose),
    Storage = new PostgreSqlFlexibleServerStorage
    {
        StorageSizeInGB = 256,
        Tier = PostgreSqlStorageTierName.P40
    }
};

ArmOperation<PostgreSqlFlexibleServerResource> operation = await server
    .UpdateAsync(WaitUntil.Completed, patch);
```

### 11. 刪除 Server

```csharp
PostgreSqlFlexibleServerResource server = await resourceGroup
    .GetPostgreSqlFlexibleServerAsync("my-postgresql-server");

await server.DeleteAsync(WaitUntil.Completed);
```

## 主要型別參考

| 型別 | 用途 |
|------|---------|
| `PostgreSqlFlexibleServerResource` | Flexible Server instance |
| `PostgreSqlFlexibleServerData` | Server 設定資料 |
| `PostgreSqlFlexibleServerCollection` | Server 集合 |
| `PostgreSqlFlexibleServerDatabaseResource` | server 內的資料庫 |
| `PostgreSqlFlexibleServerFirewallRuleResource` | IP 防火牆規則 |
| `PostgreSqlFlexibleServerConfigurationResource` | Server 參數 |
| `PostgreSqlFlexibleServerBackupResource` | 備份 metadata |
| `PostgreSqlFlexibleServerActiveDirectoryAdministratorResource` | Entra ID 管理員 |
| `PostgreSqlFlexibleServerSku` | SKU（運算層級 + 大小） |
| `PostgreSqlFlexibleServerStorage` | 儲存設定 |
| `PostgreSqlFlexibleServerHighAvailability` | HA 設定 |
| `PostgreSqlFlexibleServerBackupProperties` | 備份設定 |
| `PostgreSqlFlexibleServerAuthConfig` | 驗證設定 |

## SKU 層級

| 層級 | 使用情境 | SKU 範例 |
|------|----------|--------------|
| `Burstable` | 開發／測試、輕量工作負載 | Standard_B1ms, Standard_B2s |
| `GeneralPurpose` | 正式環境工作負載 | Standard_D2ds_v4, Standard_D4ds_v4 |
| `MemoryOptimized` | 高記憶體需求 | Standard_E2ds_v4, Standard_E4ds_v4 |

## PostgreSQL 版本

| 版本 | Enum 值 |
|---------|------------|
| PostgreSQL 11 | `Ver11` |
| PostgreSQL 12 | `Ver12` |
| PostgreSQL 13 | `Ver13` |
| PostgreSQL 14 | `Ver14` |
| PostgreSQL 15 | `Ver15` |
| PostgreSQL 16 | `Ver16` |

## 高可用性模式

| 模式 | 說明 |
|------|-------------|
| `Disabled` | 沒有 HA（單一 server） |
| `SameZone` | 同一個 availability zone 內的 HA |
| `ZoneRedundant` | 跨 availability zone 的 HA |

## 最佳實務

1. **使用 Flexible Server**：Single Server 已棄用
2. **啟用 zone-redundant HA**：用於正式環境工作負載
3. **使用 DefaultAzureCredential**：優先於 connection string
4. **設定 Entra ID 驗證**：比單用 SQL 驗證更安全
5. **兩種驗證方式都啟用**：Entra ID + 密碼，保留彈性
6. **設定適當的備份保留期**：依合規需求設 7-35 天
7. **使用 private endpoint**：確保網路存取安全
8. **調整 server 參數**：依工作負載特性調整
9. **使用唯讀 replica**：用於讀取密集的工作負載
10. **停用開發／測試用的 server**：不使用時省成本

## 錯誤處理

```csharp
using Azure;

try
{
    ArmOperation<PostgreSqlFlexibleServerResource> operation = await servers
        .CreateOrUpdateAsync(WaitUntil.Completed, "my-postgresql", data);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("Server already exists");
}
catch (RequestFailedException ex) when (ex.Status == 400)
{
    Console.WriteLine($"Invalid configuration: {ex.Message}");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Azure error: {ex.Status} - {ex.Message}");
}
```

## Connection String

建立 server 後，用以下方式連線：

```csharp
// Npgsql connection string
string connectionString = $"Host={server.Data.FullyQualifiedDomainName};" +
    "Database=myappdb;" +
    "Username=pgadmin;" +
    "Password=YourSecurePassword123!;" +
    "SSL Mode=Require;Trust Server Certificate=true;";

// 使用 Entra ID token（建議）
var credential = new DefaultAzureCredential();
var token = await credential.GetTokenAsync(
    new TokenRequestContext(new[] { "https://ossrdbms-aad.database.windows.net/.default" }));

string connectionString = $"Host={server.Data.FullyQualifiedDomainName};" +
    "Database=myappdb;" +
    $"Username=aad-admin@contoso.com;" +
    $"Password={token.Token};" +
    "SSL Mode=Require;";
```

## 相關 SDK

| SDK | 用途 | 安裝 |
|-----|---------|---------|
| `Azure.ResourceManager.PostgreSql` | PostgreSQL 管理（本 SDK） | `dotnet add package Azure.ResourceManager.PostgreSql` |
| `Azure.ResourceManager.MySql` | MySQL 管理 | `dotnet add package Azure.ResourceManager.MySql` |
| `Npgsql` | PostgreSQL 資料存取 | `dotnet add package Npgsql` |
| `Npgsql.EntityFrameworkCore.PostgreSQL` | EF Core provider | `dotnet add package Npgsql.EntityFrameworkCore.PostgreSQL` |

## 參考連結

| 資源 | URL |
|----------|-----|
| NuGet 套件 | https://www.nuget.org/packages/Azure.ResourceManager.PostgreSql |
| API 參考 | https://learn.microsoft.com/dotnet/api/azure.resourcemanager.postgresql |
| 產品文件 | https://learn.microsoft.com/azure/postgresql/flexible-server/ |
| GitHub 原始碼 | https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/postgresql/Azure.ResourceManager.PostgreSql |
