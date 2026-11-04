---
name: "tw-ecom-logistics-cvs"
description: "透過台灣超商取貨出貨（7-11 賣貨便 / 全家 / 萊爾富 / OK）：選店 API、運單格式、取貨 SLA、貨到付款對帳、退貨運送。當要在台灣商店設定超商 超取、選擇要支援哪些連鎖，或除錯運單列印時使用。宅配或跨境「不要」用這個。STATUS: SKELETON — 內文待補。"
metadata:
  category: "WP-01 電商"
  domain: "ecommerce-tw"
  layer: "logistics"
  related_mcps: ["mcp-ecpay-logistics"]
  related_skills: ["tw-ecom-logistics-home", "tw-ecom-payment-ecpay"]
  last_verified: "2026-04"
  status: "skeleton"
  tags: ["taiwan", "logistics", "cvs", "super-pickup"]
---

# 超商取貨

> **STATUS: SKELETON**：內文待補。

## 何時使用這個 skill

- 為台灣電商商店設定超商 超取
- 選擇要支援哪些連鎖（7-11 vs 全家 vs 萊爾富 vs OK）
- 在結帳頁整合選店元件
- 處理貨到付款（超取付款）對帳
- 管理超商退貨流程

## 何時「不要」使用

- 宅配 → `tw-ecom-logistics-home`
- 跨境 → `tw-ecom-logistics-cross-border`

## 核心概念

TODO: 各連鎖的怪癖、大宗 vs 一般取貨、運單格式、SLA。

## 決策樹

TODO: 依顧客地理位置 + 平均訂單金額決定連鎖組合。

## 實作指引

TODO: 元件整合、運單列印、貨到付款結算、退貨流程。

## 常見陷阱

TODO: 5-6 個陷阱（各連鎖運單格式不一、超重被拒收、地址與門市不符、貨到付款結算延遲、門市歇業的邊界情況）。

## IRON LAW

TODO.

## 輸出格式

TODO.

## 相關

- `tw-ecom-payment-ecpay`（合併貨到付款流程）

_Last verified: 2026-04_
