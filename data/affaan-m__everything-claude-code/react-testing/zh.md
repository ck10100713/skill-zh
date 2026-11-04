---
name: react-testing
description: 用 React Testing Library、Vitest/Jest、MSW 做網路 mock、用 axe 做無障礙斷言，來測試 React 元件，並說明元件測試與 Playwright/Cypress 端對端測試之間的分界。寫或修 React 元件、hook 或頁面的測試時使用。
metadata:
  origin: ECC
---

# React 測試

完整的 React 測試模式，涵蓋以行為為主的元件測試、自訂 hook 測試、無障礙斷言，以及網路層級的 mock。

## 何時啟用

- 為 React 元件、自訂 hook 或頁面寫測試
- 為沒有測試的舊元件補測試覆蓋
- 從 Enzyme 或 class component 時代的做法遷移到 React Testing Library
- 為新的 React 專案設定 Vitest 或 Jest
- 在測試裡 mock HTTP 請求
- 斷言無障礙違規
- 判斷哪些測試該放在 RTL、Playwright Component Testing，還是完整的 E2E

## 核心原則

測試使用者看到的和做的事，不要測實作細節。

一個測試應該：

- 用和 production 相同的 provider 來 render 元件
- 透過無障礙查詢（role、label）和 `userEvent` 與它互動
- 斷言看得到的輸出和可觀察的副作用（callback 被觸發、請求送出）

一個測試**不**應該：

- 檢查元件 state、傳給子元件的 props，或呼叫了哪些 hook
- Mock React 本身或框架的 hook
- 斷言 render 次數，或超出影響使用者範圍的 DOM 結構

## 函式庫選擇

| Runner | 何時用 | 備註 |
|---|---|---|
| **Vitest** | Vite、Remix、現代的設定 | 更快、原生 ESM、API 與 Jest 相容 |
| **Jest** | Next.js、CRA、既有的 repo | 許多 React 專案的預設 |
| **Playwright Component Testing** | 需要真實瀏覽器引擎 | JSDOM 缺少所需功能時使用 |
| **Cypress Component Testing** | 要真實瀏覽器，而且已經在用 Cypress | Playwright CT 的替代方案 |

挑一個。除非有清楚的分工，不要在同一個 repo 同時跑 RTL + Vitest 和 Playwright CT。

## 查詢優先順序

React Testing Library 提供三個層級的查詢，由上往下用：

1. **所有人都能用的**：`getByRole`、`getByLabelText`、`getByPlaceholderText`、`getByText`、`getByDisplayValue`
2. **語意的**：`getByAltText`、`getByTitle`
3. **Test ID（最後手段）**：`getByTestId`

```tsx
// Best
screen.getByRole("button", { name: /save/i });

// OK for inputs
screen.getByLabelText("Email");

// Last resort
screen.getByTestId("save-btn");
```

變體：

- `getBy*`：沒有比對到就丟錯
- `queryBy*`：回傳 `null`（用來「斷言不存在」）
- `findBy*`：非同步，回傳 Promise（用在非同步工作之後才出現的元素）

## 用 `userEvent` 模擬使用者互動

```tsx
import userEvent from "@testing-library/user-event";

test("submits the form", async () => {
  const user = userEvent.setup();
  const onSubmit = vi.fn();
  render(<UserForm onSubmit={onSubmit} />);

  await user.type(screen.getByLabelText("Email"), "user@example.com");
  await user.click(screen.getByRole("button", { name: /save/i }));

  expect(onSubmit).toHaveBeenCalledWith({ email: "user@example.com" });
});
```

- `userEvent` 的呼叫一律要 `await`
- 每個測試只呼叫一次 `userEvent.setup()`，重複使用回傳的 `user`
- `userEvent` 模擬真實瀏覽器的事件序列；`fireEvent` 只派發單一個合成事件，優先用 `userEvent`

## 非同步模式

```tsx
// 非同步工作之後才出現的元素
expect(await screen.findByText("Loaded")).toBeInTheDocument();

// 副作用斷言
await waitFor(() => expect(saveSpy).toHaveBeenCalled());

// 應該消失的元素
await waitForElementToBeRemoved(() => screen.queryByText("Loading"));
```

絕對不要用 `setTimeout` 加斷言，會不穩定（flaky）。用上面的 matcher。

## 用 MSW 做網路 mock

Mock Service Worker 在網路層 mock。元件、hook 和 fetch 函式庫的行為都和 production 完全一樣。

### 設定

