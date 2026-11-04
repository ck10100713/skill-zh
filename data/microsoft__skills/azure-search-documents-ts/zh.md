---
name: azure-search-documents-ts
description: 用 JavaScript 版的 Azure AI Search SDK（@azure/search-documents）建構搜尋應用。用於建立／管理 index、實作向量／混合搜尋、語意排序，或用 knowledge base 做 agentic retrieval。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: '@azure/search-documents'
---

# TypeScript 版 Azure AI Search SDK

建構具備向量、混合和語意搜尋能力的搜尋應用。

## 安裝

```bash
npm install @azure/search-documents @azure/identity
```

## 環境變數

```bash
AZURE_SEARCH_ENDPOINT=https://<service-name>.search.windows.net
AZURE_SEARCH_INDEX_NAME=my-index
AZURE_SEARCH_ADMIN_KEY=<admin-key>  # 用 Entra ID 的話可省略
AZURE_TOKEN_CREDENTIALS=prod # 只有在 production 使用 DefaultAzureCredential 時才需要
```

## 驗證

```typescript
import { SearchClient, SearchIndexClient } from "@azure/search-documents";
import { DefaultAzureCredential, ManagedIdentityCredential } from "@azure/identity";

const endpoint = process.env.AZURE_SEARCH_ENDPOINT!;
const indexName = process.env.AZURE_SEARCH_INDEX_NAME!;
// 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
const credential = new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]});
// 或在 production 直接用特定的 credential：
// See https://learn.microsoft.com/javascript/api/overview/azure/identity-readme?view=azure-node-latest#credential-classes
// const credential = new ManagedIdentityCredential();

// 用於搜尋
const searchClient = new SearchClient(endpoint, indexName, credential);

// 用於 index 管理
const indexClient = new SearchIndexClient(endpoint, credential);
```

## 核心工作流程

### 建立含向量欄位的 Index

```typescript
import { SearchIndex, SearchField, VectorSearch } from "@azure/search-documents";

const index: SearchIndex = {
  name: "products",
  fields: [
    { name: "id", type: "Edm.String", key: true },
    { name: "title", type: "Edm.String", searchable: true },
    { name: "description", type: "Edm.String", searchable: true },
    { name: "category", type: "Edm.String", filterable: true, facetable: true },
    {
      name: "embedding",
      type: "Collection(Edm.Single)",
      searchable: true,
      vectorSearchDimensions: 1536,
      vectorSearchProfileName: "vector-profile",
    },
  ],
  vectorSearch: {
    algorithms: [
      { name: "hnsw-algorithm", kind: "hnsw" },
    ],
    profiles: [
      { name: "vector-profile", algorithmConfigurationName: "hnsw-algorithm" },
    ],
  },
};

await indexClient.createOrUpdateIndex(index);
```

### 為文件建立 Index

```typescript
const documents = [
  { id: "1", title: "Widget", description: "A useful widget", category: "Tools", embedding: [...] },
  { id: "2", title: "Gadget", description: "A cool gadget", category: "Electronics", embedding: [...] },
];

const result = await searchClient.uploadDocuments(documents);
console.log(`Indexed ${result.results.length} documents`);
```

### 全文檢索

```typescript
const results = await searchClient.search("widget", {
  select: ["id", "title", "description"],
  filter: "category eq 'Tools'",
  orderBy: ["title asc"],
  top: 10,
});

for await (const result of results.results) {
  console.log(`${result.document.title}: ${result.score}`);
}
```

### 向量搜尋

```typescript
const queryVector = await getEmbedding("useful tool"); // 你自己的 embedding 函式

const results = await searchClient.search("*", {
  vectorSearchOptions: {
    queries: [
      {
        kind: "vector",
        vector: queryVector,
        fields: ["embedding"],
        kNearestNeighborsCount: 10,
      },
    ],
  },
  select: ["id", "title", "description"],
});

for await (const result of results.results) {
  console.log(`${result.document.title}: ${result.score}`);
}
```

### 混合搜尋（文字 + 向量）

```typescript
const queryVector = await getEmbedding("useful tool");

const results = await searchClient.search("tool", {
  vectorSearchOptions: {
    queries: [
      {
        kind: "vector",
        vector: queryVector,
        fields: ["embedding"],
        kNearestNeighborsCount: 50,
      },
    ],
  },
  select: ["id", "title", "description"],
  top: 10,
});
```

### 語意搜尋

```typescript
// Index 必須有 semantic configuration
const index: SearchIndex = {
  name: "products",
  fields: [...],
  semanticSearch: {
    configurations: [
      {
        name: "semantic-config",
        prioritizedFields: {
          titleField: { name: "title" },
          contentFields: [{ name: "description" }],
        },
      },
    ],
  },
};

// 用語意排序搜尋
const results = await searchClient.search("best tool for the job", {
  queryType: "semantic",
  semanticSearchOptions: {
    configurationName: "semantic-config",
    captions: { captionType: "extractive" },
    answers: { answerType: "extractive", count: 3 },
  },
  select: ["id", "title", "description"],
});

for await (const result of results.results) {
  console.log(`${result.document.title}`);
  console.log(`  Caption: ${result.captions?.[0]?.text}`);
  console.log(`  Reranker Score: ${result.rerankerScore}`);
}
```

## Filter 與 Facet

```typescript
// Filter 語法
const results = await searchClient.search("*", {
  filter: "category eq 'Electronics' and price lt 100",
  facets: ["category,count:10", "brand"],
});

// 取得 facet
for (const [facetName, facetResults] of Object.entries(results.facets || {})) {
  console.log(`${facetName}:`);
  for (const facet of facetResults) {
    console.log(`  ${facet.value}: ${facet.count}`);
  }
}
```

## 自動完成與建議

```typescript
// 在 index 裡建立 suggester
const index: SearchIndex = {
  name: "products",
  fields: [...],
  suggesters: [
    { name: "sg", sourceFields: ["title", "description"] },
  ],
};

// Autocomplete
const autocomplete = await searchClient.autocomplete("wid", "sg", {
  mode: "twoTerms",
  top: 5,
});

// Suggestions
const suggestions = await searchClient.suggest("wid", "sg", {
  select: ["title"],
  top: 5,
});
```

## 批次操作

```typescript
// 批次 upload、merge、delete
const batch = [
  { upload: { id: "1", title: "New Item" } },
  { merge: { id: "2", title: "Updated Title" } },
  { delete: { id: "3" } },
];

const result = await searchClient.indexDocuments({ actions: batch });
```

## 重要型別

```typescript
import {
  SearchClient,
  SearchIndexClient,
  SearchIndexerClient,
  SearchIndex,
  SearchField,
  SearchOptions,
  VectorSearch,
  SemanticSearch,
  SearchIterator,
} from "@azure/search-documents";
```

## 最佳實務

1. **用混合搜尋** - 結合向量 + 文字，結果最好
2. **啟用語意排序** - 提升自然語言查詢的相關性
3. **批次上傳文件** - `uploadDocuments` 傳陣列，不要一份一份傳
4. **用 filter 做安全控管** - 用 filter 實作文件層級的安全性
5. **增量建 index** - 更新用 `mergeOrUploadDocuments`
6. **監控查詢效能** - production 裡少用 `includeTotalCount: true`
