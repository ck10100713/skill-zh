---
name: azure-search-documents-dotnet
description: |
  .NET 版的 Azure AI Search SDK（Azure.Search.Documents）。用來建構支援全文檢索、向量、語意和混合搜尋的搜尋應用。涵蓋 SearchClient（查詢、文件 CRUD）、SearchIndexClient（index 管理）和 SearchIndexerClient（indexer、skillset）。Triggers: "Azure Search .NET", "SearchClient", "SearchIndexClient", "vector search C#", "semantic search .NET", "hybrid search", "Azure.Search.Documents".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: Azure.Search.Documents
---

# Azure.Search.Documents (.NET)

建構具備全文檢索、向量、語意和混合搜尋能力的搜尋應用。

## 安裝

```bash
dotnet add package Azure.Search.Documents
dotnet add package Azure.Identity
```

**目前版本**：Stable v11.7.0、Preview v11.8.0-beta.1

## 環境變數

```bash
SEARCH_ENDPOINT=https://<search-service>.search.windows.net  # 必填：search service endpoint
SEARCH_INDEX_NAME=<index-name>  # 必填：search index 名稱
AZURE_TOKEN_CREDENTIALS=prod  # 只有在 production 使用 DefaultAzureCredential 時才需要
SEARCH_API_KEY=<api-key>  # 只有用 AzureKeyCredential 驗證時才需要
```

## 驗證

**Microsoft Entra Token Credential**：
```csharp
using Azure.Identity;
using Azure.Search.Documents;

// 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
var credential = new DefaultAzureCredential(
    DefaultAzureCredential.DefaultEnvironmentVariableName
);
// 或在 production 直接用特定的 credential：
// See https://learn.microsoft.com/dotnet/api/overview/azure/identity-readme?view=azure-dotnet#credential-classes
// var credential = new ManagedIdentityCredential();
var client = new SearchClient(
    new Uri(Environment.GetEnvironmentVariable("SEARCH_ENDPOINT")),
    Environment.GetEnvironmentVariable("SEARCH_INDEX_NAME"),
    credential);
```

**API Key**：
```csharp
using Azure;
using Azure.Search.Documents;

var credential = new AzureKeyCredential(
    Environment.GetEnvironmentVariable("SEARCH_API_KEY"));
var client = new SearchClient(
    new Uri(Environment.GetEnvironmentVariable("SEARCH_ENDPOINT")),
    Environment.GetEnvironmentVariable("SEARCH_INDEX_NAME"),
    credential);
```

## 選擇 Client

| Client | 用途 |
|--------|---------|
| `SearchClient` | 查詢 index、上傳／更新／刪除文件 |
| `SearchIndexClient` | 建立／管理 index、synonym map |
| `SearchIndexerClient` | 管理 indexer、skillset、data source |

## 建立 Index

### 使用 FieldBuilder（建議）

```csharp
using Azure.Search.Documents.Indexes;
using Azure.Search.Documents.Indexes.Models;

// 用 attribute 定義 model
public class Hotel
{
    [SimpleField(IsKey = true, IsFilterable = true)]
    public string HotelId { get; set; }

    [SearchableField(IsSortable = true)]
    public string HotelName { get; set; }

    [SearchableField(AnalyzerName = LexicalAnalyzerName.EnLucene)]
    public string Description { get; set; }

    [SimpleField(IsFilterable = true, IsSortable = true, IsFacetable = true)]
    public double? Rating { get; set; }

    [VectorSearchField(VectorSearchDimensions = 1536, VectorSearchProfileName = "vector-profile")]
    public ReadOnlyMemory<float>? DescriptionVector { get; set; }
}

// 建立 index
var indexClient = new SearchIndexClient(endpoint, credential);
var fieldBuilder = new FieldBuilder();
var fields = fieldBuilder.Build(typeof(Hotel));

var index = new SearchIndex("hotels")
{
    Fields = fields,
    VectorSearch = new VectorSearch
    {
        Profiles = { new VectorSearchProfile("vector-profile", "hnsw-algo") },
        Algorithms = { new HnswAlgorithmConfiguration("hnsw-algo") }
    }
};

await indexClient.CreateOrUpdateIndexAsync(index);
```

### 手動定義欄位

```csharp
var index = new SearchIndex("hotels")
{
    Fields =
    {
        new SimpleField("hotelId", SearchFieldDataType.String) { IsKey = true, IsFilterable = true },
        new SearchableField("hotelName") { IsSortable = true },
        new SearchableField("description") { AnalyzerName = LexicalAnalyzerName.EnLucene },
        new SimpleField("rating", SearchFieldDataType.Double) { IsFilterable = true, IsSortable = true },
        new SearchField("descriptionVector", SearchFieldDataType.Collection(SearchFieldDataType.Single))
        {
            VectorSearchDimensions = 1536,
            VectorSearchProfileName = "vector-profile"
        }
    }
};
```

## 文件操作

```csharp
var searchClient = new SearchClient(endpoint, indexName, credential);

// Upload（新增）
var hotels = new[] { new Hotel { HotelId = "1", HotelName = "Hotel A" } };
await searchClient.UploadDocumentsAsync(hotels);

// Merge（更新既有文件）
await searchClient.MergeDocumentsAsync(hotels);

// Merge or Upload（upsert）
await searchClient.MergeOrUploadDocumentsAsync(hotels);

// Delete
await searchClient.DeleteDocumentsAsync("hotelId", new[] { "1", "2" });

// 批次操作
var batch = IndexDocumentsBatch.Create(
    IndexDocumentsAction.Upload(hotel1),
    IndexDocumentsAction.Merge(hotel2),
    IndexDocumentsAction.Delete(hotel3));
await searchClient.IndexDocumentsAsync(batch);
```

