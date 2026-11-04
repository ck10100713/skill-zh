---
name: microsoft-azure-webjobs-extensions-authentication-events-dotnet
description: 'Microsoft Entra Authentication Events SDK for .NET。用於自訂驗證擴充功能的 Azure Functions trigger。適用於 Entra ID 中的 token 加料、自訂 claim、屬性蒐集和 OTP 自訂。Triggers: "Authentication Events", "WebJobsAuthenticationEventsTrigger", "OnTokenIssuanceStart", "OnAttributeCollectionStart", "custom claims", "token enrichment", "Entra custom extension", "authentication extension".'
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents (.NET)

用來處理 Microsoft Entra ID 自訂驗證事件的 Azure Functions 擴充功能。

## 安裝

```bash
dotnet add package Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents
```

**目前版本**：v1.1.0（穩定版）

## 支援的事件

| 事件 | 用途 |
|-------|---------|
| `OnTokenIssuanceStart` | 在發行 token 時加入自訂 claim |
| `OnAttributeCollectionStart` | 在顯示之前自訂屬性蒐集的 UI |
| `OnAttributeCollectionSubmit` | 使用者送出後驗證/修改屬性 |
| `OnOtpSend` | 自訂 OTP 傳送方式（SMS、email 等） |

## 核心流程

### 1. Token 加料（加入自訂 Claim）

在登入時，把自訂 claim 加進 access token 或 ID token。

```csharp
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents;
using Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents.TokenIssuanceStart;
using Microsoft.Extensions.Logging;

public static class TokenEnrichmentFunction
{
    [FunctionName("OnTokenIssuanceStart")]
    public static WebJobsAuthenticationEventResponse Run(
        [WebJobsAuthenticationEventsTrigger] WebJobsTokenIssuanceStartRequest request,
        ILogger log)
    {
        log.LogInformation("Token issuance event for user: {UserId}", 
            request.Data?.AuthenticationContext?.User?.Id);

        // Create response with custom claims
        var response = new WebJobsTokenIssuanceStartResponse();
        
        // Add claims to the token
        response.Actions.Add(new WebJobsProvideClaimsForToken
        {
            Claims = new Dictionary<string, string>
            {
                { "customClaim1", "customValue1" },
                { "department", "Engineering" },
                { "costCenter", "CC-12345" },
                { "apiVersion", "v2" }
            }
        });

        return response;
    }
}
```

### 2. 用外部資料做 Token 加料

從外部系統（資料庫、API）取得 claim。

```csharp
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents;
using Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents.TokenIssuanceStart;
using Microsoft.Extensions.Logging;
using System.Net.Http;
using System.Text.Json;

public static class TokenEnrichmentWithExternalData
{
    private static readonly HttpClient _httpClient = new();

    [FunctionName("OnTokenIssuanceStartExternal")]
    public static async Task<WebJobsAuthenticationEventResponse> Run(
        [WebJobsAuthenticationEventsTrigger] WebJobsTokenIssuanceStartRequest request,
        ILogger log)
    {
        string? userId = request.Data?.AuthenticationContext?.User?.Id;
        
        if (string.IsNullOrEmpty(userId))
        {
            log.LogWarning("No user ID in request");
            return new WebJobsTokenIssuanceStartResponse();
        }

        // Fetch user data from external API
        var userProfile = await GetUserProfileAsync(userId);
        
        var response = new WebJobsTokenIssuanceStartResponse();
        response.Actions.Add(new WebJobsProvideClaimsForToken
        {
            Claims = new Dictionary<string, string>
            {
                { "employeeId", userProfile.EmployeeId },
                { "department", userProfile.Department },
                { "roles", string.Join(",", userProfile.Roles) }
            }
        });

        return response;
    }

    private static async Task<UserProfile> GetUserProfileAsync(string userId)
    {
        var response = await _httpClient.GetAsync($"https://api.example.com/users/{userId}");
        response.EnsureSuccessStatusCode();
        var json = await response.Content.ReadAsStringAsync();
        return JsonSerializer.Deserialize<UserProfile>(json)!;
    }
}

public record UserProfile(string EmployeeId, string Department, string[] Roles);
```

### 3. 屬性蒐集：自訂 UI（Start 事件）

在屬性蒐集頁面顯示之前自訂它。

