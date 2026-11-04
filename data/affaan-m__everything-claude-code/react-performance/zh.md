---
name: react-performance
description: 改編自 Vercel Engineering《React Best Practices》（https://github.com/vercel-labs/agent-skills）的 React 與 Next.js 效能最佳化模式。70 多條規則分成 8 個優先級類別：waterfall、bundle 大小、server 端、client 資料抓取、re-render、渲染、JS 微效能、進階。寫、review 或重構 React/Next.js 程式碼以提升效能時使用。
metadata:
  origin: ECC
---

# React 效能

React 18/19 與 Next.js 的效能最佳化模式，改編自 [Vercel Labs `react-best-practices`](https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices)（MIT，v1.0.0）。這個 skill 依優先級組織規則，並提供決策樹式的指引，用在實際的 code review 和重構。

## 何時啟用

- 為了效能寫或 review React/Next.js 程式碼
- 診斷頁面載入慢、互動慢，或 client 端 CPU 過高
- 稽核 bundle 大小或 Lighthouse Core Web Vitals 退化
- 消除 Server Component / API route 裡的 waterfall
- 減少 client 端的 re-render
- 最佳化長列表、動畫或 hydration
- 稽核動到 `app/`、`pages/`、`components/` 或資料層的 PR 裡的最佳化選擇

## 優先級索引

| 優先級 | 類別 | 前綴 | 何時重要 |
|---|---|---|---|
| 1 — CRITICAL | 消除 Waterfall | `async-` | 每當 `await` 後面接著一個獨立的 `await` |
| 2 — CRITICAL | Bundle 大小最佳化 | `bundle-` | 首次載入的 JS、route 層級的 import、第三方函式庫 |
| 3 — HIGH | Server 端效能 | `server-` | RSC、Server Action、API route、SSR |
| 4 — MEDIUM-HIGH | Client 端資料抓取 | `client-` | hook 裡的 SWR / TanStack Query / 原生 `fetch` |
| 5 — MEDIUM | Re-render 最佳化 | `rerender-` | 高頻率的 state 更新、父子元件的扇出 |
| 6 — MEDIUM | 渲染效能 | `rendering-` | 長列表、動畫、hydration |
| 7 — LOW-MEDIUM | JavaScript 效能 | `js-` | 熱迴圈、頻繁配置記憶體 |
| 8 — LOW | 進階模式 | `advanced-` | Effect 與 event 整合、穩定的 ref |

## 1. 消除 Waterfall（CRITICAL）

> 「Waterfall 是效能殺手第一名」：每一個依序執行的 `await` 都會加上完整的網路延遲。

### await 之前先做便宜的條件判斷

在 await 遠端資料之前，先檢查同步條件（props、env、寫死的 flag）。

```ts
// INCORRECT
async function Page({ id }: { id: string }) {
  const flag = await getFlag("show-page");
  if (!flag || !id) return null;
  const data = await getData(id);
  // ...
}

// CORRECT: 先對便宜的同步條件短路
async function Page({ id }: { id: string }) {
  if (!id) return null;
  const flag = await getFlag("show-page");
  if (!flag) return null;
  const data = await getData(id);
}
```

### 等到要用才 await

把 `await` 移進會用到它的分支。

```ts
// INCORRECT: 還沒決定需不需要資料就先 await 了
const user = await getUser(id);
if (mode === "guest") return renderGuest();
return renderUser(user);

// CORRECT
if (mode === "guest") return renderGuest();
const user = await getUser(id);
return renderUser(user);
```

### 獨立的工作用 Promise.all

```ts
// INCORRECT: 依序執行
const user = await getUser(id);
const posts = await getPosts(id);
const followers = await getFollowers(id);

// CORRECT: 平行執行
const [user, posts, followers] = await Promise.all([
  getUser(id),
  getPosts(id),
  getFollowers(id),
]);
```

### 部分依賴：早點開始，晚點才 await

