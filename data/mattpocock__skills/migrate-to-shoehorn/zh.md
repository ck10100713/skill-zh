---
name: migrate-to-shoehorn
description: 把測試檔從 `as` 型別斷言遷移到 @total-typescript/shoehorn。當使用者提到 shoehorn、想取代測試裡的 `as`，或需要部分的測試資料時使用。
---

# 遷移到 Shoehorn

## 為什麼用 shoehorn？

`shoehorn` 讓你在測試裡傳入部分資料，同時讓 TypeScript 滿意。它用型別安全的替代方案取代 `as` 斷言。

**只用在測試程式碼。** 絕對不要在 production 程式碼裡用 shoehorn。

測試裡用 `as` 的問題：

- 我們被訓練成不要用它
- 必須手動指定目標型別
- 故意傳錯誤資料時要用雙重 as（`as unknown as Type`）

## 安裝

```bash
npm i @total-typescript/shoehorn
```

## 遷移模式

### 大型物件，只需要少數屬性

Before：

```ts
type Request = {
  body: { id: string };
  headers: Record<string, string>;
  cookies: Record<string, string>;
  // ...20 more properties
};

it("gets user by id", () => {
  // Only care about body.id but must fake entire Request
  getUser({
    body: { id: "123" },
    headers: {},
    cookies: {},
    // ...fake all 20 properties
  });
});
```

After：

```ts
import { fromPartial } from "@total-typescript/shoehorn";

it("gets user by id", () => {
  getUser(
    fromPartial({
      body: { id: "123" },
    }),
  );
});
```

### `as Type` → `fromPartial()`

Before：

```ts
getUser({ body: { id: "123" } } as Request);
```

After：

```ts
import { fromPartial } from "@total-typescript/shoehorn";

getUser(fromPartial({ body: { id: "123" } }));
```

### `as unknown as Type` → `fromAny()`

Before：

```ts
getUser({ body: { id: 123 } } as unknown as Request); // wrong type on purpose
```

After：

```ts
import { fromAny } from "@total-typescript/shoehorn";

getUser(fromAny({ body: { id: 123 } }));
```

## 各自什麼時候用

| 函式            | 使用情境                                           |
| --------------- | -------------------------------------------------- |
| `fromPartial()` | 傳入部分資料，而且仍然能通過型別檢查               |
| `fromAny()`     | 傳入刻意錯誤的資料（保留自動完成）                 |
| `fromExact()`   | 強制要完整物件（之後可以換成 fromPartial）         |

## 工作流程

1. **收集需求** - 問使用者：
   - 哪些測試檔有 `as` 斷言造成問題？
   - 他們是不是在處理大型物件，而且只有部分屬性重要？
   - 他們是不是需要為了測試錯誤情況而傳入刻意錯誤的資料？

2. **安裝並遷移**：
   - [ ] 安裝：`npm i @total-typescript/shoehorn`
   - [ ] 找出有 `as` 斷言的測試檔：`grep -r " as [A-Z]" --include="*.test.ts" --include="*.spec.ts"`
   - [ ] 把 `as Type` 換成 `fromPartial()`
   - [ ] 把 `as unknown as Type` 換成 `fromAny()`
   - [ ] 從 `@total-typescript/shoehorn` 加上 import
   - [ ] 跑型別檢查來驗證
