---
name: azure-search-documents-py
description: |
  Python 版的 Azure AI Search SDK。用於向量搜尋、混合搜尋、語意排序、indexing 和 skillset。
  Triggers: "azure-search-documents", "SearchClient", "SearchIndexClient", "vector search", "hybrid search", "semantic search".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-search-documents
---

# Python 版 Azure AI Search SDK

全文檢索、向量和混合搜尋，並具備 AI enrichment 能力。

## 安裝

```bash
pip install azure-search-documents
```

## 環境變數

```bash
AZURE_SEARCH_ENDPOINT=https://<service-name>.search.windows.net  # 所有驗證方式都必填
AZURE_SEARCH_INDEX_NAME=<your-index-name>  # 所有驗證方式都必填
AZURE_TOKEN_CREDENTIALS=prod # 只有在 production 使用 DefaultAzureCredential 時才需要
AZURE_SEARCH_API_KEY=<your-api-key>  # 只有下面舊式的 API key 驗證才需要
```

## 驗證與生命週期

> **🔑 下面每個程式碼範例都適用兩條規則：**
>
> 1. **優先用 `DefaultAzureCredential`。** 它在本機（Azure CLI / VS Code / Developer CLI）和 Azure 上（managed identity、workload identity）都能用，不用改程式碼。避免用 connection string、account key 或 API key，它們會繞過 Entra 的稽核和輪替。
>    - 本機開發：直接用 `DefaultAzureCredential` 就好。
>    - Production：設定 `AZURE_TOKEN_CREDENTIALS=prod`（或 `AZURE_TOKEN_CREDENTIALS=<specific_credential>`），把 credential chain 限縮在 production 安全的 credential。
> 2. **每個 client 都用 context manager 包起來**，這樣 HTTP transport、socket 和 token cache 才會確實釋放：
>    - 同步：`with <Client>(...) as client:`
>    - 非同步：`async with <Client>(...) as client:` **而且** `async with DefaultAzureCredential() as credential:`（來自 `azure.identity.aio`）
>
> 範例片段可能會簡化這段設定，但 production 的程式碼一定要兩條規則都遵守。

```python
import os
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.search.documents import SearchClient

# 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在 production 直接用特定的 credential：
# See https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()

with SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name=os.environ["AZURE_SEARCH_INDEX_NAME"],
    credential=credential,
) as client:
    results = list(client.search(search_text="*", top=5))
```

### 舊式做法：API Key（既有使用 key 的部署）

新程式碼請用上面的 `DefaultAzureCredential`。只有在既有的部署還在用 key、還沒遷移到 Entra ID 時才用 `AzureKeyCredential`，例如還在進行 Entra 導入的受管制環境。同一個 `AzureKeyCredential` 也能用在 `SearchIndexClient` 和 `SearchIndexerClient` 的管理操作。

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

with SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name=os.environ["AZURE_SEARCH_INDEX_NAME"],
    credential=AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]),
) as client:
    results = list(client.search(search_text="*", top=5))
```

## Client 類型

| Client | 用途 |
|--------|---------|
| `SearchClient` | 搜尋和文件操作 |
| `SearchIndexClient` | Index 管理、synonym map |
| `SearchIndexerClient` | Indexer、data source、skillset |

## 建立含向量欄位的 Index

```python
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SearchableField,
    SimpleField
)

fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SearchableField(name="title", type=SearchFieldDataType.String),
    SearchableField(name="content", type=SearchFieldDataType.String),
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=1536,
        vector_search_profile_name="my-vector-profile"
    )
]

vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(name="my-hnsw")
    ],
    profiles=[
        VectorSearchProfile(
            name="my-vector-profile",
            algorithm_configuration_name="my-hnsw"
        )
    ]
)

index = SearchIndex(
    name="my-index",
    fields=fields,
    vector_search=vector_search
)

with SearchIndexClient(endpoint, DefaultAzureCredential()) as index_client:
    index_client.create_or_update_index(index)
