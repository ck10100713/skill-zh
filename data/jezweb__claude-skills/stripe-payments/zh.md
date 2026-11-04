---
name: stripe-payments
description: "為 web app 加上 Stripe 付款：Checkout Sessions、Payment Intents、訂閱、webhook、customer portal 和定價頁。涵蓋該選哪個 Stripe API 的判斷，產出可用的整合程式碼，並處理 webhook 簽章驗證。不需要 MCP server，直接使用 Stripe npm 套件。觸發詞：'add payments'、'stripe'、'checkout'、'subscription'、'payment form'、'pricing page'、'billing'、'accept payments'、'stripe webhook'、'customer portal'。"
compatibility: claude-code-only
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

# Stripe Payments

為 web app 加上 Stripe 付款。涵蓋常見的模式：一次性付款、訂閱、webhook、customer portal，並附可用的程式碼。不需要 MCP server。

## 我該用哪個 Stripe API？

| 你想要... | 用 | 複雜度 |
|----------------|-----|-----------|
| 接受一次性付款 | Checkout Sessions | 低，付款頁由 Stripe 代管 |
| 把付款表單嵌進自己的 UI | Payment Element + Payment Intents | 中，表單你自己做，刷卡交給 Stripe |
| 定期扣款 / 訂閱 | Checkout Sessions（subscription mode） | 低到中 |
| 存卡以備之後使用 | Setup Intents | 低 |
| 市集 / 平台型付款 | Stripe Connect | 高 |
| 讓顧客自己管理帳務 | Customer Portal | 低，由 Stripe 代管 |

**預設建議**：從 Checkout Sessions 開始。這是最快開始收錢的路。之後隨時可以再加嵌入式表單。

## 設定

### 安裝

```bash
npm install stripe @stripe/stripe-js
```

### API Key

```bash
# Get keys from: https://dashboard.stripe.com/apikeys
# Test keys start with sk_test_ and pk_test_
# Live keys start with sk_live_ and pk_live_

# For Cloudflare Workers — store as secrets:
npx wrangler secret put STRIPE_SECRET_KEY
npx wrangler secret put STRIPE_WEBHOOK_SECRET

# For local dev — .dev.vars:
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Server 端 Client

```typescript
import Stripe from 'stripe';

// Cloudflare Workers
const stripe = new Stripe(c.env.STRIPE_SECRET_KEY);