```ts
// CORRECT: 先把所有 promise 都啟動，每個結果要用到時才 await
const userP = getUser(id);
const postsP = getPosts(id);
const profile = await getProfile(id);
if (profile.private) return null;
const [user, posts] = await Promise.all([userP, postsP]);
```

### 用 Suspense 做 streaming

把 `<Suspense>` boundary 推到靠近資料的地方，這樣頁面能先畫出已經有的部分，較慢的子樹再串流進來。代價：內容抵達時會有 layout shift，所以要預留空間（skeleton 或 `min-height`）。

### Server Component：透過組合達成平行

```tsx
// INCORRECT: 同一個元件裡的 sibling await 會依序執行
export default async function Page() {
  const user = await getUser();
  const cart = await getCart();
  return <View user={user} cart={cart} />;
}

// CORRECT: 拆成子元件，React 會平行執行它們
export default async function Page() {
  return (
    <View>
      <UserSection />
      <CartSection />
    </View>
  );
}
```

## 2. Bundle 大小最佳化（CRITICAL）

### 直接 import，不要用 barrel

即使 tree-shaking 已經移除大部分內容，barrel `index.ts` 檔案還是會逼 bundler 走完整個 module graph。直接 import 在很多真實世界的應用裡，可以省下 200-800ms 的首次載入 JS。

```ts
// INCORRECT
import { Button, Card, Modal } from "@/components";

// CORRECT
import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { Modal } from "@/components/Modal";
```

