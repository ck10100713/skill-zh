---
name: azure-ai-language-conversations-py
description: 用 azure-ai-language-conversations Python SDK 實作 Conversational Language Understanding（CLU）。在使用 ConversationAnalysisClient 分析對話意圖和實體、建立 NLP 功能，或把語言理解整合進應用程式時使用。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# Azure AI Language Conversations（Python）

## System Prompt
你是專精於 Azure AI Services 和自然語言處理的 Python 資深開發者。
你的任務是幫助使用者用 `azure-ai-language-conversations` SDK 實作 Conversational Language Understanding（CLU）。

回應 Azure AI Language Conversations 相關的請求時：
1. 一律使用最新版的 `azure-ai-language-conversations` SDK。
2. 強調要搭配 `DefaultAzureCredential` 使用 `ConversationAnalysisClient`。
3. 提供清楚的程式碼範例，示範如何組織對話 payload。
4. 妥善處理例外。

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

`ConversationAnalysisClient` 接受 `TokenCredential`，例如 `DefaultAzureCredential`。用 token credential，它在本機（Azure CLI / VS Code / Developer CLI）和 Azure 上（managed identity、workload identity）都能跑，程式碼不用改。

### 舊做法：API Key（既有使用金鑰的部署）

新的程式碼應該用 `DefaultAzureCredential`。只有在既有的金鑰部署還沒遷移到 Entra ID 時才用 `AzureKeyCredential`，例如還在完成 Entra 導入的受規範環境。

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient

endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
key = os.environ["AZURE_CONVERSATIONS_KEY"]

with ConversationAnalysisClient(endpoint, AzureKeyCredential(key)) as client:
    # analyze_conversation 的 payload 請見下面的「Basic Conversation Analysis」
    ...
```

## 最佳實務
- **同步或非同步擇一，並保持一致。** 同一條呼叫路徑裡，不要混用 `azure.ai.language.conversations` 的同步 client 和 `azure.ai.language.conversations.aio` 的非同步 client。每個模組選一種模式。
- **client 和非同步 credential 一律用 context manager。** 每個 client 都包在 `with ConversationAnalysisClient(...) as client:`（同步）或 `async with ConversationAnalysisClient(...) as client:`（非同步）裡。來自 `azure.identity.aio` 的非同步 `DefaultAzureCredential` 也要用 `async with credential:`，token 和 transport 才會被清掉。
- **使用 `DefaultAzureCredential`**，在本機開發和 Azure 之間都能通用（避免 API key，它們會繞過 Entra 的稽核和金鑰輪替）。
- endpoint、project 名稱和 deployment 名稱都用環境變數。
- 清楚對應 `conversationItem` payload 裡的 `participantId` 和 `id`。

## 範例

### Basic Conversation Analysis
```python
import os
from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations import ConversationAnalysisClient

endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
project_name = os.environ["AZURE_CONVERSATIONS_PROJECT"]
deployment_name = os.environ["AZURE_CONVERSATIONS_DEPLOYMENT"]

# DefaultAzureCredential 在本機和 Azure 上都能用，程式碼不用改。
credential = DefaultAzureCredential()

with ConversationAnalysisClient(endpoint, credential) as client:
    query = "Send an email to Carol about the tomorrow's meeting"
    result = client.analyze_conversation(
        task={
            "kind": "Conversation",
            "analysisInput": {
                "conversationItem": {
                    "participantId": "1",
                    "id": "1",
                    "modality": "text",
                    "language": "en",
                    "text": query
                },
                "isLoggingEnabled": False
            },
            "parameters": {
                "projectName": project_name,
                "deploymentName": deployment_name,
                "verbose": True
            }
        }
    )

    print(f"Top intent: {result['result']['prediction']['topIntent']}")
```

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打的功能、各 operation group 的涵蓋範圍，以及正式環境檢查清單。 |
| [references/non-hero-scenarios.md](references/non-hero-scenarios.md) | 針對次要／進階情境的專門範例（非主打）。 |
