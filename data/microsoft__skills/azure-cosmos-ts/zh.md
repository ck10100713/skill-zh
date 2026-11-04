---
name: azure-cosmos-ts
description: |
  Azure Cosmos DB 的 JavaScript/TypeScript SDK（@azure/cosmos），處理 data plane 操作。用於文件 CRUD、查詢、批次操作和 container 管理。Triggers: "Cosmos DB", "@azure/cosmos", "CosmosClient", "document CRUD", "NoSQL queries", "bulk operations", "partition key", "container.items".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: '@azure/cosmos'
---

# @azure/cosmos (TypeScript/JavaScript)

Azure Cosmos DB NoSQL API 的 data plane SDK，處理文件 CRUD、查詢和批次操作。

> **⚠️ Data plane 與 Management plane 的差別**
> - **這個 SDK (@azure/cosmos)**：文件 CRUD、查詢、stored procedure
> - **Management SDK (@azure/arm-cosmosdb)**：透過 ARM 建立帳號、資料庫、container

## 安裝

```bash
npm install @azure/cosmos @azure/identity
```

**目前版本**：4.9.0  
**Node.js**：>= 20.0.0

## 環境變數

```bash
COSMOS_ENDPOINT=https://<account>.documents.azure.com:443/
COSMOS_DATABASE=<database-name>
COSMOS_CONTAINER=<container-name>
# 只有金鑰驗證才需要（優先用 AAD）
COSMOS_KEY=<account-key>
AZURE_TOKEN_CREDENTIALS=prod # 只有在正式環境使用 DefaultAzureCredential 時才需要
```

## 驗證

### Microsoft Entra Token Credential（建議）

```typescript
import { CosmosClient } from "@azure/cosmos";
import { DefaultAzureCredential, ManagedIdentityCredential } from "@azure/identity";

// 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
const credential = new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]});
// 或是在正式環境直接用特定的 credential：
// 參考 https://learn.microsoft.com/javascript/api/overview/azure/identity-readme?view=azure-node-latest#credential-classes
// const credential = new ManagedIdentityCredential();

const client = new CosmosClient({
  endpoint: process.env.COSMOS_ENDPOINT!,
  aadCredentials: credential,
});
```

### 金鑰驗證

```typescript
import { CosmosClient } from "@azure/cosmos";

// 選項 1：Endpoint + Key
const client = new CosmosClient({
  endpoint: process.env.COSMOS_ENDPOINT!,
  key: process.env.COSMOS_KEY!,
});

// 選項 2：Connection String
const client = new CosmosClient(process.env.COSMOS_CONNECTION_STRING!);
```

## 資源階層

```
CosmosClient
└── Database
    └── Container
        ├── Items (documents)
        ├── Scripts (stored procedures, triggers, UDFs)
        └── Conflicts
```

## 核心操作

### 資料庫與 Container 設定

```typescript
const { database } = await client.databases.createIfNotExists({
  id: "my-database",
});

const { container } = await database.containers.createIfNotExists({
  id: "my-container",
  partitionKey: { paths: ["/partitionKey"] },
});
```

### 建立文件

```typescript
interface Product {
  id: string;
  partitionKey: string;
  name: string;
  price: number;
}

const item: Product = {
  id: "product-1",
  partitionKey: "electronics",
  name: "Laptop",
  price: 999.99,
};

const { resource } = await container.items.create<Product>(item);
```

### 讀取文件

```typescript
const { resource } = await container
  .item("product-1", "electronics") // id, partitionKey
  .read<Product>();

if (resource) {
  console.log(resource.name);
}
```

### 更新文件（Replace）

```typescript
const { resource: existing } = await container
  .item("product-1", "electronics")
  .read<Product>();

if (existing) {
  existing.price = 899.99;
  const { resource: updated } = await container
    .item("product-1", "electronics")
    .replace<Product>(existing);
}
```

### Upsert 文件

```typescript
const item: Product = {
  id: "product-1",
  partitionKey: "electronics",
  name: "Laptop Pro",
  price: 1299.99,
};

const { resource } = await container.items.upsert<Product>(item);
```

### 刪除文件

