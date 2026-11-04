---
name: "tw-ecom-invoice-universalec"
description: "使用 mcp-universalec-e-invoice（27 個 tool），透過 UniversalEC（汎宇電商）開立台灣電子發票。當商家用 UniversalEC 而不是 ezPay 當加值服務中心，或要在不同中心之間遷移時使用。ezPay 流程（`tw-ecom-invoice-ezpay`）或財政部直連（`tw-einvoice-guide`）「不要」用這個。STATUS: SKELETON — 內文待補。"
metadata:
  category: "WP-05 台灣創業"
  domain: "ecommerce-tw"
  layer: "invoice"
  related_mcps: ["mcp-universalec-e-invoice"]
  related_skills: ["tw-einvoice-guide", "tw-ecom-invoice-ezpay", "tw-ecom-invoice-carrier", "tw-ecom-invoice-void"]
  last_verified: "2026-04"
  status: "skeleton"
  tags: ["taiwan", "e-invoice", "universalec", "tax-compliance"]
---

# UniversalEC（汎宇電商）電子發票串接

> **STATUS: SKELETON**：內文待補。

## 何時使用這個 skill

- 商家用 UniversalEC 當加值服務中心
- 在 ezPay 和 UniversalEC 之間遷移
- 使用 UniversalEC 專屬的功能（27 個 tool，比 ezPay 的 7 個豐富）
- 對 UniversalEC ↔ 財政部平台做對帳

## 何時「不要」使用

- 用的是 ezPay → `tw-ecom-invoice-ezpay`
- 直連財政部 → `tw-einvoice-guide`

## 核心概念

TODO: UniversalEC 的市場定位、tool 組合的廣度。

## 決策樹

TODO: UniversalEC vs ezPay 的取捨。

## 實作指引

TODO: 27 個 tool 的類別、常見流程。

## 常見陷阱

TODO.

## IRON LAW

TODO.

## 輸出格式

TODO.

## 相關

- `tw-ecom-invoice-ezpay`（平行的 skill）
- `tw-einvoice-guide`

_Last verified: 2026-04_
