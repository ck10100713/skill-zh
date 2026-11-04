---
name: python-observability
description: Python 可觀測性模式，包含結構化 logging、指標與分散式追蹤。在加入 logging、實作指標收集、設定追蹤或除錯正式環境系統時使用。
---

# Python Observability

用結構化 log、指標與 trace 為 Python 應用程式做 instrumentation。正式環境出問題時，你需要不用部署新程式碼，就能回答「什麼、在哪、為什麼」。

## When to Use This Skill

- 為應用程式加入結構化 logging
- 用 Prometheus 實作指標收集
- 跨服務設定分散式追蹤
- 沿著請求鏈傳遞 correlation ID
- 除錯正式環境的問題
- 建立可觀測性 dashboard

## Core Concepts

### 1. Structured Logging

正式環境中，用一致的欄位把 log 輸出成 JSON。機器可讀的 log 能支援強大的查詢與警報。本機開發時，可以考慮用人類可讀的格式。

### 2. The Four Golden Signals

為每個服務邊界追蹤延遲、流量、錯誤與飽和度。

### 3. Correlation IDs

把單一請求的唯一 ID 貫穿所有 log 和 span，做到端到端的追蹤。

### 4. Bounded Cardinality

讓指標的 label 值保持有界。沒有上限的 label（像是使用者 ID）會讓儲存成本爆炸。

## Quick Start

```python
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)

logger = structlog.get_logger()
logger.info("Request processed", user_id="123", duration_ms=45)
```

## Fundamental Patterns

### Pattern 1: Structured Logging with Structlog

設定 structlog，用一致的欄位輸出 JSON。

```python
import logging
import structlog

def configure_logging(log_level: str = "INFO") -> None:
    """Configure structured logging for the application."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

# Initialize at application startup
configure_logging("INFO")
logger = structlog.get_logger()
```

### Pattern 2: Consistent Log Fields

每筆 log 都應該包含標準欄位，方便過濾與關聯。

```python
import structlog
from contextvars import ContextVar

# Store correlation ID in context
correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")

logger = structlog.get_logger()

def process_request(request: Request) -> Response:
    """Process request with structured logging."""
    logger.info(
        "Request received",
        correlation_id=correlation_id.get(),
        method=request.method,
        path=request.path,
        user_id=request.user_id,
    )

    try:
        result = handle_request(request)
        logger.info(
            "Request completed",
            correlation_id=correlation_id.get(),
            status_code=200,
            duration_ms=elapsed,
        )
        return result
    except Exception as e:
        logger.error(
            "Request failed",
            correlation_id=correlation_id.get(),
            error_type=type(e).__name__,
            error_message=str(e),
        )
        raise
```

### Pattern 3: Semantic Log Levels

在整個應用程式中，一致地使用 log level。

| Level | Purpose | Examples |
|-------|---------|----------|
| `DEBUG` | 開發時的診斷 | 變數值、內部狀態 |
| `INFO` | 請求生命週期、操作 | 請求開始/結束、job 完成 |
| `WARNING` | 可恢復的異常 | 重試、使用了 fallback |
| `ERROR` | 需要注意的失敗 | 例外、服務無法使用 |

```python
# DEBUG: Detailed internal information
logger.debug("Cache lookup", key=cache_key, hit=cache_hit)

# INFO: Normal operational events
logger.info("Order created", order_id=order.id, total=order.total)

# WARNING: Abnormal but handled situations
logger.warning(
    "Rate limit approaching",
    current_rate=950,
    limit=1000,
    reset_seconds=30,
)

# ERROR: Failures requiring investigation
logger.error(
    "Payment processing failed",
    order_id=order.id,
    error=str(e),
    payment_provider="stripe",
)
```

絕對不要把預期中的行為記成 `ERROR`。使用者輸入錯誤密碼是 `INFO`，不是 `ERROR`。

### Pattern 4: Correlation ID Propagation

在入口處產生一個唯一 ID，並貫穿所有操作。

```python
from contextvars import ContextVar
import uuid
import structlog

correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")

def set_correlation_id(cid: str | None = None) -> str:
    """Set correlation ID for current context."""
    cid = cid or str(uuid.uuid4())
    correlation_id.set(cid)
    structlog.contextvars.bind_contextvars(correlation_id=cid)
    return cid

# FastAPI middleware example
from fastapi import Request

async def correlation_middleware(request: Request, call_next):
    """Middleware to set and propagate correlation ID."""
    # Use incoming header or generate new
    cid = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    set_correlation_id(cid)

    response = await call_next(request)
    response.headers["X-Correlation-ID"] = cid
    return response
```

傳遞到對外的請求：

```python
import httpx

async def call_downstream_service(endpoint: str, data: dict) -> dict:
    """Call downstream service with correlation ID."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            endpoint,
            json=data,
            headers={"X-Correlation-ID": correlation_id.get()},
        )
        return response.json()
```

## Detailed worked examples and patterns

詳細的章節（從 `## Advanced Patterns` 開始）放在 `references/details.md`。上面的導覽摘要不夠用時，再去讀那個檔案。

## Best Practices Summary

1. **使用結構化 logging** - 欄位一致的 JSON log
2. **傳遞 correlation ID** - 貫穿所有請求與 log
3. **追蹤四大黃金訊號** - 延遲、流量、錯誤、飽和度
4. **限制 label 的基數** - 絕對不要把沒有上限的值當成指標 label
5. **用適當的 level 記錄** - 不要用 ERROR 狼來了
6. **附上 context** - 在 log 裡帶上使用者 ID、請求 ID、操作名稱
7. **使用 context manager** - 一致的計時與錯誤處理
8. **分離關注點** - 可觀測性程式碼不該污染業務邏輯
9. **測試你的可觀測性** - 在整合測試中驗證 log 與指標
10. **設定警報** - 沒有警報的指標是沒用的
