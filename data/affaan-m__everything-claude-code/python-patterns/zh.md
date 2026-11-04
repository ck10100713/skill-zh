---
name: python-patterns
description: Pythonic 慣用寫法、PEP 8 標準、type hint，以及建構穩健、高效、好維護的 Python 應用程式的最佳實踐。撰寫或 review Python 程式碼，且慣用的結構、型別標註或 PEP 8 有疑問時使用。
metadata:
  origin: ECC
---

# Python 開發模式

建構穩健、高效、好維護的應用程式所需的 Python 慣用模式與最佳實踐。

## 何時啟用

- 撰寫新的 Python 程式碼
- Review Python 程式碼
- 重構既有的 Python 程式碼
- 設計 Python 的 package/模組

## 核心原則

### 1. 可讀性很重要

Python 把可讀性放在第一位。程式碼應該一目了然、容易理解。

```python
# Good: 清楚、好讀
def get_active_users(users: list[User]) -> list[User]:
    """Return only active users from the provided list."""
    return [user for user in users if user.is_active]


# Bad: 很聰明但讓人看不懂
def get_active_users(u):
    return [x for x in u if x.a]
```

### 2. 明確優於隱含

避免魔法；要清楚說明你的程式碼在做什麼。

```python
# Good: 明確的設定
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Bad: 隱藏的副作用
import some_module
some_module.setup()  # 這在做什麼？
```

### 3. EAFP：請求原諒比請求許可容易

Python 偏好用例外處理，而不是檢查條件。

```python
# Good: EAFP 風格
def get_value(dictionary: dict, key: str, default_value: Any = None) -> Any:
    try:
        return dictionary[key]
    except KeyError:
        return default_value

# Bad: LBYL（Look Before You Leap）風格
def get_value(dictionary: dict, key: str, default_value: Any = None) -> Any:
    if key in dictionary:
        return dictionary[key]
    else:
        return default_value
```

## Type Hint

### 基本型別標註

```python
from typing import Optional, List, Dict, Any

def process_user(
    user_id: str,
    data: Dict[str, Any],
    active: bool = True
) -> Optional[User]:
    """Process a user and return the updated User or None."""
    if not active:
        return None
    return User(user_id, data)
```

### 現代的 Type Hint（Python 3.9+）

```python
# Python 3.9+：使用內建型別
def process_items(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}

# Python 3.8 以前：使用 typing 模組
from typing import List, Dict

def process_items(items: List[str]) -> Dict[str, int]:
    return {item: len(item) for item in items}
```

### Type Alias 與 TypeVar

```python
from typing import TypeVar, Union

# 複雜型別的 type alias
JSON = Union[dict[str, Any], list[Any], str, int, float, bool, None]

def parse_json(data: str) -> JSON:
    return json.loads(data)

# 泛型
T = TypeVar('T')

def first(items: list[T]) -> T | None:
    """Return the first item or None if list is empty."""
    return items[0] if items else None
```

### 以 Protocol 為基礎的 Duck Typing

```python
from typing import Protocol

class Renderable(Protocol):
    def render(self) -> str:
        """Render the object to a string."""

def render_all(items: list[Renderable]) -> str:
    """Render all items that implement the Renderable protocol."""
    return "\n".join(item.render() for item in items)
```

## 錯誤處理模式

### 處理特定的例外

```python
# Good: 捕捉特定的例外
def load_config(path: str) -> Config:
    try:
        with open(path) as f:
            return Config.from_json(f.read())
    except FileNotFoundError as e:
        raise ConfigError(f"Config file not found: {path}") from e
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in config: {path}") from e

# Bad: 裸的 except
def load_config(path: str) -> Config:
    try:
        with open(path) as f:
            return Config.from_json(f.read())
    except:
        return None  # 悄悄失敗！
```

### 例外串接

```python
def process_data(data: str) -> Result:
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as e:
        # 串接例外，保留 traceback
        raise ValueError(f"Failed to parse data: {data}") from e
```

### 自訂例外階層

```python
class AppError(Exception):
    """Base exception for all application errors."""
    pass

class ValidationError(AppError):
    """Raised when input validation fails."""
    pass

class NotFoundError(AppError):
    """Raised when a requested resource is not found."""
    pass

# 用法
def get_user(user_id: str) -> User:
    user = db.find_user(user_id)
    if not user:
        raise NotFoundError(f"User not found: {user_id}")
    return user
```

## Context Manager

### 資源管理

```python
# Good: 使用 context manager
def process_file(path: str) -> str:
    with open(path, 'r') as f:
        return f.read()

# Bad: 手動管理資源
def process_file(path: str) -> str:
    f = open(path, 'r')
    try:
        return f.read()
    finally:
        f.close()
```

