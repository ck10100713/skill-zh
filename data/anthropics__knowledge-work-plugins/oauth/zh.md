---
name: zoom-oauth
description: Zoom 驗證的參考 skill。在導向某個驗證工作流程之後，用來選擇 app 憑證、grant type、scope、token 更新行為，或除錯 Zoom OAuth 失敗時使用。
user-invocable: false
triggers:
  - zoom oauth
  - zoom authentication
  - zoom authorization
  - server to server oauth
  - s2s oauth
  - zoom access token
  - zoom refresh token
  - authorization code flow
  - device authorization
  - pkce
  - zoom api authentication
  - oauth error 4709
  - oauth error 4733
  - oauth error 4735
  - redirect uri mismatch
---

# Zoom OAuth

Zoom 驗證與 token 生命週期行為的背景參考。請先用 `setup-zoom-oauth`，再用這個 skill 查確切的流程、scope 和錯誤細節。

# Zoom OAuth

Zoom API 的驗證與授權。

## 📖 完整文件

完整指南、正式環境的做法和疑難排解，請見下方的 **Integrated Index 區段**。

快速導覽：
- **[5 分鐘 Runbook](RUNBOOK.md)** - 深入除錯之前的預先檢查
- **[OAuth 流程](concepts/oauth-flows.md)** - 該用哪個流程，以及各流程怎麼運作
- **[Token 生命週期](concepts/token-lifecycle.md)** - 過期、更新與撤銷
- **[正式環境範例](examples/s2s-oauth-redis.md)** - Redis 快取、MySQL 儲存、自動更新
- **[疑難排解](troubleshooting/common-errors.md)** - 錯誤碼 4700-4741

## 前置條件

- 在 [Marketplace](https://marketplace.zoom.us/) 建立好的 Zoom app
- Client ID 和 Client Secret
- S2S OAuth 需要：Account ID

## 四種授權使用情境

| 使用情境 | App 類型 | Grant Type | 業界名稱 |
|----------|----------|------------|---------------|
| **帳號授權（Account Authorization）** | Server-to-Server | `account_credentials` | Client Credentials Grant、M2M、Two-legged OAuth |
| **使用者授權（User Authorization）** | General | `authorization_code` | Authorization Code Grant、Three-legged OAuth |
| **裝置授權（Device Authorization）** | General | `urn:ietf:params:oauth:grant-type:device_code` | Device Authorization Grant (RFC 8628) |
| **Client 授權（Client Authorization）** | General | `client_credentials` | Client Credentials Grant（限 chatbot 範圍） |

### 業界術語

| 術語 | 意思 |
|------|---------|
| **Two-legged OAuth** | 沒有使用者參與（client ↔ server） |
| **Three-legged OAuth** | 有使用者參與（user ↔ client ↔ server） |
| **M2M** | Machine-to-Machine（後端服務） |
| **Public client** | 無法保管機密（行動 app、SPA）→ 使用 PKCE |
| **Confidential client** | 可以保管機密（後端伺服器） |
| **PKCE** | Proof Key for Code Exchange (RFC 7636)，念作「pixy」 |

### 我該用哪個流程？

```
                              ┌─────────────────────┐
                              │  What are you       │
                              │  building?          │
                              └──────────┬──────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
          ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
          │  Backend        │  │  App for other  │  │  Chatbot only   │
          │  automation     │  │  users/accounts │  │  (Team Chat)    │
          │  (your account) │  │                 │  │                 │
          └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
                   │                    │                    │
                   ▼                    │                    ▼
          ┌─────────────────┐           │           ┌─────────────────┐
          │    ACCOUNT      │           │           │     CLIENT      │
          │   (S2S OAuth)   │           │           │   (Chatbot)     │
          └─────────────────┘           │           └─────────────────┘
                                        │
                                        ▼
                              ┌─────────────────────┐
                              │  Does device have   │
                              │  a browser?         │
                              └──────────┬──────────┘
                                         │
                         ┌───────────────┴───────────────┐
                         │ NO                         YES│
                         ▼                               ▼
          ┌─────────────────────────┐         ┌─────────────────┐
          │        DEVICE           │         │      USER       │
          │     (Device Flow)       │         │  (Auth Code)    │
          │                         │         │                 │
          │ Examples:               │         │ + PKCE if       │
          │ • Smart TV              │         │   public client │
          │ • Meeting SDK device    │         │                 │
          └─────────────────────────┘         └─────────────────┘
```

---

## 帳號授權（Server-to-Server OAuth）

給不需要使用者互動的後端自動化。

### 請求 Access Token

```bash
POST https://zoom.us/oauth/token?grant_type=account_credentials&account_id={ACCOUNT_ID}

Headers:
Authorization: Basic {Base64(ClientID:ClientSecret)}
```

### 回應

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600,
  "scope": "user:read:user:admin",
  "api_url": "https://api.zoom.us"
}
```

### 更新

Access token 在 **1 小時**後過期。沒有獨立的更新流程，直接請求新的 token 就好。

---

## 使用者授權（Authorization Code Flow）

給代表使用者行動的 app。

### Step 1：把使用者導向授權頁

```
https://zoom.us/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}
```

同意畫面用 `https://zoom.us/oauth/authorize`，但 token 交換要用 `https://zoom.us/oauth/token`。

