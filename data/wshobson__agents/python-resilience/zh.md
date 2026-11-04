---
name: python-resilience
description: Python 的韌性模式，包含自動重試、exponential backoff、timeout 和容錯 decorator。在加入重試邏輯、實作 timeout、建構容錯服務或處理暫時性失敗時使用。
---

# Python Resilience Patterns

打造容錯的 Python 應用程式，讓它能從容處理暫時性失敗、網路問題和服務中斷。依賴的服務不穩定時，這些韌性模式能讓系統繼續跑。

## When to Use This Skill

- 為外部服務呼叫加入重試邏輯
- 為網路操作實作 timeout
- 建構容錯的 microservice
- 處理 rate limiting 和 backpressure
- 建立基礎設施用的 decorator
- 設計 circuit breaker

## Core Concepts

### 1. Transient vs Permanent Failures

暫時性錯誤（網路 timeout、服務暫時出問題）要重試。永久性錯誤（憑證無效、錯誤的請求）不要重試。

### 2. Exponential Backoff

重試之間的等待時間逐步拉長，避免把正在恢復的服務打爆。

### 3. Jitter

在 backoff 加入隨機性，避免大量 client 同時重試造成 thundering herd。

### 4. Bounded Retries

重試次數和總時長都要設上限，避免無限重試的迴圈。

## Quick Start

```python
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=10),
)
def call_external_service(request: dict) -> dict:
    return httpx.post("https://api.example.com", json=request).json()
```

## Fundamental Patterns

### Pattern 1: Basic Retry with Tenacity

正式環境等級的重試邏輯，用 `tenacity` 函式庫。比較簡單的情況，可以考慮用內建的重試功能，或自己寫個輕量的實作。

```python
from tenacity import (
    retry,
    stop_after_attempt,
    stop_after_delay,
    wait_exponential_jitter,
    retry_if_exception_type,
)

TRANSIENT_ERRORS = (ConnectionError, TimeoutError, OSError)

@retry(
    retry=retry_if_exception_type(TRANSIENT_ERRORS),
    stop=stop_after_attempt(5) | stop_after_delay(60),
    wait=wait_exponential_jitter(initial=1, max=30),
)
def fetch_data(url: str) -> dict:
    """Fetch data with automatic retry on transient failures."""
    response = httpx.get(url, timeout=30)
    response.raise_for_status()
    return response.json()
```

### Pattern 2: Retry Only Appropriate Errors

只對明確列出的暫時性 exception 做重試（白名單）。以下這些絕對不要重試：

- `ValueError`、`TypeError` - 這些是 bug，不是暫時性問題
- `AuthenticationError` - 無效的憑證不會自己變有效
- HTTP 4xx 錯誤（429 除外）- client 端錯誤是永久性的

```python
from tenacity import retry, retry_if_exception_type
import httpx

# Define what's retryable
RETRYABLE_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    httpx.ConnectTimeout,
    httpx.ReadTimeout,
)

@retry(
    retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=10),
)
def resilient_api_call(endpoint: str) -> dict:
    """Make API call with retry on network issues."""
    return httpx.get(endpoint, timeout=10).json()
```

### Pattern 3: HTTP Status Code Retries

針對代表暫時性問題的特定 HTTP status code 做重試。

```python
from tenacity import retry, retry_if_result, stop_after_attempt
import httpx

RETRY_STATUS_CODES = {429, 502, 503, 504}

def should_retry_response(response: httpx.Response) -> bool:
    """Check if response indicates a retryable error."""
    return response.status_code in RETRY_STATUS_CODES

@retry(
    retry=retry_if_result(should_retry_response),
    stop=stop_after_attempt(3),
    wait=wait_exponential_jitter(initial=1, max=10),
)
def http_request(method: str, url: str, **kwargs) -> httpx.Response:
    """Make HTTP request with retry on transient status codes."""
    return httpx.request(method, url, timeout=30, **kwargs)
```

### Pattern 4: Combined Exception and Status Retry

網路 exception 和 HTTP status code 兩種都處理。

```python
from tenacity import (
    retry,
    retry_if_exception_type,
    retry_if_result,
    stop_after_attempt,
    wait_exponential_jitter,
    before_sleep_log,
)
import logging
import httpx

logger = logging.getLogger(__name__)

TRANSIENT_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    httpx.ConnectError,
    httpx.ReadTimeout,
)
RETRY_STATUS_CODES = {429, 500, 502, 503, 504}

def is_retryable_response(response: httpx.Response) -> bool:
    return response.status_code in RETRY_STATUS_CODES

@retry(
    retry=(
        retry_if_exception_type(TRANSIENT_EXCEPTIONS) |
        retry_if_result(is_retryable_response)
    ),
    stop=stop_after_attempt(5),
    wait=wait_exponential_jitter(initial=1, max=30),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
def robust_http_call(
    method: str,
    url: str,
    **kwargs,
) -> httpx.Response:
    """HTTP call with comprehensive retry handling."""
    return httpx.request(method, url, timeout=30, **kwargs)
```

## Detailed worked examples and patterns

詳細的章節（從 `## Advanced Patterns` 開始）放在 `references/details.md`。上面的導覽摘要不夠用的時候，再去讀那個檔案。

## Best Practices Summary

1. **只重試暫時性錯誤** - bug 和認證失敗不要重試
2. **用 exponential backoff** - 給服務時間恢復
3. **加 jitter** - 避免同步重試造成 thundering herd
4. **限制總時長** - `stop_after_attempt(5) | stop_after_delay(60)`
5. **每次重試都要記 log** - 悄悄重試會掩蓋系統性問題
6. **用 decorator** - 讓重試邏輯跟商業邏輯分開
7. **注入依賴** - 讓基礎設施程式碼可測試
8. **到處都設 timeout** - 每個網路呼叫都需要 timeout
9. **優雅降級** - 非關鍵路徑回傳快取值或預設值
10. **監控重試率** - 重試率偏高代表底層有問題
