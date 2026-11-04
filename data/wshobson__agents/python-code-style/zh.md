---
name: python-code-style
description: Python 的程式碼風格、linting、格式化、命名慣例與文件標準。在撰寫新程式碼、審查風格、設定 linter、撰寫 docstring 或建立專案標準時使用。
---

# Python Code Style & Documentation

一致的程式碼風格與清楚的文件，能讓程式碼庫好維護、好協作。這個 skill 涵蓋現代 Python 工具、命名慣例與文件標準。

## When to Use This Skill

- 為新專案設定 linting 與格式化
- 撰寫或審查 docstring
- 建立團隊的程式碼規範
- 設定 ruff、mypy 或 pyright
- 審查程式碼的風格一致性
- 建立專案文件

## Core Concepts

### 1. Automated Formatting

格式的爭論交給工具處理。設定一次，自動強制執行。

### 2. Consistent Naming

遵循 PEP 8 慣例，使用有意義、能描述內容的名稱。

### 3. Documentation as Code

Docstring 應該跟它所描述的程式碼一起維護。

### 4. Type Annotations

現代 Python 程式碼應該為所有公開 API 加上型別標註。

## Quick Start

```bash
# Install modern tooling
pip install ruff mypy

# Configure in pyproject.toml
[tool.ruff]
line-length = 120
target-version = "py312"  # Adjust based on your project's minimum Python version

[tool.mypy]
strict = true
```

## Fundamental Patterns

### Pattern 1: Modern Python Tooling

用 `ruff` 當成一體適用的 linter 與 formatter。它用單一的快速工具，取代 flake8、isort 和 black。

```toml
# pyproject.toml
[tool.ruff]
line-length = 120
target-version = "py312"  # Adjust based on your project's minimum Python version

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "UP",   # pyupgrade
    "SIM",  # flake8-simplify
]
ignore = ["E501"]  # Line length handled by formatter

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

執行方式：

```bash
ruff check --fix .  # Lint and auto-fix
ruff format .       # Format code
```

### Pattern 2: Type Checking Configuration

為正式環境的程式碼設定嚴格的型別檢查。

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_incomplete_defs = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

替代方案：用 `pyright` 做更快的檢查。

```toml
[tool.pyright]
pythonVersion = "3.12"
typeCheckingMode = "strict"
```

### Pattern 3: Naming Conventions

遵循 PEP 8，重視清楚多過簡短。

**檔案與模組：**

```python
# Good: Descriptive snake_case
user_repository.py
order_processing.py
http_client.py

# Avoid: Abbreviations
usr_repo.py
ord_proc.py
http_cli.py
```

**Class 與函式：**

```python
# Classes: PascalCase
class UserRepository:
    pass

class HTTPClientFactory:  # Acronyms stay uppercase
    pass

# Functions and variables: snake_case
def get_user_by_email(email: str) -> User | None:
    retry_count = 3
    max_connections = 100
```

**常數：**

```python
# Module-level constants: SCREAMING_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT_SECONDS = 30
API_BASE_URL = "https://api.example.com"
```

### Pattern 4: Import Organization

用一致的順序為 import 分組：標準函式庫、第三方、本地。

```python
# Standard library
import os
from collections.abc import Callable
from typing import Any

# Third-party packages
import httpx
from pydantic import BaseModel
from sqlalchemy import Column

# Local imports
from myproject.models import User
from myproject.services import UserService
```

只使用絕對 import：

```python
# Preferred
from myproject.utils import retry_decorator

# Avoid relative imports
from ..utils import retry_decorator
```

## Advanced Patterns

### Pattern 5: Google-Style Docstrings

為所有公開的 class、method 和函式撰寫 docstring。

**簡單的函式：**

```python
def get_user(user_id: str) -> User:
    """Retrieve a user by their unique identifier."""
    ...
```

**複雜的函式：**

```python
def process_batch(
    items: list[Item],
    max_workers: int = 4,
    on_progress: Callable[[int, int], None] | None = None,
) -> BatchResult:
    """Process items concurrently using a worker pool.

    Processes each item in the batch using the configured number of
    workers. Progress can be monitored via the optional callback.

    Args:
        items: The items to process. Must not be empty.
        max_workers: Maximum concurrent workers. Defaults to 4.
        on_progress: Optional callback receiving (completed, total) counts.

    Returns:
        BatchResult containing succeeded items and any failures with
        their associated exceptions.

    Raises:
        ValueError: If items is empty.
        ProcessingError: If the batch cannot be processed.

    Example:
        >>> result = process_batch(items, max_workers=8)
        >>> print(f"Processed {len(result.succeeded)} items")
    """
    ...
```

**Class 的 docstring：**

```python
class UserService:
    """Service for managing user operations.

    Provides methods for creating, retrieving, updating, and
    deleting users with proper validation and error handling.

    Attributes:
        repository: The data access layer for user persistence.
        logger: Logger instance for operation tracking.

    Example:
        >>> service = UserService(repository, logger)
        >>> user = service.create_user(CreateUserInput(...))
    """

    def __init__(self, repository: UserRepository, logger: Logger) -> None:
        """Initialize the user service.

        Args:
            repository: Data access layer for users.
            logger: Logger for tracking operations.
        """
        self.repository = repository
        self.logger = logger
```

### Pattern 6: Line Length and Formatting

為了現代的螢幕，把行寬設成 120 字元，同時保持可讀性。

```python
# Good: Readable line breaks
def create_user(
    email: str,
    name: str,
    role: UserRole = UserRole.MEMBER,
    notify: bool = True,
) -> User:
    ...

# Good: Chain method calls clearly
result = (
    db.query(User)
    .filter(User.active == True)
    .order_by(User.created_at.desc())
    .limit(10)
    .all()
)

# Good: Format long strings
error_message = (
    f"Failed to process user {user_id}: "
    f"received status {response.status_code} "
    f"with body {response.text[:100]}"
)
```

### Pattern 7: Project Documentation

**README 結構：**

```markdown
# Project Name

Brief description of what the project does.

## Installation

\`\`\`bash
pip install myproject
\`\`\`

## Quick Start

\`\`\`python
from myproject import Client

client = Client(api_key="...")
result = client.process(data)
\`\`\`

## Configuration

Document environment variables and configuration options.

## Development

\`\`\`bash
pip install -e ".[dev]"
pytest
\`\`\`
```

**CHANGELOG 格式（Keep a Changelog）：**

```markdown
# Changelog

## [Unreleased]

### Added
- New feature X

### Changed
- Modified behavior of Y

### Fixed
- Bug in Z
```

## Best Practices Summary

1. **使用 ruff** - 一個工具同時處理 linting 與格式化
2. **啟用嚴格的 mypy** - 在執行期之前就抓出型別錯誤
3. **120 字元行寬** - 現代的可讀性標準
4. **有描述性的名稱** - 清楚比簡短重要
5. **絕對 import** - 比相對 import 更好維護
6. **Google 風格的 docstring** - 一致、好讀的文件
7. **記錄公開 API** - 每個公開函式都需要 docstring
8. **保持文件更新** - 把文件當成程式碼對待
9. **在 CI 自動化** - 每次 commit 都跑 linter
10. **目標 Python 3.10+** - 新專案建議用 Python 3.12+，以使用現代語言特性
