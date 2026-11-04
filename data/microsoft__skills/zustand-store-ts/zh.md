---
name: zustand-store-ts
description: 用 TypeScript 建立 Zustand store，搭配 subscribeWithSelector middleware，並正確分開 state 與 action。當你在做 React 狀態管理、建立全域 store，或用 Zustand 實作響應式狀態模式時使用。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# Zustand Store

依照既定模式建立 Zustand store，搭配正確的 TypeScript 型別和 middleware。

## 快速開始

複製 [assets/template.ts](assets/template.ts) 的範本，並替換佔位符：
- `{{StoreName}}` → PascalCase 的 store 名稱（例如 `Project`）
- `{{description}}` → JSDoc 用的簡短說明

## 一律使用 subscribeWithSelector

```typescript
import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';

export const useMyStore = create<MyStore>()(
  subscribeWithSelector((set, get) => ({
    // state and actions
  }))
);
```

## 分開 State 與 Action

```typescript
export interface MyState {
  items: Item[];
  isLoading: boolean;
}

export interface MyActions {
  addItem: (item: Item) => void;
  loadItems: () => Promise<void>;
}

export type MyStore = MyState & MyActions;
```

## 使用個別的 Selector

```typescript
// Good - only re-renders when `items` changes
const items = useMyStore((state) => state.items);

// Avoid - re-renders on any state change
const { items, isLoading } = useMyStore();
```

## 在 React 外面訂閱

```typescript
useMyStore.subscribe(
  (state) => state.selectedId,
  (selectedId) => console.log('Selected:', selectedId)
);
```

## 整合步驟

1. 在 `src/frontend/src/store/` 建立 store
2. 從 `src/frontend/src/store/index.ts` export
3. 在 `src/frontend/src/store/*.test.ts` 加測試
