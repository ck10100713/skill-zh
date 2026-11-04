---
name: applicationinsights-web-ts
description: 用 Application Insights JavaScript SDK（@microsoft/applicationinsights-web）為瀏覽器／web app 埋點。用於 Real User Monitoring（RUM）：page view、點擊、AJAX／fetch 相依呼叫、例外、自訂事件，以及和後端 OpenTelemetry trace 關聯的瀏覽器端 GenAI agent trace。涵蓋 SDK Loader Script 和 npm 設定、框架擴充套件（React、React Native、Angular）、Click Analytics、telemetry initializer，以及從瀏覽器送出 agent／tool／model span 的 OTel GenAI 語意慣例。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: "@microsoft/applicationinsights-web"
---

# Application Insights JavaScript SDK（Web）TypeScript 版

用 `@microsoft/applicationinsights-web` 為瀏覽器 app 做 Real User Monitoring（RUM）。自動蒐集 page view、AJAX／fetch 相依呼叫、未處理的例外，以及（搭配 Click Analytics plugin）點擊。支援自訂事件、metrics，以及遵循 OpenTelemetry GenAI 語意慣例、並透過 W3C Trace Context 和後端 span 關聯的 **GenAI agent trace**。

> **和 `azure-monitor-opentelemetry-ts` 不同**，後者是給 Node.js 伺服器 app 用的。這個 skill 是給**瀏覽器／web** 程式碼（以及 React Native）用的。

## 實作之前

先用 `microsoft-docs` MCP 搜尋目前的 API 用法：

- 查詢：「Application Insights JavaScript SDK setup」
- 查詢：「Application Insights JavaScript SDK configuration」
- 查詢：「Application Insights JavaScript framework extensions React Angular」
- 確認套件版本：`npm view @microsoft/applicationinsights-web version`

## 套件

| 套件 | 用途 |
| --- | --- |
| `@microsoft/applicationinsights-web` | 核心 RUM SDK（page view、AJAX、例外）。 |
| `@microsoft/applicationinsights-clickanalytics-js` | 自動蒐集點擊 telemetry。 |
| `@microsoft/applicationinsights-react-js` | React plugin（router 埋點、hook、HOC、ErrorBoundary）。 |
| `@microsoft/applicationinsights-react-native` | React Native plugin（原生 crash、session）。 |
| `@microsoft/applicationinsights-angularplugin-js` | Angular plugin（router 事件、ErrorHandler）。 |
| `@microsoft/applicationinsights-debugplugin-js` | 只在開發時用的 telemetry 檢視器。 |
| `@microsoft/applicationinsights-perfmarkmeasure-js` | User Timing（`performance.mark/measure`）整合。 |

## 安裝

```bash
npm i --save @microsoft/applicationinsights-web
# 選用的 plugin（只裝你會用到的）：
npm i --save @microsoft/applicationinsights-clickanalytics-js
npm i --save @microsoft/applicationinsights-react-js @microsoft/applicationinsights-react-native @microsoft/applicationinsights-angularplugin-js
```

型別定義隨套件一起提供，不用另外裝 `@types/...`。

## Connection String

瀏覽器 SDK 在初始化時需要 connection string。**它會以明文送到 client**，瀏覽器 telemetry 不支援 Microsoft Entra ID 驗證。如果需要把瀏覽器 RUM 和後端 telemetry 隔離，就另外用一個開啟 local auth 的 App Insights 資源給瀏覽器 RUM。

```bash
# Vite / CRA / Next.js：透過公開的 env 前綴暴露給 client
VITE_APPINSIGHTS_CONNECTION_STRING="InstrumentationKey=...;IngestionEndpoint=https://...;LiveEndpoint=https://..."
NEXT_PUBLIC_APPINSIGHTS_CONNECTION_STRING="InstrumentationKey=..."
```

## 快速開始（npm）

