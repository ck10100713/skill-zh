---
name: coding-standards
description: 跨專案通用的基礎寫程式慣例，涵蓋命名、可讀性、不可變性和程式碼品質審查。framework 專屬的模式請用更詳細的前端或後端 skill。適用於審查程式碼品質或命名、而且沒有適用的 framework 專屬 skill 時。
metadata:
  origin: ECC
---

# Coding Standards & Best Practices

適用於各專案的基礎寫程式慣例。

這個 skill 是共用的底線，不是詳細的 framework 作法手冊。

- React、狀態、表單、渲染和 UI 架構，用 `frontend-patterns`。
- repository/service 分層、endpoint 設計、驗證和伺服器端相關的問題，用 `backend-patterns` 或 `api-design`。
- 需要最短、可重複使用的規則層，而不是完整的 skill 導覽時，用 `rules/common/coding-style.md`。

## When to Activate

- 開始新專案或新模組
- 審查程式碼的品質與可維護性
- 重構既有程式碼以符合慣例
- 落實命名、格式或結構的一致性
- 設定 lint、格式化或型別檢查規則
- 帶新的貢獻者熟悉寫程式慣例

## Scope Boundaries

適合啟用這個 skill 的情況：
- 描述性的命名
- 預設不可變性
- 落實可讀性、KISS、DRY 和 YAGNI
- 錯誤處理的期望，以及 code smell 審查

不要把這個 skill 當作下列內容的主要依據：
- React 的組合、hook 或渲染模式
- 後端架構、API 設計或資料庫分層
- 已經有更精確的 ECC skill 時的特定領域 framework 指引

## Code Quality Principles

### 1. Readability First
- 程式碼被讀的次數比被寫的次數多
- 變數和函式名稱要清楚
- 自我說明的程式碼優於註解
- 格式要一致

### 2. KISS (Keep It Simple, Stupid)
- 用能動的最簡單解法
- 避免過度設計
- 不要過早最佳化
- 容易理解 > 耍聰明的程式碼

### 3. DRY (Don't Repeat Yourself)
- 把共通邏輯抽成函式
- 建立可重複使用的元件
- 跨模組共用工具函式
- 避免複製貼上式的寫法

### 4. YAGNI (You Aren't Gonna Need It)
- 還沒需要之前，不要先做功能
- 避免投機式的通用化
- 只在必要時才增加複雜度
- 從簡單開始，需要時再重構

## TypeScript/JavaScript Standards

### Variable Naming

```typescript
// PASS: GOOD: 描述性的名稱
const marketSearchQuery = 'election'
const isUserAuthenticated = true
const totalRevenue = 1000

// FAIL: BAD: 不清楚的名稱
const q = 'election'
const flag = true
const x = 1000
```

### Function Naming

```typescript
// PASS: GOOD: 動詞加名詞的模式
async function fetchMarketData(marketId: string) { }
function calculateSimilarity(a: number[], b: number[]) { }
function isValidEmail(email: string): boolean { }

// FAIL: BAD: 不清楚，或只有名詞
async function market(id: string) { }
function similarity(a, b) { }
function email(e) { }
```

### Immutability Pattern (CRITICAL)

```typescript
// PASS: 一律使用 spread 運算子
const updatedUser = {
  ...user,
  name: 'New Name'
}

const updatedArray = [...items, newItem]

// FAIL: 絕對不要直接修改
user.name = 'New Name'  // BAD
items.push(newItem)     // BAD
```

### Error Handling

```typescript
// PASS: GOOD: 完整的錯誤處理
async function fetchData(url: string) {
  try {
    const response = await fetch(url)

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    return await response.json()
  } catch (error) {
    console.error('Fetch failed:', error)
    throw new Error('Failed to fetch data')
  }
}

// FAIL: BAD: 沒有錯誤處理
async function fetchData(url) {
  const response = await fetch(url)
  return response.json()
}
```

### Async/Await Best Practices

```typescript
// PASS: GOOD: 可以的話就平行執行
const [users, markets, stats] = await Promise.all([
  fetchUsers(),
  fetchMarkets(),
  fetchStats()
])

// FAIL: BAD: 不必要的循序執行
const users = await fetchUsers()
const markets = await fetchMarkets()
const stats = await fetchStats()
```

