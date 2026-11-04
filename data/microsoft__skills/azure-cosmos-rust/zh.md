---
name: azure-cosmos-rust
description: |
  Rust 用的 Azure Cosmos DB 函式庫（NoSQL API）。文件 CRUD、container、全球分散式資料。
  Triggers: "cosmos db rust", "CosmosClient rust", "document crud rust", "NoSQL rust", "partition key rust".
license: MIT
metadata:
  author: Microsoft
  package: azure_data_cosmos
---

# Rust 用的 Azure Cosmos DB 函式庫

Azure Cosmos DB NoSQL API 的 client 函式庫，處理文件 CRUD、container 和全球分散式資料。

這些情況用這個 skill：

- App 需要從 Rust 在 Cosmos DB 儲存或查詢文件
- 需要對帶有 partition key 的 item 做 CRUD 操作
- 需要用金鑰驗證來取代 Entra ID

> **重要：** 只能用 [azure-sdk](https://crates.io/users/azure-sdk) 這個 crates.io 使用者發佈的官方 `azure_data_cosmos` crate。不要用非官方的 `azure_cosmos` 或 `azure_sdk_for_rust` 社群 crate。官方 crate 的名稱用底線，而且沒有任何一個版本是 0.21.0。

## 安裝

```sh
cargo add azure_data_cosmos azure_identity serde serde_json tokio
```

> 如果你的程式碼直接用到 `azure_core` 的型別（例如 `azure_core::credentials::TokenCredential`），要把 `azure_core` 加進 `Cargo.toml`。如果只用 `azure_data_cosmos` 重新匯出的東西，就不一定要直接依賴 `azure_core`。

## 環境變數

```bash
COSMOS_ENDPOINT=https://<account>.documents.azure.com/ # 所有操作都必須設定
```

## 驗證

Rust 的 Azure SDK 程式碼不能用 `DefaultAzureCredential`，因為 Rust 的 identity crate 沒有提供這個型別。

```rust
use azure_identity::DeveloperToolsCredential;
use azure_data_cosmos::{
    CosmosClient, AccountReference, AccountEndpoint, RoutingStrategy,
};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 本機開發：DeveloperToolsCredential。正式環境：用 ManagedIdentityCredential。
    let credential = DeveloperToolsCredential::new(None)?;
    let endpoint: AccountEndpoint = "https://<account>.documents.azure.com/"
        .parse()?;
    let account = AccountReference::with_credential(endpoint, credential);
    let client = CosmosClient::builder()
        .build(account, RoutingStrategy::ProximityTo("East US".into()))
        .await?;
    Ok(())
}
```

要確認 builder 的簽章和 CRUD 方法的形狀時，優先看 crate 的 README 和範例，不要憑記憶或從內部生成的程式碼去重建 API。

## Client 階層

| Client            | 用途                      | 取得方式                                        |
| ----------------- | ------------------------- | ----------------------------------------------- |
| `CosmosClient`    | 帳號層級的操作            | `CosmosClient::builder().build(account).await?` |
| `DatabaseClient`  | 資料庫操作                | `client.database_client("db")`                  |
| `ContainerClient` | Container／item 操作      | `database.container_client("c").await`          |

## 核心流程

```rust
use serde::{Serialize, Deserialize};
use azure_data_cosmos::CosmosClient;

#[derive(Serialize, Deserialize)]
struct Item {
    pub id: String,
    pub partition_key: String,
    pub value: String,
}

async fn crud(client: CosmosClient) -> Result<(), Box<dyn std::error::Error>> {
    let container = client
        .database_client("myDatabase")
        .container_client("myContainer")
        .await;

    let item = Item {
        id: "1".into(),
        partition_key: "pk1".into(),
        value: "hello".into(),
    };

    // Create
    container.create_item("pk1", "1", item, None).await?;

    // Read
    let resp = container.read_item("pk1", "1", None).await?;
    let mut item: Item = resp.into_model()?;

    // Update
    item.value = "updated".into();
    container.replace_item("pk1", "1", item, None).await?;

    // Delete
    container.delete_item("pk1", "1", None).await?;
    Ok(())
}
```

### Patch Item

```rust
use azure_data_cosmos::{PatchInstructions, PatchOperation};

let patch = PatchInstructions::from(vec![
    PatchOperation::set("/value", serde_json::json!("patched")),
]);
let patched: Item = container
    .patch_item("pk1", "1", patch, None)
    .await?
    .into_model()?;
println!("Patched value: {}", patched.value);
```

## 金鑰驗證（選用）

用 feature flag 啟用帳號金鑰驗證：

```sh
cargo add azure_data_cosmos --features key_auth
```

## RBAC 角色

用 Entra ID 驗證時，指派下面其中一個 Cosmos DB 內建角色：

| 角色                                  | 權限   |
| ------------------------------------- | ------ |
| `Cosmos DB Built-in Data Reader`      | 唯讀   |
| `Cosmos DB Built-in Data Contributor` | 讀寫   |

## 最佳實務

1. **用 `cargo add` 管理依賴，不要直接編輯 `Cargo.toml`。** 新增和移除 Rust SDK 依賴一律用 cargo 指令，不要手動改 manifest。
2. **只有在直接 import `azure_core` 型別時才加 `azure_core`。** 如果你的程式碼 import 了 `azure_core::http::Url`、`azure_core::http::RequestContent` 或 `azure_core::error::ErrorKind`，就要加 `azure_core`，否則直接依賴是選用的。
3. **本機開發用 `DeveloperToolsCredential`**，**正式環境用 `ManagedIdentityCredential`**，Rust 沒有單一的 `DefaultAzureCredential` 型別
4. **絕對不要寫死憑證**，用環境變數或 managed identity
5. **重複使用 `CosmosClient`**，client 是 thread-safe 的，建一次就好，在各 task 之間共用
6. **用 `RoutingStrategy::ProximityTo`**，路由到最近的 region，延遲最低
7. **item 操作一定要指定 partition key**，Cosmos DB 的所有 CRUD 都要求提供
8. **當 prompt、eval 或 CI 要求 lint 乾淨的輸出時，跑 `cargo clippy -- -D warnings`**
9. **為 `#[non_exhaustive]` 的 SDK model 預留擴充空間**，建構 SDK 的 model／options struct 時，initializer 結尾加 `..Default::default()`（並加上 `#[allow(clippy::needless_update)]`），比對 SDK enum 時加一個 `_` 萬用分支，這樣服務端新增欄位或 variant 時才不會讓你的 build 壞掉

## 參考連結

| 資源          | 連結                                                                               |
| ------------- | ---------------------------------------------------------------------------------- |
| API Reference | https://docs.rs/azure_data_cosmos/latest/azure_data_cosmos                         |
| crates.io     | https://crates.io/crates/azure_data_cosmos                                         |
| Source Code   | https://github.com/Azure/azure-sdk-for-rust/tree/main/sdk/cosmos/azure_data_cosmos |
