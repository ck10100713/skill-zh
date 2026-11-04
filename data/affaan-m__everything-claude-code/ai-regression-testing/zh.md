---
name: ai-regression-testing
description: 給 AI 輔助開發用的回歸測試策略。不依賴資料庫的 sandbox 模式 API 測試、自動化的 bug 檢查流程，以及抓出「同一個模型寫程式又 review」所造成的 AI 盲點的模式。要替 AI 輔助寫出的程式碼補回歸覆蓋，或同一個模型既寫又 review 同一份修改時使用。
metadata:
  origin: ECC
---

# AI 回歸測試

專門為 AI 輔助開發設計的測試模式。在這種開發方式裡，同一個模型既寫程式也 review 程式，會產生系統性的盲點，只有自動化測試抓得到。

## 何時啟用

- AI agent（Claude Code、Cursor、Codex）修改了 API route 或後端邏輯
- 找到並修好了一個 bug，需要防止它再被引入
- 專案有 sandbox/mock 模式，可以用來做免資料庫的測試
- 程式碼修改之後，執行 `/bug-check` 或類似的 review 指令
- 存在多條程式碼路徑（sandbox 對 production、feature flag 等）

## 核心問題

AI 寫完程式再 review 自己的作品時，兩個步驟帶著同樣的假設。這會造成可預測的失敗模式：

```
AI 寫修正 → AI review 修正 → AI 說「看起來正確」 → Bug 還在
```

**真實案例**（在正式環境觀察到的）：

```
Fix 1: 在 API 回應裡加了 notification_settings
  → 忘了把它加進 SELECT 查詢
  → AI review 時漏掉了（同樣的盲點）

Fix 2: 把它加進 SELECT 查詢
  → TypeScript build 錯誤（欄位不在產生出來的型別裡）
  → AI review 了 Fix 1，但沒抓到 SELECT 的問題

Fix 3: 改成 SELECT *
  → 修好了 production 路徑，忘了 sandbox 路徑
  → AI review 時又漏掉了（第 4 次發生）

Fix 4: 測試第一次跑就馬上抓到 PASS:
```

這個模式是：**sandbox/production 路徑不一致**是 AI 引入的第一名回歸。

## Sandbox 模式 API 測試

大多數對 AI 友善的架構，都有 sandbox/mock 模式。這是快速、免資料庫 API 測試的關鍵。

### 設定（Vitest + Next.js App Router）

```typescript
// vitest.config.ts
import { defineConfig } from "vitest/config";
import path from "path";

export default defineConfig({
  test: {
    environment: "node",
    globals: true,
    include: ["__tests__/**/*.test.ts"],
    setupFiles: ["__tests__/setup.ts"],
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "."),
    },
  },
});
```

```typescript
// __tests__/setup.ts
// 強制使用 sandbox 模式，不需要資料庫
process.env.SANDBOX_MODE = "true";
process.env.NEXT_PUBLIC_SUPABASE_URL = "";
process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY = "";
```

### Next.js API Route 的測試 Helper

```typescript
// __tests__/helpers.ts
import { NextRequest } from "next/server";

export function createTestRequest(
  url: string,
  options?: {
    method?: string;
    body?: Record<string, unknown>;
    headers?: Record<string, string>;
    sandboxUserId?: string;
  },
): NextRequest {
  const { method = "GET", body, headers = {}, sandboxUserId } = options || {};
  const fullUrl = url.startsWith("http") ? url : `http://localhost:3000${url}`;
  const reqHeaders: Record<string, string> = { ...headers };

  if (sandboxUserId) {
    reqHeaders["x-sandbox-user-id"] = sandboxUserId;
  }

  const init: { method: string; headers: Record<string, string>; body?: string } = {
    method,
    headers: reqHeaders,
  };

  if (body) {
    init.body = JSON.stringify(body);
    reqHeaders["content-type"] = "application/json";
  }

  return new NextRequest(fullUrl, init);
}

export async function parseResponse(response: Response) {
  const json = await response.json();
  return { status: response.status, json };
}
```

### 撰寫回歸測試

關鍵原則：**替找到過的 bug 寫測試，不是替正常運作的程式碼寫測試**。

```typescript
// __tests__/api/user/profile.test.ts
import { describe, it, expect } from "vitest";
import { createTestRequest, parseResponse } from "../../helpers";
import { GET, PATCH } from "@/app/api/user/profile/route";