```typescript
import { ApplicationInsights } from "@microsoft/applicationinsights-web";

export const appInsights = new ApplicationInsights({
  config: {
    connectionString: import.meta.env.VITE_APPINSIGHTS_CONNECTION_STRING,
    enableAutoRouteTracking: true,        // SPA 路由變化 -> page view
    enableCorsCorrelation: true,          // 把 Request-Id / traceparent 傳給跨來源的 AJAX
    enableRequestHeaderTracking: true,
    enableResponseHeaderTracking: true,
    distributedTracingMode: 2,            // DistributedTracingModes.AI_AND_W3C ：送出 traceparent 以便和後端關聯
    autoTrackPageVisitTime: true,
    disableFetchTracking: false,          // fetch() 預設就會自動埋點
    excludeRequestFromAutoTrackingPatterns: [/livemetrics\.azure\.com/i]
  }
});

appInsights.loadAppInsights();
appInsights.trackPageView();
```

`loadAppInsights()` 只能呼叫一次，而且要盡早（在你想追蹤的使用者互動之前）。然後對初次載入呼叫 `trackPageView()`；當 `enableAutoRouteTracking` 開啟時，後續的路由變化會自動處理。

## 快速開始（SDK Loader Script）

想要自動更新的 SDK、又不想動 build pipeline 時推薦用這個。把它貼成 `<head>` 裡**第一個** `<script>`：

```html
<script type="text/javascript" src="https://js.monitor.azure.com/scripts/b/ai.3.gbl.min.js" crossorigin="anonymous"></script>
<script type="text/javascript">
  var appInsights = window.appInsights || function (cfg) {
    /* 參考：https://learn.microsoft.com/azure/azure-monitor/app/javascript-sdk
       請使用上面 Microsoft Learn 頁面的最新 snippet，它包含
       備援 CDN 的 failover（cr）、SDK 載入失敗回報，以及 queue shim，
       讓 SDK 就緒前的呼叫不會遺失。 */
  }({ src: "https://js.monitor.azure.com/scripts/b/ai.3.gbl.min.js",
      crossOrigin: "anonymous",
      cfg: { connectionString: "YOUR_CONNECTION_STRING" } });
</script>
```

只有 Loader 提供的 API（會排隊到 SDK 載入完成才執行）：`trackEvent`、`trackPageView`、`trackException`、`trackTrace`、`trackDependencyData`、`trackMetric`、`trackPageViewPerformance`、`startTrackPage`、`stopTrackPage`、`startTrackEvent`、`stopTrackEvent`、`addTelemetryInitializer`、`setAuthenticatedUserContext`、`clearAuthenticatedUserContext`、`flush`。

## 核心追蹤 API

```typescript
// Page view（關閉 enableAutoRouteTracking 的 SPA）
appInsights.trackPageView({ name: "Checkout", uri: "/checkout", properties: { cartSize: 3 } });

// 自訂事件（使用者操作、業務事件）
appInsights.trackEvent({ name: "PurchaseCompleted" }, { orderId: "ord_123", amountUsd: 49.95 });

// 例外（被捕捉的錯誤）
try {
  await pay(order);
} catch (err) {
  appInsights.trackException({ exception: err as Error, severityLevel: 3, properties: { orderId: order.id } });
}

// Trace（log，severity 0=Verbose、1=Info、2=Warning、3=Error、4=Critical）
appInsights.trackTrace({ message: "Cart hydrated from local storage", severityLevel: 1 });

// 自訂 metrics（數值）
appInsights.trackMetric({ name: "checkout.duration_ms", average: 1234 });

// 相依呼叫（手動追蹤的對外呼叫，fetch/XHR 是自動追蹤的）
appInsights.trackDependencyData({
  id: crypto.randomUUID(),
  name: "GET /api/orders",
  duration: 87, success: true, responseCode: 200,
  data: "https://api.example.com/api/orders", target: "api.example.com", type: "Fetch"
});

// 使用者身分（每個已驗證的 session 只設定一次，這些值是 PII，不要傳 email）
appInsights.setAuthenticatedUserContext("user-id-123", "tenant-456", /*storeInCookie*/ true);
appInsights.clearAuthenticatedUserContext(); // 登出時

// 離開頁面前強制送出
appInsights.flush();
```

