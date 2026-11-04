---
name: azure-storage-file-share-ts
description: |
  用於 SMB 檔案共用操作的 Azure File Share JavaScript/TypeScript SDK（@azure/storage-file-share）。用於建立 share、管理目錄、上傳／下載檔案，以及處理檔案 metadata。支援 Azure Files 的 SMB 協定情境。Triggers: "file share", "@azure/storage-file-share", "ShareServiceClient", "ShareClient", "SMB", "Azure Files".
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
  package: '@azure/storage-file-share'
---

# @azure/storage-file-share (TypeScript/JavaScript)

Azure File Share 操作的 SDK，涵蓋 SMB 檔案共用、目錄和檔案操作。

## 安裝

```bash
npm install @azure/storage-file-share @azure/identity
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

### Connection String（最簡單）

```typescript
import { ShareServiceClient } from "@azure/storage-file-share";

const client = ShareServiceClient.fromConnectionString(
  process.env.AZURE_STORAGE_CONNECTION_STRING!
);
```

### StorageSharedKeyCredential（僅限 Node.js）

```typescript
import { ShareServiceClient, StorageSharedKeyCredential } from "@azure/storage-file-share";

const accountName = process.env.AZURE_STORAGE_ACCOUNT_NAME!;
const accountKey = process.env.AZURE_STORAGE_ACCOUNT_KEY!;

const sharedKeyCredential = new StorageSharedKeyCredential(accountName, accountKey);
const client = new ShareServiceClient(
  `https://${accountName}.file.core.windows.net`,
  sharedKeyCredential
);
```

### Microsoft Entra Token Credential

```typescript
import { ShareServiceClient } from "@azure/storage-file-share";
import { DefaultAzureCredential, ManagedIdentityCredential } from "@azure/identity";

// 本機開發：DefaultAzureCredential。Production：設定 AZURE_TOKEN_CREDENTIALS=prod 或 AZURE_TOKEN_CREDENTIALS=<specific_credential>
const credential = new DefaultAzureCredential({requiredEnvVars: ["AZURE_TOKEN_CREDENTIALS"]});
// 或在 production 直接用特定的 credential：
// See https://learn.microsoft.com/javascript/api/overview/azure/identity-readme?view=azure-node-latest#credential-classes
// const credential = new ManagedIdentityCredential();

const accountName = process.env.AZURE_STORAGE_ACCOUNT_NAME!;
const client = new ShareServiceClient(
  `https://${accountName}.file.core.windows.net`,
  credential
);
```

### SAS Token

```typescript
import { ShareServiceClient } from "@azure/storage-file-share";

const accountName = process.env.AZURE_STORAGE_ACCOUNT_NAME!;
const sasToken = process.env.AZURE_STORAGE_SAS_TOKEN!;

const client = new ShareServiceClient(
  `https://${accountName}.file.core.windows.net${sasToken}`
);
```

## Client 階層

```
ShareServiceClient (account level)
└── ShareClient (share level)
    └── ShareDirectoryClient (directory level)
        └── ShareFileClient (file level)
```

## Share 操作

### 建立 Share

```typescript
const shareClient = client.getShareClient("my-share");
await shareClient.create();

// 建立時指定 quota（單位 GB）
await shareClient.create({ quota: 100 });
```

### 列出 Share

```typescript
for await (const share of client.listShares()) {
  console.log(share.name, share.properties.quota);
}

// 用 prefix 篩選
for await (const share of client.listShares({ prefix: "logs-" })) {
  console.log(share.name);
}
```

### 刪除 Share

```typescript
await shareClient.delete();

// 存在才刪除
await shareClient.deleteIfExists();
```

### 取得 Share 屬性

```typescript
const properties = await shareClient.getProperties();
console.log("Quota:", properties.quota, "GB");
console.log("Last Modified:", properties.lastModified);
```

### 設定 Share Quota

```typescript
await shareClient.setQuota(200); // 200 GB
```

## 目錄操作

### 建立目錄

```typescript
const directoryClient = shareClient.getDirectoryClient("my-directory");
await directoryClient.create();

// 建立巢狀目錄
const nestedDir = shareClient.getDirectoryClient("parent/child/grandchild");
await nestedDir.create();
```

### 列出目錄和檔案

```typescript
const directoryClient = shareClient.getDirectoryClient("my-directory");

