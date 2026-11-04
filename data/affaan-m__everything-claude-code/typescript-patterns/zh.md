---
name: typescript-patterns
description: 在現代 TypeScript 和 JavaScript 應用程式裡，寫出嚴格、型別安全、好維護程式碼的 TypeScript 模式。涵蓋嚴格的編譯器設定、型別設計、narrowing、discriminated union、泛型、非同步與錯誤處理、模組邊界、相依套件管理，以及型別層級的測試。寫或 review TypeScript 或 JavaScript 程式碼時使用。
metadata:
  origin: ECC
---

# TypeScript 開發模式

用 TypeScript 建構穩健、型別安全、好維護的應用程式的模式與最佳實務。編譯器在能證明你程式的形狀時最有用，所以這裡的指導原則是：讓型別系統做真正的事，不要跟它對著幹。這個 skill 講的是「怎麼做」。至於「做什麼」和「何時」（要選哪個模式的決定），請看 TypeScript 規則，也就是這個 repo 裡的 `rules/typescript/coding-style.md` 和 `rules/typescript/patterns.md`，安裝後位於 `rules/ecc/typescript/coding-style.md` 和 `rules/ecc/typescript/patterns.md`。

## 何時啟用

- 寫新的 TypeScript 或 JavaScript 程式碼
- Review 一個動到 `.ts` 或 `.tsx` 檔案的 PR
- 重構現有的 TypeScript，移除 `any`、收緊型別，或加強嚴格度
- 為新功能設計型別、泛型或模組邊界
- 建立新的 TypeScript 專案，或升級 `tsconfig.json`
- 除錯在整個程式碼庫裡連鎖出現的型別錯誤（通常是設計問題，不是標註問題）

## 核心原則

### 1. 嚴格模式是基準線

在健康的程式碼庫裡，`strict: true`（它會啟用 `strictNullChecks`、`noImplicitAny`、`strictFunctionTypes` 和其他選項）不是選配。如果程式碼庫在 strict 下編譯不過，那是一個遷移任務，不是把這個 flag 關掉的藉口。

```jsonc
// tsconfig.json — a strict, discriminating baseline
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,
    "noPropertyAccessFromIndexSignature": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "forceConsistentCasingInFileNames": true,
    "verbatimModuleSyntax": true
  }
}
```

`noUncheckedIndexedAccess` 會讓陣列和 record 的存取變成可能是 undefined，這樣一整類的 runtime 崩潰就在編譯時浮現。如果它產生太多雜訊，要加的是下面這個模式，不是把這個 flag 移掉：

```typescript
// If you have proven the index exists, lift the element into a local first.
const [first] = items
if (first === undefined) {
  throw new Error("expected at least one item")
}
```

### 2. `any` 是 bug，不是工具

`any` 把型別系統關掉的地方，剛好是 bug 最可能藏身的地方：跟不可信或動態資料的邊界。優先用 `unknown` 然後 narrow 它。當你真的需要退路時，寧可用帶註解的明確放寬，也不要悄悄地用 `any`。

```typescript
// Bad: any disables checking on the public API
export function parseConfig(raw: any): Config {
  return raw.config ?? {}
}

interface Config {
  timeout: number
  retries: number
}

const DEFAULT_CONFIG: Config = { timeout: 30_000, retries: 3 }

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

function toPositiveInt(value: unknown, field: string): number {
  if (typeof value !== 'number' || !Number.isInteger(value) || value <= 0) {
    throw new TypeError(`Expected ${field} to be a positive integer`)
  }
  return value
}

// Good: unknown forces safe narrowing at the edge. Every consumed field is
// validated with an explicit range, and defaults are declared up front.
export function parseConfig(raw: unknown): Config {
  if (!isRecord(raw)) return { ...DEFAULT_CONFIG }
  return {
    timeout: raw['timeout'] === undefined ? DEFAULT_CONFIG.timeout : toPositiveInt(raw['timeout'], 'timeout'),
    retries: raw['retries'] === undefined ? DEFAULT_CONFIG.retries : toPositiveInt(raw['retries'], 'retries'),
  }
}
```

