---
name: go-concurrency-patterns
description: 精通 Go 並行，包含 goroutine、channel、同步原語與 context。適用於建構並行的 Go 應用、實作 worker pool，或除錯 race condition 的時候。
---

# Go 並行模式

Go 並行的 production 模式，包含 goroutine、channel、同步原語與 context 管理。

## 什麼時候用這個 Skill

- 建構並行的 Go 應用
- 實作 worker pool 與 pipeline
- 管理 goroutine 的生命週期
- 用 channel 做通訊
- 除錯 race condition
- 實作優雅關閉（graceful shutdown）

## 核心概念

### 1. Go 並行原語

| 原語              | 用途                             |
| ----------------- | -------------------------------- |
| `goroutine`       | 輕量的並行執行                   |
| `channel`         | goroutine 之間的通訊             |
| `select`          | 多工處理多個 channel 操作        |
| `sync.Mutex`      | 互斥鎖                           |
| `sync.WaitGroup`  | 等待 goroutine 完成              |
| `context.Context` | 取消與 deadline                  |

### 2. Go 並行口訣

```
Don't communicate by sharing memory;
share memory by communicating.
```

## 快速開始

```go
package main

import (
    "context"
    "fmt"
    "sync"
    "time"
)

func main() {
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    results := make(chan string, 10)
    var wg sync.WaitGroup

    // 啟動 worker
    for i := 0; i < 3; i++ {
        wg.Add(1)
        go worker(ctx, i, results, &wg)
    }

    // 完成後關閉 results
    go func() {
        wg.Wait()
        close(results)
    }()

    // 收集結果
    for result := range results {
        fmt.Println(result)
    }
}

func worker(ctx context.Context, id int, results chan<- string, wg *sync.WaitGroup) {
    defer wg.Done()

    select {
    case <-ctx.Done():
        return
    case results <- fmt.Sprintf("Worker %d done", id):
    }
}
```

## 詳細模式與實作範例

詳細的模式文件放在 `references/details.md`，上面這一層導覽不夠用的時候再去讀那份檔案。

## 最佳實務

### 該做的

- **使用 context**：用於取消與 deadline
- **關閉 channel**：只能從發送端關閉
- **使用 errgroup**：用於會回傳錯誤的並行操作
- **為 channel 加 buffer**：當你知道數量的時候
- **優先用 channel**：可以的話，優先於 mutex

### 不該做的

- **不要洩漏 goroutine**：一定要有退出的路徑
- **不要從接收端關閉**：會造成 panic
- **不要用共享記憶體**：除非必要
- **不要忽略 context 的取消**：要檢查 ctx.Done()
- **不要用 time.Sleep 來同步**：要用適當的原語