// Node.js
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);
```

## 一次性付款（Checkout Sessions）

最快的收款方式。整個結帳頁都由 Stripe 代管。

### 建立 Checkout Session（Server）

```typescript
app.post('/api/checkout', async (c) => {
  const { priceId, successUrl, cancelUrl } = await c.req.json();

  const session = await stripe.checkout.sessions.create({
    mode: 'payment',
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: successUrl || `${new URL(c.req.url).origin}/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: cancelUrl || `${new URL(c.req.url).origin}/pricing`,
  });

  return c.json({ url: session.url });
});
```

### 導向 Checkout（Client）

```typescript
async function handleCheckout(priceId: string) {
  const res = await fetch('/api/checkout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ priceId }),
  });
  const { url } = await res.json();
  window.location.href = url;
}
```

### 建立商品和價格

```bash
# Via Stripe CLI (recommended for setup)
stripe products create --name="Pro Plan" --description="Full access"
stripe prices create --product=prod_XXX --unit-amount=2900 --currency=aud --recurring[interval]=month

# Or via Dashboard: https://dashboard.stripe.com/products
```

**把 price ID 寫死**在程式碼裡（它們不會變）：
```typescript
const PRICES = {
  pro_monthly: 'price_1234567890',
  pro_yearly: 'price_0987654321',
} as const;
```

## 訂閱

跟一次性付款一樣，只是改用 `mode: 'subscription'`：

```typescript
const session = await stripe.checkout.sessions.create({
  mode: 'subscription',
  line_items: [{ price: PRICES.pro_monthly, quantity: 1 }],
  success_url: `${origin}/dashboard?session_id={CHECKOUT_SESSION_ID}`,
  cancel_url: `${origin}/pricing`,
  // Link to existing customer if known:
  customer: customerId, // or customer_email: 'user@example.com'
});
```

### 檢查訂閱狀態

```typescript
async function hasActiveSubscription(customerId: string): Promise<boolean> {
  const subs = await stripe.subscriptions.list({
    customer: customerId,
    status: 'active',
    limit: 1,
  });
  return subs.data.length > 0;
}
```

## Webhook

事情發生時（付款成功、訂閱取消等），Stripe 會把事件送到你的 server。**一定要驗證 webhook 簽章。**

### Webhook Handler（Cloudflare Workers / Hono）

```typescript
app.post('/api/webhooks/stripe', async (c) => {
  const body = await c.req.text();
  const sig = c.req.header('stripe-signature')!;

  let event: Stripe.Event;
  try {
    // Use constructEventAsync for Workers (no Node crypto)
    event = await stripe.webhooks.constructEventAsync(
      body,
      sig,
      c.env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    console.error('Webhook signature verification failed:', err);
    return c.json({ error: 'Invalid signature' }, 400);
  }

  switch (event.type) {
    case 'checkout.session.completed': {
      const session = event.data.object as Stripe.Checkout.Session;
      // Fulfill the order — update database, send email, grant access
      await handleCheckoutComplete(session);
      break;
    }
    case 'customer.subscription.updated': {
      const sub = event.data.object as Stripe.Subscription;
      await handleSubscriptionChange(sub);
      break;
    }
    case 'customer.subscription.deleted': {
      const sub = event.data.object as Stripe.Subscription;
      await handleSubscriptionCancelled(sub);
      break;
    }
    case 'invoice.payment_failed': {
      const invoice = event.data.object as Stripe.Invoice;
      await handlePaymentFailed(invoice);
      break;
    }
  }

  return c.json({ received: true });
});
```

### 註冊 Webhook

```bash
# Local testing with Stripe CLI:
stripe listen --forward-to http://localhost:8787/api/webhooks/stripe

# Production — register via Dashboard:
# https://dashboard.stripe.com/webhooks
# URL: https://yourapp.com/api/webhooks/stripe
# Events: checkout.session.completed, customer.subscription.updated,
#          customer.subscription.deleted, invoice.payment_failed
```

### Cloudflare Workers 陷阱

`constructEvent`（同步版）用的是 Node.js 的 `crypto`，Workers 裡沒有。改用 `constructEventAsync`，它用的是 Web Crypto API。

## Customer Portal

讓顧客自己管理訂閱（升級、降級、取消、更新付款方式）：

```typescript
app.post('/api/billing/portal', async (c) => {
  const { customerId } = await c.req.json();

  const session = await stripe.billingPortal.sessions.create({
    customer: customerId,
    return_url: `${new URL(c.req.url).origin}/dashboard`,
  });

  return c.json({ url: session.url });
});
```

在 Dashboard 設定 portal：https://dashboard.stripe.com/settings/billing/portal

## 定價頁模式

產生一個從 Stripe 商品讀資料的定價頁：

```typescript
// Server: fetch products and prices
app.get('/api/pricing', async (c) => {
  const prices = await stripe.prices.list({
    active: true,
    expand: ['data.product'],
    type: 'recurring',
  });

  return c.json(prices.data.map(price => ({
    id: price.id,
    name: (price.product as Stripe.Product).name,
    description: (price.product as Stripe.Product).description,
    amount: price.unit_amount,
    currency: price.currency,
    interval: price.recurring?.interval,
  })));
});
```

如果只有 2-3 個方案，也可以直接寫死，比較簡單，而且每次載入頁面都不用打 API。

## Stripe CLI（本機開發）

```bash
# Install
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Listen for webhooks locally
stripe listen --forward-to http://localhost:8787/api/webhooks/stripe

# Trigger test events
stripe trigger checkout.session.completed
stripe trigger customer.subscription.created
stripe trigger invoice.payment_failed
```

## 常見模式

### 把 Stripe Customer 連到你的 User

```typescript
// On first checkout, create or find customer:
const session = await stripe.checkout.sessions.create({
  customer_email: user.email,  // Creates new customer if none exists
  // OR
  customer: user.stripeCustomerId,  // Use existing
  metadata: { userId: user.id },  // Link back to your user
  // ...
});

// In webhook, save the customer ID:
case 'checkout.session.completed': {
  const session = event.data.object;
  await db.update(users)
    .set({ stripeCustomerId: session.customer as string })
    .where(eq(users.id, session.metadata.userId));
}
```

### 免費試用

```typescript
const session = await stripe.checkout.sessions.create({
  mode: 'subscription',
  line_items: [{ price: PRICES.pro_monthly, quantity: 1 }],
  subscription_data: {
    trial_period_days: 14,
  },
  // ...
});
```

### 澳幣

```typescript
// Set currency when creating prices
const price = await stripe.prices.create({
  product: 'prod_XXX',
  unit_amount: 2900,  // $29.00 in cents
  currency: 'aud',
  recurring: { interval: 'month' },
});
```

## 陷阱

| 陷阱 | 解法 |
|--------|-----|
| `constructEvent` 在 Workers 上失敗 | 改用 `constructEventAsync`（Web Crypto API） |
| Webhook 有觸發，但 handler 沒被呼叫 | 檢查 endpoint 網址是否完全一致（結尾的斜線也有差） |
| 測試模式的付款沒出現 | 確認用的是 `sk_test_` key，不是 `sk_live_` |
| 價格金額單位是分 | `2900` = $29.00。顯示時一律除以 100 |
| Customer email 對不上 user | 回頭的使用者要用 `customer`（既有 ID），不要用 `customer_email` |
| 訂閱狀態過期 | 不要快取，用 API 查，或相信 webhook 事件 |
| Webhook 重試 | Stripe 會對失敗的 webhook 重試最多 3 天。要快速回傳 200。 |
| Checkout 導向時的 CORS | Checkout 網址在 stripe.com 上，要用 `window.location.href`，不要用 fetch |
