---
name: azure-monitor-opentelemetry-exporter-java
description: |
  Java 版 Azure Monitor OpenTelemetry Exporter。把 OpenTelemetry 的 trace、metric 和 log 匯出到 Azure Monitor/Application Insights。
  Triggers: "AzureMonitorExporter java", "opentelemetry azure java", "application insights java otel", "azure monitor tracing java".
  Note: 這個套件已 DEPRECATED（棄用）。請遷移到 azure-monitor-opentelemetry-autoconfigure。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: com.azure:azure-monitor-opentelemetry-exporter
---

# Azure Monitor OpenTelemetry Exporter for Java

> **⚠️ 棄用通知**：這個套件已棄用。請遷移到 `azure-monitor-opentelemetry-autoconfigure`。
>
> 詳細步驟請看[遷移指南](https://github.com/Azure/azure-sdk-for-java/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/MIGRATION.md)。

把 OpenTelemetry 遙測資料匯出到 Azure Monitor / Application Insights。

## 安裝（已棄用）

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-monitor-opentelemetry-exporter</artifactId>
    <version>1.0.0-beta.x</version>
</dependency>
```

## 建議：改用 Autoconfigure

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-monitor-opentelemetry-autoconfigure</artifactId>
    <version>LATEST</version>
</dependency>
```

## 環境變數

```bash
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=xxx;IngestionEndpoint=https://xxx.in.applicationinsights.azure.com/
```

## 用 Autoconfigure 做基本設定（建議）

### 使用環境變數

```java
import io.opentelemetry.sdk.autoconfigure.AutoConfiguredOpenTelemetrySdk;
import io.opentelemetry.sdk.autoconfigure.AutoConfiguredOpenTelemetrySdkBuilder;
import io.opentelemetry.api.OpenTelemetry;
import com.azure.monitor.opentelemetry.exporter.AzureMonitorExporter;

// connection string 來自 APPLICATIONINSIGHTS_CONNECTION_STRING 環境變數
AutoConfiguredOpenTelemetrySdkBuilder sdkBuilder = AutoConfiguredOpenTelemetrySdk.builder();
AzureMonitorExporter.customize(sdkBuilder);
OpenTelemetry openTelemetry = sdkBuilder.build().getOpenTelemetrySdk();
```

### 明確指定 Connection String

```java
AutoConfiguredOpenTelemetrySdkBuilder sdkBuilder = AutoConfiguredOpenTelemetrySdk.builder();
AzureMonitorExporter.customize(sdkBuilder, "{connection-string}");
OpenTelemetry openTelemetry = sdkBuilder.build().getOpenTelemetrySdk();
```

## 建立 Span

```java
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.context.Scope;

// 取得 tracer
Tracer tracer = openTelemetry.getTracer("com.example.myapp");

// 建立 span
Span span = tracer.spanBuilder("myOperation").startSpan();

try (Scope scope = span.makeCurrent()) {
    // 你的應用程式邏輯
    doWork();
} catch (Throwable t) {
    span.recordException(t);
    throw t;
} finally {
    span.end();
}
```

## 加入 Span 屬性

```java
import io.opentelemetry.api.common.AttributeKey;
import io.opentelemetry.api.common.Attributes;

Span span = tracer.spanBuilder("processOrder")
    .setAttribute("order.id", "12345")
    .setAttribute("customer.tier", "premium")
    .startSpan();

try (Scope scope = span.makeCurrent()) {
    // 執行期間加入屬性
    span.setAttribute("items.count", 3);
    span.setAttribute("total.amount", 99.99);
    
    processOrder();
} finally {
    span.end();
}
```

## 自訂 Span Processor

```java
import io.opentelemetry.sdk.trace.SpanProcessor;
import io.opentelemetry.sdk.trace.ReadWriteSpan;
import io.opentelemetry.sdk.trace.ReadableSpan;
import io.opentelemetry.context.Context;

private static final AttributeKey<String> CUSTOM_ATTR = AttributeKey.stringKey("custom.attribute");

SpanProcessor customProcessor = new SpanProcessor() {
    @Override
    public void onStart(Context context, ReadWriteSpan span) {
        // 為每個 span 加上自訂屬性
        span.setAttribute(CUSTOM_ATTR, "customValue");
    }

    @Override
    public boolean isStartRequired() {
        return true;
    }

    @Override
    public void onEnd(ReadableSpan span) {
        // 需要的話做後處理
    }

    @Override
    public boolean isEndRequired() {
        return false;
    }
};

// 註冊 processor
AutoConfiguredOpenTelemetrySdkBuilder sdkBuilder = AutoConfiguredOpenTelemetrySdk.builder();
AzureMonitorExporter.customize(sdkBuilder);

sdkBuilder.addTracerProviderCustomizer(
    (sdkTracerProviderBuilder, configProperties) -> 
        sdkTracerProviderBuilder.addSpanProcessor(customProcessor)
);

OpenTelemetry openTelemetry = sdkBuilder.build().getOpenTelemetrySdk();
```

## 巢狀 Span

```java
public void parentOperation() {
    Span parentSpan = tracer.spanBuilder("parentOperation").startSpan();
    try (Scope scope = parentSpan.makeCurrent()) {
        childOperation();
    } finally {
        parentSpan.end();
    }
}

public void childOperation() {
    // 透過 Context 自動連結到父 span
    Span childSpan = tracer.spanBuilder("childOperation").startSpan();
    try (Scope scope = childSpan.makeCurrent()) {
        // 子工作
    } finally {
        childSpan.end();
    }
}
```

## 記錄例外

```java
Span span = tracer.spanBuilder("riskyOperation").startSpan();
try (Scope scope = span.makeCurrent()) {
    performRiskyWork();
} catch (Exception e) {
    span.recordException(e);
    span.setStatus(StatusCode.ERROR, e.getMessage());
    throw e;
} finally {
    span.end();
}
```

## Metric（透過 OpenTelemetry）

```java
import io.opentelemetry.api.metrics.Meter;
import io.opentelemetry.api.metrics.LongCounter;
import io.opentelemetry.api.metrics.LongHistogram;

Meter meter = openTelemetry.getMeter("com.example.myapp");

// Counter
LongCounter requestCounter = meter.counterBuilder("http.requests")
    .setDescription("Total HTTP requests")
    .setUnit("requests")
    .build();

requestCounter.add(1, Attributes.of(
    AttributeKey.stringKey("http.method"), "GET",
    AttributeKey.longKey("http.status_code"), 200L
));

// Histogram
LongHistogram latencyHistogram = meter.histogramBuilder("http.latency")
    .setDescription("Request latency")
    .setUnit("ms")
    .ofLongs()
    .build();

latencyHistogram.record(150, Attributes.of(
    AttributeKey.stringKey("http.route"), "/api/users"
));
```

## 關鍵概念

| 概念 | 說明 |
|---------|-------------|
| Connection String | 含 instrumentation key 的 Application Insights connection string |
| Tracer | 建立 span，用於分散式追蹤 |
| Span | 代表一個工作單位，帶有時間與屬性 |
| SpanProcessor | 攔截 span 生命週期，用來客製化 |
| Exporter | 把遙測資料送到 Azure Monitor |

## 遷移到 Autoconfigure

`azure-monitor-opentelemetry-autoconfigure` 套件提供：
- 自動對常見 library 做 instrumentation
- 更簡單的設定
- 與 OpenTelemetry SDK 有更好的整合

### 遷移步驟

1. 替換 dependency：
   ```xml
   <!-- 移除 -->
   <dependency>
       <groupId>com.azure</groupId>
       <artifactId>azure-monitor-opentelemetry-exporter</artifactId>
   </dependency>
   
   <!-- 新增 -->
   <dependency>
       <groupId>com.azure</groupId>
       <artifactId>azure-monitor-opentelemetry-autoconfigure</artifactId>
   </dependency>
   ```

2. 依照[遷移指南](https://github.com/Azure/azure-sdk-for-java/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/MIGRATION.md)更新初始化程式碼

## 最佳實務

1. **使用 autoconfigure**：遷移到 `azure-monitor-opentelemetry-autoconfigure`
2. **取有意義的 span 名稱**：用描述性的操作名稱
3. **加入相關屬性**：帶上除錯用的上下文資料
4. **處理例外**：一律在 span 上記錄例外
5. **使用 semantic conventions**：遵循 OpenTelemetry 的 semantic conventions
6. **在 finally 裡結束 span**：確保 span 一定會被結束
7. **使用 try-with-resources**：用 try-with-resources 模式管理 scope

## 參考連結

| 資源 | URL |
|----------|-----|
| Maven 套件 | https://central.sonatype.com/artifact/com.azure/azure-monitor-opentelemetry-exporter |
| GitHub | https://github.com/Azure/azure-sdk-for-java/tree/main/sdk/monitor/azure-monitor-opentelemetry-exporter |
| 遷移指南 | https://github.com/Azure/azure-sdk-for-java/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/MIGRATION.md |
| Autoconfigure 套件 | https://central.sonatype.com/artifact/com.azure/azure-monitor-opentelemetry-autoconfigure |
| OpenTelemetry Java | https://opentelemetry.io/docs/languages/java/ |
| Application Insights | https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview |
