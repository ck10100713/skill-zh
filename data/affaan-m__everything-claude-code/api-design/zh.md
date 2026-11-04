---
name: api-design
description: 給正式環境 API 用的 REST API 設計模式，包含資源命名、狀態碼、分頁、過濾、錯誤回應、版本管理和速率限制。設計或審查 REST endpoint、資源名稱、狀態碼、分頁或版本管理時使用。
metadata:
  origin: ECC
---

# API 設計模式

設計一致、對開發者友善的 REST API 的慣例與最佳實務。

## 何時啟用

- 設計新的 API endpoint
- 審查既有的 API 契約
- 加上分頁、過濾或排序
- 實作 API 的錯誤處理
- 規劃 API 的版本管理策略
- 建構公開或給合作夥伴用的 API

## 資源設計

### URL 結構

```
# 資源是名詞、複數、小寫、kebab-case
GET    /api/v1/users
GET    /api/v1/users/:id
POST   /api/v1/users
PUT    /api/v1/users/:id
PATCH  /api/v1/users/:id
DELETE /api/v1/users/:id

# 用子資源表示關聯
GET    /api/v1/users/:id/orders
POST   /api/v1/users/:id/orders

# 無法對應到 CRUD 的動作（動詞要節制使用）
POST   /api/v1/orders/:id/cancel
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
```

### 命名規則

```
# GOOD
/api/v1/team-members          # 多個單字的資源用 kebab-case
/api/v1/orders?status=active  # 過濾用 query 參數
/api/v1/users/123/orders      # 用巢狀資源表示擁有關係

# BAD
/api/v1/getUsers              # URL 裡有動詞
/api/v1/user                  # 單數（要用複數）
/api/v1/team_members          # URL 裡用 snake_case
/api/v1/users/123/getOrders   # 巢狀資源裡有動詞
```

## HTTP Method 與狀態碼

### Method 語意

| Method | 冪等 | 安全 | 用途 |
|--------|-----------|------|---------|
| GET | 是 | 是 | 取得資源 |
| POST | 否 | 否 | 建立資源、觸發動作 |
| PUT | 是 | 否 | 完整取代資源 |
| PATCH | 否* | 否 | 部分更新資源 |
| DELETE | 是 | 否 | 移除資源 |

*PATCH 只要實作得當，也可以做到冪等

### 狀態碼參考

```
# 成功
200 OK                    — GET、PUT、PATCH（有回應 body）
201 Created               — POST（要帶 Location header）
204 No Content            — DELETE、PUT（沒有回應 body）

# Client 錯誤
400 Bad Request           — 驗證失敗、JSON 格式錯誤
401 Unauthorized          — 缺少或無效的驗證
403 Forbidden             — 已驗證但沒有授權
404 Not Found             — 資源不存在
409 Conflict              — 重複的項目、狀態衝突
422 Unprocessable Entity  — 語意上無效（JSON 合法，但資料不對）
429 Too Many Requests     — 超過速率限制

# Server 錯誤
500 Internal Server Error — 非預期的失敗（絕對不要暴露細節）
502 Bad Gateway           — 上游服務失敗
503 Service Unavailable   — 暫時過載，要帶 Retry-After
```

### 常見錯誤

```
# BAD: 什麼都回 200
{ "status": 200, "success": false, "error": "Not found" }

# GOOD: 有語意地使用 HTTP 狀態碼
HTTP/1.1 404 Not Found
{ "error": { "code": "not_found", "message": "User not found" } }

# BAD: 驗證錯誤回 500
# GOOD: 回 400 或 422，並附欄位層級的細節

# BAD: 建立資源回 200
# GOOD: 回 201 並帶 Location header
HTTP/1.1 201 Created
Location: /api/v1/users/abc-123
```

## 回應格式

### 成功回應

```json
{
  "data": {
    "id": "abc-123",
    "email": "alice@example.com",
    "name": "Alice",
    "created_at": "2025-01-15T10:30:00Z"
  }
}
```

### 集合回應（含分頁）

```json
{
  "data": [
    { "id": "abc-123", "name": "Alice" },
    { "id": "def-456", "name": "Bob" }
  ],
  "meta": {
    "total": 142,
    "page": 1,
    "per_page": 20,
    "total_pages": 8
  },
  "links": {
    "self": "/api/v1/users?page=1&per_page=20",
    "next": "/api/v1/users?page=2&per_page=20",
    "last": "/api/v1/users?page=8&per_page=20"
  }
}
```

