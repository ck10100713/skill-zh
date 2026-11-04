---
name: azure-mgmt-botservice-dotnet
description: |
  .NET 用的 Azure Resource Manager SDK，管理 Bot Service。管理平面操作，用於建立和管理 Azure Bot 資源、channel（Teams、DirectLine、Slack）和連線設定。Triggers: "Bot Service", "BotResource", "Azure Bot", "DirectLine channel", "Teams channel", "bot management .NET", "create bot".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.ResourceManager.BotService
---

# Azure.ResourceManager.BotService (.NET)

管理平面 SDK，透過 Azure Resource Manager 佈建和管理 Azure Bot Service 資源。

## 安裝

```bash
dotnet add package Azure.ResourceManager.BotService
dotnet add package Azure.Identity
```

**目前版本**：穩定版 v1.1.1，預覽版 v1.1.0-beta.1

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
using Azure.ResourceManager.BotService;

// 本機開發：DefaultAzureCredential。正式環境：設 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
var credential = new DefaultAzureCredential(
    DefaultAzureCredential.DefaultEnvironmentVariableName
);
// 或在正式環境直接用特定的 credential：
// 見 https://learn.microsoft.com/dotnet/api/overview/azure/identity-readme?view=azure-dotnet#credential-classes
// var credential = new ManagedIdentityCredential();
ArmClient armClient = new ArmClient(credential);

// 取得 subscription 和 resource group
SubscriptionResource subscription = await armClient.GetDefaultSubscriptionAsync();
ResourceGroupResource resourceGroup = await subscription.GetResourceGroups().GetAsync("myResourceGroup");

// 存取 bot 集合
BotCollection botCollection = resourceGroup.GetBots();
```

## 資源階層

```
ArmClient
└── SubscriptionResource
    └── ResourceGroupResource
        └── BotResource
            ├── BotChannelResource (DirectLine, Teams, Slack, etc.)
            ├── BotConnectionSettingResource (OAuth connections)
            └── BotServicePrivateEndpointConnectionResource
```

## 核心工作流程

### 1. 建立 Bot 資源

```csharp
using Azure.ResourceManager.BotService;
using Azure.ResourceManager.BotService.Models;

// 建立 bot 資料
var botData = new BotData(AzureLocation.WestUS2)
{
    Kind = BotServiceKind.Azurebot,
    Sku = new BotServiceSku(BotServiceSkuName.F0),
    Properties = new BotProperties(
        displayName: "MyBot",
        endpoint: new Uri("https://mybot.azurewebsites.net/api/messages"),
        msaAppId: "<your-msa-app-id>")
    {
        Description = "My Azure Bot",
        MsaAppType = BotMsaAppType.MultiTenant
    }
};

// 建立或更新 bot
ArmOperation<BotResource> operation = await botCollection.CreateOrUpdateAsync(
    WaitUntil.Completed, 
    "myBotName", 
    botData);
    
BotResource bot = operation.Value;
Console.WriteLine($"Bot created: {bot.Data.Name}");
```

### 2. 設定 DirectLine Channel

```csharp
// 取得 bot
BotResource bot = await resourceGroup.GetBots().GetAsync("myBotName");

// 取得 channel 集合
BotChannelCollection channels = bot.GetBotChannels();

// 建立 DirectLine channel 設定
var channelData = new BotChannelData(AzureLocation.WestUS2)
{
    Properties = new DirectLineChannel()
    {
        Properties = new DirectLineChannelProperties()
        {
            Sites = 
            {
                new DirectLineSite("Default Site")
                {
                    IsEnabled = true,
                    IsV1Enabled = false,
                    IsV3Enabled = true,
                    IsSecureSiteEnabled = true
                }
            }
        }
    }
};

// 建立或更新 channel
ArmOperation<BotChannelResource> channelOp = await channels.CreateOrUpdateAsync(
    WaitUntil.Completed,
    BotChannelName.DirectLineChannel,
    channelData);

Console.WriteLine("DirectLine channel configured");
```

### 3. 設定 Microsoft Teams Channel

```csharp
var teamsChannelData = new BotChannelData(AzureLocation.WestUS2)
{
    Properties = new MsTeamsChannel()
    {
        Properties = new MsTeamsChannelProperties()
        {
            IsEnabled = true,
            EnableCalling = false
        }
    }
};

await channels.CreateOrUpdateAsync(
    WaitUntil.Completed,
    BotChannelName.MsTeamsChannel,
    teamsChannelData);
```

### 4. 設定 Web Chat Channel

```csharp
var webChatChannelData = new BotChannelData(AzureLocation.WestUS2)
{
    Properties = new WebChatChannel()
    {
        Properties = new WebChatChannelProperties()
        {
            Sites =
            {
                new WebChatSite("Default Site")
                {
                    IsEnabled = true
                }
            }
        }
    }
};

await channels.CreateOrUpdateAsync(
    WaitUntil.Completed,
    BotChannelName.WebChatChannel,
    webChatChannelData);
```

### 5. 取得 Bot 並列出 Channel

```csharp
// 取得 bot
BotResource bot = await botCollection.GetAsync("myBotName");
Console.WriteLine($"Bot: {bot.Data.Properties.DisplayName}");
Console.WriteLine($"Endpoint: {bot.Data.Properties.Endpoint}");

