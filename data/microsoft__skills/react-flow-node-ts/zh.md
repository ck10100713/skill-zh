---
name: react-flow-node-ts
description: 建立帶有 TypeScript 型別、handle 並整合 Zustand 的 React Flow node 元件。適用於為 React Flow 畫布建立自訂 node、製作視覺化工作流程編輯器，或實作以 node 為基礎的 UI 元件。
license: MIT
metadata:
  author: Microsoft
  version: "1.0.0"
---

# React Flow Node

依照既有模式建立 React Flow node 元件，包含正確的 TypeScript 型別和 store 整合。

## 快速開始

從 [assets/](assets/) 複製範本，並替換 placeholder：
- `{{NodeName}}` → PascalCase 元件名稱（例如 `VideoNode`）
- `{{nodeType}}` → kebab-case 型別識別字（例如 `video-node`）
- `{{NodeData}}` → Data interface 名稱（例如 `VideoNodeData`）

## 範本

- [assets/template.tsx](assets/template.tsx) - Node 元件
- [assets/types.template.ts](assets/types.template.ts) - TypeScript 型別定義

## Node 元件模式

```tsx
export const MyNode = memo(function MyNode({
  id,
  data,
  selected,
  width,
  height,
}: MyNodeProps) {
  const updateNode = useAppStore((state) => state.updateNode);
  const canvasMode = useAppStore((state) => state.canvasMode);
  
  return (
    <>
      <NodeResizer isVisible={selected && canvasMode === 'editing'} />
      <div className="node-container">
        <Handle type="target" position={Position.Top} />
        {/* Node content */}
        <Handle type="source" position={Position.Bottom} />
      </div>
    </>
  );
});
```

## 型別定義模式

```typescript
export interface MyNodeData extends Record<string, unknown> {
  title: string;
  description?: string;
}

export type MyNode = Node<MyNodeData, 'my-node'>;
```

## 整合步驟

1. 把型別加到 `src/frontend/src/types/index.ts`
2. 在 `src/frontend/src/components/nodes/` 建立元件
3. 從 `src/frontend/src/components/nodes/index.ts` export
4. 在 `src/frontend/src/store/app-store.ts` 加上預設值
5. 在畫布的 `nodeTypes` 註冊
6. 加到 AddBlockMenu 和 ConnectMenu
