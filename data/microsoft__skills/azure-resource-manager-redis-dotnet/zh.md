---
name: azure-resource-manager-redis-dotnet
description: |
  .NET 版 Redis 的 Azure Resource Manager SDK。用於 MANAGEMENT PLANE（管理平面）操作：透過 Azure Resource Manager 建立／管理 Azure Cache for Redis instance、防火牆規則、access key、patch 排程、linked server（geo-replication）與 private endpoint。NOT 用於 data plane 操作（get/set key、pub/sub），那種請用 StackExchange.Redis。Triggers: "Redis cache", "create Redis", "manage Redis", "ARM Redis", "RedisResource", "provision Redis", "Azure Cache for Redis".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.ResourceManager.Redis
---

# Azure.ResourceManager.Redis (.NET)

管理平面 SDK，透過 Azure Resource Manager 佈建與管理 Azure Cache for Redis 資源。

> **⚠️ 管理平面 vs Data Plane**
> - **這個 SDK（Azure.ResourceManager.Redis）**：建立 cache、設定防火牆規則、管理 access key、設定 geo-replication
> - **Data Plane SDK（StackExchange.Redis）**：get/set key、pub/sub、stream、Lua script

## 安裝

```bash
dotnet add package Azure.ResourceManager.Redis
dotnet add package Azure.Identity
```

**目前版本**：1.5.1 (Stable)  
**API 版本**：2024-11-01  
**目標 Framework**：.NET 8.0、.NET Standard 2.0

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
using Azure.ResourceManager.Redis;

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
        └── RedisResource
            ├── RedisFirewallRuleResource
            ├── RedisPatchScheduleResource
            ├── RedisLinkedServerWithPropertyResource
            ├── RedisPrivateEndpointConnectionResource
            └── RedisCacheAccessPolicyResource
```

## 核心流程

### 1. 建立 Redis Cache

```csharp
using Azure.ResourceManager.Redis;
using Azure.ResourceManager.Redis.Models;

// 取得 resource group
var resourceGroup = await subscription
    .GetResourceGroupAsync("my-resource-group");

// 定義 cache 設定
var cacheData = new RedisCreateOrUpdateContent(
    location: AzureLocation.EastUS,
    sku: new RedisSku(RedisSkuName.Standard, RedisSkuFamily.BasicOrStandard, 1))
{
    EnableNonSslPort = false,
    MinimumTlsVersion = RedisTlsVersion.Tls1_2,
    RedisConfiguration = new RedisCommonConfiguration
    {
        MaxMemoryPolicy = "volatile-lru"
    },
    Tags =
    {
        ["environment"] = "production"
    }
};

// 建立 cache（長時間執行的操作）
var cacheCollection = resourceGroup.Value.GetAllRedis();
var operation = await cacheCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-redis-cache",
    cacheData);

RedisResource cache = operation.Value;
Console.WriteLine($"Cache created: {cache.Data.HostName}");
```

### 2. 取得 Redis Cache

```csharp
// 取得既有的 cache
var cache = await resourceGroup.Value
    .GetRedisAsync("my-redis-cache");

Console.WriteLine($"Host: {cache.Value.Data.HostName}");
Console.WriteLine($"Port: {cache.Value.Data.Port}");
Console.WriteLine($"SSL Port: {cache.Value.Data.SslPort}");
Console.WriteLine($"Provisioning State: {cache.Value.Data.ProvisioningState}");
```

### 3. 更新 Redis Cache

```csharp
var patchData = new RedisPatch
{
    Sku = new RedisSku(RedisSkuName.Standard, RedisSkuFamily.BasicOrStandard, 2),
    RedisConfiguration = new RedisCommonConfiguration
    {
        MaxMemoryPolicy = "allkeys-lru"
    }
};

var updateOperation = await cache.Value.UpdateAsync(
    WaitUntil.Completed,
    patchData);
