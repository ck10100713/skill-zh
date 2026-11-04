---
name: m365-agents-dotnet
description: |
  Microsoft 365 Agents SDK for .NET。用 ASP.NET Core hosting、AgentApplication 路由和 MSAL 驗證，建立給 Teams/M365/Copilot Studio 用的多通路 agent。Triggers: "Microsoft 365 Agents SDK", "Microsoft.Agents", "AddAgentApplicationOptions", "AgentApplication", "AddAgentAspNetAuthentication", "Copilot Studio client", "IAgentHttpAdapter".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Microsoft.Agents.Hosting.AspNetCore, Microsoft.Agents.Authentication.Msal, Microsoft.Agents.CopilotStudio.Client
---

# Microsoft 365 Agents SDK (.NET)

## Overview

用 Microsoft.Agents SDK 搭配 ASP.NET Core hosting、agent 路由和 MSAL 驗證，為 Microsoft 365、Teams 和 Copilot Studio 建立企業級 agent。

## Before implementation

- 用 microsoft-docs MCP 驗證 AddAgent、AgentApplication 和驗證選項的最新 API。
- 到 NuGet 確認你打算使用的 Microsoft.Agents.\* 套件的版本。

## Installation

```bash
dotnet add package Microsoft.Agents.Hosting.AspNetCore
dotnet add package Microsoft.Agents.Authentication.Msal
dotnet add package Microsoft.Agents.Storage
dotnet add package Microsoft.Agents.CopilotStudio.Client
dotnet add package Microsoft.Identity.Client.Extensions.Msal
```

## Configuration (appsettings.json)

```json
{
  "TokenValidation": {
    "Enabled": true,
    "Audiences": ["{{ClientId}}"],
    "TenantId": "{{TenantId}}"
  },
  "AgentApplication": {
    "StartTypingTimer": false,
    "RemoveRecipientMention": false,
    "NormalizeMentions": false
  },
  "Connections": {
    "ServiceConnection": {
      "Settings": {
        "AuthType": "ClientSecret",
        "ClientId": "{{ClientId}}",
        "ClientSecret": "{{ClientSecret}}",
        "AuthorityEndpoint": "https://login.microsoftonline.com/{{TenantId}}",
        "Scopes": ["https://api.botframework.com/.default"]
      }
    }
  },
  "ConnectionsMap": [
    {
      "ServiceUrl": "*",
      "Connection": "ServiceConnection"
    }
  ],
  "CopilotStudioClientSettings": {
    "DirectConnectUrl": "",
    "EnvironmentId": "",
    "SchemaName": "",
    "TenantId": "",
    "AppClientId": "",
    "AppClientSecret": ""
  }
}
```

## Core Workflow: ASP.NET Core agent host

```csharp
using Microsoft.Agents.Builder;
using Microsoft.Agents.Hosting.AspNetCore;
using Microsoft.Agents.Storage;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddHttpClient();
builder.AddAgentApplicationOptions();
builder.AddAgent<MyAgent>();
builder.Services.AddSingleton<IStorage, MemoryStorage>();

builder.Services.AddControllers();
builder.Services.AddAgentAspNetAuthentication(builder.Configuration);

WebApplication app = builder.Build();

app.UseAuthentication();
app.UseAuthorization();

app.MapGet("/", () => "Microsoft Agents SDK Sample");

var incomingRoute = app.MapPost("/api/messages",
    async (HttpRequest request, HttpResponse response, IAgentHttpAdapter adapter, IAgent agent, CancellationToken ct) =>
    {
        await adapter.ProcessAsync(request, response, agent, ct);
    });

if (!app.Environment.IsDevelopment())
{
    incomingRoute.RequireAuthorization();
}
else
{
    app.Urls.Add("http://localhost:3978");
}

app.Run();
```

## AgentApplication routing

```csharp
using Microsoft.Agents.Builder;
using Microsoft.Agents.Builder.App;
using Microsoft.Agents.Builder.State;
using Microsoft.Agents.Core.Models;
using System;
using System.Threading;
using System.Threading.Tasks;

public sealed class MyAgent : AgentApplication
{
    public MyAgent(AgentApplicationOptions options) : base(options)
    {
        OnConversationUpdate(ConversationUpdateEvents.MembersAdded, WelcomeAsync);
        OnActivity(ActivityTypes.Message, OnMessageAsync, rank: RouteRank.Last);
        OnTurnError(OnTurnErrorAsync);
    }

    private static async Task WelcomeAsync(ITurnContext turnContext, ITurnState turnState, CancellationToken ct)
    {
        foreach (ChannelAccount member in turnContext.Activity.MembersAdded)
        {
            if (member.Id != turnContext.Activity.Recipient.Id)
            {
                await turnContext.SendActivityAsync(
                    MessageFactory.Text("Welcome to the agent."),
                    ct);
            }
        }
    }

    private static async Task OnMessageAsync(ITurnContext turnContext, ITurnState turnState, CancellationToken ct)
    {
        await turnContext.SendActivityAsync(
            MessageFactory.Text($"You said: {turnContext.Activity.Text}"),
            ct);
    }

    private static async Task OnTurnErrorAsync(
        ITurnContext turnContext,
        ITurnState turnState,
        Exception exception,
        CancellationToken ct)
    {
        await turnState.Conversation.DeleteStateAsync(turnContext, ct);

        var endOfConversation = Activity.CreateEndOfConversationActivity();
        endOfConversation.Code = EndOfConversationCodes.Error;
        endOfConversation.Text = exception.Message;
        await turnContext.SendActivityAsync(endOfConversation, ct);
    }
}
```

