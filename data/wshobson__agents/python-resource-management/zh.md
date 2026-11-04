---
name: python-resource-management
description: 用 context manager、cleanup 模式和 streaming 來做 Python 資源管理。在管理連線、檔案 handle、實作清理邏輯，或建構帶累積狀態的 streaming 回應時使用。
---

# Python Resource Management

用 context manager 以確定的方式管理資源。資料庫連線、檔案 handle、網路 socket 這類資源，就算發生 exception 也要可靠地釋放。

## When to Use This Skill

- 管理資料庫連線和 connection pool
- 處理檔案 handle 和 I/O
- 實作自訂的 context manager
- 建構帶狀態的 streaming 回應
- 處理巢狀資源的清理
- 建立 async context manager

## Core Concepts

### 1. Context Managers

`with` 陳述式能確保資源自動釋放，就算發生 exception 也一樣。

### 2. Protocol Methods

同步資源管理用 `__enter__`/`__exit__`，非同步用 `__aenter__`/`__aexit__`。

### 3. Unconditional Cleanup

不管有沒有發生 exception，`__exit__` 一定會執行。

### 4. Exception Handling

`__exit__` 回傳 `True` 會吞掉 exception，回傳 `False` 則讓它繼續往外傳。

## Quick Start

```python
from contextlib import contextmanager

@contextmanager
def managed_resource():
    resource = acquire_resource()
    try:
        yield resource
    finally:
        resource.cleanup()

with managed_resource() as r:
    r.do_work()
```

## Fundamental Patterns

### Pattern 1: Class-Based Context Manager

複雜的資源，就實作 context manager protocol。

```python
class DatabaseConnection:
    """Database connection with automatic cleanup."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._conn: Connection | None = None

    def connect(self) -> None:
        """Establish database connection."""
        self._conn = psycopg.connect(self._dsn)

    def close(self) -> None:
        """Close connection if open."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "DatabaseConnection":
        """Enter context: connect and return self."""
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit context: always close connection."""
        self.close()

# Usage with context manager (preferred)
with DatabaseConnection(dsn) as db:
    result = db.execute(query)

# Manual management when needed
db = DatabaseConnection(dsn)
db.connect()
try:
    result = db.execute(query)
finally:
    db.close()
```

### Pattern 2: Async Context Manager

非同步資源，實作 async protocol。

```python
class AsyncDatabasePool:
    """Async database connection pool."""

    def __init__(self, dsn: str, min_size: int = 1, max_size: int = 10) -> None:
        self._dsn = dsn
        self._min_size = min_size
        self._max_size = max_size
        self._pool: asyncpg.Pool | None = None

    async def __aenter__(self) -> "AsyncDatabasePool":
        """Create connection pool."""
        self._pool = await asyncpg.create_pool(
            self._dsn,
            min_size=self._min_size,
            max_size=self._max_size,
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Close all connections in pool."""
        if self._pool is not None:
            await self._pool.close()

    async def execute(self, query: str, *args) -> list[dict]:
        """Execute query using pooled connection."""
        async with self._pool.acquire() as conn:
            return await conn.fetch(query, *args)

# Usage
async with AsyncDatabasePool(dsn) as pool:
    users = await pool.execute("SELECT * FROM users WHERE active = $1", True)
```

### Pattern 3: Using @contextmanager Decorator

簡單的情況，用 decorator 來簡化 context manager。

```python
from contextlib import contextmanager, asynccontextmanager
import time
import structlog

logger = structlog.get_logger()

@contextmanager
def timed_block(name: str):
    """Time a block of code."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        logger.info(f"{name} completed", duration_seconds=round(elapsed, 3))

# Usage
with timed_block("data_processing"):
    process_large_dataset()

@asynccontextmanager
async def database_transaction(conn: AsyncConnection):
    """Manage database transaction."""
    await conn.execute("BEGIN")
    try:
        yield conn
        await conn.execute("COMMIT")
    except BaseException:  # also roll back on asyncio.CancelledError
        await conn.execute("ROLLBACK")
        raise

# Usage
async with database_transaction(conn) as tx:
    await tx.execute("INSERT INTO users ...")
    await tx.execute("INSERT INTO audit_log ...")
```

### Pattern 4: Unconditional Resource Release

資源一律在 `__exit__` 裡清理，不管有沒有 exception。

```python
class FileProcessor:
    """Process file with guaranteed cleanup."""

    def __init__(self, path: str) -> None:
        self._path = path
        self._file: IO | None = None
        self._temp_files: list[Path] = []

    def __enter__(self) -> "FileProcessor":
        self._file = open(self._path, "r")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Clean up all resources unconditionally."""
        # Close main file
        if self._file is not None:
            self._file.close()

        # Clean up any temporary files
        for temp_file in self._temp_files:
            try:
                temp_file.unlink()
            except OSError:
                pass  # Best effort cleanup

        # Return None/False to propagate any exception
```

## Detailed worked examples and patterns

詳細的章節（從 `## Advanced Patterns` 開始）放在 `references/details.md`。上面的導覽摘要不夠用的時候，再去讀那個檔案。

## Best Practices Summary

1. **一律用 context manager** - 任何需要清理的資源都用
2. **無條件清理** - 就算發生 exception，`__exit__` 還是會跑
3. **不要意外吞掉 exception** - 除非是刻意要吞，否則回傳 `False`
4. **用 @contextmanager** - 處理簡單的資源模式
5. **兩種 protocol 都實作** - 同時支援 `with` 和手動管理
6. **用 ExitStack** - 處理數量不固定的資源
7. **有效率地累積** - 用 list + join，不要用字串串接
8. **追蹤指標** - 對 streaming 來說，time-to-first-byte 很重要
9. **把行為寫進文件** - 特別是 exception 被吞掉的行為
10. **測試清理路徑** - 確認出錯時資源有被釋放
