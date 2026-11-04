---
name: microservices-patterns
description: 設計 microservices 架構，涵蓋服務邊界、事件驅動通訊與韌性模式。在建構分散式系統、拆解 monolith 或實作 microservices 時使用。
---

# Microservices Patterns

精通 microservices 架構模式，包含服務邊界、服務間通訊、資料管理與韌性模式，用來建構分散式系統。

## When to Use This Skill

- 把 monolith 拆解成 microservices
- 設計服務邊界與契約
- 實作服務間通訊
- 管理分散式資料與交易
- 建構有韌性的分散式系統
- 實作 service discovery 與 load balancing
- 設計事件驅動架構

## Core Concepts

### 1. Service Decomposition Strategies

**依業務能力拆分**

- 圍繞業務功能來組織服務
- 每個服務擁有自己的領域
- 例：OrderService、PaymentService、InventoryService

**依子領域拆分（DDD）**

- 核心領域與支援子領域
- Bounded context 對應到服務
- 擁有權與責任清楚

**Strangler Fig Pattern**

- 逐步從 monolith 抽出功能
- 新功能直接做成 microservices
- 用 proxy 把請求導向舊系統或新系統

### 2. Communication Patterns

**同步（Request/Response）**

- REST API
- gRPC
- GraphQL

**非同步（Events/Messages）**

- Event streaming（Kafka）
- Message queue（RabbitMQ、SQS）
- Pub/Sub 模式

### 3. Data Management

**每個服務一個資料庫**

- 每個服務擁有自己的資料
- 不共用資料庫
- 鬆耦合

**Saga Pattern**

- 分散式交易
- 補償動作
- 最終一致性

### 4. Resilience Patterns

**Circuit Breaker**

- 重複出錯時快速失敗
- 避免連鎖失敗

**Retry with Backoff**

- 處理暫時性錯誤
- 指數退避

**Bulkhead**

- 隔離資源
- 限制失敗的影響範圍

## Detailed patterns and worked examples

詳細的模式文件放在 `references/details.md`。上面的導覽層不夠用時，再去讀那個檔案。

