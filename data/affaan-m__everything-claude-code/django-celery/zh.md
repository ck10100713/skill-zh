---
name: django-celery
description: Django + Celery 非同步任務模式：設定、任務設計、beat 排程、重試、canvas 工作流程、監控和測試。當要為 Django 應用程式加入背景工作、排程任務或非同步處理時使用。
metadata:
  origin: ECC
---

# Django + Celery 非同步任務模式

在 Django 中使用 Celery 搭配 Redis 或 RabbitMQ 處理背景任務，適合 production 等級的模式。

## 何時啟用

- 為 Django 應用程式加入背景工作或非同步處理
- 實作週期性/排程任務
- 把慢的操作（email、產生 PDF、API 呼叫）從請求週期中卸載出去
- 設定 Celery Beat 做類似 cron 的排程
- 除錯任務失敗、重試或佇列積壓
- 為 Celery 任務撰寫測試

## 專案設定

### 安裝

```bash
pip install 'celery[redis]' django-celery-results django-celery-beat
```

### `celery.py`：應用程式進入點

```python
# config/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('myproject')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()  # Discovers tasks.py in each INSTALLED_APP

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
```

```python
# config/__init__.py
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### Django 設定

```python
# config/settings/base.py

# Broker (Redis recommended for production)
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='django-db')

# Serialization
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Task behavior
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60        # Hard limit: 30 min
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60   # Soft limit: sends SoftTimeLimitExceeded
CELERY_WORKER_PREFETCH_MULTIPLIER = 1   # Prevent worker hoarding long tasks
CELERY_TASK_ACKS_LATE = True            # Re-queue on worker crash

# Result persistence
CELERY_RESULT_EXPIRES = 60 * 60 * 24   # Keep results 24 hours

# Beat scheduler (for periodic tasks)
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Installed apps
INSTALLED_APPS += [
    'django_celery_results',
    'django_celery_beat',
]
```

### 執行 Worker

```bash
# Start worker (development)
celery -A config worker --loglevel=info

# Start beat scheduler (periodic tasks)
celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# Combined worker + beat (dev only, never production)
celery -A config worker --beat --loglevel=info

# Production: multiple workers with concurrency
celery -A config worker --loglevel=warning --concurrency=4 -Q default,high_priority
```

## 任務設計模式

### 基本任務

```python
# apps/notifications/tasks.py
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(name='notifications.send_welcome_email')
def send_welcome_email(user_id: int) -> None:
    """Send welcome email to newly registered user."""
    from apps.users.models import User
    from apps.notifications.services import EmailService

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning('send_welcome_email: user %s not found', user_id)
        return  # Idempotent — do not raise, task already impossible to complete

    EmailService.send_welcome(user)
    logger.info('Welcome email sent to user %s', user_id)
```

### 可重試的任務

```python
@shared_task(
    bind=True,
    name='integrations.sync_to_crm',
    max_retries=5,
    default_retry_delay=60,       # seconds before first retry
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,           # exponential backoff
    retry_backoff_max=600,        # cap at 10 minutes
    retry_jitter=True,            # randomise to avoid thundering herd
)
def sync_contact_to_crm(self, contact_id: int) -> dict:
    """Sync contact to external CRM with retry on transient failures."""
    from apps.crm.services import CRMClient

    try:
        result = CRMClient().sync(contact_id)
        return result
    except CRMClient.RateLimitError as exc:
        # Specific retry delay from response header
        raise self.retry(exc=exc, countdown=int(exc.retry_after))
```

### 冪等任務模式

把任務設計成用相同的輸入重複執行也安全：

```python
@shared_task(name='orders.mark_shipped')
def mark_order_shipped(order_id: int, tracking_number: str) -> None:
    """Mark order as shipped — safe to run multiple times."""
    from apps.orders.models import Order

    updated = Order.objects.filter(
        pk=order_id,
        status=Order.Status.PROCESSING,    # Guard: only update if not already shipped
    ).update(
        status=Order.Status.SHIPPED,
        tracking_number=tracking_number,
    )

    if not updated:
        logger.info('mark_order_shipped: order %s already shipped or not found', order_id)
