---
name: api-design-principles
description: 掌握 REST 和 GraphQL 的 API 設計原則，打造直覺、可擴充、好維護、讓開發者滿意的 API。在設計新 API、審查 API 規格，或建立 API 設計標準時使用。
---

# API 設計原則

掌握 REST 和 GraphQL 的 API 設計原則，打造直覺、可擴充、好維護、讓開發者滿意，而且經得起時間考驗的 API。

## 何時使用這個 Skill

- 設計新的 REST 或 GraphQL API
- 重構既有 API，讓它更好用
- 為你的團隊建立 API 設計標準
- 實作之前審查 API 規格
- 在不同 API 範式之間遷移（REST 到 GraphQL 等）
- 建立對開發者友善的 API 文件
- 針對特定使用情境最佳化 API（行動裝置、第三方整合）

## 核心概念

### 1. RESTful 設計原則

**以資源為導向的架構**

- 資源是名詞（users、orders、products），不是動詞
- 用 HTTP method 表達動作（GET、POST、PUT、PATCH、DELETE）
- URL 代表資源的階層
- 一致的命名慣例

**HTTP Method 的語意：**

- `GET`：取得資源（idempotent、安全）
- `POST`：建立新資源
- `PUT`：取代整個資源（idempotent）
- `PATCH`：部分更新資源
- `DELETE`：移除資源（idempotent）

### 2. GraphQL 設計原則

**Schema 優先的開發**

- 用型別定義你的領域模型
- 用 Query 讀取資料
- 用 Mutation 修改資料
- 用 Subscription 做即時更新

**Query 結構：**

- client 只要求自己需要的東西
- 單一 endpoint，多種操作
- 強型別的 schema
- 內建 introspection

### 3. API 版本策略

**URL 版本：**

```
/api/v1/users
/api/v2/users
```

**Header 版本：**

```
Accept: application/vnd.api+json; version=1
```

**Query Parameter 版本：**

```
/api/users?version=1
```

## 詳細模式與實作範例

詳細的模式文件放在 `references/details.md`。上面的導覽層不夠用時，再讀那個檔案。

## 最佳實務

### REST API

1. **一致的命名**：集合用複數名詞（`/users`，不是 `/user`）
2. **無狀態**：每個請求都包含所有必要的資訊
3. **正確使用 HTTP 狀態碼**：2xx 成功、4xx client 錯誤、5xx server 錯誤
4. **替 API 加版本**：從第一天就為破壞性變更做規劃
5. **分頁**：大型集合一律要分頁
6. **限流**：用 rate limit 保護你的 API
7. **文件**：用 OpenAPI/Swagger 做可互動的文件

### GraphQL API

1. **Schema 優先**：寫 resolver 之前先設計 schema
2. **避免 N+1**：用 DataLoader 有效率地取資料
3. **輸入驗證**：在 schema 和 resolver 兩層都要驗證
4. **錯誤處理**：在 mutation 的 payload 裡回傳結構化的錯誤
5. **分頁**：用 cursor-based 的分頁（Relay spec）
6. **棄用**：用 `@deprecated` directive 做漸進式遷移
7. **監控**：追蹤 query 的複雜度和執行時間

## 常見陷阱

- **Over-fetching/Under-fetching（REST）**：GraphQL 解決了，但需要 DataLoader
- **破壞性變更**：替 API 加版本，或用棄用策略
- **不一致的錯誤格式**：把錯誤回應標準化
- **缺少 rate limit**：沒有限制的 API 容易被濫用
- **文件不佳**：沒有文件的 API 讓開發者很挫折
- **忽略 HTTP 語意**：把 idempotent 的操作用 POST，會違背預期
- **緊密耦合**：API 結構不該照搬資料庫 schema
