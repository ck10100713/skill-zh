---
name: vitest
description: "在任何專案裡設定 Vitest 測試：偵測專案類型（Cloudflare Workers、React、Node、library），產生 vitest.config.ts、測試設定、工具函式和一個範例測試。涵蓋 mock 模式、coverage 設定、workspace 設定、Jest 遷移。只要使用者提到新增測試、設定 Vitest、設定測試、從 Jest 遷移、修復測試基礎設施，或問 'how do I test this'，就用這個 skill。"
license: MIT
---

# Vitest Setup

偵測專案類型，產生對的 Vitest 設定，並產出可用的測試基礎設施。這不是一張參考卡，這個 skill 會建立檔案。

## 工作流程

1. **Detect**：掃描專案，判斷類型和現有的設定
2. **Configure**：產生針對該環境量身打造的 vitest.config.ts
3. **Scaffold**：建立測試設定、工具函式和一個範例測試
4. **Wire up**：加上 package.json 的 script 和 TypeScript 設定

## 步驟 1：偵測專案類型

讀這些檔案來判斷專案：

```
package.json          → dependencies, scripts, type field
tsconfig.json         → paths, compiler options
wrangler.toml         → Cloudflare Workers project
vite.config.ts        → existing Vite setup (extend, don't replace)
vitest.config.ts      → already configured? just fill gaps
jest.config.*         → migration candidate
src/                  → source structure
```

分類成下列其中一種：

| 類型 | 訊號 | 環境 |
|------|---------|-------------|
| **Cloudflare Workers** | wrangler.toml、@cloudflare/workers-types、cloudflare vite plugin | `node` 搭配 Workers 專屬設定 |
| **React (Vite)** | @vitejs/plugin-react、react-dom | `jsdom` 或 `happy-dom` |
| **React (SSR/TanStack Start)** | @tanstack/start、vinxi | 分開：server 用 `node`、client 用 `jsdom` |
| **Node/Hono API** | hono、express，沒有 react-dom | `node` |
| **Library** | 有 exports 欄位，沒有框架相依 | `node` |

如果已經有 `vite.config.ts`，就擴充它，不要另外建立 vitest.config.ts，因為 Vitest 原生就會讀 Vite 的設定。

## 步驟 2：安裝相依套件

依偵測到的類型產生安裝指令：

```bash
# Base (always)
pnpm add -D vitest

# React projects — add jsdom and Testing Library
pnpm add -D @vitest/coverage-v8 jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event

# Workers projects — add Cloudflare test utilities
pnpm add -D @vitest/coverage-v8 @cloudflare/vitest-pool-workers

# Node/Hono projects
pnpm add -D @vitest/coverage-v8

# If migrating from Jest, also remove:
pnpm remove jest ts-jest @types/jest jest-environment-jsdom babel-jest
```

使用專案本來用的 package manager（檢查 pnpm-lock.yaml、yarn.lock、bun.lockb 或 package-lock.json）。

## 步驟 3：產生 vitest.config.ts

### Cloudflare Workers

```typescript
import { defineWorkersConfig } from "@cloudflare/vitest-pool-workers/config";

export default defineWorkersConfig({
  test: {
    globals: true,
    poolOptions: {
      workers: {
        wrangler: { configPath: "./wrangler.toml" },
      },
    },
  },
});
```

如果專案使用 Cloudflare Vite plugin（`@cloudflare/vite-plugin`），就改成整合進現有的 vite.config.ts：

```typescript
/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import { cloudflare } from "@cloudflare/vite-plugin";

export default defineConfig({
  plugins: [cloudflare()],
  test: {
    globals: true,
  },
});
```

### React (Vite)

```typescript
/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    css: true,
  },
});
```

如果 vite.config.ts 已經存在，就把 `test` 區塊加進去，不要建立新檔案。

### Node / Hono API

```typescript
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "node",
  },
});
```

### 加上 Coverage（加到任何設定裡）

```typescript
  test: {
    // ... existing config
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "lcov"],
      exclude: [
        "node_modules/",
        "**/*.config.*",
        "**/*.d.ts",
        "**/test/**",
      ],
    },
  },
```

