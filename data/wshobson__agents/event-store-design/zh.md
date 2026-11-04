---
name: event-store-design
description: 設計 event sourcing 應用所需的 event store 完整指南。適用於設計 event sourcing 基礎設施、在不同 event store 技術之間做選擇，或實作自訂 event store 的時候。
---

# Event Store 設計

為 event sourcing 應用設計 event store 的完整指南。

## 什麼時候用這個 Skill

- 設計 event sourcing 基礎設施
- 在不同的 event store 技術之間做選擇
- 實作自訂的 event store
- 最佳化事件的儲存與讀取
- 設定 event store 的 schema
- 規劃 event store 的擴充

## 核心概念

### 1. Event Store 架構

```
┌─────────────────────────────────────────────────────┐
│                    Event Store                       │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │   Stream 1   │  │   Stream 2   │  │   Stream 3   │ │
│  │ (Aggregate)  │  │ (Aggregate)  │  │ (Aggregate)  │ │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤ │
│  │ Event 1     │  │ Event 1     │  │ Event 1     │ │
│  │ Event 2     │  │ Event 2     │  │ Event 2     │ │
│  │ Event 3     │  │ ...         │  │ Event 3     │ │
│  │ ...         │  │             │  │ Event 4     │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────┤
│  Global Position: 1 → 2 → 3 → 4 → 5 → 6 → ...     │
└─────────────────────────────────────────────────────┘
```

### 2. Event Store 需求

| 需求              | 說明                               |
| ----------------- | ---------------------------------- |
| **Append-only**   | 事件不可變，只能附加               |
| **有順序**        | 每個 stream 以及全域都有順序       |
| **有版本**        | 樂觀並行控制                       |
| **訂閱**          | 即時事件通知                       |
| **Idempotent**    | 安全地處理重複寫入                 |

## 技術比較

| 技術             | 最適合                    | 限制                             |
| ---------------- | ------------------------- | -------------------------------- |
| **EventStoreDB** | 純 event sourcing         | 用途單一                         |
| **PostgreSQL**   | 已有 Postgres 技術棧      | 需要手動實作                     |
| **Kafka**        | 高吞吐量的串流            | 不適合以 stream 為單位的查詢     |
| **DynamoDB**     | Serverless、AWS 原生      | 查詢能力有限                     |
| **Marten**       | .NET 生態系               | 僅限 .NET                        |

## 範本與詳細實作範例

完整的範本庫和詳細實作範例放在 `references/details.md`，需要具體範本的時候去讀那份檔案。

## 最佳實務

### 該做的

- **stream ID 要包含 aggregate 類型**：`Order-{uuid}`
- **包含 correlation/causation ID**：方便追蹤
- **從第一天就為事件加版本**：為 schema 演進做準備
- **實作 idempotency**：用事件 ID 做去重
- **適當建立索引**：依你的查詢模式

### 不該做的

- **不要更新或刪除事件**：它們是不可變的事實
- **不要存大型的 payload**：事件要保持精簡
- **不要跳過樂觀並行控制**：它能防止資料毀損
- **不要忽略 backpressure**：要處理消費速度慢的 consumer
