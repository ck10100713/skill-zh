---
name: azure-monitor-opentelemetry-py
description: |
  Python 版 Azure Monitor OpenTelemetry Distro。用於一行搞定 Application Insights 設定，並附帶自動 instrumentation。
  Triggers: "azure-monitor-opentelemetry", "configure_azure_monitor", "Application Insights", "OpenTelemetry distro", "auto-instrumentation".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-monitor-opentelemetry
---

# Azure Monitor OpenTelemetry Distro for Python

一行設定 Application Insights，附帶 OpenTelemetry 自動 instrumentation。

## 安裝

```bash
pip install azure-monitor-opentelemetry
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

## 快速開始

```python
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor

# connection string 用來識別 App Insights 資源（從 APPLICATIONINSIGHTS_CONNECTION_STRING 環境變數讀取）。
# DefaultAzureCredential 透過 Microsoft Entra ID 驗證 ingestion（比只用 instrumentation key 驗證更好）。
configure_azure_monitor(
    credential=DefaultAzureCredential(),
)

# 你的應用程式碼...
```

## 明確指定 Connection String

從環境變數讀取 connection string，再明確傳入。
這個值同時包含 `InstrumentationKey` 和 `IngestionEndpoint`。

```python
import os
from azure.monitor.opentelemetry import configure_azure_monitor

# 從環境變數讀取完整的 connection string。
# 格式："InstrumentationKey=<key>;IngestionEndpoint=https://<id>.in.applicationinsights.azure.com/"
connection_string = os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]

try:
    configure_azure_monitor(
        connection_string=connection_string,
    )
    # 你的應用程式碼...
except Exception as exc:
    raise RuntimeError(f"Azure Monitor configuration failed: {exc}") from exc
```

## 搭配 Flask

```python
from flask import Flask
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor()

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

if __name__ == "__main__":
    app.run()
```

## 搭配 Django

```python
# settings.py
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor()

# Django 設定...
```

## 搭配 FastAPI

```python
from fastapi import FastAPI
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor()

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

## 自訂 Trace

```python
from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor()

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("my-operation") as span:
    span.set_attribute("custom.attribute", "value")
    # 做事情...
```

## 自訂 Metric

```python
from opentelemetry import metrics
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor()

meter = metrics.get_meter(__name__)
counter = meter.create_counter("my_counter")

counter.add(1, {"dimension": "value"})
```

## 自訂 Log

```python
import logging
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logger.info("This will appear in Application Insights")
logger.error("Errors are captured too", exc_info=True)
```

## 取樣

```python
from azure.monitor.opentelemetry import configure_azure_monitor

# 取樣 10% 的請求
configure_azure_monitor(
    sampling_ratio=0.1
)
```

## Cloud Role Name

為 Application Map 設定 cloud role name：

```python
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

configure_azure_monitor(
    resource=Resource.create({SERVICE_NAME: "my-service-name"})
)
```

## 停用特定的 Instrumentation

```python
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor(
    instrumentations=["flask", "requests"]  # 只啟用這些
)
```

## 啟用 Live Metrics

```python
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor(
    enable_live_metrics=True
)
```

## Azure AD 驗證

```python
from azure.monitor.opentelemetry import configure_azure_monitor
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential

# 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod，或使用特定的 credential。
credential = DefaultAzureCredential()
# 或在正式環境直接使用特定的 credential：
# See https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()

configure_azure_monitor(
    credential=credential
)
```

## 內建的自動 Instrumentation

| Library | 遙測類型 |
|---------|---------------|
| Flask | Trace |
| Django | Trace |
| FastAPI | Trace |
| Requests | Trace |
| urllib3 | Trace |
| httpx | Trace |
| aiohttp | Trace |
| psycopg2 | Trace |
| pymysql | Trace |
| pymongo | Trace |
| redis | Trace |

## 設定選項

| 參數 | 說明 | 預設值 |
|-----------|-------------|---------|
| `connection_string` | Application Insights connection string | 來自環境變數 |
| `credential` | 用於 AAD 驗證的 Azure credential | None |
| `sampling_ratio` | 取樣率（0.0 到 1.0） | 1.0 |
| `resource` | OpenTelemetry Resource | 自動偵測 |
| `instrumentations` | 要啟用的 instrumentation 清單 | 全部 |
| `enable_live_metrics` | 啟用 Live Metrics 串流 | False |

## 最佳實務

1. **同步或非同步擇一，並保持一致。** 在同一條呼叫路徑裡，不要混用 `azure.xxx` 同步 client 和 `azure.xxx.aio` 非同步 client。每個 module 選一種模式。
2. **程序結束時呼叫 `provider.shutdown()` / `force_flush()` 來 flush 遙測資料，provider 不是 context manager。**
3. **盡早呼叫 configure_azure_monitor()**：要在 import 被 instrument 的 library 之前
4. **正式環境用環境變數**放 connection string
5. **設定 cloud role name**，多服務的應用程式尤其需要
6. **高流量應用程式要啟用取樣**
7. **使用結構化 logging**，log analytics 查詢更好寫
8. **替 span 加上自訂屬性**，除錯更方便
9. **正式環境的工作負載用 Microsoft Entra 驗證**

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打功能、operation group 涵蓋範圍，以及正式環境檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 針對次要／進階情境的專屬非主打範例。 |
