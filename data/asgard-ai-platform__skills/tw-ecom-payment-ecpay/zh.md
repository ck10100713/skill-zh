---
name: "tw-ecom-payment-ecpay"
description: "替台灣電商串接綠界（ECPay）：信用卡、ATM、超商代碼、超商取貨付款，以及 CheckMacValue 簽章。當選定 ECPay 作為 PSP、設定物流與付款結合的流程（超取+貨到付款）、計算或驗證 CheckMacValue，或處理 ECPay 的 callback 時使用。金流選擇或比較「不要」用這個（看 tw-payment-integration）。非 ECPay 的業者也「不要」用這個。STATUS: SKELETON — 內文待補。"
metadata:
  category: "WP-05 台灣創業"
  domain: "ecommerce-tw"
  layer: "payment"
  related_mcps: ["mcp-ecpay"]
  related_skills: ["tw-payment-integration", "tw-ecom-payment-newebpay", "tw-ecom-logistics-cvs"]
  last_verified: "2026-04"
  status: "skeleton"
  tags: ["taiwan", "payment", "ecpay", "fintech"]
---

# ECPay（綠界）串接

> **STATUS: SKELETON**：內文待補。

## 何時使用這個 skill

- 串接 ECPay 的信用卡 / ATM / 超商代碼 / 超商取貨付款
- 把 ECPay 的物流 + 付款合併成一個流程
- 計算 / 驗證 CheckMacValue 簽章
- 處理 ECPay 的 callback webhook
- 和 ECPay 商家後台對帳

## 何時「不要」使用

- 非 ECPay 的業者 → 該業者專屬的 skill
- 純物流（沒有付款）→ `tw-ecom-logistics-cvs`

## 核心概念

TODO: ECPay 的定位、CheckMacValue 簽章、超取+貨到付款的合併模型。

## 決策樹

TODO: 什麼情況下 ECPay 的合併流程優於把付款和運送分開。

## 實作指引

TODO: 商家設定、第一筆交易、取貨付款的對帳。

## 常見陷阱

TODO: 5-6 個陷阱（CheckMacValue 參數排序 / URL encoding 的坑、貨到付款結算的時間差、超取失敗的退款流程、跨 sandbox 憑證外洩、境外卡的相容性）。

## IRON LAW

TODO.

## 輸出格式

TODO.

## 相關

- `tw-payment-integration`
- `tw-ecom-logistics-cvs`

_Last verified: 2026-04_
