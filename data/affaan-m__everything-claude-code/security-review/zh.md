---
name: security-review
description: 新增驗證機制、處理使用者輸入、處理 secret、建立 API endpoint，或實作付款/敏感功能時使用這個 skill。提供完整的安全檢查清單和模式。
metadata:
  origin: ECC
---

# 安全 Review Skill

這個 skill 確保所有程式碼都遵循安全最佳實務，並找出潛在的漏洞。

## 何時啟用

- 實作驗證（authentication）或授權（authorization）
- 處理使用者輸入或檔案上傳
- 建立新的 API endpoint
- 處理 secret 或憑證
- 實作付款功能
- 儲存或傳輸敏感資料
- 整合第三方 API

## 安全檢查清單

### 1. Secret 管理

#### FAIL：絕對不要這樣做
```typescript
const apiKey = "sk-proj-xxxxx"  // Hardcoded secret
const dbPassword = "password123" // In source code
```

#### PASS：一律這樣做
```typescript
const apiKey = process.env.OPENAI_API_KEY
const dbUrl = process.env.DATABASE_URL

// Verify secrets exist
if (!apiKey) {
  throw new Error('OPENAI_API_KEY not configured')
}
```

#### 驗證步驟
- [ ] 沒有寫死的 API key、token 或密碼
- [ ] 所有 secret 都放在環境變數
- [ ] `.env.local` 在 .gitignore 裡
- [ ] git 歷史裡沒有 secret
- [ ] 正式環境的 secret 放在託管平台（Vercel、Railway）

### 2. 輸入驗證

#### 一律驗證使用者輸入
```typescript
import { z } from 'zod'

// Define validation schema
const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  age: z.number().int().min(0).max(150)
})

// Validate before processing
export async function createUser(input: unknown) {
  try {
    const validated = CreateUserSchema.parse(input)
    return await db.users.create(validated)
  } catch (error) {
    if (error instanceof z.ZodError) {
      return { success: false, errors: error.issues }
    }
    throw error
  }
}
```

#### 檔案上傳驗證
```typescript
function validateFileUpload(file: File) {
  // Size check (5MB max)
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    throw new Error('File too large (max 5MB)')
  }

  // Type check
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif']
  if (!allowedTypes.includes(file.type)) {
    throw new Error('Invalid file type')
  }

  // Extension check
  const allowedExtensions = ['.jpg', '.jpeg', '.png', '.gif']
  const extension = file.name.toLowerCase().match(/\.[^.]+$/)?.[0]
  if (!extension || !allowedExtensions.includes(extension)) {
    throw new Error('Invalid file extension')
  }

  return true
}
```

#### 驗證步驟
- [ ] 所有使用者輸入都用 schema 驗證
- [ ] 檔案上傳有限制（大小、類型、副檔名）
- [ ] 沒有把使用者輸入直接用在查詢裡
- [ ] 用白名單驗證（不是黑名單）
- [ ] 錯誤訊息不會洩漏敏感資訊

### 3. 防止 SQL Injection

#### FAIL：絕對不要串接 SQL
```typescript
// DANGEROUS - SQL Injection vulnerability
const query = `SELECT * FROM users WHERE email = '${userEmail}'`
await db.query(query)
```

#### PASS：一律使用參數化查詢
```typescript
// Safe - parameterized query
const { data } = await supabase
  .from('users')
  .select('*')
  .eq('email', userEmail)

// Or with raw SQL -- the value goes in the params array, never in the
// string. Use your driver's placeholder syntax (Postgres numbers its
// placeholders, MySQL uses "?").
await db.query(
  'SELECT * FROM users WHERE email = ?',
  [userEmail]
)
```

<!-- 這個檔案裡任何地方都不要寫出字面上的「錢字號加數字」placeholder。
     帶參數呼叫這個 skill 時，它會被替換掉，上面的範例就會變成串接出來的 SQL，
     正是這一節警告要避免的反模式。請用 "?"，並在文字說明裡點出 Postgres 的寫法。 -->

#### 驗證步驟
- [ ] 所有資料庫查詢都用參數化查詢
- [ ] SQL 裡沒有字串串接
- [ ] 正確使用 ORM/query builder
- [ ] Supabase 查詢有適當地清理

### 4. 驗證與授權

#### JWT Token 處理
```typescript
// FAIL: WRONG: localStorage (vulnerable to XSS)
localStorage.setItem('token', token)

// PASS: CORRECT: httpOnly cookies
res.setHeader('Set-Cookie',
  `token=${token}; HttpOnly; Secure; SameSite=Strict; Max-Age=3600`)
```