### 錯誤回應

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address",
        "code": "invalid_format"
      },
      {
        "field": "age",
        "message": "Must be between 0 and 150",
        "code": "out_of_range"
      }
    ]
  }
}
```

### 回應封包的不同寫法

```typescript
// 選項 A：用 data 包起來的封包（公開 API 建議用這個）
interface ApiResponse<T> {
  data: T;
  meta?: PaginationMeta;
  links?: PaginationLinks;
}

interface ApiError {
  error: {
    code: string;
    message: string;
    details?: FieldError[];
  };
}

// 選項 B：扁平的回應（比較簡單，內部 API 常用）
// 成功：直接回傳資源
// 錯誤：回傳 error 物件
// 靠 HTTP 狀態碼來區分
```

## 分頁

### Offset 式（簡單）

```
GET /api/v1/users?page=2&per_page=20

# 實作
SELECT * FROM users
ORDER BY created_at DESC
LIMIT 20 OFFSET 20;
```

**優點：** 容易實作，支援「跳到第 N 頁」
**缺點：** offset 大的時候很慢（OFFSET 100000），有並行新增時結果不一致

### Cursor 式（可擴展）

```
GET /api/v1/users?cursor=eyJpZCI6MTIzfQ&limit=20

# 實作
SELECT * FROM users
WHERE id > :cursor_id
ORDER BY id ASC
LIMIT 21;  -- 多抓一筆，用來判斷有沒有下一頁
```

```json
{
  "data": [...],
  "meta": {
    "has_next": true,
    "next_cursor": "eyJpZCI6MTQzfQ"
  }
}
```

**優點：** 不管位置在哪，效能都一致，有並行新增時也穩定
**缺點：** 不能跳到任意頁，cursor 是不透明的

### 該用哪一種

| 使用情境 | 分頁類型 |
|----------|----------------|
| 管理後台、小型資料集（<10K） | Offset |
| 無限捲動、動態消息、大型資料集 | Cursor |
| 公開 API | Cursor（預設），可選擇性加 offset |
| 搜尋結果 | Offset（使用者預期有頁碼） |

## 過濾、排序與搜尋

### 過濾

```
# 單純的相等
GET /api/v1/orders?status=active&customer_id=abc-123

# 比較運算子（用中括號寫法）
GET /api/v1/products?price[gte]=10&price[lte]=100
GET /api/v1/orders?created_at[after]=2025-01-01

# 多個值（用逗號分隔）
GET /api/v1/products?category=electronics,clothing

# 巢狀欄位（用點號寫法）
GET /api/v1/orders?customer.country=US
```

### 排序

```
# 單一欄位（前面加 - 表示降序）
GET /api/v1/products?sort=-created_at

# 多個欄位（用逗號分隔）
GET /api/v1/products?sort=-featured,price,-created_at
```

### 全文搜尋

```
# 搜尋用的 query 參數
GET /api/v1/products?q=wireless+headphones

# 指定欄位的搜尋
GET /api/v1/users?email=alice
```

### 稀疏欄位集

```
# 只回傳指定的欄位（減少 payload）
GET /api/v1/users?fields=id,name,email
GET /api/v1/orders?fields=id,total,status&include=customer.name
```

## 驗證與授權

### Token 式驗證

```
# Authorization header 裡的 Bearer token
GET /api/v1/users
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

# API key（給 server 對 server 用）
GET /api/v1/data
X-API-Key: sk_live_...
```

### 授權模式

```typescript
// 資源層級：檢查擁有權
app.get("/api/v1/orders/:id", async (req, res) => {
  const order = await Order.findById(req.params.id);
  if (!order) return res.status(404).json({ error: { code: "not_found" } });
  if (order.userId !== req.user.id) return res.status(403).json({ error: { code: "forbidden" } });
  return res.json({ data: order });
});

// 角色式：檢查權限
app.delete("/api/v1/users/:id", requireRole("admin"), async (req, res) => {
  await User.delete(req.params.id);
  return res.status(204).send();
});
```

## 速率限制

### Header

```
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000

