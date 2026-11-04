---
name: auth-implementation-patterns
description: 掌握認證與授權的模式，包括 JWT、OAuth2、session 管理和 RBAC，建構安全、可擴充的存取控制系統。在實作認證系統、保護 API，或除錯資安問題時使用。
---

# 認證與授權實作模式

用業界標準的模式和現代最佳實務，建構安全、可擴充的認證與授權系統。

## 何時使用這個 Skill

- 實作使用者認證系統
- 保護 REST 或 GraphQL API
- 加入 OAuth2/社群登入
- 實作角色型存取控制（RBAC）
- 設計 session 管理
- 遷移認證系統
- 除錯認證問題
- 實作 SSO 或多租戶

## 核心概念

### 1. Authentication 與 Authorization

**Authentication（AuthN）**：你是誰？

- 驗證身分（帳號/密碼、OAuth、生物辨識）
- 發放憑證（session、token）
- 管理登入/登出

**Authorization（AuthZ）**：你能做什麼？

- 檢查權限
- 角色型存取控制（RBAC）
- 驗證資源擁有權
- 執行政策

### 2. 認證策略

**Session-Based：**

- 伺服器儲存 session 狀態
- Session ID 放在 cookie 裡
- 傳統、簡單、有狀態

**Token-Based（JWT）：**

- 無狀態、自成一體
- 可水平擴充
- 可以存放 claim

**OAuth2/OpenID Connect：**

- 委派認證
- 社群登入（Google、GitHub）
- 企業 SSO

## 詳細模式與實作範例

詳細的模式文件放在 `references/details.md`。上面的導覽層不夠用時，再讀那個檔案。

## 最佳實務

1. **絕對不要存明文密碼**：一律用 bcrypt/argon2 做雜湊
2. **使用 HTTPS**：加密傳輸中的資料
3. **短效的 access token**：最長 15 到 30 分鐘
4. **安全的 cookie**：設定 httpOnly、secure、sameSite 旗標
5. **驗證所有輸入**：Email 格式、密碼強度
6. **替認證端點做 rate limit**：防止暴力破解攻擊
7. **實作 CSRF 防護**：針對 session-based 的認證
8. **定期輪替密鑰**：JWT 密鑰、session 密鑰
9. **記錄資安事件**：登入嘗試、認證失敗
10. **盡可能使用 MFA**：多一層安全防護

## 常見陷阱

- **弱密碼**：強制執行強密碼政策
- **JWT 放在 localStorage**：容易受 XSS 攻擊，改用 httpOnly cookie
- **Token 沒有過期**：token 應該要過期
- **只在 client 端檢查認證**：一定要在伺服器端驗證
- **不安全的密碼重設**：使用有過期時間的安全 token
- **沒有 rate limit**：容易被暴力破解
- **信任 client 的資料**：一定要在伺服器端驗證
