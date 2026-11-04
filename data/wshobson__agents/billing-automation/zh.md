---
name: billing-automation
description: 建構自動化計費系統，涵蓋定期扣款、開立發票、訂閱生命週期和催繳（dunning）管理。在實作訂閱計費、自動化開立發票，或管理定期付款系統時使用。
---

# 計費自動化

掌握自動化計費系統，包括定期計費、產生發票、催繳管理、按比例計費（proration）和稅金計算。

## 何時使用這個 Skill

- 實作 SaaS 訂閱計費
- 自動化發票的產生和寄送
- 管理失敗付款的追回（dunning）
- 計算方案變更時按比例計算的費用
- 處理銷售稅、VAT 和 GST
- 處理用量計費
- 管理計費週期和續約

## 核心概念

### 1. 計費週期

**常見的間隔：**

- 每月（SaaS 最常見）
- 每年（長期優惠折扣）
- 每季
- 每週
- 自訂（用量計費、依席次計費）

### 2. 訂閱狀態

```
trial → active → past_due → canceled
              → paused → resumed
```

### 3. 催繳管理

透過下列方式追回失敗付款的自動化流程：

- 重試排程
- 客戶通知
- 寬限期
- 帳號限制

### 4. 按比例計費

在這些情況下調整收費：

- 週期中途升級/降級
- 新增/移除席次
- 變更計費頻率

## 快速開始

```python
from billing import BillingEngine, Subscription

# Initialize billing engine
billing = BillingEngine()

# Create subscription
subscription = billing.create_subscription(
    customer_id="cus_123",
    plan_id="plan_pro_monthly",
    billing_cycle_anchor=datetime.now(),
    trial_days=14
)

# Process billing cycle
billing.process_billing_cycle(subscription.id)
```

## 詳細模式與實作範例

詳細的模式文件放在 `references/details.md`。上面的導覽層不夠用時，再讀那個檔案。
