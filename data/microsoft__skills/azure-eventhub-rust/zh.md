---
name: azure-eventhub-rust
description: |
  Rust 用的 Azure Event Hubs 函式庫。收發事件，用於串流資料匯入和批次處理。
  Triggers: "event hubs rust", "ProducerClient rust", "ConsumerClient rust", "send event rust", "streaming rust", "eventhub rust".
license: MIT
metadata:
  author: Microsoft
  package: azure_messaging_eventhubs
---

# Rust 用的 Azure Event Hubs 函式庫

Azure Event Hubs 的 client 函式庫，收發事件，用於串流資料匯入。

這些情況用這個 skill：

- App 需要從 Rust 把事件送到 Azure Event Hubs
- 需要從 partition 接收並處理事件
- 需要批次送出來最佳化吞吐量
- 需要控制 consumer 的起始位置

> **重要：** 只能用 [azure-sdk](https://crates.io/users/azure-sdk) 這個 crates.io 使用者發佈的官方 `azure_messaging_eventhubs` crate。不要用非官方或社群的 crate。官方 crate 的名稱用底線，而且沒有任何一個版本是 0.21.0。

## 安裝

```sh
cargo add azure_messaging_eventhubs azure_identity tokio futures
```

> `DeveloperToolsCredential::new(None)?` 本來就回傳 `Arc<DeveloperToolsCredential>`，所以可以直接傳進 `.open()` 或 clone 它。只有在需要直接 import `azure_core` 的東西（例如 `ErrorKind`）時才加 `azure_core`。

## 環境變數

```bash
EVENTHUBS_HOST=<namespace>.servicebus.windows.net # 必須設定：完整的 namespace 名稱
EVENTHUB_NAME=<eventhub-name>                     # 必須設定：Event Hub 的名稱
```

## 關鍵概念

| 概念          | 說明                                                 |
| ------------- | ---------------------------------------------------- |
| **Namespace** | 一個或多個 Event Hub 的容器                          |
| **Event Hub** | 事件串流，切成 partition 以平行讀取                  |
| **Partition** | 有順序、只能附加的事件序列                           |
| **Producer**  | 透過 `ProducerClient` 送出事件                       |
| **Consumer**  | 透過 `ConsumerClient` 從 partition 接收事件          |

## 驗證

Rust 的 Azure SDK 程式碼不能用 `DefaultAzureCredential`，因為 Rust 的 identity crate 沒有提供這個型別。

```rust
use azure_identity::DeveloperToolsCredential;
use azure_messaging_eventhubs::ProducerClient;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 本機開發：DeveloperToolsCredential。正式環境：用 ManagedIdentityCredential。
    let credential = DeveloperToolsCredential::new(None)?;

    let producer = ProducerClient::builder()
        .open(
            "<namespace>.servicebus.windows.net",
            "<eventhub-name>",
            credential.clone(),
        )
        .await?;
    Ok(())
}
```

要確認 builder 的簽章和接收串流的事件 wrapper 形狀時，優先看 crate 的 README 和範例。

## 核心流程

### 送出事件

```rust
// 送出單一事件
producer.send_event(vec![1, 2, 3, 4], None).await?;
```

### 送出批次

```rust
let batch = producer.create_batch(None).await?;
batch.try_add_event_data(vec![1, 2, 3, 4], None)?;

producer.send_batch(batch, None).await?;
```

### 接收事件

```rust
use azure_identity::DeveloperToolsCredential;
use azure_messaging_eventhubs::ConsumerClient;

// 本機開發：DeveloperToolsCredential。正式環境：用 ManagedIdentityCredential。
let credential = DeveloperToolsCredential::new(None)?;
let consumer = ConsumerClient::builder()
    .open(
        "<namespace>.servicebus.windows.net",
        "<eventhub-name>".to_string(),
        credential.clone(),
    )
    .await?;
```

### 從 Partition 接收

```rust
use futures::stream::StreamExt;
use azure_messaging_eventhubs::{
    ConsumerClient, OpenReceiverOptions, StartLocation, StartPosition,
};

let receiver = consumer
    .open_receiver_on_partition(
        "0".to_string(),
        Some(OpenReceiverOptions {
            start_position: Some(StartPosition {
                location: StartLocation::Earliest,
                ..Default::default()
            }),
            ..Default::default()
        }),
    )
    .await?;

let mut stream = receiver.stream_events();
while let Some(event_result) = stream.next().await {
    match event_result {
        // body 在內層的 event data 上，不在接收到的 wrapper 上：`event.event_data().body()`。
        Ok(event) => {
            let body = event.event_data().body().unwrap_or_default();
            println!("Received: {:?}", body);
        }
        Err(err) => eprintln!("Error: {:?}", err),
    }
}
```

## RBAC 角色

用 Entra ID 驗證時，指派下面其中一個角色：

| 角色                             | 權限         |
| -------------------------------- | ------------ |
| `Azure Event Hubs Data Sender`   | 送出事件     |
| `Azure Event Hubs Data Receiver` | 接收事件     |
| `Azure Event Hubs Data Owner`    | 完整權限     |

## 最佳實務

1. **用 `cargo add` 管理依賴，不要直接編輯 `Cargo.toml`。** 新增和移除 Rust SDK 依賴一律用 cargo 指令，不要手動改 manifest。
2. **直接把 credential 傳進 `.open()` 或 clone 它。** `DeveloperToolsCredential::new(None)?` 本來就回傳 `Arc`，所以除非你要明確寫出那個 trait object 型別，否則不用把變數標註成 `Arc<dyn TokenCredential>`。
3. **對齊 builder 的簽章。** `ProducerClient::builder().open(...)` 的 hub 名稱是 `&str`，而 `ConsumerClient::builder().open(...)` 要的是擁有所有權的 `String`。
4. **本機開發用 `DeveloperToolsCredential`**，**正式環境用 `ManagedIdentityCredential`**，Rust 沒有單一的 `DefaultAzureCredential` 型別
5. **絕對不要寫死憑證**，用環境變數或 managed identity
6. **用批次**：`create_batch` + `send_batch` 最佳化吞吐量
7. **逐個事件處理錯誤**：在事件串流裡對 `Ok`/`Err` 做 match
8. **用 `event.event_data().body()` 取事件的 body**，不要用 `event.body()`，因為 `ReceivedEventData` 包著底層的 `EventData`。
9. **指定起始位置**：用 `StartLocation::Earliest` 或 `StartLocation::Latest` 控制從哪裡開始消費
10. **當 prompt、eval 或 CI 要求 lint 乾淨的輸出時，跑 `cargo clippy -- -D warnings`**

## 參考連結

| 資源          | 連結                                                                                          |
| ------------- | --------------------------------------------------------------------------------------------- |
| API Reference | https://docs.rs/azure_messaging_eventhubs/latest/azure_messaging_eventhubs                    |
| crates.io     | https://crates.io/crates/azure_messaging_eventhubs                                            |
| Source Code   | https://github.com/Azure/azure-sdk-for-rust/tree/main/sdk/eventhubs/azure_messaging_eventhubs |
