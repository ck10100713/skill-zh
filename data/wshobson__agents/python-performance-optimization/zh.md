---
name: python-performance-optimization
description: 用 cProfile、記憶體 profiler 和效能最佳實務來分析並優化 Python 程式碼。在除錯執行很慢的 Python 程式、優化瓶頸或提升應用程式效能時使用。
---

# Python Performance Optimization

一份完整指南，教你怎麼 profile、分析並優化 Python 程式碼來提升效能，包含 CPU profiling、記憶體優化和實作上的最佳實務。

## When to Use This Skill

- 找出 Python 應用程式的效能瓶頸
- 降低應用程式的延遲和回應時間
- 優化吃 CPU 的運算
- 降低記憶體用量和記憶體洩漏
- 提升資料庫查詢效能
- 優化 I/O 操作
- 加速資料處理 pipeline
- 實作高效能演算法
- 對正式環境的應用程式做 profiling

## Core Concepts

### 1. Profiling Types

- **CPU Profiling**：找出耗時的函式
- **Memory Profiling**：追蹤記憶體配置和洩漏
- **Line Profiling**：以逐行的粒度做 profiling
- **Call Graph**：把函式之間的呼叫關係視覺化

### 2. Performance Metrics

- **Execution Time**：操作花多久
- **Memory Usage**：記憶體用量的峰值和平均值
- **CPU Utilization**：處理器的使用模式
- **I/O Wait**：花在 I/O 操作上的時間

### 3. Optimization Strategies

- **Algorithmic**：更好的演算法和資料結構
- **Implementation**：更有效率的寫法
- **Parallelization**：多執行緒/多行程
- **Caching**：避免重複計算
- **Native Extensions**：關鍵路徑改用 C/Rust

## Quick Start

### Basic Timing

```python
import time

def measure_time():
    """Simple timing measurement."""
    start = time.time()

    # Your code here
    result = sum(range(1000000))

    elapsed = time.time() - start
    print(f"Execution time: {elapsed:.4f} seconds")
    return result

# Better: use timeit for accurate measurements
import timeit

execution_time = timeit.timeit(
    "sum(range(1000000))",
    number=100
)
print(f"Average time: {execution_time/100:.6f} seconds")
```

## Detailed patterns and worked examples

詳細的 pattern 文件放在 `references/details.md`。上面這層導覽不夠用的時候，再去讀那個檔案。

## Best Practices

1. **先 profile 再優化** - 先量測才找得到真正的瓶頸
2. **盯著 hot path** - 優化最常被執行的程式碼
3. **選對資料結構** - 查詢用 dict，判斷是否存在用 set
4. **避免過早優化** - 先求清楚，再來優化
5. **用內建函式** - 它們是用 C 實作的
6. **快取昂貴的運算** - 用 lru_cache
7. **批次處理 I/O** - 減少 system call
8. **大型資料集用 generator**
9. **數值運算考慮 NumPy**
10. **對正式環境的程式碼做 profile** - 線上系統用 py-spy

## Common Pitfalls

- 沒 profile 就開始優化
- 不必要地使用全域變數
- 沒用適當的資料結構
- 不必要地複製資料
- 資料庫沒用 connection pooling
- 忽略演算法複雜度
- 過度優化很少跑到的路徑
- 沒考慮記憶體用量