**選用參數：**

| 參數 | 說明 |
|-----------|-------------|
| `state` | CSRF 防護，在整個流程中維持狀態 |
| `code_challenge` | 給 PKCE 用（見下方） |
| `code_challenge_method` | `S256` 或 `plain`（預設：plain） |

### Step 2：使用者授權

- 使用者登入並授予權限
- 導回 `redirect_uri`，並帶上授權碼：
  ```
  https://example.com/?code={AUTHORIZATION_CODE}
  ```

### Step 3：用授權碼換 Token

```bash
POST https://zoom.us/oauth/token?grant_type=authorization_code&code={CODE}&redirect_uri={REDIRECT_URI}

Headers:
Authorization: Basic {Base64(ClientID:ClientSecret)}
```

**搭配 PKCE：** 加上 `code_verifier` 參數。

### 回應

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "refresh_token": "eyJ...",
  "expires_in": 3600,
  "scope": "user:read:user",
  "api_url": "https://api.zoom.us"
}
```

### 更新 Token

```bash
POST https://zoom.us/oauth/token?grant_type=refresh_token&refresh_token={REFRESH_TOKEN}

Headers:
Authorization: Basic {Base64(ClientID:ClientSecret)}
```

- Access token 在 **1 小時**後過期
- Refresh token 的壽命可能不同；部分以使用者為主的流程常見約 90 天。要把它當成可能改變的設定或行為，依靠執行期錯誤加上重新授權的退路。
- 下一次請求一定要用最新的 refresh token
- 如果 refresh token 過期，就把使用者導向授權網址，重新開始流程

### 使用者層級 vs 帳號層級的 App

| 類型 | 誰可以授權 | Scope 存取範圍 |
|------|-------------------|--------------|
| **使用者層級（User-level）** | 任何一般使用者 | 僅限他們自己 |
| **帳號層級（Account-level）** | 有管理員權限的使用者 | 整個帳號範圍的存取（admin scope） |

---

## 裝置授權（Device Flow）

給沒有瀏覽器的裝置（例如 Meeting SDK app）。

### 前置條件

在 Features > Embed > Enable Meeting SDK 裡啟用「Use App on Device」

### Step 1：請求 Device Code

```bash
POST https://zoom.us/oauth/devicecode?client_id={CLIENT_ID}

Headers:
Authorization: Basic {Base64(ClientID:ClientSecret)}
```

### 回應

```json
{
  "device_code": "DEVICE_CODE",
  "user_code": "abcd1234",
  "verification_uri": "https://zoom.us/oauth_device",
  "verification_uri_complete": "https://zoom.us/oauth/device/complete/{CODE}",
  "expires_in": 900,
  "interval": 5
}
```

### Step 2：使用者授權

把使用者導向：
- `verification_uri`，並顯示 `user_code` 讓他們手動輸入，或
- `verification_uri_complete`（user code 已預先填好）

使用者登入並允許該 app。

### Step 3：輪詢 Token

依照 `interval`（5 秒）輪詢，直到使用者授權：

```bash
POST https://zoom.us/oauth/token?grant_type=urn:ietf:params:oauth:grant-type:device_code&device_code={DEVICE_CODE}