```ts
// test/setup.ts
import { setupServer } from "msw/node";
import { http, HttpResponse } from "msw";

export const handlers = [
  http.get("/api/users/:id", ({ params }) =>
    HttpResponse.json({ id: params.id, name: "Alice" }),
  ),
  http.post("/api/users", async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ id: "new-id", ...body }, { status: 201 });
  }),
];

export const server = setupServer(...handlers);

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

設定 `onUnhandledRequest: "error"`，讓任何沒 mock 的請求都大聲讓測試失敗，默默通過比紅燈更糟。

### 單一測試的覆寫

```tsx
test("renders error on 500", async () => {
  server.use(
    http.get("/api/users/:id", () => new HttpResponse(null, { status: 500 })),
  );
  render(<UserPage id="1" />);
  expect(await screen.findByText(/something went wrong/i)).toBeInTheDocument();
});
```

## Provider 包裝

把 provider 在 `test-utils.tsx` 裡包一次：

```tsx
// test-utils.tsx
import { render, RenderOptions } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

export function renderWithProviders(
  ui: React.ReactElement,
  options?: RenderOptions,
) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={lightTheme}>
        <MemoryRouter>{ui}</MemoryRouter>
      </ThemeProvider>
    </QueryClientProvider>,
    options,
  );
}

export * from "@testing-library/react";
```

接著在每個測試檔裡 `import { renderWithProviders, screen } from "test-utils"`。

## 自訂 Hook 測試

```tsx
import { renderHook, act } from "@testing-library/react";

test("useCounter increments and decrements", () => {
  const { result } = renderHook(() => useCounter(0));

  expect(result.current.count).toBe(0);

  act(() => result.current.increment());
  expect(result.current.count).toBe(1);

  act(() => result.current.decrement());
  expect(result.current.count).toBe(0);
});

test("useCounter accepts initial value", () => {
  const { result } = renderHook(() => useCounter(10));
  expect(result.current.count).toBe(10);
});

test("useUser fetches user data", async () => {
  // QueryClient 要在 wrapper 外面、每個測試只建立一次，這樣才能撐過 re-render。
  // 在 wrapper closure 裡面建立，會在每次 render 重置快取狀態，造成不穩定的測試。
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  const { result } = renderHook(() => useUser("1"), { wrapper });

  await waitFor(() => expect(result.current.isSuccess).toBe(true));
  expect(result.current.data).toEqual({ id: "1", name: "Alice" });
});
```

- 會改變 state 的呼叫要包在 `act` 裡
- 只透過 hook 的公開 API 測試
- 用到 context 的 hook，要傳入 `wrapper`

## 無障礙斷言

```tsx
import { axe, toHaveNoViolations } from "jest-axe"; // or vitest-axe
expect.extend(toHaveNoViolations);

