---
name: azure-resource-manager-playwright-dotnet
description: |
  .NET 版 Microsoft Playwright Testing 的 Azure Resource Manager SDK。用於 MANAGEMENT PLANE（管理平面）操作：透過 Azure Resource Manager 建立／管理 Playwright Testing workspace、檢查名稱是否可用，以及管理 workspace quota。NOT 用於執行 Playwright 測試，那種請用 Azure.Developer.MicrosoftPlaywrightTesting.NUnit。Triggers: "Playwright workspace", "create Playwright Testing workspace", "manage Playwright resources", "ARM Playwright", "PlaywrightWorkspaceResource", "provision Playwright Testing".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.ResourceManager.Playwright
---

# Azure.ResourceManager.Playwright (.NET)

管理平面 SDK，透過 Azure Resource Manager 佈建與管理 Microsoft Playwright Testing workspace。

> **⚠️ 管理 vs 測試執行**
> - **這個 SDK（Azure.ResourceManager.Playwright）**：建立 workspace、管理 quota、檢查名稱是否可用
> - **測試執行 SDK（Azure.Developer.MicrosoftPlaywrightTesting.NUnit）**：在雲端瀏覽器上大規模執行 Playwright 測試

## 安裝

```bash
dotnet add package Azure.ResourceManager.Playwright
dotnet add package Azure.Identity
```

**目前版本**：Stable v1.0.0、Preview v1.0.0-beta.1

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
using Azure.ResourceManager.Playwright;

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
    ├── PlaywrightQuotaResource (subscription-level quotas)
    └── ResourceGroupResource
        └── PlaywrightWorkspaceResource
            └── PlaywrightWorkspaceQuotaResource (workspace-level quotas)
```

## 核心流程

### 1. 建立 Playwright Workspace

```csharp
using Azure.ResourceManager.Playwright;
using Azure.ResourceManager.Playwright.Models;

// 取得 resource group
var resourceGroup = await subscription
    .GetResourceGroupAsync("my-resource-group");

// 定義 workspace
var workspaceData = new PlaywrightWorkspaceData(AzureLocation.WestUS3)
{
    // 選用：設定區域親和性與本地驗證
    RegionalAffinity = PlaywrightRegionalAffinity.Enabled,
    LocalAuth = PlaywrightLocalAuth.Enabled,
    Tags =
    {
        ["Team"] = "Dev Exp",
        ["Environment"] = "Production"
    }
};

// 建立 workspace（長時間執行的操作）
var workspaceCollection = resourceGroup.Value.GetPlaywrightWorkspaces();
var operation = await workspaceCollection.CreateOrUpdateAsync(
    WaitUntil.Completed,
    "my-playwright-workspace",
    workspaceData);

PlaywrightWorkspaceResource workspace = operation.Value;

// 取得執行測試用的 data plane URI
Console.WriteLine($"Data Plane URI: {workspace.Data.DataplaneUri}");
Console.WriteLine($"Workspace ID: {workspace.Data.WorkspaceId}");
```

### 2. 取得既有 Workspace

```csharp
// 依名稱取得
var workspace = await workspaceCollection.GetAsync("my-playwright-workspace");

// 或先檢查是否存在
bool exists = await workspaceCollection.ExistsAsync("my-playwright-workspace");
if (exists)
{
    var existingWorkspace = await workspaceCollection.GetAsync("my-playwright-workspace");
    Console.WriteLine($"Workspace found: {existingWorkspace.Value.Data.Name}");
}
```

### 3. 列出 Workspace

```csharp
// 列出 resource group 內的
await foreach (var workspace in workspaceCollection.GetAllAsync())
{
    Console.WriteLine($"Workspace: {workspace.Data.Name}");
    Console.WriteLine($"  Location: {workspace.Data.Location}");
    Console.WriteLine($"  State: {workspace.Data.ProvisioningState}");
    Console.WriteLine($"  Data Plane URI: {workspace.Data.DataplaneUri}");
}

// 列出整個 subscription 內的
await foreach (var workspace in subscription.GetPlaywrightWorkspacesAsync())
{
    Console.WriteLine($"Workspace: {workspace.Data.Name}");
}
```

### 4. 更新 Workspace

```csharp
var patch = new PlaywrightWorkspacePatch
{
    Tags =
    {
        ["Team"] = "Dev Exp",
        ["Environment"] = "Staging",
        ["UpdatedAt"] = DateTime.UtcNow.ToString("o")
    }
};

var updatedWorkspace = await workspace.Value.UpdateAsync(patch);
```

### 5. 檢查名稱是否可用

```csharp
using Azure.ResourceManager.Playwright.Models;

var checkRequest = new PlaywrightCheckNameAvailabilityContent
{
    Name = "my-new-workspace",
    ResourceType = "Microsoft.LoadTestService/playwrightWorkspaces"
};

var result = await subscription.CheckPlaywrightNameAvailabilityAsync(checkRequest);

