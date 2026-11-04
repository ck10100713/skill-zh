---
name: stripe-integration
description: 實作 Stripe 付款處理，打造穩健且符合 PCI 規範的付款流程，包含 checkout、訂閱和 webhook。在整合 Stripe 付款、建構訂閱系統或實作安全的結帳流程時使用。
---

# Stripe Integration

精通 Stripe 付款處理的整合，打造穩健且符合 PCI 規範的付款流程，包含 checkout、訂閱、webhook 和退款。

## When to Use This Skill

- 在網頁/行動應用裡實作付款處理
- 設定訂閱計費系統
- 處理一次性付款和週期性扣款
- 處理退款和爭議
- 管理客戶的付款方式
- 為歐洲的付款實作 SCA（Strong Customer Authentication）
- 用 Stripe Connect 建構 marketplace 的付款流程

## Core Concepts

### 1. Payment Flows

**Checkout Sessions**

- 大多數整合都推薦用這個
- 支援所有 UI 路徑：
  - Stripe 代管的結帳頁面
  - 嵌入式的結帳表單
  - 搭配 Elements（Payment Element、Express Checkout Element）的自訂 UI，使用 `ui_mode='custom'`
- 提供內建的結帳功能（商品明細、折扣、稅金、運費、地址收集、已儲存的付款方式，以及結帳生命週期事件）
- 整合和維護的負擔比 Payment Intents 低

**Payment Intents (Bespoke control)**

- 含稅金、折扣、訂閱和幣別轉換的最終金額，要由你自己計算。
- 實作比較複雜，長期維護的負擔也比較重
- 為了符合 PCI，需要 Stripe.js

**Setup Intents (Save Payment Methods)**

- 收集付款方式，但不扣款
- 用於訂閱和未來的付款
- 需要客戶確認

### 2. Webhooks

**關鍵事件：**

- `payment_intent.succeeded`：付款完成
- `payment_intent.payment_failed`：付款失敗
- `customer.subscription.updated`：訂閱有變動
- `customer.subscription.deleted`：訂閱已取消
- `charge.refunded`：退款已處理
- `invoice.payment_succeeded`：訂閱付款成功

### 3. Subscriptions

**組成：**

- **Product**：你在賣的東西
- **Price**：多少錢、多久一次
- **Subscription**：客戶的週期性付款
- **Invoice**：每個計費週期產生的帳單

### 4. Customer Management

- 建立並管理客戶紀錄
- 儲存多種付款方式
- 追蹤客戶的 metadata
- 管理帳單明細

## Quick Start

```python
import stripe

stripe.api_key = "sk_test_..."

# Create a checkout session
session = stripe.checkout.Session.create(
    line_items=[{
        'price_data': {
            'currency': 'usd',
            'product_data': {
                'name': 'Premium Subscription',
            },
            'unit_amount': 2000,  # $20.00
            'recurring': {
                'interval': 'month',
            },
        },
        'quantity': 1,
    }],
    mode='subscription',
    success_url='https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}',
    cancel_url='https://yourdomain.com/cancel'
)

# Redirect user to session.url
print(session.url)
```

## Detailed patterns and worked examples

詳細的 pattern 文件放在 `references/details.md`。上面這層導覽不夠用的時候，再去讀那個檔案。

## Testing

```python
# Use test mode keys
stripe.api_key = "sk_test_..."

# Test card numbers
TEST_CARDS = {
    'success': '4242424242424242',
    'declined': '4000000000000002',
    '3d_secure': '4000002500003155',
    'insufficient_funds': '4000000000009995'
}

def test_payment_flow():
    """Test complete payment flow."""
    # Create test customer
    customer = stripe.Customer.create(
        email="test@example.com"
    )

    # Create payment intent
    intent = stripe.PaymentIntent.create(
        amount=1000,
        automatic_payment_methods={
            'enabled': True
        },
        currency='usd',
        customer=customer.id
    )

    # Confirm with test card
    confirmed = stripe.PaymentIntent.confirm(
        intent.id,
        payment_method='pm_card_visa'  # Test payment method
    )

    assert confirmed.status == 'succeeded'
```
