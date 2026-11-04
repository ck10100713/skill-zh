---
name: python-project-structure
description: Python 專案組織、模組架構與公開 API 設計。在建立新專案、整理模組、用 __all__ 定義公開介面或規劃目錄結構時使用。
---

# Python Project Structure & Module Architecture

設計組織良好的 Python 專案：模組邊界清楚、公開介面明確、目錄結構好維護。組織得好，程式碼容易找，改動也容易預測。

## When to Use This Skill

- 從零開始一個新的 Python 專案
- 為了讓結構更清楚而重組現有的 codebase
- 用 `__all__` 定義模組的公開 API
- 在扁平和巢狀的目錄結構之間做選擇
- 決定測試檔案要放在哪裡
- 建立可重複使用的函式庫套件

## Core Concepts

### 1. Module Cohesion

把會一起改動的相關程式碼放在一起。一個模組應該只有一個明確的用途。

### 2. Explicit Interfaces

用 `__all__` 定義什麼是公開的。沒列進去的，一律視為內部實作細節。

### 3. Flat Hierarchies

目錄結構盡量淺。只有真的存在獨立子領域時才加深一層。

### 4. Consistent Conventions

命名和組織的慣例要在整個專案裡一致套用。

## Quick Start

```
myproject/
├── src/
│   └── myproject/
│       ├── __init__.py
│       ├── services/
│       ├── models/
│       └── api/
├── tests/
├── pyproject.toml
└── README.md
```

## Fundamental Patterns

### Pattern 1: One Concept Per File

每個檔案專注在單一概念，或一組關係密切的函式。出現以下狀況時，考慮拆檔：

- 處理好幾個互不相關的職責
- 超過 300-500 行（依複雜度而定）
- 包含會因為不同原因而改動的 class

```python
# Good: Focused files
# user_service.py - User business logic
# user_repository.py - User data access
# user_models.py - User data structures

# Avoid: Kitchen sink files
# user.py - Contains service, repository, models, utilities...
```

### Pattern 2: Explicit Public APIs with `__all__`

每個模組都要定義公開介面。沒列出的成員都是內部實作細節。

```python
# mypackage/services/__init__.py
from .user_service import UserService
from .order_service import OrderService
from .exceptions import ServiceError, ValidationError

__all__ = [
    "UserService",
    "OrderService",
    "ServiceError",
    "ValidationError",
]

# Internal helpers remain private by omission
# from .internal_helpers import _validate_input  # Not exported
```

### Pattern 3: Flat Directory Structure

巢狀盡量少。目錄太深會讓 import 變得冗長，也不好瀏覽。

```
# Preferred: Flat structure
project/
├── api/
│   ├── routes.py
│   └── middleware.py
├── services/
│   ├── user_service.py
│   └── order_service.py
├── models/
│   ├── user.py
│   └── order.py
└── utils/
    └── validation.py

# Avoid: Deep nesting
project/core/internal/services/impl/user/
```

只有真的需要隔離的子領域才加 sub-package。

### Pattern 4: Test File Organization

選一種做法，然後整個專案一致套用。

**Option A: Colocated Tests**

```
src/
├── user_service.py
├── test_user_service.py
├── order_service.py
└── test_order_service.py
```

好處：測試跟它要驗證的程式碼放在一起，很容易看出哪裡沒被覆蓋到。

**Option B: Parallel Test Directory**

```
src/
├── services/
│   ├── user_service.py
│   └── order_service.py
tests/
├── services/
│   ├── test_user_service.py
│   └── test_order_service.py
```

好處：正式程式碼和測試程式碼分得很乾淨。大型專案的標準做法。

## Advanced Patterns

### Pattern 5: Package Initialization

用 `__init__.py` 為套件的使用者提供乾淨的公開介面。

```python
# mypackage/__init__.py
"""MyPackage - A library for doing useful things."""

from .core import MainClass, HelperClass
from .exceptions import PackageError, ConfigError
from .config import Settings

__all__ = [
    "MainClass",
    "HelperClass",
    "PackageError",
    "ConfigError",
    "Settings",
]

__version__ = "1.0.0"
```

這樣使用者就可以直接從套件 import：

```python
from mypackage import MainClass, Settings
```

### Pattern 6: Layered Architecture

依架構分層來組織程式碼，讓關注點分離得更清楚。

```
myapp/
├── api/           # HTTP handlers, request/response
│   ├── routes/
│   └── middleware/
├── services/      # Business logic
├── repositories/  # Data access
├── models/        # Domain entities
├── schemas/       # API schemas (Pydantic)
└── config/        # Configuration
```

每一層只能依賴它下面的層，絕對不能往上依賴。

### Pattern 7: Domain-Driven Structure

複雜的應用程式，改用商業領域而不是技術分層來組織。

```
ecommerce/
├── users/
│   ├── models.py
│   ├── services.py
│   ├── repository.py
│   └── api.py
├── orders/
│   ├── models.py
│   ├── services.py
│   ├── repository.py
│   └── api.py
└── shared/
    ├── database.py
    └── exceptions.py
```

## File and Module Naming

### Conventions

- 所有檔案和模組名稱都用 `snake_case`：`user_repository.py`
- 避免會讓意思變模糊的縮寫：用 `user_repository.py`，不要用 `usr_repo.py`
- class 名稱要對應檔名：`UserService` 放在 `user_service.py`

### Import Style

用絕對 import，比較清楚也比較可靠：

```python
# Preferred: Absolute imports
from myproject.services import UserService
from myproject.models import User

# Avoid: Relative imports
from ..services import UserService
from . import models
```

模組被搬動或重組時，相對 import 可能會壞掉。

## Best Practices Summary

1. **檔案要專注** - 一個檔案一個概念，300-500 行左右考慮拆分（依複雜度而定）
2. **明確定義 `__all__`** - 讓公開介面一目了然
3. **偏好扁平結構** - 只有真的有子領域才加深
4. **用絕對 import** - 更可靠也更清楚
5. **保持一致** - 整個專案統一套用同樣的 pattern
6. **名稱要對應內容** - 檔名要能說明它的用途
7. **分離關注點** - 各層分明，依賴只往一個方向流
8. **把結構寫成文件** - 放一份 README 說明組織方式
