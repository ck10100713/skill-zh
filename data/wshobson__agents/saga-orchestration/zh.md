---
name: saga-orchestration
description: 為分散式交易和跨 aggregate 的工作流程實作 saga 模式。在 2PC 用不了的 microservice 之間實作分散式交易、替橫跨庫存/付款/出貨服務的失敗訂單流程設計補償動作、為必須原子性地回滾飯店/航班/租車預訂的旅遊訂位系統建構事件驅動的 saga coordinator，或除錯正式環境中補償步驟永遠沒完成而卡住的 saga 狀態時使用。
---

# Saga Orchestration

不靠兩階段提交（two-phase commit），來管理分散式交易和長時間執行的商業流程的模式。

## Inputs and Outputs

**你要提供：**
- 服務邊界和歸屬（哪個服務負責哪個步驟）
- 交易需求（哪些步驟必須是原子性的，哪些可以最終一致）
- 每個步驟的失敗模式（暫時性 vs. 永久性、重試策略）
- 每個步驟的 SLA 需求（用來決定 timeout 設定）
- 現有的事件/訊息基礎設施（Kafka、RabbitMQ、SQS 等）

**這個 skill 會產出：**
- Saga 定義，包含有順序的步驟、動作指令和補償指令
- 針對你選的模式實作的 orchestrator 或 choreography
- 每個參與服務的補償邏輯（idempotent、一定會成功）
- 每個步驟都有各自期限的 timeout 設定
- 監控設定：狀態機指標、卡住的 saga 偵測、DLQ 復原

---

## When to Use This Skill

- 不用分散式鎖來協調跨多個服務的交易
- 為部分失敗實作補償交易
- 管理長時間執行的商業工作流程（幾分鐘到幾小時）
- 處理需要原子性的分散式系統中的失敗
- 建構訂單履行、審批或訂位流程
- 用非同步補償取代脆弱的兩階段提交

---

## Detailed section: Core Concepts

已搬到 `references/details.md`。

## Detailed section: Templates

已搬到 `references/details.md`。

## Best Practices

### Do's

- **讓每個步驟都 idempotent** — broker 重連時，指令可能被重播
- **仔細設計補償動作** — 它們是最關鍵的程式碼路徑
- **用 correlation ID** — `saga_id` 必須流經每個事件和 log
- **實作每個步驟自己的 timeout** — 絕對不要無限期等待參與者回覆
- **記錄狀態轉換** — 每次變動都要記錄 `saga_id`、`step_name`、`old_state → new_state`
- **明確測試補償路徑** — 在整合測試裡，於每個步驟索引都注入失敗

### Don'ts

- **不要假設會立刻完成** — Saga 是非同步的，可能要好幾分鐘
- **不要跳過補償的測試** — 回滾路徑是最難做對的
- **不要把服務直接耦合在一起** — 用非同步訊息，saga 步驟裡絕對不要有同步呼叫
- **不要忽略部分失敗** — 只執行了一部分的步驟，仍然需要補償
- **不要用全域 timeout** — 每個步驟的延遲特性都不一樣

---

## Troubleshooting

### Saga stuck in COMPENSATING state

Saga 進入補償階段，卻一直到不了 FAILED。這代表某個補償 handler 丟出了沒處理的 exception，從來沒發布 `SagaCompensationCompleted`。要在補償的 consumer 加上 dead-letter queue（DLQ）處理，並確保每個補償動作都會發布結果事件，就算底層操作已經被回滾過了也一樣。

```python
async def handle_release_reservation(self, command: Dict):
    try:
        await self.release_reservation(command["original_result"]["reservation_id"])
    except ReservationNotFoundError:
        pass  # Already released — treat as success
    # Always publish completion, regardless of outcome
    await self.event_publisher.publish("SagaCompensationCompleted", {
        "saga_id": command["saga_id"],
        "step_name": "reserve_inventory"
    })
```

### Duplicate saga executions on restart

如果你的 orchestrator 服務在 saga 進行到一半時重啟，它可能會重播事件，並重新執行已經完成的步驟。每個步驟的動作都要用 idempotency key 把關，見上面的 **Template 3**。

### Choreography saga losing events

在以 choreography 為基礎的 saga 裡，下游服務如果在事件發布時離線，可能會漏掉那個事件。要用持久化的 message broker（有複寫的 Kafka、有持久化的 RabbitMQ），並把目前的 saga 狀態存進專用的 `saga_log` 資料表，這樣才能從最後一個已知正常的步驟重播。

### Timeout firing before a slow-but-valid step completes

像 `create_shipment` 這種步驟，在尖峰時可能要花到 15 分鐘，但你的全域 timeout 是 5 分鐘，結果造成不該發生的補償。要讓 timeout 可以依步驟類型個別設定，`TimeoutSagaOrchestrator` 的實作和 `STEP_TIMEOUTS` dict 的寫法，請看 `references/advanced-patterns.md`。

### Compensation order not matching execution order

兩個步驟都已完成、之後才偵測到失敗時，補償必須嚴格按照相反的順序執行，否則資料會留在不一致的狀態。確認 `_compensate()` 是從 `current_step - 1` 往下迭代到 `0`，並加一個整合測試，刻意在每個步驟索引製造失敗，確認回滾的順序正確。

---

## Advanced Patterns

`references/` 目錄裡有正式環境等級的實作，大多數 saga 用不到：

- **`references/advanced-patterns.md`** — 完整的 `SagaOrchestrator` 抽象 base class、有各步驟期限的 `TimeoutSagaOrchestrator`、詳細的銀行轉帳補償交易鏈、Prometheus instrumentation、卡住 saga 的 PromQL 警報，以及 DLQ 復原 worker。

---

## Related Skills

- `cqrs-implementation` — 把 saga 跟 CQRS 搭配，在每個步驟完成後更新 read model
- `event-store-design` — 把 saga 事件存進 event store，取得完整的稽核軌跡和重播能力
- `workflow-orchestration-patterns` — 建立在 saga 概念之上的更高階 workflow 引擎（Temporal、Conductor）
