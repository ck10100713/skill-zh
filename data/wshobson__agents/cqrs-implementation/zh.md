---
name: cqrs-implementation
description: 為可擴充的架構實作 Command Query Responsibility Segregation（CQRS）。在分離讀取與寫入模型、最佳化查詢效能，或建構 event-sourced 系統時使用。
---

# CQRS 實作

實作 CQRS（Command Query Responsibility Segregation）模式的完整指南。

## 何時使用這個 Skill

- 分離讀取與寫入的關注點
- 讓讀取獨立於寫入來擴充
- 建構 event-sourced 系統
- 最佳化複雜的查詢情境
- 需要不同的讀取/寫入資料模型
- 高效能的報表需求

## 核心概念

### 1. CQRS 架構

```
                    ┌─────────────┐
                    │   Client    │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
       ┌─────────────┐          ┌─────────────┐
       │  Commands   │          │   Queries   │
       │    API      │          │    API      │
       └──────┬──────┘          └──────┬──────┘
              │                         │
              ▼                         ▼
       ┌─────────────┐          ┌─────────────┐
       │  Command    │          │   Query     │
       │  Handlers   │          │  Handlers   │
       └──────┬──────┘          └──────┬──────┘
              │                         │
              ▼                         ▼
       ┌─────────────┐          ┌─────────────┐
       │   Write     │─────────►│    Read     │
       │   Model     │  Events  │   Model     │
       └─────────────┘          └─────────────┘
```

### 2. 關鍵元件

| 元件           | 職責                  |
| ------------------- | ------------------------------- |
| **Command**         | 改變狀態的意圖          |
| **Command Handler** | 驗證並執行 command |
| **Event**           | 狀態變化的紀錄            |
| **Query**           | 對資料的請求                |
| **Query Handler**   | 從讀取模型取得資料  |
| **Projector**       | 根據 event 更新讀取模型  |

## 範本與詳細的實作範例

完整的範本庫和詳細的實作範例放在 `references/details.md`。需要具體的範本時，讀那個檔案。

## 最佳實務

### 該做的

- **分離 command 和 query 模型** - 需求不同
- **使用最終一致性** - 接受傳播的延遲
- **在 command handler 裡驗證** - 在狀態改變之前
- **讀取模型做反正規化** - 針對查詢最佳化
- **替 event 加版本** - 為了 schema 演進

### 不該做的

- **不要在 command 裡做查詢** - 只用來寫入
- **不要讓讀取/寫入的 schema 耦合** - 各自獨立演進
- **不要過度設計** - 從簡單開始
- **不要忽略一致性的 SLA** - 定義可接受的延遲
