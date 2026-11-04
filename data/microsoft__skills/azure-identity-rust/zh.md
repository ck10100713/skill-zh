---
name: azure-identity-rust
description: |
  Rust 用的 Azure Identity 函式庫。為所有 Azure SDK client 提供 Microsoft Entra ID 驗證。
  Triggers: "azure identity rust", "DeveloperToolsCredential", "authentication rust", "managed identity rust", "credential rust", "Entra ID rust".
license: MIT
metadata:
  author: Microsoft
  package: azure_identity
---

# Rust 用的 Azure Identity 函式庫

為 Azure SDK client 提供 Microsoft Entra ID 驗證。

這些情況用這個 skill：

- App 需要從 Rust 對 Azure 服務做驗證
- 本機開發需要 `DeveloperToolsCredential`
- 託管在 Azure 的工作負載需要 `ManagedIdentityCredential`
- 需要用 secret 或憑證做 service principal 驗證

> **重要：** 只能用 [azure-sdk](https://crates.io/users/azure-sdk) 這個 crates.io 使用者發佈的官方 `azure_*` crate。不要用已棄用的 `azure_sdk_*` crate（MindFlavor/AzureSDKForRust）或社群 crate。官方 crate 的名稱用底線，而且沒有任何一個版本是 0.21.0。

> **注意：** Rust SDK 沒有 `DefaultAzureCredential`。本機開發用 `DeveloperToolsCredential`，正式環境用 `ManagedIdentityCredential`。

```rust
// Rust 裡這樣寫是錯的：azure_identity 裡沒有這個型別
use azure_identity::DefaultAzureCredential;
```

## 安裝

```sh
cargo add azure_identity azure_core tokio
```

> 如果你的程式碼直接用到 `azure_core` 的型別，要把 `azure_core` 加進 `Cargo.toml`。如果只用服務 crate 重新匯出的東西，就不一定要直接依賴 `azure_core`。

## 環境變數

```bash
AZURE_TENANT_ID=<your-tenant-id>         # service principal 驗證必須設定
AZURE_CLIENT_ID=<your-client-id>         # service principal 或 user-assigned managed identity 必須設定
AZURE_CLIENT_SECRET=<your-client-secret> # ClientSecretCredential 必須設定
```

## 驗證

### DeveloperToolsCredential（本機開發）

先試 Azure CLI，再試 Azure Developer CLI：

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

    let secret = client.get_secret("secret-name", None).await?.into_model()?;
    println!("Secret: {:?}", secret.value);
    Ok(())
}
```

確認你已經登入：

```sh
az login        # Azure CLI
azd auth login  # 或 Azure Developer CLI
```

| 順序 | Credential                  | 登入指令         |
| ---- | --------------------------- | ---------------- |
| 1    | AzureCliCredential          | `az login`       |
| 2    | AzureDeveloperCliCredential | `azd auth login` |

### ManagedIdentityCredential（正式環境）

給託管在 Azure 的資源用（VM、App Service、Functions、AKS）：

```rust
use azure_identity::ManagedIdentityCredential;

// System-assigned managed identity
let credential = ManagedIdentityCredential::new(None)?;
```

### ClientSecretCredential（Service Principal）

給 CI/CD pipeline 和服務帳號用：

```rust
use azure_identity::ClientSecretCredential;

let credential = ClientSecretCredential::new(
    "<tenant-id>",
    "<client-id>",
    "<client-secret>",
    None,
)?;
```

## Credential 類型

| Credential                    | 使用情境                               |
| ----------------------------- | -------------------------------------- |
| `DeveloperToolsCredential`    | 本機開發：依序試 CLI 工具              |
| `ManagedIdentityCredential`   | Azure VM、App Service、Functions、AKS  |
| `WorkloadIdentityCredential`  | Kubernetes workload identity           |
| `ClientSecretCredential`      | 使用 secret 的 service principal       |
| `ClientCertificateCredential` | 使用憑證的 service principal           |
| `AzureCliCredential`          | 直接用 Azure CLI 驗證                  |
| `AzureDeveloperCliCredential` | 直接用 azd CLI 驗證                    |
| `AzurePipelinesCredential`    | Azure Pipelines 的 service connection  |
| `ClientAssertionCredential`   | 自訂 assertion（federated identity）   |

## 最佳實務

1. **用 `cargo add` 管理依賴，不要直接編輯 `Cargo.toml`。** 新增和移除 Rust SDK 依賴一律用 cargo 指令，不要手動改 manifest。
2. **只有在直接 import `azure_core` 型別時才加 `azure_core`。** 如果你的程式碼 import 了 `azure_core::http::Url`、`azure_core::http::RequestContent` 或 `azure_core::error::ErrorKind`，就要加 `azure_core`，否則直接依賴是選用的。
3. **本機開發用 `DeveloperToolsCredential`**，**正式環境用 `ManagedIdentityCredential`**，Rust 沒有單一的 `DefaultAzureCredential` 型別
4. **絕對不要寫死憑證**，service principal 用環境變數
5. **clone credential**：建構多個 client 時傳 `credential.clone()`，credential 是用 `Arc` 包起來的
6. **重複使用 client**，client 是 thread-safe 的，建一次就好，在各 task 之間共用
7. **指派 RBAC 角色**：確認這個身分在目標服務上有適當的角色（例如讀 secret 要有 "Key Vault Secrets User"）
8. **當 prompt、eval 或 CI 要求 lint 乾淨的輸出時，跑 `cargo clippy -- -D warnings`**；就算編譯錯誤修好了，Rust 的 trajectory grader 還是可能因為風格 lint 而失敗
9. **為 `#[non_exhaustive]` 的 SDK model 預留擴充空間**，建構 SDK 的 model／options struct 時，initializer 結尾加 `..Default::default()`（並加上 `#[allow(clippy::needless_update)]`），比對 SDK enum 時加一個 `_` 萬用分支，這樣服務端新增欄位或 variant 時才不會讓你的 build 壞掉

## 參考連結

| 資源          | 連結                                                                              |
| ------------- | --------------------------------------------------------------------------------- |
| API Reference | https://docs.rs/azure_identity/latest/azure_identity                              |
| crates.io     | https://crates.io/crates/azure_identity                                           |
| Source Code   | https://github.com/Azure/azure-sdk-for-rust/tree/main/sdk/identity/azure_identity |
