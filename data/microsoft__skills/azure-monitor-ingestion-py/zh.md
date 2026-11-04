---
name: azure-monitor-ingestion-py
description: |
  Python 版 Azure Monitor Ingestion SDK。用於透過 Logs Ingestion API 把自訂 log 送到 Log Analytics workspace。
  Triggers: "azure-monitor-ingestion", "LogsIngestionClient", "custom logs", "DCR", "data collection rule", "Log Analytics".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-monitor-ingestion
---

# Azure Monitor Ingestion SDK for Python

用 Logs Ingestion API 把自訂 log 送到 Azure Monitor Log Analytics workspace。

## 安裝

```bash
pip install azure-monitor-ingestion
pip install azure-identity
```

## 環境變數

```bash
# Data Collection Endpoint (DCE)
AZURE_DCE_ENDPOINT=https://<dce-name>.<region>.ingest.monitor.azure.com  # 所有驗證方式都必填

# Data Collection Rule (DCR) 的 immutable ID
AZURE_DCR_RULE_ID=dcr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # 所有驗證方式都必填

# DCR 的 stream 名稱
AZURE_DCR_STREAM_NAME=Custom-MyTable_CL  # 所有驗證方式都必填
AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境使用 DefaultAzureCredential 時才需要
```

## 前置條件

使用這個 SDK 之前，你需要：

1. **Log Analytics Workspace**：log 的目的地
2. **Data Collection Endpoint (DCE)**：ingestion endpoint
3. **Data Collection Rule (DCR)**：定義 schema 與目的地
4. **自訂資料表**：在 Log Analytics 裡（透過 DCR 或手動建立）

## 驗證與生命週期

> **🔑 下面每一段程式碼都適用兩條規則：**
>
> 1. **優先使用 `DefaultAzureCredential`。** 它在本機（Azure CLI / VS Code / Developer CLI）和 Azure 上（managed identity、workload identity）都能運作，不用改程式碼。避免使用 connection string、account/API key，它們會繞過 Entra 的稽核與輪替。
>    - 本機開發：直接用 `DefaultAzureCredential` 即可。
>    - 正式環境：設定 `AZURE_TOKEN_CREDENTIALS=prod`（或 `AZURE_TOKEN_CREDENTIALS=<specific_credential>`），把 credential chain 限制在適合正式環境的 credential。
> 2. **每個 client 都要包在 context manager 裡**，這樣 HTTP transport、socket 和 token cache 才會確定性地被釋放：
>    - 同步：`with <Client>(...) as client:`
>    - 非同步：`async with <Client>(...) as client:` **以及** `async with DefaultAzureCredential() as credential:`（來自 `azure.identity.aio`）
>
> 範例程式碼可能會省略這段設定，但正式環境的程式碼一定要同時遵守這兩條規則。

```python
from azure.monitor.ingestion import LogsIngestionClient
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
import os

# 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在正式環境直接使用特定的 credential：
# See https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()

with LogsIngestionClient(
    endpoint=os.environ["AZURE_DCE_ENDPOINT"],
    credential=credential
) as client:
    # 後續所有操作都用 `client.upload(...)`（見下方範例）
    ...
```

## 上傳自訂 Log

```python
from azure.monitor.ingestion import LogsIngestionClient
from azure.identity import DefaultAzureCredential
import os

rule_id = os.environ["AZURE_DCR_RULE_ID"]
stream_name = os.environ["AZURE_DCR_STREAM_NAME"]

logs = [
    {"TimeGenerated": "2024-01-15T10:00:00Z", "Computer": "server1", "Message": "Application started"},
    {"TimeGenerated": "2024-01-15T10:01:00Z", "Computer": "server1", "Message": "Processing request"},
    {"TimeGenerated": "2024-01-15T10:02:00Z", "Computer": "server2", "Message": "Connection established"}
]

with LogsIngestionClient(
    endpoint=os.environ["AZURE_DCE_ENDPOINT"],
    credential=DefaultAzureCredential()
) as client:
    client.upload(rule_id=rule_id, stream_name=stream_name, logs=logs)
```

