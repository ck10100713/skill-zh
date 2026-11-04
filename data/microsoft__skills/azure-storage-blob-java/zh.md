---
name: azure-storage-blob-java
description: 用 Java 版的 Azure Storage Blob SDK 建構 blob 儲存應用。用於在 Azure Blob Storage 上傳、下載或管理檔案、操作 container，或實作串流資料操作。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: com.azure:azure-storage-blob
---

# Java 版 Azure Storage Blob SDK

用 Java 版的 Azure Storage Blob SDK 建構 blob 儲存應用。

## 安裝

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-storage-blob</artifactId>
    <version>12.33.0</version>
</dependency>
```

## 建立 Client

### BlobServiceClient

```java
import com.azure.storage.blob.BlobServiceClient;
import com.azure.storage.blob.BlobServiceClientBuilder;

// 用 SAS token
BlobServiceClient serviceClient = new BlobServiceClientBuilder()
    .endpoint("<storage-account-url>")
    .sasToken("<sas-token>")
    .buildClient();

// 用 connection string
BlobServiceClient serviceClient = new BlobServiceClientBuilder()
    .connectionString("<connection-string>")
    .buildClient();
```

### 搭配 DefaultAzureCredential

```java
import com.azure.core.credential.TokenCredential;
import com.azure.identity.AzureIdentityEnvVars;
import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.identity.ManagedIdentityCredentialBuilder;

// 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
TokenCredential credential = new DefaultAzureCredentialBuilder()
    .requireEnvVars(AzureIdentityEnvVars.AZURE_TOKEN_CREDENTIALS)
    .build();
// 或在 production 直接用特定的 credential：
// See https://learn.microsoft.com/java/api/overview/azure/identity-readme?view=azure-java-stable#credential-classes
// TokenCredential credential = new ManagedIdentityCredentialBuilder().build();

BlobServiceClient serviceClient = new BlobServiceClientBuilder()
    .endpoint("<storage-account-url>")
    .credential(credential)
    .buildClient();
```

### BlobContainerClient

```java
import com.azure.storage.blob.BlobContainerClient;

// 從 service client 取得
BlobContainerClient containerClient = serviceClient.getBlobContainerClient("mycontainer");

// 直接建構
BlobContainerClient containerClient = new BlobContainerClientBuilder()
    .connectionString("<connection-string>")
    .containerName("mycontainer")
    .buildClient();
```

### BlobClient

```java
import com.azure.storage.blob.BlobClient;

// 從 container client 取得
BlobClient blobClient = containerClient.getBlobClient("myblob.txt");

// 含目錄結構
BlobClient blobClient = containerClient.getBlobClient("folder/subfolder/myblob.txt");

// 直接建構
BlobClient blobClient = new BlobClientBuilder()
    .connectionString("<connection-string>")
    .containerName("mycontainer")
    .blobName("myblob.txt")
    .buildClient();
```

## 核心模式

### 建立 Container

```java
// 建立 container
serviceClient.createBlobContainer("mycontainer");

// 不存在才建立
BlobContainerClient container = serviceClient.createBlobContainerIfNotExists("mycontainer");

// 從 container client 建立
containerClient.create();
containerClient.createIfNotExists();
```

### 上傳資料

```java
import com.azure.core.util.BinaryData;

// 上傳字串
String data = "Hello, Azure Blob Storage!";
blobClient.upload(BinaryData.fromString(data));

// 上傳並允許覆寫
blobClient.upload(BinaryData.fromString(data), true);
```

### 從檔案上傳

```java
blobClient.uploadFromFile("local-file.txt");

// 允許覆寫
blobClient.uploadFromFile("local-file.txt", true);
```

### 從 Stream 上傳

```java
import com.azure.storage.blob.specialized.BlockBlobClient;

BlockBlobClient blockBlobClient = blobClient.getBlockBlobClient();

try (ByteArrayInputStream dataStream = new ByteArrayInputStream(data.getBytes())) {
    blockBlobClient.upload(dataStream, data.length());
}
```

### 帶選項上傳

```java
import com.azure.storage.blob.models.BlobHttpHeaders;
import com.azure.storage.blob.options.BlobParallelUploadOptions;

BlobHttpHeaders headers = new BlobHttpHeaders()
    .setContentType("text/plain")
    .setCacheControl("max-age=3600");

Map<String, String> metadata = Map.of("author", "john", "version", "1.0");

try (InputStream stream = new FileInputStream("large-file.bin")) {
    BlobParallelUploadOptions options = new BlobParallelUploadOptions(stream)
        .setHeaders(headers)
        .setMetadata(metadata);
    
    blobClient.uploadWithResponse(options, null, Context.NONE);
}
```

### 不存在才上傳

```java
import com.azure.storage.blob.models.BlobRequestConditions;

BlobParallelUploadOptions options = new BlobParallelUploadOptions(inputStream, length)
    .setRequestConditions(new BlobRequestConditions().setIfNoneMatch("*"));

blobClient.uploadWithResponse(options, null, Context.NONE);
```

### 下載資料

```java
// 下載成 BinaryData
BinaryData content = blobClient.downloadContent();
String text = content.toString();

// 下載到檔案
blobClient.downloadToFile("downloaded-file.txt");
```

### 下載到 Stream

```java
try (ByteArrayOutputStream outputStream = new ByteArrayOutputStream()) {
    blobClient.downloadStream(outputStream);
    byte[] data = outputStream.toByteArray();
}
```

### 用 InputStream 下載

```java
import com.azure.storage.blob.specialized.BlobInputStream;

try (BlobInputStream blobIS = blobClient.openInputStream()) {
    byte[] buffer = new byte[1024];
    int bytesRead;
    while ((bytesRead = blobIS.read(buffer)) != -1) {
        // 處理 buffer
    }
}
```

### 透過 OutputStream 上傳

```java
import com.azure.storage.blob.specialized.BlobOutputStream;