### 3. 公開 API 要有明確型別，區域變數交給推論

TypeScript 對區域變數的推論很好。匯出的函式如果參數和回傳型別是隱含的，就會把推論的決定洩漏給每個使用者，也讓意圖變得讀不出來。

```typescript
// Bad: exported API without explicit types
export function formatUser(user) {
  return `${user.firstName} ${user.lastName}`
}

// Good: explicit public contract, inferred internals
interface User {
  firstName: string
  lastName: string
}

export function formatUser(user: User): string {
  return `${user.firstName} ${user.lastName}`
}
```

## 型別設計

### Interface vs. Type Alias

可能被擴充或實作的物件形狀用 `interface`；union、intersection、tuple、mapped type 和 utility type 用 `type`。優先用字串字面值 union，不要用 `enum`，除非你需要在 runtime 列舉值，或要跟需要它的程式碼互通。

```typescript
interface User {
  id: string
  email: string
}

type UserRole = 'admin' | 'member'
type AdminUser = User & { role: 'admin' }
```

### Discriminated Union 是預設的狀態機

當一個值可能有多種形狀時，把它建模成帶有字面值 `type`/`kind` 欄位的 discriminated union。這樣窮盡檢查就變成免費的編譯器功能：絕不是 runtime 的退路，缺少分支一律是編譯錯誤。

```typescript
type Transaction =
  | { kind: 'draft'; id: string }
  | { kind: 'submitted'; id: string; submittedAt: Date }
  | { kind: 'paid'; id: string; paidAt: Date; amountCents: number }

function describe(t: Transaction): string {
  switch (t.kind) {
    case 'draft':
      return 'Saved but not sent'
    case 'submitted':
      return `Submitted on ${t.submittedAt.toISOString()}`
    case 'paid':
      return `Paid ${t.amountCents} cents on ${t.paidAt.toISOString()}`
    default:
      // exhaustive: any new member forces this to fail to compile
      return assertNever(t)
  }
}

function assertNever(value: never): never {
  throw new Error(`Unhandled member: ${JSON.stringify(value)}`)
}
```

### 結構不夠時，用 Brand 取得名目安全

結構型別分不出 `CustomerId` 和 `string`。當某個 ID 或單位不能跟另一個搞混時，就加一個 brand（用 unique symbol 當 key 的幽靈欄位）。

```typescript
declare const brand: unique symbol

export type CustomerId = string & { [brand]: 'CustomerId' }

function ensureCustomerId(value: string): CustomerId {
  if (!/^cus_[a-z0-9]+$/.test(value)) {
    throw new TypeError(`Invalid customer id: ${value}`)
  }
  return value as CustomerId
}
```

要把 brand 留在邊界模組內部；絕對不要把 cast 的 helper 暴露到離能證明它合理的驗證很遠的地方。

### 泛型用來建模取決於呼叫端的型別

如果一個值的型別取決於呼叫端提供什麼，就把它做成泛型，不要壓平成 `any` 或 `unknown`，然後在呼叫處手動 cast。

```typescript
// Bad: caller must cast the result
export function getCached(key: string): unknown {
  return cache.get(key)
}

// Good: the caller's type flows through
export function getCached<T>(key: string, parse: (raw: string) => T): T | undefined {
  const raw = cache.get(key)
  if (raw === undefined) return undefined
  return parse(raw)
}
```

要約束泛型，讓契約找得到：當存在形狀假設時，優先用 `T extends SomeShape`，不要用漂浮的 `T`。

### 用選項物件取代位置參數

旋鈕超過兩三個的函式，應該接收單一選項物件。這樣呼叫處可以自我說明，加新旋鈕時也不會造成位置參數的連鎖更動。

```typescript
interface FetchOptions {
  timeoutMs?: number
  retries?: number
  signal?: AbortSignal
}

export async function fetchWithRetry(url: string, options: FetchOptions = {}): Promise<Response> {
  // ...
}
```