for await (const item of directoryClient.listFilesAndDirectories()) {
  if (item.kind === "directory") {
    console.log(`[DIR] ${item.name}`);
  } else {
    console.log(`[FILE] ${item.name} (${item.properties.contentLength} bytes)`);
  }
}
```

### 刪除目錄

```typescript
await directoryClient.delete();

// 存在才刪除
await directoryClient.deleteIfExists();
```

### 檢查目錄是否存在

```typescript
const exists = await directoryClient.exists();
if (!exists) {
  await directoryClient.create();
}
```

## 檔案操作

### 上傳檔案（簡單版）

```typescript
const fileClient = shareClient
  .getDirectoryClient("my-directory")
  .getFileClient("my-file.txt");

// 上傳字串
const content = "Hello, World!";
await fileClient.create(content.length);
await fileClient.uploadRange(content, 0, content.length);
```

### 上傳檔案（Node.js，從本機檔案）

```typescript
import * as fs from "fs";
import * as path from "path";

const fileClient = shareClient.rootDirectoryClient.getFileClient("uploaded.txt");
const localFilePath = "/path/to/local/file.txt";
const fileSize = fs.statSync(localFilePath).size;

await fileClient.create(fileSize);
await fileClient.uploadFile(localFilePath);
```

### 上傳檔案（Buffer）

```typescript
const buffer = Buffer.from("Hello, Azure Files!");
const fileClient = shareClient.rootDirectoryClient.getFileClient("buffer-file.txt");

await fileClient.create(buffer.length);
await fileClient.uploadRange(buffer, 0, buffer.length);
```

### 上傳檔案（Stream）

```typescript
import * as fs from "fs";

const fileClient = shareClient.rootDirectoryClient.getFileClient("streamed.txt");
const readStream = fs.createReadStream("/path/to/local/file.txt");
const fileSize = fs.statSync("/path/to/local/file.txt").size;

await fileClient.create(fileSize);
await fileClient.uploadStream(readStream, fileSize, 4 * 1024 * 1024, 4); // 4MB buffer、並行度 4
```

### 下載檔案

```typescript
const fileClient = shareClient
  .getDirectoryClient("my-directory")
  .getFileClient("my-file.txt");

const downloadResponse = await fileClient.download();

// 讀成字串
const chunks: Buffer[] = [];
for await (const chunk of downloadResponse.readableStreamBody!) {
  chunks.push(Buffer.from(chunk));
}
const content = Buffer.concat(chunks).toString("utf-8");
```

### 下載到檔案（Node.js）

```typescript
const fileClient = shareClient.rootDirectoryClient.getFileClient("my-file.txt");
await fileClient.downloadToFile("/path/to/local/destination.txt");
```

### 下載到 Buffer（Node.js）

```typescript
const fileClient = shareClient.rootDirectoryClient.getFileClient("my-file.txt");
const buffer = await fileClient.downloadToBuffer();
console.log(buffer.toString());
```

### 刪除檔案

```typescript
const fileClient = shareClient.rootDirectoryClient.getFileClient("my-file.txt");
await fileClient.delete();

// 存在才刪除
await fileClient.deleteIfExists();
```

### 複製檔案

```typescript
const sourceUrl = "https://account.file.core.windows.net/share/source.txt";
const destFileClient = shareClient.rootDirectoryClient.getFileClient("destination.txt");

// 開始複製操作
const copyPoller = await destFileClient.startCopyFromURL(sourceUrl);
await copyPoller.pollUntilDone();
```

## 檔案屬性與 Metadata

### 取得檔案屬性

```typescript
const fileClient = shareClient.rootDirectoryClient.getFileClient("my-file.txt");
const properties = await fileClient.getProperties();