Headers:
Authorization: Basic {Base64(ClientID:ClientSecret)}
```

### 回應

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "refresh_token": "eyJ...",
  "expires_in": 3599,
  "scope": "user:read:user user:read:token",
  "api_url": "https://api.zoom.us"
}
```

### 輪詢的回應

| 回應 | 意思 | 動作 |
|----------|---------|--------|
| 回傳 Token | 使用者已授權 | 儲存 token，完成 |
| `error: authorization_pending` | 使用者還沒授權 | 依 interval 繼續輪詢 |
| `error: slow_down` | 輪詢太快 | 把 interval 增加 5 秒 |
| `error: expired_token` | Device code 已過期（15 分鐘） | 從 Step 1 重新開始流程 |
| `error: access_denied` | 使用者拒絕授權 | 處理拒絕的情況，不要重試 |

### 輪詢的實作

```javascript
async function pollForToken(deviceCode, interval) {
  while (true) {
    await sleep(interval * 1000);
    
    try {
      const response = await axios.post(
        `https://zoom.us/oauth/token?grant_type=urn:ietf:params:oauth:grant-type:device_code&device_code=${deviceCode}`,
        null,
        { headers: { 'Authorization': `Basic ${credentials}` } }
      );
      return response.data; // Success - got tokens
    } catch (error) {
      const err = error.response?.data?.error;
      if (err === 'authorization_pending') continue;
      if (err === 'slow_down') { interval += 5; continue; }
      throw error; // expired_token or access_denied
    }
  }
}
```

### 更新

跟使用者授權一樣。如果 refresh token 過期，就從 Step 1 重新開始 device flow。

---

## Client 授權（Chatbot）

只給 chatbot 訊息操作用。

### 請求 Token

```bash
POST https://zoom.us/oauth/token?grant_type=client_credentials

Headers:
Authorization: Basic {Base64(ClientID:ClientSecret)}
```

### 回應

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600,
  "scope": "imchat:bot",
  "api_url": "https://api.zoom.us"
}
```

### 更新

Token 在 **1 小時**後過期。沒有更新流程，直接請求新的 token 就好。

---

## 使用 Access Token

### 呼叫 API

```bash
GET https://api.zoom.us/v2/users/me

Headers:
Authorization: Bearer {ACCESS_TOKEN}
```

### Me Context

把 `userID` 換成 `me`，就會指向該 token 對應的使用者：

| Endpoint | Methods |
|----------|---------|
| `/v2/users/me` | GET, PATCH |
| `/v2/users/me/token` | GET |
| `/v2/users/me/meetings` | GET, POST |

---

## 撤銷 Access Token

適用於所有授權類型。

```bash
POST https://zoom.us/oauth/revoke?token={ACCESS_TOKEN}

Headers:
Authorization: Basic {Base64(ClientID:ClientSecret)}
```

### 回應

```json
{
  "status": "success"
}
```

---

## PKCE（Proof Key for Code Exchange）

給無法安全儲存機密的 public client（行動 app、SPA、桌面 app）。

### 什麼時候該用 PKCE

| Client 類型 | 要用 PKCE 嗎？ | 為什麼 |
|-------------|-----------|-----|
| 行動 app | **要** | 無法安全儲存 client secret |
| Single Page App (SPA) | **要** | JavaScript 使用者看得到 |
| 桌面 app | **要** | 執行檔可以被反編譯 |
| Meeting SDK（client 端） | **要** | 在使用者的裝置上執行 |
| 後端伺服器 | 選用 | 可以保管機密，但 PKCE 能增加安全性 |

### PKCE 怎麼運作

