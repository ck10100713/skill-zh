---
name: azure-mgmt-weightsandbiases-dotnet
description: |
  .NET 版 Azure Weights & Biases SDK。透過 Azure Marketplace 做 ML 實驗追蹤與模型管理。用於建立 W&B instance、管理 SSO、Marketplace 整合與 ML 可觀測性。Triggers: "Weights and Biases", "W&B", "WeightsAndBiases", "ML experiment tracking", "model registry", "experiment management", "wandb".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.ResourceManager.WeightsAndBiases
---

# Azure.ResourceManager.WeightsAndBiases (.NET)

Azure Resource Manager SDK，用來透過 Azure Marketplace 部署與管理 Weights & Biases ML 實驗追蹤 instance。

## 安裝

```bash
dotnet add package Azure.ResourceManager.WeightsAndBiases --prerelease
dotnet add package Azure.Identity
```

**目前版本**：v1.0.0-beta.1（preview）  
**API 版本**：2024-09-18-preview

## 環境變數

```bash
AZURE_SUBSCRIPTION_ID=<your-subscription-id> # 必填：Azure subscription ID
AZURE_RESOURCE_GROUP=<your-resource-group> # 必填：Azure resource group 名稱
AZURE_WANDB_INSTANCE_NAME=<your-wandb-instance> # 必填：Weights & Biases instance 名稱
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境使用 DefaultAzureCredential 時才需要
```

## 驗證

```csharp
using Azure.Identity;
using Azure.ResourceManager;
using Azure.ResourceManager.WeightsAndBiases;

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
    └── WeightsAndBiasesInstance    # 來自 Azure Marketplace 的 W&B 部署
        ├── Properties
        │   ├── Marketplace          # Offer 詳細資料、plan、publisher
        │   ├── User                 # 管理員使用者資訊
        │   ├── PartnerProperties    # W&B 專屬設定（region、subdomain）
        │   └── SingleSignOnPropertiesV2  # Entra ID SSO 設定
        └── Identity                 # Managed identity（選用）
```

## 核心流程

### 1. 建立 Weights & Biases Instance

```csharp
using Azure.ResourceManager.WeightsAndBiases;
using Azure.ResourceManager.WeightsAndBiases.Models;

ResourceGroupResource resourceGroup = await client
    .GetDefaultSubscriptionAsync()
    .Result
    .GetResourceGroupAsync("my-resource-group");

WeightsAndBiasesInstanceCollection instances = resourceGroup.GetWeightsAndBiasesInstances();

WeightsAndBiasesInstanceData data = new WeightsAndBiasesInstanceData(AzureLocation.EastUS)
{
    Properties = new WeightsAndBiasesInstanceProperties
    {
        // Marketplace 設定
        Marketplace = new WeightsAndBiasesMarketplaceDetails
        {
            SubscriptionId = "<marketplace-subscription-id>",
            OfferDetails = new WeightsAndBiasesOfferDetails
            {
                PublisherId = "wandb",
                OfferId = "wandb-pay-as-you-go",
                PlanId = "wandb-payg",
                PlanName = "Pay As You Go",
                TermId = "monthly",
                TermUnit = "P1M"
            }
        },
        // 管理員使用者
        User = new WeightsAndBiasesUserDetails
        {
            FirstName = "Admin",
            LastName = "User",
            EmailAddress = "admin@example.com",
            Upn = "admin@example.com"
        },
        // W&B 專屬設定
        PartnerProperties = new WeightsAndBiasesPartnerProperties
        {
            Region = WeightsAndBiasesRegion.EastUS,
            Subdomain = "my-company-wandb"
        }
    },
    // 選用：啟用 managed identity
    Identity = new ManagedServiceIdentity(ManagedServiceIdentityType.SystemAssigned)
};

ArmOperation<WeightsAndBiasesInstanceResource> operation = await instances
    .CreateOrUpdateAsync(WaitUntil.Completed, "my-wandb-instance", data);

WeightsAndBiasesInstanceResource instance = operation.Value;

Console.WriteLine($"W&B Instance created: {instance.Data.Name}");
Console.WriteLine($"Provisioning state: {instance.Data.Properties.ProvisioningState}");
```

