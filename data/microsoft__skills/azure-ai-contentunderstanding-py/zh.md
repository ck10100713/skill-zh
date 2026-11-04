---
name: azure-ai-contentunderstanding-py
description: |
  Azure AI Content Understanding SDK（Python 版）。用於從文件、圖片、音訊和影片擷取多模態內容。
  Triggers: "azure-ai-contentunderstanding", "ContentUnderstandingClient", "multimodal analysis", "document extraction", "video analysis", "audio transcription"。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-ai-contentunderstanding
---

# Azure AI Content Understanding SDK（Python）

多模態 AI 服務，從文件、影片、音訊和圖片檔擷取語意內容，用於 RAG 和自動化流程。

## 安裝

```bash
pip install azure-ai-contentunderstanding
```

## 環境變數

```bash
CONTENTUNDERSTANDING_ENDPOINT=https://<resource>.cognitiveservices.azure.com/  # 所有認證方式都必填
AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境用 DefaultAzureCredential 時才需要
```

## 認證與生命週期

> **🔑 下面每一段範例程式都適用兩條規則：**
>
> 1. **優先用 `DefaultAzureCredential`。** 它在本機（Azure CLI / VS Code / Developer CLI）和 Azure 上（managed identity、workload identity）都能跑，程式碼不用改。避免用 connection string、帳號金鑰或 API key，它們會繞過 Entra 的稽核和金鑰輪替。
>    - 本機開發：直接用 `DefaultAzureCredential` 就好。
>    - 正式環境：設定 `AZURE_TOKEN_CREDENTIALS=prod`（或 `AZURE_TOKEN_CREDENTIALS=<specific_credential>`），把 credential chain 限縮在適合正式環境的憑證。
> 2. **每個 client 都要包在 context manager 裡**，這樣 HTTP transport、socket 和 token cache 才會確實被釋放：
>    - 同步：`with <Client>(...) as client:`
>    - 非同步：`async with <Client>(...) as client:` **以及** `async with DefaultAzureCredential() as credential:`（來自 `azure.identity.aio`）
>
> 範例片段可能會省略這些設定，但正式環境的程式碼一定要遵守這兩條規則。

```python
import os
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential

endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
# 本機開發：用 DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在正式環境直接使用指定的 credential：
# See https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()
with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
    analyzers = list(client.list_analyzers())
```

## 核心流程

Content Understanding 的操作都是非同步的長時間執行操作：

1. **開始分析**：用 `begin_analyze()` 啟動分析操作（回傳 poller）
2. **輪詢結果**：輪詢直到分析完成（SDK 用 `.result()` 處理）
3. **處理結果**：從 `AnalyzeResult.contents` 取出結構化結果

## 預建 Analyzer

| Analyzer | 內容類型 | 用途 |
|----------|--------------|---------|
| `prebuilt-documentSearch` | 文件 | 為 RAG 應用擷取 markdown |
| `prebuilt-imageSearch` | 圖片 | 從圖片擷取內容 |
| `prebuilt-audioSearch` | 音訊 | 轉錄音訊並附上時間資訊 |
| `prebuilt-videoSearch` | 影片 | 擷取畫面、逐字稿、摘要 |
| `prebuilt-invoice` | 文件 | 擷取發票欄位 |

## 分析文件

```python
import os
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import AnalyzeInput
from azure.identity import DefaultAzureCredential

endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
with ContentUnderstandingClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential()
) as client:
    # 從 URL 分析文件
    poller = client.begin_analyze(
        analyzer_id="prebuilt-documentSearch",
        inputs=[AnalyzeInput(url="https://example.com/document.pdf")]
    )

    result = poller.result()

    # 存取 markdown 內容（contents 是 list）
    content = result.contents[0]
    print(content.markdown)
```

## 存取文件內容細節

```python
from azure.ai.contentunderstanding.models import MediaContentKind, DocumentContent

content = result.contents[0]
if content.kind == MediaContentKind.DOCUMENT:
    document_content: DocumentContent = content  # type: ignore
    print(document_content.start_page_number)
```

## 分析圖片

```python
from azure.ai.contentunderstanding.models import AnalyzeInput

poller = client.begin_analyze(
    analyzer_id="prebuilt-imageSearch",
    inputs=[AnalyzeInput(url="https://example.com/image.jpg")]
)
result = poller.result()
content = result.contents[0]
print(content.markdown)
```

## 分析影片

```python
from azure.ai.contentunderstanding.models import AnalyzeInput

poller = client.begin_analyze(
    analyzer_id="prebuilt-videoSearch",
    inputs=[AnalyzeInput(url="https://example.com/video.mp4")]
)

result = poller.result()

# 存取影片內容（AudioVisualContent）
content = result.contents[0]

# 取得帶時間的逐字稿片語
for phrase in content.transcript_phrases:
    print(f"[{phrase.start_time} - {phrase.end_time}]: {phrase.text}")

# 取得關鍵畫面（影片用）
for frame in content.key_frames:
    print(f"Frame at {frame.time}: {frame.description}")
```