## Copilot Studio direct-to-engine client

### DelegatingHandler for token acquisition (interactive flow)

```csharp
using System.Net.Http.Headers;
using Microsoft.Agents.CopilotStudio.Client;
using Microsoft.Identity.Client;

internal sealed class AddTokenHandler : DelegatingHandler
{
    private readonly SampleConnectionSettings _settings;

    public AddTokenHandler(SampleConnectionSettings settings) : base(new HttpClientHandler())
    {
        _settings = settings;
    }

    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken cancellationToken)
    {
        if (request.Headers.Authorization is null)
        {
            string[] scopes = [CopilotClient.ScopeFromSettings(_settings)];

            IPublicClientApplication app = PublicClientApplicationBuilder
                .Create(_settings.AppClientId)
                .WithAuthority(AadAuthorityAudience.AzureAdMyOrg)
                .WithTenantId(_settings.TenantId)
                .WithRedirectUri("http://localhost")
                .Build();

            AuthenticationResult authResponse;
            try
            {
                var account = (await app.GetAccountsAsync()).FirstOrDefault();
                authResponse = await app.AcquireTokenSilent(scopes, account).ExecuteAsync(cancellationToken);
            }
            catch (MsalUiRequiredException)
            {
                authResponse = await app.AcquireTokenInteractive(scopes).ExecuteAsync(cancellationToken);
            }

            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", authResponse.AccessToken);
        }

        return await base.SendAsync(request, cancellationToken);
    }
}
```

### Console host with CopilotClient

```csharp
using Microsoft.Agents.CopilotStudio.Client;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

HostApplicationBuilder builder = Host.CreateApplicationBuilder(args);

var settings = new SampleConnectionSettings(
    builder.Configuration.GetSection("CopilotStudioClientSettings"));

builder.Services.AddHttpClient("mcs").ConfigurePrimaryHttpMessageHandler(() =>
{
    return new AddTokenHandler(settings);
});

builder.Services
    .AddSingleton(settings)
    .AddTransient<CopilotClient>(sp =>
    {
        var logger = sp.GetRequiredService<ILoggerFactory>().CreateLogger<CopilotClient>();
        return new CopilotClient(settings, sp.GetRequiredService<IHttpClientFactory>(), logger, "mcs");
    });

IHost host = builder.Build();
var client = host.Services.GetRequiredService<CopilotClient>();

await foreach (var activity in client.StartConversationAsync(emitStartConversationEvent: true))
{
    Console.WriteLine(activity.Type);
}

await foreach (var activity in client.AskQuestionAsync("Hello!", null))
{
    Console.WriteLine(activity.Type);
}
```

## Best Practices

1. 用 AgentApplication 的子類別集中處理路由和錯誤處理。
2. MemoryStorage 只在開發時用；正式環境用會持久化的儲存。
3. 正式環境要啟用 TokenValidation，並且對 /api/messages 要求授權。
4. 驗證用的 secret 放在 configuration provider（Key Vault、managed identity、環境變數）裡。
5. 重用 IHttpClientFactory 的 HttpClient，並快取 MSAL token。
6. 優先用非同步 handler，並把 CancellationToken 傳給 SDK 呼叫。

## Reference Links

| Resource                   | URL                                                                                                                                        |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Microsoft 365 Agents SDK   | https://learn.microsoft.com/en-us/microsoft-365/agents-sdk/                                                                                |
| AddAgent API               | https://learn.microsoft.com/en-us/dotnet/api/microsoft.agents.hosting.aspnetcore.servicecollectionextensions.addagent?view=m365-agents-sdk |
| AgentApplication API       | https://learn.microsoft.com/en-us/dotnet/api/microsoft.agents.builder.app.agentapplication?view=m365-agents-sdk                            |
| Auth configuration options | https://learn.microsoft.com/en-us/microsoft-365/agents-sdk/microsoft-authentication-library-configuration-options                          |
| Copilot Studio integration | https://learn.microsoft.com/en-us/microsoft-365/agents-sdk/integrate-with-mcs                                                              |
| GitHub samples             | https://github.com/microsoft/agents                                                                                                        |
