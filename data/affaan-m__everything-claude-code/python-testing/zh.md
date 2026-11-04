---
name: python-testing
description: 使用 pytest 的 Python 測試策略，涵蓋 TDD 方法論、fixture、mocking、參數化和 coverage 要求。撰寫 pytest 測試（fixture、mock、參數化或 coverage）時使用。
metadata:
  origin: ECC
---

# Python 測試模式

用 pytest、TDD 方法論和最佳實踐，替 Python 應用程式建立完整的測試策略。

## 何時啟用

- 撰寫新的 Python 程式碼（走 TDD：red、green、refactor）
- 替 Python 專案設計測試套件
- Review Python 的測試 coverage
- 建置測試基礎設施

## 核心測試哲學

### 測試驅動開發（TDD）

一律照 TDD 的循環走：

1. **RED**：針對想要的行為，先寫一個會失敗的測試
2. **GREEN**：寫最少的程式碼，讓測試通過
3. **REFACTOR**：在測試保持綠燈的情況下改善程式碼

```python
# Step 1: 寫一個會失敗的測試 (RED)
def test_add_numbers():
    result = add(2, 3)
    assert result == 5

# Step 2: 寫最小的實作 (GREEN)
def add(a, b):
    return a + b

# Step 3: 需要的話就重構 (REFACTOR)
```

### Coverage 要求

- **目標**：80% 以上的程式碼 coverage
- **關鍵路徑**：要求 100% coverage
- 用 `pytest --cov` 來量測 coverage

```bash
pytest --cov=mypackage --cov-report=term-missing --cov-report=html
```

## pytest 基礎

### 基本的測試結構

```python
import pytest

def test_addition():
    """Test basic addition."""
    assert 2 + 2 == 4

def test_string_uppercase():
    """Test string uppercasing."""
    text = "hello"
    assert text.upper() == "HELLO"

def test_list_append():
    """Test list append."""
    items = [1, 2, 3]
    items.append(4)
    assert 4 in items
    assert len(items) == 4
```

### 斷言

```python
# 相等
assert result == expected

# 不相等
assert result != unexpected

# 真值判斷
assert result  # Truthy
assert not result  # Falsy
assert result is True  # 剛好是 True
assert result is False  # 剛好是 False
assert result is None  # 剛好是 None

# 成員判斷
assert item in collection
assert item not in collection

# 比較
assert result > 0
assert 0 <= result <= 100

# 型別檢查
assert isinstance(result, str)

# 例外測試（建議的做法）
with pytest.raises(ValueError):
    raise ValueError("error message")

# 檢查例外訊息
with pytest.raises(ValueError, match="invalid input"):
    raise ValueError("invalid input provided")

# 檢查例外的屬性
with pytest.raises(ValueError) as exc_info:
    raise ValueError("error message")
assert str(exc_info.value) == "error message"
```

## Fixture

### 基本的 Fixture 用法

```python
import pytest

@pytest.fixture
def sample_data():
    """Fixture providing sample data."""
    return {"name": "Alice", "age": 30}

def test_sample_data(sample_data):
    """Test using the fixture."""
    assert sample_data["name"] == "Alice"
    assert sample_data["age"] == 30
```

### 含 Setup/Teardown 的 Fixture

```python
@pytest.fixture
def database():
    """Fixture with setup and teardown."""
    # Setup
    db = Database(":memory:")
    db.create_tables()
    db.insert_test_data()

    yield db  # 提供給測試使用

    # Teardown
    db.close()

def test_database_query(database):
    """Test database operations."""
    result = database.query("SELECT * FROM users")
    assert len(result) > 0
```

### Fixture 的 Scope

```python
# Function scope（預設）：每個測試都會執行一次
@pytest.fixture
def temp_file():
    with open("temp.txt", "w") as f:
        yield f
    os.remove("temp.txt")

# Module scope：每個模組執行一次
@pytest.fixture(scope="module")
def module_db():
    db = Database(":memory:")
    db.create_tables()
    yield db
    db.close()

# Session scope：每個測試 session 執行一次
@pytest.fixture(scope="session")
def shared_resource():
    resource = ExpensiveResource()
    yield resource
    resource.cleanup()
```

### 帶參數的 Fixture

```python
@pytest.fixture(params=[1, 2, 3])
def number(request):
    """Parameterized fixture."""
    return request.param

def test_numbers(number):
    """Test runs 3 times, once for each parameter."""
    assert number > 0
```

### 使用多個 Fixture