## 搜尋模式

### 基本搜尋

```csharp
var options = new SearchOptions
{
    Filter = "rating ge 4",
    OrderBy = { "rating desc" },
    Select = { "hotelId", "hotelName", "rating" },
    Size = 10,
    Skip = 0,
    IncludeTotalCount = true
};

SearchResults<Hotel> results = await searchClient.SearchAsync<Hotel>("luxury", options);

Console.WriteLine($"Total: {results.TotalCount}");
await foreach (SearchResult<Hotel> result in results.GetResultsAsync())
{
    Console.WriteLine($"{result.Document.HotelName} (Score: {result.Score})");
}
```

### Faceted 搜尋

```csharp
var options = new SearchOptions
{
    Facets = { "rating,count:5", "category" }
};

var results = await searchClient.SearchAsync<Hotel>("*", options);

foreach (var facet in results.Value.Facets["rating"])
{
    Console.WriteLine($"Rating {facet.Value}: {facet.Count}");
}
```

### 自動完成與建議

```csharp
// Autocomplete
var autocompleteOptions = new AutocompleteOptions { Mode = AutocompleteMode.OneTermWithContext };
var autocomplete = await searchClient.AutocompleteAsync("lux", "suggester-name", autocompleteOptions);

// Suggestions
var suggestOptions = new SuggestOptions { UseFuzzyMatching = true };
var suggestions = await searchClient.SuggestAsync<Hotel>("lux", "suggester-name", suggestOptions);
```

## 向量搜尋

詳細模式請看 [references/vector-search.md](references/vector-search.md)。

```csharp
using Azure.Search.Documents.Models;

// 純向量搜尋
var vectorQuery = new VectorizedQuery(embedding)
{
    KNearestNeighborsCount = 5,
    Fields = { "descriptionVector" }
};

var options = new SearchOptions
{
    VectorSearch = new VectorSearchOptions
    {
        Queries = { vectorQuery }
    }
};

var results = await searchClient.SearchAsync<Hotel>(null, options);
```

## 語意搜尋

詳細模式請看 [references/semantic-search.md](references/semantic-search.md)。

```csharp
var options = new SearchOptions
{
    QueryType = SearchQueryType.Semantic,
    SemanticSearch = new SemanticSearchOptions
    {
        SemanticConfigurationName = "my-semantic-config",
        QueryCaption = new QueryCaption(QueryCaptionType.Extractive),
        QueryAnswer = new QueryAnswer(QueryAnswerType.Extractive)
    }
};

var results = await searchClient.SearchAsync<Hotel>("best hotel for families", options);

// 取得語意 answer
foreach (var answer in results.Value.SemanticSearch.Answers)
{
    Console.WriteLine($"Answer: {answer.Text} (Score: {answer.Score})");
}

// 取得 caption
await foreach (var result in results.Value.GetResultsAsync())
{
    var caption = result.SemanticSearch?.Captions?.FirstOrDefault();
    Console.WriteLine($"Caption: {caption?.Text}");
}
```

## 混合搜尋（向量 + 關鍵字 + 語意）

```csharp
var vectorQuery = new VectorizedQuery(embedding)
{
    KNearestNeighborsCount = 5,
    Fields = { "descriptionVector" }
};

var options = new SearchOptions
{
    QueryType = SearchQueryType.Semantic,
    SemanticSearch = new SemanticSearchOptions
    {
        SemanticConfigurationName = "my-semantic-config"
    },
    VectorSearch = new VectorSearchOptions
    {
        Queries = { vectorQuery }
    }
};

// 結合關鍵字搜尋、向量搜尋和語意排序
var results = await searchClient.SearchAsync<Hotel>("luxury beachfront", options);
```

## 欄位 Attribute 參考

| Attribute | 用途 |
|-----------|---------|
| `SimpleField` | 不可搜尋的欄位（用於 filter、排序、facet） |
| `SearchableField` | 可全文檢索的欄位 |
| `VectorSearchField` | 向量 embedding 欄位 |
| `IsKey = true` | 文件 key（必填，每個 index 一個） |
| `IsFilterable = true` | 啟用 $filter 運算式 |
| `IsSortable = true` | 啟用 $orderby |
| `IsFacetable = true` | 啟用 faceted 導覽 |
| `IsHidden = true` | 從結果中排除 |
| `AnalyzerName` | 指定文字 analyzer |

## 錯誤處理

```csharp
using Azure;

try
{
    var results = await searchClient.SearchAsync<Hotel>("query");
}
catch (RequestFailedException ex) when (ex.Status == 404)
{
    Console.WriteLine("Index not found");
}
catch (RequestFailedException ex)
{
    Console.WriteLine($"Search error: {ex.Status} - {ex.ErrorCode}: {ex.Message}");
}
```

## 最佳實務

1. production 用 **`DefaultAzureCredential`**，不要用 API key
2. 用 **`FieldBuilder`** 搭配 model attribute，讓 index 定義有型別安全
3. 用 **`CreateOrUpdateIndexAsync`** 建立 index，這樣重跑也不會出問題（idempotent）
4. 文件操作用**批次**，吞吐量比較好
5. 用 **`Select`** 只回傳需要的欄位
6. 自然語言查詢要**設定語意搜尋**
7. **向量 + 關鍵字 + 語意搭配使用**，相關性最好

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/vector-search.md](references/vector-search.md) | 向量搜尋、混合搜尋、vectorizer |
| [references/semantic-search.md](references/semantic-search.md) | 語意排序、caption、answer |
