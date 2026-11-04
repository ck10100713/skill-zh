---
name: fastapi-router-py
description: 建立 FastAPI router，包含 CRUD 操作、驗證 dependency 和正確的 response model。在 FastAPI 應用程式中建 REST API endpoint、新增路由、實作 CRUD 操作，或加上需要驗證的 endpoint 時使用。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# FastAPI Router

依照既有的模式建立 FastAPI router，搭配正確的驗證、response model 和 HTTP 狀態碼。

## Quick Start

從 [assets/template.py](assets/template.py) 複製範本，並替換佔位符：
- `{{ResourceName}}` → PascalCase 名稱（例如 `Project`）
- `{{resource_name}}` → snake_case 名稱（例如 `project`）
- `{{resource_plural}}` → 複數形式（例如 `projects`）

## Authentication Patterns

```python
# Optional auth - returns None if not authenticated
current_user: Optional[User] = Depends(get_current_user)

# Required auth - raises 401 if not authenticated
current_user: User = Depends(get_current_user_required)
```

## Response Models

```python
@router.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: str) -> Item:
    ...

@router.get("/items", response_model=list[Item])
async def list_items() -> list[Item]:
    ...
```

## HTTP Status Codes

```python
@router.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate) -> Item:
  ...

@router.delete("/items/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(id: str) -> None:
  ...
```

## Integration Steps

1. 在 `src/backend/app/routers/` 建立 router
2. 在 `src/backend/app/main.py` 掛載
3. 建立對應的 Pydantic model
4. 需要的話建立 service layer
5. 加上前端的 API 函式

## Best Practices

1. **每個 endpoint 依照有沒有呼叫非同步 I/O 來選 `def` 或 `async def`；不要在 `async def` handler 裡呼叫會阻塞的 I/O。**
2. **長期存活的資源（DB pool、HTTP client）放在 `lifespan` 裡管理，並透過 `Depends` 注入；**每個 request 才用的資源則用 `with`/`async with`。

## Reference Files

| File | Contents |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打的功能、各 operation group 的涵蓋範圍，以及正式環境檢查清單。 |