#### 授權檢查
```typescript
export async function deleteUser(userId: string, requesterId: string) {
  // ALWAYS verify authorization first
  const requester = await db.users.findUnique({
    where: { id: requesterId }
  })

  if (requester.role !== 'admin') {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 403 }
    )
  }

  // Proceed with deletion
  await db.users.delete({ where: { id: userId } })
}
```

#### Row Level Security（Supabase）
```sql
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Users can only view their own data
CREATE POLICY "Users view own data"
  ON users FOR SELECT
  USING (auth.uid() = id);

-- Users can only update their own data
CREATE POLICY "Users update own data"
  ON users FOR UPDATE
  USING (auth.uid() = id);
```

#### 驗證步驟
- [ ] Token 存在 httpOnly cookie 裡（不是 localStorage）
- [ ] 敏感操作之前有授權檢查
- [ ] Supabase 啟用 Row Level Security
- [ ] 實作了角色型存取控制
- [ ] Session 管理安全

### 5. 防止 XSS

#### 清理 HTML
```typescript
import DOMPurify from 'isomorphic-dompurify'

// ALWAYS sanitize user-provided HTML
function renderUserContent(html: string) {
  const clean = DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p'],
    ALLOWED_ATTR: []
  })
  return <div dangerouslySetInnerHTML={{ __html: clean }} />
}
```

#### Content Security Policy

從嚴格開始，要放寬就一定要有文件記載的移除計畫。預設不要用 `'unsafe-inline'` 或 `'unsafe-eval'`，它們會讓 CSP 大部分的保護失效，要當成暫時的相容性債務看待。

```typescript
// next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: `
      default-src 'self';
      base-uri 'self';
      object-src 'none';
      frame-ancestors 'none';
      script-src 'self';
      style-src 'self';
      img-src 'self' data: https:;
      font-src 'self';
      connect-src 'self' https://api.example.com;
    `.replace(/\s{2,}/g, ' ').trim()
  }
]
```

#### 驗證步驟
- [ ] 使用者提供的 HTML 有清理
- [ ] 設定了 CSP header
- [ ] 沒有未驗證的動態內容渲染
- [ ] 使用 React 內建的 XSS 防護

### 6. CSRF 防護

#### CSRF Token
```typescript
import { csrf } from '@/lib/csrf'

export async function POST(request: Request) {
  const token = request.headers.get('X-CSRF-Token')

  if (!csrf.verify(token)) {
    return NextResponse.json(
      { error: 'Invalid CSRF token' },
      { status: 403 }
    )
  }

  // Process request
}
```

#### SameSite Cookie
```typescript
res.setHeader('Set-Cookie',
  `session=${sessionId}; HttpOnly; Secure; SameSite=Strict`)
```

#### 驗證步驟
- [ ] 會改變狀態的操作都有 CSRF token
- [ ] 所有 cookie 都設 SameSite=Strict
- [ ] 實作了 double-submit cookie 模式

### 7. Rate Limiting

#### API Rate Limiting
```typescript
import rateLimit from 'express-rate-limit'

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // 100 requests per window
  message: 'Too many requests'
})

// Apply to routes
app.use('/api/', limiter)
```

#### 昂貴的操作
```typescript
// Aggressive rate limiting for searches
const searchLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 10, // 10 requests per minute
  message: 'Too many search requests'
})

app.use('/api/search', searchLimiter)
```

#### 驗證步驟
- [ ] 所有 API endpoint 都有 rate limiting
- [ ] 昂貴的操作限制更嚴格
- [ ] 以 IP 為基礎的 rate limiting
- [ ] 以使用者為基礎的 rate limiting（已驗證的使用者）

### 8. 敏感資料外洩

#### 日誌
```typescript
// FAIL: WRONG: Logging sensitive data
console.log('User login:', { email, password })
console.log('Payment:', { cardNumber, cvv })

// PASS: CORRECT: Redact sensitive data
console.log('User login:', { email, userId })
console.log('Payment:', { last4: card.last4, userId })
```

#### 錯誤訊息
```typescript
// FAIL: WRONG: Exposing internal details
catch (error) {
  return NextResponse.json(
    { error: error.message, stack: error.stack },
    { status: 500 }
  )
}

// PASS: CORRECT: Generic error messages
catch (error) {
  console.error('Internal error:', error)
  return NextResponse.json(
    { error: 'An error occurred. Please try again.' },
    { status: 500 }
  )
}
```

