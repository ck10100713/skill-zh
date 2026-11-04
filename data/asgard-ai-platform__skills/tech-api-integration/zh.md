---
name: "tech-api-integration"
description: "指引 REST API 串接，包括 HTTP 方法、認證、錯誤處理和速率限制。當使用者需要連接第三方 API、設計 API client、排查 API 錯誤或理解 API 概念時使用這個 skill，就算他們說的是「幫我接這個 API」、「為什麼 API 一直回錯誤」、「怎麼做認證」或「做一個 API 整合」也一樣。"
metadata:
  category: "WP-11 通用技術"
  tags: ["technology", "api", "rest", "integration"]
---

# REST API 串接指南

## 框架

```
IRON LAW: Read the Docs, Then Build, Then Handle Errors
（鐵律：先讀文件，再開發，再處理錯誤）

1. 把 API 文件完整讀完（認證、endpoint、速率限制、錯誤）
2. 先在隔離環境讓一個請求成功跑通（curl/Postman）
3. 在做功能「之前」先把錯誤處理做好

跳過第 1 步，會在試誤中白白浪費好幾個小時。跳過第 3 步，
會做出脆弱的整合，在 production 裡悄悄壞掉。
```

### HTTP 方法

| 方法 | 用途 | 冪等？ | 範例 |
|--------|---------|------------|---------|
| GET | 讀取資料 | 是 | `GET /users/123` |
| POST | 建立新資源 | 否 | `POST /users` + body |
| PUT | 取代整個資源 | 是 | `PUT /users/123` + 完整 body |
| PATCH | 更新部分資源 | 是 | `PATCH /users/123` + 部分 body |
| DELETE | 移除資源 | 是 | `DELETE /users/123` |

### 狀態碼

| 範圍 | 意義 | 常見狀態碼 |
|-------|---------|-------------|
| 2xx | 成功 | 200 OK, 201 Created, 204 No Content |
| 3xx | 重新導向 | 301 Moved, 304 Not Modified |
| 4xx | 用戶端錯誤（你這邊的問題） | 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 429 Too Many Requests |
| 5xx | 伺服器錯誤（對方的問題） | 500 Internal, 502 Bad Gateway, 503 Service Unavailable |

### 認證類型

| 類型 | 運作方式 | 使用時機 |
|------|-------------|----------|
| **API Key** | Key 放在 header 或 query 參數 | 簡單的 API、server 對 server |
| **Bearer Token** | `Authorization: Bearer <token>` | OAuth 2.0、JWT 型的 API |
| **OAuth 2.0** | Token 交換流程（authorize → token → API call） | 使用者授權存取（Google、FB） |
| **Basic Auth** | header 裡放 Base64(username:password) | 老舊系統、內部 API |
| **HMAC Signature** | 用密鑰對請求簽章 | 金流閘道、高安全需求 |

### 錯誤處理策略

```
try:
    response = api.call(request)
    if response.status == 429:  # Rate limited
        wait(response.headers['Retry-After'])
        retry()
    elif response.status >= 500:  # Server error
        retry_with_backoff(max_retries=3)
    elif response.status >= 400:  # Client error
        log_error(response.body)
        raise ClientError(response.body['message'])
    else:
        return response.json()
```

### 速率限制

| 策略 | 做法 |
|----------|-----|
| 遵守 `Retry-After` header | 等指定的秒數再重試 |
| 指數退避（Exponential backoff） | 重試之間依序等 1 秒、2 秒、4 秒、8 秒 |
| Token bucket | 追蹤請求次數，接近上限時暫停 |
| 請求排隊 | 大量串接時用 job queue（Celery、Bull） |

### 串接檢查清單

1. [ ] 把 API 文件完整讀完
2. [ ] 測試認證流程（拿到有效的 token/key）
3. [ ] 每個 endpoint 先用 curl/Postman 測過
4. [ ] 每個狀態碼範圍都實作錯誤處理
5. [ ] 實作速率限制處理
6. [ ] 實作帶退避的重試邏輯
7. [ ] 記錄所有請求與回應（機密要遮蔽）
8. [ ] 處理 API 版本（鎖定特定版本）
9. [ ] 設定 timeout（連線：5 秒、讀取：30 秒）
10. [ ] 留意 API 棄用公告

## 輸出格式

```markdown
# API Integration Plan: {API Name}

## API Overview
- Base URL: {url}
- Auth: {type}
- Rate limit: {N requests/period}
- Documentation: {link}

## Endpoints Used
| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| {path} | GET/POST | {what it does} | {auth type} |

## Error Handling
| Error | Response | Our Action |
|-------|----------|-----------|
| 401 | Unauthorized | Refresh token, retry |
| 429 | Rate limited | Backoff, retry after Retry-After |
| 500 | Server error | Retry 3x with exponential backoff |

## Implementation Timeline
| Phase | Task | Duration |
|-------|------|----------|
| 1 | Auth + basic call | {days} |
| 2 | Full integration | {days} |
| 3 | Error handling + monitoring | {days} |
```

## 常見陷阱

- **Sandbox 與 production**：多數 API 都有 sandbox/測試環境，先在那邊開發和測試。Production 的 API key 絕對不能放進程式碼。
- **分頁**：API 會回傳分頁結果，要處理所有頁面，不是只拿第一頁。檢查有沒有 `next_page` token 或 `offset` 參數。
- **Webhook 可靠性**：用 webhook 的話，handler 要做成冪等（同一個事件收到兩次，不能造成資料重複）。存下事件 ID 來去重。
- **API 變動會弄壞東西**：鎖定特定 API 版本，並訂閱供應商的 changelog/棄用公告。
- **機密管理**：API key 和 token 絕對不放在原始碼裡。用環境變數或機密管理服務（AWS Secrets Manager、HashiCorp Vault）。

## 參考資料

- OAuth 2.0 流程細節，見 `references/oauth-guide.md`
- Webhook 實作模式，見 `references/webhook-patterns.md`
