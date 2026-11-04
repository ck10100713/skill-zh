---
name: azure-mgmt-applicationinsights-dotnet
description: |
  Azure Application Insights SDK for .NET。應用程式效能監控與可觀測性的資源管理。用於建立 Application Insights component、web test、workbook、分析項目和 API key。Triggers: "Application Insights", "ApplicationInsights", "App Insights", "APM", "application monitoring", "web tests", "availability tests", "workbooks".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.ResourceManager.ApplicationInsights
---

# Azure.ResourceManager.ApplicationInsights (.NET)

Azure Resource Manager SDK，用來管理做應用程式效能監控的 Application Insights 資源。

## 安裝

```bash
dotnet add package Azure.ResourceManager.ApplicationInsights
dotnet add package Azure.Identity
```

**目前版本**：v1.0.0 (GA)  
**API 版本**：2022-06-15

## 環境變數

```bash
AZURE_SUBSCRIPTION_ID=<your-subscription-id> # 必填：Azure subscription ID
AZURE_RESOURCE_GROUP=<your-resource-group> # 必填：Azure resource group 名稱
AZURE_APPINSIGHTS_NAME=<your-appinsights-component> # 必填：Application Insights component 名稱
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境用 DefaultAzureCredential 時才需要
```

## 認證

```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.ApplicationInsights;

// 本機開發：DefaultAzureCredential。正式環境：設 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
var credential = new DefaultAzureCredential(
    DefaultAzureCredential.DefaultEnvironmentVariableName
);
// 或在正式環境直接用特定的 credential：
// 見 https://learn.microsoft.com/dotnet/api/overview/azure/identity-readme?view=azure-dotnet#credential-classes
// var credential = new ManagedIdentityCredential();
ArmClient client = new ArmClient(credential);
```

## 資源階層

```
Subscription
└── ResourceGroup
    └── ApplicationInsightsComponent          # App Insights 資源
        ├── ApplicationInsightsComponentApiKey  # 程式化存取用的 API key
        ├── ComponentLinkedStorageAccount      # 資料匯出用的連結儲存體
        └── (via component ID)
            ├── WebTest                        # 可用性測試
            ├── Workbook                       # 分析用的 workbook
            ├── WorkbookTemplate               # Workbook 範本
            └── MyWorkbook                     # 私人 workbook
```

## 核心工作流程

### 1. 建立 Application Insights Component（以 Workspace 為基礎）

```csharp
using Azure.ResourceManager.ApplicationInsights;
using Azure.ResourceManager.ApplicationInsights.Models;

ResourceGroupResource resourceGroup = await client
    .GetDefaultSubscriptionAsync()
    .Result
    .GetResourceGroupAsync("my-resource-group");

ApplicationInsightsComponentCollection components = resourceGroup.GetApplicationInsightsComponents();

// 以 Workspace 為基礎的 Application Insights（建議）
ApplicationInsightsComponentData data = new ApplicationInsightsComponentData(
    AzureLocation.EastUS,
    ApplicationInsightsApplicationType.Web)
{
    Kind = "web",
    WorkspaceResourceId = new ResourceIdentifier(
        "/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.OperationalInsights/workspaces/<workspace-name>"),
    IngestionMode = IngestionMode.LogAnalytics,
    PublicNetworkAccessForIngestion = PublicNetworkAccessType.Enabled,
    PublicNetworkAccessForQuery = PublicNetworkAccessType.Enabled,
    RetentionInDays = 90,
    SamplingPercentage = 100,
    DisableIPMasking = false,
    ImmediatePurgeDataOn30Days = false,
    Tags =
    {
        { "environment", "production" },
        { "application", "mywebapp" }
    }
};

ArmOperation<ApplicationInsightsComponentResource> operation = await components
    .CreateOrUpdateAsync(WaitUntil.Completed, "my-appinsights", data);

ApplicationInsightsComponentResource component = operation.Value;

Console.WriteLine($"Component created: {component.Data.Name}");
Console.WriteLine($"Instrumentation Key: {component.Data.InstrumentationKey}");
Console.WriteLine($"Connection String: {component.Data.ConnectionString}");
```

### 2. 取得連線字串和 Key

```csharp
ApplicationInsightsComponentResource component = await resourceGroup
    .GetApplicationInsightsComponentAsync("my-appinsights");

// 取得 SDK 設定要用的連線字串
string connectionString = component.Data.ConnectionString;
string instrumentationKey = component.Data.InstrumentationKey;
string appId = component.Data.AppId;

Console.WriteLine($"Connection String: {connectionString}");
Console.WriteLine($"Instrumentation Key: {instrumentationKey}");
Console.WriteLine($"App ID: {appId}");
```

