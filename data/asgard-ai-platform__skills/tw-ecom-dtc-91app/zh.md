---
name: "tw-ecom-dtc-91app"
description: "透過 mcp-91app，在台灣電商情境下串接並營運 91APP。當要在 91APP 上同步訂單/商品/會員、執行 OMO（online-merge-offline）流程、整合 91APP 以 app 為主的店面，或比較 91APP 與 Shopline/Shopify 用於中型 DTC 時使用。Shopline 專屬的串接「不要」用這個（看 tw-ecom-dtc-shopline）。STATUS: SKELETON — 內文待補。"
metadata:
  category: "WP-01 電商"
  domain: "ecommerce-tw"
  layer: "platform"
  related_mcps: ["mcp-91app"]
  related_skills: ["tw-ecom-channel-strategy", "tw-ecom-dtc-shopline"]
  last_verified: "2026-04"
  status: "skeleton"
  tags: ["taiwan", "e-commerce", "91app", "platform", "integration"]
---

# 91APP 串接方法論

> **STATUS: SKELETON**：內文待補。

## 何時使用這個 skill

- 透過 mcp-91app 串接 91APP
- 執行 91APP 專屬的 OMO（online-merge-offline）流程
- 在 91APP 和 CRM 之間同步會員資料
- 除錯 91APP 的促銷 / 優惠券流程
- 比較 91APP 與 Shopline 在中型 DTC 區隔的差異

## 何時「不要」使用

- 需要一般的平台選擇指引 → 用 `tw-ecom-channel-strategy`
- 需要 91APP 的 API schema 文件 → 直接查 mcp-91app 的 README

## 核心概念

TODO: 91APP 以 app 為主的定位、OMO 模型、以會員為中心的架構。

## 決策樹

TODO: 哪個任務該用 mcp-91app 的哪個 tool。

## 實作指引

TODO: 訂單同步、會員同步、促銷設定、庫存同步流程。

## 常見陷阱

TODO: 5-6 個陷阱（候選：OMO 狀態漂移、促銷疊加規則、跨網頁/app 的會員合併、配額上限）。

## IRON LAW

TODO: 一個不明顯的限制。

## 輸出格式

TODO.

## 相關

- `tw-ecom-channel-strategy`
- `tw-ecom-dtc-shopline`（方法論範本）

_Last verified: 2026-04_
