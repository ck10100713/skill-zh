---
name: "tw-ecom-logistics-home"
description: "透過台灣宅配業者出貨：黑貓宅急便、宅配通、新竹物流、郵局。當要設定宅配、依地區 / 包裹大小選業者、整合運單列印，或處理再配送時使用。超商取貨（`tw-ecom-logistics-cvs`）「不要」用這個。STATUS: SKELETON — 內文待補。"
metadata:
  category: "WP-01 電商"
  domain: "ecommerce-tw"
  layer: "logistics"
  related_mcps: []
  related_skills: ["tw-ecom-logistics-cvs", "tw-ecom-logistics-cold-chain"]
  last_verified: "2026-04"
  status: "skeleton"
  tags: ["taiwan", "logistics", "home-delivery"]
---

# 宅配物流

> **STATUS: SKELETON**：內文待補。

## 何時使用這個 skill

- 在 黑貓 / 宅配通 / 新竹物流 / 郵局 之間選擇宅配業者
- 整合運單 API / 批次列印
- 處理再配送（二次配）排程
- 離島加收費用的處理
- 指定時段的配送選項

## 何時「不要」使用

- 超商取貨 → `tw-ecom-logistics-cvs`
- 冷鏈 / 冷凍 → `tw-ecom-logistics-cold-chain`

## 核心概念

TODO: 依材積 vs 重量的業者計價、各區域涵蓋差異、SLA 承諾。

## 決策樹

TODO: 依地區 / 重量 / 時效選業者。

## 實作指引

TODO: 運單 API、批次上傳、追蹤 webhook。

## 常見陷阱

TODO: 5-6 個陷阱（依材積加價、離島加收不透明、追蹤更新延遲、配送失敗處理、易碎品保險）。

## IRON LAW

TODO.

## 輸出格式

TODO.

## 相關

- `tw-ecom-logistics-cvs`

_Last verified: 2026-04_