```csharp
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents;
using Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents.Framework;
using Microsoft.Extensions.Logging;

public static class AttributeCollectionStartFunction
{
    [FunctionName("OnAttributeCollectionStart")]
    public static WebJobsAuthenticationEventResponse Run(
        [WebJobsAuthenticationEventsTrigger] WebJobsAttributeCollectionStartRequest request,
        ILogger log)
    {
        log.LogInformation("Attribute collection start for correlation: {CorrelationId}",
            request.Data?.AuthenticationContext?.CorrelationId);

        var response = new WebJobsAttributeCollectionStartResponse();

        // Option 1: Continue with default behavior
        response.Actions.Add(new WebJobsContinueWithDefaultBehavior());

        // Option 2: Prefill attributes
        // response.Actions.Add(new WebJobsSetPrefillValues
        // {
        //     Attributes = new Dictionary<string, string>
        //     {
        //         { "city", "Seattle" },
        //         { "country", "USA" }
        //     }
        // });

        // Option 3: Show blocking page (prevent sign-up)
        // response.Actions.Add(new WebJobsShowBlockPage
        // {
        //     Message = "Sign-up is currently disabled."
        // });

        return response;
    }
}
```

### 4. 屬性蒐集：驗證送出內容（Submit 事件）

在使用者送出後，驗證並修改屬性。

```csharp
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents;
using Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents.Framework;
using Microsoft.Extensions.Logging;

public static class AttributeCollectionSubmitFunction
{
    [FunctionName("OnAttributeCollectionSubmit")]
    public static WebJobsAuthenticationEventResponse Run(
        [WebJobsAuthenticationEventsTrigger] WebJobsAttributeCollectionSubmitRequest request,
        ILogger log)
    {
        var response = new WebJobsAttributeCollectionSubmitResponse();

        // Access submitted attributes
        var attributes = request.Data?.UserSignUpInfo?.Attributes;
        
        string? email = attributes?["email"]?.ToString();
        string? displayName = attributes?["displayName"]?.ToString();

        // Validation example: block certain email domains
        if (email?.EndsWith("@blocked.com") == true)
        {
            response.Actions.Add(new WebJobsShowBlockPage
            {
                Message = "Sign-up from this email domain is not allowed."
            });
            return response;
        }

        // Validation example: show validation error
        if (string.IsNullOrEmpty(displayName) || displayName.Length < 3)
        {
            response.Actions.Add(new WebJobsShowValidationError
            {
                Message = "Display name must be at least 3 characters.",
                AttributeErrors = new Dictionary<string, string>
                {
                    { "displayName", "Name is too short" }
                }
            });
            return response;
        }

        // Modify attributes before saving
        response.Actions.Add(new WebJobsModifyAttributeValues
        {
            Attributes = new Dictionary<string, string>
            {
                { "displayName", displayName.Trim() },
                { "city", attributes?["city"]?.ToString()?.ToUpperInvariant() ?? "" }
            }
        });

        return response;
    }
}
```

### 5. 自訂 OTP 傳送

透過自訂管道（SMS、email、推播通知）傳送一次性密碼。

```csharp
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents;
using Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents.Framework;
using Microsoft.Extensions.Logging;

public static class CustomOtpFunction
{
    [FunctionName("OnOtpSend")]
    public static async Task<WebJobsAuthenticationEventResponse> Run(
        [WebJobsAuthenticationEventsTrigger] WebJobsOnOtpSendRequest request,
        ILogger log)
    {
        var response = new WebJobsOnOtpSendResponse();

        string? phoneNumber = request.Data?.OtpContext?.Identifier;
        string? otp = request.Data?.OtpContext?.OneTimeCode;

        if (string.IsNullOrEmpty(phoneNumber) || string.IsNullOrEmpty(otp))
        {
            log.LogError("Missing phone number or OTP");
            response.Actions.Add(new WebJobsOnOtpSendFailed
            {
                Error = "Missing required data"
            });
            return response;
        }

        try
        {
            // Send OTP via your SMS provider
            await SendSmsAsync(phoneNumber, $"Your verification code is: {otp}");
            
            response.Actions.Add(new WebJobsOnOtpSendSuccess());
            log.LogInformation("OTP sent successfully to {PhoneNumber}", phoneNumber);
        }
        catch (Exception ex)
        {
            log.LogError(ex, "Failed to send OTP");
            response.Actions.Add(new WebJobsOnOtpSendFailed
            {
                Error = "Failed to send verification code"
            });
        }

        return response;
    }

    private static async Task SendSmsAsync(string phoneNumber, string message)
    {
        // Implement your SMS provider integration (Twilio, Azure Communication Services, etc.)
        await Task.CompletedTask;
    }
}
```

### 6. Function App 設定

為驗證事件設定 Function App。

```csharp
// Program.cs (Isolated worker model)
using Microsoft.Extensions.Hosting;

var host = new HostBuilder()
    .ConfigureFunctionsWorkerDefaults()
    .Build();

host.Run();
```

```json
// host.json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true
      }
    }
  },
  "extensions": {
    "http": {
      "routePrefix": ""
    }
  }
}
```