## 分析音訊

```python
from azure.ai.contentunderstanding.models import AnalyzeInput

poller = client.begin_analyze(
    analyzer_id="prebuilt-audioSearch",
    inputs=[AnalyzeInput(url="https://example.com/audio.mp3")]
)

result = poller.result()

# 存取音訊逐字稿
content = result.contents[0]
for phrase in content.transcript_phrases:
    print(f"[{phrase.start_time}] {phrase.text}")
```

## 自訂 Analyzer

用欄位 schema 建立自訂 analyzer，做專門的擷取：

```python
# 建立自訂 analyzer
analyzer = client.create_analyzer(
    analyzer_id="my-invoice-analyzer",
    analyzer={
        "description": "Custom invoice analyzer",
        "base_analyzer_id": "prebuilt-documentSearch",
        "field_schema": {
            "fields": {
                "vendor_name": {"type": "string"},
                "invoice_total": {"type": "number"},
                "line_items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "amount": {"type": "number"}
                        }
                    }
                }
            }
        }
    }
)

# 使用自訂 analyzer
from azure.ai.contentunderstanding.models import AnalyzeInput

poller = client.begin_analyze(
    analyzer_id="my-invoice-analyzer",
    inputs=[AnalyzeInput(url="https://example.com/invoice.pdf")]
)

result = poller.result()

# 存取擷取出的欄位
print(result.fields["vendor_name"])
print(result.fields["invoice_total"])
```

## Analyzer 管理

```python
# 列出所有 analyzer
analyzers = client.list_analyzers()
for analyzer in analyzers:
    print(f"{analyzer.analyzer_id}: {analyzer.description}")

# 取得指定的 analyzer
analyzer = client.get_analyzer("prebuilt-documentSearch")

# 刪除自訂 analyzer
client.delete_analyzer("my-custom-analyzer")
```

## 非同步 Client

```python
import asyncio
import os
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import AnalyzeInput
from azure.identity.aio import DefaultAzureCredential

async def analyze_document():
    endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
    async with DefaultAzureCredential() as credential:
        async with ContentUnderstandingClient(
            endpoint=endpoint,
            credential=credential
        ) as client:
            poller = await client.begin_analyze(
                analyzer_id="prebuilt-documentSearch",
                inputs=[AnalyzeInput(url="https://example.com/doc.pdf")]
            )
            result = await poller.result()
            content = result.contents[0]
            return content.markdown

asyncio.run(analyze_document())
```

## 內容類型

| Class | 適用 | 提供 |
|-------|-----|----------|
| `DocumentContent` | PDF、圖片、Office 文件 | 頁面、表格、圖、段落 |
| `AudioVisualContent` | 音訊、影片檔 | 逐字稿片語、時間、關鍵畫面 |

兩者都繼承自 `MediaContent`，它提供基本資訊和 markdown 表示。

## Model Import

```python
from azure.ai.contentunderstanding.models import (
    AnalyzeInput,
    AnalyzeResult,
    MediaContentKind,
    DocumentContent,
    AudioVisualContent,
)
```

## Client 類型

| Client | 用途 |
|--------|---------|
| `ContentUnderstandingClient` | 處理所有操作的同步 client |
| `ContentUnderstandingClient` (aio) | 處理所有操作的非同步 client |

## 最佳實務

1. **同步或非同步擇一，並保持一致。** 同一條呼叫路徑裡，不要混用 `azure.ai.contentunderstanding` 的同步 client 和 `azure.ai.contentunderstanding.aio` 的非同步 client。每個模組選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都包在 `with ContentUnderstandingClient(...) as client:`（同步）或 `async with ContentUnderstandingClient(...) as client:`（非同步）裡。來自 `azure.identity.aio` 的非同步 `DefaultAzureCredential` 也要用 `async with credential:`，token 和 transport 才會被清掉。
3. **`begin_analyze` 搭配 `AnalyzeInput` 使用**：這是正確的方法簽章
4. **用 `result.contents[0]` 存取結果**：結果是以 list 回傳的
5. 常見情境**用預建 analyzer**（文件／圖片／音訊／影片搜尋）
6. 只有在擷取特定領域的欄位時才**建立自訂 analyzer**
7. 高吞吐量情境**用非同步 client**，搭配 `azure.identity.aio` 的 credential
8. **處理長時間執行的操作**：影片／音訊分析可能要好幾分鐘
9. 可以的話**用 URL 當來源**，省下上傳的開銷

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打的功能、各 operation group 的涵蓋範圍，以及正式環境檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 針對次要／進階情境的專門範例（非主打）。 |