### 2. 取得既有 Instance

```csharp
WeightsAndBiasesInstanceResource instance = await resourceGroup
    .GetWeightsAndBiasesInstanceAsync("my-wandb-instance");

Console.WriteLine($"Instance: {instance.Data.Name}");
Console.WriteLine($"Location: {instance.Data.Location}");
Console.WriteLine($"State: {instance.Data.Properties.ProvisioningState}");

if (instance.Data.Properties.PartnerProperties != null)
{
    Console.WriteLine($"Region: {instance.Data.Properties.PartnerProperties.Region}");
    Console.WriteLine($"Subdomain: {instance.Data.Properties.PartnerProperties.Subdomain}");
}
```

### 3. 列出所有 Instance

```csharp
// 列出 resource group 內的
await foreach (WeightsAndBiasesInstanceResource instance in 
    resourceGroup.GetWeightsAndBiasesInstances())
{
    Console.WriteLine($"Instance: {instance.Data.Name}");
    Console.WriteLine($"  Location: {instance.Data.Location}");
    Console.WriteLine($"  State: {instance.Data.Properties.ProvisioningState}");
}

// 列出 subscription 內的
SubscriptionResource subscription = await client.GetDefaultSubscriptionAsync();
await foreach (WeightsAndBiasesInstanceResource instance in 
    subscription.GetWeightsAndBiasesInstancesAsync())
{
    Console.WriteLine($"{instance.Data.Name} in {instance.Id.ResourceGroupName}");
}
```

### 4. 設定單一登入（SSO）

```csharp
WeightsAndBiasesInstanceResource instance = await resourceGroup
    .GetWeightsAndBiasesInstanceAsync("my-wandb-instance");

// 用 SSO 設定更新
WeightsAndBiasesInstanceData updateData = instance.Data;

updateData.Properties.SingleSignOnPropertiesV2 = new WeightsAndBiasSingleSignOnPropertiesV2
{
    Type = WeightsAndBiasSingleSignOnType.Saml,
    State = WeightsAndBiasSingleSignOnState.Enable,
    EnterpriseAppId = "<entra-app-id>",
    AadDomains = { "example.com", "contoso.com" }
};

ArmOperation<WeightsAndBiasesInstanceResource> operation = await resourceGroup
    .GetWeightsAndBiasesInstances()
    .CreateOrUpdateAsync(WaitUntil.Completed, "my-wandb-instance", updateData);
```

### 5. 更新 Instance

```csharp
WeightsAndBiasesInstanceResource instance = await resourceGroup
    .GetWeightsAndBiasesInstanceAsync("my-wandb-instance");

// 更新 tags
WeightsAndBiasesInstancePatch patch = new WeightsAndBiasesInstancePatch
{
    Tags =
    {
        { "environment", "production" },
        { "team", "ml-platform" },
        { "costCenter", "CC-ML-001" }
    }
};

instance = await instance.UpdateAsync(patch);
Console.WriteLine($"Updated instance: {instance.Data.Name}");
```

### 6. 刪除 Instance

```csharp
WeightsAndBiasesInstanceResource instance = await resourceGroup
    .GetWeightsAndBiasesInstanceAsync("my-wandb-instance");

await instance.DeleteAsync(WaitUntil.Completed);
Console.WriteLine("Instance deleted");
```

### 7. 檢查資源名稱是否可用

```csharp
// 建立前先檢查名稱是否可用
// （如果 SDK 沒有提供，就直接呼叫 ARM）
try
{
    await resourceGroup.GetWeightsAndBiasesInstanceAsync("desired-name");
    Console.WriteLine("Name is already taken");
}
catch (RequestFailedException ex) when (ex.Status == 404)
{
    Console.WriteLine("Name is available");
}
```

## 主要型別參考