```
┌──────────┐                              ┌──────────┐                    ┌──────────┐
│  Client  │                              │   Zoom   │                    │   Zoom   │
│   App    │                              │  Auth    │                    │  Token   │
└────┬─────┘                              └────┬─────┘                    └────┬─────┘
     │                                         │                              │
     │ 1. Generate code_verifier (random)      │                              │
     │ 2. Create code_challenge = SHA256(verifier)                            │
     │                                         │                              │
     │ ─────── /authorize + code_challenge ──► │                              │
     │                                         │                              │
     │ ◄────── authorization_code ──────────── │                              │
     │                                         │                              │
     │ ─────────────── /token + code_verifier ─┼────────────────────────────► │
     │                                         │                              │
     │                                         │     Verify: SHA256(verifier) │
     │                                         │            == challenge      │
     │                                         │                              │
     │ ◄───────────────────────────────────────┼─────── access_token ──────── │
     │                                         │                              │
```

### 實作（Node.js）

```javascript
const crypto = require('crypto');

function generatePKCE() {
  const verifier = crypto.randomBytes(32).toString('base64url');
  const challenge = crypto.createHash('sha256').update(verifier).digest('base64url');
  return { verifier, challenge };
}

const pkce = generatePKCE();

const authUrl = `https://zoom.us/oauth/authorize?` +
  `response_type=code&` +
  `client_id=${CLIENT_ID}&` +
  `redirect_uri=${REDIRECT_URI}&` +
  `code_challenge=${pkce.challenge}&` +
  `code_challenge_method=S256`;

// Store pkce.verifier in session for callback
```

### 搭配 PKCE 的 Token 交換

```bash
POST https://zoom.us/oauth/token?grant_type=authorization_code&code={CODE}&redirect_uri={REDIRECT_URI}&code_verifier={VERIFIER}

