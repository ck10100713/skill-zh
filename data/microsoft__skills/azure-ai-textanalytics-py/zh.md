---
name: azure-ai-textanalytics-py
description: |
  Azure AI Text Analytics SDK，用於情緒分析、實體辨識、關鍵片語、語言偵測、PII 和醫療 NLP。用於對文字做自然語言處理。
  Triggers: "text analytics", "sentiment analysis", "entity recognition", "key phrase", "PII detection", "TextAnalyticsClient"。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-ai-textanalytics
---

# Azure AI Text Analytics SDK（Python）

Azure AI Language 服務 NLP 功能的 client 函式庫，包含情緒、實體、關鍵片語等。

## 安裝

```bash
pip install azure-ai-textanalytics
```

## 環境變數

```bash
AZURE_LANGUAGE_ENDPOINT=https://<resource>.cognitiveservices.azure.com  # 所有認證方式都必填
AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境用 DefaultAzureCredential 時才需要
AZURE_LANGUAGE_KEY=<your-api-key>  # 只有用下面舊的 API key 認證路徑時才需要
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
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.ai.textanalytics import TextAnalyticsClient

# 本機開發：用 DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在正式環境直接使用指定的 credential：
# See https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()

with TextAnalyticsClient(
    endpoint=os.environ["AZURE_LANGUAGE_ENDPOINT"],
    credential=credential,
) as client:
    languages = client.detect_language(["Hello, world!"])
```

### 舊做法：API Key（既有使用金鑰的部署）

新的程式碼應該用上面的 `DefaultAzureCredential`。只有在既有的金鑰部署還沒遷移到 Entra ID 時才用 `AzureKeyCredential`，例如還在完成 Entra 導入的受規範環境。

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

