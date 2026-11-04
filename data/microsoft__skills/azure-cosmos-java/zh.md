---
name: azure-cosmos-java
description: |
  Azure Cosmos DB SDK for Java。NoSQL 資料庫操作，支援全球分散、多模型和 reactive 模式。
  Triggers: "CosmosClient java", "CosmosAsyncClient", "cosmos database java", "cosmosdb java", "document database java".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: azure-cosmos
---

# Azure Cosmos DB SDK for Java

Azure Cosmos DB NoSQL API 的 client library，支援全球分散和 reactive 模式。

## Installation

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-cosmos</artifactId>
    <version>LATEST</version>
</dependency>
```

或使用 Azure SDK BOM：

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.azure</groupId>
            <artifactId>azure-sdk-bom</artifactId>
            <version>{bom_version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <dependency>
        <groupId>com.azure</groupId>
        <artifactId>azure-cosmos</artifactId>
    </dependency>
</dependencies>
```

## Environment Variables

```bash
COSMOS_ENDPOINT=https://<account>.documents.azure.com:443/
COSMOS_KEY=<your-primary-key>
```

## Authentication

### Key-based Authentication

```java
import com.azure.cosmos.CosmosClient;
import com.azure.cosmos.CosmosClientBuilder;

CosmosClient client = new CosmosClientBuilder()
    .endpoint(System.getenv("COSMOS_ENDPOINT"))
    .key(System.getenv("COSMOS_KEY"))
    .buildClient();
```

### Async Client

```java
import com.azure.cosmos.CosmosAsyncClient;

CosmosAsyncClient asyncClient = new CosmosClientBuilder()
    .endpoint(serviceEndpoint)
    .key(key)
    .buildAsyncClient();
```

### With Customizations

```java
import com.azure.cosmos.ConsistencyLevel;
import java.util.Arrays;

CosmosClient client = new CosmosClientBuilder()
    .endpoint(serviceEndpoint)
    .key(key)
    .directMode(directConnectionConfig, gatewayConnectionConfig)
    .consistencyLevel(ConsistencyLevel.SESSION)
    .connectionSharingAcrossClientsEnabled(true)
    .contentResponseOnWriteEnabled(true)
    .userAgentSuffix("my-application")
    .preferredRegions(Arrays.asList("West US", "East US"))
    .buildClient();
```

## Client Hierarchy

| Class | Purpose |
|-------|---------|
| `CosmosClient` / `CosmosAsyncClient` | 帳號層級的操作 |
| `CosmosDatabase` / `CosmosAsyncDatabase` | 資料庫操作 |
| `CosmosContainer` / `CosmosAsyncContainer` | Container/item 操作 |

## Core Workflow

### Create Database

```java
// 同步
client.createDatabaseIfNotExists("myDatabase")
    .map(response -> client.getDatabase(response.getProperties().getId()));

// 非同步，串接
asyncClient.createDatabaseIfNotExists("myDatabase")
    .map(response -> asyncClient.getDatabase(response.getProperties().getId()))
    .subscribe(database -> System.out.println("Created: " + database.getId()));
```

### Create Container

```java
asyncClient.createDatabaseIfNotExists("myDatabase")
    .flatMap(dbResponse -> {
        String databaseId = dbResponse.getProperties().getId();
        return asyncClient.getDatabase(databaseId)
            .createContainerIfNotExists("myContainer", "/partitionKey")
            .map(containerResponse -> asyncClient.getDatabase(databaseId)
                .getContainer(containerResponse.getProperties().getId()));
    })
    .subscribe(container -> System.out.println("Container: " + container.getId()));
```

### CRUD Operations

```java
import com.azure.cosmos.models.PartitionKey;

CosmosAsyncContainer container = asyncClient
    .getDatabase("myDatabase")
    .getContainer("myContainer");

// Create
container.createItem(new User("1", "John Doe", "john@example.com"))
    .flatMap(response -> {
        System.out.println("Created: " + response.getItem());
        // Read
        return container.readItem(
            response.getItem().getId(),
            new PartitionKey(response.getItem().getId()),
            User.class);
    })
    .flatMap(response -> {
        System.out.println("Read: " + response.getItem());
        // Update
        User user = response.getItem();
        user.setEmail("john.doe@example.com");
        return container.replaceItem(
            user,
            user.getId(),
            new PartitionKey(user.getId()));
    })
    .flatMap(response -> {
        // Delete
        return container.deleteItem(
            response.getItem().getId(),
            new PartitionKey(response.getItem().getId()));
    })
    .block();
```

### Query Documents

```java
import com.azure.cosmos.models.CosmosQueryRequestOptions;
import com.azure.cosmos.util.CosmosPagedIterable;

CosmosContainer container = client.getDatabase("myDatabase").getContainer("myContainer");

String query = "SELECT * FROM c WHERE c.status = @status";
CosmosQueryRequestOptions options = new CosmosQueryRequestOptions();

CosmosPagedIterable<User> results = container.queryItems(
    query,
    options,
    User.class
);

results.forEach(user -> System.out.println("User: " + user.getName()));
```

## Key Concepts

### Partition Keys

選擇 partition key 時要符合：
- 基數高（很多不同的值）
- 資料和請求分佈均勻
- 常用在查詢裡

### Consistency Levels

| Level | Guarantee |
|-------|-----------|
| Strong | 線性一致性 |
| Bounded Staleness | 一致的前綴，延遲有上限 |
| Session | session 內一致的前綴 |
| Consistent Prefix | 讀取永遠不會看到順序錯亂的寫入 |
| Eventual | 不保證順序 |

### Request Units (RUs)

所有操作都會消耗 RU。檢查回應 header：

```java
CosmosItemResponse<User> response = container.createItem(user);
System.out.println("RU charge: " + response.getRequestCharge());
```

## Best Practices

1. **重複使用 CosmosClient**：建立一次，整個應用程式都共用
2. **高吞吐量情境用非同步 client**
3. **謹慎選擇 partition key**：會影響效能和擴充性
4. **開啟寫入時回傳內容**，才能立即取得剛建立的 item
5. **為地理分散的應用程式設定 preferred regions**
6. **用重試政策處理 429 錯誤**（預設已內建）
7. **production 用 direct mode**，延遲最低

## Error Handling

```java
import com.azure.cosmos.CosmosException;

try {
    container.createItem(item);
} catch (CosmosException e) {
    System.err.println("Status: " + e.getStatusCode());
    System.err.println("Message: " + e.getMessage());
    System.err.println("Request charge: " + e.getRequestCharge());
    
    if (e.getStatusCode() == 409) {
        System.err.println("Item already exists");
    } else if (e.getStatusCode() == 429) {
        System.err.println("Rate limited, retry after: " + e.getRetryAfterDuration());
    }
}
```

## Reference Links

| Resource | URL |
|----------|-----|
| Maven Package | https://central.sonatype.com/artifact/com.azure/azure-cosmos |
| API Documentation | https://azuresdkdocs.z19.web.core.windows.net/java/azure-cosmos/latest/index.html |
| Product Docs | https://learn.microsoft.com/azure/cosmos-db/ |
| Samples | https://github.com/Azure-Samples/azure-cosmos-java-sql-api-samples |
| Performance Guide | https://learn.microsoft.com/azure/cosmos-db/performance-tips-java-sdk-v4-sql |
| Troubleshooting | https://learn.microsoft.com/azure/cosmos-db/troubleshoot-java-sdk-v4-sql |
