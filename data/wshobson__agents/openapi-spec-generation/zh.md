---
name: openapi-spec-generation
description: 從程式碼、design-first 規格與驗證模式產生並維護 OpenAPI 3.1 規格。在建立 API 文件、產生 SDK 或確保 API 契約合規時使用。
---

# OpenAPI Spec Generation

為 RESTful API 建立、維護與驗證 OpenAPI 3.1 規格的完整模式。

## When to Use This Skill

- 從零開始建立 API 文件
- 從現有程式碼產生 OpenAPI 規格
- 設計 API 契約（design-first 做法）
- 對照規格驗證 API 實作
- 從規格產生 client SDK
- 建立 API 文件入口網站

## Core Concepts

### 1. OpenAPI 3.1 Structure

```yaml
openapi: 3.1.0
info:
  title: API Title
  version: 1.0.0
servers:
  - url: https://api.example.com/v1
paths:
  /resources:
    get: ...
components:
  schemas: ...
  securitySchemes: ...
```

### 2. Design Approaches

| Approach         | Description                  | Best For            |
| ---------------- | ---------------------------- | ------------------- |
| **Design-First** | 先寫規格再寫程式碼       | 新的 API、契約 |
| **Code-First**   | 從程式碼產生規格      | 現有的 API       |
| **Hybrid**       | 在程式碼上加註解，再產生規格 | 持續演進的 API       |

## Templates and detailed worked examples

完整的範本庫與詳細的範例放在 `references/details.md`。需要具體範本時，再去讀那個檔案。

## Best Practices

### Do's

- **使用 $ref** - 重用 schema、參數、回應
- **加上範例** - 真實世界的值能幫助使用者
- **記錄錯誤** - 所有可能的錯誤碼
- **為 API 做版本控管** - 放在 URL 或 header
- **規格的變更用語意化版本** - semantic versioning

### Don'ts

- **不要用籠統的描述** - 要寫得具體
- **不要跳過安全性** - 定義所有 scheme
- **不要忘記 nullable** - 對 null 要明確表示
- **不要混用風格** - 全程命名一致
- **不要寫死 URL** - 使用 server variable