### Type Safety

```typescript
// PASS: GOOD: 正確的型別
interface Market {
  id: string
  name: string
  status: 'active' | 'resolved' | 'closed'
  created_at: Date
}

function getMarket(id: string): Promise<Market> {
  // Implementation
}

// FAIL: BAD: 使用 'any'
function getMarket(id: any): Promise<any> {
  // Implementation
}
```

## React Best Practices

### Component Structure

```typescript
// PASS: GOOD: 有型別的函式元件
interface ButtonProps {
  children: React.ReactNode
  onClick: () => void
  disabled?: boolean
  variant?: 'primary' | 'secondary'
}

export function Button({
  children,
  onClick,
  disabled = false,
  variant = 'primary'
}: ButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`btn btn-${variant}`}
    >
      {children}
    </button>
  )
}

// FAIL: BAD: 沒有型別，結構不清楚
export function Button(props) {
  return <button onClick={props.onClick}>{props.children}</button>
}
```

### Custom Hooks

```typescript
// PASS: GOOD: 可重複使用的自訂 hook
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => clearTimeout(handler)
  }, [value, delay])

  return debouncedValue
}

// 用法
const debouncedQuery = useDebounce(searchQuery, 500)
```

### State Management

```typescript
// PASS: GOOD: 正確的 state 更新
const [count, setCount] = useState(0)

// 以前一個 state 為基礎的更新，用函式形式
setCount(prev => prev + 1)

// FAIL: BAD: 直接引用 state
setCount(count + 1)  // 在非同步情境下可能是過期的值
```

### Conditional Rendering

```typescript
// PASS: GOOD: 清楚的條件渲染
{isLoading && <Spinner />}
{error && <ErrorMessage error={error} />}
{data && <DataDisplay data={data} />}

// FAIL: BAD: 三元運算子地獄
{isLoading ? <Spinner /> : error ? <ErrorMessage error={error} /> : data ? <DataDisplay data={data} /> : null}
```

## API Design Standards

### REST API Conventions

```
GET    /api/markets              # List all markets
GET    /api/markets/:id          # Get specific market
POST   /api/markets              # Create new market
PUT    /api/markets/:id          # Update market (full)
PATCH  /api/markets/:id          # Update market (partial)
DELETE /api/markets/:id          # Delete market

# Query parameters for filtering
GET /api/markets?status=active&limit=10&offset=0
```

### Response Format

```typescript
// PASS: GOOD: 一致的回應結構
interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  meta?: {
    total: number
    page: number
    limit: number
  }
}

// 成功回應
return NextResponse.json({
  success: true,
  data: markets,
  meta: { total: 100, page: 1, limit: 10 }
})

// 錯誤回應
return NextResponse.json({
  success: false,
  error: 'Invalid request'
}, { status: 400 })
```

### Input Validation

```typescript
import { z } from 'zod'

// PASS: GOOD: Schema 驗證
const CreateMarketSchema = z.object({
  name: z.string().min(1).max(200),
  description: z.string().min(1).max(2000),
  endDate: z.string().datetime(),
  categories: z.array(z.string()).min(1)
})

export async function POST(request: Request) {
  const body = await request.json()

  try {
    const validated = CreateMarketSchema.parse(body)
    // 用驗證過的資料繼續處理
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json({
        success: false,
        error: 'Validation failed',
        details: error.issues
      }, { status: 400 })
    }
  }
}
```

## File Organization

### Project Structure

```
src/
├── app/                    # Next.js App Router
│   ├── api/               # API routes
│   ├── markets/           # Market pages
│   └── (auth)/           # Auth pages (route groups)
├── components/            # React components
│   ├── ui/               # Generic UI components
│   ├── forms/            # Form components
│   └── layouts/          # Layout components
├── hooks/                # Custom React hooks
├── lib/                  # Utilities and configs
│   ├── api/             # API clients
│   ├── utils/           # Helper functions
│   └── constants/       # Constants
├── types/                # TypeScript types
└── styles/              # Global styles
```

### File Naming

```
components/Button.tsx          # PascalCase for components
hooks/useAuth.ts              # camelCase with 'use' prefix
lib/formatDate.ts             # camelCase for utilities
types/market.types.ts         # camelCase with .types suffix
```

## Comments & Documentation

