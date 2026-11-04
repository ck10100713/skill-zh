---
layout: "default"
skill: "migrate-to-shoehorn"
author: "Matt Pocock"
category: "測試與驗證"
summary: "把測試裡的 as 斷言換成 shoehorn"
source: "https://github.com/mattpocock/skills/blob/main/skills/misc/migrate-to-shoehorn/SKILL.md"
license: "MIT"
---

<div class="pair" markdown="1">
<section markdown="1">

## 中文翻譯

{% raw %}
~~~~~markdown
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
~~~~~
{% endraw %}

</section>
<section markdown="1">

## 英文原文

{% raw %}
~~~~~markdown
---
name: migrate-to-shoehorn
description: Migrate test files from `as` type assertions to @total-typescript/shoehorn. Use when user mentions shoehorn, wants to replace `as` in tests, or needs partial test data.
---

# Migrate to Shoehorn

## Why shoehorn?

`shoehorn` lets you pass partial data in tests while keeping TypeScript happy. It replaces `as` assertions with type-safe alternatives.

**Test code only.** Never use shoehorn in production code.

Problems with `as` in tests:

- Trained not to use it
- Must manually specify target type
- Double-as (`as unknown as Type`) for intentionally wrong data

## Install

```bash
npm i @total-typescript/shoehorn
```

## Migration patterns

### Large objects with few needed properties

Before:

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

After:

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

Before:

```ts
getUser({ body: { id: "123" } } as Request);
```

After:

```ts
import { fromPartial } from "@total-typescript/shoehorn";

getUser(fromPartial({ body: { id: "123" } }));
```

### `as unknown as Type` → `fromAny()`

Before:

```ts
getUser({ body: { id: 123 } } as unknown as Request); // wrong type on purpose
```

After:

```ts
import { fromAny } from "@total-typescript/shoehorn";

getUser(fromAny({ body: { id: 123 } }));
```

## When to use each

| Function        | Use case                                           |
| --------------- | -------------------------------------------------- |
| `fromPartial()` | Pass partial data that still type-checks           |
| `fromAny()`     | Pass intentionally wrong data (keeps autocomplete) |
| `fromExact()`   | Force full object (swap with fromPartial later)    |

## Workflow

1. **Gather requirements** - ask user:
   - What test files have `as` assertions causing problems?
   - Are they dealing with large objects where only some properties matter?
   - Do they need to pass intentionally wrong data for error testing?

2. **Install and migrate**:
   - [ ] Install: `npm i @total-typescript/shoehorn`
   - [ ] Find test files with `as` assertions: `grep -r " as [A-Z]" --include="*.test.ts" --include="*.spec.ts"`
   - [ ] Replace `as Type` with `fromPartial()`
   - [ ] Replace `as unknown as Type` with `fromAny()`
   - [ ] Add imports from `@total-typescript/shoehorn`
   - [ ] Run type check to verify
~~~~~
{% endraw %}

</section>
</div>