```json
// local.settings.json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "dotnet"
  }
}
```

## 關鍵型別參考

| 型別 | 用途 |
|------|---------|
| `WebJobsAuthenticationEventsTriggerAttribute` | Function 的 trigger attribute |
| `WebJobsTokenIssuanceStartRequest` | Token 發行事件的 request |
| `WebJobsTokenIssuanceStartResponse` | Token 發行事件的 response |
| `WebJobsProvideClaimsForToken` | 加入 claim 的動作 |
| `WebJobsAttributeCollectionStartRequest` | 屬性蒐集開始的 request |
| `WebJobsAttributeCollectionStartResponse` | 屬性蒐集開始的 response |
| `WebJobsAttributeCollectionSubmitRequest` | 屬性送出的 request |
| `WebJobsAttributeCollectionSubmitResponse` | 屬性送出的 response |
| `WebJobsSetPrefillValues` | 預先填入表單的值 |
| `WebJobsShowBlockPage` | 用訊息擋住使用者 |
| `WebJobsShowValidationError` | 顯示驗證錯誤 |
| `WebJobsModifyAttributeValues` | 修改送出的值 |
| `WebJobsOnOtpSendRequest` | OTP 傳送事件的 request |
| `WebJobsOnOtpSendResponse` | OTP 傳送事件的 response |
| `WebJobsOnOtpSendSuccess` | OTP 傳送成功 |
| `WebJobsOnOtpSendFailed` | OTP 傳送失敗 |
| `WebJobsContinueWithDefaultBehavior` | 繼續預設流程 |

## Entra ID 設定

Deploy 你的 Function App 之後，在 Entra ID 設定自訂擴充功能：

1. 在 Entra ID → App registrations **註冊 API**
2. 在 Entra ID → External Identities → Custom authentication extensions **建立自訂驗證擴充功能**
3. 在 Entra ID → External Identities → User flows **連結到 User Flow**

### 必要的 App Registration 設定

```
Expose an API:
  - Application ID URI: api://<your-function-app-name>.azurewebsites.net
  - Scope: CustomAuthenticationExtension.Receive.Payload

API Permissions:
  - Microsoft Graph: User.Read (delegated)
```

## 最佳實務

1. **驗證所有輸入**：絕對不要信任 request 資料；處理之前先驗證
2. **優雅地處理錯誤**：回傳適當的錯誤回應
3. **記錄 correlation ID**：用 `CorrelationId` 做疑難排解
4. **讓 function 保持快速**：驗證事件有 timeout 限制
5. **使用 managed identity**：安全地存取 Azure 資源
6. **快取外部資料**：避免每個 request 都做緩慢的查詢
7. **在本機測試**：用 Azure Functions Core Tools 搭配範例 payload
8. **用 App Insights 監控**：追蹤 function 的執行和錯誤

## 錯誤處理

```csharp
[FunctionName("OnTokenIssuanceStart")]
public static WebJobsAuthenticationEventResponse Run(
    [WebJobsAuthenticationEventsTrigger] WebJobsTokenIssuanceStartRequest request,
    ILogger log)
{
    try
    {
        // Your logic here
        var response = new WebJobsTokenIssuanceStartResponse();
        response.Actions.Add(new WebJobsProvideClaimsForToken
        {
            Claims = new Dictionary<string, string> { { "claim", "value" } }
        });
        return response;
    }
    catch (Exception ex)
    {
        log.LogError(ex, "Error processing token issuance event");
        
        // Return empty response - authentication continues without custom claims
        // Do NOT throw - this would fail the authentication
        return new WebJobsTokenIssuanceStartResponse();
    }
}
```

## 相關 SDK

| SDK | 用途 | 安裝 |
|-----|---------|---------|
| `Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents` | 驗證事件（本 SDK） | `dotnet add package Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents` |
| `Microsoft.Identity.Web` | Web 應用程式驗證 | `dotnet add package Microsoft.Identity.Web` |
| `Azure.Identity` | Azure 驗證 | `dotnet add package Azure.Identity` |

## 參考連結

| 資源 | URL |
|----------|-----|
| NuGet 套件 | https://www.nuget.org/packages/Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents |
| 自訂擴充功能概觀 | https://learn.microsoft.com/entra/identity-platform/custom-extension-overview |
| Token 發行事件 | https://learn.microsoft.com/entra/identity-platform/custom-extension-tokenissuancestart-setup |
| 屬性蒐集事件 | https://learn.microsoft.com/entra/identity-platform/custom-extension-attribute-collection |
| GitHub 原始碼 | https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/entra/Microsoft.Azure.WebJobs.Extensions.AuthenticationEvents |