```

## 上傳文件

```python
from azure.search.documents import SearchClient

documents = [
    {
        "id": "1",
        "title": "Azure AI Search",
        "content": "Full-text and vector search service",
        "content_vector": [0.1, 0.2, ...]  # 1536 維
    }
]

with SearchClient(endpoint, "my-index", DefaultAzureCredential()) as client:
    result = client.upload_documents(documents)
    print(f"Uploaded {len(result)} documents")
```

## 關鍵字搜尋

```python
results = client.search(
    search_text="azure search",
    select=["id", "title", "content"],
    top=10
)

for result in results:
    print(f"{result['title']}: {result['@search.score']}")
```

## 向量搜尋

```python
from azure.search.documents.models import VectorizedQuery

# 你的查詢 embedding（1536 維）
query_vector = get_embedding("semantic search capabilities")

vector_query = VectorizedQuery(
    vector=query_vector,
    k_nearest_neighbors=10,
    fields="content_vector"
)

results = client.search(
    vector_queries=[vector_query],
    select=["id", "title", "content"]
)

for result in results:
    print(f"{result['title']}: {result['@search.score']}")
```

## 混合搜尋（向量 + 關鍵字）

```python
from azure.search.documents.models import VectorizedQuery

vector_query = VectorizedQuery(
    vector=query_vector,
    k_nearest_neighbors=10,
    fields="content_vector"
)

results = client.search(
    search_text="azure search",
    vector_queries=[vector_query],
    select=["id", "title", "content"],
    top=10
)
```

## 語意排序

```python
from azure.search.documents.models import QueryType

results = client.search(
    search_text="what is azure search",
    query_type=QueryType.SEMANTIC,
    semantic_configuration_name="my-semantic-config",
    select=["id", "title", "content"],
    top=10
)

for result in results:
    print(f"{result['title']}")
    if result.get("@search.captions"):
        print(f"  Caption: {result['@search.captions'][0].text}")
```

## Filter

```python
results = client.search(
    search_text="*",
    filter="category eq 'Technology' and rating gt 4",
    order_by=["rating desc"],
    select=["id", "title", "category", "rating"]
)
```

## Facet

```python
results = client.search(
    search_text="*",
    facets=["category,count:10", "rating"],
    top=0  # 只取 facet，不取文件
)

for facet_name, facet_values in results.get_facets().items():
    print(f"{facet_name}:")
    for facet in facet_values:
        print(f"  {facet['value']}: {facet['count']}")
```

## 自動完成與建議

```python
# Autocomplete
results = client.autocomplete(
    search_text="sea",
    suggester_name="my-suggester",
    mode="twoTerms"
)

# Suggest
results = client.suggest(
    search_text="sea",
    suggester_name="my-suggester",
    select=["title"]
)
```

## 搭配 Skillset 的 Indexer

```python
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexer,
    SearchIndexerDataSourceConnection,
    SearchIndexerSkillset,
    EntityRecognitionSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry
)

with SearchIndexerClient(endpoint, DefaultAzureCredential()) as indexer_client:
    # 用 managed identity（search service 必須在 storage account 上有 RBAC 角色）。避免使用內嵌 key 的 storage connection string。
    data_source = SearchIndexerDataSourceConnection(
        name="my-datasource",
        type="azureblob",
        connection_string="ResourceId=/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/<acct>",
        container={"name": "documents"}
    )
    indexer_client.create_or_update_data_source_connection(data_source)

    # 建立 skillset
    skillset = SearchIndexerSkillset(
        name="my-skillset",
        skills=[
            EntityRecognitionSkill(
                inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                outputs=[OutputFieldMappingEntry(name="organizations", target_name="organizations")]
            )
        ]
    )
    indexer_client.create_or_update_skillset(skillset)

    # 建立 indexer
    indexer = SearchIndexer(
        name="my-indexer",
        data_source_name="my-datasource",
        target_index_name="my-index",
        skillset_name="my-skillset"
    )
    indexer_client.create_or_update_indexer(indexer)
