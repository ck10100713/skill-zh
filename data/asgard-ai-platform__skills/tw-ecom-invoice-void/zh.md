---
name: "tw-ecom-invoice-void"
description: "在同一雙月期間內作廢台灣電子發票，或為跨期更正開立折讓。當處理會影響發票狀態的退貨 / 退款時使用。初次開立「不要」用這個，請看各加值中心專屬的 skill。STATUS: SKELETON — 內文待補。"
metadata:
  category: "WP-05 台灣創業"
  domain: "ecommerce-tw"
  layer: "invoice"
  related_mcps: []
  related_skills: ["tw-einvoice-guide", "tw-ecom-invoice-ezpay", "tw-ecom-payment-dispute"]
  last_verified: "2026-04"
  status: "skeleton"
  tags: ["taiwan", "e-invoice", "void", "allowance"]
---

# 發票作廢與折讓

> **STATUS: SKELETON**：內文待補。

## 何時使用這個 skill

- 退貨 / 退款發生在同一雙月期間內 → 作廢
- 退貨 / 退款跨越雙月界線 → 折讓
- 除錯退款後發票狀態不一致
- 建立作廢 / 折讓的 SOP

## 何時「不要」使用

- 初次開立 → 開立層的 skill
- 對報稅的影響 → `tw-tax-basics`

## 核心概念

TODO: 作廢 vs 折讓、雙月界線、會計上的影響。
NOTE (填充時): 此 skill 只寫「選哪條路」的決策邏輯，不重複 API 呼叫細節。
`tw-ecom-invoice-ezpay` 已有完整的 void_invoice / issue_allowance / trigger_allowance 步驟；
`tw-ecom-invoice-universalec` 同理。此 skill 的 Implementation guidance 應只提供判斷框架，
並用 "→ see tw-ecom-invoice-ezpay / -universalec" 指向 API 層。

## 決策樹

TODO: 依退款日期 vs 開立日期 → 作廢或折讓。

## 實作指引

TODO: 決策路徑後的 SOP（accounting entries, customer notification, 字軌影響）。
不重複 void_invoice / issue_allowance / trigger_allowance 的 API 參數 — 那些在 ezpay/universalec skill。

## 常見陷阱

TODO: 5-6 個陷阱（邊界差一、字軌保留、對獎失效、折讓編號）。

## IRON LAW

TODO.

## 輸出格式

TODO.

## 相關

- `tw-ecom-invoice-ezpay`
- `tw-ecom-payment-dispute`

_Last verified: 2026-04_