```python
@pytest.fixture
def user():
    return User(id=1, name="Alice")

@pytest.fixture
def admin():
    return User(id=2, name="Admin", role="admin")

def test_user_admin_interaction(user, admin):
    """Test using multiple fixtures."""
    assert admin.can_manage(user)
```

### Autouse Fixture

```python
@pytest.fixture(autouse=True)
def reset_config():
    """Automatically runs before every test."""
    Config.reset()
    yield
    Config.cleanup()

def test_without_fixture_call():
    # reset_config 會自動執行
    assert Config.get_setting("debug") is False
```

### 用 Conftest.py 共用 Fixture (Flask)

```python
# tests/conftest.py
import pytest

@pytest.fixture
def client():
    """Shared fixture for all tests."""
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_headers(client):
    """Generate auth headers for API testing."""
    response = client.post("/api/login", json={
        "username": "test",
        "password": "test"
    })
    token = response.json["token"]
    return {"Authorization": f"Bearer {token}"}
```

## 參數化

### 基本的參數化

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("PyThOn", "PYTHON"),
])
def test_uppercase(input, expected):
    """Test runs 3 times with different inputs."""
    assert input.upper() == expected
```

### 多個參數

```python
@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_add(a, b, expected):
    """Test addition with multiple inputs."""
    assert add(a, b) == expected
```

### 用 ID 做參數化

```python
@pytest.mark.parametrize("input,expected", [
    ("valid@email.com", True),
    ("invalid", False),
    ("@no-domain.com", False),
], ids=["valid-email", "missing-at", "missing-domain"])
def test_email_validation(input, expected):
    """Test email validation with readable test IDs."""
    assert is_valid_email(input) is expected
```

### 參數化的 Fixture

```python
@pytest.fixture(params=["sqlite", "postgresql", "mysql"])
def db(request):
    """Test against multiple database backends."""
    if request.param == "sqlite":
        return Database(":memory:")
    elif request.param == "postgresql":
        return Database("postgresql://localhost/test")
    elif request.param == "mysql":
        return Database("mysql://localhost/test")

def test_database_operations(db):
    """Test runs 3 times, once for each database."""
    result = db.query("SELECT 1")
    assert result is not None
```

## Marker 與測試選取

### 自訂 Marker

```python
# 標記慢速測試
@pytest.mark.slow
def test_slow_operation():
    time.sleep(5)

# 標記整合測試
@pytest.mark.integration
def test_api_integration():
    response = requests.get("https://api.example.com")
    assert response.status_code == 200

# 標記單元測試
@pytest.mark.unit
def test_unit_logic():
    assert calculate(2, 3) == 5
```

### 執行特定的測試

```bash
# 只跑快速的測試
pytest -m "not slow"

# 只跑整合測試
pytest -m integration

# 跑整合測試或慢速測試
pytest -m "integration or slow"

# 跑標記為 unit 但不是 slow 的測試
pytest -m "unit and not slow"
```

### 在 pytest.ini 裡設定 Marker

```ini
[pytest]
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    django: marks tests as requiring Django
```

## Mocking 與 Patching

### Mock 函式

```python
from unittest.mock import patch, Mock

@patch("mypackage.external_api_call")
def test_with_mock(api_call_mock):
    """Test with mocked external API."""
    api_call_mock.return_value = {"status": "success"}

    result = my_function()

    api_call_mock.assert_called_once()
    assert result["status"] == "success"
```

### Mock 回傳值

```python
@patch("mypackage.Database.connect")
def test_database_connection(connect_mock):
    """Test with mocked database connection."""
    connect_mock.return_value = MockConnection()

    db = Database()
    db.connect()

    connect_mock.assert_called_once_with("localhost")
```

### Mock 例外

```python
@patch("mypackage.api_call")
def test_api_error_handling(api_call_mock):
    """Test error handling with mocked exception."""
    api_call_mock.side_effect = ConnectionError("Network error")

    with pytest.raises(ConnectionError):
        api_call()

    api_call_mock.assert_called_once()
```

### Mock Context Manager

```python
@patch("builtins.open", new_callable=mock_open)
def test_file_reading(mock_file):
    """Test file reading with mocked open."""
    mock_file.return_value.read.return_value = "file content"

    result = read_file("test.txt")

    mock_file.assert_called_once_with("test.txt", "r")
    assert result == "file content"