test("UserCard has no a11y violations", async () => {
  const { container } = render(<UserCard user={mockUser} />);
  expect(await axe(container)).toHaveNoViolations();
});
```

每個互動元件的元件測試裡都要跑 axe。它能抓到：

- 表單 input 缺少 label
- 無效的 ARIA 用法
- 對比度不足（有限制：JSDOM 沒有真正的 CSS 引擎，所以只對 inline style 有效；視覺對比屬於 Playwright 的範圍）
- 圖片缺少 alt 文字
- 標題順序違規

交叉連結：[skills/accessibility/SKILL.md](../accessibility/SKILL.md)，有更完整的 a11y 測試作法。

## 何時**不**該用 Snapshot 測試

渲染輸出的 snapshot：

- 每次樣式一改就壞
- review 時被無腦蓋章
- 測的是實作細節（DOM 結構），不是行為

可以接受的 snapshot 用法：

- 純資料序列化函式（`formatInvoice(invoice)` -> 穩定的字串）
- 產生出來的設定檔（例如 webpack config 輸出）

元件的視覺回歸，用 Playwright/Cypress 截圖或 Percy/Chromatic，要看真正的視覺差異，不是 DOM 字串。

## 何時該改用 Playwright / Cypress

JSDOM（Vitest/Jest 用的）做不到：

- 渲染真正的 layout（flexbox、grid、viewport 查詢）
- 執行原生瀏覽器動畫、CSS transition
- 測試捲動行為、拖放、從剪貼簿貼上
- 處理 iframe、彈出視窗、下載、跨來源流程
- 在受控環境裡跑真實網路，並有完整的 DevTools 支援

以上任何一項，都用 Playwright Component Testing（在真實瀏覽器裡做元件測試）或完整 E2E。見 [e2e-testing skill](../e2e-testing/SKILL.md)。

分界：

- hook、純展示元件、有邏輯的表單 -> RTL
- layout 很重要、或用到 JSDOM 沒有的瀏覽器 API 的元件 -> Playwright CT
- 跨多個頁面的完整使用者流程 -> Playwright/Cypress E2E

## 覆蓋率目標

| 層級 | 目標 |
|---|---|
| 純工具函式 | >=90% |
| 自訂 hook | >=85% |
| 展示元件 | >=80%，看行為，不是看行數 |
| 容器元件 | >=70%，主要路徑加錯誤狀態 |
| 頁面 | E2E 另外涵蓋；至少要有 smoke test |

透過 `vitest.config.ts` / `jest.config.js` 設定：

```ts
// vitest.config.ts
test: {
  coverage: {
    provider: "v8",
    reporter: ["text", "html", "lcov"],
    thresholds: {
      lines: 80,
      functions: 80,
      branches: 70,
      statements: 80,
    },
  },
}
```

## 反模式

- `container.querySelector("...")`：繞過無障礙查詢，真實使用者會失敗的情況下測試卻能通過
- 斷言 render 次數：實作細節
- `jest.mock("react", ...)`：絕對不要 mock React。改重構元件
- 預設就 mock 子元件：測的是整合，不是隔離。只有子元件有很重的副作用時才 mock
- 忽略 `act()` 警告：它們代表真的 bug（unmount 後更新 state、缺少非同步包裝）
- 跨測試共用可變 state：測試順序一變就 flaky
- 把 `it.skip()` 拿掉後仍然通過的測試：你的測試其實沒有斷言你以為的東西

## TDD 工作流程

```
RED     -> 為下一個需求寫會失敗的測試
GREEN   -> 寫剛好能通過的最少元件程式碼
REFACTOR -> 改進元件，測試保持綠燈
REPEAT  -> 下一個需求
```

新元件的做法：

1. 定義元件的 prop 型別和簽名
2. 為最簡單的情況寫第一個測試
3. 驗證它是因為對的原因而失敗
4. 實作到剛好能通過
5. 加下一個測試案例
6. 當第三個類似的測試顯露出模式時，就重構

## 測試指令

```bash
# Vitest
vitest                            # watch 模式
vitest run                        # 一次性執行
vitest run --coverage             # 含覆蓋率
vitest run path/to/file.test.tsx  # 單一檔案

# Jest
jest --watch
jest --coverage
jest path/to/file.test.tsx

# CI 模式
CI=true vitest run --coverage
```

## 相關

- 規則：[rules/react/testing.md](../../rules/react/testing.md)
- Skills：[react-patterns](../react-patterns/SKILL.md)、[accessibility](../accessibility/SKILL.md)、[e2e-testing](../e2e-testing/SKILL.md)、[tdd-workflow](../tdd-workflow/SKILL.md)
- Agents：`react-reviewer`（code review 時檢視測試品質）、`tdd-guide`（強制執行 TDD 流程）
- 指令：`/react-test`、`/react-review`

## 範例

### 用 MSW 與 userEvent 測試表單送出

```tsx
test("submits user form and shows success", async () => {
  server.use(
    http.post("/api/users", () =>
      HttpResponse.json({ id: "1", name: "Alice" }, { status: 201 }),
    ),
  );

  const user = userEvent.setup();
  renderWithProviders(<UserForm />);

  await user.type(screen.getByLabelText("Name"), "Alice");
  await user.type(screen.getByLabelText("Email"), "alice@example.com");
  await user.click(screen.getByRole("button", { name: /save/i }));

  expect(await screen.findByText(/saved successfully/i)).toBeInTheDocument();
});
```

### 測試 error boundary

```tsx
function Broken() {
  throw new Error("boom");
}

test("error boundary renders fallback", () => {
  // 抑制 React 對預期丟出的錯誤所產生的 console.error 雜訊，之後再還原，讓
  // spy 不會跨測試洩漏而掩蓋其他地方的真正錯誤。
  const errorSpy = vi.spyOn(console, "error").mockImplementation(() => {});
  try {
    render(
      <ErrorBoundary fallback={<div>Something went wrong</div>}>
        <Broken />
      </ErrorBoundary>,
    );

    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
  } finally {
    errorSpy.mockRestore();
  }
});
```

### 測試 Suspense boundary

```tsx
test("shows loading then content", async () => {
  renderWithProviders(
    <Suspense fallback={<div>Loading...</div>}>
      <UserDetail id="1" />
    </Suspense>,
  );

  expect(screen.getByText("Loading...")).toBeInTheDocument();
  expect(await screen.findByText("Alice")).toBeInTheDocument();
});
```
