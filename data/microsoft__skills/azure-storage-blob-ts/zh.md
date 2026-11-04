---
name: azure-storage-blob-ts
description: |
  用於 blob 操作的 Azure Blob Storage JavaScript/TypeScript SDK（@azure/storage-blob）。用於上傳、下載、列出並管理 blob 和 container。支援 block blob、append blob、page blob、SAS token 和串流。Triggers: "blob storage", "@azure/storage-blob", "BlobServiceClient", "ContainerClient", "upload blob", "download blob", "SAS token", "block blob".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: '@azure/storage-blob'
---

# @azure/storage-blob (TypeScript/JavaScript)

Azure Blob Storage 操作的 SDK，可上傳、下載、列出並管理 blob 和 container。

## 安裝

```bash
npm install @azure/storage-blob @azure/identity
```

**目前版本**：12.x  
**Node.js**：>= 18.0.0

## 環境變數

```bash
AZURE_STORAGE_ACCOUNT_NAME=<account-name>
AZURE_STORAGE_ACCOUNT_KEY=<account-key>
# 或用 connection string
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
AZURE_TOKEN_CREDENTIALS=prod # 只有在 production 使用 DefaultAzureCredential 時才需要
```

## 驗證

### Microsoft Entra Token Credential（建議）

```typescript
import { BlobServiceClient } from "@azure/storage-blob";
import { DefaultAzureCredential, ManagedIdentityCredential } from "@azure/identity";

// 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
const credential = new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]});
// 或在 production 直接用特定的 credential：
// See https://learn.microsoft.com/javascript/api/overview/azure/identity-readme?view=azure-node-latest#credential-classes
// const credential = new ManagedIdentityCredential();

const accountName = process.env.AZURE_STORAGE_ACCOUNT_NAME!;
const client = new BlobServiceClient(
  `https://${accountName}.blob.core.windows.net`,
  credential
);
```

### Connection String

```typescript
import { BlobServiceClient } from "@azure/storage-blob";

const client = BlobServiceClient.fromConnectionString(
  process.env.AZURE_STORAGE_CONNECTION_STRING!
);
```

### StorageSharedKeyCredential（僅限 Node.js）

```typescript
import { BlobServiceClient, StorageSharedKeyCredential } from "@azure/storage-blob";

const accountName = process.env.AZURE_STORAGE_ACCOUNT_NAME!;
const accountKey = process.env.AZURE_STORAGE_ACCOUNT_KEY!;

const sharedKeyCredential = new StorageSharedKeyCredential(accountName, accountKey);
const client = new BlobServiceClient(
  `https://${accountName}.blob.core.windows.net`,
  sharedKeyCredential
);
```

### SAS Token

```typescript
import { BlobServiceClient } from "@azure/storage-blob";

const accountName = process.env.AZURE_STORAGE_ACCOUNT_NAME!;
const sasToken = process.env.AZURE_STORAGE_SAS_TOKEN!; // 以 "?" 開頭

const client = new BlobServiceClient(
  `https://${accountName}.blob.core.windows.net${sasToken}`
);
```

## Client 階層

```
BlobServiceClient (account level)
└── ContainerClient (container level)
    └── BlobClient (blob level)
        ├── BlockBlobClient (block blobs - most common)
        ├── AppendBlobClient (append-only blobs)
        └── PageBlobClient (page blobs - VHDs)
```

## Container 操作

### 建立 Container

```typescript
const containerClient = client.getContainerClient("my-container");
await containerClient.create();

// 或不存在才建立
await containerClient.createIfNotExists();
```

### 列出 Container

```typescript
for await (const container of client.listContainers()) {
  console.log(container.name);
}

// 用 prefix 篩選
for await (const container of client.listContainers({ prefix: "logs-" })) {
  console.log(container.name);
}
```

### 刪除 Container

```typescript
await containerClient.delete();
// 或存在才刪除
await containerClient.deleteIfExists();
```

## Blob 操作

### 上傳 Blob（簡單版）

```typescript
const containerClient = client.getContainerClient("my-container");
const blockBlobClient = containerClient.getBlockBlobClient("my-file.txt");

// 上傳字串
await blockBlobClient.upload("Hello, World!", 13);

// 上傳 Buffer
const buffer = Buffer.from("Hello, World!");
await blockBlobClient.upload(buffer, buffer.length);
```

### 從檔案上傳（僅限 Node.js）

```typescript
const blockBlobClient = containerClient.getBlockBlobClient("uploaded-file.txt");
await blockBlobClient.uploadFile("/path/to/local/file.txt");
```

### 從 Stream 上傳（僅限 Node.js）

```typescript
import * as fs from "fs";

