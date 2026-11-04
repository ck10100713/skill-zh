---
name: "tw-payment-integration"
description: "串接台灣的金流服務業者，包括信用卡、ATM 轉帳、超商繳費和行動錢包（LINE Pay、街口支付）。當使用者需要在台灣線上收款、選擇金流閘道、了解付款流程或處理退款時使用這個 skill，就算他們說的是「在我們網站上收款」、「台灣該用哪家金流」、「串接信用卡付款」或「設定 LINE Pay」也一樣。"
metadata:
  category: "WP-05 台灣創業"
  tags: ["taiwan", "payment", "fintech", "integration"]
---

# 台灣金流串接

## 框架

```
IRON LAW: Support At Least 3 Payment Methods in Taiwan
（鐵律：在台灣至少要支援 3 種付款方式）

台灣消費者期待有選擇。只收信用卡，會漏掉約 40% 的潛在買家。
台灣電商最基本可行的付款組合：
1. 信用卡
2. ATM/銀行轉帳（ATM 虛擬帳號）
3. 超商繳費（超商代碼/超商取貨付款）

再加上 LINE Pay 和 Apple Pay，可以多抓到 10-15%。
```

### 台灣付款版圖

| 方式 | 市占率 | 使用者輪廓 | 結算時間 |
|--------|------------|-------------|----------------|
| 信用卡/簽帳卡 | 約 45% | 各年齡層、消費較高 | T+1 到 T+7 |
| ATM 虛擬帳號 | 約 15% | 價格敏感、沒有信用卡 | 即時到 T+1 |
| 超商代碼 | 約 10% | 學生、偏好現金 | T+1 到 T+3 |
| LINE Pay | 約 12% | LINE 使用者（台灣 95%） | T+1 到 T+7 |
| Apple Pay / Google Pay | 約 5% | 行動優先的使用者 | T+1 到 T+7 |
| 超商取貨付款（門市貨到付款） | 約 8% | 信任感低、想看到商品 | 取貨後 + T+3 |
| 街口支付 | 約 3% | 較年輕的族群 | T+1 |

### 金流服務業者（PSP）

| PSP | 優勢 | 費率 | 最適合 |
|-----|----------|---------|----------|
| **綠界（ECPay）** | 功能最完整（信用卡、ATM、超商、超取），市占最大 | 信用卡 2.75%、ATM 每筆 NT$15 | 一般電商、新創 |
| **藍新（NewebPay）** | API 設計好、後台現代 | 信用卡 2.5-2.8% | SaaS、訂閱制事業 |
| **TapPay** | 行動優先、整合 Apple Pay/Google Pay/LINE Pay | 信用卡 2.5-2.8% | 行動 app、應用程式內購買 |
| **PayNow** | 好設定、沒有月費 | 信用卡 2.75% | 低量、新創事業 |
| **Stripe** | 國際化、API 很優秀 | 每筆 3.4% + NT$10 | 跨境、主打國際 |

### 串接流程（標準）

```
1. Customer clicks "Pay" on your site
2. Your server creates an order → sends to PSP API
3. PSP returns a payment page URL (or token for inline)
4. Customer completes payment on PSP-hosted page
5. PSP sends callback (webhook) to your server with result
6. Your server verifies the callback signature
7. Update order status → show confirmation to customer
```

### 關鍵 API 概念

| 概念 | 是什麼 |
|---------|-----------|
| **MerchantID** | 你在 PSP 的帳號識別碼 |
| **HashKey / HashIV** | 用來驗證簽章的密鑰 |
| **TradeNo** | 你的訂單 ID（每筆交易必須唯一） |
| **PaymentType** | Credit、ATM、CVS、WebATM 等 |
| **Callback URL** | PSP 在付款後呼叫的 webhook endpoint |
| **Return URL** | 付款後把顧客導回的頁面 |
| **CheckMacValue** | 用來驗證資料完整性的 HMAC 簽章 |

### 退款處理

| 方式 | 退款能力 | 時間 |
|--------|------------------|--------|
| 信用卡 | 可透過 API 全額或部分退款 | 1-7 個工作天 |
| ATM | 無法自動退款，必須匯款退回 | 手動，3-7 天 |
| 超商付款 | 無法自動退款，必須匯款退回 | 手動，3-7 天 |
| LINE Pay | 可透過 API 全額退款 | 1-3 個工作天 |

### 安全要求

| 要求 | 該怎麼做 |
|-------------|-----------|
| **SSL/TLS** | 所有付款頁面都必須是 HTTPS |
| **3D Secure** | 啟用 3DS 2.0 以降低信用卡盜刷 |
| **PCI DSS** | 如果處理原始卡號資料，需要 PCI 合規。使用 PSP 託管的付款頁面就能避開。 |
| **Tokenization** | 儲存付款 token，絕不存原始卡號 |
| **Webhook 驗證** | 處理 callback 前，一定要先驗證 CheckMacValue 簽章 |
| **冪等性** | 妥善處理重複的 callback（PSP 可能會重試） |

## 輸出格式

```markdown
# Payment Integration Plan: {Business}

## Payment Method Selection
| Method | Include? | PSP | Rationale |
|--------|---------|-----|-----------|
| Credit card | Y/N | {provider} | {why} |
| ATM | Y/N | ... | ... |
| CVS | Y/N | ... | ... |
| LINE Pay | Y/N | ... | ... |

## PSP Selection
- Provider: {name}
- Pricing: {rate}
- Rationale: {why this provider}

## Integration Plan
| Phase | Task | Timeline |
|-------|------|----------|
| 1 | Apply for PSP merchant account | 1-2 weeks |
| 2 | Develop payment flow (sandbox) | 1-2 weeks |
| 3 | Implement webhook handler | 1 week |
| 4 | Security review (SSL, signature verification) | 2-3 days |
| 5 | Production testing with real transactions | 1 week |
| 6 | Go-live | 1 day |

## Refund Process
{How each payment method handles refunds}
```

## 常見陷阱

- **PSP 申請需要時間**：商家帳號核准可能要 1-3 週。要提早申請。信用卡收單需要額外文件（公司登記、銀行帳戶證明）。
- **ATM 和超商退款要手動**：不像信用卡，ATM 和超商付款無法自動退款。你需要顧客的銀行帳號才能匯款退回。要把這個放進客服流程。
- **Webhook 的可靠性**：PSP 的 callback 可能延遲或重複。要寫冪等的 handler，並實作對帳 job，每天把 PSP 的紀錄和你的資料庫核對。
- **外國信用卡**：不是所有台灣 PSP 都能良好支援外國信用卡。如果有國際顧客，要用非台灣的卡測試，或改用 Stripe。
- **定期扣款（訂閱）**：綠界和藍新支援定期扣款，但你需要顧客明確同意，而且必須處理卡片過期/更新的流程。

## 參考資料

- 綠界 API 串接指南，見 `references/ecpay-api.md`
- PCI DSS 合規檢查表，見 `references/pci-checklist.md`