### 自訂 Context Manager

```python
from contextlib import contextmanager

@contextmanager
def timer(name: str):
    """Context manager to time a block of code."""
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"{name} took {elapsed:.4f} seconds")

# 用法
with timer("data processing"):
    process_large_dataset()
```

### Context Manager Class

```python
class DatabaseTransaction:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        self.connection.begin_transaction()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.connection.commit()
        else:
            self.connection.rollback()
        return False  # 不要吞掉例外

# 用法
with DatabaseTransaction(conn):
    user = conn.create_user(user_data)
    conn.create_profile(user.id, profile_data)
```

## Comprehension 與 Generator

### List Comprehension

```python
# Good: 簡單的轉換用 list comprehension
names = [user.name for user in users if user.is_active]

# Bad: 手動寫迴圈
names = []
for user in users:
    if user.is_active:
        names.append(user.name)

# 複雜的 comprehension 應該展開
# Bad: 太複雜
result = [x * 2 for x in items if x > 0 if x % 2 == 0]

# Good: 用 generator function
def filter_and_transform(items: Iterable[int]) -> list[int]:
    result = []
    for x in items:
        if x > 0 and x % 2 == 0:
            result.append(x * 2)
    return result
```

### Generator Expression

```python
# Good: 用 generator 做惰性求值
total = sum(x * x for x in range(1_000_000))

# Bad: 會建立很大的中間 list
total = sum([x * x for x in range(1_000_000)])
```

### Generator Function

```python
def read_large_file(path: str) -> Iterator[str]:
    """Read a large file line by line."""
    with open(path) as f:
        for line in f:
            yield line.strip()

# 用法
for line in read_large_file("huge.txt"):
    process(line)
```

## Data Class 與 Named Tuple

### Data Class

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    """User entity with automatic __init__, __repr__, and __eq__."""
    id: str
    name: str
    email: str
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

# 用法
user = User(
    id="123",
    name="Alice",
    email="alice@example.com"
)
```

### 帶驗證的 Data Class

```python
@dataclass
class User:
    email: str
    age: int

    def __post_init__(self):
        # 驗證 email 格式
        if "@" not in self.email:
            raise ValueError(f"Invalid email: {self.email}")
        # 驗證年齡範圍
        if self.age < 0 or self.age > 150:
            raise ValueError(f"Invalid age: {self.age}")
```

### Named Tuple

```python
from typing import NamedTuple

class Point(NamedTuple):
    """Immutable 2D point."""
    x: float
    y: float

    def distance(self, other: 'Point') -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

# 用法
p1 = Point(0, 0)
p2 = Point(3, 4)
print(p1.distance(p2))  # 5.0
```

## Decorator

### 函式 Decorator

```python
import functools
import time

def timer(func: Callable) -> Callable:
    """Decorator to time function execution."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)

# slow_function() 會印出：slow_function took 1.0012s
```

### 帶參數的 Decorator

```python
def repeat(times: int):
    """Decorator to repeat a function multiple times."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            results = []
            for _ in range(times):
                results.append(func(*args, **kwargs))
            return results
        return wrapper
    return decorator

@repeat(times=3)
def greet(name: str) -> str:
    return f"Hello, {name}!"

# greet("Alice") 會回傳 ["Hello, Alice!", "Hello, Alice!", "Hello, Alice!"]
```

### 以 Class 為基礎的 Decorator

```python
class CountCalls:
    """Decorator that counts how many times a function is called."""
    def __init__(self, func: Callable):
        functools.update_wrapper(self, func)
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"{self.func.__name__} has been called {self.count} times")
        return self.func(*args, **kwargs)

@CountCalls
def process():
    pass

# 每次呼叫 process() 都會印出呼叫次數
```

## 並行模式

### I/O 密集的任務用 Threading

```python
import concurrent.futures
import threading

def fetch_url(url: str) -> str:
    """Fetch a URL (I/O-bound operation)."""
    import urllib.request
    with urllib.request.urlopen(url) as response:
        return response.read().decode()