Next.js 13.5+ 有 [Optimize Package Imports](https://nextjs.org/docs/app/api-reference/next-config-js/optimizePackageImports)，會對列出的套件自動處理這件事，用它；沒列在清單上的函式庫，仍然要手動直接 import。

### 可靜態分析的路徑

```ts
// INCORRECT: 讓 bundler／trace 分析失效
const mod = await import(`./pages/${name}`);

// CORRECT: 每個分支都明確寫出來
const mod = name === "home" ? await import("./pages/home") : await import("./pages/about");
```

### 重元件用 dynamic import

```tsx
import dynamic from "next/dynamic";

const HeavyChart = dynamic(() => import("./HeavyChart"), {
  loading: () => <Skeleton />,
  ssr: false, // 僅限 client 端時
});
```

### 延後載入第三方 script

在 hydration **之後**才載入 analytics、logging、客服 widget。用 `next/script` 搭配 `strategy="afterInteractive"`（預設）或 `"lazyOnload"`。

### 條件式載入 module

```tsx
if (user.role === "admin") {
  const { AdminPanel } = await import("./admin/AdminPanel");
  // ...
}
```

### 在 hover/focus 時預載

在 hover 時觸發 `<link rel="preload">` 或 `import()`，這樣使用者點下去時 bundle 已經在快取裡了。

## 3. Server 端效能（HIGH）

### 像對待 API route 一樣驗證 Server Action

每個 `"use server"` 函式都是公開的 endpoint。要在 action 裡面做驗證**和**授權，絕對不要依賴呼叫端 Client Component 的把關。

```ts
"use server";
export async function deleteUser(formData: FormData) {
  const session = await getSession();
  if (!session?.user) throw new Error("Unauthorized");
  const targetId = String(formData.get("id"));
  if (session.user.role !== "admin" && session.user.id !== targetId) {
    throw new Error("Forbidden");
  }
  await db.user.delete({ where: { id: targetId } });
}
```

### 用 `React.cache()` 做單一請求內的去重

```ts
import { cache } from "react";

export const getUser = cache(async (id: string) => {
  return db.user.findUnique({ where: { id } });
});
```

`React.cache` 在單一請求內去重。同一次 render 裡有三個 Server Component 呼叫 `getUser("1")`，等於一次 DB 查詢。

### 跨請求的資料用 LRU cache

不會隨請求變動的資料（設定、查找表），用 LRU cache 或 `unstable_cache` 在 React 之外快取。

### 避免 RSC props 重複序列化

當 Server Component 把同一份資料渲染進多個 Client Component 時，資料會依消費者數量各序列化一次。把 Client Component 往上提，再傳 children。

### 把靜態 I/O 提到 module 範圍

```ts
// CORRECT: module 載入時只執行一次
const fontData = readFileSync(fontPath);

export async function Page() {
  return <Banner font={fontData} />;
}
```

### RSC/SSR 裡不要有可變的 module 層級 state

server 上的 module state 在所有請求之間共享，會造成使用者之間的 race condition。改用請求範圍的儲存（`headers()`、`cookies()`、async context）。

### 最小化傳給 Client Component 的資料

只序列化 Client 需要的東西。去掉欄位、做分頁、在 DB 層就選好要的欄位。

### 巢狀 fetch 對每個項目各自用 Promise.all 平行化

```ts
const users = await getUsers();
const enriched = await Promise.all(
  users.map(async (u) => ({ ...u, posts: await getPostsFor(u.id) })),
);
```

### 用 `after()` 做不阻塞的工作

Next.js 15 的 `after()` 會在回應送出之後才執行工作，例如 logging、快取預熱、analytics。

```ts
import { after } from "next/server";
export async function GET() {
  const data = await getData();
  after(() => logAnalytics(data));
  return Response.json(data);
}
```

## 4. Client 端資料抓取（MEDIUM-HIGH）

### 用 SWR / TanStack Query 去重

多個元件呼叫 `useUser(id)` 應該共用一次網路請求和一份快取。用 SWR 或 TanStack Query，共享資料絕對不要自己土炮 `useEffect` 加 `fetch`。

### 全域事件監聽器去重

```tsx
// INCORRECT: 每個元件各自加一個
useEffect(() => {
  window.addEventListener("scroll", handler);
  return () => window.removeEventListener("scroll", handler);
}, []);

// CORRECT: 透過 hook 加全域 subject，共用單一 listener
const useScroll = createScrollHook(); // 底層是 singleton subject
```

### scroll 用 passive listener

```ts
window.addEventListener("scroll", handler, { passive: true });
```

讓捲動更順；這個 listener 不能呼叫 `preventDefault()`。

### localStorage：加版本並縮小

- 一律存一個 `version` 欄位；schema 變動時升版，並遷移或丟棄舊資料
- payload 要小，`localStorage` 是同步的，會阻塞 main thread

## 5. Re-render 最佳化（MEDIUM）

### 不要訂閱只在 callback 裡用到的 state

```tsx
// INCORRECT: count 每次變動都會 re-render
const count = useStore((s) => s.count);
const handler = () => doSomething(count);

// CORRECT: 呼叫時才讀一次
const handler = () => {
  const count = useStore.getState().count;
  doSomething(count);
};
```

### 把昂貴的工作抽進 memoize 過的元件

```tsx
// CORRECT: 子元件只在 `items` 改變時才 re-render
const Heavy = memo(function Heavy({ items }: { items: Item[] }) {
  return <Chart data={transform(items)} />;
});
```

### 把預設的非 primitive props 提出來

```tsx
// INCORRECT: 每次 render 都產生新陣列，破壞 memo
<List items={items ?? []} />

// CORRECT
const EMPTY: Item[] = [];
<List items={items ?? EMPTY} />
```

### effect 裡的依賴用 primitive

```tsx
// INCORRECT: 每次 render 物件 identity 都是新的
useEffect(() => {}, [{ id, name }]);

// CORRECT: primitive
useEffect(() => {}, [id, name]);
```

### 訂閱衍生的 boolean，不要訂閱原始值

```tsx
// INCORRECT: 購物車任何變動都會 re-render
const cart = useStore((s) => s.cart);
const hasItems = cart.length > 0;

// CORRECT: 只在「是否為空」翻轉時才 re-render
const hasItems = useStore((s) => s.cart.length > 0);
```

### 在 render 期間推導，絕對不要透過 `useEffect`

```tsx
// INCORRECT
const [full, setFull] = useState("");
useEffect(() => setFull(`${first} ${last}`), [first, last]);

// CORRECT
const full = `${first} ${last}`;
```

### 用 functional `setState` 取得穩定的 callback

```tsx
// CORRECT
const increment = useCallback(() => setCount((c) => c + 1), []);
```

### 昂貴的值用 lazy state initializer

```tsx
const [tree] = useState(() => parseTree(largeInput));
```

### 單純的 primitive 不要用 memo

`useMemo(() => x + 1, [x])` 是額外負擔。memo 的價值在物件 identity 和昂貴的運算。

### 依賴獨立的 hook 要拆開

```tsx
// INCORRECT: 任一個來源改變，兩個 selector 都會重跑
const { a, b } = useSomething(source1, source2);

// CORRECT
const a = useA(source1);
const b = useB(source2);
```

### 把互動邏輯移進事件處理器

事件處理器只在使用者動作時執行，`useEffect` 則是依賴一變就重跑。

### 非緊急的更新用 `startTransition`

```tsx
const [pending, startTransition] = useTransition();
startTransition(() => setFilters(newFilters));
```

### 昂貴的 render 用 `useDeferredValue`

```tsx
const deferredQuery = useDeferredValue(query);
const results = useMemo(() => expensiveSearch(deferredQuery), [deferredQuery]);
```

### 短暫又頻繁的值用 `useRef`

適用於經常改變、但不該觸發 re-render 的值（時間戳、最後一個按鍵、累加器）。

### 不要在元件裡面定義元件

```tsx
// INCORRECT: 每次 Outer render，Inner 都是新的元件
function Outer() {
  const Inner = () => <span />;
  return <Inner />;
}
```

每次 render 都會產生新的 `Inner` 型別，破壞 reconciliation，還會讓子元件 unmount。

## 6. 渲染效能（MEDIUM）

### 動畫要動 wrapper，不要動 SVG

對包住 SVG 的 `<div>` wrapper 做 transform 有 GPU 加速；直接 transform SVG 本身則會觸發 paint。

### 長列表用 `content-visibility: auto`

```css
.row { content-visibility: auto; contain-intrinsic-size: auto 80px; }
```

瀏覽器會跳過畫面外的渲染，對有幾百列的列表是大幅改善。

### 把靜態 JSX 提出來

```tsx
const STATIC_HEADER = <h1>Title</h1>;
function Page() {
  return <>{STATIC_HEADER}<Body /></>;
}
```

### SVG：降低座標精度

`d="M10.123456,20.654321"` → `d="M10.12,20.65"`。每個位數都花 byte，而視覺差異只有 sub-pixel。

### 用 inline script 讓 hydration 不閃爍

hydration 之前就需要的值（theme、locale），用 inline `<script>` 在 React mount 之前設定 `document.documentElement.dataset.*`。

### 小範圍地抑制預期中的 hydration 不一致

```tsx
<time suppressHydrationWarning>{new Date().toLocaleString()}</time>
```

**只**用在已知會不一致的葉節點，絕對不要用在包含其他子節點的樹上。

### 用 `<Activity>` 做顯示／隱藏，不要 mount/unmount

React 19 的 `<Activity mode="visible|hidden">` 讓樹的 state 和 effect 保持 mount 但隱藏，對 tab 和 accordion 來說比 unmount/remount 便宜。

### 條件渲染用三元運算子，不要用 `&&`

```tsx
// INCORRECT: `0` 會被渲染成文字節點
{count && <Badge>{count}</Badge>}

// CORRECT
{count > 0 ? <Badge>{count}</Badge> : null}
```

### 載入狀態用 `useTransition`

把 `startTransition` 搭配 action；下一個 state 計算期間，React 會把上一個 UI 顯示為 `isPending`。

### React DOM 資源提示

```tsx
import { preload, preconnect } from "react-dom";
preload("/api/critical", { as: "fetch" });
preconnect("https://api.example.com");
```

### `<script>` 標籤的 `defer` / `async`

`defer` 用於在 DOMContentLoaded 之後依序執行；`async` 用於丟出去就不管。

## 7. JavaScript 效能（LOW-MEDIUM）

- **批次處理 DOM/CSS 變更**：用換 class 或 `cssText` 套用，不要一個屬性一個屬性改
- **重複查找用 `Map`**：`O(1)` 對比 `O(n)` 線性掃描
- **迴圈裡快取屬性存取**：`const len = arr.length`
- **Memoize 純函式**：module 層級的 `Map<key, result>`
- **快取 `localStorage` 的讀取**：同步 API；每次 render 只讀一次
- **把 `filter().map()` 合併成一趟**：`flatMap` 或單一 `for`
- 昂貴的比較之前，**先檢查陣列長度**
- 函式**提早 return**
- 把 **RegExp 提出**迴圈外：編譯不是免費的
- 求最小／最大值用**迴圈**，不要用 `sort()`：`O(n)` 對比 `O(n log n)`
- **成員檢查用 `Set`/`Map`**：`O(1)` 對比 `Array.includes` 的 `O(n)`
- 在意不可變性時，用 **`toSorted()`** 而不是原地修改
- 用 **`flatMap` 一趟完成 map 和 filter**
- 非關鍵工作用 **`requestIdleCallback`**

## 8. 進階模式（LOW）

### `useEffectEvent` 的依賴

`useEffectEvent` 的值是穩定的，**不要**把它們加進 effect 的依賴。

### 事件處理器的 ref

傳給 memoize 過的子元件的穩定 callback：

```tsx
const handlerRef = useRef(handler);
useEffect(() => { handlerRef.current = handler; });
const stable = useCallback((arg) => handlerRef.current(arg), []);
```

### 每次載入應用只初始化一次

module 層級的 singleton（telemetry、logger），用 module 範圍的 flag 把關，不要用 `useEffect`。

### 用 `useLatest` 取得穩定的 callback ref

```tsx
function useLatest<T>(value: T) {
  const ref = useRef(value);
  ref.current = value;
  return ref;
}
```

## 自動化工具

這些規則很多現在都已經自動化了：

- **Next.js 13.5+ Optimize Package Imports**：barrel import 最佳化
- **React Compiler**（RFC，canary 中）：自動 memoization
- **Turbopack**：更快的 build、更好的 tree-shaking
- **Bundle Analyzer**（`@next/bundle-analyzer`）：視覺化首次載入的 JS

專案採用 React Compiler 之後，把 `rerender-*` 的手動 memoization 規則降級成「只用於 review」，因為 compiler 會處理它們。手動寫 `useMemo`/`useCallback` 會變成多餘的雜訊。

## Lighthouse / Web Vitals 對照

| 指標 | 最相關的類別 |
|---|---|
| **LCP**（Largest Contentful Paint） | Waterfall、Bundle 大小、Resource Hint |
| **INP**（Interaction to Next Paint） | Re-render、渲染、JavaScript |
| **CLS**（Cumulative Layout Shift） | 渲染（Suspense 放置位置、圖片尺寸） |
| **TBT**（Total Blocking Time） | Bundle 大小、JavaScript、延後載入第三方 |
| **FID**（舊指標） | Bundle 大小、Hydration |

## 相關

- Skills：[react-patterns](../react-patterns/SKILL.md)、[react-testing](../react-testing/SKILL.md)、[frontend-patterns](../frontend-patterns/SKILL.md)、[accessibility](../accessibility/SKILL.md)、[nextjs-turbopack](../nextjs-turbopack/SKILL.md)
- 規則：[rules/react/](../../rules/react/)
- Agents：`react-reviewer` 在 code review 時強制執行這些規則；`react-build-resolver` 處理相關的 build 失敗
- 指令：`/react-review`、`/react-build`、`/react-test`

## 出處

改編自 Vercel Labs 的 `react-best-practices` skill（MIT License，版權屬於 Vercel Engineering，v1.0.0，2026 年 1 月）。來源：[https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices](https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices)。

這個 skill 把原本 70 條規則的目錄重新整理、改編成單一可瀏覽的參考。完整的原始規則集與延伸範例，請看上游 repo。
