---
name: web-component-design
description: 精通 React、Vue 和 Svelte 的元件模式，包含 CSS-in-JS、組合（composition）策略和可重複使用的元件架構。建立 UI 元件庫、設計元件 API，或實作前端設計系統時使用。
---

# Web Component Design

用現代框架搭配乾淨的組合模式和樣式做法，打造可重複使用、好維護的 UI 元件。

## When to Use This Skill

- 設計可重複使用的元件庫或設計系統
- 實作複雜的元件組合模式
- 選擇並套用 CSS-in-JS 方案
- 建立無障礙、響應式的 UI 元件
- 在整個 codebase 建立一致的元件 API
- 把舊元件重構成現代模式
- 實作 compound component 或 render props

## Core Concepts

### 1. Component Composition Patterns

**Compound Components**：一起運作的相關元件

```tsx
// Usage
<Select value={value} onChange={setValue}>
  <Select.Trigger>Choose option</Select.Trigger>
  <Select.Options>
    <Select.Option value="a">Option A</Select.Option>
    <Select.Option value="b">Option B</Select.Option>
  </Select.Options>
</Select>
```

**Render Props**：把渲染工作交給父層

```tsx
<DataFetcher url="/api/users">
  {({ data, loading, error }) =>
    loading ? <Spinner /> : <UserList users={data} />
  }
</DataFetcher>
```

**Slots (Vue/Svelte)**：具名的內容注入點

```vue
<template>
  <Card>
    <template #header>Title</template>
    <template #content>Body text</template>
    <template #footer><Button>Action</Button></template>
  </Card>
</template>
```

### 2. CSS-in-JS Approaches

| Solution              | Approach               | Best For                          |
| --------------------- | ---------------------- | --------------------------------- |
| **Tailwind CSS**      | Utility class        | 快速做原型、設計系統 |
| **CSS Modules**       | 有作用域的 CSS 檔案       | 既有的 CSS、漸進式導入    |
| **styled-components** | Template literal      | React、動態樣式            |
| **Emotion**           | 物件/template 樣式 | 彈性高、對 SSR 友善            |
| **Vanilla Extract**   | 零 runtime           | 效能要求高的應用         |

### 3. Component API Design

```tsx
interface ButtonProps {
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  isDisabled?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  children: React.ReactNode;
  onClick?: () => void;
}
```

**原則**：

- 使用語意化的 prop 名稱（`isLoading` 而不是 `loading`）
- 提供合理的預設值
- 透過 `children` 支援組合
- 允許用 `className` 或 `style` 覆寫樣式

## Quick Start: React Component with Tailwind

```tsx
import { forwardRef, type ComponentPropsWithoutRef } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        primary: "bg-blue-600 text-white hover:bg-blue-700",
        secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200",
        ghost: "hover:bg-gray-100 hover:text-gray-900",
      },
      size: {
        sm: "h-8 px-3 text-sm",
        md: "h-10 px-4 text-sm",
        lg: "h-12 px-6 text-base",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  },
);

interface ButtonProps
  extends
    ComponentPropsWithoutRef<"button">,
    VariantProps<typeof buttonVariants> {
  isLoading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, isLoading, children, ...props }, ref) => (
    <button
      ref={ref}
      className={cn(buttonVariants({ variant, size }), className)}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading && <Spinner className="mr-2 h-4 w-4" />}
      {children}
    </button>
  ),
);
Button.displayName = "Button";
```

## Framework Patterns

### React: Compound Components

```tsx
import { createContext, useContext, useState, type ReactNode } from "react";

interface AccordionContextValue {
  openItems: Set<string>;
  toggle: (id: string) => void;
}

const AccordionContext = createContext<AccordionContextValue | null>(null);

function useAccordion() {
  const context = useContext(AccordionContext);
  if (!context) throw new Error("Must be used within Accordion");
  return context;
}

export function Accordion({ children }: { children: ReactNode }) {
  const [openItems, setOpenItems] = useState<Set<string>>(new Set());

  const toggle = (id: string) => {
    setOpenItems((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  return (
    <AccordionContext.Provider value={{ openItems, toggle }}>
      <div className="divide-y">{children}</div>
    </AccordionContext.Provider>
  );
}

Accordion.Item = function AccordionItem({
  id,
  title,
  children,
}: {
  id: string;
  title: string;
  children: ReactNode;
}) {
  const { openItems, toggle } = useAccordion();
  const isOpen = openItems.has(id);

  return (
    <div>
      <button onClick={() => toggle(id)} className="w-full text-left py-3">
        {title}
      </button>
      {isOpen && <div className="pb-3">{children}</div>}
    </div>
  );
};
```

### Vue 3: Composables

```vue
<script setup lang="ts">
import { ref, computed, provide, inject, type InjectionKey } from "vue";

interface TabsContext {
  activeTab: Ref<string>;
  setActive: (id: string) => void;
}

const TabsKey: InjectionKey<TabsContext> = Symbol("tabs");

// Parent component
const activeTab = ref("tab-1");
provide(TabsKey, {
  activeTab,
  setActive: (id: string) => {
    activeTab.value = id;
  },
});

// Child component usage
const tabs = inject(TabsKey);
const isActive = computed(() => tabs?.activeTab.value === props.id);
</script>
```

### Svelte 5: Runes

```svelte
<script lang="ts">
  interface Props {
    variant?: 'primary' | 'secondary';
    size?: 'sm' | 'md' | 'lg';
    onclick?: () => void;
    children: import('svelte').Snippet;
  }

  let { variant = 'primary', size = 'md', onclick, children }: Props = $props();

  const classes = $derived(
    `btn btn-${variant} btn-${size}`
  );
</script>

<button class={classes} {onclick}>
  {@render children()}
</button>
```

## Best Practices

1. **Single Responsibility**：每個元件把一件事做好
2. **Prop Drilling Prevention**：深層巢狀的資料用 context
3. **Accessible by Default**：內建 ARIA 屬性、鍵盤支援
4. **Controlled vs Uncontrolled**：適當時兩種模式都支援
5. **Forward Refs**：讓父層能存取 DOM 節點
6. **Memoization**：render 成本高的地方用 `React.memo`、`useMemo`
7. **Error Boundaries**：包住可能出錯的元件

## Common Issues

- **Prop Explosion**：prop 太多，考慮改用組合
- **Style Conflicts**：用有作用域的樣式或 CSS Modules
- **Re-render Cascades**：用 React DevTools 做 profile，適當地 memo
- **Accessibility Gaps**：用螢幕閱讀器和鍵盤操作測試
- **Bundle Size**：對沒用到的元件 variant 做 tree-shake
