---
name: python-anti-patterns
description: 在審查 Python 程式碼、找出要避免的常見反模式時使用這個 skill。在審查程式碼、定稿實作之前，或除錯可能源自已知壞習慣的問題時，當作檢查清單使用。
---

# Python Anti-Patterns Checklist

Python 程式碼常見錯誤與反模式的參考檢查清單。在定稿實作之前先看一遍，及早抓出問題。

## When to Use This Skill

- merge 前審查程式碼
- 除錯莫名其妙的問題
- 教學或學習 Python 最佳實務
- 建立團隊的程式碼規範
- 重構舊程式碼

**注意：** 這個 skill 專注在該避免什麼。想看正面的模式與架構指引，請見 `python-design-patterns` skill。

## Infrastructure Anti-Patterns

### Scattered Timeout/Retry Logic

```python
# BAD: Timeout logic duplicated everywhere
def fetch_user(user_id):
    try:
        return requests.get(url, timeout=30)
    except Timeout:
        logger.warning("Timeout fetching user")
        return None

def fetch_orders(user_id):
    try:
        return requests.get(url, timeout=30)
    except Timeout:
        logger.warning("Timeout fetching orders")
        return None
```

**修正：** 集中放在 decorator 或 client wrapper 裡。

```python
# GOOD: Centralized retry logic
@retry(stop=stop_after_attempt(3), wait=wait_exponential())
def http_get(url: str) -> Response:
    return requests.get(url, timeout=30)
```

### Double Retry

```python
# BAD: Retrying at multiple layers
@retry(max_attempts=3)  # Application retry
def call_service():
    return client.request()  # Client also has retry configured!
```

**修正：** 只在一個層級做 retry。要了解你的基礎設施的 retry 行為。

### Hard-Coded Configuration

```python
# BAD: Secrets and config in code
DB_HOST = "prod-db.example.com"
API_KEY = "sk-12345"

def connect():
    return psycopg.connect(f"host={DB_HOST}...")
```

**修正：** 用環境變數搭配有型別的設定。

```python
# GOOD
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_host: str = Field(alias="DB_HOST")
    api_key: str = Field(alias="API_KEY")

settings = Settings()
```

## Architecture Anti-Patterns

### Exposed Internal Types

```python
# BAD: Leaking ORM model to API
@app.get("/users/{id}")
def get_user(id: str) -> UserModel:  # SQLAlchemy model
    return db.query(UserModel).get(id)
```

**修正：** 使用 DTO/response model。

```python
# GOOD
@app.get("/users/{id}")
def get_user(id: str) -> UserResponse:
    user = db.query(UserModel).get(id)
    return UserResponse.from_orm(user)
```

### Mixed I/O and Business Logic

```python
# BAD: SQL embedded in business logic
def calculate_discount(user_id: str) -> float:
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    orders = db.query("SELECT * FROM orders WHERE user_id = ?", user_id)
    # Business logic mixed with data access
    if len(orders) > 10:
        return 0.15
    return 0.0
```

**修正：** 用 Repository pattern。讓業務邏輯保持純粹。

```python
# GOOD
def calculate_discount(user: User, orders: list[Order]) -> float:
    # Pure business logic, easily testable
    if len(orders) > 10:
        return 0.15
    return 0.0
```

## Error Handling Anti-Patterns

### Bare Exception Handling

```python
# BAD: Swallowing all exceptions
try:
    process()
except Exception:
    pass  # Silent failure - bugs hidden forever
```

**修正：** 捕捉特定的例外。適當地記錄或處理。

```python
# GOOD
try:
    process()
except ConnectionError as e:
    logger.warning("Connection failed, will retry", error=str(e))
    raise
except ValueError as e:
    logger.error("Invalid input", error=str(e))
    raise BadRequestError(str(e))
```

### Ignored Partial Failures

```python
# BAD: Stops on first error
def process_batch(items):
    results = []
    for item in items:
        result = process(item)  # Raises on error - batch aborted
        results.append(result)
    return results
```

**修正：** 同時記錄成功與失敗。

```python
# GOOD
def process_batch(items) -> BatchResult:
    succeeded = {}
    failed = {}
    for idx, item in enumerate(items):
        try:
            succeeded[idx] = process(item)
        except Exception as e:
            failed[idx] = e
    return BatchResult(succeeded, failed)
```