### 3. 建立 API Key

```csharp
ApplicationInsightsComponentResource component = await resourceGroup
    .GetApplicationInsightsComponentAsync("my-appinsights");

ApplicationInsightsComponentApiKeyCollection apiKeys = component.GetApplicationInsightsComponentApiKeys();

// 讀取遙測資料用的 API key
ApplicationInsightsApiKeyContent keyContent = new ApplicationInsightsApiKeyContent
{
    Name = "ReadTelemetryKey",
    LinkedReadProperties =
    {
        $"/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/microsoft.insights/components/{component.Data.Name}/api",
        $"/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/microsoft.insights/components/{component.Data.Name}/agentconfig"
    }
};

ApplicationInsightsComponentApiKeyResource apiKey = await apiKeys
    .CreateOrUpdateAsync(WaitUntil.Completed, keyContent);

Console.WriteLine($"API Key Name: {apiKey.Data.Name}");
Console.WriteLine($"API Key: {apiKey.Data.ApiKey}"); // 只會顯示一次！
```

### 4. 建立 Web Test（可用性測試）

```csharp
WebTestCollection webTests = resourceGroup.GetWebTests();

// URL Ping 測試
WebTestData urlPingTest = new WebTestData(AzureLocation.EastUS)
{
    Kind = WebTestKind.Ping,
    SyntheticMonitorId = "webtest-ping-myapp",
    WebTestName = "Homepage Availability",
    Description = "Checks if homepage is available",
    IsEnabled = true,
    Frequency = 300, // 5 分鐘
    Timeout = 120,   // 2 分鐘
    WebTestKind = WebTestKind.Ping,
    IsRetryEnabled = true,
    Locations =
    {
        new WebTestGeolocation { WebTestLocationId = "us-ca-sjc-azr" },  // West US
        new WebTestGeolocation { WebTestLocationId = "us-tx-sn1-azr" },  // South Central US
        new WebTestGeolocation { WebTestLocationId = "us-il-ch1-azr" },  // North Central US
        new WebTestGeolocation { WebTestLocationId = "emea-gb-db3-azr" }, // UK South
        new WebTestGeolocation { WebTestLocationId = "apac-sg-sin-azr" }  // Southeast Asia
    },
    Configuration = new WebTestConfiguration
    {
        WebTest = """
            <WebTest Name="Homepage" Enabled="True" Timeout="120" 
                     xmlns="http://microsoft.com/schemas/VisualStudio/TeamTest/2010">
                <Items>
                    <Request Method="GET" Version="1.1" Url="https://myapp.example.com" 
                             ThinkTime="0" Timeout="120" ParseDependentRequests="False" 
                             FollowRedirects="True" RecordResult="True" Cache="False" 
                             ResponseTimeGoal="0" Encoding="utf-8" ExpectedHttpStatusCode="200" />
                </Items>
            </WebTest>
        """
    },
    Tags =
    {
        { $"hidden-link:/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/microsoft.insights/components/my-appinsights", "Resource" }
    }
};

ArmOperation<WebTestResource> operation = await webTests
    .CreateOrUpdateAsync(WaitUntil.Completed, "webtest-homepage", urlPingTest);

WebTestResource webTest = operation.Value;
Console.WriteLine($"Web test created: {webTest.Data.Name}");
```

### 5. 建立多步驟 Web Test

```csharp
WebTestData multiStepTest = new WebTestData(AzureLocation.EastUS)
{
    Kind = WebTestKind.MultiStep,
    SyntheticMonitorId = "webtest-multistep-login",
    WebTestName = "Login Flow Test",
    Description = "Tests login functionality",
    IsEnabled = true,
    Frequency = 900, // 15 分鐘
    Timeout = 300,   // 5 分鐘
    WebTestKind = WebTestKind.MultiStep,
    IsRetryEnabled = true,
    Locations =
    {
        new WebTestGeolocation { WebTestLocationId = "us-ca-sjc-azr" }
    },
    Configuration = new WebTestConfiguration
    {
        WebTest = """
            <WebTest Name="LoginFlow" Enabled="True" Timeout="300"
                     xmlns="http://microsoft.com/schemas/VisualStudio/TeamTest/2010">
                <Items>
                    <Request Method="GET" Version="1.1" Url="https://myapp.example.com/login" 
                             ThinkTime="0" Timeout="60" />
                    <Request Method="POST" Version="1.1" Url="https://myapp.example.com/api/auth" 
                             ThinkTime="0" Timeout="60">
                        <Headers>
                            <Header Name="Content-Type" Value="application/json" />
                        </Headers>
                        <Body>{"username":"testuser","password":"{{TestPassword}}"}</Body>
                    </Request>
                </Items>
            </WebTest>
        """
    },
    Tags =
    {
        { $"hidden-link:/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/microsoft.insights/components/my-appinsights", "Resource" }
    }
};

await webTests.CreateOrUpdateAsync(WaitUntil.Completed, "webtest-login-flow", multiStepTest);
```

