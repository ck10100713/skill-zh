---
name: python-error-handling
description: Python 錯誤處理模式，包含輸入驗證、例外階層與部分失敗的處理。在實作驗證邏輯、設計例外策略、處理批次處理的失敗，或建構穩健的 API 時使用。
---

# Python Error Handling

用適當的輸入驗證、有意義的例外與優雅的失敗處理，建構穩健的 Python 應用程式。好的錯誤處理讓除錯更容易，系統也更可靠。

## When to Use This Skill

- 驗證使用者輸入與 API 參數
- 為應用程式設計例外階層
- 處理批次操作中的部分失敗
- 把外部資料轉換成領域型別
- 建立對使用者友善的錯誤訊息
- 實作 fail-fast 的驗證模式

## Core Concepts

### 1. Fail Fast

在昂貴的操作之前就先驗證輸入。可行的話，一次回報所有驗證錯誤。

### 2. Meaningful Exceptions

使用適當的例外型別並附上 context。訊息應該說明什麼失敗了、為什麼，以及怎麼修正。

### 3. Partial Failures

在批次操作中，不要讓一個失敗就讓全部中止。把成功與失敗分開追蹤。

### 4. Preserve Context

串接例外，保留完整的錯誤軌跡以利除錯。

## Quick Start

```python
def fetch_page(url: str, page_size: int) -> Page:
    if not url:
        raise ValueError("'url' is required")
    if not 1 <= page_size <= 100:
        raise ValueError(f"'page_size' must be 1-100, got {page_size}")
    # Now safe to proceed...
```

## Fundamental Patterns

### Pattern 1: Early Input Validation

在開始任何處理之前，先在 API 邊界驗證所有輸入。

```python
def process_order(
    order_id: str,
    quantity: int,
    discount_percent: float,
) -> OrderResult:
    """Process an order with validation."""
    # Validate required fields
    if not order_id:
        raise ValueError("'order_id' is required")

    # Validate ranges
    if quantity <= 0:
        raise ValueError(f"'quantity' must be positive, got {quantity}")

    if not 0 <= discount_percent <= 100:
        raise ValueError(
            f"'discount_percent' must be 0-100, got {discount_percent}"
        )

    # Validation passed, proceed with processing
    return _process_validated_order(order_id, quantity, discount_percent)
```

### Pattern 2: Convert to Domain Types Early

在系統邊界就把字串與外部資料解析成有型別的領域物件。

```python
from enum import Enum

class OutputFormat(Enum):
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"

def parse_output_format(value: str) -> OutputFormat:
    """Parse string to OutputFormat enum.

    Args:
        value: Format string from user input.

    Returns:
        Validated OutputFormat enum member.

    Raises:
        ValueError: If format is not recognized.
    """
    try:
        return OutputFormat(value.lower())
    except ValueError:
        valid_formats = [f.value for f in OutputFormat]
        raise ValueError(
            f"Invalid format '{value}'. "
            f"Valid options: {', '.join(valid_formats)}"
        )

# Usage at API boundary
def export_data(data: list[dict], format_str: str) -> bytes:
    output_format = parse_output_format(format_str)  # Fail fast
    # Rest of function uses typed OutputFormat
    ...
```

### Pattern 3: Pydantic for Complex Validation

用 Pydantic model 做結構化的輸入驗證，並自動產生錯誤訊息。

```python
from pydantic import BaseModel, Field, field_validator

class CreateUserInput(BaseModel):
    """Input model for user creation."""

    email: str = Field(..., min_length=5, max_length=255)
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(ge=0, le=150)

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v.lower()

    @field_validator("name")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        return v.strip().title()

# Usage
try:
    user_input = CreateUserInput(
        email="user@example.com",
        name="john doe",
        age=25,
    )
except ValidationError as e:
    # Pydantic provides detailed error information
    print(e.errors())
```

### Pattern 4: Map Errors to Standard Exceptions

適當地使用 Python 內建的例外型別，並視需要加上 context。

| Failure Type | Exception | Example |
|--------------|-----------|---------|
| 無效輸入 | `ValueError` | 錯誤的參數值 |
| 型別錯誤 | `TypeError` | 預期字串，卻拿到 int |
| 缺少項目 | `KeyError` | 找不到 dict 的 key |
| 操作失敗 | `RuntimeError` | 服務無法使用 |
| 逾時 | `TimeoutError` | 操作花太久 |
| 找不到檔案 | `FileNotFoundError` | 路徑不存在 |
| 權限被拒 | `PermissionError` | 禁止存取 |

```python
# Good: Specific exception with context
raise ValueError(f"'page_size' must be 1-100, got {page_size}")

# Avoid: Generic exception, no context
raise Exception("Invalid parameter")
```

## Detailed worked examples and patterns

詳細的章節（從 `## Advanced Patterns` 開始）放在 `references/details.md`。上面的導覽摘要不夠用時，再去讀那個檔案。

## Best Practices Summary

1. **及早驗證** - 在昂貴的操作之前先檢查輸入
2. **使用特定的例外** - 用 `ValueError`、`TypeError`，不要用籠統的 `Exception`
3. **附上 context** - 訊息應該說明是什麼、為什麼，以及怎麼修正
4. **在邊界轉換型別** - 及早把字串解析成 enum/領域型別
5. **串接例外** - 用 `raise ... from e` 保留除錯資訊
6. **處理部分失敗** - 不要因為單一項目的錯誤就中止整批
7. **使用 Pydantic** - 用於複雜的輸入驗證，並取得結構化的錯誤
8. **記錄失敗模式** - Docstring 應該列出可能的例外
9. **記錄時附上 context** - 包含 ID、數量與其他除錯資訊
10. **測試錯誤路徑** - 驗證例外有被正確拋出