const blockBlobClient = containerClient.getBlockBlobClient("streamed-file.txt");
const readStream = fs.createReadStream("/path/to/local/file.txt");

await blockBlobClient.uploadStream(readStream, 4 * 1024 * 1024, 5, {
  // bufferSize: 4MB, maxConcurrency: 5
  onProgress: (progress) => console.log(`Uploaded ${progress.loadedBytes} bytes`),
});
```

### 從瀏覽器上傳

```typescript
const blockBlobClient = containerClient.getBlockBlobClient("browser-upload.txt");

// 從 File input
const fileInput = document.getElementById("fileInput") as HTMLInputElement;
const file = fileInput.files![0];
await blockBlobClient.uploadData(file);

// 從 Blob/ArrayBuffer
const arrayBuffer = new ArrayBuffer(1024);
await blockBlobClient.uploadData(arrayBuffer);
```

### 下載 Blob

```typescript
const blobClient = containerClient.getBlobClient("my-file.txt");
const downloadResponse = await blobClient.download();

// 讀成字串（瀏覽器和 Node.js 都適用）
const downloaded = await streamToText(downloadResponse.readableStreamBody!);

async function streamToText(readable: NodeJS.ReadableStream): Promise<string> {
  const chunks: Buffer[] = [];
  for await (const chunk of readable) {
    chunks.push(Buffer.from(chunk));
  }
  return Buffer.concat(chunks).toString("utf-8");
}
```

### 下載到檔案（僅限 Node.js）

```typescript
const blockBlobClient = containerClient.getBlockBlobClient("my-file.txt");
await blockBlobClient.downloadToFile("/path/to/local/destination.txt");
```

### 下載到 Buffer（僅限 Node.js）

```typescript
const blockBlobClient = containerClient.getBlockBlobClient("my-file.txt");
const buffer = await blockBlobClient.downloadToBuffer();
console.log(buffer.toString());
```

### 列出 Blob

```typescript
// 列出所有 blob
for await (const blob of containerClient.listBlobsFlat()) {
  console.log(blob.name, blob.properties.contentLength);
}

// 用 prefix 列出
for await (const blob of containerClient.listBlobsFlat({ prefix: "logs/" })) {
  console.log(blob.name);
}

// 依階層列出（虛擬目錄）
for await (const item of containerClient.listBlobsByHierarchy("/")) {
  if (item.kind === "prefix") {
    console.log(`Directory: ${item.name}`);
  } else {
    console.log(`Blob: ${item.name}`);
  }
}
```

### 刪除 Blob

```typescript
const blobClient = containerClient.getBlobClient("my-file.txt");
await blobClient.delete();

// 存在才刪除
await blobClient.deleteIfExists();

// 連同 snapshot 一起刪除
await blobClient.delete({ deleteSnapshots: "include" });
```

### 複製 Blob

```typescript
const sourceBlobClient = containerClient.getBlobClient("source.txt");
const destBlobClient = containerClient.getBlobClient("destination.txt");

// 開始複製操作
const copyPoller = await destBlobClient.beginCopyFromURL(sourceBlobClient.url);
await copyPoller.pollUntilDone();
```

## Blob 屬性與 Metadata

### 取得屬性

```typescript
const blobClient = containerClient.getBlobClient("my-file.txt");
const properties = await blobClient.getProperties();

console.log("Content-Type:", properties.contentType);
console.log("Content-Length:", properties.contentLength);
console.log("Last Modified:", properties.lastModified);
console.log("ETag:", properties.etag);
```

### 設定 Metadata

```typescript
await blobClient.setMetadata({
  author: "John Doe",
  category: "documents",
});
```

### 設定 HTTP Header

```typescript
await blobClient.setHTTPHeaders({
  blobContentType: "text/plain",
  blobCacheControl: "max-age=3600",
  blobContentDisposition: "attachment; filename=download.txt",
});
```

## 產生 SAS Token（僅限 Node.js）

### 產生 Blob SAS

```typescript
import {
  BlobSASPermissions,
  generateBlobSASQueryParameters,
  StorageSharedKeyCredential,
} from "@azure/storage-blob";

const sharedKeyCredential = new StorageSharedKeyCredential(accountName, accountKey);

const sasToken = generateBlobSASQueryParameters(
  {
    containerName: "my-container",
    blobName: "my-file.txt",
    permissions: BlobSASPermissions.parse("r"), // 唯讀
    startsOn: new Date(),
    expiresOn: new Date(Date.now() + 3600 * 1000), // 1 小時
  },
  sharedKeyCredential
).toString();

const sasUrl = `https://${accountName}.blob.core.windows.net/my-container/my-file.txt?${sasToken}`;
```

### 產生 Container SAS

```typescript
import { ContainerSASPermissions, generateBlobSASQueryParameters } from "@azure/storage-blob";

