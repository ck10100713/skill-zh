---
name: react-state-management
description: 精通現代 React 狀態管理，包含 Redux Toolkit、Zustand、Jotai 和 React Query。在設定全域狀態、管理伺服器狀態，或在各種狀態管理方案之間做選擇時使用。
---

# React State Management

一份現代 React 狀態管理模式的完整指南，從元件本地狀態、全域 store，到伺服器狀態同步。

## When to Use This Skill

- 在 React 應用裡設定全域狀態管理
- 在 Redux Toolkit、Zustand 或 Jotai 之間做選擇
- 用 React Query 或 SWR 管理伺服器狀態
- 實作樂觀更新（optimistic update）
- 除錯跟狀態有關的問題
- 從舊版 Redux 遷移到現代寫法

## Core Concepts

### 1. State Categories

| Type             | Description                  | Solutions                     |
| ---------------- | ---------------------------- | ----------------------------- |
| **Local State**  | 元件專屬的 UI 狀態 | useState, useReducer          |
| **Global State** | 跨元件共用     | Redux Toolkit, Zustand, Jotai |
| **Server State** | 遠端資料、快取         | React Query, SWR, RTK Query   |
| **URL State**    | 路由參數、搜尋     | React Router, nuqs            |
| **Form State**   | 輸入值、驗證     | React Hook Form, Formik       |

### 2. Selection Criteria

```
Small app, simple state → Zustand or Jotai
Large app, complex state → Redux Toolkit
Heavy server interaction → React Query + light client state
Atomic/granular updates → Jotai
```

## Quick Start

### Zustand (Simplest)

```typescript
// store/useStore.ts
import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

interface AppState {
  user: User | null
  theme: 'light' | 'dark'
  setUser: (user: User | null) => void
  toggleTheme: () => void
}

export const useStore = create<AppState>()(
  devtools(
    persist(
      (set) => ({
        user: null,
        theme: 'light',
        setUser: (user) => set({ user }),
        toggleTheme: () => set((state) => ({
          theme: state.theme === 'light' ? 'dark' : 'light'
        })),
      }),
      { name: 'app-storage' }
    )
  )
)

// Usage in component
function Header() {
  const { user, theme, toggleTheme } = useStore()
  return (
    <header className={theme}>
      {user?.name}
      <button onClick={toggleTheme}>Toggle Theme</button>
    </header>
  )
}
```

## Detailed patterns and worked examples

詳細的 pattern 文件放在 `references/details.md`。上面這層導覽不夠用的時候，再去讀那個檔案。

## Best Practices

### Do's

- **狀態就近放（colocate）** - 狀態盡量放在最靠近使用它的地方
- **用 selector** - 用選擇性訂閱避免不必要的 re-render
- **資料正規化** - 把巢狀結構攤平，更新起來比較容易
- **全部都加型別** - 完整的 TypeScript 涵蓋可以預防 runtime 錯誤
- **關注點分離** - 伺服器狀態（React Query）和 client 狀態（Zustand）分開

### Don'ts

- **不要過度全域化** - 不是所有東西都要放進全域狀態
- **不要重複存伺服器狀態** - 交給 React Query 管
- **不要直接 mutate** - 一律用 immutable 的方式更新
- **不要存衍生資料** - 要用的時候再算
- **不要混用不同典範** - 每個類別選一個主要方案

## Migration Guides

### From Legacy Redux to RTK

```typescript
// Before (legacy Redux)
const ADD_TODO = "ADD_TODO";
const addTodo = (text) => ({ type: ADD_TODO, payload: text });
function todosReducer(state = [], action) {
  switch (action.type) {
    case ADD_TODO:
      return [...state, { text: action.payload, completed: false }];
    default:
      return state;
  }
}

// After (Redux Toolkit)
const todosSlice = createSlice({
  name: "todos",
  initialState: [],
  reducers: {
    addTodo: (state, action: PayloadAction<string>) => {
      // Immer allows "mutations"
      state.push({ text: action.payload, completed: false });
    },
  },
});
```
