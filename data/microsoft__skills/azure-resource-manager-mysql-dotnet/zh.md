---
name: azure-resource-manager-mysql-dotnet
description: |
  .NET 版 Azure MySQL Flexible Server SDK。管理 MySQL Flexible Server 部署的資料庫。用於建立 server、資料庫、防火牆規則、設定、備份與高可用性。Triggers: "MySQL", "MySqlFlexibleServer", "MySQL Flexible Server", "Azure Database for MySQL", "MySQL database management", "MySQL firewall", "MySQL backup".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.ResourceManager.MySql
---

# Azure.ResourceManager.MySql (.NET)

用來管理 MySQL Flexible Server 部署的 Azure Resource Manager SDK。

## 安裝

```bash
dotnet add package Azure.ResourceManager.MySql
dotnet add package Azure.Identity
```

**目前版本**：v1.2.0 (GA)  
**API 版本**：2023-12-30

> **Note**：這個 skill 專注在 MySQL Flexible Server。Single Server 已棄用，預定退役。

## 環境變數

```bash
AZURE_SUBSCRIPTION_ID=<your-subscription-id>  # 必填：Azure subscription ID
AZURE_RESOURCE_GROUP=<your-resource-group>  # 必填：resource group 名稱
AZURE_MYSQL_SERVER_NAME=<your-mysql-server>  # 必填：MySQL Flexible Server 名稱
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境使用 DefaultAzureCredential 時才需要
```

## 驗證

```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.MySql;
using Azure.ResourceManager.MySql.FlexibleServers;

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
    └── MySqlFlexibleServer                 # MySQL Flexible Server instance
        ├── MySqlFlexibleServerDatabase     # server 內的資料庫
        ├── MySqlFlexibleServerFirewallRule # IP 防火牆規則
        ├── MySqlFlexibleServerConfiguration # Server 參數
        ├── MySqlFlexibleServerBackup       # 備份資訊
        ├── MySqlFlexibleServerMaintenanceWindow # 維護排程
        └── MySqlFlexibleServerAadAdministrator # Entra ID 管理員
```

## 核心流程

### 1. 建立 MySQL Flexible Server

```csharp
using Azure.ResourceManager.MySql.FlexibleServers;
using Azure.ResourceManager.MySql.FlexibleServers.Models;

ResourceGroupResource resourceGroup = await client
    .GetDefaultSubscriptionAsync()
    .Result
    .GetResourceGroupAsync("my-resource-group");

MySqlFlexibleServerCollection servers = resourceGroup.GetMySqlFlexibleServers();

MySqlFlexibleServerData data = new MySqlFlexibleServerData(AzureLocation.EastUS)
{
    Sku = new MySqlFlexibleServerSku("Standard_D2ds_v4", MySqlFlexibleServerSkuTier.GeneralPurpose),
    AdministratorLogin = "mysqladmin",
    AdministratorLoginPassword = "YourSecurePassword123!",
    Version = MySqlFlexibleServerVersion.Ver8_0_21,
    Storage = new MySqlFlexibleServerStorage
    {
        StorageSizeInGB = 128,
        AutoGrow = MySqlFlexibleServerEnableStatusEnum.Enabled,
        Iops = 3000
    },
    Backup = new MySqlFlexibleServerBackupProperties
    {
        BackupRetentionDays = 7,
        GeoRedundantBackup = MySqlFlexibleServerEnableStatusEnum.Disabled
    },
    HighAvailability = new MySqlFlexibleServerHighAvailability
    {
        Mode = MySqlFlexibleServerHighAvailabilityMode.ZoneRedundant,
        StandbyAvailabilityZone = "2"
    },
    AvailabilityZone = "1"
};

ArmOperation<MySqlFlexibleServerResource> operation = await servers
    .CreateOrUpdateAsync(WaitUntil.Completed, "my-mysql-server", data);

MySqlFlexibleServerResource server = operation.Value;
Console.WriteLine($"Server created: {server.Data.FullyQualifiedDomainName}");
```

### 2. 建立資料庫

```csharp
MySqlFlexibleServerResource server = await resourceGroup
    .GetMySqlFlexibleServerAsync("my-mysql-server");

MySqlFlexibleServerDatabaseCollection databases = server.GetMySqlFlexibleServerDatabases();

MySqlFlexibleServerDatabaseData dbData = new MySqlFlexibleServerDatabaseData
{
    Charset = "utf8mb4",
    Collation = "utf8mb4_unicode_ci"
};

ArmOperation<MySqlFlexibleServerDatabaseResource> operation = await databases
    .CreateOrUpdateAsync(WaitUntil.Completed, "myappdb", dbData);

MySqlFlexibleServerDatabaseResource database = operation.Value;
Console.WriteLine($"Database created: {database.Data.Name}");
```

### 3. 設定防火牆規則

