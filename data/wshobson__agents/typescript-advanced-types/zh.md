---
name: typescript-advanced-types
description: 精通 TypeScript 的進階型別系統，包含泛型（generics）、條件型別、映射型別、template literal 和 utility type，用來打造型別安全的應用程式。實作複雜的型別邏輯、建立可重複使用的型別工具，或在 TypeScript 專案中確保編譯期型別安全時使用。
---

# TypeScript Advanced Types

精通 TypeScript 進階型別系統的完整指引，包含泛型、條件型別、映射型別、template literal 型別和 utility type，用來打造穩健、型別安全的應用程式。

## When to Use This Skill

- 建立型別安全的函式庫或框架
- 建立可重複使用的泛型元件
- 實作複雜的型別推論邏輯
- 設計型別安全的 API client
- 建立表單驗證系統
- 建立強型別的設定物件
- 實作型別安全的狀態管理
- 把 JavaScript codebase 遷移到 TypeScript

## Core Concepts

### 1. Generics

**Purpose:** 在維持型別安全的前提下，建立可重複使用、型別彈性高的元件。

**Basic Generic Function:**

```typescript
function identity<T>(value: T): T {
  return value;
}

const num = identity<number>(42); // Type: number
const str = identity<string>("hello"); // Type: string
const auto = identity(true); // Type inferred: boolean
```

**Generic Constraints:**

```typescript
interface HasLength {
  length: number;
}

function logLength<T extends HasLength>(item: T): T {
  console.log(item.length);
  return item;
}

logLength("hello"); // OK: string has length
logLength([1, 2, 3]); // OK: array has length
logLength({ length: 10 }); // OK: object has length
// logLength(42);             // Error: number has no length
```

**Multiple Type Parameters:**

```typescript
function merge<T, U>(obj1: T, obj2: U): T & U {
  return { ...obj1, ...obj2 };
}

const merged = merge({ name: "John" }, { age: 30 });
// Type: { name: string } & { age: number }
```

### 2. Conditional Types

**Purpose:** 建立依條件而定的型別，做出精細的型別邏輯。

**Basic Conditional Type:**

```typescript
type IsString<T> = T extends string ? true : false;

type A = IsString<string>; // true
type B = IsString<number>; // false
```

**Extracting Return Types:**

```typescript
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

function getUser() {
  return { id: 1, name: "John" };
}

type User = ReturnType<typeof getUser>;
// Type: { id: number; name: string; }
```

**Distributive Conditional Types:**

```typescript
type ToArray<T> = T extends any ? T[] : never;

type StrOrNumArray = ToArray<string | number>;
// Type: string[] | number[]
```

**Nested Conditions:**

```typescript
type TypeName<T> = T extends string
  ? "string"
  : T extends number
    ? "number"
    : T extends boolean
      ? "boolean"
      : T extends undefined
        ? "undefined"
        : T extends Function
          ? "function"
          : "object";

type T1 = TypeName<string>; // "string"
type T2 = TypeName<() => void>; // "function"
```

### 3. Mapped Types

**Purpose:** 遍歷既有型別的屬性來轉換它。

**Basic Mapped Type:**

```typescript
type Readonly<T> = {
  readonly [P in keyof T]: T[P];
};

interface User {
  id: number;
  name: string;
}

type ReadonlyUser = Readonly<User>;
// Type: { readonly id: number; readonly name: string; }
```

**Optional Properties:**

```typescript
type Partial<T> = {
  [P in keyof T]?: T[P];
};

type PartialUser = Partial<User>;
// Type: { id?: number; name?: string; }
```

**Key Remapping:**

```typescript
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

interface Person {
  name: string;
  age: number;
}

type PersonGetters = Getters<Person>;
// Type: { getName: () => string; getAge: () => number; }
```

**Filtering Properties:**

```typescript
type PickByType<T, U> = {
  [K in keyof T as T[K] extends U ? K : never]: T[K];
};

interface Mixed {
  id: number;
  name: string;
  age: number;
  active: boolean;
}

type OnlyNumbers = PickByType<Mixed, number>;
// Type: { id: number; age: number; }
```

### 4. Template Literal Types

**Purpose:** 建立以字串為基礎的型別，支援模式比對和轉換。

