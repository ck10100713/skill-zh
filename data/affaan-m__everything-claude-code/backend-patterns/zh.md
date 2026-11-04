---
name: backend-patterns
description: 給 Node.js、Express 和 Next.js API route 用的後端架構模式、API 設計、資料庫最佳化和伺服器端最佳實務。建構或審查 Node.js、Express 或 Next.js API route 及其資料存取時使用。
metadata:
  origin: ECC
---

# 後端開發模式

給可擴展的伺服器端應用程式用的後端架構模式與最佳實務。

## 何時啟用

- 設計 REST 或 GraphQL API endpoint
- 實作 repository、service 或 controller 層
- 最佳化資料庫查詢（N+1、索引、連線池）
- 加上快取（Redis、記憶體內、HTTP cache header）
- 設定背景 job 或非同步處理
- 規劃 API 的錯誤處理和驗證結構
- 建構 middleware（驗證、logging、速率限制）

## API 設計模式

### RESTful API 結構

```typescript
// PASS: 以資源為基礎的 URL
GET    /api/markets                 # 列出資源
GET    /api/markets/:id             # 取得單一資源
POST   /api/markets                 # 建立資源
PUT    /api/markets/:id             # 取代資源
PATCH  /api/markets/:id             # 更新資源
DELETE /api/markets/:id             # 刪除資源

// PASS: 用 query 參數做過濾、排序、分頁
GET /api/markets?status=active&sort=volume&limit=20&offset=0
```

### Repository 模式

```typescript
// 抽象化資料存取邏輯
interface MarketRepository {
  findAll(filters?: MarketFilters): Promise<Market[]>
  findById(id: string): Promise<Market | null>
  create(data: CreateMarketDto): Promise<Market>
  update(id: string, data: UpdateMarketDto): Promise<Market>
  delete(id: string): Promise<void>
}

class SupabaseMarketRepository implements MarketRepository {
  async findAll(filters?: MarketFilters): Promise<Market[]> {
    let query = supabase.from('markets').select('*')

    if (filters?.status) {
      query = query.eq('status', filters.status)
    }

    if (filters?.limit) {
      query = query.limit(filters.limit)
    }

    const { data, error } = await query

    if (error) throw new Error(error.message)
    return data
  }

  // 其他方法...
}
```

### Service 層模式

```typescript
// 商業邏輯跟資料存取分開
class MarketService {
  constructor(private marketRepo: MarketRepository) {}

  async searchMarkets(query: string, limit: number = 10): Promise<Market[]> {
    // 商業邏輯
    const embedding = await generateEmbedding(query)
    const results = await this.vectorSearch(embedding, limit)

    // 取得完整資料
    const markets = await this.marketRepo.findByIds(results.map(r => r.id))

    // 依相似度排序
    return markets.sort((a, b) => {
      const scoreA = results.find(r => r.id === a.id)?.score || 0
      const scoreB = results.find(r => r.id === b.id)?.score || 0
      return scoreA - scoreB
    })
  }

  private async vectorSearch(embedding: number[], limit: number) {
    // 向量搜尋的實作
  }
}
```

### Middleware 模式

```typescript
// 請求/回應的處理 pipeline
export function withAuth(handler: NextApiHandler): NextApiHandler {
  return async (req, res) => {
    const token = req.headers.authorization?.replace('Bearer ', '')

    if (!token) {
      return res.status(401).json({ error: 'Unauthorized' })
    }

    try {
      const user = await verifyToken(token)
      req.user = user
      return handler(req, res)
    } catch (error) {
      return res.status(401).json({ error: 'Invalid token' })
    }
  }
}

// 用法
export default withAuth(async (req, res) => {
  // Handler 可以存取 req.user
})
```

## 資料庫模式

### 查詢最佳化

```typescript
// PASS: GOOD: 只選需要的欄位
const { data } = await supabase
  .from('markets')
  .select('id, name, status, volume')
  .eq('status', 'active')
  .order('volume', { ascending: false })
  .limit(10)

// FAIL: BAD: 全部都選
const { data } = await supabase
  .from('markets')
  .select('*')
```

### 預防 N+1 查詢

