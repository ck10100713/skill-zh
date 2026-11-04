---
name: paypal-integration
description: 整合 PayPal 付款處理，支援 express checkout、訂閱與退款管理。在實作 PayPal 付款、處理線上交易或建構電商結帳流程時使用。
---

# PayPal Integration

精通 PayPal 付款整合，包含 Express Checkout、IPN 處理、定期扣款與退款流程。

## When to Use This Skill

- 把 PayPal 整合成一種付款方式
- 實作 express checkout 流程
- 用 PayPal 設定定期扣款
- 處理退款與付款爭議
- 處理 PayPal webhook（IPN）
- 支援國際付款
- 實作 PayPal 訂閱

## Core Concepts

### 1. Payment Products

**PayPal Checkout**

- 一次性付款
- Express checkout 體驗
- 支援訪客與 PayPal 帳戶付款

**PayPal Subscriptions**

- 定期扣款
- 訂閱方案
- 自動續約

**PayPal Payouts**

- 把錢付給多位收款人
- Marketplace 與平台付款

### 2. Integration Methods

**Client-Side (JavaScript SDK)**

- Smart Payment Buttons
- 託管的付款流程
- 後端程式碼很少

**Server-Side (REST API)**

- 完全掌控付款流程
- 自訂結帳 UI
- 進階功能

### 3. IPN (Instant Payment Notification)

- 類似 webhook 的付款通知
- 非同步的付款更新
- 需要驗證

## Quick Start

```javascript
// Frontend - PayPal Smart Buttons
<div id="paypal-button-container"></div>

<script src="https://www.paypal.com/sdk/js?client-id=YOUR_CLIENT_ID&currency=USD"></script>
<script>
  paypal.Buttons({
    createOrder: function(data, actions) {
      return actions.order.create({
        purchase_units: [{
          amount: {
            value: '25.00'
          }
        }]
      });
    },
    onApprove: function(data, actions) {
      return actions.order.capture().then(function(details) {
        // Payment successful
        console.log('Transaction completed by ' + details.payer.name.given_name);

        // Send to backend for verification
        fetch('/api/paypal/capture', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({orderID: data.orderID})
        });
      });
    }
  }).render('#paypal-button-container');
</script>
```

```python
# Backend - Verify and capture order
from paypalrestsdk import Payment
import paypalrestsdk

paypalrestsdk.configure({
    "mode": "sandbox",  # or "live"
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET"
})

def capture_paypal_order(order_id):
    """Capture a PayPal order."""
    payment = Payment.find(order_id)

    if payment.execute({"payer_id": payment.payer.payer_info.payer_id}):
        # Payment successful
        return {
            'status': 'success',
            'transaction_id': payment.id,
            'amount': payment.transactions[0].amount.total
        }
    else:
        # Payment failed
        return {
            'status': 'failed',
            'error': payment.error
        }
```

## Detailed patterns and worked examples

詳細的模式文件放在 `references/details.md`。上面的導覽層不夠用時，再去讀那個檔案。

## Testing

```python
# Use sandbox credentials
SANDBOX_CLIENT_ID = "..."
SANDBOX_SECRET = "..."

# Test accounts
# Create test buyer and seller accounts at developer.paypal.com

def test_payment_flow():
    """Test complete payment flow."""
    client = PayPalClient(SANDBOX_CLIENT_ID, SANDBOX_SECRET, mode='sandbox')

    # Create order
    order = client.create_order(10.00)
    assert 'id' in order

    # Get approval URL
    approval_url = next((link['href'] for link in order['links'] if link['rel'] == 'approve'), None)
    assert approval_url is not None

    # After approval (manual step with test account)
    # Capture order
    # captured = client.capture_order(order['id'])
    # assert captured['status'] == 'COMPLETED'
```