// 列出 channel
await foreach (BotChannelResource channel in bot.GetBotChannels().GetAllAsync())
{
    Console.WriteLine($"Channel: {channel.Data.Name}");
}
```

### 6. 重新產生 DirectLine Key

```csharp
var regenerateRequest = new BotChannelRegenerateKeysContent(BotChannelName.DirectLineChannel)
{
    SiteName = "Default Site"
};

BotChannelResource channelWithKeys = await bot.GetBotChannelWithRegenerateKeysAsync(regenerateRequest);
```

### 7. 更新 Bot

```csharp
BotResource bot = await botCollection.GetAsync("myBotName");

// 用 patch 更新
var updateData = new BotData(bot.Data.Location)
{
    Properties = new BotProperties(
        displayName: "Updated Bot Name",
        endpoint: bot.Data.Properties.Endpoint,
        msaAppId: bot.Data.Properties.MsaAppId)
    {
        Description = "Updated description"
    }
};

await bot.UpdateAsync(updateData);
```

### 8. 刪除 Bot

```csharp
BotResource bot = await botCollection.GetAsync("myBotName");
await bot.DeleteAsync(WaitUntil.Completed);
```

## 支援的 Channel 類型

| Channel | 常數 | Class |
|---------|----------|-------|
| Direct Line | `BotChannelName.DirectLineChannel` | `DirectLineChannel` |
| Direct Line Speech | `BotChannelName.DirectLineSpeechChannel` | `DirectLineSpeechChannel` |
| Microsoft Teams | `BotChannelName.MsTeamsChannel` | `MsTeamsChannel` |
| Web Chat | `BotChannelName.WebChatChannel` | `WebChatChannel` |
| Slack | `BotChannelName.SlackChannel` | `SlackChannel` |
| Facebook | `BotChannelName.FacebookChannel` | `FacebookChannel` |
| Email | `BotChannelName.EmailChannel` | `EmailChannel` |
| Telegram | `BotChannelName.TelegramChannel` | `TelegramChannel` |
| Telephony | `BotChannelName.TelephonyChannel` | `TelephonyChannel` |

## 主要型別參考

| 型別 | 用途 |
|------|---------|
| `ArmClient` | 所有 ARM 操作的進入點 |
| `BotResource` | 代表一個 Azure Bot 資源 |
| `BotCollection` | Bot CRUD 用的集合 |
| `BotData` | Bot 資源定義 |
| `BotProperties` | Bot 設定屬性 |
| `BotChannelResource` | Channel 設定 |
| `BotChannelCollection` | Channel 的集合 |
| `BotChannelData` | Channel 設定資料 |
| `BotConnectionSettingResource` | OAuth 連線設定 |

## BotServiceKind 值

| 值 | 說明 |
|-------|-------------|
| `BotServiceKind.Azurebot` | Azure Bot（建議） |
| `BotServiceKind.Bot` | 舊版 Bot Framework bot |
| `BotServiceKind.Designer` | Composer bot |
| `BotServiceKind.Function` | Function bot |
| `BotServiceKind.Sdk` | SDK bot |

## BotServiceSkuName 值

| 值 | 說明 |
|-------|-------------|
| `BotServiceSkuName.F0` | 免費層 |
| `BotServiceSkuName.S1` | 標準層 |

## BotMsaAppType 值

| 值 | 說明 |
|-------|-------------|
| `BotMsaAppType.MultiTenant` | 多租戶應用程式 |
| `BotMsaAppType.SingleTenant` | 單租戶應用程式 |
| `BotMsaAppType.UserAssignedMSI` | 使用者指派的 managed identity |

## 最佳實務

1. **用 `DefaultAzureCredential`**：支援多種認證方式
2. 同步操作用 **`WaitUntil.Completed`**
3. API 錯誤要處理 **`RequestFailedException`**
4. 所有操作都用 **async 方法**（`*Async`）
5. **安全地儲存 MSA App 憑證**：機密用 Key Vault
6. 正式環境的 bot 用 **managed identity**（`BotMsaAppType.UserAssignedMSI`）
7. 正式環境的 DirectLine channel 要**啟用 secure site**

## 錯誤處理

```csharp
using Azure;

try
{
    var operation = await botCollection.CreateOrUpdateAsync(
        WaitUntil.Completed, 
        botName, 
        botData);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("Bot already exists");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"ARM Error: {ex.Status} - {ex.ErrorCode}: {ex.Message}");
}
```

## 相關 SDK

| SDK | 用途 | 安裝 |
|-----|---------|---------|
| `Azure.ResourceManager.BotService` | Bot 管理（就是這個 SDK） | `dotnet add package Azure.ResourceManager.BotService` |
| `Microsoft.Bot.Builder` | Bot Framework SDK | `dotnet add package Microsoft.Bot.Builder` |
| `Microsoft.Bot.Builder.Integration.AspNet.Core` | ASP.NET Core 整合 | `dotnet add package Microsoft.Bot.Builder.Integration.AspNet.Core` |

## 參考連結

| 資源 | URL |
|----------|-----|
| NuGet 套件 | https://www.nuget.org/packages/Azure.ResourceManager.BotService |
| API 參考 | https://learn.microsoft.com/dotnet/api/azure.resourcemanager.botservice |
| GitHub 原始碼 | https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/botservice/Azure.ResourceManager.BotService |
| Azure Bot Service 文件 | https://learn.microsoft.com/azure/bot-service/ |
