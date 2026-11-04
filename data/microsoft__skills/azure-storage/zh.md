---
name: azure-storage
description: "Azure Storage 服務，包含 Blob Storage、File Shares、Queue Storage、Table Storage 和 Data Lake。可回答儲存存取層（hot、cool、cold、archive）、各層什麼時候用、層級比較等問題。提供物件儲存、SMB 檔案共用、非同步訊息、NoSQL key-value 和大數據分析，也包含生命週期管理。USE FOR: blob storage, file shares, queue storage, table storage, data lake, upload files, download blobs, storage accounts, access tiers, storage tiers, hot cool cold archive, storage tier comparison, when to use storage tiers, lifecycle management, Azure Storage concepts. DO NOT USE FOR: SQL databases、Cosmos DB（用 azure-prepare）、搭配 Event Hubs 或 Service Bus 的訊息服務（用 azure-messaging）。"
license: MIT
metadata:
  author: Microsoft
  version: "1.2.2"
---

# Azure Storage 服務

## 服務

| 服務 | 使用時機 | MCP 工具 | CLI |
|---------|----------|-----------|-----|
| Blob Storage | 物件、檔案、備份、靜態內容 | `azure__storage` | `az storage blob` |
| File Shares | SMB 檔案共用、lift-and-shift | - | `az storage file` |
| Queue Storage | 非同步訊息、工作 queue | - | `az storage queue` |
| Table Storage | NoSQL key-value（可考慮 Cosmos DB） | - | `az storage table` |
| Data Lake | 大數據分析、hierarchical namespace | - | `az storage fs` |

## MCP Server（優先使用）

啟用 Azure MCP 時：

- `azure__storage` 搭配 command `storage_account_list` - 列出 storage account
- `azure__storage` 搭配 command `storage_container_list` - 列出 account 裡的 container
- `azure__storage` 搭配 command `storage_blob_list` - 列出 container 裡的 blob
- `azure__storage` 搭配 command `storage_blob_get` - 下載 blob 內容
- `azure__storage` 搭配 command `storage_blob_put` - 上傳 blob 內容

**如果 Azure MCP 沒有啟用：** 在 Copilot CLI 或 Claude Code 裡，請使用者執行 `/mcp` 並啟用 Azure MCP；在其他 host，請使用者透過該 host 的 MCP 設定啟用 Azure MCP。

## CLI 備援

```bash
# 列出 storage account
az storage account list --output table

# 列出 container
az storage container list --account-name ACCOUNT --output table

# 列出 blob
az storage blob list --account-name ACCOUNT --container-name CONTAINER --output table

# 下載 blob
az storage blob download --account-name ACCOUNT --container-name CONTAINER --name BLOB --file LOCAL_PATH

# 上傳 blob
az storage blob upload --account-name ACCOUNT --container-name CONTAINER --name BLOB --file LOCAL_PATH
```

## Storage Account 層級

| 層級 | 使用情境 | 效能 |
|------|----------|-------------|
| Standard | 通用、備份 | 毫秒等級 |
| Premium | 資料庫、高 IOPS | 次毫秒等級 |

## Blob 存取層

| 層級 | 存取頻率 | 成本 |
|------|-----------------|------|
| Hot | 頻繁 | 儲存成本較高，存取成本較低 |
| Cool | 不常存取（30 天以上） | 儲存成本較低，存取成本較高 |
| Cold | 很少存取（90 天以上） | 更低 |
| Archive | 極少存取（180 天以上） | 儲存成本最低，需要 rehydration |

## 備援選項

| 類型 | 耐久性 | 使用情境 |
|------|------------|----------|
| LRS | 11 個 9 | Dev/test、可重建的資料 |
| ZRS | 12 個 9 | 區域內的高可用性 |
| GRS | 16 個 9 | 災難復原 |
| GZRS | 16 個 9 | 最佳耐久性 |

## 服務細節

想深入了解各個服務的文件：

- Blob storage 模式和生命週期 -> [Blob Storage documentation](https://learn.microsoft.com/azure/storage/blobs/storage-blobs-overview)
- File shares 和 Azure File Sync -> [Azure Files documentation](https://learn.microsoft.com/azure/storage/files/storage-files-introduction)
- Queue 模式和 poison 處理 -> [Queue Storage documentation](https://learn.microsoft.com/azure/storage/queues/storage-queues-introduction)

## SDK 快速參考

要用 Azure Storage SDK 建構應用程式，請看這些精簡指南：

- **Blob Storage**：[Python](references/sdk/azure-storage-blob-py.md) | [TypeScript](references/sdk/azure-storage-blob-ts.md) | [Java](references/sdk/azure-storage-blob-java.md) | [Rust](references/sdk/azure-storage-blob-rust.md)
- **Queue Storage**：[Python](references/sdk/azure-storage-queue-py.md) | [TypeScript](references/sdk/azure-storage-queue-ts.md)
- **File Shares**：[Python](references/sdk/azure-storage-file-share-py.md) | [TypeScript](references/sdk/azure-storage-file-share-ts.md)
- **Data Lake**：[Python](references/sdk/azure-storage-file-datalake-py.md)
- **Tables**：[Python](references/sdk/azure-data-tables-py.md) | [Java](references/sdk/azure-data-tables-java.md)

各語言完整的套件清單，請看 [SDK Usage Guide](references/sdk-usage.md)。

## Azure SDK

要建構以程式方式操作 Azure Storage 的應用程式，Azure 提供多種語言（.NET、Java、JavaScript、Python、Go、Rust）的 SDK 套件。套件名稱、安裝指令和快速開始範例請看 [SDK Usage Guide](references/sdk-usage.md)。
