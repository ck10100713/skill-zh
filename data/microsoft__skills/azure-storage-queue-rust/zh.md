---
name: azure-storage-queue-rust
description: |
  Rust 版的 Azure Queue Storage library。傳送、接收並管理 queue 訊息。
  Triggers: "queue storage rust", "QueueClient rust", "send message rust", "receive messages rust", "QueueServiceClient rust", "queue rust".
license: MIT
metadata:
  author: Microsoft
  package: azure_storage_queue
---

# Rust 版 Azure Queue Storage library

Azure Queue Storage 的 client library，用來傳送、接收並管理 queue 訊息。

在這些情況下使用這個 skill：

- 應用程式要用 Rust 從 Azure Queue Storage 傳送或接收訊息
- 需要建立或管理 queue
- 需要 peek、接收或刪除 queue 訊息
- queue 操作需要 RBAC 驗證

> **重要：** 只能用 [azure-sdk](https://crates.io/users/azure-sdk) 這個 crates.io 使用者發布的官方 `azure_storage_queue` crate。絕對不要用非官方或社群的 crate。官方 crate 的名稱用底線，而且沒有任何一個版本是 0.21.0。

## 安裝

```sh
cargo add azure_storage_queue azure_identity azure_core tokio
```

> 如果你的程式碼直接用到 `azure_core` 的型別，要把 `azure_core` 加進 `Cargo.toml`。如果只用 `azure_storage_queue` re-export 出來的東西，直接依賴 `azure_core` 是選用的。

## 環境變數

```bash
AZURE_STORAGE_QUEUE_ENDPOINT=https://<account>.queue.core.windows.net/ # 所有操作都必填
```

## 驗證

Rust 的 Azure SDK 程式碼不能用 `DefaultAzureCredential`。Rust 的 identity crate 沒有提供這個型別。

```rust
use azure_core::http::Url;
use azure_identity::DeveloperToolsCredential;
use azure_storage_queue::QueueServiceClient;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 本機開發：DeveloperToolsCredential。Production：用 ManagedIdentityCredential。
    let credential = DeveloperToolsCredential::new(None)?;
    let service_url = Url::parse("https://<storage_account_name>.queue.core.windows.net/")?;
    let service_client = QueueServiceClient::new(service_url, Some(credential), None)?;

    // 用名稱衍生出 queue client。
    let queue_client = service_client.queue_client("<queue_name>")?;
    Ok(())
}
```

不要從自動產生的內部 model 名稱去推測公開的 SDK 型別。確認 queue client 的方法簽章和訊息／結果的形狀時，優先參考 crate 的 README／範例。

## Client 類型

| Client               | 用途                               | 取得方式                                   |
| -------------------- | ------------------------------------- | ---------------------------------------- |
| `QueueServiceClient` | Account 層級的操作、列出 queue | `QueueServiceClient::new()`              |
| `QueueClient`        | Queue 操作、傳送／接收／刪除 | `service_client.queue_client("<name>")?` |

## 核心工作流程

### 傳送訊息

```rust
use azure_core::http::Url;
use azure_identity::DeveloperToolsCredential;
use azure_storage_queue::{models::QueueMessage, QueueServiceClient};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let credential = DeveloperToolsCredential::new(None)?;
    let service_url = Url::parse("https://<storage_account_name>.queue.core.windows.net/")?;
    let service_client = QueueServiceClient::new(service_url, Some(credential), None)?;
    let queue_client = service_client.queue_client("<queue_name>")?;

    #[allow(clippy::needless_update)]
    let message = QueueMessage {
        message_text: Some("hello world".to_string()),
        ..Default::default()
    };
    queue_client.send_message(message.try_into()?, None).await?;
    Ok(())
}
```

### 接收訊息

```rust
use azure_core::http::Url;
use azure_identity::DeveloperToolsCredential;
use azure_storage_queue::QueueServiceClient;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let credential = DeveloperToolsCredential::new(None)?;
    let service_url = Url::parse("https://<storage_account_name>.queue.core.windows.net/")?;
    let service_client = QueueServiceClient::new(service_url, Some(credential), None)?;
    let queue_client = service_client.queue_client("<queue_name>")?;

    let response = queue_client.receive_messages(None).await?;
    let messages = response.into_model()?;
    for msg in messages.items.unwrap_or_default() {
        println!("{}", msg.message_text.as_deref().unwrap_or("<empty>"));
    }
    Ok(())
}
```

### 刪除訊息

接收訊息之後，用訊息 ID 和 pop receipt 來刪除它：

```rust
let response = queue_client.receive_messages(None).await?;
let messages = response.into_model()?;
for msg in messages.items.unwrap_or_default() {
    if let (Some(id), Some(pop_receipt)) = (&msg.message_id, &msg.pop_receipt) {
        queue_client.delete_message(id, pop_receipt, None).await?;
    }
}
```

### Peek 訊息

Peek 訊息但不把它們從 queue 移除：

```rust
let response = queue_client.peek_messages(None).await?;
let messages = response.into_model()?;
for msg in messages.items.unwrap_or_default() {
    println!("Peeked: {}", msg.message_text.as_deref().unwrap_or("<empty>"));
}
```

## RBAC 角色

用 Entra ID 驗證時，要把下列其中一個角色指派給該身分：

| 角色                                   | 存取權限                 |
| -------------------------------------- | ---------------------- |
| `Storage Queue Data Reader`            | 讀取和 peek 訊息 |
| `Storage Queue Data Contributor`       | 讀寫訊息    |
| `Storage Queue Data Message Sender`    | 只能傳送訊息     |
| `Storage Queue Data Message Processor` | 接收和刪除     |

## 最佳實務

1. **用 `cargo add` 管理相依套件，不要直接編輯 `Cargo.toml`。** 新增和移除 Rust SDK 的相依套件，要用 cargo 指令，不要手動改 manifest。
2. **只有在直接 import `azure_core` 型別時才加 `azure_core`。** 如果你的程式碼 import 了 `azure_core::http::Url`、`azure_core::http::RequestContent` 或 `azure_core::error::ErrorKind`，就要加 `azure_core`；否則直接依賴是選用的。
3. 本機開發**用 `DeveloperToolsCredential`**，production 用 **`ManagedIdentityCredential`**。Rust 沒有提供單一的 `DefaultAzureCredential` 型別
4. **絕對不要把憑證寫死**，要用環境變數或 managed identity
5. **指派 RBAC 角色**，確保該身分有適當的 queue data 角色
6. **用 `QueueServiceClient` 當進入點**，再透過 `queue_client()` 從它衍生出 `QueueClient`
7. **處理完要刪除訊息**，用 `receive_messages` 回傳的訊息 ID 和 pop receipt
8. **重複使用 client**，client 是 thread-safe 的，建立一次，在各個 task 之間共用
9. 當 prompt、eval 或 CI 要求 lint 乾淨的輸出時，**要跑 `cargo clippy -- -D warnings`**
10. **讓 `#[non_exhaustive]` 的 SDK model 面向未來**：model struct 的 initializer（例如 `QueueMessage`）最後要加 `..Default::default()`（並加上 `#[allow(clippy::needless_update)]`），比對 SDK enum 時要用 `_` 萬用分支，這樣服務之後新增欄位或 variant 時，你的 build 才不會壞

## 參考連結

| 資源      | 連結                                                                                  |
| ------------- | ------------------------------------------------------------------------------------- |
| API Reference | https://docs.rs/crate/azure_storage_queue/latest                                      |
| crates.io     | https://crates.io/crates/azure_storage_queue                                          |
| Source Code   | https://github.com/Azure/azure-sdk-for-rust/tree/main/sdk/storage/azure_storage_queue |