```

### 帶軟性時間限制的任務

```python
from celery.exceptions import SoftTimeLimitExceeded

@shared_task(
    bind=True,
    name='reports.generate_pdf',
    soft_time_limit=120,
    time_limit=150,
)
def generate_pdf_report(self, report_id: int) -> str:
    """Generate PDF report with graceful timeout handling."""
    from apps.reports.services import PDFGenerator

    try:
        path = PDFGenerator.build(report_id)
        return path
    except SoftTimeLimitExceeded:
        # Clean up partial files before hard kill
        PDFGenerator.cleanup(report_id)
        raise
```

## 呼叫任務

```python
from datetime import timedelta
from django.utils import timezone

# Fire and forget (async)
send_welcome_email.delay(user.pk)

# Schedule in the future
send_reminder.apply_async(args=[user.pk], countdown=3600)  # 1 hour from now
send_reminder.apply_async(args=[user.pk], eta=timezone.now() + timedelta(days=1))

# Apply with queue routing
sync_contact_to_crm.apply_async(args=[contact.pk], queue='high_priority')

# Run synchronously (tests / debugging only)
result = generate_pdf_report.apply(args=[report.pk])
```

## Beat 排程（週期性任務）

### 用程式碼定義的排程

```python
# config/settings/base.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-sessions': {
        'task': 'users.cleanup_expired_sessions',
        'schedule': crontab(hour=2, minute=0),   # 2am daily
    },
    'sync-inventory': {
        'task': 'products.sync_inventory',
        'schedule': 60.0,                         # every 60 seconds
    },
    'weekly-digest': {
        'task': 'notifications.send_weekly_digest',
        'schedule': crontab(day_of_week='monday', hour=8, minute=0),
    },
}
```

### 用資料庫定義的排程（透過 django-celery-beat）

```python
# Manage periodic tasks from Django admin or code
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json

schedule, _ = CrontabSchedule.objects.get_or_create(
    hour='*/6', minute='0',
    timezone='UTC',
)

PeriodicTask.objects.update_or_create(
    name='Sync inventory every 6 hours',
    defaults={
        'crontab': schedule,
        'task': 'products.sync_inventory',
        'args': json.dumps([]),
        'enabled': True,
    }
)
```

## Canvas：串接與分組任務

```python
from celery import chain, group, chord

# Chain: run tasks sequentially, passing results
pipeline = chain(
    fetch_data.s(source_id),
    transform_data.s(),          # receives fetch_data result as first arg
    load_to_warehouse.s(),
)
pipeline.delay()

# Group: run tasks in parallel
parallel = group(
    send_welcome_email.s(user_id)
    for user_id in new_user_ids
)
parallel.delay()

# Chord: parallel tasks + callback when all complete
result = chord(
    group(process_chunk.s(chunk) for chunk in data_chunks),
    aggregate_results.s(),       # called with list of chunk results
)
result.delay()
```

## 錯誤處理與 Dead Letter Queue

```python
# apps/core/tasks.py
from celery.signals import task_failure

@task_failure.connect
def on_task_failure(sender, task_id, exception, args, kwargs, traceback, einfo, **kw):
    """Log all task failures to Sentry / alerting."""
    import sentry_sdk
    with sentry_sdk.new_scope() as scope:
        scope.set_context('celery', {
            'task': sender.name,
            'task_id': task_id,
            'args': args,
            'kwargs': kwargs,
        })
        sentry_sdk.capture_exception(exception)
```

```python
# Route failed tasks to dead-letter queue after max retries
@shared_task(
    bind=True,
    max_retries=3,
    name='payments.charge_card',
)
def charge_card(self, order_id: int) -> None:
    from apps.payments.models import Order, FailedCharge

    try:
        _do_charge(order_id)
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            # Persist to dead-letter table for manual review
            FailedCharge.objects.create(
                order_id=order_id,
                error=str(exc),
                task_id=self.request.id,
            )
            return  # Don't raise — task is permanently failed
        raise self.retry(exc=exc)
