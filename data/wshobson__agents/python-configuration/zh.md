---
name: python-configuration
description: 透過環境變數與有型別的設定來管理 Python 設定。在把設定抽離程式碼、設定 pydantic-settings、管理機密，或實作依環境而異的行為時使用。
---

# Python Configuration Management

用環境變數與有型別的設定，把設定從程式碼中抽離出來。管理得當的設定，讓同一份程式碼不用修改就能在任何環境執行。

## When to Use This Skill

- 為新專案建立設定系統
- 從寫死的值遷移到環境變數
- 實作 pydantic-settings 做有型別的設定
- 管理機密與敏感的值
- 建立依環境而異的設定（dev/staging/prod）
- 在應用程式啟動時驗證設定

## Core Concepts

### 1. Externalized Configuration

所有依環境而異的值（URL、機密、feature flag）都來自環境變數，不是程式碼。

### 2. Typed Settings

在啟動時就把設定解析並驗證成有型別的物件，不要散落在程式碼各處。

### 3. Fail Fast

在應用程式啟動時就驗證所有必要的設定。缺少設定時應該立刻當掉，並給出清楚的訊息。

### 4. Sensible Defaults

為本機開發提供合理的預設值，但敏感設定要求明確提供值。

## Quick Start

```python
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(alias="DATABASE_URL")
    api_key: str = Field(alias="API_KEY")
    debug: bool = Field(default=False, alias="DEBUG")

settings = Settings()  # Loads from environment
```

## Fundamental Patterns

### Pattern 1: Typed Settings with Pydantic

建立一個集中的設定 class，負責載入並驗證所有設定。

```python
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn, ValidationError
import sys

class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Database
    db_host: str = Field(alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(alias="DB_NAME")
    db_user: str = Field(alias="DB_USER")
    db_password: str = Field(alias="DB_PASSWORD")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")

    # API Keys
    api_secret_key: str = Field(alias="API_SECRET_KEY")

    # Feature flags
    enable_new_feature: bool = Field(default=False, alias="ENABLE_NEW_FEATURE")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

# Create singleton instance at module load
try:
    settings = Settings()
except ValidationError as e:
    print(f"Configuration error:\n{e}")
    sys.exit(1)
```

在整個應用程式中 import `settings`：

```python
from myapp.config import settings

def get_database_connection():
    return connect(
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )
```

### Pattern 2: Fail Fast on Missing Configuration

必要的設定缺少時，應該讓應用程式立刻當掉，並給出清楚的錯誤。

```python
from pydantic_settings import BaseSettings
from pydantic import Field, ValidationError
import sys

class Settings(BaseSettings):
    # Required - no default means it must be set
    api_key: str = Field(alias="API_KEY")
    database_url: str = Field(alias="DATABASE_URL")

    # Optional with defaults
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

try:
    settings = Settings()
except ValidationError as e:
    print("=" * 60)
    print("CONFIGURATION ERROR")
    print("=" * 60)
    for error in e.errors():
        field = error["loc"][0]
        print(f"  - {field}: {error['msg']}")
    print("\nPlease set the required environment variables.")
    sys.exit(1)
```

啟動時的一個清楚錯誤，比請求處理到一半冒出來的莫名 `None` 失敗好得多。

### Pattern 3: Local Development Defaults

為本機開發提供合理的預設值，但機密要求明確提供值。

```python
class Settings(BaseSettings):
    # Has local default, but prod will override
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")

    # Always required - no default for secrets
    db_password: str = Field(alias="DB_PASSWORD")
    api_secret_key: str = Field(alias="API_SECRET_KEY")

    # Development convenience
    debug: bool = Field(default=False, alias="DEBUG")

    model_config = {"env_file": ".env"}
```

為本機開發建立一個 `.env` 檔（絕對不要 commit）：

```bash
# .env (add to .gitignore)
DB_PASSWORD=local_dev_password
API_SECRET_KEY=dev-secret-key
DEBUG=true
```

### Pattern 4: Namespaced Environment Variables

為相關的變數加上前綴，讓它們更清楚，也更容易除錯。

```bash
# Database configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
DB_USER=admin
DB_PASSWORD=secret

# Redis configuration
REDIS_URL=redis://localhost:6379
REDIS_MAX_CONNECTIONS=10

# Authentication
AUTH_SECRET_KEY=your-secret-key
AUTH_TOKEN_EXPIRY_SECONDS=3600
AUTH_ALGORITHM=HS256

# Feature flags
FEATURE_NEW_CHECKOUT=true
FEATURE_BETA_UI=false
```

這樣除錯時很容易列出資料庫相關的設定。只印出名稱，這樣就不會有任何值（例如連線 URL 裡的密碼）出現在你的終端機或 log 裡：

```bash
env | grep -o '^DB_[A-Za-z0-9_]*'
```

## Detailed worked examples and patterns

詳細的章節（從 `## Advanced Patterns` 開始）放在 `references/details.md`。上面的導覽摘要不夠用時，再去讀那個檔案。

## Best Practices Summary

1. **絕對不要寫死設定** - 所有依環境而異的值都來自環境變數
2. **使用有型別的設定** - 用 Pydantic-settings 搭配驗證
3. **盡早失敗** - 啟動時遇到缺少必要的設定就當掉
4. **提供開發用預設值** - 讓本機開發容易
5. **絕對不要 commit 機密** - 用 `.env` 檔（已 gitignore）或 secret manager
6. **為變數加命名空間** - 用 `DB_HOST`、`REDIS_URL` 讓意思清楚
7. **import settings 單例** - 不要在程式碼各處呼叫 `os.getenv()`
8. **記錄所有變數** - README 應該列出必要的環境變數
9. **及早驗證** - 在啟動時檢查設定是否正確
10. **使用 secrets_dir** - 支援在 container 中掛載的機密