## Telemetry Initializer（補充資料與過濾）

每個 envelope 在送出前都會跑一遍。回傳 `false` 就丟棄。

```typescript
import type { ITelemetryItem } from "@microsoft/applicationinsights-web";

appInsights.addTelemetryInitializer((item: ITelemetryItem) => {
  item.tags ??= {};
  item.tags["ai.cloud.role"] = "web-shop";
  item.tags["ai.cloud.roleInstance"] = window.location.hostname;
  item.data ??= {};
  item.data["app.version"] = import.meta.env.VITE_APP_VERSION;
  item.data["app.build"] = import.meta.env.VITE_BUILD_SHA;

  // 丟掉吵雜的 health check page view
  if (item.baseType === "PageviewData" && item.baseData?.uri?.endsWith("/healthz")) return false;

  // 清除 query string 裡的機密
  if (item.baseData?.uri) {
    item.baseData.uri = item.baseData.uri.replace(/([?&](token|sig|key)=)[^&]+/gi, "$1REDACTED");
  }
});
```

## Click Analytics

```typescript
import { ClickAnalyticsPlugin } from "@microsoft/applicationinsights-clickanalytics-js";

const clickPlugin = new ClickAnalyticsPlugin();
const appInsights = new ApplicationInsights({
  config: {
    connectionString: import.meta.env.VITE_APPINSIGHTS_CONNECTION_STRING,
    extensions: [clickPlugin],
    extensionConfig: {
      [clickPlugin.identifier]: {
        autoCapture: true,
        dataTags: { useDefaultContentNameOrId: true, customDataPrefix: "data-ai-" },
        urlCollectHash: false,
        behaviorValidator: (b: string) => /^[a-z0-9_]+$/.test(b) ? b : ""
      }
    }
  }
});
appInsights.loadAppInsights();
```

用 `data-ai-*` 屬性標記元素；點擊會以 Custom Event 送出，並帶上父層內容的 metadata。

## SPA 路由追蹤

- **內建：** 設定 `enableAutoRouteTracking: true`。它會 hook `history.pushState/replaceState` 和 `popstate`。
- **React Router：** 用 `@microsoft/applicationinsights-react-js` 的 `withAITracking` HOC（見 [references/framework-extensions.md](references/framework-extensions.md)）。
- **手動：** 在 router 的 `useEffect` 裡，路由變化時呼叫 `appInsights.trackPageView({ name, uri })`。要把 `enableAutoRouteTracking` 關掉，避免重複計算。

## 分散式追蹤（和後端關聯）

設定 `distributedTracingMode: 2`（`DistributedTracingModes.AI_AND_W3C`）。SDK 會在對外的 `fetch`／`XHR` 加上 `traceparent`（以及舊版的 `Request-Id`）。用 **OpenTelemetry** 埋點的後端（例如 `@azure/monitor-opentelemetry`）會自動連到瀏覽器的 operation_Id。

跨來源呼叫時，還要設定 `enableCorsCorrelation: true`，並把發出呼叫的 origin 加進 API 的 **CORS exposed headers**。

## GenAI Agent Trace（OTel 語意慣例）

當瀏覽器呼叫 AI agent（function-calling、tool-use、直接從 client 呼叫 model）時，送出 App Insights 的 **Dependency** telemetry，屬性要遵循 OpenTelemetry 的 **GenAI 語意慣例**，這樣才能在 App Insights／Log Analytics 和後端的 agent span 一起查詢。

**先設定 opt-in 環境變數**，讓後端的 instrumentation 都用同一個 schema 版本：

```bash
OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental
```

### 必填的屬性 key（原封不動使用 OTel 的名稱）

