---
name: azure-ai-translation-document-py
description: |
  Azure AI Document Translation SDK，用來批次翻譯文件並保留格式。適合大量翻譯 Word、PDF、Excel、PowerPoint 等文件格式。
  Triggers: "document translation", "batch translation", "translate documents", "DocumentTranslationClient".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-ai-translation-document
---

# Azure AI Document Translation SDK for Python

Azure AI Translator 文件翻譯服務的 client library，用來批次翻譯文件並保留格式。

## Installation

```bash
pip install azure-ai-translation-document
```

## Environment Variables

```bash
AZURE_DOCUMENT_TRANSLATION_ENDPOINT=https://<resource>.cognitiveservices.azure.com  # 所有驗證方式都需要
# 來源與目標文件的儲存空間
AZURE_SOURCE_CONTAINER_URL=https://<storage>.blob.core.windows.net/<container>?<sas>  # 所有驗證方式都需要
AZURE_TARGET_CONTAINER_URL=https://<storage>.blob.core.windows.net/<container>?<sas>  # 所有驗證方式都需要
AZURE_TOKEN_CREDENTIALS=prod # 只有在 production 使用 DefaultAzureCredential 時才需要
AZURE_DOCUMENT_TRANSLATION_KEY=<your-api-key>  # 只有下面舊版 API key 驗證路徑才需要
```

## Authentication & Lifecycle

> **🔑 下面每個程式範例都適用兩條規則：**
>
> 1. **優先用 `DefaultAzureCredential`。** 它在本機（Azure CLI / VS Code / Developer CLI）和 Azure 上（managed identity、workload identity）都能跑，程式碼不用改。避免用 connection string、account/API key，因為它們會繞過 Entra 的稽核和金鑰輪替。
>    - 本機開發：`DefaultAzureCredential` 直接可用。
>    - Production：設定 `AZURE_TOKEN_CREDENTIALS=prod`（或 `AZURE_TOKEN_CREDENTIALS=<specific_credential>`），把 credential chain 限縮在 production 安全的 credential。
> 2. **每個 client 都要包在 context manager 裡**，這樣 HTTP transport、socket 和 token cache 會確實被釋放：
>    - 同步：`with <Client>(...) as client:`
>    - 非同步：`async with <Client>(...) as client:` **而且** `async with DefaultAzureCredential() as credential:`（來自 `azure.identity.aio`）
>
> 範例程式碼可能會省略這部分設定，但 production 程式碼一定要兩條規則都遵守。

```python
import os
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.ai.translation.document import DocumentTranslationClient

# 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential()
# 或在 production 直接用指定的 credential：
# 參考 https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()

with DocumentTranslationClient(
    endpoint=os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"],
    credential=credential,
) as client:
    statuses = list(client.list_translation_statuses())
```

### Legacy: API Key (existing keyed deployments)

新程式碼請用上面的 `DefaultAzureCredential`。只有在既有的 key 驗證部署還沒遷移到 Entra ID 時才用 `AzureKeyCredential`，例如還在進行 Entra 上線的受管制環境。

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.document import DocumentTranslationClient, SingleDocumentTranslationClient

with DocumentTranslationClient(
    endpoint=os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["AZURE_DOCUMENT_TRANSLATION_KEY"]),
) as client:
    statuses = list(client.list_translation_statuses())

# SingleDocumentTranslationClient 也接受同樣的 key 型 credential。
```

## Basic Document Translation

```python
import os
from azure.ai.translation.document import DocumentTranslationClient, DocumentTranslationInput, TranslationTarget
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()

with DocumentTranslationClient(
    endpoint=os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"],
    credential=credential,
) as client:
    source_url = os.environ["AZURE_SOURCE_CONTAINER_URL"]
    target_url = os.environ["AZURE_TARGET_CONTAINER_URL"]

    try:
        # 啟動翻譯工作
        poller = client.begin_translation(
            inputs=[
                DocumentTranslationInput(
                    source_url=source_url,
                    targets=[
                        TranslationTarget(
                            target_url=target_url,
                            language="es"  # 翻成西班牙文
                        )
                    ]
                )
            ]
        )

        # 等待完成
        result = poller.result()

        print(f"Status: {poller.status()}")
        print(f"Documents translated: {poller.details.documents_succeeded_count}")
        print(f"Documents failed: {poller.details.documents_failed_count}")
    except HttpResponseError as e:
        print(f"Translation failed: {e.message}")
        raise
