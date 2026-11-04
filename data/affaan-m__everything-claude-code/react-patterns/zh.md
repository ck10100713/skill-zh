---
name: react-patterns
description: React 18/19 模式，包括 hook 紀律、server／client component 邊界、Suspense 加 error boundary、form action、資料抓取、狀態管理決策樹，以及無障礙優先的組合方式。寫或 review React 元件時使用。
metadata:
  origin: ECC
---

# React 模式

道地的 React 18/19 模式，用來打造穩健、無障礙、高效能的元件樹。

## 何時啟用

- 寫或修改 React function component、自訂 hook 或元件樹
- Review JSX/TSX 檔案
- 設計狀態形狀或元件組合
- 遷移 class component，或大量依賴 `forwardRef`／`useEffect` 的舊程式碼
- 在區域 state、提升 state、context 和外部 store 之間做選擇
- 處理 Server Component / Client Component（Next.js App Router、RSC）
- 用 React 19 action 或受控 input 實作表單
- 用 TanStack Query / SWR / RSC 串資料抓取

## 核心原則

### 1. Render 是 props 與 state 的純函式

```tsx
// Good: 在 render 期間推導
function Cart({ items }: { items: CartItem[] }) {
  const total = items.reduce((sum, i) => sum + i.price * i.qty, 0);
  return <span>{formatMoney(total)}</span>;
}

// Bad: 另外儲存衍生的 state
function Cart({ items }: { items: CartItem[] }) {
  const [total, setTotal] = useState(0);
  useEffect(() => {
    setTotal(items.reduce((sum, i) => sum + i.price * i.qty, 0));
  }, [items]);
  return <span>{formatMoney(total)}</span>;
}
```

在 `useEffect` 裡處理衍生 state 會多一個 render 週期、可能不同步，還會讓資料流向變得模糊。

### 2. 副作用放在 render 之外

Effect、mutation、網路呼叫和訂閱都放在事件處理器或 `useEffect` 裡，絕對不要放在 render 本體。

### 3. 組合優於繼承

React 對元件沒有繼承模型。用 `children`、render props 或元件 props 來組合。

## Hook 紀律

完整規則請看 [rules/react/hooks.md](../../rules/react/hooks.md)。重點：

- 只能在最上層呼叫，絕對不要放在條件裡
- 每個訂閱、interval、listener 都要清理
- 新 state 取決於舊 state 時，用 functional updater（`setX(prev => prev + 1)`）
- 預設立場：不要 memoize，只有 profiler 或依賴鏈證明有影響時，才加 `useMemo`／`useCallback`
- 同一組 hook 序列出現在 2 個以上的元件時，才抽成自訂 hook

## State 位置決策樹

```
只有一個元件用到？
  -> 在它裡面用 useState

父層加幾個後代元件用到？
  -> 提升到最近的共同祖先

跨很遠的分支使用，而且讀取頻率低（theme、auth、locale）？
  -> React Context

整棵樹共享、更新頻率高？
  -> 外部 store（Zustand、Jotai、Redux Toolkit）

資料來自 server？
  -> server-state 函式庫（TanStack Query、SWR、RSC fetch）
```

大多數頁面不需要 context 或全域 store。在重複提升 state 真的變得痛苦之前，先不要抽象。

## Server / Client Component（RSC）

```tsx
// Server Component - 預設，async，自己絕對不會送 JS 到前端
export default async function ProductPage({ params }: { params: { id: string } }) {
  const product = await db.product.findUnique({ where: { id: params.id } });
  if (!product) notFound();
  return <ProductView product={product} />;
}

// Client Component - 用 "use client" 選擇加入
"use client";
export function AddToCartButton({ productId }: { productId: string }) {
  const [pending, startTransition] = useTransition();
  return (
    <button
      disabled={pending}
      onClick={() => startTransition(() => addToCart(productId))}
    >
      {pending ? "Adding..." : "Add to cart"}
    </button>
  );
}
```

邊界：