# 超過限制時
HTTP/1.1 429 Too Many Requests
Retry-After: 60
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Try again in 60 seconds."
  }
}
```

### 速率限制等級

| 等級 | 限制 | 時間窗 | 使用情境 |
|------|-------|--------|----------|
| 匿名 | 30/分鐘 | 每個 IP | 公開 endpoint |
| 已驗證 | 100/分鐘 | 每個使用者 | 標準的 API 存取 |
| 付費 | 1000/分鐘 | 每個 API key | 付費的 API 方案 |
| 內部 | 10000/分鐘 | 每個服務 | 服務對服務 |

## 版本管理

### URL 路徑版本（建議）

```
/api/v1/users
/api/v2/users
```

**優點：** 明確、容易路由、可以快取
**缺點：** 不同版本的 URL 會變

### Header 版本

```
GET /api/users
Accept: application/vnd.myapp.v2+json
```

**優點：** URL 乾淨
**缺點：** 比較難測試，容易忘記

### 版本管理策略

```
1. 從 /api/v1/ 開始，需要之前不要急著分版本
2. 最多維持 2 個使用中的版本（目前的 + 前一個）
3. 棄用的時程：
   - 公告棄用（公開 API 要提前 6 個月通知）
   - 加上 Sunset header：Sunset: Sat, 01 Jan 2026 00:00:00 GMT
   - 過了日落日期後回傳 410 Gone
4. 不會破壞相容性的修改，不需要新版本：
   - 在回應裡新增欄位
   - 新增選用的 query 參數
   - 新增 endpoint
5. 會破壞相容性的修改，需要新版本：
   - 移除或重新命名欄位
   - 改變欄位型別
   - 改變 URL 結構
   - 改變驗證方式
```

## 實作模式

### TypeScript（Next.js API Route）

```typescript
import { z } from "zod";
import { NextRequest, NextResponse } from "next/server";

const createUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
});

export async function POST(req: NextRequest) {
  const body = await req.json();
  const parsed = createUserSchema.safeParse(body);

  if (!parsed.success) {
    return NextResponse.json({
      error: {
        code: "validation_error",
        message: "Request validation failed",
        details: parsed.error.issues.map(i => ({
          field: i.path.join("."),
          message: i.message,
          code: i.code,
        })),
      },
    }, { status: 422 });
  }

  const user = await createUser(parsed.data);

  return NextResponse.json(
    { data: user },
    {
      status: 201,
      headers: { Location: `/api/v1/users/${user.id}` },
    },
  );
}
```

### Python（Django REST Framework）

```python
from rest_framework import serializers, viewsets, status
from rest_framework.response import Response

class CreateUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField(max_length=100)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", "created_at"]

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return CreateUserSerializer
        return UserSerializer

    def create(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserService.create(**serializer.validated_data)
        return Response(
            {"data": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
            headers={"Location": f"/api/v1/users/{user.id}"},
        )
```

### Go（net/http）

```go
func (h *UserHandler) CreateUser(w http.ResponseWriter, r *http.Request) {
    var req CreateUserRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        writeError(w, http.StatusBadRequest, "invalid_json", "Invalid request body")
        return
    }

    if err := req.Validate(); err != nil {
        writeError(w, http.StatusUnprocessableEntity, "validation_error", err.Error())
        return
    }

    user, err := h.service.Create(r.Context(), req)
    if err != nil {
        switch {
        case errors.Is(err, domain.ErrEmailTaken):
            writeError(w, http.StatusConflict, "email_taken", "Email already registered")
        default:
            writeError(w, http.StatusInternalServerError, "internal_error", "Internal error")
        }
        return
    }

    w.Header().Set("Location", fmt.Sprintf("/api/v1/users/%s", user.ID))
    writeJSON(w, http.StatusCreated, map[string]any{"data": user})
}
```

## API 設計檢查表

出貨新的 endpoint 之前：

- [ ] 資源 URL 遵循命名慣例（複數、kebab-case、沒有動詞）
- [ ] 使用正確的 HTTP method（讀取用 GET、建立用 POST 等）
- [ ] 回傳適當的狀態碼（不是什麼都回 200）
- [ ] 輸入用 schema 驗證（Zod、Pydantic、Bean Validation）
- [ ] 錯誤回應遵循含 code 和 message 的標準格式
- [ ] 列表 endpoint 有實作分頁（cursor 或 offset）
- [ ] 需要驗證（或明確標示為公開）
- [ ] 有檢查授權（使用者只能存取自己的資源）
- [ ] 已設定速率限制
- [ ] 回應沒有洩漏內部細節（stack trace、SQL 錯誤）
- [ ] 跟既有的 endpoint 命名一致（camelCase 對 snake_case）
- [ ] 有文件（OpenAPI/Swagger 規格已更新）