## Narrowing 與 Runtime 安全

### 在邊界驗證，在內部信任

不可信的資料從 I/O 邊界進來：API handler、訊息消費者、檔案載入器。用 schema 解析並驗證一次，然後把精煉後的型別帶進整個領域。這就是驗證函式庫（例如 Zod）派上用場的地方：schema 同時是 runtime 檢查和編譯時型別。

```typescript
import { z } from 'zod'

const userInputSchema = z.object({
  email: z.string().email(),
  age: z.number().int().min(0).max(150)
})

export type UserInput = z.infer<typeof userInputSchema>

// validate once at the edge
const input: UserInput = userInputSchema.parse(rawBody)
```

### Type Predicate 與 Assertion Function

守衛形狀時，優先用 type predicate 和 assertion function，不要用沒檢查的 cast。守衛會把不變量寫成文件，而編譯器會檢查它的使用。

```typescript
function isConfig(value: unknown): value is Config {
  if (typeof value !== 'object' || value === null) return false
  if (!('timeout' in value) || !('retries' in value)) return false
  const { timeout, retries } = value
  return (
    typeof timeout === 'number' && Number.isInteger(timeout) && timeout > 0 &&
    typeof retries === 'number' && Number.isInteger(retries) && retries > 0
  )
}
```

要對格式錯誤的值大聲失敗，而不是回傳布林值，就用 assertion signature：

```typescript
function assertIsStringArray(value: unknown): asserts value is string[] {
  if (!Array.isArray(value)) {
    throw new TypeError('Expected an array of strings')
  }
  // Iteration visits sparse positions as undefined instead of skipping them.
  for (const item of value) {
    if (typeof item !== 'string') throw new TypeError('Expected an array of strings')
  }
}
```

### 預設唯讀

當函式不會修改陣列和物件參數時，把它們標成 `readonly`/`ReadonlyArray`。這樣能防止意外的修改，並在簽章上表明意圖。（依照 coding-style 規則，不可變更新優先用展開運算子。）

```typescript
export function totalAmount(items: readonly LineItem[]): number {
  return items.reduce((sum, item) => sum + item.amountCents, 0)
}
```

Runtime 的不可變性（例如 `Object.freeze`）是給熱點應用程式邊界用的；型別位置上的 `readonly` 才是日常的守衛。

## 錯誤處理

### 在邊界失敗，在邊緣處理

`try/catch` 應該放在呼叫端能對失敗採取行動的地方，不要包在每個內部呼叫外面，疊成一堆被吞掉的錯誤。用 async/await 搭配 `try/catch`，並安全地 narrow `unknown` 的錯誤（依照 coding-style 規則）。

這個 endpoint 範例接受由 ASCII 字母、數字、底線和連字號組成的非空 ID，例如 `u_1`。在組出路徑或發出請求之前，要先驗證這個契約。識別碼的文法要依真實的 API 調整。

```typescript
type User = { id: string; email: string }

function isUser(value: unknown): value is User {
  if (typeof value !== 'object' || value === null) return false
  if (!('id' in value) || !('email' in value)) return false
  const { id, email } = value
  return (
    typeof id === 'string' && id.length > 0 &&
    typeof email === 'string' && email.includes('@')
  )
}

function assertUserId(userId: string): void {
  if (typeof userId !== 'string' || userId.length === 0 || /[^A-Za-z0-9_-]/.test(userId)) {
    throw new TypeError('Expected a user ID using letters, digits, "_" or "-"')
  }
}

async function loadUser(userId: string): Promise<User> {
  assertUserId(userId)
  const response = await fetch(`/users/${userId}`)
  if (!response.ok) {
    throw new Error(`Failed to load user ${userId}: ${response.status}`)
  }
  const data: unknown = await response.json()
  if (!isUser(data)) {
    throw new TypeError(`Invalid user payload for ${userId}`)
  }
  return data
}

export async function getUser(userId: string): Promise<User> {
  try {
    return await loadUser(userId)
  } catch (error: unknown) {
    if (error instanceof Error) {
      // known failure mode: retry or surface a friendly message
      throw new Error(`user lookup failed: ${error.message}`, { cause: error })
    }
    throw new TypeError('unknown error shape')
  }
}
```