console.log("Content-Length:", properties.contentLength);
console.log("Content-Type:", properties.contentType);
console.log("Last Modified:", properties.lastModified);
console.log("ETag:", properties.etag);
```

### 設定 Metadata

```typescript
await fileClient.setMetadata({
  author: "John Doe",
  category: "documents",
});
```

### 設定 HTTP Header

```typescript
await fileClient.setHttpHeaders({
  fileContentType: "text/plain",
  fileCacheControl: "max-age=3600",
  fileContentDisposition: "attachment; filename=download.txt",
});
```

## Range 操作

### 上傳 Range

```typescript
const data = Buffer.from("partial content");
await fileClient.uploadRange(data, 100, data.length); // 從 offset 100 開始寫入
```

### 下載 Range

```typescript
const downloadResponse = await fileClient.download(100, 50); // offset 100、長度 50
```

### 清除 Range

```typescript
await fileClient.clearRange(0, 100); // 清除前 100 bytes
```

## Snapshot 操作

### 建立 Snapshot

```typescript
const snapshotResponse = await shareClient.createSnapshot();
console.log("Snapshot:", snapshotResponse.snapshot);
```

### 存取 Snapshot

```typescript
const snapshotShareClient = shareClient.withSnapshot(snapshotResponse.snapshot!);
const snapshotFileClient = snapshotShareClient.rootDirectoryClient.getFileClient("file.txt");
const content = await snapshotFileClient.downloadToBuffer();
```

### 刪除 Snapshot

```typescript
await shareClient.delete({ deleteSnapshots: "include" });
```

## 產生 SAS Token（僅限 Node.js）

### 產生 File SAS

```typescript
import {
  generateFileSASQueryParameters,
  FileSASPermissions,
  StorageSharedKeyCredential,
} from "@azure/storage-file-share";

const sharedKeyCredential = new StorageSharedKeyCredential(accountName, accountKey);

const sasToken = generateFileSASQueryParameters(
  {
    shareName: "my-share",
    filePath: "my-directory/my-file.txt",
    permissions: FileSASPermissions.parse("r"), // 唯讀
    expiresOn: new Date(Date.now() + 3600 * 1000), // 1 小時
  },
  sharedKeyCredential
).toString();

const sasUrl = `https://${accountName}.file.core.windows.net/my-share/my-directory/my-file.txt?${sasToken}`;
```

### 產生 Share SAS

```typescript
import { ShareSASPermissions, generateFileSASQueryParameters } from "@azure/storage-file-share";

const sasToken = generateFileSASQueryParameters(
  {
    shareName: "my-share",
    permissions: ShareSASPermissions.parse("rcwdl"), // read, create, write, delete, list
    expiresOn: new Date(Date.now() + 24 * 3600 * 1000), // 24 小時
  },
  sharedKeyCredential
).toString();
```

## 錯誤處理

```typescript
import { RestError } from "@azure/storage-file-share";

try {
  await shareClient.create();
} catch (error) {
  if (error instanceof RestError) {
    switch (error.statusCode) {
      case 404:
        console.log("Share not found");
        break;
      case 409:
        console.log("Share already exists");
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
  ShareServiceClient,
  ShareClient,
  ShareDirectoryClient,
  ShareFileClient,

  // Authentication
  StorageSharedKeyCredential,
  AnonymousCredential,

  // SAS
  FileSASPermissions,
  ShareSASPermissions,
  AccountSASPermissions,
  AccountSASServices,
  AccountSASResourceTypes,
  generateFileSASQueryParameters,
  generateAccountSASQueryParameters,

  // Options & Responses
  ShareCreateResponse,
  FileDownloadResponseModel,
  DirectoryItem,
  FileItem,
  ShareProperties,
  FileProperties,

  // Errors
  RestError,
} from "@azure/storage-file-share";
```

## 最佳實務

1. **為了簡單，用 connection string** — 開發時設定最容易
2. **本機開發用 `DefaultAzureCredential`；production 用 `ManagedIdentityCredential` 或 `WorkloadIdentityCredential`**
3. **替 share 設定 quota** — 避免意外的儲存費用
4. **大檔案用串流** — 超過 256MB 的檔案用 `uploadStream`/`downloadToFile`
5. **部分更新用 range** — 比整個檔案取代更有效率
6. **重大變更之前先建立 snapshot** — 可以還原到某個時間點
7. **妥善處理錯誤** — 檢查 `RestError.statusCode` 做對應處理
8. **用 `*IfExists` 方法** — 讓操作可以重複執行（idempotent）

## 平台差異

| 功能 | Node.js | 瀏覽器 |
|---------|---------|---------|
| `StorageSharedKeyCredential` | ✅ | ❌ |
| `uploadFile()` | ✅ | ❌ |
| `uploadStream()` | ✅ | ❌ |
| `downloadToFile()` | ✅ | ❌ |
| `downloadToBuffer()` | ✅ | ❌ |
| SAS 產生 | ✅ | ❌ |
| DefaultAzureCredential | ✅ | ❌ |
| Anonymous/SAS 存取 | ✅ | ✅ |