Headers:
Authorization: Basic {Base64(ClientID:ClientSecret)}
```

---

## 取消授權（Deauthorization）

當使用者移除你的 app 時，Zoom 會發一個 webhook 到你的 Deauthorization Notification Endpoint URL。

### Webhook 事件

```json
{
  "event": "app_deauthorized",
  "event_ts": 1740439732278,
  "payload": {
    "account_id": "ACCOUNT_ID",
    "user_id": "USER_ID",
    "signature": "SIGNATURE",
    "deauthorization_time": "2019-06-17T13:52:28.632Z",
    "client_id": "CLIENT_ID"
  }
}
```

### 要求

- 收到這個事件之後，**要刪除所有相關的使用者資料**
- **要驗證 webhook 簽章**（使用 secret token，verification token 已在 2023 年 10 月棄用）
- 只有公開 app 會收到取消授權的 webhook（私有／開發中的 app 不會）

---

## 預先核准流程（Pre-Approval Flow）

有些 Zoom 帳號要求 Marketplace 管理員預先核准，使用者才能授權 app。

- 使用者可以向他們的管理員請求預先核准
- 帳號層級的 app（admin scope）需要適當的角色權限

---

## Active Apps Notifier（AAN）

會議中的功能，顯示哪些 app 正在即時存取內容。

- 顯示圖示加 tooltip，內含 app 資訊、被存取的內容類型、核准的帳號
- 支援：Zoom client 5.6.7+、Meeting SDK 5.9.0+

---

## OAuth Scope

### Scope 類型

| 類型 | 說明 | 適用對象 |
|------|-------------|-----|
| **Classic scope** | 舊版 scope（user、admin、master 層級） | 既有的 app |
| **Granular scope** | 新的細粒度 scope，支援選用 | 新的 app |

### Classic Scope

給先前建立的 app。三個層級：
- **User-level**：存取個別使用者的資料
- **Admin-level**：整個帳號範圍的存取，需要 admin 角色
- **Master-level**：給主帳號／子帳號架構，需要帳號擁有者

完整清單：https://developers.zoom.us/docs/integrations/oauth-scopes/

### Granular Scope

給新的 app。格式：`<service>:<action>:<data_claim>:<access>`

| 組成 | 值 |
|-----------|--------|
| **service** | `meeting`、`webinar`、`user`、`recording` 等 |
| **action** | `read`、`write`、`update`、`delete` |
| **data_claim** | 資料類別（例如 `participants`、`settings`） |
| **access** | 空白（user）、`admin`、`master` |

範例：`meeting:read:list_meetings:admin`

完整清單：https://developers.zoom.us/docs/integrations/oauth-scopes-granular/

### 選用 Scope

Granular scope 可以標記為**選用**，由使用者決定要不要授予。

**基本授權**（使用 build flow 的預設值）：
```
https://zoom.us/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}
```

**進階授權**（每次請求自訂 scope）：
```
https://zoom.us/oauth/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={required_scopes}&optional_scope={optional_scopes}
```

**包含先前已授予的 scope：**
```
https://zoom.us/oauth/authorize?...&include_granted_scopes&scope={additional_scopes}
```

### 從 Classic 遷移到 Granular

1. Manage > 選取 app > edit
2. Scope 頁面 > Development 分頁 > 點 **Migrate**
3. 檢查自動分配的 granular scope，移除不必要的，標記選用的
4. 測試
5. Production 分頁 > 點 **Migrate**

**備註：**
- 如果只是遷移或縮減 scope，不需要審核
- 既有使用者的 token 在重新授權之前，仍會沿用 classic scope 的值
- 遷移之後的新使用者會拿到 granular scope

---

## 常見錯誤碼

| 代碼 | 訊息 | 解法 |
|------|---------|----------|
| 4700 | Token cannot be empty | 檢查 Authorization header 是否帶有效的 token |
| 4702/4704 | Invalid client | 確認 Client ID 和 Client Secret |
| 4705 | Grant type not supported | 請用：`account_credentials`、`authorization_code`、`urn:ietf:params:oauth:grant-type:device_code` 或 `client_credentials` |
| 4706 | Client ID or secret missing | 把憑證加到 header 或請求參數 |
| 4709 | Redirect URI mismatch | 確保 redirect_uri 跟 app 設定完全一致（包含結尾的斜線） |
| 4711 | Refresh token invalid | Token 的 scope 跟 client 的 scope 不符 |
| 4717 | App has been disabled | 聯絡 Zoom 支援 |
| 4733 | Code is expired | 授權碼 5 分鐘後過期，要重新開始流程 |
| 4734 | Invalid authorization code | 重新產生授權碼 |
| 4735 | Owner of token does not exist | 使用者已從帳號移除，要重新授權 |
| 4741 | Token has been revoked | 使用最近一次授權的最新 token |

完整錯誤清單請見 `references/oauth-errors.md`。

---

## 快速參考

| 流程 | Grant Type | Token 有效期 | 更新方式 |
|------|------------|--------------|---------|
| Account (S2S) | `account_credentials` | 1 小時 | 請求新的 token |
| User | `authorization_code` | 1 小時 | 用 refresh_token（90 天有效） |
| Device | `urn:ietf:params:oauth:grant-type:device_code` | 1 小時 | 用 refresh_token（90 天有效） |
| Client (Chatbot) | `client_credentials` | 1 小時 | 請求新的 token |

---

## Demo 指引

如果你要做 OAuth demo app，請把它執行時的 base URL 寫在那個 demo 專案自己的
README 或 `.env.example`，不要寫在這個共用的 skill 裡。

## 資源

- **OAuth 文件**：https://developers.zoom.us/docs/integrations/oauth/
- **S2S OAuth 文件**：https://developers.zoom.us/docs/internal-apps/s2s-oauth/
- **PKCE 部落格**：https://developers.zoom.us/blog/pcke-oauth-with-postman-rest-api/
- **Classic scope**：https://developers.zoom.us/docs/integrations/oauth-scopes/
- **Granular scope**：https://developers.zoom.us/docs/integrations/oauth-scopes-granular/

---

## Integrated Index

_這個區段是從 `SKILL.md` 遷移過來的。_

## 快速上手路徑

**如果你剛接觸 Zoom OAuth，請照這個順序：**

1. **先跑預先檢查** → [RUNBOOK.md](RUNBOOK.md)

2. **選擇你的 OAuth 流程** → [concepts/oauth-flows.md](concepts/oauth-flows.md)
   - 4 種流程：S2S（後端）、User（SaaS）、Device（沒有瀏覽器）、Chatbot
   - 決策矩陣：哪個流程適合你的使用情境？

3. **了解 token 生命週期** → [concepts/token-lifecycle.md](concepts/token-lifecycle.md)
   - **關鍵**：token 怎麼過期、更新和撤銷
   - 常見陷阱：refresh token 輪替

4. **實作你的流程** → 跳到範例：
   - 後端自動化 → [examples/s2s-oauth-redis.md](examples/s2s-oauth-redis.md)
   - SaaS app → [examples/user-oauth-mysql.md](examples/user-oauth-mysql.md)
   - 行動／SPA → [examples/pkce-implementation.md](examples/pkce-implementation.md)
   - Device（電視／kiosk）→ [examples/device-flow.md](examples/device-flow.md)

5. **修 redirect URI 問題** → [troubleshooting/redirect-uri-issues.md](troubleshooting/redirect-uri-issues.md)
   - 最常見的 OAuth 錯誤：Redirect URI mismatch

6. **實作 token 更新** → [examples/token-refresh.md](examples/token-refresh.md)
   - 自動 middleware 模式
   - 處理 refresh token 輪替

7. **排查錯誤** → [troubleshooting/common-errors.md](troubleshooting/common-errors.md)
   - 錯誤碼表（4700-4741 範圍）
   - 快速診斷流程

---

## 文件結構

```
oauth/
├── SKILL.md                           # Main skill overview
├── SKILL.md                           # This file - navigation guide
│
├── concepts/                          # Core OAuth concepts
│   ├── oauth-flows.md                # 4 flows: S2S, User, Device, Chatbot
│   ├── token-lifecycle.md            # Expiration, refresh, revocation
│   ├── pkce.md                       # PKCE security for public clients
│   ├── scopes-architecture.md        # Classic vs Granular scopes
│   └── state-parameter.md            # CSRF protection with state
│
├── examples/                          # Complete working code
│   ├── s2s-oauth-basic.md            # S2S OAuth minimal example
│   ├── s2s-oauth-redis.md            # S2S OAuth with Redis caching (production)
│   ├── user-oauth-basic.md           # User OAuth minimal example
│   ├── user-oauth-mysql.md           # User OAuth with MySQL + encryption (production)
│   ├── device-flow.md                # Device authorization flow
│   ├── pkce-implementation.md        # PKCE for SPAs/mobile apps
│   └── token-refresh.md              # Auto-refresh middleware pattern
│
├── troubleshooting/                   # Problem solving guides
│   ├── common-errors.md              # Error codes 4700-4741
│   ├── redirect-uri-issues.md        # Most common OAuth error
│   ├── token-issues.md               # Expired, revoked, invalid tokens
│   └── scope-issues.md               # Scope mismatch errors
│
└── references/                        # Reference documentation
    ├── oauth-errors.md                # Complete error code reference
    ├── classic-scopes.md              # Classic scope reference
    └── granular-scopes.md             # Granular scope reference
