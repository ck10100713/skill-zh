---
name: azure-keyvault-certificates-rust
description: |
  Rust 用的 Azure Key Vault Certificates 函式庫。建立、管理和使用 X.509 憑證，包含自簽和由 CA 簽發的。
  Triggers: "keyvault certificates rust", "CertificateClient rust", "create certificate rust", "self-signed certificate rust", "X.509 rust".
license: MIT
metadata:
  author: Microsoft
  package: azure_security_keyvault_certificates
---

# Rust 用的 Azure Key Vault Certificates 函式庫

管理用於 TLS/SSL、程式碼簽署和驗證的 X.509 憑證。

這些情況用這個 skill：

- App 需要從 Rust 在 Key Vault 建立或管理 X.509 憑證
- 需要自簽或由 CA 簽發的憑證
- 憑證簽發需要用到長時間執行的操作（LRO）
- 需要用憑證的金鑰來簽署資料

> **重要：** 只能用 [azure-sdk](https://crates.io/users/azure-sdk) 這個 crates.io 使用者發佈的官方 `azure_security_keyvault_certificates` crate。不要用非官方或社群的 crate。官方 crate 的名稱用底線，而且沒有任何一個版本是 0.21.0。

## 安裝

```sh
cargo add azure_security_keyvault_certificates azure_identity tokio futures
```

> 如果你的程式碼直接用到 `azure_core` 的型別，要把 `azure_core` 加進 `Cargo.toml`。如果只用 `azure_security_keyvault_certificates` 重新匯出的東西，就不一定要直接依賴 `azure_core`。

## 環境變數

```bash
AZURE_KEYVAULT_URL=https://<vault-name>.vault.azure.net/ # 所有操作都必須設定
```

## 驗證

Rust 的 Azure SDK 程式碼不能用 `DefaultAzureCredential`，因為 Rust 的 identity crate 沒有提供這個型別。

```rust
use azure_identity::DeveloperToolsCredential;
use azure_security_keyvault_certificates::CertificateClient;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 本機開發：DeveloperToolsCredential。正式環境：用 ManagedIdentityCredential。
    let credential = DeveloperToolsCredential::new(None)?;
    let client = CertificateClient::new(
        "https://<vault-name>.vault.azure.net/",
        credential.clone(),
        None,
    )?;

    let cert = client
        .get_certificate("cert-name", None)
        .await?
        .into_model()?;
    println!("Certificate: {:?}", cert.id);
    Ok(())
}
```

要確認 LRO 和 poller 的用法時，優先看 crate 的 README 和範例，不要從生成的內部型別去推測公開行為。

## 核心流程

### 建立自簽憑證（LRO）

建立憑證是長時間執行的操作。`Poller<T>` 實作了 `IntoFuture`，直接 `.await` 就好：

```rust
use azure_security_keyvault_certificates::{
    models::{
        CertificatePolicy, CreateCertificateParameters, IssuerParameters,
        X509CertificateProperties,
    },
    ResourceExt,
};

let policy = CertificatePolicy {
    x509_certificate_properties: Some(X509CertificateProperties {
        subject: Some("CN=example.com".into()),
        ..Default::default()
    }),
    issuer_parameters: Some(IssuerParameters {
        name: Some("Self".into()),
        ..Default::default()
    }),
    ..Default::default()
};
let body = CreateCertificateParameters {
    certificate_policy: Some(policy),
    ..Default::default()
};

// Poller 實作了 IntoFuture：直接 await 等它完成
let cert = client
    .begin_create_certificate("cert-name", body.try_into()?, None)?
    .await?
    .into_model()?;

println!(
    "Name: {:?}, Version: {:?}",
    cert.resource_id()?.name,
    cert.resource_id()?.version,
);
```

### 更新憑證屬性

```rust
use azure_security_keyvault_certificates::models::UpdateCertificatePropertiesParameters;
use std::collections::HashMap;

#[allow(clippy::needless_update)]
let params = UpdateCertificatePropertiesParameters {
    tags: Some(HashMap::from_iter(vec![("env".into(), "prod".into())])),
    ..Default::default()
};

client
    .update_certificate_properties("cert-name", params.try_into()?, None)
    .await?
    .into_model()?;
```

### 刪除憑證

```rust
client.delete_certificate("cert-name", None).await?;
```

### 列出憑證（分頁）

`list_certificate_properties` 回傳 `Pager<T>`，直接迭代 item 就好：

```rust
use azure_security_keyvault_certificates::ResourceExt;
use futures::TryStreamExt as _;

let mut pager = client.list_certificate_properties(None)?;
while let Some(cert) = pager.try_next().await? {
    println!("Found: {}", cert.resource_id()?.name);
}
```

## 用憑證的金鑰簽署

Key Vault 裡的憑證有一把對應的金鑰。加密操作要用 Key Vault Keys SDK：

```rust
use azure_security_keyvault_keys::{
    models::{KeyClientSignOptions, SignParameters, SignatureAlgorithm},
    KeyClient,
};

let key_client = KeyClient::new(
    "https://<vault-name>.vault.azure.net/",
    credential.clone(),
    None,
)?;

// 用憑證的 EC 金鑰簽署
let digest = vec![0u8; 32]; // SHA-256 digest
let body = SignParameters {
    algorithm: Some(SignatureAlgorithm::Es256),
    value: Some(digest),
};

let result = key_client
    .sign(
        "cert-name",
        body.try_into()?,
        Some(KeyClientSignOptions {
            key_version: Some("<certificate-version>".to_string()),
            ..Default::default()
        }),
    )
    .await?
    .into_model()?;
println!("Signature: {:?}", result.result);
```

## 憑證格式

| 格式    | Content Type             | 使用情境                            |
| ------- | ------------------------ | ----------------------------------- |
| PKCS#12 | `application/x-pkcs12`   | 憑證和私鑰綁在一起                  |
| PEM     | `application/x-pem-file` | Base64 編碼，Linux／web 常用        |

## RBAC 角色

用 Entra ID 驗證時，指派下面其中一個角色：

| 角色                             | 權限                |
| -------------------------------- | ------------------- |
| `Key Vault Certificate User`     | 使用憑證            |
| `Key Vault Certificates Officer` | 完整的憑證管理      |

## 最佳實務

1. **用 `cargo add` 管理依賴，不要直接編輯 `Cargo.toml`。** 新增和移除 Rust SDK 依賴一律用 cargo 指令，不要手動改 manifest。
2. **只有在直接 import `azure_core` 型別時才加 `azure_core`。** 如果你的程式碼 import 了 `azure_core::http::Url`、`azure_core::http::RequestContent` 或 `azure_core::error::ErrorKind`，就要加 `azure_core`，否則直接依賴是選用的。
3. **本機開發用 `DeveloperToolsCredential`**，**正式環境用 `ManagedIdentityCredential`**，Rust 沒有單一的 `DefaultAzureCredential` 型別
4. **絕對不要寫死憑證**，用環境變數或 managed identity
5. **更新 model struct 時用 `..Default::default()`**，並加上 `#[allow(clippy::needless_update)]`
6. **用 `ResourceExt`** 從 ID 取出憑證的名稱／版本
7. **LRO**：`begin_create_certificate` 回傳 `Poller`，直接 `.await` 等完成就好（client 很少需要去輪詢狀態）
8. **重複使用 client**，`CertificateClient` 是 thread-safe 的，建一次就好，在各 task 之間共用
9. **當 prompt、eval 或 CI 要求 lint 乾淨的輸出時，跑 `cargo clippy -- -D warnings`**

## 參考連結

| 資源          | 連結                                                                                                    |
| ------------- | ------------------------------------------------------------------------------------------------------- |
| API Reference | https://docs.rs/azure_security_keyvault_certificates/latest/azure_security_keyvault_certificates        |
| crates.io     | https://crates.io/crates/azure_security_keyvault_certificates                                           |
| Source Code   | https://github.com/Azure/azure-sdk-for-rust/tree/main/sdk/keyvault/azure_security_keyvault_certificates |