// 定義契約：回應裡「必須」有哪些欄位
const REQUIRED_FIELDS = [
  "id",
  "email",
  "full_name",
  "phone",
  "role",
  "created_at",
  "avatar_url",
  "notification_settings",  // ← 發現它漏掉之後才加進來的
];

describe("GET /api/user/profile", () => {
  it("returns all required fields", async () => {
    const req = createTestRequest("/api/user/profile");
    const res = await GET(req);
    const { status, json } = await parseResponse(res);

    expect(status).toBe(200);
    for (const field of REQUIRED_FIELDS) {
      expect(json.data).toHaveProperty(field);
    }
  });

  // 回歸測試：這個一模一樣的 bug，AI 引入過 4 次
  it("notification_settings is not undefined (BUG-R1 regression)", async () => {
    const req = createTestRequest("/api/user/profile");
    const res = await GET(req);
    const { json } = await parseResponse(res);

    expect("notification_settings" in json.data).toBe(true);
    const ns = json.data.notification_settings;
    expect(ns === null || typeof ns === "object").toBe(true);
  });
});
```

### 測試 Sandbox/Production 一致性

最常見的 AI 回歸：修了 production 路徑卻忘了 sandbox 路徑（或反過來）。

```typescript
// 測試 sandbox 的回應符合預期的契約
describe("GET /api/user/messages (conversation list)", () => {
  it("includes partner_name in sandbox mode", async () => {
    const req = createTestRequest("/api/user/messages", {
      sandboxUserId: "user-001",
    });
    const res = await GET(req);
    const { json } = await parseResponse(res);

    // 這個測試抓到過一個 bug：partner_name 被加到
    // production 路徑，但沒加到 sandbox 路徑
    if (json.data.length > 0) {
      for (const conv of json.data) {
        expect("partner_name" in conv).toBe(true);
      }
    }
  });
});
```

## 把測試整合進 Bug-Check 工作流程

### 自訂 Command 定義

```markdown
<!-- .claude/commands/bug-check.md -->
# Bug Check

## Step 1: 自動化測試（必做，不能跳過）

任何 code review 之前，先跑這些指令：

    npm run test       # Vitest 測試套件
    npm run build      # TypeScript 型別檢查 + build

- 測試失敗 → 回報為最高優先的 bug
- Build 失敗 → 把型別錯誤回報為最高優先
- 兩者都通過才進到 Step 2

## Step 2: Code Review（AI review）

1. Sandbox / production 路徑一致性
2. API 回應的形狀符合前端的預期
3. SELECT 子句是否完整
4. 帶有 rollback 的錯誤處理
5. 樂觀更新的 race condition

## Step 3: 每修一個 bug，就提議一個回歸測試
```

### 工作流程

```
User: "バグチェックして" (or "/bug-check")
  │
  ├─ Step 1: npm run test
  │   ├─ FAIL → 機械式地找到 bug（不需要 AI 判斷）
  │   └─ PASS → 繼續
  │
  ├─ Step 2: npm run build
  │   ├─ FAIL → 機械式地找到型別錯誤
  │   └─ PASS → 繼續
  │
  ├─ Step 3: AI code review（心裡記著已知的盲點）
  │   └─ 回報發現的問題
  │
  └─ Step 4: 每個修正都寫一個回歸測試
      └─ 下次 bug-check 就會抓到修正是否被破壞
```

## 常見的 AI 回歸模式

### 模式 1：Sandbox/Production 路徑不一致

**頻率**：最常見（4 次回歸中有 3 次）

```typescript
// FAIL: AI 只把欄位加到 production 路徑
if (isSandboxMode()) {
  return { data: { id, email, name } };  // 缺少新欄位
}
// Production 路徑
return { data: { id, email, name, notification_settings } };