```typescript
// FAIL: BAD: N+1 查詢問題
const markets = await getMarkets()
for (const market of markets) {
  market.creator = await getUser(market.creator_id)  // N 次查詢
}

// PASS: GOOD: 批次抓取
const markets = await getMarkets()
const creatorIds = markets.map(m => m.creator_id)
const creators = await getUsers(creatorIds)  // 1 次查詢
const creatorMap = new Map(creators.map(c => [c.id, c]))

markets.forEach(market => {
  market.creator = creatorMap.get(market.creator_id)
})
```

### Transaction 模式

```typescript
async function createMarketWithPosition(
  marketData: CreateMarketDto,
  positionData: CreatePositionDto
) {
  // 使用 Supabase transaction
  const { data, error } = await supabase.rpc('create_market_with_position', {
    market_data: marketData,
    position_data: positionData
  })

  if (error) throw new Error('Transaction failed')
  return data
}

// Supabase 裡的 SQL 函式
CREATE OR REPLACE FUNCTION create_market_with_position(
  market_data jsonb,
  position_data jsonb
)
RETURNS jsonb
LANGUAGE plpgsql
AS $$
BEGIN
  -- 自動開始 transaction
  INSERT INTO markets VALUES (market_data);
  INSERT INTO positions VALUES (position_data);
  RETURN jsonb_build_object('success', true);
EXCEPTION
  WHEN OTHERS THEN
    -- 會自動 rollback
    RETURN jsonb_build_object('success', false, 'error', SQLERRM);
END;
$$;
```

## 快取策略

### Redis 快取層

```typescript
class CachedMarketRepository implements MarketRepository {
  constructor(
    private baseRepo: MarketRepository,
    private redis: RedisClient
  ) {}

  async findById(id: string): Promise<Market | null> {
    // 先檢查快取
    const cached = await this.redis.get(`market:${id}`)

    if (cached) {
      return JSON.parse(cached)
    }

    // 快取未命中，從資料庫抓取
    const market = await this.baseRepo.findById(id)

    if (market) {
      // 快取 5 分鐘
      await this.redis.setex(`market:${id}`, 300, JSON.stringify(market))
    }

    return market
  }

  async invalidateCache(id: string): Promise<void> {
    await this.redis.del(`market:${id}`)
  }
}
```

### Cache-Aside 模式

```typescript
async function getMarketWithCache(id: string): Promise<Market> {
  const cacheKey = `market:${id}`

  // 試試快取
  const cached = await redis.get(cacheKey)
  if (cached) return JSON.parse(cached)

  // 快取未命中，從資料庫抓取
  const market = await db.markets.findUnique({ where: { id } })

  if (!market) throw new Error('Market not found')

  // 更新快取
  await redis.setex(cacheKey, 300, JSON.stringify(market))

  return market
}
```

## 錯誤處理模式

### 集中式錯誤處理器

```typescript
class ApiError extends Error {
  constructor(
    public statusCode: number,
    public message: string,
    public isOperational = true
  ) {
    super(message)
    Object.setPrototypeOf(this, ApiError.prototype)
  }
}

export function errorHandler(error: unknown, req: Request): Response {
  if (error instanceof ApiError) {
    return NextResponse.json({
      success: false,
      error: error.message
    }, { status: error.statusCode })
  }

  if (error instanceof z.ZodError) {
    return NextResponse.json({
      success: false,
      error: 'Validation failed',
      details: error.issues
    }, { status: 400 })
  }

  // 記錄非預期的錯誤
  console.error('Unexpected error:', error)

  return NextResponse.json({
    success: false,
    error: 'Internal server error'
  }, { status: 500 })
}

// 用法
export async function GET(request: Request) {
  try {
    const data = await fetchData()
    return NextResponse.json({ success: true, data })
  } catch (error) {
    return errorHandler(error, request)
  }
}
```

### 指數退避的重試

```typescript
async function fetchWithRetry<T>(
  fn: () => Promise<T>,
  maxRetries = 3
): Promise<T> {
  let lastError: Error

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error as Error

      if (i < maxRetries - 1) {
        // 指數退避：1 秒、2 秒、4 秒
        const delay = Math.pow(2, i) * 1000
        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }
  }

  throw lastError!
}

// 用法
const data = await fetchWithRetry(() => fetchFromAPI())
```

## 驗證與授權

### JWT Token 驗證