```

---

## 依使用情境

### 我想在自己的帳號上自動化 Zoom 工作
1. [OAuth 流程](concepts/oauth-flows.md#server-to-server-s2s-oauth) - S2S OAuth 說明
2. [S2S OAuth Redis](examples/s2s-oauth-redis.md) - 搭配 Redis 快取的正式環境做法
3. [Token 生命週期](concepts/token-lifecycle.md) - 1 小時的 token，不用更新

### 我想為其他 Zoom 使用者做一個 SaaS app
1. [OAuth 流程](concepts/oauth-flows.md#user-authorization-oauth) - User OAuth 說明
2. [User OAuth MySQL](examples/user-oauth-mysql.md) - 搭配加密的正式環境做法
3. [Token 更新](examples/token-refresh.md) - 自動更新 middleware
4. [Redirect URI 問題](troubleshooting/redirect-uri-issues.md) - 修最常見的錯誤

### 我想做行動 app 或 SPA
1. [PKCE](concepts/pkce.md) - 為什麼 public client 一定要用 PKCE
2. [PKCE 實作](examples/pkce-implementation.md) - 完整程式碼範例
3. [State 參數](concepts/state-parameter.md) - CSRF 防護

### 我想做給沒有瀏覽器的裝置用的 app（電視、kiosk）
1. [OAuth 流程](concepts/oauth-flows.md#device-authorization-flow) - Device flow 說明
2. [Device Flow 範例](examples/device-flow.md) - 完整的輪詢實作
3. [常見錯誤](troubleshooting/common-errors.md) - 裝置專屬的錯誤

### 我在做 Team Chat bot
1. [OAuth 流程](concepts/oauth-flows.md#client-authorization-chatbot) - Chatbot 流程說明
2. [S2S OAuth Basic](examples/s2s-oauth-basic.md) - 類似的模式，不同的 grant type
3. [Scope 架構](concepts/scopes-architecture.md) - Chatbot 專屬的 scope

### 我遇到 redirect URI 錯誤（4709）
1. [Redirect URI 問題](troubleshooting/redirect-uri-issues.md) - **從這裡開始！**
2. [常見錯誤](troubleshooting/common-errors.md#4709-redirect-uri-mismatch) - 錯誤細節
3. [User OAuth Basic](examples/user-oauth-basic.md) - 看正確的做法

### 我遇到 token 錯誤（4700-4741）
1. [Token 問題](troubleshooting/token-issues.md) - 診斷流程
2. [Token 生命週期](concepts/token-lifecycle.md) - 了解過期機制
3. [Token 更新](examples/token-refresh.md) - 實作自動更新
4. [常見錯誤](troubleshooting/common-errors.md) - 錯誤碼表

### 我遇到 scope 錯誤（4711）
1. [Scope 問題](troubleshooting/scope-issues.md) - 不符的原因
2. [Scope 架構](concepts/scopes-architecture.md) - Classic vs Granular
3. [Classic Scope](references/classic-scopes.md) - 完整的 scope 參考
4. [Granular Scope](references/granular-scopes.md) - Granular scope 參考

### 我需要更新 token
1. [Token 生命週期](concepts/token-lifecycle.md#refresh-strategy) - 什麼時候更新
2. [Token 更新](examples/token-refresh.md) - Middleware 模式
3. [Token 問題](troubleshooting/token-issues.md#refresh-token-problems) - 常見的錯誤

### 我想了解 Classic 和 Granular scope 的差別
1. [Scope 架構](concepts/scopes-architecture.md) - **完整比較**
2. [Classic Scope](references/classic-scopes.md) - `resource:level` 格式
3. [Granular Scope](references/granular-scopes.md) - `service:action:data_claim:access` 格式

### 我需要保護我的 OAuth 實作
1. [PKCE](concepts/pkce.md) - Public client 的安全性
2. [State 參數](concepts/state-parameter.md) - CSRF 防護
3. [User OAuth MySQL](examples/user-oauth-mysql.md#token-encryption) - Token 靜態加密

### 我想從 JWT app 遷移到 S2S OAuth
1. [S2S OAuth Redis](examples/s2s-oauth-redis.md) - 現代的替代方案
2. [Token 生命週期](concepts/token-lifecycle.md) - 不同的 token 行為

> **備註**：JWT App Type 已在 2023 年 6 月棄用。Server-to-server 自動化請遷移到 S2S OAuth。

---

## 最關鍵的文件

### 1. OAuth 流程（決策文件）
**[concepts/oauth-flows.md](concepts/oauth-flows.md)**

了解該用 4 種流程中的哪一種：
- **S2S OAuth**：後端自動化（你的帳號）
- **User OAuth**：SaaS app（使用者授權給你）
- **Device Flow**：沒有瀏覽器的裝置
- **Chatbot**：只限 Team Chat bot

### 2. Token 生命週期（最常見的問題）
**[concepts/token-lifecycle.md](concepts/token-lifecycle.md)**

99% 的 OAuth 問題都來自誤解：
- Token 過期（所有流程都是 1 小時）
- Refresh token 輪替（一定要儲存新的 refresh token）
- 撤銷行為（會讓所有 token 失效）

### 3. Redirect URI 問題（最常見的錯誤）
**[troubleshooting/redirect-uri-issues.md](troubleshooting/redirect-uri-issues.md)**

錯誤 4709（「Redirect URI mismatch」）是排名第一的 OAuth 錯誤。
必須完全一致（包含結尾斜線、http 或 https）。

---

## 重要心得

### 關鍵發現：

1. **Refresh Token 輪替**
   - 每次更新都會回傳一個**新的** refresh token
   - 舊的 refresh token 會失效
   - 沒儲存新的 token 會造成 4735 錯誤
   - 參見：[Token 更新](examples/token-refresh.md)

2. **S2S OAuth 用 Redis，User OAuth 用資料庫**
   - S2S：整個帳號共用一個 token → Redis（暫存性質）
   - User：每位使用者各一個 token → 資料庫（持久性質）
   - 參見：[S2S OAuth Redis](examples/s2s-oauth-redis.md) vs [User OAuth MySQL](examples/user-oauth-mysql.md)

3. **Redirect URI 必須完全一致**
   - 結尾斜線有差：`/callback` ≠ `/callback/`
   - 協定有差：`http://` ≠ `https://`
   - Port 有差：`:3000` ≠ `:3001`
   - 參見：[Redirect URI 問題](troubleshooting/redirect-uri-issues.md)

