---
name: fastapi-templates
description: 建立可上 production 的 FastAPI 專案，具備 async 模式、dependency injection 與完整的錯誤處理。適用於建構新的 FastAPI 應用或設定後端 API 專案的時候。
---

# FastAPI 專案範本

可上 production 的 FastAPI 專案結構，包含 async 模式、dependency injection、middleware，以及打造高效能 API 的最佳實務。

## 什麼時候用這個 Skill

- 從零開始新的 FastAPI 專案
- 用 Python 實作 async REST API
- 建構高效能的 web 服務與 microservices
- 搭配 PostgreSQL、MongoDB 建立 async 應用
- 建立結構與測試都完善的 API 專案

## 核心概念

### 1. 專案結構

**建議的目錄配置：**

```
app/
├── api/                    # API 路由
│   ├── v1/
│   │   ├── endpoints/
│   │   │   ├── users.py
│   │   │   ├── auth.py
│   │   │   └── items.py
│   │   └── router.py
│   └── dependencies.py     # 共用的 dependency
├── core/                   # 核心設定
│   ├── config.py
│   ├── security.py
│   └── database.py
├── models/                 # 資料庫 model
│   ├── user.py
│   └── item.py
├── schemas/                # Pydantic schema
│   ├── user.py
│   └── item.py
├── services/               # 商業邏輯
│   ├── user_service.py
│   └── auth_service.py
├── repositories/           # 資料存取
│   ├── user_repository.py
│   └── item_repository.py
└── main.py                 # 應用程式進入點
```

### 2. Dependency Injection

FastAPI 內建、使用 `Depends` 的 DI 系統：

- 資料庫 session 管理
- 驗證/授權
- 共用的商業邏輯
- 設定注入

### 3. Async 模式

正確使用 async/await：

- Async 的 route handler
- Async 的資料庫操作
- Async 的背景任務
- Async middleware

### 4. 相依套件

範例會 import 的套件：

```text
# requirements.txt
fastapi
uvicorn[standard]
pydantic-settings
sqlalchemy[asyncio]>=2.0  # DeclarativeBase；[asyncio] 會為 async engine 安裝 greenlet
asyncpg                   # PostgreSQL driver：postgresql+asyncpg://...
PyJWT
pwdlib[argon2]
python-multipart          # 只有用到 OAuth2PasswordRequestForm 的登入 route 才需要

# requirements-dev.txt
pytest
pytest-asyncio
httpx
aiosqlite                 # 測試用資料庫：sqlite+aiosqlite:///:memory:
```

## 詳細的實作範例與模式

詳細的章節（從 `## Implementation Patterns` 開始）放在 `references/details.md`，上面這份導覽摘要不夠用的時候再去讀那份檔案。

## 測試

```python
# tests/conftest.py
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db, Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# 在 pytest-asyncio 的預設 strict 模式下，async fixture 需要用 pytest_asyncio.fixture
@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with AsyncSessionLocal() as session:
        yield session
    await engine.dispose()

@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # httpx 0.28 移除了 AsyncClient(app=...)；改用 ASGI transport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()

# tests/test_users.py
import pytest

@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
```