```typescript
import jwt from 'jsonwebtoken'

interface JWTPayload {
  userId: string
  email: string
  role: 'admin' | 'user'
}

export function verifyToken(token: string): JWTPayload {
  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET!) as JWTPayload
    return payload
  } catch (error) {
    throw new ApiError(401, 'Invalid token')
  }
}

export async function requireAuth(request: Request) {
  const token = request.headers.get('authorization')?.replace('Bearer ', '')

  if (!token) {
    throw new ApiError(401, 'Missing authorization token')
  }

  return verifyToken(token)
}

// 在 API route 裡使用
export async function GET(request: Request) {
  const user = await requireAuth(request)

  const data = await getDataForUser(user.userId)

  return NextResponse.json({ success: true, data })
}
```

### 角色式存取控制

```typescript
type Permission = 'read' | 'write' | 'delete' | 'admin'

interface User {
  id: string
  role: 'admin' | 'moderator' | 'user'
}

const rolePermissions: Record<User['role'], Permission[]> = {
  admin: ['read', 'write', 'delete', 'admin'],
  moderator: ['read', 'write', 'delete'],
  user: ['read', 'write']
}

export function hasPermission(user: User, permission: Permission): boolean {
  return rolePermissions[user.role].includes(permission)
}

export function requirePermission(permission: Permission) {
  return (handler: (request: Request, user: User) => Promise<Response>) => {
    return async (request: Request) => {
      const user = await requireAuth(request)

      if (!hasPermission(user, permission)) {
        throw new ApiError(403, 'Insufficient permissions')
      }

      return handler(request, user)
    }
  }
}

// 用法：用高階函式包住 handler
export const DELETE = requirePermission('delete')(
  async (request: Request, user: User) => {
    // Handler 收到的是已驗證、且權限已確認的使用者
    return new Response('Deleted', { status: 200 })
  }
)
```

## 速率限制

速率限制必須使用共用的儲存，例如 Redis、gateway 或
平台原生的限流器。正式環境的 API 不要用每個 process 各自的記憶體內計數器：
它們會在部署時重置、在多個 replica 之間被切開，而且在
serverless 或多 instance 的環境裡會 fail open。

後端這一層負責選擇整合點和錯誤的
形狀；HTTP 契約請用 `api-design`，濫用情境的審查請用 `security-review`。

## 背景 Job 與佇列

### 簡單的佇列模式

```typescript
class JobQueue<T> {
  private queue: T[] = []
  private processing = false

  async add(job: T): Promise<void> {
    this.queue.push(job)

    if (!this.processing) {
      this.process()
    }
  }

  private async process(): Promise<void> {
    this.processing = true

    while (this.queue.length > 0) {
      const job = this.queue.shift()!

      try {
        await this.execute(job)
      } catch (error) {
        console.error('Job failed:', error)
      }
    }

    this.processing = false
  }

  private async execute(job: T): Promise<void> {
    // Job 的執行邏輯
  }
}

// 用在替 market 建索引
interface IndexJob {
  marketId: string
}

const indexQueue = new JobQueue<IndexJob>()

export async function POST(request: Request) {
  const { marketId } = await request.json()

  // 丟進佇列，不要阻塞
  await indexQueue.add({ marketId })

  return NextResponse.json({ success: true, message: 'Job queued' })
}
```

## Logging 與監控

### 結構化 Logging

```typescript
interface LogContext {
  userId?: string
  requestId?: string
  method?: string
  path?: string
  [key: string]: unknown
}

class Logger {
  log(level: 'info' | 'warn' | 'error', message: string, context?: LogContext) {
    const entry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      ...context
    }

    console.log(JSON.stringify(entry))
  }

  info(message: string, context?: LogContext) {
    this.log('info', message, context)
  }

  warn(message: string, context?: LogContext) {
    this.log('warn', message, context)
  }

  error(message: string, error: Error, context?: LogContext) {
    this.log('error', message, {
      ...context,
      error: error.message,
      stack: error.stack
    })
  }
}

const logger = new Logger()

// 用法
export async function GET(request: Request) {
  const requestId = crypto.randomUUID()

  logger.info('Fetching markets', {
    requestId,
    method: 'GET',
    path: '/api/markets'
  })

  try {
    const markets = await fetchMarkets()
    return NextResponse.json({ success: true, data: markets })
  } catch (error) {
    logger.error('Failed to fetch markets', error as Error, { requestId })
    return NextResponse.json({ error: 'Internal error' }, { status: 500 })
  }
}
```

**記住**：後端模式能讓伺服器端應用程式可擴展、好維護。選擇符合你複雜度的模式。