| 型別 | 用途 |
|------|---------|
| `WeightsAndBiasesInstanceResource` | W&B instance 資源 |
| `WeightsAndBiasesInstanceData` | Instance 設定資料 |
| `WeightsAndBiasesInstanceCollection` | Instance 集合 |
| `WeightsAndBiasesInstanceProperties` | Instance 屬性 |
| `WeightsAndBiasesMarketplaceDetails` | Marketplace 訂閱資訊 |
| `WeightsAndBiasesOfferDetails` | Marketplace offer 詳細資料 |
| `WeightsAndBiasesUserDetails` | 管理員使用者資訊 |
| `WeightsAndBiasesPartnerProperties` | W&B 專屬設定 |
| `WeightsAndBiasSingleSignOnPropertiesV2` | SSO 設定 |
| `WeightsAndBiasesInstancePatch` | 更新用的 patch |
| `WeightsAndBiasesRegion` | 支援的 region enum |

## 可用的 Region

| Region Enum | Azure Region |
|-------------|--------------|
| `WeightsAndBiasesRegion.EastUS` | 美國東部 |
| `WeightsAndBiasesRegion.CentralUS` | 美國中部 |
| `WeightsAndBiasesRegion.WestUS` | 美國西部 |
| `WeightsAndBiasesRegion.WestEurope` | 西歐 |
| `WeightsAndBiasesRegion.JapanEast` | 日本東部 |
| `WeightsAndBiasesRegion.KoreaCentral` | 韓國中部 |

## Marketplace Offer 詳細資料

整合 Azure Marketplace 時：

| 屬性 | 值 |
|----------|-------|
| Publisher ID | `wandb` |
| Offer ID | `wandb-pay-as-you-go` |
| Plan ID | `wandb-payg`（Pay As You Go） |

## 最佳實務

1. **使用 DefaultAzureCredential**：自動支援多種驗證方式
2. **啟用 managed identity**：安全存取其他 Azure 資源
3. **設定 SSO**：啟用 Entra ID SSO，提升企業安全
4. **替資源加 tag**：用 tag 追蹤成本、方便整理
5. **檢查 provisioning state**：等到 `Succeeded` 再使用 instance
6. **選對 region**：選離你的運算資源最近的 region
7. **用 Azure 監控**：用 Azure Monitor 看資源健康狀態

## 錯誤處理

```csharp
using Azure;

try
{
    ArmOperation<WeightsAndBiasesInstanceResource> operation = await instances
        .CreateOrUpdateAsync(WaitUntil.Completed, "my-wandb", data);
}
catch (RequestFailedException ex) when (ex.Status == 409)
{
    Console.WriteLine("Instance already exists or name conflict");
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

## 與 W&B SDK 整合

建立好 Azure 資源後，用 W&B Python SDK 做實驗追蹤：

```python
# 安裝：pip install wandb
import wandb

# 用部署在 Azure 上的 instance 的 W&B API key 登入
wandb.login(host="https://my-company-wandb.wandb.ai")

# 初始化一次 run
run = wandb.init(project="my-ml-project")

# 記錄指標
wandb.log({"accuracy": 0.95, "loss": 0.05})

# 結束 run
run.finish()
```

## 相關 SDK

| SDK | 用途 | 安裝 |
|-----|---------|---------|
| `Azure.ResourceManager.WeightsAndBiases` | W&B instance 管理（本 SDK） | `dotnet add package Azure.ResourceManager.WeightsAndBiases --prerelease` |
| `Azure.ResourceManager.MachineLearning` | Azure ML workspace | `dotnet add package Azure.ResourceManager.MachineLearning` |

## 參考連結

| 資源 | URL |
|----------|-----|
| NuGet 套件 | https://www.nuget.org/packages/Azure.ResourceManager.WeightsAndBiases |
| W&B 文件 | https://docs.wandb.ai/ |
| Azure Marketplace | https://azuremarketplace.microsoft.com/marketplace/apps/wandb.wandb-pay-as-you-go |
| GitHub 原始碼 | https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/weightsandbiases |