```typescript
await container.item("product-1", "electronics").delete();
```

### Patch 文件（局部更新）

```typescript
import { PatchOperation } from "@azure/cosmos";

const operations: PatchOperation[] = [
  { op: "replace", path: "/price", value: 799.99 },
  { op: "add", path: "/discount", value: true },
  { op: "remove", path: "/oldField" },
];

const { resource } = await container
  .item("product-1", "electronics")
  .patch<Product>(operations);
```

## 查詢

### 簡單查詢

```typescript
const { resources } = await container.items
  .query<Product>("SELECT * FROM c WHERE c.price < 1000")
  .fetchAll();
```

### 參數化查詢（建議）

```typescript
import { SqlQuerySpec } from "@azure/cosmos";

const querySpec: SqlQuerySpec = {
  query: "SELECT * FROM c WHERE c.partitionKey = @category AND c.price < @maxPrice",
  parameters: [
    { name: "@category", value: "electronics" },
    { name: "@maxPrice", value: 1000 },
  ],
};

const { resources } = await container.items
  .query<Product>(querySpec)
  .fetchAll();
```

### 分頁查詢

```typescript
const queryIterator = container.items.query<Product>(querySpec, {
  maxItemCount: 10, // 每頁幾筆
});

while (queryIterator.hasMoreResults()) {
  const { resources, continuationToken } = await queryIterator.fetchNext();
  console.log(`Page with ${resources?.length} items`);
  // 需要的話，用 continuationToken 取下一頁
}
```

### 跨 Partition 查詢

```typescript
const { resources } = await container.items
  .query<Product>(
    "SELECT * FROM c WHERE c.price > 500",
    { enableCrossPartitionQuery: true }
  )
  .fetchAll();
```

## 批次操作

### 執行批次操作

```typescript
import { BulkOperationType, OperationInput } from "@azure/cosmos";

const operations: OperationInput[] = [
  {
    operationType: BulkOperationType.Create,
    resourceBody: { id: "1", partitionKey: "cat-a", name: "Item 1" },
  },
  {
    operationType: BulkOperationType.Upsert,
    resourceBody: { id: "2", partitionKey: "cat-a", name: "Item 2" },
  },
  {
    operationType: BulkOperationType.Read,
    id: "3",
    partitionKey: "cat-b",
  },
  {
    operationType: BulkOperationType.Replace,
    id: "4",
    partitionKey: "cat-b",
    resourceBody: { id: "4", partitionKey: "cat-b", name: "Updated" },
  },
  {
    operationType: BulkOperationType.Delete,
    id: "5",
    partitionKey: "cat-c",
  },
  {
    operationType: BulkOperationType.Patch,
    id: "6",
    partitionKey: "cat-c",
    resourceBody: {
      operations: [{ op: "replace", path: "/name", value: "Patched" }],
    },
  },
];

const response = await container.items.executeBulkOperations(operations);

response.forEach((result, index) => {
  if (result.statusCode >= 200 && result.statusCode < 300) {
    console.log(`Operation ${index} succeeded`);
  } else {
    console.error(`Operation ${index} failed: ${result.statusCode}`);
  }
});
```

## Partition Key

### 單一 Partition Key

```typescript
const { container } = await database.containers.createIfNotExists({
  id: "products",
  partitionKey: { paths: ["/category"] },
});
```

### 階層式 Partition Key（MultiHash）

```typescript
import { PartitionKeyDefinitionVersion, PartitionKeyKind } from "@azure/cosmos";

const { container } = await database.containers.createIfNotExists({
  id: "orders",
  partitionKey: {
    paths: ["/tenantId", "/userId", "/sessionId"],
    version: PartitionKeyDefinitionVersion.V2,
    kind: PartitionKeyKind.MultiHash,
  },
});

// 操作時要傳入 partition key 值的陣列
const { resource } = await container.items.create({
  id: "order-1",
  tenantId: "tenant-a",
  userId: "user-123",
  sessionId: "session-xyz",
  total: 99.99,
});

// 用階層式 partition key 讀取
const { resource: order } = await container
  .item("order-1", ["tenant-a", "user-123", "session-xyz"])
  .read();
```

