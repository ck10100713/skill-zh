---
name: azure-monitor-opentelemetry-exporter-py
description: |
  Python 版 Azure Monitor OpenTelemetry Exporter。用於底層的 OpenTelemetry 匯出到 Application Insights。
  Triggers: "azure-monitor-opentelemetry-exporter", "AzureMonitorTraceExporter", "AzureMonitorMetricExporter", "AzureMonitorLogExporter".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-monitor-opentelemetry-exporter
---

# Azure Monitor OpenTelemetry Exporter for Python

底層 exporter，把 OpenTelemetry 的 trace、metric 和 log 送到 Application Insights。

## 安裝

```bash
pip install azure-monitor-opentelemetry-exporter
```

## 環境變數

```bash
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=xxx;IngestionEndpoint=https://xxx.in.applicationinsights.azure.com/  # 所有驗證方式都必填
AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境使用 DefaultAzureCredential 時才需要
```

## 驗證與生命週期

> **🔑 下面每一段程式碼都適用兩條規則：**
>
> 1. **有支援時，ingestion 驗證優先使用 `DefaultAzureCredential`。** `APPLICATIONINSIGHTS_CONNECTION_STRING` 用來指出目標 Application Insights 資源，`credential=DefaultAzureCredential(...)` 則提供 Microsoft Entra 驗證。
>    - 本機開發：直接用 `DefaultAzureCredential` 即可。
>    - 正式環境：設定 `AZURE_TOKEN_CREDENTIALS=prod`（或 `AZURE_TOKEN_CREDENTIALS=<specific_credential>`），把 credential chain 限制在適合正式環境的 credential。
> 2. **Provider 不是 context manager。** 程序結束時要明確 flush 並 shut down 遙測 provider，緩衝區的資料才會確定被匯出。
>
> 範例程式碼可能會省略這段設定，但正式環境的程式碼一定要同時遵守這兩條規則。

## 何時使用

| 情境 | 使用 |
|----------|-----|
| 快速設定、自動 instrumentation | `azure-monitor-opentelemetry`（distro） |
| 自訂 OpenTelemetry pipeline | `azure-monitor-opentelemetry-exporter`（本套件） |
| 需要細緻控制遙測資料 | `azure-monitor-opentelemetry-exporter`（本套件） |

## Trace Exporter

```python
from azure.identity import DefaultAzureCredential
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

# 從環境變數讀取 APPLICATIONINSIGHTS_CONNECTION_STRING 來識別資源；
# DefaultAzureCredential 透過 Microsoft Entra ID 驗證 ingestion。
exporter = AzureMonitorTraceExporter(
    credential=DefaultAzureCredential(),
)

# 設定 tracer provider
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(exporter)
)

# 使用 tracer
tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("my-span"):
    print("Hello, World!")
```

## Metric Exporter

```python
from azure.identity import DefaultAzureCredential
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter

# 從環境變數讀取 APPLICATIONINSIGHTS_CONNECTION_STRING；透過 DefaultAzureCredential 以 AAD 驗證 ingestion。
exporter = AzureMonitorMetricExporter(
    credential=DefaultAzureCredential(),
)

# 設定 meter provider
reader = PeriodicExportingMetricReader(exporter, export_interval_millis=60000)
metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))

# 使用 meter
meter = metrics.get_meter(__name__)
counter = meter.create_counter("requests_total")
counter.add(1, {"route": "/api/users"})
```

## Log Exporter

```python
import logging
from azure.identity import DefaultAzureCredential
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

# 從環境變數讀取 APPLICATIONINSIGHTS_CONNECTION_STRING；透過 DefaultAzureCredential 以 AAD 驗證 ingestion。
exporter = AzureMonitorLogExporter(
    credential=DefaultAzureCredential(),
)

# 設定 logger provider
logger_provider = LoggerProvider()
logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
set_logger_provider(logger_provider)

# 把 handler 加到 Python logging
handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)

# 使用 logging
logger = logging.getLogger(__name__)
logger.info("This will be sent to Application Insights")
```

## 從環境變數讀取

Exporter 會自動讀取 `APPLICATIONINSIGHTS_CONNECTION_STRING`：

```python
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

# connection string 來自環境變數；透過 DefaultAzureCredential 以 AAD 驗證 ingestion。
exporter = AzureMonitorTraceExporter(
    credential=DefaultAzureCredential(),
)
```

## Azure AD 驗證

```python
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

# 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在正式環境直接使用特定的 credential：
# See https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()

exporter = AzureMonitorTraceExporter(
    credential=credential
)
```

## 取樣

用 `ApplicationInsightsSampler` 做一致的取樣：

```python
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio
from azure.monitor.opentelemetry.exporter import ApplicationInsightsSampler

# 取樣 10% 的 trace
sampler = ApplicationInsightsSampler(sampling_ratio=0.1)

trace.set_tracer_provider(TracerProvider(sampler=sampler))
```

## 離線儲存

設定離線儲存以便重試：

```python
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

exporter = AzureMonitorTraceExporter(
    credential=DefaultAzureCredential(),
    storage_directory="/path/to/storage",  # 自訂儲存路徑
    disable_offline_storage=False  # 啟用重試（預設）
)
```

## 停用離線儲存

```python
exporter = AzureMonitorTraceExporter(
    credential=DefaultAzureCredential(),
    disable_offline_storage=True  # 失敗時不重試
)
```

## 主權雲（Sovereign Clouds）

```python
from azure.identity import AzureAuthorityHosts, DefaultAzureCredential
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

# Azure Government
credential = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_GOVERNMENT)
exporter = AzureMonitorTraceExporter(
    connection_string="InstrumentationKey=xxx;IngestionEndpoint=https://xxx.in.applicationinsights.azure.us/",
    credential=credential
)
```

## Exporter 類型

| Exporter | 遙測類型 | Application Insights 資料表 |
|----------|---------------|---------------------------|
| `AzureMonitorTraceExporter` | Trace/Span | requests, dependencies, exceptions |
| `AzureMonitorMetricExporter` | Metric | customMetrics, performanceCounters |
| `AzureMonitorLogExporter` | Log | traces, customEvents |

## 設定選項

| 參數 | 說明 | 預設值 |
|-----------|-------------|---------|
| `connection_string` | Application Insights connection string | 來自環境變數 |
| `credential` | 用於 AAD 驗證的 Azure credential | None |
| `disable_offline_storage` | 停用重試用的儲存 | False |
| `storage_directory` | 自訂儲存路徑 | 暫存目錄 |

## 最佳實務

1. **同步或非同步擇一，並保持一致。** 在同一條呼叫路徑裡，不要混用 `azure.xxx` 同步 client 和 `azure.xxx.aio` 非同步 client。每個 module 選一種模式。
2. **程序結束時呼叫 `provider.shutdown()` / `force_flush()` 來 flush 遙測資料，provider 不是 context manager。**
3. **正式環境用 BatchSpanProcessor**（不要用 SimpleSpanProcessor）
4. **用 ApplicationInsightsSampler**，讓各服務的取樣一致
5. **啟用離線儲存**，提升正式環境的可靠性
6. **用 Microsoft Entra 驗證**，不要用 instrumentation key
7. **設定適合你工作負載的匯出間隔**
8. **使用 distro**（`azure-monitor-opentelemetry`），除非你需要自訂 pipeline

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打功能、operation group 涵蓋範圍，以及正式環境檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 針對次要／進階情境的專屬非主打範例。 |