## 步驟 4：產生測試設定檔

建立 `src/test/setup.ts`（只有 React 專案需要）：

```typescript
import "@testing-library/jest-dom/vitest";
```

光這一行 import 就會加入所有自訂的 matcher（toBeInTheDocument、toHaveTextContent 等），並自動註冊 Vitest 的 `expect.extend`。

## 步驟 5：加上 TypeScript 設定

加到 `tsconfig.json` 的 compilerOptions：

```json
{
  "compilerOptions": {
    "types": ["vitest/globals"]
  }
}
```

對有多個 tsconfig 檔案的專案（例如 tsconfig.app.json + tsconfig.node.json），加到涵蓋測試檔案的那一個，通常是根目錄的 tsconfig.json，或是建立一個繼承它的 tsconfig.test.json。

## 步驟 6：加上 Package.json Script

```json
{
  "scripts": {
    "test": "vitest",
    "test:run": "vitest run",
    "test:coverage": "vitest run --coverage",
    "test:ui": "vitest --ui"
  }
}
```

不要覆蓋既有的 script，跟現有的合併。

## 步驟 7：產生範例測試

寫一個測試檔案，示範針對這個專案的正確模式。放在真實的原始碼旁邊，不要放在獨立的 `__tests__` 目錄。

### Hono API route 的範例（例如 `src/routes/health.ts`）：

```typescript
import { describe, it, expect } from "vitest";
import { app } from "../index";

describe("GET /health", () => {
  it("returns 200 with status ok", async () => {
    const res = await app.request("/health");
    expect(res.status).toBe(200);

    const body = await res.json();
    expect(body).toEqual({ status: "ok" });
  });
});
```

### React 元件的範例（例如 `src/components/Button.tsx`）：

```typescript
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Button } from "./Button";

describe("Button", () => {
  it("renders with label", () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole("button", { name: /click me/i })).toBeInTheDocument();
  });

  it("calls onClick when clicked", async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    await user.click(screen.getByRole("button"));
    expect(handleClick).toHaveBeenCalledOnce();
  });
});
```

### 工具函式的範例（例如 `src/utils/format.ts`）：

```typescript
import { describe, it, expect } from "vitest";
import { formatCurrency } from "./format";

describe("formatCurrency", () => {
  it("formats whole numbers", () => {
    expect(formatCurrency(1000)).toBe("$1,000.00");
  });

  it("formats decimals", () => {
    expect(formatCurrency(49.9)).toBe("$49.90");
  });

  it("handles zero", () => {
    expect(formatCurrency(0)).toBe("$0.00");
  });
});
```

從專案裡挑一個真實的檔案來測。不要捏造一個假的 module，範例測試在設定完成後應該能立刻跑起來。

## 步驟 8：驗證

執行測試，確認一切正常：

```bash
pnpm test:run
```

如果失敗，診斷並修好。常見問題：

| 錯誤 | 解法 |
|-------|-----|
| `Cannot find module 'vitest'` | 檢查安裝有沒有完成，檢查 `node_modules/.vitest` 存不存在 |
| `ReferenceError: describe is not defined` | 在設定裡加上 `globals: true`，或在 tsconfig 加上 `types: ["vitest/globals"]` |
| `document is not defined` | 環境錯了，React 測試要設定 `environment: "jsdom"` |
| `Cannot use import.meta` | 確認 vitest.config 用的是 `.ts` 副檔名，且專案有 `"type": "module"`，或由 Vite 處理轉換 |
| Workers binding 是 undefined | 改用 `@cloudflare/vitest-pool-workers`，不要用單純的 vitest，並檢查 wrangler.toml 的路徑 |

---

## Mock 參考

這些模式是設定完成後，寫測試時用的。如果使用者要 mock 的範例，就把它們放進範例測試，或放進 `src/test/examples.test.ts`。

### Module mock（vi.mock）

```typescript
import { vi, describe, it, expect } from "vitest";
import { getUser } from "./api";

vi.mock("./api", () => ({
  getUser: vi.fn(),
}));

it("mocks a module function", async () => {
  vi.mocked(getUser).mockResolvedValue({ id: 1, name: "Test" });
  const user = await getUser(1);
  expect(user.name).toBe("Test");
  expect(getUser).toHaveBeenCalledWith(1);
});
```