- Server -> Client：傳可序列化的 props 或 `children`
- Client -> Server：透過 `<form action={...}>` 呼叫 Server Action，或從事件處理器命令式呼叫
- 絕對不要在 Client Component 檔案裡 `import` Server Component，改用 `children` 組合它們

## Suspense 加 Error Boundary

```tsx
<ErrorBoundary fallback={<ErrorView />}>
  <Suspense fallback={<UserSkeleton />}>
    <UserDetail id={id} />
  </Suspense>
</ErrorBoundary>
```

- Suspense boundary 放在靠近資料的地方，不要放在 route 根部，這樣內容可以漸進顯示
- Error Boundary 仍然是 class API；要 hook 友善的包裝，用 `react-error-boundary`
- boundary 只能抓到子元件 render、生命週期和 constructor 期間丟出的錯誤，抓不到事件處理器或非同步程式碼裡的

## 表單

### React 19 form action（新程式碼首選）

```tsx
"use client";
import { useActionState } from "react";

const initial = { error: null as string | null };

async function updateUserAction(_prev: typeof initial, formData: FormData) {
  "use server";
  const parsed = UserSchema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) return { error: "Invalid input" };
  await db.user.update({ where: { id: parsed.data.id }, data: parsed.data });
  return { error: null };
}

export function UserForm() {
  const [state, formAction, pending] = useActionState(updateUserAction, initial);
  return (
    <form action={formAction}>
      <input name="name" required />
      <button type="submit" disabled={pending}>Save</button>
      {state.error && <p role="alert">{state.error}</p>}
    </form>
  );
}
```

### 受控 input

值會驅動其他 UI、每次按鍵都要格式化，或要做即時驗證時，用受控的。

### 複雜表單

多步驟表單、動態欄位陣列或跨欄位驗證：用函式庫（React Hook Form、TanStack Form）。複雜度超過瑣碎程度的表單還自己土炮狀態管理，是維護陷阱。

## 資料抓取決策表

| 需求 | 工具 |
|---|---|
| Next.js App Router 的每請求資料 | RSC `await fetch()` |
| 客戶端快取加 mutation 加失效 | TanStack Query |
| 輕量客戶端快取加重新驗證 | SWR |
| 即時訂閱 | Server-Sent Events、WebSocket，或函式庫自己的訂閱 API |
| 一次性、丟出去就不管 | 事件處理器裡的 `fetch()` |

應用程式資料避免用 `useEffect` 加 `fetch`：有 race condition、沒有快取、沒有重試，也沒有 Suspense 整合。

## 組合食譜

### 用 `children` 做 slot

```tsx
<Layout>
  <Header />
  <Main>{content}</Main>
</Layout>
```

### 具名 slot

```tsx
<Page header={<Nav />} sidebar={<Filters />}>
  <Results />
</Page>
```

### Compound component（透過 Context 共享 state）

```tsx
<Tabs defaultValue="profile">
  <Tabs.List>
    <Tabs.Trigger value="profile">Profile</Tabs.Trigger>
    <Tabs.Trigger value="settings">Settings</Tabs.Trigger>
  </Tabs.List>
  <Tabs.Panel value="profile"><Profile /></Tabs.Panel>
  <Tabs.Panel value="settings"><Settings /></Tabs.Panel>
</Tabs>
```

### Render prop / function-as-child

當父層需要把參數傳給渲染輸出時很有用：

```tsx
<DataLoader id={id}>
  {({ data, isLoading }) => isLoading ? <Spinner /> : <UserCard user={data} />}
</DataLoader>
```

現代的替代做法：回傳同樣形狀的 hook（`useData(id)`），通常更乾淨。

## 效能

### `React.memo` 什麼時候真的有用

只有在以下情況，才用 `React.memo` 包元件：

1. 它很常重新 render
2. 它的 props 在各次 render 間通常相同
3. 它的 render 可量測地昂貴

`React.memo` 每次 render 都會多一次相等性檢查。如果多數 render 的 props 都不同，這個檢查就純粹是負擔。

### 避免 render 連鎖

