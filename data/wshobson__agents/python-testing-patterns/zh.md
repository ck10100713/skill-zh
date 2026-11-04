---
name: python-testing-patterns
description: 用 pytest、fixture、mock 和測試驅動開發來落實完整的測試策略。在撰寫 Python 測試、建立測試套件或實作測試最佳實務時使用。
---

# Python Testing Patterns

一份完整指南，教你用 pytest、fixture、mock、參數化和測試驅動開發，在 Python 裡建立穩固的測試策略。

## When to Use This Skill

- 為 Python 程式碼寫 unit test
- 建立測試套件和測試基礎設施
- 實作測試驅動開發（TDD）
- 為 API 和服務建立整合測試
- Mock 外部依賴和服務
- 測試 async 程式碼和並行操作
- 在 CI/CD 設定持續測試
- 實作 property-based testing
- 測試資料庫操作
- 除錯失敗的測試

## Core Concepts

### 1. Test Types

- **Unit Tests**：單獨測試個別函式/class
- **Integration Tests**：測試元件之間的互動
- **Functional Tests**：端對端測試完整功能
- **Performance Tests**：量測速度和資源使用

### 2. Test Structure (AAA Pattern)

- **Arrange**：準備測試資料和前置條件
- **Act**：執行被測試的程式碼
- **Assert**：驗證結果

### 3. Test Coverage

- 量測哪些程式碼有被測試跑到
- 找出沒被測試的程式碼路徑
- 目標是有意義的覆蓋率，不是只追高百分比

### 4. Test Isolation

- 測試之間要互相獨立
- 測試之間不共用狀態
- 每個測試跑完要自己清理

## Quick Start

```python
# test_example.py
def add(a, b):
    return a + b

def test_add():
    """Basic test example."""
    result = add(2, 3)
    assert result == 5

def test_add_negative():
    """Test with negative numbers."""
    assert add(-1, 1) == 0

# Run with: pytest test_example.py
```

## Detailed patterns and worked examples

詳細的 pattern 文件放在 `references/details.md`。上面這層導覽不夠用的時候，再去讀那個檔案。

## Testing Best Practices

### Test Organization

```python
# tests/
#   __init__.py
#   conftest.py           # Shared fixtures
#   test_unit/            # Unit tests
#     test_models.py
#     test_utils.py
#   test_integration/     # Integration tests
#     test_api.py
#     test_database.py
#   test_e2e/            # End-to-end tests
#     test_workflows.py
```

### Test Naming Convention

常見的模式是 `test_<unit>_<scenario>_<expected_outcome>`。依你團隊的偏好調整。

```python
# Pattern: test_<unit>_<scenario>_<expected>
def test_create_user_with_valid_data_returns_user():
    ...

def test_create_user_with_duplicate_email_raises_conflict():
    ...

def test_get_user_with_unknown_id_returns_none():
    ...

# Good test names - clear and descriptive
def test_user_creation_with_valid_data():
    """Clear name describes what is being tested."""
    pass

def test_login_fails_with_invalid_password():
    """Name describes expected behavior."""
    pass

def test_api_returns_404_for_missing_resource():
    """Specific about inputs and expected outcomes."""
    pass

# Bad test names - avoid these
def test_1():  # Not descriptive
    pass

def test_user():  # Too vague
    pass

def test_function():  # Doesn't explain what's tested
    pass
```

### Testing Retry Behavior

用 mock 的 side effect 來驗證重試邏輯運作正常。

```python
from unittest.mock import Mock

def test_retries_on_transient_error():
    """Test that service retries on transient failures."""
    client = Mock()
    # Fail twice, then succeed
    client.request.side_effect = [
        ConnectionError("Failed"),
        ConnectionError("Failed"),
        {"status": "ok"},
    ]

    service = ServiceWithRetry(client, max_retries=3)
    result = service.fetch()

    assert result == {"status": "ok"}
    assert client.request.call_count == 3

def test_gives_up_after_max_retries():
    """Test that service stops retrying after max attempts."""
    client = Mock()
    client.request.side_effect = ConnectionError("Failed")

    service = ServiceWithRetry(client, max_retries=3)

    with pytest.raises(ConnectionError):
        service.fetch()

    assert client.request.call_count == 3

def test_does_not_retry_on_permanent_error():
    """Test that permanent errors are not retried."""
    client = Mock()
    client.request.side_effect = ValueError("Invalid input")

    service = ServiceWithRetry(client, max_retries=3)

    with pytest.raises(ValueError):
        service.fetch()

    # Only called once - no retry for ValueError
    assert client.request.call_count == 1
```

### Mocking Time with Freezegun

用 freezegun 在測試裡控制時間，讓跟時間有關的行為可以預測。

```python
from freezegun import freeze_time
from datetime import datetime, timedelta

@freeze_time("2026-01-15 10:00:00")
def test_token_expiry():
    """Test token expires at correct time."""
    token = create_token(expires_in_seconds=3600)
    assert token.expires_at == datetime(2026, 1, 15, 11, 0, 0)

@freeze_time("2026-01-15 10:00:00")
def test_is_expired_returns_false_before_expiry():
    """Test token is not expired when within validity period."""
    token = create_token(expires_in_seconds=3600)
    assert not token.is_expired()

@freeze_time("2026-01-15 12:00:00")
def test_is_expired_returns_true_after_expiry():
    """Test token is expired after validity period."""
    token = Token(expires_at=datetime(2026, 1, 15, 11, 30, 0))
    assert token.is_expired()

def test_with_time_travel():
    """Test behavior across time using freeze_time context."""
    with freeze_time("2026-01-01") as frozen_time:
        item = create_item()
        assert item.created_at == datetime(2026, 1, 1)

        # Move forward in time
        frozen_time.move_to("2026-01-15")
        assert item.age_days == 14
```

### Test Markers

```python
# test_markers.py
import pytest

@pytest.mark.slow
def test_slow_operation():
    """Mark slow tests."""
    import time
    time.sleep(2)


@pytest.mark.integration
def test_database_integration():
    """Mark integration tests."""
    pass


@pytest.mark.skip(reason="Feature not implemented yet")
def test_future_feature():
    """Skip tests temporarily."""
    pass


@pytest.mark.skipif(os.name == "nt", reason="Unix only test")
def test_unix_specific():
    """Conditional skip."""
    pass


@pytest.mark.xfail(reason="Known bug #123")
def test_known_bug():
    """Mark expected failures."""
    assert False


# Run with:
# pytest -m slow          # Run only slow tests
# pytest -m "not slow"    # Skip slow tests
# pytest -m integration   # Run integration tests
```

### Coverage Reporting

```bash
# Install coverage
pip install pytest-cov

# Run tests with coverage
pytest --cov=myapp tests/

# Generate HTML report
pytest --cov=myapp --cov-report=html tests/

# Fail if coverage below threshold
pytest --cov=myapp --cov-fail-under=80 tests/

# Show missing lines
pytest --cov=myapp --cov-report=term-missing tests/
```

進階 pattern（async 測試、monkeypatch、property-based testing、資料庫測試、CI/CD 整合和設定）請看 [references/advanced-patterns.md](references/advanced-patterns.md)