### 監視方法（vi.spyOn）

```typescript
it("spies on console.warn", () => {
  const spy = vi.spyOn(console, "warn").mockImplementation(() => {});
  doSomethingThatWarns();
  expect(spy).toHaveBeenCalledOnce();
  spy.mockRestore();
});
```

### 假計時器

```typescript
import { vi, beforeEach, afterEach, it, expect } from "vitest";

beforeEach(() => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date("2026-01-15T10:00:00Z"));
});

afterEach(() => {
  vi.useRealTimers();
});

it("uses controlled time", () => {
  expect(new Date().toISOString()).toBe("2026-01-15T10:00:00.000Z");
});
```

### 全域 stub

```typescript
it("stubs fetch", async () => {
  const mockFetch = vi.fn().mockResolvedValue({
    ok: true,
    json: () => Promise.resolve({ data: "test" }),
  });
  vi.stubGlobal("fetch", mockFetch);

  const res = await fetch("/api/data");
  expect(mockFetch).toHaveBeenCalledWith("/api/data");

  vi.unstubAllGlobals();
});
```

### Snapshot 測試

```typescript
it("matches snapshot", () => {
  const result = generateConfig({ debug: true });
  expect(result).toMatchSnapshot();
});

it("matches inline snapshot", () => {
  expect({ status: "ok", count: 3 }).toMatchInlineSnapshot(`
    {
      "count": 3,
      "status": "ok",
    }
  `);
});
```

### 參數化測試

```typescript
describe.each([
  { input: "hello", expected: "HELLO" },
  { input: "world", expected: "WORLD" },
  { input: "", expected: "" },
])("toUpperCase($input)", ({ input, expected }) => {
  it(`returns ${expected}`, () => {
    expect(input.toUpperCase()).toBe(expected);
  });
});
```

---

## Jest 遷移

當偵測到的專案有 Jest（相依套件裡有 `jest.config.*`、`@types/jest`、`ts-jest`）時：

1. **用上面的步驟產生 vitest.config.ts**
2. **更新既有測試檔案的 import：**

```typescript
// Before
import { jest } from "@jest/globals";
jest.mock("./api");
jest.fn();
jest.spyOn(obj, "method");

// After
import { vi } from "vitest";
vi.mock("./api");
vi.fn();
vi.spyOn(obj, "method");
```

3. **移除 Jest 套件：**
```bash
pnpm remove jest ts-jest @types/jest jest-environment-jsdom babel-jest @jest/globals
```

4. **更新 tsconfig**：把 `"types": ["jest"]` 換成 `"types": ["vitest/globals"]`

5. **執行測試**，修掉剩下的問題

主要的替換對照：

| Jest | Vitest |
|------|--------|
| `jest.fn()` | `vi.fn()` |
| `jest.mock()` | `vi.mock()` |
| `jest.spyOn()` | `vi.spyOn()` |
| `jest.useFakeTimers()` | `vi.useFakeTimers()` |
| `jest.clearAllMocks()` | `vi.clearAllMocks()` |
| `jest.requireActual()` | `vi.importActual()` |
| `@jest/globals` | `vitest` |
| `jest.config.js` | `vitest.config.ts` |

---

## Workspace 設定（Monorepo）

對有多個 package 的 monorepo 專案：

```typescript
// vitest.workspace.ts
import { defineWorkspace } from "vitest/config";

export default defineWorkspace([
  "packages/*/vitest.config.ts",
]);
```

每個 package 都有自己的設定。Workspace 檔案只是指向它們。

---

## 這個 Skill 的產出

執行完之後，專案應該要有：
- `vitest.config.ts`（或把 test 區塊加到既有的 vite.config.ts）
- `src/test/setup.ts`（React 專案）
- 更新過、含 vitest/globals 型別的 `tsconfig.json`
- 更新過、含測試 script 的 `package.json`
- 至少一個針對真實原始碼、會通過的範例測試
- 已安裝的相依套件

測試第一次執行就應該通過。如果沒有，在收工之前先修好。
