---
name: rust-async-patterns
description: 精通用 Tokio 寫 Rust 非同步程式，包含 async trait、錯誤處理和並行模式。在建構 async Rust 應用、實作並行系統或除錯 async 程式碼時使用。
---

# Rust Async Patterns

用 Tokio runtime 寫 async Rust 的正式環境等級模式，包含 task、channel、stream 和錯誤處理。

## When to Use This Skill

- 建構 async Rust 應用
- 實作並行的網路服務
- 用 Tokio 做 async I/O
- 正確處理 async 錯誤
- 除錯 async 程式碼的問題
- 優化 async 效能

## Core Concepts

### 1. Async Execution Model

```
Future (lazy) → poll() → Ready(value) | Pending
                ↑           ↓
              Waker ← Runtime schedules
```

### 2. Key Abstractions

| Concept    | Purpose                                  |
| ---------- | ---------------------------------------- |
| `Future`   | 惰性的計算，之後才可能完成 |
| `async fn` | 回傳 impl Future 的函式           |
| `await`    | 暫停，直到 future 完成             |
| `Task`     | 被 spawn 出去、並行執行的 future      |
| `Runtime`  | 負責 poll future 的 executor              |

## Quick Start

```toml
# Cargo.toml
[dependencies]
tokio = { version = "1", features = ["full"] }
futures = "0.3"
async-trait = "0.1"
anyhow = "1.0"
tracing = "0.1"
tracing-subscriber = "0.3"
```

```rust
use tokio::time::{sleep, Duration};
use anyhow::Result;

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt::init();

    // Async operations
    let result = fetch_data("https://api.example.com").await?;
    println!("Got: {}", result);

    Ok(())
}

async fn fetch_data(url: &str) -> Result<String> {
    // Simulated async operation
    sleep(Duration::from_millis(100)).await;
    Ok(format!("Data from {}", url))
}
```

## Detailed patterns and worked examples

詳細的 pattern 文件放在 `references/details.md`。上面這層導覽不夠用的時候，再去讀那個檔案。

## Best Practices

### Do's

- **用 `tokio::select!`** - 讓多個 future 互相競速
- **優先用 channel** - 盡量不要用共享狀態
- **用 `JoinSet`** - 管理多個 task
- **用 tracing 加 instrumentation** - 除錯 async 程式碼用
- **處理取消** - 檢查 `CancellationToken`

### Don'ts

- **不要 block** - async 裡絕對不要用 `std::thread::sleep`
- **不要跨 await 持有 lock** - 會造成 deadlock
- **不要無限制地 spawn** - 用 semaphore 設上限
- **不要忽略錯誤** - 用 `?` 往上傳，或記 log
- **不要忘了 Send 的限制** - 給被 spawn 的 future