### 預期中的失敗用 Result 型別

對預期中的業務失敗（驗證、找不到、衝突），用 discriminated 的 `Result` union，讓失敗明確寫在型別裡，而不是藏在例外流程中。

```typescript
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E }

function createUser(input: UserInput): Result<User, ValidationIssue[]> {
  const issues = validate(input)
  if (issues.length > 0) {
    return { ok: false, error: issues }
  }
  return { ok: true, value: { id: generateId(), ...input } }
}
```

例外留給意料之外的情況。預期中的結果屬於回傳型別。

### 保留錯誤 Context

用 `new Error(message, { cause })`（ES2022 起可用），讓原本的失敗鏈在重新包裝後仍然保留。絕對不要把錯誤字串化塞進訊息裡，把 cause 弄丟。

## 非同步模式

### 獨立的 Fan-Out 優先用 `Promise.allSettled`

當結果彼此獨立，而且一個失敗不能讓其他的都掉掉時，用 `Promise.allSettled`，並處理每個 promise 各自的結果。

```typescript
const results: PromiseSettledResult<number>[] = await Promise.allSettled(
  sourceIds.map((id) => fetchCount(id))
)

const total = results.reduce((sum, result) => {
  if (result.status === 'fulfilled') {
    return sum + result.value
  }
  log.warn('count fetch failed', result.reason)
  return sum
}, 0)
```

當你要的是 fail-fast 語意，也就是真正的全有或全無的工作，才用 `Promise.all`。

### 避免無上限的並行

一次 fan-out 好幾百個 promise，會壓垮連線和 event loop。用一個小的 pool 限制並行數。

```typescript
async function mapWithConcurrency<T, R>(
  items: readonly T[],
  limit: number,
  mapper: (item: T) => Promise<R>
): Promise<R[]> {
  if (!Number.isInteger(limit) || limit < 1) {
    throw new RangeError(`Expected concurrency limit to be a positive integer, got: ${limit}`)
  }
  const results: R[] = new Array(items.length)
  let nextIndex = 0

  const workers = Array.from({ length: Math.min(limit, items.length) }, async () => {
    while (true) {
      const index = nextIndex++
      if (index >= items.length) return
      // Required under noUncheckedIndexedAccess: the index is proven
      // in-bounds above, but the compiler still types this T | undefined.
      // Skip only genuine sparse-array holes, mirroring Array.prototype.map:
      // a present `undefined` element is a legitimate value and must still
      // reach the mapper.
      if (!Object.hasOwn(items, index)) continue
      // Presence is proven above, so the indexed access is in-bounds and
      // filled — never a hole and never the compiler's speculative undefined.
      results[index] = await mapper(items[index]!)
    }
  })

  // One worker rejecting rejects the whole pool: Promise.all propagates the
  // first rejection to the caller (fail-fast). That is rejection, not
  // cancellation — the other workers keep running and may settle more of
  // their remaining items after the pool has already rejected. Use
  // Promise.all only when leaving that in-flight work running is acceptable;
  // otherwise use allSettled or thread an AbortSignal through the mapper.
  await Promise.all(workers)
  return results
}
```

### Timeout 與取消

長時間執行或對外的工作，一定要把 `AbortSignal` 串進去，讓呼叫端能取消；底層操作無法中止時，再搭配 `Promise.race` 做硬性的 timeout。

```typescript
function withTimeout<T>(promise: Promise<T>, ms: number): Promise<T> {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error(`Timed out after ${ms}ms`)), ms)
    promise.then(
      (value) => {
        clearTimeout(timer)
        resolve(value)
      },
      (reason) => {
        clearTimeout(timer)
        reject(reason)
      }
    )
  })
}
```