- 盡量把 state 往下放，不要往上提
- 拆開 context：每個關注點一個 context，這樣 `themeContext` 變動時，不會讓 auth 的消費者重新 render
- 外部 state 函式庫用 `useSyncExternalStore`，這是安全的 concurrent rendering 所必需的

### 列表

- 提供穩定的 `key` props（資料庫 id，不要用陣列 index）
- 當可見項目數超過約 50 且每列不單純時，用 `@tanstack/react-virtual` 或 `react-window` 虛擬化長列表

## 無障礙優先的組合

- 先 render 語意化 HTML（`<button>`、`<a>`、`<nav>`、`<main>`），再考慮 `role` 屬性
- 每個互動元素都必須能用鍵盤抵達
- 表單 input 需要 label：用 `<label htmlFor>`，或在視覺上由圖示標示時用 `aria-label`
- route 切換和 modal 開關時要管理 focus
- 在元件測試裡跑 `axe`（見 [skills/react-testing](../react-testing/SKILL.md)）
- 交叉連結：[skills/accessibility/SKILL.md](../accessibility/SKILL.md) 涵蓋 WCAG 準則和 pattern 函式庫

## 路由

這個 skill 與 router 無關。上面的模式適用於 React Router、TanStack Router、Next.js App Router、Remix Router。Router 專屬的模式（loader、action、巢狀 layout）請依該 router 的文件，那些是疊在 React 核心之上的框架議題。

## 範圍之外（指引段落）

- **Next.js 專屬**：App Router 資料載入、Route Handler、Middleware、Parallel Route，屬於另一個議題，請看 Next.js 文件
- **React Native**：各平台專屬的模式差異大到值得另開 `react-native-patterns` skill（目前還沒有）
- **Remix**：loader／action 慣例和 RSC 有重疊，但請依 Remix 文件

## 相關

- 規則：[rules/react/](../../rules/react/)：coding-style、hooks、patterns、security、testing
- Skills：[react-performance](../react-performance/SKILL.md) 是源自 Vercel 的效能規則集，[frontend-patterns](../frontend-patterns/SKILL.md) 處理跨框架的 UI 議題，[accessibility](../accessibility/SKILL.md)，[angular-developer](../angular-developer/SKILL.md) 用於框架比較
- Agents：`react-reviewer` 做 code review，`react-build-resolver` 處理 build／bundler 錯誤
- 指令：`/react-review`、`/react-build`、`/react-test`

## 範例

### 防抖搜尋的自訂 hook

```tsx
function useDebounce<T>(value: T, delay = 300): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);
  return debounced;
}

function SearchBox() {
  const [query, setQuery] = useState("");
  const debounced = useDebounce(query, 300);
  const { data } = useQuery({
    queryKey: ["search", debounced],
    queryFn: () => searchApi(debounced),
    enabled: debounced.length > 0,
  });
  return (
    <>
      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      <Results items={data ?? []} />
    </>
  );
}
```

### 搭配 React 19 `useOptimistic` 的 Optimistic UI

```tsx
"use client";
import { useOptimistic } from "react";

export function MessageList({ messages }: { messages: Message[] }) {
  const [optimistic, addOptimistic] = useOptimistic(
    messages,
    (state, newMessage: Message) => [...state, newMessage],
  );

  async function send(formData: FormData) {
    const text = String(formData.get("text"));
    addOptimistic({ id: "pending", text, sender: "me" });
    await saveMessage(text);
  }

  return (
    <>
      <ul>{optimistic.map((m) => <li key={m.id}>{m.text}</li>)}</ul>
      <form action={send}>
        <input name="text" />
        <button type="submit">Send</button>
      </form>
    </>
  );
}
```

### 拆分 context 避免 render 連鎖

```tsx
// 兩個 context：一個很少變，一個常常變
const ThemeContext = createContext<Theme>("light");
const NotificationsContext = createContext<Notification[]>([]);

// 只消費 ThemeContext 的元件，在通知變動時不會重新 render
```