```

## Multiple Target Languages

```python
poller = client.begin_translation(
    inputs=[
        DocumentTranslationInput(
            source_url=source_url,
            targets=[
                TranslationTarget(target_url=target_url_es, language="es"),
                TranslationTarget(target_url=target_url_fr, language="fr"),
                TranslationTarget(target_url=target_url_de, language="de")
            ]
        )
    ]
)
```

## Translate Single Document

```python
from azure.ai.translation.document import SingleDocumentTranslationClient
from azure.identity import DefaultAzureCredential

with open("document.docx", "rb") as f:
    document_content = f.read()

with SingleDocumentTranslationClient(endpoint, DefaultAzureCredential()) as single_client:
    result = single_client.translate(
        body=document_content,
        target_language="es",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# 儲存翻譯後的文件
with open("document_es.docx", "wb") as f:
    f.write(result)
```

## Check Translation Status

```python
# 取得所有翻譯作業
operations = client.list_translation_statuses()

for op in operations:
    print(f"Operation ID: {op.id}")
    print(f"Status: {op.status}")
    print(f"Created: {op.created_on}")
    print(f"Total documents: {op.documents_total_count}")
    print(f"Succeeded: {op.documents_succeeded_count}")
    print(f"Failed: {op.documents_failed_count}")
```

## List Document Statuses

```python
# 取得工作中每份文件的狀態
operation_id = poller.id
document_statuses = client.list_document_statuses(operation_id)

for doc in document_statuses:
    print(f"Document: {doc.source_document_url}")
    print(f"  Status: {doc.status}")
    print(f"  Translated to: {doc.translated_to}")
    if doc.error:
        print(f"  Error: {doc.error.message}")
```

## Cancel Translation

```python
# 取消執行中的翻譯
client.cancel_translation(operation_id)
```

## Using Glossary

```python
from azure.ai.translation.document import TranslationGlossary

poller = client.begin_translation(
    inputs=[
        DocumentTranslationInput(
            source_url=source_url,
            targets=[
                TranslationTarget(
                    target_url=target_url,
                    language="es",
                    glossaries=[
                        TranslationGlossary(
                            glossary_url="https://<storage>.blob.core.windows.net/glossary/terms.csv?<sas>",
                            file_format="csv"
                        )
                    ]
                )
            ]
        )
    ]
)
```

## Supported Document Formats

```python
# 取得支援的格式
formats = client.get_supported_document_formats()

for fmt in formats:
    print(f"Format: {fmt.format}")
    print(f"  Extensions: {fmt.file_extensions}")
    print(f"  Content types: {fmt.content_types}")
```

## Supported Languages

```python
# 取得支援的語言
languages = client.get_supported_languages()

for lang in languages:
    print(f"Language: {lang.name} ({lang.code})")
```

## Async Client

```python
from azure.ai.translation.document.aio import DocumentTranslationClient
from azure.identity.aio import DefaultAzureCredential

async def translate_documents():
    async with DefaultAzureCredential() as credential:
        async with DocumentTranslationClient(
            endpoint=endpoint,
            credential=credential,
        ) as client:
            poller = await client.begin_translation(inputs=[...])
            result = await poller.result()
```

## Supported Formats

| Category | Formats |
|----------|---------|
| Documents | DOCX, PDF, PPTX, XLSX, HTML, TXT, RTF |
| Structured | CSV, TSV, JSON, XML |
| Localization | XLIFF, XLF, MHTML |

## Storage Requirements

- 來源和目標 container 必須是 Azure Blob Storage
- 使用權限剛好夠用的 SAS token：
  - 來源：Read, List
  - 目標：Write, List

## Best Practices

1. **同步或非同步擇一，並保持一致。** 同一條呼叫路徑裡不要混用 `azure.xxx` 同步 client 和 `azure.xxx.aio` 非同步 client。每個 module 只選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都包在 `with Client(...) as client:`（同步）或 `async with Client(...) as client:`（非同步）裡。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，這樣 token 和 transport 才會被清掉。
3. **使用 SAS token**，權限給最小必要範圍
4. **用 `poller.status()` 監控**長時間執行的作業
5. **逐一檢查文件狀態**，處理文件層級的錯誤
6. **使用 glossary** 處理特定領域的術語
7. **每種語言用獨立的目標 container**
8. **多個並行工作時用非同步 client**
9. **送出文件前先確認支援的格式**

## Reference Files

| File | Contents |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打功能、operation group 涵蓋範圍，以及 production 檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 次要與進階情境的專屬非主打範例。 |