## Null 與 Undefined 的紀律

優先用有區分的做法，不要混用哨兵值。在「找不到」或「不存在」是合理狀態的地方，用 `T | undefined` 並明確檢查；避免深度巢狀的 `?.` 鏈，後面再接會藏 bug 的靜默 fallback。

```typescript
function findUser(id: string): User | undefined {
  return users.get(id)
}

const user = findUser('u_1')
if (user === undefined) {
  return notFound()
}
// from here on, `user` is narrowed to User
```

避免會悄悄接受錯誤型別的 truthiness 檢查（`result` 可能是 `0` 或 `''` 時寫 `if (result)`）。要明確地跟 `undefined`/`null` 比較。

## 模組邊界與 Export

### 小而有名字的模組

在每個模組的邊界，刻意暴露一個介面。優先用明確的具名 export，不要用 default export，並在公開的邊緣重新 export，讓使用者從擁有那個型別的模組 import，而不是從日後可能被重構的深層內部 import。

```typescript
// user/model.ts — internal types
export interface UserAccount {
  id: string
  email: string
  role: UserRole
}

// user/index.ts — public surface
export { type UserAccount, type UserRole } from './model'
export { createUser, findUser, updateUser } from './service'
```

### 避免 Barrel 膨脹和循環 Import

不要建立在模組載入時就 import 所有東西的 barrel（它們會讓 tree-shaking 失效，也會拉長 cold start）。要 import 具體的路徑。循環 import 表示有一個子邊界應該往上收；兩邊都需要的型別，屬於一個誰都不 import 的共用模組。

### 依相依方向切分

讓型別圖指出方向：跨邊界的型別放在契約模組；實作 import 契約；契約絕不 import 實作。在 node/後端程式碼庫裡，大致上就是：`domain`（純型別和規則）→ `application`（use case）→ `infrastructure`（adapter），相依只往內指。

## 相依套件與建置

### 先診斷，再加相依

優先用內建的 `Array`、`Map`、`Promise` 和 `Intl`，不要每個小操作都拉一個工具函式庫進來。一個很小的行內函式，勝過一個必須升級、稽核、並維持相容的相依套件。（Go 的慣用語「少量的複製好過少量的相依」同樣適用於 TypeScript。）

### Runtime 驗證，不是型別信任

在 runtime 驗證的 schema（Zod、validator，或手寫的守衛）是不可信資料和編譯時型別之間的橋樑。各函式庫的做法不同（Zod 和其他 schema 優先的函式庫，是從 schema 推導出型別；某些生態系的 validator 模式則是型別優先，runtime 檢查由它推導出來）。選一個模型，並在整個程式碼庫保持一致。

### 讓編譯器保持增量且快速

大型程式碼庫受益於 `composite: true` 搭配 project references、`incremental` 建置快取，以及在 bundler 支援時使用 `moduleResolution: bundler`。型別檢查太慢是一個流程問題，會把開發者推離型別系統，所以要投資在縮小被檢查的範圍，不要放寬它。

## 效能

### 型別是免費的，結構不是

型別層級的雜耍（mapped type、conditional type、template literal type）在 runtime 不花任何成本，卻可能花掉很多開發者的清晰度。把複雜的型別機制留在邊界模組裡；不要把型別特技表演當成公開的 API 匯出。

### 避免不必要的物件重新命名

在熱點路徑上，反覆複製和展開大型巢狀物件有真實的成本。優先在變更的那一點用展開做不可變更新，但避免對沒變的結構做防禦性的重複複製（例如在 render 路徑或每則訊息的 handler 裡）。

### 對冪等的計算做 Memoize

純粹而昂貴的衍生計算，如果會用同樣的輸入重複出現，就應該放在快取後面。用以 `Map` 為基礎、有明確生命週期的快取，不要用永遠不清的臨時全域快取。

## 型別層級的測試

### 斷言型別，不只是 Runtime