```

### 使用 Autospec

```python
@patch("mypackage.DBConnection", autospec=True)
def test_autospec(db_mock):
    """Test with autospec to catch API misuse."""
    db = db_mock.return_value
    db.query("SELECT * FROM users")

    # 如果 DBConnection 沒有 query method，這裡就會失敗
    db_mock.assert_called_once()
```

### Mock Class 的實例

```python
class TestUserService:
    @patch("mypackage.UserRepository")
    def test_create_user(self, repo_mock):
        """Test user creation with mocked repository."""
        repo_mock.return_value.save.return_value = User(id=1, name="Alice")

        service = UserService(repo_mock.return_value)
        user = service.create_user(name="Alice")

        assert user.name == "Alice"
        repo_mock.return_value.save.assert_called_once()
```

### Mock Property

```python
@pytest.fixture
def mock_config():
    """Create a mock with a property."""
    config = Mock()
    type(config).debug = PropertyMock(return_value=True)
    type(config).api_key = PropertyMock(return_value="test-key")
    return config

def test_with_mock_config(mock_config):
    """Test with mocked config properties."""
    assert mock_config.debug is True
    assert mock_config.api_key == "test-key"
```

## 測試非同步程式碼

### 用 pytest-asyncio 寫非同步測試

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await async_add(2, 3)
    assert result == 5

@pytest.mark.asyncio
async def test_async_with_fixture(async_client):
    """Test async with async fixture."""
    response = await async_client.get("/api/users")
    assert response.status_code == 200
```

### 非同步 Fixture (FastAPI)