def fetch_all_urls(urls: list[str]) -> dict[str, str]:
    """Fetch multiple URLs concurrently using threads."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(fetch_url, url): url for url in urls}
        results = {}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                results[url] = future.result()
            except Exception as e:
                results[url] = f"Error: {e}"
    return results
```

### CPU 密集的任務用 Multiprocessing

```python
def process_data(data: list[int]) -> int:
    """CPU-intensive computation."""
    return sum(x ** 2 for x in data)

def process_all(datasets: list[list[int]]) -> list[int]:
    """Process multiple datasets using multiple processes."""
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(executor.map(process_data, datasets))
    return results
```

### 並行 I/O 用 Async/Await

```python
import asyncio

async def fetch_async(url: str) -> str:
    """Fetch a URL asynchronously."""
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def fetch_all(urls: list[str]) -> dict[str, str]:
    """Fetch multiple URLs concurrently."""
    tasks = [fetch_async(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return dict(zip(urls, results))
```

## Package 組織

### 標準專案結構

```
myproject/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       ├── main.py
│       ├── api/
│       │   ├── __init__.py
│       │   └── routes.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── user.py
│       └── utils/
│           ├── __init__.py
│           └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api.py
│   └── test_models.py
├── pyproject.toml
├── README.md
└── .gitignore
```

### Import 慣例

```python
# Good: import 的順序：標準函式庫、第三方、本地
import os
import sys
from pathlib import Path

import requests
from fastapi import FastAPI

from mypackage.models import User
from mypackage.utils import format_name

# Good: 用 isort 自動排序 import
# pip install isort
```

### 用 __init__.py 匯出 Package 的內容

```python
# mypackage/__init__.py
"""mypackage - A sample Python package."""

__version__ = "1.0.0"

# 在 package 層級匯出主要的 class/function
from mypackage.models import User, Post
from mypackage.utils import format_name

__all__ = ["User", "Post", "format_name"]
```

## 記憶體與效能

### 用 __slots__ 提升記憶體效率

```python
# Bad: 一般的 class 用 __dict__（比較吃記憶體）
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

# Good: __slots__ 減少記憶體用量
class Point:
    __slots__ = ['x', 'y']

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
```

### 大量資料用 Generator

```python
# Bad: 把整個 list 都回傳到記憶體裡
def read_lines(path: str) -> list[str]:
    with open(path) as f:
        return [line.strip() for line in f]

# Good: 一次 yield 一行
def read_lines(path: str) -> Iterator[str]:
    with open(path) as f:
        for line in f:
            yield line.strip()
```

### 避免在迴圈裡做字串串接

```python
# Bad: 因為字串不可變，是 O(n²)
result = ""
for item in items:
    result += str(item)

# Good: 用 join 是 O(n)
result = "".join(str(item) for item in items)

# Good: 用 StringIO 來組字串
from io import StringIO

buffer = StringIO()
for item in items:
    buffer.write(str(item))
result = buffer.getvalue()
```

## Python 工具整合

### 常用指令

```bash
# 程式碼格式化
black .
isort .

# Linting
ruff check .
pylint mypackage/

# 型別檢查
mypy .

# 測試
pytest --cov=mypackage --cov-report=html

# 安全掃描
bandit -r .

# 依賴管理
pip-audit
safety check
```

### pyproject.toml 設定

```toml
[project]
name = "mypackage"
version = "1.0.0"
requires-python = ">=3.9"
dependencies = [
    "requests>=2.31.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]

[tool.black]
line-length = 88
target-version = ['py39']

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W"]

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=mypackage --cov-report=term-missing"
```

## 速查：Python 慣用寫法

| 慣用寫法 | 說明 |
|-------|-------------|
| EAFP | 請求原諒比請求許可容易 |
| Context manager | 用 `with` 管理資源 |
| List comprehension | 用於簡單的轉換 |
| Generator | 用於惰性求值和大型資料集 |
| Type hint | 替函式簽章加上標註 |
| Dataclass | 用於資料容器，自動產生方法 |
| `__slots__` | 用於記憶體最佳化 |
| f-string | 用於字串格式化（Python 3.6+） |
| `pathlib.Path` | 用於路徑操作（Python 3.4+） |
| `enumerate` | 用於迴圈中同時取得索引和元素 |

## 要避免的反模式

```python
# Bad: 可變的預設引數
def append_to(item, items=[]):
    items.append(item)
    return items

# Good: 用 None，再建立新的 list
def append_to(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items

# Bad: 用 type() 檢查型別
if type(obj) == list:
    process(obj)

# Good: 用 isinstance
if isinstance(obj, list):
    process(obj)

# Bad: 用 == 跟 None 比較
if value == None:
    process()

# Good: 用 is
if value is None:
    process()

# Bad: from module import *
from os.path import *

# Good: 明確的 import
from os.path import join, exists

# Bad: 裸的 except
try:
    risky_operation()
except:
    pass

# Good: 特定的例外
try:
    risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
```

__記住__：Python 程式碼應該可讀、明確，並遵循最小驚訝原則。有疑問時，清楚比聰明重要。
