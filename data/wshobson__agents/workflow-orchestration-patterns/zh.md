---
name: workflow-orchestration-patterns
description: 用 Temporal 為分散式系統設計 durable workflow。涵蓋 workflow 與 activity 的分離、saga 模式、狀態管理和決定性（determinism）限制。建立長時間執行的流程、分散式交易，或微服務編排時使用。
---

# Workflow Orchestration Patterns

精通用 Temporal 做 workflow 編排的架構，涵蓋基本設計決策、韌性模式，以及打造可靠分散式系統的最佳實務。

## When to Use Workflow Orchestration

### Ideal Use Cases (Source: docs.temporal.io)

- 橫跨機器/服務/資料庫的**多步驟流程**
- 需要全有或全無（all-or-nothing）語意的**分散式交易**
- 有自動狀態持久化、可長時間執行（數小時到數年）的 **workflow**
- 必須從上一個成功步驟接續的**失敗復原**
- **商業流程**：訂位、訂單、行銷活動、簽核
- **實體生命週期管理**：庫存追蹤、帳號管理、購物車流程
- **基礎設施自動化**：CI/CD 流水線、資源配置、部署
- 需要逾時和升級處理的 **human-in-the-loop** 系統

### When NOT to Use

- 簡單的 CRUD 操作（直接呼叫 API）
- 純資料處理流水線（用 Airflow、批次處理）
- 無狀態的 request/response（用一般 API）
- 即時串流（用 Kafka、事件處理器）

## Detailed patterns and worked examples

詳細的模式說明放在 `references/details.md`。上面的導覽層不夠用的時候，再去讀那個檔案。

## Best Practices

### Workflow Design

1. **Keep workflows focused** - 每個 workflow 只負責單一職責
2. **Small workflows** - 為了可擴展性，使用 child workflow
3. **Clear boundaries** - Workflow 負責編排，activity 負責執行
4. **Test locally** - 使用時間跳躍的測試環境

### Activity Design

1. **Idempotent operations** - 可以安全地重試
2. **Short-lived** - 幾秒到幾分鐘，不要到幾小時
3. **Timeout configuration** - 一定要設逾時
4. **Heartbeat for long tasks** - 回報進度
5. **Error handling** - 區分可重試與不可重試的錯誤

### Common Pitfalls

**Workflow 違規**：

- 用 `datetime.now()` 而不是 `workflow.now()`
- 在 workflow 程式碼裡用 threading 或 async 操作
- 直接從 workflow 呼叫外部 API
- Workflow 中有非決定性的邏輯

**Activity 常見錯誤**：

- 非 idempotent 的操作（無法處理重試）
- 缺少逾時（activity 會永遠跑下去）
- 沒有做錯誤分類（連驗證錯誤也重試）
- 忽略 payload 上限（每個參數 2MB）

### Operational Considerations

**Monitoring**：

- Workflow 執行時間
- Activity 失敗率
- 重試次數與 backoff
- 待處理的 workflow 數量

**Scalability**：

- 靠 worker 做水平擴展
- Task queue 分區
- 拆解成 child workflow
- 適當時對 activity 做批次處理

## Additional Resources

**官方文件**：

- Temporal Core Concepts: docs.temporal.io/workflows
- Workflow Patterns: docs.temporal.io/evaluate/use-cases-design-patterns
- Best Practices: docs.temporal.io/develop/best-practices
- Saga Pattern: temporal.io/blog/saga-pattern-made-easy

**關鍵原則**：

1. Workflow = 編排，Activity = 外部呼叫
2. Workflow 的決定性沒有商量的餘地
3. Activity 的 idempotency 至關重要
4. 狀態保存是自動的
5. 針對失敗和復原來設計