```

## 最佳實務

1. **同步或非同步選一個，然後保持一致。** 同一條呼叫路徑裡，不要混用 `azure.xxx` 同步 client 和 `azure.xxx.aio` 非同步 client。每個 module 只選一種模式。
2. **client 和非同步 credential 一律用 context manager。** 每個 client 都用 `with Client(...) as client:`（同步）或 `async with Client(...) as client:`（非同步）包起來。非同步的 `DefaultAzureCredential`（來自 `azure.identity.aio`）也要用 `async with credential:`，token 和 transport 才會清乾淨。
3. **用混合搜尋**，結合向量和關鍵字，相關性最好
4. 自然語言查詢要**啟用語意排序**
5. **分批 index**，每批 100 到 1000 份文件，效率比較好
6. 排序前**先用 filter** 縮小結果
7. **向量維度要設成**跟你的 embedding 模型一致
8. 大規模向量搜尋**用 HNSW 演算法**
9. **suggester 要在建立 index 時就建好**（之後不能再加）

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/vector-search.md](references/vector-search.md) | HNSW 設定、integrated vectorization、多向量查詢 |
| [references/semantic-ranking.md](references/semantic-ranking.md) | 語意設定、caption、answer、混合模式 |
| [scripts/setup_vector_index.py](scripts/setup_vector_index.py) | 建立支援向量的 search index 的 CLI script |


---

## 其他 Azure AI Search 模式

# Azure AI Search Python SDK

用 `azure-search-documents` 寫出乾淨、符合 Python 慣用寫法的 Azure AI Search 程式碼。

## 安裝

```bash
pip install azure-search-documents azure-identity
```

## 環境變數

```bash
AZURE_SEARCH_ENDPOINT=https://<search-service>.search.windows.net  # 所有驗證方式都必填
AZURE_SEARCH_INDEX_NAME=<index-name>  # 所有驗證方式都必填
AZURE_TOKEN_CREDENTIALS=prod # 只有在 production 使用 DefaultAzureCredential 時才需要
```

## 驗證

```python
import os
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.search.documents import SearchClient

# 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
credential = DefaultAzureCredential(require_envvar=True)
# 或在 production 直接用特定的 credential：
# See https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python#credential-classes
# credential = ManagedIdentityCredential()

with SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name=os.environ["AZURE_SEARCH_INDEX_NAME"],
    credential=credential,
) as client:
    results = list(client.search(search_text="*", top=5))
```

## 選擇 Client

| Client | 用途 |
|--------|---------|
| `SearchClient` | 查詢 index、上傳／更新／刪除文件 |
| `SearchIndexClient` | 建立／管理 index、knowledge source、knowledge base |
| `SearchIndexerClient` | 管理 indexer、skillset、data source |
| `KnowledgeBaseRetrievalClient` | 用 LLM 驅動問答的 agentic retrieval |

## 建立 Index 的模式

```python
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SearchField, VectorSearch, VectorSearchProfile,
    HnswAlgorithmConfiguration, AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters, SemanticSearch,
    SemanticConfiguration, SemanticPrioritizedFields, SemanticField
)

index = SearchIndex(
    name=index_name,
    fields=[
        SearchField(name="id", type="Edm.String", key=True),
        SearchField(name="content", type="Edm.String", searchable=True),
        SearchField(name="embedding", type="Collection(Edm.Single)",
                   vector_search_dimensions=3072,
                   vector_search_profile_name="vector-profile"),
    ],
    vector_search=VectorSearch(
        profiles=[VectorSearchProfile(
            name="vector-profile",
            algorithm_configuration_name="hnsw-algo",
            vectorizer_name="openai-vectorizer"
        )],
        algorithms=[HnswAlgorithmConfiguration(name="hnsw-algo")],
        vectorizers=[AzureOpenAIVectorizer(
            vectorizer_name="openai-vectorizer",
            parameters=AzureOpenAIVectorizerParameters(
                resource_url=aoai_endpoint,
                deployment_name=embedding_deployment,
                model_name=embedding_model
            )
        )]
    ),
    semantic_search=SemanticSearch(
        default_configuration_name="semantic-config",
        configurations=[SemanticConfiguration(
            name="semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                content_fields=[SemanticField(field_name="content")]
            )
        )]
    )
)

