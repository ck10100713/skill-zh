---
name: "tw-ecom-payment-tappay"
description: "替台灣電商串接 TapPay：TapPay Web/iOS/Android SDK、3DS 2.0 流程、透過 TapPay 串接 Apple Pay / Google Pay / LINE Pay，以及用於 token 化定期付款的 TCS（TapPay Card Service）。當選定 TapPay 當 PSP、比較 TapPay 與 NewebPay，或除錯 3DS 流程時使用。其他金流「不要」用這個。STATUS: SKELETON — 內文待補。"
metadata:
  category: "WP-05 台灣創業"
  domain: "ecommerce-tw"
  layer: "payment"
  related_mcps: []
  related_skills: ["tw-payment-integration", "tw-ecom-payment-newebpay", "tw-ecom-payment-dispute"]
  last_verified: "2026-04"
  status: "skeleton"
  tags: ["taiwan", "payment", "tappay", "fintech"]
---

# 台灣電商的 TapPay 串接

> **STATUS: SKELETON**：內文待補。

## 何時使用這個 skill

- 整合 TapPay Web/iOS/Android SDK
- 透過 TapPay 加入 Apple Pay / Google Pay / LINE Pay
- 實作 TCS（token 化定期付款）
- 除錯 TapPay 上的 3DS 2.0 流程問題
- 針對特定使用情境，比較 TapPay 與 NewebPay / ECPay

## 何時「不要」使用

- 一般的台灣金流選擇 → `tw-payment-integration`
- 非 TapPay 的業者 → 該業者專屬的 skill

## 核心概念

TODO: TapPay 的定位（mobile-first）、TapPay Direct vs TapPay Pay by Prime、TCS 流程。

## 決策樹

TODO: 什麼情況下 TapPay 勝過 NewebPay/ECPay。

## 實作指引

TODO: 取得 Prime token、處理 3DS、TCS 綁卡 + 扣款。

## 常見陷阱

TODO: 5-6 個陷阱（Prime token 的 TTL、3DS 插頁的 UX、卡片過期時 TCS 解除綁定、Apple Pay 網域驗證、sandbox 切換到 production 的商家切換）。

## IRON LAW

TODO.

## 輸出格式

TODO.

## 相關

- 金流比較請看 `tw-payment-integration`
- 退款 / 拒付處理請看 `tw-ecom-payment-dispute`

_Last verified: 2026-04_