### 6. 建立 Workbook

```csharp
WorkbookCollection workbooks = resourceGroup.GetWorkbooks();

WorkbookData workbookData = new WorkbookData(AzureLocation.EastUS)
{
    DisplayName = "Application Performance Dashboard",
    Category = "workbook",
    Kind = WorkbookSharedTypeKind.Shared,
    SerializedData = """
    {
        "version": "Notebook/1.0",
        "items": [
            {
                "type": 1,
                "content": {
                    "json": "# Application Performance\n\nThis workbook shows application performance metrics."
                },
                "name": "header"
            },
            {
                "type": 3,
                "content": {
                    "version": "KqlItem/1.0",
                    "query": "requests\n| summarize count() by bin(timestamp, 1h)\n| render timechart",
                    "size": 0,
                    "title": "Requests per Hour",
                    "timeContext": {
                        "durationMs": 86400000
                    },
                    "queryType": 0,
                    "resourceType": "microsoft.insights/components"
                },
                "name": "requestsChart"
            }
        ],
        "isLocked": false
    }
    """,
    SourceId = component.Id,
    Tags =
    {
        { "environment", "production" }
    }
};

// 注意：Workbook ID 應該是新的 GUID
string workbookId = Guid.NewGuid().ToString();

ArmOperation<WorkbookResource> operation = await workbooks
    .CreateOrUpdateAsync(WaitUntil.Completed, workbookId, workbookData);

WorkbookResource workbook = operation.Value;
Console.WriteLine($"Workbook created: {workbook.Data.DisplayName}");
```

### 7. 連結儲存體帳號

```csharp
ApplicationInsightsComponentResource component = await resourceGroup
    .GetApplicationInsightsComponentAsync("my-appinsights");

ComponentLinkedStorageAccountCollection linkedStorage = component.GetComponentLinkedStorageAccounts();

ComponentLinkedStorageAccountData storageData = new ComponentLinkedStorageAccountData
{
    LinkedStorageAccount = new ResourceIdentifier(
        "/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/<storage-account>")
};

ArmOperation<ComponentLinkedStorageAccountResource> operation = await linkedStorage
    .CreateOrUpdateAsync(WaitUntil.Completed, StorageType.ServiceProfiler, storageData);
```

### 8. 列出與管理 Component

```csharp
// 列出 resource group 裡所有 Application Insights component
await foreach (ApplicationInsightsComponentResource component in 
    resourceGroup.GetApplicationInsightsComponents())
{
    Console.WriteLine($"Component: {component.Data.Name}");
    Console.WriteLine($"  App ID: {component.Data.AppId}");
    Console.WriteLine($"  Type: {component.Data.ApplicationType}");
    Console.WriteLine($"  Ingestion Mode: {component.Data.IngestionMode}");
    Console.WriteLine($"  Retention: {component.Data.RetentionInDays} days");
}

// 列出 web test
await foreach (WebTestResource webTest in resourceGroup.GetWebTests())
{
    Console.WriteLine($"Web Test: {webTest.Data.WebTestName}");
    Console.WriteLine($"  Enabled: {webTest.Data.IsEnabled}");
    Console.WriteLine($"  Frequency: {webTest.Data.Frequency}s");
}

// 列出 workbook
await foreach (WorkbookResource workbook in resourceGroup.GetWorkbooks())
{
    Console.WriteLine($"Workbook: {workbook.Data.DisplayName}");
}
```

### 9. 更新 Component

```csharp
ApplicationInsightsComponentResource component = await resourceGroup
    .GetApplicationInsightsComponentAsync("my-appinsights");

// 用完整資料更新（PUT 操作）
ApplicationInsightsComponentData updateData = component.Data;
updateData.RetentionInDays = 180;
updateData.SamplingPercentage = 50;
updateData.Tags["updated"] = "true";

ArmOperation<ApplicationInsightsComponentResource> operation = await resourceGroup
    .GetApplicationInsightsComponents()
    .CreateOrUpdateAsync(WaitUntil.Completed, "my-appinsights", updateData);
```

### 10. 刪除資源