## 從 JSON 檔上傳

```python
import json

with open("logs.json", "r") as f:
    logs = json.load(f)

client.upload(rule_id=rule_id, stream_name=stream_name, logs=logs)
```

## 自訂錯誤處理

用 callback 處理部分失敗：

```python
failed_logs = []

def on_error(error):
    print(f"Upload failed: {error.error}")
    failed_logs.extend(error.failed_logs)

client.upload(
    rule_id=rule_id,
    stream_name=stream_name,
    logs=logs,
    on_error=on_error
)

# 重試失敗的 log
if failed_logs:
    print(f"Retrying {len(failed_logs)} failed logs...")
    client.upload(rule_id=rule_id, stream_name=stream_name, logs=failed_logs)
```

## 忽略錯誤

```python
def ignore_errors(error):
    pass  # 靜默忽略上傳失敗

client.upload(
    rule_id=rule_id,
    stream_name=stream_name,
    logs=logs,
    on_error=ignore_errors
)
```

## 非同步 Client

```python
import asyncio
from azure.monitor.ingestion.aio import LogsIngestionClient
from azure.identity.aio import DefaultAzureCredential

async def upload_logs():
    async with LogsIngestionClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential()
    ) as client:
        await client.upload(
            rule_id=rule_id,
            stream_name=stream_name,
            logs=logs
        )

asyncio.run(upload_logs())
```

## 主權雲（Sovereign Clouds）

```python
from azure.identity import AzureAuthorityHosts, DefaultAzureCredential
from azure.monitor.ingestion import LogsIngestionClient

# Azure Government
credential = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_GOVERNMENT)
with LogsIngestionClient(
    endpoint="https://example.ingest.monitor.azure.us",
    credential=credential,
    credential_scopes=["https://monitor.azure.us/.default"]
) as client:
    # client.upload(...)
    ...
```

## 批次行為

SDK 會自動：
- 把 log 切成 1MB 以下的區塊
- 用 gzip 壓縮每個區塊
- 平行上傳區塊

大量 log 不需要自己做批次。

## Client 類型

| Client | 用途 |
|--------|---------|
| `LogsIngestionClient` | 上傳 log 的同步 client |
| `LogsIngestionClient` (aio) | 上傳 log 的非同步 client |

## 關鍵概念

| 概念 | 說明 |
|---------|-------------|
| **DCE** | Data Collection Endpoint，ingestion URL |
| **DCR** | Data Collection Rule，定義 schema、轉換與目的地 |
| **Stream** | DCR 內具名的資料流 |
| **Custom Table** | Log Analytics 裡的目標資料表（名稱以 `_CL` 結尾） |

## DCR Stream 名稱格式

Stream 名稱遵循以下模式：
- `Custom-<TableName>_CL`：用於自訂資料表
- `Microsoft-<TableName>`：用於內建資料表

## 最佳實務

1. **同步或非同步擇一，並保持一致。** 在同一條呼叫路徑裡，不要混用 `azure.xxx` 同步 client 和 `azure.xxx.aio` 非同步 client。每個 module 選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都包在 `with Client(...) as client:`（同步）或 `async with Client(...) as client:`（非同步）裡，確保正確清理。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，這樣 token 和 transport 才會被清掉。
3. **在本機執行的程式碼用 `DefaultAzureCredential`**。在 Azure 上執行的程式碼用特定的 token credential。
4. **優雅地處理錯誤**：部分失敗用 `on_error` callback
5. **包含 TimeGenerated**：所有 log 都必填的欄位
6. **符合 DCR schema**：log 欄位要符合 DCR 的欄位定義
7. **高吞吐量情境用非同步 client**
8. **批次上傳**：SDK 會處理批次，但送出的區塊大小要合理
9. **監控 ingestion**：到 Log Analytics 檢查 ingestion 狀態

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打功能、operation group 涵蓋範圍，以及正式環境檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 針對次要／進階情境的專屬非主打範例。 |