if (result.Value.IsNameAvailable == true)
{
    Console.WriteLine("Name is available!");
}
else
{
    Console.WriteLine($"Name unavailable: {result.Value.Message}");
    Console.WriteLine($"Reason: {result.Value.Reason}");
}
```

### 6. 取得 Quota 資訊

```csharp
// Subscription 層級的 quota
await foreach (var quota in subscription.GetPlaywrightQuotasAsync(AzureLocation.WestUS3))
{
    Console.WriteLine($"Quota: {quota.Data.Name}");
    Console.WriteLine($"  Limit: {quota.Data.Limit}");
    Console.WriteLine($"  Used: {quota.Data.Used}");
}

// Workspace 層級的 quota
var workspaceQuotas = workspace.Value.GetAllPlaywrightWorkspaceQuota();
await foreach (var quota in workspaceQuotas.GetAllAsync())
{
    Console.WriteLine($"Workspace Quota: {quota.Data.Name}");
}
```

### 7. 刪除 Workspace

```csharp
// 刪除（長時間執行的操作）
await workspace.Value.DeleteAsync(WaitUntil.Completed);
```

## 主要型別參考

| 型別 | 用途 |
|------|---------|
| `ArmClient` | 所有 ARM 操作的進入點 |
| `PlaywrightWorkspaceResource` | 代表一個 Playwright Testing workspace |
| `PlaywrightWorkspaceCollection` | workspace CRUD 的集合 |
| `PlaywrightWorkspaceData` | workspace 建立／回應的 payload |
| `PlaywrightWorkspacePatch` | workspace 更新的 payload |
| `PlaywrightQuotaResource` | Subscription 層級的 quota 資訊 |
| `PlaywrightWorkspaceQuotaResource` | Workspace 層級的 quota 資訊 |
| `PlaywrightExtensions` | ARM 資源的 extension method |
| `PlaywrightCheckNameAvailabilityContent` | 檢查名稱是否可用的請求 |

## Workspace 屬性

| 屬性 | 說明 |
|----------|-------------|
| `DataplaneUri` | 執行測試用的 URI（例如 `https://api.dataplane.{guid}.domain.com`） |
| `WorkspaceId` | workspace 的唯一識別碼 (GUID) |
| `RegionalAffinity` | 啟用／停用測試執行的區域親和性 |
| `LocalAuth` | 啟用／停用本地驗證（access token） |
| `ProvisioningState` | 目前的佈建狀態（Succeeded、Failed 等） |

## 最佳實務

1. **需要等操作完成才能繼續時，用 `WaitUntil.Completed`**
2. **想自己輪詢或平行執行操作時，用 `WaitUntil.Started`**
3. **一律使用 `DefaultAzureCredential`**：絕對不要寫死 key
4. **處理 `RequestFailedException`**，因應 ARM API 的錯誤
5. **使用 `CreateOrUpdateAsync`** 做冪等操作
6. **透過 `Get*` 方法走訪階層**（例如 `resourceGroup.GetPlaywrightWorkspaces()`）
7. **建立 workspace 後儲存 DataplaneUri**，供測試執行的設定使用

## 錯誤處理

```csharp
using Azure;

try
{
    var operation = await workspaceCollection.CreateOrUpdateAsync(
        WaitUntil.Completed, workspaceName, workspaceData);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("Workspace already exists");
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

## 與測試執行整合

建立 workspace 之後，用 `DataplaneUri` 設定你的 Playwright 測試：

```csharp
// 1. 建立 workspace（本 SDK）
var workspace = await workspaceCollection.CreateOrUpdateAsync(
    WaitUntil.Completed, "my-workspace", workspaceData);

// 2. 取得 service URL
var serviceUrl = workspace.Value.Data.DataplaneUri;

// 3. 設定測試執行用的環境變數
Environment.SetEnvironmentVariable("PLAYWRIGHT_SERVICE_URL", serviceUrl.ToString());

// 4. 用 Azure.Developer.MicrosoftPlaywrightTesting.NUnit 執行測試
// （另外的測試執行套件）
```

## 相關 SDK

| SDK | 用途 | 安裝 |
|-----|---------|---------|
| `Azure.ResourceManager.Playwright` | 管理平面（本 SDK） | `dotnet add package Azure.ResourceManager.Playwright` |
| `Azure.Developer.MicrosoftPlaywrightTesting.NUnit` | 大規模執行 NUnit Playwright 測試 | `dotnet add package Azure.Developer.MicrosoftPlaywrightTesting.NUnit --prerelease` |
| `Azure.Developer.Playwright` | Playwright client library | `dotnet add package Azure.Developer.Playwright` |

## API 資訊

- **Resource Provider**：`Microsoft.LoadTestService`
- **預設 API 版本**：`2025-09-01`
- **Resource Type**：`Microsoft.LoadTestService/playwrightWorkspaces`

## 文件連結

- [Azure.ResourceManager.Playwright API 參考](https://learn.microsoft.com/en-us/dotnet/api/azure.resourcemanager.playwright)
- [Microsoft Playwright Testing 概觀](https://learn.microsoft.com/en-us/azure/playwright-testing/overview-what-is-microsoft-playwright-testing)
- [快速入門：大規模執行 Playwright 測試](https://learn.microsoft.com/en-us/azure/playwright-testing/quickstart-run-end-to-end-tests)
