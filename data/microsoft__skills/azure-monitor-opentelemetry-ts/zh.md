---
name: azure-monitor-opentelemetry-ts
description: 用 Azure Monitor 與 OpenTelemetry for JavaScript（@azure/monitor-opentelemetry）替應用程式加上 instrumentation。用於替搭配 Application Insights 的 Node.js 應用程式加入分散式追蹤、metric 與 log。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: '@azure/monitor-opentelemetry'
---

# Azure Monitor OpenTelemetry SDK for TypeScript

替 Node.js 應用程式自動 instrument 分散式追蹤、metric 與 log。

## 安裝

```bash
# Distro（建議，自動 instrumentation）
npm install @azure/monitor-opentelemetry

# 底層 exporter（自訂 OpenTelemetry 設定）
npm install @azure/monitor-opentelemetry-exporter

# 自訂 log ingestion
npm install @azure/monitor-ingestion
```

## 環境變數

```bash
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...;IngestionEndpoint=...
AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境使用 DefaultAzureCredential 時才需要
```

## 快速開始（自動 Instrumentation）

**重要：** 一定要在 import 其他模組**之前**呼叫 `useAzureMonitor()`。

```typescript
import { useAzureMonitor } from "@azure/monitor-opentelemetry";

useAzureMonitor({
  azureMonitorExporterOptions: {
    connectionString: process.env.APPLICATIONINSIGHTS_CONNECTION_STRING
  }
});

// 現在才 import 你的應用程式
import express from "express";
const app = express();
```

## ESM 支援（Node.js 18.19+）

```bash
node --import @azure/monitor-opentelemetry/loader ./dist/index.js
```

**package.json:**
```json
{
  "scripts": {
    "start": "node --import @azure/monitor-opentelemetry/loader ./dist/index.js"
  }
}
```

## 完整設定

```typescript
import { useAzureMonitor, AzureMonitorOpenTelemetryOptions } from "@azure/monitor-opentelemetry";
import { resourceFromAttributes } from "@opentelemetry/resources";

const options: AzureMonitorOpenTelemetryOptions = {
  azureMonitorExporterOptions: {
    connectionString: process.env.APPLICATIONINSIGHTS_CONNECTION_STRING,
    storageDirectory: "/path/to/offline/storage",
    disableOfflineStorage: false
  },
  
  // 取樣
  samplingRatio: 1.0,  // 0-1，trace 的取樣百分比
  
  // 功能
  enableLiveMetrics: true,
  enableStandardMetrics: true,
  enablePerformanceCounters: true,
  
  // Instrumentation library
  instrumentationOptions: {
    azureSdk: { enabled: true },
    http: { enabled: true },
    mongoDb: { enabled: true },
    mySql: { enabled: true },
    postgreSql: { enabled: true },
    redis: { enabled: true },
    bunyan: { enabled: false },
    winston: { enabled: false }
  },
  
  // 自訂 resource
  resource: resourceFromAttributes({ "service.name": "my-service" })
};

useAzureMonitor(options);
```

## 自訂 Trace

```typescript
import { trace } from "@opentelemetry/api";

const tracer = trace.getTracer("my-tracer");

const span = tracer.startSpan("doWork");
try {
  span.setAttribute("component", "worker");
  span.setAttribute("operation.id", "42");
  span.addEvent("processing started");
  
  // 你的工作寫在這裡
  
} catch (error) {
  span.recordException(error as Error);
  span.setStatus({ code: 2, message: (error as Error).message });
} finally {
  span.end();
}
```

## 自訂 Metric

```typescript
import { metrics } from "@opentelemetry/api";

const meter = metrics.getMeter("my-meter");

// Counter
const counter = meter.createCounter("requests_total");
counter.add(1, { route: "/api/users", method: "GET" });

// Histogram
const histogram = meter.createHistogram("request_duration_ms");
histogram.record(150, { route: "/api/users" });

// Observable Gauge
const gauge = meter.createObservableGauge("active_connections");
gauge.addCallback((result) => {
  result.observe(getActiveConnections(), { pool: "main" });
});
```

## 手動設定 Exporter

### Trace Exporter

```typescript
import { AzureMonitorTraceExporter } from "@azure/monitor-opentelemetry-exporter";
import { NodeTracerProvider, BatchSpanProcessor } from "@opentelemetry/sdk-trace-node";

const exporter = new AzureMonitorTraceExporter({
  connectionString: process.env.APPLICATIONINSIGHTS_CONNECTION_STRING
});

const provider = new NodeTracerProvider({
  spanProcessors: [new BatchSpanProcessor(exporter)]
});

provider.register();
```

### Metric Exporter