## 錯誤處理

```typescript
import { ErrorResponse } from "@azure/cosmos";

try {
  const { resource } = await container.item("missing", "pk").read();
} catch (error) {
  if (error instanceof ErrorResponse) {
    switch (error.code) {
      case 404:
        console.log("Document not found");
        break;
      case 409:
        console.log("Conflict - document already exists");
        break;
      case 412:
        console.log("Precondition failed (ETag mismatch)");
        break;
      case 429:
        console.log("Rate limited - retry after:", error.retryAfterInMs);
        break;
      default:
        console.error(`Cosmos error ${error.code}: ${error.message}`);
    }
  }
  throw error;
}
```

## 樂觀並行控制（ETag）

```typescript
// 連同 ETag 一起讀取
const { resource, etag } = await container
  .item("product-1", "electronics")
  .read<Product>();

if (resource && etag) {
  resource.price = 899.99;
  
  try {
    // 只有 ETag 相符才 replace
    await container.item("product-1", "electronics").replace(resource, {
      accessCondition: { type: "IfMatch", condition: etag },
    });
  } catch (error) {
    if (error instanceof ErrorResponse && error.code === 412) {
      console.log("Document was modified by another process");
    }
  }
}
```

## TypeScript 型別參考

```typescript
import {
  // Client 與資源
  CosmosClient,
  Database,
  Container,
  Item,
  Items,
  
  // 操作
  OperationInput,
  BulkOperationType,
  PatchOperation,
  
  // 查詢
  SqlQuerySpec,
  SqlParameter,
  FeedOptions,
  
  // Partition Key
  PartitionKeyDefinition,
  PartitionKeyDefinitionVersion,
  PartitionKeyKind,
  
  // 回應
  ItemResponse,
  FeedResponse,
  ResourceResponse,
  
  // 錯誤
  ErrorResponse,
} from "@azure/cosmos";
```

## 最佳實務

1. **用 Microsoft Entra Token Credential**：本機開發用 `DefaultAzureCredential`，正式環境用 `ManagedIdentityCredential` 或 `WorkloadIdentityCredential`
2. **一律用參數化查詢**：能防 injection，也有助於 plan 快取
3. **指定 partition key**：盡量避免跨 partition 查詢
4. **用批次操作**：要寫入多筆時用 `executeBulkOperations`
5. **處理 429 錯誤**：實作帶 exponential backoff 的重試邏輯
6. **用 ETag 做並行控制**：避免並行情境下更新被覆蓋
7. **關閉時要關 client**：在清理階段呼叫 `client.dispose()`

## 常見模式

### Service Layer 模式

```typescript
export class ProductService {
  private container: Container;

  constructor(client: CosmosClient) {
    this.container = client
      .database(process.env.COSMOS_DATABASE!)
      .container(process.env.COSMOS_CONTAINER!);
  }

  async getById(id: string, category: string): Promise<Product | null> {
    try {
      const { resource } = await this.container
        .item(id, category)
        .read<Product>();
      return resource ?? null;
    } catch (error) {
      if (error instanceof ErrorResponse && error.code === 404) {
        return null;
      }
      throw error;
    }
  }

  async create(product: Omit<Product, "id">): Promise<Product> {
    const item = { ...product, id: crypto.randomUUID() };
    const { resource } = await this.container.items.create<Product>(item);
    return resource!;
  }

  async findByCategory(category: string): Promise<Product[]> {
    const querySpec: SqlQuerySpec = {
      query: "SELECT * FROM c WHERE c.partitionKey = @category",
      parameters: [{ name: "@category", value: category }],
    };
    const { resources } = await this.container.items
      .query<Product>(querySpec)
      .fetchAll();
    return resources;
  }
}
```

## 相關 SDK

| SDK | 用途 | 安裝 |
|-----|---------|---------|
| `@azure/cosmos` | Data plane（本 SDK） | `npm install @azure/cosmos` |
| `@azure/arm-cosmosdb` | Management plane (ARM) | `npm install @azure/arm-cosmosdb` |
| `@azure/identity` | 驗證 | `npm install @azure/identity` |
