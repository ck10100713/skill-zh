---
name: azure-keyvault-keys-rust
description: |
  Rust 用的 Azure Key Vault Keys 函式庫。建立、管理和使用加密金鑰，包含 RSA、EC 和 HSM 保護的金鑰。
  Triggers: "keyvault keys rust", "KeyClient rust", "create key rust", "encrypt rust", "wrap key rust", "sign rust".
license: MIT
metadata:
  author: Microsoft
  package: azure_security_keyvault_keys
---

# Rust 用的 Azure Key Vault Keys 函式庫

安全地儲存和管理加密金鑰，包含 RSA、EC 和 HSM 保護的金鑰。

這些情況用這個 skill：

- App 需要從 Rust 在 Key Vault 建立或管理加密金鑰
- 需要 wrap／unwrap 資料加密金鑰（envelope encryption）
- 需要用 Key Vault 的金鑰簽署或驗證資料
- 需要 HSM 保護的金鑰

> **重要：** 只能用 [azure-sdk](https://crates.io/users/azure-sdk) 這個 crates.io 使用者發佈的官方 `azure_security_keyvault_keys` crate。不要用非官方或社群的 crate。官方 crate 的名稱用底線，而且沒有任何一個版本是 0.21.0。

## 安裝

```sh
cargo add azure_security_keyvault_keys azure_identity tokio futures
```

> 如果你的程式碼直接用到 `azure_core` 的型別，要把 `azure_core` 加進 `Cargo.toml`。如果只用 `azure_security_keyvault_keys` 重新匯出的東西，就不一定要直接依賴 `azure_core`。

## 環境變數

```bash
AZURE_KEYVAULT_URL=https://<vault-name>.vault.azure.net/ # 所有操作都必須設定
```

## 驗證

Rust 的 Azure SDK 程式碼不能用 `DefaultAzureCredential`，因為 Rust 的 identity crate 沒有提供這個型別。

```rust
use azure_identity::DeveloperToolsCredential;
use azure_security_keyvault_keys::KeyClient;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 本機開發：DeveloperToolsCredential。正式環境：用 ManagedIdentityCredential。
    let credential = DeveloperToolsCredential::new(None)?;
    let client = KeyClient::new(
        "https://<vault-name>.vault.azure.net/",
        credential.clone(),
        None,
    )?;

    let key = client.get_key("key-name", None).await?.into_model()?;
    println!("Key: {:?}", key.key);
    Ok(())
}
```

要確認建立金鑰、wrap，以及會看版本的 unwrap 流程這類公開操作的形狀時，優先看 crate 的 README 和範例。

## 核心流程

### 建立金鑰

```rust
use azure_security_keyvault_keys::{
    models::{CreateKeyParameters, CurveName, KeyType},
    ResourceExt,
};

// 建立 EC 金鑰
let body = CreateKeyParameters {
    kty: Some(KeyType::Ec),
    curve: Some(CurveName::P256),
    ..Default::default()
};

let key = client
    .create_key("key-name", body.try_into()?, None)
    .await?
    .into_model()?;

println!(
    "Name: {:?}, Type: {:?}, Version: {:?}",
    key.resource_id()?.name,
    key.key.as_ref().map(|k| k.kty.as_ref()),
    key.resource_id()?.version,
);
```

### 更新金鑰屬性

```rust
use azure_security_keyvault_keys::models::UpdateKeyPropertiesParameters;
use std::collections::HashMap;

#[allow(clippy::needless_update)]
let params = UpdateKeyPropertiesParameters {
    tags: Some(HashMap::from_iter(vec![("env".into(), "prod".into())])),
    ..Default::default()
};

client
    .update_key_properties("key-name", params.try_into()?, None)
    .await?
    .into_model()?;
```

### 刪除金鑰

```rust
client.delete_key("key-name", None).await?;
```

### 列出金鑰（分頁）

`list_key_properties` 回傳 `Pager<T>`，直接迭代 item 就好：

```rust
use azure_security_keyvault_keys::ResourceExt;
use futures::TryStreamExt as _;

let mut pager = client.list_key_properties(None)?;
while let Some(key) = pager.try_next().await? {
    println!("Found: {}", key.resource_id()?.name);
}
```

## Wrap / Unwrap（Envelope Encryption）

Key Vault 在伺服器端執行加密操作，私鑰永遠不會離開 HSM：

```rust
use azure_security_keyvault_keys::{
    models::{
        CreateKeyParameters, EncryptionAlgorithm, KeyOperationParameters, KeyType,
    },
    ResourceExt, ResourceId,
};
use rand::random;

// 建立 key encryption key (KEK)
let body = CreateKeyParameters {
    kty: Some(KeyType::Rsa),
    key_size: Some(2048),
    ..Default::default()
};

let key = client
    .create_key("kek-name", body.try_into()?, None)
    .await?
    .into_model()?;

// 產生對稱的 data encryption key (DEK)
let dek = random::<u32>().to_le_bytes().to_vec();

// 用 KEK 把 DEK wrap 起來
let mut params = KeyOperationParameters {
    algorithm: Some(EncryptionAlgorithm::RsaOaep256),
    value: Some(dek.clone()),
    ..Default::default()
};
let wrapped = client
    .wrap_key("kek-name", params.clone().try_into()?, None)
    .await?
    .into_model()?;

// 保留 wrap 時用的金鑰版本，之後才能用同一個版本 unwrap
let ResourceId { version, .. } = wrapped.resource_id()?;
let key_version = version.as_deref().unwrap_or_default();

// Unwrap 取回 DEK
params.value = wrapped.result;
let unwrapped = client
    .unwrap_key("kek-name", key_version, params.try_into()?, None)
    .await?
    .into_model()?;

assert!(matches!(unwrapped.result, Some(ref result) if result.eq(&dek)));
```

## 金鑰類型

| 類型    | 使用情境                      | 參數              |
| ------- | ----------------------------- | ----------------- |
| EC      | 簽署、金鑰協議                | `KeyType::Ec`     |
| RSA     | 加密、簽署、wrap              | `KeyType::Rsa`    |
| Oct     | 對稱操作（HSM）               | `KeyType::Oct`    |
| EC-HSM  | HSM 保護的 EC 金鑰            | `KeyType::EcHsm`  |
| RSA-HSM | HSM 保護的 RSA 金鑰           | `KeyType::RsaHsm` |

## RBAC 角色

用 Entra ID 驗證時，指派下面其中一個角色：

| 角色                       | 權限                  |
| -------------------------- | --------------------- |
| `Key Vault Crypto User`    | 用金鑰做加密操作      |
| `Key Vault Crypto Officer` | 完整的金鑰管理        |

## 最佳實務

1. **用 `cargo add` 管理依賴，不要直接編輯 `Cargo.toml`。** 新增和移除 Rust SDK 依賴一律用 cargo 指令，不要手動改 manifest。
2. **只有在直接 import `azure_core` 型別時才加 `azure_core`。** 如果你的程式碼 import 了 `azure_core::http::Url`、`azure_core::http::RequestContent` 或 `azure_core::error::ErrorKind`，就要加 `azure_core`，否則直接依賴是選用的。
3. **本機開發用 `DeveloperToolsCredential`**，**正式環境用 `ManagedIdentityCredential`**，Rust 沒有單一的 `DefaultAzureCredential` 型別
4. **絕對不要寫死憑證**，用環境變數或 managed identity
5. **更新 model struct 時用 `..Default::default()`**，並加上 `#[allow(clippy::needless_update)]`
6. **用 `ResourceExt`** 從金鑰 ID 取出金鑰名稱／版本
7. **重複使用 client**，`KeyClient` 是 thread-safe 的，建一次就好，在各 task 之間共用
8. **當 prompt、eval 或 CI 要求 lint 乾淨的輸出時，跑 `cargo clippy -- -D warnings`**

## 參考連結

| 資源          | 連結                                                                                            |
| ------------- | ----------------------------------------------------------------------------------------------- |
| API Reference | https://docs.rs/azure_security_keyvault_keys/latest/azure_security_keyvault_keys                |
| crates.io     | https://crates.io/crates/azure_security_keyvault_keys                                           |
| Source Code   | https://github.com/Azure/azure-sdk-for-rust/tree/main/sdk/keyvault/azure_security_keyvault_keys |