### When to Comment

```typescript
// PASS: GOOD: 解釋為什麼（WHY），不是做什麼（WHAT）
// Use exponential backoff to avoid overwhelming the API during outages
const delay = Math.min(1000 * Math.pow(2, retryCount), 30000)

// Deliberately using mutation here for performance with large arrays
items.push(newItem)

// FAIL: BAD: 說明顯而易見的事
// Increment counter by 1
count++

// Set name to user's name
name = user.name
```

### JSDoc for Public APIs

```typescript
/**
 * Searches markets using semantic similarity.
 *
 * @param query - Natural language search query
 * @param limit - Maximum number of results (default: 10)
 * @returns Array of markets sorted by similarity score
 * @throws {Error} If OpenAI API fails or Redis unavailable
 *
 * @example
 * ```typescript
 * const results = await searchMarkets('election', 5)
 * console.log(results[0].name) // "Trump vs Biden"
 * ```
 */
export async function searchMarkets(
  query: string,
  limit: number = 10
): Promise<Market[]> {
  // Implementation
}
```

## Performance Best Practices

### Memoization

```typescript
import { useMemo, useCallback } from 'react'

// PASS: GOOD: 把昂貴的計算 memoize
// 排序前先複製，因為 Array.prototype.sort 會就地修改
const sortedMarkets = useMemo(() => {
  return [...markets].sort((a, b) => b.volume - a.volume)
}, [markets])

// PASS: GOOD: 把 callback memoize
const handleSearch = useCallback((query: string) => {
  setSearchQuery(query)
}, [])
```

### Lazy Loading

```typescript
import { lazy, Suspense } from 'react'

// PASS: GOOD: 延遲載入大型元件
const HeavyChart = lazy(() => import('./HeavyChart'))

export function Dashboard() {
  return (
    <Suspense fallback={<Spinner />}>
      <HeavyChart />
    </Suspense>
  )
}
```

### Database Queries

```typescript
// PASS: GOOD: 只選需要的欄位
const { data } = await supabase
  .from('markets')
  .select('id, name, status')
  .limit(10)

// FAIL: BAD: 全部都選
const { data } = await supabase
  .from('markets')
  .select('*')
```

## Testing Standards

### Test Structure (AAA Pattern)

```typescript
test('calculates similarity correctly', () => {
  // Arrange
  const vector1 = [1, 0, 0]
  const vector2 = [0, 1, 0]

  // Act
  const similarity = calculateCosineSimilarity(vector1, vector2)

  // Assert
  expect(similarity).toBe(0)
})
```

### Test Naming

```typescript
// PASS: GOOD: 描述性的測試名稱
test('returns empty array when no markets match query', () => { })
test('throws error when OpenAI API key is missing', () => { })
test('falls back to substring search when Redis unavailable', () => { })

// FAIL: BAD: 模糊的測試名稱
test('works', () => { })
test('test search', () => { })
```

## Code Smell Detection

留意這些反模式：

### 1. Long Functions
```typescript
// FAIL: BAD: 函式超過 50 行
function processMarketData() {
  // 100 lines of code
}

// PASS: GOOD: 拆成較小的函式
function processMarketData() {
  const validated = validateData()
  const transformed = transformData(validated)
  return saveData(transformed)
}
```

### 2. Deep Nesting
```typescript
// FAIL: BAD: 5 層以上的巢狀
if (user) {
  if (user.isAdmin) {
    if (market) {
      if (market.isActive) {
        if (hasPermission) {
          // Do something
        }
      }
    }
  }
}

// PASS: GOOD: 提早 return
if (!user) return
if (!user.isAdmin) return
if (!market) return
if (!market.isActive) return
if (!hasPermission) return

// Do something
```

### 3. Magic Numbers
```typescript
// FAIL: BAD: 沒有說明的數字
if (retryCount > 3) { }
setTimeout(callback, 500)

// PASS: GOOD: 有名字的常數
const MAX_RETRIES = 3
const DEBOUNCE_DELAY_MS = 500

if (retryCount > MAX_RETRIES) { }
setTimeout(callback, DEBOUNCE_DELAY_MS)
```

**記住**：程式碼品質沒有商量餘地。清楚、好維護的程式碼，才能讓開發快速、重構有信心。
