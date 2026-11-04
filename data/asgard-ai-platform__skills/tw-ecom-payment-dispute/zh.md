---
name: "tw-ecom-payment-dispute"
description: "處理台灣電商的付款糾紛：信用卡拒付（扣款爭議）、跨雙月界線的退款（追溯折讓觸發）、收單行爭議時程，以及證據包。當客戶提出拒付、開立會影響發票的跨期退款，或建立內部糾紛 SOP 時使用。單純的同期退款「不要」用這個（由各金流專屬的 skill 處理）。STATUS: SKELETON — 內文待補。"
metadata:
  category: "WP-05 台灣創業"
  domain: "ecommerce-tw"
  layer: "payment"
  related_mcps: []
  related_skills: ["tw-payment-integration", "tw-ecom-payment-newebpay", "tw-ecom-payment-ecpay", "tw-ecom-invoice-void", "tw-ecom-compliance-consumer"]
  last_verified: "2026-04"
  status: "skeleton"
  tags: ["taiwan", "payment", "dispute", "chargeback"]
---

# 付款糾紛處理

> **STATUS: SKELETON**：內文待補。

## 何時使用這個 skill

- 客戶提出了信用卡拒付
- 開立跨越雙月發票界線的退款
- 建立內部的糾紛處理 SOP
- 準備給收單行審查的證據包
- 把糾紛結果和發票狀態對帳

## 何時「不要」使用

- 單純的同期退款 → 各金流專屬的 skill
- 消費者法層級的糾紛（鑑賞期）→ `tw-ecom-compliance-consumer`

## 核心概念

TODO: 拒付 vs 退刷 vs 折讓、典型的收單行時程、原因代碼。

## 決策樹

TODO: 依原因代碼 → 回應路徑。

## 實作指引

TODO: 證據包結構、折讓觸發邏輯、會計分錄。

## 常見陷阱

TODO: 5-6 個陷阱（雙月界線、雙重退款造成重複扣款、原因代碼不符、證據期限、各收單行的方言差異）。

## IRON LAW

TODO.

## 輸出格式

TODO.

## 相關

- `tw-ecom-compliance-consumer`
- `tw-ecom-invoice-void`

_Last verified: 2026-04_
