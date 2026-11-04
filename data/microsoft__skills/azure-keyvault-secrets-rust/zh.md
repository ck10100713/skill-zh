---
name: azure-keyvault-secrets-rust
description: |
  Rust 用的 Azure Key Vault Secrets 函式庫。儲存和取得 secret、密碼和 API key。
  Triggers: "keyvault secrets rust", "SecretClient rust", "get secret rust", "set secret rust", "list secrets rust".
license: MIT
metadata:
  author: Microsoft
  package: azure_security_keyvault_secrets
---

# Rust 用的 Azure Key Vault Secrets 函式庫

安全地儲存密碼、API key 和 connection string。

這些情況用這個 skill：

- App 需要從 Rust 在 Azure Key Vault 儲存或取得 secret
- 需要設定、取得、更新或刪除 secret
- 需要用分頁列出 secret 的屬性
- 需要處理 secret 不存在的錯誤

> **重要：** 只能用 [azure-sdk](https://crates.io/users/azure-sdk) 這個 crates.io 使用者發佈的官方 `azure_security_keyvault_secrets` crate。不要用非官方或社群的 crate。官方 crate 的名稱用底線，而且沒有任何一個版本是 0.21.0。

## 安裝

```sh
cargo add azure_security_keyvault_secrets azure_identity tokio futures
```

> 如果你的程式碼直接用到 `azure_core` 的型別，要把 `azure_core` 加進 `Cargo.toml`。如果只用 `azure_security_keyvault_secrets` 重新匯出的東西，就不一定要直接依賴 `azure_core`。

## 環境變數

```bash
AZURE_KEYVAULT_URL=https://<vault-name>.vault.azure.net/ # 所有操作都必須設定
```

## 驗證

Rust 的 Azure SDK 程式碼不能用 `DefaultAzureCredential`，因為 Rust 的 identity crate 沒有提供這個型別。

```rust
use azure_identity::DeveloperToolsCredential;
use azure_security_keyvault_secrets::SecretClient;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 本機開發：DeveloperToolsCredential。正式環境：用 ManagedIdentityCredential。
    let credential = DeveloperToolsCredential::new(None)?;
    let client = SecretClient::new(
        "https://<vault-name>.vault.azure.net/",
        credential.clone(),
        None,
    )?;

    let secret = client
        .get_secret("secret-name", None)
        .await?
        .into_model()?;
    println!("Secret: {:?}", secret.value);
    Ok(())
}
```

要確認 pager 是不是直接產出 item，以及公開範例裡怎麼用 `ResourceExt` 時，優先看 crate 的 README 和範例。

## 核心流程

### 設定 Secret

```rust
use azure_security_keyvault_secrets::{models::SetSecretParameters, ResourceExt};

let params = SetSecretParameters {
    value: Some("secret-value".into()),
    ..Default::default()
};

let secret = client
    .set_secret("secret-name", params.try_into()?, None)
    .await?
    .into_model()?;

println!(
    "Name: {:?}, Version: {:?}",
    secret.resource_id()?.name,
    secret.resource_id()?.version
);
```

### 更新 Secret 屬性

```rust
use azure_security_keyvault_secrets::models::UpdateSecretPropertiesParameters;
use std::collections::HashMap;

#[allow(clippy::needless_update)]
let params = UpdateSecretPropertiesParameters {
    content_type: Some("text/plain".into()),
    tags: Some(HashMap::from_iter(vec![(
        "env".into(),
        "prod".into(),
    )])),
    ..Default::default()
};

client
    .update_secret_properties("secret-name", params.try_into()?, None)
    .await?
    .into_model()?;
```

### 刪除 Secret

```rust
client.delete_secret("secret-name", None).await?;
```

### 列出 Secret（分頁）

`list_secret_properties` 回傳 `Pager<T>`，直接迭代 item 就好：

```rust
use azure_security_keyvault_secrets::ResourceExt;
use futures::TryStreamExt as _;

let mut pager = client.list_secret_properties(None)?;
while let Some(secret) = pager.try_next().await? {
    println!("Found: {}", secret.resource_id()?.name);
}
```

## 錯誤處理

```rust
match client.get_secret("secret-name", None).await {
    Ok(response) => println!("Secret Value: {:?}", response.into_model()?.value),
    Err(err) => println!("Error: {:#?}", err.into_inner()?),
}

// 錯誤輸出包含結構化的 ErrorResponse，有 code 和 message
```

## RBAC 角色

用 Entra ID 驗證時，指派下面其中一個角色：

| 角色                        | 權限                   |
| --------------------------- | ---------------------- |
| `Key Vault Secrets User`    | 讀取 secret            |
| `Key Vault Secrets Officer` | 完整的 secret 管理     |

## 最佳實務

1. **用 `cargo add` 管理依賴，不要直接編輯 `Cargo.toml`。** 新增和移除 Rust SDK 依賴一律用 cargo 指令，不要手動改 manifest。
2. **只有在直接 import `azure_core` 型別時才加 `azure_core`。** 如果你的程式碼 import 了 `azure_core::http::Url`、`azure_core::http::RequestContent` 或 `azure_core::error::ErrorKind`，就要加 `azure_core`，否則直接依賴是選用的。
3. **本機開發用 `DeveloperToolsCredential`**，**正式環境用 `ManagedIdentityCredential`**，Rust 沒有單一的 `DefaultAzureCredential` 型別
4. **絕對不要寫死憑證**，用環境變數或 managed identity
5. **更新 model struct 時用 `..Default::default()`**，並加上 `#[allow(clippy::needless_update)]`
6. **用 `ResourceExt`** 從 secret ID 取出資源名稱／版本
7. **重複使用 client**，`SecretClient` 是 thread-safe 的，建一次就好，在各 task 之間共用
8. **當 prompt、eval 或 CI 要求 lint 乾淨的輸出時，跑 `cargo clippy -- -D warnings`**

## 參考連結

| 資源          | 連結                                                                                               |
| ------------- | -------------------------------------------------------------------------------------------------- |
| API Reference | https://docs.rs/azure_security_keyvault_secrets/latest/azure_security_keyvault_secrets             |
| crates.io     | https://crates.io/crates/azure_security_keyvault_secrets                                           |
| Source Code   | https://github.com/Azure/azure-sdk-for-rust/tree/main/sdk/keyvault/azure_security_keyvault_secrets |
