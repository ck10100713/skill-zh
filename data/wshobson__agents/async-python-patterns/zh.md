---
name: async-python-patterns
description: 掌握 Python asyncio、並行程式設計和 async/await 模式，打造高效能應用程式。在建構 async API、並行系統，或需要非阻塞操作的 I/O 密集應用程式時使用。
---

# Async Python 模式

用 asyncio、並行程式設計模式和 async/await 實作非同步 Python 應用程式的完整指引，用來建構高效能、非阻塞的系統。

## 何時使用這個 Skill

- 建構 async 的 web API（FastAPI、aiohttp、Sanic）
- 實作並行的 I/O 操作（資料庫、檔案、網路）
- 建立發出並行請求的網路爬蟲
- 開發即時應用程式（WebSocket 伺服器、聊天系統）
- 同時處理多個獨立的任務
- 建構用 async 溝通的 microservice
- 最佳化 I/O 密集的工作負載
- 實作 async 的背景任務和佇列

## 同步還是非同步的決策指南

採用 async 之前，先想想它是不是適合你的使用情境。

| 使用情境 | 建議做法 |
|----------|---------------------|
| 大量並行的網路/資料庫呼叫 | `asyncio` |
| CPU 密集的運算 | `multiprocessing` 或 thread pool |
| I/O 加 CPU 混合 | 用 `asyncio.to_thread()` 把 CPU 的工作卸載出去 |
| 簡單的 script、連線很少 | 同步（比較簡單、比較好除錯） |
| 高並行的 Web API | Async 框架（FastAPI、aiohttp） |

**關鍵規則：** 同一條呼叫路徑裡，要嘛全部同步，要嘛全部非同步。混用會產生隱藏的阻塞和複雜度。

## 核心概念

### 1. Event Loop

event loop 是 asyncio 的核心，負責管理和排程非同步的 task。

**主要特性：**

- 單執行緒的協作式多工
- 排程 coroutine 來執行
- 處理 I/O 操作而不阻塞
- 管理 callback 和 future

### 2. Coroutine

用 `async def` 定義、可以暫停和恢復的函式。

**語法：**

```python
async def my_coroutine():
    result = await some_async_operation()
    return result
```

### 3. Task

在 event loop 上並行執行、已排程的 coroutine。

### 4. Future

低階物件，代表非同步操作最終會有的結果。

### 5. Async Context Manager

支援 `async with` 來正確清理的資源。

### 6. Async Iterator

支援 `async for`、用來迭代非同步資料來源的物件。

## 快速開始

```python
import asyncio

async def main():
    print("Hello")
    await asyncio.sleep(1)
    print("World")

# Python 3.7+
asyncio.run(main())
```

## 基礎模式

### Pattern 1：基本的 Async/Await

```python
import asyncio

async def fetch_data(url: str) -> dict:
    """Fetch data from URL asynchronously."""
    await asyncio.sleep(1)  # Simulate I/O
    return {"url": url, "data": "result"}

async def main():
    result = await fetch_data("https://api.example.com")
    print(result)

asyncio.run(main())
```

### Pattern 2：用 gather() 並行執行

```python
import asyncio
from typing import List

async def fetch_user(user_id: int) -> dict:
    """Fetch user data."""
    await asyncio.sleep(0.5)
    return {"id": user_id, "name": f"User {user_id}"}

async def fetch_all_users(user_ids: List[int]) -> List[dict]:
    """Fetch multiple users concurrently."""
    tasks = [fetch_user(uid) for uid in user_ids]
    results = await asyncio.gather(*tasks)
    return results

async def main():
    user_ids = [1, 2, 3, 4, 5]
    users = await fetch_all_users(user_ids)
    print(f"Fetched {len(users)} users")

asyncio.run(main())
```

### Pattern 3：建立與管理 Task

```python
import asyncio

async def background_task(name: str, delay: int):
    """Long-running background task."""
    print(f"{name} started")
    await asyncio.sleep(delay)
    print(f"{name} completed")
    return f"Result from {name}"

async def main():
    # Create tasks
    task1 = asyncio.create_task(background_task("Task 1", 2))
    task2 = asyncio.create_task(background_task("Task 2", 1))

    # Do other work
    print("Main: doing other work")
    await asyncio.sleep(0.5)

    # Wait for tasks
    result1 = await task1
    result2 = await task2

    print(f"Results: {result1}, {result2}")

asyncio.run(main())
```

### Pattern 4：Async 程式碼的錯誤處理

```python
import asyncio
from typing import List, Optional

async def risky_operation(item_id: int) -> dict:
    """Operation that might fail."""
    await asyncio.sleep(0.1)
    if item_id % 3 == 0:
        raise ValueError(f"Item {item_id} failed")
    return {"id": item_id, "status": "success"}

async def safe_operation(item_id: int) -> Optional[dict]:
    """Wrapper with error handling."""
    try:
        return await risky_operation(item_id)
    except ValueError as e:
        print(f"Error: {e}")
        return None

async def process_items(item_ids: List[int]):
    """Process multiple items with error handling."""
    tasks = [safe_operation(iid) for iid in item_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out failures
    successful = [r for r in results if r is not None and not isinstance(r, Exception)]
    failed = [r for r in results if r is None or isinstance(r, Exception)]

    print(f"Success: {len(successful)}, Failed: {len(failed)}")
    return successful

asyncio.run(process_items([1, 2, 3, 4, 5, 6]))
```

### Pattern 5：逾時處理

```python
import asyncio

async def slow_operation(delay: int) -> str:
    """Operation that takes time."""
    await asyncio.sleep(delay)
    return f"Completed after {delay}s"

async def with_timeout():
    """Execute operation with timeout."""
    try:
        result = await asyncio.wait_for(slow_operation(5), timeout=2.0)
        print(result)
    except asyncio.TimeoutError:
        print("Operation timed out")

asyncio.run(with_timeout())
```

## 詳細的實作範例與模式

詳細的章節（從 `## Advanced Patterns` 開始）放在 `references/details.md`。上面的導覽摘要不夠用時，再讀那個檔案。

## 常見陷阱

### 1. 忘了 await

```python
# Wrong - returns coroutine object, doesn't execute
result = async_function()

# Correct
result = await async_function()
```

### 2. 阻塞 Event Loop

```python
# Wrong - blocks event loop
import time
async def bad():
    time.sleep(1)  # Blocks!

# Correct
async def good():
    await asyncio.sleep(1)  # Non-blocking
```

### 3. 沒處理取消

```python
async def cancelable_task():
    """Task that handles cancellation."""
    try:
        while True:
            await asyncio.sleep(1)
            print("Working...")
    except asyncio.CancelledError:
        print("Task cancelled, cleaning up...")
        # Perform cleanup
        raise  # Re-raise to propagate cancellation
```

### 4. 混用同步和非同步程式碼

```python
# Wrong - can't call async from sync directly
def sync_function():
    result = await async_function()  # SyntaxError!

# Correct
def sync_function():
    result = asyncio.run(async_function())
```

## 測試 Async 程式碼

```python
import asyncio
import pytest

# Using pytest-asyncio
@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await fetch_data("https://api.example.com")
    assert result is not None

@pytest.mark.asyncio
async def test_with_timeout():
    """Test with timeout."""
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_operation(5), timeout=1.0)
```