`ASGITransport` 不會執行 lifespan 事件。當應用程式有 startup 或 shutdown handler 時，要安裝 `asgi-lifespan`，並把 client 包在 `LifespanManager` 裡。請見 [FastAPI 的非同步測試指引](https://github.com/fastapi/fastapi/blob/master/docs/en/docs/advanced/async-tests.md)。

```python
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

@pytest_asyncio.fixture
async def async_client():
    """Async fixture providing async test client with lifespan events."""
    app = create_app()  # 回傳一個 FastAPI 應用程式
    async with LifespanManager(app) as manager:
        async with AsyncClient(transport=ASGITransport(app=manager.app), base_url="http://test") as client:
            yield client

@pytest.mark.asyncio
async def test_api_endpoint(async_client):
    """Test using async fixture."""
    response = await async_client.get("/api/data")
    assert response.status_code == 200
```

### Mock 非同步函式

```python
@pytest.mark.asyncio
@patch("mypackage.async_api_call")
async def test_async_mock(api_call_mock):
    """Test async function with mock."""
    api_call_mock.return_value = {"status": "ok"}

    result = await my_async_function()

    api_call_mock.assert_awaited_once()
    assert result["status"] == "ok"
```

## 測試例外

### 測試預期中的例外

```python
def test_divide_by_zero():
    """Test that dividing by zero raises ZeroDivisionError."""
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_custom_exception():
    """Test custom exception with message."""
    with pytest.raises(ValueError, match="invalid input"):
        validate_input("invalid")
```

### 測試例外的屬性

```python
def test_exception_with_details():
    """Test exception with custom attributes."""
    with pytest.raises(CustomError) as exc_info:
        raise CustomError("error", code=400)

    assert exc_info.value.code == 400
    assert "error" in str(exc_info.value)
```

## 測試副作用

### 測試檔案操作

```python
import tempfile
import os

def test_file_processing():
    """Test file processing with temp file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("test content")
        temp_path = f.name

    try:
        result = process_file(temp_path)
        assert result == "processed: test content"
    finally:
        os.unlink(temp_path)
```

### 用 pytest 的 tmp_path Fixture 測試

```python
def test_with_tmp_path(tmp_path):
    """Test using pytest's built-in temp path fixture."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")

    result = process_file(str(test_file))
    assert result == "hello world"
    # tmp_path 會自動清理
```

### 用 tmpdir Fixture 測試

```python
def test_with_tmpdir(tmpdir):
    """Test using pytest's tmpdir fixture."""
    test_file = tmpdir.join("test.txt")
    test_file.write("data")

    result = process_file(str(test_file))
    assert result == "data"
```

## 測試組織

### 目錄結構

```
tests/
├── conftest.py                 # 共用的 fixture
├── __init__.py
├── unit/                       # 單元測試
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_utils.py
│   └── test_services.py
├── integration/                # 整合測試
│   ├── __init__.py
│   ├── test_api.py
│   └── test_database.py
└── e2e/                        # 端對端測試
    ├── __init__.py
    └── test_user_flow.py
```

### 測試 Class

```python
class TestUserService:
    """Group related tests in a class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup runs before each test in this class."""
        self.service = UserService()

    def test_create_user(self):
        """Test user creation."""
        user = self.service.create_user("Alice")
        assert user.name == "Alice"

    def test_delete_user(self):
        """Test user deletion."""
        user = User(id=1, name="Bob")
        self.service.delete_user(user)
        assert not self.service.user_exists(1)
```

## 最佳實踐

### 要做

- **走 TDD**：先寫測試再寫程式碼（red-green-refactor）
- **一次只測一件事**：每個測試只驗證單一行為
- **用有描述性的名稱**：`test_user_login_with_invalid_credentials_fails`
- **用 fixture**：用 fixture 消除重複
- **Mock 外部依賴**：不要依賴外部服務
- **測試邊界情況**：空輸入、None 值、邊界條件
- **目標 80% 以上的 coverage**：重點放在關鍵路徑
- **讓測試保持快速**：用 marker 把慢速測試分開

### 不要做

- **不要測實作細節**：測行為，不要測內部
- **不要在測試裡用複雜的條件判斷**：讓測試保持簡單
- **不要無視測試失敗**：所有測試都必須通過
- **不要測第三方的程式碼**：相信函式庫會運作
- **不要在測試之間共用狀態**：測試應該互相獨立
- **不要在測試裡捕捉例外**：用 `pytest.raises`
- **不要用 print**：用斷言和 pytest 的輸出
- **不要寫太脆弱的測試**：避免過度特定的 mock

## 常見模式

### 測試 API Endpoint (Flask)

```python
@pytest.fixture
def client():
    app = create_app(testing=True)
    return app.test_client()

def test_get_user(client):
    response = client.get("/api/users/1")
    assert response.status_code == 200
    assert response.json["id"] == 1

def test_create_user(client):
    response = client.post("/api/users", json={
        "name": "Alice",
        "email": "alice@example.com"
    })
    assert response.status_code == 201
    assert response.json["name"] == "Alice"
```

### 測試資料庫操作

```python
@pytest.fixture
def db_session():
    """Create a test database session."""
    session = Session(bind=engine)
    session.begin_nested()
    yield session
    session.rollback()
    session.close()

def test_create_user(db_session):
    user = User(name="Alice", email="alice@example.com")
    db_session.add(user)
    db_session.commit()

    retrieved = db_session.query(User).filter_by(name="Alice").first()
    assert retrieved.email == "alice@example.com"
```

### 測試 Class 的 Method

```python
class TestCalculator:
    @pytest.fixture
    def calculator(self):
        return Calculator()

    def test_add(self, calculator):
        assert calculator.add(2, 3) == 5

    def test_divide_by_zero(self, calculator):
        with pytest.raises(ZeroDivisionError):
            calculator.divide(10, 0)
```

## pytest 設定

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --disable-warnings
    --cov=mypackage
    --cov-report=term-missing
    --cov-report=html
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--cov=mypackage",
    "--cov-report=term-missing",
    "--cov-report=html",
]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
```

## 執行測試

```bash
# 執行所有測試
pytest

# 執行特定檔案
pytest tests/test_utils.py

# 執行特定測試
pytest tests/test_utils.py::test_function

# 詳細輸出
pytest -v

# 附帶 coverage
pytest --cov=mypackage --cov-report=html

# 只跑快速的測試
pytest -m "not slow"

# 跑到第一個失敗就停
pytest -x

# 失敗 N 個就停
pytest --maxfail=3

# 重跑上次失敗的測試
pytest --lf

# 依 pattern 執行測試
pytest -k "test_user"

# 失敗時啟動 debugger
pytest --pdb
```

## 速查

| 模式 | 用法 |
|---------|-------|
| `pytest.raises()` | 測試預期中的例外 |
| `@pytest.fixture()` | 建立可重複使用的測試 fixture |
| `@pytest.mark.parametrize()` | 用多組輸入執行測試 |
| `@pytest.mark.slow` | 標記慢速測試 |
| `pytest -m "not slow"` | 跳過慢速測試 |
| `@patch()` | Mock 函式和 class |
| `tmp_path` fixture | 自動的暫存目錄 |
| `pytest --cov` | 產生 coverage 報告 |
| `assert` | 簡單又好讀的斷言 |

**記住**：測試也是程式碼。要保持乾淨、好讀、好維護。好的測試能抓到 bug；很棒的測試能預防 bug。
