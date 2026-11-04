---
name: "tw-ecom-analytics-ga4"
description: "替台灣電商實作 GA4：Enhanced Ecommerce 事件（view_item、add_to_cart、begin_checkout、purchase）、台灣專屬的參數慣例（含稅 revenue、NT$ 幣別、統編當 user property）、Looker Studio 報表，以及 Big Query 匯出。當替台灣商店埋 GA4，或稽核既有 GA4 設定時使用。一般的分析「不要」用這個（改用 `ecom-analytics`）。STATUS: SKELETON — 內文待補。"
metadata:
  category: "WP-01 電商"
  domain: "ecommerce-tw"
  layer: "analytics"
  related_mcps: []
  related_skills: ["ecom-analytics", "data-cohort-analysis", "tw-ecom-analytics-benchmarks"]
  last_verified: "2026-04"
  status: "skeleton"
  tags: ["taiwan", "e-commerce", "ga4", "analytics"]
---

# 台灣電商的 GA4

> **STATUS: SKELETON**：內文待補。

## 何時使用這個 skill

- 替台灣商店埋 GA4 Enhanced Ecommerce
- 稽核既有 GA4 設定是否符合台灣慣例
- 設計台灣 KPI 的 Looker Studio 報表
- 設定 BigQuery 匯出
- 跨 LINE OA / 電商平台通路做歸因

## 何時「不要」使用

- 一般分析 → `ecom-analytics`
- 只要基準 → `tw-ecom-analytics-benchmarks`

## 核心概念

TODO: GA4 事件模型、含稅 revenue 的處理、幣別 = TWD、用 content_group 標示檔期。

## 決策樹

TODO: 事件 → 符合台灣慣例的參數對應。

## 實作指引

TODO: dataLayer 範本、tag 設定、consent mode、BigQuery 匯出。

## 常見陷阱

TODO: 5-6 個陷阱（含稅重複計算、跨網域電商平台歸因、LINE IAB 追蹤被擋、consent-mode 下 revenue 低估、參數基數上限）。

## IRON LAW

TODO.

## 輸出格式

TODO.

## 相關

- `ecom-analytics`
- `tw-ecom-analytics-benchmarks`

_Last verified: 2026-04_