with TextAnalyticsClient(
    endpoint=os.environ["AZURE_LANGUAGE_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["AZURE_LANGUAGE_KEY"]),
) as client:
    languages = client.detect_language(["Hello, world!"])
```

## 情緒分析

```python
documents = [
    "I had a wonderful trip to Seattle last week!",
    "The food was terrible and the service was slow."
]

result = client.analyze_sentiment(documents, show_opinion_mining=True)

for doc in result:
    if not doc.is_error:
        print(f"Sentiment: {doc.sentiment}")
        print(f"Scores: pos={doc.confidence_scores.positive:.2f}, "
              f"neg={doc.confidence_scores.negative:.2f}, "
              f"neu={doc.confidence_scores.neutral:.2f}")
        
        # 意見探勘（以面向為基礎的情緒分析）
        for sentence in doc.sentences:
            for opinion in sentence.mined_opinions:
                target = opinion.target
                print(f"  Target: '{target.text}' - {target.sentiment}")
                for assessment in opinion.assessments:
                    print(f"    Assessment: '{assessment.text}' - {assessment.sentiment}")
```

## 實體辨識

```python
documents = ["Microsoft was founded by Bill Gates and Paul Allen in Albuquerque."]

result = client.recognize_entities(documents)

for doc in result:
    if not doc.is_error:
        for entity in doc.entities:
            print(f"Entity: {entity.text}")
            print(f"  Category: {entity.category}")
            print(f"  Subcategory: {entity.subcategory}")
            print(f"  Confidence: {entity.confidence_score:.2f}")
```

## PII 偵測

```python
documents = ["My SSN is 123-45-6789 and my email is john@example.com"]

result = client.recognize_pii_entities(documents)

for doc in result:
    if not doc.is_error:
        print(f"Redacted: {doc.redacted_text}")
        for entity in doc.entities:
            print(f"PII: {entity.text} ({entity.category})")
```

## 關鍵片語擷取

```python
documents = ["Azure AI provides powerful machine learning capabilities for developers."]

result = client.extract_key_phrases(documents)

for doc in result:
    if not doc.is_error:
        print(f"Key phrases: {doc.key_phrases}")
```

## 語言偵測

```python
documents = ["Ce document est en francais.", "This is written in English."]

result = client.detect_language(documents)

for doc in result:
    if not doc.is_error:
        print(f"Language: {doc.primary_language.name} ({doc.primary_language.iso6391_name})")
        print(f"Confidence: {doc.primary_language.confidence_score:.2f}")
```

## 醫療文字分析

```python
documents = ["Patient has diabetes and was prescribed metformin 500mg twice daily."]

poller = client.begin_analyze_healthcare_entities(documents)
result = poller.result()

for doc in result:
    if not doc.is_error:
        for entity in doc.entities:
            print(f"Entity: {entity.text}")
            print(f"  Category: {entity.category}")
            print(f"  Normalized: {entity.normalized_text}")
            
            # 實體連結（UMLS 等）
            for link in entity.data_sources:
                print(f"  Link: {link.name} - {link.entity_id}")
```

## 多重分析（批次）

```python
from azure.ai.textanalytics import (
    RecognizeEntitiesAction,
    ExtractKeyPhrasesAction,
    AnalyzeSentimentAction
)

documents = ["Microsoft announced new Azure AI features at Build conference."]

poller = client.begin_analyze_actions(
    documents,
    actions=[
        RecognizeEntitiesAction(),
        ExtractKeyPhrasesAction(),
        AnalyzeSentimentAction()
    ]
)

results = poller.result()
for doc_results in results:
    for result in doc_results:
        if result.kind == "EntityRecognition":
            print(f"Entities: {[e.text for e in result.entities]}")
        elif result.kind == "KeyPhraseExtraction":
            print(f"Key phrases: {result.key_phrases}")
        elif result.kind == "SentimentAnalysis":
            print(f"Sentiment: {result.sentiment}")
```

## 非同步 Client

```python
from azure.ai.textanalytics.aio import TextAnalyticsClient
from azure.identity.aio import DefaultAzureCredential

async def analyze():
    async with DefaultAzureCredential() as credential:
        async with TextAnalyticsClient(
            endpoint=endpoint,
            credential=credential
        ) as client:
            result = await client.analyze_sentiment(documents)
            # 處理結果...
```

## Client 類型

| Client | 用途 |
|--------|---------|
| `TextAnalyticsClient` | 所有文字分析操作 |
| `TextAnalyticsClient` (aio) | 非同步版本 |

## 可用操作

| 方法 | 說明 |
|--------|-------------|
| `analyze_sentiment` | 含意見探勘的情緒分析 |
| `recognize_entities` | 具名實體辨識 |
| `recognize_pii_entities` | PII 偵測與遮蔽 |
| `recognize_linked_entities` | 連結到 Wikipedia 的實體連結 |
| `extract_key_phrases` | 關鍵片語擷取 |
| `detect_language` | 語言偵測 |
| `begin_analyze_healthcare_entities` | 醫療 NLP（長時間執行） |
| `begin_analyze_actions` | 批次執行多種分析 |

## 最佳實務

1. **同步或非同步擇一，並保持一致。** 同一條呼叫路徑裡，不要混用 `azure.ai.textanalytics` 的同步 client 和 `azure.ai.textanalytics.aio` 的非同步 client。每個模組選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都包在 `with TextAnalyticsClient(...) as client:`（同步）或 `async with TextAnalyticsClient(...) as client:`（非同步）裡。來自 `azure.identity.aio` 的非同步 `DefaultAzureCredential` 也要用 `async with credential:`，token 和 transport 才會被清掉。
3. 多份文件**用批次操作**（每次請求最多 10 份）
4. 想要詳細的面向式情緒分析時**開啟意見探勘**
5. 高吞吐量情境**用非同步 client**
6. **處理文件層級的錯誤**：結果 list 裡可能有些文件是錯誤
7. 知道語言時**要指定語言**，可以提高準確度

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打的功能、各 operation group 的涵蓋範圍，以及正式環境檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 針對次要／進階情境的專門範例（非主打）。 |