4. **Public Client 一定要用 PKCE**
   - 行動 app 無法保管機密
   - SPA 無法保管機密
   - PKCE 能防止授權碼被攔截
   - 參見：[PKCE](concepts/pkce.md)

5. **State 參數能防止 CSRF**
   - redirect 之前先產生隨機 state
   - 存進 session
   - callback 時驗證
   - 參見：[State 參數](concepts/state-parameter.md)

6. **Token 儲存一定要加密**
   - 絕對不要用明文儲存 token
   - 至少使用 AES-256
   - 參見：[User OAuth MySQL](examples/user-oauth-mysql.md#token-encryption)

7. **JWT App Type 已棄用（2023 年 6 月）**
   - 不能再建立新的 JWT app
   - 既有的 app 仍可運作，但最終會被淘汰
   - 請遷移到 S2S OAuth 或 User OAuth

8. **Scope 層級決定授權要求**
   - 沒有後綴（user-level）：任何使用者都可以授權
   - `:admin`：需要 admin 角色
   - `:master`：需要帳號擁有者（多帳號）
   - 參見：[Scope 架構](concepts/scopes-architecture.md)

9. **授權碼 5 分鐘後過期**
   - 立刻用授權碼換 token
   - 不要快取授權碼
   - 參見：[Token 生命週期](concepts/token-lifecycle.md#authorization-code-expiration)

10. **Device Flow 需要輪詢**
    - 依照 `/devicecode` 回傳的 interval 輪詢（通常是 5 秒）
    - 處理 `authorization_pending`、`slow_down`、`expired_token`
    - 參見：[Device Flow](examples/device-flow.md)

---

## 快速參考

### 「我該用哪個 OAuth 流程？」
→ [OAuth 流程](concepts/oauth-flows.md)

### 「Redirect URI mismatch 錯誤（4709）」
→ [Redirect URI 問題](troubleshooting/redirect-uri-issues.md)

### 「Token 過期或無效」
→ [Token 問題](troubleshooting/token-issues.md)

### 「Refresh token 無效（4735）」
→ [Token 更新](examples/token-refresh.md) - 一定要儲存新的 refresh token

### 「Scope 不符錯誤（4711）」
→ [Scope 問題](troubleshooting/scope-issues.md)

### 「我要怎麼保護我的 OAuth app？」
→ [PKCE](concepts/pkce.md) + [State 參數](concepts/state-parameter.md)

### 「我要怎麼實作自動更新？」
→ [Token 更新](examples/token-refresh.md)

### 「Classic 和 Granular scope 有什麼差別？」
→ [Scope 架構](concepts/scopes-architecture.md)

### 「哪個錯誤碼代表什麼？」
→ [常見錯誤](troubleshooting/common-errors.md)

---

## 文件版本

依據 **Zoom OAuth API v2**（2024 年起）

**已棄用：** JWT App Type（2023 年 6 月）

---

**寫得開心！**

記得：先從 [OAuth 流程](concepts/oauth-flows.md) 開始，了解哪個流程適合你的使用情境！

## 環境變數

- 標準化的 `.env` key 以及每個值該去哪裡找，請見 [references/environment-variables.md](references/environment-variables.md)。
