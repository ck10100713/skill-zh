---
name: react-patterns
description: "Vite + Cloudflare 專案用的 React 19 效能模式與組合式架構。50 多條依影響程度排序的規則：消除 waterfall、bundle 優化、避免重新渲染、用組合取代 boolean prop、server/client 邊界，以及 React 19 API。在撰寫、審查或重構 React 元件時使用。觸發詞：'react patterns'、'react review'、'react performance'、'optimise components'、'react best practices'、'composition patterns'、'why is it slow'、'reduce re-renders'、'fix waterfall'。"
compatibility: claude-code-only
allowed-tools:
  - Read
  - Glob
  - Grep
---

# React 模式

React 19 + Vite + Cloudflare Workers 專案的效能與組合模式。寫新元件時當檢查清單用，審查既有程式碼時當審查指南用，覺得哪裡慢或哪裡糾纏時當重構手冊用。

規則依影響程度排序。先修 CRITICAL，再碰 MEDIUM。

## 什麼時候套用

- 撰寫新的 React 元件或頁面
- 審查程式碼的效能問題
- 重構 prop 太多或重新渲染太多的元件
- 除錯「為什麼這麼慢？」或「為什麼會重新渲染？」
- 建立可重複使用的元件庫
- merge 之前的 code review

## 1. 消除 Waterfall（CRITICAL）

本來可以平行的非同步呼叫，卻被依序執行。這是效能的頭號殺手。

| 模式 | 問題 | 修法 |
|---------|---------|-----|
| **依序 await** | `const a = await getA(); const b = await getB();` | `const [a, b] = await Promise.all([getA(), getB()]);` |
| **在子元件裡 fetch** | 父元件渲染，然後子元件 fetch，然後孫元件再 fetch | 把 fetch 提升到最高的共同祖先，再把資料往下傳 |
| **Suspense 連鎖** | 多個 Suspense 邊界依序解析 | 用一個 Suspense 邊界包住所有非同步的兄弟元件 |
| **分支之前先 await** | `const data = await fetch(); if (condition) { use(data); }` | 把 await 移進分支裡，不要 fetch 你可能用不到的東西 |
| **先 import 再渲染** | `const Component = await import('./Heavy'); return <Component />` | 用 `React.lazy()` + `<Suspense>`，fallback 會立刻渲染 |

**怎麼找**：在元件裡搜尋 `await`。每個 `await` 都可能是 waterfall。如果兩個 await 彼此獨立，就應該平行。

## 2. Bundle 大小（CRITICAL）

使用者每多下載 1 KB，就多等 1 KB。

| 模式 | 問題 | 修法 |
|---------|---------|-----|
| **Barrel import** | `import { Button } from '@/components'` 會把整個 barrel 檔案拉進來 | `import { Button } from '@/components/ui/button'`，直接 import |
| **沒有 code splitting** | 重型元件在每個頁面都載入 | `React.lazy(() => import('./HeavyComponent'))` + `<Suspense>` |
| **載入時就載第三方套件** | 分析/追蹤在 app 渲染之前就載入 | 在 hydration 之後再載：`useEffect(() => { import('./analytics') }, [])` |
| **整個函式庫 import** | `import _ from 'lodash'`（70KB） | `import debounce from 'lodash/debounce'`（1KB） |
| **Lucide tree-shaking** | `import * as Icons from 'lucide-react'`（所有圖示） | 明確列出：`import { Home, Settings } from 'lucide-react'` |
| **React 重複** | 函式庫自己打包了一份 React → "Cannot read properties of null" | 在 vite.config.ts 設定 `resolve.dedupe: ['react', 'react-dom']` |

**怎麼找**：`npx vite-bundle-visualizer`，會顯示你的 bundle 裡有什麼。

## 3. 組合式架構（HIGH）

元件怎麼組織，比你怎麼優化它們更重要。

| 模式 | 問題 | 修法 |
|---------|---------|-----|
| **Boolean prop 爆炸** | `<Card isCompact isClickable showBorder hasIcon isLoading>` | 用明確的變體：`<CompactCard>`、`<ClickableCard>` |
| **Compound component** | 一個複雜的元件有 15 個 prop | 拆成 `<Dialog>`、`<Dialog.Trigger>`、`<Dialog.Content>`，共用 context |
| **renderX prop** | `<Layout renderSidebar={...} renderHeader={...} renderFooter={...}>` | 用 children + 具名 slot：`<Layout><Sidebar /><Header /></Layout>` |
| **狀態提升** | 兄弟元件不能共享狀態 | 把狀態移到父元件或 context provider |
| **Provider 實作** | 使用端的程式碼知道狀態管理的內部細節 | Provider 暴露介面 `{ state, actions, meta }`，把實作藏起來 |
| **Inline 元件** | `function Parent() { function Child() { ... } return <Child /> }` | 把 Child 定義在 Parent 外面，inline 元件每次渲染都會重新掛載 |

**判斷標準**：如果一個元件有超過 5 個 boolean prop，它需要的是組合，不是更多 prop。

## 4. 避免重新渲染（MEDIUM）

不是所有重新渲染都不好。只修那些造成明顯卡頓或浪費運算的重新渲染。