| Span / 操作 | 必填屬性 |
| --- | --- |
| `invoke_agent {agent.name}` | `gen_ai.operation.name=invoke_agent`, `gen_ai.provider.name`, `gen_ai.agent.name`, `gen_ai.agent.id` (when known) |
| `create_agent {agent.name}` | `gen_ai.operation.name=create_agent`, `gen_ai.provider.name`, `gen_ai.agent.name`, `gen_ai.request.model` |
| `chat {model}` | `gen_ai.operation.name=chat`, `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` |
| `execute_tool {tool.name}` | `gen_ai.operation.name=execute_tool`, `gen_ai.tool.name`, `gen_ai.tool.type` (`function` \| `extension` \| `datastore`), `gen_ai.tool.call.id` |

`gen_ai.provider.name` 的常見值：`openai`、`azure.ai.openai`、`azure.ai.inference`、`anthropic`、`aws.bedrock`、`gcp.gemini`、`gcp.vertex_ai`、`cohere`、`mistral_ai`、`groq`、`deepseek`、`perplexity`、`x_ai`、`ibm.watsonx.ai`。

> **敏感內容要 opt-in。** `gen_ai.system_instructions`、`gen_ai.input.messages`、`gen_ai.output.messages`、`gen_ai.tool.call.arguments`、`gen_ai.tool.call.result` 預設是 **Opt-In**。用執行期的 flag 控制它們，而且除非資料處理方式已獲核准，否則在正式環境不要使用。

### 模式：invoke_agent + 巢狀的 tool／model span

```typescript
import { ApplicationInsights, SeverityLevel } from "@microsoft/applicationinsights-web";

type GenAiAttrs = Record<string, string | number | boolean | undefined>;

function startGenAiSpan(name: string, attrs: GenAiAttrs) {
  const id = crypto.randomUUID();
  const start = performance.now();
  const baseProps: GenAiAttrs = { "gen_ai.span.id": id, ...attrs };
  return {
    end(success: boolean, extra: GenAiAttrs = {}, error?: Error) {
      const duration = Math.round(performance.now() - start);
      const properties = { ...baseProps, ...extra };
      appInsights.trackDependencyData({
        id, name, duration, success,
        responseCode: error ? 500 : 200,
        type: "GenAI",
        target: String(attrs["gen_ai.provider.name"] ?? "genai"),
        properties: properties as Record<string, string>
      });
      if (error) {
        appInsights.trackException({
          exception: error,
          severityLevel: SeverityLevel.Error,
          properties: { ...properties, "error.type": error.name } as Record<string, string>
        });
      }
    }
  };
}

// Agent 呼叫
const agentSpan = startGenAiSpan("invoke_agent ResearchAssistant", {
  "gen_ai.operation.name": "invoke_agent",
  "gen_ai.provider.name": "azure.ai.openai",
  "gen_ai.agent.name": "ResearchAssistant",
  "gen_ai.agent.id": "asst_5j66UpCpwteGg4YSxUnt7lPY",
  "gen_ai.request.model": "gpt-4o-mini",
  "server.address": "myresource.openai.azure.com"
});

try {
  // 巢狀的 chat completion span
  const chat = startGenAiSpan("chat gpt-4o-mini", {
    "gen_ai.operation.name": "chat",
    "gen_ai.provider.name": "azure.ai.openai",
    "gen_ai.request.model": "gpt-4o-mini"
  });
  const res = await callAzureOpenAi(/* ... */);
  chat.end(true, {
    "gen_ai.response.model": res.model,
    "gen_ai.response.id": res.id,
    "gen_ai.response.finish_reasons": JSON.stringify(res.choices.map(c => c.finish_reason)),
    "gen_ai.usage.input_tokens": res.usage.prompt_tokens,
    "gen_ai.usage.output_tokens": res.usage.completion_tokens,
    "gen_ai.output.type": "text"
  });

  // 巢狀的 tool 執行 span
  const tool = startGenAiSpan("execute_tool getWeather", {
    "gen_ai.operation.name": "execute_tool",
    "gen_ai.tool.name": "getWeather",
    "gen_ai.tool.type": "function",
    "gen_ai.tool.call.id": "call_abc123"
  });
  const toolResult = await runGetWeather({ location: "SF" });
  tool.end(true);

  agentSpan.end(true, {
    "gen_ai.usage.input_tokens": res.usage.prompt_tokens,
    "gen_ai.usage.output_tokens": res.usage.completion_tokens
  });
} catch (err) {
  agentSpan.end(false, { "error.type": (err as Error).name }, err as Error);
}
```

