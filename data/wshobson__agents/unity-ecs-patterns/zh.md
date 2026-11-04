---
name: unity-ecs-patterns
description: 精通 Unity ECS（Entity Component System），搭配 DOTS、Jobs 和 Burst 做高效能遊戲開發。開發資料導向（data-oriented）遊戲、最佳化效能，或處理大量 entity 時使用。
---

# Unity ECS Patterns

Unity 資料導向技術堆疊（DOTS）的 production 模式，包含 Entity Component System、Job System 和 Burst Compiler。

## When to Use This Skill

- 開發高效能的 Unity 遊戲
- 有效率地管理數千個 entity
- 實作資料導向的遊戲系統
- 最佳化吃 CPU 的遊戲邏輯
- 把 OOP 的遊戲程式碼轉成 ECS
- 用 Jobs 和 Burst 做平行化

## Core Concepts

### 1. ECS vs OOP

| Aspect      | Traditional OOP   | ECS/DOTS        |
| ----------- | ----------------- | --------------- |
| Data layout | 物件導向   | 資料導向   |
| Memory      | 分散         | 連續      |
| Processing  | 逐個物件        | 批次處理         |
| Scaling     | 數量一多就變差   | 線性擴展  |
| Best for    | 複雜行為 | 大量模擬 |

### 2. DOTS Components

```
Entity: Lightweight ID (no data)
Component: Pure data (no behavior)
System: Logic that processes components
World: Container for entities
Archetype: Unique combination of components
Chunk: Memory block for same-archetype entities
```

## Detailed patterns and worked examples

詳細的模式說明放在 `references/details.md`。上面的導覽層不夠用的時候，再去讀那個檔案。

## Best Practices

### Do's

- **Use ISystem over SystemBase** - 效能比較好
- **Burst compile everything** - 速度大幅提升
- **Batch structural changes** - 用 ECB
- **Profile with Profiler** - 找出瓶頸
- **Use Aspects** - 讓 component 分組更乾淨

### Don'ts

- **Don't use managed types** - 會讓 Burst 失效
- **Don't structural change in jobs** - 用 ECB
- **Don't over-architect** - 從簡單的開始
- **Don't ignore chunk utilization** - 把相似的 entity 分在一組
- **Don't forget disposal** - Native collection 會 leak
