---
name: "tw-ecom-invoice-carrier"
description: "處理台灣電子發票載具：手機條碼、自然人憑證、會員載具，以及捐贈碼的捐贈流程。涵蓋載具驗證、掃碼即存的 UX、會員載具歸戶，以及中獎通知。當要設計載具掃碼 UX、除錯無效載具被退件，或實作捐贈碼流程時使用。STATUS: SKELETON — 內文待補。"
metadata:
  category: "WP-05 台灣創業"
  domain: "ecommerce-tw"
  layer: "invoice"
  related_mcps: []
  related_skills: ["tw-einvoice-guide", "tw-ecom-invoice-ezpay"]
  last_verified: "2026-04"
  status: "skeleton"
  tags: ["taiwan", "e-invoice", "carrier"]
---

# 電子發票載具

> **STATUS: SKELETON**：內文待補。

## 何時使用這個 skill

- 設計結帳時的載具掃碼 UX
- 實作會員載具歸戶
- 加入捐贈碼的捐贈流程
- 處理中獎通知
- 除錯載具格式被退件

## 何時「不要」使用

- 整體概覽 → `tw-einvoice-guide`
- 特定加值中心的 API → `tw-ecom-invoice-ezpay` / `-universalec`

## 核心概念

TODO: 載具類型、格式規格、驗證規則。
NOTE (填充時): 格式規格（手機條碼 `/` + 7 alphanumeric、自然人憑證 2 letters + 14 digits）
已在 `tw-ecom-invoice-ezpay` Gotchas 中詳細說明。此 skill 不重複格式規格；
改聚焦在 UX 層面：validation 在哪層做、錯誤訊息設計、掃碼元件選型。

## 決策樹

TODO: 依情境決定預設用哪種載具（例如：有會員帳號 → 會員載具；無帳號 → 引導填手機條碼；B2B → 不需載具）。

## 實作指引

TODO: scan widget 選型與整合、client-side validation 流程、member-carrier linking（會員帳號與手機條碼綁定）。
不重複 `issue_invoice` carrier_type / carrier_num 參數說明 — 那些在 ezpay/universalec skill。

## 常見陷阱

TODO: 5-6 個陷阱。

## IRON LAW

TODO.

## 輸出格式

TODO.

## 相關

- `tw-einvoice-guide`

_Last verified: 2026-04_