// PASS: 兩條路徑都必須回傳同樣的形狀
if (isSandboxMode()) {
  return { data: { id, email, name, notification_settings: null } };
}
return { data: { id, email, name, notification_settings } };
```

**抓出它的測試**：

```typescript
it("sandbox and production return same fields", async () => {
  // 測試環境裡，sandbox 模式是強制開啟的
  const res = await GET(createTestRequest("/api/user/profile"));
  const { json } = await parseResponse(res);

  for (const field of REQUIRED_FIELDS) {
    expect(json.data).toHaveProperty(field);
  }
});
```

### 模式 2：SELECT 子句遺漏

**頻率**：用 Supabase/Prisma 新增欄位時很常見

```typescript
// FAIL: 新欄位加進回應，卻沒加進 SELECT
const { data } = await supabase
  .from("users")
  .select("id, email, name")  // notification_settings 不在這裡
  .single();

return { data: { ...data, notification_settings: data.notification_settings } };
// → notification_settings 永遠是 undefined

// PASS: 用 SELECT *，或明確包含新欄位
const { data } = await supabase
  .from("users")
  .select("*")
  .single();
```

### 模式 3：錯誤狀態外洩

**頻率**：中等，在既有元件加上錯誤處理時會發生

```typescript
// FAIL: 設了錯誤狀態，但舊資料沒清掉
catch (err) {
  setError("Failed to load");
  // reservations 還顯示著上一個 tab 的資料！
}

// PASS: 發生錯誤時，清掉相關的狀態
catch (err) {
  setReservations([]);  // 清掉過期資料
  setError("Failed to load");
}
```

### 模式 4：樂觀更新沒有適當的 Rollback

```typescript
// FAIL: 失敗時沒有 rollback
const handleRemove = async (id: string) => {
  setItems(prev => prev.filter(i => i.id !== id));
  await fetch(`/api/items/${id}`, { method: "DELETE" });
  // 如果 API 失敗，項目在 UI 上消失了，但還在 DB 裡
};

// PASS: 記下先前的狀態，失敗時 rollback
const handleRemove = async (id: string) => {
  const prevItems = [...items];
  setItems(prev => prev.filter(i => i.id !== id));
  try {
    const res = await fetch(`/api/items/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error("API error");
  } catch {
    setItems(prevItems);  // Rollback
    alert("削除に失敗しました");
  }
};
```

## 策略：在 Bug 出現的地方測試

不要追求 100% 覆蓋率。而是：

```
在 /api/user/profile 找到 bug     → 替 profile API 寫測試
在 /api/user/messages 找到 bug    → 替 messages API 寫測試
在 /api/user/favorites 找到 bug   → 替 favorites API 寫測試
/api/user/notifications 沒有 bug  → （暫時）不寫測試
```

**為什麼這在 AI 開發裡有效：**

1. AI 傾向於反覆犯**同一類的錯誤**
2. Bug 會集中在複雜的區域（驗證、多路徑邏輯、狀態管理）
3. 一旦有測試，那個確切的回歸**就不會再發生**
4. 測試數量隨著 bug 修正自然增長，沒有白費力氣

## 快速參考

| AI 回歸模式 | 測試策略 | 優先順序 |
|---|---|---|
| Sandbox/production 不一致 | 斷言 sandbox 模式下的回應形狀相同 |  高 |
| SELECT 子句遺漏 | 斷言回應裡有所有必要欄位 |  高 |
| 錯誤狀態外洩 | 斷言發生錯誤時狀態有被清掉 |  中 |
| 缺少 rollback | 斷言 API 失敗時狀態有被還原 |  中 |
| 型別轉換遮住 null | 斷言欄位不是 undefined |  中 |

## 該做 / 不該做

**該做：**
- 找到 bug 之後馬上寫測試（可能的話，在修之前寫）
- 測試 API 回應的形狀，不是實作
- 每次 bug-check 的第一步都跑測試
- 讓測試保持快速（用 sandbox 模式，總共不到 1 秒）
- 用它要防止的 bug 來命名測試（例如「BUG-R1 regression」）

**不該做：**
- 替從來沒出過 bug 的程式碼寫測試
- 把 AI 的自我 review 當成自動化測試的替代品
- 因為「只是 mock 資料」就跳過 sandbox 路徑的測試
- 單元測試就夠用時，還去寫整合測試
- 追求覆蓋率的百分比，要追求的是防止回歸
