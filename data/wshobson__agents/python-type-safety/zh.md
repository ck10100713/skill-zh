---
name: python-type-safety
description: 用 type hint、generic、protocol 和嚴格型別檢查來做 Python 型別安全。在加入型別註解、實作 generic class、定義結構化介面或設定 mypy/pyright 時使用。
---

# Python Type Safety

善用 Python 的型別系統，在靜態分析階段就抓出錯誤。型別註解就像是會被強制執行的文件，工具會自動幫你驗證。

## When to Use This Skill

- 為既有程式碼加上 type hint
- 建立可重複使用的 generic class
- 用 protocol 定義結構化介面
- 設定 mypy 或 pyright 做嚴格檢查
- 理解型別窄化（type narrowing）和 guard
- 建構型別安全的 API 和函式庫

## Core Concepts

### 1. Type Annotations

為函式參數、回傳值和變數宣告預期的型別。

### 2. Generics

寫出可重複使用的程式碼，同時在不同型別之間保留型別資訊。

### 3. Protocols

不靠繼承來定義結構化介面（有型別安全的 duck typing）。

### 4. Type Narrowing

用 guard 和條件判斷，在程式碼區塊內把型別縮小。

## Quick Start

```python
def get_user(user_id: str) -> User | None:
    """Return type makes 'might not exist' explicit."""
    ...

# Type checker enforces handling None case
user = get_user("123")
if user is None:
    raise UserNotFoundError("123")
print(user.name)  # Type checker knows user is User here
```

## Fundamental Patterns

### Pattern 1: Annotate All Public Signatures

每個公開的函式、method 和 class 都要有型別註解。

```python
def get_user(user_id: str) -> User:
    """Retrieve user by ID."""
    ...

def process_batch(
    items: list[Item],
    max_workers: int = 4,
) -> BatchResult[ProcessedItem]:
    """Process items concurrently."""
    ...

class UserRepository:
    def __init__(self, db: Database) -> None:
        self._db = db

    async def find_by_id(self, user_id: str) -> User | None:
        """Return User if found, None otherwise."""
        ...

    async def find_by_email(self, email: str) -> User | None:
        ...

    async def save(self, user: User) -> User:
        """Save and return user with generated ID."""
        ...
```

在 CI 裡用 `mypy --strict` 或 `pyright`，及早抓出型別錯誤。既有專案可以用逐模組的 override，一步步開啟 strict mode。

### Pattern 2: Use Modern Union Syntax

Python 3.10+ 提供了更乾淨的 union 語法。

```python
# Preferred (3.10+)
def find_user(user_id: str) -> User | None:
    ...

def parse_value(v: str) -> int | float | str:
    ...

# Older style (still valid, needed for 3.9)
from typing import Optional, Union

def find_user(user_id: str) -> Optional[User]:
    ...
```

### Pattern 3: Type Narrowing with Guards

用條件判斷幫型別檢查器縮小型別。

```python
def process_user(user_id: str) -> UserData:
    user = find_user(user_id)

    if user is None:
        raise UserNotFoundError(f"User {user_id} not found")

    # Type checker knows user is User here, not User | None
    return UserData(
        name=user.name,
        email=user.email,
    )

def process_items(items: list[Item | None]) -> list[ProcessedItem]:
    # Filter and narrow types
    valid_items = [item for item in items if item is not None]
    # valid_items is now list[Item]
    return [process(item) for item in valid_items]
```

### Pattern 4: Generic Classes

建立型別安全、可重複使用的容器。

```python
from typing import TypeVar, Generic

T = TypeVar("T")
E = TypeVar("E", bound=Exception)

class Result(Generic[T, E]):
    """Represents either a success value or an error."""

    def __init__(
        self,
        value: T | None = None,
        error: E | None = None,
    ) -> None:
        if (value is None) == (error is None):
            raise ValueError("Exactly one of value or error must be set")
        self._value = value
        self._error = error

    @property
    def is_success(self) -> bool:
        return self._error is None

    @property
    def is_failure(self) -> bool:
        return self._error is not None

    def unwrap(self) -> T:
        """Get value or raise the error."""
        if self._error is not None:
            raise self._error
        return self._value  # type: ignore[return-value]

    def unwrap_or(self, default: T) -> T:
        """Get value or return default."""
        if self._error is not None:
            return default
        return self._value  # type: ignore[return-value]

# Usage preserves types
def parse_config(path: str) -> Result[Config, ConfigError]:
    try:
        return Result(value=Config.from_file(path))
    except ConfigError as e:
        return Result(error=e)

result = parse_config("config.yaml")
if result.is_success:
    config = result.unwrap()  # Type: Config
```

## Detailed worked examples and patterns

詳細的章節（從 `## Advanced Patterns` 開始）放在 `references/details.md`。上面的導覽摘要不夠用的時候，再去讀那個檔案。

## Best Practices Summary

1. **所有公開 API 都加註解** - 函式、method、class 屬性
2. **用 `T | None`** - 用現代的 union 語法，不用 `Optional[T]`
3. **跑嚴格型別檢查** - 在 CI 裡跑 `mypy --strict`
4. **用 generic** - 在可重複使用的程式碼裡保留型別資訊
5. **定義 protocol** - 介面用結構化型別
6. **窄化型別** - 用 guard 幫型別檢查器一把
7. **限定型別變數的範圍（bound）** - 把 generic 限制在有意義的型別
8. **建立 type alias** - 給複雜型別一個有意義的名字
9. **盡量少用 `Any`** - 用具體型別或 generic。真正動態的資料，或是跟沒有型別的第三方程式碼介接時，用 `Any` 是可以的
10. **用型別當文件** - 型別是可以被強制執行的文件
