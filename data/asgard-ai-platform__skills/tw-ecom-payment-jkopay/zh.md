---
name: "tw-ecom-payment-jkopay"
description: "替台灣電商串接街口支付（JKOPay）：網頁/app 流程、JKO 幣回饋、商家結算週期，以及掃碼付款 vs app 付款的 UX。當鎖定較年輕的台灣族群，或整合 in-app 的 JKO 流程時使用。一般的電子錢包整合「不要」用這個（LINE Pay / Apple Pay 在其他地方處理）。STATUS: SKELETON — 內文待補。"
metadata:
  category: "WP-05 台灣創業"
  domain: "ecommerce-tw"
  layer: "payment"
  related_mcps: []
  related_skills: ["tw-payment-integration", "tw-ecom-payment-tappay"]
  last_verified: "2026-04"
  status: "skeleton"
  tags: ["taiwan", "payment", "jkopay", "e-wallet"]
---

# 街口支付（JKOPay）串接

> **STATUS: SKELETON**：內文待補。

## 何時使用這個 skill

- 加入街口支付當付款選項（網頁或 in-app）
- 對帳 JKO 幣回饋 / 促銷
- 透過 JKO API 處理退款 / 作廢
- 針對較年輕的台灣族群，比較 JKO 與 LINE Pay

## 何時「不要」使用

- 一般電子錢包 → 其他地方涵蓋
- 非 JKO 的錢包 → 該錢包專屬的 skill

## 核心概念

TODO: JKO 商家後台、族群契合度、幣回饋模型。

## 決策樹

TODO: 什麼時候 JKO 真的能帶來轉換率提升。

## 實作指引

TODO: 商家設定、網頁整合、app 整合、退款。

## 常見陷阱

TODO: 5-6 個陷阱。

## IRON LAW

TODO.

## 輸出格式

TODO.

## 相關

- `tw-payment-integration`

_Last verified: 2026-04_