行為測試證明 runtime 的行為；專門的型別測試鎖住公開 API 的契約。一個悄悄放寬的型別就是 regression。

```typescript
import { expectTypeOf } from 'vitest'

expectTypeOf<Result<User, ValidationIssue[]>>().toEqualTypeOf<
  | { ok: true; value: User }
  | { ok: false; error: ValidationIssue[] }
>()
```

### 用 `satisfies` 保留意圖

`satisfies` 會對照某個形狀檢查一個值，卻不把它放寬成那個形狀，是在驗證結構的同時保留字面值型別的理想做法。

```typescript
const statusByAction = {
  new: 'open',
  reopen: 'open',
  close: 'closed'
} as const satisfies Record<Action, Status>
```

## TypeScript 工具整合

### 必備指令

```bash
# Type-check the whole project
npx tsc --noEmit

# Watch mode for fast feedback
npx tsc --noEmit --watch

# Run tests (Vitest)
npx vitest run

# Lint with types-aware rules (typescript-eslint)
npx eslint .

# Formatting
npx prettier --write .
```

### 建議的 Linter 基準

`typescript-eslint` 的 recommended-type-checked 規則集是實用的預設：它把 `no-unsafe-assignment`、`no-unsafe-member-access`、`no-unsafe-argument` 和 `no-unsafe-call`，從風格雜訊提升成類似編譯器的保證。要保留感知型別的設定；如果它很慢，那是專案結構的訊號，不是停用它的理由。

## 要避免的反模式

- **把 `any` 當作加速的捷徑**：它把編譯器的證明變成 runtime 的猜測。改用 `unknown` + narrowing。
- **說謊的 `as` cast**：繞過一個你其實沒執行的檢查的 cast，就是 null 指標和形狀 bug 誕生的地方。先驗證再 cast，並把 cast 留在做驗證的模組裡。
- **深度巢狀的 callback / promise 鏈**：優先用 async/await；扁平的程式碼才是可以 narrow 的程式碼。
- **`enum` 強制轉型的 bug**：字串字面值 union 給你同樣的安全，卻沒有 runtime 產物，也沒有反向對應的陷阱。
- **巨大的 god type**：一個建模好幾個不相關形狀的 interface，應該改成 discriminated union 或好幾個 interface。
- **全是選填的選項物件**：`allOptional` 的設定型別會悄悄吞掉呼叫處的拼字錯誤；函式真正依賴的欄位，優先用必填欄位。
- **靜默的 catch**：`catch {}` 或 `catch (e) { /* nothing */ }` 會藏起呼叫端以為已經處理掉的失敗。
- **混用同步和非同步的錯誤路徑**：`async` 函式一定會把 throw 表現成 rejection，即使在第一個 `await` 之前也一樣。只有回傳 promise 的非 `async` 函式，才可能（在回傳它之前）同步 throw，逼呼叫端處理兩種錯誤形狀。要全面使用 `async`，讓每個失敗都是 rejection：

```typescript
async function asyncFails(): Promise<never> {
  throw new Error('becomes a rejection, never a sync throw')
}

function lazyFails(): Promise<never> {
  throw new Error('throws synchronously — needs try/catch AND .catch')
}
```

**記住**：型別系統是證明工具，不是文書負擔。當一個型別錯誤用合理的標註還是解不掉時，通常該改的是設計，不是編譯器。寧可選無聊、明確、範圍清楚的 TypeScript，也不要花俏的型別引擎。

## 相關 Skills

- `nestjs-patterns`：TypeScript 後端的 NestJS 架構模式（module、controller、provider、DTO 驗證）
- `frontend-patterns`：React 和 Next.js 的元件與狀態模式
- TypeScript 規則（`rules/typescript/`，安裝後位於 `rules/ecc/typescript/`）：這個 skill 把它的「做什麼」和「何時」實作成「怎麼做」
- `prisma-patterns`：TypeScript 應用程式裡使用的資料庫存取模式