### Missing Input Validation

```python
# BAD: No validation
def create_user(data: dict):
    return User(**data)  # Crashes deep in code on bad input
```

**修正：** 在 API 邊界及早驗證。

```python
# GOOD
def create_user(data: dict) -> User:
    validated = CreateUserInput.model_validate(data)
    return User.from_input(validated)
```

## Resource Anti-Patterns

### Unclosed Resources

```python
# BAD: File never closed
def read_file(path):
    f = open(path)
    return f.read()  # What if this raises?
```

**修正：** 使用 context manager。

```python
# GOOD
def read_file(path):
    with open(path) as f:
        return f.read()
```

### Blocking in Async

```python
# BAD: Blocks the entire event loop
async def fetch_data():
    time.sleep(1)  # Blocks everything!
    response = requests.get(url)  # Also blocks!
```

**修正：** 使用 async 原生的函式庫。

```python
# GOOD
async def fetch_data():
    await asyncio.sleep(1)
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
```

## Type Safety Anti-Patterns

### Missing Type Hints

```python
# BAD: No types
def process(data):
    return data["value"] * 2
```

**修正：** 為所有公開函式加上型別標註。

```python
# GOOD
def process(data: dict[str, int]) -> int:
    return data["value"] * 2
```

### Untyped Collections

```python
# BAD: Generic list without type parameter
def get_users() -> list:
    ...
```

**修正：** 使用型別參數。

```python
# GOOD
def get_users() -> list[User]:
    ...
```

## Testing Anti-Patterns

### Only Testing Happy Paths

```python
# BAD: Only tests success case
def test_create_user():
    user = service.create_user(valid_data)
    assert user.id is not None
```

**修正：** 測試錯誤情況與邊界案例。

```python
# GOOD
def test_create_user_success():
    user = service.create_user(valid_data)
    assert user.id is not None

def test_create_user_invalid_email():
    with pytest.raises(ValueError, match="Invalid email"):
        service.create_user(invalid_email_data)

def test_create_user_duplicate_email():
    service.create_user(valid_data)
    with pytest.raises(ConflictError):
        service.create_user(valid_data)
```

### Over-Mocking

```python
# BAD: Mocking everything
def test_user_service():
    mock_repo = Mock()
    mock_cache = Mock()
    mock_logger = Mock()
    mock_metrics = Mock()
    # Test doesn't verify real behavior
```

**修正：** 關鍵路徑用整合測試。只 mock 外部服務。

## Quick Review Checklist

定稿程式碼之前，確認：

- [ ] 沒有分散的 timeout/retry 邏輯（已集中）
- [ ] 沒有 double retry（應用層 + 基礎設施層）
- [ ] 沒有寫死的設定或機密
- [ ] 沒有暴露內部型別（ORM model、protobuf）
- [ ] 沒有混在一起的 I/O 與業務邏輯
- [ ] 沒有裸的 `except Exception: pass`
- [ ] 沒有被忽略的批次部分失敗
- [ ] 沒有缺少輸入驗證
- [ ] 沒有未關閉的資源（使用 context manager）
- [ ] async 程式碼裡沒有阻塞呼叫
- [ ] 所有公開函式都有型別標註
- [ ] 集合都有型別參數
- [ ] 錯誤路徑都有測試
- [ ] 邊界案例都有涵蓋

## Common Fixes Summary

| Anti-Pattern | Fix |
|-------------|-----|
| 分散的 retry 邏輯 | 集中的 decorator |
| 寫死的設定 | 環境變數 + pydantic-settings |
| 暴露 ORM model | DTO/response schema |
| 混在一起的 I/O + 邏輯 | Repository pattern |
| 裸的 except | 捕捉特定的例外 |
| 批次遇錯就停 | 回傳含成功/失敗的 BatchResult |
| 沒有驗證 | 在邊界用 Pydantic 驗證 |
| 未關閉的資源 | Context manager |
| 在 async 裡阻塞 | async 原生的函式庫 |
| 缺少型別 | 所有公開 API 都加型別標註 |
| 只測 happy path | 測試錯誤與邊界案例 |