```

### 4. 刪除 Redis Cache

```csharp
await cache.Value.DeleteAsync(WaitUntil.Completed);
```

### 5. 取得 Access Key

```csharp
var keys = await cache.Value.GetKeysAsync();
Console.WriteLine($"Primary Key: {keys.Value.PrimaryKey}");
Console.WriteLine($"Secondary Key: {keys.Value.SecondaryKey}");
```

### 6. 重新產生 Access Key

```csharp
var regenerateContent = new RedisRegenerateKeyContent(RedisRegenerateKeyType.Primary);
var newKeys = await cache.Value.RegenerateKeyAsync(regenerateContent);
Console.WriteLine($"New Primary Key: {newKeys.Value.PrimaryKey}");
```

### 7. 管理防火牆規則

```csharp
// 建立防火牆規則
var firewallData = new RedisFirewallRuleData(
    startIP: System.Net.IPAddress.Parse("10.0.0.1"),
    endIP: System.Net.IPAddress.Parse("10.0.0.255"));

var firewallCollection = cache.Value.GetRedisFirewallRules();
var firewallOperation = await firewallCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "allow-internal-network",
    firewallData);

// 列出所有防火牆規則
await foreach (var rule in firewallCollection.GetAllAsync())
{
    Console.WriteLine($"Rule: {rule.Data.Name} ({rule.Data.StartIP} - {rule.Data.EndIP})");
}

// 刪除防火牆規則
var ruleToDelete = await firewallCollection.GetAsync("allow-internal-network");
await ruleToDelete.Value.DeleteAsync(WaitUntil.Completed);
```

### 8. 設定 Patch 排程（Premium SKU）

```csharp
// Patch 排程需要 Premium SKU
var scheduleData = new RedisPatchScheduleData(
    new[]
    {
        new RedisPatchScheduleSetting(RedisDayOfWeek.Saturday, 2) // 週六凌晨 2 點
        {
            MaintenanceWindow = TimeSpan.FromHours(5)
        },
        new RedisPatchScheduleSetting(RedisDayOfWeek.Sunday, 2) // 週日凌晨 2 點
        {
            MaintenanceWindow = TimeSpan.FromHours(5)
        }
    });

var scheduleCollection = cache.Value.GetRedisPatchSchedules();
await scheduleCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    RedisPatchScheduleDefaultName.Default,
    scheduleData);
```

### 9. 匯入／匯出資料（Premium SKU）

```csharp
// 從 blob storage 匯入資料
var importContent = new ImportRdbContent(
    files: new[] { "https://mystorageaccount.blob.core.windows.net/container/dump.rdb" },
    format: "RDB");

await cache.Value.ImportDataAsync(WaitUntil.Completed, importContent);

// 匯出資料到 blob storage
var exportContent = new ExportRdbContent(
    prefix: "backup",
    container: "https://mystorageaccount.blob.core.windows.net/container?sastoken",
    format: "RDB");

await cache.Value.ExportDataAsync(WaitUntil.Completed, exportContent);
```

### 10. 強制重新開機

```csharp
var rebootContent = new RedisRebootContent
{
    RebootType = RedisRebootType.AllNodes,
    ShardId = 0 // 用於 cluster 模式的 cache
};