瀏覽器的 `traceparent` 會自動附在對外的 `fetch` 上（當 `distributedTracingMode: 2` 時），所以下游的 Azure OpenAI／agent 後端 span 會掛在 App Insights 裡同一個 operation_Id 底下。

完整的屬性參考、常見值和內容擷取指引，請看 [references/agent-traces.md](references/agent-traces.md)。

### KQL：在 App Insights 查詢 GenAI trace

```kusto
dependencies
| where type == "GenAI"
| extend op   = tostring(customDimensions["gen_ai.operation.name"]),
         agent = tostring(customDimensions["gen_ai.agent.name"]),
         model = tostring(customDimensions["gen_ai.request.model"]),
         tin   = toint(customDimensions["gen_ai.usage.input_tokens"]),
         tout  = toint(customDimensions["gen_ai.usage.output_tokens"])
| summarize calls=count(), p95_ms=percentile(duration, 95),
            avg_in=avg(tin), avg_out=avg(tout) by op, agent, model, bin(timestamp, 5m)
```

## React（TypeScript）

完整的 React、React Native、Angular、Next.js 和 Vite 做法，請看 [references/framework-extensions.md](references/framework-extensions.md)。

```typescript
import { ApplicationInsights } from "@microsoft/applicationinsights-web";
import { ReactPlugin, withAITracking } from "@microsoft/applicationinsights-react-js";
import { createBrowserHistory } from "history";

const reactPlugin = new ReactPlugin();
const browserHistory = createBrowserHistory();

export const appInsights = new ApplicationInsights({
  config: {
    connectionString: import.meta.env.VITE_APPINSIGHTS_CONNECTION_STRING,
    extensions: [reactPlugin],
    extensionConfig: { [reactPlugin.identifier]: { history: browserHistory } }
  }
});
appInsights.loadAppInsights();

export const TrackedCheckout = withAITracking(reactPlugin, Checkout, "Checkout");
```

## React Native

```typescript
import { ApplicationInsights } from "@microsoft/applicationinsights-web";
import { ReactNativePlugin } from "@microsoft/applicationinsights-react-native";

const rnPlugin = new ReactNativePlugin();
const appInsights = new ApplicationInsights({
  config: {
    connectionString: process.env.EXPO_PUBLIC_APPINSIGHTS_CONNECTION_STRING,
    extensions: [rnPlugin],
    disableFetchTracking: false
  }
});
appInsights.loadAppInsights();
```

## 效能：Web Vitals

自動蒐集：透過 `PerformanceTiming`／`PerformanceNavigationTiming` 取得的頁面載入時間。要加上 Core Web Vitals：

```typescript
import { onCLS, onLCP, onINP, type Metric } from "web-vitals";

function send(m: Metric) {
  appInsights.trackMetric(
    { name: `web_vitals.${m.name.toLowerCase()}`, average: m.value },
    { rating: m.rating, navigationType: m.navigationType, id: m.id }
  );
}
onCLS(send); onLCP(send); onINP(send);
```

## Cookie 與隱私

```typescript
new ApplicationInsights({ config: {
  connectionString,
  isCookieUseDisabled: true,         // 完全停用所有 cookie
  cookieCfg: { enabled: true, domain: ".example.com", path: "/", expiry: 365 }
}});
```

要動態配合使用者同意：

```typescript
appInsights.getCookieMgr().setEnabled(userGaveConsent);
appInsights.config.disableTelemetry = !userGaveConsent;
```

## 取樣

建議在 App Insights 資源上設定伺服器端的 ingestion 取樣。SDK 端的取樣可以減少網路用量：