**Basic Template Literal:**

```typescript
type EventName = "click" | "focus" | "blur";
type EventHandler = `on${Capitalize<EventName>}`;
// Type: "onClick" | "onFocus" | "onBlur"
```

**String Manipulation:**

```typescript
type UppercaseGreeting = Uppercase<"hello">; // "HELLO"
type LowercaseGreeting = Lowercase<"HELLO">; // "hello"
type CapitalizedName = Capitalize<"john">; // "John"
type UncapitalizedName = Uncapitalize<"John">; // "john"
```

**Path Building:**

```typescript
type Path<T> = T extends object
  ? {
      [K in keyof T]: K extends string ? `${K}` | `${K}.${Path<T[K]>}` : never;
    }[keyof T]
  : never;

interface Config {
  server: {
    host: string;
    port: number;
  };
  database: {
    url: string;
  };
}

type ConfigPath = Path<Config>;
// Type: "server" | "database" | "server.host" | "server.port" | "database.url"
```

### 5. Utility Types

**Built-in Utility Types:**

```typescript
// Partial<T> - 讓所有屬性變成可選
type PartialUser = Partial<User>;

// Required<T> - 讓所有屬性變成必填
type RequiredUser = Required<PartialUser>;

// Readonly<T> - 讓所有屬性變成唯讀
type ReadonlyUser = Readonly<User>;

// Pick<T, K> - 挑選特定屬性
type UserName = Pick<User, "name" | "email">;

// Omit<T, K> - 移除特定屬性
type UserWithoutPassword = Omit<User, "password">;

// Exclude<T, U> - 從 union 排除型別
type T1 = Exclude<"a" | "b" | "c", "a">; // "b" | "c"

// Extract<T, U> - 從 union 取出型別
type T2 = Extract<"a" | "b" | "c", "a" | "b">; // "a" | "b"

// NonNullable<T> - 排除 null 和 undefined
type T3 = NonNullable<string | null | undefined>; // string

// Record<K, T> - 建立 key 為 K、value 為 T 的物件型別
type PageInfo = Record<"home" | "about", { title: string }>;
```

## Detailed worked examples and patterns

詳細章節（從 `## Advanced Patterns` 開始）放在 `references/details.md`。上面的導覽摘要不夠用的時候，再去讀那個檔案。

## Best Practices

1. **Use `unknown` over `any`**：強制做型別檢查
2. **Prefer `interface` for object shapes**：錯誤訊息比較好懂
3. **Use `type` for unions and complex types**：比較有彈性
4. **Leverage type inference**：能讓 TypeScript 推論就讓它推論
5. **Create helper types**：建立可重複使用的型別工具
6. **Use const assertions**：保留 literal 型別
7. **Avoid type assertions**：改用 type guard
8. **Document complex types**：加上 JSDoc 註解
9. **Use strict mode**：開啟所有嚴格的編譯器選項
10. **Test your types**：用型別測試驗證型別行為

## Type Testing

```typescript
// Type assertion tests
type AssertEqual<T, U> = [T] extends [U]
  ? [U] extends [T]
    ? true
    : false
  : false;

type Test1 = AssertEqual<string, string>; // true
type Test2 = AssertEqual<string, number>; // false
type Test3 = AssertEqual<string | number, string>; // false

// Expect error helper
type ExpectError<T extends never> = T;

// Example usage
type ShouldError = ExpectError<AssertEqual<string, number>>;
```

## Common Pitfalls

1. **Over-using `any`**：這樣就失去用 TypeScript 的意義了
2. **Ignoring strict null checks**：可能導致 runtime 錯誤
3. **Too complex types**：可能拖慢編譯速度
4. **Not using discriminated unions**：會錯過型別縮小（narrowing）的機會
5. **Forgetting readonly modifiers**：會允許非預期的修改
6. **Circular type references**：可能造成編譯器錯誤
7. **Not handling edge cases**：例如空陣列或 null 值

## Performance Considerations

- 避免過深的巢狀條件型別
- 能用簡單型別就用簡單型別
- 快取複雜的型別運算結果
- 限制遞迴型別的遞迴深度
- 用建置工具在 production 跳過型別檢查
