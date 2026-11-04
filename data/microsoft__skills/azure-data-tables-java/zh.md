---
name: azure-data-tables-java
description: 用 Java 版 Azure Tables SDK 建立 table storage 應用程式。處理 Azure Table Storage 或 Cosmos DB Table API 的 NoSQL key-value 資料、無 schema 儲存、大規模結構化資料時使用。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: com.azure:azure-data-tables
---

# Java 版 Azure Tables SDK

用 Java 版 Azure Tables SDK 建立 table storage 應用程式。Azure Table Storage 和 Cosmos DB Table API 都能用。

## 安裝

```xml
<dependency>
  <groupId>com.azure</groupId>
  <artifactId>azure-data-tables</artifactId>
  <version>12.6.0-beta.1</version>
</dependency>
```

## 建立 Client

### 用 Connection String

```java
import com.azure.data.tables.TableServiceClient;
import com.azure.data.tables.TableServiceClientBuilder;
import com.azure.data.tables.TableClient;

TableServiceClient serviceClient = new TableServiceClientBuilder()
    .connectionString("<your-connection-string>")
    .buildClient();
```

### 用 Shared Key

```java
import com.azure.core.credential.AzureNamedKeyCredential;

AzureNamedKeyCredential credential = new AzureNamedKeyCredential(
    "<account-name>",
    "<account-key>");

TableServiceClient serviceClient = new TableServiceClientBuilder()
    .endpoint("<your-table-account-url>")
    .credential(credential)
    .buildClient();
```

### 用 SAS Token

```java
TableServiceClient serviceClient = new TableServiceClientBuilder()
    .endpoint("<your-table-account-url>")
    .sasToken("<sas-token>")
    .buildClient();
```

### 用 DefaultAzureCredential（僅限 Storage）

```java
import com.azure.core.credential.TokenCredential;
import com.azure.identity.AzureIdentityEnvVars;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.identity.ManagedIdentityCredentialBuilder;

// 本機開發：DefaultAzureCredential。正式環境：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
TokenCredential credential = new DefaultAzureCredentialBuilder()
    .requireEnvVars(AzureIdentityEnvVars.AZURE_TOKEN_CREDENTIALS)
    .build();
// 或是在正式環境直接用特定的 credential：
// 參考 https://learn.microsoft.com/java/api/overview/azure/identity-readme?view=azure-java-stable#credential-classes
// TokenCredential credential = new ManagedIdentityCredentialBuilder().build();

TableServiceClient serviceClient = new TableServiceClientBuilder()
    .endpoint("<your-table-account-url>")
    .credential(credential)
    .buildClient();
```

## 關鍵概念

- **TableServiceClient**：管理 table（建立、列出、刪除）
- **TableClient**：管理 table 裡的 entity（CRUD）
- **Partition Key**：把 entity 分組，讓查詢有效率
- **Row Key**：partition 內的唯一識別碼
- **Entity**：一列資料，最多 252 個屬性（Storage 上限 1MB，Cosmos 上限 2MB）

## 核心模式

### 建立 Table

```java
// 建立 table（已存在會丟例外）
TableClient tableClient = serviceClient.createTable("mytable");

// 不存在才建立（不會丟例外）
TableClient tableClient = serviceClient.createTableIfNotExists("mytable");
```

### 取得 Table Client

```java
// 從 service client 取得
TableClient tableClient = serviceClient.getTableClient("mytable");

// 直接建構
TableClient tableClient = new TableClientBuilder()
    .connectionString("<connection-string>")
    .tableName("mytable")
    .buildClient();
```

### 建立 Entity

```java
import com.azure.data.tables.models.TableEntity;

TableEntity entity = new TableEntity("partitionKey", "rowKey")
    .addProperty("Name", "Product A")
    .addProperty("Price", 29.99)
    .addProperty("Quantity", 100)
    .addProperty("IsAvailable", true);

tableClient.createEntity(entity);
```

### 取得 Entity

```java
TableEntity entity = tableClient.getEntity("partitionKey", "rowKey");

String name = (String) entity.getProperty("Name");
Double price = (Double) entity.getProperty("Price");
System.out.printf("Product: %s, Price: %.2f%n", name, price);
```

### 更新 Entity

```java
import com.azure.data.tables.models.TableEntityUpdateMode;

// Merge（只更新指定的屬性）
TableEntity updateEntity = new TableEntity("partitionKey", "rowKey")
    .addProperty("Price", 24.99);
tableClient.updateEntity(updateEntity, TableEntityUpdateMode.MERGE);

// Replace（整個 entity 換掉）
TableEntity replaceEntity = new TableEntity("partitionKey", "rowKey")
    .addProperty("Name", "Product A Updated")
    .addProperty("Price", 24.99)
    .addProperty("Quantity", 150);
tableClient.updateEntity(replaceEntity, TableEntityUpdateMode.REPLACE);
```

### Upsert Entity

```java
// 新增或更新（merge 模式）
tableClient.upsertEntity(entity, TableEntityUpdateMode.MERGE);

// 新增或取代
tableClient.upsertEntity(entity, TableEntityUpdateMode.REPLACE);
```

