---
name: pydantic-models-py
description: 依照 Base、Create、Update、Response、InDB 多模型模式建立 Pydantic 模型。適用於在使用 Pydantic v2 的 Python 應用程式中定義 API request/response schema、資料庫模型或資料驗證。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# Pydantic Models

依照多模型模式建立 Pydantic 模型，讓 API 契約乾淨清楚。

## 快速開始

從 [assets/template.py](assets/template.py) 複製範本，並替換 placeholder：
- `{{ResourceName}}` → PascalCase 名稱（例如 `Project`）
- `{{resource_name}}` → snake_case 名稱（例如 `project`）

## 多模型模式

| 模型 | 用途 |
|-------|---------|
| `Base` | 各模型共用的欄位 |
| `Create` | 建立用的 request body（必填欄位） |
| `Update` | 更新用的 request body（全部選填） |
| `Response` | 包含所有欄位的 API response |
| `InDB` | 帶有 `doc_type` 的資料庫文件 |

## camelCase 別名

```python
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class MyModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    workspace_id: str = Field(..., alias="workspaceId")
    created_at: datetime = Field(..., alias="createdAt")
```

## 選填的更新欄位

```python
class MyUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
```

## 資料庫文件

```python
class MyInDB(MyResponse):
    doc_type: str = "my_resource"
```

## 整合步驟

1. 在 `src/backend/app/models/` 建立模型
2. 從 `src/backend/app/models/__init__.py` export
3. 加上對應的 TypeScript 型別

## 參考檔案

| 檔案 | 內容 |
|------|----------|
| [references/capabilities.md](references/capabilities.md) | 其他非主打的功能、各 operation group 的涵蓋範圍，以及正式環境檢查清單。 |