```typescript
new ApplicationInsights({ config: { connectionString, samplingPercentage: 50 } });
```

依類型取樣可以透過 telemetry initializer：根據 `item.baseType` 回傳 `false` 來丟棄。

## 離線／離開頁面時送出

SDK 使用 `sendBeacon`（預設 `onunloadDisableBeacon: false`），在 `pagehide`／`unload` 時送出剩餘資料。SPA 在會破壞狀態的轉換（登出、強制重新整理）之前，也要呼叫 `appInsights.flush()`。

## 常見的坑

1. **不要初始化兩次。** 在不同 bundle 重複 import 這個模組會產生重複的 page view。用單一共用的模組匯出。
2. **在第一次使用者輸入之前就初始化**，才不會漏掉早期的點擊／例外。
3. **Connection string 是公開的**，絕對不要把同一個 App Insights 資源拿去放後端機密。
4. **`enableAutoRouteTracking` 加上手動的 `trackPageView`** 會重複計算。二選一。
5. **CORS 的分散式追蹤**需要 API 允許 `Request-Id`、`Request-Context`、`traceparent`、`tracestate` 這幾個 request header，並且公開 `Request-Context` 這個 response header。
6. **GenAI 敏感內容**（`gen_ai.input.messages` 等）是 Opt-In，沒有明確的執行期 flag 和核准的資料處理方式，絕對不要記錄。
7. **Agent 的 token 用量在 `chat` span 上，不在 `invoke_agent` 上**，只有確定時才把彙總的用量複製到父層的 agent span。
8. **React StrictMode** 在開發時會重複執行 effect，要用模組層級的 singleton 保護 `loadAppInsights()`。

## Bundle 大小

完整的 web SDK 約 110 KB（minified），gzip 後約 36 KB。預算很吃緊時，用 **Loader Script** 讓 SDK 非同步載入、離開關鍵路徑，或對沒用到的 plugin 做 tree-shake。

## 主要型別

```typescript
import {
  ApplicationInsights,
  SeverityLevel,
  DistributedTracingModes,
  type IConfiguration,
  type IConfig,
  type ITelemetryItem,
  type ITelemetryPlugin,
  type ICustomProperties,
  type IPageViewTelemetry,
  type IEventTelemetry,
  type IExceptionTelemetry,
  type ITraceTelemetry,
  type IMetricTelemetry,
  type IDependencyTelemetry
} from "@microsoft/applicationinsights-web";
```

## 最佳實務

1. **單一 singleton 實例**，從單一模組匯出。
2. **盡早初始化**，在 app 進入點、router 設定之前。
3. **用 telemetry initializer** 附上 `app.version`、`tenantId`，並清除 PII／query string 裡的機密。
4. **設定 `distributedTracingMode: 2`**，並確保你的 API 接受／公開 W3C trace context 的 header。
5. **GenAI 部分**，原封不動使用 OTel 的 `gen_ai.*` 屬性名稱，這樣瀏覽器和後端的 telemetry 才能統一查詢。
6. **敏感內容的擷取要加把關**（`gen_ai.input.messages`／`gen_ai.output.messages`），用 build 時或執行期的 opt-in 控制。
7. **登出／敏感的頁面切換時要 flush**，才不會丟掉傳輸中的 telemetry。

## 參考資料

- [references/agent-traces.md](references/agent-traces.md)：精簡整理的完整 OTel GenAI 語意慣例（agent／model／tool span、屬性、內容擷取）。
- [references/framework-extensions.md](references/framework-extensions.md)：React、React Native、Angular、Next.js、Vite 的做法。
- [references/configuration.md](references/configuration.md)：完整的 `IConfiguration` 參考和調校指南。
- Microsoft Learn：<https://learn.microsoft.com/azure/azure-monitor/app/javascript-sdk>
- ApplicationInsights-JS 原始碼：<https://github.com/microsoft/ApplicationInsights-JS>
- OTel GenAI 語意慣例：<https://opentelemetry.io/docs/specs/semconv/gen-ai/>
