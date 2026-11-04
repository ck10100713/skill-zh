---
name: "tw-einvoice-guide"
description: "實作台灣的電子發票系統，包括平台串接、B2B 與 B2C 格式、載具歸戶，以及報稅對帳。當使用者需要為台灣企業建置電子發票、串接財政部平台、了解載具代碼或排查發票問題時使用這個 skill，就算他們說的是「設定電子發票」、「電子發票怎麼運作」、「串接財政部」或「載具條碼掃描」也一樣。"
metadata:
  category: "WP-05 台灣創業"
  tags: ["taiwan", "e-invoice", "tax-compliance", "integration"]
---

# 台灣電子發票系統

## 框架

```
IRON LAW: E-Invoice Is Mandatory for Most B2C Businesses
（鐵律：多數 B2C 企業都必須開電子發票）

自 2019 年起，使用統一發票的企業必須透過財政部電子發票整合服務平台
開立電子發票。紙本發票正在逐步淘汰。
不合規會被處罰，也可能影響營業稅申報。
```

### 系統架構

```
Your System (POS/ERP/E-commerce)
    ↓ API / Turnkey
財政部電子發票整合服務平台 (einvoice.nat.gov.tw)
    ↓
Consumer (via 載具: 手機條碼 / 自然人憑證 / App)
    ↓
國稅局 (tax reconciliation)
```

### 串接方式

| 方式 | 運作方式 | 最適合 | 複雜度 |
|--------|-------------|----------|-----------|
| **Turnkey** | 安裝財政部提供的軟體，批次上傳發票 | 傳統企業、低量 | 中 |
| **API（加值服務中心）** | 透過加值中心 API 連接（例如綠界、藍新） | 電商、SaaS、大量 | 中低 |
| **直連 API** | 直接連到財政部平台 | 有 IT 團隊的大型企業 | 高 |
| **POS 整合** | POS 廠商原生處理電子發票 | 零售、餐飲 | 低（廠商處理） |

### B2B vs B2C 發票差異

| 面向 | B2B（營業人對營業人） | B2C（營業人對消費者） |
|--------|-------------------|-------------------|
| 買方資訊 | 必須有買方統編 | 沒有統編（消費者） |
| 格式 | 三聯式 | 二聯式 |
| 稅額顯示 | 稅額分開列示 | 價格含稅 |
| 載具 | 不適用 | 手機條碼、自然人憑證或會員載具 |
| 對獎資格 | 無 | 有（中獎機制） |

### 載具類型

| 載具 | 代碼格式 | 使用情境 |
|---------|-----------|----------|
| 手機條碼 | /XXXXXXX（斜線 + 7 個字元） | 最常見的消費者載具 |
| 自然人憑證 | 2 個字母 + 14 位數字 | 與政府身分證明連結 |
| 會員載具 | 由企業自行定義 | 整合會員忠誠計畫 |
| 捐贈碼 | 3-7 位數字 | 把發票捐給公益團體 |

### 實作步驟

**階段 1：註冊**
1. 在財政部電子發票整合服務平台註冊
2. 申請加值服務中心 AppID（如果用 API 方式）
3. 設定憑證與認證

**階段 2：開發/整合**
4. 選擇串接方式（Turnkey vs API vs POS）
5. 實作發票開立：建立、作廢、作廢並重開
6. 實作載具掃描（手機條碼 barcode）
7. 處理捐贈碼

**階段 3：測試**
8. 在 sandbox 環境測試
9. 開立測試發票，在財政部平台上驗證
10. 測試作廢/重開流程

**階段 4：上線**
11. 切換到 production 環境
12. 每天監控：比對開立的發票與財政部紀錄
13. 每雙月：與營業稅申報（401 表）對帳

### 常見 API 流程

**開立發票：**
```
POST /invoice → { seller_id, buyer_id (optional), items[], amount, tax, carrier_type, carrier_id }
→ Response: { invoice_number, invoice_date, random_code }
```

**作廢發票：**
```
POST /invoice/void → { invoice_number, invoice_date, void_reason }
```

**查詢發票：**
```
GET /invoice/{number} → { status, items, amount, carrier }
```

## 輸出格式

```markdown
# E-Invoice Implementation Plan: {Business}

## Current State
- Business type: B2B / B2C / Both
- Current invoicing: Paper / Partial e-invoice / None
- Transaction volume: {N}/month

## Integration Method
- Method: {Turnkey / API / POS integration}
- Provider: {加值中心 name, if applicable}
- Rationale: {why this method}

## Implementation Checklist
- [ ] MOF platform registration
- [ ] AppID obtained
- [ ] Integration developed
- [ ] Sandbox testing passed
- [ ] Carrier scanning implemented
- [ ] Donation code support
- [ ] Production go-live
- [ ] Reconciliation process documented

## Timeline
| Phase | Duration | Milestone |
|-------|----------|-----------|
| Registration | 1-2 weeks | AppID obtained |
| Development | 2-4 weeks | Integration complete |
| Testing | 1-2 weeks | Sandbox verified |
| Go-live | 1 day | First production invoice |
```

## 常見陷阱

- **發票號碼格式由財政部配發**：發票號碼不是你自己產生的。財政部會配發號碼區間（字軌），要提前申請。號碼用完 = 無法開票。要提早申請。
- **作廢期限有限**：發票只能在同一雙月期間內作廢。期間結束後，作廢需要更複雜的流程（折讓）。
- **手機條碼掃描**：條碼是斜線 + 7 個字元。很多 POS 掃描器需要設定才能正確讀取這個格式。要用真的手機條碼來測。
- **中獎**：B2C 電子發票會自動參加政府的統一發票對獎。如果發票存在會員載具裡，你的系統必須支援中獎通知。
- **對帳很重要**：財政部平台才是事實來源。如果你系統裡的發票紀錄和平台對不上，營業稅申報就會有差異。要每天對帳。

## 參考資料

- 加值服務中心 API 文件，見 `references/einvoice-api.md`
- 營業稅申報對帳，見 tw-tax-basics skill