const sasToken = generateBlobSASQueryParameters(
  {
    containerName: "my-container",
    permissions: ContainerSASPermissions.parse("racwdl"), // read, add, create, write, delete, list
    expiresOn: new Date(Date.now() + 24 * 3600 * 1000), // 24 小時
  },
  sharedKeyCredential
).toString();
```

### 產生 Account SAS

```typescript
import {
  AccountSASPermissions,
  AccountSASResourceTypes,
  AccountSASServices,
  generateAccountSASQueryParameters,
} from "@azure/storage-blob";

const sasToken = generateAccountSASQueryParameters(
  {
    services: AccountSASServices.parse("b").toString(), // blob
    resourceTypes: AccountSASResourceTypes.parse("sco").toString(), // service, container, object
    permissions: AccountSASPermissions.parse("rwdlacupi"), // 所有權限
    expiresOn: new Date(Date.now() + 24 * 3600 * 1000),
  },
  sharedKeyCredential
).toString();
```

## Blob 類型

### Block Blob（預設）

文字和二進位檔最常用的類型。

```typescript
const blockBlobClient = containerClient.getBlockBlobClient("document.pdf");
await blockBlobClient.uploadFile("/path/to/document.pdf");
```

### Append Blob

為 append 操作（log、稽核軌跡）最佳化。

```typescript
const appendBlobClient = containerClient.getAppendBlobClient("app.log");

// 建立 append blob
await appendBlobClient.create();

// 附加資料
await appendBlobClient.appendBlock("Log entry 1\n", 12);
await appendBlobClient.appendBlock("Log entry 2\n", 12);
```

### Page Blob

固定大小的 blob，用於隨機讀寫（VHD）。

```typescript
const pageBlobClient = containerClient.getPageBlobClient("disk.vhd");

// 建立 512-byte 對齊的 page blob
await pageBlobClient.create(1024 * 1024); // 1MB

// 寫入 page（必須 512-byte 對齊）
const buffer = Buffer.alloc(512);
await pageBlobClient.uploadPages(buffer, 0, 512);
```

## 錯誤處理

```typescript
import { RestError } from "@azure/storage-blob";

try {
  await containerClient.create();
} catch (error) {
  if (error instanceof RestError) {
    switch (error.statusCode) {
      case 404:
        console.log("Container not found");
        break;
      case 409:
        console.log("Container already exists");
        break;
      case 403:
        console.log("Access denied");
        break;
      default:
        console.error(`Storage error ${error.statusCode}: ${error.message}`);
    }
  }
  throw error;
}
```

## TypeScript 型別參考

```typescript
import {
  // Clients
  BlobServiceClient,
  ContainerClient,
  BlobClient,
  BlockBlobClient,
  AppendBlobClient,
  PageBlobClient,

  // Authentication
  StorageSharedKeyCredential,
  AnonymousCredential,

  // SAS
  BlobSASPermissions,
  ContainerSASPermissions,
  AccountSASPermissions,
  AccountSASServices,
  AccountSASResourceTypes,
  generateBlobSASQueryParameters,
  generateAccountSASQueryParameters,

  // Options & Responses
  BlobDownloadResponseParsed,
  BlobUploadCommonResponse,
  ContainerCreateResponse,
  BlobItem,
  ContainerItem,

  // Errors
  RestError,
} from "@azure/storage-blob";
```

## 最佳實務

1. **本機開發用 `DefaultAzureCredential`；production 用 `ManagedIdentityCredential` 或 `WorkloadIdentityCredential`**
2. **大檔案用串流** — 超過 256MB 的檔案用 `uploadStream`/`downloadToFile`
3. **設定適當的 content type** — 用 `setHTTPHeaders` 設定正確的 MIME type
4. **client 存取用 SAS token** — 為瀏覽器上傳產生短效期的 token
5. **妥善處理錯誤** — 檢查 `RestError.statusCode` 做對應處理
6. **用 `*IfNotExists` 方法** — 讓 container/blob 的建立可以重複執行（idempotent）
7. **關閉 client** — 不是必要，但在長時間執行的應用程式裡是好習慣

## 平台差異

| 功能 | Node.js | 瀏覽器 |
|---------|---------|---------|
| `StorageSharedKeyCredential` | ✅ | ❌ |
| `uploadFile()` | ✅ | ❌ |
| `uploadStream()` | ✅ | ❌ |
| `downloadToFile()` | ✅ | ❌ |
| `downloadToBuffer()` | ✅ | ❌ |
| `uploadData()` | ✅ | ✅ |
| SAS 產生 | ✅ | ❌ |
| DefaultAzureCredential | ✅ | ❌ |
| Anonymous/SAS 存取 | ✅ | ✅ |
