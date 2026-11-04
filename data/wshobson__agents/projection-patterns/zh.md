---
name: projection-patterns
description: 從 event stream 建立 read model 與 projection。在實作 CQRS 的讀取端、建立 materialized view，或優化 event sourcing 系統的查詢效能時使用。
---

# Projection Patterns

為 event sourcing 系統建立 projection 與 read model 的完整指南。

## When to Use This Skill

- 建立 CQRS read model
- 從事件建立 materialized view
- 優化查詢效能
- 實作即時 dashboard
- 從事件建立搜尋索引
- 跨 stream 彙整資料

## Core Concepts

### 1. Projection Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Event Store │────►│ Projector   │────►│ Read Model  │
│             │     │             │     │ (Database)  │
│ ┌─────────┐ │     │ ┌─────────┐ │     │ ┌─────────┐ │
│ │ Events  │ │     │ │ Handler │ │     │ │ Tables  │ │
│ └─────────┘ │     │ │ Logic   │ │     │ │ Views   │ │
│             │     │ └─────────┘ │     │ │ Cache   │ │
└─────────────┘     └─────────────┘     └─────────────┘
```

### 2. Projection Types

| Type           | Description                 | Use Case               |
| -------------- | --------------------------- | ---------------------- |
| **Live**       | 從訂閱即時處理 | 查詢目前狀態  |
| **Catchup**    | 處理歷史事件   | 重建 read model |
| **Persistent** | 儲存 checkpoint           | 重啟後繼續   |
| **Inline**     | 跟寫入在同一個交易   | 強一致性     |

## Templates and detailed worked examples

完整的範本庫與詳細的範例放在 `references/details.md`。需要具體範本時，再去讀那個檔案。

## Best Practices

### Do's

- **讓 projection 具冪等性** - 重播時是安全的
- **使用交易** - 用於多表更新
- **儲存 checkpoint** - 失敗後可以繼續
- **監控延遲** - 對 projection 的延遲設警報
- **規劃重建** - 設計時就考慮能重新建構

### Don'ts

- **不要讓 projection 互相耦合** - 每一個都是獨立的
- **不要跳過錯誤處理** - 失敗時要記錄並發出警報
- **不要忽略順序** - 事件必須依序處理
- **不要過度正規化** - 依查詢模式反正規化