```

## 測試 Celery 任務

### 單元測試（不需要 Broker）

```python
# tests/test_tasks.py
import pytest
from unittest.mock import patch, MagicMock
from apps.notifications.tasks import send_welcome_email

class TestSendWelcomeEmail:

    @pytest.mark.django_db
    def test_sends_email_to_existing_user(self, user):
        with patch('apps.notifications.services.EmailService') as mock_email:
            send_welcome_email(user.pk)
            mock_email.send_welcome.assert_called_once_with(user)

    @pytest.mark.django_db
    def test_skips_missing_user_gracefully(self):
        """Should not raise when user is deleted between enqueue and execute."""
        send_welcome_email(99999)  # Non-existent user — must not raise
```

### 用 CELERY_TASK_ALWAYS_EAGER 做整合測試

```python
# config/settings/test.py
CELERY_TASK_ALWAYS_EAGER = True      # Run tasks synchronously in tests
CELERY_TASK_EAGER_PROPAGATES = True  # Re-raise exceptions from tasks

# tests/test_integration.py
@pytest.mark.django_db
def test_registration_triggers_welcome_email(client):
    with patch('apps.notifications.services.EmailService') as mock_email:
        response = client.post('/api/users/', {
            'email': 'new@example.com',
            'password': 'strongpass123',
        })

    assert response.status_code == 201
    mock_email.send_welcome.assert_called_once()
```

### 測試重試

```python
@pytest.mark.django_db
def test_task_retries_on_connection_error():
    with patch('apps.crm.services.CRMClient.sync') as mock_sync:
        mock_sync.side_effect = ConnectionError('timeout')

        with pytest.raises(ConnectionError):
            sync_contact_to_crm.apply(args=[1], throw=True)

        assert mock_sync.call_count == 1  # First attempt only when eager
```

## 監控

```bash
# Inspect active workers and queues
celery -A config inspect active
celery -A config inspect stats
celery -A config inspect reserved

# Check queue lengths (Redis)
redis-cli llen celery

# Flower: web-based real-time monitor
pip install flower
celery -A config flower --port=5555
```

## 反模式

```python
# BAD: Passing model instances — they may be stale by execution time
send_welcome_email.delay(user)        # Never pass ORM objects
send_welcome_email.delay(user.pk)     # Always pass PKs

# BAD: Calling tasks synchronously in production views
result = generate_report.apply()      # Blocks the request thread

# BAD: Non-idempotent task without guards
@shared_task
def charge_and_fulfill(order_id):
    order.charge()     # May charge twice if task retries!
    order.fulfill()

# GOOD: Idempotent with status guard
@shared_task
def charge_and_fulfill(order_id):
    order = Order.objects.select_for_update().get(pk=order_id)
    if order.status != Order.Status.PENDING:
        return  # Already processed
    order.charge()
    order.fulfill()
```

## Production 檢查清單

| 檢查項目 | 設定 |
|-------|---------|
| Worker 當掉時會自動重啟 | `supervisord` 或 `systemd` unit |
| `CELERY_TASK_ACKS_LATE = True` | worker 當掉時把任務重新排入佇列 |
| `CELERY_WORKER_PREFETCH_MULTIPLIER = 1` | 讓長任務公平分配 |
| 依優先順序分開的佇列 | `-Q default,high_priority,low_priority` |
| 有設定 `CELERY_TASK_SOFT_TIME_LIMIT` | 在硬性終止之前優雅地逾時 |
| Sentry 整合 | 捕捉所有 `task_failure` 訊號 |
| Flower 或其他監控工具 | 看得到佇列深度 |
| Beat 只在單一節點上執行 | 避免排程任務重複執行 |

## 相關 Skills

- `django-patterns`：ORM、service layer 和專案結構
- `django-tdd`：測試 Django 的 model、view 和 service
- `python-testing`：pytest 的設定和 fixture