```csharp
MySqlFlexibleServerFirewallRuleCollection firewallRules = server.GetMySqlFlexibleServerFirewallRules();

// 允許特定的 IP 範圍
MySqlFlexibleServerFirewallRuleData ruleData = new MySqlFlexibleServerFirewallRuleData
{
    StartIPAddress = System.Net.IPAddress.Parse("10.0.0.1"),
    EndIPAddress = System.Net.IPAddress.Parse("10.0.0.255")
};

ArmOperation<MySqlFlexibleServerFirewallRuleResource> operation = await firewallRules
    .CreateOrUpdateAsync(WaitUntil.Completed, "allow-internal", ruleData);

// 允許 Azure 服務
MySqlFlexibleServerFirewallRuleData azureServicesRule = new MySqlFlexibleServerFirewallRuleData
{
    StartIPAddress = System.Net.IPAddress.Parse("0.0.0.0"),
    EndIPAddress = System.Net.IPAddress.Parse("0.0.0.0")
};

await firewallRules.CreateOrUpdateAsync(WaitUntil.Completed, "AllowAllAzureServicesAndResourcesWithinAzureIps", azureServicesRule);
```

### 4. 更新 Server 設定

```csharp
MySqlFlexibleServerConfigurationCollection configurations = server.GetMySqlFlexibleServerConfigurations();

// 取得目前的設定
MySqlFlexibleServerConfigurationResource config = await configurations
    .GetAsync("max_connections");

// 更新設定
MySqlFlexibleServerConfigurationData configData = new MySqlFlexibleServerConfigurationData
{
    Value = "500",
    Source = MySqlFlexibleServerConfigurationSource.UserOverride
};

ArmOperation<MySqlFlexibleServerConfigurationResource> operation = await configurations
    .CreateOrUpdateAsync(WaitUntil.Completed, "max_connections", configData);

// 常見要調整的設定
string[] commonParams = { "max_connections", "innodb_buffer_pool_size", "slow_query_log", "long_query_time" };
```

### 5. 設定 Entra ID 管理員

```csharp
MySqlFlexibleServerAadAdministratorCollection admins = server.GetMySqlFlexibleServerAadAdministrators();

MySqlFlexibleServerAadAdministratorData adminData = new MySqlFlexibleServerAadAdministratorData
{
    AdministratorType = MySqlFlexibleServerAdministratorType.ActiveDirectory,
    Login = "aad-admin@contoso.com",
    Sid = Guid.Parse("<entra-object-id>"),
    TenantId = Guid.Parse("<tenant-id>"),
    IdentityResourceId = new ResourceIdentifier("/subscriptions/.../userAssignedIdentities/mysql-identity")
};

ArmOperation<MySqlFlexibleServerAadAdministratorResource> operation = await admins
    .CreateOrUpdateAsync(WaitUntil.Completed, "ActiveDirectory", adminData);
```

### 6. 列出與管理 Server

```csharp
// 列出 resource group 內的 server
await foreach (MySqlFlexibleServerResource server in resourceGroup.GetMySqlFlexibleServers())
{
    Console.WriteLine($"Server: {server.Data.Name}");
    Console.WriteLine($"  FQDN: {server.Data.FullyQualifiedDomainName}");
    Console.WriteLine($"  Version: {server.Data.Version}");
    Console.WriteLine($"  State: {server.Data.State}");
    Console.WriteLine($"  SKU: {server.Data.Sku.Name} ({server.Data.Sku.Tier})");
}

// 列出 server 內的資料庫
await foreach (MySqlFlexibleServerDatabaseResource db in server.GetMySqlFlexibleServerDatabases())
{
    Console.WriteLine($"Database: {db.Data.Name}");
}
```

### 7. 備份與還原

```csharp
// 列出可用的備份
await foreach (MySqlFlexibleServerBackupResource backup in server.GetMySqlFlexibleServerBackups())
{
    Console.WriteLine($"Backup: {backup.Data.Name}");
    Console.WriteLine($"  Type: {backup.Data.BackupType}");
    Console.WriteLine($"  Completed: {backup.Data.CompletedOn}");
}

// 還原到某個時間點
MySqlFlexibleServerData restoreData = new MySqlFlexibleServerData(AzureLocation.EastUS)
{
    CreateMode = MySqlFlexibleServerCreateMode.PointInTimeRestore,
    SourceServerResourceId = server.Id,
    RestorePointInTime = DateTimeOffset.UtcNow.AddHours(-2)
};

ArmOperation<MySqlFlexibleServerResource> operation = await servers
    .CreateOrUpdateAsync(WaitUntil.Completed, "my-mysql-restored", restoreData);
```

### 8. 停止與啟動 Server

```csharp
MySqlFlexibleServerResource server = await resourceGroup
    .GetMySqlFlexibleServerAsync("my-mysql-server");

// 停止 server（不使用時可省成本）
await server.StopAsync(WaitUntil.Completed);

// 啟動 server
await server.StartAsync(WaitUntil.Completed);

// 重新啟動 server
await server.RestartAsync(WaitUntil.Completed, new MySqlFlexibleServerRestartParameter
{
    RestartWithFailover = MySqlFlexibleServerEnableStatusEnum.Enabled,
    MaxFailoverSeconds = 60
});
```

