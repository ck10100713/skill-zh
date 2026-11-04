---
name: task-coordination-strategies
description: 拆解複雜任務、設計依賴關係圖，並透過適當的任務描述和工作量平衡來協調多 agent 的工作。在為 agent 團隊拆解工作、管理任務依賴或監控團隊進度時使用這個 skill。
version: 1.0.2
---

# Task Coordination Strategies

把複雜任務拆解成可平行處理的單元、設計依賴關係圖、寫出有效的任務描述，並監控 agent 團隊之間的工作量的策略。

## When to Use This Skill

- 為了平行執行而拆解複雜任務
- 設計任務之間的依賴關係（blockedBy/blocks）
- 撰寫附有明確驗收標準的任務描述
- 監控並重新平衡隊友之間的工作量
- 找出多任務工作流程中的關鍵路徑

## Task Decomposition Strategies

### By Layer

依架構分層來切分工作：

- 前端元件
- 後端 API endpoint
- 資料庫 migration/model
- 測試套件

**最適合**：全端功能、垂直切片

### By Component

依功能元件來切分工作：

- 認證模組
- 使用者個人檔案模組
- 通知模組

**最適合**：Microservice、模組化架構

### By Concern

依橫切關注點來切分工作：

- 安全 review
- 效能 review
- 架構 review

**最適合**：Code review、稽核

### By File Ownership

依檔案/目錄的邊界來切分工作：

- `src/components/` — Implementer 1
- `src/api/` — Implementer 2
- `src/utils/` — Implementer 3

**最適合**：平行實作、避免衝突

## Dependency Graph Design

### Principles

1. **讓鏈的深度最小化** — 偏好寬而淺的圖，不要深的鏈
2. **找出關鍵路徑** — 最長的那條鏈決定了最短的完成時間
3. **少用 blockedBy** — 只加真正必要的依賴
4. **避免循環依賴** — Task A 擋住 B、B 又擋住 A，就是死結（deadlock）

### Patterns

**Independent（最佳的平行度）**：

```
Task A ─┐
Task B ─┼─→ Integration
Task C ─┘
```

**Sequential（必要的依賴）**：

```
Task A → Task B → Task C
```

**Diamond（混合）**：

```
        ┌→ Task B ─┐
Task A ─┤          ├→ Task D
        └→ Task C ─┘
```

### Using blockedBy/blocks

```
TaskCreate: { subject: "Build API endpoints" }         → Task #1
TaskCreate: { subject: "Build frontend components" }    → Task #2
TaskCreate: { subject: "Integration testing" }          → Task #3
TaskUpdate: { taskId: "3", addBlockedBy: ["1", "2"] }  → #3 waits for #1 and #2
```

## Task Description Best Practices

每個任務都應該包含：

1. **Objective** — 需要完成什麼（1-2 句話）
2. **Owned Files** — 這位隊友可以修改的檔案/目錄的明確清單
3. **Requirements** — 預期的具體交付物或行為
4. **Interface Contracts** — 這份工作跟其他隊友的工作如何銜接
5. **Acceptance Criteria** — 如何驗證任務有正確完成
6. **Scope Boundaries** — 明確不在範圍內的東西

### Template

```
## Objective
Build the user authentication API endpoints.

## Owned Files
- src/api/auth.ts
- src/api/middleware/auth-middleware.ts
- src/types/auth.ts (shared — read only, do not modify)

## Requirements
- POST /api/login — accepts email/password, returns JWT
- POST /api/register — creates new user, returns JWT
- GET /api/me — returns current user profile (requires auth)

## Interface Contract
- Import User type from src/types/auth.ts (owned by implementer-1)
- Export AuthResponse type for frontend consumption

## Acceptance Criteria
- All endpoints return proper HTTP status codes
- JWT tokens expire after 24 hours
- Passwords are hashed with bcrypt

## Out of Scope
- OAuth/social login
- Password reset flow
- Rate limiting
```

## Workload Monitoring

### Indicators of Imbalance

| Signal                     | Meaning             | Action                      |
| -------------------------- | ------------------- | --------------------------- |
| 隊友閒置，其他人很忙 | 分配不均 | 重新分配待處理的任務      |
| 隊友卡在某個任務上 | 可能有阻礙    | 關心一下，主動提供協助        |
| 所有任務都被擋住          | 依賴問題    | 先解決關鍵路徑 |
| 某位隊友的量是其他人的 3 倍 | 負荷過重          | 拆分任務或重新分配     |

### Rebalancing Steps

1. 呼叫 `TaskList` 評估目前的狀態
2. 找出閒置或負荷過重的隊友
3. 用 `TaskUpdate` 重新分配任務
4. 用 `SendMessage` 通知受影響的隊友
5. 監看吞吐量是否改善