```csharp
// 刪除 Application Insights component
ApplicationInsightsComponentResource component = await resourceGroup
    .GetApplicationInsightsComponentAsync("my-appinsights");
await component.DeleteAsync(WaitUntil.Completed);

// 刪除 web test
WebTestResource webTest = await resourceGroup.GetWebTestAsync("webtest-homepage");
await webTest.DeleteAsync(WaitUntil.Completed);
```

## 主要型別參考

| 型別 | 用途 |
|------|---------|
| `ApplicationInsightsComponentResource` | App Insights component |
| `ApplicationInsightsComponentData` | Component 設定 |
| `ApplicationInsightsComponentCollection` | Component 的集合 |
| `ApplicationInsightsComponentApiKeyResource` | 程式化存取用的 API key |
| `WebTestResource` | 可用性/web 測試 |
| `WebTestData` | Web test 設定 |
| `WorkbookResource` | 分析用 workbook |
| `WorkbookData` | Workbook 設定 |
| `ComponentLinkedStorageAccountResource` | 匯出用的連結儲存體 |

## 應用程式類型

| 類型 | Enum 值 |
|------|------------|
| Web 應用程式 | `Web` |
| iOS 應用程式 | `iOS` |
| Java 應用程式 | `Java` |
| Node.js 應用程式 | `NodeJS` |
| .NET 應用程式 | `MRT` |
| 其他 | `Other` |

## Web Test 位置

| 位置 ID | 區域 |
|-------------|--------|
| `us-ca-sjc-azr` | West US |
| `us-tx-sn1-azr` | South Central US |
| `us-il-ch1-azr` | North Central US |
| `us-va-ash-azr` | East US |
| `emea-gb-db3-azr` | UK South |
| `emea-nl-ams-azr` | West Europe |
| `emea-fr-pra-edge` | France Central |
| `apac-sg-sin-azr` | Southeast Asia |
| `apac-hk-hkn-azr` | East Asia |
| `apac-jp-kaw-edge` | Japan East |
| `latam-br-gru-edge` | Brazil South |
| `emea-au-syd-edge` | Australia East |

## 最佳實務

1. **用 workspace-based**：以 Workspace 為基礎的 App Insights 是目前的標準
2. **連結到 Log Analytics**：把資料存在 Log Analytics，查詢比較方便
3. **設定合適的保留期限**：在成本和資料可用性之間取平衡
4. **用 sampling**：降低高流量應用程式的成本
5. **安全地儲存連線字串**：用 Key Vault 或 managed identity
6. **啟用多個測試位置**：可用性監控才會準確
7. **用 workbook**：做自訂 dashboard 和分析
8. **設定警示**：依據可用性測試和指標
9. **替資源加 tag**：方便成本分攤和整理
10. **用 private endpoint**：做安全的資料擷取

## 錯誤處理

```csharp
using Azure;

try
{
    ArmOperation<ApplicationInsightsComponentResource> operation = await components
        .CreateOrUpdateAsync(WaitUntil.Completed, "my-appinsights", data);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("Component already exists");
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

## SDK 整合

把連線字串搭配 Application Insights SDK 使用：

```csharp
// ASP.NET Core 的 Program.cs
builder.Services.AddApplicationInsightsTelemetry(options =>
{
    options.ConnectionString = configuration["ApplicationInsights:ConnectionString"];
});

// 或透過環境變數設定
// APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...;IngestionEndpoint=...
```

## 相關 SDK

| SDK | 用途 | 安裝 |
|-----|---------|---------|
| `Azure.ResourceManager.ApplicationInsights` | 資源管理（就是這個 SDK） | `dotnet add package Azure.ResourceManager.ApplicationInsights` |
| `Microsoft.ApplicationInsights` | 遙測 SDK | `dotnet add package Microsoft.ApplicationInsights` |
| `Microsoft.ApplicationInsights.AspNetCore` | ASP.NET Core 整合 | `dotnet add package Microsoft.ApplicationInsights.AspNetCore` |
| `Azure.Monitor.OpenTelemetry.Exporter` | OpenTelemetry 匯出 | `dotnet add package Azure.Monitor.OpenTelemetry.Exporter` |

## 參考連結

| 資源 | URL |
|----------|-----|
| NuGet 套件 | https://www.nuget.org/packages/Azure.ResourceManager.ApplicationInsights |
| API 參考 | https://learn.microsoft.com/dotnet/api/azure.resourcemanager.applicationinsights |
| 產品文件 | https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview |
| GitHub 原始碼 | https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/applicationinsights/Azure.ResourceManager.ApplicationInsights |