#### 驗證步驟
- [ ] 日誌裡沒有密碼、token 或 secret
- [ ] 給使用者看的錯誤訊息是通用的
- [ ] 詳細的錯誤只放在伺服器日誌
- [ ] 沒有把 stack trace 暴露給使用者

### 9. 區塊鏈安全（Solana）

#### 錢包驗證
```typescript
import { verify } from '@solana/web3.js'

async function verifyWalletOwnership(
  publicKey: string,
  signature: string,
  message: string
) {
  try {
    const isValid = verify(
      Buffer.from(message),
      Buffer.from(signature, 'base64'),
      Buffer.from(publicKey, 'base64')
    )
    return isValid
  } catch (error) {
    return false
  }
}
```

#### 交易驗證
```typescript
async function verifyTransaction(transaction: Transaction) {
  // Verify recipient
  if (transaction.to !== expectedRecipient) {
    throw new Error('Invalid recipient')
  }

  // Verify amount
  if (transaction.amount > maxAmount) {
    throw new Error('Amount exceeds limit')
  }

  // Verify user has sufficient balance
  const balance = await getBalance(transaction.from)
  if (balance < transaction.amount) {
    throw new Error('Insufficient balance')
  }

  return true
}
```

#### 驗證步驟
- [ ] 錢包簽章有驗證
- [ ] 交易細節有驗證
- [ ] 交易之前有檢查餘額
- [ ] 沒有盲簽交易

### 10. 相依套件安全

#### 定期更新
```bash
# Check for vulnerabilities
npm audit

# Fix automatically fixable issues
npm audit fix

# Update dependencies
npm update

# Check for outdated packages
npm outdated
```

#### Lock 檔
```bash
# ALWAYS commit lock files
git add package-lock.json

# Use in CI/CD for reproducible builds
npm ci  # Instead of npm install
```

#### 驗證步驟
- [ ] 相依套件是最新的
- [ ] 沒有已知漏洞（npm audit 乾淨）
- [ ] Lock 檔有 commit
- [ ] GitHub 上啟用 Dependabot
- [ ] 定期做安全更新

## 安全測試

### 自動化安全測試
```typescript
// Test authentication
test('requires authentication', async () => {
  const response = await fetch('/api/protected')
  expect(response.status).toBe(401)
})

// Test authorization
test('requires admin role', async () => {
  const response = await fetch('/api/admin', {
    headers: { Authorization: `Bearer ${userToken}` }
  })
  expect(response.status).toBe(403)
})

// Test input validation
test('rejects invalid input', async () => {
  const response = await fetch('/api/users', {
    method: 'POST',
    body: JSON.stringify({ email: 'not-an-email' })
  })
  expect(response.status).toBe(400)
})

// Test rate limiting
test('enforces rate limits', async () => {
  const requests = Array(101).fill(null).map(() =>
    fetch('/api/endpoint')
  )

  const responses = await Promise.all(requests)
  const tooManyRequests = responses.filter(r => r.status === 429)

  expect(tooManyRequests.length).toBeGreaterThan(0)
})
```

## 部署前安全檢查清單

任何正式環境部署之前：

- [ ] **Secret**：沒有寫死的 secret，全部放環境變數
- [ ] **輸入驗證**：所有使用者輸入都有驗證
- [ ] **SQL Injection**：所有查詢都參數化
- [ ] **XSS**：使用者內容有清理
- [ ] **CSRF**：已啟用防護
- [ ] **驗證**：Token 處理正確
- [ ] **授權**：有角色檢查
- [ ] **Rate Limiting**：所有 endpoint 都啟用
- [ ] **HTTPS**：正式環境強制使用
- [ ] **安全 Header**：已設定 CSP、X-Frame-Options
- [ ] **錯誤處理**：錯誤裡沒有敏感資料
- [ ] **日誌**：沒有記錄敏感資料
- [ ] **相依套件**：是最新的，沒有漏洞
- [ ] **Row Level Security**：Supabase 已啟用
- [ ] **CORS**：設定正確
- [ ] **檔案上傳**：有驗證（大小、類型）
- [ ] **錢包簽章**：有驗證（如果是區塊鏈）

## 資源

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Next.js Security](https://nextjs.org/docs/security)
- [Supabase Security](https://supabase.com/docs/guides/auth)
- [Web Security Academy](https://portswigger.net/web-security)

---

**記住**：安全不是選配。一個漏洞就可能讓整個平台淪陷。有疑慮的時候，寧可保守。