### 9. 更新 Server（調整規格）

```csharp
MySqlFlexibleServerResource server = await resourceGroup
    .GetMySqlFlexibleServerAsync("my-mysql-server");

MySqlFlexibleServerPatch patch = new MySqlFlexibleServerPatch
{
    Sku = new MySqlFlexibleServerSku("Standard_D4ds_v4", MySqlFlexibleServerSkuTier.GeneralPurpose),
    Storage = new MySqlFlexibleServerStorage
    {
        StorageSizeInGB = 256,
        Iops = 6000
    }
};

ArmOperation<MySqlFlexibleServerResource> operation = await server
    .UpdateAsync(WaitUntil.Completed, patch);
```

### 10. 刪除 Server

```csharp
MySqlFlexibleServerResource server = await resourceGroup
    .GetMySqlFlexibleServerAsync("my-mysql-server");

await server.DeleteAsync(WaitUntil.Completed);
```

## 主要型別參考

| 型別 | 用途 |
|------|---------|
| `MySqlFlexibleServerResource` | Flexible Server instance |
| `MySqlFlexibleServerData` | Server 設定資料 |
| `MySqlFlexibleServerCollection` | Server 集合 |
| `MySqlFlexibleServerDatabaseResource` | server 內的資料庫 |
| `MySqlFlexibleServerFirewallRuleResource` | IP 防火牆規則 |
| `MySqlFlexibleServerConfigurationResource` | Server 參數 |
| `MySqlFlexibleServerBackupResource` | 備份 metadata |
| `MySqlFlexibleServerAadAdministratorResource` | Entra ID 管理員 |
| `MySqlFlexibleServerSku` | SKU（運算層級 + 大小） |
| `MySqlFlexibleServerStorage` | 儲存設定 |
| `MySqlFlexibleServerHighAvailability` | HA 設定 |
| `MySqlFlexibleServerBackupProperties` | 備份設定 |

## SKU 層級

| 層級 | 使用情境 | SKU 範例 |
|------|----------|--------------|
| `Burstable` | 開發／測試、輕量工作負載 | Standard_B1ms, Standard_B2s |
| `GeneralPurpose` | 正式環境工作負載 | Standard_D2ds_v4, Standard_D4ds_v4 |
| `MemoryOptimized` | 高記憶體需求 | Standard_E2ds_v4, Standard_E4ds_v4 |

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
4. **設定 Entra ID 驗證**：比 SQL 驗證更安全
5. **啟用儲存空間自動成長**：避免空間不足的問題
6. **設定適當的備份保留期**：依合規需求設 7-35 天
7. **使用 private endpoint**：確保網路存取安全
8. **調整 server 參數**：依工作負載特性調整
9. **用 Azure Monitor 監控**：啟用 metric 與 log
10. **停用開發／測試用的 server**：不使用時省成本

## 錯誤處理

```csharp
using Azure;

try
{
    ArmOperation<MySqlFlexibleServerResource> operation = await servers
        .CreateOrUpdateAsync(WaitUntil.Completed, "my-mysql", data);
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
// ADO.NET connection string
string connectionString = $"Server={server.Data.FullyQualifiedDomainName};" +
    "Database=myappdb;" +
    "User Id=mysqladmin;" +
    "Password=YourSecurePassword123!;" +
    "SslMode=Required;";

// 使用 Entra ID token（建議）
var credential = new DefaultAzureCredential();
var token = await credential.GetTokenAsync(
    new TokenRequestContext(new[] { "https://ossrdbms-aad.database.windows.net/.default" }));

string connectionString = $"Server={server.Data.FullyQualifiedDomainName};" +
    "Database=myappdb;" +
    $"User Id=aad-admin@contoso.com;" +
    $"Password={token.Token};" +
    "SslMode=Required;";
```

## 相關 SDK

| SDK | 用途 | 安裝 |
|-----|---------|---------|
| `Azure.ResourceManager.MySql` | MySQL 管理（本 SDK） | `dotnet add package Azure.ResourceManager.MySql` |
| `Azure.ResourceManager.PostgreSql` | PostgreSQL 管理 | `dotnet add package Azure.ResourceManager.PostgreSql` |
| `MySqlConnector` | MySQL 資料存取 | `dotnet add package MySqlConnector` |

## 參考連結

| 資源 | URL |
|----------|-----|
| NuGet 套件 | https://www.nuget.org/packages/Azure.ResourceManager.MySql |
| API 參考 | https://learn.microsoft.com/dotnet/api/azure.resourcemanager.mysql |
| 產品文件 | https://learn.microsoft.com/azure/mysql/flexible-server/ |
| GitHub 原始碼 | https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/mysql/Azure.ResourceManager.MySql |