try (BlobOutputStream blobOS = blobClient.getBlockBlobClient().getBlobOutputStream()) {
    blobOS.write("Data to upload".getBytes());
}
```

### 列出 Blob

```java
import com.azure.storage.blob.models.BlobItem;

// 列出所有 blob
for (BlobItem blobItem : containerClient.listBlobs()) {
    System.out.println("Blob: " + blobItem.getName());
}

// 用 prefix 列出（虛擬目錄）
import com.azure.storage.blob.models.ListBlobsOptions;

ListBlobsOptions options = new ListBlobsOptions().setPrefix("folder/");
for (BlobItem blobItem : containerClient.listBlobs(options, null)) {
    System.out.println("Blob: " + blobItem.getName());
}
```

### 依階層列出 Blob

```java
import com.azure.storage.blob.models.BlobListDetails;

String delimiter = "/";
ListBlobsOptions options = new ListBlobsOptions()
    .setPrefix("data/")
    .setDetails(new BlobListDetails().setRetrieveMetadata(true));

for (BlobItem item : containerClient.listBlobsByHierarchy(delimiter, options, null)) {
    if (item.isPrefix()) {
        System.out.println("Directory: " + item.getName());
    } else {
        System.out.println("Blob: " + item.getName());
    }
}
```

### 刪除 Blob

```java
blobClient.delete();

// 存在才刪除
blobClient.deleteIfExists();

// 連同 snapshot 一起刪除
import com.azure.storage.blob.models.DeleteSnapshotsOptionType;
blobClient.deleteWithResponse(DeleteSnapshotsOptionType.INCLUDE, null, null, Context.NONE);
```

### 複製 Blob

```java
import com.azure.storage.blob.models.BlobCopyInfo;
import com.azure.core.util.polling.SyncPoller;

// 非同步複製（大型 blob 或跨 account）
SyncPoller<BlobCopyInfo, Void> poller = blobClient.beginCopy("<source-blob-url>", Duration.ofSeconds(1));
poller.waitForCompletion();

// 從 URL 同步複製（同一個 account）
blobClient.copyFromUrl("<source-blob-url>");
```

### 產生 SAS Token

```java
import com.azure.storage.blob.sas.*;
import java.time.OffsetDateTime;

// Blob 層級的 SAS
BlobSasPermission permissions = new BlobSasPermission().setReadPermission(true);
OffsetDateTime expiry = OffsetDateTime.now().plusDays(1);

BlobServiceSasSignatureValues sasValues = new BlobServiceSasSignatureValues(expiry, permissions);
String sasToken = blobClient.generateSas(sasValues);

// Container 層級的 SAS
BlobContainerSasPermission containerPermissions = new BlobContainerSasPermission()
    .setReadPermission(true)
    .setListPermission(true);
    
BlobServiceSasSignatureValues containerSasValues = new BlobServiceSasSignatureValues(expiry, containerPermissions);
String containerSas = containerClient.generateSas(containerSasValues);
```

### Blob 屬性與 Metadata

```java
import com.azure.storage.blob.models.BlobProperties;

// 取得屬性
BlobProperties properties = blobClient.getProperties();
System.out.println("Size: " + properties.getBlobSize());
System.out.println("Content-Type: " + properties.getContentType());
System.out.println("Last Modified: " + properties.getLastModified());

// 設定 metadata
Map<String, String> metadata = Map.of("key1", "value1", "key2", "value2");
blobClient.setMetadata(metadata);

// 設定 HTTP header
BlobHttpHeaders headers = new BlobHttpHeaders()
    .setContentType("application/json")
    .setCacheControl("max-age=86400");
blobClient.setHttpHeaders(headers);
```

### Blob Lease

```java
import com.azure.storage.blob.specialized.BlobLeaseClient;
import com.azure.storage.blob.specialized.BlobLeaseClientBuilder;

BlobLeaseClient leaseClient = new BlobLeaseClientBuilder()
    .blobClient(blobClient)
    .buildClient();

// 取得 lease（-1 表示無限期）
String leaseId = leaseClient.acquireLease(60);

// 續期 lease
leaseClient.renewLease();

// 釋放 lease
leaseClient.releaseLease();
```

## 錯誤處理

```java
import com.azure.storage.blob.models.BlobStorageException;

try {
    blobClient.download(outputStream);
} catch (BlobStorageException e) {
    System.out.println("Status: " + e.getStatusCode());
    System.out.println("Error code: " + e.getErrorCode());
    // 404 = 找不到 blob
    // 409 = 衝突（lease 等）
}
```

## Proxy 設定

```java
import com.azure.core.http.ProxyOptions;
import com.azure.core.http.netty.NettyAsyncHttpClientBuilder;
import java.net.InetSocketAddress;

ProxyOptions proxyOptions = new ProxyOptions(
    ProxyOptions.Type.HTTP,
    new InetSocketAddress("localhost", 8888));

BlobServiceClient client = new BlobServiceClientBuilder()
    .endpoint("<endpoint>")
    .sasToken("<sas-token>")
    .httpClient(new NettyAsyncHttpClientBuilder().proxy(proxyOptions).build())
    .buildClient();
```

## 環境變數

```bash
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...  # Entra ID 驗證的替代方案
AZURE_STORAGE_ACCOUNT_URL=https://<account>.blob.core.windows.net  # 所有驗證方式都必填
AZURE_TOKEN_CREDENTIALS=prod  # 只有在 production 使用 DefaultAzureCredential 時才需要
```

## 觸發用語

- "Azure Blob Storage Java"
- "upload download blob"
- "blob container SDK"
- "storage streaming"
- "SAS token generation"
- "blob metadata properties"