### 刪除 Entity

```java
tableClient.deleteEntity("partitionKey", "rowKey");
```

### 列出 Entity

```java
import com.azure.data.tables.models.ListEntitiesOptions;

// 列出所有 entity
for (TableEntity entity : tableClient.listEntities()) {
    System.out.printf("%s - %s%n",
        entity.getPartitionKey(),
        entity.getRowKey());
}

// 帶篩選和欄位選取
ListEntitiesOptions options = new ListEntitiesOptions()
    .setFilter("PartitionKey eq 'sales'")
    .setSelect("Name", "Price");

for (TableEntity entity : tableClient.listEntities(options, null, null)) {
    System.out.printf("%s: %.2f%n",
        entity.getProperty("Name"),
        entity.getProperty("Price"));
}
```

### 用 OData Filter 查詢

```java
// 用 partition key 篩選
ListEntitiesOptions options = new ListEntitiesOptions()
    .setFilter("PartitionKey eq 'electronics'");

// 多個條件的篩選
options.setFilter("PartitionKey eq 'electronics' and Price gt 100");

// 用比較運算子篩選
options.setFilter("Quantity ge 10 and Quantity le 100");

// 只取前 N 筆
options.setTop(10);

for (TableEntity entity : tableClient.listEntities(options, null, null)) {
    System.out.println(entity.getRowKey());
}
```

### 批次操作（Transaction）

```java
import com.azure.data.tables.models.TableTransactionAction;
import com.azure.data.tables.models.TableTransactionActionType;
import java.util.Arrays;

// 所有 entity 的 partition key 必須相同
List<TableTransactionAction> actions = Arrays.asList(
    new TableTransactionAction(
        TableTransactionActionType.CREATE,
        new TableEntity("batch", "row1").addProperty("Name", "Item 1")),
    new TableTransactionAction(
        TableTransactionActionType.CREATE,
        new TableEntity("batch", "row2").addProperty("Name", "Item 2")),
    new TableTransactionAction(
        TableTransactionActionType.UPSERT_MERGE,
        new TableEntity("batch", "row3").addProperty("Name", "Item 3"))
);

tableClient.submitTransaction(actions);
```

### 列出 Table

```java
import com.azure.data.tables.models.TableItem;
import com.azure.data.tables.models.ListTablesOptions;

// 列出所有 table
for (TableItem table : serviceClient.listTables()) {
    System.out.println(table.getName());
}

// 篩選 table
ListTablesOptions options = new ListTablesOptions()
    .setFilter("TableName eq 'mytable'");

for (TableItem table : serviceClient.listTables(options, null, null)) {
    System.out.println(table.getName());
}
```

### 刪除 Table

```java
serviceClient.deleteTable("mytable");
```

## 具型別的 Entity

```java
public class Product implements TableEntity {
    private String partitionKey;
    private String rowKey;
    private OffsetDateTime timestamp;
    private String eTag;
    private String name;
    private double price;
    
    // 所有欄位的 getter 和 setter
    @Override
    public String getPartitionKey() { return partitionKey; }
    @Override
    public void setPartitionKey(String partitionKey) { this.partitionKey = partitionKey; }
    @Override
    public String getRowKey() { return rowKey; }
    @Override
    public void setRowKey(String rowKey) { this.rowKey = rowKey; }
    // ... 其他 getter/setter
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; }
}

// 用法
Product product = new Product();
product.setPartitionKey("electronics");
product.setRowKey("laptop-001");
product.setName("Laptop");
product.setPrice(999.99);

tableClient.createEntity(product);
```

## 錯誤處理

```java
import com.azure.data.tables.models.TableServiceException;

try {
    tableClient.createEntity(entity);
} catch (TableServiceException e) {
    System.out.println("Status: " + e.getResponse().getStatusCode());
    System.out.println("Error: " + e.getMessage());
    // 409 = Conflict（entity 已存在）
    // 404 = Not Found
}
```

## 環境變數

```bash
# Storage Account
AZURE_TABLES_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...  # Entra ID 驗證的替代方案
AZURE_TABLES_ENDPOINT=https://<account>.table.core.windows.net  # 所有驗證方式都必須設定
AZURE_TOKEN_CREDENTIALS=prod  # 只有在正式環境使用 DefaultAzureCredential 時才需要

# Cosmos DB Table API
COSMOS_TABLE_ENDPOINT=https://<account>.table.cosmosdb.azure.com  # Cosmos DB Table API 用的替代 endpoint
```

## 最佳實務

1. **Partition Key 設計**：選能讓負載平均分散的 key
2. **批次操作**：要原子更新多個 entity 時用 transaction
3. **查詢最佳化**：盡量一律用 PartitionKey 篩選
4. **選取投影**：為了效能，只選需要的屬性
5. **Entity 大小**：Storage 控制在 1MB 以下，Cosmos 控制在 2MB 以下

## 觸發詞

- "Azure Tables Java"
- "table storage SDK"
- "Cosmos DB Table API"
- "NoSQL key-value storage"
- "partition key row key"
- "table entity CRUD"
