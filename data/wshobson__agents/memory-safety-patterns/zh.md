---
name: memory-safety-patterns
description: 在 Rust、C++ 和 C 中，用 RAII、ownership、智慧指標與資源管理來實作記憶體安全的程式。在撰寫安全的系統程式碼、管理資源或預防記憶體 bug 時使用。
---

# Memory Safety Patterns

跨語言的記憶體安全程式設計模式，包含 RAII、ownership、智慧指標與資源管理。

## When to Use This Skill

- 撰寫記憶體安全的系統程式碼
- 管理資源（檔案、socket、記憶體）
- 預防 use-after-free 與記憶體洩漏
- 實作 RAII 模式
- 從安全性角度選擇語言
- 除錯記憶體問題

## Core Concepts

### 1. Memory Bug Categories

| Bug Type             | Description                      | Prevention        |
| -------------------- | -------------------------------- | ----------------- |
| **Use-after-free**   | 存取已釋放的記憶體              | Ownership、RAII   |
| **Double-free**      | 同一塊記憶體釋放兩次           | 智慧指標    |
| **Memory leak**      | 記憶體從未釋放                | RAII、GC          |
| **Buffer overflow**  | 寫入超過 buffer 結尾            | 邊界檢查   |
| **Dangling pointer** | 指向已釋放記憶體的指標          | Lifetime 追蹤 |
| **Data race**        | 並行且未同步的存取 | Ownership、Sync   |

### 2. Safety Spectrum

```
Manual (C) → Smart Pointers (C++) → Ownership (Rust) → GC (Go, Java)
Less safe                                              More safe
More control                                           Less control
```

## Detailed patterns and worked examples

詳細的模式文件放在 `references/details.md`。上面的導覽層不夠用時，再去讀那個檔案。

## Best Practices

### Do's

- **優先用 RAII** - 讓資源的生命週期綁在 scope 上
- **使用智慧指標** - 在 C++ 避免裸指標
- **理解 ownership** - 搞清楚誰擁有什麼
- **檢查邊界** - 使用安全的存取方法
- **善用工具** - AddressSanitizer、Valgrind、Miri

### Don'ts

- **不要用裸指標** - 除非是要跟 C 介接
- **不要回傳區域變數的參照** - 會變成 dangling pointer
- **不要忽略編譯器警告** - 它們能抓到 bug
- **不要隨便用 `unsafe`** - 在 Rust 裡要盡量減少
- **不要假設 thread 安全** - 要明確處理

## Debugging Tools

```bash
# AddressSanitizer (Clang/GCC)
clang++ -fsanitize=address -g source.cpp

# Valgrind
valgrind --leak-check=full ./program

# Rust Miri (undefined behavior detector)
cargo +nightly miri run

# ThreadSanitizer
clang++ -fsanitize=thread -g source.cpp
```
