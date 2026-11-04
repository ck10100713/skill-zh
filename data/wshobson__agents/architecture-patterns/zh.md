---
name: architecture-patterns
description: 實作經過驗證的後端架構模式，包括 Clean Architecture、Hexagonal Architecture 和 Domain-Driven Design。為新的 microservice 設計 clean architecture、把 monolith 重構成 bounded context、實作 hexagonal 或 onion architecture 模式，或除錯應用層之間的相依循環時，使用這個 skill。
---

# 架構模式

掌握經過驗證的後端架構模式，包括 Clean Architecture、Hexagonal Architecture 和 Domain-Driven Design，建構好維護、可測試、可擴充的系統。

**給定：** 一個要設計架構的服務邊界或模組。
**產出：** 有明確相依規則的分層結構、介面定義和測試邊界。

## 何時使用這個 Skill

- 從零開始設計新的後端服務或 microservice
- 重構業務邏輯跟 ORM model 或 HTTP 關注點糾纏在一起的 monolith 應用程式
- 在把系統拆成服務之前，先建立 bounded context
- 除錯基礎設施程式碼滲進 domain 層造成的相依循環
- 建立可測試的程式碼庫，讓 use case 的測試不需要跑著資料庫
- 實作 domain-driven design 的戰術模式（aggregate、value object、domain event）

## 核心概念

### 1. Clean Architecture（Uncle Bob）

**分層（相依方向由外向內）：**

- **Entities**：核心業務模型，不 import 任何框架
- **Use Cases**：應用層的業務規則，負責編排 entity
- **Interface Adapters**：Controller、presenter、gateway，負責在 use case 和外部格式之間轉換
- **Frameworks & Drivers**：UI、資料庫、外部服務，全部放在最外圈

**關鍵原則：**

- 相依只往內指；內層對外層一無所知
- 業務邏輯獨立於框架、資料庫和交付機制
- 每一層的邊界都透過抽象介面來跨越
- 不需要 UI、資料庫或外部服務就能測試

### 2. Hexagonal Architecture（Ports and Adapters）

**元件：**

- **Domain Core**：業務邏輯放在這裡，不依賴框架
- **Ports**：抽象介面，定義核心如何跟外界互動（driving 和 driven）
- **Adapters**：port 的具體實作（PostgreSQL adapter、Stripe adapter、REST adapter）

**好處：**

- 換實作不用動到核心（例如把 PostgreSQL 換成 DynamoDB）
- 測試裡用 in-memory adapter，不需要 Docker
- 技術決策延後到邊緣再做

### 3. Domain-Driven Design（DDD）

**戰略模式：**

- **Bounded Contexts**：為一個子領域隔離出一致的模型；避免整個系統共用單一模型
- **Context Mapping**：定義各個 context 之間的關係（Anti-Corruption Layer、Shared Kernel、Open Host Service）
- **Ubiquitous Language**：程式碼裡的每個名詞，都對應領域專家使用的名詞

**戰術模式：**

- **Entities**：有穩定的身分、會隨時間改變的物件
- **Value Objects**：不可變、由屬性來識別的物件（Email、Money、Address）
- **Aggregates**：一致性邊界；只有 root 能從外部存取
- **Repositories**：持久化並重建 aggregate；對儲存機制做抽象
- **Domain Events**：記錄 domain 裡發生過的事；用於跨 aggregate 的協調

## 詳細模式與實作範例

詳細的模式文件放在 `references/details.md`。上面的導覽層不夠用時，再讀那個檔案。

## 測試：In-Memory Adapter

正確套用 Clean Architecture 的標誌，是每個 use case 都能在單純的單元測試裡執行，不需要真的資料庫、不需要 Docker、不需要網路：

```python
# tests/unit/test_create_user.py
import asyncio
from typing import Dict, Optional
from domain.entities.user import User
from domain.interfaces.user_repository import IUserRepository
from use_cases.create_user import CreateUserUseCase, CreateUserRequest


class InMemoryUserRepository(IUserRepository):
    def __init__(self):
        self._store: Dict[str, User] = {}

    async def find_by_id(self, user_id: str) -> Optional[User]:
        return self._store.get(user_id)

    async def find_by_email(self, email: str) -> Optional[User]:
        return next((u for u in self._store.values() if u.email == email), None)

    async def save(self, user: User) -> User:
        self._store[user.id] = user
        return user

    async def delete(self, user_id: str) -> bool:
        return self._store.pop(user_id, None) is not None


async def test_create_user_succeeds():
    repo = InMemoryUserRepository()
    use_case = CreateUserUseCase(user_repository=repo)

    response = await use_case.execute(CreateUserRequest(email="alice@example.com", name="Alice"))

    assert response.success
    assert response.user.email == "alice@example.com"
    assert response.user.id is not None


async def test_duplicate_email_rejected():
    repo = InMemoryUserRepository()
    use_case = CreateUserUseCase(user_repository=repo)

    await use_case.execute(CreateUserRequest(email="alice@example.com", name="Alice"))
    response = await use_case.execute(CreateUserRequest(email="alice@example.com", name="Alice2"))

    assert not response.success
    assert "already exists" in response.error
```

## 疑難排解

### Use case 的測試需要跑著資料庫

業務邏輯洩漏到基礎設施層了。把所有資料庫呼叫都放到 `IRepository` 介面後面，並在測試裡注入 in-memory 的實作（見上面的測試章節）。use case 的 constructor 必須接受抽象的 port，不是具體的類別。

### 各層之間的循環 import

常見的症狀是 `use_cases` 和 `adapters` 之間出現 `ImportError: cannot import name X`。這是因為 use case import 了具體的 adapter 類別，而不是抽象的 port。要強制執行這條規則：`use_cases/` 只能從 `domain/`（entity 和介面）import。絕對不能從 `adapters/` 或 `infrastructure/` import。

### 框架的 decorator 出現在 domain entity 裡

如果 SQLAlchemy 的 `Column()` 或 Pydantic 的 `Field()` 標註出現在 domain entity 上，這個 entity 就不再純淨了。在 `adapters/repositories/` 裡另外建一個 ORM model，並在 repository 的 `_to_entity()` 方法裡跟 domain entity 互相轉換。

### 所有邏輯最後都跑到 controller 裡

當 controller 的內容超過 HTTP 解析和回應格式化，就把邏輯抽到 use case 類別裡。controller 的方法只該做三件事：解析請求、呼叫 use case、轉換回應。

### Value object 太晚才丟出錯誤

在 `__post_init__`（Python）或 constructor 裡驗證不變條件，讓無效的 `Email` 或 `Money` 根本建不出來。這樣壞資料會在邊界就被抓出來，不是在業務邏輯深處才出事。

### Context 在 bounded context 之間滲漏

如果 `Order` context 在 import `Identity` context 的 `User` entity，就引進 Anti-Corruption Layer。`Order` context 應該有自己輕量的 `CustomerId` value object，而且只透過明確的介面去呼叫 `Identity` context。

## 進階模式

關於詳細的 DDD bounded context 對應、完整的多服務專案樹、Anti-Corruption Layer 的實作，以及 Onion Architecture 的比較，請見：

- [`references/advanced-patterns.md`](references/advanced-patterns.md)

## 相關 Skill

- `microservices-patterns`：把 monolith 拆成服務時，套用這些架構模式
- `cqrs-implementation`：用 Clean Architecture 當作 CQRS 指令/查詢分離的結構基礎
- `saga-orchestration`：Saga 需要定義清楚的 aggregate 邊界，而 DDD 的戰術模式正好提供這個
- `event-store-design`：aggregate 產生的 domain event 會直接餵進 event store
