---
name: azure-storage-blob-rust
description: |
  Rust 版的 Azure Blob Storage library。上傳、下載並管理 blob 和 container。
  Triggers: "blob storage rust", "BlobClient rust", "upload blob rust", "download blob rust", "storage container rust", "BlobServiceClient rust".
license: MIT
metadata:
  author: Microsoft
  package: azure_storage_blob
---

# Rust 版 Azure Blob Storage library

Azure Blob Storage 的 client library，用來上傳、下載並管理 blob 和 container。

在這些情況下使用這個 skill：

- 應用程式要用 Rust 從 Azure Storage 上傳或下載 blob
- 需要建立或管理 blob container
- 需要分頁列出 blob
- blob 操作需要 RBAC 驗證

> **重要：** 只能用 [azure-sdk](https://crates.io/users/azure-sdk) 這個 crates.io 使用者發布的官方 `azure_storage_blob` crate。絕對不要用非官方的 `azure_storage`、`azure_storage_blobs` 或 `azure_sdk_for_rust` 社群 crate。官方 crate 的名稱用底線，而且沒有任何一個版本是 0.21.0。

## 安裝

```sh
cargo add azure_storage_blob azure_identity azure_core tokio futures
```

> 如果你的程式碼直接用到 `azure_core` 的型別（例如 `azure_core::http::Url` 或 `azure_core::http::RequestContent`），要把 `azure_core` 加進 `Cargo.toml`。如果只用 `azure_storage_blob` re-export 出來的東西，直接依賴 `azure_core` 是選用的。

## 環境變數

```bash
AZURE_STORAGE_ACCOUNT=<account-name>                         # 呼叫者給的是 account 名稱時優先用這個
AZURE_STORAGE_ENDPOINT=https://<account>.blob.core.windows.net/ # 呼叫者給的是完整 endpoint 時的選用替代方案
```

兩個都有的時候，優先用 `AZURE_STORAGE_ACCOUNT` 組出 endpoint，這樣程式碼才會跟常見的評測 prompt 一致。

## 驗證

Rust 的 Azure SDK 程式碼不能用 `DefaultAzureCredential`。Rust 的 identity crate 沒有提供這個型別。

```rust
// 本機開發的正確寫法
use azure_identity::DeveloperToolsCredential;

let credential = DeveloperToolsCredential::new(None)?;
```

```rust
// 在 Rust 裡是錯的：azure_identity 沒有這個型別
use azure_identity::DefaultAzureCredential;
```

```rust
use azure_core::http::Url;
use azure_identity::DeveloperToolsCredential;
use azure_storage_blob::BlobServiceClient;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 本機開發：DeveloperToolsCredential。Production：用 ManagedIdentityCredential。
    let credential = DeveloperToolsCredential::new(None)?;
    let service_url = Url::parse("https://<storage_account_name>.blob.core.windows.net/")?;
    let service_client = BlobServiceClient::new(
        service_url,
        Some(credential),
        None,
    )?;

    // 用名稱衍生出 container 和 blob client。
    let container_client = service_client.blob_container_client("<container_name>");
    let blob_client = container_client.blob_client("<blob_name>");
    Ok(())
}
```

## Client 類型

| Client                | 用途                                   |
| --------------------- | ----------------------------------------- |
| `BlobServiceClient`   | Account 層級的操作、列出 container |
| `BlobContainerClient` | Container 操作、列出 blob          |
| `BlobClient`          | 單一 blob 的操作                |

## 核心工作流程

### 上傳 Blob

```rust
use azure_core::http::{RequestContent, Url};
use azure_identity::DeveloperToolsCredential;
use azure_storage_blob::BlobServiceClient;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 本機開發：DeveloperToolsCredential。Production：用 ManagedIdentityCredential。
    let credential = DeveloperToolsCredential::new(None)?;
    let service_url = Url::parse("https://<storage_account_name>.blob.core.windows.net/")?;
    let service_client = BlobServiceClient::new(service_url, Some(credential), None)?;
    let blob_client = service_client.blob_client("<container_name>", "<blob_name>");

    let data = b"hello world";
    blob_client.upload(RequestContent::from(data.to_vec()), None).await?;
    Ok(())
}
```

### 下載 Blob／取得屬性

```rust
// 取得 blob 屬性
let props = blob_client.get_properties(None).await?;

// 下載 blob 內容
let response = blob_client.download(None).await?;
let content = String::from_utf8(response.body.collect().await?.into())?;
```

### 刪除 Blob

```rust
blob_client.delete(None).await?;
```

### Container 操作

```rust
use azure_core::http::Url;
use azure_identity::DeveloperToolsCredential;
use azure_storage_blob::BlobServiceClient;
use futures::TryStreamExt as _;

let credential = DeveloperToolsCredential::new(None)?;
let service_url = Url::parse("https://<storage_account_name>.blob.core.windows.net/")?;
let service_client = BlobServiceClient::new(service_url, Some(credential), None)?;
let container_client = service_client.blob_container_client("<container_name>");

// 建立 container
container_client.create(None).await?;

// 列出 blob（這種 client 用法下，pager 直接吐出 BlobItem）
let mut pager = container_client.list_blobs(None)?;
while let Some(blob) = pager.try_next().await? {
    let name = blob.name.as_deref().unwrap_or("<unnamed>");
    let size = blob
        .properties
        .as_ref()
        .and_then(|properties| properties.content_length);

    match size {
        Some(size) => println!("Blob: {name} ({size} bytes)"),
        None => println!("Blob: {name}"),
    }
}
```

`azure_storage_blob` 1.x 不要以為需要像 `for item in &page.blob_items` 這樣的巢狀分頁迴圈。在這種用法下，`try_next()` 吐出來的就已經是你要印的 blob item。

## 錯誤處理

要用程式方式存取 storage 專屬的錯誤代碼，就用 `StorageError`：

```rust
use azure_core::error::ErrorKind;
use azure_storage_blob::StorageError;
use azure_storage_blob::models::StorageErrorCode;

let result = blob_client.download(None).await;

match result {
    Ok(response) => {
        let content: Vec<u8> = response.body.collect().await?.into();
        println!("Downloaded {} bytes", content.len());
    }
    Err(error) => {
        if matches!(error.kind(), ErrorKind::HttpResponse { .. }) {
            // 轉成 StorageError 以便用程式存取
            let storage_error: StorageError = error.try_into()?;
            println!("HTTP Status: {}", storage_error.status_code);

            if let Some(error_code) = &storage_error.error_code {
                match error_code {
                    StorageErrorCode::BlobNotFound => {
                        println!("The blob does not exist.");
                    }
                    StorageErrorCode::ContainerNotFound => {
                        println!("The container does not exist.");
                    }
                    StorageErrorCode::AuthorizationFailure => {
                        println!("Authorization failed. Check RBAC roles.");
                    }
                    _ => println!("Storage error: {error_code}"),
                }
            }

            if let Some(request_id) = &storage_error.request_id {
                println!("Request ID (for Azure support): {request_id}");
            }
        } else {
            println!("Non-HTTP error: {:?}", error);
        }
    }
}
```

> **注意：** `StorageError::try_into` 需要擁有所有權的 error 物件，如果傳進去的是 error 的參照，就編譯不過。

## RBAC 角色

用 Entra ID 驗證時，要把下列其中一個角色指派給該身分：

| 角色                            | 存取權限                     |
| ------------------------------- | -------------------------- |
| `Storage Blob Data Reader`      | 唯讀                  |
| `Storage Blob Data Contributor` | 讀寫                 |
| `Storage Blob Data Owner`       | 完整存取，包含 RBAC |

## 最佳實務

1. **用 `cargo add` 管理相依套件，不要直接編輯 `Cargo.toml`。** 新增和移除 Rust SDK 的相依套件，要用 cargo 指令，不要手動改 manifest。
2. **只有在直接 import `azure_core` 型別時才加 `azure_core`。** 如果你的程式碼 import 了 `azure_core::http::Url`、`azure_core::http::RequestContent` 或 `azure_core::error::ErrorKind`，就要加 `azure_core`；否則直接依賴是選用的。
3. 本機開發**用 `DeveloperToolsCredential`**，production 用 **`ManagedIdentityCredential`**。Rust 沒有提供單一的 `DefaultAzureCredential` 型別
4. **絕對不要把憑證寫死**，要用環境變數或 managed identity
5. **用 `RequestContent::from()`** 包住要上傳到 blob 的資料，這樣 SDK 才能正確處理內容
6. **指派 RBAC 角色**，要寫入就要有 "Storage Blob Data Contributor"
7. **重複使用 client**，client 是 thread-safe 的，建立一次，在各個 task 之間共用
8. **優先把 `BlobServiceClient` 當作進入點**，再從它衍生出 container 和 blob client
9. **把很多 storage model 欄位當成選用的。** `blob.name` 是 `Option<String>`，內容長度要用 `blob.properties.as_ref().and_then(|p| p.content_length)` 取得。
10. 當 prompt 或 CI 要求嚴格的 lint 合規時，**在認定工作完成之前先跑 `cargo clippy -- -D warnings`**，連 collapsible `if` 區塊這類風格 lint 也要修，不只是編譯錯誤。
11. 驗證公開 API 的形狀（例如分頁結果）時，**優先參考 crate 的 README／範例**，不要看自動產生的內部型別名稱
12. **讓 `#[non_exhaustive]` 的 SDK model 面向未來**：建構 SDK model／options struct 時，initializer 最後要加 `..Default::default()`（並加上 `#[allow(clippy::needless_update)]`），比對 SDK enum 時要用 `_` 萬用分支，這樣服務之後新增欄位或 variant 時，你的 build 才不會壞

## Rust Blob 常見的坑

- 不要 import `azure_identity::DefaultAzureCredential`，要用 `DeveloperToolsCredential` 或其他真正存在的 Rust credential 型別。
- 不要以為自動產生的內部 model 名稱就代表公開的 pager item 型別，要照這個 crate 文件裡的 `list_blobs` 範例寫。
- 不要直接用 `{}` 印 `blob.name`，它是選用的，要先 unwrap 或提供 fallback。
- 當任務同時要求 `cargo clippy -- -D warnings` 時，不要在 `cargo build` 通過後就停手。

## 參考連結

| 資源      | 連結                                                                                 |
| ------------- | ------------------------------------------------------------------------------------ |
| API Reference | https://docs.rs/crate/azure_storage_blob/latest                                      |
| crates.io     | https://crates.io/crates/azure_storage_blob                                          |
| Source Code   | https://github.com/Azure/azure-sdk-for-rust/tree/main/sdk/storage/azure_storage_blob |
