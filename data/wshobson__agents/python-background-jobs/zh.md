---
name: python-background-jobs
description: Python 背景工作的模式，包含 task queue、worker 與事件驅動架構。在實作非同步任務處理、job queue、長時間運行的操作，或把工作從 request/response 週期中解耦時使用。
---

# Python Background Jobs & Task Queues

把長時間運行或不可靠的工作，從 request/response 週期中解耦。立刻回覆使用者，由背景 worker 非同步處理繁重的工作。

## When to Use This Skill

- 處理超過幾秒鐘的任務
- 寄送 email、通知或 webhook
- 產生報表或匯出資料
- 處理上傳或媒體轉換
- 整合不可靠的外部服務
- 建構事件驅動架構

## Core Concepts

### 1. Task Queue Pattern

API 接受請求、把工作放進佇列，並立刻回傳一個 job ID。Worker 非同步處理這些工作。

### 2. Idempotency

任務失敗時可能會被重試。設計時要能安全地重複執行。

### 3. Job State Machine

工作會依序轉換狀態：pending → running → succeeded/failed。

### 4. At-Least-Once Delivery

大多數佇列保證至少送達一次。你的程式碼必須能處理重複。

## Quick Start

這個 skill 的範例使用 Celery，它是廣泛採用的 task queue。RQ、Dramatiq 這類替代方案，以及雲端原生的解決方案（AWS SQS、GCP Tasks）也同樣是有效的選擇。

```python
from celery import Celery

app = Celery("tasks", broker="redis://localhost:6379")

@app.task
def send_email(to: str, subject: str, body: str) -> None:
    # This runs in a background worker
    email_client.send(to, subject, body)

# In your API handler
send_email.delay("user@example.com", "Welcome!", "Thanks for signing up")
```

## Fundamental Patterns

### Pattern 1: Return Job ID Immediately

對超過幾秒鐘的操作，回傳 job ID 並非同步處理。

```python
from uuid import uuid4
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"

@dataclass
class Job:
    id: str
    status: JobStatus
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: dict | None = None
    error: str | None = None

# API endpoint
async def start_export(request: ExportRequest) -> JobResponse:
    """Start export job and return job ID."""
    job_id = str(uuid4())

    # Persist job record
    await jobs_repo.create(Job(
        id=job_id,
        status=JobStatus.PENDING,
        created_at=datetime.utcnow(),
    ))

    # Enqueue task for background processing
    await task_queue.enqueue(
        "export_data",
        job_id=job_id,
        params=request.model_dump(),
    )

    # Return immediately with job ID
    return JobResponse(
        job_id=job_id,
        status="pending",
        poll_url=f"/jobs/{job_id}",
    )
```

### Pattern 2: Celery Task Configuration

為 Celery 任務設定適當的 retry 與 timeout。

```python
from celery import Celery

app = Celery("tasks", broker="redis://localhost:6379")

# Global configuration
app.conf.update(
    task_time_limit=3600,          # Hard limit: 1 hour
    task_soft_time_limit=3000,      # Soft limit: 50 minutes
    task_acks_late=True,            # Acknowledge after completion
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,   # Don't prefetch too many tasks
)

@app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(ConnectionError, TimeoutError),
)
def process_payment(self, payment_id: str) -> dict:
    """Process payment with automatic retry on transient errors."""
    try:
        result = payment_gateway.charge(payment_id)
        return {"status": "success", "transaction_id": result.id}
    except PaymentDeclinedError as e:
        # Don't retry permanent failures
        return {"status": "declined", "reason": str(e)}
    except TransientError as e:
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries * 60)
```

### Pattern 3: Make Tasks Idempotent

Worker 在當機或逾時時可能會重試。設計時要能安全地重複執行。

```python
@app.task(bind=True)
def process_order(self, order_id: str) -> None:
    """Process order idempotently."""
    order = orders_repo.get(order_id)

    # Already processed? Return early
    if order.status == OrderStatus.COMPLETED:
        logger.info("Order already processed", order_id=order_id)
        return

    # Already in progress? Check if we should continue
    if order.status == OrderStatus.PROCESSING:
        # Use idempotency key to avoid double-charging
        pass

    # Process with idempotency key
    result = payment_provider.charge(
        amount=order.total,
        idempotency_key=f"order-{order_id}",  # Critical!
    )

    orders_repo.update(order_id, status=OrderStatus.COMPLETED)
```

**冪等性策略：**

1. **先檢查再寫入**：動作之前先驗證狀態
2. **Idempotency key**：對外部服務使用唯一的 token
3. **Upsert 模式**：`INSERT ... ON CONFLICT UPDATE`
4. **去重視窗**：追蹤已處理的 ID，保留 N 小時

### Pattern 4: Job State Management

把 job 的狀態轉換持久化，方便查看與除錯。

```python
class JobRepository:
    """Repository for managing job state."""

    async def create(self, job: Job) -> Job:
        """Create new job record."""
        await self._db.execute(
            """INSERT INTO jobs (id, status, created_at)
               VALUES ($1, $2, $3)""",
            job.id, job.status.value, job.created_at,
        )
        return job

    async def update_status(
        self,
        job_id: str,
        status: JobStatus,
        **fields,
    ) -> None:
        """Update job status with timestamp."""
        updates = {"status": status.value, **fields}

        if status == JobStatus.RUNNING:
            updates["started_at"] = datetime.utcnow()
        elif status in (JobStatus.SUCCEEDED, JobStatus.FAILED):
            updates["completed_at"] = datetime.utcnow()

        await self._db.execute(
            "UPDATE jobs SET status = $1, ... WHERE id = $2",
            updates, job_id,
        )

        logger.info(
            "Job status updated",
            job_id=job_id,
            status=status.value,
        )
```

## Detailed worked examples and patterns

詳細的章節（從 `## Advanced Patterns` 開始）放在 `references/details.md`。上面的導覽摘要不夠用時，再去讀那個檔案。

## Best Practices Summary

1. **立刻回覆** - 不要為了長時間的操作而阻塞請求
2. **持久化 job 狀態** - 支援狀態輪詢與除錯
3. **讓任務具冪等性** - 任何失敗都能安全重試
4. **使用 idempotency key** - 用於呼叫外部服務
5. **設定 timeout** - soft 和 hard 兩種上限都要設
6. **實作 DLQ** - 收容永久失敗的任務
7. **記錄狀態轉換** - 追蹤 job 狀態的變化
8. **適當地重試** - 暫時性錯誤用指數退避
9. **不要重試永久性的失敗** - 驗證錯誤、無效的憑證
10. **監控佇列深度** - 積壓增加時發出警報