| 模式 | 問題 | 修法 |
|---------|---------|-----|
| **預設的 object/array prop** | `function Foo({ items = [] })` → 每次渲染都產生新的陣列參照 | 提升出去：`const DEFAULT = []; function Foo({ items = DEFAULT })` |
| **在 effect 裡算衍生狀態** | `useEffect(() => setFiltered(items.filter(...)), [items])` | 在渲染時推導：`const filtered = useMemo(() => items.filter(...), [items])` |
| **物件當依賴** | `useEffect(() => {...}, [config])`，如果 config 是 `{}`，每次渲染都會觸發 | 用原始型別當依賴：`useEffect(() => {...}, [config.id, config.type])` |
| **訂閱用不到的狀態** | 元件讀了 `{ user, theme, settings }`，卻只用 `user` | 拆分 context，或用 selector：`useSyncExternalStore` |
| **用 state 存暫時性的值** | 在 mousemove 上 `const [mouseX, setMouseX] = useState(0)` | 對常變動但不需要重新渲染的值用 `useRef` |
| **Inline callback prop** | `<Button onClick={() => doThing(id)} />`：每次渲染都是新函式 | `useCallback` 或函式式 setState：`<Button onClick={handleClick} />` |

**怎麼找**：React DevTools Profiler → "Why did this render?"，或是開發模式下 `<React.StrictMode>` 的雙重渲染。

## 5. React 19 的特別之處（MEDIUM）

在 React 19 有變動或是全新的模式。

| 模式 | 舊的（React 18） | 新的（React 19） |
|---------|---------------|----------------|
| **表單狀態** | `useFormState` | `useActionState`：改名了 |
| **Ref 轉發** | `forwardRef((props, ref) => ...)` | `function Component({ ref, ...props })`：ref 是一般的 prop |
| **Context** | `useContext(MyContext)` | `use(MyContext)`：可以用在條件式和迴圈裡 |
| **Pending UI** | 手動管理 loading 狀態 | `useTransition` + `startTransition`，用於非緊急更新 |
| **Route 層級的 lazy** | 只在 `createBrowserRouter` 有用 | 仍然如此：`<Route lazy={...}>` 在 `<BrowserRouter>` 下會被默默忽略 |
| **樂觀更新** | 手動管理狀態 | `useOptimistic` hook |
| **Metadata** | Helmet 或手動管理 `<head>` | 在元件 JSX 裡寫 `<title>`、`<meta>`、`<link>`，會自動提升到 `<head>` |

## 6. 渲染效能（MEDIUM）

| 模式 | 問題 | 修法 |
|---------|---------|-----|
| **載入時版面位移** | 非同步資料抵達時，內容跳動 | 用尺寸與最終版面相符的骨架畫面 |
| **直接對 SVG 做動畫** | SVG 動畫卡頓 | 包在 `<div>` 裡，改對 div 做動畫 |
| **大型列表渲染** | 表格/列表有 1000 個以上的項目 | 用 `@tanstack/react-virtual` 做虛擬化渲染 |
| **content-visibility** | 很長的可捲動內容一開始就全部渲染 | 對畫面外的區塊設定 `content-visibility: auto` |
| **用 && 做條件渲染** | `{count && <Items />}` 在 count 是 0 時會渲染出 `0` | 改用三元運算子：`{count > 0 ? <Items /> : null}` |

## 7. 資料取得（MEDIUM）

| 模式 | 問題 | 修法 |
|---------|---------|-----|
| **沒有去重** | 同一份資料被 3 個元件各 fetch 一次 | TanStack Query 或 SWR：自動去重 + 快取 |
| **掛載時 fetch** | `useEffect(() => { fetch(...) }, [])`：有 waterfall、沒快取、沒去重 | TanStack Query：`useQuery({ queryKey: ['users'], queryFn: fetchUsers })` |
| **沒有樂觀更新** | 使用者按下儲存，等 2 秒才看到改變 | 用 `useMutation` 搭配 `onMutate` 來即時提供視覺回饋 |
| **Interval 裡的過期 closure** | `setInterval` 捕捉到過期的 state | 用 `useRef` 存 interval ID 和目前的值 |
| **輪詢沒有清理** | useEffect 裡的 `setInterval` 沒有 `clearInterval` | 回傳清理函式：`useEffect(() => { const id = setInterval(...); return () => clearInterval(id); })` |

## 8. Vite + Cloudflare 的特殊情況（MEDIUM）

| 模式 | 問題 | 修法 |
|---------|---------|-----|
| **Node script 裡的 `import.meta.env`** | 是 undefined，只在 Vite 處理過的檔案裡有用 | 用 vite 的 `loadEnv()` |
| **React 重複實例** | 函式庫打包了自己的 React | 在 vite.config.ts 設定 `resolve.dedupe` + `optimizeDeps.include` |
| **Radix Select 空字串** | `<SelectItem value="">` 會丟錯 | 用一個哨兵值：`<SelectItem value="__any__">` |
| **React Hook Form 的 null** | `{...field}` 把 null 傳給 Input | 手動展開：`value={field.value ?? ''}` |
| **Edge 的環境變數** | Workers 裡沒有 `process.env` | 用 `c.env`（Hono context）或 `import.meta.env`（Vite build 時） |

## 當作審查檢查清單使用

審查程式碼時，每個 PR 都要走過第 1-3 類（CRITICAL + HIGH）。第 4-8 類只在關心效能時才看。

```
/react-patterns [file or component path]
```

讀檔案，依優先順序對照規則檢查，並以這個格式回報發現：
```
file:line — [rule] description of issue
```