with SearchIndexClient(endpoint, credential) as index_client:
    index_client.create_or_update_index(index)
```

## 文件操作

```python
from azure.search.documents import SearchIndexingBufferedSender

# 自動分批的批次上傳
with SearchIndexingBufferedSender(endpoint, index_name, credential) as sender:
    sender.upload_documents(documents)

# 透過 SearchClient 直接操作
with SearchClient(endpoint, index_name, credential) as search_client:
    search_client.upload_documents(documents)      # 新增
    search_client.merge_documents(documents)       # 更新既有文件
    search_client.merge_or_upload_documents(documents)  # Upsert
    search_client.delete_documents(documents)      # 刪除
```

## 搜尋模式

```python
# 基本搜尋
results = search_client.search(search_text="query")

# 向量搜尋
from azure.search.documents.models import VectorizedQuery

results = search_client.search(
    search_text=None,
    vector_queries=[VectorizedQuery(
        vector=embedding,
        k_nearest_neighbors=5,
        fields="embedding"
    )]
)

# 混合搜尋（向量 + 關鍵字）
results = search_client.search(
    search_text="query",
    vector_queries=[VectorizedQuery(vector=embedding, k_nearest_neighbors=5, fields="embedding")],
    query_type="semantic",
    semantic_configuration_name="semantic-config"
)

# 搭配 filter
results = search_client.search(
    search_text="query",
    filter="category eq 'technology'",
    select=["id", "title", "content"],
    top=10
)
```

## Agentic Retrieval（Knowledge Base）

要用 LLM 驅動、能合成答案的問答，請看 [references/agentic-retrieval.md](references/agentic-retrieval.md)。

關鍵概念：
- **Knowledge Source**：指向一個 search index
- **Knowledge Base**：包裝 knowledge source 加上 LLM，負責查詢規劃和答案合成
- **輸出模式**：`EXTRACTIVE_DATA`（原始 chunk）或 `ANSWER_SYNTHESIS`（LLM 產生的答案）

## 非同步模式

```python
from azure.search.documents.aio import SearchClient

async with SearchClient(endpoint, index_name, credential) as client:
    results = await client.search(search_text="query")
    async for result in results:
        print(result["title"])
```

## 最佳實務

1. endpoint、key 和 deployment 名稱**用環境變數**
2. 在本機跑的程式碼**用 `DefaultAzureCredential`**（不要用 API key）。在 Azure 上跑的程式碼用特定的 token credential。
3. 批次上傳**用 `SearchIndexingBufferedSender`**（它會處理分批和重試）
4. agentic retrieval 的 index **一定要定義 semantic configuration**
5. 建立 index 用 **`create_or_update_index`**，重跑也不會出問題（idempotent）
6. 用 context manager 或明確呼叫 `close()` 來**關閉 client**

## 欄位類型參考

| EDM 類型 | Python | 備註 |
|----------|--------|-------|
| `Edm.String` | str | 可搜尋的文字 |
| `Edm.Int32` | int | 整數 |
| `Edm.Int64` | int | 長整數 |
| `Edm.Double` | float | 浮點數 |
| `Edm.Boolean` | bool | True/False |
| `Edm.DateTimeOffset` | datetime | ISO 8601 |
| `Collection(Edm.Single)` | List[float] | 向量 embedding |
| `Collection(Edm.String)` | List[str] | 字串陣列 |

## 錯誤處理

```python
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceExistsError
)

try:
    result = search_client.get_document(key="123")
except ResourceNotFoundError:
    print("Document not found")
except HttpResponseError as e:
    print(f"Search error: {e.message}")
```