await cache.Value.ForceRebootAsync(rebootContent);
```

## SKU 參考

| SKU | Family | 容量 | 功能 |
|-----|--------|----------|----------|
| Basic | C | 0-6 | 單一節點、沒有 SLA，只適合開發／測試 |
| Standard | C | 0-6 | 兩個節點（primary/replica）、有 SLA |
| Premium | P | 1-5 | Clustering、geo-replication、VNet、persistence |

**容量大小（Family C，Basic/Standard）**：
- C0: 250 MB
- C1: 1 GB
- C2: 2.5 GB
- C3: 6 GB
- C4: 13 GB
- C5: 26 GB
- C6: 53 GB

**容量大小（Family P，Premium）**：
- P1：每個 shard 6 GB
- P2：每個 shard 13 GB
- P3：每個 shard 26 GB
- P4：每個 shard 53 GB
- P5：每個 shard 120 GB

## 主要型別參考

| 型別 | 用途 |
|------|---------|
| `ArmClient` | 所有 ARM 操作的進入點 |
| `RedisResource` | 代表一個 Redis cache instance |
| `RedisCollection` | cache CRUD 操作的集合 |
| `RedisFirewallRuleResource` | 用於 IP 過濾的防火牆規則 |
| `RedisPatchScheduleResource` | 維護時段設定 |
| `RedisLinkedServerWithPropertyResource` | Geo-replication 的 linked server |
| `RedisPrivateEndpointConnectionResource` | Private endpoint 連線 |
| `RedisCacheAccessPolicyResource` | RBAC 存取政策 |
| `RedisCreateOrUpdateContent` | 建立 cache 的 payload |
| `RedisPatch` | 更新 cache 的 payload |
| `RedisSku` | SKU 設定（name、family、capacity） |
| `RedisAccessKeys` | Primary 與 secondary access key |
| `RedisRegenerateKeyContent` | 重新產生 key 的請求 |

## 最佳實務

1. **需要等操作完成才能繼續時，用 `WaitUntil.Completed`**
2. **想自己輪詢或平行執行操作時，用 `WaitUntil.Started`**
3. **一律使用 `DefaultAzureCredential`**：絕對不要寫死 key
4. **處理 `RequestFailedException`**，因應 ARM API 的錯誤
5. **使用 `CreateOrUpdateAsync`** 做冪等操作
6. **透過 `Get*` 方法走訪階層**（例如 `cache.GetRedisFirewallRules()`）
7. **需要 geo-replication、clustering 或 persistence 的正式環境工作負載，用 Premium SKU**
8. **TLS 最低用 1.2**：設定 `MinimumTlsVersion = RedisTlsVersion.Tls1_2`
9. **停用非 SSL port**：為了安全，設定 `EnableNonSslPort = false`
10. **定期輪替 key**：用 `RegenerateKeyAsync`，並更新 connection string

## 錯誤處理

```csharp
using Azure;

try
{
    var operation = await cacheCollection.CreateOrUpdateAsync(
        WaitUntil.Completed, cacheName, cacheData);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("Cache already exists");
}
catch (RequestFailedException ex) when (ex.Status == 400)
{
    Console.WriteLine($"Invalid configuration: {ex.Message}");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"ARM Error: {ex.Status} - {ex.ErrorCode}: {ex.Message}");
}
```

## 常見陷阱

1. **SKU 不能降級**：不能從 Premium 降到 Standard/Basic
2. **Clustering 需要 Premium**：shard 設定只有 Premium SKU 才有
3. **Geo-replication 需要 Premium**：linked server 只能用在 Premium cache
4. **VNet injection 需要 Premium**：虛擬網路支援僅限 Premium
5. **Patch 排程需要 Premium**：維護時段只有 Premium 才能設定
6. **Cache 名稱必須全域唯一**：Redis cache 名稱在所有 Azure subscription 中都不能重複
7. **佈建時間很長**：建立 cache 可能要 15-20 分鐘；非同步模式用 `WaitUntil.Started`

## 用 StackExchange.Redis 連線（Data Plane）

用這個管理 SDK 建立 cache 之後，用 StackExchange.Redis 做資料操作：

```csharp
using StackExchange.Redis;

// 從管理 SDK 取得連線資訊
var cache = await resourceGroup.Value.GetRedisAsync("my-redis-cache");
var keys = await cache.Value.GetKeysAsync();

// 用 StackExchange.Redis 連線
var connectionString = $"{cache.Value.Data.HostName}:{cache.Value.Data.SslPort},password={keys.Value.PrimaryKey},ssl=True,abortConnect=False";
var connection = ConnectionMultiplexer.Connect(connectionString);
var db = connection.GetDatabase();

// 資料操作
await db.StringSetAsync("key", "value");
var value = await db.StringGetAsync("key");
```

## 相關 SDK

| SDK | 用途 | 安裝 |
|-----|---------|---------|
| `StackExchange.Redis` | Data plane（get/set、pub/sub、stream） | `dotnet add package StackExchange.Redis` |
| `Azure.ResourceManager.Redis` | 管理平面（本 SDK） | `dotnet add package Azure.ResourceManager.Redis` |
| `Microsoft.Azure.StackExchangeRedis` | Azure 專屬的 Redis 擴充 | `dotnet add package Microsoft.Azure.StackExchangeRedis` |
