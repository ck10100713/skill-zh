---
name: appinsights-instrumentation
description: "提供用 Azure Application Insights 為 web app 埋點的指引，包含 telemetry 模式、SDK 設定和設定參考。WHEN: how to instrument app, App Insights SDK, telemetry patterns, what is App Insights, Application Insights guidance, instrumentation examples, APM best practices。"
license: MIT
metadata:
  author: Microsoft
  version: "1.2.2"
---

# AppInsights 埋點指南

這個 skill 提供用 Azure Application Insights 為 web app 埋點的**指引和參考資料**。

> **⛔ 要新增元件嗎？**
>
> 如果使用者想**把 App Insights 加進他們的 app**，改呼叫 **azure-prepare**。
> 這個 skill 只提供參考資料，實際的修改由 azure-prepare 統籌。

## 何時使用這個 Skill

- 使用者問**怎麼**埋點（指引、模式、範例）
- 使用者需要 SDK 的設定說明
- azure-prepare 在研究階段呼叫這個 skill
- 使用者想了解 App Insights 的概念

## 何時改用 azure-prepare

- 使用者說「add telemetry to my app」
- 使用者說「add App Insights」
- 使用者想修改他們的專案
- 任何要變更／新增元件的請求

## 前置條件

workspace 裡的 app 必須是以下其中一種

- 託管在 Azure 上的 ASP.NET Core app
- Azure Container App
- 託管在 Azure 上的 Node.js app
- 託管在 Azure 上的 Python app

## 準則

### 蒐集背景資訊

先弄清楚使用者想加 telemetry 支援的那個應用程式的（程式語言、應用程式框架、託管方式）組合，這會決定怎麼為它埋點。讀原始碼來做合理的推測，不確定的地方向使用者確認。一定要問使用者應用程式託管在哪裡（例如個人電腦、以程式碼形式放在 Azure App Service、以 container 形式放在 Azure App Service、Azure Container App 等）。

### 能自動埋點就優先自動埋點

如果 app 是託管在 Azure App Service 上的 C# ASP.NET Core app，就用 [AUTO guide](references/auto.md) 幫使用者自動埋點。

### 手動埋點

手動埋點的做法是建立 AppInsights 資源，再更新 app 的程式碼。

#### 建立 AppInsights 資源

從下列選項挑一個符合環境的來用。

- 把 AppInsights 加進既有的 Bicep template。要加什麼請看 [examples/appinsights.bicep](examples/appinsights.bicep)。如果 workspace 裡已經有 Bicep template 檔案，這是最好的選項。
- 用 Azure CLI。要執行哪個 Azure CLI 指令來建立 App Insights 資源，請看 [scripts/appinsights.ps1](scripts/appinsights.ps1)。

不管選哪個選項，都建議使用者把 App Insights 資源建在一個有意義的 resource group，這樣管理資源比較方便。很好的選擇是和託管 app 的 Azure 資源放在同一個 resource group。

#### 修改應用程式程式碼

- 如果 app 是 ASP.NET Core app，怎麼修改 C# 程式碼請看 [ASPNETCORE guide](references/aspnetcore.md)。
- 如果 app 是 Node.js app，怎麼修改 JavaScript／TypeScript 程式碼請看 [NODEJS guide](references/nodejs.md)。
- 如果 app 是 Python app，怎麼修改 Python 程式碼請看 [PYTHON guide](references/python.md)。

## SDK 速查

- **OpenTelemetry Distro**：[Python](references/sdk/azure-monitor-opentelemetry-py.md) | [TypeScript](references/sdk/azure-monitor-opentelemetry-ts.md)
- **OpenTelemetry Exporter**：[Python](references/sdk/azure-monitor-opentelemetry-exporter-py.md) | [Java](references/sdk/azure-monitor-opentelemetry-exporter-java.md)

## 各平台指南

- **Container Apps**：[Observability Guide](references/container-apps.md)