```typescript
import { AzureMonitorMetricExporter } from "@azure/monitor-opentelemetry-exporter";
import { PeriodicExportingMetricReader, MeterProvider } from "@opentelemetry/sdk-metrics";
import { metrics } from "@opentelemetry/api";

const exporter = new AzureMonitorMetricExporter({
  connectionString: process.env.APPLICATIONINSIGHTS_CONNECTION_STRING
});

const meterProvider = new MeterProvider({
  readers: [new PeriodicExportingMetricReader({ exporter })]
});

metrics.setGlobalMeterProvider(meterProvider);
```

### Log Exporter

```typescript
import { AzureMonitorLogExporter } from "@azure/monitor-opentelemetry-exporter";
import { BatchLogRecordProcessor, LoggerProvider } from "@opentelemetry/sdk-logs";
import { logs } from "@opentelemetry/api-logs";

const exporter = new AzureMonitorLogExporter({
  connectionString: process.env.APPLICATIONINSIGHTS_CONNECTION_STRING
});

const loggerProvider = new LoggerProvider();
loggerProvider.addLogRecordProcessor(new BatchLogRecordProcessor(exporter));

logs.setGlobalLoggerProvider(loggerProvider);
```

## 自訂 Log Ingestion

```typescript
import { DefaultAzureCredential, ManagedIdentityCredential } from "@azure/identity";
import { LogsIngestionClient, isAggregateLogsUploadError } from "@azure/monitor-ingestion";

const endpoint = "https://<dce>.ingest.monitor.azure.com";
const ruleId = "<data-collection-rule-id>";
const streamName = "Custom-MyTable_CL";

// 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
const credential = new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]});
// 或在正式環境直接使用特定的 credential：
// See https://learn.microsoft.com/javascript/api/overview/azure/identity-readme?view=azure-node-latest#credential-classes
// const credential = new ManagedIdentityCredential();

const client = new LogsIngestionClient(endpoint, credential);

const logs = [
  {
    Time: new Date().toISOString(),
    Computer: "Server1",
    Message: "Application started",
    Level: "Information"
  }
];

try {
  await client.upload(ruleId, streamName, logs);
} catch (error) {
  if (isAggregateLogsUploadError(error)) {
    for (const uploadError of error.errors) {
      console.error("Failed logs:", uploadError.failedLogs);
    }
  }
}
```

## 自訂 Span Processor

```typescript
import { SpanProcessor, ReadableSpan } from "@opentelemetry/sdk-trace-base";
import { Span, Context, SpanKind, TraceFlags } from "@opentelemetry/api";
import { useAzureMonitor } from "@azure/monitor-opentelemetry";

class FilteringSpanProcessor implements SpanProcessor {
  forceFlush(): Promise<void> { return Promise.resolve(); }
  shutdown(): Promise<void> { return Promise.resolve(); }
  onStart(span: Span, context: Context): void {}
  
  onEnd(span: ReadableSpan): void {
    // 加入自訂屬性
    span.attributes["CustomDimension"] = "value";
    
    // 過濾掉內部 span
    if (span.kind === SpanKind.INTERNAL) {
      span.spanContext().traceFlags = TraceFlags.NONE;
    }
  }
}

useAzureMonitor({
  spanProcessors: [new FilteringSpanProcessor()]
});
```

## 取樣

```typescript
import { ApplicationInsightsSampler } from "@azure/monitor-opentelemetry-exporter";
import { NodeTracerProvider } from "@opentelemetry/sdk-trace-node";

// 取樣 75% 的 trace
const sampler = new ApplicationInsightsSampler(0.75);

const provider = new NodeTracerProvider({ sampler });
```

## Shutdown

```typescript
import { useAzureMonitor, shutdownAzureMonitor } from "@azure/monitor-opentelemetry";

useAzureMonitor();

// 應用程式 shutdown 時
process.on("SIGTERM", async () => {
  await shutdownAzureMonitor();
  process.exit(0);
});
```

## 主要型別

```typescript
import {
  useAzureMonitor,
  shutdownAzureMonitor,
  AzureMonitorOpenTelemetryOptions,
  InstrumentationOptions
} from "@azure/monitor-opentelemetry";

import {
  AzureMonitorTraceExporter,
  AzureMonitorMetricExporter,
  AzureMonitorLogExporter,
  ApplicationInsightsSampler,
  AzureMonitorExporterOptions
} from "@azure/monitor-opentelemetry-exporter";

import {
  LogsIngestionClient,
  isAggregateLogsUploadError
} from "@azure/monitor-ingestion";
```

## 最佳實務

1. **先呼叫 useAzureMonitor()**：要在 import 其他模組之前
2. **ESM 專案用 ESM loader**：`--import @azure/monitor-opentelemetry/loader`
3. **啟用離線儲存**：斷線情境下遙測資料才可靠
4. **設定取樣比例**：高流量應用程式要設
5. **加入自訂維度**：用 span processor 來豐富資料
6. **優雅地 shutdown**：呼叫 `shutdownAzureMonitor()` 來 flush 遙測資料
